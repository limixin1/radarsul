import io
import json
import zipfile

import pandas as pd

from src.corridor_map import corridor_figure
from src.exports import bundle, markdown_report, metadata
from src.map_view import normalize_focus
from src.preventive import CHECK_FIELD, build_card
from src.query import AREAS, DIRECTIONS, PAGES, parse_url, query_tables, url_state
from src.spatial import CHECKED, KM_ONLY, UNCERTAIN, city_options, lookup, road, spatial_records


def test_spatial_validation_uses_reference_and_preserves_colocated_senses(package):
    _, frames, _ = package
    radar = frames["antt_equipamentos"]
    reference = road()
    classified = spatial_records(radar, "ANTT", reference)
    twins = classified.loc[classified.codigo.isin(["VC101-6", "VC101-8"])]
    assert len(twins) == 2 and twins.precisao.eq(CHECKED).all()
    assert set(twins.sentido) == {"Crescente", "Decrescente"}
    figure = corridor_figure(reference, twins, pd.DataFrame(), focus="VC101-8")
    assert list(figure.data[-1].text) == ["2"]
    assert list(figure.data[-1].customdata) == ["VC101-8"]
    assert "Crescente" in figure.data[-1].hovertext[0] and "Decrescente" in figure.data[-1].hovertext[0]
    point = radar.loc[radar.identificador.eq("VC101-9")].copy()
    assert spatial_records(point, "ANTT", None).iloc[0].precisao == KM_ONLY
    point["lat"] = -28.8
    wrong = spatial_records(point, "ANTT", reference).iloc[0]
    assert wrong.precisao == UNCERTAIN and pd.isna(wrong.latitude)


def test_lookup_km_and_prf_municipality_without_radar(package):
    _, frames, _ = package
    points, prf = frames["antt_equipamentos"], frames["ocorrencias"]
    assert lookup(" km 304+000 ", points, prf) == ("trecho", 300)
    assert lookup("Criciuma", points, prf) == ("cidade", "Criciúma")
    assert lookup("passo de torres", points, prf) == ("cidade", "Passo de Torres")
    assert lookup("km 700", points, prf)[0] == "fora"
    assert lookup("imbituba", points, prf) == ("cidade", "Imbituba")
    assert lookup("VC101-9", points, prf) == ("ponto", "VC101-9")
    cities = city_options(points, prf)
    assert normalize_focus("km:300", [], cities) == "km:300"
    assert normalize_focus("cidade:passo de torres", [], cities) == "cidade:Passo de Torres"
    assert normalize_focus("km:301", [], cities) is None
    assert normalize_focus("VC101-9", [], cities) is None
    legacy = url_state(PAGES[0], [2024, 2025], AREAS[0], DIRECTIONS, "Laguna", ["VC101-9"])
    assert "foco" not in legacy
    params = {k: v if isinstance(v, list) else [v] for k, v in {**legacy, "foco": "VC101-9"}.items()}
    assert parse_url(params, points)[0]["focus"] == "VC101-9"


def test_card_and_exports_use_same_facts_and_preserve_history(package):
    manifest, frames, _ = package
    points = frames["antt_equipamentos"]
    ids, years = ["VC101-9"], [2024, 2025]
    selection, eq, cov = query_tables(frames["antt_diario"], points, ids, years, manifest["cobertura"]["trafego"])
    positions = spatial_records(points, "ANTT", road())
    card = build_card(ids[0], points, eq, cov, frames, manifest, years, positions)
    assert "7.091 de 11.178.995" in card.evidencia and "6,343" in card.evidencia
    assert card.proximo_passo == CHECK_FIELD
    assert "Para avaliar blitz, documente um problema atual" in card.falta
    assert all("independente do radar" in line for line in card.contexto)
    meta = metadata(manifest, dict(page=PAGES[4], years=years, area=AREAS[0], city="Laguna",
                    directions=DIRECTIONS, points=ids, focus=ids[0]), ids, selection, [])
    meta["ficha_preventiva"] = card.metadata()
    rendered = markdown_report(selection, eq, cov, meta, card=card)
    with zipfile.ZipFile(io.BytesIO(bundle(eq, cov, meta, rendered))) as archive:
        assert card.markdown() in archive.read("relatorio.md").decode()
        assert json.loads(archive.read("metadados.json"))["ficha_preventiva"]["evidencia"] == card.evidencia
        assert "foco=VC101-9" in meta["consulta_relativa"]
    zero = eq.assign(altas=0, por_10_mil=0)
    assert "Nenhuma contagem" in build_card(ids[0], points, zero, cov, frames, manifest, years, positions).achado
    partial = eq.assign(elegivel=False)
    assert "exploratório" in build_card(ids[0], points, partial, cov, frames, manifest, [2026], positions).achado
    empty = build_card("cidade:Passo de Torres", points, eq.iloc[:0], cov.iloc[:0],
                       frames, manifest, [2026], positions)
    assert "Indisponível" in empty.contexto[0]
    assert "evidencia" in empty.metadata()
    segment = build_card("km:300", points, eq, cov, frames, manifest, years, positions)
    assert "7.091 de 11.178.995" in segment.evidencia
    assert segment.localizacao["precisao"] == KM_ONLY
