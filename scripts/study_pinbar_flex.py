"""Variante flexivel do Pin Bar + tendencia + S&R: mais trades."""
import sys, itertools, numpy as np, pandas as pd
from tvlib import load_m1v, resample, CUSTO, FUND
from study_pinbar_sr import atr_sma, run

def sig(df, wick, bodyr, trend, LB, look, zone, atr):
    o,h,l,c=[df[k].to_numpy(float) for k in ('open','high','low','close')]
    body=np.maximum(abs(c-o),1e-9); rng=h-l; uw=h-np.maximum(o,c); lw=np.minimum(o,c)-l
    bull=(lw>=wick*body)&(body<=bodyr*rng)&(uw<lw/2)&(rng>0)
    bear=(uw>=wick*body)&(body<=bodyr*rng)&(lw<uw/2)&(rng>0)
    es=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
    if trend=='ema200': bull&=c>es; bear&=c<es
    elif trend=='50_200':
        ef=pd.Series(c).ewm(span=50,adjust=False).mean().to_numpy(); bull&=(c>ef)&(ef>es); bear&=(c<ef)&(ef<es)
    if zone>0:
        n=len(c); ph=np.full(n,np.nan); pl=np.full(n,np.nan)
        for i in range(LB,n-LB):
            if h[i]>=h[i-LB:i+LB+1].max(): ph[i+LB]=h[i]
            if l[i]<=l[i-LB:i+LB+1].min(): pl[i+LB]=l[i]
        ok_b=np.zeros(n,bool); ok_s=np.zeros(n,bool)
        for i in np.where(bull|bear)[0]:
            if i<look or atr[i]!=atr[i]: continue
            tol=zone*atr[i]
            if bull[i]:
                v=pl[i-look:i]; v=v[~np.isnan(v)]; ok_b[i]=np.any(abs(l[i]-v)<=tol)  # qualquer suporte tocado pela sombra
            if bear[i]:
                v=ph[i-look:i]; v=v[~np.isnan(v)]; ok_s[i]=np.any(abs(h[i]-v)<=tol)
        bull&=ok_b; bear&=ok_s
    return bull,bear

name=sys.argv[1]; m1=load_m1v(name); rows=[]
P=[('2000','2022'),('2022','2024'),('2024','2030')]
mo,mh,ml=[m1[k].to_numpy(float) for k in ('open','high','low')]
for tf in ['15min','30min','1h']:
    df=resample(m1,tf); bs=np.r_[m1.index.searchsorted(df.index),len(m1)][:len(df)].astype(np.int64)
    o,h,l,c=[df[k].to_numpy(float) for k in ('open','high','low','close')]; atr=atr_sma(h,l,c)
    for wick,bodyr,trend,LB,look,zone,am,rr in itertools.product([1.5,2.0],[0.33,0.45],['ema200','50_200'],[5,10],[300],[0.5,1.0],[0.5,1.0,2.0],[1.5,2.0]):
        bu,be=sig(df,wick,bodyr,trend,LB,look,zone,atr)
        r=run(o,h,l,atr,bu,be,bs,mo,mh,ml,am,rr,50)
        if len(r)<30: continue
        t=pd.DataFrame(r,columns=['i','j','d','e','x']); t['t']=df.index[t.i]
        yrs=(df.index[t.j]-df.index[t.i]).total_seconds()/(365*86400)
        t['ret']=t.d*(t.x/t.e-1)-2*CUSTO[name]-t.d*FUND[name]/100*yrs
        row=dict(tf=tf,wick=wick,body=bodyr,trend=trend,LB=LB,zone=zone,atr=am,rr=rr,n=len(t),bp=1e4*t.ret.mean(),pf=t.ret[t.ret>0].sum()/-t.ret[t.ret<0].sum())
        for k,(a,b) in zip(['tr','va','te'],P):
            s=t[(t.t>=a)&(t.t<b)].ret; row['n_'+k]=len(s); row['bp_'+k]=1e4*s.mean()
        rows.append(row)
g=pd.DataFrame(rows); g.to_csv(f'../results/study_pinbar_flex_{name}_grid.csv',index=False)
g['minp']=g[['bp_tr','bp_va','bp_te']].min(1)
pd.set_option('display.width',250)
print(len(g),'celulas; positivas nos 3 periodos:',(g.minp>0).sum())
print(g.sort_values('minp',ascending=False).head(25).round(2).to_string())
print(g.groupby('tf')[['n','bp','bp_tr','bp_va','bp_te']].median().round(2))
