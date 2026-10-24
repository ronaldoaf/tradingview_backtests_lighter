# Lote 10 do TradingView: 5 estratégias (2026-10-22)

Ativo: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem na
abertura seguinte; stops e alvos resolvidos no M1 (stop antes do alvo no mesmo minuto); ordens stop
de entrada (Pivot Reversal) executadas em max(abertura, nível). Custo 0,75 bp/perna + funding 13,8%
a.a. (o long paga, o short recebe). Controle: mesmo lado e mesma duração.

Código: `scripts/study_tvlote10.py` (saída `results/study_tvlote10.txt`, grade
`results/study_tvlote10_xau_grid.csv`). Fontes em `pine/`. Triagem: nenhum `lookahead`; o MA/Bbands
bot (Pine v3) usa `security()` no próprio período e sem Heikin Ashi, o que não vaza.

**Veredito: 5 testadas, 5 reprovadas no ouro, nenhuma célula acima do B&H (0/1007).** Sem
candidata, não houve rodada de robustez nem extensão a outros ativos.

| # | Estratégia | Células | liq>0 | t>2 | CAGR>B&H | Melhor CAGR |
|---|---|---|---|---|---|---|
| 52 | [UL] Price Divergence Strategy v1.1 (`IDoY5LgE`) | 501 | 440 | 19 | 0 | +7,5% |
| 53 | Full strategy AllinOne MACD-RSI-PSAR-ATR-MA (`l7ELtgmb`) | 222 | 54 | 3 | 0 | +8,1% |
| 54 | Monthly Returns in PineScript Strategies (`kzp8e4X3`) | 108 | 74 | 23 | 0 | +11,9% |
| 55 | Scalping Williams %R + MACD + SMA 1m (`975ByLQ5`) | 99 | 12 | 0 | 0 | +4,3% |
| 56 | Moving Average Cross and/or Bbands bot V1.1 (`Nb7PYc7W`) | 77 | 37 | 1 | 0 | +12,4% |

B&H do ouro no período: +13,4% a.a., Sharpe diário 0,73.

---

## 52. [UL] Price Divergence Strategy v1.1 (`IDoY5LgE`, Pine v4)

Divergências regulares e ocultas entre fractais de 5 barras do preço e do histograma MACD (SMA12 −
SMA26, sinal EMA9), filtradas pelo oscilador MMLO(100) no 2º quadrante (compra só com o preço na
metade de cima da faixa); sai quando o MMLO cruza zero. O trailing publicado (100 pontos sem offset)
não arma. É o sinal mais consistente do lote: 440/501 células com líquido positivo, default de +3 a
+10 bp por trade no 15m–1h (t = +2,1 no 15m). Mas fica posicionado só ~55% do tempo e cada trade é
pequeno: o default faz +4% a +7% a.a., o melhor +7,5%.

## 53. Full strategy AllinOne (`l7ELtgmb`, Pine v4)

Feito para EURUSD 1m. Long com PSAR de alta, EMA10 cruzando acima da SMA17, histograma MACD (SMA) > 0 e
RSI5 > 72; short no espelho; stop e alvo de 5 ATR14; sinal contrário fecha. O "equity protector"
(fecha tudo com 1% de perda flutuante, sobre uma posição dimensionada para arriscar 2%) não foi
reproduzido. Default: −26% a.a. no 1m, −9% no 5m, −2% a +3% do 15m ao 4h. Sem o filtro de RSI e com
alvo de 3× o stop chega a +8,1% (1h).

## 54. Monthly Returns in PineScript Strategies (`kzp8e4X3`, Pine v4)

É um utilitário que desenha a tabela de retornos mensais. A estratégia que vem junto como exemplo é o
**Pivot Reversal** do TradingView (pivô 2/1, ordem stop um tick além do último topo/fundo ainda não
rompido, sempre no mercado), e foi ela que se testou. Default: de 114 a 5000 trades/ano, −57% a.a. no
5m e +7,6% no 4h. Com pivôs maiores (4/2) o 1h faz +11,9% (t = +3,5), ainda abaixo do B&H.

## 55. Scalping Williams %R + MACD + SMA 1m (`975ByLQ5`, Pine v5)

Só roda no 1m: %R(140) cruzando −94 com close > SMA7 arma a compra (desarma em −40); entra quando o
histograma MACD(24,52,9) vira positivo; sai na primeira barra em que o histograma cai. Venda no
espelho. No 1m: 4600 trades/ano de 0,01 dia, bruto −0,1 bp, **−52% a.a.** No 5m/15m também perde;
melhor célula +4,3%.

## 56. Moving Average Cross and/or Bbands bot V1.1 (`Nb7PYc7W`, Pine v3)

Long na primeira barra com close > SMA50 > SMA200, short no espelho; não tem saída além do sinal
contrário (os stops/alvos vêm desligados). Default: +7,3% (15m) a −1,1% (1h). A opção Bollinger
(comprar abaixo da banda inferior) é pior. O melhor (SMA 20/50, 30m) faz +12,4%, sem chegar ao B&H.
