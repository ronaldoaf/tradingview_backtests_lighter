"""Cruzamento de medias moveis, 4h, carteira de 5 ativos (BTC, WTI, US100, XAU, XAG), 2020-2023.

8 tipos (HMA, KAMA, ALMA, ZLEMA, T3, FRAMA, VIDYA, McGinley) x 3 pares lenta/rapida (200/50, 100/30, 50/20).
Sempre posicionado (stop-and-reverse): long quando a rapida esta acima da lenta, short quando abaixo
(equivale a virar no cruzamento). Sinal no fechamento da barra, execucao na abertura da seguinte.
Custo CUSTO por perna (virada = 2 pernas), funding anual FUND pro-rata (long paga, short recebe).
XAG usa custo/funding do ouro. Carteira: 20% por ativo, 1x, media dos retornos diarios.
Dados cortados em 31/12/2023 ANTES de calcular qualquer coisa.
"""
import os, sys
import numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tvlib
from study_engulf_psar import CUSTO, FUND

D = tvlib.D
OUT = os.path.join(D, 'results', 'ma_cross_4h')
ATIVOS = ['btc', 'wti', 'us100', 'xau', 'xag']
INI, FIM = pd.Timestamp('2020-01-01', tz='UTC'), pd.Timestamp('2024-01-01', tz='UTC')
PARES = [(200, 50), (100, 30), (50, 20)]
CST = dict(CUSTO, xag=CUSTO['xau'])
FND = dict(FUND, xag=FUND['xau'])


def load(name):
    if name == 'xag':
        x = pd.read_parquet(os.path.join(D, 'data', 'duka1m_xag', 'all.parquet'))
        x = x[~x.index.duplicated()].sort_index()[tvlib.OHLCV]
        x = x[x.high >= x.low]
    else:
        x = tvlib.load_m1v(name)
    x = x[x.index < FIM]
    return tvlib.resample(x, '4h')


# ------------------------------------------------------------------ medias (convencoes do Pine/TradingView)
@njit(cache=True)
def ema(x, n):
    a = 2.0 / (n + 1); o = np.full(len(x), np.nan); s = np.nan
    for i in range(len(x)):
        if np.isnan(x[i]):
            continue
        s = x[i] if np.isnan(s) else a * x[i] + (1 - a) * s
        o[i] = s
    return o


def hma(c, n):
    return tvlib.hma(c, n)


@njit(cache=True)
def kama(c, n, fast=2, slow=30):
    o = np.full(len(c), np.nan); fsc = 2.0 / (fast + 1); ssc = 2.0 / (slow + 1)
    for i in range(n, len(c)):
        ch = abs(c[i] - c[i - n]); vol = 0.0
        for j in range(i - n + 1, i + 1):
            vol += abs(c[j] - c[j - 1])
        er = ch / vol if vol > 0 else 0.0
        sc = (er * (fsc - ssc) + ssc) ** 2
        prev = o[i - 1] if not np.isnan(o[i - 1]) else c[i - 1]
        o[i] = prev + sc * (c[i] - prev)
    return o


def alma(c, n, offset=0.85, sigma=6.0):
    m = offset * (n - 1); s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s)); w /= w.sum()
    o = np.full(len(c), np.nan)
    v = np.lib.stride_tricks.sliding_window_view(c, n)
    o[n - 1:] = v @ w
    return o


def zlema(c, n):
    lag = (n - 1) // 2
    src = c.copy(); src[lag:] = 2 * c[lag:] - c[:-lag]; src[:lag] = np.nan
    return ema(src, n)


def t3(c, n, v=0.7):
    e1 = ema(c, n); e2 = ema(e1, n); e3 = ema(e2, n); e4 = ema(e3, n); e5 = ema(e4, n); e6 = ema(e5, n)
    c1 = -v ** 3; c2 = 3 * v * v + 3 * v ** 3; c3 = -6 * v * v - 3 * v - 3 * v ** 3; c4 = 1 + 3 * v + v ** 3 + 3 * v * v
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


