"""Lote 37 do TradingView (2026-10-27): 20 estrategias nos 5 ativos, posicoes 956 a 1000 da lista, grade completa como
nos lotes 26 a 36 (ver docs/LOTE37_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote37.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch, dmi
from study_tvlote9 import summary
from study_tvlote20 import sh
from study_tvlote22 import meandev
from study_tvlote24 import cci
from study_tvlote25 import posflat, wilder_rsi, hh, ll, Z, NAN
from study_tvlote30 import R, supertrend


def bsh(x, k=1):
    return sh(np.asarray(x, float), k) > 0


# ------------------------------------------------------------------ 1. Laguerre RSI (vWG3tMJh)
def run_lag(name, df, mm, tag, rows=None, verbose=True, alpha=0.2, long_ok=True, short_ok=True, **extra):
    """Filtro de Laguerre (alpha 0,2): cu cruzando acima de cd compra, abaixo vende; inverte."""
    o, h, l, c = ohlc(df); g = 1 - alpha; n = len(c)
    L0 = np.zeros(n); L1 = L0.copy(); L2 = L0.copy(); L3 = L0.copy()
    for i in range(n):
        p0, p1, p2, p3 = (L0[i - 1], L1[i - 1], L2[i - 1], L3[i - 1]) if i else (0., 0., 0., 0.)
        L0[i] = alpha * c[i] + g * p0; L1[i] = -g * L0[i] + p0 + g * p1
        L2[i] = -g * L1[i] + p1 + g * p2; L3[i] = -g * L2[i] + p2 + g * p3
    cu = np.fmax(L0 - L1, 0) + np.fmax(L1 - L2, 0) + np.fmax(L2 - L3, 0)
    cd = np.fmax(L1 - L0, 0) + np.fmax(L2 - L1, 0) + np.fmax(L3 - L2, 0)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(cu, cd), T.xunder(cu, cd), long_ok, short_ok)


# ------------------------------------------------------------------ 2. Chande Kroll Stop (GoHLj2XP)
def run_ckr(name, df, mm, tag, rows=None, verbose=True, n=21, am=3.0, long_ok=True, short_ok=False, **extra):
    """So long: close cruzando acima de (minima de 21 + 3 ATR10) com close acima da SMA21 compra; close abaixo de
    (maxima de 21 - 3 ATR10) fecha (o tamanho pela minima de 1560 barras virou 1 unidade)."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 10); hs = hh(h, n) - am * a; ls_ = ll(l, n) + am * a
    res = gsim(df, mm, T.xover(c, ls_) & (c > T.sma(c, 21)), Z(c), c < hs, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. MACD + DMI com Volatility Stop (nD83sb4E)
def vstop(c, a):
    n = len(c); st = np.full(n, NAN); up = True; mx = mn = c[0]; s = 0.0
    for i in range(n):
        atrm = a[i] if a[i] == a[i] else 0.0
        mx = max(mx, c[i]); mn = min(mn, c[i])
        s = max(s, mx - atrm) if up else min(s, mn + atrm)
        nu = c[i] - s >= 0
        if nu != up:
            mx = mn = c[i]; s = mx - atrm if nu else mn + atrm
        up = nu; st[i] = s
    return st


def run_mdv(name, df, mm, tag, rows=None, verbose=True, tp=0.03, long_ok=True, short_ok=False, **extra):
    """So long: MACD 12/26/9 cruzando acima do sinal com +DI14 > -DI14 compra; alvo de 3% ou close cruzando abaixo do
    Volatility Stop (20, 2 ATR) fecha."""
    o, h, l, c = ohlc(df); m = ema(c, 12) - ema(c, 26); s = ema(m, 9); p, mi, _ = dmi(h, l, c, 14)
    vs = vstop(c, 2.0 * T.atr_rma(h, l, c, 20))
    res = gsim(df, mm, T.xover(m, s) & (p > mi), Z(c), T.xunder(c, vs), tpp=tp, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Big Bar (uuinZwsR)
def run_bbr(name, df, mm, tag, rows=None, verbose=True, am=4.0, long_ok=True, short_ok=True, **extra):
    """Vela grande (range >= 2x a media de 10 e corpo > 50% do range) de baixa seguida de vela de alta compra (espelho
    vende); stop em ohlc4 - 4 ATR14 da barra do sinal, alvo 1x o risco; inverte."""
    o, h, l, c = ohlc(df); rg = h - l; big = (rg >= 2 * T.sma(rg, 10)) & (np.abs(c - o) > 0.5 * rg)
    L = bsh(big & (c < o)) & (c > o); S = bsh(big & (c > o)) & (c < o)
    a = am * T.atr_rma(h, l, c, 14); o4 = (o + h + l + c) / 4; sl_l = o4 - a; sl_s = o4 + a
    res = gsim(df, mm, L, S, SLL=sl_l, TPL=c + (c - sl_l), SLS=sl_s, TPS=c - (sl_s - c), rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Mean-Reversion Swing (LIcdcfU8)
def run_mrs(name, df, mm, tag, rows=None, verbose=True, n=20, pb=0.5, long_ok=True, short_ok=True, **extra):
    """Canal de 20: nova maxima arma o long, nova minima o short; close cruzando o recuo de 50% entre a ultima maxima e
    a ultima minima a favor da SMA50 entra; alvo na banda do lado do trade, stop na outra (niveis da barra do sinal)."""
    o, h, l, c = ohlc(df); ub, lb = hh(h, n), ll(l, n); tr = T.sma(c, 50); N = len(c)
    lok = np.zeros(N, bool); sok = lok.copy(); trig = np.full(N, NAN); lr = hr = 0.0; a = b = a2 = False
    for i in range(N):
        if l[i] == lb[i]: lr = l[i]; a = False; b = True; a2 = False
        if h[i] == ub[i]: hr = h[i]; a = True; b = False; a2 = True
        lok[i] = a; sok[i] = b; trig[i] = hr - pb * (hr - lr) if a2 else lr + pb * (hr - lr)
    L = bsh(lok) & lok & T.xover(c, trig) & (c > tr); S = bsh(sok) & sok & T.xunder(c, trig) & (c < tr)
    res = gsim(df, mm, L, S, SLL=lb, TPL=ub, SLS=ub, TPS=lb, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. DMI Modified (usbHOChM)
def run_dmm(name, df, mm, tag, rows=None, verbose=True, n=9, long_ok=True, short_ok=True, **extra):
    """+DI e -DI feitos com a variacao da maxima de 9 e da minima de 9, diferenca suavizada por EMA9: positiva e
    subindo compra, negativa e caindo vende; inverte."""
    o, h, l, c = ohlc(df); up = np.diff(hh(h, n), prepend=NAN); dn = -np.diff(ll(l, n), prepend=NAN)
    tr = T.atr_rma(h, l, c, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        p = 100 * T.rma_nan(np.where((up > dn) & (up > 0), up, 0.0), n) / tr
        m = 100 * T.rma_nan(np.where((dn > up) & (dn > 0), dn, 0.0), n) / tr
    r = ema(p - m, 9); r1 = sh(r)
    return R(name, df, mm, tag, rows, verbose, extra, (r > 0) & (r > r1), (r < 0) & (r < r1), long_ok, short_ok)


# ------------------------------------------------------------------ 7. Hull Suite (NhBn8wuA)
def run_hul(name, df, mm, tag, rows=None, verbose=True, n=55, long_ok=True, short_ok=False, **extra):
    """HMA 55 acima da de 2 barras atras compra, abaixo vende (padrao do script: so long, venda fecha)."""
    o, h, l, c = ohlc(df); x = T.hma(c, n); x2 = sh(x, 2)
    return R(name, df, mm, tag, rows, verbose, extra, x > x2, x < x2, long_ok, short_ok)


# ------------------------------------------------------------------ 8. IU 4 Bar UP (fUiBVHl7)
def run_b4u(name, df, mm, tag, rows=None, verbose=True, f=1.0, long_ok=True, short_ok=False, **extra):
    """So long: 4 velas de alta seguidas com close acima do Supertrend (14, 1) compra; close abaixo dele fecha."""
    o, h, l, c = ohlc(df); st, _ = supertrend(h, l, c, 14, f); g = (c > o).astype(float)
    L = (g + sh(g) + sh(g, 2) + sh(g, 3) == 4) & (c > st)
    res = gsim(df, mm, L, Z(c), c < st, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. 3x Supertrend + Stoch RSI (Kls9JTiM)
def run_sts(name, df, mm, tag, rows=None, verbose=True, tpm=1.6, slm=2.7, long_ok=True, short_ok=True, **extra):
    """Acima da EMA200, dois Supertrends vizinhos (10/1, 11/2, 12/3) em alta por 2 barras e K cruzando D no Stoch RSI
    compra (espelho vende), so sem posicao; alvo 1,6 ATR14 e stop 2,7 ATR14."""
    o, h, l, c = ohlc(df); dd = [supertrend(h, l, c, n, m)[1] for n, m in ((10, 1), (11, 2), (12, 3))]
    u = [(d == -1) & (sh(d) == -1) for d in dd]; w = [(d == 1) & (sh(d) == 1) for d in dd]
    r = wilder_rsi(c, 14); k = T.sma(stoch(r, r, r, 14), 3); d_ = T.sma(k, 3); e = ema(c, 200); a = T.atr_rma(h, l, c, 14)
    L = (c > e) & ((u[0] & u[1]) | (u[1] & u[2])) & T.xover(k, d_)
    S = (c < e) & ((w[0] & w[1]) | (w[1] & w[2])) & T.xunder(k, d_)
    res = gsim(df, mm, L, S, SLL=c - slm * a, TPL=c + tpm * a, SLS=c + slm * a, TPS=c - tpm * a, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Combo 123 Reversal & Rainbow Oscillator (2JTpVVrO)
def run_c12r(name, df, mm, tag, rows=None, verbose=True, lro=2, long_ok=True, short_ok=True, **extra):
    """123 Reversal (Stoch 14 sem suavizar, D 3, nivel 50) e Rainbow Oscillator (10 SMAs encadeadas de 2, HHLL 10) do
    mesmo lado entram; discordando zera."""
    o, h, l, c = ohlc(df); f = stoch(c, h, l, 14); s = T.sma(f, 3); n = len(c); p = np.zeros(n)
    up = (sh(c, 2) < sh(c)) & (c > sh(c)) & (f < s) & (f > 50); dn = (sh(c, 2) > sh(c)) & (c < sh(c)) & (f > s) & (f < 50)
    for i in range(1, n):
        p[i] = 1 if up[i] else (-1 if dn[i] else p[i - 1])
    ms = []; x = c
    for _ in range(10):
        x = T.sma(x, lro); ms.append(x)
    with np.errstate(divide='ignore', invalid='ignore'):
        rbo = 100 * (c - np.mean(ms, 0)) / (hh(c, 10) - ll(c, 10))
    q = pd.Series(np.sign(rbo)).replace(0, np.nan).ffill().fillna(0).to_numpy()
    pos = np.where((p == 1) & (q == 1), 1, np.where((p == -1) & (q == -1), -1, 0))
    return run_g(name, df, posflat(df, mm, pos, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. HL MovingAvg2Line Cross (nhG8OBiD)
def run_hle(name, df, mm, tag, rows=None, verbose=True, n=9, long_ok=True, short_ok=True, **extra):
    """Close acima da EMA9 das maximas compra, abaixo da EMA9 das minimas vende; inverte (as saidas do script apontam
    para uma entrada que nao existe e nunca disparam)."""
    o, h, l, c = ohlc(df)
    return R(name, df, mm, tag, rows, verbose, extra, c > ema(h, n), c < ema(l, n), long_ok, short_ok)


# ------------------------------------------------------------------ 12. Directional Movement Index + Ichimoku (snP0MRjI)
def mid(h, l, n):
    return (hh(h, n) + ll(l, n)) / 2


def run_dmx(name, df, mm, tag, rows=None, verbose=True, adx_min=25, long_ok=True, short_ok=True, **extra):
    """ADX14 (DI 7) passando de 25 com +DI > -DI compra (espelho vende); o long sai quando a forca acaba ou a nuvem e
    'verde' (A < B, como no script) e grossa (>= 14% da mais grossa); o short sai quando a forca acaba ou a nuvem e
    verde."""
    o, h, l, c = ohlc(df); tk, kj = mid(h, l, 9), mid(h, l, 26); sa = mid(h, l, 52); sb = (tk + kj) / 2
    sa26, sb26 = sh(sa, 26), sh(sb, 26); green = sa26 < sb26
    with np.errstate(divide='ignore', invalid='ignore'):
        th = np.abs(sa26 - sb26) * 100 / np.where(green, sa26, sb26)
    thick = th >= pd.Series(th).rolling(10000, min_periods=1).max().to_numpy() * 0.14
    up = np.diff(h, prepend=NAN); dn = -np.diff(l, prepend=NAN); tr = T.atr_rma(h, l, c, 7)
    with np.errstate(divide='ignore', invalid='ignore'):
        p = 100 * T.rma_nan(np.where((up > dn) & (up > 0), up, 0.0), 7) / tr
        m = 100 * T.rma_nan(np.where((dn > up) & (dn > 0), dn, 0.0), 7) / tr
        adx = 100 * T.rma_nan(np.abs(p - m) / np.where(p + m == 0, 1, p + m), 14)
    su = (adx > adx_min) & (p > m); sd = (adx > adx_min) & (p < m)
    su1, sd1 = bsh(su), bsh(sd)
    res = gsim(df, mm, su & ~su1, sd & ~sd1, (su1 & ~su) | (thick & green), (sd1 & ~sd) | green, rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Reversal Catcher (PJb1qh7h)
def run_rvc(name, df, mm, tag, rows=None, verbose=True, bm=1.5, long_ok=True, short_ok=True, **extra):
    """Maxima anterior abaixo da BB 20 x 1,5 de baixo, close de volta dentro das bandas, HH/HL com close acima da maxima
    anterior, RSI14 cruzando acima de 30 e EMA21 < EMA50 compra (espelho vende); stop na minima anterior, alvo na
    banda de cima se a maxima passou do meio, senao no meio (sem fechamento no fim do dia: mercado 24h)."""
    o, h, l, c = ohlc(df); b = T.sma(c, 20); dv = bm * T.stdev_pop(c, 20); bu, bl = b + dv, b - dv
    r = wilder_rsi(c, 14); e21, e50 = ema(c, 21), ema(c, 50)
    L = (sh(h) < sh(bl)) & (c > bl) & (c < bu) & (l > sh(l)) & (h > sh(h)) & (c > sh(h)) & T.xover(r, 0 * c + 30) & (e21 < e50)
    S = (sh(l) > sh(bu)) & (c < bu) & (c > bl) & (l < sh(l)) & (h < sh(h)) & (c < sh(l)) & T.xunder(r, 0 * c + 70) & (e21 > e50)
    res = gsim(df, mm, L, S, SLL=sh(l), TPL=np.where(h >= b, bu, b), SLS=sh(h), TPS=np.where(l <= b, bl, b),
               rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Quantitative Trend Uptrend Long (I4FhUvyq)
def run_qts(name, df, mm, tag, rows=None, verbose=True, tp=0.02, sl=0.0175, long_ok=True, short_ok=False, **extra):
    """So long: close acima do close da barra que confirmou o ultimo pivo de alta (46/32, em close) compra; alvo de 2%
    e stop de 1,75%; volta a comprar enquanto a condicao vale."""
    o, h, l, c = ohlc(df); pv = T.pivothigh(c, 46, 32)
    v = pd.Series(np.where(pv, c, NAN)).ffill().to_numpy()
    res = gsim(df, mm, c > v, Z(c), slp=sl, tpp=tp, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. WMX Williams Fractals V4 (s1UnbQTF)
def run_wmx(name, df, mm, tag, rows=None, verbose=True, occ=3, long_ok=True, short_ok=True, **extra):
    """Fractais de 5 barras no close (as variantes com empates ficaram de fora); U = close na 4a mudanca anterior do
    fractal de alta, L idem no de baixa. Close cruzando acima de L com vela de alta compra, abaixo de U com vela de
    baixa vende; inverte."""
    o, h, l, c = ohlc(df); c1, c2, c3, c4 = sh(c), sh(c, 2), sh(c, 3), sh(c, 4)
    uf = (c4 < c2) & (c3 < c2) & (c1 < c2) & (c < c2); df_ = (c4 > c2) & (c3 > c2) & (c1 > c2) & (c > c2)
    U = T.valuewhen_prev(uf != bsh(uf), c, occ); Lv = T.valuewhen_prev(df_ != bsh(df_), c, occ)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(c, Lv) & (c > o), T.xunder(c, U) & (c < o),
             long_ok, short_ok)


# ------------------------------------------------------------------ 16. RSI Classic (Coinrule) (JMm04UG5)
def run_rsc(name, df, mm, tag, rows=None, verbose=True, lv=(30, 60), long_ok=True, short_ok=False, **extra):
    """So long: RSI14 abaixo de 30 compra, acima de 60 fecha."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 14)
    res = gsim(df, mm, r < lv[0], Z(c), r > lv[1], rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. OBV Accumulation/Distribution (FAnuuDAa)
def run_obv(name, df, mm, tag, rows=None, verbose=True, n=20, long_ok=True, short_ok=False, **extra):
    """So long: acumulado de volume x (close - close anterior)/(max - min) cruzando acima da EMA20 com vela de alta
    compra; cruzando abaixo com vela de baixa e close abaixo da minima anterior fecha."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        pt = np.nan_to_num(v * (c - np.nan_to_num(sh(c))) / (h - l), nan=0.0, posinf=0.0, neginf=0.0)
    a = np.cumsum(pt); e = ema(a, n); a1 = sh(a)
    L = T.xover(a, e) & (c > o) & (a > a1); X = T.xunder(a, e) & (c < o) & (a < a1) & (c < sh(l))
    res = gsim(df, mm, L, Z(c), X, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. Chaloke System (9ID5apv1)
def run_chk(name, df, mm, tag, rows=None, verbose=True, p=(9, 15, 24), long_ok=True, short_ok=True, **extra):
    """Linhas = EMA(9/15/24) - 1 ATR5 (com o close atual so quando ele e a maxima de 3, senao o close anterior): linha
    curta cruzando acima da media com close acima da curta compra; curta cruzando abaixo da longa ou close abaixo da
    longa vende; inverte."""
    o, h, l, c = ohlc(df); ax = T.atr_rma(h, l, c, 5); top = c == hh(c, 3)
    ln = [np.where(top, ema(c, n), sh(ema(c, n))) - ax for n in p]
    L = T.xover(ln[0], ln[1]) & (c > ln[0]); S = T.xunder(ln[0], ln[2]) | (c < ln[2])
    return R(name, df, mm, tag, rows, verbose, extra, L, S & ~L, long_ok, short_ok)


# ------------------------------------------------------------------ 19. Gold TDOW (zUMUafG8)
def run_tdw(name, df, mm, tag, rows=None, verbose=True, tdow=True, long_ok=True, short_ok=False, **extra):
    """So long: MACD 12/26/9 acima do sinal, Stoch 14/3 > 50 e RSI14 > 50 compra so em segunda, quarta e quinta (UTC);
    MACD abaixo do sinal fecha (o stop em dolares ficou de fora)."""
    o, h, l, c = ohlc(df); m = ema(c, 12) - ema(c, 26); s = ema(m, 9); k = T.sma(stoch(c, h, l, 14), 3)
    L = (m > s) & (k > 50) & (wilder_rsi(c, 14) > 50)
    if tdow: L &= np.isin(df.index.dayofweek, (0, 2, 3))
    res = gsim(df, mm, L, Z(c), m < s, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. RSI-CCI Fusion (cnILutZ3)
def run_rcf(name, df, mm, tag, rows=None, verbose=True, n=14, long_ok=True, short_ok=False, **extra):
    """z-score de RSI14 e CCI14 (meio a meio), reescalado; cruzando acima da banda de baixo (media 14 - 1 desvio)
    compra, abaixo da de cima fecha (com short: inverte)."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, n); cc = cci(c, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        z = 0.5 * (r - T.sma(r, n)) / T.stdev_pop(r, n) + 0.5 * (cc - T.sma(cc, n)) / T.stdev_pop(cc, n)
    rs = z * T.stdev_pop(z, n) + T.sma(z, n); m = T.sma(rs, n); d = T.stdev_pop(rs, n)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(rs, m - d), T.xunder(rs, m + d), long_ok, short_ok)


side2 = ('ambos', 'long')
sk = lambda s: dict(short_ok=s == 'ambos')
pr = lambda v: '/'.join(f'{x:g}' for x in v)


def g2(key, vals, fmt):
    return [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)]


def g4(k1, v1, k2, v2, fmt):
    return [(fmt(a, b), {k1: a, k2: b}) for a, b in itertools.product(v1, v2)]


GRID = {
    'lag': (run_lag, "1. Laguerre RSI", 'a0.2 ambos', g2('alpha', (0.2, 0.5), lambda v: f'a{v:g}')),
    'ckr': (run_ckr, "2. Chande Kroll Stop", 'n21/a3', g4('n', (21, 10), 'am', (3.0, 1.5), lambda a, b: f'n{a}/a{b:g}')),
    'mdv': (run_mdv, "3. MACD + DMI + Volatility Stop", 'tp3', [('tp10', dict(tp=0.10)), ('semtp', dict(tp=0.0))]),
    'bbr': (run_bbr, "4. Big Bar", 'a4 ambos', g2('am', (4.0, 2.0), lambda v: f'a{v:g}')),
    'mrs': (run_mrs, "5. Mean-Reversion Swing", 'n20 ambos', g2('n', (20, 50), lambda v: f'n{v}')),
    'dmm': (run_dmm, "6. DMI Modified", 'n9 ambos', g2('n', (9, 21), lambda v: f'n{v}')),
    'hul': (run_hul, "7. Hull Suite", 'n55 long', g2('n', (55, 180), lambda v: f'n{v}')),
    'b4u': (run_b4u, "8. IU 4 Bar UP", 'f1', [('f3', dict(f=3.0))]),
    'sts': (run_sts, "9. 3x Supertrend + Stoch RSI", 'tp1.6 ambos', g2('tpm', (1.6, 4.0), lambda v: f'tp{v:g}')),
    'c12r': (run_c12r, "10. Combo 123 + Rainbow Oscillator", 'ro2 ambos', g2('lro', (2, 5), lambda v: f'ro{v}')),
    'hle': (run_hle, "11. HL MovingAvg2Line Cross", 'n9 ambos', g2('n', (9, 21), lambda v: f'n{v}')),
    'dmx': (run_dmx, "12. DMI + nuvem Ichimoku", 'adx25 ambos', g2('adx_min', (25, 20), lambda v: f'adx{v}')),
    'rvc': (run_rvc, "13. Reversal Catcher", 'bb1.5 ambos', g2('bm', (1.5, 2.0), lambda v: f'bb{v:g}')),
    'qts': (run_qts, "14. Quantitative Trend (pivo)", 'tp2/sl1.75', [('tp6/sl3', dict(tp=0.06, sl=0.03))]),
    'wmx': (run_wmx, "15. WMX Williams Fractals", 'o3 ambos', g2('occ', (3, 1), lambda v: f'o{v}')),
    'rsc': (run_rsc, "16. RSI Classic (Coinrule)", '30/60', [('30/70', dict(lv=(30, 70))), ('20/60', dict(lv=(20, 60)))]),
    'obv': (run_obv, "17. OBV Acumulacao/Distribuicao", 'n20', [('n50', dict(n=50))]),
    'chk': (run_chk, "18. Chaloke System", '9/15/24 ambos', g2('p', ((9, 15, 24), (20, 50, 100)), pr)),
    'tdw': (run_tdw, "19. Gold TDOW (MACD+Stoch+RSI)", 'tdow', [('todos', dict(tdow=False))]),
    'rcf': (run_rcf, "20. RSI-CCI Fusion", 'n14 long', g2('n', (14, 30), lambda v: f'n{v}')),
}
TF_EST = {}


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
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote37')


if __name__ == '__main__':
    a = sys.argv[1:]
    main([x for x in a if '=' not in x] or ['xau', 'us100', 'wti', 'btc', 'eth'],
         next((x.split('=')[1].split(',') for x in a if x.startswith('est=')), None))
