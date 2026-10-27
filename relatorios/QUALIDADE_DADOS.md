# Qualidade dos dados — ANTT 2.0

Registro histórico dos dados coletados em 26/10/2026. Os resultados de integração abaixo foram preservados; não são uma nova inspeção dos CSV nesta revisão.

A rotina `python -m src.antt` exige os quatro CSV originais com os hashes do manifesto e escreve saídas; esses CSV não estão neste pacote. Para repetir o ETL, preparar uma cópia descartável com esses insumos. A validação disponível offline parte dos Parquet e reconcilia diário/mensal/anual/coorte: veja [VALIDACAO_SENTINELA.md](../VALIDACAO_SENTINELA.md). Resultados históricos de máquina: `auditoria_antt.json`.

| Verificação | Resultado | Tratamento |
|---|---|---|
| Hash dos quatro CSV | 4/4 coincidem com o manifesto | Bloquear se edição divergir |
| Linhas A / B / C / D | 329.410 / 155.929 / 8.841 / 1.256 | Preservar originais |
| Datas e contagens de passagens | Válidas, inteiras e não negativas no snapshot | Conversão explícita e bloqueio de valores inválidos |
| Categoria veicular ausente em A | 251.438 linhas | Não inferir classe nem reconstruir infração legal |
| Sobreposição ambígua em A | 384 linhas em 41 equipamentos-dia | Quarentena integral de 420 linhas e 526.390 contagens em 30/04/2023 |
| ID/localização A–B | 42 coincidem em km/sentido | Insuficiente para validar denominador |
| Chave estrita B sem A | 36.509 de 71.705 unidades | Bloquear B/A |
| B supera A em correspondências | 6 unidades | Bloquear B/A |
| D: correspondência espacial exata | 41/42; VC101-20 sem referência | Left join 1:1, sem vizinho |
| Repetições integrais em C além da primeira | 187 | Preservar: não há ID de evento |
| Repetições integrais em D nacional | 8 | Recorte ViaCosteira tem 41 chaves espaciais únicas |
| Cobertura anual principal | 20/42 pontos têm ≥90% em cada ano | Coorte fixa e sensibilidade 80/90/95% |
| Cobertura mensal | Corte de exibição ≥80% dos dias | Lacuna em vez de índice zero |

Todas as somas de A após quarentena são conservadas na agregação diária e na junção cadastral. A chave final é ID/data, sem duplicatas. Acidentes têm `linha_fonte` e `chave_repetida`, preservando rastreabilidade. Colunas derivadas incluem ano, mês, quantidade alta, cobertura e índice por 10 mil.

Ausência de publicação não significa ausência de tráfego, excesso ou acidentes. Contagens no mesmo ponto e período evitam o denominador incompatível de B, mas não demonstram completude de publicação. Fluxos em radares diferentes não são veículos únicos.

O ano PNV/SNV do cadastro não é data de instalação. Limites atuais não foram projetados sobre 2024–2025. Valores extremos de velocidade são faixas publicadas, sem remoção por conveniência nem substituição por média de intervalo.

## PRF independente

Os 1.750 registros do corredor em 2024–2025 estão em `dados_tratados/ocorrencias.parquet`. Os ZIP originais e seu manifesto não acompanham este checkout. Há 46 divergências de soma de pessoas, mantidas com flags. Não há soma ou deduplicação cruzada com os 3.499 registros ANTT no mesmo período. O dicionário e os testes do módulo PRF da entrega completa não estão neste checkout; as flags existentes foram preservadas. Os achados principais desta versão usam ANTT.
