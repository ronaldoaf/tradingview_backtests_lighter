"""Lote 23: robustez das celulas acima do B&H.
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE23_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote23 as L23, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'xau': [('ma1020', '1h', dict()), ('ma1020', '30min', dict(f=20, s=50))],
    'wti': [('crazy', '1h', dict(sll=30)), ('twin', '1h', dict(sltp=False))],
    'btc': [('tema', '4h', dict(short_ok=True)), ('stv', '15min', dict(short_ok=True)), ('zzrsi', '15min', dict(rl=14, os_=30, ob=70)),
            ('evw', '4h', dict(ln=100))],
    'eth': [('rsipa', '4h', dict(tpm=0, short_ok=False)), ('tema', '15min', dict(short_ok=True)), ('twin', '4h', dict(sltp=False)),
            ('stv', '15min', dict(short_ok=True)), ('stv', '15min', dict())],
}
RUN = {k: getattr(L23, 'run_' + k) for k in ('ma1020', 'crazy', 'twin', 'tema', 'stv', 'zzrsi', 'evw', 'rsipa')}

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
