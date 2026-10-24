"""Lote 27: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE27_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote27 as L27, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('tch', '15min', dict()), ('spk', '1h', dict())],
    'wti': [('tch', '15min', dict()), ('obv', '1h', dict()), ('spk', '1D', dict(sm=30)), ('gsc', '4h', dict(tpk='atr2'))],
    'btc': [('spk', '1h', dict()), ('wyk', '1h', dict()), ('ssl', '1D', dict(ln=50))],
    'eth': [('wyk', '4h', dict(sl=0.03)), ('wyk', '4h', dict()), ('spk', '30min', dict(sm=30)), ('ssl', '30min', dict(ln=50)),
            ('spk', '30min', dict(sm=30, short_ok=False))],
}
RUN = {k: getattr(L27, 'run_' + k) for k in ('tch', 'spk', 'obv', 'gsc', 'wyk', 'ssl')}

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
