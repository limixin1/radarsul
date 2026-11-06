import io
import itertools
import json
import shutil
import zipfile
import numpy as np
import pandas as pd
import pytest
from config import ROOT
from src.antt import weighted_index, context_table
from src.data_package import validate, token, MANIFEST, digest
from src.query import query_tables, area_ids, source_result, AREAS, YEARS, DIRECTIONS
from src.exports import metadata, csv_bytes, bundle, markdown_report


def test_historical_values_and_icarra(package):
    m,f,s=package
    d,eq,cov=query_tables(f['antt_diario'],f['antt_equipamentos'],s['coorte_ids'],[2024,2025],m['cobertura']['trafego'])
    assert len(f['antt_equipamentos'])==42 and len(eq)==20
    assert int(d.passagens.sum())==226870300 and int(d.altas.sum())==57163
    assert weighted_index(d.altas.sum(),d.passagens.sum())==pytest.approx(2.519633464583068,abs=1e-12)
    assert eq.iloc[0].identificador=='VC101-9' and eq.iloc[0].por_10_mil==pytest.approx(6.343146230944732,abs=1e-12)
    assert eq.elegivel.all()
    _,i,c=query_tables(f['antt_diario'],f['antt_equipamentos'],['VC101-28'],[2022],m['cobertura']['trafego'])
    assert i.iloc[0].dias==3 and i.iloc[0].altas==58 and i.iloc[0].passagens==7208
    assert i.iloc[0].por_10_mil==pytest.approx(80.4661487236404)
    assert not i.iloc[0].elegivel and c.iloc[0].cobertura_dias==pytest.approx(3/365)


def test_sources_no_false_zeros(package):
    m,f,_=package
    for source,key in [('antt','antt_acidentes'),('prf','ocorrencias')]:
        r=source_result(source,f[key],[2026],m['cobertura'][source],'trecho')
        assert r.quantidade is None and not r.anos_cobertos and 'sem cobertura' in r.situacao
        mixed=source_result(source,f[key],[2025,2026],m['cobertura'][source],'trecho')
        assert mixed.anos_solicitados==[2025,2026] and mixed.anos_cobertos==[2025] and mixed.situacao=='cobertura parcial'
        assert mixed.quantidade==len(f[key].loc[f[key].ano.eq(2025)])
    for year in [2022,2023]:assert source_result('PRF',f['ocorrencias'],[year],m['cobertura']['prf'],'trecho').quantidade is None
    assert source_result('PRF',None,[2024],m['cobertura']['prf'],'trecho').situacao=='fonte indisponível'
    zero=source_result('PRF',f['ocorrencias'].iloc[:0],[2024],m['cobertura']['prf'],'envelope')
    assert zero.quantidade==0 and 'consulta sem registros' in zero.situacao


def test_512_filter_states(package):
    m,f,s=package;populated=empty=0
    for n in range(32):
        years=[y for i,y in enumerate(YEARS) if n & (1<<i)]
        for area in AREAS:
            for mask in range(4):
                directions=[d for i,d in enumerate(DIRECTIONS) if mask & (1<<i)]
                ids=area_ids(f['antt_equipamentos'],s['coorte_ids'],area,directions)
                d,eq,c=query_tables(f['antt_diario'],f['antt_equipamentos'],ids,years,m['cobertura']['trafego'])
                assert set(d.identificador).issubset(ids) and set(d.ano).issubset(years)
                assert not eq.identificador.duplicated().any()
                if len(d):
                    populated+=1
                    assert d.passagens.sum()==eq.passagens.sum() and d.altas.sum()==eq.altas.sum()
                    assert len(c)==len(ids)*len(years)
                    assert set(c.identificador)==set(ids)
                else:empty+=1
    assert (populated,empty)==(341,171)


def test_partial_and_no_publication(package):
    m,f,s=package
    d,eq,c=query_tables(f['antt_diario'],f['antt_equipamentos'],s['coorte_ids'],[2026],m['cobertura']['trafego'])
    assert not eq.elegivel.any() and (c.dias_intervalo==181).all()
    assert (c.cobertura_intervalo>=c.cobertura_dias).all()
    assert np.isnan(weighted_index(0,0))
    t=f['antt_diario'].iloc[:1].assign(passagens=0,altas=0)
    _,eq,_=query_tables(t,f['antt_equipamentos'],t.identificador.tolist(),[int(t.ano.iloc[0])],m['cobertura']['trafego'])
    assert eq.por_10_mil.isna().all() and not eq.elegivel.any()


def test_context_conservation(package):
    m,f,s=package
    ctx=context_table(f['antt_diario'],f['antt_equipamentos'],f['antt_acidentes'],s['coorte_ids'])
    expected=f['antt_contexto_5km']
    pd.testing.assert_frame_equal(ctx,expected)
    assert ctx.registros_acidentes.sum() <= len(f['antt_acidentes'].loc[f['antt_acidentes'].ano.isin([2024,2025])])


