"""Regime de mercado por HMM gaussiano, ajustado em walk-forward (sem look-ahead).

Observacao diaria x_d = (retorno log do dia, log da vol realizada do dia com barras de 15min). Dias com menos de 6h de
M1 (domingo a noite dos ativos da Dukascopy) sao somados ao dia seguinte. Versao semanal (freq='W'): a mesma coisa por
semana (retorno da semana, vol realizada da semana), indexada no ultimo pregao da semana, para regimes mais lentos.
Reajuste no comeco de cada mes M com todas as observacoes < M (janela expansiva, minimo MINOBS), varios chutes iniciais,
estados ordenados pela vol realizada media (0 = calmo, K-1 = turbulento).
Para um dia i qualquer (calendario das series das estrategias) a probabilidade usada e P(s | x dos dias de pregao < i),
ou seja alfa_d @ A do ultimo pregao d < i: filtro progressivo, nunca suavizado (forward-backward) nem Viterbi.
Com os parametros do mes M o filtro e rodado no historico todo; quem consome so pode ler dias < i (o filtro e causal,
entao a linha d so depende de x_1..x_d)."""
import os, sys, warnings
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ.setdefault(v, '1')   # EM pequeno: threads so atrapalham
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

MINOBS = {'D': int(os.environ.get('MINOBS', '500')), 'W': int(os.environ.get('MINOBS_W', '100'))}
CACHE = os.path.join(D, 'results', 'hmm', 'cache'); os.makedirs(CACHE, exist_ok=True)


def features(A, freq='D'):
    """DataFrame por pregao (indice = dia UTC normalizado): close, r (retorno log) e lrv (log da vol realizada).
    freq='W': uma linha por semana, no ultimo pregao dela."""
    if freq == 'W':
        x = features(A); g = x.groupby(x.index.to_period('W-SUN'))
        w = pd.DataFrame({'dia': g.apply(lambda y: y.index[-1]), 'close': g.close.last(), 'r': g.r.sum(),
                          'lrv': g.lrv.apply(lambda v: 0.5 * np.log(np.exp(2 * v).sum()))})
        return w.set_index('dia').rename_axis(None)
    f = os.path.join(CACHE, f'feat_{A}.parquet')
    if os.path.exists(f): return pd.read_parquet(f)
    m1 = T.load_m1v(A); c15 = m1.close.resample('15min').last().dropna()
    n = m1.close.resample('1D').count(); ok = set(n[n >= 360].index.tz_localize(None) if n.index.tz is not None else n[n >= 360].index)
    lr = np.log(c15).diff().fillna(0.0); cs = (lr ** 2).cumsum()
    dia = c15.index.tz_localize(None).normalize() if c15.index.tz is not None else c15.index.normalize()
    ult = pd.Series(np.arange(len(c15)), index=dia).groupby(level=0).last()   # ultima barra de 15min de cada dia
    ult = ult[[d in ok for d in ult.index]]
    x = pd.DataFrame({'close': c15.values[ult.values], 'cs': cs.values[ult.values]}, index=ult.index)
    x['r'] = np.log(x.close).diff(); x['lrv'] = np.log(np.sqrt(x.cs.diff().clip(lower=1e-12)))
    x = x.dropna()[['close', 'r', 'lrv']]; x.to_parquet(f); return x


def _emis(Z, mu, cv):
    """log N(z | mu_k, cov_k) para cada dia e estado (cov cheia)."""
    out = np.empty((len(Z), len(mu)))
    for k in range(len(mu)):
        L = np.linalg.cholesky(cv[k]); y = np.linalg.solve(L, (Z - mu[k]).T)
        out[:, k] = -0.5 * (y ** 2).sum(0) - np.log(np.diag(L)).sum() - 0.5 * Z.shape[1] * np.log(2 * np.pi)
    return out


