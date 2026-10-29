"""Compras e vendas separadas pelo regime: em alta so os trades comprados de cada estrategia, em baixa so os vendidos.
Regimes das regras simples (study_regime_simples.py: mm200, cruz, mom12, dd20); series so-compras e so-vendas de cada
celula geradas com LADO=1 FULL=1 python study_us100_4p.py N -> results/<ATIVO>_4p_8p_lado/lote*_ser{L,S}.parquet
(as duas juntas reproduzem a serie original: (1 + L)(1 + S) - 1).
Mesmo corte do tvo.py (10 partes; 1-6 treino, 7-9 validacao, 10 OOS) e placebos com o regime deslocado no tempo.
  todas_lado / k6_lado  as aprovadas no treino (todas, peso igual, e a K=6 teto 0,3), cada uma so com a ponta a favor
        do regime. Controles: as mesmas com as duas pontas sempre.
  escolhe_lado  todo mes, as 6 aprovadas com melhor Sharpe das compras nos dias de alta passados e as 6 com melhor
        Sharpe das vendas nos dias de baixa passados (teto de correlacao 0,3); no dia, o grupo do regime vigente.
        Controle: escolhe_sem_regime (as 6 de maior Sharpe no passado, duas pontas).
  sel_lado  aprovacao separada no treino: compras de todas as celulas medidas so nos dias de alta e vendas so nos de
        baixa (geo > 0, >= 2/3 das partes com >= 20 dias do regime positivas, sem a melhor parte > 0, >= 50 trades da
        ponta no treino), melhor celula por estrategia, K=6 teto 0,3 em cada ponta. Controle: k6. No placebo a escolha
        e refeita com o regime deslocado.
  info_lado  media, entre as aprovadas, de (compras em alta - compras em baixa) + (vendas em baixa - vendas em alta),
        em retorno a.a.; zero = o regime nao diz qual ponta rende.
Troca de regime: cada estrategia paga duas pernas de CUSTO (fecha uma ponta, abre a outra).
uso: python study_lado.py [ativos]   -> results/lado/   |   python study_lado.py resumo"""
import os, sys, glob, json
import numpy as np, pandas as pd
import hmm_regime as H
import study_hmm as S
import study_regime_simples as RS
from study_engulf_psar import CUSTO
D = H.D; OUT = os.path.join(D, 'results', 'lado'); os.makedirs(OUT, exist_ok=True)
AT = RS.AT; REGRAS = RS.REGRAS; NSEL, TETO, N0 = 6, 0.3, 30
NPLAC = int(os.environ.get('NPLAC', '100')); MINTR_LADO, MINDIAS = 50, 20


def lados(A):
    """(cal, Lall, Sall, cel): series so-compras e so-vendas de todas as celulas (datas x celulas, float32) no calendario
    uniao, e a tabela das celulas (key, lote, est, trL_treino, trS_treino), sem templates nem peek, na ordem das colunas."""
    R0 = os.path.join(D, 'results', A + '_4p_8p_lado')
    RK = os.path.join(D, 'results', A + '_4p_8p_full', 'ranking.csv'); RK = RK if os.path.exists(RK) else os.path.join(D, 'results', 'wti_4p_8p_full', 'ranking.csv')
    nomes = pd.read_csv(RK).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()
    cel, SL, SS, ser = [], [], [], {}
    for f in sorted(glob.glob(os.path.join(R0, 'lote*.csv'))):
        l = os.path.basename(f)[4:-4]; g = pd.read_csv(f); b = l.split('_')[0]
        if 'sid' not in g or not os.path.exists(os.path.join(R0, f'lote{b}_serS.parquet')): continue
        g['est'] = g['est'].fillna(l) if 'est' in g else l
        g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
        if b not in ser:
            ser[b] = [pd.read_parquet(os.path.join(R0, f'lote{b}_ser{x}.parquet')) for x in 'LS']
            for x in ser[b]: x.index = S.naive(x.index); x.columns = x.columns.astype(str)
        for _, r in g.iterrows():
            k = str(int(r.sid)); cel.append(dict(key=f'{l}|{r.est}|{k}', lote=l, est=r.est, nome=nomes.get((l, r.est), ''),
                                                 trL_treino=r.trL_treino, trS_treino=r.trS_treino))
            SL.append(ser[b][0][k]); SS.append(ser[b][1][k])
    cel = pd.DataFrame(cel); ok = ~cel.nome.fillna('').astype(str).str.contains('Example|Template', case=False).values
    cal = pd.DatetimeIndex(sorted(set().union(*[set(x[0].index) for x in ser.values()])))
    M = lambda L: np.column_stack([x.reindex(cal).fillna(0.0).to_numpy(np.float32) for x, o in zip(L, ok) if o])
    return cal, M(SL), M(SS), cel[ok].reset_index(drop=True)


