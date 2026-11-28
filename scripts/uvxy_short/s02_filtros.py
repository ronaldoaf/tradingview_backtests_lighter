"""Filtros de regime isolados e combinados, com w=0,5 fixo. IS = 2011-10..2018, OOS = 2019..2026.
Sintetico 1,5x: 2006-07..2011-09 (pre-UVXY, inclui 2008) e 2006-2026 inteiro."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

D0 = load()
PER = {'IS': ('2011-10-04', '2018-12-31'), 'OOS': ('2019-01-01', '2026-12-31'),
       'SYNpre': ('2006-07-18', '2011-10-03'), 'SYNall': ('2006-07-18', '2026-12-31')}


def fam(D, px):
    F = {'sempre': pd.Series(1.0, index=D.index)}
    for th in (0.85, 0.9, 0.95, 1.0, 1.05):
        F[f'ts<{th}'] = sg.ts(D, th)
    for a, b in ((0.9, 1.0), (0.95, 1.0), (0.9, 0.95), (0.95, 1.05)):
        F[f'tsH{a}/{b}'] = sg.ts_hyst(D, a, b)
    for n in (3, 5, 10, 20):
        F[f'vix<ma{n}'] = sg.vix_ma(D, n)
    for n in (5, 10, 20, 50):
        F[f'px<ma{n}'] = sg.px_ma(D, px, n)
    for n in (5, 10, 20):
        for m in (0, 3):
            F[f'vrp{n}>{m}'] = sg.vrp(D, n, m)
    for L in (20, 25, 30):
        F[f'vix<{L}'] = sg.vix_lvl(D, L)
    F['ts<1&vix<ma10'] = sg.ts(D, 1.0) * sg.vix_ma(D, 10)
    F['ts<0.95&vix<ma10'] = sg.ts(D, 0.95) * sg.vix_ma(D, 10)
    F['ts<1&px<ma10'] = sg.ts(D, 1.0) * sg.px_ma(D, px, 10)
    F['ts<1&vrp10>0'] = sg.ts(D, 1.0) * sg.vrp(D, 10, 0)
    F['ts<0.95&vrp10>0'] = sg.ts(D, 0.95) * sg.vrp(D, 10, 0)
    F['vrp10>0&vix<ma10'] = sg.vrp(D, 10, 0) * sg.vix_ma(D, 10)
    return F


rows = []
W = 0.5
for per, (a, b) in PER.items():
    px = 'syn' if per.startswith('SYN') else 'c'
    D = D0.loc[a:b]
    D = D[D[px].notna() & D.ts.notna()]
    f = fund_model(D.ts.values)
    for name, s in fam(D, px).items():
        w = (s.fillna(0) * W).values
        for ex in (('close', 'open', 'pm') if px == 'c' else ('close', 'close+1')):
            ww = w if ex != 'close+1' else np.r_[0, w[:-1]]
            e = 'close' if ex == 'close+1' else ex
            if e == 'pm' and per == 'IS':
                DD = D.loc['2016-01-01':]
            else:
                DD = D
            ww = ww[-len(DD):]
            res, ns, lq = sim(DD, ww, px=px, exec=e, fund=f[-len(DD):], band=0.25)
            st = stats(res, ns, lq)
            rows.append(dict(per=per, sinal=name, exec=ex, **st))
R = pd.DataFrame(rows)
os.makedirs(os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'uvxy_short'), exist_ok=True)
R.to_csv(os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'uvxy_short', 's02_filtros.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
for ex in ('close', 'open', 'pm'):
    P = R[R.exec.isin([ex, 'close+1' if ex == 'open' else ex])]
    t = P.pivot_table(index='sinal', columns='per', values=['cagr', 'mdd', 'sharpe', 'expo'], aggfunc='first')
    t = t[[c for c in t.columns if c[1] in ('IS', 'OOS', 'SYNpre', 'SYNall')]]
    print(f'\n===== exec {ex} (SYN usa close' + ('+1' if ex == 'open' else '') + ')')
    out = pd.DataFrame({
        'IS cagr': t[('cagr', 'IS')] * 100, 'IS mdd': t[('mdd', 'IS')] * 100, 'IS sh': t[('sharpe', 'IS')],
        'OOS cagr': t[('cagr', 'OOS')] * 100, 'OOS mdd': t[('mdd', 'OOS')] * 100, 'OOS sh': t[('sharpe', 'OOS')],
        'SYNpre cagr': t[('cagr', 'SYNpre')] * 100, 'SYNpre mdd': t[('mdd', 'SYNpre')] * 100,
        'SYNall cagr': t[('cagr', 'SYNall')] * 100, 'SYNall mdd': t[('mdd', 'SYNall')] * 100, 'SYNall sh': t[('sharpe', 'SYNall')],
        'expo OOS': t[('expo', 'OOS')] * 100})
    print(out.round(2).sort_values('IS sh', ascending=False).to_string())
