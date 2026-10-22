# Lote 14 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote14.py` (grade) e `scripts/study_tvlote14_rob.py` (robustez). Resultados: `results/study_tvlote14*_{ativo}.txt` e `_grid.csv`.

O V Bottom/V Top Pattern [Misu] (`6qmzhNzi`) foi ignorado porque as ordens da estratégia estão comentadas no código publicado, então ele não opera (na prática é um indicador). O substituto é o HullMA Strategy (`qQ0MJCVL`).

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 73 | Crypto Scalper (PSAR + MACD + EMA) | `84YDnJ9V` | PSAR contra, histograma MACD contra e close do outro lado da EMA60 armam um stop no PSAR. Aqui: condição na barra anterior + virada do PSAR, ordem na abertura seguinte. TP/SL do script (long 24,5%/—, short 5,5%/3%) |
| 74 | Heikin-Ashi PSAR [QuantNomad] | `0iKy7lyG` | PSAR sobre velas Heikin-Ashi; a virada inverte a posição |
| 75 | V Bottom/V Top Pattern [Misu] | `6qmzhNzi` | ignorado (ordens comentadas) |
| 76 | Forex Master v4.0 | `AIZqyS45` | close volta para dentro da BB(20, 1,5) com ADX perdendo força; TP/SL de 500 ticks virou % (grade) |
| 77 | Delta-RSI with filters | `0OdCms2T` | derivada do polinômio de grau 3 ajustado às 50 últimas barras do RSI(21) cruza a EMA9 dela (ou o zero); inverte a posição |
| 78 | HullMA Strategy | `qQ0MJCVL` | HMA(16) subindo = comprado, senão vendido |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Crypto Scalper | BTC | 53 | 39 | 1 | 2 | +51.5% (15min e200 tp/sl sem ambos) | +43.8% |
| Crypto Scalper | ETH | 54 | 40 | 8 | 10 | +110.3% (15min e60 tp/sl default) | +56.8% |
| Crypto Scalper | US100 | 44 | 40 | 1 | 0 | +13.6% (1D e200 tp/sl default ambos) | +20.3% |
| Crypto Scalper | WTI | 45 | 14 | 0 | 6 | +28.1% (4h e200 tp/sl sem ambos) | +5.4% |
| Crypto Scalper | XAU | 44 | 43 | 5 | 0 | +12.7% (1h e60 tp/sl sim2 ambos) | +13.4% |
| Delta-RSI | BTC | 60 | 43 | 7 | 10 | +143.5% (30min r21 w100 d3 zero ambos) | +43.8% |
| Delta-RSI | ETH | 60 | 48 | 11 | 8 | +168.9% (1h r21 w50 d3 signal ambos) | +56.8% |
| Delta-RSI | US100 | 60 | 34 | 5 | 0 | +13.5% (1h r21 w50 d3 signal long) | +20.3% |
| Delta-RSI | WTI | 60 | 11 | 3 | 9 | +36.0% (4h r14 w30 d3 signal ambos) | +5.4% |
| Delta-RSI | XAU | 60 | 22 | 1 | 0 | +8.7% (1h r21 w100 d3 signal ambos) | +13.4% |
| Forex Master | BTC | 65 | 46 | 3 | 0 | +34.7% (30min bb20 1.5 sl2.0% tp2.0% ambos) | +43.8% |
| Forex Master | ETH | 65 | 30 | 0 | 0 | +27.6% (15min bb20 1.5 sl2.0% tp2.0% ambos) | +56.8% |
| Forex Master | US100 | 65 | 25 | 0 | 0 | +8.8% (15min bb20 1.5 sl2.0% tp2.0% long) | +20.3% |
| Forex Master | WTI | 65 | 16 | 1 | 7 | +16.0% (15min bb20 1.5 sl2.0% tp2.0% ambos) | +5.4% |
| Forex Master | XAU | 65 | 10 | 0 | 0 | +5.2% (1h bb20 2.0 sl2.0% tp2.0% ambos) | +13.4% |
| HA-PSAR | BTC | 30 | 22 | 0 | 0 | +31.1% (1D 0.01/0.01/0.1 ambos) | +43.8% |
| HA-PSAR | ETH | 30 | 26 | 2 | 4 | +128.2% (1D 0.005/0.005/0.05 ambos) | +56.8% |
| HA-PSAR | US100 | 30 | 19 | 1 | 0 | +15.3% (1D 0.005/0.005/0.05 ambos) | +20.3% |
| HA-PSAR | WTI | 30 | 6 | 0 | 2 | +17.5% (1D 0.005/0.005/0.05 ambos) | +5.4% |
| HA-PSAR | XAU | 30 | 20 | 3 | 1 | +14.0% (1h 0.01/0.01/0.1 ambos) | +13.4% |
| HullMA | BTC | 50 | 37 | 5 | 2 | +54.6% (1D n100 ambos) | +43.8% |
| HullMA | ETH | 50 | 42 | 9 | 8 | +150.7% (30min n100 ambos) | +56.8% |
| HullMA | US100 | 50 | 32 | 2 | 0 | +12.7% (30min n100 long) | +20.3% |
| HullMA | WTI | 50 | 8 | 1 | 5 | +22.1% (1D n100 ambos) | +5.4% |
| HullMA | XAU | 50 | 25 | 5 | 0 | +12.4% (30min n100 ambos) | +13.4% |
## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | Veredito |
|---|---|---|---|---|---|---|
| ETH Delta-RSI 30m r21 w100 zero | +168% | +232/+139/+135% (+330/+0,7/−11%) | +85% (+13%) | +126% | −76% | quase: perde no 1º terço |
| ETH Delta-RSI 1h r21 w50 sinal | +169% | +306/+125/+105% | +119% (+13%) | +120% | −83% | quase: perde no 1º terço |
| ETH HullMA 30m n100 | +151% | +335/+139/+38% | +35% (+13%) | +115% | −73% | fraco: t da 2ª metade 1,7 |
| ETH Crypto Scalper 15m padrão | +110% | +447/+2/+64% | +48% | +92% | −79% | reprova: terço do meio ≈ 0 |
| BTC Delta-RSI 30m r21 w100 zero | +144% | +435/+134/+15% (+130/+15/+13%) | +29% (+40%) | +105% | −90% | reprova: 2ª metade abaixo |
| BTC Delta-RSI 1h r21 w50 zero | +116% | +380/+51/+39% | +32% (+40%) | +84% | −107% | reprova: 2ª metade abaixo |
| BTC Delta-RSI 4h r21 w100 zero | +82% | +73/+145/+44% (1º abaixo) | +73% (+40%) | +79% | −76% | quase: perde no 1º terço |
| WTI Delta-RSI 4h r14 w30 sinal | +36% | +15/+62/+18% (−21/+40/+8%) | +32% (+2,6%) | +23% | −77% | reprova: célula isolada (vizinhos 4h em −2% a +9%) |
| XAU HA-PSAR 1h 0,01/0,1 | +14,0% | +8,7/+7,0/+30,7% (+8,4/+4,9/+31,3%) | +23% (+25%) | +4,7% | −29% | reprova: custo 2× já fica abaixo do B&H |

## Veredito

Nenhuma aprovada. O Delta-RSI é o destaque do lote: bate o B&H com folga no ETH (2022-26) e até no BTC, mas perde para o B&H no 1º terço (alta de 2020-22) no ETH, e no BTC perde na 2ª metade nas células de 30m/1h. No WTI passa nos terços, mas só numa célula isolada. Fica registrado como "quase" no ETH, mesma família de seguidor de tendência das candidatas do ETH.
