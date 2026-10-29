"""Pre-calcula o HMM walk-forward (diario e semanal, K=2 e 3) dos 5 ativos e resume os regimes por dia de pregao.
uso: python hmm_walk_all.py [ativos]"""
import sys, time
import numpy as np
import hmm_regime as H
for A in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
    for freq, K in ((f, k) for f in ('D', 'W') for k in (2, 3)):
        t = time.time(); X, ms, Q, par = H.walk(A, K, freq); Xd = H.features(A)
        P = H.no_calendario(X, ms, Q, Xd.index); v = ~np.isnan(P.values).any(1); s = P.values.argmax(1); r = Xd.r.values; n = 365 if A in ('btc', 'eth') else 252
        print(f'{A} {freq} K={K}: {len(ms)} ajustes ({ms[0]:%Y-%m} a {ms[-1]:%Y-%m}) em {time.time() - t:.0f}s; diag(A) do ultimo {np.round(par[-1][:K], 3)}; '
              f'trocas de estado/ano {np.sum(np.diff(s[v]) != 0) / (v.sum() / n):.1f}; '
              f'corr(P turbulento previsto, vol realizada do dia) {np.corrcoef(P.values[v, -1], Xd.lrv.values[v])[0, 1]:+.2f}')
        for k in range(K):
            m = v & (s == k)
            print(f'   estado {k}: {m.sum() / v.sum():4.0%} dos dias | retorno medio a.a. {r[m].mean() * n:+7.1%} | vol a.a. {r[m].std() * np.sqrt(n):6.1%} | Sharpe {r[m].mean() / r[m].std() * np.sqrt(n):+.2f}')
        sys.stdout.flush()
