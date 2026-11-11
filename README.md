# SENTINELA — consultas históricas da BR-101/SC

O SENTINELA permite localizar pontos por cidade, quilômetro e sentido, consultar contagens publicadas nas faixas de velocidade, verificar cobertura e exportar uma consulta rastreável. O índice é a razão entre contagens acima de 120 km/h e todas as contagens da **mesma base de tráfego**, multiplicada por 10.000. Não estima risco de acidente, veículos únicos ou autuações.

A `main` contém o piloto **2.1.0**, com o snapshot `2026-10-26.1`. O [site público](https://radarsul.site/) usa o commit `38987b0`, publicado em 09/11/2026. O [registro da publicação](documentacao/PUBLICACAO_2026-11-09.md) descreve o que foi verificado e os limites do piloto. A [matriz F01–F24](documentacao/MATRIZ_F01_F24.md) reúne as evidências e pendências.

O mapa interativo, o modo Satélite e as fichas preventivas da versão 2.2.0 estão em revisão no [PR #3](https://github.com/limixin1/radarsul/pull/3).

## Executar e validar

Use Python **3.12.14**, a versão configurada em `render.yaml` e `.python-version`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m src.data_package validate
python -m pytest -q
python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8502 --server.headless=true
```

Confira a versão com `python --version` no ambiente virtual. Em produção, use `requirements.txt`. O arquivo `requirements-dev.txt` inclui também as ferramentas de teste e de análise de dependências.

```bash
python -m compileall -q app.py app_antt.py src tests
python -m pip_audit
PYTHONPATH=. python scripts/benchmark.py
python scripts/probe_session.py --sessions 1
```

O último comando exige o servidor local em 8502 e verifica uma sessão WebSocket e downloads HTTP. Aceita 1, 5 e 10 sessões **somente em loopback**, para não gerar carga em produção. Não mede renderização, acessibilidade, mobile ou retomada do Render. Execute sem outros ensaios concorrentes e registre memória e condições.

## Dados e limites

- Tráfego ANTT: inventário de 01/01/2022 a 30/06/2026. Possíveis infratores: inventário de 30/12/2022 a 02/06/2026, em base separada; taxa B/A permanece bloqueada.
- Acidentes ANTT: inventário de 01/05/2021 a 31/12/2025. PRF deste snapshot: arquivos anuais 2024 e 2025. Indisponibilidade em outros anos significa falta **nesta instalação**, mesmo que o publicador já ofereça arquivos adicionais.
- Períodos e notas constam no manifesto tratado. O intervalo do inventário não certifica completude de acidentes. Primeira/última ocorrência não comprovam cobertura contínua.
- Ranking anual: ≥90% de dias com publicação em **cada ano completo solicitado**, denominador positivo. 2026 é exploratório. A tabela apresenta cobertura do calendário e do intervalo declarado da fonte. Publicação não comprova operação ou completude diária.
- Histórico: índice oculto no gráfico quando há menos de 80% dos dias do mês. A tabela fornece contagens e cobertura para inspeção; ausência não vira zero.
- O grupo histórico tem 20 pontos em 2024–2025; Criciúma não satisfaz essa cobertura nos dois anos e pode ser consultada em Todos os equipamentos. Áreas e sentidos são mostrados junto aos resultados.
- Acidentes ANTT sem ID inequívoco mantêm repetições. ANTT e PRF não são somados. Segmentos disjuntos de 5 km usam apenas dias em que todos os pontos selecionados do segmento publicaram. Envelope ANTT e trecho PRF integral são contextos distintos.
- Cadastro de junho de 2026 não reconstrói limites históricos. Não estimar velocidade média por pontos médios nem interpretar correlação como causalidade, proteção ou previsão.

## Reprodução e restauração

O [kit bruto fornecido](_contexto/SENTINELA_bases_ANTT.zip) contém quatro CSV ANTT, dois ZIP PRF e manifestos. A [especificação de correção](_contexto/Requisitos_Correcao_SENTINELA_2026-11-05.md) e a [auditoria histórica convertida](_contexto/Auditoria_Produto_SENTINELA_2026-11-02.md) permanecem no contexto. Os comandos de trabalho e os critérios de integridade estão no [guia de desenvolvimento](documentacao/GUIA_DESENVOLVIMENTO.md).

```bash
python -m src.rebuild --raw-zip _contexto/SENTINELA_bases_ANTT.zip --output /tmp/sentinela-rebuild
cat /tmp/sentinela-rebuild/comparacao.json
python -m src.data_package validate --root /tmp/sentinela-rebuild
```

Use saída nova e vazia. Não reconstrua sobre o conjunto em uso. O comando verifica os hashes brutos, executa `src.antt.build`, reconstrói PRF e compara os nove Parquet com a referência. A rotina `python -m src.antt` exige os quatro CSV e `coleta_20261026T224903Z.json` em `dados_brutos` e grava produtos e relatórios locais. O comando de reprodução acima mantém essas saídas fora do conjunto em uso.

Uma mudança legítima de dados requer revisão, nova versão e manifesto gerado **depois** da comparação. `python -m src.data_package manifest --root DIRETORIO` é uma ação de manutenção, não uma forma de ignorar corrupção. O build valida o manifesto já versionado; não gera hashes novos para aceitar arquivos desconhecidos.

A restauração usa o conjunto inteiro de uma revisão conhecida: código, `dados_tratados`, `relatorios` e manifesto juntos. Instale dependências, valide contrato, execute testes, abra a consulta padrão e exporte. Para produção, veja [operação e rollback](documentacao/OPERACAO.md). O health check do Streamlit comprova resposta do processo; não substitui integridade analítica.

## Estrutura e manutenção

`src/antt.py` preserva a transformação e os indicadores originais. `src/query.py` reúne seleção, cobertura e rótulos; `src/data_package.py`, o contrato; `src/prf.py` e `src/rebuild.py`, reprodução; `src/exports.py`, rastreabilidade. `src/antt_charts.py` gera figuras; `app_antt.py` compõe as cinco páginas. `src/antt_report.py` mantém compatibilidade de chamadas anteriores.

`dados_tratados/manifesto.json` inclui hashes, esquemas, proveniência, períodos e condições consultadas. Os [recursos oficiais e condições de reutilização](documentacao/FONTES_OFICIAIS.md) distinguem coleta do snapshot e atualização atual do catálogo. CSV brasileiro usa UTF-8 BOM, `;` e vírgula decimal; o ZIP oferece também CSV técnico, relatório e metadados. Precisão numérica é preservada. As URLs exportadas identificam uma consulta; conferir versão antes de comparar arquivos.

A [CI](.github/workflows/validacao.yml) valida o pacote, compila os módulos Python, executa os testes e verifica as dependências. O [procedimento de publicação](documentacao/OPERACAO.md#procedimento-de-publicação) reúne as verificações antes de incorporar ou implantar uma revisão.

Ao relatar um problema, informe página, filtros e versão. Omita dados pessoais e credenciais. O repositório pertence a `limixin1`. O projeto ainda precisa definir responsáveis por atualização, atendimento e disponibilidade. [Relatar um problema](https://github.com/limixin1/radarsul/issues/new)
