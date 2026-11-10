# SENTINELA — Correção integral orientada pela auditoria de produto

Esta especificação reúne as correções do SENTINELA, uma aplicação de consulta a dados rodoviários da BR-101/SC. O trabalho abrange qualidade de dados, estatística descritiva, design, acessibilidade, testes e operação. Cada correção precisa de evidência sobre o comportamento resultante.

## 1. Contexto, materiais e versão de referência

- Repositório: https://github.com/limixin1/radarsul
- Aplicação: https://radarsul.site/
- Endereço alternativo: https://radarsul.onrender.com/
- Relatório principal: `Auditoria_Produto_SENTINELA_2026-11-02.docx`, ou sua versão Markdown de mesmo nome.
- Dados brutos: `SENTINELA_bases_ANTT.zip`.
- Serviço Render identificado na auditoria: `radarsul`, ID `srv-dbfvgi59el5s73bealsg`, no workspace anteriormente confirmado como TCC 371.
- Commit examinado em 02/11/2026: `e5baed4fdab7575690a408f4ab492fd63790a00e`.
- Implementação examinada: Python, Streamlit, pandas, NumPy, SciPy, Plotly e PyArrow.
- Arquivos principais de referência: `app.py`, `app_antt.py`, `config.py`, `src/antt.py`, `src/antt_charts.py`, `src/antt_report.py`, `.streamlit/config.toml`, `render.yaml`, `requirements.txt`, dados tratados e documentação.

Leia integralmente o relatório disponível. Revalide o estado atual do código, dos dados e da implantação: a auditoria descreve uma versão histórica. Não reverta melhorias posteriores para reproduzir a versão antiga. Localize funções pelo comportamento, pois linhas e nomes podem ter mudado.

Use arquivos e acessos já disponíveis antes de pedir materiais novamente. Se algum acesso ou anexo essencial estiver ausente, identifique exatamente qual e continue as tarefas independentes. Não invente que leu um arquivo ou executou um teste.

## 2. Objetivo do produto e limites científicos

O visitante deve conseguir localizar um ponto da rodovia, escolher um período, entender as contagens publicadas e sua cobertura, comparar pontos quando a comparação for justificável e exportar uma consulta verificável.

Preserve a definição do indicador:

`índice por 10 mil = contagens publicadas nas faixas acima de 120 km/h ÷ total de contagens publicadas da mesma base de tráfego × 10.000`.

Requisitos científicos obrigatórios:

1. Numerador e denominador devem representar a mesma base, equipamentos e período aplicável.
2. O indicador não representa probabilidade de acidente, risco individual, veículos únicos ou autuações confirmadas.
3. O limiar de 120 km/h decorre dos intervalos publicados; não deve virar afirmação de infração ao limite regulamentado de cada ponto.
4. Preserve o bloqueio da taxa de possíveis infratores dividida pelo tráfego enquanto a incompatibilidade entre as bases não estiver resolvida com evidência.
5. Não some acidentes ANTT e PRF; não associe automaticamente uma ocorrência a um radar.
6. Preserve a cautela com registros repetidos de acidentes sem identificador inequívoco. Não deduplique apenas por dia e quilômetro sem justificar o significado dos registros.
7. Correlação e persistência não demonstram causalidade nem previsão validada. Uma associação negativa não significa que velocidade proteja contra acidentes.
8. Ausência de publicação ou de uma faixa de velocidade não comprova ausência real de passagem.
9. Não calcule velocidade média por pontos médios das faixas nem reconstrua limites históricos usando apenas o cadastro de 2026.
10. Não acrescente pontuações de risco, previsões, aprendizado de máquina ou automações de fiscalização sem um novo objetivo e validação próprios.

Valores de referência do snapshot auditado, para testes de regressão:

| Medida | Referência histórica |
|---|---:|
| Equipamentos com tráfego | 42 |
| Coorte principal de 2024 e 2025 | 20 equipamentos |
| Contagens publicadas na coorte | 226.870.300 |
| Contagens acima de 120 km/h na coorte | 57.163 |
| Índice agregado da coorte | Aproximadamente 2,519633464583068 por 10 mil |
| Maior índice padrão | Aproximadamente 6,343146230944732, VC101-9, Laguna |