def filtro(Z, th):
    """alfa_d = P(s_d | x_1..x_d) para todo d. Recursao progressiva normalizada a cada passo."""
    pi, A, mu, cv = th; le = _emis(Z, mu, cv); e = np.exp(le - le.max(1, keepdims=True))
    a = np.empty_like(e); p = pi * e[0]; a[0] = p / p.sum()
    for d in range(1, len(Z)):
        p = (a[d - 1] @ A) * e[d]; s = p.sum(); a[d] = p / s if s > 0 else e[d] / e[d].sum()
    return a


def ajusta(Z, K, prev=None, n_init=4, seed=0):
    """EM do hmmlearn com varios chutes (e o ajuste anterior como chute extra); devolve (pi, A, mu, cov) ordenado pela
    media da coluna 1 (vol realizada)."""
    from hmmlearn.hmm import GaussianHMM
    best, bl = None, -np.inf
    for s in range(n_init + (prev is not None)):
        m = GaussianHMM(K, covariance_type='full', n_iter=200, tol=1e-4, random_state=seed + s, min_covar=1e-6,
                        init_params='' if s == n_init else 'stmc', params='stmc')
        if s == n_init: m.startprob_, m.transmat_, m.means_, m.covars_ = prev
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try: m.fit(Z); ll = m.score(Z)
            except Exception: continue
        if np.isfinite(ll) and ll > bl and np.all(np.isfinite(m.transmat_)): best, bl = m, ll
    o = np.argsort(best.means_[:, 1])
    return best.startprob_[o], best.transmat_[np.ix_(o, o)], best.means_[o], best.covars_[o], bl


def walk(A, K, freq='D'):
    """Ajuste walk-forward mensal. Devolve (X, meses, Q) onde Q[M] e um array (observacoes x K) com a previsao
    P(s_{d+1} | x_1..x_d) feita no fechamento da observacao d, sob os parametros ajustados com as observacoes < M."""
    mo = MINOBS[freq]; f = os.path.join(CACHE, f'walk_{A}_K{K}_{freq}_m{mo}.npz')
    X = features(A, freq)
    if os.path.exists(f):
        z = np.load(f, allow_pickle=True); return X, list(pd.DatetimeIndex(z['meses'])), dict(zip(pd.DatetimeIndex(z['meses']), z['Q'])), z['par']
    Z = X[['r', 'lrv']].to_numpy(); Z = (Z - Z[:mo].mean(0)) / Z[:mo].std(0)   # escala fixa das primeiras MINOBS observacoes
    ms = pd.date_range(X.index[0].to_period('M').to_timestamp(), X.index[-1], freq='MS')[1:]
    meses, Q, par, prev = [], [], [], None
    for M in ms:
        n = int((X.index < M).sum())
        if n < mo: continue
        pi, Am, mu, cv, ll = ajusta(Z[:n], K, prev); prev = (pi, Am, mu, cv)
        Q.append(filtro(Z, (pi, Am, mu, cv)) @ Am); meses.append(M)
        par.append(np.concatenate([np.diag(Am), mu[:, 0], mu[:, 1], [ll]]))
    np.savez(f, meses=np.array(meses, dtype='datetime64[ns]'), Q=np.array(Q), par=np.array(par))
    return X, meses, dict(zip(meses, Q)), np.array(par)


def no_calendario(X, meses, Q, idx):
    """Probabilidade de regime para cada data de idx (calendario das series): parametros do mes da data e filtro do
    ultimo pregao estritamente anterior. Antes do primeiro ajuste: NaN."""
    idx = pd.DatetimeIndex(idx); idx = idx.tz_localize(None) if idx.tz is not None else idx
    pos = np.searchsorted(X.index.values, idx.values, side='left') - 1   # ultimo pregao < data
    K = next(iter(Q.values())).shape[1]; P = np.full((len(idx), K), np.nan)
    mm = np.array(meses, dtype='datetime64[ns]'); j = np.searchsorted(mm, idx.values, side='right') - 1
    for t in range(len(idx)):
        if j[t] >= 0 and pos[t] >= 0: P[t] = Q[meses[j[t]]][pos[t]]
    return pd.DataFrame(P, index=idx)


