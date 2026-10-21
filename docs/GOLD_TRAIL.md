# Gold Trend Trail [XAUUSD] — teste em ouro (2026-10-21)

Estratégia: *"Gold Trail [XAUUSD] — Regime-Gated Adaptive ATR Strategy"*, de `blitz_locked`
([TradingView](https://www.tradingview.com/script/be5yqBM1-Gold-Trail-XAUUSD-Regime-Gated-Adaptive-ATR-Strategy/)).
Código Pine v6 é aberto — baixei a fonte completa (`PUB;d33eb1136204448983b8f3eb67b28bc6`) e traduzi
linha a linha, com todos os defaults, em `scripts/study_goldtrail.py`.

Dados: XAUUSD M1 da Dukascopy, 2017-09-01 → 2026-10-04 (9,1 anos, 2,66 M barras). Sinais no TF alto,
execução no M1 (stop/alvo/gap de fim de semana resolvidos minuto a minuto). Custo 0,75 bp por perna
(spread medido na Lighter); o próprio Pine assume `slippage = 20` ticks, da mesma ordem de grandeza.
Controle: para cada trade, 20 entradas a mercado em minutos sorteados, **mesmo lado**, mesmo risco
relativo, mesma estrutura 1,2R/3R com parcial e mesma duração máxima.

## Veredito

**Não aprovada.** No conjunto, a estratégia é positiva mas pequena e estatisticamente fraca, e o pouco que
entrega é **beta do ouro, não alfa**: perde do buy & hold por uma margem larga.

| | n | /ano | acerto | R bruto | custo R | **R líq** | PF | R/ano | exposição |
|---|---|---|---|---|---|---|---|---|---|
| todos | 375 | 41 | 42,9% | +0,074 | 0,016 | **+0,059** | 1,16 | +2,4 | 34,7% |
| long | 192 | 21 | 50,5% | +0,199 | 0,016 | **+0,183** | 1,53 | +3,9 | 18,7% |
| short | 183 | 20 | 35,0% | −0,056 | 0,015 | **−0,071** | 0,83 | −1,4 | 16,0% |
| IS 70% | 262 | 41 | 43,9% | +0,081 | 0,017 | +0,064 | 1,18 | +2,6 | |
| OOS 30% | 113 | 41 | 40,7% | +0,058 | 0,011 | +0,047 | 1,12 | +1,9 | |

Nos defaults (1h, `rankMin` 65, trilha 2,6 ATR), com 1% de risco por trade: **+2,4%/ano** contra
**+13,4%/ano** de simplesmente comprar e segurar ouro no mesmo período, ficando 35% do tempo exposto.
Para igualar o buy & hold seria preciso arriscar 5,5% por trade, o que levaria o drawdown máximo
observado a 39% do capital e o pior trade a −16%.

### 1. O lado short destrói; o long é quase todo beta

- **Short: −0,071R por trade, PF 0,83.** O controle aleatório short no mesmo período rendeu −0,068R.
  Ou seja, o short não é ruim por erro da estratégia — é ruim porque vender ouro em 2017–2026 foi ruim,
  e os filtros não evitaram nada (diferença contra o controle +0,012R, t = 0,18).
- **Long: +0,199R bruto.** Mas uma entrada *aleatória* comprada, com o mesmo risco, a mesma estrutura
  1,2R/3R e a mesma duração, rendeu **+0,081R**. A estratégia acrescenta +0,118R com **t = 1,54** —
  sugestivo, não comprovado. Quase metade do resultado long é só o ouro subindo.
- Agregando os dois lados, a diferença contra o controle é +0,066R, t = 1,30. Nada significativo.

### 2. O lucro vive em pouquíssimos trades

Os **5 melhores trades (de 375) respondem por 62% do lucro total**. A mediana do R líquido é **−0,19R**:
o trade típico perde. É o perfil esperado de seguimento de tendência, mas com só 375 trades em 9 anos
significa que o resultado não é distinguível de sorte — 4 dos 10 anos fecham negativos (2017, 2019,
2023 e 2026 até agora).

### 3. O timeframe que o autor recomenda é o pior

O autor indica "15 min a 1 h". Na grade de 216 combinações (TF × percentil de armar × distância da
trilha × filtro EMA × filtro S/R × convenção de proteção):

| TF | R líq médio | R/ano médio | células positivas |
|---|---|---|---|
| 15 min | **−0,020** | −4,0 | 8 / 72 |
| 30 min | −0,002 | −0,7 | 37 / 72 |
| 1 h | +0,033 | +1,6 | **68 / 72** |

Em 15 min o problema não é custo: o R **bruto** já é só +0,012, abaixo do que o custo come (0,039).
A estratégia só existe em 1h — e nas melhores células da grade o filtro de pivô S/R está **desligado**,
ou seja, ele não contribui.

### 4. Risco de cauda acima do planejado

**44 dos 375 trades (12%) perderam mais de 1R**, o pior deles **−2,94R**. Duas causas, as duas reais:
gaps de fim de semana / abertura que atravessam a trilha, e um detalhe fiel ao Pine — `strategy.exit` só
é chamado no fechamento da barra, então **a barra de entrada fica sem stop e sem alvo**. Testei a variante
que protege desde a entrada (`PROT=1`): muda pouco o resultado médio (+0,066 vs +0,059R), mas é mais honesta.
O autor avisa disso na descrição; vale confirmar que o leitor entendeu que "1% de risco" não é teto.

### 5. Variantes testadas (1h, defaults nos demais parâmetros)

| variante | n | acerto | R bruto | R líq | PF | R/ano |
|---|---|---|---|---|---|---|
| defaults | 375 | 42,9% | +0,074 | +0,059 | 1,16 | +2,4 |
| alvo antes do stop na mesma barra (otimista) | 375 | 42,9% | +0,074 | +0,059 | 1,16 | +2,4 |
| stop/alvo ativos já na barra de entrada | 375 | 42,9% | +0,081 | +0,066 | 1,18 | +2,7 |
| `dormExit = true` (sai quando o regime dorme) | 427 | 45,9% | +0,066 | +0,050 | 1,22 | +2,4 |
| sem filtro de sessão | 523 | 41,9% | +0,074 | +0,058 | 1,15 | +3,4 |

Nenhuma muda o quadro. A convenção de resolução intrabarra é irrelevante aqui porque o stop fica a
~103 bp (mediana), longe o bastante para stop e alvo raramente caberem no mesmo minuto.

### 6. O único candidato que sobra (fraco)

**Só long, em 1h**: +0,183R líquido por trade, 21 trades/ano, +3,9R/ano, DD máximo 5,2R
(R/ano por DD = 0,74), e aguenta a divisão temporal — IS +0,154R, OOS +0,249R (t = 1,72), últimos
24 meses +0,197R. Mas:

- o controle aleatório comprado no mesmo período já dava +0,081R, então o alfa real é ~+0,12R com t = 1,54;
- a 3,5% de risco por trade (necessário para igualar o buy & hold) o DD vai a 18% e o pior trade a −10%,
  isto é, mais risco e mais complexidade para empatar com segurar ouro;
- "só long" é uma escolha feita *depois* de ver que o short perdeu. Em 9 anos de bull market de ouro,
  desligar o short é quase a definição de ajuste ao passado.

## Conclusão

A tradução do Pine está fiel e o teste é limpo, mas não há o que colocar em produção. O regime por
percentil do Efficiency Ratio de fato reduz o número de trades e evita o pior do lado short, só que o
que resta é um long de seguimento de tendência que não bate comprar ouro, com 62% do lucro em 5 trades e
diferença contra entrada aleatória que não passa de t = 1,5. Mesmo diagnóstico das últimas estratégias
de vídeo/TradingView testadas aqui (SMA30, SMC, CRT, Ruiz MTF): o filtro bonito não cria borda.

Arquivos: `scripts/study_goldtrail.py`, `scripts/study_goldtrail.txt` (saída completa),
`scripts/study_goldtrail_xau_trades.csv` (375 trades), `scripts/study_goldtrail_grid.csv` (216 combinações).
