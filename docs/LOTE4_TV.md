# Lote 4 do TradingView: 3 estratégias de tendência (2026-10-21)

Ativo padrão: **ouro (XAUUSD)**, M1 Dukascopy, 2017-09-01 → 2026-10-04. Sinal no fechamento, ordem
na abertura seguinte. Custo 0,75 bp/perna + funding 13,8% a.a. no ouro. Controle: mesmo lado e
mesma duração, entrada sorteada.

Código: `scripts/study_tvlote4.py` (grade `results/study_tvlote4_<ativo>_grid.csv`, saída
`results/study_tvlote4*.txt`) e `scripts/study_tvlote4_rob.py` (robustez). Fontes Pine baixadas
com o novo `scripts/tv_fetch.py` (em `pine/`).

| # | Estratégia | Ouro | Veredito |
|---|---|---|---|
| 26 | AI SuperTrend x Pivot Percentile (PresentTrading, `eC3qAYNQ`) | 0/48 batem o B&H, melhor +11,4% a.a. | reprovada |
| 27 | Pivot Point SuperTrend (LonesomeTheBlue, `DwdC6FT4`) | empata com o B&H (+13,4%), t≈2–3 contra o controle | **candidata no ETH**, não aprovada |
| 28 | Trend Direction Helper (Daveatt, `dzpmnane`) | 0/120 batem o B&H | reprovada |

---

## 1. AI SuperTrend x Pivot Percentile (`eC3qAYNQ`, Pine v5)

Dois SuperTrends sobre uma "VWMA" que multiplica o **close do TF maior** (6h e 12h) pelo **volume
do gráfico**, cada um com um "KNN" (k=6, n=48). O KNN inclui o próprio ponto corrente (distância 0,
peso 10⁶), então a "previsão" é praticamente o rótulo da barra atual: `WMA(close,10) > WMA(ST,80)`.
Entrada exige os dois SuperTrends e os dois KNN concordando, filtro ADX/DMI "diário" e Pivot
Percentile; saída por stop em `SuperTrend ∓ 3,5·ATR` ou entrada contrária.

- `request.security` de v5 com `lookahead_off`: sem vazamento.
- O filtro ADX diário é calculado com `HTF_High - HTF_High[1]` **na barra do gráfico**, onde o
  valor diário só muda uma vez por dia. O DM fica zero quase sempre, o ADX vira `na` e o filtro só
  libera 0,7% das barras. Sem ele a estratégia opera, mas não melhora.
- O array de janelas do Pivot Percentile sobrescreve os índices 3 e 4; as janelas 6 e 7 ficam `na`.
- Defaults: +1,4% a +3,3% a.a. contra +13,4% do B&H, t entre −0,6 e +1,3. Grade de 48 células
  (4 pares de TF × 3 fatores × ADX on/off × long/ambos): nenhuma bate o B&H; a melhor, sem ADX e
  fator 2, faz +11,4% a.a.

## 2. Pivot Point SuperTrend (`DwdC6FT4`, Pine v4)

SuperTrend cujo centro é uma média móvel dos pivôs (`center = (2·center + pivô)/3`), com ATR(10)×3.
Flip long/short a cada virada (sempre no mercado). Sem `security()`, sem repaint: o pivô só entra
quando confirmado `prd` barras depois.

**Ouro**: 176 de 185 células com líquido > 0 e 16 com t > 2 contra o controle, mas nenhuma acima do
B&H: as melhores **empatam** (+13,4% a.a., Sharpe 0,75 contra 0,73 do B&H). Robustez das 5 melhores:
líquido positivo em quase todos os terços, mas perde do B&H no terço 3 (alta de +31% a.a. do ouro)
e cai para +3% a +11% a.a. com custo 4×. Reprovada no critério do protocolo.

Como o líquido contra o controle era positivo, foi estendida aos outros ativos:

| Ativo | B&H a.a. (Sharpe) | células liq>0 | t>2 | CAGR>B&H |
|---|---|---|---|---|
| US100 | +20,3% (0,86) | 163/188 | 7 | 0 |
| BTC | +43,9% (0,49) | 178/186 | 7 | 5 (1D com 15–23 trades, e 1h p5 f4 a20 por 1 ponto) |
| **ETH** | +56,8% (0,45) | **185/185** | **22** | **37** |
| WTI | +5,4% (0,12) | 43/190 | 0 | 21 (só porque o B&H é quase zero; líquido negativo) |

**ETH** é o único ponto interessante até agora no repositório. Long/short, as 95 células têm
líquido positivo em todos os 5 TFs, com Sharpe mediano 0,40–0,45 (igual ao do B&H, 0,45). As
melhores, como `15min p5 f2 a10`, fazem +81% a.a. contra +57% do B&H, com Sharpe 0,62 e t=3,8:

| 15min p5 f2 a10 | período | CAGR | B&H | t |
|---|---|---|---|---|
| terço 1 | 2020-01 → 2022-04 | +83% | +330% | 1,1 |
| terço 2 | 2022-04 → 2024-07 | +83% | +1% | 1,7 |
| terço 3 | 2024-07 → 2026-09 | +72% | −11% | 2,2 |
| custo 2× | | +70% | +57% | 2,7 |
| custo 4× | | +49% | +57% | 3,1 |

O retorno é estável entre os terços e quase independente da direção do ETH, o oposto do
buy & hold. **Não está aprovada**, por três motivos:

1. O custo do ETH (`CUSTO['eth']`) é uma **estimativa igual ao do BTC** (0,5 bp e 10,9% de funding),
   não medida na Lighter. Com 640 trades/ano, 4× o custo já tira a vantagem sobre o B&H.
2. É 1 de 185 células. A vizinhança é boa (todas positivas), mas a escolha da melhor ainda é garimpo;
   falta walk-forward com a escolha feita só no passado.
3. O drawdown é grande (−69% em log, ≈ −50%) e a mesma regra não funciona em US100 e WTI.

Próximo passo sugerido: medir o spread do ETH na Lighter e rodar walk-forward.

## 3. Trend Direction Helper (`dzpmnane`, Pine v4)

O "TS(RISK)" com loops e tabelas se reduz a **%R de 1 barra**: `value2 = 100·(close−low)/(high−low)`
(o `wpr(1,0556)` usa comprimento 1). `up` quando o fechamento fica no topo da barra (> 60+RISK)
depois de um fechamento no fundo (< 20−RISK), e vice-versa. Entrada em `up[1]`/`dn[1]` e saída no
cruzamento SMA 7/20. O resto (zigzag, suportes, linhas) é desenho.

Defaults de −41% a.a. (15m, 3.400 trades/ano) a +3% (1D). Grade de 120 células (RISK × SMAs ×
long/ambos): 0 batem o B&H e 0 têm t > 2. O bruto por trade é ~0 bp: o giro só gera custo.
