# Auditoria das quatro bases ANTT

Versão 2.0, 26/10/2026. O ZIP recebido contém quatro CSV reais e manifesto bem-sucedido. Todos os hashes conferem. As respostas HTML de rejeição de 23/10 ficam preservadas no manifesto antigo como histórico, sem uso analítico.

| Fonte | Linhas | Intervalo observado | Unidade |
|---|---:|---|---|
| A: volume-radar-viacosteira | 329.410 | 01/01/2022–30/06/2026 | Contagem por dia, equipamento e faixas |
| B: quantidade-possiveis-infratores-viacosteira | 155.929 | 30/12/2022–02/06/2026 | Contagem publicada de possíveis infratores |
| C: demostrativo_acidentes_viacosteira | 8.841 | 01/05/2021–31/12/2025 | Registro de data/km, sem ID |
| D: dados-dos-radares6_2026 | 1.256 | Referência de junho/2026 | Cadastro nacional, 41 linhas ViaCosteira |

A, B e D usam Latin-1 e separador ponto e vírgula. C é decodificável em UTF-8. O perfil completo, incluindo ausências, cardinalidade e valores, está em `relatorios/auditoria_antt.json`.

## Decisões executadas

A velocidade é um intervalo textual, embora os exemplos dos dicionários de A/B sejam numéricos. Não converter rótulos em velocidade média. As faixas exclusivas de A permitem um índice condicional à publicação. A classe veicular está ausente em 251.438 linhas de A; nas demais é não classificada.

Na chave equipamento/dia/sentido/faixa física/faixa de velocidade, 384 linhas A diferem na categoria veicular. Os 41 equipamentos-dia envolvidos, todos em 30/04/2023, foram integralmente isolados: 420 linhas e 526.390 contagens. O recorte principal 2024–2025 não muda.

Os 42 equipamentos de A/B coincidem em localização e sentido, mas a codificação de faixas físicas diverge. A usa 1 em Crescente e 2 em Decrescente; B usa 1 e 2 nos dois sentidos e também 3 no Decrescente. Entre 71.705 unidades B agregadas pela chave estrita, 35.196 encontram denominador e 36.509 não. Em seis das correspondências, B supera A. **A taxa B/A permanece bloqueada.** Remover a faixa da chave esconderia a incompatibilidade.

D não possui ID VC101. A junção exata por rodovia/UF/km/sentido é 1:1 e conserva contagens: 41 correspondências em 42 pontos; VC101-20, km 252, Crescente, permanece sem cadastro. Nenhum vizinho foi usado. Os limites são referência de 2026, sem validade histórica presumida. Ano PNV/SNV é referência cartográfica, não data de instalação.

C tem 187 repetições integrais além da primeira e não permite identificar eventos únicos. Todas foram mantidas. A análise de sensibilidade usa combinações de data/km, sem chamá-las de total corrigido de acidentes. Em 2024–2025 são 3.499 registros ANTT, separados dos 1.750 PRF.

## Uso viável

Índice da própria A: faixas acima de 120 km/h por 10 mil contagens publicadas, no mesmo ponto e período. Coorte de 20 IDs com ao menos 90% dos dias publicados em cada ano de 2024–2025; meses com menos de 80% ficam ausentes. Esse corte é uma escolha analítica com sensibilidade de 80/90/95%, sem atestar uptime.

Contexto espacial: segmentos disjuntos de 5 km, somente nos dias de publicação comum a todos os equipamentos de cada segmento. A contagem de C usa exatamente essas datas. Junções many:1 impedem multiplicação de acidentes. Associação descritiva sem inferência causal, risco por viagem ou efeito de intervenção.

Para liberar B/A, é necessário esclarecer faixas e classes com o publicador, obter denominadores semanticamente equivalentes e refazer os testes. Para estudar velocidade regulamentada, é necessário histórico dos limites e observações compatíveis por categoria de veículo. Esses esclarecimentos não foram obtidos nem simulados.
