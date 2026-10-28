# US100 em 4 partes (seleção sem OOS)

Pedido de 2026-10-28: retestar no US100 todas as estratégias dos lotes com a grade curta de cada lote, dividindo os dados (M1 Dukascopy, 2017-01-05 a 2026-08-31) em 5 partes iguais no tempo. As 4 primeiras servem para selecionar; a 5ª (de 2024-09-25 em diante) é OOS e **nem é carregada** (`scripts/study_us100_4p.py` corta o M1 antes dela).

- Aprovada: pelo menos uma célula (TF × configuração) com lucro líquido composto > 0 em cada uma das 4 partes, com spread e funding de sempre. Trade conta na parte em que entra.
- Ordem: soma dos lucros das 4 partes da melhor célula aprovada. Variantes `peek` (lookahead de propósito) foram descartadas.
- B&H por parte: +35%, +77%, −7%, +79% (soma +184%). Só a parte 3 caiu, então quem é long a maior parte do tempo passa com facilidade.
- Não rerodadas (motores próprios, fora do padrão dos lotes): bbrsi, commas, flipma, goldtrail, ict2022, ictsuite, macdconf, macdsma, serdar, tlangle.

Resultado: **371 de 449** estratégias aprovadas. Tabela completa em `results/us100_4p/aprovadas.csv`; reproduzir com `for n in 3..38 flawless ichimoku rsidiv vixfix zigzagpa: python scripts/study_us100_4p.py n` e `python scripts/agg_us100_4p.py`.

