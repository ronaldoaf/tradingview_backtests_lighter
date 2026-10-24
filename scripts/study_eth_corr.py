"""Correlacao entre as candidatas no ETH (APROVADAS 2, 3 e 4): retornos diarios e sobreposicao das posicoes.
Posicao marcada no 15m (close a close) a partir dos trades de cada simulacao; custo e funding entram no dia da saida.
uso: python study_eth_corr.py"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_tvlote12 as L12, study_tvlote13 as L13, study_tvlote4 as L4
from study_tvlote6 import M1

name = 'eth'
m1 = T.load_m1v(name); mm = M1(m1)
c = {tf: T.resample(m1, tf) for tf in ('15min', '30min')}
L, S = L4.ppst_signals(c['15min'], prd=5, F=2.0, Pd=10)
runs = {
    'RSI-MA 15m': L12.run_rsima(name, c['15min'], mm, 'rsima', rl=10, ml=50)[1],
    'Pivot ST 15m': L4.run_bars(name, c['15min'], L, S, 'ppst')[1],
    'UT Bot 30m': L13.run_ut(name, c['30min'], mm, 'ut', a=5.0, atr_n=11, shorts=True)[1],
    'Ichimoku 15m': L13.run_ichi(name, c['15min'], mm, 'ichi', ts=20, ks=60, sb=120, off=60)[1],
    'Scalping 30m': L13.run_scalp(name, c['30min'], mm, 'scalp', sma_len=25, ema_len=0)[1],
}
base = c['15min'].close
pos, daily = {}, {}
for k, tr in runs.items():
    p = pd.Series(0.0, index=base.index)
    for t_in, t_out, d in zip(tr.t_in, tr.t_out, tr.d):
        p[(p.index >= t_in) & (p.index < t_out)] = d
    pos[k] = p
    # barra rotulada pela abertura: a posicao aberta em t_in pega o retorno dessa barra
    r = (p * base.pct_change().fillna(0)).resample('1D').sum()
    cost = (tr.ret - tr.bruto).groupby(tr.t_out.dt.floor('1D')).sum()
    daily[k] = r.add(cost.reindex(r.index).fillna(0), fill_value=0)
P = pd.DataFrame(pos); R = pd.DataFrame(daily)
R['B&H ETH'] = base.resample('1D').last().pct_change().fillna(0)
ks = list(runs)
same = pd.DataFrame([[float((np.sign(P[a]) == np.sign(P[b])).mean()) for b in ks] for a in ks], ks, ks)
pd.set_option('display.width', 200)
print("Correlacao dos retornos diarios (Pearson)\n", R.corr().round(2).to_string())
print("\nCorrelacao das posicoes (15m)\n", P.corr().round(2).to_string())
print("\nFracao do tempo na mesma direcao\n", same.round(2).to_string())
print("\nCAGR aprox. de cada uma e da carteira igual (media diaria)")
for k in ks + ['carteira']:
    x = R[ks].mean(axis=1) if k == 'carteira' else R[k]
    eq = np.exp(np.log1p(x).cumsum()); yrs = len(x) / 365
    print(f"  {k:<14} CAGR {eq.iloc[-1] ** (1 / yrs) - 1:+.1%}  DD {(eq / eq.cummax() - 1).min():+.0%}  "
          f"vol anual {x.std() * np.sqrt(365):.0%}")
