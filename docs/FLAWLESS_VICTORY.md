# Flawless Victory Strategy ("15min BTC Machine Learning Strategy") — teste em ouro e BTC (2026-10-21)

Estratégia: *"Flawless Victory Strategy (15min BTC) — Machine Learning Strategy"*, de Bunghole
([TradingView](https://www.tradingview.com/script/i3Uc79fF-Flawless-Victory-Strategy-15min-BTC-Machine-Learning-Strategy/)).
Pine v4 aberto — baixei a fonte completa (`PUB;1BVZuaaWOUGrbnKzHCECJiO5DMdrSK36`) e traduzi linha a
linha, com todos os defaults, em `scripts/study_flawless.py`. Saída completa em
`scripts/study_flawless.txt`, grades em `scripts/study_flawless_{xau,btc}_grid.csv`.

Testei nos dois ativos: **ouro** (padrão da fila) e **BTC**, que é o ativo declarado no título.

## Veredito

**Não aprovada.** No ouro: 3 de 110 células com retorno líquido positivo, **nenhuma** acima do
controle aleatório, **nenhuma** acima do buy & hold. No BTC: 88 de 110 positivas — mas **0 de 110
batem o buy & hold**, e o retorno vem todo do bull market de 2020–2022. Em 2022–2026 é negativa.

## 1. Não existe machine learning nenhum no script

Isto não é interpretação, é a fonte inteira. O script tem 4,6 KB e consiste em:

```pine
// RSI
len = 14 ; rsi = ...
// MFI
MFIlength = 14 ; mfi = ...
// v1 Bollinger: length1 = 20, mult1 = 1.0
// v2 Bollinger: length2 = 17, mult2 = 1.0
RSILowerLevel1 = 42 ; RSIUpperLevel1 = 70
RSILowerLevel2 = 42 ; RSIUpperLevel2 = 76
MFILowerLevel3 = 60 ; RSIUpperLevel3 = 65 ; MFIUpperLevel3 = 64
Buy_1  = close < lower1 and rsi > 42
Sell_1 = close > upper1 and rsi > 70
```

Bollinger + RSI (e MFI na v3), com **constantes cravadas no código**. Não há treino, não há estimação,
não há nada que se atualize com os dados. O único vestígio de "otimização" são os stops e alvos com
**três casas decimais** — 6,604% / 2,328% / 8,882% / 2,317% — que é a assinatura clássica de grade
varrida no próprio período do backtest. É *overfitting*, não aprendizado, e a precisão decimal é a
prova, não a credencial.

Três versões só-compra, selecionáveis por checkbox:

| | Bollinger | guarda de compra | guarda de venda | stop | alvo |
|---|---|---|---|---|---|
| v1 | SMA 20 ± 1,0σ | RSI > 42 | RSI > 70 | — | — |
| v2 | SMA 17 ± 1,0σ | RSI > 42 | RSI > 76 | 6,604% | 2,328% |
| v3 | SMA 20 ± 1,0σ | MFI < 60 | RSI > 65 **e** MFI > 64 | 8,882% | 2,317% |

**A guarda de venda está do lado errado da lógica.** Para sair, exige `RSI > 70/76` — ou seja, a
estratégia só vende quando o mercado está esticado para **cima**. Se o preço cair depois da compra, a
v1 **não tem saída nenhuma**: carrega o long até aparecer uma banda superior com RSI alto. É por isso
que a exposição fica em 76–92% e o acerto em 65–70% com expectativa ruim: ganhos pequenos frequentes,
perdas sem limite.

## 2. Ouro: negativa em todas as versões e todos os timeframes

Defaults, custo 0,75 bp/perna + funding 13,8%/ano:

| versão | TF | trades | /ano | bruto/trade | **líq/trade** | acerto | **CAGR** | B&H | Sharpe | expo |
|---|---|---|---|---|---|---|---|---|---|---|
| v1 | 15m | 1301 | 143 | +5,6 bp | **−3,2 bp** | 67% | **−5,9%** | +13,4% | −0,43 | 76% |
| v1 | 1h | 355 | 39 | +13,6 bp | **−12,7 bp** | 66% | −6,2% | +13,4% | −0,48 | 71% |
| v1 | 1D | 21 | 2,3 | +308 bp | **−50,0 bp** | 71% | −1,6% | +13,4% | −0,18 | 60% |
| v2 | 15m | 690 | 76 | +11,0 bp | **−6,4 bp** | 65% | **−6,2%** | +13,4% | −0,41 | 89% |
| v2 | 4h | 113 | 12 | +35,3 bp | **−47,3 bp** | 71% | −5,1% | +13,4% | −0,45 | 70% |
| v3 | 15m | 1791 | 197 | +2,5 bp | **−4,2 bp** | 66% | **−8,7%** | +13,4% | −0,66 | 74% |
| v3 | 1h | 471 | 52 | +2,1 bp | **−17,9 bp** | 63% | −9,4% | +13,4% | −0,76 | 70% |

**Grade do ouro: 3 de 110 células com líquido positivo, 0 com t > 1, 0 acima do buy & hold.** A melhor
célula da grade inteira (v2 1D sem stop/alvo) tem 16 trades em 9 anos e CAGR +4,0%.

## 3. BTC (o ativo do título): positiva, mas é beta de BTC e só até 2022

Defaults, custo 0,5 bp/perna + funding 10,9%/ano, 2020-01 → 2026-09:

| versão | TF | trades | /ano | bruto/trade | **líq/trade** | acerto | **CAGR** | B&H | Sharpe | t vs aleatório |
|---|---|---|---|---|---|---|---|---|---|---|
| v1 | 15m | 1497 | 222 | +12,6 bp | +7,6 bp | 69% | +7,8% | **+43,8%** | +0,12 | −0,64 |
| **v2** | **15m** | 1368 | 203 | +14,1 bp | **+8,7 bp** | 71% | **+18,0%** | **+43,8%** | +0,29 | +1,27 |
| v2 | 30m | 980 | 145 | +16,6 bp | +10,1 bp | 73% | **+20,2%** | +43,9% | +0,35 | +0,65 |
| v2 | 1h | 700 | 104 | +23,4 bp | +15,9 bp | 76% | +16,9% | +43,9% | +0,36 | +1,38 |
| v3 | 15m | 2576 | 381 | +8,2 bp | +5,1 bp | 70% | −9,6% | +43,8% | −0,15 | +0,97 |

Dois pontos matam o caso:

1. **Nenhuma das 110 células bate o buy & hold.** Melhor CAGR da grade: +20,2%, contra +43,8% de
   comprar BTC e não fazer nada — com 73% de exposição, drawdown de 78% e 145 trades por ano.
2. **Contra entrada aleatória com a mesma gestão (mesma duração, mesmo stop/alvo), o gatilho não
   acrescenta nada**: t = +1,27 na configuração do título, e **negativo** na v1 em todo TF. Ou seja,
   o que ganha dinheiro é estar comprado em BTC, não o sinal de Bollinger + RSI.

### Terços do período (v2 15min, a configuração do título)

| terço | período | trades | bruto/trade | **líq/trade** | **CAGR** | B&H | Sharpe |
|---|---|---|---|---|---|---|---|
| 1 | 2020-01 → 2022-04 | 599 | +30,8 bp | **+26,6 bp** | **+109%** | +129% | +1,05 |
| 2 | 2022-04 → 2024-07 | 404 | +1,5 bp | **−4,6 bp** | **−11,8%** | +14,7% | −0,24 |
| 3 | 2024-07 → 2026-09 | 366 | +0,8 bp | **−6,0 bp** | **−10,9%** | +13,2% | −0,24 |

Todo o resultado está no primeiro terço — o bull market de 2020–2021, que é exatamente o período em
que o script foi publicado e, portanto, aquele onde os decimais foram varridos. **Depois de 2022 a
estratégia perde dinheiro nos dois terços seguintes**, mesmo com BTC subindo ~14%/ano nos dois.
E mesmo no terço bom ela fica abaixo do buy & hold (+109% contra +129%).

## 4. Os decimais "otimizados" não são ótimos nem no BTC

Varri SL ∈ {2%, 4%, 6,60%, 8,88%, 15%} × TP ∈ {1%, 2,33%, 5%, 10%} na v2 e v3:

| ativo | config | default (6,604/2,328) | melhor da varredura |
|---|---|---|---|
| BTC 15m v2 | | +8,7 bp | **+9,2 bp** (SL 8,888% / TP 5%) |
| BTC 1h v2 | | +15,9 bp | **+40,5 bp** (SL 8,888% / TP 10%) |
| BTC 1h v3 | | −0,3 bp | **+12,1 bp** (SL 15% / TP 5%) |
| ouro 1h v2 | | −17,4 bp | −3,6 bp (SL 2% / TP 10%) → CAGR +0,3% |
| ouro 15m v2 | | −6,4 bp | −2,1 bp (ainda negativa) |

No 1h do BTC, o par default rende **1/3** do que um alvo de 10% renderia. Um parâmetro ajustado com
três casas decimais que é batido com folga por um número redondo não foi otimizado para nada que
sobreviva — é ruído do período de ajuste.

Desligar stop e alvo por completo (só os gatilhos de Bollinger + RSI/MFI) melhora o bruto no BTC
(v2 1h: +83,9 bp/trade) e **piora o CAGR** (+1,8%), porque os trades ficam enormes (9,3 dias) e a
exposição vai a 89% pagando funding. O stop/alvo não é a fonte do resultado nem o problema; o gatilho
simplesmente não contém informação.

## 5. Notas de fidelidade

- `ta.mfi(hlc3, 14)` com a degeneração do Pine (`MFIlower == 0 → 100`) reproduzida; no ouro usei o
  volume de ticks da Dukascopy, no BTC o volume da Binance.
- Bollinger com desvio **populacional** (`ta.stdev`, ddof = 0), como no Pine.
- `strategy.exit` das v2/v3 é chamado todo bar dentro do `if`, então stop e alvo valem **desde a barra
  de entrada**; modelei assim. Resolução minuto a minuto no M1, com a abertura de cada minuto testada
  antes do range (gap que pula o stop sai na abertura, pior que o stop) e **stop antes do alvo** quando
  os dois caem no mesmo minuto.
- `pyramiding = 0`: sinal de compra com posição aberta não faz nada. `strategy.close` sai na abertura
  da barra seguinte ao sinal.
- O script **não declara comissão nenhuma** (`strategy()` sem `commission_type`), então o backtest que
  aparece no TradingView é bruto. No ouro/15m da v3, o custo de 0,75 bp/perna já é 60% do bruto.

## Conclusão

Nome enganoso em duas camadas: não é *machine learning* (são sete constantes digitadas no código) e não
é *flawless* (no ativo e no timeframe do título, perde dinheiro nos últimos quatro anos e nunca bateu
comprar e segurar). O que o backtest bonito mostra é a interseção de três coisas: só-compra, num ativo
que multiplicou por 10 no período de ajuste, com saída que realiza ganhos pequenos e deixa a perda
correr — tudo isso sem custo.

No ouro: 0 de 110 células aproveitáveis. No BTC: positiva por beta, abaixo do buy & hold em 110 de 110
células, indistinguível de entrada aleatória com a mesma gestão, e negativa em 2022–2026. Ignorar.
