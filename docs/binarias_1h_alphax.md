# Binárias 1h AlphaX — BTC e ETH (dados 1m Binance)

**Produto:** apostar se o preço em 60 min estará acima/abaixo do atual; ganho = 85% da aposta, perda = 100%.
Equilíbrio: acerto **54,05%**. Empate contado como perda (conservador; regra da AlphaX não documentada).
**Períodos:** treino jan/2020–mai/2024 · validação jun/2024–mai/2025 · OOS jun/2025–set/2026 (usado uma vez, só nos finalistas).
Apostas sem sobreposição (no máx. 1 aposta aberta por regra). Limiares definidos só no treino.
Taxa base (apostar alta toda hora): 50–51% → sem sinal, perde ~6,5% por aposta.

## Busca
1.776 variantes: extremos (0,5%–20%) de retornos 1–1440 min, z-scores, distância a médias, RSI, posição no range,
volume, barra 1m, número redondo, força relativa BTC×ETH — seguindo ou revertendo; hora do dia, hora×dia da semana;
reversão condicionada ao regime de volatilidade.
Filtro: limite inferior (95% unilateral) do acerto > 54,05% **no treino e na validação**, n_val ≥ 100 → **21 finalistas**.
Hora do dia/dia da semana: nenhuma passou (amostras pequenas, puro ruído).

## Resultado
Os 21 finalistas são todos a mesma ideia: **comprar (ALTA) depois de queda extrema** (sobrevenda de curto prazo) — ou fade de
extremos em vol alta. No OOS, 19 de 21 ficaram acima de 54,05% (lag 0), mas a margem é pequena e quase nenhum é significativo.

Melhor e único que sobrevive à correção de múltiplos testes (Bonferroni 0,05/21 = 0,0024):

**ETH — preço abaixo da média de 60 min com (preço − MM60)/(preço·σ1m·√60) ≤ −1,42 (0,5% mais extremo do treino; σ1m = desvio dos retornos 1m nos últimos 60 min) → apostar ALTA**

| atraso de entrada | treino | validação | OOS | EV/aposta OOS | p OOS |
|---|---|---|---|---|---|
| 0 min | 59,0% (2188) | 64,2% (544) | **60,2% (713)** | +11,3% | 0,0006 |
| 1 min | 57,7% | 60,5% | 57,9% | +7,2% | 0,021 |
| 2 min | 57,2% | 59,0% | 57,8% | +6,9% | 0,025 |

Outros ETH com OOS > 56%: RSI14 no 0,5% inferior (56,8%, EV +5%), z15/z60 no 0,5% inferior (57–58%), ma240 0,5% (57%).
BTC: mesmo efeito mas mais fraco (OOS 53–56%, EV ≈ 0 a +3%) — não vale.

## Ressalvas
- Com 1 min de atraso o ETH ma60 já não passa Bonferroni; apostas se concentram em dias de crash (correlacionadas), então o n efetivo é menor que 713.
- Sinal e resultado medidos na Binance; a AlphaX usa o próprio preço de referência. Diferença/atraso no preço de referência come o edge rapidamente.
- Regra de empate, limite de aposta e se há spread embutido no preço de entrada não foram verificados.
- ~1,5 aposta/dia em média, muito irregular (dias sem nada, crashes com várias).

**Veredito:** só existe um efeito consistente — reversão de queda extrema em ETH. Edge real estimado +5 a +7% por aposta com atraso realista,
marginal estatisticamente. Candidato para paper trading na AlphaX (comparando preço de referência deles com Binance), não para dinheiro relevante ainda.

Arquivos: `scripts/study_binarias_1h.py` (grade; `--final` roda finalistas), `results/binarias_1h_grid.csv`, `results/binarias_1h_finalistas.csv`.
