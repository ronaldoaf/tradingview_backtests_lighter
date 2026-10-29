# Em alta só compras, em baixa só vendas: ajuda?

Script: `scripts/study_lado.py`. Saídas em `results/lado/`. Continuação de [REGIME_SIMPLES.md](REGIME_SIMPLES.md): mesmas
4 regras de alta/baixa, mesmas estratégias aprovadas no treino, mesmos controles e placebos. A diferença é que agora
cada estratégia foi separada nas suas duas pontas, e em cada regime só fica a ponta a favor da tendência.

## Resposta curta

**Não.** A ideia por trás do teste é que as compras rendem mais em alta e as vendas rendem mais em baixa. Na validação
(partes 7–9) aconteceu o contrário nos 5 ativos: os trades a favor do regime renderam **menos** que os contra, de
14 a 33 pontos percentuais ao ano a menos na mediana das 4 regras (17 dos 19 casos medidos ficaram negativos). No OOS
(parte 10) a diferença foi positiva só no BTC e no ETH, que passaram quase todo o OOS em baixa.

Nas carteiras, o padrão é o mesmo dos estudos anteriores: o que ganhou na validação perdeu no OOS e vice-versa.

- **WTI**: na validação, ficar só com a ponta a favor deu +1,13 de Sharpe em todas as aprovadas e +1,55 com a
  aprovação feita por ponta (acima de 82% a 96% dos placebos). No OOS, as mesmas versões perderam (−0,59 e −1,28).
- **XAU**: escolher por ponta ganhou nas 4 regras na validação (+0,90) e perdeu nas 4 no OOS (−0,69).
- **US100, BTC e ETH**: perderam na validação e ganharam (US100, BTC) ou ficaram mistos (ETH) no OOS.
- De 91 combinações (uso × ativo × regra), 9 ficaram acima de 90% dos placebos na validação e **nenhuma** repetiu no
  OOS. A correlação entre o percentil da validação e o do OOS é **−0,14**.

Com o HMM, as regras simples e agora a separação por ponta, as três formas de usar o regime de mercado falharam no
mesmo teste. Não vejo mais o que tirar dessa linha com o histórico que temos.

## O que foi feito

**Séries por ponta.** A grade de cada ativo foi regerada guardando, para cada célula, a série diária só dos trades
comprados e a série só dos vendidos (`LADO=1` no `study_us100_4p.py`). Conferências:

- as duas juntas reproduzem a série original: (1 + compras)(1 + vendas) − 1 bate com ela até 3·10⁻⁸ nos 5 ativos;
- os CSVs regerados são iguais aos originais (mesmas células, mesmos trades, mesmo retorno) nos 5 ativos;
- o WTI sem os trades de abril de 2020, como na grade original.

**Usos testados**, cada um com as 4 regras (média de 200, cruzamento 50 × 200, momento de 12 meses, queda de 20%):

| Uso | O que faz | Controle |
|---|---|---|
| todas as aprovadas | cada aprovada no treino só com a ponta a favor do regime; peso igual | as mesmas, duas pontas |
| K6 das aprovadas | o mesmo na carteira K=6 teto 0,3 do `tvo.py` | a K6, duas pontas |
| escolhe por ponta | todo mês, as 6 aprovadas com melhor Sharpe das compras nos dias de alta passados e as 6 com melhor Sharpe das vendas nos dias de baixa passados; no dia, o grupo do regime vigente | as 6 de maior Sharpe no passado, duas pontas |
| aprovação por ponta | aprovação refeita no treino com as compras de todas as células medidas só nos dias de alta e as vendas só nos de baixa; K=6 teto 0,3 em cada ponta | a K6, duas pontas |
| informação | média, entre as aprovadas, de (compras em alta − compras em baixa) + (vendas em baixa − vendas em alta), em retorno a.a. | zero |

Na aprovação por ponta valem os critérios do `tvo.py` com dois ajustes: só contam as partes do treino com pelo menos
20 dias do regime (precisa de 2/3 delas positivas e de pelo menos 3 partes), e o mínimo é de 50 trades da ponta no
treino. Cada troca de regime paga duas pernas de custo por estratégia (fecha uma ponta, abre a outra). Placebos: a
série de regimes deslocada no tempo (100 deslocamentos). Na aprovação por ponta, cada placebo refaz a aprovação com o
regime deslocado.

## Resultados

Cada célula: diferença de Sharpe (uso − controle), mediana nas 4 regras · em quantas das 4 o uso ganhou do controle ·
percentil mediano contra os placebos. Na linha da informação: diferença em retorno a.a. · em quantas regras foi
positiva (só as que têm ao menos 20 dias de cada regime no período) · percentil.

