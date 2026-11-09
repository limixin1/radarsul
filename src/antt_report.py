"""Compatibilidade para chamadas antigas; relatório usa a camada comum de exportação."""
from src.data_package import validate
from src.exports import metadata, markdown_report
from src.query import query_tables, source_result, PAGES

def report(daily, metadata_table, annual, possible, selection='Seleção do usuário', requested_years=None):
    if daily.empty:return '# SENTINELA\n\nSem publicações para os filtros. Nenhum indicador calculado.'
    manifest,frames,_=validate(allow_missing_prf=True)
    years=list(requested_years) if requested_years is not None else sorted(map(int,daily.ano.unique()))
    ids=daily.identificador.unique().tolist()
    selected,eq,cov=query_tables(daily,metadata_table,ids,years,manifest['cobertura']['trafego'])
    filters={'page':PAGES[4],'area':selection,'city':'Todas as cidades','years':years,'directions':sorted(metadata_table.loc[metadata_table.identificador.isin(ids),'sentido'].unique()),'points':ids}
    # O relatório legado não recebia recorte espacial de acidentes; não inventar um.
    sources=[source_result('ANTT',None,years,manifest['cobertura']['antt'],'contexto não solicitado nesta chamada'),source_result('PRF',None,years,manifest['cobertura']['prf'],'contexto não solicitado nesta chamada')]
    return markdown_report(selected,eq,cov,metadata(manifest,filters,ids,selected,sources),possible.loc[possible.identificador.isin(ids)&possible.ano.isin(years)])
