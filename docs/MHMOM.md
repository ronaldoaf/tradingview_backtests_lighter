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

## Versão em 1 hora (`python scripts/study_mhmom.py 1h` → `results/mhmom_1h.csv`)
Mesma regra, recalculada a cada barra de 1h (ordem na abertura da hora seguinte). Risco escalado
por 1/√24 para manter o mesmo risco diário. Sharpe e DD medidos em retornos diários.

1. **Barras literais (5/10/21/42 horas, vol 20h):** desastre fora do ETH. Giro de 3–8 mil × capital/ano.
2. **Janelas em dias equivalentes (120/240/504/1008h, vol 480h):** igual ao diário, só que reavaliado de hora em hora.

| Ativo | Treino Sharpe (B&H) | Val Sharpe (B&H) | OOS Sharpe (B&H) | Total CAGR | Sharpe total (B&H) | DD total (B&H) |
|---|---|---|---|---|---|---|
| XAU | 0,40 (0,52) | 0,17 (1,70) | 0,91 (0,27) | +7% | 0,38 (0,80) | −69% (−28%) |
| US100 | 0,31 (0,78) | 0,53 (1,41) | −0,97 (1,15) | −0,5% | 0,24 (0,99) | −59% (−36%) |
| WTI | −0,16 (0,43) | −0,32 (−0,25) | 0,77 (0,90) | −17% | −0,09 (0,33) | −95% (−76%) |
| **BTC** | **1,03 (0,82)** | 0,47 (0,85) | 1,61 (0,07) | **+78%** | **0,94 (0,76)** | **−52% (−77%)** |
| ETH | 0,88 (1,06) | 1,03 (0,38) | 0,98 (0,10) | +72% | 0,93 (0,80) | −57% (−79%) |

Tolerância de 25% (em vez de 5%) corta o giro sem mudar o resultado.

**Leitura:** no 1h com janelas em dias, BTC e ETH melhoram muito sobre o diário (Sharpe 0,64→0,94),
batem o B&H no total e têm DD menor. BTC passa o treino; ETH perde do B&H no treino (1,06, o ano de
2021) mas ganha em validação e OOS. XAU, US100 e WTI continuam reprovados.
Ressalva: a melhora vem só de reavaliar mais vezes por dia, então vale checar sensibilidade
(4h, deslocamento de hora) antes de confiar.

## Versão em 4 horas + filtro SMA200 (`python scripts/study_mhmom.py 4h` → `results/mhmom_4h.csv`)
Janelas em dias (30/60/126/252 barras de 4h), vol de 120 barras, risco 1%/√6.
Filtro: compra só com fechamento acima da SMA200, venda só abaixo (senão fica fora).
SMA200 testada em barras de 4h (~33 dias) e diária (1200 barras de 4h).

Sharpe por período (B&H entre parênteses):

| Ativo | Variante | Treino | Validação | OOS | Total | CAGR | DD |
|---|---|---|---|---|---|---|---|
| XAU | base | 0,48 (0,51) | 0,72 (1,70) | 1,19 (0,26) | 0,66 (0,80) | +24% | −51% |
| XAU | SMA200 4h | 0,44 | 0,77 | 1,16 | 0,65 | +23% | −49% |
| XAU | SMA200 diária | 0,45 | 1,15 | 0,79 | 0,76 | +28% | −44% |
| US100 | base | 0,41 (0,77) | 0,71 (1,41) | −0,63 (1,15) | 0,39 (0,99) | +6% | −63% |
| US100 | SMA200 4h | 0,41 | 0,65 | −0,76 | 0,36 | +5% | −64% |
| US100 | SMA200 diária | 0,13 | 0,75 | −0,15 | 0,31 | +3% | −54% |
| WTI | base | 0,12 (0,43) | −0,48 (−0,25) | 1,08 (0,90) | 0,07 (0,33) | −10% | −90% |
| WTI | SMA200 4h | 0,16 | −0,59 | 1,05 | 0,05 | −11% | −91% |
| WTI | SMA200 diária | 0,11 | −0,33 | 0,91 | 0,10 | −7% | −87% |
| BTC | base | 1,03 (0,82) | 0,47 (0,85) | 0,90 (0,06) | 0,86 (0,76) | +67% | −52% |
| BTC | SMA200 4h | 1,11 | 0,59 | 0,88 | 0,95 | +79% | −45% |
| BTC | SMA200 diária | 0,95 | 0,66 | 1,06 | 0,88 | +58% | −60% |
| ETH | base | 0,71 (1,06) | 1,10 (0,38) | 1,04 (0,09) | 0,86 (0,80) | +62% | −62% |
| ETH | SMA200 4h | 0,70 | 1,12 | 1,12 | 0,87 | +63% | −62% |
| ETH | SMA200 diária | 0,66 | 0,97 | 1,57 | 0,85 | +52% | −61% |

**Leitura:** o 4h dá praticamente o mesmo que o 1h em cripto (Sharpe ~0,86) e confirma que a melhora
sobre o diário não depende do timeframe exato. O filtro SMA200 mexe pouco (±0,1 de Sharpe, sem padrão
consistente entre ativos e períodos), o que é esperado: o sinal de momentum 21/42 dias já concorda
com a SMA200 quase sempre. Melhor combinação: BTC 4h + SMA200 4h (Sharpe 0,95, DD −45% vs −77% do B&H),
mas ainda perde do B&H na validação. XAU, US100 e WTI seguem reprovados.

## 5 horizontes em vez de 4 (4h, `scripts/study_mhmom_5janelas.py` → `results/mhmom_4h_5janelas.csv`)
Sinal vai de −5 a +5; risco por ponto escalado por 4/5 para manter a mesma exposição máxima.
Sharpe total (sem filtro / com SMA200 4h). Quinto horizonte em dias:

| Ativo | 4 originais | +2 | +63 | +84 | +126 | B&H |
|---|---|---|---|---|---|---|
| XAU | 0,66 / 0,65 | 0,67 / 0,68 | 0,64 / 0,66 | 0,62 / 0,63 | **0,75 / 0,78** | 0,80 |
| US100 | 0,39 / 0,36 | 0,36 / 0,37 | 0,39 / 0,35 | 0,47 / 0,40 | 0,48 / 0,41 | 0,99 |
| WTI | 0,07 / 0,05 | 0,11 / 0,09 | −0,01 / −0,01 | −0,06 / −0,06 | −0,08 / −0,09 | 0,33 |
| BTC | 0,86 / 0,95 | 0,84 / 0,91 | 0,87 / 0,93 | 0,89 / 0,97 | 0,89 / 0,95 | 0,76 |
| ETH | 0,86 / 0,87 | **0,98 / 1,00** | 0,88 / 0,90 | 0,84 / 0,86 | 0,88 / 0,90 | 0,80 |

Destaques: +126 dias ajuda XAU (treino 0,57, validação 0,96 com SMA, DD −45%) e BTC na validação
(0,74 com SMA, DD −40%); +2 dias ajuda ETH (treino 0,84, validação 1,22). Ganhos de 0,05–0,1 de
Sharpe, dentro do ruído de escolher o melhor de 4 opções; nenhuma variante vira o veredito
de XAU/US100/WTI e nenhuma faz o BTC bater o B&H na validação (0,85).
