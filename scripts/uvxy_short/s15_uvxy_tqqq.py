"""Vendido no UVXY e no TQQQ ao mesmo tempo (o TQQQ no lugar do SPY do s13).

Perna UVXY: a regra (25% vendido quando VIX/VIX3M<1, exec 16:20 ET, 10 bp/perna, funding modelo).
Perna TQQQ: perp da AlphaX vendido com nocional w_t = h * 4,4 * w_uvxy / 3,4. E o mesmo hedge de beta
ao S&P que o SPY do s13 com o mesmo h (4,4 = beta diario do UVXY; 3,4 = beta diario do TQQQ, 2011-2026),
com ~1/3,4 do nocional. Execucao no fechamento, 10 bp/perna.
Rebalanceio do TQQQ: diario (como o SPY do s13) ou banda de 25% (o vendido encolhe quando o TQQQ cai e
cresce quando sobe, como a perna UVXY; colhe parte do decaimento por volatilidade).
Funding recebido pelo vendido em TQQQ: 0, 7%/ano e 14,1%/ano (media AlphaX jul-nov/2026).
TQQQ sintetico (todo o periodo 2006-2026 do UVXY sintetico): 3 x QQQ + (0,8% - 2,74 x T-bill)/252 ao dia,
calibrado em 2010-2026 (correlacao diaria 0,999; CAGR 37,4% contra 38,2% do real).
Modos: junto (so quando vendido no UVXY), sempre, fora (so com o UVXY zerado).
Decomposicao: QQQ vendido (perp AlphaX, funding 13,2%/ano) com o mesmo hedge de beta (beta QQQ~SPY 1,15),
rebalanceio diario, separa o efeito Nasdaq contra S&P do efeito alavancagem 3x."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import sim, DD, yearly
from s13_uvxy_spy import D0, D, S, fR, fS, W0, iIS, uvxy_leg, spy_leg, combine, met, spyR, spyS, OUT
import signals as sg

BU, BT, BQ = 4.4, 3.4, 1.15
COSTT = 10e-4
tq = pd.read_parquet(os.path.join(DD, 'daily_tqqq.parquet')).close
irx = pd.read_parquet(os.path.join(DD, 'daily_irx.parquet')).close
rf = (irx.reindex(D0.index).ffill() / 100 / 252).shift(1).fillna(0)
rq = D0.qqq.pct_change().fillna(0)
tqs = (1 + 3 * rq + (0.008 / 252 - 2.74 * rf)).cumprod()
D = D.assign(tq=tq.reindex(D.index)); D = D[D.tq.notna()]
S = S.assign(tq=tqs.reindex(S.index))
fR = fR[-len(D):] if len(fR) != len(D) else fR
iIS = int((D.index <= '2018-12-31').sum())
spyR = D.spyc.pct_change().fillna(0); spyS = S.spyc.pct_change().fillna(0)


def tq_leg(X, w, fund, band, cost=COSTT):
    res, ns, lq = sim(X, w, px='tq', exec='close', fund=np.full(len(X), fund / 252), cost=cost, band=band)
    return res.equity.pct_change().fillna(0).values


def build(X, px, ff, ex, mode, h, fund, band, wu=W0, hedge='TQQQ', cost=COSTT):
    on = sg.ts(X, 1.0).fillna(0).values
    ru, _ = uvxy_leg(X, px, ff, ex, on, wu)
    base = h * BU * wu
    sel = {'junto': on, 'sempre': np.ones(len(X)), 'fora': 1 - on}[mode]
    if hedge == 'SPY':
        ws = base * sel
        return combine(ru, spy_leg(X, ws, 2e-4, fund), X.index), ws
    if hedge == 'QQQ':
        wq = base / BQ * sel
        rq_ = X.qqq.pct_change().fillna(0).values; wp = np.r_[0, wq[:-1]]
        return combine(ru, -wp * rq_ + wp * fund / 252 - np.abs(np.diff(np.r_[0, wq])) * cost, X.index), wq
    wt = base / BT * sel
    return combine(ru, tq_leg(X, wt, fund, band, cost), X.index), wt


def row(mode, h, fund, band, hedge='TQQQ', cost=COSTT):
    (r, e), w = build(D, 'c', fR, 'pm', mode, h, fund, band, hedge=hedge, cost=cost)
    a = met(r, e, spyR)
    i = met(*combine(r.values[:iIS], np.zeros(iIS), D.index[:iIS]), spyR.iloc[:iIS])
    o = met(*combine(r.values[iIS:], np.zeros(len(D) - iIS), D.index[iIS:]), spyR.iloc[iIS:])
    (rS, eS), _ = build(S, 'syn', fS, 'close', mode, h, fund, band, hedge=hedge, cost=cost)
    s = met(rS, eS, spyS)
    return dict(hedge=hedge, rebal='diario' if band == 0 else f'banda {band:g}', modo=mode, h=h, fund=fund,
                w_hedge=w[w > 0].mean() if (w > 0).any() else 0,
                **{k: a[k] for k in ('cagr', 'sh', 'mdd', 'vol', 'worst', 'beta', 'alfa', 't')},
                IS_sh=i['sh'], OOS_sh=o['sh'], OOS_cagr=o['cagr'], OOS_mdd=o['mdd'],
                SIN_sh=s['sh'], SIN_cagr=s['cagr'], SIN_mdd=s['mdd']), r, rS


if __name__ == '__main__':
    log = []
    def p(s=''):
        print(s); log.append(s)

    t = tq.reindex(D.index).pct_change(); sp = D.spyc.pct_change()
    p(f'Periodo real {D.index[0].date()}..{D.index[-1].date()}; beta diario TQQQ~SPY {t.cov(sp)/sp.var():.2f}')
    rows = []; RET = {}
    base, r0, rS0 = row('junto', 0.0, 0.0, 0.0)
    base.update(hedge='nenhum'); rows.append(base); RET['so UVXY'] = (r0, rS0)
    for fund in (0.036, 0.08):
        for h in (0.5, 1.0):
            x, r, rS = row('junto', h, fund, 0.0, hedge='SPY'); x['rebal'] = 'diario'; rows.append(x)
            RET[f'SPY h={h:g} f={fund*100:.1f}%'] = (r, rS)
    for fund in (0.0, 0.132):
        for h in (0.5, 1.0):
            x, r, rS = row('junto', h, fund, 0.0, hedge='QQQ'); x['rebal'] = 'diario'; rows.append(x)
    for band, mode, h, fund in itertools.product((0.0, 0.25), ('junto', 'sempre', 'fora'),
                                                 (0.25, 0.5, 0.75, 1.0, 1.25), (0.0, 0.07, 0.141)):
        x, r, rS = row(mode, h, fund, band); rows.append(x)
        RET[f'TQQQ {x["rebal"]} {mode} h={h:g} f={fund*100:.1f}%'] = (r, rS)
    for c in (5e-4, 20e-4):
        x, r, rS = row('junto', 0.5, 0.141, 0.25, cost=c); x['rebal'] += f' custo {c*1e4:.0f}bp'; rows.append(x)
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, 's15_uvxy_tqqq.csv'), index=False)

    def tab(P, title):
        p(f'\n# {title}')
        p('| hedge | rebal. | modo | h | funding | nocional hedge | CAGR | Queda | Sharpe | Pior dia | beta S&P | alfa | t | Sh IS | Sh OOS | Queda OOS | Sh sint. | Queda sint. | CAGR sint. |')
        p('| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
        for _, x in P.iterrows():
            p(f'| {x.hedge} | {x.rebal} | {x.modo} | {x.h:g} | {x.fund*100:.1f}% | {x.w_hedge:.2f} | {x.cagr*100:.1f}% | {x.mdd*100:.1f}% | '
              f'{x.sh:.2f} | {x.worst*100:.1f}% | {x.beta:.2f} | {x.alfa*100:.1f}% | {x.t:.2f} | {x.IS_sh:.2f} | {x.OOS_sh:.2f} | '
              f'{x.OOS_mdd*100:.1f}% | {x.SIN_sh:.2f} | {x.SIN_mdd*100:.1f}% | {x.SIN_cagr*100:.1f}% |')

    tab(R[R.hedge.isin(['nenhum', 'SPY', 'QQQ'])], 'Referencia: so UVXY, UVXY + SPY (s13) e UVXY + QQQ')
    for band in ('diario', 'banda 0.25'):
        tab(R[(R.hedge == 'TQQQ') & (R.rebal == band) & (R.modo == 'junto')].sort_values(['fund', 'h']),
            f'UVXY + TQQQ junto, rebalanceio {band}')
    tab(R[(R.hedge == 'TQQQ') & (R.modo != 'junto') & (R.h.isin([0.5, 1.0]))].sort_values(['rebal', 'modo', 'fund', 'h']),
        'Modos sempre e fora (h = 0,5 e 1)')
    tab(R[R.rebal.str.contains('custo')], 'Custo da perna TQQQ (junto, banda 0,25, h = 0,5, funding 14,1%)')

    # mesma vol da base
    p('\n# Mesma vol anual da base (escala k sobre as duas pernas)')
    p('| hedge | h | funding | k | UVXY | hedge | CAGR | Queda | Sharpe | Pior dia | Sh OOS | Queda OOS | Sh sint. | Queda sint. |')
    p('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    volR = r0.std() * np.sqrt(252); volS = rS0.std() * np.sqrt(252)
    for hedge, h, fund, band in (('TQQQ', 0.5, 0.0, 0.25), ('TQQQ', 0.5, 0.141, 0.25), ('TQQQ', 1.0, 0.141, 0.25),
                                 ('SPY', 0.5, 0.036, 0.0), ('SPY', 0.5, 0.08, 0.0)):
        out = []
        for X, px, ff, ex, tv in ((D, 'c', fR, 'pm', volR), (S, 'syn', fS, 'close', volS)):
            lo, hi = 0.2, 4.0
            for _ in range(20):
                k = (lo + hi) / 2
                (r, e), w = build(X, px, ff, ex, 'junto', h, fund, band, wu=W0 * k, hedge=hedge)
                lo, hi = (k, hi) if r.std() * np.sqrt(252) < tv else (lo, k)
            (r, e), w = build(X, px, ff, ex, 'junto', h, fund, band, wu=W0 * lo, hedge=hedge)
            out.append((lo, r, e, w))
        (k, r, e, w), (kS, rS, eS, _) = out
        a = met(r, e, spyR); o = met(*combine(r.values[iIS:], np.zeros(len(D) - iIS), D.index[iIS:]), spyR.iloc[iIS:])
        s = met(rS, eS, spyS)
        p(f'| {hedge} | {h:g} | {fund*100:.1f}% | {k:.2f} | {W0*k:.2f} | {w[w>0].mean():.2f} | {a["cagr"]*100:.1f}% | {a["mdd"]*100:.1f}% | '
          f'{a["sh"]:.2f} | {a["worst"]*100:.1f}% | {o["sh"]:.2f} | {o["mdd"]*100:.1f}% | {s["sh"]:.2f} | {s["mdd"]*100:.1f}% |')

    # detalhe
    V = {'so UVXY': RET['so UVXY'], 'SPY h=0,5 3,6%': RET['SPY h=0.5 f=3.6%'],
         'TQQQ h=0,5 0%': RET['TQQQ banda 0.25 junto h=0.5 f=0.0%'],
         'TQQQ h=0,5 14,1%': RET['TQQQ banda 0.25 junto h=0.5 f=14.1%'],
         'TQQQ h=1 14,1%': RET['TQQQ banda 0.25 junto h=1 f=14.1%']}
    qq = D0.qqq.pct_change()
    p('\n# Ano a ano (2007-2010 do sintetico), TQQQ com banda 0,25')
    p('| Ano | ' + ' | '.join(V) + ' | QQQ |'); p('| ---: |' + ' ---: |' * (len(V) + 1))
    Y = {}
    for nm, (r, rS) in V.items():
        yS = (1 + rS).groupby(rS.index.year).prod() - 1; yR = (1 + r).groupby(r.index.year).prod() - 1
        Y[nm] = pd.concat([yS.loc[2007:2010], yR.loc[2012:]])
    Y = pd.DataFrame(Y); Y['QQQ'] = ((1 + qq).groupby(qq.index.year).prod() - 1).reindex(Y.index)
    for yv, rr in Y.iterrows():
        p(f'| {yv} | ' + ' | '.join(f'{v*100:+.1f}%' for v in rr.values) + ' |')

    EP = [('2015-08-17', '2015-09-30', 'ago/2015'), ('2015-12-01', '2016-02-29', 'dez/15-fev/16'),
          ('2018-01-26', '2018-02-28', 'fev/2018'), ('2018-10-01', '2018-12-31', 'T4 2018'), ('2020-02-19', '2020-04-30', 'Covid'),
          ('2020-06-01', '2020-06-30', 'jun/2020'), ('2022-01-01', '2022-10-31', 'bear 2022'), ('2024-07-15', '2024-08-30', 'ago/2024'),
          ('2025-03-26', '2025-04-30', 'abr/2025'), ('2026-11-02', '2026-11-27', 'nov/2026'),
          ('2008-09-01', '2008-12-31', 'set-dez/2008 (sint.)'), ('2010-04-20', '2010-07-02', 'flash crash 2010 (sint.)'),
          ('2011-07-20', '2011-09-30', 'ago/2011 (sint.)')]
    p('\n# Picos (retorno na janela; queda dentro dela)')
    p('| Episodio | ' + ' | '.join(V) + ' |'); p('| --- |' + ' ---: |' * len(V))
    for a_, b_, nm in EP:
        cells = []
        for k, (r, rS) in V.items():
            x = rS if 'sint' in nm else r
            e = (1 + x).cumprod(); seg = e.loc[a_:b_]
            i0 = e.index.searchsorted(seg.index[0]) - 1
            seg = pd.concat([e.iloc[[max(i0, 0)]], seg])
            cells.append(f'{(seg.iloc[-1]/seg.iloc[0]-1)*100:+.1f}% ({(seg/seg.cummax()-1).min()*100:.0f}%)')
        p(f'| {nm} | ' + ' | '.join(cells) + ' |')

    p('\n# Os 8 piores dias da regra so no UVXY e o mesmo dia nas variantes')
    p('| Dia | ' + ' | '.join(V) + ' |'); p('| --- |' + ' ---: |' * len(V))
    for d in V['so UVXY'][0].nsmallest(8).index:
        p(f'| {d.date()} | ' + ' | '.join(f'{V[k][0].loc[d]*100:.1f}%' for k in V) + ' |')
    p('\nPiores dias de cada variante:')
    for k, (r, rS) in V.items():
        p(f'{k:18s} ' + '  '.join(f'{d.date()} {v*100:.1f}%' for d, v in r.nsmallest(4).items()))

    p('\n# Queda em 5 anos, bootstrap em blocos de 60 pregoes (4.000 trajetorias)')
    rng = np.random.default_rng(7); B = 60; H = 252 * 5
    for k, (r, rS) in V.items():
        for lab, x in (('real', r.values[1:]), ('sint', rS.values[1:])):
            n = len(x); md = []; cg = []
            for _ in range(4000):
                st = rng.integers(0, n - B, size=H // B + 1)
                y = np.concatenate([x[s0:s0 + B] for s0 in st])[:H]; e = np.cumprod(1 + y)
                md.append((e / np.maximum.accumulate(e) - 1).min()); cg.append(e[-1] ** 0.2 - 1)
            md = np.array(md); cg = np.array(cg)
            p(f'{k:18s} {lab}: CAGR mediano {np.median(cg)*100:5.1f}%  P(CAGR<0) {np.mean(cg<0)*100:4.1f}%  queda mediana {np.median(md)*100:6.1f}%  '
              f'pior 10% {np.percentile(md,10)*100:6.1f}%  P(queda>40%) {np.mean(md<-0.4)*100:4.1f}%')
    open(os.path.join(OUT, 's15_uvxy_tqqq.txt'), 'w').write('\n'.join(log) + '\n')
