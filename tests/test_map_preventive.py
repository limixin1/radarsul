import io
import json
import zipfile

import pandas as pd

from src.corridor_map import google_maps_url, location_precision, map_records, segment_for, segment_shapes
from src.explain import explain
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
    records = map_records(twins, active=["VC101-8"])
    assert len(records) == 2 and records[0]["point"] == records[1]["point"]
    assert {row["id"] for row in records} == {"VC101-6", "VC101-8"}
    assert [row["id"] for row in records if row["active"]] == ["VC101-8"]
    assert {"Crescente", "Decrescente"} == {row["detail"].split(" · ")[2] for row in records}
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
    assert card.proximo_passo.startswith("Medir velocidades atuais no km 304,000")
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
    assert "Nenhuma contagem" in build_card(ids[0], points, zero, cov.assign(altas=0), frames, manifest, years, positions).achado
    _, partial, partial_cov = query_tables(
        frames["antt_diario"], points, ids, [2026], manifest["cobertura"]["trafego"],
    )
    assert "exploratório" in build_card(ids[0], points, partial, partial_cov, frames, manifest, [2026], positions).achado
    empty = build_card("cidade:Passo de Torres", points, eq.iloc[:0], cov.iloc[:0],
                       frames, manifest, [2026], positions)
    assert "Indisponível" in empty.contexto[0]
    assert "evidencia" in empty.metadata()
    segment = build_card("km:300", points, eq, cov, frames, manifest, years, positions)
    assert "7.091 de 11.178.995" in segment.evidencia
    assert segment.localizacao["precisao"] == KM_ONLY



def test_preventive_recurrence_requires_two_comparable_years_at_same_point(package):
    manifest, frames, _ = package
    points = frames["antt_equipamentos"]
    ids = ["VC101-6", "VC101-8"]
    years = [2024, 2025, 2026]
    positions = spatial_records(points, "ANTT", road())
    # Two complete years and one officially partial year for each point.
    dates = pd.date_range("2024-01-01", "2026-06-30")
    daily = pd.MultiIndex.from_product([ids, dates], names=["identificador", "data"]).to_frame(index=False)
    daily["ano"] = daily.data.dt.year
    daily["passagens"] = 100
    daily["altas"] = 0

    def card_with_counts(*records):
        example = daily.copy()
        for point, date in records:
            example.loc[example.identificador.eq(point) & example.data.eq(date), "altas"] = 1
        _, eq, cov = query_tables(example, points, ids, years, manifest["cobertura"]["trafego"])
        return build_card("cidade:Imbituba", points, eq, cov, frames, manifest, years, positions)

    isolated = ("VC101-6", "2024-05-01")
    partial = ("VC101-6", "2026-05-01")
    other_point = ("VC101-8", "2025-05-01")
    descriptive = card_with_counts(isolated, partial, other_point)
    assert descriptive.proximo_passo != CHECK_FIELD
    assert "não sustenta uma prioridade" in descriptive.motivo

    repeated = card_with_counts(isolated, ("VC101-6", "2025-05-01"), partial)
    assert repeated.proximo_passo == CHECK_FIELD
    assert "VC101-6 em 2024, 2025" in repeated.evidencia
    assert "exploratória" in repeated.cobertura
    assert "não sustentam uma prioridade operacional" in repeated.motivo


def test_entire_catalog_and_road_gaps(package):
    _, frames, _ = package
    devices, prf = frames["antt_equipamentos"], frames["ocorrencias"]
    cities = city_options(devices, prf)
    shapes = segment_shapes()
    for city in cities.values():
        assert lookup(city, devices, prf) == ("cidade", city)
    for km in range(245, 466, 5):
        result = lookup(f"km {min(km, 465)}", devices, prf)
        assert result == ("trecho", km)
    assert segment_for(462.3, shapes) == "460"
    assert segment_for(462.301, shapes) is None
    assert segment_for(301.5, {"300": {"ranges": [[300, 301], [302, 305]]}}) is None
    radar = spatial_records(devices, "ANTT", road())
    for row in radar.itertuples(index=False):
        assert lookup(row.codigo.lower(), devices, prf) == ("ponto", row.codigo)
        precision = location_precision(row, shapes)
        url, exact = google_maps_url(row.codigo, radar, cities)
        assert exact == (row.precisao == CHECKED)
        assert (precision == "marcador") == exact
        if not exact:
            assert pd.isna(row.latitude) and pd.isna(row.longitude)
            assert url is None or "BR-101" in url
        if precision == "trecho":
            assert segment_for(row.km, shapes)


