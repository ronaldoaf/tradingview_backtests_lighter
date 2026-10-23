# Lote 33 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote33.py` (grade) e `scripts/study_tvlote33_rob.py` (robustez). Resultados: `results/study_tvlote33_{ativo}.txt`, `_grid.csv` e `results/study_tvlote33_rob_{ativo}.txt`. Mesma grade dos lotes anteriores: o padrão do script mais 4 combinações, em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (33):**
- **Página que não baixou (404):** `JuOqMfBq`, `PS8RkcfQ`, `yY7GH7OG`, `3RAQ6bbp`.
- **`security` em outro TF:** `QMvHkvdQ`, `UfLWnWQ6`, `gJjULyA2`.
- **Sessão de bolsa:** `RMrMYBYr` (também pips), `6Kubkdf3`, `bRU5AT0T`.
- **Pips, ticks, pontos ou lucro absoluto:** `5zYcH3Gx`, `zMrGet6h`, `0JSS52Y2`, `qVRxr42U`, `jN5Mtewr`.
- **Piramidação, DCA, martingale ou TP parcial:** `kHhCik9f`, `Pke3AncL` (pyramiding 2000), `RqrBb3zx`, `NJb4BQ5n`, `JkzbgenP`, `G4RNcGXg`, `vQknC52h`, `9Z9iu1y3`, `69YQAwdS`.
- **Complexas demais ou ferramentas:** `nGdo7mnS`, `RSFb5nyO` (1.690 linhas), `R9qM6XrY`, `iCzeNf6N`, `aKBYGQpf`, `WUKWF5Uu`, `w9SHOgic`, `82LZ3x0m` (ferramenta), `JwQlZ3wu`, `VQqkfWR5`, `GWXfa7R1`.

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 404 | PSAR + ADX + CMF + RSI (long-only) | `yFwSIDYf` | So long: SAR (1,02/1,02/1,2, como no script) fora da alta, RSI(50)>49, ADX14 acima da sua EMA10 e CMF20>0 compra; o espelho (SAR em alta, RSI<49, ADX abaixo da EMA, CMF<0) fecha. |
| 405 | Abdoli's Heikin Ashi Smoothed (long-only) | `2N0o6J1P` | So long: Heikin Ashi sobre as EMAs de 65 de OHLC; 3 velas verdes com o close HA subindo compra, 3 vermelhas caindo fecha. |
| 406 | Bar Counter Trend Reversal | `0KAtQQDD` | 3 closes caindo com minima abaixo do Keltner (EMA20 -/+ 2 EMA20 do TR) compra, uma vez por sequencia; 3 subindo com maxima acima da banda vende; inverte. |
| 407 | VWMA with ATR stops (long-only) | `HY2GjJIc` | So long: trailing stop de 3,5 ATR33 sobre o close; RSI14 da VWMA33 >= 30, candle de alta, close acima da VWMA e trailing em alta compra; close cruzando abaixo do trailing fecha. |
| 408 | SMA 200 bands (long-only) | `QEVAQHl6` | So long: close acima de SMA200 x 1,04 compra; abaixo de SMA200 x 0,97 fecha. |
| 409 | TASC 2024.08 VCTS (long-only) | `K3s5dmdv` | So long: ADX14>30, TTI (VWMA 13/26 com multiplicador de volume) acima do sinal SMA9 e VPCI (5/25)>0 compra; VPCI<0 fecha. |
| 410 | Trend Bounce | `xV3t2X7R` | Close acima da SMA200 e abaixo da minima de 7 anterior compra; abaixo da SMA200 e acima da maxima de 7 anterior vende (inverte); close acima da maxima anterior fecha o long, abaixo da minima fecha o short; stop de 2 x SMA10 do TR (da barra anterior a entrada) a partir da entrada. |
| 411 | Parabolic SAR stop entries | `CfnaujUD` | SAR (0,02/0,02/0,2) acima ou na maxima: stop de compra no SAR; abaixo ou na minima: stop de venda; a entrada contraria inverte (so comprado: o stop de venda fecha). |
| 412 | Money Flow (Chaikin Oscillator) | `YKeGkOA0` | Soma de (close-open)/(high-low) x volume em 10 e em 3, cada uma na sua EMA; diferenca lenta - rapida positiva = comprado, negativa = vendido. |
| 413 | SuperTrend chandelier 7/7 | `mk3G22hz` | Stop chandelier sobre hl2 com 7 x ATR7: virada para cima compra, para baixo vende; inverte. |
| 414 | 3 RSI | `raWdLVOY` | RSI 7, 14 e 21 cruzando acima de 30 na mesma barra compra; os tres cruzando abaixo de 70 vende; inverte. |
| 415 | Signal To Noise | `m8ascqf7` | StN = -10 log(media de 1/close das barras 1..20); StN acima da sua SMA7 (barra anterior) = comprado, abaixo = vendido, igual = zerado. |
| 416 | EMA + RSI Sniper (long-only) | `83Ijv4aU` | So long: maxima cruzando acima da EMA50 com close acima da EMA70 compra; maxima cruzando abaixo fecha; alvo de 9,6% e stop de 5,1% (do close do sinal). |
| 417 | MACD 8/16/11 (sinal SMA) | `zR9yW6nn` | MACD 8/16 acima do sinal SMA11 = comprado, abaixo = vendido. |
| 418 | Hull MA Crossover | `zb7PgKWs` | Hull de 14 sobre ohlc4[1] (n1) e ohlc4[2] (n2); n1>n2 com longcross1>longcross2 compra, o espelho vende, so sem posicao; a condicao contraria fecha. |
| 419 | Binary Option EMA/Stoch | `ARoezF2n` | Como escrito (contrario): close abaixo da EMA4 das minimas, abertura abaixo do meio das EMAs, close abaixo da EMA21 e Stoch14 K e D<50 compra; o espelho vende; inverte. |
| 420 | Dual Supertrend with MACD | `zFKRj4Gi` | Supertrend (10, 3) e (20, 5) em alta com histograma do MACD 12/26/9 positivo compra, o espelho vende; qualquer um virando fecha. |
| 421 | VWAP X EMA | `DP1S7S5j` | Close acima da VWAP diaria, da EMA50 e da EMA200 compra; abaixo da VWAP e da EMA50 vende; inverte. |
| 422 | Stochastic Z-Score (TradeDots) | `Nft2YKWq` | Media de z-score (80) e Stoch(14, 7) reescalado para -4..4 acima de 2,8 vende, abaixo de -2,8 compra, com espera de 5 barras; z>0 fecha o long, z<0 fecha o short. |
| 423 | Ichimoku + EMA filter | `IYQMk5fS` | Linhas lead 1 (tenkan 9 + kijun 26) e lead 2 (52) sem deslocamento: lead1>lead2, close acima da lead1, candle de alta e EMA24>EMA90 compra, so sem posicao; espelho vende; close abaixo da lead1 com candle de baixa fecha o long, acima da lead2 com candle de alta fecha o short. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (0 células acima do B&H)

