"""Carteira 4h (jan/2020 a dez/2023): roda a grade de um lote num ativo so no grafico de 4h e grava, por celula, o
retorno diario a 1x (custo da Lighter e funding inclusos, via tvlib.equity_curve). 2024+ nao e carregado (holdout).
Gravacao: results/cart4h/<ATIVO>/loteN.csv (celulas com sid) e loteN_ser.parquet (retorno diario por sid).
uso: ATIVO=btc python scripts/cart4h_lote.py N"""
import os, sys, importlib
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

A = os.environ['ATIVO']; INI = pd.Timestamp(os.environ.get('INI', '2020-01-01'), tz='UTC'); FIM = pd.Timestamp(os.environ.get('FIM', '2024-01-01'), tz='UTC')
TF = '4h'; SER = []; _load = T.load_m1v; H4 = pd.Timedelta(TF)


def load(name):
    m1 = _load(name); m1.index = m1.index.as_unit('ns')
    return m1[(m1.index >= INI) & (m1.index < FIM)]


def summarize(df, trades, name, *a, minimo=10, **k):
    if len(df) < 3 or pd.Series(df.index[:200]).diff().median() != H4: return None   # so 4h
    if trades is None or len(trades) < minimo: return None
    o = dict(sid=len(SER))
    SER.append(T.equity_curve(df, trades, name).resample('1D').last().dropna().pct_change().fillna(0.0).astype('float32'))
    o.update(trades=len(trades), bp_liq=1e4 * trades.ret.mean(), win=float((trades.ret > 0).mean()),
             dias=float(trades.yrs.mean() * 365), longs=int((trades.d > 0).sum()) if 'd' in trades else -1,
             cagr=0.0, bh=0.0, sharpe=0.0, bh_sharpe=0.0, dd=0.0, expo=0.0, ctl_bp=0.0, t=0.0, por_ano=0.0, bp_bruto=0.0, bp_sf=0.0)
    return o


T.load_m1v = load; T.summarize = summarize
N = sys.argv[1]; MOD = f'study_tvlote{N}' if N.isdigit() else f'study_{N}'
OUT = os.path.join(D, 'results', 'cart4h', A, f'lote{N}.csv'); os.makedirs(os.path.dirname(OUT), exist_ok=True)
if os.path.exists(OUT) and os.path.exists(OUT[:-4] + '_ser.parquet'): print(N, A, 'ok (ja existia)'); sys.exit()
_csv = pd.DataFrame.to_csv
def to_csv(self, path=None, *a, **k):
    if isinstance(path, str) and A in os.path.basename(path):
        suf = '' if 'grid' in path else '_' + os.path.basename(path)[:-4].rsplit('_', 1)[-1]
        if suf: return
        return _csv(self.assign(lote=N), OUT, index=False)
pd.DataFrame.to_csv = to_csv
import builtins; _print = builtins.print
builtins.print = lambda *a, **k: None
L = importlib.import_module(MOD)
for m in ([] if os.environ.get('NOPATCH') else list(sys.modules.values())):   # so 4h em todos os modulos de estudo carregados
    if getattr(m, '__name__', '').startswith('study_'):
        if hasattr(m, 'TFS'): m.TFS = [TF]
        if isinstance(getattr(m, 'TF_EST', None), dict): m.TF_EST = {k: [TF] for k in m.TF_EST}
L.main([A])
builtins.print = _print
if SER: pd.DataFrame({i: x for i, x in enumerate(SER)}).fillna(0.0).to_parquet(OUT[:-4] + '_ser.parquet')
print(N, A, 'ok' if os.path.exists(OUT) else 'SEM CSV', len(SER))
