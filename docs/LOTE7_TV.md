# Lote 7 do TradingView: 5 estratégias (2026-10-22)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops, alvos e ordens stop de entrada resolvidos no M1 (stop antes do alvo no
mesmo minuto). Custo 0,75 bp/perna + funding 13,8% a.a. (o long paga, o short recebe).
Controle: mesmo lado e mesma duração, aberto-a-aberto.

Código: `scripts/study_tvlote7.py` (saída `results/study_tvlote7.txt`, grade
`results/study_tvlote7_xau_grid.csv`) e `scripts/study_tvlote7_rob.py` (robustez do Trailing SL,
`results/study_tvlote7_rob*.txt`). Fontes em `pine/`. A triagem não acusou `security()` nem
`lookahead` em nenhum dos cinco.

**Veredito: 5 testadas; 4 reprovadas no ouro. O Trailing SL [QuantNomad] com stop de ~2% é
candidato só no ouro**: bate o B&H no 15m–4h, aguenta custo 4×, passa no OOS com t > 2 e é
platô (1,75–2,5%). Estendido a US100, BTC, WTI e ETH, reprova em todos.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 37 | Trailing SL Strategy (QuantNomad, `n3vj0MIi`) | 115 | 95 | 15 | 4 | **+20,4%** |
| 38 | Super Trend Daily 2.0 BF (`c4Cj7H2y`) | 138 | 45 | 7 | 0 | +12,8% |
| 39 | Captain Backtest Model (TFO, `tOQ8gnxj`) | 130 | 0 | 0 | 0 | −0,2% |
| 40 | 72s Adaptive HMA+ pt.1 (`FrjeeWdl`) | 292 | 227 | 53 | 0 | +9,6% |
| 41 | SR TREND / Support Resistance breakout (`hwHKYkE0`) | 40 | 31 | 1 | 0 | +10,6% |

B&H do ouro no período: +13,4% a.a., Sharpe diário 0,73.

---

## 37. Trailing SL Strategy [QuantNomad] (`n3vj0MIi`, Pine v4) — candidata no ouro

Sempre no mercado. Um trailing stop em `low − X` (comprado) ou `high + X` (vendido), com X = 4% do
close por padrão; a ordem stop fica no nível e, rompida, inverte a posição. Simulado com fill em
`max(abertura, nível)` (gap pior que o nível).

O default (4%) faz +2% a +7,5% a.a., abaixo do B&H. O que passa é o stop mais curto:

| TF | 1,5% | 1,75% | **2%** | 2,25% | 2,5% | 3% |
|---|---|---|---|---|---|---|
| 15m | +5,3% | +9,9% | **+15,4%** | +15,0% | +14,4% | +13,1% |
| 30m | +12,0% | +11,0% | **+20,4%** | +17,0% | +14,7% | +11,3% |
| 1h | +12,3% | +11,4% | **+17,5%** | +17,8% | +15,2% | +14,6% |
| 4h | +10,0% | +20,4% | **+17,8%** | +14,6% | +15,5% | +6,4% |
| 1D | +5,3% | −0,8% | −1,5% | +1,7% | +1,6% | −0,1% |

Com 2% no 30m: 325 trades (36/ano), +45 bp líquidos por trade, Sharpe 1,10 contra 0,73 do B&H, DD
−20% (log), t = +2,3 a +3,7 contra o controle.

Robustez (2%):

- **Terços**: 15m–4h batem o B&H em 2017-21 e 2021-24; em 2024-26 (ouro +31% a.a.) empatam no 1h,
  ganham no 30m/4h e perdem no 15m. O 1D reprova.
- **OOS**: % escolhido em 2017-22 (1,75–2,25% no intradiário) e medido em 2022-26: +17% a +27% a.a.,
  t ≈ +2,2, contra +25% do B&H. Ganha em Sharpe, empata ou perde em CAGR numa alta forte.
- **Custo** 2× e 4×: perde menos de 2 pontos de CAGR (36 trades/ano).
- **Lados**: long e short contribuem igual (+40 a +70 bp cada); funding zerado muda pouco
  (+16,5% / +21,9% / +18,4% / +18,2%), então não é carry do short. O só-long fica abaixo do B&H.

**Outros ativos (2%)** — reprova em todos: US100 +0% a +9% contra +20% do B&H; BTC +8% a +40%
contra +44% (shorts perdem); ETH sem padrão nos vizinhos e t ≈ 0; WTI só vive dos shorts, com OOS
negativo. Ver `results/study_tvlote7_rob_{us100,btc,eth,wti}.txt`.

Próximo passo se o usuário quiser seguir: paper/forward test do 30m–1h com 2% no ouro, comparado
ao B&H em Sharpe (não em CAGR).

## 38. Super Trend Daily 2.0 BF (`c4Cj7H2y`, Pine v4)

Dois SuperTrends (2×1,5 para o long, 3×1,3 para o short) com filtro de ROC (|EMA(ROC)| > 3%), stop
fixo de 5%/6% sobre o preço médio, sinal contrário inverte. O período de teste publicado é só
2017-2019 (ignorado aqui). Defaults: −0,4% a −4,5% a.a., acerto 35–39%. Grade (stop 0/1/2/5% × ROC
0/2/6 × multiplicadores 1,5/1,3 ou 3/3 × long/ambos): o melhor (+12,8%, 30m, sem ROC, ST 3×3) é um
SuperTrend comum sempre no mercado, abaixo do B&H.

## 39. Captain Backtest Model [TFO] (`tOQ8gnxj`, Pine v5)

Modelo de sessão de NY feito para NQ/ES: faixa 06–10h, rompimento até 11:15 dá o viés, espera vela
contrária e tomada da mínima (máxima) anterior, entra quando o close passa a máxima (mínima)
anterior; uma operação por dia, stop 25 / alvo 75 pontos ou saída às 16h. No ouro os pontos foram
convertidos em % do preço (risco 0,05–0,5%, RR 1/2/3) e testada também a saída só no fim do dia.
Bruto de −0,0 a +0,9 bp por trade em 140 trades/ano: **0/130 células com líquido positivo**.

## 40. 72s Adaptive HMA+ pt.1 (`FrjeeWdl`, Pine v4)

HMA de período adaptativo (172–233, encolhe 3,141% por barra quando ATR14 > ATR46), ângulo da
inclinação contra 17°, RSI entre 51 e 70; stop na meia zona (2,7 ATR40), alvo 3 ATR21, saída por
RSI/cruzamento depois de 1 ATR de lucro. Tudo decidido no fechamento (o script usa `strategy.close`
até para stop e alvo). É o mais "limpo" do lote: 53 células com t > 2, acerto 57–67%, Sharpe 1,5 no
4h. Mas a exposição é de ~30%: o melhor CAGR é +9,6%, e nenhuma célula chega ao B&H.

## 41. SR TREND / Support Resistance breakout (`hwHKYkE0`, Pine v4)

Fractais de 5 barras; r = média dos topos − média dos fundos nas últimas 21 barras; tendência
quando o close passa dos dois níveis deslocados por r, entrada no rompimento do último topo/fundo.
Quase sempre posicionado (90%), acerto 32–43%. Melhor: +10,6% a.a. (4h, janela 100). 0/40 acima
do B&H.
