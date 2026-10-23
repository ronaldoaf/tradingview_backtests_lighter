# Lote 32 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote32.py` (grade) e `scripts/study_tvlote32_rob.py` (robustez). Resultados: `results/study_tvlote32_{ativo}.txt`, `_grid.csv` e `results/study_tvlote32_rob_{ativo}.txt`. Mesma grade dos lotes anteriores: o padrão do script mais 4 combinações, em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (32):**
- **Página que não baixou (404):** `HeRJBY0A`.
- **`security` em outro TF:** `bwF5bCek`, `9tAEgAaL`, `RAfAWxLC`, `Epqb0L8C`, `vOaKc2FV`, `Eexf5DPB`, `14gEYN1R`, `rpyX1mx4`, `sWbPtQch`, `yveRmB4r`, `8uEYd75K`.
- **Sessão de bolsa:** `MEPX6LRn`, `FydaIIQ7` (também ticks), `LTRBSQI1`.
- **Pontos, ticks ou níveis fixos:** `wv68sDys` (pontos absolutos), `eVzMWyqP` (ticks), `zFLMuyND` (níveis de preço manuais), `Bs4yTYRy` (oscilador de números primos que depende da escala do preço).
- **Piramidação, DCA ou TP parcial:** `hEiX3kCj` (TP parcial em vários passos), `Yfu3aGsY` (pyramider), `6q79diem` (DCA), `DX7itST6` (TP parcial), `f8ztxAzF` (exemplo didático com várias ordens).
- **Complexas demais:** `tWdLcYVH` (alavancagem e trailing), `QSNkX7W1` (SMC), `SvcAJM3O` (Myth-Busting), `DxZ60Wla` (all-in-one), `P9vwlI3w`, `fIVuGtFw` (rede neural).
- **Outras:** `luiQYWOM` (datas da lua fixas de 2015 a 2021; a ideia da lua já foi testada no lote 25).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 384 | Hurst Future Lines of Demarcation | `4B9sbgmC` | FLD = ohlc4 deslocado de metade do ciclo (sinal 5, trade 20, tendencia 80); maquina de estados A..H: ohlc4 cruzando acima da FLD de sinal no estado A compra, abaixo no estado F vende; ohlc4 cruzando a FLD de trade no sentido contrario fecha. |
| 385 | Super Trend Daily BF | `fDiKl24D` | Stop ATR3 x 1,3 (estilo Chandelier) virando para cima com |EMA15 do ROC30| > 3% compra, para baixo vende; inverte; stop fixo de 6% a partir da barra seguinte a entrada. |
| 386 | Ultimate Scalping v2 (EMA + VWAP) | `n45dOuob` | EMA9 cruzando acima da EMA21 com close acima da VWAP do dia compra (espelho vende); stop 1,5 ATR14 e alvo 2 ATR14 a partir do close do sinal; o sinal contrario inverte. |
| 387 | SuperTrend Enhanced Pivot Reversal | `wcegMOXj` | Pivo de maxima (6/3) ainda nao rompido com Supertrend(5, 2,618) de alta arma stop de compra na maxima do pivo (espelho no pivo de minima); stop de 20% do nivel do pivo. So comprado: o stop de venda fecha. |
| 388 | HMA 200 + EMA 20 | `w4Z36wFl` | Close acima da HMA200 cruzando acima da EMA20 compra, abaixo da HMA cruzando abaixo vende; inverte. |
| 389 | Ichimoku Cloud with RSI (Coinrule) | `2OfRyQSy` | Tenkan>kijun, momentum de 25 positivo e close acima da nuvem deslocada com RSI14<50 compra; o espelho com RSI>50 vende; inverte (so comprado: o sinal baixista, sem RSI, fecha). Ordens no close viraram abertura seguinte. |
| 390 | AK RSI 2 | `klkZ7SdU` | Close acima da SMA200 e abaixo da SMA5 com RSI2<5 compra; espelho (RSI2>90) vende; os dois close_all do script (close acima e abaixo da SMA5) zeram a posicao no fechamento de qualquer barra, logo cada trade dura uma barra. |
| 391 | QuantNomad SuperTrend | `cX6X9Ry2` | SuperTrend (ATR14 x 2): ordens stop de compra e de venda na linha, sempre posicionado (so comprado: o stop de venda fecha). |
| 392 | Grant's PSAR (long-only) | `wAbIlZaz` | So long: com o SAR (0,013/0,005/0,2) acima da maxima, stop de compra no SAR; com o SAR abaixo da minima, stop de saida no SAR. |
| 393 | Donchian Channel (stop + EMA200) | `7lDOCF4F` | Close acima da EMA200: stop de compra na maxima de 20; abaixo: stop de venda na minima de 20; saida do long em stop na minima de 20, do short na maxima. |
| 394 | RSI Divergence Strategy | `mU02nqSK` | Divergencia regular do RSI14 (pivos 5/5, a 5..60 barras do anterior): alta com RSI<35 compra, baixa com RSI>76 vende; RSI>=80 fecha o long, RSI<=54,1 fecha o short; a entrada contraria inverte. |
| 395 | CCI & EMA (Tradeswithashish) | `SdhTE8Ao` | Sem posicao: close acima da EMA100 dupla, vela de alta fechando no terco de cima, volume acima da SMA20 e do anterior, CCI100>0, CCI20>100 e close acima da VWAP do dia compra (espelho vende); stop = maior entre EMA50 e EMA100 dupla (sobe com elas) e alvo de 5% do ohlc4; stop e alvo so ficam ativos depois de CCI100<0 ou close abaixo de uma das medias (espelho no short). |
| 396 | Hull MA_X + Ichimoku | `OpEMmVwl` | Hull dupla de 12 (atual vs barra anterior) para cima, close acima dela, do chikou (close de 23 barras atras) e da nuvem deslocada (9/24/51), com tenkan>=kijun ou close>kijun compra; espelho vende; fecha o long com a Hull virando e qualquer perda de linha (espelho no short). |
| 397 | Donchian Channels (KrisWaters) | `z7hAbAHD` | Stop de compra na maxima de 20 e saida em stop na minima de 10 (com a regra ATR: maior entre ela e abertura - 2 ATR20); o short (desligado no original) usa minima de 20 e maxima de 10. |
| 398 | Fisher Transform (Ehlers) | `qhXwZvJ2` | Fisher de 10 sobre hl2 positivo fica comprado, negativo fica vendido. |
| 399 | SuperTrend Trapping Candle | `H61Z9TNa` | Supertrend(2, 10) de alta com candle pequeno (faixa < 0,3% do close) de baixa e volume forte compra; espelho vende; inverte. |
| 400 | Supertrend + RSI (Alorse) | `zLLibnMR` | Supertrend(3, 10) virando para cima compra; RSI14>72 ou virada para baixo fecha; espelho no short (RSI<28), desligado no original. |
| 401 | TSI w SuperTrend decision | `lncoD9BX` | TSI = correlacao de 64 entre close e tempo; SuperTrend(10, 3) calculado sobre velas do proprio TSI: direcao de alta com TSI>-0,241 compra, de baixa com TSI<0,241 vende; as condicoes opostas fecham. |
| 402 | Trend Following Parabolic (TradeDots) | `hsJ1K1Uw` | Sem posicao: close acima da SMA200, EMA10 cruzando acima da EMA25 e SAR abaixo do close compra; stop na SMA200 e alvo de 1,3 x a distancia; espelho vende. |
| 403 | Kozlod MA Cross | `PevJdTsm` | SMA5 cruzando a SMA15 compra/vende; inverte (stop e alvo desligados no padrao). |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (0 células acima do B&H)

