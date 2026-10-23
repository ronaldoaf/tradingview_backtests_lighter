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

## 5. FTSMA — ETH 30m (lote 17)

- **Script:** `wffJotUo` · [LOTE17_TV](LOTE17_TV.md) · `scripts/study_tvlote17.py`
- **Regra:** EMA5 e EMA20 do close (mais um termo de Fourier de 64 barras que quase não muda nada) e EMA200. Comprado com EMA5 > EMA20 e close > EMA200; vendido no espelho; o sinal contrário inverte.
- **Configuração:** 30m, 5/20/200, long e short.
- **Resultado:** +149% a.a. vs +56,8% do B&H; t = 4,6.
- **Robustez:** terços +614/+50/+30% vs B&H +330/+0,7/−11%; 2ª metade +26% vs +13%; custo 4× +126%; vizinhança 15m, 1h e 4h também acima do B&H com t > 2.
- **Ressalvas:** DD −82% (log). Outro seguidor de tendência no ETH (mesma família de 2 a 4). Custo do ETH estimado. No BTC 30m quase passa (perde na 2ª metade).

## 6. ABCD Pattern — BTC 1h (lote 19, aprovada com ressalva)

- **Script:** `TWSr0hGH` · [LOTE19_TV](LOTE19_TV.md) · `scripts/study_tvlote19.py`
- **Regra:** zigzag de fractais Bill Williams; padrão ABCD com BC/AB entre 0,382 e 0,886 e CD/BC entre 1,13 e 2,618. D abaixo de C compra, acima vende; o padrão contrário inverte. Stop 4% e alvo 20% (5:1).
- **Resultado:** +70,4% a.a. vs +43,9% do B&H; t = 2,0; 156 trades/ano; exposição 84%.
- **Robustez:** terços +132/+31/+62% vs B&H +130/+15/+14%; 2ª metade +69% vs +40%; custo 4× +62,6% (t 3,0).
- **Ressalvas:** terço 1 só empata; vizinhança estreita (só 1h com SL 4%, RR 5 ou 2, bate o B&H no BTC); DD −87% (log). Primeira candidata do BTC; precisa de walk-forward.

## 7. Follow Line — ETH 30m (lote 20)

- **Script:** `6lhyIPGA` · [LOTE20_TV](LOTE20_TV.md) · `scripts/study_tvlote20.py`
- **Regra:** EMA21 ± 1 desvio padrão (21) do close. Close acima da banda de cima: linha = low − ATR5, que só sobe; abaixo da de baixo: high + ATR5, que só desce. A virada da linha compra ou vende; o sinal contrário inverte. Calculado no próprio TF.
- **Configuração:** 30m, 21 / 1 desvio / ATR5, long e short.
- **Resultado:** +118% a.a. vs +56,8% do B&H; t = 3,1; cerca de 330 trades/ano.
- **Robustez:** terços +403/+18/+60% vs B&H +330/+0,7/−11%; 2ª metade +35% vs +13%; custo 4× +98% (t 2,5). Vizinhança: 15m (21/1 e 50/1), 1h 50/1 e 4h 50/2 também acima do B&H.
- **Ressalvas:** DD −103% (log), cerca de −64%. Outro seguidor de tendência no ETH, da mesma família de 2 a 5. Custo do ETH estimado. No BTC e nos outros ativos não passa.

## Correlação entre as candidatas do ETH

`scripts/study_eth_corr.py` → `results/study_eth_corr.txt`. Correlação dos retornos diários entre as cinco candidatas do ETH vai de 0,29 a 0,72; com o B&H do ETH fica perto de zero. Ficam na mesma direção 62% a 81% do tempo. Pares mais parecidos: RSI-MA × Ichimoku (0,72) e RSI-MA × Pivot ST (0,66). UT Bot e Scalping são os mais diferentes. A carteira com peso igual nas cinco cai o DD para cerca de −39% (vs −55% a −74% de cada uma, na marcação diária aproximada).

## Referência: cruzamento simples de médias no ETH

No lote 16, o EMA Cross 50/200 no ETH 15m fez +111% a.a. (B&H +57%), mas fraco na 2ª metade (+19% vs +13%, t 0,6). Ou seja, bater o B&H do ETH é fácil para qualquer seguidor de tendência; as candidatas acima valem pelo que fazem a mais que isso (RSI-MA +171% e passa em todos os terços; UT Bot 30m +131%). Ver [LOTE16_TV](LOTE16_TV.md).

## Pendências comuns

- Medir o spread real do ETH na Lighter (afeta as candidatas 2 e 3).
- Walk-forward e paper/forward test antes de qualquer uso real.
- Para o ETH: comparar as candidatas 2, 3 e 4 entre si e com um seguidor de tendência simples (ex.: cruzamento de médias) para saber se alguma acrescenta algo além do efeito comum.
