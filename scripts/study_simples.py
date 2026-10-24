"""Regras simples de tendencia nos 5 ativos, para ver se reproduzem o que as 34 aprovadas capturam.

Familias (sinal no fechamento da barra de 4h, posicao aplicada da abertura seguinte em diante):
  ma    : media de sign(close - SMA_L) para L numa grade geometrica de Lmin a Lmax dias (ensemble de MAs)
  tsmom : media de sign(close / close[L] - 1) na mesma grade (time-series momentum multi-horizonte)
  ma1   : sign(close - SMA_L) com um L so (referencia)
Cada familia em 4 modos: ls (comprado e vendido, posicao fracionaria = a media), ls_d (sign da media, sempre 1x),
lo (so comprado, max(media, 0)), lo_d (comprado 1x se media > 0).
Lookbacks em dias de calendario (L dias = as barras de 4h dos ultimos L dias), igual para os 5 ativos.

Conta: retorno da barra = p * (open[t+1] / open[t] - 1) com p decidido no fechamento de t-1; custo |dp| * CUSTO
por troca (meia perna por unidade), funding p * FUND pro-rata (o long paga, o short recebe). Retorno diario =
produto dos retornos das barras (posicao rebalanceada a cada barra, aproximacao da quantidade fixa por trade).

Selecao so antes do OOS (< 2023-05-17): criterio corrigido em cada ativo (positivo em cada terco do trecho,
Sharpe >= B&H, t > 2 contra controle de deslocamento circular da posicao, positivo com spread 4x e sem funding);
entre as configuracoes, fica a de maior Sharpe medio nos 5 ativos (uma configuracao para todos). Depois do OOS so
se olha.
uso: python study_simples.py   -> results/study_simples.txt, results/study_simples_grid.csv, results/study_simples_diario.csv"""
import os, sys, glob, pickle, itertools
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_engulf_psar import CUSTO, FUND
from study_carteira8 import stats

ASSETS = ['xau', 'us100', 'wti', 'btc', 'eth']
OOS = pd.Timestamp('2023-05-17', tz='UTC'); INI = pd.Timestamp('2020-01-01', tz='UTC')
GRID = [(lo, hi, k) for lo, hi in [(0.5, 3), (1, 5), (1, 10), (2, 10), (5, 50), (10, 100), (20, 200), (5, 200), (10, 300), (2, 30), (3, 100), (30, 250)]
        for k in (4,)] + [(L, L, 1) for L in (1, 2, 3, 5, 10, 20, 30, 50, 100, 150, 200)]
FAM = ['ma', 'tsmom']; MODES = ['ls', 'ls_d', 'lo', 'lo_d']
RNG = np.random.default_rng(7)


def load(a):
    f = os.path.join(D, 'results', 'simples', f'{a}_4h.pkl')
    if os.path.exists(f): return pd.read_pickle(f)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    df = T.resample(T.load_m1v(a), '4h')[['open', 'close']]; df.to_pickle(f); return df


def bars_per_day(df):
    return len(df) / ((df.index[-1] - df.index[0]).days or 1)


def raw_signal(df, fam, lo, hi, k):
    c = df.close; bpd = bars_per_day(df)
    Ls = np.unique(np.round(np.geomspace(lo, hi, k) * bpd).astype(int)) if k > 1 else [max(int(round(lo * bpd)), 1)]
    s = [np.sign(c - c.rolling(L).mean()) if fam == 'ma' else np.sign(c / c.shift(L) - 1) for L in Ls]
    return pd.concat(s, axis=1).mean(axis=1, skipna=False)


def to_pos(m, mode):
    p = {'ls': m, 'ls_d': np.sign(m), 'lo': m.clip(lower=0), 'lo_d': (m > 0).astype(float)}[mode]
    return p.fillna(0.0)


def bar_returns(df, p, a, cmult=1.0, fund=True):
    """p decidido no fechamento da barra t; vale de open[t+1] a open[t+2]."""
    o = df.open; r = o.shift(-1) / o - 1
    held = p.shift(1).fillna(0)
    dt = (df.index.to_series().shift(-1) - df.index.to_series()).dt.total_seconds() / (365 * 86400)
    cost = held.diff().abs().fillna(held.abs()) * CUSTO[a] * cmult
    fnd = held * FUND[a] / 100 * dt if fund else 0.0
    return (held * r - cost - fnd).fillna(0.0)


def daily(br):
    d = np.exp(np.log1p(br).resample('1D').sum()) - 1
    return d


def sharpe(x):
    return x.mean() / x.std() * np.sqrt(365) if x.std() > 0 else np.nan


def cagr(x):
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    return float(np.exp(np.log1p(x).sum() / yrs) - 1)


