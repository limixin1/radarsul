# Aceitação no navegador — 06/11/2026

Esta continuação substitui o bloqueio de acesso registrado na etapa 2. Não substitui os resultados históricos de dados, reprodução ou segurança. Código corrigido: `7396d0f`, descendente de `0f789ff`, branch `correcao/sentinela-auditoria`, PR #2. O worktree existente já continha ajustes em `app_antt.py`, `src/antt_charts.py` e capturas; todos foram preservados. A ponta remota foi reconferida como `0f789ff`, sem commit posterior a sobrescrever. O diretório principal permanece em checkout separado.

## Ambiente e identidade

CPython 3.12.14 restaurado no ambiente `.venv312`, dependências do projeto preservadas. Servidor de aceitação: `http://127.0.0.1:8506`, iniciado no worktree da branch com `python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8506 --server.headless=true --browser.gatherUsageStats=false`. Foi reiniciado após alterações de módulos para carregar efetivamente o código novo; URLs de mídia de uma instância encerrada não são persistentes. Snapshot `2026-10-26.1`; exports identificam `0f789ff+alterações-locais` antes do commit desta etapa.

Controle real por `mcp__cua_repl.js`, Brave, extensão/perfil disponível no inventário (browser 3). A sessão foi recuperada após as tentativas históricas bloqueadas. Não foi presumida indisponibilidade do Chrome a partir do Brave; o navegador efetivamente usado nesta aceitação foi o Brave. O servidor local é diferente do site público: deploy público reconfirmado via Render MCP nesta entrega em `e5baed4`, sem publicação desta branch. Nenhuma ação de merge, deploy, plano, DNS ou administração foi executada.

## Correções verificadas

- Preservado `theme=None` e cores explícitas dos eixos; texto das notas opaco no DOM, com cor `rgb(20,43,60)` e opacidade composta 1. Fundos inspecionados `#FAFBFC` e `#EEF3F5`: relações calculadas 14,07:1 e 13,03:1. Não é declaração de conformidade integral de acessibilidade.
- Ícones Plotly antes tinham preenchimento translúcido; agora `rgb(20,43,60)` e ativo `rgb(7,94,104)`, inspecionados no DOM. Dicionário/configuração pt-BR traduz controles Plotly e meses; controles nativos de tabelas do Streamlit ainda podem aparecer em inglês.
- A tabela Markdown do relatório fazia o conteúdo principal alcançar 931 px com área disponível de 350 px. Passou a ter rolagem interna; em 320/360/390/768/1366 px o conteúdo principal estabilizado não excedeu a largura disponível. Tabelas extensas continuam roláveis.
- Tab chegava a `summary` e aos anos selecionados sem contorno. `summary` e elementos com `tabindex` agora recebem foco de 3 px `#075E68`, confirmado com teclado e `:focus-visible`. Reset por Espaço e troca de página por seta também foram executados.
- PNG inicial cortava a identificação do snapshot. Rodapé passou a linhas curtas com margem reservada. PNG recebido foi aberto e inspecionado, com fonte, coleta, anos, unidade, snapshot e chave de consulta visíveis; `ranking-exportado-final.png` (1100×650, 94.447 bytes) contém o último ajuste de título e foi aberto e inspecionado.
- A 320 px, datas do histórico encostavam na fonte e controles encostavam no título da matriz. Datas foram reduzidas a três marcas, sem rotação, títulos ganharam espaço e a altura do ranking passou a ser preservada. Captura `evolucao-320-graficos-corrigido.jpg` confirma o resultado. Vinte séries continuam densas nessa largura; filtro por ponto e tabelas/resumos são os percursos de leitura detalhada.
- Singular/plural e quantidade efetiva do ranking ajustados para seleções de um ponto ou poucos pontos.

## Cenários efetivamente executados

| Percurso | Resultado observado | Evidência |
|---|---|---|
| Cinco páginas | Visão geral, comparador, evolução, contexto e relatório renderizados; agregado padrão 2,520; 226.870.300 contagens; 57.163 acima de 120 km/h | `paginas.json`, capturas e AppTest |
| Busca Laguna | Um ponto VC101-9, índice 6,343; comparador explica ausência de correlação com um ponto; histórico segue seleção | `consultas.json` |
| Busca Criciúma | Fora do grupo histórico: aviso e ação para consultar em todos os equipamentos; recupera VC101-30 exploratório | `consultas.json` |
| Filtros e vazios | Remover único ponto, anos ou sentidos mostra orientação; sem downloads de consulta vazia; restaurar repõe padrão | `consultas.json`, `sem-pontos.jpg` |
| Acidentes em 2026 | ANTT e PRF indisponíveis, sem zero factual; combinação 2025+2026 informa parcialidade | `consultas.json`, `contexto-2026-*.jpg` |
| URL/reload/nova aba | URL de Laguna recarregada e aberta em outra aba recupera ponto e filtros | `consultas.json` e captura histórica `laguna-url-reload.jpg` |
| Teclado | Tab, seta em radios, reset por Espaço e foco nos controles amostrados; correção de summary/ano confirmada | `teclado.json` |
| 320/360/390/768/1366 px | Cinco páginas inspecionadas com métricas CSS reais via CDP; contexto de 2026 sem gráfico; inspeção ampliada dos gráficos a 320 px | `viewports.json`, JPEGs nomeados por página/largura |
| Equivalente a 200% | Viewport 683×450 CSS px com DSF 2 (janela equivalente a 1366×900 em 200%), sem overflow principal | `zoom-equivalente-200.jpg`, `consultas.json` |

