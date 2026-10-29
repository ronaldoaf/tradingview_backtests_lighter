"""HMM de regime aplicado as estrategias aprovadas no treino (mesmo corte do tvo.py: 10 partes, 1-6 treino, 7-9 validacao,
10 OOS). Tudo walk-forward: o HMM (hmm_regime.py) e as medias condicionais de cada estrategia sao reestimados no comeco
de cada mes so com as datas anteriores.

Para cada estrategia (e para o proprio ativo) E = media condicional prevista = sum_k P(regime k previsto) * media
historica da estrategia no regime k (pesos = probabilidade prevista em cada data passada); E0 = media sem regime.
Usos testados, cada um contra o controle sem regime e contra placebos (a serie de regimes deslocada no tempo, que mantem
persistencia e frequencia dos estados mas perde a ligacao com o mercado):
  bh_hmm / bh_rel   comprado quando E > 0 / quando E > E0 (regime melhor que a media); senao caixa.
  *_hmm   cada estrategia ligada so quando E > 0. Carteiras: todas as aprovadas com peso igual e a K=6 teto 0,3 do tvo.
  *_rel   cada estrategia ligada so quando E > E0 (desliga no regime em que ela rende abaixo da propria media).
  escolhe_hmm  todo mes, para cada regime, as NSEL de maior Sharpe condicional (> 0) com teto de correlacao; no dia,
         mistura as carteiras dos regimes pela probabilidade prevista. Controle: a mesma escolha mensal sem regime.
  propria   regime da PROPRIA estrategia: HMM 1-D de 2 estados no retorno diario de cada uma (reajuste trimestral,
          janela expansiva); liga quando a media prevista pelo filtro > 0 (_hmm) ou > media sem regime (_rel).
          Controle simples: liga quando a media dos ultimos 60 dias > 0 (media60).
  info    medida direta: media, entre as estrategias aprovadas, de (retorno medio a.a. nos dias com E > E0) - (nos dias
          com E <= E0). Zero = o regime nao diz nada sobre quando a estrategia funciona.
Custo: cada troca liga/desliga paga uma perna de CUSTO (conservador: supoe a estrategia posicionada); no escolhe, o giro
dos pesos paga CUSTO. Funding do B&H pro-rata por dia corrido.
uso: python study_hmm.py [ativos]   (HMM diario e semanal, K em {2, 3}; NPLAC placebos)"""
import os, sys, glob, json
import numpy as np, pandas as pd
import hmm_regime as H
import tvlib as T
from study_engulf_psar import CUSTO, FUND
D = H.D; OUT = os.path.join(D, 'results', 'hmm')
NSEL, TETO, N0 = 6, 0.3, 30
NPLAC = int(os.environ.get('NPLAC', '100')); MINTR = 100


def naive(i): i = pd.DatetimeIndex(i); return i.tz_localize(None) if i.tz is not None else i


