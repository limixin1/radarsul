"""Compara a mesma evidência em cinco casos, sem rede por padrão."""
import argparse
from decimal import Decimal
import json

from src.data_package import token, validate
from src.explain import (
    MAX_INPUT_BYTES, MAX_OUTPUT_TOKENS, MODELS, SCHEMA, SYSTEM_PROMPT, estimate_cost, explain, facts, make_prompt, provider_block,
)
from src.preventive import build_card
from src.query import query_tables
from src.spatial import road, spatial_records

CASES = (
    ("Velocidade recorrente", "VC101-9", ("VC101-9",), [2024, 2025], "recorrente"),
    ("Registro isolado", "VC101-9", ("VC101-9",), [2024], "isolado"),
    ("Ano parcial", "VC101-9", ("VC101-9",), [2026], "exploratorio"),
    ("Acidentes em município sem radar", "cidade:Passo de Torres", (), [2024, 2025], "acidentes_sem_velocidade"),
    ("Recorte sem dados publicados", "cidade:Passo de Torres", (), [2022], "sem_dados"),
)


def compare(live=False, approved_max_usd=None, provider="both"):
    return evaluate(load_cases(), live=live, approved_max_usd=approved_max_usd, provider=provider)


def load_cases():
    manifest, frames, _ = validate()
    points = frames["antt_equipamentos"]
    positions = spatial_records(points, "ANTT", road())
    version = token()
    cases = []
    for title, focus, ids, years, expected in CASES:
        _, eq, coverage = query_tables(frames["antt_diario"], points, ids, years, manifest["cobertura"]["trafego"])
        card = build_card(focus, points, eq, coverage, frames, manifest, years, positions)
        if card.estado != expected:
            raise ValueError(f"Caso {title} mudou de estado. Revise a evidência antes de comparar.")
        cases.append((title, focus, years, card))
    return manifest["versao"], version, cases


def evaluate(loaded, *, live, approved_max_usd, provider):
    snapshot, version, cases = loaded
    providers = list(MODELS) if provider == "both" else [provider]
    free_tier = provider == "gemini"
    ceiling = 0
    if not free_tier:
        ceiling = sum(
            estimate_cost(name, len((SYSTEM_PROMPT + make_prompt(facts(card))).encode()) + 1024, MAX_OUTPUT_TOKENS)
            for name in providers for _, _, _, card in cases
        )
        ceiling = round(ceiling + 0.000001, 6)
        if live and (approved_max_usd is None or not approved_max_usd.is_finite()
                     or approved_max_usd < Decimal(str(ceiling))):
            raise ValueError(f"A execução exige teto aprovado de pelo menos US$ {ceiling:.6f}.")
    plan = {"modelos": {name: MODELS[name] for name in providers}, "modo": "free_tier" if free_tier else "pago",
            "chamadas_maximas": len(providers) * len(cases), "chamadas_realizadas": 0,
            "saida_maxima_por_chamada_tokens": MAX_OUTPUT_TOKENS, "teto_planejado_usd": ceiling}
    blocked = {name: provider_block(name, free_tier=free_tier) for name in providers}
    results = []
    for title, focus, years, card in cases:
        local = explain(card)
        local["cost_usd"] = 0
        record = {"caso": title, "foco": focus, "anos": years, "estado": card.estado, "local": local}
        for name, model in MODELS.items():
            if live and name in providers and not blocked[name]:
                result = explain(card, name, version=version, query=focus, free_tier=free_tier)
                plan["chamadas_realizadas"] += result["chamadas"]
                if result.get("reason") == "cota ou limite da API":
                    blocked[name] = "rodada interrompida após erro de cota ou limite da API"
                count_in, count_out = result["input_tokens"], result["output_tokens"]
                result["cost_usd_estimated"] = (
                    0 if free_tier and result["chamadas"] else
                    round(estimate_cost(name, count_in, count_out), 8)
                    if count_in is not None and count_out is not None else None
                )
            else:
                reason = (blocked[name] or "execute com --live") if name in providers else "provedor fora desta rodada"
                result = {"status": "não executado", "reason": reason, "chamadas": 0,
                          "text": None, "latency_ms": None, "cost_usd_estimated": None}
            record[name] = {"model": model, **result}
        results.append(record)
    return {"snapshot": snapshot, "plano": plan, "casos": results}


def manual_packets(loaded):
    snapshot, _, cases = loaded
    return {"snapshot": snapshot, "instrucoes": SYSTEM_PROMPT, "esquema": SCHEMA, "casos": [
        {"caso": title, "fatos": facts(card)} for title, _, _, card in cases
    ]}


def markdown(result):
    lines = [
        "| Caso | Texto local | GPT | Gemini |",
        "|---|---|---|---|",
    ]
    for case in result["casos"]:
        cells = [case["caso"]]
        for provider in ("local", "openai", "gemini"):
            row = case[provider]
            if row["status"] in ("local", "validado"):
                text = row["text"]
            else:
                text = row["status"] + ". " + row["reason"]
            cells.append(text.replace("|", "\\|").replace("\n", "<br>"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("both", "gemini", "openai"), default="both",
                        help="Gemini isolado só usa projeto confirmado no Free Tier.")
    parser.add_argument("--live", action="store_true", help="Consulta o provedor selecionado quando autorizado.")
    parser.add_argument("--manual", action="store_true", help="Emite fatos públicos e instruções para ChatGPT ou Claude.")
    parser.add_argument("--approved-max-usd", type=Decimal, help="Teto explícito da rodada autorizada.")
    parser.add_argument("--markdown", action="store_true", help="Emite as cinco respostas lado a lado.")
    args = parser.parse_args()
    try:
        if args.manual:
            if args.live or args.markdown:
                parser.error("--manual gera apenas JSON local.")
            print(json.dumps(manual_packets(load_cases()), ensure_ascii=False, indent=2))
            return
        result = compare(args.live, args.approved_max_usd, args.provider)
    except ValueError as exc:
        parser.error(str(exc))
    print(markdown(result) if args.markdown else json.dumps(result, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    main()
