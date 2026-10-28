# WTI em 8 partes: 47 aprovadas

Período antes do OOS (2017-01-03 a 2024-10-19) em 8 partes iguais; trades abertos em abril de 2020 descartados; OOS fora da seleção.

Critério: a célula (TF × configuração) passa se a média geométrica das 8 partes, exp(média ln(1+r_i)) − 1, é positiva **e** nenhuma parte perde mais de 5%. Fica a melhor célula aprovada de cada estratégia. 452 estratégias → 47.

| # | Lote | Est | Nome | Célula | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | Geo | Pior | Partes + | Trades |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 5min 2/2 | +97% | +52% | +218% | +224% | +32% | +154% | -4% | +68% | +89% | -4% | 7 | 47452 |
| 2 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 4h como escrito ambos | +29% | +59% | +20% | +18% | +25% | +78% | +42% | +59% | +40% | +18% | 8 | 51 |
| 3 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.05 roc6.0 m3.0/3.0 ambos | -0% | +53% | +54% | +44% | +2% | -5% | +58% | +98% | +34% | -5% | 6 | 304 |
| 4 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 1D SHORT p1 m4.0 sl3.0 | +1% | +63% | +12% | +40% | +4% | +44% | +69% | +30% | +31% | +1% | 8 | 139 |
| 5 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 30min f10 one tp5.0 | +5% | +5% | +24% | +19% | -0% | +66% | +25% | +15% | +18% | -0% | 7 | 1268 |
| 6 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 1h l20 e40 ambos | +35% | +50% | +20% | +37% | -4% | -5% | -3% | +16% | +17% | -5% | 5 | 1601 |
| 7 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 ambos | +1% | +11% | +16% | +103% | +1% | +10% | -2% | -1% | +14% | -2% | 6 | 296 |
| 8 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 4h sl1% rr5 ambos | -3% | +33% | +42% | +2% | +6% | +9% | +5% | -4% | +10% | -4% | 6 | 460 |
| 9 | 36 | cbo | 19. Candle Breakout 13h UTC | 15min h13/rr2 ambos | +13% | +9% | +5% | +18% | +2% | +22% | -3% | -1% | +8% | -3% | 6 | 2237 |
| 10 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 15min rr1.0 vol sess ambos | +13% | -2% | +42% | +17% | +0% | -3% | -4% | +1% | +7% | -4% | 5 | 1163 |
| 11 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 30min m4.0 normal tp0.03 sl0.01 | +11% | +10% | -5% | +5% | +6% | -1% | +24% | +3% | +6% | -5% | 6 | 2106 |
| 12 | 28 | l2r | 11. L2 Reversal Labels | 30min tpsl ambos | +4% | -2% | +18% | -2% | +4% | +19% | -5% | +15% | +6% | -5% | 5 | 547 |
| 13 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 1D lb10 pb2 tp2.0 sl1.0 | +1% | +5% | +11% | +5% | +2% | -5% | +17% | +10% | +5% | -5% | 7 | 397 |
| 14 | 20 | cam |  | 4h sl1% tp2% ambos | +5% | +7% | +7% | -2% | -2% | +10% | +17% | -3% | +5% | -3% | 5 | 1243 |
| 15 | 21 | sqz | 2. Squeeze Momentum | 4h l2 sl0.5% tp1% semsqz ambos | -1% | +1% | +9% | +5% | +7% | +5% | +0% | +11% | +5% | -1% | 7 | 1194 |
| 16 | 20 | atrgod |  | 4h sl2.0 rr2.0 filtros ambos | +1% | -2% | +5% | +0% | +9% | +9% | +9% | +3% | +4% | -2% | 7 | 47 |
| 17 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 5min r0.5 rr3.0 ret11 | -1% | +17% | +9% | -2% | -1% | +11% | +1% | -1% | +4% | -2% | 4 | 1911 |
| 18 | 20 | 3st |  | 1D pl1.5 thr20 ambos | +3% | +3% | +0% | +5% | +2% | +15% | +0% | +5% | +4% | +0% | 7 | 24 |
| 19 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 15min p3 rr5.0 trend1 ambos | +2% | -2% | +10% | +2% | +1% | +15% | +5% | -1% | +4% | -2% | 6 | 1212 |
| 20 | 25 | nr7s | 46. NR7ID (short-only) | 1D sma14 | +4% | +7% | -1% | +0% | -1% | +9% | +7% | +5% | +4% | -1% | 5 | 24 |
| 21 | 31 | lch | 5. Linear Channel (long-only) | 1h v4% hma400 | +0% | +0% | -2% | +10% | +0% | +22% | +0% | +0% | +3% | -2% | 2 | 22 |
| 22 | zigzagpa | grade |  | 1h ew0.0 tp1.618 sl-1.0 | -4% | -4% | +13% | +9% | +0% | +5% | -3% | +11% | +3% | -4% | 5 | 89 |
| 23 | 24 | ectp | 19. EMA Crossover with TP | 1D sl3% tp0.5 ambos | -2% | +13% | -2% | -4% | -3% | +5% | +5% | +13% | +3% | -4% | 4 | 49 |
| 24 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 4h l200 m1.5 sl0.002 long | -1% | -4% | +7% | +27% | +2% | -2% | -0% | -3% | +3% | -4% | 3 | 123 |
| 25 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w14 -94/-6 sl0.005 contrario long | +5% | -0% | -4% | +26% | -4% | -4% | +5% | -0% | +3% | -4% | 3 | 84 |
| 26 | 30 | dip | 15. Scalping Dips On Trend (long-only) | 30min d4 tp6% | +0% | +0% | +0% | +14% | +0% | +7% | +0% | +0% | +3% | +0% | 2 | 19 |
| 27 | 19 | cipher | 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11) | 1h wt tp4 sl2 ambos | +3% | +6% | +1% | +8% | +4% | -1% | -0% | -1% | +3% | -1% | 5 | 46 |
| 28 | 12 | pt | 2. Powertrend (range filter de volume, 200, long-only) | 1h l400 m3.0 vol | +2% | -2% | +3% | +15% | +4% | -5% | +0% | +0% | +2% | -5% | 4 | 15 |
| 29 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 1D sw20 sl8atr tp1% ambos | +4% | +0% | +1% | +4% | -0% | +7% | -4% | +4% | +2% | -4% | 6 | 46 |
| 30 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 1D bb20 2.0 sl2.0% tp2.0% ambos | +4% | -5% | +11% | +0% | -0% | +9% | -4% | +2% | +2% | -5% | 4 | 43 |
| 31 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 1D sl1% tp35% filtros ambos | -3% | +28% | -0% | -3% | +0% | +0% | -1% | -3% | +2% | -3% | 1 | 14 |
| 32 | 11 | sce | 2. Strategy Code Example (EMA14x21 do open, stop 0,1% alvo 0,5%) | 4h 50/200 sl0.005 tp0.025 ambos | +10% | +3% | -2% | +0% | -0% | +1% | -3% | +5% | +2% | -3% | 5 | 91 |
| 33 | 37 | mrs | 5. Mean-Reversion Swing | 30min n50 ambos | -3% | +3% | +2% | +6% | +5% | -0% | +3% | -2% | +2% | -3% | 5 | 360 |
| 34 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 4h sl0.01 rr2.0 eod0 filt1 ambos | -0% | +2% | +0% | -4% | +1% | +5% | +7% | +3% | +2% | -4% | 6 | 107 |
| 35 | 37 | rvc | 13. Reversal Catcher | 4h bb1.5 long | +2% | +0% | +3% | +4% | -0% | -2% | +2% | +3% | +2% | -2% | 6 | 25 |
| 36 | 21 | hulk | 5. Hulk Scalper | 30min thr0.3 adx33 tp1.35 sl1.1 ambos | -1% | -1% | +0% | +3% | -1% | +2% | +1% | +5% | +1% | -1% | 5 | 202 |
| 37 | 16 | qqe | 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao) | 30min XQ f5 dfil long | -2% | -2% | -2% | +10% | +3% | +6% | -5% | +0% | +1% | -5% | 4 | 268 |
| 38 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 1D sl0.50% 24h ambos | -0% | -3% | -1% | +6% | +0% | +2% | +3% | -1% | +1% | -3% | 4 | 295 |
| 39 | 30 | stpb | 14. Supertrend pullback | 4h flip ambos | -1% | +2% | +7% | -1% | -4% | +1% | +3% | -1% | +1% | -4% | 4 | 227 |
| 40 | 24 | stb | 5. SuperTrend Backtester | 1D tp1% ambos | -0% | +3% | -3% | -0% | -0% | +2% | +3% | +0% | +1% | -3% | 4 | 63 |
| 41 | 22 | bbra | 1. BB + RSI + ADX | 1D sl1.0% adx32 ambos | +0% | -1% | +0% | +2% | +1% | -2% | +2% | +2% | +1% | -2% | 4 | 18 |
| 42 | 32 | r2 | 7. AK RSI 2 | 1D 5/90 long | +0% | +0% | +0% | +0% | +6% | -1% | +0% | -1% | +1% | -1% | 4 | 23 |
| 43 | 15 | es | 4. EMA STOCH (Crypto BOT lower timeframes) | 30min sl/tp1% long | +0% | -0% | +1% | -2% | -0% | +2% | +0% | +2% | +0% | -2% | 5 | 46 |
| 44 | 27 | gsc | 6. Gold Scalping | 1D tp0.1% ambos | +1% | -1% | +1% | +0% | -3% | +0% | +4% | +1% | +0% | -3% | 5 | 63 |
| 45 | 25 | smp | 50. Smart Money Pivot | 1D p20 sl1% tp1.5% ambos | -1% | +1% | -2% | -1% | +4% | +1% | -5% | +5% | +0% | -5% | 4 | 36 |
| 46 | vixfix | grade |  | 1h ph0.95 str5 ob70 aggr u9 | -0% | -0% | +0% | +0% | +0% | +0% | +0% | +0% | +0% | -0% | 6 | 64 |
| 47 | 6 | bbrsi | 3. Bollinger Band with RSI (piramide 50 x 10% do capital) | 1h 20/60 bb2.5 u10 | -1% | -0% | +0% | +1% | +0% | -1% | +1% | +0% | +0% | -1% | 5 | 77 |
