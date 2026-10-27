"""Auditoria e indicadores ANTT. Não calcula possíveis infratores/tráfego."""
from pathlib import Path
import calendar
import hashlib
import io
import json
import unicodedata
import numpy as np
import pandas as pd
from config import RAW, PROCESSED, REPORTS, KM_MIN, KM_MAX

FILES={'trafego':'volume-radar-viacosteira.csv','possiveis':'quantidade-possiveis-infratores-viacosteira.csv',
       'acidentes':'demostrativo_acidentes_viacosteira.csv','cadastro':'dados-dos-radares6_2026.csv'}
BANDS={'<= 20 KM/h':(0,20),'21 - 50 KM':(21,50),'51 - 80 KM':(51,80),'81 - 100 K':(81,100),
       '101 - 120':(101,120),'121 - 140':(121,140),'141 - 160':(141,160),'> 160 KM/h':(161,None)}
YEARS=(2024,2025)
MIN_COVERAGE=.90


def read_csv(path):
    payload=Path(path).read_bytes()
    try:payload.decode('utf-8-sig');encoding='utf-8-sig'
    except UnicodeDecodeError:encoding='latin1'
    return pd.read_csv(io.BytesIO(payload),sep=';',encoding=encoding,dtype='string'),encoding


def number(series):
    return pd.to_numeric(series.astype('string').str.replace(',','.',regex=False),errors='coerce')


def profile(df,encoding):
    return {'linhas':len(df),'colunas':list(df.columns),'encoding':encoding,'ausentes':{k:int(v) for k,v in df.isna().sum().items()},
        'distintos':{k:int(v) for k,v in df.nunique(dropna=False).items()},'duplicatas_integrais':int(df.duplicated().sum()),
        'valores_distintos':{c:df[c].dropna().unique().tolist() for c in df if df[c].nunique()<=60}}


def passages(df):
    required=['identificador','data_da_passagem','velocidade','volume_total','km_m','sentido_da_passagem','faixa_da_passagem','tipo_de_veiculo']
    if set(required)-set(df):raise ValueError('Esquema ANTT não reconhecido.')
    out=df.copy()
    out['data']=pd.to_datetime(out.data_da_passagem,format='%d/%m/%Y',errors='coerce')
    out['km']=number(out.km_m)
    out['quantidade']=number(out.volume_total)
    out['faixa_velocidade']=out.velocidade.str.strip()
    if not out.faixa_velocidade.isin(BANDS).all():raise ValueError('Faixa de velocidade nova ou não reconhecida.')
    out['acima_120']=out.faixa_velocidade.isin(['121 - 140','141 - 160','> 160 KM/h'])
    invalid=out.data.isna()|out.km.isna()|out.quantidade.isna()|out.quantidade.lt(0)|(out.quantidade%1).ne(0)
    if invalid.any():raise ValueError(f'{int(invalid.sum())} linhas com data, km ou quantidade inválidos. Revisar antes de analisar.')
    out['ano']=out.data.dt.year
    out['mes']=out.data.dt.to_period('M').astype(str)
    out['quantidade_alta']=out.quantidade.where(out.acima_120,0)
    out['lat']=number(out.latitude);out['lon']=number(out.longitude)
    return out


def weighted_index(high,total):
    """Índice por 10 mil contagens publicadas da própria base A."""
    return 10000*high/total if pd.notna(total) and total>0 else np.nan


def annual_table(daily):
    out=daily.groupby(['identificador','ano'],as_index=False).agg(passagens=('passagens','sum'),altas=('altas','sum'),dias=('data','nunique'))
    out['dias_calendario']=out.ano.map(lambda y:366 if calendar.isleap(int(y)) else 365)
    out['cobertura_dias']=out.dias/out.dias_calendario
    out['por_10_mil']=10000*out.altas/out.passagens.replace(0,np.nan)
    return out


def cohort_ids(annual,threshold=MIN_COVERAGE):
    target=annual.loc[annual.ano.isin(YEARS)]
    g=target.groupby('identificador').agg(anos=('ano','nunique'),cobertura_min=('cobertura_dias','min'))
    return sorted(g.index[g.anos.eq(2)&g.cobertura_min.ge(threshold)].tolist())


