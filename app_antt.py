"""SENTINELA: consulta histórica de contagens publicadas, com cobertura explícita."""
import json
import logging
from dataclasses import replace
from time import perf_counter
import pandas as pd
import streamlit as st
from config import ROOT, KM_MIN, KM_MAX
from src.antt import context_table, weighted_index
from src.chart_locale import PT_BR
from src.antt_charts import ranking, evolution, persistence, persistence_data, coverage_map, road_context, correlation, monthly_grid
from src.data_package import validate, token, MANIFEST
from src.query import PAGES, AREAS, YEARS, DIRECTIONS, POLICY, area_ids, query_tables, point_label, display_table, source_result, parse_url, url_state, br
from src.corridor_map import segment_shapes
from src.exports import APP_VERSION, metadata, markdown_report, csv_bytes, bundle, filename, code_version
from src.map_view import normalize_focus, positions, render_locator
from src.preventive import build_card
from src.spatial import ROAD_SOURCE, city_options, road

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
LOG=logging.getLogger('sentinela')
LOG.setLevel(logging.INFO)

@st.cache_data(show_spinner=False)
def load(package_token):
    started=perf_counter()
    result=validate(allow_missing_prf=True)
    LOG.info('pacote_validado snapshot=%s segundos=%.3f',result[0]['versao'],perf_counter()-started)
    return result

@st.cache_data(show_spinner=False, max_entries=8)
def consult(package_token, ids, years):
    """Cache limitado e versionado; Streamlit devolve cópias por chamada."""
    manifest, frames, _ = load(package_token)
    return query_tables(frames['antt_diario'], frames['antt_equipamentos'],
                        ids, years, manifest['cobertura']['trafego'])

CSS='''<style>
.block-container{padding-top:4.5rem;max-width:1480px}
[data-testid="stCaptionContainer"]{opacity:1!important;color:#142B3C!important}
[data-testid="stCaptionContainer"] p{color:#142B3C!important;opacity:1!important}
button:focus-visible,a:focus-visible,input:focus-visible,summary:focus-visible,[tabindex]:focus-visible,[role="combobox"]:focus-visible{outline:3px solid #075E68!important;outline-offset:3px}
p,li,h1,h2,h3{overflow-wrap:anywhere}
[data-testid="stMarkdownContainer"] table{display:block;max-width:100%;overflow-x:auto}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}h1{font-size:1.8rem!important}[data-testid="stMetricValue"]{font-size:1.6rem} [data-testid="stHorizontalBlock"]{flex-wrap:wrap} [data-testid="stColumn"]{min-width:200px;flex:1 1 100%}}
@media print{
[data-testid="stSidebar"],header,button{display:none!important}
.block-container{padding:0!important}
/* O relatório completo substitui as grades interativas na impressão. */
[data-testid="stMainBlockContainer"]:has(.st-key-print_report)>[data-testid="stVerticalBlock"]>:not(.st-key-print_report):not(:has(.st-key-print_report)){display:none!important}
.st-key-print_report [data-testid="stMarkdownContainer"] table{display:table;width:100%;table-layout:auto;overflow:visible}
.st-key-print_report th,.st-key-print_report td{overflow-wrap:normal;font-size:9pt;padding:4px}
.st-key-print_report td{white-space:nowrap}
.st-key-print_report p,.st-key-print_report li{font-size:9.5pt;line-height:1.35;orphans:3;widows:3}
.st-key-print_report p{margin:0 0 6pt}
.st-key-print_report h1{font-size:22pt}
.st-key-print_report h2{font-size:15pt}
.st-key-print_report thead{display:table-header-group}
.st-key-print_report tr{break-inside:avoid}
.st-key-print_report h1,.st-key-print_report h2,.st-key-print_report h3{break-after:avoid}
}
</style>'''


def reset():
    for k in list(st.session_state):del st.session_state[k]
    st.query_params.clear()

def select_all_area():
    st.session_state.area=AREAS[1]
    sync()

def sync():
    s=st.session_state
    if all(k in s for k in ['page','years','area','directions','city','points']):
        st.query_params.from_dict(url_state(s.page,s.years,s.area,s.directions,s.city,s.points,s.get("focus")))

def table(t,label):
    # HTML table is an accessible alternative to the interactive canvas grid.
    formatted=display_table(t)
    st.dataframe(formatted,hide_index=True,width='stretch')
    with st.expander('Tabela para leitura e teclado — '+label):st.table(formatted)

