Auditoria de produto do SENTINELA

Funcionalidade usabilidade design acessibilidade dados e operação

Data: 2 de novembro de 2026. Versão examinada: SENTINELA 2.0, commit e5baed4fdab7575690a408f4ab492fd63790a00e. Aplicação: https://radarsul.site/.

1 Parecer sobre o estado do produto

O SENTINELA funciona nos principais percursos de consulta e exportação. A transformação das quatro bases ANTT foi reproduzida a partir do ZIP fornecido: os oito Parquet reconstruídos são idênticos, inclusive byte a byte, aos arquivos do repositório. O serviço publicado corresponde ao commit examinado. Esses resultados sustentam a existência de uma aplicação utilizável para uma demonstração acompanhada.

A liberação para navegação independente por pessoas leigas ainda exige correções. A interface apresenta ausência de cobertura como zero acidentes, mantém gráficos com uma população diferente da seleção local e destaca resultados com cobertura muito pequena. Também foram identificados problemas de contraste, idioma da página, vocabulário, localização dos equipamentos e recuperação de erros.

Recomendo corrigir primeiro os problemas que alteram a interpretação dos resultados. Em seguida, simplificar o percurso principal e executar aceitação em celulares, com leitores de tela e com usuários representativos. Para oferecer disponibilidade contínua, será necessário resolver as limitações operacionais da instância gratuita e medir a capacidade real do serviço.

Esta entrega é uma auditoria com plano de correção. Não foram aplicadas alterações ao código publicado, ao GitHub ou à configuração do Render.

2 Escopo e critérios da avaliação

O objetivo de produto adotado é permitir que um visitante encontre um ponto da BR-101/SC, consulte contagens publicadas de velocidade, compreenda sua cobertura e exporte um resultado verificável. A interpretação científica continua descritiva. O sistema não foi avaliado como previsão validada de acidentes nem como ferramenta para decisões automáticas de fiscalização.

A análise combinou navegação real no domínio próprio, inspeção do código correspondente ao commit, consultas de implantação e métricas, comparação dos downloads e reconstrução dos dados ANTT. O navegador observado foi Chrome em desktop, com área de visualização de 1.363 por 936 pixels CSS. A avaliação de facilidade de uso é uma inspeção especializada; ainda não é um estudo com participantes leigos.

Os achados distinguem três situações: defeito reproduzido na interface, limitação confirmada no código ou na plataforma e verificação ainda pendente. P1 significa corrigir ou resolver antes de declarar o produto adequado para uso público independente. P2 reúne problemas que precisam entrar na preparação da versão estável. P3 indica aperfeiçoamento posterior. A prioridade se refere ao uso proposto, não a uma classificação de incidente de segurança.

3 Evidências já confirmadas

Verificação

Resultado

Implantação

Deploy dep-dbg7476c6qcc73ei65g0 em estado live, com o mesmo SHA da branch main

Código local examinado

Os 31 arquivos do commit presentes na cópia de auditoria coincidem com os hashes de blobs do GitHub

Domínio e saúde

HTTPS respondeu; /_stcore/health retornou HTTP 200 e ok

Redirecionamentos

HTTP e www terminaram em https://radarsul.site/

Integridade dos dados brutos

Os seis arquivos de dados do ZIP coincidem com os tamanhos e SHA-256 dos registros de coleta

Reconstrução ANTT

Oito Parquet idênticos byte a byte; três JSON de auditoria e resultados semanticamente idênticos

Lógica dos filtros

512 estados examinados; 341 com dados e 171 vazios; nenhuma exceção nos cenários executados

Comparação em CSV

Download real com três linhas; identificadores, contagens e índices conferidos

Relatório em Markdown

Download real de 4.684 bytes; conteúdo idêntico ao gerado com os mesmos filtros

Gráfico em PNG

Download real válido, com 893 por 520 pixels

Teclado

A navegação entre páginas por setas do grupo de opções funcionou



Os 512 estados correspondem às combinações dos subconjuntos de cinco anos, quatro recortes e subconjuntos dos dois sentidos. A execução verificou agregação, conservação de contagens, geração dos relatórios e 11 casos de contexto espacial. Essa matriz cobre a camada de dados; renderização, downloads e navegação foram conferidos separadamente nos cenários de navegador descritos adiante.

