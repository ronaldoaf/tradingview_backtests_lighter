# Binárias 1h em torno de CPI, Payroll e FOMC — BTC/ETH

Datas: CPI e Payroll pelas datas de vintage do ALFRED (CPIAUCSL, PAYEMS), 08:30 ET; FOMC 14:00 ET (reuniões regulares; cortes de emergência de mar/2020 fora).
~80 CPI, ~80 Payroll, ~53 FOMC (2020–set/2026). Entrada k ∈ {1,2,5,15,30,60} min após o evento (ou 1h antes); resultado = preço 60 min depois da entrada.
Regras: sempre ALTA, sempre BAIXA, seguir/reverter o movimento desde o evento, idem só quando o movimento é maior que a mediana do treino.
228 variantes. Mesmo split: treino < jun/24, validação jun/24–mai/25, OOS ≥ jun/25. Equilíbrio 54,05%, empate = perda.

## Resultado
- **CPI, seguir o movimento dos primeiros 1–5 min** é a única ideia consistente nos três períodos e nos dois ativos.
  Melhor: ETH, entrar 2 min após o CPI no sentido do movimento: treino 65% (52), validação 75% (12), OOS 73% (15).
  Validação+OOS: 20/27 = 74% (p = 0,027 contra 54%, sem corrigir pelas 228 variantes). BTC: 53–67% no OOS, mais fraco.
- **Payroll:** seguir o movimento perde (33–53%); reverter não chega a ser consistente.
- **FOMC "sempre ALTA"** parecia ótimo no treino (68–76%) e desabou na validação/OOS (18–45%). Clássico de regime (2020–21).
- Nada mais sobreviveu.

## Veredito
Amostra pequena demais: ~12 CPIs/ano → no máximo 12 apostas/ano por ativo. O sinal de CPI é plausível (o mercado continua na direção da surpresa),
mas 27 apostas fora do treino não separam edge de sorte com 228 variantes testadas. Vale acompanhar ao vivo/paper, não apostar pesado.

Arquivos: `scripts/study_binarias_eventos.py`, `results/binarias_eventos_grid.csv`, `results/binarias_eventos_raw.csv`.