| # | Lote | Est | Nome | Célula | P1 | P2 | P3 | P4 | Soma | Trades |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 28 | sbf | 1. Stochastic (BiznesFilosof) | 4h 20/80 ambos | +10% | +181% | +24% | +20% | +234% | 64 |
| 2 | 7 | tsl | 1. Trailing SL [QuantNomad] (4%, sempre no mercado) | 1h atr10x2.0 | +80% | +49% | +66% | +38% | +232% | 1773 |
| 3 | 7 | std | 2. Super Trend Daily 2.0 (stop 5%) | 1h sl0.0 roc0.0 m3.0/3.0 ambos | +83% | +20% | +81% | +38% | +221% | 1232 |
| 4 | 11 | hast | 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%) | 30min m4.0 normal tp0.03 sl0.01 | +110% | +35% | +45% | +28% | +218% | 1355 |
| 5 | 20 | cam |  | 15min sl1% tp2% ambos | +43% | +54% | +117% | +2% | +217% | 920 |
| 6 | 34 | zlm | 6. Zero-Lag MA Trend Following | 30min rr4 ambos | +46% | +25% | +108% | +29% | +208% | 998 |
| 7 | 20 | mrb |  | 1h 80 g2 m2 lower-atr ambos | +50% | +59% | +27% | +72% | +207% | 659 |
| 8 | 24 | stb | 5. SuperTrend Backtester | 30min tp3% ambos | +86% | +8% | +101% | +12% | +206% | 2027 |
| 9 | 28 | pmax | 8. PMax | 30min m3 ambos | +62% | +32% | +71% | +35% | +200% | 911 |
| 10 | 32 | qst | 8. QuantNomad SuperTrend | 4h m2 ambos | +60% | +48% | +66% | +19% | +192% | 534 |
| 11 | 13 | scalp | 2. Scalping Trading System (SMA25/EMA200, Keltner, MACD 4/34, Stoch 10) | 15min s25 e0 ambos | +1% | +118% | +26% | +46% | +192% | 2992 |
| 12 | 36 | vst | 3. Multi-Step Vegas SuperTrend | 1h b2 ambos | +58% | +58% | +41% | +32% | +190% | 1602 |
| 13 | 36 | at3 | 16. ATR and T3 | 30min p5 ambos | +83% | +27% | +49% | +30% | +188% | 1146 |
| 14 | 8 | eng | 4. Engulfing + SMA32 | 30min ma128 sl0.005 tp0.05 ambos | +59% | +25% | +78% | +23% | +185% | 1550 |
| 15 | 30 | mma | 3. Multi-MA | 15min l150 ambos | +42% | +14% | +91% | +36% | +183% | 904 |
| 16 | 28 | gvto | 9. Golden Vector Trend Orchestrator | 30min adx0 ambos | +54% | +23% | +75% | +31% | +183% | 1209 |
| 17 | 20 | ypmax |  | 1h 13 2 ambos | +41% | +45% | +73% | +23% | +181% | 1169 |
| 18 | 27 | sqr | 11. Squeeze Momentum on Reversal | 4h f0.0018 ambos | +2% | +1% | +142% | +36% | +181% | 384 |
| 19 | 9 | rsma | 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado) | 15min r30 m34 tend ambos | +35% | +60% | +36% | +46% | +177% | 1572 |
| 20 | 29 | ged | 7. PTS Golden Edge | 1h 9/50 ambos | +50% | +42% | +40% | +42% | +175% | 441 |
| 21 | 22 | mab | 11. Moving Average Band | 30min 100 rr0 ambos | +60% | +22% | +74% | +18% | +174% | 1416 |
| 22 | 8 | bbb | 5. BB Breakout (SMA55 +- 1 desvio) | 30min len100 m0.5 ambos | +52% | +3% | +81% | +36% | +172% | 972 |
| 23 | 24 | vws | 16. VWMA/SMA 3Commas | 4h semniveis long | +13% | +106% | +8% | +44% | +171% | 354 |
| 24 | 6 | sttsl | 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default) | 30min LONG p10 m4.0 sl3.0 | +49% | +55% | +18% | +48% | +171% | 680 |
| 25 | 25 | dax | 10. DAX Shooter | 1h adx20 ambos | +37% | +4% | +35% | +94% | +171% | 235 |
| 26 | 25 | bas | 45. BEST ATR Stop Multiple | 30min atr2 ambos | +30% | +62% | +66% | +13% | +170% | 1686 |
| 27 | 25 | bts | 27. BEST Trailing Stop | 30min tr3% ambos | +30% | +66% | +54% | +19% | +170% | 1685 |
| 28 | 36 | kel | 12. Keltner SL/TP | 1h k1/sl5 ambos | +54% | +23% | +55% | +37% | +169% | 1284 |
| 29 | 25 | spym | 39. SPY Master | 4h ambos | +28% | +30% | +33% | +79% | +169% | 1176 |
| 30 | 3 | tott | 3. TOTT (VAR MA 40, 1%, twin 0,1%) | 15min VAR20 p0.5 c0.001 | +43% | +45% | +25% | +52% | +165% | 794 |
| 31 | vixfix | grade |  | 1h ph0.85 str5 ob90 ambos u1 | +3% | +83% | +19% | +59% | +165% | 176 |
| 32 | 36 | dch | 11. Donchian stop entries | 1h n20 ambos | +20% | +22% | +80% | +42% | +164% | 1190 |
| 33 | 14 | hull | 6. HullMA Strategy (HMA16 subindo/descendo) | 30min n100 ambos | +23% | +54% | +62% | +25% | +164% | 1966 |
| 34 | 29 | mrs | 17. MACD_RSI | 1h e20 ambos | +55% | +29% | +67% | +12% | +163% | 1634 |
| 35 | 16 | aivst | 3. AI Volume SuperTrend (10, 3; rotulo WMA20 vs WMA100 do ST) | 15min l10 f5 long | +36% | +51% | +15% | +59% | +162% | 629 |
| 36 | 27 | tch | 5. TSI CCI Hull | 15min p50 ambos | +21% | +39% | +96% | +4% | +160% | 1690 |
| 37 | 32 | gps | 9. Grant's PSAR (long-only) | 1h 0.013/0.2 | +23% | +73% | +34% | +28% | +159% | 521 |
| 38 | 20 | macd |  | 15min m4.0 tp5% filtro | +45% | +46% | +15% | +52% | +157% | 1023 |
| 39 | 38 | smx | 4. SMAcross-mvr | 30min 10/50 ambos | +40% | +22% | +53% | +41% | +157% | 1699 |
| 40 | 26 | vst | 2. Vegas SuperTrend Enhanced | 1h b2 ambos | +51% | +45% | +41% | +19% | +156% | 1712 |
| 41 | 31 | sha | 18. Smoothed Heiken Ashi (long-only) | 30min 20/20 | +28% | +67% | +3% | +56% | +155% | 850 |
| 42 | 31 | gx | 11. Golden X BF | 15min 20/100 ambos | +29% | +32% | +55% | +39% | +154% | 1663 |
| 43 | 28 | sma3 | 19. Tres medias (SMA 7/25/99) | 1h 7/25 ambos | +30% | +37% | +48% | +39% | +154% | 1585 |
| 44 | 9 | micu | 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips) | 1h sl0.02 tp0.05 trail1 sess0 long | +34% | +44% | +7% | +69% | +154% | 566 |
| 45 | 36 | btm | 4. Beat the market (filtro de vol) | 4h p80/w100 | +14% | +104% | +12% | +24% | +154% | 329 |
| 46 | 5 | pvb | 1. Price and Volume Breakout (60/60/200, so long) | 15min 20/200 x1 vol0 ls | +54% | +22% | +63% | +15% | +154% | 1803 |
| 47 | 8 | tm | 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY) | 1h sl0.02 rr2.0 eod1 filt0 ambos | +35% | +59% | +41% | +19% | +153% | 1819 |
| 48 | 24 | hst | 6. HMA50 + Supertrend | 1h h50 long | +36% | +46% | +32% | +37% | +151% | 699 |
| 49 | 10 | mab | 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao) | 30min ma 20/50 ambos | +4% | +96% | +4% | +47% | +151% | 1216 |
| 50 | 4 | tdh | 3. Trend Direction Helper (RISK 10, SMA 7/20) | 1h r0 7/20 so long | +28% | +74% | +10% | +39% | +151% | 949 |
| 51 | 21 | lsf | 13. Liquidity Sweep Filter (tendencia) | 30min 30 1 ambos | +38% | +16% | +45% | +52% | +151% | 924 |
| 52 | 34 | gtf | 1. Gradient Trend Filter | 15min l25 long | +27% | +60% | +10% | +52% | +150% | 921 |
| 53 | 37 | obv | 17. OBV Acumulacao/Distribuicao | 4h n20 | +37% | +79% | +9% | +24% | +149% | 372 |
| 54 | 12 | rsima | 5. Simple RSI-MA (SMA50 do RSI10 x 50) | 30min r10 m20 long | +29% | +65% | +6% | +50% | +149% | 885 |
| 55 | 23 | stv | 16. Super trend V | 15min m3 ambos | +40% | +44% | +62% | +4% | +149% | 768 |
| 56 | 20 | dai |  | 15min 4/3 long | +31% | +33% | +29% | +54% | +148% | 948 |
| 57 | 31 | lst | 13. LunaOwl SuperTrend 2 | 30min m4 ambos | +65% | +32% | +45% | +5% | +147% | 1340 |
| 58 | 25 | ht3 | 36. Swing HULL + T3 | 30min 100 sltp ambos | +43% | +44% | +37% | +23% | +147% | 1714 |
| 59 | 17 | ftsma | 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier) | 15min 5/20/200 ft ambos | +41% | +17% | +60% | +29% | +146% | 2455 |
| 60 | 9 | hull | 4. Hull Swing Trader (HMA 210 do open) | 15min p210 long | +23% | +66% | +15% | +42% | +146% | 1045 |
| 61 | 10 | piv | 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop) | 1h 8/1 so long | +35% | +50% | +22% | +38% | +146% | 761 |
| 62 | 3 | ut | 2. UT Bot Strategy (a x ATR(c), flip) | 30min a3.0 c21 | +71% | +49% | +11% | +14% | +146% | 2110 |
| 63 | 30 | gold | 4. MAster Gold | 1D 100/30 ambos | +12% | +66% | +20% | +48% | +146% | 14 |
| 64 | 4 | ppst | 2. Pivot Point SuperTrend (2, 3, 10) | 30min p2 f4.0 a10 so long | +34% | +43% | +9% | +59% | +145% | 488 |
| 65 | 24 | dcf | 9. Donchian free bot | 30min tp2.5% ambos | +56% | +22% | +61% | +6% | +144% | 5818 |
| 66 | 22 | tsi | 5. TSI CCI Hull | 15min tp0.0% ambos | +13% | +41% | +77% | +13% | +144% | 1630 |
| 67 | 25 | stma | 12. State-aware MA Cross (long-only) | 4h padrao | +11% | +44% | +10% | +79% | +144% | 451 |
| 68 | 16 | pmax | 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%) | 15min sl0% tp35% sofiltro0 ambos | +44% | +10% | +31% | +58% | +144% | 1184 |
| 69 | 5 | crypto | 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10) | 1D 21 24/52/18 obv0 ls | +34% | +12% | +47% | +51% | +144% | 13 |
| 70 | 21 | bbb | 11. Bollinger Bands Breakout | 30min bb40 semvol sl2% tp9% long | +17% | +65% | +9% | +51% | +143% | 507 |
| 71 | 37 | wmx | 15. WMX Williams Fractals | 4h o1 long | +3% | +37% | +46% | +57% | +143% | 625 |
| 72 | 19 | ut2 | 3. UT Bot v2 (ATR10 x 1) | 30min a20 m3 ambos | +69% | +47% | +8% | +19% | +143% | 2104 |
| 73 | 33 | stc | 10. SuperTrend chandelier 7/7 | 1h m3 long | +41% | +29% | +30% | +43% | +143% | 523 |
| 74 | 13 | ut | 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only) | 1h a3.0 atr11 hma2 long | +36% | +21% | +15% | +70% | +142% | 395 |
| 75 | 21 | cons | 3. MA Consecutive Up/Down | 30min n8 ma20 long | +34% | +44% | +12% | +51% | +142% | 752 |
| 76 | 36 | mbd | 20. MACD Short/Long TVIO | 1h sl5 ambos | +24% | +43% | +59% | +15% | +141% | 1154 |
| 77 | 23 | dema | 8. DEMA ATR | 4h tp6 long | +3% | +109% | +12% | +16% | +141% | 68 |
| 78 | 27 | wvs | 8. Volatility System (Wilder) | 30min arc3 ambos | +74% | +13% | +30% | +24% | +141% | 1704 |
| 79 | 34 | kmt | 5. Ichimoku Kumo Twist | 30min stop long | +17% | +61% | +1% | +62% | +141% | 714 |
| 80 | 21 | guppy | 19. Super Guppy | 30min long | +31% | +47% | +18% | +44% | +140% | 747 |
| 81 | 30 | ott | 10. Optimized Trend Tracker | 1h 1.4% long | +32% | +47% | +12% | +49% | +140% | 646 |
| 82 | 24 | lht | 14. Low-High Trend (long-only) | 4h tp8 | +35% | +61% | +29% | +15% | +139% | 19 |
| 83 | 37 | ckr | 2. Chande Kroll Stop | 30min n10/a3 | +46% | +19% | +28% | +45% | +139% | 1087 |
| 84 | 26 | kama | 10. KAMA Strategy (long-only) | 1h f0.5 atr3 | +44% | +42% | +8% | +46% | +139% | 954 |
| 85 | 30 | rbs | 19. RSI Buy and Sell (long-only) | 30min 70/30 | +21% | +30% | +31% | +58% | +139% | 304 |
| 86 | 17 | stcci | 1. Supertrend CCI (sinal do CCI28) | 30min cci100 ambos | +51% | +13% | +72% | +2% | +138% | 2727 |
| 87 | 25 | hyb | 17. Hybrid RSI + Breakout | 30min atr4 ambos | +27% | +7% | +68% | +36% | +138% | 1514 |
| 88 | 30 | rom | 9. RSI of MACD (long-only) | 1h x15 sem stop | +36% | +47% | +13% | +42% | +138% | 215 |
| 89 | 33 | pst | 8. Parabolic SAR stop entries | 30min af0.02 long | +12% | +54% | +34% | +37% | +137% | 1701 |
| 90 | 20 | fline |  | 30min 21 1.0 long | +38% | +30% | +26% | +43% | +137% | 781 |
| 91 | 30 | lin | 13. 2x Universelle Linien | 30min 21/50 long | +26% | +45% | +19% | +47% | +137% | 735 |
| 92 | 33 | vat | 4. VWMA with ATR stops (long-only) | 30min 3.5atr/33 | +39% | +41% | +5% | +51% | +136% | 749 |
| 93 | 3 | occ | 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x) | 30min hon SMMA8 x5 | +37% | +30% | +48% | +21% | +136% | 1727 |
| 94 | 31 | akt | 9. AK Trend ID (long-only) | 1h 8/21 | +31% | +50% | +8% | +46% | +135% | 739 |
| 95 | 15 | comb | 2. Combined Strategy (fita de EMAs + RSI + Stoch) | 30min so EMAs long | +29% | +59% | +9% | +38% | +135% | 525 |
| 96 | 16 | emax | 4. EMA Cross 10/20 | 30min 20/50 long | +26% | +58% | +15% | +36% | +134% | 569 |
| 97 | 34 | mtl | 2. Market Trend Levels | 30min 20/50 adx0 long | +26% | +58% | +15% | +36% | +134% | 569 |
| 98 | 17 | bz | 5. Band-Zigzag TrendFollower (BB20x2 grudenta) | 4h bb20 3 semlatest ambos | +29% | +48% | +23% | +34% | +134% | 16 |
| 99 | 28 | t3cci | 7. FX Sniper T3-CCI | 30min cci50 long | +24% | +51% | +9% | +50% | +134% | 1177 |
| 100 | 10 | pdiv | 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2) | 15min q1 m100 reg+hid sl0.01 long | +27% | +48% | +10% | +48% | +133% | 861 |
| 101 | 22 | pmax | 16. PMax on RSI w T3 | 30min m1.5 t8 long | +28% | +57% | +5% | +44% | +133% | 838 |
| 102 | 25 | era | 31. EMA Cross + RSI + ADX | 1h sl2% ambos | +18% | +34% | +55% | +26% | +133% | 740 |
| 103 | 14 | cs | 1. Crypto Scalper (PSAR + MACD + EMA60) | 15min e60 tp/sl sim2 ambos | +7% | +20% | +72% | +34% | +132% | 1043 |
| 104 | 26 | kha | 17. Kozlod Heikin-Ashi | 4h k1 ambos | +36% | +47% | +32% | +18% | +132% | 2233 |
| 105 | 37 | chk | 18. Chaloke System | 1h 9/15/24 long | +27% | +46% | +7% | +52% | +132% | 683 |
| 106 | 22 | emax | 2. EMA Crossover hl2 | 15min 20x5 long | +28% | +52% | +9% | +43% | +132% | 798 |
| 107 | 24 | ectp | 19. EMA Crossover with TP | 30min sl3% semtp ambos | +24% | +44% | +47% | +16% | +132% | 1139 |
| 108 | 11 | sce | 2. Strategy Code Example (EMA14x21 do open, stop 0,1% alvo 0,5%) | 30min 9/50 sl0.02 tp0.1 long | +26% | +50% | +12% | +43% | +131% | 849 |
| 109 | 32 | dcs | 10. Donchian Channel (stop + EMA200) | 1h d20 long | +22% | +48% | +14% | +47% | +131% | 494 |
| 110 | 18 | tdi | 1. Traders Dynamic Index (forca 1-2) | 1h str1 long | +20% | +57% | +11% | +43% | +130% | 700 |
| 111 | 26 | sts | 5. SuperTrend STRATEGY | 30min m8.5 long | +29% | +34% | +8% | +59% | +130% | 360 |
| 112 | 26 | qc | 8. QuantCat Intraday | 15min atr4 ambos | +40% | +1% | +51% | +38% | +130% | 1808 |
| 113 | 32 | fis | 15. Fisher Transform (Ehlers) | 1h l20 long | +23% | +49% | +19% | +39% | +130% | 771 |
| 114 | 22 | force | 17. Force trade scalper | 30min 5/50 long | +40% | +43% | +12% | +35% | +130% | 469 |
| 115 | 29 | lrcb | 12. Linear Regression Channel Breakout | 4h dv1.5 long | +53% | +58% | +9% | +9% | +130% | 13 |
| 116 | 36 | rs2 | 10. RSI 2 + tendencia, trailing | 15min ts1 ambos | +15% | +30% | +58% | +27% | +130% | 1996 |
| 117 | 37 | lag | 1. Laguerre RSI | 30min a0.2 long | +31% | +51% | +2% | +45% | +129% | 1078 |
| 118 | 24 | d3 | 13. DEMA 8/20/63 | 1h x1 long | +36% | +40% | +11% | +42% | +129% | 628 |
| 119 | 37 | qts | 14. Quantitative Trend (pivo) | 15min tp2/sl1.75 | +39% | +29% | +6% | +55% | +129% | 688 |
| 120 | 32 | prv | 4. SuperTrend Enhanced Pivot Reversal | 15min f2.618 long | +24% | +22% | +38% | +45% | +129% | 1134 |
| 121 | 24 | alpha | 20. AlphaTrend | 30min rsi long | +39% | +34% | +6% | +50% | +129% | 944 |
| 122 | 11 | easy | 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT) | 1h e15 st3.0 zig1 long | +44% | +15% | +25% | +44% | +129% | 598 |
| 123 | 14 | drsi | 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9) | 1h r21 w100 d3 zero long | +11% | +48% | +15% | +55% | +129% | 562 |
| 124 | 25 | c123r | 18. Combo 123 Reversal + RSI | 30min long | +28% | +45% | +19% | +36% | +129% | 475 |
| 125 | 26 | ksr | 9. KSR (EMA 10/20) | 30min 20/50 ambos | +24% | +45% | +45% | +15% | +128% | 1139 |
| 126 | 21 | atrs | 7. ATR Strategy (5 x 3,5) | 1h a5 m3.5 long | +35% | +30% | +27% | +36% | +128% | 479 |
| 127 | 29 | kamatd | 8. KAMA TradeDots | 15min r10 long | +32% | +46% | +7% | +42% | +128% | 736 |
| 128 | 37 | dmm | 6. DMI Modified | 1h n9 long | +19% | +44% | +11% | +53% | +128% | 588 |
| 129 | 29 | atsl | 1. ATR Trailing Stoploss | 1h m2.5 ambos | +65% | +23% | +17% | +23% | +127% | 3473 |
| 130 | 15 | tmfs | 3. TMFS (rompimento de LT + media de 3 SuperTrends) | 30min sw20 sl8atr tp3% ambos | +23% | +25% | +78% | +2% | +127% | 1210 |
| 131 | 27 | atrts | 15. ATR Trailing Stops | 1h a5x3.5 long | +34% | +30% | +27% | +36% | +127% | 478 |
| 132 | 35 | lpr | 1. Linear Regression Pearson | 30min k120 sempre ambos | +23% | +26% | +6% | +72% | +127% | 1534 |
| 133 | 19 | 3ema | 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only) | 1h tp0 sl2 | +33% | +58% | +7% | +29% | +127% | 295 |
| 134 | 27 | bbbo | 9. Bollinger Band Breakout (long-only) | 1h m1.5 lower | +23% | +28% | +31% | +45% | +126% | 607 |
| 135 | 22 | crsi | 19. Cumulative RSI (long-only) | 1D 20/94 | +24% | +71% | +4% | +27% | +126% | 10 |
| 136 | 25 | imct | 16. Ichimoku + MACD/CMF/TSI | 15min long | +31% | +53% | +10% | +32% | +126% | 833 |
| 137 | 25 | pop | 22. Pivot of Pivot Reversal | 1D 4/2 ambos | +26% | +52% | +18% | +30% | +126% | 10 |
| 138 | 32 | hme | 5. HMA 200 + EMA 20 | 1h hma100 long | +15% | +45% | +9% | +56% | +125% | 509 |
| 139 | 14 | hap | 2. Heikin-Ashi PSAR [QuantNomad] | 1h 0.01/0.01/0.1 long | +21% | +56% | +3% | +46% | +125% | 738 |
| 140 | 18 | slope | 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200) | 1h 130 9/21 semfiltro long | +35% | +39% | +16% | +34% | +124% | 807 |
| 141 | 20 | qfl |  | 30min 0.5% tp3% semstop age10 | +26% | +54% | +22% | +21% | +124% | 44 |
| 142 | 34 | mls | 8. ML SuperTrend kNN | 30min f2.94 tp2.2 ambos | +73% | +2% | +27% | +21% | +123% | 2540 |
| 143 | 28 | hvc | 14. Hull MA vs Candle | 4h h100 long | +12% | +69% | +3% | +39% | +123% | 159 |
| 144 | 22 | slopes | 10. Slopes | 1h 130/400 semfiltro long | +30% | +37% | +21% | +35% | +123% | 530 |
| 145 | 7 | srt | 5. SR TREND (21) | 1h len100 so long | +21% | +41% | +32% | +29% | +123% | 414 |
| 146 | 22 | apsar | 7. ATR Parabolic SAR | 1D n3 0.02/0.2 long | +4% | +58% | +9% | +51% | +122% | 22 |
| 147 | 25 | elo | 20. EMA Long Only | 1h 50 | +24% | +51% | +14% | +32% | +122% | 340 |
| 148 | 21 | sqz | 2. Squeeze Momentum | 4h l2 sl0.0% tp0% semsqz long | +7% | +23% | +33% | +59% | +122% | 223 |
| 149 | 24 | sott | 1. SOTT | 30min s50 p0.618 long | +22% | +36% | +3% | +61% | +122% | 564 |
| 150 | 11 | evw | 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado) | 30min n100 5/20 long | +32% | +35% | +17% | +38% | +121% | 1032 |
| 151 | 25 | ao | 49. Awesome Oscillator | 4h long | +16% | +54% | +4% | +47% | +121% | 767 |
| 152 | 36 | c123 | 5. Combo 123 Reversal & N Bars Down | 30min so123 long | +40% | +34% | +10% | +38% | +121% | 490 |
| 153 | 20 | nw |  | 4h 8 x10 long | +28% | +21% | +37% | +35% | +121% | 420 |
| 154 | 33 | haw | 2. Abdoli's Heikin Ashi Smoothed (long-only) | 1h ema30/3velas | +27% | +44% | +2% | +47% | +121% | 574 |
| 155 | 25 | uhl | 35. Uhl MA System | 30min 100 long | +33% | +29% | +12% | +46% | +121% | 305 |
| 156 | 25 | made | 4. MA Displaced Envelope + ATRTS | 1D 9 long | +1% | +86% | +12% | +22% | +120% | 41 |
| 157 | 33 | vxe | 18. VWAP X EMA | 1h ema50 long | +30% | +35% | +19% | +35% | +120% | 747 |
| 158 | 28 | gch | 18. Gaussian Channel | 30min p144 ambos | +30% | +22% | +34% | +33% | +120% | 2725 |
| 159 | 23 | ttm | 18. Trend Trader + MACD | 1h m3 semmacd long | +36% | +28% | +5% | +50% | +120% | 1180 |
| 160 | 25 | thma | 9. Triangular Hull MA | 15min 100 long | +20% | +58% | +10% | +32% | +119% | 1032 |
| 161 | 37 | hul | 7. Hull Suite | 1h n55 long | +24% | +43% | +16% | +36% | +119% | 782 |
| 162 | 20 | ceyhun |  | 1h m2 3 long | +37% | +19% | +23% | +38% | +118% | 557 |
| 163 | 31 | psw | 8. Swing Parabolic SAR | 4h af0.01 long | +27% | +23% | +24% | +43% | +118% | 280 |
| 164 | 16 | qqe | 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao) | 1h XZ f5 semfil ambos | +17% | +15% | +45% | +41% | +118% | 1176 |
| 165 | 16 | edma | 5. EDMA Scalping (EMA20 x EDMA20) | 15min l50 e40 long | +18% | +32% | +26% | +41% | +118% | 674 |
| 166 | 28 | bbw | 15. Bollinger Breakout (long-only, stop) | 30min bb50 8% | +19% | +42% | +20% | +37% | +118% | 518 |
| 167 | 34 | fmv | 4. FlexiMA Variance Tracker | 30min f8 long | +40% | +17% | +19% | +41% | +117% | 907 |
| 168 | 25 | htf | 5. Hull MA TimeFrame CrossOver | 30min 1000 s14 long | +10% | +44% | +17% | +46% | +117% | 28 |
| 169 | 24 | tq | 4. Triple EMA + QQE | 1h p3% long | +37% | +48% | +17% | +15% | +117% | 108 |
| 170 | 23 | zzrsi | 13. ZigZag RSI (long-only) | 4h r5 25/75 zz1 | +4% | +80% | +8% | +25% | +117% | 31 |
| 171 | 27 | atf | 2. Adaptive Trend Flow | 4h filtros long | +21% | +40% | +14% | +42% | +117% | 525 |
| 172 | 3 | macdre | 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma) | 15min VAR 24/52/18 | +52% | +11% | +38% | +16% | +116% | 2742 |
| 173 | 25 | mst | 11. Master Supertrend | 1h 20 m2 long | +36% | +24% | +0% | +55% | +116% | 698 |
| 174 | 27 | flash | 7. The Flash | 1h mr50 long | +39% | +26% | +17% | +34% | +116% | 421 |
| 175 | 19 | hhll | 2. HHLL (BB 29 + meia largura, reverse) | 30min 20 rev ambos | +7% | +57% | +22% | +29% | +115% | 1092 |
| 176 | 29 | adxb | 15. Rob Booker ADX Breakout | 1D adx25 long | +9% | +44% | +26% | +37% | +115% | 25 |
| 177 | 33 | ers | 13. EMA + RSI Sniper (long-only) | 4h tp9.6/sl3 | +1% | +73% | +19% | +22% | +115% | 160 |
| 178 | 38 | tsl | 3. Trailing Stop Loss (SMA 21/49) | 15min 50/200 tsl7.5 | +15% | +45% | +0% | +55% | +115% | 374 |
| 179 | 30 | gso | 8. Gann Swing Oscillator | 1h l10 long | +13% | +41% | +21% | +40% | +114% | 396 |
| 180 | 37 | hle | 11. HL MovingAvg2Line Cross | 1h n21 long | +34% | +31% | +12% | +36% | +114% | 946 |
| 181 | 9 | ut | 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R) | 4h k1.0 sl1.5 be0.75 tp0.0 ema200 ambos | +19% | +41% | +26% | +27% | +114% | 167 |
| 182 | 15 | sbs | 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15) | 4h sl1.00% 24h ambos | +31% | +17% | +46% | +19% | +113% | 1037 |
| 183 | 25 | mas | 23. Mov Avg Speed (3 sinais) | 4h long | +1% | +66% | +17% | +28% | +113% | 194 |
| 184 | 30 | scl | 17. 1 min forex scalping | 30min x1 long | +33% | +32% | +14% | +34% | +113% | 625 |
| 185 | 20 | kelt |  | 1h 40 2.0 tp6% sl2% semtend | +33% | +32% | +22% | +26% | +112% | 228 |
| 186 | 30 | hul | 1. Hull MA and Candle cross | 1h z100 long | +23% | +40% | +13% | +36% | +112% | 1026 |
| 187 | 33 | pac | 1. PSAR + ADX + CMF + RSI (long-only) | 1h rsi14/cmf20 | +22% | +40% | +3% | +47% | +112% | 332 |
| 188 | 29 | bbf | 16. Bull and Bear Fear | 1h n30 ambos | +19% | +28% | +37% | +28% | +112% | 1371 |
| 189 | 19 | abcd | 1. ABCD Pattern (fractais BW, TP/SL 5:1) | 1h sl1.0% rr5 long | +15% | +30% | +4% | +64% | +112% | 199 |
| 190 | 25 | gn | 41. Gianno Nano | 30min semsltp ambos | +31% | +24% | +34% | +22% | +111% | 1479 |
| 191 | 25 | mx | 32. Multi-X (long-only) | 1h padrao | +26% | +62% | +1% | +22% | +111% | 938 |
| 192 | 33 | ich | 20. Ichimoku + EMA filter | 1h sem ema long | +36% | +23% | +13% | +39% | +111% | 1187 |
| 193 | 22 | psarc | 14. Parabolic SAR on close | 1D n3 0.01/0.1 long | +12% | +53% | +10% | +36% | +110% | 44 |
| 194 | 23 | qqe | 7. UL QQE Cross | 4h thr5 semfiltro long | +27% | +50% | +2% | +32% | +110% | 354 |
| 195 | 25 | flexi | 7. FlexiSuperTrend | 30min f15 long | +28% | +29% | +26% | +28% | +110% | 492 |
| 196 | 26 | rsx | 12. RSI Crossover | 4h r14/9 long | +27% | +23% | +28% | +32% | +110% | 863 |
| 197 | 23 | ma1020 | 12. MA 10/20 Crossover | 15min 50/200 long | +15% | +39% | +0% | +55% | +109% | 374 |
| 198 | 37 | b4u | 8. IU 4 Bar UP | 30min f3 | +48% | +37% | +9% | +14% | +108% | 746 |
| 199 | 12 | tk | 1. TK Cross > EMA200 (20/60, long-only) | 4h 40/120 ema200 long | +2% | +64% | +14% | +28% | +108% | 38 |
| 200 | 5 | qqe |  | 1h b60 x30 s180 sw20 wae0 lucro0 | +28% | +20% | +53% | +6% | +108% | 1965 |
| 201 | 32 | cce | 12. CCI & EMA (Tradeswithashish) | 1h tp10% long | +22% | +35% | +20% | +31% | +108% | 335 |
| 202 | 29 | madx | 13. Crossing MAs + ADX | 15min adx0 ambos | +9% | +18% | +50% | +29% | +107% | 1452 |
| 203 | 32 | stt | 16. SuperTrend Trapping Candle | 30min 0.3% long | +18% | +31% | +9% | +49% | +107% | 1035 |
| 204 | 30 | tsh | 2. TrendShift Supertrend + ADX | 1h m3 long | +34% | +37% | +11% | +24% | +107% | 265 |
| 205 | 25 | sta | 38. Stoch + ATR | 4h 14 long | +30% | +13% | +10% | +54% | +107% | 303 |
| 206 | 23 | twin | 1. Twin Range Filter | 4h sematr t17 sltp ambos | +31% | +30% | +25% | +20% | +106% | 630 |
| 207 | 36 | cbo | 19. Candle Breakout 13h UTC | 1h h13/rr1 long | +28% | +25% | +13% | +39% | +106% | 781 |
| 208 | 29 | hlc | 2. High/Low channel swing | 4h l12 long | +27% | +31% | +1% | +46% | +105% | 514 |
| 209 | 30 | mmr | 7. Multiple MACD RSI | 1h 12/26 long | +8% | +43% | +16% | +39% | +105% | 555 |
| 210 | 22 | tdon | 9. Turtle Donchian/ATR | 1h 20/10 m2 long | +24% | +18% | +16% | +47% | +105% | 625 |
| 211 | 22 | renko | 12. Renko Strategy V2 | 1h atr10 long | +33% | +27% | +14% | +31% | +105% | 1307 |
| 212 | 29 | dbo | 3. Donchian Breakout (long-only) | 15min d55 lower | +31% | +14% | +17% | +44% | +105% | 731 |
| 213 | 22 | hhll | 13. Highest High / Lowest Low | 15min 55 long | +31% | +14% | +17% | +44% | +105% | 731 |
| 214 | 17 | grid | 2. Grid Like (linha-base, alvo/stop = point) | 15min p2.00% long | +15% | +56% | +11% | +22% | +105% | 441 |
| 215 | 26 | dm | 18. DEMA + MACD | 4h d21 long | +27% | +23% | +14% | +40% | +104% | 784 |
| 216 | 20 | ds |  | 30min 8/72 long | +26% | +16% | +20% | +42% | +104% | 1106 |
| 217 | 28 | sflip | 5. Bitcoin SuperFlip | 1h f3 long | +25% | +36% | +8% | +35% | +104% | 337 |
| 218 | 31 | cmb | 20. Combo 123 Reversal & Stochastic | 30min l14 ambos | +38% | +14% | +23% | +27% | +103% | 1465 |
| 219 | 32 | srs | 17. Supertrend + RSI (Alorse) | 1h f2 ambos | +55% | +26% | +2% | +19% | +102% | 1708 |
| 220 | 36 | lrb | 13. Linear Regression Channel Breakout | 1h n100 long | +24% | +25% | +14% | +38% | +101% | 1167 |
| 221 | 27 | stt | 4. Stochastic Trend (long-only) | 15min k50/25 x50 | +19% | +35% | +4% | +43% | +101% | 1084 |
| 222 | 28 | pab | 6. Price Action + Bollinger | 1h bb50 ambos | +38% | +27% | +35% | +0% | +101% | 138 |
| 223 | 22 | mrsi | 4. Easy MACD + RSI (long-only) | 1h rsi101 semstop | +12% | +34% | +4% | +51% | +101% | 363 |
| 224 | 27 | spk | 14. Martin Pring's Special K | 30min s30 long | +24% | +26% | +8% | +43% | +101% | 1180 |
| 225 | 26 | mel | 4. MACD + EMA (long-only) | 1h filtro 12/26 | +31% | +31% | +2% | +37% | +101% | 1069 |
| 226 | 6 | hs | 1. Hammers & Stars (stop 1 ATR, alvo 1R) | 1h s1.0 rr2.0 fib0.333 ema50 so long | +16% | +51% | +8% | +26% | +100% | 654 |
| 227 | 26 | mrr | 14. MACD, RSI & RVOL (long-only) | 1h 40/60 rv1.5/1.5 | +3% | +39% | +19% | +38% | +100% | 180 |
| 228 | 30 | mbf | 16. Momentum BF | 1h l36 long | +21% | +29% | +21% | +28% | +99% | 1116 |
| 229 | 31 | csc | 10. Crypto Price Scalper (long-only) | 15min cc60 st10% | +25% | +26% | +38% | +10% | +99% | 291 |
| 230 | 30 | dip | 15. Scalping Dips On Trend (long-only) | 1D d2 tp6% | +7% | +71% | +0% | +21% | +99% | 33 |
| 231 | 23 | bbst | 2. BBTrend + SuperTrend | 1h f7 long | +4% | +23% | +34% | +38% | +98% | 731 |
| 232 | 25 | ffe | 15. Forex Fractal EMA Scalper | 15min tp2.0% direto long | +19% | +49% | +6% | +25% | +98% | 991 |
| 233 | 24 | smc | 8. SMC | 30min lb30 long | +6% | +24% | +28% | +39% | +97% | 350 |
| 234 | 13 | ichi | 5. Ichimoku basico (9/26/52, deslocamento 26) | 15min 20/60/120 long | +20% | +29% | +11% | +37% | +96% | 507 |
| 235 | 25 | moon | 8. Moon Phases | 30min normal long | +42% | +17% | +6% | +31% | +96% | 95 |
| 236 | 25 | muta | 21. Mutanabby AI Algo Pro (long-only) | 4h semsl | +11% | +8% | +14% | +62% | +95% | 63 |
| 237 | 28 | stc | 12. SuperTrend Cloud | 1h m2.4/4.8 long | +21% | +18% | +17% | +38% | +94% | 542 |
| 238 | 31 | ttm | 2. TTM scalper | 1D inv long | +6% | +24% | +29% | +35% | +94% | 166 |
| 239 | 33 | hcx | 15. Hull MA Crossover | 1h h28 long | +11% | +46% | +7% | +30% | +93% | 1119 |
| 240 | 18 | savwap | 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only) | 4h prd100 long | +2% | +62% | +1% | +28% | +93% | 27 |
| 241 | 25 | sr | 3. Support Resistance | 15min 30 long | +26% | +22% | +5% | +41% | +93% | 918 |
| 242 | 28 | hapa | 10. Heikin Ashi Price Action | 4h velas long | +25% | +10% | +29% | +28% | +93% | 672 |
| 243 | 23 | rsipa | 17. RSI PrimeAutomation | 15min s4 tp0 long | +30% | +13% | +8% | +41% | +92% | 696 |
| 244 | 32 | tfp | 19. Trend Following Parabolic (TradeDots) | 15min rr1.3 long | +15% | +39% | +21% | +17% | +92% | 634 |
| 245 | 23 | hl41 | 4. Higher High Lower Low | 1h 41 long | +14% | +15% | +29% | +34% | +92% | 127 |
| 246 | 21 | hulk | 5. Hulk Scalper | 30min thr0.1 adx25 tp3.00% sl2.0% long | +16% | +59% | +3% | +14% | +92% | 152 |
| 247 | 34 | ppt | 3. Pivot Percentile Trend | 4h l20 long | +11% | +36% | +8% | +35% | +91% | 28 |
| 248 | rsidiv | rsidiv |  | 4h | +18% | +29% | +5% | +39% | +91% | 42 |
| 249 | 26 | hama | 11. NSDT HAMA (EMA55) | 1h e55 ambos | +20% | +12% | +46% | +13% | +90% | 1260 |
| 250 | 24 | beng | 18. Bullish Engulfing (long-only) | 15min sl2.00% tp2.00% semtend | +21% | +49% | +0% | +19% | +89% | 629 |
| 251 | 31 | mst | 6. MACD + Stochastic | 4h st14 long | +12% | +31% | +5% | +42% | +89% | 112 |
| 252 | 34 | ttl | 9. Turtle (uma unidade, long) | 1h 20/55/10/20 sem filtro | +27% | +31% | +3% | +27% | +89% | 831 |
| 253 | 33 | vct | 6. TASC 2024.08 VCTS (long-only) | 1h adx20/vp50 | +12% | +21% | +26% | +30% | +88% | 529 |
| 254 | 25 | fbo | 43. Fractal Breakout | 30min long | +30% | +33% | +1% | +25% | +88% | 1500 |
| 255 | 22 | xsc | 15. XAUUSD Scalping V2 | 1h tp0 sl0 ambos | +30% | +21% | +2% | +35% | +88% | 1977 |
| 256 | 20 | t3sar |  | 30min stop10 long | +11% | +31% | +32% | +13% | +87% | 793 |
| 257 | 31 | ich | 3. Advanced Ichimoku (long-only) | 15min ent all sai weak | +12% | +39% | +0% | +36% | +86% | 1709 |
| 258 | 6 | sr | 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true | 4h lb20 pb2 tp0.5 sl2.0 | +15% | +19% | +22% | +30% | +86% | 676 |
| 259 | 22 | tst | 18. Triple SuperTrend + StochRSI | 4h 20/80 rr2.0/1.5 long | +3% | +73% | +3% | +7% | +86% | 74 |
| 260 | 30 | ptr | 6. Percent Trailing Stop | 1h t5% ambos | +26% | +39% | +4% | +17% | +85% | 1907 |
| 261 | 28 | mab | 13. Moving Average (BiznesFilosof) | 4h sma21 ambos | +31% | +9% | +21% | +25% | +85% | 921 |
| 262 | 25 | kpl | 40. KPL Swing | 15min 50 long | +37% | +13% | +0% | +35% | +85% | 817 |
| 263 | 12 | acr | 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%) | 30min trig3 sl0.0 long | +8% | +28% | +19% | +29% | +85% | 42 |
| 264 | 22 | ichi | 8. Ichimoku no offset + RSI | 1D rsi50 ambos | +0% | +34% | +28% | +22% | +84% | 21 |
| 265 | 6 | bbrsi | 3. Bollinger Band with RSI (piramide 50 x 10% do capital) | 1D 35/80 bb1.5 u1 | +18% | +30% | +4% | +32% | +84% | 13 |
| 266 | 24 | hf | 12. Hull Fisher | 1h h50 long | +3% | +33% | +24% | +24% | +84% | 735 |
| 267 | 21 | bbao | 8. BB + AO (long-only) | 1D bb5 | +5% | +57% | +5% | +17% | +83% | 33 |
| 268 | 20 | madrid |  | 4h tp3% sl3% long | +15% | +37% | +10% | +21% | +83% | 124 |
| 269 | 32 | dkw | 14. Donchian Channels (KrisWaters) | 1h canal long | +25% | +9% | +24% | +25% | +82% | 1001 |
| 270 | 37 | c12r | 10. Combo 123 + Rainbow Oscillator | 4h ro5 long | +17% | +27% | +6% | +31% | +82% | 327 |
| 271 | 21 | surf | 1. Trend Surfers Breakout | 1h p55 t8.0 f2.0 long | +20% | +13% | +1% | +47% | +81% | 225 |
| 272 | 4 | aist |  | 15min 1h/4h f3.5/3.0 adx0 so long | +27% | +15% | +7% | +32% | +81% | 337 |
| 273 | 24 | btcm | 11. Bitcoin Momentum (long-only) | 4h atr1 | +25% | +18% | +2% | +37% | +81% | 519 |
| 274 | 25 | davin | 25. Davin 10/200 MA Pullback (long-only) | 1D dip14 sl15 | +1% | +45% | +7% | +27% | +80% | 57 |
| 275 | 34 | azl | 7. Adaptive Zero Lag EMA | 4h cos thr0.05 long | +23% | +7% | +25% | +26% | +80% | 425 |
| 276 | 32 | irs | 6. Ichimoku Cloud with RSI (Coinrule) | 15min sem rsi long | +24% | +30% | +3% | +22% | +79% | 1153 |
| 277 | 32 | koz | 20. Kozlod MA Cross | 1h 10/30 ambos | +1% | +25% | +5% | +48% | +78% | 1235 |
| 278 | 38 | kij | 2. Kijun-Sen DasanC | 1h n20 long | +20% | +27% | +6% | +25% | +77% | 1513 |
| 279 | 26 | bx | 6. B-Xtrender | 1h trl5% long | +28% | +22% | +6% | +22% | +77% | 903 |
| 280 | 26 | tcci | 20. Triple CCI + MFI (long-only) | 30min sl3 at2.25 | +18% | +26% | +23% | +11% | +77% | 714 |
| 281 | 27 | doji | 1. Doji strategy | 1D sl1% ambos | +2% | +25% | +20% | +28% | +76% | 51 |
| 282 | 26 | dma | 15. Dual Moving Average (angulo) | 1h a3 ambos | +4% | +29% | +7% | +35% | +76% | 1051 |
| 283 | 10 | wr | 4. Williams %R + MACD + SMA (1m) | 15min w140 -94/-6 sl0.0 contrario long | +20% | +13% | +7% | +36% | +75% | 185 |
| 284 | 22 | turtle | 6. Real Turtle (stops) | 1h 20/10 n4 long | +25% | +10% | +22% | +18% | +75% | 1008 |
| 285 | 29 | vf | 19. Volume fight | 1h ma11 ambos | +20% | +21% | +32% | +1% | +74% | 1959 |
| 286 | 20 | atrgod |  | 30min sl4.5 rr1.5 semfiltros long | +8% | +57% | +5% | +4% | +74% | 368 |
| 287 | 21 | gs | 9. Gold/Silver RSI + EMA162 | 4h corrigido ambos | +41% | +14% | +2% | +18% | +74% | 17 |
| 288 | 30 | kal | 12. KALKI TFXBOT | 30min rr3 long | +13% | +24% | +21% | +16% | +74% | 592 |
| 289 | 25 | mcci | 34. MACD + CCI | 4h long | +8% | +23% | +4% | +38% | +73% | 926 |
| 290 | 23 | coin | 6. Coinrule Scalping On Trend (long-only) | 1D 70/30 | +12% | +19% | +12% | +29% | +72% | 35 |
| 291 | 27 | ssl | 18. SSL Channel Cross | 30min l50 ambos | +38% | +12% | +5% | +18% | +72% | 2251 |
| 292 | 31 | pse | 17. Parabolic SAR w/ EMA | 30min off0% long | +22% | +19% | +19% | +11% | +71% | 1110 |
| 293 | 31 | vip | 19. VIP (long-only) | 1h tp3% sl1% | +15% | +18% | +12% | +27% | +71% | 121 |
| 294 | 32 | hic | 13. Hull MA_X + Ichimoku | 4h h12 long | +14% | +24% | +11% | +23% | +71% | 478 |
| 295 | 34 | khw | 10. Kahlman HullMA / WT Cross | 4h h48 sem wt long | +24% | +17% | +5% | +25% | +71% | 254 |
| 296 | 21 | msr | 18. MACD + Stoch + RSI (long-only) | 1h k50 | +14% | +19% | +8% | +29% | +70% | 1190 |
| 297 | 37 | tdw | 19. Gold TDOW (MACD+Stoch+RSI) | 1h todos | +14% | +19% | +8% | +29% | +70% | 1190 |
| 298 | 36 | mma | 15. Multi Moving Average Crossing | 30min 9/50/100 long | +11% | +9% | +10% | +39% | +70% | 336 |
| 299 | 7 | cap | 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h) | 15min r0.5 rr3.0 ret00 | +27% | +15% | +14% | +13% | +68% | 1446 |
| 300 | 27 | c2ac | 19. Combo 2/20 EMA + AC | 1h e50 long | +20% | +35% | +8% | +5% | +68% | 2147 |
| 301 | 26 | him | 7. Hull + Ichimoku + MACD | 4h h12 long | +17% | +25% | +2% | +24% | +68% | 314 |
| 302 | 25 | ce | 1. Chandelier Exit | 1h risco ambos | +34% | +2% | +13% | +18% | +67% | 1427 |
| 303 | 33 | r3 | 11. 3 RSI | 1h 30/70 long | +22% | +14% | +7% | +23% | +66% | 58 |
| 304 | 27 | e3 | 16. 3 EMA + Stoch RSI + ATR | 1h tp4 ambos | +23% | +8% | +14% | +20% | +66% | 2726 |
| 305 | 32 | usc | 3. Ultimate Scalping v2 (EMA + VWAP) | 1h tp3atr ambos | +15% | +16% | +27% | +7% | +66% | 1297 |
| 306 | 31 | seq | 7. Sequence Snap | 30min rr1.5 long | +8% | +38% | +6% | +14% | +65% | 463 |
| 307 | 25 | cmo | 6. CMO TradeDots | 4h 20 long | +6% | +25% | +8% | +24% | +64% | 169 |
| 308 | 23 | combo | 14. Combo 123 Reversal + SMI | 30min smi50 long | +12% | +20% | +2% | +30% | +64% | 517 |
| 309 | 27 | simp | 10. Simple strat (MACD + Stoch + RSI) | 1h tp6 sl2 long | +13% | +14% | +6% | +30% | +63% | 1334 |
| 310 | 27 | tfb | 12. Trend Following Breakout | 1h 20/10 long | +8% | +27% | +2% | +26% | +63% | 841 |
| 311 | 37 | dmx | 12. DMI + nuvem Ichimoku | 4h adx20 long | +4% | +20% | +2% | +37% | +62% | 556 |
| 312 | 32 | stdbf | 2. Super Trend Daily BF | 4h m2.6 long | +6% | +9% | +1% | +46% | +62% | 39 |
| 313 | 33 | dst | 17. Dual Supertrend with MACD | 1h 2/4 ambos | +19% | +0% | +21% | +21% | +62% | 1669 |
| 314 | 29 | bot | 14. BotBot | 30min k0.02 ambos | +7% | +6% | +13% | +36% | +61% | 33 |
| 315 | 10 | aio | 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR) | 15min rsi1 atr5.0 rr3.0 long | +11% | +32% | +1% | +18% | +61% | 439 |
| 316 | 30 | lsr | 18. LunaOwl suporte/resistencia | 30min lb50 long | +13% | +1% | +9% | +39% | +61% | 253 |
| 317 | 38 | rwp | 1. Robot Wealth Pairs (BB 20x2) | 4h z2 long | +9% | +6% | +11% | +35% | +61% | 176 |
| 318 | 20 | alli |  | 1h normal ambos | +10% | +20% | +11% | +19% | +60% | 2354 |
| 319 | 30 | rdi | 5. RSI Divergence x Ichimoku x 200EMA | 1D lb3 long | +14% | +25% | +0% | +19% | +58% | 11 |
| 320 | 25 | tlb | 42. Trendline Breakout KedArc | 1D p5 ma ambos | +1% | +40% | +11% | +6% | +58% | 20 |
| 321 | 20 | 3st |  | 15min pl3.0 thr30 long | +4% | +8% | +35% | +9% | +56% | 935 |
| 322 | 25 | sec | 30. Stoch/EMA Cross | 1D tp8% long | +5% | +17% | +8% | +25% | +55% | 11 |
| 323 | 14 | fm | 4. Forex Master v4.0 (BB20x1,5 + ADX fraco) | 1h bb20 2.0 sl2.0% tp2.0% long | +17% | +12% | +7% | +19% | +55% | 183 |
| 324 | 7 | hma | 4. Adaptive HMA+ (172-233, flat 17, meia zona) | 15min f25 one tp5.0 so long | +10% | +27% | +14% | +4% | +55% | 584 |
| 325 | 25 | drm | 13. Dynamic RSI Momentum | 1h 30/70 long | +24% | +22% | +3% | +5% | +54% | 61 |
| 326 | 18 | sweep | 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16) | 1h rr3.0 semvol sess ambos | +26% | +15% | +2% | +11% | +54% | 184 |
| 327 | 30 | stpb | 14. Supertrend pullback | 30min pull ambos | +14% | +33% | +1% | +5% | +53% | 412 |
| 328 | 29 | bsc | 5. Breakout Scalper | 15min 13/52 long | +22% | +13% | +14% | +3% | +52% | 1372 |
| 329 | 31 | mdb | 16. Market Dynamics HH/LL breakout | 4h lb26 long | +10% | +25% | +5% | +12% | +52% | 56 |
| 330 | 36 | sms | 9. Super Momentum | 30min cmo9 long | +0% | +13% | +11% | +28% | +52% | 166 |
| 331 | 32 | tss | 18. TSI w SuperTrend decision | 15min p32 long | +21% | +10% | +1% | +20% | +51% | 2506 |
| 332 | 25 | smp | 50. Smart Money Pivot | 15min p20 sl0% tp0.0% long | +13% | +7% | +3% | +27% | +51% | 616 |
| 333 | 24 | mbit | 3. Mbit MA (contrario) | 30min ma200 n10 long | +8% | +15% | +5% | +22% | +50% | 236 |
| 334 | 33 | bes | 16. Binary Option EMA/Stoch | 1D e4 long | +20% | +1% | +4% | +24% | +49% | 38 |
| 335 | 21 | mtfrsi | 20. Multi Timeframe RSI | 4h 1/4/16 40/60 long | +10% | +18% | +7% | +13% | +48% | 11 |
| 336 | 22 | bbra | 1. BB + RSI + ADX | 30min sl0.0% adx32 ambos | +28% | +10% | +1% | +10% | +48% | 359 |
| 337 | 33 | mcd | 14. MACD 8/16/11 (sinal SMA) | 1h 8/16/11 long | +27% | +3% | +7% | +11% | +48% | 1669 |
| 338 | 24 | best | 2. BEST Supertrend | 1h m1.5 long | +9% | +23% | +1% | +14% | +47% | 653 |
| 339 | 32 | rdv | 11. RSI Divergence Strategy | 30min rsi<35 ambos | +18% | +6% | +6% | +14% | +44% | 64 |
| 340 | 23 | crazy | 10. Crazy Scalping (TMO + AMA) | 30min sl30 ambos | +8% | +16% | +8% | +11% | +43% | 395 |
| 341 | 33 | bct | 3. Bar Counter Trend Reversal | 1D kc1 long | +14% | +15% | +0% | +13% | +42% | 27 |
| 342 | 30 | sich | 11. SuperIchi | 4h rr3 long | +8% | +20% | +9% | +4% | +41% | 51 |
| 343 | 20 | xscalp |  | 15min gap1.00% rr3 long | +4% | +20% | +15% | +1% | +39% | 147 |
| 344 | 37 | mdv | 3. MACD + DMI + Volatility Stop | 4h semtp | +8% | +5% | +6% | +19% | +39% | 154 |
| 345 | 33 | snr | 12. Signal To Noise | 30min l21 ambos | +22% | +1% | +2% | +12% | +38% | 3390 |
| 346 | 25 | opw | 37. TASC One Percent A Week (long-only) | 1D dip1 tp1 | +4% | +25% | +6% | +3% | +38% | 189 |
| 347 | 13 | sqz | 4. Squeeze Momentum [LazyBear] (BB14x2, KC16x1,5) | 1h bb14 kc16 long | +4% | +8% | +7% | +18% | +37% | 847 |
| 348 | 37 | sts | 9. 3x Supertrend + Stoch RSI | 30min tp4 long | +3% | +14% | +9% | +10% | +37% | 1024 |
| 349 | 21 | kb | 15. Keltner bounce (SMA200 +- 8 ATR) | 30min 200 d8 saimedia long | +6% | +21% | +6% | +4% | +37% | 127 |
| 350 | 25 | rtb | 47. Reversal Trading Bot | 1D sl3% tp6% long | +13% | +1% | +20% | +2% | +36% | 27 |
| 351 | 32 | hfl | 1. Hurst Future Lines of Demarcation | 30min c40 long | +2% | +15% | +10% | +8% | +34% | 890 |
| 352 | 36 | sqz | 18. Squeeze Momentum | 1h e50 ambos | +3% | +3% | +23% | +4% | +33% | 598 |
| 353 | 36 | pin | 6. Pinbar | 1D pm2 long | +14% | +11% | +7% | +1% | +33% | 44 |
| 354 | 11 | grab | 4. Grab Trading System (80/21) | 1D 80/21 stop0 so long | +10% | +6% | +1% | +11% | +29% | 19 |
| 355 | 36 | vrb | 14. Volatility Range Breakout | 15min n50 ambos | +12% | +8% | +0% | +8% | +28% | 1114 |
| 356 | 13 | fib | 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%) | 30min l200 m2.0 sl0.03 long | +7% | +8% | +12% | +0% | +27% | 183 |
| 357 | 29 | bbe9 | 6. Bollinger Bands + EMA 9 | 1D bb20 ambos | +4% | +14% | +4% | +2% | +25% | 84 |
| 358 | 21 | lube | 16. LUBE (atrito) | 30min 500 tl-0.1 long | +3% | +10% | +5% | +6% | +25% | 79 |
| 359 | 24 | gap | 10. Gap Filling | 15min semalvo long | +5% | +4% | +8% | +6% | +23% | 682 |
| 360 | 15 | es | 4. EMA STOCH (Crypto BOT lower timeframes) | 30min sl/tp3% ambos | +4% | +6% | +8% | +4% | +23% | 44 |
| 361 | 23 | e3r | 3. 3 EMA + RSI | 30min sl0% x0 long | +12% | +5% | +4% | +2% | +23% | 352 |
| 362 | 29 | cez | 4. Chandelier Exit + ZLSMA | 30min m2 long | +4% | +5% | +4% | +5% | +17% | 348 |
| 363 | 28 | l2r | 11. L2 Reversal Labels | 1h tpsl ambos | +3% | +9% | +4% | +0% | +16% | 151 |
| 364 | 37 | rvc | 13. Reversal Catcher | 4h bb1.5 ambos | +4% | +10% | +0% | +1% | +15% | 44 |
| 365 | 9 | ict | 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R) | 1h p5 rr5.0 trend0 ambos | +5% | +7% | +2% | +2% | +15% | 248 |
| 366 | 36 | sre | 1. Stoch RSI Crossover + EMA | 4h tp3/sl2 long | +7% | +3% | +1% | +2% | +14% | 21 |
| 367 | 21 | rbin | 17. RSI Binary (6, 13/82, 3 barras) | 4h 6 13/82 h3 long | +2% | +2% | +2% | +8% | +14% | 74 |
| 368 | 21 | mbr | 10. MACD + BB + RSI (long-only) | 15min semstop | +2% | +1% | +7% | +3% | +12% | 573 |
| 369 | 18 | osb | 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario) | 15min m0.5 sl0.25% ambos | +5% | +2% | +1% | +2% | +10% | 196 |
| 370 | 31 | lch | 5. Linear Channel (long-only) | 1h v2% hma200 | +1% | +1% | +7% | +1% | +9% | 17 |
| 371 | 12 | pt | 2. Powertrend (range filter de volume, 200, long-only) | 15min l400 m3.0 vol | +0% | +1% | +4% | +0% | +6% | 10 |
