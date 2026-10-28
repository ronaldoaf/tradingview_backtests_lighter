# WTI: treino / validação / OOS

Período todo (2017-01-03 a 2026-09-30) em 10 partes iguais: 1–6 treino (até 2022-11-07), 7–9 validação (até 2025-10-10), 10 OOS (não lido). Abril de 2020 descartado. B&H na validação: −36,7%.

Exclusão (só treino): média geométrica das 6 partes > 0, pelo menos 4 de 6 partes positivas, retorno sem a melhor parte > 0, trades ≥ 100. Melhor célula de cada estratégia pela média geométrica; templates fora. Aprovadas: 143 estratégias.

Carteiras: gulosa na ordem da média geométrica, correlação diária do treino abaixo do teto; pesos fixos (inverso da vol medida no treino).

| K | Teto | Peso | Corr média | Treino | Sharpe treino | Validação | Sharpe val | DD val | Estratégias |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 0.2 | igual | 0.03 | +1070.3% | 2.63 | +21.0% | 0.61 | -13.5% | piv sta l2r twin gs abcd |
| 6 | 0.2 | inv_vol | 0.03 | +959.5% | 2.59 | +22.7% | 0.66 | -12.8% | piv sta l2r twin gs abcd |
| 6 | 0.3 | igual | 0.12 | +1237.9% | 2.30 | -11.0% | -0.24 | -26.7% | piv sta drsi pst l2r twin |
| 6 | 0.3 | inv_vol | 0.12 | +1156.9% | 2.28 | -11.4% | -0.26 | -26.3% | piv sta drsi pst l2r twin |
| 6 | 0.4 | igual | 0.12 | +1237.9% | 2.30 | -11.0% | -0.24 | -26.7% | piv sta drsi pst l2r twin |
| 6 | 0.4 | inv_vol | 0.12 | +1156.9% | 2.28 | -11.4% | -0.26 | -26.3% | piv sta drsi pst l2r twin |
| 6 | 0.5 | igual | 0.12 | +1237.9% | 2.30 | -11.0% | -0.24 | -26.7% | piv sta drsi pst l2r twin |
| 6 | 0.5 | inv_vol | 0.12 | +1156.9% | 2.28 | -11.4% | -0.26 | -26.3% | piv sta drsi pst l2r twin |
| 8 | 0.2 | igual | 0.03 | +864.0% | 2.77 | +18.1% | 0.57 | -16.1% | piv sta l2r twin gs abcd srvi wr |
| 8 | 0.2 | inv_vol | 0.03 | +770.4% | 2.74 | +20.6% | 0.64 | -15.7% | piv sta l2r twin gs abcd srvi wr |
| 8 | 0.3 | igual | 0.10 | +972.7% | 2.50 | +12.1% | 0.40 | -16.8% | piv sta drsi pst l2r twin sttsl abcd |
| 8 | 0.3 | inv_vol | 0.10 | +857.7% | 2.50 | +20.4% | 0.62 | -13.3% | piv sta drsi pst l2r twin sttsl abcd |
| 8 | 0.4 | igual | 0.10 | +972.7% | 2.50 | +12.1% | 0.40 | -16.8% | piv sta drsi pst l2r twin sttsl abcd |
| 8 | 0.4 | inv_vol | 0.10 | +857.7% | 2.50 | +20.4% | 0.62 | -13.3% | piv sta drsi pst l2r twin sttsl abcd |
| 8 | 0.5 | igual | 0.10 | +972.7% | 2.50 | +12.1% | 0.40 | -16.8% | piv sta drsi pst l2r twin sttsl abcd |
| 8 | 0.5 | inv_vol | 0.10 | +857.7% | 2.50 | +20.4% | 0.62 | -13.3% | piv sta drsi pst l2r twin sttsl abcd |
| 10 | 0.2 | igual | 0.02 | +761.3% | 2.99 | +6.8% | 0.27 | -15.4% | piv sta l2r twin gs abcd srvi wr azl rtb |
| 10 | 0.2 | inv_vol | 0.02 | +692.3% | 2.96 | +8.5% | 0.33 | -15.3% | piv sta l2r twin gs abcd srvi wr azl rtb |
| 10 | 0.3 | igual | 0.08 | +834.3% | 2.61 | +11.6% | 0.40 | -18.5% | piv sta drsi pst l2r twin sttsl abcd srvi wr |
| 10 | 0.3 | inv_vol | 0.08 | +741.1% | 2.62 | +19.3% | 0.61 | -15.5% | piv sta drsi pst l2r twin sttsl abcd srvi wr |
| 10 | 0.4 | igual | 0.08 | +834.3% | 2.61 | +11.6% | 0.40 | -18.5% | piv sta drsi pst l2r twin sttsl abcd srvi wr |
| 10 | 0.4 | inv_vol | 0.08 | +741.1% | 2.62 | +19.3% | 0.61 | -15.5% | piv sta drsi pst l2r twin sttsl abcd srvi wr |
| 10 | 0.5 | igual | 0.10 | +845.0% | 2.52 | +13.7% | 0.46 | -16.0% | piv sta drsi pst l2r twin sttsl abcd srvi edma |
| 10 | 0.5 | inv_vol | 0.10 | +765.0% | 2.49 | +20.5% | 0.64 | -13.9% | piv sta drsi pst l2r twin sttsl abcd srvi edma |
| 12 | 0.2 | igual | 0.01 | +656.0% | 3.23 | +0.6% | 0.07 | -14.4% | piv sta l2r twin gs abcd srvi wr azl rtb tlb acr |
| 12 | 0.2 | inv_vol | 0.01 | +579.0% | 3.23 | -0.7% | 0.01 | -14.2% | piv sta l2r twin gs abcd srvi wr azl rtb tlb acr |
| 12 | 0.3 | igual | 0.05 | +758.3% | 2.89 | +3.7% | 0.18 | -17.4% | piv sta drsi pst l2r twin sttsl abcd srvi wr azl rtb |
| 12 | 0.3 | inv_vol | 0.05 | +686.8% | 2.90 | +9.9% | 0.38 | -14.9% | piv sta drsi pst l2r twin sttsl abcd srvi wr azl rtb |
| 12 | 0.4 | igual | 0.05 | +758.3% | 2.89 | +3.7% | 0.18 | -17.4% | piv sta drsi pst l2r twin sttsl abcd srvi wr azl rtb |
| 12 | 0.4 | inv_vol | 0.05 | +686.8% | 2.90 | +9.9% | 0.38 | -14.9% | piv sta drsi pst l2r twin sttsl abcd srvi wr azl rtb |
| 12 | 0.5 | igual | 0.06 | +764.5% | 2.80 | +13.0% | 0.47 | -16.3% | piv sta drsi pst l2r twin sttsl abcd srvi edma wr azl |
| 12 | 0.5 | inv_vol | 0.06 | +694.9% | 2.77 | +19.8% | 0.68 | -14.1% | piv sta drsi pst l2r twin sttsl abcd srvi edma wr azl |

