# Lote 6 do TradingView: 5 estratégias (2026-10-21)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops, alvos e ordens stop de entrada resolvidos no M1 (stop antes do alvo no
mesmo minuto). Custo 0,75 bp/perna + funding 13,8% a.a. (o long paga, o short recebe).
Controle: mesmo lado e mesma duração, aberto-a-aberto.

Código: `scripts/study_tvlote6.py` (saída `results/study_tvlote6.txt`, grade
`results/study_tvlote6_xau_grid.csv`). Fontes em `pine/`.

**Veredito: 4 testadas, 4 reprovadas no ouro; 1 não reproduzida.** 1.464 células, **0** acima do
buy & hold (+13,4% a.a.). Nenhuma foi estendida aos outros ativos.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 32 | Hammers & Stars v1.2 (ZenAndTheArtOfTrading, `t776tkZv`) | 545 | 125 | 1 | 0 | +7,3% |
| 33 | Iron Support Resistance / Scalping S/R (HPotter, `gp332Dao`) | 365 | 67 | 2 | 0 | +5,6% |
| 34 | Bollinger Band with RSI (`pKOaIHpb`) | 304 | 26 | 0 | 0 | +1,1% |
| 35 | ICT Master Suite (Trading IQ, `ABYnIcdl`) | — | — | — | — | não reproduzida |
| 36 | SUPERTREND ATR with Trailing Stop Loss (`L9GkARD2`) | 250 | 145 | 16 | 0 | +6,2% |

---

## 32. Hammers & Stars (`t776tkZv`, Pine v6)

Martelo = corpo inteiro no terço superior da vela, range ≤ 3 ATR; estrela espelhada. Entra a
mercado, stop no menor low das 2 últimas velas − 1 ATR, alvo 1R; só entra sem posição.

Defaults: acerto de 49–50% com RR 1:1, ou seja moeda. O bruto por trade fica em ~0 bp em todos os
TFs (−8,9% a.a. no 15m com 900 trades/ano, +2,3% no 4h). Grade (stop 0,5/1/2 ATR × RR 1/1,5/2 ×
fib 0,333/0,25 × EMA 0/50/200 × long/ambos): a melhor faz +7,3% a.a. (1h, stop 2 ATR, RR 2, EMA 50).
O sizing de 1% de risco do script muda o tamanho, não o sinal.

## 33. Iron Support Resistance Automat (`gp332Dao`, Pine v5) — o backtest publicado é vazio

Nível = `lowest(hlc3, 10)[5]`. Sem posição: close abaixo do nível → buy stop no nível; acima → sell
stop no nível; alvo e stop de 1% do nível. O script vem com `ShowBackTest=false`, e então `Work`
só fica verdadeiro na última barra: **no histórico ele não opera nada**. Testado com o backtest
ligado: acerto de 48–52% com RR 1:1, bruto de −4 a +6 bp. Grade (janela 10/20 × atraso 2/5 ×
alvo × stop 0,5/1/2% × long/ambos): 0 acima do B&H.

## 34. Bollinger Band with RSI (`pKOaIHpb`, Pine v4)

Long com RSI(14) < 30 e close abaixo da Bollinger(20,2) inferior; `pyramiding=50`, US$ 1.000 por
entrada sobre US$ 10.000 (até 5× alavancado). Saída em RSI > 70 ou alvo +10% / stop −25% do preço médio.

Mesma armadilha do Vix Fix: acerto de 73–79% porque o stop de 25% quase nunca é tocado e a saída
espera a sobrecompra. A pirâmide compra 50 vezes na mesma queda: DD de −392% (log) no 15m.
Com 1 unidade e 1× fica entre −6,1% e +0,6% a.a. Grade: 0/304 acima do B&H.

## 35. ICT Master Suite (`ABYnIcdl`) — não reproduzida

3.378 linhas de Pine v6 mais a biblioteca `Trading-IQ/ICTlibrary` (2.836 linhas, baixada em
`pine/ICTlibrary_v1.pine`). É uma suíte de desenho (order blocks, FVG, breakers, macros, Po3) com
quatro modelos de entrada (2022 Model ligado por padrão; Unicorn, Silver Bullet e Liquidity Raid
desligados) que dependem de zigzag por ATR, varreduras de liquidez e arrays de FVG mantidos pela
biblioteca. Uma reimplementação fiel é um projeto à parte. O `lookahead_on` que a triagem acusa é só
o `high[1]` do dia anterior para desenho, que é o uso correto e não vaza.

## 36. SUPERTREND ATR with Trailing Stop Loss (`L9GkARD2`, Pine v4)

SuperTrend de **ATR(1)** × 3 (o ATR de 1 barra é o próprio true range, então a trilha pula a cada
vela). LONG por padrão: entra com direção 1, sai na virada ou se o close cruzar um stop de −3% que
passa a subir depois de +1% de lucro. Opção SHORT espelhada.

LONG: −4,5% a +3,4% a.a. SHORT: −3,4% a +5,1%. As 16 células com t > 2 são todas **SHORT**, com
bruto **negativo**: o líquido positivo vem do funding de 13,8% a.a. que o short recebe no ouro, não
do sinal. Grade: 0/250 acima do B&H.
