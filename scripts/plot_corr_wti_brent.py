"""Correlacao movel entre WTI e Brent (retornos diarios em 60 dias e retornos 4h em ~30 dias)."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from study_ma_vol_ens8 import load
from tvlib import resample
w, b = load('wti'), load('brent')
fig, ax = plt.subplots(figsize=(12, 5.5))
out = {}
for tf, n, lab, c in (('1D', 60, 'retornos diários, janela 60 dias', '#d62728'), ('4h', 180, 'retornos 4h, janela ~30 dias', '#4c78a8')):
    r = pd.concat([np.log(resample(x, tf).close).diff() for x in (w, b)], axis=1, keys=['wti', 'brent']).dropna()
    r = r[r.index >= '2018-09-01']
    cr = r.wti.rolling(n).corr(r.brent); out[tf] = (r.wti.corr(r.brent), cr.median())
    ax.plot(cr.index, cr, color=c, lw=1.3, label=f'{lab} (período todo: {out[tf][0]:.2f})')
ax.axhline(0, color='k', lw=.6); ax.set_ylim(-0.2, 1.02); ax.grid(alpha=.3)
ax.set_ylabel('correlação'); ax.legend(loc='lower left')
ax.set_title('Correlação móvel WTI x Brent (Dukascopy, 2018–2026)')
fig.tight_layout(); fig.savefig('../results/corr_wti_brent.png', dpi=130); print(out)
