"""Lote 36 do TradingView (2026-10-27): 20 estrategias nos 5 ativos, posicoes 908 a 963 da lista, grade completa como
nos lotes 26 a 35 (ver docs/LOTE36_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote36.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch
from study_tvlote9 import summary
from study_tvlote20 import sh
from study_tvlote21 import linreg
from study_tvlote22 import run_stp
from study_tvlote23 import run_trl
from study_tvlote25 import posflat, wilder_rsi, hh, ll, Z, NAN, roll
from study_tvlote27 import rev_or_long
from study_tvlote30 import R


def stdev(x, n):
    return T.stdev_pop(x, n)


def macd_sma(c, f, s, g):
    m = T.sma(c, f) - T.sma(c, s); return m, T.sma(m, g)


def st_old(h, l, c, f, n):
    """Supertrend das versoes antigas: TrendUp/TrendDown com close[1]; devolve a linha Tsl."""
    a = T.atr_rma(h, l, c, n); hl2 = (h + l) / 2; up = hl2 - f * a; dn = hl2 + f * a; N = len(c)
    tu = np.full(N, NAN); td = np.full(N, NAN); tr = np.ones(N); ts = np.full(N, NAN)
    for i in range(N):
        if up[i] != up[i]: continue
        pu = tu[i - 1] if i else NAN; pd_ = td[i - 1] if i else NAN
        tu[i] = max(up[i], pu) if (pu == pu and c[i - 1] > pu) else up[i]
        td[i] = min(dn[i], pd_) if (pd_ == pd_ and c[i - 1] < pd_) else dn[i]
        tr[i] = 1 if (pd_ == pd_ and c[i] > pd_) else (-1 if (pu == pu and c[i] < pu) else (tr[i - 1] if i else 1))
        ts[i] = tu[i] if tr[i] == 1 else td[i]
    return ts


def atr_trail(c, nl):
    """xATRTrailingStop classico (Vervoort / UT Bot)."""
    n = len(c); t = np.zeros(n)
    for i in range(1, n):
        p = t[i - 1]; d = nl[i] if nl[i] == nl[i] else 0.0
        if c[i] > p and c[i - 1] > p: t[i] = max(p, c[i] - d)
        elif c[i] < p and c[i - 1] < p: t[i] = min(p, c[i] + d)
        else: t[i] = c[i] - d if c[i] > p else c[i] + d
    return t


# ------------------------------------------------------------------ 1. Stoch RSI Crossover + EMA (isC2RICc)
def run_sre(name, df, mm, tag, rows=None, verbose=True, pf=1.5, sf=2.0, long_ok=True, short_ok=True, **extra):
    """Stoch RSI 14/14/3/3 com K cruzando D, EMAs 8 > 15 > 50 com close acima da 8 e MACD SMA 12/24/8 acima do sinal
    mas abaixo de zero compra (espelho vende), so sem posicao; alvo 1,5 ATR11 e stop 2 ATR11 da barra do sinal."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 14); k = T.sma(stoch(r, r, r, 14), 3); d = T.sma(k, 3)
    m, s = macd_sma(c, 12, 24, 8); e1, e2, e3 = ema(c, 8), ema(c, 15), ema(c, 50); a = T.atr_rma(h, l, c, 11)
    L = T.xover(k, d) & (e1 > e2) & (e2 > e3) & (c > e1) & (m > s) & (m < 0)
    S = T.xunder(k, d) & (e1 < e2) & (e2 < e3) & (c < e1) & (m < s) & (m > 0)
    res = gsim(df, mm, L, S, SLL=c - sf * a, TPL=c + pf * a, SLS=c + sf * a, TPS=c - pf * a, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Kozlod BB (D3PkU5ho)
def run_kbb(name, df, mm, tag, rows=None, verbose=True, n=55, mult=4.0, long_ok=True, short_ok=True, **extra):
    """BB 55 x 4: close cruzando acima da banda de baixo compra, abaixo da de cima vende; inverte (a ordem stop na
    banda ja esta abaixo do preco, entao vira mercado)."""
    o, h, l, c = ohlc(df); b = T.sma(c, n); dv = mult * stdev(c, n)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(c, b - dv), T.xunder(c, b + dv), long_ok, short_ok)


