# Revisão final do SENTINELA em 09/11/2026

## Código e dados

A revisão percorreu o diff do PR #2 entre a base `e5baed4` e a branch de correção, incluindo o código anterior necessário para conferir as fórmulas e as fontes. O worktree da branch foi preservado, separado do checkout principal. O servidor de comparação foi iniciado em 127.0.0.1:8510, em cópias isoladas de `5c2d0bf` e do candidato `02a704e`, com Python 3.12.14.

- O índice soma excedências e contagens da mesma base A, dos mesmos pontos e períodos. A cobertura considera cada ano civil solicitado e o ano oficialmente parcial fica em exploração. ANTT, PRF e base B têm estados próprios. O contexto de segmentos compara dias comuns e preserva junções por chaves.
- As entradas da URL são validadas com as opções da consulta. Testes exercitam URL nova, filtros vazios, consultas isoladas e a invalidação quando o pacote muda. Os caches de consultas têm limites e a identidade inclui manifesto e estatísticas dos arquivos.
- As exportações preservam precisão, cobertura, proveniência e identidade da consulta. Falhas operacionais apresentam aviso público e log técnico. A CI valida o pacote, compila os módulos, executa testes e consulta vulnerabilidades conhecidas das dependências instaladas.
- `02a704e` monta o ranking diretamente em Plotly, compartilha a formatação das tabelas e reutiliza a versão já capturada para exportações. A regressão verifica o valor completo de Laguna e sua apresentação em pt-BR. O PNG do ranking padrão gerado no Brave local foi inspecionado e teve o mesmo SHA-256 da evidência anterior, `8bd6fbdc0b6506aad2787e4913e92518858acd62794e4742585132964449d368`. A amostra adicional de 320 e 1366 px confirmou encaixe do gráfico. Fórmulas, precisão e Parquet foram preservados.
- A suíte local passou com 29 testes em 111,84 s. Compilação e `git diff --check` passaram. A aprovação da incorporação depende da CI da ponta exata, que inclui o novo teste.

## Desempenho local

Mesma máquina compartilhada, 4 CPUs e 3,7 GiB com swap, Python 3.12.14, `OPENBLAS_NUM_THREADS=1`, mesma versão de dados e mesma consulta padrão. As cópias rodaram sequencialmente na mesma porta, sem carga em paralelo com a interface ou a suíte. Foram feitas duas rodadas de sessões aquecidas em cada nível. Os tempos incluem execução Streamlit e transmissão até o término do script. A renderização do navegador ficou fora desta medição.

| Sessões simultâneas | Observações por versão | Base mediana / máx. | Candidato mediana / máx. |
|---|---:|---:|---:|
| 1 | 2 | 1,035 / 1,098 s | 0,957 / 0,985 s |
| 5 | 10 | 5,360 / 5,487 s | 5,062 / 5,373 s |
| 10 | 20 | 11,345 / 11,655 s | 9,742 / 9,775 s |

A abertura fria local foi de 5,118 s na base e 7,160 s no candidato, uma observação de cada. Todas as consultas medidas retornaram 2,520, 226.870.300 contagens e 57.163 excedências. A RAM disponível mínima do host foi de 618 MiB na base e 543 MiB no candidato. O perfil amostral de ranking passou de 0,418 s para 0,152 s. Os registros anteriores também indicam custo na apresentação de fontes e no preparo das exportações. A variação de recursos limita a atribuição causal. Os tempos ultrapassaram a meta de 5 s nas rodadas de 5 e 10 sessões e na abertura fria do candidato. O ensaio não inclui carga no Render.

## Critérios para disponibilizar o piloto

| Classificação | Critério e motivo |
|---|---|
| Bloqueante antes da incorporação | CI aprovada no SHA final, contrato íntegro, regras da main respeitadas e identidade do serviço confirmada. Essas verificações protegem o código e o pacote que irão ao ar. |
| Bloqueante na verificação pública | Deploy com identidade errada, falha de abertura ou reconexão persistente, erro nos resultados, cobertura enganosa ou regressão geral nas consultas/exportações exigem diagnóstico e avaliação de retorno. |
| Acompanhamento | A meta de latência não foi atingida na concorrência local. O piloto pode ser observado com uso leve; capacidade, SLA e retomada após inatividade do plano Free continuam sem aprovação. |
| Acompanhamento | Participantes, aparelhos reais, Firefox e leitor de tela continuam pendentes. Testes de viewport, teclado, contraste e zoom nativo no Chrome são evidências separadas. |
| Acompanhamento | Definição de responsáveis, monitoramento externo, revisão de cabeçalhos e proteção administrativa, conformidade integral e certificação de acessibilidade ficam para etapas próprias. |

## Publicação verificada

