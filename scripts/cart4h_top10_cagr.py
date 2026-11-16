"""Melhor celula (maior CAGR da carteira) de cada estrategia; top 10 estrategias por CAGR; correlacao dos retornos diarios."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'cart4h')
AT = ['btc', 'wti', 'us100', 'xau', 'xag']; DIAS = pd.date_range('2020-01-02', '2023-12-31', freq='D')
g = pd.read_csv(os.path.join(R, 'celulas.csv'), dtype={'lote': str})
b = g.sort_values('cagr', ascending=False).drop_duplicates(['lote', 'est']).head(10).reset_index(drop=True)
P = {}
for r in b.itertuples():
    cols = []
    for a in AT:
        f = os.path.join(R, a, f'lote{r.lote}.csv'); c = pd.read_csv(f); c['est'] = c['est'].fillna(r.lote) if 'est' in c else r.lote
        c = c[(c.est.astype(str) == r.est) & (c.cfg.astype(str) == r.cfg)]
        if not len(c): cols.append(np.zeros(len(DIAS))); continue
        S = pd.read_parquet(f[:-4] + '_ser.parquet'); S.index = pd.DatetimeIndex(S.index).tz_localize(None).normalize()
        sid = str(int(c.sid.iloc[0])); cols.append(S[sid if sid in S else int(sid)].reindex(DIAS).replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=-1).to_numpy())
    P[f'{r.est} ({r.lote})'] = np.column_stack(cols).mean(1)
X = pd.DataFrame(P, index=DIAS); C = X.corr(); n = len(C)
media = C.to_numpy()[np.triu_indices(n, 1)].mean()
eq = X.mean(1); e = (1 + eq).cumprod(); yrs = len(eq) / 365.25
cart = dict(cagr=e.iloc[-1] ** (1 / yrs) - 1, sharpe=eq.mean() / eq.std() * np.sqrt(365.25), dd=(e / e.cummax() - 1).min())
b[['lote', 'est', 'nome', 'cfg', 'cagr', 'vol', 'sharpe', 'dd', 'anos_pos', 'ativos_pos', 'trades']].to_csv(os.path.join(R, 'top10_cagr.csv'), index=False)
C.to_csv(os.path.join(R, 'top10_cagr_corr.csv'))
pd.set_option('display.width', 250)
print(b[['lote', 'est', 'nome', 'cfg', 'cagr', 'vol', 'sharpe', 'dd', 'anos_pos', 'ativos_pos']].to_string(float_format=lambda v: f'{v:.2f}'))
print(C.round(2).to_string()); print('corr media', round(media, 3), 'carteira 10 pesos iguais', cart)
