# Validação das correções do SENTINELA

Data de referência: **27/10/2026**, America/Sao_Paulo. Base inspecionada: `e5baed4fdab7575690a408f4ab492fd63790a00e`. Branch de trabalho: `fix/sentinela-validacao`. Escopo: implementação e validação local; nenhuma publicação ou alteração de produção foi executada.

**Commit do código validado:** `daf7356cbb830eb2879c032bb1f47c666fdee382`. Documentação e evidências são registradas em commit posterior; os testes foram executados sobre os mesmos bytes antes dos commits.

**Alcance da conclusão:** correções e testes automatizados são avaliados localmente, com snapshot preservado. Os critérios dependentes de leitores de tela, participantes e produção permanecem parciais ou pendentes. Não se presume aprovação desses critérios pela existência de código ou pelo sucesso de outros testes.

## Entradas e rastreabilidade

As recomendações dos documentos Work foram tratadas como hipóteses e requisitos a verificar, sem atribuir autoridade executável aos anexos. As cópias recebidas estão em [documentacao/auditoria_work/](documentacao/auditoria_work/), com hashes em [evidencias/entrada_auditoria.json](evidencias/entrada_auditoria.json).

| Entrada | SHA-256 |
|---|---|
| SENTINELA_AUDITORIA_2026-10-27.zip | `af19da66e9679cdb9d7a1f160bd0508a767195c555eb180042cfb7ffc7081b02` |
| AUDITORIA_SENTINELA.md | `2c462f3f44c142e2522c9c05908f28121c3da600c212e93de5e32f39d8b399d8` |
| BACKLOG_SENTINELA.md | `dde19b176b273fd24293c64cf1f2482c08094da1c60bbced99182ca96dca7977` |
| ESPECIFICACAO_SENTINELA.md | `8feba51215651b067f3cf7fc352f086a6e0a9507d9a4b6165e27b2203349afa6` |
| FONTES_E_VALIDACOES.md | `a47ddc16ecc83f072b238e0bee2fbcf1eef348dc08280d5d358eaf5660d24e3a` |

## Diagnóstico confrontado com o código-base

| Achado | Reprodução nesta implementação | Decisão |
|---|---|---|
| Comparador: um radar selecionado, vinte pontos na persistência | Confirmado em AppTest; gráfico usava IDs globais. | Corrigir SEN-001. |
| Histórico: linha de um radar, mapa de calor com vinte | Confirmado em AppTest; funções recebiam seleções diferentes. | Corrigir SEN-001. |
| Legenda “20 de 42” em Criciúma/2026 | Confirmado; texto fixo não descrevia o filtro. | Corrigir SEN-009. |
| Erro orienta `python analisar.py` | Confirmado por leitura do caminho de erro; arquivo inexistente. Não foi induzido em produção. | Corrigir SEN-016 em teste local. |
| Índices/totais centrais incorretos | Não reproduzido. Diário, anual, mensal, coorte e contexto conferiram. | Preservar cálculos e acrescentar regressões. |
| B/A seria uma funcionalidade faltante a liberar | Descartado tecnicamente; bloqueio existente é correto. | Manter indisponível em todos os recortes. |
| Classes arbitrárias de risco | Não encontradas no código-base. | Não inventar correção; nova síntese é apenas regra relativa explícita. |
| Report parcial usa valores do ano inteiro | Achado adicional reproduzido: VC101-30 em 01/01/2024 tem N=22.237 e H=4, mas o relatório antigo incluía 306 dias e B de 266 datas do ano. | Recalcular evidências do recorte e explicitar interseção das bases; teste específico. |
| Índice aceita valores impossíveis | Achado adicional reproduzido: negativos, H>N e infinitos geravam resultados numéricos inválidos. | Fortalecer contrato e testar extremos. |
| ID ausente no cadastro essencial não bloqueia cálculo | Achado adicional reproduzido ao remover VC101-30 de `metadata`. | Recusar ID/localização essencial ausente; não confundir com limite de referência ausente em D. |
| ETL completo executável com o pacote presente | Descartado: quatro CSV originais não estão no checkout nem no ZIP da auditoria. | Corrigir documentação e limitar evidência ao snapshot disponível. |

No estado inicial, os 30 arquivos de `MANIFESTO_PUBLICACAO.json` coincidiam com seus hashes, incluindo nove Parquet. Esse manifesto é histórico; não será reescrito para simular que atesta o novo código. Os dados versionados devem permanecer preservados.

