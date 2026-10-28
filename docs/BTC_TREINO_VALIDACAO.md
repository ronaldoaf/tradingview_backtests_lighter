# BTC: treino / validação / OOS

Período todo (2020-01-01 a 2026-09-30) em 10 partes iguais: 1–6 treino (até 2023-05-17), 7–9 validação (até 2026-01-27), 10 OOS (não lido). B&H BTC na validação: +115,9%.

Mesmo método do WTI (scripts/tvo.py): exclusão só no treino (geo > 0, ≥4/6 partes positivas, sem a melhor parte > 0, ≥100 trades), melhor célula por estratégia pela geo, templates fora. 18.976 células; aprovadas: 386 estratégias.

| K | Teto | Peso | Corr média | Treino | Sharpe treino | Validação | Sharpe val | DD val | Estratégias |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 0.2 | igual | 0.06 | +2997.7% | 3.25 | -7.7% | -0.13 | -30.4% | piv macdre strex tdh vwap tbn |
| 6 | 0.2 | inv_vol | 0.06 | +2522.3% | 3.36 | -10.6% | -0.25 | -31.0% | piv macdre strex tdh vwap tbn |
| 6 | 0.3 | igual | 0.19 | +4420.0% | 2.92 | +65.3% | 1.33 | -11.5% | piv drsi ftsma wyk qqe scalp |
| 6 | 0.3 | inv_vol | 0.19 | +4286.4% | 2.92 | +65.8% | 1.35 | -11.4% | piv drsi ftsma wyk qqe scalp |
| 6 | 0.4 | igual | 0.23 | +5261.3% | 2.76 | +19.1% | 0.51 | -32.1% | piv drsi ftsma ichimoku obv wyk |
| 6 | 0.4 | inv_vol | 0.23 | +5274.0% | 2.77 | +21.0% | 0.55 | -31.9% | piv drsi ftsma ichimoku obv wyk |
| 6 | 0.5 | igual | 0.29 | +5474.7% | 2.64 | +26.5% | 0.58 | -30.7% | piv drsi ftsma ichimoku force ht3 |
| 6 | 0.5 | inv_vol | 0.29 | +5479.0% | 2.66 | +28.0% | 0.60 | -30.3% | piv drsi ftsma ichimoku force ht3 |
| 8 | 0.2 | igual | 0.03 | +2403.4% | 3.48 | +9.8% | 0.36 | -23.6% | piv macdre strex tdh vwap tbn tsh abcd |
| 8 | 0.2 | inv_vol | 0.03 | +2099.6% | 3.62 | +3.3% | 0.18 | -25.7% | piv macdre strex tdh vwap tbn tsh abcd |
| 8 | 0.3 | igual | 0.13 | +3623.1% | 3.23 | +29.4% | 0.80 | -12.5% | piv drsi ftsma wyk qqe scalp tdh vwap |
| 8 | 0.3 | inv_vol | 0.13 | +3482.3% | 3.24 | +31.3% | 0.84 | -12.8% | piv drsi ftsma wyk qqe scalp tdh vwap |
| 8 | 0.4 | igual | 0.21 | +4495.6% | 2.90 | +18.5% | 0.51 | -31.8% | piv drsi ftsma ichimoku obv wyk cs macd |
| 8 | 0.4 | inv_vol | 0.21 | +4437.6% | 2.91 | +20.4% | 0.54 | -31.4% | piv drsi ftsma ichimoku obv wyk cs macd |
| 8 | 0.5 | igual | 0.27 | +4865.0% | 2.70 | +12.3% | 0.37 | -32.7% | piv drsi ftsma ichimoku force ht3 obv wyk |
| 8 | 0.5 | inv_vol | 0.27 | +4884.8% | 2.71 | +13.7% | 0.40 | -32.1% | piv drsi ftsma ichimoku force ht3 obv wyk |
| 10 | 0.2 | igual | 0.03 | +1720.7% | 3.77 | +14.3% | 0.56 | -19.2% | piv macdre strex tdh vwap tbn tsh abcd opw tlb |
| 10 | 0.2 | inv_vol | 0.03 | +1190.7% | 4.09 | +14.4% | 0.66 | -16.3% | piv macdre strex tdh vwap tbn tsh abcd opw tlb |
| 10 | 0.3 | igual | 0.10 | +2934.3% | 3.39 | +30.0% | 0.86 | -14.0% | piv drsi ftsma wyk qqe scalp tdh vwap tbn tsh |
| 10 | 0.3 | inv_vol | 0.10 | +2664.5% | 3.49 | +23.0% | 0.72 | -15.1% | piv drsi ftsma wyk qqe scalp tdh vwap tbn tsh |
| 10 | 0.4 | igual | 0.20 | +4044.5% | 2.98 | +21.3% | 0.59 | -24.7% | piv drsi ftsma ichimoku obv wyk cs macd crypto qqe |
| 10 | 0.4 | inv_vol | 0.20 | +3954.8% | 3.00 | +24.0% | 0.65 | -23.4% | piv drsi ftsma ichimoku obv wyk cs macd crypto qqe |
| 10 | 0.5 | igual | 0.23 | +4415.4% | 2.85 | +16.1% | 0.46 | -30.7% | piv drsi ftsma ichimoku force ht3 obv wyk macd crypto |
| 10 | 0.5 | inv_vol | 0.23 | +4393.6% | 2.88 | +18.1% | 0.50 | -30.3% | piv drsi ftsma ichimoku force ht3 obv wyk macd crypto |
| 12 | 0.2 | igual | 0.03 | +1313.0% | 3.87 | +13.0% | 0.58 | -16.7% | piv macdre strex tdh vwap tbn tsh abcd opw tlb lch seq |
| 12 | 0.2 | inv_vol | 0.03 | +824.5% | 4.25 | +12.3% | 0.71 | -12.9% | piv macdre strex tdh vwap tbn tsh abcd opw tlb lch seq |
| 12 | 0.3 | igual | 0.08 | +2324.2% | 3.61 | +24.1% | 0.80 | -13.7% | piv drsi ftsma wyk qqe scalp tdh vwap tbn tsh abcd tq |
| 12 | 0.3 | inv_vol | 0.08 | +1919.8% | 3.71 | +14.9% | 0.58 | -16.7% | piv drsi ftsma wyk qqe scalp tdh vwap tbn tsh abcd tq |
| 12 | 0.4 | igual | 0.18 | +3596.5% | 3.07 | +11.8% | 0.40 | -24.7% | piv drsi ftsma ichimoku obv wyk cs macd crypto qqe vwap c123 |
| 12 | 0.4 | inv_vol | 0.18 | +3554.5% | 3.08 | +14.7% | 0.47 | -23.5% | piv drsi ftsma ichimoku obv wyk cs macd crypto qqe vwap c123 |
| 12 | 0.5 | igual | 0.24 | +3948.4% | 2.82 | +11.9% | 0.38 | -27.7% | piv drsi ftsma ichimoku force ht3 obv wyk macd crypto qqe rsx |
| 12 | 0.5 | inv_vol | 0.24 | +3895.1% | 2.85 | +14.9% | 0.45 | -26.2% | piv drsi ftsma ichimoku force ht3 obv wyk macd crypto qqe rsx |

