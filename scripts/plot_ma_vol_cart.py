"""Curva de capital da carteira escolhida (4h SMA150, metade acima de 20% a.a.) vs B&H de cada ativo."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from tvlib import load_m1v
from study_ma_vol_cart import AT, prep, FUND, CUSTO
m1s = {a: load_m1v(a) for a in AT}
bars, idx, dt, t0, t1 = prep('4h', m1s)
ro = {a: np.log(b.open.shift(-1) / b.open).fillna(0.0).reindex(idx).fillna(0.0) for a, b in bars.items()}
pos = {}
for a, b in bars.items():
    ma = b.close.rolling(150).mean(); sig = np.sign(b.close - ma).where(ma.notna(), 0.0)
    pos[a] = sig.shift(1).fillna(0.0).reindex(idx).ffill().fillna(0.0) / 5
base = sum(pos[a] * ro[a] for a in AT); dly = base.resample('1D').sum()
vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1)
w = pd.Series(np.where(vol > 0.20, 0.5, 1.0), dly.index).reindex(idx.normalize()).to_numpy()
w = pd.Series(np.nan_to_num(w, nan=1.0), idx)
r = 0.0
for a in AT:
    q = pos[a] * w
    r = r + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a] - q * FUND[a] / 100 * dt * (ro[a] != 0)
m = (idx >= t0) & (idx <= t1)
fig, ax = plt.subplots(figsize=(12, 6.5))
cols = {'xau': '#c9a227', 'us100': '#4c78a8', 'wti': '#7f7f7f', 'btc': '#f58518', 'eth': '#9467bd'}
fim = {}
for a in AT:
    e = np.exp(ro[a][m].cumsum()); fim[a] = e.iloc[-1]
    ax.plot(e.index, e, lw=1, color=cols[a], alpha=.8, label=f'{a.upper()} B&H (x{e.iloc[-1]:.2f})')
eb = np.exp((sum(ro[a] for a in AT) / 5)[m].cumsum())
ax.plot(eb.index, eb, lw=1.5, ls='--', color='k', label=f'Carteira B&H 1/5 (x{eb.iloc[-1]:.2f})')
eq = np.exp(r[m].cumsum())
ax.plot(eq.index, eq, lw=2.4, color='#d62728', label=f'Estratégia, com funding (x{eq.iloc[-1]:.2f})')
for f in (0.6, 0.8):
    ax.axvline(t0 + (t1 - t0) * f, color='gray', ls=':', lw=1)
ax.text(t0 + (t1 - t0) * 0.3, 0.97, 'treino', transform=ax.get_xaxis_transform(), ha='center')
ax.text(t0 + (t1 - t0) * 0.7, 0.97, 'validação', transform=ax.get_xaxis_transform(), ha='center')
ax.text(t0 + (t1 - t0) * 0.9, 0.97, 'teste', transform=ax.get_xaxis_transform(), ha='center')
ax.set_yscale('log'); ax.set_ylabel('capital (início = 1, escala log)'); ax.grid(alpha=.3)
ax.set_title('Carteira 5 ativos: 4h SMA150 comprado/vendido, metade com vol > 20% a.a. vs buy & hold (preço, sem funding)')
ax.legend(loc='upper left', fontsize=9); fig.tight_layout()
fig.savefig('../results/ma_vol_cart_curva.png', dpi=130)
dd = lambda s: float((s / s.cummax() - 1).min() * 100)
print('estrat', eq.iloc[-1], dd(eq), 'cart', eb.iloc[-1], dd(eb), {a: round(fim[a], 2) for a in AT})
