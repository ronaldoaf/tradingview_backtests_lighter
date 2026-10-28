"""Ordena todas as estrategias pelo retorno total composto antes do OOS (melhor celula de cada uma), usando as partes
ja calculadas em results/<ATIVO>_4p<SUF> (produto de 1+p_i = todos os trades que entram antes do OOS). Sem filtro;
templates/exemplos fora. Grava ranking_total.csv.  uso: ATIVO=wti SUF=_8p_full NP=8 python rank_total.py"""
import glob, os
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.environ.get('ATIVO', 'wti'); NP = int(os.environ.get('NP', '8')); R = os.path.join(D, 'results', A + '_4p' + os.environ.get('SUF', '_8p_full'))
g = pd.concat([pd.read_csv(f).assign(lote=os.path.basename(f)[4:-4]) for f in glob.glob(os.path.join(R, 'lote*.csv'))])
g = g[~(g.cfg.astype(str).eq('peek') | g.tag.astype(str).str.contains('peek'))]
g['est'] = g.est.fillna(g.lote); P = [f'p{q}' for q in range(1, NP + 1)]
g['total'] = np.prod(1 + g[P].values, axis=1) - 1
g['celula'] = g.apply(lambda r: ' '.join(str(r[k]) for k in ('TF', 'cfg') if pd.notna(r[k])), axis=1)
nomes = pd.read_csv(os.path.join(R, 'ranking.csv')).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()
a = g.sort_values('total', ascending=False).drop_duplicates(['lote', 'est']).copy()
a['nome'] = [nomes.get((str(l), e), '') for l, e in zip(a.lote, a.est)]
a = a[~a.nome.fillna('').astype(str).str.contains('Example|Template', case=False)]
yrs = 7.79; a['cagr'] = (1 + a.total) ** (1 / yrs) - 1
cols = ['lote', 'est', 'nome', 'celula', 'total', 'cagr', 'trades']
a[cols].to_csv(os.path.join(R, 'ranking_total.csv'), index=False)
print(f'{len(a)} estrategias; total > 0: {(a.total > 0).sum()}')
print(a[cols].head(25).to_string(index=False, formatters={'total': lambda v: f'{v:+.0%}', 'cagr': lambda v: f'{v:+.1%}'}))
