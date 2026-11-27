# UVXY — todas as estratégias TradingView do repo

**Veredito: nenhuma estratégia passa no UVXY.** Tudo o que aparece positivo é o viés vendido
capturando o decaimento estrutural do ETF; o controle aleatório de mesmo lado e mesma duração
faz o mesmo ou melhor (t ≤ 1 vs controle), ou a amostra tem 5–15 trades em 15 anos.

## Dados (`scripts/fetch_uvxy_alpaca.py` e `scripts/fetch_uvxy.py`, split-ajustados)

| Série | Ativo no código | Período | Barras |
| --- | --- | --- | --- |
| **M1 Alpaca (SIP, com pré/pós)** | `uvxy` | 2016-01-01 → 2026-11-27 | 1,92 M |
| 1h Yahoo (pregão regular) | `uvxyh` | 2024-01-02 → 2026-11-27 | 5.080 |
| diário | `uvxyd` | 2011-10-04 → 2026-11-27 | 3.810 |

O M1 da Alpaca (requer `ALPACA_KEY`/`ALPACA_SECRET`) é a série principal: stops intrabar no minuto,
como nos outros ativos. As séries 1h/diária do Yahoo foram a primeira rodada; nelas os TFs menores
que a barra colapsam para ela.
Custos: spread assumido 5 bp/perna; funding 12,1%/ano pago pelo long (média medida na AlphaX,
1,1 bp/8h, jun–nov/2026).

## Benchmarks

| Série | Buy & hold CAGR | Short & hold 1x (rebalanceio por barra) |
| --- | --- | --- |
| diário 2011–2026 | −79,3%/ano | +13,8%/ano (com dias de +66% contra) |
| 1h 2024–2026 | −54,1%/ano | −35,1%/ano (picos de ago/24 e abr/25) |

Bater buy&hold é trivial (qualquer estratégia com short bate). O filtro real é o controle aleatório.

## Rodada principal — M1 Alpaca 2016–2026 (B&H −72,9%/ano), logs em `results/uvxy/m1/`

| Estratégia | Resultado | Leitura |
| --- | --- | --- |
| BB+RSI | 59/64 liq>0, 37 com t>1 | o short sozinho tem t≈0 vs controle; o t>1 vem do long perder menos que o long aleatório. 6–18 trades em 4h/1h |
| MACD+SMA200 | 158/212 liq>0, 61 com t>1 | as melhores têm 5–11 trades em 11 anos |
| Engolfo+PSAR (1h) | R médio negativo na maioria dos anos | reprova |
| Flawless Victory | 0/109 liq>0 | reprova |
| Flip MA | 152/360 liq>0, retornos pequenos | reprova |
| Gold Trail | 96/216 R_liq>0 | sem célula que bata o controle de forma consistente |
| Ichimoku+Hull+MACD | 39/55 liq>0, só 1 com t>1 | é o short do decaimento |
| MACD Confluence | 4/864 R_liq>0 | reprova |
| RSI Divergence | 1/115 liq>0 (CAGR −16%) | reprova |
| Serdar AO/Stoch RSI | 89/720 R_liq>0 | reprova |
| Trendline Angle | 55/432 R_liq>0 | reprova |
| Lote 3 (TOTT/OCC/UT/MACD-RE/ANN) | 3/470 com t>2 | múltiplos testes; o resto é o short do decaimento |
| Lote 7 | 0/50 liq>0 | reprova |
| ORB30 (NY) | −2,5%/ano, p vs controle 0,26 | só o último terço positivo; reprova |

Conclusão mantida: nenhuma passa.

## Primeira rodada — 1h/diário Yahoo (13 rodadas; 3Commas ignorada por ser template; ORB30 ficou para o M1)

| Estratégia | uvxy 1h | uvxyd diário | Leitura |
| --- | --- | --- | --- |
| BB+RSI | positivo, t≈2 vs controle | +6453 bp/trade, t≈2,8 | só 6 trades em 15 anos — amostra inútil |
| Engolfo+PSAR | R líquido < 0 em 2024 e 2026 | — | reprova |
| Flawless Victory | — | 4/104 células liq>0, todas CAGR negativo | reprova |
| Flip MA (EMA/Hull) | todas negativas | todas negativas | reprova |
| Gold Trail | 78/216 R_liq>0, melhor R 0,08 t<1 | — | reprova |
| Ichimoku+Hull+MACD | — | 50/55 liq>0, **0 com t>1** | é o short do decaimento |
| MACD Confluence | R_liq médio −0,07 | — | reprova |
| MACD+SMA200 | — | 95/100 liq>0, 5–7 trades | amostra inútil |
| RSI Divergence | — | t alto mas CAGR −53%, Sharpe −1,2 | reprova |
| Serdar AO/Stoch RSI | — | perdas enormes | reprova |
| Trendline Angle | só 4h marginal (R 0,02) | — | reprova |
| Lote 3 (TOTT/OCC/UT/MACD-RE/ANN) | 0 células t>2 | 0 células t>2 (TOTT com t<0) | é o short do decaimento |
| Lote 7 | célula do doc +27 bp/trade, t=0,5, OOS ~0 | — | reprova |

Logs completos e grades em `results/uvxy/`.
Se a ideia for explorar o decaimento, o caminho é estudar short estrutural com gestão de risco
para os picos de volatilidade, não sinais técnicos do TradingView.
