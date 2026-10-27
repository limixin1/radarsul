# Especificação funcional e metodológica do SENTINELA

**Versão da especificação:** 1.0 — 27/10/2026.  
**Destino:** implementação posterior no repositório radarsul.  
**Estado:** comportamento proposto, ainda não implementado. Esta especificação não autoriza alterar produção durante a auditoria.

## 1. Objetivo e fronteiras do produto

O SENTINELA deve apoiar a investigação preventiva de padrões observados de velocidade nos pontos monitorados da BR-101 Sul/SC. A experiência começa pelos registros de tráfego. Acidentes aparecem como contexto separado, com território, datas, unidade e limitações explícitos.

O produto entrega uma exploração descritiva e uma triagem relativa explicável. Não entrega previsão de acidentes, probabilidade de colisão, causalidade, identificação de pessoas, diagnóstico definitivo de segurança ou ordem automática de fiscalização/obra.

As regras a seguir preservam as partes confirmadas do MVP e resolvem os problemas SEN-001 a SEN-018. Não é necessário trocar o framework ou reconstruir o projeto inteiro.

## 2. Navegação e experiência em três camadas

### 2.1 Telas

| Tela atual | Nome recomendado | Função esperada |
|---|---|---|
| Visão geral | Visão geral | Apresentar seleção, medida principal, locais e padrões candidatos a investigação. |
| Comparador de equipamentos | Comparar radares | Comparar os equipamentos escolhidos com valores, publicação e restrições. |
| Evolução e persistência | Histórico de velocidade | Mostrar evolução mensal e repetição anual, sem preencher lacunas. |
| Contexto rodoviário | Acidentes no contexto | Consultar registros de acidentes em recortes claramente identificados. |
| Relatório preventivo | Síntese para investigação | Exportar seleção, evidências, interpretação limitada, fontes e próximos passos. |

SENTINELA é o nome do produto. RadarSul pode permanecer como domínio/nome de hospedagem. Não criar outra identidade concorrente na navegação.

### 2.2 Fluxo principal

1. Usuário abre Visão geral e encontra uma frase curta sobre o que o sistema faz, o recorte ativo e a definição resumida da medida.
2. Escolhe território, anos e sentidos. Esses filtros afetam todas as telas, ressalvados os contextos explicitamente identificados como referência independente.
3. Vê os locais e o motivo descritivo de indicação, ou a mensagem de que os dados não sustentam a regra.
4. Abre a ficha de um equipamento para ver contagens, datas, publicação, valores anuais/mensais, restrições e contexto espacial disponível.
5. Abre os detalhes do método quando precisar verificar fórmula, fontes, critérios e sensibilidade.
6. Exporta uma síntese ou comparação que preserve exatamente esse escopo e suas limitações.

### 2.3 Camadas

- **Camada 1 — Resultado:** município/km/ID, período, medida em linguagem simples e condição da investigação. No máximo os elementos necessários para compreender o resultado inicial.
- **Camada 2 — Evidências:** contagens, denominadores, anos, dias publicados, gráfico, motivo da regra e qualidade. Acesso próximo de cada resultado.
- **Camada 3 — Método e fontes:** fórmula, granularidade, campos, restrições, seleção, sensibilidade, URLs, hashes e versão, em expansível ou tela específica.

Advertências que mudam a interpretação imediata permanecem próximas do resultado. Detalhes de implementação e processamento não devem ocupar a primeira camada.

## 3. Modelo de escopo e filtros

### 3.1 Estado global

Manter um objeto de seleção com, no mínimo:

```text
anos_solicitados
recorte_territorial
sentidos_solicitados
ids_globais_elegiveis
snapshot_id
versao_metodo
```

`ids_globais_elegiveis` resulta da interseção de território e sentido, nunca da união. Datas efetivamente observadas e IDs com dados no período são calculados depois, sem substituir silenciosamente os filtros solicitados.

### 3.2 Contrato dos controles

