"""Carteira de 8 das 34 (mesma escolha de study_carteira94.py) com pesos pelo inverso da volatilidade, ao lado dos
pesos iguais. Movel: vol dos retornos diarios nos ultimos N dias ate ONTEM (sem olhar o futuro), contando os dias
parados; peso ~ 1/vol, normalizado para somar 1, rebalanceado todo dia. Fixo: 1/vol medida antes do OOS.
uso: python study_carteira8_ivol.py -> results/study_carteira8_ivol.txt"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from study_carteira8 import stats, escolhe, OOS, INI
from study_carteira94 import diarias34


def ivol(M, n):
    v = M.rolling(n, min_periods=20).std().shift(1)
    w = (1 / v.where(v > 1e-4)).fillna(0); w = w.div(w.sum(axis=1), axis=0)
    return (M * w).sum(axis=1), w


def main():
    M = pd.DataFrame(diarias34()); M.index = M.index.normalize(); M = M.groupby(level=0).sum(min_count=1)
    O = pd.read_csv(os.path.join(D, 'results', 'study_carteira_revisao_diario.csv'), index_col=0, parse_dates=True)
    O.index = O.index.normalize()
    tz = M.index.tz; i0, oos = pd.Timestamp(INI, tz=tz), pd.Timestamp(OOS, tz=tz)
    M = M[M.index >= i0].reindex(O.index[O.index >= i0]).fillna(0)
    sel, _ = escolhe(M[M.index < oos].corr(min_periods=120).fillna(0), 8); S = M[sel]
    vf = S[S.index < oos].std(); wf = (1 / vf) / (1 / vf).sum()
    cols = {'Pesos iguais': S.mean(axis=1), 'Inv-vol fixo (antes do OOS)': (S * wf).sum(axis=1)}
    W = {}
    for n in (30, 60, 120):
        cols[f'Inv-vol movel {n}d'], W[n] = ivol(S, n)
    eq = cols['Pesos iguais']
    for lab in list(cols):  # mesma vol da de pesos iguais antes do OOS, para comparar CAGR com o mesmo risco
        if lab == 'Pesos iguais': continue
        k = eq[eq.index < oos].std() / cols[lab][cols[lab].index < oos].std()
        cols[lab + f' x{k:.2f}'] = cols[lab] * k
    cols['B&H 4 ativos'] = O.bh4.reindex(M.index)
    out = ['Carteira 8 das 34: ' + ', '.join(sel), '\nPesos fixos (1/vol antes do OOS):']
    out += [f'  {s:<55} {wf[s]:5.1%}   vol {vf[s] * np.sqrt(365):4.0%}' for s in sel]
    out.append('\nPeso medio no movel 60d depois do OOS:')
    out += [f'  {s:<55} {W[60][W[60].index >= oos][s].mean():5.1%}' for s in sel]
    for nome, a, b in (('Antes do OOS', i0, oos), ('Depois do OOS', oos, None), ('Periodo todo', i0, None)):
        msk = (M.index >= a) & ((M.index < b) if b is not None else True)
        out.append(f'\n=== {nome}: {M.index[msk][0].date()}..{M.index[msk][-1].date()}')
        out += [f'  {lab:<38} {stats(x[msk])}' for lab, x in cols.items()]
    txt = '\n'.join(out); print(txt)
    open(os.path.join(D, 'results', 'study_carteira8_ivol.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
