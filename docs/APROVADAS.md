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

## 8. MA Consecutive Up/Down — ETH 4h (lote 21, aprovada com ressalva)

- **Script:** `7KXy9NNJ` · [LOTE21_TV](LOTE21_TV.md) · `scripts/study_tvlote21.py`
- **Regra:** 4 closes seguidos acima do anterior compra; 4 seguidos abaixo vende; o sinal contrário inverte (sempre posicionado). Média de comprimento 1, ou seja, o próprio close.
- **Resultado:** +134% a.a. vs +56,6% do B&H; t = 2,1; 57 trades/ano.
- **Robustez:** terços +469/+28/+83% vs B&H +328/0/−11%; 2ª metade +62% vs +13%; custo 4× +130% (t 2,6).
- **Ressalvas:** vizinhança irregular (30m e 1h com 4 barras acima do B&H; com EMA20 ou 8 barras no 4h, não); DD −108% (log), cerca de −66%. Outro seguidor de tendência no ETH, da mesma família de 2 a 7.

## 9. Moving Average Band — WTI 4h (lote 22, aprovada com ressalva)

- **Script:** `wwi02rpz` · [LOTE22_TV](LOTE22_TV.md) · `scripts/study_tvlote22.py`
- **Regra:** banda = SMA40 das máximas e SMA40 das mínimas. Close cruza acima da banda de cima compra; abaixo da de baixo vende; a entrada contrária inverte. Stop na banda oposta (fixado na entrada) e alvo de 3× o risco.
- **Resultado:** +27,1% a.a. vs +5,4% do B&H; Sharpe 0,80; t = 3,8; 75 trades/ano.
- **Robustez:** terços −1/+60/+21% vs B&H −21/+40/+8%; 2ª metade +30% vs +3%; custo 4× +21,6%.
- **Ressalvas:** o lucro vem do lado vendido (long-only perde −11% a.a.), o mesmo viés do WTI visto na Gold/Silver (lote 21) e no Turtle Donchian short (lote 22); vale checar se vem do rolamento do CFD. DD −67% (log), cerca de −49%. Vizinhança razoável (4h sem alvo, 4h SMA100 e 1h SMA40 também acima do B&H). Única aprovada fora de ETH/BTC/XAU.

## 10. Super trend V — ETH 15m (lote 23, aprovada com ressalva)

- **Script:** `7g8MF7f7` · [LOTE23_TV](LOTE23_TV.md) · `scripts/study_tvlote23.py`
- **Regra:** VPT "sombra" (volume × corpo da vela, normalizado pelo desvio do range) suavizado por uma EMA de 336 barras no 15m (720/TF × 7); SuperTrend 10 × 1 em volta dele. Close cruza acima da linha com close acima da EMA da abertura compra; abaixo, vende. Comprado e vendido, o sinal contrário inverte.
- **Resultado:** +146% a.a. vs +56,8% do B&H; t = 3,9; 314 trades/ano.
- **Robustez:** terços +610/+57/+25% vs B&H +330/+1/−11%; 2ª metade +29% vs +13%; custo 4× +124%.
- **Ressalvas:** DD −70% (log), cerca de −50%; depende do volume da Binance; vizinhança boa no ETH (15m, 30m e 1h com multiplicador 1 acima do B&H; a versão só comprada também passa, por pouco na 2ª metade), mas no BTC a regra morre depois de 2022. Mais um seguidor de tendência no ETH (ver correlação abaixo).

## 11. BEST Supertrend — ETH 1h (lote 24, aprovada com ressalva)

- **Script:** `6knHPR6c` · [LOTE24_TV](LOTE24_TV.md) · `scripts/study_tvlote24.py`
- **Regra:** SuperTrend diário (ATR3 × 3) do dia anterior como nível; regime de alta quando SMA7 > SMA20. Close ≥ linha diária no regime de alta compra; close ≤ linha no regime de baixa vende; sai no cruzamento contrário das médias. Comprado e vendido.
- **Resultado:** +122% a.a. vs +56,8% do B&H; t = 3,6; 264 trades/ano.
- **Robustez:** terços +366/+52/+64% vs B&H +330/+1/−11%; 2ª metade +31% vs +13%; custo 4× +105%.
- **Ressalvas:** DD −80% (log); vizinhança boa (30m, 1h e 4h, multiplicador 3 e 1,5); a versão só comprada tem Sharpe 1,6 mas perde o terço 1; no BTC perde a 2ª metade. Mais um seguidor de tendência no ETH.

## 12. VWAPStrategy — ETH 30m (lote 24, aprovada com ressalva forte)

- **Script:** `t1lk7Uvk` · [LOTE24_TV](LOTE24_TV.md) · `scripts/study_tvlote24.py`
- **Regra:** SMA3 do close cruza a VWAP diária (hlc3, âncora 00:00 UTC): acima compra, abaixo vende; sempre posicionado.
- **Resultado:** +175% a.a. vs +56,8% do B&H; t = 5,2; ~1.770 trades/ano, 7 bp brutos por trade.
- **Robustez:** terços +549/+103/+54% vs B&H +330/+1/−11%; 2ª metade +59% vs +13%; custo 2× +130%; custo 4× +61,5% (passa por pouco).
- **Ressalvas:** muito sensível a custo (no 15m o custo 4× já reprova); DD −86% (log); depende do volume da Binance para a VWAP. Só vale com custo de execução baixo.

## 13. Chandelier Exit — ETH 30m (lote 25, aprovada com ressalva)