| Controle | Valores/default | Comportamento |
|---|---|---|
| Anos dos registros | 2022, 2023, 2024, 2025, 2026; padrão 2024 e 2025 no snapshot atual | Multisseleção. Vazio significa seleção incompleta, sem indicador. Mostrar diferença entre anos solicitados e cobertura efetiva. |
| Grupo de comparação 2024–2025 | Os 20 IDs fixos validados no snapshot | Pertencimento depende de pelo menos 90% dos dias de cada ano. Não promete completude nem elegibilidade automática em 2022/2023/2026. |
| Todos os equipamentos | 42 IDs da base A auditada | Inclui pontos fora da coorte com aviso e cobertura individual. Não os chama automaticamente de comparáveis. |
| Criciúma | VC101-30 no snapshot auditado | Mostrar km 391,940 e sentido informado pela fonte. Alertar cobertura de 2024 insuficiente para a coorte principal. |
| Entorno de Criciúma | km >= 370 e km < 410 | Explicar no detalhe que o limite 410 é exclusivo. Não substituir esse recorte por limites municipais presumidos. |
| Sentido | Crescente e Decrescente; padrão ambos | Exibir “Quilometragem crescente/decrescente”. Não converter para destinos ou pontos cardeais sem validação. |
| Equipamentos locais | IDs que possuem registros no escopo global | Seleção usada por tabela, figuras locais e exportação da tela. Padrão inicial pode manter os três maiores índices, explicitamente identificados como seleção inicial. |
| Categoria veicular | Indisponível neste snapshot | Não criar opções leves/pesados/motos a partir de “Não classificado”. Explicar no método. |
| Faixa física | Indisponível para comparação validada A/B | Não apresentar códigos como se a mesma faixa física estivesse comprovada entre bases. |

Quando o filtro global mudar, preservar os IDs locais que ainda forem válidos. Remover os inválidos e informar isso. Se a interseção ficar vazia, apresentar seleção vazia; não escolher silenciosamente novos três pontos como se fossem a escolha anterior do usuário.

### 3.3 Sincronização

Todos os gráficos descritos como “da seleção” usam os IDs locais efetivos e os mesmos anos/sentidos. Uma referência fixa de quartis pode usar a coorte completa, desde que identificada como **grupo de referência**, sem transformar a figura em um conjunto não selecionado.

No comparador, a persistência usa apenas a interseção entre seleção local e pontos com índices nos dois anos elegíveis. Com um ponto, exibir os dois valores e informar que não há correlação entre pontos a calcular. Com zero, estado vazio. Com dois ou mais, uma correlação descritiva pode ser exibida em detalhes, com `n` explícito. Dois pontos não sustentam uma conclusão estatística ampla mesmo que o coeficiente seja ±1.

No histórico, linhas e mapa de calor usam o mesmo conjunto local. Se houver opção adicional de mapa de calor do conjunto inteiro, ela deve ser uma escolha separada, rotulada e desligada por padrão.

### 3.4 Resumo persistente da seleção

Mostrar: anos solicitados, datas observadas, território, sentidos, quantidade de equipamentos exibidos e snapshot. “Datas distintas no recorte” significa união das datas publicadas; fornecer dias por equipamento/ano para que 731 não pareça operação completa de todos os sensores.

## 4. Contrato dos dados e validações

### 4.1 Entradas

| Base | Grão observado | Chave/identificação | Limitação essencial |
|---|---|---|---|
| A — Tráfego | Contagem por equipamento, data, sentido, código de faixa, intervalo de velocidade e campo de categoria | ID do equipamento + dimensões publicadas | Categoria sem informação útil; cobertura intradiária desconhecida. |
| B — Possíveis infratores | Contagem nas dimensões publicadas da própria base | Mesmo domínio de IDs, sem compatibilidade demonstrada de todas as dimensões | Não é pessoa única ou autuação confirmada; não há denominador A validado. |
| C — Acidentes | Linha com concessionária, data, km e trecho | Não há ID único de evento | Repetições não podem ser resolvidas automaticamente; sem gravidade/sentido/horário. |
| D — Cadastro | Equipamento por atributos cadastrais e localização no snapshot | Não possui o mesmo identificador de A/B; associação espacial controlada | Referência de 2026, não histórico de limites nem instalação. |

Os nomes dos arquivos, URLs e hashes são os de FONTES_E_VALIDACOES.md. Dados originais devem ser preservados; transformações e saídas precisam de versão.

### 4.2 Validações obrigatórias

