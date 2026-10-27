"""SENTINELA: exploração descritiva, evidências e síntese para investigação."""
import json
import logging

import pandas as pd
import streamlit as st

from src.antt import annual_table, context_table, equipment_table, weighted_index
from src.antt_charts import (correlation_detail, coverage_map, evolution, locator,
                             monthly_display, persistence, persistence_data, ranking, road_context)
from src.antt_report import report
from src.sentinel_analysis import coverage_sensitivity, investigation_table, quality_evidence
from src.sentinel_data import load_snapshot
from src.sentinel_sources import (METHOD_VERSION, SNAPSHOT_ID, application_version, format_number,
                                  source_catalog, sources_markdown)

PAGES = ['Visão geral', 'Comparador de equipamentos', 'Evolução e persistência',
         'Contexto rodoviário', 'Relatório preventivo']
NAMES = {'identificador': 'Radar', 'municipio': 'Município', 'km': 'Quilômetro',
         'sentido': 'Sentido da quilometragem', 'ano': 'Ano', 'mes': 'Mês',
         'passagens': 'Contagens publicadas (N)', 'altas': 'Contagens acima de 120 km/h (H)',
         'dias': 'Dias publicados', 'por_10_mil': 'Acima de 120 km/h por 10 mil',
         'indice_exibido': 'Índice exibido por 10 mil', 'cobertura_dias': 'Cobertura de dias do calendário',
         'dias_calendario': 'Dias do ano', 'estado': 'Condição da investigação', 'motivo': 'Evidência',
         'proximo_passo': 'Próximo passo', 'restricoes': 'Restrições', 'data': 'Data',
         'faixas_publicadas': 'Intervalos de velocidade publicados', 'mediana_anual': 'Mediana de N por dia publicado no ano',
         'razao_mediana_anual': 'N / mediana diária anual', 'causa': 'Causa da publicação',
         'segmento': 'Segmento de 5 km', 'equipamentos': 'Radares', 'dias_comuns': 'Datas comuns do segmento',
         'cobertura_dias_comuns': 'Cobertura de datas comuns', 'registros_acidentes': 'Registros ANTT de acidentes',
         'combinacoes_data_km': 'Combinações distintas data/quilômetro', 'limiar_cobertura': 'Cobertura mínima por ano',
         'lat': 'Latitude publicada (base A)', 'lon': 'Longitude publicada (base A)',
         'situacao': 'Situação cadastral em 2026', 'limite_leve_ref_2026': 'Limite de leves: referência 2026 (km/h)',
         'limite_pesado_ref_2026': 'Limite de pesados: referência 2026 (km/h)',
         'contagens_publicadas': 'Contagens B publicadas', 'dias_com_publicacao': 'Datas com publicação B'}
COUNT_COLS = {'ano', 'passagens', 'altas', 'dias', 'dias_calendario', 'equipamentos', 'dias_comuns',
              'registros_acidentes', 'combinacoes_data_km', 'faixas_publicadas', 'contagens_publicadas',
              'dias_com_publicacao', 'limite_leve_ref_2026', 'limite_pesado_ref_2026'}
for _year in [2024, 2025]:
    for _field, _label in [('indice', 'Índice por 10 mil'), ('cobertura', 'Cobertura dos dias'),
                           ('dias', 'Dias publicados'), ('passagens', 'Contagens publicadas (N)'),
                           ('altas', 'Acima de 120 km/h (H)'), ('q75', 'Quartil 75 do grupo fixo')]:
        NAMES[f'{_field}_{_year}'] = f'{_label} em {_year}'
        if _field in {'dias', 'passagens', 'altas'}:
            COUNT_COLS.add(f'{_field}_{_year}')


@st.cache_data(show_spinner=False)
def load():
    return load_snapshot()


def number(value, digits=2):
    return format_number(value, digits=digits) if pd.notna(value) else 'Indisponível'


def table(frame, title):
    """Tabela HTML nativa: alternativa textual ao canvas e à grade interativa."""
    with st.expander(title):
        display = frame.copy()
        for col in display:
            if pd.api.types.is_datetime64_any_dtype(display[col]):
                display[col] = display[col].dt.strftime('%d/%m/%Y').fillna('Indisponível')
            elif col.startswith('cobertura') or col == 'limiar_cobertura':
                display[col] = display[col].map(lambda v: number(v * 100, 2) + '%' if pd.notna(v) else 'Indisponível')
            elif pd.api.types.is_numeric_dtype(display[col]) and not pd.api.types.is_bool_dtype(display[col]):
                digits = 0 if col in COUNT_COLS else 3 if col in {'km', 'lat', 'lon'} else 6
                display[col] = display[col].map(lambda v: number(v, digits))
        display = display.rename(columns=NAMES).fillna('Indisponível')
        st.table(display, hide_index=True)