def test_csv_roundtrip_and_bundle(package):
    m,f,s=package
    ids=['VC101-9'];years=[2025,2026]
    d,eq,c=query_tables(f['antt_diario'],f['antt_equipamentos'],ids,years,m['cobertura']['trafego'])
    source=source_result('PRF',f['ocorrencias'],years,m['cobertura']['prf'],'trecho integral')
    filters={'page':'Comparador de equipamentos','years':years,'area':AREAS[1],'directions':DIRECTIONS,'city':'Todas as cidades','points':ids}
    meta=metadata(m,filters,ids,d,[source]);doc=markdown_report(d,eq,c,meta)
    for brazil in [True,False]:
        data=csv_bytes(eq,meta,brazil)
        t=pd.read_csv(io.BytesIO(data),sep=';' if brazil else ',',decimal=',' if brazil else '.')
        assert t.municipio.iloc[0]==eq.municipio.iloc[0]
        assert t.por_10_mil.iloc[0]==pytest.approx(eq.por_10_mil.iloc[0],rel=1e-14)
        assert '2026' in t.anos_solicitados.iloc[0] and 'cobertura parcial' in t.cobertura_acidentes_json.iloc[0]
    with zipfile.ZipFile(io.BytesIO(bundle(eq,c,meta,doc))) as z:
        loaded=json.loads(z.read('metadados.json'))
        assert loaded['fontes_acidentes'][0]['anos_sem_cobertura']==[2026]
        assert len(z.namelist())==5 and 'Índice agregado' in z.read('relatorio.md').decode()

@pytest.fixture
def isolated(tmp_path):
    for folder in ['dados_tratados','relatorios','dados_brutos']:
        shutil.copytree(ROOT/folder,tmp_path/folder)
    return tmp_path

@pytest.mark.parametrize('case',['missing','corrupt','schema','summary','mixed'])
def test_bad_packages_rejected(isolated,case):
    target=isolated/'dados_tratados/antt_diario.parquet'
    if case=='missing':target.unlink()
    elif case=='corrupt':target.write_bytes(b'not parquet')
    elif case=='schema':
        d=pd.read_parquet(target).drop(columns='altas');d.to_parquet(target,index=False)
        # Mesmo hash atualizado não permite esquema diferente.
        p=isolated/MANIFEST;m=json.loads(p.read_text());m['arquivos']['dados_tratados/antt_diario.parquet']['sha256']=digest(target);p.write_text(json.dumps(m))
    elif case=='summary':
        p=isolated/'relatorios/resumo_antt.json';v=json.loads(p.read_text());v['coorte_altas']+=1;p.write_text(json.dumps(v))
        p=isolated/MANIFEST;m=json.loads(p.read_text());m['arquivos']['relatorios/resumo_antt.json']['sha256']=digest(isolated/'relatorios/resumo_antt.json');p.write_text(json.dumps(m))
    else:
        p=isolated/'dados_tratados/antt_anual.parquet';d=pd.read_parquet(p);d.loc[0,'passagens']+=1;d.to_parquet(p,index=False)
        manifest=isolated/MANIFEST;m=json.loads(manifest.read_text());m['arquivos']['dados_tratados/antt_anual.parquet']['sha256']=digest(p);manifest.write_text(json.dumps(m))
    with pytest.raises((ValueError,AssertionError)):validate(isolated)


def test_missing_prf_restore_and_cache_identity(isolated):
    original=token(isolated);p=isolated/'dados_tratados/ocorrencias.parquet';content=p.read_bytes();p.unlink()
    assert token(isolated)!=original
    _,f,_=validate(isolated,allow_missing_prf=True);assert 'ocorrencias' not in f
    with pytest.raises(ValueError):validate(isolated)
    p.write_bytes(content);validate(isolated)


def test_rebuild_prf_from_original_archives(tmp_path,package):
    from src.prf import build_prf
    raw=tmp_path/'raw';raw.mkdir()
    with zipfile.ZipFile(ROOT/'_contexto/SENTINELA_bases_ANTT.zip') as z:
        for name in ['manifesto_prf.json','datatran2024.zip','datatran2025.zip']:(raw/name).write_bytes(z.read(name))
    rebuilt,audit=build_prf(raw,tmp_path/'out')
    pd.testing.assert_frame_equal(rebuilt,package[1]['ocorrencias'])
    assert digest(tmp_path/'out/ocorrencias.parquet')==digest(ROOT/'dados_tratados/ocorrencias.parquet')
    assert [row['linhas_trecho'] for row in audit]==[921,829]
    assert sum(row['soma_pessoas_divergente'] for row in audit)==46
