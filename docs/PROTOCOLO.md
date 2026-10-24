# Protocolo de teste das estratégias do TradingView

Nota de método usada em todos os estudos deste repositório.

## Fonte

O usuário passa só o final da URL do script; a URL completa é
`https://www.tradingview.com/script/` + esse final.

## Ordem dos ativos

**Regra do usuário (2026-10-22, a partir do lote 12): toda estratégia é testada nos 5 ativos —
ouro (XAUUSD), US100, WTI, BTC e ETH — sem esperar o resultado do ouro.** Os scripts de lote rodam
com `python scripts/study_tvloteN.py xau us100 wti btc eth` e o doc do lote traz uma tabela por
ativo. Robustez (terços, OOS, custo, vizinhança) continua só para as células que batem o B&H
(a partir de 2026-10-23: Sharpe pelo menos o do B&H e t > 2, ver o critério abaixo).

Até o lote 11 a regra era outra: ouro primeiro e só estender aos outros 4 se o ouro passasse.

Antes de começar um teste novo, conferir a tabela do README para não repetir uma
estratégia já reprovada.

## Exemplos e templates

**Regra do usuário (2026-10-22):** script publicado como exemplo, template ou utilitário (ex.:
"Strategy Code Example", "Template Trailing Strategy", "Monthly Returns") não é testado. Entra na
tabela do README como *ignorado (template)* e o lote pega o próximo da lista no lugar.

## Execução

- Sinal no fechamento da barra, ordem na abertura da barra seguinte
  (Pine com `calc_on_every_tick=false`).
- Stop e alvo intrabar resolvidos no M1.
- Convenção conservadora: stop e alvo no mesmo minuto → o **stop** executa primeiro.
- Retornos sobre o nocional (1x), que é o que o Pine faz com
  `default_qty_type=percent_of_equity`.

## Custo

Por perna, `CUSTO[ativo]` = spread medido no livro da Lighter (~$1k de nocional), mais
`FUND[ativo]` = funding anual médio que o long paga (o short recebe), pro-rata ao tempo em
posição. Valores em `scripts/study_engulf_psar.py`.

| Ativo | Spread/perna | Funding a.a. (long paga) |
| --- | --- | --- |
| XAU | 0,75 bp | 13,8% |
| US100 | 1,2 bp | 4,5% |
| WTI | 1,0 bp | 67,7% |
| BTC | 0,5 bp | 10,9% |

O funding do WTI é alto o bastante para matar sozinho qualquer estratégia de long com
exposição relevante — vale olhar isso antes de rodar a grade.

## Métrica (revisão de 2026-10-23)

O CAGR, o Sharpe e o DD de `tvlib.summarize` vêm de `tvlib.equity_curve`: equity a 1x composta
**trade a trade**, cada trade usando o equity da entrada inteiro com quantidade fixa (o que o Pine faz com
`percent_of_equity`). O CAGR é `exp(Σ log(1 + ret) / anos) − 1`, com `ret` líquido de spread e funding.
O DD é simples (equity / máximo − 1). O Sharpe usa os retornos diários nos dias em que o ativo tem barra
(dia parado conta como zero), anualizado pelo número desses dias por ano; o Sharpe do B&H (`bh_sharpe`) sai
da mesma conta.

Até o lote 33 a curva somava `log(close).diff() × posição` com uma barra de atraso. Isso creditava ao
vendido `log(P0/P1)`, que é mais que o `1 − P1/P0` de um short de verdade, e inflava o CAGR de quem fica
vendido; o DD saía em log. Os números dos docs de lote até o 33 estão nessa conta antiga; o veredito
refeito de todas as células de robustez está em `results/study_veredito.txt` (`scripts/study_veredito.py`).

## Critério de aprovação (a partir de 2026-10-23)

Pensado para montar carteira, não para escolher a melhor estratégia isolada. Uma célula é aprovada se:

1. o líquido é **positivo em cada terço** do período;
2. o **Sharpe é pelo menos o do B&H** do ativo no período todo;
3. **t > 2** contra o controle aleatório;
4. continua **positiva com spread 4×** e **positiva com funding zero** (não depende de custo baixo nem do carry);
5. a correlação dos retornos diários com cada uma das já aprovadas fica **abaixo de 0,5** (entram por
   ordem de Sharpe).

O critério antigo (bater o CAGR do B&H no período todo, nos três terços, na 2ª metade e com custo 4×)
continua no relatório como referência. Vizinhança de parâmetros segue como ressalva no doc do lote.

## Benchmarks

Uma célula de grade só interessa se bate **os dois**:

1. **Buy & hold** do próprio ativo no mesmo período (Sharpe; o CAGR fica como referência).
2. **Controle aleatório**: para cada trade real, N entradas sorteadas com o **mesmo lado**,
   a **mesma duração** e a **mesma gestão de saída**. É o teste que separa sinal de beta.
   Reportado como estatística t da diferença.

## Robustez

Quem passa na grade ainda precisa sobreviver a:

- **Terços do período** — resultado concentrado num terço (tipicamente 2020-22) reprova.
- **Out-of-sample** — parâmetros fixados na primeira metade, medidos na segunda.
- **Multiplicador de custo** — 2× e 4× o spread. Estratégia que morre em 2× não tem margem.
- **Vizinhança de parâmetros** — célula boa cercada de células ruins é ilha, não edge.

## Reprovações frequentes

Vale checar estas antes de reimplementar o Pine inteiro:

- `lookahead_on` em `security()` — curva publicada boa que não existe ao vivo.
- Estratégia **sempre-no-mercado**: o benchmark é buy & hold, não zero.
- Risco/retorno abaixo de 1 com acerto perto de 50% — perda aritmética garantida.
- "ML"/"rede neural" que na verdade são constantes cravadas no código.
- Acerto alto obtido por saída assimétrica sem stop.

## Melhorias de infraestrutura

Regra do usuário: durante os testes, qualquer melhoria na infra que acelere a varredura ou que
descarte uma estratégia mais cedo pode ser implementada direto, sem pedir. Registrar a mudança
no commit e, se mudar o método, nesta página.

## Triagem rápida antes de rodar a grade

- **Versão do Pine ≤ 2 (ou sem `//@version`) com `security()`** → o histórico olha o futuro
  mesmo sem `lookahead` no código. Rodar só a versão honesta (candle HTF fechado); a publicada
  serve apenas para medir o tamanho do vazamento (ver [ZIGZAG_PA](ZIGZAG_PA.md)).
- **`scripts/tv_fetch.py <final-da-url> ...`** baixa o Pine para `pine/` (com fallback no
  pine-facade para scripts cujo HTML vem sem fonte) e já imprime versão, nº de `security()` e o
  alerta de vazamento. Rodar antes de ler o código.

- Toda estratégia que passar no critério de aprovação entra em `docs/APROVADAS.md` (configuração, resultado,
  robustez e ressalvas). Para refazer a lista: `python scripts/study_veredito.py <ativo>` para cada ativo e
  depois `python scripts/study_veredito.py --relatorio` (a célula nova precisa estar no `CELLS` do `_rob` do lote).
