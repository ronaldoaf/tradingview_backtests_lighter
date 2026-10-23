"""Carteira com as 34 aprovadas no criterio novo (results/study_veredito.csv, coluna carteira), pesos iguais rebalanceados
todo dia, ao lado das carteiras de 6 e 8 (results/study_carteira_revisao_diario.csv) e do B&H dos 4 ativos.
Retornos diarios = equity composta trade a trade de cada celula (cache de study_veredito.py em results/veredito/).
uso: python study_carteira34.py [k]  ->  results/study_carteira34.txt; com k, mais a sub-carteira das k de menor |corr|
media entre os pares antes do OOS -> results/study_carteira34_k<k>.txt"""
import os, sys, glob, pickle
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from study_carteira8 import stats, escolhe, OOS, INI


def main(k=None):
    daily = {}
    for f in glob.glob(os.path.join(D, 'results', 'veredito', '*.pkl')):
        daily.update(pickle.load(open(f, 'rb'))[1])
    R = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv'))
    C = R[R.carteira]
    M = pd.DataFrame({r.nome: daily[(r.ativo, r.lote, r.est, r.tf, r.cfg)] for r in C.itertuples()})
    M.index = M.index.normalize()
    O = pd.read_csv(os.path.join(D, 'results', 'study_carteira_revisao_diario.csv'), index_col=0, parse_dates=True)
    O.index = O.index.normalize()
    tz = M.index.tz; i0, oos = pd.Timestamp(INI, tz=tz), pd.Timestamp(OOS, tz=tz)
    M = M[M.index >= i0].reindex(O.index[O.index >= i0]).fillna(0)
    port = M.mean(axis=1); sub = None
    if k:
        sel, v = escolhe(M[M.index < oos].corr(min_periods=120), k)
        sub = M[sel].mean(axis=1)
    out = [f'Carteira das {len(C)} aprovadas (criterio novo), pesos iguais: ' + ', '.join(C.nome)]
    out.append(f'Por ativo: ' + ', '.join(f'{k.upper()} {v}' for k, v in C.ativo.value_counts().items()))
    if k:
        out.append(f'\nAs {k} de menor |corr| media antes do OOS ({v:.3f}): ' + ', '.join(sel))
        out.append(M[sel][M.index < oos].corr().round(2).to_string())
    for nome, a, b in (('Antes do OOS', i0, oos), ('Depois do OOS', oos, None), ('Periodo todo', i0, None)):
        msk = (M.index >= a) & ((M.index < b) if b is not None else True)
        out.append(f'\n=== {nome}: {M.index[msk][0].date()}..{M.index[msk][-1].date()}')
        if k: out.append(f'  {f"Carteira {k} (das {len(C)})":<30} {stats(sub[msk])}')
        out.append(f'  {f"Carteira {len(C)}":<30} {stats(port[msk])}')
        for col, lab in (('carteira6', 'Carteira 6 revisao'), ('carteira8', 'Carteira 8 anterior'), ('bh4', 'B&H 4 ativos')):
            out.append(f'  {lab:<30} {stats(O[col].reindex(M.index)[msk])}')
        out.append(f'  corr media dos pares no trecho: {M[msk].corr().where(np.triu(np.ones((len(C),) * 2, bool), 1)).stack().mean():+.2f}')
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', f'study_carteira34{f"_k{k}" if k else ""}.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main(int(sys.argv[1]) if sys.argv[1:] else None)
