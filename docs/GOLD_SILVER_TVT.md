# Gold/Silver RSI + EMA162: treino / validação / teste

Script: `scripts/study_gs_tvt.py` (resultados em `results/gs_tvt_resumo.csv` e `results/gs_tvt_grade.csv`).

- Regra (lote 21, `lx4O1PPu`): long com close > EMA162 e RSI14 < 35; short com close < EMA162 e RSI14 > 35 ("escrito") ou > 65 ("corrigido"). Só a entrada contrária inverte (ou zera, se só comprado).
- Grade: 15m/30m/1h/4h × escrito/corrigido × long/ambos = 16 células por ativo.
- Split por tempo: 60% treino, 20% validação, 20% teste. Célula escolhida pelo maior Sharpe do treino (mínimo 30 trades no treino), custos de spread da Lighter + funding.
- Critério: aprovada se Sharpe da validação > 0,5. O teste só é reportado.

| Ativo | Célula | Sharpe treino | Valid. Sharpe (sem funding) | Valid. CAGR (sem funding) | Teste Sharpe (sem funding) | Teste CAGR (sem funding) | B&H Sharpe valid/teste | Resultado |
|---|---|---:|---:|---:|---:|---:|---:|---|
| XAU | 15m escrito long | 0,82 | 1,17 (1,95) | +3,9% (+6,5%) | 2,33 (2,73) | +10,4% (+12,4%) | 1,33 / 0,87 | aprovada |
| US100 | 30m corrigido long | 0,46 | 1,43 (1,69) | +15,9% (+19,2%) | 1,09 (1,36) | +14,6% (+18,5%) | 1,61 / 0,93 | aprovada, poucos trades (19 na validação) |
| WTI | 30m escrito ambos | 0,91 | 1,83 (0,37) | +78% (+12%) | 0,53 (−0,67) | +26% (−25%) | −0,46 / 0,30 | aprovada só por causa do funding |
| BTC | 15m escrito long | 1,70 | 0,90 (1,01) | +10,5% (+11,9%) | −1,16 (−0,95) | −4,8% (−4,0%) | 1,17 / −0,40 | aprovada, mas perde no teste |
| ETH | 30m escrito long | 1,59 | 0,32 (0,45) | +3,2% (+4,5%) | −1,59 (−1,46) | −13% (−12%) | 0,03 / 0,05 | reprovada |

Ressalvas:

- WTI: sem funding o Sharpe do treino é −0,02 e o da validação 0,37. O ganho é o funding de 67,7% a.a. que o short recebe; se esse funding não se repetir na Lighter, a estratégia não existe.
- XAU: única com treino, validação e teste positivos e Sharpe estável, mas o CAGR é baixo (exposição pequena, poucos sinais).
- US100: treino fraco (0,46) e poucos trades; a escolha da célula é frágil.
- BTC: passa na validação mas o teste é negativo.
