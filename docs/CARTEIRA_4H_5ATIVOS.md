# Carteira 4h de 5 ativos: todas as estratégias do TradingView, parâmetro único

**Pergunta:** qual estratégia funciona com **os mesmos parâmetros** em BTC, WTI, US100, XAU e XAG ao mesmo tempo,
long e short, no gráfico de 4h, de jan/2020 a dez/2023?

**Resposta curta:** nenhuma passa no teste de múltiplas comparações. Várias têm Sharpe 1,5–2,1 nos 4 anos e nos 5
ativos, mas 91% das 336 estratégias long+short deram Sharpe positivo nesse período, o que mostra que 2020–2023 foi
um período de tendência forte que favorece quase qualquer regra seguidora. Com 1.516 células testadas, o Sharpe que
o melhor resultado atingiria por sorte é ~2,15; o melhor Sharpe deflacionado (DSR) é 0,48 (precisa de 0,95).
O que sobra de sinal útil: 43 estratégias têm alfa com t > 2 sobre uma tendência ingênua (EMA 50×200), contra ~8
esperadas por acaso. As mais fortes nisso são TMFS, Force trade scalper, Parabolic SAR stop entries, Keltner SL/TP,
FTSMA e Heikin Ashi Price Action.

**2024 em diante não foi carregado** (os dados são cortados em 31/12/2023): fica como holdout para validar a
seleção final.

## Método

- 41 lotes (lotes 3 a 38 + flawless, ichimoku, rsidiv, vixfix, zigzagpa), a mesma lista do `run_full.sh`.
  Grade de cada estratégia como já existia, só no **4h**. Exemplos/templates fora, `lookahead_on` (peek) fora.
- Carteira: 20% em cada ativo a 1x, rebalanceada todo dia (média dos retornos diários). Ativo sem trade naquele dia
  rende zero. O mesmo parâmetro vale para os 5.
- Só entram células que operam **os dois lados** (≥ 5% dos trades vendidos e ≥ 5% comprados): 1.703 das 3.643; 187 delas saem por série quebrada (equity zerou e voltou, retorno diário > 50%), sobram 1.516.
- Custos: spread da Lighter por perna e funding anual pro-rata (`CUSTO`/`FUND` de `study_engulf_psar.py`). XAG usa
  os valores do ouro (0,75 bp; 13,8% a.a.), como nos estudos anteriores.
- Dados 1m: Binance (BTC), Dukascopy (WTI, US100, XAU, XAG).
- Execução e marcação: as de sempre do repo (sinal no fechamento, ordem na abertura seguinte, stops no M1,
  `tvlib.equity_curve`).
- Sharpe e vol anualizados com 365 dias; t = média/desvio × √n diário.

## Controle de overfitting

- **Sharpe deflacionado** (Bailey & López de Prado) com N = 1.516 células e a variância dos Sharpes entre elas:
  Sharpe esperado do máximo sob H0 = 2,15 a.a.; nenhuma célula tem DSR > 0,95.
- **Referência de tendência ingênua**: EMA 50×200 sempre posicionado nos 5 ativos, com custos: CAGR +13%, Sharpe 0,64.
  B&H pesos iguais (sem funding): CAGR +25%, Sharpe 1,02, DD −34%. Para cada estratégia: correlação e alfa (com t)
  sobre a tendência ingênua.
- **Vizinhança**: mediana do Sharpe de toda a grade da estratégia e fração de células "robustas" (≥ 3 anos e
  ≥ 4 ativos positivos). As grades no 4h são pequenas (mediana de 2 células por estratégia, máximo 64), então a
  vizinhança é fraca em muitas delas: célula única não tem como provar robustez de parâmetro.
- **Nota de ranking** = 0,5·Sharpe da melhor célula + 0,5·Sharpe mediano da grade + bônus por anos positivos,
  ativos positivos e fração robusta.

## Top 20 por robustez

