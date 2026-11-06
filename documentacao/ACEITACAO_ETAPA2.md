# Continuação de aceitação a partir de 2a2c703

Branch limpa conferida em `2a2c703`, PR #2 aberto/rascunho, base main `e5baed4`. Aplicação local inicialmente confirmada por HTTP em 8502, Python 3.12.14. A continuação usa instância nova em **http://127.0.0.1:8506**, iniciada com o código atualizado; a instância antiga foi encerrada. O site publicado não contém estas alterações. Não houve merge, deploy, contratação ou alteração administrativa.

## Navegador e escopo de aceitação

Nesta continuação `cua.getState` retornou novamente `browsers=[]` e “Local browser use is disabled in Work settings”, inclusive após o usuário informar que habilitaria o Brave. A configuração continua impedindo a aceitação visual. Não se verificaram as larguras 320/360/390/768/1366, zoom 200%, teclado/foco real, contraste composto, legibilidade, URL/reload no navegador ou download PNG. As cinco páginas, filtros, busca, vazios, estado URL e arquivos continuam com evidência AppTest/protocolo, sem substituir as verificações de navegador solicitadas.

Participantes, leitor de tela real e ambiente de hospedagem da versão nova permanecem pendentes. A meta de aceitação continua aberta; este registro documenta progresso, não aprovação final.

## Investigação e mudança

O cliente de carga fazia downloads síncronos no event loop que observava todas as sessões. Foi corrigido para executar I/O em threads, separar conclusão do script e tempo de downloads, registrar primeiro delta/bytes e rejeitar término sem `script_finished`. Endereço/origem/downloads agora derivam da mesma URL local e a função exige loopback. Não se compararam tempos antigos e novos como se fossem o mesmo instrumento.

O perfil exploratório em uma instância separada mostrou agregações anuais repetidas e atividade de polling do framework. O profiler elevou o tempo, e tempos cumulativos de chamadas não devem ser somados ou tratados como causalidade. Pico RSS observado nessa única sessão instrumentada: 220.288 KiB (~215 MiB), não um pico para dez sessões.

Foi acrescentado cache de **até oito consultas**, identificado pelo token completo do pacote, pontos e anos. O retorno mantém cópias isoladas. O maior resultado deste snapshot serializou em 3.508.129 bytes; isso não inclui RSS adicional de figuras, deserialização, framework e cache de pacote. Teste dedicado confirma que mutar o retorno não afeta a próxima consulta e que outra identidade do pacote provoca novo cálculo.

Logs agora separam carregamento, consulta, conteúdo e exportações/fontes, sem registrar identificação do visitante. O perfil e os logs estão em `evidencias/aceitacao-etapa2`. Não foi proposta mudança de infraestrutura.

## Medições efetivas

Máquina Linux compartilhada: 4 CPUs lógicas, RAM total 3.883.172 KiB (~3,70 GiB), swap em uso. Carga de um minuto inicial ~5,89. Limites cgroup não estavam disponíveis. Há coleta de carga e memória disponível a cada ~250 ms. Ambiente diferente do Render; não comprova capacidade em 512 MiB.

| Rodada | Sessões | Mediana até conclusão/transmissão do script | Máximo | Menor RAM disponível |
|---|---:|---:|---:|---:|
| Instância anterior, cliente corrigido | 1 | 4,729 s | 4,729 s | 478 MiB |
| Instância anterior, cliente corrigido | 5 | 7,768 s | 8,243 s | 412 MiB |
| Instância anterior, cliente corrigido | 10 | 16,386 s | 17,655 s | 436 MiB |
| Nova instância com cache, primeira abertura fria | 1 | 6,730 s | 6,730 s | 691 MiB |
| Nova instância com cache | 5 | 5,783 s | 6,194 s | 644 MiB |
| Nova instância com cache | 10 | 9,431 s | 9,977 s | 511 MiB |

A rodada nova foi feita após encerrar a suíte e o servidor antigo; o aquecimento e a memória diferem. Há melhora observada nas consultas concorrentes, sem estimar efeito causal isolado do cache. A primeira abertura e concorrência continuam acima da meta de 5 s. O tempo do protocolo não é renderização no navegador. Os arquivos registram totais corretos (2,520; 226.870.300; 57.163), scripts concluídos, ausência de exceções e downloads HTTP 200.

Uma tentativa intermediária chamada `sessoes-instancia-antiga.json` ocorreu durante o fim da suíte e antes de reiniciar o servidor. Os logs não tinham as novas etapas: o módulo antigo permanecia carregado. Essa tentativa foi explicitamente excluída da avaliação do candidato. `sessoes-antes.json` e `sessoes-depois.json` são as rodadas da tabela. Isso reforça que um SHA do disco não prova o código já importado por um servidor antigo.

