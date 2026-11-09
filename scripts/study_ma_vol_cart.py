"""Carteira dos 5 ativos (XAU, US100, WTI, BTC, ETH) com media longa + filtro de vol da CARTEIRA.

Cada ativo: +1 acima da MA, -1 abaixo (sempre posicionado), peso 1/5 (nocional bruto 1x).
Mesma MA para todos (SMA/EMA 75..400, em barras do TF). Vol da carteira = desvio dos retornos
diarios da carteira (posicao cheia) nos ultimos 20 dias, anualizado, medido ate o dia anterior.
Se passar de X, todas as posicoes viram metade. X absoluto (8/10/12/15/20% a.a.) ou percentil
movel de ~1 ano (70/80/90). Execucao na abertura da barra seguinte, spread Lighter por mudanca de
posicao, funding pro-rata. Periodo comum dos 5 ativos, split 60/20/20, escolha pelo Sharpe do treino.
"""
import itertools, numpy as np, pandas as pd
from tvlib import load_m1v, resample
from study_engulf_psar import CUSTO, FUND

AT = ['xau', 'us100', 'wti', 'btc', 'eth']
MAS = [75, 100, 150, 200, 250, 300, 400]
FILT = [('nenhum', None)] + [('abs', x) for x in (0.08, 0.10, 0.12, 0.15, 0.20)] + [('pct', x) for x in (0.7, 0.8, 0.9)]
YR = 365 * 86400


def sharpe(s):
    d = s.resample('1D').sum()
    d = d[d.index.dayofweek < 5] if False else d
    return float(d.mean() / d.std() * np.sqrt(252)) if d.std() > 0 else np.nan


def stats(r, w):
    yrs = (r.index[-1] - r.index[0]).total_seconds() / YR
    eq = r.cumsum()
    return dict(sh=sharpe(r), cagr=float(np.expm1(eq.iloc[-1] / yrs)) * 100,
                dd=float((eq - eq.cummax()).min()) * 100, escala=float(w.mean()))


def prep(tf, m1s):
    bars = {a: resample(m1s[a], tf) for a in AT}
    t0 = max(b.index[0] for b in bars.values()); t1 = min(b.index[-1] for b in bars.values())
    idx = pd.DatetimeIndex(sorted(set().union(*[b.index for b in bars.values()])))
    idx = idx[(idx >= t0 - pd.Timedelta(days=500)) & (idx <= t1)]
    dt = pd.Series(np.append(np.diff(idx.values).astype('timedelta64[s]').astype(float) / YR, 0.0), idx)
    return bars, idx, dt, t0, t1


def run():
    m1s = {a: load_m1v(a) for a in AT}
    rows = []
    for tf in ('4h', '1D'):
        bars, idx, dt, t0, t1 = prep(tf, m1s)
        c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
        per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
        ro = {}
        for a, b in bars.items():
            o = b.open
            ro[a] = np.log(o.shift(-1) / o).fillna(0.0).reindex(idx).fillna(0.0)
        # benchmark: carteira so comprada, pesos iguais, com funding
        bh = sum((ro[a] - FUND[a] / 100 * dt * (ro[a] != 0)) / 5 for a in AT)
        bhs = {p: sharpe(bh[(bh.index >= x) & (bh.index < y)]) for p, (x, y) in per.items()}
        for tipo, n in itertools.product(('SMA', 'EMA'), MAS):
            pos, rr, cst, fnd = {}, {}, {}, {}
            for a, b in bars.items():
                c = b.close
                ma = c.rolling(n).mean() if tipo == 'SMA' else c.ewm(span=n, adjust=False).mean()
                sig = np.sign(c - ma).where(ma.notna(), 0.0)
                p = sig.shift(1).fillna(0.0).reindex(idx).ffill().fillna(0.0) / 5   # posicao vigente na barra
                pos[a] = p
            base = sum(pos[a] * ro[a] for a in AT)
            dly = base.resample('1D').sum()
            vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1)
            pct = vol.rolling(252, min_periods=126).rank(pct=True)
            for kind, x in FILT:
                if kind == 'nenhum': wd = pd.Series(1.0, dly.index)
                elif kind == 'abs': wd = pd.Series(np.where(vol > x, 0.5, 1.0), dly.index)
                else: wd = pd.Series(np.where(pct > x, 0.5, 1.0), dly.index)
                w = wd.reindex(idx.normalize()).to_numpy(); w = pd.Series(np.nan_to_num(w, nan=1.0), idx)
                r_sf = 0.0; fund = 0.0
                for a in AT:
                    q = pos[a] * w
                    r_sf = r_sf + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a]
                    fund = fund + q * FUND[a] / 100 * dt * (ro[a] != 0)
                r = r_sf - fund
                row = dict(tf=tf, ma=f'{tipo}{n}', filtro=kind, x=x)
                for pnm, (xa, xb) in per.items():
                    m = (idx >= xa) & (idx < xb)
                    s, s0 = stats(r[m], w[m]), stats(r_sf[m], w[m])
                    row.update({f'{pnm}_sh': round(s['sh'], 2), f'{pnm}_cagr': round(s['cagr'], 1),
                                f'{pnm}_dd': round(s['dd'], 1), f'{pnm}_sh_sf': round(s0['sh'], 2),
                                f'{pnm}_escala': round(s['escala'], 2), f'bh_{pnm}': round(bhs[pnm], 2)})
                rows.append(row)
        print(tf, {p: (x.date(), y.date()) for p, (x, y) in per.items()}, flush=True)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    g = run()
    g.to_csv('../results/ma_vol_cart_grade.csv', index=False)
    pd.set_option('display.width', 250)
    print(g.sort_values('treino_sh', ascending=False).head(15).to_string(index=False))
    print(g.groupby(['filtro', 'x'], dropna=False)[['treino_sh', 'valid_sh', 'teste_sh']].median().round(2))
