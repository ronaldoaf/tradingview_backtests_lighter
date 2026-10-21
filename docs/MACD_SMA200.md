# MACD + SMA 200 Strategy (by ChartArt) — TradingView `yMCa3XZD`

**Data do teste:** 2026-10-21 · **Ativo padrão:** ouro (XAUUSD, M1 Dukascopy, 2017-09 → 2026-10, 2,66 M barras)
**Código:** `scripts/study_macdsma.py` (grade) e `scripts/study_macdsma_rob.py` (robustez + OOS)
**Veredito: sem edge aproveitável.** O 15m no ouro parece bom, mas não sobrevive ao subperíodo do
meio nem ao OOS em outros ativos — é seguimento de tendência com exposição ~100%, não alfa.

---

## 1. O que o script publicado realmente faz

Fonte Pine v2 extraída do HTML da página (campo `script.content`; scripts de 2015 não estão no
pine-facade).

```
fastMA = sma(close,12)   slowMA = sma(close,26)   veryslowMA = sma(close,200)
macd   = fastMA - slowMA   signal = sma(macd,9)   hist = macd - signal
long  : crossover(hist,0)  e macd > 0 e fastMA > slowMA e close[26] > veryslowMA
short : crossunder(hist,0) e macd < 0 e fastMA < slowMA e close[26] < veryslowMA
```

Quatro coisas que a descrição não conta:

1. **Não existe saída nenhuma.** Sem stop, sem alvo, sem time stop. O
   `strategy.risk.max_intraday_loss(50%)` é disjuntor de equity, não saída de trade. A posição só
   muda no sinal contrário (`pyramiding=0` → inverte) ⇒ **exposição 99–100%** depois do 1º sinal,
   mesma armadilha do [Bollinger+RSI](BOLLINGER_RSI.md) do mesmo autor. Sem stop não há 1R: a
   medição é retorno sobre o nocional a 1x e o benchmark obrigatório é **buy & hold**.
2. **O "MACD" é diferença de SMAs**, não de EMAs — não é o MACD padrão.
3. **O filtro de tendência é defasado:** "the recent price has to be above the SMA 200" é na verdade
   `close[slowLength] = close[26]` (26 barras atrás) contra a SMA200 **de agora**. Testei as duas
   leituras (`QL=1` fiel / `QL=0` literal) — e a versão fiel é a **pior** na maioria das células.
4. **`crossover(hist,0)` + `macd>0` + `fastMA>slowMA` são quase a mesma condição** (redundância, não
   confluência). Os `strategy.cancel` são inócuos: as ordens stop (`stop=low` no longo, `stop=high`
   no short) ficam do lado já ativado e preenchem na abertura da barra seguinte.

Custos: 0,75 bp/perna de spread na Lighter (inverter = 2 pernas) + funding pro-rata 13,8%/ano no
ouro (o long paga, o short recebe) — protagonista, porque o carrego dura dias/semanas.
Controle aleatório: mesmo nº de inversões, mesma alternância de lados, instantes sorteados.

## 2. Grade no ouro — 228 células

| TF | nº células | trades (mediana) | bp líq (mediana) | CAGR (mediana) | Sharpe (mediana) | t vs controle |
|----|-----------|------------------|------------------|----------------|------------------|---------------|
| 15m | 50 | 643 | **+10,2** | **+7,5%** | **0,43** | **1,63** |
| 30m | 50 | 312 | +7,3 | +2,5% | 0,15 | 0,69 |
| 1h | 50 | 158 | +12,7 | +2,1% | 0,12 | 0,52 |
| 4h | 49 | 44 | +53,8 | +1,7% | 0,10 | 0,69 |
| 1D | 29 | 9 | +721 | +2,7% | 0,18 | 1,07 |

Buy & hold do ouro no período: **+13,4%/ano**.

- **Defaults do script** (12/26/9, SMA200, filtro defasado): 15m +16 bp líq/trade, CAGR +7,5%,
  Sharpe 0,43 — metade do B&H. 1h cai para +1,6%, 4h fica negativo (−2,4%).
- O topo da grade por retorno/trade é todo **1D com 5–10 trades** — ruído, descartado.
- **185/228 células positivas no líquido, 102 com t>1, mas só 8 acima do buy & hold** — e as 8 são
  todas de 15m (Sharpe 0,70–0,93, 600–1800 trades, t 2,3–3,6). Essa é a única ilha coerente, e foi
  ela que estressei.

## 3. Estresse da ilha de 15m