def equipment_table(daily,metadata,years=YEARS):
    selected=daily.loc[daily.ano.isin(years)]
    if selected.empty:return pd.DataFrame(columns=[*metadata.columns,'passagens','altas','dias','por_10_mil'])
    out=selected.groupby('identificador',as_index=False).agg(passagens=('passagens','sum'),altas=('altas','sum'),dias=('data','nunique'))
    out['por_10_mil']=10000*out.altas/out.passagens.replace(0,np.nan)
    before=out.passagens.sum()
    out=out.merge(metadata,on='identificador',how='left',validate='one_to_one')
    if out.passagens.sum()!=before:raise ValueError('Cadastro multiplicou contagens.')
    return out.sort_values(['por_10_mil','identificador'],ascending=[False,True]).reset_index(drop=True)


def monthly_table(daily):
    out=daily.groupby(['identificador','mes'],as_index=False).agg(passagens=('passagens','sum'),altas=('altas','sum'),dias=('data','nunique'))
    out['data_mes']=pd.to_datetime(out.mes+'-01')
    out['cobertura_dias']=out.dias/out.data_mes.dt.days_in_month
    out['por_10_mil']=10000*out.altas/out.passagens.replace(0,np.nan)
    out['comparavel_80pct']=out.cobertura_dias.ge(.80)
    return out


def context_table(daily,metadata,accidents,ids,years=YEARS,width=5):
    points=equipment_table(daily.loc[daily.identificador.isin(ids)],metadata,years)
    columns=['segmento_inicio','passagens','altas','equipamentos','por_10_mil','registros_acidentes','combinacoes_data_km','segmento','dias_comuns','cobertura_dias_comuns']
    if points.empty:return pd.DataFrame(columns=columns)
    points['segmento_inicio']=np.floor(points.km/width)*width
    expected=points.groupby('segmento_inicio').identificador.nunique()
    rows=daily.loc[daily.identificador.isin(ids)&daily.ano.isin(years)].merge(
        points[['identificador','segmento_inicio']],on='identificador',how='left',validate='many_to_one')
    day=rows.groupby(['segmento_inicio','data'],as_index=False).agg(
        passagens=('passagens','sum'),altas=('altas','sum'),equipamentos_publicando=('identificador','nunique'))
    day['equipamentos']=day.segmento_inicio.map(expected)
    common=day.loc[day.equipamentos_publicando.eq(day.equipamentos)].copy()
    out=common.groupby('segmento_inicio',as_index=False).agg(
        passagens=('passagens','sum'),altas=('altas','sum'),equipamentos=('equipamentos','first'),dias_comuns=('data','nunique'))
    out['por_10_mil']=10000*out.altas/out.passagens.replace(0,np.nan)
    calendar_days=sum(366 if calendar.isleap(int(y)) else 365 for y in years)
    out['cobertura_dias_comuns']=out.dias_comuns/calendar_days
    selected=accidents.loc[accidents.ano.isin(years)&accidents.km.between(KM_MIN,KM_MAX)].copy()
    selected['segmento_inicio']=np.floor(selected.km/width)*width
    # Mesmos dias e segmento, sem multiplicar um acidente pelos equipamentos do segmento.
    selected=selected.merge(common[['segmento_inicio','data']],on=['segmento_inicio','data'],
        how='inner',validate='many_to_one')
    raw=selected.groupby('segmento_inicio').size().rename('registros_acidentes')
    unique=selected.drop_duplicates(['concessionaria','data','km','trecho']).groupby('segmento_inicio').size().rename('combinacoes_data_km')
    out=out.merge(raw,on='segmento_inicio',how='left',validate='one_to_one').merge(unique,on='segmento_inicio',how='left',validate='one_to_one')
    out[['registros_acidentes','combinacoes_data_km']]=out[['registros_acidentes','combinacoes_data_km']].fillna(0).astype(int)
    out['segmento']=out.segmento_inicio.map(lambda v:f'{max(v,KM_MIN):g}–{min(v+width,KM_MAX):g} km')
    return out