1. Arquivo tem bytes, tipo e estrutura compatíveis. HTTP 200 e extensão `.csv` são insuficientes. Rejeitar HTML de erro como dados.
2. Decodificar corretamente os CSVs inspecionados: A/B/D em Latin-1; C em UTF-8 no snapshot atual. Detectar/validar alterações, sem aceitar caracteres corrompidos silenciosamente.
3. Exigir campos esperados, datas válidas e contagens inteiras não negativas. Bin de velocidade novo/indefinido não é convertido por aproximação.
4. Controlar duplicidade nas chaves antes de somar; preservar a quarentena do snapshot e registrar qualquer mudança de regra.
5. Junções cadastrais não multiplicam contagens. Chaves sem referência ficam identificadas como ausentes, sem associação por vizinho presumida.
6. Validar consistência temporal de ID, km e sentido. Mudança comprovada exige separar históricos, não usar apenas o primeiro valor.
7. Reconciliar somas após cada agregação; nenhum filtro pode misturar numerador selecionado com denominador geral.
8. Conservar ausências e zero como estados distintos. Não completar faixas ou dias com zero sem regra da fonte que comprove esse significado.

## 5. Indicadores permitidos e bloqueados

### 5.1 Medida principal disponível

Para equipamento `e` e conjunto de datas `T`:

```text
H(e,T) = soma de volume_total de A nas faixas 121–140, 141–160 e >160
N(e,T) = soma de volume_total de A em todas as faixas publicadas comparáveis
I(e,T) = 10.000 × H(e,T) / N(e,T), se N(e,T) > 0
```

Nome: **“Contagens nas faixas acima de 120 km/h por 10 mil contagens publicadas”**.

Limitação imediata: **“Descreve os registros publicados nos pontos monitorados. Não é taxa de autuações nem probabilidade de acidente.”**

O numerador é subconjunto do denominador da mesma base e do mesmo escopo. Para combinar meses/equipamentos, calcular `10.000 × soma(H) / soma(N)`. Não usar média simples de índices. Não interpretar soma entre sensores como veículos distintos no corredor.

Com N ausente ou zero, o resultado é indisponível, sem infinito ou zero artificial. H=0 significa que não há contagens positivas publicadas nas faixas altas na seleção; não comprova ausência de passagem real acima do limiar se as faixas não tiverem completude demonstrada.

### 5.2 Fórmula candidata original

```text
F = 100 × passagens classificadas como possíveis infrações / passagens comparáveis
```

**Estado no snapshot auditado: indisponível.** A/B não passam nas verificações de universo, faixa e contagem. Mesmo a agregação por ID/data deixa 17 B>A e 40 chaves sem A. Não liberar a fórmula removendo os pares problemáticos, escolhendo outro denominador conveniente ou calculando percentuais de números incompatíveis.

Uma futura liberação exige documento de equivalência de unidade, faixa/categoria, critério de classificação, cobertura de tempo, funcionamento e conservação das contagens, além de testes. Essa investigação não integra as correções automáticas deste MVP e não tem resultado favorável presumido.

### 5.3 Outras medidas

Permitidas como descrição: contagens A e B separadas, dias com linhas, cobertura de dias do calendário, índices mensais/anuais e comparações com grupo nomeado. Correlações podem aparecer em detalhes, com população, `n`, período e limites.

Não disponíveis: frequência legal de infrações, velocidade média por pontos médios dos bins, probabilidade de acidente, causalidade, taxa por veículo-quilômetro sem exposição, pessoas/veículos únicos, eficácia de fiscalização e classificação absoluta de “seguro/perigoso”.

### 5.4 Valores de referência para regressão

| Caso do snapshot | Resultado de referência |
|---|---|
| Coorte principal, 2024–2025 | 20 pontos; N=226.870.300; H=57.163; I=2,519633464583068 |
| VC101-9, 2024–2025 | N=11.178.995; H=7.091; I=6,343146230944732 |
| VC101-19, 2024–2025 | N=8.551.963; H=632; I=0,7390116163973114 |
| VC101-30, 2024 | N=4.549.086; H=1.299; 306 dias; I=2,8555186690249426 |
| VC101-30, 2025 | N=5.011.647; H=1.113; 332 dias; I=2,220826806038015 |
| VC101-30, 2026 parcial | N=2.363.431; H=516; 181 dias; I arredondado=2,18 |

