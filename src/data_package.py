"""Contrato verificável do snapshot. Geração do manifesto é ação de manutenção."""
import argparse
import hashlib
import json
import logging
from pathlib import Path
import pandas as pd
from config import ROOT
from src.antt import annual_table, monthly_table, cohort_ids, equipment_table, weighted_index

MANIFEST = 'dados_tratados/manifesto.json'
FILES = [f'dados_tratados/antt_{n}.parquet' for n in ['diario','mensal','anual','equipamentos','possiveis_diario','acidentes','contexto_5km','coorte']]+['dados_tratados/ocorrencias.parquet','relatorios/resumo_antt.json','relatorios/auditoria_antt.json','relatorios/descobertas_antt.json']
# Inventário de períodos do snapshot bruto, não inferência de completude por dias de ocorrências.
COVERAGE = {
 'trafego':{'inicio':'2022-01-01','fim':'2026-06-30','nota':'Dias com publicação; não comprova operação contínua nem completude de faixas. 2026 parcial até 30/06.'},
 'possiveis':{'inicio':'2022-12-30','fim':'2026-06-02','nota':'Base B separada. Intervalo do inventário bruto; ausência de linhas não comprova zero infrações. Taxa B/A bloqueada.'},
 'antt':{'inicio':'2021-05-01','fim':'2025-12-31','nota':'Intervalo do inventário do CSV de acidentes, sem garantia de completude. Repetições sem ID preservadas.'},
 'prf':{'inicio':'2024-01-01','fim':'2025-12-31','nota':'Arquivos anuais PRF 2024 e 2025. Ausência de registro não prova ausência real de acidente.'}}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def generate(root=ROOT):
    root=Path(root)
    records={}
    for name in FILES:
        p=root/name
        record={'sha256':digest(p),'bytes':p.stat().st_size,'opcional':name.endswith('/ocorrencias.parquet')}
        if p.suffix=='.parquet':
            df=pd.read_parquet(p)
            record.update(linhas=len(df), esquema={c:str(df[c].dtype) for c in df})
        records[name]=record
    provenance=json.loads((root/'dados_brutos/coleta_20261026T224903Z.json').read_text())
    prf=root/'dados_brutos/manifesto_prf.json'
    if prf.exists(): provenance+=json.loads(prf.read_text())
    manifest={'contrato':1,'versao':'2026-10-26.1','transformacao':'antt-2.0+prf-1.0','coleta_antt':'2026-10-26','coleta_prf':'2026-10-23',
      'cobertura':COVERAGE,'politica':'90% por ano calendário completo; 80% por mês para exibição; sem inferência de operação.',
      'declaracao_cobertura':'Inventário temporal dos arquivos brutos e nomes anuais PRF; não certifica completude das fontes de acidentes.',
      'proveniencia':provenance,'arquivos':records}
    (root/MANIFEST).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

def token(root=ROOT):
    root=Path(root)
    # Verifica mudança de qualquer arquivo, inclusive remoção/restauração, antes de consultar cache.
    m=json.loads((root/MANIFEST).read_text())
    return (digest(root/MANIFEST),tuple((n, (root/n).stat().st_mtime_ns, (root/n).stat().st_size) if (root/n).exists() else (n,None,None) for n in sorted(m['arquivos'])))

def validate(root=ROOT, allow_missing_prf=False):
    root=Path(root)
    m=json.loads((root/MANIFEST).read_text())
    if m.get('contrato')!=1 or m.get('transformacao')!='antt-2.0+prf-1.0' or set(m.get('arquivos',{}))!=set(FILES):
        raise ValueError('Contrato de dados incompatível ou incompleto.')
    frames={}
    for name,record in m['arquivos'].items():
        if name not in FILES: raise ValueError('Caminho não permitido no manifesto.')
        p=root/name
        if not p.exists() and name=='dados_tratados/ocorrencias.parquet' and allow_missing_prf:
            logging.warning('Fonte PRF indisponível no pacote %s',m['versao']);continue
        if not p.exists() or digest(p)!=record['sha256']: raise ValueError('Arquivo ausente ou hash divergente: '+name)
        if p.suffix=='.parquet':
            df=pd.read_parquet(p)
            if len(df)!=record['linhas'] or {c:str(df[c].dtype) for c in df}!=record['esquema']: raise ValueError('Esquema divergente: '+name)
            frames[p.stem]=df
    daily=frames['antt_diario']; meta=frames['antt_equipamentos']
    for name,key in [('antt_diario',['identificador','data']),('antt_mensal',['identificador','mes']),('antt_anual',['identificador','ano']),('antt_equipamentos',['identificador']),('antt_possiveis_diario',['identificador','data'])]:
        if frames[name].duplicated(key).any() or frames[name][key].isna().any().any(): raise ValueError('Chave duplicada/ausente: '+name)
    if not daily.identificador.isin(meta.identificador).all(): raise ValueError('Equipamento sem cadastro.')
    if (daily[['passagens','altas']]<0).any().any() or daily.altas.gt(daily.passagens).any(): raise ValueError('Contagens inválidas.')
    def same(a,b,keys):
        pd.testing.assert_frame_equal(a.sort_values(keys).reset_index(drop=True),b[a.columns].sort_values(keys).reset_index(drop=True),check_dtype=False,atol=1e-12,rtol=1e-12)
    same(annual_table(daily),frames['antt_anual'],['identificador','ano'])
    same(monthly_table(daily),frames['antt_mensal'],['identificador','mes'])
    summary=json.loads((root/'relatorios/resumo_antt.json').read_text())
    ids=cohort_ids(frames['antt_anual']); rank=equipment_table(daily.loc[daily.identificador.isin(ids)],meta)
    if summary['coorte_ids']!=ids or summary['coorte_passagens']!=int(rank.passagens.sum()) or summary['coorte_altas']!=int(rank.altas.sum()): raise ValueError('Resumo de outra versão.')
    if abs(summary['coorte_indice_por10mil']-weighted_index(rank.altas.sum(),rank.passagens.sum()))>1e-12: raise ValueError('Índice do resumo divergente.')
    same(rank,frames['antt_coorte'],['identificador'])
    return m,frames,summary

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['validate','manifest']);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
    if a.action=='manifest': generate(a.root)
    m,_,_=validate(a.root)
    print(json.dumps({'pacote':m['versao'],'estado':'válido','arquivos':len(m['arquivos'])},ensure_ascii=False))
if __name__=='__main__':main()
