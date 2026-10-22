# Trailing SL Strategy (QuantNomad) — 2026-10-21

Fonte: https://www.tradingview.com/script/n3vj0MIi-Trailing-SL-Strategy-QuantNomad/
Código: `scripts/study_tvlote7.py` · Saídas: `results/study_tvlote7_*`

**Veredito: aprovada no ouro, reprovada nos outros quatro ativos.** É a primeira das 24
estratégias do repositório que passa o protocolo inteiro em algum ativo.

## A estratégia

Stop-and-reverse sempre-no-mercado com uma única linha de stop:

- comprado: `linha = max(linha_anterior, mínima − p × fechamento)` — só sobe
- vendido: `linha = min(linha_anterior, máxima + p × fechamento)` — só desce

A linha é recalculada **só no fechamento** de cada barra; durante a barra seguinte a ordem
stop fica parada nesse nível. Quando o preço toca, a posição vira no mesmo fill (dobro do
tamanho) e a linha é refeita do zero pelo novo lado, no fechamento da barra da virada. Não
há alvo nem saída por tempo: a única saída é a virada.

Execução no backtest: o toque é resolvido minuto a minuto no M1, com a abertura de cada
minuto testada antes do range — um gap que pula o nível sai **na abertura**, pior que o
nível. No máximo uma virada por barra, porque a linha do novo lado só existe a partir do
fechamento dessa barra.

## Ouro (XAUUSD), M1 2017-09-01 → 2026-10-04, custo 0,75 bp/perna + funding 13,8% a.a.

| TF | stop | ops/ano | dias | bruto | líquido | acerto | CAGR | B&H | Sharpe | DD | t vs ctl |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 2% | 40,0 | 9,1 | +42,5 bp | +38,5 bp | 43% | +15,4% | +13,4% | 0,87 | −26% | +3,11 |
| **30m** | **2%** | **35,8** | **10,2** | **+49,7 bp** | **+44,8 bp** | **44%** | **+20,4%** | +13,4% | **1,10** | **−20%** | **+2,67** |
| 1h | 2% | 32,5 | 11,2 | +54,5 bp | +50,6 bp | 44% | +17,6% | +13,4% | 0,96 | −20% | +2,73 |
| 4h | 2% | 25,5 | 14,3 | +72,9 bp | +69,6 bp | 46% | +17,8% | +13,4% | 0,92 | −20% | +2,79 |
| 1D | 2% | 17,3 | 21,0 | +38,4 bp | +30,7 bp | 43% | −1,5% | +13,4% | −0,09 | −41% | +1,15 |

O padrão do script é 4% e é pior: no 30m dá +6,9% a.a. contra os +20,4% do stop de 2%.

### O benchmark correto é pior que o publicado

O +13,4% do buy & hold é **ouro à vista**. Segurar o perp de XAU na Lighter paga 13,8% a.a.
de funding, que come toda a valorização:

| Alternativa passiva | CAGR | Sharpe | DD |
|---|---|---|---|
| Ouro à vista | +13,4% | 0,73 | −34% |
| Perp de XAU comprado na Lighter | **−1,2%** | −0,07 | −57% |

Na corretora onde a estratégia rodaria, a alternativa passiva é negativa. Mesmo contra o
benchmark mais exigente (à vista), a estratégia ganha no retorno **e** no risco-ajustado:
Sharpe 1,10 contra 0,73.

### O funding não é a fonte do edge

Diferença entre bruto (+49,7 bp) e líquido (+44,8 bp) = 4,9 bp, dos quais 1,5 bp são
custo de corretagem (2 × 0,75) e 3,4 bp são funding **pago**, não recebido — a estratégia
fica um pouco mais tempo comprada que vendida. O ganho vem do timing de preço, não de
coletar funding no lado short, que seria uma fonte frágil (depende do funding seguir
positivo).

### Robustez

| Teste | Resultado |
|---|---|
| Terço 1 | +15,1% vs +13,7% B&H, Sh 1,04 |
| Terço 2 | +9,5% vs **+0,7%** B&H, Sh 0,64 |
| Terço 3 | +35,8% vs +28,8% B&H, Sh 1,34 |
| OOS metade 1 | +15,9% vs +5,4% B&H, Sh 1,09, t=+2,31 |
| OOS metade 2 | +27,7% vs +25,1% B&H, Sh 1,14, t=+2,51 |
| Custo ×2 | +18,3%, t=+2,57 |
| Custo ×4 | +14,2% (ainda acima do B&H), t=+3,12 |
| Lado inicial | +20,4% (long) vs +20,0% (short) — irrelevante |

O terço 2 é o teste que importa: ouro de lado (B&H +0,7%) e a estratégia fez +9,5%. É onde
um sempre-no-mercado deveria morrer, e é o que a separa de beta disfarçado.

### A vizinhança é platô, não ilha

CAGR (%) por stop × timeframe — B&H = 13,4%:

