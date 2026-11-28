"""Resumo da regra recomendada e graficos.
Regra: vendido no perp UVXY com 25% do patrimonio quando VIX/VIX3M < 1 no fechamento (16:15 ET),
zerado quando >= 1; execucao as 16:20 ET; rebalanceio quando a exposicao sai de [0,20; 0,31]
(banda de 25%); 10 bp por perna; funding modelado a partir da AlphaX."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core import load, sim, stats, fund_model, yearly
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
f = fund_model(D.ts.values); fS = fund_model(S.ts.values)
W = 0.25
on = sg.ts(D, 1.0).fillna(0).values; onS = sg.ts(S, 1.0).fillna(0).values
log = []
def p(s):
    print(s); log.append(s)


def line(s):
    return '| %5.1f%% | %6.1f%% | %4.2f | %5.1f%% | %3.0f%% | %4.1fx |' % (
        s['cagr'] * 100, s['mdd'] * 100, s['sharpe'], s['worst'] * 100, s['expo'] * 100, s['turn'])


iIS = int((D.index <= '2018-12-31').sum())
p(f'Regra: vendido {W:.0%} quando VIX/VIX3M<1; exec 16:20 ET; banda 25%; 10 bp/perna; funding modelo\n')
p('| Serie | Regra | CAGR | MDD | Sharpe | Pior dia | Exposto | Giro/ano |')
p('| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |')
R = {}
for nm, sig in (('VIX/VIX3M<1', on), ('short fixo', np.ones(len(D)))):
    for per, sl in (('UVXY 2011-2026', slice(0, len(D))), ('IS 2011-2018', slice(0, iIS)), ('OOS 2019-2026', slice(iIS, len(D)))):
        res, ns, lq = sim(D.iloc[sl], sig[sl] * W, exec='pm', fund=f[sl], band=0.25)
        if per.startswith('UVXY'):
            R[nm] = res
        p(f'| {per} | {nm} ' + line(stats(res, ns, lq)))
RS = {}
for nm, sig in (('VIX/VIX3M<1', onS), ('short fixo', np.ones(len(S)))):
    res, ns, lq = sim(S, sig * W, px='syn', exec='close', fund=fS, band=0.25)
    RS[nm] = res
    p(f'| Sintetico 1,5x 2006-2026 | {nm} ' + line(stats(res, ns, lq)))
    for per, (a, b) in (('Sintetico 2006-07..2011-09 (pre-UVXY)', ('2006-07-18', '2011-10-03')),):
        X = S.loc[a:b]; k = len(X)
        res2, ns2, lq2 = sim(X, sig[:k] * W, px='syn', exec='close', fund=fS[:k], band=0.25)
        p(f'| {per} | {nm} ' + line(stats(res2, ns2, lq2)))

p('\nRetorno por ano (UVXY real; 2006-2011 do sintetico)')
Y = pd.DataFrame({'VIX/VIX3M<1': yearly(R['VIX/VIX3M<1']), 'short fixo': yearly(R['short fixo'])})
YS = pd.DataFrame({'VIX/VIX3M<1': yearly(RS['VIX/VIX3M<1']), 'short fixo': yearly(RS['short fixo'])}).loc[:2011]
YS.loc[2011] = np.nan  # 2011 parcial no real; mostra o sintetico ate 2010
YY = pd.concat([YS.loc[:2010], Y])
u = D0.c.resample('YE').last().pct_change(); u.index = u.index.year
YY['UVXY'] = u.reindex(YY.index)
p('| Ano | VIX/VIX3M<1 | short fixo | UVXY |')
p('| ---: | ---: | ---: | ---: |')
for y, r in YY.iterrows():
    fmt = lambda v: '' if pd.isna(v) else f'{v*100:+.1f}%'
    p(f'| {y}{"*" if y <= 2010 else ""} | {fmt(r.iloc[0])} | {fmt(r.iloc[1])} | {fmt(r.iloc[2])} |')
p('(* sintetico 1,5x reconstruido do ^SHORTVOL; 2006 comeca em 18/07; 2011 real comeca em 04/10)')
open(os.path.join(OUT, 's09_final.txt'), 'w').write('\n'.join(log) + '\n')

# ---------- graficos ----------
BLUE, ORANGE = '#257de0', '#f47230'
TXT, TXT2, GRID = '#191919', '#666666', '#e6e6e6'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': TXT2, 'xtick.color': TXT2,
                     'ytick.color': TXT2, 'axes.titlecolor': TXT, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
                     'figure.facecolor': 'white', 'axes.facecolor': 'white'})


def curves(RR, title, fn):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.4), sharex=True, gridspec_kw={'height_ratios': [2.2, 1]})
    for nm, c in (('VIX/VIX3M<1', BLUE), ('short fixo', ORANGE)):
        e = RR[nm].equity
        a1.plot(e.index, e.values, color=c, lw=1.6, label=nm)
        a1.annotate(f'{nm}  {e.iloc[-1]:.1f}x', (e.index[-1], e.iloc[-1]), xytext=(4, 0), textcoords='offset points',
                    color=TXT, fontsize=9, va='center')
        dd = e / e.cummax() - 1
        a2.plot(dd.index, dd.values * 100, color=c, lw=1.2)
    a1.set_yscale('log'); a1.set_ylabel('patrimonio (x inicial, log)')
    a1.set_title(title, loc='left')
    a1.legend(frameon=False, loc='upper left', labelcolor=TXT)
    a2.set_ylabel('drawdown (%)')
    for a in (a1, a2):
        a.grid(True, color=GRID, lw=0.6); a.spines[['top', 'right']].set_visible(False)
    a1.set_xlim(right=a1.get_xlim()[1] + (a1.get_xlim()[1] - a1.get_xlim()[0]) * 0.08)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, fn), dpi=150); plt.close(fig)


curves(R, f'Vendido no UVXY a {W:.0%} do patrimonio, 2011-2026 (UVXY real, exec 16:20 ET, custos e funding)', 's09_curvas_real.png')
curves(RS, f'Vendido a {W:.0%} no UVXY sintetico 1,5x, 2006-2026 (inclui 2008)', 's09_curvas_sintetico.png')

# fronteira CAGR x MDD
fig, ax = plt.subplots(figsize=(7.5, 5))
for nm, sig, c in (('VIX/VIX3M<1', on, BLUE), ('short fixo', np.ones(len(D)), ORANGE)):
    xs, ys = [], []
    for w in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75):
        s = stats(*sim(D, sig * w, exec='pm', fund=f, band=0.25))
        xs.append(-s['mdd'] * 100); ys.append(s['cagr'] * 100)
        ax.annotate(f'{w:g}', (xs[-1], ys[-1]), xytext=(5, -3), textcoords='offset points', fontsize=8, color=TXT2)
    ax.plot(xs, ys, color=c, lw=1.6, marker='o', ms=6, mec='white', mew=1.5, label=nm)
ax.set_xlabel('queda maxima (%)'); ax.set_ylabel('CAGR (%)')
ax.set_title('Retorno x queda maxima por tamanho (rotulo = fracao do patrimonio vendida), 2011-2026', loc='left', fontsize=10)
ax.legend(frameon=False, labelcolor=TXT); ax.grid(True, color=GRID, lw=0.6); ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 's09_fronteira.png'), dpi=150); plt.close(fig)
print('graficos gravados')