Nenhuma célula acima do B&H.


### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (44 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| AK RSI 2 | 1D | 10/80 ambos | 212 | +6.2% | +5.7% | 1.32 | -0.83 |
| Supertrend + RSI (Alorse) | 1D | f3 ambos | 59 | +23.2% | +5.7% | 0.87 | 1.40 |
| Trend Following Parabolic (TradeDots) | 1h | rr1.3 ambos | 479 | +22.0% | +5.4% | 0.71 | 1.41 |
| Trend Following Parabolic (TradeDots) | 1h | rr2 ambos | 410 | +24.0% | +5.4% | 0.69 | 1.52 |
| Trend Following Parabolic (TradeDots) | 4h | rr2 ambos | 118 | +13.6% | +5.4% | 0.56 | 1.93 |
| Ultimate Scalping v2 (EMA + VWAP) | 4h | tp2atr ambos | 585 | +7.8% | +5.4% | 0.53 | 2.09 |
| Super Trend Daily BF | 1D | m2.6 ambos | 49 | +11.0% | +5.7% | 0.51 | 0.72 |
| HMA 200 + EMA 20 | 30min | hma200 ambos | 2434 | +26.4% | +5.4% | 0.50 | 1.48 |
| QuantNomad SuperTrend | 1D | m2 ambos | 118 | +22.1% | +5.7% | 0.43 | 0.49 |
| Supertrend + RSI (Alorse) | 1h | f2 ambos | 2670 | +15.6% | +5.4% | 0.40 | 0.94 |

