"""Roda no XAU 1h as 10 configuracoes (3a selecao) selecionadas da planilha xau_1h_ate_dez2023.csv.

uso (na pasta scripts/):
    EDGE_END=2023-12-31 python rodar_selecionadas_xau1h.py   # mesmo periodo da planilha
    python rodar_selecionadas_xau1h.py                        # serie inteira
    EDGE_START=2024-01-01 python rodar_selecionadas_xau1h.py  # so fora da amostra
Imprime e grava results/selecionadas3_xau1h.csv com as mesmas colunas da planilha."""
import os, sys, io, contextlib
import pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
import study_tvlote4 as L4, study_tvlote8 as L8, study_tvlote16 as L16, study_tvlote20 as L20, study_tvlote25 as L25
import study_tvlote27 as L27, study_tvlote28 as L28, study_tvlote31 as L31, study_tvlote36 as L36

N = 'xau'
# (rotulo na planilha, funcao(nome, df1h, mm, rows) )
SEL = [
    ('tvlote16 edma l20 e20 ambos', lambda d, mm, r: L16.run_edma(N, d, mm, '', r, False, ln=20, e1=20, short_ok=True)),
    ('tvlote25 mst 20 m4 ambos', lambda d, mm, r: L25.run_mst(N, d, mm, '', r, False, ln=20, mult=4.0, short_ok=True)),
    ('tvlote4 ppst p5 f2.0 a10', lambda d, mm, r: L4.run_bars(N, d, *L4.ppst_signals(d, 5, 2.0, 10), '', r, verbose=False)),
    ('tvlote31 pse off0% ambos', lambda d, mm, r: L31.run_pse(N, d, mm, '', r, False, off=0.0, short_ok=True)),
    ('tvlote20 fline 50 1.0 ambos', lambda d, mm, r: L20.run_fline(N, d, mm, '', r, False, ln=50, dev=1.0, short_ok=True)),
    ('tvlote16 edma l20 e40 ambos', lambda d, mm, r: L16.run_edma(N, d, mm, '', r, False, ln=20, e1=40, short_ok=True)),
    ('tvlote36 cbo h13/rr2 ambos', lambda d, mm, r: L36.run_cbo(N, d, mm, '', r, False, hr=13, rr=2.0)),
    ('tvlote8 bbb len20 m2.0 ambos', lambda d, mm, r: L8.run_bbb(N, d, mm, '', r, False, length=20, mult=2.0, short_ok=True)),
    ('tvlote28 hvc h100 ambos', lambda d, mm, r: L28.run_hvc(N, d, mm, '', r, False, ln=100, short_ok=True)),
    ('tvlote27 doji sl1% ambos', lambda d, mm, r: L27.run_doji(N, d, mm, '', r, False, sl=0.01, short_ok=True)),
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
    pd.DataFrame(out).to_csv(os.path.join(D, 'results', 'selecionadas3_xau1h.csv'), index=False)
