"""Regras locais de apoio preventivo compartilhadas entre tela e exportações."""
from dataclasses import asdict, dataclass

import pandas as pd

from src.antt import weighted_index
from src.query import br, plain, point_label, source_result
from src.spatial import KM_ONLY, segment_label, segment_mask

RULE_VERSION = "apoio-preventivo-1"
CHECK_FIELD = (
    "Medir velocidades atuais no trecho e conferir em campo o limite aplicável, "
    "a sinalização e as condições da via."
)
INTERVENTIONS = (
    "Para avaliar fiscalização de velocidade, reúna medições recentes frente ao limite aplicável. "
    "Para avaliar blitz, documente um problema atual que essa abordagem possa enfrentar. "
    "Em ambos os casos, compare alternativas e submeta a avaliação à autoridade competente."
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

    def metadata(self):
        return {"regras": RULE_VERSION, **asdict(self)}

    def markdown(self):
        blocks = [
            ("Próximo passo", self.proximo_passo), ("Motivo", self.motivo),
            ("O que falta verificar", self.falta), ("Quem valida", self.responsavel),
            ("Quando reavaliar", self.reavaliar), ("Período e cobertura", f"{self.periodo}. {self.cobertura}"),
            ("Achado", self.achado), ("Evidência", self.evidencia),
            ("Localização", self.localizacao["precisao"] + ". " + self.localizacao["motivo_localizacao"]),
        ]
        return "\n\n".join([
            f"## Ficha preventiva · {self.local}",
            *(f"**{title}.** {value}" for title, value in blocks),
            "### Registros de acidentes no recorte indicado",
            *self.contexto, f"Regras locais {RULE_VERSION}. Dados históricos.",
        ])


def local_sources(focus, points, frames, manifest, years):
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
        prf = source_result("PRF", city_records, years, manifest["cobertura"]["prf"],
                            f"BR-101/SC no corredor, município informado pela PRF: {city}. Ambos os sentidos")
        return [prf], None
    scope = segment_label(segment) + ". Ambos os sentidos. Trecho de referência independente do radar"
    antt = frames["antt_acidentes"]
    km_records = antt.loc[segment_mask(antt.km, segment)]
    prf_records = None if source is None else source.loc[segment_mask(source.km, segment)]
    return [
        source_result("ANTT", km_records, years, manifest["cobertura"]["antt"], scope),
        source_result("PRF", prf_records, years, manifest["cobertura"]["prf"], scope),
    ], segment


def build_card(focus, points, eq, cov, frames, manifest, years, positions):
    if not focus:
        return None
    sources, segment = local_sources(focus, points, frames, manifest, years)
    context = tuple(
        (f"{s.fonte} — nenhum registro encontrado na base. {s.escopo}. {s.nota}"
         if s.quantidade == 0 else s.text())
        for s in sources
    )
    period = "Anos solicitados " + ", ".join(map(str, years))
    location = {"precisao": KM_ONLY, "motivo_localizacao":
                "A localização usa a referência publicada pela fonte. Ocorrências não são atribuídas a um equipamento."}
    if focus.startswith("cidade:"):
        rows = eq.loc[eq.municipio.map(plain).eq(plain(focus[7:]))]
        directions = ", ".join(sorted(rows.sentido.dropna().unique())) or "sentido não informado"
        title = f"{focus[7:]} · BR-101/SC · {directions}"
        location["precisao"] = "Município informado pela PRF"
    elif focus.startswith("km:"):
        rows = eq.loc[segment_mask(eq.km, segment)]
        title = segment_label(segment) + " · ambos os sentidos"
    else:
        rows = eq.loc[eq.identificador.eq(focus)]
        title = point_label(points.loc[points.identificador.eq(focus)].iloc[0])
        position = positions.loc[positions.codigo.eq(focus)].iloc[0]
        location = {key: position[key] for key in ("precisao", "motivo_localizacao", "origem_coordenada")}
        if pd.notna(position.latitude):
            location.update(latitude=float(position.latitude), longitude=float(position.longitude))
        location["motivo_localizacao"] += ". Origem: " + location["origem_coordenada"]

    team = "Equipe técnica de segurança viária e responsável pelos dados do trecho."
    if rows.empty:
        published = [s for s in sources if s.quantidade]
        if published:
            step = ("Revisar ocorrências e gravidade por fonte e conferir os locais em campo. "
                    "Obter medições do trecho se a decisão depender de velocidades.")
        else:
            step = "Conferir a cobertura com a fonte e obter medições do local, se a decisão depender de velocidades."
        point_focus = not focus.startswith(("km:", "cidade:"))
        coverage = "Sem publicação de tráfego neste ponto e período." if point_focus else "Ficha territorial. Cobertura de acidentes por fonte abaixo."
        return Card(
            title, period, coverage, "A ficha não dispõe de contagens de velocidade para este local.",
            "Os registros de acidentes disponíveis estão descritos por fonte e recorte abaixo.",
            step,
            "A ausência de contagens deixa o padrão de velocidade em aberto.",
            "Dias de coleta, vigência dos registros e medições recentes do trecho.",
            team, "Quando houver dados confirmados para o local e período.", context, location,
        )

    coverage_rows = cov.loc[cov.identificador.isin(rows.identificador)]
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
    if not rows.elegivel.all():
        finding = "Resultado exploratório pela cobertura, denominador ou período incompleto."
        step = "Conferir os dias de coleta e obter dados que cubram o período necessário."
        reason = "A cobertura disponível limita a comparação anual."
        gap = "Confirmar coleta e publicação com a fonte. Para avaliar medidas, obter evidência atual do trecho."
    elif high == 0:
        finding = "Nenhuma contagem nas faixas acima de 120 km/h na base publicada deste recorte."
        step = "Se houver uma demanda atual, verificar as velocidades e o limite em campo."
        reason = "As faixas publicadas descrevem apenas o período observado."
        gap = INTERVENTIONS
    else:
        finding = "Há contagens históricas nas faixas acima de 120 km/h."
        step = CHECK_FIELD
        reason = "A faixa publicada permite investigar um padrão histórico. Infrações dependem do limite regulamentado e das condições do trecho."
        gap = INTERVENTIONS
    return Card(title, period, coverage, finding, evidence, step, reason, gap, team,
                "Com dados recentes e a validação de campo do trecho e período.", context, location)
