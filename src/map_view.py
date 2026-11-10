"""Controles Streamlit do mapa e alternativa de navegação por teclado."""
import pandas as pd
import streamlit as st

from src.corridor_map import corridor_payload, google_maps_url, map_component, segment_shapes, segment_for, location_precision
from src.explain import render_explanation
from src.query import AREAS, PAGES, br, plain, point_label
from src.spatial import CHECKED, city_options, lookup, parse_km, segment_label, segment_mask, spatial_records


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
        return f"{value[7:]} · ficha municipal"
    return labels[value]


def choose_focus(value, meta, cities):
    focus = normalize_focus(value, meta.identificador.tolist(), cities)
    if focus is None:
        st.session_state.focus = None
        return
    if focus in meta.identificador.values and focus not in st.session_state.points:
        row = meta.loc[meta.identificador.eq(focus)].iloc[0]
        st.session_state.area = AREAS[1]
        st.session_state.city = row.municipio
        if row.sentido in ("Crescente", "Decrescente") and row.sentido not in st.session_state.directions:
            st.session_state.directions = [row.sentido]
        st.session_state.points = [focus]
        st.session_state.scope = None
    elif focus.startswith("cidade:"):
        city = focus[7:]
        matches = set(meta.loc[meta.municipio.map(plain).eq(plain(city)), "identificador"])
        if matches and not matches.intersection(st.session_state.points or []):
            include_city(city)
        elif not matches:
            st.session_state.city = "Todas as cidades"
            st.session_state.points = []
            st.session_state.scope = None
    st.session_state.focus = focus


def apply_search(meta, prf, cities):
    kind, value = lookup(st.session_state.map_search, meta, prf)
    target = {"cidade": f"cidade:{value}", "trecho": f"km:{value}", "ponto": value}.get(kind)
    if target:
        choose_focus(target, meta, cities)


def choose_marker(meta, cities):
    choose_focus(st.session_state["map_chart"]["selected"], meta, cities)


def open_report(points):
    st.session_state.points = list(points)
    st.session_state.page = PAGES[4]


def include_city(city):
    st.session_state.city = city
    st.session_state.area = AREAS[1]
    st.session_state.points = None
    st.session_state.scope = None


def focus_list(targets, labels, key, meta, cities):
    selected = st.session_state.focus
    if st.session_state.get(key) != selected:
        st.session_state[key] = selected
    st.selectbox("Selecionar ponto ou trecho na lista", targets, index=None,
                 format_func=lambda value: target_label(value, labels), key=key,
                 on_change=lambda: choose_focus(st.session_state[key], meta, cities), placeholder="Escolha uma localização")


def lookup_targets(search, meta, prf):
    kind, value = lookup(search, meta, prf)
    selected = meta
    if kind == "trecho":
        matches = selected.loc[segment_mask(selected.km, value)].identificador.tolist()
        return kind, value, [f"km:{value}", *matches]
    if kind == "cidade":
        matches = selected.loc[selected.municipio.map(plain).eq(plain(value))].identificador.tolist()
        return kind, value, [*matches, f"cidade:{value}"]
    if kind == "ponto":
        return kind, value, [value]
    if kind == "cidades":
        return kind, value, [f"cidade:{city}" for city in value]
    return kind, value, list(meta.identificador) if kind is None else []


def location_table(frame, shapes):
    columns = {
        "codigo": "Código da fonte", "municipio": "Município informado", "km": "Km",
        "sentido": "Sentido", "precisao": "Localização", "motivo_localizacao": "Verificação",
        "origem_coordenada": "Origem", "data": "Data",
    }
    display = frame.loc[:, [c for c in columns if c in frame]].rename(columns=columns)
    display["Representação no mapa"] = [
        location_precision(row, shapes) for row in frame.itertuples(index=False)
    ]
    if "Km" in display:
        display["Km"] = display["Km"].map(lambda value: br(value, 3))
    return display


