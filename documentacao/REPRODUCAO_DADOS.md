# Reprodução dos dados e invariantes

O snapshot de referência não foi modificado. Os oito produtos ANTT e o produto PRF reconstruídos em `/tmp/sentinela-rebuild-312` usando Python 3.12.14 e as dependências fixadas são idênticos byte a byte aos Parquet versionados. A comparação está em `documentacao/evidencias/reproducao.json`.

## ANTT

Quatro CSV com hashes do manifesto da coleta de 26/10/2026. `src.antt` exige faixas conhecidas, quantidades inteiras não negativas e posição/sentido estáveis. Dias com chaves de faixas ambíguas são colocados em quarentena. A agregação conserva somas e os joins validam cardinalidade. Repetições de acidentes sem ID não são deduplicadas. O comando de reconstrução isolada conserva a implementação original e compara seus resultados, sem substituir referência por resultados novos.

A referência principal tem 42 equipamentos com tráfego e 20 no grupo com ≥90% dos dias em cada ano de 2024 e 2025. Total principal: 226.870.300 contagens, 57.163 acima de 120 km/h, razão ponderada 2,519633464583068 por 10 mil. VC101-9, Laguna: 6,343146230944732. Tolerância de regressão do índice: 1e-12 absoluto; reconciliação de tabelas usa atol/rtol 1e-12. Os resultados não são constantes da interface.

Em 2022, VC101-28 mantém 58/7.208 × 10.000 = 80,4661487... e três dias publicados, fora da comparação anual elegível. Em 2026, o intervalo de tráfego é 01/01–30/06 (181 dias); a proporção sobre o intervalo é distinta da proporção sobre os 365 dias. A referência de intervalo vem do inventário do CSV bruto, sem inferir início por equipamento. Ano parcial não disputa destaque anual.

## PRF

`src.prf.build_prf` verifica SHA-256 dos ZIP conforme `manifesto_prf.json`, exige um CSV por ZIP, lê `;`, Latin-1 e strings, converte campos explicitamente e preserva strings originais. Seleciona `uf=SC`, `br=101` e km inclusivo entre 244,680 e 465,100. Datas ISO devem corresponder ao ano do arquivo. Os IDs de ocorrência são únicos e obrigatórios; duplicidade provoca falha para investigação, sem remoção automática.

Originais: 73.202 linhas de 2024 e 72.529 de 2025. Trecho: 921 e 829, total 1.750; Criciúma é o valor textual `CRICIUMA`. Nenhum registro é unido a radares. Ordenação final por `data, id`, a mesma da referência, permitindo comparação byte a byte.

Campos derivados:

- `arquivo_origem`: ZIP lido; `data`: `data_inversa` validada; `ano`, `mes` (AAAA-MM), `hora` (duas primeiras posições de horário), `dia_semana_num` (segunda=0).
- `grave_ou_fatal`: mortos + feridos_graves > 0; `fatal`: mortos > 0; `vitimas_graves_fatais`: mortos + feridos_graves. São descrições dos campos publicados, sem inferência de risco.
- `problema_contagem`: alguma contagem de pessoas, mortos, feridos, ilesos, ignorados ou veículos negativa.
- `problema_soma_feridos`: feridos difere de feridos_leves + feridos_graves.
- `problema_soma_pessoas`: pessoas difere de mortos + feridos + ilesos + ignorados. Há 46 flags (23/ano), preservadas sem corrigir as contagens originais.
- `coordenada_suspeita`: coordenada ausente ou fora de latitude [-30,-27], longitude [-51,-48]. Esse envelope é verificação grosseira de plausibilidade, não validação geodésica ou localização de cada evento. Neste snapshot não há flags; os campos reconstruídos coincidem com a referência.

As demais duas flags de contagem somaram zero e IDs duplicados somaram zero no trecho. O arquivo `auditoria_prf.json` documenta contagens sem apagar ocorrências. Não deduplicar apenas por dia/km. Teste automatizado reconstrói PRF dos ZIP originais em diretório temporário e exige igualdade de valores, tipos e bytes.

## Conjunto consistente

Manifesto tratado: versão, transformação, arquivo/hash/tamanho/esquema/linhas, proveniência, períodos e notas. Validação verifica chaves, numeradores/denominadores, referências de cadastro, reconciliação diário→mensal/anual, grupo histórico e resumo. Alterar um hash para aceitar arquivo inválido não dispensa schema e reconciliação. Falha de PRF em execução é distinguida de zero; o build exige todos os produtos.

Atualizar um snapshot exige reconstrução isolada, revisão de diferenças, nova versão e troca do conjunto inteiro em release. Restaurar uma revisão conhecida com seu manifesto e validar antes de consultar; não regenerar hashes durante restauração para aceitar corrupção.
