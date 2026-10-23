"""Veredito de todas as celulas que foram para a robustez (lotes 3, 4, 7, 8, 9 e 11 a 33), com o CAGR composto
trade a trade do tvlib (o antigo somava log(close).diff() * pos, inflando o lado vendido). Para cada celula: periodo
todo (com controle), tercos e 2a metade rodados de novo em cada fatia, como nos scripts _rob; spread 2x/4x e funding
zero recontados a partir dos trades do periodo todo (o custo nao muda as entradas).

Criterio antigo (o que os lotes usavam): CAGR acima do B&H no periodo todo, nos 3 tercos e na 2a metade, e ainda
acima do B&H com spread 4x.
Criterio novo (para carteira): liquido positivo em cada terco, Sharpe >= Sharpe do B&H no periodo todo, t > 2
contra o controle, positivo com spread 4x e positivo com funding zero; entre as que passam, entra por ordem de
Sharpe quem tiver |corr| < 0,5 dos retornos diarios com todas as que ja entraram.

uso: python study_veredito.py ativo [k/n]   -> results/veredito/<ativo>_<k>.pkl (fatia k de n das celulas)
     python study_veredito.py --relatorio   -> results/study_veredito.txt e results/study_veredito.csv"""
import os, sys, io, glob, pickle, contextlib, importlib
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T, study_engulf_psar as E
from study_tvlote6 import M1

CACHE = os.path.join(D, 'results', 'veredito')
ROB = [8, 9] + list(range(11, 34))
TAGS = ['tudo', 't1', 't2', 't3', '2a']

# as 30 aprovadas antes da correcao (docs/APROVADAS.md ate o lote 33): rotulo -> (lote, est, ativo, TF, kwargs)
APROV = [
    ('§1 Trailing SL XAU 30m', 7, 'tsl', 'xau', '30min', dict(val=2.0)),
    ('§2 RSI-MA ETH 15m', 12, 'rsima', 'eth', '15min', dict(rl=10, ml=50)),
    ('§3 Pivot ST ETH 15m', 4, 'ppst', 'eth', '15min', dict(prd=5, F=2.0, Pd=10)),
    ('§4a UT Bot ETH 30m', 13, 'ut', 'eth', '30min', dict(a=5.0, atr_n=11, shorts=True)),
    ('§4b Ichimoku ETH 15m', 13, 'ichi', 'eth', '15min', dict(ts=20, ks=60, sb=120, off=60)),
    ('§4c Scalping ETH 30m', 13, 'scalp', 'eth', '30min', dict(sma_len=25, ema_len=0)),
    ('§5 FTSMA ETH 30m', 17, 'ftsma', 'eth', '30min', dict(use_ft=True)),
    ('§6 ABCD BTC 1h', 19, 'abcd', 'btc', '1h', dict(sl=0.04, rr=5.0)),
    ('§7 Follow Line ETH 30m', 20, 'fline', 'eth', '30min', dict(ln=21, dev=1.0)),
    ('§8 MA Consec ETH 4h', 21, 'cons', 'eth', '4h', dict(nb=4, malen=1)),
    ('§9 MA Band WTI 4h', 22, 'mab', 'wti', '4h', dict(ln=40, rr=3.0)),
    ('§10 Super trend V ETH 15m', 23, 'stv', 'eth', '15min', dict(short_ok=True)),
    ('§11 BEST ST ETH 1h', 24, 'best', 'eth', '1h', dict()),
    ('§12 VWAPStrategy ETH 30m', 24, 'vwap', 'eth', '30min', dict()),
    ('§13 Chandelier ETH 30m', 25, 'ce', 'eth', '30min', dict()),
    ('§14 THMA ETH 15m', 25, 'thma', 'eth', '15min', dict(ln=100)),
    ('§15 SM Pivot ETH 15m', 25, 'smp', 'eth', '15min', dict(sl=0.0, tp=0.0)),
    ('§16 HULL+T3 ETH 1h', 25, 'ht3', 'eth', '1h', dict(ln=100)),
    ('§17 5 EMA ETH 4h', 26, 'e5', 'eth', '4h', dict(rr=3.0)),
    ('§18 Wyckoff ETH 4h', 27, 'wyk', 'eth', '4h', dict(sl=0.03)),
    ('§19 HA MACD BTC 1h', 28, 'hamacd', 'btc', '1h', dict()),
    ('§20 HA PA WTI 4h', 28, 'hapa', 'wti', '4h', dict(ha=False, short_ok=True)),
    ('§21 Golden Edge WTI 30m', 29, 'ged', 'wti', '30min', dict(f=9, s=50)),
    ('§22 Multi-MA ETH 15m', 30, 'mma', 'eth', '15min', dict(ln=150)),
    ('§23 Multi-MA ETH 4h', 30, 'mma', 'eth', '4h', dict()),
    ('§24 Multi-MA BTC 4h', 30, 'mma', 'btc', '4h', dict(ln=150)),
    ('§25 MACD+Stoch WTI 4h', 31, 'mst', 'wti', '4h', dict(ls=14)),
    ('§26 TSI ST ETH 15m', 32, 'tss', 'eth', '15min', dict()),
    ('§27 TSI ST ETH 30m', 32, 'tss', 'eth', '30min', dict(per=32)),
    ('§28 VWAP X EMA ETH 30m', 33, 'vxe', 'eth', '30min', dict()),
]


