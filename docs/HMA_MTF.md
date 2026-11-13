# HMA Crossover Multi-Timeframe (CodeTrading) — reprovada como sistema

Regras: 4H, entrada no crossover HMA16/HMA65 com RSI14 > 52 e close > linreg(14) diária
(só o último dia **fechado**, sem look-ahead); saída no crossunder. Long-only, sem stop.
Custos Lighter (spread + funding). Script: `scripts/study_hmamtf.py`; logs `results/study_hmamtf_*.txt`.

## Long-only, parâmetros publicados (período todo)

| Ativo | Trades/ano | Líq./trade | CAGR | B&H | Sharpe | DD | Expo | t vs aleatório | Terços (CAGR) | 2ª metade |
|---|---|---|---|---|---|---|---|---|---|---|
| XAU | 19 | +21 bp | +2,8% | +13,4% | 0,64 | -20% | 23% | +1,7 | +1 / **-5** / +13 | +7,8% |
| US100 | 19 | +45 bp | +7,3% | +20,3% | 1,50 | -14% | 24% | +1,8 | +9 / +5 / +6 | +4,6% |
| WTI | 21 | -78 bp | -19,4% | +5,4% | -1,60 | — | 21% | -1,0 | 0 / -31 / -11 | -18% |
| BTC | 24 | +93 bp | +17,7% | +43,7% | 1,24 | -25% | 17% | +2,6 | +23 / +12 / +19 | +21% |
| ETH | 28 | +103 bp | +30,9% | +56,6% | 1,43 | -46% | 19% | +2,3 | +121 / +16 / **-12** | **-2,7%** |

Treino/teste (grade 81 células escolhida na 1ª metade por Sharpe): a melhor célula do treino
cai bastante no teste em todos (ETH Sharpe 3,5 → 1,2; BTC 2,2 → 2,2 é a exceção; WTI vira negativo).
Custo 2x/4x quase não muda nada (giro baixo) — exceto WTI, morto pelo funding de 68% a.a.

## Long + short (espelho)

Ajuda só em cripto: ETH CAGR 31% → 71% e BTC 18% → 27%, mas com DD de -58/-63% e t vs
aleatório que cai (o short vale por estar em tendência, não pelo gatilho). Piora US100
(Sharpe 1,5 → 0,2) e não salva WTI. XAU fica igual (Sharpe 0,64).

## Veredito

Não aprovada como estratégia isolada: nenhum ativo bate o buy & hold em CAGR, o edge sobre
entrada aleatória é marginal (t 1,7–2,6, abaixo do limiar nos terços), ETH quebra no terço
final e na 2ª metade, XAU tem um terço negativo, WTI é negativo em tudo. O que sobra é
um filtro de tendência razoável em **BTC** (positivo nos 3 terços e na 2ª metade, Sharpe
~1,2–2,0 com 17% de exposição) e **US100** (3 terços positivos, Sharpe 1,0 na 2ª metade) —
candidatos a componente de carteira, não a sistema próprio.
