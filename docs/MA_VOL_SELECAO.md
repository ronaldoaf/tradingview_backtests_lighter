# Carteira de 5 componentes com escolha pela tendência mais forte (4h, 24/7)

Script: `scripts/study_ma_vol_sel.py` (grade `results/ma_vol_sel_grade.csv`).
Componentes: (BTC ou ETH), (US100 ou US500), (WTI ou BRENT), XAU, XAG; peso 1/5. Em cada par entra, a cada barra de 4h, o ativo com maior força de tendência = |média de log(close/MA)| nas médias do conjunto ÷ vol de ~20 dias (medida no fechamento, vale na barra seguinte). Direção = média dos sinais das médias. Metade da posição com vol da carteira acima de X. Custos de troca e funding incluídos. Controle: escolha fixa (BTC, US100, WTI, XAU, XAG).

| Versão | Escolhida pelo treino | Sharpe treino / valid / teste (sem funding) | DD treino / valid / teste | Grade valid mín–med–máx | Grade teste mín–med–máx | Curva 2020–26 |
|---|---|---|---|---|---|---|
| tendência mais forte | SMA+EMA 100–300, metade > 12% | 1,00 / 0,56 (0,60) / 0,63 (0,70) | −13 / −9 / −10% | 0,22–0,60–0,88 | 0,28–0,53–0,84 | x2,46, DD −12% |
| fixo (BTC, US100, WTI) | SMA+EMA 100–300, metade > 12% | 1,17 / 0,26 (0,31) / 0,65 (0,68) | −9 / −11 / −9% | 0,06–0,22–0,49 | 0,28–0,51–0,70 | x2,66, DD −11% |

O ativo mais forte troca bastante: BTC entra 57% do tempo, US100 52%, WTI 54%. A escolha pela força melhora a validação (mediana 0,22 → 0,60) e mantém o teste; passa no corte de 0,5. Não supera a carteira de 6 com BTC e ETH juntos (validação ~0,6, teste ~0,8).
