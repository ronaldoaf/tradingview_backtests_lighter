"""Carteira 4h de 5 ativos (BTC, WTI, US100, XAU, XAG), pesos iguais, mesmo parametro em todos, jan/2020-dez/2023.
Le results/cart4h/<ativo>/lote*.csv + _ser.parquet (scripts/cart4h_lote.py) e grava results/cart4h/:
  celulas.csv  - uma linha por celula (lote, est, cfg) com stats da carteira no periodo, por ano e por ativo
  ranking.csv  - melhor celula por estrategia + robustez da vizinhanca (grade toda da estrategia) + Sharpe deflacionado
Long e short: so entram celulas que operam os dois lados (>= 5% dos trades vendidos). Templates/exemplos fora."""
import glob, os, sys
import numpy as np, pandas as pd
from scipy.stats import norm
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(D, 'results', 'cart4h')
AT = ['btc', 'wti', 'us100', 'xau', 'xag']; ANOS = [2020, 2021, 2022, 2023]
DIAS = pd.date_range('2020-01-02', '2023-12-31', freq='D')
nomes = pd.read_csv(os.path.join(D, 'results', 'wti_4p_8p_full', 'ranking.csv')).astype({'lote': str}).set_index(['lote', 'est']).nome.to_dict()

cel, SER = {}, {}
for a in AT:
    for f in sorted(glob.glob(os.path.join(R, a, 'lote*.csv'))):
        l = os.path.basename(f)[4:-4]; g = pd.read_csv(f)
        if 'sid' not in g or not os.path.exists(f[:-4] + '_ser.parquet'): continue
        S = pd.read_parquet(f[:-4] + '_ser.parquet'); S.index = pd.DatetimeIndex(S.index).tz_localize(None).normalize()
        S = S.reindex(DIAS).replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=-1.0)
        g['est'] = g['est'].fillna(l) if 'est' in g else l; g['cfg'] = g['cfg'].astype(str) if 'cfg' in g else g.get('tag', '')
        g = g.drop_duplicates(['est', 'cfg'])
        for _, r in g.iterrows():
            k = (l, str(r.est), str(r.cfg)); c = cel.setdefault(k, {})
            c[a] = dict(trades=int(r.trades), longs=int(r.longs), win=float(r.win)); SER.setdefault(k, {})[a] = S[str(int(r.sid)) if str(int(r.sid)) in S else int(r.sid)].to_numpy(float)


def st(r):
    r = np.asarray(r); n = len(r); yrs = n / 365.25; eq = np.cumprod(1 + r); sd = r.std(ddof=1)
    sh = r.mean() / sd * np.sqrt(365.25) if sd > 0 else 0.0
    return dict(cagr=eq[-1] ** (1 / yrs) - 1, vol=sd * np.sqrt(365.25), sharpe=sh, dd=(eq / np.maximum.accumulate(eq) - 1).min(),
                t=r.mean() / sd * np.sqrt(n) if sd > 0 else 0.0, total=eq[-1] - 1)


yr = DIAS.year.to_numpy(); rows = []; PORT = {}
for k, c in cel.items():
    tr = sum(v['trades'] for v in c.values()); lg = sum(v['longs'] for v in c.values())
    if tr == 0 or (tr - lg) / tr < 0.05 or lg / tr < 0.05: continue    # tem que operar long e short
    M = np.column_stack([SER[k].get(a, np.zeros(len(DIAS))) for a in AT])
    if np.abs(M).max() > 0.5: continue   # serie quebrada (equity zerou/voltou, divisao por zero): fora
    p = M.mean(1); PORT[k] = p
    o = dict(lote=k[0], est=k[1], cfg=k[2], nome=nomes.get((k[0], k[1]), ''), trades=tr, short_frac=(tr - lg) / tr,
             win=sum(v['win'] * v['trades'] for v in c.values()) / tr, n_ativos=len(c), **st(p))
    for y in ANOS:
        s = st(p[yr == y]); o.update({f'cagr_{y}': s['cagr'], f'sharpe_{y}': s['sharpe'], f'dd_{y}': s['dd']})
    for j, a in enumerate(AT):
        s = st(M[:, j]); o[f'cagr_{a}'] = s['cagr']; o[f'sharpe_{a}'] = s['sharpe']; o[f'tr_{a}'] = c.get(a, {}).get('trades', 0)
        o[f'contrib_{a}'] = np.log1p(M[:, j] / 5).sum() / 4   # contribuicao log anual aproximada (peso 1/5)
    rows.append(o)
g = pd.DataFrame(rows)
g = g[~g.cfg.str.contains('peek')]   # lookahead_on: fora
g = g[~g.nome.fillna('').str.contains('Example|Template|Exemplo|Modelo', case=False)].reset_index(drop=True)
g['anos_pos'] = (g[[f'cagr_{y}' for y in ANOS]] > 0).sum(1); g['ativos_pos'] = (g[[f'cagr_{a}' for a in AT]] > 0).sum(1)
g['sharpe_min_ano'] = g[[f'sharpe_{y}' for y in ANOS]].min(1); g['sharpe_min_ativo'] = g[[f'sharpe_{a}' for a in AT]].min(1)
g.to_csv(os.path.join(R, 'celulas.csv'), index=False)