@njit(cache=True)
def frama(h, l, c, n):
    n = n + (n % 2); hn = n // 2
    o = np.full(len(c), np.nan)
    for i in range(n - 1, len(c)):
        h1 = np.max(h[i - hn + 1:i + 1]); l1 = np.min(l[i - hn + 1:i + 1])
        h2 = np.max(h[i - n + 1:i - hn + 1]); l2 = np.min(l[i - n + 1:i - hn + 1])
        h3 = np.max(h[i - n + 1:i + 1]); l3 = np.min(l[i - n + 1:i + 1])
        n1 = (h1 - l1) / hn; n2 = (h2 - l2) / hn; n3 = (h3 - l3) / n
        dim = (np.log(n1 + n2) - np.log(n3)) / np.log(2.0) if n1 > 0 and n2 > 0 and n3 > 0 else 1.0
        a = np.exp(-4.6 * (dim - 1.0)); a = min(max(a, 0.01), 1.0)
        prev = o[i - 1] if not np.isnan(o[i - 1]) else c[i]
        o[i] = a * c[i] + (1 - a) * prev
    return o


@njit(cache=True)
def vidya(c, n, m=9):
    a = 2.0 / (n + 1); o = np.full(len(c), np.nan)
    for i in range(m, len(c)):
        up = 0.0; dn = 0.0
        for j in range(i - m + 1, i + 1):
            d = c[j] - c[j - 1]
            if d > 0: up += d
            else: dn -= d
        k = abs((up - dn) / (up + dn)) if up + dn > 0 else 0.0
        prev = o[i - 1] if not np.isnan(o[i - 1]) else c[i]
        o[i] = a * k * c[i] + (1 - a * k) * prev
    return o


@njit(cache=True)
def mcginley(c, n):
    o = np.full(len(c), np.nan); o[0] = c[0]
    for i in range(1, len(c)):
        p = o[i - 1]
        o[i] = p + (c[i] - p) / (n * (c[i] / p) ** 4)
    return o


def ma(tipo, df, n):
    c = df.close.values.astype(float)
    if tipo == 'HMA': return hma(c, n)
    if tipo == 'KAMA': return kama(c, n)
    if tipo == 'ALMA': return alma(c, n)
    if tipo == 'ZLEMA': return zlema(c, n)
    if tipo == 'T3': return t3(c, n)
    if tipo == 'FRAMA': return frama(df.high.values.astype(float), df.low.values.astype(float), c, n)
    if tipo == 'VIDYA': return vidya(c, n)
    if tipo == 'MDMA': return mcginley(c, n)
    raise ValueError(tipo)


TIPOS = ['HMA', 'KAMA', 'ALMA', 'ZLEMA', 'T3', 'FRAMA', 'VIDYA', 'MDMA']
WARM = {'HMA': 1, 'KAMA': 1, 'ALMA': 1, 'ZLEMA': 1, 'T3': 3, 'FRAMA': 1, 'VIDYA': 3, 'MDMA': 3}  # x lenta


def daily(df, pos, name):
    """pos[i] = sinal no fechamento da barra i -> posicao de open[i+1] a open[i+2]."""
    o = df.open.values
    held = np.r_[0.0, pos[:-1]]                    # posicao vigente durante a barra i (open i -> open i+1)
    r = np.r_[o[1:] / o[:-1] - 1, 0.0]
    dt = np.r_[np.diff(df.index.values).astype('timedelta64[s]').astype(float), 0.0] / (365 * 86400)
    ch = np.abs(np.diff(np.r_[0.0, held]))          # pernas na abertura da barra i
    ret = held * r - ch * CST[name] - held * FND[name] / 100 * dt
    s = pd.Series(ret, df.index)
    s = s[(s.index >= INI)]
    return s.groupby(s.index.floor('D')).apply(lambda x: np.prod(1 + x) - 1), int((ch > 0).sum()), ch