Não grave esses resultados como constantes da interface. O agregado deve usar a razão entre as somas, sem substituição pela média simples dos índices. Compare valores decimais com tolerância documentada. Se o snapshot ou tratamento mudar legitimamente, explique e versione as diferenças; não altere dados para fazer os testes passarem.

## 3. Método de execução e autonomia

1. Inspecione o repositório, instruções locais, alterações existentes, versão publicada e materiais da auditoria.
2. Crie uma branch de trabalho. Preserve alterações legítimas de outras pessoas. Registre código, configuração e dados usados na referência inicial.
3. Crie uma matriz F01–F24 com problema, prioridade, comportamento esperado, alteração prevista, teste e estado. Mantenha-a atualizada.
4. Implemente primeiro correções de cobertura e coerência dos filtros; depois experiência de uso e acessibilidade; em seguida operação e manutenção. Adicione a infraestrutura mínima de testes cedo, para validar as correções seguintes.
5. Preserve a arquitetura atual quando ela comportar as correções. Refatore o necessário para isolar filtros, cobertura, indicadores, apresentação e exportação. Justifique migrações ou novas dependências pelo requisito que resolvem.
6. Execute verificações proporcionais ao risco e repita os cenários afetados. Registre limitações reais de execução.
7. Prepare uma entrega revisável com código, testes, documentação e evidências. Abra PR quando o acesso permitir.

Resolva decisões rotineiras de implementação usando a auditoria e bom julgamento. Peça esclarecimento apenas quando houver ambiguidade que altere substancialmente o resultado, falta de acesso indispensável, gasto ou ação irreversível. Não repita autorizações já concedidas. Se uma tarefa bloquear, prossiga nas demais.

Não contrate serviços, altere plano pago, crie cobranças, mude público autorizado, migre domínio ou apague recursos sem autorização específica. Push e merge na branch de produção podem disparar deploy: prepare e valide primeiro. Para publicação, siga a autorização explícita existente; se ela faltar, apresente a versão pronta e faça uma única solicitação objetiva. Não trate estes requisitos de correção como autorização para novos gastos.

## 4. Correções obrigatórias F01–F24

### F01 — Cobertura por fonte e falsos zeros — P1

Modele cobertura separadamente das contagens. Diferencie fonte indisponível, fonte sem cobertura do período, cobertura parcial, consulta sem registros e zero observado em dados cobertos. Use metadados de cobertura e proveniência; a primeira e a última ocorrência, isoladamente, não comprovam completude de uma fonte de acidentes.

No snapshot auditado, acidentes ANTT terminam em 31/12/2025 e PRF contém somente 2024 e 2025. Em 2026, mostre indisponibilidade de dados de acidentes. Em 2022 e 2023, não apresente zero PRF. Para 2025 junto com 2026, informe os anos solicitados e os efetivamente cobertos por cada fonte. Preserve no filtro os anos pedidos; não omita silenciosamente os anos sem dados. Trate também o caso de arquivo PRF ausente, sem simplesmente esconder o bloco.

**Aceite:** consultas sem cobertura não exibem zero como resultado factual; seleções mistas identificam cobertura parcial junto ao valor e na exportação.

### F02 — Consistência entre seleção e gráficos — P1

Faça tabela, série, matriz mensal, gráficos, resumos e exportações respeitarem a seleção anunciada. Corrija a divergência entre `chosen` e `ids` no comparador e no histórico. Uma seleção local não pode deixar um gráfico de outra população sem identificação explícita.

Com um equipamento, mostre apenas esse ponto nos componentes pertinentes e explique por que uma correlação entre pontos não está disponível. Com nenhum, mostre orientação e bloqueie comparações e exportações vazias. Trate correlação indefinida por falta de variabilidade, sem exibir `NaN` como resultado útil. Se mantiver um panorama geral, apresente-o como componente separado, com sua própria população identificada.

### F03 — Cobertura e elegibilidade do ranking — P1

Mostre dias publicados e cobertura por equipamento e ano junto aos resultados. Preserve o grupo comparável de 2024 e 2025 como referência histórica. A elegibilidade desse grupo não garante cobertura adequada em outros anos.

Defina e documente a política de comparação para cada período selecionado. Em anos parciais, diferencie cobertura do calendário anual de cobertura do intervalo oficialmente disponibilizado; não derive esse intervalo apenas da primeira publicação de cada equipamento. Separe comparações elegíveis de consultas exploratórias com dados insuficientes.

