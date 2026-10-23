"""Lote 31 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 a 30
(ver docs/LOTE31_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote31.py xau us100 wti btc eth
"""
import os, sys, itertools, math
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
from study_tvlote25 import posflat, wilder_rsi, hh, ll, ffill, Z, NAN, roll, run_loop
from study_tvlote26 import flat_pos
from study_tvlote29 import alma
from study_tvlote30 import R, K


def psar(h, l, c, start, inc, mx):
    """SAR do Pine: devolve (sar da barra, sar previsto para a barra seguinte, em alta)."""
    n = len(c); sar = np.full(n, NAN); nxt = np.full(n, NAN); upa = np.zeros(n, bool)
    up = c[1] > c[0] if n > 1 else True; ep = h[1] if up else l[1]; s = l[0] if up else h[0]; af = start
    s = s + start * (ep - s)
    for i in range(1, n):
        first = False
        if i > 1: s = nx
        if up and s > l[i]:
            first = True; up = False; s = max(ep, h[i]); ep = l[i]; af = start
        elif (not up) and s < h[i]:
            first = True; up = True; s = min(ep, l[i]); ep = h[i]; af = start
        if not first:
            if up and h[i] > ep: ep = h[i]; af = min(af + inc, mx)
            elif (not up) and l[i] < ep: ep = l[i]; af = min(af + inc, mx)
        if up:
            s = min(s, l[i - 1]); s = min(s, l[i - 2]) if i > 1 else s
        else:
            s = max(s, h[i - 1]); s = max(s, h[i - 2]) if i > 1 else s
        nx = s + af * (ep - s); sar[i] = s; nxt[i] = nx; upa[i] = up
    return sar, nxt, upa


def ha(df):
    o, h, l, c = ohlc(df); hc = (o + h + l + c) / 4; ho = np.empty(len(c)); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    return ho, np.maximum(h, np.maximum(ho, hc)), np.minimum(l, np.minimum(ho, hc)), hc


