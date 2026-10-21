# Bollinger + RSI, Double Strategy (by ChartArt) v1.1 — ouro + OOS

TradingView `uCV8I4xA`, Pine v2, código aberto (extraído do HTML da página, campo `script.content`;
o pine-facade não serve scripts tão antigos). Tradução e teste em `scripts/study_bbrsi.py`.
Dados: ouro M1 Dukascopy 2017-09 → 2026-10 (9,1 anos); OOS em US100/WTI (Dukascopy M1) e BTC/ETH
(Binance M1). Custo: spread da Lighter por perna (ouro 0,75 bp) + funding proporcional ao tempo
(ouro 13,8 %/ano pago pelo long, recebido pelo short).

## O que a estratégia é

```
vrsi  = rsi(close, 6)
BB    = sma(close, 200) ± 2·stdev(close, 200)
long  : crossover(vrsi, 50)  E crossover(close, BBlower)   na MESMA barra
short : crossunder(vrsi, 50) E crossunder(close, BBupper)  na MESMA barra
```

Dois detalhes do código publicado que mudam tudo:

1. **`RSIoverSold = RSIoverBought = 50`.** Não há sobrecompra/sobrevenda nenhuma: o filtro de RSI é
   só "RSI(6) cruzou 50", ou seja, o próprio sinal do último movimento. A descrição ("só dispara
   quando RSI e Bollinger estão os dois em condição de sobrecompra/sobrevenda") não corresponde ao
   código — o autor fixou os níveis em 50 na v1.1 "para simplificar".
2. **Não existe saída.** Nenhum `strategy.exit`, `strategy.close`, stop, alvo ou time stop. Com
   `pyramiding=0`, a posição só muda quando o sinal contrário aparece. Depois do primeiro sinal o
   sistema fica **sempre no mercado** (exposição medida: 93–100 %), invertendo long↔short a cada
   algumas semanas (duração média 28–45 dias no 1h).

Isso é um sistema de inversão 1x sem gestão de risco, não um sistema de trades com 1R. Por isso aqui
a medição é em retorno sobre o nocional e o parâmetro de comparação é **buy & hold** (o sistema fica
praticamente 100 % investido) e um **controle aleatório com a mesma estrutura** (mesmo número de
inversões, mesma alternância de lados, instantes sorteados).

As ordens `strategy.entry(..., stop=BBlower)` são inócuas: no long o stop de compra fica *abaixo* do
preço (o close acabou de cruzar a banda para cima), então a ordem já está ativada e preenche na
abertura da barra seguinte. Testei também entrada no fechamento do sinal (`EXEC=1`): resultado
idêntico (−50 bp vs −49 bp bruto no 1h).

## Ouro, defaults (RSI 6 / BB 200)

| TF | trades | /ano | dias | bruto/trade | líq/trade | CAGR 1x | B&H | Sharpe | DD (log) | exposição |
|----|--------|------|------|-------------|-----------|---------|-----|--------|----|----|
| 15m | 306 | 33,6 | 11 | −22 bp | −23 bp | −7,7 % | +13,4 % | −0,48 | −95 % | 100 % |
| 30m | 157 | 17,3 | 21 | −24 bp | −15 bp | −2,8 % | +13,4 % | −0,17 | −60 % | 99 % |
| **1h** | 76 | 8,4 | 43 | **−49 bp** | −2 bp | +0,4 % | +13,4 % | +0,02 | −47 % | 98 % |
| 4h | 18 | 2,0 | 175 | −529 bp | −282 bp | −2,7 % | +13,4 % | −0,17 | −74 % | 95 % |

Nos defaults a estratégia é **negativa no bruto em todos os timeframes** e perde do buy & hold por
13 pontos ao ano em qualquer um deles. O "líq" acima do "bruto" no 1h/30m/4h não é mágica: é o
funding do ouro na Lighter sendo *recebido* porque o sistema passa a maior parte do tempo vendido
(sem funding, 1h = −51 bp/trade). Ou seja, o pouco que sobra vem do carrego, não do gatilho.

Testar um lado só exige inventar uma saída que o script não tem (uso "sinal contrário zera para
flat"): long-only no 1h dá +128 bp bruto/trade, mas o controle aleatório comprado no mesmo período
já dá +53 bp e o funding de 13,8 %/ano em 30 dias de carregamento (−114 bp) come o resto → +14 bp
líquidos, t = −1,46 contra o controle. É beta do ouro, como em [[goldtrail-study]].

## Grade de parâmetros (ouro)

69 células (TF × RSI 4/6/9/14 × BB 50/100/200/400): **9 com retorno líquido > 0**, só **3** também
acima do controle com t > 1. As duas melhores têm 7 e 11 trades em 9 anos. A única região
minimamente coerente é **1h com BB curta (80–120)**:

| 1h | bruto/trade | líq/trade | CAGR | Sharpe | DD | t vs controle |
|----|------|------|------|--------|----|------|
| RSI6/BB80 | +64 bp | +61 bp | +6,2 % | +0,39 | −29 % | +1,05 |
| RSI6/BB100 | +61 bp | +68 bp | +8,9 % | +0,50 | −30 % | +2,00 |
| RSI6/BB110 | +52 bp | +69 bp | +9,2 % | +0,52 | −34 % | +1,78 |
| RSI6/BB150 | −54 bp | −29 bp | −1,5 % | −0,09 | −53 % | −0,43 |
| RSI6/BB200 (default) | −49 bp | −2 bp | +0,4 % | +0,02 | −47 % | +0,06 |

A ilha existe mas **nunca bate o buy & hold** (melhor caso 9,2 % contra 13,4 %), com Sharpe 0,5 e
30 % de drawdown — pior que comprar e dormir. E o default publicado (BB 200) está fora dela.

## OOS da ilha (1h) nos outros ativos

| ativo | BB 100 líq/trade | CAGR | BB 200 líq/trade | CAGR | B&H | melhor t |
|-------|------------------|------|------------------|------|-----|----------|
| US100 | +53 bp | +3,3 % | +10 bp | +0,7 % | +20,3 % | +0,75 |
| WTI | +50 bp | +7,9 % | +106 bp | +5,3 % | +5,4 % | +0,74 |
| BTC | −127 bp | −19,8 % | −163 bp | −12,3 % | +43,9 % | −1,13 |
| ETH | +43 bp | +32,2 % | −373 bp | −28,3 % | +56,8 % | +0,39 |

Nenhum ativo bate o buy & hold, nenhum passa de t = 0,75 contra o controle aleatório, BTC é
francamente negativo e o default (BB 200) inverte de sinal entre ativos (+106 bp no WTI, −373 bp no
ETH). Os drawdowns em log passam de 100 % em BTC/ETH/WTI, isto é, ruína a 1x.

## Veredito

**Sem edge.** O gatilho é "RSI(6) cruzou 50 junto com o preço cruzando a banda de 2σ" — um filtro de
momento de curtíssimo prazo colado num gatilho de reversão à média, sem sobrecompra/sobrevenda
nenhuma (níveis fixos em 50) e sem qualquer saída. O que o backtest do TradingView mostra é
essencialmente a exposição direcional de ~100 % ao ativo, não um alfa: em todo ativo testado o
sistema fica atrás do buy & hold, e contra entradas aleatórias com a mesma estrutura o melhor caso
do ouro chega a t = 2,0 em 1 célula de 69 (compatível com acaso) e o default a t = +0,06.
