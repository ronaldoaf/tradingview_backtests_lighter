# Lote 15 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote15.py` (grade) e `scripts/study_tvlote15_rob.py` (robustez). Resultados: `results/study_tvlote15*_{ativo}.txt` e `_grid.csv`.

Três scripts da lista foram ignorados por serem template ou utilitário: Fixed Percent Stop Loss & Take Profit % (`00WHGEoc`, exemplo de SL/TP), Autoview Build-a-bot (`iVHq4EFG`, modelo de automação) e AUTOMATIC GRID BOT (`6qZpzElZ`, grade com faixa de preço manual). Os substitutos foram os próximos da lista.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 79 | [RS] Spot/Binary Scalper V0 | `PMqutqKQ` | vela atravessa a Tenkan(7) com DI > 20; sessão 04-15 (UTC aqui); TP/SL de 200/150 ticks virou % na proporção 4:3 |
| 80 | Simple profitable trading strategy (Combined) | `QoNKoXwW` | fita de EMAs 8-55 alinhada + RSI e Stoch dentro da faixa; sai com EMA13 x EMA55 ou extremo de RSI/Stoch |
| 81 | Fixed Percent SL/TP | `00WHGEoc` | ignorado (exemplo) |
| 82 | Trendline Breaks with Multi Fibonacci Supertrend (TMFS) | `aVzNdTMg` | rompimento de linha de tendência de pivô + DI + close do lado da EMA21 da média de 3 SuperTrends; stop 8×ATR13, alvo 1% (trailing tratado como saída no alvo) |
| 83 | Autoview Build-a-bot | `iVHq4EFG` | ignorado (template) |
| 84 | AUTOMATIC GRID BOT | `6qZpzElZ` | ignorado (utilitário) |
| 85 | Crypto BOT lower timeframes (EMA STOCH) | `IS7yz9s4` | toque na EMA50 nas últimas 5 barras + EMA50 vs EMA100 + Stoch(5) saindo do extremo + MACD; TP/SL 10% |
| 86 | BTC bot | `DPBeZbMP` | cc = 3·RSI21 − 2·EMA21(RSI) cruza 0; sai no R3 do pivô semanal anterior; stop 15%, alvo único (o script usa 4 alvos parciais) |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| BTC bot | BTC | 27 | 7 | 0 | 0 | +5.8% (4h sl15% tp5% long) | +43.8% |
| BTC bot | ETH | 27 | 5 | 0 | 0 | -0.5% (1D sl15% tp3% ambos) | +56.8% |
| BTC bot | US100 | 27 | 22 | 0 | 0 | +17.2% (1h sl15% tp10% long) | +20.3% |
| BTC bot | WTI | 27 | 0 | 0 | 0 | -0.6% (1D sl15% tp3% ambos) | +5.4% |
| BTC bot | XAU | 27 | 10 | 2 | 0 | +4.5% (1D sl15% tp3% ambos) | +13.4% |
| Combined Strategy | BTC | 20 | 20 | 0 | 0 | +36.4% (4h so EMAs ambos) | +43.8% |
| Combined Strategy | ETH | 20 | 20 | 3 | 4 | +88.8% (15min so EMAs ambos) | +56.8% |
| Combined Strategy | US100 | 20 | 13 | 1 | 0 | +12.9% (15min so EMAs long) | +20.3% |
| Combined Strategy | WTI | 20 | 5 | 0 | 3 | +13.6% (30min so EMAs ambos) | +5.4% |
| Combined Strategy | XAU | 20 | 15 | 3 | 0 | +9.1% (30min so EMAs ambos) | +13.4% |
| EMA STOCH | BTC | 18 | 8 | 0 | 0 | +8.4% (1h sl/tp10% ambos) | +43.8% |
| EMA STOCH | ETH | 18 | 12 | 0 | 0 | +19.3% (30min sl/tp10% ambos) | +56.8% |
| EMA STOCH | US100 | 18 | 15 | 0 | 0 | +11.4% (30min sl/tp10% ambos) | +20.3% |
| EMA STOCH | WTI | 18 | 6 | 0 | 0 | +3.8% (1h sl/tp10% ambos) | +5.4% |
| EMA STOCH | XAU | 18 | 12 | 0 | 0 | +5.0% (30min sl/tp10% ambos) | +13.4% |
| Spot/Binary Scalper | BTC | 76 | 62 | 18 | 0 | +38.5% (30min sl2.00% 24h ambos) | +43.8% |
| Spot/Binary Scalper | ETH | 76 | 64 | 16 | 3 | +85.5% (30min sl2.00% sessao ambos) | +56.8% |
| Spot/Binary Scalper | US100 | 76 | 52 | 23 | 0 | +13.1% (1h sl2.00% 24h ambos) | +20.3% |
| Spot/Binary Scalper | WTI | 76 | 4 | 0 | 1 | +8.9% (1h sl2.00% 24h ambos) | +5.4% |
| Spot/Binary Scalper | XAU | 76 | 28 | 10 | 2 | +14.8% (30min sl1.00% sessao ambos) | +13.4% |
| TMFS | BTC | 60 | 51 | 13 | 0 | +38.2% (4h sw20 sl8atr tp0% ambos) | +43.8% |
| TMFS | ETH | 60 | 53 | 17 | 3 | +100.2% (4h sw20 sl8atr tp0% ambos) | +56.8% |
| TMFS | US100 | 60 | 54 | 8 | 0 | +10.3% (30min sw20 sl8atr tp3% ambos) | +20.3% |
| TMFS | WTI | 60 | 19 | 1 | 8 | +22.0% (30min sw20 sl8atr tp0% ambos) | +5.4% |
| TMFS | XAU | 60 | 43 | 11 | 0 | +11.6% (4h sw8 sl8atr tp0% ambos) | +13.4% |
BTC e US100: nenhuma célula acima do B&H. EMA STOCH e BTC bot reprovam em todos os ativos.

## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | Veredito |
|---|---|---|---|---|---|---|
| ETH TMFS 4h sw20 sem alvo | +100% | +295/+63/+16% (+328/+0,3/−11%) | +27% (+13%) | +98% | −65% | quase: perde no 1º terço; t baixo nos terços |
| ETH TMFS 1h sw8 sem alvo | +83% | +156/+56/+54% | +47% | +69% | −67% | quase: perde no 1º terço |
| ETH Combined 15m só EMAs | +89% | +201/+50/+46% | +37% | +58% (≈ B&H) | −85% | reprova: custo 4× empata |
| ETH Spot/Binary 30m 2% 24h | +82% | +81/+57/+113% | +58% | +32% (abaixo) | −79% | reprova: custo |
| WTI TMFS 30m sw20 | +22% | +23/+49/−0,6% (−19/+35/+8%) | +6% (+3%) | +8% | −69% | reprova: último terço negativo |
| XAU Spot/Binary 30m 1% sessão | +14,8% | +14,5/+10,4/+19,2% (+8,5/+4,7/+31,5%) | +13% (+25%) | −1,6% | −22% | reprova: custo 2× e 2ª metade |

## Veredito

Nenhuma aprovada. O melhor do lote é o TMFS no ETH 4h, sem alvo (só stop de 8×ATR e saída na EMA): +100% a.a. e resistente a custo, mas perde para o B&H na alta de 2020-22, como as outras "quase" do ETH.
