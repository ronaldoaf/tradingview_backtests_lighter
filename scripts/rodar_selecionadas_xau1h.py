"""Roda no XAU 1h as 9 configuracoes selecionadas da planilha xau_1h_ate_dez2023.csv.

uso (na pasta scripts/):
    EDGE_END=2023-12-31 python rodar_selecionadas_xau1h.py   # mesmo periodo da planilha
    python rodar_selecionadas_xau1h.py                        # serie inteira
    EDGE_START=2024-01-01 python rodar_selecionadas_xau1h.py  # so fora da amostra
Imprime e grava results/selecionadas_xau1h.csv com as mesmas colunas da planilha."""
import os, sys, io, contextlib
import pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
import study_tvlote3 as L3, study_tvlote8 as L8, study_tvlote9 as L9, study_tvlote10 as L10
import study_tvlote22 as L22, study_tvlote24 as L24, study_tvlote26 as L26, study_tvlote30 as L30, study_tvlote32 as L32

N = 'xau'
# (rotulo na planilha, funcao(nome, df1h, mm, rows) )
SEL = [
    ('tvlote22 turtle 20/10 n2 ambos', lambda d, mm, r: L22.run_turtle(N, d, mm, '', r, False, ent=20, ext=10, mult=2.0, short_ok=True)),
    ('tvlote9 micu sl0.001 tp0 trail0 sess0 ambos', lambda d, mm, r: L9.run_micu(N, d, '', r, False, sl=0.001, tp=0.0, trail=False, sess=False, short_ok=True)),
    ('tvlote10 piv 4/1', lambda d, mm, r: L10.run_piv(N, d, '', r, False, lb=4, rb=1, long_only=False)),
    ('tvlote30 mbf l18 ambos', lambda d, mm, r: L30.run_mbf(N, d, mm, '', r, False, ln=18, short_ok=True)),
    ('tvlote26 rsx r50/25 ambos', lambda d, mm, r: L26.run_rsx(N, d, mm, '', r, False, rl=50, ml=25, short_ok=True)),
    ('tvlote32 hic h12 ambos', lambda d, mm, r: L32.run_hic(N, d, mm, '', r, False, keh=12, short_ok=True)),
    ('tvlote3 occ hon SMMA21 x1', lambda d, mm, r: L3.run(N, d, *L3.occ_signals(d, kind='SMMA', ln=21, mult=1, peek=False), '', r, verbose=False)),
    ('tvlote8 vwap m2.0 match1 tp0.0 ambos', lambda d, mm, r: L8.run_vwap(N, d, mm, '', r, False, mult=2.0, matched=True, tpb=0.0, short_ok=True)),
    ('tvlote24 vws semniveis ambos', lambda d, mm, r: L24.run_vws(N, d, mm, '', r, False, lv=False, short_ok=True)),
]

if __name__ == '__main__':
    m1 = T.load_m1v(N)
    ini = os.environ.get('EDGE_START')
    if ini:
        m1 = m1[m1.index >= pd.Timestamp(ini, tz='UTC')]
    mm = M1(m1)
    d = T.resample(m1, '1h')
    print(f'XAU 1h de {d.index[0]:%Y-%m-%d} a {d.index[-1]:%Y-%m-%d}')
    out = []
    for rot, fn in SEL:
        rows = []
        with contextlib.redirect_stdout(io.StringIO()):
            fn(d, mm, rows)
        r = dict(rows[-1]) if rows else {}
        r['selecionada'] = rot
        out.append(r)
        print(f"{rot:45s} trades {r.get('trades', 0):5} CAGR {r.get('cagr', float('nan')):+7.1%} "
              f"B&H {r.get('bh', float('nan')):+6.1%} Sharpe {r.get('sharpe', float('nan')):+5.2f} "
              f"DD {r.get('dd', float('nan')):+5.0%} t {r.get('t', float('nan')):+5.2f}")
    pd.DataFrame(out).to_csv(os.path.join(D, 'results', 'selecionadas_xau1h.csv'), index=False)