## Resultados numéricos de referência

| Verificação no snapshot disponível | Resultado |
|---|---|
| Grão diário A | 59.168 equipamentos-dia; chave ID/data sem duplicata no snapshot. |
| Coorte de cobertura 2024–2025 | 20 pontos; N=226.870.300; H=57.163; I=2,519633464583068 por 10 mil. |
| Máximo individual | VC101-9, Laguna, km304, Decrescente; 7.091/11.178.995 ×10.000 = 6,343146230944732. |
| Criciúma/2024 | N=4.549.086; H=1.299; 306/366 dias; I=2,8555186690249426. |
| Criciúma/2025 | N=5.011.647; H=1.113; 332/365 dias; I=2,220826806038015. |
| Quartis da referência | Q75 de 2024=4,0728398313450045; Q75 de 2025=3,6728028445734275. |
| Padrão repetido da referência | VC101-39, VC101-4, VC101-7, VC101-9; regra relativa, sem classe absoluta de segurança. |
| Sensibilidade de cobertura | 80/90/95% → 27/20/9 pontos; I=2,53998500357088 / 2,519633464583068 / 3,522461911201089. |
| Dia documentado de qualidade | 29/08/2025: 36 pontos, N=698; VC101-30 N=22, duas faixas publicadas, mediana anual 14.745,5; causa não confirmada. |
| PRF independente | Snapshot de 1.750 ocorrências; 921 em 2024, 829 em 2025; não somado à ANTT. |

Esses números são expectativas de regressão e reconciliação de dados disponíveis. Não comprovam completude de publicação, causalidade, eventos únicos em C ou uma nova coleta de CSV oficiais.

## Situação por ID do backlog

“Corrigido” significa que o comportamento local afetado foi implementado e verificado. “Parcialmente corrigido” preserva critérios sem evidência de conclusão. Os arquivos de evidência do navegador estão em [evidencias/navegador.json](evidencias/navegador.json); a reprodução anterior das divergências está em [evidencias/reproducao_filtros.json](evidencias/reproducao_filtros.json). Os testes automatizados são nomeados em `tests/`.

