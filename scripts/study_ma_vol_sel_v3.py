"""Pontos 3, 4 e 6 sobre a melhor versao (SMA+EMA 100-300, pesos inverso da vol, vol-alvo 8% teto 2):
 3) zerar quando as medias discordam: |media dos sinais| < k  (k = 0,2 / 0,4 / 0,6);
 4) ficar fora do par quando a forca do ativo escolhido < percentil q da propria forca no ultimo ~1 ano (q = 20/40/60);
 6) custos: spread 2x e 4x; funding de WTI/Brent com o valor medio real da Lighter em 2026 (-26% / -29% a.a.).
Todas as variantes tambem com o filtro 'metade > 10%' e com 'alvo 10% teto 2' para checar se o efeito depende do dimensionamento."""
import numpy as np, pandas as pd
import study_ma_vol_sel_v2 as V
from study_ma_vol_ens import SETS
from study_engulf_psar import CUSTO, FUND
BASE = SETS['SMA+EMA 100-300']
sig0, frc0 = V.sinais(BASE)
DIM = [('alvo2', 0.08), ('alvo2', 0.10), ('abs', 0.10)]


def run(tag, sig, frc, **kw):
    out = []
    for kind, x in DIM:
        r, r_sf, gr = V.carteira(sig, frc, 'ivol', kind, x)
        out.append(dict(variante=tag, dim=f'{kind} {x}', **V.mets(r, r_sf, gr)))
    return out


rows = run('base', sig0, frc0)
for k in (0.2, 0.4, 0.6):
    rows += run(f'3) zera se |sinal|<{k}', {a: s.where(s.abs() >= k - 1e-9, 0.0) for a, s in sig0.items()}, frc0)
for q in (0.2, 0.4, 0.6):
    sig = {}
    for g in V.GR:
        best = np.maximum(frc0[g[0]], frc0[g[1]])
        lim = best.rolling(6 * 365, min_periods=6 * 120).quantile(q)
        fora = best < lim
        for a in g: sig[a] = sig0[a].where(~fora, 0.0)
    rows += run(f'4) fora do par se forca<p{int(q*100)}', sig, frc0)
c0 = dict(CUSTO)
for m in (2, 4):
    for a in V.AT: CUSTO[a] = c0[a] * m
    rows += run(f'6) spread {m}x', sig0, frc0)
for a in V.AT: CUSTO[a] = c0[a]
f0 = dict(FUND); FUND['wti'], FUND['brent'] = -26.3, -29.0
rows += run('6) funding WTI/Brent 2026 (-26/-29%)', sig0, frc0)
FUND.update(f0)
g = pd.DataFrame(rows); g.to_csv('../results/ma_vol_sel4_v3.csv', index=False)
pd.set_option('display.width', 250)
print(g[['variante', 'dim', 'treino_sh', 'valid_sh', 'teste_sh', 'valid_dd', 'teste_dd', 'valid_cagr', 'teste_cagr', 'teste_bruto']].to_string(index=False))
