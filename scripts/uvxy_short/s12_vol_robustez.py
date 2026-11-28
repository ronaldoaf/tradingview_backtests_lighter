"""Robustez do tamanho 'maior com vol alta' (familia pro do s11) contra a base (w fixo 0,25), com a mesma vol anual.
1. Diferenca de Sharpe por bootstrap pareado em blocos de 60 pregoes (mesmos dias nas duas series)
2. Ano a ano
3. Episodios de pico
4. Distribuicao de queda em 5 anos (bootstrap em blocos)
5. Inverso (menor com vol alta) para comparacao e teto de tamanho"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model, yearly
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
f = fund_model(D.ts.values); fS = fund_model(S.ts.values)
W0 = 0.25
log = []
def p(s=''):
    print(s); log.append(s)


def vol(X, px, kind, n):
    r = np.log(X[px]).diff()
    if kind == 'ew':
        return np.sqrt((r ** 2).ewm(halflife=n, min_periods=n).mean() * 252)
    return r.rolling(n, min_periods=n).std() * np.sqrt(252)


def size(X, px, kind, n, a):
    v = vol(X, px, kind, n); ref = v.expanding(min_periods=60).median()
    return ((v / ref) ** a).fillna(0).values


def run(X, w, px, ff, ex):
    res, ns, lq = sim(X, w, px=px, exec=ex, fund=ff, band=0.25)
    return stats(res, ns, lq), res


def match(X, base, px, ff, ex, target, cap):
    lo, hi = 0.001, 5.0
    for _ in range(22):
        k = (lo + hi) / 2
        v = run(X, np.minimum(base * k, cap), px, ff, ex)[0]['vol']
        lo, hi = (k, hi) if v < target else (lo, k)
    return np.minimum(base * lo, cap)


onR = sg.ts(D, 1.0).fillna(0).values; onS = sg.ts(S, 1.0).fillna(0).values
sR, rR = run(D, onR * W0, 'c', f, 'pm'); sS, rS = run(S, onS * W0, 'syn', fS, 'close')
V = {'base (w fixo 0,25)': None,
     'maior c/ vol: EWMA 5d, a=1': ('ew', 5, 1), 'maior c/ vol: EWMA 10d, a=0,5': ('ew', 10, 0.5),
     'maior c/ vol: EWMA 10d, a=1': ('ew', 10, 1), 'maior c/ vol: fech. 10d, a=1': ('cc', 10, 1),
     'maior c/ vol: fech. 20d, a=1': ('cc', 20, 1),
     'menor c/ vol: fech. 20d, a=1': ('cc', 20, -1), 'menor c/ vol: EWMA 10d, a=1': ('ew', 10, -1)}
CAPS = (1.0, 0.5)
RES = {}
p('# Mesma vol anual da base; IS 2011-2018, OOS 2019-2026; sintetico 2006-2026 com escala propria')
p('| Variante | teto w | w medio | w max | Sharpe | CAGR | Queda | Pior dia | Sharpe OOS | Queda OOS | Sharpe sint. | Queda sint. |')
p('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
iIS = int((D.index <= '2018-12-31').sum())
for nm, spec in V.items():
    for cap in CAPS:
        if spec is None and cap != 1.0:
            continue
        if spec is None:
            w, wS = onR * W0, onS * W0
        else:
            w = match(D, onR * size(D, 'c', *spec), 'c', f, 'pm', sR['vol'], cap)
            wS = match(S, onS * size(S, 'syn', *spec), 'syn', fS, 'close', sS['vol'], cap)
        a, ra = run(D, w, 'c', f, 'pm')
        o, _ = run(D.iloc[iIS:], w[iIS:], 'c', f[iIS:], 'pm')
        s, rs = run(S, wS, 'syn', fS, 'close')
        RES[(nm, cap)] = (ra, rs, w)
        p(f'| {nm} | {cap:g} | {w[w>0].mean():.2f} | {w.max():.2f} | {a["sharpe"]:.2f} | {a["cagr"]*100:.1f}% | {a["mdd"]*100:.1f}% | '
          f'{a["worst"]*100:.1f}% | {o["sharpe"]:.2f} | {o["mdd"]*100:.1f}% | {s["sharpe"]:.2f} | {s["mdd"]*100:.1f}% |')

rng = np.random.default_rng(5)
B = 60; N = 3000


def sharpe(x):
    return x.mean() / x.std() * np.sqrt(252)


p('\n# Bootstrap pareado da diferenca de Sharpe contra a base (blocos de 60 pregoes, 3.000 sorteios)')
base_r = rR.equity.pct_change().fillna(0).values[1:]; base_s = rS.equity.pct_change().fillna(0).values[1:]
for (nm, cap), (ra, rs, w) in RES.items():
    if nm.startswith('base'):
        continue
    out = []
    for lab, x, y in (('real', ra.equity.pct_change().fillna(0).values[1:], base_r),
                      ('sint', rs.equity.pct_change().fillna(0).values[1:], base_s)):
        n = len(x); d = []
        for _ in range(N):
            st = rng.integers(0, n - B, size=n // B + 1)
            idx = np.concatenate([np.arange(s0, s0 + B) for s0 in st])[:n]
            d.append(sharpe(x[idx]) - sharpe(y[idx]))
        d = np.array(d)
        out.append(f'{lab}: dif {sharpe(x)-sharpe(y):+.2f}, IC90% [{np.percentile(d,5):+.2f}, {np.percentile(d,95):+.2f}], P(dif<=0) {np.mean(d<=0):.2f}')
    p(f'{nm:32s} teto {cap:g} | ' + ' | '.join(out))

p('\n# Ano a ano (real; 2007-2010 do sintetico), teto 1,0')
keys = [('base (w fixo 0,25)', 1.0), ('maior c/ vol: EWMA 10d, a=0,5', 1.0), ('maior c/ vol: EWMA 5d, a=1', 1.0),
        ('menor c/ vol: fech. 20d, a=1', 1.0)]
Y = {}
for k in keys:
    ra, rs, _ = RES[k]
    y = pd.concat([yearly(rs).loc[2007:2010], yearly(ra).loc[2012:]])
    Y[k[0]] = y * 100
Y = pd.DataFrame(Y)
p('| Ano | ' + ' | '.join(Y.columns) + ' |'); p('| ---: |' + ' ---: |' * len(Y.columns))
for yv, r in Y.iterrows():
    p(f'| {yv} | ' + ' | '.join(f'{v:+.1f}%' for v in r.values) + ' |')

p('\n# Episodios de pico (retorno na janela e queda dentro dela), teto 1,0')
EP = [('2015-08-17', '2015-09-30', 'ago/2015'), ('2015-12-01', '2016-02-29', 'dez/15-fev/16'),
      ('2018-01-26', '2018-02-28', 'fev/2018'), ('2018-10-01', '2018-12-31', 'T4 2018'), ('2020-02-19', '2020-04-30', 'Covid'),
      ('2020-05-01', '2020-12-31', 'mai-dez/2020 (pos-Covid)'), ('2022-01-01', '2022-10-31', 'bear 2022'),
      ('2024-07-15', '2024-08-30', 'ago/2024'), ('2025-03-26', '2025-04-30', 'abr/2025'),
      ('2025-05-01', '2025-07-31', 'mai-jul/2025 (pos-tarifas)'), ('2026-11-02', '2026-11-27', 'nov/2026')]
p('| Episodio | ' + ' | '.join(k[0] for k in keys) + ' |'); p('| --- |' + ' ---: |' * len(keys))
for a_, b_, nm in EP:
    cells = []
    for k in keys:
        e = RES[k][0].equity
        i0 = max(e.index.searchsorted(pd.Timestamp(a_)) - 1, 0); i1 = e.index.searchsorted(pd.Timestamp(b_), side='right') - 1
        seg = e.iloc[i0:i1 + 1]
        cells.append(f'{(seg.iloc[-1]/seg.iloc[0]-1)*100:+.1f}% ({(seg/seg.cummax()-1).min()*100:.0f}%)')
    p(f'| {nm} | ' + ' | '.join(cells) + ' |')

p('\n# Queda em janelas de 5 anos (bootstrap em blocos de 60 pregoes, 4.000 trajetorias)')
H = 252 * 5
for k in keys + [('maior c/ vol: EWMA 10d, a=0,5', 0.5)]:
    for lab, res in (('real', RES[k][0]), ('sint', RES[k][1])):
        r = res.equity.pct_change().fillna(0).values[1:]; n = len(r); md = []; cg = []
        for _ in range(4000):
            st = rng.integers(0, n - B, size=H // B + 1)
            x = np.concatenate([r[s0:s0 + B] for s0 in st])[:H]; e = np.cumprod(1 + x)
            md.append((e / np.maximum.accumulate(e) - 1).min()); cg.append(e[-1] ** 0.2 - 1)
        md = np.array(md)
        p(f'{k[0]:32s} teto {k[1]:g} {lab}: CAGR mediano {np.median(cg)*100:5.1f}%  queda mediana {np.median(md)*100:6.1f}%  '
          f'pior 10% {np.percentile(md,10)*100:6.1f}%  P(queda>40%) {np.mean(md<-0.4)*100:4.1f}%')
open(os.path.join(OUT, 's12_vol_robustez.txt'), 'w').write('\n'.join(log) + '\n')
