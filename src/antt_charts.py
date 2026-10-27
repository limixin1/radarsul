"""Figuras descritivas; tabelas equivalentes são apresentadas pela interface."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEAL = '#087F8C'
INK = '#142B3C'
LABELS = {'por_10_mil': 'Contagens acima de 120 km/h por 10 mil',
          'identificador': 'Radar', 'municipio': 'Município', 'km': 'Quilômetro',
          'sentido': 'Sentido da quilometragem', 'altas': 'Contagens acima de 120 km/h',
          'passagens': 'Contagens publicadas', 'dias': 'Dias publicados',
          'cobertura_dias': 'Cobertura dos dias do calendário'}


def style(fig, title, note):
    fig.update_layout(template='plotly_white', font=dict(family='Arial', size=14, color=INK),
                      title=dict(text=title, font=dict(size=18)), height=480,
                      margin=dict(l=55, r=25, t=85, b=70), legend_title_text='',
                      separators=',.', colorway=[TEAL, '#B45F24', '#775886', '#58708A'])
    # Explicações longas ficam fora do canvas para refluxo e leitura acessível.
    fig.update_layout(meta={'nota': note})
    return fig


def correlation_detail(frame, x, y):
    """Coeficiente somente para pares finitos e não constantes; sem inferência causal."""
    pairs = frame[[x, y]].replace([np.inf, -np.inf], np.nan).dropna()
    n = len(pairs)
    rho = pairs.corr(method='spearman').iloc[0, 1] if n > 1 and pairs[x].nunique() > 1 and pairs[y].nunique() > 1 else np.nan
    return n, float(rho) if pd.notna(rho) else None


def ranking(eq):
    t = eq.sort_values('por_10_mil', ascending=False).head(12).sort_values('por_10_mil').copy()
    t['local'] = t.apply(lambda r: f"{r['identificador']} · {r['municipio']} · km {r['km']:.3f}".replace('.', ','), axis=1)
    fig = px.bar(t, x='por_10_mil', y='local', orientation='h',
                 text=t.por_10_mil.map(lambda v: f'{v:.2f}'.replace('.', ',')),
                 hover_data=['identificador', 'municipio', 'km', 'sentido', 'altas', 'passagens', 'dias'],
                 color_discrete_sequence=[TEAL], labels={**LABELS, 'local': 'Local'})
    fig.update_traces(textposition='outside', cliponaxis=False)
    fig.update_xaxes(rangemode='tozero')
    return style(fig, f'{len(t)} maiores índices entre {len(eq)} radares do filtro',
                 'Limiar analítico; não representa autuação ou probabilidade de acidente.')


def monthly_display(monthly, ids, years):
    if not ids or not years:
        return pd.DataFrame()
    # Meses de anos não selecionados permanecem como lacunas; não ligamos anos separados.
    months = pd.period_range(f'{min(years)}-01', f'{max(years)}-12', freq='M').astype(str)
    grid = pd.MultiIndex.from_product([ids, months], names=['identificador', 'mes']).to_frame(index=False)
    t = grid.merge(monthly, on=['identificador', 'mes'], how='left', validate='one_to_one')
    chosen_year = t.mes.str[:4].astype(int).isin(years)
    t['indice_exibido'] = t.por_10_mil.where(t.cobertura_dias.ge(.8) & chosen_year)
    t['data_mes'] = pd.to_datetime(t.mes + '-01')
    t['estado'] = np.select([~chosen_year, t.passagens.isna(), t.cobertura_dias.lt(.8), t.indice_exibido.isna()],
                            ['Ano fora da seleção', 'Sem registro publicado', 'Menos de 80% dos dias publicados', 'Denominador ou índice indisponível'],
                            default='Índice disponível')
    return t


def evolution(monthly, ids, years):
    t = monthly_display(monthly, ids, years)
    fig = px.line(t, x='data_mes', y='indice_exibido', color='identificador', markers=True,
                  hover_data=['dias', 'cobertura_dias', 'altas', 'passagens', 'estado'],
                  labels={**LABELS, 'data_mes': 'Mês', 'indice_exibido': LABELS['por_10_mil'], 'estado': 'Disponibilidade'})
    fig.update_traces(connectgaps=False)
    return style(fig, 'Evolução mensal dos radares selecionados', 'Lacunas: publicação insuficiente ou indisponível; ausência não vira zero.')


def persistence_data(annual, ids):
    return (annual.loc[annual.identificador.isin(ids) & annual.ano.isin([2024, 2025])]
            .pivot(index='identificador', columns='ano', values='por_10_mil')
            .reindex(columns=[2024, 2025]).dropna().reset_index()
            .rename(columns={2024: 'ano_2024', 2025: 'ano_2025'}))


def persistence(annual, ids):
    t = persistence_data(annual, ids)
    fig = px.scatter(t, x='ano_2024', y='ano_2025', hover_name='identificador',
                     color_discrete_sequence=[TEAL], labels={'ano_2024': 'Índice em 2024 (por 10 mil)',
                     'ano_2025': 'Índice em 2025 (por 10 mil)', 'identificador': 'Radar'})
    fig.update_traces(marker=dict(size=11))
    return style(fig, 'Comparação dos índices publicados em 2024 e 2025', 'Somente os radares selecionados com dados nos dois anos.')


def coverage_map(monthly, ids, years):
    t = monthly_display(monthly, ids, years)
    months = [str(m) for m in pd.period_range(f'{min(years)}-01', f'{max(years)}-12', freq='M') if m.year in years]
    grid = t.pivot(index='identificador', columns='mes', values='indice_exibido').reindex(index=ids, columns=months)
    fig = go.Figure(go.Heatmap(z=grid.to_numpy(dtype=float, na_value=np.nan), x=grid.columns, y=grid.index,
                    colorscale='Teal', colorbar=dict(title='Por 10 mil'),
                    hovertemplate='%{y}, %{x}: %{z:.2f} por 10 mil<extra></extra>'))
    fig.update_layout(xaxis_title='Mês', yaxis_title='Radar')
    fig = style(fig, 'Índices mensais dos mesmos radares selecionados', 'Células vazias: menos de 80% dos dias ou ausência de publicação.')
    fig.update_layout(height=max(480, len(ids) * 24 + 160))
    return fig


def road_context(t):
    fig = px.scatter(t, x='por_10_mil', y='registros_acidentes', hover_name='segmento', size='equipamentos',
                     hover_data=['combinacoes_data_km', 'passagens', 'altas', 'dias_comuns'],
                     color_discrete_sequence=[TEAL], labels={**LABELS, 'registros_acidentes': 'Registros ANTT de acidentes (n)',
                     'segmento': 'Segmento', 'equipamentos': 'Radares', 'dias_comuns': 'Datas comuns',
                     'combinacoes_data_km': 'Combinações de data/quilômetro'})
    return style(fig, 'Registros de acidentes e índice por segmento de 5 km', 'Datas comuns dentro de cada segmento; sem causalidade.')


def locator(meta, selected_id=None):
    valid = meta.loc[meta.lat.between(-90, 90) & meta.lon.between(-180, 180)].copy()
    fig = px.scatter(valid, x='lon', y='lat', hover_name='identificador', custom_data=['identificador'],
                     hover_data=['municipio', 'km', 'sentido'],
                     labels={**LABELS, 'lon': 'Longitude publicada', 'lat': 'Latitude publicada'},
                     color_discrete_sequence=[TEAL])
    selected_indices = np.flatnonzero(valid.identificador.eq(selected_id).fillna(False).to_numpy(dtype=bool)).tolist()
    fig.update_traces(marker=dict(size=11), selected=dict(marker=dict(size=16)),
                      selectedpoints=selected_indices)
    fig.update_layout(clickmode='event+select', dragmode='pan')
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    return style(fig, 'Localização esquemática dos pontos publicados', 'Coordenadas da base A. Sem fundo cartográfico ou validação em campo.')
