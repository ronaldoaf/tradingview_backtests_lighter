"""Correlacao movel entre WTI e Brent (retornos diarios em 60 dias e retornos 4h em ~30 dias)."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from study_ma_vol_ens8 import load
from tvlib import resample
import sys
A, B = (sys.argv[1:3] if len(sys.argv) > 2 else ['wti', 'brent'])
w, b = load(A), load(B)
fig, ax = plt.subplots(figsize=(12, 5.5))
out = {}
for tf, n, lab, c in (('1D', 60, 'retornos diários, janela 60 dias', '#d62728'), ('4h', 180, 'retornos 4h, janela ~30 dias', '#4c78a8')):
    r = pd.concat([np.log(resample(x, tf).close).diff() for x in (w, b)], axis=1, keys=['a', 'b']).dropna()
    r = r[r.index >= '2018-09-01']
    cr = r.a.rolling(n).corr(r.b); out[tf] = (r.a.corr(r.b), cr.median())
    ax.plot(cr.index, cr, color=c, lw=1.3, label=f'{lab} (período todo: {out[tf][0]:.2f})')
ax.axhline(0, color='k', lw=.6); ax.set_ylim(min(-0.2, ax.get_ylim()[0]), 1.02); ax.grid(alpha=.3)
ax.set_ylabel('correlação'); ax.legend(loc='lower left')
ax.set_title(f'Correlação móvel {A.upper()} x {B.upper()} (Dukascopy, 2018–2026)')
fig.tight_layout(); fig.savefig(f'../results/corr_{A}_{B}.png', dpi=130); print(out)
