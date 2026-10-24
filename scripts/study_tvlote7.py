"""Lote 7 do TradingView (2026-10-22): 5 estrategias (ver docs/LOTE7_TV.md).

  1. Trailing SL Strategy [QuantNomad] (n3vj0MIi, Pine v4)
     Sempre no mercado: um trailing stop (low - X ou high + X, X = 4% / ATR / absoluto) que, rompido,
     inverte a posicao com ordem stop no proprio nivel.
  2. Super Trend Daily 2.0 BF (c4Cj7H2y, Pine v4)
     Long quando o SuperTrend(2, 1.5) vira para cima e |EMA(ROC30,15)| > 3%; short quando o
     SuperTrend(3, 1.3) vira para baixo e |EMA(ROC76,38)| > 3%. Stop fixo de 5% (L) / 6% (S) do preco
     medio. Sinal contrario inverte.
  3. Captain Backtest Model [TFO] (tOQ8gnxj, Pine v5)
     Faixa 06:00-10:00 NY; rompimento da maxima (minima) entre 10:00 e 11:15 define o vies; espera
     vela contraria e tomada de minima (maxima) anterior; entra quando o close supera a maxima
     (minima) anterior. Uma operacao por dia, stop 25 / alvo 75 pontos ou saida as 16:00.
  4. 72s Adaptive HMA+ pt.1 (FrjeeWdl, Pine v4)
     HMA de periodo adaptativo (172-233) com angulo de inclinacao; entrada quando a inclinacao passa
     de 17 graus com ATR14 > ATR46 e RSI entre 51 e 70; stop na meia zona (2.7 ATR40), alvo 3 ATR21,
     saida por RSI/cruzamento depois de 1 ATR de lucro. Tudo decidido no fechamento.
  5. SR TREND / Support Resistance breakout (hwHKYkE0, Pine v4)
     Fractais de 5 barras; r = media dos topos - media dos fundos em 21 barras; tendencia quando o close
     passa dos dois niveis deslocados por r; entrada no rompimento do ultimo topo/fundo.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos/ordens stop resolvidos no M1
(stop antes do alvo no mesmo minuto). Custo CUSTO + funding. Controle: mesmo lado e mesma duracao.

uso: python study_tvlote7.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_zigzagpa import _sim  # noqa: F401 (o import instala o controle vetorizado)
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1, _st_dir

TFS = ['15min', '30min', '1h', '4h', '1D']
NAN = np.nan


def ohlc(df):
    return (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))


# ------------------------------------------------------------------ simulador generico
@njit(cache=True)
def _gsim(o, b2m, mo, mh, ml, nmo, nmh, nml, nm, L, S, XL, XS, SLL, TPL, SLS, TPS, slp, tpp, rev):
    """Posicao unica. Sinal na barra i -> ordem a mercado na abertura de i+1. Stop/alvo absolutos
    (SLL/TPL do long, SLS/TPS do short, fixados na barra do sinal) ou relativos ao preco de entrada
    (slp/tpp > 0), resolvidos no M1 desde o minuto da entrada (stop primeiro). XL/XS: saida a mercado
    na abertura seguinte. rev: sinal contrario inverte."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; i0 = 0; ent = 0.0; st = 0.0; tg = 0.0; pend = 0; ps = 0.0; pt = 0.0; xnext = False
    for j in range(1, n):
        a = b2m[j]; b = b2m[j + 1] if j + 1 < n else nm
        if xnext and pos != 0:
            EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = ent; PO[k] = o[j]; k += 1; pos = 0
        xnext = False
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = ent; PO[k] = o[j]; k += 1
            pos = pend; i0 = j; ent = o[j]
            st = ps; tg = pt
            if slp > 0: st = ent * (1 - pos * slp)
            if tpp > 0: tg = ent * (1 + pos * tpp)
        pend = 0
        if pos != 0:
            s_ = st if st == st else (-1e18 if pos > 0 else 1e18)
            t_ = tg if tg == tg else (1e18 if pos > 0 else -1e18)
            if pos > 0:
                m, px, code = T_first_touch(mo, mh, ml, a, b, s_, t_, True)
            else:
                m, px, code = T_first_touch(nmo, nmh, nml, a, b, -s_, -t_, True)
                px = -px
            if code != 0:
                EI[k] = i0; EJ[k] = j + 1 if j + 1 < n else j; ES[k] = pos; PI[k] = ent; PO[k] = px; k += 1
                pos = 0
        # decisoes no fechamento de j
        if L[j] and (pos == 0 or (pos < 0 and rev)):
            pend = 1; ps = SLL[j]; pt = TPL[j]
        elif S[j] and (pos == 0 or (pos > 0 and rev)):
            pend = -1; ps = SLS[j]; pt = TPS[j]
        elif pos > 0 and XL[j]:
            xnext = True
        elif pos < 0 and XS[j]:
            xnext = True
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


