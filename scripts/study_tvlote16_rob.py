"""Lote 16: robustez das celulas acima do B&H (EDMA, AI Volume SuperTrend, EMA Cross e PMax).
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE16_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote16 as L16, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'eth': [('edma', '30min', dict(ln=20, e1=20)), ('aivst', '4h', dict(ln=20, fac=5.0)), ('emax', '15min', dict(f=50, s=200))],
    'btc': [('emax', '4h', dict(f=50, s=200)), ('pmax', '15min', dict(sl=0.01, filtros=False))],
    'wti': [('edma', '30min', dict(ln=50, e1=40)), ('edma', '1D', dict(ln=20, e1=40))],
    'xau': [('edma', '30min', dict(ln=50, e1=40))],
}
RUN = dict(edma=L16.run_edma, aivst=L16.run_aivst, emax=L16.run_emax, pmax=L16.run_pmax)


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
