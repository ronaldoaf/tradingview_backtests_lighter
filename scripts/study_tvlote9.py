"""Lote 9 do TradingView (2026-10-22): 5 estrategias (ver docs/LOTE9_TV.md).

  1. [RS] MicuRobert EMA cross V2 (6YthKHw1, Pine v2)
     ZLEMA(open,5) x ZLEMA(open,34); tambem entra quando o open cruza a rapida a favor da lenta.
     Trailing stop de 22 pips sobre a maxima desde a entrada e alvo de 55 pips, checados no
     fechamento (strategy.close); entradas so na sessao 04-15h. Pips de forex viram % do preco.
  2. UT Bot alerts strategy (R9nsvSZR, Pine v5)
     UT Bot (key 3, ATR 1) filtrado por EMA200; stop em close -/+ 1,5 ATR14; stop vai ao preco de
     entrada depois de 0,75R; metade sai no alvo de 3R; sinal contrario fecha se estiver no lucro.
  3. RSI versus SMA (wDLCPh1I, Pine v2)
     RSI8 do open menos 50, SMA34 dele; compra quando a SMA passa para <= 0 (reversao), vende quando
     volta a > 0. Sempre no mercado. O trailing publicado (120 ticks sem offset) nao arma.
  4. Hull Moving Average Swing Trader (j60hYGuY, Pine v4)
     HMA(open,210) e a mesma do open[1]; linhas c1/c2 = HMA +- 2 +- (n - open); compra quando
     open > c2 e open[1] > c1, vende no espelho; o cruzamento contrario fecha.
  5. ICT Entry V2 [TS_Indie] (wm9e7Wca, Pine v6) -- nucleo simplificado
     Varredura de liquidez (pivo de forca 5) com fechamento de volta; depois um iFVG a favor (FVG
     contrario invalidado pelo close) acima do nivel varrido; ordem limite no topo do iFVG, stop no
     fundo do iFVG - 0,5 ATR50, alvo 3R. Tendencia = direcao da ultima quebra de pivo de forca 10.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos/limites no M1 (stop antes do
alvo). Custo CUSTO + funding. Controle: mesmo lado e mesma duracao.

uso: python study_tvlote9.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, ny_minutes, TFS
from study_tvlote8 import ema

NAN = np.nan
T_first_touch = T._first_touch


def zlema(x, n):
    e1 = ema(x, n); e2 = ema(e1, n)
    return 2 * e1 - e2


def summary(g, name, tag='tvlote9'):
    g.to_csv(os.path.join(D, 'results', f'study_{tag}_{name}_grid.csv'), index=False)
    print(f"\n=== resumo {name} ({len(g)} celulas) ===")
    for est, h in g.groupby('est'):
        print(f"  {est:6s} {len(h):4d} cel | liq>0 {int((h.bp_liq > 0).sum()):4d} | "
              f"liq>0 e t>2 {int(((h.bp_liq > 0) & (h.t > 2)).sum()):3d} | "
              f"CAGR>B&H {int((h.cagr > h.bh).sum()):3d} | melhor CAGR {h.cagr.max():+.1%}")
    cols = ['est', 'TF', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh',
            'sharpe', 'dd', 'expo', 'ctl_bp', 't']
    print("\n  top 15 por CAGR:")
    print(g.sort_values('cagr', ascending=False).head(15)[cols].to_string(index=False, float_format=lambda v: f'{v:.3f}'))
    print("\n  top 10 por t:")
    print(g.sort_values('t', ascending=False).head(10)[cols].to_string(index=False, float_format=lambda v: f'{v:.3f}'))


# ------------------------------------------------------------------ 1. MicuRobert EMA cross
@njit(cache=True)
def _micu_sim(o, h, l, L, S, slv, tpv, trail):
    """Decisoes no fechamento, fills na abertura seguinte. buy_close/sel_close usam a maxima (minima)
    desde a entrada (trail) ou o preco de entrada (sem trail); alvo sobre o preco de entrada."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; i0 = 0; ent = 0.0; ap = 0.0; pend = 0; xn = False
    for i in range(1, n):
        if xn and pos != 0:
            EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1; pos = 0
        xn = False
        if pend != 0 and pend != pos:
            if pos != 0:
                EI[k] = i0; EJ[k] = i; ES[k] = pos; PI[k] = ent; PO[k] = o[i]; k += 1
            pos = pend; i0 = i; ent = o[i]; ap = h[i] if pos > 0 else l[i]
        elif pos != 0 and i > i0:
            ap = max(ap, h[i]) if pos > 0 else min(ap, l[i])
        pend = 0
        if pos > 0:
            ref = ap - slv[i0] if trail else ent - slv[i0]
            if l[i] <= ref or h[i] >= ent + tpv[i0]: xn = True
        elif pos < 0:
            ref = ap + slv[i0] if trail else ent + slv[i0]
            if h[i] >= ref or l[i] <= ent - tpv[i0]: xn = True
        if L[i] and pos <= 0:
            pend = 1; xn = False
        elif S[i] and pos >= 0:
            pend = -1; xn = False
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_micu(name, df, tag, rows=None, verbose=True, fast=5, slow=34, sl=0.001, tp=0.0025, trail=True, sess=True,
             long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    m0, m1_ = zlema(o, fast), zlema(o, slow)
    L = T.xover(m0, m1_) | (T.xover(o, m0) & (m0 > m1_))
    S = T.xunder(m0, m1_) | (T.xunder(o, m0) & (m0 < m1_))
    if sess:
        tmin, _ = ny_minutes(df)
        ok = (tmin >= 240) & (tmin < 900)
        L &= ok; S &= ok
    L &= long_ok; S &= short_ok
    r = _micu_sim(o, h, l, L, S, o * sl, o * (tp if tp > 0 else 1e3), trail)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. UT Bot alerts strategy
@njit(cache=True)
def _ut_trail(src, nloss):
    n = len(src); ts = np.zeros(n)
    for i in range(n):
        p = ts[i - 1] if i else 0.0
        if p != p: p = 0.0
        sp = src[i - 1] if i else NAN
        nl = nloss[i]
        if nl != nl:
            ts[i] = 0.0; continue
        if src[i] > p and sp > p:
            ts[i] = max(p, src[i] - nl)
        elif src[i] < p and sp < p:
            ts[i] = min(p, src[i] + nl)
        elif src[i] > p:
            ts[i] = src[i] - nl
        else:
            ts[i] = src[i] + nl
    return ts


@njit(cache=True)
def _ut_sim(o, c, b2m, mo, mh, ml, nmo, nmh, nml, nm, L, S, SLL, SLS, be_r, tp_r, tp_frac, close_profit):
    """Uma posicao. Entrada na abertura seguinte ao sinal; stop inicial fixado no sinal; depois de
    be_r x R a favor o stop vai ao preco de entrada; tp_frac sai em tp_r x R. Sinal contrario no
    fechamento fecha na abertura seguinte se o trade estiver no lucro. Saida registrada com o preco
    medio das duas partes."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    pos = 0; i0 = 0; ent = 0.0; st = 0.0; R = 0.0; be_done = False; tp_done = False; part = 0.0
    pend = 0; pst = 0.0; xn = False
    for j in range(1, n):
        a = b2m[j]; b = b2m[j + 1] if j + 1 < n else nm
        if xn and pos != 0:
            px = o[j]
            EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = ent
            PO[k] = part * tp_frac + px * (1 - tp_frac) if tp_done else px; k += 1; pos = 0
        xn = False
        if pend != 0 and pos == 0:
            pos = pend; i0 = j; ent = o[j]; st = pst; R = abs(ent - st); be_done = False; tp_done = False
            if R <= 0 or (pos > 0 and st >= ent) or (pos < 0 and st <= ent):
                pos = 0
        pend = 0
        if pos != 0:
            m = a
            while m < b:
                # espelho para o short: trabalha com precos negados
                if pos > 0:
                    mo_, mh_, ml_ = mo[m], mh[m], ml[m]; s_ = st; e_ = ent
                else:
                    mo_, mh_, ml_ = nmo[m], nmh[m], nml[m]; s_ = -st; e_ = -ent
                tgt = e_ + tp_r * R; bel = e_ + be_r * R
                if mo_ <= s_ or ml_ <= s_:
                    px = mo_ if mo_ <= s_ else s_
                    px = px if pos > 0 else -px
                    EI[k] = i0; EJ[k] = j + 1 if j + 1 < n else j; ES[k] = pos; PI[k] = ent
                    PO[k] = part * tp_frac + px * (1 - tp_frac) if tp_done else px; k += 1; pos = 0
                    break
                if not tp_done and tp_r > 0 and mh_ >= tgt:
                    tp_done = True; part = (max(mo_, tgt)) if pos > 0 else -(max(mo_, tgt))
                    if tp_frac >= 1.0:
                        EI[k] = i0; EJ[k] = j + 1 if j + 1 < n else j; ES[k] = pos; PI[k] = ent; PO[k] = part
                        k += 1; pos = 0
                        break
                if not be_done and mh_ > bel:
                    be_done = True; st = ent
                m += 1
        if pos > 0 and S[j] and close_profit and c[j] > ent:
            xn = True
        elif pos < 0 and L[j] and close_profit and c[j] < ent:
            xn = True
        if pos == 0 and not xn:
            if L[j]:
                pend = 1; pst = SLL[j]
            elif S[j]:
                pend = -1; pst = SLS[j]
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_ut(name, df, mm, tag, rows=None, verbose=True, key=3.0, atrp=1, ema_len=200, slm=1.5, be_r=0.75, tp_r=3.0,
           tp_frac=0.5, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    ts = _ut_trail(c, key * T.atr_rma(h, l, c, atrp))
    above = T.xover(c, ts); below = T.xover(ts, c)
    L = (c > ts) & above; S = (c < ts) & below
    if ema_len > 0:
        e = ema(c, ema_len); L &= c > e; S &= c < e
    L &= long_ok; S &= short_ok
    a14 = T.atr_rma(h, l, c, 14)
    r = _ut_sim(o, c, mm.b2m(df), mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, len(mm.o), L, S, c - slm * a14,
                c + slm * a14, be_r if be_r > 0 else 1e9, tp_r, tp_frac, True)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. RSI versus SMA
def run_rsisma(name, df, mm, tag, rows=None, verbose=True, rl=8, ml=34, invert=False, src='open', trail=0.0,
               long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    x = o if src == 'open' else c
    rsi = T.rsi_wilder(x, rl) - 50
    ma = T.sma(rsi, ml)
    td = (ma >= 0) if invert else (ma <= 0)
    td = td & ~np.isnan(ma)
    L = td & ~np.roll(td, 1); S = ~td & np.roll(td, 1) & ~np.isnan(ma) & ~np.isnan(np.roll(ma, 1))
    L[0] = S[0] = False
    XL = S if not short_ok else None; XS = L if not long_ok else None
    r = gsim(df, mm, L, S, XL, XS, slp=trail, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Hull Swing Trader
def run_hull(name, df, mm, tag, rows=None, verbose=True, period=210, src='open', long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    p = o if src == 'open' else c
    hp = int(round(period / 2)); sq = int(round(np.sqrt(period)))
    diff = 2 * T.wma(p, hp) - T.wma(p, period)
    pp = np.concatenate([[NAN], p[:-1]])
    diff1 = 2 * T.wma(pp, hp) - T.wma(pp, period)
    n1 = T.wma(diff, sq); n2 = T.wma(diff1, sq)
    hr = np.where(n1 > n2, n2 - 2, n2 + 2)          # retracao de 2 unidades de preco, como no Pine
    c1 = hr + n1 - p; c2 = hr - n2 + p
    L = (p > c2) & (np.roll(p, 1) > c1)
    S = (p < c1) & (np.roll(p, 1) < c2)
    XL = p < c2; XS = p > c2
    L[0] = S[0] = False
    r = gsim(df, mm, L, S, XL, XS, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. ICT Entry V2 (nucleo)
@njit(cache=True)
def _ict_signals(o, h, l, c, atr, plen, tlen, gmin, gmax, trend_on):
    """Devolve, por barra, ordens limite de compra/venda (preco, stop) emitidas no fechamento.
    Liquidez = pivos de forca plen confirmados; varredura = low <= nivel com close e open acima.
    FVG de alta em i: low[i] > high[i-2]; de baixa: high[i] < low[i-2]. iFVG de alta = FVG de baixa
    cujo topo e fechado acima. Sinal: estado armado pela varredura + iFVG novo acima do nivel varrido,
    com FVG de alta anterior cujo fundo fica acima do topo do iFVG a uma distancia em [gmin,gmax] ATR."""
    n = len(c)
    BL = np.full(n, NAN); BS = np.full(n, NAN); SL_ = np.full(n, NAN); SS = np.full(n, NAN)
    piv_lo = NAN; piv_hi = NAN; swept_lo = NAN; swept_hi = NAN
    arm_b = False; arm_s = False
    # FVGs ativos (o mais recente)
    dfb = NAN; dft = NAN          # FVG de alta: fundo=high[i-2], topo=low[i]
    sft = NAN; sfb = NAN          # FVG de baixa: topo=low[i-2], fundo=high[i]
    trend = 0; th = NAN; tl = NAN
    for i in range(max(plen * 2, tlen * 2) + 2, n):
        # pivos de liquidez confirmados agora (pivo em i-plen)
        p = i - plen
        ok_h = True; ok_l = True
        for q in range(p - plen, p + plen + 1):
            if q != p:
                if h[q] >= h[p]: ok_h = False
                if l[q] <= l[p]: ok_l = False
        if ok_h: piv_hi = h[p]
        if ok_l: piv_lo = l[p]
        # tendencia: quebra do ultimo pivo de forca tlen pelo close
        p2 = i - tlen
        okh2 = True; okl2 = True
        for q in range(p2 - tlen, p2 + tlen + 1):
            if q != p2:
                if h[q] >= h[p2]: okh2 = False
                if l[q] <= l[p2]: okl2 = False
        if okh2: th = h[p2]
        if okl2: tl = l[p2]
        if th == th and c[i] > th: trend = 1; th = NAN
        if tl == tl and c[i] < tl: trend = -1; tl = NAN
        # varredura
        if piv_lo == piv_lo and l[i] <= piv_lo:
            if c[i] > piv_lo and o[i] > piv_lo:
                arm_b = True; swept_lo = piv_lo; arm_s = False
            piv_lo = NAN
        if piv_hi == piv_hi and h[i] >= piv_hi:
            if c[i] < piv_hi and o[i] < piv_hi:
                arm_s = True; swept_hi = piv_hi; arm_b = False
            piv_hi = NAN
        if arm_b and swept_lo == swept_lo and c[i] < swept_lo: arm_b = False
        if arm_s and swept_hi == swept_hi and c[i] > swept_hi: arm_s = False
        # iFVG: FVG contrario invalidado pelo close
        ib = False; is_ = False; ibt = NAN; ibb = NAN; ist = NAN; isb = NAN
        if sft == sft and c[i] > sft:
            ib = True; ibt = sft; ibb = sfb; sft = NAN; sfb = NAN
        if dfb == dfb and c[i] < dfb:
            is_ = True; ist = dft; isb = dfb; dfb = NAN; dft = NAN
        if ib and arm_b and ibb > swept_lo and (trend == 1 or not trend_on):
            BL[i] = ibt; SL_[i] = ibb - 0.5 * atr[i]; arm_b = False
        if is_ and arm_s and ist < swept_hi and (trend == -1 or not trend_on):
            BS[i] = isb; SS[i] = ist + 0.5 * atr[i]; arm_s = False
        # FVGs novos no fechamento de i
        if l[i] > h[i - 2]:
            dfb = h[i - 2]; dft = l[i]
        if h[i] < l[i - 2]:
            sft = l[i - 2]; sfb = h[i]
    return BL, SL_, BS, SS


@njit(cache=True)
def _limit_sim(b2m, mo, mh, ml, nmo, nmh, nml, nm, n, BL, SL_, BS, SS, rr, ttl):
    """Ordem limite valida por ttl barras (cancelada por sinal novo); depois do fill, stop/alvo no M1
    a partir do minuto seguinte ao do fill."""
    k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    i = 0
    while i < n - 1:
        side = 0
        if BL[i] == BL[i]: side = 1; lim = BL[i]; st = SL_[i]
        elif BS[i] == BS[i]: side = -1; lim = BS[i]; st = SS[i]
        if side == 0 or abs(lim - st) <= 0:
            i += 1; continue
        tg = lim + side * rr * abs(lim - st)
        a = b2m[i + 1]; jmax = min(i + 1 + ttl, n - 1); bmax = b2m[jmax] if jmax < n else nm
        # cancela se outro sinal aparecer antes
        for q in range(i + 1, jmax):
            if BL[q] == BL[q] or BS[q] == BS[q]:
                bmax = b2m[q + 1] if q + 1 < n else nm; break
        fm = -1; fpx = 0.0
        for m in range(a, bmax):
            if side > 0 and ml[m] <= lim:
                fm = m; fpx = min(mo[m], lim); break
            if side < 0 and mh[m] >= lim:
                fm = m; fpx = max(mo[m], lim); break
        if fm < 0:
            i += 1; continue
        if side > 0:
            m, px, code = T_first_touch(mo, mh, ml, fm + 1, nm, st, tg, True)
        else:
            m, px, code = T_first_touch(nmo, nmh, nml, fm + 1, nm, -st, -tg, True)
            px = -px
        if code == 0:
            break
        # barra de entrada/saida
        bi = np.searchsorted(b2m, fm, 'right') - 1; bj = np.searchsorted(b2m, m, 'right') - 1
        EI[k] = bi; EJ[k] = max(bj + 1, bi + 1) if bj + 1 < n else n - 1; ES[k] = side; PI[k] = fpx; PO[k] = px; k += 1
        i = max(bj + 1, i + 1)
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_ict(name, df, mm, tag, rows=None, verbose=True, plen=5, tlen=10, rr=3.0, ttl=20, trend=True,
            long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    atr = T.atr_rma(h, l, c, 50)
    BL, SL_, BS, SS = _ict_signals(o, h, l, c, atr, plen, tlen, 0.01, 0.2, trend)
    if not long_ok: BL[:] = NAN
    if not short_ok: BS[:] = NAN
    r = _limit_sim(mm.b2m(df), mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, len(mm.o), len(df), BL, SL_, BS, SS, rr, ttl)
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

        print("\n### 1. MicuRobert EMA cross V2 (ZLEMA 5/34 do open, trail 22 pips ~0,1%, alvo 55 pips)")
        for tf in ['5min'] + TFS:
            df = cache[tf]
            run_micu(name, df, f"{tf} MICU default", rows, est='micu', TF=tf, cfg='sl0.001 tp0.0025 trail sess')
            for sl, tpm, tr, ss, side in itertools.product((0.001, 0.0025, 0.005, 0.01, 0.02), (2.5, 0.0),
                                                           (True, False), (True, False), ('ambos', 'long')):
                run_micu(name, df, '', rows, False, sl=sl, tp=sl * tpm, trail=tr, sess=ss, short_ok=side == 'ambos',
                         est='micu', TF=tf, cfg=f'sl{sl} tp{sl * tpm:g} trail{int(tr)} sess{int(ss)} {side}')

        print("\n### 2. UT Bot alerts (key 3, ATR1, EMA200, stop 1,5 ATR14, BE 0,75R, 50% em 3R)")
        for tf in ['5min'] + TFS:
            df = cache[tf]
            run_ut(name, df, mm, f"{tf} UT default", rows, est='ut', TF=tf, cfg='k3 a1 ema200 sl1.5 be.75 tp3x50%')
            for key, slm, be, tpr, em, side in itertools.product((1.0, 3.0), (1.5, 3.0), (0.75, 0.0), (3.0, 0.0),
                                                                 (200, 0), ('ambos', 'long')):
                run_ut(name, df, mm, '', rows, False, key=key, slm=slm, be_r=be, tp_r=tpr, ema_len=em,
                       short_ok=side == 'ambos', est='ut', TF=tf,
                       cfg=f'k{key} sl{slm} be{be} tp{tpr} ema{em} {side}')

        print("\n### 3. RSI versus SMA (RSI8 do open, SMA34, reversao, sempre no mercado)")
        for tf in TFS:
            df = cache[tf]
            run_rsisma(name, df, mm, f"{tf} RSIvsSMA default", rows, est='rsma', TF=tf, cfg='r8 m34 rev')
            for rl, ml, inv, side in itertools.product((8, 14, 30), (10, 34, 100), (False, True), ('ambos', 'long')):
                run_rsisma(name, df, mm, '', rows, False, rl=rl, ml=ml, invert=inv, short_ok=side == 'ambos',
                           est='rsma', TF=tf, cfg=f'r{rl} m{ml} ' + ('tend' if inv else 'rev') + f' {side}')

        print("\n### 4. Hull Swing Trader (HMA 210 do open)")
        for tf in TFS:
            df = cache[tf]
            run_hull(name, df, mm, f"{tf} HULL default", rows, est='hull', TF=tf, cfg='p210')
            for per, side in itertools.product((50, 100, 210, 400), ('ambos', 'long')):
                run_hull(name, df, mm, '', rows, False, period=per, short_ok=side == 'ambos', est='hull', TF=tf,
                         cfg=f'p{per} {side}')

        print("\n### 5. ICT Entry V2 (nucleo: varredura + iFVG, limite, stop iFVG-0,5ATR50, alvo 3R)")
        for tf in ['5min', '15min', '30min', '1h']:
            df = cache[tf]
            run_ict(name, df, mm, f"{tf} ICT default", rows, est='ict', TF=tf, cfg='p5 t10 rr3')
            for pl, rr, tr, side in itertools.product((3, 5, 10), (1.0, 2.0, 3.0, 5.0), (True, False), ('ambos', 'long')):
                run_ict(name, df, mm, '', rows, False, plen=pl, rr=rr, trend=tr, short_ok=side == 'ambos', est='ict',
                        TF=tf, cfg=f'p{pl} rr{rr} trend{int(tr)} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name)


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
