"""Treino / validacao / OOS: o periodo todo em 10 partes iguais; 1-6 treino, 7-9 validacao, 10 OOS (nao e lido).
Usa as series diarias de todas as celulas em results/<ATIVO>_4p_8p_full (abril/2020 ja descartado).
1) Por celula, no treino: retorno de cada uma das 6 partes, media geometrica (geo), Sharpe e trades.
2) Exclusao (so treino): geo > 0, >= 4 das 6 partes positivas, total sem a melhor parte > 0 (nao depende de um
   periodo so), trades >= MINTR. Fica a melhor celula de cada estrategia pela geo; templates fora.
3) Carteiras de K em {6,8,10,12} x teto de correlacao (treino) em {0.2,0.3,0.4,0.5}: gulosa na ordem da geo.
   Avalia na validacao com peso igual e inverso da vol (vol do treino). Grava tvo_*.csv/txt."""
import glob, os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); R = os.path.join(D, 'results', A + '_4p_8p_full'); MINTR = int(os.environ.get('MINTR', '100'))
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; c = [(t0 + (t1 - t0) * k / 10) for k in range(11)]
RK = os.path.join(R, 'ranking.csv'); RK = RK if os.path.exists(RK) else os.path.join(D, 'results', 'wti_4p_8p_full', 'ranking.csv')   # nomes iguais em todos os ativos
nomes = pd.read_csv(RK).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()
rows, TR, VA = [], {}, {}
for f in sorted(glob.glob(os.path.join(R, 'lote*.csv'))):
    l = os.path.basename(f)[4:-4]; g = pd.read_csv(f)
    if 'sid' not in g: continue
    g['est'] = g['est'].fillna(l) if 'est' in g else l
    g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
    S = pd.read_parquet(os.path.join(R, f'lote{l.split("_")[0]}_ser.parquet')); S.index = pd.DatetimeIndex(S.index)
    cc = [x if S.index.tz is not None else x.tz_localize(None) for x in c]
    S = S[S.index < cc[9]].replace([np.inf, -np.inf], np.nan).fillna(0.0)   # parte 10 (OOS) cortada aqui
    tr = S[S.index < cc[6]]; va = S[S.index >= cc[6]]
    lg = np.log1p(tr.clip(lower=-0.999))
    parts = pd.DataFrame({q: lg[(lg.index >= cc[q]) & (lg.index < cc[q + 1])].sum() for q in range(6)})
    sh = tr.mean() / tr.std() * np.sqrt(len(tr) / ((tr.index[-1] - tr.index[0]).days / 365))
    for _, r in g.iterrows():
        k = str(int(r.sid)) if str(int(r.sid)) in S else int(r.sid)
        p = parts.loc[k].values; key = f'{l}|{r.est}|{int(r.sid)}'
        rows.append(dict(lote=l, est=r.est, celula=' '.join(str(r[x]) for x in ('TF', 'cfg') if x in r and pd.notna(r[x])),
                         key=key, geo=np.expm1(p.mean()), n_pos=int((p > 0).sum()), sem_melhor=np.expm1(p.sum() - p.max()),
                         total_tr=np.expm1(p.sum()), sharpe_tr=sh[k], trades=r.trades, **{f't{q + 1}': np.expm1(p[q]) for q in range(6)}))
        TR[key] = tr[k]; VA[key] = va[k]
g = pd.DataFrame(rows)
g['nome'] = [nomes.get((l, e), '') for l, e in zip(g.lote, g.est)]
g = g[~g.nome.fillna('').astype(str).str.contains('Example|Template', case=False)]
ok = (g.geo > 0) & (g.n_pos >= 4) & (g.sem_melhor > 0) & (g.trades >= MINTR)
a = g[ok].sort_values('geo', ascending=False).drop_duplicates(['lote', 'est']).reset_index(drop=True)
a.to_csv(os.path.join(R, 'tvo_aprovadas.csv'), index=False)
X = pd.DataFrame({k: TR[k] for k in a.key}).fillna(0.0); V = pd.DataFrame({k: VA[k] for k in a.key}).fillna(0.0)
C = X.corr().to_numpy()


def st(r):
    eq = (1 + r).cumprod(); anos = (r.index[-1] - r.index[0]).days / 365
    return eq.iloc[-1] - 1, r.mean() / r.std() * np.sqrt(len(r) / anos), (eq / eq.cummax() - 1).min()


out = []
for K in (6, 8, 10, 12):
    for lim in (0.2, 0.3, 0.4, 0.5):
        s = []
        for i in range(len(a)):
            if all(C[i, j] < lim for j in s): s.append(i)
            if len(s) == K: break
        if len(s) < K: out.append(dict(K=K, teto=lim, n=len(s))); continue
        ks = list(a.key[s]); wiv = 1 / X[ks].std(); wiv /= wiv.sum()
        for nw, w in (('igual', pd.Series(1 / K, ks)), ('inv_vol', wiv)):
            tt, tsh, tdd = st(X[ks] @ w); vt, vsh, vdd = st(V[ks] @ w)
            out.append(dict(K=K, teto=lim, n=K, peso=nw, corr_media=np.mean(C[np.ix_(s, s)][np.triu_indices(K, 1)]), treino=tt, sharpe_tr=tsh, dd_tr=tdd,
                            valid=vt, sharpe_val=vsh, dd_val=vdd, ests=' '.join(a.est[s])))
o = pd.DataFrame(out); o.to_csv(os.path.join(R, 'tvo_carteiras.csv'), index=False)
bh = m1.close.resample('1D').last().dropna(); bh = bh[(bh.index >= c[6].normalize()) & (bh.index < c[9])]
print(f'partes: {[str(x)[:10] for x in c]}')
print(f'celulas {len(g)}; estrategias aprovadas no treino {len(a)}; B&H na validacao {bh.iloc[-1] / bh.iloc[0] - 1:+.1%}')
print(a[['lote', 'est', 'nome', 'celula', 'geo', 'n_pos', 'sem_melhor', 'trades']].head(15).to_string(index=False))
print(o.drop(columns='ests').to_string(index=False, float_format=lambda v: f'{v:+.2f}'))