def seleciona(Lg, al, c6i, parts, trn, grp, C):
    """Aprovacao de uma ponta medida so nos dias do regime (al: mascara de datas) do treino; devolve ate NSEL colunas
    (melhor celula por estrategia, ordem da geo, teto de correlacao TETO nos dias do regime do treino)."""
    m = al[:c6i]; nd = np.array([m[b:e].sum() for b, e in parts]); el = nd >= MINDIAS
    if el.sum() < 3: return []
    Mp = np.zeros((c6i, int(el.sum())), np.float32)
    for q, (b, e) in enumerate(pe for pe, v in zip(parts, el) if v): Mp[b:e, q] = m[b:e]
    P = (Lg[:c6i].T @ Mp).astype(float)   # celulas x partes elegiveis: soma dos log-retornos nos dias do regime
    geo = P.mean(1); npos = (P > 0).sum(1); sem = P.sum(1) - P.max(1)
    ok = (geo > 0) & (npos >= np.ceil(2 / 3 * P.shape[1])) & (sem > 0) & (trn >= MINTR_LADO)
    i = np.where(ok)[0]
    if not len(i): return []
    t = pd.DataFrame(dict(i=i, g=grp[i], geo=geo[i])).sort_values('geo', ascending=False).drop_duplicates('g')
    s, z = [], {}
    for j in t.i:
        if len(s) == NSEL: break
        z[j] = C[:c6i, j][m].astype(float)
        if z[j].std() == 0: continue
        if all(np.corrcoef(z[j], z[q])[0, 1] < TETO for q in s): s.append(j)
    return s