def local_selection(eq, key, label):
    options = eq.identificador.tolist()
    if key not in st.session_state:
        st.session_state[key] = options[:3]
        st.caption('Seleção inicial: até três radares com os maiores índices do filtro. Você pode alterá-la.')
    else:
        retained = [i for i in st.session_state[key] if i in options]
        if retained != list(st.session_state[key]):
            st.session_state[key] = retained
            st.info('Radares sem registros nos filtros atuais foram removidos da seleção local. Escolha outros se desejar.')
    return st.multiselect(label, options, key=key)


def correlation(frame, x, y, explanation):
    n, rho = correlation_detail(frame, x, y)
    with st.expander('Detalhe técnico da comparação'):
        st.write(f'Pares disponíveis: {n}.')
        if rho is None:
            st.write('Coeficiente indisponível: são necessários ao menos dois pares e valores não constantes.')
        else:
            st.write(f'Coeficiente de Spearman: {number(rho, 6)}. A descrição deste conjunto não estabelece significância ou causalidade.')
        st.write(explanation)


def synthesis(daily, meta, ids, years):
    result = investigation_table(daily, meta, years)
    result = result.loc[result.identificador.isin(ids)]
    st.subheader('O que merece verificação neste recorte')
    highlighted = result.loc[result.padrao_repetido]
    if highlighted.empty:
        highlighted = result.head(3)
    st.write(f'{int(result.padrao_repetido.sum())} ponto(s) com padrão repetido entre {len(result)} consultado(s). Todos os estados estão na tabela de evidências.')
    for row in highlighted.itertuples():
        st.markdown(f'**{row.identificador} · {row.municipio}, km {number(row.km, 3)} — {row.estado}**')
        st.write(row.motivo)
        st.caption(f'Próximo passo: {row.proximo_passo}')
    st.caption('Referência fixa: radares com publicação em pelo menos 90% dos dias de 2024 e de 2025. '
               'Quartis não são recalculados no filtro local. A regra é relativa e não classifica segurança.')
    table(result[['identificador', 'estado', 'motivo', 'proximo_passo', 'restricoes']], 'Evidências e restrições da síntese')


def point_record(daily, meta, annual, ids, years):
    st.subheader('Localizar e consultar um radar')
    points = meta.loc[meta.identificador.isin(ids)].copy()
    valid = points.loc[points.lat.between(-90, 90) & points.lon.between(-180, 180)]
    st.caption('Esquema espacial sem fundo cartográfico. Coordenadas publicadas na base de tráfego A; não validadas em campo. '
               'Clique em um ponto para abrir a ficha, ou use a lista abaixo.')
    # O callback é executado antes da nova renderização: a lista e o desenho consultam a mesma ficha.
    def selected_point():
        state = st.session_state.get('locator', {})
        selection = state.get('selection', {})
        chosen = selection.get('points', [])
        if chosen:
            custom = chosen[0].get('customdata', [])
            if custom and custom[0] in ids:
                st.session_state['point_id'] = custom[0]
    if st.session_state.get('point_id') not in ids:
        st.session_state['point_id'] = ids[0]
    if not valid.empty:
        st.plotly_chart(locator(points, st.session_state['point_id']), key='locator', on_select=selected_point,
                        selection_mode='points', alt='Pontos por longitude e latitude; consulte a tabela e a ficha abaixo.')
    else:
        st.info('Coordenadas válidas indisponíveis. Consulte a ficha textual.')
    point_id = st.selectbox('Radar para consultar', ids, key='point_id')
    row = points.loc[points.identificador.eq(point_id)].iloc[0]
    st.markdown(f"**{point_id} · {row.municipio}, km {number(row.km, 3)} · Quilometragem {row.sentido.lower()}**")
    if pd.isna(row.limite_leve_ref_2026) or pd.isna(row.situacao):
        st.warning('Referência cadastral de 2026 não encontrada para este ponto. A localização exibida vem da base de tráfego.')
    st.caption('Limites cadastrais são referência de 2026 e não determinam os limites históricos de 2024–2025.')
    result = investigation_table(daily, meta, years).loc[lambda d: d.identificador.eq(point_id)]
    finding = result.iloc[0]
    st.write(f"{finding.estado}. {finding.motivo}")
    st.write(f'Próximo passo: {finding.proximo_passo}')
    table(result[['identificador', 'indice_2024', 'q75_2024', 'indice_2025', 'q75_2025', 'cobertura_2024', 'cobertura_2025']],
          'Referência fixa e evidências anuais da regra (2024–2025)')
    point_annual = annual.loc[annual.identificador.eq(point_id) & annual.ano.isin(years)]
    table(point_annual, 'Contagens, índice e cobertura anual do radar')
    table(points[['identificador', 'municipio', 'km', 'sentido', 'lat', 'lon', 'limite_leve_ref_2026', 'limite_pesado_ref_2026', 'situacao']],
          'Tabela de localização e referência cadastral')


