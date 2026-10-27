# Auditoria independente do SENTINELA

**Consulta:** 27/10/2026, referência de data em America/Sao_Paulo.  
**Produto inspecionado:** https://radarsul.site/ — SENTINELA 2.0.  
**Repositório:** https://github.com/limixin1/radarsul.  
**Revisão de código inspecionada:** `e5baed4fdab7575690a408f4ab492fd63790a00e`.  
**Natureza:** diagnóstico. Nenhum commit, alteração no banco, correção do aplicativo ou implantação foi realizado.

Este relatório deve ser lido com [BACKLOG_SENTINELA.md](BACKLOG_SENTINELA.md), [ESPECIFICACAO_SENTINELA.md](ESPECIFICACAO_SENTINELA.md) e [FONTES_E_VALIDACOES.md](FONTES_E_VALIDACOES.md). As propostas nesses documentos ainda não estão implementadas.

## 1. Resumo executivo

**O SENTINELA cumpre parcialmente a proposta.** Há um painel descritivo funcional, baseado em registros públicos identificáveis, com cálculos centrais reproduzidos nesta auditoria. A experiência publicada ainda não entrega, de forma suficientemente direta, a seleção de situações que merecem investigação preventiva acompanhada de justificativa específica por local.

A aplicação atual já bloqueia a taxa entre possíveis infratores e tráfego. Isso é correto. Seu indicador principal é outro: a quantidade publicada nas faixas de velocidade acima de 120 km/h, dividida pelas contagens de todas as faixas publicadas da própria base de tráfego, multiplicada por 10.000. Ele não deve ser apresentado como taxa de infrações, proporção do tráfego real completo ou probabilidade de acidente.

Foram confirmados, a partir dos CSVs fornecidos no projeto e com hashes iguais aos do manifesto do repositório:

- Coorte principal de 20 dos 42 equipamentos, selecionados por publicação em pelo menos 90% dos dias de cada ano de 2024 e 2025.
- 226.870.300 contagens e 57.163 nas faixas acima de 120 km/h nessa coorte. Índice agregado ponderado: **2,519633 por 10 mil**.
- Maior índice individual: VC101-9, Laguna, km 304, sentido Decrescente: 7.091 / 11.178.995 × 10.000 = **6,343146 por 10 mil**.
- Spearman entre índices de 2024 e 2025 dos mesmos 20 pontos: **0,962406**. Isso descreve estabilidade de ordenação, sem validar previsão ou risco.
- Incompatibilidade prática entre as bases de tráfego e possíveis infratores. Mesmo agregando as faixas por equipamento e dia, restam 17 correspondências com possíveis infratores superiores ao tráfego publicado.

Problemas centrais comprovados:

1. A seleção local do comparador atualiza a tabela, mas não o gráfico de persistência. Com um radar selecionado, permanecem 20 pontos no gráfico.
2. No histórico, a seleção local altera as linhas temporais, enquanto o mapa de calor continua usando o conjunto territorial completo. O escopo distinto não é explicitado.
3. Fontes detalhadas e regras importantes existem no repositório, mas a interface oferece apenas um link genérico ao portal e o relatório exportado remete a um caminho interno sem trazer as URLs.
4. Contar dias com qualquer publicação não demonstra completude diária. Em 29/08/2025, 36 equipamentos somam apenas 698 contagens; VC101-30 tem 22, contra mediana diária de 14.745,5 no ano. A causa não foi determinada.
5. A comunicação começa por índices e coeficientes técnicos, sem uma resposta simples sobre o local e o motivo de investigar. O relatório repete encaminhamentos genéricos.

**Não foi confirmado P0 nos resultados centrais examinados.** Os problemas prioritários são P1. Isso não equivale à aprovação integral: controles auxiliares, dispositivos móveis, leitores de tela e falhas de carregamento não tiveram validação completa.

## 2. Escopo, método e força das evidências

Foram combinadas navegação real, inspeção visual, leitura da estrutura acessível da página, downloads produzidos pelo aplicativo, leitura de código fixada em um commit e recálculo independente dos CSVs. O recálculo não importou as funções analíticas do aplicativo e não executou seu procedimento de geração de dados.

Classificação usada para afirmações sobre dados:

| Marca | Significado |
|---|---|
| F | Confirmado pela inspeção dos arquivos locais do projeto, após conferência de hash. Não significa download oficial novo nesta sessão. |
| M | Confirmado apenas nos metadados/páginas oficiais recuperados na consulta. |
| I | Inferência ou hipótese, indicada expressamente. |
| NV | Não verificado. Não pode ser tratado como resultado confirmado. |

Observações do produto são identificadas por testes `UI-*`; verificações quantitativas, por `DV-*`; problemas, por `SEN-*`. As capturas `E01` a `E08` estão em `evidencias/capturas/`. O arquivo `evidencias/observacoes_ambiente.json` registra o viewport e observações estruturais.

O site respondeu e permitiu testar as cinco telas em um navegador desktop de **1363 × 936 px**. A identidade do commit efetivamente em execução não foi comprovada por um identificador exibido pela aplicação. A correspondência entre site e código foi sustentada pelos textos, fluxos, valores e exportações observados, sem assumir identidade integral do ambiente de produção.

## 3. Inventário do produto efetivamente publicado

Há uma aplicação Streamlit em uma URL principal. As cinco opções do menu são estados internos, não cinco rotas independentes com filtros compartilháveis por URL.

