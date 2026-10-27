# Lote 36 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote36.py` (grade), `scripts/study_veredito_lote.py 36` (veredito) e `scripts/study_tvlote36_corr.py` (correlação entre as que entraram). Resultados: `results/study_tvlote36_{ativo}.txt` e `_grid.csv`, `results/study_tvlote36_veredito.txt` / `.csv` e `results/study_tvlote36_corr.txt`. Grade: padrão do script mais 4 a 6 combinações, em 15m, 30m, 1h, 4h e 1D (a Candle Breakout só em 15m a 1h, porque a vela das 13:00 UTC não existe em 4h e 1D).

Posições 908 a 955 da lista. `tv_fetch.py` agora segue para o próximo script quando um dá 404, em vez de abortar o lote.

**Puladas na ordem da lista:**
- **Página que não baixou (404):** `MtvROUAk`.
- **`security` em outro TF ou outro ativo:** `miu31FHi` (lookahead_on), `gXpRI80z` (M1), `RPAgNW8h` (Pine 2), `vzWeDyXd` (diário), `P1e5S99o` (NAAIM/Quandl), `ZjjlKjxs` (semanal + VIX), `YbzbEyDY` (Heikin Ashi), `bdiMs6Zy` (lookahead_on), `0yHbGMj7` (Renko).
- **Sessão de bolsa:** `UPuf4zqJ`, `SuBXi3p8` (ICT Silver Bullet).
- **Pips, ticks ou pontos:** `GNEvvFqP` (TP/SL/trailing em pontos), `XlZ9xCNh` (pips), `k2ynWI6q` (ticks).
- **Piramidação, DCA, martingale ou TP parcial:** `iPY9JJf6` (preço médio), `f5tFaQMQ` (turtle com 4 unidades; o turtle já foi no lote 34), `MmqKTgfH` (grid/martingale), `k0yPTqHH` (TP parcial com break-even).
- **Complexas demais ou template:** `QVqti4l2` (860 linhas), `DkDNMQsn` (saídas em fases), `B3J5Ledg` (Myth-Busting), `U0AU6PJx` (máquina de estados), `Wwn7sqmI` (linhas de tendência), `UUHabgvo` (padrões de contração), `wvYrM19h` (template de webhook), `YRfaiBIW` (1.795 linhas), `OGIOgo3z` (construtor de estratégias).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 424 | Stoch RSI Crossover + EMA | `isC2RICc` | Stoch RSI 14/14/3/3 K × D, EMAs 8 > 15 > 50, MACD SMA 12/24/8 acima do sinal e abaixo de 0 (espelho no short), só sem posição; alvo 1,5 ATR11, stop 2 ATR11. |
| 425 | Kozlod BB | `D3PkU5ho` | BB 55 × 4: close cruzando a banda de baixo compra, a de cima vende; inverte. |
| 426 | Multi-Step Vegas SuperTrend | `SXtas3lS` | Supertrend em hlc3, ATR10, multiplicador 5 + 5 × largura do canal Vegas (SMA100 ± 1 desvio); sempre posicionado (TPs parciais fora). |
| 427 | Beat the market | `vrFq8cGn` | Só long: comprado com a vol de 10 abaixo do percentil 95 das últimas 100 barras. |
| 428 | Combo 123 Reversal & N Bars Down | `PmEilDJm` | Como escrito, o N Bars Down fica −1 para sempre: só vende quando o 123 dá −1, zera no resto. Variante com o 123 sozinho. |
| 429 | Pinbar | `QtCWpUWb` | Só long: pinbar de alta; alvo 2× a vela, stop na mínima menos metade do % do alvo (trailing do script trocado por alvo). |
| 430 | Trend Entry 0 (estrutura) | `W6Xttkiv` | Só long: rompimento de estrutura para cima compra, para baixo fecha. |
| 431 | RSI Alligator | `sfEGsYBL` | RSI 13 ou 5 cruzando o RSI 34 com o outro do mesmo lado; inverte; long com stop 10% e alvo 90%. |
| 432 | Super Momentum | `jjBHYafE` | CMO 9 cruzando 25 com RMIs 8/12/30 sobrevendidos compra; espelho em 75 vende e inverte (filtro de lucro mínimo ignorado). |
| 433 | RSI 2 + tendência | `Be5GdJIr` | EMA50 > EMA200, close acima da 200 e RSI2 < 10 compra (espelho > 90); trailing de 1% (em ticks no script). |
| 434 | Donchian stop entries | `ZZ0T9Wc7` | Stop de compra na máxima de 20 e de venda na mínima de 20; sempre posicionado. |
| 435 | Keltner SL/TP | `eH0FxdMp` | EMA9 ± 1 ATR19: rompimento da banda compra/vende; inverte; stop 20%, alvo 20,3%. |
| 436 | Linear Regression Channel Breakout | `diTCC7a5` | Close acima da linreg 100 das máximas compra, abaixo da das mínimas vende; volta pela mesma linha fecha. |
| 437 | Volatility Range Breakout | `2cnPhDGs` | Bandas = SMA100 de close × (1 ± vol do range de 100); rompimento entra, cruzar o meio fecha; uma unidade. |
| 438 | Multi MA Crossing (Coinrule) | `DDnx7g70` | Só long: SMA50 cruzando acima da 100 compra, SMA9 cruzando abaixo da 50 fecha. |
| 439 | ATR and T3 | `XUUH8oiL` | Só long: close acima de Supertrend 5/5, 1/1 e T3 25; hl2 abaixo de T3 × 0,95 fecha. |
| 440 | ATR Reversed (Vervoort) | `beTGXcYr` | Trailing 3,5 ATR5 ao contrário: cruzar para cima vende, para baixo compra. |
| 441 | Squeeze Momentum (LazyBear) | `G40dtEbK` | Saída do squeeze com momentum subindo, acima da EMA100, compra; momentum caindo fecha; espelho no short. 1x em vez de 8x. |
| 442 | Candle Breakout | `YJjFy8kD` | A vela das 13:00 UTC arma a caixa; o primeiro close fora dela entra, stop no outro lado, alvo 1× o risco. |
| 443 | MACD Short/Long TVIO | `X4c5lTKF` | MACD 13/19 cruzando 0 compra; MACD 11/20 cruzando 0 (1 barra de atraso) vende; inverte; short com stop 21% e alvo 20%. |