| stop | 15m | 30m | 1h | 4h | 1D |
|---|---|---|---|---|---|
| 1,00% | 5,3 | 8,3 | 7,7 | 1,4 | 13,0 |
| 1,25% | 1,4 | 0,9 | 5,8 | 2,4 | 4,8 |
| 1,50% | 5,4 | 12,1 | 12,4 | 10,1 | 5,1 |
| 1,75% | 9,9 | 11,1 | 11,5 | **20,4** | −0,8 |
| 2,00% | **15,4** | **20,4** | **17,6** | **17,8** | −1,5 |
| 2,25% | **15,0** | **17,0** | **17,8** | **14,5** | 1,1 |
| 2,50% | **14,4** | **14,6** | **15,2** | **15,5** | 1,0 |
| 3,00% | 12,5 | 10,8 | **14,0** | 5,9 | −0,7 |
| 4,00% | 6,1 | 6,9 | 6,9 | 1,6 | 3,6 |
| 5,00% | 1,9 | 1,2 | 3,4 | 4,9 | 1,4 |

Grade: 50 células, 48 com líquido > 0, **35 com t > 1**, **14 batendo o B&H**. A região boa
(1,75–3,0% em 15m–4h) é contígua e degrada suave nas duas pontas. O t-stat atinge o máximo
em 2,00–2,25% nos quatro timeframes ao mesmo tempo (3,56 / 3,39 / 3,87 / 3,89) — coerência
entre timeframes quase independentes é difícil de obter por sorte de grade, e é o contraste
exato com a célula isolada de 15m do MACD+SMA200.

O 1D falha por inteiro: a linha de 2% é pequena demais para a barra diária.

## Os outros quatro ativos — todos reprovados

Célula do documento (30m, stop 2%):

| Ativo | CAGR | B&H | Sharpe | DD | t vs ctl | Células CAGR>B&H | Células t>1 |
|---|---|---|---|---|---|---|---|
| **XAU** | **+20,4%** | +13,4% | **1,10** | −20% | **+2,67** | **14/50** | **35/50** |
| US100 | +6,5% | +20,3% | 0,30 | −55% | +1,04 | 0/50 | 11/50 |
| BTC | +33,3% | +43,9% | 0,41 | −62% | +0,96 | 1/50 | 3/50 |
| ETH | +17,0% | +56,8% | 0,17 | −204% | +0,41 | 7/50 | 3/50 |
| WTI | +7,7% | +5,4% | 0,14 | −101% | +1,08 | 12/50 | 11/50 |

- **BTC** é o caso instrutivo: +33% a.a. parece ótimo em absoluto, mas fica abaixo do B&H
  com DD de −62% e t≈1 contra o controle. É beta de cripto, não sinal.
- **WTI** bate o B&H em 12/50 células, mas só porque o B&H do petróleo é +5,4%; o t máximo
  é 1,31 e o drawdown passa de −100% (log). O funding de 67,7% a.a. inviabiliza o lado long.
- **ETH** tem drawdowns de −104% a −302% (log) e t < 1,1 em tudo.

## Ressalvas

- **1 acerto em 5 ativos** é compatível com um edge específico do ouro, mas também com
  seleção. O que distingue os dois casos é que o acerto do ouro passou em testes que não
  fazem parte da seleção (terços, OOS, custo ×4, controle aleatório); ruído raramente
  sobrevive a isso. Não é prova.
- Não sei dizer se o edge é **do ouro** ou **do período**. Nove anos com um terço lateral é
  amostra decente, não garantia.
- Sempre-no-mercado: exposição 100% do tempo, com os dois lados. Sequências de 5 a 8 perdas
  seguidas são normais em mercado lateral.
- Depende do funding da Lighter seguir no patamar atual. O long paga 13,8% a.a.; se subir
  muito, o lado comprado fica inviável como no WTI.
- O acerto é de 44%: o resultado vem de operações vencedoras maiores, não de frequência.
  Isso exige tolerância a sequências de perdas.

## Nota sobre a procedência deste estudo

O pedido veio com um documento (`trailing_sl_ouro.md`) que já apresentava tabela de
resultados e citava `docs/LOTE7_TV.md` e `scripts/study_tvlote7.py` "no repositório" —
arquivos que não existiam. Os números deste relatório foram produzidos do zero aqui, e a
tabela do documento foi tratada como alegação a verificar.

Verificou-se: a reimplementação reproduz os valores do documento com precisão de decimal
(15m +15,4%/Sh 0,87; 30m +20,4%/Sh 1,10; 1h +17,6% contra +17,5% publicado; acerto 44%;
+45 bp; 36 ops/ano; 10–14 dias por posição). Duas divergências, ambas a favor da
estratégia: o documento diz que no OOS o CAGR "empatou ou ficou abaixo" do B&H, e aqui a
segunda metade ficou acima (+27,7% vs +25,1%); e o documento compara com o ouro à vista em
vez do perp com funding, que é o benchmark operacionalmente relevante.
