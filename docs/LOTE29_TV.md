# Lote 29 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote29.py` (grade) e `scripts/study_tvlote29_rob.py` (robustez). Resultados: `results/study_tvlote29_{ativo}.txt`, `_grid.csv` e `results/study_tvlote29_rob_{ativo}.txt`. Mesma grade dos lotes 26 a 28: o padrão do script mais 4 combinações (dois valores de parâmetro × comprado e vendido vs só comprado), em 15m, 30m, 1h, 4h e 1D.

**Puladas na ordem da lista (52):**
- **`security` em outro TF, Pine antigo ou dados externos:** MA Candles Supertrend (`3o1JCZQL`), Myth-Busting 12 (`eg9wcYuj`), `pVPE2jc5` (Pine v2), Fibonacci Pullback (`bOcHnaiQ`), Mix1 EMA Cross (`3r7I67zE`), NVT Signal (`B0UQX9Mf`, dados on-chain), 123 Reversal High/Low (`HB5cmsDZ`), Heikin-Ashi EMA (`xI0RmZ81`), Strategy Tester EMA/SMA/RSI/MACD (`akcty6VI`), Best SuperTrend BTCUSD (`xsofIOja`), TDI Hedge (`Ad7SuWW5`), Silver Risk Management (`mzv5SGie`), `YQHVveUQ`, Range Breakout (`pEf6ohWk`), SuperTrend Screener (`j0IOCx2L`) e Crypto MVRV Z-Score (`czUjU1Zi`, dados on-chain).
- **Páginas que não baixaram (404):** `Qwy0Fi3g`, `BRDFaufy` e `M9mByw1M`.
- **Templates, ferramentas, sem ordens ou martingale:** GetTrend (`zJxxMvgk`, sem ordens), Backtest Terminal (`KQpraXem`), MT Strategy Template (`F4cmQIQW`), Pineconnector Template (`GM4rFZk3`), Risk Management Template (`yWj2AnpX`), Roulette Martingale (`QbTJycMV`) e Buy Every Tuesday (`8zGpvRaM`, padrão de calendário só no diário).
- **Duplicadas:** Turtle System racer8 (`6TnqZSoe`, Turtle já testada nos lotes 22) e QuantNomad Pivot Reversal (`wiymwK0X`, o Pivot Reversal do lote 10).
- **Sessão de bolsa ou stops em pips/pontos:** Triple EMA Scalper (`xK5UA23y`, sessões de Londres/NY e TP/SL em pips), 20/200 SMA Bot (`ZqnuKIAw`, pontos fixos), LANZ 2.0 (`YFZE9yFC`, pips) e Crossover 100 pips (`Qd1agKJX`).
- **Piramidação, grid ou TPs parciais:** BTFD 3min (`qRwx46ZQ`), `mycmqNjC`, SuperATR 7-Step (`FDYGrZVD`), McGinley T3 Flow (`Hrc7Gfqe`), Golden Pocket Band (`zXerPHbi`), `ZSJlXc15`, Hulk Grid V2 (`JDeL8FAl`), `N0nYQBlh`, LuxAlgo SMC Pro (`4AzLMpYa`), SSL Hybrid (`2it69GUx`), Grid Bot (`kbMsMwB8`), EMA cumulativeVolume (`mUKDFKzn`), Fair Value Ultimate (`W1XteW0B`), STR EMA Oscilator (`fS0O2J8J`), Flash + Minervini (`3eD3tqed`), Volume Weighted Supertrend (`wIqc0VyB`) e RS MA test (`UYfjzdfA`).
- **Complexas demais para reproduzir com fidelidade:** MACandles LinReg (`7ZmLpnJY`), Liquidity Sweep Breakout (`MN4tJCT5`), MACD+RSI com médias THMA e regressão (`b7zn25L6`), VoVix DEVMA (`sZ4986mM`, 690 linhas), ADX DMI Trend (`4aQD9gqq`, filtros de volume e trailing), Zero-Lag MA (`7kbjZ4he`, caixas desenhadas), MACD Liquidity Tracker (`7ix2EvNm`), ABCD (`20aoz32a`), Golden Trident AVWAP (`Eq4kPrrJ`), Triple EMA + RSI + ATR (`HERuuRt5`, saída em dois estágios), Only 2 Candles NVI (`Lfy24cmy`), ATR RSI v2 (`mqh6UJ9p`), Kumo Twist (`ZmQSRFQ4`, Pine v2 com funções próprias), Inside Bar w/ SL (`JeW4LqUA`), Gradient Trend Filter (`Va06tXWV`), Volume Difference Delta Cycle (`SseQ02vi`), Williams Fractals (`WVajplfL`), Pivot Percentile Trend (`XJfWHHEc`), Andean Scalping (`Fj0ldM0e`, 1.565 linhas) e Candlestick Signals (`CTQO6AL5`, dezenas de padrões).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 324 | ATR Trailing Stoploss | `NsD6sRKu` | Linha = maior (maxima - 2,5 x ATR5) de 10 barras, so atualizada quando o close passa dela subindo; close cruza a linha para cima compra, para baixo vende; inverte. |
| 325 | High/Low channel swing | `UXKktYt6` | Media de 7 medias (SMA, EMA, WMA, ALMA, SMMA, LSMA, VWMA) de 12 das maximas e das minimas: close acima da media das maximas compra, abaixo da das minimas vende; minima cruzando abaixo da media das minimas fecha o long (espelho). |
| 326 | Donchian Breakout (long-only) | `fF9nC8iP` | So long: close cruza acima da maxima de 20 anterior compra; cruza abaixo da minima de 20 anterior fecha (ext=basis: do meio do canal). |
| 327 | Chandelier Exit + ZLSMA | `QJRHUWcF` | Sobre o close Heikin Ashi: Chandelier Exit (ATR1 x 2) vira para cima com o close HA cruzando acima da ZLSMA50 compra; cruzar abaixo da ZLSMA fecha; espelho no short. |
| 328 | Breakout Scalper | `kX8dnXYH` | Nuvem = meio do canal de 13 menos meio do de 52, em ATR52: EMA3 acima do meio rapido com nuvem > 1 ATR arma stop de compra na maxima de 52; stop de saida no maior entre as minimas de 52 e 13; nuvem negativa fecha. Espelho. |
| 329 | Bollinger Bands + EMA 9 | `Ff0DNTh1` | Fora de posicao: close anterior abaixo da BB(20, 2) e vela de alta compra; alvo na EMA9 e stop na minima anterior (espelho no short). |
| 330 | PTS Golden Edge | `SD5jYZuC` | EMA3 cruza a EMA33 para cima com RSI12 > 56, HMA66 subindo e faixa de 14 barras > 0,5 ATR14 compra; espelho com RSI < 45 vende; inverte. |
| 331 | KAMA TradeDots | `rm6K3yV6` | KAMA(10, 5, 50) subindo por 10 barras seguidas compra (o padrao e so comprado); caindo por 10 fecha (ambos: vende). |
| 332 | RSI2 + medias (pullback) | `H4ciolWP` | Close acima da SMA200, close abaixo da SMA10 e RSI2 saindo de abaixo de 5 compra; close acima da SMA10 fecha. Espelho no short (RSI2 saindo de acima de 95). |
| 333 | RSI and SMA (Coinrule) | `Clpg5ju2` | SMA100 cruza a SMA150 para cima com RSI14 > 50 compra; para baixo com RSI < 50 vende; inverte. |
| 334 | Scalping against trapped countertrend | `mEJH90Q5` | Sobre o hl2: estocastico 60 suavizado (SMA13) > 50, RSI5 > 50 e RSI5 abaixo de 35 em algum momento das ultimas 15 barras compra (min dos tres > 0); espelho vende; inverte. |
| 335 | Linear Regression Channel Breakout | `7USLDe0j` | Canal de regressao linear de 20 com 2,3 desvios: close acima da banda de cima compra, abaixo da de baixo vende; inverte; alvo 11%. |
| 336 | Crossing MAs + ADX | `gHYXDzo7` | SMA20 acima da SMA120 com ADX14 >= 20 compra; abaixo vende; inverte (sem ADX forte fica como esta). |
| 337 | BotBot | `3ODyRfFl` | Close 0,1% acima da SMA19, maxima 4% acima de (minima anterior + ATR19) e vela de alta compra; espelho vende; inverte. |
| 338 | Rob Booker ADX Breakout | `qoaam9SI` | Fora de posicao, ADX14 < 18 e close cruzando a maxima de 20 anterior compra (cruzando a minima vende); alvo de 1 largura da caixa e stop de meia largura. |
| 339 | Bull and Bear Fear | `B85sdNEB` | BullFear = meio da faixa das maximas de 12, BearFear = meio da faixa das minimas: close cruza acima de BullFear compra, abaixo de BearFear vende; inverte. |
| 340 | MACD_RSI | `pjNTFYox` | Close > EMA20, MACD(12, 26) acima do sinal EMA20 e RSI14 acima da sua EMA20 compra; tudo ao contrario vende; inverte. |
| 341 | BTC WaveTrend R:R (long-only) | `P1BEGIzN` | So long: WaveTrend (10, 21) cruza o sinal para cima com WT1 < 20 compra; stop na menor minima das 3 ultimas barras e alvo de 1,5R. |
| 342 | Volume fight | `alrI0TBw` | Volume comprador vs vendedor (VWMA 11): primeira barra de zona compradora (com folga de 15% contra a zona neutra) compra, primeira de zona vendedora vende; inverte. |
| 343 | Channel Break (free bot) | `8vuKM6ZP` | Stop de compra na maxima de 13 e de venda na minima de 18; saida no meio do canal (ou no outro lado) ou no stop de 9%; o alvo de 46% foi ignorado. |

