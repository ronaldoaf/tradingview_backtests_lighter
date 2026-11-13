"""Roda as 50 configuracoes de selecao50.csv no XAG 30min com o filtro de tendencia HMA MTF (long+short, 4H).

Filtro: um trade de 30min so e mantido se, na entrada, a estrategia HMA (study_hmamtf.py, parametros publicados
16/65/52/14, modo 'ls') estiver posicionada do mesmo lado; HMA fora do mercado -> nenhum trade. O estado usado e o
da ultima barra 4H ja fechada (sem look-ahead). O filtro descarta trades depois de gerados (aproximacao).

uso (na pasta scripts/):
    EDGE_END=2023-12-31 python rodar_carteira50_btc30m_hma.py              # periodo da selecao
    EDGE_END=2025-06-30 python rodar_carteira50_btc30m_hma.py 2024-01-01   # fora da amostra
saida: ../results/carteira50_estrategias.csv, carteira50_retornos_diarios.csv, carteira50_trades.csv"""
import os, sys, runpy, itertools, io, contextlib
import numpy as np, pandas as pd
D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['EDGE_ROOT'] = D
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_hmamtf as H
ATIVO = 'xag'
SEL = pd.read_csv(os.path.join(D, 'selecao50.csv'))
INI = pd.Timestamp(sys.argv[1], tz='UTC') if len(sys.argv) > 1 else None

m1 = T.load_m1v(ATIVO); h4 = T.resample(m1, '4h'); d1 = T.resample(m1, '1D')
pos = np.zeros(len(h4))
for i0, j, d in H.trades_for(h4, d1, H.BASE, 'ls', {}):
    pos[i0:j] = d
FILT = pd.Series(pos, index=h4.index)


def estado(t):
    k = FILT.index.searchsorted(t, side='right') - 1
    return np.where(k >= 0, FILT.to_numpy()[np.clip(k, 0, None)], 0)


STD = {'trades','por_ano','bp_bruto','bp_liq','bp_sf','win','dias','cagr','bh','sharpe','bh_sharpe','dd','expo',
       'ctl_bp','t','long_frac','tag','TF','tid','est','cfg','trades_sem_filtro'}
_s = T.summarize; TR = {}; RD = {}; cnt = itertools.count()


def summ(df, trades, name, *a, **k):
    m30 = len(df) > 2 and (df.index[1] - df.index[0]) == pd.Timedelta('30min')
    if m30 and trades is not None and len(trades):
        tin = pd.to_datetime(trades['t_in']) if 't_in' in trades else df.index[trades['i'].to_numpy(int)]
        trades = trades[np.sign(trades['d'].to_numpy(float)) == estado(pd.DatetimeIndex(tin))]
    o = _s(df, trades, name, *a, **k)
    if o is not None and m30:
        i = next(cnt); o['tid'] = i; TR[i] = trades.copy()
        eq = T.equity_curve(df, trades, name)
        RD[i] = eq.resample('1D').last().dropna().pct_change().dropna()
    return o


T.summarize = summ


def stats(r):
    eq = (1 + r).cumprod(); yrs = max((r.index[-1] - r.index[0]).days, 1) / 365
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * np.sqrt(365),
                dd=(eq / eq.cummax() - 1).min(), total=eq.iloc[-1] - 1)


if __name__ == '__main__':
    os.makedirs(os.path.join(D, 'results'), exist_ok=True)
    rets, out, trs = {}, [], []
    for e in sorted(SEL.estudo.unique()):
        scr = os.path.join(D, 'scripts', f'study_{e}.py')
        print(f'rodando {e} ...', flush=True)
        argv = sys.argv; sys.argv = [scr, ATIVO]
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(scr, run_name='__main__')
        sys.argv = argv
        f = os.path.join(D, 'results', f'study_{e}_{ATIVO}_grid.csv')
        if not os.path.exists(f): f = os.path.join(D, 'scripts', f'study_{e}_{ATIVO}_grid.csv')
        g = pd.read_csv(f).rename(columns={'tf': 'TF'})
        g = g[g.TF.astype(str) == '30min'].copy()
        if 'est' not in g:
            g['est'] = g['model'].astype(str) if 'model' in g else (g['ver'].astype(str) if 'ver' in g else e)
        if 'cfg' not in g:
            ps = [c for c in g.columns if c not in STD | {'model', 'ver', 'est'}]
            g['cfg'] = g[ps].astype(str).apply(lambda r: ' '.join(f'{k}={v}' for k, v in r.items()), axis=1)
        for _, s in SEL[SEL.estudo == e].iterrows():
            m = g[(g.est == s.est) & (g.cfg.astype(str) == str(s.cfg))]
            if m.empty or pd.isna(m.iloc[0].get('tid')):
                print('  nao achei', s.est, s.cfg); continue
            i = int(m.iloc[0].tid); r = RD[i]; t = TR[i].assign(id=s.id)
            if INI is not None:
                r = r[r.index >= INI]; t = t[pd.to_datetime(t.t_in) >= INI]
            rets[s.id] = r; trs.append(t)
            out.append(dict(id=s.id, trades=len(t), **stats(r)))
    R = pd.DataFrame(rets).fillna(0.0)
    R.to_csv(os.path.join(D, 'results', 'carteira50_retornos_diarios.csv'))
    pd.concat(trs).to_csv(os.path.join(D, 'results', 'carteira50_trades.csv'), index=False)
    pd.DataFrame(out).sort_values('cagr', ascending=False).to_csv(os.path.join(D, 'results', 'carteira50_estrategias.csv'), index=False)
    bh = m1.close.resample('1D').last().dropna().pct_change().dropna()
    bh = bh[(bh.index >= R.index[0]) & (bh.index <= R.index[-1])]
    print(f'\nperiodo {R.index[0]:%Y-%m-%d} a {R.index[-1]:%Y-%m-%d}, {R.shape[1]} estrategias')
    print('carteira peso igual:', {k: round(v, 3) for k, v in stats(R.mean(axis=1)).items()})
    print('buy & hold XAG     :', {k: round(v, 3) for k, v in stats(bh).items()})