Esses valores são referências do snapshot conferido, não constantes a embutir no cálculo. Um novo snapshot precisa de nova reconciliação e de revisão das classificações.

## 6. Publicação, qualidade e incerteza

### 6.1 Cobertura

`cobertura_anual = dias com registro / dias do ano`. 2024 tem 366 dias. Para a coorte principal, exigir cobertura >=0,90 em cada um dos dois anos e índices calculáveis. O grupo permanece identificado pelo snapshot e método.

`cobertura_mensal = dias com registro / dias do mês`. Manter o corte atual de >=0,80 para exibir o índice mensal. Abaixo do corte, célula/trecho fica indisponível com motivo; não interpolar nem unir lacunas como dados observados. Os cortes são regras analíticas de publicação, não limites de segurança.

Para 2026, distinguir cobertura do calendário anual e janela publicada até a data efetiva. Não exibir uma fração pequena do ano como pane de operação, nem tratar junho como fim de ano. Se mostrar ambas, nomear explicitamente os denominadores.

### 6.2 Estados de qualidade

| Estado | Regra/evidência | Consequência |
|---|---|---|
| Registro válido para descrição | Data/contagem/chave válidas após tratamento documentado | Pode entrar nas somas publicadas, mantendo limites de completude. |
| Chave ambígua | Sobreposição não resolvida na unidade de contagem | Quarentena e registro de impacto; não somar ambiguidades silenciosamente. |
| Publicação esparsa | Conjunto de bins/dias observado sem documentação que confirme zeros omitidos | Informar estrutura observada; não classificar automaticamente como erro, nem preencher ausências. |
| Inconsistência A/B | Falta de chave ou B>A no pareamento inspecionado | Manter bloqueio de B/A e mostrar evidência. Não atribuir automaticamente a falha a A. |
| Candidato a publicação parcial | Anomalia observável de volume/estrutura, causa ainda desconhecida | Exibir números, datas e referência descritiva; solicitar verificação, sem remoção automática. |
| Cadastro sem correspondência | Ausência de associação exata | Manter ponto da base A e indicação de referência indisponível. |

O painel de qualidade deve permitir consultar os menores volumes publicados por radar/data e sua razão para a mediana dos dias publicados do mesmo radar/ano. Isso é uma ordenação exploratória de publicação, não um limite automático de risco. Não instituir um corte arbitrário para eliminar dias.

O dia **29/08/2025** deve aparecer como caso documentado: 36 pontos, N=698; VC101-30, N=22, duas faixas publicadas, mediana anual=14.745,5. Texto: **“Volume publicado muito inferior à mediana dos dias deste radar. A causa não foi confirmada; confira a origem antes de interpretar como mudança no tráfego.”**

### 6.3 Sensibilidade

Expor a sensibilidade já reproduzida para cobertura de 80%, 90% e 95%: 27, 20 e 9 radares; índices agregados 2,539985, 2,519633 e 3,522462. Mostrar que muda a população. O resultado principal continua separado das alternativas.

Se investigar exclusão de um dia anômalo, manter grupo fixo, rotular o cenário, declarar a regra e mostrar delta de N/H/I. Não substituir o resultado principal sem justificativa e versionamento.

Não acrescentar intervalos de confiança que pressuponham independência/completude não demonstradas. Exibir denominadores, dias, população e sensibilidade é obrigatório; inferência estatística adicional exige protocolo próprio.

## 7. Regra de síntese para investigação

### 7.1 Grupo de referência

Usar os 20 pontos da coorte principal para definir quartis anuais. Não recalcular o quartil em um subconjunto local de um ou poucos pontos. A seleção pode restringir quais resultados são mostrados, mantendo o grupo de referência explicitado.

No snapshot auditado, os percentis 75 de referência são:

- 2024: 4,0728398313450045 por 10 mil.
- 2025: 3,6728028445734275 por 10 mil.

Regra de padrão repetido: equipamento elegível com `I2024 >= Q75_2024` e `I2025 >= Q75_2025`. Empates no quartil podem fazer o grupo conter mais de 25% dos radares; não forçar quantidade fixa. São limiares relativos, não limites legais/de segurança.

