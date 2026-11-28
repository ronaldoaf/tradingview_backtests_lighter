"""Risco por bootstrap em blocos: sorteia blocos de 60 pregoes dos retornos diarios da regra
(VIX/VIX3M<1, exec 16:20, funding modelo) e mede a distribuicao de CAGR e MDD em janelas de 5 anos.
Feito para o UVXY real (2011-2026) e para o sintetico 1,5x (2006-2026, inclui 2008)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
rng = np.random.default_rng(11)
H = 252 * 5; B = 60; N = 4000
log = []
def p(s):
    print(s); log.append(s)


p(f'# bootstrap em blocos de {B} pregoes, horizonte de 5 anos, {N} trajetorias')
for nm, X, px, ex in (('UVXY real 2011-26', D, 'c', 'pm'), ('sintetico 1,5x 2006-26', S, 'syn', 'close')):
    f = fund_model(X.ts.values); on = sg.ts(X, 1.0).fillna(0).values
    for lab, sig in (('VIX/VIX3M<1', on), ('short fixo', np.ones(len(X)))):
        for w in (0.15, 0.2, 0.25, 0.3, 0.4):
            res, ns, lq = sim(X, sig * w, px=px, exec=ex, fund=f, band=0.25)
            r = res.equity.pct_change().fillna(0).values[1:]
            n = len(r); cg = []; md = []
            for _ in range(N):
                st = rng.integers(0, n - B, size=H // B + 1)
                x = np.concatenate([r[s:s + B] for s in st])[:H]
                e = np.cumprod(1 + x)
                cg.append(e[-1] ** (1 / 5) - 1); md.append((e / np.maximum.accumulate(e) - 1).min())
            cg = np.array(cg); md = np.array(md)
            p(f'{nm:22s} {lab:11s} w={w:.2f}  CAGR mediano {np.median(cg)*100:5.1f}%  P(CAGR<0) {np.mean(cg<0)*100:4.1f}%  '
              f'MDD mediano {np.median(md)*100:6.1f}%  MDD p90 {np.percentile(md,10)*100:6.1f}%  P(MDD<-40%) {np.mean(md<-0.4)*100:4.1f}%  P(MDD<-60%) {np.mean(md<-0.6)*100:4.1f}%')
open(os.path.join(OUT, 's08_bootstrap.txt'), 'w').write('\n'.join(log) + '\n')
