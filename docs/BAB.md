# Betting Against Beta (Frazzini e Pedersen, 2014) nos perps da Lighter

**Veredito: reprovada nos dois universos.** Nenhuma das 44 variantes fica positiva no OOS, e as poucas que vão bem no treino não saem da faixa do acaso.

## Construção
- Beta como em FP: correlação de retornos de 3 dias (janela 2-3 anos) × razão de vols (1 ano), encolhido 0,6·β + 0,4. Também testei baixa volatilidade (vol de 1 ano) no lugar do beta.
- Quatro construções, para separar o que a crítica de Novy-Marx e Velikov (2022) aponta:
  - `fp`: pesos por rank e cada perna alavancada para beta 1 (o fator original);
  - `fp_dn`: pesos por rank, sem alavancar as pernas (dólar-neutro);
  - `ew_dn`: tercil baixo contra tercil alto, pesos iguais, dólar-neutro;
  - `ew_bn`: tercis com pesos iguais, beta-neutro.
- Rebalanceamento semanal e mensal. Alavancagem bruta limitada a 3x. Custo por lado é o `cost_5000` da Lighter (VPS; mínimo de 0,02%). O funding é o da Lighter (cripto: horário real desde 2025; ações, XAU e WTI: média anual de cada mercado na Lighter, com long pagando).
- Placebo: 200 rodadas do `fp` mensal com os betas embaralhados entre ativos.

## Cripto (BTC, ETH e as top 30 por volume na Binance que estão na Lighter, ~20/dia; diário 2020-2026)
Treino 2020-22, validação 2023-24, OOS 2025-26. Tabela completa em `grid_cripto.csv`.

| variante | treino Sharpe | valid. Sharpe | OOS Sharpe | OOS DD |
|---|---|---|---|---|
| beta vs BTC, fp, mensal | 1,65 | 0,61 | -0,64 | -63% |
| beta vs índice, fp, mensal | 1,45 | 0,65 | -0,52 | -69% |
| beta vs BTC, ew_dn, mensal | 1,13 | -0,23 | -0,39 | -68% |
| baixa vol, ew_dn, mensal | 0,53 | 0,24 | -0,16 | -66% |
| **placebo, p95** | 1,16 | 1,37 | 1,17 | |

- O treino forte vem da alavancagem da perna de beta baixo (`fp` e `ew_bn`). Sem ela (`fp_dn` e `ew_dn`), o Sharpe cai pela metade e a validação fica negativa, que é exatamente o ponto de Novy-Marx e Velikov. Mesmo o melhor treino (1,65) mal passa do p95 do placebo (1,16; o máximo foi 1,62). Os drawdowns ficam entre -80% e -90% já no treino.
- BTC: beta médio 1,0 vs BTC (0,72 vs índice). Fica no tercil baixo em 19% dos dias e no alto em 20%.
- ETH: beta médio 1,05 vs BTC. Fica no tercil alto em 37% dos dias e quase nunca no baixo, então o BAB tende a vendê-lo.

## Ações da Lighter + XAU, WTI e US100 (subjacente diário 2015-2026, beta vs Nasdaq 100)
São 29 a 44 ativos. Treino 2015-19, validação 2020-22, OOS 2023-26. Tabela completa em `grid_acoes.csv`.

| variante | treino | valid. | OOS |
|---|---|---|---|
| fp mensal | -0,95 | 0,53 | -1,34 |
| ew_dn mensal | -1,12 | 0,30 | -1,51 |
| baixa vol, ew_dn | -0,83 | -0,66 | -1,33 |
| placebo, média / p95 | -0,28 / 0,51 | -0,10 / 0,56 | -0,20 / 0,67 |

- O resultado é negativo em todas as variantes, com ou sem XAU e WTI, e fica abaixo da média do placebo no treino e no OOS.
- **Ressalva grande:** o universo são as ações que a Lighter lista hoje (NVDA, PLTR, HOOD, MU…). É um viés de sobrevivência a favor das vencedoras de beta alto, que joga contra o BAB. O teste não refuta o fator de FP no mercado amplo, mas mostra que ele não funciona *neste* universo negociável.
- XAU: beta médio 0,42 (pós-encolhimento; o beta bruto é ~0). Fica no tercil baixo em 92% dos dias, então o BAB o compraria alavancado.
- WTI: beta médio 0,64, no tercil baixo em 83% dos dias.
- US100: beta 1,0 por construção, quase sempre no meio do ranking.
- O funding das ações de beta alto é maior (MU 17%/ano, NBIS 16%, HOOD 16% contra 2-3% em AAPL e META) e favoreceria a perna vendida, mas não compensa o preço.

## Arquivos
`bab_cripto.py` (reaproveita `ls_indice_alts/bt.py`), `bab_acoes.py`, `fund_dl.py`, `grid_*.csv`, `placebo_*.csv`, `curvas_*.csv`, `metrics.json` (snapshot de custos da VPS de 08/11/2026, um domingo, então os spreads das ações estão mais largos que em dia útil).
