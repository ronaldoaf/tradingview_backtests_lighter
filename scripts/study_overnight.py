"""Overnight NY: compra 15:00 NY (1h antes do fechamento), vende 10:30 NY do proximo dia util
(1h apos a abertura). Comparado com B&H e com o complemento intraday (10:30->15:00)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, 'scripts')
from study_engulf_psar import CUSTO, FUND
SRC = {'xau': 'data/gold/xau_1m.parquet', 'us100': 'data/duka1m_us100/all.parquet',
       'wti': 'data/duka1m_wti/all.parquet', 'btc': 'data/binance/klines_1m/BTCUSDT.parquet',
       'eth': 'data/binance/klines_1m/ETHUSDT.parquet'}

def load(a):
    d = pd.read_parquet(SRC[a])
    if 'ts' in d:
        d = d.set_index(pd.to_datetime(d.ts, unit='ms', utc=True)).rename(columns={'o': 'open', 'c': 'close'})
    return d['open'].tz_convert('America/New_York')

def legs(o, t_in, t_out, nextday):
    di = o[o.index.strftime('%H:%M') == t_in]; do = o[o.index.strftime('%H:%M') == t_out]
    di = di[di.index.dayofweek < 5]; do = do[do.index.dayofweek < 5]
    di.index = di.index.normalize(); do.index = do.index.normalize()
    di = di[~di.index.duplicated()]; do = do[~do.index.duplicated()]
    rows = []
    days = sorted(set(di.index) | set(do.index))
    for i, d in enumerate(days):
        if d not in di.index: continue
        if nextday:
            if i + 1 >= len(days) or days[i+1] not in do.index: continue
            e = days[i+1]
        else:
            if d not in do.index: continue
            e = d
        hrs = (e - d).total_seconds()/3600 + (19.5 if nextday else 4.5) - (24 if not nextday else 0)
        rows.append((d, do[e]/di[d] - 1, (e - d).days))
    return pd.DataFrame(rows, columns=['d', 'r', 'ndays']).set_index('d')

def stats(r, years, ann_on=True):
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min()
    cagr = eq.iloc[-1] ** (1/years) - 1
    sh = r.mean() / r.std() * np.sqrt(len(r)/years) if r.std() > 0 else 0
    return cagr*100, sh, dd*100

out = []
for a in SRC:
    o = load(a); years = (o.index[-1] - o.index[0]).days/365.25
    bh = o.resample('D').last().dropna(); bhr = bh.pct_change().dropna()
    c_bh = stats(bhr, years)
    for nome, ti, to, nd in [('overnight 15:00->10:30', '15:00', '10:30', True), ('intraday 10:30->15:00', '10:30', '15:00', False)]:
        t = legs(o, ti, to, nd)
        hold_d = np.where(nd, t.ndays - 1 + 19.5/24, 4.5/24)
        net = t.r - 2*CUSTO[a] - FUND[a]/100 * hold_d/365
        res = {'ativo': a, 'estrategia': nome, 'trades': len(t), 'win%': (net > 0).mean()*100,
               'media_bp': net.mean()*1e4}
        res['CAGR%'], res['Sharpe'], res['MDD%'] = stats(net, years)
        res['BH_CAGR%'], res['BH_Sharpe'], res['BH_MDD%'] = c_bh
        # tercos
        n3 = len(net)//3
        for k, part in enumerate([net.iloc[:n3], net.iloc[n3:2*n3], net.iloc[2*n3:]]):
            res[f'T{k+1}_CAGR%'] = stats(part, years/3)[0]
        res['custo4x_CAGR%'] = stats(t.r - 8*CUSTO[a] - FUND[a]/100*hold_d/365, years)[0]
        out.append(res)
df = pd.DataFrame(out).round(2)
pd.set_option('display.width', 250); print(df.to_string(index=False))
df.to_csv('results/overnight_ny.csv', index=False)
