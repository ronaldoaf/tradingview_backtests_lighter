"""Ordena todas as estrategias (melhor celula de cada uma, sem filtro) pela media geometrica das NP partes,
exp(media ln(1+p_i)) - 1. Grava results/<ATIVO>_4p<SUF>/ranking.csv e ranking.txt.
uso: ATIVO=wti SUF=_10p NP=10 python rank_np.py"""
import glob, os, re
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.environ.get('ATIVO', 'wti'); NP = int(os.environ.get('NP', '10')); R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', ''))
g = pd.concat([pd.read_csv(f).assign(lote=os.path.basename(f)[4:-4]) for f in glob.glob(os.path.join(R, 'lote*.csv'))])
g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
g['est'] = g['est'].fillna(g.lote) if 'est' in g else g.lote
P = [f'p{q}' for q in range(1, NP + 1)]
g['geo'] = np.expm1(np.log1p(np.clip(g[P].values, -0.999999, None)).mean(axis=1))
g['n_pos'] = (g[P] > 0).sum(axis=1)
nomes = {}
for f in glob.glob(os.path.join(D, 'scripts', 'study_*.py')):
    s = open(f).read(); lt = re.sub(r'^study_(tvlote)?', '', os.path.basename(f)[:-3])
    for k, lab in re.findall(r"'(\w+)':\s*\(\s*\w+,\s*[\"']([^\"']+)", s): nomes[(lt, k)] = lab
    for k, lab in re.findall(r"\(\s*'(\w+)',\s*\w+,\s*\"([^\"]+)", s): nomes.setdefault((lt, k), lab)
    for lab, k in re.findall(r'###\s*([^"\'\n{]+?)["\'][^\n]*\n(?:[^\n]*\n){0,6}?[^\n]*est=["\'](\w+)', s): nomes.setdefault((lt, k), lab.strip())
a = g.sort_values('geo', ascending=False).drop_duplicates(['lote', 'est']).copy()
a['nome'] = [nomes.get((l, e), '') for l, e in zip(a.lote, a.est)]
a['celula'] = a.apply(lambda r: ' '.join(str(r[k]) for k in ('TF', 'cfg') if k in r and pd.notna(r[k])), axis=1)
a['trades'] = a.trades.astype('Int64')
cols = ['lote', 'est', 'nome', 'celula'] + P + ['geo', 'n_pos', 'trades']
a[cols].to_csv(os.path.join(R, 'ranking.csv'), index=False)
with open(os.path.join(R, 'ranking.txt'), 'w') as fo:
    fo.write(f'{len(a)} estrategias, {len(g)} celulas; geo > 0: {(a.geo > 0).sum()}\n')
    fo.write(a[cols].to_string(index=False, formatters={k: (lambda v: f'{v:+.1%}') for k in P + ['geo']}))
print(open(os.path.join(R, 'ranking.txt')).read()[:2500])