# ------------------------------------------------------------------ 3. Multi-Step Vegas SuperTrend (SXtas3lS)
def run_vst(name, df, mm, tag, rows=None, verbose=True, base=5.0, adj=5.0, win=100, long_ok=True, short_ok=True, **extra):
    """Supertrend sobre hlc3 com ATR10 e multiplicador base + ajuste x largura do canal Vegas (SMA100 +/- 1 desvio);
    sempre posicionado e inverte (os TPs parciais ficaram de fora)."""
    o, h, l, c = ohlc(df); hlc3 = (h + l + c) / 3; vm = T.sma(c, win); w = 2 * stdev(c, win)
    m = base + adj * (w / vm); a = T.atr_rma(h, l, c, 10); su = hlc3 - m * a; sl_ = hlc3 + m * a
    n = len(c); tr = np.zeros(n); pu = NAN; pl = NAN; t = 1
    for i in range(n):
        if su[i] != su[i]: continue
        pu = su[i] if pu != pu else pu; pl = sl_[i] if pl != pl else pl
        t = 1 if c[i] > pl else (-1 if c[i] < pu else t)
        u = max(su[i], pu) if t == 1 else su[i]; lo = min(sl_[i], pl) if t == -1 else sl_[i]
        pu, pl = u, lo; tr[i] = t
    return R(name, df, mm, tag, rows, verbose, extra, tr == 1, tr == -1, long_ok, short_ok)


