"""Regras locais de apoio preventivo compartilhadas entre tela e exportações."""
from dataclasses import asdict, dataclass

import pandas as pd

from src.antt import weighted_index
from src.corridor_map import segment_shapes
from src.preventive_summary import AccidentScope, accident_summary, accidents_text, annual_text, speed_text, traffic_years, years_text
from src.query import br, comparable_years, plain, point_label
from src.spatial import CHECKED, KM_ONLY, segment_label, segment_mask

RULE_VERSION = "apoio-preventivo-4"
CHECK_FIELD = (
    "Medir velocidades atuais no trecho e conferir em campo o limite aplicável, "
    "a sinalização e as condições da via."
)
INTERVENTIONS = (
    "Para avaliar fiscalização de velocidade, reúna medições recentes frente ao limite aplicável. "
    "Para avaliar blitz, documente um problema atual que essa abordagem possa enfrentar. "
    "Em ambos os casos, confirme a evidência em campo, compare alternativas e submeta a avaliação à autoridade competente."
)


@dataclass(frozen=True)
class Card:
    local: str
    periodo: str
    cobertura: str
    achado: str
    evidencia: str
    proximo_passo: str
    motivo: str
    falta: str
    responsavel: str
    reavaliar: str
    contexto: tuple
    localizacao: dict
    estado: str
    dados: dict

    def metadata(self):
        return {"regras": RULE_VERSION, **asdict(self)}

    @property
    def titulo_curto(self):
        return self.local.rsplit(" · ", 1)[0] if self.localizacao.get("codigo") else self.local

    @property
    def aviso_localizacao(self):
        return "" if self.localizacao["precisao"] == CHECKED else "Localização aproximada."

    def summary_markdown(self, compact=False):
        title = "**" + self.titulo_curto + "**" if compact else "## Ficha preventiva · " + self.titulo_curto
        return "\n\n".join(filter(None, [
            title, years_text(self.dados["anos_solicitados"]), self.aviso_localizacao,
            "#### O que mais apareceu aqui", *[accidents_text(source) for source in self.dados["acidentes"]],
            speed_text(self.dados["trafego"], self.estado),
            "#### Ocorrências nos anos selecionados", annual_text(self.dados, limit=5 if compact else None),
            "#### Próximo passo", self.proximo_passo,
        ]))

    def technical_markdown(self, include_annual=False):
        blocks = [
            ("Motivo", self.motivo), ("O que falta verificar", self.falta),
            ("Quem valida", self.responsavel), ("Quando reavaliar", self.reavaliar),
            ("Dias com dados de velocidade", self.cobertura),
            ("Localização", self.localizacao["precisao"] + ". " + self.localizacao["motivo_localizacao"]),
        ]
        if self.localizacao.get("codigo"):
            blocks.append(("Código do equipamento", self.localizacao["codigo"]))
        if self.localizacao.get("eixo"):
            blocks.append(("Traçado disponível", self.localizacao["eixo"]))
        if include_annual:
            blocks.append(("Série completa", annual_text(self.dados)))
        traffic = self.dados["trafego"]
        if traffic:
            days = "\n".join(
                f"- {row['ano']} · {row['ponto']} · {row['dias_publicados']}/{row['dias_calendario']} dias"
                for row in traffic["cobertura_por_ponto_ano"]
            )
            if days:
                blocks.append(("Dias publicados por equipamento e ano", "\n" + days))
        distribution = []
        for source in self.dados["acidentes"]:
            bands = source.get("distribuicao_km", {}).get("faixas", [])
            if bands:
                counts = " · ".join(f"km {b['km']}–{b['km'] + 1}: {br(b['publicados'])}" for b in bands)
                distribution.append(f"**{source['fonte']} · km publicado.** {counts}.")
        return "\n\n".join([
            *(f"**{title}.** {value}" for title, value in blocks),
            "#### Recortes e publicação de acidentes", *self.contexto, *distribution,
            f"Regras locais {RULE_VERSION}. Dados históricos.",
        ])

    def markdown(self):
        return self.summary_markdown() + "\n\n### Ver dados e fontes\n\n" + self.technical_markdown()


