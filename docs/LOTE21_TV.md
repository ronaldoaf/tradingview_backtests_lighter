# Lote 21 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote21.py` (grade) e `scripts/study_tvlote21_rob.py` (robustez). Resultados: `results/study_tvlote21_{ativo}.txt`, `_grid.csv` e `results/study_tvlote21_rob_{ativo}.txt`.

**Puladas na ordem da lista (18):**
- **Olham o futuro:** ANN 2 signals (`G37UDeXt`) e Mirocana (`We6vmIza`), ambos com `security` em Pine v2.
- **Velas Renko via `security`, irreal:** [SMT] Renko (`FJLcATq9`).
- **Templates, exemplos ou ferramentas:** MACD 5 iN 1 (`TtLghbTF`, as 5 estratégias vêm desligadas), Risk to Reward Backtester (`uWMQ0vwN`), Kelly ratio (`bFXf4IXh`), Take profit Multi timeframe (`9lzBKqhc`) e PineCoders FAQ (`q9laJNG9`).
- **Página 404:** `syRkfqhT` e `ZsKsLiUU`.
- **Duplicada:** ABCD com trailing (`HkuqtyQ7`, a mesma ABCD do lote 19).
- **Complexas demais para reproduzir com fidelidade:** Quasimodo (`7WpyJVvp`), Gold Breakout WillyAlgoTrader (`HnelYN0A`, 1.006 linhas), PPO Divergence (`0ua1XvYk`), Double/Triple Pattern (`ykzrcWQf`), Order Block FVG (`PjH7wg3n`) e Fancy Bollinger Bands (`29lNzU30`).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 134 | Trend Surfers - Premium Breakout | `w91kwvnX` | rompimento de 168 barras; stop fixo 2 ATR10 e trailing 8 ATR10 no fechamento; inverte |
| 135 | Squeeze Momentum Strategy v2 | `lEQZl0vE` | momentum do squeeze virando abaixo de 0 com squeeze desligado (lógica 2); SL 0,5%, TP 1% |
| 136 | Moving Average Consecutive Up/Down (ChartArt) | `7KXy9NNJ` | 4 closes seguidos subindo compra, caindo vende; inverte |
| 137 | RSI Trend Crypto | `Ru7qOVtp` | long-only; RSI14 cruza acima de 35 compra, abaixo de 75 vende |
| 138 | Hulk Scalper x35 | `oGUYuz4N` | pullback do MACD (limiar em ATR em vez de ticks) com EMA50/200, ADX > 33, RSI20 ≈ 50; TP 1,35%, SL 1,1% |
| 139 | SuperTREX strategy | `K3U9opwQ` | RSI14 do close da 1ª barra de cada semana cruzando 35 ancora um SuperTrend 10×4; cruzamento compra/vende |
| 140 | ATR Strategy Back-test | `DW1GWSWQ` | trailing ATR5 × 3,5 (família UT Bot); inverte |
| 141 | BB+AO STRAT | `ibq1TYLX` | long-only; EMA2 cruza a SMA5 com AO a favor |
| 142 | Gold-Silver 30m Only | `lx4O1PPu` | como escrito: RSI14 + EMA162; o exit sem preço nunca fecha, só a entrada contrária |
| 143 | MACD + BB + RSI [Alorse] | `6xo9yMmT` | long-only; MACD cruza com RSI < 50 abaixo da média; sai com RSI > 70 acima da banda |
| 144 | Bollinger Bands - Breakout | `sTFw2fOj` | rompimento da BB15 com filtro de volatilidade; SL 2%, TP 9% (trailing omitido) |
| 145 | 5min MACD scalp by Joel | `qN11DuKy` | pico do histograma a favor da tendência EMA50/200; TP 0,5%, SL 0,4% |
| 146 | Liquidity Sweep Filter [AlgoAlpha] | `gx7267BR` | só a tendência (SMA da EMA12 ± 2 × desvio EMA36); níveis de liquidez só desenham |
| 147 | Renko Strategy Open_Close | `e6mDSPPe` | modo Pro (velas normais): reversão de 2 velas, alvo e stop = tamanho da vela |
| 148 | Keltner bounce from border | `mQKGzLMD` | SMA200 ± 8 ATR200; volta para dentro inverte |
| 149 | LUBE | `i9tJOtjl` | atrito (quantas velas contêm o close) baixo + FIR; fecha com atrito alto |
| 150 | RSI Binary Strategy | `1jTE6hJz` | RSI6 < 13 compra, > 82 vende; fecha em 3 barras |
| 151 | MACD + Stochastic + RSI | `2BIMZDGk` | long-only; MACD > sinal, %K > 50, RSI > 50; sai com MACD < sinal |
| 152 | Super Guppy Strategy | `vPStjyWz` | fita lenta de EMAs 24-66; sinais antecipados; inverte |
| 153 | Multi Timeframe RSI [TradeDots] | `kfj6EdjQ` | RSI14 em 3 tempos (1×, 3×, 6×) todos < 30 compra, > 70 vende |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Trend Surfers Breakout | BTC | 43 | 24 | 9 | 6 | +48.1% (15min p168 t8 f2 ambos, 1271 tr) | +43.8% |
| Trend Surfers Breakout | ETH | 43 | 25 | 7 | 12 | +100.2% (4h p55 t8.0 f2.0 ambos, 159 tr) | +56.8% |
| Trend Surfers Breakout | US100 | 45 | 18 | 0 | 0 | +10.0% (4h p55 t8.0 f2.0 long, 71 tr) | +20.3% |
| Trend Surfers Breakout | WTI | 43 | 4 | 0 | 0 | +1.8% (30min p55 t4.0 f0.0 ambos, 4677 tr) | +5.4% |
| Trend Surfers Breakout | XAU | 43 | 23 | 0 | 0 | +5.0% (1h p55 t8.0 f2.0 ambos, 558 tr) | +13.4% |
| Squeeze Momentum | BTC | 85 | 27 | 2 | 2 | +49.2% (15min l2 sl0.0% tp0% semsqz ambos, 11447 tr) | +43.8% |
| Squeeze Momentum | ETH | 85 | 32 | 4 | 3 | +95.3% (1h l1 sl0.0% tp0% semsqz ambos, 7068 tr) | +56.8% |
| Squeeze Momentum | US100 | 85 | 33 | 4 | 0 | +9.7% (4h l2 sl0.0% tp0% semsqz long, 277 tr) | +20.3% |
| Squeeze Momentum | WTI | 85 | 14 | 0 | 11 | +15.5% (4h l1 sl0.5% tp1% semsqz ambos, 1771 tr) | +5.4% |
| Squeeze Momentum | XAU | 85 | 17 | 0 | 0 | +5.2% (1D l1 sl0.5% tp1% semsqz ambos, 276 tr) | +13.4% |
| MA Consecutive Up/Down | BTC | 37 | 34 | 2 | 7 | +77.4% (30min n4 ma1 ambos, 3302 tr) | +43.8% |
| MA Consecutive Up/Down | ETH | 37 | 35 | 4 | 11 | +133.9% (4h n4 ma1 ambos, 385 tr) | +56.8% |
| MA Consecutive Up/Down | US100 | 38 | 32 | 2 | 0 | +14.2% (30min n8 ma20 long, 970 tr) | +20.3% |
| MA Consecutive Up/Down | WTI | 38 | 10 | 0 | 9 | +30.8% (4h n8 ma1 ambos, 26 tr) | +5.4% |
| MA Consecutive Up/Down | XAU | 37 | 28 | 1 | 0 | +9.6% (1h n8 ma20 ambos, 988 tr) | +13.4% |
| RSI Trend Crypto | BTC | 18 | 16 | 0 | 0 | +16.1% (30min 40/80, 212 tr) | +43.8% |
| RSI Trend Crypto | ETH | 17 | 11 | 0 | 0 | +26.4% (4h 40/80, 40 tr) | +56.8% |
| RSI Trend Crypto | US100 | 16 | 15 | 0 | 0 | +12.9% (4h 40/80, 32 tr) | +20.3% |
| RSI Trend Crypto | WTI | 18 | 0 | 0 | 0 | -2.8% (1h 25/65, 198 tr) | +5.4% |
| RSI Trend Crypto | XAU | 17 | 5 | 0 | 0 | +2.3% (1D 35/75, 10 tr) | +13.4% |
| Hulk Scalper | BTC | 68 | 51 | 8 | 0 | +20.2% (15min thr0.1 adx25 tp1.35% sl1.1% ambos, 1972 tr) | +43.8% |
| Hulk Scalper | ETH | 68 | 60 | 3 | 0 | +35.7% (15min thr0.3 adx25 tp3.00% sl2.0% ambos, 933 tr) | +56.8% |
| Hulk Scalper | US100 | 68 | 54 | 0 | 0 | +9.1% (15min thr0.1 adx25 tp3.00% sl2.0% long, 261 tr) | +20.3% |
| Hulk Scalper | WTI | 68 | 26 | 1 | 1 | +7.6% (30min thr0.1 adx33 tp3.00% sl2.0% ambos, 269 tr) | +5.4% |
| Hulk Scalper | XAU | 68 | 46 | 0 | 0 | +10.1% (15min thr0.1 adx25 tp3.00% sl2.0% ambos, 280 tr) | +13.4% |
| SuperTREX | BTC | 28 | 26 | 11 | 18 | +83.4% (1h m4 ambos, 231 tr) | +43.8% |
| SuperTREX | ETH | 27 | 27 | 0 | 0 | +52.8% (15min m2 ambos, 745 tr) | +56.8% |
| SuperTREX | US100 | 27 | 23 | 0 | 0 | +9.3% (15min m2 long, 495 tr) | +20.3% |
| SuperTREX | WTI | 29 | 1 | 0 | 0 | -0.1% (4h m8 ambos, 49 tr) | +5.4% |
| SuperTREX | XAU | 27 | 20 | 0 | 0 | +3.5% (1D m2 ambos, 25 tr) | +13.4% |
| ATR Strategy | BTC | 30 | 27 | 3 | 2 | +61.0% (4h a14 m5 ambos, 144 tr) | +43.8% |
| ATR Strategy | ETH | 30 | 30 | 3 | 6 | +94.3% (4h a14 m5 ambos, 138 tr) | +56.8% |
| ATR Strategy | US100 | 30 | 24 | 4 | 0 | +13.3% (30min a5 m3.5 long, 1159 tr) | +20.3% |
| ATR Strategy | WTI | 30 | 10 | 0 | 5 | +18.5% (1D a5 m3.5 ambos, 48 tr) | +5.4% |
| ATR Strategy | XAU | 30 | 24 | 3 | 0 | +12.9% (30min a5 m3.5 ambos, 1947 tr) | +13.4% |
| BB + AO | BTC | 10 | 8 | 0 | 0 | +23.1% (1D bb20, 51 tr) | +43.8% |
| BB + AO | ETH | 10 | 9 | 0 | 0 | +54.9% (4h bb20, 346 tr) | +56.8% |
| BB + AO | US100 | 10 | 10 | 0 | 0 | +7.5% (1D bb20, 40 tr) | +20.3% |
| BB + AO | WTI | 10 | 0 | 0 | 0 | -22.6% (1h bb20, 1266 tr) | +5.4% |
| BB + AO | XAU | 10 | 4 | 0 | 0 | +4.6% (4h bb20, 267 tr) | +13.4% |
| Gold/Silver RSI+EMA162 | BTC | 16 | 13 | 1 | 1 | +48.9% (15min corrigido ambos, 302 tr) | +43.8% |
| Gold/Silver RSI+EMA162 | ETH | 16 | 11 | 0 | 0 | +35.6% (1h corrigido long, 49 tr) | +56.8% |
| Gold/Silver RSI+EMA162 | US100 | 17 | 11 | 0 | 0 | +11.9% (1h corrigido long, 38 tr) | +20.3% |
| Gold/Silver RSI+EMA162 | WTI | 16 | 5 | 1 | 4 | +75.5% (4h como escrito ambos, 52 tr) | +5.4% |
| Gold/Silver RSI+EMA162 | XAU | 16 | 11 | 2 | 0 | +8.3% (15min como escrito ambos, 587 tr) | +13.4% |
| MACD + BB + RSI | BTC | 14 | 9 | 0 | 0 | +9.9% (1h sl5%, 397 tr) | +43.8% |
| MACD + BB + RSI | ETH | 15 | 8 | 0 | 0 | +24.3% (1h sl5%, 447 tr) | +56.8% |
| MACD + BB + RSI | US100 | 12 | 12 | 0 | 0 | +7.8% (30min sl10%, 379 tr) | +20.3% |
| MACD + BB + RSI | WTI | 15 | 1 | 0 | 0 | -7.3% (1D sl5%, 27 tr) | +5.4% |
| MACD + BB + RSI | XAU | 14 | 1 | 0 | 0 | +0.5% (1h semstop, 193 tr) | +13.4% |
| BB Breakout | BTC | 85 | 80 | 11 | 2 | +47.7% (4h bb15 vol sl0% tp0% long, 134 tr) | +43.8% |
| BB Breakout | ETH | 85 | 84 | 6 | 0 | +54.5% (1h bb40 vol sl0% tp0% long, 355 tr) | +56.8% |
| BB Breakout | US100 | 85 | 65 | 5 | 0 | +11.2% (30min bb40 semvol sl2% tp9% long, 647 tr) | +20.3% |
| BB Breakout | WTI | 85 | 26 | 0 | 14 | +15.5% (4h bb15 semvol sl0% tp0% ambos, 277 tr) | +5.4% |
| BB Breakout | XAU | 85 | 79 | 16 | 0 | +12.0% (15min bb40 semvol sl0% tp0% ambos, 1888 tr) | +13.4% |
| MACD scalp Joel | BTC | 28 | 10 | 0 | 0 | +39.0% (15min tp3.0% sl2.0% ambos, 2391 tr) | +43.8% |
| MACD scalp Joel | ETH | 28 | 3 | 0 | 0 | +40.8% (15min tp1.0% sl1.0% long, 6057 tr) | +56.8% |
| MACD scalp Joel | US100 | 28 | 13 | 0 | 0 | +8.7% (15min tp3.0% sl2.0% long, 407 tr) | +20.3% |
| MACD scalp Joel | WTI | 28 | 4 | 0 | 4 | +10.1% (15min tp3.0% sl2.0% ambos, 1780 tr) | +5.4% |
| MACD scalp Joel | XAU | 28 | 19 | 0 | 0 | +6.4% (15min tp3.0% sl2.0% ambos, 306 tr) | +13.4% |
| Liquidity Sweep Filter | BTC | 39 | 38 | 6 | 6 | +69.2% (1h 30 2 ambos, 345 tr) | +43.8% |
| Liquidity Sweep Filter | ETH | 39 | 39 | 12 | 19 | +102.8% (30min 30 2 ambos, 736 tr) | +56.8% |
| Liquidity Sweep Filter | US100 | 38 | 35 | 3 | 0 | +14.0% (15min 30 1 long, 1210 tr) | +20.3% |
| Liquidity Sweep Filter | WTI | 39 | 13 | 0 | 8 | +22.4% (30min 12 2 ambos, 1521 tr) | +5.4% |
| Liquidity Sweep Filter | XAU | 39 | 37 | 5 | 0 | +12.2% (30min 30 1 ambos, 1225 tr) | +13.4% |
| Renko Open_Close | BTC | 30 | 3 | 0 | 0 | +25.3% (1D m3 long, 210 tr) | +43.8% |
| Renko Open_Close | ETH | 30 | 5 | 0 | 0 | +24.5% (4h m3 long, 1153 tr) | +56.8% |
| Renko Open_Close | US100 | 30 | 2 | 0 | 0 | +7.0% (1D m3 long, 189 tr) | +20.3% |
| Renko Open_Close | WTI | 30 | 4 | 1 | 0 | +1.2% (1D m3 ambos, 376 tr) | +5.4% |
| Renko Open_Close | XAU | 30 | 3 | 0 | 0 | -0.6% (1D m2 ambos, 403 tr) | +13.4% |
| Keltner bounce | BTC | 52 | 10 | 0 | 0 | +16.1% (1h 200 d3 saimedia long, 204 tr) | +43.8% |
| Keltner bounce | ETH | 52 | 10 | 0 | 0 | +33.5% (1h 200 d3 ambos, 258 tr) | +56.8% |
| Keltner bounce | US100 | 51 | 28 | 0 | 0 | +8.6% (30min 200 d8 ambos, 215 tr) | +20.3% |
| Keltner bounce | WTI | 52 | 14 | 1 | 6 | +23.7% (15min 200 d8 ambos, 431 tr) | +5.4% |
| Keltner bounce | XAU | 51 | 11 | 1 | 0 | +3.7% (4h 50 d8 saimedia ambos, 24 tr) | +13.4% |
| LUBE | BTC | 14 | 11 | 3 | 1 | +53.3% (4h 500 tl0.1 ambos, 446 tr) | +43.9% |
| LUBE | ETH | 14 | 13 | 2 | 0 | +47.9% (1D 500 tl0.1 ambos, 49 tr) | +56.8% |
| LUBE | US100 | 14 | 8 | 0 | 0 | +3.8% (1D 500 tl0.1 long, 42 tr) | +20.3% |
| LUBE | WTI | 14 | 3 | 1 | 1 | +10.4% (30min 500 tl-0.1 ambos, 299 tr) | +5.4% |
| LUBE | XAU | 14 | 12 | 1 | 0 | +3.6% (1h 500 tl0.1 ambos, 1534 tr) | +13.4% |
| RSI Binary | BTC | 40 | 15 | 2 | 0 | +8.7% (15min 14 30/70 h3 long, 2546 tr) | +43.8% |
| RSI Binary | ETH | 40 | 9 | 1 | 0 | +11.2% (15min 6 13/82 h3 long, 1319 tr) | +56.8% |
| RSI Binary | US100 | 38 | 9 | 4 | 0 | +4.0% (1D 14 30/70 h10 long, 12 tr) | +20.3% |
| RSI Binary | WTI | 39 | 5 | 1 | 1 | +15.1% (1D 14 30/70 h10 ambos, 54 tr) | +5.4% |
| RSI Binary | XAU | 39 | 7 | 1 | 0 | +1.7% (4h 6 13/82 h10 long, 72 tr) | +13.4% |
| MACD + Stoch + RSI | BTC | 10 | 9 | 1 | 0 | +22.2% (4h k50, 485 tr) | +43.8% |
| MACD + Stoch + RSI | ETH | 10 | 9 | 1 | 0 | +49.2% (30min k50, 3853 tr) | +56.8% |
| MACD + Stoch + RSI | US100 | 10 | 8 | 0 | 0 | +6.5% (1h k50, 1507 tr) | +20.3% |
| MACD + Stoch + RSI | WTI | 10 | 0 | 0 | 0 | -15.1% (1h k80, 1442 tr) | +5.4% |
| MACD + Stoch + RSI | XAU | 10 | 6 | 0 | 0 | +2.7% (4h k80, 303 tr) | +13.4% |
| Super Guppy | BTC | 15 | 15 | 2 | 0 | +31.6% (1D long, 26 tr) | +43.8% |
| Super Guppy | ETH | 15 | 15 | 9 | 8 | +98.3% (30min antecipado ambos, 2848 tr) | +56.8% |
| Super Guppy | US100 | 15 | 13 | 4 | 0 | +19.1% (30min antecipado ambos, 1895 tr) | +20.3% |
| Super Guppy | WTI | 15 | 8 | 0 | 6 | +15.2% (30min antecipado ambos, 2662 tr) | +5.4% |
| Super Guppy | XAU | 15 | 10 | 2 | 0 | +12.2% (30min antecipado ambos, 2062 tr) | +13.4% |
| MTF RSI | BTC | 29 | 7 | 0 | 0 | +5.3% (4h 1/4/16 40/60 long, 10 tr) | +43.8% |
| MTF RSI | ETH | 29 | 6 | 0 | 0 | +2.6% (15min 1/4/16 40/60 long, 167 tr) | +56.8% |
| MTF RSI | US100 | 29 | 15 | 0 | 0 | +8.3% (15min 1/4/16 30/70 long, 53 tr) | +20.3% |
| MTF RSI | WTI | 32 | 6 | 0 | 2 | +30.5% (4h 1/3/6 30/70 ambos, 19 tr) | +5.4% |
| MTF RSI | XAU | 28 | 2 | 0 | 0 | +0.6% (30min 1/3/6 30/70 ambos, 117 tr) | +13.4% |

## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **MA Consecutive ETH 4h (4 barras, close)** | +134% vs +57% (t 2,1) | +469% vs +328% | +28% vs 0% | +83% vs −11% | +62% vs +13% | +130% (t 2,6) | **aprovada com ressalva** |
| MA Consecutive ETH 30m | +99% (t 1,9) | +227% vs +330% | +38% | +70% | +77% | +72% | quase (terço 1) |
| MA Consecutive BTC 30m | +77% (t 1,8) | +400% vs +130% | **−2% vs +15%** | +11% vs +13% | +12% vs +40% | +53% | reprovada |
| Gold/Silver (como escrito) WTI 4h | +75,5% vs +5,4% (t 2,0) | +39% vs −21% | +45% vs +40% | +79% vs +8% | +81% vs +3% | +75% | quase (52 trades) |
| Gold/Silver WTI 15m / 30m / 1h | +67% / +56% / +45% | ganha | **perde no 15m e 1h** | ganha | ganha | +59% / +52% / +43% | quase/reprovada |
| SuperTREX BTC 1h m4 (long e short) | +83% vs +44% (t 2,8) | +182% vs +130% | +97% vs +15% | **−3% vs +14%** | +27% vs +40% | +82% | reprovada |
| SuperTREX BTC 30m m8 / 4h m2 | +79% / +73% (t 4,6 / 3,5) | ganha | ganha | +17% / +11% vs +13% | **+40% / +31% vs +40%** | +77% / +72% | reprovadas (2ª metade) |
| Liquidity Sweep Filter BTC 1h | +69% (t 2,5) | ganha | ganha | **0% vs +14%** | +22% vs +40% | +67% | reprovada |
| Liquidity Sweep Filter ETH 1h / 15m | +101% / +100% | perde | ganha | ganha | ganha | +94% / +72% | quase (terço 1) |
| Trend Surfers ETH 4h (55) | +100% (t 1,8) | perde | ganha | ganha | ganha | +99% | quase (terço 1) |
| Super Guppy ETH 30m | +98% (t 2,5) | perde | ganha | ganha | ganha | +75% | quase (terço 1) |
| Liquidity Sweep Filter WTI 30m | +22% | ganha | perde | perde | ganha | +11,5% | reprovada |

## Conclusões

- **MA Consecutive Up/Down no ETH 4h** (4 closes seguidos subindo = compra, caindo = vende, sempre posicionado) passa em todos os terços, na 2ª metade (+62% vs +13%) e com custo 4× (+130%). Ressalvas: vizinhança irregular (30m e 1h com 4 barras também passam do B&H, mas a versão com EMA20 no 4h e a de 8 barras não); DD −66% (−1,08 em log); 57 trades/ano; é outro seguidor de tendência no ETH.
- A **SuperTREX no BTC** foi o destaque da grade (18 células acima do B&H, t até 4,6), mas todas morrem em 2024-26 (terço 3 e 2ª metade abaixo do B&H).
- A **Gold/Silver como escrita no WTI** ganha nos três terços no 4h, mas com só 52 trades; o ganho vem todo do lado vendido (o "exit" do script nunca fecha, então ela fica vendida sempre que o preço está abaixo da EMA162) e o DD é de −68% a −82%. Fica como "quase".
- XAU e US100: nenhuma célula acima do B&H com t > 1.
