# Aceitação do mapa compartilhado e da explicação · PR #3

Código validado: `9580d92c19ebf25b0c2093dcfc91f88ecd7cf331`. Snapshot `2026-10-26.1`. A versão pública não faz parte deste ensaio. Traçado SNV: o km é uma referência linear aproximada; os 5 km da ficha de acidentes e a parte desenhável do eixo são recortes distintos.

| Fluxo | Implementação e evidência | Limite ou pendência |
|---|---|---|
| Mapa compartilhado (F05–F08, F19) | Mesmo componente na Visão geral, Comparador, Contexto rodoviário e Relatório preventivo. O mapa e a lista usam os mesmos controles; uma busca exata atualiza o foco, a lista, o resumo e a URL. Selecionar ponto fora dos filtros abre a consulta correspondente. Acidentes PRF e ANTT permanecem separados. | A camada ANTT usa km, não município nem equipamento. A localização não identifica pista ou o local de uma ação de fiscalização. |
| Município, km, código (F07, F10) | Busca de catálogo testada para todos os 18 municípios, 42 códigos e referências em todo o intervalo. A busca por município sem radar pode usar a referência de localização de registros PRF; a ficha e a camada continuam nos anos solicitados. | Códigos de ocorrências PRF ficam no detalhe e na lista da camada; a busca por código é para equipamentos. Ausência de dados e falta de geometria são estados diferentes. |
| Enquadramento e acesso (F04, F11–F13) | Busca aproxima a geometria disponível. Alternância preserva seleção e enquadramento, com zoom, retorno ao corredor, agrupamento e detalhes. Lista navegável por teclado, controles do mapa com foco visível. O foco da consulta continua na URL; fundo e enquadramento ficam na aba. | Chrome com viewport móvel e toque emulado; aparelho físico, Firefox, leitor de tela e participantes pendentes. |
| Satélite e links (F14, F17) | Imagens EOX sob demanda; erro no host de imagens mostra aviso sem remover traçado, lista ou ficha. Google Maps recebe latitude/longitude somente se triadas; demais referências válidas usam busca textual identificada como aproximada. | Mosaico histórico, sem garantia de disponibilidade, atualização ou resolução para vistoria. |
| Explicação e regra preventiva (F01, F06, F10, F18) | O botão apresenta os dados e as orientações da ficha. O texto foi conferido em cinco recortes. A recomendação continua vinculada à evidência e ao relatório. | Clareza com participantes ainda pendente. |
| PNG (F18) | [PNG 2D exportado pelo Chrome](evidencias/mapa-compartilhado/mapa-2d-exportado.png), 1040 × 832; enquadramento, seleção, nome e atribuição. | O PNG é do traçado 2D, inclusive quando o fundo ativo é Satélite; não incorpora a imagem externa. |

## Inventário do corredor

Células: **marcador / trecho / texto**. ANTT acidentes não publica município, então fica fora da tabela municipal: 8.756 registros têm trecho no eixo e 85 ficam em texto. As repetições publicadas estão preservadas. O [inventário versionado](evidencias/mapa-compartilhado/inventario.json) traz cada equipamento, estado da triagem e intervalos do eixo; `python -m scripts.inventario_espacial` reproduz o levantamento. A geometria cobre 45 intervalos de 5 km total ou parcialmente, de 244,680 a 462,300; busca e ficha aceitam até 465,100.

| Município | Equipamentos ANTT | Ocorrências PRF |
|---|---:|---:|
| Araranguá | 6 / 1 / 0 | 84 / 77 / 0 |
| Capivari de Baixo | 0 / 2 / 0 | 8 / 63 / 0 |
| Criciúma | 1 / 0 / 0 | 22 / 14 / 0 |
| Garopaba | 1 / 0 / 0 | 12 / 2 / 0 |
| Imbituba | 6 / 0 / 0 | 164 / 97 / 0 |
| Içara | 3 / 0 / 0 | 83 / 68 / 0 |
| Jaguaruna | 2 / 0 / 0 | 28 / 32 / 0 |
| Laguna | 1 / 0 / 0 | 36 / 84 / 0 |
| Maracajá | 1 / 0 / 0 | 36 / 31 / 0 |
| Passo de Torres | 0 / 0 / 0 | 1 / 12 / 6 |
| Paulo Lopes | 4 / 0 / 0 | 67 / 23 / 0 |
| Pescaria Brava | 0 / 2 / 0 | 2 / 69 / 0 |
| Sangão | 5 / 0 / 0 | 57 / 46 / 0 |
| Santa Rosa do Sul | 0 / 2 / 0 | 2 / 57 / 0 |
| Sao Joao do Sul | 0 / 0 / 0 | 0 / 28 / 0 |
| Sombrio | 0 / 2 / 0 | 4 / 102 / 0 |
| Treze de Maio | 0 / 0 / 0 | 1 / 1 / 0 |
| Tubarão | 0 / 3 / 0 | 53 / 278 / 0 |
| **Total** | **30 / 12 / 0** | **660 / 1084 / 6** |

