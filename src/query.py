"""Consultas puras: seleção, cobertura declarada e apresentação pt-BR."""
import calendar
from dataclasses import dataclass, asdict
import math
import unicodedata
import pandas as pd
from src.antt import annual_table, equipment_table

PAGES = ['Visão geral', 'Comparador de equipamentos', 'Evolução e persistência', 'Contexto rodoviário', 'Relatório preventivo']
AREAS = ['Grupo com boa cobertura em 2024–2025', 'Todos os equipamentos', 'Criciúma: VC101-30', 'Entorno de Criciúma: km 370 a 410']
YEARS = [2022, 2023, 2024, 2025, 2026]
DIRECTIONS = ['Crescente', 'Decrescente']
POLICY = 'Comparação: ≥90% dos dias de cada ano calendário solicitado, denominador positivo e período anual completo no snapshot. Demais consultas são exploratórias.'

def br(value, digits=0):
    if pd.isna(value) or not math.isfinite(float(value)):
        return 'Indisponível'
    return f'{value:,.{digits}f}'.replace(',', '_').replace('.', ',').replace('_', '.')

def plain(value):
    return ''.join(c for c in unicodedata.normalize('NFD', str(value)) if not unicodedata.combining(c)).casefold()

def point_label(row):
    return f'{row.municipio} · BR-101/SC · km {br(row.km, 3)} · {row.sentido} · {row.identificador}'

def area_ids(meta, cohort, area, directions, city='Todas as cidades'):
    t = meta.loc[meta.sentido.isin(directions)]
    if area == AREAS[0]: t = t.loc[t.identificador.isin(cohort)]
    elif area == AREAS[2]: t = t.loc[t.identificador.eq('VC101-30')]
    elif area == AREAS[3]: t = t.loc[t.km.ge(370) & t.km.lt(410)]
    if city != 'Todas as cidades': t = t.loc[t.municipio.eq(city)]
    return t.sort_values(['municipio', 'km', 'sentido']).identificador.tolist()

def coverage_rows(daily, ids, years, registry):
    """Grade inclui equipamentos sem publicação. Intervalo vem do manifesto, não do ponto."""
    columns = ['identificador','ano','dias','dias_calendario','cobertura_dias','dias_intervalo','cobertura_intervalo','passagens','altas','por_10_mil']
    if not ids or not years: return pd.DataFrame(columns=columns)
    grid = pd.MultiIndex.from_product([ids, years], names=['identificador','ano']).to_frame(index=False)
    a = annual_table(daily.loc[daily.identificador.isin(ids) & daily.ano.isin(years)])
    t = grid.merge(a.drop(columns=['dias_calendario','cobertura_dias']), how='left', on=['identificador','ano'], validate='one_to_one')
    t['dias'] = t.dias.fillna(0).astype(int)
    t['dias_calendario'] = t.ano.map(lambda y: 366 if calendar.isleap(y) else 365)
    t['cobertura_dias'] = t.dias / t.dias_calendario
    start, end = pd.Timestamp(registry['inicio']), pd.Timestamp(registry['fim'])
    def interval(y):
        left, right = max(start, pd.Timestamp(y,1,1)), min(end, pd.Timestamp(y,12,31))
        return max(0, (right-left).days+1)
    t['dias_intervalo'] = t.ano.map(interval)
    t['cobertura_intervalo'] = t.dias / t.dias_intervalo.replace(0, float('nan'))
    return t[columns]

def comparable_years(coverage):
    """Cada linha representa um ponto e um ano na grade de cobertura publicada."""
    return (coverage.cobertura_dias.ge(.9)
            & coverage.passagens.gt(0)
            & coverage.dias_intervalo.eq(coverage.dias_calendario)).fillna(False)


def query_tables(daily, meta, ids, years, registry):
    selected = daily.loc[daily.identificador.isin(ids) & daily.ano.isin(years)].copy()
    cov = coverage_rows(daily, ids, years, registry)
    eq = equipment_table(selected, meta, years)
    if eq.empty:
        eq['elegivel'] = pd.Series(dtype=bool)
        eq['cobertura_minima'] = pd.Series(dtype=float)
        return selected, eq, cov
    stats = cov.assign(comparavel=comparable_years(cov)).groupby('identificador').agg(
        cobertura_minima=('cobertura_dias','min'), elegivel=('comparavel','all'),
    )
    eq = eq.merge(stats[['cobertura_minima','elegivel']], on='identificador', validate='one_to_one')
    return selected, eq, cov

@dataclass(frozen=True)
class SourceResult:
    fonte: str
    situacao: str
    anos_solicitados: list
    anos_cobertos: list
    anos_sem_cobertura: list
    intervalos: list
    quantidade: int | None
    escopo: str
    nota: str
    def to_dict(self): return asdict(self)
    def text(self):
        value = 'Indisponível' if self.quantidade is None else f'{br(self.quantidade)} registros publicados'
        return (f'{self.fonte}: {value} — {self.situacao}. Anos solicitados: {", ".join(map(str,self.anos_solicitados)) or "nenhum"}; '
                f'com dados da fonte: {", ".join(map(str,self.anos_cobertos)) or "nenhum"}. '
                f'Área: {self.escopo}. {self.nota}')

