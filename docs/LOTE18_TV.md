# Lote 18 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote18.py` (grade) e `scripts/study_tvlote18_rob.py` (robustez). Resultados: `results/study_tvlote18*_{ativo}.txt` e `_grid.csv`. Nenhum script deste lote era template.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 104 | [BACKTEST] Traders Dynamic Index | `rDZ0Id1U` | RSI13 com bandas; linha rápida SMA2 x lenta SMA7, máxima acima do canal SMMA5 e vela a favor, força 1-2; sinal contrário inverte |
| 105 | Dynamic Swing Anchored VWAP STRATEGY | `gjFSGRCo` | o VWAP só desenha; comprado enquanto a máxima de 50 barras é mais recente que a mínima; long-only (alavancagem 5x ignorada) |
| 106 | [RS] Open Session Breakout Trader | `mIvVYU42` | rompimento do open da sessão ± 0,25 × ATR100 diário; sessões 04-07 e 09-13 (UTC aqui); TP/SL em % na proporção 2,5:1; martingale ignorado |
| 107 | EMA Slope Trend Follower | `TKg40Ska` | EMA9 × EMA21 da inclinação da EMA130, filtro EMA200; sai no cruzamento contrário |
| 108 | Liquidity Sweep Reversal | `GoeqO1ev` | varredura de pivô (7/7) com volume e pavio, confirmação na barra seguinte, sessão 12-16 (UTC); stop no pavio ± 1,2 ATR, alvo 1,5R; breakeven não reproduzido |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| EMA Slope | BTC | 40 | 37 | 12 | 5 | +65.1% (4h 50 9/21 filtro ambos) | +43.8% |
| EMA Slope | ETH | 40 | 38 | 16 | 8 | +85.4% (30min 130 9/21 filtro ambos) | +56.8% |
| EMA Slope | US100 | 40 | 32 | 6 | 0 | +11.7% (1h 130 9/21 semfiltro long) | +20.3% |
| EMA Slope | WTI | 40 | 13 | 0 | 11 | +21.2% (1h 50 9/21 semfiltro ambos) | +5.4% |
| EMA Slope | XAU | 40 | 25 | 3 | 0 | +11.2% (1h 50 9/21 semfiltro ambos) | +13.4% |
| Liquidity Sweep | BTC | 48 | 12 | 0 | 0 | +7.5% (1h rr1.0 vol sess ambos) | +43.8% |
| Liquidity Sweep | ETH | 48 | 4 | 0 | 0 | +8.0% (1h rr1.5 semvol 24h ambos) | +56.8% |
| Liquidity Sweep | US100 | 45 | 16 | 3 | 0 | +9.6% (30min rr3.0 semvol sess ambos) | +20.3% |
| Liquidity Sweep | WTI | 48 | 24 | 2 | 6 | +13.6% (4h rr3.0 semvol 24h ambos) | +5.4% |
| Liquidity Sweep | XAU | 48 | 23 | 2 | 0 | +4.2% (1h rr1.5 vol sess ambos) | +13.4% |
| Open Session Breakout | BTC | 51 | 26 | 0 | 0 | +14.6% (30min m0.25 sl0.50% long) | +43.8% |
| Open Session Breakout | ETH | 51 | 23 | 2 | 0 | +55.1% (30min m0.25 sl2.00% ambos) | +56.8% |
| Open Session Breakout | US100 | 51 | 18 | 1 | 0 | +7.0% (1h m0.25 sl2.00% long) | +20.3% |
| Open Session Breakout | WTI | 51 | 11 | 0 | 9 | +15.0% (30min m0.25 sl1.00% ambos) | +5.4% |
| Open Session Breakout | XAU | 51 | 32 | 1 | 0 | +8.5% (15min m0.5 sl2.00% ambos) | +13.4% |
| Swing AVWAP | BTC | 29 | 26 | 0 | 0 | +42.6% (1D prd100 ambos) | +43.8% |
| Swing AVWAP | ETH | 29 | 28 | 6 | 9 | +88.7% (1D prd50 ambos) | +56.8% |
| Swing AVWAP | US100 | 29 | 24 | 2 | 0 | +11.5% (4h prd100 long) | +20.3% |
| Swing AVWAP | WTI | 30 | 3 | 0 | 2 | +16.0% (4h prd100 ambos) | +5.4% |
| Swing AVWAP | XAU | 28 | 23 | 4 | 1 | +14.5% (1h prd20 ambos) | +13.4% |
| TDI | BTC | 30 | 21 | 1 | 2 | +48.0% (1h str1 ambos) | +43.8% |
| TDI | ETH | 30 | 25 | 1 | 2 | +121.8% (4h str1 ambos) | +56.8% |
| TDI | US100 | 30 | 18 | 2 | 0 | +12.3% (1h str2 long) | +20.3% |
| TDI | WTI | 30 | 4 | 1 | 3 | +30.4% (1h str1 ambos) | +5.4% |
| TDI | XAU | 30 | 14 | 3 | 1 | +18.5% (1h str1 ambos) | +13.4% |
US100: nenhuma célula acima do B&H. Open Session Breakout e Liquidity Sweep não chegam perto do B&H fora do WTI.

## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | Veredito |
|---|---|---|---|---|---|---|
| XAU TDI 1h força 1 | +18,5% | +8,5/+1,3/+58% (+8,4/+4,9/+31%) | +38% (+25%) | +8,8% (abaixo) | −25% | reprova: terço do meio, custo 4× e célula isolada (30m −6%, 4h +4%) |
| ETH EMA Slope 30m 130 filtro | +85% | +218/+61/+19% (+330/+0,7/−11%) | +19% (+13%) | +57% (= B&H) | −55% | reprova: custo 4× empata |
| ETH TDI 4h força 1 | +122% | +257/+100/+46% | +66% | +116% | −122% | quase: perde no 1º terço, t baixo nos terços |
| BTC EMA Slope 4h 50 filtro | +65% | +103/+79/+24% (+129/+15/+14%) | +31% (+40%) | +62% | −41% | reprova: 2ª metade abaixo |
| BTC EMA Slope 1h 50 filtro | +45% | último terço −2,7% | +12% (+40%) | +33% | −81% | reprova |
| WTI TDI 1h força 2 | +21% | último terço −5,8% | −13% | −3% | −101% | reprova |

## Veredito

Nenhuma aprovada. O TDI no ouro 1h chamou atenção (+18,5% a.a. com DD −25%), mas o ganho vem quase todo de 2024-26, empata ou perde nos dois primeiros terços e os timeframes vizinhos são negativos.
