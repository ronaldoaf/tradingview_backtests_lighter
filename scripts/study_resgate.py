"""Resgate das celulas dos lotes 3 a 33 descartadas antes da robustez pela conta antiga (CAGR por soma de log, que
inflava o vendido). Sem rerodar a grade inteira:

1. pre-filtro nas grades salvas, so com itens que nao dependem da curva de equity: t > 2 contra o controle (media
   dos trades) e bp_liq > 0 (CAGR composto > 0 exige media liquida > 0);
2. os kwargs de cada celula sao capturados rodando o main() do lote com os run_* trocados por um gravador (nada e
   calculado, nenhuma grade e reescrita);
3. periodo todo com o tvlib corrigido: CAGR > 0, Sharpe >= Sharpe do B&H, t > 2; quem passa vai para tercos,
   2a metade, spread 4x e funding 0 (study_veredito.run_cell) e para o criterio novo inteiro.

uso: python study_resgate.py ativo [k/n]  -> results/resgate/<ativo>_<k>.pkl
     python study_resgate.py --relatorio -> results/study_resgate.txt / .csv (correlacao contra as 34 aprovadas)"""
import os, sys, io, glob, pickle, inspect, contextlib, importlib
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_veredito as V
from study_tvlote6 import M1

LOTES = [str(n) for n in range(3, 34)] + ['12b']
OUT = os.path.join(D, 'results', 'resgate')


def candidatas(a):
    ref = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv'))
    out = []
    for lote in LOTES:
        f = os.path.join(D, 'results', f'study_tvlote{lote}_{a}_grid.csv')
        if not os.path.exists(f): continue
        g = pd.read_csv(f)
        if not {'est', 'TF', 'cfg', 't', 'bp_liq'} <= set(g.columns): continue
        g = g[~g.cfg.astype(str).str.contains('peek')]
        g = g[(g.t > 2) & (g.bp_liq > 0)].drop_duplicates(['est', 'TF', 'cfg'])
        out += [(lote, r.est, r.TF, r.cfg) for r in g.itertuples()]
    return out


def _args(ps, a0, n, d, mm):
    """posicionais gravados com o df trocado pela fatia d: mm entra o atual, tag '' e sem rows; series e frames
    com o indice do df original (sinais pre-calculados) sao cortados na fatia."""
    full = a0[1]; out = [n, d]
    for p, x in zip(ps[2:], a0[2:]):
        if p == 'mm': x = mm
        elif p == 'tag': x = ''
        elif p == 'rows': x = None
        elif p == 'verbose': x = False
        elif isinstance(x, (pd.Series, pd.DataFrame)) and x.index.equals(full.index):
            x = x.loc[d.index]
        elif isinstance(x, np.ndarray) and len(x) == len(full):
            x = x[full.index.get_indexer(d.index)]
        elif isinstance(x, tuple) and all(isinstance(y, pd.Series) and y.index.equals(full.index) for y in x):
            x = tuple(y.loc[d.index] for y in x)
        out.append(x)
    return out


def captura(lote, a, m1):
    """{(est, TF, cfg): fn(n, d, mm, m1)} gravando as chamadas do main() do lote."""
    mod = V.quiet(importlib.import_module, f'study_tvlote{lote}')
    got, orig = {}, {}
    for k, f in list(vars(mod).items()):
        if not ((k == 'run' or k.startswith('run_')) and callable(f)): continue
        ps = list(inspect.signature(f).parameters)
        if 'tag' not in ps: continue

        def rec(*args, _f=f, _ps=ps, **kw):
            if 'est' in kw and 'cfg' in kw:
                got[(kw['est'], kw['TF'], kw['cfg'])] = (
                    lambda n, d, mm, m1_, f=_f, ps=_ps, a0=args, kw=dict(kw): f(*_args(ps, a0, n, d, mm), **kw))
            return None, None
        orig[k] = f; setattr(mod, k, rec)
    lm, sm, tc = T.load_m1v, getattr(mod, 'summary', None), pd.DataFrame.to_csv
    T.load_m1v = lambda name: m1
    if hasattr(mod, 'T'): mod.T.load_m1v = T.load_m1v
    pd.DataFrame.to_csv = lambda *x, **y: None
    if sm: mod.summary = lambda *x, **y: None
    try:
        V.quiet(mod.main, [a])
    except Exception as e:
        print(f'  lote {lote}: main parou ({type(e).__name__}: {e}); {len(got)} celulas capturadas', flush=True)
    finally:
        T.load_m1v = lm; pd.DataFrame.to_csv = tc
        if sm: mod.summary = sm
        for k, f in orig.items(): setattr(mod, k, f)
    return got


