# Binárias AlphaX de 5, 10 e 30 min — BTC/ETH

Payout / acerto de equilíbrio: 5m 70% → 58,8% · 10m 75% → 57,1% · 30m 80% → 55,6% · (1h 85% → 54,1%).
Mesma grade de 1.776 regras do estudo de 1h (`scripts/study_binarias_1h.py --h=5|10|30`), mesmo split e filtro
(limite inferior 95% acima do equilíbrio no treino e na validação). Também a grade de eventos (`study_binarias_eventos.py 5|10|30`).

| Prazo | Finalistas | Melhor no OOS (entrada imediata) | Com 1 min de atraso |
|---|---|---|---|
| 5m | 0 | — | — |
| 10m | 5 | ETH z15 no 0,5% inferior → ALTA: 60,1% (1.119), EV +5% | 58,1%, EV +1,7% (≈ zero) |
| 30m | 7 | ETH z15 no 0,5% inferior → ALTA: 59,9% (963), EV +7,9%, p=0,004 | 58,2%, EV +4,7% |
| 1h (anterior) | 21 | ETH ma60 0,5% inferior → ALTA: 60,2% (713), EV +11% | 57,9%, EV +7% |

z15 = retorno dos últimos 15 min dividido pela vol de 1m (janela 60) × √15.

Eventos (CPI/Payroll/FOMC) em 5/10/30 min: nada sobrevive — as regras que passam no treino quebram na validação ou no OOS
(o "seguir o CPI" de 1h não se repete nos prazos curtos).

**Veredito:** quanto menor o prazo, pior: o payout cai mais rápido do que a previsibilidade sobe. 5m: nada. 10m: o edge some com
1 min de atraso. 30m: o mesmo efeito de 1h (comprar ETH depois de queda extrema), com edge menor. A melhor opção continua sendo 1h;
30m é segunda opção. Mesmas ressalvas: preço de referência da AlphaX ≠ Binance, apostas concentradas em crashes.
