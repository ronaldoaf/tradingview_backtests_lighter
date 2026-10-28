"""Junta results/us100_4p/*.csv: estrategia aprovada se alguma celula (TF x cfg) tem p1..p4 > 0; ordena pelo tot
(soma dos lucros das 4 partes) da melhor celula aprovada. Grava results/us100_4p/aprovadas.csv e resumo.txt."""
import glob, os, re
import pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'us100_4p')
g = pd.concat([pd.read_csv(f).assign(lote=os.path.basename(f)[4:-4]) for f in glob.glob(os.path.join(R, 'lote*.csv'))])
# 'peek' e a variante com lookahead de proposito (vies), nao conta
g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
g['est'] = g['est'].fillna(g.lote) if 'est' in g else g.lote
g['soma'] = g[['p1', 'p2', 'p3', 'p4']].sum(axis=1)
g['ok'] = (g[['p1', 'p2', 'p3', 'p4']] > 0).all(axis=1)
cfgc = [c for c in g.columns if c not in ('p1', 'p2', 'p3', 'p4', 'tot', 'soma', 'ok', 'lote', 'est')]
nomes = {}
for f in glob.glob(os.path.join(D, 'scripts', 'study_*.py')):
    s = open(f).read(); lt = re.sub(r'^study_(tvlote)?', '', os.path.basename(f)[:-3])
    for k, lab in re.findall(r"'(\w+)':\s*\(\s*\w+,\s*[\"']([^\"']+)", s): nomes[(lt, k)] = lab
    for k, lab in re.findall(r"\(\s*'(\w+)',\s*\w+,\s*\"([^\"]+)", s): nomes.setdefault((lt, k), lab)
    for lab, k in re.findall(r'###\s*([^"\'\n{]+?)["\'][^\n]*\n(?:[^\n]*\n){0,6}?[^\n]*est=["\'](\w+)', s): nomes.setdefault((lt, k), lab.strip())
n_est = g.groupby(['lote', 'est']).ngroups
a = g[g.ok].sort_values('soma', ascending=False).drop_duplicates(['lote', 'est'])
a['nome'] = [nomes.get((l, e), '') for l, e in zip(a.lote, a.est)]
a['celula'] = a.apply(lambda r: ' '.join(str(r[c]) for c in ('TF', 'cfg') if c in r and pd.notna(r[c])), axis=1)
a['n_cel_ok'] = [int(g[(g.lote == l) & (g.est == e) & g.ok].shape[0]) for l, e in zip(a.lote, a.est)]
a['n_cel'] = [int(g[(g.lote == l) & (g.est == e)].shape[0]) for l, e in zip(a.lote, a.est)]
cols = ['lote', 'est', 'nome', 'celula', 'p1', 'p2', 'p3', 'p4', 'soma', 'trades', 'n_cel_ok', 'n_cel']
a[cols].to_csv(os.path.join(R, 'aprovadas.csv'), index=False)
with open(os.path.join(R, 'resumo.txt'), 'w') as fo:
    fo.write(f'{n_est} estrategias, {len(g)} celulas; aprovadas {len(a)}\n')
    fo.write(a[cols].to_string(index=False, float_format=lambda v: f'{v:+.1%}'))
print(open(os.path.join(R, 'resumo.txt')).read())