Caso obrigatório: VC101-28, Içara, em 2022, tem índice aproximadamente 80,47 por 10 mil, com 58 contagens altas, 7.208 totais e três dias publicados. O valor deve continuar correto, acompanhado da insuficiência de cobertura. Não o apresente como destaque comparável a um ano completo. Se nenhum ponto for elegível, explique a situação em vez de selecionar um vencedor.

### F04 — Contraste e legibilidade — P1

Corrija as legendas com opacidade reduzida e contraste insuficiente. Na auditoria, textos de 14 px tiveram aproximadamente 4,02:1 no fundo principal e 3,91:1 na lateral. Verifique as cores efetivamente compostas, considerando opacidade e fundos.

Use as referências WCAG pertinentes, verificando sua documentação oficial. Para texto comum, adote contraste mínimo de 4,5:1; para texto grande e componentes, aplique os critérios correspondentes. Inclua legendas, notas, eixos, avisos, controles e foco. Não dependa apenas de cor para comunicar estado ou cobertura.

### F05 — Legendas dinâmicas — P2

Substitua a frase fixa sobre 20 de 42 equipamentos por informações correspondentes ao filtro ativo. Mostre quantidade de pontos, área, sentidos, anos e regra aplicada. Preserve a descrição da coorte original nos detalhes metodológicos. A legenda precisa continuar correta ao escolher todos os pontos, uma cidade, o entorno ou um único sentido.

### F06 — Linguagem compreensível — P2

Revise navegação, campos, ajuda e tabelas para português brasileiro. Explique coorte, persistência e Spearman no contexto da tarefa. Troque nomes internos como `por_10_mil`, `altas` e `passagens` por rótulos com significado e unidade. Mantenha detalhes técnicos acessíveis, sem exigir sua leitura para uma consulta básica. Não chame contagens de pessoas ou veículos únicos.

### F07 — Localização dos equipamentos — P2

Inclua busca por cidade e equipamento e apresente opções com município, rodovia, quilômetro, sentido e código. Explique crescente e decrescente em relação à quilometragem. Não invente orientação geográfica ou referências físicas.

O visitante deve encontrar Laguna no km 304 e o ponto de Criciúma sem conhecer códigos. Um mapa é complementar: implemente-o somente se houver coordenadas verificáveis e uma alternativa acessível, após resolver a busca e os rótulos.

### F08 — Abertura e hierarquia da informação — P2

Faça a primeira tela explicar o serviço, a área e o período ativos e o próximo passo para consultar um local. Na apresentação do resultado, priorize local, indicador, cobertura e significado. Identifique claramente se um valor é agregado da seleção ou máximo entre equipamentos elegíveis.

Remova títulos redundantes. Informe quando o ranking mostra apenas os primeiros 12 pontos e ofereça acesso à lista completa. Preserve uma aparência coerente com o tema, sem transformar avisos metodológicos em textos ilegíveis ou escondê-los para deixar a página visualmente mais limpa.

### F09 — Formatação de números — P2

Padronize a apresentação em pt-BR: vírgula decimal, separador de milhar e unidades explícitas, com precisão adequada à leitura. Evite que `2.520` seja interpretado como 2.520 unidades quando o resultado pretendido é 2,520 por 10 mil.

Preserve precisão numérica interna e em exportações técnicas documentadas. Ofereça CSV adequado a planilhas brasileiras e interoperabilidade quando necessário. Teste exportação e reimportação para evitar perda de valores, caracteres ou separadores.

### F10 — Estados vazios e recuperação — P2

Trate ausência de anos, sentidos ou equipamentos; combinações sem dados; denominador zero; fonte ausente; cobertura insuficiente e seleção inválida. Explique a causa e ofereça ação para corrigir o filtro ou restaurar o padrão.

No comparador vazio, não mantenha um gráfico geral que pareça resultado da seleção. Desabilite downloads sem conteúdo útil. Diferencie erro operacional de consulta válida sem resultados. Uma mensagem genérica para todos os casos é insuficiente.

### F11 — Persistência e compartilhamento — P2

Preserve estado ao navegar e recarregar. Sincronize filtros relevantes com parâmetros de URL validados, incluindo página, período, área, sentidos e seleção suportada. A URL deve reproduzir a consulta em uma nova sessão.

