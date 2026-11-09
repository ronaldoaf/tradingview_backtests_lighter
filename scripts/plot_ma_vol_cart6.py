"""Curva da carteira de 6 (4h SMA150, metade acima de 15% a.a., escolhida pelo treino) vs B&H de cada ativo."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import study_ma_vol_cart6  # registra xag
import study_ma_vol_cart as S
from study_engulf_psar import CUSTO, FUND
AT = S.AT; N = len(AT)
m1s = {a: S.load_m1v(a) for a in AT}
bars, idx, dt, t0, t1 = S.prep('4h', m1s)
ro = {a: np.log(b.open.shift(-1) / b.open).fillna(0.0).reindex(idx).fillna(0.0) for a, b in bars.items()}
def curva(n, x):
    pos = {}
    for a, b in bars.items():
        ma = b.close.rolling(n).mean(); sig = np.sign(b.close - ma).where(ma.notna(), 0.0)
        pos[a] = sig.shift(1).fillna(0.0).reindex(idx).ffill().fillna(0.0) / N
    dly = sum(pos[a] * ro[a] for a in AT).resample('1D').sum()
    vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1)
    w = pd.Series(np.where(vol > x, 0.5, 1.0), dly.index).reindex(idx.normalize()).to_numpy()
    w = pd.Series(np.nan_to_num(w, nan=1.0), idx); r = 0.0
    for a in AT:
        q = pos[a] * w
        r = r + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a] - q * FUND[a] / 100 * dt * (ro[a] != 0)
    return r
m = (idx >= t0) & (idx <= t1)
fig, ax = plt.subplots(figsize=(12, 6.5))
cols = {'xau': '#c9a227', 'us100': '#4c78a8', 'wti': '#7f7f7f', 'btc': '#f58518', 'eth': '#9467bd', 'xag': '#17becf'}
dd = lambda s: (s / s.cummax() - 1).min() * 100
for a in AT:
    e = np.exp(ro[a][m].cumsum())
    ax.plot(e.index, e, lw=1, color=cols[a], alpha=.8, label=f'{a.upper()} B&H (x{e.iloc[-1]:.2f})')
eb = np.exp((sum(ro[a] for a in AT) / N)[m].cumsum())
ax.plot(eb.index, eb, lw=1.5, ls='--', color='k', label=f'Carteira B&H 1/6 (x{eb.iloc[-1]:.2f}, DD {dd(eb):.0f}%)')
eq = np.exp(curva(150, 0.15)[m].cumsum())
ax.plot(eq.index, eq, lw=2.4, color='#d62728', label=f'Estratégia SMA150, 15% (x{eq.iloc[-1]:.2f}, DD {dd(eq):.0f}%)')
for f in (0.6, 0.8): ax.axvline(t0 + (t1 - t0) * f, color='gray', ls=':', lw=1)
for f, t in ((0.3, 'treino'), (0.7, 'validação'), (0.9, 'teste')):
    ax.text(t0 + (t1 - t0) * f, 0.97, t, transform=ax.get_xaxis_transform(), ha='center')
ax.set_yscale('log'); ax.grid(alpha=.3); ax.set_ylabel('capital (início = 1, escala log)')
ax.set_title('Carteira 6 ativos (com XAG), 4h SMA150 comprado/vendido, metade com vol > 15% a.a.')
ax.legend(loc='upper left', fontsize=9); fig.tight_layout(); fig.savefig('../results/ma_vol_cart6_curva.png', dpi=130)
print(eq.iloc[-1], dd(eq), eb.iloc[-1], dd(eb))
