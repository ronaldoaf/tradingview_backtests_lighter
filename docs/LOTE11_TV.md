# Lote 11 do TradingView: 5 estratégias (2026-10-22)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops e alvos resolvidos no M1 (stop antes do alvo no mesmo minuto). Custo 0,75
bp/perna + funding 13,8% a.a. (o long paga, o short recebe). Controle: mesmo lado e mesma duração.

Código: `scripts/study_tvlote11.py` (saída `results/study_tvlote11.txt`, grade
`results/study_tvlote11_xau_grid.csv`) e `scripts/study_tvlote11_rob.py` (robustez,
`results/study_tvlote11_rob.txt`). Fontes em `pine/`. Triagem: nenhum `lookahead`; os `security()`
do HA Supertrend (velas Heikin Ashi) e do Easy System (mesmo período) não vazam.

**Veredito: 5 testadas, 5 reprovadas no ouro.** Duas células passam o B&H em CAGR por menos de 1
ponto (Easy System 420 no 15m com SuperTrend largo; Strategy Code Example no 30m com stop de 0,5%).
As duas morrem com custo 2×, e o Easy System ainda perde dinheiro no terço lateral de 2021-24.
Nenhuma foi estendida.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 57 | EVWMA VWAP MACD [QuantNomad] (`ZguF6GBo`) | 95 | 42 | 8 | 0 | +11,4% |
| 58 | Strategy Code Example (`zgn9pUcQ`) | 146 | 87 | 11 | 1 | +13,5% |
| 59 | Heikin Ashi Supertrend (`9z16eauD`) | 185 | 152 | 14 | 0 | +12,8% |
| 60 | Grab Trading System (`1HAKnNRc`) | 196 | 31 | 2 | 0 | +4,8% |
| 61 | Easy System 420 (`zBaDqbla`) | 185 | 163 | 23 | 6 | +14,2% |

B&H do ouro no período: +13,4% a.a., Sharpe diário 0,73.

---

## 57. EVWMA VWAP MACD [QuantNomad] (`ZguF6GBo`, Pine v4)

diff = VWAP de sessão − EVWMA(30); "MACD" = EMA5(diff) contra EMA20(diff); cada cruzamento inverte.
Sempre no mercado. Default: −22% a.a. no 5m, +7,4% no 1h. O melhor (EVWMA 100, 30m) faz +11,4%.

## 58. Strategy Code Example (`zgn9pUcQ`, Pine v2)

Template de exemplo: EMA14 × EMA21 do open, sempre no mercado, stop de 200 e alvo de 1000 ticks (no
ouro, ~0,1% e ~0,5%); o trailing de 200 ticks sem offset não arma. Default: acerto 17–23%, de −32% a
+2% a.a. Com stop de 0,5% e alvo de 2,5% o 30m faz +13,5% (Sharpe 0,93), empatado com o B&H, mas:

| Célula | 2017-21 (B&H 8,5%) | 2021-24 (4,7%) | 2024-26 (31,5%) | 2ª metade (25,1%) | custo 2× | custo 4× |
|---|---|---|---|---|---|---|
| 30m sl 0,5% tp 2,5% | +6,9% | +3,9% | +35,8% | +25,0% | +7,7% | −3,0% |

São 350 trades/ano a +3,3 bp líquidos: o custo 2× tira 6 pontos de CAGR. Reprovada.

## 59. Heikin Ashi Supertrend (`9z16eauD`, Pine v5)

SuperTrend(10, 2,7) sobre velas Heikin Ashi; a virada inverte a posição. O alvo de 47% e o stop de 21%
(checados no fechamento) quase nunca disparam no ouro, então é um SuperTrend sempre no mercado.
Default: +1,7% (15m) a +9,5% (30m). Velas normais em vez de HA, multiplicadores 1,5/4 e stop/alvo
curtos (1%/3%) não passam de +12,8%.

## 60. Grab Trading System (`1HAKnNRc`, Pine v4)

Tendência pelo rompimento da máxima/mínima de 80 barras; dentro dela compra quando se forma um fundo de
21 barras, stop na mínima de 80, realiza no topo de 21 e fecha tudo quando a tendência vira. Acerto
52–53%, bruto entre −16 e +1 bp por trade do 5m ao 4h. Só o 1D tem algo (+4,8%, 4 trades/ano).

## 61. Easy System 420 (`zBaDqbla`, Pine v4)

Placar de 14 indicadores (PSAR ±3, SuperTrend sobre um "VPT shadow" ±3, zigzag ±1, ROC, DMI ±2, CCI,
SMA20, AO, momento, MACD ±3, Ichimoku ±2, HMA). Compra com placar > 15 e SuperTrend de alta, ou com
zigzag e SuperTrend de alta; venda no espelho; sempre no mercado. O Weis Wave (±2) e o bull/bear power
(±1) não foram reproduzidos, então o placar vai a ±22 em vez de ±25.

Default: de −0,2% a +4,4% a.a., t ≈ +2,2 no 15m–30m. Na prática o sinal é o SuperTrend: com
multiplicador 6 no 15m o placar e o zigzag quase não mudam nada (+13,7% a +14,2%). Robustez (limiar
15 sem zigzag; o limiar 10 com zigzag dá o mesmo):

| Célula | 2017-21 (B&H 8,4%) | 2021-24 (4,7%) | 2024-26 (31,4%) | 2ª metade (25,1%) | custo 2× | custo 4× |
|---|---|---|---|---|---|---|
| 15m ST×6 | +12,7% | **−1,0%** | +35,6% | +22,1% | +10,9% | +4,5% |

O mesmo seguidor de tendência sempre posicionado dos lotes 8 e 9. Reprovada.
