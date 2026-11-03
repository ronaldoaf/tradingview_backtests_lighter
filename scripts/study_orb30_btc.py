"""Variacoes do ORB de NY no BTC. Grade: duracao do range (15/30/60m), saida (12:00..16:00 ET),
filtro de tamanho do range (largura/preco abaixo/acima da mediana movel de 60 dias, ou sem filtro), lado.
Selecao no TREINO (ate 2024-06-30); VALIDACAO = 2024-07-01 em diante (nao usada para escolher)."""
import sys, itertools, numpy as np, pandas as pd
from tvlib import load_m1v, CUSTO, FUND
name = sys.argv[1] if len(sys.argv) > 1 else 'btc'
m = load_m1v(name); m.index = m.index.tz_convert('America/New_York')
m = m[m.index.dayofweek < 5]
hm = m.index.hour * 60 + m.index.minute; dk = m.index.normalize()
def agg(a, b):
    s = m[(hm >= a) & (hm < b)]
    return s.groupby(s.index.normalize()).agg(high=('high', 'max'), low=('low', 'min'), close=('close', 'last'), n=('open', 'size'))
opn = m[hm % 60 == 0]; opn = opn.groupby([opn.index.normalize(), opn.index.hour])['open'].first().unstack()
CUT = pd.Timestamp('2024-07-01', tz='America/New_York')
fund = FUND[name] / 100 / (24 * 365)
rows = []
for L in (15, 30, 60):
    r1, r2 = agg(570, 570 + L), agg(570 + L, 570 + 2 * L)
    d = r1.join(r2, rsuffix='2').dropna(); d = d[(d.n >= L * .7) & (d.n2 >= L * .7)]
    d['side'] = np.where(d.close2 > d.high, 1, np.where(d.close2 < d.low, -1, 0))
    w = (d.high - d.low) / d.close2; d['wq'] = w / w.rolling(60, min_periods=20).median().shift(1)
    tin = (570 + 2 * L) / 60
    for X in (12, 13, 14, 15, 16):
        if X <= tin: continue
        ex = opn[X].reindex(d.index); raw = np.log(ex / d.close2)
        for filt, lado in itertools.product(('none', 'narrow', 'wide'), ('both', 'long', 'short')):
            s = d.side.copy()
            if filt == 'narrow': s[~(d.wq < 1)] = 0
            if filt == 'wide': s[~(d.wq >= 1)] = 0
            if lado == 'long': s[s < 0] = 0
            if lado == 'short': s[s > 0] = 0
            ret = (s * raw - (s != 0) * (2 * CUSTO[name] + s * fund * (X - tin)))[(s != 0) & raw.notna()]
            for per, msk in (('tr', ret.index < CUT), ('va', ret.index >= CUT)):
                r = ret[msk]; yrs = (5.5 if per == 'tr' else 2.25)
                rows.append(dict(L=L, X=X, filt=filt, lado=lado, per=per, n=len(r), anual=r.sum() * 100 / yrs,
                                 sharpe=r.mean() / r.std() * np.sqrt(len(r) / yrs) if len(r) > 5 else np.nan))
R = pd.DataFrame(rows).pivot_table(index=['L', 'X', 'filt', 'lado'], columns='per', values=['n', 'anual', 'sharpe'])
R.columns = [f'{a}_{b}' for a, b in R.columns]; R = R.round(2).sort_values('sharpe_tr', ascending=False)
R.to_csv(f'../results/orb_{name}_grade.csv')
print('celulas:', len(R), '| validacao>0:', (R.anual_va > 0).mean().round(2), '| corr sharpe tr/va:', R.sharpe_tr.corr(R.sharpe_va).round(2))
print(R.head(15).to_string()); print(R.loc[(30, 15, 'none', 'both')])
print(R.groupby(level=['filt']).sharpe_va.median(), R.groupby(level=['lado']).sharpe_va.median(), R.groupby(level=['X']).sharpe_va.median(), R.groupby(level=['L']).sharpe_va.median())
