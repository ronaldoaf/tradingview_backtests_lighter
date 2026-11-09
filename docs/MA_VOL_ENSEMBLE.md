# Carteira com várias médias + metade com vol da carteira alta (4h)

Script: `scripts/study_ma_vol_ens.py` (grade em `results/ma_vol_ens_grade.csv`, curvas em `results/ma_vol_ens_curva.png`).
Posição de cada ativo = média dos sinais (+1/−1) de um conjunto de médias. Conjuntos: SMA+EMA 100–300, SMA+EMA 75–400, só EMA 75–400, só SMA 75–400. Mesmos filtros, custos e split da carteira de média única. 36 células por carteira.

| Carteira | Escolhida pelo treino | Sharpe treino / valid / teste | Sem funding valid / teste | CAGR valid / teste | DD treino / valid / teste | B&H Sharpe valid / teste |
|---|---|---|---|---|---|---|
| 5 ativos | SMA+EMA 75–400, metade > 15% a.a. | 1,11 / 0,95 / 0,78 | 0,98 / 0,81 | +20% / +16% | −11% / −12% / −13% | −0,03 / 0,05 |
| 6 (com XAG) | SMA+EMA 100–300, metade > 20% a.a. | 1,09 / 0,62 / 0,78 | 0,65 / 0,81 | +15% / +20% | −14% / −15% / −12% | 0,03 / 0,25 |

- Aprovadas pelo critério (validação > 0,5). As 72 células têm validação entre 0,31 e 0,95 e teste entre 0,55 e 1,04: o resultado não depende da escolha.
- A queda do treino para fora dele ficou bem menor que com média única (1,1 → 0,6–0,95, contra 1,3–1,4 → 0,0–0,6).
- O filtro corta o DD (−17% → −12%/−14%) e melhora pouco o Sharpe; em retorno total fica abaixo da versão sem filtro porque fica metade do tempo com meia posição. Sem filtro: x6,25 (5 ativos) e x5,64 (6), DD −17%; B&H x4,93 e x4,70, DD −49% e −45%.