## Grade por ativo (10 melhores células acima do B&H, por Sharpe, mínimo de 30 trades)

### XAU (0 células acima do B&H)

Nenhuma célula acima do B&H.


### US100 (0 células acima do B&H)

Nenhuma célula acima do B&H.


### WTI (42 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| BotBot | 1D | k0.04 ambos | 35 | +43.3% | +5.7% | 0.79 | 1.75 |
| BotBot | 15min | k0.04 ambos | 34 | +32.0% | +5.4% | 0.78 | 2.69 |
| BotBot | 4h | k0.04 ambos | 50 | +40.4% | +5.4% | 0.76 | 0.56 |
| Volume fight | 1h | ma11 ambos | 4308 | +42.4% | +5.4% | 0.73 | 3.09 |
| PTS Golden Edge | 30min | 9/50 ambos | 1392 | +31.3% | +5.4% | 0.58 | 1.76 |
| BotBot | 30min | k0.02 ambos | 218 | +29.8% | +5.4% | 0.58 | 0.52 |
| BotBot | 1D | k0.02 ambos | 110 | +28.0% | +5.7% | 0.53 | 2.59 |
| RSI and SMA (Coinrule) | 15min | 50/100 ambos | 1510 | +25.8% | +5.4% | 0.49 | 1.83 |
| Volume fight | 1h | ma30 ambos | 780 | +24.4% | +5.4% | 0.44 | 0.94 |
| Bull and Bear Fear | 1h | n30 ambos | 2218 | +21.7% | +5.4% | 0.43 | 1.62 |

