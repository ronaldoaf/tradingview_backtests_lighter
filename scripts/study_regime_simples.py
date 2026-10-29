"""Regras simples de regime de alta/baixa (sem HMM), no mesmo motor do study_hmm.py (aprovadas no treino do tvo.py,
medias condicionais reestimadas todo mes so com o passado, controle sem regime, placebos com o regime deslocado).
  mm200  alta se o fechamento > media dos ultimos 200 pregoes
  cruz   alta se a media de 50 pregoes > media de 200
  mom12  alta se o fechamento > fechamento de 365 dias corridos antes
  dd20   baixa se o fechamento < 80% da maxima dos ultimos 365 dias corridos
O regime e decidido no fechamento do pregao d e vale a partir do dia seguinte (mesmo mapeamento do HMM).
Estados: 0 = baixa, 1 = alta. Os usos sao os do study_hmm (nomes com _reg no lugar de _hmm) mais bh_regra: comprado
so em alta. O principal e escolhe_reg: todo mes as 6 melhores no historico de alta e as 6 melhores no de baixa; no dia,
a carteira do regime vigente.
uso: python study_regime_simples.py [ativos]   -> results/regime_simples/ (ao final refaz resumo.md, resumo.csv e o grafico)
     python study_regime_simples.py resumo     -> so as tabelas e o grafico, a partir dos CSVs ja gerados"""
import os, sys, glob
import numpy as np, pandas as pd
import hmm_regime as H
import study_hmm as S
OUT = os.path.join(H.D, 'results', 'regime_simples'); os.makedirs(OUT, exist_ok=True)
REGRAS = ['mm200', 'cruz', 'mom12', 'dd20']; AT = ['xau', 'us100', 'wti', 'btc', 'eth']; MINHIST = 250


def regime(A, nome):
    """(X, meses, Q): Q[M] = indicadora (pregoes x 2) do regime vigente no fechamento de cada pregao, igual em todo mes."""
    x = H.features(A); c = x.close
    if nome == 'mm200': alta, ok = c > c.rolling(200).mean(), c.rolling(200).count() == 200
    elif nome == 'cruz': alta, ok = c.rolling(50).mean() > c.rolling(200).mean(), c.rolling(200).count() == 200
    else:
        ok = pd.Series(c.index >= c.index[0] + pd.Timedelta(days=365), c.index)
        if nome == 'mom12': alta = c > c.asof(c.index - pd.Timedelta(days=365)).values
        else: alta = c >= 0.8 * c.rolling('365D').max()
    X = x[ok.values]; a = alta[ok.values].values.astype(float); q = np.column_stack([1 - a, a])
    ms = [M for M in pd.date_range(X.index[0].to_period('M').to_timestamp(), X.index[-1], freq='MS')[1:] if (X.index < M).sum() >= MINHIST]
    return X, ms, {M: q for M in ms}


