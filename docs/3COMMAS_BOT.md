# 3Commas Bot (Bjorgum) — ouro + OOS em US100/WTI/BTC/ETH

TradingView `MvlwAzSg`, Pine v5/v6, código aberto (fonte baixada do pine-facade,
`PUB;b3d1b9c1f597491390fb5eca58097871`). Tradução e teste em `scripts/study_commas.py`,
saída completa em `scripts/study_commas.txt`, grade em `scripts/study_commas_grid.csv`.

Dados: ouro M1 Dukascopy 2017-09 → 2026-10 (9,1 anos); OOS em US100/WTI (Dukascopy M1) e
BTC/ETH (Binance M1). Custo: spread da Lighter por perna (ouro 0,75 bp) + funding proporcional
ao tempo (o long paga, o short recebe).

## 1. O que o script realmente é

**Não é uma estratégia — é um template de webhook para bots do 3Commas.** O próprio autor
escreve no código, em cima do bloco de entrada:

> *"These conditions are the only thing that you would change to put in your own criteria."*

E o que vem de fábrica ali é:

```
validLongEntry  = ta.crossover (ma1, ma2) and not na(atr)
validShortEntry = ta.crossunder(ma1, ma2) and not na(atr)
```

Ou seja, o que se está testando é **cruzamento de EMA21 × EMA50 com bracket de ATR/pivô e RR 1:1**.
Todo o trabalho do script está no encanamento de risco, não numa ideia de entrada:

| peça | regra (default do Pine) |
|---|---|
| MAs | `ma1 = EMA(close, 21)`, `ma2 = EMA(close, 50)` (9 tipos à escolha: EMA/HEMA/SMA/HMA/WMA/DEMA/VWMA/VWAP/T3) |
| entrada | cruzamento no **fechamento** da barra, ordem a mercado na **abertura** da seguinte |
| stop | `lowest(low, 5) − ATR(14) × RiskM(1,0)` (espelhado no short) |
| alvo | `close_do_sinal + RnR(1,0) × (close_do_sinal − stop)` |
| trilha | `trailStop` = **false** por padrão; ligada, trilha `lowest(low,5) − ATR × 1,0` com ratchet |
| FLIP | **false** — sinal contrário com posição aberta é **ignorado**; só entra estando flat |
| tamanho | 10k fixos sobre 10k de capital (1x), comissão 0,05%/perna, 1 tick de slippage |

Detalhes que reproduzi fielmente: `lowest`/`highest` **incluem** a barra do sinal; o alvo é medido
do *close* do sinal mas a entrada é no *open* seguinte (então o RR efetivo não é exatamente 1,00);
`strategy.exit` é chamado em toda barra, logo — diferente dos scripts anteriores da fila — **a barra
de entrada já está protegida** (`PROT=1` é o default aqui, e `PROT=0` não muda nada: 501 trades
idênticos).

Nenhum bug relevante no código publicado. É um encanamento bem-feito com um gatilho vazio.

## 2. Defaults no ouro, 1h

| | n | /ano | acerto | R bruto | custo R | **R líq** | PF | R/ano | stop | expo |
|---|---|---|---|---|---|---|---|---|---|---|
| todos | 501 | 55 | 0,497 | +0,020 | 0,030 | **−0,010** | 0,98 | −0,5 | 79 bp | 38% |
| long | 241 | 27 | 0,544 | +0,132 | 0,123 | +0,009 | 1,02 | +0,2 | | 18% |
| short | 260 | 29 | 0,454 | −0,083 | −0,056 | −0,027 | 0,95 | −0,8 | | 20% |
| IS 70% | 351 | | 0,510 | +0,056 | | +0,023 | 1,04 | +1,2 | | |
| OOS 30% | 150 | | 0,467 | −0,064 | | **−0,085** | 0,84 | −4,7 | | |

- **−0,5 %/ano** a 1% de risco por trade, contra **+13,4 %/ano** do buy&hold no ouro, com 38% do
  tempo exposto. Com os 0,05%/perna que o próprio Pine assume, cai para **−7,4 R/ano**.
- 835 cruzamentos crus → 501 trades: o `FLIP=false` joga 40% dos sinais no lixo (o cruzamento
  contrário chega enquanto o bracket anterior ainda está aberto).
- Saídas 50/50 (251 stop, 249 alvo) com acerto 49,7% e RR 1:1 — exatamente o que um bracket
  simétrico produz quando a entrada não informa nada. O custo (0,030 R) é o que leva ao vermelho.