O índice agregado da coorte foi reproduzido em 2,519633 por 10 mil, a partir de 57.163 contagens acima de 120 km/h e 226.870.300 contagens publicadas. O maior índice padrão foi 6,343146, do equipamento VC101-9, em Laguna. Os resultados conferem com o snapshot tratado examinado.

4 Correções prioritárias de interpretação e acessibilidade

F01 Ausência de cobertura apresentada como zero acidentes

Situação confirmada e prioridade P1. Selecionar somente 2026 e abrir Contexto rodoviário apresenta zero registros ANTT e zero ocorrências PRF. A base ANTT de acidentes termina em 31/12/2025; o arquivo PRF incluído contém somente 2024 e 2025. O mesmo problema de PRF pode ocorrer ao selecionar 2022 ou 2023, pois o código filtra e conta uma tabela sem aqueles anos.

O visitante pode interpretar esses zeros como ausência de acidentes na rodovia. A mensagem correta deve identificar a cobertura de cada fonte e informar que não há dados disponíveis para o período solicitado. Seleções que misturam anos cobertos e descobertos devem mostrar os anos efetivamente utilizados, sem apresentar a contagem como representativa do período inteiro.

Critério de aceite: 2026 isolado produz indicação de indisponibilidade para ANTT e PRF; 2022 isolado produz indisponibilidade da PRF; 2025 junto com 2026 explicita cobertura parcial. Zero só aparece quando a fonte cobre o período e não há registros no recorte consultado. Referência: app_antt.py, linhas 76 a 83, e períodos dos arquivos.

F02 Gráficos não acompanham a seleção local de equipamentos

Defeito reproduzido e prioridade P1. No comparador, selecionar apenas VC101-9 reduz a tabela e a base de possíveis infratores, mas mantém o gráfico de persistência da coorte, com Spearman 0,96. Retirar todos os equipamentos também mantém esse gráfico. No histórico, a curva usa a seleção local, enquanto a matriz mensal continua usando os equipamentos do recorte global.

O código usa chosen para parte da tela e ids para os gráficos secundários. A interface não identifica essa diferença com clareza. Uma seleção visualmente única passa a representar populações diferentes.

Correção recomendada: fazer todos os componentes de comparação usarem o mesmo filtro. Se houver valor em manter um panorama geral, separá-lo e nomear explicitamente sua população. Critério de aceite: com um equipamento, a curva, a matriz, a tabela e a exportação exibem esse ponto; a correlação entre equipamentos fica indisponível e explica a necessidade de ao menos dois pontos elegíveis. Com seleção vazia, a tela orienta a seleção e não oferece uma comparação aparentemente válida. Referência: app_antt.py, linhas 48 a 64.

F03 Ranking destaca resultados sem qualificar sua cobertura

Limitação de produto reproduzida e prioridade P1. Em Todos os equipamentos e ano 2022, a manchete destaca índice 80,47 por 10 mil. O equipamento VC101-28, de Içara, tem apenas três dias publicados: 58 contagens altas em 7.208 contagens totais, aproximadamente 0,82% dos dias do ano.

A divisão está correta. O problema é a apresentação do maior valor como destaque sem a cobertura correspondente na manchete ou na barra. O aviso geral de que existem equipamentos fora da coorte não permite que um leigo avalie a fragilidade daquele resultado. O cartão de dias distintos mostra 365 para o conjunto, o que também não informa os três dias do equipamento destacado.

Correção recomendada: exibir cobertura por equipamento e ano, junto ao índice; manter o modo de comparação confiável como padrão; identificar os demais como exploração com cobertura insuficiente. A regra de elegibilidade deve ser definida e documentada para o período realmente selecionado. A elegibilidade de 2024 e 2025 não garante representatividade de 2022.

Critério de aceite: VC101-28 em 2022 aparece com três dias e aviso de cobertura insuficiente; sua apresentação não sugere comparação equivalente com um ano completo. Diferenciar cobertura do ano calendário de cobertura do período publicado em anos parciais. Referências: app_antt.py, linhas 35 a 45; equipment_table; ranking.

F04 Legendas têm contraste insuficiente

Medição na interface e prioridade P1. As legendas examinadas usam texto rgb(20,43,60) em um ancestral com opacidade 0,6. Sobre o fundo principal rgb(250,251,252), a composição resulta em contraste aproximado de 4,02:1. Sobre a barra lateral rgb(238,243,245), o contraste é aproximadamente 3,91:1. Os textos medidos têm 14 pixels.

