# Vix FIX / StochRSI Strategy (`TDxSLJRA`) — 2026-10-21

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte. Custo 0,75 bp/perna + funding 13,8% a.a. Controle: mesmo lado, mesma duração.

Código: `scripts/study_vixfix.py` (saída `results/study_vixfix.txt`, grade
`results/study_vixfix_xau_grid.csv`).

**Veredito: reprovada no ouro, não estendida.** 752 células, **0** batem o buy & hold
(+13,4% a.a.) e **0** têm t > 2 contra o controle. A melhor por t (+0,70) tem 10 trades.

## A regra

- **Williams Vix Fix**: `wvf = (highest(close,22) − low) / highest(close,22)`, com Bollinger
  (20, 2) e teto de percentil `highest(wvf,50) × 0,85`. Mede o quanto o preço caiu do topo recente.
- **Entrada long** quando o wvf *estava* acima da banda/teto na barra anterior (pânico) e o preço
  confirma a virada (`filtered`: mínima e fechamento acima da barra anterior; `aggressive`:
  fechamento acima do anterior e da abertura), com `close > close[3]` e o fechamento ainda abaixo
  do de 14 ou 40 barras atrás. `pyramiding=9`, 3% do capital por sinal.
- **Saída total** no cruzamento do estocástico lento (14,3,3) acima de 80.
- O RSI do nome é calculado e **nunca usado**. Não há stop nem alvo. Sem `security()`, então
  apesar de ser Pine v2 não há vazamento de futuro.

## Resultado nos defaults

| TF | trades/ano | acerto | líquido/trade | CAGR | t vs controle |
|---|---|---|---|---|---|
| 15m | 139 | 68% | −1,6 bp | −13,4% | −0,85 |
| 30m | 70 | 69% | −1,7 bp | −9,8% | −1,00 |
| 1h | 32 | 66% | −8,4 bp | −9,1% | −0,99 |
| 4h | 10 | 72% | −14,1 bp | −4,3% | −1,40 |
| 1D | 2 | 72% | −32,6 bp | −1,1% | −0,76 |

(pyramiding 9, nocional cheio = 9 unidades). Com uma unidade só, o 4h e o 1D ficam levemente
positivos (+1,1% e +0,3% a.a.), ainda muito abaixo do B&H e abaixo do controle aleatório.

## Grade

5 TFs × percentil {0,85; 0,90; 0,95} × força {1, 3, 5} × sobrecompra {70, 80, 90} ×
{filtered, aggressive, ambos} × {1 unidade, pyramiding 9}. 74 células com líquido > 0, todas
com t < 0,7; as de CAGR mais alto (+3,7% a.a.) são 1D com 10 trades em 9 anos.

## Diagnóstico

- **Acerto alto sem stop** (66–72%) vem da saída assimétrica: só sai em sobrecompra, então
  os ganhadores são realizados e os perdedores ficam abertos. Mesma armadilha do RSI Divergence.
- **Exposição de ~50% num ativo que subiu 13% a.a.**: o controle aleatório com a mesma duração
  ganha tanto ou mais por trade (ex.: 1D, +103 bp do controle contra −33 bp da estratégia). O
  "pânico" do Vix Fix não acrescenta nada a estar comprado no ouro.
- **Pyramiding piora**: soma unidades justamente quando o preço continua caindo.
