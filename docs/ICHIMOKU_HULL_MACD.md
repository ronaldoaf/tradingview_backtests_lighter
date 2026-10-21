# Ichimoku + Daily-Candle_X + HULL-MA_X + MacD — teste em ouro (2026-10-21)

Estratégia: *"Ichimoku + Daily-Candle_X + HULL-MA_X + MacD"*, de SeaSide420
([TradingView](https://www.tradingview.com/script/RJBjyl2W-Ichimoku-Daily-Candle-X-HULL-MA-X-MacD/)).
Pine v4 aberto — baixei a fonte completa (`PUB;3177`) e traduzi linha a linha, com todos os defaults,
em `scripts/study_ichimoku.py`. Saída completa em `scripts/study_ichimoku.txt`, grade em
`scripts/study_ichimoku_xau_grid.csv`.

O autor descreve como *"custom Hull/MacD combination 420 special blend"*: quatro filtros em série
(HullMA + candle diário + nuvem Ichimoku + MACD de Hull) para compra e os quatro espelhados para venda.

Dados: XAUUSD M1 da Dukascopy, 2017-09-01 → 2026-10-04 (9,1 anos, 2,66 M barras). Sinal no fechamento
do TF do gráfico, ordem a mercado na abertura seguinte. Custo 0,75 bp por perna (spread medido na
Lighter) + funding 13,8%/ano pro-rata — e, como o **próprio script declara `commission_value = 0,25%`
por perna** e 1 tick de slippage, reporto esse cenário também. Controle: para cada trade, 20 entradas
a mercado em barras sorteadas, mesmo lado e mesma duração.

## Veredito

**Não aprovada. 0 de 55 células da grade batem o buy & hold do ouro**, que é o único comparativo que
importa para uma estratégia **sempre no mercado**. Mesma família do Hull Suite já reprovada
(`HULL_EMA_FLIP.md`): é um sistema de flip direcional com 100% de exposição.

## 1. O que o script realmente faz (três dos nomes no título não descrevem o que o código calcula)

Vale ler a fonte antes de olhar número nenhum:

```pine
price = input(defval=open)              // TODAS as fontes são a ABERTURA
hma1 = hma(price, Period)
hma2 = hma(price[1], Period)            // (a)
D1 = security(tickerid, "D", price,    barmerge.lookahead_off)   // (b)
D2 = security(tickerid, "D", price[1], barmerge.lookahead_off)
leadLine1 = avg(donchian(9), donchian(26))
leadLine2 = donchian(52)
longCondition = hma1>hma2 and D1>D2 and price>hma2 and leadLine1>leadLine2 and MACD>aMACD   // (c)
```

- **(a) "HULL-MA_X" não é cruzamento de duas médias.** `hma2` é a *mesma* HullMA defasada uma barra,
  então `hma1 > hma2` significa apenas "a HullMA está subindo". É um filtro de inclinação, não um cruzamento.
- **(b) "Daily-Candle_X" é 1 bit por dia, e do dia passado.** Com `lookahead_off`, dentro do dia em
  formação o `security` devolve o último dia **fechado** — logo a condição é "a abertura diária de
  ontem foi maior que a de anteontem". Correto (sem repintura e sem vazamento de futuro), mas é um
  filtro que muda de valor uma vez por dia.
- **(c) Não é a nuvem do Ichimoku.** `displacement = 26` aparece só nos `plot`. A condição compara
  `leadLine1` e `leadLine2` **não deslocadas**, ou seja, duas médias de Donchian na barra atual. O
  gráfico mostra uma nuvem projetada 26 barras à frente; a decisão usa outra coisa.
- **O "MacD" é de HullMA, não de EMA**: `hma(open,12) - hma(open,26)`, sinal `hma(MACD,9)`.
- **Não existe saída.** Os blocos de stop e alvo estão comentados na fonte. `pyramiding = 0`, então a
  posição só muda quando o lado oposto aparece: **exposição de 97% a 100% do tempo**, sempre comprado
  ou sempre vendido.

Nada disso é vazamento de futuro — o script é honesto nesse ponto. Mas o nome descreve uma coisa e o
código faz outra, e isso importa para quem acha que está comprando confirmação de quatro indicadores.

## 2. Defaults (Period 14): abaixo do buy & hold em todo timeframe

| TF | trades | /ano | bruto/trade | **líq/trade** | acerto | **CAGR** | B&H | Sharpe | DD | expo |
|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 931 | 102 | −0,3 bp | **−3,3 bp** | 40% | **−2,5%** | +13,4% | −0,15 | −56% | 100% |
| 30m | 673 | 74 | +4,8 bp | **+1,2 bp** | 38% | **+2,3%** | +13,4% | +0,13 | −41% | 100% |
| **1h** | 495 | 54 | +10,3 bp | **+7,3 bp** | 38% | **+6,9%** | +13,4% | +0,38 | −44% | 100% |
| 4h | 164 | 18 | +27,6 bp | **+13,2 bp** | 36% | **+2,3%** | +13,4% | +0,13 | −31% | 98% |
| 1D | 29 | 3,2 | +385 bp | **+294 bp** | 52% | **+6,4%** | +13,4% | +0,37 | −35% | 97% |

A melhor célula dos defaults (1h) rende metade do buy & hold, com drawdown de 44% e 100% de exposição.
O 1D tem 29 trades em 9 anos — amostra que não decide nada (t = +1,65 contra entrada aleatória).

**Com o custo que o autor declara no próprio script (0,25%/perna):**

| TF | líq/trade | o que sobra |
|---|---|---|
| 15m | **−51,8 bp** | t = −8,90 contra o aleatório |
| 30m | **−47,3 bp** | t = −6,57 |
| 1h | **−41,2 bp** | t = −4,14 |
| 4h | **−35,3 bp** | t = −1,16 |

Ou seja: nas configurações que o script mais usa (intradiário), a própria comissão que ele assume
destrói tudo. O resultado só respira porque eu uso o spread da Lighter (0,75 bp), que é ~30x menor.

Entrar na abertura da **própria** barra do sinal (legítimo aqui, já que todas as fontes são o `open` —
a condição está decidida no início da barra) melhora o bruto mas não muda o veredito: 1h vai a
+10,0 bp líquido e CAGR **+3,2%**, pior que o cenário fiel.

## 3. Abertura por lado: os dois lados valem o mesmo, e isso é o diagnóstico

TF 1h, cada lado isolado (o sinal contrário apenas zera):

| | trades | bruto/trade | **líq/trade** | CAGR | expo |
|---|---|---|---|---|---|
| só compra | 248 | **+35,6 bp** | +7,3 bp | +2,7% | 55% |
| só venda | 247 | **−15,1 bp** | +7,2 bp | +4,0% | 45% |

O bruto do lado curto é **negativo** (−15,1 bp): vender ouro perdeu dinheiro, como se espera num ativo
que subiu 13,4%/ano. O líquido do short só fica positivo porque **o short recebe funding** (13,8%/ano
na Lighter) — isto é, o lado vendedor é pago pelo carrego, não pelo sinal. Tirado o funding, não há
nada: o "blend" não distingue direção melhor que moeda.

## 4. Ablação: o conjunto é PIOR que as partes

Esta é a parte mais informativa. TF 1h, ligando/desligando cada bloco:

| variante | trades | bruto/trade | **líq/trade** | CAGR | Sharpe | t vs aleatório |
|---|---|---|---|---|---|---|
| **completa (default)** | 495 | +10,3 bp | **+7,3 bp** | +6,9% | +0,38 | +0,72 |
| sem o filtro diário | 771 | +17,5 bp | **+15,5 bp** | **+12,0%** | **+0,69** | **+4,18** |
| sem Ichimoku | 1059 | −1,7 bp | −4,2 bp | −1,4% | −0,08 | −0,37 |
| sem MACD | 531 | +10,9 bp | +7,7 bp | +5,3% | +0,30 | +0,72 |
| só Hull (inclinação) | 6592 | +1,3 bp | −0,5 bp | +3,3% | +0,20 | +1,81 |
| só o filtro diário | 1224 | −2,3 bp | −4,3 bp | −5,4% | −0,32 | −0,47 |
| só Ichimoku | 1077 | +13,0 bp | **+10,6 bp** | **+10,8%** | +0,60 | +1,85 |
| só MACD de Hull | 7491 | +0,1 bp | −1,3 bp | −10,7% | −0,67 | +0,55 |

Dois achados:

1. **Remover o "Daily-Candle_X" melhora tudo** (CAGR +6,9% → +12,0%, Sharpe 0,38 → 0,69). O filtro
   que o autor destaca no título é o que mais atrapalha — e faz sentido: "a abertura diária de ontem
   foi maior que a de anteontem" é um bit quase aleatório que só corta trades.
2. **O bloco Ichimoku sozinho (+10,6 bp, CAGR +10,8%) é melhor que os quatro juntos (+7,3 bp, +6,9%)**.
   A "confluência" dos quatro indicadores destrói valor em vez de somar. E mesmo o melhor recorte
   (sem diário: +12,0%) **continua abaixo do buy & hold de +13,4%**, com 100% de exposição e DD de 28%.

## 5. Grade de robustez: 0/55 batem o buy & hold

Period (7/14/21/28/56/100) × TF (15m/30m/1h/4h/1D) × lados × execução:

- líquido > 0: 42 de 55 — esperado, porque um sistema sempre-no-mercado num ativo que subiu 9 anos
  tende a capturar beta de um dos lados.
- líquido > 0 **e** acima do controle aleatório (t > 1): 12 de 55.
- **CAGR > buy & hold: 0 de 55.** Melhor CAGR da grade inteira: +6,8% (1D, Period 56), metade do B&H.
- As células com maior retorno por trade são todas 1D com 12 a 37 trades em 9 anos.

## 6. Notas de fidelidade

- `hma(open[1], n)` = `hma(open, n)` defasada 1 barra (a WMA é linear e invariante a deslocamento) —
  calculei assim, é exato.
- `donchian(n) = avg(lowest(low,n), highest(high,n))` com `low`/`high` como fontes default de
  `lowest`/`highest`. Confirmado contra a fonte.
- `security(..., "D", ..., lookahead_off)`: reproduzido como "abertura do último dia fechado",
  propagada barra a barra. Sem vazamento.
- `max_bars_back = 2999` e o slippage de 1 tick declarado no script não foram modelados — o slippage
  entraria *contra* a estratégia, então o resultado aqui já é otimista.

## Conclusão

Sistema de flip direcional sempre no mercado, com três dos quatro blocos fazendo algo diferente do que
o nome anuncia. **Não bate o buy & hold do ouro em nenhuma das 55 células testadas**, o lado curto só
sobrevive pelo funding, e a ablação mostra que o filtro-título (candle diário) *piora* o resultado
enquanto a nuvem Ichimoku sozinha supera o conjunto. Com a comissão de 0,25%/perna que o próprio
script declara, o intradiário perde 35 a 52 bp por trade.

Mesmo padrão de `flipma-study`: estratégia sem saída + exposição total = beta do ativo disfarçado de
estratégia. Ignorar.
