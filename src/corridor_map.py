"""Dados espaciais do mapa compartilhado. O km não vira coordenada de ocorrência."""
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import streamlit as st

from config import KM_MAX, KM_MIN
from src.query import br, plain
from src.spatial import ANCHOR, CHECKED, ROAD_SOURCE, SCALE, UNAVAILABLE, road, segment_label

SATELLITE_URL = (
    "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/"
    "GoogleMapsCompatible/{z}/{y}/{x}.jpg"
)
SATELLITE_CREDIT = "EOX IT Services GmbH · Sentinel-2 cloudless 2016 · dados Copernicus modificados · CC BY 4.0"
ASSETS = Path(__file__).with_name("map_assets")


@lru_cache(maxsize=1)
def map_component():
    leaflet = (ASSETS / "leaflet-1.9.4.js").read_text(encoding="utf-8").split("//# sourceMappingURL=")[0]
    js = ("const L = (() => { const module = {exports:{}}; const exports = module.exports;\n"
          + leaflet + "\nreturn module.exports; })();\n")
    return st.components.v2.component(
        "sentinela_corredor",
        html=(ASSETS / "map.html").read_text(encoding="utf-8"),
        css="\n".join((ASSETS / file).read_text(encoding="utf-8") for file in ("leaflet-1.9.4.css", "map.css")),
        js=js + (ASSETS / "map.js").read_text(encoding="utf-8"),
    )


def km_bucket(km):
    return int(km // 5 * 5)


@lru_cache(maxsize=4)
def segment_shapes():
    """Interpola limites de intervalos sobre os vértices SNV. Conserva lacunas."""
    reference = road()
    if reference is None:
        return {}
    shapes = {}
    for bucket in range(km_bucket(KM_MIN), km_bucket(KM_MAX) + 1, 5):
        lo, hi = max(bucket, KM_MIN), min(bucket + 5, KM_MAX)
        starts = reference.start_km
        ends = starts + reference.delta_km
        overlap = (starts < hi) & (ends > lo)
        if not overlap.any():
            continue
        clipped = np.column_stack([np.maximum(starts[overlap], lo), np.minimum(ends[overlap], hi)])
        fractions = (clipped - starts[overlap, None]) / reference.delta_km[overlap, None]
        edges = reference.vertices[overlap, None, :] + fractions[:, :, None] * reference.vectors[overlap, None, :]
        paths = []
        for a, b in ((edges / SCALE + ANCHOR)[:, :, ::-1]).round(6).tolist():
            if paths and paths[-1][-1] == a:
                paths[-1].append(b)
            else:
                paths.append([a, b])
        ranges = []
        for start, end in sorted(clipped.tolist()):
            if ranges and start <= ranges[-1][1] + 1e-8:
                ranges[-1][1] = max(ranges[-1][1], end)
            else:
                ranges.append([start, end])
        shapes[str(bucket)] = {"paths": paths, "ranges": ranges, "label": segment_label(bucket)}
    return shapes


def segment_for(km, shapes):
    if km is None or not np.isfinite(km) or not KM_MIN <= km <= KM_MAX:
        return None
    key = str(km_bucket(km))
    shape = shapes.get(key)
    if shape and any(lo <= km <= hi for lo, hi in shape["ranges"]):
        return key
    return None


def location_precision(record, shapes):
    if record.precisao == CHECKED:
        return "marcador"
    if record.precisao != UNAVAILABLE and segment_for(record.km, shapes):
        return "trecho"
    return "texto"


def google_maps_url(focus, positions, cities):
    """Só coordenadas triadas entram em URLs. Trechos usam busca textual."""
    if focus.startswith("km:"):
        query = segment_label(int(focus[3:])).replace(" · ", " ")
    elif focus.startswith("cidade:"):
        city = cities.get(plain(focus[7:]))
        if not city:
            return None, False
        query = f"BR-101, {city}, SC"
    else:
        found = positions.loc[positions.codigo.eq(focus)]
        if found.empty or found.iloc[0].precisao == UNAVAILABLE:
            return None, False
        row = found.iloc[0]
        if row.precisao == CHECKED:
            query = f"{row.latitude:.6f},{row.longitude:.6f}"
            return "https://www.google.com/maps/search/?" + urlencode({"api": 1, "query": query}), True
        query = f"BR-101 km {br(row.km, 3)}, {row.municipio}, SC"
    return "https://www.google.com/maps/search/?" + urlencode({"api": 1, "query": query}), False


def map_records(frame, active=(), prf=False, shapes=None):
    shapes = shapes if shapes is not None else segment_shapes()
    records = []
    for row in frame.itertuples(index=False):
        city = row.municipio if isinstance(row.municipio, str) else "Município não informado"
        precision = location_precision(row, shapes)
        segment = segment_for(row.km, shapes) if row.precisao != UNAVAILABLE else None
        point = [row.latitude, row.longitude] if precision == "marcador" else None
        if prf:
            detail = f"{city} · km {br(row.km, 3)} · {row.data} · {row.sentido}"
        else:
            detail = f"{city} · km {br(row.km, 3)} · {row.sentido} · {row.codigo}"
        records.append({"id": row.codigo, "city": city, "cityKey": plain(city), "point": point,
                        "segment": segment, "precision": precision, "detail": detail,
                        "note": row.motivo_localizacao, "active": row.codigo in active})
    return records


def corridor_payload(shapes, shown, catalog, prf, prf_anchors, ant, active, focus, search, show_radar):
    incidents = {}
    for km in ant.km:
        key = segment_for(km, shapes)
        if key is not None:
            incidents[key] = incidents.get(key, 0) + 1
    return {"segments": shapes, "radars": map_records(shown, active, shapes=shapes) if show_radar else [],
            "places": map_records(catalog, active, shapes=shapes),
            "prf": map_records(prf, prf=True, shapes=shapes), "antt": incidents, "focus": focus,
            "anchors": map_records(prf_anchors, prf=True, shapes=shapes),
            "search": search, "axisCredit": ROAD_SOURCE, "satelliteUrl": SATELLITE_URL,
            "satelliteCredit": SATELLITE_CREDIT}
