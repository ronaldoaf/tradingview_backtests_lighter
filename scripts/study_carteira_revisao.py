"""Carteira das 6 aprovadas de antes que continuam aprovadas na revisao de 2026-10-23 (docs/APROVADAS.md: §4c, §8, §16,
§17, §18, §24), pesos iguais rebalanceados todo dia, ao lado da carteira de 8 (study_carteira8.py) e do B&H.
Antes = 2020-01-01..2023-05-16, depois = 2023-05-17 em diante. Retorno diario de study_aprovadas_corr.daily.
uso: python study_carteira_revisao.py  ->  results/study_carteira_revisao.txt"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_aprovadas_corr import EST, daily
from study_carteira8 import stats, OOS, INI

C6 = ['§4c Scalping ETH 30m', '§8 MA Consec ETH 4h', '§16 HULL+T3 ETH 1h', '§17 5 EMA ETH 4h', '§18 Wyckoff ETH 4h',
      '§24 Multi-MA BTC 4h']
C8 = ['§1 Trailing SL XAU 30m', '§21 Golden Edge WTI 30m', '§25 MACD+Stoch WTI 4h', '§6 ABCD BTC 1h', '§19 HA MACD BTC 1h',
      '§8 MA Consec ETH 4h', '§24 Multi-MA BTC 4h', '§13 Chandelier ETH 30m']


def main():
    R = {}; BH = {}
    for ativo in ('xau', 'wti', 'btc', 'eth'):
        m1 = T.load_m1v(ativo); mm = M1(m1); base = T.resample(m1, '15min').close; cache = {}
        BH[ativo.upper()] = base.resample('1D').last().dropna().pct_change()
        for rot, _, tf, fn in [e for e in EST if e[1] == ativo and e[0] in C6 + C8]:
            R[rot] = daily(fn(ativo, cache.setdefault(tf, T.resample(m1, tf)), mm)[1], base)[0]
    M = pd.DataFrame(R).fillna(0); tz = M.index.tz
    i0, oos = pd.Timestamp(INI, tz=tz), pd.Timestamp(OOS, tz=tz); M = M[M.index >= i0]
    B = pd.DataFrame(BH).reindex(M.index).fillna(0)
    p6, p8, bh = M[C6].mean(axis=1), M[C8].mean(axis=1), B.mean(axis=1)
    out = ['Carteira das 6 que continuam aprovadas: ' + ', '.join(C6)]
    out.append('\nCorrelacao das 6 antes do OOS\n' + M[C6][M.index < oos].corr().round(2).to_string())
    for nome, a, b in (('Antes do OOS', i0, oos), ('Depois do OOS', oos, None), ('Periodo todo', i0, None)):
        msk = (M.index >= a) & ((M.index < b) if b is not None else True)
        out.append(f'\n=== {nome}: {M.index[msk][0].date()}..{M.index[msk][-1].date()}')
        out.append(f'  {"Carteira 6 revisao":<30} {stats(p6[msk])}')
        out.append(f'  {"Carteira 8 (anterior)":<30} {stats(p8[msk])}')
        out.append(f'  {"B&H 4 ativos (pesos iguais)":<30} {stats(bh[msk])}')
        for k in B: out.append(f'  {"B&H " + k:<30} {stats(B[k][msk])}')
        for k in C6: out.append(f'  {k:<30} {stats(M[k][msk])}')
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', 'study_carteira_revisao.txt'), 'w').write(txt + '\n')
    pd.DataFrame({'carteira6': p6, 'carteira8': p8, 'bh4': bh}).to_csv(os.path.join(D, 'results', 'study_carteira_revisao_diario.csv'))


if __name__ == '__main__':
    main()
