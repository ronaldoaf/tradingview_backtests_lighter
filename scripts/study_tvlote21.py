"""Lote 21 do TradingView (2026-10-23): 20 estrategias nos 5 ativos (ver docs/LOTE21_TV.md).

Ignoradas na ordem da lista: Quasimodo Pattern (7WpyJVvp, zigzag de padrao QM com ordens por nivel, complexo
demais), ANN 2 signals (G37UDeXt, security Pine v2 = olha o futuro), MACD 5 iN 1 (TtLghbTF, caixa de
ferramentas com as 5 estrategias desligadas), Risk to Reward FIXED SL Backtester (uWMQ0vwN, template para
indicador externo), Mirocana (We6vmIza, security diario Pine v2 = olha o futuro), [SMT] Renko (FJLcATq9,
velas Renko via security = irreal), Kelly ratio (bFXf4IXh, exemplo de dimensionamento), syRkfqhT e
ZsKsLiUU (404), Gold Breakout WillyAlgoTrader (HnelYN0A, 1.006 linhas), PPO Divergence (0ua1XvYk, 8 regras
de divergencia por valuewhen), Take profit Multi timeframe (9lzBKqhc, exemplo de TP), ABCD Trailing
(HkuqtyQ7, mesma ABCD do lote 19), PineCoders FAQ (q9laJNG9, educativo), Double/Triple Pattern (ykzrcWQf),
Order Block FVG (PjH7wg3n) e Fancy Bollinger Bands (29lNzU30): complexos demais para reproduzir fielmente.

 1. Trend Surfers Breakout (w91kwvnX)        11. Bollinger Bands Breakout (sTFw2fOj)
 2. Squeeze Momentum LazyBear (lEQZl0vE)     12. 5min MACD scalp by Joel (qN11DuKy)
 3. MA Consecutive Up/Down (7KXy9NNJ)        13. Liquidity Sweep Filter AlgoAlpha (gx7267BR)
 4. RSI Trend Crypto (Ru7qOVtp)              14. Renko Open_Close, modo Pro (e6mDSPPe)
 5. Hulk Scalper (oGUYuz4N)                  15. Keltner bounce from border (mQKGzLMD)
 6. SuperTREX (K3U9opwQ)                     16. LUBE (i9tJOtjl)
 7. ATR Strategy (DW1GWSWQ)                  17. RSI Binary (1jTE6hJz)
 8. BB + AO (ibq1TYLX)                       18. MACD + Stochastic + RSI (2BIMZDGk)
 9. Gold/Silver 30m RSI + EMA162 (lx4O1PPu)  19. Super Guppy (vPStjyWz)
10. MACD + BB + RSI Alorse (6xo9yMmT)        20. Multi Timeframe RSI TradeDots (kfj6EdjQ)

uso: python study_tvlote21.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, stoch, dmi
from study_tvlote9 import summary
from study_tvlote20 import sh, Z, _trail, rma, tr_

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)


def G(df, mm, L, S, XL=None, XS=None, rev=True, short_ok=True, **kw):
    """gsim com saida do long no sinal de venda quando o short esta desligado."""
    if not short_ok and rev and XL is None:
        XL = S
    return gsim(df, mm, L, S, XL, XS, rev=rev, short_ok=short_ok, **kw)


def linreg(x, n, off=0):
    xs = np.arange(n, dtype=float); xm = xs.mean()
    W = np.lib.stride_tricks.sliding_window_view(np.nan_to_num(x), n)
    b = ((W - W.mean(1, keepdims=True)) * (xs - xm)).sum(1) / ((xs - xm) ** 2).sum()
    a = W.mean(1) - b * xm
    out = np.full(len(x), NAN); out[n - 1:] = a + b * (n - 1 - off)
    return out


# ------------------------------------------------------------------ 1. Trend Surfers
def run_surf(name, df, mm, tag, rows=None, verbose=True, per=168, trail=8.0, fix=2.0, long_ok=True, short_ok=True, **extra):
    """Rompimento da maxima (minima) de 168 barras; stop fixo close - 2 ATR10 e trailing close - 8 ATR10 que so
    sobe; o rompimento contrario inverte. Trailing avaliado no fechamento."""
    o, h, l, c = ohlc(df)
    hh, ll = sh(roll(h, per).max().to_numpy()), sh(roll(l, per).min().to_numpy())
    L, S = T.xover(c, hh), T.xunder(c, ll)
    a = T.atr_rma(h, l, c, 10)
    n = len(c); XL = np.zeros(n, bool); XS = np.zeros(n, bool); pos = 0; ts = 0.0
    for i in range(n):
        if pos == 1:
            ts = max(ts, c[i] - trail * a[i]); XL[i] = c[i] < ts
            if XL[i] or S[i]: pos = 0
        elif pos == -1:
            ts = min(ts, c[i] + trail * a[i]); XS[i] = c[i] > ts
            if XS[i] or L[i]: pos = 0
        if pos == 0:
            if L[i] and long_ok: pos, ts = 1, c[i] - trail * a[i]
            elif S[i] and short_ok: pos, ts = -1, c[i] + trail * a[i]
    r = G(df, mm, L, S, XL, XS, SLL=c - fix * a, SLS=c + fix * a, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Squeeze Momentum
def run_sqz(name, df, mm, tag, rows=None, verbose=True, logic=2, sl=0.005, tp=0.01, sqz=True, long_ok=True,
            short_ok=True, **extra):
    """Momentum do squeeze (linreg 20 do ohlc4 menos a media do canal). Logica 2 (padrao): compra quando o
    momentum vira para cima abaixo de zero, com squeeze desligado (BB fora do KC); vende no espelho. Sai quando
    vira contra do outro lado do zero, ou SL 0,5% / TP 1%."""
    o, h, l, c = ohlc(df)
    src = (o + h + l + c) / 4
    m1 = T.sma(src, 20); dv = 2 * roll(src, 20).std(ddof=0).to_numpy()
    rg = T.sma(h - l, 20)
    sqz_off = (m1 - dv < m1 - rg * 1.5) & (m1 + dv > m1 + rg * 1.5)
    hl2 = (h + l) / 2
    base = ((roll(hl2, 20).max().to_numpy() + roll(l, 20).min().to_numpy()) / 2 + T.sma(hl2, 20)) / 2
    val = linreg(src - base, 20)
    up, dn = T.xover(val, np.nan_to_num(sh(val))), T.xunder(val, np.nan_to_num(sh(val)))
    f = sqz_off if sqz else np.ones(len(c), bool)
    if logic == 1:
        L, S, XL, XS = up & f, dn & f, dn, up
    else:
        L, S = up & (val < 0) & f, dn & (val > 0) & f
        XL, XS = dn & (val > 0), up & (val < 0)
    r = gsim(df, mm, L, S & ~L, XL, XS, slp=sl, tpp=tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. MA Consecutive
def run_cons(name, df, mm, tag, rows=None, verbose=True, nb=4, malen=1, long_ok=True, short_ok=True, **extra):
    """4 barras seguidas com a media (comprimento 1 = o proprio close) subindo compra; caindo vende; inverte."""
    o, h, l, c = ohlc(df)
    m = ema(c, malen) if malen > 1 else c
    up = (m > sh(m)).astype(int)
    cu = np.zeros(len(c)); cd = np.zeros(len(c))
    for i in range(1, len(c)):
        cu[i] = cu[i - 1] + 1 if up[i] else 0
        cd[i] = cd[i - 1] + 1 if not up[i] else 0
    L, S = cu >= nb, cd >= nb
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. RSI Trend Crypto
def run_rsitc(name, df, mm, tag, rows=None, verbose=True, lo=35, hi=75, **extra):
    """Long-only: RSI14 cruza acima de 35 compra, cruza abaixo de 75 vende."""
    o, h, l, c = ohlc(df)
    r_ = T.rsi_wilder(c, 14)
    L, X = T.xover(r_, np.full(len(c), lo)), T.xunder(r_, np.full(len(c), hi))
    r = gsim(df, mm, L, Z(L), X, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Hulk
def run_hulk(name, df, mm, tag, rows=None, verbose=True, thr=0.3, adx_min=33, tp=0.0135, sl=0.011, long_ok=True,
             short_ok=True, **extra):
    """Pullback com EMA50 > EMA200 e close > EMA200, ADX14 > 33, histograma do MACD(12,26,11) abaixo de
    -thr x ATR14 (o script usa 5,45 em ticks) e RSI20 entre 48 e 52; short no espelho. TP 1,35%, SL 1,1%.
    O limite de 6 trades por cruzamento de EMAs nao foi reproduzido."""
    o, h, l, c = ohlc(df)
    mac = ema(c, 12) - ema(c, 26); hist = mac - ema(mac, 11)
    a = T.atr_rma(h, l, c, 14)
    _, _, adx = dmi(h, l, c, 14)
    rw = T.rsi_wilder(c, 20) - 50
    ef, es = ema(c, 50), ema(c, 200)
    mid = (rw < 2) & (rw > -2) & (adx > adx_min)
    L = (c > es) & (hist < -thr * a) & (ef > es) & mid
    S = (c < es) & (hist > thr * a) & (ef < es) & mid
    L[:200] = S[:200] = False
    r = gsim(df, mm, L, S & ~L, slp=sl, tpp=tp, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. SuperTREX
def run_strex(name, df, mm, tag, rows=None, verbose=True, os_=35, ob=70, mult=4.0, htf='W', long_ok=True,
              short_ok=False, **extra):
    """RSI14 do close da primeira barra de cada semana (amostrado, sem futuro). Cruzar acima de 35 marca o
    preco; SuperTrend 10 x 4 ancorado nesse preco; close cruza acima da linha compra, abaixo vende. Long-only
    por padrao."""
    o, h, l, c = ohlc(df)
    per = df.index.to_period(htf[0]) if htf else None
    first = np.r_[True, per[1:] != per[:-1]]
    p = pd.Series(np.where(first, c, NAN)).ffill().to_numpy()
    # o RSI do script roda na serie p barra a barra (repete o valor dentro da semana)
    vr = T.rsi_wilder(np.nan_to_num(p, nan=c[0]), 14)
    lg, st_ = T.xover(vr, np.full(len(c), os_)), T.xunder(vr, np.full(len(c), ob))
    lol = pd.Series(np.where(lg, c, NAN)).ffill().fillna(0).to_numpy()
    los = pd.Series(np.where(st_, c, NAN)).ffill().fillna(0).to_numpy()
    a = np.nan_to_num(T.atr_rma(h, l, c, 10))
    up_lev, dn_lev = lol - mult * a, lol + mult * a
    n = len(c); ut = np.zeros(n); dt = np.zeros(n); tr = np.ones(n)
    for i in range(n):
        if i:
            ut[i] = max(up_lev[i], ut[i - 1]) if lol[i - 1] > ut[i - 1] else up_lev[i]
            dt[i] = min(dn_lev[i], dt[i - 1]) if los[i - 1] < dt[i - 1] else dn_lev[i]
            tr[i] = 1 if c[i] > dt[i - 1] else (-1 if c[i] < ut[i - 1] else tr[i - 1])
        else:
            ut[i], dt[i] = up_lev[i], dn_lev[i]
    line = np.where(tr == 1, ut, dt)
    L, S = T.xover(c, line), T.xunder(c, line)
    L[:50] = S[:50] = False
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. ATR Strategy
def run_atrs(name, df, mm, tag, rows=None, verbose=True, an=5, mult=3.5, long_ok=True, short_ok=True, **extra):
    """Trailing ATR5 x 3,5 no close (mesma familia do UT Bot); close acima compra, abaixo vende; inverte."""
    o, h, l, c = ohlc(df)
    t = _trail(c, mult * T.atr_rma(h, l, c, an))
    up = c > t
    L = up & (sh(up) != 1); S = ~up & (sh(up) == 1)
    L[:an] = S[:an] = False
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. BB + AO
def run_bbao(name, df, mm, tag, rows=None, verbose=True, bl=5, **extra):
    """Long-only. EMA2 do close cruza acima da SMA5 (meio da BB) com close acima e AO subindo acima de zero;
    sai no cruzamento para baixo com AO caindo."""
    o, h, l, c = ohlc(df)
    basis = T.sma(c, bl); f = ema(c, 2)
    ao = T.sma((h + l) / 2, 5) - T.sma((h + l) / 2, 34)
    aov = np.where(ao >= 0, np.where(ao > sh(ao), 1, 2), np.where(ao > sh(ao), -1, -2))
    L = T.xover(f, basis) & (c > basis) & (np.abs(aov) == 1)
    X = T.xunder(f, basis) & (c < basis) & (np.abs(aov) == 2)
    r = gsim(df, mm, L, Z(L), X, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Gold/Silver RSI + EMA162
def run_gs(name, df, mm, tag, rows=None, verbose=True, os_=35, ob=65, fixed=False, long_ok=True, short_ok=True, **extra):
    """Como escrito: compra com close > EMA162 e RSI14 < 35; vende com close < EMA162 e RSI > 35 (o 'exit'
    do script nao tem preco e nunca fecha, entao so a entrada contraria inverte). fixed=True usa RSI > 65
    no short, que parece ser a intencao."""
    o, h, l, c = ohlc(df)
    r_ = T.rsi_wilder(c, 14); e = ema(c, 162)
    L = (c > e) & (r_ < os_); S = (c < e) & (r_ > (ob if fixed else os_))
    L[:162] = S[:162] = False
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. MACD + BB + RSI
def run_mbr(name, df, mm, tag, rows=None, verbose=True, sl=0.0, **extra):
    """Long-only. MACD 12/26/9 cruza para cima com RSI14 < 50 e close abaixo do meio da BB20; sai com RSI > 70
    e close acima da banda de cima. Stop desligado por padrao (opcional 10%)."""
    o, h, l, c = ohlc(df)
    mac = ema(c, 12) - ema(c, 26); sg = ema(mac, 9)
    r_ = T.rsi_wilder(c, 14); b = T.sma(c, 20); up = b + 2 * roll(c, 20).std(ddof=0).to_numpy()
    L = T.xover(mac, sg) & (r_ < 50) & (c < b)
    X = (r_ > 70) & (c > up)
    r = gsim(df, mm, L, Z(L), X, None, slp=sl, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 11. BB breakout
def run_bbb(name, df, mm, tag, rows=None, verbose=True, bl=15, vol=True, sl=0.02, tp=0.09, long_ok=True,
            short_ok=True, **extra):
    """Close cruza acima da BB(15, 2) compra, abaixo da banda de baixo vende; filtro de volatilidade (desvio 15
    acima da sua SMA15). Sai no rompimento contrario, SL 2%, TP 9%. O trailing de 2%/0,5% foi omitido. O script
    so opera short em perpetuos ('Auto'); aqui testamos os dois."""
    o, h, l, c = ohlc(df)
    m = T.sma(c, bl); dv = 2 * roll(c, bl).std(ddof=0).to_numpy()
    upx, dnx = T.xover(c, m + dv), T.xunder(c, m - dv)
    sd = roll(c, 15).std(ddof=0).to_numpy()
    f = (sd > T.sma(sd, 15)) if vol else np.ones(len(c), bool)
    r = gsim(df, mm, upx & f, dnx & f, dnx, upx, slp=sl, tpp=tp, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. Joel MACD scalp
def run_joel(name, df, mm, tag, rows=None, verbose=True, tp=0.005, sl=0.004, long_ok=True, short_ok=True, **extra):
    """EMA50 >= EMA200 com o cruzamento a menos de 350 barras; histograma do MACD negativo e no pico de
    |hist| das ultimas 10 barras (ou na barra anterior) compra; short no espelho com hist positivo no
    maximo de 10 barras. TP 0,5%, SL 0,4%, uma posicao por vez."""
    o, h, l, c = ohlc(df)
    mac = ema(c, 12) - ema(c, 26); hist = mac - ema(mac, 9)
    ef, es = ema(c, 50), ema(c, 200)
    bs_bull = T.barssince(T.xover(ef, es)); bs_bear = T.barssince(T.xunder(ef, es))
    ah = np.abs(hist)
    hi_abs = roll(ah, 10).max().to_numpy() == ah
    lo_abs_prev = sh(roll(ah, 10).min().to_numpy() == ah) == 1
    hi_h = roll(hist, 10).max().to_numpy() == hist
    hi_h = hi_h | (sh(hi_h) == 1)
    L = (ef >= es) & (bs_bull <= 350) & (hist < 0) & (hi_abs | lo_abs_prev)
    S = (ef < es) & (bs_bear <= 350) & (hist >= 0) & hi_h
    L[:200] = S[:200] = False
    r = gsim(df, mm, L, S & ~L, slp=sl, tpp=tp, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Liquidity Sweep Filter (tendencia)
def run_lsf(name, df, mm, tag, rows=None, verbose=True, ln=12, mult=2.0, long_ok=True, short_ok=False, **extra):
    """So a tendencia da estrategia: base = SMA12(EMA12), desvio = EMA36 de |close - base| x 2; close acima
    da banda de cima vira alta, abaixo da de baixo vira baixa. Virada compra/vende; long-only por padrao.
    Os niveis de liquidez so desenham."""
    o, h, l, c = ohlc(df)
    base = T.sma(ema(c, ln), ln); dv = ema(np.nan_to_num(np.abs(c - base)), ln * 3) * mult
    tr = np.zeros(len(c)); t = 0
    for i in range(len(c)):
        if c[i] > base[i] + dv[i]: t = 1
        elif c[i] < base[i] - dv[i]: t = -1
        tr[i] = t
    L = (tr == 1) & (sh(tr) != 1); S = (tr == -1) & (sh(tr) != -1)
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. Renko Open_Close (Pro = velas normais)
def run_renko(name, df, mm, tag, rows=None, verbose=True, mult=1.0, long_ok=True, short_ok=True, **extra):
    """Modo Pro (padrao): vela anterior de baixa, atual de alta e open[1] < open[2] compra; espelho vende. Alvo
    = tamanho da vela anterior x mult e stop = tamanho da vela anterior. A entrada por ordem stop em open[2]
    virou entrada a mercado."""
    o, h, l, c = ohlc(df)
    bs = np.abs(sh(o) - sh(c))
    L = (sh(o) > sh(c)) & (c > o) & (sh(o) < sh(o, 2))
    S = (sh(o) < sh(c)) & (c < o) & (sh(o) > sh(o, 2))
    r = gsim(df, mm, L, S & ~L, SLL=c - bs, TPL=c + bs * mult, SLS=c + bs, TPS=c - bs * mult, rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Keltner bounce
def run_kbounce(name, df, mm, tag, rows=None, verbose=True, ln=200, dev=8.0, sl=0.0, ema_exit=False, long_ok=True,
                short_ok=True, **extra):
    """SMA200 +- 8 ATR200. Close volta para dentro pela banda de baixo compra, pela de cima vende; inverte.
    Stop de 50 ticks virou % opcional; saida na media opcional."""
    o, h, l, c = ohlc(df)
    m = T.sma(c, ln); a = T.atr_rma(h, l, c, ln)
    L, S = T.xover(c, m - dev * a), T.xunder(c, m + dev * a)
    XL, XS = (T.xover(c, m), T.xunder(c, m)) if ema_exit else (None, None)
    r = gsim(df, mm, L, S, XL, XS, slp=sl, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. LUBE
@njit(cache=True)
def _friction(h, l, c, nb):
    n = len(c); f = np.zeros(n)
    for i in range(n):
        s = 0.0
        for k in range(1, nb + 1):
            j = i - k
            if j < 0: break
            if h[j] >= c[i] and l[j] <= c[i]:
                s += (1 + nb) / (k + nb)
        f[i] = s
    return f


def run_lube(name, df, mm, tag, rows=None, verbose=True, nb=500, rg=100, fl=0.5, tl=-0.1, long_ok=True, short_ok=True,
             **extra):
    """'Atrito': quantas das ultimas 500 velas contem o close atual (peso maior para as recentes). Atrito abaixo
    do minimo de 100 barras (tl = -10%, 5 barras atras) com FIR subindo compra, caindo vende; fecha quando o
    atrito passa do meio da faixa."""
    o, h, l, c = ohlc(df)
    f = _friction(h, l, c, nb)
    lo, hi = roll(f, rg).min().to_numpy(), roll(f, rg).max().to_numpy()
    mid, lo2 = lo * (1 - fl) + hi * fl, lo * (1 - tl) + hi * tl
    fir = (4 * c + 3 * np.nan_to_num(sh(c)) + 2 * np.nan_to_num(sh(c, 2)) + np.nan_to_num(sh(c, 3))) / 10
    tr = fir > sh(fir)
    base = f < sh(lo2, 5)
    L, S = base & tr, base & ~tr
    end = f > sh(mid, 5)
    L[:nb] = S[:nb] = False
    r = gsim(df, mm, L, S, end | S, end | L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 17. RSI Binary
def run_rbin(name, df, mm, tag, rows=None, verbose=True, ln=6, os_=13, ob=82, hold=3, long_ok=True, short_ok=True, **extra):
    """RSI6 cruza abaixo de 13 compra, acima de 82 vende; fecha tudo depois de 3 barras."""
    o, h, l, c = ohlc(df)
    r_ = T.rsi_wilder(c, ln)
    L, S = T.xunder(r_, np.full(len(c), os_)), T.xover(r_, np.full(len(c), ob))
    XL = (sh(L, hold) == 1); XS = (sh(S, hold) == 1)
    r = gsim(df, mm, L, S, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. MACD + Stoch + RSI
def run_msr(name, df, mm, tag, rows=None, verbose=True, kmin=50, **extra):
    """Long-only. Compra com MACD > sinal, %K(14,3) > 50 e RSI14 > 50; vende com MACD < sinal."""
    o, h, l, c = ohlc(df)
    mac = ema(c, 12) - ema(c, 26); sg = ema(mac, 9)
    k = T.sma(stoch(c, h, l, 14), 3); r_ = T.rsi_wilder(c, 14)
    L = (mac > sg) & (k > kmin) & (r_ > 50)
    r = gsim(df, mm, L, Z(L), mac < sg, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. Super Guppy
def run_guppy(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    """Fita lenta (EMAs 24 a 66, de 3 em 3) toda em ordem de alta = verde, de baixa = vermelha, senao cinza.
    Sinais antecipados (padrao): cinza -> verde ou vermelho -> cinza compra; verde -> cinza ou cinza ->
    vermelho vende; inverte."""
    o, h, l, c = ohlc(df)
    es = [ema(c, k) for k in range(24, 67, 3)]
    up = np.ones(len(c), bool); dn = np.ones(len(c), bool)
    for a, b in zip(es[:-1], es[1:]):
        up &= a > b; dn &= a < b
    col = np.where(up, 1, np.where(dn, -1, 0)); p = sh(col)
    L = ((col == 1) & (p == 0)) | ((col == 0) & (p == -1))
    S = ((col == 0) & (p == 1)) | ((col == -1) & (p == 0))
    L[:66] = S[:66] = False
    r = G(df, mm, L, S, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. MTF RSI
def htf_rsi(df, mult, ln=14):
    if mult == 1:
        return T.rsi_wilder(df.close.to_numpy(float), ln)
    step = (df.index[1] - df.index[0]) * mult
    w = df.close.resample(step, label='left', closed='left').last().dropna()
    rv = pd.Series(T.rsi_wilder(w.to_numpy(float), ln), index=w.index + step)  # vale no fim da barra maior
    bar_end = df.index + (df.index[1] - df.index[0])
    return rv.reindex(bar_end, method='ffill').to_numpy()


def run_mtfrsi(name, df, mm, tag, rows=None, verbose=True, buy=30, sell=70, cool=5, mults=(1, 3, 6), long_ok=True,
               short_ok=True, **extra):
    """RSI14 em tres tempos (o grafico, 3x e 6x, como 5/15/30m no script; o maior so com barra fechada). Todos
    abaixo de 30 compra, todos acima de 70 vende; inverte. Espera de 5 sinais iguais entre repeticoes."""
    o, h, l, c = ohlc(df)
    rs = [htf_rsi(df, m) for m in mults]
    bc = np.all([r_ < buy for r_ in rs], 0); sc = np.all([r_ > sell for r_ in rs], 0)
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); bcnt = scnt = cool
    for i in range(n):
        if bc[i]:
            if bcnt >= cool: L[i] = True; scnt = cool; bcnt = 0
            else: bcnt += 1
        if sc[i]:
            if scnt >= cool: S[i] = True; scnt = 0; bcnt = cool
            else: scnt += 1
    r = G(df, mm, L, S & ~L, short_ok=short_ok, long_ok=long_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')
        sk = lambda s: dict(short_ok=s == 'ambos')

        def sec(t):
            print(f"\n### {t}", flush=True)

        def grid(est, fn, label, tfs, default_cfg, combos):
            sec(label)
            for tf in tfs:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)

        grid('surf', run_surf, "1. Trend Surfers Breakout", TFS, 'p168 t8 f2 ambos',
             [(f'p{p} t{t} f{f} {s}', dict(per=p, trail=t, fix=f, **sk(s)))
              for p, (t, f), s in itertools.product((55, 168), ((8.0, 2.0), (4.0, 0.0)), side2)])
        grid('sqz', run_sqz, "2. Squeeze Momentum", TFS, 'l2 sl0.5 tp1 sqz ambos',
             [(f'l{lg} sl{sl:.1%} tp{tp:.0%} ' + ('sqz' if q else 'semsqz') + f' {s}',
               dict(logic=lg, sl=sl, tp=tp, sqz=q, **sk(s)))
              for lg, (sl, tp), q, s in itertools.product((1, 2), ((0.005, 0.01), (0.0, 0.0)), (True, False), side2)])
        grid('cons', run_cons, "3. MA Consecutive Up/Down", TFS, 'n4 ma1 ambos',
             [(f'n{nb} ma{ml} {s}', dict(nb=nb, malen=ml, **sk(s))) for nb, ml, s in itertools.product((4, 8), (1, 20), side2)])
        grid('rsitc', run_rsitc, "4. RSI Trend Crypto (long-only)", TFS, '35/75',
             [(f'{lo}/{hi}', dict(lo=lo, hi=hi)) for lo, hi in ((30, 70), (35, 75), (40, 80), (25, 65))])
        grid('hulk', run_hulk, "5. Hulk Scalper", ['15min', '30min', '1h', '4h'], 'thr0.3 adx33 tp1.35 sl1.1 ambos',
             [(f'thr{th} adx{ad} tp{tp:.2%} sl{sl:.1%} {s}', dict(thr=th, adx_min=ad, tp=tp, sl=sl, **sk(s)))
              for th, ad, (tp, sl), s in itertools.product((0.1, 0.3), (25, 33), ((0.0135, 0.011), (0.03, 0.02)), side2)])
        grid('strex', run_strex, "6. SuperTREX (RSI semanal amostrado)", TFS, 'm4 long',
             [(f'm{mu:g} {s}', dict(mult=mu, **sk(s))) for mu, s in itertools.product((2.0, 4.0, 8.0), side2)])
        grid('atrs', run_atrs, "7. ATR Strategy (5 x 3,5)", TFS, 'a5 m3.5 ambos',
             [(f'a{a} m{mu:g} {s}', dict(an=a, mult=mu, **sk(s))) for (a, mu), s in itertools.product(((5, 3.5), (14, 2.0), (14, 5.0)), side2)])
        grid('bbao', run_bbao, "8. BB + AO (long-only)", TFS, 'bb5', [(f'bb{b}', dict(bl=b)) for b in (5, 20)])
        grid('gs', run_gs, "9. Gold/Silver RSI + EMA162", TFS, 'como escrito ambos',
             [(('corrigido ' if fx else 'como escrito ') + s, dict(fixed=fx, **sk(s))) for fx, s in itertools.product((False, True), side2)])
        grid('mbr', run_mbr, "10. MACD + BB + RSI (long-only)", TFS, 'semstop',
             [('semstop', dict(sl=0.0)), ('sl5%', dict(sl=0.05)), ('sl10%', dict(sl=0.10))])
        grid('bbb', run_bbb, "11. Bollinger Bands Breakout", TFS, 'bb15 vol sl2 tp9 ambos',
             [(f'bb{b} ' + ('vol' if v else 'semvol') + f' sl{sl:.0%} tp{tp:.0%} {s}', dict(bl=b, vol=v, sl=sl, tp=tp, **sk(s)))
              for b, v, (sl, tp), s in itertools.product((15, 40), (True, False), ((0.02, 0.09), (0.0, 0.0)), side2)])
        grid('joel', run_joel, "12. 5min MACD scalp (Joel)", ['15min', '30min', '1h', '4h'], 'tp0.5 sl0.4 ambos',
             [(f'tp{tp:.1%} sl{sl:.1%} {s}', dict(tp=tp, sl=sl, **sk(s)))
              for (tp, sl), s in itertools.product(((0.005, 0.004), (0.01, 0.01), (0.03, 0.02)), side2)])
        grid('lsf', run_lsf, "13. Liquidity Sweep Filter (tendencia)", TFS, '12 2 long',
             [(f'{ln} {mu:g} {s}', dict(ln=ln, mult=mu, **sk(s))) for ln, mu, s in itertools.product((12, 30), (1.0, 2.0), side2)])
        grid('renko', run_renko, "14. Renko Open_Close (Pro)", TFS, 'm1 ambos',
             [(f'm{mu:g} {s}', dict(mult=mu, **sk(s))) for mu, s in itertools.product((1.0, 2.0, 3.0), side2)])
        grid('kb', run_kbounce, "15. Keltner bounce (SMA200 +- 8 ATR)", TFS, '200 d8 ambos',
             [(f'{ln} d{dv:g} ' + ('saimedia ' if ex else '') + s, dict(ln=ln, dev=dv, ema_exit=ex, **sk(s)))
              for ln, dv, ex, s in itertools.product((200, 50), (8.0, 3.0), (False, True), side2)])
        grid('lube', run_lube, "16. LUBE (atrito)", ['30min', '1h', '4h', '1D'], '500 tl-0.1 ambos',
             [(f'500 tl{tl} {s}', dict(tl=tl, **sk(s))) for tl, s in itertools.product((-0.1, 0.1), side2)])
        grid('rbin', run_rbin, "17. RSI Binary (6, 13/82, 3 barras)", TFS, '6 13/82 h3 ambos',
             [(f'{ln} {a}/{b} h{hd} {s}', dict(ln=ln, os_=a, ob=b, hold=hd, **sk(s)))
              for (ln, a, b), hd, s in itertools.product(((6, 13, 82), (14, 30, 70)), (3, 10), side2)])
        grid('msr', run_msr, "18. MACD + Stoch + RSI (long-only)", TFS, 'k50', [('k50', dict(kmin=50)), ('k80', dict(kmin=80))])
        grid('guppy', run_guppy, "19. Super Guppy", TFS, 'antecipado ambos', [(s, sk(s)) for s in side2])
        grid('mtfrsi', run_mtfrsi, "20. Multi Timeframe RSI", TFS, '1/3/6 30/70 ambos',
             [(f'{"/".join(map(str, ms))} {b}/{s_} {s}', dict(mults=ms, buy=b, sell=s_, **sk(s)))
              for ms, (b, s_), s in itertools.product(((1, 3, 6), (1, 4, 16)), ((30, 70), (40, 60)), side2)])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote21')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