Esses valores ficam abaixo de 4,5:1, referência WCAG 2.2 para texto comum. As legendas incluem informações essenciais sobre coleta, lacunas e limites de interpretação. Sua leitura não pode depender de visão confortável ou de ampliação.

Critério de aceite: remover a redução de opacidade ou escolher cores cuja composição final atinja ao menos 4,5:1; verificar também avisos, eixos, notas de gráficos e estados de foco. A medição de algumas legendas não equivale a uma certificação completa de acessibilidade. Referências: estilos computados na página; WCAG 2.2, critério 1.4.3.

5 Design e facilidade de uso para pessoas leigas

F05 Textos sobre a coorte permanecem fixos em outros recortes

Defeito reproduzido e prioridade P2. Depois de selecionar Todos os equipamentos, a visão geral mostra 42 equipamentos, mas a legenda continua dizendo Coorte fixa de 20 de 42. A frase também permanece nos recortes locais e nas seleções de apenas um sentido.

A legenda precisa informar quantos equipamentos estão na seleção, quais regras foram aplicadas e quais anos sustentam a elegibilidade. Informações sobre a coorte original podem ficar na explicação metodológica. Aceite: legenda, cartões, gráfico e filtro descrevem a mesma população em todos os recortes. Referência: app_antt.py, linha 45.

F06 Vocabulário e tabelas exigem conhecimento técnico prévio

Inspeção de usabilidade e prioridade P2. O primeiro contato apresenta coorte, recorte, persistência, contagens, B/A e Spearman sem uma explicação próxima à decisão que o visitante precisa tomar. O comparador mostra nomes internos como por_10_mil, altas e passagens. Crescente e decrescente também precisam ser relacionados à quilometragem.

Recomendo usar rótulos orientados à tarefa: grupo de equipamentos com boa cobertura; área consultada; histórico do índice; contagens acima de 120 km/h; índice por 10 mil. Um texto curto deve explicar Spearman como semelhança na ordenação dos pontos entre períodos, sem sugerir previsão ou causalidade. Os termos técnicos podem permanecer em detalhes acessíveis.

Aceite: uma pessoa sem formação em dados consegue identificar local, período, significado do índice e limite da conclusão. Deve compreender que contagens não representam veículos únicos nem acidentes prováveis. A validação dessa compreensão exige o teste com participantes descrito na seção 10.

F07 Equipamentos são difíceis de localizar

Limitação confirmada e prioridade P2. As seleções e barras priorizam códigos como VC101-9. A cidade e o quilômetro aparecem na tabela ou ao passar o mouse. A navegação oferece a coorte, todos os equipamentos, Criciúma e seu entorno, sem um filtro simples para as demais cidades.

Cada opção deve mostrar município, BR, quilômetro, sentido e identificador. Um filtro por cidade e busca textual resolveriam a maior parte dessa dificuldade. Um mapa pode complementar a consulta depois dessas correções; sua presença não substitui rótulos claros e acesso por teclado.

Aceite: o visitante encontra Laguna no km 304 e Criciúma no ponto correspondente sem conhecer o código do equipamento. Explicar que crescente acompanha o aumento dos quilômetros e decrescente o caminho inverso, evitando inventar referências geográficas sem validá-las.

F08 A abertura não explica o percurso de uso

Inspeção de design e prioridade P2. A página abre com o maior índice do recorte, sem nomear o município e sem explicar o que fazer com o resultado. O mesmo título aparece novamente no gráfico. O índice agregado da seleção não é destacado; o usuário recebe a maior observação individual antes de entender o conjunto.

Recomendo abrir com uma descrição curta do serviço, o período e a área ativos, seguida de uma ação principal para consultar um local. Na leitura do resultado, apresentar o ponto, o índice, a cobertura e uma explicação de uma frase. O maior índice deve ser identificado como maior valor entre os pontos elegíveis daquela seleção.

O ranking apresenta até 12 equipamentos, mas essa limitação não é explicitada no título. Identificar a quantidade mostrada e oferecer acesso à lista completa. Aceite: a primeira tela responde o que o serviço mostra, qual seleção está ativa e como abrir uma consulta local.

F09 Números e textos precisam de apresentação consistente

