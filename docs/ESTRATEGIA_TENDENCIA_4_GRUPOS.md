# Estratégia: Tendência em 4 grupos com escolha do ativo mais forte

Carteira sempre posicionada (comprada ou vendida) em 4 componentes, um por grupo de ativos. Em cada grupo entra o ativo com a tendência mais forte no momento. O tamanho de cada componente é ajustado pelo risco, e a carteira mira uma volatilidade fixa.

Código: `scripts/study_ma_vol_sel_v2.py` (versão final), `scripts/study_ma_vol_sel.py` (seleção) e `scripts/study_ma_vol_sel_v3.py` (testes adicionais). Detalhe de todos os testes em `docs/MA_VOL_SELECAO.md`.

## 1. Universo

| Grupo | Candidatos (escolhe 1) |
|---|---|
| Cripto | BTC ou ETH |
| Índices dos EUA | US100 ou US500 |
| Petróleo | WTI ou BRENT |
| Metais | XAU ou XAG |

Todos são perpétuos da Lighter. Gráfico de **4h**, operando **24/7**.

## 2. Regras

Todas as contas são feitas no **fechamento** de cada barra de 4h, e a ordem é executada na **abertura da barra seguinte**.

### 2.1 Direção de cada ativo (várias médias)
Para cada ativo, calculam-se 10 médias do fechamento: **SMA e EMA de 100, 150, 200, 250 e 300 barras de 4h** (de ~17 a ~50 dias).

- Cada média dá um sinal: **+1** se o preço está acima dela, **−1** se está abaixo.
- **Sinal do ativo = média dos 10 sinais**, um número entre −1 e +1. Por exemplo, +0,6 significa que 8 médias dizem "comprado" e 2 dizem "vendido".
- O sinal define o lado e a convicção: +1 é comprado cheio, −1 vendido cheio, e valores intermediários dão posição parcial.

### 2.2 Escolha do ativo em cada grupo (tendência mais forte)
Para cada ativo:

```
força = | média de log(preço / média_i), sobre as 10 médias | ÷ volatilidade de ~20 dias (desvio dos retornos de 4h em 120 barras)
```

Ou seja, mede o quanto o preço está afastado das médias, em unidades de volatilidade. **Em cada grupo entra o ativo de maior força**, e o outro fica zerado. A escolha é refeita a cada barra, **sem tempo mínimo**: testes com espera mínima de 1 a 20 dias pioraram o resultado.

### 2.3 Peso de cada grupo (inverso da volatilidade)
```
peso_grupo = (1 / vol_20d do ativo escolhido) ÷ soma dos (1 / vol_20d) dos 4 grupos
```
Os pesos somam 1. Assim cada grupo contribui com risco parecido: a cripto, mais volátil, recebe peso menor e o ouro recebe peso maior.

### 2.4 Tamanho da carteira (volatilidade-alvo)
- Retorno diário da carteira "cheia" = soma de (peso × sinal × retorno de cada ativo).
- Vol da carteira = desvio desses retornos diários nos últimos 20 dias, anualizado (×√252), medido **até o dia anterior**.
- **Escala = min(8% ÷ vol da carteira, 2)**. A carteira mira 8% a.a. de volatilidade, com teto de 2× o nocional.
- **Posição final de cada ativo = escala × peso_grupo × sinal_ativo**, como fração do capital.

### 2.5 Resumo em uma linha
> A cada 4h: em cada grupo, pegue o ativo mais afastado das suas médias (em unidades de vol). Posicione-se na direção da média dos 10 sinais SMA/EMA 100–300, com peso inverso à vol, escalando a carteira para 8% a.a. de vol (máximo 2×).

## 3. Como foi testado
- **Dados:** 1m da Binance (BTC, ETH) e da Dukascopy (XAU, XAG, WTI, BRENT, US100, US500), reamostrados em 4h. O período comum vai de **01/01/2020 a 31/08/2026**.
- **Divisão por tempo:** 60% treino (até 31/12/2023), 20% validação (até 01/05/2025) e 20% teste (até 31/08/2026). A configuração foi escolhida pelo Sharpe do **treino**. O critério de aprovação foi Sharpe da validação > 0,5.
- **Custos:** spread medido no livro da Lighter por perna, a cada mudança de posição: BTC 0,5 bp, ETH 0,35, XAU 0,75, XAG 0,65, WTI 1,0, BRENT 1,5, US100 e US500 1,2 bp. Mais o funding anual médio, pro-rata, que o comprado paga e o vendido recebe (WTI 67,7%, BRENT igual ao WTI, XAU 13,8%, XAG 16,2%, BTC 10,9%, ETH 11,2%, US100 4,5%, US500 3,1%).
- **Sharpe:** calculado com retornos diários.

