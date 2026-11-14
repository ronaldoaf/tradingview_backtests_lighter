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
