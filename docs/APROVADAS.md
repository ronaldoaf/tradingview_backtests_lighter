# Estratégias aprovadas nos testes

Revisão de 2026-10-23: métrica corrigida e critério para carteira de [PROTOCOLO.md](PROTOCOLO.md#critério-de-aprovação-a-partir-de-2026-10-23). Os números saem de `scripts/study_veredito.py` → [`results/study_veredito.txt`](../results/study_veredito.txt) e `.csv`. Nenhuma está aprovada para dinheiro real: todas são **candidatas** para paper/forward test.

Convenções: sinal no fechamento, ordem na abertura seguinte, spread + funding de cada ativo, retornos a 1x. CAGR anual líquido, composto trade a trade. DD simples (equity / máximo − 1). Sharpe dos retornos diários contando os dias parados, ao lado do Sharpe do B&H calculado do mesmo jeito. Terços e 2ª metade rodados de novo em cada fatia, como nos scripts `_rob`.

## O que mudou

- **Métrica.** O CAGR antigo somava `log(close).diff() × posição`, o que creditava ao vendido `log(P0/P1)` em vez de `1 − P1/P0` e marcava a posição com uma barra de atraso. Nas 30 aprovadas de antes o CAGR caiu, em mediana, 30 pontos por ano (de 5 pontos no Trailing SL do ouro a 81 no Chandelier do ETH); só o Swing HULL + T3 subiu.
- **Critério.** Antes: bater o CAGR do B&H no período todo, em cada terço, na 2ª metade e com custo 4×. Agora: líquido positivo em cada terço, Sharpe pelo menos o do B&H, t > 2 contra o controle, positivo com spread 4× e sem funding, e correlação abaixo de 0,5 com as já aprovadas (entram por ordem de Sharpe).
- **Universo.** As 306 células que chegaram à robustez nos lotes 3 a 33, aprovadas ou não, sem repetir a mesma regra testada em dois lotes.

## Resumo

- **Critério novo:** 120 células passam nos itens 1 a 4 e **34 entram** depois do filtro de correlação: 15 no ETH, 8 no BTC, 8 no WTI e 3 no ouro. Nenhuma no US100.
- **As 30 de antes:** 6 entram (§4c, §8, §16, §17, §18, §24), 17 passam mas são redundantes com alguma que entrou, e 7 reprovam: as quatro do WTI (§9, §20, §21, §25), §4b Ichimoku, §6 ABCD e §12 VWAPStrategy.
- **Critério antigo com a conta corrigida:** 13 passam, e só 5 delas estavam entre as 30 (§2, §5, §16, §21, §22).
- **Quase:** 95 células falham em um item só do critério novo, a maioria por Sharpe abaixo do B&H (31) ou t ≤ 2 (25).

Como ler: o critério novo é mais largo que o antigo, porque não exige bater o B&H em todo regime, só ganhar em cada terço com risco ajustado pelo menos igual ao do B&H. Com 306 células testadas, algumas passam por acaso (só o t > 2 deixa passar uns 2% de células sem sinal nenhum). A seleção também não é cega: os terços e a 2ª metade são os mesmos dados usados para aprovar. A lista serve para escolher a carteira de paper, não para operar as 34.

## Aprovadas (critério novo)

Ordem de Sharpe, que é a ordem em que entraram no filtro de correlação. Terços = CAGR em cada terço do período; spread 4× e sem funding = CAGR nesses cenários.

| # | Estratégia | Ativo | Configuração | CAGR (B&H) | Sharpe (B&H) | DD | t | Terços | Spread 4× | Sem funding | Lote |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | :---: |
| 1 | Heikin Ashi MACD | ETH 1h | sem stop/alvo | +171% (+57%) | 1,69 (0,96) | −82% | 4,96 | +365% / +80% / +127% | +129% | +171% | [28](LOTE28_TV.md) |
| 2 | BEST Supertrend | ETH 1h | só comprado | +90% (+57%) | 1,68 (0,96) | −40% | 4,10 | +288% / +41% / +23% | +82% | +96% | [24](LOTE24_TV.md) |
| 3 | Delta-RSI | BTC 1h | rl 21, window 50, mode zero | +115% (+44%) | 1,66 (0,91) | −56% | 4,03 | +339% / +80% / +26% | +83% | +115% | [14](LOTE14_TV.md) |
| 4 | Swing HULL + T3 (§16) | ETH 1h | ln 100 | +142% (+57%) | 1,48 (0,96) | −68% | 4,11 | +767% / +41% / +11% | +114% | +144% | [25](LOTE25_TV.md) |
| 5 | Gold/Silver RSI + EMA162 | WTI 4h | padrão do script | +55% (+5%) | 1,46 (0,35) | −50% | 2,37 | +32% / +33% / +63% | +55% | +1% | [21](LOTE21_TV.md) |
| 6 | Simple RSI-MA | ETH 15m | rl 5, ml 50 | +128% (+57%) | 1,44 (0,96) | −60% | 4,60 | +305% / +53% / +85% | +79% | +130% | [12](LOTE12_TV.md) |
| 7 | Force trade scalper | BTC 4h | fast 5, slow 50, só comprado | +61% (+44%) | 1,44 (0,91) | −33% | 2,47 | +169% / +35% / +12% | +60% | +68% | [22](LOTE22_TV.md) |
| 8 | Crypto Squeeze | ETH 4h | mfl 14 | +108% (+57%) | 1,36 (0,96) | −67% | 2,71 | +194% / +97% / +116% | +104% | +107% | [26](LOTE26_TV.md) |
| 9 | Scalping Trading System (§4c) | ETH 30m | sma_len 25, ema_len 0 | +97% (+57%) | 1,25 (0,96) | −57% | 3,31 | +318% / +17% / +52% | +74% | +105% | [13](LOTE13_TV.md) |
| 10 | SuperTrend Enhanced Pivot Reversal | ETH 4h | padrão do script | +92% (+57%) | 1,25 (0,96) | −68% | 2,15 | +99% / +82% / +77% | +91% | +93% | [32](LOTE32_TV.md) |
| 11 | Combo 123 Reversal & Stoch | ETH 4h | padrão do script | +75% (+57%) | 1,21 (0,96) | −50% | 2,63 | +255% / +17% / +34% | +74% | +82% | [31](LOTE31_TV.md) |
| 12 | Wyckoff Range (§18) | ETH 4h | sl 0,03 | +65% (+57%) | 1,20 (0,96) | −50% | 2,93 | +215% / +15% / +24% | +64% | +67% | [27](LOTE27_TV.md) |
| 13 | Combo 123 Reversal & Stoch | BTC 1h | padrão do script | +58% (+44%) | 1,18 (0,91) | −58% | 2,66 | +123% / +67% / +5% | +51% | +64% | [31](LOTE31_TV.md) |
| 14 | Triple EMA Trend | ETH 15m | comprado e vendido | +48% (+57%) | 1,18 (0,96) | −52% | 4,33 | +52% / +44% / +49% | +35% | +48% | [23](LOTE23_TV.md) |
| 15 | Delta-RSI | BTC 4h | rl 21, window 100, mode zero | +67% (+44%) | 1,17 (0,91) | −69% | 2,51 | +51% / +121% / +35% | +63% | +67% | [14](LOTE14_TV.md) |
| 16 | Multi-MA (§24) | BTC 4h | ln 150 | +61% (+44%) | 1,16 (0,91) | −54% | 3,33 | +168% / +46% / +3% | +60% | +61% | [30](LOTE30_TV.md) |
| 17 | Delta-RSI | ETH 1h | rl 21, window 50, mode signal | +77% (+57%) | 1,13 (0,96) | −68% | 3,76 | +106% / +55% / +68% | +45% | +77% | [14](LOTE14_TV.md) |
| 18 | Twin Range Filter | ETH 4h | sem stop/alvo | +48% (+57%) | 1,13 (0,96) | −37% | 3,65 | +47% / +68% / +20% | +46% | +48% | [23](LOTE23_TV.md) |
| 19 | Volume fight | BTC 1D | padrão do script | +60% (+44%) | 1,12 (0,91) | −41% | 2,38 | +170% / +50% / +8% | +59% | +57% | [29](LOTE29_TV.md) |
| 20 | Delta-RSI | WTI 4h | rl 14, window 30, mode signal | +51% (+5%) | 1,09 (0,35) | −67% | 3,18 | +22% / +120% / +18% | +36% | +51% | [14](LOTE14_TV.md) |
| 21 | Spot/Binary Scalper | ETH 30m | sl 0,02, session não | +64% (+57%) | 1,09 (0,96) | −53% | 3,16 | +166% / +13% / +46% | +15% | +63% | [15](LOTE15_TV.md) |
| 22 | Scalping Trading System | BTC 1D | sma_len 25, ema_len 0 | +57% (+44%) | 1,08 (0,91) | −63% | 3,25 | +145% / +13% / +33% | +57% | +60% | [13](LOTE13_TV.md) |
| 23 | Trailing SL [QuantNomad] | XAU 4h | val 2,0 | +18% (+13%) | 1,06 (0,82) | −17% | 3,04 | +12% / +8% / +32% | +16% | +18% | [7](LOTE7_TV.md) |
| 24 | 5 EMA (§17) | ETH 4h | rr 3,0 | +70% (+57%) | 1,06 (0,96) | −70% | 2,40 | +170% / +113% / +45% | +66% | +73% | [26](LOTE26_TV.md) |
| 25 | Heikin-Ashi PSAR | XAU 1h | start 0,01, inc 0,01, mx 0,1 | +17% (+13%) | 1,05 (0,82) | −22% | 3,24 | +10% / +14% / +32% | +7% | +18% | [14](LOTE14_TV.md) |
| 26 | MA Consecutive Up/Down (§8) | ETH 4h | nb 4, malen 1 | +66% (+57%) | 1,04 (0,96) | −82% | 2,39 | +171% / +0% / +77% | +63% | +69% | [21](LOTE21_TV.md) |
| 27 | Open Close Cross R5.1 (honesta) | XAU 1h | HULL13 x5 | +16% (+13%) | 1,00 (0,82) | −26% | 2,65 | +17% / +1% / +25% | +9% | +17% | [3](LOTE3_TV.md) |
| 28 | [DS] EMA8 x DEMA34 | BTC 30m | f 8, s 72 | +47% (+44%) | 0,95 (0,91) | −56% | 2,14 | +129% / +18% / +16% | +25% | +47% | [20](LOTE20_TV.md) |
| 29 | Trendline Breakout KedArc | WTI 4h | maf não | +25% (+5%) | 0,87 (0,35) | −43% | 2,91 | +17% / +32% / +16% | +20% | +27% | [25](LOTE25_TV.md) |
| 30 | BotBot | WTI 1D | k 0,02 | +27% (+6%) | 0,80 (0,35) | −51% | 2,32 | +7% / +39% / +11% | +26% | +21% | [29](LOTE29_TV.md) |
| 31 | Linear Channel | WTI 15m | padrão do script | +12% (+5%) | 0,78 (0,35) | −15% | 6,07 | +11% / +23% / +3% | +11% | +12% | [31](LOTE31_TV.md) |
| 32 | Stoch + ATR | WTI 4h | ln 14 | +28% (+5%) | 0,77 (0,35) | −73% | 2,58 | +19% / +74% / +1% | +20% | +36% | [25](LOTE25_TV.md) |
| 33 | Crazy Scalping (TradeIQ) | WTI 1h | sll 30 | +13% (+5%) | 0,77 (0,35) | −29% | 2,91 | +22% / +16% / +2% | +10% | +11% | [23](LOTE23_TV.md) |
| 34 | Nadaraya-Watson | WTI 1D | hlen 8, x0 25, comprado e vendido | +22% (+6%) | 0,66 (0,35) | −74% | 2,75 | +32% / +10% / +1% | +21% | +18% | [20](LOTE20_TV.md) |

Ressalvas:

- **Gold/Silver RSI + EMA162 no WTI 4h:** quase todo o ganho é funding (sem funding, +1% a.a.). Só vale se o funding do WTI na Lighter for mesmo o da média usada (67,7% a.a. que o long paga).
- **BEST Supertrend ETH 1h, Force trade scalper BTC 4h e Linear Channel WTI 15m** são só compradas; as outras operam dos dois lados.
- **Open Close Cross (lote 3)** é a versão honesta do script, com o candle da resolução maior já fechado; a publicada olha o futuro.
- Várias do ETH têm DD de −60% a −82% a 1x. Na carteira o tamanho tem de ser por volatilidade.
- O custo do ETH é estimado (igual ao do BTC), não medido na Lighter.

## Passam, mas são redundantes

Passam nos itens 1 a 4 do critério, mas têm correlação de 0,5 ou mais com uma que entrou antes (coluna "com"). Servem de reserva se a que entrou cair no paper.

| Estratégia | Ativo | Configuração | CAGR | Sharpe | t | corr | com | Lote |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | :---: |
| Simple RSI-MA (§2) | ETH 15m | rl 10, ml 50 | +156% | 1,59 | 4,50 | 0,50 | BEST Supertrend ETH 1h | [12](LOTE12_TV.md) |
| Delta-RSI | ETH 30m | rl 21, window 100, mode zero | +144% | 1,56 | 5,07 | 0,64 | Heikin Ashi MACD ETH 1h | [14](LOTE14_TV.md) |
| Delta-RSI | BTC 30m | rl 21, window 100, mode zero | +105% | 1,54 | 4,56 | 0,82 | Delta-RSI BTC 1h | [14](LOTE14_TV.md) |
| Super trend V | ETH 15m | padrão do script | +100% | 1,53 | 2,45 | 0,71 | BEST Supertrend ETH 1h | [23](LOTE23_TV.md) |
| SuperTrend Enhanced Pivot Reversal | ETH 4h | só comprado | +96% | 1,48 | 2,15 | 0,67 | BEST Supertrend ETH 1h | [32](LOTE32_TV.md) |
| Multi-MA (§22) | ETH 15m | ln 150 | +125% | 1,48 | 3,23 | 0,77 | Swing HULL + T3 ETH 1h | [30](LOTE30_TV.md) |
| Slopes | ETH 4h | só comprado | +82% | 1,47 | 2,89 | 0,69 | BEST Supertrend ETH 1h | [22](LOTE22_TV.md) |
| BEST Supertrend (§11) | ETH 1h | padrão do script | +102% | 1,46 | 6,07 | 0,73 | BEST Supertrend ETH 1h | [24](LOTE24_TV.md) |
| Slopes | ETH 4h | padrão do script | +109% | 1,45 | 3,32 | 0,51 | Swing HULL + T3 ETH 1h | [22](LOTE22_TV.md) |
| FTSMA | ETH 30m | use_ft não | +118% | 1,45 | 3,63 | 0,75 | Swing HULL + T3 ETH 1h | [17](LOTE17_TV.md) |
| Super trend V (§10) | ETH 15m | comprado e vendido | +118% | 1,44 | 3,08 | 0,77 | Swing HULL + T3 ETH 1h | [23](LOTE23_TV.md) |
| FTSMA (§5) | ETH 30m | use_ft sim | +115% | 1,43 | 4,56 | 0,74 | Swing HULL + T3 ETH 1h | [17](LOTE17_TV.md) |
| Martin Pring's Special K | ETH 30m | sm 30, só comprado | +89% | 1,42 | 3,13 | 0,61 | BEST Supertrend ETH 1h | [27](LOTE27_TV.md) |
| VWAP X EMA | ETH 4h | ef 20, só comprado | +75% | 1,40 | 2,35 | 0,76 | BEST Supertrend ETH 1h | [33](LOTE33_TV.md) |
| Triangular Hull MA (§14) | ETH 15m | ln 100 | +116% | 1,39 | 3,40 | 0,78 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| Heikin Ashi MACD (§19) | BTC 1h | padrão do script | +81% | 1,37 | 2,72 | 0,56 | Delta-RSI BTC 1h | [28](LOTE28_TV.md) |
| TASC 2024.08 VCTS | ETH 4h | thr 20, lv 50 | +64% | 1,36 | 2,48 | 0,58 | BEST Supertrend ETH 1h | [33](LOTE33_TV.md) |
| PMax (Profit Maximizer) | ETH 4h | padrão do script | +79% | 1,33 | 2,73 | 0,69 | BEST Supertrend ETH 1h | [28](LOTE28_TV.md) |
| RSI PrimeAutomation | ETH 4h | tpm 0, só comprado | +61% | 1,32 | 2,06 | 0,66 | BEST Supertrend ETH 1h | [23](LOTE23_TV.md) |
| Ichimoku + EMA filter | ETH 4h | padrão do script | +63% | 1,32 | 2,78 | 0,72 | BEST Supertrend ETH 1h | [33](LOTE33_TV.md) |
| Vegas SuperTrend Enhanced | ETH 4h | só comprado | +76% | 1,31 | 2,44 | 0,70 | BEST Supertrend ETH 1h | [26](LOTE26_TV.md) |
| BEST Trailing Stop | ETH 30m | padrão do script | +90% | 1,29 | 2,89 | 0,69 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| Force trade scalper | BTC 4h | fast 5, slow 50 | +72% | 1,28 | 2,35 | 0,71 | Force trade scalper BTC 4h | [22](LOTE22_TV.md) |
| Force trade scalper | ETH 1h | fast 5, slow 50, só comprado | +68% | 1,28 | 2,11 | 0,59 | BEST Supertrend ETH 1h | [22](LOTE22_TV.md) |
| VWAP X EMA (§28) | ETH 30m | padrão do script | +92% | 1,27 | 3,43 | 0,64 | Simple RSI-MA ETH 15m | [33](LOTE33_TV.md) |
| SuperTrend STRATEGY | ETH 4h | comprado e vendido | +91% | 1,27 | 2,55 | 0,52 | BEST Supertrend ETH 1h | [26](LOTE26_TV.md) |
| Smoothed Heiken Ashi | ETH 30m | ln 20 | +74% | 1,25 | 2,05 | 0,72 | BEST Supertrend ETH 1h | [31](LOTE31_TV.md) |
| Smart Money Pivot (§15) | ETH 15m | sl 0,0, tp 0,0 | +93% | 1,24 | 2,86 | 0,57 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| Simple RSI-MA | ETH 30m | rl 10, ml 20 | +93% | 1,23 | 3,49 | 0,81 | Simple RSI-MA ETH 15m | [12](LOTE12_TV.md) |
| Signal To Noise | ETH 30m | ln 42 | +92% | 1,23 | 3,08 | 0,61 | Swing HULL + T3 ETH 1h | [33](LOTE33_TV.md) |
| Multi-MA (§23) | ETH 4h | padrão do script | +87% | 1,23 | 2,38 | 0,61 | SuperTrend Enhanced Pivot Reversal ETH 4h | [30](LOTE30_TV.md) |
| TSI w SuperTrend (§27) | ETH 30m | per 32 | +91% | 1,21 | 5,42 | 0,83 | Simple RSI-MA ETH 15m | [32](LOTE32_TV.md) |
| SuperTREX | BTC 1h | mult 4,0, só comprado | +52% | 1,21 | 2,64 | 0,76 | Force trade scalper BTC 4h | [21](LOTE21_TV.md) |
| Follow Line | ETH 4h | ln 50, dev 2,0 | +83% | 1,21 | 4,51 | 0,51 | SuperTrend Enhanced Pivot Reversal ETH 4h | [20](LOTE20_TV.md) |
| HullMA | ETH 30m | n 100 | +88% | 1,21 | 3,30 | 0,75 | Simple RSI-MA ETH 15m | [14](LOTE14_TV.md) |
| Martin Pring's Special K | ETH 30m | sm 30 | +89% | 1,20 | 3,83 | 0,65 | Simple RSI-MA ETH 15m | [27](LOTE27_TV.md) |
| Golden X BF | ETH 15m | p (20, 100) | +86% | 1,19 | 3,15 | 0,75 | Simple RSI-MA ETH 15m | [31](LOTE31_TV.md) |
| Liquidity Sweep Filter | ETH 1h | ln 12, mult 2,0, comprado e vendido | +81% | 1,17 | 3,45 | 0,69 | Swing HULL + T3 ETH 1h | [21](LOTE21_TV.md) |
| Triple EMA Trend | BTC 4h | comprado e vendido | +44% | 1,16 | 3,20 | 0,50 | Multi-MA BTC 4h | [23](LOTE23_TV.md) |
| EMA Cross + RSI + ADX | BTC 4h | sl 0,05 | +52% | 1,16 | 3,48 | 0,52 | Force trade scalper BTC 4h | [25](LOTE25_TV.md) |
| TSI w SuperTrend (§26) | ETH 15m | padrão do script | +84% | 1,16 | 3,13 | 0,85 | Simple RSI-MA ETH 15m | [32](LOTE32_TV.md) |
| EMA Slope | ETH 30m | ln 130, trend sim | +70% | 1,16 | 4,24 | 0,73 | Simple RSI-MA ETH 15m | [18](LOTE18_TV.md) |
| Supertrend CCI | BTC 1D | n 50 | +60% | 1,15 | 2,92 | 0,90 | Multi-MA BTC 4h | [17](LOTE17_TV.md) |
| UT Bot v5 (§4a) | ETH 30m | a 5,0, atr_n 11, comprado e vendido | +78% | 1,15 | 2,46 | 0,56 | Swing HULL + T3 ETH 1h | [13](LOTE13_TV.md) |
| SSL Channel Cross | BTC 1D | ln 50 | +59% | 1,14 | 3,25 | 0,85 | Multi-MA BTC 4h | [27](LOTE27_TV.md) |
| Combo 123 Reversal & Stoch | ETH 30m | ln 28 | +67% | 1,13 | 2,30 | 0,52 | BEST Supertrend ETH 1h | [31](LOTE31_TV.md) |
| SuperTREX | BTC 30m | mult 8,0, comprado e vendido | +59% | 1,12 | 2,98 | 0,72 | Multi-MA BTC 4h | [21](LOTE21_TV.md) |
| Percent Trailing Stop | ETH 1h | trl 0,05 | +73% | 1,11 | 2,65 | 0,71 | Simple RSI-MA ETH 15m | [30](LOTE30_TV.md) |
| Multi-MA | BTC 15m | ln 150 | +59% | 1,11 | 3,06 | 0,52 | Combo 123 Reversal & Stoch BTC 1h | [30](LOTE30_TV.md) |
| 2x Universelle Linien | ETH 30m | padrão do script | +74% | 1,11 | 2,89 | 0,73 | Simple RSI-MA ETH 15m | [30](LOTE30_TV.md) |
| Chandelier Exit (§13) | ETH 30m | padrão do script | +72% | 1,09 | 2,83 | 0,66 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| Multi-MA | BTC 30m | padrão do script | +58% | 1,09 | 2,18 | 0,51 | Combo 123 Reversal & Stoch BTC 1h | [30](LOTE30_TV.md) |
| EMA Cross | BTC 4h | f 50, s 200 | +55% | 1,09 | 3,41 | 0,84 | Multi-MA BTC 4h | [16](LOTE16_TV.md) |
| Ichimoku + MACD/CMF/TSI | ETH 30m | padrão do script | +69% | 1,07 | 2,56 | 0,65 | Swing HULL + T3 ETH 1h | [25](LOTE25_TV.md) |
| Follow Line (§7) | ETH 30m | ln 21, dev 1,0 | +69% | 1,06 | 2,58 | 0,72 | Simple RSI-MA ETH 15m | [20](LOTE20_TV.md) |
| Triangular Hull MA | ETH 30m | padrão do script | +69% | 1,06 | 2,28 | 0,78 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| Pivot of Pivot Reversal | BTC 4h | lb 10, rb 5 | +55% | 1,05 | 2,29 | 0,72 | Multi-MA BTC 4h | [25](LOTE25_TV.md) |
| EMA Cross | ETH 15m | f 50, s 200 | +65% | 1,04 | 2,56 | 0,83 | Swing HULL + T3 ETH 1h | [16](LOTE16_TV.md) |
| FTSMA | BTC 30m | use_ft sim | +52% | 1,02 | 2,45 | 0,53 | Combo 123 Reversal & Stoch BTC 1h | [17](LOTE17_TV.md) |
| HHLL | ETH 1h | ln 29 | +62% | 1,02 | 2,43 | 0,56 | Swing HULL + T3 ETH 1h | [19](LOTE19_TV.md) |
| Y-PMax | ETH 15m | ln 30, mult 3,0, comprado e vendido | +63% | 1,01 | 2,91 | 0,73 | Simple RSI-MA ETH 15m | [20](LOTE20_TV.md) |
| SuperTrend (chandelier 7/7) | BTC 4h | padrão do script | +49% | 1,01 | 2,40 | 0,70 | Multi-MA BTC 4h | [33](LOTE33_TV.md) |
| SuperTREX | BTC 4h | mult 2,0, comprado e vendido | +49% | 1,00 | 3,01 | 0,67 | Multi-MA BTC 4h | [21](LOTE21_TV.md) |
| HULLTSIBOT | ETH 30m | ln 100, sh 50 | +61% | 1,00 | 3,93 | 0,56 | Heikin Ashi MACD ETH 1h | [17](LOTE17_TV.md) |
| HMA50 + Supertrend | ETH 30m | hl 100 | +60% | 1,00 | 3,01 | 0,75 | Simple RSI-MA ETH 15m | [24](LOTE24_TV.md) |
| Simple RSI-MA | BTC 15m | rl 10, ml 50 | +51% | 1,00 | 3,92 | 0,54 | Simple RSI-MA ETH 15m | [12](LOTE12_TV.md) |
| Trailing SL [QuantNomad] | XAU 1h | val 2,0 | +16% | 1,00 | 3,25 | 0,78 | Trailing SL [QuantNomad] XAU 4h | [7](LOTE7_TV.md) |
| Parabolic SAR w/ EMA | BTC 30m | off 0,0 | +46% | 0,99 | 2,47 | 0,53 | Combo 123 Reversal & Stoch BTC 1h | [31](LOTE31_TV.md) |
| Pivot Point SuperTrend (§3) | ETH 15m | prd 5, F 2,0, Pd 10 | +60% | 0,99 | 2,76 | 0,68 | Simple RSI-MA ETH 15m | [4](LOTE4_TV.md) |
| BEST ATR Stop Multiple | ETH 15m | padrão do script | +56% | 0,99 | 2,86 | 0,60 | Simple RSI-MA ETH 15m | [25](LOTE25_TV.md) |
| TK Cross > EMA200 | ETH 30m | conv 20, base 60, ema_len 200, comprado e vendido | +57% | 0,98 | 2,54 | 0,77 | Swing HULL + T3 ETH 1h | [12](LOTE12_TV.md) |
| Trend Surfers | ETH 4h | per 55 | +55% | 0,98 | 3,30 | 0,61 | SuperTrend Enhanced Pivot Reversal ETH 4h | [21](LOTE21_TV.md) |
| Liquidity Sweep Filter | ETH 15m | ln 30, mult 1,0, comprado e vendido | +58% | 0,97 | 3,39 | 0,74 | Simple RSI-MA ETH 15m | [21](LOTE21_TV.md) |
| BEST Supertrend | BTC 1h | padrão do script | +41% | 0,97 | 3,31 | 0,62 | Multi-MA BTC 4h | [24](LOTE24_TV.md) |
| Real Turtle | XAU 1h | nb 1, start 0,01, mx 0,1 | +15% | 0,96 | 3,40 | 0,86 | Heikin-Ashi PSAR XAU 1h | [22](LOTE22_TV.md) |
| Trailing SL [QuantNomad] (§1) | XAU 30m | val 2,0 | +16% | 0,95 | 4,42 | 0,70 | Trailing SL [QuantNomad] XAU 4h | [7](LOTE7_TV.md) |
| Golden X BF | BTC 4h | p (20, 100) | +44% | 0,94 | 2,69 | 0,60 | Multi-MA BTC 4h | [31](LOTE31_TV.md) |
| Swing Parabolic SAR | XAU 1h | p (0,01, 0,01, 0,1) | +15% | 0,93 | 4,17 | 0,67 | Heikin-Ashi PSAR XAU 1h | [31](LOTE31_TV.md) |
| Trailing SL [QuantNomad] | XAU 15m | val 2,0 | +15% | 0,93 | 3,99 | 0,64 | Trailing SL [QuantNomad] XAU 4h | [7](LOTE7_TV.md) |
| EMA Slope | BTC 4h | ln 50, trend sim | +37% | 0,92 | 2,27 | 0,53 | Multi-MA BTC 4h | [18](LOTE18_TV.md) |
| PMax on RSI w T3 | XAU 30m | mult 1,5, tl 20 | +14% | 0,90 | 3,02 | 0,54 | Heikin-Ashi PSAR XAU 1h | [22](LOTE22_TV.md) |
| Twin OTT (TOTT) | XAU 30m | VAR20 p.5 c0 | +14% | 0,87 | 2,30 | 0,65 | Trailing SL [QuantNomad] XAU 4h | [3](LOTE3_TV.md) |
| Twin OTT (TOTT) | XAU 30m | VAR20 p1 c.005 | +14% | 0,86 | 2,62 | 0,78 | Trailing SL [QuantNomad] XAU 4h | [3](LOTE3_TV.md) |
| HULLTSIBOT | WTI 1h | ln 100, sh 50 | +36% | 0,86 | 2,85 | 0,71 | Delta-RSI WTI 4h | [17](LOTE17_TV.md) |
| TSI CCI Hull | XAU 15m | padrão do script | +13% | 0,83 | 2,78 | 0,61 | Heikin-Ashi PSAR XAU 1h | [27](LOTE27_TV.md) |
| Linear Channel | WTI 15m | hl 200 | +10% | 0,77 | 12,43 | 0,83 | Linear Channel WTI 15m | [31](LOTE31_TV.md) |

## Quase: falham em um item só

As 25 de maior Sharpe; a lista completa (95) está em `results/study_veredito.txt`.

| Estratégia | Ativo | Configuração | CAGR (B&H) | Sharpe (B&H) | t | Terços | Falha | Lote |
| --- | --- | --- | --- | --- | ---: | --- | --- | :---: |
| VWAP X EMA | ETH 30m | só comprado | +91% (+57%) | 1,53 (0,96) | 1,97 | +343% / +31% / +18% | t ≤ 2 | [33](LOTE33_TV.md) |
| VWAPStrategy | ETH 15m | padrão do script | +141% (+57%) | 1,51 (0,96) | 4,79 | +722% / −4% / +72% | negativo no 2º terço | [24](LOTE24_TV.md) |
| Breakout Trend Follower | ETH 30m | lb 10 | +86% (+57%) | 1,39 (0,96) | 1,59 | +392% / +6% / +21% | t ≤ 2 | [22](LOTE22_TV.md) |
| VWAPStrategy (§12) | ETH 30m | padrão do script | +114% (+57%) | 1,35 (0,96) | 5,54 | +398% / −11% / +115% | negativo no 2º terço | [24](LOTE24_TV.md) |
| ZigZag RSI | BTC 15m | rl 14, os_ 30, ob 70 | +52% (+44%) | 1,34 (0,91) | 1,65 | +73% / +43% / +39% | t ≤ 2 | [23](LOTE23_TV.md) |
| FTSMA | BTC 4h | use_ft sim | +73% (+44%) | 1,32 (0,91) | 2,67 | +180% / +73% / −12% | negativo no 3º terço | [17](LOTE17_TV.md) |
| Golden Vector Trend Orchestrator | ETH 4h | só comprado | +63% (+57%) | 1,29 (0,96) | 1,82 | +127% / +35% / +33% | t ≤ 2 | [28](LOTE28_TV.md) |
| ATR Parabolic SAR | BTC 4h | só comprado | +56% (+44%) | 1,29 (0,91) | 1,63 | +126% / +47% / +19% | t ≤ 2 | [22](LOTE22_TV.md) |
| MACD + trailing ATR | BTC 30m | mult 2,2, tp 0,05, filt sim | +63% (+44%) | 1,23 (0,91) | 1,84 | +178% / +48% / +7% | t ≤ 2 | [20](LOTE20_TV.md) |
| Donchian Channel | ETH 30m | só comprado | +60% (+57%) | 1,21 (0,96) | 1,88 | +217% / +12% / +14% | t ≤ 2 | [32](LOTE32_TV.md) |
| EDMA | WTI 1D | ln 20, e1 40 | +42% (+6%) | 1,21 (0,35) | 1,82 | +9% / +26% / +53% | t ≤ 2 | [16](LOTE16_TV.md) |
| Combo 123 Reversal & Stoch | ETH 15m | ln 28 | +76% (+57%) | 1,21 (0,96) | 2,38 | +198% / −11% / +100% | negativo no 2º terço | [31](LOTE31_TV.md) |
| SuperTREX | BTC 1h | mult 4,0, comprado e vendido | +66% (+44%) | 1,20 (0,91) | 2,42 | +157% / +77% / −11% | negativo no 3º terço | [21](LOTE21_TV.md) |
| Ichimoku básico (§4b) | ETH 15m | ts 20, ks 60, sb 120, off 60 | +86% (+57%) | 1,19 (0,96) | 2,85 | +393% / −13% / +47% | negativo no 2º terço | [13](LOTE13_TV.md) |
| Heikin Ashi MACD | BTC 1h | sem stop/alvo | +69% (+44%) | 1,19 (0,91) | 3,53 | +171% / +79% / −1% | negativo no 3º terço | [28](LOTE28_TV.md) |
| Slopes | BTC 1D | tf_ não, só comprado | +47% (+44%) | 1,17 (0,91) | 1,89 | +128% / +28% / +10% | t ≤ 2 | [22](LOTE22_TV.md) |
| KAMA TradeDots | ETH 4h | rp 5 | +64% (+57%) | 1,16 (0,96) | 1,52 | +181% / +27% / +13% | t ≤ 2 | [29](LOTE29_TV.md) |
| Wyckoff Range | ETH 4h | padrão do script | +73% (+57%) | 1,15 (0,96) | 2,90 | +281% / +53% / −21% | negativo no 3º terço | [27](LOTE27_TV.md) |
| Crypto Scalper | ETH 15m | padrão do script | +76% (+57%) | 1,15 (0,96) | 2,94 | +356% / −6% / +39% | negativo no 2º terço | [14](LOTE14_TV.md) |
| EMA Crossover | ETH 1h | ln 50, ratio 5, só comprado | +62% (+57%) | 1,14 (0,96) | 1,97 | +228% / +12% / +11% | t ≤ 2 | [22](LOTE22_TV.md) |
| Pivot Point Reversal + RSI | XAU 1h | lb 6, rb 3 | +19% (+13%) | 1,13 (0,82) | 4,61 | +22% / −4% / +43% | negativo no 2º terço | [26](LOTE26_TV.md) |
| Liquidity Sweep Filter | BTC 1h | ln 30, mult 2,0, comprado e vendido | +58% (+44%) | 1,10 (0,91) | 3,49 | +154% / +63% / −6% | negativo no 3º terço | [21](LOTE21_TV.md) |
| AI Volume SuperTrend | ETH 4h | ln 20, fac 5,0 | +68% (+57%) | 1,09 (0,96) | 1,96 | +129% / +7% / +48% | t ≤ 2 | [16](LOTE16_TV.md) |
| Linear Regression Channel Breakout | ETH 1h | só comprado | +102% (+57%) | 1,09 (0,96) | 2,87 | +722% / −1% / +14% | negativo no 2º terço | [29](LOTE29_TV.md) |
| TMFS | ETH 4h | swing 20, tp 0,0 | +59% (+57%) | 1,08 (0,96) | 1,99 | +138% / +40% / +8% | t ≤ 2 | [15](LOTE15_TV.md) |

## Critério antigo com a conta corrigida

Bater o CAGR do B&H no período todo, nos três terços, na 2ª metade e com spread 4×.

| Estratégia | Ativo | Configuração | CAGR (B&H) | Sharpe (B&H) | t | Terços (B&H) | 2ª metade (B&H) | Critério novo | Lote |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | :---: |
| Heikin Ashi MACD | ETH 1h | sem stop/alvo | +171% (+57%) | 1,69 (0,96) | 4,96 | +365% / +80% / +127% (+330% / +1% / −11%) | +112% (+13%) | entra | [28](LOTE28_TV.md) |
| Simple RSI-MA (§2) | ETH 15m | rl 10, ml 50 | +156% (+57%) | 1,59 (0,96) | 4,50 | +394% / +65% / +99% (+330% / +1% / −11%) | +50% (+13%) | redundante | [12](LOTE12_TV.md) |
| VWAP X EMA | ETH 30m | só comprado | +91% (+57%) | 1,53 (0,96) | 1,97 | +343% / +31% / +18% (+330% / +1% / −11%) | +27% (+13%) | t ≤ 2 | [33](LOTE33_TV.md) |
| Super trend V | ETH 15m | padrão do script | +100% (+57%) | 1,53 (0,96) | 2,45 | +488% / +25% / +6% (+330% / +1% / −11%) | +13% (+13%) | redundante | [23](LOTE23_TV.md) |
| Swing HULL + T3 (§16) | ETH 1h | ln 100 | +142% (+57%) | 1,48 (0,96) | 4,11 | +767% / +41% / +11% (+330% / +1% / −11%) | +15% (+13%) | entra | [25](LOTE25_TV.md) |
| Multi-MA (§22) | ETH 15m | ln 150 | +125% (+57%) | 1,48 (0,96) | 3,23 | +363% / +18% / +105% (+330% / +1% / −11%) | +71% (+13%) | redundante | [30](LOTE30_TV.md) |
| FTSMA | ETH 30m | use_ft não | +118% (+57%) | 1,45 (0,96) | 3,63 | +357% / +53% / +34% (+330% / +1% / −11%) | +39% (+13%) | redundante | [17](LOTE17_TV.md) |
| FTSMA (§5) | ETH 30m | use_ft sim | +115% (+57%) | 1,43 (0,96) | 4,56 | +357% / +74% / +16% (+330% / +1% / −11%) | +35% (+13%) | redundante | [17](LOTE17_TV.md) |
| Breakout Trend Follower | ETH 30m | lb 10 | +86% (+57%) | 1,39 (0,96) | 1,59 | +392% / +6% / +21% (+330% / +1% / −11%) | +15% (+13%) | t ≤ 2 | [22](LOTE22_TV.md) |
| Delta-RSI | WTI 4h | rl 14, window 30, mode signal | +51% (+5%) | 1,09 (0,35) | 3,18 | +22% / +120% / +18% (−21% / +40% / +8%) | +35% (+3%) | entra | [14](LOTE14_TV.md) |
| HULLTSIBOT | WTI 1h | ln 100, sh 50 | +36% (+5%) | 0,86 (0,35) | 2,85 | +17% / +76% / +18% (−19% / +36% / +7%) | +26% (+3%) | redundante | [17](LOTE17_TV.md) |
| BotBot | WTI 1D | k 0,02 | +27% (+6%) | 0,80 (0,35) | 2,32 | +7% / +39% / +11% (−21% / +32% / +8%) | +16% (+3%) | entra | [29](LOTE29_TV.md) |
| PTS Golden Edge (§21) | WTI 30m | f 9, s 50 | +18% (+5%) | 0,58 (0,35) | 1,76 | −19% / +83% / +13% (−19% / +35% / +8%) | +10% (+3%) | negativo no 1º terço; t ≤ 2 | [29](LOTE29_TV.md) |

## As 30 aprovadas até o lote 33

"Antes" é o CAGR na conta antiga (o mesmo dos docs de lote); "agora" é o composto trade a trade.

| § | Estratégia | CAGR antes → agora (B&H) | Sharpe (B&H) | Terços agora (B&H) | 2ª metade (B&H) | Critério antigo | Critério novo |
| --- | --- | --- | --- | --- | --- | :---: | --- |
| §1 | Trailing SL XAU 30m | +20% → **+16%** (+13%) | 0,95 (0,82) | +9% / +9% / +28% (+8% / +5% / +31%) | +21% (+25%) | — | passa, redundante |
| §2 | RSI-MA ETH 15m | +171% → **+156%** (+57%) | 1,59 (0,96) | +394% / +65% / +99% (+330% / +1% / −11%) | +50% (+13%) | passa | passa, redundante |
| §3 | Pivot ST ETH 15m | +81% → **+60%** (+57%) | 0,99 (0,96) | +46% / +75% / +53% (+330% / +1% / −11%) | +60% (+13%) | — | passa, redundante |
| §4a | UT Bot ETH 30m | +131% → **+78%** (+57%) | 1,15 (0,96) | +185% / +70% / +17% (+330% / +1% / −11%) | +21% (+13%) | — | passa, redundante |
| §4b | Ichimoku ETH 15m | +120% → **+86%** (+57%) | 1,19 (0,96) | +393% / −13% / +47% (+330% / +1% / −11%) | +38% (+13%) | — | reprova: negativo no 2º terço |
| §4c | Scalping ETH 30m | +125% → **+97%** (+57%) | 1,25 (0,96) | +318% / +17% / +52% (+330% / +1% / −11%) | +31% (+13%) | — | entra |
| §5 | FTSMA ETH 30m | +148% → **+115%** (+57%) | 1,43 (0,96) | +357% / +74% / +16% (+330% / +1% / −11%) | +35% (+13%) | passa | passa, redundante |
| §6 | ABCD BTC 1h | +70% → **+44%** (+44%) | 0,99 (0,91) | +106% / +12% / +38% (+129% / +15% / +13%) | +51% (+40%) | — | reprova: t ≤ 2 |
| §7 | Follow Line ETH 30m | +118% → **+69%** (+57%) | 1,06 (0,96) | +194% / +15% / +32% (+330% / +1% / −11%) | +14% (+13%) | — | passa, redundante |
| §8 | MA Consec ETH 4h | +134% → **+66%** (+57%) | 1,04 (0,96) | +171% / +0% / +77% (+328% / +0% / −11%) | +63% (+13%) | — | entra |
| §9 | MA Band WTI 4h | +27% → **+12%** (+5%) | 0,52 (0,35) | −9% / +24% / +14% (−21% / +40% / +8%) | +14% (+3%) | — | reprova: negativo no 1º terço; t ≤ 2 |
| §10 | Super trend V ETH 15m | +146% → **+118%** (+57%) | 1,44 (0,96) | +520% / +41% / +11% (+330% / +1% / −11%) | +10% (+13%) | — | passa, redundante |
| §11 | BEST ST ETH 1h | +122% → **+102%** (+57%) | 1,46 (0,96) | +278% / +57% / +48% (+330% / +1% / −11%) | +26% (+13%) | — | passa, redundante |
| §12 | VWAPStrategy ETH 30m | +175% → **+114%** (+57%) | 1,35 (0,96) | +398% / −11% / +115% (+330% / +1% / −11%) | +105% (+13%) | — | reprova: negativo no 2º terço |
| §13 | Chandelier ETH 30m | +153% → **+72%** (+57%) | 1,09 (0,96) | +162% / +61% / +19% (+330% / +1% / −11%) | +16% (+13%) | — | passa, redundante |
| §14 | THMA ETH 15m | +155% → **+116%** (+57%) | 1,39 (0,96) | +241% / +135% / +14% (+330% / +1% / −11%) | +23% (+13%) | — | passa, redundante |
| §15 | SM Pivot ETH 15m | +130% → **+93%** (+57%) | 1,24 (0,96) | +275% / +15% / +60% (+330% / +1% / −11%) | +28% (+13%) | — | passa, redundante |
| §16 | HULL+T3 ETH 1h | +115% → **+142%** (+57%) | 1,48 (0,96) | +767% / +41% / +11% (+330% / +1% / −11%) | +15% (+13%) | passa | entra |
| §17 | 5 EMA ETH 4h | +133% → **+70%** (+57%) | 1,06 (0,96) | +170% / +113% / +45% (+328% / +0% / −11%) | +27% (+13%) | — | entra |
| §18 | Wyckoff ETH 4h | +100% → **+65%** (+57%) | 1,20 (0,96) | +215% / +15% / +24% (+328% / +0% / −11%) | +30% (+13%) | — | entra |
| §19 | HA MACD BTC 1h | +94% → **+81%** (+44%) | 1,37 (0,91) | +123% / +120% / +17% (+129% / +15% / +13%) | +49% (+40%) | — | passa, redundante |
| §20 | HA PA WTI 4h | +41% → **+16%** (+5%) | 0,56 (0,35) | +4% / +6% / +42% (−21% / +40% / +8%) | +12% (+3%) | — | reprova: t ≤ 2; negativo sem funding |
| §21 | Golden Edge WTI 30m | +31% → **+18%** (+5%) | 0,58 (0,35) | −19% / +83% / +13% (−19% / +35% / +8%) | +10% (+3%) | passa | reprova: negativo no 1º terço; t ≤ 2 |
| §22 | Multi-MA ETH 15m | +152% → **+125%** (+57%) | 1,48 (0,96) | +363% / +18% / +105% (+330% / +1% / −11%) | +71% (+13%) | passa | passa, redundante |
| §23 | Multi-MA ETH 4h | +129% → **+87%** (+57%) | 1,23 (0,96) | +269% / +35% / +10% (+328% / +0% / −11%) | +11% (+13%) | — | passa, redundante |
| §24 | Multi-MA BTC 4h | +84% → **+61%** (+44%) | 1,16 (0,91) | +168% / +46% / +3% (+129% / +15% / +14%) | +26% (+40%) | — | entra |
| §25 | MACD+Stoch WTI 4h | +39% → **+11%** (+5%) | 0,47 (0,35) | −10% / +0% / +25% (−21% / +40% / +8%) | +31% (+3%) | — | reprova: negativo no 1º terço; t ≤ 2; negativo sem funding |
| §26 | TSI ST ETH 15m | +162% → **+84%** (+57%) | 1,16 (0,96) | +175% / +53% / +42% (+330% / +1% / −11%) | +35% (+13%) | — | passa, redundante |
| §27 | TSI ST ETH 30m | +165% → **+91%** (+57%) | 1,21 (0,96) | +185% / +69% / +41% (+330% / +1% / −11%) | +50% (+13%) | — | passa, redundante |
| §28 | VWAP X EMA ETH 30m | +138% → **+92%** (+57%) | 1,27 (0,96) | +230% / +52% / +40% (+330% / +1% / −11%) | +34% (+13%) | — | passa, redundante |

## Fichas das 30 de antes

Regra e configuração de cada uma, com o veredito da revisão. Os números antigos de resultado e robustez estão nos docs de lote e no histórico deste arquivo.

### 1. Trailing SL Strategy [QuantNomad] — ouro (XAU)

- **Script:** `n3vj0MIi` · lote 7 · [LOTE7_TV](LOTE7_TV.md) · `scripts/study_tvlote7.py`
- **Regra:** sempre no mercado. Trailing stop em `low − X` (comprado) ou `high + X` (vendido); rompido, inverte a posição.
- **Configuração:** X = **2%** do close (platô 1,75–2,5%), timeframe **30m a 1h** (15m e 4h também passam).
- **Na revisão:** passa, mas é redundante (corr 0,70).

### 2. Simple RSI-MA Algo — ETH 15m

- **Script:** `qSoZRbX7` · lote 12 · [LOTE12_TV](LOTE12_TV.md) · `scripts/study_tvlote12.py`
- **Regra:** SMA(ml) do RSI(rl); cruzar 50 para cima compra, para baixo vende. Sempre no mercado.
- **Configuração:** **15m**, RSI 10 ou 5, SMA 50, long e short.
- **Na revisão:** passa, mas é redundante (corr 0,50).

### 3. Pivot Point SuperTrend (LonesomeTheBlue) — ETH 15m

- **Script:** `DwdC6FT4` · lote 4 · [LOTE4_TV](LOTE4_TV.md)
- **Configuração:** 15m, pivot 5, fator 2, ATR 10, long e short.
- **Na revisão:** passa, mas é redundante (corr 0,68).

### 4. Seguidores de tendência no ETH — UT Bot v5, Ichimoku básico, Scalping System

- **Scripts:** `2wkJx7Ix`, `XZcsLIEW`, `YotdMm0M` · [LOTE13_TV](LOTE13_TV.md) · `scripts/study_tvlote13.py`
- **Configurações:** UT Bot 30m (a=5, ATR 11, HMA2 do open, long e short); Ichimoku 15m (20/60/120, deslocamento 60, long e short); Scalping 30m (SMA25 do low, sem EMA200, long e short).
- **Na revisão:** §4a: passa, mas é redundante (corr 0,56); §4b: reprova (negativo no 2º terço); §4c: entra na lista.

### 5. FTSMA — ETH 30m

- **Script:** `wffJotUo` · [LOTE17_TV](LOTE17_TV.md) · `scripts/study_tvlote17.py`
- **Regra:** EMA5 e EMA20 do close (mais um termo de Fourier de 64 barras que quase não muda nada) e EMA200. Comprado com EMA5 > EMA20 e close > EMA200; vendido no espelho; o sinal contrário inverte.
- **Configuração:** 30m, 5/20/200, long e short.
- **Na revisão:** passa, mas é redundante (corr 0,74).

### 6. ABCD Pattern — BTC 1h

- **Script:** `TWSr0hGH` · [LOTE19_TV](LOTE19_TV.md) · `scripts/study_tvlote19.py`
- **Regra:** zigzag de fractais Bill Williams; padrão ABCD com BC/AB entre 0,382 e 0,886 e CD/BC entre 1,13 e 2,618. D abaixo de C compra, acima vende; o padrão contrário inverte. Stop 4% e alvo 20% (5:1).
- **Na revisão:** reprova (t ≤ 2).

### 7. Follow Line — ETH 30m

- **Script:** `6lhyIPGA` · [LOTE20_TV](LOTE20_TV.md) · `scripts/study_tvlote20.py`
- **Regra:** EMA21 ± 1 desvio padrão (21) do close. Close acima da banda de cima: linha = low − ATR5, que só sobe; abaixo da de baixo: high + ATR5, que só desce. A virada da linha compra ou vende; o sinal contrário inverte. Calculado no próprio TF.
- **Configuração:** 30m, 21 / 1 desvio / ATR5, long e short.
- **Na revisão:** passa, mas é redundante (corr 0,72).

### 8. MA Consecutive Up/Down — ETH 4h

- **Script:** `7KXy9NNJ` · [LOTE21_TV](LOTE21_TV.md) · `scripts/study_tvlote21.py`
- **Regra:** 4 closes seguidos acima do anterior compra; 4 seguidos abaixo vende; o sinal contrário inverte (sempre posicionado). Média de comprimento 1, ou seja, o próprio close.
- **Na revisão:** entra na lista.

### 9. Moving Average Band — WTI 4h

- **Script:** `wwi02rpz` · [LOTE22_TV](LOTE22_TV.md) · `scripts/study_tvlote22.py`
- **Regra:** banda = SMA40 das máximas e SMA40 das mínimas. Close cruza acima da banda de cima compra; abaixo da de baixo vende; a entrada contrária inverte. Stop na banda oposta (fixado na entrada) e alvo de 3× o risco.
- **Na revisão:** reprova (negativo no 1º terço; t ≤ 2).

### 10. Super trend V — ETH 15m

- **Script:** `7g8MF7f7` · [LOTE23_TV](LOTE23_TV.md) · `scripts/study_tvlote23.py`
- **Regra:** VPT "sombra" (volume × corpo da vela, normalizado pelo desvio do range) suavizado por uma EMA de 336 barras no 15m (720/TF × 7); SuperTrend 10 × 1 em volta dele. Close cruza acima da linha com close acima da EMA da abertura compra; abaixo, vende. Comprado e vendido, o sinal contrário inverte.
- **Na revisão:** passa, mas é redundante (corr 0,77).

### 11. BEST Supertrend — ETH 1h

- **Script:** `6knHPR6c` · [LOTE24_TV](LOTE24_TV.md) · `scripts/study_tvlote24.py`
- **Regra:** SuperTrend diário (ATR3 × 3) do dia anterior como nível; regime de alta quando SMA7 > SMA20. Close ≥ linha diária no regime de alta compra; close ≤ linha no regime de baixa vende; sai no cruzamento contrário das médias. Comprado e vendido.
- **Na revisão:** passa, mas é redundante (corr 0,73).

### 12. VWAPStrategy — ETH 30m

- **Script:** `t1lk7Uvk` · [LOTE24_TV](LOTE24_TV.md) · `scripts/study_tvlote24.py`
- **Regra:** SMA3 do close cruza a VWAP diária (hlc3, âncora 00:00 UTC): acima compra, abaixo vende; sempre posicionado.
- **Na revisão:** reprova (negativo no 2º terço).

### 13. Chandelier Exit — ETH 30m

- **Script:** `yca6gmSk` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Chandelier Exit (ATR22 × 3, extremos do close): virada para cima compra, para baixo vende (inverte). Stop de 5% pelo close, alvo de 20% pela máxima e trailing de 5 pontos percentuais depois de +10%.
- **Na revisão:** passa, mas é redundante (corr 0,66).

### 14. Triangular Hull MA — ETH 15m

- **Script:** `gMeYb8Dp` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** THMA de 100 (WMA de 3·WMA(n/3) − WMA(n/2) − WMA(n)) cruzando ela mesma de 2 barras atrás; inverte.
- **Na revisão:** passa, mas é redundante (corr 0,78).

### 15. Smart Money Pivot — ETH 15m

- **Script:** `IMTwV7U8` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Pivô de topo 20/20: quando a máxima rompe o último pivô ainda ativo, compra; quando a mínima perde o último pivô de fundo, vende; inverte. Sem o stop de 1% e o alvo de 1,5% do script.
- **Na revisão:** passa, mas é redundante (corr 0,57).

### 16. Swing HULL + T3 — ETH 1h

- **Script:** `YgRqvCGx` · [LOTE25_TV](LOTE25_TV.md) · `scripts/study_tvlote25.py`
- **Regra:** Média de HMA100 e T3(100, 0,7): subindo compra, caindo vende (inverte); alvo 8% no long, alvo 3% e stop 6% no short.
- **Na revisão:** entra na lista.

### 17. 5 EMA — ETH 4h

- **Script:** `EaZHR7q6` · [LOTE26_TV](LOTE26_TV.md) · `scripts/study_tvlote26.py`
- **Regra:** A última barra toda abaixo da EMA5 marca a máxima de gatilho (toda acima marca a mínima); o rompimento entra se estiver fora; stop na menor mínima das 2 últimas barras (maior máxima no short), alvo 3R (o script usa 1,5R).
- **Na revisão:** entra na lista.

### 18. Wyckoff Range — ETH 4h

- **Script:** `vQSBf9rh` · [LOTE27_TV](LOTE27_TV.md) · `scripts/study_tvlote27.py`
- **Regra:** Close cruza acima da SMA32 junto com a mínima cruzando acima da SMA10 das mínimas compra; close abaixo da SMA35 com máxima abaixo da SMA20 das máximas vende; inverte; stop de 3% (o script usa 10%).
- **Na revisão:** entra na lista.

### 19. Heikin Ashi MACD — BTC 1h

- **Script:** `YfPnKE22` · [LOTE28_TV](LOTE28_TV.md) · `scripts/study_tvlote28.py`
- **Regra:** MACD de DEMAs feitas com SMA (12, 25, sinal SMA15) sobre o close Heikin Ashi: delta cruza 0 para cima compra, para baixo vende; inverte; alvo 10% e stop 3%.
- **Na revisão:** passa, mas é redundante (corr 0,56).

### 20. HA Price Action com velas comuns — WTI 4h

- **Script:** `FEJvYRkw` · [LOTE28_TV](LOTE28_TV.md) · `scripts/study_tvlote28.py`
- **Regra:** Close acima da máxima anterior, vela de alta e máxima anterior acima da de 2 barras atrás compra; vela de baixa fechando abaixo da mínima anterior vende; inverte. O original usa velas Heikin Ashi e só compra; aqui são velas comuns e os dois lados.
- **Na revisão:** reprova (t ≤ 2; negativo sem funding).

### 21. PTS Golden Edge — WTI 30m

- **Script:** `SD5jYZuC` · [LOTE29_TV](LOTE29_TV.md) · `scripts/study_tvlote29.py`
- **Regra:** EMA9 cruza a EMA50 para cima com RSI12 > 56, HMA66 subindo e faixa de 14 barras > 0,5 ATR14 compra; espelho com RSI < 45 vende; inverte (o script usa EMA 3/33).
- **Na revisão:** reprova (negativo no 1º terço; t ≤ 2).

### 22. Multi-MA — ETH 15m

- **Script:** `34lAHcyo` · [LOTE30_TV](LOTE30_TV.md) · `scripts/study_tvlote30.py`
- **Regra:** VWMA, RMA, SMA, WMA e EMA do mesmo período todas subindo compra, todas caindo vende; inverte. Período 150 (o padrão é 66).
- **Na revisão:** passa, mas é redundante (corr 0,77).

### 23. Multi-MA — ETH 4h

- **Script:** `34lAHcyo` · [LOTE30_TV](LOTE30_TV.md) · `scripts/study_tvlote30.py`
- **Regra:** VWMA, RMA, SMA, WMA e EMA do mesmo período todas subindo compra, todas caindo vende; inverte. Período 66 (o padrão do script).
- **Na revisão:** passa, mas é redundante (corr 0,61).

### 24. Multi-MA — BTC 4h

- **Script:** `34lAHcyo` · [LOTE30_TV](LOTE30_TV.md) · `scripts/study_tvlote30.py`
- **Regra:** VWMA, RMA, SMA, WMA e EMA do mesmo período todas subindo compra, todas caindo vende; inverte. Período 150 (o padrão é 66).
- **Na revisão:** entra na lista.

### 25. MACD + Stochastic — WTI 4h

- **Script:** `sqDK1npx` · [LOTE31_TV](LOTE31_TV.md) · `scripts/study_tvlote31.py`
- **Regra:** EMA8−EMA24 subindo com Stoch(14) D<25 subindo compra; EMA8−EMA24 caindo com D>75 caindo vende; inverte. Stoch 14 (o padrão é 7).
- **Na revisão:** reprova (negativo no 1º terço; t ≤ 2; negativo sem funding).

### 26. TSI w SuperTrend — ETH 15m

- **Script:** `lncoD9BX` · [LOTE32_TV](LOTE32_TV.md) · `scripts/study_tvlote32.py`
- **Regra:** TSI = correlação de 64 barras entre close e tempo; SuperTrend(10, 3) sobre velas do TSI: direção de alta com TSI>−0,241 compra, de baixa com TSI<0,241 vende; as condições opostas fecham. Período 64 (o padrão).
- **Na revisão:** passa, mas é redundante (corr 0,85).

### 27. TSI w SuperTrend — ETH 30m

- **Script:** `lncoD9BX` · [LOTE32_TV](LOTE32_TV.md) · `scripts/study_tvlote32.py`
- **Regra:** a mesma da §26 com período 32 (o padrão é 64).
- **Na revisão:** passa, mas é redundante (corr 0,83).

### 28. VWAP X EMA — ETH 30m

- **Script:** `DP1S7S5j` · [LOTE33_TV](LOTE33_TV.md) · `scripts/study_tvlote33.py`
- **Regra:** close acima da VWAP diária, da EMA50 e da EMA200 compra; abaixo da VWAP e da EMA50 vende; inverte. EMA50 (o padrão).
- **Na revisão:** passa, mas é redundante (corr 0,64).

## Resgatadas pela métrica corrigida (lotes 3 a 33, fora da robustez)

Células que a conta antiga descartou antes da robustez. Pré-filtro nas grades salvas só com o que não depende da curva de equity (t > 2 e média líquida por trade > 0): 3235 células. Período todo recalculado com o CAGR composto: 458 passam em CAGR > 0, Sharpe ≥ B&H e t > 2; 254 passam no critério novo inteiro (terços, spread 4×, sem funding); **60 entram** com |corr| < 0,5 contra as 34 acima e entre si. Fonte: `scripts/study_resgate.py` → `results/study_resgate.txt` e `.csv`. Excluídas: células com lookahead (`peek` do lote 3), 265 configurações que o main atual não reproduz e 18 do lote 7 (HMA) que quebram ao fatiar.

Cautela maior que nas 34: cada uma é a melhor de uma grade com milhares de células, então parte delas passa por acaso. Lotes 3, 5, 6 e 8 a 11 só têm grade no ouro.

Por ativo: ETH 27, BTC 17, XAU 7, US100 6, WTI 3.

| # | Célula | CAGR (B&H) | Sharpe (B&H) | DD | t | Terços | Spread 4× | Sem funding | Corr máx (com) |
| ---: | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| R1 | L20 cam ETH 1h sl0.5% tp1% ambos | +25% (+57%) | 1,87 (0,96) | −14% | 4,92 | +29% / +31% / +16% | +15% | +25% | 0,19 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R2 | L20 cam ETH 15min sl1% tp2% ambos | +50% (+57%) | 1,76 (0,96) | −27% | 4,48 | +125% / +19% / +26% | +36% | +50% | 0,44 (L20 cam ETH 1h sl0.5% tp1% ambos) |
| R3 | L23 tema BTC 4h adx43 long | +35% (+44%) | 1,69 (0,91) | −12% | 3,87 | +54% / +40% / +14% | +34% | +37% | 0,47 (L22 force BTC 4h {'fast': 5, 'slow': 50, 'short_ok': False}) |
| R4 | L31 lch ETH 15min v2% hma400 | +35% (+57%) | 1,65 (0,96) | −27% | 7,71 | +84% / +17% / +14% | +33% | +35% | 0,25 (§4c Scalping ETH 30m) |
| R5 | L26 pprs ETH 15min pv6/3 ambos | +159% (+57%) | 1,64 (0,96) | −62% | 4,80 | +197% / +13% / +409% | +78% | +160% | 0,47 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R6 | L15 sbs ETH 15min sl1.00% sessao ambos | +72% (+57%) | 1,61 (0,96) | −40% | 3,68 | +136% / +50% / +44% | +12% | +72% | 0,36 (L15 sbs ETH 30min {'sl': 0.02, 'session': False}) |
| R7 | L24 dcf ETH 15min semtp long | +76% (+57%) | 1,58 (0,96) | −38% | 3,98 | +202% / +14% / +57% | +2% | +82% | 0,46 (L24 best ETH 1h {'short_ok': False}) |
| R8 | L31 lch BTC 15min v2% hma200 | +18% (+44%) | 1,56 (0,91) | −14% | 6,87 | +40% / +16% / +2% | +18% | +18% | 0,47 (L31 lch ETH 15min v2% hma400) |
| R9 | L20 cam BTC 15min sl1% tp2% ambos | +42% (+44%) | 1,56 (0,91) | −25% | 3,05 | +65% / +33% / +30% | +30% | +42% | 0,31 (L20 cam ETH 15min sl1% tp2% ambos) |
| R10 | L21 hulk BTC 15min thr0.1 adx33 tp1.35% sl1.1% ambos | +22% (+44%) | 1,48 (0,91) | −12% | 3,19 | +29% / +24% / +14% | +17% | +22% | 0,16 (§16 HULL+T3 ETH 1h) |
| R11 | L15 sbs ETH 4h sl2.00% 24h ambos | +60% (+57%) | 1,39 (0,96) | −41% | 2,67 | +103% / +50% / +27% | +48% | +60% | 0,38 (§16 HULL+T3 ETH 1h) |
| R12 | L24 d3 ETH 1D x1 ambos | +109% (+56%) | 1,37 (0,96) | −64% | 3,07 | +154% / +36% / +117% | +108% | +110% | 0,46 (L24 best ETH 1h {'short_ok': False}) |
| R13 | L31 vip ETH 30min tp1% stop no close | +13% (+57%) | 1,32 (0,96) | −15% | 2,47 | +23% / +12% / +5% | +11% | +14% | 0,19 (L24 dcf ETH 15min semtp long) |
| R14 | L21 hulk ETH 15min thr0.3 adx33 tp1.35% sl1.1% ambos | +15% (+57%) | 1,31 (0,96) | −16% | 2,40 | +27% / +5% / +12% | +12% | +15% | 0,21 (L21 hulk BTC 15min thr0.1 adx33 tp1.35% sl1.1% ambos) |
| R15 | L14 cs ETH 4h e60 tp/sl default long | +60% (+57%) | 1,31 (0,96) | −64% | 2,53 | +312% / +52% / +6% | +60% | +63% | 0,42 (L24 best ETH 1h {'short_ok': False}) |
| R16 | L24 tq BTC 4h p1% ambos | +20% (+44%) | 1,29 (0,91) | −18% | 4,91 | +11% / +21% / +32% | +19% | +20% | 0,20 (L20 cam BTC 15min sl1% tp2% ambos) |
| R17 | L16 pmax BTC 1h sl1% tp35% sofiltro0 ambos | +45% (+44%) | 1,28 (0,91) | −29% | 3,54 | +39% / +66% / +22% | +42% | +45% | 0,42 (L31 cmb BTC 1h) |
| R18 | L12b zig ETH 15min lb6 dmi1 cond long | +35% (+57%) | 1,26 (0,96) | −22% | 2,95 | +38% / +27% / +42% | +30% | +37% | 0,36 (L24 dcf ETH 15min semtp long) |
| R19 | L21 lube BTC 30min 500 tl-0.1 ambos | +29% (+44%) | 1,26 (0,91) | −28% | 3,77 | +53% / +12% / +24% | +27% | +29% | 0,27 (L16 pmax BTC 1h sl1% tp35% sofiltro0 ambos) |
| R20 | L20 kelt ETH 4h 81 2.5 tp6% sl2% tend | +18% (+57%) | 1,26 (0,96) | −11% | 3,20 | +22% / +20% / +11% | +17% | +18% | 0,24 (L24 best ETH 1h {'short_ok': False}) |
| R21 | L19 3ema US100 1h tp0 sl2 | +12% (+20%) | 1,22 (0,93) | −14% | 2,27 | +17% / +13% / +5% | +9% | +13% | 0,12 (L24 dcf ETH 15min semtp long) |
| R22 | L12b zig ETH 1h lb6 dmi1 cond long | +41% (+57%) | 1,20 (0,96) | −27% | 2,51 | +100% / +7% / +31% | +38% | +44% | 0,42 (L24 best ETH 1h {'short_ok': False}) |
| R23 | L31 lch ETH 1h v4% hma200 | +18% (+57%) | 1,20 (0,96) | −18% | 4,30 | +30% / +22% / +4% | +18% | +18% | -0,10 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R24 | L15 tmfs ETH 30min sw20 sl8atr tp1% ambos | +31% (+57%) | 1,20 (0,96) | −31% | 2,58 | +54% / +16% / +26% | +18% | +31% | 0,30 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R25 | L17 bz ETH 1h bb20 3 semlatest ambos | +81% (+57%) | 1,19 (0,96) | −69% | 2,82 | +314% / +13% / +48% | +81% | +81% | 0,35 (L24 d3 ETH 1D x1 ambos) |
| R26 | L31 seq ETH 1D rr1 long | +39% (+56%) | 1,18 (0,96) | −34% | 2,90 | +86% / +6% / +36% | +39% | +41% | 0,41 (L24 best ETH 1h {'short_ok': False}) |
| R27 | L24 tq BTC 1D p1% long | +15% (+44%) | 1,18 (0,91) | −12% | 2,82 | +14% / +22% / +8% | +15% | +15% | 0,31 (L23 tema BTC 4h adx43 long) |
| R28 | L20 cam US100 15min sl1% tp2% ambos | +17% (+20%) | 1,16 (0,93) | −25% | 3,80 | +20% / +28% / +4% | +7% | +18% | 0,35 (L19 3ema US100 1h tp0 sl2) |
| R29 | L33 vxe BTC 4h ema20 ambos | +56% (+44%) | 1,13 (0,91) | −47% | 3,87 | +207% / +10% / +11% | +50% | +53% | 0,50 (§24 Multi-MA BTC 4h) |
| R30 | L18 osb ETH 30min m0.25 sl2.00% ambos | +47% (+57%) | 1,13 (0,96) | −50% | 3,12 | +165% / +15% / +4% | +39% | +47% | 0,30 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R31 | L15 sbs BTC 30min sl2.00% 24h ambos | +56% (+44%) | 1,13 (0,91) | −50% | 4,09 | +77% / +27% / +67% | +14% | +56% | 0,44 (L15 sbs ETH 30min {'sl': 0.02, 'session': False}) |
| R32 | L24 tq ETH 1h p3% ambos | +51% (+57%) | 1,13 (0,96) | −49% | 2,76 | +119% / +12% / +44% | +47% | +51% | 0,34 (§16 HULL+T3 ETH 1h) |
| R33 | L32 prv US100 15min f2.618 long | +17% (+20%) | 1,11 (0,93) | −23% | 2,30 | +8% / +23% / +22% | +5% | +20% | 0,47 (L19 3ema US100 1h tp0 sl2) |
| R34 | L22 apsar BTC 4h n1 0.02/0.2 ambos | +60% (+44%) | 1,11 (0,91) | −59% | 2,26 | +89% / +87% / +27% | +58% | +61% | 0,48 (L33 vxe BTC 4h ema20 ambos) |
| R35 | L20 kelt XAU 1D 81 2.5 tp6% sl2% tend | +6% (+13%) | 1,11 (0,82) | −7% | 2,90 | +3% / +4% / +9% | +5% | +7% | 0,17 (L7 tsl XAU 4h {'val': 2.0}) |
| R36 | L20 atrgod XAU 4h sl4.5 rr1.5 semfiltros ambos | +11% (+13%) | 1,11 (0,82) | −13% | 2,72 | +6% / +2% / +27% | +10% | +13% | 0,25 (L7 tsl XAU 4h {'val': 2.0}) |
| R37 | L15 sbs US100 4h sl1.00% sessao ambos | +12% (+20%) | 1,11 (0,93) | −14% | 4,02 | +9% / +15% / +11% | +5% | +12% | 0,33 (L20 cam US100 15min sl1% tp2% ambos) |
| R38 | L16 qqe ETH 1h XZ f5 dfil long | +33% (+57%) | 1,09 (0,96) | −27% | 2,03 | +58% / +21% / +23% | +30% | +35% | 0,48 (L24 best ETH 1h {'short_ok': False}) |
| R39 | L22 force BTC 4h 3/20 ambos | +57% (+44%) | 1,08 (0,91) | −58% | 2,41 | +115% / +53% / +8% | +55% | +56% | 0,47 (L33 vxe BTC 4h ema20 ambos) |
| R40 | L23 twin ETH 1h atr t17 sltp ambos | +42% (+57%) | 1,08 (0,96) | −41% | 4,35 | +121% / +7% / +22% | +33% | +43% | 0,32 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R41 | L13 sqz BTC 4h bb14 kc16 ambos | +31% (+44%) | 1,04 (0,91) | −40% | 2,85 | +59% / +17% / +17% | +28% | +31% | 0,47 (L33 vxe BTC 4h ema20 ambos) |
| R42 | L14 fm BTC 15min bb20 2.0 sl2.0% tp2.0% ambos | +33% (+44%) | 1,03 (0,91) | −42% | 2,07 | +56% / +5% / +47% | +18% | +33% | 0,18 (L21 hulk BTC 15min thr0.1 adx33 tp1.35% sl1.1% ambos) |
| R43 | L15 tmfs ETH 1h sw8 sl8atr tp1% ambos | +29% (+57%) | 1,02 (0,96) | −30% | 2,67 | +52% / +11% / +25% | +15% | +29% | 0,38 (L15 tmfs ETH 30min sw20 sl8atr tp1% ambos) |
| R44 | L24 stb US100 1h tp3% ambos | +18% (+20%) | 1,00 (0,93) | −34% | 3,20 | +10% / +32% / +13% | +6% | +18% | 0,48 (L20 cam US100 15min sl1% tp2% ambos) |
| R45 | L24 sott ETH 15min s250 p0.618 ambos | +61% (+57%) | 1,00 (0,96) | −62% | 2,68 | +78% / +31% / +70% | +50% | +61% | 0,48 (L12 rsima ETH 15min {'rl': 5, 'ml': 50}) |
| R46 | L21 bbb ETH 4h bb40 vol sl2% tp9% ambos | +33% (+57%) | 1,00 (0,96) | −42% | 2,55 | +44% / +17% / +31% | +31% | +34% | 0,40 (L31 cmb ETH 4h) |
| R47 | L13 sqz BTC 1D bb20 kc20 long | +20% (+44%) | 0,99 (0,91) | −29% | 2,41 | +42% / +19% / +2% | +20% | +21% | 0,49 (L22 force BTC 4h {'fast': 5, 'slow': 50, 'short_ok': False}) |
| R48 | L19 abcd BTC 4h sl2.0% rr2 ambos | +21% (+44%) | 0,98 (0,91) | −25% | 2,91 | +50% / +14% / +5% | +19% | +21% | 0,18 (L20 ds BTC 30min {'f': 8, 's': 72}) |
| R49 | L16 qqe ETH 15min XZ f5 dfil ambos | +38% (+57%) | 0,97 (0,96) | −37% | 2,82 | +52% / +29% / +32% | +12% | +38% | 0,42 (L26 pprs ETH 15min pv6/3 ambos) |
| R50 | L15 sbs ETH 1h sl1.00% sessao ambos | +25% (+57%) | 0,97 (0,96) | −46% | 3,79 | +66% / +2% / +15% | +6% | +25% | 0,34 (L15 sbs ETH 15min sl1.00% sessao ambos) |
| R51 | L19 cipher US100 4h wt tp4 sl2 ambos | +3% (+20%) | 0,96 (0,93) | −3% | 3,41 | +2% / +2% / +4% | +2% | +3% | 0,16 (L24 tq BTC 1D p1% long) |
| R52 | L24 stb XAU 4h tp3% ambos | +11% (+13%) | 0,94 (0,82) | −20% | 3,96 | +10% / +2% / +26% | +9% | +10% | 0,45 (L7 tsl XAU 4h {'val': 2.0}) |
| R53 | L15 tmfs BTC 30min sw20 sl8atr tp3% ambos | +27% (+44%) | 0,91 (0,91) | −61% | 2,53 | +55% / +0% / +32% | +16% | +27% | 0,44 (L15 sbs BTC 30min sl2.00% 24h ambos) |
| R54 | L28 hvc XAU 1h h100 ambos | +14% (+13%) | 0,87 (0,82) | −23% | 3,22 | +11% / +7% / +26% | +8% | +15% | 0,42 (L7 tsl XAU 4h {'val': 2.0}) |
| R55 | L20 atrgod XAU 4h sl2.0 rr2.0 filtros ambos | +3% (+13%) | 0,85 (0,82) | −4% | 3,27 | +3% / +1% / +3% | +3% | +2% | 0,31 (L20 atrgod XAU 4h sl4.5 rr1.5 semfiltros ambos) |
| R56 | L30 sich XAU 4h rr2 long | +8% (+13%) | 0,84 (0,82) | −15% | 2,30 | +7% / +5% / +12% | +8% | +12% | 0,36 (L20 atrgod XAU 4h sl4.5 rr1.5 semfiltros ambos) |
| R57 | L33 pst XAU 1h af0.01 ambos | +13% (+13%) | 0,84 (0,82) | −19% | 2,22 | +3% / +7% / +38% | +5% | +13% | 0,47 (L14 hap XAU 1h {'start': 0.01, 'inc': 0.01, 'mx': 0.1}) |
| R58 | L27 obv WTI 1h l50 ambos | +23% (+5%) | 0,70 (0,35) | −53% | 2,20 | +47% / +13% / +12% | +10% | +23% | 0,29 (L25 sta WTI 4h {'ln': 14}) |
| R59 | L22 apsar WTI 30min n1 0.01/0.1 ambos | +22% (+5%) | 0,67 (0,35) | −69% | 3,09 | +19% / +7% / +38% | +15% | +27% | 0,27 (L25 sta WTI 4h {'ln': 14}) |
| R60 | L31 seq WTI 1D rr1.5 ambos | +11% (+6%) | 0,62 (0,35) | −34% | 2,37 | +7% / +3% / +24% | +11% | +16% | 0,16 (L29 bot WTI 1D {'k': 0.02}) |

## Pendências comuns

- Medir o spread real do ETH e o histórico de funding de cada mercado na Lighter; refazer as células com o funding hora a hora.
- Testar o processo: rodar a triagem só com dados até 17/05/2023, aprovar por este critério e medir o que as aprovadas fizeram depois.
- Montar a carteira de paper a partir desta lista. `study_aprovadas_corr.py` e `study_carteira*.py` ainda usam as 30 de antes.
- Paper/forward test antes de qualquer uso real.
