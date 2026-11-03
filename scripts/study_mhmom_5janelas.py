import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
import numpy as np, pandas as pd, study_mhmom as M
from tvlib import load_m1v, resample
h=6; rows=[]
VAR={'4 (5/10/21/42)':(5,10,21,42),'5 +63':(5,10,21,42,63),'5 +84':(5,10,21,42,84),'5 +126':(5,10,21,42,126),'5 +2':(2,5,10,21,42)}
for a in M.ATIVOS:
    d=resample(load_m1v(a),'4h')
    if a=='wti': d=d[~((d.index>='2020-04-01')&(d.index<'2020-05-01'))]
    bh=pd.Series(np.r_[d.open.values[1:]/d.open.values[:-1]-1,0.0],index=d.index)
    t0,t1=d.index[0],d.index[-1]; e=[t0+(t1-t0)*k/10 for k in range(11)]
    per={'treino':(e[0],e[6]),'validacao':(e[6],e[9]),'oos':(e[9],e[10]),'total':(e[0],e[10])}
    for vn,w in VAR.items():
      for sm in (0,200):
        x=M.run(d,a,wins=tuple(k*h for k in w),nvol=20*h,risco=0.01/np.sqrt(h)*4/len(w),sma=sm)
        for p,(lo,hi) in per.items():
            m=(x.index>=lo)&(x.index<=hi); rows.append(dict(ativo=a,janelas=vn,sma=sm,per=p,**M.stats(x[m],bh[m])))
R=pd.DataFrame(rows); R.to_csv('results/mhmom_4h_5janelas.csv',index=False)
P=R.pivot_table(index=['ativo','sma','janelas'],columns='per',values='sharpe')[['treino','validacao','oos','total']]
T=R[R.per=='total'].set_index(['ativo','sma','janelas'])[['cagr','dd']]
print(P.join(T).round(2).to_string())
