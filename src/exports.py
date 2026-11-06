"""Arquivos de consulta com filtros solicitados, efetivos e proveniência."""
from datetime import datetime, timezone
import hashlib
import io
import json
import os
import subprocess
import zipfile
from urllib.parse import urlencode
import pandas as pd
from config import ROOT
from src.antt import weighted_index
from src.query import br, display_table, POLICY, url_state

APP_VERSION='2.1.0'

def code_version():
    value=os.environ.get('RENDER_GIT_COMMIT')
    if value: return value
    try:
        sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL,timeout=2).strip()
        dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL,timeout=2).strip()
        return sha+('+alterações-locais' if dirty else '')
    except (OSError,subprocess.SubprocessError):return 'SHA não disponível nesta instalação'

def metadata(manifest, filters, ids, daily, sources):
    params=url_state(filters['page'],filters['years'],filters['area'],filters['directions'],filters['city'],ids)
    return {'aplicacao':'SENTINELA','versao_aplicacao':APP_VERSION,'codigo':code_version(),'snapshot':manifest['versao'],
      'gerado_utc':datetime.now(timezone.utc).isoformat(),'filtros_solicitados':filters,
      'efetivo':{'equipamentos':sorted(daily.identificador.unique().tolist()),'anos_com_trafego':sorted(map(int,daily.ano.unique())),
       'inicio_publicado':str(daily.data.min().date()) if not daily.empty else None,'fim_publicado':str(daily.data.max().date()) if not daily.empty else None},
      'unidade':'Contagens nas faixas acima de 120 km/h por 10 mil contagens publicadas da mesma base A',
      'politica_cobertura':POLICY,'fontes_acidentes':[s.to_dict() for s in sources],
      'cobertura_declarada':manifest['cobertura'],'proveniencia':manifest['proveniencia'],
      'consulta_relativa':'?'+urlencode(params,doseq=True),
      'consulta_publica_apos_publicacao':'https://radarsul.site/?'+urlencode(params,doseq=True),
      'aviso_url':'A URL pública reproduzirá esta versão somente após sua publicação; confira código e snapshot.',
      'limites':'Não representa risco individual, probabilidade de acidente, veículos únicos ou autuações. Não somar ANTT e PRF. Taxa B/A bloqueada.'}

def csv_bytes(table,meta,brazil=True):
    t=table.copy()
    t['anos_solicitados']=', '.join(map(str,meta['filtros_solicitados']['years']))
    t['equipamentos_solicitados']=', '.join(meta['filtros_solicitados']['points'])
    t['area_solicitada']=meta['filtros_solicitados']['area'];t['sentidos_solicitados']=', '.join(meta['filtros_solicitados']['directions'])
    t['unidade_indice']=meta['unidade'];t['snapshot']=meta['snapshot'];t['codigo']=meta['codigo'];t['gerado_utc']=meta['gerado_utc']
    t['cobertura_acidentes_json']=json.dumps(meta['fontes_acidentes'],ensure_ascii=False)
    return t.to_csv(index=False,sep=';' if brazil else ',',decimal=',' if brazil else '.',lineterminator='\n').encode('utf-8-sig')

def markdown_report(daily, eq, cov, meta, possible=None):
    total=daily.passagens.sum(); high=daily.altas.sum()
    rows=['# SENTINELA — Consulta verificável',
      f"Área: {meta['filtros_solicitados']['area']}. Cidade: {meta['filtros_solicitados']['city']}.",
      f"Anos solicitados: {', '.join(map(str,meta['filtros_solicitados']['years']))}. Anos com tráfego: {', '.join(map(str,meta['efetivo']['anos_com_trafego']))}.",
      'Pontos solicitados: '+', '.join(meta['filtros_solicitados']['points'])+'.',
      'Pontos com tráfego: '+', '.join(meta['efetivo']['equipamentos'])+'.',
      'Sentidos: '+', '.join(meta['filtros_solicitados']['directions'])+'.',
      f"Publicações de tráfego: {meta['efetivo']['inicio_publicado']} a {meta['efetivo']['fim_publicado']}.",
      f'Contagens publicadas: {br(total)}. Acima de 120 km/h: {br(high)}. Índice agregado: {br(weighted_index(high,total),3)} por 10 mil.',
      meta['limites'], POLICY,
      '## Cobertura por ponto e ano',
      'Dias publicados não comprovam operação ou completude de faixas. A cobertura do intervalo usa o período declarado da fonte; a cobertura anual usa o calendário completo.',
      table_markdown(display_table(cov)),
      '## Contextos de acidentes independentes']
    for s in meta['fontes_acidentes']:
        rows.append(f"{s['fonte']}: {'indisponível' if s['quantidade'] is None else br(s['quantidade'])+' registros publicados'}; {s['situacao']}. Anos solicitados {s['anos_solicitados']}; cobertos {s['anos_cobertos']}; intervalos {s['intervalos']}. Área: {s['escopo']}. {s['nota']}")
    if possible is not None:
        rows+=['## Base B separada',f'{br(possible.possiveis.sum())} contagens em {br(possible.data.nunique())} datas publicadas.' if not possible.empty else 'Sem linhas publicadas neste recorte; não comprova zero infrações.', 'Taxa possíveis infratores/tráfego bloqueada por incompatibilidade de faixas e classificação.']
    rows+=['## Fontes e rastreabilidade',f"Aplicação {meta['versao_aplicacao']}; código {meta['codigo']}; snapshot {meta['snapshot']}; geração UTC {meta['gerado_utc']}.",f"[Reproduzir após publicação]({meta['consulta_publica_apos_publicacao']}) — {meta['aviso_url']}"]
    rows += [f"- [{r['arquivo']}]({r['url']}), coleta {r['acesso_utc']}, SHA-256 {r['sha256']}" for r in meta['proveniencia']]
    rows+=['120 km/h é limiar dos intervalos publicados, sem inferir infração regulamentada. Cadastro de junho de 2026 não reconstrói limites históricos. Repetições ANTT sem ID preservadas. Correlação e persistência não validam previsão ou causalidade. Associação negativa não significa proteção pela velocidade.']
    return '\n\n'.join(rows)+'\n'

def table_markdown(t):
    def safe(v):return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(map(safe,t.columns))+' |\n| '+' | '.join(['---']*len(t.columns))+' |\n'+'\n'.join('| '+' | '.join(map(safe,row))+' |' for row in t.itertuples(index=False,name=None))

def bundle(eq,cov,meta,document,extra=None):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('comparacao_pt-BR.csv',csv_bytes(eq,meta));z.writestr('comparacao_tecnica.csv',csv_bytes(eq,meta,False))
        z.writestr('cobertura_pt-BR.csv',csv_bytes(cov,meta));z.writestr('metadados.json',json.dumps(meta,ensure_ascii=False,indent=2));z.writestr('relatorio.md',document)
        for name,t in (extra or {}).items():z.writestr(name,csv_bytes(t,meta))
    return buffer.getvalue()

def filename(meta,suffix):
    key=hashlib.sha256(json.dumps(meta['filtros_solicitados'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:10]
    return f"sentinela_{meta['snapshot']}_{key}.{suffix}"
