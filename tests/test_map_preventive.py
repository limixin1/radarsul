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


def test_explanation_checks_facts_caches_and_keeps_a_local_fallback(package, monkeypatch):
    import src.explain as module

    manifest, frames, _ = package
    points = frames["antt_equipamentos"]
    focus, years = "VC101-9", [2024, 2025]
    _, eq, cov = query_tables(frames["antt_diario"], points, [focus], years, manifest["cobertura"]["trafego"])
    card = build_card(focus, points, eq, cov, frames, manifest, years, spatial_records(points, "ANTT", road()))
    local = explain(card)["text"]
    packet = module.facts(card)
    assert packet["dados"]["trafego"]["acima_de_120"] == 7091
    assert "latitude" not in packet["localizacao"]
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert explain(card, "openai")["text"] == local
    monkeypatch.setenv("OPENAI_API_KEY", "key-for-mock")
    monkeypatch.setenv("GEMINI_API_KEY", "key-for-mock")
    monkeypatch.setenv("SENTINELA_ENABLE_PAID_AI", "1")
    for index, raw in enumerate((
        '{"ordem":"direto","abertura":0,"estado":"recorrente","numeros":"99.999 em 2026"}',
        '{"ordem":"direto","abertura":0,"estado":"recorrente","acao":"Realizar blitz agora"}',
        '{"ordem":"por_fontes","abertura":1,"estado":"sem_dados"}',
        'texto livre',
    )):
        monkeypatch.setattr(module, "request_presentation", lambda *_: (raw, 500, 12))
        result = explain(card, "openai", version="teste", query=f"invalido-{index}")
        assert result["status"] == "fallback" and result["text"] == local

    calls = []

    def valid(provider, prompt):
        calls.append((provider, prompt))
        return '{"ordem":"por_cobertura","abertura":1,"estado":"recorrente"}', 500, 12

    monkeypatch.setattr(module, "request_presentation", valid)
    first = explain(card, "openai", version="teste-v1", query=focus)
    repeat = explain(card, "openai", version="teste-v1", query=focus)
    updated = explain(card, "openai", version="teste-v2", query=focus)
    gemini = explain(card, "gemini", version="teste-v2", query=focus)
    assert [row["status"] for row in (first, repeat, updated, gemini)] == ["validado"] * 4
    assert repeat["cache"] and len(calls) == 3 and calls[1][1] == calls[2][1]
    assert set(first["text"].split("\n\n")[1:]) == set(local.split("\n\n"))
    assert first["text"].index("**Cobertura.**") < first["text"].index("**O que foi observado.**")
    monkeypatch.setattr(module, "MAX_CALLS_PER_HOUR", 0)
    capped = explain(card, "gemini", version="teste-v3", query=focus)
    assert capped["text"] == local and "limite horário" in capped["reason"]