| Campo | Resultado |
|---|---|
| Site | [radarsul.site](https://radarsul.site) e [radarsul.onrender.com](https://radarsul.onrender.com) |
| GitHub | [PR #2](https://github.com/limixin1/radarsul/pull/2), incorporado às 17:46:55 em São Paulo, preservando os commits |
| Ponta verificada antes da incorporação | `02a704eb77ba13bb4242da33a202b52eca4144ee` |
| Commit executável na main e SHA implantado | `38987b05baf99faaca2d3f7bafed0271969ee281` |
| Aplicação e dados | 2.1.0, snapshot `2026-10-26.1`, 12 arquivos do contrato |
| Render | [Serviço radarsul](https://dashboard.render.com/web/srv-dbfvgi59el5s73bealsg) no workspace TCC 371, uma instância Free em Virginia |
| Deploy definitivo | `dep-dbp32h3nv7mc73bbhb10`, live às 17:49:58 em São Paulo |
| Referência anterior | `dep-dbg7476c6qcc73ei65g0`, SHA `e5baed4fdab7575690a408f4ab492fd63790a00e` |

A [CI do PR](https://github.com/limixin1/radarsul/actions/runs/42695886084) e a [CI do push](https://github.com/limixin1/radarsul/actions/runs/42695876394) passaram no SHA final da branch. A CI do PR validou os 12 arquivos, compilou os módulos, passou 29 testes em 22,27 s e não encontrou vulnerabilidades conhecidas nas dependências auditadas. A [CI do merge na main](https://github.com/limixin1/radarsul/actions/runs/42696225571) também passou.

O Render iniciou automaticamente `dep-dbp32gi9lscs73anoulg` pelo commit e enfileirou `dep-dbp32h3nv7mc73bbhb10` ao sincronizar a mudança de build do Blueprint existente. Ambos usaram o mesmo SHA. O segundo substituiu o primeiro. Os logs do segundo registraram checkout na main, Python 3.12.14, validação dos 12 arquivos no build e inicialização do Streamlit na porta atribuída. Os dois domínios devolveram HTTP 200 e corpo `ok` em `/_stcore/health`. O filtro de avisos e erros da aplicação veio vazio de 17:49:58 a 17:55:47. Nenhum deploy manual ou retorno foi necessário. Não houve contratação nem operação administrativa em domínio, plano ou acesso.

### Verificações públicas

| Item | Evidência e estado |
|---|---|
| Identidade e Visão geral | O Brave exibiu o SHA completo, 2.1.0, snapshot e totais padrão 2,520, 226.870.300 e 57.163. |
| Páginas e filtros | Comparador, Evolução, Contexto e Relatório foram abertos. O Comparador padrão exibiu Spearman 0,962 e base B separada. A busca por Laguna selecionou VC101-9; a URL e os filtros foram recuperados no reload. A consulta padrão voltou após restaurar. |
| Cobertura e vazios | Em 2026, as fontes de acidentes ANTT e PRF apareceram como indisponíveis. No período misto 2024–2026 apareceram como parciais. O tráfego de 2026 é exploratório e o inventário vai até 30/06. Remover todos os pontos ou anos exibiu orientação e nenhum botão de exportação. |
| CSV e PNG | Ambos chegaram à pasta de downloads no Brave. O CSV reaberto tinha 20 linhas, o SHA e snapshot implantados e somas 226.870.300 e 57.163. O PNG de 1100 × 650, gerado pelo teclado, foi aberto e inspecionado; mostra unidade, anos, origem, snapshot e chave de consulta. |
| Markdown e ZIP | Os cliques no Brave não deixaram arquivos, inclusive após reteste. A captura do usuário mostra “O arquivo não estava disponível no site”; ele informou nova falha manual. O controle do Chrome respondeu `Browser is not available: chrome` nas duas tentativas. O teste independente de serviço abriu uma sessão WebSocket, requisitou os três links gerados e obteve HTTP 200 de todos. O Markdown continha SHA, snapshot e totais; o ZIP abriu sem erro, com cinco membros, os mesmos metadados e 40 linhas de cobertura. No reteste manual, o agente encontrou os dois arquivos salvos, reabriu o Markdown e o ZIP e reconciliou os CSVs. O Markdown avulso é idêntico ao do ZIP. Os cinco membros, 20 pontos, 40 linhas de cobertura, índices, totais, SHA e snapshot conferem. O resultado manual complementa a sonda e encerra a pendência de recebimento. |
| Primeira abertura e reconexão | Na primeira visita após o deploy por commit, o primeiro resultado útil apareceu entre 24,5 e 28,8 s observados pela ferramenta. Os logs mediram 12,702 s para o script inicial e 12,298 s na primeira consulta da instância definitiva. O mesmo Brave voltou a responder após a troca automática de instância; o clique que coincidiu com a transição teve de ser repetido. Uma execução padrão aquecida levou 1,003 s no log, e a sonda pública isolada levou 4,825 s até o fim do script e da transmissão. A interrupção breve simulada no navegador não derrubou o socket e foi inconclusiva para continuidade da sessão. |

[Evidências públicas e sonda](evidencias/publicacao-2026-11-09/) · [Procedimento de retorno](OPERACAO.md)

O piloto foi disponibilizado. Não apareceu regressão crítica de identidade, cálculo, cobertura ou entrega HTTP que justificasse retorno. A abertura inicial ultrapassou a meta de 5 s. Permanecem em acompanhamento a reprodução automatizada no Chrome, a capacidade e a retomada por inatividade do plano Free, a avaliação com participantes, aparelhos reais, Firefox, leitor de tela e a operação continuada. As medições públicas usaram interações individuais e não certificam capacidade ou SLA.
