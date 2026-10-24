# Lote 12 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote12.py`, `scripts/study_tvlote12b.py` (Zigma), `scripts/study_tvlote12_rob.py`.
Resultados: `results/study_tvlote12*_{ativo}.txt` e `_grid.csv`.

O Template Trailing Strategy (`n8bgynWl`) foi ignorado por ser template. O substituto é o Solution Zigma (`k1GLeZco`).
Aproximação do Zigma: o nível 0,5 do Fibonacci automático do 1H virou o meio da faixa das 12 últimas barras de 1H fechadas (a biblioteca AutoFiboRetrace não existe fora do TradingView). O DMI vem do 15m e o Chandelier Exit é 1×3. Séries de timeframe maior só entram depois do fechamento da barra maior.

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR, B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Acrypto | BTC | 85 | 32 | 0 | 0 | +24,4% | +43,8% |
| Acrypto | ETH | 85 | 36 | 0 | 1 | +57,9% | +56,8% |
| Acrypto | US100 | 88 | 50 | 2 | 0 | +9,4% | +20,3% |
| Acrypto | WTI | 89 | 21 | 1 | 9 | +22,4% | +5,4% |
| Acrypto | XAU | 88 | 16 | 0 | 0 | +11,8% | +13,4% |
| Powertrend | BTC | 15 | 10 | 3 | 0 | +5,5% | +43,8% |
| Powertrend | ETH | 28 | 11 | 1 | 0 | +4,2% | +56,8% |
| Powertrend | US100 | 3 | 1 | 0 | 0 | +0,5% | +20,3% |
| Powertrend | WTI | 20 | 6 | 2 | 0 | +2,5% | +5,4% |
| Simple RSI-MA | BTC | 92 | 84 | 11 | 13 | +84,6% | +43,8% |
| Simple RSI-MA | ETH | 92 | 92 | 19 | 24 | +189,1% | +56,8% |
| Simple RSI-MA | US100 | 90 | 74 | 5 | 0 | +14,7% | +20,3% |
| Simple RSI-MA | WTI | 94 | 27 | 1 | 16 | +17,8% | +5,4% |
| Simple RSI-MA | XAU | 94 | 92 | 17 | 3 | +16,5% | +13,4% |
| TK Cross | BTC | 58 | 57 | 5 | 2 | +46,4% | +43,8% |
| TK Cross | ETH | 59 | 59 | 16 | 14 | +104,0% | +56,8% |
| TK Cross | US100 | 58 | 45 | 2 | 0 | +12,8% | +20,3% |
| TK Cross | WTI | 60 | 20 | 1 | 14 | +19,2% | +5,4% |
| TK Cross | XAU | 58 | 53 | 13 | 2 | +13,8% | +13,4% |
| Solution Zigma | BTC | 100 | 78 | 1 | 0 | +22,6% | +43,8% |
| Solution Zigma | ETH | 100 | 85 | 12 | 0 | +44,8% | +56,8% |
| Solution Zigma | US100 | 100 | 74 | 19 | 0 | +11,3% | +20,3% |
| Solution Zigma | WTI | 100 | 22 | 2 | 8 | +17,2% | +5,4% |
| Solution Zigma | XAU | 100 | 29 | 5 | 0 | +8,6% | +13,4% |

Powertrend gera poucas operações; no XAU não houve célula válida.

## Robustez (terços, 2ª metade, custo 2×/4×, vizinhança)

| Célula | Resultado |
|---|---|
| ETH Simple RSI-MA 15m r10 m50 | +171% a.a.; terços +458/+80/+93% vs B&H +330/+0,7/−11%; 2ª metade +48% vs +13%; custo 4× +128%; DD −88% (log). **Passa** |
| ETH Simple RSI-MA 15m r5 m50 | +189%; terços +524/+54/+143%; 2ª metade +79% vs +13%; custo 4× +126%; DD −65%; t=+5,7. **Passa** |
| ETH RSI-MA vizinhança | 15m bom (r20 m20/m50 > +100%); 30m r10 m50 só +21%; 1h+ fraco |
| ETH TK 30m 20/60 ema200 ambos | +104%; terço do meio +33% vs +0,7%; 2ª metade +21% vs +13%; DD −97%. Frágil |
| BTC RSI-MA 15m r10 m50 | último terço +3% vs +13%; 2ª metade +12% vs +40%. Falha |
| BTC RSI-MA 30m r10 m20 / TK 4h | 2ª metade abaixo do B&H. Falha |
| XAU RSI-MA | terço do meio −3,9%; abaixo do B&H com custo 2×. Falha |
| WTI (TK 15m, RSI-MA 30m, ACR 4h, Zigma 1h) | algum terço fraco ou negativo; DD −51% a −99%. Falha |

## Veredito

Simple RSI-MA no ETH 15m é candidato, com ressalvas: o custo do ETH é estimado (não medido), o drawdown é enorme e o mesmo sinal no BTC falha no período recente. Junta-se ao Pivot Point SuperTrend (lote 4) como candidato no ETH. As demais estratégias e ativos não passam.
