# Carteira de 8 ativos (2 por grupo): várias médias + metade com vol alta, 4h

Script: `scripts/study_ma_vol_ens8.py` (grade `results/ma_vol_ens8_grade.csv`). BTC, ETH, WTI, BRENT, XAU, XAG, US100, US500, peso 1/8.
Brent e US500 da Dukascopy 1m (`data/duka_jetta_dl.py`); Brent com spread 1,5 bp e funding igual ao WTI (67,7% a.a.). Mesmo método de `MA_VOL_ENSEMBLE.md` (36 células por modo), período 2020-01 a 2026-08.

| Modo | Escolhida pelo treino | Sharpe treino / valid / teste (sem funding) | DD treino / valid / teste | Grade valid mín–med–máx | Grade teste mín–med–máx | Curva 2020–26 | B&H 1/8 |
|---|---|---|---|---|---|---|---|
| 24/7 | EMA 75–400, metade > 15% | 1,02 / 0,59 (0,59) / 0,59 (0,60) | −12 / −14 / −11% | 0,13–0,47–0,62 | 0,39–0,61–0,88 | x2,96, DD −13% | x3,70, DD −43% |
| forex, mantém fds | SMA 75–400, metade > 10% | 1,12 / 0,28 (0,32) / 0,96 (1,01) | −9 / −12 / −7% | 0,12–0,29–0,46 | 0,42–0,74–1,01 | x2,50, DD −12% | x3,70, DD −43% |
| forex, zera sexta | EMA 75–400, metade > 10% | 0,76 / 0,57 (0,57) / 0,45 (0,48) | −11 / −11 / −9% | −0,22–0,30–0,57 | 0,30–0,59–0,85 | x1,84, DD −10% | x2,79, DD −36% |

Leitura: com 8 ativos o Sharpe fora do treino não melhorou em relação a 5 ou 6; Brent e US500 são muito correlacionados com WTI e US100 e acrescentam pouca diversificação. O 24/7 passa por pouco (0,59 / 0,59); as versões forex ficam mais fracas na validação.
