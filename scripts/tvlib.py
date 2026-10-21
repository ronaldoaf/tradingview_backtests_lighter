"""Infra comum dos testes de estrategias do TradingView (lote 2026-10-21b:
Flawless Victory / Ichimoku+Hull+MacD / RSI Divergence).

Contem:
  - load_m1v / resample            : M1 com volume (ouro Dukascopy, BTC Binance, indices/WTI Duka)
  - rsi_wilder, mfi, hma, sma, stdev_pop, atr_rma : equivalentes dos ta.* do Pine v4
  - engine_bars                    : posicao por sinal, execucao na ABERTURA da barra seguinte,
                                     sem stop intrabar (serve Ichimoku e RSI-Div)
  - engine_sltp                    : long com stop/alvo percentuais resolvidos no M1 (serve Flawless v2/v3)
  - stats / control                : metricas (CAGR vs buy&hold, Sharpe, DD, expo) e controle aleatorio
                                     com MESMO lado, MESMA duracao e MESMA gestao

Convencoes de custo: CUSTO[ativo] por perna (spread medido na Lighter) e FUND[ativo] de funding anual
que o long paga (o short recebe), proporcional ao tempo em posicao. Retornos medidos sobre o nocional
(1x), que e o que o Pine faz com default_qty_type=percent_of_equity.
Convencao conservadora quando stop e alvo caem no MESMO minuto: o stop e executado primeiro.
"""
import os, sys
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO, FUND

OHLCV = ['open', 'high', 'low', 'close', 'volume']
RNG = np.random.default_rng(20261021)


# ------------------------------------------------------------------ dados
def load_m1v(name):
    import glob
    if name == 'xau':
        x = pd.read_parquet(os.path.join(D, 'data', 'gold', 'xau_1m.parquet'))
    elif name in ('us100', 'us500', 'wti'):
        fs = sorted(glob.glob(os.path.join(D, 'data', f'duka1m_{name}', '*.parquet')))
        x = pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f) > 0])
    else:
        sym = {'btc': 'BTCUSDT', 'eth': 'ETHUSDT'}[name]
        b = pd.read_parquet(os.path.join(D, 'data', 'binance', 'klines_1m', f'{sym}.parquet'))
        x = b.set_index(pd.to_datetime(b.ts, unit='ms', utc=True))[['o', 'h', 'l', 'c', 'v']].set_axis(
            OHLCV, axis=1)
    if 'volume' not in x.columns:
        x = x.assign(volume=1.0)
    x = x[~x.index.duplicated()].sort_index()[OHLCV]
    return x[x.high >= x.low]


def resample(m1, tf):
    agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    if 'volume' in m1.columns:
        agg['volume'] = 'sum'
    df = m1.resample(tf, label='left', closed='left').agg(agg).dropna()
    return df[df.high >= df.low]


# ------------------------------------------------------------------ indicadores (ta.* do Pine)
def rsi_wilder(c, n):
    d = np.diff(c, prepend=np.nan)
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    up[0] = dn[0] = np.nan
    u, v = rma_nan(up, n), rma_nan(dn, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(v == 0, 100.0, 100.0 - 100.0 / (1.0 + u / v))
    return np.where(np.isnan(u), np.nan, r)


def rma_nan(x, n):
    """ta.rma de serie que comeca com NaN (ta.change): seed = media das n primeiras validas."""
    out = np.full(len(x), np.nan)
    i0 = next((i for i in range(len(x)) if x[i] == x[i]), -1)
    if i0 < 0 or len(x) - i0 < n: return out
    out[i0 + n - 1] = np.mean(x[i0:i0 + n])
    a = 1.0 / n
    for i in range(i0 + n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def mfi(hlc3, vol, n):
    """ta.mfi: RSI do fluxo de dinheiro, com a mesma degeneracao do Pine (lower==0 -> 100)."""
    ch = np.diff(hlc3, prepend=np.nan)
    pos = np.where(ch > 0, vol * hlc3, 0.0)
    neg = np.where(ch < 0, vol * hlc3, 0.0)
    pos[0] = neg[0] = np.nan
    up = pd.Series(pos).rolling(n).sum().to_numpy()
    dn = pd.Series(neg).rolling(n).sum().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100.0 - 100.0 / (1.0 + up / dn)))
    return np.where(np.isnan(up), np.nan, r)


