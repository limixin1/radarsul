"""Explicação sob demanda. A IA escolhe uma apresentação dos fatos da ficha."""
from collections import OrderedDict, deque
from hashlib import sha256
import json
import os
from threading import Lock
from time import monotonic, perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MODELS = {"openai": "gpt-5.4-mini", "gemini": "gemini-3.1-flash-lite"}
KEYS = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
RATES = {"openai": (0.75, 4.50), "gemini": (0.25, 1.50)}  # USD por milhão de tokens
MAX_INPUT_BYTES = 12_000
MAX_OUTPUT_TOKENS = 256
TIMEOUT = 8
MAX_CALLS_PER_HOUR = 10
CACHE_TTL = 3600
MAX_CACHE = 128
FORMAT_VERSION = "explicacao-2"
LABELS = {
    "local": "Local e período",
    "observacao": "O que foi observado",
    "cobertura": "Cobertura",
    "fontes": "Registros por fonte",
    "precisao": "Como o local foi identificado",
    "verificacao": "O que vale verificar agora",
    "limites": "O que ainda precisa ser confirmado",
}
ORDERS = {
    "direto": ("observacao", "cobertura", "fontes"),
    "por_fontes": ("fontes", "observacao", "cobertura"),
    "por_cobertura": ("cobertura", "observacao", "fontes"),
}
OPENINGS = {
    "recorrente": ("O mesmo ponto teve contagens acima da faixa em mais de um ano comparável.",
                   "A repetição histórica ajuda a escolher o que medir hoje."),
    "isolado": ("O recorte permite descrever as contagens históricas.",
                "Para verificar se o sinal se repete, é preciso outro período comparável."),
    "exploratorio": ("Os dados disponíveis permitem descrever parte do período.",
                    "Confira os dias publicados antes de comparar anos."),
    "zero_observado": ("As faixas publicadas não registraram contagens acima de 120 km/h neste recorte.",
                       "A observação vale para o local e o período publicados."),
    "acidentes_sem_velocidade": ("Há registros de acidentes para consultar por fonte.",
                                "A checagem começa pelas ocorrências e pelos locais publicados."),
    "sem_dados": ("A consulta tem lacunas de publicação.",
                  "Confira a cobertura antes de interpretar o trecho."),
}
SCHEMA = {
    "type": "object",
    "properties": {
        "ordem": {"type": "string", "enum": list(ORDERS)},
        "abertura": {"type": "integer", "enum": [0, 1]},
        "estado": {"type": "string", "enum": list(OPENINGS)},
    },
    "required": ["ordem", "abertura", "estado"],
    "additionalProperties": False,
}

_lock = Lock()
_calls = deque()
_cache = OrderedDict()
_pending = set()


def facts(card):
    return {
        "local": card.local, "periodo": card.periodo, "estado": card.estado,
        "achado": card.achado, "evidencia": card.evidencia, "cobertura": card.cobertura,
        "dados": card.dados, "contexto_por_fonte": card.contexto,
        "localizacao": {k: v for k, v in card.localizacao.items() if k not in {"latitude", "longitude"}},
        "proximo_passo": card.proximo_passo, "motivo": card.motivo, "limites": card.falta,
        "quem_valida": card.responsavel, "aberturas_validadas": OPENINGS[card.estado],
    }


def compose(packet, order="direto", opening=None):
    location = packet["localizacao"]
    blocks = {
        "local": f"{packet['local']}. {packet['periodo']}.",
        "observacao": f"{packet['achado']} {packet['evidencia']}",
        "cobertura": packet["cobertura"],
        "fontes": "\n\n".join(packet["contexto_por_fonte"]),
        "precisao": f"{location['precisao']}. {location['motivo_localizacao']}",
        "verificacao": f"{packet['proximo_passo']} {packet['motivo']}",
        "limites": f"{packet['limites']} {packet['quem_valida']}",
    }
    sections = ["local", *ORDERS[order], "precisao", "verificacao", "limites"]
    paragraphs = [f"**{LABELS[key]}.** {blocks[key]}" for key in sections]
    if opening is not None:
        paragraphs.insert(0, packet["aberturas_validadas"][opening])
    return "\n\n".join(paragraphs)


def validate_response(raw, packet):
    result = json.loads(raw)
    if (not isinstance(result, dict) or set(result) != set(SCHEMA["required"])
            or not isinstance(result["ordem"], str) or result["ordem"] not in ORDERS
            or type(result["abertura"]) is not int or result["abertura"] not in (0, 1)
            or result["estado"] != packet["estado"]):
        raise ValueError("Resposta fora dos fatos da ficha.")
    return result


def provider_block(provider):
    if provider not in MODELS:
        return "provedor externo não selecionado"
    if not os.environ.get(KEYS[provider]):
        return f"{KEYS[provider]} ausente"
    if os.environ.get("SENTINELA_ENABLE_PAID_AI") != "1":
        return "opt-in de IA externa ausente"
    return None