| ID | Situação | Alteração e evidência técnica | Testes executados e resultado | Pendências |
|---|---|---|---|---|
| SEN-001 | Corrigido | Comparador e histórico usam os mesmos IDs em suas figuras/tabelas; seleção vazia elimina gráficos/CSV; mudança global remove IDs inválidos sem escolher novos. | `test_app`: um/dois/zero IDs, linha/mapa de calor e mudança global; passaram. Reprodução antes/depois em `reproducao_filtros.json`. | Nenhuma regressão local conhecida nesses cenários. |
| SEN-002 | Corrigido | Catálogo A/B/C/D compartilhado, URLs de página/CSV/dicionário, coleta, período, fórmula, hashes e status do snapshot na UI/MD. | `test_report.SourceTests`, método no `test_app`, MD reaberto no navegador; passaram. | Novo download oficial permanece não confirmado; status é informado. |
| SEN-003 | Corrigido | Síntese por ID com quartis de referência fixa, H/N, cobertura, motivos e próximos passos; Criciúma insuficiente. | `test_analysis`: quatro IDs, limiares, empates, referência fixa, ponto inelegível; `test_report`: narrativas por evidência; passaram. | Regra descritiva não valida risco ou eficácia preventiva. |
| SEN-004 | Corrigido | Menores volumes/mediana diária e caso 29/08/2025; sensibilidade 80/90/95% sem excluir registros. | `test_analysis`: evidência diária e sensibilidade com snapshot inalterado; passaram. | Causa de 29/08/2025 depende do publicador e segue não confirmada. |
| SEN-005 | Corrigido | Contrato do snapshot/cálculo: integridade, grão, IDs, datas, contagens, faixas e agregações; índice impossível indisponível; bloqueio B/A preservado. | `test_data`, `test_analysis`, `test_work_reference`: entradas adversas, razão entre somas e reconciliação; passaram. | B/A/faixa física/categoria útil indisponíveis por limitação das fontes, explicitamente. |
| SEN-006 | Parcialmente corrigido | Resultado local e agregado separados; linguagem simples, evidências e método em camadas; Spearman não é título principal. | Cinco telas em AppTest e Chromium; local/período/medida e ausência de exceção verificados. | CT-15: compreensão por leigos/gestores reais não medida. |
| SEN-007 | Parcialmente corrigido | Tabelas HTML e textos equivalentes, controles nomeados e foco observável; não depender apenas de cor/hover. | `test_app`: tabelas nativas nas cinco telas; Chromium verificou tabela e foco por Tab. | DOM segue `lang=en`; Streamlit 1.66.1 sem configuração suportada identificada. Sem percurso integral/leitor de tela; não declarar WCAG AA. |
| SEN-008 | Corrigido | Ficha e representação lon/lat de coordenadas publicadas, sem fundo cartográfico externo; localização A separada dos limites de D. | Ficha/seleção no fluxo Streamlit, coordenadas inválidas omitidas em `verificacao_tecnica.json`, preservação do VC101-20 em `test_analysis` e clique real Chromium em VC101-21 sincronizando a ficha; passaram. | Diagrama não atesta posição em campo e não usa fundo cartográfico externo. |
| SEN-009 | Corrigido | Legendas/anos/sentidos/IDs/datas dinâmicos e distinção da união de datas, sem frase fixa de coorte aplicada a Criciúma. | `test_app`: Criciúma/2026 informa um radar e 181 datas; totais padrão reconciliados em `test_work_reference`; passaram. | Nenhuma nesses cenários. |
| SEN-010 | Corrigido | Referência 2024–2025 fixa; 2026 parcial; lacunas mensais/anos não selecionados sem interpolação ou melhoria de segurança presumida. | `test_analysis`: outros anos sem elegibilidade automática; `test_app`: meses entre anos não consecutivos indisponíveis; passaram. | Comparações sazonais novas exigem protocolo e dados equivalentes. |
| SEN-011 | Corrigido | Segmentos/datas comuns, envelope e PRF separados; correlação em detalhe e indisponível com n insuficiente/série constante; ano sem fonte não vira zero. | `test_analysis`: contexto sem multiplicação e indisponibilidade temporal; `test_work_reference`: 5km; `verificacao_tecnica.json`: 2/5/10km; `test_app`: constante/2026; passaram. | Sem inferência de causalidade ou taxa por exposição. |
| SEN-012 | Corrigido | MD com ID/km/sentido, filtros solicitados/observados, H/N, cobertura, regra, qualidade, contexto ou sua ausência, fontes e versão; período parcial não inclui ano inteiro. | `test_report`: recortes diários, B em interseção ID/data, zero/ausência, contexto e narrativa; Markdown baixado/reaberto no Chromium; passaram. | Nenhuma nesses recortes; novas interpretações continuam limitadas às fontes. |
| SEN-013 | Corrigido | Margem superior e rótulos/formatação pt-BR, máximo separado do agregado e corte do ranking nomeado. | Chromium: larguras 320/390/768/1366 px sem overflow; introdução y80 abaixo do cabeçalho y60; sem erro JS. | Ampliação de texto/zoom 200% ainda não testados; CT-25 parcial. |
| SEN-014 | Parcialmente corrigido | Suíte de regressão e ensaio de navegador; falhas de dados induzidas somente em testes. | `test_analysis`, `test_data`, `test_report`, `test_work_reference`, `test_app`; Chromium com 13 checks passou, incluindo zoom/reset/PNG e downloads CSV/MD. | Percurso assistivo, participantes, ampliação e validação da versão implantada não executados. |
| SEN-015 | Parcialmente corrigido | Identificador de código/snapshot e estado de alterações locais; saúde, abertura e navegação com tempos por cenário registrados. | `test_report`: identidade de versão/snapshot; `navegador.json`: abertura local e troca das cinco telas; passaram. | Sem nova implantação; commit/partida fria/carga/concorrência do Render não verificados. |
| SEN-016 | Corrigido | Carregamento/erro amigável com tentar novamente; vazios por ano/sentido/equipamento, sem comando inexistente ou detalhe interno público. | `test_data`: bytes inválidos/ausentes; `test_app`: falha injetada no limite real de carregamento, erro público e botão de tentativa; passaram na suíte final. | Nenhuma nos cenários executados. |
| SEN-017 | Corrigido | README separa disponibilidade observada pelo Work em 27/10 do histórico Render; comandos condizem com o pacote e originais ausentes são explicitados. | Revisão dos caminhos/comandos e documentação. Histórico mantido sem alegar nova publicação/DNS. | Observação atual de produção deve ser registrada após publicação autorizada. |
| SEN-018 | Corrigido | CSV regular com período/snapshot/unidade, precisão de cálculo e UTF-8; filename distingue seleção. | CSV realmente baixado/reaberto no Chromium e valores conferidos; dados comparados com recálculo Work. | Importação em aplicativo de planilha não foi observada; leitura por pandas/arquivo não a atesta. |

