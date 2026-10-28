"""Carteira de K pouco correlacionadas a partir de results/<ATIVO>_4p<SUF>/ranking.csv (so geo > 0): percorre na
ordem do ranking e aceita se a maior correlacao com as ja aceitas fica abaixo do limite, o menor (passo 0,01) que
fecha K. Correlacao dos retornos diarios so antes do OOS, com as series de <...>_full. Grava sel{K}.csv e sel{K}_corr.csv.
uso: ATIVO=wti SUF=_10p K=10 python sel_np.py"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); SUF = os.environ.get('SUF', '_10p'); K = int(os.environ.get('K', '10'))
R = os.path.join(D, 'results', A + '_4p' + SUF); F = R + '_full'
a = pd.read_csv(os.path.join(R, 'ranking.csv')); a = a[a.geo > 0].reset_index(drop=True)
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; oos = (t0 + (t1 - t0) * 4 / 5).normalize()
ser, G = {}, {}; cols = []
for i, r in a.iterrows():
    l = str(r.lote).split('_')[0]
    if l not in G:
        g = pd.read_csv(os.path.join(F, f'lote{l}.csv')); g['celula'] = g.apply(lambda x: ' '.join(str(x[c]) for c in ('TF', 'cfg') if c in x and pd.notna(x[c])), axis=1)
        g['est'] = g['est'].fillna(str(r.lote)) if 'est' in g else str(r.lote)
        G[l] = g; ser[l] = pd.read_parquet(os.path.join(F, f'lote{l}_ser.parquet'))
    h = G[l][(G[l].est == r.est) & (G[l].celula == r.celula)].iloc[0]
    cols.append(ser[l][str(int(h.sid))] if str(int(h.sid)) in ser[l] else ser[l][int(h.sid)])
X = pd.concat([c.rename(i) for i, c in enumerate(cols)], axis=1).fillna(0.0)
X.index = pd.DatetimeIndex(X.index); X = X[X.index < (oos.tz_localize(None) if X.index.tz is None else oos)]
C = X.corr().to_numpy()


def pega(lim):
    s = []
    for i in range(len(a)):
        if all(C[i, j] < lim for j in s): s.append(i)
        if len(s) == K: return s


lim = next(l for l in np.arange(-0.2, 1.01, 0.01) if pega(l)); s = pega(lim)
b = a.iloc[s].assign(rank=[i + 1 for i in s], corr_max=[max(C[i, j] for j in s if j != i) for i in s])
b.to_csv(os.path.join(R, f'sel{K}.csv'), index=False)
pd.DataFrame(C[np.ix_(s, s)], index=b.est, columns=b.est).round(2).to_csv(os.path.join(R, f'sel{K}_corr.csv'))
cart = X[s].mean(axis=1); eq = (1 + cart).cumprod(); yrs = (X.index[-1] - X.index[0]).days / 365
print(f'{len(a)} candidatas; limite {lim:.2f}; corr media do par {np.mean(C[np.ix_(s, s)][np.triu_indices(K, 1)]):.2f}')
print(f'carteira peso igual antes do OOS: total {eq.iloc[-1] - 1:+.0%}, CAGR {eq.iloc[-1] ** (1 / yrs) - 1:+.1%}, Sharpe {cart.mean() / cart.std() * np.sqrt(252):.2f}, DD {(eq / eq.cummax() - 1).min():.0%}')
print(b[['rank', 'lote', 'est', 'nome', 'celula', 'geo', 'n_pos', 'corr_max']].to_string(index=False, float_format=lambda v: f'{v:+.2f}'))