Os casos de aceitação anteriores aparecem no inventário: Laguna e Criciúma têm marcador; Imbituba tem seis equipamentos e preserva sentidos em posições coincidentes; Passo de Torres não tem equipamento ANTT e oferece ficha territorial com PRF. Garopaba é o caso adicional de ponta a ponta: VC101-2, km 264,600, sentido decrescente, 187/366 dias em 2024 e 277/365 em 2025, cobertura insuficiente para comparação.

## Evidência de navegador

| Enquadramento de Garopaba · VC101-2 | Mapa 2D | Satélite |
|---|---|---|
| Desktop (1366 px, Chrome e Brave) | [Captura](evidencias/mapa-compartilhado/desktop-2d.jpg) | [Captura](evidencias/mapa-compartilhado/desktop-satelite.jpg) |
| Celular (390 × 844, simulação) | [Captura](evidencias/mapa-compartilhado/celular-2d.jpg) | [Captura](evidencias/mapa-compartilhado/celular-satelite.jpg) |

[Aviso ao bloquear as imagens da EOX](evidencias/mapa-compartilhado/satelite-indisponivel.jpg). O primeiro ensaio ocorreu no Chrome, com o aplicativo local. A retomada usou também o Brave. A busca saiu de Laguna (VC101-9) para a ficha municipal de Garopaba, e o clique no VC101-2 atualizou a seleção e a URL. O Chrome reconectado abriu a consulta padrão, mas o controle do navegador desconectou durante a repetição do fluxo. As capturas móveis e de satélite do Chrome são do ensaio do componente antes da última alteração de busca. A captura 2D desktop é da retomada no Brave. Os tamanhos e posição do marcador do par anterior estão em [medidas de enquadramento](evidencias/mapa-compartilhado/enquadramento-chrome.json). Bloqueio de rede e emulação foram removidos ao fim.

## Validação automatizada

Python 3.12.14. A suíte local passou com 38 testes. O contrato confirmou 12 arquivos válidos do snapshot. Compilação Python, sintaxe JavaScript e `git diff --check` sem erros. A regressão da consulta padrão preservou 226.870.300 contagens, 57.163 acima da faixa e 2,520 por 10 mil. A mesma abertura apareceu no Chrome. AppTest percorreu Laguna → Garopaba → Passo de Torres, sem ponto de velocidade, com 19 registros PRF e ficha territorial. O teste comparou a orientação da ficha com Markdown e ZIP, inclusive a distinção entre sinal isolado e recorrente. A CI da ponta do PR é acompanhada em [Checks do PR #3](https://github.com/limixin1/radarsul/pull/3/checks).

## Fundo, atribuição e custo

O 2D usa Leaflet 1.9.4 (BSD-2-Clause, distribuído no projeto) e o eixo DNIT/SNV, com atribuição no mapa e no PNG. Os rótulos municipais referenciam itens do catálogo, não limites administrativos. O modo Satélite usa o **Sentinel-2 cloudless 2016** (EOX IT Services GmbH; dados Copernicus modificados; CC BY 4.0), pelo WMTS público `s2cloudless_3857` / `GoogleMapsCompatible`. A camada foi confirmada no catálogo WMTS e as imagens foram vistas no Chrome. A imagem é fundo histórico de contexto, sem relação temporal presumida com as ocorrências, e não comprova condições atuais da pista.

A EOX permite uso comercial e não comercial gratuito no mosaico 2016 com atribuição e tráfego razoável. Não publica cota numérica nem garantia de serviço. Esta entrega não cria conta, chave ou assinatura. Busca e zoom limitados ao corredor; imagens só após escolher Satélite, com zoom nativo limitado a 14, sem pré-carregamento em lote e sem raster nas exportações. Se houver necessidade de tráfego intenso ou garantia contratual, reavaliar com a EOX antes de contratar. O navegador solicita apenas imagens por coordenadas de bloco; nenhuma ficha é enviada. O link externo Google Maps é acionado pela pessoa usuária e não fornece o fundo do painel.

Fontes: [condições de uso da EOX](https://cloudless.eox.at/documentation/faq) · [licença da imagem](https://cloudless.eox.at/documentation/license) · [mosaico de 2016](https://eox.at/2017/08/sentinel-2-global-cloudless-mosaic/) · [Google Maps URLs](https://developers.google.com/maps/documentation/urls/get-started) · [Leaflet](https://leafletjs.com/install.html).