def control_t(df, p, a, msk, nsim=60):
    """t do log-retorno total contra a mesma serie de posicao deslocada circularmente (mesma exposicao, lado e
    duracao dos trechos, datas sorteadas)."""
    real = np.log1p(bar_returns(df, p, a)[msk]).sum()
    pv = p[msk].to_numpy(); sub = df[msk]; n = len(pv); sims = []
    for _ in range(nsim):
        q = pd.Series(np.roll(pv, RNG.integers(n // 10, n - n // 10)), sub.index)
        sims.append(np.log1p(bar_returns(sub, q, a)).sum())
    return (real - np.mean(sims)) / (np.std(sims) or np.nan)


def evaluate(df, p, a, a0, a1, with_t=True):
    msk = (df.index >= a0) & (df.index < a1)
    br = bar_returns(df, p, a)[msk]; dl = daily(br)
    bh = daily((df.open.shift(-1) / df.open - 1).fillna(0)[msk])
    cuts = np.array_split(dl.index, 3)
    rec = dict(cagr=cagr(dl), sharpe=sharpe(dl), bh_cagr=cagr(bh), bh_sharpe=sharpe(bh),
               dd=float((np.exp(np.log1p(dl).cumsum()) / np.exp(np.log1p(dl).cumsum()).cummax() - 1).min()),
               t1=cagr(dl[cuts[0]]), t2=cagr(dl[cuts[1]]), t3=cagr(dl[cuts[2]]),
               sp4=cagr(daily(bar_returns(df, p, a, cmult=4)[msk])), f0=cagr(daily(bar_returns(df, p, a, fund=False)[msk])),
               expo=float((p[msk] != 0).mean()), comprado=float((p[msk] > 0).mean()),
               giro=float(p[msk].diff().abs().sum() / ((a1 - max(a0, df.index[0])).days / 365.25)))
    rec['t'] = control_t(df, p, a, msk) if with_t else np.nan
    rec['passa'] = bool(min(rec['t1'], rec['t2'], rec['t3']) > 0 and rec['sharpe'] >= rec['bh_sharpe']
                        and rec['t'] > 2 and rec['sp4'] > 0 and rec['f0'] > 0) if with_t else np.nan
    return rec, dl


def main():
    dfs = {a: load(a) for a in ASSETS}
    end = pd.Timestamp('2030-01-01', tz='UTC')
    rows = []
    for fam, (lo, hi, k), mode in itertools.product(FAM, GRID, MODES):
        for a in ASSETS:
            df = dfs[a]; p = to_pos(raw_signal(df, fam, lo, hi, k), mode)
            rec, _ = evaluate(df, p, a, df.index[0], OOS)
            rows.append(dict(fam=fam if k > 1 else fam + '1', lo=lo, hi=hi, mode=mode, ativo=a, **rec))
        print(fam, lo, hi, mode, flush=True)
    G = pd.DataFrame(rows).drop_duplicates(['fam', 'lo', 'hi', 'mode', 'ativo'])
    G.to_csv(os.path.join(D, 'results', 'study_simples_grid.csv'), index=False, float_format='%.4f')
    key = ['fam', 'lo', 'hi', 'mode']
    A = G.groupby(key).agg(sharpe_med=('sharpe', 'mean'), passam=('passa', 'sum'),
                           bh=('bh_sharpe', 'mean')).reset_index().sort_values('sharpe_med', ascending=False)
    out = ['Antes do OOS (inicio de cada ativo .. 2023-05-16), configuracoes por Sharpe medio nos 5 ativos:',
           A.head(25).to_string(index=False, float_format=lambda x: f'{x:.2f}')]
    best_fam = {}
    for f in ('ma', 'tsmom', 'ma1', 'tsmom1'):
        for lo_only in (False, True):
            sub = A[(A.fam == f) & (A['mode'].str.startswith('lo') == lo_only)]
            best_fam[(f, lo_only)] = sub.iloc[0]
    out.append('\nEscolhidas (melhor Sharpe medio antes do OOS em cada familia, com e sem vendido):')
    daily_cols = {}
    for (f, lo_only), b in best_fam.items():
        tag = f"{b.fam} {b.lo}-{b.hi}d {b['mode']}"
        out.append(f'\n--- {tag}')
        for a in ASSETS:
            df = dfs[a]; p = to_pos(raw_signal(df, b.fam.rstrip('1'), b.lo, b.hi, 1 if b.lo == b.hi else 4), b['mode'])
            for nm, a0, a1 in (('antes', df.index[0], OOS), ('depois', OOS, end)):
                r, dl = evaluate(df, p, a, a0, a1)
                out.append(f"  {a:<5} {nm:<6} CAGR {r['cagr']:+6.1%} (B&H {r['bh_cagr']:+6.1%})  Sharpe {r['sharpe']:+5.2f}"
                           f" ({r['bh_sharpe']:+5.2f})  DD {r['dd']:+4.0%}  t {r['t']:+5.2f}  tercos {r['t1']:+5.0%}/"
                           f"{r['t2']:+5.0%}/{r['t3']:+5.0%}  sp4 {r['sp4']:+5.0%} f0 {r['f0']:+5.0%}  expo {r['expo']:.2f}"
                           f" comprado {r['comprado']:.2f} giro {r['giro']:.0f}/ano  {'PASSA' if r['passa'] else ''}")
            _, dl = evaluate(df, p, a, df.index[0], end, with_t=False)
            daily_cols[(tag, a)] = dl
    pickle.dump((best_fam, daily_cols), open(os.path.join(D, 'results', 'simples', 'escolhidas.pkl'), 'wb'))
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'results', 'study_simples.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
