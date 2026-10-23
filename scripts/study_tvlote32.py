"""Lote 32 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 a 31
(ver docs/LOTE32_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote32.py xau us100 wti btc eth
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
from study_tvlote22 import run_stp, meandev
from study_tvlote23 import vwap_d
from study_tvlote25 import posflat, wilder_rsi, hh, ll, ffill, Z, NAN, roll, run_loop
from study_tvlote26 import flat_pos
from study_tvlote30 import R, K, supertrend
from study_tvlote31 import psar

NA = lambda c: np.full(len(c), NAN)


def chand(h, l, c, a, wick=False):
    """Stop no estilo Chandelier sobre hl2 (o 'SuperTrend' dos scripts BF): devolve a direcao (+1 alta)."""
    n = len(c); hl2 = (h + l) / 2; ls = hl2 - a; ss = hl2 + a; d = np.ones(n)
    for i in range(1, n):
        if a[i] != a[i]: continue
        lp = ls[i - 1] if ls[i - 1] == ls[i - 1] else ls[i]; sp = ss[i - 1] if ss[i - 1] == ss[i - 1] else ss[i]
        if c[i - 1] > lp: ls[i] = max(ls[i], lp)
        if c[i - 1] < sp: ss[i] = min(ss[i], sp)
        d[i] = 1 if (d[i - 1] == -1 and c[i] > sp) else (-1 if (d[i - 1] == 1 and c[i] < lp) else d[i - 1])
    return d


def stop_loop(name, df, tag, rows, verbose, extra, L, S, sl, long_ok, short_ok, delay=True):
    """Inverte nos sinais; stop fixo de sl% da entrada (a partir da barra seguinte se delay); so comprado: o sinal
    de venda fecha."""
    o, h, l, c = ohlc(df)

    def ex(j, pos, ent, st):
        if st.get('n', 0) > 0 or not delay:
            if pos > 0 and l[j] <= ent * (1 - sl): return 1, min(o[j], ent * (1 - sl))
            if pos < 0 and h[j] >= ent * (1 + sl): return 1, max(o[j], ent * (1 + sl))
        st['n'] = st.get('n', 0) + 1
        if pos > 0 and not short_ok and S[j]: return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 1. Hurst Future Lines of Demarcation
def run_hfl(name, df, mm, tag, rows=None, verbose=True, cyc=20, long_ok=True, short_ok=True, **extra):
    """FLD = ohlc4 deslocado de metade do ciclo (sinal 5, trade 20, tendencia 80); maquina de estados A..H:
    ohlc4 cruzando acima da FLD de sinal no estado A compra, abaixo no estado F vende; ohlc4 cruzando a FLD de
    trade no sentido contrario fecha."""
    o, h, l, c = ohlc(df); p = (o + h + l + c) / 4; hr = lambda n: int(n / 2 + 0.5)
    sg, tr, td = sh(p, hr(5)), sh(p, hr(cyc)), sh(p, hr(4 * cyc)); n = len(c); st = np.zeros(n); s = 0
    for i in range(n):
        if sg[i] > tr[i] and tr[i] > td[i]: s = 1
        if s == 1 and p[i] < sg[i]: s = 2
        if sg[i] < tr[i] and tr[i] > td[i]: s = 3
        if s == 3 and p[i] < sg[i]: s = 4
        if sg[i] < tr[i] and tr[i] < td[i]: s = 5
        if s == 5 and p[i] < sg[i]: s = 6
        if sg[i] > tr[i] and tr[i] < td[i]: s = 7
        if s == 7 and p[i] < sg[i]: s = 8
        st[i] = s
    L = T.xover(p, sg) & (st == 1); S = T.xunder(p, sg) & (st == 6)
    res = gsim(df, mm, L, S & ~L, T.xunder(p, tr), T.xover(p, tr), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Super Trend Daily BF
def run_stdbf(name, df, mm, tag, rows=None, verbose=True, mult=1.3, long_ok=True, short_ok=True, **extra):
    """Stop ATR3 x 1,3 (estilo Chandelier) virando para cima com |EMA15 do ROC30| > 3% compra, para baixo vende;
    inverte; stop fixo de 6% a partir da barra seguinte a entrada."""
    o, h, l, c = ohlc(df); d = chand(h, l, c, mult * T.atr_rma(h, l, c, 3))
    roc = 100 * (c - sh(c, 30)) / sh(c, 30); er = ema(np.nan_to_num(roc), 15); mv = np.abs(er) > 3
    L = (d == 1) & (sh(d) == -1) & mv; S = (d == -1) & (sh(d) == 1) & mv
    return stop_loop(name, df, tag, rows, verbose, extra, L, S, 0.06, long_ok, short_ok)


# ------------------------------------------------------------------ 3. Ultimate Scalping v2 (EMA + VWAP)
def run_usc(name, df, mm, tag, rows=None, verbose=True, tpm=2.0, long_ok=True, short_ok=True, **extra):
    """EMA9 cruzando acima da EMA21 com close acima da VWAP do dia compra (espelho vende); stop 1,5 ATR14 e alvo
    2 ATR14 a partir do close do sinal; o sinal contrario inverte."""
    o, h, l, c = ohlc(df); a, b = ema(c, 9), ema(c, 21); vw = vwap_d(df); at = T.atr_rma(h, l, c, 14)
    L = T.xover(a, b) & (c > vw); S = T.xunder(a, b) & (c < vw)
    res = gsim(df, mm, L, S, SLL=c - 1.5 * at, TPL=c + tpm * at, SLS=c + 1.5 * at, TPS=c - tpm * at, rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. SuperTrend Enhanced Pivot Reversal
def run_prv(name, df, mm, tag, rows=None, verbose=True, fac=2.618, long_ok=True, short_ok=True, **extra):
    """Pivo de maxima (6/3) ainda nao rompido com Supertrend(5, 2,618) de alta arma stop de compra na maxima do
    pivo (espelho no pivo de minima); stop de 20% do nivel do pivo. So comprado: o stop de venda fecha."""
    o, h, l, c = ohlc(df); _, d = supertrend(h, l, c, 5, fac); n = len(c)
    hp = ffill(np.where(T.pivothigh(h, 6, 3), sh(h, 3), NAN)); lp = ffill(np.where(T.pivotlow(l, 6, 3), sh(l, 3), NAN))
    ph, pl = T.pivothigh(h, 6, 3), T.pivotlow(l, 6, 3); le = np.zeros(n, bool); se = np.zeros(n, bool)
    for i in range(1, n):
        le[i] = True if ph[i] else (False if (le[i - 1] and h[i] > hp[i]) else le[i - 1])
        se[i] = True if pl[i] else (False if (se[i - 1] and l[i] < lp[i]) else se[i - 1])
    LE = np.where(le & (d == -1), hp, NAN); SE = np.where(se & (d == 1), lp, NAN)
    if short_ok:
        return run_stp(name, df, tag, rows, verbose, extra, LE, SE, KL=0.2 * hp, KS=0.2 * lp, long_ok=long_ok)
    return run_stp(name, df, tag, rows, verbose, extra, LE, NA(c), SE, KL=0.2 * hp, short_ok=False)


# ------------------------------------------------------------------ 5. HMA 200 + EMA 20
def run_hme(name, df, mm, tag, rows=None, verbose=True, hl=200, long_ok=True, short_ok=True, **extra):
    """Close acima da HMA200 cruzando acima da EMA20 compra, abaixo da HMA cruzando abaixo vende; inverte."""
    o, h, l, c = ohlc(df); hm, e = T.hma(c, hl), ema(c, 20)
    return R(name, df, mm, tag, rows, verbose, extra, (c > hm) & T.xover(c, e), (c < hm) & T.xunder(c, e), long_ok, short_ok)


# ------------------------------------------------------------------ 6. Ichimoku Cloud with RSI (Coinrule)
def run_irs(name, df, mm, tag, rows=None, verbose=True, rl=50, long_ok=True, short_ok=True, **extra):
    """Tenkan>kijun, momentum de 25 positivo e close acima da nuvem deslocada com RSI14<50 compra; o espelho com
    RSI>50 vende; inverte (so comprado: o sinal baixista, sem RSI, fecha). Ordens no close viraram abertura seguinte."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2; tk, kj = dc(9), dc(26)
    A, B = sh((tk + kj) / 2, 25), sh(dc(52), 25); mo = c - sh(c, 25); r = wilder_rsi(c, 14)
    bu = (tk > kj) & (mo > 0) & (c > np.maximum(A, B)); be = (tk < kj) & (mo < 0) & (c < np.minimum(A, B))
    L = bu & (r < rl)
    if short_ok:
        return R(name, df, mm, tag, rows, verbose, extra, L, be & (r > 100 - rl), long_ok, True)
    return run_g(name, df, gsim(df, mm, L, Z(c), be, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. AK RSI 2
def run_r2(name, df, mm, tag, rows=None, verbose=True, lv=(5, 90), long_ok=True, short_ok=True, **extra):
    """Close acima da SMA200 e abaixo da SMA5 com RSI2<5 compra; espelho (RSI2>90) vende; os dois close_all do
    script (close acima e abaixo da SMA5) zeram a posicao no fechamento de qualquer barra, logo cada trade dura
    uma barra."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 2); m5, m200 = T.sma(c, 5), T.sma(c, 200)
    L = (c > m200) & (c < m5) & (r < lv[0]); S = (c < m200) & (c > m5) & (r > lv[1]); X = c != m5
    res = gsim(df, mm, L, S & ~L, X, X, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. QuantNomad SuperTrend
def run_qst(name, df, mm, tag, rows=None, verbose=True, mult=2.0, long_ok=True, short_ok=True, **extra):
    """SuperTrend (ATR14 x 2): ordens stop de compra e de venda na linha, sempre posicionado (so comprado: o stop
    de venda fecha)."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 14); hl2 = (h + l) / 2; n = len(c)
    up = np.zeros(n); dn = np.zeros(n); tr = np.ones(n)
    for i in range(1, n):
        u, d_ = hl2[i] - mult * a[i], hl2[i] + mult * a[i]
        if u != u: continue
        up[i] = max(u, up[i - 1]) if c[i - 1] > up[i - 1] else u
        dn[i] = min(d_, dn[i - 1]) if c[i - 1] < dn[i - 1] else d_
        tr[i] = 1 if c[i] > dn[i - 1] else (-1 if c[i] < up[i - 1] else tr[i - 1])
    stl = np.where(tr == 1, up, dn); stl[np.isnan(a)] = NAN
    LE = np.where(tr == -1, stl, NAN); SE = np.where(tr == 1, stl, NAN)
    if short_ok:
        return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok)
    return run_stp(name, df, tag, rows, verbose, extra, LE, NA(c), SE, short_ok=False)


# ------------------------------------------------------------------ 9. Grant's PSAR (long-only)
def run_gps(name, df, mm, tag, rows=None, verbose=True, st=0.013, mx=0.2, **extra):
    """So long: com o SAR (0,013/0,005/0,2) acima da maxima, stop de compra no SAR; com o SAR abaixo da minima,
    stop de saida no SAR."""
    o, h, l, c = ohlc(df); ps = psar(h, l, c, st, 0.005, mx)[0]
    return run_stp(name, df, tag, rows, verbose, extra, np.where(ps > h, ps, NAN), NA(c), np.where(ps < l, ps, NAN),
                   short_ok=False)


# ------------------------------------------------------------------ 10. Donchian Channel (stop + EMA200)
def run_dcs(name, df, mm, tag, rows=None, verbose=True, ln=20, long_ok=True, short_ok=True, **extra):
    """Close acima da EMA200: stop de compra na maxima de 20; abaixo: stop de venda na minima de 20; saida do long
    em stop na minima de 20, do short na maxima."""
    o, h, l, c = ohlc(df); H, Lw = hh(h, ln), ll(l, ln); e = ema(c, 200)
    return run_stp(name, df, tag, rows, verbose, extra, np.where(c > e, H, NAN), np.where(c < e, Lw, NAN), Lw, H,
                   long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 11. RSI Divergence Strategy
def run_rdv(name, df, mm, tag, rows=None, verbose=True, le=35, long_ok=True, short_ok=True, **extra):
    """Divergencia regular do RSI14 (pivos 5/5, a 5..60 barras do anterior): alta com RSI<35 compra, baixa com
    RSI>76 vende; RSI>=80 fecha o long, RSI<=54,1 fecha o short; a entrada contraria inverte."""
    o, h, l, c = ohlc(df); r = wilder_rsi(c, 14); n = len(c); lb = 5
    pl, ph = T.pivotlow(r, lb, lb), T.pivothigh(r, lb, lb); bu = np.zeros(n, bool); be = np.zeros(n, bool)
    a = b = -1
    for i in range(n):
        if pl[i]:
            if a >= 0 and 5 <= i - a - 1 <= 60:
                bu[i] = l[i - lb] < l[a - lb] and r[i - lb] > r[a - lb]
            a = i
        if ph[i]:
            if b >= 0 and 5 <= i - b - 1 <= 60:
                be[i] = h[i - lb] > h[b - lb] and r[i - lb] < r[b - lb]
            b = i
    L = bu & (r < le); S = be & (r > 76)
    res = gsim(df, mm, L, S & ~L, r >= 80, r <= 54.1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. CCI & EMA (Tradeswithashish)
def run_cce(name, df, mm, tag, rows=None, verbose=True, ret=0.05, long_ok=True, short_ok=True, **extra):
    """Sem posicao: close acima da EMA100 dupla, vela de alta fechando no terco de cima, volume acima da SMA20 e do
    anterior, CCI100>0, CCI20>100 e close acima da VWAP do dia compra (espelho vende); stop = maior entre EMA50
    e EMA100 dupla (sobe com elas) e alvo de 5% do ohlc4; stop e alvo so ficam ativos depois de CCI100<0 ou close
    abaixo de uma das medias (espelho no short)."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); es = ema(ema(c, 100), 100); e2 = ema(c, 50)
    hlc = (h + l + c) / 3
    cci = lambda n: (hlc - T.sma(hlc, n)) / (0.015 * meandev(hlc, n))
    c100, c20 = cci(100), cci(20); vw = vwap_d(df); rg = np.where(h > l, (c - l) / np.where(h > l, h - l, 1), 0.5)
    vc = (v > T.sma(v, 20)) & (v > sh(v))
    L = (c > es) & (c > o) & vc & (c100 > 0) & (c20 > 100) & (c > vw) & (rg > 0.6)
    S = (c < es) & (c < o) & vc & (c100 < 0) & (c20 < -100) & (c < vw) & (rg < 0.4)
    o4 = (o + h + l + c) / 4; hi, lo = np.maximum(e2, es), np.minimum(e2, es)

    def ex(j, pos, ent, st):
        if 'sp' not in st:
            st['sp'] = hi[j - 1] if pos > 0 else lo[j - 1]; st['tg'] = o4[j - 1] * (1 + pos * ret)
        if st.get('arm'):
            sp, tg = st['sp'], st['tg']
            if pos > 0 and l[j] <= sp: return 1, min(o[j], sp)
            if pos < 0 and h[j] >= sp: return 1, max(o[j], sp)
            if pos > 0 and h[j] >= tg: return 1, max(o[j], tg)
            if pos < 0 and l[j] <= tg: return 1, min(o[j], tg)
        st['sp'] = max(st['sp'], hi[j]) if pos > 0 else min(st['sp'], lo[j])
        st['arm'] = (c100[j] < 0 or c[j] < es[j] or c[j] < e2[j]) if pos > 0 else (c100[j] > 0 or c[j] > es[j] or c[j] > e2[j])
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, rev=False, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 13. Hull MA_X + Ichimoku
def run_hic(name, df, mm, tag, rows=None, verbose=True, keh=12, long_ok=True, short_ok=True, **extra):
    """Hull dupla de 12 (atual vs barra anterior) para cima, close acima dela, do chikou (close de 23 barras atras)
    e da nuvem deslocada (9/24/51), com tenkan>=kijun ou close>kijun compra; espelho vende; fecha o long com a Hull
    virando e qualquer perda de linha (espelho no short)."""
    o, h, l, c = ohlc(df)
    hull = lambda x: T.wma(2 * T.wma(x, int(round(keh / 2))) - T.wma(x, keh), int(round(math.sqrt(keh))))
    n1, n2 = hull(c), hull(sh(c)); dc = lambda n: (hh(h, n) + ll(l, n)) / 2; tk, kj = dc(9), dc(24)
    A, B = sh((tk + kj) / 2, 23), sh(dc(51), 23); SH, SL = np.maximum(A, B), np.minimum(A, B); ch = sh(c, 23)
    L = (n1 > n2) & (c > n2) & (c > ch) & (c > SH) & ((tk >= kj) | (c > kj))
    S = (n1 < n2) & (c < n2) & (c < ch) & (c < SL) & ((tk <= kj) | (c < kj))
    XL = (n1 < n2) & ((c < n2) | (tk < kj) | (c < tk) | (c < kj) | (c < SH) | (c < ch))
    XS = (n1 > n2) & ((c > n2) | (tk > kj) | (c > tk) | (c > kj) | (c > SL) | (c > ch))
    res = gsim(df, mm, L, S & ~L, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Donchian Channels (KrisWaters)
def run_dkw(name, df, mm, tag, rows=None, verbose=True, atr_rule=False, long_ok=True, short_ok=False, **extra):
    """Stop de compra na maxima de 20 e saida em stop na minima de 10 (com a regra ATR: maior entre ela e abertura
    - 2 ATR20); o short (desligado no original) usa minima de 20 e maxima de 10."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 20)
    LX = np.maximum(ll(l, 10), o - 2 * a) if atr_rule else ll(l, 10)
    SX = np.minimum(hh(h, 10), o + 2 * a) if atr_rule else hh(h, 10)
    return run_stp(name, df, tag, rows, verbose, extra, hh(h, 20), ll(l, 20), LX, SX, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 15. Fisher Transform (Ehlers)
def run_fis(name, df, mm, tag, rows=None, verbose=True, ln=10, long_ok=True, short_ok=True, **extra):
    """Fisher de 10 sobre hl2 positivo fica comprado, negativo fica vendido."""
    o, h, l, c = ohlc(df); x = (h + l) / 2; mx, mn = hh(x, ln), ll(x, ln); n = len(c)
    v1 = 0.0; f = 0.0; p = np.zeros(n)
    for i in range(n):
        if mx[i] != mx[i] or mx[i] == mn[i]: p[i] = p[i - 1] if i else 0; continue
        v1 = 0.33 * 2 * ((x[i] - mn[i]) / (mx[i] - mn[i]) - 0.5) + 0.67 * v1
        v2 = min(max(v1, -0.999), 0.999) if abs(v1) > 0.99 else v1
        f = 0.5 * math.log((1 + v2) / (1 - v2)) + 0.5 * f
        p[i] = 1 if f > 0 else (-1 if f < 0 else (p[i - 1] if i else 0))
    return run_g(name, df, posflat(df, mm, flat_pos(p, long_ok, short_ok) * (p != 0)), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. SuperTrend Trapping Candle
def run_stt(name, df, mm, tag, rows=None, verbose=True, cd=0.003, long_ok=True, short_ok=True, **extra):
    """Supertrend(2, 10) de alta com candle pequeno (faixa < 0,3% do close) de baixa e volume forte compra; espelho
    vende; inverte."""
    o, h, l, c = ohlc(df); _, d = supertrend(h, l, c, 10, 2.0); v = df.volume.to_numpy(float)
    bd = (v < sh(v)) & (sh(v) < sh(v, 2)) & (c > sh(c)) & (sh(c) > sh(c, 2)) & (o > sh(o)) & (sh(o) > sh(o, 2))
    sd = (v < sh(v)) & (sh(v) < sh(v, 2)) & (c < sh(c)) & (sh(c) < sh(c, 2)) & (o < sh(o)) & (sh(o) < sh(o, 2))
    strong = (v > sh(v)) | bd | sd; small = (h - l) < c * cd
    L = (d == -1) & (c < o) & strong & small; S = (d == 1) & (c > o) & strong & small
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 17. Supertrend + RSI (Alorse)
def run_srs(name, df, mm, tag, rows=None, verbose=True, fac=3.0, long_ok=True, short_ok=False, **extra):
    """Supertrend(3, 10) virando para cima compra; RSI14>72 ou virada para baixo fecha; espelho no short (RSI<28),
    desligado no original."""
    o, h, l, c = ohlc(df); _, d = supertrend(h, l, c, 10, fac); r = wilder_rsi(c, 14); ch = d - sh(d)
    res = gsim(df, mm, ch < 0, ch > 0, (r > 72) | (ch > 0), (r < 28) | (ch < 0), rev=True, long_ok=long_ok,
               short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. TSI w SuperTrend decision
def run_tss(name, df, mm, tag, rows=None, verbose=True, per=64, long_ok=True, short_ok=True, **extra):
    """TSI = correlacao de 64 entre close e tempo; SuperTrend(10, 3) calculado sobre velas do proprio TSI: direcao
    de alta com TSI>-0,241 compra, de baixa com TSI<0,241 vende; as condicoes opostas fecham."""
    o, h, l, c = ohlc(df); t = pd.Series(c).rolling(per).corr(pd.Series(np.arange(len(c), dtype=float))).to_numpy()
    n = len(c); bo = sh(t); bo = np.where(np.isnan(bo), t, bo); bh, bl = np.maximum(bo, t), np.minimum(bo, t)
    tr = np.maximum(bh - bl, np.maximum(np.abs(bh - sh(t)), np.abs(bl - sh(t)))); tr[0] = bh[0] - bl[0]
    a = T.rma_nan(np.where(np.isnan(t), NAN, tr), 10); hl2 = (bh + bl) / 2
    up = np.zeros(n); dn = np.zeros(n); d = np.ones(n); st = np.zeros(n)
    for i in range(n):
        if t[i] != t[i] or a[i] != a[i]: continue
        u = hl2[i] + 3 * a[i]; w = hl2[i] - 3 * a[i]; pu = up[i - 1] if i else 0; pd_ = dn[i - 1] if i else 0
        pc = t[i - 1] if i and t[i - 1] == t[i - 1] else 0
        up[i] = u if (u < pu or pc > pu) else pu; dn[i] = w if (w > pd_ or pc < pd_) else pd_
        if i == 0 or a[i - 1] != a[i - 1]: d[i] = 1
        elif st[i - 1] == pu: d[i] = -1 if t[i] > up[i] else 1
        else: d[i] = 1 if t[i] < dn[i] else -1
        st[i] = dn[i] if d[i] == -1 else up[i]
    ok = ~np.isnan(t) & ~np.isnan(a)
    L = ok & (d < 0) & (t > -0.241); S = ok & (d > 0) & (t < 0.241)
    res = gsim(df, mm, L, S & ~L, S, L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Trend Following Parabolic (TradeDots)
def run_tfp(name, df, mm, tag, rows=None, verbose=True, rr=1.3, long_ok=True, short_ok=True, **extra):
    """Sem posicao: close acima da SMA200, EMA10 cruzando acima da EMA25 e SAR abaixo do close compra; stop na
    SMA200 e alvo de 1,3 x a distancia; espelho vende."""
    o, h, l, c = ohlc(df); ps = psar(h, l, c, 0.02, 0.02, 0.2)[0]; m = T.sma(c, 200); f, s = ema(c, 10), ema(c, 25)
    L = (c > m) & T.xover(f, s) & (ps < c); S = (c < m) & T.xover(s, f) & (ps > c)
    res = gsim(df, mm, L, S & ~L, SLL=m, TPL=c + (c - m) * rr, SLS=m, TPS=c - (m - c) * rr, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Kozlod MA Cross
def run_koz(name, df, mm, tag, rows=None, verbose=True, p=(5, 15), long_ok=True, short_ok=True, **extra):
    """SMA5 cruzando a SMA15 compra/vende; inverte (stop e alvo desligados no padrao)."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, p[0]), T.sma(c, p[1])
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(a, b), T.xunder(a, b), long_ok, short_ok)


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
        g2('hfl', run_hfl, "1. Hurst Future Lines of Demarcation", 'cyc', (20, 40), lambda v: f'c{v}', 'c20 ambos')
        g2('stdbf', run_stdbf, "2. Super Trend Daily BF", 'mult', (1.3, 2.6), lambda v: f'm{v:g}', 'm1.3 ambos')
        g2('usc', run_usc, "3. Ultimate Scalping v2 (EMA + VWAP)", 'tpm', (2.0, 3.0), lambda v: f'tp{v:g}atr', 'tp2atr ambos')
        g2('prv', run_prv, "4. SuperTrend Enhanced Pivot Reversal", 'fac', (2.618, 4.0), lambda v: f'f{v:g}', 'f2.618 ambos')
        g2('hme', run_hme, "5. HMA 200 + EMA 20", 'hl', (200, 100), lambda v: f'hma{v}', 'hma200 ambos')
        g2('irs', run_irs, "6. Ichimoku Cloud with RSI (Coinrule)", 'rl', (50, 101), lambda v: 'rsi50' if v == 50 else 'sem rsi', 'rsi50 ambos')
        g2('r2', run_r2, "7. AK RSI 2", 'lv', ((5, 90), (10, 80)), pr, '5/90 ambos')
        g2('qst', run_qst, "8. QuantNomad SuperTrend", 'mult', (2.0, 3.0), lambda v: f'm{v:g}', 'm2 ambos')
        g4('gps', run_gps, "9. Grant's PSAR (long-only)", 'st', (0.013, 0.02), 'mx', (0.2, 0.1),
           lambda a, b: f'{a:g}/{b:g}', '0.013/0.2')
        g2('dcs', run_dcs, "10. Donchian Channel (stop + EMA200)", 'ln', (20, 55), lambda v: f'd{v}', 'd20 ambos')
        g2('rdv', run_rdv, "11. RSI Divergence Strategy", 'le', (35, 50), lambda v: f'rsi<{v}', 'rsi<35 ambos')
        g2('cce', run_cce, "12. CCI & EMA (Tradeswithashish)", 'ret', (0.05, 0.10), lambda v: f'tp{v * 100:g}%', 'tp5% ambos')
        g2('hic', run_hic, "13. Hull MA_X + Ichimoku", 'keh', (12, 24), lambda v: f'h{v}', 'h12 ambos')
        g2('dkw', run_dkw, "14. Donchian Channels (KrisWaters)", 'atr_rule', (False, True),
           lambda v: 'atr' if v else 'canal', 'canal long', dict(short_ok=False))
        g2('fis', run_fis, "15. Fisher Transform (Ehlers)", 'ln', (10, 20), lambda v: f'l{v}', 'l10 ambos')
        g2('stt', run_stt, "16. SuperTrend Trapping Candle", 'cd', (0.003, 0.006), lambda v: f'{v * 100:g}%', '0.3% ambos')
        g2('srs', run_srs, "17. Supertrend + RSI (Alorse)", 'fac', (3.0, 2.0), lambda v: f'f{v:g}', 'f3 long',
           dict(short_ok=False))
        g2('tss', run_tss, "18. TSI w SuperTrend decision", 'per', (64, 32), lambda v: f'p{v}', 'p64 ambos')
        g2('tfp', run_tfp, "19. Trend Following Parabolic (TradeDots)", 'rr', (1.3, 2.0), lambda v: f'rr{v:g}', 'rr1.3 ambos')
        g2('koz', run_koz, "20. Kozlod MA Cross", 'p', ((5, 15), (10, 30)), pr, '5/15 ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote32')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
