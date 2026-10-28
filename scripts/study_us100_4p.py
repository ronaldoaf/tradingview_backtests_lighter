"""Reroda a grade de um lote so no US100, com os dados cortados no fim da 4a de 5 partes iguais no tempo (a 5a e OOS
e nao e carregada). Cada celula ganha o lucro liquido composto (custo e funding) dos trades que entram em cada uma
das 4 partes (p1..p4) e no total (tot). Pula o controle aleatorio e as metricas de equity para ir rapido.
Grava results/us100_4p/loteN.csv.
uso: python study_us100_4p.py N"""
import os, sys, importlib
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

_load = T.load_m1v
A = os.environ.get('ATIVO', 'us100')   # ATIVO=wti etc.
B = {}; SER = []; FULL = os.environ.get('FULL') == '1'   # FULL=1: dados todos, para medir o OOS das ja escolhidas


def load_4p(name):
    m1 = _load(name); t0, t1 = m1.index[0], m1.index[-1]
    B['cortes'] = [t0 + (t1 - t0) * k / 5 for k in range(5)]
    return m1 if FULL else m1[m1.index < B['cortes'][4]]


def summarize(df, trades, name, *a, minimo=10, **k):
    if trades is None or len(trades) < minimo: return None
    c = B['cortes']; ti = pd.DatetimeIndex(trades.t_in); g = np.log1p(np.clip(trades.u * trades.ret, -0.999, None))
    o = {f'p{q + 1}': float(np.expm1(g[(ti >= c[q]) & (ti < (c[q + 1] if q < 3 else c[4]))].sum())) for q in range(4)}
    o['tot'] = float(np.expm1(g.sum()))
    if FULL or all(o[f'p{q}'] > 0 for q in range(1, 5)):   # guarda o retorno diario das celulas que passam
        o['sid'] = len(SER); SER.append(T.equity_curve(df, trades, name).resample('1D').last().dropna().pct_change().fillna(0.0))
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400); mu = trades.ret.mean()
    o.update(trades=len(trades), por_ano=len(trades) / yrs, bp_bruto=1e4 * trades.bruto.mean(), bp_liq=1e4 * mu,
             bp_sf=1e4 * trades.ret_sf.mean(), win=float((trades.ret > 0).mean()), dias=float(trades.yrs.mean() * 365),
             cagr=o['tot'], bh=0.0, sharpe=0.0, bh_sharpe=0.0, dd=0.0, expo=0.0, ctl_bp=0.0, t=0.0)
    return o


T.load_m1v = load_4p; T.summarize = summarize
N = sys.argv[1]; MOD = f'study_tvlote{N}' if N.isdigit() else f'study_{N}'
OUT = os.path.join(D, 'results', A + '_4p' + ('_full' if FULL else ''), f'lote{N}.csv')
_csv = pd.DataFrame.to_csv
def to_csv(self, path=None, *a, **k):
    if isinstance(path, str) and A in os.path.basename(path):
        suf = '' if 'grid' in path else '_' + os.path.basename(path)[:-4].rsplit('_', 1)[-1]
        return _csv(self.assign(lote=N + suf), OUT[:-4] + suf + '.csv', index=False)
pd.DataFrame.to_csv = to_csv
import builtins; _print = builtins.print
builtins.print = lambda *a, **k: None   # silencia o log das celulas
L = importlib.import_module(MOD)
L.main([A])
builtins.print = _print
if SER: pd.DataFrame({i: x for i, x in enumerate(SER)}).fillna(0.0).to_parquet(OUT[:-4] + '_ser.parquet')
print(N, 'ok' if os.path.exists(OUT) else 'SEM CSV')