def shard(a, k=0, n=1):
    os.makedirs(OUT, exist_ok=True)
    m1 = T.load_m1v(a); mm = M1(m1); cache = {}
    cand = candidatas(a)[k::n]
    lotes = sorted({c[0] for c in cand}, key=lambda x: (int(x.rstrip('b')), x))
    fns = {}
    for lote in lotes:
        fns[lote] = captura(lote, a, m1)
    rows, daily, falta = [], {}, []
    for i, (lote, est, tf, cfg) in enumerate(cand):
        fn = fns[lote].get((est, tf, cfg))
        if fn is None:
            falta.append((lote, est, tf, cfg)); continue
        full = cache.setdefault(tf, T.resample(m1, tf))
        try:
            o, tr = V.quiet(fn, a, full, mm, m1)
        except Exception as e:
            print(f'  erro L{lote} {est} {tf} {cfg}: {e}', flush=True); continue
        if not o: continue
        bh = T.bh_stats(full)
        if not (o['cagr'] > 0 and o['sharpe'] >= bh['bh_sharpe'] and o['t'] > 2): continue
        lt = int(lote.rstrip('b'))
        try:
            rec, dly = V.run_cell(a, m1, mm, cache, (lt, est, a, tf, {}, fn))
        except Exception as e:
            print(f'  erro nas fatias L{lote} {est} {tf} {cfg}: {e}', flush=True); continue
        rec.update(cfg=cfg, lote_txt=lote, nome=f'L{lote} {est} {a.upper()} {tf} {cfg}')
        rows.append(rec)
        if dly is not None: daily[rec['nome']] = dly
        print(f"[{i + 1}/{len(cand)}] {rec['nome']:<48} CAGR {rec['cagr_tudo']:+7.1%} Sh {rec['sharpe']:+5.2f} "
              f"({rec['bh_sharpe']:+4.2f}) t {rec['t']:+5.2f}", flush=True)
    print(f'{a} {k}/{n}: {len(cand)} candidatas, {len(falta)} sem captura, {len(rows)} passaram no periodo todo',
          flush=True)
    pickle.dump((rows, daily, falta, len(cand)), open(os.path.join(OUT, f'{a}_{k}.pkl'), 'wb'))


