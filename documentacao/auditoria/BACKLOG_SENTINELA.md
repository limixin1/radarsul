# Backlog de implementação do SENTINELA

**Base:** auditoria independente de 27/10/2026.  
**Repositório de referência:** https://github.com/limixin1/radarsul.  
**Commit inspecionado:** `e5baed4fdab7575690a408f4ab492fd63790a00e`.  
**Estado:** tarefas propostas; nenhuma implementada nesta auditoria.

Este backlog deve ser executado com ESPECIFICACAO_SENTINELA.md. AUDITORIA_SENTINELA.md contém os testes executados e FONTES_E_VALIDACOES.md registra o que foi confirmado nos arquivos, nos metadados e o que continua desconhecido.

## 1. Critérios de prioridade e esforço

- **P0 — Crítico:** indicador inválido exposto como factual, conteúdo enganoso essencial ou falha central grave. Nenhum P0 foi confirmado nos cálculos centrais examinados. Introduzir B/A ou probabilidade de acidente sem validação seria uma regressão P0, não uma funcionalidade deste backlog.
- **P1 — Alto:** falhas de escopo, requisitos centrais da proposta, rastreabilidade ou barreiras importantes de entendimento/acesso.
- **P2 — Médio:** visualização, organização, completude dos relatórios, estados de erro, verificação e desempenho.
- **P3 — Baixo:** documentação operacional e refinamentos secundários.

Esforço **pequeno/médio/grande** é uma estimativa qualitativa da alteração e de sua verificação, não prazo ou compromisso de horas. Não foram atribuídos responsáveis ou datas.

## 2. Ordem de execução e dependências

| Ordem | ID | Prioridade | Entrega | Dependências | Esforço |
|---:|---|---|---|---|---|
| 1 | SEN-001 | P1 | Escopo consistente dos filtros locais | Nenhuma | Pequeno |
| 2 | SEN-002 | P1 | Catálogo de fontes e método verificável | Nenhuma | Médio |
| 3 | SEN-005 | P1 | Contrato dos indicadores e bloqueios | SEN-002 | Médio |
| 4 | SEN-004 | P1 | Qualidade da publicação e incerteza observável | SEN-005 | Grande |
| 5 | SEN-003 | P1 | Síntese preventiva específica por local | SEN-001/002/004/005 | Grande |
| 6 | SEN-006 | P1 | Experiência em camadas e linguagem compreensível | SEN-002/003/005 | Médio |
| 7 | SEN-007 | P1 | Acesso equivalente a resultados e idioma correto | SEN-001/006 | Médio |
| 8 | SEN-009 | P2 | Escopo e cobertura com textos dinâmicos | SEN-001/005 | Pequeno |
| 9 | SEN-010 | P2 | Comparações temporais com população e período explícitos | SEN-004/005/009 | Médio |
| 10 | SEN-011 | P2 | Contexto de acidentes com recortes transparentes | SEN-001/005/009 | Médio |
| 11 | SEN-008 | P2 | Localização visual e ficha do ponto | SEN-005/006 | Médio |
| 12 | SEN-012 | P2 | Relatório autossuficiente e ligado ao diagnóstico | SEN-002/003/009/010/011 | Médio |
| 13 | SEN-013 | P2 | Legibilidade, formato numérico e layout | SEN-006/007/009 | Pequeno |
| 14 | SEN-016 | P2 | Estados de indisponibilidade e erro recuperáveis | SEN-002/005 | Médio |
| 15 | SEN-014 | P2 | Regressão e cenários pendentes concluídos | Acompanha todas as anteriores | Médio |
| 16 | SEN-015 | P2 | Verificação de versão, carregamento e demonstração | SEN-014/016 | Médio |
| 17 | SEN-017 | P3 | Documentação de publicação coerente com o estado verificado | SEN-015 | Pequeno |
| 18 | SEN-018 | P3 | Exportação CSV com contexto suficiente | SEN-001/002/009/012 | Pequeno |

