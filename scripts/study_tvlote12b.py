"""Lote 12, substituto do template: Solution Zigma (Fibonacci Impulse) (k1GLeZco, Pine v6).

O Template Trailing Strategy (n8bgynWl) foi ignorado por ser template (regra do usuario); este e o
proximo da lista. Modo padrao "Original 0 Extra (Zigma with DMI + CE)":
  - src = nivel 0,5 do Fibonacci automatico do 1H (aqui: meio da faixa maxima-minima das 12 ultimas
    barras de 1H fechadas; a biblioteca AutoFiboRetrace nao esta disponivel); open_p = EMA12(src).
  - DMI(14) do 15m (o script cai no ramo do 15m porque o timeframe '60' nao bate com os rotulos).
  - Chandelier Exit (1, 3) define a direcao.
  - Long: close cruza acima de open_p, DI+ >= 25 e DI+ > ADX, CE de alta, sem posicao.
    Sai (modo "Condition") quando close < open_p com CE de baixa. Short no espelho.
  Variante RR: stop 1% e alvo 2R.
Series de timeframe maior entram so depois do fechamento da barra maior (sem vazamento).

uso: python study_tvlote12b.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc
from study_tvlote8 import ema, dmi
from study_tvlote9 import summary

NAN = np.nan


def htf_on(df, htf_df, values, htf):
    """Valor da ultima barra HTF FECHADA ate o fechamento de cada barra do grafico."""
    close_t = htf_df.index + pd.Timedelta(htf)
    s = pd.Series(values, index=close_t)
    dt = df.index[1] - df.index[0]
    return s.reindex(df.index + dt, method='ffill').to_numpy()


def chandelier(h, l, c, n, m):
    a = m * T.atr_rma(h, l, c, n)
    hh = pd.Series(h).rolling(n).max().to_numpy() if n > 1 else h
    ll = pd.Series(l).rolling(n).min().to_numpy() if n > 1 else l
    ls = hh - a; ss = ll + a
    nn = len(c); d = np.ones(nn); lsv = np.copy(ls); ssv = np.copy(ss)
    for i in range(1, nn):
        lp = lsv[i - 1] if lsv[i - 1] == lsv[i - 1] else ls[i]
        sp = ssv[i - 1] if ssv[i - 1] == ssv[i - 1] else ss[i]
        lsv[i] = max(ls[i], lp) if c[i - 1] > lp else ls[i]
        ssv[i] = min(ss[i], sp) if c[i - 1] < sp else ss[i]
        d[i] = 1 if c[i] > sp else (-1 if c[i] < lp else d[i - 1])
    return d


def run_zig(name, df, mm, tag, rows=None, verbose=True, h1=None, m15=None, lb=12, use_dmi=True, rr=False, sl=0.01,
            long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    H = h1.high.rolling(lb).max().to_numpy(); Lw = h1.low.rolling(lb).min().to_numpy()
    src = htf_on(df, h1, (H + Lw) / 2, '1h')
    op = ema(np.nan_to_num(src, nan=c[0]), 12)
    p, m, adx = dmi(*(m15[k].to_numpy(float) for k in ('high', 'low', 'close')), 14)
    p = htf_on(df, m15, p, '15min'); m = htf_on(df, m15, m, '15min'); adx = htf_on(df, m15, adx, '15min')
    d = chandelier(h, l, c, 1, 3.0)
    L = T.xover(c, op) & (d == 1); S = T.xunder(c, op) & (d != 1)
    if use_dmi:
        L &= (p >= 25) & (p > adx); S &= (m >= 25) & (m > adx)
    if rr:
        r = gsim(df, mm, L, S, slp=sl, tpp=2 * sl, rev=False, long_ok=long_ok, short_ok=short_ok)
    else:
        XL = (c < op) & (d != 1); XS = (c > op) & (d == 1)
        r = gsim(df, mm, L, S, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        cache = {tf: T.resample(m1, tf) for tf in ['5min', '15min', '30min', '1h']}
        rows = []
        print("\n### 6. Solution Zigma (Fibo 0,5 do 1H, DMI 15m, CE 1x3)")
        for tf in ['5min', '15min', '30min', '1h']:
            df = cache[tf]
            run_zig(name, df, mm, f"{tf} ZIG default", rows, h1=cache['1h'], m15=cache['15min'], est='zig', TF=tf,
                    cfg='lb12 dmi cond')
            for lb, ud, rr, side in itertools.product((6, 12, 24), (True, False), (False, True), ('ambos', 'long')):
                run_zig(name, df, mm, '', rows, False, h1=cache['1h'], m15=cache['15min'], lb=lb, use_dmi=ud, rr=rr,
                        short_ok=side == 'ambos', est='zig', TF=tf,
                        cfg=f'lb{lb} dmi{int(ud)} ' + ('rr' if rr else 'cond') + f' {side}')
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote12b')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
