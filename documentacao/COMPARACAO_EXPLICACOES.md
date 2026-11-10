# Prova de conceito de explicação

Cinco recortes do snapshot `2026-10-26.1` foram executados localmente. As [respostas integrais lado a lado](evidencias/mapa-compartilhado/respostas-lado-a-lado.md) e a [saída JSON](evidencias/mapa-compartilhado/comparacao-local.json) registram o texto, o tempo de composição e o estado de cada provedor.

| Caso | Texto local, fatos principais | GPT-5.4 mini | Gemini 3.1 Flash-Lite |
|---|---|---|---|
| Velocidade recorrente · Laguna, VC101-9, 2024–2025 | ANTT base A: 7.091 de 11.178.995 contagens acima de 120 km/h, 6,343 por 10 mil. Cobertura de 361/366 e 365/365 dias. Mesmo ponto em anos comparáveis. Medir velocidades atuais e conferir limite, sinalização e condições. | Pendente | Pendente |
| Registro isolado · Laguna, VC101-9, 2024 | 3.324 de 5.322.924, índice 6,245. A consulta contém um único ano comparável, com 361/366 dias. Registrar e reavaliar quando houver outro período comparável ou evidência atual. | Pendente | Pendente |
| Ano parcial · Laguna, VC101-9, 2026 | 2.183 de 3.002.851, índice 7,270. Apenas 181/365 dias publicados, resultado exploratório. Conferir os dias de coleta e obter cobertura do período necessário. | Pendente | Pendente |
| Acidentes sem radar · Passo de Torres, 2024–2025 | Sem contagens de velocidade no local. A PRF publicou 19 registros no corredor, em ambos os sentidos. Revisar as ocorrências e a gravidade, conferir os locais e medir se a decisão depender de velocidade. | Pendente | Pendente |
| Sem dados publicados · Passo de Torres, 2022 | Sem contagens de velocidade, com PRF indisponível no ano. Conferir a cobertura com a fonte. | Pendente | Pendente |

A composição em Python levou menos de 1 ms por caso nesta execução, sem custo de API. O tempo exclui a consulta, o navegador e a rede. Os cinco textos preservaram local, período, fonte, valores, recortes e próximo passo da ficha. A ordem fixa facilita a comparação entre recortes. A hipótese a avaliar é se antecipar a limitação nos casos sem publicação e as fontes no caso sem radar melhora a compreensão. Participantes e APIs ainda não foram avaliados.

Os dois adaptadores recebem o mesmo pacote estruturado de fatos calculados pelo painel. Inclui local, período, estado, valores ANTT base A, cobertura por ano/ponto, acidentes por fonte, precisão, limitações, próximo passo e motivo. A IA escolhe a abertura e a ordem de blocos de uma lista de opções compatíveis com o estado. Essa abordagem compara escolhas de apresentação em linguagem controlada. O servidor valida os campos, confere o estado contra a ficha e só renderiza os blocos locais. Tentativas de acrescentar números, misturar fontes ou trocar a ação, além de falta de chave, cota, timeout e erros de API, resultam no texto local. O relatório exportado usa a ficha original.

A integração externa vem desligada. Em ambiente de teste autorizado, `SENTINELA_AI_PROVIDER=openai` ou `gemini` seleciona um modelo. Cada consulta faz no máximo uma chamada ao provedor ativo dentro da janela do cache, por identidade da consulta, conteúdo, modelo e versão do pacote. O cache dura uma hora, comporta 128 entradas e é compartilhado pelas sessões da mesma instância. Há limite de 10 chamadas por hora por processo, 12.000 bytes no prompt, 256 tokens de saída e timeout de rede de 8 segundos, sem nova tentativa automática. O limite reinicia com o processo. As chaves `OPENAI_API_KEY` e `GEMINI_API_KEY` devem ser novas e fornecidas pelo responsável no ambiente seguro de teste, sem valores no chat, código, frontend, logs ou CI.

Para a rodada real, os projetos precisam ter acesso aos dois modelos e cota. O plano calculado para os cinco casos é **até 10 chamadas**, cinco por modelo, e **US$ 0,029280 de teto estimado**, arredondado para **US$ 0,03 para aprovação**. A estimativa usa bytes UTF-8 do prompt como margem conservadora de tokens, mais 1.024 tokens para a estrutura, e o limite de saída. O faturamento final é medido pelas APIs. Com autorização e chaves configuradas no ambiente do servidor de teste:

```bash
SENTINELA_ENABLE_PAID_AI=1 python -m scripts.compare_explanations --live --approved-max-usd 0.03
```

Acrescente `--markdown` para emitir as respostas lado a lado. Primeiro elimine qualquer resposta com divergência factual, incluindo troca de fonte, estado, número, recorte ou ação. Entre as aprovadas, compare clareza e utilidade nos mesmos casos, latência e custo calculado a partir dos tokens retornados. Sem resultados reais, o padrão é o texto local e a escolha do provedor está pendente.

| Modelo | Entrada por milhão de tokens | Saída por milhão de tokens |
|---|---:|---:|
| GPT-5.4 mini | US$ 0,75 | US$ 4,50 |
| Gemini 3.1 Flash-Lite, texto na faixa paga | US$ 0,25 | US$ 1,50 |

Fontes de preços e formatos. [OpenAI GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) · [Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-lite) · [Saída estruturada OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) · [Saída estruturada Gemini](https://ai.google.dev/gemini-api/docs/structured-output).
