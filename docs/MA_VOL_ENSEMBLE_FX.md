# Carteira com várias médias, sem fim de semana (janela do forex)

Script: `scripts/study_ma_vol_ens_fx.py` (grade `results/ma_vol_ens_fx_grade.csv`, curvas `results/ma_vol_ens_fx_curva.png`).
Igual a `MA_VOL_ENSEMBLE.md`, mas todos os ativos só têm barras de domingo 22:00 UTC (abertura de segunda na Ásia) a sexta 21:00 UTC (fechamento de NY). Cripto perde o sábado e o domingo. Duas versões:
- **mantém**: posição carregada no fim de semana; o movimento de sexta a segunda entra como gap.
- **zera na sexta**: fecha no fechamento de sexta e reabre na abertura de segunda (2 pernas de spread por semana, sem gap e sem funding do fds).

Sharpe treino / validação / teste da célula escolhida pelo treino (sem funding entre parênteses):

| Carteira | Versão | Escolhida | Sharpe | DD treino / valid / teste | Grade: validação mín–mediana–máx | Grade: teste mín–mediana–máx |
|---|---|---|---|---|---|---|
| 5 | mantém | EMA 75–400, metade > 15% | 1,16 / 0,44 (0,49) / 0,63 (0,65) | −12 / −18 / −14% | 0,20–0,43–0,61 | 0,42–0,80–1,01 |
| 5 | zera sexta | SMA+EMA 75–400, metade > 12% | 0,88 / 0,28 (0,30) / 0,67 (0,71) | −13 / −16 / −8% | 0,12–0,32–0,92 | 0,39–0,74–0,99 |
| 6 | mantém | SMA+EMA 75–400, metade > 15% | 1,14 / 0,34 (0,39) / 1,00 (1,06) | −14 / −15 / −10% | 0,18–0,42–0,61 | 0,63–0,87–1,15 |
| 6 | zera sexta | EMA 75–400, metade > 15% | 0,84 / 0,66 (0,70) / 0,93 (0,97) | −12 / −12 / −13% | 0,11–0,43–0,73 | 0,48–0,70–1,04 |

Comparado com a versão 24/7 (validação mediana ~0,6, mín 0,31), a validação piorou: só a carteira de 6 zerando na sexta passa no corte de 0,5. O teste continua bom em todas (mediana 0,7–0,87). Ver a cripto só nos dias de forex atrasa os sinais e os gaps de segunda pesam em 2024.
