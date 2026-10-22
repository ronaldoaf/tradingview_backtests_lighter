"""Lote 8 do TradingView (2026-10-22): 5 estrategias (ver docs/LOTE8_TV.md).

  1. TrendMaster Pro 2.3 (mVkDf8qh, Pine v6)
     Cruzamento SMA 9/21 filtrado por BB(20,2) mais larga que 2 ATR20, close do lado da media da BB,
     RSI14 > 55 (< 45), MACD acima (abaixo) do sinal, Stoch K>20 e K>D (K<80 e K<D), ADX14 > 25.
     Stop 1% e alvo 2R; sinal contrario inverte; tudo fecha as 18:00 (NY). O security() com lookahead
     so desenha pivos, nao entra no sinal.
  2. Backtesting 3commas DCA Bot v2 (8d6Auyst, Pine v4)
     Long-only, sem stop: RSI7 < 30 abre a ordem base (100) e 6 ordens de seguranca limite a
     -1,5% com passo x1,6 e volume x1,5 (140, 210, ...; total 3009 = capital); alvo +4,5% sobre o
     preco medio. Simulado minuto a minuto (limites e alvo no M1).
  3. VWAP Trendfollow [wbburgin] (XoR8rQaW, Pine v5)
     VWAP de sessao com banda de 0,88 desvio; entra quando o close cruza a banda 1 a favor da
     inclinacao do VWAP, realiza quando volta a cruzar a banda 2 (2x0,88); sinal contrario inverte.
  4. BEST Engulfing + MA (ROM3crig, Pine v4)
     Estado do ultimo engolfo (alta/baixa) + estado do ultimo cruzamento close x SMA32; entra quando os
     dois concordam; sai quando close[1] cruza a SMA; stop/alvo fixos em USD (200/2000 no BTC),
     aqui em % do preco.
  5. Bollinger Bands Breakout (GKgxKjlC, Pine v4)
     SMA55 +- 1 desvio; o ultimo rompimento (close fora da banda) define a direcao. Sempre no mercado.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos/limites no M1 (stop antes do
alvo). Custo CUSTO + funding. Controle: mesmo lado e mesma duracao (no DCA: inicio sorteado).

uso: python study_tvlote8.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_zigzagpa import _sim  # noqa: F401
from study_tvlote4 import finish
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, ny_minutes, TFS
from study_engulf_psar import CUSTO, FUND

NAN = np.nan


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


def stoch(c, h, l, n):
    hh = pd.Series(h).rolling(n).max().to_numpy(); ll = pd.Series(l).rolling(n).min().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        return 100 * (c - ll) / (hh - ll)


def dmi(h, l, c, n):
    up = np.diff(h, prepend=NAN); dn = -np.diff(l, prepend=NAN)
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    pdm[0] = mdm[0] = NAN
    tr = T.atr_rma(h, l, c, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        p = 100 * T.rma_nan(pdm, n) / tr; m = 100 * T.rma_nan(mdm, n) / tr
        dx = 100 * np.abs(p - m) / (p + m)
    return p, m, T.rma_nan(dx, n)


# ------------------------------------------------------------------ 1. TrendMaster Pro
def tm_signals(df, fs=9, fl=21, filtros=True, adx_min=25):
    o, h, l, c = ohlc(df)
    sf, sl_ = T.sma(c, fs), T.sma(c, fl)
    L = T.xover(sf, sl_); S = T.xunder(sf, sl_)
    if filtros:
        basis = T.sma(c, 20); dev = pd.Series(c).rolling(20).std(ddof=0).to_numpy()
        vol = 4 * dev > 2 * T.atr_rma(h, l, c, 20)
        rsi = T.rsi_wilder(c, 14)
        macd = ema(c, 12) - ema(c, 26); sig = ema(macd, 9)
        k = T.sma(stoch(c, h, l, 14), 3); d = T.sma(k, 3)
        _, _, adx = dmi(h, l, c, 14)
        L &= vol & (c > basis) & (rsi > 55) & (macd > sig) & (k > 20) & (k > d) & (adx > adx_min)
        S &= vol & (c < basis) & (rsi < 45) & (macd < sig) & (k < 80) & (k < d) & (adx > adx_min)
    return L, S


def run_tm(name, df, mm, tag, rows=None, verbose=True, sl=0.01, rr=2.0, eod=True, filtros=True, fs=9, fl=21,
           long_ok=True, short_ok=True, **extra):
    L, S = tm_signals(df, fs, fl, filtros)
    X = None
    if eod:
        tmin, _ = ny_minutes(df)
        # a barra que comeca antes das 18:00 e termina depois dela: fecha na abertura seguinte
        dt = int((df.index[1] - df.index[0]).total_seconds() // 60)
        X = (tmin < 1080) & (tmin + dt >= 1080) if dt < 1440 else None
    r = gsim(df, mm, L, S, X, X, slp=sl, tpp=sl * rr if rr > 0 else 0.0, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. 3commas DCA
@njit(cache=True)
def _dca_sim(mo, mh, ml, sig_m, start_px, tp, dev, step, base, so, vscale, nso, sl):
    """Uma deal por vez. sig_m[m] = True no minuto em que a ordem base e executada (abertura do
    minuto, preco start_px[m]). Ordens de seguranca limite no M1; alvo no preco medio x (1+tp),
    checado a partir do minuto seguinte a cada execucao (conservador). sl>0: stop sobre a base.
    Devolve deals (m_ini, m_fim, pnl_usd, max_usd_alocado, n_so)."""
    n = len(mo)
    MI = np.empty(n // 10 + 10, np.int64); MF = np.empty(n // 10 + 10, np.int64)
    PN = np.empty(n // 10 + 10); MX = np.empty(n // 10 + 10); NS = np.empty(n // 10 + 10, np.int64)
    k = 0
    lv = np.empty(nso); qv = np.empty(nso)
    m = 0
    while m < n:
        if not sig_m[m]:
            m += 1; continue
        b0 = start_px[m]
        qty = base / b0; usd = base; last = b0
        for s in range(nso):
            last = last * (1 - dev * step ** s); lv[s] = last; qv[s] = so * vscale ** s
        filled = 0; m0 = m; done = False; stp = b0 * (1 - sl) if sl > 0 else -1.0
        q = m + 1
        while q < n:
            avg = usd / qty; tgt = avg * (1 + tp)
            if sl > 0 and ml[q] <= stp:
                px = mo[q] if mo[q] < stp else stp
                MI[k] = m0; MF[k] = q; PN[k] = qty * px - usd; MX[k] = usd; NS[k] = filled; k += 1
                done = True; break
            if mh[q] >= tgt:
                px = mo[q] if mo[q] > tgt else tgt
                MI[k] = m0; MF[k] = q; PN[k] = qty * px - usd; MX[k] = usd; NS[k] = filled; k += 1
                done = True; break
            while filled < nso and ml[q] <= lv[filled]:
                px = mo[q] if mo[q] < lv[filled] else lv[filled]
                qty += qv[filled] / px; usd += qv[filled]; filled += 1
            q += 1
        if not done:
            MI[k] = m0; MF[k] = n - 1; PN[k] = qty * mo[n - 1] - usd; MX[k] = usd; NS[k] = filled; k += 1
            break
        m = q + 1
    return MI[:k], MF[:k], PN[:k], MX[:k], NS[:k]


def dca_run(name, df, m1, rsi_thr=30, tp=0.045, dev=0.015, step=1.6, vscale=1.5, nso=6, base=100.0, so=140.0,
            sl=0.0, rnd=None):
    o, h, l, c = ohlc(df)
    mi = m1.index
    if rnd is None:
        sig = T.rsi_wilder(c, 7) < rsi_thr
    else:
        sig = rnd
    sig_m = np.zeros(len(mi), bool)
    j = np.where(sig[:-1])[0] + 1
    ms = mi.searchsorted(df.index[j]); ms = ms[ms < len(mi)]
    sig_m[ms] = True
    mo = m1.open.to_numpy(float)
    cap = base + sum(so * vscale ** s for s in range(nso))
    r = _dca_sim(mo, m1.high.to_numpy(float), m1.low.to_numpy(float), sig_m, mo, tp, dev, step, base, so,
                 vscale, nso, sl)
    MI, MF, PN, MX, NS = r
    mmin = mi.as_unit('s').asi8 / 60.0
    yrs_d = (mmin[MF] - mmin[MI]) / (365 * 1440)
    # custo: 2 pernas por ordem executada sobre o USD alocado; funding sobre USD alocado x tempo (aprox.
    # pelo maximo alocado, conservador para o long)
    cost = 2 * CUSTO[name] * MX + FUND.get(name, 5.0) / 100 * MX * yrs_d
    pnl = PN - cost
    return dict(MI=MI, MF=MF, pnl=pnl, bruto=PN, mx=MX, ns=NS, cap=cap, yrs_d=yrs_d), mmin


def dca_stats(name, df, m1, res, mmin, nsim=20, **kw):
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
    cap = res['cap']
    # equity a capital fixo (as ordens sao em USD fixo): ganho anual simples e pior perda aberta
    pnl = res['pnl']
    ann = pnl.sum() / cap / yrs
    mo = m1.open.to_numpy(float)
    bh = float(np.expm1(np.log(df.close.iloc[-1] / df.close.iloc[0]) / yrs))
    # perda aberta maxima: pior ponto de cada deal (aprox. via minima do M1 dentro da deal, ordens ja feitas)
    worst = 0.0
    lo = m1.low.to_numpy(float)
    for a, b, mx in zip(res['MI'], res['MF'], res['mx']):
        worst = min(worst, (lo[a:b + 1].min() / mo[a] - 1))
    expo = float((res['MF'] - res['MI']).sum() / len(mo))
    # controle: mesmas deals iniciadas em barras sorteadas (mesmo numero de deals por ano)
    ctl = []
    rng = np.random.default_rng(8)
    for s in range(nsim):
        p = len(res['MI']) / len(df) * 3
        rnd = rng.random(len(df)) < p
        r2, _ = dca_run(name, df, m1, rnd=rnd, **kw)
        ctl.append(r2['pnl'].sum() / cap / yrs)
    ctl = np.array(ctl)
    return dict(deals=len(pnl), por_ano=len(pnl) / yrs, ann=ann, bh=bh, win=float((pnl > 0).mean()),
                dias=float(res['yrs_d'].mean() * 365), so_med=float(res['ns'].mean()),
                so_max=int(res['ns'].max()) if len(pnl) else 0, uso_med=float(res['mx'].mean() / cap),
                pior_queda=worst, expo=expo, ctl=float(ctl.mean()),
                t=float((ann - ctl.mean()) / (ctl.std(ddof=1) + 1e-12)))


# ------------------------------------------------------------------ 3. VWAP Trendfollow
def vwap_bands(df, mult=0.88, roll_h=17):
    o, h, l, c = ohlc(df)
    src = (h + l + c) / 3
    v = df.volume.to_numpy(float); v = np.where(v > 0, v, 1e-9)
    t = df.index.tz_convert('America/New_York') if df.index.tz is not None else df.index.tz_localize(
        'UTC').tz_convert('America/New_York')
    sess = (t - pd.Timedelta(hours=roll_h)).normalize().asi8
    g = pd.Series(sess)
    sv = pd.Series(v).groupby(g.values).cumsum().to_numpy()
    spv = pd.Series(v * src).groupby(g.values).cumsum().to_numpy()
    spv2 = pd.Series(v * src * src).groupby(g.values).cumsum().to_numpy()
    vw = spv / sv
    sd = np.sqrt(np.maximum(spv2 / sv - vw * vw, 0))
    return vw, sd, c


def run_vwap(name, df, mm, tag, rows=None, verbose=True, mult=0.88, matched=True, tpb=2.0, long_ok=True,
             short_ok=True, **extra):
    vw, sd, c = vwap_bands(df)
    u1, l1 = vw + mult * sd, vw - mult * sd
    u2, l2 = vw + tpb * mult * sd, vw - tpb * mult * sd
    upv = vw > np.concatenate([[NAN], vw[:-1]])
    L = T.xover(c, u1); S = T.xunder(c, l1)
    if matched:
        L &= upv; S &= ~upv
    XL = T.xunder(c, u2) if tpb > 0 else None
    XS = T.xover(c, l2) if tpb > 0 else None
    r = gsim(df, mm, L, S, XL, XS, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Engulfing + MA
def eng_signals(df, ma_len=32):
    o, h, l, c = ohlc(df)
    po = np.concatenate([[NAN], o[:-1]]); pc = np.concatenate([[NAN], c[:-1]])
    body = np.abs(c - o); pbody = np.abs(pc - po)
    g = c > o; r = c < o; pg = pc > po; pr = pc < po
    mxp, mnp = np.maximum(pc, po), np.minimum(pc, po); mx, mn = np.maximum(c, o), np.minimum(c, o)
    bull = (mxp < mx) & (body > pbody) & g & pr          # engolfo 1 ou 2 (min livre)
    bear = ((mxp < mx) & (mnp > mn) | (mxp >= mx) & (mnp > mn)) & (body > pbody) & r & pg
    bs_bull, bs_bear = T.barssince(bull), T.barssince(bear)
    eb = (bs_bull < bs_bear); es = (bs_bull > bs_bear)
    ma = T.sma(c, ma_len)
    bx, bu = T.barssince(T.xover(c, ma)), T.barssince(T.xunder(c, ma))
    mb = bx < bu; ms = bx > bu
    up = eb.astype(int) + mb.astype(int); dn = es.astype(int) + ms.astype(int)
    cu = (up == 2) & (np.roll(up, 1) < 2); cd = (dn == 2) & (np.roll(dn, 1) < 2)
    su, sd = T.barssince(cu), T.barssince(cd)
    sun, sdn = np.nan_to_num(su, nan=1e9), np.nan_to_num(sd, nan=1e9)
    nup = T.xunder(sun, sdn); ndn = T.xover(sun, sdn)
    XL = pc < ma; XS = pc > ma
    return nup, ndn, XL, XS


def run_eng(name, df, mm, tag, rows=None, verbose=True, ma_len=32, sl=0.0, tp=0.0, long_ok=True, short_ok=True,
            **extra):
    L, S, XL, XS = eng_signals(df, ma_len)
    r = gsim(df, mm, L, S, XL, XS, slp=sl, tpp=tp, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. BB Breakout
def run_bbb(name, df, mm, tag, rows=None, verbose=True, length=55, mult=1.0, long_ok=True, short_ok=True,
            **extra):
    o, h, l, c = ohlc(df)
    b = T.sma(c, length); d = mult * pd.Series(c).rolling(length).std(ddof=0).to_numpy()
    L1 = T.barssince(c > b + d); S1 = T.barssince(c < b - d)
    st = np.nan_to_num(L1, nan=1e9) < np.nan_to_num(S1, nan=1e9)
    ss = np.nan_to_num(S1, nan=1e9) < np.nan_to_num(L1, nan=1e9)
    L = st & ~np.roll(st, 1); S = ss & ~np.roll(ss, 1); L[0] = S[0] = False
    r = gsim(df, mm, L, S, S if not short_ok else None, L if not long_ok else None,
             long_ok=long_ok, short_ok=short_ok)
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

        print("\n### 1. TrendMaster Pro (SMA 9/21 + filtros, stop 1% alvo 2R, fecha 18h NY)")
        for tf in ['5min'] + TFS[:4]:
            df = cache[tf]
            run_tm(name, df, mm, f"{tf} TM default", rows, est='tm', TF=tf, cfg='sl1 rr2 eod filt')
            for sl, rr, eod, fil, side in itertools.product((0.0025, 0.005, 0.01, 0.02), (1.0, 2.0, 0.0),
                                                            (True, False), (True, False), ('ambos', 'long')):
                run_tm(name, df, mm, '', rows, False, sl=sl, rr=rr, eod=eod, filtros=fil, short_ok=side == 'ambos',
                       est='tm', TF=tf, cfg=f'sl{sl} rr{rr} eod{int(eod)} filt{int(fil)} {side}')

        print("\n### 3. VWAP Trendfollow (sessao, 0.88 desvio, saida na banda 2)")
        for tf in ['5min', '15min', '30min', '1h']:
            df = cache[tf]
            run_vwap(name, df, mm, f"{tf} VWAP default", rows, est='vwap', TF=tf, cfg='m0.88 matched tp2')
            for mu, mt, tpb, side in itertools.product((0.5, 0.88, 1.5, 2.0), (True, False), (2.0, 3.0, 0.0),
                                                       ('ambos', 'long')):
                run_vwap(name, df, mm, '', rows, False, mult=mu, matched=mt, tpb=tpb, short_ok=side == 'ambos',
                         est='vwap', TF=tf, cfg=f'm{mu} match{int(mt)} tp{tpb} {side}')

        print("\n### 4. Engulfing + SMA32")
        for tf in TFS:
            df = cache[tf]
            run_eng(name, df, mm, f"{tf} ENG default (sem stop)", rows, est='eng', TF=tf, cfg='ma32 sl0 tp0')
            for ma, sl, side in itertools.product((16, 32, 64, 128), (0.0, 0.005, 0.01, 0.02), ('ambos', 'long')):
                run_eng(name, df, mm, '', rows, False, ma_len=ma, sl=sl, tp=10 * sl, short_ok=side == 'ambos',
                        est='eng', TF=tf, cfg=f'ma{ma} sl{sl} tp{10 * sl} {side}')

        print("\n### 5. BB Breakout (SMA55 +- 1 desvio)")
        for tf in TFS:
            df = cache[tf]
            run_bbb(name, df, mm, f"{tf} BBB default", rows, est='bbb', TF=tf, cfg='len55 m1')
            for ln, mu, side in itertools.product((20, 55, 100, 200), (0.5, 1.0, 2.0), ('ambos', 'long')):
                run_bbb(name, df, mm, '', rows, False, length=ln, mult=mu, short_ok=side == 'ambos', est='bbb',
                        TF=tf, cfg=f'len{ln} m{mu} {side}')

        g = pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg'])
        g.to_csv(os.path.join(D, 'results', f'study_tvlote8_{name}_grid.csv'), index=False)
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

        print("\n### 2. 3commas DCA Bot v2 (RSI7<30, 6 SO, alvo 4,5%, sem stop; capital = 3009)")
        drows = []
        for tf in ['15min', '1h', '4h', '1D']:
            df = cache[tf]
            for thr, tp, dev, sl in itertools.product((30, 20, 101), (0.015, 0.045), (0.005, 0.015),
                                                      (0.0, 0.5)):
                kw = dict(rsi_thr=thr, tp=tp, dev=dev, sl=sl)
                res, mmin = dca_run(name, df, m1, **kw)
                if len(res['pnl']) < 10: continue
                s = dca_stats(name, df, m1, res, mmin, nsim=10, **kw)
                s.update(TF=tf, cfg=f'rsi<{thr} tp{tp} dev{dev} sl{sl}')
                drows.append(s)
                print(f"  {tf:5s} {s['cfg']:<32} {s['deals']:4d} deals ({s['por_ano']:5.1f}/a, {s['dias']:5.1f}d) "
                      f"win {s['win']:.0%} SO med {s['so_med']:.1f} max {s['so_max']} uso {s['uso_med']:.0%} | "
                      f"a.a. {s['ann']:+6.1%} vs B&H {s['bh']:+6.1%} | queda max {s['pior_queda']:+.0%} "
                      f"expo {s['expo']:.0%} | ctl {s['ctl']:+6.1%} t={s['t']:+5.2f}", flush=True)
        pd.DataFrame(drows).to_csv(os.path.join(D, 'results', f'study_tvlote8_{name}_dca.csv'), index=False)


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
