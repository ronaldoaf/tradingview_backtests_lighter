"""Robustez / OOS da ilha de 15m do MACD + SMA 200 (ChartArt, yMCa3XZD).

A grade em ouro (study_macdsma.py) deu uma ilha coerente no 15m: todas as 50 celulas positivas no
liquido, mediana t=1,6 vs controle, e 8 celulas com CAGR acima do buy&hold (Sharpe 0,7-0,93, 600-1800
trades). Aqui estresso essa ilha antes de qualquer veredito:

  1. t de trade (mean/se) alem do t vs controle aleatorio;
  2. subperiodos (3 tercos do historico) - a ilha sobrevive fora do bull 2024-2026?
  3. custo x1 / x2 / x4 por perna (o gatilho inverte muito no 15m: 2 pernas por inversao);
  4. atraso de execucao: +1 e +2 barras de 15m depois do sinal (gap de execucao medido no fade);
  5. execucao no fechamento do sinal (EXEC=1) como contraste otimista;
  6. OOS nos outros ativos (us100, wti, btc, eth) com as MESMAS celulas, sem reotimizar.

uso: python study_macdsma_rob.py
"""
import os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO, FUND
from study_macdconf import resample, OHLC
import study_macdsma as M
from study_macdsma import BASE, signals, run

CUSTO.setdefault('eth', 0.8e-4)
FUND.setdefault('eth', 9.0)
BASE_CUSTO = dict(CUSTO)

# as 8 celulas de 15m que bateram o B&H no ouro + os defaults do script
ILHA = [dict(FAST=12, SLOW=26, SIG=9, VSLOW=50, QL=0),
        dict(FAST=12, SLOW=26, SIG=9, VSLOW=100, QL=0),
        dict(FAST=12, SLOW=26, SIG=9, VSLOW=400, QL=1),
        dict(FAST=8, SLOW=17, SIG=9, VSLOW=50, QL=0),
        dict(FAST=8, SLOW=17, SIG=9, VSLOW=100, QL=0),
        dict(FAST=8, SLOW=17, SIG=9, VSLOW=400, QL=0),
        dict(FAST=12, SLOW=26, SIG=5, VSLOW=100, QL=0),
        dict(FAST=12, SLOW=26, SIG=5, VSLOW=200, QL=0)]
DEF = dict(FAST=12, SLOW=26, SIG=9, VSLOW=200, QL=1)


def load_m1(name):
    if name == 'xau':
        return _clean(pd.read_parquet(os.path.join(D, 'data', 'gold', 'xau_1m.parquet')))
    if name in ('us100', 'us500', 'wti'):
        import glob
        fs = sorted(glob.glob(os.path.join(D, 'data', f'duka1m_{name}', '*.parquet')))
        return _clean(pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f) > 0]))
    sym = {'btc': 'BTCUSDT', 'eth': 'ETHUSDT'}[name]
    b = pd.read_parquet(os.path.join(D, 'data', 'binance', 'klines_1m', f'{sym}.parquet'))
    return _clean(b.set_index(pd.to_datetime(b.ts, unit='ms', utc=True))[['o', 'h', 'l', 'c']]
                  .set_axis(OHLC, axis=1))


def _clean(x):
    x = x[~x.index.duplicated()].sort_index()[OHLC]
    return x[x.high >= x.low]


def shifted(df, p, d):
    """mesma celula, mas o sinal so e executado d barras depois (atraso de execucao)."""
    L, S = signals(df, p)
    if d:
        L = np.concatenate([np.zeros(d, bool), L[:-d]])
        S = np.concatenate([np.zeros(d, bool), S[:-d]])
    return L, S


