# Carteira dos 5 ativos: média longa + filtro de vol da carteira

Script: `scripts/study_ma_vol_cart.py` (grade em `results/ma_vol_cart_grade.csv`).

- XAU, US100, WTI, BTC e ETH ao mesmo tempo, peso 1/5 cada (nocional bruto 1x). Cada ativo fica comprado acima e vendido abaixo da **mesma** média (SMA/EMA 75–400, em barras de 4h ou 1D).
- Vol da carteira = desvio dos retornos diários da carteira cheia nos últimos 20 dias, anualizado, medido até o dia anterior. Acima de X, **todas as posições caem pela metade**. X absoluto (8/10/12/15/20% a.a.) ou percentil móvel de ~1 ano (70/80/90).
- Período comum 2020-01 a 2026-08: treino até 31/12/2023, validação até 01/05/2025, teste até 31/08/2026. Spread Lighter + funding. Célula escolhida pelo Sharpe do treino. B&H = carteira só comprada com pesos iguais, com funding.

| Célula escolhida | Treino Sharpe / CAGR / DD | Validação Sharpe (sem funding) / CAGR / DD | Teste Sharpe (sem funding) / CAGR / DD | B&H Sharpe treino / valid / teste |
|---|---|---|---|---|
| 4h SMA150, metade acima de 20% a.a. | 1,38 / +41,6% / −17,9% | 0,57 (0,58) / +14,9% / −15,8% | 0,47 (0,48) / +11,8% / −14,4% | 0,28 / −0,03 / 0,05 |

- Mesma célula sem filtro: Sharpe 1,26 / 0,39 / 0,39. O filtro de 20% melhora todos os períodos e corta o DD do treino pouco.
- Mediana da grade (252 células), Sharpe validação / teste: sem filtro 0,48 / 0,43; percentil 70 0,69 / 0,56; 20% a.a. 0,66 / 0,55. O filtro ajuda de forma consistente.
- Vizinhas boas: 4h EMA150 com 20% (1,21 / 1,02 / 0,65), 4h EMA200 com 15% (1,21 / 0,85 / 0,94).
- Leitura: positiva nos três períodos e bem acima do B&H, mas o Sharpe cai de ~1,4 no treino para ~0,5 fora dele. Passa no corte de 0,5 na validação por pouco.
