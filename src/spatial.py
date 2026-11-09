"""Triagem espacial de posições publicadas e pesquisa textual do corredor."""
from dataclasses import dataclass
from functools import lru_cache
import json
import math
import re

import numpy as np
import pandas as pd

from config import KM_MAX, KM_MIN, ROOT
from src.query import br, plain

ROAD_FILE = ROOT / "dados_geograficos" / "snv_br101_sc.geojson"
ROAD_SOURCE = "DNIT · SNV de 25/07/2024, via Ibama"
MAX_DISTANCE_M = 150
MAX_KM_DIFFERENCE = 1
CHECKED = "Coordenada compatível com o eixo SNV"
KM_ONLY = "Referência por km"
UNCERTAIN = "Coordenada ambígua · referência por km"
UNAVAILABLE = "Localização indisponível"
SCALE = np.array([111_195 * math.cos(math.radians(-28.6)), 111_195])
ANCHOR = np.array([-49, -28.6])


@dataclass(frozen=True)
class Road:
    paths: tuple
    vertices: np.ndarray
    vectors: np.ndarray
    lengths2: np.ndarray
    start_km: np.ndarray
    delta_km: np.ndarray


@lru_cache(maxsize=1)
def road():
    """O eixo é auxiliar. Falha de leitura deixa referências em km utilizáveis."""
    paths, starts, vectors, kms, increments = [], [], [], [], []
    try:
        features = json.loads(ROAD_FILE.read_text(encoding="utf-8"))["features"]
        for feature in features:
            props = feature["properties"]
            xy = np.asarray(feature["geometry"]["coordinates"], dtype=float)
            coords = (xy - ANCHOR) * SCALE
            delta = np.diff(coords, axis=0)
            lengths = np.linalg.norm(delta, axis=1)
            km = props["inicio"] + np.r_[0, lengths.cumsum()] / lengths.sum() * (
                props["fim"] - props["inicio"]
            )
            valid = lengths > 0
            starts.extend(coords[:-1][valid])
            vectors.extend(delta[valid])
            kms.extend(km[:-1][valid])
            increments.extend(np.diff(km)[valid])
            inside = (km >= KM_MIN) & (km <= KM_MAX)
            if inside.any():
                paths.append(xy[inside])
        if not paths:
            return None
        vectors = np.asarray(vectors)
        return Road(tuple(paths), np.asarray(starts), vectors,
                    np.einsum("ij,ij->i", vectors, vectors), np.asarray(kms),
                    np.asarray(increments))
    except (OSError, KeyError, TypeError, ValueError, IndexError):
        return None


def coordinate_check(lon, lat, km, reference):
    """Distância ao eixo no km compatível. Nunca corrige a coordenada publicada."""
    plausible = pd.notna(lat) and pd.notna(lon) and -30 <= lat <= -27 and -51 <= lon <= -48
    if not plausible or reference is None:
        return None
    nearby = np.abs(reference.start_km + reference.delta_km / 2 - km) <= MAX_KM_DIFFERENCE + .1
    if not nearby.any():
        return None
    offset = (np.array([lon, lat]) - ANCHOR) * SCALE - reference.vertices[nearby]
    vec = reference.vectors[nearby]
    fraction = np.clip(np.einsum("ij,ij->i", offset, vec) / reference.lengths2[nearby], 0, 1)
    dist = np.linalg.norm(offset - fraction[:, None] * vec, axis=1)
    estimate = reference.start_km[nearby] + fraction * reference.delta_km[nearby]
    candidates = dist[np.abs(estimate - km) <= MAX_KM_DIFFERENCE]
    return float(candidates.min()) if candidates.size else None


