# Operação e retorno a uma versão conhecida

## Piloto publicado em 09/11/2026

O [registro da publicação](PUBLICACAO_2026-11-09.md) identifica o commit executável, o deploy ativo, o snapshot, a validação pública e as limitações desta etapa.

### Retorno ao artefato anterior

1. Em caso de regressão crítica, confirme primeiro o SHA ativo, o estado do pacote e os logs. Verifique se há deploys do mesmo commit em fila antes de operar.
2. No serviço existente `radarsul` (`srv-dbfvgi59el5s73bealsg`), workspace TCC 371, o artefato anterior de referência é `dep-dbg7476c6qcc73ei65g0`, código `e5baed4fdab7575690a408f4ab492fd63790a00e`. Confira que o Render ainda o oferece para retorno. Ele recupera o piloto anterior, com as limitações históricas registradas na matriz.
3. Use o retorno autorizado do Render para esse artefato. Confira saúde, SHA, pacote, consulta e download após o novo deploy ficar live. O retorno do artefato não reverte o Blueprint nem a main. Confira o estado do autoDeploy e registre a ocorrência antes de retomar publicações.
4. Se o artefato estiver indisponível, preserve o diagnóstico e prepare uma reversão revisada no Git. Evite novo deploy do mesmo código até entender a regressão.

## Estado confirmado em 05/11/2026 (histórico)

Em 05/11/2026 o Render MCP confirmou `radarsul`, serviço `srv-dbfvgi59el5s73bealsg`, workspace TCC 371, região Virginia, uma instância Free. A branch acompanhada é `main`, com autoDeploy por commit e previews desligados. Deploy `dep-dbg7476c6qcc73ei65g0` live no SHA `e5baed4fdab7575690a408f4ab492fd63790a00e`. O YAML configura Python 3.12.14; o ambiente real do processo remoto não foi aberto por SSH nesta rodada.

HTTPS no domínio próprio e saúde no domínio e onrender retornaram 200/ok nesta rodada. Isso verifica a versão publicada histórica. Nenhuma alteração do PR foi publicada. Os JSON de publicação na raiz são registros históricos, não a validação desta entrega. Ver `documentacao/evidencias/http-publicado.json` e a matriz.

Na janela de uma hora consultada com resolução de 600 segundos, o maior ponto de memória foi 283.910.140 bytes (~270,76 MiB), limite ~512 MiB, com instâncias distintas. Amostra esparsa não comprova pico absoluto, vazamento ou capacidade. As métricas HTTP de contagem/latência retornaram vazias, sem evidência para calcular disponibilidade ou latência.

A [documentação atual Free](https://render.com/docs/free) informa suspensão após 15 minutos sem tráfego e retomada aproximada de um minuto; não oferece a continuidade pretendida para produção. A [tabela oficial de preços](https://render.com/pricing) apresenta a alternativa 0,5 CPU/512 MB por US$7/mês, anteriormente Starter (`0.5c-512mb` na nomenclatura atual). Verificar preço, impostos e demais consumos no momento da decisão. Essa opção remove a suspensão gratuita; não aumenta a RAM nem certifica capacidade. Nenhum plano foi contratado ou alterado.

## Procedimento de publicação

1. Concluir a revisão e resolver os bloqueantes da matriz. Confirmar autorização de publicação, serviço, commit, snapshot e janela.
2. Designar responsáveis de manutenção e disponibilidade. Preparar política de proteção da main com revisão e check `validar`, sem dispensar falhas. No Render selecionar `After CI Checks Pass` em etapa administrativa autorizada; isso não foi aplicado por este PR. Não mudar público, permissões, plano ou domínio junto desta correção.
3. Guardar SHA e identidade do pacote anterior e preservar checkout de referência. Revalidar build, testes, consulta padrão, fontes 2026/parcial e arquivos exportados.
4. Incorporar somente o commit revisto quando autorizado. AutoDeploy atual por commit dispara no push/merge da main; não disparar um segundo deploy sem necessidade.
5. Acompanhar o deploy até live. Conferir versão visível, snapshot, uma consulta não padrão e download real. Saúde HTTP isolada não aprova dados.

Referências atuais: [deploys](https://render.com/docs/deploys), [health checks](https://render.com/docs/health-checks). As versões Markdown foram tentadas e o leitor web não suportou o content-type; as versões HTML foram consultadas.

## Falha e restauração

O visitante recebe aviso de indisponibilidade, sem caminhos ou stack trace. Logs técnicos identificam falha e versão; logs de consulta registram página, quantidade de pontos/anos, snapshot e duração, sem IP ou filtros pessoais adicionados pela aplicação. Logs de acesso da plataforma são independentes.

Em cópia isolada, remover/corromper um arquivo ou misturar resumo/tabela provoca rejeição. A ausência de PRF permite consulta ANTT com bloco PRF indisponível; o build exige o pacote completo. Restaurar o arquivo correto e o manifesto inteiro permite validar de novo. Chave de cache inclui hash do manifesto e estatísticas de todos os arquivos, incluindo ausência; reiniciar após substituir um conjunto é a rotina recomendada.

Em incidente de produção, restaurar um artefato conhecido do Render somente com autorização operacional. [Rollback](https://render.com/docs/rollbacks) cria outro deploy; não pressupor que reverte configurações ou serviços externos. Nesta aplicação os dados são versionados no código; verificar identidade do conjunto e configurações. Inspecionar autoDeploy depois do retorno, conferir consulta e exportação e registrar resultado. O registro de cada publicação informa se houve retorno no provedor.

## Monitoramento e ensaios

Preparado: `python -m src.data_package validate`, teste sintético `scripts/probe_session.py` e regressão AppTest. Operador deve executar o teste sintético em um ambiente autorizado após releases e em uma cadência acordada; alertar somente falhas ou mudanças relevantes. Monitor externo/alerta não foi ativado porque destino e responsável ainda não estão definidos. Não usar pings artificiais para prometer continuidade do plano Free.

Antes de certificar capacidade: medir navegador, servidor e rede separadamente; primeira consulta útil ≤5s com serviço ativo, interação comum ≤2s, exportação ≤5s são metas propostas. Repetir 5 e 10 WebSockets no ambiente de homologação, sem outros testes concorrentes; registrar percentis, memória, exceções e conteúdo. Testar reconexão e retomada após inatividade com o provedor. A carga desta entrega foi somente local; não inferir equivalência com o Render.

## Segurança e privacidade

Fluxo público de leitura, sem novos cadastros/uploads. Dados brutos públicos permanecem com proveniência. Sem segredos encontrados nos arquivos revisados; não se trata de auditoria administrativa integral. `pip-audit` consultou 62 dependências instaladas, sem vulnerabilidades conhecidas naquele instante. Parâmetros URL são validados por lista; JavaScript é constante e usa API oficial para o idioma, sem interpolar entrada externa.

Nas respostas HTTPS observadas não vieram CSP/HSTS/X-Content-Type-Options. Confirmado neste caminho HTTP, sem concluir ausência em todos os intermediários. Não foi injetada CSP sem ensaio de Streamlit, Plotly e WebSockets. Cabeçalhos do proxy e permissões administrativas demandam revisão do ambiente de entrega; acessibilidade, segurança e capacidade não estão integralmente aprovadas.