**Passa** nos testes de execução e custo (o que é de esperar: o giro é moderado, 5–25 bp/trade de
retorno bruto contra 1,5 bp de custo):

| cenário | CAGR mediana da ilha | Sharpe mediano |
|---|---|---|
| base (abertura seguinte, custo 1x) | +14,5% | 0,83 |
| custo 2x (1,5 bp/perna) | +13,0% | 0,74 |
| custo 4x (3,0 bp/perna) | +9,1% | 0,52 |
| sinal executado +1 barra depois | +14,4% | 0,82 |
| sinal executado +2 barras depois | +14,0% | 0,79 |
| execução no fechamento do sinal | +14,6% | 0,82 |

**Falha** nos dois testes que importam:

**(a) Subperíodos (terços do histórico).** O resultado vem de dois regimes de alta do ouro; o terço
do meio zera ou perde em **7 das 9** configurações:

| célula | 2017-09→2021-05 (B&H +8,4%) | 2021-05→2024-02 (B&H +4,7%) | 2024-02→2026-10 (B&H +31,4%) |
|---|---|---|---|
| defaults 12/26/9 V200 QL1 | +11,1% | **−1,6%** | +11,0% (vs 31,4% do B&H) |
| i1 12/26/9 V50 | +8,8% | **−6,4%** | +49,1% |
| i2 12/26/9 V100 | +10,9% | **−5,1%** | +42,2% |
| i3 12/26/9 V400 QL1 | +9,6% | +17,6% | +19,5% |
| i4 8/17/9 V50 | +12,5% | +1,8% | +33,1% |
| i5 8/17/9 V100 | +12,3% | +6,7% | +33,0% |
| i6 8/17/9 V400 | +15,1% | +6,2% | +23,2% |
| i7 12/26/5 V100 | +19,1% | **−5,5%** | +41,5% |
| i8 12/26/5 V200 | +13,1% | **−0,5%** | +33,2% |

Note que os **defaults do script ficam abaixo do buy & hold em todos os três terços**. E a única
célula consistente nos três (i3) é a de SMA 400 com 311 trades — fora da especificação e com o
filtro defasado, combinação que não tem razão de ser.

**(b) OOS nos outros ativos, mesmas células, sem reotimizar** (protocolo: só estender se o ouro for
positivo — foi, então estendi):

| ativo | células positivas no líquido | melhor CAGR | B&H | células acima do B&H | melhor t |
|---|---|---|---|---|---|
| US100 | 7/9 | +7,5% | **+20,3%** | 0/9 | 1,44 |
| WTI | 3/9 | +19,0% | +5,4% | 2/9 (DD −119% e −124%) | 1,55 |
| BTC | 9/9 | +58,2% | +43,8% | 1/9 (os defaults, t=1,98) | 1,98 |
| ETH | 9/9 | +88,1% | +56,8% | 2/9 (t=2,44, DD −112%) | 2,44 |

US100: Sharpe 0,0–0,34 com DD de até −92% — o gatilho não acrescenta nada (t≤1,44) e fica a um
terço do buy & hold. WTI: 6 das 8 células da ilha são **negativas**, com DD de −120% a −266%. BTC e
ETH são positivos, mas é exposição direcional: drawdowns de −83% a −206% a 1x, Sharpe 0,2–0,65 e
quase tudo abaixo do B&H do próprio ativo. Nenhum ativo tem t>2,5 e as duas células que passam de
t=2 em cripto não são as mesmas que se destacam no ouro.

## 4. Conclusão

A ilha de 15m no ouro é real no sentido estatístico fraco (t de trade 2,5–2,9 com 600–1800 trades,
robusta a custo 4x e a atraso de 2 barras), mas:

- **as 8 células foram selecionadas olhando a própria grade de 228** — o t in-sample delas está
  inflado por construção, e os testes honestos (terço do meio, OOS) reprovam;
- **a exposição é 99–100%** e o CAGR da melhor célula (+16,6%) fica a 3 pp do buy & hold do ouro
  (+13,4%), com DD de −31% — risco/retorno equivalente a simplesmente carregar ouro;
- **os defaults publicados perdem do buy & hold em todos os terços e em todos os 5 ativos.**

Mesmo padrão de [GOLD_TRAIL](GOLD_TRAIL.md), [MACD_CONFLUENCE](MACD_CONFLUENCE.md),
[TRENDLINE_ANGLE](TRENDLINE_ANGLE.md) e [BOLLINGER_RSI](BOLLINGER_RSI.md): o "backtest bonito" é
exposição direcional de ~100% num ativo que subiu, não alfa. Reprovada — não vale sombra.