def historico(X, Qm, idx, ate):
    """Rotulos (previsao) de todas as datas de idx < ate sob os parametros de um mes so (Qm): para estatistica condicional."""
    idx = pd.DatetimeIndex(idx); idx = idx.tz_localize(None) if idx.tz is not None else idx
    sel = idx < ate; pos = np.searchsorted(X.index.values, idx.values[sel], side='left') - 1
    P = np.full((sel.sum(), Qm.shape[1]), np.nan); v = pos >= 0; P[v] = Qm[pos[v]]
    return sel, P


def hmm1d(Y, K=2, n_iter=40, th=None):
    """EM de um HMM gaussiano 1-D para N series ao mesmo tempo (Y: datas x N), cada uma com os seus parametros.
    Usado no regime da propria estrategia. Devolve (pi, A, mu, sd) com shapes (N,K), (N,K,K), (N,K), (N,K); estados
    ordenados pela media (K-1 = melhor)."""
    T_, N = Y.shape
    if th is None:
        s = Y.std(0) + 1e-12; m = Y.mean(0); q = np.linspace(-0.5, 0.5, K)
        pi = np.full((N, K), 1 / K); A = np.full((N, K, K), 0.05 / (K - 1)); A[:, np.arange(K), np.arange(K)] = 0.95
        mu = m[:, None] + q[None, :] * s[:, None]; sd = np.tile(s[:, None], (1, K))
    else: pi, A, mu, sd = (x.copy() for x in th)
    for _ in range(n_iter):
        b = np.exp(-0.5 * ((Y[:, :, None] - mu[None]) / sd[None]) ** 2) / sd[None] + 1e-300
        a = np.empty((T_, N, K)); c = np.empty((T_, N)); p = pi * b[0]; c[0] = p.sum(1); a[0] = p / c[0][:, None]
        for t in range(1, T_):
            p = np.einsum('nk,nkj->nj', a[t - 1], A) * b[t]; c[t] = p.sum(1); a[t] = p / c[t][:, None]
        be = np.ones((T_, N, K)); xi = np.zeros((N, K, K))
        for t in range(T_ - 2, -1, -1):
            v = b[t + 1] * be[t + 1]; be[t] = np.einsum('nkj,nj->nk', A, v) / c[t + 1][:, None]
            xi += a[t][:, :, None] * A * v[:, None, :] / c[t + 1][:, None, None]
        g = a * be; g /= g.sum(2, keepdims=True); w = g.sum(0) + 1e-12
        pi = g[0]; A = xi / xi.sum(2, keepdims=True)
        mu = np.einsum('tnk,tn->nk', g, Y) / w; sd = np.sqrt(np.einsum('tnk,tnk->nk', g, (Y[:, :, None] - mu[None]) ** 2) / w)
        sd = np.maximum(sd, 0.05 * Y.std(0)[:, None] + 1e-12)
    o = np.argsort(mu, axis=1); ix = np.arange(N)[:, None]
    return pi[ix, o], A[ix[:, :, None], o[:, :, None], o[:, None, :]], mu[ix, o], sd[ix, o]


def filtro1d(Y, th):
    """Previsao P(s_{t+1} | y_1..y_t) para cada data e serie (datas x N x K)."""
    pi, A, mu, sd = th; T_, N = Y.shape; K = mu.shape[1]
    b = np.exp(-0.5 * ((Y[:, :, None] - mu[None]) / sd[None]) ** 2) / sd[None] + 1e-300
    q = np.empty((T_, N, K)); p = pi * b[0]; a = p / p.sum(1)[:, None]; q[0] = np.einsum('nk,nkj->nj', a, A)
    for t in range(1, T_):
        p = q[t - 1] * b[t]; a = p / p.sum(1)[:, None]; q[t] = np.einsum('nk,nkj->nj', a, A)
    return q