A maior parte do tempo residual da instância candidata ocorre em conteúdo e exportações/fontes, não no cálculo em cache, conforme logs por etapa. Isso orienta a próxima investigação; não prova que uma compra de CPU/RAM resolveria o percurso completo.

## Validação e próximos passos

- 27 regressões existentes aprovadas, incluindo cinco páginas, dados, filtros, URL e exportações; novo teste de cache aprovado isoladamente. CI do novo commit deve executar a suíte inteira (28 testes).
- Compilação e diff sem erros; nenhum Parquet alterado.
- Reproduzir: iniciar a branch em porta nova e executar `python scripts/investigate_performance.py --url ws://127.0.0.1:8506/_stcore/stream --output /tmp/sentinela-sessoes.json`. Não executar carga em produção.
- Falta habilitar o Brave para cumprir os cenários visuais e PNG solicitados. Depois, coletar evidências por largura/zoom, teclado e downloads, corrigir problemas efetivos e repetir cenários afetados.

## Nova tentativa com Chrome, Brave e navegador integrado em 06/11/2026

A pedido do usuário, o acesso foi revalidado do zero pela ferramenta `mcp__cua_repl.js`, sem estender ao Chrome uma conclusão anterior sobre o Brave. `cua.getState()` retornou inventário vazio e erro de acesso. Em seguida foram tentadas separadamente as chamadas documentadas `cua.createBrowserTab('chrome', ...)`, `cua.createBrowserTab('brave', ...)` e `cua.createBrowserTab('iab', ...)`, todas com a URL local 8506. **Cada chamada retornou “Local browser use is disabled in Work settings”.** Nenhuma aba foi disponibilizada à ferramenta. Trata-se do resultado desta sessão, mesmo que o controle tenha funcionado em outro momento.

O Git local estava limpo na branch solicitada e no commit `42dec24`. O PR remoto #2 confirmou a mesma ponta, continuando em rascunho, sem commits posteriores a preservar nesta consulta. Foram lidos integralmente AGENTS.md, matriz F01–F24, validação de 05/11 e este relatório.

A aplicação em `http://127.0.0.1:8506` continuava ativa: saúde `ok`, sessão concluída sem exceções, quatro downloads HTTP 200, agregado 2,520 por 10 mil, 226.870.300 contagens e 57.163 acima de 120 km/h. O ZIP exportado identificou exatamente `42dec2424379062144e710be4da8d2125a23c067` e snapshot `2026-10-26.1`. Essas verificações são de protocolo/arquivo, não de interface. O Render MCP confirmou o deploy publicado antigo `dep-dbg7476c6qcc73ei65g0`, em `e5baed4`, estado live; portanto o site público não foi usado para validar a branch corrigida. A CI do commit `42dec24`, run 42153357635, foi reconferida como success.

Evidência estruturada: `evidencias/tentativas-navegadores-2026-11-06.json`. Sem alteração do código ou dos dados nesta rodada, não se repetiu a carga ou a suíte local sem motivo novo. Os resultados de desempenho da seção anterior permanecem válidos dentro de seus limites; não há nova evidência para atribuir a lentidão a infraestrutura nem propor contratação.

Continuam sem validação no navegador as cinco páginas e seus percursos visuais, busca, filtros, vazios, compartilhamento/reload/recuperação, clique nos downloads, PNG, larguras de 320/360/390/768/1366 px, zoom 200%, teclado/foco, contraste composto e legibilidade. Não foram produzidas capturas fictícias nem classificados testes de protocolo como testes de viewport. Participantes, leitor de tela e dispositivos reais continuam pendentes. O próximo passo depende de uma sessão de navegador disponibilizada à ferramenta; esta tentativa não encerra a aceitação.

## Continuação em 06/11 — navegador disponível

O relato anterior de indisponibilidade é histórico. Ver [aceitação no navegador](ACEITACAO_NAVEGADOR_2026-11-06.md) e matriz atualizada: cenários reais, correções visuais, 28 regressões finais, evidências e desempenho. Downloads finais CSV/MD/ZIP bloqueados pela organização no Brave; PNG recebido e inspecionado. Zoom equivalente emulado, sem confirmação de zoom nativo. Pessoas/leitor de tela/aparelhos/hospedagem permanecem sem aprovação.

Atualização de downloads: o usuário concluiu CSV/Markdown/ZIP manualmente no Chrome; captura fornecida e arquivos efetivamente recebidos inspecionados (20 pontos, totais e metadados coerentes, ZIP íntegro). F18 atualizado no relatório/matriz. O bloqueio do Brave permanece como resultado específico, sem alteração de políticas.