def render_locator(meta, frames, ids, years, package_token, reference, radar_positions, card, page):
    st.subheader("Localize no corredor")
    prf = frames.get("ocorrencias")
    cities = city_options(meta, prf)
    search = st.text_input("Buscar município, km ou código do ponto",
                           placeholder="Laguna, km 304+000 ou VC101-9", max_chars=64, key="map_search",
                           on_change=apply_search, args=(meta, prf, cities))
    kind, value, targets = lookup_targets(search, meta, prf)
    labels = {r.identificador: point_label(r) + (" · fora dos filtros atuais" if r.identificador not in ids else "")
              for r in meta.itertuples(index=False)}
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
    shapes = segment_shapes() if reference is not None else {}
    searched_km = parse_km(search) if kind == "trecho" else None
    if searched_km is not None and segment_for(searched_km, shapes) is None:
        st.info(f"O km {br(searched_km, 3)} tem apenas referência textual neste eixo. "
                "Consulte o intervalo na lista.")
    if kind == "trecho" and len(targets) == 1:
        st.caption("Nenhum ponto selecionado nesse trecho. A ficha pode usar referências de acidentes por km.")
    if kind is None:
        targets += [f"cidade:{city}" for city in sorted(cities.values())]
    if focus and focus not in targets:
        targets.append(focus)

    with st.expander("Camadas e enquadramento"):
        show_radar = st.checkbox("Pontos de velocidade ANTT", value=True, key="map_radar")
        show_prf = st.checkbox("Ocorrências PRF", key="map_prf")
        show_antt = st.checkbox("Registros de acidentes ANTT por km", key="map_antt")
    shown = radar_positions
    if kind is not None:
        shown = shown.loc[shown.codigo.isin(targets)]
    prf_positions = pd.DataFrame()
    prf_scope = "corredor integral"
    prf_anchors = pd.DataFrame()
    focus_city = plain(focus[7:]) if focus and focus.startswith("cidade:") else None
    location_cities = {plain(value)} if kind == "cidade" else set()
    if focus_city:
        location_cities.add(focus_city)
    location_cities -= set(radar_positions.municipio.map(plain))
    if prf is not None and location_cities:
        # A camada e a ficha continuam limitadas aos anos solicitados.
        published = positions(package_token, "PRF", reference is not None, prf, reference)
        prf_anchors = published.loc[published.municipio.map(plain).isin(location_cities)]
        st.caption("A busca municipal usa a localização de registros publicados pela PRF como referência. "
                   "Confira os anos cobertos na ficha.")
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
    antt = frames["antt_acidentes"].iloc[:0]
    if show_antt:
        antt = frames["antt_acidentes"].loc[lambda d: d.ano.isin(years)]
        if kind == "trecho" or (focus and focus.startswith("km:")):
            segment = value if kind == "trecho" else int(focus[3:])
            antt = antt.loc[segment_mask(antt.km, segment)]
        elif focus in ids:
            point = meta.loc[meta.identificador.eq(focus)].iloc[0]
            antt = antt.loc[segment_mask(antt.km, int(point.km // 5 * 5))]
        elif kind in ("cidade", "cidades") or focus or st.session_state.city != "Todas as cidades":
            antt = antt.iloc[:0]

    if targets:
        focus_list(targets, labels, "map_focus_choice", meta, cities)
    map_col, detail_col = st.columns([3, 2], gap="medium")
    with map_col:
        if not shapes:
            st.info("Eixo cartográfico indisponível. A lista mantém as referências por km e as fichas.")
        else:
            map_kind = "texto" if searched_km is not None and segment_for(searched_km, shapes) is None else kind
            search_data = {"kind": map_kind, "value": plain(value) if kind == "cidade" else value}
            payload = corridor_payload(shapes, shown, radar_positions, prf_positions, prf_anchors, antt,
                                       set(ids), focus, search_data, show_radar)
            map_component()(data=payload, key="map_chart", on_selected_change=lambda: choose_marker(meta, cities))
            if show_prf:
                st.caption(f"Mapa PRF · {prf_scope} · ambos os sentidos · anos {", ".join(map(str, years))}.")
            st.caption("Marcadores usam coordenadas triadas. Faixas no eixo representam intervalos aproximados de 5 km. "
                       "A lista distingue a referência por km da localização apenas textual.")
    with detail_col:
        if card:
            with st.container(key="point_summary"):
                st.markdown(card.summary_markdown(compact=True))
                maps_url, precise = google_maps_url(focus, radar_positions, cities)
                if maps_url:
                    st.link_button("Abrir no Google Maps" if precise else "Google Maps · Busca aproximada", maps_url)
                with st.expander("Ver dados e fontes"):
                    st.markdown(card.technical_markdown(include_annual=True))
            render_explanation(card, package_token, focus)
            scope_points = meta.loc[meta.identificador.isin(ids)]
            if focus.startswith("km:"):
                scope_points = scope_points.loc[segment_mask(scope_points.km, int(focus[3:]))]
            elif focus.startswith("cidade:"):
                scope_points = scope_points.loc[scope_points.municipio.map(plain).eq(plain(focus[7:]))]
            else:
                scope_points = scope_points.loc[scope_points.identificador.eq(focus)]
            if page != PAGES[4]:
                st.caption("A ficha abre com os pontos deste local que fazem parte da seleção atual.")
                st.button("Abrir ficha preventiva", on_click=open_report,
                          args=(scope_points.identificador.tolist(),), key="open_preventive")
        else:
            st.markdown("**Escolha uma localização**")
            st.write("Clique em um círculo ou selecione um ponto ou trecho na lista. Os sentidos de pontos na mesma posição aparecem separadamente.")
    with st.expander("Lista de localizações e precisão"):
        if shown.empty:
            st.write("Nenhum equipamento da consulta nesta busca.")
        else:
            st.table(location_table(shown, shapes))
        if show_prf:
            if prf is None:
                st.info("Fonte PRF indisponível neste snapshot.")
            elif prf_positions.empty:
                st.info("Nenhum registro PRF encontrado nos anos e no recorte escolhidos. Confira a cobertura na ficha.")
            else:
                st.caption(f"{len(visible_prf)} de {len(prf_positions)} ocorrências PRF passam pela triagem espacial. Consulte as demais pelo km informado.")
                st.dataframe(location_table(prf_positions, shapes), hide_index=True)
        if show_antt:
            st.caption("Acidentes ANTT · referência por km e ano. A fonte não informa município. As repetições publicadas são preservadas.")
            if antt.empty:
                st.write("Nenhum registro disponível neste recorte da lista. Busque por km e confira a cobertura por fonte.")
            else:
                grouped = antt.groupby(["ano", "km"]).size().rename("Registros publicados").reset_index()
                grouped["Representação no mapa"] = [
                    "trecho" if segment_for(km, shapes) else "texto" for km in grouped.km
                ]
                st.dataframe(grouped.rename(columns={"ano": "Ano", "km": "Km publicado"}), hide_index=True)
