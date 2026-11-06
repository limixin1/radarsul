# Instruções do SENTINELA

## Escopo e ambiente

- Python de produção: 3.12.14 (`render.yaml` e `.python-version`). Dependências em `requirements.txt`; validação em `requirements-dev.txt`.
- Iniciar: `python -m streamlit run app.py --server.port=8501 --server.headless=true`.
- Validar: `python -m src.data_package validate`, `python -m pytest -q`, `python -m compileall -q app.py app_antt.py src tests`. Ensaios locais: `python scripts/validate_local.py` (servidor em 127.0.0.1:8502) e `PYTHONPATH=. python scripts/benchmark.py`; não executar carga em produção.
- Reconstruir em diretório isolado: `python -m src.rebuild --raw-zip _contexto/SENTINELA_bases_ANTT.zip --output /tmp/sentinela-rebuild`. Nunca reconstruir sobre o snapshot de referência sem comparação e revisão.
- Trabalhar na branch `correcao/sentinela-auditoria`. Preparar PR para main; merge, deploy, DNS, plano e recursos externos ficam para etapa posterior.

## Integridade e significado

- Índice = soma das contagens acima de 120 km/h / soma de contagens da **mesma base A, pontos e período** × 10.000. Não usar média de índices.
- Publicação ausente não é zero observado. Cobertura por fonte deve acompanhar valores e arquivos exportados, preservando anos solicitados sem cobertura.
- Comparabilidade exige pelo menos 90% dos dias de cada ano calendário solicitado; anos oficialmente parciais são exploratórios. Publicação não comprova operação ou completude diária.
- Preservar bloqueio B/A, acidentes ANTT e PRF separados, repetições ANTT sem ID e segmentos disjuntos com dias comuns. Não inferir causalidade, infração, veículos únicos ou previsão.
- Não mudar Parquet para satisfazer testes. Preservar hashes, proveniência, manifesto e comparação antes/depois. Publicar dados como conjunto consistente, nunca substituindo tabelas individuais em execução.
- Não versionar segredos, ambientes virtuais, CSV brutos extraídos ou arquivos temporários. O ZIP fornecido fica em `_contexto`; não extraí-lo na inicialização.

## Entrega e validação

- Prompt integral e auditoria histórica em `_contexto`; revalidar achados na versão atual.
- Manter `documentacao/MATRIZ_F01_F24.md` e evidências de execução. Distinguir implementação, testes executados e validações pendentes.
- Usar AppTest para comportamento; navegador real para interface, teclado e downloads. Teste de viewport não comprova teste em celular ou leitor de tela.
- Mensagens públicas sem stack traces e caminhos; erros técnicos somente no log. Validar entradas URL e invalidar cache pela identidade do pacote.
- Não declarar aprovação de participantes, segurança, acessibilidade ou capacidade sem evidência. Não alterar acessos administrativos ou produção sem autorização específica.
