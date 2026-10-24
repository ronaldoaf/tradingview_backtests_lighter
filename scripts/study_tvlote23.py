"""Lote 23 do TradingView (2026-10-23): 20 estrategias nos 5 ativos (ver docs/LOTE23_TV.md).

Ignoradas na ordem da lista: renko intraday (j0iaMxsl, velas Renko via security = irreal), Turtle System
(cOv24513, piramidacao de 5 unidades com L1/L2 e trade fantasma), Rocket Grid (lm2BJL4V, grid), Two Take Profit
(OZnjwvZv, exemplo de 2 alvos em ticks), Simple and Profitable Scalping (x4za4NFZ, 394 linhas com filtro de
outro tempo), TradersAI UTBot (QDxGi5Ux, o mesmo UT Bot do lote 13), Custom Screener (QKgb0Fud, screener),
Dual MA Ribbons (KpbbCOzp, 599 linhas), Catch the Big Fish (ZkyK1BVD, sem ordens), Follow Line (NCdNYR6I, a
mesma do lote 20), 8JML9Cqd (security Pine v2 = olha o futuro), Renko Emulator (CmZUAjHp, Renko via security),
Zendog DCA (9NXf1Bqb, bot de DCA), Divergence IQ (hgcTVYeX, 1.090 linhas), futPZepe (404), Vegas Tunnel
(Grfdbh8A, 4 entradas piramidadas), 6w9Jchj6 (622 linhas) e 4All V3 (SMQcpefL, piramidacao de 5 scalps).

 1. Twin Range Filter Algo v3 (ZsiaNicR)         11. Triple EMA Trend ADX/ATR (vzXlqRCT)
 2. BBTrend w SuperTrend decision (7C1kIEOn)      12. MA 10/20 Crossover (2cbpO8lO)
 3. 3 EMA + RSI with Trail Stop (mgD7xBuw)        13. Crypto ZigZag RSI 15min (LhpfQMtP)
 4. Higher High Lower Low (JWsBrWBu)              14. Combo 123 Reversal & SMI (NudssmJx)
 5. NR7 + Inside Day long-only (Dln4aFaM)         15. Buying Dip TP/SL racer8 (AHxkEMXm)
 6. Maximized Scalping On Trend Coinrule (XAiEh7nb) 16. Super trend V (7g8MF7f7)
 7. UL QQE Cross v1.1 (nkka4EfU)                  17. RSI Strategy PrimeAutomation (RiQzLLoh)
 8. DEMA ATR PrimeAutomation (rqRd3f62)           18. Trend Trader with MACD (dUNRiEBG)
 9. MA Bollinger Bands + RSI (2MMNHl97)           19. EVWMA VWAP Cross QuantNomad (QPIGo8hs)
10. TradeIQ Crazy Scalping Kaspricci (R7OSA2ar)   20. VWAP Momentum Pullback JS-TechTrading (uhdaobby)

uso: python study_tvlote23.py xau us100 wti btc eth
"""
import os, sys, itertools
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
from study_tvlote20 import sh, Z, rma, tr_, _st
from study_tvlote21 import G
from study_tvlote22 import macd

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
full = lambda c, v: np.full(len(c), float(v))


def bsince(x):
    """ta.barssince (NaN antes da primeira ocorrencia)."""
    x = np.asarray(x, bool); idx = np.where(x, np.arange(len(x)), -1)
    last = np.maximum.accumulate(idx).astype(float); last[last < 0] = NAN
    return np.arange(len(x)) - last


def vwap_d(df):
    """ta.vwap ancorado no dia (UTC) com hlc3."""
    h, l, c = (df[k].to_numpy(float) for k in ('high', 'low', 'close')); v = df.volume.to_numpy(float)
    g = df.index.normalize()
    pv = pd.Series((h + l + c) / 3 * v).groupby(g).cumsum().to_numpy(); vv = pd.Series(v).groupby(g).cumsum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(vv > 0, pv / vv, c)


