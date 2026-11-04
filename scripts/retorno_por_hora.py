"""Retorno médio por hora do dia (horário de NY), dados até 31/12/2025."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'results'
def load(f, bin=False):
    d = pd.read_parquet(f)
    if bin: d = d.set_index(pd.to_datetime(d.ts, unit='ms', utc=True)).rename(columns={'c': 'close'})
    return d['close']
A = {'XAU': load('data/gold/xau_1m.parquet'), 'US100': load('data/duka1m_us100/all.parquet'),
     'WTI': load('data/duka1m_wti/all.parquet'), 'BTC': load('data/binance/klines_1m/BTCUSDT.parquet', 1),
     'ETH': load('data/binance/klines_1m/ETHUSDT.parquet', 1)}
rows, tabs = [], {}
for k, c in A.items():
    c = c[c.index < '2026-01-01']
    h = c.tz_convert('America/New_York').resample('1h').last().dropna()
    r = np.log(h).diff().dropna() * 1e4  # bps; retorno de gaps (fim de semana) cai na 1a hora após o gap
    df = pd.DataFrame({'r': r, 'hr': r.index.hour, 'y': r.index.year})
    mid = df.index[len(df)//2]
    g = df.groupby('hr').r
    t = pd.DataFrame({'media_bps': g.mean(), 't': g.mean()/(g.std()/np.sqrt(g.count())),
                      'pct_pos': g.apply(lambda x: (x > 0).mean()*100), 'n': g.count(),
                      'media_1a_metade': df[df.index < mid].groupby('hr').r.mean(),
                      'media_2a_metade': df[df.index >= mid].groupby('hr').r.mean(),
                      'soma_anual_bps': g.sum()/((df.index[-1]-df.index[0]).days/365.25)})
    t['anos_pos'] = df.groupby(['hr', 'y']).r.sum().gt(0).groupby('hr').mean()*100
    tabs[k] = (t, df.index[0].date(), df.index[-1].date())
    t.round(2).to_csv(f'{OUT}/retorno_hora_{k}.csv')
fig, ax = plt.subplots(5, 1, figsize=(11, 16), sharex=True)
for a, (k, (t, i, f)) in zip(ax, tabs.items()):
    a.bar(t.index, t.media_bps, color=['#2a9d8f' if v > 0 else '#e76f51' for v in t.media_bps])
    for hr, v, tt in zip(t.index, t.media_bps, t.t):
        if abs(tt) >= 2: a.text(hr, v, '*', ha='center', va='bottom' if v > 0 else 'top', fontsize=14)
    a.axhline(0, color='k', lw=.6); a.set_title(f'{k}  ({i} a {f})'); a.set_ylabel('bps/hora')
ax[-1].set_xticks(range(24)); ax[-1].set_xlabel('Hora de início da barra (America/New_York)  * = |t|>=2')
plt.tight_layout(); plt.savefig(f'{OUT}/retorno_por_hora.png', dpi=110)
for k, (t, i, f) in tabs.items():
    print(f'\n## {k} ({i} a {f})'); print(t.round(2).to_markdown())
