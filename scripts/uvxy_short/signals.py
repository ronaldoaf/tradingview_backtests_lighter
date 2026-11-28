"""Sinais de regime para o short no UVXY. Todos retornam serie booleana/0-1 decidida no
fechamento do dia t (usa apenas dados ate t). 1 = pode ficar vendido."""
import numpy as np
import pandas as pd


def sma(x, n):
    return x.rolling(n, min_periods=n).mean()


def hv(px, n):
    r = np.log(px).diff()
    return r.rolling(n, min_periods=n).std() * np.sqrt(252) * 100


def ts(D, th=1.0):
    """Estrutura a termo: VIX/VIX3M abaixo de th (contango)."""
    return (D.ts < th).astype(float).where(D.ts.notna())


def ts_hyst(D, th_in=0.95, th_out=1.0):
    """Entra quando VIX/VIX3M < th_in, sai quando > th_out."""
    x = D.ts.values; out = np.full(len(x), np.nan); st = 0.0
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        if st == 0 and v < th_in:
            st = 1.0
        elif st == 1 and v > th_out:
            st = 0.0
        out[i] = st
    return pd.Series(out, index=D.index)


def ts9(D, th=1.0):
    """VIX9D/VIX abaixo de th (curto prazo em contango)."""
    r = D.vix9d / D.vix
    return (r < th).astype(float).where(r.notna())


def vix_ma(D, n=10, k=1.0):
    """VIX abaixo de k * media de n dias (vol caindo)."""
    m = sma(D.vix, n)
    return (D.vix < k * m).astype(float).where(m.notna())


def px_ma(D, col='c', n=10):
    """Preco do UVXY abaixo da media de n dias."""
    m = sma(D[col], n)
    return (D[col] < m).astype(float).where(m.notna())


def vrp(D, n=10, m=0.0):
    """Premio de risco de variancia: VIX - vol realizada do S&P (n dias) > m."""
    h = hv(D.spx, n)
    return ((D.vix - h) > m).astype(float).where(h.notna())


def vix_lvl(D, L=25):
    return (D.vix < L).astype(float).where(D.vix.notna())


def volsize(D, col='c', n=20, target=0.5, wmax=1.0):
    """Tamanho por alvo de vol: target / vol realizada anualizada do UVXY (n dias), limitado a wmax."""
    r = np.log(D[col]).diff()
    s = r.rolling(n, min_periods=n).std() * np.sqrt(252)
    return (target / s).clip(upper=wmax)


def ts_size(D, lo=0.8, hi=1.0, wmax=1.0):
    """Tamanho linear na estrutura a termo: wmax quando VIX/VIX3M <= lo, 0 quando >= hi."""
    x = ((hi - D.ts) / (hi - lo)).clip(0, 1) * wmax
    return x.where(D.ts.notna())
