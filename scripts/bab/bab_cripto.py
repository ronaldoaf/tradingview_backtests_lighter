# Betting Against Beta nos perps cripto da Lighter (dados diários Binance desde 2020, custo/funding Lighter)
import os,sys,json,numpy as np,pandas as pd
os.environ.setdefault('VAR','btceth'); os.environ.setdefault('TOPN','30')
BASE='/mnt/project-files/estrategias/ls_indice_alts'; os.chdir(BASE); sys.path.insert(0,BASE)
import bt
R,U,D,F,CST,TRAD,IDXr=bt.R,bt.U,bt.D,bt.F,bt.CST,bt.TRAD,bt.IDXr
OUT='/mnt/project-files/estrategias/bab/'
ELIG=(U&TRAD).values
lr=np.log1p(R.fillna(0))
def betas(mkt,win_s=365,win_c=730):
    m=np.log1p(mkt.fillna(0))
    sd=lr.rolling(win_s,min_periods=120).std(); sdm=m.rolling(win_s,min_periods=120).std()
    r3=lr.rolling(3).sum(); m3=m.rolling(3).sum()
    rho=r3.rolling(win_c,min_periods=180).corr(m3)
    b=rho.mul(sd).div(sdm,axis=0)
    return (0.6*b+0.4).where(R.notna())
BETA={'btc':betas(R['BTC']),'idx':betas(IDXr)}
VOL=lr.rolling(365,min_periods=120).std()
Rv=R.fillna(0).values; Fv=F.values; cv=CST.values; n=len(D)
def weights(b,mode,rng=None):
    ok=~np.isnan(b)
    if ok.sum()<9: return None
    idx=np.where(ok)[0]; bb=b[idx]
    if rng is not None: bb=rng.permutation(bb)  # placebo: betas embaralhados
    W=np.zeros(len(b))
    if mode in('fp','fp_dn'):
        z=pd.Series(bb).rank().values; d=z-z.mean(); k=2/np.abs(d).sum()
        wh=k*np.clip(d,0,None); wl=k*np.clip(-d,0,None)
        bH=(wh*b[idx]).sum(); bL=(wl*b[idx]).sum()
        if mode=='fp': wl=wl/bL; wh=wh/bH       # FP: cada perna alavancada para beta 1
        W[idx]=wl-wh
    else:  # tercis equal-weight
        o=np.argsort(bb); t=len(o)//3; lo=idx[o[:t]]; hi=idx[o[-t:]]
        if mode=='ew_dn': W[lo]=1/t; W[hi]=-1/t
        else:  # ew_bn: beta neutro
            bL=b[lo].mean(); bH=b[hi].mean(); W[lo]=1/t/bL; W[hi]=-1/t/bH
    g=np.abs(W).sum()
    if g>3: W*=3/g
    return W
def run(sig,mode,Rb=30,rng=None,fcost=None,lag=0):
    S=sig.where(ELIG).values if not isinstance(sig,np.ndarray) else sig
    c=cv if fcost is None else np.full(len(cv),fcost)
    W=np.zeros(S.shape[1]); out=np.zeros(n); start=400
    for i in range(start,n-1-lag):
        if (i-start)%Rb==0:
            Wn=weights(S[i],mode,rng)
            if Wn is not None:
                out[i+1+lag]-=(np.abs(Wn-W)*c).sum(); W=Wn
        j=i+1+lag
        out[j]+=(W*Rv[j]).sum()-(W*Fv[j]).sum(); W=W*(1+Rv[j])
    return pd.Series(out,D)[D[start+1]:]
P=[('treino','2020-01-01','2022-12-31'),('valid','2023-01-01','2024-12-31'),('oos','2025-01-01','2026-12-31')]
def st(p):
    if len(p)<30 or p.std()==0: return np.nan,np.nan,np.nan
    eq=(1+p).cumprod(); return eq.iloc[-1]**(365/len(p))-1,p.mean()/p.std()*np.sqrt(365),(eq/eq.cummax()-1).min()
def row(p,**k):
    d=dict(k)
    for nm,a,b in P:
        c,s,dd=st(p[a:b]); d[nm+'_cagr']=c; d[nm+'_sh']=s; d[nm+'_dd']=dd
    return d
if __name__=='__main__':
    print('início efetivo',D[401],'moedas elegíveis/dia (média):',ELIG[401:].sum(1).mean().round(1))
    rows=[];curvas={}
    for sname,sig in [('beta_btc',BETA['btc']),('beta_idx',BETA['idx']),('vol',VOL)]:
        for mode in ['fp','fp_dn','ew_dn','ew_bn']:
            if sname=='vol' and mode in('fp','ew_bn'): continue
            for Rb in [7,30]:
                p=run(sig,mode,Rb); rows.append(row(p,sinal=sname,modo=mode,R=Rb)); curvas[f'{sname}_{mode}_R{Rb}']=p
    df=pd.DataFrame(rows); df.to_csv(OUT+'grid_cripto.csv',index=False)
    pd.set_option('display.width',250); print(df.round(2).to_string())
    pd.DataFrame(curvas).to_csv(OUT+'curvas_cripto.csv')
    # placebo: betas embaralhados entre moedas, FP mensal (sinal beta_btc)
    rng=np.random.default_rng(0); pl=[]
    for k in range(200):
        p=run(BETA['btc'],'fp',30,rng); pl.append(row(p))
    pl=pd.DataFrame(pl); pl.to_csv(OUT+'placebo_cripto.csv',index=False)
    print('placebo Sharpe (média, p95):'); print(pl[[c for c in pl if c.endswith('_sh')]].describe(percentiles=[.95]).round(2))
    # BTC e ETH: beta, perna e frequência
    B=BETA['btc'].where(ELIG); rk=B.rank(axis=1,pct=True)
    for s in ['BTC','ETH']:
        print(s,'beta médio vs BTC',B[s].mean().round(2),'vs idx',BETA['idx'][s].where(ELIG[:,list(R.columns).index(s)]).mean().round(2),
              'percentil médio',rk[s].mean().round(2),'% dias no tercil baixo',(rk[s]<=1/3).mean().round(2),'alto',(rk[s]>2/3).mean().round(2))
