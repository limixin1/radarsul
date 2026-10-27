"""Contrato do snapshot local: integridade de bytes e consistência entre agregações.

Hashes detectam divergências do pacote, não autenticam uma nova resposta da ANTT.
Não há download nem execução de ETL durante a abertura da aplicação.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from config import ROOT, PROCESSED, REPORTS, KM_MIN, KM_MAX
from src.antt import annual_table, monthly_table, cohort_ids, weighted_index


class SnapshotError(ValueError):
    """O snapshot não satisfaz o contrato necessário à apresentação."""


def _require(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise SnapshotError(f'{label}: colunas ausentes: {sorted(missing)}')


def _counts(frame, columns, label):
    for column in columns:
        values = frame[column]
        if not pd.api.types.is_numeric_dtype(values):
            raise SnapshotError(f'{label}: {column} não numérico')
        if not (np.isfinite(values) & values.ge(0) & values.mod(1).eq(0)).all():
            raise SnapshotError(f'{label}: {column} deve ser inteiro, finito e não negativo')


def _dates(frame, label):
    if not pd.api.types.is_datetime64_any_dtype(frame.data) or frame.data.isna().any():
        raise SnapshotError(f'{label}: datas inválidas')
    if not frame.data.eq(frame.data.dt.normalize()).all():
        raise SnapshotError(f'{label}: granularidade deve ser diária')
    if not frame.ano.eq(frame.data.dt.year).all():
        raise SnapshotError(f'{label}: ano diverge da data')
    if 'mes' in frame and not frame.mes.eq(frame.data.dt.strftime('%Y-%m')).all():
        raise SnapshotError(f'{label}: mês diverge da data')


def _aggregate_matches(actual, expected, keys, label):
    _require(actual, expected.columns, label)
    try:
        pd.testing.assert_frame_equal(
            actual[list(expected.columns)].sort_values(keys).reset_index(drop=True),
            expected.sort_values(keys).reset_index(drop=True),
            check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12,
        )
    except AssertionError as exc:
        raise SnapshotError(f'{label}: agregação não reconcilia com os registros diários') from exc


def validate_frames(frames, summary):
    """Valida o grão antes de permitir métricas; sem corrigir/remover dados."""
    daily, meta = frames['diario'], frames['equipamentos']
    _require(meta, ['identificador', 'km', 'municipio', 'sentido', 'rodovia', 'uf'], 'cadastro')
    if meta.identificador.isna().any() or meta.identificador.duplicated().any():
        raise SnapshotError('cadastro: ID ausente ou duplicado')
    for column in ['identificador', 'municipio', 'sentido']:
        if meta[column].isna().any() or meta[column].astype(str).str.strip().eq('').any():
            raise SnapshotError(f'cadastro: {column} ausente')
    if not meta.km.between(KM_MIN, KM_MAX).all() or not meta.rodovia.eq('BR-101').all() or not meta.uf.eq('SC').all():
        raise SnapshotError('cadastro: localização fora do corredor declarado')
    if not meta.sentido.isin(['Crescente', 'Decrescente']).all():
        raise SnapshotError('cadastro: sentido desconhecido')
    for name, counts in [('diario', ['passagens', 'altas']), ('possiveis_diario', ['possiveis'])]:
        frame = frames[name]
        _require(frame, ['identificador', 'data', 'ano', 'mes', *counts], name)
        if frame.empty or frame.identificador.isna().any() or frame.duplicated(['identificador', 'data']).any():
            raise SnapshotError(f'{name}: chave ID/data vazia, ausente ou duplicada')
        if not frame.identificador.isin(meta.identificador).all():
            raise SnapshotError(f'{name}: ID sem localização cadastrada na base A')
        _dates(frame, name)
        _counts(frame, counts, name)
    if daily.altas.gt(daily.passagens).any():
        raise SnapshotError('diario: numerador supera denominador da mesma base')
    if 'faixas_publicadas' in daily:
        _counts(daily, ['faixas_publicadas'], 'diario')
        if not daily.faixas_publicadas.between(1, 8).all():
            raise SnapshotError('diario: quantidade de faixas desconhecida')
    accidents = frames['acidentes']
    _require(accidents, ['concessionaria', 'data', 'ano', 'km', 'trecho'], 'acidentes')
    _dates(accidents, 'acidentes')
    if not np.isfinite(accidents.km).all():
        raise SnapshotError('acidentes: quilometragem inválida')
    # Repetições de acidentes são preservadas: data/km não é ID de ocorrência.
    _aggregate_matches(frames['anual'], annual_table(daily), ['identificador', 'ano'], 'anual')
    _aggregate_matches(frames['mensal'], monthly_table(daily), ['identificador', 'mes'], 'mensal')
    ids = cohort_ids(frames['anual'])
    if sorted(summary.get('coorte_ids', [])) != ids:
        raise SnapshotError('resumo: população da referência diverge da cobertura observada')
    group = daily.loc[daily.identificador.isin(ids) & daily.ano.isin([2024, 2025])]
    expected = {'coorte_passagens': int(group.passagens.sum()), 'coorte_altas': int(group.altas.sum()),
                'coorte_equipamentos': len(ids), 'equipamentos_trafego': len(meta)}
    for key, value in expected.items():
        if summary.get(key) != value:
            raise SnapshotError(f'resumo: {key} não reconcilia')
    index = weighted_index(group.altas.sum(), group.passagens.sum())
    if not np.isclose(summary.get('coorte_indice_por10mil', np.nan), index, rtol=1e-12):
        raise SnapshotError('resumo: índice agregado não reconcilia')
    if summary.get('taxa_possiveis_infracoes_disponivel') is not False:
        raise SnapshotError('resumo: taxa B/A não validada não pode ser habilitada')


def load_snapshot(processed=PROCESSED, reports=REPORTS, manifest=ROOT/'MANIFESTO_PUBLICACAO.json'):
    """Carrega arquivos fixados no manifesto; PRF é opcional e validado isoladamente."""
    processed, reports = Path(processed), Path(reports)
    try:
        entries = json.loads(Path(manifest).read_text(encoding='utf-8'))['arquivos']
        hashes = {Path(e['caminho']).name: e['sha256'] for e in entries if e['caminho'].startswith('dados_tratados/')}
        frames = {}
        for name in ['diario', 'mensal', 'anual', 'equipamentos', 'possiveis_diario', 'acidentes']:
            path = processed/f'antt_{name}.parquet'
            if hashlib.sha256(path.read_bytes()).hexdigest() != hashes.get(path.name):
                raise SnapshotError(f'Integridade divergente: {path.name}')
            frames[name] = pd.read_parquet(path)
        summary = json.loads((reports/'resumo_antt.json').read_text(encoding='utf-8'))
        validate_frames(frames, summary)
        frames['prf'] = None
        path = processed/'ocorrencias.parquet'
        if path.exists():
            # Fonte opcional não deve derrubar as telas ANTT.
            try:
                if hashlib.sha256(path.read_bytes()).hexdigest() != hashes.get(path.name):
                    raise SnapshotError('Integridade PRF divergente')
                prf = pd.read_parquet(path)
                _require(prf, ['id', 'data', 'ano', 'municipio', 'uf', 'br', 'km'], 'PRF')
                _dates(prf, 'PRF')
                if prf.duplicated(['ano', 'id']).any() or not (prf.uf.eq('SC') & prf.br.eq(101) & prf.km.between(KM_MIN, KM_MAX)).all():
                    raise SnapshotError('PRF: duplicidade ou corredor divergente')
                frames['prf'] = prf
            except (OSError, ValueError, TypeError):
                frames['prf_status'] = 'Contexto PRF indisponível: arquivo não validado.'
        else:
            frames['prf_status'] = 'Contexto PRF indisponível neste pacote.'
        return frames, summary
    except SnapshotError:
        raise
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        raise SnapshotError('Falha ao carregar ou validar o snapshot local') from exc
