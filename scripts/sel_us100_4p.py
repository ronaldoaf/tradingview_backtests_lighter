"""Das aprovadas em results/us100_4p/aprovadas.csv, escolhe 20 pouco correlacionadas: percorre por ordem de soma e
aceita a estrategia se a maior correlacao (retornos diarios, so nas 4 partes) com as ja aceitas fica abaixo do
limite; o limite e o menor (passo 0,01) que ainda fecha 20. Grava results/us100_4p/sel20.csv e sel20_corr.csv."""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = os.environ.get('ATIVO', 'us100'); R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', ''))
BH = A != 'us100'   # nos outros ativos: aprovadas pelo criterio do B&H com as 4 partes positivas, ordem pela media geometrica
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
a = pd.read_csv(os.path.join(R, 'aprovadas_bh.csv' if BH else 'aprovadas.csv')); ser = {}
if BH: a = a[a.todas_pos].reset_index(drop=True).rename(columns={'geo': 'soma'})
for l in a.lote.astype(str).str.split('_').str[0].unique():
    ser[l] = pd.read_parquet(os.path.join(R, f'lote{l}_ser.parquet'))
X = pd.concat([ser[str(l).split('_')[0]][int(s)].rename(i) for i, (l, s) in enumerate(zip(a.lote, a.sid))], axis=1).fillna(0.0)
C = X.corr().to_numpy()


def pega(lim):
    s = []
    for i in range(len(a)):
        if all(C[i, j] < lim for j in s): s.append(i)
        if len(s) == K: return s
    return None


LIM = float(sys.argv[2]) if len(sys.argv) > 2 else None   # limite fixo (ex.: 0.5); sem ele, o menor que fecha K
lim = LIM if LIM is not None else next(l for l in np.arange(0.0, 1.01, 0.01) if pega(l)); s = pega(lim)
b = a.iloc[s].assign(rank=[i + 1 for i in s], corr_max=[max([C[i, j] for j in s if j != i]) for i in s],
                     corr_med=[np.mean([C[i, j] for j in s if j != i]) for i in s])
b.to_csv(os.path.join(R, f'sel{K}.csv'), index=False)
pd.DataFrame(C[np.ix_(s, s)], index=b.est, columns=b.est).round(2).to_csv(os.path.join(R, f'sel{K}_corr.csv'))
cart = X[s].mean(axis=1); eq = (1 + cart).cumprod()
print(f'limite {lim:.2f}; corr media do par {np.mean(C[np.ix_(s, s)][np.triu_indices(K, 1)]):.2f}')
print(f'carteira igual peso: total {eq.iloc[-1] - 1:+.0%}, Sharpe {cart.mean() / cart.std() * np.sqrt(252):.2f}, DD {(eq / eq.cummax() - 1).min():.0%}')
print(b[['rank', 'lote', 'est', 'nome', 'celula', 'p1', 'p2', 'p3', 'p4', 'soma', 'corr_max']].to_string(index=False, float_format=lambda v: f'{v:+.2f}'))
