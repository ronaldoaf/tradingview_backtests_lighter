"""Lote 12 do TradingView (2026-10-22): 5 estrategias nos 5 ativos (ver docs/LOTE12_TV.md).

  1. TK Cross > EMA200 (Ichimoku, 88TwdvFZ, Pine v3)
     Long-only: compra com Tenkan(20) > Kijun(60) e close > EMA200; sai quando Tenkan < Kijun.
  2. Powertrend - Volume Range Filter [wbburgin] (45FlB2qH, Pine v5)
     Range filter (faixa suavizada de 200) que so anda para cima quando o volume sobe; compra quando o
     filtro sobe e o close cruza a banda de cima; sai quando o filtro cai e o close perde a de baixo.
     Long-only.
  3. (Template Trailing Strategy, n8bgynWl: ignorado por ser template; o substituto, Solution Zigma,
     esta em study_tvlote12b.py)
  4. Acrypto - Weighted Strategy v1.4.8 (OF3TzrNS, Pine v5)
     Cinco gatilhos com peso 1 (cruzamento MACD EMA16(hl2)-EMA36(high) x SMA9, saida de sobrevenda do
     Stoch RSI, do RSI, virada do SuperTrend(2, 2,4), cruzamento EMA46 x EMA82); entra quando >= 2
     disparam juntos; stop 6%; sinal contrario inverte. As saidas parciais (15% a cada +6,8%) e o
     stop movel nao foram reproduzidos.
  5. Simple RSI-MA Algo (qSoZRbX7, Pine v2)
     SMA50 do RSI10 cruzando 50 inverte a posicao. Sempre no mercado.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos no M1 (stop antes do alvo).
Custo CUSTO + funding de cada ativo. Controle: mesmo lado e mesma duracao.

uso: python study_tvlote12.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1, _st_dir
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote10 import shift

NAN = np.nan


def donch(h, l, n):
    return (pd.Series(h).rolling(n).max() + pd.Series(l).rolling(n).min()).to_numpy() / 2


def flips(state):
    s = np.asarray(state, bool)
    up = s & ~np.roll(s, 1); dn = ~s & np.roll(s, 1)
    up[0] = dn[0] = False
    return up, dn


# ------------------------------------------------------------------ 1. TK Cross > EMA200
def run_tk(name, df, mm, tag, rows=None, verbose=True, conv=20, base=60, ema_len=200, shorts=False, **extra):
    o, h, l, c = ohlc(df)
    tk = donch(h, l, conv) > donch(h, l, base)
    L = tk & (c > ema(c, ema_len)) if ema_len else tk
    XL = ~tk
    if shorts:
        S = ~tk & ((c < ema(c, ema_len)) if ema_len else True)
        XS = tk
    else:
        S = np.zeros_like(L); XS = None
    r = gsim(df, mm, L, S, XL, XS, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Powertrend
def smoothrng(x, t, m):
    ad = np.abs(np.diff(x, prepend=x[0]))
    return ema(ema(ad, t), t * 2 - 1) * m


def volrng_filter(c, v, r):
    n = len(c); f = np.empty(n); f[0] = c[0]
    for i in range(1, n):
        p = f[i - 1]
        if v[i] > v[i - 1]:
            f[i] = p if c[i] - r[i] < p else c[i] - r[i]
        else:
            f[i] = p if c[i] + r[i] > p else c[i] + r[i]
    return f


def run_pt(name, df, mm, tag, rows=None, verbose=True, length=200, mult=3.0, use_vol=True, **extra):
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float) if use_vol else np.arange(len(c), dtype=float)   # sem volume: filtro so sobe
    r = smoothrng(c, length, mult)
    f = volrng_filter(c, v, r)
    up = f > shift(f, 1)
    L = up & T.xover(c, f + r); X = ~up & T.xunder(c, f - r)
    r_ = gsim(df, mm, L, np.zeros_like(L), X, None, rev=False)
    return run_g(name, df, r_, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Acrypto Weighted
def acr_signals(df, trig=2):
    o, h, l, c = ohlc(df)
    hl2 = (h + l) / 2
    macd = ema(hl2, 16) - ema(h, 36); sig = T.sma(macd, 9)
    l1, s1 = flips(macd > sig)
    rsi = T.rsi_wilder(c, 14)
    lo = pd.Series(rsi).rolling(14).min().to_numpy(); hi = pd.Series(rsi).rolling(14).max().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        k = T.sma(100 * (rsi - lo) / (hi - lo), 3)
    l2 = (shift(k, 2) <= 27) & ~(k >= 70); s2 = (shift(k, 2) >= 70) & ~(k <= 27)
    l3 = (shift(rsi, 2) <= 30) & ~(rsi >= 77); s3 = (shift(rsi, 2) >= 77) & ~(rsi <= 30)
    d = _st_dir(h, l, c, 2.4 * np.nan_to_num(T.atr_rma(h, l, c, 2)))
    l4 = (d == 1) & (np.roll(d, 1) == -1); s4 = (d == -1) & (np.roll(d, 1) == 1)
    l5, s5 = flips(ema(c, 46) > ema(c, 82))
    wl = sum(x.astype(int) for x in (l1, l2, l3, l4, l5)); ws = sum(x.astype(int) for x in (s1, s2, s3, s4, s5))
    L = wl >= trig; S = (ws >= trig) & ~L     # o script avalia o short antes; os dois juntos: fica o long
    L[0] = S[0] = False
    return L, S


def run_acr(name, df, mm, tag, rows=None, verbose=True, trig=2, sl=0.06, long_ok=True, short_ok=True, **extra):
    L, S = acr_signals(df, trig)
    r = gsim(df, mm, L, S, S if not short_ok else None, L if not long_ok else None, slp=sl,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Simple RSI-MA
def run_rsima(name, df, mm, tag, rows=None, verbose=True, rl=10, ml=50, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    m = T.sma(T.rsi_wilder(c, rl), ml)
    L = T.xover(m, np.full_like(m, 50.0)); S = T.xunder(m, np.full_like(m, 50.0))
    r = gsim(df, mm, L, S, S if not short_ok else None, L if not long_ok else None, long_ok=long_ok,
             short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        side2 = ('ambos', 'long')

        print("\n### 1. TK Cross > EMA200 (20/60, long-only)")
        for tf in TFS:
            df = cache[tf]
            run_tk(name, df, mm, f"{tf} TK default", rows, est='tk', TF=tf, cfg='20/60 ema200 long')
            for (cv, bs), el, sh in itertools.product(((9, 26), (20, 60), (40, 120)), (200, 0), (False, True)):
                run_tk(name, df, mm, '', rows, False, conv=cv, base=bs, ema_len=el, shorts=sh, est='tk', TF=tf,
                       cfg=f'{cv}/{bs} ema{el} ' + ('ambos' if sh else 'long'))

        print("\n### 2. Powertrend (range filter de volume, 200, long-only)")
        for tf in TFS:
            df = cache[tf]
            run_pt(name, df, mm, f"{tf} PT default", rows, est='pt', TF=tf, cfg='l200 m3 vol')
            for ln, mu, uv in itertools.product((50, 100, 200, 400), (1.5, 3.0), (True, False)):
                run_pt(name, df, mm, '', rows, False, length=ln, mult=mu, use_vol=uv, est='pt', TF=tf,
                       cfg=f'l{ln} m{mu} ' + ('vol' if uv else 'semvol'))

        print("\n### 4. Acrypto Weighted (>=2 de 5 gatilhos, stop 6%)")
        for tf in TFS:
            df = cache[tf]
            run_acr(name, df, mm, f"{tf} ACR default", rows, est='acr', TF=tf, cfg='trig2 sl0.06')
            for tg, sl, side in itertools.product((1, 2, 3), (0.06, 0.02, 0.0), side2):
                run_acr(name, df, mm, '', rows, False, trig=tg, sl=sl, short_ok=side == 'ambos', est='acr', TF=tf,
                        cfg=f'trig{tg} sl{sl} {side}')

        print("\n### 5. Simple RSI-MA (SMA50 do RSI10 x 50)")
        for tf in TFS:
            df = cache[tf]
            run_rsima(name, df, mm, f"{tf} RSIMA default", rows, est='rsima', TF=tf, cfg='r10 m50')
            for rl, ml, side in itertools.product((5, 10, 20), (20, 50, 100), side2):
                run_rsima(name, df, mm, '', rows, False, rl=rl, ml=ml, short_ok=side == 'ambos', est='rsima', TF=tf,
                          cfg=f'r{rl} m{ml} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote12')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
