# Lote 25 do TradingView (50 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote25.py` (grade) e `scripts/study_tvlote25_rob.py` (robustez). Resultados: `results/study_tvlote25_{ativo}.txt`, `_grid.csv` e `results/study_tvlote25_rob_{ativo}.txt`. Para caber 50 estratégias, cada uma tem uma grade menor (padrão, um parâmetro alternativo e comprado e vendido vs só comprado).

**Puladas na ordem da lista (68):**
- **Olha o futuro:** Orion Algo v2 (`1QOQnMVn`, lookahead_on), HTF High/Low Repaint (`5FvIVVS2`), Universal Breakout KedArc (`tSoUhlM9`), X48 MA Type Cross (`DAD06s8m`), Octopus Nest (`2EEuy0st`), SuperTrend Multi Time Frame (`nXIb4hOt`), Optimized Heikin Ashi (`f4SEwIH3`) e Renko T3 (`KeWBWLGT`), todos com lookahead_on; `security` em Pine antigo: Mega crypto bot (`o9VK7ifK`), Heiken Ashi Ichimoku (`9RTfHpTI`), P2-V2 BTC (`ec7Z0XWA`), Bobo Intraday Swing (`rLNCQUqm`), SlingShot + MTF (`6RrnYult`) e Camarilla V2 (`MXkclJVM`, pivôs do dia corrente).
- **Páginas que não baixaram (404):** noro's wavetrend (`FDCf5Nus`), Ema Scalp (`kUncyS8L`), noro's trend MAs (`01KhVWQx`), PerfectStrategy (`9JoYuVLt`) e robotrading zz-8 fractals (`ddFmph9w`).
- **Templates, exemplos, ferramentas ou bots:** Joint Conditions Suite (`2SMDLIj7`), Stop Loss Example (`WD09HFwm`), Trading Report Generator (`OTfw8b2a`), Backtesting Module (`uLY2TQdm`), Strategy Template (`ImCFrBhi`), Multi MA Trend Following Template (`tzykpyCd`), Alerts to MT4/MT5 (`BTSkg8IP`, TP parcial em ticks), Oscillator Evaluator (`M9taaIkp`), Zendog V3 DCA (`Ejzw96lp`), Signal Tester (`YKadF8OO`), Linear trend (`C7OvNbAU`, sem ordens) e Follow the Trend (`HJgxw5dy`, sem ordens).
- **Duplicadas:** Chandelier Exit + EMA200 (`T7c4n0Qu`, o Chandelier Exit deste lote), Ichimoku Cloud (`sE2bIlCG`, o Ichimoku básico do lote 13), Pivot Reversal (`PIWdkQtS` e `fq8iiXQI`, o exemplo do lote 10) e Multi-Step FlexiSuperTrend (`FxxdXitn`, a FlexiSuperTrend deste lote com TPs parciais).
- **Sessão de bolsa específica ou dados externos:** ORB LuciTech (`10yYqaY7`), Pro Trading Art ORB (`wkwvEkmS`, NSE 9:15), 3 Candle Strike (`zqbs2shU`, janelas de sessão e ATR diário) e Put/Call ratio (`ZhTSnvCF`).
- **Não gera trades:** 15m Asia Gold ORB (`oYW9gdag`): o script zera a faixa da Ásia antes da janela de entrada, então a condição nunca é verdadeira.
- **Piramidação, grid ou TPs parciais:** Smart Grid Scalping (`B3Ey5I4g`), Quadratic Semaphore (`AgOZCtFE`, pirâmide de 5), Simple RSI (`CqjfRFhX`, 7 entradas), MTF stochastic (`5xJO5TfO`, pirâmide de 3 e trailing em ticks), Ultimate Prop Firm (`PkUPYbw7`, TP1/TP2) e Yesterday's High (`JoYgHVFj`, trailing em ticks e filtros truncados).
- **Complexas demais para reproduzir com fidelidade:** Divergence Trendoscope (`haCPJOF2`), `EbAcK7HY` (656 linhas), Elliott Wave + Supertrend (`hlOgflm1`), cRSI Waves (`mcr9VUaB`, 1.004 linhas), VWMA + kNN (`73oLZ8IM`), Momentum Sequence (`mmrInMTp`), RSI OB/OS Divergence (`d92hvFQx`, 1.777 linhas), Coral Trend Pullback (`kc6Itas8`), NQ Super Scalper (`6ve1ax1D`), Myth-Busting 6 (`wkb7JqzN`), Technicals Rating (`preK60Qg`, dezenas de indicadores), `FxJdGwmG` (643 linhas), Fibonacci Trend Reversal (`cZa2pcyV`), ATR Trend TP/SL (`fM3YQz8i`, 447 linhas), Renko Emulation (`cwGp0ul5`, tijolo absoluto de 3 pontos), PercentX Trend Follower (`WKgRAD0V`, biblioteca externa), Divergence for Many (`C8cpBFWm`), EMA Cross + Divergence (`x5Rl4RAz`, biblioteca externa), Ichimoku Kumo Twist (`SDUJ54K4`, presets em Pine v3), Multi-Oscillator Divergence (`8tJR3Gvh`) e Heikin/Kaufman (`KPDPfaQK`, velas Heikin Ashi de 25 min via `security`).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 214 | Chandelier Exit | `yca6gmSk` | Chandelier Exit (22, 3, extremos do close): virada compra/vende; stop de 5% no close, alvo 20% pela maxima, trailing de 5 pontos percentuais depois de +10% (risk=False: so a virada). |
| 215 | Bollinger Bands Enhanced (long-only) | `V4B5nKIx` | So long: minima acima da EMA200 tocando a banda inferior (BB20, 2); stop entrada - 1,75 ATR14; depois que a maxima passa entrada + 2,25 ATR, sai com close abaixo da media. |
| 216 | Support Resistance | `6GeSAYfE` | R = maxima de 10 no penultimo cruzamento close x SMA10, S = minima de 10 idem; close rompe R compra, perde S vende; inverte. |
| 217 | MA Displaced Envelope + ATRTS | `n45eXKBG` | Envelope +-0,5% da EMA9 deslocada 13 barras define a direcao; so fica posicionado se o close concordar com o ATR trailing stop (15, 2); senao zera. |
| 218 | FlexiSuperTrend | `y9noW915` | Mediana de (hlc3 - linha) de 20 SuperTrends (ATR10, fatores 0,618 + 0,382k); SuperTrend (10, 15) sobre velas sinteticas da mediana: direcao de alta com mediana > 0 compra (espelho vende); sai na virada. |
| 219 | Hull MA TimeFrame CrossOver | `KdC6xqb8` | Sobre a abertura: HMA1000 subindo, HMA2 acima da abertura do dia e da HMA1000, e HMA1000 cruzando acima do ATR trailing (14 x ATR14) compra; espelho vende; inverte. |
| 220 | CMO TradeDots | `MNBZqC72` | CMO9 e sinal EMA9: sinal abaixo de -40 com histograma negativo subindo compra; acima de 40 com histograma positivo caindo vende; fecha quando o sinal entra na zona oposta. |
| 221 | Moon Phases | `BAc77VfD` | Fase da lua pela data: compra na 'lua nova' do script (idade cruza 15) e vende quando a idade reinicia; inv troca os lados. |
| 222 | Triangular Hull MA | `gMeYb8Dp` | THMA40 cruza ela mesma de 2 barras atras; inverte. |
| 223 | DAX Shooter | `CfgKji30` | RSI7 cruza acima de 30 com ADX14 > 32 e minima abaixo da BB50 inferior compra (limite acima do preco = mercado); espelho vende; inverte. |
| 224 | Master Supertrend | `YexkkFy8` | SuperTrend de faixa +/- (maxima de 60 de max(h-o, h-c1) e max(o-l, c1-l)) x 2, stops so encolhem, viradas pelo close; sempre posicionado na direcao. |
| 225 | State-aware MA Cross (long-only) | `FgwP9BhA` | So long: o par de medias muda com o estado (EMA20 subindo e close acima dela); cruzamento para cima da curta (do estado) sobre a longa compra, para baixo zera. |
| 226 | Dynamic RSI Momentum | `08eSyDlq` | RSI com periodo dinamico (20 a 50 pela correlacao close x momento 10) cruzando 30 para cima compra, 70 para baixo vende; inverte. |
| 227 | Range Strat MACD/RSI | `XWgu79vU` | Sobre a abertura: histograma MACD cruza zero para cima com RSI14 <= 55 compra; para baixo com RSI >= 50 vende; stop 15%; inverte. |
| 228 | Forex Fractal EMA Scalper | `pgsJGhIg` | EMAs 10/20/100 do hl2 alinhadas para cima + fractal de topo (2 barras) -> o script VENDE (sinais trocados; inv=False desfaz); TP/SL de 25 pips -> tp%. |
| 229 | Ichimoku + MACD/CMF/TSI | `Pjsgs9JO` | Tenkan10 > Kijun30, momento 25 > 0, close acima da nuvem (deslocada 25), histograma MACD (SMA do hl2) > 0, CMF10 > 0,1 e TSI(20, 20) > 0 compra; espelho vende; inverte. |
| 230 | Hybrid RSI + Breakout | `aAszLZWi` | ADX14 <= 20 (lateral): RSI14 < 40 acima da EMA200 compra, > 60 abaixo vende, sai com RSI cruzando 50; ADX > 20: rompimento de 20 closes a favor da EMA200 com trailing de 2 ATR ativado apos 2 ATR de lucro. |
| 231 | Combo 123 Reversal + RSI | `IuTkaU1w` | 123 Reversal (estocastico 14) e RSI12 fora de 30/70 concordando; discordando, zera. |
| 232 | RSI Bull Div (long-only) | `NC603cui` | So long: RSI14 < 30, RSI suavizado (HMA10) < 35 caindo ha 3+ barras, minima do suavizado em 25 < 25, close abaixo do close da barra do menor RSI em 25 e RSI acima desse minimo (divergencia); TP 3%, SL 1,75%; sai com RSI > 65. |
| 233 | EMA Long Only | `yeBIG7oZ` | So long: SMA2 cruza acima da EMA21 + ATR21 compra; cruza abaixo da EMA21 - ATR21 zera. |
| 234 | Mutanabby AI Algo Pro (long-only) | `t3UuM5DI` | So long: engolfo de alta com corpo/TR > 0,5, RSI14 < 50 e close abaixo de 5 barras atras compra; engolfo de baixa espelhado zera; stop 2% da entrada. |
| 235 | Pivot of Pivot Reversal | `mXygJWkv` | Pivos (4, 2) com folga de 0,1 ATR14; pivo de pivos (o do meio de 3 maiores); stop de compra acima do pivo de pivos de topo enquanto o topo recente nao foi rompido (espelho na venda); inverte. |
| 236 | Mov Avg Speed (3 sinais) | `pCxvfqFv` | Voto de 3 (ROC1 medio de 10 da SMA50, estocastico 14 em 20/80, EMA9 do MACD subindo): 2 a favor compra ou vende; inverte. |
| 237 | BEST Trailing Stop | `NOGqbIcu` | SMA15 x SMA45 inverte; stop movel = minima x 0,97 (maxima x 1,03 no short) desde o cruzamento, so anda a favor; a perda dele fecha na abertura seguinte. |
| 238 | RSI mensal (long-only) | `rHDrnos6` | So long: RSI14 mensal (mes fechado) acima da sua SMA14 compra, abaixo zera. |
| 239 | Davin 10/200 MA Pullback (long-only) | `Gkib6KgL` | So long: close acima da SMA200 e abaixo da SMA10 (ou 14% abaixo da maxima de 52) compra; sai com close acima da SMA10 e abaixo da minima anterior, ou close 15% abaixo da entrada. |
| 240 | MA Scalper Coinrule (long-only) | `PfBSgqMw` | So long: SMA9 cruza acima da SMA50 com SMA50 < SMA100 < SMA200 compra; sai com SMA9 cruzando a SMA200, stop 2%, alvo 8%. |
| 241 | Grover Llorens Activator | `VuYM89Tw` | Grover Llorens Activator (480, 14): close cruzando a linha compra/vende; inverte. |
| 242 | VWAP Breakout | `39HGmmqK` | Close cruza a VWAP diaria: compra/vende; stop 1,5 ATR14, alvo 2 ATR14 (do sinal); inverte. |
| 243 | Stoch/EMA Cross | `PPKWNyyw` | Estocastico (14, 6, 3) cruza para cima abaixo de 20 com EMA55 >= EMA89 compra; espelho acima de 80 vende; sai com %D cruzando 80/20 ou o cruzamento das EMAs; alvo 8%. |
| 244 | EMA Cross + RSI + ADX | `e7XQPek8` | EMA9 x EMA21 com RSI14 > 55 compra, < 40 vende; fecha no cruzamento contrario; stop 2% do close do sinal. |
| 245 | Multi-X (long-only) | `LZ1KzR4f` | So long: EMA9 cruza acima da SMA21 compra, abaixo zera. |
| 246 | Trend Reversal Alerts (long-only) | `2DxTUzED` | So long: dois closes subindo com vela de alta (resistencia > 0) compra; dois caindo com vela de baixa zera. |
| 247 | MACD + CCI | `l7eeKNis` | CCI14 > 100 com MACD > 0, ou CCI > -100 com MACD < 0, compra; CCI < -100 com MACD < 0, ou CCI < 100 com MACD > 0, vende (a venda prevalece quando as duas valem); as 'saidas' do script nao tem efeito; inverte. |
| 248 | Uhl MA System | `4S9Yz3DB` | Uhl MA (100): CTS cruza a CMA; inverte. |
| 249 | Swing HULL + T3 | `YgRqvCGx` | Media de HMA50 e T3(50, 0,7) subindo compra, caindo vende; alvo 8% no long, alvo 3% / stop 6% no short. |
| 250 | TASC One Percent A Week (long-only) | `nVECqIQx` | So long: limite de compra 1% abaixo da abertura de segunda (UTC); alvo de 1% sobre a entrada a partir do dia seguinte; se cair 0,5%, alvo vira o preco de entrada; zera no fechamento da ultima barra de sexta. |
| 251 | Stoch + ATR | `OK4OIiJ2` | Estocastico 34 (suav. 2) cruza acima de 90 - RSI34 do ATR34 compra; abaixo de RSI(ATR) + 10 vende; inverte. |
| 252 | SPY Master | `4c9zIvHX` | RSI2 do ohlc4: EMA3 cruza acima de 50 compra, EMA5 cruza abaixo de 50 vende; inverte. |
| 253 | KPL Swing | `4mz6xvnK` | Rompimento da maxima/minima de 20 define o lado; linha = minima de 20 (lado comprado) ou maxima de 20; close cruza a linha compra/vende; inverte. |
| 254 | Gianno Nano | `M7e4uwLN` | EMA10 x EMA60 inverte; stop 3% / alvo 36% no long, stop 5% / alvo 24% no short (do close do sinal). |
| 255 | Trendline Breakout KedArc | `grMQIRAr` | LTA pelos dois ultimos fundos (se ascendentes) e LTB pelos dois ultimos topos (se descendentes), pivos 5/5; close rompe a LTB acima da EMA200 compra, perde a LTA abaixo dela vende; stop 2 ATR14, alvo 4 ATR; inverte. |
| 256 | Fractal Breakout | `Mwu4JMaQ` | Close cruza acima do penultimo fractal de topo compra; abaixo do penultimo fractal de fundo vende; inverte. |
| 257 | Double Bottom/Top Hunter | `tkyuZRbN` | Minima igual a minima de 100 e igual a minima da ocorrencia anterior (fundo duplo exato) compra; topo duplo vende; inverte (as saidas do script nunca disparam). |
| 258 | BEST ATR Stop Multiple | `UA83Q4Je` | SMA15 x SMA45 inverte; stop = close do sinal - 2 ATR14 (espelho no short). |
| 259 | NR7ID (short-only) | `abjeWQD5` | So short: NR7 + inside bar de baixa com SMA14 nao subindo vende; zera na proxima vela de baixa. |
| 260 | Reversal Trading Bot | `cXVnf1WH` | Divergencia simples (minima de 5 caindo com minimo do RSI8 de 5 subindo; espelho) compra/vende; stop 1%, alvo 2%; filtros opcionais desligados (padrao); inverte. |
| 261 | Multi-MA (4MA) | `C1hyNDWO` | HMA3 dupla, VWMA3 e WMA75: HMA subindo abaixo da WMA75 e acima da VWMA compra (so flat); espelho vende; fecha quando a HMA vira do outro lado da VWMA. |
| 262 | Awesome Oscillator | `fSHXMVey` | AO (SMA5 - SMA34 do hl2) subindo compra, caindo vende; inverte. |
| 263 | Smart Money Pivot | `IMTwV7U8` | Rompimento (pela maxima) do ultimo pivo de topo (20/20) ainda ativo compra; perda do ultimo pivo de fundo vende; stop 1%, alvo 1,5%; inverte. |

