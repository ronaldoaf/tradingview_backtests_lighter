# Cruzamento de médias móveis no 4h: 8 tipos × 3 pares, carteira de 5 ativos (2020–2023)

**Resposta curta:** nenhuma das 24 configurações bate o buy&hold sem funding (Sharpe 1,03) e nenhuma é estatisticamente
significativa (maior t = 1,5). A melhor é **T3 200/50** (CAGR +14,7%, Sharpe 0,76, DD −26%), mas 2020 sozinho dá +62% e
os outros três anos somam quase zero; ela ganha no BTC (+58% a.a.) e perde no ouro e na prata. Só 3 de 24 configurações
são positivas em ≥ 3 anos **e** ≥ 3 ativos ao mesmo tempo (T3, ALMA e KAMA, todas 200/50).
Com 24 tentativas, o Sharpe máximo esperado por sorte num período de 4 anos fica em torno de 1,0, então 0,76 é ruído.
Por tipo, T3 e VIDYA são as menos ruins; HMA e ZLEMA (as "sem atraso") são as piores, viram demais e pagam o vai-e-vem.
O par lento 200/50 é o melhor em média; 50/20 é o pior.

Pela mesma métrica, a EMA 50×200 simples dá CAGR +11,6% e Sharpe 0,59, ou seja, as médias "sofisticadas" não acrescentam
nada claro sobre a média exponencial comum.

## Método
- BTC (Binance 1m), WTI, US100, XAU, XAG (Dukascopy 1m) reamostrados para 4h; dados cortados em 31/12/2023 antes de
  qualquer cálculo. 2024+ não foi usado.
- Sempre posicionado: long se rápida > lenta, short se rápida < lenta (vira no cruzamento). Sinal no fechamento,
  execução na abertura da barra seguinte. Mesma configuração nos 5 ativos.
- Custos: spread da Lighter por perna (virada = 2 pernas) e funding anual pro-rata (long paga, short recebe), os mesmos
  `CUSTO`/`FUND` do repo; XAG usa os do ouro. A última coluna mostra o CAGR sem funding.
- Carteira 20% por ativo a 1x, média dos retornos diários. Sharpe/vol com 365 dias, t = média/desvio × √n diário.
- Parâmetros das médias (padrões do TradingView): KAMA rápida 2/lenta 30 com ER no período; ALMA offset 0,85 sigma 6;
  ZLEMA lag (n−1)/2; T3 fator 0,7; FRAMA de Ehlers (alfa = exp(−4,6·(D−1)), entre 0,01 e 1); VIDYA com CMO de 9;
  McGinley `md + (c−md)/(n·(c/md)^4)`.
- Buy&hold de referência: com o funding da Lighter (WTI 67,7% a.a. destrói o long) CAGR +0,9%, Sharpe 0,16;
  sem funding CAGR +25,8%, Sharpe 1,03, DD −34%.

## Ranking (por Sharpe)

