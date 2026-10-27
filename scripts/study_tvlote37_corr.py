"""Correlacao diaria entre as celulas do lote 37 que entraram e as 5 aprovadas do lote 36 (uso: python study_tvlote37_corr.py)."""
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
import pandas as pd, tvlib as T, study_veredito as V
from study_tvlote6 import M1
C = [(36, 'kel', 'eth', '4h', 'k2/sl5 ambos'), (36, 'sqz', 'eth', '1D', 'e100 long'), (36, 'sqz', 'btc', '1D', 'e100 long'),
     (36, 'vrb', 'btc', '1h', 'n100 ambos'), (36, 'cbo', 'us100', '1h', 'h13/rr1 long'),
     (37, 'ckr', 'eth', '30min', 'n21/a1.5'), (37, 'tdw', 'eth', '1h', 'tdow'), (37, 'tdw', 'eth', '30min', 'tdow'),
     (37, 'dmx', 'eth', '30min', 'adx20 long'), (37, 'tdw', 'btc', '1h', 'tdow'), (37, 'tdw', 'btc', '30min', 'tdow'),
     (37, 'b4u', 'us100', '30min', 'f3'), (37, 'wmx', 'us100', '4h', 'o1 long')]
daily = {}
for a in sorted({c[2] for c in C}):
    m1 = T.load_m1v(a); mm = M1(m1); cache = {}
    for lote, est, a_, tf, cfg in [c for c in C if c[2] == a]:
        mod = importlib.import_module(f'study_tvlote{lote}'); kw = mod.KW(est, cfg)
        fn = lambda n, d, mm_, m1_, f=getattr(mod, 'run_' + est), kw=kw: f(n, d, mm_, '', **kw)
        rec, dly = V.run_cell(a, m1, mm, cache, (lote, est, a, tf, kw, fn)); daily[f'L{lote} {est} {a} {tf}'] = dly
txt = pd.DataFrame(daily).corr().round(2).to_string()
print(txt); open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'study_tvlote37_corr.txt'), 'w').write(txt + '\n')
