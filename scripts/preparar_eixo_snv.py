"""Normaliza um recorte GeoJSON já baixado do serviço SNV espelhado no Ibama."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode

SERVICE = (
    "https://pamgia.ibama.gov.br/server/rest/services/BasesSincronizadas/"
    "line_rodovias_federais_dnit_l/MapServer/0/query"
)
PARAMS = {
    "where": "sg_uf='SC' AND vl_br='101' AND vl_km_inic < 465.1 AND vl_km_fina > 244.68",
    "outFields": "id_trecho_,vl_br,sg_uf,nm_tipo_tr,vl_km_inic,vl_km_fina,vl_extensa",
    "outSR": "4326", "orderByFields": "vl_km_inic", "f": "geojson",
}


def prepare(raw, collected):
    data = json.loads(raw)
    features = []
    for feature in data["features"]:
        props, shape = feature["properties"], feature["geometry"]
        if props["nm_tipo_tr"] != "Eixo Principal":
            continue
        if (props["sg_uf"], props["vl_br"], shape["type"]) != ("SC", "101", "LineString"):
            raise ValueError("Geometria inesperada no recorte SNV.")
        features.append({
            "type": "Feature",
            "properties": {"id": props["id_trecho_"], "inicio": props["vl_km_inic"],
                           "fim": props["vl_km_fina"]},
            "geometry": {"type": "LineString", "coordinates": [
                [round(lon, 6), round(lat, 6)] for lon, lat in shape["coordinates"]
            ]},
        })
    if not features:
        raise ValueError("Recorte SNV sem eixo principal.")
    return {"type": "FeatureCollection", "proveniencia": {
        "fonte": "DNIT · Sistema Nacional de Viação (SNV), 25/07/2024, via Ibama",
        "consulta": SERVICE + "?" + urlencode(PARAMS),
        "coleta": collected, "sha256_resposta": hashlib.sha256(raw).hexdigest(),
    }, "features": sorted(features, key=lambda f: f["properties"]["inicio"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origem", type=Path)
    parser.add_argument("destino", type=Path)
    parser.add_argument("--coleta", required=True)
    args = parser.parse_args()
    args.destino.write_text(
        json.dumps(prepare(args.origem.read_bytes(), args.coleta),
                   ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8",
    )
