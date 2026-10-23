# Lote 23 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote23.py` (grade) e `scripts/study_tvlote23_rob.py` (robustez). Resultados: `results/study_tvlote23_{ativo}.txt`, `_grid.csv` e `results/study_tvlote23_rob_{ativo}.txt`.

**Puladas na ordem da lista (19):**
- **Olha o futuro:** `8JML9Cqd` (`security` em Pine v2).
- **Velas Renko via `security`, irreal:** renko intraday (`j0iaMxsl`) e Renko Emulator OCC (`CmZUAjHp`).
- **Templates, exemplos ou ferramentas:** Two Take Profit (`OZnjwvZv`, exemplo de 2 alvos em ticks), Custom Screener (`QKgb0Fud`), Catch the Big Fish (`ZkyK1BVD`, sem ordens), Rocket Grid (`lm2BJL4V`, grid) e Zendog DCA (`9NXf1Bqb`).
- **Página 404:** `futPZepe`.
- **Duplicadas:** TradersAI UTBot (`QDxGi5Ux`, o UT Bot do lote 13) e Strategy Follow Line (`NCdNYR6I`, a Follow Line do lote 20).
- **Piramidação ou complexas demais para reproduzir com fidelidade:** Turtle System (`cOv24513`, 5 unidades com L1/L2), Simple and Profitable Scalping (`x4za4NFZ`, 394 linhas com filtro de outro tempo), Dual MA Ribbons (`KpbbCOzp`, 599 linhas), Divergence IQ (`hgcTVYeX`, 1.090 linhas), Vegas Tunnel (`Grfdbh8A`, 4 entradas piramidadas), `6w9Jchj6` (622 linhas) e 4All V3 (`SMQcpefL`, 5 scalps piramidados).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 174 | Twin Range Filter Algo v.3 | `ZsiaNicR` | range filter duplo (27×1,6 e 55×2); filtro SMA32 do TR < RMA64; stop pela mínima de 10, alvo 5 ATR10, saída por tempo em 17 barras (ticks ignorados) |
| 175 | BBTrend w SuperTrend decision | `7C1kIEOn` | BBTrend (BB20 vs BB50) com SuperTrend 10×7 sobre ele; padrão só long |
| 176 | 3 EMA + RSI with Trail Stop | `mgD7xBuw` | EMA10 × 20 acima da EMA100; sai com RSI > 70 ou após 24 barras no lucro; stop 5% (trailing em pontos omitido) |
| 177 | HIGHER HIGH LOWER LOW | `JWsBrWBu` | close rompe a máxima de 41 que está acima da de 10; inverte |
| 178 | NR7 + Inside Day (ChartArt) | `Dln4aFaM` | long-only; NR7 + inside bar de alta com SMA14 subindo; sai na próxima vela de alta |
| 179 | Maximized Scalping On Trend (Coinrule) | `XAiEh7nb` | long-only; close cruza abaixo da SMA9 com SMA50 > SMA100 e RSI > 50; sai com RSI > 70 ou < 30 |
| 180 | [UL] QQE Cross v1.1 | `nkka4EfU` | RSI6 suavizado acima de 60 (abaixo de 40) com EMA20 subindo e close > SMA50; sai quando a direção da EMA20 muda (trailing em pontos omitido) |
| 181 | DEMA ATR [PrimeAutomation] | `rqRd3f62` | DEMA75 presa em ±1,2 ATR20, cruzamento com ela mesma 2 barras atrás; os 3 alvos parciais viraram um alvo único opcional |
| 182 | MA Bollinger Bands + RSI | `2MMNHl97` | reentrada na BB200 com RSI6 cruzando 50 em 10 barras; filtro de volatilidade; trailing mínima de 2 − 9 ATR14 |
| 183 | TradeIQ Crazy Scalping (Kaspricci) | `R7OSA2ar` | divergência do TMO + modo do filtro AMA(50) + corpo das velas filtradas crescendo; stop na mínima de 10 |
| 184 | Triple EMA Trend (ADX + ATR) | `vzXlqRCT` | ADX > 43 e EMAs 30/46/80 alinhadas; stop 1,8 ATR, alvo 3,3 ATR; trade "virtual" do script reproduzido |
| 185 | MA 10/20 Crossover | `2cbpO8lO` | SMA10 × SMA20; inverte |
| 186 | Crypto ZigZag RSI 15min | `LhpfQMtP` | long-only; zigzag de 1% sobre os closes dos cruzamentos do RSI5 em 25/75 |
| 187 | Combo 123 Reversal & SMI | `NudssmJx` | 123 Reversal e Smart Money Index (diário anterior) concordando; discordância zera |
| 188 | Buying Dip with TP/SL (racer8) | `AHxkEMXm` | long-only; close abaixo da mínima de 7; alvo e stop 2 × SMA10 do TR |
| 189 | Super trend V | `7g8MF7f7` | SuperTrend 10×1 em volta da EMA (720/TF × 7 barras) de um VPT com volume; filtro close vs EMA da abertura; padrão só long |
| 190 | RSI Strategy [PrimeAutomation] | `RiQzLLoh` | RSI40 cruza 60/35 (sem posição); trailing 4 ATR200 pela mínima; alvo 7 ATR200 |
| 191 | Trend Trader Strategy with MACD | `dUNRiEBG` | linha do Trend Trader (21, 3 × WMA do TR); compra com histograma > 0; inverte |
| 192 | EVWMA VWAP Cross [QuantNomad] | `QPIGo8hs` | VWAP diária (UTC) cruza a EVWMA30; inverte |
| 193 | VWAP Momentum Pullback (JS-TechTrading) | `uhdaobby` | long-only; RSI ≤ 40 nas últimas 10 barras e SMA7 cruza acima da VWAP; stop 3%, alvo 7% |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Twin Range Filter | BTC | 65 | 52 | 5 | 1 | +58.2% (4h atr t0 semsltp ambos, 367 tr) | +43.7% |
| Twin Range Filter | ETH | 66 | 56 | 14 | 3 | +106.1% (4h atr t0 semsltp ambos, 359 tr) | +56.6% |
| Twin Range Filter | US100 | 66 | 43 | 12 | 0 | +13.7% (1D sematr t0 sltp ambos, 157 tr) | +20.2% |
| Twin Range Filter | WTI | 65 | 18 | 0 | 14 | +21.6% (1D atr t0 semsltp ambos, 62 tr) | +5.7% |
| Twin Range Filter | XAU | 65 | 35 | 3 | 0 | +8.5% (4h sematr t17 semsltp ambos, 725 tr) | +13.4% |
| BBTrend + ST | BTC | 20 | 13 | 0 | 0 | +27.7% (4h f3 long, 433 tr) | +43.7% |
| BBTrend + ST | ETH | 20 | 13 | 2 | 2 | +118.5% (30min f3 ambos, 6888 tr) | +56.8% |
| BBTrend + ST | US100 | 20 | 13 | 1 | 0 | +13.4% (1D f7 long, 44 tr) | +20.2% |
| BBTrend + ST | WTI | 20 | 7 | 1 | 5 | +19.1% (30min f7 ambos, 4668 tr) | +5.4% |
| BBTrend + ST | XAU | 20 | 12 | 0 | 0 | +9.8% (4h f3 ambos, 714 tr) | +13.4% |
| 3 EMA + RSI | BTC | 45 | 30 | 3 | 0 | +19.1% (30min sl0% x0 ambos, 1006 tr) | +43.9% |
| 3 EMA + RSI | ETH | 45 | 19 | 0 | 0 | +17.7% (4h sl0% x0 ambos, 131 tr) | +56.6% |
| 3 EMA + RSI | US100 | 45 | 21 | 0 | 0 | +4.2% (4h sl0% x0 long, 74 tr) | +20.3% |
| 3 EMA + RSI | WTI | 43 | 5 | 0 | 1 | +5.4% (4h sl5% x24 ambos, 166 tr) | +5.4% |
| 3 EMA + RSI | XAU | 45 | 14 | 0 | 0 | +3.3% (4h sl5% x24 ambos, 109 tr) | +13.4% |
| HH/LL 41 | BTC | 17 | 15 | 1 | 2 | +62.3% (4h 100 ambos, 54 tr) | +43.7% |
| HH/LL 41 | ETH | 17 | 16 | 0 | 0 | +43.3% (30min 100 ambos, 426 tr) | +56.8% |
| HH/LL 41 | US100 | 17 | 12 | 0 | 0 | +9.1% (1h 41 long, 166 tr) | +20.3% |
| HH/LL 41 | WTI | 17 | 2 | 0 | 1 | +8.6% (4h 100 ambos, 48 tr) | +5.4% |
| HH/LL 41 | XAU | 17 | 15 | 0 | 0 | +7.6% (30min 41 ambos, 542 tr) | +13.4% |
| NR7 + Inside | BTC | 10 | 5 | 0 | 0 | +5.0% (4h sma14, 294 tr) | +43.7% |
| NR7 + Inside | ETH | 10 | 6 | 0 | 0 | +5.8% (1h semfiltro, 1924 tr) | +56.8% |
| NR7 + Inside | US100 | 9 | 2 | 1 | 0 | +0.8% (1h sma14, 750 tr) | +20.3% |
| NR7 + Inside | WTI | 10 | 1 | 0 | 0 | -3.6% (30min sma14, 1585 tr) | +5.4% |
| NR7 + Inside | XAU | 10 | 2 | 0 | 0 | +0.5% (1D sma14, 45 tr) | +13.4% |
| Coinrule Scalping | BTC | 10 | 10 | 0 | 0 | +39.8% (30min 80/20, 383 tr) | +43.9% |
| Coinrule Scalping | ETH | 10 | 10 | 0 | 0 | +52.5% (30min 80/20, 393 tr) | +56.8% |
| Coinrule Scalping | US100 | 9 | 9 | 0 | 0 | +14.4% (4h 80/20, 63 tr) | +20.3% |
| Coinrule Scalping | WTI | 9 | 0 | 0 | 0 | -10.9% (4h 70/30, 192 tr) | +5.4% |
| Coinrule Scalping | XAU | 10 | 7 | 0 | 0 | +2.7% (1D 70/30, 33 tr) | +13.4% |
| UL QQE Cross | BTC | 40 | 29 | 1 | 2 | +55.3% (1D thr5 filtro ambos, 137 tr) | +43.8% |
| UL QQE Cross | ETH | 40 | 38 | 9 | 6 | +79.7% (4h thr5 semfiltro ambos, 1170 tr) | +56.6% |
| UL QQE Cross | US100 | 40 | 32 | 6 | 0 | +8.9% (1D thr10 semfiltro long, 67 tr) | +20.2% |
| UL QQE Cross | WTI | 40 | 12 | 0 | 3 | +9.5% (1h thr10 filtro ambos, 2899 tr) | +5.4% |
| UL QQE Cross | XAU | 40 | 24 | 4 | 0 | +7.2% (4h thr10 semfiltro ambos, 717 tr) | +13.4% |
| DEMA ATR | BTC | 19 | 16 | 0 | 0 | +29.9% (30min semtp ambos, 860 tr) | +43.9% |
| DEMA ATR | ETH | 20 | 19 | 0 | 2 | +66.6% (30min semtp ambos, 860 tr) | +56.8% |
| DEMA ATR | US100 | 19 | 17 | 2 | 0 | +16.5% (4h tp6 ambos, 157 tr) | +20.3% |
| DEMA ATR | WTI | 20 | 2 | 0 | 1 | +5.6% (4h semtp ambos, 116 tr) | +5.4% |
| DEMA ATR | XAU | 19 | 14 | 1 | 0 | +7.2% (1h semtp ambos, 341 tr) | +13.4% |
| MA BB + RSI | BTC | 32 | 19 | 0 | 0 | +40.4% (15min a9 semvol long, 317 tr) | +43.8% |
| MA BB + RSI | ETH | 31 | 20 | 0 | 0 | +40.4% (15min a9 semvol long, 298 tr) | +56.8% |
| MA BB + RSI | US100 | 32 | 21 | 0 | 0 | +2.4% (30min a9 semvol long, 103 tr) | +20.3% |
| MA BB + RSI | WTI | 32 | 7 | 0 | 2 | +8.6% (15min a9 vol ambos, 446 tr) | +5.4% |
| MA BB + RSI | XAU | 28 | 4 | 0 | 0 | +3.3% (1h a9 semvol long, 56 tr) | +13.4% |
| Crazy Scalping | BTC | 18 | 8 | 0 | 0 | +6.6% (30min sl30 ambos, 575 tr) | +43.9% |
| Crazy Scalping | ETH | 18 | 14 | 2 | 0 | +31.8% (4h sl30 ambos, 75 tr) | +56.6% |
| Crazy Scalping | US100 | 18 | 8 | 4 | 0 | +5.1% (30min sl30 ambos, 488 tr) | +20.3% |
| Crazy Scalping | WTI | 18 | 11 | 1 | 3 | +11.4% (1h sl30 ambos, 373 tr) | +5.4% |
| Crazy Scalping | XAU | 18 | 6 | 0 | 0 | +0.5% (4h sl10 ambos, 77 tr) | +13.4% |
| Triple EMA ADX | BTC | 20 | 19 | 6 | 2 | +55.1% (4h adx43 ambos, 156 tr) | +43.7% |
| Triple EMA ADX | ETH | 20 | 19 | 4 | 2 | +78.9% (15min adx43 ambos, 2149 tr) | +56.8% |
| Triple EMA ADX | US100 | 18 | 10 | 1 | 0 | +4.2% (4h adx25 ambos, 458 tr) | +20.3% |
| Triple EMA ADX | WTI | 20 | 6 | 1 | 2 | +17.3% (1h adx25 ambos, 1748 tr) | +5.4% |
| Triple EMA ADX | XAU | 20 | 9 | 0 | 0 | +2.2% (1h adx25 ambos, 1341 tr) | +13.4% |
| MA 10/20 | BTC | 29 | 26 | 2 | 1 | +51.2% (1h 10/20 ambos, 3441 tr) | +43.9% |
| MA 10/20 | ETH | 29 | 28 | 8 | 11 | +114.7% (1h 10/20 ambos, 3323 tr) | +56.8% |
| MA 10/20 | US100 | 28 | 20 | 1 | 0 | +10.9% (30min 20/50 long, 927 tr) | +20.3% |
| MA 10/20 | WTI | 29 | 6 | 0 | 4 | +17.3% (30min 20/50 ambos, 2502 tr) | +5.4% |
| MA 10/20 | XAU | 28 | 20 | 2 | 2 | +13.9% (1h 10/20 ambos, 2464 tr) | +13.4% |
| ZigZag RSI | BTC | 18 | 17 | 0 | 1 | +51.3% (15min r14 30/70 zz1, 161 tr) | +43.8% |
| ZigZag RSI | ETH | 16 | 16 | 0 | 1 | +58.2% (15min r5 25/75 zz3, 274 tr) | +56.8% |
| ZigZag RSI | US100 | 14 | 14 | 0 | 0 | +13.2% (15min r14 30/70 zz3, 46 tr) | +20.3% |
| ZigZag RSI | WTI | 16 | 0 | 0 | 0 | -13.5% (30min r14 30/70 zz1, 107 tr) | +5.4% |
| ZigZag RSI | XAU | 14 | 12 | 0 | 0 | +4.0% (1h r14 30/70 zz1, 34 tr) | +13.4% |
| 123 Reversal + SMI | BTC | 20 | 19 | 1 | 1 | +45.9% (1h smi50 ambos, 855 tr) | +43.9% |
| 123 Reversal + SMI | ETH | 20 | 19 | 0 | 0 | +51.2% (1h smi50 ambos, 908 tr) | +56.8% |
| 123 Reversal + SMI | US100 | 20 | 15 | 0 | 0 | +7.8% (30min smi50 long, 646 tr) | +20.3% |
| 123 Reversal + SMI | WTI | 20 | 4 | 0 | 1 | +8.3% (30min smi18 ambos, 1588 tr) | +5.4% |
| 123 Reversal + SMI | XAU | 20 | 12 | 0 | 0 | +7.0% (1D smi50 ambos, 598 tr) | +13.4% |
| Buying Dip | BTC | 27 | 12 | 0 | 0 | +37.0% (15min d20 tp4 sl2, 4971 tr) | +43.8% |
| Buying Dip | ETH | 30 | 12 | 0 | 0 | +56.5% (15min d7 tp4 sl2, 6871 tr) | +56.8% |
| Buying Dip | US100 | 30 | 10 | 0 | 0 | +11.6% (1h d20 tp4 sl2, 1300 tr) | +20.3% |
| Buying Dip | WTI | 30 | 0 | 0 | 0 | -9.7% (1D d20 tp1 sl1, 106 tr) | +5.7% |
| Buying Dip | XAU | 30 | 1 | 0 | 0 | +0.6% (4h d7 tp1 sl1, 769 tr) | +13.4% |
| Super trend V | BTC | 20 | 20 | 2 | 2 | +63.5% (15min m1 ambos, 2195 tr) | +43.8% |
| Super trend V | ETH | 20 | 20 | 8 | 10 | +146.2% (15min m1 ambos, 2119 tr) | +56.8% |
| Super trend V | US100 | 20 | 18 | 2 | 0 | +14.5% (15min m1 long, 830 tr) | +20.3% |
| Super trend V | WTI | 20 | 6 | 0 | 1 | +10.6% (1D m3 ambos, 59 tr) | +5.7% |
| Super trend V | XAU | 20 | 18 | 1 | 0 | +12.7% (1h m3 ambos, 393 tr) | +13.4% |
| RSI PrimeAutomation | BTC | 30 | 25 | 2 | 0 | +42.5% (4h s4 tp0 ambos, 97 tr) | +43.7% |
| RSI PrimeAutomation | ETH | 30 | 30 | 7 | 4 | +70.0% (30min s4 tp0 ambos, 736 tr) | +56.8% |
| RSI PrimeAutomation | US100 | 30 | 30 | 3 | 0 | +9.0% (15min s4 tp0 long, 878 tr) | +20.3% |
| RSI PrimeAutomation | WTI | 30 | 4 | 0 | 0 | +3.6% (4h s2 tp4 ambos, 191 tr) | +5.4% |
| RSI PrimeAutomation | XAU | 30 | 27 | 2 | 0 | +6.8% (30min s4 tp0 long, 417 tr) | +13.4% |
| Trend Trader MACD | BTC | 40 | 24 | 0 | 0 | +32.6% (1D m3 macd ambos, 110 tr) | +43.8% |
| Trend Trader MACD | ETH | 40 | 34 | 2 | 2 | +82.7% (4h m1.5 semmacd ambos, 2549 tr) | +56.6% |
| Trend Trader MACD | US100 | 40 | 21 | 4 | 0 | +10.6% (1D m3 semmacd long, 65 tr) | +20.2% |
| Trend Trader MACD | WTI | 40 | 7 | 1 | 4 | +19.9% (1D m1.5 macd ambos, 275 tr) | +5.7% |
| Trend Trader MACD | XAU | 40 | 20 | 4 | 0 | +13.0% (4h m3 semmacd ambos, 635 tr) | +13.4% |
| EVWMA x VWAP | BTC | 20 | 17 | 2 | 2 | +83.3% (4h 100 ambos, 254 tr) | +43.7% |
| EVWMA x VWAP | ETH | 20 | 18 | 4 | 5 | +88.1% (4h 100 ambos, 246 tr) | +56.6% |
| EVWMA x VWAP | US100 | 20 | 17 | 0 | 0 | +9.7% (1D 30 long, 55 tr) | +20.2% |
| EVWMA x VWAP | WTI | 20 | 7 | 0 | 5 | +22.0% (30min 30 ambos, 2286 tr) | +5.4% |
| EVWMA x VWAP | XAU | 20 | 18 | 0 | 0 | +8.6% (1h 100 ambos, 534 tr) | +13.4% |
| VWAP Pullback | BTC | 25 | 12 | 0 | 0 | +37.0% (1h sl5% tp15% rsi40, 256 tr) | +43.9% |
| VWAP Pullback | ETH | 25 | 15 | 0 | 0 | +32.6% (30min sl5% tp15% rsi40, 381 tr) | +56.8% |
| VWAP Pullback | US100 | 23 | 23 | 0 | 0 | +16.7% (15min sl5% tp15% rsi40, 52 tr) | +20.3% |
| VWAP Pullback | WTI | 25 | 0 | 0 | 0 | -11.1% (4h sl3% tp7% rsi30, 125 tr) | +5.4% |
| VWAP Pullback | XAU | 23 | 23 | 0 | 0 | +2.5% (30min sl3% tp7% rsi30, 80 tr) | +13.4% |
## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **Super trend V ETH 15m (m1, ambos)** | +146% vs +57% (t 3,9) | +610% vs +330% | +57% vs +1% | +25% vs −11% | +29% vs +13% | +124% | **aprovada com ressalva** |
| Super trend V ETH 15m (m1, long) | +86% (Sh 1,1) | +418% vs +330% | +18% vs +1% | +3% vs −11% | +14% vs +13% | +77% | passa, mas fraca na 2ª metade |
| ZigZag RSI BTC 15m (RSI14 30/70) | +51% vs +44% (Sh 1,35) | **+70% vs +129%** | +44% vs +15% | +39% vs +13% | +51% vs +40% | +50% | quase (terço 1) |
| Triple EMA ETH 15m (ambos) | +79% (Sh 1,4) | **+225% vs +330%** | +20% | +45% | +19% vs +13% | +63% | quase (terço 1) |
| RSI PrimeAutomation ETH 4h (sem alvo, long) | +60% (Sh 1,7) | **perde** | +28% | +9% vs −11% | +19% vs +13% | +60% | quase (terço 1, 64 trades) |
| Twin Range ETH 4h (sem stop/alvo) | +59% | **perde** | ganha | ganha | +35% vs +13% | **+56% vs +57%** | reprovada |
| Super trend V BTC 15m (ambos) | +63,5% | ganha | **+3% vs +15%** | **+6% vs +13%** | +13% vs +40% | +48% | reprovada |
| Triple EMA BTC 4h / EVWMA BTC 4h | +55% / +83% | perdem / ganha | ganham | **perdem** | **perdem** | — | reprovadas |
| Crazy Scalping WTI 1h / Twin Range WTI 1h | +11% / +18,5% | ganham | perde / ganha | **perdem** | perde / +4% vs +3% | +9% / +8% | reprovadas |
| MA 10/20 XAU 1h e 30m 20/50 | +13,9% / +13,5% | ganham | **perdem** | ganham | perdem | +1% / +3% | reprovadas |

## Conclusões

- **Super trend V no ETH 15m** (SuperTrend 10×1 em volta de um VPT suavizado, comprado e vendido) passa em todos os terços, na 2ª metade (+29% vs +13%) e com custo 4× (+124%). A vizinhança é boa: 15m, 30m e 1h com multiplicador 1 ficam acima do B&H, e a versão só comprada também passa, mas por pouco na 2ª metade. Ressalvas: 314 trades por ano, DD −70% em log (cerca de −50%), depende do volume da Binance e é mais um seguidor de tendência no ETH. No BTC a mesma regra morre depois de 2022.
- **ZigZag RSI no BTC 15m** é a mais limpa do lote fora do ETH (Sharpe 1,35, ganha nos terços 2 e 3 e na 2ª metade), mas perde na alta de 2020-22: "quase".
- **ETH:** de novo vários seguidores de tendência que perdem só o terço 1 (Triple EMA, RSI PrimeAutomation, Twin Range).
- **US100:** nada acima do B&H. **XAU:** só o MA 10/20, marginal e destruído pelo custo 4×.
