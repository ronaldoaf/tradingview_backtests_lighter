# Estratégias aprovadas nos testes

Lista das estratégias que passaram na grade e na robustez (terços, 2ª metade ou OOS, custo 2×/4×, vizinhança de parâmetros) de [PROTOCOLO.md](PROTOCOLO.md). Atualizada a cada lote. Nenhuma está aprovada para dinheiro real: todas são **candidatas** para paper/forward test.

Convenções: sinal no fechamento, ordem na abertura seguinte, custo de spread + funding de cada ativo. CAGR é anual líquido.

## 1. Trailing SL Strategy [QuantNomad] — ouro (XAU)

- **Script:** `n3vj0MIi` · lote 7 · [LOTE7_TV](LOTE7_TV.md) · `scripts/study_tvlote7.py`
- **Regra:** sempre no mercado. Trailing stop em `low − X` (comprado) ou `high + X` (vendido); rompido, inverte a posição.
- **Configuração:** X = **2%** do close (platô 1,75–2,5%), timeframe **30m a 1h** (15m e 4h também passam).
- **Resultado (30m, 2%):** +20,4% a.a. vs +13,4% do B&H; Sharpe 1,10 vs 0,73; DD −20% (log); 36 trades/ano; t = +2,3 a +3,7 contra o controle.
- **Robustez:** bate o B&H em 2017-21 e 2021-24; OOS (parâmetro escolhido em 2017-22, medido em 2022-26) +17% a +27% a.a. com t ≈ 2,2; custo 4× tira menos de 2 pontos; long e short contribuem igual.
- **Ressalvas:** em alta forte do ouro (2024-26) empata ou perde em CAGR, ganha em Sharpe. O 1D reprova. Reprova nos outros 4 ativos.

## 2. Simple RSI-MA Algo — ETH 15m

- **Script:** `qSoZRbX7` · lote 12 · [LOTE12_TV](LOTE12_TV.md) · `scripts/study_tvlote12.py`
- **Regra:** SMA(ml) do RSI(rl); cruzar 50 para cima compra, para baixo vende. Sempre no mercado.
- **Configuração:** **15m**, RSI 10 ou 5, SMA 50, long e short.
- **Resultado:** r10 m50 +171% a.a.; r5 m50 +189% a.a. (t = +5,7) vs +56,8% do B&H.
- **Robustez:** terços +458/+80/+93% (r10) e +524/+54/+143% (r5) vs B&H +330/+0,7/−11%; 2ª metade +48%/+79% vs +13%; custo 4× ainda +128%/+126%; vizinhança no 15m boa (r20 m20/m50 > +100%).
- **Ressalvas:** DD −65% a −88% (log). Custo do ETH estimado, não medido na Lighter. No 30m cai para +21% e no 1h+ é fraco. O mesmo sinal no BTC falha no período recente.

## 3. Pivot Point SuperTrend (LonesomeTheBlue) — ETH 15m

- **Script:** `DwdC6FT4` · lote 4 · [LOTE4_TV](LOTE4_TV.md)
- **Configuração:** 15m, pivot 5, fator 2, ATR 10, long e short.
- **Resultado:** +81% a.a. vs +57% do B&H; Sharpe 0,62; t = 3,8; 185/185 células com líquido positivo.
- **Robustez:** terços +83/+83/+72% vs B&H +330/+1/−11%, estável e quase independente da direção do ETH.
- **Ressalvas:** custo do ETH estimado; com 640 trades/ano, custo 4× já tira a vantagem. Falta walk-forward. DD −69% (log). Não funciona em US100 e WTI.

## 4. Seguidores de tendência no ETH (lote 13) — UT Bot v5, Ichimoku básico, Scalping System

- **Scripts:** `2wkJx7Ix`, `XZcsLIEW`, `YotdMm0M` · [LOTE13_TV](LOTE13_TV.md) · `scripts/study_tvlote13.py`
- **Configurações:** UT Bot 30m (a=5, ATR 11, HMA2 do open, long e short); Ichimoku 15m (20/60/120, deslocamento 60, long e short); Scalping 30m (SMA25 do low, sem EMA200, long e short).
- **Resultado:** +131%, +120% e +125% a.a. vs +56,8% do B&H; t = 2,4 a 2,6.
- **Robustez:** os três batem o B&H nos três terços e na 2ª metade; custo 4× ainda +98% a +122%.
- **Ressalvas:** DD −90% a −95% (log). Mesma aposta das candidatas 2 e 3: seguir tendência no ETH, cujo B&H é quase zero desde 2022, então quase toda regra de tendência long/short passa. Não são vantagens independentes. Custo do ETH estimado. Reprovam no BTC, XAU, US100 e WTI.

## Pendências comuns

- Medir o spread real do ETH na Lighter (afeta as candidatas 2 e 3).
- Walk-forward e paper/forward test antes de qualquer uso real.
- Para o ETH: comparar as candidatas 2, 3 e 4 entre si e com um seguidor de tendência simples (ex.: cruzamento de médias) para saber se alguma acrescenta algo além do efeito comum.
