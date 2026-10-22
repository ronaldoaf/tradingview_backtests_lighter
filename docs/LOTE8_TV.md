# Lote 8 do TradingView: 5 estratégias (2026-10-22)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops, alvos e ordens limite resolvidos no M1 (stop antes do alvo no mesmo
minuto). Custo 0,75 bp/perna + funding 13,8% a.a. (o long paga, o short recebe). Controle: mesmo
lado e mesma duração, aberto-a-aberto (no DCA: deals iniciadas em barras sorteadas).

Código: `scripts/study_tvlote8.py` (saída `results/study_tvlote8.txt`, grades
`results/study_tvlote8_xau_grid.csv` e `results/study_tvlote8_xau_dca.csv`) e
`scripts/study_tvlote8_rob.py` (robustez, `results/study_tvlote8_rob.txt`). Fontes em `pine/`.
Triagem: o TrendMaster tem `security(..., lookahead_on)`, mas só para desenhar pivôs; não entra no
sinal. Os outros quatro não têm `security()` no sinal.

**Veredito: 5 testadas, 5 reprovadas no ouro.** Três células (BB Breakout, VWAP com banda de 2
desvios, SMA 9/21 sem os filtros do TrendMaster) passam o B&H em CAGR por 1,5–2 pontos, mas todas
perdem dinheiro no terço do meio (2021-24), ficam abaixo do B&H na segunda metade e caem abaixo
dele com custo 2×. Nenhuma foi estendida aos outros ativos.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 42 | TrendMaster Pro 2.3 (`mVkDf8qh`) | 449 | 125 | 15 | 4 | +14,8% (sem filtros) |
| 43 | Backtesting 3commas DCA Bot v2 (`8d6Auyst`) | 96 | — | 0 | 0 | +0,9% |
| 44 | VWAP Trendfollow [wbburgin] (`XoR8rQaW`) | 164 | 72 | 37 | 1 | +15,5% |
| 45 | BEST Engulfing + MA (`ROM3crig`) | 165 | 89 | 3 | 0 | +9,6% |
| 46 | Bollinger Bands Breakout (`GKgxKjlC`) | 116 | 106 | 16 | 6 | +14,9% |

B&H do ouro no período: +13,4% a.a., Sharpe diário 0,73.

---

## 42. TrendMaster Pro 2.3 (`mVkDf8qh`, Pine v6)

Cruzamento SMA 9/21 com sete filtros simultâneos (BB mais larga que 2 ATR, lado da média da BB, RSI
> 55 / < 45, MACD, Stoch, ADX > 25), stop de 1% e alvo de 2R, fechamento de tudo às 18h de NY. Os
limites de operações por sessão e de 3 stops/alvos por dia não foram reproduzidos (só cortariam
trades). Defaults: −3% a +1,6% a.a. do 5m ao 4h, t ≈ 0. Os filtros deixam a estratégia fora do
mercado 40–98% do tempo sem melhorar o trade.

Sem os filtros (um SMA 9/21 sempre no mercado com stop de 2%) o 1h chega a +14,8%, mas é ilha: 30m
e 4h ficam em +1% a +4%.

## 43. Backtesting 3commas DCA Bot v2 (`8d6Auyst`, Pine v4)

Bot de preço médio só comprado e sem stop: RSI7 < 30 abre a ordem base de 100 USD, seis ordens de
segurança limite em −1,5%, −3,9%, −7,7% ... com volume ×1,5 (total 3009 USD = o capital), alvo de
+4,5% sobre o preço médio. Simulado minuto a minuto. Grade: RSI < 20/30/sempre × alvo 1,5/4,5% ×
desvio 0,5/1,5% × stop nenhum/50%, em 15m/1h/4h/1D.

Acerto de 80–93%, como prometido, mas o retorno é **−4% a +0,9% a.a.**: o bot usa em média ~15% do
capital (o resto fica parado esperando quedas que o ouro quase não deu) e paga funding de long o
tempo todo. O gatilho de RSI não difere de abrir a deal em hora sorteada (t entre −2 e +1). É
estrutural: mesmo com custo zero o teto seria uma fração do B&H.

## 44. VWAP Trendfollow [wbburgin] (`XoR8rQaW`, Pine v5)

VWAP de sessão (virada às 17h de NY) com banda de 0,88 desvio; entra quando o close rompe a banda 1 a
favor da inclinação do VWAP, realiza ao voltar pela banda 2. Default: 700–2100 trades/ano, −2% a
−18% a.a.; o bruto (+0,4 a +1,2 bp) não paga o spread. Sem a saída na banda 2 e com banda de 2
desvios, o 1h faz +15,5%, mas os vizinhos (0,88/1,5 desvio, 30m) ficam em +5% a +11%.

## 45. BEST Engulfing + MA (`ROM3crig`, Pine v4)

Estado do último engolfo + estado do último cruzamento close × SMA32; entra quando os dois
concordam, sai quando o close anterior cruza a SMA. O stop/alvo publicado (200/2000 USD) é de BTC;
aqui virou 0,5–2% / 10×. Acerto 26–31%, quase sempre posicionado. Melhor: +9,6% a.a. 0/165 acima do
B&H.

## 46. Bollinger Bands Breakout (`GKgxKjlC`, Pine v4)

SMA55 ± 1 desvio; o último close fora da banda define a direção, sempre no mercado. É o melhor do
lote: o default no 30m faz +14,8% (Sharpe 0,82, t = +2,9) e o 1h com SMA20 +14,9%.

Robustez (as quatro células acima do B&H no lote se comportam igual):

| Célula | 2017-21 | 2021-24 | 2024-26 | 2ª metade (B&H +25%) | custo 2× | custo 4× |
|---|---|---|---|---|---|---|
| BBB 30m len55 | +16,6% (B&H 8,5%) | **−2,7%** (B&H 4,7%) | +34,2% (31,5%) | +21,5% | +11,8% | +5,9% |
| BBB 1h len20 | +17,0% | **−3,7%** | +35,2% | +21,3% | +11,2% | +4,0% |
| VWAP 1h 2σ sem TP | +18,3% | **−1,3%** | +32,6% | +18,0% | +11,2% | +3,0% |
| SMA 9/21 1h sl2% | +14,8% | **−1,4%** | +34,5% | +20,1% | +10,4% | +2,2% |

Ganham nos terços de tendência e perdem no lateral, como todo seguidor de tendência sempre posicionado;
o excesso sobre o B&H é de 1,5 ponto e some com custo 2× (o protocolo exige sobreviver a 2×).
Reprovadas.
