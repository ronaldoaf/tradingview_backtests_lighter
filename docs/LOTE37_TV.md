# Lote 37 do TradingView (20 estratégias, 5 ativos)

Scripts: `scripts/study_tvlote37.py` (grade), `scripts/study_veredito_lote.py 37` (veredito) e `scripts/study_tvlote37_corr.py` (correlação das que entraram entre si e com as 5 do lote 36). Resultados: `results/study_tvlote37_{ativo}_grid.csv`, `results/study_tvlote37_veredito.txt` / `.csv` e `results/study_tvlote37_corr.txt`. Grade: padrão do script mais 1 a 4 combinações, em 15m, 30m, 1h, 4h e 1D.

Posições 956 a 1000 da lista (a lista tem 1.007; sobram 7).

**Puladas na ordem da lista:**
- **Sessão de bolsa ou tamanho variável:** `Tts2YhVP` (Wave Trend com sessões e lotes 1/2/4), `UDNlq5ow` (sessões), `CzQ5lLHJ` (VWAP diário).
- **`security` em outro TF ou outro ativo:** `uk1XyAub` (Pine 1), `5zEiJjGu`, `LGAJeltq` (força relativa contra SPX/BTC), `ULdigyGh`, `7wgvQ883` (Pine 1), `6iDU009f` (MACD do 1m), `sw58QT16` (lookahead_on), `6mfMvXzj`, `1pKkKl3g` (Renko).
- **Pips, ticks ou pontos:** `4F1hjypD`, `ii4VZhUA`, `l5RKDiyV`.
- **DCA, piramidação, binária:** `skl7JtgC` (3Commas), `qgofvS9I` (DCA), `S7ZJRMi7` (opção binária, pyramiding 15).
- **Complexas demais, template ou sem estratégia:** `2qapmnO6` (3.183 linhas), `brMq1l1s` (template), `570UaPp3` (linha desenhada à mão), `Iv1wlVa8` (tabela de retornos), `e2fWFUIo` (sem strategy.entry), `BTzQGau9`, `AMxhpBej` (pump catcher com alavancagem 5x; ficou fora para fechar 20).

| # | Estratégia | Script | Regra simulada (simplificações) |
|---|---|---|---|
| 444 | Laguerre RSI | `vWG3tMJh` | cu × cd do filtro de Laguerre (alpha 0,2); inverte. |
| 445 | Chande Kroll Stop | `GoHLj2XP` | Só long: close cruzando mín21 + 3 ATR10 acima da SMA21 compra; close < máx21 − 3 ATR10 fecha. |
| 446 | MACD + DMI + Volatility Stop | `nD83sb4E` | Só long: MACD × sinal com +DI > −DI; alvo 3% ou vStop (20, 2) fecha. |
| 447 | Big Bar | `uuinZwsR` | Vela grande contra + vela a favor; stop ohlc4 ∓ 4 ATR14, alvo 1R; inverte. |
| 448 | Mean-Reversion Swing | `LIcdcfU8` | Recuo de 50% no canal de 20 a favor da SMA50; alvo/stop nas bandas. |
| 449 | DMI Modified | `usbHOChM` | DI com máx/mín de 9, diferença em EMA9: >0 e subindo compra, <0 e caindo vende. |
| 450 | Hull Suite | `NhBn8wuA` | HMA55 vs 2 barras atrás (padrão só long). |
| 451 | IU 4 Bar UP | `fUiBVHl7` | Só long: 4 velas de alta acima do Supertrend 14/1; abaixo fecha. |
| 452 | 3x Supertrend + Stoch RSI | `Kls9JTiM` | 2 Supertrends vizinhos + K × D + EMA200; alvo 1,6 / stop 2,7 ATR14. |
| 453 | Combo 123 + Rainbow | `2JTpVVrO` | Os dois do mesmo lado entram, discordando zera. |
| 454 | HL MovingAvg2Line Cross | `nhG8OBiD` | Close > EMA9(máx) compra, < EMA9(mín) vende; inverte. |
| 455 | DMI + nuvem Ichimoku | `snP0MRjI` | ADX passando de 25 com DI a favor entra; fim da força ou nuvem "verde" sai. |
| 456 | Reversal Catcher | `PJb1qh7h` | Volta para dentro da BB 20×1,5 com RSI cruzando 30/70 contra a tendência; sem fechamento no fim do dia. |
| 457 | Quantitative Trend | `I4FhUvyq` | Só long: close acima do close da confirmação do último pivô 46/32; alvo 2%, stop 1,75%. |
| 458 | WMX Williams Fractals | `s1UnbQTF` | Fractal de 5 barras no close (sem as variantes com empate); inverte. |
| 459 | RSI Classic (Coinrule) | `JMm04UG5` | Só long: RSI14 < 30 compra, > 60 fecha. |
| 460 | OBV Acumulação/Distribuição | `FAnuuDAa` | Só long: acumulado cruzando a EMA20 com vela a favor. |
| 461 | Chaloke System | `9ID5apv1` | EMAs 9/15/24 − ATR5; inverte. |
| 462 | Gold TDOW | `zUMUafG8` | Só long: MACD > sinal, Stoch > 50, RSI > 50, entrada só seg/qua/qui (UTC); MACD < sinal fecha. Stop em US$ fora. |
| 463 | RSI-CCI Fusion | `cnILutZ3` | z-score de RSI e CCI cruzando bandas de 1 desvio (padrão só long). |

## Resultado

35 células passam no filtro barato. Depois de terços, 2ª metade, spread 4×, funding 0 e |corr| < 0,5 com as 34 aprovadas, 8 células entram. Contra as 5 do lote 36 e entre si (corr ≥ 0,5 sai), **2 entram**:

| Estratégia | Ativo | Config | CAGR (B&H) | Sharpe (B&H) | DD | t | Terços | Spread 4× | Corr máx |
|---|---|---|---|---|---:|---:|---|---:|---|
| Chande Kroll Stop | ETH 30m | n21, 1,5 ATR, só comprado | +42,8% (+56,8%) | 1,63 (0,96) | −18% | 3,45 | +80% / +30% / +25% | +28% | +0,35 |
| Gold TDOW | ETH 1h | seg/qua/qui, só comprado | +61,7% (+56,8%) | 1,42 (0,96) | −45% | 2,74 | +168% / +47% / +7% | +54% | +0,47 |

- A **Gold TDOW no BTC 1h e 30m** (+31,8%, Sharpe 1,04, t 3,41) passa, mas tem corr 0,62 com a do ETH 1h e fica de fora. A do ETH 30m é a mesma regra (0,74).
- O **DMI + Ichimoku no ETH 30m** passa, mas tem corr 0,57 com a TDOW do ETH.
- No **US100**, o IU 4 Bar UP 30m (f3) e o WMX Fractals 4h passam contra as 34, mas têm corr 0,54 e 0,52 com a Candle Breakout do lote 36.
- Ouro e WTI: nenhuma célula passa no filtro barato.
