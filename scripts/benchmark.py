"""Microbenchmark da camada de dados/exportação; não mede navegador ou rede."""
import json
from statistics import median
from time import perf_counter
from pathlib import Path
from src.data_package import validate
from src.query import query_tables,AREAS,PAGES,DIRECTIONS,source_result
from src.exports import metadata,markdown_report,bundle

def measure(fn,n=10):
    samples=[]
    for _ in range(n):
        s=perf_counter();fn();samples.append(perf_counter()-s)
    return {'n':n,'mediana_s':median(samples),'max_s':max(samples),'amostras_s':samples}

m,f,s=validate();ids=s['coorte_ids'];d=f['antt_diario'];meta=f['antt_equipamentos'];registry=m['cobertura']['trafego']
query=lambda:query_tables(d,meta,ids,[2024,2025],registry)
selected,eq,cov=query()
filters={'page':PAGES[0],'years':[2024,2025],'area':AREAS[0],'directions':DIRECTIONS,'city':'Todas as cidades','points':ids}
e=metadata(m,filters,ids,selected,[source_result('PRF',f['ocorrencias'],[2024,2025],m['cobertura']['prf'],'trecho integral')])
def export():
    doc=markdown_report(selected,eq,cov,e)
    return bundle(eq,cov,e,doc)
result={'ambiente':'Python 3.12.14 local; mesma máquina; execução sequencial; sem renderização, rede ou cache Streamlit','validacao_pacote':measure(validate,3),'consulta':measure(query),'exportacao':measure(export)}
print(json.dumps(result,indent=2,ensure_ascii=False))
