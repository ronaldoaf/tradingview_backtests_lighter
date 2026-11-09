"""Baixa 1m BID (jetta) de 2020-01-01 ate ontem em threads e salva um unico all.parquet.
uso: python duka_1m_all.py USA500.IDX-USD us500 [destino]"""
import os, sys
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from duka_inst import fetch_day, decode

inst, name = sys.argv[1:3]
dest = sys.argv[3] if len(sys.argv) > 3 else r'C:\Users\Lenovo\Desktop\edge_crypto\dukas_novos'
days = pd.date_range('2020-01-01', pd.Timestamp.now().normalize() - pd.Timedelta(days=1), tz='UTC')

def get(d):
    try:
        x = decode(fetch_day(inst, d))
        return x if len(x) else None
    except Exception as e:
        print('FAIL', d.date(), e, flush=True)

with ThreadPoolExecutor(6) as ex:
    r = [x for x in ex.map(get, days) if x is not None]
x = pd.concat(r).sort_index()
x = x[~x.index.duplicated()].astype(float)
x.index = x.index.as_unit('ms')
out = os.path.join(dest, f'duka1m_{name}'); os.makedirs(out, exist_ok=True)
x.to_parquet(os.path.join(out, 'all.parquet'))
print('FIM', name, len(x), x.index[0], x.index[-1], x.close.iloc[-1], flush=True)
