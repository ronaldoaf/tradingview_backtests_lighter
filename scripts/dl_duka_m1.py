"""Baixa M1 (BID) da Dukascopy para um instrumento e grava data/duka1m_<nome>/all.parquet (UTC).
Uso: python dl_duka_m1.py aapl AAPLUSUSD 2017-01-01 [ponto=1e-3]. Barras de volume 0 (preenchimento) sao descartadas."""
import sys, os, lzma, struct, time, datetime as dt, urllib.request, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, sym, ini = sys.argv[1], sys.argv[2], dt.date.fromisoformat(sys.argv[3])
pt = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-3
def get(day):
    url = f'https://datafeed.dukascopy.com/datafeed/{sym}/{day.year}/{day.month-1:02d}/{day.day:02d}/BID_candles_min_1.bi5'
    for k in range(8):
        try:
            b = urllib.request.urlopen(url, timeout=30).read()
            if not b: return None
            a = np.frombuffer(lzma.decompress(b), dtype='>i4,>i4,>i4,>i4,>i4,>f4')
            t = pd.Timestamp(day, tz='UTC') + pd.to_timedelta(a['f0'], unit='s')
            return pd.DataFrame({'open': a['f1'] * pt, 'high': a['f4'] * pt, 'low': a['f3'] * pt, 'close': a['f2'] * pt,
                                 'volume': a['f5'].astype(float)}, index=t)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 ** k)
        except Exception:
            time.sleep(2 ** k)
    raise RuntimeError(url)
days = [d.date() for d in pd.date_range(ini, dt.date.today() - dt.timedelta(days=2)) if d.dayofweek < 5]
with ThreadPoolExecutor(4) as ex: parts = [p for p in ex.map(get, days) if p is not None]
x = pd.concat(parts); x = x[x.volume > 0]
os.makedirs(os.path.join(D, 'data', f'duka1m_{name}'), exist_ok=True)
x.to_parquet(os.path.join(D, 'data', f'duka1m_{name}', 'all.parquet'), compression='zstd')
print(name, len(x), x.index[0], x.index[-1])
