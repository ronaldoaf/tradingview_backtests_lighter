# Tendência por média longa + filtro de volatilidade: treino / validação / teste

Script: `scripts/study_ma_vol.py` (resultados em `results/ma_vol_resumo.csv` e `results/ma_vol_grade.csv`).

- Regra: comprado com close > MA, vendido abaixo (ou fora, no modo só comprado). MA = SMA ou EMA 75/100/150/200/250/300/400.
- Filtro: vol realizada (~20 dias) vs. seu percentil no último ~1 ano (janela móvel, sem lookahead). Acima do percentil X (70/80/90) a posição vira **metade** ou **zero**. Também a versão sem filtro.
- Grade: 1h/4h/1D × 14 médias × long/ambos × 7 filtros = 588 células por ativo.
- Sinal no fechamento, execução na abertura seguinte, spread da Lighter por unidade de mudança de posição, funding pro-rata (long paga, short recebe). Sharpe diário com todos os dias (dia fora = zero).
- Split 60/20/20; célula escolhida pelo maior Sharpe do treino (com funding). Critério: Sharpe da validação > 0,5. B&H inclui o funding do long.

| Ativo | Célula escolhida | Sharpe treino | Valid. Sharpe (sem funding) | Valid. CAGR / DD | Teste Sharpe (sem funding) | Teste CAGR / DD | B&H Sharpe valid / teste | Resultado |
|---|---|---:|---:|---:|---:|---:|---:|---|
| XAU | 4h SMA250 ambos, fora > p70 | 0,73 | 0,22 (0,33) | +2,5% / −10% | 0,81 (0,99) | +14,6% / −19% | 0,41 / 0,37 | reprovada |
| US100 | 1h SMA75 long, fora > p70 | 1,42 | 0,80 (0,99) | +9,3% / −11% | −0,35 (−0,17) | −2,9% / −16% | 1,35 / 0,68 | passa na validação, perde no teste e para o B&H |
| WTI | 4h SMA150 ambos, sem filtro | 0,48 | −0,64 (−0,77) | −19% / −67% | −0,48 (−0,52) | −22% / −62% | −2,56 / −1,04 | reprovada |
| BTC | 1h EMA75 long, fora > p90 | 1,29 | 1,25 (1,37) | +65% / −25% | −0,11 (0,06) | −3,2% / −40% | 0,98 / −0,61 | passa na validação, zera no teste |
| ETH | 1h EMA75 long, metade > p80 | 1,52 | 0,24 (0,33) | +13% / −51% | 0,49 (0,60) | +28% / −38% | −0,10 / −0,10 | reprovada |

O filtro ajuda pouco, mas de forma consistente: Sharpe mediano da validação (todas as células) sem filtro vs. "fora > p70":
BTC 0,67 → 0,98; ETH 0,27 → 0,75; US100 0,90 → 1,10; XAU 0,29 → 0,24; WTI −1,14 → −1,12. "Fora" foi um pouco melhor que "metade".

Leitura: nenhuma célula escolhida pelo treino fica positiva com folga na validação e no teste ao mesmo tempo. BTC e US100 passam no corte de 0,5 da validação e caem no teste. No WTI o funding de 67,7% a.a. derruba o lado comprado. No ouro, a média longa só funciona no teste (0,81), que ninguém escolheria pelo treino/validação.
