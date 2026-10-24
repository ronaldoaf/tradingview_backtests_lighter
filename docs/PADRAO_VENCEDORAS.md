# O que as 34 aprovadas têm em comum, e se médias móveis simples reproduzem

Scripts: `scripts/study_padrao.py` (traços das 34), `scripts/study_simples.py` (grade de regras simples, escolha só antes do OOS), `scripts/study_simples_vs.py` (comparação com as carteiras). Saídas em `results/study_padrao.txt`, `results/study_simples.txt`, `results/study_simples_vs.txt`.

## Resposta curta

Não. Uma regra simples de tendência (ensemble de médias, momento multi-horizonte, média única) escolhida antes do OOS rende **+6% a +23% a.a. com Sharpe 0,4 a 1,0 depois do OOS**, contra **+42% a.a. e Sharpe 2,46** da Carteira 8 (das 34). A correlação diária com a Carteira 8 fica entre 0,23 e 0,45. Tirando a parte explicada pela regra simples, a Carteira 34 ainda tem Sharpe ~3 no resíduo: o retorno das aprovadas **não é** tendência de médio prazo disfarçada.

## O que elas têm em comum

- **Sempre posicionadas e simétricas.** 22 de 34 ficam no mercado mais de 95% do tempo; mediana 50% comprado / 45% vendido. Só 3 são só compradas.
- **Horizonte curto.** Trade mediano dura **2 dias**, ~70 trades/ano. O sinal de momento que mais se parece com a posição é o de **1 a 3 dias** (mediana 2,5 d), e mesmo assim a correlação é só 0,41. No ouro e no ETH o pico é em 1–3 dias; no BTC, 20–30 dias; no WTI quase nada se parece com momento (≤ 0,14).
- **Ganham onde tem tendência curta forte (cripto) e pouco ligadas a momento no WTI**, onde o ganho vem de outra coisa (reversão, funding).
- Resumo: são reversões de stop-and-reverse rápidas, que pegam movimentos de dias, cada uma com um "ruído" próprio, e é esse ruído descorrelacionado entre elas que faz a carteira.

## Regras simples testadas (4h, custo e funding da Lighter)

Famílias: média de sign(close − SMA_L) para L numa grade geométrica (ensemble de MAs), média de sign(retorno em L) (TSMOM), e uma única MA ou um único lookback; modos comprado+vendido ou só comprado, fracionário ou 1x. Uma configuração única para os 5 ativos, escolhida pelo Sharpe médio antes de 2023-05-17.

| Carteira (pesos iguais, 5 ativos) | Antes do OOS | Depois do OOS | corr c/ C8 |
| --- | --- | --- | ---: |
| **Carteira 8 (das 34)** | +111%, Sh 3,84 | **+42%, Sh 2,46, DD −11%** | — |
| Ensemble MA 3–100 d, L/S | +43%, Sh 1,41 | +13%, Sh 0,66 | 0,36 |
| TSMOM 3–100 d, L/S | +44%, Sh 1,44 | +6%, Sh 0,36 | 0,32 |
| TSMOM 2–30 d, só comprado | +26%, Sh 1,48 | +11%, Sh 0,91 | 0,34 |
| MA única 3 d, L/S | +43%, Sh 1,18 | +11%, Sh 0,56 | 0,43 |
| TSMOM 30 d, L/S | +62%, Sh 1,52 | +23%, Sh 0,99 | 0,28 |
| TSMOM 30 d, só comprado | +42%, Sh 1,59 | +15%, Sh 0,91 | 0,23 |

Por ativo: nenhuma regra passa no critério corrigido em XAU, US100 ou WTI (no WTI todas perdem, inclusive só comprado, por causa do funding de 67,7% a.a.). Só ETH, e às vezes BTC, passam. TSMOM 30 d no ETH passa antes e depois do OOS (+76% a.a., Sharpe 1,19 depois).

## Ressalvas

- A Carteira 8 das 34 foi montada com informação do período todo (os terços da aprovação incluem o pós-OOS), então o OOS dela é otimista; as regras simples foram escolhidas só com o trecho anterior. Mesmo descontando isso, a distância é grande.
- Regras simples rebalanceiam a posição fracionária a cada barra de 4h (aproximação da quantidade fixa por trade).