## Aprovadas no treino

| # | Lote | Est | Nome | Célula | Geo | Partes + | Sem a melhor | Trades |
|---|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 2/2 | +115.0% | 6/6 | +2987.8% | 47452 |
| 2 | 25 | sta | 38. Stoch + ATR | 30min 34 ambos | +39.3% | 5/6 | +186.0% | 4420 |
| 3 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 4h r14 w30 d3 signal ambos | +37.8% | 5/6 | +232.1% | 1651 |
| 4 | 33 | pst | 8. Parabolic SAR stop entries | 1h af0.02 ambos | +36.8% | 4/6 | +67.7% | 2731 |
| 5 | 28 | l2r | 11. L2 Reversal Labels | 30min semtpsl ambos | +31.2% | 4/6 | +84.1% | 545 |
| 6 | 23 | twin | 1. Twin Range Filter | 1D sematr t0 sltp ambos | +30.6% | 5/6 | +119.5% | 156 |
| 7 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 1D SHORT p1 m3 sl3 | +28.4% | 6/6 | +194.8% | 140 |
| 8 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 15min como escrito ambos | +27.8% | 4/6 | +138.2% | 887 |
| 9 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 4h sl4.0% rr5 ambos | +27.2% | 6/6 | +182.3% | 315 |
| 10 | 24 | srvi | 7. Stochastic RSI + RVI | 4h p10 30/70 ambos | +26.7% | 5/6 | +121.1% | 359 |
| 11 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 30min fiel ambos | +25.4% | 4/6 | +64.1% | 746 |
| 12 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 30min l50 e40 ambos | +25.1% | 5/6 | +122.4% | 1143 |
| 13 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w140 -94/-6 sl0.005 contrario ambos | +24.9% | 4/6 | +122.6% | 2433 |
| 14 | 34 | azl | 7. Adaptive Zero Lag EMA | 1h cos thr0.05 ambos | +24.7% | 4/6 | +10.3% | 5509 |
| 15 | 26 | pprs | 16. Pivot Point Reversal + RSI | 30min pv3/3 ambos | +24.3% | 4/6 | +102.1% | 5960 |
| 16 | 27 | tch | 5. TSI CCI Hull | 4h p25 ambos | +24.1% | 5/6 | +84.2% | 176 |
| 17 | 25 | rtb | 47. Reversal Trading Bot | 1h sl3% tp6% ambos | +23.9% | 5/6 | +89.4% | 1464 |
| 18 | 29 | bot | 14. BotBot | 1D k0.02 ambos | +23.1% | 4/6 | +59.4% | 107 |
| 19 | ichimoku | ichimoku |  | 15min | +23.0% | 4/6 | +73.3% | 560 |
| 20 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 15min sl0.0 roc6.0 m3.0/3.0 ambos | +23.0% | 4/6 | +74.3% | 134 |
| 21 | 25 | ht3 | 36. Swing HULL + T3 | 4h 100 sltp ambos | +22.9% | 4/6 | +15.9% | 764 |
| 22 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 1h 12/26/9 ambos | +22.8% | 4/6 | +32.5% | 4610 |
| 23 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 30min 100/50/7 ambos | +22.7% | 4/6 | +26.2% | 4255 |
| 24 | 30 | hms | 20. Harmonic System | 4h close ambos | +22.6% | 5/6 | +84.5% | 1791 |
| 25 | 25 | tlb | 42. Trendline Breakout KedArc | 4h p5 semma ambos | +21.9% | 4/6 | +72.3% | 698 |
| 26 | 33 | cho | 9. Money Flow (Chaikin Oscillator) | 1D 3/10 ambos | +21.2% | 5/6 | +89.7% | 279 |
| 27 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 30min trig3 sl0.02 ambos | +20.6% | 5/6 | +97.0% | 211 |
| 28 | 31 | psw | 8. Swing Parabolic SAR | 4h af0.02 ambos | +20.1% | 4/6 | +29.1% | 1280 |
| 29 | 22 | ewo | 3. EWO RSI Exhaustion | 1h semvol ambos | +20.1% | 4/6 | +63.4% | 516 |
| 30 | 36 | mma | 15. Multi Moving Average Crossing | 15min 9/50/100 ambos | +20.1% | 4/6 | +29.2% | 2441 |
| 31 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 ambos | +19.6% | 6/6 | +44.6% | 296 |
| 32 | 22 | tst | 18. Triple SuperTrend + StochRSI | 30min 28/78 rr3.0/3.0 ambos | +19.3% | 4/6 | +73.1% | 449 |
| 33 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 4h sl3% tp35% sofiltro0 ambos | +19.2% | 4/6 | +45.5% | 120 |
| 34 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 15min lb20 pb2 tp2.0 sl2.0 | +19.1% | 4/6 | +72.6% | 2284 |
| 35 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 1h 50 rev ambos | +19.0% | 5/6 | +87.8% | 201 |
| 36 | 22 | hhll | 13. Highest High / Lowest Low | 4h 55 ambos | +18.8% | 4/6 | +45.5% | 134 |
| 37 | 28 | pab | 6. Price Action + Bollinger | 1h bb50 ambos | +18.6% | 6/6 | +80.3% | 245 |
| 38 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 30min f10 one tp5.0 | +18.3% | 5/6 | +63.3% | 1268 |
| 39 | 37 | chk | 18. Chaloke System | 4h 20/50/100 ambos | +18.0% | 5/6 | +27.3% | 257 |
| 40 | 33 | bct | 3. Bar Counter Trend Reversal | 4h kc2 ambos | +18.0% | 5/6 | +53.3% | 222 |
| 41 | 15 | comb | 2. Combined Strategy (fita de EMAs + RSI + Stoch) | 4h osc ambos | +17.6% | 4/6 | +18.4% | 725 |
| 42 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 1D m1.5 HA tp0.47 sl0.21 | +17.3% | 5/6 | +28.5% | 108 |
| 43 | 33 | stc | 10. SuperTrend chandelier 7/7 | 4h m7 ambos | +17.2% | 6/6 | +54.3% | 109 |
| 44 | 11 | grab | 4. Grab Trading System (80/21) | 4h 80/21 stop | +16.9% | 5/6 | +55.9% | 267 |
| 45 | 36 | kel | 12. Keltner SL/TP | 4h k2/sl20 ambos | +16.4% | 4/6 | +17.8% | 129 |
| 46 | 21 | kb | 15. Keltner bounce (SMA200 +- 8 ATR) | 1h 200 d3 ambos | +16.3% | 5/6 | +69.6% | 285 |
| 47 | 5 | pvb | 1. Price and Volume Breakout (60/60/200, so long) | 1h 20/50 x5 vol1 ls | +16.2% | 4/6 | +21.9% | 625 |
| 48 | 32 | qst | 8. QuantNomad SuperTrend | 1D m2 ambos | +16.1% | 4/6 | +30.3% | 115 |
| 49 | 25 | dbt | 44. Double Bottom/Top Hunter | 30min 30 ambos | +16.1% | 4/6 | +31.5% | 340 |
| 50 | 25 | cmo | 6. CMO TradeDots | 4h 40 ambos | +15.8% | 5/6 | +55.5% | 243 |
| 51 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 1h r14 m100 tend ambos | +15.8% | 4/6 | +37.4% | 484 |
| 52 | 24 | mbit | 3. Mbit MA (contrario) | 30min ma520 n10 ambos | +15.7% | 4/6 | +45.0% | 462 |
| 53 | 36 | lrb | 13. Linear Regression Channel Breakout | 1D n100 ambos | +15.5% | 4/6 | +14.4% | 162 |
| 54 | 28 | hamacd | 17. Heikin Ashi MACD | 1D tp10 sl3 ambos | +15.5% | 6/6 | +67.0% | 162 |
| 55 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 15min rr1.0 vol 24h ambos | +15.0% | 5/6 | +68.7% | 2785 |
| 56 | 23 | crazy | 10. Crazy Scalping (TMO + AMA) | 1h sl30 ambos | +15.0% | 5/6 | +25.1% | 370 |
| 57 | 22 | ichi | 8. Ichimoku no offset + RSI | 4h rsi0 ambos | +14.9% | 4/6 | +28.5% | 286 |
| 58 | 6 | hs | 1. Hammers & Stars (stop 1 ATR, alvo 1R) | 4h s2.0 rr2.0 fib0.333 ema200 | +14.9% | 4/6 | +7.6% | 249 |
| 59 | 37 | hul | 7. Hull Suite | 1D n55 ambos | +14.6% | 5/6 | +57.9% | 103 |
| 60 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 1D n55 ambos | +14.5% | 4/6 | +60.9% | 106 |
| 61 | 8 | eng | 4. Engulfing + SMA32 | 30min ma64 sl0.005 tp0.05 ambos | +14.3% | 5/6 | +50.1% | 4120 |
| 62 | 25 | pop | 22. Pivot of Pivot Reversal | 4h 4/2 ambos | +14.1% | 4/6 | +46.0% | 151 |
| 63 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 1h n30 5/20 ambos | +14.1% | 4/6 | +39.3% | 2480 |
| 64 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 1D atr10x2.0 | +13.5% | 5/6 | +29.5% | 103 |
| 65 | 20 | frama |  | 1D 40 propriotf ambos | +13.5% | 4/6 | +22.1% | 145 |
| 66 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 4h sw8 sl8atr tp1% ambos | +13.4% | 5/6 | +67.0% | 647 |
| 67 | 36 | sms | 9. Super Momentum | 30min cmo14 ambos | +13.2% | 5/6 | +54.5% | 466 |
| 68 | 22 | tdon | 9. Turtle Donchian/ATR | 1h 55/20 m2 short | +13.2% | 4/6 | +23.6% | 408 |
| 69 | 30 | ptr | 6. Percent Trailing Stop | 1D t5% ambos | +13.1% | 4/6 | +23.7% | 128 |
| 70 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 30min bb20 3 semlatest ambos | +12.9% | 5/6 | +25.1% | 257 |
| 71 | 33 | tbn | 7. Trend Bounce | 4h c7 ambos | +12.8% | 4/6 | +35.6% | 499 |
| 72 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 15min e60 tp/sl sim2 ambos | +12.8% | 4/6 | +29.8% | 2067 |
| 73 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 4h k3.0 sl3.0 be0.75 tp3.0 ema0 ambos | +12.4% | 4/6 | +1.2% | 436 |
| 74 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 1D a2.0 c14 | +12.3% | 4/6 | +43.0% | 121 |
| 75 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 1D a14 m2 ambos | +11.8% | 4/6 | +38.7% | 120 |
| 76 | 20 | nw |  | 1D 8 x25 ambos | +11.4% | 4/6 | +20.3% | 213 |
| 77 | 36 | cbo | 19. Candle Breakout 13h UTC | 15min h13/rr2 ambos | +11.0% | 6/6 | +53.2% | 2237 |
| 78 | 24 | sott | 1. SOTT | 4h s250 p0.618 ambos | +11.0% | 5/6 | +30.2% | 102 |
| 79 | 20 | fline |  | 4h 21 2.0 ambos | +10.9% | 4/6 | +20.6% | 126 |
| 80 | 24 | hf | 12. Hull Fisher | 1D h50 ambos | +10.8% | 4/6 | +32.6% | 100 |
| 81 | 20 | mrb |  | 1h 40 g2 m1 central ambos | +10.7% | 6/6 | +56.5% | 4659 |
| 82 | 9 | micu | 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips) | 4h sl0.0025 tp0 trail0 sess1 ambos | +10.6% | 4/6 | +10.9% | 1428 |
| 83 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 4h hon EMA21 x5 | +10.3% | 4/6 | +19.3% | 334 |
| 84 | 28 | sbf | 1. Stochastic (BiznesFilosof) | 1h 14/86 ambos | +10.0% | 4/6 | +29.7% | 488 |
| 85 | 25 | opw | 37. TASC One Percent A Week (long-only) | 1h dip1 tp1 | +10.0% | 6/6 | +49.3% | 406 |
| 86 | 22 | apsar | 7. ATR Parabolic SAR | 30min n1 0.01/0.1 ambos | +9.8% | 4/6 | +25.3% | 904 |
| 87 | 22 | mab | 11. Moving Average Band | 4h 100 rr3 ambos | +9.6% | 4/6 | +5.6% | 456 |
| 88 | 29 | vf | 19. Volume fight | 1h ma11 ambos | +9.3% | 4/6 | +8.8% | 4290 |
| 89 | 26 | sts | 5. SuperTrend STRATEGY | 4h m8.5 ambos | +9.3% | 5/6 | +20.6% | 101 |
| 90 | 20 | ds |  | 1h 8/34 ambos | +9.1% | 4/6 | +19.9% | 2633 |
| 91 | 37 | wmx | 15. WMX Williams Fractals | 4h o3 ambos | +8.9% | 4/6 | +14.4% | 1059 |
| 92 | 23 | ma1020 | 12. MA 10/20 Crossover | 1D 10/20 ambos | +8.9% | 4/6 | +5.0% | 127 |
| 93 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 15min r0.5 rr3.0 ret00 | +8.4% | 6/6 | +33.0% | 1900 |
| 94 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 30min r5 m100 ambos | +8.4% | 4/6 | +12.2% | 1556 |
| 95 | 28 | sma3 | 19. Tres medias (SMA 7/25/99) | 1D 7/25 ambos | +8.2% | 4/6 | +28.9% | 103 |
| 96 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 30min 12 2 ambos | +8.2% | 4/6 | +8.9% | 1511 |
| 97 | 23 | e3r | 3. 3 EMA + RSI | 1h sl0% x24 ambos | +8.2% | 6/6 | +20.4% | 550 |
| 98 | 31 | ten | 12. Tendency EMA + RSI | 1h x24 ambos | +8.1% | 6/6 | +20.0% | 551 |
| 99 | 29 | r2m | 9. RSI2 + medias (pullback) | 4h 5/95 ambos | +8.0% | 4/6 | +7.6% | 306 |
| 100 | 23 | mabb | 9. MA BB + RSI | 30min a9 vol ambos | +8.0% | 5/6 | +20.4% | 246 |
| 101 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 4h a1.0 atr11 hma2 ambos | +8.0% | 4/6 | +13.7% | 1406 |
| 102 | 27 | obv | 20. OBV Oscillator | 30min l50 ambos | +7.9% | 5/6 | +9.1% | 3836 |
| 103 | 24 | dcf | 9. Donchian free bot | 1h semtp ambos | +7.6% | 4/6 | +17.7% | 4540 |
| 104 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 1h p5 rr5.0 trend1 ambos | +7.1% | 4/6 | +4.9% | 262 |
| 105 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 1D len20 m1.0 ambos | +7.1% | 4/6 | +8.2% | 104 |
| 106 | 20 | 3st |  | 4h pl3.0 thr20 ambos | +6.9% | 4/6 | +22.0% | 142 |
| 107 | 25 | made | 4. MA Displaced Envelope + ATRTS | 1D 9 ambos | +6.8% | 4/6 | +18.0% | 133 |
| 108 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 30min bb20 2.0 sl1.0% tp1.0% ambos | +6.8% | 4/6 | +7.4% | 2153 |
| 109 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 30min sl0.01 rr0.0 eod1 filt1 ambos | +6.6% | 4/6 | +7.6% | 499 |
| 110 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 4h TILL 12/26/9 | +6.5% | 5/6 | +5.9% | 756 |
| 111 | 27 | sqr | 11. Squeeze Momentum on Reversal | 1h f0.0018 ambos | +6.5% | 4/6 | +1.5% | 2142 |
| 112 | 5 | qqe |  | 4h b60 x30 s180 sw20 wae0 lucro1 | +6.5% | 4/6 | +23.8% | 476 |
| 113 | 23 | dema | 8. DEMA ATR | 4h tp6 ambos | +6.4% | 4/6 | +2.6% | 178 |
| 114 | 9 | hull | 4. Hull Swing Trader (HMA 210 do open) | 4h p400 ambos | +6.3% | 4/6 | +1.3% | 161 |
| 115 | 24 | smc | 8. SMC | 15min lb8 ambos | +6.3% | 4/6 | +0.8% | 4222 |
| 116 | 29 | mrs | 17. MACD_RSI | 1D e20 ambos | +6.3% | 4/6 | +12.8% | 119 |
| 117 | 21 | hulk | 5. Hulk Scalper | 30min thr0.1 adx33 tp3.00% sl2.0% ambos | +6.1% | 5/6 | +19.9% | 263 |
| 118 | 34 | mls | 8. ML SuperTrend kNN | 1h f4 tp2.2 ambos | +6.1% | 5/6 | +11.0% | 1797 |
| 119 | 36 | kbb | 2. Kozlod BB | 1h bb55x2 ambos | +6.1% | 4/6 | +8.0% | 561 |
| 120 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 4h l50 m2.0 sl0.03 ambos | +5.9% | 4/6 | +17.1% | 126 |
| 121 | 29 | cez | 4. Chandelier Exit + ZLSMA | 15min m2 ambos | +5.6% | 5/6 | +16.7% | 1978 |
| 122 | 10 | pdiv | 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2) | 4h q1 m50 hid sl0.0 ambos | +5.5% | 4/6 | +4.3% | 194 |
| 123 | 22 | tsi | 5. TSI CCI Hull | 4h tp0.0% ambos | +5.3% | 4/6 | +0.3% | 186 |
| 124 | 25 | fbo | 43. Fractal Breakout | 4h ambos | +5.2% | 4/6 | +3.1% | 575 |
| 125 | 10 | aio | 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR) | 4h rsi1 atr2.0 rr1.0 ambos | +5.1% | 4/6 | +4.7% | 112 |
| 126 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 1D a20 m2 ambos | +5.0% | 4/6 | +4.2% | 124 |
| 127 | 30 | kal | 12. KALKI TFXBOT | 1h rr1.5 ambos | +4.9% | 5/6 | +13.7% | 873 |
| 128 | vixfix | grade |  | 4h ph0.95 str3 ob70 ambos u1 | +4.8% | 5/6 | +5.5% | 107 |
| 129 | 29 | ged | 7. PTS Golden Edge | 4h 9/50 ambos | +4.8% | 4/6 | +7.0% | 189 |
| 130 | 19 | 3ema | 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only) | 4h tp3 sl4 | +4.6% | 4/6 | +4.9% | 127 |
| 131 | 19 | cipher | 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11) | 1h semwt tp4 sl2 ambos | +4.6% | 4/6 | +15.7% | 397 |
| 132 | 21 | sqz | 2. Squeeze Momentum | 4h l2 sl0.5% tp1% semsqz ambos | +4.3% | 5/6 | +17.7% | 1194 |
| 133 | 20 | cam |  | 4h sl1% tp2% ambos | +4.1% | 4/6 | +15.3% | 1243 |
| 134 | 28 | ibm | 20. Babypips Inside Bar Momentum | 1h tp2 ambos | +4.0% | 4/6 | +8.6% | 4726 |
| 135 | 31 | fxf | 14. FXFUNDINGMATE Trend | 4h tp1atr ambos | +3.9% | 4/6 | +9.1% | 306 |
| 136 | 20 | rsirev |  | 1D 8 1.5 ha ambos | +3.7% | 4/6 | +3.9% | 205 |
| 137 | 4 | aist |  | 15min 6h/12h f5.0/4.0 adx1 | +3.6% | 4/6 | +6.9% | 123 |
| 138 | 20 | atrgod |  | 30min sl2.0 rr2.0 semfiltros ambos | +3.5% | 4/6 | +6.5% | 1873 |
| 139 | 25 | nr7s | 46. NR7ID (short-only) | 30min semfiltro | +3.3% | 4/6 | +4.9% | 3077 |
| 140 | 24 | vws | 16. VWMA/SMA 3Commas | 1D niveis long | +3.3% | 4/6 | +8.7% | 121 |
| 141 | 18 | osb | 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario) | 30min m0.5 sl2.00% ambos | +2.7% | 4/6 | +3.4% | 335 |
| 142 | zigzagpa | grade |  | 1h ew0.0 tp1.618 sl-0.236 | +2.6% | 4/6 | +4.1% | 174 |
| 143 | 37 | mrs | 5. Mean-Reversion Swing | 30min n50 ambos | +2.1% | 4/6 | +7.6% | 360 |