Situação confirmada e prioridade P2. Os cartões usam separadores brasileiros, enquanto tabelas e gráficos exibem pontos decimais e nomes de campos internos. O relatório mostra valores como 2.520, que podem ser interpretados como dois mil quinhentos e vinte no padrão brasileiro. A comparação contém precisão excessiva para leitura cotidiana.

Formatar a apresentação em português brasileiro, com unidade no cabeçalho, separador de milhar e duas ou três casas decimais conforme a finalidade. Manter a precisão completa em exportações técnicas documentadas. A escolha do formato de CSV precisa considerar seu uso em planilhas brasileiras, preservando também uma opção interoperável.

Aceite: a mesma medida tem o mesmo significado em cartão, tabela, gráfico e relatório. A interface mostra por exemplo 2,520 por 10 mil, com explicação da unidade.

F10 Estados vazios e recuperação não orientam suficientemente

Defeito do comparador reproduzido e prioridade P2. A comparação sem equipamentos mantém tabela vazia, botão de CSV e gráfico de outra população. O histórico, por sua vez, apresenta uma orientação adequada quando a seleção fica vazia. A seleção global sem dados tem uma mensagem genérica, sem indicar qual filtro produziu o vazio.

Aplicar o comportamento do histórico ao comparador e oferecer uma ação para restaurar uma seleção válida. Ao combinar Criciúma com um sentido sem equipamento disponível, explicar essa incompatibilidade. Aceite: cada estado vazio informa a causa provável e uma ação de recuperação; downloads vazios são desabilitados ou claramente identificados.

F11 Atualizar a página perde a consulta

Comportamento reproduzido e prioridade P2. Recarregar após selecionar 2022 e Todos os equipamentos voltou à visão geral padrão de 2024 e 2025. A URL não registra os filtros. O visitante não consegue compartilhar um endereço que preserve sua consulta.

Persistir os filtros importantes em parâmetros de URL validados e manter o estado local durante a navegação. Disponibilizar um comando explícito para restaurar o padrão. Aceite: copiar o endereço e abri-lo em uma sessão nova reproduz área, anos e seleção suportados, sem aceitar parâmetros inválidos ou silenciosamente trocar a população.

F12 Idioma e alternativas acessíveis precisam de revisão

Situação confirmada e prioridade P2. O HTML declara lang="en", embora a página esteja em português. Parte dos controles dos gráficos e tabelas também aparece em inglês. Isso prejudica pronúncia por leitor de tela e compreensão de comandos.

A navegação básica por teclado entre páginas funcionou. Ainda faltam testes completos de foco, ordem de tabulação, entrada e saída dos gráficos, leitura das tabelas e anúncios após mudar filtros. Cada gráfico precisa de resumo textual e alternativa tabular alcançável, inclusive para os valores que hoje dependem do mouse.

Aceite: idioma português declarado por mecanismo suportado, controles compreensíveis, foco visível e acesso a todas as funções relevantes por teclado e leitor de tela. Corrigir o idioma sem depender de alterações frágeis que desapareçam em atualizações do Streamlit.

F13 Espaçamento e adaptação a telas precisam de aceitação

Problema visual observado e verificação pendente, prioridade P2. A linha de contexto no topo aparece parcialmente encoberta no desktop examinado. O CSS reduz o espaçamento superior para dois rem; o ajuste precisa considerar o cabeçalho do Streamlit. Títulos de gráficos têm tamanho fixo de 23 pixels e notas de fonte usam 10 pixels, com margens fixas.

As capturas não permitem afirmar que todo celular apresenta corte ou transbordamento. O teste de largura reduzida por zoom não foi efetivado pelo navegador disponível. Permanecem obrigatórios testes reais de adaptação e ampliação antes de declarar aprovação nessa frente.

Aceite: conteúdo principal e filtros utilizáveis em larguras de 320, 360, 390 e 768 pixels CSS e em desktop; ampliação de texto preserva funções; títulos e fontes não se sobrepõem. Tabelas e mapas podem exigir rolagem bidimensional, mas textos e controles comuns devem reorganizar-se. Referência de reflow: WCAG 2.2, critério 1.4.10.

6 Robustez funcional dados e exportações

F14 Recuperação aponta para um programa inexistente

Defeito confirmado no código e prioridade P2. Se o carregamento falha, o aplicativo orienta executar python analisar.py. Esse arquivo não existe no commit. O comando disponível para reconstruir ANTT é python -m src.antt, com os quatro CSV e o manifesto na pasta esperada.