| # | Estratégia (lote) | Parâmetro | CAGR | Vol | Sharpe | DD | t | DSR | t do alfa vs tendência | Anos + | Ativos + | 2020 | 2021 | 2022 | 2023 | Células | Trades | Win |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 17. Force trade scalper (22) | 3/20 ambos | +42% | 20% | 1.82 | -22% | 3.6 | 0.25 | 3.4 | 4/4 | 5/5 | +75% | +36% | +34% | +27% | 2 | 737 | 39% |
| 2 | 3. TMFS (15) | sw8 sl8atr tp1% ambos | +14% | 6% | 2.12 | -4% | 4.2 | 0.48 | 4.1 | 4/4 | 5/5 | +15% | +17% | +9% | +14% | 6 | 1367 | 71% |
| 3 | 3. FTSMA (17) | 5/20/200 semft ambos | +32% | 19% | 1.57 | -14% | 3.1 | 0.12 | 3.1 | 4/4 | 5/5 | +81% | +32% | +18% | +7% | 2 | 486 | 30% |
| 4 | 8. Parabolic SAR stop entries (33) | af0.02 ambos | +34% | 19% | 1.64 | -14% | 3.3 | 0.15 | 3.3 | 4/4 | 5/5 | +104% | +19% | +19% | +11% | 2 | 1497 | 39% |
| 5 | 10. Slopes (22) | 50/200 filtro ambos | +25% | 17% | 1.41 | -10% | 2.8 | 0.06 | 2.5 | 4/4 | 5/5 | +57% | +14% | +11% | +22% | 4 | 1035 | 33% |
| 6 | 10. Heikin Ashi Price Action (28) | ha ambos | +32% | 20% | 1.52 | -15% | 3.0 | 0.10 | 2.8 | 4/4 | 4/5 | +55% | +26% | +43% | +10% | 2 | 2176 | 37% |
| 7 | 15. Rob Booker ADX Breakout (29) | adx18 ambos | +8% | 7% | 1.20 | -7% | 2.4 | 0.02 | 2.3 | 4/4 | 4/5 | +26% | +1% | +4% | +3% | 1 | 331 | 40% |
| 8 | 11. HL MovingAvg2Line Cross (37) | n9 ambos | +26% | 20% | 1.28 | -16% | 2.6 | 0.04 | 2.3 | 3/4 | 5/5 | +105% | +18% | -5% | +10% | 2 | 2300 | 35% |
| 9 | 16. Bull and Bear Fear (29) | n30 ambos | +23% | 20% | 1.16 | -14% | 2.3 | 0.02 | 2.0 | 4/4 | 4/5 | +89% | +3% | +7% | +10% | 2 | 1242 | 32% |
| 10 | 7. UL QQE Cross (23) | thr5 semfiltro ambos | +21% | 17% | 1.19 | -14% | 2.4 | 0.02 | 2.0 | 3/4 | 5/5 | +63% | +19% | -4% | +15% | 4 | 2496 | 35% |
| 11 | 12. Keltner SL/TP (36) | k2/sl20 ambos | +33% | 18% | 1.72 | -14% | 3.4 | 0.17 | 3.2 | 4/4 | 5/5 | +39% | +18% | +44% | +33% | 4 | 242 | 49% |
| 12 | 2. High/Low channel swing (29) | l12 ambos | +23% | 20% | 1.15 | -15% | 2.3 | 0.02 | 2.1 | 3/4 | 5/5 | +91% | +13% | -3% | +10% | 2 | 3115 | 37% |
| 13 | 8. RSI Alligator (36) | sl3 ambos | +16% | 20% | 0.86 | -19% | 1.7 | 0.00 | 1.7 | 4/4 | 5/5 | +49% | +8% | +3% | +11% | 2 | 3425 | 29% |
| 14 | 20. Ichimoku + EMA filter (33) | ema ambos | +19% | 16% | 1.14 | -11% | 2.3 | 0.02 | 1.9 | 3/4 | 5/5 | +63% | +12% | -2% | +11% | 2 | 1251 | 31% |
| 15 | 1. Supertrend CCI (17) | cci14 ambos | +26% | 20% | 1.22 | -15% | 2.4 | 0.03 | 2.2 | 3/4 | 5/5 | +76% | +33% | -2% | +9% | 4 | 4315 | 28% |
| 16 | 14. Volatility Range Breakout (36) | n50 ambos | +16% | 13% | 1.21 | -9% | 2.4 | 0.02 | 2.1 | 3/4 | 4/5 | +46% | +10% | -1% | +13% | 1 | 179 | 45% |
| 17 | 10. Combo 123 + Rainbow Oscillator (37) | ro5 ambos | +18% | 17% | 1.07 | -22% | 2.1 | 0.01 | 1.7 | 3/4 | 5/5 | +89% | +6% | -12% | +12% | 2 | 1770 | 27% |
| 18 | 5. Bitcoin SuperFlip (28) | f1.8 ambos | +16% | 15% | 1.05 | -17% | 2.1 | 0.01 | 1.7 | 3/4 | 5/5 | +73% | +3% | +2% | -1% | 2 | 819 | 40% |
| 19 | 18. Gaussian Channel (28) | p144 ambos | +21% | 20% | 1.05 | -21% | 2.1 | 0.01 | 1.7 | 3/4 | 5/5 | +71% | +3% | -2% | +22% | 2 | 1342 | 24% |
| 20 | 18. VWAP X EMA (33) | ema20 ambos | +29% | 18% | 1.53 | -15% | 3.1 | 0.10 | 2.8 | 4/4 | 4/5 | +45% | +37% | +29% | +7% | 2 | 2200 | 26% |

