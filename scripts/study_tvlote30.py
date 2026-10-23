"""Lote 30 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 a 29
(ver docs/LOTE30_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote30.py xau us100 wti btc eth
"""
import os, sys, itertools, math
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch, dmi
from study_tvlote9 import summary
from study_tvlote20 import sh
from study_tvlote25 import posflat, wilder_rsi, hh, ll, ffill, Z, NAN, roll, run_loop
from study_tvlote26 import flat_pos
from study_tvlote27 import rev_or_long


K = lambda c, v: np.full(len(c), float(v))


def R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok, **kw):
    return run_g(name, df, rev_or_long(df, mm, L, S, long_ok, short_ok, **kw), tag, rows, verbose, extra)


def supertrend(h, l, c, n, mult):
    """ta.supertrend com multiplicador por barra; devolve (linha, direcao) com -1 = alta."""
    a = T.atr_rma(h, l, c, n); m = mult * np.ones(len(c)); hl2 = (h + l) / 2; N = len(c)
    st = np.full(N, NAN); d = np.ones(N); lo = np.full(N, NAN); up = np.full(N, NAN)
    for i in range(N):
        if a[i] != a[i]: continue
        lb = hl2[i] - m[i] * a[i]; ub = hl2[i] + m[i] * a[i]
        if i > 0 and lo[i - 1] == lo[i - 1]:
            pl, pu = lo[i - 1], up[i - 1]
            lb = lb if (lb > pl or c[i - 1] < pl) else pl
            ub = ub if (ub < pu or c[i - 1] > pu) else pu
            if st[i - 1] == pu: d[i] = -1 if c[i] > ub else 1
            else: d[i] = 1 if c[i] < lb else -1
        lo[i], up[i] = lb, ub; st[i] = lb if d[i] == -1 else ub
    return st, d


# ------------------------------------------------------------------ 1. Hull MA and Candle cross
def run_hul(name, df, mm, tag, rows=None, verbose=True, z=50, long_ok=True, short_ok=True, **extra):
    """Hull de z sobre a abertura: abertura acima da Hull e acima da abertura de 10 barras atras compra, o
    espelho vende; inverte."""
    o, h, l, c = ohlc(df)
    n1 = T.wma(2 * T.wma(o, int(round(z / 2))) - T.wma(o, z), int(round(math.sqrt(z))))
    L = (o > n1) & (o > sh(o, 10)); S = (o < n1) & (o < sh(o, 10))
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 2. TrendShift Supertrend + ADX
def run_tsh(name, df, mm, tag, rows=None, verbose=True, tight=1.75, long_ok=True, short_ok=True, **extra):
    """Supertrend ATR10 com multiplicador 1,75 quando ADX>25 e 4,5 quando ADX<20 (mantem o anterior entre os dois);
    virada do Supertrend compra/vende, sem entrada quando ADX<20; inverte (o stop/alvo vem desligado)."""
    o, h, l, c = ohlc(df); adx = dmi(h, l, c, 14)[2]; n = len(c); m = np.full(n, tight); cur = tight
    for i in range(n):
        if adx[i] > 25: cur = tight
        elif adx[i] < 20: cur = 4.5
        m[i] = cur
    _, d = supertrend(h, l, c, 10, m); ok = ~(adx < 20); ch = d != sh(d)
    return R(name, df, mm, tag, rows, verbose, extra, ch & (d == -1) & ok, ch & (d == 1) & ok, long_ok, short_ok)


