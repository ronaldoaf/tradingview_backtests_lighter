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

## Permanência mínima antes de trocar de ativo (carteira de 4; `python study_ma_vol_sel.py 4 hold`, grade `results/ma_vol_sel4_hold_grade.csv`)

H = barras de 4h desde a última troca no par antes de permitir outra. Célula escolhida pelo treino dentro de cada H; Sharpe treino / valid / teste e mediana da grade (36 células).

| H | Escolhida | Sharpe | Mediana valid / teste | Curva |
|---|---|---|---|---|
| 1 (sem trava) | SMA+EMA 75–400, > 20% | 1,07 / 0,56 / 0,92 | 0,63 / 0,68 | x4,35 |
| 6 (1 dia) | EMA 75–400, > 12% | 1,01 / 0,81 / 0,49 | 0,34 / 0,57 | x2,76 |
| 12 (2 dias) | SMA+EMA 100–300, > 20% | 1,19 / 0,39 / 0,62 | 0,46 / 0,52 | — |
| 30 (5 dias) | SMA+EMA 100–300, > 20% | 1,31 / 0,36 / 0,27 | 0,25 / 0,37 | x4,17 |
| 60 (10 dias) | SMA+EMA 75–400, > 20% | 1,24 / 0,44 / 0,74 | 0,27 / 0,61 | x4,57 |
| 120 (20 dias) | SMA+EMA 100–300, > 10% | 1,23 / 0,49 / 0,05 | 0,17 / 0,39 | x2,55 |

A trava piora a validação em todos os H (mediana 0,63 → 0,17–0,46): a troca rápida para o ativo mais forte é justamente o que ajuda, e o custo das trocas é pequeno. Manter sem trava.

## Mesma carteira de 4 no gráfico de 1h (`python study_ma_vol_sel.py 4 1h` e `... 4 1hx4`)

`1h`: médias nas mesmas 75–400 barras (horizonte 4× mais curto). `1hx4`: médias ×4 (mesmo horizonte do 4h), seleção e sinais checados a cada hora.

| Versão | Escolhida | Sharpe treino / valid / teste | Mediana valid / teste | Curva |
|---|---|---|---|---|
| 4h (referência) | SMA+EMA 75–400, > 20% | 1,07 / 0,56 / 0,92 | 0,63 / 0,68 | x4,35, DD −15% |
| 1h, mesmas barras | EMA 75–400, pct 80 | 1,10 / 0,54 / 0,62 | 0,34 / 0,32 | x4,59, DD −19% |
| 1h, médias ×4 | EMA 75–400 (×4), > 20% | 1,12 / 0,53 / 0,47 | 0,54 / 0,49 | x3,96, DD −19% |

O 1h não melhora: a validação fica parecida e o teste cai. A vantagem da seleção não vem de trocar mais rápido que 4h.

## Melhorias na carteira de 4 (`scripts/study_ma_vol_sel_v2.py`, grade `results/ma_vol_sel4_v2_grade.csv`, controle `results/ma_vol_sel4_aleat.csv`)

1. Pesos pelo inverso da vol (~20d) do ativo escolhido, normalizados para somar 1 (`ivol`), contra 1/4 (`igual`).
2. Vol-alvo da carteira: escala = min(alvo / vol 20d, teto), alvo 8–20% a.a., teto 1 (`alvo1`) ou 2 (`alvo2`), no lugar de "metade acima de X".

Melhor célula pelo treino em cada família; Sharpe treino / valid / teste; mediana e mínimo da grade (valid / teste).

| Pesos / dimensionamento | Escolhida | Sharpe | DD valid / teste | Mediana | Mínimo |
|---|---|---|---|---|---|
| igual / metade > X (atual) | SMA+EMA 75–400, 20% | 1,07 / 0,56 / 0,92 | −15 / −12% | 0,60 / 0,70 | 0,38 / 0,52 |
| igual / alvo, teto 1 | SMA+EMA 75–400, 8% | 1,20 / 0,67 / 1,01 | −9 / −7% | 0,64 / 0,84 | 0,43 / 0,63 |
| igual / alvo, teto 2 | SMA+EMA 75–400, 10% | 1,27 / 0,69 / 1,02 | −11 / −8% | 0,69 / 0,88 | 0,43 / 0,81 |
| ivol / metade > X | SMA+EMA 100–300, 10% | 1,29 / 0,82 / 0,64 | −7 / −5% | 0,74 / 0,84 | 0,49 / 0,64 |
| ivol / percentil | SMA+EMA 100–300, p80 | 1,02 / 0,85 / 0,91 | −8 / −10% | 0,85 / 0,84 | 0,67 / 0,76 |
| **ivol / alvo, teto 2** | SMA+EMA 100–300, 8% | **1,29 / 0,90 / 0,97** | −7 / −6% | **0,80 / 0,97** | **0,59 / 0,87** |

3. Controle aleatório (50 sorteios do ativo de cada par, mesma frequência de trocas): % de sorteios com Sharpe ≥ real.

| Célula | treino | valid | teste |
|---|---|---|---|
| igual, metade > 20% | 6% | 16% | 8% |
| ivol, metade > 10% | 6% | 4% | 62% |
| ivol, alvo 8% teto 2 | 4% | 8% | 20% |

Leitura: pesos pelo inverso da vol e vol-alvo melhoram tudo (Sharpe fora do treino ~0,9–1,0, DD −6 a −7%, grade inteira com teste ≥ 0,87 na família ivol/alvo2). O controle aleatório mostra que a escolha pela força ajuda (real acima de ~80–95% dos sorteios na maioria dos períodos), mas o ganho sobre o sorteio é moderado: média do aleatório já é 0,45–0,71 fora do treino; boa parte do resultado vem da tendência + diversificação, não da escolha. Com teto 2, a exposição bruta média fica em ~0,66x (no teste).