### 7.2 Estados da síntese

| Estado | Condição | Texto principal |
|---|---|---|
| Padrão repetido para investigação | Elegível e regra dos dois quartis satisfeita | “Índice entre os 25% maiores do grupo nos dois anos. Verifique este padrão.” |
| Regra não observada | Elegível e regra não satisfeita | “Este ponto não atende à regra de repetição do grupo. Isso não permite classificá-lo como seguro.” |
| Dados insuficientes para a regra | Fora da coorte, ano ausente, denominador indisponível ou violação de contrato | “Os dados disponíveis não sustentam esta comparação. Veja a cobertura e as restrições.” |

Um alerta de publicação pode acompanhar qualquer estado. Não ocultá-lo nem transformar todos os dados em inválidos sem evidência. Se uma ambiguidade comprometer o próprio cálculo, o resultado afetado fica indisponível; se for hipótese de completude, a descrição publicada pode continuar com a restrição explícita.

Criciúma/VC101-30 fica no estado de dados insuficientes para a regra principal de dois anos, com seus números descritivos disponíveis. Não reduzir automaticamente o limiar de cobertura para incluir o ponto.

### 7.3 Conteúdo mínimo por local

ID, município, km, sentido, período, H e N anuais, índice, dias e denominador de cobertura, referência usada, condição da regra, alertas de qualidade, contexto de acidentes disponível e limites. Próximo passo deve corresponder ao achado: conferir publicação; investigar estabilidade; verificar condições locais com profissional responsável. Não recomendar obra específica sem evidência de infraestrutura.

Acidentes não são usados para produzir score combinado de risco. A ficha pode mostrar que existe um padrão comportamental repetido e, ao lado, a quantidade de registros no segmento, sem dizer que a segurança foi demonstrada por haver poucos registros. Se não houver contagem espacial/temporal compatível, exibir “contexto não calculado para este recorte”.

## 8. Gráficos, mapas e tabelas

### 8.1 Ranking

Barras em escala linear, iniciando em zero, medida por 10 mil claramente visível. Rótulo com município/km e ID acessível. Se mostrar 12, escrever “12 maiores índices entre N equipamentos do filtro”. Um filtro com um radar não recebe rótulo “alto” por ocupar a largura do gráfico. Não usar vermelho/verde como classificação de segurança.

Título padrão recomendado: **“Laguna, km 304: maior índice do grupo em 2024–2025”**, acompanhado do valor e da unidade. Separar um eventual cartão de índice agregado e mostrar de onde vem seu denominador.

### 8.2 Histórico e persistência

Meses em ordem, anos completos/parciais identificados, sem interpolação. Tooltip/detalhe com H/N/dias/cobertura; alternativa tabular equivalente. Índice zero publicado e dado indisponível devem ser distinguíveis por texto/padrão, sem depender apenas de cor.

A dispersão anual deve ter os eixos com unidade e anos. Spearman fica no detalhe, com `n` e explicação: **“Mede a semelhança da ordenação dos equipamentos entre os anos; não mede chance de acidente nem mudança causal.”**

### 8.3 Localização geográfica

Mapa simples opcional à leitura, mas recomendado para a utilidade regional. Usar coordenadas publicadas, indicar fonte e referência e oferecer tabela equivalente. Não apresentar coordenadas ausentes ou fora de domínio como pontos válidos. Não alegar precisão/validação em campo que não ocorreu. Não usar mapa de calor temporal como substituto de mapa geográfico sem nomear a diferença.

### 8.4 Tabelas

Usar rótulos de apresentação compreensíveis, mantendo mapeamento para nomes internos no dicionário. Expor todas as medidas relevantes também em texto/tabela acessível. Ordenação não pode mudar a associação entre ID, valor e localização. Busca e seleção de colunas são controles locais de visualização; não alteram filtros científicos sem aviso explícito.

## 9. Contexto de acidentes

### 9.1 Segmentação e período

Manter segmentos disjuntos de 5 km, alinhados por `floor(km/5)*5`, com bordas limitadas ao corredor. Usar a referência quilométrica informada e registrar que sua equivalência histórica não foi comprovada por georreferenciamento em campo.

