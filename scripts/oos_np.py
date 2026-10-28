"""OOS da carteira das aprovadas (results/<ATIVO>_4p<SUF>/aprovadas.csv), parametros congelados, com peso igual e com
peso pelo inverso da volatilidade diaria medida so antes do OOS (pesos fixos). Grava oos_carteira.txt e .png.
uso: ATIVO=wti SUF=_8p_full python oos_np.py"""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', '_8p_full'))
a = pd.read_csv(os.path.join(R, os.environ.get('IN', 'aprovadas.csv')))   # IN=ranking_total.csv: ranking pelo retorno total
if 'total' in a: a = a[a.total > 0]
a = a[~a.nome.fillna('').str.contains('Example|Template', case=False)].reset_index(drop=True)   # exemplos/templates nao contam
G, S, cols = {}, {}, {}
for _, r in a.iterrows():
    l = str(r.lote)
    if l not in G:
        g = pd.read_csv(os.path.join(R, f'lote{l}.csv')); g['est'] = g['est'].fillna(l) if 'est' in g else l
        g['celula'] = g.apply(lambda x: ' '.join(str(x[k]) for k in ('TF', 'cfg') if k in x and pd.notna(x[k])), axis=1)
        G[l] = g; S[l] = pd.read_parquet(os.path.join(R, f'lote{l.split("_")[0]}_ser.parquet'))
    h = G[l][(G[l].est == r.est) & (G[l].celula == r.celula)].iloc[0]
    cols[f'{l}:{r.est}'] = S[l][str(int(h.sid))] if str(int(h.sid)) in S[l] else S[l][int(h.sid)]
X = pd.DataFrame(cols).fillna(0.0); X.index = pd.DatetimeIndex(X.index); X = X[(X != 0).any(axis=1)]
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; corte = (t0 + (t1 - t0) * 4 / 5).normalize()
if X.index.tz is None: corte = corte.tz_localize(None)
I, O = X[X.index < corte], X[X.index > corte]
K = int(os.environ.get('K', '0'))   # K>0: so as K pouco correlacionadas (gulosa na ordem do ranking, menor limite que fecha K)
if K:
    C = I.corr().to_numpy()
    def pega(lim):
        s = []
        for i in range(len(C)):
            if all(C[i, j] < lim for j in s): s.append(i)
            if len(s) == K: return s
    lim = float(os.environ['LIM']) if os.environ.get('LIM') else next(l for l in np.arange(-0.2, 1.01, 0.01) if pega(l)); s = pega(lim)   # LIM: teto fixo
    print(f'limite {lim:.2f}; corr media do par {np.mean(C[np.ix_(s, s)][np.triu_indices(K, 1)]):.2f}; ranks {[i + 1 for i in s]}')
    X, I, O = X.iloc[:, s], I.iloc[:, s], O.iloc[:, s]
w_iv = (1 / I.std()); w_iv /= w_iv.sum(); w_eq = pd.Series(1 / X.shape[1], X.columns)
yrs = (O.index[-1] - O.index[0]).days / 365
px = m1.close[m1.index >= m1.index[0] + (t1 - t0) * 4 / 5].resample('1D').last().dropna(); bhr = px.pct_change().dropna()


def st(r, n):
    eq = (1 + r).cumprod(); f = len(r) / ((r.index[-1] - r.index[0]).days / 365)
    return eq, f'{n}: total {eq.iloc[-1] - 1:+.1%} CAGR {eq.iloc[-1] ** (365 / (r.index[-1] - r.index[0]).days) - 1:+.1%} Sharpe {r.mean() / r.std() * np.sqrt(f):.2f} DD {(eq / eq.cummax() - 1).min():.1%}'


out = [f'{X.shape[1]} estrategias; OOS {O.index[0].date()} a {O.index[-1].date()} ({yrs:.2f} anos)']
plt.figure(figsize=(10, 5))
for w, n in ((w_eq, 'peso igual'), (w_iv, 'inverso da vol')):
    eqi, si = st(I @ w, 'antes do OOS'); eqo, so = st(O @ w, 'OOS'); out += [f'[{n}] {si} | {so}']; plt.plot(eqo, label=n)
eqb, sb = st(bhr, f'B&H {A.upper()} OOS'); out.append(sb); plt.plot(eqb, label=f'B&H {A.upper()}')
ind = (1 + O).prod() - 1
out.append(f'positivas no OOS: {(ind > 0).sum()}/{len(ind)}\n\nmaiores pesos inverso da vol: ' + ', '.join(f'{k} {v:.1%}' for k, v in w_iv.sort_values(ascending=False).head(5).items()))
out.append('\npor estrategia (OOS):\n' + ind.sort_values(ascending=False).to_string(float_format=lambda v: f'{v:+.1%}'))
open(os.path.join(R, f'oos_carteira{K or ""}{os.environ.get("TAG", "")}.txt'), 'w').write('\n'.join(out))
plt.title(f'{A.upper()} OOS: {X.shape[1]} aprovadas'); plt.legend(); plt.grid(alpha=.3); plt.tight_layout(); plt.savefig(os.path.join(R, f'oos_carteira{K or ""}{os.environ.get("TAG", "")}.png'), dpi=110)
print('\n'.join(out))
