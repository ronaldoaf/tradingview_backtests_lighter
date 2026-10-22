"""Lote 11 do TradingView (2026-10-22): 5 estrategias (ver docs/LOTE11_TV.md).

  1. EVWMA VWAP MACD Strategy [QuantNomad] (ZguF6GBo, Pine v4)
     diff = VWAP de sessao - EVWMA(30) (media ponderada por volume elastica); MACD = EMA5(diff),
     sinal = EMA20(diff); cruzamentos invertem a posicao. Sempre no mercado.
  2. Strategy Code Example (zgn9pUcQ, Pine v2)
     EMA14 x EMA21 do open, sempre no mercado; stop 200 / alvo 1000 ticks (no ouro, 0,1% / 0,5% do
     preco); o trailing de 200 ticks sem offset nao arma.
  3. Heikin Ashi Supertrend (9z16eauD, Pine v5)
     SuperTrend(10, 2,7) calculado sobre velas Heikin Ashi; virada inverte a posicao; alvo 47%,
     stop 21% (checado no fechamento, so depois de 2 barras), stop vai a +1% depois de +4%.
  4. Grab Trading System (1HAKnNRc, Pine v4)
     Tendencia = rompimento da maxima/minima de 80 barras. Em alta, compra quando a barra anterior fez
     a minima de 21 e a atual nao (fundo menor formado); stop na minima de 80; realiza quando se forma
     um topo de 21; tudo fecha quando a tendencia vira. Venda no espelho.
  5. Easy System 420 (zBaDqbla, Pine v4)
     Placar de ~14 indicadores (PSAR, SuperTrend sobre um "VPT shadow", zigzag, ROC, DMI, CCI, SMA20,
     AO, momento, MACD, Ichimoku, HMA...); compra com placar > 15 e SuperTrend de alta, ou zigzag e
     SuperTrend de alta; venda no espelho. Sempre no mercado.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos no M1 (stop antes do alvo).
Custo CUSTO + funding. Controle: mesmo lado e mesma duracao.

uso: python study_tvlote11.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, dmi
from study_tvlote9 import summary
from study_tvlote10 import shift, psar_up

NAN = np.nan


def session_vwap(df):
    o, h, l, c = ohlc(df)
    src = (h + l + c) / 3
    v = df.volume.to_numpy(float); v = np.where(v > 0, v, 1e-9)
    t = (df.index if df.index.tz is not None else df.index.tz_localize('UTC')).tz_convert('America/New_York')
    sess = (t - pd.Timedelta(hours=17)).normalize().asi8
    g = pd.Series(sess).values
    return (pd.Series(v * src).groupby(g).cumsum() / pd.Series(v).groupby(g).cumsum()).to_numpy()


# ------------------------------------------------------------------ 1. EVWMA VWAP MACD
@njit(cache=True)
def _evwma(c, v, n):
    out = np.empty(len(c)); vs = 0.0; prev = NAN
    for i in range(len(c)):
        vs += v[i]
        if i >= n: vs -= v[i - n]
        p = prev if prev == prev else c[i]
        out[i] = ((vs - v[i]) * p + v[i] * c[i]) / vs if vs > 0 else c[i]
        prev = out[i]
    return out


def run_evw(name, df, mm, tag, rows=None, verbose=True, n=30, f=5, s=20, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float); v = np.where(v > 0, v, 1e-9)
    diff = session_vwap(df) - _evwma(c, v, n)
    m, sg = ema(diff, f), ema(diff, s)
    L = T.xover(m, sg); S = T.xunder(m, sg)
    r = gsim(df, mm, L, S, S if not short_ok else None, L if not long_ok else None, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Strategy Code Example
def run_sce(name, df, mm, tag, rows=None, verbose=True, f=14, s=21, sl=0.001, tp=0.005, long_ok=True, short_ok=True,
            **extra):
    o, h, l, c = ohlc(df)
    td = ema(o, f) >= ema(o, s)
    L = td & ~np.roll(td, 1); S = ~td & np.roll(td, 1); L[:s] = S[:s] = False
    r = gsim(df, mm, L, S, S, L, slp=sl, tpp=tp, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Heikin Ashi Supertrend
def heikin(df):
    o, h, l, c = ohlc(df)
    hc = (o + h + l + c) / 4
    ho = np.empty(len(c)); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(c)):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc)); hl = np.minimum(l, np.minimum(ho, hc))
    return ho, hh, hl, hc


@njit(cache=True)
def _ha_st(hh, hl, hc, atr, m):
    n = len(hc); d = np.ones(n); up = np.full(n, NAN); dn = np.full(n, NAN)
    for i in range(n):
        su = (hh[i] + hl[i]) / 2 - m * atr[i]; sd = (hh[i] + hl[i]) / 2 + m * atr[i]
        if i and hc[i - 1] > up[i - 1]: up[i] = max(su, up[i - 1])
        else: up[i] = su
        if i and hc[i - 1] < dn[i - 1]: dn[i] = min(sd, dn[i - 1])
        else: dn[i] = sd
        pd_ = d[i - 1] if i else 1.0
        if i and hc[i] > dn[i - 1]: d[i] = 1
        elif i and hc[i] < up[i - 1]: d[i] = -1
        else: d[i] = pd_
    return d


@njit(cache=True)
def _hast_sim(o, c, L, S, tp, sl, mv_after, mv_to):
    """Decisoes no fechamento, fills na abertura seguinte. Alvo e stop pelo close (o script usa
    strategy.close para o alvo e so arma o stop depois de 2 barras)."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; i0 = 0; ent = 0.0; pend = 0; xn = False; moved = False
    for i in range(1, n):
        if xn and pos != 0:
            EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1; pos = 0
        xn = False
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1
            pos = pend; i0 = i; ent = o[i]; moved = False
        pend = 0
        if pos != 0:
            g = pos * (c[i] / ent - 1)
            if mv_after > 0 and g > mv_after: moved = True
            stop = mv_to if moved else -sl
            if (tp > 0 and g > tp) or (sl > 0 and i - i0 > 2 and g < stop):
                xn = True
        if L[i]: pend = 1; xn = False
        elif S[i]: pend = -1; xn = False
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_hast(name, df, tag, rows=None, verbose=True, ap=10, m=2.7, ha=True, tp=0.47, sl=0.21, mv=(0.04, 0.01),
             long_only=False, **extra):
    o, h, l, c = ohlc(df)
    if ha:
        ho, hh, hl, hc = heikin(df)
    else:
        hh, hl, hc = h, l, c
    d = _ha_st(hh, hl, hc, np.nan_to_num(T.atr_rma(hh, hl, hc, ap)), m)
    L = (d == 1) & (np.roll(d, 1) == -1); S = (d == -1) & (np.roll(d, 1) == 1); L[0] = S[0] = False
    r = _hast_sim(o, c, L, S, tp, sl, mv[0], mv[1])
    if long_only:
        keep = r[2] > 0
        r = tuple(x[keep] for x in r)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Grab Trading System