def build():
    audit={'perfis':{},'proveniencia':[],'decisoes':[]}
    frames={}
    manifest=json.loads((RAW/'coleta_20261026T224903Z.json').read_text())
    for name,filename in FILES.items():
        df,enc=read_csv(RAW/filename);frames[name]=df
        audit['perfis'][name]=profile(df,enc)
        record=next(x for x in manifest if x['arquivo']==filename)
        actual=hashlib.sha256((RAW/filename).read_bytes()).hexdigest()
        if actual!=record['sha256']:raise ValueError(f'Hash divergente: {filename}')
        audit['proveniencia'].append({**record,'hash_conferido':True})
    a,b=passages(frames['trafego']),passages(frames['possiveis'])
    loc_a=a.groupby('identificador').agg(km=('km','first'),sentido=('sentido_da_passagem','first'))
    loc_b=b.groupby('identificador').agg(km=('km','first'),sentido=('sentido_da_passagem','first'))
    check=loc_a.join(loc_b,lsuffix='_a',rsuffix='_b',validate='one_to_one')
    audit['localizacao_ab']={'equipamentos':len(check),'km_e_sentido_coincidem':int((check.km_a.eq(check.km_b)&check.sentido_a.eq(check.sentido_b)).sum())}
    if audit['localizacao_ab']['km_e_sentido_coincidem']!=len(check):raise ValueError('IDs de A e B apresentam localização ou sentido incompatível.')
    for name,df in [('trafego',a),('possiveis',b)]:
        audit['perfis'][name].update(data_min=str(df.data.min().date()),data_max=str(df.data.max().date()),
                                   soma_quantidade=int(df.quantidade.sum()),equipamentos=int(df.identificador.nunique()))
    # Classes ausente e não classificado não têm disjunção demonstrada no mesmo dia/faixa.
    key=['identificador','data','sentido_da_passagem','faixa_da_passagem','faixa_velocidade']
    ambiguous=a.duplicated(key,keep=False)
    days_bad=a.loc[ambiguous,['identificador','data']].drop_duplicates().assign(sobreposicao_ambigua=True)
    a=a.merge(days_bad,on=['identificador','data'],how='left',validate='many_to_one')
    quarantine=a.loc[a.sobreposicao_ambigua.eq(True)].copy()
    valid=a.loc[~a.sobreposicao_ambigua.eq(True)].copy()
    if valid.duplicated(key).any():raise ValueError('Chave das contagens de tráfego ainda ambígua.')
    daily=valid.groupby(['identificador','data','ano','mes'],as_index=False).agg(passagens=('quantidade','sum'),altas=('quantidade_alta','sum'),faixas_publicadas=('faixa_velocidade','nunique'))
    if daily.passagens.sum()!=valid.quantidade.sum():raise ValueError('A agregação diária não conserva tráfego.')
    audit['sobreposicao_trafego']={'linhas_chave_repetida':int(ambiguous.sum()),'equipamentos_dia_excluidos':len(days_bad),
                                 'linhas_em_quarentena':len(quarantine),'passagens_em_quarentena':int(quarantine.quantidade.sum()),
                                 'datas':sorted(quarantine.data.dt.strftime('%Y-%m-%d').unique().tolist())}
    # Demonstra o problema do denominador, sem produzir a taxa B/A.
    strict=['identificador','data','sentido_da_passagem','faixa_da_passagem']
    aa=valid.groupby(strict,as_index=False).quantidade.sum().rename(columns={'quantidade':'passagens'})
    bb=b.groupby(strict,as_index=False).quantidade.sum().rename(columns={'quantidade':'possiveis'})
    joined=bb.merge(aa,on=strict,how='left',validate='one_to_one',indicator=True)
    audit['compatibilidade_ab']={'unidades_b':len(bb),'sem_denominador':int(joined.passagens.isna().sum()),
        'com_denominador':int(joined.passagens.notna().sum()),'numerador_maior_denominador':int(joined.possiveis.gt(joined.passagens).sum()),
        'codigo_faixa_a_por_sentido':pd.crosstab(valid.sentido_da_passagem,valid.faixa_da_passagem).to_dict(),
        'codigo_faixa_b_por_sentido':pd.crosstab(b.sentido_da_passagem,b.faixa_da_passagem).to_dict(),
        'taxa_possiveis_infracoes_validada':False,
        'motivo':'Semântica de faixas incompatível e categoria de veículo ausente em A. Não calcular B/A.'}
    meta=valid.groupby('identificador',as_index=False).agg(km=('km','first'),municipio=('municipio','first'),sentido=('sentido_da_passagem','first'),
        lat=('lat','first'),lon=('lon','first'),km_distintos=('km','nunique'),sentidos_distintos=('sentido_da_passagem','nunique'))
    if meta.km_distintos.gt(1).any() or meta.sentidos_distintos.gt(1).any():raise ValueError('Equipamento mudou de posição/sentido: separar histórico antes de continuar.')
    cadastro=frames['cadastro'].rename(columns={'Municipio':'municipio'}).copy()
    cadastro=cadastro.loc[cadastro.concessionaria.str.upper().eq('VIA COSTEIRA')].copy()
    cadastro['km']=number(cadastro.km_m);cadastro['limite_leve_ref_2026']=number(cadastro.velocidade_leve);cadastro['limite_pesado_ref_2026']=number(cadastro.velocidade_pesado)
    ckey=['rodovia','uf','km','sentido']
    if cadastro.duplicated(ckey).any():raise ValueError('Cadastro ViaCosteira não tem chave espacial única.')
    meta['rodovia']='BR-101';meta['uf']='SC'
    meta=meta.merge(cadastro[ckey+['limite_leve_ref_2026','limite_pesado_ref_2026','situacao']],on=ckey,how='left',validate='one_to_one')
    audit['cadastro']={'linhas_viacosteira':len(cadastro),'equipamentos_trafego':len(meta),
        'correspondencias_exatas':int(meta.situacao.notna().sum()),'sem_correspondencia':meta.loc[meta.situacao.isna(),'identificador'].tolist(),
        'uso':'Referência de junho de 2026. Não inferir limites regulamentados históricos.'}
    annual=annual_table(daily);ids=cohort_ids(annual)
    meta['coorte_90pct_2024_2025']=meta.identificador.isin(ids)
    rawc=frames['acidentes'].rename(columns={'Concessionaria':'concessionaria','Data':'data_texto','Km':'km_texto','Trecho':'trecho'}).copy()
    rawc['data']=pd.to_datetime(rawc.data_texto,format='%d/%m/%Y',errors='raise');rawc['km']=number(rawc.km_texto);rawc['ano']=rawc.data.dt.year
    rawc['linha_fonte']=np.arange(1,len(rawc)+1)
    rawc['chave_repetida']=rawc.duplicated(['concessionaria','data','km','trecho'],keep=False)
    audit['acidentes']={'data_min':str(rawc.data.min().date()),'data_max':str(rawc.data.max().date()),'linhas':len(rawc),
        'duplicatas_alem_primeira':int(rawc.duplicated(['concessionaria','data','km','trecho']).sum()),'sem_id_ocorrencia':True,
        'decisao':'Preservar registros repetidos: podem representar múltiplas ocorrências no mesmo dia/km. Não somar com PRF.'}
    monthly=monthly_table(daily)
    possible_daily=b.groupby(['identificador','data','ano','mes'],as_index=False).agg(possiveis=('quantidade','sum'),faixas=('faixa_da_passagem','nunique'))
    rank=equipment_table(daily.loc[daily.identificador.isin(ids)],meta)
    ay=annual.loc[annual.identificador.isin(ids)&annual.ano.isin(YEARS)]
    pivot=ay.pivot(index='identificador',columns='ano',values='por_10_mil')
    q=pivot.quantile(.75)
    persistent=pivot.index[pivot[2024].ge(q[2024])&pivot[2025].ge(q[2025])].tolist()
    rho=float(pivot.corr(method='spearman').iloc[0,1])
    context=context_table(daily,meta,rawc,ids)
    rho_context=float(context[['por_10_mil','registros_acidentes']].corr(method='spearman').iloc[0,1])
    sensitivities=[]
    for width in [2,5,10]:
        ctx=context_table(daily,meta,rawc,ids,width=width)
        sensitivities.append({'largura_km':width,'segmentos':len(ctx),'spearman':float(ctx[['por_10_mil','registros_acidentes']].corr(method='spearman').iloc[0,1]),
            'spearman_combinacoes_data_km':float(ctx[['por_10_mil','combinacoes_data_km']].corr(method='spearman').iloc[0,1])})
    for threshold in [.80,.90,.95]:
        cids=cohort_ids(annual,threshold);eq=equipment_table(daily.loc[daily.identificador.isin(cids)],meta)
        sensitivities.append({'cobertura_minima':threshold,'equipamentos':len(cids),'indice_agregado_por10mil':weighted_index(eq.altas.sum(),eq.passagens.sum())})
    y=valid.loc[valid.ano.isin(YEARS)]
    summary={'versao':'2.0','coleta_local':'26/10/2026','periodo_principal':['2024-01-01','2025-12-31'],
        'equipamentos_trafego':len(meta),'municipios':int(meta.municipio.nunique()),'coorte_equipamentos':len(ids),
        'coorte_ids':ids,'coorte_passagens':int(rank.passagens.sum()),'coorte_altas':int(rank.altas.sum()),
        'coorte_indice_por10mil':weighted_index(rank.altas.sum(),rank.passagens.sum()),
        'todos_passagens_2024_2025':int(y.quantidade.sum()),'todos_altas_2024_2025':int(y.quantidade_alta.sum()),
        'spearman_anos':rho,'persistentes':persistent,'limiares_q75':{str(k):float(v) for k,v in q.items()},
        'spearman_contexto_5km':rho_context,'segmentos_contexto':len(context),
        'taxa_possiveis_infracoes_disponivel':False,
        'acidentes_antt_2024_2025':int(rawc.ano.isin(YEARS).sum()),
        'criciuma':annual.loc[annual.identificador.eq('VC101-30')&annual.ano.isin(YEARS)].to_dict('records')}
    facts=[{'id':'D1','titulo':f'O índice acima de 120 km/h varia de {rank.por_10_mil.min():.2f} a {rank.por_10_mil.max():.2f} por 10 mil',
            'minimo':float(rank.por_10_mil.min()),'maximo':float(rank.por_10_mil.max()),'periodo':'2024–2025','equipamentos':len(ids),
            'max_id':rank.iloc[0].identificador,'max_altas':int(rank.iloc[0].altas),'max_denominador':int(rank.iloc[0].passagens),
            'interpretacao':'Heterogeneidade entre contagens publicadas em pontos monitorados com cobertura diária mínima de 90% em cada ano.',
            'limite':'Limiar analítico de 120 km/h. Não é frequência de autuações, nem risco de acidente. Cobertura é de registros, não de operação.'},
           {'id':'D2','titulo':f'A ordenação anual do índice apresenta Spearman {rho:.2f}',
            'rho':rho,'persistentes':persistent,'n_persistentes':len(persistent),'periodo':'2024–2025',
            'interpretacao':'Quatro equipamentos estão no quartil superior nos dois anos. A consulta pode priorizar investigação de padrões repetidos.',
            'limite':'Dois anos e seleção de cobertura. Não é validação de previsão. Sem teste de significância ou inferência causal.'},
           {'id':'D3','titulo':f'O contexto por segmentos de 5 km apresenta Spearman {rho_context:.2f}',
            'rho':rho_context,'segmentos':len(context),'sensibilidade':sensitivities[:3],'periodo':'2024–2025',
            'interpretacao':'Em segmentos disjuntos de 5 km e somente nos dias em que todos os equipamentos do segmento publicaram, maior índice acima de 120 não acompanha maior contagem de registros de acidentes.',
            'limite':'Não significa efeito protetor da velocidade. Fluxo, localização dos radares, seleção, subregistro e agregação espacial podem explicar a associação.'}]
    audit['coorte']={'limiar_cobertura':MIN_COVERAGE,'equipamentos':len(ids),'ids':ids,'limiar_mensal_exibicao':.80,
        'limite':'Proporção de dias com publicação, sem atestar disponibilidade técnica do equipamento.'}
    PROCESSED.mkdir(exist_ok=True);REPORTS.mkdir(exist_ok=True)
    outputs={'antt_diario':daily,'antt_mensal':monthly,'antt_anual':annual,'antt_equipamentos':meta,
        'antt_possiveis_diario':possible_daily,'antt_acidentes':rawc,'antt_contexto_5km':context,'antt_coorte':rank}
    for name,frame in outputs.items():
        frame.to_parquet(PROCESSED/f'{name}.parquet',index=False)
        frame.to_csv(PROCESSED/f'{name}.csv',index=False,encoding='utf-8-sig')
    quarantine.to_csv(PROCESSED/'antt_quarentena_trafego.csv',index=False)
    pd.DataFrame(sensitivities).to_csv(PROCESSED/'antt_sensibilidade.csv',index=False)
    for name,obj in [('auditoria_antt.json',audit),('resumo_antt.json',summary),('descobertas_antt.json',facts)]:
        (REPORTS/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
    return outputs,audit,summary,facts


if __name__=='__main__':
    _,_,summary,facts=build()
    print(json.dumps(summary,indent=2,ensure_ascii=False))
