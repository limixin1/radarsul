# Publicação e validação independente do SENTINELA

Este documento descreve uma etapa posterior à revisão. **Não foi executado deploy nesta implementação.** Não há migração, banco ou secret novo. Não altere DNS, plano, faturamento ou configuração de produção como parte de uma verificação local.

Revisão disponível no [PR #1](https://github.com/limixin1/radarsul/pull/1), em rascunho, na branch `fix/sentinela-validacao`. O PR foi criado para revisão; não foi realizado merge ou deploy.

## Antes de publicar

1. Revisar a branch `fix/sentinela-validacao`, o diff, os commits e [VALIDACAO_SENTINELA.md](VALIDACAO_SENTINELA.md). Resolver ou aceitar explicitamente as [pendências](PENDENCIAS_SENTINELA.md), principalmente acessibilidade e limites das fontes.
2. Executar em checkout limpo a instalação, `pip check`, testes e compilação descritos no README. Iniciar o painel e verificar as cinco telas, filtros, Criciúma, estados vazios, qualidade e downloads. Guardar resultados vinculados ao commit testado.
3. Conferir que nenhum Parquet original ou hash histórico foi substituído sem revisão. Um snapshot novo exige nova reconciliação; não basta editar um hash esperado.
4. Conferir no Render qual serviço, branch, commit e política de deploy automático estão configurados. Um merge pode disparar publicação automática; **não realizar o merge antes da autorização de publicação** se esse for o caso. O arquivo `render.yaml` descreve a configuração proposta, não prova o estado atual do provedor.
5. Manter Python 3.12.14 e o comando existente de instalação. Identificador fornecido pelo Render, como `RENDER_GIT_COMMIT`, pode atestar o código implantado; não deve ser inventado nem preenchido com um commit diferente do artefato. A identificação local deve declarar alterações não commitadas, quando houver.

## Execução autorizada pelo responsável

Após aprovação específica, selecionar no serviço existente o commit revisado. Não criar outro Blueprint/serviço, contratar recursos ou trocar DNS apenas para atualizar o código. Usar os comandos de `render.yaml`:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false
```

A configuração existente declara `PYTHON_VERSION=3.12.14`, `PYTHONUNBUFFERED=1` e `OPENBLAS_NUM_THREADS=1`. São valores de runtime, não credenciais. Nenhuma chave é necessária para o snapshot local. Dados escritos no servidor não são armazenamento durável e o ETL não deve ser iniciado no serviço de apresentação.

## Critérios após a implantação

- Registrar horário, commit efetivamente implantado, identificador de snapshot, URL realmente servida e resultado da implantação.
- Verificar `/_stcore/health` (`ok`) e HTTP 200 da página. Isso só atesta conectividade básica.
- Abrir as cinco telas no navegador. Comparador de um radar não pode mostrar vinte pontos; histórico de um radar deve ter uma linha no mapa de calor. Criciúma/2026 deve identificar um radar e 181 datas observadas do snapshot atual.
- Baixar CSV e Markdown após duas seleções diferentes; conferir IDs, anos, contagens, unidade, acentos e fontes. Abrir os arquivos isoladamente.
- Conferir a regra relativa: neste snapshot, VC101-39, VC101-4, VC101-7 e VC101-9; Criciúma informa dados insuficientes para a regra. B/A permanece indisponível.
- Repetir os cenários responsivos/teclado pertinentes e registrar limitações. Não declarar conformidade WCAG ou compreensão de leigos com base no carregamento.
- Medir abertura fria/aquecida e troca de tela no ambiente real antes da apresentação; tempos locais não são SLA do Render.

Se houver regressão, usar o mecanismo do provedor para retornar ao último commit anteriormente validado, preservando as evidências do erro e a identificação do snapshot. Não modificar dados em produção para compensar falhas de código.

## Roteiro para o modo Work

Comparar a revisão recebida com o código-base auditado e ler os SEN/CT em [VALIDACAO_SENTINELA.md](VALIDACAO_SENTINELA.md). Reproduzir os números a partir do snapshot, testar controles em navegador e confrontar os downloads com a tela. Diferenciar “implementado e validado localmente”, “publicado” e “validado em produção”. A auditoria recebida está preservada em [documentacao/auditoria_work/](documentacao/auditoria_work/); seus resultados são históricos, não aprovação automática da versão corrigida.

## Histórico de domínio e provedor

`VERIFICACAO_PUBLICACAO.json` registra a implantação anterior e uma pendência de domínio daquele momento. A auditoria Work de 27/10/2026 posteriormente observou `https://radarsul.site/` servindo o painel. Isso supera a antiga pendência como observação de disponibilidade, sem comprovar titularidade, acesso ao DNS, configuração atual do provedor, identidade exata do commit de produção ou funcionamento futuro. O histórico não foi reescrito como se fosse uma nova implantação.
