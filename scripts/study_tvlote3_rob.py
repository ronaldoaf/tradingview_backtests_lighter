"""Robustez das 8 celulas do lote 3 que bateram o buy&hold do ouro (de 467 testadas):
tercos do historico + conferencia do custo. Se a vantagem so existe num terco, e ruido de garimpo.
uso: python study_tvlote3_rob.py
"""
import os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_tvlote3 as S

CELLS = [
    ('occ', '1h', 'HULL13 x5', lambda df: S.occ_signals(df, kind='HULL', ln=13, mult=5, peek=False)),
    ('tott', '15min', 'VAR20 p1 c0', lambda df: S.tott_signals(df, ln=20, percent=1.0, coeff=0.0)),
    ('tott', '15min', 'VAR20 p1 c.005', lambda df: S.tott_signals(df, ln=20, percent=1.0, coeff=0.005)),
    ('tott', '15min', 'VAR40 p1 c.005', lambda df: S.tott_signals(df, ln=40, percent=1.0, coeff=0.005)),
    ('tott', '30min', 'VAR20 p.5 c0', lambda df: S.tott_signals(df, ln=20, percent=0.5, coeff=0.0)),
    ('tott', '30min', 'VAR20 p1 c.005', lambda df: S.tott_signals(df, ln=20, percent=1.0, coeff=0.005)),
    ('tott', '1h', 'VAR20 p1 c0', lambda df: S.tott_signals(df, ln=20, percent=1.0, coeff=0.0)),
    ('macdre', '1h', 'TILL 12/26/9', lambda df: S.macdre_signals(df, kind='TILL')),
]


def main(name='xau'):
    m1 = T.load_m1v(name)
    cache = {tf: T.resample(m1, tf) for tf in {c[1] for c in CELLS}}
    print(f"{name}: {m1.index[0].date()} -> {m1.index[-1].date()}")
    for est, tf, cfg, fn in CELLS:
        df = cache[tf]
        L, Sg = fn(df)
        print(f"\n{est} {tf} {cfg}")
        n = len(df)
        for k, (a, b, lab) in enumerate([(0, n, 'tudo'), (0, n // 3, 'terco 1'),
                                         (n // 3, 2 * n // 3, 'terco 2'), (2 * n // 3, n, 'terco 3')]):
            d = df.iloc[a:b]
            o, tr = S.run(name, d, L[a:b], Sg[a:b], '', verbose=False)
            if not o:
                print(f"  {lab:8s} (poucos trades)"); continue
            print(f"  {lab:8s} {d.index[0].date()}->{d.index[-1].date()} " + T.FMT.format(**o))
        # custo 2x: o edge sobrevive a um spread do dobro?
        cst = T.CUSTO[name]
        T.CUSTO[name] = cst * 2
        o, _ = S.run(name, df, L, Sg, '', verbose=False)
        T.CUSTO[name] = cst
        if o: print(f"  {'custo 2x':8s} " + T.FMT.format(**o))


if __name__ == '__main__':
    main(*(sys.argv[1:] or []))