def stats(d):
    d = d[(d.index >= INI) & (d.index < FIM)]
    eq = (1 + d).cumprod(); yrs = (d.index[-1] - d.index[0]).days / 365.25
    cagr = eq.iloc[-1] ** (1 / yrs) - 1; vol = d.std() * np.sqrt(365)
    sh = d.mean() / d.std() * np.sqrt(365); dd = (eq / eq.cummax() - 1).min()
    t = d.mean() / d.std() * np.sqrt(len(d))
    anos = {y: (1 + g).prod() - 1 for y, g in d.groupby(d.index.year)}
    return dict(cagr=cagr, vol=vol, sharpe=sh, dd=dd, t=t, **{str(y): v for y, v in anos.items()})


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {a: load(a) for a in ATIVOS}
    idx = pd.date_range(INI, FIM - pd.Timedelta('1D'), freq='D')
    rows, curvas = [], {}
    # buy & hold de referencia (sem funding e com funding do long)
    bh = {}
    for a in ATIVOS:
        df = data[a]; pos = np.ones(len(df)); pos[df.index < INI - pd.Timedelta('4h')] = 0
        bh[a] = daily(df, pos, a)[0].reindex(idx).fillna(0)
    curvas['BH'] = pd.concat(bh, axis=1).mean(axis=1)
    for tipo in TIPOS:
        for lenta, rapida in PARES:
            por = {}; ntr = {}
            for a in ATIVOS:
                df = data[a]
                f = ma(tipo, df, rapida); s = ma(tipo, df, lenta)
                ok = ~(np.isnan(f) | np.isnan(s))
                ok[:WARM[tipo] * lenta] = False
                pos = np.where(f > s, 1.0, -1.0); pos[~ok] = 0.0
                pos[df.index < INI - pd.Timedelta('4h')] = 0.0   # entra so a partir de 2020
                dr, n, _ = daily(df, pos, a)
                por[a] = dr.reindex(idx).fillna(0); ntr[a] = n
            cart = pd.concat(por, axis=1).mean(axis=1)
            nome = f'{tipo} {lenta}/{rapida}'
            curvas[nome] = cart
            st = stats(cart); st.update(cfg=nome, tipo=tipo, par=f'{lenta}/{rapida}', viradas=sum(ntr.values()))
            for a in ATIVOS:
                sa = stats(por[a]); st[f'{a}_cagr'] = sa['cagr']; st[f'{a}_sh'] = sa['sharpe']
            st['ativos_pos'] = sum(st[f'{a}_cagr'] > 0 for a in ATIVOS)
            st['anos_pos'] = sum(st[y] > 0 for y in ['2020', '2021', '2022', '2023'])
            st['corr_bh'] = cart.corr(curvas['BH'])
            rows.append(st)
            print(f"{nome:14s} CAGR {st['cagr']:+.1%} Sh {st['sharpe']:.2f} DD {st['dd']:.1%}")
    r = pd.DataFrame(rows).sort_values('sharpe', ascending=False)
    b = stats(curvas['BH']); b.update(cfg='Buy&hold 5 ativos (com funding)')
    for a in ATIVOS:
        sa = stats(bh[a]); b[f'{a}_cagr'] = sa['cagr']; b[f'{a}_sh'] = sa['sharpe']
    r = pd.concat([r, pd.DataFrame([b])], ignore_index=True)
    r.to_csv(os.path.join(OUT, 'ranking.csv'), index=False, float_format='%.4f')
    pd.DataFrame(curvas).to_csv(os.path.join(OUT, 'curvas_diarias.csv'), float_format='%.6f')
    print(f"BH: CAGR {b['cagr']:+.1%} Sh {b['sharpe']:.2f} DD {b['dd']:.1%}")


if __name__ == '__main__':
    main()
