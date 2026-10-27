Os seletores locais do SENTINELA atualizavam tabelas enquanto mantinham radares fora da seleção nos gráficos. Esta revisão sincroniza os escopos, corrige relatórios de períodos parciais e acrescenta validação do snapshot, síntese descritiva por radar e rastreabilidade de fontes e exportações.

A regra usa quartis da referência fixa de 2024–2025. B/A continua indisponível; dados históricos, dependências e configuração Render foram preservados. Nenhum deploy foi executado.

Validação: 62 testes automatizados passaram; 13 verificações Chromium passaram, incluindo cinco telas, CSV/Markdown, localizador, controles de gráfico e viewports 320/390/768/1366 px. Integridade dos nove Parquet e referências independentes Work conferidas.

Leia VALIDACAO_SENTINELA.md para os 18 itens SEN e 26 cenários CT; PUBLICACAO_SENTINELA.md descreve a publicação posterior à autorização. Permanecem limitações de idioma/leitor de tela, teste com usuários, ampliação, originais CSV bloqueados na rede e ensaio real de produção.
