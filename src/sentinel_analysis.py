"""Regras descritivas para investigação, sem classificação de risco ou previsão.

As funções recebem o snapshot diário completo. Filtros de exibição só devem ser
aplicados ao resultado, preservando a população dos quartis de referência.
"""
import numpy as np
import pandas as pd

from src.antt import annual_table, cohort_ids, equipment_table, validate_daily, weighted_index

REPEATED = 'Padrão repetido para investigação'
NOT_OBSERVED = 'Regra não observada'
INSUFFICIENT = 'Dados insuficientes para a regra'
LIMITS = ('Regra relativa aos registros publicados; cobertura de dias não comprova '
          'completude das faixas nem operação contínua. Não classifica segurança '
          'ou risco de acidente. A causa de variações na publicação não foi confirmada.')


def investigation_table(daily, metadata, years=(2024, 2025)):
    """Síntese por ID; Q75 anual (interpolação linear) do grupo fixo 90%/90%.

    Dados fora de 2024/2025 permanecem descritivos e não recebem interpretação
    automática de melhora/piora. A chamada requer daily completo, nunca seleção.
    """
    annual = annual_table(daily)
    reference_ids = cohort_ids(annual)
    reference = annual.loc[annual.identificador.isin(reference_ids)]
    q = reference.loc[reference.ano.isin([2024, 2025])].groupby('ano').por_10_mil.quantile(.75)
    # Reuse the checked one-to-one dimensions, retaining every observed point.
    all_years = sorted(daily.ano.unique().tolist())
    points = equipment_table(daily, metadata, all_years)
    result = points[['identificador', 'municipio', 'km', 'sentido']].copy()
    for year in [2024, 2025]:
        subset = annual.loc[annual.ano.eq(year), ['identificador', 'passagens', 'altas', 'dias', 'cobertura_dias', 'por_10_mil']]
        subset = subset.rename(columns={c: f'{name}_{year}' for c, name in [('passagens', 'passagens'), ('altas', 'altas'), ('dias', 'dias'), ('cobertura_dias', 'cobertura'), ('por_10_mil', 'indice')]})
        result = result.merge(subset, on='identificador', how='left', validate='one_to_one')
        result[f'q75_{year}'] = q.get(year, np.nan)
    result['referencia_equipamentos'] = len(reference_ids)
    result['referencia'] = 'Grupo fixo com ≥90% dos dias de 2024 e de 2025; quartil por interpolação linear'
    calculable = (np.isfinite(result.indice_2024) & np.isfinite(result.indice_2025)
                  & result.passagens_2024.gt(0) & result.passagens_2025.gt(0)
                  & np.isfinite(result.q75_2024) & np.isfinite(result.q75_2025))
    result['elegivel'] = result.identificador.isin(reference_ids) & calculable & (set(years) == {2024, 2025})
    result['padrao_repetido'] = (result.elegivel & result.indice_2024.ge(result.q75_2024)
                                & result.indice_2025.ge(result.q75_2025))
    result['estado'] = np.select([~result.elegivel, result.padrao_repetido], [INSUFFICIENT, REPEATED], default=NOT_OBSERVED)
    result['restricoes'] = LIMITS
    reasons, steps = [], []
    for row in result.itertuples():
        if set(years) != {2024, 2025}:
            reason = 'A regra exige conjuntamente 2024 e 2025; outros períodos são exploração descritiva.'
            step = 'Selecione 2024 e 2025 para consultar a regra; confira a cobertura de cada período.'
        elif not row.elegivel:
            reason = 'O ponto não tem cobertura de dias ≥90% e índice calculável em cada ano de 2024 e 2025.'
            step = 'Conferir lacunas de publicação e esclarecer a completude com o publicador antes de comparar.'
        elif row.padrao_repetido:
            reason = 'Índice entre os 25% maiores do grupo fixo nos dois anos, incluindo empates no quartil.'
            step = 'Conferir publicação e estabilidade do padrão; investigar condições locais com responsável técnico.'
        else:
            reason = 'Este ponto não atende à regra de repetição do grupo. Isso não permite classificá-lo como seguro.'
            step = 'Examinar a série e a qualidade dos registros; a ausência desta regra não dispensa investigação.'
        reasons.append(reason)
        steps.append(step)
    result['motivo'], result['proximo_passo'] = reasons, steps
    return result.sort_values('identificador').reset_index(drop=True)


def quality_evidence(daily):
    """Ordenação exploratória de publicação; nenhum registro é excluído.

    O caso documentado identifica a data para consulta, não uma classe automática
    de erro. Razão zero representa zero publicado; ausência continua ausente.
    """
    validate_daily(daily)
    result = daily.copy()
    medians = daily.groupby(['identificador', 'ano']).passagens.median().rename('mediana_anual')
    result = result.merge(medians, on=['identificador', 'ano'], how='left', validate='many_to_one')
    result['razao_mediana_anual'] = result.passagens / result.mediana_anual.where(result.mediana_anual.gt(0))
    result['caso_documentado'] = result.data.eq(pd.Timestamp('2025-08-29'))
    result['causa'] = 'Não confirmada; não excluir registros automaticamente.'
    result['interpretacao'] = ('Compare o volume publicado e as faixas observadas com a mediana dos dias '
                               'publicados do mesmo radar/ano; a causa de diferenças não foi confirmada.')
    result.loc[result.caso_documentado, 'interpretacao'] = (
        'Volume publicado muito inferior à mediana dos dias deste radar. A causa não foi confirmada; '
        'confira a origem antes de interpretar como mudança no tráfego.')
    return result.sort_values(['razao_mediana_anual', 'identificador', 'data'], na_position='last').reset_index(drop=True)


def coverage_sensitivity(daily, metadata):
    """Grupos alternativos por cobertura; preserva dados e não mistura populações."""
    annual = annual_table(daily)
    rows = []
    for threshold in [.8, .9, .95]:
        ids = cohort_ids(annual, threshold)
        eq = equipment_table(daily.loc[daily.identificador.isin(ids)], metadata)
        total, high = eq.passagens.sum(), eq.altas.sum()
        rows.append({'limiar_cobertura': threshold, 'equipamentos': len(ids),
                     'passagens': int(total), 'altas': int(high),
                     'por_10_mil': weighted_index(high, total)})
    return pd.DataFrame(rows)
