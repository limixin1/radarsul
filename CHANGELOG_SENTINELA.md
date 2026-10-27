# Alterações do SENTINELA

## Revisão de engenharia — 27/10/2026

Base: `e5baed4fdab7575690a408f4ab492fd63790a00e`; branch `fix/sentinela-validacao`. A suíte final tem 62 testes aprovados, e o ensaio Chromium local tem 13 verificações aprovadas. Inclui testes analíticos, de contrato, relatório e AppTest. Critérios de acessibilidade/usuários/produção não concluídos permanecem explícitos. Os resultados e pendências são discriminados em [VALIDACAO_SENTINELA.md](VALIDACAO_SENTINELA.md).

### Correções e comportamento revisado

- Escopo único para tabela, persistência, histórico e mapa de calor; seleção vazia não deve conservar dados antigos nem restaurar silenciosamente novos radares.
- Resumo dinâmico de território, anos, sentidos, datas observadas e número de pontos; máximo individual separado do agregado ponderado.
- Contrato do snapshot com integridade dos Parquet, chaves ID/data, IDs/localização, datas, contagens e reconciliação entre diário, mensal, anual e resumo. Dados inválidos são recusados; não há correção silenciosa das fontes.
- Validação do índice para evitar negativos, infinitos, numerador maior que denominador e denominador inválido; cadastro essencial ausente fica explícito. É preservada a ausência legítima de referência de limites do VC101-20.
- Síntese descritiva com referência fixa da cobertura 2024–2025: índices no quartil superior nos dois anos, motivos e restrições. Não se cria score de risco nem previsão. Criciúma não ganha elegibilidade artificial.
- Qualidade de publicação separada de operação: caso de 29/08/2025 e sensibilidade a 80/90/95% dos dias, sem excluir, completar ou interpolar registros.
- Catálogo compartilhado de fontes, fórmula, coleta, período, hashes e limitações, consumido pela página e pelo relatório.
- Relatório com localização, seleção solicitada/observada, valores reproduzíveis, versão, fontes e narrativa condicionada às evidências; evidências de um dia deixam de incluir silenciosamente o ano inteiro.
- Alternativas tabulares/textuais aos gráficos, rótulos compreensíveis, formatação pt-BR e instruções de erro orientadas ao usuário.
- Exportação CSV com identidade de período/snapshot/unidade, mantendo números e precisão de cálculo.
- Testes analíticos, de contrato, relatório e interação; documentação operacional revista.

### Arquivos principais

| Área | Arquivos |
|---|---|
| Interface e figuras | `app_antt.py`, `src/antt_charts.py` |
| Contrato e cálculos | `src/antt.py`, `src/sentinel_data.py`, `src/sentinel_analysis.py` |
| Fontes e relatório | `src/sentinel_sources.py`, `src/antt_report.py` |
| Regressão | `tests/` e evidências de execução |
| Engenharia e operação | README, plano, validação, pendências e instruções de publicação |

### Decisões e limites

Streamlit, Plotly, pandas e o snapshot existente foram mantidos. A taxa B/A já estava corretamente bloqueada; essa restrição é preservada. Não foram acrescentados banco de dados, serviço externo, modelo preditivo, dados de demonstração no produto ou credenciais. Não há migração de dados nem necessidade de novas variáveis secretas.

Os CSV originais não acompanham o pacote e seu novo download foi negado pelo proxy; a reconciliação nesta sessão parte dos Parquet, não equivale ao ETL completo desde os originais. O idioma do documento e os testes com leitores de tela/participantes exigem tratamento específico, registrado nas pendências. A revisão de código não atesta a versão em produção; nenhuma publicação foi executada.

Os manifestos de publicação e a verificação do pacote anterior são preservados como históricos. Os Parquet versionados não são reescritos para fazer a validação passar.
