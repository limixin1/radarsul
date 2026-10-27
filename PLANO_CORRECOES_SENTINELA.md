# Plano técnico de correções do SENTINELA

Referência: auditoria Work de 27/10/2026, código-base `e5baed4fdab7575690a408f4ab492fd63790a00e`. Trabalho na branch `fix/sentinela-validacao`; sem deploy, alteração de produção, migração ou troca de framework.

O inventário confirmou `app.py` → `app_antt.main()`, cinco estados de navegação Streamlit, dados Parquet locais, cálculos em `src/antt.py`, gráficos Plotly e relatório Markdown. Não existem API própria, banco, front-end separado ou atualização automática das fontes. Não havia testes na árvore de referência. As dependências de runtime permanecem fixadas em `requirements.txt`.

| Prioridade | Problema confirmado/risco | Implementação e dependências | Critério de saída |
|---|---|---|---|
| P0 | Nenhum P0 nos resultados centrais do snapshot foi reproduzido. Liberar B/A incompatível seria regressão crítica. | Preservar bloqueios de B/A, inferência causal, risco absoluto e ausência como zero. | Testes impedem indicador incompatível ou impossível. |
| P1 | SEN-001: gráficos ignoram seleção local; defeito reproduzido. | Seleção efetiva comum a tabela, figura e exportação; preservar/remover IDs ao mudar filtros globais. | CT-01/02/03. |
| P1 | SEN-002/005: rastreabilidade incompleta e contrato insuficiente para entradas novas. | Catálogo único; validação de grão, chaves, IDs, contagens, datas, hashes e reconciliação; razão entre somas. | CT-04/05/09/12/13/18. |
| P1 | SEN-004: presença de dia não comprova completude intradiária. | Evidência observável de 29/08/2025; menores volumes/mediana; sensibilidade 80/90/95%, sem excluir registros. Depende do contrato. | CT-10/11. |
| P1 | SEN-003/006: falta síntese específica e linguagem por local. | Regra relativa de Q75 nos dois anos da referência fixa; motivos, H/N, cobertura, restrições e próximos passos. Depende das seleções, fontes e qualidade. | CT-06/07/08/14; CT-15 exige participantes reais. |
| P1 | SEN-007: informação visual sem alternativa suficiente e idioma incorreto. | Tabelas nativas e resumo textual; controles nomeados. Não alterar pacote nem injetar JavaScript para simular suporte a idioma. | CT-16/17; leitor de tela e `lang` têm evidência própria, não presumida. |
| P2 | SEN-009/010/011: legendas, tempo e contexto com escopos diferentes. | Resumo dinâmico; anos parciais; datas comuns por segmento; PRF/envelope nomeados; correlação em detalhe com `n`. | CT-20/21/22/23. |
| P2 | SEN-008/012/013/016: localização, relatório, leitura e erro. | Ficha dos pontos com coordenadas publicadas; relatório autossuficiente; margem/formatação; erro recuperável sem stack trace público. | CT-08/13/19/24/25. |
| P2 | SEN-014/015: ausência de regressão e versão executada não identificada. | Testes unitários/AppTest/navegador, identificador de código e snapshot, registros de ensaio por ambiente. | CT-18/26; produção só após publicação autorizada. |
| P3 | SEN-017/018: documentação e CSV perdem contexto. | Histórico separado do estado atual; exportação tabular com período/snapshot/unidade, sem arredondar cálculo. | CT-18/24. |

A validação é por comportamento e números conhecidos, não pela presença de componentes. Os dados de teste artificiais são fixtures explícitas dos testes; não entram no produto. Os valores de referência auditados são expectativas dos testes, nunca constantes do algoritmo. [VALIDACAO_SENTINELA.md](VALIDACAO_SENTINELA.md) é o registro de conclusão; este plano não declara tarefas concluídas.