Para a comparação principal de 2024–2025, um segmento usa as datas em que todos os seus equipamentos selecionados publicaram. Os registros C são filtrados por essas mesmas datas e segmento. Uma ocorrência publicada não é replicada por cada radar. Mostrar quantidade de sensores, datas comuns e cobertura por segmento.

As datas comuns são internas a cada segmento; podem diferir entre segmentos. Uma comparação causal ou de taxas exigiria outra exposição e outro desenho.

### 9.2 Unidade, repetições e escopos

Nomear a medida **“Registros ANTT de acidentes no segmento”**. Preservar linhas repetidas e oferecer, em detalhe, contagem de combinações distintas de data/km como diagnóstico de sensibilidade; não chamar essa segunda quantidade de eventos únicos corrigidos.

Separar visualmente:

1. Segmentos com datas comuns usados na comparação principal.
2. Envelope de consulta entre pontos selecionados, com margem de 2,5 km, sem atribuição de acidente ao radar.
3. PRF, contexto independente do corredor integral e anos selecionados, enquanto esse for seu filtro implementado.

Um único segmento pode ter tabela e medidas descritivas, mas não coeficiente entre segmentos. Na consulta local fora da coorte, mostrar somente o contexto que possa ser calculado e sua restrição, sem forçar a análise principal.

### 9.3 Interpretação

Não usar “baixa concentração” sem definir a medida e referência. Preferir a contagem objetiva e o período. Sem veículo-quilômetro compatível, não gerar taxa de acidentes. Não somar ANTT e PRF. Não inferir proteção por correlação negativa nem segurança por poucos/nenhum registro.

O detalhe técnico informa, para o snapshot auditado, Spearman −0,584253 com 16 segmentos de 5 km e sensibilidade de 2/10 km. Não apresentar esse coeficiente como a principal conclusão preventiva.

## 10. Textos e estados de interface

| Situação | Texto recomendado |
|---|---|
| Apresentação | “Explore registros de velocidade da BR-101 Sul/SC e veja quais padrões merecem investigação preventiva.” |
| Explicação da unidade | “O índice compara contagens nas faixas acima de 120 km/h com todas as contagens publicadas no mesmo ponto e período.” |
| Grupo principal | “20 radares com registros em pelo menos 90% dos dias de 2024 e de 2025. Publicação não comprova operação contínua ou completude diária.” |
| Taxa B/A | “Percentual de possíveis infrações indisponível: as contagens das bases ainda não são compatíveis.” |
| Sem anos selecionados | “Selecione pelo menos um ano para consultar os registros.” |
| Sem sentido selecionado | “Selecione pelo menos um sentido da quilometragem.” |
| Sem equipamento local | “Selecione pelo menos um radar para comparar ou acompanhar o histórico.” |
| Nenhum dado para uma interseção válida | “Não há registros publicados para estes filtros. Isso não comprova ausência de tráfego ou de infrações.” |
| Sem cadastro associado | “Referência cadastral de 2026 não encontrada para este ponto. A localização exibida vem da base de tráfego.” |
| 2026 | “2026 parcial: tráfego até 30/06/2026 e possíveis infratores até 02/06/2026 neste snapshot. Comparações exigem períodos equivalentes.” |
| Mês com publicação insuficiente | “Índice não exibido: menos de 80% dos dias do mês têm registros publicados.” |
| Carregamento | “Carregando os dados do snapshot selecionado…” |
| Falha de dados | “Não foi possível carregar os dados desta versão. Tente novamente. Se o problema continuar, consulte o status da aplicação.” |
| Recurso oficial rejeita download | “Não foi possível confirmar um novo download da fonte. O painel usa o snapshot identificado abaixo.” |
| Demonstração futura | “DEMONSTRAÇÃO — dados simulados; estes valores não são medições oficiais.” |

Textos com datas e quantidades são gerados a partir da proveniência, não copiados como literais para snapshots futuros. Erro de contrato não pode manter indicadores da seleção anterior com aparência de atuais. Mensagem pública não orienta executar script interno inexistente nem mostra stack trace.

## 11. Exportações e rastreabilidade

### 11.1 Relatório Markdown

