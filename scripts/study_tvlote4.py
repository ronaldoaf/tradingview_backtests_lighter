"""Lote 4 do TradingView (2026-10-21): 3 estrategias de tendencia.

  1. AI SuperTrend x Pivot Percentile (PresentTrading, eC3qAYNQ, Pine v5)
     Dois SuperTrends calculados sobre uma "VWMA" que mistura o close de um TF maior (6h e 12h)
     com o volume do grafico, cada um com um "KNN" (k=6, n=48) que rotula se WMA(close,10) esta
     acima da WMA(SuperTrend,80). Entrada quando os dois SuperTrends e os dois KNN concordam, com
     filtro ADX/DMI diario e "Pivot Percentile" (percentis 75/25 de 5 janelas vs. janela de 144).
     Saida: stop em SuperTrend -/+ factor*ATR (praticamente sempre armado) ou entrada contraria.
     security() de v5 com lookahead_off: o valor do TF maior so muda quando o candle fecha.
  2. Pivot Point SuperTrend [Backtest] (LonesomeTheBlue, DwdC6FT4, Pine v4)
     SuperTrend cujo centro e a media movel dos pivos (2,2); flip long/short a cada virada.
  3. Trend Direction Helper (Daveatt, dzpmnane, Pine v4)
     O "TS(RISK)" se reduz a %R de 1 barra: value2 = 100*(close-low)/(high-low). up quando
     value2 > 60+RISK e o ultimo extremo anterior foi < 20-RISK (e vice-versa para dn).
     Entrada em up[1]/dn[1]; saida no cruzamento SMA 7/20.

Execucao: sinal no fechamento, ordem na ABERTURA seguinte; o stop do AI SuperTrend e resolvido na
barra do grafico (gap pula o stop -> sai na abertura). Custo CUSTO[ativo] por perna + funding.
Controle: mesmo lado, mesma duracao, entrada sorteada (aberto-a-aberto).

uso: python study_tvlote4.py [xau us100 wti btc eth]   (ESTS=ppst roda so a estrategia 2)
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_zigzagpa import _sim, _control_fast  # noqa: F401 (o import instala o controle vetorizado)

TFS = ['15min', '30min', '1h', '4h', '1D']


# ------------------------------------------------------------------ utilidades
def htf_map(df, m1, tf, col='close', fn=None):
    """request.security(tf, x) com lookahead_off: na barra do grafico que termina em t, o valor do
    ultimo candle HTF que terminou ate t (o candle corrente so aparece na barra que o fecha)."""
    h = T.resample(m1, tf)
    v = fn(h) if fn is not None else h[col].to_numpy(float)
    step = pd.Timedelta(tf)
    hend = (h.index + step).as_unit('ns').asi8
    cstep = df.index.to_series().diff().min()
    cend = (df.index + cstep).as_unit('ns').asi8
    k = np.searchsorted(hend, cend, side='right') - 1
    out = np.full(len(df), np.nan)
    ok = k >= 0
    out[ok] = v[k[ok]]
    return out


def lag(x, k=1):
    x = np.asarray(x, float)
    return np.concatenate([np.full(k, np.nan), x[:-k]])


def trades_frame(df, ei, ej, es, pin, pout, name):
    idx = df.index
    t_in = idx[ei]; t_out = idx[np.minimum(ej, len(df) - 1)]
    out = pd.DataFrame(dict(t_in=t_in, t_out=t_out, i=ei, j=ej, d=es.astype(float), u=1.0,
                            entry=pin, exit=pout))
    out['bruto'] = out.d * (out.exit / out.entry - 1)
    out['yrs'] = (out.t_out - out.t_in).dt.total_seconds() / (365 * 86400)
    return T._cost(out, name, True)


def finish(name, df, tr, tag, rows, verbose, extra):
    o = T.summarize(df, tr, name)
    if o:
        o['long_frac'] = float((tr.d > 0).mean())
        if verbose: T.line(tag, o)
        if rows is not None: rows.append(dict(o, tag=tag, **extra))
    elif verbose:
        print(f"  {tag:<34} (menos de 10 trades)")
    return o


def run_sig(name, df, le, lx, se, sx, tag, rows=None, verbose=True, **extra):
    ei, ej, es = _sim(le, lx, se, sx)
    tr = T.book(df, list(zip(ei, ej, es)), name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 1. AI SuperTrend x Pivot Percentile
@njit(cache=True)
def _supertrend(vw, atr, c, f):
    n = len(c)
    LB = np.zeros(n); UB = np.zeros(n); ST = np.zeros(n); DIR = np.ones(n)
    for i in range(n):
        lb = vw[i] - f * atr[i]; ub = vw[i] + f * atr[i]
        plb = LB[i - 1] if i and LB[i - 1] == LB[i - 1] else 0.0     # nz(lowerBand[1])
        pub = UB[i - 1] if i and UB[i - 1] == UB[i - 1] else 0.0
        cp = c[i - 1] if i else np.nan
        LB[i] = lb if (lb > plb or cp < plb) else plb
        UB[i] = ub if (ub < pub or cp > pub) else pub
        if i == 0 or atr[i - 1] != atr[i - 1]:
            d = 1
        elif ST[i - 1] == pub:
            d = -1 if c[i] > UB[i] else 1
        else:
            d = 1 if c[i] < LB[i] else -1
        DIR[i] = d
        ST[i] = LB[i] if d == -1 else UB[i]
    return ST, DIR


@njit(cache=True)
def _knn(st, lab, n, k):
    """knn_weighted do script: vizinhos do ST corrente entre os n ultimos ST (inclui ele mesmo,
    distancia 0 -> peso 1e6), ordenacao estavel como o bubble sort do Pine."""
    N = len(st); out = np.full(N, np.nan)
    for i in range(n - 1, N):
        x = st[i]
        dd = np.empty(n); ll = np.empty(n)
        bad = False
        for j in range(n):
            v = st[i - j]
            if v != v: bad = True; break
            dd[j] = abs(x - v); ll[j] = lab[i - j]
        if bad: continue
        o = np.argsort(dd, kind='mergesort')
        ws = 0.0; tw = 0.0
        for q in range(k):
            w = 1.0 / (dd[o[q]] + 1e-6)
            ws += w * ll[o[q]]; tw += w
        out[i] = ws / tw
    return out


@njit(cache=True)
def _pct_rank(x, L, p):
    """ta.percentile_nearest_rank: elemento de posto ceil(p/100*L) da janela ordenada."""
    n = len(x); out = np.full(n, np.nan)
    r = int(np.ceil(p / 100.0 * L)) - 1
    for i in range(L - 1, n):
        w = np.sort(x[i - L + 1:i + 1])
        if w[-1] == w[-1]:
            out[i] = w[r]
    return out


def aist_setup(df, m1, tf1='6h', tf2='12h', ln=10, f1=3.5, ln2=5, f2=3.0, adx_tf='1D', adx_len=14,
               plen=14):
    c = df.close.to_numpy(float); h = df.high.to_numpy(float); l = df.low.to_numpy(float)
    v = df.volume.to_numpy(float)
    atr_h = lambda n: (lambda x: T.atr_rma(x.high.to_numpy(float), x.low.to_numpy(float),
                                           x.close.to_numpy(float), n))
    out = {}
    for tag, tf, n, f in (('1', tf1, ln, f1), ('2', tf2, ln2, f2)):
        tc = htf_map(df, m1, tf)
        atr = htf_map(df, m1, tf, fn=atr_h(n))
        vw = T.wma(tc * v, n) / T.wma(v, n)
        st, d = _supertrend(vw, atr, c, f)
        price = T.wma(c, 10); sT = T.wma(st, 80)
        lab = np.where(price > sT, 1.0, 0.0)
        knn = _knn(st, lab, 48, 6)
        out['st' + tag], out['dir' + tag], out['knn' + tag], out['atr' + tag] = st, d, knn, atr
    # ADX/DMI "diario": series diarias mapeadas e diferencas feitas na barra do grafico, como no Pine
    HC = htf_map(df, m1, adx_tf); HH = htf_map(df, m1, adx_tf, 'high'); HL = htf_map(df, m1, adx_tf, 'low')
    dh = HH - lag(HH); dl = lag(HL) - HL
    pdm = np.where((dh > dl) & (dh > 0), dh, 0.0); mdm = np.where((dl > dh) & (dl > 0), dl, 0.0)
    tr = np.abs(HH - HL) + np.abs(HH - lag(HC)) + np.abs(HL - lag(HC))
    A = T.wma(tr, adx_len)
    with np.errstate(divide='ignore', invalid='ignore'):
        pdi = 100 * T.wma(pdm, adx_len) / A; mdi = 100 * T.wma(mdm, adx_len) / A
        dx = 100 * np.abs(pdi - mdi) / (pdi + mdi)
    adx = T.wma(dx, adx_len)
    out['adx_long'] = (adx > 20) & (pdi > mdi); out['adx_short'] = (adx > 20) & (mdi > pdi)
    # Pivot Percentile: o script sobrescreve os indices 3 e 4 -> 5 janelas validas (14,28,42,84,98)
    hh = _pct_rank(h, 144, 75); ll = _pct_rank(l, 144, 25)
    bull = np.zeros(len(c)); bear = np.zeros(len(c)); wb = np.zeros(len(c)); ws = np.zeros(len(c))
    for L in (plen, 2 * plen, 3 * plen, 6 * plen, 7 * plen):
        ph = _pct_rank(h, L, 75); pl = _pct_rank(l, L, 25)
        bull += (ph > hh).astype(float) + (pl > hh)
        bear += (ph < ll).astype(float) + (pl < ll)
        wb += (pl < hh) & (pl > ll); ws += (ph > ll) & (ph < hh)
    out['trend'] = (bull + 0.5 * wb - 0.5 * ws - bear) - (bear + 0.5 * ws - 0.5 * wb - bull)
    return out


def aist_signals(S, use_adx=True, f1=3.5):
    d1, d2, k1, k2 = S['dir1'], S['dir2'], S['knn1'], S['knn2']
    tup = (d1 == -1) & (lag(d1) == 1) & (k1 == 1); tup2 = (d2 == -1) & (lag(d2) == 1) & (k2 == 1)
    tdn = (d1 == 1) & (lag(d1) == -1) & (k1 == 0); tdn2 = (d2 == 1) & (lag(d2) == -1) & (k2 == 0)
    al = S['adx_long'] if use_adx else True; as_ = S['adx_short'] if use_adx else True
    le = (d1 < 0) & (k1 == 1) & (d2 < 0) & (k2 == 1) & al & (S['trend'] > 0)
    se = (d1 > 0) & (k1 == 0) & (d2 > 0) & (k2 == 0) & as_ & (S['trend'] < 0)
    lx = ~(tup | tup2) | (S['trend'] < 0)
    sx = ~(tdn | tdn2) | (S['trend'] > 0)
    lstop = S['st1'] - S['atr1'] * f1; sstop = S['st1'] + S['atr1'] * f1
    return le, se, np.where(lx, lstop, np.nan), np.where(sx, sstop, np.nan)


@njit(cache=True)
def _sim_stop(o, h, l, le, se, lstop, sstop, long_ok, short_ok):
    """strategy.entry na abertura seguinte (contraria inverte) + strategy.exit(stop) armado no
    fechamento e ativo na barra seguinte; gap alem do stop sai na abertura."""
    n = len(o); pos = 0; i0 = -1; pin = 0.0; pend = 0
    sl_l = np.nan; sl_s = np.nan
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n); k = 0
    for j in range(1, n):
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = pin; PO[k] = o[j]; k += 1
            pos = pend; i0 = j; pin = o[j]
        pend = 0
        if pos == 1 and sl_l == sl_l and (o[j] <= sl_l or l[j] <= sl_l):
            EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], sl_l); k += 1; pos = 0
        elif pos == -1 and sl_s == sl_s and (o[j] >= sl_s or h[j] >= sl_s):
            EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], sl_s); k += 1; pos = 0
        if le[j] and long_ok: pend = 1
        elif se[j] and short_ok: pend = -1
        sl_l = lstop[j]; sl_s = sstop[j]
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_aist(name, df, S, tag, rows=None, verbose=True, use_adx=True, f1=3.5, long_ok=True,
             short_ok=True, **extra):
    le, se, ls, ss = aist_signals(S, use_adx, f1)
    o, h, l = (df[k].to_numpy(float) for k in ('open', 'high', 'low'))
    ei, ej, es, pi, po = _sim_stop(o, h, l, le, se, ls, ss, long_ok, short_ok)
    tr = trades_frame(df, ei, ej, es, pi, po, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 2. Pivot Point SuperTrend
@njit(cache=True)
def _ppst(c, ph, pl, phv, plv, atr, F):
    n = len(c); center = np.nan
    TU = np.full(n, np.nan); TD = np.full(n, np.nan); TR = np.ones(n)
    for i in range(n):
        lp = phv[i] if ph[i] else (plv[i] if pl[i] else np.nan)
        if lp == lp:
            center = lp if center != center else (center * 2 + lp) / 3
        up = center - F * atr[i]; dn = center + F * atr[i]
        if i and c[i - 1] > TU[i - 1]: TU[i] = max(up, TU[i - 1])
        else: TU[i] = up
        if i and c[i - 1] < TD[i - 1]: TD[i] = min(dn, TD[i - 1])
        else: TD[i] = dn
        prev = TR[i - 1] if i else 1.0
        if i and c[i] > TD[i - 1]: TR[i] = 1
        elif i and c[i] < TU[i - 1]: TR[i] = -1
        else: TR[i] = prev
    return TR


def ppst_signals(df, prd=2, F=3.0, Pd=10):
    h = df.high.to_numpy(float); l = df.low.to_numpy(float); c = df.close.to_numpy(float)
    ph = T.pivothigh(h, prd, prd); pl = T.pivotlow(l, prd, prd)
    tr = _ppst(c, ph, pl, lag(h, prd), lag(l, prd), T.atr_rma(h, l, c, Pd), F)
    return (tr == 1) & (lag(tr) == -1), (tr == -1) & (lag(tr) == 1)


def run_bars(name, df, L, S, tag, rows=None, verbose=True, long_ok=True, short_ok=True,
             flat_on_opp=False, **extra):
    raw = T.engine_bars(df, L, S, long_ok=long_ok, short_ok=short_ok, flat_on_opp=flat_on_opp)
    tr = T.book(df, raw, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 3. Trend Direction Helper
@njit(cache=True)
def _tdh(v2, x1, x2):
    n = len(v2); up = np.zeros(n, np.bool_); dn = np.zeros(n, np.bool_)
    for i in range(51, n):
        ii = 1
        for q in range(1, 51):
            z = v2[i - q]
            if z < x2 or z > x1:
                ii = q; break
        z = v2[i - ii]
        up[i] = v2[i] > x1 and z < x2
        dn[i] = v2[i] < x2 and z > x1
    return up, dn


def tdh_signals(df, risk=10, fast=7, slow=20):
    h = df.high.to_numpy(float); l = df.low.to_numpy(float); c = df.close.to_numpy(float)
    with np.errstate(divide='ignore', invalid='ignore'):
        v2 = 100 * (c - l) / (h - l)              # 100 - |wpr(1)|; barra sem range -> na
    up, dn = _tdh(v2, 60 + risk, 20 - risk)
    sf, ss = T.sma(c, fast), T.sma(c, slow)
    up1 = np.r_[False, up[:-1]]; dn1 = np.r_[False, dn[:-1]]
    return up1, T.xunder(sf, ss), dn1, T.xover(sf, ss)


# ------------------------------------------------------------------ main
AIST_CFG = [('15min', '6h', '12h'), ('1h', '6h', '12h'), ('15min', '1h', '4h'), ('1h', '4h', '1D')]


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        ests = os.environ.get('ESTS', 'aist,ppst,tdh').split(',')

        if 'aist' in ests: print("\n### 1. AI SuperTrend x Pivot Percentile")
        for tf, a, b in (AIST_CFG if 'aist' in ests else []):
            df = cache[tf]
            for f1, f2 in ((3.5, 3.0), (2.0, 2.0), (5.0, 4.0)):
                S = aist_setup(df, m1, a, b, f1=f1, f2=f2)
                for adx, lo in itertools.product((True, False), (False, True)):
                    dflt = (f1 == 3.5 and adx)
                    cfg = f'{a}/{b} f{f1}/{f2} adx{int(adx)}' + (' so long' if lo else '')
                    run_aist(name, df, S, f"{tf} {cfg}", rows, verbose=dflt, use_adx=adx, f1=f1,
                             short_ok=not lo, est='aist', TF=tf, cfg=cfg)

        if 'ppst' in ests: print("\n### 2. Pivot Point SuperTrend (2, 3, 10)")
        for tf in (TFS if 'ppst' in ests else []):
            df = cache[tf]
            L, Sg = ppst_signals(df)
            run_bars(name, df, L, Sg, f"{tf} PPST default", rows, est='ppst', TF=tf, cfg='p2 f3 a10')
            run_bars(name, df, L, Sg, f"{tf} PPST so long", rows, short_ok=False, flat_on_opp=True,
                     est='ppst', TF=tf, cfg='p2 f3 a10 so long')
            for prd, F, Pd, lo in itertools.product((2, 3, 5), (2.0, 3.0, 4.0), (10, 20), (False, True)):
                L, Sg = ppst_signals(df, prd, F, Pd)
                run_bars(name, df, L, Sg, '', rows, verbose=False, short_ok=not lo, flat_on_opp=lo,
                         est='ppst', TF=tf, cfg=f'p{prd} f{F} a{Pd}' + (' so long' if lo else ''))

        if 'tdh' in ests: print("\n### 3. Trend Direction Helper (RISK 10, SMA 7/20)")
        for tf in (TFS if 'tdh' in ests else []):
            df = cache[tf]
            le, lx, se, sx = tdh_signals(df)
            run_sig(name, df, le, lx, se, sx, f"{tf} TDH default", rows, est='tdh', TF=tf, cfg='r10 7/20')
            run_sig(name, df, le, lx, np.zeros_like(se), sx, f"{tf} TDH so long", rows, est='tdh',
                    TF=tf, cfg='r10 7/20 so long')
            for r, (fa, sl), lo in itertools.product((0, 5, 10, 15), ((5, 10), (7, 20), (10, 30)),
                                                     (False, True)):
                le, lx, se, sx = tdh_signals(df, r, fa, sl)
                if lo: se = np.zeros_like(se)
                run_sig(name, df, le, lx, se, sx, '', rows, verbose=False, est='tdh', TF=tf,
                        cfg=f'r{r} {fa}/{sl}' + (' so long' if lo else ''))

        g = pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg'])
        g.to_csv(os.path.join(D, 'results', f'study_tvlote4_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        for est, h in g.groupby('est'):
            print(f"  {est:5s} {len(h):4d} cel | liq>0 {int((h.bp_liq > 0).sum()):4d} | "
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
