"""Regressão de isolamento e invalidação do cache de consulta."""
from app_antt import consult


def test_cached_queries_are_copied_and_versioned(package, monkeypatch):
    import app_antt
    manifest,frames,summary=package
    calls=[]
    def loaded(identity):
        calls.append(identity)
        return manifest,frames,summary
    monkeypatch.setattr(app_antt,'load',loaded)
    consult.clear()
    ids=tuple(summary['coorte_ids'])
    try:
        first=consult(('snapshot-a',),ids,(2024,2025))
        assert first[0].passagens.sum()==226870300
        first[0].loc[:,'passagens']=0
        again=consult(('snapshot-a',),ids,(2024,2025))
        assert again[0].passagens.sum()==226870300
        assert len(calls)==1
        consult(('snapshot-b',),ids,(2024,2025))
        assert len(calls)==2
    finally:consult.clear()
