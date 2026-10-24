# Lote 28 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote28.py` (grade) e `scripts/study_tvlote28_rob.py` (robustez). Resultados: `results/study_tvlote28_{ativo}.txt`, `_grid.csv` e `results/study_tvlote28_rob_{ativo}.txt`. Mesma grade dos lotes 26 e 27: o padrão do script mais 4 combinações (dois valores de parâmetro × comprado e vendido vs só comprado), em 15m, 30m, 1h, 4h e 1D (Hull MA vs Candle só intradiário, porque usa a abertura do dia).

**Puladas na ordem da lista (36):**
- **`security` em outro TF, Pine antigo ou dados externos:** Ajay R5.41 (`mBhnRO3S`, 26 `security`), Camarilla H4/L4 (`11Of2i0P`, Pine v2), MACD EMA Strategy (`8WbIRZkS`, EMA de 15 min via `security`), MTF HTF MACD MFI Scalper (`X4Ix7Tbw`), `cGX0aCYh`, MA Candles Supertrend (`3o1JCZQL`) e Myth-Busting 12 (`eg9wcYuj`).
- **Páginas que não baixaram (404):** `jCFatPh6`, `p2y7o8RN` e `cUBda2di`.
- **Templates, ferramentas ou alertas:** Moving Stop-Loss para MT4/MT5 (`GRTIMXzJ`), TP/SL Toolkit AxeAlgo (`iILE5e3m`, 892 linhas) e Volume Block Order Analyzer (`NMag7dki`).
- **Sessão de bolsa específica:** TICK para opções do SPY (`5NpphIlt`), Premarket Breakout (`0LJUxO7T`), NIFTY 50 5 min (`VUldc7Rr`), PURE MORNING 2.0 (`TsR0HZC3`) e Candle Patterns (`5K3LE0Zs`, sessão e stops em ticks).
- **Piramidação ou TPs parciais:** VWAP and BB (`oZYSB6Ui`), MTF Diagonally Layered RSI (`z1fsrtce`), `CEzU8qc0` (pirâmide de 5), Golden Triangle (`YC0Fpmus`), Multi-Step FlexiMA (`627VbHkS`), Z-Score TradeDots (`tb0HYAkd`, pirâmide 9999) e VCP pivot buy (`ZjWK7n8O`, saídas parciais).
- **Stop/alvo absoluto em ticks ou forex:** Squeeze Momentum LazyBear (`5tuGpzpd`, SL/TP/trailing em pontos), Elliott strategy (`6Ry6W4hu`, distância fixa de 0,02 e lucro em dinheiro) e YK Fuller (`VIcQB3cV`, níveis redondos de forex).
- **Complexas demais para reproduzir com fidelidade:** SSL Wave Trend (`J0urw1QI`, 568 linhas), Hilega Milega (`rQZMXkcZ`, seis modos de entrada), `OePmdMFg` (280 linhas), `1Im3kKwi` (560 linhas), MultiCross v4.20 (`7S2pDMA5`, três Hulls + MACD + TSI em Pine v2), Market Trend Levels BigBeluga (`v0XszvRG`, filtros múltiplos), Breaks and Retests (`800ndgbX`, 396 linhas), Ichimoku Keltner (`WSufrZ4b`, ordens stop com cancelamento e filtro de volume), MA Crossover Swing (`uNIA4siU`, 437 linhas), Morun Astro (`dWi5MI7l`, 406 linhas), YinYang RSI Volume (`cO34DTxx`, máquina de estados de zonas) e Loft V4 (`Laq4rDWw`, 393 linhas).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 304 | Stochastic (BiznesFilosof) | `V5PHO3OM` | %K(21, 3) cruza a %D para cima no mesmo candle em que cruza 14 para cima compra; cruza para baixo junto com 86 vende; inverte. |
| 305 | Kozlod 3 MA | `pJS1gX7O` | SMA5 cruza a SMA20 para cima com SMA20 > SMA100 compra; espelho vende; inverte (SL/PT desligados). |
| 306 | PlanB Quant Investing 101 | `Tz02ikOo` | Menor RSI14 das 6 barras anteriores < 50 e RSI atual 2 pontos acima dele compra; maior RSI das 6 anteriores > 90 e RSI atual < 65 vende; inverte. |
| 307 | Crypto Crew University (MFI/RSI/StochRSI) | `pVHd5BHO` | MFI14 e RSI14 do hlc3, %K e %D do Stoch RSI (14, 14, 3, 3) todos abaixo de 20 compra, todos acima de 80 vende; inverte; stop 20%. |
| 308 | Bitcoin SuperFlip | `NgSIfKQx` | SuperTrend(10, 1,8) vira para cima com close > EMA200 compra, para baixo com close < EMA200 vende; toda virada contraria fecha (ADX, SL e TP vem desligados). |
| 309 | Price Action + Bollinger | `ExBZnqPc` | Vela grande (corpo > 2x a media de 100) de baixa fechando abaixo da BB(21, 2,1), seguida de vela de alta com menos da metade do corpo compra; espelho vende; inverte. |
| 310 | FX Sniper T3-CCI | `tfkYcvBX` | T3 (5, 0,618) do CCI14 do close: acima de 0 comprado, abaixo vendido; sempre posicionado. |
| 311 | PMax | `v6Ws9H9j` | EMA10 do hl2 com stop de 3 x ATR10 (PMax): media cruza o PMax para cima compra, para baixo fecha (o padrao e so comprado; ambos inverte). |
| 312 | Golden Vector Trend Orchestrator | `dxhgQwyI` | SuperTrend(14, 3,5) de alta, close > EMA200, ADX14 >= 25 e DI+ > DI- (no primeiro candle em que tudo vale) compra; espelho vende; fecha quando o SuperTrend vira. |
| 313 | Heikin Ashi Price Action | `FEJvYRkw` | So long: close HA acima da maxima HA anterior, vela HA verde e maxima HA anterior acima da de 2 barras atras compra; vela HA vermelha fechando abaixo da minima HA anterior fecha (ambos: o espelho vende). |
| 314 | L2 Reversal Labels | `FH1VyeNT` | MACD(12, 26, 9) cruza o sinal para cima com close abaixo e MACD acima dos valores do cruzamento de alta anterior (divergencia) compra; espelho vende; inverte; stop 2 ATR14 e alvo 3 ATR; 3 barras de espera entre sinais. |
| 315 | SuperTrend Cloud | `sO5mkXTE` | Duas SuperTrends (ATR4 x 2,4 e x 4,8): close cruza uma estando acima da outra compra (espelho vende); fecha quando o close entra na nuvem entre as duas. |
| 316 | Moving Average (BiznesFilosof) | `GFqaQvbX` | Close cruza a SMA21 para cima compra, para baixo vende; inverte. |
| 317 | Hull MA vs Candle | `lc6FSl0Z` | Sobre a abertura: abertura > HMA50 > abertura do dia e abertura subindo compra; espelho vende; abertura < HMA < abertura do dia fecha o long (espelho no short). |
| 318 | Bollinger Breakout (long-only, stop) | `EBlgYNEe` | So long: ordem stop na banda superior (BB20, 2) compra pelo pavio; stop de saida na banda inferior (tight: o maior entre a banda e entrada - 8%). |
| 319 | RCI | `BsqKKqyq` | RCI10 cruza a sua SMA14 para cima compra, para baixo vende; inverte. |
| 320 | Heikin Ashi MACD | `YfPnKE22` | MACD de DEMAs feitas com SMA (12, 25, sinal SMA15) sobre o close Heikin Ashi: delta cruza 0 para cima compra, para baixo vende; inverte; alvo 10% e stop 3% (a ordem stop no close virou mercado). |
| 321 | Gaussian Channel | `erJi1tWf` | Filtro gaussiano de 4 polos (periodo 144) do hlc3: o preco cruza o filtro para cima (ou esta acima ate 3 barras depois do cruzamento) compra; espelho vende; inverte. |
| 322 | Tres medias (SMA 7/25/99) | `sPAROdDQ` | SMA7 cruza a SMA25 para cima compra, para baixo vende; inverte (a SMA99 so desenha). |
| 323 | Babypips Inside Bar Momentum | `Y2e6lEXw` | Barra interna com a vela-mae de alta: stop de compra 10% da faixa da mae acima da maxima dela, stop de perda 20% abaixo da maxima e alvo 80% acima (espelho na mae de baixa); stop e alvo valem a partir da barra seguinte a entrada; um novo sinal cancela a ordem e fecha a posicao. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (3 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Hull MA vs Candle | 30min | h50 ambos | 2025 | +19.5% | +13.4% | 1.06 | 5.59 |
| Hull MA vs Candle | 1h | h100 ambos | 1079 | +16.4% | +13.4% | 0.91 | 2.11 |
| Hull MA vs Candle | 15min | h100 ambos | 2170 | +16.3% | +13.4% | 0.87 | 4.02 |

### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (44 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Babypips Inside Bar Momentum | 1D | tp0.8 ambos | 199 | +9.0% | +5.7% | 1.32 | -0.32 |
| Heikin Ashi Price Action | 4h | velas ambos | 1949 | +41.2% | +5.4% | 0.73 | 1.64 |
| L2 Reversal Labels | 30min | semtpsl ambos | 551 | +32.1% | +5.4% | 0.60 | 1.77 |
| Crypto Crew University (MFI/RSI/StochRSI) | 1D | th30 ambos | 32 | +20.4% | +5.7% | 0.56 | 1.72 |
| Heikin Ashi Price Action | 1D | velas ambos | 322 | +25.3% | +5.7% | 0.49 | 1.12 |
| PMax | 1D | m1.5 ambos | 52 | +22.7% | +5.7% | 0.45 | 0.87 |
| Heikin Ashi MACD | 1h | tp10 sl3 ambos | 3782 | +20.2% | +5.4% | 0.44 | 1.19 |
| L2 Reversal Labels | 1h | semtpsl ambos | 263 | +18.2% | +5.4% | 0.36 | 0.67 |
| Heikin Ashi MACD | 1D | tp10 sl3 ambos | 163 | +6.3% | +5.7% | 0.34 | 0.69 |
| Heikin Ashi Price Action | 4h | ha ambos | 1159 | +16.4% | +5.4% | 0.32 | 2.13 |

### BTC (12 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Heikin Ashi MACD | 1h | semsltp ambos | 3859 | +120.1% | +43.9% | 1.11 | 2.80 |
| Heikin Ashi MACD | 1h | tp10 sl3 ambos | 3859 | +93.7% | +43.9% | 1.04 | 3.41 |
| Moving Average (BiznesFilosof) | 1D | sma50 ambos | 131 | +69.0% | +43.8% | 0.74 | 3.08 |
| RCI | 1h | rci30 ambos | 3308 | +58.7% | +43.9% | 0.67 | 1.55 |
| Heikin Ashi Price Action | 4h | velas ambos | 1545 | +55.4% | +43.7% | 0.60 | 1.34 |
| Tres medias (SMA 7/25/99) | 1D | 7/99 ambos | 30 | +45.5% | +43.8% | 0.58 | 1.51 |
| FX Sniper T3-CCI | 1D | cci50 ambos | 77 | +49.9% | +43.8% | 0.55 | 3.17 |
| Tres medias (SMA 7/25/99) | 4h | 7/99 ambos | 269 | +50.1% | +43.7% | 0.55 | 2.70 |
| Hull MA vs Candle | 1h | h100 ambos | 1445 | +47.8% | +43.9% | 0.53 | 1.12 |
| Tres medias (SMA 7/25/99) | 1h | 7/25 ambos | 2993 | +46.5% | +43.9% | 0.53 | 1.35 |

### ETH (58 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Golden Vector Trend Orchestrator | 4h | adx25 long | 82 | +64.2% | +56.6% | 1.50 | 2.58 |
| Golden Vector Trend Orchestrator | 4h | adx0 long | 100 | +63.8% | +56.6% | 1.26 | 1.56 |
| Heikin Ashi MACD | 1h | semsltp ambos | 3789 | +168.6% | +56.8% | 1.09 | 4.03 |
| PMax | 4h | m3 long | 72 | +66.9% | +56.6% | 1.08 | 2.29 |
| Bollinger Breakout (long-only, stop) | 15min | bb50 banda | 1930 | +92.5% | +56.8% | 1.05 | 1.27 |
| Bollinger Breakout (long-only, stop) | 15min | bb50 8% | 1930 | +90.5% | +56.8% | 1.03 | 1.42 |
| Golden Vector Trend Orchestrator | 30min | adx0 long | 842 | +62.5% | +56.8% | 0.99 | 1.44 |
| Bollinger Breakout (long-only, stop) | 1D | bb20 banda | 41 | +59.8% | +56.5% | 0.96 | 1.58 |
| Bitcoin SuperFlip | 1D | f3 ambos | 30 | +66.2% | +56.5% | 0.96 | 2.77 |
| Bollinger Breakout (long-only, stop) | 30min | bb20 8% | 2448 | +84.5% | +56.8% | 0.96 | 0.54 |

## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| BTC | Heikin Ashi MACD 1h tp10 sl3 (padrão) | +154% vs +130% | +99% vs +15% | +49% vs +14% | +70% vs +40% | +63% vs +44% | **aprovada** |
| BTC | Heikin Ashi MACD 1h sem SL/TP | +359% vs +130% | +75% | +35% | +57% | +85% | **aprovada** (variante) |
| WTI | HA Price Action 4h, velas comuns, ambos | +38% vs −21% | +41,0% vs +39,7% | +39% vs +8% | +35% vs +3% | +25% vs +5% | **aprovada** (terço 2 por pouco) |
| ETH | Heikin Ashi MACD 1h sem SL/TP | +256% vs +330% | +90% vs +1% | +176% vs −11% | +143% vs +13% | +127% | quase (terço 1) |
| ETH | GVTO 4h long | +118% vs +328% | +40% | +37% | +37% | +64% | quase (terço 1) |
| ETH | Bollinger Breakout stop 15m bb50 | +274% vs +330% | +39% | +33% | +43% | +77% | quase (terço 1) |
| ETH | PMax 4h long | +233% vs +328% | +27% | +3% vs −11% | +20% vs +13% | +66% | quase (terço 1) |
| BTC | Moving Average 1D sma50 | +176% vs +129% | +16,5% vs +15,1% | +24% vs +14% | +38,7% vs +39,2% | +68% | quase (2ª metade por 0,5 p.p.) |
| BTC | Três médias 4h 7/99 | +47% vs +129% | +44% | +40% | +46% vs +40% | +48% | quase (terço 1) |
| WTI | L2 Reversal 30m sem TP/SL | +65% vs −19% | +32% vs +35% | +4% vs +8% | −0% vs +3% | +28% | não |
| XAU | Hull MA vs Candle 30m h50 | +21% vs +9% | −5% vs +5% | +50% vs +32% | +27% vs +25% | +8% vs +13% | não |
| XAU | Hull MA vs Candle 15m h100 | +23% | −8% | +38% | +19% vs +25% | +5% | não |

US100 não teve nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: Heikin Ashi MACD no BTC 1h** (configuração padrão, alvo 10% e stop 3%, comprado e vendido). +94% a.a. vs +44%, t = 3,4, 571 trades/ano; bate o B&H nos três terços, na 2ª metade (+70% vs +40%) e com custo 4× (+63%). Sem SL/TP também passa (+120% a.a.). Ressalvas: muitos trades por ano, então depende de custo baixo; DD alto; no ETH a mesma regra fica "quase" (perde só o 1º terço).
- **Aprovada: HA Price Action no WTI 4h**, mas na variante com velas comuns e os dois lados (o original é Heikin Ashi e só comprado). +41% a.a. vs +5%, t = 1,6, 200 trades/ano; passa em tudo, mas o 2º terço por 1,3 p.p. É a primeira aprovada do WTI nos lotes recentes; o t baixo pede cautela.
- ETH: mais quatro "quase" que só perdem o 1º terço (HA MACD, GVTO, Bollinger Breakout e PMax). BTC: Moving Average 1D empata na 2ª metade.
- XAU teve células acima do B&H, mas nenhuma passou. US100 não teve nada.
