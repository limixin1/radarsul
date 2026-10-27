"""Catálogo do snapshot: metadados históricos não são uma nova coleta oficial."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
METHOD_VERSION = '2.1-descritivo'
FORMULA = 'I = (H / N) × 10.000, se N > 0; H e N são somas da própria base A no mesmo equipamento e período.'
BLOCKED_RATIO = ('Taxa B/A bloqueada: a equivalência física dos códigos de faixa e das categorias de veículo '
                 'não foi demonstrada; há unidades B sem denominador e contagens B superiores a A. '
                 'Agregar por ID/data não corrige essa incompatibilidade.')


def _snapshot_id():
    try:
        manifest = json.loads((ROOT / 'MANIFESTO_PUBLICACAO.json').read_text(encoding='utf-8'))
        entries = sorted((r['caminho'], r['sha256']) for r in manifest['arquivos']
                         if r['caminho'].startswith('dados_tratados/') and r['caminho'].endswith('.parquet'))
        if not entries:
            return 'snapshot não identificado'
        payload = '\n'.join(f'{path}:{digest}' for path, digest in entries)
        return 'snapshot-' + hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]
    except (OSError, ValueError, KeyError, TypeError):
        # O carregador valida/bloqueia o snapshot; o catálogo ainda pode explicar a falha.
        return 'snapshot não identificado'


SNAPSHOT_ID = _snapshot_id()


def format_number(value, digits=2):
    """Representação pt-BR sem transformar ausência/NaN/infinito em zero."""
    try:
        if value is None or not math.isfinite(float(value)):
            return 'indisponível'
        return f'{value:,.{digits}f}'.translate(str.maketrans({',': '.', '.': ','}))
    except (TypeError, ValueError):
        return 'indisponível'


def application_version():
    """Commit desta execução; isso não confirma a versão publicada em produção."""
    render_commit = os.environ.get('RENDER_GIT_COMMIT', '')
    if re.fullmatch(r'[0-9a-fA-F]{40,64}', render_commit):
        return render_commit[:12]
    try:
        commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], check=True,
                                capture_output=True, text=True, timeout=3).stdout.strip()
        dirty = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], check=True,
                               capture_output=True, text=True, timeout=3).stdout.strip()
        return commit[:12] + (' + alterações locais' if dirty else '')
    except (OSError, subprocess.SubprocessError):
        return 'versão da aplicação não identificada'


def source_catalog():
    records = json.loads((ROOT / 'dados_brutos/coleta_20261026T224903Z.json').read_text(encoding='utf-8'))
    definitions = [
        ('A', 'Volume de tráfego da ViaCosteira', '2022-01-01 a 2026-06-30', '2026-07-28',
         'volume-radar', '7d32f5d1-7a5d-403b-8db5-09e7e11addf1/download/dicionario_de_dados_volume_radar.pdf',
         'Contagens publicadas por equipamento/data e faixas; não são veículos únicos.',
         'Completude horária desconhecida; ausência de faixa não demonstra zero; categorias veiculares indisponíveis.'),
        ('B', 'Possíveis infratores da ViaCosteira', '2022-12-30 a 2026-06-02', '2026-07-28',
         'quantidade-possiveis-infratores', 'd69fc6e3-c693-47b2-b1cc-aa0c05e734a9/download/dicionario_dados_surod_quantidade_possiveis_infratores.pdf',
         'Contagens publicadas de possíveis infratores; não são autuações confirmadas.', BLOCKED_RATIO),
        ('C', 'Acidentes por quilômetro da ViaCosteira', '2021-05-01 a 2025-12-31', '2026-01-28',
         'acidentes-quilometro-rodovias', '3d9e26ca-5d8f-4854-9744-836e8bcb088e/download/dicionario_dados_surod_acidentes_km.pdf',
         'Linhas administrativas por data/km; sem identificador único de ocorrência.',
         'Repetições preservadas; não somar com PRF, atribuir ao radar ou inferir causalidade.'),
        ('D', 'Cadastro de radares — referência junho/2026', 'Referência cadastral junho/2026', '2026-07-28',
         'radar', 'b10de933-f8fa-4f13-8a40-a87759b0b4c9/download/radar_dicionario_dados.pdf',
         'Registro cadastral; associação exata por rodovia/UF/km/sentido.',
         'Não comprova limites históricos ou operação; VC101-20 permanece sem correspondência cadastral.'),
    ]
    records_by_filename = {r['arquivo']: r for r in records}
    filenames = ['volume-radar-viacosteira.csv', 'quantidade-possiveis-infratores-viacosteira.csv',
                 'demostrativo_acidentes_viacosteira.csv', 'dados-dos-radares6_2026.csv']
    result = []
    for filename, definition in zip(filenames, definitions):
        r = records_by_filename[filename]
        code, name, period, updated, slug, dictionary, unit, limitations = definition
        dataset_root = r['url'].split('/resource/')[0]
        resource_id = r['url'].split('/resource/')[1].split('/')[0]
        result.append(dict(code=code, name=name,
                           page_url=f'https://dados.antt.gov.br/dataset/{slug}/resource/{resource_id}',
                           csv_url=r['url'], dictionary_url=f'{dataset_root}/resource/{dictionary}',
                           collected_at_utc=r['acesso_utc'], sha256=r['sha256'], period=period,
                           resource_updated_at=updated,
                           metadata_status='Data de atualização relatada pela auditoria Work em 27/10/2026; não revalidada nesta execução.',
                           status='snapshot; novo download não confirmado', unit=unit, limitations=limitations))
    return result


def sources_markdown():
    parts = [f'**Snapshot:** `{SNAPSHOT_ID}`. **Método:** `{METHOD_VERSION}`.',
             '**Fórmula:** ' + FORMULA,
             'H: contagens nas faixas 121–140, 141–160 e >160 km/h. N: todas as contagens publicadas comparáveis de A. '
             '120 km/h é um limiar analítico, sem equivalência a infração legal, velocidade média ou risco de acidente.',
             '**' + BLOCKED_RATIO + '**',
             'Este painel usa arquivos tratados locais. Os hashes dos CSV abaixo são os declarados no manifesto histórico; '
             'os CSV originais não acompanham este pacote e não foram revalidados nesta execução. '
             'Uma resposta HTTP 200 com HTML não confirma um CSV válido. '
             'Data de atualização do portal, período dos registros e coleta são informações diferentes.']
    for r in source_catalog():
        parts.append(f"### {r['code']} — {r['name']}\n\n"
                     f"[Página oficial]({r['page_url']}) · [CSV oficial]({r['csv_url']}) · [Dicionário]({r['dictionary_url']})\n\n"
                     f"Período: {r['period']}. Coleta declarada (UTC): {r['collected_at_utc']}. "
                     f"Atualização do recurso relatada: {r['resource_updated_at']}. {r['metadata_status']}\n\n"
                     f"SHA-256 declarado: `{r['sha256']}`. Estado: **{r['status']}**.\n\n"
                     f"Unidade: {r['unit']} Limitações: {r['limitations']}")
    return '\n\n'.join(parts)
