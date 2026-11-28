"""Detalhe do vendido UVXY + SPY (hedge junto, beta fixo 4,4): ano a ano, picos, dias de salto e
queda em 5 anos por bootstrap, contra a regra so no UVXY."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from s13_uvxy_spy import D, S, fR, fS, build, OUT

V = {'so UVXY': (0.0, 0.0), 'h=0,5 funding 3,6%': (0.5, 0.036), 'h=1 funding 3,6%': (1.0, 0.036),
     'h=0,5 funding 8%': (0.5, 0.08), 'h=1 funding 8%': (1.0, 0.08)}
RR = {}; RS = {}
for k, (h, fu) in V.items():
    (r, e), _ = build(D, 'c', fR, 'pm', 'ts<1', 'junto', 'fixo', h, 2e-4, fu)
    (rs, es), _ = build(S, 'syn', fS, 'close', 'ts<1', 'junto', 'fixo', h, 2e-4, fu)
    RR[k] = (r, e); RS[k] = (rs, es)
log = []
def p(s=''):
    print(s); log.append(s)


def yr(e):
    y = e.resample('YE').last(); y0 = pd.concat([pd.Series([e.iloc[0]], index=[e.index[0]]), y])
    o = y0.pct_change().dropna(); o.index = o.index.year; return o


p('# Ano a ano (2007-2010 do sintetico)')
p('| Ano | ' + ' | '.join(V) + ' | SPY |'); p('| ---: |' + ' ---: |' * (len(V) + 1))
spy = D.spyc.resample('YE').last().pct_change(); spy.index = spy.index.year
spyS = S.spyc.resample('YE').last().pct_change(); spyS.index = spyS.index.year
for y in list(range(2007, 2011)) + list(range(2012, 2027)):
    src = RS if y <= 2010 else RR
    cells = [f'{yr(src[k][1]).get(y, np.nan)*100:+.1f}%' for k in V]
    sp = (spyS if y <= 2010 else spy).get(y, np.nan)
    p(f'| {y} | ' + ' | '.join(cells) + f' | {sp*100:+.1f}% |')

p('\n# Picos (retorno na janela; queda dentro dela)')
EP = [('2015-08-17', '2015-09-30', 'ago/2015'), ('2015-12-01', '2016-02-29', 'dez/15-fev/16'), ('2018-01-26', '2018-02-28', 'fev/2018'),
      ('2018-10-01', '2018-12-31', 'T4 2018'), ('2020-02-19', '2020-04-30', 'Covid'), ('2020-06-08', '2020-06-30', 'jun/2020'),
      ('2022-01-01', '2022-10-31', 'bear 2022'), ('2024-07-15', '2024-08-30', 'ago/2024'), ('2025-03-26', '2025-04-30', 'abr/2025'),
      ('2026-11-02', '2026-11-27', 'nov/2026')]
EPs = [('2008-09-01', '2008-12-31', 'set-dez/2008 (sint.)'), ('2010-04-20', '2010-07-31', 'flash crash 2010 (sint.)'),
       ('2011-07-20', '2011-10-31', 'ago/2011 (sint.)')]
p('| Episodio | ' + ' | '.join(V) + ' |'); p('| --- |' + ' ---: |' * len(V))
for src, eps in ((RR, EP), (RS, EPs)):
    for a, b, nm in eps:
        cells = []
        for k in V:
            e = src[k][1]; i0 = max(e.index.searchsorted(pd.Timestamp(a)) - 1, 0); i1 = e.index.searchsorted(pd.Timestamp(b), side='right') - 1
            seg = e.iloc[i0:i1 + 1]; cells.append(f'{(seg.iloc[-1]/seg.iloc[0]-1)*100:+.1f}% ({(seg/seg.cummax()-1).min()*100:.0f}%)')
        p(f'| {nm} | ' + ' | '.join(cells) + ' |')

p('\n# Os 8 piores dias da regra so no UVXY e o mesmo dia com o hedge')
r0 = RR['so UVXY'][0]
worst = r0.nsmallest(8).index
p('| Dia | ' + ' | '.join(V) + ' |'); p('| --- |' + ' ---: |' * len(V))
for d in worst:
    p(f'| {d.date()} | ' + ' | '.join(f'{RR[k][0][d]*100:+.1f}%' for k in V) + ' |')

p('\n# Queda em 5 anos, bootstrap em blocos de 60 pregoes (4.000 trajetorias)')
rng = np.random.default_rng(3); B = 60; H = 252 * 5
for k in V:
    for lab, src in (('real', RR), ('sint', RS)):
        r = src[k][0].values[1:]; n = len(r); md = []; cg = []
        for _ in range(4000):
            st = rng.integers(0, n - B, size=H // B + 1); x = np.concatenate([r[s0:s0 + B] for s0 in st])[:H]
            e = np.cumprod(1 + x); md.append((e / np.maximum.accumulate(e) - 1).min()); cg.append(e[-1] ** 0.2 - 1)
        md = np.array(md)
        p(f'{k:20s} {lab}: CAGR mediano {np.median(cg)*100:5.1f}%  P(CAGR<0) {np.mean(np.array(cg)<0)*100:4.1f}%  queda mediana {np.median(md)*100:6.1f}%  '
          f'pior 10% {np.percentile(md,10)*100:6.1f}%  P(queda>40%) {np.mean(md<-0.4)*100:4.1f}%')
open(os.path.join(OUT, 's14_uvxy_spy_detalhe.txt'), 'w').write('\n'.join(log) + '\n')
