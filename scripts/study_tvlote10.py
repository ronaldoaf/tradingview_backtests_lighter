"""Lote 10 do TradingView (2026-10-22): 5 estrategias (ver docs/LOTE10_TV.md).

  1. [UL] Price Divergence Strategy v1.1 (IDoY5LgE, Pine v4)
     Divergencias (regular e oculta) entre fractais de 5 barras do preco e do histograma MACD
     (SMA12-SMA26, sinal EMA9), filtradas pelo oscilador MMLO(100) no 2o quadrante; sai quando o
     MMLO cruza zero. O trailing de 100 pontos sem offset nao arma.
  2. Full strategy AllinOne MACD-RSI-PSAR-ATR-MA (l7ELtgmb, Pine v4)
     Long: PSAR de alta, EMA10 cruza acima da SMA17, histograma MACD(SMA) > 0 e RSI5 > 72; short no
     espelho (RSI5 < 23). Stop e alvo de 5 ATR14; sinal contrario fecha.
  3. Monthly Returns in PineScript Strategies (kzp8e4X3, Pine v4)
     O exemplo do script e o Pivot Reversal do TradingView: pivo 2/1; ordem stop um tick acima do
     ultimo topo (abaixo do ultimo fundo) enquanto nao rompido. Sempre no mercado.
  4. Scalping Williams %R + MACD + SMA (975ByLQ5, Pine v5, so 1 minuto)
     %R(140) cruzando -94 com close > SMA7 arma a compra (desarma ao cruzar -40); entra quando o
     histograma MACD(24,52,9) vira positivo; sai quando o histograma cai. Venda no espelho.
  5. Moving Average Cross and/or Bbands bot V1.1 (Nb7PYc7W, Pine v3)
     Long na primeira barra com close > SMA50 > SMA200, short no espelho; so o sinal contrario fecha.
     Opcao Bollinger: compra close < banda inferior (com ou sem o filtro de medias).

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos no M1 (stop antes do alvo).
Custo CUSTO + funding. Controle: mesmo lado e mesma duracao.

uso: python study_tvlote10.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary as _summary

NAN = np.nan


def summary(g, name):
    _summary(g, name, '')
    os.replace(os.path.join(D, 'results', f'study_tvlote9_{name}_grid.csv'),
               os.path.join(D, 'results', f'study_tvlote10_{name}_grid.csv'))


def shift(x, k):
    x = np.asarray(x, float)
    return np.concatenate([np.full(k, NAN), x[:-k]]) if k else x


# ------------------------------------------------------------------ 1. Price Divergence
def pdiv_signals(df, quad=2, mmlo=100, use_reg=True, use_hid=True):
    o, h, l, c = ohlc(df)
    hist = T.sma(c, 12) - T.sma(c, 26)
    hist = hist - pd.Series(hist).ewm(span=9, adjust=False).mean().to_numpy()
    s = [shift(hist, k) for k in range(5)]
    top = (s[4] < s[2]) & (s[3] < s[2]) & (s[2] > s[1]) & (s[2] > s[0])
    bot = (s[4] > s[2]) & (s[3] > s[2]) & (s[2] < s[1]) & (s[2] < s[0])
    h2, l2 = shift(h, 2), shift(l, 2)
    hp = T.valuewhen_prev(top, s[2], 1); hpp = T.valuewhen_prev(top, h2, 1)
    lp = T.valuewhen_prev(bot, s[2], 1); lpp = T.valuewhen_prev(bot, l2, 1)
    rbe = top & (h2 > hpp) & (s[2] < hp); hbe = top & (h2 < hpp) & (s[2] > hp)
    rbu = bot & (l2 < lpp) & (s[2] > lp); hbu = bot & (l2 > lpp) & (s[2] < lp)
    hi = pd.Series(h).rolling(mmlo).max().to_numpy(); lo = pd.Series(l).rolling(mmlo).min().to_numpy()
    rng = hi - lo; mid = lo + rng * 0.5
    with np.errstate(divide='ignore', invalid='ignore'):
        osc = (c - mid) / (rng / 2)
    th = 0.125 * 2 * (quad - 1)
    q_up = shift(osc > th if quad > 1 else osc > 0, 1) == 1
    q_dn = shift(osc < -th if quad > 1 else osc < 0, 1) == 1
    L = ((use_reg & rbu) | (use_hid & hbu)) & q_up
    S = ((use_reg & rbe) | (use_hid & hbe)) & q_dn
    return L, S, osc <= 0, osc >= 0


def run_pdiv(name, df, mm, tag, rows=None, verbose=True, quad=2, mmlo=100, reg=True, hid=True, sl=0.0, invq=False,
             long_ok=True, short_ok=True, **extra):
    L, S, XL, XS = pdiv_signals(df, quad, mmlo, reg, hid)
    r = gsim(df, mm, L, S, XL, XS, slp=sl, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. AllinOne
@njit(cache=True)
def psar_up(h, l, c, start, inc, mx):
    n = len(c); up = np.zeros(n, np.bool_)
    if n < 3: return up
    upt = c[1] > c[0]
    ep = h[1] if upt else l[1]
    sar = (l[0] if upt else h[0]); sar = sar + start * (ep - sar)
    af = start
    up[1] = upt
    nxt = sar + af * (ep - sar)
    for i in range(2, n):
        sar = nxt; first = False
        if upt:
            if sar > l[i]:
                first = True; upt = False; sar = max(ep, h[i]); ep = l[i]; af = start
        else:
            if sar < h[i]:
                first = True; upt = True; sar = min(ep, l[i]); ep = h[i]; af = start
        if not first:
            if upt:
                if h[i] > ep: ep = h[i]; af = min(af + inc, mx)
            else:
                if l[i] < ep: ep = l[i]; af = min(af + inc, mx)
        if upt:
            sar = min(sar, l[i - 1], l[i - 2])
        else:
            sar = max(sar, h[i - 1], h[i - 2])
        nxt = sar + af * (ep - sar)
        up[i] = upt
    return up


def run_aio(name, df, mm, tag, rows=None, verbose=True, ob=72, os_=23, atrm=5.0, rr=1.0, use_rsi=True,
            long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    rsi = T.rsi_wilder(c, 5)
    macd = T.sma(c, 12) - T.sma(c, 26); hist = macd - T.sma(macd, 9)
    up = psar_up(h, l, c, 0.02, 0.02, 0.2)
    e10 = ema(c, 10); s17 = T.sma(c, 17)
    L = up & T.xover(e10, s17) & (hist > 0)
    S = ~up & T.xunder(e10, s17) & (hist < 0)
    if use_rsi:
        L &= rsi > ob; S &= rsi < os_
    a = T.atr_rma(h, l, c, 14)
    # stop/alvo em distancia de ATR a partir do close do sinal (o Pine usa pontos a partir do fill)
    r = gsim(df, mm, L, S, S, L, SLL=c - atrm * a, TPL=c + rr * atrm * a, SLS=c + atrm * a, TPS=c - rr * atrm * a,
             rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Pivot Reversal (Monthly Returns)
@njit(cache=True)
def _pivrev_sim(o, h, l, LV, SV, long_only):
    """LV/SV: nivel da ordem stop de compra/venda ativa para a barra i (NaN = sem ordem). Fill em
    max(abertura, nivel) (compra) / min(abertura, nivel) (venda); as duas na mesma barra: a mais
    proxima da abertura executa (a outra ficaria para a barra seguinte)."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; i0 = 0; ent = 0.0
    for i in range(1, n):
        lb = LV[i] == LV[i] and pos != 1 and h[i] >= LV[i]
        sb = SV[i] == SV[i] and pos != -1 and l[i] <= SV[i]
        if lb and sb:
            if abs(LV[i] - o[i]) <= abs(o[i] - SV[i]): sb = False
            else: lb = False
        if lb or sb:
            side = 1 if lb else -1
            px = max(o[i], LV[i]) if lb else min(o[i], SV[i])
            if pos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = px; k += 1; pos = 0
            if side > 0 or not long_only:
                pos = side; i0 = i; ent = px
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_piv(name, df, tag, rows=None, verbose=True, lb=2, rb=1, long_only=False, **extra):
    o, h, l, c = ohlc(df)
    tick = 0.01 * np.median(c) / 2000
    swh = T.pivothigh(h, lb, rb); swl = T.pivotlow(l, lb, rb)
    n = len(c); LV = np.full(n, NAN); SV = np.full(n, NAN)
    hp = NAN; lp = NAN; le = False; se = False
    for i in range(n):
        if swh[i]: hp = h[i - rb]; le = True
        elif le and h[i] > hp: le = False
        if swl[i]: lp = l[i - rb]; se = True
        elif se and l[i] < lp: se = False
        if i + 1 < n:
            if le: LV[i + 1] = hp + tick
            if se: SV[i + 1] = lp - tick
    return run_g(name, df, _pivrev_sim(o, h, l, LV, SV, long_only), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Williams %R scalper
@njit(cache=True)
def _wr_states(bc, dbc, sc, dsc, bull, bear):
    n = len(bc); ba = np.zeros(n, np.bool_); sa = np.zeros(n, np.bool_)
    b = False; s = False
    for i in range(n):
        if bc[i] and bull[i]: b = True
        if dbc[i]: b = False
        if sc[i] and bear[i]: s = True
        if dsc[i]: s = False
        ba[i] = b; sa[i] = s
    return ba, sa


def run_wr(name, df, mm, tag, rows=None, verbose=True, wl=140, lo=-94, hi=-6, sl=0.0, exit_fall=True,
           long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    hh = pd.Series(h).rolling(wl).max().to_numpy(); ll = pd.Series(l).rolling(wl).min().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        wr = (hh - c) / (hh - ll) * -100
    macd = ema(c, 24) - ema(c, 52); hist = macd - ema(macd, 9)
    s7 = T.sma(c, 7)
    ba, sa = _wr_states(T.xover(wr, np.full_like(wr, lo)), T.xover(wr, np.full_like(wr, -40)),
                        T.xunder(wr, np.full_like(wr, hi)), T.xunder(wr, np.full_like(wr, -60)), c > s7, c < s7)
    ph = shift(hist, 1)
    L = ba & (ph < 0) & (hist > 0); S = sa & (ph > 0) & (hist < 0)
    if exit_fall:
        XL = hist < ph; XS = hist > ph
    else:
        XL = S; XS = L
    r = gsim(df, mm, L, S, XL, XS, slp=sl, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. MA Cross / Bbands bot
def run_mab(name, df, mm, tag, rows=None, verbose=True, f=50, s=200, mode='ma', bbl=20, bbm=2.0, long_ok=True,
            short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    m1, m2 = T.sma(c, f), T.sma(c, s)
    mal = (c > m1) & (m1 > m2); mas = (c < m1) & (m1 < m2)
    b = T.sma(c, bbl); d = bbm * pd.Series(c).rolling(bbl).std(ddof=0).to_numpy()
    if mode == 'ma':
        lg, sh = mal, mas
    elif mode == 'bb':
        lg, sh = c < b - d, c > b + d
    else:
        lg, sh = (c < b - d) & mal, (c > b + d) & mas
    # primeira barra de cada secao (pyramiding "menor ou igual a 1")
    n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); sl_ = 0; ss = 0
    for i in range(n):
        if lg[i]: sl_ += 1; ss = 0
        if sh[i]: sl_ = 0; ss += 1
        L[i] = lg[i] and sl_ <= 1; S[i] = sh[i] and ss <= 1
    XL = S if not short_ok else None; XS = L if not long_ok else None
    r = gsim(df, mm, L, S, XL, XS, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in ['5min'] + TFS}
        cache['1min'] = m1
        rows = []

        print("\n### 1. Price Divergence v1.1 (MACD SMA, fractais, MMLO quadrante 2)")
        for tf in TFS:
            df = cache[tf]
            run_pdiv(name, df, mm, f"{tf} PDIV default", rows, est='pdiv', TF=tf, cfg='q2 m100 reg+hid')
            for q, ml, rh, sl, side in itertools.product((1, 2, 3), (50, 100, 200), ('reg+hid', 'reg', 'hid'),
                                                         (0.0, 0.01), ('ambos', 'long')):
                run_pdiv(name, df, mm, '', rows, False, quad=q, mmlo=ml, reg='reg' in rh, hid='hid' in rh, sl=sl,
                         short_ok=side == 'ambos', est='pdiv', TF=tf, cfg=f'q{q} m{ml} {rh} sl{sl} {side}')

        print("\n### 2. AllinOne (PSAR + EMA10xSMA17 + MACD + RSI5>72, stop/alvo 5 ATR)")
        for tf in ['1min', '5min'] + TFS[:4]:
            df = cache[tf]
            run_aio(name, df, mm, f"{tf} AIO default", rows, est='aio', TF=tf, cfg='rsi72/23 atr5 rr1')
            for ur, am, rr, side in itertools.product((True, False), (1.0, 2.0, 5.0), (1.0, 2.0, 3.0), ('ambos', 'long')):
                run_aio(name, df, mm, '', rows, False, use_rsi=ur, atrm=am, rr=rr, short_ok=side == 'ambos', est='aio',
                        TF=tf, cfg=f'rsi{int(ur)} atr{am} rr{rr} {side}')

        print("\n### 3. Pivot Reversal (Monthly Returns, pivo 2/1, ordem stop)")
        for tf in ['5min'] + TFS:
            df = cache[tf]
            run_piv(name, df, f"{tf} PIV default", rows, est='piv', TF=tf, cfg='2/1')
            for lb, rb, lo in itertools.product((2, 4, 8), (1, 2, 4), (False, True)):
                run_piv(name, df, '', rows, False, lb=lb, rb=rb, long_only=lo, est='piv', TF=tf,
                        cfg=f'{lb}/{rb}' + (' so long' if lo else ''))

        print("\n### 4. Williams %R + MACD + SMA (1m)")
        for tf in ['1min', '5min', '15min']:
            df = cache[tf]
            run_wr(name, df, mm, f"{tf} WR default", rows, est='wr', TF=tf, cfg='w140 -94/-6 queda')
            for wl, (lo, hi), sl, ef, side in itertools.product((14, 140), ((-94, -6), (-80, -20)), (0.0, 0.005),
                                                                 (True, False), ('ambos', 'long')):
                run_wr(name, df, mm, '', rows, False, wl=wl, lo=lo, hi=hi, sl=sl, exit_fall=ef, short_ok=side == 'ambos',
                       est='wr', TF=tf, cfg=f'w{wl} {lo}/{hi} sl{sl} ' + ('queda' if ef else 'contrario') + f' {side}')

        print("\n### 5. MA Cross / Bbands bot (SMA 50/200, primeira barra da secao)")
        for tf in TFS:
            df = cache[tf]
            run_mab(name, df, mm, f"{tf} MAB default", rows, est='mab', TF=tf, cfg='ma 50/200')
            for (f, s), mode, side in itertools.product(((20, 50), (50, 200), (100, 400)), ('ma', 'bb', 'ma+bb'),
                                                        ('ambos', 'long')):
                run_mab(name, df, mm, '', rows, False, f=f, s=s, mode=mode, short_ok=side == 'ambos', est='mab', TF=tf,
                        cfg=f'{mode} {f}/{s} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name)


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