Nenhuma célula acima do B&H.


### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (38 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Trend Bounce | 4h | c7 ambos | 506 | +17.5% | +5.4% | 0.79 | 1.33 |
| Money Flow (Chaikin Oscillator) | 1h | 3/10 ambos | 6656 | +30.1% | +5.4% | 0.54 | 1.07 |
| Dual Supertrend with MACD | 1h | 3/5 ambos | 2211 | +18.2% | +5.4% | 0.52 | 1.43 |
| MACD 8/16/11 (sinal SMA) | 1h | 12/26/9 ambos | 4642 | +25.3% | +5.4% | 0.49 | 2.91 |
| VWAP X EMA | 1h | ema50 ambos | 2439 | +25.6% | +5.4% | 0.48 | 1.46 |
| 3 RSI | 1h | 40/60 ambos | 489 | +24.7% | +5.4% | 0.46 | 0.83 |
| Trend Bounce | 1D | c7 ambos | 79 | +6.0% | +5.7% | 0.45 | 0.33 |
| Trend Bounce | 4h | c14 ambos | 313 | +6.7% | +5.4% | 0.43 | -0.05 |
| SuperTrend chandelier 7/7 | 1h | m3 ambos | 1619 | +22.4% | +5.4% | 0.42 | 1.48 |
| SuperTrend chandelier 7/7 | 4h | m7 ambos | 112 | +21.1% | +5.4% | 0.42 | 1.24 |

### BTC (13 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| VWAP X EMA | 1D | ema20 long | 93 | +44.3% | +43.8% | 1.20 | 1.85 |
| VWAP X EMA | 4h | ema50 long | 329 | +44.6% | +43.7% | 1.13 | 1.34 |
| VWAP X EMA | 1D | ema50 long | 56 | +44.6% | +43.8% | 1.10 | 2.10 |
| SuperTrend chandelier 7/7 | 1h | m7 long | 185 | +44.9% | +43.9% | 1.03 | 1.02 |
| SuperTrend chandelier 7/7 | 4h | m7 ambos | 91 | +65.5% | +43.7% | 0.70 | 2.33 |
| VWAP X EMA | 1D | ema50 ambos | 113 | +63.9% | +43.8% | 0.68 | 1.98 |
| VWAP X EMA | 1D | ema20 ambos | 187 | +62.6% | +43.8% | 0.66 | 2.21 |
| VWAP X EMA | 4h | ema50 ambos | 659 | +62.0% | +43.7% | 0.66 | 2.01 |
| SuperTrend chandelier 7/7 | 1h | m7 ambos | 371 | +61.7% | +43.9% | 0.64 | 1.71 |
| VWAP X EMA | 1h | ema50 ambos | 2443 | +56.0% | +43.9% | 0.62 | 2.59 |

