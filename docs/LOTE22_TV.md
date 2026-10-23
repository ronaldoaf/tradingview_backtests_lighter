# Lote 22 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote22.py` (grade) e `scripts/study_tvlote22_rob.py` (robustez). Resultados: `results/study_tvlote22_{ativo}.txt`, `_grid.csv` e `results/study_tvlote22_rob_{ativo}.txt`.

**Puladas na ordem da lista (17):**
- **Olha o futuro:** MULTIPLE TIME FRAME STRATEGY (`gciwtPOi`, `security` em Pine v2).
- **Dado externo:** TICK Scalping SPY (`yiBwexdm`, usa o TICK e o SPY) e MVRV Z-Score (`v3TqVthK`, dado on-chain).
- **Templates, exemplos ou ferramentas:** Traling SL Target (`4jxYYaGU`), GRID SPOT (`LK1zL4D8`, sem ordens de estratégia), DCA Bot Emulator (`vyStpg6g`), Advanced Position Management (`IsMKlnoJ`) e BEST Trailing Take Profit (`9YaLIh0i`).
- **Página 404:** noro's bands scalper (`nWSGZciA`) e Instrument Z 3Commas (`1OX9Wu8g`).
- **Sem entradas:** Price Action (`2Zg5oABG`, as entradas estão comentadas no código).
- **Complexas demais para reproduzir com fidelidade:** Rally Base Drop SND LuxAlgo (`dagKHrx4`), ML SuperTrend (`9Mm3qKME`, k-means), SSL Hybrid QQE (`fl8CV2N0`, 555 linhas), FTB (`gcu6zUkw`, sessão no fuso da corretora + PineConnector), HalfTrend + HullButterfly (`lL04fUNr`, 427 linhas), Session Breakout Scalper (`7abDoROC`, 670 linhas) e VXD Cloud (`OKKz3vDv`, nuvem com TPs parciais e breakeven).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 154 | Forex Scalping BB + RSI + ADX | `sR1hePBi` | RSI20 cruza 35 (65) com close abaixo (acima) da banda superior BB60 e ADX < 32; sai na média; TP/SL de 90 ticks virou % |
| 155 | EMA Crossover Strategy | `sxJejjdy` | EMA(hl2) 20 × 60; inverte |
| 156 | EWO, RSI advanced Signals (Exhaustion Filter) | `B7MQqWes` | RSI cruza 40/60 com MFI, EWO, volume e rompimento/exaustão; sinais alternados; inverte |
| 157 | Easy to Use MACD + RSI | `06gU5i7b` | long-only; MACD cruza para cima abaixo de 0 com RSI < 50; sai no cruzamento para baixo acima de 0 |
| 158 | TSI CCI Hull with profit | `qwN8CGrU` | TSI suavizado, Hull e CCI da Hull a favor; lucro de 0,5% (checado no fechamento no Pine; aqui alvo no M1) |
| 159 | Real Turtle | `67fpKimh` | stops no canal de 20; saída no canal de 10 ou entrada ∓ 2 × EMA13 do TR; inverte (simulador de stops) |
| 160 | ATR Parabolic SAR [QuantNomad] | `LKfHdoNv` | PSAR com passo af × ATR14, virada no fechamento; entra na 1ª barra; inverte |
| 161 | Ichimoku no offset no repaint + RSI | `MGSCiuSP` | Tenkan × Kijun deslocados 25 barras, close vs nuvem deslocada 50; short com RSI ≥ 50 |
| 162 | Turtle trading (Donchian/ATR) | `gbxblhGl` | uma direção por vez; close rompe o canal de 20; sai no canal de 10 ou no stop EMA3(close ∓ 2 ATR20) |
| 163 | Slopes | `XBgfW9k9` | inclinação da EMA130 vs EMA400 com filtro EMA200; sai no cruzamento das inclinações |
| 164 | Moving Average Band | `wwi02rpz` | close cruza SMA40 das máximas (mínimas); stop na banda oposta, alvo 3R; inverte |
| 165 | Renko Strategy V2 | `oAlFKwej` | tijolos ATR10 no close e na abertura; virada de cor; short desligado no padrão |
| 166 | Highest High and Lowest Low Channel | `1SMJivyk` | close rompe o canal de 20; sempre posicionado |
| 167 | Parabolic SAR on close [QuantNomad] | `gK7skk6m` | PSAR clássico com virada no fechamento; inverte |
| 168 | XAUUSD Scalping V2 AGRESIV | `5q4PsY3a` | EMA5 × 13 com RSI7 > 55 / < 45; TP 1,2 ATR, SL 0,8 ATR (o trailing não ativa no Pine) |
| 169 | PMax on Rsi w T3 | `ZLcmWQtj` | PMax sobre o T3 do RSI com "ATR" do RSI; inverte |
| 170 | volatility based force trade scalper | `FN3ZkHZA` | force index acumulado EMA3 × 20 com ATR20 > ATR50 e vela a favor; inverte |
| 171 | Tripple super Trend Strategy | `aCbQTE0W` | como escrito, o filtro de SuperTrend é sempre verdadeiro; StochRSI 28/78 + EMA200 (do próprio tempo, não do 15m); stop no extremo de 30/25 barras, alvo 2R/1,5R |
| 172 | Cumulative RSI Strategy | `nI9Csm8g` | long-only; soma de 3 RSI3 cruza 60 compra, 282 vende |
| 173 | Breakout Trend Follower | `9uvZIPnH` | long-only; stop de compra no último pivô de alta (acima da SMA50), stop de saída no último pivô de baixa |

