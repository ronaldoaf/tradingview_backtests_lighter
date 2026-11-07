"""Baixa candles 1m USDJPY (BID e ASK) da Dukascopy, 2016-01..2026-10; guarda so 23:00-03:00 UTC (janela Tokyo fix)."""
import lzma,struct,datetime as dt,urllib.request,os,pandas as pd
from concurrent.futures import ThreadPoolExecutor
OUT='/home/user/tradingview_backtests_lighter/data/duka1m_usdjpy/usdjpy_1m_window_'+__import__('sys').argv[1]+'.parquet'
def get(args):
    d,side=args
    u=f"https://datafeed.dukascopy.com/datafeed/USDJPY/{d.year}/{d.month-1:02d}/{d.day:02d}/{side}_candles_min_1.bi5"
    for k in range(4):
        try:
            b=urllib.request.urlopen(u,timeout=30).read();break
        except Exception: b=None; __import__('time').sleep(1+k*2)
    if not b: return []
    raw=lzma.decompress(b);rows=[]
    t0=dt.datetime(d.year,d.month,d.day)
    for i in range(0,len(raw),24):
        s,o,c,l,h,v=struct.unpack('>5if',raw[i:i+24])
        ts=t0+dt.timedelta(seconds=s)
        if ts.hour in (23,0,1,2): rows.append((ts,side,o/1000,h/1000,l/1000,c/1000,v))
    return rows
days=[dt.date(2016,1,1)+dt.timedelta(i) for i in range((dt.date(2026,10,31)-dt.date(2016,1,1)).days+1)]
days=[d for d in days if d.weekday()!=5 and (int(__import__('sys').argv[1]) in (d.year,))]
jobs=[(d,s) for d in days for s in ('BID','ASK')]
with ThreadPoolExecutor(6) as ex: res=list(ex.map(get,jobs))
df=pd.DataFrame([r for x in res for r in x],columns=['ts','side','o','h','l','c','v'])
df=df[df.v>0]
df.to_parquet(OUT);print(len(df),df.ts.min(),df.ts.max())
