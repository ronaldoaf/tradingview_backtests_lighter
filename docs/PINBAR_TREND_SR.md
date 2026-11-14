# Pin Bar + Tendência (EMA 50/200) + S&R por swings — XAU

Fonte: github.com/ZiadFrancis/Pinbar_Trend_KeyLvls (vídeo CodeTrading). Lógica reimplementada
em `scripts/study_pinbar_sr.py` (código do repo externo não foi executado).

Regras do original: pin bar (sombra ≥ 2× corpo, corpo ≤ 33% do range, sombra oposta < corpo);
tendência = close > EMA50 > EMA200 (venda espelhada); swing high/low 10/10 confirmado 10 barras
depois; S&R = swing mais recente nas últimas 100 barras abaixo (suporte) / acima (resistência)
do close, com distância ≤ 0,4%. SL = mínima/máxima da vela ± 2×ATR14(SMA), TP = 2R, time stop 50 barras.
Diferença: aqui entra na abertura seguinte (original entra no close) e custo Lighter (0,75 bp/perna + funding).

Grade: fases 1/2/3 × prox {0,2; 0,3; 0,4; 0,6%} × ATR {1; 1,5; 2} × RR {1; 1,5; 2} × TF {30m, 1h, 4h}.
Períodos: treino 2017–21, validação 2022–23, teste 2024–26.

## Resultado (1h, config do original, fase 3)

73 trades em 9 anos, **+5 bp/trade** líquidos; treino **−15,8 bp**, validação +26, teste +34
(12 trades). Fase 1 (só pin bar) ≈ 0 bp; fase 2 (+EMA) ≈ +3 bp, negativo no treino.
Em 30m e 4h nada se sustenta nos 3 períodos (4h fase 3 tem 2–11 trades). Num ativo que
subiu ~4× no período, com risco de ~50–100 bp por trade, isso é ruído.

**Veredito: reprovada no ouro.** O +15% do notebook vem de 62 trades num único período
de alta (2020–26) sem separação in/out-of-sample. Pelo protocolo, não estendida aos outros ativos.
Grade completa: `results/study_pinbar_xau_grid.csv`.

## Versão flexível (mais trades) — `study_pinbar_flex.py`

Afrouxado: sombra ≥ 1,5–2× corpo, corpo ≤ 33–45%; tendência só EMA200 ou EMA50/200; swings 5/5 ou
10/10; S&R = qualquer swing das últimas 300 barras a até 0,5–1×ATR da sombra; stop 0,5–2×ATR; RR 1,5–2;
TF 15m/30m/1h. 576 células, **8 positivas nos 3 períodos** (esperado por acaso).
Mediana de cada TF negativa (−1,5 a −3 bp).

Melhor célula: 1h, EMA200, swings 10/10, zona 0,5×ATR, stop 2×ATR, 2R → 461 trades (~50/ano),
+7,5 bp/trade (treino +1,6 / val +3,3 / teste +17,5), PF 1,18. Placebo (entradas aleatórias com o
mesmo filtro EMA200 e a mesma gestão, 200 sorteios): média −0,1 bp, dp 5,2 bp; o real fica acima de
93% deles (p≈0,07), o que não sobrevive a escolher a melhor de 576. **Continua reprovada.**
