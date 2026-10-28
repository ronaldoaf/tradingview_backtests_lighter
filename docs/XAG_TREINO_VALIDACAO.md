# XAG (prata): treino / validação / OOS

Dados: Dukascopy XAG-USD BID 1m (`data/xag_1m_dl.py`), 2017-09-01 a 2026-10-04, 3,16M barras, mesmo período do XAU. Custo e funding da Lighter ainda não medidos para prata: usados os do ouro (0,75 bp por perna, 13,8%/ano).

Período em 10 partes iguais: 1–6 treino (até 2023-02-14), 7–9 validação (até 2025-11-06), 10 OOS (não lido). B&H XAG na validação: +120,6%.

Mesmo método do XAU (`ATIVO=xag bash scripts/run_full.sh` e `ATIVO=xag python scripts/tvo.py`). 19.249 células; aprovadas no treino: 189 estratégias.

| K | Teto | Peso | Corr média | Treino | Sharpe treino | Validação | Sharpe val | DD val | Estratégias |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 0.2 | igual | -0.03 | +295,6% | 2.15 | +10,6% | 0.43 | -10,7% | rsirev macdre atr kbb std es |
| 6 | 0.2 | inv_vol | -0.03 | +277,4% | 2.28 | +3,5% | 0.18 | -13,2% | rsirev macdre atr kbb std es |
| 6 | 0.3 | igual | -0.01 | +357,3% | 2.22 | +62,5% | 1.96 | -5,4% | rsirev macdre atr stdbf kbb evw |
| 6 | 0.3 | inv_vol | -0.01 | +352,9% | 2.40 | +62,2% | 1.96 | -5,6% | rsirev macdre atr stdbf kbb evw |
| 6 | 0.4 | igual | -0.01 | +366,7% | 2.30 | +51,7% | 1.66 | -4,6% | rsirev macdre atr stdbf vf kbb |
| 6 | 0.4 | inv_vol | -0.01 | +362,5% | 2.45 | +50,4% | 1.59 | -5,4% | rsirev macdre atr stdbf vf kbb |
| 6 | 0.5 | igual | 0.03 | +345,1% | 2.34 | +34,6% | 1.05 | -8,4% | rsirev macdre atr stdbf vf apsar |
| 6 | 0.5 | inv_vol | 0.03 | +343,5% | 2.31 | +35,3% | 1.06 | -8,6% | rsirev macdre atr stdbf vf apsar |
| 8 | 0.2 | igual | -0.02 | +237,5% | 2.42 | +12,5% | 0.55 | -9,3% | rsirev macdre atr kbb std es obv xscalp |
| 8 | 0.2 | inv_vol | -0.02 | +207,9% | 2.48 | +6,2% | 0.30 | -12,4% | rsirev macdre atr kbb std es obv xscalp |
| 8 | 0.3 | igual | 0.02 | +333,5% | 2.27 | +28,0% | 1.14 | -7,0% | rsirev macdre atr stdbf kbb evw htsi acr |
| 8 | 0.3 | inv_vol | 0.02 | +330,7% | 2.44 | +28,0% | 1.16 | -4,7% | rsirev macdre atr stdbf kbb evw htsi acr |
| 8 | 0.4 | igual | 0.04 | +339,5% | 2.26 | +28,1% | 1.14 | -4,8% | rsirev macdre atr stdbf vf kbb evw htsi |
| 8 | 0.4 | inv_vol | 0.04 | +335,3% | 2.35 | +27,9% | 1.08 | -5,6% | rsirev macdre atr stdbf vf kbb evw htsi |
| 8 | 0.5 | igual | 0.05 | +348,3% | 2.35 | +34,3% | 1.14 | -7,0% | rsirev macdre atr stdbf vf apsar hhll kbb |
| 8 | 0.5 | inv_vol | 0.05 | +343,0% | 2.36 | +32,6% | 1.06 | -6,2% | rsirev macdre atr stdbf vf apsar hhll kbb |
| 10 | 0.2 | igual | -0.01 | +199,9% | 2.57 | +4,4% | 0.26 | -9,9% | rsirev macdre atr kbb std es obv xscalp tq tlb |
| 10 | 0.2 | inv_vol | -0.01 | +164,6% | 2.61 | -3,4% | -0.15 | -12,8% | rsirev macdre atr kbb std es obv xscalp tq tlb |
| 10 | 0.3 | igual | 0.02 | +292,6% | 2.41 | +13,4% | 0.65 | -9,5% | rsirev macdre atr stdbf kbb evw htsi acr sr es |
| 10 | 0.3 | inv_vol | 0.02 | +282,1% | 2.56 | +10,6% | 0.53 | -8,5% | rsirev macdre atr stdbf kbb evw htsi acr sr es |
| 10 | 0.4 | igual | 0.06 | +323,6% | 2.30 | +24,1% | 0.98 | -10,4% | rsirev macdre atr stdbf vf kbb evw htsi mtl gso |
| 10 | 0.4 | inv_vol | 0.06 | +319,9% | 2.33 | +24,1% | 0.95 | -8,9% | rsirev macdre atr stdbf vf kbb evw htsi mtl gso |
| 10 | 0.5 | igual | 0.06 | +331,4% | 2.43 | +14,8% | 0.60 | -10,3% | rsirev macdre atr stdbf vf apsar hhll kbb htsi mtl |
| 10 | 0.5 | inv_vol | 0.06 | +326,6% | 2.39 | +13,9% | 0.55 | -9,5% | rsirev macdre atr stdbf vf apsar hhll kbb htsi mtl |
| 12 | 0.2 | igual | -0.01 | +172,3% | 2.80 | +8,2% | 0.51 | -7,0% | rsirev macdre atr kbb std es obv xscalp tq tlb opw hulk |
| 12 | 0.2 | inv_vol | -0.01 | +129,9% | 2.98 | +5,3% | 0.39 | -7,1% | rsirev macdre atr kbb std es obv xscalp tq tlb opw hulk |
| 12 | 0.3 | igual | 0.02 | +259,3% | 2.48 | +6,4% | 0.38 | -9,7% | rsirev macdre atr stdbf kbb evw htsi acr sr es hap hs |
| 12 | 0.3 | inv_vol | 0.02 | +246,6% | 2.62 | +4,1% | 0.26 | -9,2% | rsirev macdre atr stdbf kbb evw htsi acr sr es hap hs |
| 12 | 0.4 | igual | 0.06 | +311,9% | 2.45 | +24,1% | 1.00 | -11,3% | rsirev macdre atr stdbf vf kbb evw htsi mtl gso acr irs |
| 12 | 0.4 | inv_vol | 0.06 | +308,5% | 2.47 | +24,1% | 0.99 | -9,9% | rsirev macdre atr stdbf vf kbb evw htsi mtl gso acr irs |
| 12 | 0.5 | igual | 0.06 | +320,2% | 2.46 | +14,3% | 0.62 | -14,3% | rsirev macdre atr stdbf vf apsar hhll kbb htsi mtl gso acr |
| 12 | 0.5 | inv_vol | 0.06 | +317,1% | 2.46 | +13,7% | 0.59 | -13,2% | rsirev macdre atr stdbf vf apsar hhll kbb htsi mtl gso acr |

