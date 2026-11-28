"""Grade de sinais x dimensionamento x stop, normalizada por risco: para cada combinacao,
escolhe a alavancagem L que da MDD de 30% no IS (2011-10..2018) e reporta o OOS (2019..2026)
com essa mesma L. Execucao 'pm' (16:20 ET no M1 quando existe, senao fechamento) e 'open'."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
f = fund_model(D.ts.values)
IS = D.index <= '2018-12-31'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
TARGET = 0.30

SIG = {'sempre': pd.Series(1.0, index=D.index)}
for th in (0.9, 0.925, 0.95, 0.975, 1.0):
    SIG[f'ts<{th}'] = sg.ts(D, th)
for a in (0.9, 0.95):
    SIG[f'tsH{a}/1.0'] = sg.ts_hyst(D, a, 1.0)
SIG['ts<1&ts9<1'] = sg.ts(D, 1.0) * sg.ts9(D, 1.0)
SIG['ts<0.95&ts9<1'] = sg.ts(D, 0.95) * sg.ts9(D, 1.0)
SIG['ts<1&vrp10>0'] = sg.ts(D, 1.0) * sg.vrp(D, 10, 0)
SIG['ts<1&vrp5>0'] = sg.ts(D, 1.0) * sg.vrp(D, 5, 0)
SIG['ts<1&vix<ma10'] = sg.ts(D, 1.0) * sg.vix_ma(D, 10)
SIG['ts<1&px<ma10'] = sg.ts(D, 1.0) * sg.px_ma(D, 'c', 10)
SIG['vrp5>0'] = sg.vrp(D, 5, 0)
SIG['vrp10>0'] = sg.vrp(D, 10, 0)
SIZE = {'fixo': pd.Series(1.0, index=D.index)}
for n in (10, 20, 60):
    SIZE[f'vt{n}'] = sg.volsize(D, 'c', n, target=1.0, wmax=10.0)  # escala relativa; L ajusta o nivel
SIZE['tslin0.8'] = sg.ts_size(D, 0.8, 1.0, 1.0)
STOP = [(0.0, 0), (0.15, 0), (0.25, 0), (0.15, 3)]
EXEC = ['pm', 'open']


def run(w, ex, stop, cool, sl):
    res, ns, lq = sim(D.iloc[sl], w[sl], exec=ex, fund=f[sl], band=0.25, stop=stop, cool=cool)
    return stats(res, ns, lq)


def fitL(base, ex, stop, cool, wcap=1.5):
    """Bisseccao em L para MDD_IS = TARGET (exposicao limitada a wcap)."""
    sl = np.where(IS)[0]; sl = slice(sl[0], sl[-1] + 1)
    lo, hi = 0.01, 3.0
    for _ in range(18):
        L = (lo + hi) / 2
        s = run(np.minimum(base * L, wcap), ex, stop, cool, sl)
        if s['mdd'] < -TARGET or s['liq']:
            hi = L
        else:
            lo = L
    return lo


rows = []
slIS = slice(0, int(IS.sum())); slOOS = slice(int(IS.sum()), len(D))
for (sn, s), (zn, z), (stp, cl), ex in itertools.product(SIG.items(), SIZE.items(), STOP, EXEC):
    base = (s.fillna(0) * z.fillna(0)).values
    L = fitL(base, ex, stp, cl)
    w = np.minimum(base * L, 1.5)
    a = run(w, ex, stp, cl, slIS); b = run(w, ex, stp, cl, slOOS)
    rows.append(dict(sinal=sn, tam=zn, stop=stp, cool=cl, exec=ex, L=L, w_med=np.mean(w[w > 0]) if (w > 0).any() else 0,
                     IS_cagr=a['cagr'], IS_mdd=a['mdd'], IS_sh=a['sharpe'],
                     OOS_cagr=b['cagr'], OOS_mdd=b['mdd'], OOS_sh=b['sharpe'], OOS_worst=b['worst'], OOS_expo=b['expo'],
                     OOS_turn=b['turn'], OOS_liq=b['liq']))
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, 's03_grade.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400)
for ex in EXEC:
    P = R[R.exec == ex].copy()
    for c in ('IS_cagr', 'IS_mdd', 'OOS_cagr', 'OOS_mdd', 'OOS_worst', 'OOS_expo'):
        P[c] = (P[c] * 100).round(1)
    print(f'\n===== exec {ex}: top 40 por CAGR no IS (MDD_IS fixado em {TARGET:.0%})')
    print(P.sort_values('IS_cagr', ascending=False).head(40).round(2).to_string(index=False))
    print(f'\n-- correlacao de rank IS x OOS (CAGR): %.2f' % P.IS_cagr.rank().corr(P.OOS_cagr.rank()))