def make_prompt(packet):
    return (
        "Organize uma explicação em português simples. Escolha uma das duas aberturas autorizadas "
        "pelo índice 0 ou 1 e uma ordem: direto para velocidade, por_fontes para acidentes, "
        "por_cobertura quando a limitação for a informação principal. Repita o estado recebido. "
        "Responda apenas com ordem, abertura e estado. O servidor exibe os fatos e o próximo passo.\n"
        + json.dumps(packet, ensure_ascii=False, allow_nan=False)
    )


def request_presentation(provider, prompt):
    model = MODELS[provider]
    key = os.environ[KEYS[provider]]
    if provider == "openai":
        endpoint = "https://api.openai.com/v1/responses"
        headers = {"Authorization": "Bearer " + key}
        body = {"model": model, "input": prompt, "store": False, "max_output_tokens": MAX_OUTPUT_TOKENS,
                "reasoning": {"effort": "none"}, "text": {"format": {
                    "type": "json_schema", "name": "explicacao", "strict": True, "schema": SCHEMA,
                }}}
    else:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {"x-goog-api-key": key}
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": MAX_OUTPUT_TOKENS, "responseMimeType": "application/json",
                                     "responseJsonSchema": SCHEMA}}
    request = Request(endpoint, json.dumps(body, ensure_ascii=False).encode(),
                      {"Content-Type": "application/json", **headers}, method="POST")
    with urlopen(request, timeout=TIMEOUT) as response:
        payload = json.loads(response.read(65536))
    if provider == "openai":
        text = "".join(part["text"] for item in payload["output"] if item["type"] == "message"
                       for part in item["content"] if part["type"] == "output_text")
        usage = payload.get("usage", {})
        return text, usage.get("input_tokens"), usage.get("output_tokens")
    text = "".join(part.get("text", "") for part in payload["candidates"][0]["content"]["parts"]
                   if not part.get("thought"))
    usage = payload.get("usageMetadata", {})
    output = usage.get("candidatesTokenCount")
    return text, usage.get("promptTokenCount"), None if output is None else output + usage.get("thoughtsTokenCount", 0)


def estimate_cost(provider, input_tokens, output_tokens):
    rate_in, rate_out = RATES[provider]
    return (rate_in * input_tokens + rate_out * output_tokens) / 1_000_000


def _remote(provider, prompt, packet, version, query, result):
    key = (version, FORMAT_VERSION, MODELS[provider], query, sha256(prompt.encode()).hexdigest())
    now = monotonic()
    with _lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < CACHE_TTL:
            _cache.move_to_end(key)
            return {**cached[1], "cache": True}
        if key in _pending:
            return {**result, "reason": "explicação em andamento em outra sessão"}
        while _calls and now - _calls[0] >= 3600:
            _calls.popleft()
        if len(_calls) >= MAX_CALLS_PER_HOUR:
            return {**result, "reason": "limite horário da instância atingido"}
        _calls.append(now)
        _pending.add(key)

    result = dict(result)
    start = perf_counter()
    try:
        raw, result["input_tokens"], result["output_tokens"] = request_presentation(provider, prompt)
        choice = validate_response(raw, packet)
        result.update(text=compose(packet, choice["ordem"], choice["abertura"]),
                      status="validado", apresentacao=choice)
    except HTTPError as exc:
        result["reason"] = "cota ou limite da API" if exc.code == 429 else "API indisponível"
    except (OSError, ValueError, TypeError, AttributeError, KeyError, IndexError):
        result["reason"] = "API indisponível ou resposta fora dos fatos da ficha"
    finally:
        result["provider_latency_ms"] = round((perf_counter() - start) * 1000, 3)
        with _lock:
            _pending.remove(key)
            _cache[key] = (monotonic(), result)
            _cache.move_to_end(key)
            if len(_cache) > MAX_CACHE:
                _cache.popitem(last=False)
    return result


def explain(card, provider="local", *, version="", query=""):
    start = perf_counter()
    packet = facts(card)
    result = {"text": compose(packet), "status": "local", "provider": provider,
              "input_tokens": None, "output_tokens": None, "cache": False}
    if provider != "local":
        result["status"] = "fallback"
        blocked = provider_block(provider)
        if blocked:
            result["reason"] = blocked
        else:
            prompt = make_prompt(packet)
            if len(prompt.encode()) > MAX_INPUT_BYTES:
                result["reason"] = "recorte acima do limite de entrada"
            else:
                result = _remote(provider, prompt, packet, version, query, result)
    return {**result, "latency_ms": round((perf_counter() - start) * 1000, 3)}


def render_explanation(card, version, query):
    import streamlit as st

    provider = os.environ.get("SENTINELA_AI_PROVIDER", "local")
    if st.button("Explique este trecho", key="explain_focus"):
        result = explain(card, provider, version=version, query=query)
        st.session_state["map_explanation"] = (version, query, card, result)
    previous = st.session_state.get("map_explanation")
    if previous and previous[:3] == (version, query, card):
        result = previous[3]
        if result["status"] == "validado":
            st.caption(f"Apresentação sugerida por {MODELS[result['provider']]}. Os fatos vêm da ficha.")
        else:
            st.caption("Explicação local, com base na ficha e nas regras do painel.")
        st.markdown(result["text"])
