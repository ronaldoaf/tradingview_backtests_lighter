# Gotōbi USDJPY (short 09:55→10:30 JST, stop 12 pips)

Dados: HistData M1 bid, jan/2016–out/2026 (EST fixo convertido para JST). Script: `scripts/study_gotobi_usdjpy.py`.
Dias Gotōbi: dias 5,10,15,20,25,30 (recuados ao dia útil anterior; feriados japoneses não tratados, só fins de semana e 1–3/jan, 31/dez).
Controle: mesmos horários em dias não Gotōbi.

| Grupo (sem custo) | n | média pips | t |
|---|---|---|---|
| Gotōbi total | 749 | +1,13 | 2,63 |
| treino 2016–20 | 352 | +0,67 | 1,22 |
| validação 2021–23 | 199 | +0,82 | 0,93 |
| OOS 2024–26 | 198 | +2,28 | 2,36 |
| Controle total | 1921 | +0,60 | 2,41 |

Com custo de 1,2 pip ida+volta, o Gotōbi total fica em −0,07 pip/trade (treino e validação negativos).
Custo real na Lighter (VPS /metrics, 00:50–01:35 UTC, 2–6/nov/2026): spread mediano entre 0,1 e 2,75 pips conforme o dia.

Conclusão: **reprovada**. O vídeo mostra +2,35 pips com 58% de acerto; aqui o bruto é +1,1 pip com 48,5%. Desse ganho, ~0,6 pip
aparece também nos dias de controle (o USDJPY tende a cair depois do fix todo dia), então o excesso atribuível ao Gotōbi é ~0,5 pip,
sem significância no treino nem na validação. Só 2022, 2024 e 2025 sustentam o resultado. Com o spread da Lighter, não sobra edge.
