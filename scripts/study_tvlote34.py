"""Lote 34 (2026-10-23): resgate de 10 scripts pulados por complexidade nos lotes 21 a 29, so o nucleo de tendencia
de cada um (ver docs/LOTE34_TV.md e a triagem em estrategias/puladas_complexas.md). Grade completa nos 5 ativos.

uso: python study_tvlote34.py xau us100 wti btc eth
"""
import os, sys, itertools, math
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote20 import sh
from study_tvlote22 import run_stp
from study_tvlote25 import posflat, hh, ll, NAN, roll
from study_tvlote30 import R


# ------------------------------------------------------------------ comuns
@njit(cache=True)
def st_series(src, factor, ln):
    """Supertrend do presentTrading sobre uma serie: barra sintetica o=src[1], h=max, l=min, c=src; ATR rma(ln).
    Devolve a direcao (-1 = alta)."""
    n = len(src); d = np.ones(n); up = np.zeros(n); dn = np.zeros(n); st = np.zeros(n); atr = np.full(n, np.nan)
    trs = np.zeros(n); a = 1.0 / ln; acc = 0.0; cnt = 0
    for i in range(n):
        c = src[i]; o = src[i - 1] if i > 0 else c
        h = max(o, c); l = min(o, c)
        tr = h - l if i == 0 else max(h - l, abs(h - src[i - 1]), abs(l - src[i - 1]))
        if ln == 1:
            atr[i] = tr
        elif cnt < ln:
            acc += tr; cnt += 1
            if cnt == ln: atr[i] = acc / ln
        else:
            atr[i] = a * tr + (1 - a) * atr[i - 1]
        hl2 = (h + l) / 2
        u = hl2 + factor * atr[i]; w = hl2 - factor * atr[i]
        pu = up[i - 1] if i > 0 else 0.0; pw = dn[i - 1] if i > 0 else 0.0
        pc = src[i - 1] if i > 0 else c
        if not (u < pu or pc > pu): u = pu
        if not (w > pw or pc < pw): w = pw
        up[i] = u; dn[i] = w
        if i == 0 or atr[i - 1] != atr[i - 1]:
            d[i] = 1
        elif st[i - 1] == pu:
            d[i] = -1 if c > u else 1
        else:
            d[i] = 1 if c < w else -1
        st[i] = w if d[i] == -1 else u
    return d


def pctl_nr(x, n, p):
    """ta.percentile_nearest_rank(x, n, p): valor de ordem ceil(p/100 * n) da janela."""
    k = max(int(math.ceil(p / 100 * n)) - 1, 0)
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), n)
    out = np.full(len(x), NAN); out[n - 1:] = np.partition(W, k, axis=1)[:, k]
    return out


# ------------------------------------------------------------------ 1. Gradient Trend Filter (ChartPrime)
def run_gtf(name, df, mm, tag, rows=None, verbose=True, ln=25, long_ok=True, short_ok=False, **extra):
    """Filtro = EMA tripla em cascata (25); filtro - filtro[2] cruzando acima de 0 compra, abaixo vende (padrao so
    comprado: fecha)."""
    o, h, l, c = ohlc(df); b = ema(ema(ema(c, ln), ln), ln); d = b - sh(b, 2)
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(d, np.zeros(len(c))), T.xunder(d, np.zeros(len(c))),
             long_ok, short_ok)


# ------------------------------------------------------------------ 2. Market Trend Levels (BigBeluga)
def run_mtl(name, df, mm, tag, rows=None, verbose=True, p=(12, 25), adx=0, long_ok=True, short_ok=False, **extra):
    """EMA 12 cruzando a EMA 25 compra/vende (padrao so comprado); filtros desligados no padrao, ADX > adx como
    variante (vale nos dois lados, como no script)."""
    from study_tvlote8 import dmi
    o, h, l, c = ohlc(df); a, b = ema(c, p[0]), ema(c, p[1]); L, S = T.xover(a, b), T.xunder(a, b)
    if adx:
        f = dmi(h, l, c, 14)[2] > adx
        if short_ok:
            L, S = L & f, S & f
        else:   # so comprado: a saida e o cruzamento para baixo, sem filtro
            L = L & f
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