# ------------------------------------------------------------------ 4. Simple way to beat the market (vrFq8cGn)
def run_btm(name, df, mm, tag, rows=None, verbose=True, pct=95, win=100, long_ok=True, short_ok=False, **extra):
    """So long: comprado enquanto a vol historica (desvio de 10 dos log-retornos) fica abaixo do percentil 95 das
    ultimas 100 barras; acima zera."""
    o, h, l, c = ohlc(df); hv = stdev(np.log(c / sh(c)), 10)
    q = pd.Series(hv).rolling(win).quantile(pct / 100, interpolation='lower').to_numpy()
    p = np.where(q != q, 0, np.where(hv >= q, 0, 1))
    return run_g(name, df, posflat(df, mm, p, True, False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Combo 123 Reversal & N Bars Down (PmEilDJm)
def run_c123(name, df, mm, tag, rows=None, verbose=True, fiel=True, long_ok=True, short_ok=True, **extra):
    """123 Reversal (Stoch 14, D 3, nivel 50). No script o N Bars Down vira -1 para sempre depois do primeiro disparo,
    entao a combinacao so vende (123 = -1) e zera no resto (fiel); 'so123' usa o 123 sozinho, posicao +1/-1."""
    o, h, l, c = ohlc(df); f = stoch(c, h, l, 14); s = T.sma(f, 3); n = len(c); p = np.zeros(n)
    up = (sh(c, 2) < sh(c)) & (c > sh(c)) & (f < s) & (f > 50); dn = (sh(c, 2) > sh(c)) & (c < sh(c)) & (f > s) & (f < 50)
    for i in range(1, n):
        p[i] = 1 if up[i] else (-1 if dn[i] else p[i - 1])
    if fiel:
        cnt = np.zeros(n); seen = np.zeros(n, bool)
        for i in range(1, n):
            cnt[i] = cnt[i - 1] + 1 if c[i - 1] <= o[i - 1] else 0
            seen[i] = seen[i - 1] or cnt[i] >= 4
        p = np.where(seen & (p == -1), -1, 0)
        return run_g(name, df, posflat(df, mm, p, long_ok, short_ok), tag, rows, verbose, extra)
    return run_g(name, df, posflat(df, mm, p, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Pinbar (QtCWpUWb)
def run_pin(name, df, mm, tag, rows=None, verbose=True, pm=2.0, lm=1.0, long_ok=True, short_ok=False, **extra):
    """Pinbar de alta (corpo nos 30% de cima, minima abaixo da anterior) compra sem posicao; alvo = entrada + 2x o
    tamanho da vela, stop = minima x (1 - metade do % do alvo); espelho no short (trailing do script trocado por alvo)."""
    o, h, l, c = ohlc(df); cd = h - l; hl2 = (h + l) / 2
    L = (c > hl2) & (o > hl2) & (c > h - 0.3 * cd) & (o > h - 0.3 * cd) & (l < sh(l))
    S = (c < hl2) & (o < hl2) & (c < l + 0.3 * cd) & (o < l + 0.3 * cd) & (h > sh(h))
    with np.errstate(divide='ignore', invalid='ignore'):
        tpl = c + cd * pm; pl = (tpl / c - 1) / pm * lm; tps = c - cd * pm; ps = (c / tps - 1) / pm * lm
    res = gsim(df, mm, L, S, SLL=l * (1 - pl), TPL=tpl, SLS=h * (1 + ps), TPS=tps, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. Trend Entry 0 (market structure) (W6Xttkiv)
def run_mst(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=False, **extra):
    """Estrutura de mercado: em baixa, close acima da maxima de referencia vira alta (compra); em alta, close abaixo da
    minima de referencia vira baixa (fecha; com os dois lados, inverte). A referencia e a vela do ultimo extremo."""
    o, h, l, c = ohlc(df); n = len(c); cu = np.zeros(n, bool); cdn = cu.copy()
    up = c[0] > o[0]; shh, sll = h[0], l[0]
    for i in range(1, n):
        if not up:
            if c[i] > shh: up = True; cu[i] = True; shh, sll = h[i], l[i]
            if not cu[i] and l[i] <= sll: shh, sll = h[i], l[i]
        if up:
            if c[i] < sll: up = False; cdn[i] = True; shh, sll = h[i], l[i]
            if not cdn[i] and h[i] >= shh: shh, sll = h[i], l[i]
    return R(name, df, mm, tag, rows, verbose, extra, cu, cdn, long_ok, short_ok)


# ------------------------------------------------------------------ 8. RSI Alligator (sfEGsYBL)
def run_ral(name, df, mm, tag, rows=None, verbose=True, sl=0.10, long_ok=True, short_ok=True, **extra):
    """RSI 13 (ou 5) cruzando acima do RSI 34 com o outro acima compra, espelho vende; inverte; long com stop de 10%
    e alvo de 90%."""
    o, h, l, c = ohlc(df); r5, r13, r34 = wilder_rsi(c, 5), wilder_rsi(c, 13), wilder_rsi(c, 34)
    L = (T.xover(r13, r34) & (r5 > r34)) | (T.xover(r5, r34) & (r13 > r34))
    S = (T.xunder(r13, r34) & (r5 < r34)) | (T.xunder(r5, r34) & (r13 < r34))
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok, SLL=c * (1 - sl), TPL=c * 1.9)


# ------------------------------------------------------------------ 9. Super Momentum (jjBHYafE)
def rmi(c, n, m):
    d = c - sh(c, m); up = T.rma_nan(np.fmax(d, 0), n); dn = T.rma_nan(-np.fmin(d, 0), n)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(dn == 0, 100, np.where(up == 0, 0, 100 - 100 / (1 + up / dn)))


def run_sms(name, df, mm, tag, rows=None, verbose=True, cl=9, long_ok=True, short_ok=True, **extra):
    """CMO 9 (+50) cruzando acima de 25 com RMI 8/3 < 37, 12/3 < 37 e 30/53 < 24 (RMIs de 520 so filtram o aquecimento)
    compra; CMO cruzando abaixo de 75 com RMIs acima de 57/72/46 vende e inverte (filtro de lucro minimo 0 ignorado)."""
    o, h, l, c = ohlc(df); dm = c - sh(c)
    s1 = roll(np.fmax(dm, 0), cl).sum().to_numpy(); s2 = roll(-np.fmin(dm, 0), cl).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        ch = 100 * (s1 - s2) / (s1 + s2) + 50
    r1, r2, r3, r4 = rmi(c, 8, 3), rmi(c, 12, 3), rmi(c, 30, 53), rmi(c, 520, 137)
    L = T.xover(ch, 0 * c + 25) & (r1 < 37) & (r2 < 37) & (r3 < 24) & (r4 < 100) & (r4 > 0)
    S = T.xunder(ch, 0 * c + 75) & (r1 > 57) & (r2 > 72) & (r3 > 46) & (r4 > 0) & (r4 < 100)
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 10. RSI 2 com filtro de tendencia (Be5GdJIr)
def run_rs2(name, df, mm, tag, rows=None, verbose=True, ts=0.01, long_ok=True, short_ok=True, **extra):
    """EMA50 > EMA200, close acima da EMA200 e RSI2 < 10 compra; espelho com RSI2 > 90 vende; inverte; trailing de 1%
    sobre a maxima (minima) desde a entrada, atualizado no fechamento."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 2); f, s = ema(c, 50), ema(c, 200)
    L = (f > s) & (c > s) & (r < 10); S = (f < s) & (c < s) & (r > 90)
    return run_trl(name, df, tag, rows, verbose, extra, L, S, TRL=h * (1 - ts), TRS=l * (1 + ts), rev=True,
                   long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 11. Donchian Channel stop entries (ZZ0T9Wc7)
def run_dch(name, df, mm, tag, rows=None, verbose=True, n=20, long_ok=True, short_ok=True, **extra):
    """Stop de compra na maxima de 20 (com a barra atual) e de venda na minima de 20; sempre posicionado e inverte;
    so comprado: o stop de venda fecha."""
    o, h, l, c = ohlc(df); up, dn = hh(h, n), ll(l, n)
    return run_stp(name, df, tag, rows, verbose, extra, up, dn, LX=None if short_ok else dn, long_ok=long_ok,
                   short_ok=short_ok)


# ------------------------------------------------------------------ 12. Keltner SL/TP (eH0FxdMp)
def run_kel(name, df, mm, tag, rows=None, verbose=True, mult=1.0, sl=0.20, long_ok=True, short_ok=True, **extra):
    """EMA9 +/- 1 ATR19: close cruzando acima da banda de cima compra, abaixo da de baixo vende (a ordem stop um tick
    acima do close vira mercado); inverte; stop de 20% e alvo de 20,3%."""
    o, h, l, c = ohlc(df); m = ema(c, 9); a = T.atr_rma(h, l, c, 19)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(c, m + mult * a), T.xunder(c, m - mult * a), long_ok,
             short_ok, slp=sl, tpp=sl + 0.003)


# ------------------------------------------------------------------ 13. Linear Regression Channel Breakout (diTCC7a5)
def run_lrb(name, df, mm, tag, rows=None, verbose=True, n=100, long_ok=True, short_ok=True, **extra):
    """Close cruzando acima da linreg 100 das maximas compra, abaixo da linreg das minimas vende, so sem posicao; o long
    fecha ao cruzar abaixo da linreg das maximas, o short ao cruzar acima da das minimas."""
    o, h, l, c = ohlc(df); a, b = linreg(h, n), linreg(l, n)
    res = gsim(df, mm, T.xover(c, a), T.xunder(c, b), T.xunder(c, a), T.xover(c, b), rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Volatility Range Breakout (2cnPhDGs)
def run_vrb(name, df, mm, tag, rows=None, verbose=True, n=100, long_ok=True, short_ok=True, **extra):
    """Vol = 2(max-min)/(max+min) do close em 100; bandas = media de 100 de close x (1 +/- vol) (o peso do wma do script
    e constante, entao vira SMA). Maxima cruzando a banda de cima compra, minima cruzando a de baixo vende; close
    cruzando o meio fecha; entradas invertem (uma unidade, sem a piramidacao)."""
    o, h, l, c = ohlc(df); a, b = hh(c, n), ll(c, n); v = 2 * (a - b) / (a + b)
    hb, lb = T.sma(c * (1 + v), n), T.sma(c * (1 - v), n); md = (hb + lb) / 2
    L = T.xover(h, hb); S = T.xunder(l, lb) & ~L
    res = gsim(df, mm, L, S, T.xunder(c, md), T.xover(c, md), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Multi Moving Average Crossing (DDnx7g70)
def run_mma(name, df, mm, tag, rows=None, verbose=True, p=(9, 50, 100), long_ok=True, short_ok=False, **extra):
    """So long: SMA50 cruzando acima da SMA100 compra; SMA9 cruzando abaixo da SMA50 fecha. Os dois lados: espelho no
    short, inverte."""
    o, h, l, c = ohlc(df); f, m, s = (T.sma(c, x) for x in p)
    res = gsim(df, mm, T.xover(m, s), T.xunder(m, s), T.xunder(f, m), T.xover(f, m), rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. ATR and T3 (XUUH8oiL)
def t3(c, n, v):
    e1 = ema(c, n); e2 = ema(e1, n); e3 = ema(e2, n); e4 = ema(e3, n); e5 = ema(e4, n); e6 = ema(e5, n)
    return (-v ** 3) * e6 + (3 * v * v + 3 * v ** 3) * e5 + (-6 * v * v - 3 * v - 3 * v ** 3) * e4 + \
        (1 + 3 * v + v ** 3 + 3 * v * v) * e3


def run_at3(name, df, mm, tag, rows=None, verbose=True, pct=0.05, long_ok=True, short_ok=False, **extra):
    """So long (padrao): close acima do Supertrend 5/5, do Supertrend 1/1 e do T3 25 (0,72) compra; hl2 abaixo do
    T3 x 0,95 fecha. Os dois lados: espelho, entradas invertem."""
    o, h, l, c = ohlc(df); t = t3(c, 25, 0.72); a, b = st_old(h, l, c, 5, 5), st_old(h, l, c, 1, 1); hl2 = (h + l) / 2
    L = (c > a) & (c > b) & (c > t); S = (c < a) & (c < b) & (c < t)
    res = gsim(df, mm, L, S, hl2 < t * (1 - pct), hl2 > t * (1 + pct), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. ATR Reversed (beTGXcYr)
def run_atr(name, df, mm, tag, rows=None, verbose=True, p=(5, 3.5), long_ok=True, short_ok=True, **extra):
    """Trailing de 3,5 ATR5 (Vervoort) ao contrario: close cruzando acima do trailing vende, abaixo compra; sempre
    posicionado."""
    o, h, l, c = ohlc(df); t = atr_trail(c, p[1] * T.atr_rma(h, l, c, p[0])); pt = sh(t)
    up = (sh(c) < pt) & (c > pt); dn = (sh(c) > pt) & (c < pt)
    return R(name, df, mm, tag, rows, verbose, extra, dn, up, long_ok, short_ok)


# ------------------------------------------------------------------ 18. Squeeze Momentum (G40dtEbK)
def run_sqz(name, df, mm, tag, rows=None, verbose=True, ef=100, long_ok=True, short_ok=True, **extra):
    """Squeeze do LazyBear (BB 20 com 1,5 desvio, como no codigo, e KC 20 x 1,5 TR): saida do squeeze com momentum
    subindo, acima da minima de 100 do momentum, close subindo e acima da EMA100 compra; momentum caindo fecha. Short:
    entrada no squeeze com o espelho; momentum subindo fecha. Alavancagem 8x do script trocada por 1x."""
    o, h, l, c = ohlc(df); b = T.sma(c, 20); dv = 1.5 * stdev(c, 20); pc = sh(c)
    tr = np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc))); rm = T.sma(tr, 20)
    on = (b - dv > b - 1.5 * rm) & (b + dv < b + 1.5 * rm); off = (b - dv < b - 1.5 * rm) & (b + dv > b + 1.5 * rm)
    v = linreg(c - ((hh(h, 20) + ll(l, 20)) / 2 + b) / 2, 20); v1 = sh(v); e = ema(c, ef)
    gray = off & ~on; black = on
    L = gray & sh(black.astype(float)).astype(bool) & (v > v1) & (v > sh(ll(v, 100))) & (c > pc) & (c > e)
    S = black & sh(gray.astype(float)).astype(bool) & (v < v1) & (v < sh(hh(v, 100))) & (c < pc) & (c < e)
    res = gsim(df, mm, L, S & ~L, v < v1, v > v1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Candle Breakout (YJjFy8kD)
def run_cbo(name, df, mm, tag, rows=None, verbose=True, hr=13, rr=1.0, long_ok=True, short_ok=True, **extra):
    """A vela que abre as 13:00 UTC arma a caixa; o primeiro close acima da maxima compra (stop na minima da caixa,
    alvo rr x risco), abaixo da minima vende (espelho); uma entrada por caixa, so sem posicao."""
    o, h, l, c = ohlc(df); n = len(c); ix = df.index
    first = (ix.hour == hr) & (ix.minute == 0); L = np.zeros(n, bool); S = L.copy()
    bh = bl = NAN; w = False
    for i in range(n):
        if first[i]: bh, bl, w = h[i], l[i], True
        elif w and c[i] > bh: L[i] = True; w = False
        elif w and c[i] < bl: S[i] = True; w = False
    BH = pd.Series(np.where(first, h, NAN)).ffill().to_numpy(); BL = pd.Series(np.where(first, l, NAN)).ffill().to_numpy()
    res = gsim(df, mm, L, S, SLL=BL, TPL=c + (c - BL) * rr, SLS=BH, TPS=c - (BH - c) * rr, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. MACD Short/Long TVIO (X4c5lTKF)
def run_mbd(name, df, mm, tag, rows=None, verbose=True, sl=0.21, long_ok=True, short_ok=True, **extra):
    """MACD 13/19 cruzando acima de zero compra; MACD 11/20 cruzando abaixo de zero (uma barra de atraso) vende;
    inverte; short com stop de 21% e alvo de 20%. So comprado: MACD 13/19 cruzando abaixo de zero fecha."""
    o, h, l, c = ohlc(df); ml = ema(c, 13) - ema(c, 19); ms = ema(c, 11) - ema(c, 20)
    L = T.xover(ml, 0 * c)
    if not short_ok:
        res = gsim(df, mm, L, Z(c), T.xunder(ml, 0 * c), rev=False, short_ok=False)
        return run_g(name, df, res, tag, rows, verbose, extra)
    S = sh(T.xunder(ms, 0 * c).astype(float)) > 0
    res = gsim(df, mm, L, S & ~L, SLS=c * (1 + sl), TPS=c * (1 - sl + 0.01), rev=True, long_ok=long_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


side2 = ('ambos', 'long')
sk = lambda s: dict(short_ok=s == 'ambos')
pr = lambda v: '/'.join(f'{x:g}' for x in v)


def g2(key, vals, fmt):
    return [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)]


def g4(k1, v1, k2, v2, fmt):
    return [(fmt(a, b), {k1: a, k2: b}) for a, b in itertools.product(v1, v2)]


GRID = {
    'sre': (run_sre, "1. Stoch RSI Crossover + EMA", 'tp1.5/sl2 ambos', g2('pf', (1.5, 3.0), lambda v: f'tp{v:g}/sl2')),
    'kbb': (run_kbb, "2. Kozlod BB", 'bb55x4 ambos', g4('n', (55, 20), 'mult', (4.0, 2.0), lambda a, b: f'bb{a}x{b:g} ambos')
            + [('bb55x4 long', dict(short_ok=False)), ('bb20x2 long', dict(n=20, mult=2.0, short_ok=False))]),
    'vst': (run_vst, "3. Multi-Step Vegas SuperTrend", 'b5 ambos', g2('base', (5.0, 2.0), lambda v: f'b{v:g}')),
    'btm': (run_btm, "4. Beat the market (filtro de vol)", 'p95/w100', g4('pct', (95, 80), 'win', (100, 250),
                                                                           lambda a, b: f'p{a}/w{b}')),
    'c123': (run_c123, "5. Combo 123 Reversal & N Bars Down", 'fiel ambos',
             [('so123 ambos', dict(fiel=False)), ('so123 long', dict(fiel=False, short_ok=False))]),
    'pin': (run_pin, "6. Pinbar", 'pm2 long', g2('pm', (2.0, 3.0), lambda v: f'pm{v:g}')),
    'mst': (run_mst, "7. Trend Entry 0 (estrutura)", 'long', [('ambos', dict(short_ok=True))]),
    'ral': (run_ral, "8. RSI Alligator", 'sl10 ambos', g2('sl', (0.10, 0.03), lambda v: f'sl{v * 100:g}')),
    'sms': (run_sms, "9. Super Momentum", 'cmo9 ambos', g2('cl', (9, 14), lambda v: f'cmo{v}')),
    'rs2': (run_rs2, "10. RSI 2 + tendencia, trailing", 'ts1 ambos', g2('ts', (0.01, 0.03), lambda v: f'ts{v * 100:g}')),
    'dch': (run_dch, "11. Donchian stop entries", 'n20 ambos', g2('n', (20, 55), lambda v: f'n{v}')),
    'kel': (run_kel, "12. Keltner SL/TP", 'k1/sl20 ambos', g4('mult', (1.0, 2.0), 'sl', (0.20, 0.05),
                                                              lambda a, b: f'k{a:g}/sl{b * 100:g} ambos')
            + [('k1/sl20 long', dict(short_ok=False)), ('k2/sl20 long', dict(mult=2.0, short_ok=False))]),
    'lrb': (run_lrb, "13. Linear Regression Channel Breakout", 'n100 ambos', g2('n', (100, 50), lambda v: f'n{v}')),
    'vrb': (run_vrb, "14. Volatility Range Breakout", 'n100 ambos', g2('n', (100, 50), lambda v: f'n{v}')),
    'mma': (run_mma, "15. Multi Moving Average Crossing", '9/50/100 long', g2('p', ((9, 50, 100), (5, 20, 50)), pr)),
    'at3': (run_at3, "16. ATR and T3", 'p5 long', g2('pct', (0.05, 0.02), lambda v: f'p{v * 100:g}')),
    'atr': (run_atr, "17. ATR Reversed", '5/3.5 ambos', g2('p', ((5, 3.5), (14, 2.0)), pr)),
    'sqz': (run_sqz, "18. Squeeze Momentum", 'e100 ambos', g2('ef', (100, 50), lambda v: f'e{v}')),
    'cbo': (run_cbo, "19. Candle Breakout 13h UTC", 'h13/rr1 ambos', g4('hr', (13, 8), 'rr', (1.0, 2.0),
                                                                       lambda a, b: f'h{a}/rr{b:g} ambos')
            + [('h13/rr1 long', dict(short_ok=False)), ('h13/rr2 long', dict(rr=2.0, short_ok=False))]),
    'mbd': (run_mbd, "20. MACD Short/Long TVIO", 'sl21 ambos', g2('sl', (0.21, 0.05), lambda v: f'sl{v * 100:g}')),
}
TF_EST = {'cbo': ('15min', '30min', '1h')}   # a caixa e a vela das 13:00; em 4h e 1D ela nao existe


def KW(est, cfg):
    """kwargs de uma celula da grade a partir do rotulo (usado por study_veredito_lote)."""
    fn, _, dflt, combos = GRID[est]
    return {} if cfg == dflt else dict(combos)[cfg]


def main(nomes, ests=None):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        for est, (fn, label, default_cfg, combos) in GRID.items():
            if ests and est not in ests: continue
            print(f"\n### {label}", flush=True)
            for tf in TF_EST.get(est, TFS):
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    if cfg == default_cfg: continue
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote36')


if __name__ == '__main__':
    a = sys.argv[1:]
    main([x for x in a if '=' not in x] or ['xau', 'us100', 'wti', 'btc', 'eth'],
         next((x.split('=')[1].split(',') for x in a if x.startswith('est=')), None))
