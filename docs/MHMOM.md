# Momentum multi-horizonte com vol targeting (paper de hedge fund / Unbiased Trading)

Script: `scripts/study_mhmom.py` · saída bruta: `results/mhmom.csv`

## Regras implementadas (como no pseudocódigo)
- Barras diárias (UTC). Sinal no fechamento: S = Σ sign(P_t − P_{t−n}), n ∈ {5, 10, 21, 42} → −4..+4.
- Alvo w = S × 1% / vol diária (desvio dos log-retornos, 20 dias). Sem teto de alavancagem.
- Rebalanceia só se |Δw / w_atual| > 5%. Ordem na **abertura do dia seguinte**.
- Custo Lighter por perna (`CUSTO`) sobre |Δw| + funding pro-rata (long paga, short recebe).
- Universo top-50 não se aplica: cada ativo isolado. WTI sem abril/2020.
- Períodos: 10 partes iguais; 1–6 treino, 7–9 validação, 10 OOS (iguais aos estudos anteriores).
- Não há parâmetro a otimizar, então o OOS foi lido direto. Variantes só para robustez.

## Resultado (spec: vol20, risco 1%) — retorno do período / Sharpe / DD máx

| Ativo | Treino | B&H treino | Validação | B&H val | OOS | B&H OOS | Total CAGR | Sharpe total (B&H) | DD total (B&H) | Alav. média |
|---|---|---|---|---|---|---|---|---|---|---|
| XAU | −37,7% / 0,12 | +40,4% / 0,52 | +148,5% / 0,77 | +115,1% / 1,71 | +80,6% / 1,11 | +4,2% | +12,0% | 0,48 (0,80) | −74% (−28%) | 3,4× |
| US100 | +14,1% / 0,31 | +131,5% / 0,79 | +46,1% / 0,55 | +119,6% / 1,43 | −23,0% / −0,18 | +21,4% | +3,0% | 0,33 (0,99) | −62% (−36%) | 2,5× |
| WTI | −49,8% / 0,09 | +70,2% / 0,43 | −55,4% / −0,26 | −33,0% / −0,25 | +39,9% / 0,77 | +44,6% | −11,2% | 0,09 (0,33) | −92% (−76%) | 1,4× |
| BTC | +257,6% / 0,64 | +474,8% / 0,82 | +34,6% / 0,46 | +113,7% / 0,86 | +62,2% / 1,11 | −5,3% | +35,6% | 0,64 (0,76) | −74% (−77%) | 1,1× |
| ETH | +215,2% / 0,62 | +1814% / 1,06 | +113,8% / 0,75 | +18,5% / 0,39 | +34,7% / 0,78 | −8,6% | +38,7% | 0,67 (0,80) | −71% (−79%) | 0,8× |

Variantes (vol60, teto 2×, risco 0,5%, sem tolerância) não mudam o quadro: risco 0,5% só divide
retorno e DD; vol60 e teto 2× pioram ou empatam. A tolerância de 5% quase nunca segura ordem
(a vol muda todo dia), giro de 100–400× o capital por ano.

## Veredito
**Reprovada nos 5 ativos pelo critério do projeto** (exclusão no treino: precisa bater o B&H).
Em nenhum ativo o Sharpe do treino supera o do B&H.
- **XAU / US100 / WTI:** sem vantagem. Treino negativo ou fraco, DD de 60–90% com 1,4–3,4× de alavancagem.
- **BTC / ETH:** o único sinal de vida. Positiva em treino, validação e OOS, DD um pouco menor que o B&H,
  e ganha do B&H quando o mercado cai (OOS 2026, ETH na validação). Mas perde para o B&H em Sharpe
  no total e no treino, e DD de ~70% não é proteção. Se for reaproveitar, é como diversificador
  de tendência em cripto numa carteira, não como estratégia isolada.
