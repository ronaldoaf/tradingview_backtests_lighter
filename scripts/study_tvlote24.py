"""Lote 24 do TradingView (2026-10-23): 20 estrategias nos 5 ativos (ver docs/LOTE24_TV.md).

Ignoradas na ordem da lista: Q5TPHHLs (404), Qullamaggie (5bTajWQM, lookahead_on), BTC 15 min (xGk5K4DE, security
de HMA de 1 minuto), Elder Ray (Cv3YP9Tw, limiar absoluto de -200 no preco), Donchian Breakout (hyYvFjux, o
breakout/Turtle do lote 22), RSI divergence (ASVRhqFM, regressoes e arrays), DNjH5QA9 (security Pine v2), KOfsPM9h
(sessao NSE 09:15-14:45), Death to the Bear (COwM0rKz, piramidacao de 6), CHOP Zone (GrP0zABg, maquina de estados),
Two TP/Two SL (tGTV8MkY, template), Supply/Demand Order Block (lQ5zIOGa), zFPZofwt (662 linhas), hNPuoyrz (404),
Braid filter (ZmsAUj1J, 343 linhas), PowerHouse (xR8aIjgP, lookahead), Kirk65 UTBot (cbPurhXs, o UT Bot do lote
13), Daily Candle Cross (z9AN5ziF, security Pine v2), Trailing Take Profit (W8nc1c3V, template), IK Grid
(IIchZZ2m, grid), backtest time ranges (xAEG4ZJG, exemplo), Fractal [KL] (agyP7x3R, TPs parciais), EmperorBTC VWAP
(wmJ1ovZQ, lookahead), SPY day trader (7zXPSx9G, lookahead), SSL Hybrid (Sso2cdEm, 552 linhas), leverage/margin
(9Iwinz7I, exemplo), 2mars (Y68meyX1, 649 linhas) e TOv4zoTc (security Pine v2).

 1. SOTT (cJhpIJ2w)                               11. Bitcoin Momentum (Tce7SnL7)
 2. BEST Supertrend (6knHPR6c)                    12. Hull Fisher (QTYaYuX7)
 3. Mbit MA (hXrtpUdS)                            13. DEMA 8/20/63 (AbRhwDeX)
 4. Triple EMA + QQE TradeDots (M4y5HT3h)         14. Low-High Trend (o97hSCY4)
 5. SuperTrend Backtester (GMZLB374)              15. Combo 123 Reversal & Statistical Volatility (3w6l57bw)
 6. HMA50 + Supertrend (3SHJZytF)                 16. VWMA/SMA 3Commas (cH5Tjlns)
 7. Stochastic RSI + RVI (22FnhBk9)               17. VWAPStrategy (t1lk7Uvk)
 8. SMC (Zcf69Yqd)                                18. Bullish Engulfing Quant Science (0moOi6G5)
 9. Donchian free bot (KZuFvEYa)                  19. EMA Crossover with TP (B7umqU7W)
10. Gap Filling (ghocsiv7)                        20. AlphaTrend (uvkI3QJC)

uso: python study_tvlote24.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch
from study_tvlote9 import summary
from study_tvlote20 import sh, tr_, _st, supertrend
from study_tvlote21 import G
from study_tvlote22 import mfi, meandev
from study_tvlote23 import vwap_d

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
full = lambda c, v: np.full(len(c), float(v))
ITF = TFS[:-1]


def cci(x, n):
    with np.errstate(divide='ignore', invalid='ignore'):
        return (x - T.sma(x, n)) / (0.015 * meandev(x, n))


def swma(x):
    return (sh(x, 3) + 2 * sh(x, 2) + 2 * sh(x) + x) / 6


def st_line(h, l, c, n, mult):
    t, up, dn = supertrend(h, l, c, n, mult)
    return t, np.where(t == 1, up, dn)


# ------------------------------------------------------------------ 1. SOTT
@njit(cache=True)
def _var(src, n):
    a = 2.0 / (n + 1); m = len(src); out = np.zeros(m)
    for i in range(m):
        ud = 0.0; dd = 0.0
        for k in range(max(1, i - 8), i + 1):
            d = src[k] - src[k - 1]
            if d == d:
                if d > 0: ud += d
                else: dd -= d
        cmo = (ud - dd) / (ud + dd) if ud + dd > 0 else 0.0
        p = out[i - 1] if i else 0.0
        s = src[i] if src[i] == src[i] else p
        out[i] = a * abs(cmo) * s + (1 - a * abs(cmo)) * p
    return out


@njit(cache=True)
def _ott(m, pct):
    n = len(m); ls = np.zeros(n); ss = np.zeros(n); d = 1; ott = np.zeros(n)
    for i in range(n):
        f = m[i] * pct * 0.01; a = m[i] - f; b = m[i] + f
        if i:
            if m[i] > ls[i - 1]: a = max(a, ls[i - 1])
            if m[i] < ss[i - 1]: b = min(b, ss[i - 1])
            if d == -1 and m[i] > ss[i - 1]: d = 1
            elif d == 1 and m[i] < ls[i - 1]: d = -1
        ls[i] = a; ss[i] = b
        mt = a if d == 1 else b
        ott[i] = mt * (200 + pct) / 200 if m[i] > mt else mt * (200 - pct) / 200
    return ott


def run_sott(name, df, mm, tag, rows=None, verbose=True, sl=250, pct=0.618, long_ok=True, short_ok=True, **extra):
    """Estocastico 250 suavizado por VAR (VIDYA com CMO9) de 50 (+1000) cruzando o OTT (VAR 3, 0,618%) de duas
    barras atras; inverte."""
    o, h, l, c = ohlc(df)
    src = _var(np.nan_to_num(stoch(c, h, l, sl), nan=50.0), 50) + 1000
    ott = sh(_ott(_var(src, 3), pct), 2)
    r = G(df, mm, T.xover(src, ott), T.xunder(src, ott), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. BEST Supertrend
def run_best(name, df, mm, tag, rows=None, verbose=True, mult=3.0, long_ok=True, short_ok=True, **extra):
    """SuperTrend diario (3, 3) do dia anterior; regime = SMA7 > SMA20. Compra com close >= linha diaria no regime
    de alta (vende no espelho); sai no cruzamento contrario das medias."""
    o, h, l, c = ohlc(df)
    dd = df.resample('1D').agg({'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    _, ln = st_line(dd.high.to_numpy(float), dd.low.to_numpy(float), dd.close.to_numpy(float), 3, mult)
    stD = pd.Series(ln, dd.index).shift(1).reindex(df.index.normalize()).to_numpy()
    a, b = T.sma(c, 7), T.sma(c, 20)
    L = (c >= stD) & (a > b); S = (c <= stD) & (a < b)
    r = gsim(df, mm, L, S, T.xunder(a, b), T.xover(a, b), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Mbit MA
def run_mbit(name, df, mm, tag, rows=None, verbose=True, ma=520, cnt=27, long_ok=True, short_ok=True, **extra):
    """Contrario: 27 fechamentos seguidos abaixo da SMA520 compra; 27 acima vende; inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, ma)
    def run(b):
        out = np.zeros(len(b)); k = 0
        for i, x in enumerate(b):
            k = k + 1 if x else 0; out[i] = k
        return out
    L = run(c < m) == cnt; S = run(c > m) == cnt
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Triple EMA + QQE
def tema(x, n):
    e1 = ema(x, n); e2 = ema(e1, n); return 3 * e1 - 3 * e2 + ema(e2, n)