| Tela/componente | Conteúdo e controles encontrados | Observações |
|---|---|---|
| Barra lateral | Nome SENTINELA 2.0, subtítulo, menu de cinco opções, anos 2022–2026, quatro recortes territoriais, sentidos Crescente/Decrescente, avisos sobre coleta e indicador bloqueado | A nomenclatura “coorte comparável” exige explicação; sentido por crescimento da quilometragem não é traduzido para destinos. |
| Visão geral | Título com maior índice, cartões de equipamentos, contagens, contagens acima de 120 e dias distintos; ranking horizontal de até 12 equipamentos | Não identifica o município do maior valor no título. O agregado 2,52 não é o máximo 6,34. Não há indicação explícita de “12 de 20” no gráfico padrão. |
| Comparador de equipamentos | Multisseleção local, tabela com oito colunas, download CSV, dispersão 2024 × 2025, contagens separadas de possíveis infratores | Tabela e gráfico usam seleções diferentes. Campos técnicos, como `altas` e `por_10_mil`, aparecem diretamente. |
| Evolução e persistência | Multisseleção local, linhas mensais, mapa de calor por equipamento/mês, avisos sobre lacunas | O “mapa” existente é um mapa de calor temporal; não é um mapa geográfico. Linhas e mapa de calor usam escopos diferentes. |
| Contexto rodoviário | Dispersão de índice × registros de acidentes, tabela de segmentos de 5 km, dias comuns, contagem num envelope territorial, contexto PRF independente | Destaque principal para Spearman negativo. Existem avisos corretos sobre causalidade e repetições. PRF é explicitamente do trecho integral, mesmo no filtro local. |
| Relatório preventivo | Escopo geral ou radar individual, documento Markdown na página e download `.md` | Exportação funciona e valores locais conferem. Recomendações não se adaptam às evidências do local; faltam URLs diretas e localização detalhada no arquivo. |
| Método, cadastro e fontes | Expansível no fim das telas, texto sobre limiar de 120 e cadastro de 2026, tabela cadastral, link ao portal ANTT | Não contém uma fórmula completa, catálogo dos quatro recursos ou explicação integral da seleção e sensibilidade. |
| Controles auxiliares | Barras Plotly com zoom, arraste, escala automática, restauração, PNG e tela cheia; tabelas com colunas, busca, CSV e tela cheia | A presença foi inventariada. O funcionamento de todos esses controles não foi aprovado: ver limitações e registro de testes. |
| Estados vazios | Ausência global de registros; ausência de equipamentos no histórico; contexto sem segmentos comparáveis suficientes | Estados observados sem inventar zeros. Há oportunidade de indicar precisamente qual filtro causou a ausência. |

Não foram encontrados no aplicativo publicado: mapa geográfico, filtro de categoria veicular, filtro de faixa física, seletor de intervalo mensal, cadastro de decisões do gestor, probabilidades de acidente, modo de simulação ou barras qualitativas “Elevado/Baixo/Atenção”. A inexistência desses controles foi verificada no inventário e no código; não se atribuiu falha de execução a funcionalidades inexistentes.

### Arquitetura observada no repositório

`app.py` chama `app_antt.main()`. A aplicação lê seis arquivos Parquet ANTT e `resumo_antt.json`; o contexto PRF lê um Parquet adicional quando disponível. Não há conexão com banco no fluxo examinado. Os dados são um snapshot empacotado e carregado com cache, sem atualização automática das fontes oficiais a cada visita.

`src/antt.py` contém o processamento, validações, agregações e seleção da coorte; `src/antt_charts.py`, as cinco figuras; `src/antt_report.py`, o relatório. A configuração de implantação é um serviço web Python/Streamlit. Essa leitura não constitui auditoria de segurança, análise de carga ou inspeção da configuração real do provedor.

## 4. Matriz de conformidade com a proposta

| Requisito | Classificação | Fundamentação verificável |
|---|---|---|
| R01 — Dados públicos verificáveis | Atendido | Quatro recursos oficiais identificados; quatro CSVs locais conferidos com os hashes declarados; resultados principais reproduzidos. Limitação de novo download oficial descrita em fontes. DV-001/003. |
| R02 — BR-101 Sul pertinente | Atendido | 42 pontos da ViaCosteira, BR-101/SC, em 15 municípios, incluindo Criciúma e entorno. A cobertura é dos radares publicados, não da malha urbana regional. DV-002/010. |
| R03 — Identificação/localização | Atendido | IDs, município, km e sentido disponíveis; coordenadas existem nos arquivos. Um ponto sem correspondência no cadastro de referência é preservado com dados de localização da base A. Falta mapa, mas a localização textual existe. |
| R04 — Comportamento de velocidade/possíveis infrações | Atendido | Índice descritivo das faixas de velocidade da base A e contagens B separadas. A fórmula candidata B/A está corretamente bloqueada. DV-003/005/006. |
| R05 — Comparação entre equipamentos quando válida | Parcialmente atendido | Índices e denominadores reproduzidos; escopo do gráfico diverge da seleção; cobertura não assegura completude nem contexto equivalente. UI-006, DV-014. |
| R06 — Evolução/persistência | Parcialmente atendido | Séries mensais, lacunas e correlação entre anos existem. Mapa de calor ignora seleção local; persistência por radar não vira diagnóstico acessível. UI-007/008, DV-007. |
| R07 — Categoria/faixa/sentido | Parcialmente atendido | Sentido funciona. Categoria útil está ausente/não classificada nas duas bases; faixa física comparável não foi demonstrada. Esses dois recortes são inviáveis neste snapshot sem esclarecimentos ou novos dados. DV-009. |
| R08 — Contextualização com acidentes | Parcialmente atendido | Segmentos disjuntos e datas comuns implementados e reproduzidos. Contagens não são taxas ajustadas; vários escopos territoriais/temporais coexistem na tela e precisam ficar mais claros. UI-009/010, DV-008/011. |
| R09 — Situações para investigação preventiva | Não atendido | Ranking e correlação não geram uma lista de casos com evidência comportamental, restrições e motivo específico de investigação. A regra de quartis existente nos resultados não é apresentada como fluxo de investigação. SEN-003. |
| R10 — Diagnósticos explicáveis | Parcialmente atendido | Relatório fornece medidas e limites, mas encaminhamentos são iguais para todos os locais e não exibem uma cadeia de justificativa individual. UI-011/012. |
| R11 — Método documentado/verificável | Parcialmente atendido | Documentação e código acessíveis no repositório, mas método e links insuficientes no produto e no relatório exportado. UI-003/033, SEN-002. |
| R12 — Incertezas/limitações | Parcialmente atendido | Avisos sobre publicação, ausência, causalidade, anos parciais e B/A existem. Sensibilidade e anomalias de publicação não chegam à decisão; não há certificação de completude. DV-013/014. |
| R13 — Dados reais × simulações | Atendido | Dados reais de um snapshot; nenhuma simulação ou valor ilustrativo foi encontrado como resultado factual nos fluxos examinados. As barras atuais têm eixo numérico e unidade. |
| R14 — Público não técnico | Parcialmente atendido | Navegação curta e filtros visíveis. Termos e coeficientes técnicos dominam os resultados. Esta é avaliação heurística; compreensão real por leigos não foi medida. UI-032. |
| R15 — Utilidade para gestores | Parcialmente atendido | CSV, localização e histórico ajudam a explorar. Faltam priorização explicável por local, contexto organizado e relatório autossuficiente. |
| R16 — Diferencial inovador demonstrado | Parcialmente atendido | Análise começa por velocidade e mantém acidentes como contexto, mas o mecanismo preventivo não está demonstrado como decisão operacional. Não foi comprovada originalidade global ou inexistência de similares. |
| R17 — SENTINELA/RadarSul | Atendido | O aplicativo se identifica como SENTINELA; RadarSul funciona como domínio/nome de hospedagem, e o README explica essa relação. Não há necessidade demonstrada de renomear o produto. |
| R18 — Funcionamento técnico/visual | Parcialmente atendido | Cinco telas e duas exportações funcionaram nos cenários concluídos. Há inconsistências de filtro, conteúdo encoberto e lacunas de acessibilidade; parte dos controles e o comportamento móvel ficaram sem teste completo. |

