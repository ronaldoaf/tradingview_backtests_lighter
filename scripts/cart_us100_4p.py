"""Carteira das 20 de results/us100_4p/sel20.csv com peso proporcional a 1/vol dos retornos diarios (vol medida nas
4 partes; o OOS nao entra). Rebalanceio diario. Compara com peso igual. Grava results/us100_4p/carteira20.txt e .png."""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'us100_4p')
b = pd.read_csv(os.path.join(R, 'sel20.csv'))
X = pd.concat([pd.read_parquet(os.path.join(R, f"lote{str(l).split('_')[0]}_ser.parquet"))[int(s)].rename(e)
               for l, s, e in zip(b.lote, b.sid, b.est)], axis=1).fillna(0.0)
X = X[(X != 0).any(axis=1)]   # so dias com barra
w = 1 / X.std(); w /= w.sum()
c0 = X.index[0]; c4 = X.index[-1]; cortes = [c0 + (c4 - c0) * k / 4 for k in range(5)]


def stats(r):
    eq = (1 + r).cumprod(); yrs = (r.index[-1] - r.index[0]).days / 365
    parts = [float((1 + r[(r.index >= cortes[k]) & (r.index <= cortes[k + 1])]).prod() - 1) for k in range(4)]
    return dict(total=eq.iloc[-1] - 1, cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * np.sqrt(len(r) / yrs),
                dd=(eq / eq.cummax() - 1).min(), vol=r.std() * np.sqrt(len(r) / yrs), **{f'p{k+1}': p for k, p in enumerate(parts)}), eq


si, ei = stats(X @ w); se, ee = stats(X.mean(axis=1))
with open(os.path.join(R, 'carteira20.txt'), 'w') as f:
    f.write(f"{X.index[0].date()} a {X.index[-1].date()} (4 partes, sem OOS)\n")
    for n, s in (('inv-vol', si), ('peso igual', se)):
        f.write(f"{n:10s} total {s['total']:+.0%} CAGR {s['cagr']:+.1%} Sharpe {s['sharpe']:.2f} vol {s['vol']:.1%} DD {s['dd']:.1%} | "
                + ' '.join(f"P{k} {s[f'p{k}']:+.1%}" for k in range(1, 5)) + '\n')
    f.write('\npesos inv-vol:\n' + pd.DataFrame({'nome': b.nome.fillna('').values, 'celula': b.celula.values, 'peso': w.values,
                                                 'vol_aa': (X.std() * np.sqrt(252)).values}, index=b.est).sort_values('peso', ascending=False)
            .to_string(float_format=lambda v: f'{v:.1%}'))
plt.figure(figsize=(10, 5)); plt.plot(ei, label='inv-vol'); plt.plot(ee, label='peso igual'); plt.yscale('log')
plt.title('US100: carteira das 20 (4 partes, sem OOS)'); plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(R, 'carteira20.png'), dpi=110)
print(open(os.path.join(R, 'carteira20.txt')).read())
