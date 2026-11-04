"""Retorno médio por dia da semana (dia de negociação fechando às 17h NY), dados até 31/12/2024."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'results'
def load(f, bin=False):
    d = pd.read_parquet(f)
    if bin: d = d.set_index(pd.to_datetime(d.ts, unit='ms', utc=True)).rename(columns={'c': 'close'})
    return d['close']
A = {'XAU': load('data/gold/xau_1m.parquet'), 'US100': load('data/duka1m_us100/all.parquet'),
     'WTI': load('data/duka1m_wti/all.parquet'), 'BTC': load('data/binance/klines_1m/BTCUSDT.parquet', 1),
     'ETH': load('data/binance/klines_1m/ETHUSDT.parquet', 1)}
NOMES = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
tabs = {}
for k, c in A.items():
    c = c.tz_convert('America/New_York')
    c = c[c.index < pd.Timestamp('2025-01-01 17:00', tz='America/New_York')]
    # dia de negociação: barra até 16:59 NY pertence ao dia; após 17h vai para o dia seguinte
    d = c.groupby((c.index + pd.Timedelta(hours=7)).date).last()
    d.index = pd.to_datetime(d.index); d = d[d.index < '2025-01-01']
    r = np.log(d).diff().dropna() * 1e4  # bps; retorno de seg inclui o fim de semana (ativos tradicionais)
    df = pd.DataFrame({'r': r, 'dw': r.index.dayofweek, 'y': r.index.year})
    mid = df.index[len(df)//2]; g = df.groupby('dw').r
    t = pd.DataFrame({'media_bps': g.mean(), 't': g.mean()/(g.std()/np.sqrt(g.count())),
                      'mediana_bps': g.median(), 'pct_pos': g.apply(lambda x: (x > 0).mean()*100), 'n': g.count(),
                      'media_1a_metade': df[df.index < mid].groupby('dw').r.mean(),
                      'media_2a_metade': df[df.index >= mid].groupby('dw').r.mean(),
                      'soma_anual_bps': g.sum()/((df.index[-1]-df.index[0]).days/365.25)})
    t['anos_pos'] = df.groupby(['dw', 'y']).r.sum().gt(0).groupby('dw').mean()*100
    t.index = [NOMES[i] for i in t.index]; t.index.name = 'dia'
    porano = df.groupby(['y', 'dw']).r.mean().unstack(); porano.columns = [NOMES[i] for i in porano.columns]
    tabs[k] = (t, df.index[0].date(), df.index[-1].date(), porano)
    t.round(2).to_csv(f'{OUT}/retorno_dia_{k}.csv'); porano.round(1).to_csv(f'{OUT}/retorno_dia_por_ano_{k}.csv')
fig, ax = plt.subplots(5, 1, figsize=(9, 15))
for a, (k, (t, i, f, _)) in zip(ax, tabs.items()):
    a.bar(t.index, t.media_bps, color=['#2a9d8f' if v > 0 else '#e76f51' for v in t.media_bps])
    for x, v, tt in zip(t.index, t.media_bps, t.t):
        if abs(tt) >= 2: a.text(x, v, '*', ha='center', va='bottom' if v > 0 else 'top', fontsize=14)
    a.axhline(0, color='k', lw=.6); a.set_title(f'{k}  ({i} a {f})'); a.set_ylabel('bps/dia')
ax[-1].set_xlabel('Dia de negociação (fecha 17h America/New_York)  * = |t|>=2')
plt.tight_layout(); plt.savefig(f'{OUT}/retorno_por_dia_semana.png', dpi=110)
for k, (t, i, f, p) in tabs.items():
    print(f'\n## {k} ({i} a {f})'); print(t.round(2).to_markdown()); print(p.round(1).to_markdown())