## 5. Auditoria de UX, UI e comunicação

### 5.1 Primeira visita e experiência em camadas

A identidade visual é relativamente sóbria: fundo claro, texto escuro, barras em uma cor e menu consistente. Os gráficos quantitativos são mais defensáveis que barras qualitativas sem escala. Não há evidência para recomendar uma troca geral de paleta, tipografia ou tecnologia por preferência estética.

O problema de hierarquia é concreto. O usuário vê uma definição longa do indicador, um máximo sem local no título e números agregados. Precisa descobrir por conta própria o que fazer com isso. Em outras telas, o destaque “Spearman” exige formação estatística e pode deslocar o foco para uma associação negativa com acidentes.

- **Camada 1 atual:** há números e gráficos, mas falta resultado simples ligado ao local e à ação de investigação.
- **Camada 2 atual:** evidências estão distribuídas por tabela, histórico e avisos; o vínculo entre elas não é explícito.
- **Camada 3 atual:** parcialmente presente em um expansível curto e, com mais detalhe, fora do site no repositório.

Recomenda-se começar por “Explore os registros de velocidade e veja quais padrões merecem investigação”, indicar o período e permitir abrir o local, suas evidências e o método. Alertas que realmente limitam a interpretação devem ficar junto do resultado afetado. Detalhes de junção, hash e sensibilidade podem ficar em seções expansíveis.

### 5.2 Perspectivas dos três públicos

| Público | O que já consegue fazer | Barreira principal |
|---|---|---|
| Leigo | Navegar entre cinco telas e mudar filtros | Entender “coorte”, “por_10_mil”, cobertura e Spearman; distinguir máximo individual de agregado; perceber a diferença entre excesso analítico e infração legal. |
| Gestor | Encontrar município/km e baixar comparação e relatório | Obter justificativa específica de investigação, localizar visualmente o ponto e separar evidência comportamental de deficiência de publicação. |
| Avaliador técnico | Rastrear fórmulas e resultados pelo repositório | Verificar tudo dentro da demonstração, identificar a versão executada e obter fontes diretamente no relatório exportado. |

### 5.3 Termos e textos substitutos

| Termo/texto | Avaliação | Substituição pronta ou condição de uso |
|---|---|---|
| Frequência relativa | Correto como proporção de unidades comparáveis. Não descreve a fórmula B/A neste produto, pois ela não foi validada. | “Percentual de passagens classificadas como possíveis infrações — indisponível: as bases ainda não têm contagens compatíveis.” |
| Índice acima de 120 por 10 mil | Aritmeticamente correto para as contagens publicadas; precisa explicitar a base e não equivaler a infrações. | “Contagens nas faixas acima de 120 km/h a cada 10 mil contagens publicadas.” |
| Possíveis infrações/infratores | É nomenclatura do conjunto oficial, não confirmação de autuação ou pessoa identificada. | “Contagens classificadas como possíveis infratores pela fonte ANTT. Não representam autuações confirmadas nem pessoas únicas.” |
| Diagnóstico preventivo | Coerente como apoio à investigação, mas forte demais para um relatório só com medidas e lista genérica. | “Síntese para investigação preventiva”, acompanhada de evidências e de conclusão individual. |
| Comportamento preocupante | Vago sem regra e pode sugerir risco validado. | “Índice entre os 25% maiores do grupo de referência nos dois anos”, somente quando a regra for satisfeita. |
| Concentração de acidentes | Não é sinônimo de contagem em qualquer janela ou taxa de risco. | “Registros de acidentes no segmento de 5 km e nas datas analisadas.” |
| Revisão sugerida | Não aparece nos controles examinados. Exige razão verificável se for introduzida. | “Verificar este padrão: [motivo documentado].” |
| Prioridade de investigação | Aceitável como triagem explicável; não confundir com classificação de segurança. | “Investigar primeiro: padrão repetido e documentação de publicação disponível”, mostrando a regra e sem ordem automática de fiscalização. |
| Coorte comparável 2024–2025 | Termo técnico e comparabilidade mais ampla do que a cobertura demonstra. | “Grupo de comparação 2024–2025”; detalhe: “Radares com registros em pelo menos 90% dos dias de cada ano. Isso não garante publicação completa em cada dia.” |
| Crescente / Decrescente | Correto na base; pouco intuitivo para leigos. | “Quilometragem crescente” / “Quilometragem decrescente”. Não inventar destinos Norte/Sul sem validação. |
| `altas`, `por_10_mil`, `dias` | Nomes de implementação na interface | “Contagens acima de 120 km/h”, “Índice por 10 mil contagens publicadas”, “Dias com publicação”. |