Trate parâmetros desconhecidos, repetidos, antigos, vazios ou incompatíveis com o snapshot. Informe ajustes necessários, evitando mudanças silenciosas da população. Inclua restauração explícita do padrão e teste que o estado de um visitante não seja aplicado a outro por cache global.

### F12 — Idioma e acesso sem mouse — P2

Corrija a declaração de idioma para pt-BR usando mecanismo suportado. Localize controles quando a biblioteca permitir. Verifique teclado, foco visível, ordem de navegação, nomes acessíveis e comunicação de atualizações dos filtros.

Disponibilize resumo textual e alternativa tabular para cada gráfico, sem depender de hover. Se houver limitação da versão do framework, investigue a solução documentada, teste alternativas e registre a limitação residual. Não declare conformidade integral com base apenas em verificação automática ou acesso por teclado a um controle.

### F13 — Espaçamento e responsividade — P2

Corrija o texto parcialmente encoberto no topo, considerando o cabeçalho do Streamlit. Ajuste títulos, notas, margens, tabelas e gráficos para diferentes larguras.

Verifique 320, 360, 390, 768 e aproximadamente 1.366 px CSS; ampliação de 200% e reorganização de conteúdo em largura equivalente a 320 px. Evite rolagem horizontal em textos e controles comuns; avalie separadamente elementos que exigem apresentação bidimensional. Diferencie teste de viewport de teste em celular real. Registre navegador, largura e cenário efetivamente examinados.

### F14 — Tratamento de erros e restauração — P2

Remova a instrução de executar `python analisar.py`, inexistente no commit auditado. Valide o comando realmente disponível de reconstrução, historicamente `python -m src.antt`, com seus arquivos necessários.

Mostre ao visitante uma mensagem útil de indisponibilidade e registre detalhes técnicos no servidor, evitando exposição de caminhos, credenciais ou stack traces. Simule arquivo ausente ou corrompido em ambiente isolado e verifique o procedimento de restauração.

### F15 — Contrato e versionamento do pacote de dados — P2

Crie manifesto do pacote tratado com versão, proveniência, hashes, arquivos, esquemas, períodos, cobertura declarada e compatibilidade com a transformação. Valide coerência entre tabelas e resumo e rejeite pacotes incompletos ou misturados.

Publique dados como conjunto consistente, com falha segura e restauração. Preserve snapshots de referência. Inclua validação no build e teste de consulta após implantação. Não trate a resposta `ok` do health check do servidor como prova de integridade analítica.

### F16 — Reprodução dos dados PRF — P2

Implemente ou recupere o procedimento que transforma os ZIP PRF em `ocorrencias.parquet`. Documente filtros de rodovia, UF, quilometragem, datas, esquema, coordenadas, contagens, duplicidades e campos derivados.

Reproduza em ambiente limpo, compare com o snapshot auditado e explique diferenças. Não suponha o significado de um campo derivado sem investigar sua definição. A auditoria reproduziu oito produtos ANTT; isso não validou automaticamente toda a cadeia PRF.

### F17 — Fontes e materiais verificáveis — P2

Ofereça fontes com links específicos dos recursos, datas de coleta e atualização, períodos de cada base, manifesto baixável e condições de reutilização verificadas. Diferencie download efetivamente disponível, link externo e material restrito ao kit de reprodução.

Remova a afirmação de que arquivos acompanham um pacote quando eles não estão acessíveis naquele pacote. Identifique dados históricos e parciais; data recente de coleta não significa monitoramento em tempo real.

### F18 — Exportações com contexto completo — P2

Preserve CSV, Markdown e PNG que já funcionam e acrescente o contexto necessário: filtros solicitados e efetivos, equipamentos, área, sentidos, unidade, cobertura, fontes, coleta, geração e versões do código e dos dados.

Use nomes de arquivo que distingam consultas e links que funcionem fora da sessão. Se o formato exigir, ofereça metadados em arquivo complementar ou pacote, sem quebrar a leitura do CSV. Imagem de gráfico deve incluir título, período, unidade e fonte. Acrescente impressão ou PDF se houver solução simples, verificável e útil, depois de corrigir conteúdo e rastreabilidade.

### F19 — Escopos espaciais explícitos — P2

Distinga os segmentos da análise principal, o envelope ANTT entre pontos e o contexto PRF do trecho integral. Mostre área, datas, unidade, cobertura e população perto de cada valor. Explique por que Criciúma pode aparecer na consulta local e ficar fora da coorte principal.