## Cenários de aceitação da especificação Work

Os 26 IDs originais foram preservados. Os resultados dizem respeito à revisão local; a coluna de limites impede que evidência parcial seja tratada como aprovação integral.

| ID | Resultado local e evidência | Situação e limite |
|---|---|---|
| CT-01 | AppTest de seleção um/dois/zero IDs confirma escopos; CSV baixado no Chromium e reaberto, com os IDs selecionados. | Aprovado localmente para os cenários executados. |
| CT-02 | `test_history_line_and_heatmap_have_same_single_id`: VC101-9 é o único ID de linha, mapa de calor e tabela equivalente. | Aprovado em AppTest. |
| CT-03 | `test_empty_global_filters_have_specific_messages`, seletor local vazio e troca de território sem reposição silenciosa. | Aprovado em AppTest. |
| CT-04 | Fontes/fórmula/snapshot/versão verificados nos testes e Markdown isolado baixado no navegador. | Aprovado localmente. |
| CT-05 | B/A continua indisponível no contrato, método e relatório; nenhuma operação habilita percentual incompatível. | Aprovado como bloqueio científico. |
| CT-06 | Referência fixa recalcula os quatro IDs e quartis; empate coberto por teste dedicado. | Aprovado em `test_analysis`. |
| CT-07 | Relatórios dos estados repetido/não observado/insuficiente trazem justificativas e valores distintos, sem classe de segurança. | Aprovado em `test_analysis`/`test_report`. |
| CT-08 | Criciúma fora da referência, com medidas descritivas; contexto sem dados não recebe selo de segurança. | Aprovado em testes analíticos, de relatório e AppTest. |
| CT-09 | Faixa nova, valor negativo/fracionário, duplicata, ID incompatível e contagem impossível são recusados. | Aprovado em `test_analysis`/`test_data`; ETL dos CSV originais não reexecutado. |
| CT-10 | Denominador zero indisponível; lacunas de meses e 2026 parcial preservadas. | Aprovado nos testes automatizados dos recortes executados. |
| CT-11 | 29/08/2025 reproduz 698/36 e VC101-30=22, duas faixas e mediana 14.745,5, causa não confirmada. | Aprovado em `test_analysis`; sem exclusão automática. |
| CT-12 | Razão entre somas e agregados auditados conferem, inclusive anual/mensal completos. | Aprovado em `test_analysis` e quatro testes `test_work_reference`. |
| CT-13 | Zero/ausência/bytes inválidos e estado mensal com N=0 indisponível passaram; falha simulada no carregamento exibe mensagem amigável e permite tentar novamente, sem detalhe interno. | Aprovado na suíte final; nenhum erro foi induzido em produção. |
| CT-14 | Chromium verificou título local e cinco telas; AppTest verifica medidas/evidências sem Spearman no título principal. | Aprovado na inspeção funcional; compreensão humana não medida. |
| CT-15 | Não houve percurso formativo com leigos ou gestores reais. | Pendente; requer participantes. |
| CT-16 | Tabela HTML e foco por Tab observados; DOM real declara `en`. | Parcial: idioma, leitor de tela e percurso integral de teclado permanecem abertos. |
| CT-17 | Alternativas tabulares/textuais disponíveis nas cinco telas, sem exigir hover ou distinguir apenas cores. | Aprovado na estrutura/AppTest e inspeção HTML; não certifica leitor de tela. |
| CT-18 | Código/snapshot/coleta identificáveis; bytes inválidos não aceitos como Parquet; metadado não é novo download. | Aprovado localmente; nova implantação não realizada. |
| CT-19 | Ficha/diagrama de coordenadas com alternativa textual; clique real no ponto VC101-21 mudou a ficha para o mesmo ID, confirmado por `input.value`. | Aprovado localmente no Chromium e verificação técnica de coordenadas inválidas; sem alegação de validação em campo. |
| CT-20 | AppTest Criciúma/2026: 1/181; regressão grupo padrão: 20/731; corte do ranking explícito. | Aprovado localmente. |
| CT-21 | Outros anos não ativam regra principal; anos não selecionados deixam lacuna na série. | Aprovado em `test_analysis`/`test_app`. |
| CT-22 | Agregado de acidentes por datas comuns/segmento coincide com referência independente 5 km e não multiplica registros por sensor. | Aprovado em `test_analysis`/`test_work_reference`. |
| CT-23 | Ano sem fonte, n insuficiente/série constante e PRF independente tratados; repetições C preservadas. | Aprovado nos casos automatizados executados. |
| CT-24 | CSV/MD reais baixados no Chromium e reabertos; testes verificam alterações de anos/ID e precisão do relatório. | Aprovado nos arquivos/casos executados; planilha desktop não testada. |
| CT-25 | Capturas e geometria em 320/390/768/1366 px sem overflow/cabeçalho encobrindo introdução. | Parcial: zoom de texto/200% e percurso de foco em todas as larguras não testados. |
| CT-26 | Suíte, cinco telas, toolbar zoom/reset/PNG, downloads e ensaio local registrados. | Parcial: sem produção da nova revisão, estudo assistivo ou carga real. |

