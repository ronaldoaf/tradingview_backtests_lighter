# Lote 9 do TradingView: 5 estratégias (2026-10-22)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops, alvos e ordens limite resolvidos no M1 (stop antes do alvo no mesmo
minuto). Custo 0,75 bp/perna + funding 13,8% a.a. (o long paga, o short recebe). Controle: mesmo
lado e mesma duração.

Código: `scripts/study_tvlote9.py` (saída `results/study_tvlote9.txt`, grade
`results/study_tvlote9_xau_grid.csv`) e `scripts/study_tvlote9_rob.py` (robustez,
`results/study_tvlote9_rob.txt`). Fontes em `pine/`. Triagem: o MicuRobert e o RSI vs SMA são
Pine v2, mas sem `security()`; o único `security()` do lote (UT Bot) é para Heikin Ashi, desligado
por padrão.

**Veredito: 5 testadas, 5 reprovadas no ouro.** Só uma variante passa o B&H em CAGR: o RSI versus
SMA **invertido** (o default faz o contrário e perde), e ela repete o padrão do lote 8. Perde
dinheiro no terço lateral de 2021-24 e cai abaixo do B&H com custo 2×. Nenhuma foi estendida.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 47 | [RS] MicuRobert EMA cross V2 (`6YthKHw1`) | 425 | 93 | 4 | 0 | +9,8% |
| 48 | UT Bot alerts strategy (`R9nsvSZR`) | 312 | 100 | 11 | 0 | +12,6% |
| 49 | RSI versus SMA (`wDLCPh1I`) | 181 | 85 | 10 | 2 | +14,8% (invertido) |
| 50 | Hull Moving Average Swing Trader (`j60hYGuY`) | 44 | 36 | 9 | 0 | +11,5% |
| 51 | ICT Entry V2 [TS_Indie] (`wm9e7Wca`), núcleo | 188 | 7 | 0 | 0 | +0,3% |

B&H do ouro no período: +13,4% a.a., Sharpe diário 0,73.

---

## 47. [RS] MicuRobert EMA cross V2 (`6YthKHw1`, Pine v2)

ZLEMA(open, 5) × ZLEMA(open, 34), mais reentrada quando o open cruza a rápida a favor da lenta; só
entra na sessão 04–15h. Saída (no fechamento) por trailing de 22 pips sobre a máxima desde a entrada ou
alvo de 55 pips. Feito para forex: no ouro 22 pips ≈ 0,1% do preço, que é ruído intrabarra. Default:
de 140 a 4800 trades/ano, bruto ≈ 0, **−3% a −53% a.a.** Com stop de 2% e sem sessão vira um
cruzamento de médias quase sempre posicionado: +9,8% no 1h, abaixo do B&H.

## 48. UT Bot alerts strategy (`R9nsvSZR`, Pine v5)

UT Bot (key 3, ATR 1) com filtro de EMA200; stop em 1,5 ATR14; o stop vai ao preço de entrada
depois de 0,75R; metade sai em 3R; sinal contrário fecha só se estiver no lucro. O breakeven cedo
derruba o acerto para 15–34%: o default faz de −11% a +4% a.a. A melhor célula (key 3, stop 3 ATR,
sem EMA, 30m) faz +12,6% com 62% de exposição, sem bater o B&H. (O UT Bot puro já tinha reprovado no
lote 3.)

## 49. RSI versus SMA (`wDLCPh1I`, Pine v2)

RSI8 do open − 50 e sua SMA34; o default **compra quando a SMA fica ≤ 0** (reversão) e vende quando
volta acima; sempre no mercado. O trailing publicado (120 ticks sem offset) não arma; os stops
testados não ajudaram. Default: −3% a −18% a.a., t até −4,2 contra o controle. É um sinal anti-edge, e
a versão **invertida** (seguir a SMA do RSI) é a única célula do lote acima do B&H:

| Célula | 2017-21 (B&H 8,5%) | 2021-24 (4,7%) | 2024-26 (31,5%) | 2ª metade (25,1%) | custo 2× | custo 4× |
|---|---|---|---|---|---|---|
| 30m RSI8/SMA34 | +14,3% | **−4,0%** | +40,1% | +27,5% | +11,3% | +4,4% |
| 30m RSI14/SMA34 | +15,5% | **−5,2%** | +38,8% | +23,5% | +11,5% | +5,9% |
| 1h RSI8/SMA34 | +11,6% | **−7,1%** | +16,6% | +7,3% | +5,3% | +2,1% |

Um seguidor de tendência sempre posicionado com ~200 trades/ano: ganha nas tendências, perde no
lateral, e o excesso de 1,4 ponto some com custo 2×. O 1h já fica bem abaixo do B&H. Reprovada.

## 50. Hull Moving Average Swing Trader (`j60hYGuY`, Pine v4)

HMA(open, 210) contra a mesma HMA do open anterior; as linhas c1/c2 somam a diferença da HMA ao
preço e uma retração fixa de 2 unidades de preço (feita para um ativo específico). Sempre no mercado.
Default: +8,5% (15m), +5,3% (30m), +5,5% (1h), t ≈ +2 a +2,6 contra o controle, mas nenhum dos 44
chega ao B&H (melhor +11,5%, HMA100 no 30m).

## 51. ICT Entry V2 [TS_Indie] (`wm9e7Wca`, Pine v6) — núcleo

O script tem 1283 linhas (arrays de FVG/iFVG, estrutura interna, várias regras de cancelamento).
Foi reproduzido o núcleo: varredura de um pivô de liquidez (força 5) com fechamento de volta, depois
um iFVG a favor (FVG contrário invalidado pelo close) além do nível varrido, ordem limite na borda
do iFVG, stop na outra borda ± 0,5 ATR50, alvo 3R, tendência pela última quebra de pivô de força 10.
Os filtros finos (gap FVG–iFVG, premium/discount, sessões) não foram copiados.

Default: 20 a 270 trades/ano, acerto 23–29% com RR 3 (o empate exige 25%), **bruto de −1,3 a −0,1
bp por trade**. 7/188 células com líquido positivo, nenhuma com t > 2; melhor +0,3% a.a. Nos lotes
anteriores, ICT 2022 e ICT Master Suite reprovaram do mesmo jeito.