@njit(cache=True)
def _qqe_ts(rm, mar, fac):
    n = len(rm); ts = np.zeros(n)
    for i in range(n):
        p = ts[i - 1] if i else 0.0; pr = rm[i - 1] if i else rm[i]
        if rm[i] != rm[i] or mar[i] != mar[i]: ts[i] = rm[i] if rm[i] == rm[i] else 0.0; continue
        if rm[i] > p and pr <= p: v = rm[i] - mar[i] * fac
        elif rm[i] < p and pr >= p: v = rm[i] + mar[i] * fac
        elif rm[i] > p: v = max(rm[i] - mar[i] * fac, p)
        else: v = min(rm[i] + mar[i] * fac, p)
        ts[i] = v
    return ts


def close_stop(c, L, S, p):
    """So entra flat; stop no fechamento a p do close, que so anda a favor; devolve sinais de entrada e saida."""
    n = len(c); EL = np.zeros(n, bool); ES = np.zeros(n, bool); X = np.zeros(n, bool); pos = 0; st = 0.0
    for i in range(n):
        if pos == 1:
            if c[i] < st: X[i] = True; pos = 0; continue
            st = max(st, c[i] * (1 - p))
        elif pos == -1:
            if c[i] > st: X[i] = True; pos = 0; continue
            st = min(st, c[i] * (1 + p))
        elif L[i]: EL[i] = True; pos = 1; st = c[i] * (1 - p)
        elif S[i]: ES[i] = True; pos = -1; st = c[i] * (1 + p)
    return EL, ES, X


