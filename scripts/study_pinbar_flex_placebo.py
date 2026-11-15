import sys; sys.path.insert(0,'.')
import numpy as np,pandas as pd
from tvlib import load_m1v,resample,CUSTO,FUND
from study_pinbar_sr import atr_sma,run
import importlib.util
src=open('study_pinbar_flex.py').read().split("name=sys.argv")[0]; exec(src)
m1=load_m1v('xau'); df=resample(m1,'1h'); bs=np.r_[m1.index.searchsorted(df.index),len(m1)][:len(df)].astype(np.int64)
o,h,l,c=[df[k].to_numpy(float) for k in ('open','high','low','close')]; atr=atr_sma(h,l,c)
mo,mh,ml=[m1[k].to_numpy(float) for k in ('open','high','low')]
def ev(bu,be):
    t=pd.DataFrame(run(o,h,l,atr,bu,be,bs,mo,mh,ml,2.0,2.0,50),columns=['i','j','d','e','x'])
    y=(df.index[t.j]-df.index[t.i]).total_seconds()/(365*86400)
    t['ret']=t.d*(t.x/t.e-1)-2*CUSTO['xau']-t.d*FUND['xau']/100*y; return t
bu,be=sig(df,2.0,0.33,'ema200',10,300,0.5,atr); t=ev(bu,be)
print('real',len(t),1e4*t.ret.mean(), t.groupby('d').ret.agg(['count','mean']))
es=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
rng=np.random.default_rng(1); r=[]
pb=bu.mean(); ps=be.mean()
for k in range(200):
    u=rng.random(len(c)); r.append(1e4*ev((u<pb)&(c>es),(u>1-ps)&(c<es)).ret.mean())
r=np.array(r); print('placebo media %.2f sd %.2f  pct real>=%.2f'%(r.mean(),r.std(),(r>=1e4*t.ret.mean()).mean()))
