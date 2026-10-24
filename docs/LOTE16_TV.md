# Lote 16 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote16.py` (grade) e `scripts/study_tvlote16_rob.py` (robustez). Resultados: `results/study_tvlote16*_{ativo}.txt` e `_grid.csv`.

Quatro scripts da lista foram ignorados por serem template ou utilitário: DCA Bot Long/Short (`LTcMeU50`, emulador de robô DCA do 3commas), Ultimate Strategy Template (`XIJrNXQc`), Strategy Designer (`Hp05f5Dq`, montador de estratégias) e Stepped trailing strategy example (`jjhUHcje`). Os substitutos foram os próximos da lista: EMA Cross e EDMA Scalping.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 87 | [Backtest] QQE Cross v6.0 | `H0TR67ED` | RSI14 suavizado passa de 60/40 ("XC") com filtro de direção das EMAs 21 e 84; fecha no cruzamento da banda QQE ou RSI do outro lado de 50 |
| 88 | Profit Maximizer (PMax) | `7yn5dteO` | média VAR(12) cruza o PMax (ATR10×3) + MACD, PSAR e CCI a favor; stop 1%, alvo 35% |
| 89 | AI Volume SuperTrend | `eaTIyEty` | SuperTrend (10, 3) sobre WMA por volume; o "KNN" consulta o próprio ponto, então o rótulo vira WMA20(close) > WMA100(ST) |
| 90 | DCA Bot Long/Short | `LTcMeU50` | ignorado (utilitário) |
| 91 | Ultimate Strategy Template | `XIJrNXQc` | ignorado (template) |
| 92 | Strategy Designer | `Hp05f5Dq` | ignorado (template) |
| 93 | Stepped trailing strategy example | `jjhUHcje` | ignorado (exemplo) |
| 94 | EMA Cross Strategy | `fAxX6kbm` | EMA10 × EMA20 inverte a posição |
| 95 | EDMA Scalping Strategy | `CJesxF5m` | EMA20 da fonte (high/low conforme a vela) cruza a EDMA (HMA de um "expoente" alto/baixo) |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| AI Volume SuperTrend | BTC | 58 | 58 | 5 | 1 | +51.0% (1h l20 f5 ambos) | +43.8% |
| AI Volume SuperTrend | ETH | 58 | 58 | 14 | 19 | +103.0% (4h l20 f5 ambos) | +56.8% |
| AI Volume SuperTrend | US100 | 60 | 53 | 10 | 0 | +17.4% (15min l10 f5 long) | +20.3% |
| AI Volume SuperTrend | WTI | 59 | 20 | 1 | 10 | +23.7% (15min l20 f5 ambos) | +5.4% |
| AI Volume SuperTrend | XAU | 60 | 55 | 5 | 0 | +13.3% (1h l20 f5 ambos) | +13.4% |
| EDMA Scalping | BTC | 40 | 37 | 8 | 0 | +40.3% (1D l20 e20 ambos) | +43.8% |
| EDMA Scalping | ETH | 40 | 37 | 12 | 6 | +98.6% (30min l20 e20 ambos) | +56.8% |
| EDMA Scalping | US100 | 40 | 28 | 0 | 0 | +9.4% (15min l50 e40 long) | +20.3% |
| EDMA Scalping | WTI | 40 | 19 | 1 | 20 | +64.1% (1D l20 e40 ambos) | +5.4% |
| EDMA Scalping | XAU | 40 | 31 | 11 | 1 | +14.5% (30min l50 e40 ambos) | +13.4% |
| EMA Cross | BTC | 29 | 28 | 3 | 5 | +65.6% (4h 50/200 ambos) | +43.8% |
| EMA Cross | ETH | 29 | 29 | 8 | 10 | +110.7% (15min 50/200 ambos) | +56.8% |
| EMA Cross | US100 | 28 | 24 | 2 | 0 | +13.3% (30min 20/50 long) | +20.3% |
| EMA Cross | WTI | 30 | 11 | 1 | 6 | +15.7% (1h 10/20 ambos) | +5.4% |
| EMA Cross | XAU | 29 | 26 | 1 | 0 | +12.8% (1h 10/20 ambos) | +13.4% |
| PMax | BTC | 44 | 42 | 11 | 3 | +53.9% (15min sl3% tp35% sofiltro0 ambos) | +43.8% |
| PMax | ETH | 53 | 48 | 8 | 5 | +78.2% (15min sl3% tp35% sofiltro0 ambos) | +56.8% |
| PMax | US100 | 43 | 40 | 6 | 0 | +11.8% (15min sl0% tp35% sofiltro0 ambos) | +20.3% |
| PMax | WTI | 48 | 17 | 1 | 9 | +31.1% (15min sl0% tp35% filtros ambos) | +5.4% |
| PMax | XAU | 46 | 38 | 6 | 3 | +13.5% (1h sl0% tp35% filtros ambos) | +13.4% |
| QQE Cross | BTC | 58 | 48 | 1 | 0 | +27.2% (1D XZ f5 semfil ambos) | +43.8% |
| QQE Cross | ETH | 59 | 48 | 6 | 1 | +58.7% (15min XZ f5 dfil ambos) | +56.8% |
| QQE Cross | US100 | 60 | 39 | 7 | 0 | +7.3% (1h XZ f5 semfil ambos) | +20.3% |
| QQE Cross | WTI | 58 | 16 | 1 | 5 | +29.8% (1h XZ f5 semfil ambos) | +5.4% |
| QQE Cross | XAU | 60 | 36 | 6 | 0 | +8.5% (1h XC f5 dfil ambos) | +13.4% |
US100: nenhuma célula acima do B&H.

## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | Veredito |
|---|---|---|---|---|---|---|
| ETH EDMA 30m l20 e20 | +99% | +273/+33/+47% (+330/+0,7/−11%) | +36% (+13%) | +76% | −62% | quase: perde no 1º terço |
| ETH AI Volume ST 4h l20 f5 | +103% | +210/−5,5/+73% | +64% | +102% | −88% | reprova: terço do meio negativo |
| ETH EMA Cross 15m 50/200 | +111% | +455/+38/+22% | +19% (+13%) | +98% | −90% | fraco: t da 2ª metade 0,6 |
| BTC EMA Cross 4h 50/200 | +66% | +171/+49/+11% (+129/+15/+14%) | +30% (+40%) | +65% | −92% | reprova: recente abaixo |
| BTC PMax 15m sem filtros | +47% | +118/+22/+25% | +27% (+40%) | +37% | −48% | reprova |
| WTI EDMA 1D l20 e40 | +64% | +26/+32/+62% (−21/+32/+8%) | +52% (+3%) | +64% | −73% | quase: só 53 trades, t 1,6; terço do meio empata |
| WTI EDMA 30m l50 e40 | +33% | +76/+27/+4% (−19/+35/+8%) | +14% | +24% | −96% | reprova: perde no meio e no fim |
| XAU EDMA 30m l50 e40 | +14,5% | +23/+4/+15% (+8,5/+4,7/+31,5%) | +7,5% (+25%) | +9,9% | −36% | reprova |

## Veredito

Nenhuma aprovada. Dois pontos úteis:

1. **O EMA Cross 50/200, a média móvel mais simples, também bate o B&H do ETH** (+111% a.a. no 15m). Isso confirma a ressalva das candidatas do ETH em [APROVADAS](APROVADAS.md): no ETH 2020-26 quase qualquer seguidor de tendência long/short bate o B&H. As candidatas só acrescentam algo se forem melhores que esse cruzamento simples; a RSI-MA (+171%, passa em todos os terços) e o UT Bot 30m (+131%) são, o EMA 50/200 falha na 2ª metade (t 0,6).
2. **EDMA no WTI diário** passa terços, 2ª metade e custo, e a grade tem 20 de 40 células acima do B&H no WTI. Mas são só 53 trades em 10 anos (t 1,6), então fica como "quase".
