"""Lote 28 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 e 27
(ver docs/LOTE28_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote28.py xau us100 wti btc eth
"""
import os, sys, itertools, math
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch, dmi
from study_tvlote9 import summary
from study_tvlote20 import sh, _st, heikin
from study_tvlote22 import run_stp, macd
from study_tvlote24 import cci
from study_tvlote25 import run_loop, posflat, wilder_rsi, hh, ll, ITF, Z, NAN, roll
from study_tvlote26 import flat_pos
from study_tvlote27 import rev_or_long


def st_dir(h, l, c, n, mult, src=None):
    return _st((h + l) / 2 if src is None else src, c, np.nan_to_num(T.atr_rma(h, l, c, n)), mult)[0]


# ------------------------------------------------------------------ 1. Stochastic (BiznesFilosof)
def run_sbf(name, df, mm, tag, rows=None, verbose=True, lv=14, long_ok=True, short_ok=True, **extra):
    """%K(21, 3) cruza a %D para cima no mesmo candle em que cruza 14 para cima compra; cruza para baixo junto com
    86 vende; inverte."""
    o, h, l, c = ohlc(df); k = T.sma(stoch(c, h, l, 21), 3); d = T.sma(k, 3); z = 0 * c
    L = T.xover(k, d) & T.xover(k, z + lv); S = T.xunder(k, d) & T.xunder(k, z + 100 - lv)
    return run_g(name, df, gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Kozlod 3 MA
def run_k3ma(name, df, mm, tag, rows=None, verbose=True, typ='sma', long_ok=True, short_ok=True, **extra):
    """SMA5 cruza a SMA20 para cima com SMA20 > SMA100 compra; espelho vende; inverte (SL/PT desligados)."""
    o, h, l, c = ohlc(df); f = T.sma if typ == 'sma' else ema
    a, b, d = f(c, 5), f(c, 20), f(c, 100)
    L = T.xover(a, b) & (b > d); S = T.xunder(a, b) & (b < d)
    return run_g(name, df, gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. PlanB Quant Investing 101
def run_planb(name, df, mm, tag, rows=None, verbose=True, top=90, long_ok=True, short_ok=True, **extra):
    """Menor RSI14 das 6 barras anteriores < 50 e RSI atual 2 pontos acima dele compra; maior RSI das 6 anteriores > 90
    e RSI atual < 65 vende; inverte."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 14); mn, mx = sh(ll(r_, 6)), sh(hh(r_, 6))
    L = (mn < 50) & (r_ > mn + 2); S = (mx > top) & (r_ < 65)
    return run_g(name, df, gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Crypto Crew University (MFI/RSI/StochRSI)
def run_ccu(name, df, mm, tag, rows=None, verbose=True, th=20, long_ok=True, short_ok=True, **extra):
    """MFI14 e RSI14 do hlc3, %K e %D do Stoch RSI (14, 14, 3, 3) todos abaixo de 20 compra, todos acima de 80 vende;
    inverte; stop 20%."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); tp = (h + l + c) / 3
    mf = T.mfi(tp, v, 14); r_ = wilder_rsi(tp, 14); r1 = wilder_rsi(c, 14)
    k = T.sma(stoch(r1, r1, r1, 14), 3); d = T.sma(k, 3)
    L = (mf < th) & (r_ < th) & (k < th) & (d < th); S = (mf > 100 - th) & (r_ > 100 - th) & (k > 100 - th) & (d > 100 - th)
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok, slp=0.2)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Bitcoin SuperFlip
def run_sflip(name, df, mm, tag, rows=None, verbose=True, fac=1.8, long_ok=True, short_ok=True, **extra):
    """SuperTrend(10, 1,8) vira para cima com close > EMA200 compra, para baixo com close < EMA200 vende; toda virada
    contraria fecha (ADX, SL e TP vem desligados)."""
    o, h, l, c = ohlc(df); t = st_dir(h, l, c, 10, fac); e = ema(c, 200)
    up = (t == 1) & (sh(t) == -1); dn = (t == -1) & (sh(t) == 1)
    r = gsim(df, mm, up & (c > e), dn & (c < e), dn, up, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Price Action + Bollinger
def run_pab(name, df, mm, tag, rows=None, verbose=True, ln=21, long_ok=True, short_ok=True, **extra):
    """Vela grande (corpo > 2x a media de 100) de baixa fechando abaixo da BB(21, 2,1), seguida de vela de alta com
    menos da metade do corpo compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); bar = np.sign(c - o); body = np.abs(c - o); ab = T.sma(body, 100)
    m = T.sma(c, ln); dv = 2.1 * roll(c, ln).std(ddof=0).to_numpy()
    base = (body < sh(body) / 2) & (sh(body) > sh(ab) * 2)
    S = base & (sh(bar) == 1) & (bar == -1) & (sh(c) > sh(m + dv))
    L = base & (sh(bar) == -1) & (bar == 1) & (sh(c) < sh(m - dv))
    return run_g(name, df, gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. FX Sniper T3-CCI
def run_t3cci(name, df, mm, tag, rows=None, verbose=True, cp=14, long_ok=True, short_ok=True, **extra):
    """T3 (5, 0,618) do CCI14 do close: acima de 0 comprado, abaixo vendido; sempre posicionado."""
    o, h, l, c = ohlc(df); x = np.nan_to_num(cci(c, cp)); b = 0.618; b2, b3 = b * b, b ** 3
    w1 = 2 / (1 + 0.5 * 4 + 1); e = [ema(x, 0)] if False else None
    es = []; s = x
    for _ in range(6):
        s = pd.Series(s).ewm(alpha=w1, adjust=False).mean().to_numpy(); es.append(s)
    e1, e2, e3, e4, e5, e6 = es
    xr = -b3 * e6 + 3 * (b2 + b3) * e5 - 3 * (2 * b2 + b + b3) * e4 + (1 + 3 * b + b3 + 3 * b2) * e3
    t = pd.Series(np.where(xr > 0, 1.0, np.where(xr < 0, -1.0, np.nan))).ffill().fillna(0).to_numpy()
    return run_g(name, df, posflat(df, mm, flat_pos(t, long_ok, short_ok), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. PMax (Profit Maximizer)
def run_pmax(name, df, mm, tag, rows=None, verbose=True, mult=3.0, long_ok=True, short_ok=False, **extra):
    """EMA10 do hl2 com stop de 3 x ATR10 (PMax): media cruza o PMax para cima compra, para baixo fecha (o padrao e
    so comprado; ambos inverte)."""
    o, h, l, c = ohlc(df); src = (h + l) / 2; m = ema(src, 10); a = np.nan_to_num(T.atr_rma(h, l, c, 10)); n = len(c)
    ls = m - mult * a; ss = m + mult * a; dr = np.ones(n); pm = np.zeros(n)
    for i in range(1, n):
        lp, sp = ls[i - 1], ss[i - 1]
        ls[i] = max(ls[i], lp) if m[i] > lp else ls[i]
        ss[i] = min(ss[i], sp) if m[i] < sp else ss[i]
        dr[i] = 1 if (dr[i - 1] == -1 and m[i] > sp) else (-1 if (dr[i - 1] == 1 and m[i] < lp) else dr[i - 1])
        pm[i] = ls[i] if dr[i] == 1 else ss[i]
    pm[0] = ls[0]
    return run_g(name, df, rev_or_long(df, mm, T.xover(m, pm), T.xunder(m, pm), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Golden Vector Trend Orchestrator
def run_gvto(name, df, mm, tag, rows=None, verbose=True, adx_t=25, long_ok=True, short_ok=True, **extra):
    """SuperTrend(14, 3,5) de alta, close > EMA200, ADX14 >= 25 e DI+ > DI- (no primeiro candle em que tudo vale)
    compra; espelho vende; fecha quando o SuperTrend vira."""
    o, h, l, c = ohlc(df); t = st_dir(h, l, c, 14, 3.5); e = ema(c, 200); p, m_, ad = dmi(h, l, c, 14)
    lc = (t == 1) & (c > e) & (ad >= adx_t) & (p > m_); sc = (t == -1) & (c < e) & (ad >= adx_t) & (m_ > p)
    L = lc & ~(sh(lc.astype(float)) == 1); S = sc & ~(sh(sc.astype(float)) == 1)
    r = gsim(df, mm, L, S, t == -1, t == 1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Heikin Ashi Price Action (long-only)
def run_hapa(name, df, mm, tag, rows=None, verbose=True, ha=True, long_ok=True, short_ok=False, **extra):
    """So long: close HA acima da maxima HA anterior, vela HA verde e maxima HA anterior acima da de 2 barras atras
    compra; vela HA vermelha fechando abaixo da minima HA anterior fecha (ambos: o espelho vende)."""
    o, h, l, c = ohlc(df)
    if ha: o, h, l, c = heikin(o, h, l, c)
    L = (c > sh(h)) & (c > o) & (sh(h) > sh(h, 2)); S = (c < o) & (c < sh(l))
    return run_g(name, df, rev_or_long(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. L2 Reversal Labels (blackcat)
def run_l2r(name, df, mm, tag, rows=None, verbose=True, tpsl=True, long_ok=True, short_ok=True, **extra):
    """MACD(12, 26, 9) cruza o sinal para cima com close abaixo e MACD acima dos valores do cruzamento de alta anterior
    (divergencia) compra; espelho vende; inverte; stop 2 ATR14 e alvo 3 ATR; 3 barras de espera entre sinais."""
    o, h, l, c = ohlc(df); d, s = macd(c); a = T.atr_rma(h, l, c, 14); n = len(c)
    xu, xd = T.xover(d, s), T.xunder(d, s); L = np.zeros(n, bool); S = np.zeros(n, bool)
    pu = pd_ = -1; last = -99; st = 0
    for i in range(n):
        lo = xu[i] and pu >= 0 and c[pu] > c[i] and d[i] > d[pu]
        so = xd[i] and pd_ >= 0 and c[pd_] < c[i] and d[pd_] > d[i]
        ok = i - last > 3
        le = lo and st <= 0 and ok; se = so and st >= 0 and ok and short_ok
        if le and not se: L[i] = True; st = 1; last = i
        elif se and not le: S[i] = True; st = -1; last = i
        if xu[i]: pu = i
        if xd[i]: pd_ = i
    kw = dict(SLL=c - 2 * a, TPL=c + 3 * a, SLS=c + 2 * a, TPS=c - 3 * a) if tpsl else {}
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. SuperTrend Cloud
def _st_cloud(h, l, c, a, m):
    n = len(c); up = np.zeros(n); dn = np.zeros(n); t = np.ones(n); line = np.zeros(n)
    for i in range(n):
        ul = (h[i] + l[i]) / 2 - m * a[i]; dl = (h[i] + l[i]) / 2 + m * a[i]
        if i:
            up[i] = max(ul, up[i - 1]) if c[i - 1] > up[i - 1] else ul
            dn[i] = min(dl, dn[i - 1]) if c[i - 1] < dn[i - 1] else dl
            t[i] = 1 if c[i] > dn[i - 1] else (-1 if c[i] < up[i - 1] else t[i - 1])
        else:
            up[i], dn[i] = ul, dl
        line[i] = up[i] if t[i] == 1 else dn[i]
    return line


def run_stc(name, df, mm, tag, rows=None, verbose=True, m1=2.4, m2=4.8, long_ok=True, short_ok=True, **extra):
    """Duas SuperTrends (ATR4 x 2,4 e x 4,8): close cruza uma estando acima da outra compra (espelho vende); fecha
    quando o close entra na nuvem entre as duas."""
    o, h, l, c = ohlc(df); a = np.nan_to_num(T.atr_rma(h, l, c, 4)); s1, s2 = _st_cloud(h, l, c, a, m1), _st_cloud(h, l, c, a, m2)
    L = (T.xover(c, s1) & (c > s2)) | (T.xover(c, s2) & (c > s1)); S = (T.xunder(c, s1) & (c < s2)) | (T.xunder(c, s2) & (c < s1))
    X = (T.xunder(c, s1) & (c > s2)) | (T.xover(c, s1) & (c < s2)) | (T.xunder(c, s2) & (c > s1)) | (T.xover(c, s2) & (c < s1))
    r = gsim(df, mm, L, S & ~L, X, X, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Moving Average (BiznesFilosof)
def run_mab(name, df, mm, tag, rows=None, verbose=True, ln=21, long_ok=True, short_ok=True, **extra):
    """Close cruza a SMA21 para cima compra, para baixo vende; inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, ln)
    return run_g(name, df, gsim(df, mm, T.xover(c, m), T.xunder(c, m), rev=True, long_ok=long_ok, short_ok=short_ok),
                 tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Hull MA vs Candle
def run_hvc(name, df, mm, tag, rows=None, verbose=True, ln=50, long_ok=True, short_ok=True, **extra):
    """Sobre a abertura: abertura > HMA50 > abertura do dia e abertura subindo compra; espelho vende; abertura < HMA <
    abertura do dia fecha o long (espelho no short)."""
    o, h, l, c = ohlc(df); hm = T.hma(o, ln); d = df.open.groupby(df.index.normalize()).transform('first').to_numpy()
    L = (o > hm) & (hm > d) & (o > sh(o)); S = (o < hm) & (hm < d) & (o < sh(o))
    XL = (o < hm) & (hm < d); XS = (o > hm) & (hm > d)
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Bollinger Breakout (long-only, stop)
def run_bbw(name, df, mm, tag, rows=None, verbose=True, ln=20, tight=False, **extra):
    """So long: ordem stop na banda superior (BB20, 2) compra pelo pavio; stop de saida na banda inferior (tight: o
    maior entre a banda e entrada - 8%)."""
    o, h, l, c = ohlc(df); b = T.sma(c, ln); d = 2 * roll(c, ln).std(ddof=0).to_numpy()
    kl = 0.08 * c if tight else None
    return run_stp(name, df, tag, rows, verbose, extra, b + d, np.full(len(c), NAN), LX=b - d, KL=kl, short_ok=False)


# ------------------------------------------------------------------ 16. RCI
def rci(x, n):
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), n)
    rp = W.argsort(1).argsort(1) + 1; rt = np.arange(1, n + 1)
    out = np.full(len(x), NAN); d2 = ((rt - rp) ** 2).sum(1)
    out[n - 1:] = (1 - 6 * d2 / (n * (n * n - 1))) * 100
    return out


