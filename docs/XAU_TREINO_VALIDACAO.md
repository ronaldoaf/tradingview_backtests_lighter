# XAU: treino / validação / OOS

Período todo (2017-09-01 a 2026-10-04) em 10 partes iguais: 1–6 treino (até 2023-02-14), 7–9 validação (até 2025-11-06), 10 OOS (não lido). B&H XAU na validação: +115,1%.

Mesmo método do BTC/WTI (scripts/tvo.py, ATIVO=xau): exclusão só no treino (geo > 0, ≥4/6 partes positivas, sem a melhor parte > 0, ≥100 trades), melhor célula por estratégia pela geo, templates fora. 18.863 células; aprovadas: 256 estratégias.

| K | Teto | Peso | Corr média | Treino | Sharpe treino | Validação | Sharpe val | DD val | Estratégias |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 0.2 | igual | 0.02 | +84,6% | 1.88 | +6,9% | 0.44 | -8,7% | tsi ut qst e5 moon drm |
| 6 | 0.2 | inv_vol | 0.02 | +84,7% | 1.88 | +7,6% | 0.48 | -8,7% | tsi ut qst e5 moon drm |
| 6 | 0.3 | igual | 0.18 | +99,3% | 1.68 | +23,1% | 1.10 | -7,5% | tsi mtl ut hulk bbr gso |
| 6 | 0.3 | inv_vol | 0.18 | +97,9% | 1.69 | +23,5% | 1.14 | -7,2% | tsi mtl ut hulk bbr gso |
| 6 | 0.4 | igual | 0.17 | +102,4% | 1.69 | +11,0% | 0.52 | -9,7% | tsi tott hulk ged stt gs |
| 6 | 0.4 | inv_vol | 0.17 | +102,4% | 1.69 | +11,5% | 0.54 | -9,3% | tsi tott hulk ged stt gs |
| 6 | 0.5 | igual | 0.29 | +110,5% | 1.57 | +25,0% | 0.93 | -7,4% | tsi tott ut hulk mst sbs |
| 6 | 0.5 | inv_vol | 0.29 | +110,2% | 1.57 | +25,2% | 0.95 | -7,4% | tsi tott ut hulk mst sbs |
| 8 | 0.2 | igual | -0.00 | +74,9% | 2.17 | +2,7% | 0.25 | -6,3% | tsi ut qst e5 moon drm sr xscalp |
| 8 | 0.2 | inv_vol | -0.00 | +73,2% | 2.17 | +2,5% | 0.24 | -6,0% | tsi ut qst e5 moon drm sr xscalp |
| 8 | 0.3 | igual | 0.13 | +90,6% | 1.80 | +17,3% | 0.96 | -6,5% | tsi mtl ut hulk bbr gso wyk e5 |
| 8 | 0.3 | inv_vol | 0.13 | +89,5% | 1.81 | +17,0% | 0.96 | -6,5% | tsi mtl ut hulk bbr gso wyk e5 |
| 8 | 0.4 | igual | 0.16 | +93,1% | 1.73 | +14,3% | 0.75 | -6,7% | tsi tott hulk ged stt gs bbr gso |
| 8 | 0.4 | inv_vol | 0.16 | +92,4% | 1.74 | +14,9% | 0.79 | -6,4% | tsi tott hulk ged stt gs bbr gso |
| 8 | 0.5 | igual | 0.26 | +103,8% | 1.60 | +18,9% | 0.77 | -9,5% | tsi tott ut hulk mst sbs ged stt |
| 8 | 0.5 | inv_vol | 0.26 | +103,8% | 1.61 | +19,3% | 0.79 | -9,4% | tsi tott ut hulk mst sbs ged stt |
| 10 | 0.2 | igual | 0.01 | +64,4% | 2.23 | -2,0% | -0.20 | -5,6% | tsi ut qst e5 moon drm sr xscalp mabb abcd |
| 10 | 0.2 | inv_vol | 0.01 | +59,4% | 2.19 | -4,2% | -0.46 | -5,7% | tsi ut qst e5 moon drm sr xscalp mabb abcd |
| 10 | 0.3 | igual | 0.14 | +84,9% | 1.81 | +9,4% | 0.63 | -8,5% | tsi mtl ut hulk bbr gso wyk e5 hs moon |
| 10 | 0.3 | inv_vol | 0.14 | +83,4% | 1.82 | +8,1% | 0.57 | -8,6% | tsi mtl ut hulk bbr gso wyk e5 hs moon |
| 10 | 0.4 | igual | 0.13 | +87,4% | 1.81 | +11,7% | 0.70 | -8,5% | tsi tott hulk ged stt gs bbr gso wyk e5 |
| 10 | 0.4 | inv_vol | 0.13 | +86,7% | 1.82 | +11,7% | 0.71 | -8,4% | tsi tott hulk ged stt gs bbr gso wyk e5 |
| 10 | 0.5 | igual | 0.27 | +97,6% | 1.59 | +16,6% | 0.74 | -8,7% | tsi tott ut hulk mst sbs ged stt ut cbo |
| 10 | 0.5 | inv_vol | 0.27 | +96,9% | 1.59 | +16,8% | 0.75 | -8,6% | tsi tott ut hulk mst sbs ged stt ut cbo |
| 12 | 0.2 | igual | 0.01 | +56,4% | 2.19 | -6,3% | -0.73 | -7,3% | tsi ut qst e5 moon drm sr xscalp mabb abcd wr grab |
| 12 | 0.2 | inv_vol | 0.01 | +50,0% | 2.10 | -8,4% | -1.05 | -9,2% | tsi ut qst e5 moon drm sr xscalp mabb abcd wr grab |
| 12 | 0.3 | igual | 0.09 | +80,7% | 2.07 | +2,1% | 0.20 | -9,5% | tsi mtl ut hulk bbr gso wyk e5 hs moon drm fm |
| 12 | 0.3 | inv_vol | 0.09 | +78,8% | 2.07 | +0,4% | 0.06 | -10,3% | tsi mtl ut hulk bbr gso wyk e5 hs moon drm fm |
| 12 | 0.4 | igual | 0.12 | +83,5% | 1.92 | +10,6% | 0.67 | -8,0% | tsi tott hulk ged stt gs bbr gso wyk e5 htf hs |
| 12 | 0.4 | inv_vol | 0.12 | +82,4% | 1.94 | +9,5% | 0.63 | -7,9% | tsi tott hulk ged stt gs bbr gso wyk e5 htf hs |
| 12 | 0.5 | igual | 0.25 | +93,4% | 1.60 | +13,2% | 0.63 | -8,2% | tsi tott ut hulk mst sbs ged stt ut cbo gs kha |
| 12 | 0.5 | inv_vol | 0.25 | +93,1% | 1.60 | +13,4% | 0.64 | -8,1% | tsi tott ut hulk mst sbs ged stt ut cbo gs kha |

