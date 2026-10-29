### Validação (partes 7–9): Sharpe com a regra menos Sharpe do controle sem regime

Cada célula: mediana nas 4 regras · em quantas das 4 a regra ganhou do controle · percentil mediano contra os placebos.

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| B&H só em alta | -0,10 · 0/4 · p63 | -0,23 · 0/4 · p12 | +0,64 · 3/4 · p50 | -0,27 · 1/4 · p48 | -0,35 · 1/4 · p24 |
| B&H só no regime bom | -0,39 · 0/4 · p52 | -0,43 · 0/4 · p38 | +0,61 · 4/4 · p37 | -0,27 · 1/4 · p54 | -0,35 · 1/4 · p29 |
| todas, liga se E>0 | -0,07 · 1/4 · p16 | -0,01 · 1/4 · p48 | +0,09 · 4/4 · p62 | -0,01 · 1/4 · p52 | -0,00 · 2/4 · p49 |
| todas, liga no regime bom | -0,22 · 1/4 · p33 | -0,09 · 0/4 · p54 | +0,19 · 4/4 · p66 | -0,03 · 2/4 · p68 | -0,22 · 1/4 · p44 |
| K6, liga no regime bom | -0,12 · 1/4 · p63 | -0,03 · 1/4 · p78 | -0,16 · 1/4 · p32 | -0,42 · 1/4 · p40 | -0,58 · 0/4 · p65 |
| escolhe por regime | +0,87 · 4/4 · p78 | +0,07 · 2/4 · p80 | -0,40 · 0/4 · p39 | -0,97 · 0/4 · p36 | -0,68 · 0/4 · p57 |

### OOS (parte 10): Sharpe com a regra menos Sharpe do controle sem regime

Cada célula: mediana nas 4 regras · em quantas das 4 a regra ganhou do controle · percentil mediano contra os placebos.

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| B&H só em alta | +0,02 · 2/4 · p60 | +0,00 · 0/4 · p56 | -0,08 · 2/4 · p40 | +0,57 · 4/4 · p87 | +0,94 · 4/4 · p86 |
| B&H só no regime bom | +0,02 · 2/4 · p52 | -0,91 · 0/4 · p30 | +0,29 · 3/4 · p66 | +0,57 · 4/4 · p73 | +0,94 · 3/4 · p78 |
| todas, liga se E>0 | +0,01 · 3/4 · p84 | +0,00 · 2/4 · p43 | -0,30 · 1/4 · p44 | -0,04 · 0/4 · p40 | +0,02 · 2/4 · p74 |
| todas, liga no regime bom | -0,07 · 1/4 · p60 | -0,13 · 1/4 · p47 | -0,48 · 1/4 · p36 | +0,22 · 3/4 · p86 | -0,01 · 2/4 · p54 |
| K6, liga no regime bom | +0,03 · 2/4 · p54 | +0,45 · 3/4 · p82 | -0,09 · 2/4 · p52 | -0,45 · 1/4 · p26 | -1,29 · 0/4 · p24 |
| escolhe por regime | -0,90 · 1/4 · p30 | +1,15 · 4/4 · p82 | +0,54 · 3/4 · p66 | +0,21 · 3/4 · p73 | -0,12 · 2/4 · p69 |

### Escolher por regime, regra a regra (Sharpe do uso − controle · percentil contra placebos)

| Regra | Período | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|---|
| mm200 | valid | +0,83 · p74 | -0,02 · p73 | -0,36 · p45 | -0,57 · p56 | -0,54 · p73 |
| mm200 | oos | -2,28 · p1 | +1,18 · p87 | +0,82 · p82 | +2,02 · p98 | +0,35 · p81 |
| cruz | valid | +0,79 · p65 | +0,15 · p85 | -0,85 · p5 | -1,18 · p15 | -0,74 · p60 |
| cruz | oos | -0,22 · p58 | +0,02 · p14 | +0,25 · p51 | -0,29 · p20 | -0,39 · p40 |
| mom12 | valid | +1,01 · p88 | -0,07 · p74 | -0,23 · p39 | -0,75 · p66 | -0,62 · p55 |
| mom12 | oos | +0,34 · p84 | +1,28 · p91 | +0,94 · p85 | +0,06 · p66 | +0,01 · p77 |
| dd20 | valid | +0,90 · p83 | +0,60 · p100 | -0,44 · p39 | -2,39 · p0 | -1,26 · p15 |
| dd20 | oos | -1,59 · p3 | +1,12 · p77 | -0,01 · p30 | +0,36 · p79 | -0,25 · p61 |

160 combinações (uso × ativo × regra): acima de 90% dos placebos na validação 9, nos dois períodos 2; correlação validação × OOS dos percentis -0,02.