def aprovadas(A):
    """Reproduz a aprovacao do tvo.py (so treino) e devolve (R: retornos diarios do periodo todo das aprovadas,
    a: tabela das aprovadas na ordem da geo, k6: chaves da carteira K=6 teto 0,3, cortes)."""
    fp, fa, fc = (os.path.join(H.CACHE, f'apr_{A}.{x}') for x in ('parquet', 'csv', 'json'))
    if os.path.exists(fc):
        j = json.load(open(fc)); return pd.read_parquet(fp), pd.read_csv(fa), j['k6'], [pd.Timestamp(x) for x in j['c']]
    R0 = os.path.join(D, 'results', A + '_4p_8p_full')
    m1 = T.load_m1v(A); t0, t1 = m1.index[0], m1.index[-1]; c = [(t0 + (t1 - t0) * k / 10) for k in range(11)]; del m1
    c = [x.tz_localize(None) if x.tz is not None else x for x in c]
    RK = os.path.join(R0, 'ranking.csv'); RK = RK if os.path.exists(RK) else os.path.join(D, 'results', 'wti_4p_8p_full', 'ranking.csv')
    nomes = pd.read_csv(RK).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()
    rows, SER = [], {}
    for f in sorted(glob.glob(os.path.join(R0, 'lote*.csv'))):
        l = os.path.basename(f)[4:-4]; g = pd.read_csv(f)
        fs = os.path.join(R0, f'lote{l.split("_")[0]}_ser.parquet')
        if 'sid' not in g or not os.path.exists(fs): continue
        g['est'] = g['est'].fillna(l) if 'est' in g else l
        g = g[~(g.get('cfg', pd.Series('', g.index)).astype(str).eq('peek') | g.get('tag', pd.Series('', g.index)).astype(str).str.contains('peek'))]
        S = pd.read_parquet(fs); S.index = naive(S.index); S = S.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        tr = S[S.index < c[6]]; lg = np.log1p(tr.clip(lower=-0.999))
        parts = pd.DataFrame({q: lg[(lg.index >= c[q]) & (lg.index < c[q + 1])].sum() for q in range(6)})
        for _, r in g.iterrows():
            k = str(int(r.sid)) if str(int(r.sid)) in S else int(r.sid)
            p = parts.loc[k].values; key = f'{l}|{r.est}|{int(r.sid)}'
            rows.append(dict(lote=l, est=r.est, celula=' '.join(str(r[x]) for x in ('TF', 'cfg') if x in r and pd.notna(r[x])), key=key,
                             geo=np.expm1(p.mean()), n_pos=int((p > 0).sum()), sem_melhor=np.expm1(p.sum() - p.max()), trades=r.trades))
            SER[key] = S[k]
    g = pd.DataFrame(rows); g['nome'] = [nomes.get((l, e), '') for l, e in zip(g.lote, g.est)]
    g = g[~g.nome.fillna('').astype(str).str.contains('Example|Template', case=False)]
    ok = (g.geo > 0) & (g.n_pos >= 4) & (g.sem_melhor > 0) & (g.trades >= MINTR)
    a = g[ok].sort_values('geo', ascending=False).drop_duplicates(['lote', 'est']).reset_index(drop=True)
    R = pd.DataFrame({k: SER[k] for k in a.key}).fillna(0.0).sort_index()
    C = R[R.index < c[6]].corr().to_numpy(); s = []
    for i in range(len(a)):
        if all(C[i, j] < 0.3 for j in s): s.append(i)
        if len(s) == 6: break
    k6 = list(a.key[s]); R.columns = R.columns.astype(str)
    R.to_parquet(fp); a.to_csv(fa, index=False); json.dump(dict(k6=k6, c=[str(x) for x in c]), open(fc, 'w'))
    return R, a, k6, c


def st(r):
    r = r.dropna(); eq = (1 + r).cumprod(); anos = (r.index[-1] - r.index[0]).days / 365
    sd = r.std(); sh = r.mean() / sd * np.sqrt(len(r) / anos) if sd > 0 else 0.0
    return dict(ret=eq.iloc[-1] - 1, cagr=eq.iloc[-1] ** (1 / anos) - 1, sharpe=sh, dd=(eq / eq.cummax() - 1).min())


class Reg:
    """Probabilidades de regime de um ativo/K mapeadas num calendario idx, mes a mes; shift > 0 = placebo."""
    def __init__(s, X, ms, Q, idx):
        s.idx = naive(idx); s.ms = [M for M in ms if M <= s.idx[-1]]; s.Q = Q
        s.pos = np.searchsorted(X.index.values, s.idx.values, side='left') - 1   # ultimo pregao < data
        s.b = list(np.searchsorted(s.idx.values, np.array(s.ms, dtype='datetime64[ns]'))) + [len(s.idx)]
        s.h0 = int(np.argmax(s.pos >= 0))   # primeira data com regime definido (as linhas validas sao contiguas)

    def prep(s, Rv):
        """Somas acumuladas para media/variancia sem regime em O(1) por mes, e Rv^2 para a variancia condicional."""
        z = np.zeros((1, Rv.shape[1])); s.c1 = np.vstack([z, np.cumsum(Rv, 0)]); s.c2 = np.vstack([z, np.cumsum(Rv ** 2, 0)]); s.R2 = Rv ** 2
        return s

    def P(s, j, shift=0):
        q = s.Q[s.ms[j]]; q = np.roll(q, shift, axis=0) if shift else q
        P = np.full((len(s.pos), q.shape[1]), np.nan); v = s.pos >= 0; P[v] = q[s.pos[v]]; return P


