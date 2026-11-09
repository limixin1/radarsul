# Conferência da entrega de aceitação

Escopo: objetivo de continuação do PR #2, incluindo leitura da matriz, validação local, navegador, desempenho, evidências e entrega para revisão. Não é aprovação integral do produto ou autorização de publicação. Evidência principal: ACEITACAO_NAVEGADOR_2026-11-06.md, sua seção complementar e os diretórios de evidências vinculados.

| Requisito do objetivo | Evidência autoritativa | Resultado e limite |
|---|---|---|
| Preservar branch/commits/correções | Git da branch correcao/sentinela-auditoria; 2a2c703 → 42dec24 → 0f789ff → 7396d0f → aefaac0 → 7dbdd27; diff desta continuação | Sem reset, force push ou reversão. Worktree existente preservado; diretório principal separado. Ponta remota reconferida antes do envio. |
| Ler instruções e configuração | AGENTS.md, requirements, .python-version, render.yaml, prompt/auditoria em _contexto e relatórios | Python 3.12.14 e ambiente preservados. Alteração final restrita a apresentação/impressão; nenhum Parquet/fórmula alterado. |
| Navegador e local diferentes do publicado | Brave pelo mcp__cua_repl; servidor 127.0.0.1:8506; identidade no PDF/exportações; Render list_deploys | Acesso real disponível; versão corrigida local. Último Render reconfirmado em e5baed4. |
| Cinco páginas | paginas.json, paginas-teclado.json, capturas e test_five_pages | Percurso visual e navegação por setas preservando Laguna; sem erro. |
| Filtros, cidade e vazios | consultas.json, filtros-teclado.json, captura sem-pontos; AppTest | Laguna, Criciúma e recuperação; anos/sentidos/pontos; vazio orientado e sem downloads; reset. |
| URL, reload, nova sessão, isolamento | consultas.json, laguna-url-reload.jpg, test_shared_url_new_session_isolation | Reload e nova aba reais, isolamento e entradas inválidas cobertos por AppTest. |
| Downloads e conteúdo | Arquivos Chrome manuais/PNG e JSONs de validação; png-gerado-por-teclado-laguna.png | Usuário concluiu CSV/MD/ZIP no Chrome; agente abriu/inspecionou. Brave bloqueou esses tipos; política preservada. PNG por clique e por Espaço recebido/inspecionado. |
| Larguras 320/360/390/768/1366 | viewports.json, capturas por página, impressao-viewports.json | Dimensões CSS confirmadas; relatório principal sem overflow. Matriz/gráficos bidimensionais e tabelas não equivalem a leitura de todos os dados em uma única tela. |
| Zoom nativo de 200% | zoom-nativo-200-manual.json e resposta textual do usuário | Usuário confirmou cinco páginas e filtros no Chrome. Separado da emulação equivalente; sem captura específica. |
| Teclado, foco, contraste e leitura | teclado-percurso.json (60 posições), paginas/filtros-teclado.json, foco/cores no DOM e capturas | Percurso funcional, busca, setas, Backspace, Espaço, tabelas alternativas e saída das grades. Não certifica WCAG integral ou leitor de tela. |
| Corrigir problemas e repetir cenários | Commits de contraste/foco/Plotly/tabela/PNG e correção de impressão; PDFs e cinco larguras repetidas | Problemas observados corrigidos. Dois testes pertinentes após impressão passaram (6,79 s); suíte integral anterior 28/28, CI da ponta registrada no PR. |
| Impressão adicional útil | output/pdf/sentinela-aceitacao-20-pontos.pdf e sentinela-aceitacao-laguna.pdf; renders/textos e validacao-impressao.json | Motor do navegador via CDP, A4, três/duas páginas. 40 linhas e valores/identidade preservados; todas as páginas abertas. Sem impressora física/diálogo nativo. |
| Investigar lentidão com etapas/recursos | ACEITACAO_ETAPA2.md e desempenho-final.json/etapas-servidor.log | 1/5/10 sessões locais; recursos, cache e conteúdo/exportações medidos. Concorrência excede meta de 5 s; não atribuído causalmente a uma compra/plano. Sem carga em produção. |
| Matriz F01–F24 e limites | MATRIZ_F01_F24.md, registro de validação e relatório atual | 24 achados com estado, correção, evidência e pendência. Pessoas, leitor de tela, Firefox, aparelhos reais, provedor/monitoramento e responsáveis explicitamente não aprovados. Roteiro de pessoas disponível. |
| Entregar no PR sem publicar | PR #2, branch remota, CI vinculada na descrição | Alterações para revisão. Sem merge, contratação, deploy, DNS ou administração. A CI final deve ser conferida no SHA atual antes de encerrar a tarefa. |

As pendências externas estão mantidas conforme o objetivo: esta entrega não simula participantes, leitor de tela ou aparelhos, e não publica a versão para tentar certificar a hospedagem. As metas propostas de latência não foram declaradas atendidas. Elas são resultado da investigação e pendência do piloto, não aprovação de capacidade.
