"""Roda no XAU 1h as 8 configuracoes (2a selecao) selecionadas da planilha xau_1h_ate_dez2023.csv.

uso (na pasta scripts/):
    EDGE_END=2023-12-31 python rodar_selecionadas_xau1h.py   # mesmo periodo da planilha
    python rodar_selecionadas_xau1h.py                        # serie inteira
    EDGE_START=2024-01-01 python rodar_selecionadas_xau1h.py  # so fora da amostra
Imprime e grava results/selecionadas2_xau1h.csv com as mesmas colunas da planilha."""
import os, sys, io, contextlib
import pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
import study_tvlote12b as L12b, study_tvlote14 as L14, study_tvlote18 as L18, study_tvlote22 as L22
import study_tvlote25 as L25, study_tvlote26 as L26, study_tvlote37 as L37

N = 'xau'
# (rotulo na planilha, funcao(nome, df1h, mm, rows) )
SEL = [
    ('tvlote14 hap 0.01/0.01/0.1 ambos', lambda d, mm, r: L14.run_hap(N, d, mm, '', r, False, start=0.01, inc=0.01, mx=0.1, short_ok=True)),
    ('tvlote25 thma 40 ambos', lambda d, mm, r: L25.run_thma(N, d, mm, '', r, False, ln=40, short_ok=True)),
    ('tvlote26 pprs pv6/3 ambos', lambda d, mm, r: L26.run_pprs(N, d, mm, '', r, False, lb=6, rb=3, short_ok=True)),
    ('tvlote22 psarc n1 0.01/0.1 ambos', lambda d, mm, r: L22.run_psarc(N, d, mm, '', r, False, nb=1, start=0.01, mx=0.1, short_ok=True)),
    ('tvlote25 sr 10 ambos', lambda d, mm, r: L25.run_sr(N, d, mm, '', r, False, lb=10, short_ok=True)),
    ('tvlote37 dmm n9 ambos', lambda d, mm, r: L37.run_dmm(N, d, mm, '', r, False, n=9, short_ok=True)),
    ('tvlote18 savwap prd20 ambos', lambda d, mm, r: L18.run_savwap(N, d, mm, '', r, False, prd=20, shorts=True)),
    ('tvlote12b zig lb6 dmi0 cond ambos', lambda d, mm, r: L12b.run_zig(N, d, mm, '', r, False, h1=d, m15=T.resample(mm_m1[0], '15min'), lb=6, use_dmi=False, rr=False, short_ok=True)),
]
mm_m1 = []

if __name__ == '__main__':
    m1 = T.load_m1v(N)
    ini = os.environ.get('EDGE_START')
    if ini:
        m1 = m1[m1.index >= pd.Timestamp(ini, tz='UTC')]
    mm = M1(m1); mm_m1.append(m1)
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
    pd.DataFrame(out).to_csv(os.path.join(D, 'results', 'selecionadas2_xau1h.csv'), index=False)