def chart(fig,summary,t,label,export_name):
    st.write(summary)
    fig.add_annotation(text='Snapshot '+export_name.split('_')[1]+'<br>Consulta '+export_name.split('_')[2],x=0,y=0,yshift=-132,yanchor='top',xref='paper',yref='paper',showarrow=False,xanchor='left',font=dict(size=12,color='#142B3C'))
    fig.update_layout(margin_b=190)
    st.plotly_chart(fig,width='stretch',theme=None,config={'locale':'pt-BR','locales':{'pt-BR':PT_BR},'displayModeBar':True,'displaylogo':False,'toImageButtonOptions':{'format':'png','filename':export_name,'width':1100,'height':650,'scale':1}})
    with st.expander('Dados e resumo do gráfico — '+label):st.table(display_table(t))

def sources_for(frames,ids,years,manifest,meta):
    points=meta.loc[meta.identificador.isin(ids),'km']
    left=max(KM_MIN,float(points.min())-2.5) if len(points) else KM_MIN
    right=min(KM_MAX,float(points.max())+2.5) if len(points) else KM_MAX
    a=frames['antt_acidentes'].loc[lambda x:x.km.between(left,right)]
    sources=[source_result('ANTT — envelope contínuo',a,years,manifest['cobertura']['antt'],f'BR-101/SC, km {br(left,3)} a {br(right,3)}, margem de 2,5 km entre pontos; ambos os sentidos')]
    prf=frames.get('ocorrencias')
    prf_result=source_result('PRF — trecho integral',prf,years,manifest['cobertura']['prf'],f'BR-101/SC, km {br(KM_MIN,3)} a {br(KM_MAX,3)}; ambos os sentidos; independente da seleção de pontos')
    if prf_result.quantidade is not None:
        city_count=len(prf.loc[prf.ano.isin(prf_result.anos_cobertos)&prf.municipio.eq('CRICIUMA')])
        prf_result=replace(prf_result,nota=prf_result.nota+f' Desses registros do trecho, {br(city_count)} têm município Criciúma nos anos disponíveis. Não são atribuídos a um radar.')
    sources.append(prf_result)
    return sources

