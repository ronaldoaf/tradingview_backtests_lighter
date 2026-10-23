"""Lote 21: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE21_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote21 as L21, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'btc': [('strex', '1h', dict(mult=4.0, short_ok=True)), ('strex', '30min', dict(mult=8.0, short_ok=True)),
            ('strex', '4h', dict(mult=2.0, short_ok=True)), ('strex', '1h', dict(mult=4.0, short_ok=False)),
            ('cons', '30min', dict(nb=4, malen=1)), ('lsf', '1h', dict(ln=30, mult=2.0, short_ok=True))],
    'eth': [('cons', '4h', dict(nb=4, malen=1)), ('cons', '30min', dict(nb=4, malen=1)),
            ('lsf', '1h', dict(ln=12, mult=2.0, short_ok=True)), ('lsf', '15min', dict(ln=30, mult=1.0, short_ok=True)),
            ('surf', '4h', dict(per=55)), ('guppy', '30min', dict())],
    'wti': [('gs', '4h', dict()), ('gs', '15min', dict()), ('gs', '30min', dict()), ('gs', '1h', dict()), ('lsf', '30min', dict(ln=12, mult=2.0, short_ok=True))],
}
RUN = dict(strex=L21.run_strex, cons=L21.run_cons, lsf=L21.run_lsf, surf=L21.run_surf, guppy=L21.run_guppy,
           gs=L21.run_gs)


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