def run_tq(name, df, mm, tag, rows=None, verbose=True, p=0.01, long_ok=True, short_ok=True, **extra):
    """c > TEMA20 > TEMA40 com TEMA40 subindo e RSI14 suavizado cruzando acima da linha QQE (4,238), fora de
    segunda-feira, compra (espelho vende); so flat; stop movel no fechamento (120 pips -> p% do preco)."""
    o, h, l, c = ohlc(df)
    t1, t2 = tema(c, 20), tema(c, 40)
    rm = ema(np.nan_to_num(T.rsi_wilder(c, 14), nan=50.0), 5)
    mar = ema(np.abs(rm - sh(rm)), 27); ts = _qqe_ts(rm, mar, 4.238)
    mon = df.index.dayofweek.to_numpy() == 0
    L = (c > t1) & (t1 > t2) & (t2 > sh(t2)) & T.xover(rm, ts) & ~mon
    S = (c < t1) & (t1 < t2) & (t2 < sh(t2)) & T.xunder(rm, ts) & ~mon
    EL, ES, X = close_stop(c, L & long_ok, S & short_ok, p)
    r = gsim(df, mm, EL, ES, X, X, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. SuperTrend Backtester
def run_stb(name, df, mm, tag, rows=None, verbose=True, tp=0.0, long_ok=True, short_ok=True, **extra):
    """SuperTrend (ATR7 x 3) inverte na virada; TP/SL de 100 ticks -> tp% (0 = sem)."""
    o, h, l, c = ohlc(df); t, _ = st_line(h, l, c, 7, 3.0)
    L, S = (t == 1) & (sh(t) == -1), (t == -1) & (sh(t) == 1)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok, slp=tp, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. HMA50 + Supertrend
def run_hst(name, df, mm, tag, rows=None, verbose=True, hl=50, long_ok=True, short_ok=True, **extra):
    """SuperTrend (10, 3) de alta com HMA50 subindo compra; espelho vende; discordando, zera."""
    o, h, l, c = ohlc(df); t, _ = st_line(h, l, c, 10, 3.0); hm = T.hma(c, hl)
    p = np.where((t == 1) & (hm > sh(hm)), 1, np.where((t == -1) & (hm < sh(hm)), -1, 0))
    r = gsim(df, mm, p == 1, p == -1, p != 1, p != -1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. Stochastic RSI + RVI
def run_srvi(name, df, mm, tag, rows=None, verbose=True, per=5, lo=30, long_ok=True, short_ok=True, **extra):
    """StochRSI K >= D abaixo de 30 e RVI cruzando o sinal para cima compra; espelho acima de 70 vende; alterna."""
    o, h, l, c = ohlc(df); r_ = T.rsi_wilder(c, 14)
    K = T.sma(stoch(r_, r_, r_, 14), 3); Dd = T.sma(K, 3)
    with np.errstate(divide='ignore', invalid='ignore'):
        rvi = roll(swma(c - o), per).sum().to_numpy() / roll(swma(h - l), per).sum().to_numpy()
    sg = swma(rvi)
    Up = (K >= Dd) & (K < lo) & (rvi >= sg) & (sh(rvi) <= sh(sg))
    Dn = (K <= Dd) & (K > 100 - lo) & (rvi <= sg) & (sh(rvi) >= sh(sg))
    r = G(df, mm, Up & ~Dn, Dn & ~Up, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. SMC
def run_smc(name, df, mm, tag, rows=None, verbose=True, lb=8, long_ok=True, short_ok=True, **extra):
    """Topo/fundo de swing = maxima/minima da barra que e a maior/menor de 8; abaixo do equilibrio (meio), acima do
    fundo e acima da SMA50 compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df)
    swh = pd.Series(np.where(h >= roll(h, lb).max().to_numpy(), h, NAN)).ffill().to_numpy()
    swl = pd.Series(np.where(l <= roll(l, lb).min().to_numpy(), l, NAN)).ffill().to_numpy()
    eq = (swh + swl) / 2; m = T.sma(c, 50)
    L = (c < eq) & (c > swl) & (c > m); S = (c > eq) & (c < swh) & (c < m)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Donchian free bot
@njit(cache=True)
def _dcf_sim(o, h, l, LE, SE, LX, SX, tp):
    """Stops de entrada armados no fechamento e ativos na barra seguinte, so flat; saida por stop no meio do canal
    (do fechamento anterior) ou alvo tp sobre a entrada, a partir da barra seguinte a entrada (stop primeiro)."""
    n = len(o); pos = 0; i0 = 0; pin = 0.0; k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    for j in range(1, n):
        i = j - 1
        if pos == 1 and j > i0:
            lv = LX[i]; tg = pin * (1 + tp) if tp > 0 else np.nan
            if lv == lv and l[j] <= lv:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], lv); k += 1; pos = 0
            elif tg == tg and h[j] >= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = max(o[j], tg); k += 1; pos = 0
            continue
        if pos == -1 and j > i0:
            lv = SX[i]; tg = pin * (1 - tp) if tp > 0 else np.nan
            if lv == lv and h[j] >= lv:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], lv); k += 1; pos = 0
            elif tg == tg and l[j] <= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = min(o[j], tg); k += 1; pos = 0
            continue
        le = LE[i]; se = SE[i]
        hl = le == le and h[j] >= le; hs = se == se and l[j] <= se
        if hl and hs:
            if max(le - o[j], 0.0) <= max(o[j] - se, 0.0): hs = False
            else: hl = False
        if hl: pos = 1; i0 = j; pin = max(o[j], le)
        elif hs: pos = -1; i0 = j; pin = min(o[j], se)
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_dcf(name, df, mm, tag, rows=None, verbose=True, tp=0.025, short=True, **extra):
    """Stop de compra na maxima de 10 (saida por stop no meio do canal de 10); stop de venda na minima de 20 (saida
    no meio do canal de 20); alvo 2,5%; so entra flat."""
    o, h, l, c = ohlc(df)
    h10, l10 = roll(h, 10).max().to_numpy(), roll(l, 10).min().to_numpy()
    h20, l20 = roll(h, 20).max().to_numpy(), roll(l, 20).min().to_numpy()
    se = l20 if short else full(c, NAN)
    r = _dcf_sim(o, h, l, h10, se, (h10 + l10) / 2, (h20 + l20) / 2, tp)
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 10. Gap Filling
def run_gap(name, df, mm, tag, rows=None, verbose=True, tgt=True, long_ok=True, short_ok=True, **extra):
    """Gap de baixa (abertura abaixo da minima anterior e corpo abaixo do corpo anterior) compra, gap de alta vende;
    alvo na borda do corpo anterior; zera na virada do dia (UTC)."""
    o, h, l, c = ohlc(df)
    bt, bb = np.maximum(c, o), np.minimum(c, o)
    up = (o > sh(h)) & (bb > sh(bt)); dn = (o < sh(l)) & (bt < sh(bb))
    d = df.index.normalize(); ses = np.r_[False, d[1:] != d[:-1]]
    X = np.r_[ses[1:], False]
    kw = dict(TPL=sh(bb), TPS=sh(bt)) if tgt else {}
    r = gsim(df, mm, dn & ~X, up & ~X, X, X, rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Bitcoin Momentum
def run_btcm(name, df, mm, tag, rows=None, verbose=True, am=1.0, **extra):
    """So long: close acima da EMA20 semanal (semana fechada) e sem 'cautela' compra; stop movel = maior minima de 7
    - ATR5 (0,2 ATR em cautela), so sobe; sai com close abaixo do stop ou da EMA semanal."""
    o, h, l, c = ohlc(df)
    wk = df.close.resample('W-SUN').last().dropna()
    we = pd.Series(ema(wk.to_numpy(float), 20), wk.index + pd.Timedelta(days=1))
    htf = we.reindex(df.index.union(we.index)).ffill().reindex(df.index).to_numpy()
    e20 = ema(c, 20); a = T.atr_rma(h, l, c, 5)
    hh7 = roll(h, 7).max().to_numpy(); hl7 = roll(l, 7).max().to_numpy()
    caut = (c > htf) & ((hh7 - l > 1.5 * a) | (c < e20))
    n = len(c); L = np.zeros(n, bool); X = np.zeros(n, bool); pos = False; st = NAN
    for i in range(1, n):
        tv = hl7[i] - (0.2 if caut[i - 1] else am) * a[i]
        if pos:
            st = max(st, tv) if tv == tv else st
            if c[i] < st or c[i] < htf[i]: X[i] = True; pos = False
        elif c[i] > htf[i] and not caut[i]:
            L[i] = True; pos = True; st = tv
    r = gsim(df, mm, L, np.zeros(n, bool), X, None, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Hull Fisher
@njit(cache=True)
def _fisher(x, hi, lo):
    n = len(x); v = 0.0; v1 = np.zeros(n); p1 = 0.0
    for i in range(n):
        if x[i] == x[i] and hi[i] == hi[i]:
            v = 0.66 * ((x[i] - lo[i]) / max(hi[i] - lo[i], 0.001) - 0.5) + 0.67 * v
            v = 0.999 if v > 0.99 else (-0.999 if v < -0.99 else v)
            p1 = 0.5 * np.log((1 + v) / max(1 - v, 0.001)) + 0.5 * p1
        v1[i] = p1
    return v1


def run_hf(name, df, mm, tag, rows=None, verbose=True, per=14, long_ok=True, short_ok=True, **extra):
    """Fisher (9) da HMA14 da abertura: virada para cima abaixo de -5 ou acima de zero, com CCI14 e HMA subindo,
    compra (espelho vende); fecha na virada do Fisher ou da HMA."""
    o, h, l, c = ohlc(df); hm = T.hma(o, per)
    v1 = _fisher(hm, roll(hm, 9).max().to_numpy(), roll(hm, 9).min().to_numpy()); v2 = sh(v1)
    cc = cci(o, per); cu, hu = cc > sh(cc), hm > sh(hm); cd, hd = cc < sh(cc), hm < sh(hm)
    L = (v1 > v2) & ((v1 < -5) | (v1 > 0)) & cu & hu
    S = (v1 < v2) & ((v1 > 5) | (v1 < 0)) & cd & hd
    r = gsim(df, mm, L, S, (v1 < v2) | hd, (v1 > v2) | hu, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. DEMA 8/20/63
def dema(x, n):
    e = ema(x, n); return 2 * e - ema(e, n)


def run_d3(name, df, mm, tag, rows=None, verbose=True, k=1, long_ok=True, short_ok=True, **extra):
    """DEMA8 do ohlc4 acima da DEMA20 da minima e da DEMA63 do close compra; espelho vende (k escala os periodos)."""
    o, h, l, c = ohlc(df)
    d1, d2, d3 = dema((o + h + l + c) / 4, 8 * k), dema(l, 20 * k), dema(c, 63 * k)
    r = G(df, mm, (d1 > d2) & (d1 > d3), (d1 < d2) & (d1 < d3), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Low-High Trend
def run_lht(name, df, mm, tag, rows=None, verbose=True, ext='tp8', **extra):
    """So long: close cruza acima da minima de 20 fechamentos (anterior) acima da EMA200; sai 8% acima da entrada
    (tp8) ou com close abaixo da maxima de 10 fechamentos (hi10)."""
    o, h, l, c = ohlc(df)
    L = T.xover(c, sh(roll(c, 20).min().to_numpy())) & (c > ema(c, 200))
    z = np.zeros(len(c), bool)
    if ext == 'tp8':
        r = gsim(df, mm, L, z, rev=False, short_ok=False, tpp=0.08)
    else:
        r = gsim(df, mm, L, z, T.xunder(c, sh(roll(c, 10).max().to_numpy())), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. 123 Reversal + Statistical Volatility
def run_c123sv(name, df, mm, tag, rows=None, verbose=True, top=0.005, long_ok=True, short_ok=True, **extra):
    """123 Reversal (estocastico 14, nivel 50) e volatilidade estatistica (30 barras, faixa 0,0016-0,005)
    concordando: compra/vende; inverte."""
    o, h, l, c = ohlc(df)
    vf = stoch(c, h, l, 14); vs = T.sma(vf, 3)
    c1, c2 = sh(c), sh(c, 2)
    p1 = np.where((c2 < c1) & (c > c1) & (vf < vs) & (vf > 50), 1.0,
                  np.where((c2 > c1) & (c < c1) & (vf > vs) & (vf < 50), -1.0, NAN))
    p1 = pd.Series(p1).ffill().fillna(0).to_numpy()
    k = np.sqrt(253 / 30)
    mxc, mnc = roll(c, 30).max().to_numpy(), roll(c, 30).min().to_numpy()
    mxh, mnl = roll(h, 30).max().to_numpy(), roll(l, 30).min().to_numpy()
    vol = np.clip(((0.6 * np.log(mxc / mnc) * k) + (0.6 * np.log(mxh / mnl) * k)) * 0.5, 0, 2.99)
    p2 = pd.Series(np.where(vol > top, 1.0, np.where(vol < 0.0016, -1.0, NAN))).ffill().fillna(0).to_numpy()
    r = G(df, mm, (p1 == 1) & (p2 == 1), (p1 == -1) & (p2 == -1), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. VWMA/SMA 3Commas
def run_vws(name, df, mm, tag, rows=None, verbose=True, lv=True, long_ok=True, short_ok=True, **extra):
    """VWMA13 x SMA13 inverte; saida por TP/SL (close +- ATR21 x 1 / 1,5, fixados nos cruzamentos de 26) ou pelo
    estocastico (14, 6, 3) cruzando na zona de 80/20."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    def vwma(n):
        with np.errstate(divide='ignore', invalid='ignore'):
            return roll(c * v, n).sum().to_numpy() / roll(v, n).sum().to_numpy()
    f1, f2, s1, s2 = vwma(13), T.sma(c, 13), vwma(26), T.sma(c, 26)
    a = T.atr_rma(h, l, c, 21); su, sd = T.xover(s1, s2), T.xunder(s1, s2)
    ff = lambda m, x: pd.Series(np.where(m, x, NAN)).ffill().to_numpy()
    k = T.sma(stoch(c, h, l, 14), 6); d = T.sma(k, 3); av = (k + d) / 2
    XL = T.xunder(k, d) & (av >= 80); XS = T.xover(k, d) & (av <= 20)
    if lv:
        with np.errstate(invalid='ignore'):
            XL = XL | (h > ff(su, c + a)) | (l < ff(su, c - 1.5 * a))
            XS = XS | (l < ff(sd, c - a)) | (h > ff(sd, c + 1.5 * a))
    r = gsim(df, mm, T.xover(f1, f2), T.xunder(f1, f2), XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. VWAP
def run_vwap(name, df, mm, tag, rows=None, verbose=True, ln=3, long_ok=True, short_ok=True, **extra):
    """SMA3 cruza a VWAP diaria; inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, ln); vw = vwap_d(df)
    r = G(df, mm, T.xover(m, vw), T.xunder(m, vw), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. Bullish Engulfing
def run_beng(name, df, mm, tag, rows=None, verbose=True, sl=0.0667, tp=0.0667, trend=True, **extra):
    """So long: engolfo de alta (corpo longo branco engolindo corpo curto preto, corpo vs EMA14) em tendencia de
    baixa (close < SMA50); TP/SL de 2% do capital com 30% de posicao = 6,67% do preco."""
    o, h, l, c = ohlc(df); b = np.abs(c - o); ba = ema(b, 14)
    L = (c > o) & (b > ba) & (sh(c) < sh(o)) & (sh(b) < sh(ba)) & (c >= sh(o)) & (o <= sh(c))
    if trend: L = L & (c < T.sma(c, 50))
    r = gsim(df, mm, L, np.zeros(len(c), bool), rev=False, short_ok=False, slp=sl, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. EMA Crossover with TP
@njit(cache=True)
def _rst_sim(o, h, l, L, S, TP, STL, STS):
    """A mercado na abertura seguinte; alvo TP (da barra do sinal) e stop recolocado a cada fechamento (sem
    catraca, inclusive para a barra da entrada); stop antes do alvo; sinal contrario inverte."""
    n = len(o); pos = 0; pend = 0; i0 = 0; pin = 0.0; tg = np.nan; k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    for j in range(1, n):
        i = j - 1
        if pend != 0:
            if pos != 0:
                EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = pin; PO[k] = o[j]; k += 1
            pos = pend; i0 = j; pin = o[j]; tg = TP[i]; pend = 0
        if pos == 1:
            st = STL[i]
            if st == st and l[j] <= st:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], st); k += 1; pos = 0
            elif tg == tg and h[j] >= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = max(o[j], tg); k += 1; pos = 0
        elif pos == -1:
            st = STS[i]
            if st == st and h[j] >= st:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], st); k += 1; pos = 0
            elif tg == tg and l[j] <= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = min(o[j], tg); k += 1; pos = 0
        if L[j] and pos != 1: pend = 1
        elif S[j] and pos != -1: pend = -1
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_ectp(name, df, mm, tag, rows=None, verbose=True, sl=0.03, tpk=0.5, long_ok=True, short_ok=True, **extra):
    """EMA20 x EMA50 inverte; alvo = maxima + 0,5 x range da barra do sinal (minima - 0,5 x range no short); stop
    a 3% do close recolocado a cada barra."""
    o, h, l, c = ohlc(df); a, b = ema(c, 20), ema(c, 50)
    L, S = T.xover(a, b) & long_ok, T.xunder(a, b) & short_ok
    rg = h - l; tp = np.where(L, h + tpk * rg, l - tpk * rg) if tpk else full(c, NAN)
    r = _rst_sim(o, h, l, L, S, tp, c * (1 - sl), c * (1 + sl))
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 20. AlphaTrend
@njit(cache=True)
def _alpha(up, dn, bull):
    n = len(up); at = np.zeros(n)
    for i in range(n):
        p = at[i - 1] if i else 0.0
        if bull[i]: at[i] = p if up[i] < p or up[i] != up[i] else up[i]
        else: at[i] = p if dn[i] > p or dn[i] != dn[i] else dn[i]
    return at


def run_alpha(name, df, mm, tag, rows=None, verbose=True, mf=True, long_ok=True, short_ok=True, **extra):
    """AlphaTrend (ATR SMA14 x 1, MFI14 >= 50; rsi = RSI14 no lugar do MFI) cruzando a si mesmo de 2 barras atras;
    alterna/inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    a = T.sma(tr_(h, l, c), 14)
    osc = mfi(h, l, c, v, 14) if mf else T.rsi_wilder(c, 14)
    at = _alpha(l - a, h + a, np.nan_to_num(osc) >= 50)
    r = G(df, mm, T.xover(at, sh(at, 2)), T.xunder(at, sh(at, 2)), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')
        sk = lambda s: dict(short_ok=s == 'ambos')

        def grid(est, fn, label, tfs, default_cfg, combos):
            print(f"\n### {label}", flush=True)
            for tf in tfs:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)

        grid('sott', run_sott, "1. SOTT", TFS, 's250 p0.618 ambos',
             [(f's{a} p{p:g} {s}', dict(sl=a, pct=p, **sk(s))) for a, p, s in itertools.product((250, 50), (0.618, 2.0), side2)])
        grid('best', run_best, "2. BEST Supertrend", TFS, 'm3 ambos',
             [(f'm{m:g} {s}', dict(mult=m, **sk(s))) for m, s in itertools.product((3.0, 1.5), side2)])
        grid('mbit', run_mbit, "3. Mbit MA (contrario)", TFS, 'ma520 n27 ambos',
             [(f'ma{a} n{b} {s}', dict(ma=a, cnt=b, **sk(s))) for a, b, s in itertools.product((520, 200), (27, 10), side2)])
        grid('tq', run_tq, "4. Triple EMA + QQE", TFS, 'p1% ambos',
             [(f'p{p:.0%} {s}', dict(p=p, **sk(s))) for p, s in itertools.product((0.01, 0.03), side2)])
        grid('stb', run_stb, "5. SuperTrend Backtester", TFS, 'semtp ambos',
             [((f'tp{tp:.0%}' if tp else 'semtp') + f' {s}', dict(tp=tp, **sk(s))) for tp, s in itertools.product((0.0, 0.01, 0.03), side2)])
        grid('hst', run_hst, "6. HMA50 + Supertrend", TFS, 'h50 ambos',
             [(f'h{a} {s}', dict(hl=a, **sk(s))) for a, s in itertools.product((50, 100), side2)])
        grid('srvi', run_srvi, "7. Stochastic RSI + RVI", TFS, 'p5 30/70 ambos',
             [(f'p{p} {a}/{100 - a} {s}', dict(per=p, lo=a, **sk(s))) for p, a, s in itertools.product((5, 10), (30, 50), side2)])
        grid('smc', run_smc, "8. SMC", TFS, 'lb8 ambos',
             [(f'lb{a} {s}', dict(lb=a, **sk(s))) for a, s in itertools.product((8, 30), side2)])
        grid('dcf', run_dcf, "9. Donchian free bot", TFS, 'tp2.5% ambos',
             [((f'tp{tp:.1%}' if tp else 'semtp') + (' ambos' if s else ' long'), dict(tp=tp, short=s))
              for tp, s in itertools.product((0.025, 0.0), (True, False))])
        grid('gap', run_gap, "10. Gap Filling", ITF, 'alvo ambos',
             [(('alvo ' if t else 'semalvo ') + s, dict(tgt=t, **sk(s))) for t, s in itertools.product((True, False), side2)])
        grid('btcm', run_btcm, "11. Bitcoin Momentum (long-only)", TFS, 'atr1',
             [(f'atr{a:g}', dict(am=a)) for a in (1.0, 2.0, 3.0)])
        grid('hf', run_hf, "12. Hull Fisher", TFS, 'h14 ambos',
             [(f'h{a} {s}', dict(per=a, **sk(s))) for a, s in itertools.product((14, 50), side2)])
        grid('d3', run_d3, "13. DEMA 8/20/63", TFS, 'x1 ambos',
             [(f'x{k} {s}', dict(k=k, **sk(s))) for k, s in itertools.product((1, 3), side2)])
        grid('lht', run_lht, "14. Low-High Trend (long-only)", TFS, 'tp8',
             [(e, dict(ext=e)) for e in ('tp8', 'hi10')])
        grid('c123sv', run_c123sv, "15. 123 Reversal + Statistical Volatility", TFS, 'top0.005 ambos',
             [(f'top{t:g} {s}', dict(top=t, **sk(s))) for t, s in itertools.product((0.005, 0.3), side2)])
        grid('vws', run_vws, "16. VWMA/SMA 3Commas", TFS, 'niveis ambos',
             [(('niveis ' if v else 'semniveis ') + s, dict(lv=v, **sk(s))) for v, s in itertools.product((True, False), side2)])
        grid('vwap', run_vwap, "17. VWAPStrategy", ITF, 'sma3 ambos',
             [(f'sma{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((3, 20), side2)])
        grid('beng', run_beng, "18. Bullish Engulfing (long-only)", TFS, 'sl6.67 tp6.67 tend',
             [(f'sl{a:.2%} tp{b:.2%} ' + ('tend' if t else 'semtend'), dict(sl=a, tp=b, trend=t))
              for (a, b), t in itertools.product(((0.0667, 0.0667), (0.02, 0.02)), (True, False))])
        grid('ectp', run_ectp, "19. EMA Crossover with TP", TFS, 'sl3% tp0.5 ambos',
             [(f'sl{a:.0%} ' + (f'tp{k:g}' if k else 'semtp') + f' {s}', dict(sl=a, tpk=k, **sk(s)))
              for a, k, s in itertools.product((0.03, 0.06), (0.5, 0.0), side2)])
        grid('alpha', run_alpha, "20. AlphaTrend", TFS, 'mfi ambos',
             [(('mfi ' if m else 'rsi ') + s, dict(mf=m, **sk(s))) for m, s in itertools.product((True, False), side2)])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote24')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
