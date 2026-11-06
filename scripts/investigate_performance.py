"""Mede sessões locais e recursos; não é teste de navegador ou da hospedagem."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from time import perf_counter
from probe_session import query


def resources():
    memory={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key,value=line.split(':',1)
        if key in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:memory[key+'_kib']=int(value.split()[0])
    return {'cpu_logicas':os.cpu_count(),'carga_1_5_15min':os.getloadavg(),**memory}


async def batch(count,url):
    samples=[];start=perf_counter()
    tasks=[asyncio.create_task(query(url)) for _ in range(count)]
    while not all(t.done() for t in tasks):
        samples.append({'segundos':perf_counter()-start,**resources()})
        await asyncio.sleep(.25)
    results=await asyncio.gather(*tasks)
    for row in results:row.pop('session_id',None)
    assert all(not r['erros'] and r['script_concluido'] for r in results)
    assert all(r['metricas'][0]['value']=='2,520' for r in results)
    assert all(d['status']==200 for r in results for d in r['downloads'])
    return {'sessoes':count,'recursos_amostrados':samples,'resultados':results}


async def run(url):
    return [await batch(count,url) for count in [1,5,10]]


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--url',default='ws://127.0.0.1:8502/_stcore/stream');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    record={'gerado_utc':datetime.now(timezone.utc).isoformat(),'ambiente':'Loopback Linux; cliente e servidor na mesma máquina compartilhada; sem navegador. Downloads em threads para não bloquear observação dos pares. Limites cgroup não disponíveis neste host.','lotes':asyncio.run(run(a.url))}
    a.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
