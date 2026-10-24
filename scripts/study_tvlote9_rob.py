"""Lote 9: robustez do RSI versus SMA invertido (tendencia), unica celula acima do B&H no ouro.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE9_TV.md."""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote9 as L9, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = [('rsma', '30min', dict(rl=8, ml=34, invert=True)), ('rsma', '30min', dict(rl=14, ml=34, invert=True)),
         ('rsma', '1h', dict(rl=8, ml=34, invert=True))]
RUN = dict(rsma=L9.run_rsisma)


def main(name='xau'):
    m1 = T.load_m1v(name); mm = M1(m1)
    for est, tf, kw in CELLS:
        full = T.resample(m1, tf)
        print(f"\n### {est} {tf} {kw}")
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