@njit(cache=True)
def _grab_sim(o, h, l, c, majr, majs, minr, mins, use_stop):
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    trend = 0; pos = 0; i0 = 0; ent = 0.0; pend = 0; xn = False; stp = NAN
    for i in range(2, n):
        if xn and pos != 0:
            EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1; pos = 0
        xn = False
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1
            pos = pend; i0 = i; ent = o[i]
        pend = 0
        # stop no nivel fixado no fechamento anterior
        if use_stop and pos != 0 and stp == stp:
            if pos > 0 and l[i] <= stp:
                EI[k] = i0; EJ[k] = i + 1 if i + 1 < n else i; ES[k] = pos; PI[k] = ent; PO[k] = min(o[i], stp); k += 1; pos = 0
            elif pos < 0 and h[i] >= stp:
                EI[k] = i0; EJ[k] = i + 1 if i + 1 < n else i; ES[k] = pos; PI[k] = ent; PO[k] = max(o[i], stp); k += 1; pos = 0
        pt = trend
        if h[i] > majr[i - 1]: trend = 1
        elif l[i] < majs[i - 1]: trend = -1
        buy = trend == 1 and l[i - 1] == mins[i - 1] and l[i] > mins[i]
        sell = trend == -1 and h[i - 1] == minr[i - 1] and h[i] < minr[i]
        if pos > 0 and (sell or (h[i - 1] == minr[i - 1] and h[i] < minr[i])): xn = True
        if pos < 0 and (buy or (l[i - 1] == mins[i - 1] and l[i] > mins[i])): xn = True
        if pos != 0 and trend != pt: xn = True
        if buy and pos <= 0: pend = 1; xn = False
        elif sell and pos >= 0: pend = -1; xn = False
        stp = majs[i] if (pend > 0 or (pos > 0 and pend == 0)) else (majr[i] if (pend < 0 or pos < 0) else NAN)
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_grab(name, df, tag, rows=None, verbose=True, flb=80, slb=21, use_stop=True, long_only=False, **extra):
    o, h, l, c = ohlc(df)
    roll = lambda x, n, f: getattr(pd.Series(x).rolling(n), f)().to_numpy()
    r = _grab_sim(o, h, l, c, roll(h, flb, 'max'), roll(l, flb, 'min'), roll(h, slb, 'max'), roll(l, slb, 'min'), use_stop)
    if long_only:
        keep = r[2] > 0
        r = tuple(x[keep] for x in r)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Easy System 420