### BTC (10 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| TSI w SuperTrend decision | 15min | p64 long | 2420 | +43.8% | +43.8% | 0.72 | 2.07 |
| Donchian Channel (stop + EMA200) | 4h | d20 ambos | 316 | +47.4% | +43.7% | 0.68 | 1.53 |
| TSI w SuperTrend decision | 1D | p32 ambos | 80 | +62.2% | +43.8% | 0.67 | 1.69 |
| TSI w SuperTrend decision | 15min | p64 ambos | 4840 | +60.6% | +43.8% | 0.64 | 3.51 |
| SuperTrend Trapping Candle | 15min | 0.6% ambos | 7534 | +52.2% | +43.8% | 0.59 | 2.23 |
| TSI w SuperTrend decision | 1D | p64 ambos | 43 | +44.5% | +43.8% | 0.56 | 1.74 |
| TSI w SuperTrend decision | 4h | p64 ambos | 269 | +48.7% | +43.7% | 0.54 | 2.20 |
| TSI w SuperTrend decision | 1h | p64 ambos | 1124 | +46.7% | +43.9% | 0.53 | 1.75 |
| TSI w SuperTrend decision | 30min | p32 ambos | 4498 | +47.4% | +43.9% | 0.53 | 1.89 |
| Ichimoku Cloud with RSI (Coinrule) | 15min | sem rsi ambos | 4577 | +44.8% | +43.8% | 0.50 | 2.44 |

### ETH (48 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| SuperTrend Enhanced Pivot Reversal | 4h | f2.618 long | 96 | +89.9% | +56.6% | 1.29 | 2.69 |
| Donchian Channel (stop + EMA200) | 30min | d55 long | 582 | +64.6% | +56.8% | 1.00 | 1.75 |
| TSI w SuperTrend decision | 30min | p32 long | 2172 | +92.8% | +56.8% | 0.99 | 1.62 |
| Donchian Channel (stop + EMA200) | 30min | d20 long | 1355 | +59.0% | +56.8% | 0.98 | 2.20 |
| TSI w SuperTrend decision | 30min | p32 ambos | 4344 | +164.9% | +56.8% | 0.98 | 3.21 |
| TSI w SuperTrend decision | 15min | p64 long | 2317 | +91.4% | +56.8% | 0.98 | 2.52 |
| TSI w SuperTrend decision | 15min | p64 ambos | 4633 | +161.6% | +56.8% | 0.98 | 4.58 |
| SuperTrend Enhanced Pivot Reversal | 4h | f2.618 ambos | 193 | +157.7% | +56.6% | 0.97 | 3.18 |
| SuperTrend Enhanced Pivot Reversal | 1h | f2.618 long | 400 | +64.8% | +56.8% | 0.97 | 2.43 |
| Kozlod MA Cross | 30min | 10/30 long | 2389 | +86.0% | +56.8% | 0.95 | 2.96 |


## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| ETH | TSI w SuperTrend 15m p64 ambos | +356% vs +330% | +105% vs +1% | +85% vs −11% | +85% vs +13% | +113% vs +57% | **aprovada** |
| ETH | TSI w SuperTrend 30m p32 ambos | +466% vs +330% | +58% vs +1% | +101% vs −11% | +95% vs +13% | +118% vs +57% | **aprovada** |
| ETH | SuperTrend Enhanced Pivot Reversal 4h ambos | +231% vs +328% | +140% vs +0% | +93% vs −11% | +93% vs +13% | +156% | quase (terço 1) |
| ETH | SuperTrend Enhanced Pivot Reversal 4h long | +239% vs +328% | +50% vs +0% | +27% vs −11% | +38% vs +13% | +89% | quase (terço 1) |
| ETH | Donchian Channel 30m d20 long | +196% vs +330% | +23% vs +1% | +8% vs −11% | +22% vs +13% | +50% vs +57% | não |
| BTC | TSI w SuperTrend 15m p64 ambos | +120% vs +129% | +75% vs +15% | +8% vs +13% | +31% vs +40% | +30% vs +44% | não |
| BTC | Donchian Channel 4h d20 ambos | +100% vs +129% | +42% vs +15% | +15% vs +14% | +20% vs +40% | +45% | não |
| BTC | SuperTrend Trapping Candle 15m 0.6% | +9% vs +129% | +121% vs +15% | +44% vs +13% | +71% vs +40% | +9% | não |
| WTI | Supertrend + RSI 1D f3 ambos | +2% vs −21% | +29% vs +32% | +29% vs +8% | +28% vs +3% | +23% vs +6% | quase (terço 2) |
| WTI | Trend Following Parabolic 4h rr2 | −15% vs −21% | +29% vs +40% | +9% vs +8% | +26% vs +3% | +13% | quase (terço 2) |
| WTI | Trend Following Parabolic 1h rr2 | +16% vs −19% | +45% vs +36% | +4% vs +8% | +0% vs +3% | +21% | não |
| WTI | Ultimate Scalping v2 4h | −3% vs −21% | +19% vs +40% | +7% vs +8% | +14% vs +3% | +4% vs +5% | não |
| WTI | HMA 200 + EMA 20 30m | +31% vs −19% | +50% vs +35% | +3% vs +8% | +21% vs +3% | +9% | não |

XAU e US100 não tiveram nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: TSI w SuperTrend (`lncoD9BX`) no ETH 15m (p64, o padrão) e 30m (p32), comprado e vendido.** O TSI é a correlação entre o close e o tempo; um SuperTrend calculado sobre velas do próprio TSI decide o lado.
  - ETH 15m p64: +162% a.a. vs +57%, t = 4,4, 686 trades/ano.
  - ETH 30m p32: +165% a.a. vs +57%, t = 3,0, 643 trades/ano.
  - Ressalvas: muitos trades (o lucro médio é de 13 a 14 bp por trade, então depende do custo baixo de cripto na Lighter, embora passe no custo 4×); sempre posicionado, com drawdown acima de 100% no simulador; no BTC a mesma regra não passa.
- Quase: SuperTrend Enhanced Pivot Reversal no ETH 4h (perde só o 1º terço); Supertrend + RSI no WTI 1D e Trend Following Parabolic no WTI 4h (perdem só o 2º terço).
- XAU e US100 não tiveram nada acima do B&H.
