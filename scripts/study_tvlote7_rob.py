"""Robustez do Trailing SL [QuantNomad] no lote 7 (unica celula acima do buy & hold no ouro).

Vizinhanca do % de stop, terços do periodo, out-of-sample (melhor % escolhido na 1a metade, medido
na 2a), custo 2x/4x, e separacao long/short.

uso: python study_tvlote7_rob.py [xau ...]
"""
import os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote7 import run_tsl

TFS = ['15min', '30min', '1h', '4h', '1D']
VALS = (0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 3.5, 4.0)


def bh_sharpe(df):
    r = np.log(df.close).diff().resample('1D').sum()
    r = r[r != 0]
    return float(r.mean() / r.std() * np.sqrt(252))


def cell(name, df, val, long_only=False):
    o, tr = run_tsl(name, df, '', None, False, val=val, long_only=long_only)
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        base = T.CUSTO[name]

        print("\n### vizinhanca (% do stop) -> CAGR | t ; B&H e Sharpe do B&H por TF")
        for tf in TFS:
            df = cache[tf]
            out = []
            for v in VALS:
                o, _ = cell(name, df, v)
                out.append(f"{v}:{o['cagr']:+.1%}/{o['t']:+.1f}")
            print(f"  {tf:6s} B&H {o['bh']:+.1%} Sh {bh_sharpe(df):.2f} | " + ' '.join(out))

        print("\n### 2% por terco do periodo (CAGR estrategia vs B&H)")
        for tf in TFS:
            df = cache[tf]
            parts = np.array_split(np.arange(len(df)), 3)
            s = []
            for p in parts:
                d = df.iloc[p]
                o, _ = cell(name, d, 2.0)
                s.append(f"{d.index[0].year}-{d.index[-1].year}: {o['cagr']:+.1%} vs {o['bh']:+.1%} (t {o['t']:+.1f})")
            print(f"  {tf:6s} " + ' | '.join(s))

        print("\n### OOS: % escolhido na 1a metade (maior CAGR), medido na 2a")
        for tf in TFS:
            df = cache[tf]
            h = len(df) // 2
            a, b = df.iloc[:h], df.iloc[h:]
            best = max(VALS, key=lambda v: cell(name, a, v)[0]['cagr'])
            oa, _ = cell(name, a, best); ob, _ = cell(name, b, best)
            o2, _ = cell(name, b, 2.0)
            print(f"  {tf:6s} IS {a.index[0].date()}..{a.index[-1].date()} melhor {best}% {oa['cagr']:+.1%} "
                  f"(B&H {oa['bh']:+.1%}) | OOS {ob['cagr']:+.1%} t {ob['t']:+.1f} vs B&H {ob['bh']:+.1%} "
                  f"| OOS com 2%: {o2['cagr']:+.1%}")

        print("\n### custo 1x/2x/4x (2%)")
        for tf in TFS:
            df = cache[tf]
            s = []
            for k in (1, 2, 4):
                T.CUSTO[name] = base * k
                o, _ = cell(name, df, 2.0)
                s.append(f"{k}x {o['cagr']:+.1%} t {o['t']:+.1f}")
            T.CUSTO[name] = base
            print(f"  {tf:6s} " + ' | '.join(s))

        print("\n### lados (2%): bp liquido medio e soma por lado; so-long como estrategia")
        for tf in TFS:
            df = cache[tf]
            o, tr = cell(name, df, 2.0)
            ol, _ = cell(name, df, 2.0, long_only=True)
            lg = tr[tr.d > 0]; sh = tr[tr.d < 0]
            print(f"  {tf:6s} long {len(lg)} tr {1e4 * lg.ret.mean():+6.1f}bp soma {lg.ret.sum():+.2f} | "
                  f"short {len(sh)} tr {1e4 * sh.ret.mean():+6.1f}bp soma {sh.ret.sum():+.2f} | "
                  f"so long: CAGR {ol['cagr']:+.1%} Sh {ol['sharpe']:.2f} DD {ol['dd']:.0%} t {ol['t']:+.1f}")


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
