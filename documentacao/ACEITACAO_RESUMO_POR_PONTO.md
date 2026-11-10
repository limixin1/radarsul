# Resumo por ponto e avaliação Gemini Free Tier

O cartão ao lado do mapa e a abertura da ficha usam os mesmos dados e a mesma ordem do Markdown e do ZIP. O ensaio compara a referência `738dfee` com o código `88fe23a`, no snapshot `2026-10-26.1`. O ajuste final esclarece que, em trechos com vários equipamentos, a repetição é verificada por ponto. A [CI do PR #3](https://github.com/limixin1/radarsul/pull/3/checks) identifica a ponta que inclui as evidências.

| Requisito | Evidência | Resultado e limite |
|---|---|---|
| Ordem de leitura e detalhes | [Antes desktop](evidencias/resumo-por-ponto/antes-desktop.jpg), [depois desktop](evidencias/resumo-por-ponto/depois-desktop.jpg), [antes 390 px](evidencias/resumo-por-ponto/antes-mobile.jpg), [depois 390 px](evidencias/resumo-por-ponto/depois-mobile.jpg), [série móvel](evidencias/resumo-por-ponto/depois-mobile-serie.jpg) | A referência abre o cartão com cobertura e orientação. O candidato coloca local, período, fatos por fonte, série e próximo passo nessa ordem. Código, coordenada, eixo, dias publicados e critérios ficam em Ver dados e fontes. O móvel foi emulado no Chrome, sem aparelho físico. |
| Recorte e período | km 330–335 com VC101-11 e VC101-12. Mudança para [somente 2025](evidencias/resumo-por-ponto/somente-2025.jpg) no Chrome | O cartão recalculou ANTT de 223 para 90 e PRF de 172 para 79. A série de velocidade também usa o ponto, o ano e os dias publicados correspondentes. |
| Precisão e orientação territorial | Snapshot de Passo de Torres, 2024–2025. No Chrome, 2025 e [2022 sem publicação](evidencias/resumo-por-ponto/passo-de-torres-2022.jpg). Regressão com dados sintéticos para as regras de distribuição | Em 2024–2025 são 19 registros PRF. Seis têm km sem traçado disponível, dos quais cinco na faixa km 463–464. A ficha orienta confirmar a posição antes de escolher um trecho. Em 2025 são dez registros, quatro sem eixo e três na faixa 463–464. Em 2022 a mensagem é de publicação indisponível. Concentração, dispersão e referência insuficiente tiveram testes separados. |
| Busca, seleção e mapa | Chrome desktop. Laguna VC101-9 → ficha municipal de Garopaba → marcador VC101-2. [Satélite](evidencias/resumo-por-ponto/garopaba-satelite.jpg) | URL e lista acompanharam o novo foco. Marcador em x=244, y=160 relativo ao mapa nos dois fundos. Seis imagens de satélite carregaram. O link Google Maps do ponto usa a coordenada triada. Trechos e municípios usam a ação Busca aproximada. |
| Ficha e arquivos | [Downloads Chrome inspecionados](evidencias/resumo-por-ponto/downloads-chrome.json), [PNG de Garopaba](evidencias/resumo-por-ponto/garopaba-png-2d.png), AppTest | Markdown de Garopaba em 2025 idêntico ao `relatorio.md` do ZIP. Ordem e próximo passo conferidos. PNG 1038 × 832. ZIP territorial de Passo de Torres em 2022 íntegro e com ausência de publicação explícita. AppTest validou a mesma orientação na ficha e no relatório de Laguna com sinal recorrente e com um único ano. A [ficha de Laguna no Chrome](evidencias/resumo-por-ponto/laguna-recorrente.jpg) e o botão de explicação confirmaram a orientação no km 304,000. |
| Segurança e avaliação Gemini | [Execução local](evidencias/resumo-por-ponto/comparacao-local.json), [cinco casos lado a lado](evidencias/resumo-por-ponto/respostas-lado-a-lado.md), [pacotes manuais](evidencias/resumo-por-ponto/pacotes-chatgpt-claude.json) | Zero chamadas externas. A chave não estava configurada no servidor de teste e o nível do projeto não pôde ser confirmado para uma chave nova. O teste simulado confirmou o bloqueio de um projeto não atestado, cinco respostas Gemini aceitas pelo esquema e retorno local com interrupção da rodada após HTTP 429. |
| Validação do pacote | `python -m src.data_package validate`, `python -m pytest -q` e compilação Python | 41 testes locais em Python 3.12.14. Snapshot e dados de origem preservados. Firefox, leitor de tela, participantes e aparelho móvel físico continuam pendentes. |

## Km 330–335 no mesmo recorte

| Série de acidentes | 2024 | 2025 | Total |
|---|---:|---:|---:|
| ANTT, trecho e ambos os sentidos | 133 | 90 | 223 |
| PRF, trecho e ambos os sentidos | 93 | 79 | 172 |

A PRF registrou 43 colisões transversais e 40 colisões traseiras, de 172 registros. A primeira é a categoria mais frequente no arquivo selecionado. Nenhuma faixa de 1 km reuniu a maioria dos registros em qualquer das fontes. O arquivo de acidentes ANTT contém data e km, sem tipo. A velocidade tem base distinta e pertence aos equipamentos. Foram 2.329 de 27.443.639 contagens nas faixas acima de 120 km/h nos dois pontos em 2024–2025. O cartão mostra os valores de cada ponto por ano e a regra informa que a faixa publicada não identifica uma infração.

## Critérios descritivos

- Tipo em destaque exige pelo menos cinco registros, campo preenchido em todos e liderança por dois registros ou mais. A ficha cita o numerador e o total da fonte. Empate, frequências próximas e campo incompleto têm mensagens próprias. A faixa de cinco registros e a diferença de dois são limites de apresentação para evitar promover amostras pequenas e quase empates.
- A distribuição usa intervalos disjuntos de 1 km a partir do km publicado. Um destaque exige pelo menos cinco registros com referência no eixo, que representem mais da metade de todos os registros da fonte no período coberto. O denominador mantém registros sem eixo. Com dispersão, orienta conferir locais antes de escolher uma faixa. Quando falta geometria, mostra a lacuna e orienta confirmar primeiro a faixa com mais registros sem eixo. A base pode descrever onde publicou mais registros, sem estimar risco, causalidade ou efeito de intervenção.
- Para velocidade, o cartão usa numerador e denominador ANTT base A por equipamento e ano. O índice aparece na série apenas para anos com publicação suficiente conforme a regra existente. Ano parcial, ausência de publicação e total zero têm rótulos próprios. A ficha usa as magnitudes anuais para explicar a repetição. Um único ano com dados suficientes orienta registrar o observado e reavaliar com outro período ou evidência atual. Fiscalização e blitz dependem de evidência atual e validação da autoridade competente.

## Rodada de custo zero

| Caso | O texto local torna explícito | Gemini Free Tier |
|---|---|---|
| Laguna VC101-9, 2024–2025 | 7.091 de 11.178.995 em dois anos com dados suficientes, série anual e o que medir no km 304,000 | Pendente |
| Laguna VC101-9, só 2024 | 3.324 de 5.322.924, um ano com dados suficientes e quando reavaliar | Pendente |
| Laguna VC101-9, só 2026 | 2.183 de 3.002.851, ano parcial e checagem da publicação | Pendente |
| Passo de Torres, 2024–2025 | 19 registros PRF, 9 em 2024 e 10 em 2025, sem radar e com km sem traçado | Pendente |
| Passo de Torres, só 2022 | Fonte sem publicação e checagem de cobertura | Pendente |

O texto local foi conferido quanto à ordem, aos recortes, às fontes e à utilidade da checagem. O JSON registra latência de composição por caso, sem incluir consulta, navegador ou rede. Nenhuma diferença de clareza ou utilidade entre modelos foi medida. GPT por API continua pendente. Os pacotes para ChatGPT e Claude foram preparados para teste manual, sem submissão nesta rodada. Para comparar manualmente, use as instruções e um caso por vez do JSON. Valide as chaves e o estado do JSON retornado e monte o texto com a abertura e a ordem propostas antes de comparar com o resultado local.

Para executar a rodada de até cinco chamadas de custo zero, o responsável deve confirmar no Google AI Studio que o projeto ligado à **chave nova** está no Free Tier e verificar no Google Cloud que esse mesmo projeto tem Cloud Billing desativado. Só depois, no servidor de teste, configure a chave no ambiente seguro e sinalize a verificação:

```bash
SENTINELA_GEMINI_FREE_TIER_VERIFIED=1 python -m scripts.compare_explanations --provider gemini --live
```

A variável atesta a conferência pelo responsável. O aplicativo não consulta a conta de faturamento a partir de uma chave da Gemini API. Sem chave ou atestado, o avaliador só retorna texto local. A primeira resposta de cota interrompe as chamadas restantes. O provedor recebe apenas fatos públicos agregados e escolhe a abertura e a ordem, com blocos obrigatórios e recomendação preservados. O opt-in gratuito é específico do avaliador. [Tarifa Free Tier do modelo](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite) · [Níveis e Cloud Billing](https://ai.google.dev/gemini-api/docs/billing)
