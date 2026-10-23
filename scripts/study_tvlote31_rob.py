"""Lote 31: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE31_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote31 as L29, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('psw', '1h', dict(p=(0.01, 0.01, 0.1)))],
    'wti': [('lch', '15min', dict(hl=200)), ('lch', '15min', dict()), ('psw', '4h', dict()), ('mst', '4h', dict(ls=14))],
    'btc': [('pse', '30min', dict(off=0.0)), ('cmb', '1h', dict()), ('gx', '4h', dict(p=(20, 100)))],
    'eth': [('cmb', '15min', dict(ln=28)), ('gx', '15min', dict(p=(20, 100))), ('cmb', '30min', dict(ln=28)),
            ('cmb', '4h', dict()), ('sha', '30min', dict(ln=20)), ('pse', '1h', dict(off=0.0))],
}
RUN = {k: getattr(L29, 'run_' + k) for k in ('psw', 'lch', 'mst', 'pse', 'cmb', 'gx', 'sha')}

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
