# tradingview_backtests_lighter

Infraestrutura de backtest para reproduzir, com custo real da **Lighter**, estratégias
publicadas no [TradingView](https://www.tradingview.com/scripts/). Cada estudo reimplementa
o Pine Script em Python/NumPy, roda uma grade de parâmetros em vários timeframes e compara
o resultado contra dois benchmarks: **buy & hold** e um **controle aleatório** com o mesmo
lado, a mesma duração e a mesma gestão de saída.

Resultado até agora: **nenhuma das 24 estratégias testadas passou**. Os relatórios em
[`docs/`](docs/) explicam o motivo de cada reprovação — o que costuma ser mais útil que o
veredito, porque o mesmo punhado de falhas se repete (sempre-no-mercado disfarçado de
sinal, `lookahead_on`, risco/retorno impossível por construção, ilha de parâmetros que
morre no out-of-sample).

## Protocolo de teste

1. O ativo padrão é **ouro (XAUUSD)**. Só se o ouro for positivo a estratégia é estendida
   para US100, BTC, WTI e ETH. Não vale gastar 5 ativos numa ideia que já morre no primeiro.
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

Todas reprovadas. Ordem cronológica inversa.

| # | Estratégia (autor, id do script) | Doc | Diagnóstico |
| --- | --- | --- | --- |
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
