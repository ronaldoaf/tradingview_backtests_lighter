"""Camadas extras sobre a regra VIX/VIX3M<1: cada variante e escalada para a mesma volatilidade
anual da regra base (w=0,3) no periodo 2011-2026, e comparada no IS, OOS e no sintetico 2006-2026."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
f = fund_model(D.ts.values); fS = fund_model(S.ts.values)
iIS = int((D.index <= '2018-12-31').sum())


def var(X, px):
    t = sg.ts(X, 1.0)
    V = {'base ts<1': (t, 0.0)}
    for n in (5, 10, 20):
        V[f'+ vrp{n}>0'] = (t * sg.vrp(X, n, 0), 0.0)
    V['+ vix<ma10'] = (t * sg.vix_ma(X, 10), 0.0)
    V['+ vix<ma20'] = (t * sg.vix_ma(X, 20), 0.0)
    V['+ px<ma10'] = (t * sg.px_ma(X, px, 10), 0.0)
    V['+ vix<25'] = (t * sg.vix_lvl(X, 25), 0.0)
    V['+ ts9<1'] = (t * sg.ts9(X, 1.0), 0.0) if px == 'c' else None
    V['+ stop 15%'] = (t, 0.15)
    V['+ stop 25%'] = (t, 0.25)
    V['+ alvo de vol 20d'] = (t * sg.volsize(X, px, 20, 1.0, 10.0), 0.0)
    V['+ alvo de vol 60d'] = (t * sg.volsize(X, px, 60, 1.0, 10.0), 0.0)
    V['+ tamanho linear na curva'] = (sg.ts_size(X, 0.8, 1.0, 1.0), 0.0)
    V['short fixo (sem filtro)'] = (pd.Series(1.0, index=X.index), 0.0)
    return {k: v for k, v in V.items() if v is not None}


def run(X, w, px, ff, stop, ex):
    return stats(*sim(X, w, px=px, exec=ex, fund=ff, band=0.25, stop=stop))


ref = run(D, sg.ts(D, 1.0).fillna(0).values * 0.3, 'c', f, 0.0, 'pm')['vol']
refS = run(S, sg.ts(S, 1.0).fillna(0).values * 0.3, 'syn', fS, 0.0, 'close')['vol']
rows = []
VS = var(S, 'syn')
for k, (s, stop) in var(D, 'c').items():
    base = s.fillna(0).values
    # escala para a vol de referencia (bisseccao)
    lo, hi = 0.01, 5.0
    for _ in range(25):
        L = (lo + hi) / 2
        v = run(D, np.minimum(base * L, 1.5), 'c', f, stop, 'pm')['vol']
        lo, hi = (L, hi) if v < ref else (lo, L)
    w = np.minimum(base * L, 1.5)
    a = run(D, w, 'c', f, stop, 'pm')
    i = run(D.iloc[:iIS], w[:iIS], 'c', f[:iIS], stop, 'pm')
    o = run(D.iloc[iIS:], w[iIS:], 'c', f[iIS:], stop, 'pm')
    row = dict(variante=k, w_medio=np.mean(w[w > 0]), sh=a['sharpe'], cagr=a['cagr'] * 100, mdd=a['mdd'] * 100,
               IS_sh=i['sharpe'], OOS_sh=o['sharpe'], OOS_cagr=o['cagr'] * 100, OOS_mdd=o['mdd'] * 100)
    if k in VS and stop == 0:
        sS = VS[k][0].fillna(0).values
        lo, hi = 0.01, 5.0
        for _ in range(25):
            L = (lo + hi) / 2
            v = run(S, np.minimum(sS * L, 1.5), 'syn', fS, 0.0, 'close')['vol']
            lo, hi = (L, hi) if v < refS else (lo, L)
        s2 = run(S, np.minimum(sS * L, 1.5), 'syn', fS, 0.0, 'close')
        row.update(SIN_sh=s2['sharpe'], SIN_cagr=s2['cagr'] * 100, SIN_mdd=s2['mdd'] * 100)
    rows.append(row)
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, 's05_camadas.csv'), index=False)
pd.set_option('display.width', 220)
print('vol de referencia (ts<1, w=0,3): real %.1f%%  sintetico %.1f%%' % (ref * 100, refS * 100))
print(R.round(2).to_string(index=False))
