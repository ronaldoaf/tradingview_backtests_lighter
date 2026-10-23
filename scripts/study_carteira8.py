"""Carteira de 8 aprovadas com a menor correlacao absoluta media entre si (matriz antes do OOS,
results/study_aprovadas_corr.csv), pesos iguais rebalanceados todo dia. Antes = 2020-01-01..2023-05-16, depois
(OOS de todas) = 2023-05-17 em diante.
uso: python study_carteira8.py  ->  results/study_carteira8.txt"""
import os, sys, itertools
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_aprovadas_corr import EST, daily

OOS = '2023-05-17'; INI = '2020-01-01'


def escolhe(C, k=8):
    """Busca local (todas as trocas 1 por 1) a partir de varios pontos; minimiza a media de |corr| dos pares."""
    A = C.abs().to_numpy(); n = len(A); best = (9, None); rng = np.random.default_rng(0)
    f = lambda s: A[np.ix_(s, s)][np.triu_indices(k, 1)].mean()
    for _ in range(300):
        s = list(rng.choice(n, k, replace=False)); v = f(s); mel = True
        while mel:
            mel = False
            for i, j in itertools.product(range(k), range(n)):
                if j in s: continue
                t = s.copy(); t[i] = j; w = f(t)
                if w < v - 1e-12: s, v, mel = t, w, True
        if v < best[0]: best = (v, sorted(s))
    return [C.index[i] for i in best[1]], best[0]


def stats(x):
    x = x.dropna(); eq = np.exp(np.log1p(x).cumsum()); yrs = (x.index[-1] - x.index[0]).days / 365.25
    sh = x.mean() / x.std() * np.sqrt(365) if x.std() > 0 else np.nan
    return f'CAGR {eq.iloc[-1] ** (1 / yrs) - 1:+7.1%}  Sharpe {sh:+5.2f}  DD {(eq / eq.cummax() - 1).min():+5.0%}  vol {x.std() * np.sqrt(365):4.0%}'


def main():
    C = pd.read_csv(os.path.join(D, 'results', 'study_aprovadas_corr.csv'), index_col=0)
    sel, v = escolhe(C)
    R = {}; BH = {}
    for ativo in ('xau', 'wti', 'btc', 'eth'):
        es = [e for e in EST if e[1] == ativo and e[0] in sel]
        m1 = T.load_m1v(ativo); mm = M1(m1); base = T.resample(m1, '15min').close; cache = {}
        BH[ativo.upper()] = base.resample('1D').last().pct_change()
        for rot, _, tf, fn in es:
            R[rot] = daily(fn(ativo, cache.setdefault(tf, T.resample(m1, tf)), mm)[1], base)[0]
    tz = R[sel[0]].index.tz; i0, oos = pd.Timestamp(INI, tz=tz), pd.Timestamp(OOS, tz=tz)
    M = pd.DataFrame(R)[sel].fillna(0); M = M[M.index >= i0]
    B = pd.DataFrame(BH).fillna(0); B = B[B.index >= i0]
    port = M.mean(axis=1); bh = B.mean(axis=1)
    out = [f'Escolhidas (|corr| media entre os pares antes do OOS = {v:.3f}):']
    sub = C.loc[sel, sel]; out += ['  ' + s for s in sel]
    out.append('\nMatriz das 8 (antes do OOS)\n' + sub.round(2).to_string())
    for nome, a, b in (('Antes do OOS', i0, oos), ('Depois do OOS', oos, None), ('Periodo todo', i0, None)):
        msk = (M.index >= a) & ((M.index < b) if b is not None else True)
        out.append(f'\n=== {nome}: {M.index[msk][0].date()}..{M.index[msk][-1].date()}')
        out.append(f'  {"Carteira 8 (pesos iguais)":<30} {stats(port[msk])}')
        out.append(f'  {"B&H 4 ativos (pesos iguais)":<30} {stats(bh[msk])}')
        for k in B: out.append(f'  {"B&H " + k:<30} {stats(B[k][msk])}')
        for k in sel: out.append(f'  {k:<30} {stats(M[k][msk])}')
        out.append(f'  corr media dos pares no trecho: {M[msk].corr().where(np.triu(np.ones((8, 8), bool), 1)).stack().mean():+.2f}')
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', 'study_carteira8.txt'), 'w').write(txt + '\n')
    pd.DataFrame({'carteira': port, 'bh4': bh}).to_csv(os.path.join(D, 'results', 'study_carteira8_diario.csv'))


if __name__ == '__main__':
    main()
