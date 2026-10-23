"""Lote 20 do TradingView (2026-10-23): 20 estrategias nos 5 ativos (ver docs/LOTE20_TV.md).

Ignoradas na ordem da lista: The Always Winning Holy Grail (aStSXzDa, exemplo: compra sempre),
d0FZtMLp (404), ORB Heikin Ashi SPY Correlation (QpJvYDzb, depende do SPY), Super Z (NIGCEUME,
security diario com lookahead_on sem [1] = olha o futuro), ICT Entry V1 (mVdZBLJ7, 1.282 linhas de
FVG/iFVG com ordens limite, nao reproduzivel com fidelidade), Trailing TP/SL (V7IfK3mr, template de
saidas) e FreedX Grid (4J80gPhd, grade com niveis manuais).

 1. Keltner Channel ETH 1H (ezSBm5MS)        11. Bill Williams Alligator HA (b2ShO5Fv)
 2. ATR Trailing Stop by ceyhun (cj3MJWNz)   12. Camarilla H4/L4 breakout (tBJNISwj)
 3. 3C QFL Mean reversal (SDRM0bBY)          13. Nadaraya-Watson Envelope (HrZicISx)
 4. Follow Line MTF (6lhyIPGA)               14. Extreme Scalping (qVTgdPBT)
 5. MACD + trailing ATR stop (2jDHQAJc)      15. Y-PMax (6ZFa2t7o)
 6. 3x SuperTrend Mel0nTek (FUnOi1Nx)        16. PMARP + Madrid MA Ribbon (T4rBZCvC)
 7. RSI-Adaptive T3 & SAR (bldXp6gY)         17. ATR GOD (Je04kGO0)
 8. Moving Regression Band Breakout (Tls8Y2hc) 18. [DS] Entry_Exit EMA8 x DEMA34 (RO4rB2HF)
 9. Double AI Super Trend (hLZPT7it)         19. FRAMA strategy (y81orwSC)
10. RSI and ATR Trend Reversal (hZLgJ29l)    20. World Cycle ATH/ATL (824WmIi7)

Simplificacoes estao no docstring de cada funcao e em docs/LOTE20_TV.md.
uso: python study_tvlote20.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch
from study_tvlote9 import summary
from study_tvlote10 import psar_up

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
Z = lambda x: np.zeros(len(x), bool)


def sh(x, k=1):
    x = np.asarray(x, float)
    return np.concatenate([np.full(k, NAN), x[:-k]])


def tr_(h, l, c):
    pc = sh(c)
    return np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)


def rma(x, n):
    return T.rma_nan(np.asarray(x, float), n)


def heikin(o, h, l, c):
    hc = (o + h + l + c) / 4; ho = np.empty(len(c)); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(c)):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    return ho, np.maximum(h, np.maximum(ho, hc)), np.minimum(l, np.minimum(ho, hc)), hc


@njit(cache=True)
def _trail(src, slv):
    """ATR trailing stop do UT Bot / ceyhun / MOST."""
    n = len(src); t = np.zeros(n); p = 0.0
    for i in range(n):
        v = slv[i] if slv[i] == slv[i] else 0.0
        s1 = src[i - 1] if i else src[i]
        if src[i] > p and s1 > p: t[i] = max(p, src[i] - v)
        elif src[i] < p and s1 < p: t[i] = min(p, src[i] + v)
        elif src[i] > p: t[i] = src[i] - v
        else: t[i] = src[i] + v
        p = t[i]
    return t


@njit(cache=True)
def _st(src, c, a, mult):
    """SuperTrend classico (KivancOzbilgic): devolve trend (+1/-1), linha de alta e de baixa."""
    n = len(c); up = np.zeros(n); dn = np.zeros(n); tr = np.ones(n)
    for i in range(n):
        av = a[i] if a[i] == a[i] else 0.0
        u = src[i] - mult * av; d = src[i] + mult * av
        if i:
            u1, d1 = up[i - 1], dn[i - 1]
            if c[i - 1] > u1: u = max(u, u1)
            if c[i - 1] < d1: d = min(d, d1)
            t = tr[i - 1]
            if t == -1 and c[i] > d1: t = 1
            elif t == 1 and c[i] < u1: t = -1
            tr[i] = t
        up[i], dn[i] = u, d
    return tr, up, dn


def supertrend(h, l, c, n, mult, src=None):
    return _st((h + l) / 2 if src is None else src, c, T.atr_rma(h, l, c, n), mult)


def flips(pos):
    prev = np.concatenate([[0], pos[:-1]])
    return (pos == 1) & (prev != 1), (pos == -1) & (prev != -1)


# ------------------------------------------------------------------ 1. Keltner
def run_kelt(name, df, mm, tag, rows=None, verbose=True, ln=81, mult=2.5, bench=27, tp=0.20, sl=0.04, trend=True,
             **extra):
    """Long-only. EMA46 > SMA46; open dentro do canal SMA81 +- 2,5 x SMA(TR) e close acima da banda de cima,
    DI+(19) > DI- e DI+ > 27. Sai com close < banda de baixo, SL 4%, TP 20% (o TP1 parcial de 15% em 4,5%
    foi ignorado)."""
    o, h, l, c = ohlc(df)
    ma = T.sma(c, ln); rg = T.sma(tr_(h, l, c), ln)
    up, lo = ma + mult * rg, ma - mult * rg
    p, m, _ = __import__('study_tvlote8').dmi(h, l, c, 19)
    L = (o < up) & (o > lo) & (c > up) & (p > m) & (p > bench)
    if trend:
        L &= ema(c, 46) > T.sma(c, 46)
    r = gsim(df, mm, L, Z(L), c < lo, None, slp=sl, tpp=tp, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. ceyhun ATR trailing
def run_ceyhun(name, df, mm, tag, rows=None, verbose=True, a1=5, m1=0.5, a2=10, m2=3.0, long_ok=True, short_ok=True,
               **extra):
    """Trailing rapido (ATR5 x 0,5) cruza o lento (ATR10 x 3): compra/vende, inverte."""
    o, h, l, c = ohlc(df)
    t1 = _trail(c, m1 * T.atr_rma(h, l, c, a1)); t2 = _trail(c, m2 * T.atr_rma(h, l, c, a2))
    L, S = T.xover(t1, t2), T.xunder(t1, t2); L[:a2] = S[:a2] = False
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. QFL
def run_qfl(name, df, mm, tag, rows=None, verbose=True, pct=0.005, tp=0.01, sl=0.0, maxage=10, **extra):
    """Long-only. Base = ultimo fractal de baixa com volume (low[3] minimo de 5 velas e volume[3] > SMA60), lida
    com [1] (o lookahead_on do script e o idioma sem repaint). Compra quando close < base x (1 - 0,5%) e a
    base de cima mudou ha menos de 10 barras (o script usa a idade da base de cima). TP 1%. As ordens de
    seguranca (DCA com escala 2x) nao foram reproduzidas: uma entrada so, com stop opcional."""
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float); vam = T.sma(v, 60)
    dn = (sh(l, 3) < sh(l, 4)) & (sh(l, 4) < sh(l, 5)) & (sh(l, 2) > sh(l, 3)) & (sh(l, 1) > sh(l, 2)) & (sh(v, 3) > sh(vam, 3))
    upf = (sh(h, 3) > sh(h, 4)) & (sh(h, 4) > sh(h, 5)) & (sh(h, 2) < sh(h, 3)) & (sh(h, 1) < sh(h, 2)) & (sh(v, 3) > sh(vam, 3))
    fd = pd.Series(np.where(dn, sh(l, 3), NAN)).ffill().fillna(0).to_numpy()
    fu = pd.Series(np.where(upf, sh(h, 3), NAN)).ffill().fillna(0).to_numpy()
    fd, fu = sh(fd), sh(fu)
    age = T.barssince(fu != sh(fu))
    agecond = (age < maxage) if maxage else np.ones(len(c), bool)
    with np.errstate(invalid='ignore', divide='ignore'):
        buy = (c / fd < 1 - pct) & agecond & (fd > 0)
    L = buy & (~np.concatenate([[False], buy[:-1]]) | (fd != sh(fd)))
    r = gsim(df, mm, L, Z(L), slp=sl, tpp=tp, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Follow Line
def run_fline(name, df, mm, tag, rows=None, verbose=True, ln=21, dev=1.0, ap=5, long_ok=True, short_ok=True, **extra):
    """TF do proprio grafico (UCCR=true). EMA21 +- 1 desvio do close; close acima da banda: linha = low - ATR5
    (so sobe); abaixo: high + ATR5 (so desce). Virada da linha compra/vende e inverte."""
    o, h, l, c = ohlc(df)
    ma = ema(c, ln); sd = roll(c, ln).std(ddof=0).to_numpy()
    bs = np.where(c > ma + dev * sd, 1, np.where(c < ma - dev * sd, -1, 0))
    a = T.atr_rma(h, l, c, ap); n = len(c)
    tl = np.zeros(n); it = np.zeros(n)
    for i in range(1, n):
        t = tl[i - 1]
        if bs[i] == 1:
            t = max(l[i] - a[i], tl[i - 1]) if a[i] == a[i] else t
        elif bs[i] == -1:
            t = min(h[i] + a[i], tl[i - 1]) if a[i] == a[i] else t
        tl[i] = t
        it[i] = 1 if t > tl[i - 1] else (-1 if t < tl[i - 1] else it[i - 1])
    L, S = flips(it)
    L[:ln] = S[:ln] = False
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. MACD + trailing ATR
def run_macd(name, df, mm, tag, rows=None, verbose=True, mult=2.2, tp=0.0, filt=True, **extra):
    """Long-only. MACD 3/5 (EMA) com sinal SMA2; compra no cruzamento para cima com SMA34 < EMA34. Sai quando
    close < (close do ultimo sinal) - 2,2 x ATR17. Os TPs parciais (10% em 1%, 50% em 5%) viraram o TP
    opcional da grade."""
    o, h, l, c = ohlc(df)
    mac = ema(c, 3) - ema(c, 5); sg = T.sma(mac, 2)
    L = T.xover(mac, sg)
    if filt:
        L &= T.sma(c, 34) < ema(c, 34)
    L[:34] = False
    ep = pd.Series(np.where(L, c, NAN)).ffill().to_numpy()
    X = c < ep - mult * T.atr_rma(h, l, c, 17)
    r = gsim(df, mm, L, Z(L), X, None, tpp=tp, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. 3x SuperTrend
def run_3st(name, df, mm, tag, rows=None, verbose=True, pl=1.5, thr=20, long_ok=True, short_ok=True, **extra):
    """EMA200 de tendencia, StochRSI(3,3,14,14) cruzando abaixo de 20 (acima de 80 no short) e pelo menos um
    dos 3 SuperTrends (12x3, 11x2, 10x1) a favor. Stop no ST medio (se os 3 concordam) ou no lento; alvo
    1,5 x o risco. Sem nova entrada com posicao aberta."""
    o, h, l, c = ohlc(df)
    hl2 = (h + l) / 2
    ts, us, ds = supertrend(h, l, c, 12, 3.0, hl2)
    tm, um, dm = supertrend(h, l, c, 11, 2.0, hl2)
    tf, _, _ = supertrend(h, l, c, 10, 1.0, hl2)
    r_ = T.rsi_wilder(c, 14)
    k = T.sma(stoch(r_, r_, r_, 14), 3); d = T.sma(k, 3)
    e = ema(c, 200); cnt = ts + tm + tf
    L = (c > e) & (k < thr) & T.xover(k, d) & (cnt >= 1)
    S = (c < e) & (k > 100 - thr) & T.xunder(k, d) & (cnt <= -1)
    L[:200] = S[:200] = False
    sll = np.where(cnt == 3, um, us); sls = np.where(cnt == -3, dm, ds)
    tpl = c + pl * np.abs(c - sll); tps = c - pl * np.abs(c - sls)
    r = gsim(df, mm, L, S & ~L, SLL=sll, TPL=tpl, SLS=sls, TPS=tps, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. RSI-adaptive T3 + SAR
@njit(cache=True)
def _vema(src, ln):
    out = np.empty(len(src)); s = src[0]
    for i in range(len(src)):
        a = 2.0 / (ln[i] + 1)
        s = src[i] if i == 0 else a * src[i] + (1 - a) * s
        out[i] = s
    return out


def run_t3sar(name, df, mm, tag, rows=None, verbose=True, v=0.7, stop_len=10, use_stop=True, long_ok=True,
              short_ok=True, **extra):
    """T3 com comprimento 5..50 escalado pelo RSI14 (RSI alto = T3 rapido). Compra quando T3 cruza acima do
    T3[2] e close > SAR(0,02; 0,0002; 0,21); vende no espelho com close < SAR. Sai no cruzamento contrario
    do T3; stop na minima (maxima) de 10 barras da entrada."""
    o, h, l, c = ohlc(df)
    rs = np.nan_to_num(T.rsi_wilder(c, 14), nan=50.0)
    ln = np.round(5 + 45 * (1 - rs / 100))
    e1 = _vema(c, ln); e2 = _vema(e1, ln); e3 = _vema(e2, ln); e4 = _vema(e3, ln); e5 = _vema(e4, ln); e6 = _vema(e5, ln)
    c1 = -v ** 3; c2 = 3 * v * v + 3 * v ** 3; c3 = -6 * v * v - 3 * v - 3 * v ** 3; c4 = 1 + 3 * v + v ** 3 + 3 * v * v
    t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
    up = psar_up(h, l, c, 0.02, 0.0002, 0.21)
    t32 = sh(t3, 2)
    xo, xu = T.xover(t3, t32), T.xunder(t3, t32)
    L, S = xo & up, xu & ~up
    L[:60] = S[:60] = False
    kw = dict(SLL=roll(l, stop_len).min().to_numpy(), SLS=roll(h, stop_len).max().to_numpy()) if use_stop else {}
    r = gsim(df, mm, L, S, xu, xo, rev=False, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. Moving Regression Band
def mreg(x, window, degree):
    """Ajuste polinomial por minimos quadrados na janela: valor no fim (MR), previsao 1 passo (MR_f) e MAE."""
    J = np.vander(np.arange(window, dtype=float), degree + 1, increasing=True)
    P = np.linalg.pinv(J)                                  # (deg+1, window)
    wY = np.vander([window - 1.0], degree + 1, increasing=True)[0] @ P
    wF = np.vander([float(window)], degree + 1, increasing=True)[0] @ P
    R = np.eye(window) - J @ P
    n = len(x); mr = np.full(n, NAN); mf = np.full(n, NAN); err = np.full(n, NAN)
    if n < window: return mr, mf, err
    W = np.lib.stride_tricks.sliding_window_view(x, window)
    for a in range(0, len(W), 20000):
        w = W[a:a + 20000]
        mr[window - 1 + a: window - 1 + a + len(w)] = w @ wY
        mf[window - 1 + a: window - 1 + a + len(w)] = w @ wF
        err[window - 1 + a: window - 1 + a + len(w)] = np.abs(w @ R.T).mean(1)
    return mr, mf, err


def run_mrb(name, df, mm, tag, rows=None, verbose=True, window=80, degree=2, mult=2.0, exit_='lower-atr',
            long_ok=True, short_ok=False, **extra):
    """Banda = previsao do periodo anterior +- 2 x MAE do ajuste (grau 2, janela 80). Compra no rompimento da
    banda de cima; sai quando close cruza abaixo de banda de baixo - ATR14 (padrao). Short desligado por
    padrao (sai na linha central). O stop no preco de entrada depois que a saida passa dele foi omitido."""
    o, h, l, c = ohlc(df)
    mr, mf, err = mreg(c, window, degree)
    hb, lb, cl = sh(mf) + mult * sh(err), sh(mf) - mult * sh(err), sh(mf)
    a = T.atr_rma(h, l, c, 14)
    tl = {'lower-atr': lb - a, 'lower': lb, 'central': cl}[exit_]
    L, S = T.xover(c, hb), T.xunder(c, lb)
    XL, XS = T.xunder(c, tl), T.xover(c, cl)
    r = gsim(df, mm, L, S, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Double AI SuperTrend
def vst(h, l, c, v, ln, fac):
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
    return d, st, a0


def run_dai(name, df, mm, tag, rows=None, verbose=True, f1=4.0, f2=3.0, long_ok=True, short_ok=True, **extra):
    """Dois SuperTrends de VWMA (10 x 4 e 5 x 3). O rotulo KNN de cada um foi aproximado (como no lote 16) por
    WMA do preco (20 e 40) acima da WMA do SuperTrend (80). Compra com os dois em alta e rotulo 1, vende no
    espelho, inverte; stop movel em ST -+ 4 ATR."""
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float)
    d1, s1, a1 = vst(h, l, c, v, 10, f1); d2, s2, a2 = vst(h, l, c, v, 5, f2)
    l1 = T.wma(c, 20) > T.wma(s1, 80); l2 = T.wma(c, 40) > T.wma(s2, 80)
    lc = (d1 == -1) & l1 & (d2 == -1) & l2
    sc = (d1 == 1) & ~l1 & (d2 == 1) & ~l2
    pos = np.where(lc, 1, np.where(sc, -1, 0))
    L = lc & (sh(pos) != 1); S = sc & (sh(pos) != -1)
    L[:100] = S[:100] = False
    r = gsim(df, mm, L, S, (c < s1 - f1 * a1) | (S if not short_ok else Z(S)), c > s1 + f1 * a1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. RSI and ATR Trend Reversal
@njit(cache=True)
def _rsirev(src, rsl, rsu, atrp, mult, sl, tp, cap):
    n = len(src); th = np.full(n, np.nan)
    a = np.full(n, np.nan); b = np.full(n, np.nan); a2 = np.full(n, np.nan); b2 = np.full(n, np.nan)
    cu = False; cd = False; last = -1; bear = 0; dr = 1.0; thr_prev = np.nan
    for i in range(n):
        if cu or cd:
            last = i - 1
        if last < 0:
            bear += 1
        else:
            bear = i - last
        B = min(bear, cap)
        hh = src[i]; ll = src[i]
        for j in range(max(0, i - B), i + 1):
            if src[j] > hh: hh = src[j]
            if src[j] < ll: ll = src[j]
        if rsl[i] == rsl[i] and rsl[i] > 0 and atrp[i] == atrp[i]:
            a[i] = hh * (1 - (atrp[i] + 1 / rsl[i] * mult))
        if rsu[i] == rsu[i] and rsu[i] > 0 and atrp[i] == atrp[i]:
            b[i] = ll * (1 + (atrp[i] + 1 / rsu[i] * mult))
        m1 = a[i]; m2 = b[i]
        for j in range(max(0, i - B), i + 1):
            if a[j] == a[j] and (m1 != m1 or a[j] > m1): m1 = a[j]
            if b[j] == b[j] and (m2 != m2 or b[j] < m2): m2 = b[j]
        a2[i] = max(m1, src[i] * sl) if m1 == m1 else src[i] * sl
        b2[i] = min(m2, src[i] * tp) if m2 == m2 else src[i] * tp
        lo = a2[i]; up = b2[i]
        for j in range(max(0, i - B), i + 1):
            if a2[j] > lo: lo = a2[j]
            if b2[j] < up: up = b2[j]
        if cd: dr = -1.0
        if cu: dr = 1.0
        t = lo if dr == 1 else up
        th[i] = t
        if i:
            cu = src[i] > t and src[i - 1] <= thr_prev
            cd = src[i] < t and src[i - 1] >= thr_prev
        thr_prev = t
    return th


def run_rsirev(name, df, mm, tag, rows=None, verbose=True, ln=8, mult=1.5, sltp=10.0, ha=True, long_ok=True,
               short_ok=True, **extra):
    """Linha de reversao do RSI e ATR sobre o close Heikin Ashi: em alta, maxima desde a ultima virada x
    (1 - (ATR8/preco + 1,5/RSI8)), limitada a 10% do preco; em baixa, o espelho. Cruzamento do close HA com a
    linha compra/vende e inverte, com 1 barra de atraso (padrao do script). Janela limitada a 300 barras."""
    o, h, l, c = ohlc(df)
    src = heikin(o, h, l, c)[3] if ha else c
    rs = T.rsi_wilder(src, ln)
    atrp = T.atr_rma(h, l, c, ln) / src
    th = _rsirev(src, rs, np.abs(rs - 100), atrp, mult, (100 - sltp) / 100, (100 + sltp) / 100, 300)
    L, S = T.xover(src, th), T.xunder(src, th)
    L, S = sh(L) == 1, sh(S) == 1
    L[:ln * 3] = S[:ln * 3] = False
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Alligator HA
def run_alli(name, df, mm, tag, rows=None, verbose=True, ha=True, long_ok=True, short_ok=True, **extra):
    """SMAs 13/8/5 do hl2 Heikin Ashi (sem deslocamento no calculo). Compra com duas velas HA de alta e
    mandibula < dentes < labios; fecha quando a ordem quebra. Short no espelho."""
    o, h, l, c = ohlc(df)
    if ha:
        ho, hh, hl, hc = heikin(o, h, l, c)
    else:
        ho, hh, hl, hc = o, h, l, c
    m = (hh + hl) / 2
    jaw, teeth, lips = T.sma(m, 13), T.sma(m, 8), T.sma(m, 5)
    up = hc > ho; dn = hc < ho
    d = np.where(up & (sh(up) == 1), 1, np.where(dn & (sh(dn) == 1), -1, 0))
    bull = (jaw < teeth) & (jaw < lips) & (teeth < lips); bear = (jaw > teeth) & (jaw > lips) & (teeth > lips)
    L, S = (d == 1) & bull, (d == -1) & bear
    r = gsim(df, mm, L, S, ~bull, ~bear, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Camarilla
def daily_prev(df, daily, cols):
    sh_ = daily[cols].copy(); sh_.index = sh_.index + pd.Timedelta('1D')
    return sh_.reindex(df.index, method='ffill')


def run_cam(name, df, mm, daily, tag, rows=None, verbose=True, sl=0.01, tp=0.02, long_ok=True, short_ok=True, **extra):
    """H4/L4 da vela diaria anterior (C +- 1,1 x (H-L)/2). Compra quando o candle abre abaixo de H4 e fecha
    acima com close > EMA8; venda no espelho em L4. Stop/trailing em ticks viraram SL/TP em %."""
    o, h, l, c = ohlc(df)
    p = daily_prev(df, daily, ['high', 'low', 'close'])
    rg = (p.high - p.low).to_numpy(); pc = p.close.to_numpy()
    h4, l4 = pc + rg * 1.1 / 2, pc - rg * 1.1 / 2
    e8 = ema(c, 8)
    L = (c > h4) & (o < h4) & (e8 < c); S = (c < l4) & (o > l4) & (e8 > c)
    r = gsim(df, mm, L, S, slp=sl, tpp=tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Nadaraya-Watson
def nw(x, hlen=8, alpha=8.0, x0=25):
    i = np.arange(hlen + 1)
    w = (1 + (x0 - i) ** 2 / (2 * alpha * hlen * hlen)) ** -alpha
    out = np.full(len(x), NAN)
    for k in range(hlen + 1):
        out[hlen:] = (0 if k == 0 else out[hlen:]) + w[k] * x[hlen - k:len(x) - k]
    return out / w.sum()


def run_nw(name, df, mm, tag, rows=None, verbose=True, hlen=8, x0=25, shorts=False, **extra):
    """Kernel racional quadratico (janela 8, peso 8, inicio 25) no log de close/high/low. Compra quando o close
    cruza acima do envelope das minimas; fecha quando cruza abaixo do envelope das maximas. Long/short opcional
    (short quando cruza abaixo do envelope das maximas)."""
    o, h, l, c = ohlc(df)
    eh, el = np.exp(nw(np.log(h), hlen, 8.0, x0)), np.exp(nw(np.log(l), hlen, 8.0, x0))
    L = T.xover(c, el); XL = T.xover(eh, c)
    if shorts:
        S = T.xunder(c, eh); XS = T.xunder(el, c)
        r = gsim(df, mm, L, S & ~L, XL, XS, rev=True)
    else:
        r = gsim(df, mm, L, Z(L), XL, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Extreme Scalping
def run_xscalp(name, df, mm, tag, rows=None, verbose=True, gap=0.005, rr=3.0, long_ok=True, short_ok=True, **extra):
    """Regressao linear 14 (offset 1). Compra com close < reta - gap, vende com close > reta + gap; SL = gap e
    TP = 3 x gap (100/300 ticks viraram %). Sinal contrario inverte."""
    o, h, l, c = ohlc(df)
    n = 14; x = np.arange(n, dtype=float); xm = x.mean()
    W = np.lib.stride_tricks.sliding_window_view(c, n)
    b = ((W - W.mean(1, keepdims=True)) * (x - xm)).sum(1) / ((x - xm) ** 2).sum()
    a = W.mean(1) - b * xm
    out = np.full(len(c), NAN); out[n - 1:] = a + b * (n - 1 - 1)
    L, S = c < out * (1 - gap), c > out * (1 + gap)
    r = gsim(df, mm, L, S, slp=gap, tpp=gap * rr, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Y-PMax
def run_ypmax(name, df, mm, tag, rows=None, verbose=True, ln=13, mult=3.0, ap=10, shorts=False, **extra):
    """PMax: ZLEMA13 do hl2 com stop ATR10 x 3. Compra quando a ZLEMA cruza acima do PMax, fecha tudo no
    cruzamento para baixo. As saidas parciais pelo MOST foram ignoradas. Long-only (short opcional)."""
    o, h, l, c = ohlc(df)
    src = (h + l) / 2; lag = ln // 2 if ln % 2 == 0 else (ln - 1) // 2
    mav = ema(src + (src - sh(src, lag)), ln)
    mav = np.where(np.isfinite(mav), mav, src)
    a = np.nan_to_num(T.atr_rma(h, l, c, ap))
    n = len(c); ls = np.zeros(n); ss = np.zeros(n); d = np.ones(n)
    for i in range(n):
        l_ = mav[i] - mult * a[i]; s_ = mav[i] + mult * a[i]
        lp = ls[i - 1] if i else l_; sp = ss[i - 1] if i else s_
        ls[i] = max(l_, lp) if mav[i] > lp else l_
        ss[i] = min(s_, sp) if mav[i] < sp else s_
        dd = d[i - 1] if i else 1
        d[i] = 1 if (dd == -1 and mav[i] > sp) else (-1 if (dd == 1 and mav[i] < lp) else dd)
    pm = np.where(d == 1, ls, ss)
    L, S = T.xover(mav, pm), T.xunder(mav, pm); L[:ln + ap] = S[:ln + ap] = False
    if shorts:
        r = gsim(df, mm, L, S, rev=True)
    else:
        r = gsim(df, mm, L, Z(L), S, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. PMARP + Madrid ribbon
def run_madrid(name, df, mm, tag, rows=None, verbose=True, tp=0.01, sl=0.2775, rsi_min=55, long_ok=True,
               short_ok=True, **extra):
    """Fita Madrid: 18 EMAs (5 a 90) todas subindo e acima da EMA100 (lime) = long, com vela anterior de baixa e
    RSI14 > 55; todas caindo e abaixo (red) = short. TP 1% e SL 27,75% (padrao). A saida por PMARP >= 99
    quase nunca coincide com o sinal red e foi omitida."""
    o, h, l, c = ohlc(df)
    ms = [ema(c, k) for k in range(5, 95, 5)]; m100 = ema(c, 100)
    lime = np.ones(len(c), bool); red = np.ones(len(c), bool)
    for m in ms:
        ch = np.diff(m, prepend=NAN)
        lime &= (ch >= 0) & (m > m100); red &= (ch < 0) & (m < m100)
    L = lime & ~(sh(c) > sh(o)) & (T.rsi_wilder(c, 14) > rsi_min); S = red
    L[:100] = S[:100] = False
    r = gsim(df, mm, L, S & ~L, slp=sl, tpp=tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. ATR GOD
def run_atrgod(name, df, mm, tag, rows=None, verbose=True, slm=4.5, rr=1.5, filters=True, long_ok=True,
               short_ok=True, **extra):
    """4 SuperTrends (20x2 hl2, 5x15 hlcc4, 10x3 hl2, 20x10 hl2). Gatilho = virada do ST1, ST3 ou ST4, com os
    4 na mesma direcao. Filtros padrao: volume > RMA200 do volume, ATR50 abaixo da sua RMA400 e sem quartas.
    SL = 4,5 x ATR100 e TP = 1,5 x isso. Sinal contrario inverte."""
    o, h, l, c = ohlc(df)
    hl2 = (h + l) / 2; hlcc4 = (h + l + 2 * c) / 4
    sts = [supertrend(h, l, c, 20, 2.0, hl2)[0], supertrend(h, l, c, 5, 15.0, hlcc4)[0],
           supertrend(h, l, c, 10, 3.0, hl2)[0], supertrend(h, l, c, 20, 10.0, hl2)[0]]
    allup = np.all([t == 1 for t in sts], 0); alldn = np.all([t == -1 for t in sts], 0)
    trig_l = np.any([(sts[k] == 1) & (sh(sts[k]) == -1) for k in (0, 2, 3)], 0)
    trig_s = np.any([(sts[k] == -1) & (sh(sts[k]) == 1) for k in (0, 2, 3)], 0)
    L, S = trig_l & allup, trig_s & alldn
    if filters:
        v = df.volume.to_numpy(float)
        tr = tr_(h, l, c); a50 = rma(tr, 50)
        ok = (v > rma(v, 200)) & (a50 < rma(a50, 400)) & (df.index.dayofweek != 2)
        L &= ok; S &= ok
    a = rma(tr_(h, l, c), 100)
    L[:100] = S[:100] = False
    r = gsim(df, mm, L, S, SLL=c - slm * a, TPL=c + slm * rr * a, SLS=c + slm * a, TPS=c - slm * rr * a, rev=True,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. [DS] EMA8 x DEMA34
def run_ds(name, df, mm, tag, rows=None, verbose=True, f=8, s=34, long_ok=True, short_ok=True, **extra):
    """EMA8 do ohlc4 cruza a DEMA34 do close: compra/vende e inverte."""
    o, h, l, c = ohlc(df)
    e = ema((o + h + l + c) / 4, f); e1 = ema(c, s); dm = 2 * e1 - ema(e1, s)
    L, S = T.xover(e, dm), T.xunder(e, dm); L[:2 * s] = S[:2 * s] = False
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. FRAMA
def frama(src, H, L, ln=12, fc=1, sc=200):
    l1 = ln // 2; w = np.log(2 / (sc + 1))
    H1 = roll(H, l1).max().to_numpy(); L1 = roll(L, l1).min().to_numpy()
    N1 = (H1 - L1) / l1; N2 = (sh(H1, l1) - sh(L1, l1)) / l1
    N3 = (roll(H, ln).max().to_numpy() - roll(L, ln).min().to_numpy()) / ln
    with np.errstate(divide='ignore', invalid='ignore'):
        dim = (np.log(N1 + N2) - np.log(N3)) / np.log(2)
    ok = (N1 > 0) & (N2 > 0) & (N3 > 0)
    dim = pd.Series(np.where(ok, dim, NAN)).ffill().fillna(0).to_numpy()
    a1 = np.exp(w * (dim - 1)); oa = np.clip(a1, 0.01, 1); oN = (2 - oa) / oa
    N = ((sc - fc) * (oN - 1)) / (sc - 1) + fc
    al = np.clip(2 / (N + 1), 2 / (sc + 1), 1)
    out = np.zeros(len(src)); p = 0.0
    for i in range(len(src)):
        x = src[i] if src[i] == src[i] else 0.0
        p = (1 - al[i]) * p + al[i] * x; out[i] = p
    return out


def run_frama(name, df, mm, tag, rows=None, verbose=True, ln=12, weekly=True, long_ok=True, short_ok=True, **extra):
    """FRAMA 12 (FC 1, SC 200) e sinal = FRAMA da FRAMA; cruzamento compra/vende e inverte. Padrao: calculado
    no semanal (barras fechadas, o sinal vale a partir da semana seguinte)."""
    o, h, l, c = ohlc(df)
    if weekly:
        w = df.resample('W-MON', label='left', closed='left').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
        H, Lw, C = w.high.to_numpy(float), w.low.to_numpy(float), w.close.to_numpy(float)
        fr = frama(C, H, Lw, ln); sg = frama(fr, H, Lw, ln)
        lw, sw = T.xover(fr, sg), T.xunder(fr, sg)
        lw[:2 * ln] = sw[:2 * ln] = False
        end = w.index + pd.Timedelta('7D')
        pos = np.searchsorted(df.index.values, end.values) - 1       # ultima barra da semana
        L = Z(c); S = Z(c)
        ok = (pos >= 0) & (pos < len(c))
        L[pos[ok & lw]] = True; S[pos[ok & sw]] = True
    else:
        fr = frama(c, h, l, ln); sg = frama(fr, h, l, ln)
        L, S = T.xover(fr, sg), T.xunder(fr, sg); L[:2 * ln] = S[:2 * ln] = False
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. World Cycle (Pi Cycle)
def run_wcycle(name, df, mm, daily, tag, rows=None, verbose=True, k=1.0, long_ok=True, short_ok=True, **extra):
    """Diario: vende quando 2 x SMA350 cruza abaixo da SMA111 (topo); compra quando 0,745 x SMA471 cruza acima
    da EMA150 (fundo). Inverte. Comprimentos multiplicados por k na grade."""
    C = daily.close.to_numpy(float)
    a = T.sma(C, int(350 * k)) * 2; b = T.sma(C, int(111 * k))
    cL = T.sma(C, int(471 * k)) * 0.745; dL = ema(C, int(150 * k))
    sd, ld = T.xunder(a, b), T.xover(cL, dL)
    end = daily.index + pd.Timedelta('1D')
    pos = np.searchsorted(df.index.values, end.values) - 1
    L = Z(df); S = Z(df); ok = (pos >= 0) & (pos < len(df))
    L[pos[ok & ld]] = True; S[pos[ok & sd]] = True
    r = gsim(df, mm, L, S, None if short_ok else S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        daily = cache['1D']
        rows = []; side2 = ('ambos', 'long')
        sk = lambda s: dict(short_ok=s == 'ambos')

        def sec(t):
            print(f"\n### {t}", flush=True)

        sec("1. Keltner Channel (long-only)")
        for tf in TFS:
            df = cache[tf]
            run_kelt(name, df, mm, f"{tf} KELT default", rows, est='kelt', TF=tf, cfg='81 2.5 tp20 sl4 tend')
            for (ln, mu), (tp, sl), tr in itertools.product(((81, 2.5), (40, 2.0)), ((0.20, 0.04), (0.06, 0.02)), (True, False)):
                run_kelt(name, df, mm, '', rows, False, ln=ln, mult=mu, tp=tp, sl=sl, trend=tr, est='kelt', TF=tf,
                         cfg=f'{ln} {mu} tp{tp:.0%} sl{sl:.0%} ' + ('tend' if tr else 'semtend'))

        sec("2. ATR Trailing Stop ceyhun (5x0,5 vs 10x3)")
        for tf in TFS:
            df = cache[tf]
            run_ceyhun(name, df, mm, f"{tf} CEYHUN default", rows, est='ceyhun', TF=tf, cfg='m2 3 ambos')
            for m2, side in itertools.product((2.0, 3.0, 5.0), side2):
                run_ceyhun(name, df, mm, '', rows, False, m2=m2, **sk(side), est='ceyhun', TF=tf, cfg=f'm2 {m2:g} {side}')

        sec("3. 3C QFL Mean reversal (long-only, sem DCA)")
        for tf in TFS:
            df = cache[tf]
            run_qfl(name, df, mm, f"{tf} QFL default", rows, est='qfl', TF=tf, cfg='0.5% tp1% semstop age10')
            for pct, tp, sl in itertools.product((0.005, 0.02), (0.01, 0.03), (0.0, 0.05)):
                run_qfl(name, df, mm, '', rows, False, pct=pct, tp=tp, sl=sl, est='qfl', TF=tf,
                        cfg=f'{pct:.1%} tp{tp:.0%} ' + (f'sl{sl:.0%}' if sl else 'semstop') + ' age10')
            run_qfl(name, df, mm, '', rows, False, maxage=0, est='qfl', TF=tf, cfg='0.5% tp1% semstop semage')

        sec("4. Follow Line (EMA21 +- 1 desvio, ATR5)")
        for tf in TFS:
            df = cache[tf]
            run_fline(name, df, mm, f"{tf} FLINE default", rows, est='fline', TF=tf, cfg='21 1.0 ambos')
            for ln, dv, side in itertools.product((21, 50), (1.0, 2.0), side2):
                run_fline(name, df, mm, '', rows, False, ln=ln, dev=dv, **sk(side), est='fline', TF=tf, cfg=f'{ln} {dv} {side}')

        sec("5. MACD 3/5/2 + stop ATR17 x 2,2 (long-only)")
        for tf in TFS:
            df = cache[tf]
            run_macd(name, df, mm, f"{tf} MACD default", rows, est='macd', TF=tf, cfg='m2.2 semtp filtro')
            for mu, tp, fl in itertools.product((2.2, 4.0), (0.0, 0.05), (True, False)):
                run_macd(name, df, mm, '', rows, False, mult=mu, tp=tp, filt=fl, est='macd', TF=tf,
                         cfg=f'm{mu} ' + (f'tp{tp:.0%}' if tp else 'semtp') + (' filtro' if fl else ' semfiltro'))

        sec("6. 3x SuperTrend + StochRSI + EMA200")
        for tf in TFS:
            df = cache[tf]
            run_3st(name, df, mm, f"{tf} 3ST default", rows, est='3st', TF=tf, cfg='pl1.5 thr20 ambos')
            for pl, thr, side in itertools.product((1.5, 3.0), (20, 30), side2):
                run_3st(name, df, mm, '', rows, False, pl=pl, thr=thr, **sk(side), est='3st', TF=tf, cfg=f'pl{pl} thr{thr} {side}')

        sec("7. RSI-Adaptive T3 + SAR")
        for tf in TFS:
            df = cache[tf]
            run_t3sar(name, df, mm, f"{tf} T3SAR default", rows, est='t3sar', TF=tf, cfg='stop10 ambos')
            for st, side in itertools.product((True, False), side2):
                run_t3sar(name, df, mm, '', rows, False, use_stop=st, **sk(side), est='t3sar', TF=tf,
                          cfg=('stop10 ' if st else 'semstop ') + side)

        sec("8. Moving Regression Band Breakout (long-only)")
        for tf in TFS:
            df = cache[tf]
            run_mrb(name, df, mm, f"{tf} MRB default", rows, est='mrb', TF=tf, cfg='80 g2 m2 lower-atr long')
            for (wd, mu), ex, shs in itertools.product(((80, 2.0), (40, 1.0)), ('lower-atr', 'central'), (False, True)):
                run_mrb(name, df, mm, '', rows, False, window=wd, mult=mu, exit_=ex, short_ok=shs, est='mrb', TF=tf,
                        cfg=f'{wd} g2 m{mu:g} {ex} ' + ('ambos' if shs else 'long'))

        sec("9. Double AI SuperTrend (VWMA 10x4 + 5x3)")
        for tf in TFS:
            df = cache[tf]
            run_dai(name, df, mm, f"{tf} DAI default", rows, est='dai', TF=tf, cfg='4/3 ambos')
            for (f1, f2), side in itertools.product(((4.0, 3.0), (2.0, 1.5)), side2):
                run_dai(name, df, mm, '', rows, False, f1=f1, f2=f2, **sk(side), est='dai', TF=tf, cfg=f'{f1:g}/{f2:g} {side}')

        sec("10. RSI and ATR Trend Reversal (HA)")
        for tf in TFS:
            df = cache[tf]
            run_rsirev(name, df, mm, f"{tf} RSIREV default", rows, est='rsirev', TF=tf, cfg='8 1.5 ha ambos')
            for (ln, mu), ha, side in itertools.product(((8, 1.5), (14, 3.0)), (True, False), side2):
                run_rsirev(name, df, mm, '', rows, False, ln=ln, mult=mu, ha=ha, **sk(side), est='rsirev', TF=tf,
                           cfg=f'{ln} {mu} ' + ('ha ' if ha else 'normal ') + side)

        sec("11. Alligator Heikin Ashi")
        for tf in TFS:
            df = cache[tf]
            run_alli(name, df, mm, f"{tf} ALLI default", rows, est='alli', TF=tf, cfg='ha ambos')
            for ha, side in itertools.product((True, False), side2):
                run_alli(name, df, mm, '', rows, False, ha=ha, **sk(side), est='alli', TF=tf, cfg=('ha ' if ha else 'normal ') + side)

        sec("12. Camarilla H4/L4 breakout")
        for tf in ['15min', '30min', '1h', '4h']:
            df = cache[tf]
            run_cam(name, df, mm, daily, f"{tf} CAM default", rows, est='cam', TF=tf, cfg='sl1% tp2% ambos')
            for (sl, tp), side in itertools.product(((0.005, 0.01), (0.01, 0.02), (0.02, 0.06)), side2):
                run_cam(name, df, mm, daily, '', rows, False, sl=sl, tp=tp, **sk(side), est='cam', TF=tf,
                        cfg=f'sl{sl:.1%} tp{tp:.0%} {side}'.replace('sl1.0%', 'sl1%'))

        sec("13. Nadaraya-Watson Envelope")
        for tf in TFS:
            df = cache[tf]
            run_nw(name, df, mm, f"{tf} NW default", rows, est='nw', TF=tf, cfg='8 x25 long')
            for hl, x0, shs in itertools.product((8, 20), (25, 10), (False, True)):
                run_nw(name, df, mm, '', rows, False, hlen=hl, x0=x0, shorts=shs, est='nw', TF=tf,
                       cfg=f'{hl} x{x0} ' + ('ambos' if shs else 'long'))

        sec("14. Extreme Scalping (linreg 14, gap)")
        for tf in TFS:
            df = cache[tf]
            run_xscalp(name, df, mm, f"{tf} XSCALP default", rows, est='xscalp', TF=tf, cfg='gap0.5% rr3 ambos')
            for gp, rr, side in itertools.product((0.0025, 0.005, 0.01), (1.0, 3.0), side2):
                run_xscalp(name, df, mm, '', rows, False, gap=gp, rr=rr, **sk(side), est='xscalp', TF=tf,
                           cfg=f'gap{gp:.2%} rr{rr:g} {side}'.replace('gap0.50%', 'gap0.5%'))

        sec("15. Y-PMax (ZLEMA13, ATR10 x 3)")
        for tf in TFS:
            df = cache[tf]
            run_ypmax(name, df, mm, f"{tf} YPMAX default", rows, est='ypmax', TF=tf, cfg='13 3 long')
            for ln, mu, shs in itertools.product((13, 30), (2.0, 3.0), (False, True)):
                run_ypmax(name, df, mm, '', rows, False, ln=ln, mult=mu, shorts=shs, est='ypmax', TF=tf,
                          cfg=f'{ln} {mu:g} ' + ('ambos' if shs else 'long'))

        sec("16. PMARP + Madrid MA Ribbon")
        for tf in TFS:
            df = cache[tf]
            run_madrid(name, df, mm, f"{tf} MADRID default", rows, est='madrid', TF=tf, cfg='tp1% sl27.75% ambos')
            for (tp, sl), side in itertools.product(((0.01, 0.2775), (0.03, 0.03), (0.06, 0.03)), side2):
                run_madrid(name, df, mm, '', rows, False, tp=tp, sl=sl, **sk(side), est='madrid', TF=tf,
                           cfg=f'tp{tp:.0%} sl{sl:.2%} {side}'.replace('sl27.75%', 'sl27.75%').replace('sl3.00%', 'sl3%'))

        sec("17. ATR GOD (4 SuperTrends + filtros)")
        for tf in TFS:
            df = cache[tf]
            run_atrgod(name, df, mm, f"{tf} ATRGOD default", rows, est='atrgod', TF=tf, cfg='sl4.5 rr1.5 filtros ambos')
            for (slm, rr), fl, side in itertools.product(((4.5, 1.5), (2.0, 2.0)), (True, False), side2):
                run_atrgod(name, df, mm, '', rows, False, slm=slm, rr=rr, filters=fl, **sk(side), est='atrgod', TF=tf,
                           cfg=f'sl{slm} rr{rr} ' + ('filtros ' if fl else 'semfiltros ') + side)

        sec("18. [DS] EMA8(ohlc4) x DEMA34")
        for tf in TFS:
            df = cache[tf]
            run_ds(name, df, mm, f"{tf} DS default", rows, est='ds', TF=tf, cfg='8/34 ambos')
            for (f, s), side in itertools.product(((8, 34), (8, 72), (17, 72)), side2):
                run_ds(name, df, mm, '', rows, False, f=f, s=s, **sk(side), est='ds', TF=tf, cfg=f'{f}/{s} {side}')

        sec("19. FRAMA (semanal por padrao)")
        for tf in ['1h', '4h', '1D']:
            df = cache[tf]
            run_frama(name, df, mm, f"{tf} FRAMA default", rows, est='frama', TF=tf, cfg='12 semanal ambos')
            for wk, side in itertools.product((True,), side2):
                run_frama(name, df, mm, '', rows, False, weekly=wk, **sk(side), est='frama', TF=tf, cfg=f'12 semanal {side}')
        for tf in TFS:
            df = cache[tf]
            for ln, side in itertools.product((12, 40), side2):
                run_frama(name, df, mm, '', rows, False, ln=ln, weekly=False, **sk(side), est='frama', TF=tf,
                          cfg=f'{ln} propriotf {side}')

        sec("20. World Cycle ATH/ATL (diario)")
        for tf in ['4h', '1D']:
            df = cache[tf]
            run_wcycle(name, df, mm, daily, f"{tf} WCYCLE default", rows, est='wcycle', TF=tf, cfg='k1 ambos')
            for k, side in itertools.product((1.0, 0.5, 0.25), side2):
                run_wcycle(name, df, mm, daily, '', rows, False, k=k, **sk(side), est='wcycle', TF=tf, cfg=f'k{k:g} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote20')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