O texto principal sugerido para o snapshot padrão é: **“Laguna, km 304: maior índice do grupo, com 6,34 contagens nas faixas acima de 120 km/h a cada 10 mil contagens publicadas em 2024–2025.”** O complemento deve esclarecer que isso descreve o ponto monitorado, sem prever acidentes ou confirmar infrações.

### 5.4 Gráficos e barras

As barras encontradas são quantitativas, têm origem em zero, eixo numérico, unidade por 10 mil e valores derivados dos dados. Não foram identificadas intensidades arbitrárias apresentadas como resultado real. Uma barra ocupar quase toda a largura no filtro de um único radar é efeito de escala automática; não comprova “intensidade elevada”.

Melhorias justificadas: informar quantos pontos são exibidos no ranking; localizar cada ID por município/km; separar máximo individual e índice agregado; manter a escala explicitada em comparações entre estados; impedir gráficos com escopo diferente da seleção; colocar denominação e cobertura nos detalhes. A dispersão de contexto deve mostrar `n` de segmentos e usar linguagem descritiva. Mapas de calor precisam de alternativa tabular e distinção entre índice zero publicado e informação indisponível.

### 5.5 Acessibilidade e layout

Achados observados:

- O documento declara `lang="en"`, embora o conteúdo seja português. Controles auxiliares também exibem mensagens em inglês.
- A estrutura acessível lida pelo navegador contém os controles, mas não expõe os dados dos gráficos como tabelas. As tabelas nativas do relatório expõem células; as grades visuais do comparador não apareceram dessa forma na observação acessível.
- O primeiro parágrafo principal começa em y=48 px, enquanto o cabeçalho fixo termina em y=60 px. Nas capturas, parte da apresentação territorial fica encoberta. A regra de `padding-top:2rem` no código é compatível com esse defeito.
- Edição por teclado de seletores foi executada, inclusive Backspace. Isso não comprova navegação integral por teclado nem ausência de armadilhas de foco.

Não foi realizada certificação WCAG. Testes em leitor de tela, contraste calculado, zoom de 200%/400%, viewport móvel e diferentes navegadores permanecem pendentes. A especificação adota WCAG 2.2 AA como meta de implementação, sem afirmar conformidade atual.

## 6. Auditoria científica dos dados e indicadores

### 6.1 Arquivos e atualização

Os quatro CSVs foram inspecionados a partir de `SENTINELA_bases_ANTT.zip`, já fornecido ao projeto. Seus hashes coincidem integralmente com o manifesto referido no código. As tentativas de baixar os mesmos recursos diretamente nesta sessão receberam **HTTP 200 com HTML de rejeição de 246 bytes**, não CSV. Não se declara uma nova coleta oficial bem-sucedida nem se garante que o servidor continue oferecendo exatamente o mesmo snapshot.

As páginas oficiais consultadas identificam atualizações em 28/07/2026 para tráfego, possíveis infratores e o cadastro selecionado, e em 28/01/2026 para o recurso de acidentes. Atualização do portal, cobertura dos registros e data da coleta são coisas diferentes. Os dicionários também podem ter versões e datas próprias. Inventário, hashes, esquemas e URLs estão em FONTES_E_VALIDACOES.md.

### 6.2 Fórmula candidata B/A

Considere A = contagens de tráfego e B = contagens classificadas como possíveis infratores. **B/A × 100 não foi validado e deve continuar bloqueado.**

| Verificação independente | Resultado |
|---|---:|
| IDs de equipamentos em A e B | 42 em cada base |
| Chaves B por ID/data/sentido/faixa | 71.705 |
| Chaves B sem A correspondente, após quarentena de A | 36.509 |
| Chaves B com A correspondente | 35.196 |
| B maior que A nessas correspondências estritas | 6 |
| Chaves B após agregar faixas por ID/data | 37.835 |
| Dessas, sem denominador A | 40 |
| Dessas, B maior que A | 17 |

Os códigos de faixa têm distribuições diferentes: A usa 1 apenas no sentido Crescente e 2 apenas no Decrescente; B usa 1 e 2 nos dois sentidos e 3 em parte dos registros Decrescentes. Isso evidencia falta de correspondência demonstrada, mas não permite deduzir sozinho o significado físico exato dos códigos. Agregar as faixas reduz chaves sem pareamento, mas não resolve a incompatibilidade. Não há justificativa para selecionar só pares convenientes ou descartar B>A para fabricar uma taxa válida.

Em A, 251.438 linhas não têm categoria veicular e as outras 77.972 são “Não classificado”. Em B, todas as 155.929 linhas usam “Não Classificado”. Portanto, **não há classificação útil para distinguir leves, pesados e motos neste snapshot**, apesar da presença da coluna no esquema. O cadastro de referência possui limites distintos para leves e pesados, mas isso não reconstrói a classe dos registros nem o limite histórico.

### 6.3 Indicador alternativo A-alta/A-total

O código soma A das faixas `121–140`, `141–160` e `>160`, divide pela soma de A de todas as faixas publicadas e multiplica por 10.000, sempre para o mesmo ID e período. Isso evita cruzar numerador e denominador de A/B e conserva contagens na agregação. A coorte e os números exibidos foram reproduzidos.

