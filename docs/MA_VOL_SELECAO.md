# Carteira de 5 componentes com escolha pela tendência mais forte (4h, 24/7)

Script: `scripts/study_ma_vol_sel.py` (grade `results/ma_vol_sel_grade.csv`).
Componentes: (BTC ou ETH), (US100 ou US500), (WTI ou BRENT), XAU, XAG; peso 1/5. Em cada par entra, a cada barra de 4h, o ativo com maior força de tendência = |média de log(close/MA)| nas médias do conjunto ÷ vol de ~20 dias (medida no fechamento, vale na barra seguinte). Direção = média dos sinais das médias. Metade da posição com vol da carteira acima de X. Custos de troca e funding incluídos. Controle: escolha fixa (BTC, US100, WTI, XAU, XAG).

| Versão | Escolhida pelo treino | Sharpe treino / valid / teste (sem funding) | DD treino / valid / teste | Grade valid mín–med–máx | Grade teste mín–med–máx | Curva 2020–26 |
|---|---|---|---|---|---|---|
| tendência mais forte | SMA+EMA 100–300, metade > 12% | 1,00 / 0,56 (0,60) / 0,63 (0,70) | −13 / −9 / −10% | 0,22–0,60–0,88 | 0,28–0,53–0,84 | x2,46, DD −12% |
| fixo (BTC, US100, WTI) | SMA+EMA 100–300, metade > 12% | 1,17 / 0,26 (0,31) / 0,65 (0,68) | −9 / −11 / −9% | 0,06–0,22–0,49 | 0,28–0,51–0,70 | x2,66, DD −11% |

O ativo mais forte troca bastante: BTC entra 57% do tempo, US100 52%, WTI 54%. A escolha pela força melhora a validação (mediana 0,22 → 0,60) e mantém o teste; passa no corte de 0,5. Não supera a carteira de 6 com BTC e ETH juntos (validação ~0,6, teste ~0,8).

## Versão com 4 componentes: (BTC ou ETH), (US100 ou US500), (WTI ou BRENT), (XAU ou XAG); peso 1/4 (`python study_ma_vol_sel.py 4`, grade `results/ma_vol_sel4_grade.csv`)

| Versão | Escolhida pelo treino | Sharpe treino / valid / teste (sem funding) | DD treino / valid / teste | Grade valid mín–med–máx | Grade teste mín–med–máx | Curva 2020–26 |
|---|---|---|---|---|---|---|
| tendência mais forte | SMA+EMA 75–400, metade > 20% | 1,07 / 0,56 (0,57) / 0,92 (0,93) | −17 / −15 / −12% | 0,38–0,63–0,95 | 0,44–0,68–1,07 | x4,35, DD −15% |
| fixo (BTC, US100, WTI, XAU) | SMA+EMA 100–300, metade > 12% | 1,25 / 0,23 (0,28) / 0,51 (0,50) | −12 / −12 / −8% | 0,06–0,23–0,57 | 0,04–0,20–0,53 | x2,78, DD −11% |

XAU entra 54% do tempo. Melhor versão de seleção até aqui: aprovada, todas as 36 células com validação ≥ 0,38 e teste ≥ 0,44.
