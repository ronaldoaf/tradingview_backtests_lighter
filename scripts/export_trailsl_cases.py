"""Casos de paridade do Trailing SL (QuantNomad) para o modo sombra do paper (test/trailsl.test.js).

Exporta, de fatias reais do ouro, as barras de 30m, os minutos de cada barra e os trades que o motor
do backtest (study_tvlote7._run) produz, para o JS reproduzir bit a bit.

uso: python export_trailsl_cases.py [saida.json]
"""
import json, os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_tvlote7 as S

TF, PCT = '30min', 0.02
FATIAS = [('2018-04-01', '2018-05-15'), ('2020-02-20', '2020-04-05'),
          ('2023-01-15', '2023-03-01'), ('2026-08-20', '2026-10-04')]


def main(out):
    m1 = T.load_m1v('xau')
    casos = []
    for a, b in FATIAS:
        m = m1[(m1.index >= a) & (m1.index < b)]
        df = T.resample(m, TF)
        tr = S.run(df, m, PCT, 'xau')
        b2m = m.index.searchsorted(df.index).astype(np.int64)
        b2m = np.append(b2m, len(m))
        casos.append(dict(
            de=a, ate=b, tf=TF, pct=PCT,
            bars=dict(t=[int(x.value // 10**6) for x in df.index], o=df.open.tolist(),
                      h=df.high.tolist(), l=df.low.tolist(), c=df.close.tolist()),
            b2m=[int(x) for x in b2m],
            m1=dict(t=[int(x.value // 10**6) for x in m.index], o=m.open.tolist(),
                    h=m.high.tolist(), l=m.low.tolist()),
            trades=[] if tr is None else [
                dict(i=int(r.i), j=int(r.j), d=int(r.d), entry=float(r.entry), exit=float(r['exit']),
                     t_in=int(pd.Timestamp(r.t_in).value // 10**6), t_out=int(pd.Timestamp(r.t_out).value // 10**6))
                for _, r in tr.iterrows()],
        ))
        print(f"{a} -> {b}: {len(df)} barras de 30m, {len(m)} minutos, "
              f"{0 if tr is None else len(tr)} trades", flush=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(dict(regra=dict(tf=TF, pct=PCT, sym='xau'), casos=casos), f)
    print('ok ->', out, round(os.path.getsize(out) / 1e6, 1), 'MB')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'results', 'trailsl_cases.json'))