T_first_touch = T._first_touch


def gsim(df, mm, L, S, XL=None, XS=None, SLL=None, TPL=None, SLS=None, TPS=None, slp=0.0, tpp=0.0,
         rev=True, long_ok=True, short_ok=True):
    n = len(df); z = np.zeros(n, bool); na = np.full(n, NAN)
    L = L & long_ok; S = S & short_ok
    return _gsim(df.open.to_numpy(float), mm.b2m(df), mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, len(mm.o), L, S,
                 z if XL is None else XL, z if XS is None else XS,
                 na if SLL is None else SLL, na if TPL is None else TPL,
                 na if SLS is None else SLS, na if TPS is None else TPS, slp, tpp, rev)


def run_g(name, df, r, tag, rows, verbose, extra):
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 1. Trailing SL [QuantNomad]
@njit(cache=True)
def _tsl_sim(o, h, l, slv, long_only):
    """Indicador e estrategia andam juntos: a ordem stop colocada no fechamento de i fica no nivel
    tsl[i]; a barra i+1 que o rompe vira a posicao, com fill em max(abertura, nivel) (gap)."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; tsl = 0.0; i0 = 0; ent = 0.0; spos = 0
    for i in range(n):
        lv = tsl
        ls = pos != 1 and h[i] > lv
        ss = pos != -1 and l[i] < lv
        if ss:
            tsl = h[i] + slv[i]
        elif ls:
            tsl = l[i] - slv[i]
        elif pos == 1:
            tsl = max(l[i] - slv[i], tsl)
        elif pos == -1:
            tsl = min(h[i] + slv[i], tsl)
        npos = 1 if ls else (-1 if ss else pos)
        if npos != pos and i > 0 and lv > 0:
            px = max(o[i], lv) if npos > 0 else min(o[i], lv)
            if spos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = spos; PI[k] = ent; PO[k] = px; k += 1; spos = 0
            if npos > 0 or not long_only:
                spos = npos; i0 = i; ent = px
        pos = npos
        if slv[i] != slv[i]:
            pos = 0; tsl = 0.0
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_tsl(name, df, tag, rows=None, verbose=True, kind='%', val=4.0, atr_len=10, long_only=False, **extra):
    o, h, l, c = ohlc(df)
    if kind == '%':
        slv = c * val / 100
    else:
        slv = val * T.atr_rma(h, l, c, atr_len)
    return run_g(name, df, _tsl_sim(o, h, l, slv, long_only), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Super Trend Daily 2.0
def roc_moving(c, n, pct):
    s = pd.Series(c)
    roc = 100 * (s - s.shift(n)) / s.shift(n)
    e = roc.ewm(span=n // 2, adjust=False).mean().to_numpy()
    return (e > pct / 2) | (e < -pct / 2)


def std_signals(df, pl=2, ml_=1.5, ps=3, ms=1.3, rocl=30, rocs=76, pct=6.0):
    o, h, l, c = ohlc(df)
    dl = _st_dir(h, l, c, ml_ * np.nan_to_num(T.atr_rma(h, l, c, pl)))
    ds = _st_dir(h, l, c, ms * np.nan_to_num(T.atr_rma(h, l, c, ps)))
    L = (dl == 1) & (np.roll(dl, 1) == -1)
    S = (ds == -1) & (np.roll(ds, 1) == 1)
    if pct > 0:
        L &= roc_moving(c, rocl, pct); S &= roc_moving(c, rocs, pct)
    L[0] = S[0] = False
    return L, S


def run_std(name, df, mm, tag, rows=None, verbose=True, sl=0.05, pct=6.0, mults=(1.5, 1.3), long_ok=True,
            short_ok=True, **extra):
    L, S = std_signals(df, ml_=mults[0], ms=mults[1], pct=pct)
    r = gsim(df, mm, L, S, slp=sl, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Captain Backtest Model
@njit(cache=True)
def _cap_sim(o, h, l, c, tmin, day, b2m, mo, mh, ml, nmo, nmh, nml, nm, risk, reward, fixed, retr1, retr2):
    """tmin = minuto do dia em NY da abertura da barra. Janelas: faixa [360,600), vies [600,675),
    operacao [600,960). Entrada a mercado na abertura seguinte; stop/alvo (fracao do preco) no M1;
    sem fixed: sai na abertura da primeira barra fora da janela (EOD)."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    ph = NAN; pl = NAN; bias = 0; pbias = 0; lg = False; sh = False; oc = False; th = False
    traded = False; pos = 0; i0 = 0; ent = 0.0; st = 0.0; tg = 0.0; pend = 0; eod = False
    prev_trade = False
    for i in range(1, n):
        t = tmin[i]
        tpre = 360 <= t < 600; ttake = 600 <= t < 675; ttrade = 600 <= t < 960
        a = b2m[i]; b = b2m[i + 1] if i + 1 < n else nm
        # abertura de i: ordens pendentes
        if eod and pos != 0:
            EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1; pos = 0
        eod = False
        if pend != 0 and pos == 0:
            pos = pend; i0 = i; ent = o[i]
            st = ent * (1 - pos * risk); tg = ent * (1 + pos * reward)
        pend = 0
        if pos != 0 and fixed:
            if pos > 0:
                m, px, code = T_first_touch(mo, mh, ml, a, b, st, tg, True)
            else:
                m, px, code = T_first_touch(nmo, nmh, nml, a, b, -st, -tg, True)
                px = -px
            if code != 0:
                EI[k] = i0; EJ[k] = i + 1 if i + 1 < n else i; ES[k] = pos; PI[k] = ent; PO[k] = px; k += 1
                pos = 0
        # fechamento de i
        if tpre:
            ph = h[i] if ph != ph else max(ph, h[i])
            pl = l[i] if pl != pl else min(pl, l[i])
        if (not ttrade) and prev_trade:
            ph = NAN; pl = NAN; bias = 0; lg = False; sh = False; oc = False; th = False; traded = False
            if pos != 0: eod = True
        pbias_now = bias
        if ttake and bias == 0:
            if h[i] > ph:
                bias = 1
            elif l[i] < pl:
                bias = -1
        if ttrade:
            if not retr1: oc = True
            elif (bias == 1 and c[i] < o[i]) or (bias == -1 and c[i] > o[i]): oc = True
            if not retr2: th = True
            elif (bias == 1 and l[i] < l[i - 1]) or (bias == -1 and h[i] > h[i - 1]): th = True
            if pbias == 1 and c[i] > h[i - 1] and oc and th and not lg:
                lg = True
            if pbias == -1 and c[i] < l[i - 1] and oc and th and not sh:
                sh = True
            if not traded and pos == 0:
                if lg:
                    pend = 1; traded = True
                elif sh:
                    pend = -1; traded = True
        pbias = bias
        prev_trade = ttrade
        _ = pbias_now
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def ny_minutes(df):
    t = df.index.tz_localize('UTC') if df.index.tz is None else df.index
    t = t.tz_convert('America/New_York')
    return (t.hour * 60 + t.minute).to_numpy(np.int64), t.normalize().asi8