- Por ano: só 2020 (+16,1 R) e 2023 (+8,3 R) salvam; 2021, 2022, 2024, 2025 e 2026 todos negativos.

**Controle (entrada em barra aleatória, mesmo lado, mesmo risco relativo, mesmo alvo, mesma
gestão, mesma duração):** R bruto do controle **−0,009** vs estratégia **+0,020**, diferença
**+0,030 (t = 0,58)**. No long, +0,019 vs +0,132 (t = 1,42); no short, −0,035 vs −0,083 (t = −0,74).
**O cruzamento de médias não bate sortear a barra de entrada.**

## 3. Variantes (uma mudança por vez)

| variante | n | acerto | R bruto | R líq | R/ano |
|---|---|---|---|---|---|
| `ORD=1` (alvo antes do stop) | 501 | 0,497 | +0,020 | −0,010 | −0,5 |
| `PROT=0` | 501 | 0,497 | +0,020 | −0,010 | −0,5 |
| `FLIP=1` (inverte) | 835 | 0,425 | +0,019 | −0,014 | −1,3 |
| `TRAIL=1` | 741 | 0,389 | +0,027 | −0,008 | −0,6 |
| `TRAIL=1, USELIMIT=0` (só trilha) | 740 | 0,341 | +0,064 | **+0,031** | +2,5 |
| `TRAIL=1, RREXIT=0,6` (o do print do autor) | 581 | 0,484 | +0,001 | −0,030 | −1,9 |
| `RNR=2,0` | 326 | 0,356 | +0,091 | **+0,055** | +2,0 |
| `RNR=0,6` | 579 | 0,606 | −0,005 | −0,033 | −2,1 |
| `RISKM=1,2` | 474 | 0,513 | +0,055 | +0,030 | +1,6 |
| só long | 348 | 0,543 | +0,122 | −0,001 | −0,0 |
| só short | 334 | 0,461 | −0,117 | −0,059 | −2,2 |
| HEMA/SMA 50/100 (o print do autor) | 437 | 0,513 | +0,048 | +0,016 | +0,8 |

O padrão é inequívoco: **o que melhora o resultado é aumentar a assimetria do payoff** (RR ≥ 2,
tirar o limite e deixar a trilha correr), não nada que o gatilho faça. É o retrato de uma entrada
neutra dentro de um ativo que subiu 13%/ano.

## 4. Grade de robustez — 1152 células no ouro

TF (15m/30m/1h/4h) × tipo de MA (EMA/EMA, SMA/SMA, HEMA/SMA, HMA/EMA) × comprimentos (9/21, 21/50,
50/100) × RR (0,6/1/2/3) × ATR do stop (0,5/1/2) × trilha (on/off):

- **R líquido > 0 em 408/1152 (35%)** — pior que moeda. Bruto > 0 em 728/1152.
- Médias: 15m **−0,059 R** (o custo come tudo: 0,057 R por trade), 30m −0,018, 1h +0,002, 4h +0,024.
  Quanto mais rápido, mais negativo — assinatura de custo, não de sinal.
- Por RR: 0,6 → −0,033; 1,0 → −0,022; 2,0 → −0,007; 3,0 → **+0,010**. Monotônico no payoff.
- Melhor célula de todas: **+11,1 %/ano** (30m HEMA/SMA 9/21, RR 3, ATR 0,5) — ainda **abaixo do
  buy&hold de 13,4%**, com 89% de exposição.

### Checagem das 5 melhores células

| célula | n | R líq | R/ano | controle | t | IS | OOS | terços |
|---|---|---|---|---|---|---|---|---|
| 30m HEMA/SMA 9/21 RR3 ATR0,5 | 903 | +0,112 | +11,1% | +0,025 vs +0,147 | 1,92 | +0,078 | +0,191 | +0,13 / +0,01 / +0,19 |
| 30m EMA 50/100 RR2 ATR0,5 | 583 | +0,169 | +10,9% | +0,026 vs +0,230 | 1,87 | +0,193 | +0,114 | +0,30 / +0,12 / +0,09 |
| 1h HEMA/SMA 9/21 RR3 ATR0,5 trilha | 2070 | +0,047 | +10,8% | +0,005 vs +0,091 | 2,55 | +0,032 | +0,082 | +0,07 / −0,02 / +0,09 |
| 30m SMA 50/100 RR2 ATR1 | 711 | +0,133 | +10,4% | +0,009 vs +0,189 | 2,85 | +0,100 | +0,209 | +0,12 / +0,11 / +0,17 |
| 30m EMA 50/100 RR3 ATR0,5 | 523 | +0,176 | +10,1% | +0,027 vs +0,239 | 1,65 | +0,191 | +0,141 | +0,42 / −0,03 / +0,14 |

