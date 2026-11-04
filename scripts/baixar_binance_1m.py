"""Baixa klines 1m de um par spot da Binance (data.binance.vision, mensal) -> data/binance/klines_1m/<SYM>.parquet.
Uso: python scripts/baixar_binance_1m.py PAXGUSDT"""
import io, sys, zipfile, urllib.request, pandas as pd
sym = sys.argv[1]; B = f'https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/'
dfs = []
for m in pd.period_range('2017-08', pd.Timestamp.today().to_period('M') - 1, freq='M'):
    try: z = urllib.request.urlopen(f'{B}{sym}-1m-{m}.zip', timeout=60).read()
    except Exception: continue
    with zipfile.ZipFile(io.BytesIO(z)) as f:
        d = pd.read_csv(f.open(f.namelist()[0]), header=None, usecols=range(6), names=['ts','o','h','l','c','v'])
    d = d[pd.to_numeric(d.ts, errors='coerce').notna()].astype({'ts':'int64'})
    if d.ts.iloc[0] > 1e14: d['ts'] //= 1000  # a partir de 2025 os arquivos vêm em microssegundos
    dfs.append(d.astype({c: float for c in 'ohlcv'})); print(m, len(d), flush=True)
d = pd.concat(dfs).drop_duplicates('ts').sort_values('ts').reset_index(drop=True)
d.to_parquet(f'data/binance/klines_1m/{sym}.parquet', index=False); print(sym, len(d), pd.to_datetime(d.ts.iloc[[0,-1]], unit='ms').tolist())
