"""Apresentação verificável das ocorrências e das séries da ficha."""
from collections import Counter
from math import floor, isfinite
from typing import NamedTuple

import pandas as pd

from src.corridor_map import segment_for
from src.query import br, comparable_years, plain, source_result

MIN_RECORDS = 5


class AccidentScope(NamedTuple):
    name: str
    rows: pd.DataFrame | None
    coverage: dict
    scope: str


def leading_type(rows):
    if "tipo_acidente" not in rows:
        return {"estado": "campo ausente"}
    types = rows.tipo_acidente.dropna().astype(str).str.strip()
    types = types.loc[~types.map(plain).isin({"", "ignorado", "nao informado", "indisponivel", "null", "nan"})]
    if len(types) != len(rows):
        return {"estado": "campo incompleto"}
    if len(types) < MIN_RECORDS:
        return {"estado": "poucos registros"}
    ranking = types.value_counts()
    first, second = int(ranking.iloc[0]), int(ranking.iloc[1]) if len(ranking) > 1 else 0
    if first - second < 2:
        return {"estado": "empate" if first == second else "frequências próximas"}
    return {"estado": "destaque", "tipo": str(ranking.index[0]), "quantidade": first, "segundo": second}


def km_distribution(rows, shapes):
    """Faixas disjuntas de 1 km. Só sugere checagem quando a maioria tem referência defensável."""
    observed, mapped = Counter(), Counter()
    years = {}
    for row in rows.itertuples(index=False):
        if pd.isna(row.km) or not isfinite(row.km):
            continue
        bucket = floor(row.km)
        observed[bucket] += 1
        if segment_for(row.km, shapes) is not None:
            mapped[bucket] += 1
            years.setdefault(bucket, set()).add(int(row.ano))
    missing = len(rows) - sum(mapped.values())
    bins = [{"km": km, "publicados": count, "com_eixo": mapped[km]} for km, count in sorted(observed.items())]
    if not len(rows):
        return {"estado": "sem registros", "sem_eixo": 0, "faixas": bins}
    if mapped:
        km, count = mapped.most_common(1)[0]
        if count >= MIN_RECORDS and count * 2 > len(rows):
            return {"estado": "concentrados", "km": km, "quantidade": count, "anos": sorted(years[km]),
                    "sem_eixo": missing, "faixas": bins}
    state = "localização insuficiente" if missing else ("poucos registros" if len(rows) < MIN_RECORDS else "dispersos")
    return {"estado": state, "sem_eixo": missing, "faixas": bins}


def accident_summary(spec, years, shapes):
    total = source_result(spec.name, spec.rows, years, spec.coverage, spec.scope)
    covered = None if spec.rows is None else spec.rows.loc[spec.rows.ano.isin(total.anos_cobertos)]
    annual = []
    for year in total.anos_solicitados:
        result = source_result(spec.name, spec.rows, [year], spec.coverage, spec.scope)
        entry = result.to_dict()
        if result.quantidade:
            year_rows = covered.loc[covered.ano.eq(year)]
            entry["tipo"] = leading_type(year_rows)
            entry["sem_eixo"] = km_distribution(year_rows, shapes)["sem_eixo"]
        annual.append(entry)
    data = total.to_dict()
    data["por_ano"] = annual
    if covered is not None and len(covered):
        data["tipo"] = leading_type(covered)
        data["distribuicao_km"] = km_distribution(covered, shapes)
    return total, data


def traffic_years(cov, points):
    labels = points.set_index("identificador")
    annual = []
    for row in cov.assign(comparavel=comparable_years(cov)).sort_values(["ano", "identificador"]).itertuples(index=False):
        point = labels.loc[row.identificador]
        available = pd.notna(row.passagens)
        annual.append({
            "ponto": row.identificador, "ano": int(row.ano), "km": float(point.km), "sentido": point.sentido,
            "dias_publicados": int(row.dias), "dias_calendario": int(row.dias_calendario),
            "contagens": int(row.passagens) if available else None,
            "acima_de_120": int(row.altas) if available else None,
            "indice_por_10_mil": float(row.por_10_mil) if row.comparavel else None,
            "parcial": 0 < row.dias_intervalo < row.dias_calendario, "comparavel": bool(row.comparavel),
        })
    return annual


def years_text(years):
    return ", ".join(map(str, years))


