"""OOS (parte 10 de 10) de UMA carteira escolhida na validacao de tvo_wti.py: K estrategias, teto de correlacao LIM.
Pesos fixos (igual e inverso da vol do treino). uso: ATIVO=wti K=12 LIM=0.5 python tvo_oos.py"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); R = os.path.join(D, 'results', A + '_4p_8p_full'); K = int(os.environ.get('K', '12')); LIM = float(os.environ.get('LIM', '0.5'))
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; c = [(t0 + (t1 - t0) * k / 10) for k in range(11)]
a = pd.read_csv(os.path.join(R, 'tvo_aprovadas.csv')); cols = {}
for key in a.key:
    l, e, sid = key.split('|'); S = pd.read_parquet(os.path.join(R, f"lote{l.split('_')[0]}_ser.parquet"))
    cols[key] = S[sid] if sid in S else S[int(sid)]
X = pd.DataFrame(cols).replace([np.inf, -np.inf], np.nan).fillna(0.0); X.index = pd.DatetimeIndex(X.index)
cc = [x if X.index.tz is not None else x.tz_localize(None) for x in c]
TR, O = X[X.index < cc[6]], X[X.index >= cc[9]]
C = TR.corr().to_numpy(); s = []
for i in range(len(a)):
    if all(C[i, j] < LIM for j in s): s.append(i)
    if len(s) == K: break
ks = list(a.key[s]); wiv = 1 / TR[ks].std(); wiv /= wiv.sum()


def st(r):
    eq = (1 + r).cumprod(); anos = (r.index[-1] - r.index[0]).days / 365
    return f'total {eq.iloc[-1] - 1:+.1%} Sharpe {r.mean() / r.std() * np.sqrt(len(r) / anos):.2f} DD {(eq / eq.cummax() - 1).min():.1%}'


px = m1.close.resample('1D').last().dropna(); px = px[px.index >= c[9].normalize()]
out = [f'OOS {O.index[0].date()} a {O.index[-1].date()}; K={K} teto={LIM}',
       f'peso igual: {st(O[ks].mean(axis=1))}', f'inverso da vol: {st(O[ks] @ wiv)}', f'B&H {A.upper()}: {st(px.pct_change().dropna())}',
       '\npor estrategia (OOS):\n' + ((1 + O[ks]).prod() - 1).rename(lambda k: k.split('|')[1]).sort_values(ascending=False).to_string(float_format=lambda v: f'{v:+.1%}')]
open(os.path.join(R, f'tvo_oos_K{K}_{LIM}.txt'), 'w').write('\n'.join(out)); print('\n'.join(out))