### BTC (11 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Volume fight | 1D | ma11 ambos | 57 | +68.8% | +43.8% | 0.74 | 2.41 |
| Bull and Bear Fear | 1D | n30 ambos | 89 | +60.5% | +43.8% | 0.66 | 2.28 |
| ATR Trailing Stoploss | 4h | m2.5 ambos | 1279 | +60.1% | +43.7% | 0.66 | 0.41 |
| MACD_RSI | 1D | e50 ambos | 82 | +59.5% | +43.8% | 0.64 | 2.87 |
| Crossing MAs + ADX | 1h | adx20 ambos | 617 | +52.6% | +43.9% | 0.58 | 1.86 |
| KAMA TradeDots | 15min | r5 ambos | 3986 | +51.8% | +43.8% | 0.58 | 1.34 |
| KAMA TradeDots | 15min | r10 ambos | 2474 | +51.0% | +43.8% | 0.58 | 1.67 |
| KAMA TradeDots | 4h | r5 ambos | 245 | +48.9% | +43.7% | 0.54 | 1.53 |
| RSI and SMA (Coinrule) | 15min | 50/100 ambos | 1647 | +46.6% | +43.8% | 0.53 | 1.84 |
| Scalping against trapped countertrend | 15min | ck15 ambos | 3853 | +45.0% | +43.8% | 0.53 | 1.63 |