def local_sources(focus, points, frames, manifest):
    """Município PRF e trecho quilométrico ANTT/PRF têm escopos explícitos."""
    source = frames.get("ocorrencias")
    segment = None
    if focus.startswith("km:"):
        segment = int(focus[3:])
    elif not focus.startswith("cidade:"):
        point = points.loc[points.identificador.eq(focus)].iloc[0]
        segment = int(point.km // 5 * 5)
    if segment is None:
        city = focus[7:]
        city_records = None if source is None else source.loc[source.municipio.map(plain).eq(plain(city))]
        prf = AccidentScope("PRF", city_records, manifest["cobertura"]["prf"],
                            f"BR-101/SC no corredor, município informado pela PRF: {city}. Ambos os sentidos")
        return [prf], None
    scope = segment_label(segment) + ". Ambos os sentidos. Trecho de referência independente do radar"
    antt = frames["antt_acidentes"]
    km_records = antt.loc[segment_mask(antt.km, segment)]
    prf_records = None if source is None else source.loc[segment_mask(source.km, segment)]
    return [
        AccidentScope("ANTT", km_records, manifest["cobertura"]["antt"], scope),
        AccidentScope("PRF", prf_records, manifest["cobertura"]["prf"], scope),
    ], segment


def accident_next_step(sources, segment):
    # Use a defensible band from one source at a time. Prefer the PRF when both qualify.
    with_records = sorted((s for s in sources if s["quantidade"]), key=lambda s: s["fonte"] != "PRF")
    for source in with_records:
        distribution = source["distribuicao_km"]
        if distribution["estado"] == "concentrados":
            km = distribution["km"]
            return (f"Conferir em campo o trecho entre os km {km} e {km + 1}, onde a {source['fonte']} registrou "
                    f"{br(distribution['quantidade'])} ocorrências em {years_text(distribution['anos'])}.")
    for source in with_records:
        distribution = source["distribuicao_km"]
        if distribution["estado"] == "localização insuficiente":
            bands = [band for band in distribution["faixas"] if band["publicados"] > band["com_eixo"]]
            if bands:
                band = max(bands, key=lambda b: b["publicados"] - b["com_eixo"])
                count = band["publicados"] - band["com_eixo"]
                return (f"Confirmar com a {source['fonte']} a posição de {br(count)} registros entre os km "
                        f"{band['km']} e {band['km'] + 1}, antes de escolher um trecho para vistoria.")
            return f"Confirmar com a {source['fonte']} os km dos registros sem referência suficiente para escolher o trecho."
    if with_records:
        where = f" no trecho {segment_label(segment)}" if segment is not None else " neste município"
        return f"Revisar com a {with_records[0]['fonte']} os locais dos acidentes{where} antes de escolher uma faixa para vistoria."
    if any(source["quantidade"] == 0 for source in sources):
        return "Registrar o resultado da consulta e reavaliar com nova publicação ou informação do local."
    return "Conferir a cobertura com a fonte e reavaliar quando houver dados do local."


def build_card(focus, points, eq, cov, frames, manifest, years, positions, *, shapes=None):
    if not focus:
        return None
    shapes = segment_shapes() if shapes is None else shapes
    specs, segment = local_sources(focus, points, frames, manifest)
    sources, accidents = zip(*(accident_summary(spec, years, shapes) for spec in specs))
    context = tuple(
        (f"{s.fonte} — nenhum registro encontrado na base. {s.escopo}. {s.nota}"
         if s.quantidade == 0 else s.text())
        for s in sources
    )
    period = "Anos solicitados " + ", ".join(map(str, years))
    data = {"anos_solicitados": sorted(set(years)), "acidentes": list(accidents), "trafego": None}
    location = {"precisao": KM_ONLY, "motivo_localizacao":
                "A localização usa a referência publicada pela fonte. Ocorrências não são atribuídas a um equipamento."}
    if focus.startswith("cidade:"):
        scope = points.loc[points.municipio.map(plain).eq(plain(focus[7:]))]
        rows = eq.loc[eq.identificador.isin(scope.identificador)]
        directions = ", ".join(sorted(rows.sentido.dropna().unique())) or "sentido não informado"
        title = f"{focus[7:]} · BR-101/SC · {directions}"
        location["precisao"] = "Município informado pela PRF"
    elif focus.startswith("km:"):
        scope = points.loc[segment_mask(points.km, segment)]
        rows = eq.loc[eq.identificador.isin(scope.identificador)]
        title = segment_label(segment) + " · ambos os sentidos"
        shape = shapes.get(str(segment))
        location["eixo"] = ("; ".join(f"km {br(start, 3)} a {br(end, 3)}" for start, end in shape["ranges"])
                            if shape else "Sem geometria para este intervalo.")
    else:
        scope = points.loc[points.identificador.eq(focus)]
        rows = eq.loc[eq.identificador.eq(focus)]
        title = point_label(scope.iloc[0])
        position = positions.loc[positions.codigo.eq(focus)].iloc[0]
        location = {key: position[key] for key in ("precisao", "motivo_localizacao", "origem_coordenada")}
        if pd.notna(position.latitude):
            location.update(latitude=float(position.latitude), longitude=float(position.longitude))
        location["codigo"] = focus
        location["motivo_localizacao"] += ". Origem: " + location["origem_coordenada"]

    coverage_rows = cov.loc[cov.identificador.isin(scope.identificador)]
    annual = traffic_years(coverage_rows, scope)
    if annual:
        data["trafego"] = {"fonte": "ANTT, base A", "contagens": None, "acima_de_120": None,
                           "indice_por_10_mil": None, "cobertura_por_ponto_ano": annual}
    team = "Equipe técnica de segurança viária e responsável pelos dados do trecho."
    if rows.empty:
        published = [s for s in sources if s.quantidade]
        step = accident_next_step(accidents, segment)
        point_focus = not focus.startswith(("km:", "cidade:"))
        coverage = "Sem publicação de tráfego neste ponto e período." if point_focus else "Ficha territorial. Cobertura de acidentes por fonte abaixo."
        return Card(
            title, period, coverage, "A ficha não dispõe de contagens de velocidade para este local.",
            "Os registros de acidentes disponíveis estão descritos por fonte e recorte abaixo.",
            step,
            "A ausência de contagens deixa o padrão de velocidade em aberto.",
            "Dias de coleta, vigência dos registros e medições recentes do trecho. " + INTERVENTIONS,
            team, "Quando houver dados confirmados para o local e período.", context, location,
            "acidentes_sem_velocidade" if published else "sem_dados", data,
        )

    if len(rows) == 1:
        row = rows.iloc[0]
        coverage = " · ".join(f"{r.ano}: {r.dias}/{r.dias_calendario} dias publicados"
                              for r in coverage_rows.itertuples(index=False))
        days = f" em {br(row.dias)} dias publicados"
    else:
        coverage = (f"{len(rows)} pontos selecionados com publicação. Menor cobertura anual "
                    f"{br(coverage_rows.cobertura_dias.min() * 100, 1)}%. Consulte os dias por ponto no relatório.")
        days = ""
    high, total = rows.altas.sum(), rows.passagens.sum()
    evidence = (f"ANTT, base A. {br(high)} de {br(total)} contagens nas faixas acima de 120 km/h{days}. "
                f"Índice {br(weighted_index(high, total), 3)} por 10 mil.")
    annual_signal = coverage_rows.loc[comparable_years(coverage_rows) & coverage_rows.altas.gt(0)]
    years_per_point = annual_signal.groupby("identificador").ano.transform("nunique")
    recurring = annual_signal.loc[years_per_point.ge(2)]
    data["trafego"] = {
        "fonte": "ANTT, base A", "contagens": int(total), "acima_de_120": int(high),
        "indice_por_10_mil": float(weighted_index(high, total)) if total else None,
        "cobertura_por_ponto_ano": annual,
    }
    if not recurring.empty:
        state = "recorrente"
        years_by_point = [
            f"{point} em {', '.join(map(str, sorted(annual.ano)))}"
            for point, annual in recurring.groupby("identificador")
        ]
        evidence += " Contagens em anos comparáveis no mesmo ponto. " + " · ".join(years_by_point) + "."
        finding = "O sinal histórico se repete no mesmo ponto em anos comparáveis."
        step = CHECK_FIELD
        if location.get("codigo"):
            step = f"Medir velocidades atuais no km {br(scope.iloc[0].km, 3)} e conferir em campo o limite e a sinalização."
        reason = "A repetição orienta o que verificar em campo. Os dados históricos não sustentam uma prioridade operacional."
        if not rows.elegivel.all():
            coverage += " A comparação do recorte completo é exploratória. O sinal usa apenas os anos comparáveis de cada ponto."
    elif not rows.elegivel.all():
        state = "exploratorio"
        finding = "Resultado exploratório pela cobertura, denominador ou período incompleto."
        step = "Conferir os dias de coleta e obter dados que cubram o período necessário."
        reason = "A cobertura disponível limita a comparação anual. A base permite descrever o observado e não sustenta uma prioridade."
    elif high == 0:
        state = "zero_observado"
        finding = "Nenhuma contagem nas faixas acima de 120 km/h na base publicada deste recorte."
        step = "Se houver uma demanda atual, verificar as velocidades e o limite em campo."
        reason = "As faixas publicadas descrevem apenas o período observado."
    else:
        state = "isolado"
        finding = "Há contagens históricas acima de 120 km/h."
        if len(years) == 1:
            finding += " A seleção contém um único ano comparável."
        else:
            finding += " O sinal não se repetiu no mesmo ponto nos anos comparáveis selecionados."
        step = "Registrar o observado e reavaliar quando houver outros períodos comparáveis ou evidência atual do trecho."
        reason = "Os dados permitem descrever o observado e não sustentam uma prioridade de verificação em campo."
    if state == "recorrente":
        magnitudes = [
            f"{year}: {br(count)}" for year, count in recurring.groupby("ano").altas.sum().items()
        ]
        reason += " Contagens acima de 120 km/h nos pontos e anos que sustentam a repetição: " + " · ".join(magnitudes) + "."
    elif state == "exploratorio" and all(row["parcial"] for row in annual if row["contagens"] is not None):
        step = "Conferir quando termina a publicação do ano e reavaliar após completar o período."
    return Card(title, period, coverage, finding, evidence, step, reason, INTERVENTIONS, team,
                "Com dados recentes e a validação de campo do trecho e período.", context, location, state, data)
