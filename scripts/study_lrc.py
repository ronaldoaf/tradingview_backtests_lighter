"""LRC(N,dev,dev) reversao a favor da inclinacao, 15m. Long: slope>0 e close<banda inferior; short: slope<0 e
close>banda superior. Sinal no fechamento, entrada na abertura seguinte. Saida: trailing stop k*ATR(L)
(ancorado no extremo de fechamento desde a entrada, atualizado no fechamento; execucao intrabar no nivel,
ou na abertura se gap). Custo = CUSTO por perna + funding pro-rata (long paga, short recebe).
uso: python study_lrc.py"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from tvlib import load_m1v, resample, atr_rma
from study_engulf_psar import CUSTO, FUND
OUT = os.path.join(D, 'results', 'lrc'); ASSETS = ['xau', 'us100', 'wti', 'btc', 'eth']
CUT = pd.Timestamp('2024-01-01', tz='UTC')

def bars(a):
    f = os.path.join(OUT, f'{a}_15m.parquet')
    if not os.path.exists(f): resample(load_m1v(a), '15min').to_parquet(f)
    return pd.read_parquet(f)

@njit(cache=True)
def lrc(c, n):
    m = len(c); sl = np.full(m, np.nan); up = np.full(m, np.nan); lo = np.full(m, np.nan)
    x = np.arange(n) * 1.0; xm = x.mean(); sxx = ((x - xm) ** 2).sum()
    for i in range(n - 1, m):
        y = c[i - n + 1:i + 1]; ym = y.mean(); b = ((x - xm) * (y - ym)).sum() / sxx
        a = ym - b * xm; r = y - (a + b * x); sd = np.sqrt((r * r).mean()); end = a + b * (n - 1)
        sl[i] = b; up[i] = end; lo[i] = end
        up[i] += 0.0; sd_ = sd; up[i] = end + sd_; lo[i] = end - sd_  # dev aplicado fora
    return sl, up, lo

@njit(cache=True)
def sim(o, h, l, c, sig, atr, k):
    m = len(c); ei = np.empty(m, np.int64); xi = np.empty(m, np.int64); side = np.empty(m, np.int64)
    pi = np.empty(m); px = np.empty(m); nt = 0; pos = 0; stop = 0.0; ext = 0.0; i = 0
    while i < m - 1:
        if pos == 0:
            if sig[i] != 0 and not np.isnan(atr[i]):
                pos = sig[i]; i += 1; ei[nt] = i; pi[nt] = o[i]; side[nt] = pos; ext = c[i]
                stop = o[i] - pos * k * atr[i - 1]
                # checa stop na propria barra de entrada
            else:
                i += 1; continue
        # em posicao na barra i
        hit = False
        if pos == 1:
            if o[i] <= stop: fill = o[i]; hit = True
            elif l[i] <= stop: fill = stop; hit = True
        else:
            if o[i] >= stop: fill = o[i]; hit = True
            elif h[i] >= stop: fill = stop; hit = True
        if hit:
            xi[nt] = i; px[nt] = fill; nt += 1; pos = 0
            continue  # mesma barra pode gerar novo sinal no fechamento
        if pos == 1:
            ext = max(ext, c[i]); stop = max(stop, ext - k * atr[i])
        else:
            ext = min(ext, c[i]); stop = min(stop, ext + k * atr[i])
        i += 1
    if pos != 0:
        xi[nt] = m - 1; px[nt] = c[m - 1]; nt += 1
    return ei[:nt], xi[:nt], side[:nt], pi[:nt], px[:nt]

def run(df, a, n, dev, k, L, cache={}):
    key = ('lrc', a, n, len(df))
    if key not in cache: cache[key] = lrc(df.close.values, n)
    sl, up, lo = cache[key]; sd = up - (up + lo) / 2; mid = (up + lo) / 2
    c = df.close.values
    sig = np.where((sl > 0) & (c < mid - dev * sd), 1, np.where((sl < 0) & (c > mid + dev * sd), -1, 0))
    ka = ('atr', a, L, len(df))
    if ka not in cache: cache[ka] = atr_rma(df.high.values, df.low.values, c, L)
    ei, xi, s, pi, px = sim(df.open.values, df.high.values, df.low.values, c, sig.astype(np.int64), cache[ka], k)
    t = pd.DataFrame({'t_in': df.index[ei], 't_out': df.index[xi], 'd': s, 'p_in': pi, 'p_out': px})
    yrs = (t.t_out - t.t_in).dt.total_seconds() / (365 * 86400)
    t['ret'] = t.d * np.log(t.p_out / t.p_in) - 2 * CUSTO[a] - t.d * FUND[a] / 100 * yrs
    return t

def stats(t, df):
    if len(t) == 0: return dict(tr=0, ret=0, pf=np.nan, win=np.nan, dd=0, cagr=0)
    r = t.ret.values; eq = np.cumsum(r); dd = (np.maximum.accumulate(np.maximum(eq, 0)) - eq).max()
    y = (df.index[-1] - df.index[0]).days / 365
    return dict(tr=len(t), ret=round(100 * (np.exp(r.sum()) - 1), 1), cagr=round(100 * (np.exp(r.sum() / y) - 1), 1),
                pf=round(r[r > 0].sum() / max(-r[r < 0].sum(), 1e-12), 2), win=round(100 * (r > 0).mean(), 1),
                dd=round(100 * (1 - np.exp(-dd)), 1), bp=round(1e4 * r.mean(), 1),
                bh=round(100 * (df.close.iloc[-1] / df.open.iloc[0] - 1), 1))

if __name__ == '__main__':
    grid = list(itertools.product([50, 100, 200, 300, 500], [1.5, 2, 2.5, 3], [1, 1.5, 2, 3, 4, 6], [14, 50]))
    rows = []; fix = []
    for a in ASSETS:
        df = bars(a); ins = df[df.index < CUT]; oos = df[df.index >= CUT]
        for nm, part in [('IS', ins), ('OOS', oos)]:
            fix.append(dict(ativo=a, per=nm, **stats(run(part, a, 200, 2, 2, 14), part)))
        for n, dev, k, L in grid:
            t = run(ins, a, n, dev, k, L)
            h1 = t[t.t_in < ins.index[0] + (ins.index[-1] - ins.index[0]) / 2].ret.sum(); h2 = t.ret.sum() - h1
            rows.append(dict(ativo=a, N=n, dev=dev, k=k, L=L, h1=h1, h2=h2, **stats(t, ins)))
        print(a, 'ok', flush=True)
    fix = pd.DataFrame(fix); print(fix.to_string()); fix.to_csv(os.path.join(OUT, 'fixo.csv'), index=False)
    g = pd.DataFrame(rows); g.to_csv(os.path.join(OUT, 'grid_is.csv'), index=False)
    best = []
    for a in ASSETS:
        x = g[(g.ativo == a) & (g.tr >= 50)].sort_values('cagr', ascending=False)
        pos = x[(x.h1 > 0) & (x.h2 > 0)]
        b = (pos if len(pos) else x).iloc[0]
        df = bars(a); oos = df[df.index >= CUT]
        so = stats(run(oos, a, int(b.N), b.dev, b.k, int(b.L)), oos)
        frac = (g[g.ativo == a].cagr > 0).mean()
        best.append(dict(ativo=a, N=b.N, dev=b.dev, k=b.k, L=b.L, IS_cagr=b.cagr, IS_pf=b.pf, IS_tr=b.tr, IS_dd=b.dd,
                         OOS_cagr=so['cagr'], OOS_pf=so['pf'], OOS_tr=so['tr'], OOS_dd=so['dd'], OOS_bh=so['bh'],
                         grade_pos=round(100 * frac)))
    best = pd.DataFrame(best); print(best.to_string()); best.to_csv(os.path.join(OUT, 'otimo_oos.csv'), index=False)
