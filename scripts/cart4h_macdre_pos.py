"""MACD ReLoaded (lote 3, HULL 12/26/9), parametros de 2020-2023, carteira 5 ativos pesos iguais: jul/2025 a ago/2026.
Le results/cart4h_full (cart4h_lote.py 3 com OUTD=cart4h_full FIM=2026-09-01)."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'cart4h_full')
AT = ['btc', 'wti', 'us100', 'xau', 'xag']; DIAS = pd.date_range('2020-01-02', '2026-08-31', freq='D'); M = {}
for a in AT:
    c = pd.read_csv(os.path.join(R, a, 'lote3.csv')); c = c[(c.est == 'macdre') & (c.cfg == 'HULL 12/26/9')]
    S = pd.read_parquet(os.path.join(R, a, 'lote3_ser.parquet')); S.index = pd.DatetimeIndex(S.index).tz_localize(None).normalize(); sid = str(int(c.sid.iloc[0]))
    M[a] = S[sid if sid in S else int(sid)].reindex(DIAS).fillna(0).clip(lower=-1)
X = pd.DataFrame(M); X['carteira'] = X[AT].mean(1)
def st(r):
    r = np.asarray(r); n = len(r); eq = np.cumprod(1 + r); sd = r.std(ddof=1)
    return dict(cagr=eq[-1] ** (365.25 / n) - 1, total=eq[-1] - 1, vol=sd * np.sqrt(365.25), sharpe=r.mean() / sd * np.sqrt(365.25), dd=(eq / np.maximum.accumulate(eq) - 1).min(), t=r.mean() / sd * np.sqrt(n))
per = {'IS 2020-23': (X.index < '2024-01-01'), 'OOS1 jan24-jun25': (X.index >= '2024-01-01') & (X.index < '2025-07-01'), 'OOS2 jul25-ago26': X.index >= '2025-07-01'}
rows = [dict(serie=k, periodo=p, **st(X.loc[m, k])) for p, m in per.items() for k in X]
o = pd.DataFrame(rows); o.to_csv(os.path.join(D, 'results', 'cart4h', 'macdre_pos_jun25.csv'), index=False)
print(o.round(3).to_string(index=False))
Y = X[X.index >= '2025-07-01']; q = (1 + Y).groupby(Y.index.to_period('Q')).prod() - 1; m = (1 + Y.carteira).groupby(Y.index.to_period('M')).prod() - 1
print(q.round(3).to_string()); print(m.round(3).to_string())
