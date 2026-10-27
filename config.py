"""Configuração explícita e fontes oficiais. Não contém credenciais."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'dados_brutos'
PROCESSED = ROOT / 'dados_tratados'
REPORTS = ROOT / 'relatorios'
KM_MIN, KM_MAX = 244.680, 465.100
YEARS = (2024, 2025)
PRF_PAGE = 'https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf'
PRF_FILES = {2024: '14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO', 2025: '1-G3MdmHBt6CprDwcW99xxC4BZ2DU5ryR'}
ANTT = {
 'volume-radar-viacosteira.csv': ('269aebaa-05e7-4d76-a105-408f12bf4094','2af017dc-edde-4501-9c10-ae1f0da461f6'),
 'quantidade-possiveis-infratores-viacosteira.csv': ('c3844135-55c4-43b3-88a0-247f6ff9ca67','121be806-df31-4ebb-aa2d-8caa5f102226'),
 'demostrativo_acidentes_viacosteira.csv': ('8a57b663-2302-405a-bf5a-cbece12c13d1','05e0cbd2-2acb-4b81-8124-3c28a3030234'),
 'dados-dos-radares6_2026.csv': ('79d287f4-f5ca-4385-a17c-f61f53831f17','64044fcf-756e-4fd1-9cb2-a6037785829d')
}
