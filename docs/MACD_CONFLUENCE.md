# MACD Confluence Strategy (Trend + Pullback + Reversal) — teste em ouro (2026-10-21)

Estratégia: *"MACD Confluence Strategy (Trend + Pullback + Reversal Entries)"*, de blitz_locked
([TradingView](https://www.tradingview.com/script/PtmuSsWV-MACD-Confluence-Strategy-Trend-Pullback-Reversal-Entries/)).
Pine v6 aberto — baixei a fonte completa (`PUB;1c20606db61c434db6e5c6e8a8a6ae54`) e traduzi linha a
linha, com todos os defaults, em `scripts/study_macdconf.py`. Saída completa em
`scripts/study_macdconf.txt`, grade em `scripts/study_macdconf_grid.csv`.

A tese anunciada pelo autor é: *"MACD decides WHEN, the channel + higher timeframe decide WHETHER."*
Três gatilhos (T = cruzamento na tendência, P = pullback com re-aceleração, R = reversão na banda
externa), filtrados por EMA(200) com bandas de ATR, ADX/DI e o histograma MACD de 4h não repintante.

Dados: XAUUSD M1 da Dukascopy, 2017-09-01 → 2026-10-04 (9,1 anos, 2,66 M barras). Sinais no fechamento
do TF do gráfico, ordem a mercado na abertura seguinte, execução no M1 (stop, alvo, trilha e gap de fim
de semana resolvidos minuto a minuto). Custo 0,75 bp por perna (spread medido na Lighter) — o **próprio
Pine assume 0,05% = 5 bp por perna**, e reporto esse cenário também. Controle: para cada trade, 20
entradas a mercado em barras sorteadas, **mesmo lado**, mesmo risco relativo, **mesma gestão**
(break-even + trilha chandelier + alvo 3R) e mesma duração máxima — isola o gatilho de entrada com a
gestão neutralizada.

## Veredito

**Não aprovada. 0 de 864 combinações da grade dão R líquido positivo**, e nos defaults a estratégia
perde para uma entrada aleatória com a mesma gestão. Mas o achado mais útil veio antes dos números.

## 1. O script publicado tem um bug que apaga metade da estratégia

Linha 159 da fonte, lado a lado com a linha 163:

```pine
rawLA = useTrendX and crossDn and trendOkS and (not crossPullbackOnly or macdL < 0)   // COMPRA
rawSA = useTrendX and crossDn and trendOkS and (not crossPullbackOnly or macdL > 0)   // VENDA
```

A entrada "T" de **compra** usa `crossDn` + `trendOkS` — o gatilho da **venda**. Ou seja: compra no
cruzamento de **baixa** do MACD dentro de uma tendência de **baixa** confirmada. Deveria ser
`crossUp` + `trendOkL`.

E o efeito é pior que um sinal invertido. Como `shortA` exige `not longSig` (linha 175) e com o default
`crossPullbackOnly = false` as duas condições ficam **idênticas**, `longA` sempre ganha e **`shortA`
nunca dispara**. Medido no ouro/1h, bloco T:

| | longs | shorts |
|---|---|---|
| fiel ao publicado | 98 | **0** |
| corrigido (`crossUp` + `trendOkL`) | 100 | 98 |

No estado publicado, o bloco de tendência — o núcleo da tese do autor — só produz compras **contra** a
tendência, e o lado curto dele simplesmente não existe. Testei as duas versões em tudo que segue.

## 2. Nos defaults, perde dinheiro nas duas versões

TF 1h, stop 2 ATR, alvo 3R, break-even + trilha 2,5 ATR em +1R, saída no cruzamento contrário:

| | n | /ano | acerto | R bruto | custo R | **R líq** | PF | R/ano | exposição |
|---|---|---|---|---|---|---|---|---|---|
| fiel ao publicado | 1669 | 184 | 37,4% | −0,046 | 0,030 | **−0,076** | 0,85 | −14,0 | 50,5% |
| corrigido | 1723 | 190 | 38,0% | −0,026 | 0,031 | **−0,056** | 0,89 | −10,7 | 49,9% |

Corrigir o bug melhora, mas não salva: **−0,056R por trade**. A 1% de risco por trade são
**−10,7%/ano**, contra **+13,4%/ano** de simplesmente comprar e segurar ouro, com metade do tempo
exposto. Com os 5 bp/perna que o autor assume no próprio script: **−0,229R por trade, −43,5 R/ano**.

Abertura da versão corrigida:

| | n | acerto | R bruto | **R líq** | PF | R/ano |
|---|---|---|---|---|---|---|
| long | 713 | 41,2% | +0,052 | **+0,021** | 1,05 | +1,7 |
| short | 1010 | 35,6% | −0,080 | **−0,111** | 0,79 | −12,3 |
| T tendência | 172 | 38,4% | +0,070 | **+0,037** | 1,10 | +0,7 |
| P pullback | 110 | 42,7% | +0,010 | **−0,022** | 0,94 | −0,3 |
| R reversão | 1441 | 37,5% | −0,040 | **−0,070** | 0,86 | −11,1 |
| IS 70% | 1206 | 38,1% | −0,020 | −0,054 | 0,89 | −10,2 |
| OOS 30% | 517 | 37,7% | −0,039 | −0,062 | 0,87 | −11,7 |

Não há degradação IS→OOS: é ruim de forma estável em todo o período. Por ano, só 2019, 2023 e 2026
fecham positivos.

## 3. O problema é que 84% dos trades não passam por nenhuma "confluência"

Este é o ponto central. Dos 1723 trades, **1441 (84%) vêm do bloco R (reversão)** — e o bloco R é o
único que **não tem filtro nenhum**:

```pine
rawLC = useRev and tagLow and histTurnUp and close > open and close > close[1]
```

Sem regime (`trendOkL`), sem HTF, sem ADX, sem limite de extensão. A premissa anunciada — "o canal e o
timeframe maior decidem SE" — não se aplica à grande maioria das entradas que o script realmente toma.
Os dois blocos que passam pela confluência (T e P) somam 282 trades em 9 anos, 31 por ano.

Desligar a reversão é a **única** variante que vira positiva — e por uma margem irrelevante:

| variante (sobre o corrigido) | n | acerto | R bruto | **R líq** | PF | R/ano |
|---|---|---|---|---|---|---|
| **`REV = 0` (sem reversão)** | 307 | 41,0% | +0,078 | **+0,046** | 1,13 | **+1,5** |
| `SHORT = 0` (só compras) | 743 | 41,2% | +0,057 | +0,026 | 1,06 | +2,2 |
| `TRENDX = 0` (sem tendência) | 1635 | 37,2% | −0,050 | −0,080 | 0,84 | −14,4 |
| `PULLBACK = 0` | 1629 | 37,6% | −0,027 | −0,057 | 0,89 | −10,3 |
| `USEHTF = 0` (sem filtro de 4h) | 1820 | 38,3% | −0,020 | −0,051 | 0,90 | −10,2 |
| `MINADX = 0` (sem ADX) | 1810 | 37,2% | −0,031 | −0,062 | 0,87 | −12,4 |
| `TRAIL = 0` (sem trilha) | 1691 | 30,6% | −0,026 | −0,056 | 0,89 | −10,4 |
| `MOMOEXIT = 0` | 1558 | 41,0% | −0,028 | −0,058 | 0,90 | −10,0 |
| `MAXBARS = 24` (time stop) | 1772 | 38,4% | −0,032 | −0,063 | 0,87 | −12,2 |

Note também o que isso diz dos filtros anunciados: **tirar o HTF de 4h melhora o R bruto** (−0,020 vs
−0,026) e tirar o ADX piora pouco. Os filtros de "confluência" não estão selecionando nada —
basicamente só reduzem o número de trades.

E `REV = 0` não é uma estratégia: 34 trades por ano, +1,5 R/ano, contra +13,4%/ano do buy & hold.

## 4. Contra entrada aleatória: nada

Com a gestão idêntica (break-even, trilha, alvo 3R, mesma duração, mesmo lado, mesmo risco relativo),
a diferença entre o gatilho do script e uma barra sorteada:

| | aleatório | estratégia | diferença | t |
|---|---|---|---|---|
| todos | −0,003 | −0,026 | −0,022 | **−0,65** |
| long | +0,047 | +0,052 | +0,005 | 0,09 |
| short | −0,039 | −0,080 | −0,041 | −0,89 |
| T tendência | +0,017 | +0,070 | +0,053 | 0,65 |
| P pullback | +0,002 | +0,010 | +0,008 | 0,09 |
| R reversão | −0,006 | −0,040 | −0,034 | −0,86 |

Nenhum bloco chega perto de significância. O T, que é o único com sinal na direção certa (+0,053R,
t = 0,65), tem 172 trades em 9 anos — não dá para distinguir de ruído. Na versão fiel ao publicado o
T fica **negativo** contra o controle (−0,015), como esperado de um gatilho que compra em tendência
de baixa.

## 5. Grade de robustez: 0/864

TF (15m/30m/1h/4h) × stop (1/2/3 ATR) × alvo (1,5/3/5 R) × trilha (lig/des) × saída no cruzamento
(lig/des) × ADX mínimo (0/18/25) × versão (fiel/corrigida):

- **R líquido > 0: 0 de 864.** R bruto > 0: 29 de 864.
- Melhor célula: 4h, stop 1 ATR, alvo 5R, sem trilha, sem saída no cruzamento, sem ADX —
  R bruto +0,028, **R líq −0,003**, −0,18 R/ano com 570 trades. Empata com zero antes do custo.
- Por TF, R líq médio: 15m −0,106 · 30m −0,092 · **1h −0,078** · 4h −0,099.
- Por versão, R líq médio: fiel −0,094 · corrigida −0,093. **O bug não é o que quebra a estratégia** —
  ela não funciona nas duas versões.
- Stop mais curto gera mais trades e muito mais custo relativo (1 ATR: 0,079 R de custo por trade
  contra 0,025 R com 3 ATR), então −52 R/ano contra −20 R/ano. É o efeito do custo, não do sinal.

## 6. Notas de fidelidade

- **HTF não repintante, confirmado.** `htfCalc()` devolve `nh[1]` e entra por
  `request.security(..., lookahead_off)`, então o valor é o histograma da **penúltima** barra de 4h
  fechada. Duplo atraso — reproduzi exatamente assim. Não há vazamento de futuro aqui (ao contrário de
  vários scripts de MACD multi-timeframe).
- **Barra de entrada desprotegida (quirk fiel).** `strategy.exit` só é chamado quando
  `position_size != 0`, isto é, no fechamento da barra já preenchida — logo a barra de entrada fica sem
  stop e sem alvo. `PROT = 1` protege desde a entrada e muda 3 trades em 1723 (R bruto −0,02566 →
  −0,02571). Irrelevante.
- **Ordem stop/alvo no mesmo minuto é inerte aqui.** `ORD = 1` (otimista) dá resultado **idêntico** ao
  conservador: com stop de 2 ATR e alvo de 6 ATR, nenhum minuto de ouro abrange os dois.
- A normalização `squash()` (tanh em −100..+100) é só visual; é monotônica, então o sinal do histograma
  de 4h usado no filtro não muda. Todo o resto do script (tabela, bandas, marcadores, tint de barras)
  é visual e não entra em `longSig`/`shortSig`.

## Conclusão

Duas coisas separadas:

1. **O script como publicado está quebrado** — a compra do bloco de tendência usa o gatilho da venda, e
   isso silencia o lado curto desse bloco por completo. Quem rodar esse script no TradingView está
   vendo um backtest de algo diferente do que o autor descreve.
2. **Corrigir não cria edge.** A estratégia é dominada (84% dos trades) pelo único bloco que ignora
   toda a confluência anunciada, perde para entrada aleatória com a mesma gestão (t = −0,65) e não tem
   uma única célula positiva em 864. Tirar o bloco de reversão deixa sobrar 34 trades/ano e +1,5 R/ano
   — menos que comprar e segurar ouro, com risco de execução muito maior.

Reaproveitável do estudo: o controle com **gestão idêntica** (break-even + trilha + alvo, não só 1R/2R
fixo) é melhor que o controle dos estudos anteriores, porque separa o gatilho da gestão em estratégias
que trilham o stop. Vale usar esse formato daqui para frente.
