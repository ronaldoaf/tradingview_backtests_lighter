"""Lote 26 do TradingView (2026-10-23): 20 estrategias nos 5 ativos, grade completa como nos lotes 21-24
(ver docs/LOTE26_TV.md, com as puladas na ordem da lista).

uso: python study_tvlote26.py xau us100 wti btc eth
"""
import os, sys, itertools, math
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote20 import sh, tr_, _st, heikin
from study_tvlote21 import linreg
from study_tvlote22 import run_stp, macd
from study_tvlote24 import cci
from study_tvlote25 import run_loop, posflat, wilder_rsi, hh, ll, ffill, full, ITF, Z, NAN, roll


def flat_pos(t, long_ok, short_ok):
    return np.where(t == 1, 1, np.where(short_ok, -1, 0)) if long_ok else np.where(t == -1, -1, 0)


# ------------------------------------------------------------------ 1. 5 EMA
def run_e5(name, df, mm, tag, rows=None, verbose=True, rr=1.5, long_ok=True, short_ok=True, **extra):
    """A ultima barra toda abaixo da EMA5 marca a maxima de gatilho (toda acima marca a minima); rompeu -> entra
    se estiver fora; stop na menor minima das 2 ultimas barras (maior maxima no short), alvo 1,5R. O limite de
    4 trades por dia foi ignorado."""
    o, h, l, c = ohlc(df); e = ema(c, 5)
    hi = ffill(np.where(h < e, h, NAN)); lo = ffill(np.where(l > e, l, NAN))
    L = h > sh(hi); S = (l < sh(lo)) & ~L
    sll = np.fmin(l, sh(l)); sls = np.fmax(h, sh(h))
    r = gsim(df, mm, L, S, SLL=sll, TPL=c + rr * (c - sll), SLS=sls, TPS=c - rr * (sls - c), rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Vegas SuperTrend Enhanced
def run_vst(name, df, mm, tag, rows=None, verbose=True, base=5.0, long_ok=True, short_ok=True, **extra):
    """SuperTrend no hlc3 com ATR10 e multiplicador base + base x (2 x desvio100 / media100); sempre na direcao."""
    o, h, l, c = ohlc(df); sd = roll(c, 100).std(ddof=0).to_numpy()
    m = base + base * (2 * sd / T.sma(c, 100)); a = np.nan_to_num(T.atr_rma(h, l, c, 10) * m)
    t = _st((h + l + c) / 3, c, a, 1.0)[0]
    return run_g(name, df, posflat(df, mm, flat_pos(t, long_ok, short_ok), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Crypto Squeeze
def run_csq(name, df, mm, tag, rows=None, verbose=True, mfl=58, long_ok=True, short_ok=True, **extra):
    """BlueWave = linreg(close - media(media(maxima20, minima20), SMA20), 20); fluxo = (MFI(hlc3) - 50) x 3.
    BlueWave cruza 0 para cima com fluxo > 0 compra, espelho vende, inverte. SL/TP de 50% (na pratica nenhum)."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float)
    bw = linreg(c - ((hh(h, 20) + ll(l, 20)) / 2 + T.sma(c, 20)) / 2, 20)
    mf = (T.mfi((h + l + c) / 3, v, mfl) - 50) * 3
    L = T.xover(bw, 0 * c) & (mf > 0); S = T.xunder(bw, 0 * c) & (mf < 0)
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok, slp=0.5, tpp=0.5)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. MACD + EMA (long-only)
def run_mel(name, df, mm, tag, rows=None, verbose=True, filt=True, f=12, s=26, **extra):
    """So long: MACD acima do sinal compra (abaixo da SMA200 exige close > EMA20); sai com MACD abaixo do sinal
    (acima da SMA200 exige close < EMA20)."""
    o, h, l, c = ohlc(df); m, sg = macd(c, f, s); d = m - sg
    e20, s200 = ema(c, 20), T.sma(c, 200)
    L, X = d > 0, d < 0
    if filt:
        L = L & ((c >= s200) | (c > e20)); X = X & ((c < s200) | (c < e20))
    r = gsim(df, mm, L, Z(c), X, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. SuperTrend STRATEGY
def run_sts(name, df, mm, tag, rows=None, verbose=True, mult=8.5, long_ok=True, short_ok=False, **extra):
    """SuperTrend no hl2 com ATR = SMA(TR, 10) e multiplicador 8,5; o original so compra na virada para cima e
    fecha na virada para baixo."""
    o, h, l, c = ohlc(df); a = np.nan_to_num(T.sma(tr_(h, l, c), 10))
    t = _st((h + l) / 2, c, a, mult)[0]
    return run_g(name, df, posflat(df, mm, flat_pos(t, long_ok, short_ok), long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. B-Xtrender
def run_bx(name, df, mm, tag, rows=None, verbose=True, trl=0.2, long_ok=True, short_ok=True, **extra):
    """curto = RSI15(EMA5 - EMA20) - 50, longo = RSI15(EMA20) - 50. Os dois > 0 com close > EMA200 compra; sai
    quando qualquer um fica < 0 ou o close recua 20% do maior close (espelho no short)."""
    o, h, l, c = ohlc(df); e200 = ema(c, 200)
    xs = wilder_rsi(ema(c, 5) - ema(c, 20), 15) - 50; xl = wilder_rsi(ema(c, 20), 15) - 50
    L = (xs > 0) & (xl > 0) & (c > e200); S = (xs < 0) & (xl < 0) & (c < e200)
    def ex(j, s, e, st):
        if s == 1:
            if xs[j] < 0 or xl[j] < 0: return 2, None
            pk = st['pk'] = max(st.get('pk', e), c[j])
            if c[j] < pk * (1 - trl): return 2, None
        else:
            if xs[j] > 0 or xl[j] > 0: return 2, None
            pk = st['pk'] = min(st.get('pk', e), c[j])
            if c[j] > pk * (1 + trl): return 2, None
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, S, ex, True, long_ok, short_ok)


# ------------------------------------------------------------------ 7. Hull + Ichimoku + MACD
def run_him(name, df, mm, tag, rows=None, verbose=True, keh=12, long_ok=True, short_ok=True, **extra):
    """Hull duplo (12) contra o mesmo Hull um candle atras, Ichimoku 9/24/51 com nuvem deslocada 23 e MACD
    12/24/9; entradas e fechamentos com as condicoes do script, inverte."""
    o, h, l, c = ohlc(df); k2, sq = round(keh / 2), round(math.sqrt(keh))
    hull = lambda x: T.wma(2 * T.wma(x, k2) - T.wma(x, keh), sq)
    n1, n2 = hull(c), hull(sh(c))
    dc = lambda n: (hh(h, n) + ll(l, n)) / 2
    tk, kj, sb = dc(9), dc(24), dc(51); sa = (tk + kj) / 2
    sH, sL = np.fmax(sh(sa, 23), sh(sb, 23)), np.fmin(sh(sa, 23), sh(sb, 23))
    m = ema(c, 12) - ema(c, 24); am = ema(m, 9)
    L = (n1 > n2) & (c > n2) & (c > sH) & (m > am) & ((tk > kj) | (c > kj))
    S = (n1 < n2) & (c < n2) & (c < sL) & ((m < am) | (tk < kj) | (c < tk) | (c < kj))
    XL = (n1 < n2) & (c < n2) & ((m < am) | (tk < kj) | (c < tk) | (c < kj) | (c < sL))
    XS = (n1 > n2) & (c > n2) & ((m > am) | (tk > kj) | (c > tk) | (c > kj) | (c > sH))
    r = gsim(df, mm, L, S & ~L, XL, XS, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 8. QuantCat Intraday
def run_qc(name, df, mm, tag, rows=None, verbose=True, sm=4.0, long_ok=True, short_ok=True, **extra):
    """SMA25/SMA100 com no maximo 10 cruzamentos do close na SMA25 em 25 barras: cruzamento das medias (agressivo)
    ou recuo entre elas (conservador) entra, inverte; stop fixo de 4 ATR14 a partir da entrada."""
    o, h, l, c = ohlc(df); f, s = T.sma(c, 25), T.sma(c, 100); a = T.atr_rma(h, l, c, 14)
    cr = (T.xover(c, f) | T.xunder(c, f)).astype(float); ok = roll(cr, 25).sum().to_numpy() <= 10
    L = ok & (T.xover(f, s) | ((c < f) & (c > s) & (f > s)))
    S = ok & (T.xunder(f, s) | ((c > f) & (c < s) & (f < s)))
    r = gsim(df, mm, L, S & ~L, SLL=c - sm * a, SLS=c + sm * a, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. KSR
def run_ksr(name, df, mm, tag, rows=None, verbose=True, f=10, s=20, long_ok=True, short_ok=True, **extra):
    """EMA10 cruza a EMA20: compra/vende, inverte (os security do script so desenham)."""
    o, h, l, c = ohlc(df); a, b = ema(c, f), ema(c, s)
    r = gsim(df, mm, T.xover(a, b), T.xunder(a, b), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. KAMA Strategy (long-only)
def kama(x, n, fa, sa):
    x = np.asarray(x, float); mom = np.abs(x - sh(x, n))
    vol = roll(np.abs(np.diff(x, prepend=NAN)), n).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        er = np.where(vol != 0, mom / vol, 0.0)
    sc = (er * (2 / (fa + 1) - 2 / (sa + 1)) + 2 / (sa + 1)) ** 2
    out = np.zeros(len(x)); k = 0.0
    for i in range(len(x)):
        if sc[i] == sc[i]: k = sc[i] * x[i] + (1 - sc[i]) * k
        out[i] = k
    return out


def run_kama(name, df, mm, tag, rows=None, verbose=True, ef=1.0, atrs=False, **extra):
    """So long: delta da KAMA(14, 2, 20) > 0 e maior que 1 desvio(14) do delta compra; delta < 0 e |delta| maior
    que 0,5 desvio vende. atrs: stop movel de 3 ATR14 pela maxima (opcao do script)."""
    o, h, l, c = ohlc(df); k = kama(c, 14, 2, 20); d = k - sh(k); sd = roll(d, 14).std(ddof=1).to_numpy()
    L = (d > 0) & (d > ef * sd); X = (d < 0) & (np.abs(d) > 0.5 * sd); a = T.atr_rma(h, l, c, 14)
    def ex(j, s, e, st):
        lv = st.get('lv', -1e18)
        if l[j] <= lv: return 1, min(o[j], lv)
        st['lv'] = max(lv, h[j] - 3 * a[j])
        return (2, None) if X[j] else (0, None)
    def ex0(j, s, e, st):
        return (2, None) if X[j] else (0, None)
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex if atrs else ex0, False, True, False)


# ------------------------------------------------------------------ 11. NSDT HAMA
def run_hama(name, df, mm, tag, rows=None, verbose=True, ln=55, long_ok=True, short_ok=True, **extra):
    """EMA55 subindo 2 barras seguidas compra, caindo 2 vende, inverte (ADX > 0 nao filtra; a janela de 2022 foi
    ignorada)."""
    o, h, l, c = ohlc(df); e = ema(c, ln)
    L = (e > sh(e)) & (sh(e) > sh(e, 2)); S = (e < sh(e)) & (sh(e) < sh(e, 2))
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 12. RSI Crossover
def run_rsx(name, df, mm, tag, rows=None, verbose=True, rl=50, ml=25, long_ok=True, short_ok=False, **extra):
    """RSI50 cruza acima da sua SMA25 compra, abaixo fecha (o original so compra; ambos inverte)."""
    o, h, l, c = ohlc(df); r_ = wilder_rsi(c, rl); m = T.sma(r_, ml)
    L, S = T.xover(r_, m), T.xunder(r_, m)
    r = gsim(df, mm, L, S, Z(c), S, rev=True, long_ok=long_ok, short_ok=short_ok) if short_ok else \
        gsim(df, mm, L, Z(c), S, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 13. Previous Day High/Low Breakout
def prev_day(df):
    g = df.index.normalize(); d = df.groupby(g).agg(hi=('high', 'max'), lo=('low', 'min')).shift(1)
    return d.hi.reindex(g).to_numpy(), d.lo.reindex(g).to_numpy()


def run_pdb(name, df, mm, tag, rows=None, verbose=True, src='hl', long_ok=True, short_ok=True, **extra):
    """Maxima cruza a maxima do dia anterior compra, minima cruza a minima anterior vende, inverte (src=close:
    usa o close nos dois cruzamentos)."""
    o, h, l, c = ohlc(df); ph, pl = prev_day(df)
    a, b = (h, l) if src == 'hl' else (c, c)
    L, S = T.xover(a, ph), T.xunder(b, pl)
    r = gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 14. MACD, RSI & RVOL (long-only)
def run_mrr(name, df, mm, tag, rows=None, verbose=True, lo=30, rv=(2.0, 5.0), **extra):
    """So long: 2 de 3 entre RSI14 cruza acima de 30, delta do MACD cruza 0 para cima e RVOL14 cruza acima de 2
    compra; 2 de 3 entre RSI cruza abaixo de 70, delta cruza 0 para baixo e RVOL cruza abaixo de 5 fecha."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); r_ = wilder_rsi(c, 14)
    m, sg = macd(c); d = m - sg; rvol = v / T.sma(v, 14); z = 0 * c
    a1, a2, a3 = T.xover(r_, z + lo), T.xover(d, z), T.xover(rvol, z + rv[0])
    b1, b2, b3 = T.xunder(r_, z + 100 - lo), T.xunder(d, z), T.xunder(rvol, z + rv[1])
    L = (a1 & a2) | (a1 & a3) | (a2 & a3); X = (b1 & b2) | (b1 & b3) | (b2 & b3)
    r = gsim(df, mm, L, Z(c), X, rev=False, short_ok=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 15. Dual Moving Average (angulo)
def run_dma(name, df, mm, tag, rows=None, verbose=True, ang=7, long_ok=True, short_ok=True, **extra):
    """SMA8 x SMA21 nas ultimas 15 barras e angulo da SMA21 (2 barras, normalizado pelo ATR10) acima de 7 graus
    compra; espelho vende; inverte."""
    o, h, l, c = ohlc(df); a, b = T.sma(c, 8), T.sma(c, 21)
    with np.errstate(divide='ignore', invalid='ignore'):
        an = np.degrees(np.arctan((b - sh(b, 2)) / T.atr_rma(h, l, c, 10) / 2))
    lc = roll(sh(T.xover(a, b).astype(float)), 15).max().to_numpy() == 1
    sc = roll(sh(T.xunder(a, b).astype(float)), 15).max().to_numpy() == 1
    L = lc & (an > ang); S = sc & (an < -ang)
    r = gsim(df, mm, L, S & ~L, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 16. Pivot Point Reversal + RSI
def run_pprs(name, df, mm, tag, rows=None, verbose=True, lb=3, rb=3, long_ok=True, short_ok=True, **extra):
    """Pivos (3, 3): stop de compra 1 tick acima do ultimo topo enquanto nao rompido e com RSI14 de 3 barras
    atras < 70; stop de venda abaixo do ultimo fundo com RSI > 30; inverte."""
    o, h, l, c = ohlc(df); n = len(c); r_ = sh(wilder_rsi(c, 14), rb)
    ph, pl = T.pivothigh(h, lb, rb), T.pivotlow(l, lb, rb); hs, ls = sh(h, rb), sh(l, rb)
    LE = full(c, NAN); SE = full(c, NAN); hp = lp = 0.0; le = se = False
    for i in range(n):
        if ph[i]: hp = hs[i]; le = True
        elif le and h[i] > hp: le = False
        if pl[i]: lp = ls[i]; se = True
        elif se and l[i] < lp: se = False
        if le and r_[i] < 70: LE[i] = hp
        if se and r_[i] > 30: SE[i] = lp
    return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok, short_ok=short_ok)


# ------------------------------------------------------------------ 17. Kozlod Heikin-Ashi
def run_kha(name, df, mm, tag, rows=None, verbose=True, k=1, long_ok=True, short_ok=True, **extra):
    """Heikin-Ashi vira verde compra, vira vermelho vende, inverte (k=2: exige 2 velas da nova cor)."""
    o, h, l, c = ohlc(df); ho, _, _, hc = heikin(o, h, l, c); g = (hc > ho).astype(float); rd = (hc < ho).astype(float)
    gk = roll(g, k).min().to_numpy() == 1; rk = roll(rd, k).min().to_numpy() == 1
    L = gk & (sh(g, k) == 0); S = rk & (sh(rd, k) == 0)
    r = gsim(df, mm, L, S, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 18. DEMA + MACD
def run_dm(name, df, mm, tag, rows=None, verbose=True, ln=21, long_ok=True, short_ok=True, **extra):
    """Close acima da DEMA21 fica comprado, abaixo vendido (o controle por MACD vem desligado)."""
    o, h, l, c = ohlc(df); e = ema(c, ln); d = 2 * e - ema(e, ln)
    p = np.where(c > d, 1, -1) if long_ok else np.where(c <= d, -1, 0)
    if long_ok and not short_ok: p = np.where(c > d, 1, 0)
    return run_g(name, df, posflat(df, mm, p, long_ok, short_ok), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 19. London BreakOut Classic
def run_lbo(name, df, mm, tag, rows=None, verbose=True, rr=1.0, long_ok=True, short_ok=True, **extra):
    """Faixa de Toquio 00:00-06:55 UTC; das 07:00 as 16:00 UTC, maxima >= topo da faixa compra e minima <= fundo
    vende, uma vez por dia; stop no meio da faixa, alvo 1R; fecha na barra das 00h."""
    o, h, l, c = ohlc(df); idx = df.index; hr = idx.hour.to_numpy(); day = idx.normalize()
    ins = hr < 7; g = pd.DataFrame({'h': np.where(ins, h, NAN), 'l': np.where(ins, l, NAN)}).groupby(day)
    mx, mn = g.h.transform('max').to_numpy(), g.l.transform('min').to_numpy(); mid = (mx + mn) / 2
    win = (hr >= 7) & (hr < 16)
    L0 = win & (h >= mx); S0 = win & (l <= mn) & ~L0
    if not long_ok: L0 = L0 & False
    if not short_ok: S0 = S0 & False
    L = np.zeros(len(c), bool); S = np.zeros(len(c), bool); last = None; dv = day.to_numpy()
    for i in np.flatnonzero(L0 | S0):
        if dv[i] != last:
            last = dv[i]; L[i] = L0[i]; S[i] = S0[i]
    X = hr == 0
    r = gsim(df, mm, L, S, X, X, SLL=mid, TPL=c + rr * (c - mid), SLS=mid, TPS=c - rr * (mid - c), rev=False,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 20. Triple CCI + MFI (long-only)
def run_tcci(name, df, mm, tag, rows=None, verbose=True, slm=1.75, act=2.25, **extra):
    """So long: CCI14(hlc3) cruza 0 para cima, close > EMA50, CCI25 e CCI50 > 0 e MFI14 > 50; stop entrada - 1,75
    ATR14; depois que a maxima passa entrada + 2,25 ATR, sai com close abaixo da EMA20."""
    o, h, l, c = ohlc(df); v = df.volume.to_numpy(float); tp = (h + l + c) / 3
    L = T.xover(cci(tp, 14), 0 * c) & (c > ema(c, 50)) & (cci(tp, 25) > 0) & (cci(tp, 50) > 0) & (T.mfi(tp, v, 14) > 50)
    a = T.atr_rma(h, l, c, 14); e20 = ema(c, 20)
    def ex(j, s, e, st):
        if l[j] <= e - slm * a[j]: return 2, None
        if st.get('act') and c[j] < e20[j]: return 2, None
        if h[j] > e + act * a[j]: st['act'] = True
        return 0, None
    return run_loop(name, df, tag, rows, verbose, extra, L, Z(c), ex, False, True, False)


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

        grid('e5', run_e5, "1. 5 EMA", TFS, 'rr1.5 ambos',
             [(f'rr{a:g} {s}', dict(rr=a, **sk(s))) for a, s in itertools.product((1.5, 3.0), side2)])
        grid('vst', run_vst, "2. Vegas SuperTrend Enhanced", TFS, 'b5 ambos',
             [(f'b{a:g} {s}', dict(base=a, **sk(s))) for a, s in itertools.product((5.0, 2.0), side2)])
        grid('csq', run_csq, "3. Crypto Squeeze", TFS, 'mfi58 ambos',
             [(f'mfi{a} {s}', dict(mfl=a, **sk(s))) for a, s in itertools.product((58, 14), side2)])
        grid('mel', run_mel, "4. MACD + EMA (long-only)", TFS, 'filtro 12/26',
             [(('filtro ' if a else 'semfiltro ') + f'{f}/{s}', dict(filt=a, f=f, s=s))
              for a, (f, s) in itertools.product((True, False), ((12, 26), (8, 21)))])
        grid('sts', run_sts, "5. SuperTrend STRATEGY", TFS, 'm8.5 long',
             [(f'm{a:g} {s}', dict(mult=a, **sk(s))) for a, s in itertools.product((8.5, 3.0), side2)])
        grid('bx', run_bx, "6. B-Xtrender", TFS, 'trl20% ambos',
             [(f'trl{a:.0%} {s}', dict(trl=a, **sk(s))) for a, s in itertools.product((0.2, 0.05), side2)])
        grid('him', run_him, "7. Hull + Ichimoku + MACD", TFS, 'h12 ambos',
             [(f'h{a} {s}', dict(keh=a, **sk(s))) for a, s in itertools.product((12, 30), side2)])
        grid('qc', run_qc, "8. QuantCat Intraday", TFS, 'atr4 ambos',
             [(f'atr{a:g} {s}', dict(sm=a, **sk(s))) for a, s in itertools.product((4.0, 2.0), side2)])
        grid('ksr', run_ksr, "9. KSR (EMA 10/20)", TFS, '10/20 ambos',
             [(f'{f}/{s_} {s}', dict(f=f, s=s_, **sk(s))) for (f, s_), s in itertools.product(((10, 20), (20, 50)), side2)])
        grid('kama', run_kama, "10. KAMA Strategy (long-only)", TFS, 'f1 semtrail',
             [(f'f{a:g} ' + ('atr3' if t else 'semtrail'), dict(ef=a, atrs=t)) for a, t in itertools.product((1.0, 0.5), (False, True))])
        grid('hama', run_hama, "11. NSDT HAMA (EMA55)", TFS, 'e55 ambos',
             [(f'e{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((55, 20), side2)])
        grid('rsx', run_rsx, "12. RSI Crossover", TFS, 'r50/25 long',
             [(f'r{a}/{b} {s}', dict(rl=a, ml=b, **sk(s))) for (a, b), s in itertools.product(((50, 25), (14, 9)), side2)])
        grid('pdb', run_pdb, "13. Previous Day High/Low Breakout", ITF, 'hl ambos',
             [(f'{a} {s}', dict(src=a, **sk(s))) for a, s in itertools.product(('hl', 'close'), side2)])
        grid('mrr', run_mrr, "14. MACD, RSI & RVOL (long-only)", TFS, '30/70 rv2/5',
             [(f'{a}/{100 - a} rv{b[0]:g}/{b[1]:g}', dict(lo=a, rv=b)) for a, b in itertools.product((30, 40), ((2.0, 5.0), (1.5, 1.5)))])
        grid('dma', run_dma, "15. Dual Moving Average (angulo)", TFS, 'a7 ambos',
             [(f'a{a} {s}', dict(ang=a, **sk(s))) for a, s in itertools.product((7, 3), side2)])
        grid('pprs', run_pprs, "16. Pivot Point Reversal + RSI", TFS, 'pv3/3 ambos',
             [(f'pv{a}/{b} {s}', dict(lb=a, rb=b, **sk(s))) for (a, b), s in itertools.product(((3, 3), (6, 3)), side2)])
        grid('kha', run_kha, "17. Kozlod Heikin-Ashi", TFS, 'k1 ambos',
             [(f'k{a} {s}', dict(k=a, **sk(s))) for a, s in itertools.product((1, 2), side2)])
        grid('dm', run_dm, "18. DEMA + MACD", TFS, 'd21 ambos',
             [(f'd{a} {s}', dict(ln=a, **sk(s))) for a, s in itertools.product((21, 50), side2)])
        grid('lbo', run_lbo, "19. London BreakOut Classic", ITF, 'rr1 ambos',
             [(f'rr{a:g} {s}', dict(rr=a, **sk(s))) for a, s in itertools.product((1.0, 2.0), side2)])
        grid('tcci', run_tcci, "20. Triple CCI + MFI (long-only)", TFS, 'sl1.75 at2.25',
             [(f'sl{a:g} at{b:g}', dict(slm=a, act=b)) for a, b in itertools.product((1.75, 3.0), (2.25, 1.0))])

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote26')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
