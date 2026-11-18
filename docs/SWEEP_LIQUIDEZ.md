# Varredura de liquidez + deslocamento + reteste (price action)

Origem: documento "Conceitos de Price Action" (síntese do vídeo *Claude Tested 100,000 Price Action
Strategies*). Script: `scripts/study_sweep.py`; grades em `results/sweep_<ativo>_grid.csv`.

## Regra implementada (pseudocódigo do anexo)

1. **Sweep**: na janela de horário, a barra fura a mínima (máxima) das últimas N barras e fecha de volta
   dentro → arma compra (venda); stop técnico = extremo da barra ± 0,2·ATR(14).
2. **Deslocamento**: candle a favor com corpo ≥ k·ATR e corpo/range ≥ 70% (o próprio candle do sweep ou um
   posterior dentro da janela).
3. **Entrada limitada** no reteste: 50% do candle de deslocamento (`fvg=0`) ou meio do FVG formado com o
   candle seguinte (`fvg=1`). Ordem vale 6 barras e é cancelada se o alvo for tocado antes.
4. **Gestão**: alvo RR·R, breakeven após +1R (opcional), stop/alvo no M1 (stop primeiro no mesmo minuto,
   sem alvo no minuto do preenchimento), saída forçada 4 h após o fim da janela.
5. Filtro de volatilidade opcional: ATR(14) > SMA(ATR, 50).

Custos: spread Lighter nas 2 pernas (`CUSTO`) convertido em R (`custo·preço/R`) + funding pro-rata.
Conta: 1% de risco por trade, não composto. **Desenvolvimento até 31/12/2023; 2024+ fora da amostra.**

Grade por ativo (1.728 células): tf 5/15 min × janela ET (Londres 03:00–06:00, NY 08:30–11:30,
NY 09:30–12:00) × N 10/20/40 × k 1,0/1,5/2,0 × filtro ATR × 50%/FVG × RR 1,5/2/2,5/3 × breakeven.

## Resultado

Grade inteira (células com ≥100 trades no desenvolvimento):

| ativo | células IS > 0 | células OOS > 0 | corr Sharpe IS×OOS | E[R] mediano IS | custo mediano (R) |
|---|---|---|---|---|---|
| XAU | 21% | 8% | -0,14 | -0,07 | 0,09 |
| US100 | 10% | 29% | 0,38 | -0,12 | 0,10 |
| WTI | 26% | 29% | 0,24 | -0,06 | 0,05 |
| BTC | 16% | 23% | 0,34 | -0,06 | 0,03 |
| ETH | 17% | 10% | 0,13 | -0,07 | 0,02 |

Regra canônica do pseudocódigo (5 min, NY 09:30–12:00, N=20, k=1,5, filtro ATR, 50%, 2,5R, breakeven):

| ativo | trades IS | E[R] IS | %/ano IS | trades OOS | E[R] OOS | %/ano OOS |
|---|---|---|---|---|---|---|
| XAU | 104 | +0,01 | +0,1 | 63 | -0,23 | -5,2 |
| US100 | 356 | -0,12 | -6,1 | 160 | -0,05 | -2,8 |
| WTI | 276 | -0,10 | -4,1 | 103 | +0,01 | +0,3 |
| BTC | 111 | -0,04 | -1,1 | 177 | +0,01 | +0,3 |
| ETH | 122 | -0,15 | -4,6 | 137 | -0,05 | -2,4 |

Melhor célula do desenvolvimento (Sharpe, ≥100 trades) e o que fez fora da amostra:

| ativo | célula | Sharpe IS | %/ano IS | Sharpe OOS | %/ano OOS |
|---|---|---|---|---|---|
| XAU | 5m NY08:30 N10 k1,5 ATR 50% 1,5R | 0,79 | +5,1 | -0,57 | -4,6 |
| US100 | 5m NY N40 k2,0 50% 2,5R BE | 0,49 | +2,8 | -0,59 | -3,0 |
| WTI | 15m Londres N20 k1,0 ATR 50% 2,5R | 0,73 | +7,0 | -1,98 | -17,7 |
| BTC | 5m NY N10 k1,0 ATR FVG 2,5R | 0,74 | +8,6 | -0,05 | -0,8 |
| ETH | 5m Londres N40 k1,0 ATR FVG 1,5R | 0,96 | +7,7 | -0,11 | -0,9 |

## Veredito: reprovada nos 5 ativos

- Antes de custo o E[R] mediano da grade é ≈ 0 (de -0,05 a +0,02 R): não há sinal bruto. O custo de
  spread pesa 0,02–0,10 R por trade porque os stops do sweep em 5 min são curtos, e afunda tudo.
- Só 10–26% das células são positivas no desenvolvimento, o esperado de uma grade de ruído; as melhores
  de cada ativo ficam negativas em 2024+ (nenhuma das 5 escolhidas no IS ganha dinheiro fora da amostra).
- A regra canônica do anexo perde ou empata em todos os ativos, nos dois períodos.
- Não vale estudo adicional; nenhuma variação de janela, timeframe, FVG ou breakeven muda o quadro.
