# WTI em 4 partes (seleção sem OOS)

Pedido de 2026-10-28: retestar no WTI as estratégias dos lotes com a grade curta, dados M1 Dukascopy divididos em 5 partes iguais no tempo. A 5ª parte (de 2024-10-19 em diante) é OOS e não é carregada. Sem variantes `peek`, custos e funding de sempre.

- Aprovada: a melhor célula tem retorno composto nas 4 partes ≥ 0,5 × B&H do mesmo período.
- Ordem: média geométrica das 4 partes, exp(média ln(1+r_i)) − 1.
- Não rerodadas (motores próprios): bbrsi, commas, flipma, goldtrail, ict2022, ictsuite, macdconf, macdsma, serdar, tlangle.
- Atenção: a parte 2 contém abril de 2020 (petróleo negativo); retornos gigantes ali são suspeitos.

```
cortes: ['2017-01-03', '2018-12-15', '2020-11-26', '2022-11-07', '2024-10-19']
B&H por parte: ['-5.2%', '-10.4%', '+100.1%', '-25.1%']  total +27.4%  limite +13.7%
451 estrategias, 19349 celulas; aprovadas 304; com as 4 partes positivas 31
```

| # | Lote | Est | Nome | Célula | P1 | P2 | P3 | P4 | Total 4p | Geo | Trades |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 2/2 | +199% | +4921% | +237% | +62% | +81760% | +435% | 38174.0 |
| 2 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 4h r14 w30 d3 signal ambos | -12% | +950% | +113% | +80% | +3434% | +144% | 1332.0 |
| 3 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 4h como escrito ambos | +106% | +188% | +122% | +60% | +2004% | +114% | 40.0 |
| 4 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.0 roc6.0 m3.0/3.0 ambos | +56% | +172% | +40% | +222% | +1807% | +109% | 155.0 |
| 5 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 1h 100/50/7 ambos | -28% | +748% | +68% | +48% | +1425% | +98% | 1649.0 |
| 6 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 30min l50 e40 ambos | +129% | +376% | -13% | +36% | +1187% | +89% | 911.0 |
| 7 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 30min n30 12/26 ambos | +39% | +391% | +24% | +40% | +1089% | +86% | 2827.0 |
| 8 | 22 | pmax | 16. PMax on RSI w T3 | 15min m3 t8 ambos | -8% | +421% | +112% | +8% | +997% | +82% | 1924.0 |
| 9 | 25 | sta | 38. Stoch + ATR | 4h 14 ambos | -34% | +408% | +116% | +45% | +953% | +80% | 827.0 |
| 10 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 30min fiel ambos | +73% | +320% | -17% | +62% | +884% | +77% | 595.0 |
| 11 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 1D SHORT p1 m1.0 sl1.0 | +81% | +109% | +30% | +100% | +876% | +77% | 222.0 |
| 12 | 30 | hms | 20. Harmonic System | 4h close ambos | +65% | +523% | -12% | +4% | +840% | +75% | 1452.0 |
| 13 | 27 | obv | 20. OBV Oscillator | 1h l50 ambos | -26% | +699% | -25% | +103% | +795% | +73% | 1548.0 |
| 14 | 29 | bot | 14. BotBot | 1D k0.02 ambos | +50% | +270% | +9% | +44% | +771% | +72% | 88.0 |
| 15 | 27 | spk | 14. Martin Pring's Special K | 1D s30 ambos | +191% | +80% | +74% | -6% | +759% | +71% | 29.0 |
| 16 | 26 | csq | 3. Crypto Squeeze | 1D mfi14 ambos | +32% | +334% | +94% | -24% | +747% | +71% | 50.0 |
| 17 | 28 | pab | 6. Price Action + Bollinger | 1D bb21 ambos | -28% | +512% | +82% | +0% | +702% | +68% | 13.0 |
| 18 | 28 | l2r | 11. L2 Reversal Labels | 30min semtpsl ambos | +19% | +396% | +2% | +32% | +692% | +68% | 454.0 |
| 19 | 25 | tlb | 42. Trendline Breakout KedArc | 4h p5 semma ambos | -10% | +240% | +76% | +47% | +691% | +68% | 571.0 |
| 20 | 26 | pprs | 16. Pivot Point Reversal + RSI | 15min pv3/3 ambos | +17% | +814% | -2% | -30% | +631% | +64% | 9692.0 |
| 21 | 22 | force | 17. Force trade scalper | 4h 5/50 ambos | +142% | +308% | -59% | +73% | +604% | +63% | 156.0 |
| 22 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 4h sl4.0% rr5 ambos | +80% | +123% | +47% | +14% | +574% | +61% | 243.0 |
| 23 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w140 -94/-6 sl0.005 contrario ambos | +28% | +22% | +167% | +55% | +545% | +59% | 1934.0 |
| 24 | 36 | mma | 15. Multi Moving Average Crossing | 15min 9/50/100 ambos | -10% | +305% | +95% | -11% | +532% | +59% | 1942.0 |
| 25 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 15min sl0% tp35% filtros ambos | +2% | +136% | +26% | +103% | +515% | +57% | 982.0 |
| 26 | 20 | nw |  | 1D 8 x25 ambos | +103% | +361% | -24% | -14% | +512% | +57% | 163.0 |
| 27 | 20 | ds |  | 1h 8/34 ambos | -13% | +289% | +89% | -7% | +499% | +56% | 2110.0 |
| 28 | 22 | tsi | 5. TSI CCI Hull | 15min tp0.0% ambos | -6% | +506% | +26% | -18% | +494% | +56% | 2137.0 |
| 29 | 24 | sott | 1. SOTT | 4h s250 p0.618 ambos | -14% | +404% | +29% | +3% | +469% | +54% | 78.0 |
| 30 | 37 | chk | 18. Chaloke System | 4h 20/50/100 ambos | +36% | +161% | +17% | +36% | +462% | +54% | 196.0 |
| 31 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 1h TILL 12/26/9 | -20% | +374% | +46% | -1% | +452% | +53% | 2329.0 |
| 32 | 27 | tch | 5. TSI CCI Hull | 15min p25 ambos | -24% | +547% | +6% | +5% | +447% | +53% | 2128.0 |
| 33 | ichimoku | ichimoku |  | 15min | +92% | +121% | -21% | +60% | +435% | +52% | 452.0 |
| 34 | 29 | rss | 10. RSI and SMA (Coinrule) | 15min 50/100 ambos | -24% | +191% | +157% | -8% | +420% | +51% | 1193.0 |
| 35 | 18 | tdi | 1. Traders Dynamic Index (forca 1-2) | 1h str2 ambos | -17% | +1464% | -33% | -41% | +419% | +51% | 2927.0 |
| 36 | 16 | qqe | 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao) | 1h XZ f5 semfil ambos | -19% | +382% | +26% | +2% | +405% | +50% | 1628.0 |
| 37 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 30min sw20 sl8atr tp0% ambos | +8% | +268% | +1% | +20% | +382% | +48% | 1605.0 |
| 38 | 29 | vf | 19. Volume fight | 1h ma11 ambos | +21% | +675% | +0% | -50% | +367% | +47% | 3539.0 |
| 39 | 22 | tdon | 9. Turtle Donchian/ATR | 1h 20/10 m2 short | +21% | +192% | -30% | +87% | +364% | +47% | 695.0 |
| 40 | 29 | ged | 7. PTS Golden Edge | 4h 9/50 ambos | +41% | +302% | -19% | -0% | +357% | +46% | 145.0 |
| 41 | 34 | khw | 10. Kahlman HullMA / WT Cross | 1h h48 sem wt ambos | -8% | +181% | +43% | +21% | +345% | +45% | 2380.0 |
| 42 | 24 | srvi | 7. Stochastic RSI + RVI | 4h p10 30/70 ambos | +26% | +178% | +38% | -10% | +332% | +44% | 286.0 |
| 43 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 1h 12/26/9 ambos | +8% | +402% | +33% | -41% | +330% | +44% | 3693.0 |
| 44 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 30min hon HULL21 x5 | -34% | +419% | -8% | +35% | +324% | +43% | 1768.0 |
| 45 | 21 | cons | 3. MA Consecutive Up/Down | 4h n8 ma1 ambos | +16% | +92% | +9% | +74% | +323% | +43% | 20.0 |
| 46 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 30min 12 2 ambos | -18% | +386% | -5% | +7% | +303% | +42% | 1216.0 |
| 47 | 5 | pvb | 1. Price and Volume Breakout (60/60/200, so long) | 1h 20/50 x5 vol1 ls | +32% | +115% | +5% | +34% | +302% | +42% | 502.0 |
| 48 | 29 | lrcb | 12. Linear Regression Channel Breakout | 1D dv2.3 ambos | +49% | +1% | +27% | +108% | +300% | +41% | 34.0 |
| 49 | 34 | fmv | 4. FlexiMA Variance Tracker | 15min f15 ambos | -16% | +613% | -16% | -21% | +298% | +41% | 2278.0 |
| 50 | 20 | frama |  | 1D 40 propriotf ambos | -37% | +393% | +27% | +0% | +297% | +41% | 119.0 |
| 51 | 8 | eng | 4. Engulfing + SMA32 | 4h ma16 sl0.02 tp0.2 ambos | -6% | +146% | +50% | +15% | +295% | +41% | 890.0 |
| 52 | 24 | smc | 8. SMC | 1D lb30 ambos | +62% | +149% | -61% | +150% | +295% | +41% | 27.0 |
| 53 | 34 | azl | 7. Adaptive Zero Lag EMA | 1h cos thr0.05 ambos | +28% | -38% | +462% | -12% | +292% | +41% | 4452.0 |
| 54 | 31 | psw | 8. Swing Parabolic SAR | 1h af0.02 ambos | +51% | +184% | -19% | +8% | +276% | +39% | 3910.0 |
| 55 | 30 | rdi | 5. RSI Divergence x Ichimoku x 200EMA | 4h lb5 ambos | -4% | +88% | +78% | +15% | +271% | +39% | 115.0 |
| 56 | 28 | hapa | 10. Heikin Ashi Price Action | 1D velas ambos | +110% | +61% | -30% | +56% | +268% | +38% | 252.0 |
| 57 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 1D m2.7 normal tp0.47 sl0.21 | +25% | +145% | +10% | +10% | +268% | +38% | 60.0 |
| 58 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 1D a3.0 atr30 hma2 ambos | +74% | +106% | -12% | +16% | +266% | +38% | 39.0 |
| 59 | 36 | lrb | 13. Linear Regression Channel Breakout | 1h n50 ambos | -28% | +547% | -24% | +3% | +262% | +38% | 4082.0 |
| 60 | 32 | tfp | 19. Trend Following Parabolic (TradeDots) | 1h rr1.3 ambos | +26% | +359% | -21% | -21% | +261% | +38% | 393.0 |
| 61 | 25 | ht3 | 36. Swing HULL + T3 | 4h 100 semsltp ambos | +85% | +85% | +5% | -1% | +258% | +38% | 255.0 |
| 62 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 4h e200 tp/sl sem ambos | -3% | +130% | +10% | +45% | +257% | +37% | 55.0 |
| 63 | 37 | rcf | 20. RSI-CCI Fusion | 4h n14 ambos | +3% | +159% | -20% | +66% | +254% | +37% | 987.0 |
| 64 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 30min atr10x4.0 | -14% | +199% | -15% | +61% | +253% | +37% | 1792.0 |
| 65 | 32 | srs | 17. Supertrend + RSI (Alorse) | 1D f3 ambos | -6% | +70% | +9% | +100% | +249% | +37% | 46.0 |
| 66 | 33 | pst | 8. Parabolic SAR stop entries | 1h af0.02 ambos | +52% | +86% | +39% | -12% | +244% | +36% | 2202.0 |
| 67 | 9 | micu | 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips) | 1h sl0.005 tp0 trail0 sess0 ambos | -34% | +548% | +6% | -26% | +241% | +36% | 4824.0 |
| 68 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 1h 9 24/52/18 obv0 ls | -38% | +479% | +1% | -6% | +240% | +36% | 585.0 |
| 69 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 30min bb20 1.5 semlatest ambos | +8% | +233% | -23% | +20% | +230% | +35% | 1090.0 |
| 70 | 23 | crazy | 10. Crazy Scalping (TMO + AMA) | 1h sl30 ambos | +13% | +105% | +25% | +12% | +227% | +35% | 296.0 |
| 71 | 32 | qst | 8. QuantNomad SuperTrend | 1D m3 ambos | +12% | +117% | +13% | +17% | +221% | +34% | 51.0 |
| 72 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 4h k3.0 sl3.0 be0.0 tp3.0 ema0 ambos | -6% | +107% | +20% | +35% | +215% | +33% | 337.0 |
| 73 | 5 | qqe |  | 1D b60 x30 s90 sw20 wae1 lucro1 | +35% | +55% | +35% | +9% | +209% | +33% | 59.0 |
| 74 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 1h r14 m10 tend ambos | -1% | +77% | +60% | +9% | +205% | +32% | 1529.0 |
| 75 | 23 | ma1020 | 12. MA 10/20 Crossover | 30min 20/50 ambos | +1% | +238% | +12% | -21% | +202% | +32% | 1983.0 |
| 76 | 37 | hul | 7. Hull Suite | 1D n55 ambos | +6% | +135% | +41% | -15% | +199% | +31% | 77.0 |
| 77 | 10 | mab | 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao) | 30min ma 20/50 ambos | -9% | +150% | +53% | -17% | +188% | +30% | 1714.0 |
| 78 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 1D n55 ambos | +6% | +141% | +36% | -18% | +184% | +30% | 78.0 |
| 79 | 20 | atrgod |  | 4h sl4.5 rr1.5 semfiltros ambos | +24% | +48% | +9% | +43% | +183% | +30% | 101.0 |
| 80 | 25 | flexi | 7. FlexiSuperTrend | 15min f15 ambos | -19% | +545% | -31% | -22% | +181% | +29% | 2449.0 |
| 81 | 34 | gtf | 1. Gradient Trend Filter | 30min l25 ambos | -12% | +131% | +17% | +17% | +179% | +29% | 1244.0 |
| 82 | 24 | stb | 5. SuperTrend Backtester | 1D semtp ambos | -7% | +100% | -10% | +64% | +176% | +29% | 49.0 |
| 83 | 29 | bbf | 16. Bull and Bear Fear | 4h n30 ambos | +60% | +108% | -29% | +18% | +175% | +29% | 482.0 |
| 84 | 9 | hull | 4. Hull Swing Trader (HMA 210 do open) | 4h p400 ambos | -20% | +145% | +26% | +11% | +174% | +29% | 112.0 |
| 85 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 30min f10 one tp5.0 | +10% | +4% | +66% | +43% | +172% | +28% | 1018.0 |
| 86 | 22 | apsar | 7. ATR Parabolic SAR | 15min n3 0.02/0.2 ambos | +33% | +130% | -1% | -11% | +171% | +28% | 3569.0 |
| 87 | 33 | stc | 10. SuperTrend chandelier 7/7 | 1D m3 ambos | -9% | +100% | -10% | +64% | +170% | +28% | 45.0 |
| 88 | 23 | twin | 1. Twin Range Filter | 1D sematr t0 sltp ambos | +54% | +310% | -13% | -51% | +168% | +28% | 128.0 |
| 89 | 26 | sts | 5. SuperTrend STRATEGY | 1h m3 ambos | -18% | +290% | -41% | +41% | +165% | +28% | 1533.0 |
| 90 | 31 | lch | 5. Linear Channel (long-only) | 15min v2% hma400 | -1% | +177% | -5% | +1% | +165% | +28% | 79.0 |
| 91 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 4h rr3.0 semvol 24h ambos | +0% | +179% | -18% | +16% | +165% | +28% | 158.0 |
| 92 | 29 | kamatd | 8. KAMA TradeDots | 30min r5 ambos | -15% | +160% | -2% | +22% | +164% | +28% | 1552.0 |
| 93 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 ambos | +12% | +119% | +11% | -3% | +164% | +28% | 232.0 |
| 94 | 13 | scalp | 2. Scalping Trading System (SMA25/EMA200, Keltner, MACD 4/34, Stoch 10) | 1h s25 e200 ambos | -21% | +193% | +26% | -9% | +164% | +27% | 342.0 |
| 95 | 30 | mmr | 7. Multiple MACD RSI | 30min 10/22 ambos | -23% | +429% | +18% | -45% | +163% | +27% | 2823.0 |
| 96 | 26 | kha | 17. Kozlod Heikin-Ashi | 4h k2 ambos | -23% | +123% | +14% | +35% | +162% | +27% | 1751.0 |
| 97 | 37 | dmm | 6. DMI Modified | 1D n9 ambos | -7% | +105% | -2% | +37% | +158% | +27% | 56.0 |
| 98 | 37 | wmx | 15. WMX Williams Fractals | 4h o3 ambos | +13% | +87% | +13% | +7% | +158% | +27% | 837.0 |
| 99 | 17 | stcci | 1. Supertrend CCI (sinal do CCI28) | 1D cci28 ambos | +4% | +161% | +6% | -10% | +157% | +27% | 176.0 |
| 100 | 22 | psarc | 14. Parabolic SAR on close | 1D n1 0.01/0.1 ambos | -10% | +310% | +13% | -39% | +153% | +26% | 89.0 |
| 101 | 32 | hme | 5. HMA 200 + EMA 20 | 30min hma200 ambos | -32% | +158% | +56% | -7% | +153% | +26% | 1997.0 |
| 102 | 23 | ttm | 18. Trend Trader + MACD | 1D m1.5 semmacd ambos | +46% | +119% | -18% | -3% | +153% | +26% | 273.0 |
| 103 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 1h a3.0 c7 | -17% | +242% | -27% | +19% | +150% | +26% | 1360.0 |
| 104 | 22 | mab | 11. Moving Average Band | 4h 40 rr3 ambos | +12% | +65% | -2% | +37% | +149% | +26% | 575.0 |
| 105 | 34 | zlm | 6. Zero-Lag MA Trend Following | 1D rr2 ambos | -9% | +28% | +90% | +12% | +148% | +25% | 34.0 |
| 106 | 18 | slope | 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200) | 30min 130 9/21 semfiltro ambos | -38% | +494% | +18% | -44% | +144% | +25% | 3955.0 |
| 107 | 30 | lin | 13. 2x Universelle Linien | 4h 50/200 ambos | -19% | +132% | +19% | +8% | +143% | +25% | 57.0 |
| 108 | 30 | lsr | 18. LunaOwl suporte/resistencia | 4h lb50 ambos | +57% | +131% | +23% | -46% | +142% | +25% | 78.0 |
| 109 | 20 | t3sar |  | 1D semstop ambos | -31% | +17% | +59% | +88% | +142% | +25% | 21.0 |
| 110 | 25 | ao | 49. Awesome Oscillator | 4h ambos | -44% | +159% | +11% | +48% | +141% | +25% | 2006.0 |
| 111 | 31 | okx | 15. OKX MA Crossover | 1h 7% ambos | +42% | +217% | -30% | -23% | +140% | +25% | 3145.0 |
| 112 | 16 | aivst | 3. AI Volume SuperTrend (10, 3; rotulo WMA20 vs WMA100 do ST) | 30min l20 f3 ambos | -24% | +289% | -25% | +7% | +139% | +24% | 1457.0 |
| 113 | 21 | rbin | 17. RSI Binary (6, 13/82, 3 barras) | 1D 14 30/70 h10 ambos | +9% | +15% | +22% | +57% | +139% | +24% | 45.0 |
| 114 | 23 | bbst | 2. BBTrend + SuperTrend | 30min f7 ambos | -20% | +52% | +10% | +76% | +135% | +24% | 3747.0 |
| 115 | 32 | usc | 3. Ultimate Scalping v2 (EMA + VWAP) | 4h tp3atr ambos | -36% | +139% | +16% | +32% | +134% | +24% | 469.0 |
| 116 | 22 | tst | 18. Triple SuperTrend + StochRSI | 30min 28/78 rr3.0/3.0 ambos | +102% | -5% | +38% | -13% | +131% | +23% | 397.0 |
| 117 | 29 | mrs | 17. MACD_RSI | 1D e20 ambos | +15% | +122% | +3% | -13% | +129% | +23% | 88.0 |
| 118 | 30 | sich | 11. SuperIchi | 1D rr2 ambos | -6% | +106% | +6% | +10% | +128% | +23% | 16.0 |
| 119 | 32 | fis | 15. Fisher Transform (Ehlers) | 1h l20 ambos | -7% | +174% | +11% | -20% | +127% | +23% | 2130.0 |
| 120 | 24 | d3 | 13. DEMA 8/20/63 | 30min x1 ambos | -40% | +356% | +39% | -41% | +125% | +22% | 3077.0 |
| 121 | 25 | thma | 9. Triangular Hull MA | 1h 40 ambos | -34% | +140% | +26% | +13% | +125% | +22% | 1660.0 |
| 122 | 25 | rtb | 47. Reversal Trading Bot | 1h sl1% tp2% ambos | -4% | +56% | +93% | -22% | +124% | +22% | 1662.0 |
| 123 | 30 | hul | 1. Hull MA and Candle cross | 30min z100 ambos | -23% | +258% | +13% | -28% | +123% | +22% | 5555.0 |
| 124 | 33 | dst | 17. Dual Supertrend with MACD | 1h 3/5 ambos | -1% | +167% | -12% | -4% | +123% | +22% | 1767.0 |
| 125 | 32 | koz | 20. Kozlod MA Cross | 1h 10/30 ambos | -37% | +231% | +22% | -12% | +123% | +22% | 1677.0 |
| 126 | 26 | him | 7. Hull + Ichimoku + MACD | 4h h12 ambos | -1% | +240% | -33% | -2% | +122% | +22% | 770.0 |
| 127 | 34 | ppt | 3. Pivot Percentile Trend | 4h l20 ambos | -3% | +107% | +5% | +5% | +121% | +22% | 66.0 |
| 128 | 30 | scl | 17. 1 min forex scalping | 30min x1 ambos | -2% | +58% | +26% | +14% | +121% | +22% | 1712.0 |
| 129 | 33 | vxe | 18. VWAP X EMA | 1h ema50 ambos | +41% | +108% | -30% | +7% | +121% | +22% | 1983.0 |
| 130 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR40 p0.5 c0.005 | +100% | +111% | +7% | -51% | +119% | +22% | 85.0 |
| 131 | 20 | cam |  | 4h sl2.0% tp6% ambos | +24% | -9% | +46% | +33% | +119% | +22% | 676.0 |
| 132 | 34 | mtl | 2. Market Trend Levels | 4h 20/50 adx20 ambos | +6% | +32% | +51% | +4% | +119% | +22% | 94.0 |
| 133 | 24 | hst | 6. HMA50 + Supertrend | 1D h50 ambos | -6% | +97% | +8% | +9% | +118% | +22% | 71.0 |
| 134 | 36 | kel | 12. Keltner SL/TP | 1D k1/sl20 ambos | +21% | +1% | +5% | +70% | +118% | +21% | 71.0 |
| 135 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 4h sl2.00% 24h ambos | +1% | +13% | +6% | +79% | +117% | +21% | 1150.0 |
| 136 | 4 | ppst | 2. Pivot Point SuperTrend (2, 3, 10) | 1D p2 f2.0 a20 | -23% | +94% | +2% | +41% | +116% | +21% | 43.0 |
| 137 | 36 | cbo | 19. Candle Breakout 13h UTC | 1h h13/rr2 ambos | +41% | +136% | -39% | +6% | +116% | +21% | 1006.0 |
| 138 | 21 | kb | 15. Keltner bounce (SMA200 +- 8 ATR) | 15min 200 d8 saimedia ambos | -9% | +19% | +68% | +18% | +115% | +21% | 594.0 |
| 139 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 4h a20 m2 ambos | -11% | +155% | -23% | +22% | +114% | +21% | 621.0 |
| 140 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 4h trig1 sl0.02 ambos | +32% | +127% | -27% | -2% | +114% | +21% | 1929.0 |
| 141 | 21 | sqz | 2. Squeeze Momentum | 4h l1 sl0.0% tp0% semsqz ambos | -7% | +81% | +19% | +7% | +113% | +21% | 1422.0 |
| 142 | 28 | pmax | 8. PMax | 1D m1.5 ambos | -22% | +72% | +2% | +56% | +113% | +21% | 44.0 |
| 143 | 26 | ksr | 9. KSR (EMA 10/20) | 1D 10/20 ambos | -28% | +116% | +16% | +17% | +112% | +21% | 76.0 |
| 144 | 16 | emax | 4. EMA Cross 10/20 | 1D 10/20 ambos | -28% | +116% | +16% | +17% | +112% | +21% | 76.0 |
| 145 | 14 | hap | 2. Heikin-Ashi PSAR [QuantNomad] | 30min 0.005/0.005/0.05 ambos | -24% | +358% | -38% | -2% | +111% | +20% | 2240.0 |
| 146 | 31 | mst | 6. MACD + Stochastic | 4h st14 ambos | -33% | -33% | +141% | +92% | +110% | +20% | 281.0 |
| 147 | 18 | osb | 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario) | 30min m0.25 sl2.00% ambos | -23% | +150% | -40% | +82% | +109% | +20% | 649.0 |
| 148 | 32 | tss | 18. TSI w SuperTrend decision | 1D p32 ambos | -29% | +162% | +25% | -11% | +107% | +20% | 57.0 |
| 149 | 18 | savwap | 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only) | 4h prd100 ambos | -7% | +114% | -5% | +8% | +105% | +20% | 66.0 |
| 150 | 25 | dbt | 44. Double Bottom/Top Hunter | 30min 30 ambos | +17% | -22% | +90% | +18% | +105% | +20% | 283.0 |
| 151 | 26 | rsx | 12. RSI Crossover | 1D r50/25 ambos | +7% | +16% | +84% | -10% | +104% | +20% | 186.0 |
| 152 | 25 | mst | 11. Master Supertrend | 1h 20 m2 ambos | -22% | +437% | -75% | +89% | +104% | +19% | 1693.0 |
| 153 | 23 | evw | 19. EVWMA x VWAP | 4h 100 ambos | +11% | +119% | +3% | -19% | +102% | +19% | 238.0 |
| 154 | 31 | gx | 11. Golden X BF | 4h 50/200 ambos | -19% | +102% | +25% | -1% | +102% | +19% | 57.0 |
| 155 | 34 | kmt | 5. Ichimoku Kumo Twist | 15min stop ambos | +5% | +204% | -14% | -27% | +101% | +19% | 3538.0 |
| 156 | 36 | pin | 6. Pinbar | 4h pm2 ambos | -12% | +454% | -59% | +1% | +101% | +19% | 406.0 |
| 157 | 30 | tsh | 2. TrendShift Supertrend + ADX | 30min m3 ambos | -18% | +288% | -43% | +9% | +99% | +19% | 1163.0 |
| 158 | 29 | hlc | 2. High/Low channel swing | 4h l12 ambos | -45% | +185% | +13% | +12% | +99% | +19% | 1233.0 |
| 159 | 24 | alpha | 20. AlphaTrend | 30min mfi ambos | -8% | +202% | -40% | +20% | +98% | +19% | 2283.0 |
| 160 | 31 | lst | 13. LunaOwl SuperTrend 2 | 1D m2.618 ambos | -6% | +119% | -1% | -3% | +98% | +19% | 56.0 |
| 161 | 21 | bbb | 11. Bollinger Bands Breakout | 4h bb15 semvol sl0% tp0% ambos | +101% | +63% | -31% | -13% | +98% | +19% | 219.0 |
| 162 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 30min lb20 pb2 tp2.0 sl2.0 | +31% | -33% | +119% | +3% | +97% | +18% | 1593.0 |
| 163 | 23 | mabb | 9. MA BB + RSI | 15min a9 vol ambos | +28% | +23% | +2% | +22% | +95% | +18% | 357.0 |
| 164 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 30min r20 m20 ambos | -15% | +104% | +40% | -20% | +95% | +18% | 1804.0 |
| 165 | 29 | adxb | 15. Rob Booker ADX Breakout | 1h adx25 ambos | -5% | +59% | +30% | -2% | +93% | +18% | 1100.0 |
| 166 | 25 | sec | 30. Stoch/EMA Cross | 15min tp8 ambos | -2% | +57% | -5% | +32% | +93% | +18% | 1974.0 |
| 167 | 32 | prv | 4. SuperTrend Enhanced Pivot Reversal | 15min f4 ambos | -4% | +157% | -26% | +7% | +93% | +18% | 2111.0 |
| 168 | 20 | madrid |  | 1D tp3% sl3% ambos | -8% | +18% | +27% | +40% | +93% | +18% | 260.0 |
| 169 | 20 | ceyhun |  | 1D m2 3 ambos | -11% | +28% | -1% | +70% | +92% | +18% | 48.0 |
| 170 | 22 | bbra | 1. BB + RSI + ADX | 4h sl0.0% adx32 ambos | -26% | +152% | +20% | -15% | +90% | +17% | 69.0 |
| 171 | 21 | joel | 12. 5min MACD scalp (Joel) | 15min tp3.0% sl2.0% ambos | -23% | +165% | +5% | -12% | +90% | +17% | 1378.0 |
| 172 | 25 | drm | 13. Dynamic RSI Momentum | 30min 20/80 ambos | -64% | +248% | +52% | -1% | +88% | +17% | 35.0 |
| 173 | 24 | ectp | 19. EMA Crossover with TP | 30min sl3% semtp ambos | +8% | +188% | -22% | -23% | +87% | +17% | 1683.0 |
| 174 | 6 | hs | 1. Hammers & Stars (stop 1 ATR, alvo 1R) | 4h s2.0 rr2.0 fib0.333 ema0 | -18% | +419% | -30% | -38% | +85% | +17% | 253.0 |
| 175 | 13 | sqz | 4. Squeeze Momentum [LazyBear] (BB14x2, KC16x1,5) | 4h bb14 kc16 ambos | -4% | +151% | -18% | -7% | +84% | +17% | 512.0 |
| 176 | 11 | sce | 2. Strategy Code Example (EMA14x21 do open, stop 0,1% alvo 0,5%) | 1h 14/21 sl0.0 tp0 ambos | -16% | +67% | +34% | -3% | +84% | +17% | 1523.0 |
| 177 | 27 | wvs | 8. Volatility System (Wilder) | 1h arc3 ambos | -18% | +98% | +37% | -18% | +84% | +16% | 1044.0 |
| 178 | 22 | emax | 2. EMA Crossover hl2 | 1h 50x3 ambos | +30% | +134% | -32% | -12% | +82% | +16% | 271.0 |
| 179 | 25 | grov | 28. Grover Llorens Activator | 4h 480 m14 ambos | +58% | +110% | -38% | -12% | +82% | +16% | 109.0 |
| 180 | 27 | atf | 2. Adaptive Trend Flow | 1D filtros ambos | +31% | +361% | -70% | +2% | +82% | +16% | 251.0 |
| 181 | 32 | stdbf | 2. Super Trend Daily BF | 1D m2.6 ambos | +13% | +19% | +34% | +1% | +82% | +16% | 39.0 |
| 182 | 28 | rci | 16. RCI | 1h rci30 ambos | -10% | +156% | -35% | +20% | +79% | +16% | 2446.0 |
| 183 | 20 | mrb |  | 1h 80 g2 m2 central ambos | -0% | +176% | -28% | -10% | +79% | +16% | 1737.0 |
| 184 | 31 | pse | 17. Parabolic SAR w/ EMA | 30min off0% ambos | -13% | +152% | -25% | +10% | +79% | +16% | 2453.0 |
| 185 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 1D len20 m1.0 ambos | +3% | +116% | -2% | -18% | +79% | +16% | 78.0 |
| 186 | 24 | dcf | 9. Donchian free bot | 1h semtp ambos | +40% | +9% | -4% | +21% | +78% | +16% | 3678.0 |
| 187 | 28 | sflip | 5. Bitcoin SuperFlip | 4h f1.8 ambos | -7% | +114% | -6% | -5% | +77% | +15% | 337.0 |
| 188 | 30 | ptr | 6. Percent Trailing Stop | 1D t5% ambos | +16% | +83% | +13% | -26% | +77% | +15% | 98.0 |
| 189 | 33 | tbn | 7. Trend Bounce | 4h c7 ambos | +25% | +32% | +15% | -7% | +76% | +15% | 406.0 |
| 190 | 32 | irs | 6. Ichimoku Cloud with RSI (Coinrule) | 15min rsi50 ambos | +2% | +185% | +20% | -49% | +76% | +15% | 1586.0 |
| 191 | 11 | easy | 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT) | 1h e10 st3.0 zig1 ambos | +1% | +155% | -35% | +5% | +76% | +15% | 1466.0 |
| 192 | 28 | hvc | 14. Hull MA vs Candle | 1h h50 ambos | +16% | +96% | -22% | -1% | +76% | +15% | 1441.0 |
| 193 | 20 | 3st |  | 1D pl3.0 thr20 ambos | -11% | +13% | +81% | -3% | +75% | +15% | 16.0 |
| 194 | 20 | fline |  | 30min 21 1.0 ambos | -36% | +182% | -53% | +107% | +75% | +15% | 1962.0 |
| 195 | 36 | mbd | 20. MACD Short/Long TVIO | 1h sl21 ambos | -14% | +117% | +3% | -10% | +75% | +15% | 1609.0 |
| 196 | 11 | grab | 4. Grab Trading System (80/21) | 4h 80/21 stop1 | -1% | +34% | +52% | -14% | +73% | +15% | 213.0 |
| 197 | 33 | szs | 19. Stochastic Z-Score (TradeDots) | 1D z2.8 ambos | -17% | +1% | +22% | +70% | +73% | +15% | 10.0 |
| 198 | 27 | flash | 7. The Flash | 1D mr60 ambos | -36% | +118% | -3% | +27% | +73% | +15% | 41.0 |
| 199 | 36 | ral | 8. RSI Alligator | 1D sl3 ambos | +42% | +17% | +12% | -8% | +72% | +15% | 227.0 |
| 200 | 27 | doji | 1. Doji strategy | 4h sl3% ambos | -32% | +228% | -36% | +22% | +72% | +15% | 327.0 |
| 201 | 27 | atrts | 15. ATR Trailing Stops | 30min a5x3.5 ambos | -34% | +429% | -59% | +20% | +72% | +14% | 2290.0 |
| 202 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 30min a5 m3.5 ambos | -34% | +429% | -59% | +20% | +72% | +14% | 2291.0 |
| 203 | 22 | hhll | 13. Highest High / Lowest Low | 1D 20 ambos | -42% | +94% | +3% | +47% | +71% | +14% | 42.0 |
| 204 | 25 | kpl | 40. KPL Swing | 1D 20 ambos | -42% | +94% | +3% | +47% | +71% | +14% | 42.0 |
| 205 | 38 | smx | 4. SMAcross-mvr | 4h 50/200 ambos | -23% | +107% | +15% | -8% | +70% | +14% | 57.0 |
| 206 | 10 | pdiv | 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2) | 30min q2 m50 reg+hid sl0.01 ambos | -19% | +169% | -18% | -4% | +70% | +14% | 1314.0 |
| 207 | 23 | tema | 11. Triple EMA Trend | 1D adx43 ambos | +22% | +81% | -25% | +0% | +67% | +14% | 13.0 |
| 208 | 26 | hama | 11. NSDT HAMA (EMA55) | 4h e55 ambos | +0% | +62% | -21% | +29% | +66% | +14% | 465.0 |
| 209 | 21 | hulk | 5. Hulk Scalper | 30min thr0.1 adx33 tp3.00% sl2.0% ambos | +2% | +26% | +14% | +13% | +66% | +13% | 218.0 |
| 210 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 1h 29 norm ambos | -35% | +9% | +53% | +53% | +65% | +13% | 336.0 |
| 211 | 28 | gch | 18. Gaussian Channel | 4h p144 ambos | +22% | +84% | -33% | +10% | +65% | +13% | 486.0 |
| 212 | 29 | cez | 4. Chandelier Exit + ZLSMA | 15min m2 ambos | +20% | +1% | +27% | +7% | +65% | +13% | 1577.0 |
| 213 | 28 | sma3 | 19. Tres medias (SMA 7/25/99) | 1D 7/25 ambos | +4% | +102% | +12% | -30% | +63% | +13% | 81.0 |
| 214 | 31 | seq | 7. Sequence Snap | 1D rr1 ambos | +10% | +30% | -5% | +22% | +63% | +13% | 18.0 |
| 215 | 10 | aio | 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR) | 1h rsi0 atr2.0 rr3.0 ambos | -12% | +123% | -10% | -7% | +63% | +13% | 982.0 |
| 216 | 15 | comb | 2. Combined Strategy (fita de EMAs + RSI + Stoch) | 30min so EMAs ambos | -10% | +87% | +3% | -6% | +62% | +13% | 1462.0 |
| 217 | 32 | hfl | 1. Hurst Future Lines of Demarcation | 1h c20 ambos | -20% | +118% | -0% | -7% | +61% | +13% | 1284.0 |
| 218 | 20 | ypmax |  | 1D 13 3 ambos | -21% | +40% | -9% | +60% | +61% | +13% | 45.0 |
| 219 | 21 | renko | 14. Renko Open_Close (Pro) | 1D m2 ambos | -19% | +62% | +8% | +12% | +60% | +13% | 354.0 |
| 220 | 13 | ichi | 5. Ichimoku basico (9/26/52, deslocamento 26) | 15min 9/26/52 ambos | +4% | +243% | -47% | -16% | +60% | +13% | 3149.0 |
| 221 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 4h sl0.02 rr0.0 eod0 filt1 ambos | +33% | +42% | -25% | +13% | +60% | +12% | 76.0 |
| 222 | 30 | gso | 8. Gann Swing Oscillator | 1h l10 ambos | -57% | +159% | -21% | +83% | +59% | +12% | 883.0 |
| 223 | 25 | ce | 1. Chandelier Exit | 1h semrisco ambos | -14% | +125% | -30% | +17% | +58% | +12% | 1716.0 |
| 224 | 26 | dm | 18. DEMA + MACD | 4h d21 ambos | -22% | +130% | +19% | -26% | +58% | +12% | 2050.0 |
| 225 | 12 | tk | 1. TK Cross > EMA200 (20/60, long-only) | 1D 9/26 ema0 ambos | -22% | +98% | +45% | -30% | +57% | +12% | 69.0 |
| 226 | 33 | snr | 12. Signal To Noise | 1D l21 ambos | -39% | +81% | +36% | +3% | +57% | +12% | 64.0 |
| 227 | 37 | rsc | 16. RSI Classic (Coinrule) | 1h 20/60 | -1% | +32% | -5% | +24% | +55% | +12% | 92.0 |
| 228 | 26 | e5 | 1. 5 EMA | 4h rr1.5 ambos | -6% | +86% | +16% | -23% | +55% | +12% | 1094.0 |
| 229 | 29 | r2m | 9. RSI2 + medias (pullback) | 4h 5/95 ambos | -13% | +44% | +13% | +9% | +55% | +11% | 254.0 |
| 230 | 23 | e3r | 3. 3 EMA + RSI | 4h sl5% x24 ambos | -14% | +35% | +49% | -11% | +54% | +11% | 135.0 |
| 231 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 15min bb20 2.0 sl2.0% tp2.0% ambos | -9% | +96% | -7% | -8% | +54% | +11% | 2081.0 |
| 232 | 25 | opw | 37. TASC One Percent A Week (long-only) | 4h dip2 tp2 | -11% | +5% | +44% | +13% | +53% | +11% | 259.0 |
| 233 | 27 | c2ac | 19. Combo 2/20 EMA + AC | 4h e14 ambos | +8% | +14% | +2% | +21% | +52% | +11% | 1838.0 |
| 234 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 1h l200 m1.5 sl0.03 ambos | -3% | +0% | +35% | +16% | +52% | +11% | 444.0 |
| 235 | 36 | rs2 | 10. RSI 2 + tendencia, trailing | 30min ts3 ambos | +8% | +157% | -52% | +14% | +51% | +11% | 1002.0 |
| 236 | 28 | ccu | 4. Crypto Crew University (MFI/RSI/StochRSI) | 1D th30 ambos | +23% | -13% | +58% | -11% | +50% | +11% | 28.0 |
| 237 | 28 | hamacd | 17. Heikin Ashi MACD | 1D tp10 sl3 ambos | +38% | +55% | +8% | -35% | +50% | +11% | 126.0 |
| 238 | 26 | vst | 2. Vegas SuperTrend Enhanced | 1D b2 ambos | -12% | +79% | +20% | -20% | +50% | +11% | 107.0 |
| 239 | 25 | made | 4. MA Displaced Envelope + ATRTS | 1D 9 ambos | -1% | +140% | -10% | -30% | +50% | +11% | 104.0 |
| 240 | 7 | srt | 5. SR TREND (21) | 1h len100 | -4% | +123% | -13% | -19% | +50% | +11% | 1016.0 |
| 241 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 15min r0.5 rr3.0 ret00 | +20% | +11% | +21% | -7% | +49% | +11% | 1545.0 |
| 242 | 24 | best | 2. BEST Supertrend | 1D m3 ambos | -10% | +47% | +13% | -0% | +49% | +10% | 74.0 |
| 243 | 23 | rsipa | 17. RSI PrimeAutomation | 15min s2 tp4 ambos | -19% | +77% | +2% | +2% | +49% | +10% | 2128.0 |
| 244 | 23 | stv | 16. Super trend V | 1D m3 ambos | -14% | +19% | -8% | +55% | +46% | +10% | 45.0 |
| 245 | 20 | xscalp |  | 30min gap1.00% rr3 ambos | +11% | +87% | -6% | -26% | +45% | +10% | 2189.0 |
| 246 | 20 | dai |  | 30min 4/3 ambos | -17% | +172% | -36% | +1% | +45% | +10% | 1237.0 |
| 247 | 22 | xsc | 15. XAUUSD Scalping V2 | 4h tp3 sl1.5 ambos | -30% | +62% | +16% | +10% | +44% | +10% | 774.0 |
| 248 | 37 | hle | 11. HL MovingAvg2Line Cross | 1D n9 ambos | +15% | +51% | -27% | +14% | +44% | +10% | 152.0 |
| 249 | 17 | ftsma | 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier) | 30min 5/20/200 semft ambos | +15% | +226% | -41% | -34% | +43% | +9% | 1718.0 |
| 250 | 28 | mab | 13. Moving Average (BiznesFilosof) | 1h sma50 ambos | -11% | +116% | -28% | +3% | +43% | +9% | 2965.0 |
| 251 | 29 | madx | 13. Crossing MAs + ADX | 1h adx20 ambos | +70% | +35% | -34% | -6% | +42% | +9% | 464.0 |
| 252 | 36 | dch | 11. Donchian stop entries | 30min n20 ambos | +5% | +49% | -24% | +18% | +42% | +9% | 3386.0 |
| 253 | 23 | qqe | 7. UL QQE Cross | 1h thr10 filtro ambos | -23% | +233% | -43% | -3% | +41% | +9% | 2307.0 |
| 254 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 1h p5 rr5.0 trend1 ambos | +17% | +31% | -6% | -3% | +41% | +9% | 219.0 |
| 255 | 26 | bx | 6. B-Xtrender | 1h trl20% ambos | -15% | +121% | -21% | -6% | +40% | +9% | 1909.0 |
| 256 | 31 | ten | 12. Tendency EMA + RSI | 1h x24 ambos | +38% | +21% | +7% | -22% | +40% | +9% | 454.0 |
| 257 | 27 | ichb | 17. Ichimoku Backtester | 4h 9/26/52 ambos | +68% | -23% | +34% | -20% | +39% | +9% | 60.0 |
| 258 | 23 | hl41 | 4. Higher High Lower Low | 4h 100 ambos | +4% | +24% | +35% | -20% | +39% | +9% | 39.0 |
| 259 | 33 | hcx | 15. Hull MA Crossover | 1h h28 ambos | -35% | +256% | -25% | -20% | +38% | +8% | 2733.0 |
| 260 | 25 | pop | 22. Pivot of Pivot Reversal | 4h 4/2 ambos | +43% | +18% | +9% | -25% | +36% | +8% | 121.0 |
| 261 | 25 | rbd | 19. RSI Bull Div (long-only) | 4h tp3 sl1.75 | -11% | +41% | +6% | +2% | +35% | +8% | 31.0 |
| 262 | 31 | fxf | 14. FXFUNDINGMATE Trend | 4h tp1atr ambos | +12% | +36% | -8% | -4% | +35% | +8% | 250.0 |
| 263 | 25 | imct | 16. Ichimoku + MACD/CMF/TSI | 15min ambos | -25% | +350% | -57% | -7% | +34% | +8% | 2472.0 |
| 264 | 25 | ffe | 15. Forex Fractal EMA Scalper | 1D tp2.0% direto ambos | -19% | +12% | +51% | -2% | +34% | +8% | 209.0 |
| 265 | 24 | tq | 4. Triple EMA + QQE | 4h p1% ambos | -1% | +3% | +18% | +11% | +34% | +8% | 184.0 |
| 266 | 29 | wtr | 18. BTC WaveTrend R:R (long-only) | 1h rr1.5 lim-40 | -28% | +119% | +7% | -21% | +34% | +8% | 759.0 |
| 267 | 36 | vst | 3. Multi-Step Vegas SuperTrend | 1D b2 ambos | -6% | +46% | -22% | +23% | +33% | +7% | 50.0 |
| 268 | 30 | mbf | 16. Momentum BF | 1D l18 ambos | -23% | +58% | +22% | -11% | +33% | +7% | 176.0 |
| 269 | 25 | gn | 41. Gianno Nano | 4h semsltp ambos | +15% | +15% | +12% | -12% | +31% | +7% | 272.0 |
| 270 | 25 | bts | 27. BEST Trailing Stop | 1h tr8% ambos | -11% | +150% | -27% | -20% | +31% | +7% | 1163.0 |
| 271 | 24 | vws | 16. VWMA/SMA 3Commas | 1D niveis ambos | -5% | +62% | -6% | -10% | +31% | +7% | 215.0 |
| 272 | 35 | lpr | 1. Linear Regression Pearson | 30min k360 sempre ambos | +21% | +54% | -28% | -4% | +30% | +7% | 1055.0 |
| 273 | 29 | bbe9 | 6. Bollinger Bands + EMA 9 | 1h bb50 ambos | -7% | +18% | +32% | -11% | +30% | +7% | 2088.0 |
| 274 | 37 | lag | 1. Laguerre RSI | 1h a0.2 ambos | -19% | +75% | +4% | -12% | +29% | +7% | 1350.0 |
| 275 | 6 | bbrsi | 3. Bollinger Band with RSI (piramide 50 x 10% do capital) | 1h 20/60 bb2.5 u1 | -2% | +29% | -13% | +17% | +29% | +7% | 66.0 |
| 276 | 19 | cipher | 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11) | 30min semwt tp2 sl1 ambos | +3% | +12% | -3% | +14% | +29% | +6% | 782.0 |
| 277 | 29 | chb | 20. Channel Break (free bot) | 1D canal ambos | +5% | +80% | -5% | -29% | +29% | +6% | 78.0 |
| 278 | 30 | mma | 3. Multi-MA | 4h l150 ambos | -25% | +102% | -11% | -5% | +28% | +6% | 92.0 |
| 279 | zigzagpa | grade |  | 1h ew0.0 tp1.618 sl-1.0 | -8% | +23% | +5% | +8% | +28% | +6% | 69.0 |
| 280 | 25 | bas | 45. BEST ATR Stop Multiple | 1h atr2 ambos | -16% | +64% | -19% | +14% | +27% | +6% | 1163.0 |
| 281 | 27 | ssl | 18. SSL Channel Cross | 4h l10 ambos | -36% | +202% | -24% | -13% | +27% | +6% | 1017.0 |
| 282 | 31 | alm | 1. ALMA/EMA | 4h tp6% ambos | -13% | +31% | +14% | -2% | +27% | +6% | 70.0 |
| 283 | 25 | hyb | 17. Hybrid RSI + Breakout | 30min atr2 ambos | -9% | +53% | +9% | -19% | +24% | +5% | 2706.0 |
| 284 | 27 | wyk | 13. Wyckoff Range | 1D sl3% ambos | +20% | +43% | -26% | -3% | +23% | +5% | 24.0 |
| 285 | 25 | htf | 5. Hull MA TimeFrame CrossOver | 30min 1000 s3 ambos | -39% | +40% | -7% | +55% | +23% | +5% | 52.0 |
| 286 | 36 | vrb | 14. Volatility Range Breakout | 15min n50 ambos | -18% | +100% | -24% | -2% | +23% | +5% | 1463.0 |
| 287 | 36 | sre | 1. Stoch RSI Crossover + EMA | 1h tp3/sl2 ambos | +5% | +42% | -0% | -18% | +23% | +5% | 108.0 |
| 288 | 37 | rvc | 13. Reversal Catcher | 4h bb1.5 ambos | +0% | +27% | -14% | +8% | +19% | +5% | 52.0 |
| 289 | 30 | kal | 12. KALKI TFXBOT | 1h rr1.5 ambos | +4% | -5% | +32% | -9% | +19% | +4% | 706.0 |
| 290 | 12 | pt | 2. Powertrend (range filter de volume, 200, long-only) | 1h l400 m3.0 vol | +1% | +19% | -1% | +0% | +18% | +4% | 13.0 |
| 291 | 37 | mrs | 5. Mean-Reversion Swing | 30min n20 long | -7% | +14% | -4% | +16% | +18% | +4% | 398.0 |
| 292 | 29 | bsc | 5. Breakout Scalper | 1D 13/52 ambos | +10% | +27% | -1% | -16% | +17% | +4% | 31.0 |
| 293 | 33 | r3 | 11. 3 RSI | 1h 40/60 ambos | -46% | -45% | +132% | +70% | +17% | +4% | 396.0 |
| 294 | 28 | t3cci | 7. FX Sniper T3-CCI | 1D cci14 ambos | +1% | +92% | -34% | -8% | +17% | +4% | 156.0 |
| 295 | 25 | fbo | 43. Fractal Breakout | 1D ambos | -18% | +30% | +25% | -12% | +17% | +4% | 74.0 |
| 296 | 27 | simp | 10. Simple strat (MACD + Stoch + RSI) | 1h tp6 sl2 ambos | -28% | +206% | -45% | -3% | +17% | +4% | 2970.0 |
| 297 | 22 | turtle | 6. Real Turtle (stops) | 1h 20/10 n4 ambos | -23% | +110% | -32% | +6% | +16% | +4% | 2303.0 |
| 298 | 27 | gsc | 6. Gold Scalping | 4h tp2atr ambos | -2% | +64% | -25% | -4% | +16% | +4% | 232.0 |
| 299 | 19 | 3ema | 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only) | 4h tp3 sl0 | -8% | +21% | -1% | +4% | +15% | +4% | 96.0 |
| 300 | 32 | dkw | 14. Donchian Channels (KrisWaters) | 1h atr ambos | -18% | +60% | -18% | +8% | +15% | +4% | 2448.0 |
| 301 | vixfix | grade |  | 15min ph0.95 str5 ob70 aggr u1 | -3% | +11% | +13% | -6% | +15% | +4% | 166.0 |
| 302 | 24 | gap | 10. Gap Filling | 1h semalvo ambos | +15% | +18% | -27% | +16% | +14% | +3% | 757.0 |
| 303 | 32 | r2 | 7. AK RSI 2 | 30min 5/90 long | -2% | +18% | +16% | -15% | +14% | +3% | 1526.0 |
| 304 | 22 | slopes | 10. Slopes | 4h 50/200 filtro ambos | -2% | +52% | -37% | +21% | +14% | +3% | 407.0 |
