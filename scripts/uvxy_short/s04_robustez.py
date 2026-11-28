"""Robustez da regra principal (vendido no UVXY so com VIX/VIX3M < 1) contra o short fixo.

1. Fronteira de alavancagem (w) - real 2011-2026, IS/OOS e sintetico 1,5x 2006-2026
2. Sensibilidade ao limiar de VIX/VIX3M
3. Momento de execucao (fechamento, 16:20 ET, abertura seguinte, fechamento seguinte)
4. Custos e banda de rebalanceio
5. Cenarios de funding
6. Placebo: periodos fora do mercado sorteados (mesmo numero e duracao) - p-valor
7. Episodios de pico de volatilidade
8. Hedge com short no S&P 500
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model, fmt, yearly
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
os.makedirs(OUT, exist_ok=True)
D0 = load()
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna()]
f = fund_model(D.ts.values); fS = fund_model(S.ts.values)
W = 0.3
BASE = dict(exec='pm', band=0.25)
ON = sg.ts(D, 1.0).fillna(0).values
ONS = sg.ts(S, 1.0).fillna(0).values
ALL = np.ones(len(D)); ALLS = np.ones(len(S))
iIS = int((D.index <= '2018-12-31').sum())


def st(w, DD=D, ff=None, px='c', **kw):
    ff = f if ff is None else ff
    a = dict(BASE); a.update(kw)
    res, ns, lq = sim(DD, w, px=px, fund=ff, **a)
    return stats(res, ns, lq), res


def line(s):
    return 'CAGR %6.1f%%  MDD %6.1f%%  Sh %5.2f  pior dia %6.1f%%  exposto %3.0f%%  giro %4.1fx%s' % (
        s['cagr'] * 100, s['mdd'] * 100, s['sharpe'], s['worst'] * 100, s['expo'] * 100, s['turn'], '  LIQ' if s['liq'] else '')


log = []
def p(*a):
    s = ' '.join(str(x) for x in a); print(s); log.append(s)


p('# 1. Fronteira de alavancagem (exec 16:20 ET, banda 25%, custo 10 bp/perna, funding modelo)')
for nm, on, ons in (('short fixo', ALL, ALLS), ('VIX/VIX3M<1', ON, ONS)):
    for w in (0.1, 0.2, 0.3, 0.4, 0.5, 0.75):
        a, _ = st(on * w)
        i, _ = st((on * w)[:iIS], DD=D.iloc[:iIS], ff=f[:iIS])
        o, _ = st((on * w)[iIS:], DD=D.iloc[iIS:], ff=f[iIS:])
        s, _ = st(ons * w, DD=S, ff=fS, px='syn', exec='close')
        p(f'{nm:12s} w={w:.2f} | 2011-26 {line(a)}')
        p(f'{"":12s}        | IS      {line(i)}')
        p(f'{"":12s}        | OOS     {line(o)}')
        p(f'{"":12s}        | SINT06+ {line(s)}')

p('\n# 2. Limiar de VIX/VIX3M (w=0,3)')
for th in (0.85, 0.9, 0.925, 0.95, 0.975, 1.0, 1.025, 1.05, 1.1, 9):
    on = sg.ts(D, th).fillna(0).values; ons = sg.ts(S, th).fillna(0).values
    a, _ = st(on * W); o, _ = st((on * W)[iIS:], DD=D.iloc[iIS:], ff=f[iIS:])
    s, _ = st(ons * W, DD=S, ff=fS, px='syn', exec='close')
    p(f'ts<{th:<5} 2011-26 {line(a)} | OOS CAGR {o["cagr"]*100:6.1f}% MDD {o["mdd"]*100:6.1f}% | SINT06+ CAGR {s["cagr"]*100:6.1f}% MDD {s["mdd"]*100:6.1f}%')

p('\n# 3. Momento de execucao (w=0,3)')
for nm, on in (('short fixo', ALL), ('VIX/VIX3M<1', ON)):
    for ex in ('close', 'pm', 'open', 'close+1'):
        w = on * W
        if ex == 'close+1':
            a, _ = st(np.r_[0, w[:-1]], exec='close')
        else:
            a, _ = st(w, exec=ex)
        p(f'{nm:12s} exec {ex:8s} {line(a)}')

p('\n# 4. Custo por perna e banda de rebalanceio (VIX/VIX3M<1, w=0,3)')
for c in (0, 10e-4, 20e-4, 30e-4):
    for b in (0.0, 0.25, 0.5, 1.0):
        a, _ = st(ON * W, cost=c, band=b)
        p(f'custo {c*1e4:4.0f} bp banda {b:4.2f} {line(a)}')

p('\n# 5. Funding (w=0,3)')
FS = {'zero': np.zeros(len(D)), 'modelo (+5,5/-33 bp por pregao)': f,
      'pessimista (0 / -50 bp)': fund_model(D.ts.values, 0.0, -50e-4),
      'vendido paga 10%/ano sempre': np.full(len(D), -0.10 / 252),
      'vendido recebe 14%/ano sempre': np.full(len(D), 0.14 / 252)}
for nm, on in (('short fixo', ALL), ('VIX/VIX3M<1', ON)):
    for k, ff in FS.items():
        a, _ = st(on * W, ff=ff)
        p(f'{nm:12s} {k:32s} {line(a)}')

p('\n# 6. Placebo: mesmos periodos fora (numero e duracao) em ordem aleatoria, 1000 sorteios (w=0,3)')


def runs(x):
    """codificacao de corridas: lista de (valor, duracao)"""
    out = []; v = x[0]; n = 0
    for e in x:
        if e == v:
            n += 1
        else:
            out.append((v, n)); v = e; n = 1
    out.append((v, n))
    return out


def placebo(x, rng):
    r = runs(x)
    ones = [n for v, n in r if v == 1]; zeros = [n for v, n in r if v == 0]
    rng.shuffle(ones); rng.shuffle(zeros)
    first = r[0][0]; out = []
    a, b = (ones, zeros) if first == 1 else (zeros, ones)
    va, vb = (1, 0) if first == 1 else (0, 1)
    for i in range(max(len(a), len(b))):
        if i < len(a): out += [va] * a[i]
        if i < len(b): out += [vb] * b[i]
    return np.array(out[:len(x)], dtype=float)


rng = np.random.default_rng(7)
real, _ = st(ON * W)
P = []
for i in range(1000):
    x = placebo(ON, rng)
    s, _ = st(x * W)
    P.append((s['cagr'], s['mdd'], s['sharpe']))
P = np.array(P)
p('real: ' + line(real))
p('placebo mediano: CAGR %.1f%%  MDD %.1f%%  Sh %.2f' % tuple(np.median(P, 0) * [100, 100, 1]))
p('p-valor (placebo >= real): CAGR %.3f  MDD %.3f  Sharpe %.3f' % (
    (P[:, 0] >= real['cagr']).mean(), (P[:, 1] >= real['mdd']).mean(), (P[:, 2] >= real['sharpe']).mean()))
Pdf = pd.DataFrame(P, columns=['cagr', 'mdd', 'sharpe']); Pdf.to_csv(os.path.join(OUT, 's04_placebo.csv'), index=False)

p('\n# 7. Episodios de pico (retorno da estrategia na janela; w=0,3, exec 16:20)')
EP = [('2011-10-04', '2011-12-30', 'out-dez/2011 (fim da crise do euro)'), ('2014-10-01', '2014-10-31', 'out/2014'),
      ('2015-08-17', '2015-09-30', 'ago/2015 (desvalorizacao da China)'), ('2015-12-01', '2016-02-29', 'dez/15-fev/16'),
      ('2016-06-20', '2016-07-08', 'Brexit'), ('2018-01-26', '2018-02-28', 'Volmageddon fev/2018'),
      ('2018-10-01', '2018-12-31', 'T4 2018'), ('2020-02-19', '2020-04-30', 'Covid'), ('2020-06-08', '2020-06-30', 'jun/2020'),
      ('2021-01-20', '2021-02-05', 'GameStop jan/2021'), ('2022-01-01', '2022-10-31', 'bear 2022'),
      ('2023-03-06', '2023-03-24', 'SVB mar/2023'), ('2024-07-15', '2024-08-30', 'carry trade ago/2024'),
      ('2025-03-26', '2025-04-30', 'tarifas abr/2025'), ('2026-11-02', '2026-11-27', 'nov/2026')]
_, rA = st(ALL * W); _, rB = st(ON * W)
_, rS = st(ON * W, ff=FS['zero'])
rows = []
for a, b, nm in EP:
    def ret(r):
        e = r.equity; i0 = e.index.searchsorted(pd.Timestamp(a)) - 1; i1 = e.index.searchsorted(pd.Timestamp(b), side='right') - 1
        seg = e.iloc[max(i0, 0):i1 + 1]
        return seg.iloc[-1] / seg.iloc[0] - 1, (seg / seg.cummax() - 1).min()
    u = D.c.loc[a:b]; up = u.max() / D.c.iloc[max(D.index.searchsorted(pd.Timestamp(a)) - 1, 0)] - 1
    ra, da = ret(rA); rb, db = ret(rB)
    rows.append(dict(episodio=nm, inicio=a, fim=b, uvxy_pico=up, fixo_ret=ra, fixo_dd=da, ts_ret=rb, ts_dd=db))
    p(f'{nm:36s} UVXY pico {up*100:6.0f}% | short fixo {ra*100:6.1f}% (dd {da*100:6.1f}%) | VIX/VIX3M<1 {rb*100:6.1f}% (dd {db*100:6.1f}%)')
pd.DataFrame(rows).to_csv(os.path.join(OUT, 's04_episodios.csv'), index=False)

p('\n# 8. Hedge: short no S&P 500 (preco, sem funding) = h x beta(-4,4) x exposicao no UVXY')
spx = D.spx.values
for h in (0.0, 0.1, 0.25, 0.5):
    _, r = st(ON * W)
    # perna do hedge: vendido h*4.4*w_t do S&P, rebalanceado diariamente no fechamento (aprox.)
    rs = pd.Series(spx, index=D.index).pct_change().fillna(0).values
    wh = np.r_[0, (ON * W)[:-1]] * 4.4 * h
    hed = -wh * rs - np.abs(np.diff(np.r_[0, wh])) * 2e-4
    ru = r.equity.pct_change().fillna(0).values
    e = pd.Series(np.cumprod(1 + ru + hed), index=D.index)
    s = stats(pd.DataFrame({'equity': e, 'turn': 0, 'exp': ON}, index=D.index))
    p(f'hedge h={h:.2f}  {line(s)}')

open(os.path.join(OUT, 's04_robustez.txt'), 'w').write('\n'.join(log) + '\n')
