"""Lote 18: robustez das celulas acima do B&H (TDI e EMA Slope).
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE18_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote18 as L18, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('tdi', '1h', dict(strength=1)), ('tdi', '30min', dict(strength=1)), ('tdi', '4h', dict(strength=1))],
    'btc': [('slope', '4h', dict(ln=50, trend=True)), ('slope', '1h', dict(ln=50, trend=True))],
    'eth': [('slope', '30min', dict(ln=130, trend=True)), ('tdi', '4h', dict(strength=1))],
    'wti': [('tdi', '1h', dict(strength=2))],
}
RUN = dict(tdi=L18.run_tdi, slope=L18.run_slope)


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
