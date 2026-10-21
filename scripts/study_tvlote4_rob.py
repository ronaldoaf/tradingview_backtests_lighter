"""Robustez das celulas do Pivot Point SuperTrend que empataram com o buy&hold do ouro ou tiveram
t > 2,5 contra o controle: tercos, metade OOS (vizinhanca escolhida na 1a metade) e custo 2x/4x.
uso: python study_tvlote4_rob.py [xau|eth|btc]
"""
import os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_tvlote4 as S

CELLS = {'xau': [('1h', 5, 4.0, 20), ('30min', 5, 2.0, 20), ('30min', 3, 2.0, 20), ('15min', 5, 4.0, 20),
                 ('30min', 2, 3.0, 10)],
         'eth': [('1h', 2, 4.0, 20), ('15min', 3, 3.0, 20), ('15min', 5, 2.0, 10), ('1h', 3, 3.0, 20),
                 ('4h', 5, 4.0, 20), ('1h', 5, 4.0, 20)],
         'btc': [('1h', 5, 4.0, 20)]}


def main(name='xau'):
    m1 = T.load_m1v(name)
    cache = {tf: T.resample(m1, tf) for tf in {c[0] for c in CELLS[name]}}
    for tf, prd, F, Pd in CELLS[name]:
        df = cache[tf]
        L, Sg = S.ppst_signals(df, prd, F, Pd)
        print(f"\n{name} PPST {tf} p{prd} f{F} a{Pd}")
        n = len(df)
        for a, b, lab in [(0, n, 'tudo'), (0, n // 3, 'terco 1'), (n // 3, 2 * n // 3, 'terco 2'),
                          (2 * n // 3, n, 'terco 3'), (0, n // 2, 'metade 1'), (n // 2, n, 'metade 2')]:
            d = df.iloc[a:b]
            o, _ = S.run_bars(name, d, L[a:b], Sg[a:b], '', verbose=False)
            print(f"  {lab:8s} {d.index[0].date()}->{d.index[-1].date()} " + (T.FMT.format(**o) if o else '(poucos)'))
        cst = T.CUSTO[name]
        for mult in (2, 4):
            T.CUSTO[name] = cst * mult
            o, _ = S.run_bars(name, df, L, Sg, '', verbose=False)
            print(f"  custo {mult}x " + T.FMT.format(**o))
        T.CUSTO[name] = cst


if __name__ == '__main__':
    main(*(sys.argv[1:] or []))