Os números dos IDs são estáveis e não representam ordem de execução. Catálogo, fórmula, nomes e regras devem ter definições únicas; as tarefas que os consomem não devem criar versões paralelas.

## 3. Tarefas detalhadas

### SEN-001 — Fazer os filtros locais governarem todas as visualizações da seleção

- **Prioridade/tipo:** P1; falha funcional comprovada.
- **Componente:** Comparador e Evolução e persistência.
- **Descrição:** o multisseletor local restringe a tabela e as linhas, mas não a dispersão anual nem o mapa de calor.
- **Evidência:** UI-006/007, E04. No [comparador](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py#L48), `show` usa `chosen`, enquanto `persistence` recebe `aid` derivado de `ids`. No [histórico](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py#L64), `coverage_map` recebe `ids`.
- **Impacto:** usuário pode atribuir um coeficiente ou padrão do conjunto inteiro aos pontos que selecionou.
- **Causa:** uso de conjuntos de IDs diferentes no mesmo fluxo.
- **Solução:** definir uma seleção efetiva por tela. Gráfico, tabela e exportação usam esse conjunto; grupos de referência fixos são nomeados como referência, sem substituir silenciosamente a seleção.
- **Aceitação:** com apenas VC101-4, tabela tem uma linha e nenhum gráfico afirma correlação com 20 radares; persistência informa insuficiência para correlação com um ponto. No histórico de VC101-9, mapa de calor tem uma linha. Com zero itens, não há resultado anterior ou CSV de uma seleção antiga. Anos, sentido e território continuam aplicados. CT-01/02/03.
- **Dependências/esforço:** nenhuma; pequeno.

### SEN-002 — Tornar fontes, fórmula e proveniência verificáveis no produto

- **Prioridade/tipo:** P1; lacuna de rastreabilidade comprovada.
- **Componente:** Método, cadastro e fontes; catálogo consumido por relatórios.
- **Descrição:** a interface aponta só para a raiz do portal ANTT e o relatório remete a um caminho interno. Usuário externo não consegue conferir imediatamente os quatro recursos e o cálculo.
- **Evidência:** UI-003/033; [expansível atual](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py#L91); download real `relatorio_publicado_criciuma.md`.
- **Impacto:** demonstração e relatório exigem explicação oral ou busca fora do produto para comprovar dados e critérios.
- **Causa:** documentação detalhada ficou no pacote/repositório, sem incorporação suficiente à interface.
- **Solução:** catálogo único A/B/C/D com página oficial, URL do CSV, dicionário, período efetivo, data de atualização do recurso quando verificada, data de coleta, hash e limitações. Expansível com fórmula completa e regras; link para documentação fixada em versão. Diferenciar metadado recuperado de novo download validado.
- **Aceitação:** os quatro recursos e suas URLs constam na página e em exportações; fórmula A-alta/A-total × 10.000 aparece; B/A está indicado como indisponível com motivo. Status 200 com HTML nunca é classificado como CSV válido. Não anunciar “atualizado hoje” com base só na data de consulta. CT-04/05/18.
- **Dependências/esforço:** nenhuma; médio.

### SEN-003 — Gerar síntese preventiva com evidência específica por local

- **Prioridade/tipo:** P1; requisito central não atendido.
- **Componente:** Visão geral, detalhe do equipamento e Relatório preventivo.
- **Descrição:** o produto mostra ranking/correlações e encaminhamentos invariantes; não explica quais padrões locais justificam investigar.
- **Evidência:** R09; [relatório](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt_report.py#L36) repete cinco encaminhamentos. Os resultados já contêm quartis e quatro pontos persistentes, sem fluxo equivalente na UI.
- **Impacto:** o diferencial de começar pelo comportamento não se transforma em uma decisão exploratória compreensível.
- **Causa:** ausência de regra de triagem consumida pela interface e de narrativa condicionada aos dados.
- **Solução:** usar regra descritiva transparente: ponto elegível no quartil superior do grupo principal nos dois anos; mostrar numerador, denominador, dias, valores anuais, referência e restrições. Contextualizar acidentes separadamente, sem converter poucos registros em segurança. Mostrar “dados insuficientes para esta regra” quando necessário. Não criar score ponderado de risco.
- **Aceitação:** no snapshot auditado, a regra relativa identifica VC101-39, VC101-4, VC101-7 e VC101-9, com limiares reproduzidos; seleção não recalcula silenciosamente o quartil em apenas um radar. Criciúma informa insuficiência da cobertura principal, sem receber classe de baixo risco. Cada indicação tem motivo, evidências, restrições e próximo passo de verificação. Nenhuma prescrição automática de obra/fiscalização. CT-06/07/08.
- **Dependências/esforço:** SEN-001/002/004/005; grande.

### SEN-004 — Expor sinais de publicação incompleta e a sensibilidade da análise

- **Prioridade/tipo:** P1; limitação científica comprovada, com causa operacional ainda desconhecida.
- **Componente:** processamento de qualidade, histórico, detalhe e síntese.
- **Descrição:** um dia com contagem mínima e poucas faixas pode contar como cobertura integral de publicação, embora a UI avise que isso não comprova completude.
- **Evidência:** DV-014: 29/08/2025, 36 radares e 698 contagens; VC101-30 tem 22 em duas faixas e mediana diária anual de 14.745,5. DV-013 demonstra mudança de resultados com seleção de cobertura.
- **Impacto:** comparação e triagem podem confundir padrão de publicação com padrão do tráfego; público pode superestimar a qualidade por ver 90% dos dias.
- **Causa provável:** limitação do sistema de publicação/medição ou mudança real de operação/tráfego. Não foi determinada. A rotina observa presença de dias, não cobertura horária ou semântica da ausência de faixas.
- **Solução:** separar disponibilidade de linhas, abrangência das faixas e completude desconhecida. Acrescentar painel de qualidade com datas, quantidades e ausências, sensibilidade 80/90/95% e sinalização de candidatos a publicação parcial. Investigar o dia observado antes de afirmar erro ou excluir registros. Não inventar faixas com zero, interpolar contagens ou mudar os totais históricos silenciosamente.
- **Aceitação:** o exemplo de 29/08 aparece como alerta verificável, com causa “não confirmada”; o indicador publicado original continua reproduzível; eventual cenário de exclusão é identificado como sensibilidade, com regra e delta de valores. Se a completude não puder ser confirmada, a síntese mantém a restrição. Zero registrado, ausência de linha e indisponibilidade têm estados diferentes. CT-09/10/11.
- **Dependências/esforço:** SEN-005; grande.

### SEN-005 — Fixar o contrato científico dos indicadores e dos recortes inviáveis

- **Prioridade/tipo:** P1; robustez metodológica e prevenção de regressão. O bloqueio atual de B/A já está correto.
- **Componente:** agregações, esquema dos dados, chamadas da UI e documentação.
- **Descrição:** o novo indicador pode ser confundido com a métrica original de possíveis infrações; mudanças futuras de filtro ou esquema podem violar sua unidade.
- **Evidência:** DV-005/006/009; B/A incompatível mesmo após agregação. Categoria de A é ausente ou não classificada em todas as linhas; B é inteiramente não classificada. O dicionário A dá exemplo numérico de velocidade, mas o CSV contém intervalos.
- **Impacto:** risco de implementar uma taxa sem denominador compatível ou disponibilizar recortes sem significado físico comprovado.
- **Causa:** propriedades e limitações das fontes, não ausência de um algoritmo sofisticado.
- **Solução:** contrato de unidade e granularidade; catálogo de métricas disponíveis/indisponíveis; razão entre somas da mesma base; denominador positivo; versionamento de faixas; bloqueio de novas classes desconhecidas até revisão. Manter veículos únicos, velocidade média, infrações legais e probabilidade de acidente fora das saídas. Categoria/faixa física ficam indisponíveis com explicação.
- **Aceitação:** B/A permanece nulo/indisponível em todos os filtros e exportações. Alteração de faixa ou esquema não produz cálculo silencioso. Agregações mantêm totais; join não multiplica linhas. Um denominador zero não gera infinito nem zero artificial. “Não classificado” não vira categoria leve/pesado. CT-05/09/12/13.
- **Dependências/esforço:** SEN-002; médio.

### SEN-006 — Reorganizar a experiência em resultado, evidências e método

- **Prioridade/tipo:** P1; barreira de comunicação comprovada por avaliação heurística.
- **Componente:** títulos, navegação, rótulos e cartões.
- **Descrição:** a primeira camada exige entender coorte, índice e Spearman. O maior valor aparece sem município no título e coexistem máximo individual e totais do conjunto.
- **Evidência:** E01/E02/E05/E06, UI-032; termos `altas` e `por_10_mil` visíveis. Não houve teste com usuários reais.
- **Impacto:** dificuldade de explicar o resultado sem um apresentador técnico; risco de confundir índice agregado, máximo, infração e risco.
- **Causa:** linguagem de processamento usada como linguagem do produto.
- **Solução:** aplicar a tabela de textos e os três níveis da especificação. Resultado simples com município/km/período; evidências disponíveis ao abrir detalhe; fórmula e fontes no método. Spearman em detalhe técnico, com explicação e `n`.
- **Aceitação:** nenhum nome interno de coluna no texto principal; título identifica local e medida; máximo e agregado são rotulados separadamente; “por 10 mil” tem explicação próxima. Teste formativo posterior registra se leigos distinguem registros, infrações e previsão, sem afirmar aprovação antes do teste. CT-14/15.
- **Dependências/esforço:** SEN-002/003/005; médio.

### SEN-007 — Dar acesso equivalente aos resultados e corrigir o idioma

- **Prioridade/tipo:** P1; lacuna de acessibilidade observada. Conformidade integral ainda não medida.
- **Componente:** documento, gráficos, grades, controles e foco.
- **Descrição:** `lang=en` em português; dados de gráficos/grades não aparecem como tabela na observação acessível. Leitura do relatório é melhor por usar tabela nativa.
- **Evidência:** UI-025/026/027 e observacoes_ambiente.json. Não houve teste com leitor de tela.
- **Impacto:** leitura e compreensão prejudicadas para usuários de tecnologia assistiva e navegação sem mouse.
- **Causa:** configuração padrão e dependência de representações gráficas/grades.
- **Solução:** idioma pt-BR por mecanismo suportado; nome acessível por controle; alternativa tabular e resumo textual para cada figura; teclado e foco visível; estados anunciados. Não esconder valores só em hover ou cor. Se Streamlit limitar a solução, documentar e validar a alternativa, sem declarar AA por suposição.
- **Aceitação:** auditoria do DOM confirma idioma; cada série/ranking/contexto pode ser consultado sem desenho; teclado permite selecionar, abrir detalhes, exportar e sair; leitura por ao menos uma tecnologia assistiva é registrada. Critérios relevantes WCAG 2.2 AA são verificados conforme especificação. CT-16/17.
- **Dependências/esforço:** SEN-001/006; médio.

### SEN-008 — Facilitar a localização dos pontos e o acesso à ficha

- **Prioridade/tipo:** P2; melhoria de utilidade para gestores, não falha de um mapa existente.
- **Componente:** ranking, detalhe e visualização geográfica nova.
- **Descrição:** resultados usam principalmente IDs e não há mapa geográfico; município/km existem em tabela, coordenadas estão no arquivo.
- **Evidência:** inventário das cinco telas; DV-010; metadados de 42 pontos.
- **Impacto:** usuário precisa cruzar manualmente ranking, tabela e território.
- **Causa:** falta de apresentação espacial na UI atual.
- **Solução:** adicionar ficha com ID, município, km, sentido e referência cadastral; mapa simples dos pontos publicados, com seleção sincronizada e tabela equivalente. Exibir origem das coordenadas, sem alegar levantamento em campo ou converter sentido para Norte/Sul por inferência.
- **Aceitação:** clicar/selecionar um ponto abre a mesma ficha usada na tabela; filtros coincidem; coordenada ausente/inválida não cria ponto fictício. VC101-20 mantém localização de A, com ausência de referência cadastral de D explícita. Mapa indisponível não bloqueia consulta textual. CT-19.
- **Dependências/esforço:** SEN-005/006; médio.

### SEN-009 — Fazer as legendas descreverem a população e o período exibidos

- **Prioridade/tipo:** P2; inconsistência comprovada.
- **Componente:** visão geral, cobertura, rodapé e cabeçalhos.
- **Descrição:** a legenda fixa “20 de 42” aparece mesmo no filtro de um radar em 2026; “dias distintos” é união de datas e não dias de operação de todos os radares.
- **Evidência:** UI-020/E08; [app_antt.py:45](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py#L45).
- **Impacto:** interpretação errada da composição e cobertura do recorte.
- **Causa:** textos fixos e agregação de datas sem descrição suficiente.
- **Solução:** resumo dinâmico de território, anos, sentidos, IDs efetivos, datas observadas e número de pontos; separar definição da coorte de composição da seleção. Nomear a união de datas e expor cobertura por radar/ano.
- **Aceitação:** Criciúma/2026 informa um radar e 181 datas observadas, sem apresentá-lo como parte da coorte de 20; padrão 2024–2025 informa corretamente o grupo principal. “731” não é descrito como operação de cada sensor. CT-03/10/20.
- **Dependências/esforço:** SEN-001/005; pequeno.

### SEN-010 — Explicitar os limites das comparações temporais

- **Prioridade/tipo:** P2; limitação de comparabilidade, com controles parcialmente existentes.
- **Componente:** seleção de anos, evolução e comparador.
- **Descrição:** o pertencimento à coorte depende de 2024/2025, mas o usuário pode selecionar 2022, 2023 ou 2026. Um aviso de ano parcial não garante comparação sazonal adequada.
- **Evidência:** código dos anos e da seleção fixa; A cobre até junho/2026, B até 02/06/2026; B tem apenas dois dias publicados em 2022; UI-014.
- **Impacto:** aparentes variações anuais podem refletir cobertura, sazonalidade ou alteração de publicação.
- **Causa:** períodos e populações diferentes sob o mesmo rótulo de grupo.
- **Solução:** manter grupo de referência fixo documentado; indicar elegibilidade no ano efetivamente exibido; distinguir análise 2024–2025 de exploração de outros anos. Comparações de janelas parciais usam mesmas datas/calendário e população quando houver suporte; caso contrário não produzem interpretação automática de melhora/piora.
- **Aceitação:** 2026 nunca é tratado como ano completo; 2022/2023 não herdam certificação de cobertura por pertencerem ao grupo 2024/2025. Série mensal preserva lacunas e não conecta por interpolação. Ausência de B em um período não vira zero real. CT-10/21.
- **Dependências/esforço:** SEN-004/005/009; médio.

### SEN-011 — Organizar o contexto de acidentes sem sugerir risco ou proteção

- **Prioridade/tipo:** P2; problema de hierarquia e escopo, com cálculo descritivo reproduzido.
- **Componente:** Contexto rodoviário e contexto do detalhe.
- **Descrição:** o coeficiente negativo é o destaque principal; segmentos com datas comuns, envelope territorial e PRF integral são apresentados na mesma tela.
- **Evidência:** UI-009/010/E06/E07; DV-008/011/012; dias comuns de 636 a 731 entre os 16 segmentos.
- **Impacto:** usuário pode interpretar maior índice como proteção ou comparar números com recortes distintos.
- **Causa:** destaque estatístico e apresentação insuficiente da população/tempo de cada medida.
- **Solução:** primeiro mostrar segmento, registros, período e qualidade. Detalhe estatístico contém coeficiente, `n`, dependências e sensibilidade. Nomear separadamente os três escopos; fornecer tabela para um segmento sem inventar correlação. Não somar PRF/ANTT, não deduplicar eventos pela chave data/km e não produzir taxa por exposição com soma de radares.
- **Aceitação:** cada contagem informa território e datas; um segmento não gera coeficiente; legenda explica datas comuns dentro do segmento. Os valores reproduzidos em 2/5/10 km ficam disponíveis em detalhe. Poucos/nenhum registro nunca geram selo de segurança. CT-08/22/23.
- **Dependências/esforço:** SEN-001/005/009; médio.

### SEN-012 — Tornar o relatório uma entrega autossuficiente

- **Prioridade/tipo:** P2; lacuna comprovada do documento exportado.
- **Componente:** src/antt_report.py e download.
- **Descrição:** exportação funciona, mas não leva todos os elementos para localizar o ponto, reproduzir a análise e compreender por que foi indicado.
- **Evidência:** UI-011/012/033; arquivo real de Criciúma informa município/ID, mas não km/sentido, URLs e justificativa individual.
- **Impacto:** relatório perde valor fora do aplicativo e pode ser interpretado sem o contexto necessário.
- **Causa:** template genérico e referência a caminho interno.
- **Solução:** consumir o catálogo de SEN-002 e a síntese de SEN-003. Incluir seleção completa, local, definição, contagens, cobertura, regra aplicada, restrições, contexto compatível, fontes e versão. Indicar se o contexto não foi calculado, em vez de sugerir que sempre foi.
- **Aceitação:** arquivo aberto isoladamente permite identificar ID/km/sentido, período, numerador/denominador, método e quatro URLs; narrativa muda com a evidência; valores conferem com a tela. Não há promessa de arquivos externos que não acompanham o relatório. CT-04/07/24.
- **Dependências/esforço:** SEN-002/003/009/010/011; médio.

### SEN-013 — Corrigir conteúdo encoberto e padronizar a leitura numérica

- **Prioridade/tipo:** P2; defeito visual e comunicação numérica comprovados.
- **Componente:** margem superior, tabelas e títulos das figuras.
- **Descrição:** parte do primeiro parágrafo fica atrás do cabeçalho; casas decimais e separadores diferem entre cartões, gráficos, tabela e relatório; ranking padrão exibe apenas 12 de 20 sem explicitar o corte.
- **Evidência:** UI-028, E01/E08; tabelas com 6.3431 e rótulos ingleses nas figuras; `padding-top:2rem` e `eq.head(12)` no código.
- **Impacto:** perda de informação territorial e esforço extra para ler medidas pequenas.
- **Causa:** CSS de espaçamento e padrões de bibliotecas sem adequação completa ao conteúdo.
- **Solução:** garantir margem abaixo do cabeçalho; usar nomes de exibição e formatação pt-BR; distinguir inteiros, proporções e índice por 10 mil; indicar “12 de N”. Preservar precisão interna.
- **Aceitação:** primeiro texto não se sobrepõe ao cabeçalho em viewports verificados; números não são cortados; índice tem precisão visual consistente de duas casas no resumo e maior precisão no detalhe; CSV mantém valores numéricos. CT-15/20/25.
- **Dependências/esforço:** SEN-006/007/009; pequeno.

### SEN-014 — Adicionar regressões que protejam os cálculos e os controles

- **Prioridade/tipo:** P2; verificação necessária às alterações. O kit externo pode conter testes, mas eles não estão na árvore do repositório inspecionado.
- **Componente:** testes analíticos e testes de interação em ambiente de desenvolvimento.
- **Descrição:** defeitos de escopo passaram até a publicação; estados de erro e vários controles não foram concluídos nesta auditoria.
- **Evidência:** UI-006/007; UI-021 a UI-024 e UI-029 a UI-032; ausência de testes na árvore do snapshot público examinado.
- **Impacto:** regressões podem produzir números corretos na unidade errada ou manter gráficos de seleções antigas.
- **Causa provável:** cobertura insuficiente de integração entre filtros e visualizações, sem confirmação do processo externo de testes.
- **Solução:** testes por comportamento, não cópias literais da implementação. Usar casos de conservação, junção sem multiplicação, nulo/zero, seleção vazia, filtros locais/globais, exportações e amostras conferidas. Concluir toolbar, mobile, teclado e leitura assistiva fora de produção.
- **Aceitação:** CT-01 a CT-26 com resultados e evidências; casos que reproduzem SEN-001 falham antes e passam depois; snapshots numéricos têm origem documentada; falhas de fonte são simuladas apenas em ambiente de teste. Nenhum teste é marcado aprovado só pela presença do componente. CT-26.
- **Dependências/esforço:** acompanha alterações anteriores; médio.

### SEN-015 — Tornar a versão e a preparação da demonstração verificáveis

- **Prioridade/tipo:** P2; limitação de verificação, sem pane de produção comprovada.
- **Componente:** informações sobre versão, carregamento e verificação prévia.
- **Descrição:** site não atesta o commit executado; desempenho, inicialização fria e concorrência não foram medidos. O README descreve infraestrutura gratuita, mas a auditoria não confirmou sua configuração real.
- **Evidência:** limitação da auditoria; VERIFICACAO_PUBLICACAO.json é registro anterior do projeto, não nova medição independente.
- **Impacto:** equipe pode demonstrar uma versão diferente da revisada ou descobrir tempo de reativação durante a apresentação.
- **Causa:** falta de identificação pública da versão e de ensaio documentado na infraestrutura efetiva.
- **Solução:** expor versão do app, snapshot e data de coleta no método; checagem de saúde/abertura; medir abertura e troca de tela em cenários definidos e preparar uma cópia de demonstração identificada pelo mesmo snapshot. Definir o orçamento de tempo a partir da medição e necessidade do pitch, sem prometer SLA inexistente.
- **Aceitação:** versão visível corresponde à revisão implantada; ensaio das cinco telas e exportações é registrado; medições distinguem abertura fria/aquecida e ambiente; fallback tem identificação e limites. Não alterar plano ou contratar recursos sem tarefa própria autorizada. CT-18/26.
- **Dependências/esforço:** SEN-014/016; médio.

### SEN-016 — Oferecer estados vazios e de erro orientados ao usuário

- **Prioridade/tipo:** P2; melhoria de robustez. Estados vazios comuns já funcionam; falha de arquivos não foi induzida.
- **Componente:** carregamento e ausência de dados.
- **Descrição:** aviso vazio é genérico; o caminho de erro orienta executar `python analisar.py`, que não existe na árvore inspecionada, e expõe mensagem interna.
- **Evidência:** UI-013/018/030; [carregamento](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py#L22).
- **Impacto:** usuário não sabe qual filtro corrigir nem como agir diante de indisponibilidade.
- **Causa:** orientação de desenvolvimento usada no fluxo público.
- **Solução:** estado de carregamento; vazio específico por ano/sentido/equipamento; falha de arquivo/contrato com mensagem simples e possibilidade de tentar novamente. Detalhes técnicos ficam no diagnóstico apropriado, sem afirmar que o erro foi observado em produção.
- **Aceitação:** seleção vazia sugere selecionar um item; sentido sem ponto informa a incompatibilidade; falha de arquivo em teste não mostra stack trace ou comando inexistente nem mantém indicadores antigos como atuais. CT-03/13/26.
- **Dependências/esforço:** SEN-002/005; médio.

### SEN-017 — Atualizar a documentação operacional a partir do estado observado

- **Prioridade/tipo:** P3; documentação desatualizada comprovada.
- **Componente:** README e verificação de publicação.
- **Descrição:** README e manifestos ainda declaram o domínio personalizado pendente, embora radarsul.site tenha servido a aplicação nesta auditoria.
- **Evidência:** UI-001 e registros de publicação no commit inspecionado.
- **Impacto:** divergência entre instrução de entrega e produto disponível.
- **Causa:** registro histórico não atualizado após configuração do domínio.
- **Solução:** separar histórico de implantação e estado verificado com data; corrigir comandos de reprodução conforme arquivos realmente disponíveis. Não afirmar acesso ao DNS ou certificado além do que foi verificado.
- **Aceitação:** documentação descreve a URL que respondeu e a data, preserva o histórico necessário e não apresenta pendência antiga como estado atual; nenhum segredo ou dado de conta pessoal é incluído. CT-18.
- **Dependências/esforço:** SEN-015; pequeno.

### SEN-018 — Levar contexto e identidade da seleção ao CSV

- **Prioridade/tipo:** P3; melhoria secundária. O CSV atual funciona e seus valores foram conferidos.
- **Componente:** exportação de comparação e metadados associados.
- **Descrição:** nome fixo e colunas técnicas não carregam claramente período, snapshot e definição de medida ao compartilhar o arquivo.
- **Evidência:** download `sentinela_comparacao.csv`, 281 bytes, sem anos ou origem no próprio conteúdo.
- **Impacto:** arquivo pode ser reutilizado fora de seu recorte ou confundido com outra exportação.
- **Causa:** exportação direta da tabela sem contexto adicional.
- **Solução:** incluir período e unidade em campos/documento de metadados associado; nome seguro e informativo; manter estrutura tabular legível por máquina e precisão. Não incluir linhas narrativas antes do cabeçalho que quebrem a leitura do CSV.
- **Aceitação:** duas seleções distintas geram arquivos distinguíveis; importação em pandas e em uma planilha preserva inteiros, decimais, acentos e IDs; nenhum item fora da seleção é exportado; não se chama contagem de “veículos únicos”. CT-01/04/24.
- **Dependências/esforço:** SEN-001/002/009/012; pequeno.

## 4. Hipóteses e verificações pendentes, sem diagnóstico fabricado

| ID de investigação | Questão ainda aberta | Como concluir | Tarefa relacionada |
|---|---|---|---|
| INV-001 | Por que há volumes tão reduzidos em 29/08/2025? | Conferir documento de origem, semântica de publicação, incidentes/operacional e esclarecimento do publicador; manter causa desconhecida até evidência | SEN-004 |
| INV-002 | Qual revisão está efetivamente em produção? | Identificador da aplicação e comparação com implantação, somente leitura | SEN-015 |
| INV-003 | Busca, colunas e tela cheia funcionam integralmente? | Repetir em navegador disponível, conferir resultado e arquivo/estado final; não atribuir os timeouts da ferramenta ao site | SEN-014 |
| INV-004 | Leigos e gestores compreendem o significado das saídas? | Ensaio formativo com tarefas e perguntas de interpretação, registrando evidências reais | SEN-006 |
| INV-005 | Experiência móvel, leitor de tela e desempenho atendem à demonstração? | Executar cenários específicos da especificação em ambiente adequado | SEN-007/014/015 |

Não criar tarefas duplicadas para essas investigações: elas detalham pendências das tarefas relacionadas.

## 5. Restrições que a implementação deve preservar

1. Não desbloquear B/A com simples agregação, exclusão de pares inconsistentes ou normalização artificial.
2. Não produzir probabilidade de acidente, causalidade ou classes absolutas de risco.
3. Não preencher ausências como zeros reais nem fabricar classe de veículo ou faixa física.
4. Não deduplicar acidentes por data/km como se essa chave identificasse o evento.
5. Não somar PRF e ANTT nem dividir acidentes por uma soma de radares como taxa por exposição.
6. Não deslocar limites de 2026 para anos anteriores sem histórico comprovado.
7. Não reduzir o corte da coorte só para incluir Criciúma. Qualquer sensibilidade permanece separada e identificada.
8. Não substituir problemas concretos por redesenho decorativo ou modelos preditivos complexos.

## 6. Condição de conclusão da implementação posterior

A implementação estará pronta para revisão quando as tarefas P1 estiverem concluídas, as exportações e números permanecerem reconciliados, os testes afetados e pendentes relevantes tiverem evidências, e a demonstração descrever exatamente o que o produto entrega. Um backlog implementado não transforma automaticamente um estudo descritivo em modelo validado de previsão. Publicação e serviços de produção pertencem a uma etapa posterior; não foram modificados por esta auditoria.