## Aprovadas no treino (top 40)

| # | Lote | Est | Nome | Célula | Geo | Partes + | Trades |
|---|---|---|---|---|---|---|---|
| 1 | 22 | tsi | 5. TSI CCI Hull | 30min tp0.0% ambos | +16,5% | 6/6 | 1034 |
| 2 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR20 p1.0 c0.0 | +14,4% | 5/6 | 754 |
| 3 | 27 | tch | 5. TSI CCI Hull | 30min p25 ambos | +14,3% | 4/6 | 1026 |
| 4 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 1h l20 e20 ambos | +14,2% | 5/6 | 978 |
| 5 | 34 | mtl | 2. Market Trend Levels | 1h 20/50 adx20 ambos | +13,7% | 6/6 | 360 |
| 6 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 4h % 2.0 | +13,5% | 6/6 | 231 |
| 7 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 30min hon DEMA21 x5 | +12,9% | 4/6 | 2687 |
| 8 | 36 | kel | 12. Keltner SL/TP | 30min k2/sl5 ambos | +12,6% | 5/6 | 684 |
| 9 | 28 | hvc | 14. Hull MA vs Candle | 15min h100 ambos | +12,2% | 4/6 | 2170 |
| 10 | 27 | atrts | 15. ATR Trailing Stops | 4h a10x2 ambos | +12,0% | 5/6 | 578 |
| 11 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 4h a2.0 c10 | +11,9% | 4/6 | 580 |
| 12 | 20 | ceyhun |  | 4h m2 2 ambos | +11,9% | 4/6 | 580 |
| 13 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 4h a10 m2 ambos | +11,9% | 4/6 | 580 |
| 14 | 23 | ttm | 18. Trend Trader + MACD | 4h m3 semmacd ambos | +11,7% | 6/6 | 635 |
| 15 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 30min 20 rev ambos | +11,6% | 4/6 | 1275 |
| 16 | 20 | fline |  | 1h 50 1.0 ambos | +11,6% | 5/6 | 657 |
| 17 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 1h a5.0 atr30 hma2 ambos | +11,5% | 5/6 | 384 |
| 18 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 1h len20 m2.0 ambos | +11,4% | 4/6 | 1019 |
| 19 | 25 | thma | 9. Triangular Hull MA | 1h 40 ambos | +11,4% | 5/6 | 1614 |
| 20 | 21 | hulk | 5. Hulk Scalper | 15min thr0.1 adx25 tp3.00% sl2.0% ambos | +11,3% | 5/6 | 280 |
| 21 | 25 | mst | 11. Master Supertrend | 1h 20 m4 ambos | +11,3% | 6/6 | 780 |
| 22 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 4h a14 m2 ambos | +11,2% | 4/6 | 585 |
| 23 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 30min 50 24/52/18 obv0 ls | +11,1% | 4/6 | 527 |
| 24 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 30min sl2.00% sessao ambos | +10,9% | 6/6 | 2856 |
| 25 | 14 | hap | 2. Heikin-Ashi PSAR [QuantNomad] | 1h 0.01/0.01/0.1 ambos | +10,9% | 5/6 | 1730 |
| 26 | ichimoku | ichimoku |  | 1h | +10,8% | 5/6 | 399 |
| 27 | 32 | srs | 17. Supertrend + RSI (Alorse) | 4h f2 ambos | +10,4% | 4/6 | 539 |
| 28 | 31 | lst | 13. LunaOwl SuperTrend 2 | 4h m2.618 ambos | +10,4% | 5/6 | 365 |
| 29 | 12 | tk | 1. TK Cross > EMA200 (20/60, long-only) | 30min 20/60 ema0 ambos | +10,3% | 4/6 | 1953 |
| 30 | 4 | ppst | 2. Pivot Point SuperTrend (2, 3, 10) | 1h p5 f2.0 a10 | +10,2% | 4/6 | 762 |
| 31 | 29 | ged | 7. PTS Golden Edge | 30min 9/50 ambos | +10,0% | 5/6 | 1122 |
| 32 | 25 | sr | 3. Support Resistance | 1h 10 ambos | +10,0% | 4/6 | 1232 |
| 33 | 22 | psarc | 14. Parabolic SAR on close | 4h n1 0.01/0.1 ambos | +9,9% | 4/6 | 502 |
| 34 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 4h m1.5 HA tp0.03 sl0.01 | +9,9% | 6/6 | 491 |
| 35 | 32 | stt | 16. SuperTrend Trapping Candle | 30min 0.6% ambos | +9,8% | 6/6 | 3374 |
| 36 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 1h r8 m10 tend ambos | +9,7% | 5/6 | 2051 |
| 37 | 31 | pse | 17. Parabolic SAR w/ EMA | 1h off0% ambos | +9,6% | 6/6 | 1154 |
| 38 | 25 | made | 4. MA Displaced Envelope + ATRTS | 4h 9 ambos | +9,6% | 6/6 | 484 |
| 39 | 22 | emax | 2. EMA Crossover hl2 | 15min 20x5 ambos | +9,5% | 4/6 | 2287 |
| 40 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 30min k3.0 sl3.0 be0.75 tp0.0 ema0 ambos | +9,4% | 4/6 | 1881 |
