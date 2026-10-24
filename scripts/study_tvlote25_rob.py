"""Lote 25: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE25_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote25 as L25, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('sr', '1h', dict())],
    'wti': [('sta', '4h', dict(ln=14)), ('tlb', '4h', dict(maf=False)), ('flexi', '15min', dict())],
    'btc': [('pop', '4h', dict(lb=10, rb=5)), ('grov', '30min', dict(ln=100, mult=5.0)), ('bas', '30min', dict()), ('era', '4h', dict(sl=0.05))],
    'eth': [('thma', '15min', dict(ln=100)), ('ce', '30min', dict()), ('thma', '30min', dict()), ('smp', '15min', dict(sl=0.0, tp=0.0)),
            ('bts', '30min', dict()), ('bas', '15min', dict()), ('ht3', '1h', dict(ln=100)), ('imct', '30min', dict())],
}
RUN = {k: getattr(L25, 'run_' + k) for k in ('sr', 'sta', 'tlb', 'flexi', 'pop', 'grov', 'bas', 'era', 'thma', 'ce', 'smp', 'bts', 'ht3', 'imct')}

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
