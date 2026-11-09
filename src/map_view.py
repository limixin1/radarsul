"""Controles Streamlit do mapa e alternativa de navegação por teclado."""
import pandas as pd
import streamlit as st

from src.chart_locale import PT_BR
from src.corridor_map import corridor_figure
from src.query import AREAS, PAGES, br, plain, point_label
from src.spatial import CHECKED, ROAD_SOURCE, lookup, segment_label, segment_mask, spatial_records


@st.cache_data(show_spinner=False, max_entries=2)
def positions(package_token, source, has_reference, _frame, _road):
    return spatial_records(_frame, source, _road)


def normalize_focus(value, ids, cities):
    if value in ids:
        return value
    if value and value.startswith("km:"):
        number = value[3:]
        if number.isascii() and number.isdigit() and len(number) == 3:
            start = int(number)
            if 240 <= start <= 465 and start % 5 == 0:
                return f"km:{start}"
    if value and value.startswith("cidade:"):
        city = cities.get(plain(value[7:]))
        if city:
            return f"cidade:{city}"
    return None


def target_label(value, labels):
    if value.startswith("km:"):
        return segment_label(int(value[3:]))
    if value.startswith("cidade:"):
        return f"{value[7:]} · registros municipais da PRF"
    return labels[value]


def choose_focus(key):
    st.session_state.focus = st.session_state.get(key)


def choose_marker(valid):
    points = st.session_state["map_chart"]["selection"]["points"]
    codes = [item.get("customdata") for item in points if item.get("customdata") in valid]
    if codes:
        st.session_state.focus = codes[-1]


def open_report(points):
    st.session_state.points = list(points)
    st.session_state.page = PAGES[4]


def include_city(city):
    st.session_state.city = city
    st.session_state.area = AREAS[1]
    st.session_state.points = None
    st.session_state.scope = None


def focus_list(targets, labels, key):
    selected = st.session_state.focus
    if st.session_state.get(key) != selected:
        st.session_state[key] = selected
    st.selectbox("Selecionar ponto ou trecho na lista", targets, index=None,
                 format_func=lambda value: target_label(value, labels), key=key,
                 on_change=choose_focus, args=(key,), placeholder="Escolha uma localização")


def lookup_targets(search, meta, prf, ids):
    kind, value = lookup(search, meta, prf)
    selected = meta.loc[meta.identificador.isin(ids)]
    if kind == "trecho":
        matches = selected.loc[segment_mask(selected.km, value)].identificador.tolist()
        return kind, value, [f"km:{value}", *matches]
    if kind == "cidade":
        matches = selected.loc[selected.municipio.map(plain).eq(plain(value))].identificador.tolist()
        return kind, value, [*matches, f"cidade:{value}"]
    if kind == "ponto":
        return kind, value, [value] if value in ids else []
    if kind == "cidades":
        return kind, value, [f"cidade:{city}" for city in value]
    return kind, value, list(ids) if kind is None else []


def location_table(frame):
    columns = {
        "codigo": "Código da fonte", "municipio": "Município informado", "km": "Km",
        "sentido": "Sentido", "precisao": "Localização", "motivo_localizacao": "Verificação",
        "origem_coordenada": "Origem", "data": "Data",
    }
    display = frame.loc[:, [c for c in columns if c in frame]].rename(columns=columns)
    if "Km" in display:
        display["Km"] = display["Km"].map(lambda value: br(value, 3))
    return display


