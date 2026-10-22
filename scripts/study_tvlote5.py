"""Lote 5 do TradingView (2026-10-21): 3 estrategias de rompimento/confluencia.

  1. Price and Volume Breakout Buy Strategy (TradeDots, jc2hs2qK, Pine v5)
     Long quando close > maxima de 60 barras E volume > maximo de volume de 60 barras E
     close > SMA(200), so com a carteira zerada. Saida: 5 closes seguidos abaixo da SMA(200).
     Default so long (o short espelhado e opcional).
  2. QQE MOD + SSL Hybrid + Waddah Attar Explosion (YCob5r03, Pine v5)
     Entrada na primeira barra azul do QQE MOD (QQE2 > +3 e RsiMa-50 > banda de Bollinger do
     QQE1), com close acima do canal Keltner de HMA(60) e explosao WAE (delta MACD*180 > largura
     da BB). Stop fixo na minima/maxima de 10 barras da barra do sinal; saida quando o close cruza
     a linha SSL de saida (HMA 15) contra o trade E o trade esta no lucro.
     A JMA do SSL2 nao entra em nenhuma condicao e nao foi implementada.
  3. Full CRYPTO pack macd-rsi-obv-ema (SoftKill21, DbRYTl6G, Pine v4)
     Long quando close > EMA9(hl2) subindo, close subindo, histograma MACD(hl2) vira positivo,
     OBV > SMA10(OBV). Saida no sinal espelhado. O RSI < 100 e sempre verdadeiro. Os security()
     so existem com Heikin Ashi ligado (default desligado), sem vazamento.

Execucao: sinal no fechamento, ordem na ABERTURA seguinte; o stop do QQE e resolvido na barra do
grafico (gap pula o stop -> sai na abertura). Filtros de data dos scripts ignorados (periodo todo).
Tamanho 1x nocional (o QQE publicado arrisca 2% da conta por trade; isso so escala o resultado).

uso: python study_tvlote5.py [xau us100 wti btc eth]   (ESTS=pvb,qqe,crypto)
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_zigzagpa import _sim  # noqa: F401 (o import instala o controle vetorizado)
from study_tvlote4 import lag, trades_frame, finish, run_sig

TFS = ['15min', '30min', '1h', '4h', '1D']


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


def roll_max(x, n):
    return pd.Series(x).rolling(n).max().to_numpy()


def roll_min(x, n):
    return pd.Series(x).rolling(n).min().to_numpy()


@njit(cache=True)
def _sim_flat(le, lx, se, sx):
    """Como _sim, mas so entra com a carteira zerada (strategy.opentrades == 0): sem virada."""
    n = len(le); pos = 0; i0 = -1
    ei = np.empty(n, np.int64); ej = np.empty(n, np.int64); es = np.empty(n, np.int64); k = 0
    for i in range(n - 1):
        new = pos
        if pos == 0:
            if le[i]: new = 1
            elif se[i]: new = -1
        elif pos == 1:
            if lx[i]: new = 0
        else:
            if sx[i]: new = 0
        if new != pos:
            if pos != 0:
                ei[k] = i0; ej[k] = i + 1; es[k] = pos; k += 1
            pos = new; i0 = i + 1
    return ei[:k], ej[:k], es[:k]


def run_flat(name, df, le, lx, se, sx, tag, rows=None, verbose=True, **extra):
    ei, ej, es = _sim_flat(le, lx, se, sx)
    tr = T.book(df, list(zip(ei, ej, es)), name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 1. Price and Volume Breakout
def pvb_signals(df, pp=60, vp=60, tl=200, nx=5, use_vol=True):
    c = df.close.to_numpy(float); v = df.volume.to_numpy(float)
    ma = T.sma(c, tl)
    vol_ok = (v > lag(roll_max(v, vp))) if use_vol else True
    le = (c > lag(roll_max(c, pp))) & vol_ok & (c > ma)
    se = (c < lag(roll_min(c, pp))) & vol_ok & (c < ma)
    below = c < ma; above = c > ma
    lx = np.ones(len(c), bool); sx = np.ones(len(c), bool)
    for k in range(nx):
        lx &= np.r_[np.zeros(k, bool), below[:len(c) - k]]
        sx &= np.r_[np.zeros(k, bool), above[:len(c) - k]]
    return le, lx, se, sx


# ------------------------------------------------------------------ 2. QQE MOD + SSL + WAE
@njit(cache=True)
def _qqe_trend(rs, dar):
    n = len(rs); LB = np.zeros(n); SB = np.zeros(n); TR = np.ones(n); TL = np.full(n, np.nan)
    for i in range(1, n):
        nsb = rs[i] + dar[i]; nlb = rs[i] - dar[i]
        if rs[i - 1] > LB[i - 1] and rs[i] > LB[i - 1]:
            LB[i] = max(LB[i - 1], nlb)
        else:
            LB[i] = nlb
        if rs[i - 1] < SB[i - 1] and rs[i] < SB[i - 1]:
            SB[i] = min(SB[i - 1], nsb)
        else:
            SB[i] = nsb
        if LB[i] != LB[i] or SB[i] != SB[i]:   # aquecimento: o Pine fica em na ate dar existir
            LB[i] = 0.0 if LB[i] != LB[i] else LB[i]; SB[i] = 0.0 if SB[i] != SB[i] else SB[i]
            continue
        # ta.cross(RSIndex, shortband[1]) e ta.cross(longband[1], RSIndex), ambos os sentidos
        a0 = rs[i - 1] - SB[i - 2] if i >= 2 else np.nan; a1 = rs[i] - SB[i - 1]
        b0 = LB[i - 2] - rs[i - 1] if i >= 2 else np.nan; b1 = LB[i - 1] - rs[i]
        if a0 == a0 and ((a0 <= 0 and a1 > 0) or (a0 >= 0 and a1 < 0)):
            TR[i] = 1
        elif b0 == b0 and ((b0 <= 0 and b1 > 0) or (b0 >= 0 and b1 < 0)):
            TR[i] = -1
        else:
            TR[i] = TR[i - 1]
        TL[i] = LB[i] if TR[i] == 1 else SB[i]
    return TL


def _qqe(c, rsi_p, sf, q):
    rsma = ema(T.rsi_wilder(c, rsi_p), sf)
    wp = rsi_p * 2 - 1
    dar = ema(ema(np.abs(lag(rsma) - rsma), wp), wp) * q
    return rsma, dar


def hma_pine(x, n):
    """ma('HMA') do script: wma(2*wma(x, n/2) - wma(x, n), round(sqrt(n)))."""
    return T.wma(2 * T.wma(x, max(1, int(n / 2))) - T.wma(x, n), max(1, int(round(np.sqrt(n)))))


@njit(cache=True)
def _hlv(c, hi, lo):
    n = len(c); out = np.zeros(n)
    for i in range(n):
        p = out[i - 1] if i else 0.0
        out[i] = 1.0 if c[i] > hi[i] else (-1.0 if c[i] < lo[i] else p)
    return out


def qqe_setup(df, base_len=60, exit_len=15, sens=180, multy=0.2):
    c, h, l = (df[k].to_numpy(float) for k in ('close', 'high', 'low'))
    rsma, dar = _qqe(c, 6, 6, 3.0)
    tl = _qqe_trend(rsma, dar) - 50
    basis = T.sma(tl, 50); dev = 0.35 * T.stdev_pop(tl, 50)
    rsma2, _ = _qqe(c, 6, 5, 1.61)
    green = (rsma2 - 50 > 3) & (rsma - 50 > basis + dev)
    red = (rsma2 - 50 < -3) & (rsma - 50 < basis - dev)
    qb = green & ~np.r_[False, green[:-1]]
    qs = red & ~np.r_[False, red[:-1]]
    bbmc = hma_pine(c, base_len)
    pc = lag(c); tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    rng = ema(np.where(np.isnan(tr), h - l, tr), base_len)
    upk = bbmc + rng * multy; lok = bbmc - rng * multy
    ssl_b = (c > upk) & (c > bbmc); ssl_s = (c < lok) & (c < bbmc)
    macd = ema(c, 20) - ema(c, 40)
    t1 = (macd - lag(macd)) * sens
    e1 = 2 * 2.0 * T.stdev_pop(c, 20)
    wae_b = (t1 > 0) & (t1 > e1); wae_s = (t1 < 0) & (-t1 > e1)
    eh, el = hma_pine(h, exit_len), hma_pine(l, exit_len)
    hl3 = _hlv(c, eh, el)
    ssl_exit = np.where(hl3 < 0, eh, el)
    return dict(qb=qb, qs=qs, ssl_b=ssl_b, ssl_s=ssl_s, wae_b=wae_b, wae_s=wae_s,
                xl=T.xover(ssl_exit, c), xs=T.xover(c, ssl_exit), c=c, h=h, l=l)


@njit(cache=True)
def _sim_qqe(o, h, l, c, le, se, lst, sst, xl, xs, need_profit, long_ok, short_ok):
    """Entrada na abertura seguinte so com carteira zerada; stop fixo calculado na barra do sinal
    e ativo desde a barra de entrada; saida a mercado quando o close cruza a SSL de saida contra
    o trade e o trade esta no lucro nesse close."""
    n = len(o); pos = 0; i0 = -1; pin = 0.0; pend = 0; stp = np.nan; nst = np.nan; xpend = False
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n); k = 0
    for j in range(1, n):
        if xpend and pos != 0:
            EI[k] = i0; EJ[k] = j; ES[k] = pos; PI[k] = pin; PO[k] = o[j]; k += 1; pos = 0
        xpend = False
        if pend != 0 and pos == 0:
            pos = pend; i0 = j; pin = o[j]; stp = nst
        pend = 0
        if pos == 1 and stp == stp and l[j] <= stp:
            EI[k] = i0; EJ[k] = j; ES[k] = 1; PI[k] = pin; PO[k] = min(o[j], stp); k += 1; pos = 0
        elif pos == -1 and stp == stp and h[j] >= stp:
            EI[k] = i0; EJ[k] = j; ES[k] = -1; PI[k] = pin; PO[k] = max(o[j], stp); k += 1; pos = 0
        if pos == 1 and xl[j] and (not need_profit or c[j] > pin): xpend = True
        elif pos == -1 and xs[j] and (not need_profit or c[j] < pin): xpend = True
        if pos == 0:
            if le[j] and long_ok: pend = 1; nst = lst[j]
            elif se[j] and short_ok: pend = -1; nst = sst[j]
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_qqe(name, df, S, tag, rows=None, verbose=True, swing=10, use_wae=True, need_profit=True,
            long_ok=True, short_ok=True, **extra):
    wb = S['wae_b'] if use_wae else True; ws = S['wae_s'] if use_wae else True
    le = S['qb'] & S['ssl_b'] & wb; se = S['qs'] & S['ssl_s'] & ws
    o = df.open.to_numpy(float)
    ei, ej, es, pi, po = _sim_qqe(o, S['h'], S['l'], S['c'], le, se, roll_min(S['l'], swing),
                                  roll_max(S['h'], swing), S['xl'], S['xs'], need_profit,
                                  long_ok, short_ok)
    tr = trades_frame(df, ei, ej, es, pi, po, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 3. Full CRYPTO pack
def crypto_signals(df, ln=9, fast=12, slow=26, sig=9, obv_len=10, use_obv=True):
    c, h, l = (df[k].to_numpy(float) for k in ('close', 'high', 'low'))
    v = df.volume.to_numpy(float)
    src = (h + l) / 2
    out = ema(src, ln)
    macd = ema(src, fast) - ema(src, slow)
    hist = macd - ema(macd, sig)
    obv = np.cumsum(np.sign(np.diff(c, prepend=c[0])) * v)
    ob_up = (obv > T.sma(obv, obv_len)) if use_obv else True
    ob_dn = (obv < T.sma(obv, obv_len)) if use_obv else True
    rsi = T.rsi_wilder(c, 14)
    pc, po_ = lag(c), lag(out); ph = lag(hist)
    long = (c > out) & (c > pc) & (out > po_) & (hist > 0) & (ph < 0) & (rsi < 100) & ob_up
    short = (c < out) & (c < pc) & (out < po_) & (hist < 0) & (ph > 0) & (rsi > 35) & ob_dn
    return long, short


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        ests = os.environ.get('ESTS', 'pvb,qqe,crypto').split(',')
        Z = lambda x: np.zeros_like(x)

        if 'pvb' in ests: print("\n### 1. Price and Volume Breakout (60/60/200, so long)")
        for tf in (TFS if 'pvb' in ests else []):
            df = cache[tf]
            le, lx, se, sx = pvb_signals(df)
            run_flat(name, df, le, lx, Z(se), sx, f"{tf} PVB default", rows, est='pvb', TF=tf,
                     cfg='60/60/200 so long')
            run_flat(name, df, le, lx, se, sx, f"{tf} PVB long+short", rows, est='pvb', TF=tf,
                     cfg='60/60/200 ls')
            for pp, tl, nx, vol, lo in itertools.product((20, 60, 120), (50, 100, 200), (1, 5),
                                                         (True, False), (True, False)):
                le, lx, se, sx = pvb_signals(df, pp, pp, tl, nx, vol)
                run_flat(name, df, le, lx, Z(se) if lo else se, sx, '', rows, verbose=False,
                         est='pvb', TF=tf, cfg=f'{pp}/{tl} x{nx} vol{int(vol)}' + (' so long' if lo else ' ls'))

        if 'qqe' in ests: print("\n### 2. QQE MOD + SSL Hybrid + WAE")
        for tf in (TFS if 'qqe' in ests else []):
            df = cache[tf]
            for bl, xl_, sens in itertools.product((60, 30), (15, 30), (180, 90)):
                S = qqe_setup(df, bl, xl_, sens)
                for sw, wae, prof, lo in itertools.product((10, 20), (True, False), (True, False),
                                                           (False, True)):
                    dflt = bl == 60 and xl_ == 15 and sens == 180 and sw == 10 and wae and prof
                    cfg = f'b{bl} x{xl_} s{sens} sw{sw} wae{int(wae)} lucro{int(prof)}' + (' so long' if lo else '')
                    run_qqe(name, df, S, f"{tf} {cfg}", rows, verbose=dflt, swing=sw, use_wae=wae,
                            need_profit=prof, short_ok=not lo, est='qqe', TF=tf, cfg=cfg)

        if 'crypto' in ests: print("\n### 3. Full CRYPTO pack (EMA9 hl2, MACD 12/26/9, OBV 10)")
        for tf in (TFS if 'crypto' in ests else []):
            df = cache[tf]
            L, Sg = crypto_signals(df)
            run_sig(name, df, L, Sg, Z(L), Z(L), f"{tf} CRYPTO default", rows, est='crypto', TF=tf,
                    cfg='9 12/26/9 obv10 so long')
            run_sig(name, df, L, Z(L), Sg, Z(L), f"{tf} CRYPTO long+short", rows, est='crypto', TF=tf,
                    cfg='9 12/26/9 obv10 ls')
            for ln, (fa, sl, sg), obv, lo in itertools.product((9, 21, 50), ((12, 26, 9), (24, 52, 18)),
                                                               (True, False), (True, False)):
                L, Sg = crypto_signals(df, ln, fa, sl, sg, use_obv=obv)
                if lo: run_sig(name, df, L, Sg, Z(L), Z(L), '', rows, verbose=False, est='crypto', TF=tf,
                               cfg=f'{ln} {fa}/{sl}/{sg} obv{int(obv)} so long')
                else: run_sig(name, df, L, Z(L), Sg, Z(L), '', rows, verbose=False, est='crypto', TF=tf,
                              cfg=f'{ln} {fa}/{sl}/{sg} obv{int(obv)} ls')

        g = pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg'])
        g.to_csv(os.path.join(D, 'results', f'study_tvlote5_{name}_grid.csv'), index=False)
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
