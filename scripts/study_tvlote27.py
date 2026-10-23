"""Lote 27 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 21-24 e 26
(ver docs/LOTE27_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote27.py xau us100 wti btc eth
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
from study_tvlote20 import sh, tr_, _st
from study_tvlote21 import linreg
from study_tvlote22 import run_stp, macd
from study_tvlote25 import run_loop, posflat, wilder_rsi, hh, ll, full, Z, NAN, roll
from study_tvlote26 import flat_pos


def rev_or_long(df, mm, L, S, long_ok, short_ok, **kw):
    """Inverte com os dois lados; so comprado: o sinal de venda fecha o long."""
    if short_ok:
        return gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, **kw)
    return gsim(df, mm, L, Z(L), S, rev=False, short_ok=False, **kw)


def trail_most(src, pct):
    """Linha de trailing do tipo MOST/ATR-trailing: sobe com src - d, desce com src + d."""
    n = len(src); t = np.zeros(n); d = np.asarray(pct, float) * np.ones(n)
    for i in range(1, n):
        p = t[i - 1]; s, s1 = src[i], src[i - 1]
        if s != s or d[i] != d[i]: t[i] = p; continue
        if s > p and s1 > p: t[i] = max(p, s - d[i])
        elif s < p and s1 < p: t[i] = min(p, s + d[i])
        else: t[i] = s - d[i] if s > p else s + d[i]
    return t


# ------------------------------------------------------------------ 1. Doji strategy
def run_doji(name, df, mm, tag, rows=None, verbose=True, sl=0.01, long_ok=True, short_ok=True, **extra):
    """Doji (corpo <= 5% da faixa): stop de compra na maxima (ou na maior das 2 ultimas se a vela anterior era longa
    e maior) e stop de venda na minima, so na barra seguinte; stop de perda fixo (200 ticks -> 1%). O alvo de 200
    ticks foi ignorado."""
    o, h, l, c = ohlc(df); rg = h - l
    with np.errstate(divide='ignore', invalid='ignore'):
        lc = np.abs(c - o) / rg > 0.7
    dj = np.abs(o - c) <= rg * 0.05; prev = sh(lc.astype(float)) == 1
    ld = np.where(prev & (sh(rg) > rg), h, np.fmax(h, sh(h))); sd = np.where(prev & (sh(rg) > rg), l, np.fmin(l, sh(l)))
    LE, SE = np.where(dj, ld, NAN), np.where(dj, sd, NAN)
    return run_stp(name, df, tag, rows, verbose, extra, LE, SE, KL=sl * c, KS=sl * c, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 2. Adaptive Trend Flow
def run_atf(name, df, mm, tag, rows=None, verbose=True, filt=True, long_ok=True, short_ok=False, **extra):
    """Base = media de EMA2 e EMA4 do hlc3, faixa +- 2 x EMA2(desvio2); tendencia vira com o close fora da faixa.
    Virada para cima com close > SMA4 e MACD(2, 7, 2) acima do sinal compra; virada para baixo fecha (ambos: vende)."""
    o, h, l, c = ohlc(df); tp = (h + l + c) / 3
    b = (ema(tp, 2) + ema(tp, 4)) / 2; sv = ema(np.nan_to_num(roll(tp, 2).std(ddof=0).to_numpy()), 2)
    up, lo = b + 2 * sv, b - 2 * sv; n = len(c); t = np.zeros(n); t[0] = 1 if c[0] > b[0] else -1
    for i in range(1, n):
        t[i] = -1 if (t[i - 1] == 1 and c[i] < lo[i]) else (1 if (t[i - 1] == -1 and c[i] > up[i]) else t[i - 1])
    L = (t == 1) & (sh(t) == -1); S = (t == -1) & (sh(t) == 1)
    if filt:
        m, sg = macd(c, 2, 7, 2); L = L & (c > T.sma(c, 4)) & (m > sg)
    return run_g(name, df, rev_or_long(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Optimized RSI Buy The Dips (long-only)
def run_rdip(name, df, mm, tag, rows=None, verbose=True, lo=35, ma=100, **extra):
    """So long: RSI14 < 35 com close abaixo da SMA100 compra; RSI > 65 fecha."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 14)
    r = gsim(df, mm, (r_ < lo) & (c < T.sma(c, ma)), Z(c), r_ > 100 - lo, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Stochastic Trend (long-only)
def run_stt(name, df, mm, tag, rows=None, verbose=True, k=200, sm=100, xt=60, **extra):
    """So long: %K(200) suavizado por SMA100 cruza acima de 50 compra; cruza abaixo de 60 fecha."""
    o, h, l, c = ohlc(df); kk = T.sma(stoch(c, h, l, k), sm)
    r = gsim(df, mm, T.xover(kk, 0 * c + 50), Z(c), T.xunder(kk, 0 * c + xt), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. TSI CCI Hull
def run_tch(name, df, mm, tag, rows=None, verbose=True, per=25, long_ok=True, short_ok=True, **extra):
    """Sobre a abertura: TSI(50, 50) x 5 suavizado (EMA125) subindo, Hull25 suavizado abaixo do preco, CCI do Hull > 0
    e subindo e Hull subindo compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); p = o; pc = np.diff(p, prepend=NAN)
    ds = lambda x: ema(ema(np.nan_to_num(x), 50), 50)
    with np.errstate(divide='ignore', invalid='ignore'):
        tsi = 100 * ds(pc) / ds(np.abs(pc))
    t1 = ema(np.nan_to_num(tsi) * 5, 125); t2 = sh(t1, 2)
    hull = lambda x, n: T.wma(2 * T.wma(x, round(n / 2)) - T.wma(x, n), round(math.sqrt(n)))
    n1 = hull(p, per); dv = roll(p, per).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True).to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        cc = (p - n1) / (0.015 * dv)
    hs = T.wma(2 * T.wma(n1, per // 2) - T.wma(n1, per), round(math.sqrt(per)))
    L = (t1 > t2) & (hs < p) & (cc > 0) & (cc > sh(cc)) & (n1 > sh(n1))
    S = (t1 < t2) & (hs > p) & (cc < 0) & (cc < sh(cc)) & (n1 < sh(n1))
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Gold Scalping
def run_gsc(name, df, mm, tag, rows=None, verbose=True, tpk='pct', long_ok=True, short_ok=True, **extra):
    """EMA50 > EMA200, RSI14 entre 45 e 55, engolfo de alta e close > EMA50 compra (espelho vende); stop de 1 ATR14
    e alvo de 20 pips do ouro (US$ 2, aqui 0,1% do preco; tpk=atr2: 2 ATR)."""
    o, h, l, c = ohlc(df); e50, e200 = ema(c, 50), ema(c, 200); r_ = wilder_rsi(c, 14); a = T.atr_rma(h, l, c, 14)
    bu = (c > o) & (sh(c) < sh(o)) & (c > sh(c)) & (o < sh(c)); be = (c < o) & (sh(c) > sh(o)) & (c < sh(c)) & (o > sh(c))
    mid = (r_ >= 45) & (r_ <= 55)
    L = (e50 > e200) & mid & bu & (c > e50); S = (e50 < e200) & mid & be & (c < e50)
    tp = 0.001 * c if tpk == 'pct' else 2 * a
    r = gsim(df, mm, L, S, SLL=c - a, TPL=c + tp, SLS=c + a, TPS=c - tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. The Flash
def run_flash(name, df, mm, tag, rows=None, verbose=True, mr=60, long_ok=True, short_ok=True, **extra):
    """EMA12 acima do seu trailing de 1% (MOST), SuperTrend(10, 3) de alta e RSI10 do momento 10 > 60 compra se
    estiver fora (espelho vende); sai quando o close cruza a linha do SuperTrend."""
    o, h, l, c = ohlc(df); e = ema(c, 12); tr2 = trail_most(e, 0.01 * e)
    rm = wilder_rsi(c - sh(c, 10), 10); t = _st((h + l) / 2, c, np.nan_to_num(T.atr_rma(h, l, c, 10)), 3.0)[0]
    L = (e > tr2) & (t == 1) & (rm > mr); S = (e < tr2) & (t == -1) & (rm > mr)
    r = gsim(df, mm, L, S & ~L, t == -1, t == 1, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. Volatility System (Wilder)
def run_wvs(name, df, mm, tag, rows=None, verbose=True, arc=1.8, long_ok=True, short_ok=True, **extra):
    """ARC = ATR9 x 1,8; close cruza acima de (menor close de 9 + ARC) da barra anterior compra, abaixo de (maior
    close de 9 - ARC) vende; inverte (stop and reverse)."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 9) * arc
    L = T.xover(c, sh(ll(c, 9) + a)); S = T.xunder(c, sh(hh(c, 9) - a))
    r = gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Bollinger Band Breakout (long-only)
def run_bbbo(name, df, mm, tag, rows=None, verbose=True, mult=1.5, ext='lower', **extra):
    """So long: close cruza acima da banda superior (BB20, 1,5) compra; cruza abaixo da inferior fecha (ext=basis:
    da media)."""
    o, h, l, c = ohlc(df); b = T.sma(c, 20); d = mult * roll(c, 20).std(ddof=0).to_numpy()
    X = T.xunder(c, b - d) if ext == 'lower' else T.xunder(c, b)
    r = gsim(df, mm, T.xover(c, b + d), Z(c), X, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Simple strat (MACD + Stoch + RSI)
def run_simp(name, df, mm, tag, rows=None, verbose=True, tpm=6, slm=2, long_ok=True, short_ok=True, **extra):
    """MACD acima do sinal, %K(14, 3) > 50 e RSI14 > 50 compra (a ordem stop na maxima virou mercado); sai com MACD
    abaixo do sinal ou close alem de entrada - 2 ATR10 / + 6 ATR10. Espelho no short."""
    o, h, l, c = ohlc(df); m, sg = macd(c); k = T.sma(stoch(c, h, l, 14), 3); r_ = wilder_rsi(c, 14)
    a = T.atr_rma(h, l, c, 10)
    L = (m > sg) & (k > 50) & (r_ > 50); S = (m < sg) & (k < 50) & (r_ < 50)
    def ex(j, s, e, st):
        if s == 1 and (m[j] < sg[j] or c[j] < e - a[j] * slm or c[j] > e + a[j] * tpm): return 2, None
        if s == -1 and (m[j] > sg[j] or c[j] > e + a[j] * slm or c[j] < e - a[j] * tpm): return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, False, long_ok, short_ok)


# ------------------------------------------------------------------ 11. Squeeze Momentum on Reversal
def run_sqr(name, df, mm, tag, rows=None, verbose=True, st=0.0018, long_ok=True, short_ok=True, **extra):
    """Momento do squeeze (linreg 20) abaixo de -forca e subindo compra, acima de +forca e caindo vende; inverte. A
    forca 0,0018 era em preco de forex; aqui e relativa ao close."""
    o, h, l, c = ohlc(df); v = linreg(c - ((hh(h, 20) + ll(l, 20)) / 2 + T.sma(c, 20)) / 2, 20) / c
    L = (v < -st) & (v > sh(v)); S = (v > st) & (v < sh(v))
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Trend Following Breakout
def run_tfb(name, df, mm, tag, rows=None, verbose=True, en=100, xt=50, long_ok=True, short_ok=True, **extra):
    """Close cruza acima da maxima de 100 (barra anterior) compra; fecha quando o close cruza acima da menor maxima
    de 50 ou na venda; short: close abaixo da minima de 100, fecha com close acima da maior minima de 50."""
    o, h, l, c = ohlc(df)
    L = T.xover(c, sh(hh(h, en))); S = T.xunder(c, sh(ll(l, en)))
    XL = T.xover(c, sh(ll(h, xt))); XS = T.xover(c, sh(hh(l, xt)))
    r = gsim(df, mm, L, S & ~L, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Wyckoff Range
def run_wyk(name, df, mm, tag, rows=None, verbose=True, sl=0.10, long_ok=True, short_ok=True, **extra):
    """Close cruza acima da SMA32 junto com a minima cruzando acima da SMA10 das minimas compra; close abaixo da
    SMA35 com maxima abaixo da SMA20 das maximas vende; inverte; stop 10%."""
    o, h, l, c = ohlc(df)
    L = T.xover(c, T.sma(c, 32)) & T.xover(l, T.sma(l, 10)); S = T.xunder(c, T.sma(c, 35)) & T.xunder(h, T.sma(h, 20))
    r = gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok, slp=sl)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Martin Pring's Special K
def run_spk(name, df, mm, tag, rows=None, verbose=True, sm=10, long_ok=True, short_ok=True, **extra):
    """Special K (soma ponderada de 12 ROCs suavizados, de 10 a 530 barras) acima da sua SMA10 compra, abaixo vende;
    sempre posicionado."""
    o, h, l, c = ohlc(df); roc = lambda n: (c / sh(c, n) - 1) * 100
    spec = [(10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4), (40, 50, 1), (65, 65, 2), (75, 75, 3), (100, 100, 4),
            (195, 130, 1), (265, 130, 2), (390, 130, 3), (530, 195, 4)]
    osc = sum(T.sma(roc(a), b) * w for a, b, w in spec); s = T.sma(osc, sm)
    t = np.where(osc > s, 1, np.where(osc < s, -1, 0)); t = pd.Series(np.where(t == 0, np.nan, t)).ffill().fillna(0).to_numpy()
    return run_g(name, df, posflat(df, mm, flat_pos(t, long_ok, short_ok), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. ATR Trailing Stops
def run_atrts(name, df, mm, tag, rows=None, verbose=True, n=5, mult=3.5, long_ok=True, short_ok=False, **extra):
    """Trailing de 3,5 x ATR5 sobre o close: cruzar acima compra, abaixo fecha (com shorts: inverte)."""
    o, h, l, c = ohlc(df); ts = trail_most(c, mult * T.atr_rma(h, l, c, n))
    return run_g(name, df, rev_or_long(df, mm, T.xover(c, ts), T.xunder(c, ts), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. 3 EMA + Stoch RSI + ATR
def run_e3(name, df, mm, tag, rows=None, verbose=True, tpm=4.0, long_ok=True, short_ok=True, **extra):
    """EMA8 > EMA14 > EMA50 e close > EMA8 compra (espelho vende), inverte; alvo 4 ATR14 e stop 1 ATR fixados na
    entrada (o filtro de Stoch RSI vem desligado)."""
    o, h, l, c = ohlc(df); a, b, d = ema(c, 8), ema(c, 14), ema(c, 50); at = T.atr_rma(h, l, c, 14)
    L = (a > b) & (b > d) & (c > a); S = (a < b) & (b < d) & (c < a)
    r = gsim(df, mm, L, S, SLL=c - at, TPL=c + tpm * at, SLS=c + at, TPS=c - tpm * at, rev=True,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. Ichimoku Backtester
def run_ichb(name, df, mm, tag, rows=None, verbose=True, p=(9, 26, 52), long_ok=True, short_ok=True, **extra):
    """Tenkan cruza a Kijun para cima, close acima de 26 barras atras, close acima da nuvem (deslocada 26) e nuvem
    verde compra; espelho vende; a entrada contraria fecha e inverte (RSI, TP e SL vem desligados)."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2
    tk, kj, sb = dc(p[0]), dc(p[1]), dc(p[2]); sa = (tk + kj) / 2; off = p[1]
    sH, sL = np.fmax(sh(sa, off), sh(sb, off)), np.fmin(sh(sa, off), sh(sb, off)); mo = c - sh(c, off)
    L = T.xover(tk, kj) & (mo > 0) & (c > sH) & (sa > sb); S = T.xunder(tk, kj) & (mo < 0) & (c < sL) & (sa < sb)
    return run_g(name, df, rev_or_long(df, mm, L, S, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. SSL Channel Cross
def run_ssl(name, df, mm, tag, rows=None, verbose=True, ln=10, long_ok=True, short_ok=True, **extra):
    """Canal SSL (SMA10 das maximas e das minimas, lado pelo close fora do canal): linha de alta cruza a de baixa
    compra, o contrario vende; inverte."""
    o, h, l, c = ohlc(df); a, b = T.sma(h, ln), T.sma(l, ln)
    hv = pd.Series(np.where(c > a, 1.0, np.where(c < b, -1.0, np.nan))).ffill().fillna(0).to_numpy()
    dn = np.where(hv < 0, a, b); up = np.where(hv < 0, b, a)
    r = gsim(df, mm, T.xover(up, dn), T.xunder(up, dn), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Combo 2/20 EMA + Accelerator Oscillator
def run_c2ac(name, df, mm, tag, rows=None, verbose=True, ln=14, long_ok=True, short_ok=True, **extra):
    """2/20 EMA (EMA14; minima/maxima de 2 barras contra a media e o close anterior) e AC (SMA6 - SMA33 do hl2 menos
    a SMA6 disso) concordando compra ou vende; discordando, zera."""
    o, h, l, c = ohlc(df); x = ema(c, ln); hh2, ll2 = np.fmax(h, sh(h)), np.fmin(l, sh(l))
    xs = np.where((ll2 > x) | (hh2 < x), ll2, hh2); c1 = sh(c)
    p1 = np.where(xs > c1, -1.0, np.where(xs < c1, 1.0, np.nan))
    hl2 = (h + l) / 2; d = T.sma(hl2, 6) - T.sma(hl2, 33); res = d - T.sma(d, 6)
    p2 = np.where(res < 0, -1.0, np.where(res > 0, 1.0, np.nan))
    f = lambda z: pd.Series(z).ffill().fillna(0).to_numpy()
    p1, p2 = f(p1), f(p2); t = np.where((p1 == 1) & (p2 == 1), 1, np.where((p1 == -1) & (p2 == -1), -1, 0))
    if not short_ok: t = np.where(t == 1, 1, 0)
    return run_g(name, df, posflat(df, mm, t, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. OBV Oscillator
def run_obv(name, df, mm, tag, rows=None, verbose=True, ln=20, long_ok=True, short_ok=True, **extra):
    """OBV de 20 barras dividido pelo volume de 20: EMA12 cruza a EMA26 para cima compra, para baixo vende; inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    ob = roll(v * np.sign(np.diff(c, prepend=NAN)), ln).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        osc = np.nan_to_num(ob / roll(v, ln).sum().to_numpy())
    a, b = ema(osc, 12), ema(osc, 26)
    r = gsim(df, mm, T.xover(a, b), T.xunder(a, b), rev=True, long_ok=long_ok, short_ok=short_ok)
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

        grid('doji', run_doji, "1. Doji strategy", TFS, 'sl1% ambos',
             [(f'sl{a:.0%} {s}', dict(sl=a, **sk(s))) for a, s in itertools.product((0.01, 0.03), side2)])
        grid('atf', run_atf, "2. Adaptive Trend Flow", TFS, 'filtros long',
             [(('filtros ' if f else 'semfiltro ') + s, dict(filt=f, **sk(s))) for f, s in itertools.product((True, False), side2)])
        grid('rdip', run_rdip, "3. Optimized RSI Buy The Dips (long-only)", TFS, '35/65 sma100',
             [(f'{a}/{100 - a} sma{m}', dict(lo=a, ma=m)) for a, m in itertools.product((35, 30), (100, 200))])
        grid('stt', run_stt, "4. Stochastic Trend (long-only)", TFS, 'k200/100 x60',
             [(f'k{k}/{s} x{x}', dict(k=k, sm=s, xt=x)) for (k, s), x in itertools.product(((200, 100), (50, 25)), (60, 50))])
        grid('tch', run_tch, "5. TSI CCI Hull", TFS, 'p25 ambos',
             [(f'p{a} {s}', dict(per=a, **sk(s))) for a, s in itertools.product((25, 50), side2)])
        grid('gsc', run_gsc, "6. Gold Scalping", TFS, 'tp0.1% ambos',
             [(('tp0.1% ' if t == 'pct' else 'tp2atr ') + s, dict(tpk=t, **sk(s))) for t, s in itertools.product(('pct', 'atr2'), side2)])
        grid('flash', run_flash, "7. The Flash", TFS, 'mr60 ambos',
             [(f'mr{a} {s}', dict(mr=a, **sk(s))) for a, s in itertools.product((60, 50), side2)])
        grid('wvs', run_wvs, "8. Volatility System (Wilder)", TFS, 'arc1.8 ambos',
             [(f'arc{a:g} {s}', dict(arc=a, **sk(s))) for a, s in itertools.product((1.8, 3.0), side2)])
        grid('bbbo', run_bbbo, "9. Bollinger Band Breakout (long-only)", TFS, 'm1.5 lower',
             [(f'm{a:g} {e}', dict(mult=a, ext=e)) for a, e in itertools.product((1.5, 2.0), ('lower', 'basis'))])
        grid('simp', run_simp, "10. Simple strat (MACD + Stoch + RSI)", TFS, 'tp6 sl2 ambos',
             [(f'tp{a} sl{b} {s}', dict(tpm=a, slm=b, **sk(s))) for (a, b), s in itertools.product(((6, 2), (3, 1)), side2)])
        grid('sqr', run_sqr, "11. Squeeze Momentum on Reversal", TFS, 'f0.0018 ambos',
             [(f'f{a:g} {s}', dict(st=a, **sk(s))) for a, s in itertools.product((0.0018, 0.005), side2)])
        grid('tfb', run_tfb, "12. Trend Following Breakout", TFS, '100/50 ambos',
             [(f'{a}/{b} {s}', dict(en=a, xt=b, **sk(s))) for (a, b), s in itertools.product(((100, 50), (20, 10)), side2)])
        grid('wyk', run_wyk, "13. Wyckoff Range", TFS, 'sl10% ambos',
             [(f'sl{a:.0%} {s}', dict(sl=a, **sk(s))) for a, s in itertools.product((0.10, 0.03), side2)])
        grid('spk', run_spk, "14. Martin Pring's Special K", TFS, 's10 ambos',
             [(f's{a} {s}', dict(sm=a, **sk(s))) for a, s in itertools.product((10, 30), side2)])
        grid('atrts', run_atrts, "15. ATR Trailing Stops", TFS, 'a5x3.5 long',
             [(f'a{n}x{m:g} {s}', dict(n=n, mult=m, **sk(s))) for (n, m), s in itertools.product(((5, 3.5), (10, 2.0)), side2)])
        grid('e3', run_e3, "16. 3 EMA + Stoch RSI + ATR", TFS, 'tp4 ambos',
             [(f'tp{a:g} {s}', dict(tpm=a, **sk(s))) for a, s in itertools.product((4.0, 2.0), side2)])
        grid('ichb', run_ichb, "17. Ichimoku Backtester", TFS, '9/26/52 ambos',
             [('/'.join(map(str, p)) + f' {s}', dict(p=p, **sk(s))) for p, s in itertools.product(((9, 26, 52), (20, 60, 120)), side2)])
        grid('ssl', run_ssl, "18. SSL Channel Cross", TFS, 'l10 ambos',
             [(f'l{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((10, 50), side2)])
        grid('c2ac', run_c2ac, "19. Combo 2/20 EMA + AC", TFS, 'e14 ambos',
             [(f'e{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((14, 50), side2)])
        grid('obv', run_obv, "20. OBV Oscillator", TFS, 'l20 ambos',
             [(f'l{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((20, 50), side2)])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote27')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