def test_explanation_uses_the_facts_and_guidance_from_the_card(package):
    manifest, frames, _ = package
    points = frames["antt_equipamentos"]
    focus, years = "VC101-9", [2024, 2025]
    _, eq, cov = query_tables(frames["antt_diario"], points, [focus], years, manifest["cobertura"]["trafego"])
    card = build_card(focus, points, eq, cov, frames, manifest, years, spatial_records(points, "ANTT", road()))

    text = explain(card)
    assert "7.091" in text and "11.178.995" in text
    assert card.periodo in text and card.proximo_passo in text and card.cobertura in text
    assert text.index("**O que mais apareceu aqui.**") < text.index("**Cobertura.**")


def test_summary_preserves_separate_sources_years_and_passos_location_limit(package):
    manifest, frames, _ = package
    points = frames["antt_equipamentos"]
    positions = spatial_records(points, "ANTT", road())

    def card_at(focus, ids, years):
        _, eq, cov = query_tables(frames["antt_diario"], points, ids, years, manifest["cobertura"]["trafego"])
        return build_card(focus, points, eq, cov, frames, manifest, years, positions)

    trecho = card_at("km:330", ["VC101-11", "VC101-12"], [2024, 2025])
    antt, prf = trecho.dados["acidentes"]
    assert (antt["quantidade"], prf["quantidade"]) == (223, 172)
    assert [r["quantidade"] for r in prf["por_ano"]] == [93, 79]
    assert [r["quantidade"] for r in antt["por_ano"]] == [133, 90]
    assert prf["tipo"]["tipo"] == "Colisão transversal" and prf["tipo"]["quantidade"] == 43
    assert antt["tipo"]["estado"] == "campo ausente"
    assert prf["distribuicao_km"]["estado"] == antt["distribuicao_km"]["estado"] == "dispersos"
    assert "O que mais apareceu aqui" in trecho.markdown()
    assert trecho.markdown().index("Ocorrências nos anos") < trecho.markdown().index("Próximo passo")
    assert trecho.summary_markdown(compact=True).index("223 registros") < trecho.summary_markdown(compact=True).index("Próximo passo")
    partial = card_at("km:330", ["VC101-11", "VC101-12"], [2025, 2026])
    assert [r["quantidade"] for r in partial.dados["acidentes"][1]["por_ano"]] == [79, None]
    assert "(ano parcial)" in partial.summary_markdown() and "sem publicação" in partial.summary_markdown()
    for row in partial.dados["trafego"]["cobertura_por_ponto_ano"]:
        if row["ano"] == 2026:
            assert row["parcial"] and row["indice_por_10_mil"] is None
    passo = card_at("cidade:Passo de Torres", [], [2024, 2025])
    prf = passo.dados["acidentes"][0]
    assert prf["quantidade"] == 19 and passo.dados["trafego"] is None
    assert prf["distribuicao_km"]["sem_eixo"] == 6
    assert "5 registros entre os km 463 e 464" in passo.proximo_passo
    empty = card_at("cidade:Passo de Torres", [], [2022])
    assert "Sem publicação" in empty.summary_markdown() and "19 registros" not in empty.summary_markdown()
    zero = card_at("km:305", [], [2022])
    assert zero.dados["acidentes"][1]["quantidade"] is None


def test_geographic_rule_requires_a_majority_and_does_not_promote_bad_locations():
    from src.preventive import accident_next_step
    from src.preventive_summary import km_distribution, leading_type

    valid = {"330": {"ranges": [[330, 335]]}}
    base = pd.DataFrame({"km": [331.2] * 5 + [332.1, 332.2, 333.0], "ano": [2024, 2025] * 4})
    concentrated = km_distribution(base, valid)
    assert concentrated["estado"] == "concentrados"
    assert concentrated["quantidade"] == 5 and concentrated["anos"] == [2024, 2025]
    assert "331 e 332" in accident_next_step([{
        "fonte": "PRF", "quantidade": 8, "distribuicao_km": concentrated,
    }], 330)
    assert km_distribution(base.assign(km=[330.2] * 4 + [332.2] * 4), valid)["estado"] == "dispersos"
    assert km_distribution(base.assign(km=463), valid)["estado"] == "localização insuficiente"
    assert km_distribution(base.iloc[:4], valid)["estado"] == "poucos registros"
    assert leading_type(base.assign(tipo_acidente=["A"] * 4 + ["B"] * 4))["estado"] == "empate"
    assert leading_type(base.assign(tipo_acidente=["A"] * 7 + [None]))["estado"] == "campo incompleto"
