"""Baixa UVXY do Yahoo (split-ajustado): 1h dos ultimos ~730 dias e diario desde 2011.
Grava data/uvxy/uvxy_1h.parquet e uvxy_1d.parquet (indice UTC, open/high/low/close/volume)."""
import json, os, urllib.request
import pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get(interval, rng):
    u = f'https://query1.finance.yahoo.com/v8/finance/chart/UVXY?interval={interval}&' + (f'range={rng}' if rng != 'max' else 'period1=0&period2=9999999999')
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})))
    r = r['chart']['result'][0]; q = r['indicators']['quote'][0]
    x = pd.DataFrame({k: q[k] for k in ('open', 'high', 'low', 'close', 'volume')},
                     index=pd.to_datetime(r['timestamp'], unit='s', utc=True)).dropna(subset=['open', 'close'])
    return x[~x.index.duplicated()].sort_index().astype(float)

if __name__ == '__main__':
    os.makedirs(os.path.join(D, 'data', 'uvxy'), exist_ok=True)
    for iv, rng, f in (('60m', '730d', 'uvxy_1h'), ('1d', 'max', 'uvxy_1d')):
        x = get(iv, rng); x.to_parquet(os.path.join(D, 'data', 'uvxy', f + '.parquet'), compression='zstd')
        print(f, len(x), x.index[0], x.index[-1], x.close.iloc[0], x.close.iloc[-1])