def medias(Rv, G, shift=0):
    """(E, E0): media condicional prevista e media sem regime de cada estrategia em cada data, so com datas anteriores
    ao mes. Antes do 1o ajuste: NaN."""
    E = np.full(Rv.shape, np.nan); E0 = np.full(Rv.shape, np.nan); h = G.h0
    for j in range(len(G.ms)):
        b, e = G.b[j], G.b[j + 1]
        if b <= h: continue
        P = G.P(j, shift); w = P[h:b]; nk = w.sum(0); m0 = (G.c1[b] - G.c1[h]) / (b - h)
        mu = np.where(nk[:, None] >= N0, (w.T @ Rv[h:b]) / np.maximum(nk, 1e-9)[:, None], m0[None, :])
        E[b:e] = P[b:e] @ mu; E0[b:e] = m0
    return E, E0


def info(Rv, E, E0, m, ppy):
    """Diferenca media a.a. entre os dias com E > E0 e os dias com E <= E0 (so datas da mascara m)."""
    on = E[m] > E0[m]; r = Rv[m]; d = []
    for n in range(Rv.shape[1]):
        a, b = r[on[:, n], n], r[~on[:, n], n]
        if len(a) >= 20 and len(b) >= 20: d.append((a.mean() - b.mean()) * ppy)
    return float(np.mean(d)) if d else np.nan


def guloso(score, C, n=NSEL, teto=TETO):
    s = []
    for i in np.argsort(-score):
        if score[i] <= 0 or len(s) == n: break
        if all(C[i, j] < teto for j in s): s.append(i)
    return s


def escolhe(Rv, G, CS, shift=0, cond=True):
    """Pesos diarios (datas x estrategias) da escolha mensal por regime (cond) ou sem regime."""
    W = np.zeros(Rv.shape); h = G.h0
    for j in range(len(G.ms)):
        b, e = G.b[j], G.b[j + 1]; C = CS[j]
        if b == 0: continue
        m0 = G.c1[b] / b; sh0 = m0 / (np.sqrt(np.maximum(G.c2[b] / b - m0 ** 2, 0)) + 1e-12)
        if not cond or b <= h:
            W[b:e][:, guloso(sh0, C)] = 1 / NSEL; continue
        P = G.P(j, shift); w = P[h:b]; nk = w.sum(0); K = P.shape[1]
        M1, M2 = w.T @ Rv[h:b], w.T @ G.R2[h:b]; Pk = np.zeros((K, Rv.shape[1]))
        for k in range(K):
            if nk[k] < N0: sc = sh0
            else:
                m = M1[k] / nk[k]; sc = m / (np.sqrt(np.maximum(M2[k] / nk[k] - m ** 2, 0)) + 1e-12)
            Pk[k, guloso(sc, C)] = 1 / NSEL
        W[b:e] = P[b:e] @ Pk
    return W


def pct(pl, v):
    """Percentil do valor real entre os placebos (empate conta meio; 0,5 = igual ao acaso)."""
    pl = pl[~np.isnan(pl)]; return np.nan if np.isnan(v) or not len(pl) else float(np.mean(pl < v) + 0.5 * np.mean(pl == v))


def ret_liga(Rv, on, cu): return (Rv * on).astype(float) - cu * np.abs(np.diff(on.astype(float), axis=0, prepend=on[:1].astype(float)))
def ret_pesos(Rv, W, cu): return (Rv * W).sum(1) - cu * np.abs(np.diff(W, axis=0, prepend=W[:1])).sum(1)


def atual(G, shift=0):
    """Probabilidade de regime vigente em cada data (parametros do mes da data)."""
    P = np.full((len(G.idx), G.Q[G.ms[0]].shape[1]), np.nan)
    for j in range(len(G.ms)): P[G.b[j]:G.b[j + 1]] = G.P(j, shift)[G.b[j]:G.b[j + 1]]
    return P


def roda(A, K, freq, rng):
    X, ms, Q, par = H.walk(A, K, freq); o, inf = avalia(A, X, ms, Q, rng)
    o.insert(1, 'freq', freq); o.insert(2, 'K', K)
    return o, dict(inf, ajustes=f'{ms[0]:%Y-%m}..{ms[-1]:%Y-%m}', diagA=np.round(par[-1][:K], 3).tolist())