# Sharpe deflacionado (Bailey & Lopez de Prado): N = todas as celulas testadas, variancia dos Sharpes entre elas
N = len(g); n = len(DIAS); sr = g.sharpe / np.sqrt(365.25); vsr = sr.var(); em = 0.5772156649
sr0 = np.sqrt(vsr) * ((1 - em) * norm.ppf(1 - 1 / N) + em * norm.ppf(1 - 1 / (N * np.e)))
sk = {k: pd.Series(v).skew() for k, v in PORT.items()}; ku = {k: pd.Series(v).kurt() + 3 for k, v in PORT.items()}
def dsr(r):
    k = (r.lote, r.est, r.cfg); s = r.sharpe / np.sqrt(365.25)
    return norm.cdf((s - sr0) * np.sqrt(n - 1) / np.sqrt(1 - sk[k] * s + (ku[k] - 1) / 4 * s * s))
g['dsr'] = g.apply(dsr, axis=1)

# por estrategia: melhor celula (Sharpe) + a grade toda como vizinhanca
best = g.sort_values('sharpe', ascending=False).drop_duplicates(['lote', 'est'])
viz = g.groupby(['lote', 'est']).agg(celulas=('sharpe', 'size'), sharpe_mediana=('sharpe', 'median'), frac_pos=('sharpe', lambda x: (x > 0).mean()),
                                      frac_robusta=('anos_pos', lambda x: 0)).reset_index()
rob = g.assign(rb=(g.anos_pos >= 3) & (g.ativos_pos >= 4) & (g.sharpe > 0)).groupby(['lote', 'est']).rb.mean().rename('frac_robusta')
viz = viz.drop(columns='frac_robusta').merge(rob.reset_index(), on=['lote', 'est'])
rk = best.merge(viz, on=['lote', 'est'])
# nota de robustez: Sharpe da celula escolhida encolhido para a mediana da grade + consistencia em anos e ativos
rk['score'] = 0.5 * rk.sharpe + 0.5 * rk.sharpe_mediana + 0.25 * (rk.anos_pos - 2) + 0.15 * (rk.ativos_pos - 2.5) + rk.frac_robusta
rk = rk.sort_values('score', ascending=False).reset_index(drop=True)
rk.to_csv(os.path.join(R, 'ranking.csv'), index=False)
# benchmark: buy & hold pesos iguais (sem funding) com os mesmos dias
print(f'celulas long+short: {N} de {len(cel)}; estrategias: {len(rk)}; Sharpe esperado do maximo sob H0 (anual): {sr0 * np.sqrt(365.25):.2f}')
cols = ['lote', 'est', 'nome', 'cfg', 'cagr', 'vol', 'sharpe', 'dd', 't', 'dsr', 'anos_pos', 'ativos_pos', 'sharpe_mediana', 'frac_pos', 'frac_robusta', 'celulas', 'trades', 'score']
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 30)
print(rk[cols].head(30).to_string(index=False, float_format=lambda v: f'{v:.2f}'))

# referencias: B&H pesos iguais e tendencia ingenua (sinal do EMA50 x EMA200 no 4h, sempre posicionado, custo+funding)
sys.path.insert(0, os.path.join(D, 'scripts')); import tvlib as T
os.environ['EDGE_END'] = '2023-12-31'; BH, TS = [], []
for a in AT:
    m = T.load_m1v(a); m.index = m.index.as_unit('ns'); m = m[m.index >= '2020-01-01']; c = T.resample(m, '4h').close
    e1, e2 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean(); pos = np.sign(e1 - e2).shift(1).fillna(0)
    r = c.pct_change().fillna(0); rr = pos * r - pos.diff().abs().fillna(0) * T.CUSTO[a] - (pos > 0) * T.FUND[a] / 100 / 2190 + (pos < 0) * T.FUND[a] / 100 / 2190
    d = lambda x: (1 + x).groupby(x.index.tz_localize(None).normalize()).prod().sub(1).reindex(DIAS).fillna(0).to_numpy()
    BH.append(d(r)); TS.append(d(rr))
ref = {}
for nm, M in (('B&H pesos iguais', BH), ('EMA50x200 ingenua', TS)):
    p = np.column_stack(M).mean(1); s = st(p); ref[nm] = p
    print(nm, ' '.join(f'{k}={v:.2f}' for k, v in s.items()), '| por ano:', ' '.join(f'{y}:{st(p[yr == y])["cagr"]:+.0%}' for y in ANOS))
tsr = ref['EMA50x200 ingenua']
rk['corr_tendencia'] = [np.corrcoef(PORT[(r.lote, r.est, r.cfg)], tsr)[0, 1] for r in rk.itertuples()]
X = np.column_stack([tsr, np.ones(len(tsr))])
def alfa(k):
    y = PORT[k]; b, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ b
    return b[1] * 365.25, b[1] / (e.std(ddof=2) / np.sqrt(len(y)))
rk[['alfa_vs_tend', 't_alfa']] = [alfa((r.lote, r.est, r.cfg)) for r in rk.itertuples()]
rk.to_csv(os.path.join(R, 'ranking.csv'), index=False)
pd.DataFrame(ref, index=DIAS).to_csv(os.path.join(R, 'referencias_diario.csv'))
print(rk[['lote', 'est', 'nome', 'cfg', 'sharpe', 'dsr', 'corr_tendencia', 'alfa_vs_tend', 't_alfa', 'score']].head(25).to_string(index=False, float_format=lambda v: f'{v:.2f}'))
print('t_alfa>2:', (rk.t_alfa > 2).sum(), 'de', len(rk), '| dsr>0.95:', (rk.dsr > 0.95).sum())