# ------------------------------------------------------------------ 3. Pivot Percentile Trend (presentTrading)
def run_ppt(name, df, mm, tag, rows=None, verbose=True, ln=10, f=16.0, long_ok=True, short_ok=True, **extra):
    """Forca de tendencia: percentis 75 das maximas e 25 das minimas em 1, 2, 3, 6 e 7 x 10 barras contra os mesmos
    percentis em 144; Supertrend (20, 16) sobre essa forca; forca > 0 com Supertrend em alta compra, o espelho vende."""
    o, h, l, c = ohlc(df); HH = pctl_nr(h, 144, 75); LL = pctl_nr(l, 144, 25)
    cb = np.zeros(len(c)); cs = cb.copy(); wb = cb.copy(); ws = cb.copy()
    for m in (1, 2, 3, 6, 7):
        ph, pl = pctl_nr(h, ln * m, 75), pctl_nr(l, ln * m, 25)
        cb += (ph > HH) + 0.0 + (pl > HH); cs += (ph < LL) + 0.0 + (pl < LL)
        wb += (pl < HH) & (pl > LL); ws += (ph > LL) & (ph < HH)
    v = 2 * (cb + 0.5 * wb - 0.5 * ws - cs)
    d = st_series(np.nan_to_num(v), f, 20)
    return R(name, df, mm, tag, rows, verbose, extra, (v > 0) & (d < 0), (v < 0) & (d > 0), long_ok, short_ok)


# ------------------------------------------------------------------ 4. FlexiMA Variance Tracker (presentTrading)
def run_fmv(name, df, mm, tag, rows=None, verbose=True, ln=10, f=15.0, long_ok=True, short_ok=True, **extra):
    """Mediana dos desvios de hlc3 para 20 SMAs (10, 20, ..., 200); Supertrend (10, 15) sobre a mediana: em alta
    comprado, em baixa vendido."""
    o, h, l, c = ohlc(df); s = (h + l + c) / 3
    M = np.column_stack([s - T.sma(s, int(round(ln * k))) for k in range(1, 21)])
    med = np.median(M, axis=1)
    d = st_series(np.nan_to_num(med), f, 10)
    return R(name, df, mm, tag, rows, verbose, extra, d < 0, d > 0, long_ok, short_ok)


# ------------------------------------------------------------------ 5. Ichimoku Kumo Twist
def run_kmt(name, df, mm, tag, rows=None, verbose=True, p=(9, 26, 52), stop=True, long_ok=True, short_ok=True, **extra):
    """Lead 1 (tenkan 9 + kijun 26) cruzando a lead 2 (52) arma stop de compra na maxima do cruzamento (o espelho
    arma stop de venda na minima), valido ate o cruzamento contrario; inverte. stop=False: a mercado."""
    o, h, l, c = ohlc(df); dc = lambda n: (hh(h, n) + ll(l, n)) / 2; a = (dc(p[0]) + dc(p[1])) / 2; b = dc(p[2])
    L, S = T.xover(a, b), T.xunder(a, b)
    if not stop:
        return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)
    reg = pd.Series(np.where(L, 1.0, np.where(S, -1.0, NAN))).ffill().to_numpy()
    LE = pd.Series(np.where(L, h, np.where(S, 0.0, NAN))).ffill().to_numpy().copy(); LE[(reg != 1) | (LE == 0)] = NAN
    SE = pd.Series(np.where(S, l, np.where(L, 0.0, NAN))).ffill().to_numpy().copy(); SE[(reg != -1) | (SE == 0)] = NAN
    if short_ok:
        return run_stp(name, df, tag, rows, verbose, extra, LE, SE, long_ok=long_ok)
    # so comprado: depois do cruzamento para baixo o long sai a mercado na abertura seguinte
    return run_stp(name, df, tag, rows, verbose, extra, LE, np.full(len(c), NAN), np.where(reg == -1, np.inf, NAN),
                   short_ok=False)


