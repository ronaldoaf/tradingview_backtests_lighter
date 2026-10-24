"""Compara as regras simples escolhidas antes do OOS (results/simples/escolhidas.pkl, de study_simples.py) com a
Carteira 8 das 34 e a Carteira 34 (retornos diarios das celulas em results/padrao/, de study_padrao.py).
Carteiras de regra simples: pesos iguais nos 5 ativos e nos 4 do resto (sem US100), rebalanceadas todo dia.
Mede tambem quanto do retorno diario de cada aprovada a regra simples do mesmo ativo explica (corr e R2).
uso: python study_simples_vs.py   -> results/study_simples_vs.txt"""
import os, sys, glob, pickle
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from study_carteira8 import stats

K8 = ['L3 occ HULL13 x5 XAU 1h', "L22 force BTC 4h {'fast': 5, 'slow': 50, 'short_ok': False}",
      "L23 tema ETH 15min {'short_ok': True}", "L23 crazy WTI 1h {'sll': 30}", "L25 tlb WTI 4h {'maf': False}",
      "L26 csq ETH 4h {'mfl': 14}", "L28 hamacd ETH 1h {'sltp': False}", "L29 bot WTI 1D {'k': 0.02}"]
OOS = pd.Timestamp('2023-05-17', tz='UTC'); INI = pd.Timestamp('2020-01-01', tz='UTC')


def main():
    cells = {}
    for f in glob.glob(os.path.join(D, 'results', 'padrao', '*.pkl')):
        cells.update(pickle.load(open(f, 'rb')))
    best, dc = pickle.load(open(os.path.join(D, 'results', 'simples', 'escolhidas.pkl'), 'rb'))
    idx = pd.date_range(INI, pd.Timestamp('2026-09-30', tz='UTC'), freq='1D', tz='UTC')
    M = pd.DataFrame({n: c['dly'].set_axis(c['dly'].index.normalize()) for n, c in cells.items()}).reindex(idx).fillna(0)
    S = pd.DataFrame({k: v.set_axis(v.index.normalize()) for k, v in dc.items()}).reindex(idx).fillna(0)
    tags = list(dict.fromkeys(t for t, _ in S.columns))
    P = {'Carteira 8 (das 34)': M[K8].mean(axis=1), 'Carteira 34': M.mean(axis=1)}
    for t in tags:
        P[f'{t} 5 ativos'] = S[t].mean(axis=1)
        P[f'{t} sem US100'] = S[t].drop(columns='us100').mean(axis=1)
    out = []
    for nome, a, b in (('Antes do OOS', INI, OOS), ('Depois do OOS', OOS, None), ('Periodo todo', INI, None)):
        msk = (idx >= a) & ((idx < b) if b is not None else True)
        out.append(f'\n=== {nome}: {idx[msk][0].date()}..{idx[msk][-1].date()}')
        for k, v in P.items():
            out.append(f'  {k:<38} {stats(v[msk])}')
    out.append('\nCorrelacao diaria com a Carteira 8 / Carteira 34 (periodo todo, depois do OOS):')
    for k, v in P.items():
        if k.startswith('Carteira'): continue
        oo = idx >= OOS
        out.append(f'  {k:<38} C8 {v.corr(P["Carteira 8 (das 34)"]):+.2f} / {v[oo].corr(P["Carteira 8 (das 34)"][oo]):+.2f}'
                   f'   C34 {v.corr(P["Carteira 34"]):+.2f} / {v[oo].corr(P["Carteira 34"][oo]):+.2f}')
    # quanto da Carteira 34 sobra depois de tirar a regra simples (regressao diaria, periodo todo)
    for t in tags:
        x = P[f'{t} 5 ativos']; y = P['Carteira 34']
        beta = np.cov(x, y)[0, 1] / x.var(); res = y - beta * x
        out.append(f'  Carteira 34 = {beta:.2f} x [{t}] + residuo; residuo: {stats(res)}')
    out.append('\nCada aprovada contra a regra simples do mesmo ativo (corr diaria, periodo todo):')
    out.append(f"  {'aprovada':<62} " + '  '.join(f'{t[:18]:>18}' for t in tags))
    for n, c in sorted(cells.items(), key=lambda x: x[1]['ativo']):
        out.append(f'  {n[:62]:<62} ' + '  '.join(f"{M[n].corr(S[(t, c['ativo'])]):>+18.2f}" for t in tags))
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', 'study_simples_vs.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