## Aprovadas no treino (top 40)

| # | Lote | Est | Nome | Célula | Geo | Partes + | Trades |
|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 8/4 | +105.9% | 6/6 | 18975 |
| 2 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 1h r21 w50 d3 zero ambos | +99.1% | 5/6 | 3620 |
| 3 | 17 | ftsma | 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier) | 4h 5/20/200 ft ambos | +75.4% | 6/6 | 246 |
| 4 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 4h HULL 12/26/9 | +72.6% | 6/6 | 2490 |
| 5 | 21 | strex | 6. SuperTREX (RSI semanal amostrado) | 1h m4 ambos | +71.7% | 6/6 | 231 |
| 6 | ichimoku | ichimoku |  | 15min | +70.4% | 6/6 | 1209 |
| 7 | 22 | force | 17. Force trade scalper | 4h 3/20 ambos | +68.7% | 5/6 | 264 |
| 8 | 25 | ht3 | 36. Swing HULL + T3 | 1h 100 sltp ambos | +66.8% | 5/6 | 2299 |
| 9 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 1h 50/50/7 ambos | +66.2% | 5/6 | 3078 |
| 10 | 34 | khw | 10. Kahlman HullMA / WT Cross | 1h h48 sem wt ambos | +65.1% | 5/6 | 3313 |
| 11 | 28 | hamacd | 17. Heikin Ashi MACD | 1h semsltp ambos | +64.2% | 4/6 | 3859 |
| 12 | 33 | vxe | 18. VWAP X EMA | 4h ema20 ambos | +63.1% | 5/6 | 988 |
| 13 | 27 | obv | 20. OBV Oscillator | 1h l20 ambos | +62.1% | 5/6 | 2810 |
| 14 | 27 | wyk | 13. Wyckoff Range | 1h sl10% ambos | +61.4% | 5/6 | 561 |
| 15 | 23 | evw | 19. EVWMA x VWAP | 4h 100 ambos | +60.6% | 6/6 | 254 |
| 16 | 22 | tst | 18. Triple SuperTrend + StochRSI | 30min 20/80 rr2.0/1.5 ambos | +60.2% | 5/6 | 628 |
| 17 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 15min e200 tp/sl default ambos | +60.2% | 5/6 | 1357 |
| 18 | 20 | macd |  | 30min m2.2 tp5% filtro | +59.0% | 6/6 | 1872 |
| 19 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 30min 9 24/52/18 obv1 ls | +58.3% | 4/6 | 1496 |
| 20 | 23 | stv | 16. Super trend V | 15min m1 ambos | +57.7% | 6/6 | 2195 |
| 21 | 5 | qqe |  | 4h b30 x15 s90 sw20 wae1 lucro1 | +57.3% | 6/6 | 423 |
| 22 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 15min r10 m50 | +56.5% | 6/6 | 4051 |
| 23 | 18 | slope | 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200) | 1h 50 9/21 filtro ambos | +56.0% | 5/6 | 1997 |
| 24 | 7 | srt | 5. SR TREND (21) | 4h len100 | +55.7% | 5/6 | 278 |
| 25 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 1h 30 2 ambos | +55.5% | 6/6 | 345 |
| 26 | 26 | rsx | 12. RSI Crossover | 1h r50/25 ambos | +54.2% | 6/6 | 6656 |
| 27 | 31 | cmb | 20. Combo 123 Reversal & Stochastic | 1h l14 ambos | +54.0% | 5/6 | 950 |
| 28 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 30min n100 ambos | +53.4% | 6/6 | 3573 |
| 29 | 30 | mma | 3. Multi-MA | 30min l66 ambos | +53.3% | 6/6 | 1918 |
| 30 | 30 | mbf | 16. Momentum BF | 1D l36 ambos | +53.2% | 5/6 | 180 |
| 31 | 31 | pse | 17. Parabolic SAR w/ EMA | 30min off0% ambos | +52.7% | 5/6 | 2950 |
| 32 | 17 | stcci | 1. Supertrend CCI (sinal do CCI28) | 1D cci50 ambos | +52.4% | 5/6 | 131 |
| 33 | 28 | mab | 13. Moving Average (BiznesFilosof) | 1D sma50 ambos | +52.4% | 5/6 | 131 |
| 34 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 15min bb20 3 latest ambos | +52.2% | 5/6 | 407 |
| 35 | 25 | era | 31. EMA Cross + RSI + ADX | 4h sl2 ambos | +52.2% | 6/6 | 293 |
| 36 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 1h VAR20 p0.5 c0.005 | +51.8% | 5/6 | 304 |
| 37 | 28 | hapa | 10. Heikin Ashi Price Action | 4h ha ambos | +51.7% | 5/6 | 915 |
| 38 | 22 | apsar | 7. ATR Parabolic SAR | 4h n1 0.02/0.2 ambos | +51.6% | 5/6 | 287 |
| 39 | 21 | surf | 1. Trend Surfers Breakout | 15min p168 t8.0 f2.0 ambos | +51.5% | 6/6 | 1271 |
| 40 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 30min hon HULL13 x5 | +51.2% | 5/6 | 3524 |
