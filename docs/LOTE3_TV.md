# Lote 3 do TradingView — 5 estratégias (2026-10-21)

Ativo: **ouro (XAUUSD)**, M1 da Dukascopy, 2017-09-01 → 2026-10-04 (2,66M minutos).
Timeframes: 15m, 30m, 1h, 4h, 1D. Sinal no fechamento, ordem na **abertura da barra seguinte**
(Pine com `calc_on_every_tick=false`). Custo 0,75 bp por perna + funding 13,8% a.a. pro-rata
(Lighter). Controle: para cada trade, 20 entradas sorteadas com o **mesmo lado e a mesma duração**.

Código: `scripts/study_tvlote3.py` (saída `study_tvlote3.txt`, grade `study_tvlote3_xau_grid.csv`)
e `scripts/study_tvlote3_rob.py` (robustez).

**Veredito: nenhuma das 5 passa.** 467 células testadas, 8 batem o buy&hold do ouro (+13,4% a.a.),
nenhuma por mais de 2,6 pontos e nenhuma sobrevive aos terços. Todas as 5 são
*sempre-no-mercado* (exposição 98–100%), ou seja, são beta do ouro com custo de giro por cima.

---

## 1. Open Close Cross Strategy R5.1 (JustUncleL / JayRogers, `vObmEraY`) — **olha o futuro**

SMMA(8) do `open` e do `close`, lidos numa resolução 3× a do gráfico via
`security(..., lookahead=barmerge.lookahead_on)`. Com `lookahead_on`, o valor do candle HTF
**corrente** (que só é conhecido no fim dele) já aparece na primeira barra do bloco. O autor
avisa no cabeçalho ("re-painting has been observed") e oferece `delayOffset ≥ 1` dizendo que
"the reported performance will drop dramatically". Ele não exagerou — é a estratégia inteira:

| versão | 15m | 30m | 1h | 4h | 1D |
|---|---|---|---|---|---|
| como publicado (lookahead) | **+215% a.a.** | +155% | +113% | +47% | +18% |
| honesta (candle HTF fechado) | −9% | +4% | +7% | +4% | +0,3% |

Win rate cai de 75% para ~30%. Buy&hold do ouro no mesmo período: +13,4% a.a. Ou seja, o
resultado espetacular do script publicado é 100% vazamento de futuro; a regra honesta perde do
buy&hold em todos os timeframes. Grade honesta (MA × período × multiplicador, 180 células):
1 célula acima do B&H (HULL13 ×5 no 1h, +16,0% vs +13,4%) — e ela fica **negativa no terço do
meio** (−2,2% a.a. entre 2021 e 2024).

## 2. UT Bot Strategy (`VKMgZdYr`, creditado a HPotter)

Trilha de ATR (`nLoss = a × ATR(c)`, defaults a=1, c=10), flip quando o preço cruza a trilha.
O `ema(src,1)` do código é literalmente o próprio preço — não filtra nada.
Defaults: −33,5% a.a. no 15m (2.392 trades/ano), −13,9% no 30m, +6,3% no 1h, +3,7% no 1D.
Grade 4 valores de `a` × 4 de `c` × 5 TFs (85 células): **nenhuma** bate o buy&hold.
É o caso clássico de trilha apertada: o bruto é ~0 e o giro come o resto.

## 3. Twin Optimized Trend Tracker / TOTT (KivancOzbilgic, `eENf7NpJ`)

OTT sobre VAR MA(40) com banda de 1% e gatilho defasado 2 barras (`OTTup[2]`), mais um "twin"
de ±0,1%. É a melhor das cinco e ainda assim não passa: defaults dão +12,0% a.a. no 15m e
+12,3% no 30m, **abaixo** do buy&hold em todos os 5 timeframes.
Grade de 127 células: 6 acima do B&H, todas por 0,0–0,7 ponto. Nos terços elas se desfazem —
ex.: `VAR20 p1 c0` no 15m faz +20,0% vs +8,4% no terço 1, mas +11,5% vs **+31,4%** no terço 3
(a alta recente do ouro), que é onde o buy&hold ganha. O topo da grade por retorno/trade é só
amostra pequena (10–20 trades, t < 1,3).

## 4. ANN Strategy v2 (sirolf2009, `oY725jQw`) — **a "rede neural" é o sinal do candle anterior**

