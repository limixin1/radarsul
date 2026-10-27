# Fontes e validações do SENTINELA

**Data de consulta:** 27/10/2026, referência America/Sao_Paulo.  
**Aplicação:** https://radarsul.site/.  
**Código inspecionado:** https://github.com/limixin1/radarsul/tree/e5baed4fdab7575690a408f4ab492fd63790a00e.  
**Escopo principal:** registros administrativos da ViaCosteira, BR-101/SC, análise de 2024–2025 e consulta exploratória de outros períodos publicados.

Este documento registra o que foi examinado. Não declara uma nova coleta oficial dos quatro CSVs nem homologação científica dos indicadores. As recomendações estão na especificação e no backlog; a auditoria não modificou o produto.

## 1. Como interpretar a evidência

| Marca | Alcance |
|---|---|
| F — arquivo inspecionado | Conteúdo da cópia disponibilizada no projeto, com tamanho e SHA-256 conferidos. |
| M — metadado oficial | Informação recuperada da página/recurso oficial. Não substitui inspeção dos bytes atuais. |
| I — inferência | Interpretação ou hipótese explicitamente indicada; não é observação confirmada. |
| NV — não verificado | Não foi possível obter evidência suficiente. |

UI e código são outras categorias de origem das evidências, identificadas pelos testes UI e pelos links do commit. Os números F vieram de uma reprodução independente que não importou as funções analíticas do aplicativo.

### Origem das cópias examinadas

Os quatro arquivos foram obtidos do `SENTINELA_bases_ANTT.zip` já fornecido ao projeto. O ZIP tem SHA-256 `2fb175fbed8f7bee826d7cbb3fb8912d39dd36fb5f1c9a54c3a6ba507fa2b617`. Seu manifesto declara coleta em 26/10/2026; horários do manifesto são UTC. Os quatro hashes dos CSVs coincidem com os declarados na documentação do repositório.

Isso confirma identidade entre as cópias examinadas e o snapshot documentado. Não é uma assinatura da ANTT nem prova independente da hora em que a coleta original foi feita.

## 2. Disponibilidade dos recursos oficiais nesta consulta

As páginas dos quatro recursos foram recuperadas por pesquisa/leitura web. As tentativas HTTP diretas dos quatro CSVs retornaram status **200**, `Content-Type: text/html; charset=utf-8`, tamanho **246 bytes**, com título **Request Rejected**. Não foram aceitas como dados. A API CKAN consultada também retornou página de rejeição, e não JSON utilizável.

O bloqueio de acesso desta sessão não significa que a ANTT deixou de publicar os dados ou que o usuário não consegue baixá-los. Os links e metadados existem; a obtenção atual dos bytes pelo ambiente da auditoria não foi concluída. As respostas estão resumidas em `evidencias/fontes/tentativas_oficiais.json`.

Não foram usadas tentativas de contornar o bloqueio, rotacionar rede ou assumir status 200 como sucesso. O trabalho prosseguiu com as cópias do projeto e registrou essa limitação.

## 3. Inventário das quatro fontes previstas

