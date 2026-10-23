"""Reroda a grade de um lote so no US100 e so no periodo antes do OOS (1a metade das barras, como na robustez).
Grava results/study_tvloteN_is_us100_grid.csv.
uso: python study_us100_is.py N"""
import os, sys, importlib
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
_load = T.load_m1v


def load_is(name):
    m1 = _load(name); c15 = T.resample(m1, '15min'); corte = c15.index[len(c15) // 2]
    print(f'  corte OOS {corte}', flush=True)
    return m1[m1.index < corte]


T.load_m1v = load_is
N = sys.argv[1]; L = importlib.import_module(f'study_tvlote{N}')
_s = L.summary
L.summary = lambda g, name, tag='x': _s(g, name, f'tvlote{N}_is')
L.main(['us100'])
