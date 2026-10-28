"""Baixa XAG-USD (prata, BID, 1m) do endpoint jetta da Dukascopy, mesmo formato do data/gold/xau_1m.parquet
(2017-09-01 a 2026-10-04, todos os dias com dado, inclusive domingo). Cache por dia em data/silver/days/, junta em
data/silver/xag_1m.parquet.  uso: python data/xag_1m_dl.py"""
import os, json, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd

G = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'silver'); C = os.path.join(G, 'days'); os.makedirs(C, exist_ok=True)


def fetch(d):
    f = os.path.join(C, f'{d:%Y-%m-%d}.json')
    if os.path.exists(f): return
    url = f'https://jetta.dukascopy.com/v1/candles/minute/XAG-USD/BID/{d.year}/{d.month}/{d.day}'
    for k in range(8):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.dukascopy.com/'})
            b = urllib.request.urlopen(req, timeout=60).read()
            if b: open(f, 'wb').write(b); return
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(5 * 2 ** k)
    print('falhou', d.date(), flush=True)


def decode(j):
    if not j.get('times'): return pd.DataFrame()
    m = j['multiplier']; t = j['timestamp'] + np.cumsum(j['times']) * j['shift']
    df = pd.DataFrame({k: j[k] + np.cumsum(j[k + 's']) * m for k in ('open', 'high', 'low', 'close')}, pd.to_datetime(t, unit='ms', utc=True))
    df['volume'] = j['volumes']
    return df


if __name__ == '__main__':
    days = [d for d in pd.date_range('2017-09-01', '2026-10-04', tz='UTC') if d.dayofweek != 5]
    with ThreadPoolExecutor(4) as ex:
        for i, _ in enumerate(ex.map(fetch, days)):
            if i % 250 == 0: print(i, len(days), flush=True)
    df = pd.concat([p for p in (decode(json.load(open(os.path.join(C, f)))) for f in sorted(os.listdir(C))) if len(p)]).sort_index()
    df = df[~df.index.duplicated()]; df.index = df.index.as_unit('ms')
    df.to_parquet(os.path.join(G, 'xag_1m.parquet'))
    print(len(df), 'barras', df.index[0], df.index[-1])
