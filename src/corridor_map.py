"""Mapa local, com seleção de equipamentos e eixo de referência sem mapa-base remoto."""
from collections import defaultdict

import plotly.graph_objects as go

from src.query import br
from src.spatial import ANCHOR, CHECKED, ROAD_SOURCE, SCALE


def corridor_figure(reference, points, prf, focus=None, zoom=False):
    figure = go.Figure()
    lons, lats = [], []
    if reference is not None:
        for path in reference.paths:
            lons.extend([*path[:, 0], None])
            lats.extend([*path[:, 1], None])
        figure.add_scatter(x=lons, y=lats, mode="lines", hoverinfo="skip",
                           name="BR-101/SC · eixo SNV", line={"color": "#597182", "width": 2})

    if not prf.empty:
        figure.add_scatter(
            x=prf.longitude.tolist(), y=prf.latitude.tolist(), mode="markers",
            name="Ocorrência PRF", marker={"symbol": "diamond", "color": "#885517", "size": 7, "opacity": .7},
            text=[f"PRF · {row.municipio} · km {br(row.km, 3)}<br>{row.data} · {CHECKED}"
                  for row in prf.itertuples(index=False)],
            hovertemplate="%{text}<extra></extra>",
        )

    groups = defaultdict(list)
    for row in points.loc[points.precisao.eq(CHECKED)].itertuples(index=False):
        groups[row.longitude, row.latitude].append(row)
    if groups:
        highlighted = [any(row.codigo == focus for row in group) for group in groups.values()]
        figure.add_scatter(
            x=[lon for lon, _ in groups], y=[lat for _, lat in groups], mode="markers+text",
            name="Equipamento ANTT", text=[str(len(group)) if len(group) > 1 else "" for group in groups.values()],
            textfont={"color": "#FFFFFF", "size": 11},
            marker={"color": ["#143047" if flag else "#075E68" for flag in highlighted],
                    "size": [24 if flag or len(group) > 1 else 13
                             for flag, group in zip(highlighted, groups.values())],
                    "line": {"color": "#FFFFFF", "width": 2}},
            customdata=[next((r.codigo for r in group if r.codigo == focus), group[0].codigo)
                        for group in groups.values()],
            hovertext=["<br>".join(f"{r.municipio} · km {br(r.km, 3)} · {r.sentido} · {r.codigo}"
                                  for r in group) for group in groups.values()],
            hovertemplate="%{hovertext}<br>" + CHECKED + "<extra></extra>",
            selected={"marker": {"opacity": 1}}, unselected={"marker": {"opacity": .85}},
        )
    if zoom:
        active = points.loc[points.codigo.eq(focus) & points.precisao.eq(CHECKED)]
        if not active.empty:
            lon, lat = active[["longitude", "latitude"]].iloc[0]
            figure.update_xaxes(range=[lon - .065, lon + .065])
            figure.update_yaxes(range=[lat - .06, lat + .06])
        elif reference is not None and focus and focus.startswith("km:"):
            start = int(focus[3:])
            vertices = reference.vertices[(reference.start_km >= start) & (reference.start_km <= start + 5)]
            if len(vertices):
                coords = vertices / SCALE + ANCHOR
                mins, maxs = coords.min(axis=0) - .035, coords.max(axis=0) + .035
                figure.update_xaxes(range=[mins[0], maxs[0]])
                figure.update_yaxes(range=[mins[1], maxs[1]])
        elif groups:
            xs, ys = zip(*groups)
            figure.update_xaxes(range=[min(xs) - .055, max(xs) + .055])
            figure.update_yaxes(range=[min(ys) - .055, max(ys) + .055])
    figure.update_layout(
        height=395, margin={"t": 14, "b": 42, "l": 12, "r": 12},
        paper_bgcolor="#F5F8F8", plot_bgcolor="#E8F0F1",
        hoverlabel={"bgcolor": "#FFFFFF", "font_color": "#142B3C"},
        font={"color": "#142B3C"}, showlegend=False, clickmode="event+select",
        dragmode="pan",
    )
    figure.add_annotation(xref="paper", yref="paper", x=0, y=0, yshift=-12,
                          text=ROAD_SOURCE, showarrow=False, xanchor="left", yanchor="top",
                          font={"size": 10, "color": "#142B3C"})
    figure.add_annotation(xref="paper", yref="paper", x=1, y=1,
                          text="↑ N", showarrow=False, xanchor="right", yanchor="top")
    figure.update_xaxes(visible=False, constrain="domain")
    figure.update_yaxes(visible=False, scaleanchor="x", scaleratio=float(SCALE[1] / SCALE[0]),
                        constrain="domain")
    return figure