def run_cap(name, df, mm, tag, rows=None, verbose=True, risk=0.15, rr=3.0, fixed=True, retr1=True,
            retr2=True, **extra):
    o, h, l, c = ohlc(df)
    tmin, day = ny_minutes(df)
    r = _cap_sim(o, h, l, c, tmin, day, mm.b2m(df), mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, len(mm.o), risk / 100,
                 risk * rr / 100, fixed, retr1, retr2)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Adaptive HMA+
@njit(cache=True)
def _wma_at(x, i, L):
    if L < 1 or i - L + 1 < 0: return NAN
    s = 0.0; w = 0.0
    for q in range(L):
        v = x[i - q]
        if v != v: return NAN
        wt = L - q; s += v * wt; w += wt
    return s / w


@njit(cache=True)
def _adaptive_hma(src, charged, lo, hi, pct):
    n = len(src); dl = (lo + hi) / 2.0
    diff = np.full(n, NAN); out = np.full(n, NAN)
    for i in range(n):
        dl = max(lo, dl * (1 - pct)) if charged[i] else min(hi, dl * (1 + pct))
        L = int(dl)
        diff[i] = 2 * _wma_at(src, i, L // 2) - _wma_at(src, i, L)
        out[i] = _wma_at(diff, i, int(np.floor(np.sqrt(L))))
    return out


@njit(cache=True)
def _hma_sim(o, h, l, c, buy, sell, obuy, osell, rsi, hma, atr21, upTL, loTL, supTL, sloTL,
             slbuy, slsell, tpm, minp):
    """Decisoes no fechamento, fills na abertura seguinte (o script usa strategy.close tambem para
    stop e alvo). Tipo 1 = buy/sell, 2 = overBuy/overSell."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; typ = 0; i0 = 0; ent = 0.0; bSL = NAN; sSL = NAN; bTP = NAN; sTP = NAN
    pend = 0; ptyp = 0; xnext = False
    for i in range(1, n):
        if xnext and pos != 0:
            EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1; pos = 0
        xnext = False
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1
            pos = pend; typ = ptyp; i0 = i; ent = o[i]
        pend = 0
        if buy[i] or sell[i] or obuy[i] or osell[i]:
            bTP = h[i] + tpm * atr21[i]; sTP = l[i] - tpm * atr21[i]
            if buy[i] or obuy[i]: bSL = slbuy[i]
            if sell[i] or osell[i]: sSL = slsell[i]
        if pos > 0:
            mp = ent + minp * atr21[i]
            stopb = l[i] <= bSL; tpb = h[i] >= bTP
            rx = (rsi[i - 1] >= 70 and rsi[i] < 70) or rsi[i] < 50
            cx = c[i - 1] >= hma[i - 1] and c[i] < hma[i]
            if typ == 1:
                ex = (c[i] >= mp and (rx or cx)) or stopb or tpb
            else:
                ex = (c[i] >= mp and ((rsi[i - 1] >= 45 and rsi[i] < 45) or (o[i] < supTL[i] and (h[i] + l[i]) / 2 < supTL[i]))) \
                    or (o[i] < hma[i] and rsi[i] < 60) or stopb or tpb
            if ex: xnext = True
        elif pos < 0:
            mp = ent - minp * atr21[i]
            stops = h[i] >= sSL; tps = l[i] <= sTP
            rx = (rsi[i - 1] <= 30 and rsi[i] > 30) or rsi[i] > 50
            cx = c[i - 1] <= hma[i - 1] and c[i] > hma[i]
            if typ == 1:
                ex = (c[i] <= mp and (rx or cx)) or stops or tps
            else:
                ex = (c[i] <= mp and ((rsi[i - 1] <= 55 and rsi[i] > 55) or (o[i] > sloTL[i] and (h[i] + l[i]) / 2 > sloTL[i]))) \
                    or (o[i] > hma[i] and rsi[i] > 40) or stops or tps
            if ex: xnext = True
        if buy[i] or obuy[i]:
            if pos <= 0: pend = 1; ptyp = 1 if buy[i] else 2; xnext = False
        elif sell[i] or osell[i]:
            if pos >= 0: pend = -1; ptyp = 1 if sell[i] else 2; xnext = False
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def hma_setup(df, minl=172, maxl=233):
    o, h, l, c = ohlc(df)
    charged = np.nan_to_num(T.atr_rma(h, l, c, 14)) > np.nan_to_num(T.atr_rma(h, l, c, 46))
    hma = _adaptive_hma(c, charged, float(minl), float(maxl), 0.03141)
    hh = pd.Series(h).rolling(34).max().to_numpy(); ll = pd.Series(l).rolling(34).min().to_numpy()
    rng = 25 / (hh - ll) * ll
    dt = (np.concatenate([[NAN, NAN], hma[:-2]]) - hma) / c * rng
    ang = np.round(np.degrees(np.arccos(1 / np.sqrt(1 + dt * dt))))
    slope = np.where(dt > 0, -ang, ang)
    rsi = T.rsi_wilder(c, 14)
    return dict(charged=charged, hma=hma, slope=slope, rsi=rsi, atr21=T.atr_rma(h, l, c, 21),
                atr40=T.atr_rma(h, l, c, 40))


def run_hma(name, df, mm, tag, rows=None, verbose=True, cache=None, flat=17, mult=2.7, slmode='half',
            tpm=3.0, maxsl=4.5, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    z = cache if cache is not None else hma_setup(df)
    hma, rsi, a40, a21 = z['hma'], z['rsi'], z['atr40'], z['atr21']
    up = (z['slope'] >= flat) & z['charged']; dn = (z['slope'] <= -flat) & z['charged']
    upn = up & ~np.roll(up, 1); dnn = dn & ~np.roll(dn, 1)
    upTL = hma + mult * a40; loTL = hma - mult * a40
    hl2 = (h + l) / 2
    buy = upn & (c > hma) & (l <= upTL) & (rsi > 51) & (rsi <= 70)
    sell = dnn & (c < hma) & (h >= loTL) & (rsi < 49) & (rsi >= 30)
    p21 = pd.Series(c).rolling(10).mean().to_numpy()  # nao usado (minorHMA so entra no overBuy)
    del p21
    minor = _adaptive_hma(c, z['charged'], 89.0, 121.0, 0.03141)
    obuy = upn & (rsi > 70) & (c > hma) & (hl2 > upTL) & (minor > hma)
    osell = dnn & (rsi < 30) & (c < hma) & (hl2 < loTL) & (minor < hma)
    if not long_ok: buy &= False; obuy &= False
    if not short_ok: sell &= False; osell &= False
    lomax = l - maxsl * a21; himax = h + maxsl * a21
    if slmode == 'half':
        sb, ss = loTL, upTL
    elif slmode == 'one':
        sb, ss = hma - 2 * mult * a40, hma + 2 * mult * a40
    elif slmode == 'hl':
        sb = pd.Series(l).rolling(48).min().to_numpy(); ss = pd.Series(h).rolling(48).max().to_numpy()
    else:
        sb, ss = lomax, himax
    slbuy = np.where(lomax < sb, sb, lomax); slsell = np.where(himax > ss, ss, himax)
    r = _hma_sim(o, h, l, c, buy, sell, obuy, osell, rsi, hma, a21, upTL, loTL, hma + mult / 2 * a40,
                 hma - mult / 2 * a40, slbuy, slsell, tpm, 1.0)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. SR TREND
@njit(cache=True)
def _srt_levels(h, l, c, length):
    n = len(c)
    hf = np.zeros(n); lf = np.zeros(n); hv = np.zeros(n); lv = np.zeros(n)
    for i in range(6, n):
        if h[i - 5] < h[i - 4] and h[i - 4] < h[i - 3] and h[i - 3] > h[i - 2] and h[i - 2] > h[i - 1]:
            hf[i] = 1; hv[i] = h[i - 3]
        if l[i - 5] > l[i - 4] and l[i - 4] > l[i - 3] and l[i - 3] < l[i - 2] and l[i - 2] < l[i - 1]:
            lf[i] = 1; lv[i] = l[i - 3]
    trend = np.zeros(n); lvc = np.full(n, NAN); lvr = np.full(n, NAN); hvc = np.full(n, NAN); hvr = np.full(n, NAN)
    tr = 0.0; a = NAN; b = NAN; cc = NAN; d = NAN
    for i in range(n):
        lo = max(0, i - length + 1)
        ln = lf[lo:i + 1].sum(); hn = hf[lo:i + 1].sum()
        r = abs(hv[lo:i + 1].sum() / hn - lv[lo:i + 1].sum() / ln) if (ln > 0 and hn > 0) else 0.0
        if lv[i] != 0 and r > 0: a = lv[i]; b = lv[i] + r
        if hv[i] != 0 and r > 0: cc = hv[i]; d = hv[i] - r
        lvc[i] = a; lvr[i] = b; hvc[i] = cc; hvr[i] = d
        if c[i] > b and c[i] > d: tr = 1.0
        elif c[i] < b and c[i] < d: tr = -1.0
        trend[i] = tr
    return trend, lvc, hvc


def run_srt(name, df, tag, rows=None, verbose=True, length=21, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    trend, lvc, hvc = _srt_levels(h, l, c, length)
    le = (trend == 1) & (c > hvc); se = (trend == -1) & (c < lvc)
    lx = trend == -1; sx = trend == 1
    if not long_ok: le = np.zeros_like(le)
    if not short_ok: se = np.zeros_like(se)
    ei, ej, es = _sim(le, lx, se, sx)
    tr = T.book(df, list(zip(ei, ej, es)), name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in ['5min'] + TFS}
        rows = []

        print("\n### 1. Trailing SL [QuantNomad] (4%, sempre no mercado)")
        for tf in TFS:
            df = cache[tf]
            run_tsl(name, df, f"{tf} TSL 4%", rows, est='tsl', TF=tf, cfg='% 4')
            for kind, val, lo in itertools.product(('%',), (0.25, 0.5, 1.0, 2.0, 4.0, 8.0), (False, True)):
                run_tsl(name, df, '', rows, False, kind=kind, val=val, long_only=lo, est='tsl', TF=tf,
                        cfg=f'% {val}' + (' so long' if lo else ''))
            for val, lo in itertools.product((1.0, 2.0, 3.0, 4.0, 6.0), (False, True)):
                run_tsl(name, df, '', rows, False, kind='atr', val=val, long_only=lo, est='tsl', TF=tf,
                        cfg=f'atr10x{val}' + (' so long' if lo else ''))

        print("\n### 2. Super Trend Daily 2.0 (stop 5%)")
        for tf in TFS:
            df = cache[tf]
            run_std(name, df, mm, f"{tf} STD default", rows, est='std', TF=tf, cfg='sl5 roc6 m1.5/1.3')
            for sl, pct, mu, side in itertools.product((0.01, 0.02, 0.05, 0.0), (0.0, 2.0, 6.0),
                                                       ((1.5, 1.3), (3.0, 3.0)), ('ambos', 'long')):
                run_std(name, df, mm, '', rows, False, sl=sl, pct=pct, mults=mu, short_ok=side == 'ambos',
                        est='std', TF=tf, cfg=f'sl{sl} roc{pct} m{mu[0]}/{mu[1]} {side}')

        print("\n### 3. Captain Backtest Model (faixa 6-10h NY, vies ate 11:15, saida 16h)")
        for tf in ['5min', '15min']:
            df = cache[tf]
            run_cap(name, df, mm, f"{tf} CAP r0.15% rr3", rows, est='cap', TF=tf, cfg='r0.15 rr3')
            for risk, rr, r1, r2 in itertools.product((0.05, 0.1, 0.15, 0.25, 0.5), (1.0, 2.0, 3.0),
                                                      (True, False), (True, False)):
                run_cap(name, df, mm, '', rows, False, risk=risk, rr=rr, retr1=r1, retr2=r2, est='cap',
                        TF=tf, cfg=f'r{risk} rr{rr} ret{int(r1)}{int(r2)}')
            for r1, r2 in itertools.product((True, False), (True, False)):
                run_cap(name, df, mm, f"{tf} CAP EOD ret{int(r1)}{int(r2)}", rows, fixed=False, retr1=r1,
                        retr2=r2, est='cap', TF=tf, cfg=f'EOD ret{int(r1)}{int(r2)}')

        print("\n### 4. Adaptive HMA+ (172-233, flat 17, meia zona)")
        for tf in TFS[:4]:
            df = cache[tf]
            z = hma_setup(df)
            run_hma(name, df, mm, f"{tf} HMA default", rows, cache=z, est='hma', TF=tf, cfg='f17 half tp3')
            for fl, slm, tp, lo in itertools.product((10, 17, 25), ('half', 'one', 'hl', 'atr'), (2.0, 3.0, 5.0),
                                                     (False, True)):
                run_hma(name, df, mm, '', rows, False, cache=z, flat=fl, slmode=slm, tpm=tp, short_ok=not lo,
                        est='hma', TF=tf, cfg=f'f{fl} {slm} tp{tp}' + (' so long' if lo else ''))

        print("\n### 5. SR TREND (21)")
        for tf in TFS:
            df = cache[tf]
            run_srt(name, df, f"{tf} SRT 21", rows, est='srt', TF=tf, cfg='len21')
            for ln, lo in itertools.product((10, 21, 50, 100), (False, True)):
                run_srt(name, df, '', rows, False, length=ln, short_ok=not lo, est='srt', TF=tf,
                        cfg=f'len{ln}' + (' so long' if lo else ''))

        g = pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg'])
        g.to_csv(os.path.join(D, 'results', f'study_tvlote7_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        for est, h in g.groupby('est'):
            print(f"  {est:6s} {len(h):4d} cel | liq>0 {int((h.bp_liq > 0).sum()):4d} | "
                  f"liq>0 e t>2 {int(((h.bp_liq > 0) & (h.t > 2)).sum()):3d} | "
                  f"CAGR>B&H {int((h.cagr > h.bh).sum()):3d} | melhor CAGR {h.cagr.max():+.1%}")
        cols = ['est', 'TF', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh',
                'sharpe', 'dd', 'expo', 'ctl_bp', 't']
        print("\n  top 15 por CAGR:")
        print(g.sort_values('cagr', ascending=False).head(15)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))
        print("\n  top 10 por t:")
        print(g.sort_values('t', ascending=False).head(10)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