Preserve segmentos disjuntos e o alinhamento de dias de publicação entre pontos quando esse método for aplicado. Não multiplique ocorrências ao juntar radares e segmentos. Qualquer mudança metodológica deve ter justificativa, teste e comparação com a referência.

### F20 — Disponibilidade e capacidade — P1 para operação contínua

Revalide configuração, limites e documentação atual da hospedagem. A auditoria observou instância gratuita, suspensão por inatividade como limitação da plataforma e pico amostrado de aproximadamente 379 MiB frente a 512 MiB; esses números são históricos e não comprovam vazamento nem capacidade simultânea.

Meça primeira abertura, retomada após inatividade, reconexão e consultas comuns. Teste cinco e depois dez sessões simultâneas em ambiente adequado e com carga controlada. Não realize carga agressiva em produção nem contrate plano sem autorização. Se a disponibilidade pretendida exigir gasto, entregue opção concreta com custo atual verificado e deixe a decisão explícita.

### F21 — Testes automatizados e publicação controlada — P1

Adicione testes de regressão dos problemas encontrados, contratos de dados, geração de relatórios e comportamento das cinco páginas, usando recursos oficiais adequados, como AppTest quando compatível. Integre verificações à CI e registre a versão de demonstração.

Prepare proteção da branch e publicação condicionada às verificações, conforme permissões disponíveis. Não rebaixe verificações para obter uma aprovação aparente. Exiba versão do código e snapshot na interface, com detalhes técnicos em local apropriado. Confirme o que ficou apenas configurado no repositório e o que foi efetivamente ativado no provedor.

### F22 — Cache desempenho e monitoramento — P2

Meça gargalos antes de refatorar. Evite leituras e cálculos repetidos sem necessidade, incluindo PRF, e use a versão dos dados para invalidar cache. Preserve isolamento por sessão e evite compartilhar objetos mutáveis que possam contaminar consultas.

Registre falhas e tempos úteis sem coletar dados pessoais desnecessários. Prepare monitoramento de disponibilidade e teste sintético de consulta com responsabilidade definida. Séries de métricas vazias significam falta de evidência, não latência zero ou ausência absoluta de falhas.

### F23 — Segurança proporcional ao serviço — P2

Revise dependências, segredos, permissões administrativas disponíveis, HTTPS, tratamento de erros e entradas por URL. Confirme cabeçalhos no caminho real de entrega antes de diagnosticar sua ausência. Teste qualquer mudança de CSP ou outros cabeçalhos com Streamlit, Plotly e WebSockets.

Corrija vulnerabilidades efetivamente identificadas com ferramentas e fontes adequadas e verifique regressões. Preserve o fluxo público de leitura; introduza contas somente diante de requisito específico. Não enfraqueça proteções nem trate um scanner isolado como certificação de segurança.

### F24 — Documentação operacional e responsabilidade — P2

Atualize README, registros de publicação, estrutura de arquivos e instruções de instalação, reconstrução e manutenção. Preserve o histórico, identificando o estado atual com data e evidência. Registre origem das bases, versão, pendências PRF, comandos reais, recuperação e rollback.

Documente quem responde pela atualização e por falhas usando informações conhecidas, sem inventar responsáveis ou contatos. Prepare um canal de relato de problema adequado. Outra pessoa deve conseguir operar e restaurar o projeto usando a documentação.

## 5. Testes obrigatórios de aceitação

Crie uma matriz que relacione cenário, resultado esperado, resultado observado, ambiente, evidência e F01–F24 correspondente. Cubra, no mínimo:

