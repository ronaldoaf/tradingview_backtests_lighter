"""Lote 13 do TradingView (2026-10-22): 5 estrategias nos 5 ativos (ver docs/LOTE13_TV.md).

  1. Fibonacci + RSI (Ouv7XVfc, Pine v4)
     Bandas VWMA(hlc3, 200) +- k*3*stdev. Long: low < banda -1 e RSI14[1] cruza 30 para cima, com
     high < banda -0,764 (o alvo). Alvo = banda -0,764 da barra do sinal; stop 0,2% (o input 2 vira
     2*0,001). Short no espelho. A ordem limite no close virou ordem a mercado na abertura seguinte.
  2. Scalping Trading System Crypto and Stocks (YotdMm0M, Pine v5)
     src = low. Long: close > SMA25, close > EMA200, dentro do Keltner(10, 2xATR14), histograma MACD
     (4/34/5) < 0 e Stoch(10) < 50. Short no espelho. Sem saida: so o sinal contrario inverte.
  3. UT Bot v5 (2wkJx7Ix, Pine v5)
     Trailing stop ATR (a=1, ATR 11) sobre o open; compra quando HMA(2) do open cruza acima do stop,
     sai quando cruza abaixo. Long-only por padrao (AllowSell=false). TP/SL de $50000 nunca disparam.
  4. Squeeze Momentum [LazyBear] (qp9BoNyS, Pine v3)
     BB(14, 2) dentro/fora do KC(16, 1,5, TR). Entra quando o squeeze solta (scolor vira aqua) com
     momento subindo acima de zero (long) ou caindo abaixo (short); sai quando o momento perde forca
     (green/maroon). A janela de datas de 2018 do script foi ignorada.
  5. Ichimoku Kinko Hyo Basic (XZcsLIEW, Pine v1)
     Long: Tenkan(9) > Kijun(26), mom(close, 25) > 0, close acima da nuvem deslocada 25 barras.
     Short no espelho. Sinal contrario inverte.

uso: python study_tvlote13.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote10 import shift

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)


# ------------------------------------------------------------------ 1. Fibonacci + RSI
def run_fib(name, df, mm, tag, rows=None, verbose=True, length=200, mult=3.0, sl=0.002, rl=14, long_ok=True,
            short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float); src = (h + l + c) / 3
    basis = roll(src * v, length).sum().to_numpy() / roll(v, length).sum().to_numpy()
    dev = mult * roll(src, length).std(ddof=0).to_numpy()
    fu1, fd1 = basis + dev, basis - dev
    fu7, fd7 = basis + 0.764 * dev, basis - 0.764 * dev
    r1 = shift(T.rsi_wilder(c, rl), 1)
    L = (l < fd1) & T.xover(r1, np.full_like(r1, 30.0)) & (h < fd7)
    S = (h > fu1) & T.xunder(r1, np.full_like(r1, 70.0)) & (l > fu7)
    r = gsim(df, mm, L, S, TPL=fd7, TPS=fu7, slp=sl, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Scalping Trading System
def run_scalp(name, df, mm, tag, rows=None, verbose=True, sma_len=25, ema_len=200, long_ok=True, short_ok=True,
              **extra):
    o, h, l, c = ohlc(df)
    src = l
    out = T.sma(src, sma_len); out2 = ema(src, ema_len) if ema_len else np.full_like(c, -np.inf)
    ma = T.sma(src, 10); rg = T.atr_rma(h, l, c, 14)
    up, lo = ma + 2 * rg, ma - 2 * rg
    k = 100 * (c - roll(l, 10).min().to_numpy()) / (roll(h, 10).max().to_numpy() - roll(l, 10).min().to_numpy())
    macd = ema(src, 4) - ema(src, 34); hist = macd - ema(macd, 5)
    inside = (c < up) & (c > lo)
    L = (c > out) & inside & (hist < 0) & (k < 50) & (c > out2)
    S = (c < out) & inside & (hist > 0) & (k > 50) & ((c < out2) if ema_len else True)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. UT Bot
def ut_stop(src, nl):
    n = len(src); t = np.zeros(n)
    for i in range(1, n):
        p = t[i - 1]; s = src[i]; s1 = src[i - 1]
        if s > p and s1 > p:
            t[i] = max(p, s - nl[i])
        elif s < p and s1 < p:
            t[i] = min(p, s + nl[i])
        else:
            t[i] = s - nl[i] if s > p else s + nl[i]
    return t


def run_ut(name, df, mm, tag, rows=None, verbose=True, a=1.0, atr_n=11, ma_n=2, shorts=False, **extra):
    o, h, l, c = ohlc(df)
    src = o
    t = ut_stop(src, np.nan_to_num(a * T.atr_rma(h, l, c, atr_n)))
    th = T.hma(src, ma_n) if ma_n > 1 else src
    buy = (src > t) & T.xover(th, t); sell = (src < t) & T.xover(t, th)
    if shorts:
        r = gsim(df, mm, buy, sell, rev=True)
    else:
        r = gsim(df, mm, buy, np.zeros_like(buy), sell, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Squeeze Momentum
def linreg_end(x, n):
    """ta.linreg(x, n, 0): valor da reta de regressao na ultima barra da janela."""
    idx = np.arange(n, dtype=float); xm = idx.mean(); den = ((idx - xm) ** 2).sum()

    def f(w):
        b = ((idx - xm) * (w - w.mean())).sum() / den
        return w.mean() + b * (n - 1 - xm)
    return roll(x, n).apply(f, raw=True).to_numpy()


def run_sqz(name, df, mm, tag, rows=None, verbose=True, bl=14, bm=2.0, kl=16, km=1.5, long_ok=True, short_ok=True,
            **extra):
    o, h, l, c = ohlc(df)
    basis = T.sma(c, bl); dev = bm * roll(c, bl).std(ddof=0).to_numpy()
    ma = T.sma(c, kl); pc = shift(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    rg = T.sma(tr, kl)
    sqzOn = (basis - dev > ma - km * rg) & (basis + dev < ma + km * rg)
    sqzOff = (basis - dev < ma - km * rg) & (basis + dev > ma + km * rg)
    aqua = sqzOff & ~sqzOn
    mid = ((roll(h, kl).max() + roll(l, kl).min()).to_numpy() / 2 + T.sma(c, kl)) / 2
    val = linreg_end(c - mid, kl)
    v1 = np.nan_to_num(shift(val, 1))
    lime = (val > 0) & (val > v1); green = (val > 0) & ~(val > v1)
    red = (val <= 0) & (val < v1); maroon = (val <= 0) & ~(val < v1)
    rel = aqua & ~np.concatenate([[True], aqua[:-1]])
    L = rel & lime; S = rel & red
    r = gsim(df, mm, L, S, green, maroon, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Ichimoku basico
def run_ichi(name, df, mm, tag, rows=None, verbose=True, ts=9, ks=26, sb=52, off=26, long_ok=True, short_ok=True,
             **extra):
    o, h, l, c = ohlc(df)
    mid = lambda n: (roll(h, n).max() + roll(l, n).min()).to_numpy() / 2
    tk, kj = mid(ts), mid(ks)
    sa = (tk + kj) / 2; sbv = mid(sb)
    hi = np.fmax(shift(sa, off - 1), shift(sbv, off - 1)); lo = np.fmin(shift(sa, off - 1), shift(sbv, off - 1))
    mom = c - shift(c, off - 1)
    bull = (tk > kj) & (mom > 0) & (c > hi); bear = (tk < kj) & (mom < 0) & (c < lo)
    r = gsim(df, mm, bull, bear, bear if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. Fibonacci + RSI (VWMA200 x 3 stdev, alvo 0,764, stop 0,2%)")
        for tf in TFS:
            df = cache[tf]
            run_fib(name, df, mm, f"{tf} FIB default", rows, est='fib', TF=tf, cfg='l200 m3 sl0.002')
            for ln, mu, sl, side in itertools.product((50, 100, 200), (1.5, 2.0, 3.0), (0.002, 0.01, 0.03), side2):
                run_fib(name, df, mm, '', rows, False, length=ln, mult=mu, sl=sl, short_ok=side == 'ambos', est='fib',
                        TF=tf, cfg=f'l{ln} m{mu} sl{sl} {side}')

        print("\n### 2. Scalping Trading System (SMA25/EMA200, Keltner, MACD 4/34, Stoch 10)")
        for tf in TFS:
            df = cache[tf]
            run_scalp(name, df, mm, f"{tf} SCALP default", rows, est='scalp', TF=tf, cfg='s25 e200 ambos')
            for sl_, el, side in itertools.product((10, 25, 50), (200, 0), side2):
                run_scalp(name, df, mm, '', rows, False, sma_len=sl_, ema_len=el, short_ok=side == 'ambos',
                          est='scalp', TF=tf, cfg=f's{sl_} e{el} {side}')

        print("\n### 3. UT Bot v5 (a=1, ATR11, HMA2 do open, long-only)")
        for tf in TFS:
            df = cache[tf]
            run_ut(name, df, mm, f"{tf} UT default", rows, est='ut', TF=tf, cfg='a1 atr11 hma2 long')
            for a, an, sh in itertools.product((1.0, 2.0, 3.0, 5.0), (11, 30), (False, True)):
                run_ut(name, df, mm, '', rows, False, a=a, atr_n=an, shorts=sh, est='ut', TF=tf,
                       cfg=f'a{a} atr{an} hma2 ' + ('ambos' if sh else 'long'))

        print("\n### 4. Squeeze Momentum [LazyBear] (BB14x2, KC16x1,5)")
        for tf in TFS:
            df = cache[tf]
            run_sqz(name, df, mm, f"{tf} SQZ default", rows, est='sqz', TF=tf, cfg='bb14 kc16 ambos')
            for bl, kl, side in itertools.product((14, 20), (16, 20), side2):
                run_sqz(name, df, mm, '', rows, False, bl=bl, kl=kl, short_ok=side == 'ambos', est='sqz', TF=tf,
                        cfg=f'bb{bl} kc{kl} {side}')

        print("\n### 5. Ichimoku basico (9/26/52, deslocamento 26)")
        for tf in TFS:
            df = cache[tf]
            run_ichi(name, df, mm, f"{tf} ICHI default", rows, est='ichi', TF=tf, cfg='9/26/52 ambos')
            for (t_, k_, b_), side in itertools.product(((9, 26, 52), (20, 60, 120)), side2):
                run_ichi(name, df, mm, '', rows, False, ts=t_, ks=k_, sb=b_, off=k_, short_ok=side == 'ambos',
                         est='ichi', TF=tf, cfg=f'{t_}/{k_}/{b_} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote13')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
