"""Pin Bar + tendencia EMA50/200 + S&R por swings (ZiadFrancis/Pinbar_Trend_KeyLvls, CodeTrading).
Sinal no fechamento, entrada na abertura seguinte, SL/TP resolvidos no M1 (stop primeiro), time stop."""
import sys, itertools, numpy as np, pandas as pd
from numba import njit
from tvlib import load_m1v, resample, CUSTO, FUND

def atr_sma(h,l,c,n=14):
    pc=np.r_[np.nan,c[:-1]]; tr=np.nanmax(np.c_[h-l,abs(h-pc),abs(l-pc)],1)
    return pd.Series(tr).rolling(n).mean().to_numpy()

def signals(df, phase, prox, LB=10, look=100):
    o,h,l,c=[df[k].to_numpy(float) for k in ('open','high','low','close')]
    body=np.maximum(abs(c-o),1e-9); rng=h-l; uw=h-np.maximum(o,c); lw=np.minimum(o,c)-l
    bull=(lw>=2*body)&(body<=.33*rng)&(uw<body)&(rng>0)
    bear=(uw>=2*body)&(body<=.33*rng)&(lw<body)&(rng>0)
    if phase>=2:
        ef=pd.Series(c).ewm(span=50,adjust=False).mean().to_numpy(); es=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
        bull&=(c>ef)&(ef>es); bear&=(c<ef)&(ef<es)
    if phase>=3:
        n=len(c)
        # pivos confirmados em i+LB, guardam preco do pivo
        ph=np.full(n,np.nan); pl=np.full(n,np.nan)
        for i in range(LB,n-LB):
            if h[i]>h[i-LB:i].max() and h[i]>h[i+1:i+LB+1].max(): ph[i+LB]=h[i]
            if l[i]<l[i-LB:i].min() and l[i]<l[i+1:i+LB+1].min(): pl[i+LB]=l[i]
        sup=np.zeros(n,bool); res=np.zeros(n,bool)
        for i in range(look,n):
            if not(bull[i] or bear[i]): continue
            wh=ph[i-look:i]; wl=pl[i-look:i]
            if bull[i]:
                v=wl[(~np.isnan(wl))&(wl<c[i])]
                sup[i]=len(v)>0 and abs(c[i]-v[-1])/v[-1]<=prox
            if bear[i]:
                v=wh[(~np.isnan(wh))&(wh>c[i])]
                res[i]=len(v)>0 and abs(c[i]-v[-1])/v[-1]<=prox
        bull&=sup; bear&=res
    return bull,bear

@njit
def run(o,h,l,atr,bull,bear,bstart,mo,mh,ml,am,rr,hold):
    n=len(o); res=[]
    i=0
    while i<n-1:
        d=1 if bull[i] else (-1 if bear[i] else 0)
        if d==0 or atr[i]!=atr[i]: i+=1; continue
        e=o[i+1]
        sl=l[i]-am*atr[i] if d==1 else h[i]+am*atr[i]
        r=(e-sl)*d
        if r<=0: i+=1; continue
        tp=e+d*rr*r
        jend=min(i+1+hold,n-1); a=bstart[i+1]; b=bstart[jend]
        px=o[jend]; jx=jend; hit=-1
        for m in range(a,b):
            if d==1:
                if mo[m]<=sl: px=mo[m]; hit=m; break
                if mo[m]>=tp: px=mo[m]; hit=m; break
                if ml[m]<=sl: px=sl; hit=m; break
                if mh[m]>=tp: px=tp; hit=m; break
            else:
                if mo[m]>=sl: px=mo[m]; hit=m; break
                if mo[m]<=tp: px=mo[m]; hit=m; break
                if mh[m]>=sl: px=sl; hit=m; break
                if ml[m]<=tp: px=tp; hit=m; break
        if hit>=0:
            jx=i+1
            while jx<jend and bstart[jx+1]<=hit: jx+=1
        res.append((i+1,jx,d,e,px))
        i=jx+1
    return res

def bt(df,m1,bs,phase,prox,am,rr,name,hold=50):
    bull,bear=signals(df,phase,prox)
    o,h,l,c=[df[k].to_numpy(float) for k in ('open','high','low','close')]
    atr=atr_sma(h,l,c)
    r=run(o,h,l,atr,bull,bear,bs,m1.open.to_numpy(float),m1.high.to_numpy(float),m1.low.to_numpy(float),am,rr,hold)
    if not r: return pd.DataFrame()
    t=pd.DataFrame(r,columns=['i','j','d','e','x'])
    t['t']=df.index[t.i]; yrs=(df.index[t.j]-df.index[t.i]).total_seconds()/(365*86400)
    t['ret']=t.d*(t.x/t.e-1)-2*CUSTO[name]-t.d*FUND[name]/100*yrs
    return t

def per(t,a,b):
    s=t[(t.t>=a)&(t.t<b)].ret; return len(s),1e4*s.mean() if len(s) else np.nan, s.sum()

if __name__=='__main__':
    name=sys.argv[1]; tfs=sys.argv[2].split(',')
    m1=load_m1v(name); rows=[]
    P=[('2000','2022'),('2022','2024'),('2024','2030')]
    for tf in tfs:
        df=resample(m1,tf); bs=m1.index.searchsorted(df.index).astype(np.int64)
        bs=np.r_[bs,len(m1)][:len(df)]
        for phase,prox,am,rr in itertools.product([1,2,3],[0.002,0.003,0.004,0.006],[1.0,1.5,2.0],[1.0,1.5,2.0]):
            if phase<3 and prox!=0.004: continue
            t=bt(df,m1,bs,phase,prox,am,rr,name)
            if len(t)==0: continue
            row=dict(ativo=name,tf=tf,fase=phase,prox=prox,atr=am,rr=rr,n=len(t),bp=1e4*t.ret.mean(),win=(t.ret>0).mean(),soma=t.ret.sum())
            for k,(a,b) in zip(['tr','va','te'],P):
                n_,bp,_=per(t,a,b); row[f'n_{k}']=n_; row[f'bp_{k}']=bp
            rows.append(row)
    g=pd.DataFrame(rows); g.to_csv(f'../results/study_pinbar_{name}_grid.csv',index=False)
    pd.set_option('display.width',250); print(g.round(3).to_string())
