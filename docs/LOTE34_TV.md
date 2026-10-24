# Lote 34 do TradingView: scripts resgatados (2026-10-23)

São 10 scripts que tinham sido pulados nos lotes 21 a 29 por "complexos demais". A triagem está em `estrategias/puladas_complexas.md`, na pasta do projeto. De cada script portei só o núcleo de tendência e deixei de fora os TPs parciais, os painéis e os SL/TP em pontos de forex. Rodei a grade completa (15m a 1D, os dois lados ou só comprado) nos 5 ativos. O código está em `scripts/study_tvlote34.py`.

Para o veredito, usei o script novo `scripts/study_veredito_lote.py`. Ele pega as células com CAGR > 0, Sharpe ≥ B&H e t > 2 e aplica o critério novo inteiro: terços, spread 4×, funding 0 e |corr| < 0,5 com as 34 aprovadas. Assim não é preciso escrever um `_rob` à mão. O resultado está em `results/study_tvlote34_veredito.txt`.

| # | Estratégia | Script | Núcleo simulado |
|---|---|---|---|
| 1 | Gradient Trend Filter | `Va06tXWV` | EMA tripla 25; inclinação de 2 barras cruzando 0 |
| 2 | Market Trend Levels | `v0XszvRG` | EMA 12 × 25 (filtro ADX como variante) |
| 3 | Pivot Percentile Trend | `XJfWHHEc` | força por percentis + Supertrend (20, 16) sobre ela |
| 4 | FlexiMA Variance Tracker | `R9qM6XrY` | mediana dos desvios de 20 SMAs + Supertrend (10, 15) |
| 5 | Ichimoku Kumo Twist | `ZmQSRFQ4` | Senkou A × B com stop na máxima/mínima do cruzamento |
| 6 | Zero-Lag MA | `7kbjZ4he` | ZLMA × EMA 34, rompimento da caixa ATR, SL no fundo, alvo rr× |
| 7 | Adaptive Zero Lag EMA | `Q7h83i1t` | EC × EMA com período Cos IFM (SL em pontos ignorado) |
| 8 | ML SuperTrend kNN | `9Mm3qKME` | Supertrend sobre kernel racional + média kNN das SMAs 3/50 |
| 9 | Turtle | `cOv24513` | uma unidade, L1 20/10 com filtro do último vencedor, L2 55/20, stop 2N |
| 10 | Kahlman HullMA / WT | `1Im3kKwi` | Kalman(Hull) × Kalman(HMA3) com confirmação do WaveTrend |

## Resultado

Das 35 candidatas, **2 entram**, 13 passam no critério mas são redundantes (corr ≥ 0,5) e o resto reprova.

| Estratégia | Ativo | Config | CAGR (B&H) | Sharpe (B&H) | DD | t | Terços | Spread 4× | Corr máx |
|---|---|---|---|---|---:|---:|---|---:|---|
| Zero-Lag MA | US100 30m | rr 4, os dois lados | +19,9% (+20,3%) | 1,20 (0,93) | −26% | 3,24 | +16% / +34% / +12% | +9% | +0,13 |
| ML SuperTrend kNN | BTC 4h | 2,94, TP 2,2% | +16,5% (+43,7%) | 1,17 (0,91) | −18% | 2,25 | +25% / +11% / +14% | +14% | +0,13 |

A Zero-Lag no US100 é a **primeira aprovada no US100**. O ML SuperTrend no BTC fica pouco tempo posicionado (o TP de 2,2% fecha rápido), e por isso o DD é baixo e o CAGR fica abaixo do B&H.

Redundantes de destaque: o ML SuperTrend no ETH 4h sem TP (+114%, Sharpe 1,44, corr 0,54 com o Combo 123 do ETH) e o Kumo Twist no ETH 15m (+88%). Os dois são bons, mas repetem as tendências do ETH já aprovadas.
