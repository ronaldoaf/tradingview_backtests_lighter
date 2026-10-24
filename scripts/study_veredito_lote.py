"""Veredito direto de um lote novo, sem script _rob escrito a mao (o modulo do lote expoe KW(est, cfg)): pega as celulas da grade que ja passam nos itens
baratos do criterio novo (CAGR > 0, Sharpe >= B&H, t > 2), roda tercos, 2a metade, spread 4x e funding zero com
study_veredito.run_cell e aplica o criterio novo inteiro, incluindo |corr| < 0,5 com as aprovadas de
results/study_veredito.csv (as diarias delas sao recalculadas aqui).

uso: python study_veredito_lote.py 34 [ativos...]   -> results/study_tvlote<N>_veredito.txt / .csv"""
import os, sys, importlib
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
import study_veredito as V
from study_tvlote6 import M1


def main(lote, ativos):
    mod = importlib.import_module(f'study_tvlote{lote}')
    ref = pd.read_csv(os.path.join(D, 'results', 'study_veredito.csv'))
    ref = ref[ref.carteira]
    aprov = {(r.lote, r.est, r.ativo, r.tf, r.cfg) for r in ref.itertuples()}
    allc = [c for c in V.ensure_aprov(V.cells()) if (c[0], c[1], c[2], c[3], str(c[4])) in aprov]
    rows, daily = [], {}
    for a in ativos:
        g = pd.read_csv(os.path.join(D, 'results', f'study_tvlote{lote}_{a}_grid.csv'))
        cand = g[(g.cagr > 0) & (g.sharpe >= g.bh_sharpe) & (g.t > 2)]
        print(f'{a}: {len(g)} celulas, {len(cand)} candidatas', flush=True)
        m1 = T.load_m1v(a); mm = M1(m1); cache = {}
        for c in [c for c in allc if c[2] == a]:
            rec, dly = V.run_cell(a, m1, mm, cache, c)
            daily[f'L{rec["lote"]} {rec["est"]} {a.upper()} {rec["tf"]}'] = dly
        for r in cand.itertuples():
            kw = mod.KW(r.est, r.cfg)
            fn = lambda n, d, mm_, m1_, f=getattr(mod, 'run_' + r.est), kw=kw: f(n, d, mm_, '', **kw)
            rec, dly = V.run_cell(a, m1, mm, cache, (lote, r.est, a, r.TF, kw, fn))
            rec['cfg'] = r.cfg
            rec['nome'] = f'L{lote} {r.est} {a.upper()} {r.TF} {r.cfg}'
            rows.append(rec)
            if dly is not None: daily[rec['nome']] = dly
            print(f"  {rec['nome']:<44} CAGR {rec['cagr_tudo']:+7.1%} Sh {rec.get('sharpe', np.nan):+5.2f} "
                  f"t {rec.get('t', np.nan):+5.2f}", flush=True)
    R = pd.DataFrame(rows)
    if R.empty:
        txt = f'Lote {lote}: nenhuma celula passa em CAGR > 0, Sharpe >= B&H e t > 2.'
    else:
        _, N = V.criterios(R)
        R['novo_sem_corr'] = N.all(axis=1)
        R['falha_novo'] = [','.join(c for c in N.columns if not N.loc[i, c]) for i in R.index]
        M = pd.DataFrame(daily)
        names = [k for k in daily if not k.startswith(f'L{lote} ')]
        R['corr_max'] = np.nan; R['corr_com'] = ''
        for i, r in R.iterrows():
            if r.nome not in M: continue
            cc = {k: M[[r.nome, k]].dropna().corr().iloc[0, 1] for k in names if len(M[[r.nome, k]].dropna()) >= 120}
            if cc:
                w = max(cc, key=lambda k: abs(cc[k])); R.at[i, 'corr_max'] = cc[w]; R.at[i, 'corr_com'] = w
        R['entra'] = R.novo_sem_corr & (R.corr_max.abs() < 0.5)
        R = R.sort_values('sharpe', ascending=False)
        out = [f'Lote {lote}: {len(R)} celulas candidatas (CAGR > 0, Sharpe >= B&H, t > 2) com tercos, 2a metade, '
               f'spread 4x e funding 0; correlacao contra as {len(names)} aprovadas.\n']
        for r in R.itertuples():
            st = 'ENTRA' if r.entra else ('redundante' if r.novo_sem_corr else 'reprova')
            out.append(f"{r.nome:<48} {st:<10} CAGR {r.cagr_tudo:+7.1%} (B&H {r.bh_tudo:+7.1%}) Sh {r.sharpe:+5.2f} "
                       f"({r.bh_sharpe:+4.2f}) DD {r.dd:+4.0%} t {r.t:+5.2f} tercos {r.cagr_t1:+5.0%}/{r.cagr_t2:+5.0%}/"
                       f"{r.cagr_t3:+5.0%} 2a {r.cagr_2a:+5.0%} sp4 {r.cagr_sp4:+5.0%} f0 {r.cagr_f0:+5.0%} "
                       f"corr {r.corr_max:+.2f} ({r.corr_com}) {r.falha_novo}")
        txt = '\n'.join(out)
        R.to_csv(os.path.join(D, 'results', f'study_tvlote{lote}_veredito.csv'), index=False, float_format='%.4f')
    print(txt)
    open(os.path.join(D, 'results', f'study_tvlote{lote}_veredito.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main(int(sys.argv[1]), sys.argv[2:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
