"""Figuras descritivas; a interface oferece resumos e tabelas equivalentes."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.query import br
TEAL='#087F8C';INK='#142B3C'

def style(fig,title,note,years=None):
    period=', '.join(map(str,years or [2024,2025]))
    fig.update_layout(template='plotly_white',font=dict(family='Arial',size=14,color=INK),
      title=dict(text=title,font=dict(size=17),y=.92,yanchor='top'),height=fig.layout.height or 520,margin=dict(l=40,r=25,t=105,b=190),legend_title_text='',
      modebar=dict(color=INK,activecolor='#075E68',bgcolor='#FAFBFC'),separators=',.',colorway=[TEAL,'#9C4C16','#775886','#405D78'],paper_bgcolor='#FAFBFC',plot_bgcolor='#FAFBFC')
    fig.update_xaxes(tickfont_color=INK,title_font_color=INK)
    fig.update_yaxes(tickfont_color=INK,title_font_color=INK)
    # Fonte e período acompanham também o PNG do modo de exportação.
    fig.add_annotation(text=f'ANTT · coleta 26/10/2026<br>Anos: {period}<br>{note}',x=0,y=0,yshift=-65,yanchor='top',xref='paper',yref='paper',showarrow=False,xanchor='left',align='left',font=dict(size=12,color=INK))
    return fig

def ranking(eq,years=None):
    t=eq.head(12).sort_values('por_10_mil').copy()
    t['local']=t.apply(lambda r:f'{r.municipio}<br>{r.identificador}',axis=1)
    fig=go.Figure(go.Bar(x=t.por_10_mil,y=t.local,orientation='h',text=t.por_10_mil.map(lambda v:br(v,3)),
      marker_color=TEAL,hovertemplate='Local e ponto=%{y}<br>Índice por 10 mil contagens=%{x}<extra></extra>'))
    fig.update_layout(xaxis_title='Índice por 10 mil contagens',yaxis_title='Local e ponto',showlegend=False)
    fig.update_traces(textposition='outside',cliponaxis=False)
    fig.update_layout(yaxis=dict(automargin=True),xaxis=dict(automargin=True),height=max(520,len(t)*36+255))
    return style(fig,('1 ponto elegível' if len(eq)==1 else f'{min(12,len(eq))} de {len(eq)} pontos elegíveis'),'Base A · acima de 120 km/h<br>por 10 mil contagens',years)

def monthly_grid(monthly,ids,years):
    if not years or not ids:return pd.DataFrame()
    months=[str(m) for m in pd.period_range(f'{min(years)}-01',f'{max(years)}-12',freq='M') if m.year in years]
    grid=pd.MultiIndex.from_product([ids,months],names=['identificador','mes']).to_frame(index=False)
    t=grid.merge(monthly,on=['identificador','mes'],how='left',validate='one_to_one')
    t['indice_exibido']=t.por_10_mil.where(t.cobertura_dias.ge(.8));t['data_mes']=pd.to_datetime(t.mes+'-01')
    return t

def evolution(monthly,ids,years):
    t=monthly_grid(monthly,ids,years)
    fig=px.line(t,x='data_mes',y='indice_exibido',color='identificador',markers=True,
      labels={'data_mes':'Mês','indice_exibido':'Índice por 10 mil','identificador':'Ponto'})
    fig.update_traces(connectgaps=False)
    fig.update_xaxes(tickangle=0,nticks=3,tickformat='%b<br>%Y',title_standoff=8)
    return style(fig,'Histórico dos pontos selecionados','Lacuna: menos de 80%<br>dos dias publicados no mês',years)

def correlation(t):
    t=t.replace([np.inf,-np.inf],np.nan).dropna()
    if len(t)<2 or (t.nunique()<2).any():return None
    return float(t.corr(method='spearman').iloc[0,1])

def persistence_data(annual,ids):
    return annual.loc[annual.identificador.isin(ids)&annual.ano.isin([2024,2025])].pivot(index='identificador',columns='ano',values='por_10_mil').reindex(columns=[2024,2025]).dropna().reset_index().rename(columns={2024:'ano_2024',2025:'ano_2025'})

def persistence(annual,ids):
    t=persistence_data(annual,ids)
    fig=px.scatter(t,x='ano_2024',y='ano_2025',hover_name='identificador',color_discrete_sequence=[TEAL],labels={'ano_2024':'Índice 2024 (por 10 mil)','ano_2025':'Índice 2025 (por 10 mil)'})
    fig.update_traces(marker=dict(size=11))
    return style(fig,'Ordenação dos pontos entre anos','≥90% dos dias em cada ano<br>Sem previsão ou causalidade',[2024,2025])

def coverage_map(monthly,ids,years):
    t=monthly_grid(monthly,ids,years)
    grid=t.pivot(index='identificador',columns='mes',values='indice_exibido').reindex(index=ids)
    fig=go.Figure(go.Heatmap(z=grid.to_numpy(dtype=float,na_value=np.nan),x=grid.columns,y=grid.index,colorscale='Teal',colorbar=dict(title='Por 10 mil'),hovertemplate='%{y}, %{x}: %{z:.3f} por 10 mil<extra></extra>'))
    fig.update_layout(xaxis_title='Mês',yaxis_title='Ponto')
    fig.update_xaxes(tickangle=0,nticks=3,title_standoff=8)
    fig=style(fig,'Matriz mensal da seleção','Vazio: menos de 80%<br>ou sem publicação',years)
    fig.update_layout(height=max(520,len(ids)*23+180))
    return fig

def road_context(t):
    fig=px.scatter(t,x='por_10_mil',y='registros_acidentes',hover_name='segmento',size='equipamentos',color_discrete_sequence=[TEAL],labels={'por_10_mil':'Índice por 10 mil','registros_acidentes':'Registros ANTT de acidentes (n)'})
    return style(fig,'Segmentos disjuntos de 5 km','Dias comuns a todos os pontos<br>Sem causalidade',[2024,2025])
