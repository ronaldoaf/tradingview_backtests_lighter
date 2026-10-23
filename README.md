# tradingview_backtests_lighter

Infraestrutura de backtest para reproduzir, com custo real da **Lighter**, estratégias
publicadas no [TradingView](https://www.tradingview.com/scripts/). Cada estudo reimplementa
o Pine Script em Python/NumPy, roda uma grade de parâmetros em vários timeframes e compara
o resultado contra dois benchmarks: **buy & hold** e um **controle aleatório** com o mesmo
lado, a mesma duração e a mesma gestão de saída.

Resultado até agora: **nenhuma das 41 estratégias testadas passou**. As candidatas são o
**Trailing SL [QuantNomad] no ouro** (ver [LOTE7_TV](docs/LOTE7_TV.md)) e o **Pivot Point SuperTrend no ETH** (ver [LOTE4_TV](docs/LOTE4_TV.md)), ainda dependente de medir o custo real do ETH. Os relatórios em
[`docs/`](docs/) explicam o motivo de cada reprovação — o que costuma ser mais útil que o
veredito, porque o mesmo punhado de falhas se repete (sempre-no-mercado disfarçado de
sinal, `lookahead_on`, risco/retorno impossível por construção, ilha de parâmetros que
morre no out-of-sample).

Lista das candidatas aprovadas: [docs/APROVADAS.md](docs/APROVADAS.md).

## Protocolo de teste

1. A partir do lote 12, toda estratégia é testada nos **5 ativos** (XAU, US100, WTI, BTC, ETH).
   Até o lote 11 o ouro vinha primeiro e só quem passava nele era estendido aos outros 4.
2. Sinal no **fechamento** da barra, ordem na **abertura da barra seguinte**
   (equivalente a Pine com `calc_on_every_tick=false`). Stops e alvos intrabar são
   resolvidos no M1; quando stop e alvo caem no mesmo minuto, **o stop executa primeiro**.
3. Custo por perna = spread medido na Lighter (`CUSTO`) + funding anual pro-rata que o long
   paga (`FUND`). Ambos em `scripts/study_engulf_psar.py`.
4. Toda estratégia é comparada contra buy & hold **e** contra entrada aleatória de mesmo
   lado/duração. Uma célula de grade só interessa se bate os dois.
5. Quem sobrevive à grade ainda passa por robustez: terços do período, out-of-sample e
   multiplicador de custo.

## Layout

| Pasta | Conteúdo |
| --- | --- |
| `scripts/` | Os estudos (`study_*.py`) e a infra comum (`tvlib.py`) |
| `docs/` | Um relatório Markdown por estratégia/lote, com veredito e diagnóstico |
| `results/` | Saídas brutas: grades (`*_grid.csv`), trades (`*_trades.csv`), logs (`*.txt`) |
| `pine/` | Fontes Pine baixadas por `scripts/tv_fetch.py` |
| `data/` | Candles de 1 minuto em Parquet (zstd) — ver abaixo |

## Dados

Candles de **1 minuto**, dos quais todos os timeframes são agregados em memória
(`tvlib.resample`). Nada é baixado em tempo de execução.

| Ativo | Caminho | Período | Linhas | Fonte |
| --- | --- | --- | --- | --- |
| XAU (ouro) | `data/gold/xau_1m.parquet` | 2017-09-01 → 2026-10-04 | 2,66 M | Dukascopy (bid) |
| US100 (Nasdaq) | `data/duka1m_us100/all.parquet` | 2017-01-05 → 2026-08-31 | 2,69 M | Dukascopy (bid) |
| WTI (petróleo) | `data/duka1m_wti/all.parquet` | 2017-01-03 → 2026-09-30 | 3,24 M | Dukascopy (bid) |
| BTC | `data/binance/klines_1m/BTCUSDT.parquet` | 2020-01-01 → 2026-09-30 | 3,55 M | Binance perp |
| ETH | `data/binance/klines_1m/ETHUSDT.parquet` | 2020-01-01 → 2026-09-30 | 3,55 M | Binance perp |

Os arquivos da Dukascopy foram consolidados num único Parquet por ativo (eram ~2,5 mil
arquivos mensais) e tudo foi recomprimido em zstd para caber no limite de 100 MB por
arquivo do GitHub. Total ≈ 265 MB.

Os de índice (ouro/US100/WTI) vêm indexados por `DatetimeIndex` UTC com colunas
`open/high/low/close[/volume]`; os da Binance vêm com `ts` em milissegundos e colunas
`o/h/l/c/v`. `tvlib.load_m1v(nome)` normaliza os dois formatos.

## Como rodar

```bash
pip install -r requirements.txt
cd scripts
python study_rsidiv.py xau            # um ativo
python study_tvlote3.py xau us100 btc # vários
```

Cada script aceita a lista de ativos (`xau us100 wti btc eth`) como argumentos; sem
argumento rodam no ouro. A raiz do repositório é descoberta a partir do próprio arquivo;
para apontar os dados para outro lugar, defina `EDGE_ROOT`.

As grades são pesadas (dezenas de milhões de barras × centenas de combinações) e usam
`numba`. A primeira execução paga a compilação JIT; contar em minutos, não segundos.

## Infra comum (`scripts/tvlib.py`)

- `load_m1v` / `resample` — carrega o M1 com volume e agrega para qualquer timeframe.
- `rsi_wilder`, `mfi`, `hma`, `sma`, `stdev_pop`, `atr_rma` — equivalentes exatos dos
  `ta.*` do Pine v4/v5. Reimplementados porque as versões "óbvias" do pandas diferem do
  Pine na inicialização (Wilder vs. média simples) e isso muda o sinal.
- `engine_bars` — posição por sinal, execução na abertura da barra seguinte, sem stop
  intrabar.
- `engine_sltp` — long com stop/alvo percentuais resolvidos no M1.
- `stats` / `control` — CAGR vs. buy & hold, Sharpe, drawdown, exposição, e o controle
  aleatório de mesmo lado/duração/gestão.

Os estudos mais antigos (`study_goldtrail`, `study_tlangle`, `study_macdconf`,
`study_bbrsi`, `study_macdsma`, `study_commas`, `study_flipma`, `study_serdar`) foram
escritos antes do `tvlib` e carregam o próprio `load_m1`/`resample`, encadeados por import
(`study_flipma` importa de `study_commas`, e assim por diante). `study_engulf_psar.py` está
aqui porque é onde vivem as constantes `CUSTO` e `FUND`, importadas por todos.

## Estratégias testadas

Todas reprovadas, exceto a candidata indicada. Ordem cronológica inversa.

| # | Estratégia (autor, id do script) | Doc | Diagnóstico |
| --- | --- | --- | --- |
| 263 | Smart Money Pivot (`IMTwV7U8`) | [LOTE25_TV](docs/LOTE25_TV.md) | **aprovada: ETH 15m (sem stop/alvo)** |
| 262 | Awesome Oscillator (`fSHXMVey`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 261 | Multi-MA (4MA) (`C1hyNDWO`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 260 | Reversal Trading Bot (`cXVnf1WH`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 259 | NR7ID (short-only) (`abjeWQD5`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 258 | BEST ATR Stop Multiple (`UA83Q4Je`) | [LOTE25_TV](docs/LOTE25_TV.md) | ETH 15m quase (terço 1); BTC reprovada |
| 257 | Double Bottom/Top Hunter (`tkyuZRbN`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 256 | Fractal Breakout (`Mwu4JMaQ`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 255 | Trendline Breakout KedArc (`grMQIRAr`) | [LOTE25_TV](docs/LOTE25_TV.md) | WTI 4h quase (terço 2) |
| 254 | Gianno Nano (`M7e4uwLN`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 253 | KPL Swing (`4mz6xvnK`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 252 | SPY Master (`4c9zIvHX`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 251 | Stoch + ATR (`OK4OIiJ2`) | [LOTE25_TV](docs/LOTE25_TV.md) | WTI 4h quase (terço 3) |
| 250 | TASC One Percent A Week (long-only) (`nVECqIQx`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 249 | Swing HULL + T3 (`YgRqvCGx`) | [LOTE25_TV](docs/LOTE25_TV.md) | **aprovada: ETH 1h (100)** |
| 248 | Uhl MA System (`4S9Yz3DB`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 247 | MACD + CCI (`l7eeKNis`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 246 | Trend Reversal Alerts (long-only) (`2DxTUzED`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 245 | Multi-X (long-only) (`LZ1KzR4f`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 244 | EMA Cross + RSI + ADX (`e7XQPek8`) | [LOTE25_TV](docs/LOTE25_TV.md) | BTC 4h quase (terço 1) |
| 243 | Stoch/EMA Cross (`PPKWNyyw`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 242 | VWAP Breakout (`39HGmmqK`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 241 | Grover Llorens Activator (`VuYM89Tw`) | [LOTE25_TV](docs/LOTE25_TV.md) | BTC 30m reprovada |
| 240 | MA Scalper Coinrule (long-only) (`PfBSgqMw`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 239 | Davin 10/200 MA Pullback (long-only) (`Gkib6KgL`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 238 | RSI mensal (long-only) (`rHDrnos6`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 237 | BEST Trailing Stop (`NOGqbIcu`) | [LOTE25_TV](docs/LOTE25_TV.md) | ETH 30m quase (terço 1) |
| 236 | Mov Avg Speed (3 sinais) (`pCxvfqFv`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 235 | Pivot of Pivot Reversal (`mXygJWkv`) | [LOTE25_TV](docs/LOTE25_TV.md) | BTC 4h reprovada (51 trades, perde 2023-26) |
| 234 | Mutanabby AI Algo Pro (long-only) (`t3UuM5DI`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 233 | EMA Long Only (`yeBIG7oZ`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 232 | RSI Bull Div (long-only) (`NC603cui`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 231 | Combo 123 Reversal + RSI (`IuTkaU1w`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 230 | Hybrid RSI + Breakout (`aAszLZWi`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 229 | Ichimoku + MACD/CMF/TSI (`Pjsgs9JO`) | [LOTE25_TV](docs/LOTE25_TV.md) | ETH 30m quase (terço 1) |
| 228 | Forex Fractal EMA Scalper (`pgsJGhIg`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 227 | Range Strat MACD/RSI (`XWgu79vU`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 226 | Dynamic RSI Momentum (`08eSyDlq`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 225 | State-aware MA Cross (long-only) (`FgwP9BhA`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 224 | Master Supertrend (`YexkkFy8`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 223 | DAX Shooter (`CfgKji30`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 222 | Triangular Hull MA (`gMeYb8Dp`) | [LOTE25_TV](docs/LOTE25_TV.md) | **aprovada: ETH 15m (THMA100)** |
| 221 | Moon Phases (`BAc77VfD`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 220 | CMO TradeDots (`MNBZqC72`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 219 | Hull MA TimeFrame CrossOver (`KdC6xqb8`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 218 | FlexiSuperTrend (`y9noW915`) | [LOTE25_TV](docs/LOTE25_TV.md) | WTI 15m reprovada |
| 217 | MA Displaced Envelope + ATRTS (`n45eXKBG`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 216 | Support Resistance (`6GeSAYfE`) | [LOTE25_TV](docs/LOTE25_TV.md) | XAU 1h reprovada |
| 215 | Bollinger Bands Enhanced (long-only) (`V4B5nKIx`) | [LOTE25_TV](docs/LOTE25_TV.md) | nada robusto |
| 214 | Chandelier Exit (`yca6gmSk`) | [LOTE25_TV](docs/LOTE25_TV.md) | **aprovada: ETH 30m** |
| 213 | AlphaTrend (`uvkI3QJC`) | [LOTE24_TV](docs/LOTE24_TV.md) | BTC 30m reprovada |
| 212 | EMA Crossover with TP (`B7umqU7W`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 211 | Bullish Engulfing [Quant Science] (`0moOi6G5`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada acima do B&H |
| 210 | VWAPStrategy (`t1lk7Uvk`) | [LOTE24_TV](docs/LOTE24_TV.md) | **aprovada: ETH 30m** (ressalva forte: custo) |
| 209 | VWMA/SMA 3Commas (`cH5Tjlns`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada acima do B&H |
| 208 | Combo 123 Reversal & Statistical Volatility (`3w6l57bw`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada (o filtro de volatilidade quase nunca vira) |
| 207 | Low-High Trend (`o97hSCY4`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada acima do B&H |
| 206 | DEMA 8/20/63 (`AbRhwDeX`) | [LOTE24_TV](docs/LOTE24_TV.md) | ETH 4h quase (terço 1) |
| 205 | Hull Fisher (`QTYaYuX7`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 204 | Bitcoin Momentum (`Tce7SnL7`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada acima do B&H |
| 203 | Gap Filling (`ghocsiv7`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada (quase não há gaps fora do WTI) |
| 202 | Donchian free bot (`KZuFvEYa`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 201 | SMC (`Zcf69Yqd`) | [LOTE24_TV](docs/LOTE24_TV.md) | WTI 15m reprovada |
| 200 | Stochastic RSI + RVI (`22FnhBk9`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 199 | HMA50 + Supertrend (`3SHJZytF`) | [LOTE24_TV](docs/LOTE24_TV.md) | ETH 30m quase (terço 1) |
| 198 | SuperTrend Backtester (`GMZLB374`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 197 | Triple EMA + QQE [TradeDots] (`M4y5HT3h`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada acima do B&H |
| 196 | Mbit MA (`hXrtpUdS`) | [LOTE24_TV](docs/LOTE24_TV.md) | nada robusto |
| 195 | BEST Supertrend (`6knHPR6c`) | [LOTE24_TV](docs/LOTE24_TV.md) | **aprovada: ETH 1h ambos** (com ressalva) |
| 194 | SOTT (`cJhpIJ2w`) | [LOTE24_TV](docs/LOTE24_TV.md) | WTI 30m reprovada (perde 2023-26) |
| 193 | VWAP Momentum Pullback (`uhdaobby`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada acima do B&H |
| 192 | EVWMA VWAP Cross [QuantNomad] (`QPIGo8hs`) | [LOTE23_TV](docs/LOTE23_TV.md) | BTC 4h perde 2024-26 |
| 191 | Trend Trader Strategy with MACD (`dUNRiEBG`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada robusto |
| 190 | RSI Strategy [PrimeAutomation] (`RiQzLLoh`) | [LOTE23_TV](docs/LOTE23_TV.md) | ETH 4h quase (terço 1, 64 trades) |
| 189 | Super trend V (`7g8MF7f7`) | [LOTE23_TV](docs/LOTE23_TV.md) | **candidata: ETH 15m** (+146% vs +57%) |
| 188 | Buying Dip with TP/SL (racer8) (`AHxkEMXm`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada acima do B&H |
| 187 | Combo 123 Reversal & SMI (`NudssmJx`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada robusto |
| 186 | Crypto ZigZag RSI 15min (`LhpfQMtP`) | [LOTE23_TV](docs/LOTE23_TV.md) | BTC 15m quase (perde o terço 1) |
| 185 | MA 10/20 Crossover (`2cbpO8lO`) | [LOTE23_TV](docs/LOTE23_TV.md) | XAU marginal, morre no custo 4x |
| 184 | Triple EMA Trend ADX/ATR (`vzXlqRCT`) | [LOTE23_TV](docs/LOTE23_TV.md) | ETH 15m quase (terço 1); BTC 4h perde 2024-26 |
| 183 | TradeIQ Crazy Scalping (Kaspricci) (`R7OSA2ar`) | [LOTE23_TV](docs/LOTE23_TV.md) | WTI 1h perde 2023-26 |
| 182 | MA Bollinger Bands + RSI (`2MMNHl97`) | [LOTE23_TV](docs/LOTE23_TV.md) | poucos trades, nada acima do B&H |
| 181 | DEMA ATR [PrimeAutomation] (`rqRd3f62`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada robusto |
| 180 | [UL] QQE Cross v1.1 (`nkka4EfU`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada robusto |
| 179 | Maximized Scalping On Trend (Coinrule) (`XAiEh7nb`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada acima do B&H |
| 178 | NR7 + Inside Day (ChartArt) (`Dln4aFaM`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada acima do B&H |
| 177 | HIGHER HIGH LOWER LOW (`JWsBrWBu`) | [LOTE23_TV](docs/LOTE23_TV.md) | BTC 4h acima do B&H com poucos trades |
| 176 | 3 EMA + RSI with Trail Stop (`mgD7xBuw`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada acima do B&H |
| 175 | BBTrend w SuperTrend decision (`7C1kIEOn`) | [LOTE23_TV](docs/LOTE23_TV.md) | nada robusto (WTI 30m isolada) |
| 174 | Twin Range Filter Algo v.3 (`ZsiaNicR`) | [LOTE23_TV](docs/LOTE23_TV.md) | ETH 4h quase (perde o terço 1 e o custo 4x) |
| 173 | Breakout Trend Follower (`9uvZIPnH`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH 30m quase (terço 1) |
| 172 | Cumulative RSI Strategy (`nI9Csm8g`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada acima do B&H |
| 171 | Tripple super Trend Strategy (`aCbQTE0W`) | [LOTE22_TV](docs/LOTE22_TV.md) | BTC 1h +63%, isolada |
| 170 | Volatility based force trade scalper (`FN3ZkHZA`) | [LOTE22_TV](docs/LOTE22_TV.md) | BTC 4h perde a 2ª metade |
| 169 | PMax on Rsi w T3 (`ZLcmWQtj`) | [LOTE22_TV](docs/LOTE22_TV.md) | XAU 30m perde terços e custo 4x |
| 168 | XAUUSD Scalping V2 AGRESIV (`5q4PsY3a`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada robusto (ETH só sem TP/SL) |
| 167 | Parabolic SAR on close [QuantNomad] (`gK7skk6m`) | [LOTE22_TV](docs/LOTE22_TV.md) | XAU 4h perde o terço 2 |
| 166 | Highest High and Lowest Low Channel (`1SMJivyk`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada acima do B&H |
| 165 | Renko Strategy V2 (`oAlFKwej`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH 1h +90%, perde o terço 1 |
| 164 | Moving Average Band (`wwi02rpz`) | [LOTE22_TV](docs/LOTE22_TV.md) | **candidata: WTI 4h** (+27% vs +5%, lucro do lado vendido) |
| 163 | Slopes (`XBgfW9k9`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH 4h +116% quase (terço 1); BTC perde a 2ª metade |
| 162 | Turtle trading Donchian/ATR (`gbxblhGl`) | [LOTE22_TV](docs/LOTE22_TV.md) | WTI short quase (perde o terço 2020-23) |
| 161 | Ichimoku no offset + RSI (`MGSCiuSP`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH 15m +75%, isolada |
| 160 | ATR Parabolic SAR [QuantNomad] (`LKfHdoNv`) | [LOTE22_TV](docs/LOTE22_TV.md) | BTC 4h long perde a 2ª metade |
| 159 | Real Turtle (`67fpKimh`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH 1D +86%, perde o terço 1 |
| 158 | TSI CCI Hull with profit (`qwN8CGrU`) | [LOTE22_TV](docs/LOTE22_TV.md) | WTI/XAU 15m acima do B&H, perde terços e custo 4x |
| 157 | Easy to Use MACD + RSI (`06gU5i7b`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada acima do B&H |
| 156 | EWO RSI advanced Signals (`B7MQqWes`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada acima do B&H |
| 155 | EMA Crossover Strategy (`sxJejjdy`) | [LOTE22_TV](docs/LOTE22_TV.md) | ETH: 18 células acima do B&H, todas perdem o terço 1 |
| 154 | Forex Scalping BB + RSI + ADX (`sR1hePBi`) | [LOTE22_TV](docs/LOTE22_TV.md) | nada acima do B&H com t > 1 (WTI 4h +9%, 81 trades) |
| 153 | Multi Timeframe RSI [TradeDots] (`kfj6EdjQ`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 152 | Super Guppy Strategy (`vPStjyWz`) | [LOTE21_TV](docs/LOTE21_TV.md) | ETH 30m +98% perde o terço 1 |
| 151 | MACD + Stochastic + RSI (`2BIMZDGk`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 150 | RSI Binary Strategy (`1jTE6hJz`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 149 | LUBE (`i9tJOtjl`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 148 | Keltner bounce from border (`mQKGzLMD`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada robusto |
| 147 | Renko Strategy Open_Close (`e6mDSPPe`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 146 | Liquidity Sweep Filter [AlgoAlpha] (`gx7267BR`) | [LOTE21_TV](docs/LOTE21_TV.md) | ETH 1h +101% perde o terço 1; BTC 1h morre em 2024-26 |
| 145 | 5min MACD scalp by Joel (`qN11DuKy`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 144 | Bollinger Bands - Breakout (`sTFw2fOj`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada robusto |
| 143 | MACD + BB + RSI [Alorse] (`6xo9yMmT`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 142 | Gold-Silver 30m Only (`lx4O1PPu`) | [LOTE21_TV](docs/LOTE21_TV.md) | WTI 4h +75% (todos os terços) com só 52 trades: quase |
| 141 | BB+AO STRAT (`ibq1TYLX`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 140 | ATR Strategy Back-test (`DW1GWSWQ`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada robusto |
| 139 | SuperTREX strategy (`K3U9opwQ`) | [LOTE21_TV](docs/LOTE21_TV.md) | BTC 1h +83% (18 células > B&H) mas perde em 2024-26 |
| 138 | Hulk Scalper x35 (`oGUYuz4N`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 137 | RSI Trend Crypto (`Ru7qOVtp`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada acima do B&H |
| 136 | Moving Average Consecutive Up/Down (ChartArt) (`7KXy9NNJ`) | [LOTE21_TV](docs/LOTE21_TV.md) | **ETH 4h aprovada com ressalva** (+134% vs +57%, todos os terços, custo 4×) |
| 135 | Squeeze Momentum Strategy v2 (`lEQZl0vE`) | [LOTE21_TV](docs/LOTE21_TV.md) | nada robusto |
| 134 | Trend Surfers - Premium Breakout (`w91kwvnX`) | [LOTE21_TV](docs/LOTE21_TV.md) | ETH 4h (55) +100% mas perde o terço 1 |
| 133 | World Cycle ATH/ATL Logarithmic (`824WmIi7`) | [LOTE20_TV](docs/LOTE20_TV.md) | poucos trades; nada acima do B&H |
| 132 | FRAMA Supertrend strategy (`y81orwSC`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células robustas acima do B&H |
| 131 | [DS] Entry_Exit TRADE V01 (`RO4rB2HF`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH/BTC 30m acima do B&H no total mas morrem em 2024-26; WTI 1h falha no custo 4× |
| 130 | ATR GOD Strategy (`Je04kGO0`) | [LOTE20_TV](docs/LOTE20_TV.md) | WTI 1D com só 32 trades; reprovada |
| 129 | PMARP + Madrid MA Ribbon (`T4rBZCvC`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH 15m +94% mas perde na 2ª metade |
| 128 | Y-Profit Maximizer (Y-PMax) (`6ZFa2t7o`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH 15m/30m +122%/+133% mas perde o terço 1: quase |
| 127 | Extreme Scalping (`qVTgdPBT`) | [LOTE20_TV](docs/LOTE20_TV.md) | nada com t > 0 acima do B&H |
| 126 | Nadaraya-Watson Envelope Strategy (`HrZicISx`) | [LOTE20_TV](docs/LOTE20_TV.md) | WTI 1D +22% mas perde em 2020-23 e na 2ª metade |
| 125 | CamarillaStrategy V1 (`tBJNISwj`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células robustas acima do B&H |
| 124 | Scalping with Bill Williams Alligator (`b2ShO5Fv`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células acima do B&H |
| 123 | RSI and ATR Trend Reversal SL/TP (`hZLgJ29l`) | [LOTE20_TV](docs/LOTE20_TV.md) | XAU 30m empata com o B&H; reprovada |
| 122 | Double AI Super Trend (`hLZPT7it`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH acima do B&H no total; não passou na grade |
| 121 | Moving Regression Band Breakout (`Tls8Y2hc`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH/BTC acima do B&H só no total; não passou na grade |
| 120 | RSI-Adaptive T3 & SAR (`bldXp6gY`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células robustas acima do B&H |
| 119 | 3x SuperTrend Strategy (Mel0nTek) (`FUnOi1Nx`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células robustas acima do B&H |
| 118 | MACD Strategy with trailing ATR stop (`2jDHQAJc`) | [LOTE20_TV](docs/LOTE20_TV.md) | BTC 30m +65% mas morre em 2024-26 |
| 117 | Strategy Follow Line MTF (`6lhyIPGA`) | [LOTE20_TV](docs/LOTE20_TV.md) | **ETH 30m (21, 1 desvio) aprovada**: +118% vs +57%, todos os terços, custo 4× |
| 116 | 3C QFL Mean reversal (`SDRM0bBY`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células acima do B&H (sem DCA) |
| 115 | ATR Trailing Stop by ceyhun (`cj3MJWNz`) | [LOTE20_TV](docs/LOTE20_TV.md) | ETH 4h +103% mas perde o terço 1: quase; BTC perde na 2ª metade |
| 114 | Keltner Channel ETH/USDT 1H (`ezSBm5MS`) | [LOTE20_TV](docs/LOTE20_TV.md) | 0 células robustas acima do B&H |
| 113 | Cipher B+ Divergence EMA Pullback (`ywcSiaaV`) | [LOTE19_TV](docs/LOTE19_TV.md) | quase não opera; nenhum ativo acima do B&H |
| 112 | 3EMA (`9bA3Z56w`) | [LOTE19_TV](docs/LOTE19_TV.md) | 0 células acima do B&H |
| 111 | UT Bot v2 (`lDGmh7ou`) | [LOTE19_TV](docs/LOTE19_TV.md) | ETH 30m ATR×3 +107% mas perde o terço 1 e t < 2: quase |
| 110 | HHLL Strategy (`CRNp5xev`) | [LOTE19_TV](docs/LOTE19_TV.md) | ETH 1h +97% (t 2,5), perde só o terço 1: quase |
| 109 | BEST ABCD Pattern Strategy (`TWSr0hGH`) | [LOTE19_TV](docs/LOTE19_TV.md) | **BTC 1h SL 4% RR 5 aprovada com ressalva** (+70% vs +44%, todos os terços, custo 4×); WTI 4h morreu em 2023-26 |
| 108 | Liquidity Sweep Reversal (`GoeqO1ev`) | [LOTE18_TV](docs/LOTE18_TV.md) | 0 células acima do B&H fora do WTI |
| 107 | EMA Slope Trend Follower (`TKg40Ska`) | [LOTE18_TV](docs/LOTE18_TV.md) | ETH 30m +85% mas empata com custo 4×; BTC perde na 2ª metade |
| 106 | [RS] Open Session Breakout Trader (`mIvVYU42`) | [LOTE18_TV](docs/LOTE18_TV.md) | 0 células acima do B&H fora do WTI |
| 105 | Dynamic Swing Anchored VWAP STRATEGY (`gjFSGRCo`) | [LOTE18_TV](docs/LOTE18_TV.md) | ETH 1D +89% com 26 trades; resto abaixo do B&H |
| 104 | [BACKTEST] Traders Dynamic Index (`rDZ0Id1U`) | [LOTE18_TV](docs/LOTE18_TV.md) | XAU 1h +18,5% (DD −25%) mas só em 2024-26 e célula isolada; ETH 4h quase |
| 103 | Wolfe Strategy (`EGvQ2nLb`) | [LOTE17_TV](docs/LOTE17_TV.md) | ignorado (sem ordens) |
| 102 | Band-Zigzag TrendFollower (`9FsHYtrq`) | [LOTE17_TV](docs/LOTE17_TV.md) | ETH 1h +123% mas terço do meio ≈ 0 |
| 101 | HULLTSIBOT (`gf21APTn`) | [LOTE17_TV](docs/LOTE17_TV.md) | ETH 30m e WTI 1h passam nos testes, mas só na célula 100/50; vizinhos negativos |
| 100 | FTSMA (`wffJotUo`) | [LOTE17_TV](docs/LOTE17_TV.md) | **candidata no ETH 30m** (+149%, passa terços, 2ª metade e custo 4×; vizinhança boa); BTC quase |
| 99 | Grid Like Strategy (`oxvR5vMy`) | [LOTE17_TV](docs/LOTE17_TV.md) | nenhuma célula robusta; t ≈ 0 |
| 98 | ZigZag PA Strategy V4 (`DYONEypp`) | [LOTE17_TV](docs/LOTE17_TV.md) | ignorado (repetido e com lookahead) |
| 97 | Best Supertrend CCI (`YsWWsOGs`) | [LOTE17_TV](docs/LOTE17_TV.md) | ETH 30m +133% mas empata com o B&H com custo 4× |
| 96 | SMA (`soKH38lY`) | [LOTE17_TV](docs/LOTE17_TV.md) | ignorado (sem ordens) |
| 95 | EDMA Scalping Strategy (`CJesxF5m`) | [LOTE16_TV](docs/LOTE16_TV.md) | quase no WTI 1D (+64%, passa terços) mas só 53 trades e t 1,6; ETH perde no 1º terço |
| 94 | EMA Cross Strategy (`fAxX6kbm`) | [LOTE16_TV](docs/LOTE16_TV.md) | o 50/200 bate o B&H do ETH (+111%), mas 2ª metade fraca; serve de referência para as candidatas do ETH |
| 93 | Stepped trailing strategy example (`jjhUHcje`) | [LOTE16_TV](docs/LOTE16_TV.md) | ignorado (exemplo) |
| 92 | Strategy Designer (`Hp05f5Dq`) | [LOTE16_TV](docs/LOTE16_TV.md) | ignorado (template) |
| 91 | Ultimate Strategy Template (`XIJrNXQc`) | [LOTE16_TV](docs/LOTE16_TV.md) | ignorado (template) |
| 90 | DCA Bot Long/Short (`LTcMeU50`) | [LOTE16_TV](docs/LOTE16_TV.md) | ignorado (utilitário) |
| 89 | AI Volume SuperTrend (`eaTIyEty`) | [LOTE16_TV](docs/LOTE16_TV.md) | ETH 4h +103% mas terço do meio negativo |
| 88 | Profit Maximizer PMax (`7yn5dteO`) | [LOTE16_TV](docs/LOTE16_TV.md) | BTC e XAU perto do B&H; 2ª metade abaixo |
| 87 | [Backtest] QQE Cross v6.0 (`H0TR67ED`) | [LOTE16_TV](docs/LOTE16_TV.md) | só WTI acima do B&H; melhor ETH +59% ≈ B&H |
| 86 | BTC bot (`DPBeZbMP`) | [LOTE15_TV](docs/LOTE15_TV.md) | 0 células acima do B&H; melhor +17% a.a. (US100) |
| 85 | Crypto BOT lower timeframes (`IS7yz9s4`) | [LOTE15_TV](docs/LOTE15_TV.md) | 0 células acima do B&H |
| 84 | AUTOMATIC GRID BOT (`6qZpzElZ`) | [LOTE15_TV](docs/LOTE15_TV.md) | ignorado (utilitário) |
| 83 | Autoview Build-a-bot (`iVHq4EFG`) | [LOTE15_TV](docs/LOTE15_TV.md) | ignorado (template) |
| 82 | Trendline Breaks Multi Fibonacci Supertrend (`aVzNdTMg`) | [LOTE15_TV](docs/LOTE15_TV.md) | quase no ETH 4h (+100%, custo 4× ok) mas perde no 1º terço; WTI falha no último terço |
| 81 | Fixed Percent SL/TP (`00WHGEoc`) | [LOTE15_TV](docs/LOTE15_TV.md) | ignorado (exemplo) |
| 80 | Simple profitable trading strategy (`QoNKoXwW`) | [LOTE15_TV](docs/LOTE15_TV.md) | ETH 15m +89% mas empata com o B&H com custo 4× |
| 79 | [RS] Spot/Binary Scalper V0 (`PMqutqKQ`) | [LOTE15_TV](docs/LOTE15_TV.md) | XAU 30m +14,8% mas perde com custo 2×; ETH perde com custo 4× |
| 78 | HullMA Strategy (`qQ0MJCVL`) | [LOTE14_TV](docs/LOTE14_TV.md) | substituto do V Pattern; ETH 30m n100 +151% mas 2ª metade fraca (t 1,7) |
| 77 | Delta-RSI with filters (`0OdCms2T`) | [LOTE14_TV](docs/LOTE14_TV.md) | quase no ETH (+168%, 2022-26 muito acima do B&H) mas perde no 1º terço; BTC falha na 2ª metade; WTI célula isolada |
| 76 | Forex Master v4.0 (`AIZqyS45`) | [LOTE14_TV](docs/LOTE14_TV.md) | só WTI acima do B&H; melhor +16% a.a. |
| 75 | V Bottom/V Top Pattern [Misu] (`6qmzhNzi`) | [LOTE14_TV](docs/LOTE14_TV.md) | ignorado: ordens comentadas, não opera |
| 74 | Heikin-Ashi PSAR [QuantNomad] (`0iKy7lyG`) | [LOTE14_TV](docs/LOTE14_TV.md) | XAU 1h empata com o B&H e perde com custo 2× |
| 73 | Crypto Scalper (`84YDnJ9V`) | [LOTE14_TV](docs/LOTE14_TV.md) | ETH 15m +110% mas terço do meio ≈ 0 |
| 72 | Ichimoku Kinko Hyo Basic (`XZcsLIEW`) | [LOTE13_TV](docs/LOTE13_TV.md) | **candidata no ETH 15m** (20/60/120): passa terços, 2ª metade e custo 4×; DD −90% |
| 71 | Squeeze Momentum [LazyBear] (`qp9BoNyS`) | [LOTE13_TV](docs/LOTE13_TV.md) | nenhuma célula acima do B&H fora do WTI (e lá com DD enorme) |
| 70 | UT Bot v5 (`2wkJx7Ix`) | [LOTE13_TV](docs/LOTE13_TV.md) | **candidata no ETH 30m** (a=5, long/short); BTC falha no último terço |
| 69 | Scalping Trading System (`YotdMm0M`) | [LOTE13_TV](docs/LOTE13_TV.md) | **candidata no ETH 30m**; BTC 1D com 54 trades e t baixo |
| 68 | Fibonacci + RSI (`Ouv7XVfc`) | [LOTE13_TV](docs/LOTE13_TV.md) | 0 células acima do B&H em 4 ativos; melhor +11% a.a. |
| 67 | Solution Zigma (`k1GLeZco`) | [LOTE12_TV](docs/LOTE12_TV.md) | substituto do template; só WTI bate o B&H e falha nos terços |
| 66 | Simple RSI-MA Algo (`qSoZRbX7`) | [LOTE12_TV](docs/LOTE12_TV.md) | **candidata no ETH 15m**: passa terços, 2ª metade e custo 4×; DD enorme, custo ETH estimado; BTC falha no recente |
| 65 | Acrypto Weighted v1.4.8 (`OF3TzrNS`) | [LOTE12_TV](docs/LOTE12_TV.md) | só WTI acima do B&H, com terços negativos |
| 64 | Template Trailing Strategy (`n8bgynWl`) | [LOTE12_TV](docs/LOTE12_TV.md) | ignorado (template) |
| 63 | Powertrend Volume Range Filter (`45FlB2qH`) | [LOTE12_TV](docs/LOTE12_TV.md) | poucas operações; nenhuma célula acima do B&H |
| 62 | TK Cross > EMA200 (`88TwdvFZ`) | [LOTE12_TV](docs/LOTE12_TV.md) | ETH 30m +104% mas DD −97%; demais ativos falham |
| 61 | Easy System 420 (`zBaDqbla`) | [LOTE11_TV](docs/LOTE11_TV.md) | placar de 14 indicadores; com SuperTrend largo bate o B&H no 15m, mas perde no terço do meio e com custo 2× |
| 60 | Grab Trading System (`1HAKnNRc`) | [LOTE11_TV](docs/LOTE11_TV.md) | acerto 52% e bruto ≈ 0; melhor +4,8% a.a. |
| 59 | Heikin Ashi Supertrend (`9z16eauD`) | [LOTE11_TV](docs/LOTE11_TV.md) | alvo 47%/stop 21% nunca disparam; é um SuperTrend sempre no mercado, melhor +12,8% |
| 58 | Strategy Code Example (`zgn9pUcQ`) | [LOTE11_TV](docs/LOTE11_TV.md) | template EMA14/21; uma célula empata com o B&H e morre em custo 2× |
| 57 | EVWMA VWAP MACD (QuantNomad, `ZguF6GBo`) | [LOTE11_TV](docs/LOTE11_TV.md) | sempre no mercado; −22% a +7% a.a. no default |
| 56 | Moving Average Cross and/or Bbands bot (`Nb7PYc7W`) | [LOTE10_TV](docs/LOTE10_TV.md) | SMA 50/200 sempre no mercado; 0/77 batem o B&H |
| 55 | Scalping Williams %R + MACD + SMA 1m (`975ByLQ5`) | [LOTE10_TV](docs/LOTE10_TV.md) | 4600 trades/ano no 1m, bruto negativo; −52% a.a. |
| 54 | Monthly Returns in PineScript Strategies (`kzp8e4X3`) | [LOTE10_TV](docs/LOTE10_TV.md) | é utilitário de tabela; o exemplo é o Pivot Reversal, 0/108 batem o B&H |
| 53 | Full strategy AllinOne MACD-RSI-PSAR-ATR-MA (`l7ELtgmb`) | [LOTE10_TV](docs/LOTE10_TV.md) | feito para EURUSD 1m; −26% a.a. no 1m, melhor +8% |
| 52 | [UL] Price Divergence Strategy v1.1 (`IDoY5LgE`) | [LOTE10_TV](docs/LOTE10_TV.md) | 440/501 com líquido positivo, mas exposição ~55%: melhor +7,5% a.a. |
| 51 | ICT Entry V2 (TS_Indie, `wm9e7Wca`) | [LOTE9_TV](docs/LOTE9_TV.md) | núcleo varredura + iFVG; 7/188 células com líquido positivo, melhor +0,3% a.a. |
| 50 | Hull Moving Average Swing Trader (`j60hYGuY`) | [LOTE9_TV](docs/LOTE9_TV.md) | sempre no mercado; t>2 em 9 células, mas 0/44 batem o B&H |
| 49 | RSI versus SMA (`wDLCPh1I`) | [LOTE9_TV](docs/LOTE9_TV.md) | o default (reversão) perde 3–18% a.a.; invertido bate o B&H no 30m mas morre no terço do meio e com custo 2× |
| 48 | UT Bot alerts strategy (`R9nsvSZR`) | [LOTE9_TV](docs/LOTE9_TV.md) | acerto 15–34% com BE + 3R; 0/312 batem o B&H |
| 47 | [RS] MicuRobert EMA cross V2 (`6YthKHw1`) | [LOTE9_TV](docs/LOTE9_TV.md) | stop de 22 pips = ruído; −3% a −53% a.a. no default |
| 46 | Bollinger Bands Breakout (`GKgxKjlC`) | [LOTE8_TV](docs/LOTE8_TV.md) | sempre no mercado; +14,8% no 30m, mas perde no terço do meio, no OOS e com custo 2× |
| 45 | BEST Engulfing + MA (`ROM3crig`) | [LOTE8_TV](docs/LOTE8_TV.md) | acerto 26–31%; 0/165 batem o B&H |
| 44 | VWAP Trendfollow (wbburgin, `XoR8rQaW`) | [LOTE8_TV](docs/LOTE8_TV.md) | default perde 2–18% a.a.; a única célula acima do B&H é ilha |
| 43 | Backtesting 3commas DCA Bot v2 (`8d6Auyst`) | [LOTE8_TV](docs/LOTE8_TV.md) | martingale long sem stop; usa ~17% do capital, −4% a +0,9% a.a. |
| 42 | TrendMaster Pro 2.3 (`mVkDf8qh`) | [LOTE8_TV](docs/LOTE8_TV.md) | filtros cortam tudo (+1% a.a.); sem eles é um SMA 9/21 que morre no terço do meio |
| 41 | SR TREND / Support Resistance breakout (`hwHKYkE0`) | [LOTE7_TV](docs/LOTE7_TV.md) | 90% do tempo posicionado; 0/40 batem o B&H |
| 40 | 72s Adaptive HMA+ pt.1 (`FrjeeWdl`) | [LOTE7_TV](docs/LOTE7_TV.md) | t>2 em 53 células, mas exposição de 30%: 0/292 batem o B&H |
| 39 | Captain Backtest Model (TFO, `tOQ8gnxj`) | [LOTE7_TV](docs/LOTE7_TV.md) | modelo de sessão NY; bruto ~0 bp, 0/130 com líquido positivo |
| 38 | Super Trend Daily 2.0 BF (`c4Cj7H2y`) | [LOTE7_TV](docs/LOTE7_TV.md) | 0/138 batem o B&H |
| 37 | Trailing SL Strategy (QuantNomad, `n3vj0MIi`) | [LOTE7_TV](docs/LOTE7_TV.md) | **candidata no ouro** com stop de 2% (+15% a +20% vs +13% a.a., Sharpe 1,1, OOS t>2); reprova nos outros 4 ativos |
| 36 | SUPERTREND ATR with Trailing Stop Loss (`L9GkARD2`) | [LOTE6_TV](docs/LOTE6_TV.md) | ATR(1) = true range; os t>2 são shorts vivendo do funding; 0/250 batem o B&H |
| 35 | ICT Master Suite, todos os modelos (Trading IQ, `ABYnIcdl`) | [ICT2022](docs/ICT2022.md), [ICT_SUITE](docs/ICT_SUITE.md) | 2022/Unicorn/OTE/Silver Bullet/Liquidity Raid × XAU/US100/WTI/BTC/ETH: nenhum bate o B&H com risco aceitável |
| 34 | Bollinger Band with RSI (`pKOaIHpb`) | [LOTE6_TV](docs/LOTE6_TV.md) | pirâmide de 50 e stop de 25%: acerto 77%, 0/304 batem o B&H |
| 33 | Iron Support Resistance / Scalping S/R (HPotter, `gp332Dao`) | [LOTE6_TV](docs/LOTE6_TV.md) | publicado com o backtest desligado; ligado, 0/365 batem o B&H |
| 32 | Hammers & Stars v1.2 (ZenAndTheArtOfTrading, `t776tkZv`) | [LOTE6_TV](docs/LOTE6_TV.md) | acerto 50% com RR 1:1; 0/545 batem o B&H |
| 31 | Full CRYPTO pack macd-rsi-obv-ema (SoftKill21, `DbRYTl6G`) | [LOTE5_TV](docs/LOTE5_TV.md) | o RSI é `< 100` (sempre verdadeiro); 0/128 batem o B&H |
| 30 | QQE MOD + SSL Hybrid + Waddah Attar Explosion (`YCob5r03`) | [LOTE5_TV](docs/LOTE5_TV.md) | "só sai no lucro" infla o acerto; 0/640 batem o B&H |
| 29 | Price and Volume Breakout Buy (TradeDots, `jc2hs2qK`) | [LOTE5_TV](docs/LOTE5_TV.md) | o filtro de volume piora; 0/334 batem o B&H |
| 28 | Trend Direction Helper (Daveatt, `dzpmnane`) | [LOTE4_TV](docs/LOTE4_TV.md) | é %R de 1 barra; 0/120 batem o B&H |
| 27 | Pivot Point SuperTrend (LonesomeTheBlue, `DwdC6FT4`) | [LOTE4_TV](docs/LOTE4_TV.md) | empata com o B&H no ouro; **candidata no ETH** (+81% vs +57% a.a., estável nos terços) |
| 26 | AI SuperTrend x Pivot Percentile (PresentTrading, `eC3qAYNQ`) | [LOTE4_TV](docs/LOTE4_TV.md) | o "KNN" é o rótulo da barra atual; 0/48 batem o B&H |
| 25 | Vix FIX / StochRSI Strategy (`TDxSLJRA`) | [VIX_FIX_STOCHRSI](docs/VIX_FIX_STOCHRSI.md) | só long, sai só em sobrecompra; 0/752 batem o B&H, o RSI do nome nem é usado |
| 24 | [STRATEGY][RS]ZigZag PA Strategy V4.1 (RicardoSantos, `NEDEDcsP`) | [ZIGZAG_PA](docs/ZIGZAG_PA.md) | Pine v2: `security()` sem `lookahead` olha o futuro (+70% a.a., win 89%); honesta 0/423 batem o B&H |
| 23 | MACD ReLoaded (Kivanc, `VO6DY8s1`) | [LOTE3_TV](docs/LOTE3_TV.md) | 1/60 células acima do B&H, só no terço final |
| 22 | ANN Strategy v2 (sirolf2009, `oY725jQw`) | [LOTE3_TV](docs/LOTE3_TV.md) | a "rede neural" é `sign(variação do ohlc4)`; −70% a.a. no 15m |
| 21 | Twin Optimized Trend Tracker / TOTT (Kivanc, `eENf7NpJ`) | [LOTE3_TV](docs/LOTE3_TV.md) | melhor do lote e ainda abaixo do B&H nos defaults |
| 20 | UT Bot Strategy (`VKMgZdYr`) | [LOTE3_TV](docs/LOTE3_TV.md) | trilha de ATR; 0/85 células batem o B&H |
| 19 | Open Close Cross Strategy R5.1 (JustUncleL, `vObmEraY`) | [LOTE3_TV](docs/LOTE3_TV.md) | o resultado publicado vive de `lookahead_on`: +215% a.a. vira −9% |
| 18 | RSI Divergence Indicator strategy (`qSLcZSyw`) | [RSI_DIVERGENCE](docs/RSI_DIVERGENCE.md) | dispara em todo pivô de RSI; 0/119 batem o B&H |
| 17 | Ichimoku + Daily-Candle_X + HULL-MA_X + MacD (SeaSide420, `RJBjyl2W`) | [ICHIMOKU_HULL_MACD](docs/ICHIMOKU_HULL_MACD.md) | sempre-no-mercado; 0/55 batem o B&H; o Ichimoku sozinho supera os 4 juntos |
| 16 | Flawless Victory Strategy (Bunghole, `i3Uc79fF`) | [FLAWLESS_VICTORY](docs/FLAWLESS_VICTORY.md) | não tem ML nenhum (constantes cravadas); 0/110 no ouro e no BTC |
| 15 | AO+Stoch+RSI+ATR (SerdarYILMAZ, `RpYoQCVJ`) | [SERDAR_AO_STOCH_RSI](docs/SERDAR_AO_STOCH_RSI.md) | RR 0,81 exige 55% de acerto por construção e entrega 52% |
| 14 | Hull Suite Strategy (InSilico/DashTrader, `Q9OQye4C`) + Backtest single EMA cross (che-trader, `j9rq1wQq`) | [HULL_EMA_FLIP](docs/HULL_EMA_FLIP.md) | sempre-no-mercado; 0/360 células batem o B&H |
| 13 | 3Commas Bot (Bjorgum, `MvlwAzSg`) | [3COMMAS_BOT](docs/3COMMAS_BOT.md) | é template de webhook; o cruzamento de MA é placeholder |
| 12 | Bollinger + RSI Double (ChartArt v1.1) | [BOLLINGER_RSI](docs/BOLLINGER_RSI.md) | sem saída nenhuma e RSI em 50/50; nunca bate o B&H |
| 11 | MACD + SMA 200 (ChartArt, `yMCa3XZD`) | [MACD_SMA200](docs/MACD_SMA200.md) | a ilha de 15m passa custo 4× mas morre no terço do meio e no OOS |
| 10 | MACD Confluence | [MACD_CONFLUENCE](docs/MACD_CONFLUENCE.md) | 0/864 células; bug no Pine publicado zera o short; reversão = 84% dos trades |
| 9 | Trendline Angle Pro V6 | [TRENDLINE_ANGLE](docs/TRENDLINE_ANGLE.md) | ângulo/ATR é razão sem escala — as zonas de 20°/45° não calibram nada |
| 8 | Gold Trail XAUUSD | [GOLD_TRAIL](docs/GOLD_TRAIL.md) | +2,4% a.a. contra +13,4% do B&H; o long é só beta |

Testadas no mesmo protocolo mas de **outras fontes** (vídeos, não TradingView), e por isso
fora deste repositório: CRT (Babayan), Ruiz MTF Fibo, SMC H4/M15/M1, SMA30 de vídeo, VWAP
pullback, Engolfo + PSAR, rompimento de NQ H1.

## Armadilhas que já custaram tempo

- **`lookahead_on`** em `security()` é a causa número um de curva publicada boa. Sempre
  conferir antes de reimplementar. Em Pine v1/v2 ele é **implícito**: o `security()` histórico
  já devolve o candle HTF corrente, sem nenhum parâmetro no código.
- **Sempre-no-mercado** (Hull, Ichimoku, Bollinger) não é estratégia: é beta com custo de
  giro. O benchmark certo é buy & hold, não zero.
- **Acerto alto sem stop** (RSI Divergence) vem da saída assimétrica, não do sinal.
- **Risco/retorno abaixo de 1 com acerto de moeda** (Serdar) é perda garantida; dá para
  reprovar lendo o Pine, antes de rodar.
- **Trendlines do Pine são desenho**, não série de dados — não existe `plot` para elas e o
  valor "ângulo" não tem unidade comparável entre ativos.
- `DatetimeIndex.asi8` no pandas 3 vem em **milissegundos**, não nanossegundos; usar
  `as_unit` antes de qualquer aritmética de timestamp.