def wma(x, n):
    """ta.wma: pesos 1..n (o mais recente pesa n). Convolucao, com NaN propagado."""
    x = np.asarray(x, float)
    w = np.arange(1, n + 1, dtype=float); w /= w.sum()
    bad = np.isnan(x)
    out = np.convolve(np.where(bad, 0.0, x), w[::-1], mode='full')[:len(x)]
    out[:n - 1] = np.nan
    if bad.any():   # qualquer NaN na janela invalida a saida, como no Pine
        cnt = np.convolve(bad.astype(float), np.ones(n), mode='full')[:len(x)]
        out[cnt > 0] = np.nan
    return out


def hma(x, n):
    """ta.hma = wma(2*wma(x,n/2) - wma(x,n), sqrt(n)); o Pine usa int() nos comprimentos."""
    h = max(1, int(n / 2)); s = max(1, int(np.sqrt(n)))
    return wma(2 * wma(x, h) - wma(x, n), s)


def sma(x, n):
    return pd.Series(x).rolling(n).mean().to_numpy()


def stdev_pop(x, n):
    return pd.Series(x).rolling(n).std(ddof=0).to_numpy()


def atr_rma(h, l, c, n):
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return rma_nan(tr, n)


def xover(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    out = np.zeros(len(a), bool)
    out[1:] = (a[1:] > b[1:]) & (a[:-1] <= b[:-1])
    return out & ~np.isnan(a) & ~np.isnan(b)


def xunder(a, b):
    return xover(b, a)


def pivotlow(x, lbL, lbR):
    """ta.pivotlow: True na barra onde o pivo fica CONFIRMADO (o pivo esta em i-lbR)."""
    n = len(x); out = np.zeros(n, bool)
    for i in range(lbL + lbR, n):
        p = i - lbR; v = x[p]
        if v != v: continue
        w = x[p - lbL:p + lbR + 1]
        if np.isnan(w).any(): continue
        if v <= w.min() and (w < v).sum() == 0:
            out[i] = True
    return out


def pivothigh(x, lbL, lbR):
    return pivotlow(-np.asarray(x, float), lbL, lbR)


def valuewhen_prev(cond, src, occ=1):
    """valuewhen(cond, src, occ): valor de src na occ-esima ocorrencia ANTERIOR de cond (inclusiva)."""
    n = len(cond); out = np.full(n, np.nan)
    hist = []
    for i in range(n):
        if len(hist) > occ:
            out[i] = hist[-1 - occ]
        if cond[i]:
            hist.append(src[i])
            if len(hist) > occ:
                out[i] = hist[-1 - occ]
    return out


def barssince(cond):
    n = len(cond); out = np.full(n, np.nan); last = -1
    for i in range(n):
        if cond[i]: last = i
        if last >= 0: out[i] = i - last
    return out


# ------------------------------------------------------------------ varredura intrabar (M1)
@njit(cache=True)
def _first_touch(mo, mh, ml, a, b, slp, tpp, sl_first):
    """Primeiro minuto em [a,b) que toca stop ou alvo. Devolve (indice, preco, codigo)
    com codigo 1=stop, 2=alvo, 0=nada. A ABERTURA do minuto e testada antes do range, logo um
    gap que pula o nivel sai na abertura (pior que o nivel)."""
    for m in range(a, b):
        if mo[m] <= slp:
            return m, mo[m], 1
        if mo[m] >= tpp:
            return m, mo[m], 2
        hs = ml[m] <= slp; ht = mh[m] >= tpp
        if hs and (sl_first or not ht):
            return m, slp, 1
        if ht:
            return m, tpp, 2
    return -1, 0.0, 0


# ------------------------------------------------------------------ engines
def engine_bars(df, L, S, long_ok=True, short_ok=True, flat_on_opp=False, shift=1):
    """Posicao por sinal, execucao na ABERTURA da barra seguinte (como o Pine com
    calc_on_every_tick=false). pyramiding=0: sinal contrario inverte (ou apenas zera, se
    flat_on_opp). Devolve lista de trades (i_entrada, i_saida, lado)."""
    ev = []
    for i in np.where(L | S)[0]:
        j = i + shift
        if j < len(df):
            ev.append((j, 1 if L[i] else -1))
    tr = []; pos = 0; i0 = None
    for j, side in ev:
        ok = (side > 0 and long_ok) or (side < 0 and short_ok)
        if not ok:
            if flat_on_opp and pos != 0 and j > i0:
                tr.append((i0, j, pos)); pos, i0 = 0, None
            continue
        if side == pos: continue
        if pos != 0 and j > i0:
            tr.append((i0, j, pos))
        pos, i0 = side, j
    return tr


def engine_signal_exit(df, L, X, maxunits=1):
    """Long-only com entrada por sinal e saida por sinal, ambas na abertura da barra seguinte.
    maxunits>1 reproduz pyramiding: unidades adicionais com preco medio. Devolve
    (i_entrada, i_saida, unidades, preco_medio_de_entrada)."""
    o = df.open.to_numpy(float)
    n = len(df); tr = []
    units = 0; i0 = None; cost = 0.0
    for i in range(n - 1):
        j = i + 1
        if X[i] and units > 0:
            tr.append((i0, j, units, cost / units)); units = 0; i0 = None; cost = 0.0
            continue
        if L[i] and units < maxunits:
            if units == 0: i0 = j
            units += 1; cost += o[j]
    return tr


def engine_sltp(df, m1, L, X, sl, tp, ord_sl_first=True):
    """Long-only: entrada na abertura da barra seguinte ao sinal; stop em entry*(1-sl) e alvo em
    entry*(1+tp) ativos desde a entrada e resolvidos minuto a minuto no M1 (a abertura de cada
    minuto e testada primeiro, logo um gap que pula o stop sai NA ABERTURA); saida por sinal
    contrario na abertura da barra seguinte, se nada tiver sido tocado antes.
    sl/tp <= 0 desligam a protecao. Devolve (t_in, t_out, entry, exit, motivo, i, j)."""
    o = df.open.to_numpy(float)
    tix = df.index.to_numpy()
    mi = m1.index
    mo = m1.open.to_numpy(float); mh = m1.high.to_numpy(float); ml = m1.low.to_numpy(float)
    n = len(df); out = []
    i = 0
    while i < n - 1:
        if not L[i]:
            i += 1; continue
        j0 = i + 1
        ent = o[j0]
        # barra de saida por sinal: primeira barra >= j0 com sinal de saida -> sai na seguinte
        k = j0
        while k < n - 1 and not X[k]:
            k += 1
        jx = min(k + 1, n - 1)
        t_in = tix[j0]; t_out = tix[jx]
        a = mi.searchsorted(t_in); b = mi.searchsorted(t_out)
        px = o[jx]; why = 'sinal'
        if sl > 0 or tp > 0:
            slp = ent * (1 - sl) if sl > 0 else -np.inf
            tpp = ent * (1 + tp) if tp > 0 else np.inf
            m, pxh, code = _first_touch(mo, mh, ml, a, min(b, len(mi)), slp, tpp, ord_sl_first)
            if code:
                px = pxh; why = 'stop' if code == 1 else 'alvo'; t_out = mi[m]
        # indice de barra efetivo da saida (p/ exposicao e controle): a barra que contem t_out
        jeff = jx if why == 'sinal' else max(int(df.index.searchsorted(pd.Timestamp(t_out),
                                                                      side='right')), j0 + 1)
        out.append((t_in, t_out, ent, px, why, j0, min(jeff, n - 1)))
        if why == 'sinal':
            i = max(jx, j0 + 1)
        else:
            # stop/alvo tocado dentro da barra: a estrategia volta a poder comprar na barra seguinte
            i = max(int(df.index.searchsorted(pd.Timestamp(t_out))) + 1, j0 + 1)
    return out


# ------------------------------------------------------------------ contabilidade / metricas
def book(df, tr, name, with_fund=True):
    """tr = lista de (i, j, lado) [ou (i, j, unid, preco_medio)]. Preco de execucao = abertura."""
    o = df.open.to_numpy(float)
    rows = []
    for t in tr:
        if len(t) == 3:
            i, j, d = t; u = 1.0; ent = o[i]
        else:
            i, j, u, ent = t; d = 1.0
        yrs = (df.index[j] - df.index[i]).total_seconds() / (365 * 86400)
        bruto = d * (o[j] / ent - 1)
        rows.append((df.index[i], df.index[j], i, j, d, u, ent, o[j], bruto, yrs))
    out = pd.DataFrame(rows, columns=['t_in', 't_out', 'i', 'j', 'd', 'u', 'entry', 'exit', 'bruto', 'yrs'])
    return _cost(out, name, with_fund)


def book_sltp(df, tr, name, with_fund=True):
    rows = []
    for t_in, t_out, ent, ex, why, i, j in tr:
        yrs = (pd.Timestamp(t_out) - pd.Timestamp(t_in)).total_seconds() / (365 * 86400)
        rows.append((pd.Timestamp(t_in), pd.Timestamp(t_out), i, j, 1.0, 1.0, ent, ex,
                     ex / ent - 1, yrs, why))
    out = pd.DataFrame(rows, columns=['t_in', 't_out', 'i', 'j', 'd', 'u', 'entry', 'exit',
                                      'bruto', 'yrs', 'motivo'])
    return _cost(out, name, with_fund)


def _cost(out, name, with_fund):
    if len(out) == 0: return out
    cst = CUSTO[name]
    out['fund'] = (FUND.get(name, 5.0) / 100 * out.yrs * out.d) if with_fund else 0.0
    out['ret_sf'] = out.bruto - 2 * cst
    out['ret'] = out.ret_sf - out.fund
    return out


def equity(df, tr, name, dcol='d'):
    """serie de equity a 1x (log) para Sharpe/DD/expo, com custo na mudanca de posicao e funding."""
    pos = pd.Series(0.0, index=df.index)
    for _, r in tr.iterrows():
        pos.iloc[int(r.i):int(r.j)] = r[dcol] * r.u
    r = np.log(df.close).diff().fillna(0.0) * pos.shift(1).fillna(0.0)
    chg = pos.diff().abs().fillna(0.0)
    fr = FUND.get(name, 5.0) / 100 * (
        df.index.to_series().diff().dt.total_seconds() / (365 * 86400)).fillna(0.0)
    r = r - chg * CUSTO[name] - pos.shift(1).fillna(0.0) * fr
    dd_eq = r.cumsum()
    dly = r.resample('1D').sum(); dly = dly[dly != 0]
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
    return dict(cagr=float(np.expm1(dd_eq.iloc[-1] / yrs)),
                sharpe=float(dly.mean() / dly.std() * np.sqrt(252)) if dly.std() else np.nan,
                dd=float((dd_eq - dd_eq.cummax()).min()), expo=float((pos != 0).mean()))


@njit(cache=True)
def _ctl_sltp(o, b2m, mmin, mo, mh, ml, starts, durs, sides, sl, tp, sl_first, cst, fund):
    """Controle com stop/alvo: nsim x ntrades entradas sorteadas, mesma gestao, tudo em njit."""
    nsim, ntr = starts.shape
    out = np.zeros(nsim)
    for s in range(nsim):
        acc = 0.0
        for k in range(ntr):
            i = starts[s, k]; j = i + durs[k]
            ent = o[i]; px = o[j]
            a = b2m[i]; b = b2m[j]
            mout = b
            if sl > 0.0 or tp > 0.0:
                slp = ent * (1.0 - sl) if sl > 0.0 else -1e18
                tpp = ent * (1.0 + tp) if tp > 0.0 else 1e18
                m, pxh, code = _first_touch(mo, mh, ml, a, b, slp, tpp, sl_first)
                if code != 0:
                    px = pxh; mout = m
            yrs = (mmin[mout] - mmin[a]) / (365.0 * 1440.0)
            acc += sides[k] * (px / ent - 1.0) - 2.0 * cst - fund * yrs * sides[k]
        out[s] = acc / ntr
    return out


def control_dur(df, trades, name, nsim=20, sl=0.0, tp=0.0, m1=None):
    """Controle: para cada trade real, nsim entradas a mercado em barras sorteadas, com o MESMO
    lado, a MESMA duracao maxima em barras e a MESMA gestao (stop/alvo, quando houver).
    Isola o que o GATILHO acrescenta sobre entrar no acaso com a mesma gestao."""
    o = df.open.to_numpy(float)
    n = len(df)
    res = np.zeros(nsim)
    durs = np.maximum(1, (trades.j.to_numpy(int) - trades.i.to_numpy(int)))
    sides = trades.d.to_numpy(float)
    if sl > 0 or tp > 0:
        starts = np.empty((nsim, len(durs)), np.int64)
        for s in range(nsim):
            starts[s] = RNG.integers(0, np.maximum(n - durs - 1, 1))
        b2m = m1.index.searchsorted(df.index).astype(np.int64)
        mmin = (m1.index.as_unit('s').asi8 // 60).astype(np.float64)
        return _ctl_sltp(o, b2m, mmin, m1.open.to_numpy(float), m1.high.to_numpy(float),
                         m1.low.to_numpy(float), starts, durs.astype(np.int64), sides,
                         float(sl), float(tp), True, CUSTO[name], FUND.get(name, 5.0) / 100)
    for s in range(nsim):
        acc = []
        for _, r in trades.iterrows():
            dur = max(1, int(r.j) - int(r.i))
            i = int(RNG.integers(0, n - dur - 1))
            j = i + dur
            ent = o[i]; px = o[j]; t_out = df.index[j]
            if sl > 0 or tp > 0:
                slp = ent * (1 - sl) if sl > 0 else -np.inf
                tpp = ent * (1 + tp) if tp > 0 else np.inf
                a = mi.searchsorted(df.index[i]); b = mi.searchsorted(df.index[j])
                for m in range(a, min(b, len(mi))):
                    if mo[m] <= slp: px, t_out = mo[m], mi[m]; break
                    if mo[m] >= tpp: px, t_out = mo[m], mi[m]; break
                    if ml[m] <= slp: px, t_out = slp, mi[m]; break
                    if mh[m] >= tpp: px, t_out = tpp, mi[m]; break
            yrs = (t_out - df.index[i]).total_seconds() / (365 * 86400)
            acc.append(r.d * (px / ent - 1) - 2 * CUSTO[name] - FUND.get(name, 5.0) / 100 * yrs * r.d)
        res[s] = np.mean(acc)
    return res


def summarize(df, trades, name, nsim=20, sl=0.0, tp=0.0, m1=None, minimo=10):
    if trades is None or len(trades) < minimo:
        return None
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
    st = equity(df, trades, name)
    bh = float(np.expm1(np.log(df.close.iloc[-1] / df.close.iloc[0]) / yrs))
    ctl = control_dur(df, trades, name, nsim=nsim, sl=sl, tp=tp, m1=m1)
    mu = trades.ret.mean()
    t = (mu - ctl.mean()) / (ctl.std(ddof=1) + 1e-12)
    return dict(trades=len(trades), por_ano=len(trades) / yrs,
                bp_bruto=1e4 * trades.bruto.mean(), bp_liq=1e4 * mu, bp_sf=1e4 * trades.ret_sf.mean(),
                win=float((trades.ret > 0).mean()), dias=float(trades.yrs.mean() * 365),
                cagr=st['cagr'], bh=bh, sharpe=st['sharpe'], dd=st['dd'], expo=st['expo'],
                ctl_bp=1e4 * ctl.mean(), t=t)


FMT = ('{trades:4d} tr ({por_ano:5.1f}/ano, {dias:6.2f}d) | bruto {bp_bruto:+7.1f}bp liq {bp_liq:+7.1f}bp'
       ' (win {win:.0%}) | CAGR {cagr:+7.1%} vs B&H {bh:+7.1%} | Sh {sharpe:+5.2f} DD {dd:6.0%}'
       ' expo {expo:4.0%} | ctl {ctl_bp:+7.1f}bp t={t:+5.2f}')


def line(tag, o):
    print(f"  {tag:<34} " + FMT.format(**o))