def render_locator(meta, frames, ids, years, package_token, reference, radar_positions, card):
    st.subheader("Localize no corredor")
    search = st.text_input("Buscar município, km ou código do ponto",
                           placeholder="Laguna, km 304+000 ou VC101-9", max_chars=64, key="map_search")
    prf = frames.get("ocorrencias")
    kind, value, targets = lookup_targets(search, meta, prf, ids)
    labels = {r.identificador: point_label(r) for r in meta.itertuples(index=False)}
    focus = st.session_state.focus
    if kind == "fora":
        st.info(f"O km {br(value, 3)} fica fora do corredor consultado.")
    elif kind == "desconhecido":
        st.info("Local não encontrado no cadastro de pontos nem nos municípios publicados pela PRF. Confira o nome ou busque pelo km.")
    elif kind == "cidades":
        st.caption("A busca corresponde a mais de um município. Escolha na lista.")
    elif kind in ("cidade", "ponto"):
        city = value if kind == "cidade" else meta.loc[meta.identificador.eq(value), "municipio"].iloc[0]
        city_has_points = meta.municipio.map(plain).eq(plain(city)).any()
        if not city_has_points:
            st.info(f"{city} consta nos registros PRF deste snapshot. O cadastro de tráfego do painel não contém ponto no município.")
        elif not any(target in ids for target in targets):
            st.info("Há equipamento cadastrado neste local fora da seleção atual. A cobertura pode ser exploratória.")
            st.button("Consultar todos os equipamentos deste município", on_click=include_city,
                      args=(city,), key="map_all_city")
    if kind == "trecho" and len(targets) == 1:
        st.caption("Nenhum ponto selecionado nesse trecho. A ficha pode usar referências de acidentes por km.")
    if focus and focus not in targets:
        targets.append(focus)

    with st.expander("Camadas e enquadramento"):
        show_radar = st.checkbox("Pontos de velocidade ANTT", value=True, key="map_radar")
        show_prf = st.checkbox("Ocorrências PRF", key="map_prf")
        show_antt = st.checkbox("Registros de acidentes ANTT por km", key="map_antt")
        zoom = st.checkbox("Aproximar seleção", key="map_zoom")
    shown = radar_positions.loc[radar_positions.codigo.isin(ids)]
    matched = [value for value in targets if value in ids]
    if kind is not None:
        shown = shown.loc[shown.codigo.isin(matched)]
    prf_positions = pd.DataFrame()
    prf_scope = "corredor integral"
    if show_prf and prf is not None:
        prf_positions = positions(package_token, "PRF", reference is not None, prf, reference)
        prf_positions = prf_positions.loc[prf_positions.ano.isin(years)]
        scope = focus
        if kind == "trecho":
            scope = f"km:{value}"
        elif kind == "cidade":
            scope = f"cidade:{value}"
        if scope and scope.startswith("km:"):
            segment = int(scope[3:])
            prf_scope = segment_label(segment)
            prf_positions = prf_positions.loc[segment_mask(prf_positions.km, segment)]
        elif scope:
            city = scope[7:] if scope.startswith("cidade:") else meta.loc[meta.identificador.eq(scope), "municipio"].iloc[0]
            prf_scope = f"{city}, município informado pela PRF"
            prf_positions = prf_positions.loc[prf_positions.municipio.map(plain).eq(plain(city))]
        elif st.session_state.city != "Todas as cidades":
            prf_scope = f"{st.session_state.city}, município informado pela PRF"
            prf_positions = prf_positions.loc[prf_positions.municipio.map(plain).eq(plain(st.session_state.city))]
    visible_prf = (prf_positions.loc[prf_positions.precisao.eq(CHECKED)]
                   if not prf_positions.empty else prf_positions)

    map_col, detail_col = st.columns([3, 2], gap="medium")
    with map_col:
        if reference is None:
            st.info("Eixo cartográfico indisponível. A lista mantém as referências por km e as fichas.")
        else:
            figure = corridor_figure(reference, shown if show_radar else shown.iloc[:0], visible_prf, focus, zoom)
            st.plotly_chart(figure, key="map_chart", theme=None, width="stretch",
                            selection_mode="points",
                            on_select=lambda: choose_marker(set(shown.codigo)),
                            config={"displaylogo": False, "locale": "pt-BR",
                                    "locales": {"pt-BR": PT_BR}, "scrollZoom": False,
                                    "toImageButtonOptions": {"filename": "sentinela_mapa_br101_sc",
                                                             "width": 1000, "height": 700}})
            st.caption("Linha: eixo BR-101/SC. Círculos: equipamentos ANTT. Número no círculo: equipamentos na mesma posição. Losangos: ocorrências PRF com posição compatível.")
            if show_prf:
                st.caption(f"Mapa PRF · {prf_scope} · ambos os sentidos · anos {", ".join(map(str, years))}.")
            st.caption(f"{ROAD_SOURCE}. O eixo é uma referência espacial. A triagem não certifica pista, sentido ou posição em campo.")
    with detail_col:
        if card:
            st.markdown(f"**{card.local}**")
            st.write(card.evidencia)
            st.caption(card.cobertura)
            st.caption(card.localizacao["precisao"] + ". " + card.localizacao["motivo_localizacao"])
            st.write(card.proximo_passo)
            scope_points = meta.loc[meta.identificador.isin(ids)]
            if focus.startswith("km:"):
                scope_points = scope_points.loc[segment_mask(scope_points.km, int(focus[3:]))]
            elif focus.startswith("cidade:"):
                scope_points = scope_points.loc[scope_points.municipio.map(plain).eq(plain(focus[7:]))]
            else:
                scope_points = scope_points.loc[scope_points.identificador.eq(focus)]
            st.caption("A ficha abre com os pontos deste local que fazem parte da seleção atual.")
            st.button("Abrir ficha preventiva", on_click=open_report,
                      args=(scope_points.identificador.tolist(),), key="open_preventive")
        else:
            st.markdown("**Escolha uma localização**")
            st.write("Clique em um círculo ou selecione um ponto ou trecho na lista. Os sentidos de pontos na mesma posição aparecem separadamente.")
    if targets:
        focus_list(targets, labels, "map_focus_choice")
    with st.expander("Lista de localizações e precisão"):
        if shown.empty:
            st.write("Nenhum equipamento da consulta nesta busca.")
        else:
            st.table(location_table(shown))
        if show_prf:
            if prf is None:
                st.info("Fonte PRF indisponível neste snapshot.")
            elif prf_positions.empty:
                st.info("Nenhum registro PRF encontrado nos anos e no recorte escolhidos. Confira a cobertura na ficha.")
            else:
                st.caption(f"{len(visible_prf)} de {len(prf_positions)} ocorrências PRF passam pela triagem espacial. Consulte as demais pelo km informado.")
                st.dataframe(location_table(prf_positions), hide_index=True)
        if show_antt:
            rows = frames["antt_acidentes"].loc[lambda d: d.ano.isin(years)]
            if kind == "trecho":
                rows = rows.loc[segment_mask(rows.km, value)]
            elif focus and focus.startswith("km:"):
                rows = rows.loc[segment_mask(rows.km, int(focus[3:]))]
            elif focus in ids:
                point = meta.loc[meta.identificador.eq(focus)].iloc[0]
                rows = rows.loc[segment_mask(rows.km, int(point.km // 5 * 5))]
            elif kind in ("cidade", "cidades") or focus or st.session_state.city != "Todas as cidades":
                rows = rows.iloc[:0]
                st.caption("A fonte ANTT não informa município. Busque por km para consultar o trecho.")
            st.caption("Acidentes ANTT · referência por km e ano. As repetições publicadas são preservadas.")
            if rows.empty:
                st.write("Nenhum registro disponível neste recorte da lista. Confira a cobertura por fonte.")
            else:
                grouped = rows.groupby(["ano", "km"]).size().rename("Registros publicados").reset_index()
                st.dataframe(grouped.rename(columns={"ano": "Ano", "km": "Km publicado"}), hide_index=True)
