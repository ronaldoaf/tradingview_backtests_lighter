"""Lote 17 do TradingView (2026-10-23): 5 estrategias nos 5 ativos (ver docs/LOTE17_TV.md).

Ignorados: SMA (soKH38lY, nao tem ordens: so define o golden/death cross), ZigZag PA Strategy V4
(DYONEypp, mesma familia do ZigZag PA V4.1 ja reprovado, docs/ZIGZAG_PA.md, e usa security() sem
lookahead_off em Pine v1, que olha o futuro) e Wolfe Strategy (EGvQ2nLb, nao tem ordens).

  1. Best Supertrend CCI Strategy (YsWWsOGs, Pine v4)
     A "tendencia" do SuperTrend e o sinal do CCI28 (> 0 comprado, < 0 vendido); o stop do
     SuperTrend so desenha. Sempre no mercado, virando com o CCI.
  2. Grid Like Strategy (oxvR5vMy, Pine v4)
     Linha-base que so anda quando o close se afasta mais de `point` dela; quando sobe, compra com
     alvo base+point e stop base-point (e o espelho). Martingale de tamanho ignorado (1 unidade).
     `point` = 2 (preco absoluto) virou percentual do preco (grade).
  3. FTSMA - Trend is your frend (wffJotUo, Pine v4)
     A cada barra soma ao close o termo cos de Fourier de ordem k da janela de 64 barras e tira EMAs
     (5, 20, 200). Long com rapida > media e close > lenta; short no espelho; sinal contrario inverte.
  4. HULLTSIBOT (gf21APTn, Pine v4)
     TSI com HMA no lugar da EMA (50/50, sobre o open) e sinal HMA7. Compra quando o sinal sobe e o
     open sobe; vende no espelho. Sempre no mercado.
  5. Band-Zigzag TrendFollower [Trendoscope] (9FsHYtrq, Pine v5)
     Zigzag de pivos marcados quando a maxima toca a banda de cima (ou a minima a de baixo) da
     BB(20, 2) "grudenta" e adaptativa; a tendencia vem da razao de retracao do pivo vs o %B; troca de
     tendencia inverte a posicao (modo "Any"). As bandas "sticky" da biblioteca foram aproximadas:
     so mudam quando o preco sai delas.

uso: python study_tvlote17.py xau us100 wti btc eth
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
from study_tvlote16 import cci

NAN = np.nan


def flips(state):
    s = np.asarray(state, bool); p = np.concatenate([[s[0]], s[:-1]])
    return s & ~p, ~s & p


# ------------------------------------------------------------------ 1. Supertrend CCI
def run_stcci(name, df, mm, tag, rows=None, verbose=True, n=28, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    cc = cci(c, h, l, n)
    tr = np.zeros(len(c))
    for i in range(len(c)):
        v = cc[i]
        tr[i] = 1 if v > 0 else (-1 if v < 0 else (tr[i - 1] if i else 1))
    L, S = flips(tr == 1)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Grid Like
def run_grid(name, df, mm, tag, rows=None, verbose=True, pct=0.01, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    n = len(c); b = np.empty(n); b[0] = c[0]
    for i in range(1, n):
        pt = pct * b[i - 1]
        b[i] = c[i] if (c[i] > b[i - 1] + pt or c[i] < b[i - 1] - pt) else b[i - 1]
    bp = np.concatenate([[b[0]], b[:-1]])
    L = b > bp; S = b < bp
    pt = pct * b
    r = gsim(df, mm, L, S, SLL=b - pt, TPL=b + pt, SLS=b + pt, TPS=b - pt, rev=True, long_ok=long_ok,
             short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. FTSMA
def fourier_cos(c, k, N=64):
    """sx(0, k) do script: (2/N) * sum_{i<N} close[i] * cos(2*pi*k*i/N), com i = barras para tras."""
    w = 2.0 / N * np.cos(2 * np.pi * k * np.arange(N) / N)   # w[i] multiplica close[t-i]
    out = np.convolve(c, w, mode='full')[:len(c)]
    out[:N - 1] = NAN
    return out


def run_ftsma(name, df, mm, tag, rows=None, verbose=True, slow=200, mid=20, fast=5, N=64, use_ft=True, long_ok=True,
              short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    f = (lambda k: np.nan_to_num(fourier_cos(c, k, N))) if use_ft else (lambda k: 0.0)
    sl_, md, fs = ema(c + f(1), slow), ema(c + f(2), mid), ema(c + f(3), fast)
    st = np.where((fs > md) & (c > sl_), 1, np.where((fs < md) & (c < sl_), -1, 0))
    sp = np.concatenate([[0], st[:-1]])
    L = (st == 1) & (sp != 1); S = (st == -1) & (sp != -1)
    L[:max(slow, N)] = S[:max(slow, N)] = False
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. HULLTSIBOT
def run_htsi(name, df, mm, tag, rows=None, verbose=True, ln=50, sh=50, sig=7, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    p = o; pc = np.nan_to_num(np.diff(p, prepend=p[0]))
    ds = lambda x: T.hma(T.hma(x, ln), sh)
    with np.errstate(divide='ignore', invalid='ignore'):
        tsi = 500 * ds(pc) / ds(np.abs(pc))
    line = T.hma(np.nan_to_num(tsi), sig)
    up = (line > shift(line, 1)) & (p > shift(p, 1)); dn = (line < shift(line, 1)) & (p < shift(p, 1))
    st = np.zeros(len(c))
    for i in range(len(c)):
        st[i] = 1 if up[i] else (-1 if dn[i] else (st[i - 1] if i else 0))
    sp = np.concatenate([[0], st[:-1]])
    L = (st == 1) & (sp != 1); S = (st == -1) & (sp != -1)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Band-Zigzag
def band_zigzag_trend(h, l, c, n=20, mult=2.0, inv=1.618, use_latest=True):
    mid = T.sma(c, n); sd = pd.Series(c).rolling(n).std(ddof=0).to_numpy()
    raw_u, raw_l = mid + mult * sd, mid - mult * sd
    N = len(c); up = np.full(N, NAN); lo = np.full(N, NAN)
    for i in range(N):                       # "sticky": a banda so muda quando o preco sai dela
        if i == 0 or np.isnan(up[i - 1]):
            up[i], lo[i] = raw_u[i], raw_l[i]; continue
        up[i] = raw_u[i] if (c[i] > up[i - 1] or c[i] < lo[i - 1]) else up[i - 1]
        lo[i] = raw_l[i] if (c[i] > up[i - 1] or c[i] < lo[i - 1]) else lo[i - 1]
    piv = []                                 # [price, dir(+-1/2), percentB, ratio]
    uu = ll = 0.0; cur_dir = 0; trend = cur_force = 0
    comb = np.zeros(N, int); cb = 0
    for i in range(N):
        if np.isnan(up[i]):
            comb[i] = cb; continue
        if len(piv) > 1:
            rp, lp = piv[0], piv[1]
            cur_dir = rp[1]
            trend = int(np.sign(lp[1])) if lp[3] > lp[2] else -int(np.sign(lp[1]))
            cur_force = int(np.sign(rp[1])) if (rp[3] > rp[2] and rp[3] > inv) else -int(np.sign(rp[1]))
        uu = up[i] if (cur_dir >= 0) else min(up[i], uu)
        ll = lo[i] if (cur_dir <= 0) else max(lo[i], ll)
        rng = uu - ll if uu != ll else NAN
        pbh = (h[i] - ll) / rng; pbl = (uu - l[i]) / rng
        ph, pl = h[i] >= uu, l[i] <= ll

        def add(d):
            price = h[i] if d > 0 else l[i]; pb = pbh if d > 0 else pbl
            p = [price, d, pb, 0.0]
            if piv:
                last = piv[0]; ld = int(np.sign(last[1]))
                if ld == d:
                    if last[0] * d < price * d:
                        piv.pop(0)
                    else:
                        return
            if len(piv) > 1:
                a, b = piv[0], piv[1]
                p[1] = d * 2 if price * d > b[0] * d else d
                den = abs(b[0] - a[0])
                p[3] = abs(price - a[0]) / den if den else 0.0
            piv.insert(0, p)
            del piv[15:]
        if not piv:
            if ph: add(1)
            if pl: add(-1)
        else:
            ld = int(np.sign(piv[0][1]))
            if (ph and ld == 1) or (pl and ld == -1): add(ld)
            if (ph and ld == -1) or (pl and ld == 1): add(-ld)
        if trend > 0 or (use_latest and cur_force > 0):
            cb = 1
        elif trend < 0 or (use_latest and cur_force < 0):
            cb = -1
        comb[i] = cb
    return comb


def run_bz(name, df, mm, tag, rows=None, verbose=True, n=20, mult=2.0, use_latest=True, long_ok=True, short_ok=True,
           **extra):
    o, h, l, c = ohlc(df)
    cb = band_zigzag_trend(h, l, c, n, mult, use_latest=use_latest)
    cp = np.concatenate([[0], cb[:-1]])
    L = (cb > 0) & (cp <= 0); S = (cb < 0) & (cp >= 0)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. Supertrend CCI (sinal do CCI28)")
        for tf in TFS:
            df = cache[tf]
            run_stcci(name, df, mm, f"{tf} STCCI default", rows, est='stcci', TF=tf, cfg='cci28 ambos')
            for n, side in itertools.product((14, 28, 50, 100), side2):
                run_stcci(name, df, mm, '', rows, False, n=n, short_ok=side == 'ambos', est='stcci', TF=tf,
                          cfg=f'cci{n} {side}')

        print("\n### 2. Grid Like (linha-base, alvo/stop = point)")
        for tf in TFS:
            df = cache[tf]
            run_grid(name, df, mm, f"{tf} GRID 1%", rows, est='grid', TF=tf, cfg='p1% ambos')
            for pct, side in itertools.product((0.0025, 0.005, 0.01, 0.02, 0.05), side2):
                run_grid(name, df, mm, '', rows, False, pct=pct, short_ok=side == 'ambos', est='grid', TF=tf,
                         cfg=f'p{pct:.2%} {side}')

        print("\n### 3. FTSMA (EMAs 5/20/200 do close + termo de Fourier)")
        for tf in TFS:
            df = cache[tf]
            run_ftsma(name, df, mm, f"{tf} FTSMA default", rows, est='ftsma', TF=tf, cfg='5/20/200 ft ambos')
            for ft, side in itertools.product((True, False), side2):
                run_ftsma(name, df, mm, '', rows, False, use_ft=ft, short_ok=side == 'ambos', est='ftsma', TF=tf,
                          cfg='5/20/200 ' + ('ft' if ft else 'semft') + f' {side}')

        print("\n### 4. HULLTSIBOT (TSI com HMA 50/50, sinal 7)")
        for tf in TFS:
            df = cache[tf]
            run_htsi(name, df, mm, f"{tf} HTSI default", rows, est='htsi', TF=tf, cfg='50/50/7 ambos')
            for (a, b), side in itertools.product(((25, 13), (50, 50), (100, 50)), side2):
                run_htsi(name, df, mm, '', rows, False, ln=a, sh=b, short_ok=side == 'ambos', est='htsi', TF=tf,
                         cfg=f'{a}/{b}/7 {side}')

        print("\n### 5. Band-Zigzag TrendFollower (BB20x2 grudenta)")
        for tf in TFS:
            df = cache[tf]
            run_bz(name, df, mm, f"{tf} BZ default", rows, est='bz', TF=tf, cfg='bb20 2 latest ambos')
            for mu, ul, side in itertools.product((1.5, 2.0, 3.0), (True, False), side2):
                run_bz(name, df, mm, '', rows, False, mult=mu, use_latest=ul, short_ok=side == 'ambos', est='bz', TF=tf,
                       cfg=f'bb20 {mu:g} ' + ('latest' if ul else 'semlatest') + f' {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote17')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
