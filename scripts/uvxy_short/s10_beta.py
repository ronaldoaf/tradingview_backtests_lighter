"""Quanto do resultado e beta de bolsa: regressao semanal dos retornos da regra (w=0,25) contra o S&P 500,
e a variante com hedge vendido no S&P (perp SPX500 da AlphaX, funding medido de +8,7%/ano ao vendido)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
f = fund_model(D.ts.values); on = sg.ts(D, 1.0).fillna(0).values
W = 0.25
m = D.spx.pct_change().fillna(0)
log = []
def p(s):
    print(s); log.append(s)


def ab(r, a='2011', b='2026'):
    x = r.loc[a:b]; y = m.loc[a:b]
    xw = (1 + x).resample('W').prod() - 1; yw = (1 + y).resample('W').prod() - 1
    be, al = np.polyfit(yw, xw, 1); e = xw - (al + be * yw)
    return be, al * 52, al / (e.std() / np.sqrt(len(xw))), np.corrcoef(xw, yw)[0, 1]


p('# Regressao semanal contra o S&P 500 (w=0,25)')
for nm, sig in (('VIX/VIX3M<1', on), ('short fixo', np.ones(len(D)))):
    res, _, _ = sim(D, sig * W, exec='pm', fund=f, band=0.25); r = res.equity.pct_change().fillna(0)
    for per, (a, b) in (('2011-2026', ('2011', '2026')), ('IS 2011-2018', ('2011', '2018')), ('OOS 2019-2026', ('2019', '2026'))):
        be, al, t, c = ab(r, a, b)
        p(f'{nm:12s} {per:14s} beta {be:5.2f}  alfa {al*100:5.1f}%/ano  t(alfa) {t:5.2f}  corr {c:4.2f}')
p('S&P 500 (preco) Sharpe 2011-2026: %.2f' % (m.mean() / m.std() * np.sqrt(252)))

p('\n# Hedge: vendido no S&P = h x 4,4 x exposicao no UVXY (beta diario do UVXY ao S&P = -4,4), 2 bp por perna')
res, _, _ = sim(D, on * W, exec='pm', fund=f, band=0.25); ru = res.equity.pct_change().fillna(0)
for h in (0.0, 0.5, 1.0):
    for fs in (0.0, 0.087):
        wh = pd.Series(np.r_[0, (on * W)[:-1]] * 4.4 * h, index=D.index)
        r = ru - wh * m + wh * fs / 252 - wh.diff().abs().fillna(0) * 2e-4
        e = (1 + r).cumprod()
        s = stats(pd.DataFrame({'equity': e, 'turn': 0, 'exp': on}, index=D.index))
        be, al, t, c = ab(r)
        o = r.loc['2019':]; eo = (1 + o).cumprod()
        p(f'h={h:.1f} funding S&P {fs*100:3.1f}%/a  CAGR {s["cagr"]*100:5.1f}%  MDD {s["mdd"]*100:6.1f}%  Sh {s["sharpe"]:4.2f} | '
          f'beta {be:4.2f} alfa {al*100:5.1f}% t {t:4.2f} | OOS Sh {o.mean()/o.std()*np.sqrt(252):4.2f} MDD {(eo/eo.cummax()-1).min()*100:6.1f}%')
open(os.path.join(OUT, 's10_beta.txt'), 'w').write('\n'.join(log) + '\n')