@njit(cache=True)
def _trl_sim(o, h, l, L, S, SL0, TP0, TRL, TRS, rev):
    """Ordem a mercado na abertura seguinte ao sinal; stop inicial SL0 e alvo TP0 (absolutos, da barra do sinal)
    e trailing que so anda a favor: max(stop, TRL[i]) no long (min no short), atualizado no fechamento e ativo
    na barra seguinte (inclusive a da entrada). Stop antes do alvo. rev: sinal contrario inverte; senao ignora
    sinais com posicao aberta."""
    n = len(o); pos = 0; pend = 0; i0 = 0; pin = 0.0; st = np.nan; tg = np.nan; k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    for j in range(1, n):
        i = j - 1
        if pend != 0:
            if pos != 0:
                EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = pin; PO[k] = o[j]; k += 1
            pos = pend; i0 = j; pin = o[j]; st = SL0[i]; tg = TP0[i]; pend = 0
            if pos == 1 and TRL[i] == TRL[i]: st = TRL[i] if st != st else max(st, TRL[i])
            if pos == -1 and TRS[i] == TRS[i]: st = TRS[i] if st != st else min(st, TRS[i])
        if pos == 1:
            if st == st and l[j] <= st:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], st); k += 1; pos = 0
            elif tg == tg and h[j] >= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = max(o[j], tg); k += 1; pos = 0
        elif pos == -1:
            if st == st and h[j] >= st:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], st); k += 1; pos = 0
            elif tg == tg and l[j] <= tg:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = min(o[j], tg); k += 1; pos = 0
        if pos == 1 and TRL[j] == TRL[j]: st = TRL[j] if st != st else max(st, TRL[j])
        if pos == -1 and TRS[j] == TRS[j]: st = TRS[j] if st != st else min(st, TRS[j])
        if L[j] and pos != 1 and (rev or pos == 0): pend = 1
        elif S[j] and pos != -1 and (rev or pos == 0): pend = -1
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_trl(name, df, tag, rows, verbose, extra, L, S, SL0=None, TP0=None, TRL=None, TRS=None, rev=True,
            long_ok=True, short_ok=True):
    o, h, l, c = ohlc(df); na = full(c, NAN)
    f = lambda x: na if x is None else np.asarray(x, float)
    r = _trl_sim(o, h, l, L & long_ok, S & short_ok, f(SL0), f(TP0), f(TRL), f(TRS), rev)
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 1. Twin Range Filter
def smoothrng(x, t, m):
    return ema(ema(np.abs(np.diff(x, prepend=x[0])), t), t * 2 - 1) * m


@njit(cache=True)
def _rngfilt(x, r):
    n = len(x); f = np.empty(n); p = 0.0
    for i in range(n):
        if x[i] > p: v = p if x[i] - r[i] < p else x[i] - r[i]
        else: v = p if x[i] + r[i] > p else x[i] + r[i]
        f[i] = v; p = v
    return f