Correção durante o lote: a primeira rodada usou o PSAR com ATR na célula padrão do "PSAR on close"; a grade foi rodada de novo com o PSAR clássico.

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| BB + RSI + ADX | BTC | 54 | 18 | 1 | 0 | +26.8% (4h sl0.0% adx32 ambos, 87 tr) | +43.7% |
| BB + RSI + ADX | ETH | 56 | 17 | 0 | 0 | +6.0% (15min sl0.0% adx32 long, 694 tr) | +56.8% |
| BB + RSI + ADX | US100 | 55 | 19 | 0 | 0 | +6.3% (4h sl0.0% adx32 ambos, 53 tr) | +20.3% |
| BB + RSI + ADX | WTI | 60 | 6 | 2 | 1 | +9.0% (4h sl0.0% adx32 ambos, 81 tr) | +5.4% |
| BB + RSI + ADX | XAU | 56 | 3 | 0 | 0 | +2.3% (4h sl0.0% adx100 ambos, 95 tr) | +13.4% |
| EMA Crossover hl2 | BTC | 37 | 37 | 5 | 3 | +55.0% (4h 50x5 ambos, 74 tr) | +43.7% |
| EMA Crossover hl2 | ETH | 38 | 38 | 13 | 18 | +113.9% (15min 20x3 ambos, 4238 tr) | +56.8% |
| EMA Crossover hl2 | US100 | 35 | 32 | 1 | 0 | +14.6% (15min 20x5 long, 1014 tr) | +20.3% |
| EMA Crossover hl2 | WTI | 38 | 17 | 0 | 9 | +14.1% (1h 50x3 ambos, 347 tr) | +5.4% |
| EMA Crossover hl2 | XAU | 38 | 37 | 2 | 0 | +10.5% (15min 20x5 ambos, 2287 tr) | +13.4% |
| EWO RSI | BTC | 19 | 10 | 0 | 0 | +19.2% (4h semvol long, 69 tr) | +43.7% |
| EWO RSI | ETH | 18 | 6 | 0 | 0 | +23.1% (4h vol long, 49 tr) | +56.6% |
| EWO RSI | US100 | 18 | 9 | 0 | 0 | +10.2% (1h semvol long, 233 tr) | +20.3% |
| EWO RSI | WTI | 18 | 6 | 0 | 4 | +35.4% (1h semvol ambos, 526 tr) | +5.4% |
| EWO RSI | XAU | 18 | 0 | 0 | 0 | -0.4% (30min vol ambos, 594 tr) | +13.4% |
| Easy MACD + RSI | BTC | 20 | 13 | 0 | 0 | +10.1% (1h rsi50 sl5%, 533 tr) | +43.9% |
| Easy MACD + RSI | ETH | 20 | 15 | 0 | 0 | +23.2% (4h rsi101 sl5%, 270 tr) | +56.6% |
| Easy MACD + RSI | US100 | 19 | 15 | 0 | 0 | +10.9% (1h rsi101 semstop, 459 tr) | +20.3% |
| Easy MACD + RSI | WTI | 20 | 0 | 0 | 0 | -7.2% (1D rsi50 sl5%, 31 tr) | +5.7% |
| Easy MACD + RSI | XAU | 20 | 0 | 0 | 0 | -1.3% (1h rsi50 semstop, 317 tr) | +13.4% |
| TSI CCI Hull | BTC | 30 | 21 | 0 | 0 | +25.3% (15min tp0.0% long, 1454 tr) | +43.8% |
| TSI CCI Hull | ETH | 30 | 27 | 0 | 1 | +59.2% (1h tp0.0% ambos, 690 tr) | +56.8% |
| TSI CCI Hull | US100 | 30 | 18 | 3 | 0 | +13.2% (15min tp0.0% long, 1033 tr) | +20.3% |
| TSI CCI Hull | WTI | 30 | 8 | 1 | 9 | +39.3% (15min tp0.0% ambos, 2690 tr) | +5.4% |
| TSI CCI Hull | XAU | 30 | 22 | 5 | 3 | +14.4% (15min tp2.0% ambos, 2384 tr) | +13.4% |
| Real Turtle | BTC | 40 | 36 | 5 | 0 | +38.7% (4h 55/20 n4 ambos, 268 tr) | +43.7% |
| Real Turtle | ETH | 40 | 40 | 12 | 5 | +86.2% (1D 20/10 n2 ambos, 93 tr) | +56.5% |
| Real Turtle | US100 | 40 | 36 | 4 | 0 | +7.2% (1D 20/10 n4 long, 57 tr) | +20.2% |
| Real Turtle | WTI | 40 | 11 | 0 | 2 | +7.6% (1D 20/10 n4 ambos, 98 tr) | +5.7% |
| Real Turtle | XAU | 40 | 35 | 9 | 0 | +10.5% (1h 20/10 n2 ambos, 2180 tr) | +13.4% |
| ATR PSAR | BTC | 40 | 38 | 3 | 7 | +83.3% (4h n1 0.02/0.2 ambos, 287 tr) | +43.7% |
| ATR PSAR | ETH | 38 | 37 | 2 | 10 | +101.9% (30min n1 0.02/0.2 ambos, 2105 tr) | +56.8% |
| ATR PSAR | US100 | 40 | 34 | 0 | 0 | +13.1% (1D n1 0.02/0.2 ambos, 54 tr) | +20.2% |
| ATR PSAR | WTI | 40 | 13 | 2 | 10 | +26.8% (30min n1 0.01/0.1 ambos, 910 tr) | +5.4% |
| ATR PSAR | XAU | 40 | 30 | 3 | 0 | +12.3% (30min n1 0.02/0.2 ambos, 1856 tr) | +13.4% |
| Ichimoku no offset | BTC | 20 | 20 | 0 | 0 | +35.2% (15min rsi0 ambos, 4993 tr) | +43.8% |
| Ichimoku no offset | ETH | 20 | 20 | 1 | 1 | +75.0% (15min rsi0 ambos, 4954 tr) | +56.8% |
| Ichimoku no offset | US100 | 20 | 16 | 0 | 0 | +8.8% (30min rsi50 long, 954 tr) | +20.3% |
| Ichimoku no offset | WTI | 20 | 1 | 0 | 1 | +8.5% (4h rsi0 ambos, 289 tr) | +5.4% |
| Ichimoku no offset | XAU | 20 | 11 | 2 | 0 | +5.8% (15min rsi0 ambos, 3456 tr) | +13.4% |
| Turtle Donchian/ATR | BTC | 40 | 23 | 3 | 0 | +35.2% (1D 20/10 m2 long, 33 tr) | +43.8% |
| Turtle Donchian/ATR | ETH | 40 | 21 | 0 | 0 | +49.6% (30min 20/10 m4 long, 1605 tr) | +56.8% |
| Turtle Donchian/ATR | US100 | 40 | 20 | 1 | 0 | +8.2% (1h 20/10 m2 long, 797 tr) | +20.3% |
| Turtle Donchian/ATR | WTI | 40 | 20 | 1 | 18 | +25.2% (15min 55/20 m4 short, 1724 tr) | +5.4% |
| Turtle Donchian/ATR | XAU | 40 | 29 | 3 | 0 | +6.0% (1h 20/10 m2 short, 610 tr) | +13.4% |
| Slopes | BTC | 40 | 39 | 11 | 13 | +73.7% (1D 130/400 semfiltro ambos, 65 tr) | +43.8% |
| Slopes | ETH | 40 | 40 | 17 | 12 | +115.9% (4h 130/400 filtro ambos, 278 tr) | +56.6% |
| Slopes | US100 | 40 | 37 | 8 | 0 | +12.1% (30min 50/200 semfiltro long, 2083 tr) | +20.3% |
| Slopes | WTI | 40 | 9 | 0 | 6 | +12.4% (4h 130/400 semfiltro ambos, 492 tr) | +5.4% |
| Slopes | XAU | 40 | 34 | 6 | 0 | +9.1% (1h 50/200 semfiltro ambos, 2192 tr) | +13.4% |
| MA Band | BTC | 40 | 30 | 2 | 1 | +60.4% (1D 40 rr0 ambos, 71 tr) | +43.8% |
| MA Band | ETH | 40 | 38 | 5 | 12 | +130.3% (30min 40 rr0 ambos, 4312 tr) | +56.8% |
| MA Band | US100 | 40 | 37 | 9 | 0 | +12.8% (30min 100 rr0 long, 902 tr) | +20.3% |
| MA Band | WTI | 40 | 14 | 1 | 9 | +27.1% (4h 40 rr3 ambos, 728 tr) | +5.4% |
| MA Band | XAU | 40 | 23 | 4 | 0 | +9.0% (30min 40 rr0 ambos, 3347 tr) | +13.4% |
| Renko V2 | BTC | 20 | 17 | 1 | 1 | +49.0% (1h atr30 ambos, 3613 tr) | +43.9% |
| Renko V2 | ETH | 20 | 20 | 4 | 5 | +89.7% (1h atr30 ambos, 3653 tr) | +56.8% |
| Renko V2 | US100 | 20 | 14 | 4 | 0 | +13.7% (1h atr30 long, 1589 tr) | +20.3% |
| Renko V2 | WTI | 20 | 3 | 0 | 1 | +9.5% (4h atr30 ambos, 1139 tr) | +5.4% |
| Renko V2 | XAU | 20 | 10 | 0 | 0 | +8.9% (4h atr10 ambos, 821 tr) | +13.4% |
| HH/LL channel | BTC | 28 | 22 | 0 | 0 | +42.6% (4h 20 ambos, 275 tr) | +43.7% |
| HH/LL channel | ETH | 27 | 26 | 0 | 2 | +91.2% (1D 20 ambos, 42 tr) | +56.5% |
| HH/LL channel | US100 | 28 | 20 | 0 | 0 | +11.6% (15min 55 long, 935 tr) | +20.3% |
| HH/LL channel | WTI | 29 | 3 | 0 | 2 | +10.2% (1D 20 ambos, 50 tr) | +5.7% |
| HH/LL channel | XAU | 27 | 23 | 0 | 0 | +11.2% (1h 20 ambos, 941 tr) | +13.4% |
| PSAR on close | BTC | 40 | 24 | 0 | 0 | +33.6% (1D n1 0.02/0.2 ambos, 156 tr) | +43.8% |
| PSAR on close | ETH | 40 | 33 | 5 | 5 | +102.3% (1h n3 0.02/0.2 ambos, 3613 tr) | +56.8% |
| PSAR on close | US100 | 40 | 28 | 1 | 0 | +12.2% (1D n1 0.02/0.2 long, 88 tr) | +20.2% |
| PSAR on close | WTI | 40 | 5 | 0 | 2 | +15.6% (1D n3 0.01/0.1 ambos, 102 tr) | +5.7% |
| PSAR on close | XAU | 40 | 20 | 2 | 2 | +15.6% (4h n1 0.01/0.1 ambos, 502 tr) | +13.4% |
| XAUUSD Scalping V2 | BTC | 24 | 10 | 0 | 0 | +29.0% (4h tp0 sl0 ambos, 856 tr) | +43.7% |
| XAUUSD Scalping V2 | ETH | 24 | 20 | 2 | 3 | +83.1% (4h tp0 sl0 ambos, 840 tr) | +56.6% |
| XAUUSD Scalping V2 | US100 | 24 | 13 | 2 | 0 | +12.9% (1h tp0 sl0 long, 1258 tr) | +20.3% |
| XAUUSD Scalping V2 | WTI | 24 | 1 | 0 | 0 | +3.9% (4h tp1.2 sl0.8 ambos, 984 tr) | +5.4% |
| XAUUSD Scalping V2 | XAU | 24 | 6 | 0 | 0 | +6.5% (4h tp0 sl0 ambos, 688 tr) | +13.4% |
| PMax RSI T3 | BTC | 39 | 30 | 1 | 1 | +70.6% (1D m1.5 t8 ambos, 52 tr) | +43.8% |
| PMax RSI T3 | ETH | 40 | 31 | 1 | 3 | +85.9% (1D m1.5 t8 ambos, 48 tr) | +56.5% |
| PMax RSI T3 | US100 | 40 | 27 | 1 | 0 | +14.6% (15min m3 t20 long, 721 tr) | +20.3% |
| PMax RSI T3 | WTI | 39 | 15 | 3 | 10 | +34.4% (15min m3 t8 ambos, 2430 tr) | +5.4% |
| PMax RSI T3 | XAU | 39 | 20 | 2 | 1 | +14.7% (30min m1.5 t20 ambos, 1314 tr) | +13.4% |
| Force scalper | BTC | 20 | 17 | 4 | 4 | +101.4% (4h 5/50 ambos, 134 tr) | +43.7% |
| Force scalper | ETH | 19 | 17 | 3 | 4 | +86.0% (1h 5/50 ambos, 569 tr) | +56.8% |
| Force scalper | US100 | 20 | 14 | 0 | 0 | +13.2% (30min 5/50 long, 607 tr) | +20.3% |
| Force scalper | WTI | 20 | 7 | 1 | 7 | +41.6% (1D 5/50 ambos, 30 tr) | +5.7% |
| Force scalper | XAU | 20 | 19 | 0 | 0 | +7.8% (1D 3/20 ambos, 74 tr) | +13.4% |
| Triple ST + StochRSI | BTC | 41 | 38 | 2 | 6 | +62.9% (1h 20/80 rr3.0/3.0 ambos, 177 tr) | +43.9% |
| Triple ST + StochRSI | ETH | 43 | 37 | 0 | 2 | +94.9% (15min 28/78 rr3.0/3.0 ambos, 604 tr) | +56.8% |
| Triple ST + StochRSI | US100 | 45 | 36 | 0 | 0 | +11.9% (4h 28/78 rr2.0/1.5 long, 89 tr) | +20.3% |
| Triple ST + StochRSI | WTI | 45 | 14 | 0 | 7 | +27.4% (4h 20/80 rr3.0/3.0 ambos, 101 tr) | +5.4% |
| Triple ST + StochRSI | XAU | 45 | 40 | 1 | 0 | +9.5% (30min 28/78 rr3.0/3.0 ambos, 240 tr) | +13.4% |
| Cumulative RSI | BTC | 19 | 16 | 0 | 0 | +19.3% (1h 20/94, 225 tr) | +43.9% |
| Cumulative RSI | ETH | 19 | 17 | 0 | 0 | +8.4% (4h 10/90, 77 tr) | +56.6% |
| Cumulative RSI | US100 | 18 | 16 | 0 | 0 | +11.8% (4h 20/94, 95 tr) | +20.3% |
| Cumulative RSI | WTI | 18 | 0 | 0 | 0 | -11.9% (1h 10/90 ema100, 104 tr) | +5.4% |
| Cumulative RSI | XAU | 19 | 9 | 0 | 0 | +3.1% (15min 10/90 ema100, 276 tr) | +13.4% |
| Breakout Trend Follower | BTC | 20 | 17 | 0 | 0 | +43.1% (1D p3 sma50, 44 tr) | +43.8% |
| Breakout Trend Follower | ETH | 20 | 20 | 1 | 4 | +73.8% (30min p10 semfiltro, 1051 tr) | +56.8% |
| Breakout Trend Follower | US100 | 20 | 14 | 0 | 0 | +9.1% (15min p10 sma50, 1902 tr) | +20.3% |
| Breakout Trend Follower | WTI | 20 | 0 | 0 | 0 | -18.2% (1D p3 sma50, 48 tr) | +5.7% |
| Breakout Trend Follower | XAU | 20 | 14 | 0 | 0 | +5.5% (4h p3 sma50, 262 tr) | +13.4% |
## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **MA Band WTI 4h (40, alvo 3R, ambos)** | +27,1% vs +5,4% | −0,8% vs −21% | +60% vs +40% | +21% vs +8% | +30% vs +3% | +21,6% | **aprovada com ressalva** |
| Turtle Donchian WTI 30m 55/20 short | +23,2% (Sh 1,0) | +27% vs −19% | **+16% vs +35%** | +26% vs +8% | +22% vs +3% | +17% | quase (terço 2) |
| Turtle Donchian WTI 1h 20/10 m4 short | +22,7% | +45% | **+11% vs +36%** | +14% vs +8% | +13,5% vs +3% | +16% | quase (terço 2) |
| Force scalper WTI 1D 3/20 | +36% | +8% vs −21% | **−10% vs +32%** | +29% vs +8% | +22% vs +3% | +35,5% | reprovada (56 trades) |
| Slopes ETH 4h (ambos) | +116% vs +57% | **+160% vs +328%** | +84% vs 0% | +108% vs −11% | +81% vs +13% | +113% | quase (terço 1) |
| Slopes ETH 4h (long) | +72% (Sh 1,4) | **+134% vs +328%** | +52% | +32% | +43% vs +13% | +71% | quase (terço 1) |
| Force ETH 1h 5/50 long | +61% | perde | ganha | +2% vs −11% | **+6% vs +13%** | +59% | reprovada |
| Breakout Trend Follower ETH 30m p10 | +71% | perde | +4% vs +1% | +20% vs −11% | +17,5% vs +13% | +64% | quase (terço 1, fraco no 2) |
| EMA Crossover ETH 1h 50×5 long | +57% vs +57% | perde | ganha | ganha | +13% vs +13% | +56% | reprovada |
| Force scalper BTC 4h 5/50 (ambos / long) | +101% / +58% | ganha | ganha | ganha | **+24,5% / +23% vs +40%** | +100% / +58% | reprovadas (2ª metade) |
| ATR PSAR BTC 4h long | +54% | +120% vs +129% | ganha | ganha | **+30% vs +40%** | +53% | reprovada |
| Slopes BTC 4h 50/200 / 1D long | +55% / +47,5% | perdem | ganha / <10 trades | ganha / perde | **perdem** | — | reprovadas |
| PSAR on close XAU 4h 0,01/0,1 | +15,6% vs +13,4% | +20% vs +8% | **−5% vs +5%** | +35% vs +31,5% | +21% vs +25% | +12,8% | reprovada |
| PSAR on close XAU 1h / PMax XAU 30m / TSI XAU 15m | +14% / +15% / +14% | — | **perdem** | — | — | +4% / +7,5% / +3% | reprovadas |