def accidents_text(source):
    count, name = source["quantidade"], source["fonte"]
    scope = source["escopo"].split(". ", 1)[0]
    area = (f"no trecho {scope} (ambos os sentidos)" if "km " in scope
            else "no município informado (ambos os sentidos)")
    if count is None:
        return f"**{name}** · Sem publicação para esta consulta." if source["situacao"] != "fonte indisponível" else f"**{name}** · Fonte indisponível."
    years = years_text(source["anos_cobertos"])
    if count == 0:
        return f"**{name}** · Nenhum registro de acidente encontrado na base em {years}, {area}."
    noun = "registro de acidente" if count == 1 else "registros de acidente"
    message = f"**{name}** · {br(count)} {noun} em {years}, {area}."
    type_info = source["tipo"]
    if type_info["estado"] == "destaque":
        message += f" Tipo mais registrado: {type_info['tipo'].lower()} ({br(type_info['quantidade'])} de {br(count)})."
    else:
        explanations = {
            "campo ausente": "A fonte não publica o tipo.",
            "campo incompleto": "Há registros sem tipo informado.",
            "poucos registros": "Poucos registros para destacar um tipo.",
            "empate": "Os tipos mais registrados estão empatados.",
            "frequências próximas": "Os tipos mais registrados têm frequências próximas.",
        }
        message += " " + explanations[type_info["estado"]]
    distribution = source["distribuicao_km"]
    if distribution["estado"] == "concentrados":
        km = distribution["km"]
        message += (f" Entre os km {km} e {km + 1}, foram {br(distribution['quantidade'])} de {br(count)} "
                    f"em {years_text(distribution['anos'])}.")
    elif distribution["estado"] == "dispersos":
        message += " Os registros se distribuem pelo trecho; nenhuma faixa de 1 km reuniu a maioria."
    elif distribution["estado"] == "localização insuficiente":
        missing = distribution["sem_eixo"]
        message += f" {br(missing)} sem referência por km no eixo disponível; a distribuição não sustenta apontar uma faixa."
    else:
        message += " Poucos registros para destacar uma faixa."
    return message


def speed_text(traffic, state):
    if not traffic or traffic["contagens"] is None:
        return "Sem contagens de velocidade dos equipamentos neste recorte."
    if traffic["contagens"] == 0:
        return "**Velocidade · ANTT, base A.** O total publicado é zero. Falta base para calcular o índice."
    count = br(traffic["acima_de_120"])
    total = br(traffic["contagens"])
    text = f"**Velocidade · ANTT, base A.** {count} de {total} contagens ficaram nas faixas acima de 120 km/h."
    if state == "recorrente":
        points = {row["ponto"] for row in traffic["cobertura_por_ponto_ano"] if row["contagens"] is not None}
        if len(points) == 1:
            text += " O ponto registrou contagens nessa faixa em mais de um ano com dados suficientes para comparação."
        else:
            text += " A repetição foi verificada por equipamento, em anos com dados suficientes para comparação."
    elif state == "isolado":
        text += " Os dados permitem descrever o observado sem indicar repetição."
    elif state == "exploratorio":
        text += " A publicação disponível limita a comparação entre anos."
    return text + " A faixa publicada, sozinha, não identifica uma infração."


def annual_text(data, limit=None):
    lines = []
    for year in data["anos_solicitados"]:
        entries = []
        for source in data["acidentes"]:
            annual = next(row for row in source["por_ano"] if row["anos_solicitados"] == [year])
            number = annual["quantidade"]
            if number is None:
                value = "fonte indisponível" if annual["situacao"] == "fonte indisponível" else "sem publicação"
            elif number == 0:
                value = "nenhum registro de acidente na base"
            else:
                value = f"{br(number)} {'registro de acidente' if number == 1 else 'registros de acidente'}"
            if annual["situacao"] == "cobertura parcial":
                value += " (ano parcial)"
            kind = annual.get("tipo", {})
            if kind.get("estado") == "destaque":
                value += f" · {kind['tipo'].lower()} ({br(kind['quantidade'])})"
            if annual.get("sem_eixo"):
                value += f" · {br(annual['sem_eixo'])} sem referência no eixo"
            entries.append(f"**{source['fonte']}** · {value}")
        traffic = data["trafego"]
        for point in traffic["cobertura_por_ponto_ano"] if traffic else []:
            if point["ano"] != year:
                continue
            total = point["contagens"]
            value = "sem publicação de velocidade" if total is None else (
                f"{br(point['acima_de_120'])} acima de 120 km/h de {br(total)} contagens"
            )
            if point["comparavel"]:
                value += f" · {br(point['indice_por_10_mil'], 3)} por 10 mil"
            elif point["parcial"]:
                value += " (ano parcial)"
            elif total is not None:
                value += " (sem total positivo para calcular o índice)" if total == 0 else " (dias insuficientes para comparar)"
            entries.append(f"**Velocidade · km {br(point['km'], 3)} · {point['sentido']}** · {value}")
        if limit is not None and len(entries) > limit:
            entries = entries[:limit] + ["Mais pontos em Ver dados e fontes."]
        lines.append(f"**{year}**\n" + "\n".join(f"- {entry}" for entry in entries))
    return "\n\n".join(lines)
