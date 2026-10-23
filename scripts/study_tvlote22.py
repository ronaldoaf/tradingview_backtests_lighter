"""Lote 22 do TradingView (2026-10-23): 20 estrategias nos 5 ativos (ver docs/LOTE22_TV.md).

Ignoradas na ordem da lista: Traling SL Target (4jxYYaGU, template de trailing sobre cruzamento de EMAs),
GRID SPOT (LK1zL4D8, grid sem ordens de estrategia), TICK Scalping SPY (yiBwexdm, depende do TICK/SPY),
noro's bands scalper (nWSGZciA, 404), Price Action (2Zg5oABG, entradas comentadas no codigo), Rally Base Drop
SND (dagKHrx4, LuxAlgo, complexo demais), DCA Bot Emulator (vyStpg6g, emulador de DCA), ML SuperTrend
(9Mm3qKME, k-means, complexo demais), SSL Hybrid QQE (fl8CV2N0, 555 linhas com JMA/VAMA etc.), Advanced
Position Management (IsMKlnoJ, template de gestao), FTB (gcu6zUkw, sessao 02-07 do fuso da corretora +
PineConnector), HalfTrend + HullButterfly (lL04fUNr, 427 linhas), MULTIPLE TIME FRAME (gciwtPOi, security
Pine v2 = olha o futuro), BEST Trailing TP (9YaLIh0i, template), MVRV (v3TqVthK, dado on-chain externo),
Session Breakout Scalper (7abDoROC, 670 linhas), Instrument Z 3Commas (1OX9Wu8g, 404) e VXD Cloud
(OKKz3vDv, nuvem + TPs parciais + breakeven, complexo demais).

 1. BB + RSI + ADX scalping (sR1hePBi)        11. Moving Average Band (wwi02rpz)
 2. EMA Crossover hl2 20/60 (sxJejjdy)        12. Renko Strategy V2 (oAlFKwej)
 3. EWO RSI Exhaustion Filter (B7MQqWes)      13. Highest High / Lowest Low channel (1SMJivyk)
 4. Easy MACD + RSI (06gU5i7b)                14. Parabolic SAR on close QuantNomad (gK7skk6m)
 5. TSI CCI Hull (qwN8CGrU)                   15. XAUUSD Scalping V2 AGRESIV (5q4PsY3a)
 6. Real Turtle (67fpKimh)                    16. PMax on RSI w T3 (ZLcmWQtj)
 7. ATR Parabolic SAR QuantNomad (LKfHdoNv)   17. Volatility force trade scalper (FN3ZkHZA)
 8. Ichimoku no offset + RSI (MGSCiuSP)       18. Triple SuperTrend + StochRSI (aCbQTE0W)
 9. Turtle Donchian/ATR (gbxblhGl)            19. Cumulative RSI (nI9Csm8g)
10. Slopes (XBgfW9k9)                         20. Breakout Trend Follower (9uvZIPnH)

uso: python study_tvlote22.py xau us100 wti btc eth
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
from study_tvlote20 import sh, Z, rma, tr_
from study_tvlote21 import G

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)
full = lambda c, v: np.full(len(c), float(v))


@njit(cache=True)
def _stp_sim(o, h, l, LE, SE, LX, SX, KL, KS, long_ok, short_ok):
    """Ordens stop armadas no fechamento de i e ativas na barra i+1: entrada long em LE (short em SE), com fill
    em max(abertura, nivel); saida do long em max(LX, entrada - KL[barra que armou]) (short no espelho). A
    entrada contraria inverte; a saida e checada antes das entradas."""
    n = len(o); pos = 0; i0 = 0; pin = 0.0; k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    for j in range(1, n):
        i = j - 1
        if pos == 1:
            lv = LX[i]; kk = KL[i0 - 1]
            if kk == kk:
                lv = pin - kk if lv != lv else max(lv, pin - kk)
            if lv == lv and l[j] <= lv:
                EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], lv); k += 1; pos = 0
        elif pos == -1:
            lv = SX[i]; kk = KS[i0 - 1]
            if kk == kk:
                lv = pin + kk if lv != lv else min(lv, pin + kk)
            if lv == lv and h[j] >= lv:
                EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], lv); k += 1; pos = 0
        le = LE[i] if long_ok else np.nan; se = SE[i] if short_ok else np.nan
        hl = le == le and h[j] >= le and pos != 1
        hs = se == se and l[j] <= se and pos != -1
        if hl and hs:
            if max(le - o[j], 0.0) <= max(o[j] - se, 0.0): hs = False
            else: hl = False
        if hl or hs:
            fill = max(o[j], le) if hl else min(o[j], se)
            if pos != 0:
                EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = pin; PO[k] = fill; k += 1
            pos = 1 if hl else -1; i0 = j; pin = fill
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_stp(name, df, tag, rows, verbose, extra, LE, SE, LX=None, SX=None, KL=None, KS=None, long_ok=True, short_ok=True):
    o, h, l, c = ohlc(df); na = full(c, NAN)
    r = _stp_sim(o, h, l, LE, SE, na if LX is None else LX, na if SX is None else SX,
                 na if KL is None else KL, na if KS is None else KS, long_ok, short_ok)
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


def mfi(h, l, c, v, n):
    tp = (h + l + c) / 3; mf = tp * v; d = np.diff(tp, prepend=NAN)
    up = roll(np.where(d > 0, mf, 0.0), n).sum().to_numpy(); dn = roll(np.where(d < 0, mf, 0.0), n).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        return 100 - 100 / (1 + up / dn)


def meandev(x, n):
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), n)
    out = np.full(len(x), NAN); out[n - 1:] = np.abs(W - W.mean(1, keepdims=True)).mean(1)
    return out


def macd(c, f=12, s=26, g=9):
    m = ema(c, f) - ema(c, s)
    return m, ema(m, g)


# ------------------------------------------------------------------ 1. BB + RSI + ADX
def run_bbra(name, df, mm, tag, rows=None, verbose=True, sl=0.003, adx_max=32, long_ok=True, short_ok=True, **extra):
    """Long: close < banda superior BB(60,2), RSI20 cruza acima de 35 e ADX14 < 32; short: close > banda superior e
    RSI cruza abaixo de 65. Sai ao cruzar a media de 60, ou TP/SL de 90 ticks (aqui em %, igual dos dois lados)."""
    o, h, l, c = ohlc(df)
    r_ = T.rsi_wilder(c, 20); bas = T.sma(c, 60); up = bas + 2 * roll(c, 60).std(ddof=0).to_numpy()
    adx = dmi(h, l, c, 14)[2]; f = adx < adx_max
    L = (c < up) & T.xover(r_, full(c, 35)) & f
    S = (c > up) & T.xunder(r_, full(c, 65)) & f
    r = G(df, mm, L, S & ~L, T.xunder(c, bas), T.xover(c, bas), slp=sl, tpp=sl, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. EMA Crossover
def run_emax(name, df, mm, tag, rows=None, verbose=True, ln=20, ratio=3, long_ok=True, short_ok=True, **extra):
    """EMA(hl2, 20) cruzando a EMA(hl2, 60): sempre posicionado, inverte no cruzamento."""
    o, h, l, c = ohlc(df); hl2 = (h + l) / 2
    f, s = ema(hl2, ln), ema(hl2, ln * ratio)
    r = G(df, mm, T.xover(f, s), T.xunder(f, s), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. EWO RSI
def run_ewo(name, df, mm, tag, rows=None, verbose=True, vol=True, long_ok=True, short_ok=True, **extra):
    """Compra: RSI14 cruza acima de 40, MFI14 > 30, EWO (SMA5 - SMA34 do hl2) subindo, volume > 0,8 x SMA20 e
    (rompimento da maxima de 10 barras ou zona de exaustao: RSI < 30 desde a ultima compra). Venda: RSI cruza
    abaixo de 60, MFI < 70, EWO caindo e volume ok. Sinais alternados; sempre posicionado (inverte)."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); hl2 = (h + l) / 2
    ew = T.sma(hl2, 5) - T.sma(hl2, 34); r_ = T.rsi_wilder(c, 14); mf = mfi(h, l, c, v, 14)
    vok = v > T.sma(v, 20) * 0.8 if vol else np.ones(len(c), bool)
    brk = c > sh(roll(h, 10).max().to_numpy())
    rb = T.xover(r_, full(c, 40)) & (mf > 30) & (ew > sh(ew)) & vok
    rs = T.xunder(r_, full(c, 60)) & (mf < 70) & (ew < sh(ew)) & vok
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); zone = False; last = 0
    for i in range(n):
        if r_[i] < 30: zone = True
        b = rb[i] and (brk[i] or zone)
        if b: zone = False
        if b and last != 1: L[i] = True; last = 1
        if rs[i] and last != -1: S[i] = True; last = -1
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Easy MACD + RSI
def run_mrsi(name, df, mm, tag, rows=None, verbose=True, rmax=50, sl=0.0, **extra):
    """Long-only: MACD cruza acima do sinal com MACD < 0 e RSI14 < 50; sai quando cruza abaixo com MACD > 0."""
    o, h, l, c = ohlc(df)
    m, s = macd(c); r_ = T.rsi_wilder(c, 14)
    L = T.xover(m, s) & (m < 0) & (r_ < rmax); X = T.xunder(m, s) & (m > 0)
    r = gsim(df, mm, L, Z(L), X, None, slp=sl, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. TSI CCI Hull
def run_tsi(name, df, mm, tag, rows=None, verbose=True, tp=0.005, long_ok=True, short_ok=True, **extra):
    """TSI(50,50) x5 suavizado pela EMA125 subindo (vs 2 barras atras), close acima da Hull suavizada e CCI da
    Hull(26) > 0 e subindo com a Hull subindo: compra (venda no espelho). Sai no sinal contrario ou com lucro de
    0,5% (no Pine checado no fechamento; aqui alvo no M1)."""
    o, h, l, c = ohlc(df)
    pc = np.diff(c, prepend=NAN); pc[0] = 0
    tsi = 100 * ema(ema(pc, 50), 50) / ema(ema(np.abs(pc), 50), 50)
    t1 = ema(tsi * 5, 125); t2 = sh(t1, 2)
    n1 = T.wma(2 * T.wma(c, 13) - T.wma(c, 26), 5)
    with np.errstate(divide='ignore', invalid='ignore'):
        cci = (c - n1) / (0.015 * meandev(c, 26))
    hs = T.wma(2 * T.wma(n1, 13) - T.wma(n1, 26), 5)
    lc = (t1 > t2) & (hs < c) & (cci > 0); scn = (t1 < t2) & (hs > c) & (cci < 0)
    L = lc & (cci > sh(cci)) & (n1 > sh(n1)); S = scn & (cci < sh(cci)) & (n1 < sh(n1))
    r = G(df, mm, L, S, tpp=tp, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. Real Turtle
def run_turtle(name, df, mm, tag, rows=None, verbose=True, ent=20, ext=10, mult=2.0, long_ok=True, short_ok=True, **extra):
    """Stop de compra na maxima de 20 barras e de venda na minima de 20; saida em stop no canal de 10 barras ou
    entrada -/+ 2 x EMA13 do TR (o que estiver mais perto). A entrada contraria inverte."""
    o, h, l, c = ohlc(df)
    et = mult * ema(tr_(h, l, c), 13)
    hh, ll = roll(h, ent).max().to_numpy(), roll(l, ent).min().to_numpy()
    return run_stp(name, df, tag, rows, verbose, extra, hh, ll, roll(l, ext).min().to_numpy(),
                   roll(h, ext).max().to_numpy(), et, et, long_ok, short_ok)


# ------------------------------------------------------------------ 7/14. Parabolic SAR QuantNomad
@njit(cache=True)
def _psar_q(o, h, l, c, atr, start, inc, mx, use_atr):
    """PSAR do QuantNomad com virada no fechamento; use_atr: o passo e af x ATR em vez de af x (ep - psar)."""
    n = len(c); tb = np.zeros(n, np.int64)
    psar = 0.0; af = 0.0; d = 0; ep = 0.0; b = 0
    for i in range(1, n):
        first = i == 1
        l2s = d == 1 and c[i] <= psar; s2l = d == -1 and c[i] >= psar
        chg = first or l2s or s2l
        nd = (1 if c[i - 1] > o[i - 1] else -1) if first else (-1 if l2s else (1 if s2l else d))
        b = -1 if l2s else (1 if s2l else (b + 1 if nd == 1 else (b - 1 if nd == -1 else b)))
        if chg: naf = start
        elif (nd == 1 and h[i] > ep) or (nd == -1 and l[i] < ep): naf = min(mx, af + inc)
        else: naf = af
        nep = (h[i] if nd == 1 else l[i]) if chg else (max(ep, h[i]) if nd == 1 else min(ep, l[i]))
        if first: np_ = l[i - 1] if c[i - 1] > o[i - 1] else h[i - 1]
        elif chg: np_ = ep
        elif use_atr: np_ = psar + naf * atr[i] if nd == 1 else psar - naf * atr[i]
        else: np_ = psar + naf * (nep - psar) if nd == 1 else psar - naf * (psar - nep)
        psar = np_; af = naf; d = nd; ep = nep; tb[i] = b
    return tb


def run_psar(name, df, mm, tag, rows=None, verbose=True, use_atr=True, nb=1, start=0.02, mx=0.2, long_ok=True,
             short_ok=True, **extra):
    """Entra na N-esima barra da tendencia do PSAR (padrao 1); sempre posicionado."""
    o, h, l, c = ohlc(df)
    a = T.atr_rma(h, l, c, 14); a = np.where(np.isnan(a), h - l, a)
    tb = _psar_q(o, h, l, c, a, start, start, mx, use_atr)
    r = G(df, mm, tb == nb, tb == -nb, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


def run_psarc(name, df, mm, tag, rows=None, verbose=True, **kw):
    """PSAR classico (passo af x (ep - psar)) com virada no fechamento."""
    return run_psar(name, df, mm, tag, rows, verbose, **{'use_atr': False, **kw})


# ------------------------------------------------------------------ 8. Ichimoku no offset
def dch(h, l, n):
    return (roll(h, n).max().to_numpy() + roll(l, n).min().to_numpy()) / 2


def run_ichi(name, df, mm, tag, rows=None, verbose=True, rsi_ob=50, long_ok=True, short_ok=True, **extra):
    """Linhas deslocadas 25 barras para tras (sem repintar): Tenkan/Kijun [25], nuvem [50], Chikou = close.
    Compra: Tenkan cruza acima da Kijun com close acima da nuvem; sai no cruzamento contrario ainda acima da
    nuvem. Venda: cruzamento para baixo abaixo da nuvem com RSI14 >= 50 (filtro do padrao); sai no espelho."""
    o, h, l, c = ohlc(df)
    cv, bl = dch(h, l, 9), dch(h, l, 26); sa, sb = (cv + bl) / 2, dch(h, l, 52)
    cv, bl, sa, sb = sh(cv, 25), sh(bl, 25), sh(sa, 50), sh(sb, 50)
    mxc, mnc = np.fmax(sa, sb), np.fmin(sa, sb); up, dn = c > mxc, c < mnc
    bu, be = T.xover(cv, bl), T.xunder(cv, bl); r_ = T.rsi_wilder(c, 14)
    L, XL = bu & up, be & up; S, XS = be & dn & (r_ >= rsi_ob), bu & dn
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Turtle Donchian/ATR
def run_tdon(name, df, mm, tag, rows=None, verbose=True, ent=20, ext=10, mult=2.0, short=False, **extra):
    """Uma direcao por vez (parametro). Long: close >= maxima de 20 barras anterior compra; sai quando close <=
    minima de 10 anterior ou close <= EMA3(close - 2 x EMA20 do TR) anterior. Short no espelho."""
    o, h, l, c = ohlc(df)
    a = mult * ema(tr_(h, l, c), 20)
    if not short:
        L = c >= sh(roll(h, ent).max().to_numpy())
        X = (c <= sh(roll(l, ext).min().to_numpy())) | (c <= sh(ema(c - a, 3)))
        r = gsim(df, mm, L, Z(L), X, None, rev=False)
    else:
        S = c <= sh(roll(l, ent).min().to_numpy())
        X = (c >= sh(roll(h, ext).max().to_numpy())) | (c >= sh(ema(c + a, 3)))
        r = gsim(df, mm, Z(S), S, None, X, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Slopes
def run_slopes(name, df, mm, tag, rows=None, verbose=True, l1=130, l2=400, tf_=True, long_ok=True, short_ok=True, **extra):
    """Inclinacao da EMA130 vs da EMA400 (cada uma suavizada pela EMA3): rapida acima compra, com close acima da
    EMA200 (filtro); abaixo vende com close abaixo da EMA200. Sai no cruzamento das inclinacoes."""
    o, h, l, c = ohlc(df)
    m1, m2 = ema(c, l1), ema(c, l2)
    e1, e2 = ema(np.nan_to_num((m1 - sh(m1)) / m1), 3), ema(np.nan_to_num((m2 - sh(m2)) / m2), 3)
    e200 = ema(c, 200)
    L = (e1 > e2) & ((c > e200) if tf_ else True); S = (e1 < e2) & ((c < e200) if tf_ else True)
    r = gsim(df, mm, L, S, T.xunder(e1, e2), T.xover(e1, e2), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. Moving Average Band
def run_mab(name, df, mm, tag, rows=None, verbose=True, ln=40, rr=3.0, long_ok=True, short_ok=True, **extra):
    """Banda = SMA40 das maximas / das minimas. Close cruza acima da banda de cima compra, abaixo da de baixo
    vende (inverte). Stop na banda oposta da entrada e alvo de 3x o risco; rr=0: so a inversao."""
    o, h, l, c = ohlc(df)
    up, lo = T.sma(h, ln), T.sma(l, ln)
    L, S = T.xover(c, up), T.xunder(c, lo)
    kw = dict(SLL=lo, TPL=c + (c - lo) * rr, SLS=up, TPS=c - (up - c) * rr) if rr else {}
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Renko V2
@njit(cache=True)
def _renko_v2(o, c, atr):
    n = len(c); col = np.zeros(n, np.int64); p1 = 0.0; p3 = 0.0; ov = 0.0; last = 0
    for i in range(n):
        a = atr[i]
        if a == a:
            q1 = p1 + a if c[i] > p1 + a else (p1 - a if c[i] < p1 - a else p1)
            q3 = p3 + a if o[i] > p3 + a else (p3 - a if o[i] < p3 - a else p3)
            if q3 != p3: ov = p3
            p1, p3 = q1, q3
        col[i] = 1 if ov < p1 else (-1 if ov > p1 else 0)
    return col


def run_renko(name, df, mm, tag, rows=None, verbose=True, an=10, long_ok=True, short_ok=False, **extra):
    """Tijolos de ATR10 no close e na abertura; verde quando o nivel anterior do tijolo da abertura esta abaixo
    do tijolo do close. Compra na virada para verde e sai no vermelho (short desligado no padrao)."""
    o, h, l, c = ohlc(df)
    col = _renko_v2(o, c, T.atr_rma(h, l, c, an)); pc = sh(col)
    L, S = (col == 1) & (pc != 1), (col == -1) & (pc != -1)
    r = gsim(df, mm, L, S, col == -1, col == 1, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Highest High / Lowest Low
def run_hhll(name, df, mm, tag, rows=None, verbose=True, ln=20, long_ok=True, short_ok=True, **extra):
    """Close acima da maxima de 20 barras anterior compra; abaixo da minima vende; sempre posicionado."""
    o, h, l, c = ohlc(df)
    L, S = c > sh(roll(h, ln).max().to_numpy()), c < sh(roll(l, ln).min().to_numpy())
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. XAUUSD Scalping V2
def run_xsc(name, df, mm, tag, rows=None, verbose=True, tpm=1.2, slm=0.8, long_ok=True, short_ok=True, **extra):
    """EMA5 cruza a EMA13 com RSI7 > 55 compra (< 45 vende); alvo 1,2 ATR14 e stop 0,8 ATR14 (o trailing do
    Pine nao ativa sem trail_offset); o sinal contrario inverte. Filtro ATR > 0,5 ignorado (sempre verdade)."""
    o, h, l, c = ohlc(df)
    f, s = ema(c, 5), ema(c, 13); r_ = T.rsi_wilder(c, 7); a = T.atr_rma(h, l, c, 14)
    L, S = T.xover(f, s) & (r_ > 55), T.xunder(f, s) & (r_ < 45)
    kw = dict(SLL=c - slm * a, TPL=c + tpm * a, SLS=c + slm * a, TPS=c - tpm * a) if tpm else {}
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok, **kw)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. PMax on RSI w T3
def t3(x, n, vf):
    e1 = ema(x, n); e2 = ema(e1, n); e3 = ema(e2, n); e4 = ema(e3, n); e5 = ema(e4, n); e6 = ema(e5, n)
    c1 = -vf ** 3; c2 = 3 * vf ** 2 + 3 * vf ** 3; c3 = -6 * vf ** 2 - 3 * vf - 3 * vf ** 3
    c4 = 1 + 3 * vf + vf ** 3 + 3 * vf ** 2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


@njit(cache=True)
def _pmax(m, atr, mult):
    n = len(m); d = np.ones(n); ls = np.nan; ss = np.nan; dd = 1
    for i in range(n):
        if m[i] != m[i] or atr[i] != atr[i]:
            d[i] = dd; continue
        nl = m[i] - mult * atr[i]; lp = nl if ls != ls else ls
        nl = max(nl, lp) if m[i] > lp else nl
        ns = m[i] + mult * atr[i]; sp = ns if ss != ss else ss
        ns = min(ns, sp) if m[i] < sp else ns
        dd = 1 if (dd == -1 and m[i] > sp) else (-1 if (dd == 1 and m[i] < lp) else dd)
        ls, ss = nl, ns; d[i] = dd
    return d


def run_pmax(name, df, mm, tag, rows=None, verbose=True, mult=3.0, tl=8, long_ok=True, short_ok=True, **extra):
    """PMax aplicado a T3(8, 0,7) do RSI14 com 'ATR' do proprio RSI (SMA10 do TR montado com RSIs da maxima e
    da minima): compra quando o T3 cruza acima do PMax, vende abaixo; sempre posicionado."""
    o, h, l, c = ohlc(df); pc = sh(c)
    r_ = T.rsi_wilder(c, 14)
    i1 = np.where(c >= pc, c - pc, 0.0); i2 = np.where(c < pc, pc - c, 0.0)
    au, ad = T.sma(i1, 14), T.sma(i2, 14)
    k1 = np.where(h > pc, h - pc, 0.0); k2 = np.where(h < pc, pc - h, 0.0)
    k3 = np.where(l > pc, l - pc, 0.0); k4 = np.where(l < pc, pc - l, 0.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        rh = 100 - 100 / (1 + (au * 13 + k1) / (ad * 13 + k2))
        rl = 100 - 100 / (1 + (au * 13 + k3) / (ad * 13 + k4))
    rp = sh(r_)
    trr = np.fmax(np.fmax(rh - rl, np.abs(rh - rp)), np.abs(rl - rp))
    mv = t3(np.nan_to_num(r_, nan=50.0), tl, 0.7)
    d = _pmax(mv, T.sma(trr, 10), mult)
    r = G(df, mm, (d == 1) & (sh(d) == -1), (d == -1) & (sh(d) == 1), long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. Force trade scalper
def run_force(name, df, mm, tag, rows=None, verbose=True, fast=3, slow=20, long_ok=True, short_ok=True, **extra):
    """Force index acumulado (volume x variacao): EMA3 acima da EMA20 com ATR20 > ATR50, numa barra em que uma
    das duas condicoes acabou de ligar, e vela de alta: compra (espelho vende); sempre posicionado."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    xf = np.cumsum(np.nan_to_num(v * np.diff(c, prepend=c[0])))
    ff, fs = ema(xf, fast), ema(xf, slow); af, as_ = T.atr_rma(h, l, c, 20), T.atr_rma(h, l, c, 50)
    vo, pvo = af > as_, sh(af) < sh(as_)
    S = (ff < fs) & vo & ((sh(ff) > sh(fs)) | pvo) & (c < o)
    L = (ff > fs) & vo & ((sh(ff) < sh(fs)) | pvo) & (c > o)
    r = G(df, mm, L, S, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. Triple SuperTrend + StochRSI
def run_tst(name, df, mm, tag, rows=None, verbose=True, os_=28, ob=78, pl=2.0, ps=1.5, long_ok=True, short_ok=True, **extra):
    """Como escrito, o filtro dos 3 SuperTrends e sempre verdadeiro (compara o close com +-1). Compra: close >
    EMA200, %K do StochRSI cruza acima do %D com %K < 28; stop na minima de 30 barras e alvo 2x o risco. Venda:
    close < EMA200, cruza abaixo com %K > 78; stop na maxima de 25 e alvo 1,5x. Sem inversao. A EMA200 do Pine
    vem do grafico de 15m; aqui e a do proprio tempo grafico."""
    o, h, l, c = ohlc(df)
    r_ = T.rsi_wilder(c, 14); k = T.sma(stoch(r_, r_, r_, 14), 3); d = T.sma(k, 3); e = ema(c, 200)
    L = (c > e) & T.xover(k, d) & (k < os_); S = (c < e) & T.xunder(k, d) & (k > ob)
    ll, hh = roll(l, 30).min().to_numpy(), roll(h, 25).max().to_numpy()
    r = gsim(df, mm, L, S & ~L, SLL=ll, TPL=c + (c - ll) * pl, SLS=hh, TPS=c - (hh - c) * ps, rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Cumulative RSI
def run_crsi(name, df, mm, tag, rows=None, verbose=True, lo=20, hi=94, trend=False, **extra):
    """Long-only: soma de 3 RSI3 cruza acima de 20% (60) compra; cruza acima de 94% (282) vende. Filtro opcional
    de close acima da EMA100."""
    o, h, l, c = ohlc(df)
    cr = roll(T.rsi_wilder(c, 3), 3).sum().to_numpy()
    L = T.xover(cr, full(c, 3 * lo)) & ((c > ema(c, 100)) if trend else True); X = T.xover(cr, full(c, 3 * hi))
    r = gsim(df, mm, L, Z(L), X, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Breakout Trend Follower
def pivots(h, l, lb):
    n = len(h); W = 2 * lb + 1
    Hw = np.lib.stride_tricks.sliding_window_view(h, W); Lw = np.lib.stride_tricks.sliding_window_view(l, W)
    ph = np.zeros(n, bool); pl = np.zeros(n, bool)
    mid_h, mid_l = Hw[:, lb], Lw[:, lb]
    ph[W - 1:] = (mid_h >= Hw.max(1)) & (mid_h > np.delete(Hw, lb, 1).max(1))
    pl[W - 1:] = (mid_l <= Lw.min(1)) & (mid_l < np.delete(Lw, lb, 1).min(1))
    hv = pd.Series(np.where(ph, sh(h, lb), NAN)).ffill().to_numpy()
    lv = pd.Series(np.where(pl, sh(l, lb), NAN)).ffill().to_numpy()
    return hv, lv


def run_btf(name, df, mm, tag, rows=None, verbose=True, lb=3, malen=50, **extra):
    """Long-only: stop de compra no ultimo pivo de alta (3/3) quando ele esta acima da SMA50; stop de saida no
    ultimo pivo de baixa."""
    o, h, l, c = ohlc(df)
    hv, lv = pivots(h, l, lb)
    LE = np.where(hv > T.sma(c, malen), hv, NAN) if malen else hv
    return run_stp(name, df, tag, rows, verbose, extra, LE, full(c, NAN), lv, None, long_ok=True, short_ok=False)


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

        grid('bbra', run_bbra, "1. BB + RSI + ADX", TFS, 'sl0.3% adx32 ambos',
             [(f'sl{sl:.1%} adx{ax} {s}', dict(sl=sl, adx_max=ax, **sk(s)))
              for sl, ax, s in itertools.product((0.003, 0.01, 0.0), (32, 100), side2)])
        grid('emax', run_emax, "2. EMA Crossover hl2", TFS, '20x3 ambos',
             [(f'{ln}x{rt} {s}', dict(ln=ln, ratio=rt, **sk(s))) for ln, rt, s in itertools.product((20, 50), (3, 5), side2)])
        grid('ewo', run_ewo, "3. EWO RSI Exhaustion", TFS, 'vol ambos',
             [(('vol ' if v else 'semvol ') + s, dict(vol=v, **sk(s))) for v, s in itertools.product((True, False), side2)])
        grid('mrsi', run_mrsi, "4. Easy MACD + RSI (long-only)", TFS, 'rsi50 semstop',
             [(f'rsi{rm} ' + (f'sl{sl:.0%}' if sl else 'semstop'), dict(rmax=rm, sl=sl))
              for rm, sl in itertools.product((50, 101), (0.0, 0.05))])
        grid('tsi', run_tsi, "5. TSI CCI Hull", TFS, 'tp0.5% ambos',
             [(f'tp{tp:.1%} {s}', dict(tp=tp, **sk(s))) for tp, s in itertools.product((0.005, 0.02, 0.0), side2)])
        grid('turtle', run_turtle, "6. Real Turtle (stops)", TFS, '20/10 n2 ambos',
             [(f'{e}/{x} n{mu:g} {s}', dict(ent=e, ext=x, mult=mu, **sk(s)))
              for (e, x), mu, s in itertools.product(((20, 10), (55, 20)), (2.0, 4.0), side2)])
        grid('apsar', run_psar, "7. ATR Parabolic SAR", TFS, 'n1 0.02/0.2 ambos',
             [(f'n{nb} {st}/{mx} {s}', dict(use_atr=True, nb=nb, start=st, mx=mx, **sk(s)))
              for nb, (st, mx), s in itertools.product((1, 3), ((0.02, 0.2), (0.01, 0.1)), side2)])
        grid('ichi', run_ichi, "8. Ichimoku no offset + RSI", TFS, 'rsi50 ambos',
             [(f'rsi{ob} {s}', dict(rsi_ob=ob, **sk(s))) for ob, s in itertools.product((50, 0), side2)])
        grid('tdon', run_tdon, "9. Turtle Donchian/ATR", TFS, '20/10 m2 long',
             [(f'{e}/{x} m{mu:g} ' + ('short' if sd else 'long'), dict(ent=e, ext=x, mult=mu, short=sd))
              for (e, x), mu, sd in itertools.product(((20, 10), (55, 20)), (2.0, 4.0), (False, True))])
        grid('slopes', run_slopes, "10. Slopes", TFS, '130/400 filtro ambos',
             [(f'{a}/{b} ' + ('filtro ' if tf_ else 'semfiltro ') + s, dict(l1=a, l2=b, tf_=tf_, **sk(s)))
              for (a, b), tf_, s in itertools.product(((130, 400), (50, 200)), (True, False), side2)])
        grid('mab', run_mab, "11. Moving Average Band", TFS, '40 rr3 ambos',
             [(f'{ln} rr{rr:g} {s}', dict(ln=ln, rr=rr, **sk(s))) for ln, rr, s in itertools.product((40, 100), (3.0, 0.0), side2)])
        grid('renko', run_renko, "12. Renko Strategy V2", TFS, 'atr10 long',
             [(f'atr{a} {s}', dict(an=a, **sk(s))) for a, s in itertools.product((10, 30), side2)])
        grid('hhll', run_hhll, "13. Highest High / Lowest Low", TFS, '20 ambos',
             [(f'{ln} {s}', dict(ln=ln, **sk(s))) for ln, s in itertools.product((20, 55, 100), side2)])
        grid('psarc', run_psarc, "14. Parabolic SAR on close", TFS, 'n1 0.02/0.2 ambos',
             [(f'n{nb} {st}/{mx} {s}', dict(nb=nb, start=st, mx=mx, **sk(s)))
              for nb, (st, mx), s in itertools.product((1, 3), ((0.02, 0.2), (0.01, 0.1)), side2)])
        grid('xsc', run_xsc, "15. XAUUSD Scalping V2", ['15min', '30min', '1h', '4h'], 'tp1.2 sl0.8 ambos',
             [(f'tp{tp:g} sl{sl:g} {s}', dict(tpm=tp, slm=sl, **sk(s)))
              for (tp, sl), s in itertools.product(((1.2, 0.8), (3.0, 1.5), (0, 0)), side2)])
        grid('pmax', run_pmax, "16. PMax on RSI w T3", TFS, 'm3 t8 ambos',
             [(f'm{mu:g} t{tl} {s}', dict(mult=mu, tl=tl, **sk(s))) for mu, tl, s in itertools.product((3.0, 1.5), (8, 20), side2)])
        grid('force', run_force, "17. Force trade scalper", TFS, '3/20 ambos',
             [(f'{f}/{s_} {s}', dict(fast=f, slow=s_, **sk(s))) for (f, s_), s in itertools.product(((3, 20), (5, 50)), side2)])
        grid('tst', run_tst, "18. Triple SuperTrend + StochRSI", TFS, '28/78 rr2/1.5 ambos',
             [(f'{a}/{b} rr{p}/{q} {s}', dict(os_=a, ob=b, pl=p, ps=q, **sk(s)))
              for (a, b), (p, q), s in itertools.product(((28, 78), (20, 80)), ((2.0, 1.5), (3.0, 3.0)), side2)])
        grid('crsi', run_crsi, "19. Cumulative RSI (long-only)", TFS, '20/94',
             [(f'{lo}/{hi}' + (' ema100' if tr else ''), dict(lo=lo, hi=hi, trend=tr))
              for (lo, hi), tr in itertools.product(((20, 94), (10, 90)), (False, True))])
        grid('btf', run_btf, "20. Breakout Trend Follower (long-only)", TFS, 'p3 sma50',
             [(f'p{lb} ' + (f'sma{ma}' if ma else 'semfiltro'), dict(lb=lb, malen=ma))
              for lb, ma in itertools.product((3, 10), (50, 0))])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote22')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
