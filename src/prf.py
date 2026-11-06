"""Reconstrução PRF por ocorrência, com proveniência e auditoria explícitas."""
import io
import json
import zipfile
from pathlib import Path
import pandas as pd
from config import KM_MIN, KM_MAX
from src.data_package import digest

COUNTS=['pessoas','mortos','feridos_leves','feridos_graves','ilesos','ignorados','feridos','veiculos']

def build_prf(raw, output):
    raw,output=Path(raw),Path(output)
    records=json.loads((raw/'manifesto_prf.json').read_text())
    frames=[];audit=[]
    for record in records:
        p=raw/record['arquivo']
        if digest(p)!=record['sha256']: raise ValueError('Hash PRF divergente.')
        with zipfile.ZipFile(p) as z:
            names=[n for n in z.namelist() if n.endswith('.csv')]
            if len(names)!=1: raise ValueError('ZIP PRF deve conter um CSV.')
            d=pd.read_csv(io.BytesIO(z.read(names[0])),sep=';',encoding='latin1',dtype='string')
        required=['id','data_inversa','uf','br','km','latitude','longitude','horario',*COUNTS]
        if set(required)-set(d):raise ValueError('Esquema PRF desconhecido.')
        for c in ['br',*COUNTS]: d[c]=pd.to_numeric(d[c],errors='raise').astype('Int64')
        for c in ['km','latitude','longitude']: d[c]=pd.to_numeric(d[c].str.replace(',','.',regex=False),errors='raise').astype('Float64')
        total=len(d)
        d=d.loc[d.uf.eq('SC') & d.br.eq(101) & d.km.between(KM_MIN,KM_MAX)].copy()
        d['arquivo_origem']=record['arquivo']
        d['data']=pd.to_datetime(d.data_inversa,format='%Y-%m-%d',errors='raise')
        if not d.data.dt.year.eq(record['ano']).all():raise ValueError('Ano PRF incompatível com o arquivo.')
        if d.id.isna().any() or d.id.duplicated().any(): raise ValueError('ID PRF duplicado/ausente: investigar sem deduplicação silenciosa.')
        d['ano']=d.data.dt.year.astype('Int64');d['mes']=d.data.dt.to_period('M').astype('string')
        d['hora']=pd.to_numeric(d.horario.str[:2],errors='raise').astype('Int64');d['dia_semana_num']=d.data.dt.dayofweek.astype('Int64')
        d['grave_ou_fatal']=(d.mortos+d.feridos_graves).gt(0);d['fatal']=d.mortos.gt(0)
        d['vitimas_graves_fatais']=d.mortos+d.feridos_graves
        # Flags de qualidade, sem modificar contagens publicadas.
        d['problema_contagem']=d[COUNTS].lt(0).any(axis=1).astype('boolean')
        d['problema_soma_feridos']=d.feridos.ne(d.feridos_leves+d.feridos_graves)
        d['problema_soma_pessoas']=d.pessoas.ne(d.mortos+d.feridos+d.ilesos+d.ignorados)
        d['coordenada_suspeita']=(d.latitude.isna() | d.longitude.isna() | ~d.latitude.between(-30,-27) | ~d.longitude.between(-51,-48)).astype('boolean')
        audit.append({'arquivo':record['arquivo'],'linhas_originais':total,'linhas_trecho':len(d),'ids_duplicados':int(d.id.duplicated().sum()),'soma_pessoas_divergente':int(d.problema_soma_pessoas.sum()),'coordenadas_suspeitas':int(d.coordenada_suspeita.sum())})
        frames.append(d)
    result=pd.concat(frames,ignore_index=True).sort_values(['data','id']).reset_index(drop=True)
    if result.id.duplicated().any():raise ValueError('IDs PRF repetidos entre anos.')
    output.mkdir(parents=True,exist_ok=True);result.to_parquet(output/'ocorrencias.parquet',index=False)
    (output/'auditoria_prf.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result,audit
