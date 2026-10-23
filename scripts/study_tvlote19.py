"""Lote 19 do TradingView (2026-10-23): 5 estrategias nos 5 ativos (ver docs/LOTE19_TV.md).

  1. BEST ABCD Pattern Strategy (TWSr0hGH, Pine v4)
     Zigzag de fractais Bill Williams (pivo em high[2]/low[2], confirmado 2 barras depois). ABCD de alta
     quando BC/AB entre 0,382 e 0,886, CD/BC entre 1,13 e 2,618 e D < C; baixa no espelho. Entra na
     primeira barra do padrao, inverte. TP 100 / SL 20 em USD viraram % na proporcao 5:1.
  2. HHLL Strategy (CRNp5xev)
     BB(hlc3, 29, 2); xHHM = banda sup + meia largura, xLLM = banda inf - meia largura. pos = -1 se a
     maxima passa xHHM[1], +1 se a minima passa xLLM[1]; reverse=true (padrao) inverte o sinal.
  3. UT Bot v2 (lDGmh7ou, Pine v6)
     Trailing stop ATR(10) x 1 no close; compra quando o close cruza acima do stop, vende abaixo; inverte.
  4. 3EMA (9bA3Z56w)
     Long quando EMA21 cruza acima da EMA55, TP close + 3 ATR14, SL close - 2 ATR14; fecha quando EMA9
     cruza abaixo da EMA21. Long-only. O filtro de data ate 2022 foi ignorado.
  5. Cipher B+ Divergence EMA Pullback (ywcSiaaV, Pine v4)
     WaveTrend(14,10) cruzando em sobrevenda (wt2 <= -60) + area MFI > 0 + close > EMA150 + pullback
     (close cruza acima da EMA50 depois de 3 barras acima dela); short no espelho (wt2 >= 53). Saida TP
     2 ATR11 / SL 4 ATR11. As EMAs do script vem do grafico de 30m; aqui usamos as do proprio TF.

uso: python study_tvlote19.py xau us100 wti btc eth
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

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
sh = lambda x, k: np.concatenate([np.full(k, NAN), x[:-k]])


# ------------------------------------------------------------------ 1. ABCD
def abcd_signals(h, l):
    n = len(h)
    top = np.zeros(n, bool); bot = np.zeros(n, bool)
    top[4:] = (h[:-4] < h[2:-2]) & (h[1:-3] <= h[2:-2]) & (h[2:-2] >= h[3:-1]) & (h[2:-2] > h[4:])
    bot[4:] = (l[:-4] > l[2:-2]) & (l[1:-3] >= l[2:-2]) & (l[2:-2] <= l[3:-1]) & (l[2:-2] < l[4:])
    bull = np.zeros(n, bool); bear = np.zeros(n, bool)
    lt = lb = -10 ** 9; zz = []; pb = pr = False
    for i in range(n):
        tc1, bc1 = i - 1 - lt, i - 1 - lb       # barssince[1]
        z = NAN
        if top[i] and tc1 > bc1: z = h[i - 2]
        elif bot[i] and tc1 < bc1: z = l[i - 2]
        if top[i]: lt = i
        if bot[i]: lb = i
        if z == z: zz.append(z)
        cb = cr = False
        if len(zz) >= 4:
            a, b, c, d = zz[-4:]
            abc = abs(b - c) / abs(a - b) if a != b else 0
            bcd = abs(c - d) / abs(b - c) if b != c else 0
            ok = 0.382 <= abc <= 0.886 and 1.13 <= bcd <= 2.618
            cb, cr = ok and d < c, ok and d > c
        bull[i] = cb and not pb; bear[i] = cr and not pr; pb, pr = cb, cr
    return bull, bear


def run_abcd(name, df, mm, tag, rows=None, verbose=True, sl=0.01, rr=5.0, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    L, S = abcd_signals(h, l)
    r = gsim(df, mm, L, S & ~L, slp=sl, tpp=sl * rr, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. HHLL
def run_hhll(name, df, mm, tag, rows=None, verbose=True, ln=29, reverse=True, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    src = (h + l + c) / 3
    mid = T.sma(src, ln); dev = 2 * roll(src, ln).std(ddof=0).to_numpy()
    up, lo = mid + dev, mid - dev; half = dev
    hhm, llm = sh(up + half, 1), sh(lo - half, 1)
    pos = np.zeros(len(c)); p = 0
    for i in range(len(c)):
        if h[i] > hhm[i]: p = -1
        elif l[i] < llm[i]: p = 1
        pos[i] = p
    if reverse: pos = -pos
    prev = np.concatenate([[0], pos[:-1]])
    L = (pos == 1) & (prev != 1); S = (pos == -1) & (prev != -1)
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. UT Bot v2
def run_ut(name, df, mm, tag, rows=None, verbose=True, an=10, mult=1.0, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    slv = mult * T.atr_rma(h, l, c, an)
    t = np.zeros(len(c)); p = 0.0
    for i in range(len(c)):
        s1 = c[i - 1] if i else c[i]
        v = slv[i] if slv[i] == slv[i] else 0.0
        if c[i] > p and s1 > p: t[i] = max(p, c[i] - v)
        elif c[i] < p and s1 < p: t[i] = min(p, c[i] + v)
        elif c[i] > p: t[i] = c[i] - v
        else: t[i] = c[i] + v
        p = t[i]
    L, S = T.xover(c, t), T.xover(t, c)
    L[:an] = S[:an] = False
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. 3EMA
def run_3ema(name, df, mm, tag, rows=None, verbose=True, tpm=3.0, slm=2.0, **extra):
    o, h, l, c = ohlc(df)
    e9, e21, e55 = ema(c, 9), ema(c, 21), ema(c, 55)
    a = T.atr_rma(h, l, c, 14)
    L = T.xover(e21, e55); L[:55] = False
    XL = T.xunder(e9, e21)
    SLL = c - slm * a if slm else None
    TPL = c + tpm * a if tpm else None
    r = gsim(df, mm, L, np.zeros_like(L), XL, None, SLL=SLL, TPL=TPL, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Cipher B+ EMA pullback
def run_cipher(name, df, mm, tag, rows=None, verbose=True, tpm=2.0, slm=4.0, use_wt=True, long_ok=True,
               short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    ap = (h + l + c) / 3
    esa = ema(ap, 14); d = ema(np.abs(ap - esa), 14)
    with np.errstate(divide='ignore', invalid='ignore'):
        ci = np.nan_to_num((ap - esa) / (0.015 * d))
        mf = np.nan_to_num((c - o) / (h - l) * 200)
    wt1 = ema(ci, 10); wt2 = T.sma(wt1, 4)
    x = T.xover(wt1, wt2) | T.xunder(wt1, wt2)
    buy = x & (wt2 <= -60) & (wt2 - wt1 <= 0); sell = x & (wt2 >= 53) & (wt2 - wt1 >= 0)
    mfi = T.sma(mf, 71) - 1.5
    e1, e2 = ema(c, 150), ema(c, 50)
    ab = c > e2; be = c < e2
    def run3(m, k): return sh(m.astype(float), k) == 1
    pbl2 = (run3(ab, 2) & run3(ab, 3) & run3(ab, 4)) | (run3(ab, 5) & run3(ab, 6) & run3(ab, 7)) | \
           (run3(ab, 8) & run3(ab, 9) & run3(ab, 10))
    pbs2 = (run3(be, 2) & run3(be, 3) & run3(be, 4)) | (run3(be, 5) & run3(be, 6) & run3(be, 7)) | \
           (run3(be, 8) & run3(be, 9) & run3(be, 10))
    L = (c > e1) & (wt2 < 0) & (mfi > 0) & T.xover(c, e2) & pbl2
    S = (c < e1) & (wt2 > 0) & (mfi < 0) & T.xunder(c, e2) & pbs2
    if use_wt:
        L &= buy; S &= sell
    L[:150] = S[:150] = False
    a = T.atr_rma(h, l, c, 11)
    r = gsim(df, mm, L, S & ~L, SLL=c - slm * a, TPL=c + tpm * a, SLS=c + slm * a, TPS=c - tpm * a, rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. ABCD Pattern (fractais BW, TP/SL 5:1)")
        for tf in TFS:
            df = cache[tf]
            run_abcd(name, df, mm, f"{tf} ABCD default", rows, est='abcd', TF=tf, cfg='sl1% rr5 ambos')
            for sl, rr, side in itertools.product((0.005, 0.01, 0.02, 0.04), (2.0, 5.0), side2):
                run_abcd(name, df, mm, '', rows, False, sl=sl, rr=rr, short_ok=side == 'ambos', est='abcd', TF=tf,
                         cfg=f'sl{sl:.1%} rr{rr:g} {side}')

        print("\n### 2. HHLL (BB 29 + meia largura, reverse)")
        for tf in TFS:
            df = cache[tf]
            run_hhll(name, df, mm, f"{tf} HHLL default", rows, est='hhll', TF=tf, cfg='29 rev ambos')
            for ln, rv, side in itertools.product((20, 29, 50), (True, False), side2):
                run_hhll(name, df, mm, '', rows, False, ln=ln, reverse=rv, short_ok=side == 'ambos', est='hhll',
                         TF=tf, cfg=f'{ln} ' + ('rev' if rv else 'norm') + f' {side}')

        print("\n### 3. UT Bot v2 (ATR10 x 1)")
        for tf in TFS:
            df = cache[tf]
            run_ut(name, df, mm, f"{tf} UT2 default", rows, est='ut2', TF=tf, cfg='a10 m1 ambos')
            for mu, an, side in itertools.product((1.0, 2.0, 3.0), (10, 20), side2):
                run_ut(name, df, mm, '', rows, False, an=an, mult=mu, short_ok=side == 'ambos', est='ut2', TF=tf,
                       cfg=f'a{an} m{mu:g} {side}')

        print("\n### 4. 3EMA (21x55, TP 3 ATR, SL 2 ATR, saida 9x21, long-only)")
        for tf in TFS:
            df = cache[tf]
            run_3ema(name, df, mm, f"{tf} 3EMA default", rows, est='3ema', TF=tf, cfg='tp3 sl2')
            for tp, sl in itertools.product((0, 3.0, 6.0), (0, 2.0, 4.0)):
                run_3ema(name, df, mm, '', rows, False, tpm=tp, slm=sl, est='3ema', TF=tf, cfg=f'tp{tp:g} sl{sl:g}')

        print("\n### 5. Cipher B+ EMA pullback (WT + MFI + EMA150/50, TP 2 / SL 4 ATR11)")
        for tf in TFS:
            df = cache[tf]
            run_cipher(name, df, mm, f"{tf} CIPHER default", rows, est='cipher', TF=tf, cfg='wt tp2 sl4 ambos')
            for wt, (tp, sl), side in itertools.product((True, False), ((2, 4), (2, 1), (4, 2)), side2):
                run_cipher(name, df, mm, '', rows, False, tpm=tp, slm=sl, use_wt=wt, short_ok=side == 'ambos',
                           est='cipher', TF=tf, cfg=('wt' if wt else 'semwt') + f' tp{tp} sl{sl} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote19')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
