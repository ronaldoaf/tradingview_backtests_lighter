"""Lote 32: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE32_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote32 as L32, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'wti': [('srs', '1D', dict(fac=3.0, short_ok=True)), ('tfp', '1h', dict(rr=2.0)), ('tfp', '4h', dict(rr=2.0)),
            ('usc', '4h', dict()), ('hme', '30min', dict())],
    'btc': [('tss', '15min', dict()), ('dcs', '4h', dict()), ('stt', '15min', dict(cd=0.006))],
    'eth': [('prv', '4h', dict(short_ok=False)), ('prv', '4h', dict()), ('tss', '30min', dict(per=32)),
            ('tss', '15min', dict()), ('dcs', '30min', dict(short_ok=False))],
}
RUN = {k: getattr(L32, 'run_' + k) for k in ('srs', 'tfp', 'usc', 'hme', 'tss', 'dcs', 'stt', 'prv')}

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
