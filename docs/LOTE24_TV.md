# Lote 24 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote24.py` (grade) e `scripts/study_tvlote24_rob.py` (robustez). Resultados: `results/study_tvlote24_{ativo}.txt`, `_grid.csv` e `results/study_tvlote24_rob_{ativo}.txt`.

**Puladas na ordem da lista (28):**
- **Olha o futuro:** Qullamaggie (`5bTajWQM`, lookahead_on), PowerHouse (`xR8aIjgP`), EmperorBTC VWAP (`wmJ1ovZQ`), SPY day trader (`7zXPSx9G`) e `security` em Pine v2 (`DNjH5QA9`, Daily Candle Cross `z9AN5ziF`, `TOv4zoTc`).
- **Páginas 404:** `Q5TPHHLs` e `hNPuoyrz`.
- **Templates, exemplos ou ferramentas:** Two TP/Two SL (`tGTV8MkY`), Trailing Take Profit (`W8nc1c3V`), IK Grid (`IIchZZ2m`, grid), backtest time ranges (`xAEG4ZJG`) e leverage/margin (`9Iwinz7I`).
- **Duplicadas:** Donchian Breakout (`hyYvFjux`, o breakout/Turtle do lote 22) e Kirk65 UTBot (`cbPurhXs`, o UT Bot do lote 13).
- **Fora do escopo ou complexas demais para reproduzir com fidelidade:** BTC 15 min (`xGk5K4DE`, HMA de 1 minuto via `security`), Elder Ray (`Cv3YP9Tw`, limiar absoluto de −200 no preço), RSI divergence (`ASVRhqFM`, regressões e arrays), `KOfsPM9h` (sessão da NSE), Death to the Bear (`COwM0rKz`, piramidação de 6), CHOP Zone (`GrP0zABg`, máquina de estados), Supply/Demand Order Block (`lQ5zIOGa`), `zFPZofwt` (662 linhas), Braid filter (`ZmsAUj1J`, 343 linhas), Fractal [KL] (`agyP7x3R`, TPs parciais), SSL Hybrid (`Sso2cdEm`, 552 linhas) e 2mars (`Y68meyX1`, 649 linhas).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 194 | SOTT | `cJhpIJ2w` | estocástico 250 suavizado por VAR (VIDYA/CMO9) de 50 cruzando o OTT (VAR 3, 0,618%) de 2 barras atrás; inverte |
| 195 | BEST Supertrend | `6knHPR6c` | SuperTrend diário (3, 3) do dia anterior + regime SMA7 > SMA20; sai no cruzamento contrário |
| 196 | Mbit MA | `hXrtpUdS` | contrário: 27 fechamentos seguidos abaixo (acima) da SMA520 compra (vende); inverte |
| 197 | Triple EMA + QQE [TradeDots] | `M4y5HT3h` | c > TEMA20 > TEMA40 subindo e RSI suavizado cruzando a linha QQE, fora de segunda; só flat; stop móvel no fechamento (120 pips → 1%/3%) |
| 198 | SuperTrend Backtester | `GMZLB374` | SuperTrend ATR7 × 3 inverte na virada; TP/SL de 100 ticks → 0/1/3% |
| 199 | HMA50 + Supertrend | `3SHJZytF` | SuperTrend (10, 3) e HMA50 subindo/caindo concordando; discordância zera |
| 200 | Stochastic RSI + RVI | `22FnhBk9` | StochRSI K ≥ D abaixo de 30 com RVI cruzando o sinal (espelho acima de 70); alterna |
| 201 | SMC | `Zcf69Yqd` | abaixo do equilíbrio do swing (8 barras), acima do fundo e da SMA50 compra; espelho vende (order block sempre verdadeiro) |
| 202 | Donchian free bot | `KZuFvEYa` | stop de compra na máxima de 10 (saída no meio do canal de 10), venda na mínima de 20 (meio do canal de 20); alvo 2,5%; só flat |
| 203 | Gap Filling | `ghocsiv7` | gap de baixa compra / de alta vende com alvo na borda do corpo anterior; zera na virada do dia; só intraday |
| 204 | Bitcoin Momentum | `Tce7SnL7` | long-only; close acima da EMA20 semanal (semana fechada) sem cautela; stop móvel maior mínima de 7 − ATR5 |
| 205 | Hull Fisher | `QTYaYuX7` | Fisher (9) da HMA14 da abertura com CCI14 e HMA (condições 7 e 8); fecha na virada do Fisher ou da HMA |
| 206 | DEMA 8/20/63 | `AbRhwDeX` | DEMA8 do ohlc4 acima da DEMA20 da mínima e da DEMA63 do close compra; espelho vende |
| 207 | Low-High Trend | `o97hSCY4` | long-only; close cruza acima da mínima de 20 fechamentos acima da EMA200; alvo 8% (ou saída pela máxima de 10) |
| 208 | Combo 123 Reversal & Statistical Volatility | `3w6l57bw` | 123 Reversal (estocástico 14) e volatilidade estatística (30) concordando; inverte |
| 209 | VWMA/SMA 3Commas | `cH5Tjlns` | VWMA13 × SMA13 inverte; saída por TP/SL de ATR21 fixados nos cruzamentos de 26 ou pelo estocástico 80/20 |
| 210 | VWAPStrategy | `t1lk7Uvk` | SMA3 cruza a VWAP diária; inverte; só intraday |
| 211 | Bullish Engulfing [Quant Science] | `0moOi6G5` | long-only; engolfo de alta abaixo da SMA50; TP/SL 6,67% (2% do capital com 30%) ou 2% |
| 212 | EMA Crossover with TP | `B7umqU7W` | EMA20 × EMA50 inverte; alvo 0,5 × range além da barra do sinal; stop 3% do close recolocado a cada barra |
| 213 | AlphaTrend | `uvkI3QJC` | AlphaTrend (ATR14, MFI14 ou RSI14) cruzando a si mesmo de 2 barras atrás; inverte |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H. XAU e US100 não tiveram nenhuma célula acima do B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| SOTT | BTC | 37 | 36 | 3 | 3 | +54.1% (4h s250 p2 ambos, 63 tr) | +43.7% |
| SOTT | ETH | 38 | 37 | 3 | 8 | +108.1% (15min s50 p0.618 ambos, 4106 tr) | +56.8% |
| SOTT | US100 | 37 | 28 | 0 | 0 | +11.7% (15min s250 p2 long, 432 tr) | +20.3% |
| SOTT | WTI | 39 | 14 | 3 | 9 | +23.2% (30min s50 p0.618 ambos, 1863 tr) | +5.4% |
| SOTT | XAU | 37 | 37 | 4 | 0 | +11.9% (1h s50 p0.618 ambos, 777 tr) | +13.4% |
| BEST Supertrend | BTC | 20 | 20 | 4 | 2 | +58.1% (1h m3 ambos, 1837 tr) | +43.9% |
| BEST Supertrend | ETH | 20 | 20 | 11 | 10 | +121.9% (1h m3 ambos, 1784 tr) | +56.8% |
| BEST Supertrend | US100 | 20 | 16 | 2 | 0 | +9.8% (1D m1.5 long, 48 tr) | +20.2% |
| BEST Supertrend | WTI | 20 | 4 | 0 | 1 | +7.3% (1D m3 ambos, 97 tr) | +5.7% |
| BEST Supertrend | XAU | 20 | 15 | 1 | 0 | +10.2% (1h m1.5 ambos, 1438 tr) | +13.4% |
| Mbit MA | BTC | 34 | 13 | 0 | 0 | +12.2% (30min ma520 n27 long, 166 tr) | +43.9% |
| Mbit MA | ETH | 35 | 14 | 0 | 0 | +19.3% (1h ma200 n27 long, 140 tr) | +56.8% |
| Mbit MA | US100 | 32 | 17 | 0 | 0 | +8.4% (30min ma200 n27 long, 215 tr) | +20.3% |
| Mbit MA | WTI | 35 | 3 | 0 | 2 | +9.0% (15min ma200 n27 ambos, 1009 tr) | +5.4% |
| Mbit MA | XAU | 34 | 6 | 0 | 0 | +2.1% (1h ma200 n27 ambos, 196 tr) | +13.4% |
| Triple EMA + QQE | BTC | 20 | 19 | 4 | 0 | +32.7% (1h p1% ambos, 832 tr) | +43.9% |
| Triple EMA + QQE | ETH | 20 | 20 | 3 | 0 | +50.3% (1h p3% ambos, 551 tr) | +56.8% |
| Triple EMA + QQE | US100 | 20 | 14 | 1 | 0 | +13.4% (1h p3% long, 135 tr) | +20.3% |
| Triple EMA + QQE | WTI | 20 | 4 | 0 | 0 | +4.0% (4h p3% ambos, 170 tr) | +5.4% |
| Triple EMA + QQE | XAU | 20 | 15 | 1 | 0 | +7.1% (30min p1% long, 381 tr) | +13.4% |
| SuperTrend Backtester | BTC | 30 | 23 | 0 | 0 | +28.2% (4h semtp long, 168 tr) | +43.7% |
| SuperTrend Backtester | ETH | 30 | 23 | 3 | 2 | +60.4% (30min semtp ambos, 2476 tr) | +56.8% |
| SuperTrend Backtester | US100 | 30 | 27 | 8 | 0 | +18.3% (1h tp3% ambos, 1348 tr) | +20.3% |
| SuperTrend Backtester | WTI | 30 | 5 | 0 | 4 | +21.7% (1h semtp ambos, 1623 tr) | +5.4% |
| SuperTrend Backtester | XAU | 30 | 14 | 3 | 0 | +10.8% (30min semtp ambos, 2242 tr) | +13.4% |
| HMA50 + Supertrend | BTC | 20 | 19 | 2 | 0 | +38.1% (30min h100 ambos, 3021 tr) | +43.9% |
| HMA50 + Supertrend | ETH | 20 | 20 | 4 | 4 | +113.3% (30min h100 ambos, 2958 tr) | +56.8% |
| HMA50 + Supertrend | US100 | 20 | 17 | 3 | 0 | +12.2% (1h h50 long, 902 tr) | +20.3% |
| HMA50 + Supertrend | WTI | 20 | 7 | 0 | 4 | +22.8% (1D h100 ambos, 61 tr) | +5.7% |
| HMA50 + Supertrend | XAU | 20 | 14 | 2 | 0 | +10.1% (1h h50 ambos, 1645 tr) | +13.4% |
| StochRSI + RVI | BTC | 40 | 20 | 0 | 0 | +30.4% (4h p5 50/50 ambos, 742 tr) | +43.7% |
| StochRSI + RVI | ETH | 40 | 22 | 0 | 0 | +34.9% (1D p5 50/50 ambos, 114 tr) | +56.5% |
| StochRSI + RVI | US100 | 40 | 17 | 1 | 0 | +12.9% (4h p5 30/70 long, 221 tr) | +20.3% |
| StochRSI + RVI | WTI | 40 | 6 | 0 | 6 | +24.3% (4h p10 30/70 ambos, 361 tr) | +5.4% |
| StochRSI + RVI | XAU | 40 | 8 | 0 | 0 | +4.1% (1D p10 30/70 ambos, 51 tr) | +13.4% |
| SMC | BTC | 20 | 15 | 3 | 1 | +53.7% (1D lb8 ambos, 40 tr) | +43.8% |
| SMC | ETH | 20 | 16 | 1 | 4 | +82.7% (30min lb8 ambos, 2303 tr) | +56.8% |
| SMC | US100 | 20 | 14 | 2 | 0 | +11.9% (30min lb30 long, 458 tr) | +20.3% |
| SMC | WTI | 20 | 7 | 1 | 4 | +28.3% (15min lb30 ambos, 2522 tr) | +5.4% |
| SMC | XAU | 20 | 14 | 0 | 0 | +7.6% (30min lb8 ambos, 1603 tr) | +13.4% |
| Donchian free bot | BTC | 20 | 16 | 2 | 0 | +31.1% (1D semtp ambos, 173 tr) | +43.8% |
| Donchian free bot | ETH | 20 | 19 | 13 | 1 | +57.3% (1h semtp ambos, 4413 tr) | +56.8% |
| Donchian free bot | US100 | 20 | 18 | 12 | 0 | +6.2% (1D tp2.5% long, 189 tr) | +20.2% |
| Donchian free bot | WTI | 20 | 6 | 6 | 0 | +2.6% (1h tp2.5% ambos, 5137 tr) | +5.4% |
| Donchian free bot | XAU | 20 | 12 | 6 | 0 | +8.9% (4h tp2.5% ambos, 938 tr) | +13.4% |
| Gap Filling | BTC | 8 | 2 | 0 | 0 | +1.2% (15min semalvo long, 69 tr) | +43.8% |
| Gap Filling | ETH | 8 | 6 | 0 | 0 | +0.6% (30min semalvo ambos, 36 tr) | +56.8% |
| Gap Filling | US100 | 16 | 7 | 0 | 0 | +3.5% (4h semalvo long, 201 tr) | +20.3% |
| Gap Filling | WTI | 16 | 5 | 0 | 2 | +8.9% (1h semalvo ambos, 951 tr) | +5.4% |
| Gap Filling | XAU | 16 | 5 | 0 | 0 | +0.8% (15min semalvo long, 720 tr) | +13.4% |
| Bitcoin Momentum | BTC | 15 | 12 | 4 | 0 | +36.6% (4h atr1, 565 tr) | +43.7% |
| Bitcoin Momentum | ETH | 15 | 15 | 3 | 0 | +47.9% (4h atr3, 565 tr) | +56.6% |
| Bitcoin Momentum | US100 | 15 | 12 | 0 | 0 | +6.1% (1D atr2, 124 tr) | +20.2% |
| Bitcoin Momentum | WTI | 15 | 0 | 0 | 0 | -12.8% (4h atr1, 574 tr) | +5.4% |
| Bitcoin Momentum | XAU | 15 | 3 | 1 | 0 | +4.5% (1h atr3, 1965 tr) | +13.4% |
| Hull Fisher | BTC | 20 | 12 | 1 | 0 | +43.1% (4h h50 ambos, 660 tr) | +43.7% |
| Hull Fisher | ETH | 20 | 15 | 0 | 0 | +52.7% (4h h50 ambos, 641 tr) | +56.6% |
| Hull Fisher | US100 | 20 | 10 | 0 | 0 | +6.5% (1h h50 long, 945 tr) | +20.3% |
| Hull Fisher | WTI | 20 | 4 | 0 | 1 | +6.0% (1h h50 ambos, 2437 tr) | +5.4% |
| Hull Fisher | XAU | 20 | 7 | 1 | 0 | +10.3% (1h h50 ambos, 1883 tr) | +13.4% |
| DEMA 8/20/63 | BTC | 20 | 19 | 2 | 1 | +47.4% (4h x1 ambos, 498 tr) | +43.7% |
| DEMA 8/20/63 | ETH | 20 | 19 | 4 | 9 | +134.9% (1D x1 ambos, 62 tr) | +56.5% |
| DEMA 8/20/63 | US100 | 20 | 18 | 3 | 0 | +13.9% (30min x1 long, 1554 tr) | +20.3% |
| DEMA 8/20/63 | WTI | 20 | 5 | 0 | 2 | +15.7% (15min x3 ambos, 3080 tr) | +5.4% |
| DEMA 8/20/63 | XAU | 20 | 16 | 2 | 0 | +10.7% (1h x1 ambos, 1532 tr) | +13.4% |
| Low-High Trend | BTC | 10 | 10 | 0 | 0 | +33.0% (30min tp8, 34 tr) | +43.9% |
| Low-High Trend | ETH | 10 | 8 | 1 | 0 | +51.9% (15min tp8, 57 tr) | +56.8% |
| Low-High Trend | US100 | 10 | 8 | 0 | 0 | +5.6% (4h hi10, 157 tr) | +20.3% |
| Low-High Trend | WTI | 10 | 0 | 0 | 0 | -3.8% (4h hi10, 139 tr) | +5.4% |
| Low-High Trend | XAU | 10 | 6 | 0 | 0 | -1.1% (15min hi10, 1824 tr) | +13.4% |
| VWMA/SMA 3Commas | BTC | 20 | 11 | 0 | 0 | +26.3% (4h semniveis long, 259 tr) | +43.7% |
| VWMA/SMA 3Commas | ETH | 20 | 10 | 0 | 0 | +22.6% (1D semniveis long, 55 tr) | +56.5% |
| VWMA/SMA 3Commas | US100 | 20 | 9 | 2 | 0 | +17.4% (4h semniveis long, 453 tr) | +20.3% |
| VWMA/SMA 3Commas | WTI | 20 | 3 | 0 | 0 | +0.7% (4h semniveis ambos, 2388 tr) | +5.4% |
| VWMA/SMA 3Commas | XAU | 20 | 7 | 0 | 0 | +2.1% (4h niveis long, 886 tr) | +13.4% |
| VWAPStrategy | BTC | 16 | 13 | 7 | 3 | +54.1% (30min sma3 ambos, 12239 tr) | +43.9% |
| VWAPStrategy | ETH | 16 | 11 | 9 | 8 | +175.0% (30min sma3 ambos, 11975 tr) | +56.8% |
| VWAPStrategy | US100 | 16 | 8 | 5 | 0 | +6.5% (4h sma20 long, 405 tr) | +20.3% |
| VWAPStrategy | WTI | 16 | 0 | 0 | 2 | +13.3% (4h sma3 ambos, 5577 tr) | +5.4% |
| VWAPStrategy | XAU | 16 | 4 | 4 | 0 | +4.6% (1h sma3 ambos, 6688 tr) | +13.4% |
| Bullish Engulfing | BTC | 25 | 17 | 0 | 0 | +29.7% (30min sl6.67% tp6.67% semtend, 415 tr) | +43.9% |
| Bullish Engulfing | ETH | 25 | 16 | 0 | 0 | +39.1% (4h sl6.67% tp6.67% semtend, 310 tr) | +56.6% |
| Bullish Engulfing | US100 | 22 | 21 | 0 | 0 | +16.6% (30min sl6.67% tp6.67% semtend, 101 tr) | +20.3% |
| Bullish Engulfing | WTI | 25 | 0 | 0 | 0 | +4.2% (4h sl2.00% tp2.00% tend, 145 tr) | +5.4% |
| Bullish Engulfing | XAU | 25 | 10 | 0 | 0 | +1.6% (1D sl6.67% tp6.67% semtend, 31 tr) | +13.4% |
| EMA Cross TP | BTC | 40 | 37 | 3 | 0 | +41.5% (15min sl3% semtp ambos, 4680 tr) | +43.8% |
| EMA Cross TP | ETH | 40 | 27 | 4 | 4 | +95.9% (15min sl3% semtp ambos, 4742 tr) | +56.8% |
| EMA Cross TP | US100 | 34 | 23 | 6 | 0 | +12.1% (30min sl3% semtp ambos, 1456 tr) | +20.3% |
| EMA Cross TP | WTI | 40 | 8 | 1 | 2 | +15.7% (30min sl3% semtp ambos, 2093 tr) | +5.4% |
| EMA Cross TP | XAU | 33 | 17 | 3 | 0 | +11.1% (30min sl6% semtp ambos, 1674 tr) | +13.4% |
| AlphaTrend | BTC | 20 | 18 | 2 | 1 | +53.9% (30min mfi ambos, 2403 tr) | +43.9% |
| AlphaTrend | ETH | 20 | 20 | 3 | 4 | +98.7% (30min rsi ambos, 2561 tr) | +56.8% |
| AlphaTrend | US100 | 20 | 18 | 1 | 0 | +13.6% (30min rsi long, 1217 tr) | +20.3% |
| AlphaTrend | WTI | 20 | 8 | 0 | 6 | +18.5% (30min mfi ambos, 2877 tr) | +5.4% |
| AlphaTrend | XAU | 20 | 19 | 1 | 0 | +8.6% (1h rsi ambos, 1089 tr) | +13.4% |

## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **BEST Supertrend ETH 1h (m3, ambos)** | +122% vs +57% (t 3,6) | +366% vs +330% | +52% vs +1% | +64% vs −11% | +31% vs +13% | +105% | **aprovada com ressalva** |
| **VWAPStrategy ETH 30m (SMA3, ambos)** | +175% vs +57% (t 5,2) | +549% vs +330% | +103% vs +1% | +54% vs −11% | +59% vs +13% | **+61,5% vs +57%** | **aprovada com ressalva forte (custo)** |
| VWAPStrategy ETH 15m (SMA3, ambos) | +163% | ganha | ganha | ganha | +80% vs +13% | **+27% vs +57%** | reprovada (custo) |
| BEST Supertrend ETH 1h (m3, long) | +78% (Sh 1,6) | **+275% vs +330%** | +25% vs +1% | +20% vs −11% | +18% vs +13% | +70% | quase (terço 1) |
| DEMA 8/20/63 ETH 4h (ambos) | +115% | **+287% vs +328%** | +99% | +19% vs −11% | +37% vs +13% | +110% | quase (terço 1) |
| HMA + Supertrend ETH 30m (HMA100, ambos) | +113% | **+261% vs +330%** | +82% | +41% vs −11% | +32% vs +13% | +87% | quase (terço 1) |
| BEST Supertrend BTC 1h / AlphaTrend BTC 30m / VWAP BTC 30m | +58% / +54% / +54% | **perdem** / perde / ganha | ganham | +14 / +18 / +5% vs +13% | **perdem** (+20 / +21 / +19% vs +40%) | +46% / +38% / −10% | reprovadas |
| SMC WTI 15m (lb30) | +28% vs +5% | ganha | **+31% vs +38%** | ganha | +4,6% vs +3,6% | +10% | reprovada |
| SOTT WTI 30m (s50) | +23% | ganha | ganha | **+7,4% vs +7,7%** | +19% vs +3% | +10% | reprovada |

## Conclusões

- **BEST Supertrend no ETH 1h** (SuperTrend diário do dia anterior como filtro de nível + SMA7/SMA20 como regime, comprado e vendido) passa em todos os terços, na 2ª metade e com custo 4× (+105%). A vizinhança é boa: 30m, 1h e 4h com multiplicador 3 e 1,5 ficam acima do B&H, e a versão só comprada tem Sharpe 1,6 (mas perde o terço 1). Ressalvas: 264 trades/ano, DD −80% (log), mais um seguidor de tendência no ETH; no BTC a mesma regra perde a 2ª metade.
- **VWAPStrategy no ETH 30m** (SMA3 cruzando a VWAP diária) passa em tudo, mas faz ~1.770 trades/ano e com custo 4× sobra só +61,5% vs +57%; no 15m o custo 4× já reprova. Lucro bruto de 7 bp por trade: depende de custo baixo e execução boa. Fica aprovada com ressalva forte.
- **ETH:** DEMA 8/20/63, HMA + Supertrend e BEST só comprado perdem só o terço 1 (o padrão dos seguidores de tendência no ETH).
- **XAU e US100:** nada acima do B&H. **WTI:** várias células acima do B&H fraco (+5%), nenhuma robusta.
