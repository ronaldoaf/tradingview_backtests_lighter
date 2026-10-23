# Lote 26 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote26.py` (grade) e `scripts/study_tvlote26_rob.py` (robustez). Resultados: `results/study_tvlote26_{ativo}.txt`, `_grid.csv` e `results/study_tvlote26_rob_{ativo}.txt`. A grade voltou ao tamanho dos lotes 21 a 24: o padrão do script mais 4 combinações (dois valores de parâmetro e, quando faz sentido, comprado e vendido vs só comprado), em 15m, 30m, 1h, 4h e 1D (só intradiário nas estratégias de sessão diária).

**Puladas na ordem da lista (32):**
- **Olha o futuro ou `security` em Pine antigo:** SMI (`YyNeevML`, Pine v2), Heikin Ashi v3 (`z1WjikI3`), `KafnxzJR` (`security` diário em 305 linhas), Kitchen (`T2juFbHt`, 4 `security`), `Yal3QxFW` (Pine v2), `FeoUBe91` (vários TFs via `security`) e `T85iFvQj` (lookahead_on).
- **Página que não baixou (404):** `3kMUl7fJ`.
- **Templates, exemplos ou bots:** 3Commas DCA (`Txo3OEBa` e `zaMgoLFt`), `nSgePqla` (template), `hoCPm5UY` (exemplo de tamanho de posição), `0KrB3hnV` (template de trailing), `a5CmxEJq` (exemplo de ordens pendentes nas BB) e `MIi3WUU2` (não gera ordens).
- **Duplicada:** Pivot Point SuperTrend (`WpJ5ym7u`), já testada e aprovada antes.
- **Sessão de bolsa específica:** ICT 10AM FVG (`Za5HKgrL`, NY), `8hZoUlTI` (sessão das 9h) e `3BFuBf4F` (SPY 5min).
- **Piramidação ou TPs parciais:** LuxAlgo SMC (`mEHJ2lCm`), `0Blrq2NA`, `BWHP25CQ`, Double Supertrend (`RyY2VKLD`, pirâmide de 10) e `OUzp2NR6` (saídas parciais).
- **Complexas demais para reproduzir com fidelidade:** Boom Hunter (`McuqT8px`, 254 linhas com HTF), `f09TPuYj` (2.056 linhas), `SUKIoh1K` (985 linhas), SMC Uncle Sam (`KUeL7SY5`, 325 linhas), All-in-One (`6vHRkdsf`, 362 linhas), NNFX (`XnvfXLPF`, SL/TP absolutos de forex), `IRCgOETG` (281 linhas, vários modos de saída), `itKnLY6I` (222 linhas) e X48 (`nt3wgHEc`).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 264 | 5 EMA | `EaZHR7q6` | A ultima barra toda abaixo da EMA5 marca a maxima de gatilho (toda acima marca a minima); rompeu -> entra se estiver fora; stop na menor minima das 2 ultimas barras (maior maxima no short), alvo 1,5R. O limite de 4 trades por dia foi ignorado. |
| 265 | Vegas SuperTrend Enhanced | `ec57c7xL` | SuperTrend no hlc3 com ATR10 e multiplicador base + base x (2 x desvio100 / media100); sempre na direcao. |
| 266 | Crypto Squeeze | `I3YaZmDO` | BlueWave = linreg(close - media(media(maxima20, minima20), SMA20), 20); fluxo = (MFI(hlc3) - 50) x 3. BlueWave cruza 0 para cima com fluxo > 0 compra, espelho vende, inverte. SL/TP de 50% (na pratica nenhum). |
| 267 | MACD + EMA (long-only) | `o97VVZNr` | So long: MACD acima do sinal compra (abaixo da SMA200 exige close > EMA20); sai com MACD abaixo do sinal (acima da SMA200 exige close < EMA20). |
| 268 | SuperTrend STRATEGY | `VLRj2sG9` | SuperTrend no hl2 com ATR = SMA(TR, 10) e multiplicador 8,5; o original so compra na virada para cima e fecha na virada para baixo. |
| 269 | B-Xtrender | `uCWPAPT2` | curto = RSI15(EMA5 - EMA20) - 50, longo = RSI15(EMA20) - 50. Os dois > 0 com close > EMA200 compra; sai quando qualquer um fica < 0 ou o close recua 20% do maior close (espelho no short). |
| 270 | Hull + Ichimoku + MACD | `jSXWoUXz` | Hull duplo (12) contra o mesmo Hull um candle atras, Ichimoku 9/24/51 com nuvem deslocada 23 e MACD 12/24/9; entradas e fechamentos com as condicoes do script, inverte. |
| 271 | QuantCat Intraday | `68EaMFyt` | SMA25/SMA100 com no maximo 10 cruzamentos do close na SMA25 em 25 barras: cruzamento das medias (agressivo) ou recuo entre elas (conservador) entra, inverte; stop fixo de 4 ATR14 a partir da entrada. |
| 272 | KSR (EMA 10/20) | `N2c1PkLs` | EMA10 cruza a EMA20: compra/vende, inverte (os security do script so desenham). |
| 273 | KAMA Strategy (long-only) | `h8cfMnVH` | So long: delta da KAMA(14, 2, 20) > 0 e maior que 1 desvio(14) do delta compra; delta < 0 e |delta| maior que 0,5 desvio vende. atrs: stop movel de 3 ATR14 pela maxima (opcao do script). |
| 274 | NSDT HAMA (EMA55) | `B4dBAINf` | EMA55 subindo 2 barras seguidas compra, caindo 2 vende, inverte (ADX > 0 nao filtra; a janela de 2022 foi ignorada). |
| 275 | RSI Crossover | `ZINSYeR8` | RSI50 cruza acima da sua SMA25 compra, abaixo fecha (o original so compra; ambos inverte). |
| 276 | Previous Day High/Low Breakout | `dn6ogsKO` | Maxima cruza a maxima do dia anterior compra, minima cruza a minima anterior vende, inverte (src=close: usa o close nos dois cruzamentos). |
| 277 | MACD, RSI & RVOL (long-only) | `7GmXKfig` | So long: 2 de 3 entre RSI14 cruza acima de 30, delta do MACD cruza 0 para cima e RVOL14 cruza acima de 2 compra; 2 de 3 entre RSI cruza abaixo de 70, delta cruza 0 para baixo e RVOL cruza abaixo de 5 fecha. |
| 278 | Dual Moving Average (angulo) | `WEALnfiN` | SMA8 x SMA21 nas ultimas 15 barras e angulo da SMA21 (2 barras, normalizado pelo ATR10) acima de 7 graus compra; espelho vende; inverte. |
| 279 | Pivot Point Reversal + RSI | `3UcIwSrE` | Pivos (3, 3): stop de compra 1 tick acima do ultimo topo enquanto nao rompido e com RSI14 de 3 barras atras < 70; stop de venda abaixo do ultimo fundo com RSI > 30; inverte. |
| 280 | Kozlod Heikin-Ashi | `eHfnBW5S` | Heikin-Ashi vira verde compra, vira vermelho vende, inverte (k=2: exige 2 velas da nova cor). |
| 281 | DEMA + MACD | `xeqJN1KH` | Close acima da DEMA21 fica comprado, abaixo vendido (o controle por MACD vem desligado). |
| 282 | London BreakOut Classic | `Fh42LHOM` | Faixa de Toquio 00:00-06:55 UTC; das 07:00 as 16:00 UTC, maxima >= topo da faixa compra e minima <= fundo vende, uma vez por dia; stop no meio da faixa, alvo 1R; fecha na barra das 00h. |
| 283 | Triple CCI + MFI (long-only) | `PETNavGq` | So long: CCI14(hlc3) cruza 0 para cima, close > EMA50, CCI25 e CCI50 > 0 e MFI14 > 50; stop entrada - 1,75 ATR14; depois que a maxima passa entrada + 2,25 ATR, sai com close abaixo da EMA20. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (2 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Pivot Point Reversal + RSI | 1h | pv6/3 ambos | 1523 | +16.3% | +13.4% | 0.90 | 2.74 |
| Dual Moving Average (angulo) | 1h | a7 ambos | 756 | +14.0% | +13.4% | 0.79 | 2.24 |

### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (32 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Crypto Squeeze | 1D | mfi14 ambos | 59 | +27.4% | +5.7% | 0.68 | 2.12 |
| Vegas SuperTrend Enhanced | 15min | b5 ambos | 3061 | +22.7% | +5.4% | 0.44 | 1.35 |
| 5 EMA | 4h | rr1.5 ambos | 1331 | +21.4% | +5.4% | 0.42 | 1.41 |
| SuperTrend STRATEGY | 1D | m3 ambos | 64 | +17.9% | +5.7% | 0.35 | 0.64 |
| Dual Moving Average (angulo) | 1D | a7 ambos | 43 | +16.7% | +5.7% | 0.34 | 0.50 |
| Kozlod Heikin-Ashi | 4h | k1 ambos | 3597 | +17.1% | +5.4% | 0.34 | 0.38 |
| SuperTrend STRATEGY | 1h | m3 ambos | 1910 | +17.1% | +5.4% | 0.33 | 1.74 |
| Vegas SuperTrend Enhanced | 1h | b2 ambos | 2622 | +16.7% | +5.4% | 0.32 | 1.00 |
| KSR (EMA 10/20) | 1h | 10/20 ambos | 2358 | +15.7% | +5.4% | 0.31 | 1.27 |
| NSDT HAMA (EMA55) | 4h | e55 ambos | 619 | +14.7% | +5.4% | 0.29 | 0.83 |

### BTC (23 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| DEMA + MACD | 4h | d50 long | 779 | +45.7% | +43.7% | 0.92 | 1.62 |
| Hull + Ichimoku + MACD | 1D | h30 ambos | 100 | +47.0% | +43.8% | 0.84 | 2.00 |
| DEMA + MACD | 4h | d50 ambos | 1558 | +64.4% | +43.7% | 0.68 | 1.51 |
| DEMA + MACD | 1D | d50 ambos | 217 | +58.1% | +43.8% | 0.62 | 2.13 |
| Vegas SuperTrend Enhanced | 1D | b5 ambos | 59 | +57.0% | +43.8% | 0.62 | 0.65 |
| QuantCat Intraday | 4h | atr4 ambos | 182 | +55.0% | +43.7% | 0.62 | 1.46 |
| KSR (EMA 10/20) | 1D | 10/20 ambos | 93 | +55.6% | +43.8% | 0.61 | 1.99 |
| Pivot Point Reversal + RSI | 1D | pv6/3 ambos | 78 | +55.0% | +43.8% | 0.60 | 2.28 |
| QuantCat Intraday | 15min | atr4 ambos | 3404 | +52.3% | +43.8% | 0.58 | 1.76 |
| QuantCat Intraday | 4h | atr2 ambos | 252 | +49.7% | +43.7% | 0.58 | 1.83 |

### ETH (66 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Vegas SuperTrend Enhanced | 4h | b5 long | 80 | +69.6% | +56.6% | 1.14 | 2.18 |
| SuperTrend STRATEGY | 4h | m8.5 long | 38 | +70.4% | +56.6% | 1.14 | 1.62 |
| DEMA + MACD | 1D | d50 long | 130 | +74.4% | +56.5% | 1.10 | 0.17 |
| Crypto Squeeze | 4h | mfi14 ambos | 460 | +137.1% | +56.6% | 0.94 | 4.69 |
| KAMA Strategy (long-only) | 1h | f0.5 atr3 | 1506 | +62.7% | +56.8% | 0.87 | 2.11 |
| 5 EMA | 4h | rr3 ambos | 537 | +133.0% | +56.6% | 0.86 | 2.05 |
| MACD + EMA (long-only) | 4h | filtro 8/21 | 529 | +57.7% | +56.6% | 0.85 | 1.94 |
| SuperTrend STRATEGY | 4h | m8.5 ambos | 76 | +120.0% | +56.6% | 0.83 | 3.86 |
| QuantCat Intraday | 15min | atr4 ambos | 3280 | +112.8% | +56.8% | 0.79 | 2.60 |
| DEMA + MACD | 1D | d50 ambos | 260 | +117.5% | +56.5% | 0.79 | 1.27 |

## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| ETH | 5 EMA 4h rr3 ambos | +372% vs +328% | +181% vs +0% | +81% vs −11% | +59% vs +13% | +131% vs +57% | **aprovada** |
| ETH | Crypto Squeeze 4h mfi14 | +191% vs +328% | +79% vs +0% | +154% vs −11% | +100% vs +13% | +132% | quase (terço 1) |
| ETH | SuperTrend STRATEGY 4h m8.5 ambos | +286% vs +328% | +57% | +65% | +63% | +119% | quase (terço 1) |
| ETH | QuantCat 15m atr4 | +328% vs +330% | +65% | +37% | +34% | +84% | quase (terço 1, por 2 p.p.) |
| ETH | DEMA 1D d50 ambos | +191% vs +329% | +63% | +72% | +85% | +115% | quase (terço 1) |
| ETH | KAMA 1h f0.5 atr3 | +202% vs +330% | +13% | +22% | +35% | +52% vs +57% | não (terço 1 e custo) |
| ETH | Vegas SuperTrend 4h long | +275% vs +328% | +24% | −2% vs −11% | +11% vs +13% | +69% | não |
| BTC | DEMA 4h d50 long | +109% vs +129% | +29% vs +15% | +13% vs +14% | +22% vs +40% | +41% vs +44% | não |
| BTC | Hull+Ichimoku+MACD 1D h30 | +109% vs +129% | +8% vs +15% | +28% vs +14% | +19% vs +39% | +46% | não |
| BTC | QuantCat 4h atr4 | +122% vs +129% | +13% vs +15% | +49% vs +14% | +33% vs +40% | +54% | não |
| WTI | Crypto Squeeze 1D mfi14 | +44% vs −21% | +19% vs +32% | −1% vs +8% | +2% vs +3% | +27% | não |
| WTI | Vegas SuperTrend 15m b5 | +36% vs −21% | +24% vs +38% | +9% vs +8% | +3% vs +4% | +2% vs +5% | não |
| WTI | 5 EMA 4h rr1.5 | +19% vs −21% | −3% vs +40% | +6% vs +8% | +14% vs +3% | +18% | não |
| XAU | Pivot Point Reversal + RSI 1h pv6/3 | +19% vs +8% | −9% vs +5% | +46% vs +31% | +27% vs +25% | +8% vs +13% | não (terço 2 e custo) |
| XAU | Dual MA angulo 1h | +14% vs +8% | −6% vs +5% | +41% vs +31% | +23% vs +25% | +10% vs +13% | não |

US100 não teve nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: 5 EMA no ETH 4h com alvo 3R (comprado e vendido).** +133% a.a. vs +57%, t = 2,0, 80 trades/ano; bate o B&H nos três terços, na 2ª metade e com custo 4× (+131%). Ressalvas: só a variante com alvo 3R passa (com o alvo padrão de 1,5R fica em +61%, quase igual ao B&H); DD alto (−86% na marcação do estudo); fica posicionada quase o tempo todo, então é mais um seguidor de tendência do ETH, provavelmente correlacionado com as outras aprovadas do ETH.
- Cinco células do ETH só perdem o 1º terço (2020–2022, quando o B&H fez +330% a.a.): Crypto Squeeze 4h, SuperTrend STRATEGY 4h, QuantCat 15m, DEMA 1D e (com custo apertado) KAMA 1h. É o mesmo padrão dos lotes anteriores.
- BTC, WTI e XAU tiveram células acima do B&H na amostra inteira, mas nenhuma passou nos terços. US100 não teve nada.
