# ORB 30m de NY (opening range breakout)

Regra: barra 9:30–10:00 ET define o range; se a barra 10:00–10:30 ET fechar acima da máxima → long,
abaixo da mínima → short; entrada no fechamento (10:30 ET), saída às 15:00 ET. Mesma janela de NY nos 5
ativos (America/New_York, DST tratado), só dias úteis. Custo Lighter 2 pernas + funding pro-rata.
`p_ctl` = fração de 2000 controles (mesmos dias, lado aleatório) com resultado ≥ estratégia.
T1/T2/T3 = terços dos trades. Script: `scripts/study_orb30.py`; saída `results/orb30_resumo.csv`.

| ativo | ALL anual% | Sharpe | DD% | p_ctl | T1 | T2 | T3 |
|---|---|---|---|---|---|---|---|
| XAU | 0.9 | 0.21 | -15.9 | 0.075 | -2.5 | 0.1 | 6.2 |
| US100 | 1.3 | 0.15 | -26.5 | 0.075 | -1.6 | 2.8 | 3.1 |
| WTI | -2.9 | -0.18 | -61.7 | 0.55 | -1.8 | 3.1 | -10.6 |
| BTC | 23.8 | 1.46 | -24.3 | 0.000 | 22.7 | 38.6 | 7.7 |
| ETH | 13.4 | 0.66 | -57.0 | 0.036 | -17.7 | 29.5 | 24.5 |

Veredito: reprovada em XAU, US100 e WTI (no US100, o ativo de origem da ideia, não bate o controle).
BTC é o único positivo nos três terços, mas o último terço (set/2024→) cai para 7,7%/ano e Sharpe 0,5
(p_ctl 0,21). ETH perde 18%/ano no 1º terço. Candidato a estudo adicional só no BTC.
