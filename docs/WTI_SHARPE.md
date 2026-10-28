# WTI: ranking pelo Sharpe antes do OOS

Sharpe dos retornos diários de 2017-01-03 a 2024-10-19 (sem partes, sem filtro); melhor célula de cada estratégia pelo Sharpe; trades abertos em abril de 2020 descartados; templates fora.

| # | Lote | Est | Nome | Célula | Sharpe | Total | Trades |
|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 2/2 | 1.78 | +16523% | 47452 |
| 2 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 1D SHORT p1 m4.0 sl5.0 | 1.30 | +729% | 82 |
| 3 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 4h como escrito ambos | 1.26 | +1358% | 51 |
| 4 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.05 roc6.0 m3.0/3.0 ambos | 1.10 | +930% | 304 |
| 5 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 30min fiel ambos | 1.07 | +592% | 746 |
| 6 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 4h r14 w30 d3 signal ambos | 1.05 | +1137% | 1651 |
| 7 | 22 | ewo | 3. EWO RSI Exhaustion | 1D vol ambos | 1.05 | +1079% | 12 |
| 8 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 ambos | 1.02 | +183% | 296 |
| 9 | ichimoku | ichimoku |  | 1h | 1.02 | +425% | 306 |
| 10 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w140 -94/-6 sl0.005 contrario ambos | 1.01 | +509% | 2433 |
| 11 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 4h sw8 sl8atr tp1% ambos | 0.94 | +141% | 647 |
| 12 | 29 | bot | 14. BotBot | 1D k0.04 ambos | 0.92 | +509% | 32 |
| 13 | 23 | crazy | 10. Crazy Scalping (TMO + AMA) | 1h sl10 ambos | 0.91 | +159% | 387 |
| 14 | 25 | tlb | 42. Trendline Breakout KedArc | 4h p5 semma ambos | 0.90 | +382% | 698 |
| 15 | 26 | csq | 3. Crypto Squeeze | 1D mfi14 ambos | 0.86 | +406% | 58 |
| 16 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 30min f10 one tp5.0 | 0.86 | +288% | 1268 |
| 17 | 28 | l2r | 11. L2 Reversal Labels | 30min semtpsl ambos | 0.85 | +654% | 545 |
| 18 | 25 | nr7s | 46. NR7ID (short-only) | 1D sma14 | 0.85 | +34% | 24 |
| 19 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 4h sl4.0% rr5 ambos | 0.84 | +356% | 315 |
| 20 | 20 | 3st |  | 1D pl3.0 thr30 ambos | 0.83 | +183% | 22 |
| 21 | 22 | tdon | 9. Turtle Donchian/ATR | 4h 20/10 m4 short | 0.81 | +220% | 211 |
| 22 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 30min l50 e40 ambos | 0.81 | +454% | 1143 |
| 23 | 33 | pst | 8. Parabolic SAR stop entries | 1h af0.02 ambos | 0.80 | +488% | 2731 |
| 24 | 27 | spk | 14. Martin Pring's Special K | 1D s30 ambos | 0.78 | +313% | 47 |
| 25 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 1D m2.7 normal tp0.47 sl0.21 | 0.74 | +268% | 76 |
| 26 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 1h 100/50/7 ambos | 0.74 | +421% | 2076 |
| 27 | 30 | sich | 11. SuperIchi | 1D rr3 ambos | 0.73 | +125% | 14 |
| 28 | 20 | atrgod |  | 4h sl4.5 rr1.5 semfiltros ambos | 0.73 | +241% | 118 |
| 29 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 4h r8 m34 rev | 0.73 | +334% | 316 |
| 30 | 5 | pvb | 1. Price and Volume Breakout (60/60/200, so long) | 1h 20/50 x5 vol1 ls | 0.72 | +240% | 625 |
| 31 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 15min sl0% tp35% filtros ambos | 0.72 | +359% | 1222 |
| 32 | 25 | dax | 10. DAX Shooter | 1D adx32 ambos | 0.71 | +228% | 10 |
| 33 | 8 | eng | 4. Engulfing + SMA32 | 30min ma64 sl0.005 tp0.05 ambos | 0.70 | +189% | 4120 |
| 34 | 22 | tst | 18. Triple SuperTrend + StochRSI | 1D 28/78 rr2/1.5 ambos | 0.70 | +367% | 19 |
| 35 | 34 | khw | 10. Kahlman HullMA / WT Cross | 1h h48 sem wt ambos | 0.69 | +327% | 2972 |
| 36 | 5 | qqe |  | 1D b60 x30 s90 sw20 wae1 lucro1 | 0.67 | +254% | 74 |
| 37 | 16 | qqe | 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao) | 1h XZ f5 dfil ambos | 0.67 | +159% | 1005 |
| 38 | 32 | srs | 17. Supertrend + RSI (Alorse) | 1D f3 ambos | 0.67 | +190% | 59 |
| 39 | 30 | hms | 20. Harmonic System | 4h close ambos | 0.66 | +288% | 1791 |
| 40 | 21 | mtfrsi | 20. Multi Timeframe RSI | 4h 1/3/6 30/70 ambos | 0.66 | +283% | 18 |
| 41 | 25 | cmo | 6. CMO TradeDots | 4h 40 ambos | 0.65 | +269% | 243 |
| 42 | 37 | chk | 18. Chaloke System | 4h 20/50/100 ambos | 0.65 | +254% | 257 |
| 43 | 25 | rtb | 47. Reversal Trading Bot | 1h sl1% tp2% ambos | 0.64 | +124% | 2052 |
| 44 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 15min rr1.0 vol sess ambos | 0.64 | +74% | 1163 |
| 45 | 36 | kel | 12. Keltner SL/TP | 4h k2/sl20 ambos | 0.64 | +264% | 129 |
| 46 | 25 | opw | 37. TASC One Percent A Week (long-only) | 1h dip1 tp1 | 0.63 | +62% | 406 |
| 47 | 36 | mma | 15. Multi Moving Average Crossing | 15min 9/50/100 ambos | 0.63 | +166% | 2441 |
| 48 | 33 | szs | 19. Stochastic Z-Score (TradeDots) | 1D z2 ambos | 0.63 | +255% | 39 |
| 49 | 29 | r2m | 9. RSI2 + medias (pullback) | 4h 5/95 ambos | 0.63 | +73% | 306 |
| 50 | 19 | cipher | 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11) | 1h wt tp4 sl2 ambos | 0.63 | +22% | 46 |
| 51 | 25 | sta | 38. Stoch + ATR | 4h 14 ambos | 0.62 | +267% | 1040 |
| 52 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 15min p3 rr5.0 trend1 long | 0.62 | +30% | 616 |
| 53 | 34 | zlm | 6. Zero-Lag MA Trend Following | 1D rr2 ambos | 0.62 | +148% | 41 |
| 54 | 34 | azl | 7. Adaptive Zero Lag EMA | 1h cos thr0.05 ambos | 0.62 | +253% | 5509 |
| 55 | 27 | obv | 20. OBV Oscillator | 1h l50 ambos | 0.61 | +235% | 1891 |
| 56 | 30 | rdi | 5. RSI Divergence x Ichimoku x 200EMA | 4h lb5 ambos | 0.61 | +195% | 146 |
| 57 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 1D k3.0 sl3.0 be0.0 tp0.0 ema0 ambos | 0.61 | +154% | 36 |
| 58 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 1h n30 5/20 | 0.60 | +228% | 2480 |
| 59 | 22 | force | 17. Force trade scalper | 1D 3/20 ambos | 0.60 | +349% | 55 |
| 60 | 24 | srvi | 7. Stochastic RSI + RVI | 4h p10 30/70 ambos | 0.60 | +235% | 359 |
| 61 | 12 | pt | 2. Powertrend (range filter de volume, 200, long-only) | 15min l50 m1.5 vol | 0.60 | +11% | 16 |
| 62 | 26 | pprs | 16. Pivot Point Reversal + RSI | 30min pv3/3 ambos | 0.58 | +225% | 5960 |
| 63 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 15min r0.5 rr3.0 ret00 | 0.58 | +53% | 1900 |
| 64 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 15min lb20 pb2 tp1.0 sl1.0 | 0.58 | +132% | 5544 |
| 65 | 31 | psw | 8. Swing Parabolic SAR | 4h af0.02 ambos | 0.58 | +206% | 1280 |
| 66 | 29 | lrcb | 12. Linear Regression Channel Breakout | 1D dv2.3 ambos | 0.58 | +52% | 49 |
| 67 | 33 | bct | 3. Bar Counter Trend Reversal | 4h kc2 ambos | 0.57 | +207% | 222 |
| 68 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 4h e200 tp/sl sim2 ambos | 0.57 | +98% | 344 |
| 69 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 1h sl0.0025 rr2.0 eod0 filt1 long | 0.57 | +7% | 161 |
| 70 | 6 | hs | 1. Hammers & Stars (stop 1 ATR, alvo 1R) | 4h s0.5 rr1.0 fib0.25 ema50 | 0.55 | +54% | 313 |
| 71 | 25 | ht3 | 36. Swing HULL + T3 | 4h 100 sltp ambos | 0.55 | +181% | 764 |
| 72 | 21 | kb | 15. Keltner bounce (SMA200 +- 8 ATR) | 1h 200 d3 ambos | 0.55 | +176% | 285 |
| 73 | 9 | micu | 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips) | 4h sl0.0025 tp0 trail0 sess1 ambos | 0.55 | +105% | 1428 |
| 74 | 31 | lch | 5. Linear Channel (long-only) | 1h v4% hma400 | 0.54 | +31% | 22 |
| 75 | 25 | dbt | 44. Double Bottom/Top Hunter | 30min 30 ambos | 0.54 | +230% | 340 |
| 76 | 21 | hulk | 5. Hulk Scalper | 30min thr0.1 adx33 tp3.00% sl2.0% ambos | 0.54 | +61% | 263 |
| 77 | 11 | grab | 4. Grab Trading System (80/21) | 4h 80/21 stop1 | 0.54 | +108% | 267 |
| 78 | 21 | sqz | 2. Squeeze Momentum | 4h l2 sl0.5% tp1% semsqz ambos | 0.53 | +43% | 1194 |
| 79 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 4h sl2.00% sessao ambos | 0.53 | +104% | 1016 |
| 80 | 20 | cam |  | 4h sl2.0% tp6% ambos | 0.52 | +131% | 857 |
| 81 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 1h TILL 12/26/9 | 0.52 | +156% | 2897 |
| 82 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 1h 50 rev ambos | 0.52 | +154% | 201 |
| 83 | 33 | tbn | 7. Trend Bounce | 4h c7 ambos | 0.51 | +92% | 499 |
| 84 | 32 | tfp | 19. Trend Following Parabolic (TradeDots) | 1h rr1.3 ambos | 0.51 | +138% | 477 |
| 85 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 1h l100 m3.0 sl0.002 ambos | 0.51 | +4% | 35 |
| 86 | 15 | comb | 2. Combined Strategy (fita de EMAs + RSI + Stoch) | 4h osc ambos | 0.51 | +135% | 725 |
| 87 | 31 | seq | 7. Sequence Snap | 1D rr1 ambos | 0.50 | +76% | 21 |
| 88 | 23 | twin | 1. Twin Range Filter | 1D sematr t0 sltp ambos | 0.49 | +125% | 156 |
| 89 | 31 | vip | 19. VIP (long-only) | 1h tp1% sl1% | 0.48 | +20% | 210 |
| 90 | 29 | cez | 4. Chandelier Exit + ZLSMA | 15min m2 ambos | 0.48 | +48% | 1978 |
| 91 | 36 | sms | 9. Super Momentum | 30min cmo14 ambos | 0.48 | +131% | 466 |
| 92 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR80 p0.5 c0.005 | 0.48 | +163% | 24 |
| 93 | 28 | sbf | 1. Stochastic (BiznesFilosof) | 4h 14/86 ambos | 0.47 | +141% | 140 |
| 94 | 23 | e3r | 3. 3 EMA + RSI | 4h sl0% x0 ambos | 0.47 | +72% | 135 |
| 95 | 32 | hme | 5. HMA 200 + EMA 20 | 1h hma200 ambos | 0.46 | +116% | 1188 |
| 96 | 33 | dst | 17. Dual Supertrend with MACD | 1h 3/5 ambos | 0.46 | +96% | 2192 |
| 97 | 24 | mbit | 3. Mbit MA (contrario) | 30min ma520 n10 ambos | 0.46 | +128% | 462 |
| 98 | zigzagpa | grade |  | 1h ew0.0 tp1.618 sl-1.0 | 0.46 | +28% | 89 |
| 99 | 36 | cbo | 19. Candle Breakout 13h UTC | 15min h13/rr2 ambos | 0.46 | +81% | 2237 |
| 100 | 23 | mabb | 9. MA BB + RSI | 15min a9 vol ambos | 0.46 | +64% | 442 |
| 101 | 18 | osb | 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario) | 30min m0.25 sl1.00% ambos | 0.46 | +75% | 1494 |
| 102 | 22 | apsar | 7. ATR Parabolic SAR | 30min n1 0.01/0.1 ambos | 0.46 | +109% | 904 |
| 103 | 24 | ectp | 19. EMA Crossover with TP | 1D sl3% tp0.5 ambos | 0.45 | +25% | 49 |
| 104 | 28 | hapa | 10. Heikin Ashi Price Action | 1D velas ambos | 0.45 | +112% | 319 |
| 105 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 1h 12/26/9 ambos | 0.45 | +110% | 4610 |
| 106 | 22 | pmax | 16. PMax on RSI w T3 | 15min m3 t8 ambos | 0.44 | +126% | 2416 |
| 107 | 22 | tsi | 5. TSI CCI Hull | 15min tp0.0% ambos | 0.44 | +111% | 2670 |
| 108 | 20 | qfl |  | 30min 2.0% tp1% semstop age10 | 0.44 | -100% | 59 |
| 109 | 24 | dcf | 9. Donchian free bot | 1h semtp ambos | 0.43 | +90% | 4540 |
| 110 | 20 | ds |  | 1D 17/72 ambos | 0.43 | +55% | 46 |
| 111 | 34 | fmv | 4. FlexiMA Variance Tracker | 1D f8 ambos | 0.42 | +64% | 51 |
| 112 | 33 | stc | 10. SuperTrend chandelier 7/7 | 4h m7 ambos | 0.42 | +90% | 109 |
| 113 | 24 | smc | 8. SMC | 30min lb30 ambos | 0.41 | +90% | 1200 |
| 114 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 30min atr10x4.0 | 0.41 | +93% | 2225 |
| 115 | 22 | mab | 11. Moving Average Band | 1h 100 rr3 ambos | 0.40 | +69% | 1716 |
| 116 | 13 | sqz | 4. Squeeze Momentum [LazyBear] (BB14x2, KC16x1,5) | 4h bb20 kc16 ambos | 0.40 | +49% | 444 |
| 117 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 1h a3.0 atr11 hma2 ambos | 0.40 | +90% | 1214 |
| 118 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 15min bb20 3 semlatest ambos | 0.40 | +78% | 412 |
| 119 | 27 | tch | 5. TSI CCI Hull | 15min p25 ambos | 0.40 | +85% | 2655 |
| 120 | 29 | rss | 10. RSI and SMA (Coinrule) | 15min 50/100 ambos | 0.40 | +81% | 1502 |
| 121 | 37 | wmx | 15. WMX Williams Fractals | 4h o3 ambos | 0.39 | +75% | 1059 |
| 122 | 10 | aio | 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR) | 1h rsi1 atr1.0 rr2.0 long | 0.39 | +20% | 259 |
| 123 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 30min 12 2 ambos | 0.39 | +76% | 1511 |
| 124 | 21 | rbin | 17. RSI Binary (6, 13/82, 3 barras) | 1D 14 30/70 h3 ambos | 0.39 | +31% | 70 |
| 125 | 20 | nw |  | 1D 8 x25 ambos | 0.39 | +76% | 213 |
| 126 | 25 | grov | 28. Grover Llorens Activator | 30min 100 m5 ambos | 0.38 | +76% | 3364 |
| 127 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 1D hon DEMA13 x1 | 0.38 | +71% | 478 |
| 128 | 22 | bbra | 1. BB + RSI + ADX | 1D sl0.0% adx100 ambos | 0.38 | +63% | 24 |
| 129 | 31 | ten | 12. Tendency EMA + RSI | 4h x24 ambos | 0.38 | +40% | 155 |
| 130 | 29 | adxb | 15. Rob Booker ADX Breakout | 1h adx25 ambos | 0.38 | +59% | 1400 |
| 131 | 20 | madrid |  | 1D tp3% sl3% ambos | 0.37 | +68% | 307 |
| 132 | 18 | tdi | 1. Traders Dynamic Index (forca 1-2) | 30min str1 ambos | 0.37 | +73% | 4504 |
| 133 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 30min trig3 sl0.02 ambos | 0.37 | +51% | 211 |
| 134 | 28 | hamacd | 17. Heikin Ashi MACD | 1D tp10 sl3 ambos | 0.37 | +55% | 162 |
| 135 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 1h r10 m100 ambos | 0.37 | +67% | 578 |
| 136 | 20 | t3sar |  | 1D semstop ambos | 0.37 | +54% | 24 |
| 137 | 31 | pse | 17. Parabolic SAR w/ EMA | 4h off1% ambos | 0.37 | +54% | 373 |
| 138 | 36 | kbb | 2. Kozlod BB | 1h bb55x2 ambos | 0.37 | +75% | 561 |
| 139 | 19 | 3ema | 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only) | 4h tp3 sl0 | 0.36 | +37% | 126 |
| 140 | 24 | sott | 1. SOTT | 4h s250 p0.618 ambos | 0.36 | +78% | 102 |
| 141 | 24 | tq | 4. Triple EMA + QQE | 4h p1% ambos | 0.36 | +31% | 233 |
| 142 | 36 | at3 | 16. ATR and T3 | 30min p5 long | 0.35 | -100% | 47 |
| 143 | 25 | hyb | 17. Hybrid RSI + Breakout | 30min atr2 ambos | 0.35 | +60% | 3383 |
| 144 | 26 | bx | 6. B-Xtrender | 1h trl20% ambos | 0.35 | +53% | 2392 |
| 145 | 32 | qst | 8. QuantNomad SuperTrend | 1D m3 ambos | 0.35 | +56% | 63 |
| 146 | 37 | hul | 7. Hull Suite | 1D n55 ambos | 0.35 | +65% | 103 |
| 147 | 30 | rom | 9. RSI of MACD (long-only) | 1D x15 sem stop | 0.35 | -100% | 11 |
| 148 | 21 | cons | 3. MA Consecutive Up/Down | 4h n8 ma1 ambos | 0.34 | +19% | 25 |
| 149 | 27 | sqr | 11. Squeeze Momentum on Reversal | 1h f0.0018 ambos | 0.34 | +55% | 2142 |
| 150 | 25 | pop | 22. Pivot of Pivot Reversal | 4h 4/2 ambos | 0.34 | +51% | 151 |
| 151 | 23 | dema | 8. DEMA ATR | 1h tp6 ambos | 0.34 | +51% | 673 |
| 152 | 18 | slope | 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200) | 1h 130 9/21 filtro ambos | 0.34 | +55% | 1813 |
| 153 | 17 | stcci | 1. Supertrend CCI (sinal do CCI28) | 1D cci28 ambos | 0.33 | +50% | 245 |
| 154 | 6 | bbrsi | 3. Bollinger Band with RSI (piramide 50 x 10% do capital) | 1h 20/60 bb2.5 u1 | 0.33 | +29% | 77 |
| 155 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 1D n55 ambos | 0.32 | +53% | 106 |
| 156 | 20 | frama |  | 1D 40 propriotf ambos | 0.32 | +47% | 145 |
| 157 | 36 | lrb | 13. Linear Regression Channel Breakout | 4h n50 ambos | 0.32 | +51% | 1378 |
| 158 | 31 | fxf | 14. FXFUNDINGMATE Trend | 4h tp1atr ambos | 0.32 | +21% | 306 |
| 159 | 30 | ptr | 6. Percent Trailing Stop | 1D t5% ambos | 0.32 | +47% | 128 |
| 160 | 24 | gap | 10. Gap Filling | 1h semalvo ambos | 0.32 | +34% | 944 |
| 161 | 33 | cho | 9. Money Flow (Chaikin Oscillator) | 1D 3/10 ambos | 0.32 | +53% | 279 |
| 162 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 1D bb20 2.0 sl2.0% tp2.0% ambos | 0.32 | +15% | 43 |
| 163 | 26 | kha | 17. Kozlod Heikin-Ashi | 4h k2 ambos | 0.32 | +41% | 2194 |
| 164 | 24 | best | 2. BEST Supertrend | 4h m3 ambos | 0.31 | +46% | 466 |
| 165 | 34 | mtl | 2. Market Trend Levels | 15min 12/25 adx20 ambos | 0.31 | +47% | 2359 |
| 166 | 25 | fbo | 43. Fractal Breakout | 4h ambos | 0.31 | +40% | 575 |
| 167 | 21 | bbb | 11. Bollinger Bands Breakout | 4h bb40 vol sl2% tp9% ambos | 0.31 | +48% | 300 |
| 168 | 36 | sre | 1. Stoch RSI Crossover + EMA | 1h tp3/sl2 ambos | 0.31 | +17% | 133 |
| 169 | 28 | rci | 16. RCI | 1h rci30 ambos | 0.31 | +43% | 3046 |
| 170 | 31 | mst | 6. MACD + Stochastic | 4h st14 ambos | 0.31 | +32% | 356 |
| 171 | 37 | mrs | 5. Mean-Reversion Swing | 30min n20 long | 0.31 | +18% | 480 |
| 172 | 20 | fline |  | 4h 50 2.0 ambos | 0.30 | +54% | 85 |
| 173 | 10 | pdiv | 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2) | 1h q3 m200 reg sl0.0 ambos | 0.30 | +35% | 143 |
| 174 | 30 | dip | 15. Scalping Dips On Trend (long-only) | 30min d4 tp6% | 0.30 | +22% | 19 |
| 175 | 32 | hfl | 1. Hurst Future Lines of Demarcation | 1h c20 ambos | 0.30 | +38% | 1590 |
| 176 | 26 | e5 | 1. 5 EMA | 1D rr3 ambos | 0.30 | +62% | 144 |
| 177 | 29 | mrs | 17. MACD_RSI | 30min e20 ambos | 0.30 | +41% | 5469 |
| 178 | 37 | dmm | 6. DMI Modified | 1D n9 ambos | 0.29 | +33% | 73 |
| 179 | 9 | hull | 4. Hull Swing Trader (HMA 210 do open) | 4h p400 ambos | 0.29 | +38% | 161 |
| 180 | 24 | stb | 5. SuperTrend Backtester | 1D semtp ambos | 0.29 | +23% | 61 |
| 181 | 23 | ma1020 | 12. MA 10/20 Crossover | 30min 20/50 ambos | 0.28 | +32% | 2484 |
| 182 | 29 | trap | 11. Scalping against trapped countertrend | 15min ck5 ambos | 0.28 | +40% | 2424 |
| 183 | 20 | dai |  | 4h 2/1.5 ambos | 0.28 | +34% | 368 |
| 184 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 1h 9 12/26/9 obv0 ls | 0.28 | +33% | 1470 |
| 185 | 26 | him | 7. Hull + Ichimoku + MACD | 4h h12 ambos | 0.28 | +35% | 968 |
| 186 | 23 | qqe | 7. UL QQE Cross | 4h thr5 semfiltro ambos | 0.28 | +34% | 1175 |
| 187 | 30 | gold | 4. MAster Gold | 1h 100/30 ambos | 0.28 | +31% | 1012 |
| 188 | 23 | hl41 | 4. Higher High Lower Low | 1D 41 ambos | 0.28 | +31% | 14 |
| 189 | 10 | mab | 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao) | 30min ma 20/50 ambos | 0.28 | +29% | 2153 |
| 190 | 31 | okx | 15. OKX MA Crossover | 1h 7% ambos | 0.28 | +28% | 3941 |
| 191 | 34 | gtf | 1. Gradient Trend Filter | 30min l25 ambos | 0.28 | +29% | 1551 |
| 192 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 4h len20 m2.0 ambos | 0.28 | +28% | 309 |
| 193 | 28 | pab | 6. Price Action + Bollinger | 1h bb50 ambos | 0.27 | +36% | 245 |
| 194 | 25 | gn | 41. Gianno Nano | 1D sltp ambos | 0.27 | +45% | 65 |
| 195 | 31 | alm | 1. ALMA/EMA | 4h tp6% ambos | 0.27 | +27% | 91 |
| 196 | 29 | madx | 13. Crossing MAs + ADX | 1h adx20 ambos | 0.27 | +27% | 564 |
| 197 | 32 | prv | 4. SuperTrend Enhanced Pivot Reversal | 1D f4 ambos | 0.27 | +29% | 25 |
| 198 | 29 | ged | 7. PTS Golden Edge | 4h 9/50 ambos | 0.27 | +25% | 189 |
| 199 | 25 | ffe | 15. Forex Fractal EMA Scalper | 1D tp2.0% direto ambos | 0.27 | +28% | 266 |
| 200 | 13 | scalp | 2. Scalping Trading System (SMA25/EMA200, Keltner, MACD 4/34, Stoch 10) | 30min s50 e0 ambos | 0.26 | +26% | 1923 |
| 201 | 20 | mrb |  | 1h 80 g2 m2 central ambos | 0.26 | +32% | 2167 |
| 202 | 38 | rwp | 1. Robot Wealth Pairs (BB 20x2) | 1D z2 ambos | 0.26 | +32% | 82 |
| 203 | 27 | wvs | 8. Volatility System (Wilder) | 1h arc3 ambos | 0.26 | +28% | 1323 |
| 204 | 30 | kal | 12. KALKI TFXBOT | 1h rr1.5 ambos | 0.26 | +21% | 873 |
| 205 | 33 | bes | 16. Binary Option EMA/Stoch | 4h e8 ambos | 0.26 | +27% | 815 |
| 206 | 28 | sflip | 5. Bitcoin SuperFlip | 4h f1.8 ambos | 0.26 | +26% | 427 |
| 207 | 22 | slopes | 10. Slopes | 4h 50/200 filtro ambos | 0.26 | +16% | 517 |
| 208 | rsidiv | rsidiv |  | 1D | 0.26 | -100% | 25 |
| 209 | 31 | mdb | 16. Market Dynamics HH/LL breakout | 1D lb50 long | 0.26 | +7% | 10 |
| 210 | 27 | simp | 10. Simple strat (MACD + Stoch + RSI) | 1D tp3 sl1 ambos | 0.26 | +26% | 247 |
| 211 | 32 | usc | 3. Ultimate Scalping v2 (EMA + VWAP) | 1D tp3atr ambos | 0.25 | +26% | 82 |
| 212 | 12 | tk | 1. TK Cross > EMA200 (20/60, long-only) | 1h 9/26 ema200 ambos | 0.25 | +28% | 1863 |
| 213 | 36 | dch | 11. Donchian stop entries | 30min n20 ambos | 0.25 | +26% | 4194 |
| 214 | 30 | lsr | 18. LunaOwl suporte/resistencia | 4h lb50 ambos | 0.25 | +17% | 97 |
| 215 | 30 | lin | 13. 2x Universelle Linien | 4h 50/200 ambos | 0.24 | +20% | 72 |
| 216 | 28 | ccu | 4. Crypto Crew University (MFI/RSI/StochRSI) | 1D th30 ambos | 0.24 | +11% | 32 |
| 217 | 25 | sec | 30. Stoch/EMA Cross | 1h semtp ambos | 0.24 | +24% | 603 |
| 218 | 27 | doji | 1. Doji strategy | 15min sl3% ambos | 0.24 | +16% | 5441 |
| 219 | 27 | c2ac | 19. Combo 2/20 EMA + AC | 4h e14 ambos | 0.24 | +25% | 2279 |
| 220 | 21 | joel | 12. 5min MACD scalp (Joel) | 15min tp3.0% sl2.0% ambos | 0.24 | +23% | 1623 |
| 221 | 34 | ppt | 3. Pivot Percentile Trend | 4h l10 ambos | 0.24 | +22% | 98 |
| 222 | 26 | sts | 5. SuperTrend STRATEGY | 4h m8.5 ambos | 0.24 | +15% | 101 |
| 223 | 23 | evw | 19. EVWMA x VWAP | 4h 30 ambos | 0.24 | +8% | 570 |
| 224 | 29 | kamatd | 8. KAMA TradeDots | 4h r10 ambos | 0.24 | +20% | 175 |
| 225 | 11 | easy | 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT) | 4h e15 st3.0 zig0 ambos | 0.24 | +15% | 468 |
| 226 | 37 | rcf | 20. RSI-CCI Fusion | 4h n14 ambos | 0.23 | +13% | 1211 |
| 227 | 29 | vf | 19. Volume fight | 1h ma30 ambos | 0.23 | +10% | 773 |
| 228 | 25 | flexi | 7. FlexiSuperTrend | 15min f15 ambos | 0.23 | +17% | 3041 |
| 229 | 31 | gx | 11. Golden X BF | 30min 20/100 ambos | 0.23 | +13% | 1423 |
| 230 | 27 | atf | 2. Adaptive Trend Flow | 1D filtros ambos | 0.23 | +14% | 322 |
| 231 | 18 | savwap | 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only) | 4h prd100 ambos | 0.23 | +12% | 80 |
| 232 | 26 | rsx | 12. RSI Crossover | 1D r50/25 ambos | 0.22 | +15% | 258 |
| 233 | 37 | rvc | 13. Reversal Catcher | 4h bb1.5 long | 0.22 | +13% | 25 |
| 234 | 20 | xscalp |  | 1D gap0.25% rr1 ambos | 0.22 | -9% | 2247 |
| 235 | 37 | hle | 11. HL MovingAvg2Line Cross | 1D n9 ambos | 0.22 | +14% | 197 |
| 236 | 4 | aist |  | 1h 4h/1D f3.5/3.0 adx0 | 0.22 | +20% | 220 |
| 237 | 32 | stdbf | 2. Super Trend Daily BF | 1D m2.6 ambos | 0.22 | +20% | 46 |
| 238 | 24 | hst | 6. HMA50 + Supertrend | 1D h50 ambos | 0.21 | +18% | 91 |
| 239 | 33 | ich | 20. Ichimoku + EMA filter | 1h ema ambos | 0.21 | +16% | 2321 |
| 240 | 36 | vrb | 14. Volatility Range Breakout | 15min n50 ambos | 0.21 | +20% | 1795 |
| 241 | 32 | r2 | 7. AK RSI 2 | 1D 5/90 long | 0.21 | +5% | 23 |
| 242 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 1D a0.5 c7 | 0.21 | +8% | 573 |
| 243 | 25 | made | 4. MA Displaced Envelope + ATRTS | 4h 30 ambos | 0.21 | +12% | 640 |
| 244 | 4 | ppst | 2. Pivot Point SuperTrend (2, 3, 10) | 1D p2 f2.0 a20 | 0.21 | +1% | 54 |
| 245 | 24 | vws | 16. VWMA/SMA 3Commas | 1D semniveis ambos | 0.21 | +13% | 253 |
| 246 | 30 | scl | 17. 1 min forex scalping | 30min x1 ambos | 0.20 | +6% | 2150 |
| 247 | 24 | d3 | 13. DEMA 8/20/63 | 30min x1 ambos | 0.20 | +4% | 3866 |
| 248 | 23 | tema | 11. Triple EMA Trend | 15min adx43 ambos | 0.20 | +15% | 1614 |
| 249 | 33 | r3 | 11. 3 RSI | 30min 30/70 ambos | 0.20 | +8% | 274 |
| 250 | 30 | mmr | 7. Multiple MACD RSI | 30min 12/26 ambos | 0.20 | -0% | 3576 |
| 251 | 15 | es | 4. EMA STOCH (Crypto BOT lower timeframes) | 30min sl/tp1% long | 0.20 | +3% | 46 |
| 252 | 29 | bbf | 16. Bull and Bear Fear | 1h n30 ambos | 0.20 | +3% | 2202 |
| 253 | 28 | pmax | 8. PMax | 1D m1.5 ambos | 0.19 | +1% | 51 |
| 254 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 4h a20 m2 ambos | 0.19 | +3% | 775 |
| 255 | 22 | crsi | 19. Cumulative RSI (long-only) | 1D 20/94 | 0.19 | -100% | 12 |
| 256 | 25 | drm | 13. Dynamic RSI Momentum | 30min 20/80 ambos | 0.19 | +26% | 37 |
| 257 | 26 | ksr | 9. KSR (EMA 10/20) | 1D 10/20 ambos | 0.19 | +6% | 103 |
| 258 | 16 | emax | 4. EMA Cross 10/20 | 1D 10/20 ambos | 0.19 | +6% | 103 |
| 259 | 23 | ttm | 18. Trend Trader + MACD | 1D m1.5 semmacd ambos | 0.19 | +4% | 361 |
| 260 | 34 | mls | 8. ML SuperTrend kNN | 4h f4 tp0 ambos | 0.19 | +5% | 472 |
| 261 | 25 | thma | 9. Triangular Hull MA | 4h 40 ambos | 0.19 | +4% | 541 |
| 262 | 36 | mbd | 20. MACD Short/Long TVIO | 1D sl21 ambos | 0.19 | +7% | 84 |
| 263 | 23 | rsipa | 17. RSI PrimeAutomation | 15min s4 tp7 ambos | 0.19 | +16% | 1860 |
| 264 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 1D a14 m2 ambos | 0.19 | +13% | 120 |
| 265 | 23 | bbst | 2. BBTrend + SuperTrend | 30min f7 ambos | 0.19 | -1% | 4629 |
| 266 | 14 | hap | 2. Heikin-Ashi PSAR [QuantNomad] | 30min 0.005/0.005/0.05 ambos | 0.19 | -1% | 2804 |
| 267 | 22 | ichi | 8. Ichimoku no offset + RSI | 4h rsi0 ambos | 0.19 | +7% | 286 |
| 268 | 37 | rsc | 16. RSI Classic (Coinrule) | 1D 30/60 | 0.19 | +14% | 14 |
| 269 | 36 | atr | 17. ATR Reversed | 4h 5/3.5 ambos | 0.18 | +6% | 378 |
| 270 | 24 | hf | 12. Hull Fisher | 1D h50 ambos | 0.18 | +10% | 100 |
| 271 | 17 | grid | 2. Grid Like (linha-base, alvo/stop = point) | 1D p1.00% ambos | 0.18 | -9% | 1479 |
| 272 | 27 | ichb | 17. Ichimoku Backtester | 4h 9/26/52 ambos | 0.18 | +10% | 77 |
| 273 | 36 | btm | 4. Beat the market (filtro de vol) | 1D p95/w250 | 0.18 | -100% | 26 |
| 274 | 29 | hlc | 2. High/Low channel swing | 4h l12 ambos | 0.18 | +1% | 1556 |
| 275 | 38 | smx | 4. SMAcross-mvr | 1h 10/50 ambos | 0.17 | -4% | 1419 |
| 276 | 32 | tss | 18. TSI w SuperTrend decision | 1D p32 ambos | 0.17 | -2% | 78 |
| 277 | 25 | 4ma | 48. Multi-MA (4MA) | 1D wma200 ambos | 0.17 | -34% | 40 |
| 278 | 22 | hhll | 13. Highest High / Lowest Low | 4h 55 ambos | 0.17 | -2% | 134 |
| 279 | 22 | emax | 2. EMA Crossover hl2 | 30min 20x3 ambos | 0.17 | -8% | 1816 |
| 280 | 31 | lst | 13. LunaOwl SuperTrend 2 | 1D m2.618 ambos | 0.17 | -0% | 74 |
| 281 | vixfix | grade |  | 15min ph0.95 str5 ob70 aggr u1 | 0.16 | +8% | 206 |
| 282 | 25 | mst | 11. Master Supertrend | 15min 60 m4 ambos | 0.16 | -12% | 2108 |
| 283 | 32 | hic | 13. Hull MA_X + Ichimoku | 1h h24 ambos | 0.16 | +4% | 2787 |
| 284 | 20 | ceyhun |  | 1D m2 3 ambos | 0.16 | -2% | 62 |
| 285 | 26 | lbo | 19. London BreakOut Classic | 4h rr2 ambos | 0.16 | +8% | 2460 |
| 286 | 25 | ao | 49. Awesome Oscillator | 4h ambos | 0.16 | -10% | 2520 |
| 287 | 30 | stpb | 14. Supertrend pullback | 4h flip ambos | 0.15 | +5% | 227 |
| 288 | 32 | koz | 20. Kozlod MA Cross | 1h 10/30 ambos | 0.15 | -10% | 2078 |
| 289 | 28 | sma3 | 19. Tres medias (SMA 7/25/99) | 4h 7/99 ambos | 0.15 | -6% | 297 |
| 290 | 36 | ral | 8. RSI Alligator | 1D sl10 ambos | 0.15 | -6% | 283 |
| 291 | 25 | moon | 8. Moon Phases | 1D normal ambos | 0.15 | -9% | 237 |
| 292 | 26 | hama | 11. NSDT HAMA (EMA55) | 1D e20 ambos | 0.14 | -8% | 174 |
| 293 | 30 | hul | 1. Hull MA and Candle cross | 30min z100 ambos | 0.14 | -13% | 6903 |
| 294 | 24 | alpha | 20. AlphaTrend | 30min mfi ambos | 0.14 | -14% | 2861 |
| 295 | 28 | hvc | 14. Hull MA vs Candle | 1h h50 ambos | 0.14 | -12% | 1802 |
| 296 | 21 | renko | 14. Renko Open_Close (Pro) | 1D m1 ambos | 0.14 | +0% | 568 |
| 297 | 33 | vxe | 18. VWAP X EMA | 1h ema50 ambos | 0.14 | -10% | 2431 |
| 298 | 28 | ibm | 20. Babypips Inside Bar Momentum | 1h tp2 ambos | 0.14 | +7% | 4726 |
| 299 | 26 | dm | 18. DEMA + MACD | 1D d21 ambos | 0.14 | -10% | 459 |
| 300 | 32 | stt | 16. SuperTrend Trapping Candle | 4h 0.3% ambos | 0.13 | -100% | 62 |
| 301 | 34 | kmt | 5. Ichimoku Kumo Twist | 15min stop ambos | 0.13 | -12% | 4358 |
| 302 | 21 | surf | 1. Trend Surfers Breakout | 4h p55 t8.0 f2.0 ambos | 0.13 | -5% | 201 |
| 303 | 29 | bsc | 5. Breakout Scalper | 15min 20/100 ambos | 0.13 | +1% | 2597 |
| 304 | 28 | t3cci | 7. FX Sniper T3-CCI | 1D cci14 ambos | 0.13 | -12% | 205 |
| 305 | 32 | irs | 6. Ichimoku Cloud with RSI (Coinrule) | 4h rsi50 ambos | 0.13 | -12% | 133 |
| 306 | 37 | sts | 9. 3x Supertrend + Stoch RSI | 1D tp1.6 ambos | 0.13 | +4% | 96 |
| 307 | 32 | fis | 15. Fisher Transform (Ehlers) | 1h l20 ambos | 0.13 | -16% | 2651 |
| 308 | 13 | ichi | 5. Ichimoku basico (9/26/52, deslocamento 26) | 15min 20/60/120 ambos | 0.13 | -15% | 1832 |
| 309 | 26 | qc | 8. QuantCat Intraday | 30min atr4 ambos | 0.13 | -14% | 1513 |
| 310 | 27 | e3 | 16. 3 EMA + Stoch RSI + ATR | 1D tp2 ambos | 0.12 | +2% | 301 |
| 311 | 25 | kpl | 40. KPL Swing | 1D 20 ambos | 0.12 | -29% | 49 |
| 312 | 36 | rs2 | 10. RSI 2 + tendencia, trailing | 30min ts3 ambos | 0.11 | -11% | 1252 |
| 313 | 26 | vst | 2. Vegas SuperTrend Enhanced | 1D b2 ambos | 0.11 | -13% | 123 |
| 314 | 36 | sqz | 18. Squeeze Momentum | 4h e50 ambos | 0.11 | +5% | 239 |
| 315 | 20 | rsirev |  | 30min 8 1.5 normal ambos | 0.11 | -22% | 1626 |
| 316 | 37 | bbr | 4. Big Bar | 1h a4 ambos | 0.11 | -1% | 1221 |
| 317 | 28 | gch | 18. Gaussian Channel | 1D p50 ambos | 0.11 | -14% | 203 |
| 318 | 24 | vwap | 17. VWAPStrategy | 4h sma20 ambos | 0.11 | -22% | 1096 |
| 319 | 27 | flash | 7. The Flash | 1D mr60 ambos | 0.11 | -11% | 52 |
| 320 | 28 | mab | 13. Moving Average (BiznesFilosof) | 1D sma21 ambos | 0.10 | -16% | 273 |
| 321 | 27 | gsc | 6. Gold Scalping | 1h tp2atr ambos | 0.10 | +4% | 998 |
| 322 | 27 | atrts | 15. ATR Trailing Stops | 1D a5x3.5 ambos | 0.10 | -32% | 48 |
| 323 | 32 | dcs | 10. Donchian Channel (stop + EMA200) | 30min d20 ambos | 0.10 | -11% | 2903 |
| 324 | 7 | srt | 5. SR TREND (21) | 1h len100 | 0.10 | -20% | 1278 |
| 325 | 20 | ypmax |  | 1D 13 3 ambos | 0.09 | -30% | 50 |
| 326 | 20 | macd |  | 1D m4.0 tp5% semfiltro | 0.09 | -100% | 42 |
| 327 | 20 | kelt |  | 1D 40 2.0 tp6% sl2% tend | 0.09 | +3% | 13 |
| 328 | 17 | ftsma | 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier) | 4h 5/20/200 ft ambos | 0.09 | -20% | 323 |
| 329 | 3 | ann | 4. ANN Strategy v2 | 1D thr 0 | 0.09 | -26% | 917 |
| 330 | 30 | mbf | 16. Momentum BF | 1D l18 ambos | 0.08 | -20% | 238 |
| 331 | 25 | smp | 50. Smart Money Pivot | 1D p20 sl1 tp1.5 ambos | 0.07 | +2% | 36 |
| 332 | 33 | snr | 12. Signal To Noise | 1D l21 ambos | 0.07 | -21% | 97 |
| 333 | 30 | mma | 3. Multi-MA | 30min l66 ambos | 0.07 | -29% | 1754 |
| 334 | 30 | gso | 8. Gann Swing Oscillator | 1h l10 ambos | 0.06 | -35% | 1105 |
| 335 | 30 | tsh | 2. TrendShift Supertrend + ADX | 30min m3 ambos | 0.06 | -30% | 1456 |
| 336 | 25 | htf | 5. Hull MA TimeFrame CrossOver | 1h 200 s3 ambos | 0.06 | -29% | 228 |
| 337 | 23 | stv | 16. Super trend V | 1D m3 ambos | 0.06 | -32% | 58 |
| 338 | 22 | xsc | 15. XAUUSD Scalping V2 | 4h tp3 sl1.5 ambos | 0.05 | -13% | 956 |
| 339 | 22 | turtle | 6. Real Turtle (stops) | 1D 20/10 n4 ambos | 0.05 | -21% | 96 |
| 340 | 32 | dkw | 14. Donchian Channels (KrisWaters) | 1D canal ambos | 0.05 | -21% | 96 |
| 341 | 21 | rsitc | 4. RSI Trend Crypto (long-only) | 1D 35/75 | 0.05 | -100% | 10 |
| 342 | 29 | chb | 20. Channel Break (free bot) | 1D canal ambos | 0.04 | -30% | 98 |
| 343 | 25 | ce | 1. Chandelier Exit | 1h risco ambos | 0.04 | -30% | 2151 |
| 344 | 16 | aivst | 3. AI Volume SuperTrend (10, 3; rotulo WMA20 vs WMA100 do ST) | 30min l20 f3 ambos | 0.04 | -25% | 1823 |
| 345 | 32 | cce | 12. CCI & EMA (Tradeswithashish) | 1h tp5% ambos | 0.04 | -19% | 1081 |
| 346 | 25 | rbd | 19. RSI Bull Div (long-only) | 4h tp3 sl1.75 | 0.03 | +2% | 37 |
| 347 | 22 | psarc | 14. Parabolic SAR on close | 1D n3 0.01/0.1 ambos | 0.03 | -30% | 101 |
| 348 | 36 | vst | 3. Multi-Step Vegas SuperTrend | 1D b2 ambos | 0.03 | -29% | 66 |
| 349 | 28 | k3ma | 2. Kozlod 3 MA | 4h sma ambos | 0.03 | -30% | 100 |
| 350 | 31 | ttm | 2. TTM scalper | 1D inv ambos | 0.03 | -39% | 491 |
| 351 | 28 | stc | 12. SuperTrend Cloud | 1D m2.4/4.8 ambos | 0.02 | -21% | 64 |
| 352 | zigzagpa | hon_long |  | 1h ew.236 tp.618 sl-.236 | 0.02 | -0% | 430 |
| 353 | 21 | guppy | 19. Super Guppy | 30min ambos | 0.01 | -40% | 2644 |
| 354 | 25 | bas | 45. BEST ATR Stop Multiple | 1h atr4 ambos | 0.01 | -40% | 1424 |
| 355 | 33 | ers | 13. EMA + RSI Sniper (long-only) | 4h tp5/sl3 | 0.01 | -5% | 172 |
| 356 | 26 | dma | 15. Dual Moving Average (angulo) | 4h a3 ambos | 0.01 | -35% | 472 |
| 357 | 25 | mas | 23. Mov Avg Speed (3 sinais) | 4h ambos | 0.01 | -41% | 491 |
| 358 | 33 | hcx | 15. Hull MA Crossover | 1h h28 ambos | 0.00 | -38% | 3394 |
| 359 | 28 | gvto | 9. Golden Vector Trend Orchestrator | 4h adx0 ambos | 0.00 | -34% | 278 |
| 360 | 25 | bts | 27. BEST Trailing Stop | 1D tr3% ambos | -0.01 | -14% | 58 |
| 361 | 24 | beng | 18. Bullish Engulfing (long-only) | 1D sl2.00% tp2.00% semtend | -0.02 | -4% | 97 |
| 362 | 35 | lpr | 1. Linear Regression Pearson | 30min k360 sempre ambos | -0.02 | -42% | 1324 |
| 363 | 25 | sr | 3. Support Resistance | 1D 10 ambos | -0.02 | -41% | 67 |
| 364 | 37 | lag | 1. Laguerre RSI | 1h a0.2 ambos | -0.03 | -46% | 1679 |
| 365 | 25 | uhl | 35. Uhl MA System | 4h 100 ambos | -0.03 | -41% | 121 |
| 366 | 25 | imct | 16. Ichimoku + MACD/CMF/TSI | 15min ambos | -0.04 | -48% | 3108 |
| 367 | 29 | bbe9 | 6. Bollinger Bands + EMA 9 | 1D bb20 ambos | -0.04 | -12% | 128 |
| 368 | 27 | ssl | 18. SSL Channel Cross | 4h l10 ambos | -0.06 | -48% | 1262 |
| 369 | 25 | spym | 39. SPY Master | 1D ambos | -0.06 | -48% | 332 |
| 370 | 25 | rmr | 14. Range Strat MACD/RSI | 4h sl5% ambos | -0.08 | -46% | 362 |
| 371 | 31 | cmb | 20. Combo 123 Reversal & Stochastic | 15min l28 ambos | -0.09 | -47% | 4271 |
| 372 | 27 | tfb | 12. Trend Following Breakout | 4h 20/10 ambos | -0.09 | -40% | 588 |
| 373 | 25 | c123r | 18. Combo 123 Reversal + RSI | 30min ambos | -0.10 | -49% | 1365 |
| 374 | 31 | csc | 10. Crypto Price Scalper (long-only) | 4h cc60 st3% | -0.10 | -6% | 49 |
| 375 | 30 | ott | 10. Optimized Trend Tracker | 4h 0.1% ambos | -0.10 | -58% | 2448 |
| 376 | 23 | nr7 | 5. NR7 + Inside Day (long-only) | 1D sma14 | -0.10 | -5% | 23 |
| 377 | 37 | dmx | 12. DMI + nuvem Ichimoku | 1D adx25 ambos | -0.10 | -35% | 254 |
| 378 | 23 | combo | 14. Combo 123 Reversal + SMI | 1D smi50 ambos | -0.10 | -36% | 643 |
| 379 | zigzagpa | hon_short |  | 4h ew.236 tp.618 sl-.236 | -0.12 | -5% | 208 |
| 380 | 27 | wyk | 13. Wyckoff Range | 30min sl3% ambos | -0.12 | -50% | 1211 |
| 381 | 38 | kij | 2. Kijun-Sen DasanC | 4h n20 ambos | -0.13 | -40% | 744 |
| 382 | 22 | renko | 12. Renko Strategy V2 | 4h atr10 ambos | -0.13 | -59% | 1123 |
| 383 | 29 | wtr | 18. BTC WaveTrend R:R (long-only) | 4h rr1.5 lim-40 | -0.14 | -25% | 263 |
| 384 | 26 | pdb | 13. Previous Day High/Low Breakout | 4h hl ambos | -0.17 | -64% | 1112 |
| 385 | 20 | alli |  | 1D ha ambos | -0.19 | -51% | 181 |
| 386 | 36 | pin | 6. Pinbar | 4h pm2 ambos | -0.20 | -44% | 503 |
| 387 | 25 | bbe | 2. Bollinger Bands Enhanced (long-only) | 30min sl3 | -0.21 | -34% | 1221 |
| 388 | 25 | masc | 26. MA Scalper Coinrule (long-only) | 1D sl2 tp8 | -0.22 | -13% | 13 |
| 389 | 33 | s200 | 5. SMA 200 bands (long-only) | 15min 1.04/0.99 | -0.23 | -32% | 103 |
| 390 | flawless | flawless |  | 1D | -0.23 | -100% | 10 |
| 391 | 25 | mcci | 34. MACD + CCI | 4h ambos | -0.24 | -72% | 2729 |
| 392 | zigzagpa | honesto |  | 30min ew.236 tp.618 sl-.236 | -0.24 | -14% | 935 |
| 393 | 37 | c12r | 10. Combo 123 + Rainbow Oscillator | 1D ro2 ambos | -0.24 | -50% | 306 |
| 394 | 25 | era | 31. EMA Cross + RSI + ADX | 4h sl5% ambos | -0.26 | -51% | 305 |
| 395 | 25 | vwbo | 29. VWAP Breakout | 4h tp4 ambos | -0.27 | -74% | 5356 |
| 396 | 4 | tdh | 3. Trend Direction Helper (RISK 10, SMA 7/20) | 4h r0 7/20 | -0.28 | -76% | 4048 |
| 397 | 36 | mst | 7. Trend Entry 0 (estrutura) | 1D ambos | -0.29 | -70% | 466 |
| 398 | 32 | gps | 9. Grant's PSAR (long-only) | 1D 0.013/0.2 | -0.29 | -55% | 31 |
| 399 | 24 | lht | 14. Low-High Trend (long-only) | 4h tp8 | -0.30 | -43% | 10 |
| 400 | 33 | vct | 6. TASC 2024.08 VCTS (long-only) | 1D adx30/vp50 | -0.31 | -36% | 10 |
| 401 | 26 | tcci | 20. Triple CCI + MFI (long-only) | 4h sl3 at1 | -0.34 | -36% | 144 |
| 402 | 8 | vwap | 3. VWAP Trendfollow (sessao, 0.88 desvio, saida na banda 2) | 1h m0.5 match1 tp0.0 ambos | -0.34 | -79% | 6611 |
| 403 | 37 | tdw | 19. Gold TDOW (MACD+Stoch+RSI) | 1h tdow | -0.34 | -49% | 1422 |
| 404 | 21 | strex | 6. SuperTREX (RSI semanal amostrado) | 4h m4 ambos | -0.34 | -73% | 94 |
| 405 | 31 | haw | 4. Heikin Ashi Wick (long-only) | 1D candle nowick | -0.34 | -100% | 12 |
| 406 | 37 | ckr | 2. Chande Kroll Stop | 1h n21/a1.5 | -0.34 | -28% | 1079 |
| 407 | 33 | pac | 1. PSAR + ADX + CMF + RSI (long-only) | 1D rsi50/cmf40 | -0.35 | -82% | 14 |
| 408 | 27 | rdip | 3. Optimized RSI Buy The Dips (long-only) | 1D 30/70 sma100 | -0.40 | -59% | 10 |
| 409 | 32 | rdv | 11. RSI Divergence Strategy | 1h rsi<35 ambos | -0.42 | -57% | 32 |
| 410 | 15 | btcb | 5. BTC bot (cc do RSI21 x 0; saida no R3 semanal) | 1D sl15% tp5% ambos | -0.43 | -33% | 15 |
| 411 | 25 | muta | 21. Mutanabby AI Algo Pro (long-only) | 1D sl2 | -0.46 | -43% | 46 |
| 412 | 23 | dip | 15. Buying Dip (long-only) | 4h d20 tp2 sl2 | -0.49 | -56% | 437 |
| 413 | 22 | mrsi | 4. Easy MACD + RSI (long-only) | 1D rsi50 semstop | -0.50 | -55% | 16 |
| 414 | 26 | kama | 10. KAMA Strategy (long-only) | 1D f1 atr3 | -0.53 | -68% | 53 |
| 415 | vixfix | u1 |  | 4h default | -0.54 | -73% | 130 |
| 416 | 37 | b4u | 8. IU 4 Bar UP | 1D f1 | -0.54 | -63% | 62 |
| 417 | 21 | mbr | 10. MACD + BB + RSI (long-only) | 1D semstop | -0.55 | -94% | 11 |
| 418 | 38 | tsl | 3. Trailing Stop Loss (SMA 21/49) | 4h 50/200 tsl7.5 | -0.55 | -61% | 39 |
| 419 | 23 | zzrsi | 13. ZigZag RSI (long-only) | 30min r14 30/70 zz1 | -0.57 | -73% | 106 |
| 420 | 37 | mdv | 3. MACD + DMI + Volatility Stop | 1h semtp | -0.57 | -63% | 802 |
| 421 | 25 | davin | 25. Davin 10/200 MA Pullback (long-only) | 4h dip14 sl5 | -0.58 | -78% | 418 |
| 422 | 31 | ich | 3. Advanced Ichimoku (long-only) | 30min ent strong sai weak | -0.58 | -70% | 842 |
| 423 | 34 | ttl | 9. Turtle (uma unidade, long) | 1D 55/55/20/20 sem filtro | -0.59 | -65% | 20 |
| 424 | 26 | mrr | 14. MACD, RSI & RVOL (long-only) | 1h 40/60 rv1.5/1.5 | -0.60 | -79% | 269 |
| 425 | 23 | vwpb | 20. VWAP Momentum Pullback (long-only) | 4h sl3% tp7% rsi30 | -0.61 | -57% | 122 |
| 426 | 27 | bbbo | 9. Bollinger Band Breakout (long-only) | 4h m2 basis | -0.62 | -62% | 263 |
| 427 | 29 | atsl | 1. ATR Trailing Stoploss | 1h m2.5 ambos | -0.62 | -89% | 5732 |
| 428 | 23 | coin | 6. Coinrule Scalping On Trend (long-only) | 4h 70/30 | -0.63 | -69% | 192 |
| 429 | 25 | rsim | 24. RSI mensal (long-only) | 4h padrao | -0.63 | -80% | 10 |
| 430 | 25 | elo | 20. EMA Long Only | 1D 21 | -0.64 | -81% | 29 |
| 431 | 21 | bbao | 8. BB + AO (long-only) | 1D bb5 | -0.66 | -81% | 42 |
| 432 | 25 | mx | 32. Multi-X (long-only) | 1D padrao | -0.68 | -81% | 60 |
| 433 | 30 | rbs | 19. RSI Buy and Sell (long-only) | 4h 70/30 | -0.69 | -80% | 59 |
| 434 | 29 | dbo | 3. Donchian Breakout (long-only) | 1D d20 basis | -0.70 | -70% | 45 |
| 435 | vixfix | default |  | 1D default | -0.71 | -67% | 18 |
| 436 | 26 | mel | 4. MACD + EMA (long-only) | 1h semfiltro 12/26 | -0.71 | -83% | 2111 |
| 437 | 31 | sha | 18. Smoothed Heiken Ashi (long-only) | 1D 20/10 | -0.73 | -83% | 40 |
| 438 | 22 | btf | 20. Breakout Trend Follower (long-only) | 1D p3 sma50 | -0.73 | -80% | 48 |
| 439 | 21 | msr | 18. MACD + Stoch + RSI (long-only) | 1h k50 | -0.75 | -81% | 1809 |
| 440 | 27 | stt | 4. Stochastic Trend (long-only) | 4h k200/100 x50 | -0.77 | -86% | 30 |
| 441 | 37 | qts | 14. Quantitative Trend (pivo) | 1D tp2/sl1.75 | -0.80 | -90% | 724 |
| 442 | 31 | akt | 9. AK Trend ID (long-only) | 1D 5/13 | -0.83 | -86% | 96 |
| 443 | 33 | vat | 4. VWMA with ATR stops (long-only) | 1D 2.5atr/20 | -0.83 | -82% | 42 |
| 444 | 33 | haw | 2. Abdoli's Heikin Ashi Smoothed (long-only) | 1D ema30/2velas | -0.86 | -87% | 58 |
| 445 | 28 | bbw | 15. Bollinger Breakout (long-only, stop) | 4h bb50 banda | -0.91 | -87% | 106 |
| 446 | 37 | obv | 17. OBV Acumulacao/Distribuicao | 1h n50 | -0.92 | -90% | 1293 |
| 447 | 25 | stma | 12. State-aware MA Cross (long-only) | 4h padrao | -1.02 | -95% | 765 |
| 448 | 28 | planb | 3. PlanB Quant Investing 101 | 4h top80 ambos | -1.05 | -100% | 35 |
| 449 | 24 | btcm | 11. Bitcoin Momentum (long-only) | 1D atr1 | -1.20 | -85% | 129 |
| 450 | 25 | tra | 33. Trend Reversal Alerts (long-only) | 1D padrao | -1.23 | -93% | 207 |