As dimensões foram confirmadas por `innerWidth` e largura/scroll do `main`, não apenas pelo nome da captura. A capacidade `viewport.set` não alterava a dimensão efetiva; as tentativas ineficazes não foram contadas. Houve transiente de redimensionamento Plotly (scroll 1285 ao mudar para 1366); após estabilização, `main` 1056/scroll 1056. A sequência de teclas para zoom não mudou DPR/viewport; portanto **zoom nativo de 200% permanece sem confirmação**. A emulação equivalente não é aparelho físico nem prova todos os comportamentos de zoom. Alguns registros/capturas precedem o ajuste final de espaçamento dos gráficos; `evolucao-final-*` e `evolucao-320-graficos-corrigido.jpg` são posteriores. Não confundir uma ausência de overflow com aprovação de toda legibilidade.

A extração inicial do histórico de um ponto concatenou textos SVG (`VC101-9` com números do eixo); não representa outro equipamento. A seleção e o comportamento são cobertos por AppTest; essa regex não serve como prova isolada dos IDs do gráfico.

## Downloads: servidor, recebimento e bloqueio são distintos

CSV recebido em Downloads: 34.518 bytes, 20 linhas, UTF-8, `;`, vírgula decimal, snapshot, anos, código e cobertura por fonte. Foi reaberto por `csv.DictReader`; cópia em `comparacao-recebida.csv`. PNG recebido pelo navegador, aberto visualmente; dimensões 1100×650 e identificação no rodapé. Mensagem do Plotly informou geração concluída.

Após o relato “arquivo não estava disponível”, a página foi recarregada e os três controles clicados novamente. Diagnóstico dos endereços efetivamente observados no navegador retornou HTTP 200 para CSV (34.518), Markdown (8.865) e ZIP (13.653 bytes), com MIME, tamanho e Content-Disposition coerentes (`download-diagnostico.json`). Isso comprova a resposta do servidor naquele instante; não comprova entrega pelo navegador. Reiniciar o servidor invalida mídias antigas, mas **não foi demonstrado que essa foi a causa do erro relatado**.

A captura enviada pelo usuário esclareceu o resultado das tentativas atuais: CSV, Markdown e ZIP exibem **“Bloqueado pela sua organização”** no Brave; o PNG exibe concluído. Recorte fiel em `bloqueio-downloads-informado-pelo-usuario.png`, identificado como evidência fornecida pelo usuário. Não houve tentativa de enfraquecer políticas ou usar outro canal para contornar o bloqueio. Há um CSV recebido anteriormente, mas isso não aprova os três downloads finais. Markdown/ZIP têm validação automatizada de conteúdo e HTTP; a entrega final por clique continua bloqueada pelo ambiente. Impressão/PDF pelo navegador não foi validada.

## Regressões e desempenho

Após as correções, 28 testes passaram em 110,94 s. Após o último ajuste de gráficos, nova execução: **28 passaram em 131,13 s**, Python 3.12.14; `pytest-final.xml`/log. Compilação de app.py/app_antt.py/src/tests passou. Contrato de 12 arquivos e hashes reconfirmado; nenhum Parquet alterado. A CI do commit enviado é registrada no PR.

Nova rodada sequencial após a suíte, sem ações de navegador e sem downloads, mediu apenas sessões de protocolo loopback. Navegador permaneceu aberto. Não é renderização nem ensaio do Render. Host compartilhado, 4 CPUs lógicas, ~3,70 GiB RAM, swap já em uso, carga de 1 minuto até 6,59.

| Sessões | Mediana protocolo/script | Máximo | RAM disponível mínima |
|---|---:|---:|---:|
| 1 | 4,171 s | 4,171 s | 586 MiB |
| 5 | 10,853 s | 10,861 s | 499 MiB |
| 10 | 10,704 s | 10,709 s | 479 MiB |

Nas 16 execuções, tempos registrados pelo servidor: consulta em cache mediana 0,025 s (0,006–0,076), conteúdo 3,469 s (0,793–7,624), exportações/fontes 1,543 s (0,137–2,189), carregamento de cópias 0,457 s (0,130–0,773). O total do protocolo inclui conexão, fila e transmissão, diferindo do tempo dentro do script. As condições e o número de sessões não garantem monotonicidade; não atribuir melhora/piora causal a uma única mudança. O perfil anterior também capturou watcher/asyncio e não deve ser interpretado como CPU pura da consulta.

`desempenho-final.json` e `etapas-servidor.log` permitem inspecionar amostras. Resultados reforçam que o cálculo em cache não domina a rodada aquecida; apresentação, serialização/exportação e contenção local merecem perfil específico antes de alterar infraestrutura. A meta de 5 s sob concorrência **não foi atendida**. Não foi contratado recurso, aplicado ajuste especulativo no Render ou certificada capacidade em 512 MiB.

## Pendências de aceitação

- Entrega por clique de CSV/Markdown/ZIP em ambiente sem o bloqueio organizacional; impressão do relatório; zoom nativo de 200%.
- Percurso integral por teclado, leitor de tela, Firefox, aparelhos reais e cinco participantes, com o roteiro existente. Foco/contraste amostrados não equivalem a auditoria integral WCAG.
- Meta de latência sob concorrência, retomada Free e memória/capacidade no provedor, após eventual aprovação para publicação; responsáveis por atualização/atendimento/monitoramento.
- Controles administrativos, CSP/HSTS e proteção da main continuam para etapa posterior. PR segue para revisão, sem merge/publicação.

Os arquivos diretamente em `evidencias/aceitacao-final` já existiam no worktree e foram preservados. A subpasta `2026-11-06-retomada` contém as evidências desta continuação. Capturas “antes” e tentativas falhas foram mantidas com contexto, sem usá-las como aprovação do estado final. O inventário registra hashes e dimensões; não contém extração de CSV bruto ou segredos.
