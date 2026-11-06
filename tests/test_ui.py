import json
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from config import ROOT
from src.query import PAGES, AREAS, parse_url, url_state
from src.antt_charts import persistence_data, correlation, monthly_grid

@pytest.fixture
def app():return AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()


def test_five_pages(app):
    for page in PAGES:
        app.radio(key='page').set_value(page).run()
        assert not app.exception
        assert app.get('download_button')
    assert '2,520' in '\n'.join(x.value for x in app.markdown)


def test_comparison_selection_and_empty(app):
    app.radio(key='page').set_value(PAGES[1]).run()
    app.multiselect(key='points').set_value(['VC101-9']).run()
    assert not app.exception
    assert len(app.get('plotly_chart'))==0
    assert set(app.dataframe[0].value['Equipamento'])=={'VC101-9'}
    assert 'um ponto' in '\n'.join(i.value for i in app.info)
    app.multiselect(key='points').set_value([]).run()
    assert not app.exception and len(app.get('plotly_chart'))==0 and len(app.get('download_button'))==0
    assert 'Nenhum equipamento' in app.info[0].value


def test_history_uses_identical_selection(app):
    app.radio(key='page').set_value(PAGES[2]).run()
    app.multiselect(key='points').set_value(['VC101-9']).run()
    assert not app.exception
    specs=[json.loads(x.proto.spec) for x in app.get('plotly_chart')]
    assert len(specs)==2
    assert len(specs[0]['data'])==1 and specs[1]['data'][0]['y']==['VC101-9']
    app.multiselect(key='points').set_value([]).run()
    assert len(app.get('plotly_chart'))==0 and not app.get('download_button')

@pytest.mark.parametrize('years,phrase',[([2026],'sem cobertura do período'),([2022],'sem cobertura do período'),([2023],'sem cobertura do período'),([2025,2026],'cobertura parcial')])
def test_source_states_in_app(app,years,phrase):
    app.radio(key='page').set_value(PAGES[3]).run()
    app.multiselect(key='years').set_value(years).run()
    assert not app.exception
    text='\n'.join(x.value for x in app.markdown)
    assert phrase in text
    if years==[2026]:assert '0 registros publicados' not in text and text.count('Indisponível')>=2


def test_empty_filters_and_reset(app):
    app.multiselect(key='years').set_value([]).run()
    assert 'Nenhum ano' in app.info[0].value and not app.get('download_button')
    app.button[0].click().run()
    assert app.multiselect(key='years').value==[2024,2025]
    app.multiselect(key='directions').set_value([]).run()
    assert 'Nenhum sentido' in '\n'.join(x.value for x in app.info)


def test_shared_url_new_session_isolation(package):
    _,f,_=package
    state={'pagina':PAGES[2],'anos':['2022'],'area':AREAS[1],'pontos':['VC101-28'],'sentidos':['Crescente'],'cidade':'Todas as cidades','v':'1'}
    a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60);a.query_params=state;a.run()
    assert not a.exception
    assert a.multiselect(key='years').value==[2022] and a.multiselect(key='points').value==['VC101-28']
    a.radio(key='page').set_value(PAGES[1]).run()
    b=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60);b.query_params=dict(a.query_params);b.run()
    assert not b.exception and b.multiselect(key='points').value==['VC101-28']
    clean=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert clean.multiselect(key='years').value==[2024,2025] and len(clean.multiselect(key='points').value)==20
    out,notes=parse_url({'anos':['2026','2026','2099'],'pagina':['old','old'],'pontos':['gone'],'x':['bad']},f['antt_equipamentos'])
    assert out['years']==[2026] and out['points']==[] and len(notes)>=3


def test_undefined_correlation_and_missing_months(package):
    _,f,_=package
    p=persistence_data(f['antt_anual'],['VC101-9'])
    assert correlation(p[['ano_2024','ano_2025']]) is None
    assert correlation(pd.DataFrame({'a':[1,1,1],'b':[3,4,5]})) is None
    grid=monthly_grid(f['antt_mensal'],['VC101-28'],[2022])
    assert grid.indice_exibido.isna().all()


def test_city_search_and_insufficient_coverage(app):
    app.selectbox(key='area').set_value(AREAS[1]).run()
    app.selectbox(key='city').set_value('Içara').run()
    app.multiselect(key='years').set_value([2022]).run()
    app.multiselect(key='points').set_value(['VC101-28']).run()
    assert not app.exception
    text='\n'.join(i.value for i in app.info)
    assert 'Nenhum ponto elegível' in text
    assert app.dataframe[0].value['Dias publicados'].iloc[0]=='3'
    assert app.dataframe[0].value['Índice por 10 mil contagens'].iloc[0]=='80,466'


def test_local_areas_directions_and_recovery(app):
    for area in AREAS:
        app.selectbox(key='area').set_value(area).run()
        for directions in [['Crescente'],['Crescente','Decrescente']]:
            app.multiselect(key='directions').set_value(directions).run()
            assert not app.exception
    app.selectbox(key='area').set_value(AREAS[0]).run()
    app.selectbox(key='city').set_value('Criciúma').run()
    assert not app.get('download_button')
    app.button(key='all_city').click().run()
    assert app.selectbox(key='area').value==AREAS[1]
    assert 'VC101-30' in app.multiselect(key='points').value


def test_operational_error_is_publicly_contained(monkeypatch):
    import app_antt
    def broken():raise FileNotFoundError('/private/server/dados.parquet')
    monkeypatch.setattr(app_antt,'token',broken)
    a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not a.exception and 'Não foi possível validar' in a.error[0].value
    public='\n'.join(x.value for x in a.markdown)+a.error[0].value
    assert '/private' not in public and 'analisar.py' not in public


def test_missing_prf_block_remains_visible(monkeypatch,package):
    import app_antt
    m,f,s=package
    frames={k:v for k,v in f.items() if k!='ocorrencias'}
    monkeypatch.setattr(app_antt,'load',lambda _: (m,frames,s))
    a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60)
    a.query_params={'pagina':PAGES[3],'anos':['2024','2025']};a.run()
    assert not a.exception
    text='\n'.join(x.value for x in a.markdown)
    assert 'PRF' in text and 'fonte indisponível' in text
