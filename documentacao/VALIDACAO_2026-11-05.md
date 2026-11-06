# Registro de validação da correção SENTINELA

Baseline limpa: `e5baed4fdab7575690a408f4ab492fd63790a00e`, branch local já existente `correcao/sentinela-auditoria`, remote `limixin1/radarsul`, sem AGENTS.md preexistente. `_contexto` estava vazio e excluído localmente do Git; os materiais foram copiados e explicitamente versionados, incluindo prompt integral e conversão textual da auditoria com seus links externos. Nenhuma melhoria posterior à auditoria foi revertida.

Data da execução: 05/11/2026, fuso America/Sao_Paulo. Host Linux, ambiente isolado `.venv312`, CPython **3.12.14**, sem substituir Python 3.12.3 do sistema/ambiente anterior. Diretas: pandas 2.2.3, numpy 2.3.5, scipy 1.17.0, plotly 7.1.0, streamlit 1.66.1, pyarrow 26.0.0. Lista instalada em `evidencias/ambiente-python31214.txt`. Python foi obtido por uv de distribuição CPython, dependências dos registros PyPI. Rede e porta local exigiram execução fora do sandbox; nenhum serviço externo foi criado.

A abertura inicial foi reproduzida por AppTest em 3.12.3 antes das alterações (11,286 s incluindo importações; os três totais de referência corretos). A abertura de uma porta de servidor dentro do sandbox falhou com `PermissionError`; o servidor completo foi iniciado em 127.0.0.1:8502 com 3.12.14 e verificado por sessões WebSocket e downloads HTTP. A abertura inicial **visual** não pôde ser verificada: o acesso ao navegador estava desativado.

## Resultados analíticos antes e depois

| Medida | Antes | Depois | Critério |
|---|---:|---:|---|
| Equipamentos com tráfego | 42 | 42 | Igual |
| Grupo histórico 2024–2025 | 20 | 20 | Igual |
| Contagens do grupo | 226.870.300 | 226.870.300 | Igual |
| Acima de 120 km/h no grupo | 57.163 | 57.163 | Igual |
| Índice ponderado por 10 mil | 2,519633464583068 | 2,519633464583068 | abs 1e-12 |
| Máximo padrão VC101-9 | 6,343146230944732 | 6,343146230944732 | abs 1e-12 |
| VC101-28 / 2022 | 58/7.208, três dias | Mesmos valores, exploratório | Apresentação corrigida |
| PRF no trecho | 1.750 | 1.750 | 921/2024 + 829/2025 |
| Produtos reconstruídos | 8 ANTT + PRF | Nove idênticos byte a byte | Referência preservada |

A apresentação muda: resultados de poucos dias ou de ano parcial deixam de disputar destaque anual; ausência de acidentes no snapshot vira indisponibilidade; todos os gráficos usam os pontos selecionados. Não há mudança artificial dos resultados para satisfazer testes.

## Matriz de aceitação executada

| Cenário | Esperado e observado | Ambiente/evidência | Achados |
|---|---|---|---|
| Padrão e cinco páginas | Sem exceção; agregado ponderado e arquivos presentes | AppTest, JUnit | F02,F05,F08,F09,F21 |
| 2026 isolado | ANTT e PRF indisponíveis; sem 0 factual por falta de período | Dados + AppTest | F01,F10 |
| 2022/2023 | PRF sem cobertura do snapshot; ANTT conforme intervalo | Dados + AppTest | F01 |
| 2025+2026 | Anos solicitados mantidos, PRF/ANTT acidentes parciais; exportação registra 2025 efetivo | Dados/AppTest/ZIP/CSV | F01,F11,F18 |
| Comparador 1/0 pontos | Tabela um ponto e sem correlação entre pontos; nenhum ponto remove gráficos/downloads | AppTest | F02,F10 |
| Histórico 1/0 pontos | Curva e matriz com o mesmo único ID; vazio orientado | Especificação Plotly inspecionada no AppTest | F02 |
| Içara 2022 | 3 dias, 58/7.208, 80,466; nenhum destaque anual elegível | Regressão + AppTest | F03 |
| Áreas/sentidos/cidades | Grupo/todos/Criciúma/entorno, um/ambos os sentidos e recuperação de cidade sem grupo | 512 estados de dados + AppTest | F05,F07,F10,F19 |
| Sem anos/sentidos/pontos | Mensagens distintas e reset funcional; sem exportação vazia | AppTest | F10,F11 |
| Denominador zero/variância nula | Índice indisponível e sem elegibilidade; correlação sem NaN útil | Dados/teste de gráficos | F02,F03,F10 |
| URL em nova sessão | Filtros reproduzidos, página preservada, desconhecidos/repetidos/antigos avisados, sessão nova isolada | AppTest; reload real pendente | F11,F23 |
| CSV/ZIP/Markdown | Round trip pt-BR/técnico, precisão, caracteres, cobertura e metadados; HTTP 200 com conteúdo | Teste de exportação + sessões sintéticas | F09,F18 |
| PNG e impressão | Código mantém PNG contextual e CSS de impressão | Sem execução no navegador; não aprovado | F04,F12,F13,F18 |
| Pacote inválido/restauração | Ausente/corrompido/esquema/resumo/mistura rejeitados; restauração e PRF ausente distinguida | Diretórios temporários + AppTest | F14,F15,F22 |
| Reprodução limpa | Nove Parquet idênticos; 46 flags originais PRF preservadas | `evidencias/reproducao.json`, `auditoria_prf.json`, teste PRF | F15,F16 |
| Cores/teclado/alternativas/viewports | Cores do projeto calculadas e tabelas HTML/resumos implementados; nenhuma inspeção efetiva de DOM/teclado/largura | `contraste-e-navegador.json`; Brave desativado | F04,F06–F08,F12,F13 |
| Saúde/carga/reconexão | Baseline publicada 200/ok; sessões/carga/reconexão da versão nova somente locais | JSON HTTP, sessões finais e benchmark | F20,F22,F23 |

