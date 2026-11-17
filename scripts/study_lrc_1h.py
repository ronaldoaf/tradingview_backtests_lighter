"""LRC em 1h: treino ate dez/2023 (grade), validacao jan/2024-jun/2025, teste jul/2025+. Mesma logica de study_lrc.py.
Escolha: maior CAGR no treino com as duas metades positivas; o teste so e olhado no fim."""
import os, sys, itertools
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from tvlib import load_m1v, resample
from study_lrc import run, stats, OUT, ASSETS
TF = os.environ.get('TF', '1h')
C1, C2 = pd.Timestamp('2024-01-01', tz='UTC'), pd.Timestamp('2025-07-01', tz='UTC')

def bars(a):
    f = os.path.join(OUT, f'{a}_{TF}.parquet')
    if not os.path.exists(f): resample(load_m1v(a), {'1h':'1h','30m':'30min'}[TF]).to_parquet(f)
    return pd.read_parquet(f)

def parts(df): return [('TR', df[df.index < C1]), ('VAL', df[(df.index >= C1) & (df.index < C2)]), ('TESTE', df[df.index >= C2])]

grid = list(itertools.product([50, 100, 200, 300, 500], [1.5, 2, 2.5, 3], [1, 1.5, 2, 3, 4, 6], [14, 50]))
fix, rows, best = [], [], []
for a in ASSETS:
    df = bars(a); P = parts(df); tr = P[0][1]
    for nm, p in P: fix.append(dict(ativo=a, per=nm, **stats(run(p, a, 200, 2, 2, 14), p)))
    for n, dev, k, L in grid:
        t = run(tr, a, n, dev, k, L); h1 = t[t.t_in < tr.index[0] + (tr.index[-1] - tr.index[0]) / 2].ret.sum()
        r = dict(ativo=a, N=n, dev=dev, k=k, L=L, ok=(h1 > 0) & (t.ret.sum() - h1 > 0), **stats(t, tr))
        r['val_cagr'] = stats(run(P[1][1], a, n, dev, k, L), P[1][1])['cagr']; rows.append(r)
    g = pd.DataFrame([r for r in rows if r['ativo'] == a]); x = g[g.tr >= 30].sort_values('cagr', ascending=False)
    b = (x[x.ok] if x.ok.any() else x).iloc[0]
    sv = stats(run(P[1][1], a, int(b.N), b.dev, b.k, int(b.L)), P[1][1])
    st = stats(run(P[2][1], a, int(b.N), b.dev, b.k, int(b.L)), P[2][1])
    best.append(dict(ativo=a, cfg=f'{b.N}/{b.dev}/{b.k}/{b.L}', TR_cagr=b.cagr, TR_tr=b.tr, VAL_cagr=sv['cagr'], VAL_pf=sv['pf'],
                     VAL_bh=sv['bh'], TESTE_cagr=st['cagr'], TESTE_pf=st['pf'], TESTE_tr=st['tr'], TESTE_bh=st['bh'],
                     grade_tr_pos=round(100 * (g.cagr > 0).mean()), grade_val_pos=round(100 * (g.val_cagr > 0).mean()),
                     tr_e_val_pos=round(100 * ((g.cagr > 0) & (g.val_cagr > 0)).mean())))
    print(a, 'ok', flush=True)
fix = pd.DataFrame(fix); print(fix.to_string()); fix.to_csv(os.path.join(OUT, f'fixo_{TF}.csv'), index=False)
pd.DataFrame(rows).to_csv(os.path.join(OUT, f'grid_{TF}.csv'), index=False)
best = pd.DataFrame(best); print(best.to_string()); best.to_csv(os.path.join(OUT, f'otimo_{TF}.csv'), index=False)
