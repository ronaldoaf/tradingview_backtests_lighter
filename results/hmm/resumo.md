### Validação (partes 7–9): Sharpe do uso com HMM menos Sharpe do controle sem regime

Cada célula: diferença mediana de Sharpe nas 4 versões do HMM (diário/semanal × 2/3 estados) · em quantas das 4 o HMM ganhou do controle · percentil mediano contra os placebos (regimes deslocados no tempo; 50 = igual ao acaso, ≥ 90 = sinal).

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| B&H só se E>0 | -0,29 · 1/4 · p82 | +0,00 · 0/4 · p58 | +2,42 · 4/4 · p50 | +0,00 · 0/4 · p51 | +0,00 · 0/4 · p51 |
| B&H só no regime bom | -0,25 · 0/4 · p54 | -0,26 · 1/4 · p55 | +1,66 · 4/4 · p98 | -0,25 · 1/4 · p48 | -0,29 · 1/4 · p41 |
| todas, liga se E>0 | -0,01 · 2/4 · p49 | -0,00 · 0/4 · p66 | -0,01 · 2/4 · p36 | +0,00 · 2/4 · p62 | +0,01 · 4/4 · p94 |
| todas, liga no regime bom | -0,35 · 0/4 · p22 | -0,24 · 1/4 · p34 | +0,26 · 3/4 · p70 | +0,34 · 4/4 · p90 | -0,22 · 1/4 · p52 |
| K6, liga se E>0 | -0,02 · 0/4 · p31 | +0,00 · 0/4 · p54 | +0,00 · 1/4 · p48 | +0,00 · 0/4 · p50 | +0,00 · 0/4 · p51 |
| K6, liga no regime bom | +0,05 · 2/4 · p84 | -0,23 · 1/4 · p57 | -0,30 · 2/4 · p33 | +0,09 · 2/4 · p84 | -1,88 · 0/4 · p4 |
| escolhe por regime | +0,59 · 3/4 · p68 | -0,17 · 0/4 · p43 | -0,16 · 1/4 · p53 | +0,20 · 4/4 · p78 | -0,12 · 1/4 · p92 |

### Validação (partes 7–9): informação do regime (retorno a.a. nos dias de regime bom menos nos de regime ruim)

| Medida | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| informação, ativo | -0,01 · p48 | +0,04 · p54 | +0,05 · p54 | +0,51 · p71 | -0,25 · p46 |
| informação, estratégias | -0,00 · p50 | +0,04 · p83 | -0,08 · p10 | +0,24 · p90 | -0,09 · p50 |

### OOS (parte 10): Sharpe do uso com HMM menos Sharpe do controle sem regime

Cada célula: diferença mediana de Sharpe nas 4 versões do HMM (diário/semanal × 2/3 estados) · em quantas das 4 o HMM ganhou do controle · percentil mediano contra os placebos (regimes deslocados no tempo; 50 = igual ao acaso, ≥ 90 = sinal).

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| B&H só se E>0 | -0,23 · 1/4 · p47 | +0,00 · 0/4 · p50 | +0,15 · 4/4 · p50 | +0,00 · 0/4 · p50 | +0,00 · 0/4 · p50 |
| B&H só no regime bom | -0,24 · 1/4 · p36 | +0,02 · 2/4 · p65 | -0,37 · 1/4 · p32 | -0,31 · 0/4 · p26 | -0,80 · 0/4 · p18 |
| todas, liga se E>0 | +0,01 · 3/4 · p67 | -0,00 · 1/4 · p36 | -0,39 · 0/4 · p22 | -0,01 · 1/4 · p39 | -0,01 · 1/4 · p36 |
| todas, liga no regime bom | -0,18 · 0/4 · p44 | +0,09 · 3/4 · p66 | -0,70 · 0/4 · p25 | -0,16 · 1/4 · p54 | +0,04 · 2/4 · p53 |
| K6, liga se E>0 | +0,00 · 0/4 · p53 | +0,00 · 0/4 · p53 | -0,09 · 0/4 · p34 | +0,00 · 0/4 · p50 | +0,00 · 0/4 · p50 |
| K6, liga no regime bom | -0,19 · 0/4 · p40 | +0,69 · 3/4 · p90 | +0,13 · 3/4 · p79 | +0,51 · 3/4 · p84 | -1,75 · 0/4 · p6 |
| escolhe por regime | +0,07 · 3/4 · p66 | +0,67 · 3/4 · p64 | +0,04 · 2/4 · p38 | +0,13 · 3/4 · p26 | +0,18 · 4/4 · p50 |

