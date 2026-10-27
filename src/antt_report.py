"""Relatório autossuficiente; dados e limites acompanham a seleção exportada."""
from __future__ import annotations

import pandas as pd
from src.antt import annual_table, context_table, weighted_index
from src.sentinel_sources import (METHOD_VERSION, SNAPSHOT_ID, application_version,
                                  format_number, sources_markdown)


def _text(value):
    """Preservar campos de dados como texto em tabelas Markdown."""
    return str(value).replace('|', '\\|').replace('\n', ' ')


def _scope_text(scope):
    if scope is None:
        return 'Não informado; os IDs e as datas observadas abaixo definem o recorte efetivo.'
    if isinstance(scope, dict):
        return '; '.join(f'{_text(k)}: {_text(v)}' for k, v in scope.items())
    return _text(scope)


def _context_section(daily, metadata, accidents, ids, years):
    if accidents is None or accidents.empty:
        return ('Contexto de acidentes não calculado neste relatório: base não fornecida ou sem registros disponíveis. '
                'Isso não indica ausência de acidentes.')
    available_years = set(accidents.ano.unique())
    if not set(years).issubset(available_years):
        return ('Contexto de acidentes não calculado: a base C não tem registros em todos os anos solicitados da seleção. '
                'Ausência de publicação não é zero acidentes.')
    ctx = context_table(daily, metadata, accidents, ids, years)
    if ctx.empty:
        return 'Contexto de acidentes não calculado: sem segmento com datas comuns publicadas para o recorte.'
    table = ['| Segmento | Equipamentos | Dias comuns | Registros ANTT |',
             '|---|---:|---:|---:|']
    for r in ctx.itertuples():
        table.append(f'| {_text(r.segmento)} | {r.equipamentos} | {r.dias_comuns} | {r.registros_acidentes} |')
    return ('Contexto calculado em segmentos disjuntos de 5 km, somente nas mesmas datas publicadas em A '
            'por todos os pontos selecionados de cada segmento; acidentes não são multiplicados por radar. '
            f'Quantidade de segmentos: {len(ctx)}; anos {", ".join(map(str, years))}. Não representa taxa por viagem ou atribuição ao equipamento.\n\n'
            + '\n'.join(table))


