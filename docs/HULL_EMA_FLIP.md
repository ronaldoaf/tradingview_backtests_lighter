# Hull Suite Strategy + Backtest single EMA cross — sem edge

Testadas em 2026-10-21 no **ouro (XAUUSD)**, M1 da Dukascopy, 2017-09-01 → 2026-10-04
(9,1 anos, 2.664.019 barras; buy&hold **+13,4%/ano**).

- Fontes: `https://www.tradingview.com/script/Q9OQye4C-Hull-Suite-Strategy/` (InSilico/DashTrader) e
  `https://www.tradingview.com/script/j9rq1wQq-BUY-and-SELL-Backtest-single-EMA-cross-By-che-trader/`
- Pine aberto baixado do pine-facade (`PUB;p6LLNvabNCx9xxBVh43i5UtOrXQYEySv` e
  `PUB;A1eOoWMfLUJebdapPZlcgmUMI3UmzX5z`)
- Código: `scripts/study_flipma.py` · saída completa: `scripts/study_flipma.txt`,
  grade em `scripts/study_flipma_grid.csv`

## O que as duas são

As duas são **a mesma família**: sempre-no-mercado, invertendo a posição num sinal de linha de
tendência. **Sem stop, sem alvo, sem filtro, sem gestão de risco.**

| | Hull Suite | single EMA cross |
|---|---|---|
| linha | `HULL = HMA/EHMA/THMA(close, 55)` | `EMA(close,10)` vs `EMA(close,20)` |
| compra | `HULL[0] > HULL[2]` | `crossover(ema10, ema20)` |
| venda | `HULL[0] < HULL[2]` | `crossunder(ema10, ema20)` |
| direção default | `strat_dir="long"` → `allow_entry_in(long)`: a venda **só fecha** o long | ambos os lados |

Como o `if` do Hull roda em toda barra e `strategy.entry` com o mesmo id é ignorado estando no
mesmo lado, as duas se reduzem a "posição desejada = sinal no fechamento, executada na **abertura
da barra seguinte**" — exatamente o que o motor implementa. Não há nada intrabarra a resolver.

Custo aplicado: spread da Lighter por perna (ouro 0,75 bp) + funding 13,8%/ano pro-rata do tempo
(o long paga). Controle: para cada trade, 20 trades sorteados com o **mesmo lado e a mesma duração
em barras**, começando em barras aleatórias.

## Resultado: sem edge

**Defaults, 4h:**

| | n | acerto | bruto/trade | custo | líq/trade | PF | CAGR líq | CAGR bruto | exposição |
|---|---|---|---|---|---|---|---|---|---|
| Hull (long-only) | 261 | 0,356 | +0,366% | 0,256% | **+0,110%** | 1,18 | **+2,6%/ano** | +10,4% | 50,2% |
| EMA cross (2 lados) | 475 | 0,301 | +0,163% | 0,014% | **+0,150%** | 1,25 | **+6,9%/ano** | +7,6% | 99,7% |

Contra **+13,4%/ano** do buy&hold. Ou seja: as duas ficam 2 a 5 vezes abaixo de simplesmente
comprar e segurar o ouro, enquanto giram 29 e 52 trades por ano.

**Nenhuma das 360 células da grade** (2 famílias × 6 TFs de 15m a 1W × 3 direções × variações ×
comprimentos) bate o buy&hold no retorno composto líquido — 0/360. O melhor caso da grade é
Hull/Thma/180 em 30m com +11,4%/ano, ainda abaixo, e com 158 trades/ano.

**Contra o controle aleatório** (mesmo lado, mesma duração, barra de entrada sorteada):

- Hull: controle +0,272% vs estratégia +0,366% → diferença +0,094% (**t = 0,74**)
- EMA cross: controle +0,052% vs +0,163% → diferença +0,111% (**t = 1,13**);
  long t = 0,90, short t = 0,69

Isto é, o momento em que a linha vira não informa nada: entrar em barra aleatória com o mesmo
perfil de exposição rende praticamente o mesmo.

## Por que não funciona

1. **É beta com giro.** O que sobra do resultado é a tendência do ouro filtrada pela exposição: o
   Hull default fica long 50% do tempo e captura ~metade da alta, menos custo. A média da grade por
   direção confirma — `all` +2,1%, `long` +1,4%, `short` +0,6% de CAGR; o lado short é bruto
   negativo em quase toda a grade (média −1,06%/trade) e só não é pior porque **recebe funding**.
2. **Taxa de acerto de 30–36%** sem nenhum mecanismo de payoff: não há stop nem alvo, então a
   assimetria vem só do fato de que a tendência às vezes dura. É a mesma falha do
   [[sma30-video-study]].
3. **Instabilidade temporal.** O Hull tem IS (70% inicial) **negativo** (−0,027%/trade, PF 0,96) e
   OOS positivo (+0,430%, PF 1,72) — o resultado inteiro vem de 2025 (+31% dos +28,7% somados do
   período). O EMA cross é o espelho: 2018–2020 somam −30%, 2021–2026 somam +94%.
   Cinco melhores trades de 475 respondem por +51,9% de +71,2%.
4. **Custo mata os TFs rápidos.** Média por TF no CAGR: 15m **−4,0%**, 30m +1,8%, 1h +4,0%,
   4h +1,9%, 1D +1,1%. Em 1W as células têm 1 a 20 trades em 9 anos — números bonitos
   (até +24,7%/trade) sem amostra nenhuma.
5. **O `strat_dir="long"` do Hull é honesto mas enganoso no backtest do TradingView**: como a venda
   só fecha, o gráfico de equity parece uma curva de tendência bem comportada, mas é um long
   intermitente de ouro — e com funding de 13,8%/ano na perna comprada, o custo come 0,256% por
   trade, ~70% do bruto.

## Veredito

Nenhuma das duas passa. Sem extensão para US100/BTC/WTI/ETH (protocolo: só se o ouro for positivo —
aqui as duas são positivas no absoluto, mas perdem do buy&hold e empatam com entrada aleatória, o
que é reprovação).
