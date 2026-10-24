"""Lote 12: robustez das celulas acima do B&H (Simple RSI-MA em ETH/BTC/XAU, TK Cross em ETH/WTI, Acrypto e Zigma no WTI).
Tercos, metades (OOS = segunda metade com o parametro fixo) e custo 2x/4x. Ver docs/LOTE12_TV.md.
uso: python study_tvlote12_rob.py ativo"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote12 as L12, study_tvlote12b as L12b, study_engulf_psar as E
from study_tvlote6 import M1

CELLS = {
    'eth': [('rsima', '15min', dict(rl=10, ml=50)), ('rsima', '15min', dict(rl=5, ml=50)), ('rsima', '30min', dict(rl=10, ml=20)),
            ('rsima', '1h', dict(rl=10, ml=50)), ('tk', '30min', dict(conv=20, base=60, ema_len=200, shorts=True))],
    'btc': [('rsima', '15min', dict(rl=10, ml=50)), ('rsima', '30min', dict(rl=10, ml=20)), ('rsima', '1h', dict(rl=10, ml=50)),
            ('tk', '4h', dict(conv=9, base=26, ema_len=200, shorts=True))],
    'xau': [('rsima', '15min', dict(rl=20, ml=50)), ('rsima', '30min', dict(rl=20, ml=20)), ('rsima', '15min', dict(rl=10, ml=50))],
    'wti': [('tk', '15min', dict(conv=40, base=120, ema_len=200, shorts=True)), ('rsima', '30min', dict(rl=20, ml=20)),
            ('acr', '4h', dict(trig=1, sl=0.02)), ('zig', '1h', dict(lb=24, use_dmi=True))],
    'us100': [('rsima', '15min', dict(rl=10, ml=50))],
}
RUN = dict(rsima=L12.run_rsima, tk=L12.run_tk, acr=L12.run_acr, zig=L12b.run_zig)


def main(name='xau'):
    m1 = T.load_m1v(name); mm = M1(m1)
    for est, tf, kw in CELLS[name]:
        full = T.resample(m1, tf)
        if est == 'zig':
            kw = dict(kw, h1=T.resample(m1, '1h'), m15=T.resample(m1, '15min'))
        print(f"\n### {est} {tf} " + str({k: v for k, v in kw.items() if k not in ('h1', 'm15')}))
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