def report(daily, metadata, annual, possible, selection='Seleção do usuário', *,
           years=None, scope=None, all_daily=None, accidents=None):
    """`annual` é mantido por compatibilidade; evidência anual é recalculada do recorte.

    `all_daily`, quando fornecido, precisa ser a base A completa para a referência
    fixa da síntese. Nunca se infere esse grupo de uma seleção de poucos pontos.
    """
    requested_years = sorted(set(years if years is not None else daily.ano.unique()))
    daily = daily.loc[daily.ano.isin(requested_years)].copy()
    prefix = (f'# SENTINELA — Relatório preventivo\n\n'
              f'**Seleção:** {_text(selection)}. **Filtros solicitados:** {_scope_text(scope)}\n\n'
              f'**Anos solicitados:** {", ".join(map(str, requested_years)) or "nenhum"}. '
              f'**Snapshot:** `{SNAPSHOT_ID}`. **Método:** `{METHOD_VERSION}`. '
              f'**Versão desta execução:** `{application_version()}`; não confirma a versão em produção.\n\n')
    if daily.empty:
        return prefix + ('Sem registros para o filtro. Nenhum indicador ou contexto de acidentes calculado. '
                         'Ausência de linhas não comprova ausência de passagens ou eventos.\n\n' + sources_markdown())
    ids = sorted(daily.identificador.unique())
    observed_years = sorted(daily.ano.unique())
    total, high = int(daily.passagens.sum()), int(daily.altas.sum())
    idx = weighted_index(high, total)
    met = metadata.loc[metadata.identificador.isin(ids)]
    ay = annual_table(daily)
    location = ['| ID | Município | Km publicado | Sentido publicado |', '|---|---|---:|---|']
    for r in met.itertuples():
        location.append(f'| {_text(r.identificador)} | {_text(r.municipio)} | {format_number(r.km, 3)} | {_text(r.sentido)} |')
    details = ['| ID | Ano | H acima de 120 | N publicado | Dias com linhas | Dias do ano | Cobertura do ano | Índice por 10 mil |',
               '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in ay.itertuples():
        details.append(f'| {_text(r.identificador)} | {r.ano} | {format_number(r.altas, 0)} | '
                       f'{format_number(r.passagens, 0)} | {r.dias} | {r.dias_calendario} | '
                       f'{format_number(100*r.cobertura_dias, 1)}% | {format_number(r.por_10_mil, 3)} |')
    keys = daily[['identificador', 'data']].drop_duplicates()
    b = possible.merge(keys, on=['identificador', 'data'], how='inner', validate='many_to_one')
    b_text = (f'Na interseção de ID/data com A selecionada há {format_number(b.possiveis.sum(), 0)} '
              f'contagens publicadas de B em {b.data.nunique()} datas distintas. '
              f'{len(keys)} equipamentos-dia têm A; {len(b[["identificador", "data"]].drop_duplicates())} têm linhas B correspondentes. '
              'A interseção alinha datas, mas não torna as populações comparáveis. '
              'Ausência de linha B não representa zero infrações; não são autuações confirmadas.') if not b.empty else (
              'Sem registros B na interseção ID/data com A selecionada. Contagem indisponível; não equivale a zero infrações.')
    synthesis = ('Síntese de referência não calculada: a base completa A não foi fornecida. '
                 'Não se define quartil a partir desta seleção; os indicadores acima são descritivos.')
    quality = ('Completude horária desconhecida. Dias com linhas não comprovam operação contínua ou publicação de todas as faixas. '
               'Ausência de faixa não foi preenchida com zero; nenhum registro foi excluído automaticamente nesta consulta.')
    if all_daily is not None:
        from src.sentinel_analysis import investigation_table, quality_evidence
        conclusions = investigation_table(all_daily, metadata, years=requested_years)
        conclusions = conclusions.loc[conclusions.identificador.isin(ids)]
        synthesis_parts = []
        for r in conclusions.itertuples():
            synthesis_parts.append(
                f'### {_text(r.identificador)} — {_text(r.estado)}\n\n{_text(r.motivo)}\n\n'
                f'Referência fixa: {r.referencia_equipamentos} pontos com cobertura ≥90% em cada ano de 2024/2025. '
                f'Q75 de 2024: {format_number(r.q75_2024, 6)}; Q75 de 2025: {format_number(r.q75_2025, 6)} por 10 mil. '
                'A regra exige índice ≥ Q75 nos dois anos; os limiares não são limites legais ou de segurança.\n\n'
                'Evidência do ponto no snapshot completo usado pela regra (pode ser mais amplo que o recorte acima):\n\n'
                '| Ano | H | N | Dias | Índice por 10 mil |\n|---|---:|---:|---:|---:|\n'
                f'| 2024 | {format_number(r.altas_2024, 0)} | {format_number(r.passagens_2024, 0)} | '
                f'{format_number(r.dias_2024, 0)} | {format_number(r.indice_2024, 6)} |\n'
                f'| 2025 | {format_number(r.altas_2025, 0)} | {format_number(r.passagens_2025, 0)} | '
                f'{format_number(r.dias_2025, 0)} | {format_number(r.indice_2025, 6)} |\n\n'
                f'Próximo passo: {_text(r.proximo_passo)}\n\nRestrições: {_text(r.restricoes)}')
        synthesis = '\n\n'.join(synthesis_parts)
        evidence = quality_evidence(all_daily)
        evidence = evidence.merge(keys, on=['identificador', 'data'], how='inner', validate='many_to_one')
        documented = evidence.loc[evidence.caso_documentado]
        if not documented.empty:
            quality += (f' No dia documentado 29/08/2025, quantidade de pontos deste recorte: {len(documented)}; '
                        f'contagens publicadas: {format_number(documented.passagens.sum(), 0)}. Causa não confirmada; '
                        'volume reduzido é sinal de publicação a investigar, sem concluir defeito de medição.')
    return prefix + f'''**Anos observados:** {', '.join(map(str, observed_years))}. **Datas publicadas:** {daily.data.min():%d/%m/%Y} a {daily.data.max():%d/%m/%Y}.
**Equipamentos observados:** {len(ids)}. **União de datas com linhas:** {daily.data.nunique()} (não são dias de operação de cada sensor).

## Localização publicada na base A

{chr(10).join(location)}

As coordenadas e o km são referências administrativas, sem validação em campo. O cadastro D é referência de junho/2026 e não prova limites históricos; não associar por vizinho um ID sem correspondência exata.

## Observação descritiva da seleção

| Medida da própria base A | Resultado |
|---|---:|
| N — Contagens publicadas | {format_number(total, 0)} |
| H — Contagens nas faixas acima de 120 km/h | {format_number(high, 0)} |
| Índice agregado: H / N × 10.000 | {format_number(idx, 3)} |

É uma razão entre somas da mesma base, ponto e período; não é média simples de índices. Não são veículos únicos, frequência legal de infrações ou probabilidade de acidente.

## Cobertura e valores anuais da seleção

{chr(10).join(details)}

Cobertura do ano usa 365/366 dias, inclusive em 2026 parcial. Não comparar janelas parciais como anos completos ou interpretar diferenças como melhora/piora automática. Grupo de referência: pontos com pelo menos 90% dos dias em cada ano de 2024 e 2025; pertencer ao grupo não certifica a cobertura de outros anos.

## Síntese para investigação

{synthesis}

Esta regra é relativa ao grupo, sem classe absoluta de risco, previsão de acidente ou recomendação automática de fiscalização/obra.

## Qualidade e incerteza

{quality}

## Possíveis infratores — base B separada

{b_text}

## Contexto de acidentes

{_context_section(daily, metadata, accidents, ids, requested_years)}

Acidentes ANTT não têm ID único de ocorrência. Repetições de dia/km são preservadas. Não somar ANTT e PRF, atribuir acidentes ao radar ou interpretar associação como causalidade ou efeito protetor da velocidade.

## Método, fontes e proveniência

{sources_markdown()}
'''