## Resultado

58 células passam no filtro barato (CAGR > 0, Sharpe ≥ B&H, t > 2). Depois de terços, 2ª metade, spread 4×, funding 0 e |corr| < 0,5 com as 34 aprovadas, 19 células entram, de 7 pares estratégia/ativo. Fico com uma por par e tiro as que se repetem entre si (corr ≥ 0,5): **5 entram**, mais uma que passa no critério mas vive do funding.

| Estratégia | Ativo | Config | CAGR (B&H) | Sharpe (B&H) | DD | t | Terços | Spread 4× | Corr máx |
|---|---|---|---|---|---:|---:|---|---:|---|
| Keltner SL/TP | ETH 4h | k2, stop 5%, os dois lados | +49,8% (+56,6%) | 1,48 (0,96) | −26% | 2,76 | +77% / +36% / +40% | +48% | +0,33 |
| Squeeze Momentum | BTC 1D | EMA100, só comprado | +20,7% (+43,8%) | 1,35 (0,91) | −13% | 3,43 | +38% / +7% / +18% | +21% | +0,38 |
| Squeeze Momentum | ETH 1D | EMA100, só comprado | +31,2% (+56,5%) | 1,25 (0,96) | −22% | 2,56 | +94% / +3% / +13% | +31% | +0,39 |
| Candle Breakout | US100 1h | 13:00 UTC, rr 1, só comprado | +14,1% (+20,3%) | 1,18 (0,93) | −19% | 2,52 | +11% / +14% / +19% | +6% | +0,16 |
| Volatility Range Breakout | BTC 1h | n100, os dois lados | +42,3% (+43,9%) | 1,18 (0,91) | −38% | 3,63 | +72% / +50% / +11% | +41% | +0,45 |

- A **Candle Breakout no US100** é a segunda aprovada no US100 (a primeira foi a Zero-Lag do lote 34) e a de menor correlação com tudo (0,16). A versão com os dois lados também entra (+16,0%, Sharpe 1,06, t 3,13). A margem de custo é pequena: com spread 4× sobra +3% a +6% a.a.
- A **Multi-Step Vegas SuperTrend no BTC 4h** (b2, os dois lados) passa no critério, mas tem corr 0,58 com a Volatility Range Breakout do BTC 1h e fica de fora.
- O **Combo 123 no WTI 30m** (+37,8%, Sharpe 1,22) passa no critério, mas só vende e sem funding cai para +1% a.a.: o ganho é o funding que o short recebe no WTI (67,7% a.a.), não o sinal. Não conto como aprovada.
- Redundantes de destaque: Keltner ETH 30m (+105%, corr 0,59), Volatility Range Breakout no ETH 15m a 1h (corr 0,53 a 0,59 com o BEST Supertrend e o Heikin Ashi T3) e Multi MA no BTC 15m (corr 0,51).
- No ouro, nada entra: o RSI 2 no 1D reprova por terço negativo e o Donchian 1h é redundante (corr 0,65 com o hap).

As próximas da lista para o lote 37 começam em `Tts2YhVP` (posição 956).