@njit(cache=True)
def _st_src(src, vpt, atr, mult):
    n = len(src); up = np.zeros(n); dn = np.zeros(n); tr = np.ones(n)
    for i in range(n):
        ul = vpt[i] - mult * atr[i]; dl = vpt[i] + mult * atr[i]
        if i and src[i - 1] > up[i - 1]: up[i] = max(ul, up[i - 1])
        else: up[i] = ul
        if i and src[i - 1] < dn[i - 1]: dn[i] = min(dl, dn[i - 1])
        else: dn[i] = dl
        if i and src[i] > dn[i - 1]: tr[i] = 1
        elif i and src[i] < up[i - 1]: tr[i] = -1
        else: tr[i] = tr[i - 1] if i else 1
        if up[i] != up[i]: up[i] = 0.0
        if dn[i] != dn[i]: dn[i] = 0.0
    return tr


@njit(cache=True)
def _zig(h, l, lo_d, hi_d):
    """Zig = +1 quando o evento mais recente do zigzag foi uma maxima nova (perna de alta), -1 se
    foi uma minima nova. lo_d/hi_d: minima/maxima de Depth barras."""
    n = len(h); z = np.zeros(n); last = 0.0; plo = NAN; phi = NAN
    for i in range(n):
        if lo_d[i] == lo_d[i] and lo_d[i] != plo and l[i] - lo_d[i] <= 0: last = -1.0
        if hi_d[i] == hi_d[i] and hi_d[i] != phi and hi_d[i] - h[i] <= 0: last = 1.0
        plo = lo_d[i]; phi = hi_d[i]; z[i] = last
    return z


@njit(cache=True)
def _mad(x, n):
    out = np.full(len(x), NAN)
    for i in range(n - 1, len(x)):
        m = x[i - n + 1:i + 1].mean(); out[i] = np.abs(x[i - n + 1:i + 1] - m).mean()
    return out


def easy_signals(df, enter=15, st_mult=3.0, st_period=7, use_zig=True):
    o, h, l, c = ohlc(df)
    src = o
    v = df.volume.to_numpy(float)
    rng = np.where(h - l > 0, h - l, np.nan)
    spreadvol = np.nan_to_num((c - o) / rng * v)
    vp = spreadvol + np.cumsum(spreadvol)
    ps = pd.Series(h - l).rolling(28).std(ddof=0).to_numpy()
    sm = T.sma(vp, 14); vs = pd.Series(vp - sm).rolling(28).std(ddof=0).to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        shadow = (vp - sm) / vs * ps
    out1 = np.where(shadow > 0, h + shadow, l + shadow)
    vpt = ema(np.nan_to_num(out1, nan=c), 5)
    tr10 = _st_src(src, vpt, np.nan_to_num(T.atr_rma(h, l, c, st_period)), st_mult)
    zig = _zig(h, l, pd.Series(l).rolling(12).min().to_numpy(), pd.Series(h).rolling(12).max().to_numpy())
    pts = np.zeros(len(c))
    pts += np.where(psar_up(h, l, c, 0.02, 0.02, 0.2), 3, -3)
    pts += np.where(tr10 == 1, 3, -3) + zig
    roc = src / shift(src, 20) - 1; pts += np.where(roc > 0, 1, -1)
    p, m, _ = dmi(h, l, c, 5); pts += np.where(p - m >= 0, 2, -2)
    tp_ = src; mad = _mad(tp_, 21)
    cci = (tp_ - T.sma(tp_, 21)) / (0.015 * mad); pts += np.where(cci > 0, 1, -1)
    pts += np.where(src > T.sma(src, 20), 1, -1)
    ao = T.sma((h + l) / 2, 5) - T.sma((h + l) / 2, 34); pts += np.sign(np.nan_to_num(ao))
    pts += np.sign(np.nan_to_num(src - shift(src, 14)))
    macd = ema(src, 12) - ema(src, 26); hist = macd - ema(macd, 9); pts += np.where(hist > shift(hist, 1), 3, -3)
    base = (pd.Series(h).rolling(26).max() + pd.Series(l).rolling(26).min()).to_numpy() / 2
    pts += np.where(src > base, 2, -2)
    pts += np.where(src > T.hma(src, 14), 1, -1)
    # Weis wave (+-2) e o bull/bear power (+-1) nao foram reproduzidos: o placar vai a +-22 em vez de +-25
    L = (tr10 == 1) & ((pts > enter) | ((zig == 1) & use_zig))
    S = (tr10 == -1) & ((pts < -enter) | ((zig == -1) & use_zig))
    return L, S


