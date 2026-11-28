"""Tamanho da posicao pela volatilidade do proprio UVXY.

Estimadores (decididos no fechamento t, so com dados ate t):
  cc{n}   desvio dos log-retornos fechamento-fechamento em n pregoes (n = 5, 10, 20, 40, 60, 120)
  ew{h}   EWMA dos retornos ao quadrado com meia-vida h pregoes (h = 5, 10, 20)
  pk{n}   Parkinson (maxima/minima do dia) em n pregoes (so UVXY real; o sintetico nao tem H/L)
Regras de tamanho (k = escala; escolhida para igualar a vol anual da regra base):
  inv a     w = k * (ref / vol)^a, ref = mediana expansiva do estimador, a = 0,5 / 1 / 2  (menor com vol alta)
  pro a     w = k * (vol / ref)^a, a = 0,5 / 1                                          (maior com vol alta)
  razao     w = k * (vol_longa / vol_curta)^a  (10/60 e 20/120 pregoes, a = 1 / 2)      (corta quando a vol curta dispara)
  degrau p  w = k quando vol < percentil p expansivo, senao k*m (p = 70 / 80 / 90, m = 0 / 0,5)
Todas com e sem o filtro VIX/VIX3M<1, w limitado a 1,0. Comparacao com a mesma vol anual da regra base
(VIX/VIX3M<1 com w fixo = 0,25) no periodo 2011-2026; IS 2011-2018, OOS 2019-2026 e sintetico 2006-2026
(este com a sua propria escala, igualando a vol da base no sintetico)."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
f = fund_model(D.ts.values); fS = fund_model(S.ts.values)
iIS = int((D.index <= '2018-12-31').sum())
WCAP = 1.0
W0 = 0.25


def vols(X, px):
    r = np.log(X[px]).diff()
    V = {}
    for n in (5, 10, 20, 40, 60, 120):
        V[f'cc{n}'] = r.rolling(n, min_periods=n).std() * np.sqrt(252)
    for h in (5, 10, 20):
        V[f'ew{h}'] = np.sqrt((r ** 2).ewm(halflife=h, min_periods=h).mean() * 252)
    if px == 'c':
        pk = np.log(X.h / X.l) ** 2 / (4 * np.log(2))
        for n in (5, 10, 20):
            V[f'pk{n}'] = np.sqrt(pk.rolling(n, min_periods=n).mean() * 252)
    return V


def rules(X, px):
    """Retorna {nome: serie de tamanho relativo (antes da escala k)}."""
    V = vols(X, px); R = {'fixo': pd.Series(1.0, index=X.index)}
    for vn, v in V.items():
        ref = v.expanding(min_periods=60).median()
        for a in (0.5, 1, 2):
            R[f'inv{a:g} {vn}'] = (ref / v) ** a
        for a in (0.5, 1):
            R[f'pro{a:g} {vn}'] = (v / ref) ** a
        for p in (70, 80, 90):
            q = v.expanding(min_periods=120).quantile(p / 100)
            for m in (0.0, 0.5):
                R[f'degrau{p}x{m:g} {vn}'] = pd.Series(np.where(v < q, 1.0, m), index=X.index).where(q.notna())
    r = np.log(X[px]).diff()
    for a_, b_ in ((10, 60), (20, 120), (5, 40)):
        s1 = r.rolling(a_, min_periods=a_).std(); s2 = r.rolling(b_, min_periods=b_).std()
        for a in (1, 2):
            R[f'razao{a} {a_}/{b_}'] = (s2 / s1) ** a
    return R


def run(X, w, px, ff, ex):
    return stats(*sim(X, w, px=px, exec=ex, fund=ff, band=0.25))


def scale_to(X, base, px, ff, ex, target):
    lo, hi = 0.001, 5.0
    for _ in range(22):
        k = (lo + hi) / 2
        v = run(X, np.minimum(base * k, WCAP), px, ff, ex)['vol']
        lo, hi = (k, hi) if v < target else (lo, k)
    return lo


refR = run(D, sg.ts(D, 1.0).fillna(0).values * W0, 'c', f, 'pm')
refS = run(S, sg.ts(S, 1.0).fillna(0).values * W0, 'syn', fS, 'close')
RR = rules(D, 'c'); RS = rules(S, 'syn')
fil = {'ts<1': (sg.ts(D, 1.0).fillna(0).values, sg.ts(S, 1.0).fillna(0).values),
       'sem filtro': (np.ones(len(D)), np.ones(len(S)))}
rows = []
for (fn, (onR, onS)), (rn, z) in itertools.product(fil.items(), RR.items()):
    base = onR * z.fillna(0).clip(lower=0).values
    k = scale_to(D, base, 'c', f, 'pm', refR['vol'])
    w = np.minimum(base * k, WCAP)
    a = run(D, w, 'c', f, 'pm')
    i = run(D.iloc[:iIS], w[:iIS], 'c', f[:iIS], 'pm')
    o = run(D.iloc[iIS:], w[iIS:], 'c', f[iIS:], 'pm')
    row = dict(filtro=fn, regra=rn, k=k, w_med=w[w > 0].mean() if (w > 0).any() else 0, w_max=w.max(),
               cap=(w >= WCAP - 1e-9).mean(), sh=a['sharpe'], cagr=a['cagr'], mdd=a['mdd'], pior=a['worst'],
               giro=a['turn'], IS_sh=i['sharpe'], IS_mdd=i['mdd'], OOS_sh=o['sharpe'], OOS_cagr=o['cagr'], OOS_mdd=o['mdd'])
    if rn in RS:
        bS = onS * RS[rn].fillna(0).clip(lower=0).values
        kS = scale_to(S, bS, 'syn', fS, 'close', refS['vol'])
        s = run(S, np.minimum(bS * kS, WCAP), 'syn', fS, 'close')
        row.update(SIN_sh=s['sharpe'], SIN_cagr=s['cagr'], SIN_mdd=s['mdd'])
    rows.append(row)
R = pd.DataFrame(rows)
b = R[(R.filtro == 'ts<1') & (R.regra == 'fixo')].iloc[0]
R['bate_base_3'] = (R.IS_sh > b.IS_sh) & (R.OOS_sh > b.OOS_sh) & (R.SIN_sh.fillna(-9) > b.SIN_sh)
R['bate_base_3_e_mdd'] = R.bate_base_3 & (R.mdd >= b.mdd) & (R.OOS_mdd >= b.OOS_mdd) & (R.SIN_mdd.fillna(-9) >= b.SIN_mdd)
R.to_csv(os.path.join(OUT, 's11_tamanho_vol.csv'), index=False)

log = []
def p(s=''):
    print(s); log.append(s)


pct = lambda x: f'{x*100:6.1f}%'
p(f'Base: VIX/VIX3M<1, w fixo {W0} -> vol anual {refR["vol"]*100:.1f}% (real) / {refS["vol"]*100:.1f}% (sintetico); '
  f'todas as variantes escaladas para essa vol, w <= {WCAP}')
p(f'Base: Sharpe {b.sh:.2f}  CAGR {pct(b.cagr)}  MDD {pct(b.mdd)} | IS Sh {b.IS_sh:.2f} | OOS Sh {b.OOS_sh:.2f} MDD {pct(b.OOS_mdd)} | '
  f'SIN Sh {b.SIN_sh:.2f} MDD {pct(b.SIN_mdd)}')
p(f'\nVariantes testadas: {len(R)} ({R.regra.nunique()} regras x 2 filtros)')
for fn in ('ts<1', 'sem filtro'):
    P = R[R.filtro == fn]
    p(f'  {fn}: Sharpe > base em {(P.sh > b.sh).sum()}/{len(P)}; bate a base no IS, OOS e sintetico: {P.bate_base_3.sum()}; '
      f'e sem piorar a queda nos tres: {P.bate_base_3_e_mdd.sum()}')

p('\n# Media por familia de regra (com filtro ts<1)')
P = R[R.filtro == 'ts<1'].copy()
P['familia'] = P.regra.str.split(' ').str[0].str.replace(r'[0-9.x]+$', '', regex=True)
P.loc[P.regra.str.startswith('degrau'), 'familia'] = P.regra.str.extract(r'(degrau\d+x[0-9.]+)')[0]
P.loc[P.regra.str.startswith('inv'), 'familia'] = P.regra.str.extract(r'^(inv[0-9.]+)')[0]
P.loc[P.regra.str.startswith('pro'), 'familia'] = P.regra.str.extract(r'^(pro[0-9.]+)')[0]
P.loc[P.regra.str.startswith('razao'), 'familia'] = P.regra.str.extract(r'^(razao\d)')[0]
g = P.groupby('familia').agg(n=('sh', 'size'), sh=('sh', 'mean'), mdd=('mdd', 'mean'), IS_sh=('IS_sh', 'mean'),
                             OOS_sh=('OOS_sh', 'mean'), OOS_mdd=('OOS_mdd', 'mean'), SIN_sh=('SIN_sh', 'mean'),
                             SIN_mdd=('SIN_mdd', 'mean'), w_max=('w_max', 'mean'), pior=('pior', 'mean'))
for c in ('mdd', 'OOS_mdd', 'SIN_mdd', 'pior'):
    g[c] = (g[c] * 100).round(1)
p(g.round(2).sort_values('sh', ascending=False).to_string())

p('\n# Media por estimador de vol (inverso, a=1, com filtro)')
Q = P[P.regra.str.startswith('inv1 ')].copy(); Q['est'] = Q.regra.str.split(' ').str[1]
p(Q.set_index('est')[['sh', 'mdd', 'IS_sh', 'OOS_sh', 'OOS_mdd', 'SIN_sh', 'SIN_mdd', 'w_max', 'pior']].assign(
    mdd=lambda x: (x.mdd * 100).round(1), OOS_mdd=lambda x: (x.OOS_mdd * 100).round(1),
    SIN_mdd=lambda x: (x.SIN_mdd * 100).round(1), pior=lambda x: (x.pior * 100).round(1)).round(2).to_string())

cols = ['filtro', 'regra', 'w_med', 'w_max', 'sh', 'cagr', 'mdd', 'pior', 'IS_sh', 'OOS_sh', 'OOS_mdd', 'SIN_sh', 'SIN_mdd']
T = R[cols].copy()
for c in ('cagr', 'mdd', 'pior', 'OOS_mdd', 'SIN_mdd'):
    T[c] = (T[c] * 100).round(1)
p('\n# 25 melhores por Sharpe 2011-2026')
p(T.sort_values('sh', ascending=False).head(25).round(2).to_string(index=False))
p('\n# As que batem a base no IS, no OOS e no sintetico')
p(T[R.bate_base_3].sort_values('sh', ascending=False).round(2).to_string(index=False))
open(os.path.join(OUT, 's11_tamanho_vol.txt'), 'w').write('\n'.join(log) + '\n')
