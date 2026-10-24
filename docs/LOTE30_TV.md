# Lote 30 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote30.py` (grade) e `scripts/study_tvlote30_rob.py` (robustez). Resultados: `results/study_tvlote30_{ativo}.txt`, `_grid.csv` e `results/study_tvlote30_rob_{ativo}.txt`. Mesma grade dos lotes 26 a 29: o padrão do script mais 4 combinações (dois valores de parâmetro × comprado e vendido vs só comprado; nas só comprado, 2 × 2 parâmetros), em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (31):**
- **`security` em outro TF ou Pine antigo com `security`:** Qullamaggie Breakout (`cDCAPrd1`), RichG Easy MTF (`zeMUHHOD`), DCA com Bollinger (`uVaU9LVC`, também DCA), BTC Candle Correlation (`Bp053p4R`), Investing Gold (`wwOpdv9J`), Elite Strategy (`IyPlUmDS`), Footprint (`x51WyBCh`), `XPMLrxgf` (lookahead_on), MACD oscillator 4H (`VCWVU9ge`), MA Crossover (`uyd6qx2b`) e Nifty 2 Candle Theory (`rloZrXAT`, também sessão).
- **Página que não baixou (404):** noro's MA ATR (`Wmch7RYL`).
- **Templates, exemplos e ferramentas:** BEST Strategy Template Autoview (`jeD5jntQ`), Strategy Template Benson (`IR3QU1Tm`) e Strategy Code Example 2 (`uCalwUsg`, também stops em ticks).
- **Sessão de bolsa:** HalfTrend SNIPERMONKEY (`0vvrOpg1`, sessão indiana) e ThinkTech AI Signals (`xJJYblbA`, janela 9h–12h).
- **Stops ou lucros em valor absoluto, pips ou ticks:** 15min50MA (`0BHGOwdj`, lucro aberto > 500), RipsterTest (`gBGb81Tw`, lucro aberto > 300), Alerts to MT4 (`WHOZ6UPz`, alvo em ticks), Patient Trendfollower (`8Pm6VUL5`, alvo em pips) e NNFX ATR/Kijun/%R (`kISazOzG`, pips).
- **Piramidação, DCA, martingale ou TP parcial:** Trend Catcher (`EqoxkfoI`, saída parcial de 50%), Momentum BTC 30m Stoch RSI (`79Tn4cQY`, tamanho que cresce após perda), MACD + RSI oversold (`eYF1FQ2T`, pyramiding 4 e venda parcial), Peri Bollinger (`XRPeqEdA`, até 5 ordens), Gunbot Bbands (`fKGXQw0p`, pyramiding 100), TASC 2026.08 Ag Selling (`VFzCk3HX`, sazonal e pyramiding 3).
- **Complexas demais para reproduzir com fidelidade:** EMA Slope RSI Oscillator (`RNxThUtE`, 1.367 linhas) e Trend Trader Remastered (`En4PabIp`, bibliotecas externas e TPs/reentradas parciais).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 344 | Hull MA and Candle cross | `PDt7xwn2` | Hull de z sobre a abertura: abertura acima da Hull e acima da abertura de 10 barras atras compra, o espelho vende; inverte. |
| 345 | TrendShift Supertrend + ADX | `TbK1rB5B` | Supertrend ATR10 com multiplicador 1,75 quando ADX>25 e 4,5 quando ADX<20 (mantem o anterior entre os dois); virada do Supertrend compra/vende, sem entrada quando ADX<20; inverte (o stop/alvo vem desligado). |
| 346 | Multi-MA | `34lAHcyo` | VWMA, RMA, SMA, WMA e EMA de 66 todas subindo compra, todas caindo vende; inverte. |
| 347 | MAster Gold | `9morbD5t` | Close acima da EMA182 cruzando acima da SMA60 compra; minima abaixo da SMA182 com close cruzando abaixo da EMA60 vende; inverte. |
| 348 | RSI Divergence x Ichimoku x 200EMA | `IDBU7W3o` | Divergencia (regular ou oculta) do RSI14 por pivos 5/5: alta com o topo da nuvem (sem deslocamento) acima da EMA200 compra, baixa com a EMA200 acima do fundo da nuvem vende; RSI cruzando acima de 75 fecha o long, acima de 25 fecha o short; a entrada contraria inverte. |
| 349 | Percent Trailing Stop | `bVkqAx0s` | SMA10 x SMA20 compra/vende e inverte; trailing stop de 10% sobre o close (ordem stop na barra seguinte). So comprado: o cruzamento para baixo fecha o long. |
| 350 | Multiple MACD RSI | `0bqo8tHC` | Histograma do MACD 10/22/9 (close, sinal SMA) e do MACD 21/45/20 (abertura) positivos com (close+max) acima do anterior compra; os dois negativos, (close+min) abaixo do anterior e StochRSI D>20 vende; inverte. |
| 351 | Gann Swing Oscillator | `FTT9zMVm` | Maxima de 5 subindo depois de cair = +1, minima de 5 caindo depois de subir = -1 (senao mantem); fica comprado em +1 e vendido em -1. |
| 352 | RSI of MACD (long-only) | `WfaaCqaN` | So long: RSI14 da linha MACD 12/21 cruzando acima de 30 ou 35 com close >= EMA21 compra; RSI cruzando abaixo de 15 fecha (sl: stop opcional em % da entrada). |
| 353 | Optimized Trend Tracker | `ycDUERPO` | VIDYA (CMO 9, periodo 1) e OTT de pct%: VIDYA cruzando acima da OTT de 2 barras atras compra, abaixo vende; inverte. |
| 354 | SuperIchi | `hTdfAu3p` | SuperIchi (tenkan 9x2, kijun 26x4, span B 52x6, deslocamento 26): tenkan>kijun, close>tenkan, kijun>senkouA[25], senkouA[25]>senkouB[25] e pullback para baixo das duas linhas nas ultimas 5 barras compra (espelho vende); stop no menor de (close - ATR14) e minima de 15, alvo 2R; a entrada contraria inverte. |
| 355 | KALKI TFXBOT | `gFMT7BUb` | Ultimo pivo de minima (10/3) varrido (minima abaixo, close acima, candle de alta, close>EMA200) compra com stop na minima e alvo rr x risco; espelho no pivo de maxima; a entrada contraria inverte (o buffer de stop em pontos foi ignorado). |
| 356 | 2x Universelle Linien | `mpwbMiL9` | EMA21 cruzando acima da SMA50 compra e fecha o short; abaixo vende e fecha o long. |
| 357 | Supertrend pullback | `kRMAa3JF` | Supertrend 3/10: pullback (minima anterior cruzando abaixo da linha de alta e maxima acima da anterior) ou virada simples, com RSI14>=50 e close>EMA200 compra (espelho vende), so sem posicao; stop e alvo de 1%. |
| 358 | Scalping Dips On Trend (long-only) | `iHHO0PJA` | So long: queda de mais de 2% na barra com SMA50 acima do close compra; close 10% abaixo ou 3% acima da entrada fecha na abertura seguinte. |
| 359 | Momentum BF | `xd2U2Gho` | Momentum de 18 e sua variacao positivos compra, negativos vende (inverte); stop fixo de 8% no long e 7% no short a partir da barra seguinte a entrada. So comprado: o sinal de venda fecha. |
| 360 | 1 min forex scalping | `WlJVt2vS` | EMA12 cruzando a SMA55 com EMA12>EMA26 compra, com EMA12<EMA26 vende; inverte (k multiplica os periodos). |
| 361 | LunaOwl suporte/resistencia | `dC2MG4Dj` | Resistencia = maxima de 50 no penultimo cruzamento close x SMA50, suporte = minima de 50 no mesmo ponto; close rompendo a resistencia compra, perdendo o suporte vende; inverte. |
| 362 | RSI Buy and Sell (long-only) | `Z59QoZWN` | So long: RSI14 acima de 70 compra (momentum), abaixo de 30 fecha. |
| 363 | Harmonic System | `WG8oLdFX` | Seis medias harmonicas encadeadas (3 barras cada, a partir do close anterior): min(T1,T2,T3) cruzando acima de max(T4,T5,T6) compra, min(T1,T2) cruzando abaixo de max(T3,T4) vende; inverte. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (2 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Percent Trailing Stop | 1h | t10% ambos | 2464 | +13.9% | +13.4% | 0.76 | 2.90 |
| Percent Trailing Stop | 1h | t5% ambos | 2464 | +13.7% | +13.4% | 0.75 | 3.95 |

### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (39 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| RSI Divergence x Ichimoku x 200EMA | 4h | lb5 ambos | 147 | +29.4% | +5.4% | 0.82 | 1.10 |
| Hull MA and Candle cross | 30min | z100 ambos | 6955 | +26.2% | +5.4% | 0.49 | 1.22 |
| RSI Divergence x Ichimoku x 200EMA | 4h | lb3 ambos | 158 | +15.8% | +5.4% | 0.46 | 0.97 |
| Multiple MACD RSI | 30min | 10/22 ambos | 3540 | +22.3% | +5.4% | 0.42 | 2.12 |
| Harmonic System | 4h | close ambos | 1802 | +20.1% | +5.4% | 0.40 | 1.24 |
| Gann Swing Oscillator | 1h | l10 ambos | 1116 | +20.3% | +5.4% | 0.40 | 1.64 |
| Multiple MACD RSI | 1D | 12/26 ambos | 76 | +19.1% | +5.7% | 0.39 | 0.96 |
| Multiple MACD RSI | 1D | 10/22 ambos | 74 | +18.5% | +5.7% | 0.38 | 0.86 |
| 2x Universelle Linien | 4h | 50/200 ambos | 73 | +18.0% | +5.4% | 0.37 | 1.22 |
| Multiple MACD RSI | 30min | 12/26 ambos | 3604 | +19.4% | +5.4% | 0.36 | 1.70 |

### BTC (26 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Multi-MA | 4h | l150 long | 43 | +49.5% | +43.7% | 1.14 | 3.14 |
| TrendShift Supertrend + ADX | 4h | m3 long | 82 | +46.4% | +43.7% | 1.09 | 1.71 |
| Multi-MA | 30min | l66 long | 959 | +55.3% | +43.9% | 1.03 | 2.39 |
| Multi-MA | 1h | l66 long | 463 | +45.9% | +43.9% | 0.96 | 2.00 |
| Multi-MA | 15min | l150 long | 961 | +45.7% | +43.8% | 0.88 | 1.90 |
| Multi-MA | 30min | l66 ambos | 1918 | +86.9% | +43.9% | 0.86 | 2.70 |
| Multi-MA | 4h | l150 ambos | 86 | +83.6% | +43.7% | 0.84 | 3.26 |
| Multi-MA | 15min | l66 long | 2153 | +48.3% | +43.8% | 0.83 | 1.35 |
| RSI Divergence x Ichimoku x 200EMA | 4h | lb3 ambos | 145 | +46.5% | +43.7% | 0.78 | 1.88 |
| Momentum BF | 30min | l36 long | 4950 | +45.1% | +43.9% | 0.77 | 1.12 |

### ETH (65 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Multi-MA | 4h | l66 long | 101 | +77.2% | +56.6% | 1.15 | 2.16 |
| Multi-MA | 15min | l150 long | 958 | +88.2% | +56.8% | 1.14 | 1.70 |
| TrendShift Supertrend + ADX | 4h | m3 long | 77 | +68.5% | +56.6% | 1.09 | 1.23 |
| Multi-MA | 30min | l66 long | 978 | +83.6% | +56.8% | 1.08 | 2.80 |
| LunaOwl suporte/resistencia | 4h | lb50 long | 47 | +67.9% | +56.6% | 1.02 | 1.30 |
| Hull MA and Candle cross | 4h | z100 long | 412 | +64.2% | +56.6% | 0.97 | 1.38 |
| MAster Gold | 30min | 100/30 long | 1228 | +66.0% | +56.8% | 0.97 | 1.26 |
| Multi-MA | 15min | l150 ambos | 1916 | +152.2% | +56.8% | 0.96 | 3.86 |
| 2x Universelle Linien | 4h | 50/200 long | 38 | +58.1% | +56.6% | 0.96 | 1.59 |
| Multi-MA | 30min | l66 ambos | 1956 | +139.9% | +56.8% | 0.92 | 3.41 |


## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| ETH | Multi-MA 15m l150 ambos | +496% vs +330% | +29% vs +1% | +106% vs −11% | +76% vs +13% | +132% vs +57% | **aprovada** |
| ETH | Multi-MA 4h l66 ambos | +338% vs +328% | +67% vs +0% | +38% vs −11% | +30% vs +13% | +127% | **aprovada** |
| BTC | Multi-MA 4h l150 ambos | +189% vs +129% | +69% vs +15% | +18% vs +14% | +47% vs +40% | +83% vs +44% | **aprovada** |
| BTC | Multi-MA 30m l66 ambos | +324% vs +130% | +27% vs +15% | +22% vs +13% | +25% vs +40% | +72% | quase (2ª metade) |
| BTC | Multi-MA 15m l150 ambos | +214% | −3% vs +15% | +44% vs +13% | +19% vs +40% | +51% | não |
| BTC | TrendShift Supertrend 4h m3 ambos | +57% vs +129% | +88% vs +15% | +41% vs +14% | +65% vs +40% | +65% | quase (terço 1) |
| ETH | TrendShift Supertrend 4h m3 ambos | +226% vs +328% | +79% vs +0% | +45% vs −11% | +57% vs +13% | +112% | quase (terço 1) |
| ETH | 2x Universelle Linien 30m 21/50 ambos | +318% vs +330% | +54% vs +1% | +42% vs −11% | +19% vs +13% | +90% | quase (terço 1) |
| ETH | Percent Trailing Stop 1h t5% ambos | +204% vs +330% | +71% vs +1% | +86% vs −11% | +44% vs +13% | +90% | quase (terço 1) |
| WTI | RSI Divergence x Ichimoku 4h lb5 ambos | +24% vs −21% | +32% vs +40% | +23% vs +8% | +34% vs +3% | +28% | quase (terço 2) |
| WTI | Gann Swing Oscillator 1h l10 ambos | +22% vs −19% | +11% vs +36% | +28% vs +8% | +27% vs +3% | +12% | quase (terço 2) |
| WTI | Multiple MACD RSI 30m 10/22 ambos | +6% vs −19% | +78% vs +35% | −5% vs +8% | −13% vs +3% | −2% | não |
| XAU | Percent Trailing Stop 1h t5% ambos | +11% vs +8% | −2% vs +5% | +37% vs +31% | +21% vs +25% | +1% | não |

US100 não teve nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: Multi-MA (`34lAHcyo`) no ETH 15m (l150) e 4h (l66) e no BTC 4h (l150), comprado e vendido.** A regra é simples: as cinco médias (VWMA, RMA, SMA, WMA, EMA) do mesmo período subindo juntas compram, caindo juntas vendem.
  - ETH 15m l150: +152% a.a. vs +57%, t = 3,9, 284 trades/ano.
  - ETH 4h l66 (o padrão do script): +129% a.a. vs +57%, t = 3,0, 30 trades/ano.
  - BTC 4h l150: +84% a.a. vs +44%, t = 3,3, 13 trades/ano.
  - Ressalvas: é um seguidor de tendência sempre posicionado, e o custo de cripto na Lighter é baixo, por isso o custo 4× quase não pesa; no ETH 4h o 1º terço passa por pouco (+338% vs +328%); no BTC 4h o 3º terço também passa por pouco (+18% vs +14%); as três células são a mesma ideia e devem ser bem correlacionadas.
- Quase: Multi-MA no BTC 30m, TrendShift Supertrend no BTC e ETH 4h, 2x Universelle Linien no ETH 30m e Percent Trailing Stop no ETH 1h (todas perdem só o 1º terço, a alta de 2020–21); RSI Divergence x Ichimoku e Gann Swing no WTI (perdem o 2º terço).
- XAU e US100 não tiveram nada robusto.
