"""LRC com inclinacao minima: |slope| x N / ATR(L) >= S (subida da linha em N barras, em ATRs).
Configs 50/1.5/6/50 e 50/2/5/50, TF 15m/30m/1h, 5 ativos; janelas treino<2024, valid<jul/2025, teste."""
import os, sys, itertools
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from study_lrc import lrc, sim, stats, OUT, ASSETS
from tvlib import atr_rma
from study_engulf_psar import CUSTO, FUND
C1, C2 = pd.Timestamp('2024-01-01', tz='UTC'), pd.Timestamp('2025-07-01', tz='UTC')

def run_s(df, a, n, dev, k, L, S):
    c = df.close.values; b, up, lo = lrc(c, n); mid = (up + lo) / 2; sd = up - mid
    atr = atr_rma(df.high.values, df.low.values, c, L); ns = b * n / atr
    sig = np.where((ns >= max(S, 1e-12)) & (c < mid - dev * sd), 1, np.where((ns <= -max(S, 1e-12)) & (c > mid + dev * sd), -1, 0)).astype(np.int64)
    ei, xi, s, pi, px = sim(df.open.values, df.high.values, df.low.values, c, sig, atr, k)
    t = pd.DataFrame({'t_in': df.index[ei], 't_out': df.index[xi], 'd': s, 'p_in': pi, 'p_out': px})
    yrs = (t.t_out - t.t_in).dt.total_seconds() / (365 * 86400)
    t['ret'] = t.d * np.log(t.p_out / t.p_in) - 2 * CUSTO[a] - t.d * FUND[a] / 100 * yrs
    return t

if __name__ == '__main__':
    rows = []
    for a, tf in itertools.product(ASSETS, ['15m', '30m', '1h']):
        f = os.path.join(OUT, f'{a}_{tf}.parquet')
        if not os.path.exists(f):
            from tvlib import load_m1v, resample; resample(load_m1v(a), {'15m': '15min', '30m': '30min', '1h': '1h'}[tf]).to_parquet(f)
        df = pd.read_parquet(f)
        P = [df[df.index < C1], df[(df.index >= C1) & (df.index < C2)], df[df.index >= C2]]
        for (n, dev, k, L), S in itertools.product([(50, 1.5, 6, 50), (50, 2, 5, 50)], [0, 1, 2, 3, 5, 8]):
            r = dict(ativo=a, tf=tf, cfg=f'{n}/{dev}/{k}/{L}', S=S)
            for nm, p in zip(['tr', 'val', 'te'], P):
                s = stats(run_s(p, a, n, dev, k, L, S), p); r[nm] = s['cagr']; r[nm + '_n'] = s['tr']
            rows.append(r)
        print(a, tf, flush=True)
    g = pd.DataFrame(rows); g.to_csv(os.path.join(OUT, 'slope_min.csv'), index=False)
    g['pos3'] = (g.tr > 0) & (g.val > 0) & (g.te > 0)
    pd.set_option('display.width', 250); print(g.to_string())