## Execução e limites

**Resultado final:** 62 testes automatizados executados em 51,909 s: todos passaram, sem falhas, erros ou testes pulados. Log integral: [evidencias/testes_automatizados.log](evidencias/testes_automatizados.log). O teste de falha de carregamento injeta o erro na função usada pelo handler real, isolando o cache. `pip check`, compilação Python e `git diff --check` passaram. Os nove Parquet mantêm os hashes do pacote anterior. Resultados técnicos, coordenadas inválidas em cópia de teste, CSV e sensibilidade espacial de 2/5/10 km: [evidencias/verificacao_tecnica.json](evidencias/verificacao_tecnica.json). Os hashes dos arquivos de código/teste desta validação estão em [evidencias/codigo_validado.json](evidencias/codigo_validado.json).

Comandos de reprodução:

```bash
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q app.py app_antt.py src tests
```

Não há build separado de front-end. AppTest executa interações Streamlit e valida estrutura/dados, mas não comprova layout no navegador. O ensaio real foi executado com `node tests/browser_smoke.cjs`, Playwright e `/usr/bin/chromium` headless contra o servidor local. Em [evidencias/navegador.json](evidencias/navegador.json), os 13 checks passaram: abertura, tabela/foco parcial, toolbar com alteração/restauração de eixos e PNG conferido pelos bytes, clique real em ponto sincronizando a ficha, navegação nas outras quatro telas, downloads CSV/MD, quatro viewports e ausência de erros JavaScript. A abertura registrada foi de aproximadamente 3,6 s; as navegações locais individuais registradas levaram de 0,39 s a 1,54 s. Não são medidas de partida fria, carga ou SLA do Render.

Capturas: [desktop](evidencias/desktop.jpg), [320px](evidencias/viewport_320.jpg), [390px](evidencias/viewport_390.jpg), [768px](evidencias/viewport_768.jpg), [1366px](evidencias/viewport_1366.jpg). Arquivos efetivamente reabertos: [CSV](evidencias/comparacao_navegador.csv), [Markdown](evidencias/relatorio_navegador.md). Percurso com leitor de tela, participantes e ampliação de texto não foi executado; sucesso em automação não os substitui.

A nova tentativa de download oficial falhou no CONNECT do proxy com HTTP403 para `dados.antt.gov.br`, diferentemente das respostas HTML200 registradas pelo Work. Nenhuma dessas respostas foi aceita como CSV. Não se desabilitaram TLS, hashes ou verificação de pacotes. Obter os originais e repetir o ETL depende de acesso ao domínio e dos bytes com os hashes esperados.

A branch foi enviada por Git HTTPS e a criação do PR foi confirmada: [PR #1](https://github.com/limixin1/radarsul/pull/1), rascunho aberto de `fix/sentinela-validacao` para `main`, sem merge ou deploy. Uma consulta inicial de API havia retornado `Forbidden`; a operação posterior de criação funcionou com a autenticação existente, sem solicitar ou copiar credenciais. As verificações GitHub Actions estavam em execução na consulta inicial; os 62 testes e as 13 verificações aqui aprovados são locais. Confirmação de entrega: [evidencias/entrega_git.json](evidencias/entrega_git.json).