**Validação:** aprovado como estatística descritiva das contagens publicadas, com as limitações declaradas. **Não validado** como frequência real completa de excesso de velocidade, taxa legal de infrações, medida absoluta de perigo ou preditor de acidente.

O limiar 120 deriva dos intervalos disponíveis; não é um limiar de segurança validado para todas as características viárias. A soma não conta veículos únicos. Um veículo pode contribuir em dias e radares diferentes. O agregado de vários sensores deve ser tratado como contagens em pontos monitorados, não população de condutores.

O denominador agregado deve ser a soma das contagens comparáveis. Uma média simples de índices por radar ou mês não substitui a razão entre somas. Não estimar velocidade média usando pontos médios dos intervalos, especialmente pela classe aberta `>160` e pela ausência de velocidades individuais.

### 6.4 Completude, ausências, sobreposição e incerteza

Há 384 linhas com chave de tráfego ambígua em 30/04/2023. A rotina coloca em quarentena os 41 equipamentos-dia envolvidos: 420 linhas e 526.390 contagens. A auditoria reproduziu essa decisão conservadora. Ela não afeta diretamente os totais principais de 2024–2025.

A cobertura anual mede dias com algum registro / dias do calendário. O corte de 90% seleciona a população analítica e não certifica operação contínua, cobertura horária ou publicação de todas as faixas. O mesmo vale para o corte mensal de 80%.

Exemplo de alerta de qualidade: em 29/08/2025, 36 radares somam apenas 698 contagens e zero nas faixas altas publicadas. VC101-30 apresenta 22 contagens em duas faixas; a mediana de seus dias publicados de 2025 é 14.745,5. A hipótese de publicação parcial merece investigação, mas não foi comprovada como falha do equipamento ou da ANTT. O fato não autoriza exclusão automática ou preenchimento com médias.

Uma faixa sem linha publicada não comprova zero passagens reais. Zero no índice pode ser uma soma publicada sem linhas positivas nas faixas altas; sua interpretação precisa preservar essa condição. Em B, ausência de linhas pode também se relacionar ao modo de publicação de possíveis infratores. Não se deve tratar os dias sem linhas de B como dias de funcionamento comprovado com zero infrações.

Sensibilidade confirmada da seleção:

| Mínimo anual de dias publicados, em ambos os anos | Equipamentos | Índice agregado por 10 mil |
|---|---:|---:|
| 80% | 27 | 2,539985 |
| 90% | 20 | 2,519633 |
| 95% | 9 | 3,522462 |

Os totais elevados de contagens não eliminam vieses de seleção, autocorrelação temporal, repetição de passagens ou problemas de medição. Intervalos binomiais calculados como se cada passagem fosse uma observação independente completa poderiam dar precisão enganosa. Para o MVP, priorizar cobertura, denominadores, quantidade de dias/pontos, dispersão mensal e sensibilidade. Qualquer inferência adicional exige desenho amostral/modelo explícito; não há obrigação metodológica de adicionar p-valores a este estudo descritivo.

### 6.5 Persistência

O coeficiente 0,962406 indica que a ordenação dos 20 índices anuais se mantém semelhante entre 2024 e 2025. Ele não identifica sozinho quais pontos devem ser investigados, não mede crescimento temporal e não valida previsão.

Os resultados do processamento já registram quatro pontos no quartil superior nos dois anos: **VC101-39, VC101-4, VC101-7 e VC101-9**. Limiares anuais: 4,072839831 por 10 mil em 2024 e 3,672802845 em 2025. Essa regra é relativa ao grupo, não um limite universal de segurança. Sua exposição, com cobertura e limites, é uma alternativa transparente para construir a triagem preventiva que falta na interface.

### 6.6 Acidentes e relação espacial

A base ANTT contém 8.841 linhas entre 01/05/2021 e 31/12/2025; 3.499 estão em 2024–2025. São quatro colunas, sem ID único, horário, gravidade ou sentido. Há 187 repetições integrais além da primeira. Preservá-las é defensável: elas podem representar ocorrências distintas no mesmo dia/km. Também não é defensável afirmar que as 8.841 linhas equivalem a 8.841 eventos únicos comprovados.

O processamento utiliza segmentos quilométricos disjuntos e, dentro de cada segmento, apenas datas em que todos os equipamentos selecionados publicaram. A junção de acidentes é many-to-one por segmento/data, evitando multiplicar linhas por radar. A correspondência é por referência quilométrica, não por demonstração de que um radar influenciou um acidente.

Resultado reproduzido em 5 km: 16 segmentos, Spearman −0,584253; dias comuns variam de 636 a 731. Em 2 km e 10 km, os coeficientes são −0,455417 e −0,446154. As comparações usam datas comuns **dentro de cada segmento**, não necessariamente o mesmo calendário entre todos os segmentos.

Contagens não equivalem a taxas ajustadas por exposição. A soma de passagens em radares não fornece veículo-quilômetro de todo o segmento; somá-la pode contar o mesmo veículo mais de uma vez. Sem exposição, infraestrutura e regras de registro compatíveis, o sinal negativo não demonstra proteção da velocidade. Tampouco valida a afirmação de que um ponto com poucos registros seja seguro.

A aplicação ainda mostra um envelope entre os pontos selecionados, acrescido de 2,5 km, que é outro recorte. Na seleção de Criciúma, exibe 62 registros ANTT nesse envelope. O contexto PRF permanece no corredor integral: 1.750 ocorrências, das quais 36 em Criciúma. Esses números não devem ser somados ou comparados como se fossem recortes e sistemas de registro idênticos.

### 6.7 Limitação específica de Criciúma

VC101-30 está no km 391,940, sentido Crescente. Em 2024 tem 306/366 dias com publicação, 4.549.086 contagens e 1.299 nas faixas altas: 2,855519 por 10 mil. Em 2025 tem 332/365 dias, 5.011.647 e 1.113: 2,220827 por 10 mil. Está corretamente fora da coorte principal por não atingir 90% em 2024.

