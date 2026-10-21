# RSI Divergence Indicator strategy — teste em ouro (2026-10-21)

Estratégia: *"RSI Divergence Indicator strategy"*
([TradingView](https://www.tradingview.com/script/qSLcZSyw-RSI-Divergence-Indicator-strategy/)).
Pine v4 aberto — baixei a fonte completa (`PUB;wUU7CXCaw0qQ1hF3fjTVkjcXmCTY12oK`) e traduzi linha a
linha, com todos os defaults, em `scripts/study_rsidiv.py`. Saída completa em
`scripts/study_rsidiv.txt`, grade em `scripts/study_rsidiv_xau_grid.csv`.

É o indicador de divergência padrão do TradingView (RSI + pivôs) embrulhado numa estratégia só-compra.
Os comentários no topo da própria fonte anunciam o resultado:

```pine
//GOOGL setting 5, close, 3, 1  profitLevel at 75 shows win rate 87.21 % profit factor 7.059
//SPY   setting 5, close, 3, 3  profitLevel at 70 shows win rate 80.34 % profit factor 2.348
```

Dados: XAUUSD M1 da Dukascopy, 2017-09-01 → 2026-10-04 (9,1 anos). Sinal no fechamento, ordem a
mercado na abertura seguinte. Custo 0,75 bp por perna + funding 13,8%/ano pro-rata. Controle: para
cada trade, 20 entradas a mercado em barras sorteadas, mesma duração.

## Veredito

**Não aprovada. Nos defaults perde dinheiro em todo timeframe, e 0 de 119 células da grade batem o
buy & hold.** O gatilho não se distingue de entrada aleatória (|t| < 0,8 em todos os defaults).

## 1. O gatilho "divergência" dispara em quase todo pivô de RSI

Esta é a observação central, e ela sai da leitura da fonte:

```pine
oscHL = osc[lbR] > valuewhen(plFound, osc[lbR], 1)   // fundo de RSI mais ALTO
priceLL = low[lbR] < valuewhen(plFound, low[lbR], 1) // fundo de preço mais BAIXO
bullCond = plotBull and priceLL and oscHL and plFound

oscLL = osc[lbR] < valuewhen(plFound, osc[lbR], 1)   // fundo de RSI mais BAIXO
priceHL = low[lbR] > valuewhen(plFound, low[lbR], 1) // fundo de preço mais ALTO
hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound

longCondition = bullCond or hiddenBullCond           // as DUAS, e plotHiddenBull é true no default
```

`bullCond` exige (RSI sobe, preço desce). `hiddenBullCond` exige (RSI desce, preço sobe). **A união
das duas cobre todo pivô em que RSI e preço discordam de sinal** — os dois únicos casos excluídos são
a concordância perfeita (ambos sobem ou ambos descem). Em ouro/1h, dos 697 sinais de compra:

| | sinais |
|---|---|
| divergência clássica (`bullCond`) | 150 |
| divergência **oculta** (`hiddenBullCond`) | **547** |
| total de compras | 697 |

79% das entradas são da divergência "oculta" — o caso em que o preço fez um fundo **mais alto** e o RSI
um fundo mais baixo, que é quase o oposto da ideia que o nome do script vende. O default liga as duas
ao mesmo tempo, então a estratégia não é "compre divergência de alta": é "compre perto de qualquer
pivô de RSI".

## 2. Defaults (RSI 9, pivô 1/3, saída em RSI > 80 ou divergência de baixa)

| TF | trades | /ano | bruto/trade | **líq/trade** | acerto | dias | **CAGR** | B&H | Sharpe | DD | expo | t |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 1350 | 148 | +4,0 bp | **−3,7 bp** | 62% | 1,6 | **−5,0%** | +13,4% | −0,41 | −76% | 63% | −0,72 |
| 30m | 690 | 76 | +9,3 bp | **−2,7 bp** | 63% | 2,8 | **−3,1%** | +13,4% | −0,28 | −65% | 60% | −0,10 |
| 1h | 381 | 42 | +18,3 bp | **−1,7 bp** | 65% | 4,9 | **−0,9%** | +13,4% | −0,09 | −46% | 59% | +0,33 |
| 4h | 114 | 12,5 | +55,8 bp | **−13,0 bp** | 61% | 17,8 | **−2,1%** | +13,4% | −0,21 | −56% | 58% | −0,17 |
| 1D | 23 | 2,5 | +248 bp | **+67,0 bp** | 61% | 47 | **+0,5%** | +13,4% | +0,11 | −20% | 34% | +0,02 |

**Líquido negativo em quatro dos cinco timeframes.** A taxa de acerto de 61–65% é exatamente o perfil
que gera as "win rates" de 80%+ anunciadas: a saída é `crossover(RSI, 80)` — fecha na força — enquanto
o lado perdedor **não tem saída nenhuma** (com o default `sl_type = NONE` não existe stop). Muitos
ganhos pequenos, perdas livres. O 1D "positivo" tem 23 trades em 9 anos e t = +0,02 contra o acaso.

O bruto por trade cresce com o TF só porque o trade dura mais (1,6 dia no 15m contra 47 dias no 1D) —
é tempo exposto, não qualidade de sinal. Normalizado pelo tempo, nada rende mais que o ouro parado.

## 3. Os dois gatilhos separados: nenhum diz nada

| TF | gatilho | trades | bruto/trade | **líq/trade** | CAGR | t |
|---|---|---|---|---|---|---|
| 1h | só clássica | 106 | +33,7 bp | **+3,3 bp** | +0,2% | +0,19 |
| 1h | só oculta | 352 | +16,5 bp | **−2,2 bp** | −1,3% | −0,31 |
| 4h | só clássica | 36 | +56,7 bp | **−42,3 bp** | −1,4% | −1,15 |
| 4h | só oculta | 106 | +52,3 bp | **−12,8 bp** | −2,0% | −0,54 |
| 15m | só clássica | 487 | +5,0 bp | **−3,8 bp** | −2,2% | −0,45 |
| 15m | só oculta | 1225 | +2,9 bp | **−4,4 bp** | −5,7% | −0,44 |

A divergência clássica isolada, que é a tese do script, só é positiva numa célula (1h, +3,3 bp,
t = +0,19, 11,7 trades/ano) — ruído puro. A oculta é negativa em todo lugar.

## 4. Bug na fonte: o multiplicador de ATR não é usado

```pine
atrMultiplier = input(3.5, title="ATR Multiplier (for Trailing stop loss)")   // nunca lido
sl_val = sl_type == "ATR" ? stopLoss * atr(atrLength) :
         sl_type == "PERC" ? close * stopLoss / 100 : 0.00
```

O input `atrMultiplier` (3,5) **nunca aparece de novo no script**. A trilha por ATR usa
`stopLoss * atr(14)`, isto é, o campo **"Stop Loss%"** (que o usuário lê como porcentagem) vira
multiplicador de ATR. Com o default `stopLoss = 5`, a trilha é 5 × ATR. Quem trocar o stop de 5% para
2% está trocando também a trilha de 5 ATR para 2 ATR sem perceber — e quem ajustar o `atrMultiplier`
não muda nada.

Testei as duas variantes de trilha fiéis ao bug:

| TF | trilha | trades | bruto/trade | **líq/trade** | CAGR | B&H | Sharpe | t |
|---|---|---|---|---|---|---|---|---|
| 15m | PERC 5% | 61 | +216 bp | +14,9 bp | −1,0% | +13,4% | −0,06 | +0,01 |
| 15m | ATR 5× | 1106 | +10,3 bp | +1,6 bp | +1,9% | +13,4% | +0,15 | +1,07 |
| 1h | ATR 5× | 270 | +41,1 bp | +14,8 bp | +3,8% | +13,4% | +0,35 | +1,00 |
| 4h | ATR 5× | 68 | +171 bp | +47,6 bp | +1,8% | +13,4% | +0,16 | +1,00 |
| 1D | PERC 5% | 15 | +525 bp | +81,8 bp | +0,9% | +13,4% | +0,10 | −0,09 |

A trilha por ATR salva o sinal do líquido (ela corta a cauda de perda que o default não tem), mas o
melhor CAGR da família é **+3,8% contra +13,4% do buy & hold**, com Sharpe 0,35 e t = 1,00. Não é edge:
é um stop decente colado num gatilho sem informação.

`pyramiding = 2` (como publicado) melhora o retorno por trade (+4,4 bp no 1h) e **piora o CAGR**
(−9,1%), porque dobra o nocional sem melhorar o acerto: DD vai a −120%.

## 5. Grade de robustez: 0/119 batem o buy & hold

RSI (5/9/14) × pivô direito (3/5/8) × nível de alvo (70/80) × TF, mais as variantes de trilha e
pyramiding:

- líquido > 0: 42 de 119. Líquido > 0 **e** t > 1: **8 de 119**.
- **CAGR > buy & hold: 0 de 119.** Melhor CAGR da grade: **+3,6%** (1D, RSI 5, pivô 3, alvo 70),
  contra +13,4% do ouro parado.
- A única célula com t respeitável (1D, RSI 5, pivô 8, alvo 70, t = +2,45) rende **CAGR +1,5%** com
  45 trades e 22% de exposição. Em 119 células, uma com t > 2 é o que se espera de ruído.
- Todas as 12 melhores células por retorno líquido são 1D com 12 a 45 trades em 9 anos.

## 6. Por que os números do cabeçalho (GOOGL 87%, PF 7,0) não significam nada

1. **Só-compra, sem stop, em ação de alta secular.** GOOGL subiu ~6x no período típico desses testes.
   Qualquer regra que compre e espere o RSI chegar a 80 acerta quase sempre; a medida correta é contra
   buy & hold, e ela não é mostrada.
2. **"Win rate" com saída assimétrica é autopromoção.** Fecha no RSI > 80 (ganho pequeno garantido) e
   não fecha nunca na perda. Acerto alto com expectativa ruim é o resultado esperado, não um achado.
3. **Profit factor sem custo.** O script não declara comissão nenhuma. No 15m, 148 trades/ano a
   0,75 bp/perna já come 2,2 bp por trade — e a estratégia só gera +4,0 bp brutos.

## 7. Notas de fidelidade

- Pivôs `ta.pivotlow(osc, lbL=1, lbR=3)` confirmam 3 barras **depois** do fundo; o sinal sai na barra
  da confirmação, então **não há repintura** (ao contrário do que costuma acontecer com divergência).
  Os `plot(..., offset=-lbR)` só desenham o marcador no passado.
- `valuewhen(plFound, osc[lbR], 1)` = valor na ocorrência **anterior** do pivô; reproduzido exato.
- `_inRange(plFound[1])`: o pivô anterior tem de estar entre 5 e 60 barras atrás. Reproduzido.
- `plotHiddenBear = false` no default, então `bearCond` (saída) usa só divergência de baixa clássica.
- A trilha atualiza no **fechamento** de cada barra e a saída é `crossunder(close, trilha)` → execução
  na abertura seguinte. Sem resolução intrabar, que é como o Pine realmente se comporta aqui.

## Conclusão

O gatilho é vazio: com os dois tipos de divergência ligados (default), ele dispara em praticamente todo
pivô de RSI, e separados nenhum dos dois supera entrada aleatória. O que produz os números bonitos do
cabeçalho é a assimetria de saída (sai no RSI 80, não sai na perda) aplicada a um ativo em alta, sem
custo. Em ouro, com custo real: líquido negativo em 4 de 5 timeframes nos defaults e **nenhuma das 119
células da grade bate comprar e segurar**. Ignorar.
