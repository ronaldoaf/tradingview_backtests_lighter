"""Lote 18 do TradingView (2026-10-23): 5 estrategias nos 5 ativos (ver docs/LOTE18_TV.md).

  1. [BACKTEST] Traders Dynamic Index (rDZ0Id1U, Pine v4)
     RSI13 com bandas (SMA34 +- 1,6185 desvios), linha rapida SMA2 e lenta SMA7 do RSI e canal de
     precos SMMA5 da maxima/minima. Long quando rapida > lenta, 22 < rapida < 78, maxima > SMMA da
     maxima e vela de alta, com forca 1 ou 2 (lenta acima do meio, ou rapida acima e lenta abaixo);
     short no espelho. Sinal contrario inverte. Sem stop/alvo por padrao.
  2. Dynamic Swing Anchored VWAP STRATEGY (gjFSGRCo, Pine v6)
     O VWAP so desenha; a ordem depende so da direcao do swing: comprado enquanto a maxima de 50
     barras e mais recente que a minima de 50 barras, fora caso contrario. Long-only (o 5x de
     alavancagem do script foi ignorado: 1 unidade).
  3. [RS] Open Session Breakout Trader (mIvVYU42, Pine v6)
     Na abertura de cada sessao (04-07 e 09-13, horario da bolsa; aqui UTC) marca o open; compra se a
     maxima rompe open + 0,25 x ATR100 diario (do dia anterior), vende se a minima rompe
     open - 0,25 x ATR. Uma posicao por vez, TP/SL de 250/100 ticks (virou % na proporcao 2,5:1).
     Martingale de tamanho ignorado.
  4. EMA Slope Trend Follower (TKg40Ska, Pine v4)
     Inclinacao da EMA130 (variacao %), EMA9 e EMA21 dela. Long com EMA9 > EMA21 da inclinacao e close
     > EMA200; sai quando a EMA9 cruza abaixo. Short no espelho.
  5. Liquidity Sweep Reversal (GoeqO1ev, Pine v6)
     Niveis de pivo (7/7) ainda nao varridos (ate 150 barras). Varredura = pavio passa do nivel e o
     close volta, com volume > 1,3 x SMA20 e pavio >= 1,5 x corpo. Confirmacao na barra seguinte
     (close alem do meio do pavio), sessao 12-16 (UTC aqui). Stop = pavio -+ 1,2 x ATR14, alvo 1,5R,
     risco minimo 0,5 ATR. O breakeven aos 50% do alvo nao foi reproduzido.

uso: python study_tvlote18.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote10 import shift

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)


def smma(x, n):
    out = np.full(len(x), NAN); s = T.sma(x, n)
    for i in range(len(x)):
        p = out[i - 1] if i else NAN
        out[i] = s[i] if p != p else (p * (n - 1) + x[i]) / n
    return out


# ------------------------------------------------------------------ 1. TDI
def run_tdi(name, df, mm, tag, rows=None, verbose=True, strength=2, rl=13, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    r = T.rsi_wilder(c, rl)
    ma = T.sma(r, 34); off = 1.6185 * roll(r, 34).std(ddof=0).to_numpy()
    mid = ma
    mab, mbb = T.sma(r, 2), T.sma(r, 7)
    sH, sL = smma(h, 5), smma(l, 5)
    baseL = (mab > mbb) & (mab < 78) & (mab > 22) & (h > sH) & (c > o)
    baseS = (mab < mbb) & (mab < 78) & (mab > 22) & (l < sL) & (c < o)
    lg = np.where(baseL, np.where(mbb > mid, 1, np.where((mab > mid) & (mbb < mid), 2, np.where((mab < mid) & (mbb < mid), 3, 0))), 0)
    sg = np.where(baseS, np.where(mbb < mid, 1, np.where((mab < mid) & (mbb > mid), 2, np.where((mab > mid) & (mbb > mid), 3, 0))), 0)
    L = (lg > 0) & (lg != np.concatenate([[0], lg[:-1]])) & (lg <= strength)
    S = (sg > 0) & (sg != np.concatenate([[0], sg[:-1]])) & (sg <= strength)
    r_ = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r_, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Swing AVWAP (direcao do swing)
def run_savwap(name, df, mm, tag, rows=None, verbose=True, prd=50, shorts=False, **extra):
    o, h, l, c = ohlc(df)
    n = len(c)
    hb = roll(h, prd).apply(np.argmax, raw=True).to_numpy()   # posicao do maximo na janela
    lb = roll(l, prd).apply(np.argmin, raw=True).to_numpy()
    newH = hb == prd - 1; newL = lb == prd - 1                   # highestbars == 0
    phL = np.zeros(n); plL = np.zeros(n); a = b = 0
    for i in range(n):
        if newH[i]: a = i
        if newL[i]: b = i
        phL[i], plL[i] = a, b
    d = np.where(phL > plL, 1, -1)
    up = d > 0; prev = np.concatenate([[False], up[:-1]])
    L = up & ~prev; X = ~up & prev
    if shorts:
        r = gsim(df, mm, L, X, rev=True)
    else:
        r = gsim(df, mm, L, np.zeros_like(L), X, None, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Open Session Breakout
def run_osb(name, df, mm, daily, tag, rows=None, verbose=True, mult=0.25, sl=0.005, sessions=((4, 7), (9, 13)),
            long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    hr = df.index.hour + df.index.minute / 60
    ins = np.zeros(len(c), bool)
    for a, b in sessions:
        ins |= np.asarray((hr >= a) & (hr < b))
    start = ins & ~np.concatenate([[False], ins[:-1]])
    atr_d = T.atr_rma(daily.high.to_numpy(float), daily.low.to_numpy(float), daily.close.to_numpy(float), 100)
    atr_prev = pd.Series(atr_d, index=daily.index + pd.Timedelta('1D')).reindex(df.index, method='ffill').to_numpy()
    op = np.full(len(c), NAN); cur = NAN
    for i in range(len(c)):
        if start[i]: cur = o[i]
        op[i] = cur
    bl, sl_line = op + atr_prev * mult, op - atr_prev * mult
    is_new = start
    bt = T.xover(h, bl) | (is_new & (h > bl)); st = T.xunder(l, sl_line) | (is_new & (l < sl_line))
    L = ins & bt; S = ins & st & ~L
    r = gsim(df, mm, L, S, slp=sl, tpp=sl * 2.5, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. EMA Slope
def run_slope(name, df, mm, tag, rows=None, verbose=True, ln=130, f=9, s=21, trend=True, long_ok=True, short_ok=True,
              **extra):
    o, h, l, c = ohlc(df)
    out = ema(c, ln)
    with np.errstate(divide='ignore', invalid='ignore'):
        slp = np.nan_to_num(np.diff(out, prepend=out[0]) / out)
    ef, es = ema(slp, f), ema(slp, s)
    e200 = ema(c, 200)
    L = ef > es; S = ef < es
    if trend:
        L = L & (c > e200); S = S & (c < e200)
    XL, XS = T.xunder(ef, es), T.xover(ef, es)
    L[:200] = S[:200] = False
    r = gsim(df, mm, L, S, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Liquidity Sweep Reversal
def run_sweep(name, df, mm, tag, rows=None, verbose=True, piv=7, rr=1.5, use_vol=True, use_sess=True, confirm=True,
              long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    v = df.volume.to_numpy(float); n = len(c)
    atr = T.atr_rma(h, l, c, 14); vs = T.sma(v, 20)
    ph = T.pivothigh(h, piv, piv); pl = T.pivotlow(l, piv, piv)
    hr = df.index.hour + df.index.minute / 60
    sess = np.asarray((hr >= 12) & (hr < 16)) if use_sess else np.ones(n, bool)
    highs, lows = [], []                    # [preco, barra]
    L = np.zeros(n, bool); S = np.zeros(n, bool)
    SLL = np.full(n, NAN); TPL = np.full(n, NAN); SLS = np.full(n, NAN); TPS = np.full(n, NAN)
    pend_l = pend_s = False; pw = pm = NAN
    for i in range(n):
        a = atr[i]
        if a != a:
            continue
        if ph[i]:
            px = h[i - piv]
            if all(abs(x[0] - px) >= a * 0.25 for x in highs): highs.append([px, i - piv])
        if pl[i]:
            px = l[i - piv]
            if all(abs(x[0] - px) >= a * 0.25 for x in lows): lows.append([px, i - piv])
        body = abs(c[i] - o[i]); volok = (not use_vol) or (v[i] > vs[i] * 1.3)
        swh = False; wh = NAN
        uw = h[i] - max(c[i], o[i]); lw = min(c[i], o[i]) - l[i]
        okh = (body > 0 and uw / body >= 1.5) or (body == 0 and uw > 0)
        okl = (body > 0 and lw / body >= 1.5) or (body == 0 and lw > 0)
        keep = []
        for lv in highs:
            if h[i] > lv[0] and c[i] < lv[0] and volok and okh:
                swh = True; wh = h[i] if wh != wh else max(wh, h[i])
            elif i - lv[1] > 150:
                pass
            else:
                keep.append(lv)
        highs = keep
        swl = False; wl = NAN; keep = []
        for lv in lows:
            if l[i] < lv[0] and c[i] > lv[0] and volok and okl:
                swl = True; wl = l[i] if wl != wl else min(wl, l[i])
            elif i - lv[1] > 150:
                pass
            else:
                keep.append(lv)
        lows = keep
        doL = doS = False; wick = NAN
        if confirm:
            if pend_l and c[i] > pm and sess[i]: doL, wick = True, pw
            if pend_s and c[i] < pm and sess[i]: doS, wick = True, pw
            pend_l = pend_s = False
            if swl: pend_l, pw, pm = True, wl, (wl + c[i]) / 2
            if swh: pend_s, pw, pm = True, wh, (wh + c[i]) / 2
        else:
            if swl and sess[i]: doL, wick = True, wl
            if swh and sess[i]: doS, wick = True, wh
        if doL or doS:
            isl = doL
            stp = wick - a * 1.2 if isl else wick + a * 1.2
            risk = c[i] - stp if isl else stp - c[i]
            if risk >= a * 0.5:
                if isl:
                    L[i] = True; SLL[i] = stp; TPL[i] = c[i] + risk * rr
                else:
                    S[i] = True; SLS[i] = stp; TPS[i] = c[i] - risk * rr
    r = gsim(df, mm, L, S, SLL=SLL, TPL=TPL, SLS=SLS, TPS=TPS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. Traders Dynamic Index (forca 1-2)")
        for tf in TFS:
            df = cache[tf]
            run_tdi(name, df, mm, f"{tf} TDI default", rows, est='tdi', TF=tf, cfg='str2 ambos')
            for stg, side in itertools.product((1, 2, 3), side2):
                run_tdi(name, df, mm, '', rows, False, strength=stg, short_ok=side == 'ambos', est='tdi', TF=tf,
                        cfg=f'str{stg} {side}')

        print("\n### 2. Swing Anchored VWAP (direcao do swing de 50 barras, long-only)")
        for tf in TFS:
            df = cache[tf]
            run_savwap(name, df, mm, f"{tf} SAVWAP default", rows, est='savwap', TF=tf, cfg='prd50 long')
            for prd, sh in itertools.product((20, 50, 100), (False, True)):
                run_savwap(name, df, mm, '', rows, False, prd=prd, shorts=sh, est='savwap', TF=tf,
                           cfg=f'prd{prd} ' + ('ambos' if sh else 'long'))

        print("\n### 3. Open Session Breakout (open da sessao +- 0,25 ATR100 diario)")
        daily = cache['1D']
        for tf in ['15min', '30min', '1h']:
            df = cache[tf]
            run_osb(name, df, mm, daily, f"{tf} OSB default", rows, est='osb', TF=tf, cfg='m0.25 sl0.5% ambos')
            for mu, sl, side in itertools.product((0.25, 0.5), (0.0025, 0.005, 0.01, 0.02), side2):
                run_osb(name, df, mm, daily, '', rows, False, mult=mu, sl=sl, short_ok=side == 'ambos', est='osb',
                        TF=tf, cfg=f'm{mu} sl{sl:.2%} {side}')

        print("\n### 4. EMA Slope Trend Follower (EMA130, inclinacao 9/21, filtro EMA200)")
        for tf in TFS:
            df = cache[tf]
            run_slope(name, df, mm, f"{tf} SLOPE default", rows, est='slope', TF=tf, cfg='130 9/21 filtro ambos')
            for ln, tr, side in itertools.product((50, 130), (True, False), side2):
                run_slope(name, df, mm, '', rows, False, ln=ln, trend=tr, short_ok=side == 'ambos', est='slope', TF=tf,
                          cfg=f'{ln} 9/21 ' + ('filtro' if tr else 'semfiltro') + f' {side}')

        print("\n### 5. Liquidity Sweep Reversal (pivo 7, vol, pavio, confirmacao, sessao 12-16)")
        for tf in ['15min', '30min', '1h', '4h']:
            df = cache[tf]
            run_sweep(name, df, mm, f"{tf} SWEEP default", rows, est='sweep', TF=tf, cfg='rr1.5 vol sess ambos')
            for rr, ses, vol in itertools.product((1.0, 1.5, 3.0), (True, False), (True, False)):
                run_sweep(name, df, mm, '', rows, False, rr=rr, use_sess=ses, use_vol=vol, est='sweep', TF=tf,
                          cfg=f'rr{rr} ' + ('vol' if vol else 'semvol') + ' ' + ('sess' if ses else '24h') + ' ambos')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote18')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
