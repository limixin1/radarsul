"""Compara a mesma evidência em cinco casos, sem rede por padrão."""
import argparse
from decimal import Decimal
import json

from src.data_package import token, validate
from src.explain import (
    MAX_INPUT_BYTES, MAX_OUTPUT_TOKENS, MODELS, estimate_cost, explain, facts, make_prompt, provider_block,
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


def compare(live=False, approved_max_usd=None):
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
    # Usa bytes UTF-8 como estimativa conservadora de tokens de entrada, mais margem
    # para instruções do provedor e schema. Não é um teto do faturamento do projeto.
    ceiling = sum(
        estimate_cost(provider, len(make_prompt(facts(card)).encode()) + 1024, MAX_OUTPUT_TOKENS)
        for provider in MODELS for _, _, _, card in cases
    )
    ceiling = round(ceiling + 0.000001, 6)
    plan = {"modelos": MODELS, "chamadas_maximas": len(MODELS) * len(cases),
            "saida_maxima_por_chamada_tokens": MAX_OUTPUT_TOKENS, "teto_planejado_usd": ceiling}
    if live:
        if approved_max_usd is None or not approved_max_usd.is_finite() or approved_max_usd < Decimal(str(ceiling)):
            raise ValueError(f"A execução exige teto aprovado de pelo menos US$ {ceiling:.6f}.")
        blocked = [reason for provider in MODELS if (reason := provider_block(provider))]
        if blocked:
            raise ValueError("Comparação real indisponível. " + "; ".join(blocked))
        if any(len(make_prompt(facts(card)).encode()) > MAX_INPUT_BYTES for _, _, _, card in cases):
            raise ValueError("Pelo menos um caso excede o limite de entrada.")
    results = []
    for title, focus, years, card in cases:
        local = explain(card)
        local["cost_usd"] = 0
        record = {"caso": title, "foco": focus, "anos": years, "estado": card.estado, "local": local}
        for provider, model in MODELS.items():
            if live:
                result = explain(card, provider, version=version, query=focus)
                count_in, count_out = result["input_tokens"], result["output_tokens"]
                result["cost_usd_estimated"] = (
                    round(estimate_cost(provider, count_in, count_out), 8)
                    if count_in is not None and count_out is not None else None
                )
            else:
                result = {"status": "não executado", "reason": provider_block(provider) or "execute com --live",
                          "text": None, "latency_ms": None, "cost_usd_estimated": None}
            record[provider] = {"model": model, **result}
        results.append(record)
    return {"snapshot": manifest["versao"], "plano": plan, "casos": results}


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Consulta as duas APIs quando autorizado.")
    parser.add_argument("--approved-max-usd", type=Decimal, help="Teto explícito da rodada autorizada.")
    parser.add_argument("--markdown", action="store_true", help="Emite as cinco respostas lado a lado.")
    args = parser.parse_args()
    try:
        result = compare(args.live, args.approved_max_usd)
    except ValueError as exc:
        parser.error(str(exc))
    print(markdown(result) if args.markdown else json.dumps(result, ensure_ascii=False, indent=2))
