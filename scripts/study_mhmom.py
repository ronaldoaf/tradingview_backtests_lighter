"""Momentum multi-horizonte com vol targeting (paper de hedge fund, via Unbiased Trading).
Sinal no fechamento diario: S = soma sign(P_t - P_{t-n}), n em 5/10/21/42 (-4..+4).
Alvo w = S * risco_alvo / vol_diaria(N). Rebalanceia so se |dw/w_atual| > 5%. Ordem na abertura seguinte.
Custo |dw|*CUSTO por perna + funding pro-rata (long paga, short recebe). Periodo em 10 partes: 1-6 treino, 7-9 validacao, 10 OOS."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from tvlib import load_m1v, resample, CUSTO, FUND

ATIVOS = ['xau', 'us100', 'wti', 'btc', 'eth']

def run(d, name, risco=0.01, nvol=20, tol=0.05, cap=None, wins=(5, 10, 21, 42), sma=0):
    c = d.close.values; o = d.open.values; n = len(c)
    S = sum(np.sign(c - pd.Series(c).shift(k).values) for k in wins)
    lr = np.log(d.close).diff()
    vol = lr.rolling(nvol).std().values
    tgt = np.nan_to_num(S * risco / vol)
    if cap: tgt = np.clip(tgt, -cap, cap)
    if sma:  # compra so acima da SMA, venda so abaixo
        m = d.close.rolling(sma).mean().values
        tgt = np.where(np.isnan(m), 0.0, np.where(tgt > 0, tgt * (c > m), tgt * (c < m)))
    w = np.zeros(n); cur = 0.0  # w[i] = posicao decidida no fechamento de i, executada na abertura de i+1
    for i in range(n):
        t = tgt[i]
        if cur == 0.0 or t == 0.0 or abs((t - cur) / cur) > tol:
            cur = t
        w[i] = cur
    # retorno open->open: posicao w[i-1] mantida de open[i] ate open[i+1]
    r_oo = np.r_[o[1:] / o[:-1] - 1, 0.0]
    pos = np.r_[0.0, w[:-1]]
    dt = np.r_[np.diff(d.index.values).astype('timedelta64[s]').astype(float), 0] / (365 * 86400)
    chg = np.abs(np.diff(np.r_[0.0, pos]))
    r = pos * r_oo - chg * CUSTO[name] - pos * FUND[name] / 100 * dt
    return pd.DataFrame({'r': r, 'pos': pos, 'chg': chg}, index=d.index)

def stats(x, bh):
    if len(x) < 2: return {}
    x = pd.DataFrame({'r': np.log1p(x.r.clip(lower=-0.99)).resample('1D').sum().pipe(np.expm1), 'pos': x.pos.abs().resample('1D').mean(), 'chg': x.chg.resample('1D').sum()}).dropna()
    bh = np.expm1(np.log1p(bh).resample('1D').sum()).reindex(x.index)
    x = x[x.pos.notna()]
    eq = np.cumprod(1 + x.r.clip(lower=-0.99)); yrs = (x.index[-1] - x.index[0]).days / 365
    beq = np.cumprod(1 + bh)
    s = lambda v: v.mean() / v.std() * np.sqrt(252) if v.std() else np.nan
    dd = lambda e: (e / np.maximum.accumulate(e) - 1).min()
    return dict(ret=eq.iloc[-1] - 1, cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=s(x.r), dd=dd(eq),
                lev=x.pos.abs().mean(), giro=x.chg.sum() / yrs,
                bh=beq.iloc[-1] - 1, bh_sharpe=s(bh), bh_dd=dd(beq))

def main(tf='1D'):
    rows = []; h = {'1h': 24, '4h': 6}.get(tf, 1)
    for a in ATIVOS:
        d = resample(load_m1v(a), tf)
        if a == 'wti':
            d = d[~((d.index >= '2020-04-01') & (d.index < '2020-05-01'))]
        bh = pd.Series(np.r_[d.open.values[1:] / d.open.values[:-1] - 1, 0.0], index=d.index)
        t0, t1 = d.index[0], d.index[-1]; edges = [t0 + (t1 - t0) * k / 10 for k in range(11)]
        per = {'treino': (edges[0], edges[6]), 'validacao': (edges[6], edges[9]), 'oos': (edges[9], edges[10]),
               'total': (edges[0], edges[10])}
        for var, kw in ([('spec (vol20)', {}), ('vol60', dict(nvol=60)), ('vol20 cap2x', dict(cap=2)),
                        ('risco 0.5%', dict(risco=0.005)), ('sem tol', dict(tol=0.0))] if h == 1 else
                       ([('1h barras 5/10/21/42 vol20', dict(risco=0.01/np.sqrt(24))),
                        ('1h janelas em dias (x24) vol480', dict(wins=(120, 240, 504, 1008), nvol=480, risco=0.01/np.sqrt(24))),
                        ('1h janelas em dias, rebal so com tol 25%', dict(wins=(120, 240, 504, 1008), nvol=480, risco=0.01/np.sqrt(24), tol=0.25))]
                        if h == 24 else
                        [(f'{tf} janelas em dias' + lab, dict(wins=tuple(k * h for k in (5, 10, 21, 42)), nvol=20 * h,
                                                             risco=0.01 / np.sqrt(h), sma=sm))
                         for lab, sm in [('', 0), (' + SMA200 4h', 200), (' + SMA200 diaria', 200 * h)]])):
            x = run(d, a, **kw)
            for p, (lo, hi) in per.items():
                m = (x.index >= lo) & (x.index <= hi)
                rows.append(dict(ativo=a, var=var, per=p, ini=lo.date(), fim=hi.date(), **stats(x[m], bh[m])))
    R = pd.DataFrame(rows)
    R.to_csv(f'results/mhmom_{tf}.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    print(R.round(3).to_string())

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '1D')
