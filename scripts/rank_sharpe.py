"""Ordena todas as estrategias pelo Sharpe diario antes do OOS (melhor celula de cada uma, pelo Sharpe), com as
series de results/<ATIVO>_4p<SUF> (FULL=1). Sem filtro; templates/exemplos fora. Grava ranking_sharpe.csv.
uso: ATIVO=wti SUF=_8p_full NP=8 python rank_sharpe.py"""
import glob, os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); NP = int(os.environ.get('NP', '8')); R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', '_8p_full'))
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; corte = (t0 + (t1 - t0) * 4 / 5).normalize()
nomes = pd.read_csv(os.path.join(R, 'ranking.csv')).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()
P = [f'p{q}' for q in range(1, NP + 1)]; out = []
for f in glob.glob(os.path.join(R, 'lote*.csv')):
    l = os.path.basename(f)[4:-4]; g = pd.read_csv(f)
    if 'sid' not in g: continue   # csv auxiliar sem series
    g['est'] = g['est'].fillna(l) if 'est' in g else l
    S = pd.read_parquet(os.path.join(R, f'lote{l.split("_")[0]}_ser.parquet')); S.index = pd.DatetimeIndex(S.index)
    c = corte if S.index.tz is not None else corte.tz_localize(None); S = S[S.index < c].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    f_ano = len(S) / ((S.index[-1] - S.index[0]).days / 365)
    if os.environ.get('METRIC') == 'kalmar':   # CAGR / |DD maximo| da equity diaria
        eq = (1 + S).cumprod(); anos = (S.index[-1] - S.index[0]).days / 365
        sh = (eq.iloc[-1].clip(lower=1e-9) ** (1 / anos) - 1) / (1 - eq / eq.cummax()).max().clip(lower=1e-4)
    elif os.environ.get('METRIC') == 'sortino':   # media / desvio so dos dias negativos
        sh = S.mean() / np.sqrt((S.clip(upper=0) ** 2).mean()) * np.sqrt(f_ano)
    else: sh = S.mean() / S.std() * np.sqrt(f_ano)
    sh.index = sh.index.astype(str)
    g['sharpe'] = [sh.get(str(int(s)), np.nan) for s in g.sid]
    g['lote'] = l; out.append(g)
g = pd.concat(out)
g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
g['total'] = np.prod(1 + g[P].values, axis=1) - 1
g['celula'] = g.apply(lambda r: ' '.join(str(r[k]) for k in ('TF', 'cfg') if k in r and pd.notna(r[k])), axis=1)
g = g[g.trades >= int(os.environ.get('MINTR', '0'))]   # MINTR: minimo de trades da celula
a = g.dropna(subset=['sharpe']).sort_values('sharpe', ascending=False).drop_duplicates(['lote', 'est']).copy()
a['nome'] = [nomes.get((l, e), '') for l, e in zip(a.lote, a.est)]
a = a[~a.nome.fillna('').astype(str).str.contains('Example|Template', case=False)]
cols = ['lote', 'est', 'nome', 'celula', 'sharpe', 'total', 'trades']
M = os.environ.get('METRIC', 'sharpe'); a = a.rename(columns={'sharpe': M}); cols = [M if c == 'sharpe' else c for c in cols]
a[cols].to_csv(os.path.join(R, f"ranking_{os.environ.get('METRIC', 'sharpe')}{os.environ.get('MINTR', '')}.csv"), index=False)
print(f'{len(a)} estrategias; {M} > 0: {(a[M] > 0).sum()}')
print(a[cols].head(20).to_string(index=False, formatters={'total': lambda v: f'{v:+.0%}', M: lambda v: f'{v:.2f}'}))
