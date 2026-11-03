"""ORB 30m (opening range de NY): range = barra 9:30-10:00 ET; se a barra 10:00-10:30 FECHAR acima
da maxima -> long, abaixo da minima -> short; entra no fechamento (10:30 ET) e sai as 15:00 ET.
Mesma janela de NY para todos os ativos (America/New_York, com horario de verao). Custo Lighter
(2 pernas) + funding pro-rata. Controle: mesmos dias, lado aleatorio (2000 sorteios)."""
import sys, numpy as np, pandas as pd
from tvlib import load_m1v, CUSTO, FUND

def run(name):
    m = load_m1v(name)
    m.index = m.index.tz_convert('America/New_York')
    day = m.index.normalize(); hm = m.index.hour * 60 + m.index.minute
    def pick(a, b):  # minutos [a,b)
        s = m[(hm >= a) & (hm < b)]; g = s.groupby(s.index.normalize())
        return g.agg(open=('open', 'first'), high=('high', 'max'), low=('low', 'min'), close=('close', 'last'), n=('open', 'size'))
    b1, b2 = pick(570, 600), pick(600, 630)
    ex = m[(hm >= 900) & (hm < 905)].groupby(lambda t: t.normalize())['open'].first()
    d = b1.join(b2, rsuffix='2').join(ex.rename('exit')).dropna()
    d = d[(d.n >= 20) & (d.n2 >= 20) & (d.index.dayofweek < 5)]
    d['side'] = np.where(d.close2 > d.high, 1, np.where(d.close2 < d.low, -1, 0))
    d['raw'] = np.log(d.exit / d.close2)  # log-retorno 10:30 -> 15:00
    fund = FUND[name] / 100 * 4.5 / (24 * 365)
    t = d[d.side != 0].copy()
    t['ret'] = t.side * t.raw - 2 * CUSTO[name] - t.side * fund
    out = []
    n = len(t); cuts = [t.index[0], t.index[n // 3], t.index[2 * n // 3], t.index[-1] + pd.Timedelta('1D')]
    for lab, a, b in [('ALL', cuts[0], cuts[3]), ('T1', cuts[0], cuts[1]), ('T2', cuts[1], cuts[2]), ('T3', cuts[2], cuts[3])]:
        s = t[(t.index >= a) & (t.index < b)]
        rng = np.random.default_rng(1); sides = rng.choice([-1, 1], size=(2000, len(s)))
        ctl = (sides * s.raw.values - 2 * CUSTO[name] - sides * fund).sum(1)
        yrs = (b - a).days / 365.25
        out.append(dict(ativo=name, per=lab, ini=a.date(), n=len(s), longs=int((s.side > 0).sum()),
                        hit=round((s.ret > 0).mean(), 3), tot_pct=round(s.ret.sum() * 100, 1),
                        anual_pct=round(s.ret.sum() * 100 / yrs, 1),
                        sharpe=round(s.ret.mean() / s.ret.std() * np.sqrt(len(s) / yrs), 2),
                        dd_pct=round((s.ret.cumsum() - s.ret.cumsum().cummax()).min() * 100, 1),
                        p_ctl=round((ctl >= s.ret.sum()).mean(), 3),
                        L_tot=round(s.ret[s.side > 0].sum() * 100, 1), S_tot=round(s.ret[s.side < 0].sum() * 100, 1)))
    t.to_csv(f'../results/orb30_{name}_trades.csv')
    return out

if __name__ == '__main__':
    rows = sum((run(a) for a in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])), [])
    r = pd.DataFrame(rows); print(r.to_string(index=False)); r.to_csv('../results/orb30_resumo.csv', index=False)
