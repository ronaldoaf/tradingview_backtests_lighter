# ICT Master Suite (Trading IQ, `ABYnIcdl`): todos os modelos em todos os ativos

Pedido: depois do 2022 Model no ouro ([ICT2022](ICT2022.md)), testar as variações de modelo da suíte em
XAU, US100, WTI, BTC e ETH (fora do protocolo, que só estenderia se o ouro fosse positivo).

Scripts: `scripts/study_ict2022.py` (2022 Model, grade agg 4–8 × fib) e `scripts/study_ictsuite.py`
(Unicorn, OTE, Silver Bullet, Liquidity Raid; padrão + só long + só short; OTE com grade de nível 0,62/0,705
× alvo 0,5/1/2). TFs 5min/15min/1h (+4h no 2022). Silver Bullet só no 5min, como o script exige.
Execução: limitada/alvo/stop no M1, stop primeiro no mesmo minuto, custo + funding.

## Resultado (melhor CAGR por modelo; B&H entre parênteses)

| modelo | XAU (+13,4%) | US100 (+20,3%) | WTI (+5,4%) | BTC (+43,8%) | ETH (+56,8%) |
|---|---|---|---|---|---|
| 2022 Model | +2,8% | +2,7% | +1,4% | +15,2% | +14,7% |
| Unicorn | +0,8% | +1,4% | +1,6% | +2,7% | +6,3% |
| OTE | +3,1% | +1,3% | +10,7%* | +10,9% | +54,8%* |
| Silver Bullet | −1,1% | −0,4% | −1,6% | +3,1% | +3,7% |
| Liquidity Raid | +0,1% | +0,5% | +2,9% | +1,2% | +4,8% |

\* OTE no WTI (15m lvl0,62 tp2) e no ETH (1h lvl0,62 tp1) chegam perto/acima do B&H só com drawdown de
90–180% (stop no pivo de origem da perna, longe da entrada, e o petróleo negativo de 2020), Sharpe 0,3–0,7 e
t < 2. Não é candidato.

Leitura:
- Nenhum modelo, em nenhum ativo, bate o buy & hold com risco aceitável.
- Unicorn e Liquidity Raid têm bom resultado por trade (+25 a +150bp no US100/BTC/ETH), mas são raros
  (1–11 trades/ano, exposição ~1%) e com t < 2,4: retorno anual irrelevante e estatística fraca.
- OTE e Silver Bullet operam muito (50–550/ano) com acerto de 10–20% (OTE) e custo comendo o pouco que sobra.
- O 2022 Model nas cripto dá +15% a.a., um terço do B&H, com só 1 célula de 56 com t > 2.

Veredito: **ICT Master Suite reprovada** em todos os modelos e ativos.
Resultados: `results/study_ict2022_<ativo>.txt`, `results/study_ictsuite_<ativo>.txt` e os `_grid.csv`.
