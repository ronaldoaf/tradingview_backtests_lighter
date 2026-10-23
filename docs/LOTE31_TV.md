# Lote 31 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote31.py` (grade) e `scripts/study_tvlote31_rob.py` (robustez). Resultados: `results/study_tvlote31_{ativo}.txt`, `_grid.csv` e `results/study_tvlote31_rob_{ativo}.txt`. Mesma grade dos lotes anteriores: o padrão do script mais 4 combinações, em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (16):**
- **`security` em outro TF ou lookahead:** `EyqZ5jxf`, `N1WlPESB`, `ZrBjZveO`, `NP615SiK`, `gCbd29CF` e `Puprh5UJ` (template com `security` e lookahead).
- **Templates:** `Cd5vj6Wp`.
- **Sessão ou calendário:** `6Uf1wNAR` (também ticks), `wRVX66cb` (Londres/NY), `ZFATelK4` (filtro de calendário).
- **Pips ou ticks:** `8Q2g9IW1` (buffer em pips), `GJZHJwkA` (ticks, ordens limite e breakeven).
- **Piramidação ou TP parcial:** `o1YNgHYa` (TP parcial e sessões), `1wc9v4rw` (sessão e piramidação), `iImkk8VO`.
- **Complexa demais:** `5q6K1Suu` (regressão polinomial).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 364 | ALMA/EMA | `As3pijB6` | EMA49 cruzando acima da EMA9 com os dois closes anteriores acima da ALMA130 compra (espelho vende); StochRSI K cruzando abaixo de D acima de 92 fecha o long (espelho abaixo de 8); alvo 3% e stop 5,49%; inverte. |
| 365 | TTM scalper | `k79YeNBc` | Close subindo depois de recuo (gatilho de venda) e caindo depois de alta (gatilho de compra) alternam o estado; fica comprado no estado verde e vendido no vermelho (inv troca os lados). |
| 366 | Advanced Ichimoku (long-only) | `uycyVpIq` | So long: tenkan cruzando acima da kijun compra (todas, ou so a forte acima da nuvem deslocada); cruzamento para baixo com a tenkan acima da nuvem (fraco) fecha, ou qualquer cruzamento para baixo. |
| 367 | Heikin Ashi Wick (long-only) | `NWUYjOxI` | So long: candle HA verde com pavio superior compra; sem pavio superior ou pavio inferior maior fecha (src=candle usa o candle comum; ext=nowick so fecha sem pavio superior). |
| 368 | Linear Channel (long-only) | `loS16r1z` | So long: close 2% abaixo da regressao linear de 55 com a HMA400 abaixo do close compra; close acima da regressao fecha. |
| 369 | MACD + Stochastic | `sqDK1npx` | EMA8-EMA24 subindo com Stoch(7) D<25 e subindo compra; espelho (D>75 caindo) vende; inverte. |
| 370 | Sequence Snap | `49jNhJXM` | Candle de baixa seguido de 5 de alta (closes subindo com folga de 0,05% e minimas acima da do candle de baixa) com RSI14>40 subindo compra; stop na minima do candle de baixa, alvo 1,5R; so sem posicao (o short, espelho, vem desligado). |
| 371 | Swing Parabolic SAR | `Kf33o8g5` | Ordem stop no SAR previsto para a barra seguinte, do lado contrario a tendencia: sempre posicionado. So comprado: o stop de venda fecha o long. |
| 372 | AK Trend ID (long-only) | `ztKUkLYL` | So long: EMA3 acima da EMA8 compra, abaixo fecha. |
| 373 | Crypto Price Scalper (long-only) | `2Rx9y2VQ` | So long: posicao media do close no canal de 60 cruzando acima de zero, close acima da maxima de 2 barras atras e Vortex+ cruzando acima do Vortex- compra; o cruzamento inverso fecha; alvo e stop de 10%. |
| 374 | Golden X BF | `ob4p8rLf` | SMA50 cruzando a SMA200 compra/vende; inverte. |
| 375 | Tendency EMA + RSI | `X6K0ARDV` | EMA10 cruzando acima da EMA20 com EMA10>EMA100 e candle de alta compra; RSI>70 fecha, ou depois de 24 barras se o close estiver acima da abertura de entrada; espelho no short (desligado no original). |
| 376 | LunaOwl SuperTrend 2 | `eF9EN1ag` | Stop ATR(1) x 2,618 suavizado por RMA14, no estilo Chandelier sobre hl2 e close: comprado com a direcao de alta e o close acima do stop, vendido no espelho. |
| 377 | FXFUNDINGMATE Trend | `k0LMZo1H` | Stoch(5,3) cruzando acima de 20 com MACD>0, close acima da SMA100 e das duas linhas da nuvem deslocada compra (espelho em 80 vende); stop e alvo de 1 ATR8 a partir da entrada; a entrada contraria inverte. |
| 378 | OKX MA Crossover | `BeDjJdpx` | Minima abaixo da SMA13 anterior (e nao 2 barras antes) compra; maxima acima vende (vence quando os dois ocorrem); alvo e stop de 7% do close do sinal; inverte (a ordem limite no close virou mercado). |
| 379 | Market Dynamics HH/LL breakout | `xyov8Du1` | Close acima da maxima de 26 anterior (se ela for maior que a maxima de 10 anterior) compra, espelho vende; com os dois lados inverte; so comprado: fecha no sinal de venda, close 2% abaixo ou 7% acima da entrada. |
| 380 | Parabolic SAR w/ EMA | `6OEvKyvN` | Maxima rompendo o SAR (0,01/0,005/0,1) ou EMA100 cruzando abaixo da EMA10 com close acima do SAR, sempre com close 1% acima da EMA100, compra (espelho vende); o SAR tocado fecha a posicao. |
| 381 | Smoothed Heiken Ashi (long-only) | `4JDTWBH3` | So long: HA sobre EMAs de 10 de OHLC, com abertura e close HA suavizados por EMA10; virada para verde compra, para vermelho fecha. |
| 382 | VIP (long-only) | `4OYdIrWk` | So long: canal SSL (SMA200 das maximas/minimas) virando para cima, abertura suavizada subindo, EMA100 e maxima suavizada abaixo do meio do candle compra; alvo 1%; close abaixo da EMA100 arma um stop no close (ou no stop de 1% da entrada). |
| 383 | Combo 123 Reversal & Stochastic | `IYPg1Xjt` | 123 Reversal (Stoch 14/1/3, nivel 50) e Stochastic Crossover (7/3, 20/70) concordando dao a posicao; discordando zera. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (1 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Swing Parabolic SAR | 1h | af0.01 ambos | 2261 | +15.7% | +13.4% | 0.85 | 4.33 |

### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (19 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Linear Channel (long-only) | 15min | v2% hma200 | 76 | +10.8% | +5.4% | 5.43 | 8.35 |
| Linear Channel (long-only) | 15min | v2% hma400 | 104 | +11.5% | +5.4% | 4.21 | 7.78 |
| Linear Channel (long-only) | 30min | v2% hma200 | 87 | +5.7% | +5.4% | 1.65 | 2.44 |
| Linear Channel (long-only) | 30min | v2% hma400 | 128 | +6.8% | +5.4% | 1.55 | 2.43 |
| MACD + Stochastic | 4h | st14 ambos | 359 | +39.4% | +5.4% | 0.70 | 1.37 |
| Sequence Snap | 1h | rr1.5 ambos | 455 | +9.2% | +5.4% | 0.46 | 0.68 |
| MACD + Stochastic | 4h | st7 ambos | 234 | +23.8% | +5.4% | 0.46 | 0.48 |
| LunaOwl SuperTrend 2 | 1h | m2.618 ambos | 1888 | +19.7% | +5.4% | 0.38 | 1.25 |
| LunaOwl SuperTrend 2 | 30min | m4 ambos | 2096 | +16.3% | +5.4% | 0.31 | 0.98 |
| Golden X BF | 4h | 50/200 ambos | 77 | +14.1% | +5.4% | 0.29 | 1.05 |

### BTC (8 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Combo 123 Reversal & Stochastic | 1h | l14 long | 528 | +46.6% | +43.9% | 1.00 | 1.75 |
| Combo 123 Reversal & Stochastic | 1h | l14 ambos | 950 | +70.0% | +43.9% | 0.96 | 2.39 |
| Combo 123 Reversal & Stochastic | 1h | l28 ambos | 813 | +60.6% | +43.9% | 0.90 | 2.15 |
| Parabolic SAR w/ EMA | 30min | off0% ambos | 2950 | +55.0% | +43.9% | 0.70 | 2.54 |
| Golden X BF | 4h | 20/100 ambos | 187 | +53.4% | +43.7% | 0.59 | 1.62 |
| Swing Parabolic SAR | 1D | af0.01 ambos | 118 | +49.7% | +43.8% | 0.55 | 1.03 |
| TTM scalper | 4h | normal ambos | 3101 | +43.8% | +43.7% | 0.53 | 0.84 |
| Market Dynamics HH/LL breakout | 4h | lb50 ambos | 82 | +43.8% | +43.7% | 0.50 | 1.30 |

### ETH (28 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Combo 123 Reversal & Stochastic | 4h | l28 long | 103 | +62.3% | +56.6% | 1.06 | 1.48 |
| Golden X BF | 4h | 50/200 long | 37 | +58.1% | +56.6% | 0.95 | 1.78 |
| Smoothed Heiken Ashi (long-only) | 30min | 20/10 | 2242 | +79.7% | +56.8% | 0.92 | 2.33 |
| Smoothed Heiken Ashi (long-only) | 30min | 10/20 | 2242 | +79.7% | +56.8% | 0.92 | 1.92 |
| Combo 123 Reversal & Stochastic | 1h | l14 long | 515 | +59.0% | +56.8% | 0.90 | 0.87 |
| Combo 123 Reversal & Stochastic | 15min | l28 ambos | 3471 | +94.4% | +56.8% | 0.90 | 2.88 |
| LunaOwl SuperTrend 2 | 30min | m2.618 long | 1549 | +73.2% | +56.8% | 0.87 | 1.20 |
| Combo 123 Reversal & Stochastic | 4h | l14 ambos | 236 | +81.4% | +56.6% | 0.85 | 2.35 |
| Combo 123 Reversal & Stochastic | 1h | l14 ambos | 931 | +86.6% | +56.8% | 0.85 | 1.12 |
| Golden X BF | 15min | 20/100 long | 1633 | +71.5% | +56.8% | 0.84 | 1.96 |


## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| WTI | MACD + Stochastic 4h st14 ambos | +2% vs −21% | +47% vs +40% | +46% vs +8% | +60% vs +3% | +36% vs +5% | **aprovada** |
| BTC | Combo 123 Reversal & Stochastic 1h ambos | +133% vs +130% | +77% vs +15% | +18% vs +14% | +36% vs +40% | +63% vs +44% | quase (2ª metade) |
| ETH | Combo 123 Reversal & Stochastic 4h ambos | +256% vs +328% | +19% vs +0% | +45% vs −11% | +33% vs +13% | +80% vs +57% | quase (terço 1) |
| ETH | Smoothed Heiken Ashi 30m ln20 | +321% vs +330% | +23% vs +1% | +10% vs −11% | +18% vs +13% | +63% vs +57% | quase (terço 1) |
| ETH | Golden X BF 15m 20/100 ambos | +314% vs +330% | +73% vs +1% | +19% vs −11% | +31% vs +13% | +81% vs +57% | quase (terço 1) |
| ETH | Combo 123 Reversal & Stochastic 15m ln28 | +324% vs +330% | −13% vs +1% | +93% vs −11% | +60% vs +13% | +67% | não |
| ETH | Combo 123 Reversal & Stochastic 30m ln28 | +212% vs +330% | +4% vs +1% | +45% vs −11% | +31% vs +13% | +57% vs +57% | não |
| ETH | Parabolic SAR w/ EMA 1h off0 | +190% vs +330% | +49% vs +1% | −10% vs −11% | +14% vs +13% | +48% vs +57% | não |
| BTC | Parabolic SAR w/ EMA 30m off0 | +226% vs +130% | +3% vs +15% | +10% vs +13% | −4% vs +40% | +36% vs +44% | não |
| BTC | Golden X BF 4h 20/100 ambos | +82% vs +129% | +8% vs +15% | +47% vs +14% | +41% vs +40% | +52% | não |
| WTI | Linear Channel 15m hl200 | +15% vs −21% | +13% vs +38% | +3% vs +8% | +1% vs +4% | +10% | não (exposição de 1%) |
| WTI | Linear Channel 15m padrão | +8% vs −21% | +24% vs +38% | +4% vs +8% | +3% vs +4% | +11% | não (exposição de 1%) |
| WTI | Swing Parabolic SAR 4h padrão | −1% vs −21% | +16% vs +40% | +5% vs +8% | +26% vs +3% | −1% vs +5% | não |
| XAU | Swing Parabolic SAR 1h af0.01 | +11% vs +8% | +4% vs +5% | +38% vs +31% | +24% vs +25% | +4% vs +13% | não |

US100 não teve nenhuma célula acima do B&H.

## Conclusões

- **Aprovada com ressalva: MACD + Stochastic (`sqDK1npx`) no WTI 4h com Stoch 14, comprado e vendido.** EMA8−EMA24 subindo com Stoch D<25 subindo compra, o espelho vende, e inverte. +39% a.a. vs +5%, t = 1,4, 37 trades/ano; terços +2/+47/+46% vs −21/+40/+8%; 2ª metade +60% vs +3%; custo 4× +36%.
  - Ressalvas: o t total é baixo (1,4); o 1º terço é quase zero (só ganha porque o B&H caiu); o líquido fica acima do bruto, ou seja, parte do ganho vem do funding/carry do WTI e não do sinal; o Stoch 14 não é o padrão (7).
- Quase: Combo 123 Reversal & Stochastic no BTC 1h (perde só a 2ª metade) e no ETH 4h; Smoothed Heiken Ashi e Golden X BF no ETH (perdem só o 1º terço, a alta de 2020–21).
- O Linear Channel no WTI 15m tem Sharpe alto (4 a 5) mas fica posicionado só 1% do tempo e perde o 2º terço; não serve como estratégia isolada.
- XAU e US100 não tiveram nada robusto.
