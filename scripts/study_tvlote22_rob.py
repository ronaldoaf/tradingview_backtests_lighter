"""Lote 22: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE22_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote22 as L22, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('psarc', '4h', dict(nb=1, start=0.01, mx=0.1)), ('psarc', '1h', dict(nb=1, start=0.01, mx=0.1)),
            ('pmax', '30min', dict(mult=1.5, tl=20)), ('tsi', '15min', dict(tp=0.02))],
    'wti': [('tdon', '30min', dict(ent=55, ext=20, mult=2.0, short=True)), ('tdon', '1h', dict(ent=20, ext=10, mult=4.0, short=True)),
            ('mab', '4h', dict(ln=40, rr=3.0)), ('force', '1D', dict(fast=3, slow=20))],
    'btc': [('force', '4h', dict(fast=5, slow=50, short_ok=False)), ('force', '4h', dict(fast=5, slow=50)),
            ('slopes', '1D', dict(tf_=False, short_ok=False)), ('apsar', '4h', dict(short_ok=False)),
            ('slopes', '4h', dict(l1=50, l2=200))],
    'eth': [('slopes', '4h', dict(short_ok=False)), ('slopes', '4h', dict()), ('force', '1h', dict(fast=5, slow=50, short_ok=False)),
            ('btf', '30min', dict(lb=10)), ('emax', '1h', dict(ln=50, ratio=5, short_ok=False))],
}
RUN = dict(psarc=L22.run_psarc, pmax=L22.run_pmax, tsi=L22.run_tsi, tdon=L22.run_tdon, mab=L22.run_mab,
           force=L22.run_force, slopes=L22.run_slopes, apsar=L22.run_psar, btf=L22.run_btf, emax=L22.run_emax)

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
