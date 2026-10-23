"""Lote 25 do TradingView (2026-10-23): 50 estrategias nos 5 ativos (ver docs/LOTE25_TV.md).

As puladas (na ordem da lista) estao documentadas em docs/LOTE25_TV.md.

uso: python study_tvlote25.py xau us100 wti btc eth
"""
import os, sys, itertools, math
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch, dmi
from study_tvlote9 import summary
from study_tvlote20 import sh, tr_, _trail, rma
from study_tvlote21 import G
from study_tvlote22 import run_stp, macd, meandev
from study_tvlote23 import vwhen, bsince, vwap_d
from study_tvlote24 import cci, st_line

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
full = lambda c, v: np.full(len(c), float(v))
ffill = lambda x: pd.Series(x).ffill().to_numpy()
ITF = TFS[:-1]
Z = lambda c: np.zeros(len(c), bool)


def hh(x, n): return roll(x, n).max().to_numpy()
def ll(x, n): return roll(x, n).min().to_numpy()


def run_loop(name, df, tag, rows, verbose, extra, L, S, ex=None, rev=True, long_ok=True, short_ok=True):
    """Simulador em Python: sinal no fechamento de j -> mercado na abertura de j+1. ex(j, lado, entrada, st)
    devolve (1, preco) para sair na propria barra j (stop/alvo intrabarra) ou (2, None) para sair na abertura
    seguinte; st e um dict zerado a cada entrada."""
    o, h, l, c = ohlc(df); n = len(c)
    Lb = (np.asarray(L, bool) & long_ok).tolist(); Sb = (np.asarray(S, bool) & short_ok).tolist()
    EI, EJ, ES, PI, PO = [], [], [], [], []
    pos = 0; pend = 0; px_ = False; ent = 0.0; i0 = 0; st = {}
    for j in range(1, n):
        if px_ and pos:
            EI.append(i0); EJ.append(j); ES.append(pos); PI.append(ent); PO.append(o[j]); pos = 0
        px_ = False
        if pend and pend != pos:
            if pos:
                EI.append(i0); EJ.append(j); ES.append(pos); PI.append(ent); PO.append(o[j])
            pos = pend; ent = o[j]; i0 = j; st = {}
        pend = 0
        if pos and ex is not None:
            k, px = ex(j, pos, ent, st)
            if k == 1:
                EI.append(i0); EJ.append(j); ES.append(pos); PI.append(ent); PO.append(px); pos = 0
            elif k == 2:
                px_ = True
        if Lb[j] and pos != 1 and (rev or pos == 0): pend = 1
        elif Sb[j] and pos != -1 and (rev or pos == 0): pend = -1
    r = tuple(np.array(x, t) for x, t in zip((EI, EJ, ES, PI, PO), (np.int64, np.int64, np.int64, float, float)))
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


def posflat(df, mm, p, long_ok=True, short_ok=True):
    """Posicao alvo +1/-1/0 (0 zera)."""
    return gsim(df, mm, p == 1, p == -1, p != 1, p != -1, rev=True, long_ok=long_ok, short_ok=short_ok)


def wilder_rsi(x, n):
    return T.rsi_wilder(np.asarray(x, float), n)


# ------------------------------------------------------------------ 1. Chandelier Exit
@njit(cache=True)
def _ce(c, hc, lc, a):
    n = len(c); ls = np.full(n, np.nan); ss = np.full(n, np.nan); d = np.ones(n)
    for i in range(n):
        ls[i] = hc[i] - a[i]; ss[i] = lc[i] + a[i]
        if i:
            lp = ls[i - 1] if ls[i - 1] == ls[i - 1] else ls[i]
            sp = ss[i - 1] if ss[i - 1] == ss[i - 1] else ss[i]
            if c[i - 1] > lp: ls[i] = max(ls[i], lp)
            if c[i - 1] < sp: ss[i] = min(ss[i], sp)
            d[i] = 1 if c[i] > sp else (-1 if c[i] < lp else d[i - 1])
    return d


def ce_dir(h, l, c, n=22, mult=3.0):
    return _ce(c, hh(c, n), ll(c, n), mult * T.atr_rma(h, l, c, n))


def run_ce(name, df, mm, tag, rows=None, verbose=True, risk=True, long_ok=True, short_ok=True, **extra):
    """Chandelier Exit (22, 3, extremos do close): virada compra/vende; stop de 5% no close, alvo 20% pela
    maxima, trailing de 5 pontos percentuais depois de +10% (risk=False: so a virada)."""
    o, h, l, c = ohlc(df); d = ce_dir(h, l, c)
    L, S = (d == 1) & (sh(d) == -1), (d == -1) & (sh(d) == 1)
    def ex(j, s, e, st):
        if s == 1:
            lo, hi = (c[j] - e) / e * 100, (h[j] - e) / e * 100
            pk = st.get('pk', 0.0)
            if lo < -5 or hi > 20 or (pk > 10 and pk - hi > 5): return 2, None
            st['pk'] = max(pk, hi)
        else:
            lo, hi = (c[j] - e) / e * 100, (l[j] - e) / e * 100
            pk = st.get('pk', 0.0)
            if lo > 5 or hi < -20 or (-pk > 10 and hi - pk > 5): return 2, None
            st['pk'] = min(pk, lo)
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex if risk else None, True, long_ok, short_ok)


# ------------------------------------------------------------------ 2. Bollinger Bands Enhanced
def run_bbe(name, df, mm, tag, rows=None, verbose=True, slm=1.75, **extra):
    """So long: minima acima da EMA200 tocando a banda inferior (BB20, 2); stop entrada - 1,75 ATR14; depois que
    a maxima passa entrada + 2,25 ATR, sai com close abaixo da media."""
    o, h, l, c = ohlc(df); m = T.sma(c, 20); lo = m - 2 * roll(c, 20).std(ddof=0).to_numpy()
    a = T.atr_rma(h, l, c, 14); L = (l > ema(c, 200)) & (l <= lo)
    def ex(j, s, e, st):
        if l[j] <= e - slm * a[j]: return 2, None
        if st.get('act') and c[j] < m[j]: return 2, None
        if h[j] > e + 2.25 * a[j]: st['act'] = True
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, False, True, False)


# ------------------------------------------------------------------ 3. Support Resistance
def run_sr(name, df, mm, tag, rows=None, verbose=True, lb=10, long_ok=True, short_ok=True, **extra):
    """R = maxima de 10 no penultimo cruzamento close x SMA10, S = minima de 10 idem; close rompe R compra, perde S
    vende; inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, lb); x = T.xover(c, m) | T.xunder(c, m)
    R, S_ = vwhen(x, hh(h, lb), 1), vwhen(x, ll(l, lb), 1)
    r = G(df, mm, T.xover(c, R), T.xunder(c, S_), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. MA Displaced Envelope + ATRTS
def run_made(name, df, mm, tag, rows=None, verbose=True, per=9, long_ok=True, short_ok=True, **extra):
    """Envelope +-0,5% da EMA9 deslocada 13 barras define a direcao; so fica posicionado se o close concordar com
    o ATR trailing stop (15, 2); senao zera."""
    o, h, l, c = ohlc(df); e = sh(ema(c, per), 13)
    p = ffill(np.where(c < e * 0.995, -1.0, np.where(c > e * 1.005, 1.0, NAN)))
    ts = _trail(c, 2 * T.atr_rma(h, l, c, 15))
    q = np.where((p == 1) & (c > ts), 1, np.where((p == -1) & (c < ts), -1, 0))
    return run_g(name, df, posflat(df, mm, q, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Hull MA TimeFrame CrossOver
def run_htf(name, df, mm, tag, rows=None, verbose=True, ln=1000, sens=14.0, long_ok=True, short_ok=True, **extra):
    """Sobre a abertura: HMA1000 subindo, HMA2 acima da abertura do dia e da HMA1000, e HMA1000 cruzando acima do
    ATR trailing (14 x ATR14) compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); ma = T.hma(o, ln); m0 = T.hma(o, 2)
    d1 = df.open.groupby(df.index.normalize()).transform('first').to_numpy()
    ts = _trail(o, sens * T.atr_rma(h, l, c, 14))
    L = (ma > sh(ma)) & (m0 > d1) & (m0 > ma) & T.xover(ma, ts)
    S = (ma < sh(ma)) & (m0 < d1) & (m0 < ma) & T.xover(ts, ma)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. CMO TradeDots