def main():
    started=perf_counter()
    stages={}
    st.set_page_config(page_title='SENTINELA — consulta BR-101/SC',layout='wide',menu_items={'Report a bug':'https://github.com/limixin1/radarsul/issues/new'})
    st.markdown(CSS,unsafe_allow_html=True)
    # st.html supports non-iframed, static JS in this pinned Streamlit version.
    # Keep localized labels and numerical punctuation as published.
    st.html('<script>document.documentElement.lang="pt-BR";'
            'document.documentElement.translate=false;'
            'document.documentElement.classList.add("notranslate");</script>',unsafe_allow_javascript=True)
    st.sidebar.title('SENTINELA')
    st.sidebar.write('Contagens históricas na BR-101/SC')
    try:
        package_token=token()
        manifest,frames,summary=load(package_token)
    except Exception:
        LOG.exception('falha_carregamento_pacote')
        st.title('Consulta temporariamente indisponível')
        st.error('Não foi possível validar os dados desta instalação. Tente recarregar a página. Se persistir, relate o problema à manutenção.')
        st.link_button('Relatar problema','https://github.com/limixin1/radarsul/issues/new')
        return
    stages['carregamento_s']=perf_counter()-started
    daily=frames['antt_diario'];meta=frames['antt_equipamentos'];annual=frames['antt_anual']
    if 'initialized' not in st.session_state:
        state,notes=parse_url({k:st.query_params.get_all(k) for k in st.query_params},meta)
        st.session_state.update(state);st.session_state['url_notes']=notes;st.session_state['initialized']=True
    for note in st.session_state.get('url_notes',[]):st.warning(note)
    page=st.sidebar.radio('Página',PAGES,key='page',on_change=sync)
    years=st.sidebar.multiselect('Anos solicitados',YEARS,key='years',on_change=sync)
    area=st.sidebar.selectbox('Área consultada',AREAS,key='area',on_change=sync)
    city=st.sidebar.selectbox('Buscar cidade',['Todas as cidades',*sorted(meta.municipio.unique())],key='city',on_change=sync)
    directions=st.sidebar.multiselect('Sentidos',DIRECTIONS,key='directions',on_change=sync,help='Crescente acompanha o aumento da quilometragem; decrescente acompanha a redução. Não indica orientação geográfica.')
    available=area_ids(meta,summary['coorte_ids'],area,directions,city)
    scope=(area,city,tuple(directions))
    if st.session_state.get('scope') not in [None,scope]:
        st.session_state['points']=available
        st.info('Área, cidade ou sentidos mudaram: os pontos foram atualizados para o recorte mostrado. Confira a seleção.')
    if st.session_state.points is None:st.session_state.points=available
    invalid=set(st.session_state.points)-set(available)
    if invalid:
        st.warning('Pontos incompatíveis com área/cidade/sentidos foram removidos: '+', '.join(sorted(invalid))+'. Confira os filtros ou restaure o padrão.')
        st.session_state.points=[x for x in st.session_state.points if x in available]
    st.session_state['scope']=scope
    labels={r.identificador:point_label(r) for r in meta.itertuples()}
    ids=st.sidebar.multiselect('Buscar e selecionar pontos',available,key='points',format_func=labels.get,on_change=sync,help='Digite cidade, km ou código. Remova pontos para comparar somente os locais desejados.')
    st.sidebar.button('Restaurar consulta padrão',on_click=reset)
    cities = city_options(meta, frames.get("ocorrencias"))
    old_focus = st.session_state.focus
    focus = normalize_focus(old_focus, ids, cities)
    if old_focus and not focus:
        st.caption("A localização em foco ficou fora da seleção atual.")
    st.session_state.focus = focus
    sync()
    st.sidebar.caption('Snapshot histórico. Coleta ANTT 26/10/2026 e PRF 23/10/2026. Tráfego até junho de 2026.')
    st.sidebar.caption(f'Aplicação {APP_VERSION} · dados {manifest["versao"]}')
    st.title(page if page != PAGES[0] else 'Consulte um ponto da BR-101/SC')
    area_label = 'Corredor BR-101/SC' if city == 'Todas as cidades' else f'{city}, BR-101/SC'
    location_phrase = 'No corredor da BR-101/SC' if city == 'Todas as cidades' else f'Em {city}, na BR-101/SC'
    point_count = f'{len(ids)} ' + ('ponto selecionado' if len(ids) == 1 else 'pontos selecionados')
    period_label = ', '.join(map(str, years)) or 'nenhum ano'
    st.caption(f'{area_label} · {period_label} · {point_count} · {", ".join(directions) or "sem sentido"}')
    if not years:st.info('Nenhum ano selecionado. Escolha ao menos um ano ou restaure a consulta padrão.');return
    if not directions:st.info('Nenhum sentido selecionado. Escolha crescente ou decrescente ou restaure o padrão.');return
    if not available:
        st.info('Não há pontos para esta combinação de área, cidade e sentidos. Escolha Todos os equipamentos, outra cidade ou ambos os sentidos.')
        st.button('Consultar esta cidade em todos os equipamentos',key='all_city',on_click=select_all_area)
    elif not ids:
        st.info('Nenhum equipamento selecionado. Selecione um ponto no painel ou restaure o padrão para comparar contagens de tráfego.')
    query_started=perf_counter()
    selected,eq,cov=consult(package_token,tuple(ids),tuple(years))
    stages['consulta_s']=perf_counter()-query_started
    if selected.empty and ids:
        st.info('Os pontos escolhidos não têm publicações de tráfego nos anos solicitados. Altere os anos ou os pontos. Ausência de publicação não é zero observado.')

    reference = road()
    radar_positions = positions(package_token, "ANTT", reference is not None, meta, reference)
    shapes = segment_shapes() if reference is not None else {}
    card = build_card(focus, meta, eq, cov, frames, manifest, years, radar_positions, shapes=shapes)
    if page == PAGES[0]:
        if not card:
            if selected.empty:
                st.write(f'{location_phrase}, a seleção de {period_label} está sem contagens disponíveis.')
            else:
                high, total = selected.altas.sum(), selected.passagens.sum()
                st.write(f'{location_phrase}, no recorte de {period_label}, cerca de '
                         f'**{br(weighted_index(high, total), 2)} por 10 mil contagens** ficaram nas faixas acima de 120 km/h.')
                st.caption(f'{br(high)} de {br(total)} contagens publicadas. Use o mapa ou a lista para consultar um local.')
        render_locator(meta, frames, ids, years, package_token, reference, radar_positions, card, page)
        if not card:
            st.subheader('O que merece atenção')
            if 2026 in years:
                st.write('**Cobertura parcial de 2026.** O inventário de tráfego vai até 30/06. '
                         'Confira os dias publicados do ponto e a disponibilidade de acidentes por fonte.')
            if not selected.empty and eq.elegivel.any():
                example = eq.loc[eq.elegivel].iloc[0]
                st.write(f'**{example.municipio}, km {br(example.km, 3)}.** Entre os pontos elegíveis da seleção, '
                         f'esse ponto tem {br(example.por_10_mil, 3)} por 10 mil contagens ANTT no período {period_label}. '
                         'Selecione o ponto para ver os dias com dados e as verificações de campo.')
            elif 2026 not in years:
                st.write('Os dias com dados deste recorte limitam a comparação. Consulte a cobertura antes de interpretar os resultados.')
    elif page in (PAGES[1], PAGES[3], PAGES[4]):
        render_locator(meta, frames, ids, years, package_token, reference, radar_positions, card, page)
    if selected.empty:
        if page == PAGES[4] and card:
            filters = {'page': page, 'years': years, 'area': area, 'directions': directions,
                       'city': city, 'points': ids, 'focus': focus}
            emeta = metadata(manifest, filters, ids, selected, [])
            emeta["ficha_preventiva"] = card.metadata()
            document = card.markdown() + f'\n\nSnapshot {manifest["versao"]} · código {code_version()}\n'
            with st.container(key="print_report"):
                st.markdown(document)
            st.subheader("Exportar esta consulta")
            st.download_button("Baixar ficha preventiva em Markdown", document,
                               "sentinela_ficha_preventiva.md", "text/markdown", on_click="ignore")
            st.download_button("Baixar ficha preventiva em ZIP", bundle(eq, cov, emeta, document),
                               "sentinela_ficha_preventiva.zip", "application/zip", on_click="ignore")
        return
    content_started=perf_counter()
    sources=sources_for(frames,ids,years,manifest,meta)
    filters={'page':page,'years':years,'area':area,'directions':directions,'city':city,'points':ids}
    if focus:
        filters['focus'] = focus
    emeta=metadata(manifest,filters,ids,selected,sources)
    emeta["mapa"] = {"eixo": ROAD_SOURCE, "coordenadas": "Posições publicadas com triagem espacial. Ocorrências ANTT permanecem por km."}
    selected_locations = radar_positions.loc[radar_positions.codigo.isin(ids)]
    emeta["localizacao_pontos"] = json.loads(selected_locations.to_json(orient="records"))
    if card:
        emeta["ficha_preventiva"] = card.metadata()
    export_name=filename(emeta,'png')[:-4]
    st.info('Índice: contagens nas faixas acima de 120 km/h ÷ contagens publicadas da mesma base de tráfego × 10.000. Não representa probabilidade de acidente, veículos únicos ou autuações confirmadas.')
    st.caption('120 km/h é um limiar dos intervalos publicados, não o limite regulamentado de cada ponto. Ausência de faixa não comprova ausência real de passagem.')
    eligible=eq.loc[eq.elegivel]
    if len(eligible)<len(eq):
        count=len(eq)-len(eligible)
        st.warning(f'{count} {"ponto com tráfego é exploratório" if count==1 else "pontos com tráfego são exploratórios"} neste período: cobertura anual insuficiente ou ano parcial. Os índices permanecem disponíveis na tabela, sem disputar o ranking.')
    no_data=set(ids)-set(eq.identificador)
    if no_data:st.warning('Pontos solicitados sem publicação no período: '+', '.join(sorted(no_data))+'. A tabela de cobertura preserva esses pontos.')
    columns=['identificador','municipio','km','sentido','passagens','altas','dias','por_10_mil','cobertura_minima','elegivel']
    if page==PAGES[0]:
        st.subheader('Resultado agregado da seleção')
        for col,label,value in zip(st.columns(3),['Índice agregado por 10 mil','Contagens publicadas','Acima de 120 km/h'],[br(weighted_index(selected.altas.sum(),selected.passagens.sum()),3),br(selected.passagens.sum()),br(selected.altas.sum())]):col.metric(label,value)
        st.caption('Agregado = razão entre somas, ponderada pelas contagens. A cobertura detalhada por ponto e ano está abaixo.')
        if len(eligible):
            winner=eligible.iloc[0]
            st.write(f'Maior índice da comparação ({len(eligible)} {"ponto elegível" if len(eligible)==1 else "pontos elegíveis"}): {labels[winner.identificador]} — {br(winner.por_10_mil,3)} por 10 mil; menor cobertura anual {br(winner.cobertura_minima*100,1)}%.')
            with st.expander('Ranking dos pontos comparáveis', expanded=False):
                chart(ranking(eligible,years),
                      f'Índice de faixas acima de 120 km/h por 10 mil contagens ANTT em {period_label}. '
                      f'O gráfico mostra {min(12,len(eligible))} de {len(eligible)} pontos elegíveis. {POLICY}',
                      eligible.head(12)[columns],'ranking',export_name+'_ranking')
        else:st.info('Nenhum ponto elegível para comparação anual neste período. Consulte os valores exploratórios e sua cobertura; não há destaque comparável.')
        table(eq[columns],'todos os pontos com publicação')
    elif page==PAGES[1]:
        table(eq[columns],'comparação da seleção')
        aid=eligible.identificador.tolist()
        if set(years)=={2024,2025} and len(aid)>1:
            p=persistence_data(annual,aid);rho=correlation(p[['ano_2024','ano_2025']])
            if rho is None:st.info('Correlação indefinida: faltam valores variáveis entre pontos. Não há coeficiente interpretável.')
            else:chart(persistence(annual,aid),f'Spearman {br(rho,3)}: semelhança na ordenação de {len(aid)} pontos selecionados entre 2024 e 2025. Não é previsão nem causalidade.',p.rename(columns={'ano_2024':'Índice 2024 por 10 mil','ano_2025':'Índice 2025 por 10 mil'}),'ordenação entre anos',export_name+'_anos')
        else:st.info('A comparação da ordenação entre pontos exige pelo menos dois pontos selecionados elegíveis e os anos 2024 e 2025. Com um ponto não há correlação entre pontos.')
        b=frames['antt_possiveis_diario'].loc[lambda x:x.ano.isin(years)&x.identificador.isin(ids)]
        st.subheader('Possíveis infratores: base B separada')
        if b.empty:st.info('Sem linhas publicadas da base B para esta seleção; não significa zero infrações.')
        else:table(b.groupby('identificador',as_index=False).agg(possiveis=('possiveis','sum'),dias=('data','nunique')),'base B')
        r=manifest['cobertura']['possiveis'];st.caption(f"Intervalo da base B: {r['inicio']} a {r['fim']}. {r['nota']}")
    elif page==PAGES[2]:
        monthly=frames['antt_mensal'];g=monthly_grid(monthly,ids,years)
        chart(evolution(monthly,ids,years),'As curvas incluem somente os pontos selecionados. Índices mensais exigem 80% dos dias publicados; lacunas não são zeros.',g[['identificador','mes','passagens','altas','dias','cobertura_dias','por_10_mil']],'histórico',export_name+'_historico')
        chart(coverage_map(monthly,ids,years),'Cada linha corresponde a um ponto selecionado. Células vazias indicam publicação insuficiente ou ausente.',g[['identificador','mes','dias','cobertura_dias','por_10_mil']],'matriz mensal',export_name+'_matriz')
    elif page==PAGES[3]:
        st.subheader('ANTT: segmentos disjuntos de 5 km')
        if set(years)=={2024,2025}:
            ctx=context_table(daily,meta,frames['antt_acidentes'],eligible.identificador.tolist(),years)
            if len(ctx)>1:
                rho=correlation(ctx[['por_10_mil','registros_acidentes']])
                chart(road_context(ctx),'Somente pontos selecionados elegíveis; mesmos dias em todos os pontos de cada segmento. '+('Correlação indefinida por falta de variabilidade.' if rho is None else f'Spearman {br(rho,3)}; associação descritiva, sem causalidade.'),ctx[['segmento','equipamentos','dias_comuns','cobertura_dias_comuns','por_10_mil','registros_acidentes','combinacoes_data_km']],'segmentos ANTT',export_name+'_contexto')
            else:st.info('Não há segmentos suficientes com pontos selecionados elegíveis para a análise de associação.')
        else:st.info('A análise por segmentos usa a referência fixa 2024–2025. Os contextos por fonte abaixo preservam todos os anos solicitados.')
        if 'VC101-30' in ids:st.caption('Criciúma pode ser consultada localmente, mas seu ponto não alcança 90% dos dias em ambos os anos 2024–2025 e fica fora do grupo histórico.')
        for source in sources:
            st.subheader(source.fonte);st.write(source.text())
            if source.intervalos:st.caption('Intervalos disponíveis: '+'; '.join(' a '.join(pair) for pair in source.intervalos)+'. Não certificam completude da fonte.')
        st.warning('Não somar acidentes ANTT e PRF nem atribuir automaticamente acidentes a um radar. Repetições ANTT sem ID são preservadas. Associação negativa não significa que velocidade proteja contra acidentes.')
    if page != PAGES[4]:
        st.subheader('Dias publicados por ponto e ano')
        table(cov,'cobertura anual e intervalo da fonte')
        st.caption('O intervalo usa o inventário do arquivo bruto, igual para todos os pontos; 2026 de tráfego vai até 30/06. Cobertura não comprova operação contínua. O grupo histórico reúne os pontos com ≥90% de dias em cada ano de 2024 e 2025.')
    stages['conteudo_s']=perf_counter()-content_started
    export_started=perf_counter()
    possible=frames['antt_possiveis_diario'].loc[lambda x:x.ano.isin(years)&x.identificador.isin(ids)]
    document=markdown_report(selected,eq,cov,emeta,possible,card)
    if page==PAGES[4]:
        with st.container(key='print_report'):st.markdown(document)
    st.subheader('Exportar esta consulta')
    st.caption('CSV brasileiro: UTF-8, ponto e vírgula e vírgula decimal. ZIP inclui CSV técnico, localização, cobertura, relatório e metadados completos. O PNG está no menu do gráfico. O relatório pode ser impresso pelo navegador.')
    st.download_button('Baixar comparação em CSV (pt-BR)',csv_bytes(eq[columns],emeta),filename(emeta,'csv'),'text/csv',on_click='ignore')
    st.download_button('Baixar relatório em Markdown',document.encode(),filename(emeta,'md'),'text/markdown',on_click='ignore')
    extra={"localizacao_pt-BR.csv": selected_locations.rename(columns={"codigo": "identificador"})}
    if page==PAGES[2]:extra['historico_mensal.csv']=g[['identificador','mes','passagens','altas','dias','cobertura_dias','por_10_mil']]
    st.download_button('Baixar consulta completa em ZIP',bundle(eq[columns],cov,emeta,document,extra),filename(emeta,'zip'),'application/zip',on_click='ignore')
    with st.expander('Método, versões e fontes verificáveis'):
        st.write('Taxa possíveis infratores/tráfego bloqueada por incompatibilidade das bases. Cadastro de junho de 2026 é referência; não reconstrói limites históricos. Não calcular velocidade média por pontos médios das faixas.')
        st.write(f"Aplicação {APP_VERSION} · código {emeta['codigo']} · dados {manifest['versao']}. Dados históricos, sem atualização automática.")
        for name,r in manifest['cobertura'].items():st.write(f"{name}: {r['inicio']} a {r['fim']}. {r['nota']}")
        for r in manifest['proveniencia']:st.markdown(f"[{r['arquivo']}]({r['url']}) — coleta {r['acesso_utc'][:10]}. Recurso externo; disponibilidade depende do publicador.")
        st.caption('Originais completos estão no kit de reprodução do repositório; não são baixados ao abrir esta página. Manifestos comprovam identidade com a coleta, sem certificar completude.')
        st.markdown('[Kit bruto de reprodução](https://github.com/limixin1/radarsul/blob/correcao/sentinela-auditoria/_contexto/SENTINELA_bases_ANTT.zip) · [PRF: condições de uso e atualização](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)')
        st.write('ANTT: os quatro catálogos declaram Creative Commons Atribuição (CC BY). PRF: a página de dados abertos declara uso, reutilização e redistribuição livres. Preserve atribuição e proveniência; consulta em 05/11/2026.')
        for source,record in manifest.get('reutilizacao',{}).items():
            if isinstance(record,dict) and 'metadata_modified' in record:st.caption(f"Atualização do catálogo {source}: {record['metadata_modified']}. Não significa atualização deste snapshot.")
        st.download_button('Baixar manifesto de dados',(ROOT/MANIFEST).read_bytes(),'sentinela_manifesto.json','application/json',on_click='ignore')
        st.link_button('Relatar um problema','https://github.com/limixin1/radarsul/issues/new')
    stages['exportacoes_e_fontes_s']=perf_counter()-export_started
    LOG.info('etapas_consulta %s',json.dumps(stages,sort_keys=True))
    LOG.info('consulta pagina=%s pontos=%d anos=%d snapshot=%s segundos=%.3f',page,len(ids),len(years),manifest['versao'],perf_counter()-started)

if __name__=='__main__':main()