## 4. Resultados

| | Treino | Validação | Teste |
|---|---:|---:|---:|
| Sharpe (com funding) | 1,29 | **0,90** | **0,97** |
| Sharpe sem funding | — | 1,02 | 0,99 |
| CAGR | — | +13,5% | +14,1% |
| Drawdown máximo | — | −6,9% | −5,6% |
| Exposição bruta média | — | — | ~0,66× |

**Robustez da grade** (as 20 combinações de conjunto de médias × alvo de vol, com teto 2 e pesos inverso da vol): a validação ficou em pelo menos 0,59 e o teste em pelo menos 0,87, com medianas de 0,80 e 0,97. O resultado não depende de um parâmetro específico.

### Evolução até a versão final (Sharpe treino / validação / teste)
| Passo | Sharpe | Comentário |
|---|---|---|
| Uma média por ativo, ativo isolado | — | nenhum ativo passou na validação e no teste ao mesmo tempo |
| Carteira de 5, uma média (SMA150) | 1,38 / 0,57 / 0,47 | positiva, mas frágil à escolha da média |
| Carteira de 5, várias médias | 1,11 / 0,95 / 0,78 | a escolha da média deixa de importar |
| Sem fim de semana (janela forex) | pior | a validação cai para ~0,3–0,4 |
| Carteira de 8 (todos) | 1,02 / 0,59 / 0,59 | Brent e US500 repetem WTI e US100 (correlação ~0,9) |
| 4 grupos, escolha pela força, pesos iguais | 1,07 / 0,56 / 0,92 | |
| **+ inverso da vol + vol-alvo 8%** | **1,29 / 0,90 / 0,97** | **versão final** |

### Testes que não entraram na versão final
- **Tempo mínimo antes de trocar de ativo (1 a 20 dias):** piora. O ganho vem da troca rápida.
- **Gráfico de 1h:** não melhora. O teste cai para 0,47–0,62.
- **Zerar quando as médias discordam:** praticamente sem efeito.
- **Ficar fora do grupo sem tendência forte:** resultado inconsistente entre os períodos.

## 5. Riscos e ressalvas
- **Custo de execução é o ponto crítico.** Com 2× o spread, o Sharpe fica em 0,75 / 0,81. Com 4×, cai para 0,44 / 0,51. É preciso executar perto do spread medido (ordens limite ou maker) e conferir o custo real na VPS.
- **Quanto vale a escolha do ativo:** no controle aleatório (50 sorteios do ativo de cada grupo, com a mesma frequência de trocas), a escolha real supera ~80–96% dos sorteios. Mas o sorteio já tem Sharpe de 0,45–0,71 fora do treino. Boa parte do resultado vem da tendência e da diversificação, e a escolha soma cerca de +0,3 de Sharpe.
- **O Sharpe do treino é otimista:** fora dele a referência é ~0,9.
- **A estratégia ganha mais em tendências longas** (como o bear de 2022). Em mercados de alta, tende a empatar com o buy & hold, com drawdown bem menor.
- **Funding é uma premissa:** usei médias históricas. O funding real de 2026 no petróleo (negativo) muda pouco o resultado (0,87 / 0,85).
- **Histórico de ~6,7 anos:** com Sharpe ~0,9 fora do treino em ~2,7 anos, a evidência estatística ainda é moderada.

## 6. Operação na prática
1. A cada fechamento de 4h (UTC 00, 04, 08, 12, 16, 20), atualizar as médias, a força e a vol dos 8 ativos.
2. Escolher 1 ativo por grupo, calcular o sinal, os pesos e a escala.
3. Ajustar as posições na Lighter para os alvos, de preferência com ordens limite. Ignorar ajustes muito pequenos, por exemplo menores que 5% do alvo, para economizar custo. **Essa banda ainda não foi testada.**
4. Alavancagem: a exposição bruta média é ~0,66× e o teto 2×. Para mirar mais retorno, aumentar o alvo de vol (10% deu Sharpe parecido, com CAGR ~17% e DD −7 a −9%).
