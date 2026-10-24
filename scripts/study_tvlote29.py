"""Lote 29 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 26 a 28
(ver docs/LOTE29_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote29.py xau us100 wti btc eth
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
from study_tvlote21 import linreg
from study_tvlote22 import run_stp, macd
from study_tvlote25 import posflat, wilder_rsi, hh, ll, ffill, Z, NAN, roll
from study_tvlote26 import flat_pos
from study_tvlote27 import rev_or_long


def G(df, mm, L, S, long_ok, short_ok, **kw):
    return gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok, **kw)


# ------------------------------------------------------------------ 1. ATR Trailing Stoploss
def run_atsl(name, df, mm, tag, rows=None, verbose=True, mult=2.5, long_ok=True, short_ok=True, **extra):
    """Linha = maior (maxima - 2,5 x ATR5) de 10 barras, so atualizada quando o close passa dela subindo; close cruza
    a linha para cima compra, para baixo vende; inverte."""
    o, h, l, c = ohlc(df); hv = hh(h - mult * T.atr_rma(h, l, c, 5), 10)
    ts = ffill(np.where((c > hv) & (c > sh(c)), hv, NAN))
    return run_g(name, df, G(df, mm, T.xover(c, ts), T.xunder(c, ts), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. High/Low channel swing
def alma(x, n, off=0.85, sig=6.0):
    m = off * (n - 1); s = n / sig; w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s)); w /= w.sum()
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), n)
    out = np.full(len(x), NAN); out[n - 1:] = W @ w
    return out


def ma7(x, v, n):
    vw = roll(x * v, n).sum().to_numpy() / roll(v, n).sum().to_numpy()
    return (T.sma(x, n) + ema(x, n) + T.wma(x, n) + alma(x, n) + pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
            + linreg(x, n) + vw) / 7


def run_hlc(name, df, mm, tag, rows=None, verbose=True, ln=12, long_ok=True, short_ok=True, **extra):
    """Media de 7 medias (SMA, EMA, WMA, ALMA, SMMA, LSMA, VWMA) de 12 das maximas e das minimas: close acima da
    media das maximas compra, abaixo da das minimas vende; minima cruzando abaixo da media das minimas fecha o long
    (espelho)."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float) + 1e-12; ah, al = ma7(h, v, ln), ma7(l, v, ln)
    r = gsim(df, mm, c > ah, c < al, T.xunder(l, al), T.xover(h, ah), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Donchian Breakout (long-only)
def run_dbo(name, df, mm, tag, rows=None, verbose=True, ln=20, ext='lower', **extra):
    """So long: close cruza acima da maxima de 20 anterior compra; cruza abaixo da minima de 20 anterior fecha
    (ext=basis: do meio do canal)."""
    o, h, l, c = ohlc(df); up, lo = sh(hh(h, ln)), sh(ll(l, ln))
    X = T.xunder(c, lo) if ext == 'lower' else T.xunder(c, (up + lo) / 2)
    return run_g(name, df, gsim(df, mm, T.xover(c, up), Z(c), X, rev=False, short_ok=False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Chandelier Exit + ZLSMA
def run_cez(name, df, mm, tag, rows=None, verbose=True, mult=2.0, long_ok=True, short_ok=True, **extra):
    """Sobre o close Heikin Ashi: Chandelier Exit (ATR1 x 2) vira para cima com o close HA cruzando acima da ZLSMA50
    compra; cruzar abaixo da ZLSMA fecha; espelho no short."""
    o, h, l, c = ohlc(df); hc = (o + h + l + c) / 4; a = mult * np.nan_to_num(T.atr_rma(h, l, c, 1)); n = len(c)
    ls = hc - a; ss = hc + a; d = np.ones(n)
    for i in range(1, n):
        lp, sp = ls[i - 1], ss[i - 1]
        if hc[i] > lp: ls[i] = max(ls[i], lp)
        if hc[i] < sp: ss[i] = min(ss[i], sp)
        d[i] = 1 if hc[i] > sp else (-1 if hc[i] < lp else d[i - 1])
    l1 = linreg(hc, 50); zl = 2 * l1 - linreg(np.nan_to_num(l1), 50)
    L = (d == 1) & (sh(d) == -1) & T.xover(hc, zl); S = (d == -1) & (sh(d) == 1) & T.xunder(hc, zl)
    r = gsim(df, mm, L, S, T.xunder(hc, zl), T.xover(hc, zl), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Breakout Scalper
def run_bsc(name, df, mm, tag, rows=None, verbose=True, fw=13, sw=52, long_ok=True, short_ok=True, **extra):
    """Nuvem = meio do canal de 13 menos meio do de 52, em ATR52: EMA3 acima do meio rapido com nuvem > 1 ATR arma stop
    de compra na maxima de 52; stop de saida no maior entre as minimas de 52 e 13; nuvem negativa fecha. Espelho."""
    o, h, l, c = ohlc(df); fl, fh, sl_, sh_ = ll(l, fw), hh(h, fw), ll(l, sw), hh(h, sw)
    fm, sm = (fl + fh) / 2, (sl_ + sh_) / 2; ip = ema(c, 3); cp = (fm - sm) / T.atr_rma(h, l, c, sw)
    LE = np.where((ip > fm) & (cp > 1), sh_, NAN); SE = np.where((ip < fm) & (cp < -1), sl_, NAN)
    LX = np.where(cp < 0, 1e18, np.fmax(sl_, fl)); SX = np.where(cp > 0, -1e18, np.fmin(sh_, fh))
    return run_stp(name, df, tag, rows, verbose, extra, LE, SE, LX, SX, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 6. Bollinger Bands + EMA 9
def run_bbe9(name, df, mm, tag, rows=None, verbose=True, ln=20, long_ok=True, short_ok=True, **extra):
    """Fora de posicao: close anterior abaixo da BB(20, 2) e vela de alta compra; alvo na EMA9 e stop na minima anterior
    (espelho no short)."""
    o, h, l, c = ohlc(df); m = T.sma(c, ln); d = 2 * roll(c, ln).std(ddof=1).to_numpy(); e = ema(c, 9)
    L = (sh(c) < sh(m - d)) & (c > o); S = (sh(c) > sh(m + d)) & (c < o)
    r = gsim(df, mm, L, S & ~L, SLL=sh(l), TPL=e, SLS=sh(h), TPS=e, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. PTS Golden Edge
def run_ged(name, df, mm, tag, rows=None, verbose=True, f=3, s=33, long_ok=True, short_ok=True, **extra):
    """EMA3 cruza a EMA33 para cima com RSI12 > 56, HMA66 subindo e faixa de 14 barras > 0,5 ATR14 compra; espelho
    com RSI < 45 vende; inverte."""
    o, h, l, c = ohlc(df); a, b = ema(c, f), ema(c, s); r_ = wilder_rsi(c, 12); hm = T.hma(c, 66)
    rf = hh(h, 14) - ll(l, 14) > 0.5 * T.atr_rma(h, l, c, 14)
    L = T.xover(a, b) & (r_ > 56) & (hm > sh(hm)) & rf; S = T.xunder(a, b) & (r_ < 45) & (hm < sh(hm)) & rf
    return run_g(name, df, G(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. KAMA TradeDots
def kama_td(c, n=10, f=5, s=50):
    ch = np.abs(c - sh(c, n)); vol = roll(np.abs(np.diff(c, prepend=NAN)), n).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        er = ch / vol
    sc = (er * (2 / (f + 1) - 2 / (s + 1)) + 2 / (s + 1)) ** 2; out = np.zeros(len(c)); k = c[0]
    for i in range(len(c)):
        if sc[i] == sc[i]: k = k + sc[i] * (c[i] - k)
        out[i] = k
    return out


def run_kamatd(name, df, mm, tag, rows=None, verbose=True, rp=10, long_ok=True, short_ok=False, **extra):
    """KAMA(10, 5, 50) subindo por 10 barras seguidas compra (o padrao e so comprado); caindo por 10 fecha (ambos:
    vende)."""
    o, h, l, c = ohlc(df); k = kama_td(c); up = (np.diff(k, prepend=NAN) > 0).astype(float); dn = (np.diff(k, prepend=NAN) < 0).astype(float)
    ri = roll(up, rp).min().to_numpy() == 1; fa = roll(dn, rp).min().to_numpy() == 1
    t = pd.Series(np.where(ri, 1.0, np.where(fa, -1.0, np.nan))).ffill().fillna(0).to_numpy()
    return run_g(name, df, posflat(df, mm, flat_pos(t, long_ok, short_ok), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. RSI2 + medias (pullback)
def run_r2m(name, df, mm, tag, rows=None, verbose=True, lv=5, long_ok=True, short_ok=True, **extra):
    """Close acima da SMA200, close abaixo da SMA10 e RSI2 saindo de abaixo de 5 compra; close acima da SMA10 fecha.
    Espelho no short (RSI2 saindo de acima de 95)."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 2); m10, m200 = T.sma(c, 10), T.sma(c, 200)
    L = (c > m200) & (c < m10) & (sh(r_) < lv) & (r_ >= lv); S = (c < m200) & (c > m10) & (sh(r_) > 100 - lv) & (r_ <= 100 - lv)
    r = gsim(df, mm, L, S, c > m10, c <= m10, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. RSI and SMA (Coinrule)
def run_rss(name, df, mm, tag, rows=None, verbose=True, f=100, s=150, long_ok=True, short_ok=True, **extra):
    """SMA100 cruza a SMA150 para cima com RSI14 > 50 compra; para baixo com RSI < 50 vende; inverte."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, f), T.sma(c, s); r_ = wilder_rsi(c, 14)
    return run_g(name, df, G(df, mm, T.xover(a, b) & (r_ > 50), T.xover(b, a) & (r_ < 50), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Scalping against trapped countertrend
def run_trap(name, df, mm, tag, rows=None, verbose=True, ck=15, long_ok=True, short_ok=True, **extra):
    """Sobre o hl2: estocastico 60 suavizado (SMA13) > 50, RSI5 > 50 e RSI5 abaixo de 35 em algum momento das ultimas
    15 barras compra (min dos tres > 0); espelho vende; inverte."""
    o, h, l, c = ohlc(df); s = (h + l) / 2; k = T.sma(stoch(s, h, l, 60), 13); r_ = wilder_rsi(s, 5)
    up = np.fmin(np.fmin(k - 50, r_ - 50), 35 - ll(r_, ck)); dn = np.fmax(np.fmax(k - 50, r_ - 50), 65 - hh(r_, ck))
    return run_g(name, df, G(df, mm, up > 0, dn < 0, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Linear Regression Channel Breakout
def run_lrcb(name, df, mm, tag, rows=None, verbose=True, dv=2.3, long_ok=True, short_ok=True, **extra):
    """Canal de regressao linear de 20 com 2,3 desvios: close acima da banda de cima compra, abaixo da de baixo vende;
    inverte; alvo 11%."""
    o, h, l, c = ohlc(df); n = 20; y = linreg(c, n); x = pd.Series(np.arange(len(c), dtype=float))
    cs = pd.Series(c); r = cs.rolling(n).corr(x).to_numpy(); sd = cs.rolling(n).std(ddof=0).to_numpy()
    dev = sd * np.sqrt(np.clip(1 - r * r, 0, None))
    return run_g(name, df, G(df, mm, c > y + dv * dev, c < y - dv * dev, long_ok, short_ok, tpp=0.11), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Crossing MAs + ADX
def run_madx(name, df, mm, tag, rows=None, verbose=True, adx_t=20, long_ok=True, short_ok=True, **extra):
    """SMA20 acima da SMA120 com ADX14 >= 20 compra; abaixo vende; inverte (sem ADX forte fica como esta)."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, 20), T.sma(c, 120); ad = dmi(h, l, c, 14)[2]; ok = ad >= adx_t
    return run_g(name, df, G(df, mm, (a > b) & ok, (a < b) & ok, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. BotBot
def run_bot(name, df, mm, tag, rows=None, verbose=True, k=0.04, long_ok=True, short_ok=True, **extra):
    """Close 0,1% acima da SMA19, maxima 4% acima de (minima anterior + ATR19) e vela de alta compra; espelho vende;
    inverte."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 19); m = T.sma(c, 19)
    L = (c / m > 1.001) & (h / (sh(l) + a) > 1 + k) & (c / o > 1.001)
    S = (c / m < 0.999) & (l / (sh(h) - a) < 1 - k) & (c / o < 0.999)
    return run_g(name, df, G(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Rob Booker ADX Breakout
def run_adxb(name, df, mm, tag, rows=None, verbose=True, adx_l=18, long_ok=True, short_ok=True, **extra):
    """Fora de posicao, ADX14 < 18 e close cruzando a maxima de 20 anterior compra (cruzando a minima vende); alvo de 1
    largura da caixa e stop de meia largura."""
    o, h, l, c = ohlc(df); up, lo = sh(hh(h, 20)), sh(ll(l, 20)); w = up - lo; ad = dmi(h, l, c, 14)[2] < adx_l
    cr = lambda a, b: T.xover(a, b) | T.xunder(a, b)
    L = cr(c, up) & ad; S = cr(c, lo) & ad & ~L
    r = gsim(df, mm, L, S, SLL=c - 0.5 * w, TPL=c + w, SLS=c + 0.5 * w, TPS=c - w, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Bull and Bear Fear
def run_bbf(name, df, mm, tag, rows=None, verbose=True, n=12, long_ok=True, short_ok=True, **extra):
    """BullFear = meio da faixa das maximas de 12, BearFear = meio da faixa das minimas: close cruza acima de BullFear
    compra, abaixo de BearFear vende; inverte."""
    o, h, l, c = ohlc(df); bu = (hh(h, n) + ll(h, n)) / 2; be = (hh(l, n) + ll(l, n)) / 2
    return run_g(name, df, G(df, mm, T.xover(c, bu), T.xunder(c, be), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. MACD_RSI
def run_mrs(name, df, mm, tag, rows=None, verbose=True, el=20, long_ok=True, short_ok=True, **extra):
    """Close > EMA20, MACD(12, 26) acima do sinal EMA20 e RSI14 acima da sua EMA20 compra; tudo ao contrario vende;
    inverte."""
    o, h, l, c = ohlc(df); e = ema(c, el); m = ema(c, 12) - ema(c, 26); s = ema(m, 20); r_ = wilder_rsi(c, 14); rs = ema(np.nan_to_num(r_), 20)
    return run_g(name, df, G(df, mm, (c > e) & (m > s) & (r_ > rs), (c < e) & (m < s) & (r_ < rs), long_ok, short_ok),
                 tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. BTC WaveTrend R:R (long-only)
def run_wtr(name, df, mm, tag, rows=None, verbose=True, rr=1.5, lim=20, **extra):
    """So long: WaveTrend (10, 21) cruza o sinal para cima com WT1 < 20 compra; stop na menor minima das 3 ultimas
    barras e alvo de 1,5R."""
    o, h, l, c = ohlc(df); ap = (h + l + c) / 3; es = ema(ap, 10); d = ema(np.abs(ap - es), 10)
    with np.errstate(divide='ignore', invalid='ignore'):
        ci = np.nan_to_num((ap - es) / (0.015 * d))
    w1 = ema(ci, 21); w2 = T.sma(w1, 4); sl = np.fmin(np.fmin(l, sh(l)), sh(l, 2))
    r = gsim(df, mm, T.xover(w1, w2) & (w1 < lim), Z(c), SLL=sl, TPL=c + rr * (c - sl), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Volume fight
def run_vf(name, df, mm, tag, rows=None, verbose=True, ma=11, long_ok=True, short_ok=True, **extra):
    """Volume comprador vs vendedor (VWMA 11): primeira barra de zona compradora (com folga de 15% contra a zona neutra)
    compra, primeira de zona vendedora vende; inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); rg = np.where(h - l == 0, np.nan, h - l)
    bv = np.where(o < c, v, v * (h - o) / rg); sv = np.where(o > c, v, v * (o - l) / rg)
    vw = lambda x: roll(x * x, ma).sum().to_numpy() / roll(x, ma).sum().to_numpy()
    ab, ase = vw(np.nan_to_num(bv)), vw(np.nan_to_num(sv)); fl = np.abs(ab + ase) / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        bull = (ab > ase) & (fl / ab < 0.85); bear = (ab < ase) & (fl / ase < 0.85)
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); up = dn = 0
    for i in range(n):
        if bull[i]: up += 1; dn = 0
        if bear[i]: dn += 1; up = 0
        L[i] = bull[i] and up == 1; S[i] = bear[i] and dn == 1
    return run_g(name, df, G(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Channel Break (free bot)
def run_chb(name, df, mm, tag, rows=None, verbose=True, mid=True, long_ok=True, short_ok=True, **extra):
    """Stop de compra na maxima de 13 e de venda na minima de 18; saida no meio do canal (ou no outro lado) ou no stop
    de 9%; o alvo de 46% foi ignorado."""
    o, h, l, c = ohlc(df); h13, l13, h18, l18 = hh(h, 13), ll(l, 13), hh(h, 18), ll(l, 18)
    LX = (h13 + l13) / 2 if mid else l13; SX = (h18 + l18) / 2 if mid else h18
    return run_stp(name, df, tag, rows, verbose, extra, h13, l18, LX, SX, 0.09 * c, 0.09 * c, long_ok=long_ok, short_ok=short_ok)


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

        g2('atsl', run_atsl, "1. ATR Trailing Stoploss", 'mult', (2.5, 4.0), lambda v: f'm{v:g}', 'm2.5 ambos')
        g2('hlc', run_hlc, "2. High/Low channel swing", 'ln', (12, 30), lambda v: f'l{v}', 'l12 ambos')
        grid('dbo', run_dbo, "3. Donchian Breakout (long-only)", TFS, 'd20 lower',
             [(f'd{a} {e}', dict(ln=a, ext=e)) for a, e in itertools.product((20, 55), ('lower', 'basis'))])
        g2('cez', run_cez, "4. Chandelier Exit + ZLSMA", 'mult', (2.0, 3.0), lambda v: f'm{v:g}', 'm2 ambos')
        grid('bsc', run_bsc, "5. Breakout Scalper", TFS, '13/52 ambos',
             [(f'{a}/{b} {s}', dict(fw=a, sw=b, **sk(s))) for (a, b), s in itertools.product(((13, 52), (20, 100)), side2)])
        g2('bbe9', run_bbe9, "6. Bollinger Bands + EMA 9", 'ln', (20, 50), lambda v: f'bb{v}', 'bb20 ambos')
        grid('ged', run_ged, "7. PTS Golden Edge", TFS, '3/33 ambos',
             [(f'{a}/{b} {s}', dict(f=a, s=b, **sk(s))) for (a, b), s in itertools.product(((3, 33), (9, 50)), side2)])
        g2('kamatd', run_kamatd, "8. KAMA TradeDots", 'rp', (10, 5), lambda v: f'r{v}', 'r10 long')
        g2('r2m', run_r2m, "9. RSI2 + medias (pullback)", 'lv', (5, 10), lambda v: f'{v}/{100 - v}', '5/95 ambos')
        grid('rss', run_rss, "10. RSI and SMA (Coinrule)", TFS, '100/150 ambos',
             [(f'{a}/{b} {s}', dict(f=a, s=b, **sk(s))) for (a, b), s in itertools.product(((100, 150), (50, 100)), side2)])
        g2('trap', run_trap, "11. Scalping against trapped countertrend", 'ck', (15, 5), lambda v: f'ck{v}', 'ck15 ambos')
        g2('lrcb', run_lrcb, "12. Linear Regression Channel Breakout", 'dv', (2.3, 1.5), lambda v: f'dv{v:g}', 'dv2.3 ambos')
        g2('madx', run_madx, "13. Crossing MAs + ADX", 'adx_t', (20, 0), lambda v: f'adx{v}', 'adx20 ambos')
        g2('bot', run_bot, "14. BotBot", 'k', (0.04, 0.02), lambda v: f'k{v:g}', 'k0.04 ambos')
        g2('adxb', run_adxb, "15. Rob Booker ADX Breakout", 'adx_l', (18, 25), lambda v: f'adx{v}', 'adx18 ambos')
        g2('bbf', run_bbf, "16. Bull and Bear Fear", 'n', (12, 30), lambda v: f'n{v}', 'n12 ambos')
        g2('mrs', run_mrs, "17. MACD_RSI", 'el', (20, 50), lambda v: f'e{v}', 'e20 ambos')
        grid('wtr', run_wtr, "18. BTC WaveTrend R:R (long-only)", TFS, 'rr1.5 lim20',
             [(f'rr{a:g} lim{b}', dict(rr=a, lim=b)) for a, b in itertools.product((1.5, 3.0), (20, -40))])
        g2('vf', run_vf, "19. Volume fight", 'ma', (11, 30), lambda v: f'ma{v}', 'ma11 ambos')
        g2('chb', run_chb, "20. Channel Break (free bot)", 'mid', (True, False), lambda v: 'meio' if v else 'canal', 'meio ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote29')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