def resumo():
    o = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(OUT, 'study_*.csv'))], ignore_index=True)
    o.to_csv(os.path.join(OUT, 'resumo.csv'), index=False)
    f = lambda v: '' if pd.isna(v) else f'{v:+.2f}'.replace('.', ',')
    PAR = [('bh_regra', 'bh', 'B&H só em alta'), ('bh_rel', 'bh', 'B&H só no regime bom'), ('todas_reg', 'todas', 'todas, liga se E>0'),
           ('todas_rel', 'todas', 'todas, liga no regime bom'), ('k6_rel', 'k6', 'K6, liga no regime bom'),
           ('escolhe_reg', 'escolhe_sem_regime', 'escolhe por regime')]
    L = []
    for per, tit in (('valid', 'Validação (partes 7–9)'), ('oos', 'OOS (parte 10)')):
        L += [f'### {tit}: Sharpe com a regra menos Sharpe do controle sem regime', '',
              'Cada célula: mediana nas 4 regras · em quantas das 4 a regra ganhou do controle · percentil mediano contra os placebos.', '',
              '| Uso | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|' + '---|' * len(AT)]
        for t, b, rot in PAR:
            cel = []
            for a in AT:
                x = o[(o.ativo == a) & (o.periodo == per)]
                m = x[x.teste == t].merge(x[x.teste == b][['regra', 'sharpe']], on='regra', suffixes=('', '_c'))
                d = m.sharpe - m.sharpe_c
                cel.append('—' if m.empty else f'{f(d.median())} · {int((d > 0).sum())}/{len(d)} · p{int(round(100 * m.placebo_pct.median()))}')
            L.append(f'| {rot} | ' + ' | '.join(cel) + ' |')
        L.append('')
    L += ['### Escolher por regime, regra a regra (Sharpe do uso − controle · percentil contra placebos)', '',
          '| Regra | Período | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|---|' + '---|' * len(AT)]
    for r in REGRAS:
        for per in ('valid', 'oos'):
            cel = []
            for a in AT:
                x = o[(o.ativo == a) & (o.periodo == per) & (o.regra == r)]
                e, c = x[x.teste == 'escolhe_reg'], x[x.teste == 'escolhe_sem_regime']
                cel.append('—' if e.empty else f'{f(e.sharpe.iloc[0] - c.sharpe.iloc[0])} · p{int(round(100 * e.placebo_pct.iloc[0]))}')
            L.append(f'| {r} | {per} | ' + ' | '.join(cel) + ' |')
    x = o[o.placebo_pct.notna() & ~o.teste.str.startswith('info')].pivot_table(index=['teste', 'ativo', 'regra'], columns='periodo', values='placebo_pct').dropna()
    L += ['', f'{len(x)} combinações (uso × ativo × regra): acima de 90% dos placebos na validação {int((x.valid >= 0.9).sum())}, '
          f'nos dois períodos {int(((x.valid >= 0.9) & (x.oos >= 0.9)).sum())}; correlação validação × OOS dos percentis {f(np.corrcoef(x.valid, x.oos)[0, 1])}.']
    open(os.path.join(OUT, 'resumo.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.2, 5.6), facecolor='#fcfcfb'); ax.set_facecolor('#fcfcfb')
    ax.axvspan(0.9, 1.02, color='#e4e3df', alpha=0.5, lw=0); ax.axhspan(0.9, 1.02, color='#e4e3df', alpha=0.5, lw=0)
    ax.scatter(x.valid, x.oos, s=34, color='#2a78d6', edgecolor='#fcfcfb', linewidth=1.5, zorder=3)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel('validação: fração dos placebos abaixo', color='#52514e', fontsize=9); ax.set_ylabel('OOS: fração dos placebos abaixo', color='#52514e', fontsize=9)
    ax.set_title(f'Cada ponto: um uso × ativo × regra ({len(x)})\ncorrelação validação × OOS = {f(np.corrcoef(x.valid, x.oos)[0, 1])}', color='#0b0b0b', fontsize=10, loc='left')
    ax.text(0.91, 0.97, 'sinal nos dois\nperíodos', color='#52514e', fontsize=8, va='top'); ax.tick_params(colors='#52514e', labelsize=8)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color('#e4e3df')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'placebo_valid_oos.png'), dpi=110)


if __name__ == '__main__':
    if sys.argv[1:] == ['resumo']: resumo(); sys.exit()
    rng = np.random.default_rng(11)
    for A in (sys.argv[1:] or AT):
        for r in REGRAS:
            X, ms, Q = regime(A, r); a = Q[ms[0]][:, 1]; tr = np.abs(np.diff(a)).sum() / ((X.index[-1] - X.index[0]).days / 365)
            o, inf = S.avalia(A, X, ms, Q, rng, bh_estado=1)
            o['teste'] = o.teste.str.replace('_hmm', '_reg'); o.insert(1, 'regra', r); o.to_csv(os.path.join(OUT, f'study_{A}_{r}.csv'), index=False)
            print(f'\n== {A} {r}: alta em {a.mean():.0%} dos pregoes, {tr:.1f} trocas/ano, regime desde {X.index[0]:%Y-%m-%d}')
            print(o.drop(columns=['ativo', 'regra']).to_string(index=False, float_format=lambda v: f'{v:+.2f}')); sys.stdout.flush()
    resumo()
