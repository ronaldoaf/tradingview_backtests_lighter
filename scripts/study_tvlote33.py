"""Lote 33 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 a 32
(ver docs/LOTE33_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote33.py xau us100 wti btc eth
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
from study_tvlote22 import run_stp
from study_tvlote23 import vwap_d
from study_tvlote25 import posflat, wilder_rsi, hh, ll, Z, NAN, roll, run_loop
from study_tvlote30 import R, K, supertrend
from study_tvlote31 import psar
from study_tvlote32 import chand

NA = lambda c: np.full(len(c), NAN)
vol = lambda df: df.volume.to_numpy(float)


def vwma(x, v, n):
    return roll(x * v, n).sum().to_numpy() / roll(v, n).sum().to_numpy()


def truerange(h, l, c):
    pc = sh(c); return np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc)))


# ------------------------------------------------------------------ 1. PSAR + ADX + CMF + RSI (long-only)
def run_pac(name, df, mm, tag, rows=None, verbose=True, rl=50, cl=20, long_ok=True, short_ok=False, **extra):
    """So long: SAR (1,02/1,02/1,2, como no script) fora da alta, RSI(50)>49, ADX14 acima da sua EMA10 e CMF20>0
    compra; o espelho (SAR em alta, RSI<49, ADX abaixo da EMA, CMF<0) fecha."""
    o, h, l, c = ohlc(df); v = vol(df); up = psar(h, l, c, 1.02, 1.02, 1.2)[2]; r = wilder_rsi(c, rl)
    adx = dmi(h, l, c, 14)[2]; ae = ema(np.nan_to_num(adx), 10)
    with np.errstate(divide='ignore', invalid='ignore'):
        ad = np.where(h == l, 0.0, (2 * c - l - h) / (h - l) * v)
    mf = roll(ad, cl).sum().to_numpy() / roll(v, cl).sum().to_numpy()
    L = ~up & (r > 49) & (adx > ae) & (mf > 0); S = up & (r < 49) & (adx < ae) & (mf < 0)
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 2. Abdoli's Heikin Ashi Smoothed (long-only)
def run_haw(name, df, mm, tag, rows=None, verbose=True, ln=65, k=3, long_ok=True, short_ok=False, **extra):
    """So long: Heikin Ashi sobre as EMAs de 65 de OHLC; 3 velas verdes com o close HA subindo compra, 3 vermelhas
    caindo fecha."""
    o, h, l, c = ohlc(df); mo, mh, ml, mc = (ema(x, ln) for x in (o, h, l, c)); hc = (mo + mh + ml + mc) / 4
    ho = np.empty(len(c)); ho[0] = (mo[0] + mc[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    b = hc - ho; L = np.ones(len(c), bool); S = L.copy()
    for i in range(k):
        L &= sh(b, i) > 0 if i else b > 0; S &= sh(b, i) < 0 if i else b < 0
    for i in range(k - 1):
        x0 = hc if i == 0 else sh(hc, i)
        L &= x0 > sh(hc, i + 1); S &= x0 < sh(hc, i + 1)
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 3. Bar Counter Trend Reversal (TradeDots)
def run_bct(name, df, mm, tag, rows=None, verbose=True, mult=2, long_ok=True, short_ok=True, **extra):
    """3 closes caindo com minima abaixo do Keltner (EMA20 -/+ 2 EMA20 do TR) compra, uma vez por sequencia; 3
    subindo com maxima acima da banda vende; inverte."""
    o, h, l, c = ohlc(df); m = ema(c, 20); a = ema(np.nan_to_num(truerange(h, l, c)), 20)
    up, lo = m + mult * a, m - mult * a
    fall = (c < sh(c)) & (sh(c) < sh(c, 2)) & (sh(c, 2) < sh(c, 3))
    rise = (c > sh(c)) & (sh(c) > sh(c, 2)) & (sh(c, 2) > sh(c, 3))
    rr, fr = fall & (l < lo), rise & (h > up); n = len(c); L = np.zeros(n, bool); S = L.copy(); rp = fp = False
    for i in range(1, n):
        if c[i] > c[i - 1]: rp = False
        if c[i] < c[i - 1]: fp = False
        if rr[i] and not rp: L[i] = True; rp = True
        if fr[i] and not fp: S[i] = True; fp = True
    return R(name, df, mm, tag, rows, verbose, extra, L, S & ~L, long_ok, short_ok)


# ------------------------------------------------------------------ 4. VWMA with ATR stops (long-only)
def run_vat(name, df, mm, tag, rows=None, verbose=True, am=3.5, vl=33, long_ok=True, short_ok=False, **extra):
    """So long: trailing stop de 3,5 ATR33 sobre o close; RSI14 da VWMA33 >= 30, candle de alta, close acima da VWMA
    e trailing em alta compra; close cruzando abaixo do trailing fecha."""
    o, h, l, c = ohlc(df); vw = vwma(c, vol(df), vl); rv = wilder_rsi(vw, 14); nl = am * T.atr_rma(h, l, c, vl)
    n = len(c); ts = np.zeros(n); p = np.zeros(n)
    for i in range(1, n):
        pv = ts[i - 1]; d = nl[i] if nl[i] == nl[i] else 0.0
        if c[i] > pv and c[i - 1] > pv: ts[i] = max(pv, c[i] - d)
        elif c[i] < pv and c[i - 1] < pv: ts[i] = min(pv, c[i] + d)
        else: ts[i] = c[i] - d if c[i] > pv else c[i] + d
        p[i] = 1 if (c[i - 1] < pv and c[i] > pv) else (-1 if (c[i - 1] > pv and c[i] < pv) else p[i - 1])
    L = (rv >= 30) & (c > o) & (c > vw) & (p == 1)
    return R(name, df, mm, tag, rows, verbose, extra, L, T.xunder(c, ts), long_ok, short_ok)


# ------------------------------------------------------------------ 5. SMA200 bands (long-only)
def run_s200(name, df, mm, tag, rows=None, verbose=True, up=1.04, dn=0.97, long_ok=True, short_ok=False, **extra):
    """So long: close acima de SMA200 x 1,04 compra; abaixo de SMA200 x 0,97 fecha."""
    o, h, l, c = ohlc(df); m = T.sma(c, 200)
    return R(name, df, mm, tag, rows, verbose, extra, c > m * up, c < m * dn, long_ok, short_ok)


# ------------------------------------------------------------------ 6. TASC 2024.08 VCTS (long-only)
def run_vct(name, df, mm, tag, rows=None, verbose=True, thr=30, lv=25, long_ok=True, short_ok=False, **extra):
    """So long: ADX14>30, TTI (VWMA 13/26 com multiplicador de volume) acima do sinal SMA9 e VPCI (5/25)>0 compra;
    VPCI<0 fecha."""
    o, h, l, c = ohlc(df); v = vol(df); adx = dmi(h, l, c, 14)[2]
    f, s = vwma(c, v, 13), vwma(c, v, 26); vm = (f / s) ** 2; tti = f * vm - s / vm; sg = T.sma(tti, 9)
    with np.errstate(divide='ignore', invalid='ignore'):
        vp = (vwma(c, v, lv) - T.sma(c, lv)) * (vwma(c, v, 5) / T.sma(c, 5)) * (T.sma(v, 5) / T.sma(v, lv))
    return R(name, df, mm, tag, rows, verbose, extra, (adx > thr) & (tti > sg) & (vp > 0), vp < 0, long_ok, short_ok)


# ------------------------------------------------------------------ 7. Trend Bounce
def run_tbn(name, df, mm, tag, rows=None, verbose=True, nn=7, long_ok=True, short_ok=True, **extra):
    """Close acima da SMA200 e abaixo da minima de 7 anterior compra; abaixo da SMA200 e acima da maxima de 7
    anterior vende (inverte); close acima da maxima anterior fecha o long, abaixo da minima fecha o short; stop de
    2 x SMA10 do TR (da barra anterior a entrada) a partir da entrada."""
    o, h, l, c = ohlc(df); m = T.sma(c, 200); hi, lo = sh(hh(h, nn)), sh(ll(l, nn)); a = T.sma(truerange(h, l, c), 10)
    L = (c > m) & (c < lo); S = (c < m) & (c > hi)

    def ex(j, pos, ent, st):
        if 'd' not in st:
            st['d'] = 2 * a[j - 1]
        else:
            d = st['d']
            if d == d and pos > 0 and l[j] <= ent - d: return 1, min(o[j], ent - d)
            if d == d and pos < 0 and h[j] >= ent + d: return 1, max(o[j], ent + d)
        if pos > 0 and (c[j] > hi[j] or (not short_ok and S[j])): return 2, None
        if pos < 0 and c[j] < lo[j]: return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 8. Parabolic SAR stop entries
def run_pst(name, df, mm, tag, rows=None, verbose=True, st=0.02, long_ok=True, short_ok=True, **extra):
    """SAR (0,02/0,02/0,2) acima ou na maxima: stop de compra no SAR; abaixo ou na minima: stop de venda; a entrada
    contraria inverte (so comprado: o stop de venda fecha)."""
    o, h, l, c = ohlc(df); ps = psar(h, l, c, st, st, 0.2)[0]
    LE, SE = np.where(ps >= h, ps, NAN), np.where(ps <= l, ps, NAN)
    if short_ok:
        return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok)
    return run_stp(name, df, tag, rows, verbose, extra, LE, NA(c), SE, short_ok=False)


# ------------------------------------------------------------------ 9. Money Flow (Chaikin Oscillator)
def run_cho(name, df, mm, tag, rows=None, verbose=True, p=(3, 10), long_ok=True, short_ok=True, **extra):
    """Soma de (close-open)/(high-low) x volume em 10 e em 3, cada uma na sua EMA; diferenca lenta - rapida positiva
    = comprado, negativa = vendido."""
    o, h, l, c = ohlc(df); v = vol(df)
    with np.errstate(divide='ignore', invalid='ignore'):
        x = np.where((h - l) * v > 0, (c - o) / (h - l) * v, 0.0)
    a, b = max(p), min(p); res = ema(roll(x, a).sum().to_numpy(), a) - ema(roll(x, b).sum().to_numpy(), b)
    q = pd.Series(np.sign(res)).replace(0, np.nan).ffill().fillna(0).to_numpy()
    return run_g(name, df, posflat(df, mm, q, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. SuperTrend (chandelier 7/7)
def run_stc(name, df, mm, tag, rows=None, verbose=True, mult=7.0, long_ok=True, short_ok=True, **extra):
    """Stop chandelier sobre hl2 com 7 x ATR7: virada para cima compra, para baixo vende; inverte."""
    o, h, l, c = ohlc(df); d = chand(h, l, c, mult * T.atr_rma(h, l, c, 7))
    return R(name, df, mm, tag, rows, verbose, extra, (d == 1) & (sh(d) == -1), (d == -1) & (sh(d) == 1),
             long_ok, short_ok)


# ------------------------------------------------------------------ 11. 3 RSI
def run_r3(name, df, mm, tag, rows=None, verbose=True, lv=(30, 70), long_ok=True, short_ok=True, **extra):
    """RSI 7, 14 e 21 cruzando acima de 30 na mesma barra compra; os tres cruzando abaixo de 70 vende; inverte."""
    o, h, l, c = ohlc(df); rs = [wilder_rsi(c, n) for n in (7, 14, 21)]
    L = np.logical_and.reduce([T.xover(r, K(c, lv[0])) for r in rs])
    S = np.logical_and.reduce([T.xunder(r, K(c, lv[1])) for r in rs])
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 12. Signal To Noise
def run_snr(name, df, mm, tag, rows=None, verbose=True, ln=21, long_ok=True, short_ok=True, **extra):
    """StN = -10 log(media de 1/close das barras 1..20); StN acima da sua SMA7 (barra anterior) = comprado, abaixo =
    vendido, igual = zerado."""
    o, h, l, c = ohlc(df); s = -10 * np.log10(roll(sh(1 / c), ln - 1).sum().to_numpy() / ln); m = T.sma(s, 7)
    q = np.where(sh(m) > sh(s), -1, np.where(sh(m) < sh(s), 1, 0))
    return run_g(name, df, posflat(df, mm, q, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. EMA + RSI Sniper (long-only)
def run_ers(name, df, mm, tag, rows=None, verbose=True, tp=0.096, sl=0.051, long_ok=True, short_ok=False, **extra):
    """So long: maxima cruzando acima da EMA50 com close acima da EMA70 compra; maxima cruzando abaixo fecha; alvo de
    9,6% e stop de 5,1% (do close do sinal)."""
    o, h, l, c = ohlc(df); e = ema(c, 50)
    res = gsim(df, mm, T.xunder(e, h) & (c > ema(c, 70)), Z(c), T.xover(e, h), SLL=c * (1 - sl), TPL=c * (1 + tp),
               rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. MACD 8/16/11 (sinal SMA)
def run_mcd(name, df, mm, tag, rows=None, verbose=True, p=(8, 16, 11), long_ok=True, short_ok=True, **extra):
    """MACD 8/16 acima do sinal SMA11 = comprado, abaixo = vendido."""
    o, h, l, c = ohlc(df); m = ema(c, p[0]) - ema(c, p[1]); q = np.sign(m - T.sma(m, p[2]))
    return run_g(name, df, posflat(df, mm, q, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Hull MA Crossover
def run_hcx(name, df, mm, tag, rows=None, verbose=True, keh=14, long_ok=True, short_ok=True, **extra):
    """Hull de 14 sobre ohlc4[1] (n1) e ohlc4[2] (n2); n1>n2 com longcross1>longcross2 compra, o espelho vende, so
    sem posicao; a condicao contraria fecha."""
    o, h, l, c = ohlc(df); p = (o + h + l + c) / 4; s = int(round(math.sqrt(keh)))
    hull = lambda x: T.wma(2 * T.wma(x, int(round(keh / 2))) - T.wma(x, keh), s)
    n1, n2 = hull(sh(p)), hull(sh(p, 2))
    c1 = (n1 - sh(n1, 3)) + (n1 - sh(n2, 4)) * 100; c2 = (n2 - sh(n2, 3)) + (n2 - sh(n1, 4)) * 100
    L = (n1 > n2) & (c1 > c2); S = (n1 < n2) & (c1 < c2)
    res = gsim(df, mm, L, S, S, L, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Binary Option EMA/Stoch
def run_bes(name, df, mm, tag, rows=None, verbose=True, ln=4, long_ok=True, short_ok=True, **extra):
    """Como escrito (contrario): close abaixo da EMA4 das minimas, abertura abaixo do meio das EMAs, close abaixo da
    EMA21 e Stoch14 K e D<50 compra; o espelho vende; inverte."""
    o, h, l, c = ohlc(df); H, Lo = ema(h, ln), ema(l, ln); m = (H + Lo) / 2; e = ema(c, 21)
    k = stoch(c, h, l, 14); d = T.sma(k, 3)
    L = (c < Lo) & (o < m) & (c < e) & (d < 50) & (k < 50); S = (c > H) & (o > m) & (c > e) & (d > 50) & (k > 50)
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 17. Dual Supertrend with MACD
def run_dst(name, df, mm, tag, rows=None, verbose=True, f=(3.0, 5.0), long_ok=True, short_ok=True, **extra):
    """Supertrend (10, 3) e (20, 5) em alta com histograma do MACD 12/26/9 positivo compra, o espelho vende;
    qualquer um virando fecha."""
    o, h, l, c = ohlc(df); d1 = supertrend(h, l, c, 10, f[0])[1]; d2 = supertrend(h, l, c, 20, f[1])[1]
    m = ema(c, 12) - ema(c, 26); hs = m - ema(m, 9)
    L = (d1 < 0) & (d2 < 0) & (hs > 0); S = (d1 > 0) & (d2 > 0) & (hs < 0)
    res = gsim(df, mm, L, S, (d1 > 0) | (d2 > 0) | (hs < 0), (d1 < 0) | (d2 < 0) | (hs > 0), rev=True,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. VWAP X EMA
def run_vxe(name, df, mm, tag, rows=None, verbose=True, ef=50, long_ok=True, short_ok=True, **extra):
    """Close acima da VWAP diaria, da EMA50 e da EMA200 compra; abaixo da VWAP e da EMA50 vende; inverte."""
    o, h, l, c = ohlc(df); vw = vwap_d(df); e = ema(c, ef)
    return R(name, df, mm, tag, rows, verbose, extra, (c > vw) & (c > e) & (c > ema(c, 200)), (c < vw) & (c < e),
             long_ok, short_ok)


# ------------------------------------------------------------------ 19. Stochastic Z-Score (TradeDots)
def run_szs(name, df, mm, tag, rows=None, verbose=True, thr=2.8, long_ok=True, short_ok=True, **extra):
    """Media de z-score (80) e Stoch(14, 7) reescalado para -4..4 acima de 2,8 vende, abaixo de -2,8 compra, com
    espera de 5 barras; z>0 fecha o long, z<0 fecha o short."""
    o, h, l, c = ohlc(df); st = T.sma(stoch(c, h, l, 14), 7) / 100 * 8 - 4
    z = (c - T.sma(c, 80)) / roll(c, 80).std(ddof=0).to_numpy(); v = (z + st) / 2
    n = len(c); L = np.zeros(n, bool); S = L.copy(); bc = sc = 5
    for i in range(n):
        if v[i] > thr:
            if sc >= 5: S[i] = True; sc = 0; bc = 5
            else: sc += 1
        if z[i] > 0: pass
        elif v[i] < -thr:
            if bc >= 5: L[i] = True; sc = 5; bc = 0
            else: bc += 1
    res = gsim(df, mm, L, S & ~L, z > 0, z < 0, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Ichimoku + EMA filter
def run_ich(name, df, mm, tag, rows=None, verbose=True, ef=True, long_ok=True, short_ok=False, **extra):
    """Linhas lead 1 (tenkan 9 + kijun 26) e lead 2 (52) sem deslocamento: lead1>lead2, close acima da lead1, candle
    de alta e EMA24>EMA90 compra, so sem posicao; espelho vende; close abaixo da lead1 com candle de baixa fecha o
    long, acima da lead2 com candle de alta fecha o short."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2; a = (dc(9) + dc(26)) / 2; b = dc(52)
    up, dn = (ema(c, 24) > ema(c, 90), ema(c, 24) < ema(c, 90)) if ef else (Z(c) | True, Z(c) | True)
    L = (a > b) & (c > a) & (c > o) & up; S = (a < b) & (c < a) & (c < o) & dn
    res = gsim(df, mm, L, S, (c < a) & (c < o), (c > b) & (c > o), rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


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

        pr = lambda v: '/'.join(f'{x:g}' for x in v)
        g4('pac', run_pac, "1. PSAR + ADX + CMF + RSI (long-only)", 'rl', (50, 14), 'cl', (20, 40),
           lambda a, b: f'rsi{a}/cmf{b}', 'rsi50/cmf20')
        g4('haw', run_haw, "2. Abdoli's Heikin Ashi Smoothed (long-only)", 'ln', (65, 30), 'k', (3, 2),
           lambda a, b: f'ema{a}/{b}velas', 'ema65/3velas')
        g2('bct', run_bct, "3. Bar Counter Trend Reversal", 'mult', (2, 1), lambda v: f'kc{v}', 'kc2 ambos')
        g4('vat', run_vat, "4. VWMA with ATR stops (long-only)", 'am', (3.5, 2.5), 'vl', (33, 20),
           lambda a, b: f'{a:g}atr/{b}', '3.5atr/33')
        g4('s200', run_s200, "5. SMA 200 bands (long-only)", 'up', (1.04, 1.02), 'dn', (0.97, 0.99),
           lambda a, b: f'{a:g}/{b:g}', '1.04/0.97')
        g4('vct', run_vct, "6. TASC 2024.08 VCTS (long-only)", 'thr', (30, 20), 'lv', (25, 50),
           lambda a, b: f'adx{a}/vp{b}', 'adx30/vp25')
        g2('tbn', run_tbn, "7. Trend Bounce", 'nn', (7, 14), lambda v: f'c{v}', 'c7 ambos')
        g2('pst', run_pst, "8. Parabolic SAR stop entries", 'st', (0.02, 0.01), lambda v: f'af{v:g}', 'af0.02 ambos')
        g2('cho', run_cho, "9. Money Flow (Chaikin Oscillator)", 'p', ((3, 10), (5, 20)), pr, '3/10 ambos')
        g2('stc', run_stc, "10. SuperTrend chandelier 7/7", 'mult', (7.0, 3.0), lambda v: f'm{v:g}', 'm7 ambos')
        g2('r3', run_r3, "11. 3 RSI", 'lv', ((30, 70), (40, 60)), pr, '30/70 ambos')
        g2('snr', run_snr, "12. Signal To Noise", 'ln', (21, 42), lambda v: f'l{v}', 'l21 ambos')
        g4('ers', run_ers, "13. EMA + RSI Sniper (long-only)", 'tp', (0.096, 0.05), 'sl', (0.051, 0.03),
           lambda a, b: f'tp{a * 100:g}/sl{b * 100:g}', 'tp9.6/sl5.1')
        g2('mcd', run_mcd, "14. MACD 8/16/11 (sinal SMA)", 'p', ((8, 16, 11), (12, 26, 9)), pr, '8/16/11 ambos')
        g2('hcx', run_hcx, "15. Hull MA Crossover", 'keh', (14, 28), lambda v: f'h{v}', 'h14 ambos')
        g2('bes', run_bes, "16. Binary Option EMA/Stoch", 'ln', (4, 8), lambda v: f'e{v}', 'e4 ambos')
        g2('dst', run_dst, "17. Dual Supertrend with MACD", 'f', ((3.0, 5.0), (2.0, 4.0)), pr, '3/5 ambos')
        g2('vxe', run_vxe, "18. VWAP X EMA", 'ef', (50, 20), lambda v: f'ema{v}', 'ema50 ambos')
        g2('szs', run_szs, "19. Stochastic Z-Score (TradeDots)", 'thr', (2.8, 2.0), lambda v: f'z{v:g}', 'z2.8 ambos')
        g2('ich', run_ich, "20. Ichimoku + EMA filter", 'ef', (True, False), lambda v: 'ema' if v else 'sem ema',
           'ema long', dict(short_ok=False))

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote33')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
