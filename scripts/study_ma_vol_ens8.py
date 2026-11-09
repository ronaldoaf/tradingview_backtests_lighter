"""Carteira de 8 (BTC, ETH, WTI, BRENT, XAU, XAG, US100, US500), varias medias + metade com vol alta, 4h.
Roda 24/7 (study_ma_vol_ens.run) e na janela do forex mantendo / zerando no fds (study_ma_vol_ens_fx.run).
Brent e US500: Dukascopy 1m (data/duka_jetta_dl.py). Brent: spread 1,5 bp, funding igual ao WTI (67,7% a.a.)."""
import glob, os, numpy as np, pandas as pd
import tvlib, study_ma_vol_cart6, study_ma_vol_cart as S
import study_ma_vol_ens as E, study_ma_vol_ens_fx as F
from study_engulf_psar import CUSTO, FUND
CUSTO['brent'] = 1.5e-4; FUND['brent'] = FUND['wti']
_l = S.load_m1v
def load(a):
    if a != 'brent': return _l(a)
    x = pd.read_parquet(os.path.join(tvlib.D, 'data', 'duka1m_brent', 'all.parquet'))
    x = x[~x.index.duplicated()].sort_index()[tvlib.OHLCV]; return x[x.high >= x.low]
AT = ['btc', 'eth', 'wti', 'brent', 'xau', 'xag', 'us100', 'us500']
if __name__ == '__main__':
    raw = {a: load(a) for a in AT}
    out = []
    for modo, m1s, fn in (('24/7', raw, lambda: E.run(AT, raw)),
                          ('forex mantem', None, lambda: F.run(AT, fx, False)),
                          ('forex zera sexta', None, lambda: F.run(AT, fx, True))):
        if m1s is None and 'fx' not in globals(): fx = {a: F.forex(raw[a]) for a in AT}
        g, cv, ro, idx, t0, t1 = fn(); g.insert(1, 'modo', modo); out.append(g)
        b = g.sort_values('treino_sh', ascending=False).iloc[0]
        m = (idx >= t0) & (idx <= t1); dd = lambda s: (s / s.cummax() - 1).min() * 100
        eq = np.exp(cv[(b.conjunto, b.filtro, b.x)][m].cumsum()); eb = np.exp((sum(ro[a] for a in AT) / 8)[m].cumsum())
        print(modo, b.conjunto, b.filtro, b.x, b[['treino_sh', 'valid_sh', 'teste_sh', 'valid_sh_sf', 'teste_sh_sf', 'treino_dd', 'valid_dd', 'teste_dd', 'valid_cagr', 'teste_cagr', 'bh_valid', 'bh_teste']].tolist(),
              'val', g.valid_sh.min(), g.valid_sh.median(), g.valid_sh.max(), 'teste', g.teste_sh.min(), g.teste_sh.median(), g.teste_sh.max(),
              'curva', round(eq.iloc[-1], 2), round(dd(eq)), 'bh', round(eb.iloc[-1], 2), round(dd(eb)), t0.date(), t1.date(), flush=True)
    pd.concat(out).to_csv('../results/ma_vol_ens8_grade.csv', index=False)
