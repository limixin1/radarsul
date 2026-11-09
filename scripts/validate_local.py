"""Aceitação de sessões/arquivos somente em loopback; sem renderizador de navegador."""
import asyncio
import json
from pathlib import Path
from probe_session import query, main

async def validate():
    out=Path('documentacao/evidencias')
    url='ws://127.0.0.1:8502/_stcore/stream'
    single=await query(url)
    assert not single['erros'] and single['metricas'][0]['value']=='2,520'
    out.joinpath('sessao-local-final.json').write_text(json.dumps({k:v for k,v in single.items() if k!='session_id'},ensure_ascii=False,indent=2))
    reconnect=await query(url,existing=single['session_id'])
    assert reconnect['session_id']==single['session_id'] and not reconnect['erros']
    out.joinpath('reconexao-local.json').write_text(json.dumps({k:v for k,v in reconnect.items() if k!='session_id'}|{'mesma_sessao_confirmada':True},ensure_ascii=False,indent=2))
    for count in [5,10]:
        sessions=await main(count,url)
        assert all(not s['erros'] and s['metricas'][0]['value']=='2,520' for s in sessions)
        assert all(d['status']==200 and d['bytes']>0 for s in sessions for d in s['downloads'])
        out.joinpath(f'sessoes-{count}-final.json').write_text(json.dumps([{k:v for k,v in row.items() if k!='session_id'} for row in sessions],ensure_ascii=False,indent=2))
    print('Sessão, reconexão, 5 e 10 sessões e downloads HTTP válidos. Não mede renderização.')
if __name__=='__main__':asyncio.run(validate())