Nenhuma passa de t ≈ 2,9 **sendo o topo de 1152 tentativas** — é o máximo esperado sob a hipótese
nula com esse tanto de células. E nenhuma bate o buy&hold do próprio ativo.

### Vizinhança do bolso "MA lenta + alvo grande" (144 células, ouro)

MA lenta (30/70, 50/100, 70/150) × RR 1,5–3 × ATR 0,75–1,5 × 30m/1h: **109/144 positivas no
líquido**, mas **t médio vs o controle de apenas +0,85**, só 11/144 com t > 2, e o melhor
R/ano = **+6,7%**. O sub-bloco 1h SMA 50/100 é inteiramente *negativo* (até −0,187 R/trade) — a
superfície não tem platô, tem manchas.

## 5. OOS: a família promissora nos outros 4 ativos

Mesmas 48 células ("MA lenta 50/100 e 70/150, RR 2–3, ATR 0,75–1,0, 30m e 1h"), sem reotimizar:

| ativo | período | buy&hold | células R líq > 0 | t > 2 | t médio | R líq médio | melhor R/ano |
|---|---|---|---|---|---|---|---|
| ouro | 9,1 anos | +13,4%/ano | 39/48 | 7 | +1,14 | +0,082 | +11,6% |
| US100 | 9,7 anos | +20,4%/ano | 38/48 | 7 | +1,05 | +0,047 | +9,2% |
| WTI | 9,7 anos | +5,4%/ano | 24/48 | 1 | +0,35 | +0,010 | +6,3% |
| BTC | 6,7 anos | +43,9%/ano | 19/48 | **0** | +0,09 | −0,004 | +9,7% |
| ETH | 6,7 anos | +56,8%/ano | 37/48 | **0** | +0,56 | +0,040 | +12,2% |

Dois fatos matam a ideia:

1. **O t vs o controle desce junto com a tendência do ativo** (+1,14 no ouro, +1,05 no US100, +0,35
   no WTI, +0,09 no BTC). Se o cruzamento de médias carregasse informação, ela não escolheria
   justamente os ativos que subiram em linha reta. O que a família captura é **beta**.
2. **Em nenhum ativo a melhor célula bate o buy&hold** (11,6 vs 13,4; 9,2 vs 20,4; 9,7 vs 43,9;
   12,2 vs 56,8). A única exceção é o WTI (+6,3 vs +5,4), e ali o buy&hold é ruim enquanto o
   funding de 67,7%/ano **paga o lado short** — é subsídio de carrego, não entrada.

## 6. Veredito

**Sem edge. Reprovada.**

- A entrada de fábrica (cruzamento de médias) **não bate sortear a barra de entrada** com o mesmo
  bracket: t = 0,58 nos defaults do ouro, t médio +0,85 na vizinhança do melhor bolso, t ≤ 0 em
  várias fatias.
- Nos defaults do Pine o resultado no ouro é **−0,5 %/ano** contra **+13,4%** do buy&hold, e o
  OOS dos últimos 30% do período é o pior pedaço (−0,085 R/trade).
- Só 35% das 1152 células dão líquido positivo, e as que dão só melhoram **esticando o alvo**
  (RR 3 > RR 2 > RR 1 > RR 0,6, monotônico) — assimetria de payoff dentro de um mercado em alta,
  não informação do gatilho.
- Nos 15m o custo (0,057 R/trade) sozinho já afunda qualquer configuração.
- O teste é, na prática, uma confirmação do óbvio: **o script é um template de encanamento de risco
  e o autor nunca prometeu que o cruzamento de médias ganhasse dinheiro** — ele diz, no código, que
  é ali que você coloca o seu próprio critério. O encanamento (stop no pivô + ATR, alvo por RR,
  trilha com ratchet, gatilho da trilha por fração do alvo) é sólido e reaproveitável; o gatilho é
  placeholder.

**Único resíduo digno de nota, e não é da estratégia:** o lado short no WTI financiado a 67,7%/ano
de funding na Lighter é a mesma observação de carrego que já apareceu em outros estudos — vale como
ideia independente, não como validação deste script.
