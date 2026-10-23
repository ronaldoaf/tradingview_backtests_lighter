"""Lote 28: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE28_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote28 as L28, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('hvc', '30min', dict()), ('hvc', '15min', dict(ln=100))],
    'wti': [('hapa', '4h', dict(ha=False, short_ok=True)), ('l2r', '30min', dict(tpsl=False))],
    'btc': [('hamacd', '1h', dict(sltp=False)), ('hamacd', '1h', dict()), ('mab', '1D', dict(ln=50)), ('sma3', '4h', dict(sl=99))],
    'eth': [('gvto', '4h', dict(short_ok=False)), ('hamacd', '1h', dict(sltp=False)), ('pmax', '4h', dict()), ('bbw', '15min', dict(ln=50))],
}
RUN = {k: getattr(L28, 'run_' + k) for k in ('hvc', 'hapa', 'l2r', 'hamacd', 'mab', 'sma3', 'gvto', 'pmax', 'bbw')}

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
