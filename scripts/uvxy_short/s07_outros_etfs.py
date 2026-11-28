"""A mesma ideia em outros ETFs alavancados da AlphaX: vendido (w=0,3) com e sem o filtro VIX/VIX3M<1.
Inversos 3x (SQQQ, SOXS, TZA, SPXU): vender = ficar comprado no indice + colher o decaimento.
Diretos 3x (TQQQ, SOXL, TNA, UPRO): vender = ficar vendido no indice + colher o decaimento.
Par TQQQ+SQQQ (e SOXL+SOXS, TNA+TZA, UPRO+SPXU): metade em cada, quase neutro em direcao.
Funding: media medida na AlphaX recebida pelo vendido (constante) e cenario zero.
Execucao no fechamento (dados diarios do Yahoo), banda de 25%, 10 bp por perna."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, DD
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load(with_pm=False)
FUND = {'SQQQ': 16.1, 'TQQQ': 14.1, 'SOXS': 13.5, 'SOXL': 15.4, 'TZA': 16.3, 'TNA': 0, 'SPXU': 0, 'UPRO': 0}
W = 0.3
log = []
def p(s):
    print(s); log.append(s)


def mk(sym):
    x = pd.read_parquet(os.path.join(DD, f'daily_{sym.lower()}.parquet'))
    X = D0[['ts', 'vix', 'spx']].join(x[['open', 'high', 'low', 'close']].rename(columns={'open': 'o', 'high': 'h', 'low': 'l', 'close': 'c'}), how='inner')
    return X[X.c.notna() & X.ts.notna()]


def line(s):
    return 'CAGR %6.1f%%  MDD %6.1f%%  Sh %5.2f  pior dia %6.1f%%  exposto %3.0f%%' % (
        s['cagr'] * 100, s['mdd'] * 100, s['sharpe'], s['worst'] * 100, s['expo'] * 100)


p('# ETFs isolados (vendido w=0,3)')
rows = []
for sym in ('SQQQ', 'SOXS', 'TZA', 'SPXU', 'TQQQ', 'SOXL', 'TNA', 'UPRO'):
    X = mk(sym).loc['2011-10-04':]
    for fn, fr in (('funding AlphaX', FUND[sym] / 100 / 252), ('funding zero', 0.0)):
        if fn == 'funding AlphaX' and FUND[sym] == 0:
            continue
        for nm, s in (('fixo', pd.Series(1.0, index=X.index)), ('ts<1', sg.ts(X, 1.0))):
            res, ns, lq = sim(X, s.fillna(0).values * W, exec='close', fund=np.full(len(X), fr), band=0.25)
            st = stats(res, ns, lq)
            iOOS = X.index >= '2019-01-01'
            so = stats(*sim(X[iOOS], s.fillna(0).values[iOOS] * W, exec='close', fund=np.full(iOOS.sum(), fr), band=0.25))
            p(f'{sym:5s} {nm:5s} {fn:15s} 2011-26 {line(st)} | OOS CAGR {so["cagr"]*100:6.1f}% MDD {so["mdd"]*100:6.1f}%')
            rows.append(dict(etf=sym, regra=nm, funding=fn, **{k: st[k] for k in ('cagr', 'mdd', 'sharpe', 'worst', 'expo')},
                             oos_cagr=so['cagr'], oos_mdd=so['mdd']))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 's07_etfs.csv'), index=False)

p('\n# Referencia: comprado no indice com a mesma exposicao direcional (3 x 0,3 = 0,9x), rebalanceio diario, sem custos')
for sym in ('QQQ', 'SMH', 'IWM', 'SPY'):
    x = pd.read_parquet(os.path.join(DD, f'daily_{sym.lower()}.parquet')).close.loc['2011-10-04':]
    r = x.pct_change().fillna(0) * 0.9
    e = (1 + r).cumprod()
    st = stats(pd.DataFrame({'equity': e, 'turn': 0, 'exp': 1.0}, index=e.index))
    p(f'long {sym:4s} 0,9x  {line(st)}')

p('\n# Pares: metade do capital em cada perna, cada metade vendida a 0,3 (0,15 do patrimonio por perna)')
for a, b in (('TQQQ', 'SQQQ'), ('SOXL', 'SOXS'), ('TNA', 'TZA'), ('UPRO', 'SPXU')):
    A, B = mk(a).loc['2011-10-04':], mk(b).loc['2011-10-04':]
    idx = A.index.intersection(B.index); A, B = A.loc[idx], B.loc[idx]
    for nm, s in (('fixo', pd.Series(1.0, index=idx)), ('ts<1', sg.ts(A, 1.0))):
        for fn, fa, fb in (('funding AlphaX', FUND[a], FUND[b]), ('funding zero', 0, 0)):
            if fn == 'funding AlphaX' and (fa == 0 or fb == 0):
                continue
            ra, _, _ = sim(A, s.fillna(0).values * W, exec='close', fund=np.full(len(A), fa / 100 / 252), band=0.25)
            rb, _, _ = sim(B, s.fillna(0).values * W, exec='close', fund=np.full(len(B), fb / 100 / 252), band=0.25)
            r = (ra.equity.pct_change().fillna(0) + rb.equity.pct_change().fillna(0)) / 2
            e = (1 + r).cumprod()
            st = stats(pd.DataFrame({'equity': e, 'turn': 0, 'exp': s.fillna(0).values}, index=idx))
            p(f'{a}+{b:5s} {nm:5s} {fn:15s} {line(st)}')
open(os.path.join(OUT, 's07_outros_etfs.txt'), 'w').write('\n'.join(log) + '\n')
