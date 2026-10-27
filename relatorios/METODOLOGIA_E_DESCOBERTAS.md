# Metodologia e três descobertas verificáveis

Estudo quantitativo, observacional, exploratório e descritivo de registros administrativos. Principal: ViaCosteira BR-101/SC, 2024–2025. Coleta: 26/10/2026. Não há amostra probabilística, teste de intervenção ou previsão validada.

## Indicador e seleção

10.000 × contagens A das faixas 121–140, 141–160 e >160 / contagens A de todas as faixas publicadas, para o mesmo ponto e período. O limiar é analítico, sem reconstrução legal. A taxa possíveis infratores/passagens não foi validada e permanece bloqueada. A classe veicular de A é frequentemente ausente; códigos de faixa de A/B divergem.

Dos 42 pontos, a coorte fixa contém 20 com publicação em pelo menos 90% dos dias de cada ano. Ela reúne 57.163 contagens acima de 120 em 226.870.300 publicadas, índice agregado 2,519633 por 10 mil. O agregado pondera por contagens, e não pela média simples dos índices. Mediana e quartis entre pontos estão no notebook. Cobertura de publicação não é uptime nem completude.

## D1 — heterogeneidade

Índice mínimo 0,739012 e máximo 6,343146 por 10 mil. O maior valor é VC101-9, Laguna, km 304, Decrescente: 7.091 / 11.178.995 × 10.000. O menor é VC101-19: 632 / 8.551.963 × 10.000. Esse ranking descreve contagens publicadas em pontos selecionados, sem classificar probabilidade de acidente ou desempenho da fiscalização.

## D2 — persistência

Spearman dos índices de 2024 e 2025 nos mesmos 20 pontos = 0,962406. Limiares do quartil superior: 4,072840 em 2024 e 3,672803 em 2025. VC101-39, VC101-4, VC101-7 e VC101-9 estão acima de ambos. Dois anos, dependência espacial e seleção de cobertura limitam a inferência. Não houve validação preditiva ou p-valor para tratar esses registros como amostra aleatória independente.

## D3 — contexto de acidentes

Agrupamos a coorte em 16 segmentos disjuntos de 5 km, com bordas cortadas ao corredor. Cada segmento usa somente as datas em que todos os seus equipamentos publicaram. Registros C usam essas mesmas datas e segmento, com junção many:1 para não multiplicar acidentes por radar. Spearman entre índice e contagem de registros = −0,584253.

O sinal não demonstra efeito protetor da velocidade. Fluxo, geometria, localização de radares, publicação e seleção são possíveis fatores não isolados. Sem denominador veículo-quilômetro, gravidade em C ou histórico de intervenção, não estimamos risco causal nem eficácia preventiva.

## Sensibilidade e limites locais

Em 2, 5 e 10 km, Spearman é −0,455417, −0,584253 e −0,446154 (16, 16 e 14 segmentos). Usar combinações distintas de data/km muda os resultados para −0,440679, −0,584253 e −0,437844. Isso não corrige o número de eventos, pois C não tem ID.

Cobertura de 80%, 90% e 95% gera 27, 20 e 9 pontos e índices agregados de 2,539985, 2,519633 e 3,522462. A escolha muda a população observada. Os índices mensais abaixo de 80% de dias publicados ficam ausentes, sem interpolação.

VC101-30, Criciúma, publica em 306/366 dias em 2024 e 332/365 em 2025. Índices 2,855519 e 2,220827 por 10 mil. São 1.299/4.549.086 e 1.113/5.011.647 contagens. O ponto fica fora da coorte principal, mas continua disponível em consulta local. A diferença entre anos não demonstra melhora de segurança.

Fontes, hashes, transformações, tabelas e saídas acompanham o notebook. `descobertas_antt.json` e `resumo_antt.json` são os resultados principais; `descobertas.json` e `resumo.json` são o contexto PRF independente.
