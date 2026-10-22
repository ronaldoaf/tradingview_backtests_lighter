"""Lote 13: robustez das celulas acima do B&H (UT Bot, Ichimoku e Scalping em ETH/BTC/WTI).
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE13_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote13 as L13, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'eth': [('ut', '30min', dict(a=5.0, atr_n=11, shorts=True)), ('ut', '4h', dict(a=5.0, atr_n=11, shorts=True)),
            ('ichi', '30min', dict()), ('ichi', '15min', dict(ts=20, ks=60, sb=120, off=60)),
            ('scalp', '30min', dict(sma_len=25, ema_len=0))],
    'btc': [('scalp', '1D', dict(sma_len=25, ema_len=0)), ('scalp', '1h', dict(sma_len=50, ema_len=0)),
            ('ut', '30min', dict(a=2.0, atr_n=30, shorts=True))],
    'wti': [('ut', '15min', dict(a=5.0, atr_n=11, shorts=True)), ('ichi', '15min', dict(ts=20, ks=60, sb=120, off=60)),
            ('scalp', '30min', dict(sma_len=50, ema_len=0))],
}
RUN = dict(ut=L13.run_ut, ichi=L13.run_ichi, scalp=L13.run_scalp)


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