def source_result(name, frame, years, registry, scope):
    years = sorted(set(years))
    if frame is None:
        return SourceResult(name, 'fonte indisponível', years, [], years, [], None, scope, 'Arquivo não disponível; não significa zero ocorrências.')
    start, end = pd.Timestamp(registry['inicio']), pd.Timestamp(registry['fim'])
    covered = [y for y in years if start <= pd.Timestamp(y,12,31) and end >= pd.Timestamp(y,1,1)]
    intervals = [[str(max(start,pd.Timestamp(y,1,1)).date()), str(min(end,pd.Timestamp(y,12,31)).date())] for y in covered]
    missing = [y for y in years if y not in covered]
    partial = bool(missing) or any(a != f'{y}-01-01' or b != f'{y}-12-31' for y,(a,b) in zip(covered,intervals))
    rows = frame.loc[frame.ano.isin(covered)]
    if not covered: state, value = 'sem cobertura do período', None
    elif partial: state, value = 'cobertura parcial', len(rows)
    elif rows.empty: state, value = 'consulta sem registros em período coberto', 0
    else: state, value = 'período disponível no snapshot', len(rows)
    return SourceResult(name, state, years, covered, missing, intervals, value, scope, registry['nota'])

LABELS = {'identificador':'Equipamento','municipio':'Município','km':'Km na BR-101/SC','sentido':'Sentido',
 'passagens':'Contagens publicadas (base A)','altas':'Contagens acima de 120 km/h (base A)',
 'dias':'Dias publicados','por_10_mil':'Índice por 10 mil contagens','ano':'Ano','mes':'Mês',
 'cobertura_dias':'Cobertura do ano (%)','cobertura_minima':'Menor cobertura anual (%)',
 'dias_calendario':'Dias do ano','dias_intervalo':'Dias do intervalo da fonte','cobertura_intervalo':'Cobertura do intervalo (%)',
 'elegivel':'Comparação anual elegível','possiveis':'Contagens separadas (base B)','segmento':'Segmento (km)',
 'equipamentos':'Pontos','dias_comuns':'Dias com publicação em todos os pontos','cobertura_dias_comuns':'Cobertura de dias comuns (%)',
 'registros_acidentes':'Registros ANTT de acidentes','combinacoes_data_km':'Combinações distintas dia/km'}

def display_table(t):
    t = t.copy()
    for c in t:
        if c.startswith('cobertura'):
            t[c] = t[c].map(lambda x: br(x*100,1)+'%' if pd.notna(x) else 'Indisponível')
        elif c == 'por_10_mil': t[c] = t[c].map(lambda x: br(x,3))
        elif c == 'km': t[c] = t[c].map(lambda x: br(x,3))
        elif c == 'elegivel': t[c] = t[c].map({True:'Sim',False:'Não — exploratório'})
        elif pd.api.types.is_numeric_dtype(t[c]) and c != 'ano': t[c] = t[c].map(br)
    return t.rename(columns=LABELS)


def parse_url(params, meta):
    """Entradas são listas para detectar repetição. Não descarta seleções vazias."""
    out = {'page':PAGES[0], 'years':[2024,2025], 'area':AREAS[0], 'directions':DIRECTIONS.copy(), 'city':'Todas as cidades', 'points':None, 'focus':None}
    notes=[]
    known={'pagina','anos','area','sentidos','cidade','pontos','v','foco'}
    if set(params)-known: notes.append('Parâmetros desconhecidos foram ignorados: '+', '.join(sorted(set(params)-known)))
    if 'v' in params and params['v'] != ['1']: notes.append('Versão de URL não reconhecida; os filtros foram validados novamente.')
    cities=['Todas as cidades',*sorted(meta.municipio.unique())]
    for key, field, options in [('pagina','page',PAGES),('area','area',AREAS),('cidade','city',cities)]:
        if key in params:
            values=params[key]
            if len(values)!=1: notes.append(f'Parâmetro repetido ou vazio: {key}. Usado o padrão indicado nos filtros.')
            elif values[0] in options: out[field]=values[0]
            else: notes.append(f'Valor de {key} desconhecido ou antigo. Usado o padrão indicado nos filtros.')
    for key,field,valid in [('anos','years',list(map(str,YEARS))),('sentidos','directions',DIRECTIONS),('pontos','points',meta.identificador.tolist())]:
        if key not in params: continue
        values=params[key]
        # Listas canônicas usam repetição; valores vazios representam seleção vazia.
        clean=list(dict.fromkeys(v for v in values if v in valid))
        if len(set(values))!=len(values): notes.append(f'Valores repetidos em {key} foram consolidados.')
        if any(v and v not in valid for v in values): notes.append(f'Valores de {key} incompatíveis com o snapshot foram removidos; confira a seleção.')
        out[field]=list(map(int,clean)) if field=='years' else clean
    focus = params.get('foco', [])
    if len(focus) == 1 and 0 < len(focus[0]) <= 80:
        out['focus'] = focus[0]
    elif 'foco' in params:
        notes.append('Foco da consulta inválido ou repetido.')
    return out,notes

def url_state(page, years, area, directions, city, points, focus=None):
    params = {'v':'1','pagina':page,'anos':list(map(str,years)) or [''], 'area':area,'sentidos':directions or [''], 'cidade':city,'pontos':points or ['']}
    if focus:
        params['foco'] = focus
    return params
