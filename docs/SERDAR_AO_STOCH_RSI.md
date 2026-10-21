# Buy&Sell Strategy depends on AO+Stoch+RSI+ATR (SerdarYILMAZ) — sem edge

Testada em 2026-10-21 no **ouro (XAUUSD)**, M1 da Dukascopy, 2017-09-01 → 2026-10-04
(9,1 anos; buy&hold **+13,4%/ano**).

- Fonte: `https://www.tradingview.com/script/RpYoQCVJ-Buy-Sell-Strategy-depends-on-AO-Stoch-RSI-ATR-by-SerdarYILMAZ/`
- Pine aberto do pine-facade (`PUB;TfrUjDEBUT7M7cNaUcJOBmhkoI0Syx58`)
- Código: `scripts/study_serdar.py` · saída: `scripts/study_serdar.txt` · grade:
  `scripts/study_serdar_grid.csv`

O próprio autor avisa no código: *"This strategy is just for training... Don't make buy or sell
decision with this strategy."* Testei de todo jeito, como as outras da fila.

## Regras

```
awesome = (sma(hl2,5) - sma(hl2,34)) * 1000
k       = sma(stoch(close,high,low,14), 3)      // d = sma(k,3) é calculado e NÃO é usado
rsi     = rsi(close,10) ;  atr = rma(tr,14)

Long  : k<20  and rsi<30 and awesome > awesome[1]
        stoploss = low  - atr    takeprofit = close + atr     (níveis ABSOLUTOS do sinal)
Short : k>80  and rsi>70 and awesome < awesome[1]
        stoploss = high + atr    takeprofit = close - atr
```

Entrada a mercado → fill na abertura da barra seguinte; `strategy.exit` é chamado na barra do
sinal, logo o bracket já está no book quando a entrada executa (barra de entrada protegida).
Medida em R (R = |fill − stop| no fill real), custo = spread Lighter por perna + funding pro-rata.

## O defeito está no desenho, não nos parâmetros

**O alvo dista 1 ATR do close; o stop dista (close − low) + 1 ATR.** O payoff é assimétrico
**contra** por construção:

- RR efetivo mediano medido: **0,813**
- acerto necessário para empatar nesse RR: **0,552**
- acerto observado (líquido): **0,520**

Falta exatamente isso. Nada no script compensa — não há filtro de tendência, de sessão ou de
volatilidade; é sobrecompra/sobrevenda pura com concordância de três osciladores.

## Resultado: sem edge

| | n | /ano | acerto | R bruto | custo R | **R líq** | PF | R/ano |
|---|---|---|---|---|---|---|---|---|
| todos | 550 | 60,5 | 0,520 | −0,050 | 0,036 | **−0,085** | 0,83 | −5,2 |
| long | 197 | 21,7 | 0,574 | +0,039 | 0,078 | −0,039 | 0,91 | −0,9 |
| short | 353 | 38,8 | 0,490 | −0,099 | 0,012 | −0,111 | 0,79 | −4,3 |
| IS 70% | 385 | | 0,543 | −0,002 | | −0,039 | 0,92 | −2,4 |
| OOS 30% | 165 | | 0,467 | −0,161 | | −0,193 | 0,65 | −11,7 |

A 1% de risco por trade: **−5,2%/ano** (vs +13,4% do buy&hold), com só 4,7% de exposição. Com os
0,05%/perna de um cenário típico de corretora: −0,374 R/trade (−22,6 R/ano) — o stop mediano é de
**33 bp**, então qualquer custo pesa desproporcionalmente.

**Controle** (entrada em barra aleatória, mesmo lado/risco/alvo em R/duração):
controle −0,009 R vs estratégia −0,050 R → diferença **−0,041 R (t = −0,97)**. A confluência dos
três osciladores é **pior** que entrar no acaso com o mesmo bracket; no short,
t = −1,52 (contra a estratégia).

**Grade de 720 células** (5 TFs × 4 pares de limiares × 4 alvos × 3 multiplicadores de ATR ×
lado): **28/720 positivas no líquido**, 14/626 entre as que têm n ≥ 50 — e **27 das 28 são
long-only** num ativo que subiu 13,4%/ano, com n mediano de 54. Nenhuma estrutura: a média de
R_liq é negativa em **todos** os cortes (todos os 5 TFs, todos os 4 limiares, todos os 4 alvos,
todos os 3 ATRs, os 3 lados).

A monotonia do alvo confirma que é payoff e não informação: média de R_liq por RR pedido
0,0 → −0,101; 1,0 → −0,123; 2,0 → −0,160; 3,0 → −0,173 — quanto mais longe o alvo, pior, com o
acerto caindo de 0,55 para 0,25 na proporção exata do RR.

## Observações técnicas

- `d = sma(k, smooth)` é calculado e nunca usado — o `%D` do estocástico não entra em decisão
  nenhuma, só no plot.
- O `*1000` do AO é puro ajuste de escala de plot; o sinal só usa `awesome > awesome[1]`, ou seja,
  **a derivada** do AO, não o seu nível.
- `strategy.exit("TP/SL", ...)` é chamado sem `from_entry`, valendo para qualquer entrada aberta.
  Como as condições long/short são extremas e mutuamente exclusivas, a inversão praticamente não
  ocorre (`FLIP=0` dá resultado idêntico).
- Afrouxar os limiares só aumenta a amostra mantendo o prejuízo (k<30/rsi<40: n=662, −0,083 R;
  rsi<40/>60: n=1110, −0,074 R) — não há "zona boa" escondida nos extremos.

## Veredito

Sem edge. Sem extensão para US100/BTC/WTI/ETH.
