"""Baseline: short fixo no UVXY sem protecao, varias politicas de rebalanceio e custos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fmt, fund_model, yearly

D0 = load()
R = D0.loc['2011-10-04':].copy()
S = D0.loc['2006-07-18':].copy()   # sintetico (VIX3M existe desde 2006-07-17)
fR = fund_model(R.ts.values); fS = fund_model(S.ts.values)
print('UVXY real', R.index[0].date(), R.index[-1].date(), '| sintetico', S.index[0].date(), S.index[-1].date())
# checagem do sintetico vs real pos-2018 (1,5x)
x = pd.concat([R.c.pct_change(), R.syn_r], axis=1).loc['2018-03-01':].dropna()
print('sintetico vs real 2018-03+: corr %.4f  CAGR real %.1f%%  CAGR sint %.1f%%' % (
    x.corr().iloc[0, 1], ((1 + x.iloc[:, 0]).prod() ** (252 / len(x)) - 1) * 100, ((1 + x.iloc[:, 1]).prod() ** (252 / len(x)) - 1) * 100))
for nm, DD, px, ff in (('REAL 2011-2026', R, 'c', fR), ('SINT 1,5x 2006-2026', S, 'syn', fS)):
    print('\n==', nm)
    for w in (0.5, 1.0):
        for band in (0.0, 0.25, 0.5, 1.0, 3.0):
            for ex in (['close', 'open'] if px == 'c' else ['close']):
                for fn, f in (('sem funding', None), ('funding modelo', ff)):
                    res, ns, lq = sim(DD, np.full(len(DD), w), px=px, exec=ex, fund=f, band=band)
                    print('w=%.1f banda %.2f exec %-5s %-14s ' % (w, band, ex, fn) + fmt(stats(res, ns, lq)))
