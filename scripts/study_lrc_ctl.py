"""Controle aleatorio do LRC 50/1.5/6/50 em 30m (BTC, ETH): embaralha a serie de sinais (mesmo numero e mesma
proporcao long/short, posicoes aleatorias), mesma saida trailing 6xATR(50) e mesmos custos. 500 sims por janela."""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
from study_lrc import lrc, sim, OUT
from tvlib import atr_rma
from study_engulf_psar import CUSTO, FUND
C1, C2 = pd.Timestamp('2024-01-01', tz='UTC'), pd.Timestamp('2025-07-01', tz='UTC')
rng = np.random.default_rng(7); N, DEV, K, L, NS = 50, 1.5, 6, 50, 500

def tot(df, a, sig, atr):
    ei, xi, s, pi, px = sim(df.open.values, df.high.values, df.low.values, df.close.values, sig, atr, K)
    yrs = (df.index.values[xi] - df.index.values[ei]) / np.timedelta64(1, 's') / (365 * 86400)
    r = s * np.log(px / pi) - 2 * CUSTO[a] - s * FUND[a] / 100 * yrs
    return r.sum(), len(r)

rows = []
for a in ['btc', 'eth']:
    for nm, sl in [('treino', slice(None, C1)), ('valid', slice(C1, C2)), ('teste', slice(C2, None))]:
        df = pd.read_parquet(os.path.join(OUT, f'{a}_30m.parquet')); df = df[(df.index >= (sl.start or df.index[0])) & (df.index < (sl.stop or df.index[-1] + pd.Timedelta('1s')))]
        c = df.close.values; b, up, lo = lrc(c, N); mid = (up + lo) / 2; sd = up - mid
        sig = np.where((b > 0) & (c < mid - DEV * sd), 1, np.where((b < 0) & (c > mid + DEV * sd), -1, 0)).astype(np.int64)
        atr = atr_rma(df.high.values, df.low.values, c, L); real, nt = tot(df, a, sig, atr)
        ok = np.where(~np.isnan(atr) & ~np.isnan(b))[0]; sims = []
        for _ in range(NS):
            s2 = np.zeros_like(sig); s2[ok] = rng.permutation(sig[ok]); sims.append(tot(df, a, s2, atr)[0])
        sims = np.array(sims)
        rows.append(dict(ativo=a, janela=nm, trades=nt, estrat=round(100 * (np.exp(real) - 1), 1),
                         aleat_mediana=round(100 * (np.exp(np.median(sims)) - 1), 1), percentil=round(100 * (sims < real).mean())))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'controle_30m.csv'), index=False)
