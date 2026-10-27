"""Cinco figuras ANTT com unidades e denominadores explícitos."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
TEAL='#087F8C';INK='#142B3C'

def style(fig,title,note):
    fig.update_layout(template='plotly_white',font=dict(family='Arial',size=14,color=INK),title=dict(text=title,font=dict(size=23)),height=520,margin=dict(l=65,r=35,t=85,b=110),legend_title_text='',colorway=[TEAL,'#B45F24','#775886','#58708A'])
    fig.add_annotation(text='Fonte: ANTT, coleta 26/10/2026. Índice da própria base de tráfego.<br>'+note,x=0,y=-.25,xref='paper',yref='paper',showarrow=False,xanchor='left',align='left',font=dict(size=10,color='#506270'))
    return fig

def ranking(eq):
    t=eq.head(12).sort_values('por_10_mil')
    fig=px.bar(t,x='por_10_mil',y='identificador',orientation='h',text=t.por_10_mil.map(lambda v:f'{v:.2f}'),hover_data=['municipio','km','sentido','altas','passagens','dias'],color_discrete_sequence=[TEAL],labels={'por_10_mil':'Registros acima de 120 km/h por 10 mil contagens','identificador':'Equipamento'})
    fig.update_traces(textposition='outside',cliponaxis=False)
    return style(fig,f'O maior índice no recorte é {eq.por_10_mil.max():.2f} por 10 mil'.replace('.',','),'Limiar analítico. Não representa autuação ou probabilidade de acidente.')

def evolution(monthly,ids,years):
    grid=pd.MultiIndex.from_product([ids,pd.period_range(f'{min(years)}-01',f'{max(years)}-12',freq='M').astype(str)],names=['identificador','mes']).to_frame(index=False)
    grid=grid.loc[grid.mes.str[:4].astype(int).isin(years)]
    t=grid.merge(monthly,on=['identificador','mes'],how='left',validate='one_to_one')
    t['indice_exibido']=t.por_10_mil.where(t.cobertura_dias.ge(.8));t['data_mes']=pd.to_datetime(t.mes+'-01')
    fig=px.line(t,x='data_mes',y='indice_exibido',color='identificador',markers=True,hover_data=['dias','cobertura_dias','altas','passagens'],labels={'data_mes':'Mês','indice_exibido':'Registros acima de 120 por 10 mil','identificador':'Equipamento'})
    fig.update_traces(connectgaps=False)
    return style(fig,'O histórico mostra mudanças no índice publicado','Lacunas: menos de 80% dos dias com publicação. Ausência não vira zero.')

def persistence(annual,ids):
    t=annual.loc[annual.identificador.isin(ids)&annual.ano.isin([2024,2025])].pivot(index='identificador',columns='ano',values='por_10_mil').reindex(columns=[2024,2025]).dropna().reset_index().rename(columns={2024:'ano_2024',2025:'ano_2025'})
    fig=px.scatter(t,x='ano_2024',y='ano_2025',hover_name='identificador',color_discrete_sequence=[TEAL],labels={'ano_2024':'Índice em 2024 (por 10 mil)','ano_2025':'Índice em 2025 (por 10 mil)'})
    fig.update_traces(marker=dict(size=11));rho=t[['ano_2024','ano_2025']].corr(method='spearman').iloc[0,1] if len(t)>1 else np.nan
    return style(fig,f'A ordenação entre os anos apresenta Spearman {rho:.2f}'.replace('.',','),'Coorte fixa com pelo menos 90% dos dias publicados em cada ano.')

def coverage_map(monthly,ids,years):
    t=monthly.loc[monthly.identificador.isin(ids)&monthly.mes.str[:4].astype(int).isin(years)].copy()
    months=[str(m) for m in pd.period_range(f'{min(years)}-01',f'{max(years)}-12',freq='M') if m.year in years]
    t['indice_exibido']=t.por_10_mil.where(t.cobertura_dias.ge(.8))
    grid=t.pivot(index='identificador',columns='mes',values='indice_exibido').reindex(index=ids,columns=months)
    fig=go.Figure(go.Heatmap(z=grid.to_numpy(dtype=float,na_value=np.nan),x=grid.columns,y=grid.index,colorscale='Teal',colorbar=dict(title='Por 10 mil'),hovertemplate='%{y}, %{x}: %{z:.2f} por 10 mil<extra></extra>'))
    fig.update_layout(xaxis_title='Mês',yaxis_title='Equipamento')
    fig=style(fig,'O padrão mensal pode ser acompanhado por equipamento','Células vazias: cobertura inferior a 80% ou ausência de publicação.')
    fig.update_layout(height=max(520,len(ids)*22+180))
    return fig

def road_context(t):
    fig=px.scatter(t,x='por_10_mil',y='registros_acidentes',hover_name='segmento',size='equipamentos',hover_data=['combinacoes_data_km','passagens','altas'],color_discrete_sequence=[TEAL],labels={'por_10_mil':'Índice acima de 120 (por 10 mil)','registros_acidentes':'Registros ANTT de acidentes no segmento (n)'})
    rho=t[['por_10_mil','registros_acidentes']].corr(method='spearman').iloc[0,1] if len(t)>1 else np.nan
    return style(fig,f'No recorte espacial, Spearman é {rho:.2f}'.replace('.',','),'5 km, 2024–2025. Mesmos dias com publicação em todos os pontos do segmento. Sem causalidade.')
