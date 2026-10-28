"""Ranking com exclusao: a celula passa se a media geometrica das NP partes e > 0 e nenhuma parte perde mais que
PMIN (padrao -5%); fica a melhor celula aprovada de cada estrategia, ordenada pela media geometrica.
Le results/<ATIVO>_4p<SUF>/ranking.csv para os nomes; grava aprovadas.csv.
uso: ATIVO=wti SUF=_8p_full NP=8 PMIN=-0.05 python filt_np.py"""
import glob, os
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.environ.get('ATIVO', 'wti'); NP = int(os.environ.get('NP', '8')); PMIN = float(os.environ.get('PMIN', '-0.05'))
R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', ''))
g = pd.concat([pd.read_csv(f).assign(lote=os.path.basename(f)[4:-4]) for f in glob.glob(os.path.join(R, 'lote*.csv'))])
g = g[~(g.cfg.astype(str).eq('peek') | g.tag.astype(str).str.contains('peek'))]
g['est'] = g.est.fillna(g.lote); P = [f'p{q}' for q in range(1, NP + 1)]
g['geo'] = np.expm1(np.log1p(np.clip(g[P].values, -0.999999, None)).mean(axis=1)); g['n_pos'] = (g[P] > 0).sum(axis=1)
g['pior'] = g[P].min(axis=1)
g['celula'] = g.apply(lambda r: ' '.join(str(r[k]) for k in ('TF', 'cfg') if pd.notna(r[k])), axis=1)
nomes = pd.read_csv(os.path.join(R, 'ranking.csv')).set_index(['lote', 'est']).nome.to_dict()
a = g[(g.geo > 0) & (g.pior >= PMIN)].sort_values('geo', ascending=False).drop_duplicates(['lote', 'est']).copy()
a['nome'] = [nomes.get((l, e), nomes.get((int(l) if l.isdigit() else l, e), '')) for l, e in zip(a.lote, a.est)]
cols = ['lote', 'est', 'nome', 'celula'] + P + ['geo', 'pior', 'n_pos', 'trades']
a[cols].to_csv(os.path.join(R, 'aprovadas.csv'), index=False)
print(f'{g.groupby(["lote", "est"]).ngroups} estrategias; aprovadas {len(a)} (geo > 0 e nenhuma parte abaixo de {PMIN:+.0%})')
print(a[cols].to_string(index=False, formatters={k: (lambda v: f'{v:+.1%}') for k in P + ['geo', 'pior']}))
