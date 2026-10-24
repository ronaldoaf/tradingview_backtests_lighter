# Lote 20 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote20.py` (grade) e `scripts/study_tvlote20_rob.py` (robustez). Resultados: `results/study_tvlote20_{ativo}.txt`, `_grid.csv` e `results/study_tvlote20_rob_{ativo}.txt`.

**Puladas na ordem da lista (substituídas pelas seguintes):** The Always Winning Holy Grail (`aStSXzDa`, exemplo que compra sempre), `d0FZtMLp` (página 404), ORB Heikin Ashi SPY Correlation (`QpJvYDzb`, opera pelo SPY), Super Z (`NIGCEUME`, `security` diário com `lookahead_on` sem `[1]`, olha o futuro), ICT Entry V1 (`mVdZBLJ7`, 1.282 linhas de FVG/iFVG com ordens limite, sem como reproduzir com fidelidade), Trailing Take Profit/Stop Loss (`V7IfK3mr`, template de saídas) e FreedX Grid (`4J80gPhd`, grade com níveis de preço manuais).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 114 | Keltner Channel ETH/USDT 1H | `ezSBm5MS` | long-only; EMA46 > SMA46, open dentro do KC(SMA81, 2,5 × SMA do TR) e close acima, DI+(19) > DI− e > 27; sai abaixo da banda de baixo, SL 4%, TP 20% (TP1 parcial ignorado) |
| 115 | ATR Trailing Stop by ceyhun | `cj3MJWNz` | trailing ATR5 × 0,5 cruza o ATR10 × 3; inverte |
| 116 | 3C QFL Mean reversal | `SDRM0bBY` | long-only; compra 0,5% abaixo da última base (fractal de baixa com volume), TP 1%; DCA de ordens de segurança não reproduzido |
| 117 | Strategy Follow Line MTF | `6lhyIPGA` | EMA21 ± 1 desvio; linha = low − ATR5 (só sobe) ou high + ATR5 (só desce); virada inverte; TF do gráfico |
| 118 | MACD Strategy with trailing ATR stop | `2jDHQAJc` | long-only; MACD 3/5/2 cruza para cima com SMA34 < EMA34; sai com close < preço do sinal − 2,2 × ATR17; TPs parciais viraram TP opcional |
| 119 | 3x SuperTrend (Mel0nTek) | `FUnOi1Nx` | EMA200 + StochRSI cruzando em < 20 (> 80) + 1 dos 3 STs a favor; stop no ST, alvo 1,5R |
| 120 | RSI-Adaptive T3 & SAR | `bldXp6gY` | T3 de comprimento 5-50 pelo RSI; T3 × T3[2] com filtro SAR; stop na mínima/máxima de 10 barras |
| 121 | Moving Regression Band Breakout | `Tls8Y2hc` | regressão polinomial grau 2 em 80 barras ± 2 × MAE; rompimento compra; sai na banda de baixo − ATR (stop no preço de entrada omitido) |
| 122 | Double AI Super Trend | `hLZPT7it` | 2 SuperTrends de VWMA (10×4, 5×3); KNN aproximado por WMA do preço vs WMA do ST (como no lote 16) |
| 123 | RSI and ATR Trend Reversal SL/TP | `hZLgJ29l` | linha de reversão do RSI8/ATR8 no close Heikin Ashi, entrada 1 barra depois; janela limitada a 300 barras |
| 124 | Scalping with Bill Williams Alligator | `b2ShO5Fv` | SMAs 13/8/5 do hl2 HA alinhadas + 2 velas HA a favor; sai quando a ordem quebra |
| 125 | CamarillaStrategy V1 | `tBJNISwj` | H4/L4 do dia anterior (via `[1]`, sem vazamento); trailing em ticks virou SL/TP em % |
| 126 | Nadaraya-Watson Envelope | `HrZicISx` | kernel racional quadrático (8, peso 8, início 25) no log; close cruza o envelope das mínimas compra, sai no das máximas |
| 127 | Extreme Scalping | `qVTgdPBT` | regressão linear 14 ± gap; SL = gap, TP = 3 × gap (ticks viraram %) |
| 128 | Y-Profit Maximizer (Y-PMax) | `6ZFa2t7o` | PMax (ZLEMA13 do hl2, ATR10 × 3); saídas parciais pelo MOST ignoradas; long-only por padrão |
| 129 | PMARP + Madrid MA Ribbon | `T4rBZCvC` | 18 EMAs (5-90) subindo acima da EMA100 + vela anterior de baixa + RSI > 55; espelho no short; TP 1%, SL 27,75% |
| 130 | ATR GOD (TradeSmart) | `Je04kGO0` | 4 SuperTrends alinhados, gatilho na virada do 1º, 3º ou 4º; filtros de volume, ATR e sem quartas; SL 4,5 ATR100, TP 1,5R |
| 131 | [DS] Entry_Exit TRADE V01 | `RO4rB2HF` | EMA8 do ohlc4 cruza a DEMA34; inverte |
| 132 | FRAMA Supertrend strategy | `y81orwSC` | FRAMA 12 × FRAMA da FRAMA no semanal (barras fechadas); o SuperTrend vem desligado por padrão |
| 133 | World Cycle ATH/ATL | `824WmIi7` | diário: 2 × SMA350 cruza abaixo da SMA111 vende; 0,745 × SMA471 cruza acima da EMA150 compra |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Keltner Channel | BTC | 45 | 44 | 1 | 0 | +36.7% (15min 81 2.5 tp20% sl4% semtend, 923 tr) | +43.8% |
| Keltner Channel | ETH | 45 | 45 | 5 | 0 | +51.5% (15min 40 2.0 tp20% sl4% semtend, 1294 tr) | +56.8% |
| Keltner Channel | US100 | 39 | 39 | 1 | 0 | +11.3% (30min 81 2.5 tp6% sl2% semtend, 366 tr) | +20.3% |
| Keltner Channel | WTI | 45 | 1 | 0 | 0 | +0.8% (1D 40 2.0 tp6% sl2% tend, 13 tr) | +5.4% |
| Keltner Channel | XAU | 45 | 42 | 2 | 0 | +5.7% (1h 81 2.5 tp6% sl2% tend, 140 tr) | +13.4% |
| ATR Trailing ceyhun | BTC | 30 | 28 | 0 | 2 | +64.5% (4h m2 5 ambos, 147 tr) | +43.8% |
| ATR Trailing ceyhun | ETH | 30 | 30 | 3 | 6 | +104.0% (30min m2 3 ambos, 2630 tr) | +56.8% |
| ATR Trailing ceyhun | US100 | 30 | 25 | 2 | 0 | +11.0% (15min m2 5 long, 1295 tr) | +20.3% |
| ATR Trailing ceyhun | WTI | 30 | 9 | 0 | 5 | +19.2% (15min m2 5 ambos, 3174 tr) | +5.4% |
| ATR Trailing ceyhun | XAU | 30 | 24 | 2 | 0 | +11.0% (4h m2 3 ambos, 332 tr) | +13.4% |
| 3C QFL | BTC | 45 | 29 | 0 | 0 | +29.7% (15min 0.5% tp3% semstop age10, 87 tr) | +43.8% |
| 3C QFL | ETH | 45 | 31 | 0 | 0 | +32.3% (15min 0.5% tp1% semstop semage, 313 tr) | +56.8% |
| 3C QFL | US100 | 45 | 36 | 2 | 0 | +13.8% (30min 0.5% tp3% semstop age10, 52 tr) | +20.3% |
| 3C QFL | WTI | 44 | 0 | 0 | 0 | +2.6% (1D 2.0% tp1% sl5% age10, 31 tr) | +5.4% |
| 3C QFL | XAU | 44 | 19 | 0 | 0 | +3.6% (1h 2.0% tp3% semstop age10, 21 tr) | +13.4% |
| Follow Line | BTC | 39 | 37 | 3 | 3 | +53.6% (4h 50 2.0 ambos, 98 tr) | +43.8% |
| Follow Line | ETH | 39 | 39 | 5 | 15 | +119.9% (4h 50 2.0 ambos, 94 tr) | +56.8% |
| Follow Line | US100 | 38 | 34 | 4 | 0 | +14.5% (30min 21 1.0 long, 1003 tr) | +20.3% |
| Follow Line | WTI | 40 | 10 | 0 | 3 | +22.8% (30min 50 1.0 ambos, 1760 tr) | +5.4% |
| Follow Line | XAU | 38 | 36 | 7 | 1 | +13.9% (30min 21 2.0 ambos, 788 tr) | +13.4% |
| MACD + ATR stop | BTC | 39 | 39 | 0 | 4 | +64.8% (30min m2.2 tp5% filtro, 1872 tr) | +43.8% |
| MACD + ATR stop | ETH | 39 | 38 | 2 | 7 | +80.2% (30min m2.2 tp5% filtro, 2122 tr) | +56.8% |
| MACD + ATR stop | US100 | 39 | 39 | 0 | 0 | +16.9% (1h m4.0 semtp filtro, 346 tr) | +20.3% |
| MACD + ATR stop | WTI | 39 | 0 | 0 | 0 | -21.9% (30min m2.2 semtp filtro, 1843 tr) | +5.4% |
| MACD + ATR stop | XAU | 39 | 18 | 0 | 0 | +5.1% (1D m4.0 tp5% semfiltro, 38 tr) | +13.4% |
| 3x SuperTrend | BTC | 40 | 29 | 1 | 0 | +41.5% (15min pl1.5 thr20 ambos, 2573 tr) | +43.8% |
| 3x SuperTrend | ETH | 40 | 27 | 0 | 0 | +37.5% (15min pl3.0 thr20 long, 1211 tr) | +56.8% |
| 3x SuperTrend | US100 | 40 | 25 | 1 | 0 | +5.7% (15min pl3.0 thr30 long, 1181 tr) | +20.3% |
| 3x SuperTrend | WTI | 40 | 18 | 0 | 1 | +26.1% (1D pl3.0 thr30 ambos, 22 tr) | +5.4% |
| 3x SuperTrend | XAU | 40 | 25 | 4 | 0 | +7.5% (15min pl3.0 thr20 ambos, 1586 tr) | +13.4% |
| RSI T3 + SAR | BTC | 20 | 20 | 3 | 1 | +50.2% (30min stop10 ambos, 1706 tr) | +43.8% |
| RSI T3 + SAR | ETH | 20 | 20 | 2 | 0 | +56.7% (30min semstop long, 1291 tr) | +56.8% |
| RSI T3 + SAR | US100 | 20 | 18 | 0 | 0 | +6.9% (30min semstop long, 1020 tr) | +20.3% |
| RSI T3 + SAR | WTI | 20 | 4 | 0 | 1 | +23.7% (1D semstop ambos, 25 tr) | +5.4% |
| RSI T3 + SAR | XAU | 20 | 17 | 2 | 0 | +10.1% (30min stop10 ambos, 1231 tr) | +13.4% |
| Moving Regression Band | BTC | 40 | 30 | 0 | 3 | +52.7% (1h 40 g2 m1 lower-atr ambos, 2217 tr) | +43.8% |
| Moving Regression Band | ETH | 40 | 34 | 1 | 5 | +77.2% (1h 40 g2 m1 lower-atr ambos, 2228 tr) | +56.8% |
| Moving Regression Band | US100 | 40 | 30 | 2 | 0 | +16.9% (30min 80 g2 m2 lower-atr ambos, 1749 tr) | +20.3% |
| Moving Regression Band | WTI | 40 | 4 | 0 | 2 | +11.5% (1h 80 g2 m2 central ambos, 2182 tr) | +5.4% |
| Moving Regression Band | XAU | 40 | 14 | 1 | 0 | +7.9% (4h 80 g2 m2 central ambos, 447 tr) | +13.4% |
| Double AI SuperTrend | BTC | 20 | 20 | 0 | 0 | +41.2% (4h 4/3 ambos, 160 tr) | +43.8% |
| Double AI SuperTrend | ETH | 20 | 20 | 3 | 5 | +71.6% (15min 4/3 ambos, 2482 tr) | +56.8% |
| Double AI SuperTrend | US100 | 20 | 18 | 4 | 0 | +14.5% (15min 4/3 long, 1205 tr) | +20.3% |
| Double AI SuperTrend | WTI | 20 | 8 | 0 | 5 | +11.3% (30min 4/3 ambos, 1554 tr) | +5.4% |
| Double AI SuperTrend | XAU | 20 | 19 | 3 | 0 | +9.6% (15min 4/3 ambos, 2130 tr) | +13.4% |
| RSI/ATR Trend Reversal | BTC | 40 | 39 | 1 | 2 | +49.7% (1D 14 3.0 normal ambos, 163 tr) | +43.8% |
| RSI/ATR Trend Reversal | ETH | 40 | 40 | 0 | 8 | +85.8% (1D 14 3.0 ha ambos, 169 tr) | +56.8% |
| RSI/ATR Trend Reversal | US100 | 40 | 33 | 0 | 0 | +11.7% (1D 8 1.5 ha long, 59 tr) | +20.3% |
| RSI/ATR Trend Reversal | WTI | 40 | 16 | 0 | 7 | +18.6% (1D 14 3.0 ha ambos, 126 tr) | +5.4% |
| RSI/ATR Trend Reversal | XAU | 40 | 32 | 2 | 1 | +14.1% (30min 8 1.5 ha ambos, 392 tr) | +13.4% |
| Alligator HA | BTC | 20 | 9 | 0 | 0 | +31.8% (1D normal long, 81 tr) | +43.8% |
| Alligator HA | ETH | 20 | 15 | 0 | 0 | +36.4% (1h ha ambos, 4674 tr) | +56.8% |
| Alligator HA | US100 | 20 | 12 | 1 | 0 | +8.7% (1D ha long, 101 tr) | +20.3% |
| Alligator HA | WTI | 20 | 0 | 0 | 0 | -3.4% (1D ha ambos, 183 tr) | +5.4% |
| Alligator HA | XAU | 20 | 10 | 3 | 0 | +5.8% (1h normal ambos, 2843 tr) | +13.4% |
| Camarilla H4/L4 | BTC | 24 | 24 | 12 | 0 | +38.0% (1h sl1% tp2% ambos, 1632 tr) | +43.8% |
| Camarilla H4/L4 | ETH | 24 | 24 | 12 | 0 | +49.3% (4h sl2.0% tp6% ambos, 1075 tr) | +56.8% |
| Camarilla H4/L4 | US100 | 24 | 24 | 9 | 0 | +16.6% (15min sl2.0% tp6% ambos, 832 tr) | +20.3% |
| Camarilla H4/L4 | WTI | 24 | 10 | 0 | 3 | +9.5% (4h sl2.0% tp6% ambos, 869 tr) | +5.4% |
| Camarilla H4/L4 | XAU | 24 | 23 | 4 | 0 | +11.3% (4h sl2.0% tp6% ambos, 687 tr) | +13.4% |
| Nadaraya-Watson | BTC | 40 | 23 | 0 | 6 | +66.6% (1D 8 x10 ambos, 210 tr) | +43.8% |
| Nadaraya-Watson | ETH | 40 | 21 | 0 | 0 | +53.3% (1D 8 x10 ambos, 200 tr) | +56.8% |
| Nadaraya-Watson | US100 | 40 | 16 | 1 | 0 | +12.1% (1D 20 x10 long, 58 tr) | +20.3% |
| Nadaraya-Watson | WTI | 40 | 8 | 0 | 4 | +23.8% (1D 8 x10 ambos, 229 tr) | +5.4% |
| Nadaraya-Watson | XAU | 40 | 2 | 0 | 0 | -0.2% (1D 20 x10 long, 66 tr) | +13.4% |
| Extreme Scalping | BTC | 60 | 0 | 0 | 6 | +64.0% (15min gap0.25% rr3 ambos, 51590 tr) | +43.8% |
| Extreme Scalping | ETH | 60 | 2 | 0 | 2 | +82.7% (1h gap0.5% rr3 ambos, 18804 tr) | +56.8% |
| Extreme Scalping | US100 | 60 | 10 | 5 | 0 | +9.2% (1D gap1.00% rr3 long, 369 tr) | +20.3% |
| Extreme Scalping | WTI | 60 | 4 | 1 | 8 | +15.2% (1h gap1.00% rr1 ambos, 3221 tr) | +5.4% |
| Extreme Scalping | XAU | 60 | 7 | 1 | 0 | +2.0% (1D gap1.00% rr1 ambos, 511 tr) | +13.4% |
| Y-PMax | BTC | 40 | 39 | 3 | 6 | +70.6% (30min 30 2 ambos, 2275 tr) | +43.8% |
| Y-PMax | ETH | 40 | 40 | 9 | 15 | +133.3% (30min 13 2 ambos, 3287 tr) | +56.8% |
| Y-PMax | US100 | 40 | 34 | 7 | 0 | +13.1% (30min 13 3 long, 972 tr) | +20.3% |
| Y-PMax | WTI | 40 | 16 | 0 | 6 | +19.9% (1D 13 3 ambos, 51 tr) | +5.4% |
| Y-PMax | XAU | 40 | 37 | 4 | 0 | +11.1% (30min 30 2 ambos, 1862 tr) | +13.4% |
| PMARP + Madrid | BTC | 30 | 29 | 3 | 0 | +34.5% (15min tp1% sl27.75% long, 724 tr) | +43.8% |
| PMARP + Madrid | ETH | 30 | 22 | 2 | 3 | +93.5% (15min tp1% sl27.75% ambos, 6549 tr) | +56.8% |
| PMARP + Madrid | US100 | 30 | 25 | 0 | 0 | +13.8% (15min tp1% sl27.75% long, 235 tr) | +20.3% |
| PMARP + Madrid | WTI | 30 | 11 | 0 | 13 | +17.4% (4h tp1% sl27.75% ambos, 839 tr) | +5.4% |
| PMARP + Madrid | XAU | 30 | 26 | 1 | 0 | +7.1% (30min tp3% sl3% ambos, 630 tr) | +13.4% |
| ATR GOD | BTC | 36 | 26 | 1 | 0 | +14.9% (30min sl4.5 rr1.5 filtros long, 216 tr) | +43.8% |
| ATR GOD | ETH | 36 | 27 | 1 | 0 | +48.0% (4h sl4.5 rr1.5 semfiltros ambos, 112 tr) | +56.8% |
| ATR GOD | US100 | 36 | 35 | 4 | 0 | +7.0% (1h sl4.5 rr1.5 semfiltros long, 208 tr) | +20.3% |
| ATR GOD | WTI | 36 | 14 | 0 | 6 | +20.5% (1D sl2.0 rr2.0 semfiltros ambos, 32 tr) | +5.4% |
| ATR GOD | XAU | 36 | 28 | 6 | 0 | +8.7% (4h sl4.5 rr1.5 semfiltros ambos, 94 tr) | +13.4% |
| [DS] EMA8 x DEMA34 | BTC | 30 | 29 | 3 | 3 | +67.2% (30min 8/72 ambos, 3718 tr) | +43.8% |
| [DS] EMA8 x DEMA34 | ETH | 30 | 29 | 5 | 7 | +101.3% (30min 17/72 ambos, 2606 tr) | +56.8% |
| [DS] EMA8 x DEMA34 | US100 | 30 | 23 | 4 | 0 | +10.9% (1h 8/72 long, 719 tr) | +20.3% |
| [DS] EMA8 x DEMA34 | WTI | 30 | 10 | 1 | 7 | +25.7% (30min 17/72 ambos, 2505 tr) | +5.4% |
| [DS] EMA8 x DEMA34 | XAU | 30 | 14 | 2 | 0 | +12.0% (1h 8/72 ambos, 1405 tr) | +13.4% |
| FRAMA | BTC | 26 | 15 | 0 | 0 | +21.9% (4h 12 propriotf long, 369 tr) | +43.9% |
| FRAMA | ETH | 23 | 19 | 0 | 1 | +63.8% (1D 12 propriotf ambos, 127 tr) | +56.8% |
| FRAMA | US100 | 26 | 17 | 0 | 0 | +8.2% (1D 12 semanal long, 14 tr) | +20.3% |
| FRAMA | WTI | 26 | 6 | 0 | 5 | +19.6% (1D 12 semanal ambos, 30 tr) | +5.4% |
| FRAMA | XAU | 26 | 14 | 1 | 0 | +10.5% (1h 40 propriotf ambos, 2558 tr) | +13.4% |

## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **Follow Line ETH 30m (21, 1 desvio, long e short)** | +118% vs +57% (t 3,1) | +403% vs +330% | +18% vs +1% | +60% vs −11% | +35% vs +13% | +98% (t 2,5) | **aprovada** |
| Follow Line ETH 4h (50, 2 desvios) | +120% (t 2,3) | +226% vs +328% | +7% vs 0% | +104% vs −11% | +64% vs +13% | +119% | quase (terço 1; 94 trades) |
| Y-PMax ETH 15m (30, 3, long e short) | +122% (t 2,7) | +193% vs +330% | +79% | +100% | +81% vs +13% | +92% | quase (terço 1) |
| Y-PMax ETH 30m (13, 2) | +133% (t 2,5) | +218% vs +330% | +66% | +132% | +81% | +102% | quase (terço 1) |
| ATR Trailing ceyhun ETH 4h (m2 5) | +103% (t 1,7) | +200% vs +328% | +53% | +65% | +43% vs +13% | +102% | quase (terço 1) |
| [DS] EMA8 × DEMA34 ETH 30m (17/72) | +101% (t 3,5) | +225% vs +330% | +161% | **−11% vs −11%** | +19% vs +13% | +79% | reprovada |
| PMARP + Madrid ETH 15m | +94% (t 3,0) | +312% vs +330% | +44% | +22% | **+6% vs +13%** | +67% | reprovada |
| [DS] BTC 30m (8/72) | +67% vs +44% (t 2,6) | +257% vs +130% | +35% vs +15% | **−4% vs +13%** | +8% vs +40% | +42% | reprovada |
| MACD + ATR stop BTC 30m (TP 5%) | +65% (t 1,6) | +255% | +23% | **+2% vs +13%** | +21% vs +40% | +52% | reprovada |
| Y-PMax BTC 30m (30, 3) | +53% (t 3,3) | +76% vs +130% | +62% | +18% | +39% vs +40% | +43% | reprovada |
| ceyhun BTC 4h / [DS] BTC 1D | +65% / +59% | ~empate | ganha | ganha | +25% / +30% vs +40% | +63% / +58% | reprovadas (2ª metade) |
| [DS] WTI 1h (8/34) | +23% vs +5% (t 1,9) | ganha | ganha | +8% vs +8% | +9% vs +3% | **+4,7% vs +5,4%** | reprovada (custo) |
| Nadaraya-Watson WTI 1D | +22% (t 2,0) | ganha | **+15% vs +32%** | −7% vs +8% | −12% | +21% | reprovada |
| ATR GOD WTI 1D (sem filtros) | +20,5% (32 trades) | ganha | **+1% vs +32%** | ganha | ganha | +20% | reprovada (poucos trades) |
| RSI/ATR Reversal XAU 30m / Follow Line XAU 30m | +14% vs +13% | perde | ganha/perde | ganha/perde | — | abaixo | reprovadas |

## Conclusões

- **Follow Line no ETH 30m (EMA21 ± 1 desvio, ATR5, long e short)** passa em tudo: ganha do B&H nos três terços (inclusive no bull de 2020-22: +403% vs +330%), na 2ª metade (+35% vs +13%) e com custo 4× (+98%). A vizinhança no ETH é boa (15m 21/1, 15m 50/1, 4h 50/2 e 1h 50/1 acima do B&H). Ressalvas: DD −64% (−1,03 em log); é mais um seguidor de tendência no ETH, da mesma família das candidatas 2 a 5 de APROVADAS.
- Y-PMax, ceyhun e Follow Line 4h no ETH repetem o padrão "quase": perdem só o terço 1.
- No BTC nada passa: os seguidores de tendência ganham muito em 2020-22 e morrem em 2024-26.
- WTI: [DS] 1h e Nadaraya-Watson 1D batem o B&H no total, mas um falha com custo 4× e o outro em 2020-23.
- XAU e US100: nada acima do B&H com robustez. QFL, 3x SuperTrend, T3+SAR, Alligator, Camarilla, Extreme Scalping e World Cycle não chegam perto em nenhum ativo.
