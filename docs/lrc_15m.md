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

## Versão 1h (treino até dez/2023, validação jan/2024–jun/2025, teste jul/2025+)

Config fixa (200,2,2×ATR14), CAGR treino / validação / teste: XAU -7,5/-6,0/+9,3; US100 +3,2/+1,7/-14,4;
WTI -3,5/-15,2/-36,0; BTC -22,8/-4,4/+35,4; ETH -12,3/-7,5/-8,6.

| Ativo | Melhor N/dp/k/L (treino) | Treino | Validação | Teste | B&H teste | % grade + em treino e validação |
|---|---|---|---|---|---|---|
| XAU | 50/2/1/50 | +2,9% | -6,2% | -3,7% | +25% | 2% |
| US100 | 200/2/6/14 | +13,1% | +10,2% | -21,2% | +30% | 35% |
| WTI | 300/2,5/1/50 | +4,3% | -19,4% | -4,2% | +39% | 3% |
| BTC | 50/1,5/6/14 | +71,5% | +6,1% | **+94,7%** (PF 1,69, 122 tr) | -22% | 6% |
| ETH | 50/2/6/14 | +89,7% | -21,9% | +42,0% | +8% | 10% |

Reprovada também em 1h. BTC passa nas três janelas, mas a mesma config falhou no 15m 2024+, só 6% da grade
sobrevive a treino+validação e a validação foi fraca (+6% contra B&H +153%). Script: `scripts/study_lrc_1h.py`.

## Versão 30m (mesmas janelas; `TF=30m python scripts/study_lrc_1h.py`)

Config fixa: negativa no treino nos 5 ativos (CAGR -3% a -27%).

| Ativo | Melhor N/dp/k/L | Treino | Validação | Teste | B&H teste | % grade + treino e validação |
|---|---|---|---|---|---|---|
| XAU | 50/2/4/50 | +8,0% | -13,1% | +19,4% | +25% | 1% |
| US100 | 300/2,5/4/14 | +6,4% | +7,3% | -3,5% | +30% | 12% |
| WTI | 50/3/6/14 | +19,6% | +10,6% | +29,6% (76 tr) | +39% | 2% |
| BTC | 50/1,5/6/50 | +84,7% | +24,7% | +44,3% | -22% | 6% |
| ETH | 100/2,5/4/14 | +61,9% | +9,2% | +51,2% | +8% | 10% |

WTI, BTC e ETH ficam positivos nas três janelas, mas são ilhas (2–10% da grade). O padrão N curto + k alto (5–6 ATR)
em BTC se repete em 15m, 30m e 1h, porém falhou no 15m pós-2023.

## Controle aleatório, 50/1,5/6/50 em 30m (`scripts/study_lrc_ctl.py`, 500 sinais embaralhados por janela)

| Ativo | Janela | Estratégia | Mediana aleatória | Percentil |
|---|---|---|---|---|
| BTC | treino | +1064% | +209% | 91 |
| BTC | validação | +39% | -8% | 84 |
| BTC | teste | +58% | -11% | 96 |
| ETH | treino | +62% | +164% | 36 |
| ETH | validação | +50% | +41% | 55 |
| ETH | teste | +316% | +42% | 98 |

BTC bate o aleatório nas três janelas (nenhuma acima de p95 em treino/validação). ETH não: o bom teste parece sorte.

## Inclinação mínima (`scripts/study_lrc_slope.py`, `results/lrc/slope_min.csv`)

Filtro: |slope| × N / ATR(L) ≥ S (quanto a linha sobe em N barras, em ATRs), S ∈ {0,1,2,3,5,8}.
O filtro não melhora de forma sistemática: corta trades e muda o resultado sem padrão monotônico.
Blocos positivos nas 3 janelas para quase todo S: BTC 30m (ambas configs), BTC 1h 50/2/5/50 (S 0–5),
XAU 15m (ambas configs, S 0–8), ETH 1h 50/2/5/50 (S 1–5). US100 e WTI: nada estável.

Controle XAU 15m: 50/1,5/6/50 percentis 73/72/48; 50/2/5/50 53/85/27 (treino/valid/teste). Não bate o aleatório → descartado.
