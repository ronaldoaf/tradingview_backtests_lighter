"""Vendido no UVXY e no SPY ao mesmo tempo.

Perna UVXY: a regra do estudo (25% do patrimonio vendido quando VIX/VIX3M<1, exec 16:20 ET, 10 bp/perna,
funding modelo). Perna SPY: vendida com nocional w_spy decidido no fechamento t, rebalanceio diario,
custo por perna (2 bp = Lighter; 5 bp = SPX500 na AlphaX) e funding recebido pelo vendido
(0; 3,6%/ano = SPY na Lighter; 8%/ano = SPY/SPX500 na AlphaX, jun-nov/2026).

Modos da perna SPY:
  junto   w_spy = h * beta * w_uvxy   (so quando vendido no UVXY; hedge de beta)
  sempre  w_spy = h * beta * 0,25     (tambem quando o UVXY esta zerado)
  fora    w_spy = h * beta * 0,25 so quando o UVXY esta zerado (aposta de crise, sem hedge)
beta: fixo 4,4 (beta diario do UVXY ao S&P, 2018-2026) ou movel de 60/120 pregoes (causal, limitado a [1, 8]).
Comparacao no mesmo tamanho de UVXY (0,25) e com a mesma vol anual da regra sozinha."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from core import load, sim, stats, fund_model, DD
import signals as sg

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'uvxy_short')
D0 = load()
spy = pd.read_parquet(os.path.join(DD, 'daily_spy.parquet')).close
D0['spyc'] = spy.reindex(D0.index)
D = D0.loc['2011-10-04':]; D = D[D.c.notna() & D.ts.notna() & D.spyc.notna()]
S = D0.loc['2006-07-18':]; S = S[S.syn.notna() & S.ts.notna() & S.spyc.notna()]
fR = fund_model(D.ts.values); fS = fund_model(S.ts.values)
W0 = 0.25
iIS = int((D.index <= '2018-12-31').sum())


def uvxy_leg(X, px, ff, ex, on, w):
    res, ns, lq = sim(X, on * w, px=px, exec=ex, fund=ff, band=0.25)
    return res.equity.pct_change().fillna(0).values, res.exp.values


def beta_series(X, px, kind):
    if kind == 'fixo':
        return np.full(len(X), 4.4)
    n = int(kind[3:])
    ru = X[px].pct_change(); rs = X.spyc.pct_change()
    b = (ru.rolling(n, min_periods=n).cov(rs) / rs.rolling(n, min_periods=n).var()).abs()
    return b.clip(1, 8).fillna(4.4).values


def spy_leg(X, wspy, cost, fund):
    """retorno diario da perna vendida: w decidido em t-1 aplicado ao retorno de t."""
    rs = X.spyc.pct_change().fillna(0).values
    wp = np.r_[0, wspy[:-1]]
    tr = np.abs(np.diff(np.r_[0, wspy]))
    return -wp * rs + wp * fund / 252 - tr * cost


def combine(ru, rsp, idx):
    r = pd.Series(ru + rsp, index=idx)
    e = (1 + r).cumprod()
    return r, e


def met(r, e, spyr):
    yrs = (e.index[-1] - e.index[0]).days / 365.25
    cagr = e.iloc[-1] ** (1 / yrs) - 1 if e.iloc[-1] > 0 else -1
    sh = r.mean() / r.std() * np.sqrt(252)
    mdd = (e / e.cummax() - 1).min()
    xw = (1 + r).resample('W').prod() - 1; yw = (1 + spyr).resample('W').prod() - 1
    be, al = np.polyfit(yw, xw, 1); res = xw - (al + be * yw)
    t = al / (res.std() / np.sqrt(len(xw)))
    return dict(cagr=cagr, sh=sh, mdd=mdd, vol=r.std() * np.sqrt(252), worst=r.min(), beta=be, alfa=al * 52, t=t,
                corr=np.corrcoef(xw, yw)[0, 1])


def build(X, px, ff, ex, filt, mode, bk, h, cost, fund, wu=W0):
    on = sg.ts(X, 1.0).fillna(0).values if filt == 'ts<1' else np.ones(len(X))
    ru, expo = uvxy_leg(X, px, ff, ex, on, wu)
    b = beta_series(X, px, bk)
    if mode == 'junto':
        ws = h * b * on * wu
    elif mode == 'sempre':
        ws = h * b * wu * np.ones(len(X))
    else:
        ws = h * b * wu * (1 - on)
    return combine(ru, spy_leg(X, ws, cost, fund), X.index), ws


spyR = D.spyc.pct_change().fillna(0); spyS = S.spyc.pct_change().fillna(0)
rows = []

if __name__ == '__main__':
    GRID = list(itertools.product(['ts<1', 'sem filtro'], ['junto', 'sempre', 'fora'], ['fixo', 'rol60', 'rol120'],
                                  [0.0, 0.25, 0.5, 0.75, 1.0, 1.25], [0.0, 0.036, 0.08]))
    for filt, mode, bk, h, fund in GRID:
        if h == 0 and (mode != 'junto' or bk != 'fixo' or fund != 0):
            continue
        if filt == 'sem filtro' and mode == 'fora':
            continue
        (r, e), ws = build(D, 'c', fR, 'pm', filt, mode, bk, h, 2e-4, fund)
        a = met(r, e, spyR)
        i = met(*combine(r.values[:iIS], np.zeros(iIS), D.index[:iIS]), spyR.iloc[:iIS])
        o = met(*combine(r.values[iIS:], np.zeros(len(D) - iIS), D.index[iIS:]), spyR.iloc[iIS:])
        (rS, eS), _ = build(S, 'syn', fS, 'close', filt, mode, bk, h, 2e-4, fund)
        s = met(rS, eS, spyS)
        rows.append(dict(filtro=filt, modo=mode, beta_spy=bk, h=h, fund_spy=fund, spy_medio=ws[ws > 0].mean() if (ws > 0).any() else 0,
                         **{k: a[k] for k in ('cagr', 'sh', 'mdd', 'vol', 'worst', 'beta', 'alfa', 't', 'corr')},
                         IS_sh=i['sh'], OOS_sh=o['sh'], OOS_cagr=o['cagr'], OOS_mdd=o['mdd'],
                         SIN_sh=s['sh'], SIN_cagr=s['cagr'], SIN_mdd=s['mdd'], SIN_beta=s['beta']))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, 's13_uvxy_spy.csv'), index=False)

    log = []
    def p(s=''):
        print(s); log.append(s)


    def tab(P, title):
        p(f'\n# {title}')
        p('| filtro | modo | beta | h | funding SPY | SPY medio | CAGR | Queda | Sharpe | Pior dia | beta S&P | alfa | t | Sh IS | Sh OOS | Queda OOS | Sh sint. | Queda sint. | CAGR sint. |')
        p('| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
        for _, x in P.iterrows():
            p(f'| {x.filtro} | {x.modo} | {x.beta_spy} | {x.h:g} | {x.fund_spy*100:.1f}% | {x.spy_medio:.2f} | {x.cagr*100:.1f}% | {x.mdd*100:.1f}% | '
              f'{x.sh:.2f} | {x.worst*100:.1f}% | {x.beta:.2f} | {x.alfa*100:.1f}% | {x.t:.2f} | {x.IS_sh:.2f} | {x.OOS_sh:.2f} | '
              f'{x.OOS_mdd*100:.1f}% | {x.SIN_sh:.2f} | {x.SIN_mdd*100:.1f}% | {x.SIN_cagr*100:.1f}% |')


    base = R[(R.filtro == 'ts<1') & (R.h == 0)]
    tab(base, 'Base: so UVXY (25%, VIX/VIX3M<1)')
    P = R[(R.filtro == 'ts<1') & (R.modo == 'junto') & (R.beta_spy == 'fixo')].sort_values(['fund_spy', 'h'])
    tab(P, 'Hedge junto, beta fixo 4,4, por proporcao h e funding do SPY')
    P = R[(R.filtro == 'ts<1') & (R.h == 1.0) & (R.fund_spy == 0.036)].sort_values(['modo', 'beta_spy'])
    tab(P, 'h = 1, funding 3,6% (Lighter): modos e betas')
    P = R[(R.filtro == 'sem filtro') & (R.modo == 'junto') & (R.beta_spy == 'fixo') & (R.fund_spy == 0.036)].sort_values('h')
    tab(P, 'Sem filtro (UVXY sempre vendido) + SPY junto, beta fixo, funding 3,6%')
    P = R[(R.filtro == 'ts<1') & (R.modo == 'fora') & (R.beta_spy == 'fixo') & (R.fund_spy == 0.0)].sort_values('h')
    tab(P, 'Vendido em SPY so quando o UVXY esta zerado (backwardation), sem funding')

    # mesma vol da base: escala a combinacao (UVXY e SPY juntos)
    p('\n# Mesma vol anual da base (escala k sobre as duas pernas; w_uvxy = 0,25k)')
    p('| h | funding SPY | k | UVXY | SPY medio | CAGR | Queda | Sharpe | Pior dia | Sh OOS | Queda OOS | Sh sint. | Queda sint. | CAGR sint. |')
    p('| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    volR = base.vol.iloc[0]
    (r0, e0), _ = build(S, 'syn', fS, 'close', 'ts<1', 'junto', 'fixo', 0.0, 2e-4, 0.0)
    volS = r0.std() * np.sqrt(252)
    for h in (0.0, 0.5, 1.0):
        for fund in (0.0, 0.036, 0.08):
            if h == 0 and fund > 0:
                continue
            out = []
            for X, px, ff, ex, tv in ((D, 'c', fR, 'pm', volR), (S, 'syn', fS, 'close', volS)):
                lo, hi = 0.2, 4.0
                for _ in range(20):
                    k = (lo + hi) / 2
                    (r, e), ws = build(X, px, ff, ex, 'ts<1', 'junto', 'fixo', h, 2e-4, fund, wu=W0 * k)
                    v = r.std() * np.sqrt(252)
                    lo, hi = (k, hi) if v < tv else (lo, k)
                (r, e), ws = build(X, px, ff, ex, 'ts<1', 'junto', 'fixo', h, 2e-4, fund, wu=W0 * lo)
                out.append((lo, r, e, ws))
            (k, r, e, ws), (kS, rS, eS, _) = out
            a = met(r, e, spyR); o = met(*combine(r.values[iIS:], np.zeros(len(D) - iIS), D.index[iIS:]), spyR.iloc[iIS:])
            s = met(rS, eS, spyS)
            p(f'| {h:g} | {fund*100:.1f}% | {k:.2f} | {W0*k:.2f} | {ws[ws>0].mean() if (ws>0).any() else 0:.2f} | {a["cagr"]*100:.1f}% | {a["mdd"]*100:.1f}% | '
              f'{a["sh"]:.2f} | {a["worst"]*100:.1f}% | {o["sh"]:.2f} | {o["mdd"]*100:.1f}% | {s["sh"]:.2f} | {s["mdd"]*100:.1f}% | {s["cagr"]*100:.1f}% |')
    open(os.path.join(OUT, 's13_uvxy_spy.txt'), 'w').write('\n'.join(log) + '\n')
