# LRC(200,2,2) reversão a favor da inclinação — 15m

**Veredito: reprovada na configuração pedida; XAU otimizado fica como candidato fraco a revisar.**

Regras: long se inclinação da regressão (200) > 0 e close < banda inferior (2 dp); short no espelho.
Sinal no fechamento, entrada na abertura seguinte, saída por trailing stop k×ATR(L). Custo Lighter por perna
+ funding pro-rata. In-sample até dez/2023, OOS 2024 → set/out-2026. Script: `scripts/study_lrc.py`.

## Config fixa (200, 2, 2×ATR14)

| Ativo | IS CAGR | IS PF | IS trades | OOS CAGR | OOS PF |
|---|---|---|---|---|---|
| XAU | -4,0% | 0,90 | 1904 | -9,5% | 0,86 |
| US100 | -13,6% | 0,80 | 2403 | -7,4% | 0,88 |
| WTI | -12,6% | 0,90 | 2832 | +0,4% | 1,00 |
| BTC | -34,4% | 0,84 | 2278 | -0,9% | 0,99 |
| ETH | -40,8% | 0,85 | 2381 | +3,7% | 1,01 |

## Otimizado por ativo (grade 240 combinações: N, dp, k, L; escolha = maior CAGR IS com as duas metades positivas)

| Ativo | N/dp/k/L | IS CAGR | OOS CAGR | OOS PF | B&H OOS | % grade positiva |
|---|---|---|---|---|---|---|
| XAU | 50/2,5/6/50 | +9,5% | **+22,1%** | 1,34 | +101% | 13% |
| US100 | 50/1,5/6/50 | +9,3% | +9,5% | 1,10 | +75% | 10% |
| WTI | 50/1,5/3/50 | +26,7% | -4,8% | 0,98 | +25% | 19% |
| BTC | 50/1,5/6/14 | +61,7% | -10,0% | 0,96 | +98% | 16% |
| ETH | 50/2/4/14 | +160,6% | -34,4% | 0,89 | +18% | 35% |

- WTI, BTC, ETH: overfit claro (IS ótimo, OOS negativo).
- US100: positivo no OOS, mas o lucro vem dos longs num mercado em alta (84% exposto) — é beta, não sinal.
- XAU: único com sinal consistente — **shorts ganham IS (+9,6 bp/trade) e OOS (+9,5 bp)** mesmo com o ouro
  subindo. Ressalvas: ótimo na borda da grade (N mínimo, k máximo), só 13% da grade positiva, e falta controle aleatório.