def one(name, df, p, delay=0, label=''):
    if delay == 0:
        o, tr = run(name, p, df=df, verbose=False)
    else:
        L, S = shifted(df, p, delay)
        tr = M.to_trades(df, L, S, p, name)
        if len(tr) < 5: return None
        import study_bbrsi as B
        st = B.equity_stats(df, tr, name)
        yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
        ctl = B.control(df, tr, name)
        o = dict(trades=len(tr), bp_bruto=1e4 * tr.bruto.mean(), bp_liq=1e4 * tr.ret.mean(),
                 cagr=st['cagr'], bh=np.expm1(np.log(df.close.iloc[-1] / df.close.iloc[0]) / yrs),
                 sharpe=st['sharpe'], dd=st['dd'], expo=st['expo'], ctl_bp=1e4 * ctl.mean(),
                 t=(tr.ret.mean() - ctl.mean()) / (ctl.std(ddof=1) + 1e-12))
    if o is None: return None
    if delay == 0:
        L, S = signals(df, p)
        tr2 = M.to_trades(df, L, S, p, name)
    else:
        tr2 = tr
    o['t_trade'] = tr2.ret.mean() / (tr2.ret.std(ddof=1) / np.sqrt(len(tr2)))
    o['cfg'] = f"{p['FAST']}/{p['SLOW']}/{p['SIG']} V{p['VSLOW']} QL{p['QL']}"
    o['label'] = label
    return o


def show(rows, title):
    if not rows:
        print(f"\n{title}: nada"); return
    g = pd.DataFrame([r for r in rows if r])
    cols = ['label', 'cfg', 'trades', 'bp_bruto', 'bp_liq', 'cagr', 'bh', 'sharpe', 'dd', 'expo',
            'ctl_bp', 't', 't_trade']
    print(f"\n{title}")
    print(g[cols].to_string(index=False, float_format=lambda v: f'{v:.3f}'))
    return g


def main():
    print("==================== OURO 15m: ilha + defaults ====================")
    m1 = load_m1('xau')
    df = resample(m1, '15min')
    cfgs = [('def', DEF)] + [(f'i{k+1}', c) for k, c in enumerate(ILHA)]

    rows = [one('xau', df, dict(BASE, TF='15min', **c), label=lb) for lb, c in cfgs]
    show(rows, "-- base (custo 1x, execucao na abertura seguinte)")

    print("\n==================== subperiodos (3 tercos) ====================")
    n = len(df); cuts = [(0, n // 3), (n // 3, 2 * n // 3), (2 * n // 3, n)]
    for k, (a, b) in enumerate(cuts):
        d = df.iloc[a:b]
        rows = [one('xau', d, dict(BASE, TF='15min', **c), label=lb) for lb, c in cfgs]
        show(rows, f"-- terco {k+1}: {d.index[0].date()} -> {d.index[-1].date()}")

    print("\n==================== custo por perna ====================")
    for mult in (2, 4):
        CUSTO['xau'] = BASE_CUSTO['xau'] * mult
        rows = [one('xau', df, dict(BASE, TF='15min', **c), label=f'{lb} x{mult}') for lb, c in cfgs]
        show(rows, f"-- custo {mult}x ({1e4*CUSTO['xau']:.1f} bp/perna)")
    CUSTO['xau'] = BASE_CUSTO['xau']

    print("\n==================== atraso de execucao ====================")
    for d_ in (1, 2):
        rows = [one('xau', df, dict(BASE, TF='15min', **c), delay=d_, label=f'{lb} +{d_}b') for lb, c in cfgs]
        show(rows, f"-- sinal executado {d_} barra(s) de 15m depois")

    print("\n==================== execucao no fechamento (EXEC=1) ====================")
    rows = [one('xau', df, dict(BASE, TF='15min', EXEC=1, **c), label=lb) for lb, c in cfgs]
    show(rows, "-- EXEC=1 (otimista)")

    print("\n==================== OOS: outros ativos, mesmas celulas ====================")
    for name in ('us100', 'wti', 'btc', 'eth'):
        try:
            mm = load_m1(name)
        except Exception as e:
            print(f"\n{name}: sem dados ({e})"); continue
        d = resample(mm, '15min')
        print(f"\n### {name}: {d.index[0].date()} -> {d.index[-1].date()} ({len(d)/1e3:.0f}k barras 15m)")
        rows = [one(name, d, dict(BASE, TF='15min', **c), label=lb) for lb, c in cfgs]
        show(rows, f"-- {name} 15m")


if __name__ == '__main__':
    main()