O visitante deve receber uma mensagem de indisponibilidade e recuperação apropriada ao seu papel. Detalhes de caminho e exceção devem ir para os registros operacionais. A equipe precisa de um procedimento real de restauração, validado em cópia isolada. Aceite: ausência ou corrupção de um arquivo tratado gera uma mensagem compreensível, sem orientar o usuário leigo a executar comandos de servidor. Referência: app_antt.py, linhas 20 a 22.

F15 Validação de inicialização e atualização precisa de um contrato explícito

Limitação do código e prioridade P2. O carregamento lê seis Parquet e um JSON, sem verificar um manifesto do pacote tratado, seus esquemas ou a coerência entre os arquivos. Há validações importantes na transformação, mas elas não são integralmente repetidas ao iniciar uma instalação ou carregar uma atualização.

Criar um manifesto de versão de dados com arquivos necessários, hashes, colunas, períodos e versão da transformação. Verificar o pacote no build e em um teste de consulta; atualizar os arquivos de forma conjunta. Um health check que responde ok comprova que o servidor responde, mas não a integridade do conjunto analítico.

Aceite: um pacote com arquivo ausente, esquema divergente ou resumo de outra versão é rejeitado antes da publicação. Um teste após o deploy abre a consulta padrão e gera uma exportação.

F16 A reprodução da PRF ainda não está documentada no código atual

Lacuna confirmada e prioridade P2. O ZIP inclui os arquivos PRF de 2024 e 2025, com hashes conferidos. O repositório inclui ocorrencias.parquet, mas os módulos presentes não contêm o procedimento completo de geração desse arquivo a partir dos ZIP da PRF. A reconstrução executada nesta rodada cobre os oito produtos ANTT.

Preservar e documentar a transformação PRF, com filtros geográficos, tratamento de campos, datas, duplicidades e colunas derivadas. Aceite: uma instalação limpa reconstrói o contexto PRF, reproduz as contagens do trecho e deixa rastreável qualquer diferença. Não declarar essa cadeia integralmente reproduzida com base apenas na conferência dos arquivos originais.

F17 Fontes e materiais não estão acessíveis no ponto de uso

Limitação confirmada e prioridade P2. O painel diz que originais e hashes acompanham o pacote, mas oferece essencialmente o portal geral da ANTT. O commit contém o manifesto dos quatro CSV, sem os próprios CSV brutos. O kit enviado pelo usuário resolve sua disponibilidade para esta auditoria, mas não o acesso do visitante do site.

Oferecer uma página de fontes com o recurso específico, data de coleta, cobertura, licença ou condições de reutilização verificadas e manifesto baixável. Identificar o snapshot como histórico. A coleta de outubro não transforma dados até junho de 2026 em monitoramento em tempo real.

Aceite: o visitante consegue verificar a origem do indicador e a data máxima de cada base sem procurar arquivos internos do projeto. A documentação distingue o pacote publicado do kit de reprodução.

F18 Exportações precisam carregar todo o contexto da consulta

Downloads validados e melhoria necessária, prioridade P2. CSV, Markdown e PNG funcionaram nos cenários examinados. O CSV de comparação, porém, não inclui anos, data de coleta, regra de cobertura ou versão do código. Os relatórios têm fontes e limites, mas usam caminhos relativos para os manifestos e não registram o SHA da aplicação. O nome de arquivo é o mesmo para diferentes consultas.

Incluir metadados suficientes para reconstruir a seleção, com links utilizáveis e data de geração. Oferecer impressão ou PDF pode facilitar o uso leigo, após resolver o conteúdo. Aceite: quem recebe um arquivo entende de onde veio, quais anos e equipamentos representa e qual unidade está sendo medida, sem depender da sessão que o gerou.

F19 O contexto espacial precisa explicar seus escopos distintos

Comportamento confirmado e prioridade P2. O gráfico espacial usa somente os pontos elegíveis da coorte em 2024 e 2025. A legenda ANTT abaixo dele conta um envelope contínuo entre o primeiro e o último ponto, com margem. Já a PRF usa o trecho integral e apresenta separadamente Criciúma. Esses universos são diferentes.

Na consulta de Criciúma, o painel informa 62 registros ANTT no envelope e 1.750 ocorrências PRF no trecho integral, das quais 36 em Criciúma. A redação identifica o trecho integral, portanto não se trata de uma soma incorreta. Ainda assim, as diferenças espaciais devem estar mais próximas dos valores para evitar comparação direta entre fontes.