### ETH (50 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Ichimoku + EMA filter | 4h | ema long | 381 | +59.4% | +56.6% | 1.46 | 1.95 |
| TASC 2024.08 VCTS (long-only) | 4h | adx20/vp50 | 183 | +57.0% | +56.6% | 1.38 | 2.52 |
| VWAP X EMA | 4h | ema20 long | 511 | +65.8% | +56.6% | 1.26 | 2.37 |
| VWAP X EMA | 30min | ema50 long | 2403 | +82.6% | +56.8% | 1.19 | 2.61 |
| VWAP X EMA | 4h | ema50 long | 353 | +59.5% | +56.6% | 1.07 | 1.63 |
| SMA 200 bands (long-only) | 4h | 1.02/0.99 | 67 | +63.6% | +56.6% | 1.07 | 1.67 |
| SMA 200 bands (long-only) | 4h | 1.04/0.99 | 49 | +57.4% | +56.6% | 1.06 | 1.64 |
| VWMA with ATR stops (long-only) | 4h | 3.5atr/33 | 119 | +60.4% | +56.6% | 1.04 | 1.54 |
| VWAP X EMA | 30min | ema20 long | 3746 | +60.0% | +56.8% | 0.98 | 2.82 |
| VWMA with ATR stops (long-only) | 4h | 3.5atr/20 | 126 | +56.6% | +56.6% | 0.97 | 1.27 |


## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| ETH | VWAP X EMA 30m ema50 ambos | +335% vs +330% | +89% vs +1% | +60% vs −11% | +48% vs +13% | +92% vs +57% | **aprovada** |
| ETH | VWAP X EMA 30m ema50 long | +306% vs +330% | +30% vs +1% | +13% vs −11% | +22% vs +13% | +64% | quase (terço 1) |
| ETH | VWAP X EMA 4h ema20 long | +181% vs +328% | +40% vs +0% | +20% vs −11% | +28% vs +13% | +62% | quase (terço 1) |
| ETH | Ichimoku + EMA filter 4h long | +181% vs +328% | +31% vs +0% | +12% vs −11% | +31% vs +13% | +57% vs +57% | quase (terço 1) |
| ETH | TASC VCTS 4h adx20/vp50 | +164% vs +328% | +15% vs +0% | +26% vs −11% | +29% vs +13% | +56% vs +57% | não |
| ETH | Signal To Noise 30m l42 ambos | +327% vs +330% | +51% vs +1% | +11% vs −11% | −7% vs +13% | +62% | não |
| BTC | SuperTrend chandelier 4h m7 ambos | +181% vs +129% | +36% vs +15% | +9% vs +14% | +20% vs +40% | +65% | não |
| BTC | VWAP X EMA 1D ema20 ambos | +133% vs +129% | +54% vs +15% | −4% vs +14% | +30% vs +39% | +61% | não |
| BTC | VWAP X EMA 1D ema20 long | +119% vs +129% | +29% vs +15% | +1% vs +14% | +27% vs +39% | +44% vs +44% | não |
| WTI | Trend Bounce 4h c7 ambos | +11% vs −21% | +18% vs +40% | +9% vs +8% | +9% vs +3% | +14% vs +5% | quase (terço 2) |
| WTI | MACD 1h 12/26/9 ambos | +20% vs −19% | +50% vs +36% | +9% vs +8% | −3% vs +3% | −6% | não |
| WTI | Dual Supertrend 1h 3/5 ambos | +17% vs −19% | +30% vs +36% | +9% vs +8% | +2% vs +3% | +3% | não |

XAU e US100 não tiveram nenhuma célula acima do B&H.

## Conclusões

- **Aprovada com ressalva: VWAP X EMA (`DP1S7S5j`) no ETH 30m com EMA50 (o padrão), comprado e vendido.** Close acima da VWAP diária, da EMA50 e da EMA200 compra; abaixo da VWAP e da EMA50 vende; inverte. +138% a.a. vs +57%, t = 4,0, cerca de 710 trades/ano.
  - Ressalvas: o 1º terço passa por apenas 5 p.p. (+335% vs +330%); muitos trades, dependendo do custo baixo de cripto (passa no custo 4× com +92%); a mesma regra não passa no BTC.
- Quase: VWAP X EMA só comprado no ETH 30m e 4h e Ichimoku + EMA no ETH 4h (perdem só o 1º terço); Trend Bounce no WTI 4h (perde só o 2º terço).
- XAU e US100 não tiveram nada acima do B&H.
