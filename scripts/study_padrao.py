"""O que as 34 aprovadas (results/study_veredito.csv, coluna carteira) tem em comum.
Roda de novo cada celula no periodo todo, guarda a posicao horaria (lado x unidades, 0 = fora) e os retornos diarios
(equity composta trade a trade do tvlib) e mede: exposicao, fracao do tempo comprado/vendido, duracao mediana do
trade, trades por ano e o "horizonte efetivo": o lookback L (em dias) cujo sinal de momento sign(close/close[L] - 1)
mais se parece com a posicao da celula (corr de Pearson das posicoes horarias).

uso: python study_padrao.py ativo      -> results/padrao/<ativo>.pkl (posicoes e retornos das celulas do ativo)
     python study_padrao.py --relatorio -> results/study_padrao.txt e results/study_padrao.csv"""
import os, sys, glob, pickle
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

CACHE = os.path.join(D, 'results', 'padrao')
LBS = [1, 2, 3, 5, 7, 10, 15, 20, 30, 45, 60, 90, 120, 180, 250]


def hourly_pos(full, tr):
    pos = np.zeros(len(full))
    for r in tr.itertuples():
        pos[int(r.i):int(r.j)] = r.d * r.u
    return pd.Series(pos, full.index).resample('1h').last().ffill()


def shard(name):
    import study_veredito as V
    from study_tvlote6 import M1
    os.makedirs(CACHE, exist_ok=True)
    R = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv'))
    C = R[R.carteira & (R.ativo == name)]
    want = {(r.lote, r.est, r.tf, r.cfg): r.nome for r in C.itertuples()}
    cs = [c for c in V.ensure_aprov(V.cells()) if c[2] == name and (c[0], c[1], c[3], str(c[4])) in want]
    m1 = T.load_m1v(name); mm = M1(m1); cache = {}; out = {}
    for lote, est, a, tf, kw, fn in cs:
        nm = want[(lote, est, tf, str(kw))]
        if nm in out: continue
        full = cache.setdefault(tf, T.resample(m1, tf))
        T.control_dur = lambda df, trades, *x, **k: np.zeros(2)      # o controle nao interessa aqui
        _, tr = V.quiet(fn, name, full, mm, m1)
        eq = T.equity_curve(full, tr, name)
        out[nm] = dict(ativo=name, tf=tf, pos=hourly_pos(full, tr),
                       dly=eq.resample('1D').last().dropna().pct_change().dropna(),
                       dur=float(np.median(tr.yrs) * 365), n=len(tr),
                       yrs=(full.index[-1] - full.index[0]).total_seconds() / (365 * 86400))
        print(nm, len(tr), flush=True)
    pickle.dump(out, open(os.path.join(CACHE, f'{name}.pkl'), 'wb'))


def mom_sign(close_h, L):
    return np.sign(close_h / close_h.shift(24 * L) - 1)


def relatorio():
    cells = {}
    for f in glob.glob(os.path.join(CACHE, '*.pkl')):
        cells.update(pickle.load(open(f, 'rb')))
    closes = {a: T.resample(T.load_m1v(a), '1h').close for a in {c['ativo'] for c in cells.values()}}
    rows = []
    for nm, c in cells.items():
        p = c['pos']; ch = closes[c['ativo']].reindex(p.index).ffill()
        cr = {L: p.corr(mom_sign(ch, L)) for L in LBS}
        best = max(cr, key=cr.get)
        rows.append(dict(nome=nm, ativo=c['ativo'], tf=c['tf'], expo=(p != 0).mean(), comprado=(p > 0).mean(),
                         vendido=(p < 0).mean(), dur_dias=c['dur'], trades_ano=c['n'] / c['yrs'], L_best=best,
                         corr_best=cr[best], **{f'c{L}': cr[L] for L in LBS}))
    S = pd.DataFrame(rows).sort_values(['ativo', 'L_best'])
    S.to_csv(os.path.join(D, 'results', 'study_padrao.csv'), index=False, float_format='%.3f')
    out = [f'{len(S)} celulas. Colunas: exposicao, tempo comprado / vendido, duracao mediana do trade (dias), '
           'trades/ano, lookback L (dias) do sinal de momento mais parecido com a posicao e essa correlacao.\n']
    out.append(S[['nome', 'expo', 'comprado', 'vendido', 'dur_dias', 'trades_ano', 'L_best', 'corr_best']]
               .to_string(index=False, float_format=lambda x: f'{x:.2f}'))
    out.append('\nCorrelacao media posicao x sign(momento L) por ativo:')
    out.append(S.groupby('ativo')[[f'c{L}' for L in LBS]].mean().round(2).to_string())
    out.append('\nMedianas: ' + ', '.join(f'{k} {S[k].median():.2f}' for k in
                                         ('expo', 'comprado', 'vendido', 'dur_dias', 'trades_ano', 'L_best', 'corr_best')))
    out.append(f"Sempre posicionadas (expo > 0,95): {(S.expo > 0.95).sum()} de {len(S)}; "
               f"so compradas: {(S.vendido == 0).sum()}")
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', 'study_padrao.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    relatorio() if sys.argv[1:] == ['--relatorio'] else shard(sys.argv[1])
