"""Lote 14: robustez das celulas acima do B&H (Delta-RSI em BTC/ETH/WTI, HullMA e Crypto Scalper no ETH, HA-PSAR no XAU).
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE14_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote14 as L14, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'btc': [('drsi', '30min', dict(rl=21, window=100, mode='zero')), ('drsi', '1h', dict(rl=21, window=50, mode='zero')),
            ('drsi', '4h', dict(rl=21, window=100, mode='zero'))],
    'eth': [('drsi', '1h', dict(rl=21, window=50, mode='signal')), ('drsi', '30min', dict(rl=21, window=100, mode='zero')),
            ('hull', '30min', dict(n=100)), ('cs', '15min', dict())],
    'wti': [('drsi', '4h', dict(rl=14, window=30, mode='signal'))],
    'xau': [('hap', '1h', dict(start=0.01, inc=0.01, mx=0.1))],
}
RUN = dict(drsi=L14.run_drsi, hull=L14.run_hull, cs=L14.run_cs, hap=L14.run_hap)


def main(name='xau'):
    m1 = T.load_m1v(name); mm = M1(m1)
    for est, tf, kw in CELLS[name]:
        full = T.resample(m1, tf)
        print(f"\n### {est} {tf} " + str(kw))
        cuts = np.array_split(np.arange(len(full)), 3)
        parts = [('tudo', full)] + [(f'terco{k+1}', full.iloc[c[0]:c[-1] + 1]) for k, c in enumerate(cuts)] + \
            [('2a metade', full.iloc[len(full) // 2:])]
        for tag, df in parts:
            RUN[est](name, df, mm, f'{tag} {df.index[0].date()}..{df.index[-1].date()}', **kw)
        base = E.CUSTO[name]
        for mlt in (2, 4):
            E.CUSTO[name] = base * mlt; T.CUSTO[name] = base * mlt
            RUN[est](name, full, mm, f'custo {mlt}x', **kw)
        E.CUSTO[name] = base; T.CUSTO[name] = base


if __name__ == '__main__':
    main(*(sys.argv[1:] or ['xau']))
