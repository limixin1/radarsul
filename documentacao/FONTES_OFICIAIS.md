# Fontes oficiais e proveniência

Registro de proveniência do snapshot coletado pelo usuário em 26/10/2026, com SHA-256 conferido na integração histórica. O horário do manifesto é UTC. As declarações de consulta abaixo são daquela etapa; não equivalem a uma nova coleta nesta revisão.

Neste checkout há Parquet tratados e manifesto ANTT, sem os quatro CSV originais, ZIP originais PRF ou PDFs. A nova tentativa de obter os CSV nesta implementação foi negada pelo proxy da rede (CONNECT HTTP403 para `dados.antt.gov.br`). O painel continua usando o snapshot identificado, sem anunciar atualização dos bytes oficiais. Ver [VALIDACAO_SENTINELA.md](../VALIDACAO_SENTINELA.md).

## volume-radar-viacosteira.csv

```json
{
  "arquivo": "volume-radar-viacosteira.csv",
  "url": "https://dados.antt.gov.br/dataset/269aebaa-05e7-4d76-a105-408f12bf4094/resource/2af017dc-edde-4501-9c10-ae1f0da461f6/download/volume-radar-viacosteira.csv",
  "acesso_utc": "2026-10-26T22:46:35.184423+00:00",
  "status_http": 200,
  "content_type": "text/csv",
  "bytes_resposta": 47784599,
  "sha256_resposta": "d2a0b20ba6fa0fc2dcd69a11cd87e2248982327e908e4161a3d617271372c0f0",
  "estado": "obtido",
  "bytes": 47784599,
  "sha256": "d2a0b20ba6fa0fc2dcd69a11cd87e2248982327e908e4161a3d617271372c0f0"
}
```

## quantidade-possiveis-infratores-viacosteira.csv

```json
{
  "arquivo": "quantidade-possiveis-infratores-viacosteira.csv",
  "url": "https://dados.antt.gov.br/dataset/c3844135-55c4-43b3-88a0-247f6ff9ca67/resource/121be806-df31-4ebb-aa2d-8caa5f102226/download/quantidade-possiveis-infratores-viacosteira.csv",
  "acesso_utc": "2026-10-26T22:48:01.082448+00:00",
  "status_http": 200,
  "content_type": "text/csv",
  "bytes_resposta": 24500215,
  "sha256_resposta": "3dd3b9bb37834e80fc4d94de22170aa85d7013224a5b8f56397967ede8c4aa93",
  "estado": "obtido",
  "bytes": 24500215,
  "sha256": "3dd3b9bb37834e80fc4d94de22170aa85d7013224a5b8f56397967ede8c4aa93"
}
```

## demostrativo_acidentes_viacosteira.csv

```json
{
  "arquivo": "demostrativo_acidentes_viacosteira.csv",
  "url": "https://dados.antt.gov.br/dataset/8a57b663-2302-405a-bf5a-cbece12c13d1/resource/05e0cbd2-2acb-4b81-8124-3c28a3030234/download/demostrativo_acidentes_viacosteira.csv",
  "acesso_utc": "2026-10-26T22:48:42.786818+00:00",
  "status_http": 200,
  "content_type": "text/csv",
  "bytes_resposta": 433240,
  "sha256_resposta": "a798c5ca821f8f6905102c60c5c9300da454729b6f5ef06d5cd429d684b3e00e",
  "estado": "obtido",
  "bytes": 433240,
  "sha256": "a798c5ca821f8f6905102c60c5c9300da454729b6f5ef06d5cd429d684b3e00e"
}
```

## dados-dos-radares6_2026.csv

```json
{
  "arquivo": "dados-dos-radares6_2026.csv",
  "url": "https://dados.antt.gov.br/dataset/79d287f4-f5ca-4385-a17c-f61f53831f17/resource/64044fcf-756e-4fd1-9cb2-a6037785829d/download/dados-dos-radares6_2026.csv",
  "acesso_utc": "2026-10-26T22:48:55.149473+00:00",
  "status_http": 200,
  "content_type": "text/csv",
  "bytes_resposta": 147125,
  "sha256_resposta": "a5d2b6facc9eed86a88c94bfa7870a31576db2b832daf0f664802497e60cf17d",
  "estado": "obtido",
  "bytes": 147125,
  "sha256": "a5d2b6facc9eed86a88c94bfa7870a31576db2b832daf0f664802497e60cf17d"
}
```

## Dicionários ANTT consultados

- [A — volume](https://dados.antt.gov.br/dataset/269aebaa-05e7-4d76-a105-408f12bf4094/resource/7d32f5d1-7a5d-403b-8db5-09e7e11addf1/download/dicionario_de_dados_volume_radar.pdf)
- [B — possíveis infratores](https://dados.antt.gov.br/dataset/c3844135-55c4-43b3-88a0-247f6ff9ca67/resource/d69fc6e3-c693-47b2-b1cc-aa0c05e734a9/download/dicionario_dados_surod_quantidade_possiveis_infratores.pdf)
- [C — acidentes por km](https://dados.antt.gov.br/dataset/8a57b663-2302-405a-bf5a-cbece12c13d1/resource/3d9e26ca-5d8f-4854-9744-836e8bcb088e/download/dicionario_dados_surod_acidentes_km.pdf)
- [D — cadastro](https://dados.antt.gov.br/dataset/79d287f4-f5ca-4385-a17c-f61f53831f17/resource/b10de933-f8fa-4f13-8a40-a87759b0b4c9/download/radar_dicionario_dados.pdf)

A integração histórica registrou leitura dos PDFs via consulta web. A auditoria independente de 27/10/2026 recuperou integralmente apenas o texto de A; B/C/D não foram confirmados integralmente naquela consulta. Esta implementação não refez essas leituras. Não se afirma que cópias oficiais dos quatro dicionários foram baixadas para este pacote. A divergência entre exemplos de velocidade numérica e intervalos textuais reais está documentada na auditoria.

## PRF e trecho

- [PRF — dados abertos](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf). A documentação histórica registra extrações por ocorrência de 2024 e 2025 coletadas em 23/10/2026. Neste checkout está incluído somente o Parquet tratado `dados_tratados/ocorrencias.parquet`; manifestos e ZIP originais PRF não estão presentes.
- [PRF — dicionário](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes). Referência oficial identificada; PDF não incluído neste checkout. Não se presume correspondência perfeita entre exemplos de 2017 e o formato atual.
- [ANTT — ViaCosteira](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/ccr-viacosteira/ccr-viacosteira-capa). Delimitação de referência do corredor.

## Regulamento e comparação funcional

- [Hackathon TC3S](https://profgustavozanatta.vercel.app/#/hackathon-tc3s). Sete páginas verificadas em 23/10/2026. O documento REGULAMENTO_E_CONFORMIDADE.md pertence à entrega anterior e não está presente neste checkout.
- [ANTT — painéis interativos](https://www.gov.br/antt/pt-br/assuntos/informacoes-estrategicas/paineis_interativos).
- [DNIT — sinistros de trânsito/SIOR](https://www.gov.br/dnit/pt-br/assuntos/infraestrutura-rodoviaria/sinistros-de-transito).
- [INRIX — Roadway Analytics](https://inrix.com/products/roadway-analytics/). Descrição do fornecedor, sem teste do produto.

Os três exemplos anteriores foram consultados em 23/10/2026 e demonstram que análise rodoviária já existe. Não demonstram demanda pelo SENTINELA, ausência de concorrência ou parceria institucional. Nenhuma cotação comercial foi obtida.