def roda(A, rng):
    R, a, k6, c = S.aprovadas(A); cu = CUSTO[A]
    cal, Lall, Sall, cel = lados(A)
    R = R.reindex(cal).fillna(0.0); Rv = R.to_numpy(); kpos = {k: i for i, k in enumerate(cel.key)}
    ia = [kpos[k] for k in a.key]; La, Sa = Lall[:, ia].astype(float), Sall[:, ia].astype(float); i6 = [list(a.key).index(k) for k in k6]
    err = np.abs((1 + La) * (1 + Sa) - 1 - Rv).max()
    per = {'valid': (c[6], c[9]), 'oos': (c[9], c[10] + pd.Timedelta(days=1))}
    mk = {p: (cal >= i0) & (cal < i1) for p, (i0, i1) in per.items()}
    ppy = {p: m.sum() / ((cal[m][-1] - cal[m][0]).days / 365) for p, m in mk.items()}
    c6i = int(np.searchsorted(cal.values, np.datetime64(c[6]))); cut = [int(np.searchsorted(cal.values, np.datetime64(x))) for x in c[:7]]
    parts = list(zip(cut[:-1], cut[1:]))
    Lg, Sg = np.log1p(np.clip(Lall, -0.999, None)), np.log1p(np.clip(Sall, -0.999, None))
    grp = (cel.lote.str.split('_').str[0] + '|' + cel.est.astype(str)).to_numpy()
    tL, tS = cel.trL_treino.to_numpy(), cel.trS_treino.to_numpy()
    Cb = Lall.astype(np.float32) + Sall   # aproximacao da serie das duas pontas, so para as correlacoes da aprovacao
    CSd = {}; W0 = None; rows = []

    def regime_cal(X, Q, ms, shift):
        q = Q[ms[0]]; q = np.roll(q, shift, axis=0) if shift else q
        pos = np.searchsorted(X.index.values, cal.values, side='left') - 1
        al = np.full(len(cal), np.nan); v = pos >= 0; al[v] = q[pos[v], 1]
        return al

    def testes(G, al, shift):
        A1 = al == 1; B1 = al == 0; ind = ~(A1 | B1)   # indefinido (antes do aquecimento) = duas pontas
        sw = np.abs(np.diff(A1.astype(float), prepend=A1[0]))
        lado = np.where(A1[:, None], La, np.where(B1[:, None], Sa, Rv)) - 2 * cu * sw[:, None]
        s = {'todas_lado': lado.mean(1), 'k6_lado': lado[:, i6].mean(1)}
        # escolhe por ponta: todo mes, Sharpe das compras nos dias de alta e das vendas nos de baixa, so com o passado
        W = np.zeros((len(cal), 2 * len(ia)))
        for j in range(len(G.ms)):
            b, e = G.b[j], G.b[j + 1]
            if b == 0: continue
            for col, msk, Z in ((0, A1[:b], La[:b]), (1, B1[:b], Sa[:b])):
                zz = Z[msk] if msk.sum() >= N0 else Z
                m = zz.mean(0); sc = m / (zz.std(0) + 1e-12)
                ix = S.guloso(sc, CS[j]); reg = A1[b:e] if col == 0 else B1[b:e]
                for q in ix: W[b:e, col * len(ia) + q] = reg / NSEL
            W[b:e][ind[b:e]] = 0.0
        RW = np.hstack([La, Sa]); s['escolhe_lado'] = S.ret_pesos(RW, W, cu)
        # aprovacao separada por ponta (refeita a cada deslocamento)
        sl = seleciona(Lg, A1, c6i, parts, tL, grp, Cb); ss = seleciona(Sg, B1, c6i, parts, tS, grp, Cb)
        rl = Lall[:, sl].astype(float).mean(1) if sl else np.zeros(len(cal)); rs = Sall[:, ss].astype(float).mean(1) if ss else np.zeros(len(cal))
        s['sel_lado'] = np.where(A1, rl, np.where(B1, rs, 0.0)) - 2 * cu * sw
        out = {(t, p): r[mk[p]] for t, r in s.items() for p in per}
        for p in per:
            m = mk[p]; d = []
            for n in range(len(ia)):
                x = [(La[m & A1, n], La[m & B1, n]), (Sa[m & B1, n], Sa[m & A1, n])]
                if all(len(u) >= 20 and len(v) >= 20 for u, v in x): d.append(sum(u.mean() - v.mean() for u, v in x) * ppy[p])
            out[('info_lado', p)] = float(np.mean(d)) if d else np.nan
        return out, dict(n_sel_L=len(sl), n_sel_S=len(ss), sel_L=[cel.est[i] for i in sl], sel_S=[cel.est[i] for i in ss])

    for r in REGRAS:
        X, ms, Q = RS.regime(A, r); G = S.Reg(X, ms, Q, cal).prep(Rv)
        for j, M in enumerate(G.ms):
            if M not in CSd: CSd[M] = np.nan_to_num(np.corrcoef(Rv[:G.b[j]].T))
        CS = [CSd[M] for M in G.ms]
        if W0 is None: W0 = S.escolhe(Rv, G, CS, cond=False)   # so meses antes de cada data: igual para qualquer regra na validacao e no OOS
        real, inf = testes(G, regime_cal(X, Q, ms, 0), 0); plac = {}
        for _ in range(NPLAC):
            sh = int(rng.integers(len(X) // 10, len(X) - len(X) // 10))
            o, _ = testes(G, regime_cal(X, Q, ms, sh), sh)
            for k, v in o.items(): plac.setdefault(k, []).append(v if k[0].startswith('info') else S.st(pd.Series(v, index=cal[mk[k[1]]]))['sharpe'])
        base = {'todas': Rv.mean(1), 'k6': Rv[:, i6].mean(1), 'escolhe_sem_regime': S.ret_pesos(Rv, W0, cu)}
        for p in per:
            for t, v in base.items(): rows.append(dict(regra=r, teste=t, periodo=p, **S.st(pd.Series(v[mk[p]], index=cal[mk[p]]))))
            for (t, q), v in real.items():
                if q != p: continue
                pl = np.array(plac[(t, q)])
                if t.startswith('info'): rows.append(dict(regra=r, teste=t, periodo=p, ret=v, placebo_med=np.nanmedian(pl), placebo_pct=S.pct(pl, v)))
                else:
                    s = S.st(pd.Series(v, index=cal[mk[p]])); rows.append(dict(regra=r, teste=t, periodo=p, **s, placebo_med=np.median(pl), placebo_pct=S.pct(pl, s['sharpe'])))
        print(f'\n== {A} {r}: {inf}'); sys.stdout.flush()
    o = pd.DataFrame(rows); o.insert(0, 'ativo', A)
    return o, dict(n_aprovadas=len(a), celulas=len(cel), erro_max_L_S=float(err))


def resumo():
    o = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(OUT, 'study_*.csv'))], ignore_index=True)
    o.to_csv(os.path.join(OUT, 'resumo.csv'), index=False)
    f = lambda v: '' if pd.isna(v) else f'{v:+.2f}'.replace('.', ',').replace('-', '−')
    pp = lambda v: 'p—' if pd.isna(v) else f'p{int(round(100 * v))}'
    PAR = [('todas_lado', 'todas', 'todas as aprovadas'), ('k6_lado', 'k6', 'K6 das aprovadas'),
           ('escolhe_lado', 'escolhe_sem_regime', 'escolhe por ponta'), ('sel_lado', 'k6', 'aprovação por ponta')]
    L = []
    for per, tit in (('valid', 'Validação (partes 7–9)'), ('oos', 'OOS (parte 10)')):
        L += [f'### {tit}: Sharpe só com a ponta a favor do regime menos Sharpe com as duas pontas', '',
              'Cada célula: mediana nas 4 regras · em quantas das 4 ganhou do controle · percentil mediano contra os placebos.', '',
              '| Uso | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|' + '---|' * len(AT)]
        for t, b, rot in PAR:
            cel = []
            for a in AT:
                x = o[(o.ativo == a) & (o.periodo == per)]
                m = x[x.teste == t].merge(x[x.teste == b][['regra', 'sharpe']], on='regra', suffixes=('', '_c')); d = m.sharpe - m.sharpe_c
                cel.append('—' if m.empty else f'{f(d.median())} · {int((d > 0).sum())}/{len(d)} · {pp(m.placebo_pct.median())}')
            L.append(f'| {rot} | ' + ' | '.join(cel) + ' |')
        cel = []
        for a in AT:
            x = o[(o.ativo == a) & (o.periodo == per) & (o.teste == 'info_lado')]
            cel.append('—' if x.ret.notna().sum() == 0 else f'{f(x.ret.median())} · {int((x.ret > 0).sum())}/{int(x.ret.notna().sum())} · {pp(x.placebo_pct.median())}')
        L += [f'| informação (a.a.) | ' + ' | '.join(cel) + ' |', '']
    L += ['### Regra a regra (Sharpe do uso − controle · percentil contra placebos)', '',
          '| Uso | Regra | Período | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|---|---|' + '---|' * len(AT)]
    for t, b, rot in PAR:
        for r in REGRAS:
            for per in ('valid', 'oos'):
                cel = []
                for a in AT:
                    x = o[(o.ativo == a) & (o.periodo == per) & (o.regra == r)]; e, c = x[x.teste == t], x[x.teste == b]
                    cel.append('—' if e.empty else f'{f(e.sharpe.iloc[0] - c.sharpe.iloc[0])} · {pp(e.placebo_pct.iloc[0])}')
                L.append(f'| {rot} | {r} | {per} | ' + ' | '.join(cel) + ' |')
    L += ['', '### Controles (Sharpe)', '', '| Carteira | Período | ' + ' | '.join(a.upper() for a in AT) + ' |', '|---|---|' + '---|' * len(AT)]
    for b in ('todas', 'k6', 'escolhe_sem_regime'):
        for per in ('valid', 'oos'):
            L.append(f'| {b} | {per} | ' + ' | '.join('—' if (x := o[(o.ativo == a) & (o.periodo == per) & (o.teste == b)]).empty else f(x.sharpe.iloc[0]) for a in AT) + ' |')
    x = o[o.placebo_pct.notna()].pivot_table(index=['teste', 'ativo', 'regra'], columns='periodo', values='placebo_pct').dropna()
    L += ['', f'{len(x)} combinações (uso × ativo × regra, com a informação): acima de 90% dos placebos na validação {int((x.valid >= 0.9).sum())}, '
          f'nos dois períodos {int(((x.valid >= 0.9) & (x.oos >= 0.9)).sum())}; correlação validação × OOS dos percentis {f(np.corrcoef(x.valid, x.oos)[0, 1])}.']
    open(os.path.join(OUT, 'resumo.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))


if __name__ == '__main__':
    if sys.argv[1:] == ['resumo']: resumo(); sys.exit()
    rng = np.random.default_rng(13)
    for A in (sys.argv[1:] or AT):
        o, inf = roda(A, rng); o.to_csv(os.path.join(OUT, f'study_{A}.csv'), index=False)
        print(f'\n== {A}: {inf}'); print(o.drop(columns='ativo').to_string(index=False, float_format=lambda v: f'{v:+.2f}')); sys.stdout.flush()
    resumo()