def method(daily, meta, selected, ids, years, scope):
    with st.expander('Método, qualidade, versões e fontes oficiais'):
        st.markdown('**Fórmula:** índice = 10.000 × H / N, com N > 0. H e N são somas da mesma base A, ponto e período. '
                    'H contém as contagens nos intervalos 121–140, 141–160 e >160 km/h; N contém todas as contagens publicadas. '
                    'A soma entre radares não representa veículos únicos. O limiar de 120 km/h é analítico, não um limite legal atribuído ao trecho.')
        st.write('Percentual de possíveis infrações (B/A): indisponível por incompatibilidade de universos, faixas e contagens. '
                 'Categoria veicular e faixa física comparável A/B: indisponíveis. “Não classificado” não permite separar leves, pesados ou motos. '
                 'Ausência de linha não comprova zero eventos; dias publicados não comprovam completude diária ou operação contínua.')
        st.write(f'Snapshot: {SNAPSHOT_ID}. Versão da aplicação: {application_version()}.')
        st.write('Seleção solicitada:', scope)
        st.write('Período observado:', f'{selected.data.min():%d/%m/%Y} a {selected.data.max():%d/%m/%Y}')
        st.markdown(sources_markdown())
        st.download_button('Baixar catálogo de fontes e proveniência', json.dumps(source_catalog(), ensure_ascii=False, indent=2),
                           'sentinela_fontes.json', 'application/json')
        sensitivity = coverage_sensitivity(daily, meta)
        st.markdown('**Sensibilidade à cobertura:** cada limiar muda o grupo; não substitui o resultado principal de 90%.')
        table(sensitivity, 'Valores da sensibilidade 80%, 90% e 95%')
        evidence = quality_evidence(daily)
        sample = evidence.loc[evidence.identificador.isin(ids) & evidence.ano.isin(years)]
        st.markdown('**Qualidade da publicação:** menores volumes em relação à mediana dos dias publicados do mesmo radar/ano. '
                    'A ordenação não é um limiar de risco. Nenhum registro foi excluído automaticamente; a causa permanece não confirmada.')
        cols = ['identificador', 'data', 'passagens', 'altas', 'faixas_publicadas', 'mediana_anual', 'razao_mediana_anual', 'causa']
        table(sample.head(20)[cols], 'Até 20 menores razões de volume / mediana na seleção')
        documented = evidence.loc[evidence.caso_documentado]
        st.write(f'Caso documentado de 29/08/2025: {documented.identificador.nunique()} pontos; '
                 f'{number(documented.passagens.sum(), 0)} contagens publicadas. Causa não confirmada.')
        table(documented.loc[documented.identificador.eq('VC101-30'), cols], 'Caso documentado: Criciúma em 29/08/2025')
        table(annual_table(selected), 'Cobertura por radar e ano no filtro atual')
        st.caption('Idioma do documento e alguns controles do framework dependem do Streamlit; esta versão não oferece configuração suportada de idioma. '
                   'As tabelas nativas acima dão alternativa aos gráficos. Conformidade WCAG e leitura assistiva dependem de validação específica.')