Aceite: cada bloco identifica área, datas, elegibilidade e unidade. Explicar por que o ponto de Criciúma não integra a coorte principal, em vez de apresentar apenas insuficiência de segmentos. Preservar a separação ANTT e PRF e os avisos contra interpretação causal.

7 Disponibilidade desempenho manutenção e segurança

F20 A infraestrutura gratuita limita a oferta contínua

Condição confirmada e prioridade P1 para uso contínuo. O serviço tem uma instância gratuita na região da Virgínia. A documentação atual do Render informa suspensão após 15 minutos sem tráfego de entrada, retomada em aproximadamente um minuto e possibilidade de reinícios. A própria plataforma recomenda não usar essas instâncias para produção.

Nas métricas amostradas, o maior consumo observado foi aproximadamente 379 MiB, cerca de 74% do limite de 512 MiB. Houve valores menores na mesma janela e identificadores distintos de instância. Esses dados não demonstram vazamento de memória nem estabelecem capacidade simultânea.

Definir a disponibilidade esperada e escolher uma configuração compatível. Medir a primeira abertura, a recuperação após inatividade e sessões simultâneas no ambiente escolhido. Aumentar o plano pode reduzir limitações da hospedagem, mas não resolve problemas de interface ou metodologia. Aceite: cumprir objetivos de tempo e estabilidade registrados na seção 10.

F21 Faltam testes automatizados e controle de publicação

Lacuna confirmada e prioridade P1. A árvore do commit examinado não contém suíte de testes ou configuração de CI. A branch main não está protegida, e o Render publica automaticamente a cada commit. Uma mudança pode substituir a versão demonstrada sem validar regressões.

Adicionar testes dos defeitos identificados, testes de contrato dos dados e um teste das cinco páginas. Usar CI antes do deploy, revisão das mudanças e uma versão de demonstração identificável. Exibir na aplicação a versão do código e do snapshot. Aceite: um teste que detecte falsa contagem zero ou gráfico fora do filtro impede a publicação de uma versão com essa regressão.

F22 Cache e observação da aplicação precisam ser mais específicos

Limitação do código e prioridade P2. load() usa cache, mas retorna todas as seis tabelas mesmo para páginas que precisam de apenas parte delas. O contexto PRF é lido novamente em cada execução dessa tela. Agregações e figuras também são refeitas nas interações. O cache sem argumento de versão não explicita a invalidação quando dados são substituídos em um processo em execução.

Carregar apenas os dados necessários, usar a versão do snapshot como entrada do cache e medir antes de otimizar. A documentação do Streamlit informa que cache_data devolve cópias; portanto, compartilhar recursos mutáveis indiscriminadamente para economizar memória exigiria cuidado adicional.

As consultas de erros e eventos de falha não retornaram entradas na janela consultada. As séries de latência e contagem HTTP vieram vazias. Isso é uma lacuna de observação, sem provar indisponibilidade ou ausência absoluta de erros. Aceite: registrar tempos de consulta, falhas de carregamento e versão; configurar alerta de indisponibilidade e um teste sintético de consulta com responsabilidade definida.

F23 Segurança precisa de verificação focada no serviço real

Revisão parcial e prioridade P2. O fluxo examinado é de leitura de dados públicos, sem cadastro, pagamento ou envio de arquivos pelo visitante. Os arquivos de configuração revisados não contêm credenciais explícitas. O uso de unsafe_allow_html observado injeta CSS fixo; não foi identificada entrada de usuário interpolada nesse trecho.

A cadeia HTTPS funcionou nos acessos examinados. Cabeçalhos como HSTS e CSP não apareceram nas respostas vistas pelo cliente HTTP da auditoria. Intermediários podem alterar cabeçalhos; esse resultado exige confirmação no caminho real de entrega antes de classificar a configuração. Uma CSP deve ser testada com os recursos do Streamlit e do Plotly.

Ainda faltam análise de dependências, verificação dos acessos administrativos e teste do comportamento de erros. Não houve teste de invasão ou constatação de vulnerabilidade explorável. Aceite: documentar essa revisão, corrigir vulnerabilidades relevantes que sejam efetivamente identificadas e manter segredos fora do código. Para a consulta pública atual, a inclusão de contas deve depender de uma necessidade de produto definida.

