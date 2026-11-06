"""SENTINELA: consulta histórica de contagens publicadas, com cobertura explícita."""
import json
import logging
from dataclasses import replace
from time import perf_counter
import pandas as pd
import streamlit as st
from config import ROOT, KM_MIN, KM_MAX
from src.antt import context_table, weighted_index
from src.antt_charts import ranking, evolution, persistence, persistence_data, coverage_map, road_context, correlation, monthly_grid
from src.data_package import validate, token, MANIFEST
from src.query import PAGES, AREAS, YEARS, DIRECTIONS, POLICY, area_ids, query_tables, point_label, display_table, source_result, parse_url, url_state, br
from src.exports import APP_VERSION, code_version, metadata, markdown_report, csv_bytes, bundle, filename

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
LOG=logging.getLogger('sentinela')
LOG.setLevel(logging.INFO)

@st.cache_data(show_spinner=False)
def load(package_token):
    started=perf_counter()
    result=validate(allow_missing_prf=True)
    LOG.info('pacote_validado snapshot=%s segundos=%.3f',result[0]['versao'],perf_counter()-started)
    return result

CSS='''<style>
.block-container{padding-top:4.5rem;max-width:1480px}
[data-testid="stCaptionContainer"]{opacity:1!important;color:#142B3C!important}
[data-testid="stCaptionContainer"] p{color:#142B3C!important;opacity:1!important}
button:focus-visible,a:focus-visible,input:focus-visible,[role="combobox"]:focus-visible{outline:3px solid #075E68!important;outline-offset:3px}
p,li,h1,h2,h3{overflow-wrap:anywhere}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem}h1{font-size:1.8rem!important}[data-testid="stMetricValue"]{font-size:1.6rem} [data-testid="stHorizontalBlock"]{flex-wrap:wrap} [data-testid="stColumn"]{min-width:200px;flex:1 1 100%}}
@media print{[data-testid="stSidebar"],header,button{display:none!important}.block-container{padding:0!important}}
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
        st.query_params.from_dict(url_state(s.page,s.years,s.area,s.directions,s.city,s.points))

def table(t,label):
    # HTML table is an accessible alternative to the interactive canvas grid.
    st.dataframe(display_table(t),hide_index=True,width='stretch')
    with st.expander('Tabela para leitura e teclado — '+label):st.table(display_table(t))

def chart(fig,summary,t,label,export_name):
    st.write(summary)
    fig.add_annotation(text='Snapshot '+export_name.split('_')[1]+' · consulta '+export_name.split('_')[2],x=0,y=-.34,xref='paper',yref='paper',showarrow=False,xanchor='left',font=dict(size=12,color='#142B3C'))
    fig.update_layout(margin_b=120)
    st.plotly_chart(fig,width='stretch',config={'locale':'pt-BR','displaylogo':False,'toImageButtonOptions':{'format':'png','filename':export_name,'width':1100,'height':650,'scale':1}})
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
    st.set_page_config(page_title='SENTINELA — consulta BR-101/SC',layout='wide',menu_items={'Report a bug':'https://github.com/limixin1/radarsul/issues/new'})
    st.markdown(CSS,unsafe_allow_html=True)
    # st.html supports non-iframed, static JS in this pinned Streamlit version.
    # Standard DOM language attribute; no private frontend selectors or untrusted interpolation.
    st.html('<script>document.documentElement.lang="pt-BR";</script>',unsafe_allow_javascript=True)
    st.sidebar.title('SENTINELA')
    st.sidebar.write('Contagens históricas na BR-101/SC')
    try:manifest,frames,summary=load(token())
    except Exception:
        LOG.exception('falha_carregamento_pacote')
        st.title('Consulta temporariamente indisponível')
        st.error('Não foi possível validar os dados desta instalação. Tente recarregar a página. Se persistir, relate o problema à manutenção.')
        st.link_button('Relatar problema','https://github.com/limixin1/radarsul/issues/new')
        return
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
    sync()
    st.sidebar.caption('Snapshot histórico. Coleta ANTT 26/10/2026; PRF 23/10/2026. Tráfego até junho de 2026. Sem monitoramento em tempo real.')
    st.sidebar.caption(f'Aplicação {APP_VERSION} · dados {manifest["versao"]}')
    st.title(page if page!=PAGES[0] else 'Consulte um ponto da BR-101/SC')
    st.write('Escolha uma cidade e os pontos no painel de filtros. Consulte contagens publicadas de velocidade, confira os dias disponíveis e exporte a consulta com suas fontes.')
    st.caption(f'{len(ids)} pontos solicitados · {area} · {city} · anos: {", ".join(map(str,years)) or "nenhum"} · sentidos: {", ".join(directions) or "nenhum"}. {POLICY}')
    if not years:st.info('Nenhum ano selecionado. Escolha ao menos um ano ou restaure a consulta padrão.');return
    if not directions:st.info('Nenhum sentido selecionado. Escolha crescente ou decrescente ou restaure o padrão.');return
    if not available:
        st.info('Não há pontos para esta combinação de área, cidade e sentidos. Escolha Todos os equipamentos, outra cidade ou ambos os sentidos.')
        st.button('Consultar esta cidade em todos os equipamentos',key='all_city',on_click=select_all_area)
        return
    if not ids:st.info('Nenhum equipamento selecionado. Selecione ao menos um ponto no painel ou restaure o padrão. Comparações e downloads ficam indisponíveis.');return
    selected,eq,cov=query_tables(daily,meta,ids,years,manifest['cobertura']['trafego'])
    if selected.empty:st.info('Os pontos escolhidos não têm publicações de tráfego nos anos solicitados. Altere os anos ou os pontos; ausência de publicação não é zero observado.');return
    sources=sources_for(frames,ids,years,manifest,meta)
    filters={'page':page,'years':years,'area':area,'directions':directions,'city':city,'points':ids}
    emeta=metadata(manifest,filters,ids,selected,sources)
    export_name=filename(emeta,'png')[:-4]
    st.info('Índice: contagens nas faixas acima de 120 km/h ÷ contagens publicadas da mesma base de tráfego × 10.000. Não representa probabilidade de acidente, veículos únicos ou autuações confirmadas.')
    st.caption('120 km/h é um limiar dos intervalos publicados, não o limite regulamentado de cada ponto. Ausência de faixa não comprova ausência real de passagem.')
    eligible=eq.loc[eq.elegivel]
    if len(eligible)<len(eq):st.warning(f'{len(eq)-len(eligible)} pontos com tráfego são exploratórios neste período: cobertura anual insuficiente ou ano parcial. Seus índices permanecem disponíveis na tabela, sem disputar o ranking.')
    no_data=set(ids)-set(eq.identificador)
    if no_data:st.warning('Pontos solicitados sem publicação no período: '+', '.join(sorted(no_data))+'. A tabela de cobertura preserva esses pontos.')
    columns=['identificador','municipio','km','sentido','passagens','altas','dias','por_10_mil','cobertura_minima','elegivel']
    if page==PAGES[0]:
        st.subheader('Resultado agregado da seleção')
        for col,label,value in zip(st.columns(3),['Índice agregado por 10 mil','Contagens publicadas','Acima de 120 km/h'],[br(weighted_index(selected.altas.sum(),selected.passagens.sum()),3),br(selected.passagens.sum()),br(selected.altas.sum())]):col.metric(label,value)
        st.caption('Agregado = razão entre somas, ponderada pelas contagens. A cobertura detalhada por ponto e ano está abaixo.')
        if len(eligible):
            winner=eligible.iloc[0]
            st.write(f'Maior índice entre os {len(eligible)} pontos elegíveis: {labels[winner.identificador]} — {br(winner.por_10_mil,3)} por 10 mil; menor cobertura anual {br(winner.cobertura_minima*100,1)}%.')
            chart(ranking(eligible,years),f'O ranking mostra até 12 de {len(eligible)} pontos elegíveis. A lista completa inclui também os pontos exploratórios.',eligible.head(12)[columns],'ranking',export_name+'_ranking')
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
    st.subheader('Dias publicados por ponto e ano')
    table(cov,'cobertura anual e intervalo da fonte')
    st.caption('O intervalo usa o inventário do arquivo bruto, igual para todos os pontos; 2026 de tráfego vai até 30/06. Cobertura não comprova operação contínua. O grupo histórico reúne os pontos com ≥90% de dias em cada ano de 2024 e 2025.')
    possible=frames['antt_possiveis_diario'].loc[lambda x:x.ano.isin(years)&x.identificador.isin(ids)]
    document=markdown_report(selected,eq,cov,emeta,possible)
    if page==PAGES[4]:st.markdown(document)
    st.subheader('Exportar esta consulta')
    st.caption('CSV brasileiro: UTF-8, ponto e vírgula e vírgula decimal. ZIP inclui CSV técnico, cobertura, relatório e metadados completos. O PNG está no menu do gráfico. O relatório pode ser impresso pelo navegador.')
    st.download_button('Baixar comparação em CSV (pt-BR)',csv_bytes(eq[columns],emeta),filename(emeta,'csv'),'text/csv',on_click='ignore')
    st.download_button('Baixar relatório em Markdown',document.encode(),filename(emeta,'md'),'text/markdown',on_click='ignore')
    extra={}
    if page==PAGES[2]:extra['historico_mensal.csv']=g[['identificador','mes','passagens','altas','dias','cobertura_dias','por_10_mil']]
    st.download_button('Baixar consulta completa em ZIP',bundle(eq[columns],cov,emeta,document,extra),filename(emeta,'zip'),'application/zip',on_click='ignore')
    with st.expander('Método, versões e fontes verificáveis'):
        st.write('Taxa possíveis infratores/tráfego bloqueada por incompatibilidade das bases. Cadastro de junho de 2026 é referência; não reconstrói limites históricos. Não calcular velocidade média por pontos médios das faixas.')
        st.write(f'Aplicação {APP_VERSION} · código {code_version()} · dados {manifest["versao"]}. Dados históricos, sem atualização automática.')
        for name,r in manifest['cobertura'].items():st.write(f"{name}: {r['inicio']} a {r['fim']}. {r['nota']}")
        for r in manifest['proveniencia']:st.markdown(f"[{r['arquivo']}]({r['url']}) — coleta {r['acesso_utc'][:10]}. Recurso externo; disponibilidade depende do publicador.")
        st.caption('Originais completos estão no kit de reprodução do repositório; não são baixados ao abrir esta página. Manifestos comprovam identidade com a coleta, sem certificar completude.')
        st.markdown('[Kit bruto de reprodução](https://github.com/limixin1/radarsul/blob/correcao/sentinela-auditoria/_contexto/SENTINELA_bases_ANTT.zip) · [PRF: condições de uso e atualização](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf)')
        st.write('ANTT: os quatro catálogos declaram Creative Commons Atribuição (CC BY). PRF: a página de dados abertos declara uso, reutilização e redistribuição livres. Preserve atribuição e proveniência; consulta em 05/11/2026.')
        for source,record in manifest.get('reutilizacao',{}).items():
            if isinstance(record,dict) and 'metadata_modified' in record:st.caption(f"Atualização do catálogo {source}: {record['metadata_modified']}. Não significa atualização deste snapshot.")
        st.download_button('Baixar manifesto de dados',(ROOT/MANIFEST).read_bytes(),'sentinela_manifesto.json','application/json',on_click='ignore')
        st.link_button('Relatar um problema','https://github.com/limixin1/radarsul/issues/new')
    LOG.info('consulta pagina=%s pontos=%d anos=%d snapshot=%s segundos=%.3f',page,len(ids),len(years),manifest['versao'],perf_counter()-started)

if __name__=='__main__':main()
