"""Relatório de investigação com unidades, cobertura e limites da análise."""
from src.antt import weighted_index

def report(daily,metadata,annual,possible,selection='Seleção do usuário'):
    if daily.empty:return '# SENTINELA\n\nSem registros para o filtro. Nenhum indicador calculado.'
    ids=daily.identificador.unique().tolist();years=sorted(daily.ano.unique().tolist())
    total=int(daily.passagens.sum());high=int(daily.altas.sum());idx=weighted_index(high,total)
    met=metadata.loc[metadata.identificador.isin(ids)]
    ay=annual.loc[annual.identificador.isin(ids)&annual.ano.isin(years)]
    details='\n'.join(f'| {x.identificador} | {x.ano} | {x.dias} | {100*x.cobertura_dias:.1f}% | {x.por_10_mil:.3f} |' for x in ay.itertuples())
    b=possible.loc[possible.identificador.isin(ids)&possible.ano.isin(years)]
    return f'''# SENTINELA 2.0 - Relatório preventivo

**Seleção:** {selection}. Datas publicadas: {daily.data.min():%d/%m/%Y} a {daily.data.max():%d/%m/%Y}.

**Localização:** {', '.join(sorted(met.municipio.unique()))}. Equipamentos: {', '.join(ids)}.

| Medida da base de tráfego A | Resultado |
|---|---:|
| Contagens publicadas de passagens | {total} |
| Contagens nas faixas acima de 120 km/h | {high} |
| Registros acima de 120 por 10 mil contagens publicadas | {idx:.3f} |

O cálculo usa numerador e denominador da mesma base, ponto e período. Não são veículos únicos. Ausência de faixa publicada não comprova ausência real de passagem.

## Cobertura de publicação

| Equipamento | Ano | Dias com registros | Cobertura de dias do ano | Índice por 10 mil |
|---|---:|---:|---:|---:|
{details}

Cobertura significa dias com publicação, sem comprovar disponibilidade operacional ou completude diária. 2026 é parcial. A coorte principal exige 90% dos dias em cada ano de 2024–2025. O histórico mensal oculta índices abaixo de 80%.

## Possíveis infratores, base B separada

O filtro tem {int(b.possiveis.sum())} contagens publicadas na base B em {b.data.nunique()} datas distintas. Ausência de linhas não comprova zero infrações. **Taxa B/A bloqueada:** a semântica de faixas diverge, há B maior que A e a classificação veicular de A é frequentemente ausente. Não são autuações confirmadas.

## Encaminhamentos para avaliação técnica

1. Conferir cobertura, períodos sem publicação e documentos originais.
2. Investigar persistência e alterações operacionais, sem classificar risco absoluto.
3. Consultar infraestrutura, acessos e iluminação com responsável técnico.
4. Solicitar ao publicador esclarecimento das faixas e categorias antes de calcular possíveis infratores/passagens.
5. Registrar o motivo de investigar, adiar ou descartar cada hipótese.

## Limites e fontes

120 km/h é um limiar analítico definido pelas faixas disponíveis. O cadastro de junho de 2026 é referência e não prova os limites de 2024–2025. Não se estima velocidade média por pontos médios de intervalos.

Acidentes ANTT não têm identificador único. Repetições de dia/km são preservadas. Não somar ANTT e PRF nem atribuir automaticamente acidentes a radares. O contexto espacial usa segmentos disjuntos de 5 km e os mesmos dias em que todos os equipamentos selecionados do segmento publicaram. Não demonstra causalidade ou efeito protetor da velocidade.

Fonte: quatro CSV oficiais ANTT coletados pelo usuário em 26/10/2026. URLs e SHA-256 em dados_brutos/coleta_20261026T224903Z.json. Dicionários consultados e divergências documentadas. Apoio à investigação técnica, sem previsão individual ou ordem automática de fiscalização.
'''
