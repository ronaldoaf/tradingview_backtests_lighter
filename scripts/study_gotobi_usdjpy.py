"""Gotobi USDJPY: short no fix de Toquio 09:55 JST, stop 12 pips, saida 10:30 JST. Dados HistData M1 (bid, EST fixo UTC-5)."""
import zipfile,glob,io,datetime as dt,numpy as np,pandas as pd,sys
D='data/histdata_usdjpy'
fr=[]
for z in sorted(glob.glob(D+'/u_*.zip')):
    zf=zipfile.ZipFile(z);n=[x for x in zf.namelist() if x.endswith('.csv')][0]
    fr.append(pd.read_csv(zf.open(n),sep=';',header=None,names=['t','o','h','l','c','v']))
df=pd.concat(fr);df['t']=pd.to_datetime(df.t,format='%Y%m%d %H%M%S')+pd.Timedelta(hours=14)  # EST->JST
df=df.drop_duplicates('t').set_index('t').sort_index()
try:
    import holidays;jp=holidays.Japan(years=range(2015,2027))
except Exception: jp={}
def bday(d): return d.weekday()<5 and d not in jp and not (d.month==1 and d.day<=3) and not (d.month==12 and d.day==31)
got=set()
d=dt.date(2016,1,1)
while d<=dt.date(2026,10,31):
    if d.day%5==0 or (d+dt.timedelta(1)).month!=d.month:  # 5,10,..,30 + ultimo dia do mes (variante comum)
        e=d
        while not bday(e): e-=dt.timedelta(1)
        got.add((e,d.day%5==0))
    d+=dt.timedelta(1)
g5={e for e,f in got if f}; gme={e for e,f in got}
STOP=float(sys.argv[1]) if len(sys.argv)>1 else 0.12
rows=[]
for day,grp in df[(df.index.hour==9)|(df.index.hour==10)].groupby(df[(df.index.hour==9)|(df.index.hour==10)].index.date):
    if not bday(day): continue
    w=grp.between_time('09:55','10:29')
    if len(w)<25 or w.index[0].strftime('%H:%M')!='09:55': continue
    en=w.o.iloc[0]; ex=grp.between_time('10:30','10:30')
    ex=ex.o.iloc[0] if len(ex) else w.c.iloc[-1]
    hit=(w.h>=en+STOP)
    pnl=-STOP if hit.any() else en-ex
    pre=grp.between_time('09:00','09:54')
    rows.append(dict(d=day,pips=pnl*100,stop=hit.any(),g5=day in g5,gme=day in gme))
r=pd.DataFrame(rows);r['y']=[x.year for x in r.d]
r['per']=np.where(r.y<=2020,'treino16-20',np.where(r.y<=2023,'valid21-23','oos24-26'))
r.to_csv('results/gotobi/trades_all_days.csv',index=False)
def st(x,c):
    p=x.pips-c; return f"n={len(x):4d} win={100*(p>0).mean():4.1f}% media={p.mean():+.2f}p t={p.mean()/p.std()*np.sqrt(len(p)):+.2f} soma={p.sum():+.0f}p"
for c in (0,0.7,1.2):
    print(f"\n== custo ida+volta {c} pip | stop {STOP*100:.0f} pips")
    for nm,m in [('Gotobi 5/10/..',r.g5),('Gotobi+fim mes',r.gme),('Controle (nao gotobi)',~r.gme)]:
        print(f"  {nm:22s} TOTAL {st(r[m],c)}")
        for p in ['treino16-20','valid21-23','oos24-26']: print(f"    {p:12s} {st(r[m&(r.per==p)],c)}")
print("\nPor ano (Gotobi 5/10, sem custo):");print(r[r.g5].groupby('y').pips.agg(['count','mean','sum']).round(2).T.to_string())
print("Por ano (controle):");print(r[~r.gme].groupby('y').pips.agg(['count','mean']).round(2).T.to_string())