def run_rci(name, df, mm, tag, rows=None, verbose=True, ln=10, long_ok=True, short_ok=True, **extra):
    """RCI10 cruza a sua SMA14 para cima compra, para baixo vende; inverte."""
    o, h, l, c = ohlc(df); r_ = rci(c, ln); m = T.sma(r_, 14)
    return run_g(name, df, gsim(df, mm, T.xover(r_, m), T.xunder(r_, m), rev=True, long_ok=long_ok, short_ok=short_ok),
                 tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. Heikin Ashi MACD
def run_hamacd(name, df, mm, tag, rows=None, verbose=True, sltp=True, long_ok=True, short_ok=True, **extra):
    """MACD de DEMAs feitas com SMA (12, 25, sinal SMA15) sobre o close Heikin Ashi: delta cruza 0 para cima compra,
    para baixo vende; inverte; alvo 10% e stop 3% (a ordem stop no close virou mercado)."""
    o, h, l, c = ohlc(df); hc = (o + h + l + c) / 4
    dm = lambda n: 2 * T.sma(hc, n) - T.sma(T.sma(hc, n), n)
    ml = dm(12) - dm(25); dl = ml - T.sma(ml, 15)
    kw = dict(slp=0.03, tpp=0.10) if sltp else {}
    r = gsim(df, mm, T.xover(dl, 0 * c), T.xunder(dl, 0 * c), rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. Gaussian Channel
def gauss(x, per, N):
    beta = (1 - math.cos(2 * math.pi / per)) / (1.414 ** (2 / N) - 1); a = -beta + math.sqrt(beta * beta + 2 * beta)
    xx = 1 - a; co = [(-1) ** (k + 1) * math.comb(N, k) * xx ** k for k in range(1, N + 1)]
    s = np.nan_to_num(np.asarray(x, float)); f = np.zeros(len(s))
    for i in range(len(s)):
        v = a ** N * s[i]
        for k in range(1, N + 1):
            if i - k >= 0: v += co[k - 1] * f[i - k]
        f[i] = v
    return f


def run_gch(name, df, mm, tag, rows=None, verbose=True, per=144, long_ok=True, short_ok=True, **extra):
    """Filtro gaussiano de 4 polos (periodo 144) do hlc3: o preco cruza o filtro para cima (ou esta acima ate 3 barras
    depois do cruzamento) compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); s = (h + l + c) / 3; f = gauss(s, per, 4)
    u, d = T.xover(s, f), T.xunder(s, f)
    L = u | ((s > f) & (T.barssince(u) <= 3)); S = d | ((s < f) & (T.barssince(d) <= 3))
    return run_g(name, df, gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Tres medias (SMA 7/25/99)
def run_sma3(name, df, mm, tag, rows=None, verbose=True, sl=25, long_ok=True, short_ok=True, **extra):
    """SMA7 cruza a SMA25 para cima compra, para baixo vende; inverte (a SMA99 so desenha)."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, 7), T.sma(c, sl)
    return run_g(name, df, gsim(df, mm, T.xover(a, b), T.xover(b, a), rev=True, long_ok=long_ok, short_ok=short_ok),
                 tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Babypips Inside Bar Momentum
def run_ibm(name, df, mm, tag, rows=None, verbose=True, tpk=0.8, long_ok=True, short_ok=True, **extra):
    """Barra interna com a vela-mae de alta: stop de compra 10% da faixa da mae acima da maxima dela, stop de perda
    20% abaixo da maxima e alvo 80% acima (espelho na mae de baixa); stop e alvo valem a partir da barra seguinte a entrada; um novo sinal cancela a ordem e fecha a posicao."""
    o, h, l, c = ohlc(df); n = len(c); rg = sh(h) - sh(l); ib = (sh(h) > h) & (sh(l) < l)
    bull, bear = sh(o) < sh(c), sh(o) > sh(c)
    EI, EJ, ES, PI, PO = [], [], [], [], []
    pos = 0; pend = None; ent = 0.0; i0 = 0; sl = tp = 0.0
    def close_(j, px):
        EI.append(i0); EJ.append(j); ES.append(pos); PI.append(ent); PO.append(px)
    for j in range(1, n):
        i = j - 1
        if pend is not None and pos == 0:
            s_, lv, s_l, t_ = pend
            if (s_ == 1 and h[j] >= lv) or (s_ == -1 and l[j] <= lv):
                pos = s_; ent = max(o[j], lv) if s_ == 1 else min(o[j], lv); i0 = j; sl, tp = s_l, t_; pend = None
        if pos == 1:
            if j == i0: pass
            elif l[j] <= sl: close_(j, min(o[j], sl)); pos = 0
            elif h[j] >= tp: close_(j, max(o[j], tp)); pos = 0
        elif pos == -1:
            if j == i0: pass
            elif h[j] >= sl: close_(j, max(o[j], sl)); pos = 0
            elif l[j] <= tp: close_(j, min(o[j], tp)); pos = 0
        if ib[j] and (bull[j] or bear[j]):
            s_ = 1 if bull[j] else -1
            if (s_ == 1 and not long_ok) or (s_ == -1 and not short_ok): continue
            if pos and j + 1 < n: close_(j + 1, o[j + 1]); pos = 0
            hp, lp = h[i], l[i]
            pend = (1, hp + rg[j] * 0.1, hp - rg[j] * 0.2, hp + rg[j] * tpk) if s_ == 1 else \
                   (-1, lp - rg[j] * 0.1, lp + rg[j] * 0.2, lp - rg[j] * tpk)
    r = tuple(np.array(x, t) for x, t in zip((EI, EJ, ES, PI, PO), (np.int64, np.int64, np.int64, float, float)))
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


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

        g2('sbf', run_sbf, "1. Stochastic (BiznesFilosof)", 'lv', (14, 20), lambda v: f'{v}/{100 - v}', '14/86 ambos')
        g2('k3ma', run_k3ma, "2. Kozlod 3 MA", 'typ', ('sma', 'ema'), str, 'sma ambos')
        g2('planb', run_planb, "3. PlanB Quant Investing 101", 'top', (90, 80), lambda v: f'top{v}', 'top90 ambos')
        g2('ccu', run_ccu, "4. Crypto Crew University (MFI/RSI/StochRSI)", 'th', (20, 30), lambda v: f'th{v}', 'th20 ambos')
        g2('sflip', run_sflip, "5. Bitcoin SuperFlip", 'fac', (1.8, 3.0), lambda v: f'f{v:g}', 'f1.8 ambos')
        g2('pab', run_pab, "6. Price Action + Bollinger", 'ln', (21, 50), lambda v: f'bb{v}', 'bb21 ambos')
        g2('t3cci', run_t3cci, "7. FX Sniper T3-CCI", 'cp', (14, 50), lambda v: f'cci{v}', 'cci14 ambos')
        g2('pmax', run_pmax, "8. PMax", 'mult', (3.0, 1.5), lambda v: f'm{v:g}', 'm3 long')
        g2('gvto', run_gvto, "9. Golden Vector Trend Orchestrator", 'adx_t', (25, 0), lambda v: f'adx{v}', 'adx25 ambos')
        g2('hapa', run_hapa, "10. Heikin Ashi Price Action", 'ha', (True, False), lambda v: 'ha' if v else 'velas', 'ha long')
        g2('l2r', run_l2r, "11. L2 Reversal Labels", 'tpsl', (True, False), lambda v: 'tpsl' if v else 'semtpsl', 'tpsl ambos')
        grid('stc', run_stc, "12. SuperTrend Cloud", TFS, 'm2.4/4.8 ambos',
             [(f'm{a:g}/{b:g} {s}', dict(m1=a, m2=b, **sk(s))) for (a, b), s in itertools.product(((2.4, 4.8), (1.2, 2.4)), side2)])
        g2('mab', run_mab, "13. Moving Average (BiznesFilosof)", 'ln', (21, 50), lambda v: f'sma{v}', 'sma21 ambos')
        g2('hvc', run_hvc, "14. Hull MA vs Candle", 'ln', (50, 100), lambda v: f'h{v}', 'h50 ambos', ITF)
        grid('bbw', run_bbw, "15. Bollinger Breakout (long-only, stop)", TFS, 'bb20 banda',
             [(f'bb{a} ' + ('8%' if t else 'banda'), dict(ln=a, tight=t)) for a, t in itertools.product((20, 50), (False, True))])
        g2('rci', run_rci, "16. RCI", 'ln', (10, 30), lambda v: f'rci{v}', 'rci10 ambos')
        g2('hamacd', run_hamacd, "17. Heikin Ashi MACD", 'sltp', (True, False), lambda v: 'tp10 sl3' if v else 'semsltp', 'tp10 sl3 ambos')
        g2('gch', run_gch, "18. Gaussian Channel", 'per', (144, 50), lambda v: f'p{v}', 'p144 ambos')
        g2('sma3', run_sma3, "19. Tres medias (SMA 7/25/99)", 'sl', (25, 99), lambda v: f'7/{v}', '7/25 ambos')
        g2('ibm', run_ibm, "20. Babypips Inside Bar Momentum", 'tpk', (0.8, 2.0), lambda v: f'tp{v:g}', 'tp0.8 ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote28')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