### OOS (parte 10): informação do regime (retorno a.a. nos dias de regime bom menos nos de regime ruim)

| Medida | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| informação, ativo | -0,34 · p28 | +0,26 · p75 | -0,86 · p32 | -0,70 · p25 | -3,46 · p4 |
| informação, estratégias | -0,54 · p4 | +0,05 · p74 | -0,24 · p37 | -0,08 · p44 | +0,04 · p52 |

### Controles sem regime (Sharpe)

| Carteira | Período | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|---|
| bh | valid | +0,99 | +1,11 | -2,42 | +0,81 | +0,33 |
| bh | oos | -0,18 | +0,91 | -0,15 | -0,20 | -0,14 |
| todas | valid | +0,65 | +1,13 | -0,56 | +0,59 | +0,68 |
| todas | oos | +0,79 | +0,16 | +0,69 | +0,91 | +0,44 |
| k6 | valid | +1,10 | +0,81 | -0,24 | +1,33 | +2,58 |
| k6 | oos | +0,04 | -0,21 | +0,66 | +0,54 | +1,93 |
| escolhe_sem_regime | valid | -0,32 | +0,64 | +0,67 | +1,40 | +2,77 |
| escolhe_sem_regime | oos | +1,11 | -0,38 | -0,03 | +0,61 | +1,31 |

### Regime da própria estratégia (HMM 1-D no retorno de cada uma) — Sharpe

| Carteira | Período | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|---|
| todas | valid | +0,65 | +1,13 | -0,56 | +0,59 | +0,68 |
| todas | oos | +0,79 | +0,16 | +0,69 | +0,91 | +0,44 |
| todas_propria_hmm | valid | +0,57 | +1,13 | -0,53 | +0,57 | +0,59 |
| todas_propria_hmm | oos | +0,80 | +0,09 | +0,43 | +0,87 | +0,35 |
| todas_propria_rel | valid | -0,00 | +0,87 | -0,38 | +0,35 | +0,16 |
| todas_propria_rel | oos | +0,26 | +0,13 | +0,28 | +0,71 | -0,27 |
| todas_media60 | valid | +0,53 | +0,73 | -0,41 | +0,30 | +0,72 |
| todas_media60 | oos | +0,19 | -0,26 | +0,00 | +0,32 | -0,00 |
| k6 | valid | +1,10 | +0,81 | -0,24 | +1,33 | +2,58 |
| k6 | oos | +0,04 | -0,21 | +0,66 | +0,54 | +1,93 |
| k6_propria_hmm | valid | +1,10 | +0,81 | -0,24 | +1,33 | +2,58 |
| k6_propria_hmm | oos | +0,04 | -0,21 | +0,66 | +0,54 | +1,93 |
| k6_propria_rel | valid | +1,00 | +0,84 | -0,44 | +0,48 | +0,10 |
| k6_propria_rel | oos | -0,63 | -0,00 | +0,88 | +1,26 | +1,79 |
| k6_media60 | valid | +0,62 | +0,32 | +0,44 | +0,58 | +2,43 |
| k6_media60 | oos | -0,84 | -0,50 | +0,74 | -0,05 | +1,34 |
| info_propria | valid | -0,05 | +0,01 | -0,00 | -0,04 | -0,25 |
| info_propria | oos | -0,17 | +0,01 | -0,12 | +0,21 | -0,19 |
| info_media60 | valid | -0,01 | -0,14 | -0,09 | -0,15 | -0,00 |
| info_media60 | oos | -0,43 | -0,17 | -0,39 | -0,38 | -0,53 |
