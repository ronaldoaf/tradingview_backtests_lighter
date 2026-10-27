"""Correlacao diaria entre as celulas do lote 36 que entraram (uso: python study_tvlote36_corr.py)."""
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, tvlib as T, study_veredito as V, study_tvlote36 as mod
from study_tvlote6 import M1
C = [('kel','eth','4h','k2/sl5 ambos'),('sqz','eth','1D','e100 long'),('sqz','btc','1D','e100 long'),
     ('vrb','btc','1h','n100 ambos'),('vst','btc','4h','b2 ambos'),('cbo','us100','1h','h13/rr1 long'),('c123','wti','30min','fiel ambos')]
daily = {}
for a in sorted({c[1] for c in C}):
    m1 = T.load_m1v(a); mm = M1(m1); cache = {}
    for est, a_, tf, cfg in [c for c in C if c[1] == a]:
        kw = mod.KW(est, cfg); fn = lambda n, d, mm_, m1_, f=getattr(mod, 'run_' + est), kw=kw: f(n, d, mm_, '', **kw)
        rec, dly = V.run_cell(a, m1, mm, cache, (36, est, a, tf, kw, fn)); daily[f'{est} {a} {tf}'] = dly
print(pd.DataFrame(daily).corr().round(2).to_string())