## Conclusões

- **MA Band no WTI 4h** (close cruza a SMA40 das máximas compra, a SMA40 das mínimas vende, stop na banda oposta e alvo 3× o risco) passa nos três terços, na 2ª metade (+30% vs +3%) e com custo 4× (+21,6%). A vizinhança é razoável: 4h 40 sem alvo, 4h 100 e 1h 40 também passam do B&H. Ressalva: o lucro vem do lado vendido (a versão long-only perde −11% a.a.). É o mesmo padrão do WTI que já apareceu na Gold/Silver (lote 21) e no Turtle Donchian short deste lote (18 células acima do B&H, todas short): no WTI desta base, rompimentos para baixo funcionam e rompimentos para cima não. Antes de usar, vale checar se isso vem do rolamento do CFD.
- O **Turtle Donchian short no WTI** ganha em quase tudo, mas perde no terço 2020-23 (alta do petróleo). Fica como "quase".
- **ETH:** de novo vários seguidores de tendência acima do B&H (Slopes, EMA Crossover, PSAR, MA Band, Real Turtle, Renko), todos perdendo no terço 1 (alta de 2020-22). A Slopes 4h é a mais forte (+116%, terços 2 e 3 bem acima).
- **BTC:** o Force scalper 4h ganha nos três terços, mas fica abaixo do B&H na 2ª metade.
- **US100:** nenhuma célula acima do B&H. **XAU:** só células marginais, que perdem no terço 2 e com custo 4×.
