# Trendline Angle Pro V6 (Degree + Strategy) — teste em ouro (2026-10-21)

Estratégia: *"Trendline Angle Pro V6 (Degree + Strategy)"*, de Sanjay Dewan
([TradingView](https://www.tradingview.com/script/DUCODGjC-Trendline-Angle-Pro-V6-Degree-Strategy/)).
Pine v6 aberto — baixei a fonte completa (`PUB;d12a6a1e3c9d461b99b243c34ca80a99`) e traduzi linha a
linha, com todos os defaults, em `scripts/study_tlangle.py`.

**Primeiro achado, antes de qualquer número:** no Pine, **as trendlines não entram na estratégia**. Os
pivôs, a linha do swing maior, o leque de 20°/40°/45° e o painel são 100% visuais — `longSig`/`shortSig`
só usam o *ângulo ao vivo* (inclinação da regressão linear) e duas EMAs. O que o script negocia é:

```
angR    = atan( inclinação_OLS(close, 20) / ATR(14) × 5 ) em graus
longSig = angR >= 20°  e  EMA9 > EMA50  e  close > EMA50  e  cruzamento de close para cima da EMA9
saídas  = stop 1,5 ATR | alvo 2R | ou fecha a mercado quando |angR| < 20° ("ângulo virou flat")
```

Dados: XAUUSD M1 da Dukascopy, 2017-09-01 → 2026-10-04 (9,1 anos, 2,66 M barras). Sinais no TF alto,
execução no M1 (stop/alvo/gap resolvidos minuto a minuto). Custo 0,75 bp por perna (spread medido na
Lighter) — note que o **próprio Pine assume 0,05% = 5 bp por perna**, e reporto esse cenário também.
Controle: para cada trade, 20 entradas a mercado em minutos sorteados, **mesmo lado**, mesmo risco
relativo, mesma estrutura 1R/2R, mesma duração máxima.

## Veredito

**Não aprovada, e com o diagnóstico mais limpo até agora: o filtro de ângulo acrescenta exatamente zero.**
Nos defaults, o R bruto da estratégia é **+0,009** e o de uma entrada **aleatória** com o mesmo lado,
risco, estrutura e duração é **+0,008** — diferença +0,001R, **t = 0,03**. Depois do custo fica negativa.

| | n | /ano | acerto | R bruto | custo R | **R líq** | PF | R/ano | exposição |
|---|---|---|---|---|---|---|---|---|---|
| todos | 1122 | 123 | 35,7% | +0,009 | 0,043 | **−0,033** | 0,92 | −4,1 | 11,1% |
| long | 625 | 69 | 38,2% | +0,060 | 0,044 | **+0,016** | 1,04 | +1,1 | 6,2% |
| short | 497 | 55 | 32,6% | −0,054 | 0,042 | **−0,096** | 0,77 | −5,2 | 4,9% |
| IS 70% | 785 | 123 | 34,5% | −0,035 | 0,047 | −0,082 | 0,81 | −10,2 | |
| OOS 30% | 337 | 124 | 38,6% | +0,112 | 0,032 | +0,080 | 1,21 | +9,9 | |

A 1% de risco por trade: **−4,1%/ano**, contra **+13,4%/ano** de simplesmente comprar e segurar ouro.
Com os 5 bp/perna que o autor assume no próprio script: **−0,276R por trade, −34 R/ano** — a estratégia
só não é um desastre completo porque medimos com o spread real da Lighter, dez vezes menor.

### 1. O ângulo não filtra nada — e não é "independente de mercado" no sentido que o autor sugere

O autor vende a normalização por ATR como o diferencial: "os mesmos graus significam a mesma coisa em
ações, índices, cripto, commodities e forex". Só que `inclinação_por_barra / ATR` é uma razão **sem
escala**: o numerador e o denominador crescem juntos quando se muda de TF ou de ativo. Resultado no ouro:

| TF | mediana \|ângulo\| | barras ≥ 20° ("Moderate+") | barras ≥ 45° ("Steep") |
|---|---|---|---|
| 5 min | 26,4° | 62,0% | 17,6% |
| 15 min | 26,1° | 61,5% | 17,9% |
| 30 min | 27,0° | 62,8% | 19,2% |
| 1 h | 27,8° | 64,0% | 21,7% |
| 4 h | 30,4° | 67,8% | 26,3% |
| 1 dia | 30,0° | 67,1% | 26,9% |

A distribuição é praticamente **a mesma em todos os TFs** — o que confirma que a quantidade é invariante
de escala, mas também mostra que ela **não carrega informação sobre o horizonte**. Pior: o gatilho de 20°
passa **62–68% das barras**, e "Steep ≥ 45°" pega 18–27%. A instrução "fique de fora quando o ângulo
estiver Flat" descarta só um terço do tempo. Não é um filtro seletivo; é quase sempre ligado.

O `k45` ("barras para mover 1 ATR = 45°") também não é um grau de liberdade real: ele é uma reescala
monotônica do mesmo número. Com o gatilho fixado em um percentil do \|ângulo\|, varrer k45 = 2,5 / 5 / 10
dá o **mesmo conjunto de trades** (1h, p50: n = 930/846/840; 1h, p90: n = 111/111/111). Os 20° e 45° das
zonas não estão calibrados em nada — são percentis disfarçados de geometria.

### 2. Contra entrada aleatória, o lado long empata e o short é pior que o acaso

| | controle aleatório (R bruto) | estratégia (R bruto) | diferença | t |
|---|---|---|---|---|
| todos | +0,008 | +0,009 | +0,001 | **0,03** |
| long | +0,023 | +0,060 | +0,037 | 0,85 |
| short | −0,009 | −0,054 | **−0,045** | **−1,02** |

O short não só perde: ele perde **mais** do que vender ouro em minutos sorteados no mesmo período. Os
filtros de ângulo e EMA não evitaram nada — pioraram a seleção. E o long, que no agregado parece o lado
"bom", está dentro do ruído de uma compra aleatória em 9 anos de alta do ouro.

### 3. A saída pelo "ângulo flat" mata 62% dos trades no prejuízo

| saída | n | % |
|---|---|---|
| ângulo virou flat | 700 | 62% |
| stop (1,5 ATR) | 252 | 22% |
| alvo (2R) | 170 | 15% |

Como 36% das barras de 1h são "Flat", a posição morre em mediana **5 horas** — 5 barras. A mediana do R
líquido é **−0,259R**: o trade típico é fechado no meio do caminho, sem ter batido nem stop nem alvo,
pagando o spread. Desligar essa saída (`exitFlat = false`) melhora o resultado (R líq −0,001 contra
−0,033), ou seja, **o mecanismo central do script é destrutivo**. E a conta de break-even confirma o
aperto: um stop de 1,5 ATR com alvo 2R precisa de 33,3% de acerto; a estratégia entrega 35,7%, na linha.

### 4. Risco de cauda acima do planejado

O pior trade perdeu **−4,59R** contra 1R nominal. Duas causas, as duas reais: gaps de fim de semana /
abertura que atravessam o stop, e um detalhe fiel ao Pine — `strategy.exit` só é chamado quando
`position_size != 0`, isto é, no fechamento da barra já preenchida, então **a barra de entrada fica sem
stop e sem alvo**. Testei a variante que protege desde a entrada (`PROT=1`): muda pouco a média (−0,039
contra −0,033R). Quem ler "risque 0,5% a 1% do capital usando o stop de 1,5 ATR" precisa saber que 1% não
é teto — aqui o pior caso foi 4,6×.

### 5. Variantes (1h, defaults nos demais parâmetros)

| variante | n | acerto | R bruto | R líq | PF | R/ano |
|---|---|---|---|---|---|---|
| defaults | 1122 | 35,7% | +0,009 | −0,033 | 0,92 | −4,1 |
| alvo antes do stop no mesmo minuto (otimista) | 1122 | 35,7% | +0,009 | −0,033 | 0,92 | −4,1 |
| stop/alvo ativos já na barra de entrada | 1124 | 35,4% | +0,004 | −0,039 | 0,91 | −4,8 |
| sem a saída no ângulo flat | 1065 | 34,7% | +0,041 | −0,001 | 1,00 | −0,2 |
| sem entradas na zona Steep (`allowSteep=false`) | 913 | 34,6% | −0,020 | −0,063 | 0,85 | −6,3 |
| só long | 625 | 38,2% | +0,060 | +0,016 | 1,04 | +1,1 |
| só short | 497 | 32,6% | −0,054 | −0,096 | 0,77 | −5,2 |

Nenhuma salva. Note que **proibir a zona Steep piora** — o contrário do que a narrativa das zonas sugere.

### 6. Grade de robustez: 432 combinações, e o TF que o autor recomenda é o pior

Varri TF × ângulo mínimo × stop (ATR) × R:R × saída no flat × convenção de proteção:

| TF | R líq médio | custo R médio | R/ano médio | n médio |
|---|---|---|---|---|
| 15 min | **−0,088** | 0,093 | −46,7 | 4574 |
| 30 min | −0,032 | 0,063 | −9,4 | 2248 |
| 1 h | −0,018 | 0,044 | −2,8 | 1115 |
| 4 h | −0,035 | 0,021 | −1,2 | 298 |

O autor indica "5 a 15 minutos para intraday". Em 15 min o R **bruto** médio é +0,005 e o custo come
0,093R — o stop fica a ~17 bp, então o spread é 9% do risco. Não há margem para nada.

| ângulo mínimo | R líq médio | R/ano médio |
|---|---|---|
| 10° | −0,037 | −19,8 |
| 20° (default) | −0,049 | −15,6 |
| 30° | −0,044 | −9,7 |

Apertar o ângulo não ajuda. **87 das 432 combinações (20%) ficam positivas no líquido** — menos do que
os ~50% que se esperaria se o sinal fosse neutro e o custo fosse zero, e as que sobram têm um padrão
revelador: **todas desligam a saída no ângulo flat**, usam stop largo (2,5 ATR), alvo 3R e ficam
**32% a 65% do tempo expostas**. A melhor célula por R/ano (30 min, 2,5 ATR, 3R, sem saída no flat)
rende +10,7 R/ano com 64,7% de exposição — ainda **abaixo do buy & hold de +13,4%/ano**, nos dois lados,
com 1741 trades de custo. Isto é, a grade "resolve" o problema transformando a estratégia em
"fique comprado/vendido em ouro com stop largo" — beta, não alfa.

### 7. Calibrando como o autor manda — e o ângulo some do resultado

O autor é explícito: *"os ajustes que servem para o Nifty não servem para Bitcoin ou Ouro, então calibre
a escala do ângulo, as EMAs e o stop para cada mercado"*. Fiz isso: 3240 combinações de TF (5 min a
1 dia) × gatilho de ângulo como **percentil** do \|ângulo\| observado (p0/p50/p75/p90/p95, para o filtro
ser de fato seletivo) × EMAs (9/50, 20/100, 5/20) × stop (1,0/1,5/2,5 ATR) × R:R (1/2/3) × lado ×
saída no flat. Resultado: **1266 das 3240 ficam positivas no líquido (39%)**.

| TF | n médio | R bruto | custo R | R líq | R/ano |
|---|---|---|---|---|---|
| 5 min | 6319 | +0,036 | **0,167** | **−0,132** | −136,1 |
| 15 min | 2043 | +0,013 | 0,086 | −0,073 | −20,3 |
| 30 min | 1001 | +0,049 | 0,062 | −0,012 | −3,7 |
| 1 h | 498 | +0,064 | 0,044 | +0,020 | +0,3 |
| 4 h | 132 | +0,094 | 0,021 | +0,073 | +0,7 |
| 1 dia | 26 | +0,232 | 0,008 | +0,224 | +0,4 |

Confirma o padrão: **a faixa que o autor recomenda para intraday (5–15 min) é a pior da varredura
inteira** — em 5 min o custo sozinho come 0,167R, quatro vezes o R bruto. No diário o R por trade é bom
(+0,224) mas são 26 trades em 9 anos: +0,4 R/ano, irrelevante.

E a parte que interessa: **as melhores células desligam o ângulo.** Das 25 melhores por R/ano, as três
primeiras são todas `flat=0` (sem a saída no ângulo), `ambos=0` (só long) e com o gatilho em p0 ou p50 —
e **p0 reduz o "ângulo" a um simples teste de sinal da inclinação** (`angR ≥ 0`), isto é, as zonas de
20°/45° desaparecem. A melhor célula de todas:

> 30 min, só long, EMA 5/20, stop 2,5 ATR, alvo 3R, sem saída no flat, ângulo ≥ 0°:
> n = 1065, R líq **+0,170**, **+19,9 R/ano**, 59,8% de exposição.

Parece ótimo — até olhar os três testes que importam:

- **controle aleatório:** +0,059 contra +0,206 bruto, diferença +0,147 com **t = 2,10**. Escolhida entre
  **3240 combinações**, um t de 2,1 é exatamente o que o acaso produz: sob a hipótese nula o maior t de
  3240 sorteios fica tipicamente acima de 3,5. As cinco melhores dão t entre 1,85 e 2,17 — nenhuma
  sobrevive a qualquer correção para múltiplos testes.
- **custo do próprio autor:** com os 5 bp/perna que o Pine assume, **todas as cinco melhores ficam
  negativas** (−0,015 a −0,170R). Elas só existem porque medimos com o spread da Lighter.
- **o que de fato está sendo negociado:** só long, 60% do tempo exposto, stop largo, alvo distante, sem
  a saída no ângulo e sem filtro de ângulo. Isto é "fique comprado em ouro com stop largo" — e +19,9%/ano
  a 1% de risco contra +13,4% do buy & hold, com 60% de exposição e 1065 trades de custo, não é um prêmio
  que justifique o aparato. O "só long" também foi escolhido *depois* de ver o short perder em 9 anos de
  alta do ouro.

A varredura por percentil ainda mostra que k45 não é grau de liberdade: fixado o gatilho em percentil,
k45 = 2,5/5/10 dá o mesmo n e o mesmo R (tabela da seção 1).

## Conclusão

A tradução está fiel (inclinação OLS, ângulo, EMA/RMA e risco = 1,5 ATR conferidos contra recálculo
independente; nenhum trade sobreposto) e o teste é limpo. O problema é conceitual, não de implementação:

1. o ângulo normalizado por ATR tem a **mesma distribuição em todo TF e ativo**, então a "zona" não diz
   nada sobre força de tendência — e o corte de 20° deixa passar dois terços das barras;
2. contra entrada aleatória de mesmo lado e estrutura, a diferença é **t = 0,03**;
3. a saída pelo ângulo flat, que é a ideia do script, **destrói valor** (62% dos trades, mediana −0,26R);
4. calibrando por mercado como o autor pede, 3672 combinações no total, as melhores **desligam o ângulo
   e a saída no ângulo** — o que sobra é exposição direcional long ao ouro, com t ≈ 2 contra entrada
   aleatória (nada, depois de 3240 tentativas) e negativa com o custo que o próprio Pine assume.

Mesmo diagnóstico das últimas estratégias de vídeo/TradingView testadas aqui (SMA30, SMC, CRT, Ruiz MTF,
Gold Trail): o filtro bonito não cria borda. A diferença é que aqui ele é mensuravelmente **nulo** —
o t = 0,03 contra o controle é o resultado mais próximo de zero que já saiu desta bancada.

Para crédito do autor: a descrição dele é honesta ("o lucro vem do controle de risco e de testar em cada
mercado, não do indicador"; "calibre para cada mercado"; "faça backtest com comissão e slippage
realistas"). Este teste é exatamente isso, e no ouro a resposta é não.

Arquivos: `scripts/study_tlangle.py`, `scripts/study_tlangle.txt` (saída completa),
`scripts/study_tlangle_xau_trades.csv` (1122 trades), `scripts/study_tlangle_grid.csv` (432 combinações),
`scripts/study_tlangle_cal.py` + `.txt` + `.csv` (calibração por mercado, 3240 combinações).
