"""Inventário do snapshot por município, ano, fonte e estado de posição."""
import json
from collections import Counter

from src.corridor_map import location_precision, segment_for, segment_shapes
from src.data_package import validate
from src.query import plain
from src.spatial import city_options, road, spatial_records


def inventory():
    manifest, frames, _ = validate()
    reference = road()
    meta = frames["antt_equipamentos"]
    devices = spatial_records(meta, "ANTT", reference)
    prf = spatial_records(frames["ocorrencias"], "PRF", reference)
    antt = frames["antt_acidentes"]
    shapes = segment_shapes()
    cities = city_options(meta, frames["ocorrencias"])
    sources = {"equipamentos_antt": devices, "ocorrencias_prf": prf}
    by_city = {}
    for source, frame in sources.items():
        frame["representacao_mapa"] = [location_precision(row, shapes) for row in frame.itertuples(index=False)]
        keys = frame.municipio.map(plain)
        by_city[source] = {cities[key]: dict(Counter(frame.loc[keys.eq(key), "representacao_mapa"]))
                           for key in sorted(set(keys)) if key in cities}
    antt_map = ["trecho" if segment_for(km, shapes) else "texto" for km in antt.km]
    daily = frames["antt_diario"].merge(meta[["identificador", "municipio"]],
                                      on="identificador", validate="many_to_one")
    traffic = daily.groupby(["municipio", "ano"], as_index=False).agg(
        pontos=("identificador", "nunique"), dias_com_publicacao=("data", "nunique"),
        contagens=("passagens", "sum"),
    )
    return {
        "snapshot": manifest["versao"],
        "cobertura_declarada": manifest["cobertura"],
        "eixo": {"segmentos": len(reference.paths), "arestas": len(reference.vertices)},
        "representacao_mapa": {
            **{source: dict(Counter(frame.representacao_mapa)) for source, frame in sources.items()},
            "acidentes_antt": dict(Counter(antt_map)),
            "municipios": {label: {source: by_city[source].get(label, {}) for source in sources}
                           for label in sorted(cities.values())},
            "intervalos_do_eixo": {key: shape["ranges"] for key, shape in shapes.items()},
        },
        "equipamentos_antt_por_estado": dict(Counter(devices.precisao)),
        "prf_por_estado": dict(Counter(prf.precisao)),
        "equipamentos_antt": json.loads(devices.to_json(orient="records")),
        "antt_trafego_por_municipio_ano": traffic.to_dict(orient="records"),
        "prf_por_municipio_ano_estado": prf.groupby(["municipio", "ano", "precisao"])
            .size().rename("registros").reset_index().to_dict(orient="records"),
        "antt_acidentes_por_ano": {
            str(year): {"registros": len(rows), "km_min": float(rows.km.min()), "km_max": float(rows.km.max()),
                        "referencia": "km publicado. Município e coordenada ausentes."}
            for year, rows in antt.groupby("ano")
        },
    }


if __name__ == "__main__":
    print(json.dumps(inventory(), ensure_ascii=False, indent=2, allow_nan=False))