# ------------------------------------------------------------------ 1. ALMA/EMA
def run_alm(name, df, mm, tag, rows=None, verbose=True, tp=0.03, long_ok=True, short_ok=True, **extra):
    """EMA49 cruzando acima da EMA9 com os dois closes anteriores acima da ALMA130 compra (espelho vende); StochRSI
    K cruzando abaixo de D acima de 92 fecha o long (espelho abaixo de 8); alvo 3% e stop 5,49%; inverte."""
    o, h, l, c = ohlc(df); da = alma(c, 130, 0.775, 4.5); e49, e9 = ema(c, 49), ema(c, 9)
    L = T.xover(e49, e9) & (sh(c, 2) > sh(da, 2)) & (sh(c) > sh(da))
    S = T.xunder(e49, e9) & (sh(c, 2) < sh(da, 2)) & (sh(c) < sh(da))
    r = wilder_rsi(c, 14); k = T.sma(stoch(r, r, r, 8), 3); d = T.sma(k, 15)
    res = gsim(df, mm, L, S & ~L, T.xunder(k, d) & (k > 92), T.xover(k, d) & (k < 8), slp=0.0549, tpp=tp,
               rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. TTM scalper
def run_ttm(name, df, mm, tag, rows=None, verbose=True, inv=False, long_ok=True, short_ok=True, **extra):
    """Close subindo depois de recuo (gatilho de venda) e caindo depois de alta (gatilho de compra) alternam o
    estado; fica comprado no estado verde e vendido no vermelho (inv troca os lados)."""
    o, h, l, c = ohlc(df); n = len(c); sw = np.zeros(n); cs = np.zeros(n)
    for i in range(3, n):
        ts = c[i - 1] < c[i] and (c[i - 2] < c[i - 1] or c[i - 3] < c[i - 1])
        tb = c[i - 1] > c[i] and (c[i - 2] > c[i - 1] or c[i - 3] > c[i - 1])
        sw[i] = 1 if ts else (0 if tb else sw[i - 1])
        cs[i] = 1 if (ts and sw[i - 1] == 0) else (0 if (tb and sw[i - 1] == 1) else cs[i - 1])
    p = np.where(cs == 1, 1, -1) * (-1 if inv else 1); p[:3] = 0
    return run_g(name, df, posflat(df, mm, flat_pos(p, long_ok, short_ok)), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Advanced Ichimoku (long-only)
def run_ich(name, df, mm, tag, rows=None, verbose=True, ent='all', ext='weak', **extra):
    """So long: tenkan cruzando acima da kijun compra (todas, ou so a forte acima da nuvem deslocada); cruzamento
    para baixo com a tenkan acima da nuvem (fraco) fecha, ou qualquer cruzamento para baixo."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2
    tk, kj = dc(9), dc(26); A, B = sh((tk + kj) / 2, 25), sh(dc(52), 25)
    bu, be = T.xover(tk, kj), T.xunder(tk, kj)
    L = bu if ent == 'all' else bu & (tk > A) & (tk > B)
    X = be & (tk > A) & (tk > B) if ext == 'weak' else be
    return run_g(name, df, gsim(df, mm, L, Z(c), X, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Heikin Ashi Wick (long-only)
def run_haw(name, df, mm, tag, rows=None, verbose=True, src='ha', ext='both', **extra):
    """So long: candle HA verde com pavio superior compra; sem pavio superior ou pavio inferior maior fecha
    (src=candle usa o candle comum; ext=nowick so fecha sem pavio superior)."""
    if src == 'ha': O, H, Lw, C = ha(df)
    else: O, H, Lw, C = ohlc(df)
    uw = H - np.maximum(O, C); lw = np.minimum(O, C) - Lw
    X = (uw == 0) | (lw > uw) if ext == 'both' else (uw == 0)
    return run_g(name, df, gsim(df, mm, (C > O) & (uw > 0), Z(C), X, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Linear Channel (long-only)
def run_lch(name, df, mm, tag, rows=None, verbose=True, v=2.0, hl=400, **extra):
    """So long: close 2% abaixo da regressao linear de 55 com a HMA400 abaixo do close compra; close acima da
    regressao fecha."""
    o, h, l, c = ohlc(df); lr = linreg(c, 55)
    L = (c < lr * (1 - v / 100)) & (T.hma(c, hl) < c)
    return run_g(name, df, gsim(df, mm, L, Z(c), c > lr, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. MACD + Stochastic
def run_mst(name, df, mm, tag, rows=None, verbose=True, ls=7, long_ok=True, short_ok=True, **extra):
    """EMA8-EMA24 subindo com Stoch(7) D<25 e subindo compra; espelho (D>75 caindo) vende; inverte."""
    o, h, l, c = ohlc(df); dv = ema(c, 8) - ema(c, 24); d = T.sma(stoch(c, h, l, ls), 3)
    L = (dv > sh(dv)) & (d < 25) & (d > sh(d)); S = (dv < sh(dv)) & (d > 75) & (d < sh(d))
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 7. Sequence Snap
def run_seq(name, df, mm, tag, rows=None, verbose=True, rr=1.5, long_ok=True, short_ok=False, **extra):
    """Candle de baixa seguido de 5 de alta (closes subindo com folga de 0,05% e minimas acima da do candle de
    baixa) com RSI14>40 subindo compra; stop na minima do candle de baixa, alvo 1,5R; so sem posicao (o short,
    espelho, vem desligado)."""
    o, h, l, c = ohlc(df); n = len(c); rl = 5; t = 0.0005; r = wilder_rsi(c, 14)
    bull = (sh(c, rl) < sh(o, rl)); bear = (sh(c, rl) > sh(o, rl))
    sx = lambda x, k: np.asarray(x, float) if k == 0 else sh(x, k)
    for i in range(rl):
        bull &= (sx(c, i) > sx(o, i)) & (sx(l, i) > sx(l, rl)); bear &= (sx(c, i) < sx(o, i)) & (sx(h, i) < sx(h, rl))
        if i < rl - 1:
            bull &= sx(c, i) > sx(c, i + 1) * (1 - t); bear &= sx(c, i) < sx(c, i + 1) * (1 + t)
    L = bull & (r > 40) & (r > sh(r)); S = bear & (r < 60) & (r < sh(r))
    sl_, ss_ = sh(l, rl), sh(h, rl)
    res = gsim(df, mm, L, S & ~L, SLL=sl_, TPL=c + (c - sl_) * rr, SLS=ss_, TPS=c - (ss_ - c) * rr,
               rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. Swing Parabolic SAR
def run_psw(name, df, mm, tag, rows=None, verbose=True, p=(0.02, 0.02, 0.2), long_ok=True, short_ok=True, **extra):
    """Ordem stop no SAR previsto para a barra seguinte, do lado contrario a tendencia: sempre posicionado.
    So comprado: o stop de venda fecha o long."""
    o, h, l, c = ohlc(df); _, nx, up = psar(h, l, c, *p)
    LE = np.where(~up, nx, NAN); SE = np.where(up, nx, NAN)
    if short_ok:
        return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok)
    return run_stp(name, df, tag, rows, verbose, extra, LE, np.full(len(c), NAN), SE, short_ok=False)


# ------------------------------------------------------------------ 9. AK Trend ID (long-only)
def run_akt(name, df, mm, tag, rows=None, verbose=True, p=(3, 8), **extra):
    """So long: EMA3 acima da EMA8 compra, abaixo fecha."""
    o, h, l, c = ohlc(df); s = ema(c, p[0]) - ema(c, p[1])
    return run_g(name, df, gsim(df, mm, s > 0, Z(c), s < 0, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Crypto Price Scalper (long-only)
def run_csc(name, df, mm, tag, rows=None, verbose=True, cc=60, st=0.10, **extra):
    """So long: posicao media do close no canal de 60 cruzando acima de zero, close acima da maxima de 2 barras
    atras e Vortex+ cruzando acima do Vortex- compra; o cruzamento inverso fecha; alvo e stop de 10%."""
    o, h, l, c = ohlc(df); lo, hi = ll(l, cc), hh(h, cc); g = ((c - lo) / lo + (c - hi) / hi) * 50
    tr = np.maximum(h - l, np.maximum(np.abs(h - sh(c)), np.abs(l - sh(c))))
    s = lambda x: roll(x, 14).sum().to_numpy()
    vp, vm = s(np.abs(h - sh(l))) / s(tr), s(np.abs(l - sh(h))) / s(tr); z = K(c, 0)
    L = T.xover(g, z) & (c > sh(h, 2)) & T.xover(vp, vm); X = T.xunder(g, z) & T.xunder(vp, vm)
    return run_g(name, df, gsim(df, mm, L, Z(c), X, slp=st, tpp=st, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Golden X BF
def run_gx(name, df, mm, tag, rows=None, verbose=True, p=(50, 200), long_ok=True, short_ok=True, **extra):
    """SMA50 cruzando a SMA200 compra/vende; inverte."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, p[0]), T.sma(c, p[1])
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(a, b), T.xunder(a, b), long_ok, short_ok)


# ------------------------------------------------------------------ 12. Tendency EMA + RSI
def run_ten(name, df, mm, tag, rows=None, verbose=True, xb=24, long_ok=True, short_ok=False, **extra):
    """EMA10 cruzando acima da EMA20 com EMA10>EMA100 e candle de alta compra; RSI>70 fecha, ou depois de 24
    barras se o close estiver acima da abertura de entrada; espelho no short (desligado no original)."""
    o, h, l, c = ohlc(df); a, b, e = ema(c, 10), ema(c, 20), ema(c, 100); r = wilder_rsi(c, 14)
    L = T.xover(a, b) & (a > e) & (c > o); S = T.xunder(a, b) & (a < e) & (c < o)

    def ex(j, pos, ent, st):
        st['n'] = st.get('n', 0) + 1
        if pos > 0 and (r[j] > 70 or (st['n'] >= xb and c[j] > ent)): return 2, None
        if pos < 0 and (r[j] < 30 or (st['n'] >= xb and c[j] < ent)): return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 13. LunaOwl SuperTrend 2
def run_lst(name, df, mm, tag, rows=None, verbose=True, mult=2.618, long_ok=True, short_ok=True, **extra):
    """Stop ATR(1) x 2,618 suavizado por RMA14, no estilo Chandelier sobre hl2 e close: comprado com a direcao
    de alta e o close acima do stop, vendido no espelho."""
    o, h, l, c = ohlc(df); a = T.rma_nan(mult * T.atr_rma(h, l, c, 1), 14); hl2 = (h + l) / 2; n = len(c)
    ls = hl2 - a; ss = hl2 + a; d = np.ones(n); p = np.zeros(n)
    for i in range(1, n):
        if a[i] != a[i]: continue
        lp = ls[i - 1] if ls[i - 1] == ls[i - 1] else ls[i]; sp = ss[i - 1] if ss[i - 1] == ss[i - 1] else ss[i]
        if c[i - 1] > lp: ls[i] = max(ls[i], lp)
        if c[i - 1] < sp: ss[i] = min(ss[i], sp)
        d[i] = 1 if (d[i - 1] == -1 and c[i] > sp) else (-1 if (d[i - 1] == 1 and c[i] < lp) else d[i - 1])
        p[i] = 1 if (d[i] == 1 and c[i] > ls[i]) else (-1 if (d[i] == -1 and c[i] < ss[i]) else p[i - 1])
    return R(name, df, mm, tag, rows, verbose, extra, (p == 1) & (sh(p) != 1), (p == -1) & (sh(p) != -1), long_ok, short_ok)


# ------------------------------------------------------------------ 14. FXFUNDINGMATE Trend
def run_fxf(name, df, mm, tag, rows=None, verbose=True, tm=1.0, long_ok=True, short_ok=True, **extra):
    """Stoch(5,3) cruzando acima de 20 com MACD>0, close acima da SMA100 e das duas linhas da nuvem deslocada compra
    (espelho em 80 vende); stop e alvo de 1 ATR8 a partir da entrada; a entrada contraria inverte."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2
    A, B = sh((dc(9) + dc(26)) / 2, 25), sh(dc(52), 25); m = ema(c, 12) - ema(c, 26)
    k = T.sma(stoch(c, h, l, 5), 3); s = T.sma(c, 100); a = T.atr_rma(h, l, c, 8)
    L = T.xover(k, K(c, 20)) & (m > 0) & (c > s) & (c > A) & (c > B)
    S = T.xunder(k, K(c, 80)) & (m < 0) & (c < s) & (c < A) & (c < B)
    res = gsim(df, mm, L, S & ~L, SLL=c - a, TPL=c + tm * a, SLS=c + a, TPS=c - tm * a, rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. OKX MA Crossover
def run_okx(name, df, mm, tag, rows=None, verbose=True, st=0.07, long_ok=True, short_ok=True, **extra):
    """Minima abaixo da SMA13 anterior (e nao 2 barras antes) compra; maxima acima vende (vence quando os dois
    ocorrem); alvo e stop de 7% do close do sinal; inverte (a ordem limite no close virou mercado)."""
    o, h, l, c = ohlc(df); m = sh(T.sma(c, 13)); dL = l < m; dS = h > m
    S = dS & ~sh(dS, 2).astype(bool); L = dL & ~sh(dL, 2).astype(bool) & ~S
    res = gsim(df, mm, L, S, SLL=c * (1 - st), TPL=c * (1 + st), SLS=c * (1 + st), TPS=c * (1 - st), rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Market Dynamics HH/LL breakout
def run_mdb(name, df, mm, tag, rows=None, verbose=True, lb=26, long_ok=True, short_ok=True, **extra):
    """Close acima da maxima de 26 anterior (se ela for maior que a maxima de 10 anterior) compra, espelho vende;
    com os dois lados inverte; so comprado: fecha no sinal de venda, close 2% abaixo ou 7% acima da entrada."""
    o, h, l, c = ohlc(df); H, Lw = sh(hh(h, lb)), sh(ll(l, lb)); HG, LG = sh(hh(h, 10)), sh(ll(l, 10))
    L = (c > H) & (H > HG); S = (c < Lw) & (Lw < LG)
    if short_ok:
        return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, True)

    def ex(j, pos, ent, st):
        return (2, None) if (S[j] or c[j] < ent * 0.98 or c[j] > ent * 1.07) else (0, None)
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, rev=False, short_ok=False)


# ------------------------------------------------------------------ 17. Parabolic SAR w/ EMA
def run_pse(name, df, mm, tag, rows=None, verbose=True, off=1.0, long_ok=True, short_ok=True, **extra):
    """Maxima rompendo o SAR (0,01/0,005/0,1) ou EMA100 cruzando abaixo da EMA10 com close acima do SAR, sempre
    com close 1% acima da EMA100, compra (espelho vende); o SAR tocado fecha a posicao."""
    o, h, l, c = ohlc(df); ps = psar(h, l, c, 0.01, 0.005, 0.1)[0]; e, f = ema(c, 100), ema(c, 10); of = off / 100 * e
    L = (((sh(h) < sh(ps, 2)) & (h >= sh(ps))) | (T.xunder(e, f) & (c > ps))) & (c > e + of)
    S = (((sh(l) > sh(ps, 2)) & (l <= sh(ps))) | (T.xover(e, f) & (c < ps))) & (c < e - of)
    res = gsim(df, mm, L, S & ~L, l < ps, h > ps, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. Smoothed Heiken Ashi (long-only)
def run_sha(name, df, mm, tag, rows=None, verbose=True, ln=10, l2=10, **extra):
    """So long: HA sobre EMAs de 10 de OHLC, com abertura e close HA suavizados por EMA10; virada para verde compra,
    para vermelho fecha."""
    o, h, l, c = ohlc(df); O, H, Lw, C = ema(o, ln), ema(h, ln), ema(l, ln), ema(c, ln)
    hc = (O + H + Lw + C) / 4; ho = np.empty(len(c)); ho[0] = (O[0] + C[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    col = (ema(ho, l2) <= ema(hc, l2)).astype(int)
    L = (col == 1) & (sh(col) == 0); X = (col == 0) & (sh(col) == 1)
    return run_g(name, df, gsim(df, mm, L, Z(c), X, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. VIP (long-only)
def run_vip(name, df, mm, tag, rows=None, verbose=True, tp=0.01, usl=False, **extra):
    """So long: canal SSL (SMA200 das maximas/minimas) virando para cima, abertura suavizada subindo, EMA100 e
    maxima suavizada abaixo do meio do candle compra; alvo 1%; close abaixo da EMA100 arma um stop no close
    (ou no stop de 1% da entrada)."""
    o, h, l, c = ohlc(df); a, b = T.sma(h, 200), T.sma(l, 200); n = len(c); hv = np.zeros(n)
    for i in range(1, n): hv[i] = 1 if c[i] > a[i] else (-1 if c[i] < b[i] else hv[i - 1])
    co = ema((sh(o) + sh(c)) / 2, 25); ch = ema(np.maximum(h, c), 20); m = ema(c, 100); av = (h + l) / 2
    L = (hv == 1) & (sh(hv) == -1) & (co > sh(co)) & (m < av) & (ch < av)

    def ex(j, pos, ent, st):
        s = st.get('s'); tg = ent * (1 + tp)
        if s is not None and l[j] <= s: return 1, min(o[j], s)
        if h[j] >= tg: return 1, max(o[j], tg)
        if c[j] < m[j]: st['s'] = ent * 0.99 if usl else c[j]
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, rev=False, short_ok=False)


# ------------------------------------------------------------------ 20. Combo 123 Reversal & Stochastic Crossover
def run_cmb(name, df, mm, tag, rows=None, verbose=True, ln=14, long_ok=True, short_ok=True, **extra):
    """123 Reversal (Stoch 14/1/3, nivel 50) e Stochastic Crossover (7/3, 20/70) concordando dao a posicao;
    discordando zera."""
    o, h, l, c = ohlc(df); n = len(c)
    f1 = T.sma(stoch(c, h, l, ln), 1); s1 = T.sma(f1, 3); f2 = stoch(c, h, l, 7); s2 = T.sma(f2, 3)
    p1 = np.zeros(n); p2 = np.zeros(n)
    for i in range(2, n):
        if c[i - 2] < c[i - 1] and c[i] > c[i - 1] and f1[i] < s1[i] and f1[i] > 50: p1[i] = 1
        elif c[i - 2] > c[i - 1] and c[i] < c[i - 1] and f1[i] > s1[i] and f1[i] < 50: p1[i] = -1
        else: p1[i] = p1[i - 1]
        if f2[i] < s2[i] and f2[i] > 70 and s2[i] > 70: p2[i] = 1
        elif f2[i] >= s2[i] and f2[i] < 20 and s2[i] < 20: p2[i] = -1
        else: p2[i] = p2[i - 1]
    p = np.where((p1 == 1) & (p2 == 1), 1, np.where((p1 == -1) & (p2 == -1), -1, 0))
    return run_g(name, df, posflat(df, mm, flat_pos(p, long_ok, short_ok) * (p != 0)), tag, rows, verbose, extra)


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')
        sk = lambda s: dict(short_ok=s == 'ambos')

        def grid(est, fn, label, tfs, default_cfg, combos, dkw=None):
            print(f"\n### {label}", flush=True)
            for tf in tfs:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg, **(dkw or {}))
                for cfg, kw in combos:
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)

        def g2(est, fn, label, key, vals, fmt, default_cfg, dkw=None):
            grid(est, fn, label, TFS, default_cfg,
                 [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)], dkw)

        def g4(est, fn, label, k1, v1, k2, v2, fmt, default_cfg):
            grid(est, fn, label, TFS, default_cfg,
                 [(fmt(a, b), {k1: a, k2: b}) for a, b in itertools.product(v1, v2)])

        pr = lambda v: f'{v[0]}/{v[1]}'
        g2('alm', run_alm, "1. ALMA/EMA", 'tp', (0.03, 0.06), lambda v: f'tp{v * 100:g}%', 'tp3% ambos')
        g2('ttm', run_ttm, "2. TTM scalper", 'inv', (False, True), lambda v: 'inv' if v else 'normal', 'normal ambos')
        g4('ich', run_ich, "3. Advanced Ichimoku (long-only)", 'ent', ('all', 'strong'), 'ext', ('weak', 'all'),
           lambda a, b: f'ent {a} sai {b}', 'ent all sai weak')
        g4('haw', run_haw, "4. Heikin Ashi Wick (long-only)", 'src', ('ha', 'candle'), 'ext', ('both', 'nowick'),
           lambda a, b: f'{a} {b}', 'ha both')
        g4('lch', run_lch, "5. Linear Channel (long-only)", 'v', (2.0, 4.0), 'hl', (400, 200),
           lambda a, b: f'v{a:g}% hma{b}', 'v2% hma400')
        g2('mst', run_mst, "6. MACD + Stochastic", 'ls', (7, 14), lambda v: f'st{v}', 'st7 ambos')
        g2('seq', run_seq, "7. Sequence Snap", 'rr', (1.5, 1.0), lambda v: f'rr{v:g}', 'rr1.5 long',
           dict(short_ok=False))
        g2('psw', run_psw, "8. Swing Parabolic SAR", 'p', ((0.02, 0.02, 0.2), (0.01, 0.01, 0.1)),
           lambda v: f'af{v[0]:g}', 'af0.02 ambos')
        grid('akt', run_akt, "9. AK Trend ID (long-only)", TFS, '3/8',
             [(pr(v), dict(p=v)) for v in ((3, 8), (5, 13), (8, 21), (13, 34))])
        g4('csc', run_csc, "10. Crypto Price Scalper (long-only)", 'cc', (60, 20), 'st', (0.10, 0.03),
           lambda a, b: f'cc{a} st{b * 100:g}%', 'cc60 st10%')
        g2('gx', run_gx, "11. Golden X BF", 'p', ((50, 200), (20, 100)), pr, '50/200 ambos')
        g2('ten', run_ten, "12. Tendency EMA + RSI", 'xb', (24, 48), lambda v: f'x{v}', 'x24 long',
           dict(short_ok=False))
        g2('lst', run_lst, "13. LunaOwl SuperTrend 2", 'mult', (2.618, 4.0), lambda v: f'm{v:g}', 'm2.618 ambos')
        g2('fxf', run_fxf, "14. FXFUNDINGMATE Trend", 'tm', (1.0, 2.0), lambda v: f'tp{v:g}atr', 'tp1atr ambos')
        g2('okx', run_okx, "15. OKX MA Crossover", 'st', (0.07, 0.03), lambda v: f'{v * 100:g}%', '7% ambos')
        g2('mdb', run_mdb, "16. Market Dynamics HH/LL breakout", 'lb', (26, 50), lambda v: f'lb{v}', 'lb26 ambos')
        g2('pse', run_pse, "17. Parabolic SAR w/ EMA", 'off', (1.0, 0.0), lambda v: f'off{v:g}%', 'off1% ambos')
        g4('sha', run_sha, "18. Smoothed Heiken Ashi (long-only)", 'ln', (10, 20), 'l2', (10, 20),
           lambda a, b: f'{a}/{b}', '10/10')
        g4('vip', run_vip, "19. VIP (long-only)", 'tp', (0.01, 0.03), 'usl', (False, True),
           lambda a, b: f'tp{a * 100:g}% ' + ('sl1%' if b else 'stop no close'), 'tp1% stop no close')
        g2('cmb', run_cmb, "20. Combo 123 Reversal & Stochastic", 'ln', (14, 28), lambda v: f'l{v}', 'l14 ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote31')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
