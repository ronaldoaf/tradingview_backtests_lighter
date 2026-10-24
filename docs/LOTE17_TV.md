# Lote 17 do TradingView (5 ativos)

Scripts: `scripts/study_tvlote17.py` (grade) e `scripts/study_tvlote17_rob.py` (robustez). Resultados: `results/study_tvlote17*_{ativo}.txt` e `_grid.csv`.

Ignorados: SMA (`soKH38lY`) e Wolfe Strategy (`EGvQ2nLb`) não têm ordens de estratégia; ZigZag PA Strategy V4 (`DYONEypp`) é da mesma família do ZigZag PA V4.1 já reprovado ([ZIGZAG_PA](ZIGZAG_PA.md)) e usa `security()` em Pine v1, que olha o futuro.

| # | Estratégia | Script | Regra simulada |
|---|---|---|---|
| 96 | SMA | `soKH38lY` | ignorado (sem ordens) |
| 97 | Best Supertrend CCI | `YsWWsOGs` | na prática, posição = sinal do CCI28 (o stop do SuperTrend só desenha) |
| 98 | ZigZag PA Strategy V4 | `DYONEypp` | ignorado (repetido e com lookahead) |
| 99 | Grid Like Strategy | `oxvR5vMy` | linha-base anda quando o close se afasta `point`; entra a favor com alvo e stop = `point` (virou %); martingale ignorado |
| 100 | FTSMA | `wffJotUo` | EMAs 5/20/200 do close + termo de Fourier (janela 64); long com rápida > média e close > lenta. O termo de Fourier quase não muda nada (com e sem dão o mesmo resultado) |
| 101 | HULLTSIBOT | `gf21APTn` | TSI com HMA (50/50 sobre o open), sinal HMA7 subindo + open subindo |
| 102 | Band-Zigzag TrendFollower | `9FsHYtrq` | zigzag de toques na BB(20, 2) "grudenta"; tendência pela razão de retração vs %B (bibliotecas aproximadas) |
| 103 | Wolfe Strategy | `EGvQ2nLb` | ignorado (sem ordens) |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR>B&H, melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Band-Zigzag | BTC | 51 | 48 | 1 | 5 | +66.1% (4h bb20 1.5 latest ambos) | +43.8% |
| Band-Zigzag | ETH | 50 | 50 | 10 | 26 | +122.7% (1h bb20 3 latest ambos) | +56.8% |
| Band-Zigzag | US100 | 50 | 41 | 0 | 0 | +12.0% (1h bb20 1.5 semlatest long) | +20.3% |
| Band-Zigzag | WTI | 53 | 7 | 0 | 4 | +25.4% (30min bb20 1.5 semlatest ambos) | +5.4% |
| Band-Zigzag | XAU | 50 | 16 | 0 | 0 | +5.5% (1h bb20 3 semlatest ambos) | +13.4% |
| FTSMA | BTC | 20 | 20 | 11 | 11 | +89.7% (4h 5/20/200 ft ambos) | +43.8% |
| FTSMA | ETH | 20 | 20 | 11 | 13 | +148.5% (30min 5/20/200 semft ambos) | +56.8% |
| FTSMA | US100 | 20 | 20 | 3 | 0 | +13.9% (30min 5/20/200 semft long) | +20.3% |
| FTSMA | WTI | 20 | 10 | 0 | 6 | +12.7% (1h 5/20/200 ft ambos) | +5.4% |
| FTSMA | XAU | 20 | 18 | 0 | 0 | +9.1% (1h 5/20/200 semft ambos) | +13.4% |
| Grid Like | BTC | 55 | 31 | 1 | 5 | +71.1% (1D p0.25% ambos) | +43.8% |
| Grid Like | ETH | 55 | 34 | 1 | 4 | +77.2% (1D p5.00% ambos) | +56.8% |
| Grid Like | US100 | 55 | 28 | 1 | 0 | +15.5% (15min p2.00% ambos) | +20.3% |
| Grid Like | WTI | 55 | 5 | 0 | 6 | +18.7% (4h p2.00% ambos) | +5.4% |
| Grid Like | XAU | 55 | 32 | 1 | 0 | +12.2% (30min p2.00% ambos) | +13.4% |
| HULLTSIBOT | BTC | 30 | 19 | 2 | 3 | +58.1% (30min 100/50/7 ambos) | +43.8% |
| HULLTSIBOT | ETH | 30 | 21 | 3 | 5 | +160.3% (30min 100/50/7 ambos) | +56.8% |
| HULLTSIBOT | US100 | 30 | 14 | 0 | 0 | +13.3% (4h 25/13/7 long) | +20.3% |
| HULLTSIBOT | WTI | 30 | 6 | 2 | 4 | +45.5% (1h 100/50/7 ambos) | +5.4% |
| HULLTSIBOT | XAU | 30 | 12 | 2 | 0 | +11.5% (1h 50/50/7 ambos) | +13.4% |
| Supertrend CCI | BTC | 40 | 31 | 2 | 3 | +69.0% (1D cci50 ambos) | +43.8% |
| Supertrend CCI | ETH | 40 | 37 | 6 | 13 | +132.5% (30min cci50 ambos) | +56.8% |
| Supertrend CCI | US100 | 40 | 31 | 7 | 0 | +11.6% (30min cci100 long) | +20.3% |
| Supertrend CCI | WTI | 40 | 10 | 0 | 3 | +13.3% (1h cci50 ambos) | +5.4% |
| Supertrend CCI | XAU | 40 | 20 | 1 | 0 | +8.6% (4h cci28 ambos) | +13.4% |
XAU e US100: nenhuma célula acima do B&H.

