"""SENTINELA 2.0: análise ANTT com contexto PRF independente."""
import json
import pandas as pd
import streamlit as st
from config import PROCESSED,REPORTS
from src.antt import equipment_table,context_table
from src.antt_charts import ranking,evolution,persistence,coverage_map,road_context
from src.antt_report import report

@st.cache_data
def load():
    frames={n:pd.read_parquet(PROCESSED/f'antt_{n}.parquet') for n in ['diario','mensal','anual','equipamentos','possiveis_diario','acidentes']}
    return frames,json.loads((REPORTS/'resumo_antt.json').read_text())

def main():
    st.set_page_config(page_title='SENTINELA — ANTT',layout='wide')
    st.markdown('<style>.stApp{background:#FAFBFC;color:#142B3C}h1,h2,h3{color:#142B3C}[data-testid="stSidebar"]{background:#EEF3F5}.block-container{padding-top:2rem;max-width:1480px}</style>',unsafe_allow_html=True)
    st.sidebar.title('SENTINELA 2.0');st.sidebar.caption('Inteligência Preventiva para Segurança Viária')
    page=st.sidebar.radio('Navegação',['Visão geral','Comparador de equipamentos','Evolução e persistência','Contexto rodoviário','Relatório preventivo'])
    try:frames,summary=load()
    except (FileNotFoundError,ImportError,ValueError) as e:
        st.error('Execute python analisar.py para gerar os dados tratados ANTT.');st.caption(str(e));st.stop()
    daily,monthly,annual,meta,possible,accidents=[frames[n] for n in ['diario','mensal','anual','equipamentos','possiveis_diario','acidentes']]
    years=st.sidebar.multiselect('Anos dos registros',[2022,2023,2024,2025,2026],default=[2024,2025])
    area=st.sidebar.selectbox('Recorte',['Coorte comparável 2024–2025','Todos os equipamentos','Criciúma: VC101-30','Entorno de Criciúma: km 370 a 410'])
    ids=summary['coorte_ids'] if area.startswith('Coorte') else meta.identificador.tolist()
    if area.startswith('Criciúma'):ids=['VC101-30']
    if area.startswith('Entorno'):ids=meta.loc[meta.km.ge(370)&meta.km.lt(410),'identificador'].tolist()
    directions=st.sidebar.multiselect('Sentido',sorted(meta.sentido.unique()),default=sorted(meta.sentido.unique()))
    ids=meta.loc[meta.identificador.isin(ids)&meta.sentido.isin(directions),'identificador'].tolist()
    selected=daily.loc[daily.ano.isin(years)&daily.identificador.isin(ids)]
    st.sidebar.divider();st.sidebar.caption('ANTT · Coleta 26/10/2026\n\nPeríodo principal: 2024–2025\n\n2026 parcial até junho\n\nTaxa possíveis infratores/tráfego bloqueada por incompatibilidade.')
    if selected.empty:
        st.title('SENTINELA');st.info('Nenhum registro para os filtros. Selecione anos e sentidos disponíveis.');return
    eq=equipment_table(selected,meta,years)
    st.caption('BR-101/SC · CRICIÚMA E SUL DE SANTA CATARINA · DADOS OFICIAIS ANTT')
    st.info('Indicador: contagens nas faixas acima de 120 km/h por 10 mil contagens publicadas na própria base de tráfego. Não é taxa de autuações nem probabilidade de acidente.')
    if set(ids)-set(summary['coorte_ids']):st.warning('O recorte inclui equipamentos fora da coorte de cobertura de 90% nos dois anos. Confira os dias publicados antes de comparar.')
    if 2026 in years:st.caption('2026 parcial: tráfego até 30/06 e possíveis infratores até 02/06. Não comparar contagens anuais como anos completos.')
    if page=='Visão geral':
        st.title(f'O maior índice no recorte é {eq.por_10_mil.max():.2f} por 10 mil'.replace('.',','))
        cols=st.columns(4)
        for col,label,value in zip(cols,['Equipamentos','Contagens publicadas','Acima de 120 km/h','Dias distintos com registros'],[len(eq),int(selected.passagens.sum()),int(selected.altas.sum()),selected.data.nunique()]):col.metric(label,f'{value:,}'.replace(',','.'))
        st.plotly_chart(ranking(eq),width='stretch')
        st.caption('Coorte fixa: 20 de 42 equipamentos, com registros em pelo menos 90% dos dias de cada ano de 2024–2025. Publicação não comprova operação contínua.')
    elif page=='Comparador de equipamentos':
        st.title('Comparador de equipamentos')
        chosen=st.multiselect('Equipamentos',eq.identificador.tolist(),default=eq.identificador.head(3).tolist())
        show=eq.loc[eq.identificador.isin(chosen),['identificador','municipio','km','sentido','passagens','altas','dias','por_10_mil']]
        st.dataframe(show,hide_index=True,width='stretch')
        st.download_button('Baixar comparação em CSV',show.to_csv(index=False).encode('utf-8-sig'),'sentinela_comparacao.csv','text/csv')
        aid=[i for i in ids if i in summary['coorte_ids']]
        if set(years)=={2024,2025} and len(aid)>1:st.plotly_chart(persistence(annual,aid),width='stretch')
        else:st.caption('Persistência exige ambos os anos de 2024–2025 e equipamentos da coorte.')
        b=possible.loc[possible.ano.isin(years)&possible.identificador.isin(chosen)]
        st.subheader('Possíveis infratores: contagens separadas')
        st.dataframe(b.groupby('identificador',as_index=False).agg(contagens_publicadas=('possiveis','sum'),dias_com_publicacao=('data','nunique')),hide_index=True)
        st.caption('Ausência de linhas não comprova zero infrações. Nenhum percentual B/A foi calculado.')
    elif page=='Evolução e persistência':
        st.title('Evolução dos registros de velocidade')
        chosen=st.multiselect('Equipamentos no histórico',eq.identificador.tolist(),default=eq.identificador.head(3).tolist())
        if chosen:
            st.plotly_chart(evolution(monthly,chosen,years),width='stretch')
            st.plotly_chart(coverage_map(monthly,ids,years),width='stretch')
        else:st.info('Selecione ao menos um equipamento para o histórico.')
        st.caption('Lacunas indicam menos de 80% dos dias publicados no mês. Ausência não recebe índice zero.')
    elif page=='Contexto rodoviário':
        st.title('Contexto de acidentes nos mesmos segmentos')
        if set(years)=={2024,2025}:
            ctx=context_table(daily,meta,accidents,[i for i in ids if i in summary['coorte_ids']],years)
            if len(ctx)>1:
                st.plotly_chart(road_context(ctx),width='stretch');st.dataframe(ctx[['segmento','equipamentos','dias_comuns','cobertura_dias_comuns','por_10_mil','registros_acidentes','combinacoes_data_km']],hide_index=True)
                st.caption('Cada segmento usa somente as datas em que todos os seus equipamentos selecionados publicaram. Os acidentes usam essas mesmas datas, sem multiplicação por radar.')
            else:st.info('Não há segmentos suficientes da coorte para investigar associação neste recorte.')
        else:st.caption('A análise espacial principal fixa 2024–2025. Selecione ambos os anos para consultar o gráfico.')
        km=meta.loc[meta.identificador.isin(ids),'km']
        local=accidents.loc[accidents.ano.isin(years)&accidents.km.between(max(244.68,float(km.min())-2.5),min(465.1,float(km.max())+2.5))]
        st.caption(f'{len(local)} registros ANTT no envelope entre os pontos selecionados, com margem de 2,5 km. Isso não atribui cada acidente a um radar.')
        st.warning('Repetições de dia/km são preservadas por falta de ID de ocorrência. Associação negativa não significa que velocidade proteja contra acidentes.')
        if (PROCESSED/'ocorrencias.parquet').exists():
            pdf=pd.read_parquet(PROCESSED/'ocorrencias.parquet');pdf=pdf.loc[pdf.ano.isin(years)]
            st.subheader('PRF: contexto independente')
            st.write(f'{len(pdf)} ocorrências PRF no trecho integral para os anos selecionados. Em Criciúma: {int(pdf.municipio.eq("CRICIUMA").sum())}. Não somar às contagens ANTT.')
    else:
        st.title('Relatório preventivo')
        choice=st.selectbox('Escopo',['Todos os equipamentos do filtro',*eq.identificador.tolist()])
        frame=selected if choice.startswith('Todos') else selected.loc[selected.identificador.eq(choice)]
        document=report(frame,meta,annual,possible,choice)
        st.download_button('Baixar relatório com fontes e limites',document.encode('utf-8'),'SENTINELA_relatorio_preventivo.md','text/markdown')
        st.markdown(document)
    with st.expander('Método, cadastro e fontes'):
        st.write('120 km/h é um limiar analítico dos intervalos disponíveis. O cadastro de junho de 2026 é referência, sem reconstrução de limites históricos. Não calcular velocidade média por pontos médios das faixas.')
        st.dataframe(meta.loc[meta.identificador.isin(ids),['identificador','km','municipio','sentido','limite_leve_ref_2026','limite_pesado_ref_2026']],hide_index=True)
        st.markdown('[Portal de dados ANTT](https://dados.antt.gov.br/) · Dados originais e hashes acompanham o pacote.')

if __name__=='__main__':main()
