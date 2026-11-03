# Overnight NY (compra 15:00 NY, vende 10:30 NY do próximo dia útil)

Script: `scripts/study_overnight.py` · resultado: `results/overnight_ny.csv`.
Entrada/saída na abertura do minuto 15:00 e 10:30 (horário de NY, DST tratado). Sexta segura até segunda.
Custo Lighter (2× `CUSTO` + funding pro-rata). Comparado com B&H e com o complemento intraday (10:30→15:00).

| Ativo | CAGR overnight | Sharpe | MDD | B&H CAGR / Sharpe | Terços (CAGR) | Custo 4× |
|---|---|---|---|---|---|---|
| XAU | -1,0% | 0,00 | -36% | 13,4% / 0,84 | -4 / -7 / +10 | -9,8% |
| US100 | +6,8% | 0,49 | -38% | 20,3% / 0,92 | +11 / 0 / +9 | -8,7% |
| WTI | -38,0% | -1,04 | -99% | 5,4% / 0,37 | todos negativos | -46,5% |
| BTC | +35,2% | 0,84 | -58% | 43,8% / 0,91 | +98 / +24 / +1 | +25,0% |
| ETH | +41,9% | 0,85 | -71% | 56,6% / 0,97 | +166 / +13 / -5 | +34,3% |

**Veredito: reprovada nos 5.** O overnight captura a maior parte do retorno do US100 (o intraday é negativo,
confirmando o efeito clássico), mas com ~0,4 de exposição não bate o B&H em CAGR nem Sharpe, e morre com custo 4×.
Em BTC/ETH o edge se concentra no primeiro terço e some no último. WTI é destruído pelo funding do long (67,7%/ano).
