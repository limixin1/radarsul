"""Teste sintético local do protocolo Streamlit; não substitui renderização no navegador."""
import argparse
import asyncio
import json
import time
import hashlib
import io
import zipfile
import urllib.request
from urllib.parse import urlencode
import websockets
from streamlit.proto.BackMsg_pb2 import BackMsg
from streamlit.proto.ForwardMsg_pb2 import ForwardMsg

async def query(url, params=None, existing=None):
    start=time.perf_counter();metrics=[];errors=[];downloads=[];session=None
    subprotocols=['streamlit'] if not existing else ['streamlit','unused',existing]
    async with websockets.connect(url,subprotocols=subprotocols,origin='http://127.0.0.1:8502',open_timeout=10,max_size=32*1024*1024) as ws:
        msg=BackMsg();msg.rerun_script.query_string=urlencode(params or {},doseq=True);msg.rerun_script.page_script_hash=''
        ws_start=time.perf_counter();await ws.send(msg.SerializeToString())
        while time.perf_counter()-start<45:
            raw=await asyncio.wait_for(ws.recv(),45)
            f=ForwardMsg();f.ParseFromString(raw)
            kind=f.WhichOneof('type')
            if kind=='new_session':session=f.new_session.initialize.session_id
            if kind=='delta' and f.delta.WhichOneof('type')=='new_element':
                el=f.delta.new_element;typ=el.WhichOneof('type')
                if typ=='metric':metrics.append({'label':el.metric.label,'value':el.metric.body})
                if typ=='exception':errors.append(el.exception.message)
                if typ=='download_button':downloads.append({'label':el.download_button.label,'url':el.download_button.url})
            if kind=='script_finished':break
        server_done=time.perf_counter()
        for download in downloads:
            response=urllib.request.urlopen('http://127.0.0.1:8502'+download['url'],timeout=10)
            body=response.read()
            download.update(status=response.status,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),content_type=response.headers.get('Content-Type'))
            if download['url'].endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(body)) as z:
                    download['arquivos']=z.namelist()
                    info=json.loads(z.read('metadados.json'));download['snapshot']=info['snapshot'];download['anos_solicitados']=info['filtros_solicitados']['years']
        return {'tempo_conexao_e_servidor_s':server_done-start,'tempo_execucao_e_transmissao_s':server_done-ws_start,'tempo_total_com_downloads_s':time.perf_counter()-start,'metricas':metrics,'erros':errors,'downloads':downloads,'session_id':session}

async def main(count,url):return await asyncio.gather(*(query(url) for _ in range(count)))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sessions',type=int,default=1);p.add_argument('--url',default='ws://127.0.0.1:8502/_stcore/stream');a=p.parse_args()
    if a.sessions not in [1,5,10] or not a.url.startswith('ws://127.0.0.1:'):raise SystemExit('Somente ensaio local controlado, 1/5/10 sessões.')
    print(json.dumps(asyncio.run(main(a.sessions,a.url)),ensure_ascii=False,indent=2))
