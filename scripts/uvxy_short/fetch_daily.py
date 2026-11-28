"""Dados diarios para o estudo do short estrutural no UVXY.

Yahoo (OHLC diario, split-ajustado; indices sem ajuste) para:
  UVXY SVXY VIXY VIXM VXX SPY QQQ TQQQ SQQQ e os indices ^VIX ^VIX3M ^VIX9D ^VVIX ^SHORTVOL ^GSPC ^IRX (T-bill 13 semanas, para o TQQQ sintetico)
Grava data/uvxy/daily_<sym>.parquet (indice = data, colunas open/high/low/close/volume).
^SHORTVOL (Cboe Short VIX Futures Index, desde 2005) serve para reconstruir o indice
S&P VIX Short-Term Futures e um UVXY sintetico antes de 2011 (inclui 2008).
"""
import json, os, time, urllib.request
import pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(D, 'data', 'uvxy')
SYMS = ['UVXY', 'SVXY', 'VIXY', 'VIXM', 'VXX', 'SPY', 'QQQ', 'TQQQ', 'SQQQ',
        '^VIX', '^VIX3M', '^VIX9D', '^VVIX', '^SHORTVOL', '^GSPC', '^IRX']


def yahoo(sym):
    u = ('https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(sym) +
         '?interval=1d&period1=0&period2=9999999999&events=split')
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60))
    r = r['chart']['result'][0]
    q = r['indicators']['quote'][0]
    idx = pd.to_datetime(r['timestamp'], unit='s', utc=True).tz_convert('America/New_York').normalize().tz_localize(None)
    x = pd.DataFrame({k: q[k] for k in ('open', 'high', 'low', 'close', 'volume')}, index=idx)
    x = x.dropna(subset=['close'])
    x = x[~x.index.duplicated(keep='last')].sort_index().astype(float)
    x.index.name = 'date'
    return x


if __name__ == '__main__':
    import urllib.parse
    os.makedirs(OUT, exist_ok=True)
    for s in SYMS:
        x = yahoo(s)
        f = os.path.join(OUT, 'daily_' + s.replace('^', '').lower() + '.parquet')
        x.to_parquet(f, compression='zstd')
        print(f'{s:10s} {len(x):5d} {x.index[0].date()} {x.index[-1].date()} close={x.close.iloc[-1]:.2f}')
        time.sleep(0.3)