- **Script:** `yca6gmSk` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Chandelier Exit (ATR22 × 3, extremos do close): virada para cima compra, para baixo vende (inverte). Stop de 5% pelo close, alvo de 20% pela máxima e trailing de 5 pontos percentuais depois de +10%.
- **Resultado:** +153% a.a. vs +56,8% do B&H; t = 2,5; 493 trades/ano.
- **Robustez:** terços +408/+95/+59% vs B&H +330/+1/−11%; 2ª metade +47% vs +13%; custo 4× +118%.
- **Ressalvas:** sem o stop/alvo também fica acima do B&H (+125%); o terço 1 passa por pouco; mais um seguidor de tendência no ETH, provavelmente muito correlacionado com as outras aprovadas do ETH.

## 14. Triangular Hull MA — ETH 15m (lote 25, aprovada com ressalva)

- **Script:** `gMeYb8Dp` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** THMA de 100 (WMA de 3·WMA(n/3) − WMA(n/2) − WMA(n)) cruzando ela mesma de 2 barras atrás; inverte.
- **Resultado:** +155% a.a. vs +56,8%; t = 4,3; 531 trades/ano.
- **Robustez:** terços +338/+157/+33% vs +330/+1/−11%; 2ª metade +41% vs +13%; custo 4× +117%.
- **Ressalvas:** a THMA40 no 30m também passa em quase tudo (perde o terço 1); o terço 1 passa por pouco; mais um seguidor de tendência no ETH, provavelmente muito correlacionado com as outras aprovadas do ETH.

## 15. Smart Money Pivot — ETH 15m (lote 25, aprovada com ressalva)

- **Script:** `IMTwV7U8` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Pivô de topo 20/20: quando a máxima rompe o último pivô ainda ativo, compra; quando a mínima perde o último pivô de fundo, vende; inverte. Sem o stop de 1% e o alvo de 1,5% do script.
- **Resultado:** +130% a.a. vs +56,8%; t = 3,8; 288 trades/ano.
- **Robustez:** terços +355/+24/+110% vs +330/+1/−11%; 2ª metade +61% vs +13%; custo 4× +111%.
- **Ressalvas:** com o stop/alvo original de 1%/1,5% não passa; o terço 1 passa por pouco; mais um seguidor de tendência no ETH, provavelmente muito correlacionado com as outras aprovadas do ETH.

## 16. Swing HULL + T3 — ETH 1h (lote 25, aprovada com ressalva)

- **Script:** `YgRqvCGx` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Média de HMA100 e T3(100, 0,7): subindo compra, caindo vende (inverte); alvo 8% no long, alvo 3% e stop 6% no short.
- **Resultado:** +115% a.a. vs +56,8%; t = 3,8; 420 trades/ano.
- **Robustez:** terços +403/+51/+23% vs +330/+1/−11%; 2ª metade +29% vs +13%; custo 4× +101%.
- **Ressalvas:** sem os alvos o resultado é igual; o terço 1 passa por pouco; mais um seguidor de tendência no ETH, provavelmente muito correlacionado com as outras aprovadas do ETH.

## 17. 5 EMA — ETH 4h (lote 26, aprovada com ressalva)

- **Script:** `EaZHR7q6` · [LOTE26_TV](LOTE26_TV.md) · `scripts/study_tvlote26.py`
- **Regra:** A última barra toda abaixo da EMA5 marca a máxima de gatilho (toda acima marca a mínima); o rompimento entra se estiver fora; stop na menor mínima das 2 últimas barras (maior máxima no short), alvo 3R (o script usa 1,5R).
- **Resultado:** +133% a.a. vs +56,6%; t = 2,0; 80 trades/ano.
- **Robustez:** terços +372/+181/+81% vs +328/+0/−11%; 2ª metade +59% vs +13%; custo 4× +131%.
- **Ressalvas:** só o alvo 3R passa (com 1,5R fica em +61%, perto do B&H); DD alto; mais um seguidor de tendência no ETH, provavelmente correlacionado com as outras aprovadas do ETH.

## Correlação entre as candidatas do ETH

`scripts/study_eth_corr.py` → `results/study_eth_corr.txt`. Correlação dos retornos diários entre as cinco candidatas do ETH vai de 0,29 a 0,72; com o B&H do ETH fica perto de zero. Ficam na mesma direção 62% a 81% do tempo. Pares mais parecidos: RSI-MA × Ichimoku (0,72) e RSI-MA × Pivot ST (0,66). UT Bot e Scalping são os mais diferentes. A carteira com peso igual nas cinco cai o DD para cerca de −39% (vs −55% a −74% de cada uma, na marcação diária aproximada).

## Referência: cruzamento simples de médias no ETH

No lote 16, o EMA Cross 50/200 no ETH 15m fez +111% a.a. (B&H +57%), mas fraco na 2ª metade (+19% vs +13%, t 0,6). Ou seja, bater o B&H do ETH é fácil para qualquer seguidor de tendência; as candidatas acima valem pelo que fazem a mais que isso (RSI-MA +171% e passa em todos os terços; UT Bot 30m +131%). Ver [LOTE16_TV](LOTE16_TV.md).

## Pendências comuns

- Medir o spread real do ETH na Lighter (afeta as candidatas 2 e 3).
- Walk-forward e paper/forward test antes de qualquer uso real.
- Para o ETH: comparar as candidatas 2, 3 e 4 entre si e com um seguidor de tendência simples (ex.: cruzamento de médias) para saber se alguma acrescenta algo além do efeito comum.
