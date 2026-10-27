# SENTINELA — RadarSul

O SENTINELA é um MVP Python/Streamlit para explorar contagens publicadas de velocidade na BR-101 Sul de Santa Catarina e apoiar investigação preventiva. RadarSul é o domínio/nome de hospedagem; o produto continua sendo SENTINELA.

A medida disponível é `10.000 × soma das contagens A nas faixas acima de 120 km/h / soma de todas as contagens publicadas de A`, no mesmo ponto e período. Ela descreve registros publicados; não mede infrações legais, veículos únicos, probabilidade de acidente nem causalidade. A taxa entre possíveis infratores e tráfego **permanece indisponível**, porque as populações/faixas não são compatíveis.

## Desenvolvimento local

Requer Python **3.12.14**, conforme `render.yaml`. Não há banco de dados, serviço externo, chave de API ou migração para iniciar o painel. Use o checkout existente; uma tarefa em nuvem já é isolada e não precisa de um worktree adicional.

```bash
cd /workspace/radarsul
python3.12 -m venv .venv
PIP_CACHE_DIR=/workspace/.cache/pip .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true --browser.gatherUsageStats=false
```

Em outro terminal, verifique a saúde e execute os testes:

```bash
curl --fail http://127.0.0.1:8501/_stcore/health
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q app.py app_antt.py src tests
```

O endpoint de saúde responde `ok`. Ele não substitui o teste funcional das telas, filtros e exportações. Streamlit executa o Python diretamente; não há etapa de build de front-end separada.

O ensaio opcional em navegador usa Node, Playwright e Chromium já disponíveis no ambiente de validação, sem acrescentá-los às dependências do servidor. Com o servidor local em execução, rode `node tests/browser_smoke.cjs`. O executável padrão é `/usr/bin/chromium`; ajuste `SENTINELA_CHROMIUM` se necessário. O script escreve resultados, capturas e downloads em `evidencias/` e testa somente a instância local. Sem essas ferramentas, registre o teste como não executado; AppTest não o substitui.

## Dados e reprodução

O repositório inclui nove Parquet: snapshot ANTT tratado e contexto PRF independente. A aplicação lê arquivos locais; não atualiza fontes oficiais a cada visita. O manifesto de coleta, as fontes e os hashes históricos estão em `dados_brutos/coleta_20261026T224903Z.json` e [documentacao/FONTES_OFICIAIS.md](documentacao/FONTES_OFICIAIS.md).

Os quatro CSV originais ANTT, os ZIP originais PRF, notebooks e PDFs não estão neste checkout. A auditoria Work entregue em 27/10/2026 registra sua própria inspeção desses insumos; esse registro não equivale a uma nova inspeção dos originais nesta implementação. As novas tentativas de obtenção dos CSV foram negadas pelo proxy da rede. Os testes locais verificam integridade do snapshot, contratos e reconciliação dos agregados a partir dos Parquet.

`python -m src.antt` é a rotina de ETL e **exige os quatro CSV originais com os hashes do manifesto**. Não a execute como preparação do servidor nem sobre o snapshot versionado: ela escreve saídas. Para reproduzir todo o ETL, use uma cópia descartável com esses insumos e compare as saídas, sem substituir silenciosamente dados oficiais por respostas HTML ou snapshots novos.

## Engenharia e revisão

- [Plano de correções](PLANO_CORRECOES_SENTINELA.md): prioridades e dependências.
- [Changelog](CHANGELOG_SENTINELA.md): alterações e decisões técnicas.
- [Validação](VALIDACAO_SENTINELA.md): situação dos SEN-001–018 e CT-01–26, evidências e limites.
- [Pendências](PENDENCIAS_SENTINELA.md): somente o trabalho ainda não concluído.
- [Publicação](PUBLICACAO_SENTINELA.md): procedimento para a versão revisada, sem deploy automático.
- [Auditoria recebida](documentacao/auditoria_work/AUDITORIA_SENTINELA.md), [backlog](documentacao/auditoria_work/BACKLOG_SENTINELA.md), [especificação](documentacao/auditoria_work/ESPECIFICACAO_SENTINELA.md) e [fontes da auditoria](documentacao/auditoria_work/FONTES_E_VALIDACOES.md): entradas preservadas; recomendações foram confrontadas com código e dados disponíveis.

## Publicação e histórico

A auditoria independente de **27/10/2026** registrou resposta de `https://radarsul.site/` e navegação nas cinco telas. É uma observação datada da versão anterior, sem atestar o commit de produção ou a configuração atual do Render/DNS. Esta implementação não publica mudanças nem altera serviços ou DNS.

`VERIFICACAO_PUBLICACAO.json` e `MANIFESTO_PUBLICACAO.json` são registros históricos do pacote anterior. Seus estados e hashes não atestam os novos arquivos de código desta branch; os hashes dos Parquet preservados continuam sendo usados como referência de integridade do snapshot. O procedimento de revisão/publicação está em [PUBLICACAO_SENTINELA.md](PUBLICACAO_SENTINELA.md).
