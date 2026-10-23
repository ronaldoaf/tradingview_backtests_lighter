"""Carteira das k aprovadas de menor |corr| media entre os pares antes do OOS, escolhidas entre as 34 do veredito
(results/study_veredito.csv, carteira) e as 60 do resgate (results/study_resgate.csv, entra), pesos iguais
rebalanceados todo dia; ao lado da carteira de 8 das 34, da de 94 e do B&H dos 4 ativos.
Diarias: as do resgate vem de results/resgate/*.pkl; as das 34 sao recalculadas e guardadas em results/resgate/ap34.pkl.
uso: python study_carteira94.py [k=10] -> results/study_carteira94_k<k>.txt"""
import os, sys, glob, pickle
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_veredito as V
from study_tvlote6 import M1
from study_carteira8 import stats, escolhe, OOS, INI


def diarias34():
    f = os.path.join(D, 'results', 'resgate', 'ap34.pkl')
    if os.path.exists(f): return pickle.load(open(f, 'rb'))
    ref = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv')); ap = ref[ref.carteira]
    aprov = {(r.lote, r.est, r.ativo, r.tf, r.cfg): r.nome for r in ap.itertuples()}; out = {}
    for a in sorted(ap.ativo.unique()):
        m1 = T.load_m1v(a); mm = M1(m1); cache = {}
        for c in V.ensure_aprov(V.cells()):
            key = (c[0], c[1], c[2], c[3], str(c[4]))
            if c[2] == a and key in aprov and aprov[key] not in out:
                out[aprov[key]] = V.run_cell(a, m1, mm, cache, c)[1]
    pickle.dump(out, open(f, 'wb')); return out


def main(k=10):
    d34 = diarias34(); dn = {}
    for f in glob.glob(os.path.join(D, 'results', 'resgate', '*_[0-9]*.pkl')):
        dn.update(pickle.load(open(f, 'rb'))[1])
    N = pd.read_csv(os.path.join(D, 'results', 'study_resgate.csv')); N = N[N.entra]
    M = pd.DataFrame({**d34, **{n: dn[n] for n in N.nome}}); M.index = M.index.normalize()
    M = M.groupby(level=0).sum(min_count=1)
    O = pd.read_csv(os.path.join(D, 'results', 'study_carteira_revisao_diario.csv'), index_col=0, parse_dates=True)
    O.index = O.index.normalize()
    tz = M.index.tz; i0, oos = pd.Timestamp(INI, tz=tz), pd.Timestamp(OOS, tz=tz)
    M = M[M.index >= i0].reindex(O.index[O.index >= i0]).fillna(0)
    pre = M[M.index < oos]
    sel, v = escolhe(pre.corr(min_periods=120).fillna(0), k)
    s8, v8 = escolhe(pre[list(d34)].corr(min_periods=120).fillna(0), 8)
    cols = {f'Carteira {k} (das {M.shape[1]})': M[sel].mean(axis=1), 'Carteira 8 (das 34)': M[s8].mean(axis=1),
            f'Carteira {M.shape[1]}': M.mean(axis=1), 'Carteira 34': M[list(d34)].mean(axis=1),
            'B&H 4 ativos': O.bh4.reindex(M.index)}
    out = [f'As {k} de menor |corr| media antes do OOS entre as {M.shape[1]} aprovadas ({v:.3f}):']
    out += ['  ' + s + ('' if s in d34 else '  [resgate]') for s in sel]
    out.append(pre[sel].corr().round(2).to_string())
    out.append(f'\nCarteira 8 das 34 ({v8:.3f}): ' + ', '.join(s8))
    for nome, a, b in (('Antes do OOS', i0, oos), ('Depois do OOS', oos, None), ('Periodo todo', i0, None)):
        msk = (M.index >= a) & ((M.index < b) if b is not None else True)
        out.append(f'\n=== {nome}: {M.index[msk][0].date()}..{M.index[msk][-1].date()}')
        out += [f'  {lab:<30} {stats(x[msk])}' for lab, x in cols.items()]
        out += [f'    {s:<48} {stats(M[s][msk])}' for s in sel]
    txt = '\n'.join(out); print(txt)
    open(os.path.join(D, 'results', f'study_carteira94_k{k}.txt'), 'w').write(txt + '\n')
    pd.DataFrame(cols).to_csv(os.path.join(D, 'results', f'study_carteira94_k{k}_diario.csv'))


if __name__ == '__main__':
    main(int(sys.argv[1]) if sys.argv[1:] else 10)
