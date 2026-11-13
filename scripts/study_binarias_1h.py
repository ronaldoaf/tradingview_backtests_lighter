"""Binárias 1h (AlphaX): prever sinal de close[t+60]-close[t] com dados 1m.
Payout 85%, empate = perda. Apostas sem sobreposição (cooldown 60m) por regra.
Treino < 2024-06, Validação 2024-06..2025-05, OOS >= 2025-06."""
import numpy as np, pandas as pd, itertools, sys
H=int(next((a.split('=')[1] for a in sys.argv if a.startswith('--h=')),60))
PAY={5:.70,10:.75,30:.80,60:.85}[H]; BE=1/(1+PAY)
SUF='' if H==60 else f'_{H}m'
T1=pd.Timestamp('2024-06-01',tz='UTC').value//10**6; T2=pd.Timestamp('2025-06-01',tz='UTC').value//10**6
def load(s):
    d=pd.read_parquet(f'data/binance/klines_1m/{s}USDT.parquet').sort_values('ts').reset_index(drop=True)
    full=np.arange(d.ts.iloc[0],d.ts.iloc[-1]+1,60000)
    d=d.set_index('ts').reindex(full).ffill().reset_index().rename(columns={'index':'ts'})
    return d
D={s:load(s) for s in ['BTC','ETH']}
n=min(len(D['BTC']),len(D['ETH']))
assert (D['BTC'].ts.values[:n]==D['ETH'].ts.values[:n]).all()
def feats(d,o):
    c=d.c.values; F={}
    y=np.full(len(c),np.nan); y[:-H]=np.sign(c[H:]-c[:-H]); F['y']=y
    lr=np.log(c)
    for L in [1,3,5,15,30,60,240,1440]:
        r=np.full(len(c),np.nan); r[L:]=lr[L:]-lr[:-L]; F[f'r{L}']=r
    r1=np.r_[0,np.diff(lr)]
    v=pd.Series(r1).rolling(60).std().values; vl=pd.Series(r1).rolling(1440*7).std().values
    F['vr']=v/vl
    for L in [15,60,240,1440]:
        F[f'z{L}']=F[f'r{L}']/(v*np.sqrt(L))
    for W in [60,240,1440]:
        m=pd.Series(c).rolling(W).mean().values; F[f'ma{W}']=(c-m)/(c*v*np.sqrt(W))
    rng=(d.h.values-d.l.values)/c; F['bar']=rng/pd.Series(rng).rolling(1440).median().values*np.sign(r1)
    ro=pd.Series(r1)
    up=ro.clip(lower=0).ewm(alpha=1/14).mean(); dn=(-ro.clip(upper=0)).ewm(alpha=1/14).mean()
    F['rsi14']=(100-100/(1+up/dn)).values
    hi=pd.Series(d.h.values).rolling(60).max().values; lo=pd.Series(d.l.values).rolling(60).min().values
    F['pos60']=(c-lo)/(hi-lo)
    vol=d.v.values; F['vz']=vol/pd.Series(vol).rolling(1440).median().values
    step=1000 if c[-1]>10000 else 100
    F['rnd']=(c%step)/step
    o_=o.c.values; lo_=np.log(o_)
    for L in [5,15,60]:
        ro_=np.full(len(c),np.nan); ro_[L:]=lo_[L:]-lo_[:-L]; F[f'rel{L}']=F[f'r{L}']-ro_
    t=pd.to_datetime(d.ts.values,unit='ms',utc=True)
    F['hr']=t.hour.values; F['mn']=t.minute.values; F['dow']=t.dayofweek.values
    return {k:np.asarray(v)[:n] for k,v in F.items()}
FE={'BTC':feats(D['BTC'].iloc[:n],D['ETH'].iloc[:n]),'ETH':feats(D['ETH'].iloc[:n],D['BTC'].iloc[:n])}
ts=D['BTC'].ts.values[:n]
per=np.where(ts<T1,0,np.where(ts<T2,1,2)); valid=np.arange(n)>=1440*7; valid[-61:]=False

def cooldown(idx):
    out=[];last=-10**9
    for i in idx:
        if i>=last+H: out.append(i); last=i
    return np.array(out,dtype=int)
