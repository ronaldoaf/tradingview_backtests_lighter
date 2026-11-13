"""HMA Crossover Multi-Timeframe (CodeTrading, "cloned from a trading community").

Regras (4H, long-only):
  entrada: crossover(HMA(16), HMA(65)) E RSI(14) > 52 E close > linreg(close_D1, 14)
  saida  : crossunder(HMA(16), HMA(65))
Sinal no fechamento da barra 4H, execucao na abertura da seguinte. Sem stop.

Linreg diaria SEM look-ahead: usa so o valor do ULTIMO dia ja fechado no momento do fechamento
da barra 4H (o dia corrente, ainda aberto, nunca entra).
Variante 'ls': espelho para short (crossunder E RSI < 100-limite E close < linreg), saida no
crossover. Long e short sao independentes (nunca simultaneos, porque os cruzamentos alternam).

Protocolo: 5 ativos, base publicada + grade; terços do periodo; parametros escolhidos na 1a metade
e medidos na 2a; custo Lighter (spread + funding) e 2x/4x spread; controle aleatorio.
uso: python study_hmamtf.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tvlib as T
from tvlib import load_m1v, resample, hma, rsi_wilder, xover, xunder, summarize, book, line

ASSETS = sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']
BASE = (16, 65, 52, 14)
GRID = list(itertools.product([10, 16, 24], [45, 65, 90], [50, 52, 55], [14, 20, 50]))


def linreg(c, n):
    """ta.linreg(c, n, 0): valor da reta de minimos quadrados na ultima barra da janela."""
    x = np.arange(n, dtype=float); xm = x.mean(); sxx = ((x - xm) ** 2).sum()
    s = pd.Series(c)
    ym = s.rolling(n).mean()
    sxy = s.rolling(n).apply(lambda y: ((x - xm) * (y - y.mean())).sum(), raw=True)
    return (ym + sxy / sxx * (n - 1 - xm)).to_numpy()


def daily_lr_on_4h(d1, df, n):
    lr = linreg(d1.close.to_numpy(float), n)
    avail = d1.index + pd.Timedelta('1D')          # dia so fica disponivel apos fechar
    close_t = df.index + pd.Timedelta('4h')         # momento de fechamento da barra 4H
    k = avail.searchsorted(close_t, side='right') - 1
    out = np.where(k >= 0, lr[np.clip(k, 0, None)], np.nan)
    return out


def trades_for(df, d1, p, mode, cache):
    f, s, th, nlr = p
    c = df.close.to_numpy(float)
    key = ('h', f); cache.setdefault(key, hma(c, f)); hf = cache[key]
    key = ('h', s); cache.setdefault(key, hma(c, s)); hs = cache[key]
    cache.setdefault('rsi', rsi_wilder(c, 14)); r = cache['rsi']
    key = ('lr', nlr); cache.setdefault(key, daily_lr_on_4h(d1, df, nlr)); lr = cache[key]
    up, dn = xover(hf, hs), xunder(hf, hs)
    L = up & (r > th) & (c > lr)
    S = dn & (r < 100 - th) & (c < lr)
    tr = []; pos = 0; i0 = 0
    for i in range(len(df) - 1):
        j = i + 1
        if pos == 1 and dn[i]: tr.append((i0, j, 1)); pos = 0
        elif pos == -1 and up[i]: tr.append((i0, j, -1)); pos = 0
        if pos == 0:
            if L[i]: pos, i0 = 1, j
            elif mode == 'ls' and S[i]: pos, i0 = -1, j
    return tr


def run(df, d1, name, p, mode, cache, nsim=20, mult=1.0):
    tb = book(df, trades_for(df, d1, p, mode, cache), name)
    if mult != 1.0 and len(tb):
        tb['ret'] -= 2 * T.CUSTO[name] * (mult - 1); tb['ret_sf'] -= 2 * T.CUSTO[name] * (mult - 1)
    return tb


def sub(df, d1, a, b):
    m = (df.index >= a) & (df.index < b)
    return df[m], d1


def main():
    rows = []
    for name in ASSETS:
        m1 = load_m1v(name)
        df = resample(m1, '4h'); d1 = resample(m1, '1D'); del m1
        t0, t1 = df.index[0], df.index[-1]
        print(f'\n=== {name.upper()} 4H {t0.date()} -> {t1.date()} ({len(df)} barras)')
        for mode in ['long', 'ls']:
            cache = {}
            tb = run(df, d1, name, BASE, mode, cache)
            o = summarize(df, tb, name, minimo=5)
            if o:
                line(f'BASE {mode}', o); rows.append(dict(ativo=name, modo=mode, fase='base_full', p=BASE, **o))
            for mult in [2, 4]:
                tbm = run(df, d1, name, BASE, mode, cache, mult=mult)
                om = summarize(df, tbm, name, minimo=5, nsim=5)
                if om: line(f'BASE {mode} custo {mult}x', om)
            # terços
            edges = [t0 + (t1 - t0) * k / 3 for k in range(4)]
            for k in range(3):
                dfk = df[(df.index >= edges[k]) & (df.index < edges[k + 1])]
                ok = summarize(dfk, run(dfk, d1, name, BASE, mode, {}), name, minimo=3)
                if ok:
                    line(f'  terço {k+1} {mode}', ok)
                    rows.append(dict(ativo=name, modo=mode, fase=f'terco{k+1}', p=BASE, **ok))
            # escolha na 1a metade, medida na 2a
            mid = t0 + (t1 - t0) / 2
            dA = df[df.index < mid]; dB = df[df.index >= mid]
            cA, cB = {}, {}
            g = []
            for p in GRID:
                tA = run(dA, d1, name, p, mode, cA)
                if len(tA) < 8: continue
                eq = T.equity(dA, tA, name)
                g.append((eq['sharpe'], p))
            g.sort(reverse=True)
            for rank, (sh, p) in enumerate(g[:3]):
                oA = summarize(dA, run(dA, d1, name, p, mode, cA), name, minimo=3)
                oB = summarize(dB, run(dB, d1, name, p, mode, cB), name, minimo=3)
                if oA and oB:
                    line(f'  #{rank+1} {p} {mode} TREINO', oA); line(f'  #{rank+1} {p} {mode} TESTE', oB)
                    rows.append(dict(ativo=name, modo=mode, fase=f'treino#{rank+1}', p=p, **oA))
                    rows.append(dict(ativo=name, modo=mode, fase=f'teste#{rank+1}', p=p, **oB))
            oB = summarize(dB, run(dB, d1, name, BASE, mode, {}), name, minimo=3)
            if oB:
                line(f'  BASE {mode} TESTE', oB); rows.append(dict(ativo=name, modo=mode, fase='base_teste', p=BASE, **oB))
            # fração da grade positiva no período todo (vizinhança)
            cf = {}; pos = 0; tot = 0
            for p in GRID:
                eq = T.equity(df, run(df, d1, name, p, mode, cf), name); tot += 1; pos += eq['cagr'] > 0
            print(f'  grade {mode}: {pos}/{tot} celulas com CAGR liquido > 0')
            rows.append(dict(ativo=name, modo=mode, fase='grade_pos', p=None, trades=pos, por_ano=tot))
    out = os.path.join(T.D, 'results', f'study_hmamtf_resumo_{"_".join(ASSETS)}.csv')
    pd.DataFrame(rows).to_csv(out, index=False); print('->', out)


if __name__ == '__main__':
    main()