def relatorio():
    rows, daily, falta, ncand = [], {}, [], 0
    for f in sorted(glob.glob(os.path.join(OUT, '*_[0-9]*.pkl'))):
        r, d, fl, nc = pickle.load(open(f, 'rb')); rows += r; daily.update(d); falta += fl; ncand += nc
    R = pd.DataFrame(rows)
    ref = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv'))
    # fora as que ja estavam nas 306 da robustez (mesma celula: ativo, TF, trades e CAGR iguais)
    k306 = {(r.ativo, r.tf, int(r.trades), round(r.cagr_tudo, 4)) for r in ref.itertuples()}
    R['ja_rob'] = [(r.ativo, r.tf, int(r.trades), round(r.cagr_tudo, 4)) in k306 for r in R.itertuples()]
    # lookahead do script publicado (cfg 'peek') nao e negociavel
    R = R[~R.ja_rob & ~R.cfg.astype(str).str.contains('peek')].drop_duplicates(['ativo', 'tf', 'trades', 'cagr_tudo']).reset_index(drop=True)
    _, N = V.criterios(R)
    R['novo_sem_corr'] = N.all(axis=1)
    R['falha_novo'] = [','.join(c for c in N.columns if not N.loc[i, c]) for i in R.index]
    # diarias das 34 aprovadas
    ap = ref[ref.carteira]; aprov = {(r.lote, r.est, r.ativo, r.tf, r.cfg): r.nome for r in ap.itertuples()}
    M = dict(daily)
    for a in sorted(ap.ativo.unique()):
        m1 = T.load_m1v(a); mm = M1(m1); cache = {}
        for c in V.ensure_aprov(V.cells()):
            key = (c[0], c[1], c[2], c[3], str(c[4]))
            if c[2] == a and key in aprov:
                M['AP ' + aprov[key]] = V.run_cell(a, m1, mm, cache, c)[1]
    M = pd.DataFrame(M); names = [c for c in M if c.startswith('AP ')]
    # gulosa por Sharpe: entra quem tiver |corr| < 0,5 com as 34 e com as novas que ja entraram
    R['corr_max'] = np.nan; R['corr_com'] = ''; R['entra'] = False
    chosen = list(names)
    for i in R[R.novo_sem_corr].sort_values('sharpe', ascending=False).index:
        nm = R.at[i, 'nome']
        cc = {c: M[[nm, c]].dropna().corr().iloc[0, 1] for c in chosen if len(M[[nm, c]].dropna()) >= 120}
        w = max(cc, key=lambda c: abs(cc[c]), default=None)
        R.at[i, 'corr_max'] = cc[w] if w else 0.0; R.at[i, 'corr_com'] = (w or '').replace('AP ', '')
        if w is None or abs(cc[w]) < 0.5:
            chosen.append(nm); R.at[i, 'entra'] = True
    R = R.sort_values('sharpe', ascending=False)
    R.to_csv(os.path.join(D, 'results', 'study_resgate.csv'), index=False, float_format='%.4f')
    out = [f'Resgate lotes 3 a 33: {ncand} celulas das grades com t > 2 e bp_liq > 0 ({len(falta)} sem captura); '
           f'{len(R)} novas passam em CAGR > 0, Sharpe >= B&H e t > 2 no periodo todo com a conta corrigida; '
           f'{int(R.novo_sem_corr.sum())} passam no criterio novo; {int(R.entra.sum())} entram com |corr| < 0,5 '
           f'contra as {len(names)} aprovadas e entre si.\n']
    for r in R.itertuples():
        st = 'ENTRA' if r.entra else ('redundante' if r.novo_sem_corr else 'reprova')
        out.append(f"{r.nome:<52} {st:<10} CAGR {r.cagr_tudo:+7.1%} (B&H {r.bh_tudo:+7.1%}) Sh {r.sharpe:+5.2f} "
                   f"({r.bh_sharpe:+4.2f}) DD {r.dd:+4.0%} t {r.t:+5.2f} tercos {r.cagr_t1:+5.0%}/{r.cagr_t2:+5.0%}/"
                   f"{r.cagr_t3:+5.0%} 2a {r.cagr_2a:+5.0%} sp4 {r.cagr_sp4:+5.0%} f0 {r.cagr_f0:+5.0%} "
                   f"corr {r.corr_max:+.2f} ({r.corr_com}) {r.falha_novo}")
    if falta:
        out.append('\nSem captura (cfg da grade nao reproduzida pelo main atual):')
        out += [f'  L{l} {e} {t} {c}' for l, e, t, c in falta]
    txt = '\n'.join(out); print(txt)
    open(os.path.join(D, 'results', 'study_resgate.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    if sys.argv[1:] == ['--relatorio']:
        relatorio()
    else:
        k, n = map(int, (sys.argv[2] if len(sys.argv) > 2 else '0/1').split('/'))
        shard(sys.argv[1], k, n)
