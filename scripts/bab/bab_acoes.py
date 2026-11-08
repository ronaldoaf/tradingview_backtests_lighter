# BAB em ações da Lighter + XAU, WTI, US100 (subjacente diário 2015-2026; custo snapshot VPS, funding médio Lighter)
import json,glob,numpy as np,pandas as pd
OUT='/mnt/project-files/estrategias/bab/'
A=pd.read_csv('/mnt/project-files/estrategias/indice_acoes_lighter/dados/acoes_eua_diario.csv',index_col=0,parse_dates=True)
def yh(f):
    r=json.load(open(f))['chart']['result'][0]; t=pd.to_datetime(r['timestamp'],unit='s').normalize()
    return pd.Series(r['indicators']['adjclose'][0]['adjclose'] if 'adjclose' in r['indicators'] else r['indicators']['quote'][0]['close'],t).groupby(level=0).last()
A['XAU']=yh(OUT+'y_GC%3DF.json').reindex(A.index).ffill(limit=2)
A['WTI']=yh(OUT+'y_CL%3DF.json').reindex(A.index).ffill(limit=2)
A['US100']=A['^NDX']; A=A.drop(columns=['^NDX','^GSPC','QQQ','SPY'])
R=A.pct_change(fill_method=None)
R[(A<=0)|(A.shift()<=0)]=np.nan; R=R.clip(-0.5,1.0)   # WTI negativo em abr/2020
M=R['US100']; D=R.index; n=len(D)
# custo: snapshot VPS cost_5000 por lado (mín 0,02%); funding: média anual Lighter (long paga)
met=json.load(open(OUT+'metrics.json')); cols=met['columns']
cst={r[1]:r[cols.index('cost_5000')] for r in met['rows']}
CST=np.array([max(cst.get(s,0.001) or 0.001,0.0002) for s in R.columns])
FU=np.array([json.load(open(OUT+f'fund/{s}.json'))['anual']/252 if glob.glob(OUT+f'fund/{s}.json') else 0.05/252 for s in R.columns])
lr=np.log1p(R)
def betas(win_s=252,win_c=756):
    m=np.log1p(M); sd=lr.rolling(win_s,min_periods=120).std(); sdm=m.rolling(win_s,min_periods=120).std()
    rho=lr.rolling(3).sum().rolling(win_c,min_periods=250).corr(m.rolling(3).sum())
    return (0.6*rho.mul(sd).div(sdm,axis=0)+0.4).where(R.notna())
BETA=betas(); VOL=lr.rolling(252,min_periods=120).std()
ELIG=(R.notna()&(R.notna().rolling(250).sum()>=250)).values
Rv=R.fillna(0).values
def weights(b,mode,rng=None):
    ok=~np.isnan(b)
    if ok.sum()<9: return None
    idx=np.where(ok)[0]; bb=b[idx]
    if rng is not None: bb=rng.permutation(bb)
    W=np.zeros(len(b))
    if mode in('fp','fp_dn'):
        z=pd.Series(bb).rank().values; d=z-z.mean(); k=2/np.abs(d).sum()
        wh=k*np.clip(d,0,None); wl=k*np.clip(-d,0,None)
        if mode=='fp': wl=wl/(wl*b[idx]).sum(); wh=wh/(wh*b[idx]).sum()
        W[idx]=wl-wh
    else:
        o=np.argsort(bb); t=len(o)//3; lo=idx[o[:t]]; hi=idx[o[-t:]]
        if mode=='ew_dn': W[lo]=1/t; W[hi]=-1/t
        else: W[lo]=1/t/b[lo].mean(); W[hi]=-1/t/b[hi].mean()
    g=np.abs(W).sum()
    if g>3: W*=3/g
    return W
def run(sig,mode,Rb=21,rng=None,ex=None,fcost=None):
    S=sig.where(ELIG).values.copy()
    if ex is not None: S[:,[list(R.columns).index(e) for e in ex]]=np.nan
    c=CST if fcost is None else np.full(len(CST),fcost)
    W=np.zeros(S.shape[1]); out=np.zeros(n); start=260
    for i in range(start,n-1):
        if (i-start)%Rb==0:
            Wn=weights(S[i],mode,rng)
            if Wn is not None: out[i+1]-=(np.abs(Wn-W)*c).sum(); W=Wn
        out[i+1]+=(W*Rv[i+1]).sum()-(W*FU).sum(); W=W*(1+Rv[i+1])
    return pd.Series(out,D)[D[start+1]:]
P=[('treino','2015-01-01','2019-12-31'),('valid','2020-01-01','2022-12-31'),('oos','2023-01-01','2026-12-31')]
def st(p):
    if len(p)<30 or p.std()==0: return np.nan,np.nan,np.nan
    eq=(1+p).cumprod(); return eq.iloc[-1]**(252/len(p))-1,p.mean()/p.std()*np.sqrt(252),(eq/eq.cummax()-1).min()
def row(p,**k):
    d=dict(k)
    for nm,a,b in P:
        c,s,dd=st(p[a:b]); d[nm+'_cagr']=c; d[nm+'_sh']=s; d[nm+'_dd']=dd
    return d
if __name__=='__main__':
    print('ativos elegíveis/dia por ano:',pd.Series(ELIG.sum(1),D).resample('YE').mean().round(0).to_dict())
    rows=[];cur={}
    for ex in [None,['XAU','WTI']]:
        for sname,sig in [('beta',BETA),('vol',VOL)]:
            for mode in ['fp','fp_dn','ew_dn','ew_bn']:
                if sname=='vol' and mode in('fp','ew_bn'): continue
                for Rb in [5,21]:
                    p=run(sig,mode,Rb,ex=ex); k=dict(univ='so_acoes' if ex else 'acoes+XAU+WTI',sinal=sname,modo=mode,R=Rb)
                    rows.append(row(p,**k)); cur['_'.join(map(str,k.values()))]=p
    df=pd.DataFrame(rows); df.to_csv(OUT+'grid_acoes.csv',index=False); pd.DataFrame(cur).to_csv(OUT+'curvas_acoes.csv')
    pd.set_option('display.width',250); print(df.round(2).to_string())
    rng=np.random.default_rng(0); pl=pd.DataFrame([row(run(BETA,'fp',21,rng)) for _ in range(200)]); pl.to_csv(OUT+'placebo_acoes.csv',index=False)
    print(pl[[c for c in pl if c.endswith('_sh')]].describe(percentiles=[.95]).round(2))
    rk=BETA.where(ELIG).rank(axis=1,pct=True)
    for s in ['XAU','WTI','US100']:
        print(s,'beta médio',BETA[s].mean().round(2),'percentil',rk[s].mean().round(2),'tercil baixo',(rk[s]<=1/3).mean().round(2),'alto',(rk[s]>2/3).mean().round(2))
    # contribuição dos 5 ativos no FP mensal
    print('beta médio por ano:'); print(BETA[['XAU','WTI','US100']].resample('YE').mean().round(2).T.to_string())