# ------------------------------------------------------------------ 3. Multi-MA
def run_mma(name, df, mm, tag, rows=None, verbose=True, ln=66, long_ok=True, short_ok=True, **extra):
    """VWMA, RMA, SMA, WMA e EMA de 66 todas subindo compra, todas caindo vende; inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float) + 1e-12
    ms = [roll(c * v, ln).sum().to_numpy() / roll(v, ln).sum().to_numpy(), T.rma_nan(c, ln), T.sma(c, ln),
          T.wma(c, ln), ema(c, ln)]
    L = np.logical_and.reduce([x > sh(x) for x in ms]); S = np.logical_and.reduce([x < sh(x) for x in ms])
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 4. MAster Gold
def run_gold(name, df, mm, tag, rows=None, verbose=True, p=(182, 60), long_ok=True, short_ok=True, **extra):
    """Close acima da EMA182 cruzando acima da SMA60 compra; minima abaixo da SMA182 com close cruzando abaixo da
    EMA60 vende; inverte."""
    o, h, l, c = ohlc(df); a, b = p
    L = (c > ema(c, a)) & T.xover(c, T.sma(c, b)); S = (l < T.sma(c, a)) & T.xunder(c, ema(c, b))
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 5. RSI Divergence x Ichimoku x 200EMA
def _div(osc, px, found, lb, sign):
    """Divergencia regular e oculta (pivo confirmado lb barras depois) contra o pivo anterior a 5..60 barras."""
    n = len(osc); reg = np.zeros(n, bool); hid = np.zeros(n, bool); last = -1
    for i in range(n):
        if found[i]:
            if last >= 0 and 5 <= i - last - 1 <= 60:
                o0, o1 = osc[i - lb], osc[last - lb]; p0, p1 = px[i - lb], px[last - lb]
                reg[i] = sign * (p0 - p1) < 0 and sign * (o0 - o1) > 0
                hid[i] = sign * (p0 - p1) > 0 and sign * (o0 - o1) < 0
            last = i
    return reg | hid


def run_rdi(name, df, mm, tag, rows=None, verbose=True, lb=5, long_ok=True, short_ok=True, **extra):
    """Divergencia (regular ou oculta) do RSI14 por pivos 5/5: alta com o topo da nuvem (sem deslocamento) acima
    da EMA200 compra, baixa com a EMA200 acima do fundo da nuvem vende; RSI cruzando acima de 75 fecha o long,
    acima de 25 fecha o short; a entrada contraria inverte."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 14); e = ema(c, 200)
    dc = lambda n: (hh(h, n) + ll(l, n)) / 2
    a = (dc(9) + dc(26)) / 2; b = dc(52); top, bot = np.maximum(a, b), np.minimum(a, b)
    L = _div(r, l, T.pivotlow(r, lb, lb), lb, 1) & (top > e)
    S = _div(r, h, T.pivothigh(r, lb, lb), lb, -1) & (e > bot)
    res = gsim(df, mm, L, S & ~L, T.xover(r, K(r, 75)), T.xover(r, K(r, 25)), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Percent Trailing Stop
def run_ptr(name, df, mm, tag, rows=None, verbose=True, trl=0.10, long_ok=True, short_ok=True, **extra):
    """SMA10 x SMA20 compra/vende e inverte; trailing stop de 10% sobre o close (ordem stop na barra seguinte).
    So comprado: o cruzamento para baixo fecha o long."""
    o, h, l, c = ohlc(df); L = T.xover(T.sma(c, 10), T.sma(c, 20)); S = T.xunder(T.sma(c, 10), T.sma(c, 20))

    def ex(j, pos, ent, st):
        lv = st.get('lv')
        if lv is not None:
            if pos > 0 and l[j] <= lv: return 1, min(o[j], lv)
            if pos < 0 and h[j] >= lv: return 1, max(o[j], lv)
        st['lv'] = (max(c[j] * (1 - trl), lv or 0) if pos > 0 else min(c[j] * (1 + trl), lv or 1e18))
        if pos > 0 and not short_ok and S[j]: return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 7. Multiple MACD RSI
def run_mmr(name, df, mm, tag, rows=None, verbose=True, f=(10, 22), long_ok=True, short_ok=True, **extra):
    """Histograma do MACD 10/22/9 (close, sinal SMA) e do MACD 21/45/20 (abertura) positivos com (close+max) acima
    do anterior compra; os dois negativos, (close+min) abaixo do anterior e StochRSI D>20 vende; inverte."""
    o, h, l, c = ohlc(df)
    m1 = ema(c, f[0]) - ema(c, f[1]); d1 = m1 - T.sma(m1, 9)
    m2 = ema(o, 21) - ema(o, 45); d2 = m2 - T.sma(m2, 20)
    r = wilder_rsi(c, 7); k = T.sma(stoch(r, r, r, 8), 2); d = T.sma(k, 3)
    L = (d1 > 0) & (d2 > 0) & (c + h > sh(c) + sh(h)); S = (d1 < 0) & (d2 < 0) & (c + l < sh(c) + sh(l)) & (d > 20)
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 8. Gann Swing Oscillator
def run_gso(name, df, mm, tag, rows=None, verbose=True, ln=5, long_ok=True, short_ok=True, **extra):
    """Maxima de 5 subindo depois de cair = +1, minima de 5 caindo depois de subir = -1 (senao mantem); fica
    comprado em +1 e vendido em -1."""
    o, h, l, c = ohlc(df); H, Lw = hh(h, ln), ll(l, ln); n = len(c); g = np.zeros(n)
    for i in range(2, n):
        if H[i - 2] > H[i - 1] and H[i] > H[i - 1]: g[i] = 1
        elif Lw[i - 2] < Lw[i - 1] and Lw[i] < Lw[i - 1]: g[i] = -1
        else: g[i] = g[i - 1]
    return run_g(name, df, posflat(df, mm, flat_pos(g, long_ok, short_ok)), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. RSI of MACD (long-only)
def run_rom(name, df, mm, tag, rows=None, verbose=True, xl=15, sl=0.0, **extra):
    """So long: RSI14 da linha MACD 12/21 cruzando acima de 30 ou 35 com close >= EMA21 compra; RSI cruzando abaixo
    de 15 fecha (sl: stop opcional em % da entrada)."""
    o, h, l, c = ohlc(df); m = ema(c, 12) - ema(c, 21); r = wilder_rsi(m, 14)
    L = (T.xover(r, K(r, 30)) | T.xover(r, K(r, 35))) & (c >= ema(c, 21))
    res = gsim(df, mm, L, Z(c), T.xunder(r, K(r, xl)), rev=False, short_ok=False, slp=sl)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Optimized Trend Tracker
def run_ott(name, df, mm, tag, rows=None, verbose=True, pct=0.1, long_ok=True, short_ok=True, **extra):
    """VIDYA (CMO 9, periodo 1) e OTT de pct%: VIDYA cruzando acima da OTT de 2 barras atras compra, abaixo vende;
    inverte."""
    o, h, l, c = ohlc(df); n = len(c); dc = np.diff(c, prepend=NAN)
    ud = np.where(dc > 0, dc, np.where(dc < 0, 0, 0)); dd = np.where(dc < 0, -dc, 0)
    UD, DD = roll(ud, 9).sum().to_numpy(), roll(dd, 9).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        k = np.nan_to_num(np.abs((UD - DD) / (UD + DD)))
    V = np.zeros(n); ls = np.zeros(n); ss = np.zeros(n); d = np.ones(n); ott = np.zeros(n)
    for i in range(n):
        V[i] = k[i] * c[i] + (1 - k[i]) * (V[i - 1] if i else 0)
        f = V[i] * pct / 100; a, b = V[i] - f, V[i] + f
        pl = ls[i - 1] if i else a; ps = ss[i - 1] if i else b
        ls[i] = max(a, pl) if V[i] > pl else a; ss[i] = min(b, ps) if V[i] < ps else b
        dp = d[i - 1] if i else 1
        d[i] = 1 if (dp == -1 and V[i] > ps) else (-1 if (dp == 1 and V[i] < pl) else dp)
        mt = ls[i] if d[i] == 1 else ss[i]
        ott[i] = mt * (200 + pct) / 200 if V[i] > mt else mt * (200 - pct) / 200
    o2 = sh(ott, 2)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(V, o2), T.xunder(V, o2), long_ok, short_ok)


# ------------------------------------------------------------------ 11. SuperIchi
def _si_avg(src, h, l, c, n, mult):
    a = T.atr_rma(h, l, c, n) * mult; hl2 = (h + l) / 2; N = len(c)
    up, lo, os_, mx, mn, out = 0.0, 0.0, 0, 0.0, 0.0, np.full(N, NAN); pspt = NAN
    for i in range(N):
        if a[i] != a[i]: continue
        u, d = hl2[i] + a[i], hl2[i] - a[i]
        up = min(u, up) if (i and src[i - 1] < up) else u
        lo = max(d, lo) if (i and src[i - 1] > lo) else d
        os_ = 1 if src[i] > up else (0 if src[i] < lo else os_)
        spt = lo if os_ == 1 else up
        cr = pspt == pspt and ((src[i] > spt) != (src[i - 1] > pspt))
        mx = max(src[i], mx) if (cr or os_ == 1) else spt
        mn = min(src[i], mn) if (cr or os_ == 0) else spt
        pspt = spt; out[i] = (mx + mn) / 2
    return out


def run_sich(name, df, mm, tag, rows=None, verbose=True, pf=2.0, long_ok=True, short_ok=True, **extra):
    """SuperIchi (tenkan 9x2, kijun 26x4, span B 52x6, deslocamento 26): tenkan>kijun, close>tenkan,
    kijun>senkouA[25], senkouA[25]>senkouB[25] e pullback para baixo das duas linhas nas ultimas 5 barras compra
    (espelho vende); stop no menor de (close - ATR14) e minima de 15, alvo 2R; a entrada contraria inverte."""
    o, h, l, c = ohlc(df)
    tk, kj = _si_avg(c, h, l, c, 9, 2.0), _si_avg(c, h, l, c, 26, 4.0); sa = (tk + kj) / 2
    sb = _si_avg(c, h, l, c, 52, 6.0); sa25, sb25 = sh(sa, 25), sh(sb, 25)
    pbL = T.barssince((c < kj) & (c < tk)) <= 5; pbS = T.barssince((c > kj) & (c > tk)) <= 5
    L = (tk > kj) & (c > tk) & (kj > sa25) & (sa25 > sb25) & pbL
    S = (tk < kj) & (c < tk) & (kj < sa25) & (sa25 < sb25) & pbS
    a = T.atr_rma(h, l, c, 14)
    sll = np.minimum(c - a, ll(l, 15)); sls = np.maximum(c + a, hh(h, 15))
    res = gsim(df, mm, L, S & ~L, SLL=sll, TPL=c + (c - sll) * pf, SLS=sls, TPS=c - (sls - c) * pf,
               rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. KALKI TFXBOT (liquidity sweep)
def run_kal(name, df, mm, tag, rows=None, verbose=True, rr=3.0, long_ok=True, short_ok=True, **extra):
    """Ultimo pivo de minima (10/3) varrido (minima abaixo, close acima, candle de alta, close>EMA200) compra com
    stop na minima e alvo rr x risco; espelho no pivo de maxima; a entrada contraria inverte (o buffer
    de stop em pontos foi ignorado)."""
    o, h, l, c = ohlc(df); e = ema(c, 200)
    sup = ffill(np.where(T.pivotlow(l, 10, 3), sh(l, 3), NAN)); res_ = ffill(np.where(T.pivothigh(h, 10, 3), sh(h, 3), NAN))
    L = (l < sup) & (c > sup) & (c > o) & (c > e); S = (h > res_) & (c < res_) & (c < o) & (c < e)
    r = gsim(df, mm, L, S & ~L, SLL=l, TPL=c + (c - l) * rr, SLS=h, TPS=c - (h - c) * rr,
             rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. 2x Universelle Linien
def run_lin(name, df, mm, tag, rows=None, verbose=True, p=(21, 50), long_ok=True, short_ok=True, **extra):
    """EMA21 cruzando acima da SMA50 compra e fecha o short; abaixo vende e fecha o long."""
    o, h, l, c = ohlc(df); a, b = ema(c, p[0]), T.sma(c, p[1])
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(a, b), T.xunder(a, b), long_ok, short_ok)


# ------------------------------------------------------------------ 14. Supertrend pullback (JS-TechTrading)
def run_stpb(name, df, mm, tag, rows=None, verbose=True, mode='pull', long_ok=True, short_ok=True, **extra):
    """Supertrend 3/10: pullback (minima anterior cruzando abaixo da linha de alta e maxima acima da anterior) ou
    virada simples, com RSI14>=50 e close>EMA200 compra (espelho vende), so sem posicao; stop e alvo de 1%."""
    o, h, l, c = ohlc(df); stl, d = supertrend(h, l, c, 10, 3.0)
    lg = np.where(d == -1, stl, NAN); sg = np.where(d == 1, stl, NAN); r = wilder_rsi(c, 14); e = ema(c, 200)
    if mode == 'pull':
        bL = T.xunder(sh(l), lg) & ~np.isnan(lg) & (h > sh(h)); bS = T.xover(sh(h), sg) & ~np.isnan(sg) & (l < sh(l))
    else:
        bL = (d == -1) & (sh(d) == 1); bS = (d == 1) & (sh(d) == -1)
    L = bL & (r >= 50) & (c > e); S = bS & (r <= 50) & (c < e)
    res = gsim(df, mm, L, S & ~L, slp=0.01, tpp=0.01, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Scalping Dips On Trend (Coinrule)
def run_dip(name, df, mm, tag, rows=None, verbose=True, dip=2.0, tp=0.03, **extra):
    """So long: queda de mais de 2% na barra com SMA50 acima do close compra; close 10% abaixo ou 3% acima da
    entrada fecha na abertura seguinte."""
    o, h, l, c = ohlc(df); ch = (c - sh(c)) / sh(c) * 100; L = (ch < -dip) & (T.sma(c, 50) > c)

    def ex(j, pos, ent, st):
        return (2, None) if (c[j] < ent * 0.9 or c[j] > ent * (1 + tp)) else (0, None)
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, rev=False, short_ok=False)


# ------------------------------------------------------------------ 16. Momentum BF
def run_mbf(name, df, mm, tag, rows=None, verbose=True, ln=18, long_ok=True, short_ok=True, **extra):
    """Momentum de 18 e sua variacao positivos compra, negativos vende (inverte); stop fixo de 8% no long e 7% no
    short a partir da barra seguinte a entrada. So comprado: o sinal de venda fecha."""
    o, h, l, c = ohlc(df); m0 = c - sh(c, ln); m1 = m0 - sh(m0); L = (m0 > 0) & (m1 > 0); S = (m0 < 0) & (m1 < 0)

    def ex(j, pos, ent, st):
        if st.get('n', 0) > 0:
            if pos > 0 and l[j] <= ent * 0.92: return 1, min(o[j], ent * 0.92)
            if pos < 0 and h[j] >= ent * 1.07: return 1, max(o[j], ent * 1.07)
        st['n'] = st.get('n', 0) + 1
        if pos > 0 and not short_ok and S[j]: return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 17. 1 min forex scalping
def run_scl(name, df, mm, tag, rows=None, verbose=True, k=1, long_ok=True, short_ok=True, **extra):
    """EMA12 cruzando a SMA55 com EMA12>EMA26 compra, com EMA12<EMA26 vende; inverte (k multiplica os periodos)."""
    o, h, l, c = ohlc(df); a, b, s = ema(c, 12 * k), ema(c, 26 * k), T.sma(c, 55 * k)
    x = T.xover(a, s) | T.xunder(a, s)
    return R(name, df, mm, tag, rows, verbose, extra, x & (a > b), x & (a < b), long_ok, short_ok)


# ------------------------------------------------------------------ 18. LunaOwl suporte/resistencia
def run_lsr(name, df, mm, tag, rows=None, verbose=True, lb=50, long_ok=True, short_ok=True, **extra):
    """Resistencia = maxima de 50 no penultimo cruzamento close x SMA50, suporte = minima de 50 no mesmo ponto;
    close rompendo a resistencia compra, perdendo o suporte vende; inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, lb); x = T.xover(c, m) | T.xunder(c, m)
    Rr = T.valuewhen_prev(x, hh(h, lb), 1); Ss = T.valuewhen_prev(x, ll(l, lb), 1)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(c, Rr), T.xunder(c, Ss), long_ok, short_ok)


# ------------------------------------------------------------------ 19. RSI Buy and Sell (long-only)
def run_rbs(name, df, mm, tag, rows=None, verbose=True, ob=70, os_=30, **extra):
    """So long: RSI14 acima de 70 compra (momentum), abaixo de 30 fecha."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 14)
    return run_g(name, df, gsim(df, mm, r > ob, Z(c), r < os_, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Harmonic System
def run_hms(name, df, mm, tag, rows=None, verbose=True, src='close', long_ok=True, short_ok=True, **extra):
    """Seis medias harmonicas encadeadas (3 barras cada, a partir do close anterior): min(T1,T2,T3) cruzando acima
    de max(T4,T5,T6) compra, min(T1,T2) cruzando abaixo de max(T3,T4) vende; inverte."""
    o, h, l, c = ohlc(df); x = c if src == 'close' else (h + l + c) / 3
    hm = lambda a, b, d: 3 / (1 / a + 1 / b + 1 / d)
    t = [hm(sh(x, 1), sh(x, 2), sh(x, 3))]
    for _ in range(5): t.append(hm(t[-1], sh(t[-1]), sh(t[-1], 2)))
    T1, T2, T3, T4, T5, T6 = t
    X1 = np.minimum(np.minimum(T1, T2), T3); X2 = np.maximum(np.maximum(T4, T5), T6)
    X3 = np.minimum(T1, T2); X4 = np.maximum(T3, T4)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(X1, X2), T.xunder(X3, X4), long_ok, short_ok)


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

        def g2(est, fn, label, key, vals, fmt, default_cfg, tfs=TFS):
            grid(est, fn, label, tfs, default_cfg,
                 [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)])

        pr = lambda v: f'{v[0]}/{v[1]}'
        g2('hul', run_hul, "1. Hull MA and Candle cross", 'z', (50, 100), lambda v: f'z{v}', 'z50 ambos')
        g2('tsh', run_tsh, "2. TrendShift Supertrend + ADX", 'tight', (1.75, 3.0), lambda v: f'm{v:g}', 'm1.75 ambos')
        g2('mma', run_mma, "3. Multi-MA", 'ln', (66, 150), lambda v: f'l{v}', 'l66 ambos')
        g2('gold', run_gold, "4. MAster Gold", 'p', ((182, 60), (100, 30)), pr, '182/60 ambos')
        g2('rdi', run_rdi, "5. RSI Divergence x Ichimoku x 200EMA", 'lb', (5, 3), lambda v: f'lb{v}', 'lb5 ambos')
        g2('ptr', run_ptr, "6. Percent Trailing Stop", 'trl', (0.10, 0.05), lambda v: f't{v * 100:g}%', 't10% ambos')
        g2('mmr', run_mmr, "7. Multiple MACD RSI", 'f', ((10, 22), (12, 26)), pr, '10/22 ambos')
        g2('gso', run_gso, "8. Gann Swing Oscillator", 'ln', (5, 10), lambda v: f'l{v}', 'l5 ambos')
        grid('rom', run_rom, "9. RSI of MACD (long-only)", TFS, 'x15 sem stop',
             [(f'x{a} ' + (f'sl{b * 100:g}%' if b else 'sem stop'), dict(xl=a, sl=b))
              for a, b in itertools.product((15, 50), (0.0, 0.03))])
        g2('ott', run_ott, "10. Optimized Trend Tracker", 'pct', (0.1, 1.4), lambda v: f'{v:g}%', '0.1% ambos')
        g2('sich', run_sich, "11. SuperIchi", 'pf', (2.0, 3.0), lambda v: f'rr{v:g}', 'rr2 ambos')
        g2('kal', run_kal, "12. KALKI TFXBOT", 'rr', (3.0, 1.5), lambda v: f'rr{v:g}', 'rr3 ambos')
        g2('lin', run_lin, "13. 2x Universelle Linien", 'p', ((21, 50), (50, 200)), pr, '21/50 ambos')
        g2('stpb', run_stpb, "14. Supertrend pullback", 'mode', ('pull', 'flip'), str, 'pull ambos')
        grid('dip', run_dip, "15. Scalping Dips On Trend (long-only)", TFS, 'd2 tp3%',
             [(f'd{a:g} tp{b * 100:g}%', dict(dip=a, tp=b)) for a, b in itertools.product((2.0, 4.0), (0.03, 0.06))])
        g2('mbf', run_mbf, "16. Momentum BF", 'ln', (18, 36), lambda v: f'l{v}', 'l18 ambos')
        g2('scl', run_scl, "17. 1 min forex scalping", 'k', (1, 2), lambda v: f'x{v}', 'x1 ambos')
        g2('lsr', run_lsr, "18. LunaOwl suporte/resistencia", 'lb', (50, 100), lambda v: f'lb{v}', 'lb50 ambos')
        grid('rbs', run_rbs, "19. RSI Buy and Sell (long-only)", TFS, '70/30',
             [(f'{a}/{b}', dict(ob=a, os_=b)) for a, b in itertools.product((70, 60), (30, 40))])
        g2('hms', run_hms, "20. Harmonic System", 'src', ('close', 'hlc3'), str, 'close ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote30')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
