"""Lote 33: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE33_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote33 as L33, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'wti': [('tbn', '4h', dict()), ('mcd', '1h', dict(p=(12, 26, 9))), ('dst', '1h', dict())],
    'btc': [('stc', '4h', dict()), ('vxe', '1D', dict(ef=20)), ('vxe', '1D', dict(ef=20, short_ok=False))],
    'eth': [('ich', '4h', dict()), ('vxe', '30min', dict()), ('vxe', '30min', dict(short_ok=False)),
            ('vxe', '4h', dict(ef=20, short_ok=False)), ('vct', '4h', dict(thr=20, lv=50)), ('snr', '30min', dict(ln=42))],
}
RUN = {k: getattr(L33, 'run_' + k) for k in ('tbn', 'mcd', 'dst', 'stc', 'vxe', 'ich', 'vct', 'snr')}

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
