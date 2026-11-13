"""Binárias 1h em torno de Payroll, CPI (08:30 ET) e FOMC (14:00 ET). BTC/ETH 1m Binance.
Aposta entra k minutos após o evento; referência = close do minuto de entrada; resultado = close 60 min depois.
Payout 85%, empate = perda. Treino < jun/24, validação jun/24-mai/25, OOS >= jun/25."""
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
import sys
HZ=int(sys.argv[1]) if len(sys.argv)>1 else 60
BE=1/(1+{5:.7,10:.75,30:.8,60:.85}[HZ])
SUF='' if HZ==60 else f'_{HZ}m'
CPI="""2020-01-14 2020-02-13 2020-03-11 2020-04-10 2020-05-12 2020-06-10 2020-07-14 2020-08-12 2020-09-11 2020-10-13 2020-11-12 2020-12-10 2021-01-13 2021-02-10 2021-03-10 2021-04-13 2021-05-12 2021-06-10 2021-07-13 2021-08-11 2021-09-14 2021-10-13 2021-11-10 2021-12-10 2022-01-12 2022-02-10 2022-03-10 2022-04-12 2022-05-11 2022-06-10 2022-07-13 2022-08-10 2022-09-13 2022-10-13 2022-11-10 2022-12-13 2023-01-12 2023-02-14 2023-03-14 2023-04-12 2023-05-10 2023-06-13 2023-07-12 2023-08-10 2023-09-13 2023-10-12 2023-11-14 2023-12-12 2024-01-11 2024-02-13 2024-03-12 2024-04-10 2024-05-15 2024-06-12 2024-07-11 2024-08-14 2024-09-11 2024-10-10 2024-11-13 2024-12-11 2025-01-15 2025-02-12 2025-03-12 2025-04-10 2025-05-13 2025-06-11 2025-07-15 2025-08-12 2025-09-11 2025-10-24 2025-12-18 2026-01-13 2026-02-13 2026-03-11 2026-04-10 2026-05-12 2026-06-10 2026-07-14 2026-08-12 2026-09-11"""
NFP="""2020-01-10 2020-02-07 2020-03-06 2020-04-03 2020-05-08 2020-06-05 2020-07-02 2020-08-07 2020-09-04 2020-10-02 2020-11-06 2020-12-04 2021-01-08 2021-02-05 2021-03-05 2021-04-02 2021-05-07 2021-06-04 2021-07-02 2021-08-06 2021-09-03 2021-10-08 2021-11-05 2021-12-03 2022-01-07 2022-02-04 2022-03-04 2022-04-01 2022-05-06 2022-06-03 2022-07-08 2022-08-05 2022-09-02 2022-10-07 2022-11-04 2022-12-02 2023-01-06 2023-02-03 2023-03-10 2023-04-07 2023-05-05 2023-06-02 2023-07-07 2023-08-04 2023-09-01 2023-10-06 2023-11-03 2023-12-08 2024-01-05 2024-02-02 2024-03-08 2024-04-05 2024-05-03 2024-06-07 2024-07-05 2024-08-02 2024-09-06 2024-10-04 2024-11-01 2024-12-06 2025-01-10 2025-02-07 2025-03-07 2025-04-04 2025-05-02 2025-06-06 2025-07-03 2025-08-01 2025-09-05 2025-11-20 2025-12-16 2026-01-09 2026-02-11 2026-03-06 2026-04-03 2026-05-08 2026-06-05 2026-07-02 2026-08-07 2026-09-04"""
FOMC="""2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16 2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15 2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14 2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13 2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18 2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10 2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16"""
ET=ZoneInfo('America/New_York')
def ts(dates,hm):
    return np.array([int(pd.Timestamp(f'{d} {hm}',tz=ET).value//10**6) for d in dates.split()])
EV={'CPI':ts(CPI,'08:30'),'Payroll':ts(NFP,'08:30'),'FOMC':ts(FOMC,'14:00')}
T1=pd.Timestamp('2024-06-01',tz='UTC').value//10**6; T2=pd.Timestamp('2025-06-01',tz='UTC').value//10**6
rows=[]
for A in ['BTC','ETH']:
    d=pd.read_parquet(f'data/binance/klines_1m/{A}USDT.parquet')
    c=pd.Series(d.c.values,index=d.ts.values)
    px=lambda t: c.get(t,np.nan)
    for ev,T in EV.items():
        for t in T:
            p=0 if t<T1 else 1 if t<T2 else 2
            ref=px(t-60000)                       # close do minuto anterior ao evento
            for k in [-60,1,2,5,15,30,60]:          # k=-60: aposta 1h antes do evento
                te=t+k*60000 if k>0 else t-3600000
                e=px(te-60000); x=px(te-60000+HZ*60000)
                mv=(e/ref-1) if k>0 else np.nan
                rows.append([A,ev,t,p,k,mv,np.sign(x-e)])
E=pd.DataFrame(rows,columns=['ativo','evento','t','per','k','mov','y']).dropna(subset=['y'])
E.to_csv(f'results/binarias_eventos_raw{SUF}.csv',index=False)
out=[]
for (A,ev,k),g in E.groupby(['ativo','evento','k']):
    regras={'sempre ALTA':np.ones(len(g)),'sempre BAIXA':-np.ones(len(g))}
    if k>0:
        regras['seguir movimento']=np.sign(g.mov.values); regras['reverter movimento']=-np.sign(g.mov.values)
        thr=g[g.per==0].mov.abs().median()
        big=(g.mov.abs()>thr).values
        regras['seguir mov. grande']=np.where(big,np.sign(g.mov.values),0); regras['reverter mov. grande']=np.where(big,-np.sign(g.mov.values),0)
    for nm,dr in regras.items():
        r=[A,ev,k,nm]
        for p in range(3):
            m=(g.per.values==p)&(dr!=0); w=(dr[m]*g.y.values[m]>0)
            r+=[m.sum(), w.mean() if m.sum() else np.nan]
        out.append(r)
R=pd.DataFrame(out,columns=['ativo','evento','k_min','regra','n_tr','hit_tr','n_val','hit_val','n_oos','hit_oos'])
R.to_csv(f'results/binarias_eventos_grid{SUF}.csv',index=False)
lb=lambda h,n: h-1.645*np.sqrt(h*(1-h)/n)
print('variantes',len(R))
S=R[(lb(R.hit_tr,R.n_tr)>BE)]
print('passam treino (lb95>BE):',len(S))
pd.set_option('display.width',250)
print(S.assign(ev_oos=S.hit_oos*1.85-1).round(3).to_string())
print('\nTop por hit_tr (n>=25):'); print(R[R.n_tr>=25].sort_values('hit_tr',ascending=False).head(15).round(3).to_string())
