"""Junta results/<ATIVO>_4p/*.csv com o criterio do B&H: a celula (TF x cfg) passa se o retorno composto nas 4 partes
(tot) >= 0,5 x retorno do B&H no mesmo periodo (se o B&H for negativo, a mesma regra fica mais facil). Ordena pela
media geometrica das 4 partes, exp(media ln(1+p_i)) - 1, da melhor celula aprovada de cada estrategia.
Grava results/<ATIVO>_4p/aprovadas_bh.csv e resumo_bh.txt.
uso: ATIVO=wti python agg_4p_bh.py"""
import glob, os, re
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
A = os.environ.get('ATIVO', 'wti'); R = os.path.join(D, 'results', A + '_4p')
m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; c = [t0 + (t1 - t0) * k / 5 for k in range(5)]
cl = m1.close[m1.index < c[4]]   # a 5a parte (OOS) nao entra
bh = [float(cl[cl.index < c[q + 1]].iloc[-1] / cl[cl.index < c[q]].iloc[-1] - 1) if q else float(cl[cl.index < c[1]].iloc[-1] / cl.iloc[0] - 1) for q in range(4)]
bh_tot = float(np.prod([1 + b for b in bh]) - 1); lim = 0.5 * bh_tot
g = pd.concat([pd.read_csv(f).assign(lote=os.path.basename(f)[4:-4]) for f in glob.glob(os.path.join(R, 'lote*.csv'))])
g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
g['est'] = g['est'].fillna(g.lote) if 'est' in g else g.lote
P = ['p1', 'p2', 'p3', 'p4']
g['tot4'] = np.prod(1 + g[P].values, axis=1) - 1
g['geo'] = np.expm1(np.log1p(np.clip(g[P].values, -0.999999, None)).mean(axis=1))
g['ok'] = g.tot4 >= lim
nomes = {}
for f in glob.glob(os.path.join(D, 'scripts', 'study_*.py')):
    s = open(f).read(); lt = re.sub(r'^study_(tvlote)?', '', os.path.basename(f)[:-3])
    for k, lab in re.findall(r"'(\w+)':\s*\(\s*\w+,\s*[\"']([^\"']+)", s): nomes[(lt, k)] = lab
    for k, lab in re.findall(r"\(\s*'(\w+)',\s*\w+,\s*\"([^\"]+)", s): nomes.setdefault((lt, k), lab)
    for lab, k in re.findall(r'###\s*([^"\'\n{]+?)["\'][^\n]*\n(?:[^\n]*\n){0,6}?[^\n]*est=["\'](\w+)', s): nomes.setdefault((lt, k), lab.strip())
n_est = g.groupby(['lote', 'est']).ngroups
a = g[g.ok].sort_values('geo', ascending=False).drop_duplicates(['lote', 'est']).copy()
a['nome'] = [nomes.get((l, e), '') for l, e in zip(a.lote, a.est)]
a['celula'] = a.apply(lambda r: ' '.join(str(r[k]) for k in ('TF', 'cfg') if k in r and pd.notna(r[k])), axis=1)
ok = g[g.ok].groupby(['lote', 'est']).size(); tt = g.groupby(['lote', 'est']).size()
a['n_cel_ok'] = [int(ok[(l, e)]) for l, e in zip(a.lote, a.est)]; a['n_cel'] = [int(tt[(l, e)]) for l, e in zip(a.lote, a.est)]
a['todas_pos'] = (a[P] > 0).all(axis=1)
cols = ['lote', 'est', 'nome', 'celula', 'p1', 'p2', 'p3', 'p4', 'tot4', 'geo', 'todas_pos', 'trades', 'n_cel_ok', 'n_cel', 'sid']
a[cols].to_csv(os.path.join(R, 'aprovadas_bh.csv'), index=False)
with open(os.path.join(R, 'resumo_bh.txt'), 'w') as fo:
    fo.write(f'cortes: {[str(x)[:10] for x in c]}\nB&H por parte: {[f"{b:+.1%}" for b in bh]}  total {bh_tot:+.1%}  limite {lim:+.1%}\n')
    fo.write(f'{n_est} estrategias, {len(g)} celulas; aprovadas {len(a)}; com as 4 partes positivas {int(a.todas_pos.sum())}\n')
    fo.write(a[cols].to_string(index=False, formatters={k: (lambda v: f'{v:+.1%}') for k in P + ['tot4', 'geo']}))
print(open(os.path.join(R, 'resumo_bh.txt')).read()[:3000])