| Base | Recurso oficial | Atualização do recurso na página (M) | Cobertura no arquivo (F) |
|---|---|---|---|
| A | [Tráfego nos radares da ViaCosteira](https://dados.antt.gov.br/dataset/volume-radar/resource/2af017dc-edde-4501-9c10-ae1f0da461f6) | 28/07/2026 | 01/01/2022 a 30/06/2026 |
| B | [Possíveis infratores da ViaCosteira](https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores/resource/121be806-df31-4ebb-aa2d-8caa5f102226) | 28/07/2026 | 30/12/2022 a 02/06/2026 |
| C | [Acidentes por quilômetro da ViaCosteira](https://dados.antt.gov.br/dataset/acidentes-quilometro-rodovias/resource/05e0cbd2-2acb-4b81-8124-3c28a3030234) | 28/01/2026 | 01/05/2021 a 31/12/2025 |
| D | [Cadastro dos radares — referência junho/2026](https://dados.antt.gov.br/pt_BR/dataset/radar/resource/64044fcf-756e-4fd1-9cb2-a6037785829d) | 28/07/2026 | Snapshot cadastral; não há série histórica de limites neste arquivo |

**Três datas diferentes:** atualização do recurso no portal; datas dos registros dentro do arquivo; coleta/consulta do projeto. A data de 28/07/2026 não significa que os registros se estendam até julho. A data de atualização de um dicionário também não atualiza automaticamente o CSV correspondente.

Os metadados recuperados podem refletir a versão indexada pela ferramenta de pesquisa. Sem novo download válido, não foi possível excluir uma alteração posterior dos bytes oficiais.

### A — Tráfego nos radares da ViaCosteira

- Página oficial: [Tráfego nos radares da ViaCosteira](https://dados.antt.gov.br/dataset/volume-radar/resource/2af017dc-edde-4501-9c10-ae1f0da461f6).
- CSV oficial: [volume-radar-viacosteira.csv](https://dados.antt.gov.br/dataset/269aebaa-05e7-4d76-a105-408f12bf4094/resource/2af017dc-edde-4501-9c10-ae1f0da461f6/download/volume-radar-viacosteira.csv).
- Consulta: 27/10/2026. Novo download oficial: rejeitado nesta sessão. Cópia do projeto: inspecionada.
- Arquivo local: **329.410 linhas**, **47.784.599 bytes**, codificação detectada **latin1**.
- SHA-256 conferido: `d2a0b20ba6fa0fc2dcd69a11cd87e2248982327e908e4161a3d617271372c0f0`.
- Cobertura: 01/01/2022 a 30/06/2026.

**Unidade observada (F):** contagem `volume_total` por equipamento/data/sentido/código de faixa/intervalo de velocidade/campo de categoria, não uma linha por veículo individual. São 42 IDs em 15 municípios, km 252,0 a 445,6, BR-101/SC. As oito faixas textuais são `<=20`, `21–50`, `51–80`, `81–100`, `101–120`, `121–140`, `141–160`, `>160`, preservando-se no processamento os rótulos originais e espaços de origem.

**Qualidade (F):** 329.410 linhas; 251.438 sem categoria e 77.972 com “Não classificado”; nenhuma categoria veicular útil. Não foram encontradas contagens negativas/fracionárias, datas inválidas ou duplicatas integrais no arquivo completo. A ausência de linha de uma faixa não demonstra zero real. O código de faixa 1 ocorre só em Crescente e 2 só em Decrescente.

**Tratamento reproduzido (F):** 41 equipamentos-dia de 30/04/2023 entram em quarentena por sobreposição ambígua de chave: 420 linhas, 526.390 contagens. Não houve edição dos originais. Cobertura de dias e contagens foram recalculadas após esse tratamento.

**Limites:** não há velocidades individuais, horário de passagem, veículos únicos, declaração de completude horária ou histórico de limites. O índice acima de 120 é descrição de contagens publicadas e não frequência legal de infração.

### B — Possíveis infratores da ViaCosteira

- Página oficial: [Possíveis infratores da ViaCosteira](https://dados.antt.gov.br/dataset/quantidade-possiveis-infratores/resource/121be806-df31-4ebb-aa2d-8caa5f102226).
- CSV oficial: [quantidade-possiveis-infratores-viacosteira.csv](https://dados.antt.gov.br/dataset/c3844135-55c4-43b3-88a0-247f6ff9ca67/resource/121be806-df31-4ebb-aa2d-8caa5f102226/download/quantidade-possiveis-infratores-viacosteira.csv).
- Consulta: 27/10/2026. Novo download oficial: rejeitado nesta sessão. Cópia do projeto: inspecionada.
- Arquivo local: **155.929 linhas**, **24.500.215 bytes**, codificação detectada **latin1**.
- SHA-256 conferido: `3dd3b9bb37834e80fc4d94de22170aa85d7013224a5b8f56397967ede8c4aa93`.
- Cobertura: 30/12/2022 a 02/06/2026.

**Unidade observada (F):** contagem publicada nas dimensões próprias de B, com os mesmos 42 IDs, municípios e faixa quilométrica geral de A. Há cinco intervalos de velocidade a partir de 81–100. A categoria é “Não Classificado” em todas as 155.929 linhas. Não são 155.929 pessoas ou autuações.

**Qualidade (F):** sem nulos nas colunas examinadas, duplicatas integrais, contagens negativas/fracionárias ou datas inválidas. Há 1.256.255 contagens no período total. Em 2022 só há linhas em dois dias; isso não comprova que os demais dias tiveram zero possíveis infrações.

**Faixas (F):** códigos 1 e 2 nos dois sentidos, além de código 3 em parte do sentido Decrescente. A equivalência física com as faixas de A não foi demonstrada. IDs e localização compatíveis, isoladamente, não validam B/A.

**Limites:** critérios de publicação, zeros omitidos, universo efetivo e correspondência dimensional permanecem insuficientemente documentados para a divisão por A. As contagens podem ser apresentadas separadamente, com esse aviso.

### C — Acidentes por quilômetro da ViaCosteira

- Página oficial: [Acidentes por quilômetro da ViaCosteira](https://dados.antt.gov.br/dataset/acidentes-quilometro-rodovias/resource/05e0cbd2-2acb-4b81-8124-3c28a3030234).
- CSV oficial: [demostrativo_acidentes_viacosteira.csv](https://dados.antt.gov.br/dataset/8a57b663-2302-405a-bf5a-cbece12c13d1/resource/05e0cbd2-2acb-4b81-8124-3c28a3030234/download/demostrativo_acidentes_viacosteira.csv).
- Consulta: 27/10/2026. Novo download oficial: rejeitado nesta sessão. Cópia do projeto: inspecionada.
- Arquivo local: **8.841 linhas**, **433.240 bytes**, codificação detectada **utf-8-sig**.
- SHA-256 conferido: `a798c5ca821f8f6905102c60c5c9300da454729b6f5ef06d5cd429d684b3e00e`.
- Cobertura: 01/05/2021 a 31/12/2025.

**Unidade observada (F):** linha administrativa com concessionária, data, km e trecho. A fonte tem 8.841 linhas, km 244,6 a 465,0; 3.499 linhas em 2024–2025. Todo o arquivo é da ViaCosteira, trecho BR-101/SC.

**Qualidade (F):** quatro colunas sem nulos; 187 repetições integrais além da primeira. Não há ID único de ocorrência para decidir se são duplicidades de cadastro ou eventos distintos no mesmo local/data. Preservar registros e oferecer sensibilidade por combinações distintas, sem chamá-las de eventos únicos corrigidos.

**Limites:** não há município, coordenadas, sentido, faixa, gravidade, horário ou exposição neste CSV. Relação com radares só pode ser contextual por quilometragem e data; não atribuir acidentes ao equipamento nem calcular taxa ajustada dividindo por passagens somadas de radares.

### D — Cadastro dos radares — referência junho/2026

- Página oficial: [Cadastro dos radares — referência junho/2026](https://dados.antt.gov.br/pt_BR/dataset/radar/resource/64044fcf-756e-4fd1-9cb2-a6037785829d).
- CSV oficial: [dados-dos-radares6_2026.csv](https://dados.antt.gov.br/dataset/79d287f4-f5ca-4385-a17c-f61f53831f17/resource/64044fcf-756e-4fd1-9cb2-a6037785829d/download/dados-dos-radares6_2026.csv).
- Consulta: 27/10/2026. Novo download oficial: rejeitado nesta sessão. Cópia do projeto: inspecionada.
- Arquivo local: **1.256 linhas**, **147.125 bytes**, codificação detectada **latin1**.
- SHA-256 conferido: `a5d2b6facc9eed86a88c94bfa7870a31576db2b832daf0f664802497e60cf17d`.
- Cobertura: Snapshot cadastral; não há série histórica de limites neste arquivo.

**Unidade observada (F):** registro cadastral de equipamento, sem ID equivalente ao identificador VC101 de A/B. O arquivo nacional tem 1.256 linhas e oito duplicatas integrais. O recorte VIA COSTEIRA tem 41 linhas, chaves espaciais únicas, BR-101/SC, pista Principal, tipo Controlador e situação Ativo.

**Associação (F):** por concessionária/rodovia/UF/km/sentido, 41 dos 42 pontos de A têm correspondência; VC101-20, km 252,0, Crescente, não tem referência nesse cadastro. Não usar aproximação por vizinho para completar o limite ausente.

**Referência (F):** nome do arquivo indica junho/2026; `ano_do_pnv_snv` é 2020 para o recorte ViaCosteira, e não data de instalação. Em 38 linhas o limite de referência é 110 para leves e 90 para pesados; em três, 80 para ambos. O cadastro não comprova os limites de 2024–2025 nem classifica as passagens de A por veículo.

**Limites:** ausência de data da inativação em todas as 1.256 linhas do arquivo nacional não reconstrói a disponibilidade histórica. Situação Ativo no snapshot não é uptime nem completude dos dados de tráfego.

## 4. Esquemas examinados e variáveis utilizáveis

### A e B — mesmas colunas, sem equivalência automática de significado operacional

| Campo | Tipo efetivo | Uso | Restrição |
|---|---|---|---|
| concessionaria | Texto | Publicador/concessionária | VIA COSTEIRA; não representa unidade individual de passagem |
| identificador | Texto | Identificador do equipamento | VC101-*; 42 em cada arquivo |
| rodovia / uf | Texto | Rodovia e estado | BR-101 / SC |
| km_m | Número decimal | Referência quilométrica | Usar junto de rodovia/UF e versão da referência |
| municipio | Texto | Município informado | 15 nomes, conforme tabela abaixo |
| tipo_de_pista | Texto | Pista | Principal no recorte examinado |
| latitude / longitude | Números decimais | Localização publicada | Origem administrativa; não conferida em campo |
| data_da_passagem | Data dd/mm/aaaa | Data do registro agregado | Sem horário ou veículo individual |
| sentido_da_passagem | Texto | Crescente/Decrescente | Direção na referência quilométrica |
| faixa_da_passagem | Código numérico | Faixa conforme publicação | A/B apresentam distribuições incompatíveis para pareamento físico presumido |
| velocidade | Intervalo textual | Faixa de velocidade | Não é velocidade exata; não usar média de pontos médios |
| tipo_de_veiculo | Texto ou ausente | Categoria declarada | Não fornece categorias úteis neste snapshot |
| volume_total | Inteiro não negativo | Contagem agregada | Não é número de pessoas/veículos únicos |

### C — acidentes

`Concessionaria`, `Data`, `Km`, `Trecho`. Conversão de data explícita e quilômetro decimal com vírgula. A unidade de análise segura é linha publicada, preservando identificador de linha na cópia tratada. Nenhum campo identifica unicamente o evento.

### D — cadastro

`concessionaria`, `ano_do_pnv_snv`, `tipo_de_radar`, `rodovia`, `uf`, `km_m`, `Municipio`, `tipo_de_pista`, `sentido`, `situacao`, `data_da_inativacao`, `latitude`, `longitude`, `velocidade_leve`, `velocidade_pesado`.

O esquema permite consultar referência cadastral e limites daquele snapshot. Não resolve classe de veículo, critérios de possíveis infratores ou operação histórica.

## 5. Equipamentos e municípios realmente encontrados

Os 42 IDs pertencem a 15 municípios: Araranguá, Capivari de Baixo, Criciúma, Garopaba, Imbituba, Içara, Jaguaruna, Laguna, Maracajá, Paulo Lopes, Pescaria Brava, Sangão, Santa Rosa do Sul, Sombrio, Tubarão. A tabela usa o cadastro de localização da própria base de tráfego; “coorte” indica apenas a regra de dias publicados em 2024 e 2025.

| ID | Município | Km publicado | Sentido | Coorte 2024–2025 |
|---|---|---|---|---|
| VC101-1 | Paulo Lopes | 259.7 | Crescente | Não |
| VC101-10 | Imbituba | 289.5 | Decrescente | Sim |
| VC101-11 | Tubarão | 334.7 | Crescente | Sim |
| VC101-12 | Tubarão | 334.9 | Decrescente | Sim |
| VC101-13 | Capivari de Baixo | 325.4 | Decrescente | Sim |
| VC101-14 | Capivari de Baixo | 324.9 | Decrescente | Sim |
| VC101-15 | Pescaria Brava | 318.4 | Decrescente | Sim |
| VC101-16 | Sangão | 360.6 | Crescente | Não |
| VC101-17 | Sangão | 367.5 | Decrescente | Não |
| VC101-18 | Sangão | 363.4 | Crescente | Não |
| VC101-19 | Sangão | 361.9 | Decrescente | Sim |
| VC101-2 | Garopaba | 264.6 | Decrescente | Não |
| VC101-20 | Paulo Lopes | 252.0 | Crescente | Não |
| VC101-21 | Imbituba | 269.032 | Decrescente | Sim |
| VC101-22 | Pescaria Brava | 324.0 | Crescente | Sim |
| VC101-23 | Tubarão | 336.8 | Decrescente | Não |
| VC101-24 | Jaguaruna | 347.28 | Crescente | Sim |
| VC101-25 | Jaguaruna | 347.84 | Decrescente | Sim |
| VC101-26 | Sangão | 355.3 | Crescente | Sim |
| VC101-27 | Içara | 371.9 | Decrescente | Não |
| VC101-28 | Içara | 373.0 | Crescente | Não |
| VC101-29 | Içara | 387.7 | Decrescente | Não |
| VC101-3 | Paulo Lopes | 255.6 | Decrescente | Não |
| VC101-30 | Criciúma | 391.94 | Crescente | Não |
| VC101-31 | Maracajá | 400.7 | Crescente | Sim |
| VC101-32 | Araranguá | 407.5 | Decrescente | Sim |
| VC101-33 | Araranguá | 410.8 | Crescente | Não |
| VC101-34 | Araranguá | 411.0 | Decrescente | Não |
| VC101-35 | Araranguá | 412.2 | Crescente | Não |
| VC101-36 | Araranguá | 412.2 | Decrescente | Não |
| VC101-37 | Araranguá | 416.0 | Crescente | Não |
| VC101-38 | Araranguá | 416.0 | Decrescente | Sim |
| VC101-39 | Sombrio | 432.5 | Crescente | Sim |
| VC101-4 | Paulo Lopes | 252.4 | Decrescente | Sim |
| VC101-40 | Sombrio | 432.5 | Decrescente | Não |
| VC101-41 | Santa Rosa do Sul | 445.6 | Crescente | Não |
| VC101-42 | Santa Rosa do Sul | 445.6 | Decrescente | Sim |
| VC101-5 | Imbituba | 275.9 | Crescente | Não |
| VC101-6 | Imbituba | 277.3 | Crescente | Não |
| VC101-7 | Imbituba | 287.1 | Crescente | Sim |
| VC101-8 | Imbituba | 277.3 | Decrescente | Não |
| VC101-9 | Laguna | 304.0 | Decrescente | Sim |

Não há dados para toda a malha urbana desses municípios. Um ID localizado em Criciúma não representa todas as vias da cidade. O cadastro nacional D cobre outras concessões e estados, mas esses registros não fazem parte da análise regional principal.

## 6. Cobertura temporal e quantidade publicada por ano

Estas tabelas descrevem os CSVs brutos completos, **antes da quarentena de A de 30/04/2023**. “Dias” é a união de datas com alguma linha na base; não é cobertura de cada radar. H é contagem nas faixas acima de 120 da respectiva base; H de B não é usado no indicador principal.

### Base A

| Ano | Linhas | Datas distintas | IDs | Contagens | H da base |
|---|---|---|---|---|---|
| 2022 | 57233 | 365 | 42 | 127491137 | 610 |
| 2023 | 74083 | 365 | 42 | 176158580 | 23154 |
| 2024 | 79618 | 366 | 42 | 206136150 | 57004 |
| 2025 | 77425 | 365 | 42 | 204677385 | 54976 |
| 2026 | 41051 | 181 | 42 | 110935217 | 33259 |

### Base B

| Ano | Linhas | Datas distintas | IDs | Contagens | H da base |
|---|---|---|---|---|---|
| 2022 | 78 | 2 | 9 | 3120 | 114 |
| 2023 | 45712 | 365 | 42 | 691918 | 33122 |
| 2024 | 45879 | 319 | 42 | 236515 | 20615 |
| 2025 | 44542 | 358 | 42 | 220191 | 17799 |
| 2026 | 19718 | 148 | 42 | 104511 | 8455 |

A data máxima de B é 02/06/2026, embora A vá até 30/06. Meses/anos sem linhas de B não foram tratados como zero real. A cobertura anual de cada equipamento e a coorte foram calculadas nos arquivos tratados de auditoria.

## 7. Compatibilidade entre bases e verificação dos indicadores

| Relação | Verificação concluída | Conclusão |
|---|---|---|
| A-alta / A-total | Mesmo arquivo, ID e período; razão entre somas; quarentena reproduzida; máximos e agregado conferidos | Válido como descrição de contagens publicadas, com completude desconhecida. |
| B/A por ID/data/sentido/faixa | 71.705 chaves B; 36.509 sem A; 35.196 com A; seis B>A | Não validado. |
| B/A agregando faixas por ID/data | 37.835 chaves B; 40 sem A; 17 B>A | Agregação não resolve incompatibilidade. |
| A/D | Mesmo km/sentido no recorte de concessão/rodovia/UF; 41 correspondências, uma ausente | Referência cadastral parcial, sem histórico de limites. |
| A/C | Segmentação quilométrica e datas comuns dentro de cada segmento | Contexto espacial/temporal, sem causalidade, taxa de exposição ou vínculo individual radar–evento. |
| ANTT/PRF | Bases distintas, definições e recortes diferentes | Não somar nem supor deduplicação cruzada. |

### Indicador principal reproduzido

`10.000 × soma(A nas faixas 121–140, 141–160 e >160) / soma(A em todas as faixas publicadas)`.

Na coorte de 20 pontos em 2024–2025: H=57.163; N=226.870.300; índice=2,519633464583068. VC101-9 tem máximo=6,343146230944732, obtido de H=7.091 e N=11.178.995. O CSV baixado do produto com VC101-9, VC101-39 e VC101-4 confere com o recálculo, até precisão de 1e-12 para os índices.

Essa validação não transforma o índice em frequência legal de infrações, probabilidade de acidente ou medida real completa do tráfego. O limiar de 120 é analítico e as passagens não identificam veículos únicos.

### Persistência e acidentes

Spearman anual entre os mesmos 20 pontos: 0,9624060150375939. Quartis superiores: 4,0728398313450045 em 2024 e 3,6728028445734275 em 2025. Pontos acima de ambos: VC101-39, VC101-4, VC101-7, VC101-9. São classificações relativas, sem limite absoluto de segurança.

Contexto: segmentos de 2/5/10 km produzem, respectivamente, 16/16/14 segmentos e Spearman −0,45541747253447173 / −0,5842532854724708 / −0,4461538461538462. Em 5 km, datas comuns variam de 636 a 731 entre segmentos. Coeficientes não são teste de efeito protetor ou preditivo.

### Qualidade e sensibilidade

O corte de 80/90/95% dos dias anuais em ambos os anos gera 27/20/9 equipamentos e índice agregado 2,53998500357088 / 2,519633464583068 / 3,522461911201089. Isso muda a população observada.

Em 29/08/2025, 36 radares publicam 698 contagens. VC101-30 tem 22 em duas faixas, contra mediana diária de 14.745,5 em seus dias publicados de 2025. **I:** pode haver publicação parcial, alteração operacional ou outra explicação; a causa permanece desconhecida. O dia não foi removido dos resultados principais desta auditoria.

## 8. Dicionários oficiais e seu grau de verificação

| Base | URL oficial do dicionário | Resultado nesta consulta |
|---|---|---|
| A | [Volume de tráfego](https://dados.antt.gov.br/dataset/269aebaa-05e7-4d76-a105-408f12bf4094/resource/7d32f5d1-7a5d-403b-8db5-09e7e11addf1/download/dicionario_de_dados_volume_radar.pdf) | Texto de duas páginas recuperado. Define campos e apresenta exemplo numérico de velocidade; o CSV real usa intervalos. O exemplo não substitui o conteúdo observado. |
| B | [Possíveis infratores](https://dados.antt.gov.br/dataset/c3844135-55c4-43b3-88a0-247f6ff9ca67/resource/d69fc6e3-c693-47b2-b1cc-aa0c05e734a9/download/dicionario_dados_surod_quantidade_possiveis_infratores.pdf) | Página do recurso localizada; PDF não recuperado integralmente. Esquema da página e CSV examinados; critério operacional completo não confirmado. |
| C | [Acidentes por km](https://dados.antt.gov.br/dataset/8a57b663-2302-405a-bf5a-cbece12c13d1/resource/3d9e26ca-5d8f-4854-9744-836e8bcb088e/download/dicionario_dados_surod_acidentes_km.pdf) | Tentativa de PDF com timeout; página do dicionário localizada. Metadados do dicionário indicam atualização própria, que não deve ser atribuída ao CSV de acidentes. |
| D | [Cadastro, referência citada no projeto](https://dados.antt.gov.br/dataset/79d287f4-f5ca-4385-a17c-f61f53831f17/resource/b10de933-f8fa-4f13-8a40-a87759b0b4c9/download/radar_dicionario_dados.pdf) | Página localizada; PDF não lido integralmente. Metadados recuperados apresentam formato PDF e MIME application/json, inconsistência que exige conferir bytes antes de aceitar arquivo. |

Foi localizado também um recurso de dicionário D de agosto/2026, distinto do recurso citado no pacote: [página oficial](https://dados.antt.gov.br/dataset/radar/resource/2fbc0b5a-59e1-4166-9d4a-e2a9b92b227b). Apenas metadados foram consultados; não se assume que represente a mesma referência cadastral de junho. Essa diferença reforça a necessidade de versionar dicionários junto dos dados.

Não foi afirmado que os quatro PDFs foram baixados ou lidos integralmente. A documentação anterior do projeto afirma consultas anteriores; isso não foi usado como substituto de verificação independente nesta sessão.

## 9. PRF — fonte adicional efetivamente usada pelo produto

Página oficial: [Dados abertos da PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf). A página separa arquivos por ocorrência, por pessoa e por múltiplas causas; esses grãos não podem ser somados indiscriminadamente. Sua modificação indicada na consulta é 28/07/2026. A análise abaixo usou os ZIPs por ocorrência fornecidos no projeto, sem alegar novo download oficial nesta sessão.

| Ano | URL registrada no manifesto | SHA-256 do ZIP conferido | Recorte BR-101/SC, km 244,680–465,100 | Criciúma |
|---|---|---|---:|---:|
| 2024 | https://drive.google.com/uc?export=download&id=14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO | 905dac836867297b261e4edefff6cdb470809814e7e1796b3f2f57517099d165 | 921 | 24 |
| 2025 | https://drive.google.com/uc?export=download&id=1-G3MdmHBt6CprDwcW99xxC4BZ2DU5ryR | 52c8a631ac9d428bf845e2fa996b8c61f66b219f7014a61d292f9d95d186bb0f | 829 | 12 |

A soma conferida é 1.750 ocorrências e 36 em Criciúma, igual à tela. O filtro independente usou UF=SC, BR=101, quilometragem convertida com decimal e intervalo inclusivo 244,680–465,100. Não houve ID duplicado em cada recorte anual. As cópias nacionais têm 73.202 e 72.529 linhas, respectivamente. O manifesto declara coleta em 23/10/2026.

Esses números não são denominador de tráfego, nem substituem a base ANTT C. A auditoria não refez todas as verificações das variáveis de vítimas da PRF, pois a tela examinada usa apenas o contexto de ocorrências e município. Não assumir que toda qualidade do Parquet PRF foi certificada.

## 10. Outras referências primárias consultadas

- [ANTT — ViaCosteira](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-viacosteira/ccr-viacosteira-capa): página oficial da concessão, consultada como referência institucional. Os limites quilométricos usados nos cálculos foram lidos na configuração do projeto, não tratados como levantamento novo em campo.
- [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/): referência para a meta de acessibilidade proposta. Não comprova conformidade do SENTINELA.
- [Código da aplicação](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py), [processamento](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt.py), [gráficos](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt_charts.py), [relatório](https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt_report.py): evidência da implementação no commit fixado. Não prova, sozinho, qual commit o servidor executa.

Não foram inventadas referências científicas ou estatísticas de eficácia preventiva. A presente avaliação de validade decorre dos arquivos, das unidades de observação e da implementação examinada. Não houve estudo de intervenção, validação causal, teste preditivo ou comprovação de inovação inédita.

## 11. Evidências de cálculo e possibilidade de reprodução

| Arquivo do pacote | Conteúdo |
|---|---|
| evidencias/calculos/validacao_independente.json | Perfis, hashes, geografia, coorte, pareamento A/B, persistência, contexto e reconciliação. |
| evidencias/calculos/ranking_coorte.csv | IDs, medidas, dias e localização da coorte recalculada. |
| evidencias/calculos/anual_recalculado.csv | Contagens, índice e cobertura por radar/ano. |
| evidencias/calculos/mensal_recalculado.csv | Contagens, índice e cobertura por radar/mês. |
| evidencias/calculos/equipamentos.csv | Localização dos 42 pontos da base A. |
| evidencias/calculos/contexto_2km.csv, contexto_5km.csv, contexto_10km.csv | Medidas recalculadas nos segmentos e calendários comuns. |
| evidencias/calculos/checagem_ab_agregada.json | Limitações que permanecem ao agregar as faixas de A/B. |
| evidencias/calculos/qualidade_intradiaria.json | Exemplo de 29/08/2025, com causa não determinada. |
| evidencias/calculos/sensibilidade_cobertura.json | Sensibilidade a 80/90/95% de publicação anual. |
| evidencias/calculos/prf_independente.json | Contagens PRF e hashes dos ZIPs. |
| evidencias/calculos/conferencia_exportacao.json | Comparação do CSV real do site com o recálculo. |
| evidencias/downloads/ | CSV e Markdown efetivamente exportados da aplicação. |
| evidencias/capturas/ | Oito capturas, com mapa de testes/problemas no relatório de auditoria. |
| evidencias/observacoes_ambiente.json | Viewport, idioma, geometria de sobreposição e limite da navegação. |

### Procedimento de reprodução para outra pessoa

1. Obter os quatro CSVs e o manifesto do snapshot conferido, ou o ZIP já disponibilizado ao projeto. Conferir os SHA-256 completos desta fonte antes de analisar.
2. Ler os arquivos com separador ponto e vírgula e codificação correta, preservando nomes e valores originais.
3. Converter datas dd/mm/aaaa e contagens, normalizar apenas espaços dos rótulos de velocidade e verificar o domínio das oito faixas de A.
4. Localizar repetição da chave ID/data/sentido/faixa/intervalo; colocar os equipamentos-dia ambíguos na quarentena declarada, sem deduplicação arbitrária de categorias.
5. Somar A por equipamento/data; H usa apenas as três faixas superiores a 120. Agregar por mês/ano, contar datas e calcular razão entre somas.
6. Selecionar os IDs com >=90% dos dias em cada um de 2024 e 2025. Comparar os 20 IDs, totais, extremos e índices com as saídas de auditoria.
7. Fazer pareamentos A/B estrito e agregado, mantendo sem correspondência como ausentes e contando B>A. Nenhum desses pareamentos validou a taxa.
8. Associar D somente com controle de cardinalidade; preservar VC101-20 sem limite de referência.
9. Para C, preservar repetições, associar por segmento e data comum sem multiplicação por sensor; repetir 2/5/10 km.
10. Reproduzir os casos de interface no produto que estiver disponível e comparar com o snapshot. Não assumir que resultado diferente após atualização seja erro sem comparar versões.

O script analítico independente `evidencias/verificar_dados.py` pode ser usado em uma pasta descartável. Ele lê `insumos/bases/` com os quatro CSVs e manifesto e a referência `evidencias/repositorio/relatorios/resumo_antt.json` do commit fixado; escreve somente em `evidencias/calculos/`. Os CSVs brutos e uma cópia integral do repositório não foram duplicados no pacote de auditoria. Para executar o script, preparar essas entradas a partir das fontes/artefatos identificados. Não executar sobre dados de produção ou confundir o script de auditoria com correção do app.

## 12. O que permanece não verificado

- Bytes mais recentes servidos pela ANTT depois do snapshot, por falha do novo download nesta sessão.
- Completude horária/intradiária, universo de possíveis infratores, faixa física e critério operacional suficiente para B/A.
- Motivo dos dias de volume reduzido e da ausência de certas linhas.
- Limites regulamentados históricos e equivalência completa da referência quilométrica ao longo do tempo.
- Eventos únicos reais na base C, gravidade e subregistro por fonte.
- Causa/efeito de velocidade sobre acidentes, risco individual, eficácia de medidas e previsão.
- Commit realmente em produção e configuração efetiva do serviço.
- Finalização de busca/colunas/tela cheia da tabela, toolbar Plotly, mobile, leitores de tela, desempenho e compreensão por participantes reais.

O inventário permite implementar melhorias sem tratar essas lacunas como fatos conhecidos. A taxa B/A permanece não validada; a descrição de contagens publicadas permanece reprodutível nos limites deste snapshot.
