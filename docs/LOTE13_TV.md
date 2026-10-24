# Lote 13 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote13.py` (grade) e `scripts/study_tvlote13_rob.py` (robustez). Resultados: `results/study_tvlote13*_{ativo}.txt` e `_grid.csv`. Nenhuma das 5 era template ou exemplo.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 68 | Fibonacci + RSI | `Ouv7XVfc` | bandas VWMA200 ± k·stdev; RSI[1] sai de 30/70 fora da banda 1; alvo na banda 0,764; stop 0,2%. A ordem limite no close virou ordem a mercado |
| 69 | Scalping Trading System | `YotdMm0M` | close vs SMA25/EMA200 do low, dentro do Keltner, MACD 4/34 contra, Stoch 10 contra; sinal contrário inverte |
| 70 | UT Bot v5 | `2wkJx7Ix` | trailing ATR sobre o open; HMA2 do open cruza o stop. Long-only por padrão |
| 71 | Squeeze Momentum [LazyBear] | `qp9BoNyS` | entra quando o squeeze solta com momento a favor; sai quando o momento perde força. Janela de 2018 ignorada |
| 72 | Ichimoku Kinko Hyo básico | `XZcsLIEW` | TK, chikou e preço fora da nuvem; sinal contrário inverte |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Fibonacci+RSI | BTC | 223 | 42 | 0 | 0 | +11.4% (4h l50 m1.5 sl0.03 ambos) | +43.8% |
| Fibonacci+RSI | ETH | 225 | 53 | 3 | 0 | +9.9% (4h l100 m1.5 sl0.03 ambos) | +56.8% |
| Fibonacci+RSI | US100 | 221 | 69 | 4 | 0 | +4.9% (30min l100 m2.0 sl0.03 long) | +20.3% |
| Fibonacci+RSI | WTI | 233 | 47 | 0 | 2 | +6.8% (1D l50 m1.5 sl0.03 ambos) | +5.4% |
| Fibonacci+RSI | XAU | 225 | 49 | 0 | 0 | +2.1% (4h l50 m2.0 sl0.03 ambos) | +13.4% |
| Ichimoku básico | BTC | 19 | 19 | 1 | 2 | +46.9% (1D 20/60/120 ambos) | +43.8% |
| Ichimoku básico | ETH | 19 | 19 | 4 | 7 | +129.0% (30min 9/26/52 ambos) | +56.8% |
| Ichimoku básico | US100 | 19 | 18 | 0 | 0 | +13.0% (15min 20/60/120 long) | +20.3% |
| Ichimoku básico | WTI | 20 | 4 | 0 | 4 | +21.2% (15min 20/60/120 ambos) | +5.4% |
| Ichimoku básico | XAU | 19 | 19 | 2 | 0 | +11.3% (30min 20/60/120 ambos) | +13.4% |
| Scalping System | BTC | 50 | 50 | 5 | 13 | +74.0% (1D s25 e0 ambos) | +43.8% |
| Scalping System | ETH | 50 | 50 | 9 | 7 | +125.1% (30min s25 e0 ambos) | +56.8% |
| Scalping System | US100 | 49 | 41 | 2 | 0 | +17.3% (15min s25 e0 ambos) | +20.3% |
| Scalping System | WTI | 50 | 12 | 1 | 6 | +17.6% (30min s50 e0 ambos) | +5.4% |
| Scalping System | XAU | 46 | 43 | 1 | 0 | +10.0% (30min s50 e0 ambos) | +13.4% |
| Squeeze Momentum | BTC | 40 | 32 | 9 | 0 | +31.7% (1D bb14 kc20 long) | +43.8% |
| Squeeze Momentum | ETH | 40 | 33 | 5 | 0 | +39.9% (1h bb14 kc20 ambos) | +56.8% |
| Squeeze Momentum | US100 | 40 | 19 | 5 | 0 | +3.8% (1h bb14 kc16 long) | +20.3% |
| Squeeze Momentum | WTI | 40 | 6 | 1 | 4 | +10.4% (4h bb14 kc16 ambos) | +5.4% |
| Squeeze Momentum | XAU | 40 | 22 | 2 | 0 | +4.5% (1h bb20 kc16 ambos) | +13.4% |
| UT Bot v5 | BTC | 83 | 69 | 3 | 10 | +73.3% (30min a2.0 atr30 hma2 ambos) | +43.8% |
| UT Bot v5 | ETH | 84 | 77 | 7 | 11 | +131.5% (30min a5.0 atr11 hma2 ambos) | +56.8% |
| UT Bot v5 | US100 | 85 | 68 | 4 | 0 | +15.8% (1D a3.0 atr30 hma2 ambos) | +20.3% |
| UT Bot v5 | WTI | 85 | 15 | 1 | 13 | +28.7% (1D a3.0 atr30 hma2 ambos) | +5.4% |
| UT Bot v5 | XAU | 84 | 54 | 8 | 0 | +12.4% (4h a3.0 atr30 hma2 ambos) | +13.4% |
XAU e US100: nenhuma célula acima do B&H. Fibonacci+RSI e Squeeze reprovam em todos os ativos.

## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | t | Veredito |
|---|---|---|---|---|---|---|---|
| ETH UT Bot 30m a5 ATR11 ambos | +131% | +375/+95/+34% (+330/+0,7/−11%) | +26% (+13%) | +122% | −95% | 2,5 | **passa** |
| ETH Ichimoku 15m 20/60/120 ambos | +120% | +378/+5/+104% | +73% | +101% | −90% | 2,6 | **passa** (terço do meio fraco) |
| ETH Scalping 30m SMA25 sem EMA ambos | +125% | +413/+21/+78% | +47% | +98% | −91% | 2,4 | **passa** |
| ETH UT Bot 4h a5 | +91% | +285/+21/+65% (perde no 1º) | +59% | +90% | −122% | 2,0 | quase; 1º terço abaixo |
| ETH Ichimoku 30m 9/26/52 | +129% | +571/+12/+57% | +45% | +107% | −102% | 1,9 | quase; t < 2 |
| BTC Scalping 1D SMA25 | +74% | +177/+16/+38% (+129/+15/+14%) | +45% (+39%) | +74% | −97% | 1,3 | reprova: 54 trades, t baixo |
| BTC Scalping 1h SMA50 | +66% | 1º terço abaixo | +42% (+40%) | +58% | −87% | 1,7 | reprova |
| BTC UT Bot 30m a2 ATR30 | +73% | 3º terço +8% vs +13% | +39% (+40%) | +46% | −81% | 2,0 | reprova |
| WTI UT 15m / Ichimoku 15m / Scalping 30m | +18% a +21% | terço perdedor em cada | — | ≈ B&H | −90% a −137% | ~2 | reprova |

## Veredito

Três células no ETH passam em terços, 2ª metade e custo 4×: UT Bot 30m, Ichimoku 15m (20/60/120) e Scalping 30m. Entram em [APROVADAS](APROVADAS.md) como candidatas, com uma ressalva forte: todas são seguidoras de tendência sempre no mercado, e o ETH tem B&H quase zero ou negativo desde 2022. Por isso, quase qualquer regra de tendência long/short bate o B&H no ETH. São a mesma aposta (seguir tendência no ETH), não cinco vantagens independentes. Valem as ressalvas de sempre do ETH: custo estimado e drawdown de −90% (log).