def quiet(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def cells():
    """(lote, est, ativo, TF, kwargs, fn(nome, df, mm, m1) -> (resumo, trades)) de todos os scripts de robustez."""
    out = []
    L3 = quiet(importlib.import_module, 'study_tvlote3_rob')
    for est, tf, cfg, sig in L3.CELLS:
        out.append((3, f'{est} {cfg}', 'xau', tf, {},
                    lambda n, d, mm, m1, sig=sig: L3.S.run(n, d, *sig(d), '', verbose=False)))
    L4 = quiet(importlib.import_module, 'study_tvlote4_rob')
    for a, cs in L4.CELLS.items():
        for tf, prd, F, Pd in cs:
            out.append((4, 'ppst', a, tf, dict(prd=prd, F=F, Pd=Pd),
                        lambda n, d, mm, m1, p=(prd, F, Pd): L4.S.run_bars(n, d, *L4.S.ppst_signals(d, *p), '',
                                                                           verbose=False)))
    L7 = quiet(importlib.import_module, 'study_tvlote7')
    for tf in ('15min', '30min', '1h', '4h'):
        out.append((7, 'tsl', 'xau', tf, dict(val=2.0),
                    lambda n, d, mm, m1: L7.run_tsl(n, d, '', None, False, val=2.0)))
    for lote in ROB:
        R = quiet(importlib.import_module, f'study_tvlote{lote}_rob')
        cs = R.CELLS if isinstance(R.CELLS, dict) else {'xau': R.CELLS}
        for a, lst in cs.items():
            for est, tf, kw in lst:
                def fn(n, d, mm, m1, f=R.RUN[est], kw=kw, zig=(lote == 12 and est == 'zig')):
                    if zig:
                        kw = dict(kw, h1=T.resample(m1, '1h'), m15=T.resample(m1, '15min'))
                    return f(n, d, mm, '', **kw)
                out.append((lote, est, a, tf, kw, fn))
    return out


def label(lote, est, a, tf, kw):
    for rot, l2, e2, a2, tf2, kw2 in APROV:
        if (l2, e2, a2, tf2, kw2) == (lote, est, a, tf, kw):
            return rot
    return ''


def ensure_aprov(cs):
    """As aprovadas que nao aparecem com os mesmos kwargs nos scripts _rob entram como celulas extras."""
    have = {label(*c[:5]) for c in cs}
    for rot, lote, est, a, tf, kw in APROV:
        if rot in have: continue
        mod = importlib.import_module(f'study_tvlote{lote}')
        f = getattr(mod, 'run_' + est)
        cs.append((lote, est, a, tf, kw, lambda n, d, mm, m1, f=f, kw=kw: f(n, d, mm, '', **kw)))
    return cs


def cagr_of(df, tr, name, ret=None):
    if tr is None or len(tr) == 0:
        return 0.0
    if ret is not None:
        tr = tr.assign(ret=ret)
    return T.equity(df, tr, name)['cagr']


def run_cell(name, m1, mm, cache, cell):
    lote, est, a, tf, kw, fn = cell
    full = cache.setdefault(tf, T.resample(m1, tf))
    o, tr = quiet(fn, name, full, mm, m1)     # resumo do proprio script: controle com a mesma gestao
    rec = dict(lote=lote, est=est, ativo=a, tf=tf, cfg=str(kw), rotulo=label(lote, est, a, tf, kw))
    bh = T.bh_stats(full)
    rec.update(trades=len(tr) if tr is not None else 0, bh_tudo=bh['bh'], bh_sharpe=bh['bh_sharpe'], bh_dd=bh['bh_dd'])
    if o:
        rec.update(cagr_tudo=o['cagr'], sharpe=o['sharpe'], dd=o['dd'], t=o['t'], por_ano=o['por_ano'],
                   bp_liq=o['bp_liq'], expo=o['expo'])
        c = E.CUSTO[name]
        rec['cagr_sp2'] = cagr_of(full, tr, name, tr.bruto - 4 * c - tr.fund)
        rec['cagr_sp4'] = cagr_of(full, tr, name, tr.bruto - 8 * c - tr.fund)
        rec['cagr_f0'] = cagr_of(full, tr, name, tr.bruto - 2 * c)
        rec['vend'] = float((tr.d < 0).mean())
        eq = T.equity_curve(full, tr, name)
        dly = eq.resample('1D').last().dropna().pct_change().dropna()
    else:
        rec['cagr_tudo'] = cagr_of(full, tr, name); dly = None
    cuts = np.array_split(np.arange(len(full)), 3)
    parts = [(f't{k + 1}', full.iloc[c[0]:c[-1] + 1]) for k, c in enumerate(cuts)] + [('2a', full.iloc[len(full) // 2:])]
    ctl = T.control_dur
    T.control_dur = lambda df, trades, *a, **k: np.zeros(2)     # nas fatias so o CAGR interessa
    try:
        for tag, df in parts:
            t2 = quiet(fn, name, df, mm, m1)[1]
            rec[f'cagr_{tag}'] = cagr_of(df, t2, name)
            rec[f'bh_{tag}'] = T.bh_stats(df)['bh']
    finally:
        T.control_dur = ctl
    return rec, dly


def shard(name, k=0, n=1):
    os.makedirs(CACHE, exist_ok=True)
    cs = [c for c in ensure_aprov(cells()) if c[2] == name][k::n]
    m1 = T.load_m1v(name); mm = M1(m1); cache = {}
    rows, daily = [], {}
    for c in cs:
        rec, dly = run_cell(name, m1, mm, cache, c)
        rows.append(rec)
        if dly is not None:
            daily[(rec['ativo'], rec['lote'], rec['est'], rec['tf'], rec['cfg'])] = dly
        print(f"{rec['lote']:3d} {rec['est']:<14} {rec['ativo']} {rec['tf']:<6} {rec['cfg'][:40]:<40} "
              f"CAGR {rec['cagr_tudo']:+7.1%} vs {rec['bh_tudo']:+7.1%}  t {rec.get('t', np.nan):+5.2f}", flush=True)
    pickle.dump((rows, daily), open(os.path.join(CACHE, f'{name}_{k}.pkl'), 'wb'))


def criterios(R):
    old = {f'acima_{t}': R[f'cagr_{t}'] > R[f'bh_{t}'] for t in TAGS}
    old['sp4_acima'] = R.cagr_sp4 > R.bh_tudo
    new = {f'pos_{t}': R[f'cagr_{t}'] > 0 for t in ('t1', 't2', 't3')}
    new.update(sharpe=R.sharpe >= R.bh_sharpe, t2=R.t > 2, sp4_pos=R.cagr_sp4 > 0, f0_pos=R.cagr_f0 > 0)
    return pd.DataFrame(old).fillna(False), pd.DataFrame(new).fillna(False)


def relatorio():
    rows, daily = [], {}
    for f in sorted(glob.glob(os.path.join(CACHE, '*.pkl'))):
        r, d = pickle.load(open(f, 'rb')); rows += r; daily.update(d)
    R = pd.DataFrame(rows)
    # celulas repetidas entre lotes (mesma regra testada de novo) ficam uma vez so
    R = R.sort_values(['rotulo', 'lote'], ascending=[False, True])
    R = R.drop_duplicates(['ativo', 'tf', 'trades', 'cagr_tudo']).reset_index(drop=True)
    O, N = criterios(R)
    R['antigo'] = O.all(axis=1); R['novo_sem_corr'] = N.all(axis=1)
    R['falha_antigo'] = [','.join(c for c in O.columns if not O.loc[i, c]) for i in R.index]
    R['falha_novo'] = [','.join(c for c in N.columns if not N.loc[i, c]) for i in R.index]
    R['nome'] = [r.rotulo or f'L{r.lote} {r.est} {r.ativo.upper()} {r.tf} {r.cfg if r.cfg != "{}" else ""}'.strip()
                 for r in R.itertuples()]
    key = lambda r: (r.ativo, r.lote, r.est, r.tf, r.cfg)
    M = pd.DataFrame({r.nome: daily[key(r)] for r in R.itertuples() if key(r) in daily})
    # carteira gulosa: por Sharpe, entra quem tiver |corr| < 0,5 com todas as que ja entraram
    R['corr_max'] = np.nan; R['carteira'] = False; R['corr_com'] = ''
    chosen = []
    for i in R[R.novo_sem_corr].sort_values('sharpe', ascending=False).index:
        nm = R.at[i, 'nome']
        cc = {c: M[[nm, c]].dropna().corr().iloc[0, 1] if len(M[[nm, c]].dropna()) >= 120 else 0.0 for c in chosen}
        worst = max(cc, key=lambda c: abs(cc[c]), default=None)
        R.at[i, 'corr_max'] = cc[worst] if worst else 0.0
        if worst is None or abs(cc[worst]) < 0.5:
            chosen.append(nm); R.at[i, 'carteira'] = True
        else:
            R.at[i, 'corr_com'] = worst
    R.to_csv(os.path.join(D, 'results', 'study_veredito.csv'), index=False, float_format='%.4f')

    def fmt(r):
        return (f"{r.nome:<44} {r.cagr_tudo:+7.1%} {r.bh_tudo:+7.1%}  Sh {r.sharpe:+5.2f} ({r.bh_sharpe:+4.2f})"
                f"  DD {r.dd:+4.0%}  t {r.t:+5.2f}  tercos {r.cagr_t1:+5.0%}/{r.cagr_t2:+5.0%}/{r.cagr_t3:+5.0%}"
                f" (B&H {r.bh_t1:+5.0%}/{r.bh_t2:+5.0%}/{r.bh_t3:+5.0%})  2a {r.cagr_2a:+5.0%} ({r.bh_2a:+5.0%})"
                f"  sp4 {r.cagr_sp4:+5.0%}  f0 {r.cagr_f0:+5.0%}")
    head = (f"{'celula':<44} {'CAGR':>7} {'B&H':>7}  Sharpe (B&H)    DD      t      tercos (B&H)"
            f"                          2a metade (B&H)  spread 4x  funding 0")
    ok = R.dropna(subset=['sharpe'])
    out = [f'{len(R)} celulas de robustez (lotes 3 a 33, sem repetir), CAGR composto trade a trade.\n']
    out.append(f"Criterio novo, aprovadas para carteira ({int(R.carteira.sum())}), em ordem de Sharpe:\n" + head)
    out += [fmt(r) for r in ok[ok.carteira].sort_values('sharpe', ascending=False).itertuples()]
    red = ok[ok.novo_sem_corr & ~ok.carteira].sort_values('sharpe', ascending=False)
    out.append(f"\nPassam no criterio novo mas ficam fora por correlacao >= 0,5 ({len(red)}):")
    out += [f"{fmt(r)}  corr {r.corr_max:+.2f} com {r.corr_com}" for r in red.itertuples()]
    q = ok[~ok.novo_sem_corr & (ok.falha_novo.str.count(',') == 0)].sort_values('sharpe', ascending=False)
    out.append(f"\nQuase no criterio novo: falham em um item so ({len(q)}):")
    out += [f"{fmt(r)}  falha: {r.falha_novo}" for r in q.itertuples()]
    out.append(f"\nCriterio antigo com a conta corrigida ({int(R.antigo.sum())}):\n" + head)
    out += [fmt(r) for r in ok[ok.antigo].sort_values('sharpe', ascending=False).itertuples()]
    q = ok[~ok.antigo & (ok.falha_antigo.str.count(',') == 0)].sort_values('sharpe', ascending=False)
    out.append(f"\nQuase no criterio antigo: falham em um item so ({len(q)}):")
    out += [f"{fmt(r)}  falha: {r.falha_antigo}" for r in q.itertuples()]
    A = ok[ok.rotulo != ''].copy()
    A['n'] = A.rotulo.str.extract(r'§(\d+)')[0].astype(int)
    out.append('\nAs 30 aprovadas de antes, com a conta corrigida:\n' + head + '  antigo  novo  falhas (novo)')
    out += [f"{fmt(r)}  {'S' if r.antigo else 'n':>5}  {'C' if r.carteira else ('S' if r.novo_sem_corr else 'n'):>4}"
            f"  {r.falha_novo}" for r in A.sort_values(['n', 'rotulo']).itertuples()]
    out.append('\nLegenda: novo C = entra na carteira, S = passa mas e redundante (corr >= 0,5), n = nao passa. Itens do '
               'criterio novo: pos_t1/t2/t3 = liquido positivo no terco, sharpe = Sharpe >= B&H, t2 = t > 2, sp4_pos = '
               'positivo com spread 4x, f0_pos = positivo com funding zero.')
    txt = '\n'.join(out); print(txt)
    open(os.path.join(D, 'results', 'study_veredito.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    if sys.argv[1:] == ['--relatorio']:
        relatorio()
    else:
        k, n = map(int, (sys.argv[2] if len(sys.argv) > 2 else '0/1').split('/'))
        shard(sys.argv[1], k, n)