Não se conclui que a segurança melhorou por esse decréscimo. O ponto pode ser explorado com aviso de cobertura, sem alterar a regra para incluí-lo artificialmente. A pertinência regional do projeto deve ser apresentada com essa restrição local, além dos pontos do entorno.

## 7. Registro de testes do produto

“Aprovado” significa que o resultado esperado daquele teste foi observado, não aprovação integral do componente. Testes de criação de erro não foram executados em produção. Quando a navegação deixou de responder, os resultados pendentes foram mantidos como inconclusivos/não testados.

| ID | Página/componente e procedimento | Resultado esperado | Resultado observado e evidência | Situação |
|---|---|---|---|---|
| UI-001 | Abrir https://radarsul.site/ | Carregar aplicação e controles | Menu, filtros e dados disponíveis; E01; HTTP GET 200 | Aprovado |
| UI-002 | Examinar ranking e cartões padrão e confrontar CSV | Valores e escala coerentes | 20; 226.870.300; 57.163; 731; máximo 6,34; E01/DV-003 | Aprovado |
| UI-003 | Abrir “Método, cadastro e fontes” | Acessar método verificável | Expansível abre, cadastro e portal presentes; fórmula e quatro URLs ausentes | Parcialmente funcional |
| UI-004 | Navegar pelas cinco opções laterais | Cada opção abrir seu conteúdo | Cinco títulos/conteúdos observados, E01/E02/E05/E06 e DOM do relatório | Aprovado |
| UI-005 | Baixar comparação padrão | CSV legível com seleção e medidas corretas | Arquivo de 281 bytes, três radares; conferência independente integral dessas linhas | Aprovado |
| UI-006 | Remover VC101-9 e VC101-39 do comparador | Tabela e gráfico refletirem VC101-4 | Tabela fica com um radar; dispersão permanece com 20 pontos; E04; código app_antt.py:53 | Falhou |
| UI-007 | No histórico, reduzir seleção para VC101-9 | Visualizações da seleção usarem o mesmo conjunto | Linha de um radar; mapa de calor mantém 20 linhas; observação DOM e app_antt.py:64 | Falhou |
| UI-008 | Remover o último equipamento do histórico por Backspace | Estado vazio, sem gráfico residual após conclusão | “Selecione ao menos um equipamento para o histórico.” | Aprovado |
| UI-009 | Abrir contexto no padrão 2024–2025 | Gráfico e tabela com contexto documentado | Dispersão e tabela; cálculo dos 16 segmentos reproduzido; E06/DV-008 | Aprovado |
| UI-010 | Mudar contexto para Criciúma | Não forçar associação sem segmento elegível | Aviso de insuficiência, 62 registros no envelope, PRF explicitamente integral; E07 | Aprovado |
| UI-011 | Gerar e baixar relatório de Criciúma | Arquivo consistente com medidas selecionadas | 2.760 bytes; 9.560.733 e 2.412; índice 2,523; cobertura e limites presentes | Aprovado |
| UI-012 | Escolher escopo VC101-30 e apenas 2024 | Recalcular relatório para o ano selecionado | 4.549.086, 1.299, 306 dias, 2,856; período efetivo até 10/12/2024 | Aprovado |
| UI-013 | Remover o último ano | Mostrar ausência de resultados sem zero artificial | Estado “Nenhum registro para os filtros”; dados anteriores somem após atualização | Aprovado |
| UI-014 | Selecionar 2026 e visão geral de Criciúma | Indicar parcialidade e dados desse período | Aviso até junho; 2.363.431, 516, 181 dias, 2,18; E08 | Aprovado |
| UI-015 | Selecionar todos os equipamentos em 2026 | Abranger o conjunto correspondente | 42 radares, 110.935.217 contagens, 33.259 acima do limiar | Aprovado |
| UI-016 | Selecionar entorno km 370 a 410, 2026 | Restringir território | 6 radares, 15.314.016 contagens, 4.636 acima do limiar | Aprovado |
| UI-017 | Remover sentido Crescente nesse entorno | Restar apenas Decrescente | 3 radares, 7.379.041 contagens, 2.207 acima do limiar | Aprovado |
| UI-018 | Usar Clear all de sentido | Mostrar estado sem resultados | Estado vazio após atualização, sem exceção visível | Aprovado |
| UI-019 | Buscar Crescente e usar “Select 2 matches” | Recuperar ambos os sentidos | Chips dos dois sentidos e dados reaparecem; comparador abre | Aprovado |
| UI-020 | Conferir legenda em Criciúma/2026 | Descrever o escopo realmente exibido | Texto fixo “Coorte fixa: 20 de 42” mesmo com um radar em 2026; E08 e app_antt.py:45 | Falhou |
| UI-021 | Abrir busca da primeira tabela e preencher Maracajá | Buscar e evidenciar correspondência | Campo abriu e recebeu o texto. Retorno final de correspondências não verificado após interrupção do navegador | Parcialmente funcional |
| UI-022 | Clicar Show/hide columns na tabela | Expor configuração e permitir mudar colunas | Clique executado; opção de configuração não ficou verificável no DOM/captura. Não se conclui defeito do produto | Parcialmente funcional |
| UI-023 | Conferir tela cheia da tabela | Expandir e restaurar tabela | A tentativa em lote não teve retorno; não é possível confirmar sequer a etapa final executada | Não testado |
| UI-024 | Zoom, pan, restaurar e PNG das figuras | Operar cada controle e conferir resultado | Controles inventariados, sem execução concluída desses cenários | Não testado |
| UI-025 | Editar multisseleção por teclado | Remover seleção sem mouse | Backspace removeu itens; busca em seletor funcionou. Escopo limitado a esses controles | Aprovado |
| UI-026 | Ler atributo de idioma do documento | Português identificado por tecnologia assistiva | `lang=en` em conteúdo português; observacoes_ambiente.json | Falhou |
| UI-027 | Inspecionar representação acessível dos gráficos/grades | Dados disponíveis sem depender apenas do desenho | Controles aparecem; série de valores/células das grades não aparece como tabela na observação; relatório nativo possui células | Parcialmente funcional |
| UI-028 | Comparar posição do primeiro parágrafo e cabeçalho | Texto integralmente visível | Parágrafo y=48–70,39 e cabeçalho até 60; sobreposição de 12 px; E01/E08 | Falhou |
| UI-029 | Testar viewports móveis e zoom | Refluxo adequado | Ambiente usado não expôs controle de viewport; não houve ensaio móvel | Não testado |
| UI-030 | Testar dados ausentes/corrompidos e falha de fonte | Erro seguro e recuperável | Não houve injeção em produção. Apenas leitura do caminho de erro, que menciona script inexistente no repositório | Não testado |
| UI-031 | Medir desempenho e concorrência | Tempos e consumo sob cenários definidos | Navegação funcional observada; sem benchmark, teste de carga ou medição confiável de inicialização fria | Não testado |
| UI-032 | Validar entendimento com leigos e gestores reais | Compreensão das medidas e limites | Avaliação heurística realizada; nenhum estudo com participantes executado | Não testado |
| UI-033 | Conferir referências disponíveis na página/exportação | Recursos diretos acessíveis ao usuário | Link da página leva à raiz ANTT; relatório remete a caminho interno e não traz URLs; arquivos inspecionados | Falhou |