## Grade por ativo

Colunas: células, liq>0, t>2, CAGR > B&H (com ≥ 30 trades), melhor CAGR (célula), B&H. Células acima do B&H: ETH 110, WTI 77, BTC 28, XAU 6 e US100 nenhuma.

| Estratégia | Ativo | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR | B&H |
|---|---|---|---|---|---|---|---|
| Chandelier Exit | BTC | 15 | 14 | 0 | 0 | +38.4% (1D semrisco ambos, 65 tr) | +43.8% |
| Chandelier Exit | ETH | 15 | 14 | 2 | 4 | +152.8% (30min risco ambos, 3332 tr) | +56.8% |
| Chandelier Exit | US100 | 15 | 11 | 1 | 0 | +11.7% (15min risco long, 77 tr) | +20.3% |
| Chandelier Exit | WTI | 15 | 4 | 0 | 4 | +12.7% (1h semrisco ambos, 2161 tr) | +5.4% |
| Chandelier Exit | XAU | 15 | 13 | 1 | 0 | +9.7% (4h risco ambos, 410 tr) | +13.4% |
| Bollinger Bands Enhanced (long-only) | BTC | 10 | 10 | 2 | 0 | +31.3% (4h sl1.75, 192 tr) | +43.7% |
| Bollinger Bands Enhanced (long-only) | ETH | 10 | 8 | 1 | 0 | +40.3% (15min sl3, 2171 tr) | +56.8% |
| Bollinger Bands Enhanced (long-only) | US100 | 10 | 8 | 0 | 0 | +7.4% (4h sl3, 194 tr) | +20.3% |
| Bollinger Bands Enhanced (long-only) | WTI | 10 | 0 | 0 | 0 | -7.9% (4h sl3, 150 tr) | +5.4% |
| Bollinger Bands Enhanced (long-only) | XAU | 10 | 4 | 0 | 0 | +0.4% (1D sl1.75, 32 tr) | +13.4% |
| Support Resistance | BTC | 20 | 15 | 1 | 1 | +47.1% (4h 10 ambos, 399 tr) | +43.7% |
| Support Resistance | ETH | 20 | 19 | 0 | 1 | +94.7% (1D 10 ambos, 54 tr) | +56.5% |
| Support Resistance | US100 | 20 | 17 | 1 | 0 | +10.6% (30min 10 long, 1419 tr) | +20.3% |
| Support Resistance | WTI | 20 | 4 | 0 | 1 | +6.9% (1D 10 ambos, 68 tr) | +5.7% |
| Support Resistance | XAU | 20 | 18 | 2 | 1 | +15.9% (1h 10 ambos, 1232 tr) | +13.4% |
| MA Displaced Envelope + ATRTS | BTC | 20 | 18 | 1 | 1 | +47.2% (1D 30 ambos, 100 tr) | +43.8% |
| MA Displaced Envelope + ATRTS | ETH | 20 | 20 | 4 | 4 | +85.3% (30min 30 ambos, 3976 tr) | +56.8% |
| MA Displaced Envelope + ATRTS | US100 | 20 | 18 | 5 | 0 | +12.8% (1h 9 long, 948 tr) | +20.3% |
| MA Displaced Envelope + ATRTS | WTI | 20 | 6 | 0 | 5 | +14.6% (1D 9 ambos, 135 tr) | +5.7% |
| MA Displaced Envelope + ATRTS | XAU | 20 | 15 | 5 | 0 | +7.7% (4h 9 ambos, 484 tr) | +13.4% |
| Hull MA TimeFrame CrossOver | BTC | 31 | 30 | 0 | 3 | +52.8% (15min 200 s14 ambos, 442 tr) | +43.8% |
| Hull MA TimeFrame CrossOver | ETH | 29 | 27 | 4 | 5 | +96.3% (1h 200 s14 ambos, 111 tr) | +56.8% |
| Hull MA TimeFrame CrossOver | US100 | 28 | 23 | 0 | 0 | +12.5% (30min 1000 s14 long, 36 tr) | +20.3% |
| Hull MA TimeFrame CrossOver | WTI | 30 | 8 | 0 | 7 | +23.1% (4h 200 s3 ambos, 54 tr) | +5.4% |
| Hull MA TimeFrame CrossOver | XAU | 28 | 21 | 1 | 0 | +13.3% (30min 200 s3 ambos, 337 tr) | +13.4% |
| CMO TradeDots | BTC | 20 | 6 | 0 | 0 | +7.6% (15min 20 long, 3671 tr) | +43.8% |
| CMO TradeDots | ETH | 20 | 7 | 0 | 0 | +11.4% (4h 20 long, 231 tr) | +56.6% |
| CMO TradeDots | US100 | 20 | 7 | 1 | 0 | +7.6% (4h 20 long, 215 tr) | +20.3% |
| CMO TradeDots | WTI | 20 | 1 | 0 | 0 | -1.3% (1D 40 ambos, 36 tr) | +5.7% |
| CMO TradeDots | XAU | 20 | 1 | 0 | 0 | -0.2% (4h 40 ambos, 174 tr) | +13.4% |
| FlexiSuperTrend | BTC | 20 | 17 | 2 | 1 | +49.4% (4h f15 ambos, 153 tr) | +43.7% |
| FlexiSuperTrend | ETH | 20 | 20 | 2 | 2 | +84.0% (4h f5 ambos, 451 tr) | +56.6% |
| FlexiSuperTrend | US100 | 20 | 14 | 3 | 0 | +10.8% (1h f5 ambos, 1629 tr) | +20.3% |
| FlexiSuperTrend | WTI | 20 | 6 | 0 | 2 | +30.3% (15min f15 ambos, 3056 tr) | +5.4% |
| FlexiSuperTrend | XAU | 20 | 12 | 2 | 0 | +10.5% (15min f15 ambos, 2141 tr) | +13.4% |
| Moon Phases | BTC | 20 | 15 | 0 | 0 | +21.0% (15min normal long, 83 tr) | +43.8% |
| Moon Phases | ETH | 20 | 14 | 0 | 0 | +33.8% (15min normal long, 83 tr) | +56.8% |
| Moon Phases | US100 | 20 | 15 | 0 | 0 | +10.5% (15min normal long, 119 tr) | +20.3% |
| Moon Phases | WTI | 20 | 5 | 0 | 1 | +6.1% (30min inv ambos, 240 tr) | +5.4% |
| Moon Phases | XAU | 20 | 10 | 0 | 0 | +4.2% (1D normal ambos, 188 tr) | +13.4% |
| Triangular Hull MA | BTC | 20 | 19 | 2 | 1 | +53.3% (15min 100 ambos, 3701 tr) | +43.8% |
| Triangular Hull MA | ETH | 20 | 20 | 5 | 7 | +154.6% (15min 100 ambos, 3588 tr) | +56.8% |
| Triangular Hull MA | US100 | 20 | 16 | 1 | 0 | +11.9% (15min 100 long, 1325 tr) | +20.3% |
| Triangular Hull MA | WTI | 20 | 5 | 0 | 4 | +20.6% (30min 100 ambos, 1652 tr) | +5.4% |
| Triangular Hull MA | XAU | 20 | 18 | 4 | 0 | +11.5% (1h 40 ambos, 1614 tr) | +13.4% |
| DAX Shooter | BTC | 18 | 9 | 0 | 0 | +12.9% (15min adx20 long, 1119 tr) | +43.8% |
| DAX Shooter | ETH | 19 | 7 | 0 | 0 | +1.0% (1h adx20 long, 272 tr) | +56.8% |
| DAX Shooter | US100 | 17 | 15 | 0 | 0 | +14.5% (1h adx20 long, 154 tr) | +20.3% |
| DAX Shooter | WTI | 19 | 1 | 1 | 0 | -3.8% (30min adx20 ambos, 978 tr) | +5.4% |
| DAX Shooter | XAU | 18 | 4 | 0 | 0 | +4.3% (4h adx20 ambos, 103 tr) | +13.4% |
| Master Supertrend | BTC | 40 | 28 | 0 | 2 | +52.7% (1D 20 m2 ambos, 93 tr) | +43.8% |
| Master Supertrend | ETH | 40 | 33 | 1 | 3 | +61.5% (30min 20 m4 ambos, 1965 tr) | +56.8% |
| Master Supertrend | US100 | 40 | 32 | 0 | 0 | +14.5% (1D 20 m4 ambos, 43 tr) | +20.2% |
| Master Supertrend | WTI | 40 | 9 | 0 | 5 | +23.2% (15min 60 m4 ambos, 2121 tr) | +5.4% |
| Master Supertrend | XAU | 40 | 27 | 3 | 1 | +14.0% (1h 60 m4 ambos, 348 tr) | +13.4% |
| State-aware MA Cross (long-only) | BTC | 5 | 5 | 0 | 0 | +33.4% (1D padrao, 115 tr) | +43.8% |
| State-aware MA Cross (long-only) | ETH | 5 | 5 | 0 | 1 | +60.9% (4h padrao, 732 tr) | +56.6% |
| State-aware MA Cross (long-only) | US100 | 5 | 4 | 0 | 0 | +15.9% (4h padrao, 584 tr) | +20.3% |
| State-aware MA Cross (long-only) | WTI | 5 | 0 | 0 | 0 | -28.7% (4h padrao, 770 tr) | +5.4% |
| State-aware MA Cross (long-only) | XAU | 5 | 1 | 0 | 0 | +1.4% (4h padrao, 636 tr) | +13.4% |
| Dynamic RSI Momentum | BTC | 14 | 4 | 0 | 0 | -5.5% (4h 30/70 ambos, 44 tr) | +43.7% |
| Dynamic RSI Momentum | ETH | 15 | 2 | 0 | 0 | -3.7% (30min 30/70 long, 168 tr) | +56.8% |
| Dynamic RSI Momentum | US100 | 13 | 7 | 0 | 0 | +7.9% (1h 30/70 long, 77 tr) | +20.3% |
| Dynamic RSI Momentum | WTI | 13 | 5 | 1 | 1 | +20.6% (30min 20/80 ambos, 40 tr) | +5.4% |
| Dynamic RSI Momentum | XAU | 13 | 2 | 0 | 0 | +3.2% (1h 30/70 ambos, 131 tr) | +13.4% |
| Range Strat MACD/RSI | BTC | 25 | 10 | 0 | 0 | +15.1% (1D sl15 ambos, 56 tr) | +43.8% |
| Range Strat MACD/RSI | ETH | 25 | 14 | 0 | 0 | +34.1% (1D sl5% ambos, 91 tr) | +56.5% |
| Range Strat MACD/RSI | US100 | 25 | 17 | 0 | 0 | +12.9% (1h sl15% long, 342 tr) | +20.3% |
| Range Strat MACD/RSI | WTI | 25 | 1 | 0 | 0 | -0.7% (4h sl5% ambos, 366 tr) | +5.4% |
| Range Strat MACD/RSI | XAU | 25 | 0 | 0 | 0 | -2.1% (4h sl5% long, 98 tr) | +13.4% |
| Forex Fractal EMA Scalper | BTC | 45 | 11 | 2 | 0 | +38.0% (15min tp2.0% direto ambos, 5617 tr) | +43.8% |
| Forex Fractal EMA Scalper | ETH | 45 | 9 | 0 | 1 | +80.2% (30min tp2.0% direto ambos, 4867 tr) | +56.8% |
| Forex Fractal EMA Scalper | US100 | 45 | 14 | 1 | 0 | +11.8% (15min tp2.0% direto long, 1247 tr) | +20.3% |
| Forex Fractal EMA Scalper | WTI | 45 | 5 | 0 | 0 | +3.2% (1D tp2.0% direto ambos, 268 tr) | +5.7% |
| Forex Fractal EMA Scalper | XAU | 45 | 12 | 2 | 0 | +9.6% (15min tp2.0% direto ambos, 2459 tr) | +13.4% |
| Ichimoku + MACD/CMF/TSI | BTC | 10 | 10 | 1 | 0 | +40.4% (15min ambos, 3183 tr) | +43.8% |
| Ichimoku + MACD/CMF/TSI | ETH | 10 | 10 | 1 | 2 | +110.8% (30min ambos, 1445 tr) | +56.8% |
| Ichimoku + MACD/CMF/TSI | US100 | 10 | 10 | 1 | 0 | +13.0% (15min long, 1065 tr) | +20.3% |
| Ichimoku + MACD/CMF/TSI | WTI | 10 | 3 | 0 | 1 | +12.9% (30min ambos, 1593 tr) | +5.4% |
| Ichimoku + MACD/CMF/TSI | XAU | 10 | 10 | 1 | 0 | +11.0% (30min ambos, 1185 tr) | +13.4% |
| Hybrid RSI + Breakout | BTC | 20 | 20 | 1 | 2 | +63.5% (4h atr4 ambos, 279 tr) | +43.7% |
| Hybrid RSI + Breakout | ETH | 20 | 20 | 2 | 3 | +100.6% (30min atr4 ambos, 2346 tr) | +56.8% |
| Hybrid RSI + Breakout | US100 | 20 | 18 | 4 | 0 | +13.1% (30min atr4 long, 407 tr) | +20.3% |
| Hybrid RSI + Breakout | WTI | 20 | 1 | 0 | 0 | +2.2% (4h atr4 ambos, 312 tr) | +5.4% |
| Hybrid RSI + Breakout | XAU | 20 | 16 | 0 | 0 | +8.1% (4h atr4 ambos, 239 tr) | +13.4% |
| Combo 123 Reversal + RSI | BTC | 10 | 10 | 1 | 1 | +50.6% (1h ambos, 632 tr) | +43.9% |
| Combo 123 Reversal + RSI | ETH | 10 | 10 | 4 | 4 | +72.6% (1h ambos, 670 tr) | +56.8% |
| Combo 123 Reversal + RSI | US100 | 10 | 10 | 2 | 0 | +14.0% (30min long, 597 tr) | +20.3% |
| Combo 123 Reversal + RSI | WTI | 10 | 3 | 0 | 2 | +18.2% (30min ambos, 1372 tr) | +5.4% |
| Combo 123 Reversal + RSI | XAU | 10 | 9 | 0 | 0 | +9.2% (30min ambos, 1035 tr) | +13.4% |
| RSI Bull Div (long-only) | BTC | 8 | 1 | 0 | 0 | +0.8% (1h tp6 sl3.5, 109 tr) | +43.9% |
| RSI Bull Div (long-only) | ETH | 8 | 1 | 0 | 0 | +5.7% (4h tp6 sl3.5, 36 tr) | +56.6% |
| RSI Bull Div (long-only) | US100 | 8 | 4 | 0 | 0 | +2.5% (30min tp6 sl3.5, 160 tr) | +20.3% |
| RSI Bull Div (long-only) | WTI | 8 | 2 | 1 | 0 | +2.5% (4h tp3 sl1.75, 40 tr) | +5.4% |
| RSI Bull Div (long-only) | XAU | 8 | 0 | 0 | 0 | -1.2% (30min tp6 sl3.5, 118 tr) | +13.4% |
| EMA Long Only | BTC | 10 | 10 | 1 | 0 | +43.2% (4h 21, 161 tr) | +43.7% |
| EMA Long Only | ETH | 10 | 10 | 0 | 1 | +65.5% (30min 21, 1260 tr) | +56.8% |
| EMA Long Only | US100 | 10 | 10 | 0 | 0 | +13.3% (30min 21, 1131 tr) | +20.3% |
| EMA Long Only | WTI | 10 | 0 | 0 | 0 | -19.7% (30min 50, 1093 tr) | +5.4% |
| EMA Long Only | XAU | 10 | 10 | 0 | 0 | +4.5% (30min 50, 794 tr) | +13.4% |
| Mutanabby AI Algo Pro (long-only) | BTC | 15 | 15 | 0 | 0 | +25.0% (15min semsl, 1686 tr) | +43.8% |
| Mutanabby AI Algo Pro (long-only) | ETH | 15 | 13 | 0 | 0 | +41.3% (4h sl5, 143 tr) | +56.6% |
| Mutanabby AI Algo Pro (long-only) | US100 | 15 | 14 | 0 | 0 | +12.3% (4h semsl, 82 tr) | +20.3% |
| Mutanabby AI Algo Pro (long-only) | WTI | 15 | 0 | 0 | 0 | -0.1% (4h sl2, 159 tr) | +5.4% |
| Mutanabby AI Algo Pro (long-only) | XAU | 14 | 4 | 0 | 0 | +2.3% (4h semsl, 83 tr) | +13.4% |
| Pivot of Pivot Reversal | BTC | 10 | 10 | 1 | 1 | +73.0% (4h 10/5 ambos, 51 tr) | +43.7% |
| Pivot of Pivot Reversal | ETH | 10 | 9 | 0 | 4 | +82.9% (15min 4/2 ambos, 2022 tr) | +56.8% |
| Pivot of Pivot Reversal | US100 | 9 | 7 | 0 | 0 | +8.0% (30min 10/5 ambos, 437 tr) | +20.3% |
| Pivot of Pivot Reversal | WTI | 9 | 5 | 0 | 1 | +6.3% (4h 4/2 ambos, 154 tr) | +5.4% |
| Pivot of Pivot Reversal | XAU | 9 | 7 | 3 | 0 | +10.6% (15min 4/2 ambos, 1439 tr) | +13.4% |
| Mov Avg Speed (3 sinais) | BTC | 10 | 9 | 0 | 0 | +33.0% (15min ambos, 6428 tr) | +43.8% |
| Mov Avg Speed (3 sinais) | ETH | 10 | 9 | 2 | 2 | +84.8% (15min ambos, 6228 tr) | +56.8% |
| Mov Avg Speed (3 sinais) | US100 | 10 | 7 | 0 | 0 | +7.9% (4h long, 248 tr) | +20.3% |
| Mov Avg Speed (3 sinais) | WTI | 10 | 0 | 0 | 0 | -4.4% (1D ambos, 71 tr) | +5.7% |
| Mov Avg Speed (3 sinais) | XAU | 10 | 6 | 1 | 0 | +8.2% (1D ambos, 55 tr) | +13.4% |
| RSI mensal (long-only) | WTI | 5 | 0 | 0 | 0 | — | — |
| Davin 10/200 MA Pullback (long-only) | BTC | 15 | 15 | 1 | 2 | +52.8% (4h dip14 sl15, 323 tr) | +43.7% |
| Davin 10/200 MA Pullback (long-only) | ETH | 15 | 15 | 0 | 1 | +63.5% (4h dip30 sl15, 268 tr) | +56.6% |
| Davin 10/200 MA Pullback (long-only) | US100 | 15 | 12 | 0 | 0 | +9.4% (4h dip30 sl15, 333 tr) | +20.3% |
| Davin 10/200 MA Pullback (long-only) | WTI | 15 | 0 | 0 | 0 | -17.5% (4h dip14 sl5, 434 tr) | +5.4% |
| Davin 10/200 MA Pullback (long-only) | XAU | 15 | 6 | 0 | 0 | +3.5% (1D dip14 sl5, 62 tr) | +13.4% |
| MA Scalper Coinrule (long-only) | BTC | 10 | 4 | 0 | 0 | +1.9% (1h sl2 tp8, 295 tr) | +43.9% |
| MA Scalper Coinrule (long-only) | ETH | 10 | 8 | 0 | 0 | +7.6% (30min sl2 tp8, 557 tr) | +56.8% |
| MA Scalper Coinrule (long-only) | US100 | 8 | 6 | 0 | 0 | +6.3% (30min sl5 tp15, 258 tr) | +20.3% |
| MA Scalper Coinrule (long-only) | WTI | 10 | 2 | 0 | 0 | -5.2% (1h sl2 tp8, 253 tr) | +5.4% |
| MA Scalper Coinrule (long-only) | XAU | 8 | 1 | 0 | 0 | +0.2% (4h sl2 tp8, 41 tr) | +13.4% |
| BEST Trailing Stop | BTC | 24 | 24 | 2 | 3 | +61.6% (30min tr8% ambos, 3195 tr) | +43.9% |
| BEST Trailing Stop | ETH | 25 | 25 | 7 | 6 | +121.1% (30min tr3 ambos, 3123 tr) | +56.8% |
| BEST Trailing Stop | US100 | 21 | 18 | 4 | 0 | +15.1% (30min tr3 ambos, 2193 tr) | +20.3% |
| BEST Trailing Stop | WTI | 25 | 7 | 1 | 2 | +10.0% (30min tr8% ambos, 2906 tr) | +5.4% |
| BEST Trailing Stop | XAU | 18 | 15 | 4 | 3 | +14.3% (30min tr8% ambos, 2238 tr) | +13.4% |
| Grover Llorens Activator | BTC | 18 | 14 | 2 | 2 | +65.3% (30min 100 m5 ambos, 3505 tr) | +43.9% |
| Grover Llorens Activator | ETH | 16 | 13 | 3 | 3 | +100.7% (30min 100 m5 ambos, 3476 tr) | +56.8% |
| Grover Llorens Activator | WTI | 20 | 5 | 0 | 4 | +26.7% (4h 480 m14 ambos, 134 tr) | +5.4% |
| Grover Llorens Activator | XAU | 19 | 11 | 0 | 0 | +6.3% (30min 100 m5 ambos, 2660 tr) | +13.4% |
| VWAP Breakout | BTC | 8 | 2 | 0 | 0 | +32.1% (4h tp4 ambos, 5488 tr) | +43.7% |
| VWAP Breakout | ETH | 8 | 7 | 6 | 1 | +64.5% (30min tp4 ambos, 17643 tr) | +56.8% |
| VWAP Breakout | US100 | 8 | 0 | 2 | 0 | -1.2% (4h tp4 ambos, 4428 tr) | +20.3% |
| VWAP Breakout | WTI | 8 | 0 | 0 | 0 | -5.0% (4h tp2 ambos, 5388 tr) | +5.4% |
| VWAP Breakout | XAU | 8 | 1 | 2 | 0 | -3.4% (4h tp4 ambos, 3983 tr) | +13.4% |
| Stoch/EMA Cross | BTC | 25 | 8 | 0 | 0 | +8.7% (4h tp8 ambos, 141 tr) | +43.7% |
| Stoch/EMA Cross | ETH | 23 | 13 | 1 | 0 | +24.5% (4h tp8 ambos, 132 tr) | +56.6% |
| Stoch/EMA Cross | US100 | 25 | 10 | 2 | 0 | +5.1% (4h tp8 ambos, 152 tr) | +20.3% |
| Stoch/EMA Cross | WTI | 25 | 9 | 0 | 3 | +14.8% (4h semtp ambos, 187 tr) | +5.4% |
| Stoch/EMA Cross | XAU | 25 | 10 | 0 | 0 | +3.2% (30min tp8 ambos, 947 tr) | +13.4% |
| EMA Cross + RSI + ADX | BTC | 25 | 25 | 9 | 4 | +52.6% (4h sl5% ambos, 293 tr) | +43.7% |
| EMA Cross + RSI + ADX | ETH | 25 | 25 | 5 | 8 | +87.9% (30min sl2 ambos, 2238 tr) | +56.8% |
| EMA Cross + RSI + ADX | US100 | 25 | 21 | 1 | 0 | +7.0% (1h sl2 ambos, 929 tr) | +20.3% |
| EMA Cross + RSI + ADX | WTI | 25 | 0 | 0 | 0 | -3.3% (1h sl2 ambos, 1180 tr) | +5.4% |
| EMA Cross + RSI + ADX | XAU | 25 | 10 | 0 | 0 | +3.5% (4h sl5% long, 169 tr) | +13.4% |
| Multi-X (long-only) | BTC | 5 | 5 | 0 | 0 | +35.4% (4h padrao, 410 tr) | +43.7% |
| Multi-X (long-only) | ETH | 5 | 5 | 1 | 1 | +66.2% (1h padrao, 1642 tr) | +56.8% |
| Multi-X (long-only) | US100 | 5 | 5 | 0 | 0 | +13.9% (1h padrao, 1219 tr) | +20.3% |
| Multi-X (long-only) | WTI | 5 | 0 | 0 | 0 | -20.6% (1D padrao, 60 tr) | +5.7% |
| Multi-X (long-only) | XAU | 5 | 3 | 1 | 0 | +7.4% (1h padrao, 1191 tr) | +13.4% |
| Trend Reversal Alerts (long-only) | BTC | 5 | 2 | 0 | 0 | +27.2% (4h padrao, 1242 tr) | +43.7% |
| Trend Reversal Alerts (long-only) | ETH | 5 | 4 | 0 | 0 | +40.9% (4h padrao, 1246 tr) | +56.6% |
| Trend Reversal Alerts (long-only) | US100 | 5 | 3 | 0 | 0 | +12.8% (4h padrao, 990 tr) | +20.3% |
| Trend Reversal Alerts (long-only) | WTI | 5 | 0 | 0 | 0 | -28.5% (1D padrao, 210 tr) | +5.7% |
| Trend Reversal Alerts (long-only) | XAU | 5 | 1 | 0 | 0 | -0.1% (1D padrao, 196 tr) | +13.4% |
| MACD + CCI | BTC | 10 | 5 | 0 | 0 | +23.4% (4h long, 1305 tr) | +43.7% |
| MACD + CCI | ETH | 10 | 6 | 0 | 0 | +22.0% (4h long, 1288 tr) | +56.6% |
| MACD + CCI | US100 | 10 | 3 | 1 | 0 | +10.6% (4h long, 1181 tr) | +20.3% |
| MACD + CCI | WTI | 10 | 1 | 0 | 0 | -9.5% (4h ambos, 2746 tr) | +5.4% |
| MACD + CCI | XAU | 10 | 3 | 0 | 0 | +4.5% (4h ambos, 2074 tr) | +13.4% |
| Uhl MA System | BTC | 19 | 18 | 3 | 1 | +44.9% (4h 100 ambos, 128 tr) | +43.7% |
| Uhl MA System | ETH | 19 | 19 | 5 | 6 | +96.6% (4h 100 ambos, 112 tr) | +56.6% |
| Uhl MA System | US100 | 19 | 17 | 2 | 0 | +11.5% (30min 100 long, 392 tr) | +20.3% |
| Uhl MA System | WTI | 20 | 7 | 0 | 1 | +9.3% (4h 100 ambos, 122 tr) | +5.4% |
| Uhl MA System | XAU | 19 | 17 | 2 | 0 | +10.8% (30min 30 ambos, 2787 tr) | +13.4% |
| Swing HULL + T3 | BTC | 30 | 28 | 7 | 1 | +45.2% (1D 100 sltp ambos, 453 tr) | +43.8% |
| Swing HULL + T3 | ETH | 30 | 30 | 16 | 20 | +114.8% (1h 100 sltp ambos, 2839 tr) | +56.8% |
| Swing HULL + T3 | US100 | 30 | 27 | 8 | 0 | +9.3% (15min 100 sltp ambos, 4412 tr) | +20.3% |
| Swing HULL + T3 | WTI | 30 | 14 | 1 | 8 | +18.6% (4h 100 sltp ambos, 830 tr) | +5.4% |
| Swing HULL + T3 | XAU | 30 | 22 | 4 | 0 | +10.7% (1h 50 sltp ambos, 1953 tr) | +13.4% |
| TASC One Percent A Week (long-only) | BTC | 10 | 10 | 6 | 0 | +14.8% (1h dip2 tp2, 250 tr) | +43.9% |
| TASC One Percent A Week (long-only) | ETH | 10 | 10 | 0 | 0 | +15.4% (1D dip1 tp1, 315 tr) | +56.5% |
| TASC One Percent A Week (long-only) | US100 | 10 | 10 | 2 | 0 | +4.2% (1D dip2 tp2, 160 tr) | +20.2% |
| TASC One Percent A Week (long-only) | WTI | 10 | 5 | 1 | 0 | -4.4% (1D dip2 tp2, 317 tr) | +5.7% |
| TASC One Percent A Week (long-only) | XAU | 10 | 8 | 0 | 0 | +0.8% (1D dip2 tp2, 103 tr) | +13.4% |
| Stoch + ATR | BTC | 20 | 10 | 0 | 0 | +13.5% (1D 34 long, 39 tr) | +43.8% |
| Stoch + ATR | ETH | 20 | 13 | 1 | 0 | +43.4% (30min 14 ambos, 8508 tr) | +56.8% |
| Stoch + ATR | US100 | 20 | 15 | 1 | 0 | +15.2% (1D 14 ambos, 114 tr) | +20.2% |
| Stoch + ATR | WTI | 20 | 5 | 1 | 3 | +34.9% (4h 14 ambos, 1048 tr) | +5.4% |
| Stoch + ATR | XAU | 20 | 8 | 0 | 0 | +10.1% (1D 14 ambos, 162 tr) | +13.4% |
| SPY Master | BTC | 10 | 7 | 2 | 0 | +20.2% (1D long, 170 tr) | +43.8% |
| SPY Master | ETH | 10 | 9 | 0 | 0 | +40.8% (30min ambos, 17996 tr) | +56.8% |
| SPY Master | US100 | 10 | 4 | 1 | 0 | +11.5% (4h long, 745 tr) | +20.3% |
| SPY Master | WTI | 10 | 1 | 0 | 0 | +4.2% (4h ambos, 2054 tr) | +5.4% |
| SPY Master | XAU | 10 | 2 | 0 | 0 | +3.8% (4h ambos, 1626 tr) | +13.4% |
| KPL Swing | BTC | 20 | 14 | 0 | 0 | +42.6% (4h 20 ambos, 275 tr) | +43.7% |
| KPL Swing | ETH | 20 | 19 | 1 | 2 | +91.2% (1D 20 ambos, 42 tr) | +56.5% |
| KPL Swing | US100 | 20 | 15 | 0 | 0 | +9.8% (15min 50 long, 1048 tr) | +20.3% |
| KPL Swing | WTI | 20 | 2 | 0 | 1 | +10.2% (1D 20 ambos, 50 tr) | +5.7% |
| KPL Swing | XAU | 19 | 16 | 0 | 0 | +11.2% (1h 20 ambos, 941 tr) | +13.4% |
| Gianno Nano | BTC | 15 | 15 | 2 | 0 | +38.0% (1D semsltp ambos, 53 tr) | +43.8% |
| Gianno Nano | ETH | 15 | 15 | 6 | 5 | +77.3% (1h semsltp ambos, 1355 tr) | +56.8% |
| Gianno Nano | US100 | 15 | 14 | 1 | 0 | +10.2% (30min sltp long, 35 tr) | +20.3% |
| Gianno Nano | WTI | 15 | 7 | 0 | 4 | +23.5% (1D sltp ambos, 65 tr) | +5.7% |
| Gianno Nano | XAU | 15 | 11 | 0 | 0 | +7.9% (30min semsltp ambos, 2156 tr) | +13.4% |
| Trendline Breakout KedArc | BTC | 40 | 28 | 4 | 0 | +28.0% (1h p5 semma ambos, 3094 tr) | +43.9% |
| Trendline Breakout KedArc | ETH | 39 | 37 | 0 | 0 | +44.7% (30min p10 semma ambos, 3838 tr) | +56.8% |
| Trendline Breakout KedArc | US100 | 40 | 35 | 4 | 0 | +9.2% (1D p5 semma long, 33 tr) | +20.2% |
| Trendline Breakout KedArc | WTI | 40 | 17 | 4 | 8 | +31.9% (4h p5 semma ambos, 702 tr) | +5.4% |
| Trendline Breakout KedArc | XAU | 40 | 16 | 2 | 0 | +8.2% (4h p5 semma ambos, 557 tr) | +13.4% |
| Fractal Breakout | BTC | 10 | 6 | 0 | 0 | +29.4% (1D ambos, 90 tr) | +43.8% |
| Fractal Breakout | ETH | 10 | 9 | 0 | 1 | +64.2% (30min ambos, 4768 tr) | +56.8% |
| Fractal Breakout | US100 | 10 | 8 | 1 | 0 | +11.0% (1h long, 941 tr) | +20.3% |
| Fractal Breakout | WTI | 10 | 2 | 0 | 0 | +0.0% (1D ambos, 98 tr) | +5.7% |
| Fractal Breakout | XAU | 10 | 6 | 0 | 0 | +5.3% (1D ambos, 93 tr) | +13.4% |
| Double Bottom/Top Hunter | BTC | 9 | 4 | 0 | 0 | +21.0% (30min 30 ambos, 47 tr) | +43.9% |
| Double Bottom/Top Hunter | ETH | 8 | 2 | 0 | 0 | +11.2% (15min 30 long, 59 tr) | +56.8% |
| Double Bottom/Top Hunter | US100 | 5 | 3 | 2 | 0 | -1.9% (15min 30 long, 30 tr) | +20.3% |
| Double Bottom/Top Hunter | WTI | 12 | 5 | 0 | 4 | +36.4% (30min 30 ambos, 341 tr) | +5.4% |
| Double Bottom/Top Hunter | XAU | 8 | 4 | 0 | 0 | +3.6% (15min 100 ambos, 57 tr) | +13.4% |
| BEST ATR Stop Multiple | BTC | 10 | 10 | 1 | 2 | +65.7% (30min atr4 ambos, 3195 tr) | +43.9% |
| BEST ATR Stop Multiple | ETH | 10 | 10 | 6 | 6 | +119.9% (30min atr4 ambos, 3123 tr) | +56.8% |
| BEST ATR Stop Multiple | US100 | 10 | 7 | 4 | 0 | +14.8% (30min atr2 ambos, 2193 tr) | +20.3% |
| BEST ATR Stop Multiple | WTI | 16 | 6 | 1 | 3 | +15.2% (1D atr2 ambos, 57 tr) | +5.7% |
| BEST ATR Stop Multiple | XAU | 17 | 10 | 2 | 1 | +13.9% (30min atr4 ambos, 2238 tr) | +13.4% |
| NR7ID (short-only) | BTC | 10 | 4 | 1 | 0 | +7.6% (1h semfiltro, 1865 tr) | +43.9% |
| NR7ID (short-only) | ETH | 10 | 3 | 0 | 0 | +8.1% (1D semfiltro, 88 tr) | +56.5% |
| NR7ID (short-only) | US100 | 10 | 0 | 0 | 0 | +1.3% (1D semfiltro, 33 tr) | +20.2% |
| NR7ID (short-only) | WTI | 10 | 5 | 0 | 1 | +7.1% (30min semfiltro, 3110 tr) | +5.4% |
| NR7ID (short-only) | XAU | 10 | 0 | 0 | 0 | +0.2% (1D semfiltro, 89 tr) | +13.4% |
| Reversal Trading Bot | BTC | 25 | 8 | 0 | 0 | +38.2% (1h sl3% tp6% ambos, 1464 tr) | +43.9% |
| Reversal Trading Bot | ETH | 25 | 5 | 1 | 0 | +31.9% (15min sl3% tp6% ambos, 4919 tr) | +56.8% |
| Reversal Trading Bot | US100 | 25 | 8 | 0 | 0 | +4.2% (1h sl3% tp6% long, 538 tr) | +20.3% |
| Reversal Trading Bot | WTI | 25 | 4 | 0 | 0 | +3.5% (1h sl3% tp6% ambos, 1483 tr) | +5.4% |
| Reversal Trading Bot | XAU | 25 | 7 | 0 | 0 | +1.7% (1D sl1% tp2% long, 36 tr) | +13.4% |
| Multi-MA (4MA) | BTC | 20 | 6 | 0 | 0 | +8.6% (30min wma75 long, 1962 tr) | +43.9% |
| Multi-MA (4MA) | ETH | 20 | 6 | 0 | 0 | +8.1% (4h wma75 long, 247 tr) | +56.6% |
| Multi-MA (4MA) | US100 | 19 | 7 | 0 | 0 | +9.5% (4h wma75 long, 174 tr) | +20.3% |
| Multi-MA (4MA) | WTI | 20 | 0 | 0 | 0 | +1.3% (4h wma75 ambos, 363 tr) | +5.4% |
| Multi-MA (4MA) | XAU | 20 | 5 | 0 | 0 | +2.8% (4h wma75 ambos, 318 tr) | +13.4% |
| Awesome Oscillator | BTC | 10 | 5 | 0 | 0 | +8.6% (1D long, 210 tr) | +43.8% |
| Awesome Oscillator | ETH | 10 | 7 | 0 | 0 | +23.7% (1D long, 203 tr) | +56.5% |
| Awesome Oscillator | US100 | 10 | 5 | 0 | 0 | +6.6% (1D long, 183 tr) | +20.2% |
| Awesome Oscillator | WTI | 10 | 1 | 0 | 0 | +2.5% (4h ambos, 2535 tr) | +5.4% |
| Awesome Oscillator | XAU | 10 | 2 | 1 | 0 | +0.8% (4h ambos, 2003 tr) | +13.4% |
| Smart Money Pivot | BTC | 45 | 40 | 2 | 0 | +43.3% (1D p5 sl0% tp0.0% ambos, 78 tr) | +43.8% |
| Smart Money Pivot | ETH | 45 | 44 | 15 | 6 | +130.3% (15min p20 sl0% tp0.0% ambos, 1944 tr) | +56.8% |
| Smart Money Pivot | US100 | 44 | 32 | 0 | 0 | +7.2% (30min p20 sl1 tp1.5 ambos, 1157 tr) | +20.3% |
| Smart Money Pivot | WTI | 45 | 6 | 0 | 1 | +9.9% (4h p20 sl0% tp0.0% ambos, 113 tr) | +5.4% |
| Smart Money Pivot | XAU | 44 | 38 | 5 | 0 | +12.9% (1h p5 sl0% tp0.0% ambos, 1386 tr) | +13.4% |