def run_easy(name, df, mm, tag, rows=None, verbose=True, enter=15, st_mult=3.0, use_zig=True, long_ok=True,
             short_ok=True, **extra):
    L, S = easy_signals(df, enter, st_mult, 7, use_zig)
    r = gsim(df, mm, L, S, S if not short_ok else None, L if not long_ok else None, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in ['5min'] + TFS}
        rows = []

        print("\n### 1. EVWMA VWAP MACD (30, 5/20, sempre no mercado)")
        for tf in ['5min'] + TFS[:4]:
            df = cache[tf]
            run_evw(name, df, mm, f"{tf} EVW default", rows, est='evw', TF=tf, cfg='n30 5/20')
            for n, (f, s), side in itertools.product((10, 30, 100), ((5, 20), (12, 26), (3, 10)), ('ambos', 'long')):
                run_evw(name, df, mm, '', rows, False, n=n, f=f, s=s, short_ok=side == 'ambos', est='evw', TF=tf,
                        cfg=f'n{n} {f}/{s} {side}')

        print("\n### 2. Strategy Code Example (EMA14x21 do open, stop 0,1% alvo 0,5%)")
        for tf in ['5min'] + TFS:
            df = cache[tf]
            run_sce(name, df, mm, f"{tf} SCE default", rows, est='sce', TF=tf, cfg='14/21 sl0.001 tp0.005')
            for (f, s), sl, side in itertools.product(((14, 21), (9, 50), (50, 200)), (0.001, 0.005, 0.02, 0.0),
                                                      ('ambos', 'long')):
                run_sce(name, df, mm, '', rows, False, f=f, s=s, sl=sl, tp=5 * sl, short_ok=side == 'ambos', est='sce',
                        TF=tf, cfg=f'{f}/{s} sl{sl} tp{5 * sl:g} {side}')

        print("\n### 3. Heikin Ashi Supertrend (10, 2,7; alvo 47%, stop 21%)")
        for tf in TFS:
            df = cache[tf]
            run_hast(name, df, f"{tf} HAST default", rows, est='hast', TF=tf, cfg='a10 m2.7 HA tp47 sl21')
            for m, ha, (tp, sl), lo in itertools.product((1.5, 2.7, 4.0), (True, False),
                                                         ((0.47, 0.21), (0.0, 0.0), (0.03, 0.01)), (False, True)):
                run_hast(name, df, '', rows, False, m=m, ha=ha, tp=tp, sl=sl, mv=(0.04, 0.01) if tp > 0.1 else (0, 0),
                         long_only=lo, est='hast', TF=tf,
                         cfg=f'm{m} ' + ('HA' if ha else 'normal') + f' tp{tp} sl{sl}' + (' so long' if lo else ''))

        print("\n### 4. Grab Trading System (80/21)")
        for tf in ['5min'] + TFS:
            df = cache[tf]
            run_grab(name, df, f"{tf} GRAB default", rows, est='grab', TF=tf, cfg='80/21 stop')
            for flb, slb, st, lo in itertools.product((40, 80, 160), (10, 21, 40), (True, False), (False, True)):
                if slb >= flb: continue
                run_grab(name, df, '', rows, False, flb=flb, slb=slb, use_stop=st, long_only=lo, est='grab', TF=tf,
                         cfg=f'{flb}/{slb} stop{int(st)}' + (' so long' if lo else ''))

        print("\n### 5. Easy System 420 (placar > 15 ou zigzag, com SuperTrend do VPT)")
        for tf in TFS:
            df = cache[tf]
            run_easy(name, df, mm, f"{tf} EASY default", rows, est='easy', TF=tf, cfg='e15 st3 zig')
            for e, stm, z, side in itertools.product((5, 10, 15), (1.5, 3.0, 6.0), (True, False), ('ambos', 'long')):
                run_easy(name, df, mm, '', rows, False, enter=e, st_mult=stm, use_zig=z, short_ok=side == 'ambos',
                         est='easy', TF=tf, cfg=f'e{e} st{stm} zig{int(z)} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote11')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