def spatial_records(frame, source, reference):
    """Classifica equipamentos ANTT ou ocorrências PRF sem alterar o snapshot."""
    radar = source == "ANTT"
    rows = []
    if frame is None:
        return pd.DataFrame()
    for row in frame.itertuples(index=False):
        lon, lat = (row.lon, row.lat) if radar else (row.longitude, row.latitude)
        br_uf = (row.rodovia, row.uf) if radar else (str(row.br), row.uf)
        km_valid = br_uf in {("BR-101", "SC"), ("101", "SC")} and pd.notna(row.km) and KM_MIN <= row.km <= KM_MAX
        conflict = ((row.km_distintos != 1 or row.sentidos_distintos != 1) if radar
                    else pd.isna(row.coordenada_suspeita) or bool(row.coordenada_suspeita))
        if radar and row.sentido not in ("Crescente", "Decrescente"):
            conflict = True
        if pd.isna(row.municipio) or not str(row.municipio).strip():
            conflict = True
        has_position = pd.notna(lon) and pd.notna(lat)
        distance = coordinate_check(lon, lat, row.km, reference) if km_valid and not conflict and has_position else None
        if not km_valid:
            status, reason = UNAVAILABLE, "BR, UF ou km fora do recorte"
        elif conflict:
            status, reason = UNCERTAIN, "Atributos conflitantes, ausentes ou marcados pela fonte"
        elif not has_position:
            status, reason = KM_ONLY, "Coordenada ausente ou incompleta"
        elif reference is None:
            status, reason = KM_ONLY, "Eixo de referência indisponível"
        elif distance is None or distance > MAX_DISTANCE_M:
            status, reason = UNCERTAIN, "Posição sem concordância espacial com o km no eixo disponível"
        else:
            status, reason = CHECKED, "Posição publicada passa pela triagem de km e distância"
        sense = row.sentido if radar else row.sentido_via
        if pd.isna(sense) or plain(sense) not in {"crescente", "decrescente"}:
            sense = "Sentido não informado"
        rows.append({
            "codigo": str(row.identificador if radar else row.id), "municipio": row.municipio,
            "km": float(row.km) if pd.notna(row.km) else None, "sentido": sense,
            "latitude": float(lat) if status == CHECKED else None,
            "longitude": float(lon) if status == CHECKED else None,
            "precisao": status, "motivo_localizacao": reason,
            "origem_coordenada": "Tráfego ANTT · metadados do equipamento" if radar else "PRF · ocorrência publicada",
            "distancia_eixo_m": round(distance, 1) if distance is not None else None,
            **({} if radar else {"ano": int(row.ano), "data": str(row.data.date()),
                                 "classificacao": row.classificacao_acidente}),
        })
    return pd.DataFrame(rows)


def city_options(points, prf):
    cities = {plain(city): city for city in points.municipio.dropna().unique()}
    if prf is not None:
        particles = {"de", "da", "do", "das", "dos"}
        for name in prf.municipio.dropna().unique():
            words = name.lower().split()
            label = " ".join(word.capitalize() if i == 0 or word not in particles else word
                             for i, word in enumerate(words))
            cities.setdefault(plain(name), label)
    return cities


def lookup(text, points, prf):
    """Reconhece município, identificador e referência km com vírgula, ponto ou +."""
    value = plain(text).strip()
    if not value:
        return None, None
    match = re.fullmatch(r"(?:km\s*)?(\d{1,3})(?:([,.+])(\d{1,3}))?", value)
    if match:
        integer, separator, fraction = match.groups()
        km = int(integer)
        if fraction:
            km += int(fraction) / (1000 if separator == "+" else 10 ** len(fraction))
        return ("trecho", int(km // 5 * 5)) if KM_MIN <= km <= KM_MAX else ("fora", km)
    direct = points.loc[points.identificador.map(plain).eq(value)]
    if not direct.empty:
        return "ponto", direct.iloc[0].identificador
    cities = city_options(points, prf)
    matches = [city for key, city in cities.items() if key == value]
    if not matches:
        matches = sorted(city for key, city in cities.items() if key.startswith(value))
    if len(matches) == 1:
        return "cidade", matches[0]
    return ("cidades", matches) if matches else ("desconhecido", value)


def segment_label(start):
    return f"BR-101/SC · km {br(max(KM_MIN, start), 3)} a {br(min(KM_MAX, start + 5), 3)}"


def segment_mask(kms, start):
    if start + 5 > KM_MAX:
        return kms.ge(max(start, KM_MIN)) & kms.le(KM_MAX)
    return kms.ge(max(start, KM_MIN)) & kms.lt(start + 5)
