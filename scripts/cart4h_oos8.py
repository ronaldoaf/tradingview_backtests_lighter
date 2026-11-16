"""As 8 estrategias escolhidas em 2020-2023 (top 10 CAGR sem std e vxe), parametros congelados, rodadas ate jun/2025.
OOS = jan/2024 a jun/2025. Le results/cart4h_jun25 (cart4h_lote.py com OUTD=cart4h_jun25 FIM=2025-07-01)."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'cart4h_jun25')
AT = ['btc', 'wti', 'us100', 'xau', 'xag']; DIAS = pd.date_range('2020-01-02', '2025-06-30', freq='D')
b = pd.read_csv(os.path.join(D, 'results', 'cart4h', 'top10_cagr.csv'), dtype={'lote': str}); b = b[~b.est.isin(['std', 'vxe'])]
P, PA = {}, {}
for r in b.itertuples():
    cols = []
    for a in AT:
        f = os.path.join(R, a, f'lote{r.lote}.csv'); c = pd.read_csv(f); c = c[(c.est.astype(str) == r.est) & (c.cfg.astype(str) == r.cfg)]
        if not len(c): cols.append(np.zeros(len(DIAS))); continue
        S = pd.read_parquet(f[:-4] + '_ser.parquet'); S.index = pd.DatetimeIndex(S.index).tz_localize(None).normalize(); sid = str(int(c.sid.iloc[0]))
        cols.append(S[sid if sid in S else int(sid)].reindex(DIAS).replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=-1).to_numpy())
    nm = r.nome.split('(')[0].split('. ', 1)[-1].strip(); P[nm] = np.column_stack(cols).mean(1); PA[nm] = np.column_stack(cols)
X = pd.DataFrame(P, index=DIAS); X['CARTEIRA 8'] = X.mean(1)
def st(r):
    r = np.asarray(r); n = len(r); eq = np.cumprod(1 + r); sd = r.std(ddof=1)
    return dict(cagr=eq[-1] ** (365.25 / n) - 1, total=eq[-1] - 1, vol=sd * np.sqrt(365.25), sharpe=r.mean() / sd * np.sqrt(365.25), dd=(eq / np.maximum.accumulate(eq) - 1).min(), t=r.mean() / sd * np.sqrt(n))
per = {'IS 2020-23': DIAS < '2024-01-01', 'OOS 2024-jun25': DIAS >= '2024-01-01', '2024': DIAS.year == 2024, '1S2025': DIAS.year == 2025, 'Tudo 2020-jun25': DIAS >= '2020'}
rows = []
for k in X:
    for p, m in per.items(): rows.append(dict(estrategia=k, periodo=p, **st(X[k].to_numpy()[m])))
o = pd.DataFrame(rows); o.to_csv(os.path.join(D, 'results', 'cart4h', 'oos8_stats.csv'), index=False)
pd.set_option('display.width', 200)
print(o.pivot(index='estrategia', columns='periodo', values='sharpe').round(2).to_string())
print(o.pivot(index='estrategia', columns='periodo', values='cagr').round(3).to_string())
print(o[o.estrategia == 'CARTEIRA 8'].round(3).to_string(index=False))
oos = DIAS >= '2024-01-01'; C = X.drop(columns='CARTEIRA 8')[oos].corr().to_numpy(); print('corr media OOS', C[np.triu_indices(8, 1)].mean().round(3))
for j, a in enumerate(AT): print(a, round(st(np.mean([PA[k][oos, j] for k in PA], 0))['cagr'], 3))
X.to_csv(os.path.join(D, 'results', 'cart4h', 'oos8_diario.csv'))