1. Abertura padrão de 2024 e 2025 e percurso pelas cinco páginas.
2. 2026 isolado: indisponibilidade correta de acidentes ANTT e PRF.
3. 2022 e 2023: indisponibilidade PRF; dados das demais fontes conforme suas coberturas.
4. 2025 junto com 2026: cobertura parcial explícita por fonte, inclusive na exportação.
5. Um equipamento, vários e nenhum no comparador; correspondência entre tabela, gráfico e arquivo.
6. Um equipamento, vários e nenhum no histórico; correspondência entre série e matriz mensal.
7. VC101-28 em 2022: índice correto e três dias de cobertura claramente identificados.
8. Todos os equipamentos, coorte, Criciúma e entorno, com um e com ambos os sentidos.
9. Ausência de anos ou sentidos e combinações que produzam consulta vazia.
10. Denominador zero, índice ausente, correlação indefinida e equipamento sem dados no período.
11. URL compartilhada em nova sessão; reload; troca de página; parâmetros inválidos; isolamento entre visitantes.
12. CSV, relatório e PNG: download, conteúdo, unidade, filtros, cobertura, metadados e caracteres portugueses.
13. Pacote incompleto, arquivo corrompido, esquema incompatível e resumo de outra versão, em ambiente isolado.
14. Reconstrução ANTT a partir dos quatro CSV e reconstrução PRF a partir de seus arquivos originais.
15. Legendas dinâmicas, contraste, foco, teclado e alternativas dos gráficos.
16. Larguras previstas, ampliação, Chrome, Firefox e navegador móvel quando disponíveis.
17. Serviço ativo, retomada, reconexão, carga controlada e procedimento de restauração.

Reaplique a matriz histórica de 512 combinações na camada de dados, ajustando-a de forma documentada se os filtros evoluírem. Ela correspondia a 32 subconjuntos de cinco anos, quatro recortes e quatro subconjuntos de sentidos. Isso não substitui testes de interface ou concorrência.

Execute regressões que verifiquem resultados esperados e falhas reais, sem escrever testes que apenas repitam a implementação. Inclua conservação das somas, unicidade de chaves e prevenção da multiplicação de registros em joins.

Metas iniciais propostas para um piloto, a validar no ambiente escolhido:

- Primeira consulta útil em até cinco segundos com serviço ativo.
- Interações comuns em até dois segundos.
- Exportações em até cinco segundos.

Defina como os tempos serão medidos, informe tamanho da amostra, condições e resultados. Não confunda download do HTML, tempo do servidor e renderização completa. Se as metas falharem, explique o gargalo e o que foi corrigido ou continua pendente.

## 6. Validação com pessoas leigas

Prepare e, se houver participantes reais disponíveis, execute uma rodada qualitativa com cinco pessoas que não conheçam o projeto. Peça que localizem uma cidade, expliquem o índice e a cobertura, consultem 2026 e exportem uma comparação.

Como critério inicial, busque quatro de cinco participantes concluindo tarefas principais sem ajuda. Qualquer interpretação do índice como probabilidade de acidente, ou da falta de cobertura como zero acidentes, deve provocar revisão da interface.

Não simule participantes para declarar esse critério aprovado. Sem pessoas reais, entregue roteiro, formulário de observação e estado pendente. Da mesma forma, distinga testes automáticos de acessibilidade, uso efetivo de leitor de tela, emulação de viewport e teste em aparelho real.

## 7. Entrega e publicação

Entregue:

1. Código corrigido, organizado em mudanças revisáveis, com branch, commits e PR quando disponível.
2. Matriz F01–F24 atualizada, com estados como corrigido e testado, implementado com teste pendente, bloqueado ou não aplicável com justificativa.
3. Testes automatizados e resultados de execução; evidências visuais de desktop e telas estreitas quando esses testes forem possíveis.
4. Comparação dos resultados analíticos antes e depois, com explicação de qualquer diferença.
5. Documentação operacional, fontes, versões e procedimentos de reprodução e restauração.
6. Pendências reais de pessoas, aparelhos, acessos, infraestrutura ou regulamento, acompanhadas do que falta para concluí-las.

Antes de publicar, confirme a autorização, a identidade do serviço, o commit, o pacote de dados, os testes e o procedimento de retorno. Reutilize autorizações já concedidas. Com deploy automático ativo, evite um segundo disparo desnecessário após o push. Acompanhe a implantação até estado final e confira a aplicação publicada, seus filtros e uma exportação.

Se a publicação depender de acesso, aprovação ou custo ainda não disponível, entregue a versão corrigida e testada, pronta para esse passo. Não deixe a implementação por fazer à espera da aprovação de produção.

O regulamento do hackathon deve ser verificado quando estiver disponível. Sua ausência não deve paralisar correções independentes nem justificar declaração de conformidade com regras desconhecidas.

No relatório de entrega, registre as alterações, o estado dos requisitos F01–F24, os testes executados, a versão entregue ou publicada e os bloqueios restantes. Separe implementação de validação. Não declare o sistema completamente aprovado enquanto critérios relevantes permanecerem sem teste.