## Robustez

| Célula | Tudo | Terços (B&H) | 2ª metade (B&H) | Custo 4× | DD log | Veredito |
|---|---|---|---|---|---|---|
| **ETH FTSMA 30m (EMAs 5/20/200)** | +149% | +614/+50/+30% (+330/+0,7/−11%) | +26% (+13%) | +126% | −82% | **passa**; vizinhança 15m-4h toda acima do B&H com t > 2 |
| ETH HULLTSIBOT 30m 100/50 | +160% | +385/+73/+105% | +79% | +113% | −119% | reprova: célula isolada (50/50 e 25/13 negativos; 15m negativo) |
| ETH Supertrend CCI 30m cci50 | +133% | +268/+140/+39% (1º abaixo) | +45% | +57% (= B&H) | −61% | reprova: custo 4× |
| ETH Band-Zigzag 1h bb3 | +123% | +598/+4/+33% | +16% | +122% | −124% | reprova: terço do meio ≈ 0, t 1,5 |
| BTC FTSMA 4h | +90% | +236/+78/−8% (+129/+15/+14%) | +28% (+40%) | +88% | −63% | reprova: último terço negativo |
| BTC FTSMA 30m | +68% | +178/+32/+25% | +30% (+40%) | +51% | −69% | quase: passa nos terços, perde na 2ª metade |
| BTC Supertrend CCI 1D cci50 | +69% | +176/+32/+22% | +39% (+39%) | +68% | −78% | quase: 2ª metade empata, t baixo nos terços |
| WTI HULLTSIBOT 1h 100/50 | +46% | +38/+89/+15% (−19/+36/+8%) | +17% (+3%) | +28% | −93% | reprova: célula isolada |

## Veredito

**FTSMA no ETH 30m entra como candidata** em [APROVADAS](APROVADAS.md): passa nos três terços, na 2ª metade e com custo 4×, e a vizinhança (15m a 4h) é toda acima do B&H. Ressalvas: o termo de Fourier não faz diferença, então ela é na prática um cruzamento EMA5 × EMA20 filtrado pela EMA200, outro seguidor de tendência no ETH (mesma família das candidatas 2 a 4); DD −82% (log); custo do ETH estimado. No BTC a mesma regra quase passa (30m perde só na 2ª metade).