def run_twin(name, df, mm, tag, rows=None, verbose=True, atrf=True, tm=17, sltp=True, long_ok=True, short_ok=True, **extra):
    """Range filter com a media de duas faixas (27 x 1,6 e 55 x 2); virada de condicao compra/vende, com SMA32
    do TR < RMA64 do TR. Stop low - 0,8 x (close - minima de 10), alvo close + 5 ATR10 (ticks ignorados); fecha
    17 barras depois do sinal; inverte."""
    o, h, l, c = ohlc(df)
    sm = (smoothrng(c, 27, 1.6) + smoothrng(c, 55, 2.0)) / 2
    f = _rngfilt(c, sm); fu, fd = f > sh(f), f < sh(f)
    up = np.zeros(len(c)); dw = np.zeros(len(c))
    for i in range(1, len(c)):
        up[i] = up[i - 1] + 1 if fu[i] else (0 if fd[i] else up[i - 1])
        dw[i] = dw[i - 1] + 1 if fd[i] else (0 if fu[i] else dw[i - 1])
    lc = (c > f) & (up > 0); sc = (c < f) & (dw > 0)
    ci = pd.Series(np.where(lc, 1.0, np.where(sc, -1.0, NAN))).ffill().fillna(0).to_numpy()
    pci = sh(ci)
    tr = tr_(h, l, c); vok = (T.sma(tr, 32) < rma(tr, 64)) if atrf else np.ones(len(c), bool)
    L = lc & (pci == -1) & vok; S = sc & (pci == 1) & vok
    a = T.atr_rma(h, l, c, 10)
    kw = dict(SLL=l - (c - roll(l, 10).min().to_numpy()) * 0.8, TPL=c + 5 * a,
              SLS=h + np.abs(c - roll(h, 10).min().to_numpy()) * 0.8, TPS=c - 5 * a) if sltp else {}
    XL = (bsince(L) == tm) if tm else None; XS = (bsince(S) == tm) if tm else None
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. BBTrend + SuperTrend
def run_bbst(name, df, mm, tag, rows=None, verbose=True, fac=7.0, long_ok=True, short_ok=False, **extra):
    """BBTrend = (|inferior BB20 - inferior BB50| - |superior BB20 - superior BB50|) / media20 x 100; SuperTrend
    (10, 7) sobre velas sinteticas do BBTrend (abertura = valor anterior). Comprado com a tendencia de alta,
    sai na virada (padrao so long)."""
    o, h, l, c = ohlc(df)
    def bb(n):
        m = T.sma(c, n); d = 2 * roll(c, n).std(ddof=0).to_numpy(); return m, m + d, m - d
    m1, u1, l1 = bb(20); m2, u2, l2 = bb(50)
    s = np.nan_to_num((np.abs(l1 - l2) - np.abs(u1 - u2)) / m1 * 100)
    so = np.concatenate([[s[0]], s[:-1]]); sh_, sl_ = np.fmax(so, s), np.fmin(so, s)
    t = _st((sh_ + sl_) / 2, s, T.atr_rma(sh_, sl_, s, 10), fac)[0]
    L, S = t == 1, t == -1
    r = gsim(df, mm, L, S, S, L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. 3 EMA + RSI
def run_e3r(name, df, mm, tag, rows=None, verbose=True, sl=0.05, xb=24, long_ok=True, short_ok=False, **extra):
    """EMA10 cruza acima da EMA20 com EMA10 > EMA100 e vela de alta compra; sai com RSI14 > 70, ou depois de 24
    barras se estiver no lucro (fechamento); stop fixo de 5%. O trailing de 50/10 pontos foi omitido (ticks)."""
    o, h, l, c = ohlc(df)
    a, b, cc = ema(c, 10), ema(c, 20), ema(c, 100); r_ = T.rsi_wilder(c, 14)
    L = T.xover(a, b) & (a > cc) & (c > o); S = T.xunder(a, b) & (a < cc) & (c < o)
    n = len(c); XL = np.zeros(n, bool); XS = np.zeros(n, bool); pos = 0; ent = 0.0; nb = 0
    for i in range(n):
        if pos == 1:
            nb += 1; XL[i] = r_[i] > 70 or (xb and nb >= xb and c[i] > ent)
            if XL[i] or (S[i] and short_ok): pos = 0
        elif pos == -1:
            nb += 1; XS[i] = r_[i] < 30 or (xb and nb >= xb and c[i] < ent)
            if XS[i] or (L[i] and long_ok): pos = 0
        if pos == 0:
            if L[i] and long_ok: pos, ent, nb = 1, c[i], 0
            elif S[i] and short_ok: pos, ent, nb = -1, c[i], 0
    r = gsim(df, mm, L, S, XL, XS, slp=sl, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Higher High Lower Low
def run_hl41(name, df, mm, tag, rows=None, verbose=True, lb=41, long_ok=True, short_ok=True, **extra):
    """Close acima da maxima de 41 barras anterior, com essa maxima acima da maxima de 10 da barra anterior
    (topo antigo rompido): compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df)
    H, Lw = sh(roll(h, lb).max().to_numpy()), sh(roll(l, lb).min().to_numpy())
    hg, lg = sh(roll(h, 10).max().to_numpy()), sh(roll(l, 10).min().to_numpy())
    r = G(df, mm, (c > H) & (H > hg), (c < Lw) & (Lw < lg), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. NR7 + Inside Day
def run_nr7(name, df, mm, tag, rows=None, verbose=True, maf=True, **extra):
    """Long-only: menor range de 7 barras, inside bar e vela de alta, com SMA14 subindo; sai na proxima vela de alta."""
    o, h, l, c = ohlc(df); rg = h - l
    nr = np.ones(len(c), bool)
    for k in range(1, 7):
        nr &= rg < sh(rg, k)
    m = T.sma(c, 14)
    L = nr & (h < sh(h)) & (l > sh(l)) & (c > o) & ((m > sh(m)) if maf else True)
    r = gsim(df, mm, L, Z(L), (c > o) & ~L, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Coinrule scalping on trend
def run_coin(name, df, mm, tag, rows=None, verbose=True, tp=70, sl=30, **extra):
    """Long-only: close cruza abaixo da SMA9 com SMA50 > SMA100 e RSI14 > 50; sai com RSI > 70 ou < 30."""
    o, h, l, c = ohlc(df); r_ = T.rsi_wilder(c, 14)
    L = T.xunder(c, T.sma(c, 9)) & (T.sma(c, 50) > T.sma(c, 100)) & (r_ > 50)
    r = gsim(df, mm, L, Z(L), (r_ > tp) | (r_ < sl), None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. UL QQE Cross
def rising(x, n):
    m = np.full(len(x), -np.inf)
    for k in range(1, n + 1):
        m = np.fmax(m, sh(x, k))
    return x > m


def falling(x, n):
    m = np.full(len(x), np.inf)
    for k in range(1, n + 1):
        m = np.fmin(m, sh(x, k))
    return x < m


def run_qqe(name, df, mm, tag, rows=None, verbose=True, thr=10, dfilt=True, long_ok=True, short_ok=True, **extra):
    """EMA3 do RSI6 acima de 50 + 10 (primeira barra) com EMA20 subindo (3 barras) e close > SMA50 compra; espelho
    vende. Sai quando a direcao da EMA20 muda (subindo/lateral/caindo). Trailing de 100 pontos omitido (ticks)."""
    o, h, l, c = ohlc(df)
    ri = ema(np.nan_to_num(T.rsi_wilder(c, 6), nan=50.0), 3); e20, s50 = ema(c, 20), T.sma(c, 50)
    d = np.where(rising(e20, 3), 1, np.where(falling(e20, 3), -1, 0))
    fl = ((d > 0) & (c > s50)) if dfilt else np.ones(len(c), bool)
    fs = ((d < 0) & (c < s50)) if dfilt else np.ones(len(c), bool)
    bl, bs = (ri > 50 + thr) & fl, (ri < 50 - thr) & fs
    L, S = bl & ~sh(bl).astype(bool), bs & ~sh(bs).astype(bool)
    X = d != sh(d)
    r = gsim(df, mm, L, S, X, X, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. DEMA ATR
@njit(cache=True)
def _dema_atr(d, a):
    n = len(d); out = np.empty(n); p = np.nan
    for i in range(n):
        v = d[i] if p != p else p
        if d[i] - a[i] > v: v = d[i] - a[i]
        if d[i] + a[i] < v: v = d[i] + a[i]
        out[i] = v; p = v
    return out


def run_dema(name, df, mm, tag, rows=None, verbose=True, tp=0.0, long_ok=True, short_ok=True, **extra):
    """Linha = DEMA75 presa na faixa +- 1,2 ATR20; cruzar a propria linha de 2 barras atras para cima compra e
    para baixo vende (inverte). Os 3 alvos parciais (3/6/9 ATR200, 30/30/40%) viraram um alvo unico opcional
    em tp x ATR200. Sem alvo, como escrito, fica sempre posicionado."""
    o, h, l, c = ohlc(df)
    e = ema(c, 75); dm = 2 * e - ema(e, 75)
    v = _dema_atr(dm, np.nan_to_num(T.atr_rma(h, l, c, 20)) * 1.2)
    L, S = T.xover(v, sh(v, 2)), T.xunder(v, sh(v, 2))
    a = T.atr_rma(h, l, c, 200)
    kw = dict(TPL=c + tp * a, TPS=c - tp * a) if tp else {}
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. MA BB + RSI
def run_mabb(name, df, mm, tag, rows=None, verbose=True, am=9.0, volf=True, long_ok=True, short_ok=True, **extra):
    """BB(SMA200, 2 desvios de 200): abre abaixo da inferior e fecha acima, com RSI6 cruzando 50 nas ultimas 10
    barras, compra (espelho vende); sinais alternados; sem volatilidade extrema (largura vs SMA2000 +- 50%).
    Trailing = minima de 2 barras - 9 ATR14 (so sobe); o sinal contrario inverte."""
    o, h, l, c = ohlc(df)
    m = T.sma(c, 200); d = 2 * roll(c, 200).std().to_numpy(); up, lo = m + d, m - d
    r_ = T.rsi_wilder(c, 6)
    rb = roll(T.xover(r_, full(c, 50)).astype(float), 11).max().to_numpy() > 0
    rs = roll(T.xunder(r_, full(c, 50)).astype(float), 11).max().to_numpy() > 0
    w = up - lo; base = T.sma(w, 2000)
    ok = ~((w > base * 1.5) | (w < base * 0.5)) if volf else np.ones(len(c), bool)
    vl = (o < lo) & (c > lo) & rb & ok; vs = (o > up) & (c < up) & rs & ok
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); last = 0
    for i in range(n):
        if vl[i]:
            if last != 1: L[i] = True
            last = 1
        if vs[i]:
            if last != -1: S[i] = True
            last = -1
    a = T.atr_rma(h, l, c, 14) * am
    return run_trl(name, df, tag, rows, verbose, extra, L, S, TRL=roll(l, 2).min().to_numpy() - a,
                   TRS=roll(h, 2).max().to_numpy() + a, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 10. Crazy Scalping (TradeIQ)
def ama_filter(x, n=50, al=1.0, be=0.5):
    xs = np.arange(n) / (n - 1); b = np.sin(2 * np.pi * xs ** al) * (1 - xs ** be)
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), n)[:, ::-1]
    out = np.full(len(x), NAN); out[n - 1:] = W @ b / b.sum()
    return out


def vwhen(cond, x, k):
    """ta.valuewhen(cond, x, k)."""
    s = pd.Series(np.where(cond, x, NAN)).dropna()
    out = pd.Series(NAN, index=range(len(x)))
    out[s.index] = s.shift(k).to_numpy()
    return out.ffill().to_numpy()


def run_crazy(name, df, mm, tag, rows=None, verbose=True, sll=10, long_ok=True, short_ok=True, **extra):
    """Divergencia do TMO (momentum da SMA da SMA7) num pico/vale, com o filtro AMA(50) em modo de alta (high
    cruzou a banda de cima) para comprar; entra quando o corpo das velas filtradas cresce 3 vezes seguidas e o
    sinal ainda vale. Sai na divergencia contraria ou na virada do AMA; stop na minima de 10 barras."""
    o, h, l, c = ohlc(df)
    osc = T.sma(T.sma(c, 7), 7); osc = osc - sh(osc, 7)
    up_, dn_ = roll(c, 7).max().to_numpy(), roll(c, 7).min().to_numpy()
    ch = osc - sh(osc); ph, pl = T.xunder(ch, full(c, 0)), T.xover(ch, full(c, 0))
    bear = (osc > 0) & ph & (vwhen(ph, osc, 0) < vwhen(ph, osc, 1)) & (vwhen(ph, up_, 0) > vwhen(ph, up_, 1))
    bull = (osc < 0) & pl & (vwhen(pl, osc, 0) > vwhen(pl, osc, 1)) & (vwhen(pl, dn_, 0) < vwhen(pl, dn_, 1))
    f = ama_filter(c); dev = T.sma(np.abs(c - f), 50) * 2; U, Lo = f + dev, f - dev
    cu = (T.xover(h, U) | T.xunder(h, U)); cl = (T.xover(l, Lo) | T.xunder(l, Lo))
    os_ = pd.Series(np.where(cu, 1.0, np.where(cl, 0.0, NAN))).ffill().fillna(0).to_numpy()
    fc = ama_filter(c); body = np.abs((sh(fc) + sh(fc, 2)) / 2 - fc)
    inc = (sh(body, 2) < sh(body)) & (sh(body) < body); trig = inc & ~np.nan_to_num(sh(inc.astype(float))).astype(bool)
    lec, sec_ = (os_ == 1) & bull, (os_ == 0) & bear
    bl, bs = bsince(lec), bsince(sec_)
    L = trig & (bl < bsince(os_ == 0)) & (bl < bsince(bear))
    S = trig & (bs < bsince(os_ == 1)) & (bs < bsince(bull))
    r = gsim(df, mm, L, S & ~L, bear | (os_ == 0), bull | (os_ == 1), SLL=roll(l, sll).min().to_numpy(),
             SLS=roll(h, sll).max().to_numpy(), rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Triple EMA Trend
def run_tema(name, df, mm, tag, rows=None, verbose=True, adx_t=43, long_ok=True, short_ok=False, **extra):
    """ADX14 > 43, EMA30 > EMA46 > EMA80 e close > EMA30 compra; stop 1,8 ATR14 e alvo 3,3 ATR14. O script
    controla um trade 'virtual' proprio: com shorts desligados, um sinal de venda ainda bloqueia compras ate o
    alvo/stop virtual (reproduzido)."""
    o, h, l, c = ohlc(df)
    e1, e2, e3 = ema(c, 30), ema(c, 46), ema(c, 80); adx = dmi(h, l, c, 14)[2]; a = T.atr_rma(h, l, c, 14)
    lc = (adx > adx_t) & (e1 > e2) & (e2 > e3) & (c > e1); scn = (adx > adx_t) & (e1 < e2) & (e2 < e3) & (c < e1)
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); st = 0; sl = tp = 0.0
    for i in range(1, n):
        if st == 0:
            if lc[i]: st, sl, tp = 1, c[i] - 1.8 * a[i], c[i] + 3.3 * a[i]; L[i] = True
            elif scn[i]: st, sl, tp = -1, c[i] + 1.8 * a[i], c[i] - 3.3 * a[i]; S[i] = True
        elif st == 1:
            if (h[i] > tp and h[i - 1] <= tp) or (l[i] < sl and l[i - 1] >= sl): st = 0
        else:
            if (l[i] < tp and l[i - 1] >= tp) or (h[i] > sl and h[i - 1] <= sl): st = 0
    r = gsim(df, mm, L, S, SLL=c - 1.8 * a, TPL=c + 3.3 * a, SLS=c + 1.8 * a, TPS=c - 3.3 * a, rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. MA 10/20
def run_ma1020(name, df, mm, tag, rows=None, verbose=True, f=10, s=20, long_ok=True, short_ok=True, **extra):
    """SMA10 cruza a SMA20: inverte."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, f), T.sma(c, s)
    r = G(df, mm, T.xover(a, b), T.xunder(a, b), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. ZigZag RSI
def run_zzrsi(name, df, mm, tag, rows=None, verbose=True, rl=5, os_=25, ob=75, zz=1.0, **extra):
    """Long-only: guarda o close do ultimo cruzamento do RSI5 acima de 25 (r1) e abaixo de 75 (s1); um zigzag de
    1% sobre esses niveis vira para cima compra e para baixo vende."""
    o, h, l, c = ohlc(df); r_ = T.rsi_wilder(c, rl)
    lg, sg = T.xover(r_, full(c, os_)), T.xunder(r_, full(c, ob))
    r1 = pd.Series(np.where(lg, c, NAN)).ffill().fillna(0).to_numpy()
    s1 = pd.Series(np.where(sg, c, NAN)).ffill().fillna(0).to_numpy()
    n = len(c); tr = np.ones(n); t = 1; HH = r1[0]; LL = s1[0]; P = zz / 100
    for i in range(n):
        if t > 0:
            if r1[i] >= HH: HH = r1[i]
            elif s1[i] < HH * (1 - P): t = -1; LL = s1[i]
        else:
            if s1[i] <= LL: LL = s1[i]
            elif r1[i] > LL * (1 + P): t = 1; HH = s1[i]
        tr[i] = t
    pt = sh(tr)
    r = gsim(df, mm, (tr > 0) & (pt < 0), Z(c), (tr < 0) & (pt > 0), None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Combo 123 Reversal + SMI
def run_combo(name, df, mm, tag, rows=None, verbose=True, smil=18, long_ok=True, short_ok=True, **extra):
    """123 Reversal (estocastico 14 da barra anterior) e Smart Money Index (diario anterior) concordando: compra
    ou vende; discordando, zera."""
    o, h, l, c = ohlc(df)
    vf = stoch(sh(c), sh(h), sh(l), 14); vs = T.sma(vf, 3)
    c1, c2, c3 = sh(c), sh(c, 2), sh(c, 3)
    p1 = np.where((c3 < c2) & (c1 > c2) & (vf < vs) & (vf > 50), 1.0,
                  np.where((c3 > c2) & (c1 < c2) & (vf > vs) & (vf < 50), -1.0, NAN))
    p1 = pd.Series(p1).ffill().fillna(0).to_numpy()
    dd = df.groupby(df.index.normalize()).agg(o=('open', 'first'), c=('close', 'last'))
    prev = (dd.o - dd.c).shift(1).reindex(df.index.normalize()).to_numpy()
    nres = 1 + np.cumsum(np.nan_to_num(-(o - c) + prev))
    xs = T.sma(nres, smil)
    p2 = pd.Series(np.where(xs > nres, 1.0, np.where(xs < nres, -1.0, NAN))).ffill().fillna(0).to_numpy()
    p = np.where((p1 == 1) & (p2 == 1), 1, np.where((p1 == -1) & (p2 == -1), -1, 0))
    r = gsim(df, mm, p == 1, p == -1, p != 1, p != -1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Buying Dip
def run_dip(name, df, mm, tag, rows=None, verbose=True, nd=7, tpm=2.0, slm=2.0, **extra):
    """Long-only: close abaixo da minima de 7 barras anterior compra; alvo e stop de 2 x SMA10 do TR (anterior)."""
    o, h, l, c = ohlc(df)
    a = sh(T.sma(tr_(h, l, c), 10))
    L = c < sh(roll(l, nd).min().to_numpy())
    r = gsim(df, mm, L, Z(L), SLL=c - slm * a, TPL=c + tpm * a, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Super trend V
def run_stv(name, df, mm, tag, rows=None, verbose=True, mult=1.0, long_ok=True, short_ok=False, **extra):
    """VPT 'sombra' (volume x corpo, normalizado pelo desvio do range) suavizado por EMA de 720/TF x 7 barras;
    SuperTrend 10 x 1 em volta dele. Close cruza acima da linha com close > EMA da abertura compra; abaixo
    vende (padrao so long: fecha)."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    tfm = (df.index[1] - df.index[0]).total_seconds() / 60
    ln = int(720 / tfm * 7) if tfm < 1440 else 7
    hl = (h - l) * 100; oc = (c - o) * 100
    with np.errstate(divide='ignore', invalid='ignore'):
        sv = np.where(hl > 0, oc * v / hl, 0.0)
    vv = sv + np.cumsum(sv); sm = T.sma(vv, 14)
    with np.errstate(divide='ignore', invalid='ignore'):
        shd = (vv - sm) / roll(vv - sm, 28).std().to_numpy() * roll(h - l, 28).std().to_numpy()
    out = np.where(shd > 0, h + shd, l + shd)
    out = pd.Series(out).ffill().bfill().to_numpy()
    vpt, oe = ema(out, ln), ema(o, ln); a = T.atr_rma(h, l, c, 10)
    n = len(c); ul, dl = vpt - mult * a, vpt + mult * a
    ut = np.zeros(n); dt = np.zeros(n); t = np.ones(n)
    for i in range(1, n):
        ut[i] = max(ul[i], ut[i - 1]) if c[i - 1] > ut[i - 1] else ul[i]
        dt[i] = min(dl[i], dt[i - 1]) if c[i - 1] < dt[i - 1] else dl[i]
        t[i] = 1 if c[i] > dt[i - 1] else (-1 if c[i] < ut[i - 1] else t[i - 1])
    stl = np.where(t == 1, ut, dt)
    L, S = T.xover(c, stl) & (c > oe), T.xunder(c, stl) & (c < oe)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. RSI PrimeAutomation
def run_rsipa(name, df, mm, tag, rows=None, verbose=True, sm=4.0, tpm=7.0, long_ok=True, short_ok=True, **extra):
    """RSI40 cruza acima de 60 compra, abaixo de 35 vende (so sem posicao); stop inicial 4 ATR200 que segue a
    minima - 4 ATR200 (so sobe) e alvo de 7 ATR200."""
    o, h, l, c = ohlc(df); r_ = T.rsi_wilder(c, 40); a = T.atr_rma(h, l, c, 200)
    L, S = T.xover(r_, full(c, 60)), T.xunder(r_, full(c, 35))
    tp = dict(TP0=np.where(L, c + tpm * a, c - tpm * a)) if tpm else {}
    return run_trl(name, df, tag, rows, verbose, extra, L, S, SL0=np.where(L, c - sm * a, c + sm * a),
                   TRL=l - sm * a, TRS=h + sm * a, rev=False, long_ok=long_ok, short_ok=short_ok, **tp)


# ------------------------------------------------------------------ 18. Trend Trader + MACD
def run_ttm(name, df, mm, tag, rows=None, verbose=True, mult=3.0, mc=True, long_ok=True, short_ok=True, **extra):
    """Linha = maxima de 21 anterior - 3 x WMA21 do TR (ou minima + 3 x, conforme o lado); close acima compra
    (com histograma do MACD > 0), abaixo vende; inverte."""
    o, h, l, c = ohlc(df)
    at = T.wma(tr_(h, l, c), 21); hi = sh(roll(h, 21).max().to_numpy()) - sh(at) * mult
    lo = sh(roll(l, 21).min().to_numpy()) + sh(at) * mult
    rt = pd.Series(np.where((c > hi) & (c > lo), hi, np.where((c < lo) & (c < hi), lo, NAN))).ffill().fillna(0).to_numpy()
    p = pd.Series(np.where(c > rt, 1.0, np.where(c < rt, -1.0, NAN))).ffill().fillna(0).to_numpy()
    m, s = macd(c)
    r = G(df, mm, (p == 1) & ((m - s > 0) if mc else True), p == -1, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. EVWMA x VWAP
@njit(cache=True)
def _evwma(c, v, vp):
    n = len(c); e = np.empty(n); p = np.nan
    for i in range(n):
        pv = c[i] if p != p else p
        e[i] = ((vp[i] - v[i]) * pv + v[i] * c[i]) / vp[i] if vp[i] > 0 else pv
        p = e[i]
    return e


def run_evw(name, df, mm, tag, rows=None, verbose=True, ln=30, long_ok=True, short_ok=True, **extra):
    """VWAP diaria cruza a EVWMA(30) (media ponderada pelo volume da janela): inverte."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    e = _evwma(c, v, roll(v, ln).sum().to_numpy()); vw = vwap_d(df)
    r = G(df, mm, T.xover(vw, e), T.xunder(vw, e), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. VWAP Momentum Pullback
def run_vwpb(name, df, mm, tag, rows=None, verbose=True, sl=0.03, tp=0.07, os_=40, **extra):
    """Long-only: RSI14 <= 40 nas ultimas 10 barras e SMA7 cruza acima da VWAP diaria; stop 3% e alvo 7% (o
    fechamento no sinal contrario fica dentro do bloco de compra e nunca roda)."""
    o, h, l, c = ohlc(df); r_ = T.rsi_wilder(c, 14)
    L = (bsince(r_ <= os_) <= 10) & T.xover(T.sma(c, 7), vwap_d(df))
    r = gsim(df, mm, L, Z(L), slp=sl, tpp=tp, rev=False)
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

        grid('twin', run_twin, "1. Twin Range Filter", TFS, 'atr t17 sltp ambos',
             [(('atr ' if a else 'sematr ') + f't{tm} ' + ('sltp ' if st else 'semsltp ') + s, dict(atrf=a, tm=tm, sltp=st, **sk(s)))
              for a, tm, st, s in itertools.product((True, False), (17, 0), (True, False), side2)])
        grid('bbst', run_bbst, "2. BBTrend + SuperTrend", TFS, 'f7 long',
             [(f'f{f:g} {s}', dict(fac=f, **sk(s))) for f, s in itertools.product((7.0, 3.0), side2)])
        grid('e3r', run_e3r, "3. 3 EMA + RSI", TFS, 'sl5 x24 long',
             [(f'sl{sl:.0%} x{xb} {s}', dict(sl=sl, xb=xb, **sk(s))) for sl, xb, s in itertools.product((0.05, 0.0), (24, 0), side2)])
        grid('hl41', run_hl41, "4. Higher High Lower Low", TFS, '41 ambos',
             [(f'{lb} {s}', dict(lb=lb, **sk(s))) for lb, s in itertools.product((41, 100), side2)])
        grid('nr7', run_nr7, "5. NR7 + Inside Day (long-only)", TFS, 'sma14', [('sma14', dict(maf=True)), ('semfiltro', dict(maf=False))])
        grid('coin', run_coin, "6. Coinrule Scalping On Trend (long-only)", TFS, '70/30',
             [(f'{a}/{b}', dict(tp=a, sl=b)) for a, b in ((70, 30), (80, 20))])
        grid('qqe', run_qqe, "7. UL QQE Cross", TFS, 'thr10 filtro ambos',
             [(f'thr{t} ' + ('filtro ' if d else 'semfiltro ') + s, dict(thr=t, dfilt=d, **sk(s)))
              for t, d, s in itertools.product((10, 5), (True, False), side2)])
        grid('dema', run_dema, "8. DEMA ATR", TFS, 'semtp ambos',
             [((f'tp{tp:g}' if tp else 'semtp') + f' {s}', dict(tp=tp, **sk(s))) for tp, s in itertools.product((0.0, 6.0), side2)])
        grid('mabb', run_mabb, "9. MA BB + RSI", TFS, 'a9 vol ambos',
             [(f'a{a:g} ' + ('vol ' if v else 'semvol ') + s, dict(am=a, volf=v, **sk(s)))
              for a, v, s in itertools.product((9.0, 3.0), (True, False), side2)])
        grid('crazy', run_crazy, "10. Crazy Scalping (TMO + AMA)", TFS, 'sl10 ambos',
             [(f'sl{x} {s}', dict(sll=x, **sk(s))) for x, s in itertools.product((10, 30), side2)])
        grid('tema', run_tema, "11. Triple EMA Trend", TFS, 'adx43 long',
             [(f'adx{a} {s}', dict(adx_t=a, **sk(s))) for a, s in itertools.product((43, 25), side2)])
        grid('ma1020', run_ma1020, "12. MA 10/20 Crossover", TFS, '10/20 ambos',
             [(f'{f}/{s_} {s}', dict(f=f, s=s_, **sk(s))) for (f, s_), s in itertools.product(((10, 20), (20, 50), (50, 200)), side2)])
        grid('zzrsi', run_zzrsi, "13. ZigZag RSI (long-only)", TFS, 'r5 25/75 zz1',
             [(f'r{rl} {a}/{b} zz{z:g}', dict(rl=rl, os_=a, ob=b, zz=z)) for (rl, a, b), z in itertools.product(((5, 25, 75), (14, 30, 70)), (1.0, 3.0))])
        grid('combo', run_combo, "14. Combo 123 Reversal + SMI", TFS, 'smi18 ambos',
             [(f'smi{x} {s}', dict(smil=x, **sk(s))) for x, s in itertools.product((18, 50), side2)])
        grid('dip', run_dip, "15. Buying Dip (long-only)", TFS, 'd7 tp2 sl2',
             [(f'd{d} tp{a:g} sl{b:g}', dict(nd=d, tpm=a, slm=b)) for d, (a, b) in itertools.product((7, 20), ((2, 2), (4, 2), (1, 1)))])
        grid('stv', run_stv, "16. Super trend V", TFS, 'm1 long',
             [(f'm{m:g} {s}', dict(mult=m, **sk(s))) for m, s in itertools.product((1.0, 3.0), side2)])
        grid('rsipa', run_rsipa, "17. RSI PrimeAutomation", TFS, 's4 tp7 ambos',
             [(f's{a:g} tp{b:g} {s}', dict(sm=a, tpm=b, **sk(s))) for (a, b), s in itertools.product(((4, 7), (4, 0), (2, 4)), side2)])
        grid('ttm', run_ttm, "18. Trend Trader + MACD", TFS, 'm3 macd ambos',
             [(f'm{m:g} ' + ('macd ' if mc else 'semmacd ') + s, dict(mult=m, mc=mc, **sk(s)))
              for m, mc, s in itertools.product((3.0, 1.5), (True, False), side2)])
        grid('evw', run_evw, "19. EVWMA x VWAP", TFS, '30 ambos',
             [(f'{ln} {s}', dict(ln=ln, **sk(s))) for ln, s in itertools.product((30, 100), side2)])
        grid('vwpb', run_vwpb, "20. VWAP Momentum Pullback (long-only)", TFS, 'sl3 tp7 rsi40',
             [(f'sl{sl:.0%} tp{tp:.0%} rsi{r}', dict(sl=sl, tp=tp, os_=r)) for (sl, tp), r in itertools.product(((0.03, 0.07), (0.05, 0.15)), (40, 30))])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote23')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
