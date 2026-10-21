"""Vix FIX / StochRSI Strategy (TDxSLJRA, Pine v2). So long, pyramiding=9 (3% do capital cada).

Regra publicada:
  - Williams Vix Fix: wvf = (highest(close,22) - low) / highest(close,22) * 100, com banda de
    Bollinger (20, 2) e teto de percentil (highest(wvf,50) * 0.85).
  - Entrada long (filtered OU aggressive): o wvf ESTAVA acima da banda/teto na barra anterior e
    o preco confirma (upRange / upRange_Aggr), close > close[3] e close abaixo do close de 40 OU
    14 barras atras. Cada sinal soma uma unidade ate 9.
  - Saida total: crossover(k, d) do estocastico lento (14,3,3) com k > 80.
  O RSI e calculado e nunca usado. Sem security(), sem stop, sem alvo.

Execucao na abertura seguinte. Retorno medido sobre o nocional cheio (9 unidades = 1x);
'u1' = so a primeira unidade (pyramiding=0). Controle: mesmo lado e mesma duracao.

uso: python study_vixfix.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_zigzagpa  # noqa: F401  (instala o controle vetorizado em T.control_dur)

TFS = ['15min', '30min', '1h', '4h', '1D']


def lag(x, k):
    return np.concatenate([np.full(k, np.nan), x[:-k]])


def roll_max(x, n):
    return pd.Series(x).rolling(n).max().to_numpy()


def roll_min(x, n):
    return pd.Series(x).rolling(n).min().to_numpy()


def signals(df, pd_=22, bbl=20, mult=2.0, lb=50, ph=0.85, ltLB=40, mtLB=14, st=3,
            slen=14, sk=3, sd=3, ob=80, use_filt=True, use_aggr=True):
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    hc = roll_max(c, pd_)
    wvf = (hc - l) / hc * 100
    up = T.sma(wvf, bbl) + mult * T.stdev_pop(wvf, bbl)
    rh = roll_max(wvf, lb) * ph
    was = (lag(wvf, 1) >= lag(up, 1)) | (lag(wvf, 1) >= lag(rh, 1))
    now_in = (wvf < up) & (wvf < rh)
    filt = was & now_in
    aggr = was & ~now_in
    upr = (l > lag(l, 1)) & (c > lag(h, 1))
    upa = (c > lag(c, 1)) & (c > lag(o, 1))
    base = (c > lag(c, st)) & ((c < lag(c, ltLB)) | (c < lag(c, mtLB)))
    L = (use_filt & upr & base & filt) | (use_aggr & upa & base & aggr)
    ll = roll_min(l, slen); hh = roll_max(h, slen)
    with np.errstate(divide='ignore', invalid='ignore'):
        sto = 100 * (c - ll) / (hh - ll)
    k = T.sma(sto, sk); d = T.sma(k, sd)
    X = T.xover(k, d) & (k > ob)
    return L, X


def run(name, df, L, X, tag, rows=None, verbose=True, units=9, **extra):
    raw = T.engine_signal_exit(df, L, X, maxunits=units)
    raw = [(i, j, u / units, ent) for i, j, u, ent in raw]   # 9 unidades = nocional cheio
    tr = T.book(df, raw, name)
    if len(tr):
        tr['bruto'] *= tr.u; tr['ret_sf'] = tr.bruto - 2 * T.CUSTO[name] * tr.u
        tr['fund'] *= tr.u; tr['ret'] = tr.ret_sf - tr.fund
    o = T.summarize(df, tr, name)
    if o:
        o['u_med'] = float(tr.u.mean() * units)
        if verbose: T.line(tag, o)
        if rows is not None: rows.append(dict(o, tag=tag, **extra))
    elif verbose:
        print(f"  {tag:<34} (menos de 10 trades)")
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        rows = []
        for tf in TFS:
            df = T.resample(m1, tf)
            print(f"\n### {tf}")
            L, X = signals(df)
            run(name, df, L, X, f"{tf} default (pyr 9)", rows, est='default', TF=tf, cfg='default')
            run(name, df, L, X, f"{tf} default (1 unidade)", rows, units=1, est='u1', TF=tf, cfg='default')
            for ph, st, ob, filt in itertools.product((0.85, 0.9, 0.95), (1, 3, 5), (70, 80, 90),
                                                      ('ambos', 'filt', 'aggr')):
                L, X = signals(df, ph=ph, st=st, ob=ob, use_filt=filt != 'aggr', use_aggr=filt != 'filt')
                for u in (1, 9):
                    run(name, df, L, X, '', rows, verbose=False, units=u, est='grade', TF=tf,
                        cfg=f'ph{ph} str{st} ob{ob} {filt} u{u}')
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'results', f'study_vixfix_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name}: {len(g)} celulas ===")
        print(f"  liq>0 {int((g.bp_liq > 0).sum())} | liq>0 e t>2 {int(((g.bp_liq > 0) & (g.t > 2)).sum())}"
              f" | CAGR>B&H {int((g.cagr > g.bh).sum())}")
        cols = ['TF', 'cfg', 'trades', 'por_ano', 'dias', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh',
                'sharpe', 'dd', 'expo', 'ctl_bp', 't']
        print("\n  top 15 por t contra o controle:")
        print(g.sort_values('t', ascending=False).head(15)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))
        print("\n  top 10 por CAGR:")
        print(g.sort_values('cagr', ascending=False).head(10)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