F24 Documentação operacional e responsabilidade precisam ser atualizadas

Inconsistência confirmada e prioridade P2. README e verificação de publicação ainda descrevem o domínio como pendente e referenciam o primeiro deploy. O domínio e a implantação atual já foram verificados. A documentação também precisa indicar o kit bruto e o procedimento correto de reconstrução.

Definir quem atualiza as bases, quem responde a indisponibilidade e como o visitante relata um problema. Registrar como voltar a uma versão conhecida e como verificar o retorno. Aceite: outra pessoa consegue instalar o pacote, reproduzir ANTT, identificar as pendências PRF, restaurar a aplicação e encontrar o responsável sem depender da memória da equipe.

8 Resultado por área da aplicação

Área

O que funciona

O que precisa mudar

Visão geral

Métricas e ranking padrão; mudanças de ano e recorte

Cobertura ao lado do destaque, legenda dinâmica, local compreensível, indicação dos 12 pontos mostrados

Comparador

Tabela, base separada e CSV conferido

Sincronizar o gráfico, tratar seleção vazia, traduzir campos e formatar números

Evolução

Série, matriz e mensagem de seleção vazia

Aplicar seleção local à matriz, explicar lacunas e disponibilizar alternativa tabular

Contexto rodoviário

Associação de 2024 e 2025; insuficiência de coorte; PNG

Distinguir indisponibilidade de zero e explicar os diferentes recortes ANTT e PRF

Relatório

Geração, fontes, limites e download conferido

Formatação brasileira, metadados da versão, links diretos e leitura mais acessível



9 Ordem de execução recomendada

Etapa

Entrega

Condição para concluir

1 Corrigir interpretação

F01, F02, F03, F05 e F19

População e cobertura coerentes em todas as telas; nenhum zero por ausência de fonte

2 Preparar uso independente

F04 e F06 a F18

Percurso compreensível, exportações rastreáveis e aceitação de acessibilidade e telas

3 Preparar operação estável

F20 a F24

Infraestrutura medida, testes antes de publicar, monitoramento e restauração documentados



Executar as mudanças em uma branch separada e repetir os cenários afetados. A arquitetura atual é suficiente para realizar essas correções. A necessidade de uma migração deve surgir de limites medidos, de requisitos novos ou de restrições comprovadas de acessibilidade, e não apenas da preferência por outra tecnologia.

O esforço deve ser estimado pela equipe depois de decidir o comportamento dos filtros e a política de cobertura. Sem essas decisões, uma promessa de prazo fechado seria pouco confiável. A estimativa precisa incluir implementação, regressão e aceitação, além do trabalho visual.

10 Critérios para declarar o produto adequado ao uso

Correção funcional e científica

Cada visualização, tabela e download usa a seleção anunciada. Diferenças intencionais de escopo ficam identificadas.

Ausência de cobertura, período parcial e ausência de registros são estados diferentes, por fonte.

Índices mantêm numerador e denominador da mesma base e período. A taxa de possíveis infratores sobre tráfego continua indisponível enquanto a incompatibilidade persistir.

Não aparecem afirmações de previsão validada, risco individual, causalidade ou equivalência entre contagens e veículos únicos.

A reconstrução ANTT continua reproduzindo os resultados de referência. Mudanças justificadas no tratamento geram nova versão e explicação das diferenças.

Compreensão por pessoas leigas

Realizar uma rodada inicial com cinco participantes que não conheçam o projeto. Pedir que encontrem um ponto de uma cidade, identifiquem o período, expliquem um índice, consultem 2026 e exportem uma comparação. Essa amostra é uma primeira verificação qualitativa, sem pretensão de representar toda a população.

Como meta proposta, ao menos quatro dos cinco devem concluir as tarefas principais sem orientação do moderador. Nenhum deve interpretar o índice como probabilidade de acidente ou a ausência de dados em 2026 como zero acidentes sem que isso provoque revisão da interface. Registrar dúvidas e erros de interpretação; não aprovar apenas porque a pessoa encontrou o botão de download.

Acessibilidade e dispositivos

Concluir navegação por teclado e teste com leitor de tela, corrigir idioma, foco e contraste e verificar as alternativas dos gráficos. Testar Chrome, Firefox e um navegador móvel representativo do público. Verificar larguras de 320, 360, 390, 768 e 1.366 pixels CSS, junto com ampliação de texto e orientações de tela pertinentes.

