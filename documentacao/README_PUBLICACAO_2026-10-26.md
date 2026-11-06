# Radar Sul — publicação do painel SENTINELA

Este pacote mantém o aplicativo Python/Streamlit e os mesmos indicadores do SENTINELA 2.0. O endereço pretendido é **radarsul.site**, registrado na Hostinger. Hospedagem proposta: Render, serviço Web gratuito. A identidade do aplicativo permanece SENTINELA; o domínio não altera o nome ou a análise do projeto.

**Estado:** serviço publicado no plano Free do Render, no workspace TCC 371, em [radarsul.onrender.com](https://radarsul.onrender.com). A implantação do commit `c100045fd7b5dcc5d7017758d6f8fa7f5fb985dd` foi concluída; a página inicial e `/_stcore/health` responderam com HTTP 200. A associação e a verificação de `radarsul.site` ainda estão pendentes. Nenhuma alteração de DNS foi realizada.

## 1. Enviar os arquivos para o GitHub (reprodução da instalação)

Se a publicação for conduzida pela integração Render no ChatGPT, conecte sua conta e siga o fluxo disponível. O procedimento manual abaixo também pode ser usado.

1. Entre em https://github.com e crie um repositório chamado `radarsul`. O nome é uma sugestão; a conta pode usar outro nome de repositório.
2. Extraia este ZIP. Envie o conteúdo da pasta extraída para a raiz do repositório, mantendo as subpastas.
3. Confirme que `app.py`, `requirements.txt` e `render.yaml` aparecem na raiz. As pastas `src`, `dados_tratados`, `relatorios` e `.streamlit` devem acompanhar o envio. Envie os arquivos extraídos, em vez do ZIP fechado.
4. O repositório pode ser privado. Autorize ao Render somente o acesso necessário ao repositório escolhido. O pacote contém dados administrativos públicos e não contém credenciais.

## 2. Publicar no Render (reprodução da instalação)

Entre em https://dashboard.render.com e conecte sua conta GitHub.

### Usar a configuração pronta

Crie um **Blueprint**, selecione o repositório e utilize o arquivo `render.yaml`. Confira que o serviço `radarsul` usa o plano **Free**, sem banco de dados ou disco adicional. O arquivo fixa Python 3.12, o comando de inicialização e o endpoint de saúde. Ele também declara o domínio `radarsul.site`, cuja verificação depende da etapa de DNS abaixo.

### Alternativa: criar Web Service manualmente

Selecione **New > Web Service** e o repositório. Preencha:

| Campo | Valor |
|---|---|
| Name | `radarsul` ou outro nome disponível |
| Language / Runtime | Python |
| Region | Virginia, se disponível |
| Root Directory | Vazio, quando os arquivos estiverem na raiz |
| Build Command | `python -m pip install -r requirements.txt` |
| Start Command | `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false` |
| Instance Type / Plan | **Free** |
| Health Check Path | `/_stcore/health` |
| Environment Variable | `PYTHON_VERSION` igual ao valor definido em `render.yaml` |

Crie o serviço e acompanhe os logs até a implantação concluir. Abra o endereço `onrender.com` realmente atribuído pelo Render e teste as cinco telas, Criciúma e o download do relatório. Não presuma que o nome exato `radarsul.onrender.com` estará disponível.

## 3. Conectar radarsul.site

Faça esta etapa depois de o aplicativo abrir pelo endereço do Render. Mantenha o domínio e a gestão de DNS na Hostinger.

1. No Render, abra o serviço > **Settings > Custom Domains** e adicione `radarsul.site`, se o Blueprint ainda não tiver adicionado. O Render também configura a variante `www` para redirecionamento.
2. Confira as instruções e os valores efetivamente mostrados pelo Render.
3. Na Hostinger, acesse **Domínios > radarsul.site > DNS / Nameservers**, ou a área DNS equivalente da versão atual do painel.
4. Para o domínio raiz, uma opção documentada pelo Render é:

| Tipo | Nome | Destino |
|---|---|---|
| A | `@` | `216.24.57.1` |
| CNAME | `www` | O hostname real do aplicativo, terminado em `.onrender.com` |

O IP acima consta na documentação oficial consultada em 26/10/2026. Use os valores atuais apresentados na configuração do seu serviço se houver diferença. No CNAME, informe apenas o hostname, sem `https://` ou barras.

5. Ajuste somente registros conflitantes dos nomes `@` e `www`: entradas A/AAAA/CNAME/ALIAS de estacionamento ou encaminhamento antigo podem impedir a conexão. A documentação do Render pede retirar AAAA para os nomes apontados ao serviço, pois esse apontamento utiliza IPv4. Preserve registros de e-mail (MX, SPF, DKIM e DMARC), validações e outros subdomínios. Não é necessário trocar os nameservers apenas para usar esses registros.
6. Volte ao Render e clique em **Verify**. Aguarde a propagação do DNS; a Hostinger orienta considerar até 24 horas, embora possa ocorrer antes.
7. Depois da verificação, o Render emite o certificado HTTPS. Teste `https://radarsul.site` e a variante `www`. DNS e certificado ainda precisam ser verificados na implantação real.

## Plano gratuito e apresentação

Na documentação consultada, o serviço Free aceita domínio próprio e certificado TLS gerenciado. O plano de workspace Hobby inclui dois domínios; outros domínios além da franquia podem ser cobrados. O limite de computação Free é compartilhado com os demais serviços gratuitos do workspace, incluindo 750 horas por mês. Este pacote declara explicitamente `plan: free`, sem criar banco, disco ou outro serviço pago.

O aplicativo pausa após 15 minutos sem tráfego e leva aproximadamente um minuto para reativar. Abra o endereço e confira o painel antes de iniciar a apresentação. Mantenha o HTML offline do kit completo como reserva.

O serviço Free tem 512 MB de RAM e recursos limitados. A publicação real e o uso simultâneo ainda precisam ser observados. Não se promete disponibilidade contínua ou desempenho de produção. Os dados tratados do pacote fazem parte do código implantado; o aplicativo não depende de executar downloads ou recalcular o ETL na inicialização. Mudanças locais no servidor não são armazenamento durável.

## Dados e escopo

Inclui o snapshot tratado da ANTT, o contexto PRF independente e as mesmas fontes e limitações da versão 2.0. A taxa possíveis infratores/tráfego permanece bloqueada. Os dados originais, notebook, testes completos, slides e PDF continuam no kit completo já entregue. Este pacote menor serve à hospedagem, sem substituir a entrega acadêmica ou fingir conter todos os CSV originais.

As dependências de notebook, testes e exportação de figuras foram omitidas da instalação do servidor, que usa apenas as bibliotecas necessárias ao painel. Todos os arquivos de dados necessários ao aplicativo estão incluídos.

## Fontes oficiais da configuração

- https://render.com/docs/free
- https://render.com/docs/custom-domains
- https://render.com/docs/configure-other-dns
- https://render.com/docs/python-version
- https://render.com/docs/web-services
- https://render.com/docs/blueprint-spec
- https://www.hostinger.com/support/4737652-how-to-point-a-domain-to-external-services-at-hostinger/

Consulta: 26/10/2026. Os registros de validação local e de implantação estão em `VERIFICACAO_PUBLICACAO.json`. A confirmação HTTP não substitui uma conferência visual no navegador da apresentação. Nenhuma senha, chave de API ou configuração de conta pessoal deve ser colocada no repositório.
