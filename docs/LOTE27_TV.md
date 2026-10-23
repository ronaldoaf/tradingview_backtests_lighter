# Lote 27 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote27.py` (grade) e `scripts/study_tvlote27_rob.py` (robustez). Resultados: `results/study_tvlote27_{ativo}.txt`, `_grid.csv` e `results/study_tvlote27_rob_{ativo}.txt`. Mesma grade do lote 26: o padrão do script mais 4 combinações (dois valores de parâmetro × comprado e vendido vs só comprado), em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (45):**
- **Olha o futuro, `security` em Pine antigo ou dados externos:** VJ Gann Double Band (`dvsXy8Qi`, Pine v2), AutoView Trailing (`gONtbXRo`, Pine v2), Cueing Off S/R (`1QXfpKHE`, Pine v2), Renko Trend Reversal (`VqyhvfM0`), OCC Scalper (`ZLyHPGfK`), Hash Ribbons (`4d0HQmoy`, dados on-chain/`security`), Multi Supertrend HTF (`DrNY2LOA`), Heiken Ashi V3 (`ByphwozB`, Pine v3), HTF MACD MFI Scalper (`GOvvlTUT`), MTF Trailing SL (`pVLm0yC5`), Crypto momentum (`9cxy1Yu9`, usa CRYPTOCAP:TOTAL) e Dow Factor MFI/RSI (`UpM8dzW4`).
- **Páginas que não baixaram (404):** CCI EMA Alifer (`hHfPXUTx`) e robot whitebox shiftma (`9KvLceQ9`).
- **Templates, ferramentas ou exemplos:** Monthly Performance Table (`aHwncfep`), RSI Strategy TradingConnector (`kQY2gaLx`, o exemplo de RSI já testado), Combined Strategy (`7wrshs1q`: o Channel Breakout de exemplo domina as entradas) e Risk Reward Calculator (`GbgkGI2h`).
- **Sessão de bolsa específica:** ORB Sessions (`ErwhAFlr`).
- **Piramidação, grid, martingale ou TPs parciais:** Growth Producer (`I2oKm8nF`), OBV Pyr (`sAP5k4bs`), WOMBO COMBO (`2mVl2d9h`), Grid Spot V2 (`ZJseWDie`), Tristan's Reversal (`MmfqVjSS`, pirâmide de 10), Wunderbit BTC (`0mCr8Nfv`, TP1/TP2 parciais), VWAP and RSI (`oDnkONvx`), Big Whale (`gYGCDkW2`), RSI W Pattern (`f80Cfpfp`), inwCoin Martingale (`8OS1nbr8`) e MACD vs BB (`muzLmNwb`, pirâmide de 5).
- **Stop/alvo absoluto em ticks ou dinheiro:** FX Master EUR/USD (`Figho5B3`, 500 ticks) e TSI HMA CCI (`rjAoFt4N`, stop em dinheiro com `openprofit`).
- **Complexas demais para reproduzir com fidelidade:** Accurate BUY SELL (`jVZvCaUh`, 1.324 linhas), Enhanced OB Retest (`jsQQPsfa`, 428 linhas), `4CIWtqoT` (455 linhas), Fabio Valentini Scalper (`ybr8iE0K`, 329 linhas), Linear Regression Pearson's R (`6VHnjgfp`, canal adaptativo desenhado com linhas), Adaptive Zero Lag EMA (`Q7h83i1t`, período adaptativo e lotes de forex), 3 Line Strike (`fJEKAdgD`, 325 linhas), TrendLines (`vOyqoCwS`), Holy Grail (`emQdbShi`, simulação própria dentro do script), 2 EMA Stoch RSI ATR (`BUsgoYjm`, breakeven e pivôs do estocástico), Ichimoku + QQE (`0IY0ERtK`, dois sistemas misturados), Myth-Busting 1 (`s1ufMqI5`) e NNFX VP (`wmJpD8xR`, 342 linhas).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 284 | Doji strategy | `U3JBNJ9V` | Doji (corpo <= 5% da faixa): stop de compra na maxima (ou na maior das 2 ultimas se a vela anterior era longa e maior) e stop de venda na minima, so na barra seguinte; stop de perda fixo (200 ticks -> 1%). O alvo de 200 ticks foi ignorado. |
| 285 | Adaptive Trend Flow | `CNJ1hXQw` | Base = media de EMA2 e EMA4 do hlc3, faixa +- 2 x EMA2(desvio2); tendencia vira com o close fora da faixa. Virada para cima com close > SMA4 e MACD(2, 7, 2) acima do sinal compra; virada para baixo fecha (ambos: vende). |
| 286 | Optimized RSI Buy The Dips (long-only) | `Pm1WAtyI` | So long: RSI14 < 35 com close abaixo da SMA100 compra; RSI > 65 fecha. |
| 287 | Stochastic Trend (long-only) | `hk9a7099` | So long: %K(200) suavizado por SMA100 cruza acima de 50 compra; cruza abaixo de 60 fecha. |
| 288 | TSI CCI Hull | `MuAKk43D` | Sobre a abertura: TSI(50, 50) x 5 suavizado (EMA125) subindo, Hull25 suavizado abaixo do preco, CCI do Hull > 0 e subindo e Hull subindo compra; espelho vende; inverte. |
| 289 | Gold Scalping | `wO3Es23F` | EMA50 > EMA200, RSI14 entre 45 e 55, engolfo de alta e close > EMA50 compra (espelho vende); stop de 1 ATR14 e alvo de 20 pips do ouro (US$ 2, aqui 0,1% do preco; tpk=atr2: 2 ATR). |
| 290 | The Flash | `XKgLfo15` | EMA12 acima do seu trailing de 1% (MOST), SuperTrend(10, 3) de alta e RSI10 do momento 10 > 60 compra se estiver fora (espelho vende); sai quando o close cruza a linha do SuperTrend. |
| 291 | Volatility System (Wilder) | `pjZKWnHl` | ARC = ATR9 x 1,8; close cruza acima de (menor close de 9 + ARC) da barra anterior compra, abaixo de (maior close de 9 - ARC) vende; inverte (stop and reverse). |
| 292 | Bollinger Band Breakout (long-only) | `UHsvM5JR` | So long: close cruza acima da banda superior (BB20, 1,5) compra; cruza abaixo da inferior fecha (ext=basis: da media). |
| 293 | Simple strat (MACD + Stoch + RSI) | `pOT16FZ5` | MACD acima do sinal, %K(14, 3) > 50 e RSI14 > 50 compra (a ordem stop na maxima virou mercado); sai com MACD abaixo do sinal ou close alem de entrada - 2 ATR10 / + 6 ATR10. Espelho no short. |
| 294 | Squeeze Momentum on Reversal | `Fckzv8iH` | Momento do squeeze (linreg 20) abaixo de -forca e subindo compra, acima de +forca e caindo vende; inverte. A forca 0,0018 era em preco de forex; aqui e relativa ao close. |
| 295 | Trend Following Breakout | `vOfNuQ8n` | Close cruza acima da maxima de 100 (barra anterior) compra; fecha quando o close cruza acima da menor maxima de 50 ou na venda; short: close abaixo da minima de 100, fecha com close acima da maior minima de 50. |
| 296 | Wyckoff Range | `vQSBf9rh` | Close cruza acima da SMA32 junto com a minima cruzando acima da SMA10 das minimas compra; close abaixo da SMA35 com maxima abaixo da SMA20 das maximas vende; inverte; stop 10%. |
| 297 | Martin Pring's Special K | `CpP23CQM` | Special K (soma ponderada de 12 ROCs suavizados, de 10 a 530 barras) acima da sua SMA10 compra, abaixo vende; sempre posicionado. |
| 298 | ATR Trailing Stops | `ZPD0fN55` | Trailing de 3,5 x ATR5 sobre o close: cruzar acima compra, abaixo fecha (com shorts: inverte). |
| 299 | 3 EMA + Stoch RSI + ATR | `IhxCXn6n` | EMA8 > EMA14 > EMA50 e close > EMA8 compra (espelho vende), inverte; alvo 4 ATR14 e stop 1 ATR fixados na entrada (o filtro de Stoch RSI vem desligado). |
| 300 | Ichimoku Backtester | `fsYSuQGL` | Tenkan cruza a Kijun para cima, close acima de 26 barras atras, close acima da nuvem (deslocada 26) e nuvem verde compra; espelho vende; a entrada contraria fecha e inverte (RSI, TP e SL vem desligados). |
| 301 | SSL Channel Cross | `jds0DHEd` | Canal SSL (SMA10 das maximas e das minimas, lado pelo close fora do canal): linha de alta cruza a de baixa compra, o contrario vende; inverte. |
| 302 | Combo 2/20 EMA + AC | `Cfz1HMO1` | 2/20 EMA (EMA14; minima/maxima de 2 barras contra a media e o close anterior) e AC (SMA6 - SMA33 do hl2 menos a SMA6 disso) concordando compra ou vende; discordando, zera. |
| 303 | OBV Oscillator | `VQjItUaK` | OBV de 20 barras dividido pelo volume de 20: EMA12 cruza a EMA26 para cima compra, para baixo vende; inverte. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (3 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| TSI CCI Hull | 15min | p25 ambos | 2074 | +16.6% | +13.4% | 0.91 | 3.07 |
| Martin Pring's Special K | 1h | s10 ambos | 2300 | +13.8% | +13.4% | 0.76 | 2.65 |
| Martin Pring's Special K | 1h | s30 ambos | 1422 | +13.7% | +13.4% | 0.75 | 1.68 |

### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (34 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Gold Scalping | 4h | tp2atr ambos | 298 | +9.3% | +5.4% | 0.92 | 0.74 |
| Martin Pring's Special K | 1D | s30 ambos | 48 | +35.6% | +5.7% | 0.65 | 1.00 |
| TSI CCI Hull | 15min | p25 ambos | 2675 | +34.3% | +5.4% | 0.61 | 2.50 |
| OBV Oscillator | 1h | l20 ambos | 2709 | +30.8% | +5.4% | 0.56 | 3.59 |
| TSI CCI Hull | 15min | p50 ambos | 2853 | +31.3% | +5.4% | 0.54 | 2.19 |
| TSI CCI Hull | 30min | p50 ambos | 1400 | +22.8% | +5.4% | 0.46 | 1.55 |
| The Flash | 1D | mr50 ambos | 61 | +18.8% | +5.7% | 0.41 | 1.62 |
| Martin Pring's Special K | 1D | s10 ambos | 90 | +19.5% | +5.7% | 0.38 | 0.87 |
| Simple strat (MACD + Stoch + RSI) | 1h | tp6 sl2 ambos | 3723 | +17.7% | +5.4% | 0.38 | 1.24 |
| ATR Trailing Stops | 1D | a5x3.5 ambos | 49 | +18.5% | +5.7% | 0.37 | 0.86 |

### BTC (7 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Martin Pring's Special K | 1h | s10 long | 1536 | +46.3% | +43.9% | 0.82 | 1.24 |
| Wyckoff Range | 1h | sl10% ambos | 561 | +61.2% | +43.9% | 0.70 | 1.66 |
| Martin Pring's Special K | 1h | s10 ambos | 3072 | +66.1% | +43.9% | 0.69 | 2.44 |
| SSL Channel Cross | 1D | l50 ambos | 61 | +53.4% | +43.8% | 0.60 | 3.43 |
| Squeeze Momentum on Reversal | 15min | f0.0018 ambos | 8246 | +50.1% | +43.8% | 0.57 | 1.40 |
| SSL Channel Cross | 1h | l50 ambos | 1860 | +46.3% | +43.9% | 0.53 | 1.17 |
| Volatility System (Wilder) | 1D | arc3 ambos | 38 | +44.8% | +43.8% | 0.51 | 1.77 |

### ETH (27 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Wyckoff Range | 4h | sl3% ambos | 198 | +99.6% | +56.6% | 1.26 | 2.29 |
| Martin Pring's Special K | 30min | s30 long | 1897 | +85.6% | +56.8% | 0.97 | 2.54 |
| Wyckoff Range | 4h | sl10% ambos | 166 | +115.0% | +56.6% | 0.96 | 1.52 |
| Bollinger Band Breakout (long-only) | 1D | m1.5 lower | 37 | +61.5% | +56.5% | 0.95 | 1.08 |
| Martin Pring's Special K | 30min | s30 ambos | 3794 | +145.6% | +56.8% | 0.90 | 3.78 |
| The Flash | 30min | mr50 long | 1088 | +62.8% | +56.8% | 0.85 | 1.36 |
| SSL Channel Cross | 30min | l50 ambos | 3750 | +111.4% | +56.8% | 0.78 | 2.28 |
| Stochastic Trend (long-only) | 15min | k50/25 x50 | 2128 | +65.3% | +56.8% | 0.73 | 1.21 |
| Simple strat (MACD + Stoch + RSI) | 1h | tp3 sl1 ambos | 4953 | +77.3% | +56.8% | 0.68 | 1.83 |
| The Flash | 30min | mr50 ambos | 2118 | +76.9% | +56.8% | 0.68 | 2.35 |

## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| ETH | Wyckoff Range 4h sl3% ambos | +461% vs +328% | +23% vs +0% | +16% vs −11% | +21% vs +13% | +98% vs +57% | **aprovada** |
| ETH | Wyckoff Range 4h sl10% (padrão) | +614% | +70% | −23% vs −11% | +1% vs +13% | +114% | não |
| ETH | Special K 30m s30 ambos | +117% vs +330% | +73% vs +1% | +311% vs −11% | +212% vs +13% | +108% | quase (terço 1) |
| ETH | Special K 30m s30 long | +186% vs +330% | +24% | +81% | +77% | +71% | quase (terço 1) |
| ETH | SSL Channel 30m l50 ambos | +242% vs +330% | +70% | +48% | +48% | +79% | quase (terço 1) |
| BTC | Special K 1h s10 ambos | +101% vs +130% | +159% vs +15% | −13% vs +14% | +20% vs +40% | +45% | não |
| BTC | Wyckoff 1h sl10% | +361% vs +130% | +18% vs +15% | −17% vs +14% | −11% vs +40% | +57% | não |
| BTC | SSL Channel 1D l50 | +126% vs +129% | +19% vs +15% | +17% vs +14% | +29% vs +39% | +53% | não |
| WTI | TSI CCI Hull 15m p25 | +8% vs −21% | +93% vs +38% | +7,4% vs +7,8% | +13% vs +4% | +14% vs +5% | quase (terço 3 por 0,4 p.p.) |
| WTI | OBV Oscillator 1h | +32% vs −19% | +66% vs +36% | +1% vs +8% | +8% vs +3% | +11% | não (terço 3) |
| WTI | Special K 1D s30 | poucos trades | | | +40% vs +3% | +35% | inconclusivo (48 trades) |
| WTI | Gold Scalping 4h tp2atr | +6% vs −21% | +25% vs +40% | −1% vs +8% | −1% vs +3% | +7% | não |
| XAU | TSI CCI Hull 15m p25 | +5% vs +8% | +3% vs +5% | +54% vs +31% | +35% vs +25% | +5% vs +13% | não |
| XAU | Special K 1h s10 | +8% vs +8% | −7% vs +5% | +47% vs +31% | +25% vs +25% | +2% vs +13% | não |

US100 não teve nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: Wyckoff Range no ETH 4h com stop de 3% (comprado e vendido).** +100% a.a. vs +57%, t = 2,3, 29 trades/ano, exposição 53%; bate o B&H nos três terços, na 2ª metade (+21% vs +13%) e com custo 4× (+98%). Ressalvas: o stop padrão de 10% falha no 3º terço e na 2ª metade, então o resultado depende do stop apertado; o 1º terço (2020–2022) carrega boa parte do ganho; poucos trades por ano.
- Special K e SSL Channel no ETH 30m só perdem o 1º terço, o mesmo padrão dos seguidores de tendência dos lotes anteriores. O Special K 30m s30 tem 2ª metade muito forte (+212% vs +13%) e merece acompanhamento.
- TSI CCI Hull no WTI 15m perde o 3º terço por 0,4 p.p. e sofre com custo (+14% com 4×).
- BTC e XAU tiveram células acima do B&H na amostra toda, mas nenhuma passou nos terços. US100 não teve nada.
