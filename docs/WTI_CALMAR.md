# WTI: ranking pelo índice de Calmar antes do OOS

Calmar = CAGR / |drawdown máximo| da equity diária de 2017-01-03 a 2024-10-19 (sem partes, sem filtro); melhor célula de cada estratégia pelo Calmar; trades abertos em abril de 2020 descartados; templates fora.

| # | Lote | Est | Nome | Célula | Calmar | Total | Trades |
|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 2/2 | 2.27 | +16523% | 47452 |
| 2 | 25 | nr7s | 46. NR7ID (short-only) | 1D sma14 | 1.55 | +34% | 24 |
| 3 | 12 | pt | 2. Powertrend (range filter de volume, 200, long-only) | 15min l50 m1.5 vol | 1.22 | +11% | 16 |
| 4 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 1D SHORT p1 m3.0 sl5.0 | 1.20 | +682% | 88 |
| 5 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.05 roc6.0 m3.0/3.0 ambos | 1.08 | +930% | 304 |
| 6 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 30min como escrito ambos | 1.07 | +1079% | 437 |
| 7 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 ambos | 0.93 | +183% | 296 |
| 8 | 22 | ewo | 3. EWO RSI Exhaustion | 1D vol ambos | 0.88 | +1079% | 12 |
| 9 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 4h r14 w30 d3 signal ambos | 0.84 | +1137% | 1651 |
| 10 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 30min fiel ambos | 0.81 | +592% | 746 |
| 11 | ichimoku | ichimoku |  | 15min | 0.77 | +468% | 560 |
| 12 | 25 | tlb | 42. Trendline Breakout KedArc | 4h p5 semma ambos | 0.75 | +382% | 698 |
| 13 | 22 | tdon | 9. Turtle Donchian/ATR | 4h 20/10 m4 short | 0.73 | +220% | 211 |
| 14 | 5 | pvb | 1. Price and Volume Breakout (60/60/200, so long) | 1h 20/50 x5 vol1 ls | 0.66 | +240% | 625 |
| 15 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 4h sl1% rr5 ambos | 0.65 | +120% | 460 |
| 16 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w140 -94/-6 sl0.005 contrario ambos | 0.63 | +509% | 2433 |
| 17 | 28 | l2r | 11. L2 Reversal Labels | 30min semtpsl ambos | 0.61 | +654% | 545 |
| 18 | 29 | bot | 14. BotBot | 1D k0.04 ambos | 0.57 | +509% | 32 |
| 19 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 30min f10 one tp5.0 | 0.57 | +288% | 1268 |
| 20 | 33 | pst | 8. Parabolic SAR stop entries | 1h af0.02 ambos | 0.57 | +488% | 2731 |
| 21 | 19 | cipher | 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11) | 1h wt tp4 sl2 ambos | 0.56 | +22% | 46 |
| 22 | 23 | crazy | 10. Crazy Scalping (TMO + AMA) | 1h sl10 ambos | 0.55 | +159% | 387 |
| 23 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 1D l20 e40 ambos | 0.53 | +340% | 52 |
| 24 | 5 | qqe |  | 1D b60 x30 s90 sw20 wae1 lucro1 | 0.53 | +254% | 74 |
| 25 | 20 | atrgod |  | 4h sl4.5 rr1.5 semfiltros ambos | 0.52 | +241% | 118 |
| 26 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 1D m2.7 normal tp0.47 sl0.21 | 0.52 | +268% | 76 |
| 27 | 8 | eng | 4. Engulfing + SMA32 | 30min ma64 sl0.005 tp0.05 ambos | 0.51 | +189% | 4120 |
| 28 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 15min sl0% tp35% filtros ambos | 0.51 | +359% | 1222 |
| 29 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 1h 100/50/7 ambos | 0.48 | +421% | 2076 |
| 30 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 30min sw20 sl8atr tp0% ambos | 0.46 | +149% | 2002 |
| 31 | 30 | rdi | 5. RSI Divergence x Ichimoku x 200EMA | 4h lb5 ambos | 0.46 | +195% | 146 |
| 32 | 26 | csq | 3. Crypto Squeeze | 1D mfi14 ambos | 0.45 | +406% | 58 |
| 33 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 1h sl0.0025 rr2.0 eod1 filt1 long | 0.44 | +7% | 161 |
| 34 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 15min p3 rr5.0 trend1 long | 0.44 | +30% | 616 |
| 35 | 27 | spk | 14. Martin Pring's Special K | 1D s30 ambos | 0.43 | +313% | 47 |
| 36 | 21 | mtfrsi | 20. Multi Timeframe RSI | 4h 1/3/6 30/70 ambos | 0.42 | +283% | 18 |
| 37 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 4h l50 m1.5 sl0.002 long | 0.42 | +24% | 157 |
| 38 | 34 | khw | 10. Kahlman HullMA / WT Cross | 1h h48 sem wt ambos | 0.41 | +327% | 2972 |
| 39 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 1D lb10 pb5 tp2.0 sl1.0 | 0.40 | +49% | 312 |
| 40 | 21 | sqz | 2. Squeeze Momentum | 4h l2 sl0.5% tp1% semsqz ambos | 0.39 | +43% | 1194 |
| 41 | 29 | r2m | 9. RSI2 + medias (pullback) | 4h 5/95 ambos | 0.39 | +73% | 306 |
| 42 | 32 | srs | 17. Supertrend + RSI (Alorse) | 1D f3 ambos | 0.39 | +190% | 59 |
| 43 | 24 | srvi | 7. Stochastic RSI + RVI | 4h p10 30/70 ambos | 0.39 | +235% | 359 |
| 44 | 16 | qqe | 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao) | 1h XZ f5 dfil ambos | 0.38 | +159% | 1005 |
| 45 | 20 | 3st |  | 1D pl3.0 thr30 ambos | 0.38 | +183% | 22 |
| 46 | 25 | sta | 38. Stoch + ATR | 4h 14 ambos | 0.38 | +267% | 1040 |
| 47 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 1h n30 5/20 | 0.38 | +228% | 2480 |
| 48 | 34 | azl | 7. Adaptive Zero Lag EMA | 4h cos thr0 ambos | 0.37 | +251% | 1512 |
| 49 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 15min rr1.0 vol sess ambos | 0.37 | +74% | 1163 |
| 50 | 36 | kel | 12. Keltner SL/TP | 1D k1/sl20 ambos | 0.37 | +200% | 87 |
| 51 | 30 | hms | 20. Harmonic System | 4h close ambos | 0.37 | +288% | 1791 |
| 52 | 33 | szs | 19. Stochastic Z-Score (TradeDots) | 1D z2 ambos | 0.37 | +255% | 39 |
| 53 | 22 | tst | 18. Triple SuperTrend + StochRSI | 1D 28/78 rr2.0/1.5 ambos | 0.37 | +367% | 19 |
| 54 | 31 | lch | 5. Linear Channel (long-only) | 15min v2% hma200 | 0.36 | +34% | 58 |
| 55 | 6 | hs | 1. Hammers & Stars (stop 1 ATR, alvo 1R) | 4h s0.5 rr1.0 fib0.25 ema50 | 0.36 | +54% | 313 |
| 56 | 37 | chk | 18. Chaloke System | 4h 20/50/100 ambos | 0.36 | +254% | 257 |
| 57 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 4h r8 m34 rev ambos | 0.35 | +334% | 316 |
| 58 | 36 | mma | 15. Multi Moving Average Crossing | 30min 5/20/50 ambos | 0.34 | +126% | 2485 |
| 59 | zigzagpa | grade |  | 1h ew0.0 tp1.618 sl-1.0 | 0.34 | +28% | 89 |
| 60 | 34 | zlm | 6. Zero-Lag MA Trend Following | 1D rr2 ambos | 0.34 | +148% | 41 |
| 61 | 21 | hulk | 5. Hulk Scalper | 30min thr0.3 adx33 tp3.00% sl2.0% ambos | 0.34 | +44% | 188 |
| 62 | 26 | pprs | 16. Pivot Point Reversal + RSI | 30min pv3/3 ambos | 0.33 | +225% | 5960 |
| 63 | 31 | psw | 8. Swing Parabolic SAR | 4h af0.02 ambos | 0.33 | +206% | 1280 |
| 64 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 15min r0.5 rr3.0 ret00 | 0.33 | +53% | 1900 |
| 65 | 9 | micu | 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips) | 4h sl0.0025 tp0 trail0 sess1 ambos | 0.33 | +105% | 1428 |
| 66 | 27 | obv | 20. OBV Oscillator | 1h l50 ambos | 0.33 | +235% | 1891 |
| 67 | 25 | cmo | 6. CMO TradeDots | 4h 40 ambos | 0.32 | +269% | 243 |
| 68 | 25 | rtb | 47. Reversal Trading Bot | 1h sl1 tp2 ambos | 0.32 | +124% | 2052 |
| 69 | 30 | sich | 11. SuperIchi | 1D rr3 ambos | 0.31 | +125% | 14 |
| 70 | 25 | opw | 37. TASC One Percent A Week (long-only) | 1h dip1 tp1 | 0.30 | +62% | 406 |
| 71 | 21 | kb | 15. Keltner bounce (SMA200 +- 8 ATR) | 1h 200 d3 ambos | 0.30 | +176% | 285 |
| 72 | 33 | tbn | 7. Trend Bounce | 4h c7 ambos | 0.30 | +92% | 499 |
| 73 | 24 | dcf | 9. Donchian free bot | 1h semtp ambos | 0.30 | +90% | 4540 |
| 74 | 25 | dax | 10. DAX Shooter | 1D adx32 ambos | 0.29 | +228% | 10 |
| 75 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 4h e200 tp/sl sim2 ambos | 0.29 | +98% | 344 |
| 76 | 29 | lrcb | 12. Linear Regression Channel Breakout | 1D dv2.3 ambos | 0.29 | +52% | 49 |
| 77 | 25 | ht3 | 36. Swing HULL + T3 | 4h 100 sltp ambos | 0.29 | +181% | 764 |
| 78 | 11 | grab | 4. Grab Trading System (80/21) | 4h 80/21 stop | 0.28 | +108% | 267 |
| 79 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 1h 50 rev ambos | 0.28 | +154% | 201 |
| 80 | 20 | cam |  | 4h sl2.0% tp6% ambos | 0.27 | +131% | 857 |
| 81 | 22 | force | 17. Force trade scalper | 1D 3/20 ambos | 0.27 | +349% | 55 |
| 82 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 4h sl2.00% sessao ambos | 0.27 | +104% | 1016 |
| 83 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 4h k3.0 sl3.0 be0.75 tp3.0 ema0 ambos | 0.27 | +101% | 436 |
| 84 | 33 | dst | 17. Dual Supertrend with MACD | 1h 3/5 ambos | 0.26 | +96% | 2192 |
| 85 | 15 | comb | 2. Combined Strategy (fita de EMAs + RSI + Stoch) | 4h osc ambos | 0.26 | +135% | 725 |
| 86 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 1h TILL 12/26/9 | 0.25 | +156% | 2897 |
| 87 | 23 | e3r | 3. 3 EMA + RSI | 4h sl0% x0 ambos | 0.24 | +72% | 135 |
| 88 | 33 | bct | 3. Bar Counter Trend Reversal | 4h kc2 ambos | 0.24 | +207% | 222 |
| 89 | 36 | cbo | 19. Candle Breakout 13h UTC | 15min h13/rr2 ambos | 0.23 | +81% | 2237 |
| 90 | 31 | seq | 7. Sequence Snap | 1D rr1 ambos | 0.23 | +76% | 21 |
| 91 | 29 | cez | 4. Chandelier Exit + ZLSMA | 15min m2 ambos | 0.23 | +48% | 1978 |
| 92 | 22 | tsi | 5. TSI CCI Hull | 15min tp0.0% ambos | 0.23 | +111% | 2670 |
| 93 | 31 | vip | 19. VIP (long-only) | 1h tp1% sl1% | 0.22 | +20% | 210 |
| 94 | 25 | dbt | 44. Double Bottom/Top Hunter | 30min 30 ambos | 0.21 | +230% | 340 |
| 95 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 30min atr10x4.0 | 0.21 | +93% | 2225 |
| 96 | 36 | sms | 9. Super Momentum | 30min cmo14 ambos | 0.21 | +131% | 466 |
| 97 | 19 | 3ema | 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only) | 4h tp3 sl0 | 0.21 | +37% | 126 |
| 98 | 32 | tfp | 19. Trend Following Parabolic (TradeDots) | 1h rr1.3 ambos | 0.21 | +138% | 477 |
| 99 | 22 | apsar | 7. ATR Parabolic SAR | 30min n1 0.01/0.1 ambos | 0.21 | +109% | 904 |
| 100 | 23 | mabb | 9. MA BB + RSI | 15min a9 vol ambos | 0.20 | +64% | 442 |
| 101 | 24 | ectp | 19. EMA Crossover with TP | 1D sl3% tp0.5 ambos | 0.20 | +25% | 49 |
| 102 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR80 p0.5 c0.005 | 0.19 | +163% | 24 |
| 103 | 24 | mbit | 3. Mbit MA (contrario) | 30min ma520 n10 ambos | 0.19 | +128% | 462 |
| 104 | 18 | osb | 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario) | 30min m0.25 sl1.00% ambos | 0.18 | +75% | 1494 |
| 105 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 1h a3.0 atr11 hma2 ambos | 0.18 | +90% | 1214 |
| 106 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 1h 12/26/9 ambos | 0.18 | +110% | 4610 |
| 107 | 31 | mdb | 16. Market Dynamics HH/LL breakout | 1D lb50 long | 0.18 | +7% | 10 |
| 108 | 24 | tq | 4. Triple EMA + QQE | 4h p1% ambos | 0.17 | +31% | 233 |
| 109 | 22 | pmax | 16. PMax on RSI w T3 | 15min m3 t8 ambos | 0.17 | +126% | 2416 |
| 110 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 1D bb20 2.0 sl2.0% tp2.0% ambos | 0.17 | +15% | 43 |
| 111 | 22 | bbra | 1. BB + RSI + ADX | 1D sl0.0% adx100 ambos | 0.17 | +63% | 24 |
| 112 | 32 | r2 | 7. AK RSI 2 | 1D 5/90 long | 0.17 | +5% | 23 |
| 113 | 29 | rss | 10. RSI and SMA (Coinrule) | 15min 50/100 ambos | 0.17 | +81% | 1502 |
| 114 | 23 | twin | 1. Twin Range Filter | 1D sematr t0 sltp ambos | 0.17 | +125% | 156 |
| 115 | 37 | mrs | 5. Mean-Reversion Swing | 30min n20 long | 0.17 | +18% | 480 |
| 116 | 20 | madrid |  | 4h tp6% sl3% ambos | 0.17 | +60% | 418 |
| 117 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 15min bb20 3 semlatest ambos | 0.16 | +78% | 412 |
| 118 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 30min 12 2 ambos | 0.16 | +76% | 1511 |
| 119 | 32 | hme | 5. HMA 200 + EMA 20 | 1h hma200 ambos | 0.16 | +116% | 1188 |
| 120 | 32 | qst | 8. QuantNomad SuperTrend | 1D m3 ambos | 0.16 | +56% | 63 |
| 121 | 13 | sqz | 4. Squeeze Momentum [LazyBear] (BB14x2, KC16x1,5) | 4h bb20 kc16 ambos | 0.16 | +49% | 444 |
| 122 | 21 | rbin | 17. RSI Binary (6, 13/82, 3 barras) | 1D 14 30/70 h3 ambos | 0.16 | +31% | 70 |
| 123 | 28 | hapa | 10. Heikin Ashi Price Action | 1D velas ambos | 0.16 | +112% | 319 |
| 124 | 37 | wmx | 15. WMX Williams Fractals | 4h o3 ambos | 0.15 | +75% | 1059 |
| 125 | 27 | tch | 5. TSI CCI Hull | 15min p25 ambos | 0.15 | +85% | 2655 |
| 126 | 24 | smc | 8. SMC | 30min lb30 ambos | 0.15 | +90% | 1200 |
| 127 | 31 | ten | 12. Tendency EMA + RSI | 4h x24 ambos | 0.15 | +40% | 155 |
| 128 | 29 | adxb | 15. Rob Booker ADX Breakout | 1h adx25 ambos | 0.15 | +59% | 1400 |
| 129 | 30 | dip | 15. Scalping Dips On Trend (long-only) | 30min d4 tp6% | 0.15 | +22% | 19 |
| 130 | 20 | ds |  | 1h 8/34 ambos | 0.15 | +68% | 2633 |
| 131 | 34 | fmv | 4. FlexiMA Variance Tracker | 1D f8 ambos | 0.15 | +64% | 51 |
| 132 | 33 | stc | 10. SuperTrend chandelier 7/7 | 4h m7 ambos | 0.15 | +90% | 109 |
| 133 | 6 | bbrsi | 3. Bollinger Band with RSI (piramide 50 x 10% do capital) | 1h 20/60 bb2.5 u1 | 0.14 | +29% | 77 |
| 134 | 31 | pse | 17. Parabolic SAR w/ EMA | 4h off1% ambos | 0.14 | +54% | 373 |
| 135 | 28 | sbf | 1. Stochastic (BiznesFilosof) | 4h 14/86 ambos | 0.14 | +141% | 140 |
| 136 | 18 | slope | 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200) | 1h 130 9/21 filtro ambos | 0.14 | +55% | 1813 |
| 137 | 20 | nw |  | 1D 8 x25 ambos | 0.14 | +76% | 213 |
| 138 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 1h trig3 sl0.02 ambos | 0.14 | +38% | 132 |
| 139 | 36 | kbb | 2. Kozlod BB | 1h bb55x2 ambos | 0.14 | +75% | 561 |
| 140 | 36 | lrb | 13. Linear Regression Channel Breakout | 4h n50 ambos | 0.13 | +51% | 1378 |
| 141 | 24 | best | 2. BEST Supertrend | 4h m3 ambos | 0.13 | +46% | 466 |
| 142 | 15 | es | 4. EMA STOCH (Crypto BOT lower timeframes) | 30min sl/tp1% long | 0.13 | +3% | 46 |
| 143 | 25 | grov | 28. Grover Llorens Activator | 30min 100 m5 ambos | 0.13 | +76% | 3364 |
| 144 | 24 | sott | 1. SOTT | 4h s250 p0.618 ambos | 0.13 | +78% | 102 |
| 145 | 25 | hyb | 17. Hybrid RSI + Breakout | 30min atr2 ambos | 0.13 | +60% | 3383 |
| 146 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 1h r10 m100 ambos | 0.12 | +67% | 578 |
| 147 | 31 | fxf | 14. FXFUNDINGMATE Trend | 4h tp1atr ambos | 0.12 | +21% | 306 |
| 148 | 25 | fbo | 43. Fractal Breakout | 4h ambos | 0.12 | +40% | 575 |
| 149 | 31 | alm | 1. ALMA/EMA | 4h tp6% ambos | 0.12 | +27% | 91 |
| 150 | 26 | bx | 6. B-Xtrender | 1h trl20% ambos | 0.12 | +53% | 2392 |
| 151 | 22 | mab | 11. Moving Average Band | 1h 100 rr3 ambos | 0.12 | +69% | 1716 |
| 152 | 10 | pdiv | 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2) | 15min q3 m50 reg sl0.0 ambos | 0.11 | +18% | 599 |
| 153 | 10 | aio | 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR) | 1h rsi1 atr1.0 rr2.0 long | 0.11 | +20% | 259 |
| 154 | 24 | gap | 10. Gap Filling | 1h semalvo ambos | 0.11 | +34% | 944 |
| 155 | 23 | dema | 8. DEMA ATR | 1h tp6 ambos | 0.11 | +51% | 673 |
| 156 | 17 | stcci | 1. Supertrend CCI (sinal do CCI28) | 1D cci28 ambos | 0.11 | +50% | 245 |
| 157 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 1D hon DEMA13 x1 | 0.11 | +71% | 478 |
| 158 | 28 | hamacd | 17. Heikin Ashi MACD | 1D tp10 sl3 ambos | 0.11 | +55% | 162 |
| 159 | 20 | t3sar |  | 1D semstop ambos | 0.11 | +54% | 24 |
| 160 | 21 | cons | 3. MA Consecutive Up/Down | 4h n8 ma1 ambos | 0.11 | +19% | 25 |
| 161 | 30 | kal | 12. KALKI TFXBOT | 1h rr1.5 ambos | 0.11 | +21% | 873 |
| 162 | 18 | tdi | 1. Traders Dynamic Index (forca 1-2) | 30min str1 ambos | 0.10 | +73% | 4504 |
| 163 | 24 | stb | 5. SuperTrend Backtester | 1D semtp ambos | 0.10 | +23% | 61 |
| 164 | 37 | hul | 7. Hull Suite | 1D n55 ambos | 0.10 | +65% | 103 |
| 165 | 25 | gn | 41. Gianno Nano | 1D sltp ambos | 0.10 | +45% | 65 |
| 166 | 25 | ffe | 15. Forex Fractal EMA Scalper | 1D tp2.0% direto ambos | 0.10 | +28% | 266 |
| 167 | 26 | kha | 17. Kozlod Heikin-Ashi | 4h k2 ambos | 0.10 | +41% | 2194 |
| 168 | 36 | sre | 1. Stoch RSI Crossover + EMA | 1h tp3/sl2 ambos | 0.10 | +17% | 133 |
| 169 | 25 | pop | 22. Pivot of Pivot Reversal | 4h 4/2 ambos | 0.10 | +51% | 151 |
| 170 | 32 | usc | 3. Ultimate Scalping v2 (EMA + VWAP) | 1D tp3atr ambos | 0.09 | +26% | 82 |
| 171 | 9 | hull | 4. Hull Swing Trader (HMA 210 do open) | 4h p400 ambos | 0.09 | +38% | 161 |
| 172 | 37 | rvc | 13. Reversal Catcher | 4h bb1.5 long | 0.09 | +13% | 25 |
| 173 | 32 | hfl | 1. Hurst Future Lines of Demarcation | 1h c20 ambos | 0.09 | +38% | 1590 |
| 174 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 4h len20 m2.0 ambos | 0.09 | +28% | 309 |
| 175 | 28 | sflip | 5. Bitcoin SuperFlip | 4h f1.8 ambos | 0.09 | +26% | 427 |
| 176 | 34 | mtl | 2. Market Trend Levels | 15min 12/25 adx20 ambos | 0.09 | +47% | 2359 |
| 177 | 37 | dmm | 6. DMI Modified | 1D n9 ambos | 0.09 | +33% | 73 |
| 178 | 23 | qqe | 7. UL QQE Cross | 4h thr5 semfiltro ambos | 0.09 | +34% | 1175 |
| 179 | 21 | bbb | 11. Bollinger Bands Breakout | 4h bb40 vol sl2% tp9% ambos | 0.09 | +48% | 300 |
| 180 | 20 | frama |  | 1D 40 propriotf ambos | 0.09 | +47% | 145 |
| 181 | 27 | sqr | 11. Squeeze Momentum on Reversal | 1h f0.0018 ambos | 0.09 | +55% | 2142 |
| 182 | 28 | rci | 16. RCI | 1h rci30 ambos | 0.08 | +43% | 3046 |
| 183 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 1D n55 ambos | 0.08 | +53% | 106 |
| 184 | 20 | fline |  | 4h 50 2.0 ambos | 0.08 | +54% | 85 |
| 185 | 33 | cho | 9. Money Flow (Chaikin Oscillator) | 1D 3/10 ambos | 0.08 | +53% | 279 |
| 186 | 23 | ma1020 | 12. MA 10/20 Crossover | 30min 20/50 ambos | 0.08 | +32% | 2484 |
| 187 | 36 | vrb | 14. Volatility Range Breakout | 30min n50 ambos | 0.08 | +19% | 649 |
| 188 | 30 | ptr | 6. Percent Trailing Stop | 1D t5% ambos | 0.08 | +47% | 128 |
| 189 | 25 | sec | 30. Stoch/EMA Cross | 1h semtp ambos | 0.07 | +24% | 603 |
| 190 | 26 | him | 7. Hull + Ichimoku + MACD | 4h h12 ambos | 0.07 | +35% | 968 |
| 191 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 1h 9 12/26/9 obv0 ls | 0.07 | +33% | 1470 |
| 192 | 20 | qfl |  | 1h 2.0% tp3% semstop age10 | 0.07 | +14% | 23 |
| 193 | 20 | mrb |  | 1h 80 g2 m2 central ambos | 0.07 | +32% | 2167 |
| 194 | 23 | tema | 11. Triple EMA Trend | 15min adx43 ambos | 0.07 | +15% | 1614 |
| 195 | 29 | ged | 7. PTS Golden Edge | 4h 9/50 ambos | 0.07 | +25% | 189 |
| 196 | 22 | slopes | 10. Slopes | 4h 50/200 filtro ambos | 0.07 | +16% | 517 |
| 197 | 20 | dai |  | 4h 2/1.5 ambos | 0.07 | +34% | 368 |
| 198 | 10 | mab | 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao) | 30min ma 20/50 ambos | 0.07 | +29% | 2153 |
| 199 | 34 | gtf | 1. Gradient Trend Filter | 30min l25 ambos | 0.06 | +29% | 1551 |
| 200 | vixfix | grade |  | 15min ph0.95 str5 ob70 aggr u1 | 0.06 | +8% | 206 |
| 201 | 36 | dch | 11. Donchian stop entries | 30min n20 ambos | 0.06 | +26% | 4194 |
| 202 | 23 | rsipa | 17. RSI PrimeAutomation | 15min s4 tp7 ambos | 0.06 | +16% | 1860 |
| 203 | 31 | okx | 15. OKX MA Crossover | 1h 7% ambos | 0.06 | +28% | 3941 |
| 204 | 29 | madx | 13. Crossing MAs + ADX | 1h adx20 ambos | 0.06 | +27% | 564 |
| 205 | 29 | mrs | 17. MACD_RSI | 30min e20 ambos | 0.06 | +41% | 5469 |
| 206 | 23 | hl41 | 4. Higher High Lower Low | 4h 100 ambos | 0.06 | +31% | 47 |
| 207 | 26 | e5 | 1. 5 EMA | 1D rr3 ambos | 0.06 | +62% | 144 |
| 208 | 21 | joel | 12. 5min MACD scalp (Joel) | 15min tp3.0% sl2.0% ambos | 0.06 | +23% | 1623 |
| 209 | 30 | stpb | 14. Supertrend pullback | 4h flip ambos | 0.06 | +5% | 227 |
| 210 | 38 | rwp | 1. Robot Wealth Pairs (BB 20x2) | 1D z2 ambos | 0.06 | +32% | 82 |
| 211 | 28 | pab | 6. Price Action + Bollinger | 1h bb50 ambos | 0.06 | +36% | 245 |
| 212 | 13 | scalp | 2. Scalping Trading System (SMA25/EMA200, Keltner, MACD 4/34, Stoch 10) | 30min s50 e0 ambos | 0.06 | +26% | 1923 |
| 213 | 29 | trap | 11. Scalping against trapped countertrend | 15min ck5 ambos | 0.06 | +40% | 2424 |
| 214 | 12 | tk | 1. TK Cross > EMA200 (20/60, long-only) | 1h 9/26 ema200 ambos | 0.05 | +28% | 1863 |
| 215 | 27 | wvs | 8. Volatility System (Wilder) | 1h arc3 ambos | 0.05 | +28% | 1323 |
| 216 | 30 | gold | 4. MAster Gold | 1h 100/30 ambos | 0.05 | +31% | 1012 |
| 217 | 32 | stdbf | 2. Super Trend Daily BF | 1D m2.6 ambos | 0.05 | +20% | 46 |
| 218 | 27 | c2ac | 19. Combo 2/20 EMA + AC | 4h e14 ambos | 0.05 | +25% | 2279 |
| 219 | 30 | lin | 13. 2x Universelle Linien | 4h 50/200 ambos | 0.05 | +20% | 72 |
| 220 | 23 | evw | 19. EVWMA x VWAP | 4h 30 ambos | 0.05 | +8% | 570 |
| 221 | 24 | hst | 6. HMA50 + Supertrend | 1D h50 ambos | 0.05 | +18% | 91 |
| 222 | 27 | simp | 10. Simple strat (MACD + Stoch + RSI) | 1D tp3 sl1 ambos | 0.05 | +26% | 247 |
| 223 | 26 | sts | 5. SuperTrend STRATEGY | 4h m8.5 ambos | 0.05 | +15% | 101 |
| 224 | 32 | prv | 4. SuperTrend Enhanced Pivot Reversal | 1D f4 ambos | 0.05 | +29% | 25 |
| 225 | 4 | aist |  | 1h 4h/1D f3.5/3.0 adx0 | 0.05 | +20% | 220 |
| 226 | 28 | ccu | 4. Crypto Crew University (MFI/RSI/StochRSI) | 1D th30 ambos | 0.04 | +11% | 32 |
| 227 | 34 | ppt | 3. Pivot Percentile Trend | 4h l10 ambos | 0.04 | +22% | 98 |
| 228 | 33 | bes | 16. Binary Option EMA/Stoch | 4h e8 ambos | 0.04 | +27% | 815 |
| 229 | 27 | doji | 1. Doji strategy | 15min sl3% ambos | 0.04 | +16% | 5441 |
| 230 | 27 | gsc | 6. Gold Scalping | 1D tp0.1% ambos | 0.04 | +3% | 63 |
| 231 | 30 | lsr | 18. LunaOwl suporte/resistencia | 4h lb50 ambos | 0.04 | +17% | 97 |
| 232 | 37 | rsc | 16. RSI Classic (Coinrule) | 1D 30/60 | 0.04 | +14% | 14 |
| 233 | 31 | mst | 6. MACD + Stochastic | 4h st14 ambos | 0.04 | +32% | 356 |
| 234 | 18 | savwap | 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only) | 4h prd100 ambos | 0.04 | +12% | 80 |
| 235 | 33 | ich | 20. Ichimoku + EMA filter | 1h ema ambos | 0.04 | +16% | 2321 |
| 236 | 26 | lbo | 19. London BreakOut Classic | 4h rr2 ambos | 0.04 | +8% | 2460 |
| 237 | 26 | rsx | 12. RSI Crossover | 1D r50/25 ambos | 0.04 | +15% | 258 |
| 238 | 20 | kelt |  | 1D 40 2.0 tp6% sl2% tend | 0.04 | +3% | 13 |
| 239 | 29 | kamatd | 8. KAMA TradeDots | 4h r10 ambos | 0.04 | +20% | 175 |
| 240 | 31 | gx | 11. Golden X BF | 30min 20/100 ambos | 0.03 | +13% | 1423 |
| 241 | 11 | easy | 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT) | 4h e15 st3.0 zig0 ambos | 0.03 | +15% | 468 |
| 242 | 25 | made | 4. MA Displaced Envelope + ATRTS | 4h 30 ambos | 0.03 | +12% | 640 |
| 243 | 37 | hle | 11. HL MovingAvg2Line Cross | 1D n9 ambos | 0.03 | +14% | 197 |
| 244 | 24 | vws | 16. VWMA/SMA 3Commas | 1D semniveis ambos | 0.03 | +13% | 253 |
| 245 | 25 | smp | 50. Smart Money Pivot | 1D p20 sl1% tp1.5% ambos | 0.03 | +2% | 36 |
| 246 | 37 | rcf | 20. RSI-CCI Fusion | 4h n14 ambos | 0.03 | +13% | 1211 |
| 247 | 25 | flexi | 7. FlexiSuperTrend | 15min f15 ambos | 0.03 | +17% | 3041 |
| 248 | 27 | atf | 2. Adaptive Trend Flow | 1D filtros ambos | 0.03 | +14% | 322 |
| 249 | 4 | ppst | 2. Pivot Point SuperTrend (2, 3, 10) | 1D p2 f2.0 a20 | 0.03 | +1% | 54 |
| 250 | 36 | sqz | 18. Squeeze Momentum | 4h e50 ambos | 0.02 | +5% | 239 |
| 251 | 28 | ibm | 20. Babypips Inside Bar Momentum | 1h tp2 ambos | 0.02 | +7% | 4726 |
| 252 | 29 | vf | 19. Volume fight | 1h ma30 ambos | 0.02 | +10% | 773 |
| 253 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 1D a0.5 c7 | 0.02 | +8% | 573 |
| 254 | 16 | emax | 4. EMA Cross 10/20 | 1D 10/20 ambos | 0.02 | +6% | 103 |
| 255 | 26 | ksr | 9. KSR (EMA 10/20) | 1D 10/20 ambos | 0.02 | +6% | 103 |
| 256 | 28 | pmax | 8. PMax | 1D m1.5 ambos | 0.02 | +1% | 51 |
| 257 | 34 | mls | 8. ML SuperTrend kNN | 1h f4 tp2.2 ambos | 0.02 | +4% | 1797 |
| 258 | 23 | ttm | 18. Trend Trader + MACD | 1D m1.5 semmacd ambos | 0.02 | +4% | 361 |
| 259 | 24 | hf | 12. Hull Fisher | 1D h50 ambos | 0.01 | +10% | 100 |
| 260 | 36 | mbd | 20. MACD Short/Long TVIO | 1D sl21 ambos | 0.01 | +7% | 84 |
| 261 | 22 | ichi | 8. Ichimoku no offset + RSI | 4h rsi0 ambos | 0.01 | +7% | 286 |
| 262 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 1D a20 m3 ambos | 0.01 | +5% | 66 |
| 263 | 25 | thma | 9. Triangular Hull MA | 4h 40 ambos | 0.01 | +4% | 541 |
| 264 | 30 | scl | 17. 1 min forex scalping | 30min x1 ambos | 0.01 | +6% | 2150 |
| 265 | 32 | hic | 13. Hull MA_X + Ichimoku | 1h h24 ambos | 0.01 | +4% | 2787 |
| 266 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 1D a14 m2 ambos | 0.01 | +13% | 120 |
| 267 | 30 | mmr | 7. Multiple MACD RSI | 30min 12/26 ambos | 0.01 | -0% | 3576 |
| 268 | 24 | d3 | 13. DEMA 8/20/63 | 30min x1 ambos | 0.01 | +4% | 3866 |
| 269 | 27 | ichb | 17. Ichimoku Backtester | 4h 9/26/52 ambos | 0.01 | +10% | 77 |
| 270 | 29 | bbf | 16. Bull and Bear Fear | 1h n30 ambos | 0.01 | +3% | 2202 |
| 271 | 37 | sts | 9. 3x Supertrend + Stoch RSI | 1D tp1.6 ambos | 0.01 | +4% | 96 |
| 272 | 33 | r3 | 11. 3 RSI | 30min 30/70 ambos | 0.01 | +8% | 274 |
| 273 | 25 | rbd | 19. RSI Bull Div (long-only) | 4h tp3 sl1.75 | 0.00 | +2% | 37 |
| 274 | 29 | hlc | 2. High/Low channel swing | 4h l12 ambos | 0.00 | +1% | 1556 |
| 275 | 36 | atr | 17. ATR Reversed | 4h 5/3.5 ambos | 0.00 | +6% | 378 |
| 276 | 23 | bbst | 2. BBTrend + SuperTrend | 30min f7 ambos | 0.00 | -1% | 4629 |
| 277 | 14 | hap | 2. Heikin-Ashi PSAR [QuantNomad] | 30min 0.005/0.005/0.05 ambos | 0.00 | -1% | 2804 |
| 278 | 32 | tss | 18. TSI w SuperTrend decision | 1D p32 ambos | 0.00 | -2% | 78 |
| 279 | 29 | bsc | 5. Breakout Scalper | 15min 20/100 ambos | 0.00 | +1% | 2597 |
| 280 | 31 | lst | 13. LunaOwl SuperTrend 2 | 1D m2.618 ambos | 0.00 | -0% | 74 |
| 281 | 21 | renko | 14. Renko Open_Close (Pro) | 1D m1 ambos | 0.00 | +0% | 568 |
| 282 | 22 | hhll | 13. Highest High / Lowest Low | 4h 55 ambos | -0.00 | -2% | 134 |
| 283 | 25 | drm | 13. Dynamic RSI Momentum | 30min 20/80 ambos | -0.00 | +26% | 37 |
| 284 | 20 | ceyhun |  | 1D m2 3 ambos | -0.00 | -2% | 62 |
| 285 | rsidiv | rsidiv |  | 4h | -0.00 | -1% | 49 |
| 286 | zigzagpa | hon_long |  | 1h ew.236 tp.618 sl-.236 | -0.00 | -0% | 430 |
| 287 | 17 | grid | 2. Grid Like (linha-base, alvo/stop = point) | 1D p5.00% ambos | -0.00 | +3% | 290 |
| 288 | 22 | emax | 2. EMA Crossover hl2 | 30min 20x3 ambos | -0.00 | -8% | 1816 |
| 289 | 38 | smx | 4. SMAcross-mvr | 1h 10/50 ambos | -0.01 | -4% | 1419 |
| 290 | 21 | surf | 1. Trend Surfers Breakout | 4h p55 t8.0 f2.0 ambos | -0.01 | -5% | 201 |
| 291 | 36 | ral | 8. RSI Alligator | 1D sl10 ambos | -0.01 | -6% | 283 |
| 292 | 33 | vxe | 18. VWAP X EMA | 1h ema50 ambos | -0.01 | -10% | 2431 |
| 293 | 37 | bbr | 4. Big Bar | 1h a4 ambos | -0.01 | -1% | 1221 |
| 294 | 28 | sma3 | 19. Tres medias (SMA 7/25/99) | 4h 7/99 ambos | -0.01 | -6% | 297 |
| 295 | 36 | rs2 | 10. RSI 2 + tendencia, trailing | 30min ts3 ambos | -0.01 | -11% | 1252 |
| 296 | 26 | hama | 11. NSDT HAMA (EMA55) | 1D e20 ambos | -0.02 | -8% | 174 |
| 297 | 27 | flash | 7. The Flash | 1D mr60 ambos | -0.02 | -11% | 52 |
| 298 | 26 | dm | 18. DEMA + MACD | 1D d21 ambos | -0.02 | -10% | 459 |
| 299 | 25 | mst | 11. Master Supertrend | 15min 60 m4 ambos | -0.02 | -12% | 2108 |
| 300 | 25 | ao | 49. Awesome Oscillator | 4h ambos | -0.02 | -10% | 2520 |
| 301 | 25 | moon | 8. Moon Phases | 1D normal ambos | -0.02 | -9% | 237 |
| 302 | 27 | e3 | 16. 3 EMA + Stoch RSI + ATR | 1D tp2 ambos | -0.02 | +2% | 301 |
| 303 | 32 | koz | 20. Kozlod MA Cross | 1h 10/30 ambos | -0.02 | -10% | 2078 |
| 304 | 33 | ers | 13. EMA + RSI Sniper (long-only) | 4h tp5/sl3 | -0.02 | -5% | 172 |
| 305 | 32 | irs | 6. Ichimoku Cloud with RSI (Coinrule) | 4h rsi50 ambos | -0.02 | -12% | 133 |
| 306 | 32 | dcs | 10. Donchian Channel (stop + EMA200) | 30min d20 ambos | -0.02 | -11% | 2903 |
| 307 | 28 | t3cci | 7. FX Sniper T3-CCI | 1D cci14 ambos | -0.02 | -12% | 205 |
| 308 | 25 | kpl | 40. KPL Swing | 1D 20 ambos | -0.03 | -29% | 49 |
| 309 | 28 | hvc | 14. Hull MA vs Candle | 1h h50 ambos | -0.03 | -12% | 1802 |
| 310 | 34 | kmt | 5. Ichimoku Kumo Twist | 15min stop ambos | -0.03 | -12% | 4358 |
| 311 | 23 | nr7 | 5. NR7 + Inside Day (long-only) | 1D sma14 | -0.03 | -5% | 23 |
| 312 | 24 | alpha | 20. AlphaTrend | 30min mfi ambos | -0.03 | -14% | 2861 |
| 313 | 26 | qc | 8. QuantCat Intraday | 30min atr4 ambos | -0.03 | -14% | 1513 |
| 314 | 28 | gch | 18. Gaussian Channel | 1D p50 ambos | -0.03 | -14% | 203 |
| 315 | 30 | hul | 1. Hull MA and Candle cross | 30min z100 ambos | -0.03 | -13% | 6903 |
| 316 | 24 | beng | 18. Bullish Engulfing (long-only) | 1D sl2.00% tp2.00% semtend | -0.03 | -4% | 97 |
| 317 | 32 | fis | 15. Fisher Transform (Ehlers) | 1h l20 ambos | -0.03 | -16% | 2651 |
| 318 | 26 | vst | 2. Vegas SuperTrend Enhanced | 1D b2 ambos | -0.03 | -13% | 123 |
| 319 | 13 | ichi | 5. Ichimoku basico (9/26/52, deslocamento 26) | 15min 20/60/120 ambos | -0.03 | -15% | 1832 |
| 320 | 22 | xsc | 15. XAUUSD Scalping V2 | 4h tp3 sl1.5 ambos | -0.03 | -13% | 956 |
| 321 | 29 | bbe9 | 6. Bollinger Bands + EMA 9 | 1D bb20 ambos | -0.04 | -12% | 128 |
| 322 | 25 | bts | 27. BEST Trailing Stop | 1D tr3 ambos | -0.04 | -14% | 58 |
| 323 | 28 | mab | 13. Moving Average (BiznesFilosof) | 1D sma21 ambos | -0.04 | -16% | 273 |
| 324 | 32 | cce | 12. CCI & EMA (Tradeswithashish) | 1h tp10% ambos | -0.04 | -19% | 1081 |
| 325 | 36 | at3 | 16. ATR and T3 | 4h p2 ambos | -0.04 | -22% | 309 |
| 326 | 20 | ypmax |  | 4h 13 2 ambos | -0.04 | -22% | 520 |
| 327 | 17 | ftsma | 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier) | 4h 5/20/200 ft ambos | -0.04 | -20% | 323 |
| 328 | 20 | rsirev |  | 30min 8 1.5 normal ambos | -0.04 | -22% | 1626 |
| 329 | 7 | srt | 5. SR TREND (21) | 1h len100 | -0.05 | -20% | 1278 |
| 330 | 27 | atrts | 15. ATR Trailing Stops | 1D a5x3.5 ambos | -0.05 | -32% | 48 |
| 331 | 25 | 4ma | 48. Multi-MA (4MA) | 1D wma200 ambos | -0.05 | -34% | 40 |
| 332 | 30 | mbf | 16. Momentum BF | 1D l18 ambos | -0.05 | -20% | 238 |
| 333 | 31 | csc | 10. Crypto Price Scalper (long-only) | 4h cc60 st3% | -0.05 | -6% | 49 |
| 334 | 22 | turtle | 6. Real Turtle (stops) | 1D 20/10 n4 ambos | -0.05 | -21% | 96 |
| 335 | 32 | dkw | 14. Donchian Channels (KrisWaters) | 1D canal ambos | -0.05 | -21% | 96 |
| 336 | 20 | xscalp |  | 1D gap0.25% rr1 ambos | -0.05 | -9% | 2247 |
| 337 | zigzagpa | hon_short |  | 4h ew.236 tp.618 sl-.236 | -0.05 | -5% | 208 |
| 338 | 32 | stt | 16. SuperTrend Trapping Candle | 30min 0.3% ambos | -0.05 | -29% | 2104 |
| 339 | 28 | stc | 12. SuperTrend Cloud | 1D m2.4/4.8 ambos | -0.05 | -21% | 64 |
| 340 | 24 | vwap | 17. VWAPStrategy | 4h sma20 ambos | -0.06 | -22% | 1096 |
| 341 | 33 | snr | 12. Signal To Noise | 1D l21 ambos | -0.06 | -21% | 97 |
| 342 | 25 | htf | 5. Hull MA TimeFrame CrossOver | 1h 200 s3 ambos | -0.06 | -29% | 228 |
| 343 | 3 | ann | 4. ANN Strategy v2 | 1D thr 0 | -0.06 | -26% | 917 |
| 344 | 30 | mma | 3. Multi-MA | 15min l150 ambos | -0.06 | -29% | 1802 |
| 345 | 29 | chb | 20. Channel Break (free bot) | 1D canal ambos | -0.06 | -30% | 98 |
| 346 | 23 | stv | 16. Super trend V | 1D m3 ambos | -0.06 | -32% | 58 |
| 347 | 16 | aivst | 3. AI Volume SuperTrend (10, 3; rotulo WMA20 vs WMA100 do ST) | 4h l10 f2 ambos | -0.06 | -32% | 399 |
| 348 | 25 | ce | 1. Chandelier Exit | 1h risco ambos | -0.06 | -30% | 2151 |
| 349 | 30 | tsh | 2. TrendShift Supertrend + ADX | 30min m3 ambos | -0.07 | -30% | 1456 |
| 350 | 26 | dma | 15. Dual Moving Average (angulo) | 4h a3 ambos | -0.07 | -35% | 472 |
| 351 | 27 | wyk | 13. Wyckoff Range | 1D sl3% ambos | -0.07 | -24% | 33 |
| 352 | 28 | gvto | 9. Golden Vector Trend Orchestrator | 4h adx0 ambos | -0.07 | -34% | 278 |
| 353 | zigzagpa | honesto |  | 30min ew.236 tp.618 sl-.236 | -0.07 | -14% | 935 |
| 354 | 37 | dmx | 12. DMI + nuvem Ichimoku | 1D adx25 long | -0.07 | -30% | 122 |
| 355 | 25 | bas | 45. BEST ATR Stop Multiple | 1h atr2 ambos | -0.07 | -32% | 1425 |
| 356 | 31 | ttm | 2. TTM scalper | 1D inv ambos | -0.08 | -39% | 491 |
| 357 | 36 | vst | 3. Multi-Step Vegas SuperTrend | 1D b2 ambos | -0.08 | -29% | 66 |
| 358 | 22 | psarc | 14. Parabolic SAR on close | 1D n3 0.01/0.1 ambos | -0.08 | -30% | 101 |
| 359 | 30 | gso | 8. Gann Swing Oscillator | 1h l10 ambos | -0.08 | -35% | 1105 |
| 360 | 25 | mas | 23. Mov Avg Speed (3 sinais) | 4h ambos | -0.08 | -41% | 491 |
| 361 | 25 | masc | 26. MA Scalper Coinrule (long-only) | 1D sl2 tp8 | -0.08 | -13% | 13 |
| 362 | 33 | hcx | 15. Hull MA Crossover | 1h h28 ambos | -0.08 | -38% | 3394 |
| 363 | 27 | tfb | 12. Trend Following Breakout | 4h 20/10 ambos | -0.09 | -40% | 588 |
| 364 | 28 | k3ma | 2. Kozlod 3 MA | 4h sma ambos | -0.09 | -30% | 100 |
| 365 | 21 | guppy | 19. Super Guppy | 30min ambos | -0.09 | -40% | 2644 |
| 366 | 25 | uhl | 35. Uhl MA System | 4h 100 ambos | -0.09 | -41% | 121 |
| 367 | 35 | lpr | 1. Linear Regression Pearson | 30min k360 sempre ambos | -0.09 | -42% | 1324 |
| 368 | 25 | bbe | 2. Bollinger Bands Enhanced (long-only) | 30min sl3 | -0.09 | -34% | 1221 |
| 369 | 38 | kij | 2. Kijun-Sen DasanC | 4h n20 ambos | -0.10 | -40% | 744 |
| 370 | 25 | rmr | 14. Range Strat MACD/RSI | 4h sl5% ambos | -0.10 | -46% | 362 |
| 371 | 36 | pin | 6. Pinbar | 4h pm2 ambos | -0.10 | -44% | 503 |
| 372 | 37 | ckr | 2. Chande Kroll Stop | 1h n21/a1.5 | -0.10 | -28% | 1079 |
| 373 | 37 | lag | 1. Laguerre RSI | 1h a0.2 ambos | -0.10 | -46% | 1679 |
| 374 | 25 | spym | 39. SPY Master | 1D ambos | -0.10 | -48% | 332 |
| 375 | 29 | wtr | 18. BTC WaveTrend R:R (long-only) | 4h rr1.5 lim-40 | -0.11 | -25% | 263 |
| 376 | 23 | combo | 14. Combo 123 Reversal + SMI | 1D smi50 ambos | -0.11 | -36% | 643 |
| 377 | 24 | lht | 14. Low-High Trend (long-only) | 4h tp8 | -0.11 | -43% | 10 |
| 378 | 25 | imct | 16. Ichimoku + MACD/CMF/TSI | 15min ambos | -0.11 | -48% | 3108 |
| 379 | 27 | ssl | 18. SSL Channel Cross | 1D l10 ambos | -0.11 | -47% | 217 |
| 380 | 25 | c123r | 18. Combo 123 Reversal + RSI | 30min ambos | -0.11 | -49% | 1365 |
| 381 | 25 | sr | 3. Support Resistance | 1D 10 ambos | -0.11 | -41% | 67 |
| 382 | 26 | tcci | 20. Triple CCI + MFI (long-only) | 4h sl3 at1 | -0.12 | -36% | 144 |
| 383 | 31 | cmb | 20. Combo 123 Reversal & Stochastic | 4h l28 ambos | -0.12 | -57% | 294 |
| 384 | 30 | ott | 10. Optimized Trend Tracker | 1D 0.1% ambos | -0.12 | -54% | 426 |
| 385 | 33 | s200 | 5. SMA 200 bands (long-only) | 15min 1.04/0.99 | -0.12 | -32% | 103 |
| 386 | 15 | btcb | 5. BTC bot (cc do RSI21 x 0; saida no R3 semanal) | 1D sl15% tp10% ambos | -0.13 | -38% | 14 |
| 387 | 37 | c12r | 10. Combo 123 + Rainbow Oscillator | 1D ro2 ambos | -0.13 | -50% | 306 |
| 388 | 33 | vct | 6. TASC 2024.08 VCTS (long-only) | 1D adx30/vp50 | -0.14 | -36% | 10 |
| 389 | 32 | gps | 9. Grant's PSAR (long-only) | 1D 0.013/0.2 | -0.14 | -55% | 31 |
| 390 | 22 | renko | 12. Renko Strategy V2 | 4h atr10 ambos | -0.14 | -59% | 1123 |
| 391 | 37 | tdw | 19. Gold TDOW (MACD+Stoch+RSI) | 1h tdow | -0.14 | -49% | 1422 |
| 392 | 20 | alli |  | 1D ha ambos | -0.14 | -51% | 181 |
| 393 | 23 | vwpb | 20. VWAP Momentum Pullback (long-only) | 4h sl3% tp7% rsi30 | -0.15 | -57% | 122 |
| 394 | 30 | rom | 9. RSI of MACD (long-only) | 1h x50 sl3% | -0.15 | -49% | 677 |
| 395 | 25 | era | 31. EMA Cross + RSI + ADX | 4h sl5% ambos | -0.15 | -51% | 305 |
| 396 | 25 | muta | 21. Mutanabby AI Algo Pro (long-only) | 1D sl2 | -0.15 | -43% | 46 |
| 397 | 22 | crsi | 19. Cumulative RSI (long-only) | 4h 10/90 ema100 | -0.15 | -55% | 24 |
| 398 | 4 | tdh | 3. Trend Direction Helper (RISK 10, SMA 7/20) | 1D r15 5/10 | -0.16 | -60% | 117 |
| 399 | 23 | dip | 15. Buying Dip (long-only) | 4h d20 tp1 sl1 | -0.16 | -54% | 603 |
| 400 | 21 | mbr | 10. MACD + BB + RSI (long-only) | 1D sl5% | -0.17 | -59% | 24 |
| 401 | 22 | mrsi | 4. Easy MACD + RSI (long-only) | 1D rsi50 semstop | -0.17 | -55% | 16 |
| 402 | 32 | rdv | 11. RSI Divergence Strategy | 1h rsi<35 ambos | -0.17 | -57% | 32 |
| 403 | 27 | rdip | 3. Optimized RSI Buy The Dips (long-only) | 1D 30/70 sma100 | -0.17 | -59% | 10 |
| 404 | flawless | flawless |  | 1D | -0.17 | -54% | 68 |
| 405 | 26 | pdb | 13. Previous Day High/Low Breakout | 4h hl ambos | -0.17 | -64% | 1112 |
| 406 | 31 | ich | 3. Advanced Ichimoku (long-only) | 1h ent strong sai all | -0.18 | -60% | 465 |
| 407 | 37 | mdv | 3. MACD + DMI + Volatility Stop | 1h tp3 | -0.18 | -65% | 844 |
| 408 | 36 | mst | 7. Trend Entry 0 (estrutura) | 1D ambos | -0.18 | -70% | 466 |
| 409 | vixfix | default |  | 4h default | -0.18 | -62% | 130 |
| 410 | 37 | b4u | 8. IU 4 Bar UP | 1D f1 | -0.18 | -63% | 62 |
| 411 | 38 | tsl | 3. Trailing Stop Loss (SMA 21/49) | 4h 50/200 tsl7.5 | -0.18 | -61% | 39 |
| 412 | 25 | mcci | 34. MACD + CCI | 4h ambos | -0.19 | -72% | 2729 |
| 413 | 34 | ttl | 9. Turtle (uma unidade, long) | 1D 55/55/20/20 filtro | -0.19 | -65% | 20 |
| 414 | 25 | vwbo | 29. VWAP Breakout | 4h tp4 ambos | -0.19 | -74% | 5356 |
| 415 | 27 | bbbo | 9. Bollinger Band Breakout (long-only) | 4h m2 basis | -0.19 | -62% | 263 |
| 416 | 21 | rsitc | 4. RSI Trend Crypto (long-only) | 1h 25/65 | -0.19 | -62% | 193 |
| 417 | vixfix | u1 |  | 4h default | -0.20 | -73% | 130 |
| 418 | 26 | kama | 10. KAMA Strategy (long-only) | 1D f1 atr3 | -0.20 | -68% | 53 |
| 419 | 23 | coin | 6. Coinrule Scalping On Trend (long-only) | 4h 70/30 | -0.20 | -69% | 192 |
| 420 | 21 | strex | 6. SuperTREX (RSI semanal amostrado) | 4h m4 ambos | -0.20 | -73% | 94 |
| 421 | 29 | dbo | 3. Donchian Breakout (long-only) | 1D d20 basis | -0.20 | -70% | 45 |
| 422 | 23 | zzrsi | 13. ZigZag RSI (long-only) | 30min r14 30/70 zz1 | -0.21 | -73% | 106 |
| 423 | 30 | rbs | 19. RSI Buy and Sell (long-only) | 4h 70/40 | -0.21 | -71% | 89 |
| 424 | 8 | vwap | 3. VWAP Trendfollow (sessao, 0.88 desvio, saida na banda 2) | 1h m0.5 match1 tp0.0 ambos | -0.21 | -79% | 6611 |
| 425 | 21 | msr | 18. MACD + Stoch + RSI (long-only) | 1h k80 | -0.21 | -76% | 1434 |
| 426 | 25 | davin | 25. Davin 10/200 MA Pullback (long-only) | 4h dip14 sl5 | -0.22 | -78% | 418 |
| 427 | 26 | mrr | 14. MACD, RSI & RVOL (long-only) | 1h 40/60 rv1.5/1.5 | -0.23 | -79% | 269 |
| 428 | 25 | rsim | 24. RSI mensal (long-only) | 4h padrao | -0.23 | -80% | 10 |
| 429 | 33 | pac | 1. PSAR + ADX + CMF + RSI (long-only) | 1D rsi14/cmf40 | -0.23 | -79% | 19 |
| 430 | 22 | btf | 20. Breakout Trend Follower (long-only) | 1D p3 sma50 | -0.23 | -80% | 48 |
| 431 | 25 | elo | 20. EMA Long Only | 1D 21 | -0.23 | -81% | 29 |
| 432 | 21 | bbao | 8. BB + AO (long-only) | 1D bb5 | -0.23 | -81% | 42 |
| 433 | 24 | btcm | 11. Bitcoin Momentum (long-only) | 1h atr2 | -0.23 | -80% | 1976 |
| 434 | 33 | vat | 4. VWMA with ATR stops (long-only) | 1D 2.5atr/33 | -0.23 | -80% | 36 |
| 435 | 25 | mx | 32. Multi-X (long-only) | 1D padrao | -0.24 | -81% | 60 |
| 436 | 26 | mel | 4. MACD + EMA (long-only) | 1h semfiltro 12/26 | -0.24 | -83% | 2111 |
| 437 | 31 | sha | 18. Smoothed Heiken Ashi (long-only) | 1D 20/10 | -0.24 | -83% | 40 |
| 438 | 27 | stt | 4. Stochastic Trend (long-only) | 30min k200/100 x60 | -0.25 | -85% | 204 |
| 439 | 33 | haw | 2. Abdoli's Heikin Ashi Smoothed (long-only) | 4h ema30/2velas | -0.26 | -86% | 334 |
| 440 | 37 | qts | 14. Quantitative Trend (pivo) | 4h tp2/sl1.75 | -0.26 | -86% | 1412 |
| 441 | 31 | haw | 4. Heikin Ashi Wick (long-only) | 1D candle both | -0.26 | -86% | 642 |
| 442 | 31 | akt | 9. AK Trend ID (long-only) | 1D 5/13 | -0.26 | -86% | 96 |
| 443 | 28 | bbw | 15. Bollinger Breakout (long-only, stop) | 1D bb20 banda | -0.26 | -88% | 38 |
| 444 | 29 | atsl | 1. ATR Trailing Stoploss | 1h m2.5 ambos | -0.28 | -89% | 5732 |
| 445 | 37 | obv | 17. OBV Acumulacao/Distribuicao | 1h n50 | -0.29 | -90% | 1293 |
| 446 | 25 | tra | 33. Trend Reversal Alerts (long-only) | 1D padrao | -0.31 | -93% | 207 |
| 447 | 25 | stma | 12. State-aware MA Cross (long-only) | 1D padrao | -0.32 | -94% | 142 |
| 448 | 20 | macd |  | 30min m2.2 tp5% filtro | -0.32 | -94% | 2015 |
| 449 | 36 | btm | 4. Beat the market (filtro de vol) | 1D p80/w100 | -0.36 | -96% | 79 |
| 450 | 28 | planb | 3. PlanB Quant Investing 101 | 1h top80 ambos | -0.40 | -98% | 135 |
