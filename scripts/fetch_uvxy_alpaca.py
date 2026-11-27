"""UVXY M1 da Alpaca (SIP, split-ajustado, desde 2016, inclui pre/pos-mercado).
Requer ALPACA_KEY/ALPACA_SECRET. Grava data/uvxy/uvxy_1m.parquet."""
import json, os, urllib.request, urllib.parse
import pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'APCA-API-KEY-ID': os.environ['ALPACA_KEY'], 'APCA-API-SECRET-KEY': os.environ['ALPACA_SECRET']}
rows, tok = [], None
while True:
    q = dict(timeframe='1Min', start='2016-01-01', limit=10000, adjustment='split', feed='sip')
    if tok: q['page_token'] = tok
    u = 'https://data.alpaca.markets/v2/stocks/UVXY/bars?' + urllib.parse.urlencode(q)
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))
    rows += r.get('bars') or []; tok = r.get('next_page_token')
    if not tok: break
x = pd.DataFrame(rows)
x = x.set_index(pd.to_datetime(x.t, utc=True))[['o', 'h', 'l', 'c', 'v']].set_axis(
    ['open', 'high', 'low', 'close', 'volume'], axis=1).astype(float)
x = x[~x.index.duplicated()].sort_index()
x.to_parquet(os.path.join(D, 'data', 'uvxy', 'uvxy_1m.parquet'), compression='zstd')
print(len(x), x.index[0], x.index[-1])