Desempenho e continuidade

Estabelecer metas antes da medição. Uma proposta inicial para piloto é primeira consulta útil em até cinco segundos com serviço já ativo, mudanças comuns de filtro em até dois segundos e exportações em até cinco segundos. São objetivos de produto sugeridos; não são tempos comprovados nesta auditoria.

Executar uma carga controlada com cinco e depois dez sessões simultâneas, observando tempo de resposta, memória, falhas e comportamento de reconexão. O número de sessões é um início de ensaio, não uma capacidade já garantida. Validar abertura após inatividade, implantação de uma correção e restauração da versão anterior com o mesmo pacote de dados.

11 Matriz dos testes e limites de cobertura

Cenário executado

Resultado

Abertura padrão no domínio próprio

Indicadores e ranking carregaram

Cinco áreas de navegação

Conteúdo principal carregou

Comparador com um ponto

Tabela filtrou; persistência permaneceu geral, defeito F02

Comparador sem pontos

Tabela vazia e persistência geral; orientação insuficiente

Histórico com um ponto

Curva filtrou; matriz manteve o recorte global

Histórico sem pontos

Mensagem para selecionar equipamento

Ano 2026 no contexto

Zero ANTT e PRF sem cobertura, defeito F01

Ano 2022 com todos os equipamentos

Destaque 80,47 e legenda fixa da coorte, achados F03 e F05

Criciúma no contexto de 2024 e 2025

Aviso de insuficiência de coorte; contextos locais e integrais apresentados

Recarregamento de consulta modificada

Retorno aos filtros padrão

Navegação básica por teclado

Setas alteraram a página selecionada

CSV e Markdown baixados

Conteúdo conferido com o cálculo local

PNG baixado

Imagem válida de 893 por 520 pixels

512 estados na camada de dados

Nenhuma exceção; 341 relatórios com dados e 171 estados vazios

Reconstrução dos quatro CSV ANTT

Oito Parquet e três JSON conferidos

Estilos e idioma no DOM

Contraste insuficiente nas amostras e idioma inglês

HTTPS e saúde

Respostas bem-sucedidas e redirecionamentos observados

Implantação e métricas

SHA correspondente; memória observada abaixo do limite



Continuam pendentes testes com participantes, celulares reais, múltiplos navegadores, leitores de tela, sessões simultâneas, queda de conexão, arquivo tratado corrompido em instância de teste e recuperação após falha real. Os tempos do cliente HTTP incluíram o caminho de rede da auditoria e não foram usados como medida de desempenho da interface.

A validação de identidade do commit se apoia nas respostas GitHub e Render e na comparação dos arquivos. A aplicação ainda não apresenta seu próprio identificador de build. O monitoramento consultado não substitui uma medição independente de disponibilidade ao longo de vários dias.

12 Referências e rastreabilidade

As observações de código referem-se ao SHA informado no início. As linhas indicadas localizam a implementação examinada; uma versão posterior pode deslocá-las.

Aplicação examinada.

Repositório do SENTINELA.

Painel no commit auditado.

Código de transformação ANTT, gráficos e relatórios.

Render sobre instâncias gratuitas, deploys e health checks.

Streamlit sobre cache e testes com AppTest.

WCAG 2.2 sobre contraste mínimo e reorganização do conteúdo.

O ZIP SENTINELA_bases_ANTT.zip foi a fonte local dos quatro CSV e dos dois ZIP PRF. Os manifestos foram lidos e os hashes recalculados. A identidade com os manifestos comprova integridade em relação à coleta registrada; não equivale a uma nova autenticação independente dos arquivos no portal da ANTT.

O regulamento integral do hackathon permanece fora da validação desta rodada. A adequação de produto e o atendimento às regras da competição devem ser avaliados separadamente. Os resultados desta auditoria não constituem uma declaração de conformidade com exigências que ainda não foram recuperadas.

## Links preservados do DOCX original

- https://radarsul.site/
- https://github.com/limixin1/radarsul
- https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/app_antt.py
- https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt.py
- https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt_charts.py
- https://github.com/limixin1/radarsul/blob/e5baed4fdab7575690a408f4ab492fd63790a00e/src/antt_report.py
- https://render.com/docs/free
- https://render.com/docs/deploys
- https://render.com/docs/health-checks
- https://docs.streamlit.io/develop/concepts/architecture/caching
- https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
