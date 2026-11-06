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