# ------------------------------------------------------------------ 6. Zero-Lag MA Trend Following
def run_zlm(name, df, mm, tag, rows=None, verbose=True, ln=34, rr=2.0, long_ok=True, short_ok=True, **extra):
    """ZLMA (EMA de close + (close - EMA)) cruzando a EMA 34 cria a caixa (ZLMA e ZLMA -/+ ATR14) e arma o lado; a
    minima cruzando acima do topo da caixa compra com stop no fundo e alvo de rr x risco, o espelho vende; inverte."""
    o, h, l, c = ohlc(df); e = ema(c, ln); z = ema(c + (c - e), ln); a = T.atr_rma(h, l, c, 14)
    up, dn = T.xover(z, e), T.xunder(z, e); n = len(c)
    top = np.full(n, NAN); bot = top.copy(); L = np.zeros(n, bool); S = L.copy()
    sll = np.full(n, NAN); tpl = sll.copy(); sls = sll.copy(); tps = sll.copy(); fl = fs = False
    for i in range(n):
        top[i], bot[i] = (top[i - 1], bot[i - 1]) if i else (NAN, NAN)
        if up[i]: top[i], bot[i] = z[i], z[i] - a[i]; fl = True
        if dn[i]: top[i], bot[i] = z[i] + a[i], z[i]; fs = True
        if i and fl and l[i] > top[i] and l[i - 1] <= top[i - 1]:
            L[i] = True; sll[i] = bot[i]; tpl[i] = c[i] + (c[i] - bot[i]) * rr; fl = False
        if i and fs and h[i] < bot[i] and h[i - 1] >= bot[i - 1]:
            S[i] = True; sls[i] = top[i]; tps[i] = c[i] - (top[i] - c[i]) * rr; fs = False
    res = gsim(df, mm, L, S & ~L, SLL=sll, TPL=tpl, SLS=sls, TPS=tps, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 7. Adaptive Zero Lag EMA v2 (Ehlers)
@njit(cache=True)
def _azl(src, per, adaptive, glim):
    n = len(src); PI = 3.14159265359
    v1 = np.zeros(n); s2 = np.zeros(n); s3 = np.zeros(n); dC = np.zeros(n); inst = np.zeros(n); lenC = np.zeros(n)
    EC = np.zeros(n); EM = np.zeros(n); LE = np.zeros(n)
    for i in range(n):
        P = per
        if adaptive:
            v1[i] = src[i] - src[i - 7] if i >= 7 else 0.0
            p1 = v1[i - 1] if i else 0.0
            s2[i] = 0.2 * (p1 + v1[i]) ** 2 + 0.8 * (s2[i - 1] if i else 0.0)
            s3[i] = 0.2 * (p1 - v1[i]) ** 2 + 0.8 * (s3[i - 1] if i else 0.0)
            v2 = math.sqrt(s3[i] / s2[i]) if s2[i] != 0 else 0.0
            dC[i] = 2 * math.atan(v2) if s3[i] != 0 else 0.0
            v4 = 0.0; ic = 0.0
            for k in range(51):
                if i - k < 0: break
                v4 += dC[i - k]
                if v4 > 2 * PI and ic == 0.0: ic = k - 1
            if ic == 0.0: ic = inst[i - 1] if i else 0.0
            inst[i] = ic
            lenC[i] = 0.25 * ic + 0.75 * (lenC[i - 1] if i else 0.0)
            P = int(round(lenC[i]))
        al = 2.0 / (P + 1)
        pe = EM[i - 1] if i else 0.0; pc = EC[i - 1] if i else 0.0
        EM[i] = al * src[i] + (1 - al) * pe
        le = 1e18; bg = 0.0
        for g in range(-glim, glim + 1):
            G = g / 10.0
            ec = al * (EM[i] + G * (src[i] - pc)) + (1 - al) * pc
            if abs(src[i] - ec) < le: le = abs(src[i] - ec); bg = G
        EC[i] = al * (EM[i] + bg * (src[i] - pc)) + (1 - al) * pc
        LE[i] = le
    return EC, EM, LE


def run_azl(name, df, mm, tag, rows=None, verbose=True, adaptive=True, thr=0.05, long_ok=True, short_ok=True, **extra):
    """EC (EMA com ganho que minimiza o erro, -0,8..0,8) cruzando a EMA, com periodo adaptativo (Cos IFM) ou fixo
    em 20, e erro minimo > 0,05% do preco: acima compra, abaixo vende; inverte (SL/trailing em pontos de forex
    ignorados)."""
    o, h, l, c = ohlc(df); EC, EM, LE = _azl(c, 20, adaptive, 8); f = 100 * LE / c > thr
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(EC, EM) & f, T.xunder(EC, EM) & f, long_ok, short_ok)


