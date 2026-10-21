"""Trendline Angle Pro V6 - segunda rodada: calibracao por mercado, como o AUTOR manda fazer.

Na descricao o autor diz: "use 5 a 15 minutos para intraday ou o grafico diario para swing" e
"os ajustes que servem para o Nifty nao servem para Bitcoin ou Ouro, entao calibre a escala do angulo,
as EMAs e o stop para cada mercado". Esta rodada faz exatamente isso no ouro:

  - TF de 5 min a 1 dia (os dois extremos que ele recomenda estao cobertos);
  - o gatilho de angulo deixa de ser 20 graus fixos e passa a ser um PERCENTIL do |angulo| observado
    naquele TF (p0 = sem filtro, p50, p75, p90, p95) - assim o filtro e de fato seletivo em cada TF,
    em vez de pegar 64% das barras como os 20 graus pegam no ouro de 1h;
  - k45 (a escala que "normaliza entre mercados") varre 2,5 / 5 / 10 - so para mostrar que, com o
    gatilho em percentil, k45 nao muda NADA (ele e um reescalonamento monotonico do mesmo numero);
  - EMAs (9/50, 20/100, 5/20), stop (1,0 / 1,5 / 2,5 ATR) e R:R (1 / 2 / 3);
  - lado (ambos / so long) e saida no flat (liga/desliga).

Para as melhores celulas rodo o controle de entrada aleatoria (mesmo lado, risco, estrutura e duracao)
e a divisao temporal 70/30, que e onde quase toda estrategia de grade grande morre.

uso: python study_tlangle_cal.py [xau]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import study_tlangle as T
from study_tlangle import BASE, build, run_asset, summ, load_m1, TFS

TFS.update({'5min': 5, '1D': 1440})

PCTS = [0, 50, 75, 90, 95]


def main(names):
    lines = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s, flush=True); lines.append(s)
    pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
    rows = []
    for name in names:
        m1 = load_m1(name)
        yrs = (m1.index[-1] - m1.index[0]).days / 365.25
        bh = (m1.close.iloc[-1] / m1.close.iloc[0]) ** (1 / yrs) - 1
        P(f'\n===== {name}: calibracao por mercado | {yrs:.1f} anos | buy&hold {bh * 100:+.1f}%/ano')
        P('-- |angulo| por TF e k45 (o gatilho de 20 graus do autor pega quanto do tempo?):')
        for TF in ['5min', '15min', '30min', '1h', '4h', '1D']:
            for K in (2.5, 5.0, 10.0):
                A = build(name, m1, dict(BASE, TF=TF, K45=K))
                a = np.abs(A['angR']); a = a[~np.isnan(a)]
                P(f'   {TF:>6} k45={K:<5} n={len(a):>7} mediana {np.median(a):5.1f} '
                  f'p90 {np.percentile(a, 90):5.1f} | barras com |a|>=20: {np.mean(a >= 20) * 100:5.1f}%'
                  f' | >=45: {np.mean(a >= 45) * 100:5.1f}%')
        P('\n-- k45 com gatilho em percentil: reescalonamento monotonico, nao muda nada '
          '(so confirmando que "normaliza entre mercados" nao e um grau de liberdade):')
        for TF in ['15min', '1h', '1D']:
            for PC in (50, 90):
                out = []
                for K in (2.5, 5.0, 10.0):
                    A = build(name, m1, dict(BASE, TF=TF, K45=K))
                    a = np.abs(A['angR']); a = a[~np.isnan(a)]
                    p = dict(BASE, TF=TF, K45=K, MINENTRY=float(np.percentile(a, PC)))
                    s = summ(run_asset(name, m1, p), yrs)
                    out.append(f'k45={K}: n={s["n"]} R_liq {s["R_liq"]:+.3f}')
                P(f'   {TF:>6} p{PC}: ' + ' | '.join(out))
        for TF, K, PC, EM, SM, RR, LS, EF in itertools.product(
                ['5min', '15min', '30min', '1h', '4h', '1D'], [5.0], PCTS,
                [(9, 50), (20, 100), (5, 20)], [1.0, 1.5, 2.5], [1.0, 2.0, 3.0], [1, 0], [1, 0]):
            A = build(name, m1, dict(BASE, TF=TF, K45=K, FAST=EM[0], SLOW=EM[1]))
            a = np.abs(A['angR']); a = a[~np.isnan(a)]
            me = 0.0 if PC == 0 else float(np.percentile(a, PC))
            p = dict(BASE, TF=TF, K45=K, MINENTRY=me, FAST=EM[0], SLOW=EM[1],
                     SLMULT=SM, RR=RR, SHORT=LS, EXITFLAT=EF)
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, K45=K, pct=PC, ang=round(me, 1), EMA=f'{EM[0]}/{EM[1]}',
                     SLMULT=SM, RR=RR, ambos=LS, EXITFLAT=EF)
            rows.append(s)
        g = pd.DataFrame(rows)
        g = g[g.ativo == name]
        cols = ['TF', 'K45', 'pct', 'ang', 'EMA', 'SLMULT', 'RR', 'ambos', 'EXITFLAT',
                'n', 'por_ano', 'acerto', 'risco_bp', 'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']
        P(f'\n-- {len(g)} combinacoes. R_liq > 0 em {(g.R_liq > 0).sum()}; '
          f'R_bruto > 0 em {(g.R_bruto > 0).sum()}; com n >= 100: '
          f'{((g.R_liq > 0) & (g.n >= 100)).sum()}/{(g.n >= 100).sum()}')
        P('\n-- media por TF:')
        P(g.groupby('TF')[['n', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']].mean().round(3).to_string())
        P('\n-- media por percentil do gatilho de angulo (0 = sem filtro de angulo):')
        P(g.groupby('pct')[['n', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']].mean().round(3).to_string())
        P('\n-- media por k45 (deve ser identica entre k45 com gatilho em percentil):')
        P(g.groupby(['pct', 'K45'])[['n', 'R_bruto', 'R_liq']].mean().round(3).to_string())
        P('\n-- media por lado (ambos=1 inclui short) e por saida no flat:')
        P(g.groupby(['ambos', 'EXITFLAT'])[['n', 'R_bruto', 'R_liq', 'R_ano']].mean().round(3).to_string())
        P('\n-- 25 melhores celulas por R/ano (n >= 100):')
        top = g[g.n >= 100].sort_values('R_ano', ascending=False).head(25)
        P(top[cols].round(3).to_string(index=False))
        P('\n-- as 5 melhores, com controle aleatorio e divisao temporal 70/30:')
        for _, r in top.head(5).iterrows():
            fa, sl = (int(x) for x in r.EMA.split('/'))
            p = dict(BASE, TF=r.TF, K45=r.K45, MINENTRY=r.ang, FAST=fa, SLOW=sl,
                     SLMULT=r.SLMULT, RR=r.RR, SHORT=int(r.ambos), EXITFLAT=int(r.EXITFLAT))
            df = run_asset(name, m1, p, ctrl=True, NR=max(2, min(20, 40000 // max(len(
                run_asset(name, m1, p)), 1))))
            d = df.R - df.ctrlR
            cut = df.tent.quantile(0.7)
            a = summ(df[df.tent <= cut], yrs * 0.7); b = summ(df[df.tent > cut], yrs * 0.3)
            P(f'   {r.TF} k45={r.K45} ang>={r.ang} EMA {r.EMA} sl={r.SLMULT} rr={r.RR} '
              f'ambos={int(r.ambos)} flat={int(r.EXITFLAT)}: n={len(df)} R_liq {df.net.mean():+.3f} '
              f'({df.net.sum() / yrs:+.1f} R/ano) | controle {df.ctrlR.mean():+.3f} vs {df.R.mean():+.3f}, '
              f'dif {d.mean():+.3f} (t={d.mean() / d.std() * np.sqrt(len(df)):.2f}) | '
              f'IS {a["R_liq"]:+.3f} (n={a["n"]}) OOS {b["R_liq"]:+.3f} (n={b["n"]}) | '
              f'Pine 5bp/perna {df.net_pine.mean():+.3f}')
    pd.DataFrame(rows).to_csv(os.path.join(D, 'scripts', 'study_tlangle_cal.csv'), index=False)
    with open(os.path.join(D, 'scripts', 'study_tlangle_cal.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