| # | Config | CAGR | Vol | Sharpe | DD | t | 2020 | 2021 | 2022 | 2023 | BTC | WTI | US100 | XAU | XAG | Viradas | CAGR s/ funding |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | T3 200/50 | +15% | 21% | 0.76 | -26% | 1.52 | +62% | -5% | +10% | +1% | +58% | +9% | +1% | -17% | -5% | 149 | +15% |
| 2 | VIDYA 50/20 | +13% | 24% | 0.65 | -20% | 1.30 | +59% | -1% | +2% | +3% | +55% | -2% | +2% | -3% | -15% | 208 | +16% |
| 3 | ALMA 200/50 | +13% | 23% | 0.64 | -23% | 1.28 | +48% | +12% | -11% | +10% | +10% | -8% | +9% | +1% | +10% | 444 | +16% |
| 4 | MDMA 50/20 | +11% | 23% | 0.58 | -31% | 1.17 | +63% | +21% | -18% | -4% | +44% | -15% | +2% | -4% | -2% | 281 | +17% |
| 5 | KAMA 200/50 | +10% | 22% | 0.54 | -32% | 1.08 | +53% | +11% | -18% | +6% | +13% | +1% | +3% | -9% | +2% | 248 | +10% |
| 6 | MDMA 100/30 | +9% | 23% | 0.47 | -36% | 0.95 | +62% | +2% | -7% | -9% | +18% | -0% | -0% | -2% | -9% | 157 | +15% |
| 7 | VIDYA 100/30 | +9% | 24% | 0.47 | -25% | 0.94 | +19% | +12% | +9% | -4% | +56% | -14% | -1% | -3% | -19% | 121 | +12% |
| 8 | ALMA 100/30 | +6% | 23% | 0.36 | -32% | 0.73 | +42% | -17% | -8% | +16% | -7% | -3% | -10% | +2% | +8% | 876 | +8% |
| 9 | T3 50/20 | +5% | 22% | 0.33 | -24% | 0.67 | +17% | +9% | -15% | +12% | -0% | -18% | -6% | +4% | +8% | 533 | +8% |
| 10 | T3 100/30 | +5% | 22% | 0.32 | -28% | 0.63 | +32% | +1% | +2% | -11% | +2% | -18% | +9% | -3% | -3% | 302 | +6% |
| 11 | ZLEMA 200/50 | +4% | 22% | 0.30 | -31% | 0.61 | +43% | -5% | -21% | +10% | -6% | -26% | -1% | +3% | +18% | 470 | +5% |
| 12 | HMA 200/50 | +4% | 23% | 0.30 | -31% | 0.60 | +14% | +0% | -17% | +25% | +3% | -32% | -6% | -0% | +27% | 624 | +5% |
| 13 | VIDYA 200/50 | +3% | 22% | 0.25 | -29% | 0.49 | +12% | -8% | +21% | -9% | +33% | -27% | +0% | -4% | -12% | 70 | +8% |
| 14 | KAMA 50/20 | +2% | 22% | 0.20 | -36% | 0.41 | +31% | -26% | -5% | +17% | -13% | -18% | +5% | -1% | -0% | 604 | +6% |
| 15 | FRAMA 50/20 | +2% | 21% | 0.20 | -37% | 0.40 | +45% | -7% | -9% | -11% | -26% | -4% | -11% | -15% | +36% | 2035 | +3% |
| 16 | ALMA 50/20 | -1% | 22% | 0.07 | -38% | 0.14 | +24% | -10% | -19% | +6% | -8% | -26% | -15% | -5% | +16% | 1558 | +1% |
| 17 | MDMA 200/50 | -1% | 20% | 0.03 | -52% | 0.06 | +49% | +6% | -33% | -11% | +25% | -41% | +7% | -2% | -16% | 65 | +12% |
| 18 | FRAMA 100/30 | -1% | 20% | 0.03 | -35% | 0.06 | -21% | +9% | -5% | +16% | +37% | -36% | -6% | -7% | -18% | 1802 | -2% |
| 19 | HMA 100/30 | -3% | 22% | -0.03 | -39% | -0.06 | -17% | -13% | -5% | +29% | +30% | -48% | -16% | -3% | +5% | 1154 | -3% |
| 20 | FRAMA 200/50 | -4% | 21% | -0.12 | -39% | -0.23 | -21% | -6% | -3% | +17% | +44% | -44% | -21% | -5% | -12% | 1637 | -5% |
| 21 | ZLEMA 100/30 | -7% | 22% | -0.19 | -53% | -0.38 | -16% | -11% | -13% | +18% | -7% | -50% | -7% | +1% | +10% | 936 | -6% |
| 22 | KAMA 100/30 | -7% | 23% | -0.22 | -49% | -0.44 | +8% | -7% | -25% | -1% | -25% | -40% | +12% | +4% | -12% | 364 | -6% |
| 23 | HMA 50/20 | -8% | 20% | -0.33 | -48% | -0.66 | +7% | -26% | +3% | -13% | -31% | -22% | -9% | -10% | -1% | 1967 | -9% |
| 24 | ZLEMA 50/20 | -14% | 20% | -0.66 | -56% | -1.32 | -17% | -29% | -3% | -4% | -19% | -49% | -13% | -12% | -0% | 1699 | -14% |
| – | Buy&hold 5 ativos (com funding) | +1% | 26% | 0.16 | -44% | 0.32 | +41% | +4% | -35% | +9% | +40% | -47% | +13% | -6% | -6% |  | +26% |

**Sharpe médio por tipo (3 pares):** T3 0.47, VIDYA 0.45, MDMA 0.36, ALMA 0.36, KAMA 0.17, FRAMA 0.04, HMA -0.02, ZLEMA -0.18

**Sharpe médio por par:** 100/30 0.15, 200/50 0.34, 50/20 0.13

Arquivos: `results/ma_cross_4h/ranking.csv` (todas as métricas, inclusive Sharpe por ativo), `curvas_diarias.csv`. Script: `scripts/study_ma_cross.py`.