| # | Estratégia | BTC | WTI | US100 | XAU | XAG |
|---|---|---|---|---|---|---|
| 1 | 17. Force trade scalper | +125% | +45% | +5% | +8% | +15% |
| 2 | 3. TMFS | +24% | +25% | +3% | +6% | +8% |
| 3 | 3. FTSMA | +96% | +17% | +13% | +1% | +19% |
| 4 | 8. Parabolic SAR stop entries | +36% | +23% | +26% | +11% | +26% |
| 5 | 10. Slopes | +54% | +15% | +8% | +5% | +22% |
| 6 | 10. Heikin Ashi Price Action | +86% | +37% | +0% | -1% | +19% |
| 7 | 11. HL MovingAvg2Line Cross | +15% | +38% | +5% | +11% | +27% |
| 8 | 16. Bull and Bear Fear | +28% | +36% | -5% | +5% | +21% |
| 9 | 7. UL QQE Cross | +40% | +15% | +11% | +6% | +9% |
| 10 | 12. Keltner SL/TP | +79% | +39% | +5% | +11% | +13% |
| 11 | 2. High/Low channel swing | +1% | +49% | +7% | +7% | +23% |
| 12 | 8. RSI Alligator | +0% | +16% | +6% | +9% | +18% |
| 13 | 20. Ichimoku + EMA filter | +27% | +12% | +11% | +8% | +14% |
| 14 | 1. Supertrend CCI | +28% | +34% | +7% | +4% | +20% |
| 15 | 10. Combo 123 + Rainbow Oscillator | +42% | +11% | +8% | +2% | +7% |
| 16 | 5. Bitcoin SuperFlip | +23% | +24% | +10% | +2% | +3% |
| 17 | 18. Gaussian Channel | +5% | +23% | +14% | +7% | +17% |
| 18 | 18. VWAP X EMA | +107% | +11% | +13% | +10% | -1% |
| 19 | 49. Awesome Oscillator | -2% | +58% | +12% | +3% | +18% |
| 20 | 18. SSL Channel Cross | +9% | +26% | +0% | +6% | +21% |

(CAGR por ativo = da perna sozinha, a 1x; na carteira cada uma pesa 1/5.)

## Leitura

- BTC carrega a maioria das estratégias; US100 e XAU contribuem pouco. TMFS e Force trade scalper são as que têm
  os 5 ativos positivos e os 4 anos positivos com correlação baixa com a tendência ingênua (0,13 e 0,29).
- TMFS tem a melhor relação risco/retorno (Sharpe 2,1, DD −4%), mas o CAGR é baixo (+14%) porque passa pouco tempo
  posicionado; dá para alavancar.
- Nada aqui está aprovado: o próximo passo honesto é congelar 5–10 candidatas (as de maior t do alfa e grade
  estável) e rodá-las uma única vez em 2024–2026.

## Arquivos

- `scripts/cart4h_lote.py`: roda um lote num ativo só no 4h, jan/2020–dez/2023, grava retorno diário por célula.
- `scripts/cart4h_agg.py`: monta a carteira, estatísticas, DSR, referências e ranking.
- `results/cart4h/celulas.csv`: as 1.516 células com stats do período, por ano e por ativo.
- `results/cart4h/ranking.csv`: melhor célula de cada uma das 336 estratégias com robustez.
- Rodar: `ATIVO=btc python scripts/cart4h_lote.py 36` (lotes que fixam timeframe no código precisam de `NOPATCH=1`),
  depois `python scripts/cart4h_agg.py`.

## Top 10 por CAGR (uma configuração por estratégia, a de maior CAGR)

`scripts/cart4h_top10_cagr.py` → `results/cart4h/top10_cagr.csv` e `top10_cagr_corr.csv`.

| # | Estratégia (lote) | Configuração | CAGR | Sharpe | DD |
|---|---|---|---|---|---|
| 1 | 17. Force trade scalper (22) | 3/20 ambos | +42% | 1.82 | -22% |
| 2 | 5. Delta-RSI (14) | r14 w30 d3 signal ambos | +37% | 1.53 | -25% |
| 3 | 8. Parabolic SAR stop entries (33) | af0.02 ambos | +34% | 1.64 | -14% |
| 4 | 12. Keltner SL/TP (36) | k2/sl20 ambos | +33% | 1.72 | -14% |
| 5 | 10. Heikin Ashi Price Action (28) | ha ambos | +32% | 1.52 | -15% |
| 6 | 2. Super Trend Daily 2.0 (7) | sl0.05 roc0.0 m1.5/1.3 ambos | +32% | 1.47 | -16% |
| 7 | 3. FTSMA (17) | 5/20/200 semft ambos | +32% | 1.57 | -14% |
| 8 | 1. Open Close Cross R5.1 (3) | hon HULL13 x1 | +31% | 1.35 | -30% |
| 9 | 18. VWAP X EMA (33) | ema20 ambos | +29% | 1.53 | -15% |
| 10 | 5. MACD ReLoaded (3) | HULL 12/26/9 | +28% | 1.24 | -25% |

Correlação média entre as 10 (retornos diários da carteira, pares fora da diagonal): **0,31**. As 10 juntas, pesos iguais: CAGR +35%, Sharpe 2,5, DD −6% (in-sample, com a seleção feita no mesmo período).
