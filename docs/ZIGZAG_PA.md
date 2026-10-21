# ZigZag PA Strategy V4.1 (RicardoSantos, `NEDEDcsP`) — 2026-10-21

Ativo: **ouro (XAUUSD)**, M1 da Dukascopy, 2017-09-01 → 2026-10-04 (2,66M minutos).
Sinal no fechamento, ordem na **abertura da barra seguinte** (é o que `strategy.entry` /
`strategy.close` do Pine fazem). Custo 0,75 bp por perna + funding 13,8% a.a. pro-rata (Lighter).
Controle: para cada trade, 20 entradas sorteadas com o **mesmo lado e a mesma duração**.

Código: `scripts/study_zigzagpa.py` (saída `results/study_zigzagpa.txt`, grade
`results/study_zigzagpa_xau_grid.csv`).

**Veredito: reprovada no ouro, não estendida aos outros ativos.** A curva publicada vem
inteira de olhar o futuro. Na versão honesta, 0 de 423 células batem o buy & hold (+13,4% a.a.)
e nenhuma tem t > 2 contra o controle aleatório. A mediana do retorno **bruto** por trade é
−0,4 bp: não existe sinal nem antes do custo.

## A regra

1. **ZigZag de 2 barras.** Pivô de alta quando a barra anterior fecha em alta e a atual em
   baixa (`highest(2)`); pivô de baixa no inverso (`lowest(2)`). Os pivôs alternam.
2. O zigzag é calculado numa **resolução alternativa** (default 60 min, `useAltTF=true`) via
   `security(tickerid, tf, zigzag())` e só é posto no gráfico na primeira barra de cada candle HTF.
3. Os 5 últimos pivôs (X, A, B, C, D) são testados contra **17 padrões harmônicos** por razões
   XAB/ABC/BCD/XAD: Bat, Alt Bat, Butterfly, Gartley, Crab, Shark, 5-O, Wolf, H&S, triângulos,
   AB=CD e cinco "Anti". Qualquer um deles serve.
4. **Long:** padrão de alta (D < C) e `close <= D + 0,236·|C−D|`. **Short** espelhado.
5. **Saída** (ordem a mercado na abertura seguinte): `high >= fib 0,618` (alvo) ou
   `low <= fib −0,236` (stop), recalculados a cada barra sobre o C/D corrente.
   `pyramiding=0`; entrada contrária inverte. O "Target 2" vem desligado por default.

## Por que a curva publicada é falsa

O script é **Pine v2**. Antes do v3 não existia o parâmetro `lookahead`, e o `security()` em
barras históricas devolvia o valor **final** do candle HTF corrente — o mesmo efeito de
`lookahead_on`. Na primeira barra de 15 min de cada hora, o script já sabe se aquela hora vai
formar um pivô e qual é a máxima/mínima dela. Comprar "perto do fundo" fica trivial quando se
conhece o fundo.

| TF gráfico / zigzag | publicado (peek) | honesto (candle HTF fechado) |
|---|---|---|
| 5min / 1h | **+70,4% a.a.**, win 89%, t=+37,9 | −6,9% a.a., win 39%, t=−0,4 |
| 15min / 1h | +26,1%, win 83%, t=+31,3 | −3,9%, win 41%, t=−0,7 |
| 15min / 4h | +32,4%, win 88%, t=+22,2 | −1,4%, win 43%, t=−1,0 |
| 30min / 4h | +24,2%, win 86%, t=+25,7 | −2,5%, win 45%, t=+0,4 |
| 1h / 1D | +19,8%, win 94%, t=+13,0 | −0,7%, win 41%, t=−0,5 |

Buy & hold no período: +13,4% a.a. Win rate de 83–94% com t de 13 a 38 contra o controle é a
assinatura de vazamento, não de edge. Tirado o vazamento, o bruto por trade vai de +15–90 bp
para entre −2 e 0 bp.

## Grade honesta

Configurações: 5 combinações gráfico/HTF (5m/1h, 15m/1h, 15m/4h, 30m/4h, 1h/1D) e 4 com o
zigzag no próprio gráfico (15m, 1h, 4h, 1D). Em cada uma: defaults, só long, só short e
janela de entrada {0; 0,236; 0,382; 0,5} × alvo {0,382; 0,618; 1,0; 1,618} ×
stop {−0,236; −0,5; −1,0}. Total 423 células.

- Retorno líquido > 0: 36 células, todas com t < 1,8 contra o controle.
- CAGR acima do buy & hold: **0**. A melhor (1h/1D, entrada no próprio D, alvo 1,618) faz
  +0,7% a.a. com 15 trades/ano.
- Só long e só short, separadamente: nenhum dos dois lados tem bruto positivo consistente.

## Diagnóstico

- **`security()` de Pine v2 = `lookahead_on`.** Mesma armadilha do Open Close Cross
  ([LOTE3_TV](LOTE3_TV.md)), só que implícita: não aparece `lookahead` no código porque a
  versão da linguagem nem tinha o parâmetro. Todo script `//@version` ≤ 2 (ou sem
  `//@version`) com `security()` deve ser tratado como suspeito.
- **Os "padrões harmônicos" não filtram nada.** Com 17 padrões em OR e faixas largas
  (Wolf aceita ABC entre 0 e 5, AntiGartley aceita BCD e XAD até 5), ~10% das barras têm
  algum padrão de alta e ~10% algum de baixa. O pivô de 2 barras (uma vela de alta seguida de
  uma de baixa) é praticamente ruído, então as razões entre pernas também são.
- **Alvo e stop em fib do C–D atual** mudam a cada novo pivô, então o risco/retorno de um
  trade não é fixado na entrada. Isso não muda o veredito (o bruto já é zero), mas impede
  ler o RR 0,618/0,236 do código como o RR real.
