"""Inventário do snapshot por município, ano, fonte e estado de posição."""
import json
from collections import Counter

from src.data_package import validate
from src.spatial import road, spatial_records


def inventory():
    manifest, frames, _ = validate()
    reference = road()
    meta = frames["antt_equipamentos"]
    devices = spatial_records(meta, "ANTT", reference)
    prf = spatial_records(frames["ocorrencias"], "PRF", reference)
    antt = frames["antt_acidentes"]
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
