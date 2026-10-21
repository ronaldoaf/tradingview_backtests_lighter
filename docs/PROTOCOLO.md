# Protocolo de teste das estratégias do TradingView

Nota de método usada em todos os estudos deste repositório.

## Fonte

O usuário passa só o final da URL do script; a URL completa é
`https://www.tradingview.com/script/` + esse final.

## Ordem dos ativos

Ativo padrão: **ouro (XAUUSD)**. Só se o resultado no ouro for positivo a estratégia é
estendida para **US100, BTC, WTI e ETH**. O objetivo é varrer muitas estratégias publicadas
sem gastar 5 ativos numa ideia que já morre no primeiro.

Antes de começar um teste novo, conferir a tabela do README para não repetir uma
estratégia já reprovada.

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

## Benchmarks

Uma célula de grade só interessa se bate **os dois**:

1. **Buy & hold** do próprio ativo no mesmo período (CAGR e Sharpe).
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
