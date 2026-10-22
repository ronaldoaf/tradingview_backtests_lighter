"""Lote 16 do TradingView (2026-10-22): 5 estrategias nos 5 ativos (ver docs/LOTE16_TV.md).

Ignorados (templates/utilitarios): DCA Bot Long/Short (LTcMeU50, emulador de robo DCA do 3commas),
Ultimate Strategy Template (XIJrNXQc), Strategy Designer (Hp05f5Dq, montador de estrategias) e Stepped
trailing strategy example (jjhUHcje).

  1. [Backtest] QQE Cross v6.0 (H0TR67ED, Pine v3)
     RSI14 suavizado (EMA8) e banda QQE (fator 5). Padrao: compra quando o RSI suavizado passa de 60
     (sinal "XC") com filtro de direcao (EMA21 e EMA84 subindo, close > EMA21), avaliado na barra
     anterior; fecha quando a banda QQE cruza o RSI para baixo ou o RSI fica < 50 ("XQ"). Short no
     espelho. Uma posicao por vez (maquina de estados do script).
  2. Profit Maximizer (PMax) Strategy (7yn5dteO, Pine v4)
     PMax = stop ATR(10)x3 sobre a media VAR(12) do hl2. Long: VAR cruza o PMax para cima, MACD (SMA
     12/26, sinal 9) > 0, PSAR (0,02/0,03/0,3) de alta e CCI20 >= 0. Short no espelho. Stop 1%, alvo 35%.
  3. AI Volume SuperTrend (eaTIyEty, Pine v5)
     SuperTrend (10, 3) sobre a WMA ponderada por volume. O "KNN" consulta o proprio ponto atual
     (distancia 0, peso 1e6), entao o rotulo vira WMA20(close) > WMA100(SuperTrend). Long quando o
     rotulo vira 1 ou o SuperTrend vira para cima com rotulo 1. Sai quando a tendencia nao continua e
     o close perde o trailing (SuperTrend - 3 x ATR). Short no espelho.
  4. EMA Cross Strategy (fAxX6kbm, Pine v4)
     EMA10 x EMA20; o cruzamento inverte a posicao.
  5. EDMA Scalping Strategy (CJesxF5m, Pine v5)
     EDMA = HMA do "expoente" alto/baixo do preco (fonte: high se close > open, senao low, com SWMA);
     compra quando a EMA20 da fonte passa acima da EDMA(20), vende quando passa abaixo (sinal "forte").
     Filtro Chikou desligado por padrao.

uso: python study_tvlote16.py xau us100 wti btc eth
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
from study_tvlote10 import shift, psar_up

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)


def rising(x, n):
    """ta.rising(x, n): x maior que todos os n valores anteriores."""
    out = np.ones(len(x), bool)
    for k in range(1, n + 1):
        out &= x > shift(x, k)
    return out


def falling(x, n):
    out = np.ones(len(x), bool)
    for k in range(1, n + 1):
        out &= x < shift(x, k)
    return out


# ------------------------------------------------------------------ 1. QQE Cross
def qqe(c, rl=14, sf=8, fac=5.0):
    rsi = T.rsi_wilder(c, rl); ri = ema(np.nan_to_num(rsi, nan=50), sf)
    wp = rl * 2 - 1
    d = ema(ema(np.abs(ri - shift(ri, 1)), wp), wp) * fac
    d = np.nan_to_num(d)
    n = len(c); lb = np.zeros(n); sb = np.zeros(n); tr = np.ones(n, int)
    for i in range(1, n):
        nl, ns = ri[i] - d[i], ri[i] + d[i]
        lb[i] = max(lb[i - 1], nl) if ri[i - 1] > lb[i - 1] and ri[i] > lb[i - 1] else nl
        sb[i] = min(sb[i - 1], ns) if ri[i - 1] < sb[i - 1] and ri[i] < sb[i - 1] else ns
        crs = (ri[i] - sb[i - 1]) * (ri[i - 1] - sb[i - 2] if i > 1 else 0) < 0
        crl = (lb[i - 1] - ri[i]) * ((lb[i - 2] if i > 1 else 0) - ri[i - 1]) < 0
        tr[i] = 1 if crs else (-1 if crl else tr[i - 1])
    tl = np.where(tr == 1, lb, sb)
    return ri, tl


def first_run(cond):
    """Contador '== 1' do script: True so na primeira barra de uma sequencia."""
    cond = np.asarray(cond, bool)
    return cond & ~np.concatenate([[False], cond[:-1]])


def run_qqe(name, df, mm, tag, rows=None, verbose=True, fac=5.0, thr=10, anchor=4, dfilter=True, sig='XC',
            long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    ri, tl = qqe(c, 14, 8, fac)
    ma_f, ma_m = ema(c, 16), ema(c, 21)
    xl, xs = first_run(tl < ri), first_run(tl > ri)
    cl, cs = first_run(ri > 50 + thr), first_run(ri < 50 - thr)
    zl, zs = ri >= 50, ri < 50
    if dfilter:
        if anchor > 1:
            ma_alt = ema(c, 21 * anchor)
            fl = rising(ma_m, 3) & rising(ma_alt, 3) & (c > ma_m)
            fs = falling(ma_m, 3) & falling(ma_alt, 3) & (c < ma_m)
        else:
            fl, fs = rising(ma_m, 3), falling(ma_m, 3)
    else:
        fl = fs = np.ones(len(c), bool)
    xf = (ri > 50 + thr) | (ri < 50 - thr)
    if sig == 'XC':
        bl, bs = cl, cs
    elif sig == 'XQ':
        bl, bs = xl & xf, xs & xf
    else:
        bl, bs = first_run(zl), first_run(zs)
    buy = first_run(np.nan_to_num(shift((bl & fl).astype(float), 1)) == 1)
    sell = first_run(np.nan_to_num(shift((bs & fs).astype(float), 1)) == 1)
    if sig == 'XQ':
        XL, XS = xs, xl
    else:
        XL, XS = xs | zs | cs, xl | zl | cl
    r = gsim(df, mm, buy, sell, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. PMax
def var_ma(src, length):
    a = 2 / (length + 1)
    d = np.diff(src, prepend=src[0])
    ud = roll(np.where(d > 0, d, 0), 9).sum().to_numpy(); dd = roll(np.where(d < 0, -d, 0), 9).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        cmo = np.nan_to_num((ud - dd) / (ud + dd))
    v = np.zeros(len(src))
    for i in range(len(src)):
        k = a * abs(cmo[i]); v[i] = k * src[i] + (1 - k) * (v[i - 1] if i else 0.0)
    return v


def pmax(h, l, c, length=12, per=10, mult=3.0):
    src = (h + l) / 2; ma = var_ma(src, length)
    atr = np.nan_to_num(T.atr_rma(h, l, c, per))
    n = len(c); ls = ma - mult * atr; ss = ma + mult * atr; d = np.ones(n); pm = np.zeros(n)
    for i in range(n):
        lp = ls[i - 1] if i else ls[i]; sp = ss[i - 1] if i else ss[i]
        if ma[i] > lp: ls[i] = max(ls[i], lp)
        if ma[i] < sp: ss[i] = min(ss[i], sp)
        dd = d[i - 1] if i else 1
        if dd == -1 and ma[i] > sp: dd = 1
        elif dd == 1 and ma[i] < lp: dd = -1
        d[i] = dd; pm[i] = ls[i] if dd == 1 else ss[i]
    return ma, pm


def cci(c, h, l, n):
    """ta.cci(close, n): (x - SMA) / (0.015 * desvio medio absoluto)."""
    w = np.lib.stride_tricks.sliding_window_view(c, n)
    m = w.mean(axis=1); md = np.abs(w - m[:, None]).mean(axis=1)
    out = np.full(len(c), NAN)
    with np.errstate(divide='ignore', invalid='ignore'):
        out[n - 1:] = (c[n - 1:] - m) / (0.015 * md)
    return out


def run_pmax(name, df, mm, tag, rows=None, verbose=True, sl=0.01, tp=0.35, filtros=True, long_ok=True,
             short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    ma, pm = pmax(h, l, c)
    L = T.xover(ma, pm); S = T.xunder(ma, pm)
    if filtros:
        macd = T.sma(c, 12) - T.sma(c, 26); hist = macd - ema(np.nan_to_num(macd), 9)
        up = psar_up(h, l, c, 0.02, 0.03, 0.3); cc = cci(c, h, l, 20)
        L &= (hist > 0) & up & (cc >= 0); S &= (hist < 0) & ~up & (cc < 0)
    r = gsim(df, mm, L, S, slp=sl, tpp=tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. AI Volume SuperTrend
def run_aivst(name, df, mm, tag, rows=None, verbose=True, ln=10, fac=3.0, plen=20, stlen=100, long_ok=True,
              short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        vw = T.wma(c * v, ln) / T.wma(v, ln)
    vw = np.where(np.isfinite(vw), vw, c)
    atr = T.atr_rma(h, l, c, ln); a0 = np.nan_to_num(atr)
    n = len(c); ub = vw + fac * a0; lb = vw - fac * a0; d = np.ones(n); st = np.zeros(n)
    for i in range(n):
        if i:
            if not (lb[i] > lb[i - 1] or c[i - 1] < lb[i - 1]): lb[i] = lb[i - 1]
            if not (ub[i] < ub[i - 1] or c[i - 1] > ub[i - 1]): ub[i] = ub[i - 1]
        if i == 0 or np.isnan(atr[i - 1]):
            d[i] = 1
        elif st[i - 1] == ub[i - 1]:
            d[i] = -1 if c[i] > ub[i] else 1
        else:
            d[i] = 1 if c[i] < lb[i] else -1
        st[i] = lb[i] if d[i] == -1 else ub[i]
    lab = (T.wma(c, plen) > T.wma(st, stlen)).astype(int)
    lp = np.concatenate([[0], lab[:-1]]); dp = np.concatenate([[1], d[:-1]])
    L = ((lab == 1) & (lp != 1)) | ((d == -1) & (dp == 1) & (lab == 1))
    S = ((lab == 0) & (lp != 0)) | ((d == 1) & (dp == -1) & (lab == 0))
    cont_l = (d == -1) & (lab == 1); cont_s = (d == 1) & (lab == 0)
    ex = ~cont_l & ~cont_s
    XL = ex & (c < st - fac * a0); XS = ex & (c > st + fac * a0)
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. EMA Cross
def run_emax(name, df, mm, tag, rows=None, verbose=True, f=10, s=20, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    a, b = ema(c, f), ema(c, s)
    L, S = T.xover(a, b), T.xunder(a, b)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. EDMA
def swma(x):
    return (shift(x, 3) + 2 * shift(x, 2) + 2 * shift(x, 1) + x) / 6


def edma(src, ln):
    n = len(src); he = np.empty(n); le = np.empty(n); a = 1 / (ln + 1)
    he[0] = src[0]; le[0] = he[0]
    for i in range(1, n):
        s = src[i]
        he[i] = s if s >= he[i - 1] else he[i - 1] + (s - he[i - 1]) * a
        le[i] = he[i] if s <= le[i - 1] else le[i - 1] + (s - le[i - 1]) * a
    hl = int(ln / 1.5)
    return T.wma(2 * T.wma(le, max(1, int(hl / 2))) - T.wma(le, hl), int(round(np.sqrt(hl))))


def run_edma(name, df, mm, tag, rows=None, verbose=True, ln=20, e1=20, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    src = np.nan_to_num(swma(np.where(c > o, h, l)), nan=c[0])
    ed = swma(edma(src, ln)); e = ema(src, e1)
    L, S = T.xover(e, ed), T.xunder(e, ed)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. QQE Cross v6.0 (XC, fecha XQ, filtro de direcao)")
        for tf in TFS:
            df = cache[tf]
            run_qqe(name, df, mm, f"{tf} QQE default", rows, est='qqe', TF=tf, cfg='XC f5 dfil ambos')
            for sg, dfl, side in itertools.product(('XC', 'XQ', 'XZ'), (True, False), side2):
                run_qqe(name, df, mm, '', rows, False, sig=sg, dfilter=dfl, short_ok=side == 'ambos', est='qqe', TF=tf,
                        cfg=f'{sg} f5 ' + ('dfil' if dfl else 'semfil') + f' {side}')

        print("\n### 2. PMax (VAR12, ATR10x3, MACD/PSAR/CCI, SL1% TP35%)")
        for tf in TFS:
            df = cache[tf]
            run_pmax(name, df, mm, f"{tf} PMAX default", rows, est='pmax', TF=tf, cfg='sl1% tp35% filtros ambos')
            for sl, fl, side in itertools.product((0.01, 0.03, 0.0), (True, False), side2):
                run_pmax(name, df, mm, '', rows, False, sl=sl, filtros=fl, short_ok=side == 'ambos', est='pmax', TF=tf,
                         cfg=f'sl{sl:.0%} tp35% ' + ('filtros' if fl else 'sofiltro0') + f' {side}')

        print("\n### 3. AI Volume SuperTrend (10, 3; rotulo WMA20 vs WMA100 do ST)")
        for tf in TFS:
            df = cache[tf]
            run_aivst(name, df, mm, f"{tf} AIVST default", rows, est='aivst', TF=tf, cfg='l10 f3 ambos')
            for ln, fc, side in itertools.product((10, 20), (2.0, 3.0, 5.0), side2):
                run_aivst(name, df, mm, '', rows, False, ln=ln, fac=fc, short_ok=side == 'ambos', est='aivst', TF=tf,
                          cfg=f'l{ln} f{fc:g} {side}')

        print("\n### 4. EMA Cross 10/20")
        for tf in TFS:
            df = cache[tf]
            run_emax(name, df, mm, f"{tf} EMAX default", rows, est='emax', TF=tf, cfg='10/20 ambos')
            for (f, s), side in itertools.product(((10, 20), (20, 50), (50, 200)), side2):
                run_emax(name, df, mm, '', rows, False, f=f, s=s, short_ok=side == 'ambos', est='emax', TF=tf,
                         cfg=f'{f}/{s} {side}')

        print("\n### 5. EDMA Scalping (EMA20 x EDMA20)")
        for tf in TFS:
            df = cache[tf]
            run_edma(name, df, mm, f"{tf} EDMA default", rows, est='edma', TF=tf, cfg='l20 e20 ambos')
            for ln, e1, side in itertools.product((20, 50), (20, 40), side2):
                run_edma(name, df, mm, '', rows, False, ln=ln, e1=e1, short_ok=side == 'ambos', est='edma', TF=tf,
                         cfg=f'l{ln} e{e1} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote16')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
