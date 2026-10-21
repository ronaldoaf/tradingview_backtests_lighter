# Lote 5 do TradingView: rompimento e confluência (2026-10-21)

Ativo padrão: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem
na abertura seguinte. Custo 0,75 bp/perna + funding 13,8% a.a. no ouro. Controle: mesmo lado e
mesma duração, entrada sorteada. B&H do ouro no período: **+13,4% a.a.** (Sharpe 0,73).

Código: `scripts/study_tvlote5.py` (grade `results/study_tvlote5_xau_grid.csv`, saída
`results/study_tvlote5.txt`). Fontes em `pine/`. Nenhuma das três tem `lookahead`; os `security()`
do Full CRYPTO pack só existem com Heikin Ashi ligado (default desligado).

| # | Estratégia | Ouro | Veredito |
|---|---|---|---|
| 29 | Price and Volume Breakout Buy (TradeDots, `jc2hs2qK`) | 0/334 batem o B&H, melhor +12,8% a.a. | reprovada |
| 30 | QQE MOD + SSL Hybrid + Waddah Attar Explosion (`YCob5r03`) | 0/640 batem o B&H, melhor +9,1% a.a. | reprovada |
| 31 | Full CRYPTO pack macd-rsi-obv-ema (SoftKill21, `DbRYTl6G`) | 0/128 batem o B&H, melhor +11,8% a.a. | reprovada |

Como nenhuma passou no ouro, nenhuma foi estendida aos outros ativos.

## 1. Price and Volume Breakout Buy (`jc2hs2qK`, Pine v5)

Long quando o close rompe a máxima de 60 barras **e** o volume rompe o máximo de 60 barras **e** o
close está acima da SMA 200, só com a carteira zerada. Saída: 5 closes seguidos abaixo da SMA 200.

- Defaults (só long): +1,8% a +2,4% a.a. nos TFs intradiários, t ≤ 0,7 contra o controle. No 1D
  são menos de 10 trades em 9 anos.
- Grade de 334 células (período 20/60/120, SMA 50/100/200, saída 1 ou 5 barras, com/sem filtro de
  volume, long/ambos): 288 com líquido positivo e 31 com t > 2, mas **nenhuma acima do B&H**. As
  melhores (+12,8% a.a., Sharpe 0,74) são long+short **sem** o filtro de volume e com exposição de
  ~90%: viram um seguidor de tendência quase sempre posicionado, que empata com o B&H.
- O filtro de volume, que dá nome à estratégia, piora o resultado: o volume da Dukascopy é volume de
  ticks, mas o efeito vale em todos os TFs. Exigir o rompimento duplo só corta trades bons.

## 2. QQE MOD + SSL Hybrid + Waddah Attar Explosion (`YCob5r03`, Pine v5)

Entrada na primeira barra azul do QQE MOD (QQE2 > +3 e QQE1 acima da banda de Bollinger da sua
trilha), com close acima do canal Keltner de HMA(60) e a "explosão" do WAE (Δ MACD 20/40 × 180 maior
que a largura da BB 20/2). Stop fixo na mínima (máxima) de 10 barras do sinal; saída quando o close
cruza a SSL de saída (HMA 15) contra o trade **e o trade está no lucro**. A JMA do SSL2 é desenhada
mas não entra em nenhuma condição.

- A regra "só sai no lucro" é o que dá o acerto de 55–62%: o trade perdedor só termina no stop, que
  é largo, e o ganhador sai no primeiro cruzamento. O resultado líquido fica perto de zero.
- Defaults: −12% a +7% a.a.; o melhor é o 4h, +6,9% a.a., t = 1,7.
- Grade de 640 células (HMA 30/60, saída 15/30, sensibilidade 90/180, swing 10/20, WAE on/off,
  filtro de lucro on/off, long/ambos): 258 com líquido > 0, 25 com t > 2, nenhuma acima do B&H. A
  melhor faz +9,1% a.a.
- Tamanho: o Pine arrisca 2% da conta por trade (posição = risco / distância do stop). Aqui é 1x
  nocional, como nas outras; isso muda a escala, não o sinal.

## 3. Full CRYPTO pack macd-rsi-obv-ema (`DbRYTl6G`, Pine v4)

Long quando close > EMA9(hl2) subindo, close subindo, histograma MACD(hl2) virando positivo e OBV
acima da SMA10 do OBV. Saída no sinal espelhado. O filtro de RSI é `RSI < 100` (sobrecompra no
default é 100), ou seja, sempre verdadeiro. A janela de datas do script (2020–2021) foi ignorada.

- Defaults (só long): −6% a +4,6% a.a., acerto de 37–41%. Long+short (sempre no mercado após o
  primeiro sinal) chega a +10,8% a.a. no 4h, t = 2,3, ainda abaixo do B&H.
- Grade de 128 células (EMA 9/21/50, MACD 12/26/9 e 24/52/18, OBV on/off, long/ambos): 79 com
  líquido > 0, 4 com t > 2, nenhuma acima do B&H; melhor +11,8% a.a.
- É a mesma família do MACD + SMA 200 e do MACD Confluence já reprovados: o cruzamento do
  histograma sozinho é quase um flip de tendência, e as melhores células são as sempre posicionadas.

## Diagnóstico comum

As três ficam no padrão de sempre: as células que chegam perto do B&H são as que ficam quase o
tempo todo posicionadas (exposição ≥ 90%), ou seja, beta. Os filtros que diferenciam cada
estratégia (rompimento de volume, explosão WAE, OBV) não acrescentam nada ou pioram.
