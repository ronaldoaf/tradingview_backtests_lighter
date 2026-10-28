"""OOS (5a parte) da carteira das 20 de results/us100_4p/sel20.csv, peso igual, parametros congelados. Usa as
series de results/us100_4p_full (study_us100_4p.py com FULL=1); confere que p1..p4 batem com a selecao.
Grava results/us100_4p_full/oos.txt e oos.png."""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys_p = os.path.join(D, 'scripts')
import sys; sys.path.insert(0, sys_p); import tvlib as T
A = os.environ.get('ATIVO', 'us100'); SUF = os.environ.get('SUF', ''); K = os.environ.get('K', '20')   # ex.: ATIVO=wti SUF=_sem2004 K=10
R = os.path.join(D, 'results', A + '_4p' + SUF); F = os.path.join(D, 'results', A + '_4p' + SUF + '_full')
b = pd.read_csv(os.path.join(R, f'sel{K}.csv')); cols = {}; chk = []
for _, r in b.iterrows():
    l = str(r.lote).split('_')[0]; g = pd.read_csv(os.path.join(F, f'lote{l}.csv'))
    g['celula'] = g.apply(lambda x: ' '.join(str(x[c]) for c in ('TF', 'cfg') if c in x and pd.notna(x[c])), axis=1)
    h = g[(g.est == r.est) & (g.celula == r.celula)]; assert len(h) == 1, (r.est, r.celula, len(h))
    h = h.iloc[0]; chk.append(max(abs(h[f'p{q}'] - r[f'p{q}']) for q in range(1, 5)))
    cols[r.est] = pd.read_parquet(os.path.join(F, f'lote{l}_ser.parquet'))[int(h.sid)]
X = pd.DataFrame(cols).fillna(0.0); X = X[(X != 0).any(axis=1)]
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; corte = t0 + (t1 - t0) * 4 / 5
O = X[X.index > corte.normalize()]; cart = O.mean(axis=1); eq = (1 + cart).cumprod()
yrs = (O.index[-1] - O.index[0]).days / 365
px = m1.close[m1.index >= corte].resample('1D').last().dropna(); bh = px.iloc[-1] / px.iloc[0] - 1
bhr = px.pct_change().dropna()
ind = (1 + O).prod() - 1
with open(os.path.join(F, 'oos.txt'), 'w') as f:
    f.write(f'OOS {O.index[0].date()} a {O.index[-1].date()} ({yrs:.2f} anos); diferenca max p1..p4 vs selecao {max(chk):.2e}\n')
    f.write(f'carteira peso igual: total {eq.iloc[-1] - 1:+.2%} CAGR {eq.iloc[-1] ** (1 / yrs) - 1:+.1%} '
            f'Sharpe {cart.mean() / cart.std() * np.sqrt(len(cart) / yrs):.2f} vol {cart.std() * np.sqrt(len(cart) / yrs):.1%} '
            f'DD {(eq / eq.cummax() - 1).min():.1%}\n')
    f.write(f'B&H {A.upper()}: total {bh:+.2%} CAGR {(1 + bh) ** (1 / yrs) - 1:+.1%} Sharpe {bhr.mean() / bhr.std() * np.sqrt(len(bhr) / yrs):.2f} '
            f'DD {(px / px.cummax() - 1).min():.1%}\n')
    f.write(f'corr diaria carteira x B&H {cart.corr(bhr.reindex(cart.index).fillna(0)):.2f}; '
            f'estrategias positivas no OOS: {(ind > 0).sum()}/{len(b)}\n\npor estrategia (OOS):\n')
    f.write(pd.DataFrame({'celula': b.set_index('est').celula, 'oos': ind}).sort_values('oos', ascending=False)
            .to_string(float_format=lambda v: f'{v:+.1%}'))
plt.figure(figsize=(10, 5)); plt.plot(eq, label=f'carteira {len(b)} (peso igual)'); plt.plot(px / px.iloc[0], label=f'B&H {A.upper()}')
plt.title(f'{A.upper()} OOS'); plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig(os.path.join(F, 'oos.png'), dpi=110)
print(open(os.path.join(F, 'oos.txt')).read())
