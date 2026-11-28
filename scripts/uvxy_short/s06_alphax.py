"""Checagem no perp UVXY da AlphaX (jun-nov/2026): a regra roda nos candles de 1h do perp,
com o funding real de cada liquidacao (00/08/16 UTC), e e comparada com o modelo diario
(UVXY do Yahoo/Alpaca + funding modelado) na mesma janela."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model, COST
import signals as sg

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
A = os.path.join(ROOT, 'data', 'uvxy', 'alphax')
k = pd.read_csv(os.path.join(A, 'UVXY_1h.csv'), parse_dates=['t']).set_index('t')
old = os.path.join(A, 'UVXY_1h_ate_2026-11-16.csv')
if os.path.exists(old):
    k = pd.concat([pd.read_csv(old, parse_dates=['t']).set_index('t'), k])
    k = k[~k.index.duplicated(keep='last')].sort_index()
fu = pd.read_csv(os.path.join(A, 'UVXY_funding.csv'), parse_dates=['t']).set_index('t').rate
D = load()
W = 0.3
for name, th in (('VIX/VIX3M<1', 1.0), ('short fixo', 99)):
    sig = sg.ts(D, th).fillna(0)
    # decisao no fechamento do dia (16:15 ET); execucao no fechamento do candle 1h que comeca as 16:00 ET
    et = k.index.tz_localize('UTC').tz_convert('America/New_York')
    dec = pd.Series(np.nan, index=k.index)
    day = et.normalize().tz_localize(None)
    is_exec = (et.hour == 16) & np.isin(day, sig.index)
    dec[is_exec] = sig.reindex(day[is_exec]).values * W
    tgt = dec.ffill().fillna(0).values
    c = k.c.values; eq = 1.0; q = 0.0; E = []; cost = 0.0; fsum = 0.0
    fmap = fu.reindex(k.index).fillna(0).values
    for i in range(len(c)):
        if i > 0:
            eq -= q * (c[i] - c[i - 1])
        # funding na liquidacao (candle cujo inicio coincide com o horario de liquidacao)
        if fmap[i] != 0 and q > 0:
            g = q * c[i] * fmap[i]; eq += g; fsum += g
        if is_exec[i]:
            nq = tgt[i] * eq / c[i]
            cur = q * c[i] / eq
            if tgt[i] == 0 or q == 0 or cur > tgt[i] * 1.25 or cur < tgt[i] / 1.25:
                cc = COST * abs(nq - q) * c[i]; eq -= cc; cost += cc; q = nq
        E.append(eq)
    E = pd.Series(E, index=k.index)
    d0, d1 = E.index[0].normalize(), E.index[-1].normalize()
    # modelo diario na mesma janela
    X = D.loc[d0:d1]; X = X[X.c.notna()]
    res, ns, lq = sim(X, sg.ts(X, th).fillna(0).values * W, exec='pm', fund=fund_model(X.ts.values), band=0.25)
    dd = (E / E.cummax() - 1).min()
    print(f'{name:12s} perp AlphaX {E.index[0]:%Y-%m-%d}..{E.index[-1]:%Y-%m-%d}: retorno {(E.iloc[-1]-1)*100:6.1f}%  MDD {dd*100:6.1f}%  '
          f'funding {fsum*100:+.2f}%  custos {-cost*100:.2f}% | modelo diario: retorno {(res.equity.iloc[-1]/res.equity.iloc[0]-1)*100:6.1f}%  MDD {stats(res)["mdd"]*100:6.1f}%')
    m = E.resample('ME').last(); print('   por mes (perp):', ' '.join(f'{i:%b} {v*100:+.1f}%' for i, v in pd.concat([pd.Series([1.0], index=[E.index[0]]), m]).pct_change().dropna().items()))