# ------------------------------------------------------------------ 8. ML SuperTrend (YinYang, kNN)
@njit(cache=True)
def _mlst(c, src, atr, cs, factor, mlen, knn, tpm, eps):
    n = len(c); ub = np.zeros(n); lb = np.zeros(n); st = np.zeros(n); d = np.ones(n)
    for i in range(n):
        u = src[i] + factor * atr[i]; w = src[i] - factor * atr[i]
        pu = ub[i - 1] if i else 0.0; pw = lb[i - 1] if i else 0.0
        pu = pu if pu == pu else 0.0; pw = pw if pw == pw else 0.0
        if i and not (w > pw or cs[i - 1] < pw): w = pw
        if i and not (u < pu or cs[i - 1] > pu): u = pu
        ub[i] = u; lb[i] = w
        if i == 0 or atr[i - 1] != atr[i - 1]:
            d[i] = 1
        else:
            sl = lb[i] * (1 - eps) if d[i - 1] == -1 else ub[i] * (1 + eps)
            if st[i - 1] == pu: d[i] = -1 if cs[i] > sl else 1
            else: d[i] = 1 if cs[i] < sl else -1
        st[i] = lb[i] if d[i] == -1 else ub[i]
    fast = np.full(n, np.nan); slow = np.full(n, np.nan)
    for i in range(n):
        if i >= 2: fast[i] = (st[i] + st[i - 1] + st[i - 2]) / 3
        if i >= 49: slow[i] = st[i - 49:i + 1].mean()
    dd = np.ones(n); ml = np.full(n, np.nan); X = np.zeros(n, np.bool_)
    for i in range(mlen + 50, n):
        dist = np.empty(mlen); avg = np.empty(mlen); m = 0
        for k in range(mlen):
            if d[i - k] == d[i]:
                dist[m] = slow[i - k] - fast[i - k]; avg[m] = (slow[i - k] + fast[i - k]) / 2; m += 1
        if m == 0: continue
        kk = min(knn, m); mx = dist[:kk].max(); mn = dist[:kk].min(); s = 0.0; q = 0
        for k in range(m):
            if mn <= dist[k] <= mx: s += avg[k]; q += 1
        if q == 0: continue
        ml[i] = s / q
        sl = ml[i] * (1 - eps) if d[i] == -1 else ml[i] * (1 + eps)
        dd[i] = -1 if c[i] > sl else 1
        if tpm > 0:
            if dd[i] == -1 and c[i] > ml[i] * (1 + tpm): X[i] = True
            if dd[i] == 1 and c[i] < ml[i] * (1 - tpm): X[i] = True
    return dd, X


def rq_kernel(x, lb=8, rw=8.0, nb=27):
    """rationalQuadratic do script: media ponderada das ultimas 27 barras com peso (1 + i^2 / (2 lb^2 rw))^-rw."""
    w = (1 + np.arange(nb) ** 2 / (lb ** 2 * 2 * rw)) ** -rw
    W = np.lib.stride_tricks.sliding_window_view(np.asarray(x, float), nb)[:, ::-1]
    out = np.full(len(x), NAN); out[nb - 1:] = W @ w / w.sum()
    return out