Incluir seleção solicitada e observada; ficha dos equipamentos; snapshot e método; fórmula; H/N/I; cobertura; regra de investigação e justificativa; qualidade; contexto compatível ou sua ausência; próximos passos; limites; quatro URLs oficiais e referências de método. O arquivo precisa ser compreensível fora do aplicativo.

Conteúdo gerado e exibido na tela é o mesmo conteúdo exportado. Comparações e fontes vêm das mesmas funções/catálogos, evitando divergências. Não inserir um parágrafo que sugira contexto de acidentes calculado quando apenas descreve o método geral.

### 11.2 CSV

Manter tabela regular, UTF-8 com acentos preservados e campos numéricos tipados. Separador e decimal devem ser explícitos no padrão adotado; não inserir parágrafos antes do cabeçalho. A seleção local/global deve estar refletida no arquivo.

Além dos valores, carregar identificação suficiente de período, snapshot e unidade, em colunas ou metadados associados. Nomes internos podem permanecer estáveis para interoperabilidade, com dicionário de apresentação. Nome do arquivo distingue recorte e período, sem caracteres problemáticos. Não arredondar os valores de cálculo à precisão visual.

## 12. Acessibilidade e responsividade

Meta: WCAG 2.2 AA, conforme [recomendação oficial](https://www.w3.org/TR/WCAG22/). Esta é meta futura, não declaração de conformidade atual.

- Idioma pt-BR, nomes acessíveis e estrutura de títulos coerente.
- Operação por teclado, foco perceptível, ordem lógica e saída de menus/expansões sem armadilha.
- Dados e descrições alternativas aos gráficos; não depender de hover, cor ou canvas para obter uma informação essencial.
- Contraste mínimo aplicável: 4,5:1 para texto comum, 3:1 para texto grande e elementos não textuais essenciais, respeitando as condições da norma.
- Verificação de refluxo a 320 CSS px, ampliação de texto e foco não encoberto; tabelas/gráficos com necessidade bidimensional devem ter alternativa adequada.
- Alvos de interação e espaçamento verificados conforme os critérios aplicáveis. Exceções não são presumidas.

Testar desktop e larguras de 320, 360/390, 768 e 1366 px em ambiente apropriado. Não usar uma captura recortada como teste de viewport. Sem rolagem horizontal desnecessária de toda a página; tabela pode ter área própria com orientação. Cabeçalho não encobre apresentação nem foco.

Realizar ao menos um percurso com leitor de tela e teclado e registrar navegador/tecnologia. O resultado da avaliação automática não substitui a verificação manual.

## 13. Separação entre dados reais e demonstração

O aplicativo auditado usa um snapshot real e não precisa introduzir simulações para parecer mais completo. Se houver modo demonstrativo futuro:

1. entrada deliberada em modo separado;
2. aviso persistente e em cada exportação;
3. namespace/arquivos de dados separados;
4. nenhuma mistura de valor simulado e indicador oficial;
5. sem barras de intensidade ou rótulos absolutos arbitrários;
6. datas e proveniência correspondentes ao modo.

Valores conceituais enviados em imagens anteriores não são dados de regressão nem referência factual.

## 14. Cenários de aceitação para implementação

Os cenários CT abaixo são **testes futuros**. Seu texto não significa que tenham sido executados nesta auditoria. Os testes efetivamente realizados são UI/DV no relatório.

| ID | Dado/quando | Resultado de aceitação |
|---|---|---|
| CT-01 | Coorte 2024/2025; comparar só VC101-4 e baixar CSV | Uma linha da seleção; gráfico não mostra 20 pontos; exportação não inclui outros IDs. |
| CT-02 | Histórico com apenas VC101-9 | Linha e mapa de calor têm o mesmo único ID e mesmo período; tabela alternativa confere. |
| CT-03 | Limpar equipamentos/anos/sentidos; mudar território eliminando IDs | Estado específico, sem dado antigo como atual; IDs válidos preservados; nenhum novo ID selecionado silenciosamente. |
| CT-04 | Abrir método e exportar relatório | Quatro URLs oficiais, fórmula, unidade, período, proveniência e versão disponíveis; arquivo autossuficiente. |
| CT-05 | Solicitar taxa B/A em qualquer filtro | Indisponível com explicação; nenhum percentual, inclusive após agregação por ID/data. |
| CT-06 | Aplicar regra de repetição ao snapshot | Exatamente os quatro IDs auditados, respeitando quartis e empates; limites recalculados dos dados, não hardcoded. |
| CT-07 | Consultar um ponto com/sem padrão repetido | Justificativas distintas, H/N/dias e referência; ausência da regra não vira segurança. |
| CT-08 | Consultar Criciúma e contexto com poucos/nenhum registro | Cobertura insuficiente da regra indicada; nenhuma classe de baixo risco ou previsão; contexto só se disponível. |
| CT-09 | Entrada com nova faixa, contagem negativa/fracionária ou chave ambígua | Erro/isolamento documentado; nada de coerção silenciosa ou conservação falsa dos totais. |
| CT-10 | Consultar meses com/sem cobertura e 2026 parcial | Lacunas e zero publicados diferentes; cobertura do ano e da janela nomeadas; sem comparação anual ingênua. |
| CT-11 | Abrir qualidade de 29/08/2025 | 698 contagens em 36 pontos e caso VC101-30 disponíveis; causa desconhecida; sem exclusão automática. |
| CT-12 | Agregar dois meses/radares com denominadores diferentes | Razão entre somas igual ao cálculo independente; não média simples de índices. |
| CT-13 | Denominador ausente/zero ou arquivo inválido em ambiente de teste | Indicador indisponível, sem NaN/inf como resultado legível e sem zero artificial; erro orientado. |
| CT-14 | Ler visão geral sem documentação prévia | Local, período, medida e motivo aparecem em linguagem simples; Spearman não é requisito para começar. |
| CT-15 | Percurso formativo com leigos/gestores | Registrar interpretação de por 10 mil, contagens × veículos únicos, falta de causalidade e próximo passo. Não afirmar sucesso antes de observar. |
| CT-16 | Percurso apenas por teclado e leitor de tela | Filtros, detalhes, dados e exportação acessíveis; idioma pt-BR; foco visível e saída dos controles. |
| CT-17 | Navegar sem perceber cores/hover | Dados e estados distintos por texto/tabela; nenhuma informação essencial apenas em cor. |
| CT-18 | Novo snapshot ou implantação | Versões e datas identificáveis; atualização de metadado não se transforma em coleta de bytes; HTML 200 rejeitado. |
| CT-19 | Selecionar ponto no mapa/tabela ou falhar fundo cartográfico | Mesma ficha e escopo; alternativa textual funcional; nenhum ponto inventado. |
| CT-20 | Visão geral Criciúma/2026 e grupo padrão | Textos refletem 1/181 e 20/731, respectivamente, com definição da união de datas; ranking indica corte em 12 quando aplicável. |
| CT-21 | Selecionar 2022/2023/2026 com grupo de referência 2024/2025 | Cobertura e elegibilidade do período atual explícitas; não presumir validade pela pertença ao grupo. |
| CT-22 | Contexto 5 km com vários equipamentos no segmento | Acidentes não multiplicados por sensor; apenas datas comuns daquele segmento; `n` e período disponíveis. |
| CT-23 | Contexto com 0/1 segmento, PRF e duplicatas C | Sem coeficiente inválido; registros preservados; sistemas não somados; escopos diferentes nomeados. |
| CT-24 | Alterar seleção e exportar CSV/MD; reabrir isoladamente | Valores, IDs, anos, fontes e restrições iguais à tela; acentos/decimais e leitura por máquina preservados. |
| CT-25 | Testar viewports e ampliações previstos | Nenhum texto/foco encoberto pelo cabeçalho; legibilidade; alternativa para conteúdo bidimensional; evidências reais por viewport. |
| CT-26 | Concluir regressão, toolbar e preparação da demonstração | Testes com resultados registrados, incluindo pendências desta auditoria; cinco telas e downloads verificados na versão implantada. |

## 15. Entrega e revisão

O Codex deve apresentar alterações, motivos, números reconciliados e testes concluídos. Itens inviáveis por falta de dado permanecem indisponíveis com explicação. Suspeitas só mudam de status quando houver evidência. As correções devem tornar o MVP mais verificável e compreensível, preservando seu objetivo preventivo e a capacidade real das fontes.
