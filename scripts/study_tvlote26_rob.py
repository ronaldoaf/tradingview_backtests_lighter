"""Lote 26: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE26_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote26 as L26, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('pprs', '1h', dict(lb=6, rb=3)), ('dma', '1h', dict())],
    'wti': [('csq', '1D', dict(mfl=14)), ('vst', '15min', dict()), ('e5', '4h', dict())],
    'btc': [('dm', '4h', dict(ln=50, short_ok=False)), ('him', '1D', dict(keh=30)), ('qc', '4h', dict())],
    'eth': [('csq', '4h', dict(mfl=14)), ('e5', '4h', dict(rr=3.0)), ('sts', '4h', dict(short_ok=True)), ('qc', '15min', dict()),
            ('vst', '4h', dict(short_ok=False)), ('kama', '1h', dict(ef=0.5, atrs=True)), ('dm', '1D', dict(ln=50))],
}
RUN = {k: getattr(L26, 'run_' + k) for k in ('pprs', 'dma', 'csq', 'vst', 'e5', 'dm', 'him', 'qc', 'sts', 'kama')}

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
