# Lote 35 do TradingView: Linear Regression Pearson's R (2026-10-27)

Script `6VHnjgfp` (x11joe, Pine v4), um dos 5 de prioridade baixa em `estrategias/puladas_complexas.md`. Código em `scripts/study_tvlote35.py`.

**Regra do script.** A cada barra, testa janelas de 360, 348, ..., 24 barras e calcula o R de Pearson do close contra o tempo. Para na primeira janela com R ≥ 0,85 (baixa) ou R ≤ −0,71 (alta); se nenhuma atinge, fica o R da janela de 24. R < 0 compra, R > 0 vende; está sempre posicionado e inverte. O canal de regressão é só desenho e não entra na regra.

**Grade.** 15m a 1D × janela máxima 360 ou 120 × "sempre" (fiel) ou "forte" (zera quando nenhuma janela atinge o limiar) × os dois lados ou só comprado.

## Resultado: nenhuma entra

| Ativo | Células | Candidatas (CAGR > 0, Sharpe ≥ B&H, t > 2) | Veredito |
|---|---:|---:|---|
| XAU | 40 | 0 | melhor CAGR +6,5% contra +13,4% do B&H |
| US100 | 36 | 0 | melhor CAGR +14,8% contra +20,3%, t < 1 |
| WTI | 40 | 0 | todas negativas ou perto de zero |
| BTC | 36 | 4 | 2 passam mas são redundantes (corr 0,81 com Multi-MA, 0,74 com Force trade); 2 reprovam por t |
| ETH | 38 | 9 | 3 passam mas são redundantes (corr ~0,7 com Swing HULL+T3, BEST Supertrend, RSI-MA); 6 reprovam (último terço negativo e/ou t) |

O melhor número é o ETH 15m fiel (+102%, Sharpe 1,32), mas quase todo o ganho vem do primeiro terço (+579% / +35% / −14%) e a 2ª metade é negativa. Onde passa, repete as tendências de cripto já aprovadas. Resultado em `results/study_tvlote35_veredito.txt`.
