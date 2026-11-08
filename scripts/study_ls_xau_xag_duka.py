# Long/short XAU x XAG com historico Dukascopy 1h (2015-2026). +1 = long ouro / short prata.
# Funding: diferenca media observada na Lighter (prata 12,8% - ouro 10,4% a.a.) aplicada como constante.
import pandas as pd,numpy as np
D='data/dukascopy_xau_xag/'
def L(f):
    d=pd.read_csv(D+f);d['t']=pd.to_datetime(d.iloc[:,0],utc=True);return d.set_index('t').close
df=pd.concat({'au':L('xauusd_h1.csv'),'ag':L('xagusd_h1.csv')},axis=1,sort=True).dropna()
df=df[(df>0).all(1)]
rau=np.log(df.au).diff().shift(-1); rag=np.log(df.ag).diff().shift(-1)
s=np.log(df.au)-np.log(df.ag); n=len(df)
FUND=(0.128-0.104)/8760   # por hora, recebido pelo long ouro/short prata
COST=0.0001; H=4
seg=np.where(df.index<'2022-01-01','tr',np.where(df.index<'2025-01-01','va','oos'))
def bt(sig,hedge):
    k=np.arange(n)%H==0
    p=sig.where(k).ffill().fillna(0).clip(-1,1)
    if hedge=='vol':
        v=(rau.shift(1).rolling(720).std()/rag.shift(1).rolling(720).std()).bfill()
        wau=(2/(1+v)).where(k).ffill(); wag=(2*v/(1+v)).where(k).ffill()
    else: wau=wag=pd.Series(1.0,df.index)
    a=p*wau;b=-p*wag
    r=a*rau+b*rag+p*FUND-(a.diff().abs()+b.diff().abs()).fillna(0)*COST
    return r.fillna(0),p
crit={}
for Ld in (1,3,7,14,21,30,60,90):
    m=np.sign(s-s.shift(Ld*24)); crit[f'mom{Ld}d']=m; crit[f'rev{Ld}d']=-m
crit['votos7-14-21-30']=sum(np.sign(s-s.shift(x*24)) for x in (7,14,21,30))/4
crit['rev_votos7-14-21-30']=-crit['votos7-14-21-30']
for N in (3,7,14,30,90):
    z=(s-s.rolling(N*24).mean())/s.rolling(N*24).std()
    crit[f'zrev{N}d']=(-z/2).clip(-1,1); crit[f'zmom{N}d']=(z/2).clip(-1,1)
    pos=np.zeros(n);q=0
    for i,v in enumerate(z.values):
        if np.isnan(v): q=0
        elif q==0: q=-1 if v>2 else (1 if v<-2 else 0)
        elif (q==1 and v>0) or (q==-1 and v<0): q=0
        pos[i]=q
    crit[f'zlim{N}d']=pd.Series(pos,df.index)
# nivel da razao (media longa): razao alta -> prata barata -> short ouro/long prata
for N in (180,365):
    z=(s-s.rolling(N*24).mean())/s.rolling(N*24).std(); crit[f'nivel_rev{N}d']=(-z/2).clip(-1,1)
for Ld in (7,30,90):
    crit[f'tend_ouro{Ld}d']=np.sign(np.log(df.au)-np.log(df.au).shift(Ld*24))
crit['fixo_longOuro']=pd.Series(1.0,df.index); crit['fixo_longPrata']=pd.Series(-1.0,df.index)
sh=lambda x:x.mean()/x.std()*np.sqrt(6000) if x.std()>0 else 0   # ~6000 h/ano de mercado
R=[]
for k,v in crit.items():
  for hd in ('igual','vol'):
    r,p=bt(v.fillna(0),hd); row=[f'{k}|{hd}']
    for sg in ('tr','va','oos'):
        x=r[seg==sg]; yrs=x.index.year.nunique(); row+=[x.sum()*100/yrs,sh(x)]
    row+=[(r.cumsum()-r.cumsum().cummax()).min()*100,int((p.diff().abs()>0).sum())]
    R.append(row)
R=pd.DataFrame(R,columns=['crit','tr%aa','shTr','va%aa','shVa','oos%aa','shOOS','maxDD%','trocas']).sort_values('shTr',ascending=False)
pd.set_option('display.width',220)
print('periodo',df.index[0],df.index[-1],'n crit',len(R))
print(R.round(2).to_string(index=False))
print('pos nos 3 trechos:',list(R[(R['tr%aa']>0)&(R['va%aa']>0)&(R['oos%aa']>0)].crit))
print('spearman shTr x shVa %.2f, shTr x shOOS %.2f'%(R[['shTr','shVa']].corr('spearman').iloc[0,1],R[['shTr','shOOS']].corr('spearman').iloc[0,1]))
tr=seg=='tr';rng=np.random.default_rng(0);mx=[]
for _ in range(30):
    best=-9
    for j in range(len(R)):
        rs=pd.Series(rng.choice([-1,1],size=n//72+2).repeat(72)[:n],df.index); best=max(best,sh(bt(rs,'igual')[0][tr]))
    mx.append(best)
print('Sharpe treino max por acaso: p50 %.2f p95 %.2f'%(np.median(mx),np.percentile(mx,95)))
R.to_csv('results/ls_xau_xag_duka.csv',index=False)
