# Lote 38 do TradingView (último: 4 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote38.py` (grade) e `scripts/study_veredito_lote.py 38` (veredito). Resultados: `results/study_tvlote38_{ativo}_grid.csv` e `results/study_tvlote38_veredito.txt` / `.csv`. Grade: padrão do script mais 3 combinações, em 15m, 30m, 1h, 4h e 1D.

Posições 1.001 a 1.007 da lista, que termina aqui.

**Puladas:**
- `nzilXPNB` (2Mars OKX, 716 linhas com grade de ordens e TP parcial): complexa demais.
- `zi6NdAO0` (Strategy Backtesting Template): template.
- `69ZFfJ5L` (XGBoost Mini): modelo treinado por biblioteca externa a cada 50 barras.

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 464 | Robot Wealth Simple Pairs | `oqmZwvbA` | Num ativo só: close cruzando a banda de baixo da BB 20×2 compra, a de cima vende, a média zera; inverte. |
| 465 | Kijun-Sen DasanC | `UdTnzvG6` | Abre abaixo e fecha acima da Kijun 20 compra (espelho vende), só sem posição; close do outro lado sai. Lote por risco, stop e alvo em pontos fora. |
| 466 | Trailing Stop Loss | `YToR5J20` | Só long: SMA21 × SMA49; trailing de 7,5% da maior máxima conferido no fechamento. |
| 467 | SMAcross-mvr | `4j0UOOB8` | SMA10 × SMA50 da abertura; inverte. |

## Resultado

**Nenhuma entra.** Só 5 células passam no filtro barato (4 no ETH, 1 no WTI); ouro, US100 e BTC não têm nenhuma.

- **Kijun n60 ETH 1h (ambos)** passa em tudo menos correlação: 0,58 com a L25 ht3 ETH 1h.
- **SMAcross 10/50 ETH 30m** perde no último terço (−8%) e tem corr 0,72.
- As outras três falham em t ou em terços.

Como nenhuma passou contra as 34, a checagem extra contra as 5 do lote 36 e as 2 do lote 37 não foi necessária.