Matriz histórica: **512 estados, 341 com dados e 171 vazios**. Conservação das somas, unicidade e joins verificados. Este ensaio não substitui UI nem concorrência. Testes isolados de integridade não alteram `dados_tratados` da referência.

## Evidências e limites

`evidencias/pytest.xml` contém o resultado final da suíte; falhas intermediárias de infraestrutura dos próprios testes (caminho relativo do AppTest e seleção incorreta de botão no teste) foram corrigidas e a suíte foi reexecutada. `git diff --check`, compilação e `python -m src.data_package validate` foram executados. O código passa a executar validação de contrato no build. Workflow de CI foi preparado; ativação e resultado remoto dependem do push/PR e estão registrados no próprio PR quando disponíveis.

`evidencias/dependencias_audit.json` documenta a consulta do pip-audit, sem vulnerabilidades conhecidas nos pacotes instalados. Busca dirigida não encontrou padrões de credenciais nos arquivos revisados. Não é teste de invasão nem revisão integral dos acessos. HTTPS/cabeçalhos de produção foram consultados por HTTP real; saúde não comprova os cálculos, e ausência de cabeçalho na amostra não demonstra todos os caminhos possíveis.

O acesso ao Brave foi tentado novamente após o usuário informar que o ativaria, mas `cua.getState` continuou sem navegadores e com “Local browser use is disabled in Work settings”. Não há capturas de desktop/móvel, medição de contraste composto, idioma efetivo do DOM, validação visual de PNG, teclado completo, zoom, leitor de tela, Chrome/Firefox ou aparelho real. Não foram usados outros meios de automação para contornar essa configuração.

Participantes reais não estavam disponíveis. `ACEITACAO_PESSOAS.md` entrega roteiro/formulário, sem simulação de resultados. Responsáveis por manutenção e alertas precisam ser nomeados. Não houve mudanças administrativas, ativação de monitor externo, teste de retomada Free, rollback real ou deploy da versão nova. O regulamento integral do hackathon não foi fornecido nesta entrega; conformidade não declarada.

## Execução final e tempos

Suíte final: **27 passed em 86,63 s**; zero falhas/erros no JUnit. Compilação, `git diff --check` e contrato aprovados. A execução de sessões começou após o término da suíte, com o servidor local já iniciado, sem outra carga deliberada desta tarefa. A máquina de uso compartilhado não é equivalente à instância Render.

| Medição | Amostra | Mediana | Máximo | Resultado |
|---|---:|---:|---:|---|
| Nova sessão local, conexão até término do script | 1 | 3,482 s | 3,482 s | Totais corretos; 4 arquivos HTTP 200 |
| Reconexão à mesma sessão local | 1 | 1,809 s | 1,809 s | Identidade da sessão confirmada; 4 arquivos HTTP 200 |
| Cinco sessões simultâneas locais | 5 | 6,075 s | 6,547 s | Sem erros; 20 arquivos HTTP 200 |
| Dez sessões simultâneas locais | 10 | 12,096 s | 12,606 s | Sem erros; 40 arquivos HTTP 200 |
| Contrato do pacote, sem cache Streamlit | 3 | 0,405 s | 0,413 s | Validação completa |
| Consulta de dados, sem renderização | 10 | 0,095 s | 0,208 s | Mesmo agregado |
| Geração de relatório/ZIP, sem rede | 10 | 0,077 s | 0,116 s | Conteúdo válido |

O tempo de sessão mede conexão/servidor/transmissão até `script_finished`, separando o tempo total que inclui downloads. Não mede desenho de tela, usabilidade nem primeira consulta **visualmente** útil. Os 68 downloads da rodada final foram conferidos por HTTP local; metadados/estrutura ZIP e hashes foram registrados. O PNG depende do frontend e não está incluído nessa contagem.

As metas propostas de 5 s para abertura, 2 s para interação e 5 s para exportação não estão certificadas no produto. As sessões simultâneas excederam 5 s. A camada de cálculo/exportação isolada é muito menor que o percurso completo, indicando contenção no caminho servidor/framework/transmissão e recursos compartilhados; não houve perfil suficiente para atribuir toda a diferença a um componente. Cache por pacote elimina releituras entre consultas e preserva isolamento, mas não garante capacidade. A troca de plano sem ensaio não resolveria essa lacuna. Repetir em homologação com memória observável, navegador, rede e disponibilidade definidos.

As primeiras amostras (`sessoes-5.json`/`sessoes-10.json`) coincidiram com outras validações e chegaram a ~23 s. Foram preservadas como evidência de contenção, sem misturar com a rodada final. `benchmark.json` é a primeira amostra; `benchmark-final.json` é a rodada sequencial final. A listagem externa de processos não forneceu memória útil nesta execução isolada; não se declara consumo de pico local ou capacidade de 512 MiB.