### Verificações quantitativas executadas

| ID | Procedimento/resultado esperado | Resultado observado | Situação |
|---|---|---|---|
| DV-001 | Conferir tamanho e SHA-256 dos quatro CSVs contra manifesto | 4/4 coincidem; não são páginas HTML | Aprovado |
| DV-002 | Examinar esquema, datas, geografia, nulos, duplicatas e domínio das contagens | Perfis completos em validacao_independente.json; A/B sem contagens negativas ou fracionárias; limitações de classe identificadas | Aprovado |
| DV-003 | Recalcular dias, coorte e razão entre somas | 20 IDs, totais e extremos iguais ao resumo e à UI | Aprovado |
| DV-004 | Comparar as três linhas do CSV exportado com recálculo | Totais inteiros iguais; índices diferem menos de 1e-12 | Aprovado |
| DV-005 | Tentar pareamento A/B estrito e avaliar validade | 36.509 sem A e 6 B>A. Resultado esperado de incompatibilidade foi confirmado; indicador B/A reprovado | Aprovado |
| DV-006 | Verificar se agregar faixas resolve B/A | 40 sem A e 17 B>A. A agregação não resolve | Aprovado |
| DV-007 | Recalcular Spearman anual e quartis | 0,962406 e mesmos quatro pontos persistentes | Aprovado |
| DV-008 | Recalcular segmentos/datas e sensibilidade 2/5/10 km | Mesmos coeficientes e número de segmentos do repositório | Aprovado |
| DV-009 | Verificar se classes e faixas permitem recortes físicos | Nenhuma classe veicular útil; codificação de faixa sem correspondência demonstrada | Aprovado |
| DV-010 | Cruzar cadastro por km/sentido | 41 correspondências; VC101-20 sem referência; 42 IDs na base de tráfego | Aprovado |
| DV-011 | Examinar acidentes e repetições | 8.841 linhas, 187 repetições além da primeira, sem ID de ocorrência | Aprovado |
| DV-012 | Filtrar ZIPs PRF 2024/2025 por SC, BR-101, km 244,680–465,100 | 921 + 829 = 1.750; Criciúma 24 + 12 = 36; sem ID repetido em cada recorte anual | Aprovado |
| DV-013 | Recalcular sensibilidade da cobertura anual | 27/20/9 equipamentos e índices 2,539985/2,519633/3,522462 | Aprovado |
| DV-014 | Inspecionar anomalia de 29/08/2025 e cobertura intradiária | 36 pontos, 698 contagens; VC101-30 com 22 em duas faixas, sem comprovação da causa | Aprovado |

Os 14 testes DV aprovados confirmam a execução e o resultado da verificação, inclusive quando esse resultado é a inviabilidade de um indicador. Eles não significam que 14 indicadores científicos foram validados.

## 8. Evidências verificáveis e problemas relacionados

| Evidência | Página e teste | Achado/problema |
|---|---|---|
| E01 — SEN-E01-visao-geral.jpg | Visão geral; UI-001/002/028 | Valores padrão, escala quantitativa, excesso de tecnicidade e apresentação territorial encoberta; SEN-006/013. |
| E02 — SEN-E02-comparador.jpg | Comparador padrão; UI-005 | Cabeçalhos técnicos e três itens selecionados; SEN-006. |
| E03 — SEN-E03-filtro-comparador.jpg | Comparador em estado intermediário de duas seleções; UI-006 | Tabela com dois radares e dispersão da coorte inteira; SEN-001. |
| E04 — SEN-E04-um-radar-vinte-pontos.jpg | Comparador, seleção final VC101-4; UI-006 | Evidência principal de escopos divergentes; SEN-001. |
| E05 — SEN-E05-evolucao.jpg | Histórico padrão; UI-007 | Séries mensais, unidades e concentração de texto técnico; SEN-006. A divergência após reduzir seleção foi confirmada no DOM e no código, não nesta captura inicial. |
| E06 — SEN-E06-contexto.jpg | Contexto padrão; UI-009 | Spearman como destaque e tabela técnica; SEN-011. |
| E07 — SEN-E07-criciuma-contexto.jpg | Criciúma; UI-010 | Restrição correta da coorte, envelope ANTT e PRF integral; SEN-011. |
| E08 — SEN-E08-criciuma-2026-legenda.jpg | Visão local/2026; UI-014/020 | Captura confirma seleção local/2026 e valores. A legenda fixa, abaixo da área capturada, foi confirmada no DOM e em app_antt.py:45; SEN-009. |
| comparacao_publicada.csv | Download real do site; UI-005/DV-004 | Valores iguais ao recálculo; exportação funcional. |
| relatorio_publicado_criciuma.md | Download real do site; UI-011/033 | Medidas conferidas, referências não autossuficientes e encaminhamentos genéricos; SEN-002/003/012. |
| validacao_independente.json e CSVs de cálculo | DV-001 a DV-014 | Evidências numéricas e possibilidade de inspeção por terceiros. |
| tentativas_oficiais.json | Downloads diretos oficiais | Quatro respostas HTML de rejeição, mesmo com status 200. |