def avalia(A, X, ms, Q, rng, bh_estado=None):
    """Todos os usos para uma serie de regimes (X, ms, Q no formato do hmm_regime.walk), com placebos.
    bh_estado: indice do estado em que o teste bh_regra fica comprado (regras simples: 1 = alta)."""
    R, a, k6, c = aprovadas(A); cu = CUSTO[A]; Xd = H.features(A)
    per = {'valid': (c[6], c[9]), 'oos': (c[9], c[10] + pd.Timedelta(days=1))}
    # bh no calendario de pregoes; estrategias no calendario das series
    cl = Xd.close; d = cl.index.to_series().diff().dt.days.fillna(1).values
    rb = (cl.pct_change().fillna(0.0).values - FUND[A] / 100 * d / 365)[:, None]
    Rv = R.to_numpy(); Gx = Reg(X, ms, Q, Xd.index).prep(rb); G = Reg(X, ms, Q, R.index).prep(Rv); i6 = [R.columns.get_loc(k) for k in k6]
    CS = [np.nan_to_num(np.corrcoef(Rv[:G.b[j]].T)) for j in range(len(G.ms))]
    W0 = escolhe(Rv, G, CS, cond=False)
    mk = {p: ((G.idx >= i0) & (G.idx < i1), (Gx.idx >= i0) & (Gx.idx < i1)) for p, (i0, i1) in per.items()}
    ppy = {p: m[0].sum() / ((G.idx[m[0]][-1] - G.idx[m[0]][0]).days / 365) for p, m in mk.items()}
    ppx = {p: m[1].sum() / ((Gx.idx[m[1]][-1] - Gx.idx[m[1]][0]).days / 365) for p, m in mk.items()}

    def testes(shift=0):
        """{(teste, periodo): (serie diaria, exposicao)} e {(info*, periodo): valor} para um deslocamento dos regimes."""
        Eb, Eb0 = medias(rb, Gx, shift); E, E0 = medias(Rv, G, shift)
        on_b, rel_b = ~(Eb <= 0), ~(Eb <= Eb0); on, rel = ~(E <= 0), ~(E <= E0)   # NaN (antes do 1o ajuste) = ligado
        g1, g2 = ret_liga(Rv, on, cu), ret_liga(Rv, rel, cu); W1 = escolhe(Rv, G, CS, shift)
        s = {'bh_hmm': (ret_liga(rb, on_b, cu)[:, 0], on_b[:, 0], 1), 'bh_rel': (ret_liga(rb, rel_b, cu)[:, 0], rel_b[:, 0], 1),
             'todas_hmm': (g1.mean(1), on.mean(1), 0), 'todas_rel': (g2.mean(1), rel.mean(1), 0),
             'k6_hmm': (g1[:, i6].mean(1), on[:, i6].mean(1), 0), 'k6_rel': (g2[:, i6].mean(1), rel[:, i6].mean(1), 0),
             'escolhe_hmm': (ret_pesos(Rv, W1, cu), W1.sum(1), 0)}
        if bh_estado is not None:
            ob = ~(atual(Gx, shift)[:, bh_estado] <= 0.5)[:, None]; s['bh_regra'] = (ret_liga(rb, ob, cu)[:, 0], ob[:, 0], 1)
        out = {(t, p): (r[mk[p][x]], ex[mk[p][x]]) for t, (r, ex, x) in s.items() for p in per}
        inf = {('info_bh', p): info(rb, Eb, Eb0, mk[p][1], ppx[p]) for p in per}
        inf.update({('info_todas', p): info(Rv, E, E0, mk[p][0], ppy[p]) for p in per})
        return out, inf

    real, inf = testes(); plac = {}
    for i in range(NPLAC):
        o, f = testes(int(rng.integers(len(X) // 10, len(X) - len(X) // 10)))
        for k, (r, _) in o.items(): plac.setdefault(k, []).append(st(pd.Series(r, index=(Gx if k[0].startswith('bh') else G).idx[mk[k[1]][k[0].startswith('bh')]]))['sharpe'])
        for k, v in f.items(): plac.setdefault(k, []).append(v)
    rows = []
    base = {'bh': (rb[:, 0], 1), 'todas': (Rv.mean(1), 0), 'k6': (Rv[:, i6].mean(1), 0), 'escolhe_sem_regime': (ret_pesos(Rv, W0, cu), 0)}
    for p in per:
        for t, (r, x) in base.items():
            idx = (Gx if x else G).idx[mk[p][x]]
            rows.append(dict(teste=t, periodo=p, **st(pd.Series(r[mk[p][x]], index=idx)), exposicao=W0[mk[p][0]].sum(1).mean() if t.startswith('esc') else 1.0))
        for (t, q), (r, ex) in real.items():
            if q != p: continue
            idx = (Gx if t.startswith('bh') else G).idx[mk[p][t.startswith('bh')]]; s = st(pd.Series(r, index=idx)); pl = np.array(plac[(t, p)])
            rows.append(dict(teste=t, periodo=p, **s, exposicao=float(np.mean(ex)), placebo_med=np.median(pl), placebo_pct=pct(pl, s['sharpe'])))
        for (t, q), v in inf.items():
            if q != p: continue
            pl = np.array(plac[(t, q)]); rows.append(dict(teste=t, periodo=p, ret=v, placebo_med=np.nanmedian(pl), placebo_pct=pct(pl, v)))
    o = pd.DataFrame(rows); o.insert(0, 'ativo', A)
    return o, dict(n_aprovadas=len(a), k6=[k.split('|')[1] for k in k6], cortes=[str(x)[:10] for x in c])


def propria(A):
    """Regime da propria estrategia (HMM 1-D por estrategia) contra o filtro de media movel da curva e contra nao filtrar."""
    R, a, k6, c = aprovadas(A); cu = CUSTO[A]; Rv = R.to_numpy(); idx = naive(R.index); i6 = [R.columns.get_loc(k) for k in k6]
    qs = [q for q in pd.date_range(idx[0], idx[-1], freq='QS') if (idx < q).sum() >= 365]
    b = list(np.searchsorted(idx.values, np.array(qs, dtype='datetime64[ns]'))) + [len(idx)]
    E = np.full(Rv.shape, np.nan); E0 = np.full(Rv.shape, np.nan); th = None
    for j in range(len(qs)):
        th = H.hmm1d(Rv[:b[j]], 2, 30 if th is None else 10, th); q = H.filtro1d(Rv[:b[j + 1]], th)
        E[b[j]:b[j + 1]] = np.einsum('tnk,nk->tn', q[b[j] - 1:b[j + 1] - 1], th[2]); E0[b[j]:b[j + 1]] = Rv[:b[j]].mean(0)
    m60 = pd.DataFrame(Rv).rolling(60).mean().shift(1).to_numpy()
    on, rel, onm = ~(E <= 0), ~(E <= E0), ~(m60 <= 0)
    per = {'valid': (c[6], c[9]), 'oos': (c[9], c[10] + pd.Timedelta(days=1))}; rows = []
    for p, (i0, i1) in per.items():
        m = (idx >= i0) & (idx < i1); ppy = m.sum() / ((idx[m][-1] - idx[m][0]).days / 365)
        for nome, cols in (('todas', slice(None)), ('k6', i6)):
            for t, o in (('', None), ('_propria_hmm', on), ('_propria_rel', rel), ('_media60', onm)):
                r = Rv[:, cols] if o is None else ret_liga(Rv, o, cu)[:, cols]
                rows.append(dict(teste=nome + (t or ''), periodo=p, **st(pd.Series(r.mean(1)[m], index=idx[m])),
                                 exposicao=1.0 if o is None else o[m][:, cols].mean()))
        rows.append(dict(teste='info_propria', periodo=p, ret=info(Rv, E, E0, m, ppy)))
        rows.append(dict(teste='info_media60', periodo=p, ret=info(Rv, m60, np.zeros_like(m60), m, ppy)))
    o = pd.DataFrame(rows); o.insert(0, 'ativo', A); return o


if __name__ == '__main__':
    rng = np.random.default_rng(7)
    for A in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
        o = propria(A); o.to_csv(os.path.join(OUT, f'study_{A}_propria.csv'), index=False)
        print(f'\n== {A} regime da propria estrategia'); print(o.drop(columns='ativo').to_string(index=False, float_format=lambda v: f'{v:+.2f}'))
        for freq in ('D', 'W'):
            for K in (2, 3):
                o, inf = roda(A, K, freq, rng)
                print(f'\n== {A} {freq} K={K}: {inf}')
                print(o.drop(columns=['ativo', 'freq', 'K']).to_string(index=False, float_format=lambda v: f'{v:+.2f}')); sys.stdout.flush()
                o.to_csv(os.path.join(OUT, f'study_{A}_{freq}_K{K}.csv'), index=False)
