"""Junta os study_hmm_*.csv em tabelas Markdown (results/hmm/resumo.md) e num CSV unico (results/hmm/resumo.csv)."""
import os, glob
import numpy as np, pandas as pd
import hmm_regime as H
OUT = os.path.join(H.D, 'results', 'hmm'); AT = ['xau', 'us100', 'wti', 'btc', 'eth']
PAR = [('bh_hmm', 'bh'), ('bh_rel', 'bh'), ('todas_hmm', 'todas'), ('todas_rel', 'todas'), ('k6_hmm', 'k6'), ('k6_rel', 'k6'),
       ('escolhe_hmm', 'escolhe_sem_regime')]
ROT = {'bh_hmm': 'B&H só se E>0', 'bh_rel': 'B&H só no regime bom', 'todas_hmm': 'todas, liga se E>0', 'todas_rel': 'todas, liga no regime bom',
       'k6_hmm': 'K6, liga se E>0', 'k6_rel': 'K6, liga no regime bom', 'escolhe_hmm': 'escolhe por regime',
       'info_bh': 'informação, ativo', 'info_todas': 'informação, estratégias'}
f = lambda v: '' if pd.isna(v) else f'{v:+.2f}'.replace('.', ',')
o = pd.concat([pd.read_csv(x) for x in glob.glob(os.path.join(OUT, 'study_*_[DW]_K?.csv'))], ignore_index=True)
o.to_csv(os.path.join(OUT, 'resumo.csv'), index=False)
L = []
for per, tit in (('valid', 'Validação (partes 7–9)'), ('oos', 'OOS (parte 10)')):
    L += [f'### {tit}: Sharpe do uso com HMM menos Sharpe do controle sem regime', '',
          'Cada célula: diferença mediana de Sharpe nas 4 versões do HMM (diário/semanal × 2/3 estados) · em quantas das 4 o HMM ganhou do controle · '
          'percentil mediano contra os placebos (regimes deslocados no tempo; 50 = igual ao acaso, ≥ 90 = sinal).', '',
          '| Uso | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|' + '---|' * len(AT)]
    for t, b in PAR:
        cel = []
        for a in AT:
            x = o[(o.ativo == a) & (o.periodo == per)]
            if x.empty: cel.append('—'); continue
            m = x[x.teste == t].merge(x[x.teste == b][['freq', 'K', 'sharpe']], on=['freq', 'K'], suffixes=('', '_c'))
            d = m.sharpe - m.sharpe_c
            cel.append(f'{f(d.median())} · {int((d > 0).sum())}/{len(d)} · p{int(round(100 * m.placebo_pct.median()))}')
        L.append(f'| {ROT[t]} | ' + ' | '.join(cel) + ' |')
    L += ['', f'### {tit}: informação do regime (retorno a.a. nos dias de regime bom menos nos de regime ruim)', '',
          '| Medida | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|' + '---|' * len(AT)]
    for t in ('info_bh', 'info_todas'):
        cel = []
        for a in AT:
            x = o[(o.ativo == a) & (o.periodo == per) & (o.teste == t)]
            cel.append('—' if x.empty else f'{f(x.ret.median())} · p{int(round(100 * x.placebo_pct.median()))}')
        L.append(f'| {ROT[t]} | ' + ' | '.join(cel) + ' |')
    L.append('')
# controles (sem regime), para referencia
L += ['### Controles sem regime (Sharpe)', '', '| Carteira | Período | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|---|' + '---|' * len(AT)]
for b in ('bh', 'todas', 'k6', 'escolhe_sem_regime'):
    for per in ('valid', 'oos'):
        cel = []
        for a in AT:
            x = o[(o.ativo == a) & (o.periodo == per) & (o.teste == b)]
            cel.append('—' if x.empty else f(x.sharpe.iloc[0]))
        L.append(f'| {b} | {per} | ' + ' | '.join(cel) + ' |')
# regime da propria estrategia
pp = [pd.read_csv(x) for x in glob.glob(os.path.join(OUT, 'study_*_propria.csv'))]
if pp:
    p = pd.concat(pp, ignore_index=True)
    L += ['', '### Regime da própria estratégia (HMM 1-D no retorno de cada uma) — Sharpe', '',
          '| Carteira | Período | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|---|' + '---|' * len(AT)]
    for t in ('todas', 'todas_propria_hmm', 'todas_propria_rel', 'todas_media60', 'k6', 'k6_propria_hmm', 'k6_propria_rel', 'k6_media60', 'info_propria', 'info_media60'):
        for per in ('valid', 'oos'):
            cel = []
            for a in AT:
                x = p[(p.ativo == a) & (p.periodo == per) & (p.teste == t)]
                cel.append('—' if x.empty else f(x.ret.iloc[0] if t.startswith('info') else x.sharpe.iloc[0]))
            L.append(f'| {t} | {per} | ' + ' | '.join(cel) + ' |')
open(os.path.join(OUT, 'resumo.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))

# validacao x OOS: percentil contra os placebos de cada combinacao (uso, ativo, versao do HMM)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
x = o[o.placebo_pct.notna() & ~o.teste.str.startswith('info')].pivot_table(index=['teste', 'ativo', 'freq', 'K'], columns='periodo', values='placebo_pct')
x = x.dropna(); r = np.corrcoef(x.valid, x.oos)[0, 1]
fig, ax = plt.subplots(figsize=(6.2, 5.6), facecolor='#fcfcfb'); ax.set_facecolor('#fcfcfb')
ax.axvspan(0.9, 1.02, color='#e4e3df', alpha=0.5, lw=0); ax.axhspan(0.9, 1.02, color='#e4e3df', alpha=0.5, lw=0)
ax.scatter(x.valid, x.oos, s=34, color='#2a78d6', edgecolor='#fcfcfb', linewidth=1.5, zorder=3)
ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
ax.set_xlabel('validação: fração dos placebos abaixo', color='#52514e', fontsize=9); ax.set_ylabel('OOS: fração dos placebos abaixo', color='#52514e', fontsize=9)
ax.set_title(f'Cada ponto: um uso × ativo × versão do HMM ({len(x)})\ncorrelação validação × OOS = {r:+.2f}', color='#0b0b0b', fontsize=10, loc='left')
ax.text(0.91, 0.97, 'sinal nos dois\nperíodos', color='#52514e', fontsize=8, va='top'); ax.tick_params(colors='#52514e', labelsize=8)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
for sp in ('left', 'bottom'): ax.spines[sp].set_color('#e4e3df')
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'placebo_valid_oos.png'), dpi=110)
print(f'{len(x)} combinacoes; corr validacao x OOS dos percentis = {r:+.2f}; acima de 0,9 nos dois: {int(((x.valid >= 0.9) & (x.oos >= 0.9)).sum())}; '
      f'so na validacao: {int(((x.valid >= 0.9) & (x.oos < 0.9)).sum())}; so no OOS: {int(((x.valid < 0.9) & (x.oos >= 0.9)).sum())}')
