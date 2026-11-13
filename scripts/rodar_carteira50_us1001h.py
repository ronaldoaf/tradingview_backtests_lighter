"""Roda as 50 configuracoes da carteira (selecao50.csv) no US100 1h e monta a carteira de peso igual.

Para cada lote presente na selecao, roda o script do lote (grade inteira, no ouro), guarda os retornos diarios das
celulas de 1h e depois filtra as 50 da lista. E o caminho mais fiel: as estrategias rodam exatamente pelo mesmo
codigo da planilha.

uso (na pasta scripts/):
    EDGE_END=2023-12-31 python rodar_carteira50_xau1h.py          # periodo da selecao
    EDGE_END=2025-06-30 python rodar_carteira50_xau1h.py 2024-01-01   # roda ate jun/2025 e mede so de 2024 em diante
saida: ../results/carteira50_estrategias.csv, ../results/carteira50_retornos_diarios.csv, resumo na tela."""
import os, sys, runpy, itertools, io, contextlib
import numpy as np, pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['EDGE_ROOT'] = D
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
ATIVO = os.environ.get('ATIVO', 'us100')

SEL = pd.read_csv(os.path.join(D, 'selecao50.csv'))
INI = pd.Timestamp(sys.argv[1], tz='UTC') if len(sys.argv) > 1 else None
_s = T.summarize; CAP = {}; cnt = itertools.count()


def summ(df, trades, name, *a, **k):
    o = _s(df, trades, name, *a, **k)
    if o is not None and len(df) > 2 and (df.index[1] - df.index[0]) == pd.Timedelta('1h'):
        eq = T.equity_curve(df, trades, name)
        i = next(cnt); o['tid'] = i
        CAP[i] = eq.resample('1D').last().dropna().pct_change().dropna()
    return o


T.summarize = summ


def stats(r):
    eq = (1 + r).cumprod(); yrs = max((r.index[-1] - r.index[0]).days, 1) / 365
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * np.sqrt(252),
                dd=(eq / eq.cummax() - 1).min(), total=eq.iloc[-1] - 1)


if __name__ == '__main__':
    os.makedirs(os.path.join(D, 'results'), exist_ok=True)
    rets, out = {}, []
    for e in sorted(SEL.estudo.unique()):
        scr = os.path.join(D, 'scripts', f'study_{e}.py')
        print(f'rodando {e} ...', flush=True)
        argv = sys.argv; sys.argv = [scr, ATIVO]
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(scr, run_name='__main__')
        sys.argv = argv
        g = pd.read_csv(os.path.join(D, 'results', f'study_{e}_{ATIVO}_grid.csv'))
        g = g[g.TF.astype(str) == '1h']
        if 'est' not in g: g['est'] = g['model'].astype(str) if 'model' in g else e
        for _, s in SEL[SEL.estudo == e].iterrows():
            m = g[(g.est == s.est) & (g.cfg.astype(str) == str(s.cfg))]
            if m.empty or pd.isna(m.iloc[0].get('tid')):
                print('  nao achei', s.est, s.cfg); continue
            r = CAP[int(m.iloc[0].tid)]
            if INI is not None: r = r[r.index >= INI]
            k = f'{e} {s.est} {s.cfg}'; rets[k] = r
            out.append(dict(estrategia=k, **stats(r)))
    R = pd.DataFrame(rets).fillna(0.0)
    R.to_csv(os.path.join(D, 'results', 'carteira50_retornos_diarios.csv'))
    pd.DataFrame(out).sort_values('cagr', ascending=False).to_csv(os.path.join(D, 'results', 'carteira50_estrategias.csv'), index=False)
    m1 = T.load_m1v(ATIVO); bh = m1.close.resample('1D').last().dropna().pct_change().dropna()
    bh = bh[(bh.index >= R.index[0]) & (bh.index <= R.index[-1])]
    print(f'\nperiodo {R.index[0]:%Y-%m-%d} a {R.index[-1]:%Y-%m-%d}, {R.shape[1]} estrategias')
    print('carteira peso igual:', {k: round(v, 3) for k, v in stats(R.mean(axis=1)).items()})
    print('buy & hold        :', {k: round(v, 3) for k, v in stats(bh).items()})
    print('estrategias com CAGR > 0:', int((pd.DataFrame(out).cagr > 0).sum()), 'de', len(out))