def run_mls(name, df, mm, tag, rows=None, verbose=True, factor=2.94, tp=0.022, long_ok=True, short_ok=True, **extra):
    """Supertrend (ATR4, 2,94) sobre hl2, ATR e close suavizados por kernel racional quadratico; a linha final e a
    media kNN (k=2, 100 barras, mesma direcao) das SMAs 3 e 50 do Supertrend; close acima = alta. Virada inverte
    (stop de entrada ja rompido = a mercado); close alem de 2,2% da linha a favor fecha (tp=0 desliga)."""
    o, h, l, c = ohlc(df); a = T.atr_rma(h, l, c, 4)
    k = lambda x: np.nan_to_num(rq_kernel(x), nan=np.nan)
    d, X = _mlst(c, k((h + l) / 2), k(a), k(c), factor, 100, 2, tp, 0.0000025)
    L = (d == -1) & (sh(d) == 1); S = (d == 1) & (sh(d) == -1)
    res = gsim(df, mm, L, S, X & (d == -1), X & (d == 1), rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 9. Turtle (uma unidade)
def run_ttl(name, df, mm, tag, rows=None, verbose=True, p=(20, 55, 10, 20), stopn=2.0, filt=True, long_ok=True,
            short_ok=False, **extra):
    """So comprado, sem piramide: maxima acima da maxima de 20 compra (L1), a nao ser que o ultimo L1 tenha sido
    vencedor (filt; o trade fantasma segue sendo acompanhado), maxima acima da de 55 compra sempre (L2); sai com a
    minima abaixo da minima de 10 (L1) ou de 20 (L2), ou abaixo do stop de 2 N (ATR14) do close de entrada."""
    o, h, l, c = ohlc(df); n = len(c); a = T.atr_rma(h, l, c, 14)
    h1, h2, x1, x2 = sh(hh(h, p[0])), sh(hh(h, p[1])), sh(ll(l, p[2])), sh(ll(l, p[3]))
    q = np.zeros(n); pos = 0; mode = 1; ent = stp = 0.0; win = False; fake = False
    for i in range(n):
        if pos:
            xl = x1[i] if mode == 1 else x2[i]
            if l[i] < stp or l[i] < xl:
                ex = c[i]; g = ex >= ent
                if fake: win = g
                else: win = g
                pos = 0; fake = False
        if not pos:
            b2 = h[i] > h2[i]; b1 = h[i] > h1[i]
            if b2 or b1:
                mode = 2 if b2 else 1; fake = (mode == 1 and filt and win)
                pos = 1; ent = c[i]; stp = c[i] - stopn * a[i]
        elif fake and h[i] > h2[i]:   # o L2 promove o trade fantasma a real
            fake = False; mode = 2; ent = c[i]; stp = c[i] - stopn * a[i]
        q[i] = 1 if (pos and not fake) else 0
    return run_g(name, df, posflat(df, mm, q, long_ok, False), tag, rows, verbose, extra)


# ------------------------------------------------------------------ 10. Kahlman HullMA / WT Cross
def run_khw(name, df, mm, tag, rows=None, verbose=True, ln=24, wt=True, long_ok=True, short_ok=True, **extra):
    """Kalman (ganho 10000) da Hull 24 de hl2 contra o da HMA3; virada para cima com WT (6/23) cruzando para cima
    nas ultimas barras compra, virada para baixo com WT (8/19) cruzando para baixo vende; inverte (TPs parciais,
    trailing e checagens de posicao ignorados). wt=False: so a virada do Kalman."""
    o, h, l, c = ohlc(df); src = (h + l) / 2

    def kal(x):
        x = np.nan_to_num(x, nan=np.nan); kf = np.full(len(x), NAN); v = 0.0; g = 1.0
        for i in range(len(x)):
            if x[i] != x[i]: continue
            p = kf[i - 1] if i and kf[i - 1] == kf[i - 1] else x[i]
            dk = x[i] - p; v += g * dk; kf[i] = p + dk * math.sqrt(g * 2) + v
        return kf
    hm = T.wma(2 * T.wma(src, ln // 2) - T.wma(src, ln), int(round(math.sqrt(ln))))
    pp = ln // 2
    h3 = T.wma(T.wma(c, pp // 3) * 3 - T.wma(c, pp // 2) - T.wma(c, pp), pp)
    a, b = kal(hm), kal(h3)
    cdn = (a > b) & (sh(a) < sh(b)); cup = (b > a) & (sh(b) < sh(a))

    def wtf(n1, n2):
        ap = (h + l + c) / 3; es = ema(ap, n1); d = ema(np.abs(ap - es), n1)
        with np.errstate(divide='ignore', invalid='ignore'):
            w1 = ema(np.nan_to_num((ap - es) / (0.015 * d)), n2)
        return w1, T.sma(w1, 4)
    l1, l2 = wtf(6, 23); s1, s2 = wtf(8, 19)
    if wt:
        L = cup & (T.xover(l1, l2) | sh(T.xover(l1, l2)).astype(bool) | T.xover(sh(l1, 2), l2))
        S = cdn & T.xunder(s1, s2)
    else:
        L, S = cup, cdn
    return R(name, df, mm, tag, rows, verbose, extra, L, S, long_ok, short_ok)


side2 = ('ambos', 'long')
sk = lambda s: dict(short_ok=s == 'ambos')
pr = lambda v: '/'.join(f'{x:g}' for x in v)
g2 = lambda key, vals, fmt: [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)]
# est -> (funcao, titulo, rotulo do padrao, [(rotulo, kwargs)])
GRID = {
    'gtf': (run_gtf, "1. Gradient Trend Filter", 'l25 long', g2('ln', (25, 50), lambda v: f'l{v}')),
    'mtl': (run_mtl, "2. Market Trend Levels", 'ema12/25 long',
            [(f'{pr(p)} adx{a} {s}', dict(p=p, adx=a, **sk(s)))
             for p, a, s in itertools.product(((12, 25), (20, 50)), (0, 20), side2)]),
    'ppt': (run_ppt, "3. Pivot Percentile Trend", 'l10 ambos', g2('ln', (10, 20), lambda v: f'l{v}')),
    'fmv': (run_fmv, "4. FlexiMA Variance Tracker", 'f15 ambos', g2('f', (15.0, 8.0), lambda v: f'f{v:g}')),
    'kmt': (run_kmt, "5. Ichimoku Kumo Twist", 'stop ambos',
            [(f"{'stop' if st else 'mercado'} {s}", dict(stop=st, **sk(s))) for st, s in itertools.product((True, False), side2)]),
    'zlm': (run_zlm, "6. Zero-Lag MA Trend Following", 'rr2 ambos', g2('rr', (2.0, 4.0), lambda v: f'rr{v:g}')),
    'azl': (run_azl, "7. Adaptive Zero Lag EMA", 'cos thr0.05 ambos',
            [(f"{'cos' if ad else 'p20'} thr{t:g} {s}", dict(adaptive=ad, thr=t, **sk(s)))
             for ad, t, s in itertools.product((True, False), (0.05, 0.0), side2)]),
    'mls': (run_mls, "8. ML SuperTrend kNN", 'f2.94 tp2.2 ambos',
            [(f'f{f:g} tp{tp * 100:g} {s}', dict(factor=f, tp=tp, **sk(s)))
             for f, tp, s in itertools.product((2.94, 4.0), (0.022, 0.0), side2)]),
    'ttl': (run_ttl, "9. Turtle (uma unidade, long)", '20/55/10/20 filtro',
            [(f"{pr(p)} {'filtro' if fl else 'sem filtro'}", dict(p=p, filt=fl))
             for p, fl in itertools.product(((20, 55, 10, 20), (55, 55, 20, 20)), (True, False))]),
    'khw': (run_khw, "10. Kahlman HullMA / WT Cross", 'h24 wt ambos',
            [(f"h{n} {'wt' if w else 'sem wt'} {s}", dict(ln=n, wt=w, **sk(s)))
             for n, w, s in itertools.product((24, 48), (True, False), side2)]),
}


def KW(est, cfg):
    """kwargs de uma celula da grade a partir do rotulo (usado por study_veredito_lote)."""
    fn, _, dflt, combos = GRID[est]
    return {} if cfg == dflt else dict(combos)[cfg]


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        for est, (fn, label, default_cfg, combos) in GRID.items():
            print(f"\n### {label}", flush=True)
            for tf in TFS:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote34')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