def evalrule(F,mask,dirn):
    idx=np.flatnonzero(mask&valid&np.isfinite(F['y']))
    idx=cooldown(idx)
    res=[]
    for p in range(3):
        k=idx[per[idx]==p]
        d=dirn[k] if hasattr(dirn,'__len__') else dirn
        w=(F['y'][k]*d>0); res+= [len(k), w.mean() if len(k) else np.nan]
    return res
def quant(x,q,sel):  # thresholds from training only
    return np.nanquantile(x[sel],q)
tr=per==0
rules=[]
for A in ['BTC','ETH']:
    F=FE[A]
    # 1 extremos de features contínuas: seguir ou reverter
    cont=[k for k in F if k not in('y','hr','mn','dow')]
    for k in cont:
        x=F[k]
        for q in [0.005,0.02,0.05,0.1,0.2]:
            lo,hi=quant(x,q,tr),quant(x,1-q,tr)
            for side,m in [('baixo',x<=lo),('alto',x>=hi)]:
                for d in (1,-1):
                    rules.append((A,f'{k} {side} q{q}',d,m))
    # 2 hora do dia (entrada no minuto 0) e hora x dia da semana
    m0=F['mn']==0
    for h in range(24):
        for d in (1,-1):
            rules.append((A,f'hora {h}h',d,m0&(F['hr']==h)))
            for w in range(7):
                rules.append((A,f'hora {h}h dow{w}',d,m0&(F['hr']==h)&(F['dow']==w)))
    # 3 reversão condicionada a regime de vol
    for L in [15,60,240]:
        z=F[f'z{L}']
        for vq in [0.2,0.8]:
            vm=F['vr']<=quant(F['vr'],vq,tr) if vq<0.5 else F['vr']>=quant(F['vr'],vq,tr)
            for q in [0.02,0.1]:
                lo,hi=quant(z,q,tr),quant(z,1-q,tr)
                for d in (1,-1):
                    rules.append((A,f'z{L} extremo & vol{"baixa" if vq<.5 else "alta"} q{q}',
                                  np.where(z>=hi,d,-d),vm&((z<=lo)|(z>=hi))))
print('regras',len(rules),file=sys.stderr)
if '--final' not in sys.argv:
  rows=[]
  for A,name,d,m in rules:
    r=evalrule(FE[A],m,d)
    rows.append([A,name,d if np.isscalar(d) else 0]+r)
  R=pd.DataFrame(rows,columns=['ativo','regra','dir','n_tr','hit_tr','n_val','hit_val','n_oos','hit_oos'])
  R.to_csv(f'results/binarias_1h_grid{SUF}.csv',index=False)
  print(len(R))

from math import comb, sqrt
def pval(k,n,p=BE):  # P(X>=k), normal approx with continuity
    if n==0: return 1.0
    mu=n*p; sd=sqrt(n*p*(1-p)); z=(k-0.5-mu)/sd
    from math import erfc; return 0.5*erfc(z/sqrt(2))
if '--final' in sys.argv:
    G=pd.read_csv(f'results/binarias_1h_grid{SUF}.csv')
    lb=lambda h,n: h-1.645*np.sqrt(h*(1-h)/n)
    S=G[(G.n_tr>=150)&(G.n_val>=100)&(lb(G.hit_tr,G.n_tr)>BE)&(lb(G.hit_val,G.n_val)>BE)]
    print('finalistas',len(S),'de',len(G))
    key={(A,nm,(d if np.isscalar(d) else 0)):(d,m) for A,nm,d,m in rules}
    out=[]
    for _,r in S.iterrows():
        d,m=key[(r.ativo,r.regra,r.dir)]
        F=FE[r.ativo]
        for lag in (0,1,2):
            y=np.full(n,np.nan); c=D[r.ativo].c.values[:n]
            y[:-61-lag]=np.sign(c[H+lag:n-61+H] - c[lag:n-61]) if lag else F['y'][:-61-lag]
            G2=dict(F); G2['y']=y
            res=evalrule(G2,m,d)
            no,ho=res[4],res[5]; k=round(no*ho)
            out.append([r.ativo,r.regra,r.dir,lag]+res+[ho*PAY-(1-ho), pval(k,no)])
    O=pd.DataFrame(out,columns=['ativo','regra','dir','lag','n_tr','hit_tr','n_val','hit_val','n_oos','hit_oos','ev_oos','p_oos'])
    O.to_csv(f'results/binarias_1h_finalistas{SUF}.csv',index=False)
    pd.set_option('display.width',250); print(O.round(4).to_string())
