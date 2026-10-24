# Lote 19 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote19.py` (grade) e `scripts/study_tvlote19_rob.py` (robustez). Resultados: `results/study_tvlote19.txt`, `results/study_tvlote19_{ativo}_grid.csv` e `results/study_tvlote19_rob_{ativo}.txt`. Nenhum script deste lote era template.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 109 | BEST ABCD Pattern Strategy | `TWSr0hGH` | zigzag de fractais Bill Williams; ABCD com BC/AB 0,382-0,886 e CD/BC 1,13-2,618; entra no padrão e inverte; TP/SL de 100/20 USD viraram % (5:1, testado também 2:1) |
| 110 | HHLL Strategy | `CRNp5xev` | BB(hlc3, 29, 2) alargada em meia largura; máxima acima = vende, mínima abaixo = compra (reverse=true, padrão, inverte isso) |
| 111 | UT Bot v2 | `lDGmh7ou` | trailing stop ATR10 × 1 no close; cruzamento inverte |
| 112 | 3EMA | `9bA3Z56w` | EMA21 × EMA55 compra, TP 3 ATR / SL 2 ATR, sai com EMA9 abaixo da EMA21; long-only; filtro de data ignorado |
| 113 | Cipher B+ Divergence EMA Pullback | `ywcSiaaV` | WaveTrend cruzando em sobrevenda, área MFI > 0, close > EMA150 e pullback na EMA50; TP 2 / SL 4 ATR11; EMAs do próprio TF (o script usa 30m) |

## Grade por ativo

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| 3EMA | BTC | 45 | 45 | 3 | 0 | +35.5% (4h tp0 sl0) | +43.8% |
| 3EMA | ETH | 45 | 45 | 3 | 0 | +43.5% (4h tp0 sl2) | +56.8% |
| 3EMA | US100 | 45 | 44 | 1 | 0 | +8.8% (1h tp0 sl2) | +20.3% |
| 3EMA | WTI | 45 | 3 | 0 | 0 | +0.7% (4h tp3 sl0) | +5.4% |
| 3EMA | XAU | 45 | 24 | 0 | 0 | +3.9% (1h tp6 sl4) | +13.4% |
| ABCD Pattern | BTC | 85 | 76 | 6 | 2 | +70.4% (1h sl4.0% rr5 ambos) | +43.8% |
| ABCD Pattern | ETH | 85 | 71 | 2 | 0 | +52.5% (1h sl4.0% rr5 long) | +56.8% |
| ABCD Pattern | US100 | 85 | 47 | 4 | 0 | +15.3% (30min sl4.0% rr2 long) | +20.3% |
| ABCD Pattern | WTI | 85 | 34 | 3 | 20 | +32.1% (4h sl4.0% rr5 ambos) | +5.4% |
| ABCD Pattern | XAU | 85 | 18 | 0 | 0 | +4.3% (4h sl2.0% rr5 long) | +13.4% |
| Cipher B+ EMA PB | BTC | 50 | 31 | 0 | 0 | +14.4% (1D semwt tp2 sl4 ambos) | +43.8% |
| Cipher B+ EMA PB | ETH | 51 | 36 | 1 | 0 | +25.6% (1h semwt tp2 sl4 ambos) | +56.8% |
| Cipher B+ EMA PB | US100 | 48 | 26 | 2 | 0 | +5.1% (1D semwt tp2 sl4 long) | +20.3% |
| Cipher B+ EMA PB | WTI | 51 | 22 | 2 | 1 | +5.5% (30min semwt tp4 sl2 ambos) | +5.4% |
| Cipher B+ EMA PB | XAU | 42 | 12 | 0 | 0 | +2.0% (4h semwt tp4 sl2 ambos) | +13.4% |
| HHLL | BTC | 30 | 14 | 3 | 1 | +44.4% (1h 29 rev ambos) | +43.8% |
| HHLL | ETH | 30 | 14 | 4 | 5 | +97.1% (1h 29 rev ambos) | +56.8% |
| HHLL | US100 | 26 | 11 | 3 | 0 | +13.2% (30min 20 rev ambos) | +20.3% |
| HHLL | WTI | 26 | 11 | 0 | 7 | +23.6% (4h 20 norm ambos) | +5.4% |
| HHLL | XAU | 28 | 14 | 2 | 0 | +9.9% (15min 29 rev ambos) | +13.4% |
| UT Bot v2 | BTC | 30 | 22 | 1 | 0 | +38.7% (30min a20 m2 ambos) | +43.8% |
| UT Bot v2 | ETH | 30 | 29 | 3 | 6 | +107.5% (30min a20 m3 ambos) | +56.8% |
| UT Bot v2 | US100 | 30 | 15 | 4 | 0 | +15.3% (30min a20 m3 ambos) | +20.3% |
| UT Bot v2 | WTI | 30 | 14 | 1 | 9 | +22.5% (1h a20 m2 ambos) | +5.4% |
| UT Bot v2 | XAU | 30 | 17 | 3 | 0 | +11.9% (4h a20 m3 ambos) | +13.4% |

## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **ABCD BTC 1h SL 4% RR 5** | +70,4% vs +43,9% (t 2,0) | +132% vs +130% | +31% vs +15% | +62% vs +14% | +69% vs +40% | +62,6% (t 3,0) | **aprovada com ressalva** |
| HHLL ETH 1h 29 rev | +97,1% vs +56,8% (t 2,5) | +132% vs +330% | +58% vs +1% | +114% vs −11% | +69% vs +13% | +92% | quase (perde só o terço 1) |
| UT Bot v2 ETH 30m a20 m3 | +107,5% vs +56,8% (t 1,8) | +207% vs +330% | +64% vs +1% | +73% vs −11% | +61% vs +13% | +84% | quase (terço 1; t < 2) |
| UT Bot v2 ETH 30m a10 m3 | +104% (t 1,5) | +205% vs +330% | +55% | +75% | +68% | +82% | quase (terço 1; t baixo) |
| HHLL ETH 30m 29 / 15m 50 | +72% / +78% | perde | ganha | ganha | +21% / +23% vs +13% | +62% / +67% | quase (terço 1) |
| HHLL BTC 30m 50 | +41% vs +44% | +18% vs +130% | ganha | ganha | +44% vs +40% | +37% | reprovada |
| ABCD WTI 4h SL 4% RR 5 | +32,1% vs +5,4% (t 2,5) | +38% vs −21% | +70% vs +40% | **−0,6% vs +7,6%** | +30% vs +3% | +29,5% | reprovada (morreu em 2023-26) |
| ABCD WTI 15m (2 células) | +21% a +25% | ganha | ganha | **−1% a −3%** | +7% a +10% | +0,6% | reprovada (custo e terço 3) |

## Conclusões

- **ABCD Pattern no BTC 1h (SL 4%, alvo 20%, long e short)** é a primeira candidata do BTC: passa em todos os terços, na 2ª metade (+69% vs +40%) e com custo 4× (t 3,0). Ressalvas: o terço 1 só empata com o B&H (+132% vs +130%); a vizinhança é estreita (no BTC só 1h com SL 4% bate o B&H, com RR 5 e RR 2); DD −87% (log); 156 trades/ano e exposição 84%, então na prática é um sistema quase sempre posicionado que inverte nos padrões.
- No ETH, HHLL (bandas largas, revertido = seguir rompimento) e UT Bot v2 com ATR × 3 repetem o padrão conhecido: seguidores de tendência que batem o B&H do ETH depois de 2022 e perdem no bull run de 2020-22. Ficam como "quase", como os anteriores.
- 3EMA e Cipher B+ não batem o B&H em nenhum ativo (fora uma célula de WTI empatada). O Cipher quase não opera com a regra completa.
- XAU e US100: nada acima do B&H.