## Robustez (CAGR vs B&H)

| Célula | Tudo | Terço 1 | Terço 2 | Terço 3 | 2ª metade | Custo 4× | Veredito |
|---|---|---|---|---|---|---|---|
| **Chandelier Exit ETH 30m (com stop/alvo, ambos)** | +153% vs +57% | +408% vs +330% | +95% vs +1% | +59% vs −11% | +47% vs +13% | +118% | **aprovada com ressalva** |
| **Triangular Hull MA ETH 15m (THMA100, ambos)** | +155% (t 4,3) | +338% vs +330% | +157% vs +1% | +33% vs −11% | +41% vs +13% | +117% | **aprovada com ressalva** (terço 1 por pouco) |
| **Smart Money Pivot ETH 15m (pivô 20, sem stop/alvo)** | +130% (t 3,8) | +355% vs +330% | +24% vs +1% | +110% vs −11% | +61% vs +13% | +111% | **aprovada com ressalva** |
| **Swing HULL + T3 ETH 1h (100)** | +115% (t 3,8) | +403% vs +330% | +51% vs +1% | +23% vs −11% | +29% vs +13% | +101% | **aprovada com ressalva** |
| THMA ETH 30m (40) / BEST Trailing ETH 30m / BEST ATR Stop ETH 15m / Ichimoku+MACD/CMF/TSI ETH 30m | +132 / +121 / +117 / +111% | **perdem** (+289 / +249 / +185 / +286% vs +330%) | ganham | ganham | ganham | +91 / +92 / +64 / +98% | quase (terço 1) |
| EMA Cross + RSI + ADX BTC 4h (stop 5%) | +53% vs +44% (Sh 0,93) | **+91% vs +129%** | +54% vs +15% | +18% vs +14% | +46% vs +40% | +51% | quase (terço 1) |
| Trendline Breakout WTI 4h (sem filtro) | +32% vs +5% (Sh 0,91) | +28% vs −21% | **+31% vs +40%** | +15% vs +8% | +28% vs +3% | +26% | quase (terço 2) |
| Stoch + ATR WTI 4h (14) | +35% vs +5% | +36% vs −21% | +73% vs +40% | **+5,3% vs +7,6%** | +29% vs +3% | +27% | quase (terço 3) |
| FlexiSuperTrend WTI 15m | +30% | ganha | ganha | **perde** | **−3% vs +4%** | +8% | reprovada |
| Pivot of Pivot BTC 4h / Grover BTC 30m / BEST ATR Stop BTC 30m | +73 / +65 / +63% | ganha / ganha / perde | ganham | +13 / −10 / +29% vs +13% | **perdem** (+29 / +28 / +40% vs +40%) | +73 / +41 / +42% | reprovadas |
| Support Resistance XAU 1h | +15,9% vs +13,4% | ganha | ganha | **perde** | **perde** | **+9% vs +13%** | reprovada |

## Conclusões

- **Quatro aprovadas, todas no ETH e todas seguidoras de tendência:** Chandelier Exit 30m, Triangular Hull MA 15m, Smart Money Pivot 15m (rompimento de pivô 20/20, sem stop nem alvo) e Swing HULL + T3 1h. Todas passam nos três terços, na 2ª metade e com custo 4×, mas o terço 1 (alta de 2020-22) passa por pouco, fazem de 290 a 530 trades por ano e devem ser muito correlacionadas entre si e com as aprovadas anteriores do ETH. Na prática são variações da mesma aposta: seguir a tendência do ETH no intradiário.
- **ETH:** mais quatro quase (THMA 30m, BEST Trailing, BEST ATR Stop e Ichimoku + MACD/CMF/TSI), todas perdendo só o terço 1.
- **BTC:** EMA Cross + RSI + ADX 4h é a melhor fora do ETH (Sharpe 0,93, robusta a custo), mas perde o terço 1. **WTI:** Trendline Breakout e Stoch + ATR ganham do B&H fraco com folga, mas cada uma perde um terço. **XAU e US100:** nada robusto.