### ETH (52 células acima do B&H)

| Estratégia | TF | Config | Trades | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|
| Linear Regression Channel Breakout | 1h | dv2.3 long | 47 | +67.3% | +56.8% | 1.73 | 3.54 |
| Linear Regression Channel Breakout | 30min | dv2.3 long | 46 | +76.3% | +56.8% | 1.65 | 2.87 |
| Linear Regression Channel Breakout | 30min | dv1.5 long | 47 | +68.2% | +56.8% | 1.45 | 2.77 |
| Linear Regression Channel Breakout | 4h | dv1.5 long | 40 | +57.7% | +56.6% | 1.32 | 2.67 |
| Linear Regression Channel Breakout | 15min | dv2.3 long | 41 | +58.1% | +56.8% | 1.30 | 3.33 |
| Linear Regression Channel Breakout | 1h | dv1.5 long | 43 | +59.8% | +56.8% | 1.29 | 1.86 |
| KAMA TradeDots | 4h | r10 long | 74 | +65.0% | +56.6% | 1.05 | 1.93 |
| KAMA TradeDots | 4h | r5 long | 129 | +61.4% | +56.6% | 0.97 | 2.72 |
| Bull and Bear Fear | 30min | n30 ambos | 4568 | +135.1% | +56.8% | 0.91 | 2.89 |
| Channel Break (free bot) | 1D | meio ambos | 164 | +67.5% | +56.5% | 0.87 | 1.39 |

## Robustez (CAGR vs B&H)

| Ativo | Célula | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| WTI | PTS Golden Edge 30m EMA 9/50 ambos | −16% vs −19% | +115% vs +35% | +32% vs +8% | +25% vs +3% | +21% vs +5% | **aprovada** |
| WTI | BotBot 1D k0.02 | +21% vs −21% | +12% vs +32% | +15% vs +8% | +12% vs +3% | +27% | quase (terço 2) |
| WTI | Volume fight 1h | +38% vs −19% | +67% vs +36% | +15% vs +8% | −6% vs +3% | +9% | não |
| BTC | Crossing MAs + ADX 1h | +104% vs +130% | +37% vs +15% | +25% vs +14% | +40,3% vs +40,3% | +49% | quase (terço 1, empata na 2ª metade) |
| BTC | Volume fight 1D | +148% vs +129% | +83% | +15% vs +14% | +31% vs +39% | +68% | não (2ª metade) |
| BTC | Bull and Bear Fear 1D n30 | +181% | +12% vs +15% | +21% | +28% vs +39% | +60% | não |
| BTC | MACD_RSI 1D e50 | +187% | +23% | −6% vs +14% | +25% vs +39% | +59% | não |
| ETH | KAMA TradeDots 4h r5 long | +204% vs +328% | +15% vs +0% | +10% vs −11% | +15% vs +13% | +60% | quase (terço 1) |
| ETH | LinReg Channel Breakout 1h/30m long | todos os trades no 1º terço | | | | | não (degenerada: só comprado, sai apenas no alvo de 11%) |

XAU e US100 não tiveram nenhuma célula acima do B&H.

## Conclusões

- **Aprovada: PTS Golden Edge no WTI 30m com EMA 9/50 (comprado e vendido).** +31% a.a. vs +5%, t = 1,8, 143 trades/ano; bate o B&H nos três terços (no 1º perde menos que o B&H: −16% vs −19%), na 2ª metade (+25% vs +3%) e com custo 4× (+21%). Ressalvas: o padrão do script (EMA 3/33) também fica acima do B&H (+18%) mas não foi testado em robustez; o 1º terço é negativo em termos absolutos; o terço 2 concentra o ganho (+115%).
- Quase: BotBot no WTI 1D, Crossing MAs + ADX no BTC 1h e KAMA TradeDots no ETH 4h.
- A LinReg Channel Breakout só comprado aparece no topo do ETH, mas é artefato da variante: sem venda, o long só sai no alvo de 11%, então fica quase sempre comprado.
- XAU e US100 não tiveram nada acima do B&H.