## Aprovadas no treino (top 40)

| # | Lote | Est | Nome | Célula | Geo | Partes + | Trades |
|---|---|---|---|---|---|---|---|
| 1 | 20 | rsirev |  | 4h 8 1.5 normal ambos | +27,4% | 5/6 | 496 |
| 2 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 4h HULL 12/26/9 | +26,3% | 5/6 | 2430 |
| 3 | 36 | atr | 17. ATR Reversed | 30min 14/2 ambos | +25,2% | 5/6 | 5095 |
| 4 | 32 | stdbf | 2. Super Trend Daily BF | 1h m2.6 ambos | +24,0% | 4/6 | 107 |
| 5 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR20 p1.0 c0.005 | +23,5% | 4/6 | 670 |
| 6 | 29 | vf | 19. Volume fight | 30min ma30 ambos | +22,9% | 4/6 | 1841 |
| 7 | 22 | apsar | 7. ATR Parabolic SAR | 30min n3 0.02/0.2 ambos | +22,3% | 4/6 | 2362 |
| 8 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 30min 50 rev ambos | +21,9% | 4/6 | 519 |
| 9 | 36 | kbb | 2. Kozlod BB | 4h bb55x2 ambos | +21,2% | 5/6 | 156 |
| 10 | 34 | khw | 10. Kahlman HullMA / WT Cross | 1h h48 sem wt ambos | +21,1% | 4/6 | 2973 |
| 11 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 1h n30 12/26 ambos | +20,7% | 4/6 | 1665 |
| 12 | 10 | mab | 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao) | 15min bb 50/200 ambos | +20,6% | 5/6 | 5187 |
| 13 | 17 | htsi | 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7) | 1D 50/50/7 ambos | +20,3% | 5/6 | 139 |
| 14 | 11 | easy | 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT) | 1h e10 st1.5 zig0 ambos | +20,2% | 4/6 | 2808 |
| 15 | 34 | mtl | 2. Market Trend Levels | 4h 20/50 adx20 ambos | +20,0% | 5/6 | 113 |
| 16 | 30 | gso | 8. Gann Swing Oscillator | 4h l10 ambos | +19,8% | 5/6 | 279 |
| 17 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 1D trig1 sl0.06 ambos | +19,5% | 5/6 | 400 |
| 18 | 38 | rwp | 1. Robot Wealth Pairs (BB 20x2) | 15min z1.5 ambos | +19,4% | 5/6 | 11633 |
| 19 | 32 | irs | 6. Ichimoku Cloud with RSI (Coinrule) | 15min rsi50 ambos | +18,7% | 4/6 | 1999 |
| 20 | 20 | ds |  | 1h 8/72 ambos | +18,7% | 4/6 | 1766 |
| 21 | 27 | tch | 5. TSI CCI Hull | 30min p50 ambos | +18,6% | 4/6 | 1349 |
| 22 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 30min a5.0 atr30 hma2 ambos | +18,2% | 4/6 | 857 |
| 23 | 17 | grid | 2. Grid Like (linha-base, alvo/stop = point) | 30min p5.00% ambos | +17,8% | 6/6 | 331 |
| 24 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 15min lb10 pb5 tp2.0 sl2.0 | +17,4% | 5/6 | 1646 |
| 25 | 30 | mbf | 16. Momentum BF | 4h l18 ambos | +17,4% | 6/6 | 1424 |
| 26 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 1h so123 ambos | +17,3% | 5/6 | 602 |
| 27 | 25 | cmo | 6. CMO TradeDots | 15min 40 ambos | +17,3% | 5/6 | 2663 |
| 28 | 25 | mst | 11. Master Supertrend | 1h 60 m2 ambos | +17,2% | 4/6 | 870 |
| 29 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 15min l50 e40 ambos | +17,1% | 5/6 | 2069 |
| 30 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 15min sl0% tp35% filtros ambos | +17,0% | 4/6 | 886 |
| 31 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 4h 8/16/11 ambos | +16,7% | 4/6 | 1305 |
| 32 | 26 | pdb | 13. Previous Day High/Low Breakout | 4h hl ambos | +16,6% | 4/6 | 1263 |
| 33 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.05 roc2.0 m3.0/3.0 ambos | +15,9% | 5/6 | 544 |
| 34 | 25 | pop | 22. Pivot of Pivot Reversal | 15min 4/2 ambos | +15,9% | 5/6 | 1837 |
| 35 | 32 | stt | 16. SuperTrend Trapping Candle | 30min 0.6% ambos | +15,5% | 5/6 | 3634 |
| 36 | 26 | csq | 3. Crypto Squeeze | 1h mfi58 ambos | +15,0% | 4/6 | 575 |
| 37 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 1h f10 hl tp5.0 | +14,9% | 4/6 | 692 |
| 38 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 1h n55 ambos | +14,6% | 4/6 | 2613 |
| 39 | 18 | savwap | 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only) | 30min prd50 ambos | +14,3% | 4/6 | 1353 |
| 40 | 23 | twin | 1. Twin Range Filter | 1D sematr t17 sltp ambos | +14,1% | 4/6 | 199 |

## OOS (parte 10) da carteira K=6 teto 0,3

```
OOS 2025-11-07 a 2026-10-04; K=6 teto=0.3
peso igual: total -29.0% Sharpe -0.91 DD -36.1%
inverso da vol: total -16.6% Sharpe -0.55 DD -29.0%
B&H XAG: total +25.7% Sharpe 0.73 DD -52.8%

por estrategia (OOS):
macdre    +19.1%
rsirev    +12.4%
evw       -13.8%
atr       -19.0%
stdbf     -22.4%
kbb      -100.0%
```

kbb (Kozlod BB, 4h) zera na alta parabólica da prata em jan/2026: o retorno é sobre o nocional 1x e a posição vendida perdeu tudo.