Os caminhos relativos acima são preservados no pacote de entrega. Referências ao código no backlog apontam para o commit inspecionado, para evitar dependência de uma branch que pode mudar.

## 9. Limitações da auditoria

1. O navegador controlado deixou de responder durante a conferência da busca da tabela e tentativa de expansão. Duas chamadas não retornaram dentro de aproximadamente 300 segundos cada. A segunda buscava orientação de recuperação, não executou novo teste funcional confirmado. Isso não prova falha ou queda de radarsul.site.
2. Não foram aprovados todos os controles auxiliares das bibliotecas, nem todos os cruzamentos de filtros. Zoom, pan, PNG e tela cheia ficaram sem verificação conclusiva.
3. Não foram executados testes em dispositivos móveis, Safari/Firefox, leitores de tela, contraste automatizado, carga ou indisponibilidade induzida. O produto não recebeu certificação de acessibilidade ou desempenho.
4. Não houve teste de usabilidade com participantes. Afirmações sobre compreensão são achados heurísticos, não taxas de sucesso observadas.
5. O novo download dos CSVs oficiais foi rejeitado. Os arquivos analisados são as cópias do projeto com hashes conferidos; atualização posterior dos bytes oficiais não foi excluída.
6. Apenas o dicionário A teve texto integral recuperado nesta consulta. Os PDFs B/C/D não foram confirmados integralmente. Metadados, conteúdo do CSV e documentação interna foram distinguidos.
7. Não foi investigada diretamente a causa dos volumes reduzidos de determinados dias, a operação real dos equipamentos, alterações de limites ou completude horária. Não houve contato com ANTT/concessionária.
8. Não há demonstração de correspondência perfeita entre referências quilométricas históricas, nem de que as coordenadas foram verificadas em campo. Cadastro de 2026 não reconstrói o passado.
9. O commit do código foi fixado para a auditoria, mas a versão exata em execução não foi atestada por endpoint do aplicativo. Não houve acesso ou alteração de serviços de produção.

## 10. Conclusões obrigatórias

### 1. O SENTINELA efetivamente cumpre sua proposta?

**Parcialmente.** Cumpre a base descritiva: fontes identificáveis, análise de faixas de velocidade, comparação, histórico e contexto de acidentes. Ainda não demonstra integralmente o fluxo preventivo que transforma padrões em casos explicáveis para investigação.

### 2. Quais funcionalidades já são confiáveis?

Os cálculos das contagens publicadas e do índice alternativo, a seleção principal de cobertura, os filtros globais nos cenários concluídos, as séries mensais com restrição de publicação, os downloads CSV/Markdown examinados e o bloqueio de B/A. A confiança é específica desses cenários e das cópias conferidas. O gráfico de persistência e o mapa de calor não são confiáveis quanto ao escopo da seleção local atual.

### 3. Quais indicadores não estão suficientemente validados?

B/A; frequência real de infrações; probabilidades de acidente; classificações absolutas de perigo; taxas de acidentes por exposição; efeito causal de velocidade; resultados por tipo de veículo/faixa física; uso de ausência de linha como zero real. A aritmética do índice A está confirmada, mas sua extrapolação para todo o tráfego real não foi validada. As correlações são descritivas, não validação preditiva.

### 4. O público leigo compreende a ferramenta?

**Não foi demonstrado.** A avaliação heurística encontra barreiras relevantes de vocabulário, hierarquia, localização dos resultados e distinção entre medidas. É necessário simplificar a primeira camada e realizar um teste curto com usuários.

### 5. Quais problemas impedem uma demonstração tecnicamente defensável?

Escopos diferentes sob o mesmo seletor; método e fontes difíceis de verificar no produto; conclusões preventivas genéricas; interpretação inadequada de cobertura diária; excesso de destaque a coeficientes sem contexto; lacunas de acessibilidade. Isso impede apresentar o MVP como sistema preventivo completo e validado. Uma demonstração restrita a exploração descritiva, com limites expressos e evitando os fluxos defeituosos, é sustentada pelas evidências obtidas.

### 6. Quais são as cinco correções mais importantes?

1. Unificar o efeito dos filtros em tabelas, gráficos e exportações — SEN-001.
2. Construir uma síntese preventiva específica por local, com regra relativa, evidências e estados de insuficiência — SEN-003.
3. Incorporar ao produto e aos relatórios as URLs oficiais, fórmulas, proveniência e versão — SEN-002, com SEN-012.
4. Acrescentar diagnóstico de publicação parcial e expor as limitações do denominador, mantendo B/A bloqueado — SEN-004/005.
5. Reorganizar a experiência em camadas, com nomes compreensíveis e alternativas acessíveis aos gráficos — SEN-006/007.

### 7. O projeto está pronto para seguir à implementação das correções?

**Sim, para uma implementação guiada pelo backlog e pela especificação.** Não é necessário reconstruir todo o projeto. Devem ser preservados os cálculos descritivos conferidos, as restrições de interpretação, a quarentena, a separação ANTT/PRF e o bloqueio de B/A. A implementação posterior precisa concluir os testes pendentes antes de declarar a experiência corrigida e pronta para demonstração.