def cmo(x, n):
    d = np.diff(x, prepend=NAN); u = roll(np.where(d > 0, d, 0.0), n).sum().to_numpy(); v = roll(np.where(d < 0, -d, 0.0), n).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        return 100 * (u - v) / (u + v)


def run_cmo(name, df, mm, tag, rows=None, verbose=True, thr=40, long_ok=True, short_ok=True, **extra):
    """CMO9 e sinal EMA9: sinal abaixo de -40 com histograma negativo subindo compra; acima de 40 com histograma
    positivo caindo vende; fecha quando o sinal entra na zona oposta."""
    o, h, l, c = ohlc(df); cm = cmo(c, 9); sg = ema(np.nan_to_num(cm), 9); hs = cm - sg
    L = (sg < -thr) & (hs > sh(hs)) & (hs <= 0); S = (sg > thr) & (hs < sh(hs)) & (hs > 0)
    r = gsim(df, mm, L, S, sg > thr, sg < -thr, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. FlexiSuperTrend
@njit(cache=True)
def _flexi_med(src, hl2, atr, f0, inc):
    n = len(src); med = np.zeros(n); up = hl2[0] * np.ones(20); lo = hl2[0] * np.ones(20); tr = np.zeros(20)
    d = np.zeros(20)
    for i in range(n):
        f = f0
        for k in range(20):
            u = hl2[i] + atr[i] * f; dn = hl2[i] - atr[i] * f
            if src[i] > up[k]: tr[k] = 1
            elif src[i] < lo[k]: tr[k] = 0
            p = src[i - 1] if i else src[i]
            up[k] = min(u, up[k]) if p < up[k] else u
            lo[k] = max(dn, lo[k]) if p > lo[k] else dn
            out = lo[k] if tr[k] == 1 else up[k]
            d[k] = src[i] - out
            f += inc
        med[i] = np.median(d) if atr[i] == atr[i] else 0.0
    return med


@njit(cache=True)
def _st_bar(o, h, l, c, atr, fac):
    n = len(c); up = np.zeros(n); dn = np.zeros(n); st = np.zeros(n); d = np.ones(n)
    for i in range(n):
        hl = (h[i] + l[i]) / 2; a = atr[i] if atr[i] == atr[i] else 0.0
        u = hl + fac * a; v = hl - fac * a
        if i:
            if not (u < up[i - 1] or c[i - 1] > up[i - 1]): u = up[i - 1]
            if not (v > dn[i - 1] or c[i - 1] < dn[i - 1]): v = dn[i - 1]
        up[i] = u; dn[i] = v
        if i == 0 or atr[i - 1] != atr[i - 1]: d[i] = 1
        elif st[i - 1] == up[i - 1]: d[i] = -1 if c[i] > u else 1
        else: d[i] = 1 if c[i] < v else -1
        st[i] = v if d[i] == -1 else u
    return d


def run_flexi(name, df, mm, tag, rows=None, verbose=True, fac=15.0, long_ok=True, short_ok=True, **extra):
    """Mediana de (hlc3 - linha) de 20 SuperTrends (ATR10, fatores 0,618 + 0,382k); SuperTrend (10, 15) sobre
    velas sinteticas da mediana: direcao de alta com mediana > 0 compra (espelho vende); sai na virada."""
    o, h, l, c = ohlc(df)
    med = _flexi_med((h + l + c) / 3, (h + l) / 2, T.atr_rma(h, l, c, 10), 0.618, 0.382)
    bo = np.r_[0.0, med[:-1]]; bh, bl = np.maximum(bo, med), np.minimum(bo, med)
    d = _st_bar(bo, bh, bl, med, rma(tr_(bh, bl, med), 10), fac)
    r = gsim(df, mm, (d < 0) & (med > 0), (d > 0) & (med < 0), d > 0, d < 0, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. Moon Phases
def moon_age(dates):
    out = []
    for t in dates:
        y = t.year - (12 - t.month) // 10; m = t.month + 9
        if m >= 12: m -= 12
        k1 = math.floor(365.25 * (y + 4712)); k2 = math.floor(30.6 * m + 0.5); k3 = math.floor(math.floor(y / 100 + 49) * 0.75) - 38
        jd = k1 + k2 + t.day + 59
        if jd > 2299160: jd -= k3
        ip = (jd - 2451550.1) / 29.530588853; ip -= math.floor(ip)
        out.append(ip * 29.53)
    return np.array(out)


def run_moon(name, df, mm, tag, rows=None, verbose=True, inv=False, long_ok=True, short_ok=True, **extra):
    """Fase da lua pela data: compra na 'lua nova' do script (idade cruza 15) e vende quando a idade reinicia;
    inv troca os lados."""
    days = df.index.normalize(); ud = days.unique()
    ag = pd.Series(np.floor(moon_age(ud)), ud).reindex(days).to_numpy()
    m = np.where(sh(ag) > ag, 1, np.where((sh(ag) < 15) & (ag >= 15), -1, 0))
    L, S = (m == 1, m == -1) if inv else (m == -1, m == 1)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Triangular Hull MA
def run_thma(name, df, mm, tag, rows=None, verbose=True, ln=40, long_ok=True, short_ok=True, **extra):
    """THMA40 cruza ela mesma de 2 barras atras; inverte."""
    o, h, l, c = ohlc(df)
    t = T.wma(T.wma(c, ln // 3) * 3 - T.wma(c, ln // 2) - T.wma(c, ln), ln)
    r = G(df, mm, T.xover(t, sh(t, 2)), T.xunder(t, sh(t, 2)), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. DAX Shooter
def run_dax(name, df, mm, tag, rows=None, verbose=True, adx_t=32, long_ok=True, short_ok=True, **extra):
    """RSI7 cruza acima de 30 com ADX14 > 32 e minima abaixo da BB50 inferior compra (limite acima do preco =
    mercado); espelho vende; inverte."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 7); adx = dmi(h, l, c, 14)[2]
    m = T.sma(c, 50); sd = 2 * roll(c, 50).std(ddof=0).to_numpy()
    L = T.xover(r_, full(c, 30)) & (adx > adx_t) & (l < m - sd); S = T.xunder(r_, full(c, 70)) & (adx > adx_t) & (h > m + sd)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Master Supertrend
@njit(cache=True)
def _mst(c, pr, mr, mult):
    n = len(c); d = 1; dp = np.nan; dm = np.nan; bs = np.nan; ss = np.nan; out = np.ones(n)
    for i in range(n):
        cp = pr[i] * mult; cm = mr[i] * mult
        dp = min(dp if dp == dp else cp, cp) if d < 0 else cp
        dm = min(dm if dm == dm else cm, cm) if d > 0 else cm
        b = c[i] - dm; s = c[i] + dp
        bs = max(bs if bs == bs else b, b) if d > 0 else b
        ss = min(ss if ss == ss else s, s) if d < 0 else s
        if d > 0 and c[i] < bs: d = -1
        elif d < 0 and c[i] > ss: d = 1
        out[i] = d
    return out


def run_mst(name, df, mm, tag, rows=None, verbose=True, ln=60, mult=2.0, long_ok=True, short_ok=True, **extra):
    """SuperTrend de faixa +/- (maxima de 60 de max(h-o, h-c1) e max(o-l, c1-l)) x 2, stops so encolhem, viradas
    pelo close; sempre posicionado na direcao."""
    o, h, l, c = ohlc(df); c1 = sh(c)
    pr = hh(np.fmax(h - o, h - c1), ln); mr = hh(np.fmax(o - l, c1 - l), ln)
    d = _mst(c, np.nan_to_num(pr), np.nan_to_num(mr), mult)
    r = G(df, mm, d > 0, d < 0, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. State-aware MA Cross
def run_sma_state(name, df, mm, tag, rows=None, verbose=True, **extra):
    """So long: o par de medias muda com o estado (EMA20 subindo e close acima dela); cruzamento para cima da
    curta (do estado) sobre a longa compra, para baixo zera."""
    o, h, l, c = ohlc(df); b = ema(c, 20); up = b > sh(b); ab = c > b
    st = np.where(up, np.where(ab, 3, 2), np.where(ab, 1, 0))
    sm = np.select([st == 0, st == 1, st == 2], [ema(c, 15), T.sma(c, 19), rma(c, 16)], rma(c, 12))
    lm = np.select([st == 0, st == 1, st == 2], [T.hma(c, 24), rma(c, 45), T.hma(c, 59)], rma(c, 36))
    r = gsim(df, mm, T.xover(sm, lm), Z(c), T.xunder(sm, lm), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Dynamic RSI Momentum
@njit(cache=True)
def _drsi(x, ln):
    n = len(x); u = 0.0; v = 0.0; out = np.full(n, np.nan)
    for i in range(1, n):
        d = x[i] - x[i - 1]; a = 1.0 / ln[i]
        u = a * max(d, 0.0) + (1 - a) * u; v = a * max(-d, 0.0) + (1 - a) * v
        if i > 50 and v > 0: out[i] = 100 - 100 / (1 + u / v)
    return out


def run_drm(name, df, mm, tag, rows=None, verbose=True, lo=30, long_ok=True, short_ok=True, **extra):
    """RSI com periodo dinamico (20 a 50 pela correlacao close x momento 10) cruzando 30 para cima compra, 70 para
    baixo vende; inverte."""
    o, h, l, c = ohlc(df)
    cr = pd.Series(c).rolling(10).corr(pd.Series(c - sh(c, 10))).to_numpy()
    ln = 20 + np.nan_to_num(np.round((1 - cr) * 30 / 2))
    r_ = _drsi(c, ln.astype(float))
    r = G(df, mm, T.xover(r_, full(c, lo)), T.xunder(r_, full(c, 100 - lo)), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Range Strat MACD/RSI
def run_rmr(name, df, mm, tag, rows=None, verbose=True, sl=0.15, long_ok=True, short_ok=True, **extra):
    """Sobre a abertura: histograma MACD cruza zero para cima com RSI14 <= 55 compra; para baixo com RSI >= 50
    vende; stop 15%; inverte."""
    o, h, l, c = ohlc(df); m, s = macd(o); dl = m - s; r_ = wilder_rsi(o, 14)
    r = G(df, mm, T.xover(dl, Z(c) * 0.0) & (r_ <= 55), T.xunder(dl, Z(c) * 0.0) & (r_ >= 50), long_ok=long_ok, short_ok=short_ok, slp=sl)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Forex Fractal EMA Scalper
def fractals(h, l):
    up = (sh(h, 2) > sh(h)) & (sh(h, 2) > h) & (sh(h, 2) > sh(h, 3)) & (sh(h, 2) > sh(h, 4))
    dn = (sh(l, 2) < sh(l)) & (sh(l, 2) < l) & (sh(l, 2) < sh(l, 3)) & (sh(l, 2) < sh(l, 4))
    return up, dn


def run_ffe(name, df, mm, tag, rows=None, verbose=True, tp=0.005, inv=True, long_ok=True, short_ok=True, **extra):
    """EMAs 10/20/100 do hl2 alinhadas para cima + fractal de topo (2 barras) -> o script VENDE (sinais trocados;
    inv=False desfaz); TP/SL de 25 pips -> tp%."""
    o, h, l, c = ohlc(df); s = (h + l) / 2; e1, e2, e3 = ema(s, 10), ema(s, 20), ema(s, 100)
    fu, fd = fractals(h, l)
    up = (e1 > e2) & (e2 > e3) & fu; dn = (e1 < e2) & (e2 < e3) & fd
    L, S = (dn, up) if inv else (up, dn)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok, slp=tp, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Ichimoku + MACD/CMF/TSI
def run_imct(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """Tenkan10 > Kijun30, momento 25 > 0, close acima da nuvem (deslocada 25), histograma MACD (SMA do hl2) > 0,
    CMF10 > 0,1 e TSI(20, 20) > 0 compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    mid = lambda n: (hh(h, n) + ll(l, n)) / 2
    tk, kj = mid(10), mid(30); sa, sb = (tk + kj) / 2, mid(52)
    sH, sL = sh(np.fmax(sa, sb), 25), sh(np.fmin(sa, sb), 25)
    s = (h + l) / 2; m = T.sma(s, 12) - T.sma(s, 26); hs = m - ema(np.nan_to_num(m), 9)
    with np.errstate(divide='ignore', invalid='ignore'):
        ad = np.where(h == l, 0.0, (2 * c - l - h) / (h - l) * v)
        mf = roll(ad, 10).sum().to_numpy() / roll(v, 10).sum().to_numpy()
        pc = np.nan_to_num(np.diff(c, prepend=c[0])); tsi = 100 * ema(ema(pc, 20), 20) / ema(ema(np.abs(pc), 20), 20)
    mo = c - sh(c, 25)
    L = (tk > kj) & (mo > 0) & (c > sH) & (hs > 0) & (mf > 0.1) & (tsi > 0)
    S = (tk < kj) & (mo < 0) & (c < sL) & (hs < 0) & (mf < -0.1) & (tsi < 0)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. Hybrid RSI + Breakout
def run_hyb(name, df, mm, tag, rows=None, verbose=True, am=2.0, long_ok=True, short_ok=True, **extra):
    """ADX14 <= 20 (lateral): RSI14 < 40 acima da EMA200 compra, > 60 abaixo vende, sai com RSI cruzando 50;
    ADX > 20: rompimento de 20 closes a favor da EMA200 com trailing de 2 ATR ativado apos 2 ATR de lucro."""
    o, h, l, c = ohlc(df); adx = dmi(h, l, c, 14)[2]; e = ema(c, 200); r_ = wilder_rsi(c, 14); a = T.atr_rma(h, l, c, 14)
    tr_d, rg = adx > 20, adx <= 20
    rl, rs = rg & (r_ < 40) & (c > e), rg & (r_ > 60) & (c < e)
    bl, bs = tr_d & (c > e) & (c > sh(hh(c, 20))), tr_d & (c < e) & (c < sh(ll(c, 20)))
    L, S = rl | bl, rs | bs
    def ex(j, s, en, st):
        if 'k' not in st: st['k'] = 'rsi' if (rl[j - 1] if s == 1 else rs[j - 1]) else 'bo'; st['pk'] = en
        if st['k'] == 'rsi':
            return (2, None) if (r_[j] > 50 if s == 1 else r_[j] < 50) else (0, None)
        d = am * a[j - 1]
        if st.get('on'):
            stp = st['pk'] - s * d
            if (s == 1 and l[j] <= stp) or (s == -1 and h[j] >= stp):
                return 1, (min(o[j], stp) if s == 1 else max(o[j], stp))
        st['pk'] = max(st['pk'], h[j]) if s == 1 else min(st['pk'], l[j])
        if s * (st['pk'] - en) >= d: st['on'] = True
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, True, long_ok, short_ok)


# ------------------------------------------------------------------ 18. Combo 123 Reversal & RSI
def rev123(h, l, c):
    vf = stoch(c, h, l, 14); vs = T.sma(vf, 3); c1, c2 = sh(c), sh(c, 2)
    p = np.where((c2 < c1) & (c > c1) & (vf < vs) & (vf > 50), 1.0, np.where((c2 > c1) & (c < c1) & (vf > vs) & (vf < 50), -1.0, NAN))
    return pd.Series(p).ffill().fillna(0).to_numpy()


def run_c123r(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """123 Reversal (estocastico 14) e RSI12 fora de 30/70 concordando; discordando, zera."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 12)
    p2 = pd.Series(np.where(r_ > 70, 1.0, np.where(r_ < 30, -1.0, NAN))).ffill().fillna(0).to_numpy()
    p1 = rev123(h, l, c); q = np.where((p1 == 1) & (p2 == 1), 1, np.where((p1 == -1) & (p2 == -1), -1, 0))
    return run_g(name, df, posflat(df, mm, q, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. RSI Bull Div BigBitsIO
def run_rbd(name, df, mm, tag, rows=None, verbose=True, tp=0.03, sl=0.0175, **extra):
    """So long: RSI14 < 30, RSI suavizado (HMA10) < 35 caindo ha 3+ barras, minima do suavizado em 25 < 25, close
    abaixo do close da barra do menor RSI em 25 e RSI acima desse minimo (divergencia); TP 3%, SL 1,75%; sai com
    RSI > 65."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, 14)
    sr = T.wma(2 * T.wma(r_, 5) - T.wma(r_, 10), 3)
    dn = sr < sh(sr); cnt = np.zeros(len(c))
    for i in range(1, len(c)): cnt[i] = cnt[i - 1] + 1 if dn[i] else 0
    W = np.lib.stride_tricks.sliding_window_view(np.nan_to_num(r_, nan=1e9), 25)
    off = np.zeros(len(c), int); off[24:] = np.argmin(W[:, ::-1], axis=1)
    idx = np.arange(len(c)) - off
    tgt = c[np.clip(idx, 0, None)]
    L = (r_ < 30) & (sr < 35) & (ll(sr, 25) < 25) & (c < tgt) & (cnt >= 3) & (r_ > ll(r_, 25))
    r = gsim(df, mm, L, Z(c), r_ > 65, rev=False, short_ok=False, slp=sl, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. EMA Long Only
def run_elo(name, df, mm, tag, rows=None, verbose=True, ln=21, **extra):
    """So long: SMA2 cruza acima da EMA21 + ATR21 compra; cruza abaixo da EMA21 - ATR21 zera."""
    o, h, l, c = ohlc(df); p = T.sma(c, 2); e = ema(c, ln); a = T.atr_rma(h, l, c, ln)
    r = gsim(df, mm, T.xover(p, e + a), Z(c), T.xunder(p, e - a), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 21. Mutanabby AI Algo Pro
def run_muta(name, df, mm, tag, rows=None, verbose=True, sl=0.02, **extra):
    """So long: engolfo de alta com corpo/TR > 0,5, RSI14 < 50 e close abaixo de 5 barras atras compra; engolfo de
    baixa espelhado zera; stop 2% da entrada."""
    o, h, l, c = ohlc(df); tr = tr_(h, l, c)
    with np.errstate(divide='ignore', invalid='ignore'):
        stb = np.abs(c - o) / tr > 0.5
    r_ = wilder_rsi(c, 14)
    L = (sh(c) < sh(o)) & (c > o) & (c > sh(o)) & stb & (r_ < 50) & (c < sh(c, 5))
    X = (sh(c) > sh(o)) & (c < o) & (c < sh(o)) & stb & (r_ > 50) & (c > sh(c, 5))
    r = gsim(df, mm, L, Z(c), X, rev=False, short_ok=False, slp=sl)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 22. Pivot of Pivot Reversal
def run_pop(name, df, mm, tag, rows=None, verbose=True, lb=4, rb=2, long_ok=True, short_ok=True, **extra):
    """Pivos (4, 2) com folga de 0,1 ATR14; pivo de pivos (o do meio de 3 maiores); stop de compra acima do pivo
    de pivos de topo enquanto o topo recente nao foi rompido (espelho na venda); inverte."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 14) * 0.1; n = len(c)
    ok_h = np.ones(n, bool); ok_l = np.ones(n, bool); hr, lr = sh(h, rb), sh(l, rb)
    for i in range(1, lb + 1):
        ok_h &= ~(hr < sh(h, rb + i) + a); ok_l &= ~(lr > sh(l, rb + i) - a)
    for i in range(0, rb):
        ok_h &= ~(hr < sh(h, i) + a) if i else ~(hr < h + a); ok_l &= ~(lr > sh(l, i) - a) if i else ~(lr > l - a)
    ok_h &= ~np.isnan(hr); ok_l &= ~np.isnan(lr)
    LE = full(c, NAN); SE = full(c, NAN)
    hp = lp = 0.0; le = se = False; ph = [0.0, 0.0, 0.0]; pl = [0.0, 0.0, 0.0]; pph = ppl = 0.0
    for i in range(n):
        if ok_h[i]:
            hp = hr[i]; le = True; ph = [hp, ph[0], ph[1]]
            if ph[1] > ph[0] and ph[1] > ph[2]: pph = ph[1]
        elif le and h[i] > hp: le = False
        if ok_l[i]:
            lp = lr[i]; se = True; pl = [lp, pl[0], pl[1]]
            if pl[1] < pl[0] and pl[1] < pl[2]: ppl = pl[1]
        elif se and l[i] < lp: se = False
        if le and pph: LE[i] = pph
        if se and ppl: SE[i] = ppl
    return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 23. Mov Avg Speed (3 sinais)
def run_mas(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """Voto de 3 (ROC1 medio de 10 da SMA50, estocastico 14 em 20/80, EMA9 do MACD subindo): 2 a favor compra ou
    vende; inverte."""
    o, h, l, c = ohlc(df); a = T.sma(c, 50)
    with np.errstate(divide='ignore', invalid='ignore'):
        rc = T.sma(100 * (a - sh(a)) / sh(a), 10)
    k = T.sma(stoch(c, h, l, 14), 3); m, sg = macd(c)
    s1 = np.sign(np.nan_to_num(rc)); s2 = np.where(k <= 20, 1, np.where(k >= 80, -1, 0)); s3 = np.sign(np.nan_to_num(sg - sh(sg)))
    lc = (s1 == 1).astype(int) + (s2 == 1) + (s3 == 1); sc = (s1 == -1).astype(int) + (s2 == -1) + (s3 == -1)
    r = G(df, mm, lc >= 2, sc >= 2, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 24. RSI mensal
def run_rsim(name, df, mm, tag, rows=None, verbose=True, **extra):
    """So long: RSI14 mensal (mes fechado) acima da sua SMA14 compra, abaixo zera."""
    o, h, l, c = ohlc(df)
    mc = df.close.resample('MS').last().dropna(); r_ = wilder_rsi(mc.to_numpy(float), 14); s = T.sma(r_, 14)
    sig = pd.Series(np.where(np.isnan(s), NAN, np.sign(r_ - s)), mc.index + pd.offsets.MonthBegin(1))
    v = sig.reindex(df.index.union(sig.index)).ffill().reindex(df.index).to_numpy()
    r = gsim(df, mm, v == 1, Z(c), v == -1, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 25. Davin 10/200 MA Pullback
def run_davin(name, df, mm, tag, rows=None, verbose=True, dip=14, sl=0.15, **extra):
    """So long: close acima da SMA200 e abaixo da SMA10 (ou 14% abaixo da maxima de 52) compra; sai com close acima
    da SMA10 e abaixo da minima anterior, ou close 15% abaixo da entrada."""
    o, h, l, c = ohlc(df); m1, m2 = T.sma(c, 200), T.sma(c, 10); hi = hh(h, 52)
    L = ((c > m1) & (c < m2)) | ((hi - c) / hi * 100 >= dip)
    X = (c > m2) & (c < sh(l))
    def ex(j, s, e, st): return (2, None) if (X[j] or (e - c[j]) / c[j] > sl) else (0, None)
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, False, True, False)


# ------------------------------------------------------------------ 26. MA Scalper Coinrule
def run_masc(name, df, mm, tag, rows=None, verbose=True, sl=0.02, tp=0.08, **extra):
    """So long: SMA9 cruza acima da SMA50 com SMA50 < SMA100 < SMA200 compra; sai com SMA9 cruzando a SMA200,
    stop 2%, alvo 8%."""
    o, h, l, c = ohlc(df); s9, s50, s100, s200 = (T.sma(c, n) for n in (9, 50, 100, 200))
    L = T.xover(s9, s50) & (s50 < s100) & (s100 < s200)
    r = gsim(df, mm, L, Z(c), T.xover(s9, s200), rev=False, short_ok=False, slp=sl, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 27. BEST Trailing Stop
def run_bts(name, df, mm, tag, rows=None, verbose=True, trl=0.03, long_ok=True, short_ok=True, **extra):
    """SMA15 x SMA45 inverte; stop movel = minima x 0,97 (maxima x 1,03 no short) desde o cruzamento, so anda a
    favor; a perda dele fecha na abertura seguinte."""
    o, h, l, c = ohlc(df); f, s = T.sma(c, 15), T.sma(c, 45); L, S = T.xover(f, s), T.xunder(f, s)
    n = len(c); XL = Z(c); XS = Z(c); tr = 0; ls = 0.0; ss = 1e18
    for i in range(1, n):
        if L[i]: tr = 1; ls = 0.0
        elif S[i]: tr = -1; ss = 1e18
        if tr == 1:
            if l[i] < ls and l[i - 1] >= ls: XL[i] = True
            ls = max(ls, l[i] * (1 - trl))
        elif tr == -1:
            if h[i] > ss and h[i - 1] <= ss: XS[i] = True
            ss = min(ss, h[i] * (1 + trl))
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 28. Grover Llorens Activator
@njit(cache=True)
def _grover(c, atr, ln, mult):
    n = len(c); ts = np.zeros(n); up = np.zeros(n, np.bool_); dn = np.zeros(n, np.bool_)
    ts[0] = c[0]; val = 0.0; bars = 0; pd_ = 0.0
    for i in range(1, n):
        d = c[i] - ts[i - 1]
        up[i] = d > 0 and pd_ <= 0; dn[i] = d < 0 and pd_ >= 0
        a = atr[i] if atr[i] == atr[i] else 0.0
        if up[i] or dn[i]: val = a / ln; bars = 0
        else: bars += 1
        if up[i]: ts[i] = ts[i - 1] - a * mult
        elif dn[i]: ts[i] = ts[i - 1] + a * mult
        else: ts[i] = ts[i - 1] + np.sign(d) * val * bars
        pd_ = d
    return up, dn


def run_grov(name, df, mm, tag, rows=None, verbose=True, ln=480, mult=14.0, long_ok=True, short_ok=True, **extra):
    """Grover Llorens Activator (480, 14): close cruzando a linha compra/vende; inverte."""
    o, h, l, c = ohlc(df); up, dn = _grover(c, T.atr_rma(h, l, c, ln), float(ln), mult)
    r = G(df, mm, up, dn, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 29. VWAP Breakout
def run_vwbo(name, df, mm, tag, rows=None, verbose=True, tpm=2.0, long_ok=True, short_ok=True, **extra):
    """Close cruza a VWAP diaria: compra/vende; stop 1,5 ATR14, alvo 2 ATR14 (do sinal); inverte."""
    o, h, l, c = ohlc(df); vw = vwap_d(df); a = T.atr_rma(h, l, c, 14)
    r = gsim(df, mm, T.xover(c, vw), T.xunder(c, vw), SLL=c - 1.5 * a, TPL=c + tpm * a, SLS=c + 1.5 * a, TPS=c - tpm * a,
             rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 30. Stoch/EMA Cross
def run_sec(name, df, mm, tag, rows=None, verbose=True, tp=0.08, long_ok=True, short_ok=True, **extra):
    """Estocastico (14, 6, 3) cruza para cima abaixo de 20 com EMA55 >= EMA89 compra; espelho acima de 80 vende;
    sai com %D cruzando 80/20 ou o cruzamento das EMAs; alvo 8%."""
    o, h, l, c = ohlc(df); f, s = ema(c, 55), ema(c, 89); k = T.sma(stoch(c, h, l, 14), 6); d = T.sma(k, 3)
    L = T.xover(k, d) & (k < 20) & (f >= s); S = T.xunder(k, d) & (k > 80) & (f < s)
    XL = T.xover(d, full(c, 80)) | T.xunder(f, s); XS = T.xunder(d, full(c, 20)) | T.xover(f, s)
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 31. EMA Cross + RSI + ADX
def run_era(name, df, mm, tag, rows=None, verbose=True, sl=0.02, long_ok=True, short_ok=True, **extra):
    """EMA9 x EMA21 com RSI14 > 55 compra, < 40 vende; fecha no cruzamento contrario; stop 2% do close do sinal."""
    o, h, l, c = ohlc(df); a, b = ema(c, 9), ema(c, 21); r_ = wilder_rsi(c, 14); u, d = T.xover(a, b), T.xunder(a, b)
    r = gsim(df, mm, u & (r_ > 55), d & (r_ < 40), d, u, SLL=c * (1 - sl), SLS=c * (1 + sl), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 32. Multi-X
def run_mx(name, df, mm, tag, rows=None, verbose=True, **extra):
    """So long: EMA9 cruza acima da SMA21 compra, abaixo zera."""
    o, h, l, c = ohlc(df); a, b = ema(c, 9), T.sma(c, 21)
    r = gsim(df, mm, T.xover(a, b), Z(c), T.xunder(a, b), rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 33. Trend Reversal Alerts
def run_tra(name, df, mm, tag, rows=None, verbose=True, **extra):
    """So long: dois closes subindo com vela de alta (resistencia > 0) compra; dois caindo com vela de baixa zera."""
    o, h, l, c = ohlc(df); sp = np.abs(c - o)
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = np.where(o > c, -(h - l) / sp, (h - l) / sp)
    L = (sh(c) > sh(c, 2)) & (c > sh(c)) & (rs > 0); X = (sh(c) < sh(c, 2)) & (c < sh(c)) & (rs < 0)
    r = gsim(df, mm, L, Z(c), X, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 34. MACD + CCI
def run_mcci(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """CCI14 > 100 com MACD > 0, ou CCI > -100 com MACD < 0, compra; CCI < -100 com MACD < 0, ou CCI < 100 com MACD
    > 0, vende (a venda prevalece quando as duas valem); as 'saidas' do script nao tem efeito; inverte."""
    o, h, l, c = ohlc(df); cc = cci(c, 14); m = ema(c, 12) - ema(c, 26)
    lc = ((cc > 100) & (m > 0)) | ((cc > -100) & (m < 0)); sc = ((cc < -100) & (m < 0)) | ((cc < 100) & (m > 0))
    r = G(df, mm, lc & ~sc, sc, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 35. Uhl MA System
@njit(cache=True)
def _uhl(c, var, sma):
    n = len(c); cma = np.zeros(n); cts = np.zeros(n)
    for i in range(n):
        pc = cma[i - 1] if i else c[i]; pt = cts[i - 1] if i else c[i]
        if var[i] != var[i]: cma[i] = pc; cts[i] = pt; continue
        a = (sma[i] - pc) ** 2; b = (c[i] - pt) ** 2
        ka = 1 - var[i] / a if var[i] < a else 0.0; kb = 1 - var[i] / b if var[i] < b else 0.0
        cma[i] = ka * sma[i] + (1 - ka) * pc; cts[i] = kb * c[i] + (1 - kb) * pt
    return cma, cts


def run_uhl(name, df, mm, tag, rows=None, verbose=True, ln=100, long_ok=True, short_ok=True, **extra):
    """Uhl MA (100): CTS cruza a CMA; inverte."""
    o, h, l, c = ohlc(df); cma, cts = _uhl(c, roll(c, ln).var(ddof=0).to_numpy(), T.sma(c, ln))
    r = G(df, mm, T.xover(cts, cma), T.xunder(cts, cma), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 36. Swing HULL + T3
def t3(x, n, v=0.7):
    e1 = ema(x, n); e2 = ema(e1, n); e3 = ema(e2, n); e4 = ema(e3, n); e5 = ema(e4, n); e6 = ema(e5, n)
    c1 = -v ** 3; c2 = 3 * v ** 2 + 3 * v ** 3; c3 = -6 * v ** 2 - 3 * v - 3 * v ** 3; c4 = 1 + 3 * v + v ** 3 + 3 * v ** 2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def run_ht3(name, df, mm, tag, rows=None, verbose=True, ln=50, sltp=True, long_ok=True, short_ok=True, **extra):
    """Media de HMA50 e T3(50, 0,7) subindo compra, caindo vende; alvo 8% no long, alvo 3% / stop 6% no short."""
    o, h, l, c = ohlc(df); a = (T.hma(c, ln) + t3(c, ln)) / 2
    kw = dict(TPL=c * 1.08, TPS=c * 0.97, SLS=c * 1.06) if sltp else {}
    r = gsim(df, mm, a > sh(a), a < sh(a), rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 37. TASC One Percent A Week
def run_opw(name, df, mm, tag, rows=None, verbose=True, dip=0.01, tp=0.01, **extra):
    """So long: limite de compra 1% abaixo da abertura de segunda (UTC); alvo de 1% sobre a entrada a partir do
    dia seguinte; se cair 0,5%, alvo vira o preco de entrada; zera no fechamento da ultima barra de sexta."""
    o, h, l, c = ohlc(df); n = len(c); idx = df.index; dw = idx.dayofweek.to_numpy(); dd = idx.normalize()
    newday = np.r_[True, dd[1:] != dd[:-1]]; lastday = np.r_[dd[1:] != dd[:-1], True]
    EI, EJ, ES, PI, PO = [], [], [], [], []
    lim = NAN; pos = False; ent = 0.0; i0 = 0; pt = NAN; send = False; be = False
    for j in range(n):
        if newday[j] and dw[j] == 0 and not pos: lim = o[j] * (1 - dip)
        if pos:
            if newday[j] and send and not be: pt = ent * (1 + tp); send = False
            if not be and l[j] < ent * 0.995: pt = ent; be = True
            if pt == pt and h[j] >= pt and j > i0:
                EI.append(i0); EJ.append(j); ES.append(1); PI.append(ent); PO.append(max(o[j], pt)); pos = False
            elif dw[j] == 4 and lastday[j]:
                EI.append(i0); EJ.append(j); ES.append(1); PI.append(ent); PO.append(c[j]); pos = False
        elif lim == lim and l[j] <= lim and dw[j] <= 4:
            pos = True; ent = min(o[j], lim); i0 = j; lim = NAN; pt = NAN; send = True; be = False
            if dw[j] == 4 and lastday[j]:
                EI.append(i0); EJ.append(j); ES.append(1); PI.append(ent); PO.append(c[j]); pos = False
        if dw[j] == 4 and lastday[j]: lim = NAN
    r = tuple(np.array(x, t) for x, t in zip((EI, EJ, ES, PI, PO), (np.int64, np.int64, np.int64, float, float)))
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 38. Stoch + ATR
def run_sta(name, df, mm, tag, rows=None, verbose=True, ln=34, long_ok=True, short_ok=True, **extra):
    """Estocastico 34 (suav. 2) cruza acima de 90 - RSI34 do ATR34 compra; abaixo de RSI(ATR) + 10 vende;
    inverte."""
    o, h, l, c = ohlc(df); k = T.sma(stoch(c, h, l, ln), 2); ra = wilder_rsi(T.atr_rma(h, l, c, ln), ln)
    r = G(df, mm, T.xover(k, 100 - ra - 10), T.xunder(k, ra + 10), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 39. SPY Master
def run_spym(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """RSI2 do ohlc4: EMA3 cruza acima de 50 compra, EMA5 cruza abaixo de 50 vende; inverte."""
    o, h, l, c = ohlc(df); b = np.nan_to_num(wilder_rsi((o + h + l + c) / 4, 2), nan=50.0)
    r = G(df, mm, T.xover(ema(b, 3), full(c, 50)), T.xunder(ema(b, 5), full(c, 50)), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 40. KPL Swing
def run_kpl(name, df, mm, tag, rows=None, verbose=True, ln=20, long_ok=True, short_ok=True, **extra):
    """Rompimento da maxima/minima de 20 define o lado; linha = minima de 20 (lado comprado) ou maxima de 20;
    close cruza a linha compra/vende; inverte."""
    o, h, l, c = ohlc(df); rs, sp = hh(h, ln), ll(l, ln)
    av = ffill(np.where(c > sh(rs), 1.0, np.where(c < sh(sp), -1.0, NAN)))
    t = np.where(av == 1, sp, rs)
    r = G(df, mm, T.xover(c, t), T.xunder(c, t), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 41. Gianno Nano
def run_gn(name, df, mm, tag, rows=None, verbose=True, sltp=True, long_ok=True, short_ok=True, **extra):
    """EMA10 x EMA60 inverte; stop 3% / alvo 36% no long, stop 5% / alvo 24% no short (do close do sinal)."""
    o, h, l, c = ohlc(df); a, b = ema(c, 10), ema(c, 60)
    kw = dict(SLL=c * 0.97, TPL=c * 1.36, SLS=c * 1.05, TPS=c * 0.76) if sltp else {}
    r = gsim(df, mm, T.xover(a, b), T.xunder(a, b), rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 42. Trendline Breakout KedArc
def run_tlb(name, df, mm, tag, rows=None, verbose=True, pv=5, maf=True, long_ok=True, short_ok=True, **extra):
    """LTA pelos dois ultimos fundos (se ascendentes) e LTB pelos dois ultimos topos (se descendentes), pivos 5/5;
    close rompe a LTB acima da EMA200 compra, perde a LTA abaixo dela vende; stop 2 ATR14, alvo 4 ATR; inverte."""
    o, h, l, c = ohlc(df); n = len(c); e = ema(c, 200); a = T.atr_rma(h, l, c, 14)
    pl, ph = T.pivotlow(l, pv, pv), T.pivothigh(h, pv, pv)
    up = full(c, NAN); dn = full(c, NAN); PL = []; PH = []; ut = dt = None
    for i in range(n):
        if pl[i]:
            PL.append((i - pv, l[i - pv]))
            if len(PL) >= 2 and PL[-1][1] > PL[-2][1]: ut = (PL[-2], PL[-1])
        if ph[i]:
            PH.append((i - pv, h[i - pv]))
            if len(PH) >= 2 and PH[-1][1] < PH[-2][1]: dt = (PH[-2], PH[-1])
        if ut: (x1, y1), (x2, y2) = ut; up[i] = y1 + (y2 - y1) / (x2 - x1) * (i - x1)
        if dt: (x1, y1), (x2, y2) = dt; dn[i] = y1 + (y2 - y1) / (x2 - x1) * (i - x1)
    L = T.xover(c, dn) & ((c > e) if maf else True); S = T.xunder(c, up) & ((c < e) if maf else True)
    r = gsim(df, mm, L, S, SLL=c - 2 * a, TPL=c + 4 * a, SLS=c + 2 * a, TPS=c - 4 * a, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 43. Fractal Breakout
def fr_bw(x, sgn):
    """Fractal de Bill Williams na barra x[2] (topo: sgn=1), com ate 4 iguais a esquerda."""
    y = sgn * np.asarray(x, float); p = sh(y, 2); r = (sh(y, 1) < p) & (y < p)
    out = np.zeros(len(y), bool)
    for k in range(5):
        cond = r & (sh(y, 3 + k) < p) & (sh(y, 4 + k) < p)
        for m in range(3, 3 + k): cond &= sh(y, m) <= p
        out |= cond
    return out


def run_fbo(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """Close cruza acima do penultimo fractal de topo compra; abaixo do penultimo fractal de fundo vende; inverte."""
    o, h, l, c = ohlc(df)
    FU = vwhen(fr_bw(h, 1), sh(h, 2), 1); FD = vwhen(fr_bw(l, -1), sh(l, 2), 1)
    r = G(df, mm, T.xover(c, FU), T.xunder(c, FD), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 44. Double Bottom and Top Hunter
def run_dbt(name, df, mm, tag, rows=None, verbose=True, ln=100, long_ok=True, short_ok=True, **extra):
    """Minima igual a minima de 100 e igual a minima da ocorrencia anterior (fundo duplo exato) compra; topo duplo
    vende; inverte (as saidas do script nunca disparam)."""
    o, h, l, c = ohlc(df); l1, h1 = ll(l, ln), hh(h, ln)
    l2 = vwhen(l == l1, l, 1); h2 = vwhen(h == h1, h, 1)
    r = G(df, mm, (l == l1) & (l == l2), (h == h1) & (h == h2), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 45. BEST ATR Stop Multiple
def run_bas(name, df, mm, tag, rows=None, verbose=True, am=2.0, long_ok=True, short_ok=True, **extra):
    """SMA15 x SMA45 inverte; stop = close do sinal - 2 ATR14 (espelho no short)."""
    o, h, l, c = ohlc(df); f, s = T.sma(c, 15), T.sma(c, 45); a = T.atr_rma(h, l, c, 14)
    r = gsim(df, mm, T.xover(f, s), T.xunder(f, s), SLL=c - am * a, SLS=c + am * a, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 46. NR7ID short-only
def run_nr7s(name, df, mm, tag, rows=None, verbose=True, maf=True, **extra):
    """So short: NR7 + inside bar de baixa com SMA14 nao subindo vende; zera na proxima vela de baixa."""
    o, h, l, c = ohlc(df); rg = h - l
    nr7 = np.ones(len(c), bool)
    for k in range(1, 7): nr7 &= rg < sh(rg, k)
    m = T.sma(c, 14); S = nr7 & (h < sh(h)) & (l > sh(l)) & (o > c)
    if maf: S &= ~(m > sh(m))
    r = gsim(df, mm, Z(c), S, None, o > c, rev=False, long_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 47. Reversal Trading Bot BullByte
def run_rtb(name, df, mm, tag, rows=None, verbose=True, sl=0.01, tp=0.02, long_ok=True, short_ok=True, **extra):
    """Divergencia simples (minima de 5 caindo com minimo do RSI8 de 5 subindo; espelho) compra/vende; stop 1%,
    alvo 2%; filtros opcionais desligados (padrao); inverte."""
    o, h, l, c = ohlc(df); r_ = sh(wilder_rsi(c, 8))
    a, b = sh(ll(l, 5)), sh(ll(l, 5), 2); ra, rb = sh(ll(r_, 5)), sh(ll(r_, 5), 2)
    x, y = sh(hh(h, 5)), sh(hh(h, 5), 2); rx, ry = sh(hh(r_, 5)), sh(hh(r_, 5), 2)
    r = G(df, mm, (a < b) & (ra > rb), (x > y) & (rx < ry), long_ok=long_ok, short_ok=short_ok, slp=sl, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 48. Multi-MA (4MA)
def run_4ma(name, df, mm, tag, rows=None, verbose=True, base=75, long_ok=True, short_ok=True, **extra):
    """HMA3 dupla, VWMA3 e WMA75: HMA subindo abaixo da WMA75 e acima da VWMA compra (so flat); espelho vende;
    fecha quando a HMA vira do outro lado da VWMA."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        rv = roll(c * v, 3).sum().to_numpy() / roll(v, 3).sum().to_numpy()
    y = T.wma(c, base); n1 = T.wma(2 * T.wma(c, 2) - T.wma(c, 3), 2); n2 = sh(n1)
    L = (n1 > n2) & (n1 < y) & (n1 > rv); S = (n1 < n2) & (n1 > y) & (n1 < rv)
    XL = (n1 < n2) & (n1 > y) & (n1 < rv); XS = (n1 > n2) & (n1 < y) & (n1 > rv)
    r = gsim(df, mm, L, S, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 49. Awesome Oscillator
def run_ao(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """AO (SMA5 - SMA34 do hl2) subindo compra, caindo vende; inverte."""
    o, h, l, c = ohlc(df); s = (h + l) / 2; a = T.sma(s, 5) - T.sma(s, 34)
    p = ffill(np.where(a > sh(a), 1.0, np.where(a < sh(a), -1.0, NAN)))
    r = G(df, mm, p == 1, p == -1, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 50. Smart Money Pivot
def run_smp(name, df, mm, tag, rows=None, verbose=True, per=20, sl=0.01, tp=0.015, long_ok=True, short_ok=True, **extra):
    """Rompimento (pela maxima) do ultimo pivo de topo (20/20) ainda ativo compra; perda do ultimo pivo de fundo
    vende; stop 1%, alvo 1,5%; inverte."""
    o, h, l, c = ohlc(df); n = len(c)
    ph, pl = T.pivothigh(h, per, per), T.pivotlow(l, per, per)
    B = Z(c); S = Z(c); uh = ul = NAN; ah = al = False
    for i in range(n):
        if ph[i] and h[i - per] != uh: uh = h[i - per]; ah = True
        if pl[i] and l[i - per] != ul: ul = l[i - per]; al = True
        if ah and h[i] > uh: B[i] = True; ah = False
        if al and l[i] < ul: S[i] = True; al = False
    r = G(df, mm, B, S, long_ok=long_ok, short_ok=short_ok, slp=sl, tpp=tp)
    return run_g(name, df, r, tag, rows, verbose, extra)


SPECS = [
    ('ce', run_ce, "1. Chandelier Exit", TFS, 'risco ambos', [(('risco ' if k else 'semrisco ') + s, dict(risk=k, short_ok=s == 'ambos')) for k in (True, False) for s in ('ambos', 'long')]),
    ('bbe', run_bbe, "2. Bollinger Bands Enhanced (long-only)", TFS, 'sl1.75', [(f'sl{x:g}', dict(slm=x)) for x in (1.75, 3.0)]),
    ('sr', run_sr, "3. Support Resistance", TFS, '10 ambos', 'lb'),
    ('made', run_made, "4. MA Displaced Envelope + ATRTS", TFS, '9 ambos', 'per'),
    ('htf', run_htf, "5. Hull MA TimeFrame CrossOver", TFS, '1000 s14 ambos', [(f'{a} s{b:g} {s}', dict(ln=a, sens=b, short_ok=s == 'ambos')) for a in (1000, 200) for b in (14.0, 3.0) for s in ('ambos', 'long')]),
    ('cmo', run_cmo, "6. CMO TradeDots", TFS, '40 ambos', 'thr'),
    ('flexi', run_flexi, "7. FlexiSuperTrend", TFS, 'f15 ambos', [(f'f{f:g} {s}', dict(fac=f, short_ok=s == 'ambos')) for f in (15.0, 5.0) for s in ('ambos', 'long')]),
    ('moon', run_moon, "8. Moon Phases", TFS, 'normal ambos', [(('inv ' if i else 'normal ') + s, dict(inv=i, short_ok=s == 'ambos')) for i in (False, True) for s in ('ambos', 'long')]),
    ('thma', run_thma, "9. Triangular Hull MA", TFS, '40 ambos', 'ln'),
    ('dax', run_dax, "10. DAX Shooter", TFS, 'adx32 ambos', [(f'adx{a} {s}', dict(adx_t=a, short_ok=s == 'ambos')) for a in (32, 20) for s in ('ambos', 'long')]),
    ('mst', run_mst, "11. Master Supertrend", TFS, '60 m2 ambos', [(f'{a} m{m:g} {s}', dict(ln=a, mult=m, short_ok=s == 'ambos')) for a in (60, 20) for m in (2.0, 4.0) for s in ('ambos', 'long')]),
    ('stma', run_sma_state, "12. State-aware MA Cross (long-only)", TFS, 'padrao', []),
    ('drm', run_drm, "13. Dynamic RSI Momentum", TFS, '30/70 ambos', [(f'{a}/{100 - a} {s}', dict(lo=a, short_ok=s == 'ambos')) for a in (30, 20) for s in ('ambos', 'long')]),
    ('rmr', run_rmr, "14. Range Strat MACD/RSI", TFS, 'sl15 ambos', [(f'sl{x:.0%} {s}', dict(sl=x, short_ok=s == 'ambos')) for x in (0.15, 0.05) for s in ('ambos', 'long')]),
    ('ffe', run_ffe, "15. Forex Fractal EMA Scalper", TFS, 'tp0.5 inv ambos', [(f'tp{t:.1%} ' + ('inv ' if i else 'direto ') + s, dict(tp=t, inv=i, short_ok=s == 'ambos')) for t in (0.005, 0.02) for i in (True, False) for s in ('ambos', 'long')]),
    ('imct', run_imct, "16. Ichimoku + MACD/CMF/TSI", TFS, 'ambos', []),
    ('hyb', run_hyb, "17. Hybrid RSI + Breakout", TFS, 'atr2 ambos', [(f'atr{a:g} {s}', dict(am=a, short_ok=s == 'ambos')) for a in (2.0, 4.0) for s in ('ambos', 'long')]),
    ('c123r', run_c123r, "18. Combo 123 Reversal + RSI", TFS, 'ambos', []),
    ('rbd', run_rbd, "19. RSI Bull Div (long-only)", TFS, 'tp3 sl1.75', [('tp6 sl3.5', dict(tp=0.06, sl=0.035))]),
    ('elo', run_elo, "20. EMA Long Only", TFS, '21', [('50', dict(ln=50))]),
    ('muta', run_muta, "21. Mutanabby AI Algo Pro (long-only)", TFS, 'sl2', [('sl5', dict(sl=0.05)), ('semsl', dict(sl=0.0))]),
    ('pop', run_pop, "22. Pivot of Pivot Reversal", TFS, '4/2 ambos', [(f'{a}/{b} {s}', dict(lb=a, rb=b, short_ok=s == 'ambos')) for a, b in ((4, 2), (10, 5)) for s in ('ambos', 'long')]),
    ('mas', run_mas, "23. Mov Avg Speed (3 sinais)", TFS, 'ambos', []),
    ('rsim', run_rsim, "24. RSI mensal (long-only)", TFS, 'padrao', []),
    ('davin', run_davin, "25. Davin 10/200 MA Pullback (long-only)", TFS, 'dip14 sl15', [('dip30 sl15', dict(dip=30)), ('dip14 sl5', dict(sl=0.05))]),
    ('masc', run_masc, "26. MA Scalper Coinrule (long-only)", TFS, 'sl2 tp8', [('sl5 tp15', dict(sl=0.05, tp=0.15))]),
    ('bts', run_bts, "27. BEST Trailing Stop", TFS, 'tr3 ambos', [(f'tr{t:.0%} {s}', dict(trl=t, short_ok=s == 'ambos')) for t in (0.03, 0.08) for s in ('ambos', 'long')]),
    ('grov', run_grov, "28. Grover Llorens Activator", TFS, '480 m14 ambos', [(f'{a} m{m:g} {s}', dict(ln=a, mult=m, short_ok=s == 'ambos')) for a, m in ((480, 14.0), (100, 5.0)) for s in ('ambos', 'long')]),
    ('vwbo', run_vwbo, "29. VWAP Breakout", ITF, 'tp2 ambos', [(f'tp{t:g} {s}', dict(tpm=t, short_ok=s == 'ambos')) for t in (2.0, 4.0) for s in ('ambos', 'long')]),
    ('sec', run_sec, "30. Stoch/EMA Cross", TFS, 'tp8 ambos', [((f'tp{t:.0%}' if t else 'semtp') + f' {s}', dict(tp=t, short_ok=s == 'ambos')) for t in (0.08, 0.0) for s in ('ambos', 'long')]),
    ('era', run_era, "31. EMA Cross + RSI + ADX", TFS, 'sl2 ambos', [(f'sl{x:.0%} {s}', dict(sl=x, short_ok=s == 'ambos')) for x in (0.02, 0.05) for s in ('ambos', 'long')]),
    ('mx', run_mx, "32. Multi-X (long-only)", TFS, 'padrao', []),
    ('tra', run_tra, "33. Trend Reversal Alerts (long-only)", TFS, 'padrao', []),
    ('mcci', run_mcci, "34. MACD + CCI", TFS, 'ambos', []),
    ('uhl', run_uhl, "35. Uhl MA System", TFS, '100 ambos', 'ln'),
    ('ht3', run_ht3, "36. Swing HULL + T3", TFS, '50 sltp ambos', [(f'{a} ' + ('sltp ' if k else 'semsltp ') + s, dict(ln=a, sltp=k, short_ok=s == 'ambos')) for a in (50, 100) for k in (True, False) for s in ('ambos', 'long')]),
    ('opw', run_opw, "37. TASC One Percent A Week (long-only)", TFS, 'dip1 tp1', [('dip2 tp2', dict(dip=0.02, tp=0.02))]),
    ('sta', run_sta, "38. Stoch + ATR", TFS, '34 ambos', 'ln'),
    ('spym', run_spym, "39. SPY Master", TFS, 'ambos', []),
    ('kpl', run_kpl, "40. KPL Swing", TFS, '20 ambos', 'ln'),
    ('gn', run_gn, "41. Gianno Nano", TFS, 'sltp ambos', [(('sltp ' if k else 'semsltp ') + s, dict(sltp=k, short_ok=s == 'ambos')) for k in (True, False) for s in ('ambos', 'long')]),
    ('tlb', run_tlb, "42. Trendline Breakout KedArc", TFS, 'p5 ma ambos', [(f'p{p} ' + ('ma ' if m else 'semma ') + s, dict(pv=p, maf=m, short_ok=s == 'ambos')) for p in (5, 10) for m in (True, False) for s in ('ambos', 'long')]),
    ('fbo', run_fbo, "43. Fractal Breakout", TFS, 'ambos', []),
    ('dbt', run_dbt, "44. Double Bottom/Top Hunter", TFS, '100 ambos', 'ln'),
    ('bas', run_bas, "45. BEST ATR Stop Multiple", TFS, 'atr2 ambos', [(f'atr{a:g} {s}', dict(am=a, short_ok=s == 'ambos')) for a in (2.0, 4.0) for s in ('ambos', 'long')]),
    ('nr7s', run_nr7s, "46. NR7ID (short-only)", TFS, 'sma14', [('semfiltro', dict(maf=False))]),
    ('rtb', run_rtb, "47. Reversal Trading Bot", TFS, 'sl1 tp2 ambos', [(f'sl{a:.0%} tp{b:.0%} {s}', dict(sl=a, tp=b, short_ok=s == 'ambos')) for a, b in ((0.01, 0.02), (0.03, 0.06)) for s in ('ambos', 'long')]),
    ('4ma', run_4ma, "48. Multi-MA (4MA)", TFS, 'wma75 ambos', [(f'wma{b} {s}', dict(base=b, short_ok=s == 'ambos')) for b in (75, 200) for s in ('ambos', 'long')]),
    ('ao', run_ao, "49. Awesome Oscillator", TFS, 'ambos', []),
    ('smp', run_smp, "50. Smart Money Pivot", TFS, 'p20 sl1 tp1.5 ambos', [(f'p{p} sl{a:.0%} tp{b:.1%} {s}', dict(per=p, sl=a, tp=b, short_ok=s == 'ambos')) for p in (20, 5) for a, b in ((0.01, 0.015), (0.0, 0.0)) for s in ('ambos', 'long')]),
]
# combos simples: (nome do parametro) -> (default, alternativo) + ambos/long
ALT = {'lb': (10, 30), 'per': (9, 30), 'thr': (40, 20), 'ln': None}
LN_ALT = {'thma': (40, 100), 'uhl': (100, 30), 'sta': (34, 14), 'kpl': (20, 50), 'dbt': (100, 30)}


def combos(est, spec):
    if isinstance(spec, list):
        if not spec and est not in ('stma', 'rsim', 'mx', 'tra'):
            return [(s, dict(short_ok=s == 'ambos')) for s in ('ambos', 'long')]
        return spec
    a, b = LN_ALT[est] if spec == 'ln' else ALT[spec]
    return [(f'{v} {s}', {spec: v, 'short_ok': s == 'ambos'}) for v in (a, b) for s in ('ambos', 'long')]


def main(nomes, only=None):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        for est, fn, label, tfs, dcfg, spec in SPECS:
            if only and est not in only: continue
            print(f"\n### {label}", flush=True)
            for tf in tfs:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=dcfg)
                for cfg, kw in combos(est, spec):
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote25')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