#### Validação (partes 7–9)

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| todas as aprovadas | +0,23 · 4/4 · p75 | −0,33 · 0/4 · p10 | **+1,13 · 3/4 · p96** | −0,18 · 1/4 · p58 | −0,51 · 1/4 · p26 |
| K6 das aprovadas | −0,00 · 2/4 · p74 | −0,12 · 0/4 · p8 | +0,89 · 3/4 · p96 | −0,84 · 0/4 · p48 | −1,99 · 0/4 · p23 |
| escolhe por ponta | **+0,90 · 4/4 · p77** | −0,30 · 1/4 · p15 | +0,54 · 3/4 · p84 | −0,97 · 0/4 · p45 | −2,15 · 0/4 · p22 |
| aprovação por ponta | −0,17 · 0/4 · p58 | +0,01 · 2/4 · p14 | **+1,55 · 4/4 · p82** | −1,04 · 0/4 · p55 | −2,51 · 0/4 · p16 |
| **informação (a.a.)** | **−0,21 · 0/3 · p9** | **−0,21 · 0/4 · p13** | **−0,26 · 0/4 · p8** | **−0,14 · 1/4 · p47** | **−0,33 · 1/4 · p24** |

#### OOS (parte 10)

| Uso | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|
| todas as aprovadas | −0,49 · 0/4 · p60 | +0,38 · 4/4 · p56 | **−0,59 · 0/4 · p43** | +0,17 · 4/4 · p80 | +0,61 · 4/4 · p86 |
| K6 das aprovadas | −0,23 · 1/4 · p42 | +0,55 · 4/4 · p62 | −0,37 · 0/4 · p49 | +0,25 · 4/4 · p80 | −0,28 · 0/4 · p85 |
| escolhe por ponta | **−0,69 · 0/4 · p32** | +0,46 · 3/4 · p29 | −0,24 · 2/4 · p38 | +0,62 · 3/4 · p92 | −0,35 · 1/4 · p74 |
| aprovação por ponta | +0,12 · 3/4 · p76 | +0,38 · 4/4 · p24 | **−1,28 · 0/4 · p16** | +0,53 · 4/4 · p90 | −0,45 · 0/4 · p88 |
| informação (a.a.) | −0,05 · 1/3 · p67 | — | −0,04 · 2/4 · p45 | +0,98 · 2/2 · p88 | +0,61 · 3/3 · p69 |

No OOS o US100 ficou em alta o tempo todo, então não dá para medir a informação lá.

#### Controles (Sharpe, duas pontas)

| Carteira | Período | XAU | US100 | WTI | BTC | ETH |
|---|---|---|---|---|---|---|
| todas | valid | +0,65 | +1,13 | −0,56 | +0,59 | +0,68 |
| todas | oos | +0,79 | +0,16 | +0,69 | +0,91 | +0,44 |
| K6 | valid | +1,10 | +0,81 | −0,24 | +1,33 | +2,58 |
| K6 | oos | +0,04 | −0,21 | +0,66 | +0,54 | +1,93 |
| escolhe sem regime | valid | −0,32 | +0,64 | +0,67 | +1,40 | +2,77 |
| escolhe sem regime | oos | +1,11 | −0,38 | −0,03 | +0,61 | +1,31 |

São os mesmos números do estudo do HMM, o que confirma que as séries e as aprovadas são as mesmas.

A tabela regra a regra está em [`results/lado/resumo.md`](../results/lado/resumo.md). Nenhuma regra salva o resultado:
a mesma regra que vai bem num ativo na validação vai mal no OOS ou em outro ativo.

## Por que não funciona

1. **A ponta contra a tendência não é a que perde.** Somando as duas pontas, na validação os trades a favor do
   regime renderam menos que os contra em 17 dos 19 casos medidos. A explicação mais provável é que as aprovadas foram
   escolhidas por ganhar no treino inteiro, e boa parte delas ganha comprando quedas e vendendo altas; tirar a ponta
   contra a tendência corta justamente isso.
2. **O WTI mostra o risco de olhar só a validação.** Na validação o petróleo caiu 35%, e ficar só com as vendas na
   baixa ajudou muito. No OOS ele subiu 51%, e a mesma escolha perdeu.
3. **No OOS das criptos houve um regime só.** BTC e ETH passaram 76% a 100% do OOS em baixa, conforme a regra, então
   "só vendas" ganhou por um episódio. A validação já tinha mostrado o contrário.

## Como reproduzir

```bash
# séries por ponta (cerca de 20 min por ativo com J=4); grava em results/<ativo>_4p_8p_lado/
for N in $(seq 3 38) flawless ichimoku rsidiv vixfix zigzagpa; do
  ATIVO=xau SUF=_8p NP=8 FULL=1 LADO=1 python scripts/study_us100_4p.py $N
done
# no WTI, com EXCL=2020-04-01,2020-05-01 (como a grade original)
cd scripts
python study_lado.py              # 5 ativos x 4 regras, 100 placebos; ~4 min por ativo
python study_lado.py resumo       # só as tabelas, a partir dos CSVs
```

As pastas `results/<ativo>_4p_8p_lado/` (~250 MB cada) ficam fora do git, como as séries das grades originais.