def main():
    st.set_page_config(page_title='SENTINELA — ANTT', layout='wide')
    st.markdown('<style>.block-container{padding-top:4rem;max-width:1480px} '
                'h1,h2,h3{color:#142B3C} [data-testid="stSidebar"]{background:#EEF3F5} '
                ':focus-visible{outline:3px solid #087F8C!important;outline-offset:3px} '
                '[data-testid="stTable"]{overflow-x:auto} </style>', unsafe_allow_html=True)
    st.sidebar.title('SENTINELA')
    st.sidebar.caption('Inteligência preventiva em segurança viária · RadarSul é o domínio de hospedagem.')
    page = st.sidebar.radio('Navegação', PAGES, key='page')
    try:
        with st.spinner('Carregando os dados do snapshot selecionado…'):
            frames, summary = load()
    except (OSError, ImportError, ValueError, KeyError, TypeError):
        logging.getLogger(__name__).exception('Falha ao carregar snapshot SENTINELA')
        st.title('SENTINELA')
        st.error('Não foi possível carregar os dados desta versão. Tente novamente. Se o problema continuar, consulte o responsável pela aplicação.')
        if st.button('Tentar novamente'):
            load.clear()
            st.rerun()
        return
    daily, monthly, annual, meta, possible, accidents = [frames[n] for n in ['diario', 'mensal', 'anual', 'equipamentos', 'possiveis_diario', 'acidentes']]
    years = st.sidebar.multiselect('Anos dos registros', sorted(daily.ano.unique().tolist()), default=[2024, 2025], key='years')
    area = st.sidebar.selectbox('Recorte', ['Coorte comparável 2024–2025', 'Todos os equipamentos', 'Criciúma: VC101-30', 'Entorno de Criciúma: km 370 a 410'], key='area')
    ids = summary['coorte_ids'] if area.startswith('Coorte') else meta.identificador.tolist()
    if area.startswith('Criciúma'):
        ids = ['VC101-30']
    if area.startswith('Entorno'):
        ids = meta.loc[meta.km.ge(370) & meta.km.lt(410), 'identificador'].tolist()
    directions = st.sidebar.multiselect('Sentido da quilometragem', sorted(meta.sentido.unique()),
                                       default=sorted(meta.sentido.unique()), key='directions')
    ids = meta.loc[meta.identificador.isin(ids) & meta.sentido.isin(directions), 'identificador'].tolist()
    st.caption('BR-101 SUL DE SANTA CATARINA · CRICIÚMA E REGIÃO')
    st.write('Explore registros de velocidade e veja quais padrões merecem investigação preventiva.')
    st.sidebar.caption(f'Snapshot: {SNAPSHOT_ID}. Grupo principal definido pela publicação em 2024–2025; não certifica outros anos.')
    if not years:
        st.info('Selecione pelo menos um ano para consultar os registros.')
        return
    if not directions:
        st.info('Selecione pelo menos um sentido da quilometragem.')
        return
    selected = daily.loc[daily.ano.isin(years) & daily.identificador.isin(ids)]
    if selected.empty:
        st.info('Não há registros publicados para estes filtros. Isso não comprova ausência de tráfego ou de infrações.')
        return
    eq = equipment_table(selected, meta, years)
    observed_ids = eq.identificador.tolist()
    scope = {'anos_solicitados': sorted(years), 'territorio': area, 'sentidos': directions, 'radares_com_dados_no_filtro_global': observed_ids}
    st.caption(f"{area} · anos solicitados: {', '.join(map(str, sorted(years)))} · {len(eq)} radar(es) com registros · "
               f"observado: {selected.data.min():%d/%m/%Y} a {selected.data.max():%d/%m/%Y} · sentidos: {', '.join(directions)}.")
    st.info('O índice compara contagens nas faixas acima de 120 km/h com todas as contagens publicadas no mesmo ponto e período. '
            'Não é taxa de autuações nem probabilidade de acidente.')
    if set(observed_ids) - set(summary['coorte_ids']):
        st.warning('Há pontos fora do grupo principal de cobertura de 90% em cada ano de 2024–2025. Veja os dias publicados antes de comparar.')
    if set(years) != {2024, 2025}:
        st.warning('Exploração de outros anos: pertencer ao grupo de 2024–2025 não comprova cobertura no período exibido. '
                   'Nenhuma melhora ou piora é inferida de janelas com durações diferentes.')
    if 2026 in years:
        st.caption('2026 parcial neste snapshot: tráfego até 30/06/2026; possíveis infratores até 02/06/2026. Comparações exigem períodos equivalentes.')
    if page == 'Visão geral':
        lead = eq.iloc[0]
        st.title(f'{lead.municipio}, km {number(lead.km, 3)}: maior índice do filtro')
        st.write(f"{lead.identificador}: **{number(lead.por_10_mil)} por 10 mil**. "
                 "Este é o máximo individual; os totais abaixo incluem o conjunto selecionado.")
        total, high = selected.passagens.sum(), selected.altas.sum()
        cols = st.columns(4)
        for col, label, value in zip(cols, ['Radares com registros', 'Contagens publicadas no conjunto', 'Acima de 120 km/h no conjunto', 'Datas distintas no recorte (união)'],
                                     [len(eq), total, high, selected.data.nunique()]):
            col.metric(label, number(value, 0))
        st.write(f'Índice agregado do conjunto: **{number(weighted_index(high, total))} por 10 mil**, calculado pela razão entre somas. '
                 'A união de datas não representa os dias de operação de cada radar.')
        st.plotly_chart(ranking(eq), alt='Ranking dos índices; consulte valores na tabela a seguir.')
        table(eq[['identificador', 'municipio', 'km', 'sentido', 'passagens', 'altas', 'dias', 'por_10_mil']], 'Dados equivalentes ao ranking e totais por radar')
        synthesis(daily, meta, observed_ids, years)
        point_record(daily, meta, annual, observed_ids, years)
    elif page == 'Comparador de equipamentos':
        st.title('Comparar radares')
        chosen = local_selection(eq, 'compare_ids', 'Equipamentos')
        if not chosen:
            st.info('Selecione pelo menos um radar para comparar ou acompanhar o histórico.')
        else:
            show = eq.loc[eq.identificador.isin(chosen), ['identificador', 'municipio', 'km', 'sentido', 'passagens', 'altas', 'dias', 'por_10_mil']]
            table(show, 'Comparação: valores dos radares selecionados')
            export = show.copy()
            export['anos_solicitados'] = ','.join(map(str, sorted(years)))
            export['territorio'] = area
            export['sentidos_solicitados'] = ','.join(directions)
            export['snapshot_id'] = SNAPSHOT_ID
            export['versao_metodo'] = METHOD_VERSION
            observed = selected.loc[selected.identificador.isin(chosen)].groupby('identificador').data.agg(['min', 'max'])
            export['primeira_data_publicada'] = export.identificador.map(observed['min'].dt.strftime('%Y-%m-%d'))
            export['ultima_data_publicada'] = export.identificador.map(observed['max'].dt.strftime('%Y-%m-%d'))
            export['fonte_trafego_url'] = source_catalog()[0]['csv_url']
            export['formula'] = '10000 * altas / passagens; base A; N>0'
            st.download_button('Baixar comparação em CSV', export.to_csv(index=False).encode('utf-8-sig'),
                               f"sentinela_comparacao_{'-'.join(map(str, sorted(years)))}_{'_'.join(chosen)}.csv", 'text/csv')
            st.caption('CSV: UTF-8, separador vírgula, decimal ponto; valores numéricos preservados sem arredondamento visual.')
            aid = [i for i in chosen if i in summary['coorte_ids']]
            if set(years) == {2024, 2025} and len(aid) > 1:
                st.plotly_chart(persistence(annual, aid), alt='Índice anual dos radares selecionados; tabela equivalente a seguir.')
                pairs = persistence_data(annual, aid)
                table(pairs.rename(columns={'ano_2024': 'Índice em 2024 (por 10 mil)', 'ano_2025': 'Índice em 2025 (por 10 mil)'}), 'Valores equivalentes à comparação anual')
                correlation(pairs, 'ano_2024', 'ano_2025', 'Mede a semelhança da ordenação entre os anos; não mede chance de acidente nem mudança causal.')
            else:
                st.info('Comparação anual: selecione ambos os anos de 2024–2025 e ao menos dois radares do grupo principal. Um ponto não permite correlação.')
            b = possible.loc[possible.ano.isin(years) & possible.identificador.isin(chosen)]
            st.subheader('Possíveis infratores: base B separada')
            if b.empty:
                st.info('Sem linhas da base B neste recorte. Isso não comprova zero infrações.')
            else:
                table(b.groupby('identificador', as_index=False).agg(contagens_publicadas=('possiveis', 'sum'), dias_com_publicacao=('data', 'nunique')),
                      'Contagens da base B, sem divisão pelo tráfego')
            st.caption('Percentual B/A indisponível: as contagens das bases não são compatíveis.')
    elif page == 'Evolução e persistência':
        st.title('Histórico de velocidade')
        chosen = local_selection(eq, 'history_ids', 'Equipamentos no histórico')
        if chosen:
            st.plotly_chart(evolution(monthly, chosen, years), alt='Série mensal dos radares selecionados; valores e lacunas na tabela.')
            st.plotly_chart(coverage_map(monthly, chosen, years), alt='Matriz temporal dos mesmos radares; valores e lacunas na tabela.')
            history = monthly_display(monthly, chosen, years)
            history = history.loc[history.mes.str[:4].astype(int).isin(years)]
            table(history[['identificador', 'mes', 'passagens', 'altas', 'dias', 'cobertura_dias', 'indice_exibido', 'estado']].rename(columns={'estado': 'Disponibilidade do índice'}),
                  'Dados equivalentes à série e à matriz temporal')
        else:
            st.info('Selecione pelo menos um radar para comparar ou acompanhar o histórico.')
        st.caption('Lacunas: menos de 80% dos dias do mês publicados, ausência de registro ou ano fora da seleção. Ausência não vira zero.')
    elif page == 'Contexto rodoviário':
        st.title('Acidentes no contexto')
        st.subheader('1. Segmentos de 5 km com datas comuns')
        ctx = pd.DataFrame()
        if set(years) == {2024, 2025}:
            ctx = context_table(daily, meta, accidents, [i for i in observed_ids if i in summary['coorte_ids']], years)
            if not ctx.empty:
                st.plotly_chart(road_context(ctx), alt='Registros por segmento nas datas comuns; tabela equivalente a seguir.')
                table(ctx[['segmento', 'equipamentos', 'dias_comuns', 'cobertura_dias_comuns', 'passagens', 'altas', 'por_10_mil', 'registros_acidentes', 'combinacoes_data_km']], 'Dados equivalentes aos segmentos de 5 km')
                correlation(ctx, 'por_10_mil', 'registros_acidentes', 'Datas comuns podem diferir entre segmentos. Não mede risco, causalidade ou proteção; não há exposição em veículos-quilômetro compatível.')
            else:
                st.info('Contexto principal indisponível: nenhum segmento elegível neste recorte. Consulte o envelope abaixo.')
        else:
            st.info('A comparação principal usa 2024–2025. O envelope abaixo usa os anos solicitados sem inferência anual.')
        st.caption('Cada segmento usa apenas datas em que todos os seus radares selecionados publicaram; acidentes não são multiplicados por radar.')
        st.subheader('2. Envelope de consulta dos pontos selecionados')
        km = meta.loc[meta.identificador.isin(observed_ids), 'km']
        lower, upper = max(244.68, float(km.min()) - 2.5), min(465.1, float(km.max()) + 2.5)
        local = accidents.loc[accidents.ano.isin(years) & accidents.km.between(lower, upper)]
        unavailable_years = sorted(set(years) - set(accidents.ano.unique()))
        if unavailable_years:
            st.info(f'Contexto ANTT indisponível para {", ".join(map(str, unavailable_years))}: a base de acidentes não cobre esses anos. Ausência não é zero eventos.')
        else:
            st.write(f'{number(len(local), 0)} registros ANTT no envelope de km {number(lower, 3)} a {number(upper, 3)}, '
                     'com margem de 2,5 km. Não são atribuídos a um radar; este envelope não é a amostra dos segmentos acima.')
        st.warning('Repetições de data/quilômetro são preservadas por falta de ID único. Poucos registros não demonstram segurança. Não há taxa por exposição.')
        st.subheader('3. PRF: contexto independente do corredor integral')
        prf = frames.get('prf')
        if prf is not None and set(years).issubset(set(prf.ano.unique())):
            prf = prf.loc[prf.ano.isin(years)]
            st.write(f'{number(len(prf), 0)} registros PRF no corredor integral nos anos solicitados; '
                     f'{number(prf.municipio.eq("CRICIUMA").sum(), 0)} em Criciúma. Não somar às contagens ANTT. '
                     'Este contexto não acompanha a seleção local de radares.')
        else:
            st.info('Contexto PRF indisponível neste snapshot.')
    else:
        st.title('Síntese para investigação')
        choice = st.selectbox('Escopo', ['Todos os equipamentos do filtro', *observed_ids])
        frame = selected if choice.startswith('Todos') else selected.loc[selected.identificador.eq(choice)]
        report_scope = {**scope, 'ids_efetivos_no_relatorio': sorted(frame.identificador.unique().tolist())}
        document = report(frame, meta, annual, possible, choice, years=years, scope=report_scope, all_daily=daily, accidents=accidents)
        st.download_button('Baixar relatório com fontes e limites', document.encode('utf-8'), 'SENTINELA_relatorio_preventivo.md', 'text/markdown')
        st.markdown(document)
    method(daily, meta, selected, observed_ids, years, scope)


if __name__ == '__main__':
    main()