MLP 1-5-33-1 com pesos cravados no código. A entrada é **um escalar** (variação do `ohlc4`) e
todas as ativações são `tanh`, logo a rede inteira é uma função de uma variável. Verificação
numérica no script:

- para |variação| ≤ 5%, `sinal(rede) == sinal(variação)` em **100,00%** dos pontos, e a saída é
  estritamente crescente;
- a saída é ímpar e minúscula: rede(±1%) = ±0,0026;
- acima de ±20% ela **inverte** o sinal, por saturação do peso 41,3171 do neurônio `l2_10`
  (irrelevante na prática: nenhum candle diário anda tanto).

Portanto `buying = l3_0 > 0` é exatamente **"comprado se o ohlc4 de hoje > o de ontem"** —
um flip de 1 barra, sem nada de aprendizado. E é o pior resultado do lote: 7.271 trades/ano no
15m, −69,9% a.a.; −48,7% no 30m; −19,0% no 1h. Só long ou só short também não salva. O `getDiff()`
ainda usa `security(tickerid, '1D', ohlc4[1])` sem `lookahead`, o que mistura resoluções de forma
instável quando o gráfico não é diário.

## 5. MACD ReLoaded (KivancOzbilgic, `VO6DY8s1`)

MACD 12/26/9 com 11 tipos de média selecionáveis (default VAR), flip no cruzamento do histograma
com zero. Defaults: −7,7% a.a. no 15m, +4,2% no 30m, +11,3% no 1h, −0,6% no 1D — nenhum bate o
B&H. Grade de 60 células (7 tipos de MA × 5 TFs + 4 jogos de comprimento): **1** acima do B&H,
`TILL 12/26/9` no 1h (+14,0% vs +13,4%), e no terço 1 ela é plana (+1,0% a.a. contra +8,4% do
buy&hold) — todo o ganho vem do terço 3. Com o dobro do custo cai para +9,9%.

---

## Robustez das 8 células "vencedoras" (`study_tvlote3_rob.txt`)

| célula | tudo vs B&H | terço 1 | terço 2 | terço 3 | custo 2× |
|---|---|---|---|---|---|
| occ 1h HULL13 ×5 | +16,0% vs +13,4% | +20,4 / +8,4 | **−2,2 / +4,9** | +32,8 / +31,3 | +13,6% |
| tott 15m VAR20 p1 c0 | +14,1% | +20,0 / +8,4 | +6,3 / +4,7 | **+11,5 / +31,4** | +12,7% |
| tott 15m VAR20 p1 c.005 | +13,9% | +13,3 / +8,4 | +8,8 / +4,7 | **+19,8 / +31,4** | +13,3% |
| tott 15m VAR40 p1 c.005 | +13,5% | **+7,6 / +8,4** | +6,9 / +4,7 | +28,7 / +31,4 | +13,0% |
| tott 30m VAR20 p.5 c0 | +13,4% | +15,3 / +8,5 | +8,5 / +4,7 | **+13,0 / +31,4** | +12,2% |
| tott 30m VAR20 p1 c.005 | +13,6% | **+7,2 / +8,5** | +7,0 / +4,7 | +29,9 / +31,4 | +13,2% |
| tott 1h VAR20 p1 c0 | +13,7% | **+4,8 / +8,4** | +5,5 / +4,9 | +32,5 / +31,3 | +13,0% |
| macdre 1h TILL | +14,0% | **+1,0 / +8,4** | +5,6 / +4,9 | +45,4 / +31,3 | +9,9% |

Toda célula tem pelo menos um terço em que perde do buy&hold, e o Sharpe de nenhuma passa de
0,90 com 100% de exposição. É garimpo de 467 tentativas, não edge.

## Para a fila

Duas lições reaproveitáveis:

1. **`lookahead=barmerge.lookahead_on` com resolução alternativa** é o vazamento mais caro já
   visto na fila (+215% a.a. virando −9%). Vale um `grep lookahead_on` em todo script novo antes
   de qualquer backtest.
2. **"Rede neural" com pesos cravados e uma entrada escalar** colapsa numa regra trivial; dá para
   provar em 10 linhas (monotonicidade + igualdade de sinal) antes de rodar qualquer backtest.
