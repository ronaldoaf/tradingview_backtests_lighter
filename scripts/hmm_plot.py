"""Grafico dos regimes previstos (walk-forward) nos 5 ativos: preco em escala log e faixas do regime turbulento.
uso: python hmm_plot.py [freq K]   (padrao W 2) -> results/hmm/regimes_<freq>_K<K>.png"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter, LogLocator
import hmm_regime as H

freq, K = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ('W', 2)
AT = ['xau', 'us100', 'wti', 'btc', 'eth']; NOME = dict(xau='XAU (ouro)', us100='US100', wti='WTI', btc='BTC', eth='ETH')
INK, INK2, GRID, TURB = '#0b0b0b', '#52514e', '#e4e3df', '#eb6834'
fig, axs = plt.subplots(len(AT), 1, figsize=(11, 2.3 * len(AT)), facecolor='#fcfcfb')
for ax, A in zip(axs, AT):
    Xd = H.features(A); X, ms, Q, _ = H.walk(A, K, freq); P = H.no_calendario(X, ms, Q, Xd.index)
    v = ~P.isna().any(axis=1).values; s = P.values.argmax(1); t = Xd.index
    ax.set_facecolor('#fcfcfb'); ax.plot(t, Xd.close, color=INK, lw=1.2); ax.set_yscale('log')
    on = v & (s == K - 1); d = np.diff(np.r_[0, on.astype(int), 0]); ini, fim = np.where(d == 1)[0], np.where(d == -1)[0]
    for a, b in zip(ini, fim): ax.axvspan(t[a], t[min(b, len(t) - 1)], color=TURB, alpha=0.22, lw=0)
    fc = os.path.join(H.CACHE, f'apr_{A}.json')
    if os.path.exists(fc):
        c = [pd.Timestamp(x) for x in json.load(open(fc))['c']]
        for x, lab in ((c[6], 'validação'), (c[9], 'OOS')):
            ax.axvline(x, color=INK2, lw=1, ls='--'); ax.text(x, 1.02, ' ' + lab, transform=ax.get_xaxis_transform(), color=INK2, fontsize=8, va='bottom')
    ax.axvline(ms[0], color=GRID, lw=1); ax.text(0.005, 0.92, NOME[A], transform=ax.transAxes, color=INK, fontsize=10, va='top', weight='bold')
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0))); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'.replace(',', '.'))); ax.yaxis.set_minor_formatter(NullFormatter())
    ax.grid(axis='y', color=GRID, lw=0.6); ax.tick_params(colors=INK2, labelsize=8)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color(GRID)
from matplotlib.patches import Patch
axs[0].legend(handles=[Patch(color=TURB, alpha=0.35, label=f'regime de maior volatilidade (previsto, HMM {"semanal" if freq == "W" else "diário"}, {K} estados)')],
              loc='upper center', bbox_to_anchor=(0.5, 1.45), frameon=False, fontsize=9, labelcolor=INK2)
fig.tight_layout(); f = os.path.join(H.D, 'results', 'hmm', f'regimes_{freq}_K{K}.png'); fig.savefig(f, dpi=110); print(f)
