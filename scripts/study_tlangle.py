"""Trendline Angle Pro V6 (Degree + Strategy) - "Sanjay Dewan" / TradingView (DUCODGjC) - traducao fiel
do Pine v6 (fonte aberta baixada do pine-facade, PUB;d12a6a1e3c9d461b99b243c34ca80a99) e teste em ouro
com M1 da Dukascopy.

ATENCAO: no Pine, TODO o aparato de trendlines por pivo, leg de swing maior, fan 20/40/45 graus e
assinatura e PURAMENTE VISUAL - nenhuma dessas linhas entra em longSig/shortSig. O que a estrategia
realmente negocia e um filtro de inclinacao da regressao linear + duas EMAs + cruzamento. Traduzo so
o que decide trade (e registro os angulos de pivo para conferir que nao mudam nada).

Regras (defaults do Pine entre parenteses):
  angulo  : slope = ta.linreg(close, regLen, 0) - ta.linreg(close, regLen, 1)  (regLen=20) = inclinacao
            OLS por barra; angR = atan(slope / ATR(atrLen=14) * k45) em graus, k45=5 (ou seja, 0,2 ATR
            por barra = 45 graus). Zonas: |a| >= steepAng (45) "Steep", >= modAng (20) "Moderate", senao "Flat".
  entrada : angUp = angR >= minEntry (20) e (allowSteep (true) ou angR < steepAng);
            trendUp = EMA(9) > EMA(50) e close > EMA(50);
            longSig = angUp e trendUp e ta.crossover(close, EMA(9));  short = espelhado.
            Sinal no fechamento, ordem a mercado na ABERTURA da barra seguinte (calc_on_every_tick=false).
            pyramiding=0, entao sinal contrario com posicao aberta INVERTE (strategy.entry no lado oposto).
  saidas  : strategy.exit com stop = entrada -/+ entATR x slMult (1,5) e limit a rr (2,0) x isso,
            onde entATR e o ATR da BARRA DO SINAL e a entrada e strategy.position_avg_price (o fill).
            exitFlat (true): se |angR| < modAng (20) no fechamento, strategy.close -> sai no proximo open.
            Logo 1R = 1,5 ATR e o alvo = 2R. Stop FIXO, sem trilha, sem parcial.
            QUIRK FIEL: strategy.exit so e chamado quando position_size != 0, isto e, no fechamento da
            barra JA preenchida, logo a barra de entrada fica SEM stop e SEM alvo (PROT=0 reproduz isso;
            PROT=1 protege desde a entrada).
  tamanho : 10% do equity, commission 0,05% por perna no Pine. Medimos em R (1 trade = 1R), e o custo
            entra como CUSTO['xau'] = 0,75 bp por perna (spread medido na Lighter) - BEM menor que os
            5 bp/perna que o proprio Pine assume. Tambem reporto o cenario com os 5 bp do autor.

Execucao aqui: sinais no TF alto (15m/30m/1h/4h) a partir do M1; dentro do trade andamos no M1, de forma
que stop/alvo/gap de fim de semana sao resolvidos minuto a minuto. Convencao conservadora ORD=0 (stop
antes do alvo no mesmo minuto) e otimista ORD=1 para contraste. A abertura de cada M1 e testada primeiro,
entao um gap que pula o stop sai NA ABERTURA (pior que o stop), como na vida real.
Controle: para cada trade, 20 entradas a mercado em minutos sorteados (mesmo lado, mesmo risco relativo,
mesma estrutura 1R/2R e mesma duracao maxima) -> mede o que o filtro de angulo acrescenta sobre o acaso.

uso: python study_tlangle.py [xau us100 btc ...]
"""
import os, sys, glob, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO

OHLC = ['open', 'high', 'low', 'close']
TFS = {'15min': 15, '30min': 30, '1h': 60, '4h': 240}
BASE = dict(TF='1h', ATRLEN=14, K45=5.0, REGLEN=20, PVLEN=5, STEEP=45.0, MOD=20.0,
            LONG=1, SHORT=1, STEEPOK=1, MINENTRY=20.0, FAST=9, SLOW=50,
            SLMULT=1.5, RR=2.0, EXITFLAT=1, ORD=0, PROT=0)


def load_m1(name):
    if name == 'xau':
        x = pd.read_parquet(os.path.join(D, 'data', 'gold', 'xau_1m.parquet'))
    elif name in ('us100', 'us500', 'wti'):
        fs = sorted(glob.glob(os.path.join(D, 'data', f'duka1m_{name}', '*.parquet')))
        x = pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f) > 0])
    else:
        b = pd.read_parquet(os.path.join(D, 'data', 'binance', 'klines_1m', 'BTCUSDT.parquet'))
        x = b.set_index(pd.to_datetime(b.ts, unit='ms', utc=True))[['o', 'h', 'l', 'c']].set_axis(OHLC, axis=1)
    x = x[~x.index.duplicated()].sort_index()[OHLC]
    return x[x.high >= x.low]


def minutes(idx):
    return idx.as_unit('s').asi8 // 60


def resample(m1, tf):
    df = m1.resample(tf, label='left', closed='left').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    return df[df.high >= df.low]


# ---------------------------------------------------------------- indicadores (iguais aos ta.* do Pine)
@njit(cache=True)
def rma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n: return out
    s = 0.0
    for i in range(n): s += x[i]
    out[n - 1] = s / n
    a = 1.0 / n
    for i in range(n, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


@njit(cache=True)
def ema(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n: return out
    s = 0.0
    for i in range(n): s += x[i]
    out[n - 1] = s / n
    a = 2.0 / (n + 1)
    for i in range(n, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


@njit(cache=True)
def true_range(h, l, c):
    tr = np.empty(len(c)); tr[0] = h[0] - l[0]
    for i in range(1, len(c)):
        a = h[i] - l[i]; b = abs(h[i] - c[i - 1]); d = abs(l[i] - c[i - 1])
        tr[i] = max(a, max(b, d))
    return tr


@njit(cache=True)
def linreg_slope(c, n):
    """ta.linreg(c,n,0) - ta.linreg(c,n,1) = inclinacao OLS por barra na janela de n barras."""
    out = np.full(len(c), np.nan)
    sx = 0.0; sxx = 0.0
    for k in range(n):
        sx += k; sxx += k * k
    den = n * sxx - sx * sx
    for i in range(n - 1, len(c)):
        sy = 0.0; sxy = 0.0
        for k in range(n):
            y = c[i - n + 1 + k]
            sy += y; sxy += k * y
        out[i] = (n * sxy - sx * sy) / den
    return out


@njit(cache=True)
def pivot_angles(h, l, k, atr, k45):
    """upAng/dnAng do Pine (so para auditoria: nao entram em nenhum sinal).

    ta.pivotlow/pivothigh(k,k) confirmam k barras depois; a linha so e desenhada quando o novo pivo
    e mais alto (lows) / mais baixo (highs) que o anterior, e o angulo usa o ATR da barra corrente.
    """
    n = len(h); upA = np.full(n, np.nan); dnA = np.full(n, np.nan)
    lo1 = np.nan; lo2 = np.nan; lo1b = -1; lo2b = -1
    hi1 = np.nan; hi2 = np.nan; hi1b = -1; hi2b = -1
    cu = np.nan; cd = np.nan
    for i in range(n):
        p = i - k
        if p >= k:
            okh = True; okl = True
            for d in range(1, k + 1):
                if not (h[p] > h[p - d] and h[p] >= h[p + d]): okh = False
                if not (l[p] < l[p - d] and l[p] <= l[p + d]): okl = False
            if okl:
                lo1 = lo2; lo1b = lo2b; lo2 = l[p]; lo2b = p
                if lo1 == lo1 and lo2 > lo1 and atr[i] == atr[i] and atr[i] > 0:
                    dx = max(float(lo2b - lo1b), 1.0); dy = (lo2 - lo1) / atr[i]
                    cu = np.arctan(dy / dx * k45) * 180.0 / np.pi
            if okh:
                hi1 = hi2; hi1b = hi2b; hi2 = h[p]; hi2b = p
                if hi1 == hi1 and hi2 < hi1 and atr[i] == atr[i] and atr[i] > 0:
                    dx = max(float(hi2b - hi1b), 1.0); dy = (hi2 - hi1) / atr[i]
                    cd = np.arctan(dy / dx * k45) * 180.0 / np.pi
        upA[i] = cu; dnA[i] = cd
    return upA, dnA


# ---------------------------------------------------------------- motor de execucao
@njit(cache=True)
def engine(i0, i1, buy, sell, flat, entatr, slmult, rr, t1, o1, h1, l1, c1, ordem, prot):
    """Sinal no fechamento da barra alta j, ordem na abertura de j+1; stop/alvo andam no M1.

    out: tent texit fill risk side R why  (why: 0 stop, 1 alvo, 2 angulo flat, 3 fim, 4 inversao)
    """
    n = len(i0)
    out = np.zeros((n + 4, 7))
    q = 0; pos = 0; pend = 0
    fill = 0.0; risk = 0.0; sl = 0.0; tp = 0.0; tent = 0.0; ebar = -1
    atr_new = 0.0
    for j in range(n):
        a, b = i0[j], i1[j]
        if b <= a: continue
        # --- abertura da barra j: executa o que foi decidido no fechamento de j-1
        if pend != 0:
            px = o1[a]
            if pos != 0:
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk
                out[q, 6] = 2.0 if pend == 2 else 4.0
                q += 1; pos = 0
            if pend == 1 or pend == -1:
                pos = pend; fill = px; risk = atr_new * slmult
                sl = fill - pos * risk; tp = fill + pos * rr * risk
                tent = t1[a]; ebar = j
            pend = 0
        # --- caminhada no M1 dentro da barra j (ordens ativas so na barra seguinte a entrada, PROT=0)
        if pos != 0 and (prot == 1 or j > ebar):
            for i in range(a, b):
                s = pos
                if (o1[i] - sl) * s <= 0:                     # gap atravessa o stop -> sai na abertura
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = (o1[i] - fill) * s / risk; out[q, 6] = 0.0
                    q += 1; pos = 0; break
                if (o1[i] - tp) * s >= 0:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = (o1[i] - fill) * s / risk; out[q, 6] = 1.0
                    q += 1; pos = 0; break
                hi = h1[i] if s == 1 else -l1[i]
                lo = l1[i] if s == 1 else -h1[i]
                ssl = sl if s == 1 else -sl
                stp = tp if s == 1 else -tp
                hitsl = lo <= ssl; hittp = hi >= stp
                if ordem == 0 and hitsl:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = -1.0; out[q, 6] = 0.0
                    q += 1; pos = 0; break
                if hittp:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = rr; out[q, 6] = 1.0
                    q += 1; pos = 0; break
                if ordem == 1 and hitsl:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = -1.0; out[q, 6] = 0.0
                    q += 1; pos = 0; break
        # --- fechamento da barra j: decide a ordem da proxima abertura
        atr_new = entatr[j]
        if pos > 0:
            if sell[j] == 1: pend = -1                        # pyramiding=0 -> inverte
            elif flat[j] == 1: pend = 2
        elif pos < 0:
            if buy[j] == 1: pend = 1
            elif flat[j] == 1: pend = 2
        else:
            if buy[j] == 1: pend = 1
            elif sell[j] == 1: pend = -1
    if pos != 0:
        px = c1[len(c1) - 1]
        out[q, 0] = tent; out[q, 1] = t1[len(t1) - 1]; out[q, 2] = fill; out[q, 3] = risk
        out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 3.0
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, riscoRel, dur, rr, t1, o1, h1, l1, c1, ordem):
    """entrada a mercado num minuto sorteado: mesmo lado, mesmo risco relativo, 1R/2R, mesma duracao."""
    m = len(starts); out = np.zeros(m)
    for z in range(m):
        s0 = starts[z]; sg = side[z]; fill = o1[s0]
        risk = abs(fill) * riscoRel[z]
        sl = fill - sg * risk; tp = fill + sg * rr * risk
        acc = 0.0; done = 0
        for i in range(s0, len(c1)):
            if t1[i] - t1[s0] > dur[z]:
                acc = (c1[i] - fill) * sg / risk; done = 1; break
            hi = h1[i] if sg == 1 else -l1[i]
            lo = l1[i] if sg == 1 else -h1[i]
            ssl = sl if sg == 1 else -sl
            stp = tp if sg == 1 else -tp
            hitsl = lo <= ssl; hittp = hi >= stp
            if ordem == 0 and hitsl:
                acc = -1.0; done = 1; break
            if hittp:
                acc = rr; done = 1; break
            if ordem == 1 and hitsl:
                acc = -1.0; done = 1; break
        if done == 0:
            acc = (c1[len(c1) - 1] - fill) * sg / risk
        out[z] = acc
    return out


# ---------------------------------------------------------------- montagem dos sinais
_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'risk', 'side', 'R', 'why']


def build(name, m1, p):
    key = (name, p['TF'], p['ATRLEN'], p['K45'], p['REGLEN'], p['PVLEN'], p['FAST'], p['SLOW'])
    if key in _CACHE: return _CACHE[key]
    htf = resample(m1, p['TF'])
    o, h, l, c = (htf[k].to_numpy(np.float64) for k in OHLC)
    atr = rma(true_range(h, l, c), p['ATRLEN'])
    slope = linreg_slope(c, p['REGLEN'])
    with np.errstate(invalid='ignore', divide='ignore'):
        angR = np.arctan(slope / atr * p['K45']) * 180.0 / np.pi
    emaF = ema(c, p['FAST']); emaS = ema(c, p['SLOW'])
    upA, dnA = pivot_angles(h, l, p['PVLEN'], atr, p['K45'])
    A = dict(htf=htf, atr=atr, angR=angR, emaF=emaF, emaS=emaS, upA=upA, dnA=dnA,
             c=c, o=o, h=h, l=l, th=minutes(htf.index))
    if len(_CACHE) > 8: _CACHE.clear()
    _CACHE[key] = A
    return A


def signals(A, p):
    c, angR, emaF, emaS = A['c'], A['angR'], A['emaF'], A['emaS']
    prevc = np.concatenate([[np.nan], c[:-1]])
    prevf = np.concatenate([[np.nan], emaF[:-1]])
    xup = (c > emaF) & (prevc <= prevf)                      # ta.crossover(close, emaF)
    xdn = (c < emaF) & (prevc >= prevf)                      # ta.crossunder(close, emaF)
    angUp = (angR >= p['MINENTRY']) & (True if p['STEEPOK'] else (angR < p['STEEP']))
    angDn = (angR <= -p['MINENTRY']) & (True if p['STEEPOK'] else (angR > -p['STEEP']))
    trendUp = (emaF > emaS) & (c > emaS)
    trendDn = (emaF < emaS) & (c < emaS)
    ok = ~np.isnan(A['atr']) & ~np.isnan(angR) & ~np.isnan(emaS)
    buy = (bool(p['LONG']) & angUp & trendUp & xup & ok).astype(np.int64)
    sell = (bool(p['SHORT']) & angDn & trendDn & xdn & ok).astype(np.int64)
    flat = ((np.abs(angR) < p['MOD']) & ok).astype(np.int64) if p['EXITFLAT'] else np.zeros(len(c), np.int64)
    return buy, sell, flat


def run_asset(name, m1, p, ctrl=False, seed=1, NR=20):
    A = build(name, m1, p)
    buy, sell, flat = signals(A, p)
    t1 = minutes(m1.index).astype(np.int64)
    th = A['th']
    i0 = np.searchsorted(t1, th, 'left').astype(np.int64)
    i1 = np.searchsorted(t1, th + TFS[p['TF']], 'left').astype(np.int64)
    o1, h1, l1, c1 = (m1[k].to_numpy(np.float64) for k in OHLC)
    entatr = np.nan_to_num(A['atr'], nan=0.0)
    tr = engine(i0, i1, buy, sell, flat, entatr, p['SLMULT'], p['RR'],
                t1, o1, h1, l1, c1, p['ORD'], p['PROT'])
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['mins'] = df.texit - df.tent
    df['px'] = df.fill.abs()
    df['riscoRel'] = df.risk / df.px
    df['costR'] = 2 * CUSTO[name] / df.riscoRel
    df['net'] = df.R - df.costR
    df['costR_pine'] = 2 * 5e-4 / df.riscoRel                # os 0,05%/perna que o proprio Pine assume
    df['net_pine'] = df.R - df.costR_pine
    if ctrl:
        rng = np.random.default_rng(seed)
        ok = np.flatnonzero(t1 <= t1[-1] - 60)
        starts = rng.choice(ok, len(df) * NR).astype(np.int64)
        cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                     np.repeat(df.riscoRel.to_numpy(), NR),
                     np.repeat(df.mins.to_numpy(), NR).astype(np.float64),
                     p['RR'], t1, o1, h1, l1, c1, p['ORD'])
        df['ctrlR'] = cr.reshape(-1, NR).mean(1)
    return df


def summ(df, yrs):
    if len(df) == 0: return dict(n=0)
    w = df.net[df.net > 0].sum(); ls = -df.net[df.net < 0].sum()
    return dict(n=len(df), por_ano=len(df) / yrs, acerto=(df.net > 0).mean(), R_bruto=df.R.mean(),
                custo_R=df.costR.mean(), R_liq=df.net.mean(), PF=w / ls if ls > 0 else np.nan,
                R_ano=df.net.sum() / yrs, risco_bp=df.riscoRel.median() * 1e4,
                horas=np.nanmedian(df.mins) / 60, expo=df.mins.sum() / (yrs * 365.25 * 1440))


def main(names):
    lines = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s, flush=True); lines.append(s)
    pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40)
    grid_rows = []
    for name in names:
        _CACHE.clear()
        m1 = load_m1(name)
        t0, tN = m1.index[0], m1.index[-1]
        yrs = (tN - t0).days / 365.25
        bh = (m1.close.iloc[-1] / m1.close.iloc[0]) ** (1 / yrs) - 1
        P(f'\n===== {name}  M1 {t0.date()} -> {tN.date()} ({yrs:.1f} anos, {len(m1)} barras) '
          f'| buy&hold {bh * 100:+.1f}%/ano | custo/perna {CUSTO[name] * 1e4:.2f} bp')
        df = run_asset(name, m1, BASE, ctrl=True)
        df.to_csv(os.path.join(D, 'scripts', f'study_tlangle_{name}_trades.csv'), index=False)
        P('-- defaults do Pine:', {k: v for k, v in BASE.items()})
        A = build(name, m1, BASE)
        ang = A['angR'][~np.isnan(A['angR'])]
        P(f'distribuicao do angulo (|a|): mediana {np.median(np.abs(ang)):.1f} graus, '
          f'p90 {np.percentile(np.abs(ang), 90):.1f}, p99 {np.percentile(np.abs(ang), 99):.1f}, '
          f'max {np.abs(ang).max():.1f}; barras "Flat" (<{BASE["MOD"]}) {np.mean(np.abs(ang) < BASE["MOD"]) * 100:.1f}%, '
          f'"Steep" (>={BASE["STEEP"]}) {np.mean(np.abs(ang) >= BASE["STEEP"]) * 100:.2f}%')
        tab = {}
        tab['todos'] = summ(df, yrs)
        tab['long'] = summ(df[df.side == 1], yrs); tab['short'] = summ(df[df.side == -1], yrs)
        cut = df.tent.quantile(0.7) if len(df) else 0
        tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7); tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
        P(pd.DataFrame(tab).T.round(3).to_string())
        if len(df):
            P(f'retorno em % do capital a 1% de risco/trade: {df.net.sum() / yrs * 1.0:+.1f}%/ano '
              f'(vs buy&hold {bh * 100:+.1f}%/ano), exposicao {tab["todos"]["expo"] * 100:.1f}% do tempo')
            P(f'com os 0,05%/perna que o proprio Pine assume: R_liq {df.net_pine.mean():+.3f} '
              f'({df.net_pine.sum() / yrs:+.1f} R/ano)')
            d = df.R - df.ctrlR
            P(f'controle (entrada aleatoria, mesmo lado/risco/estrutura/duracao): R bruto medio '
              f'{df.ctrlR.mean():+.3f} vs estrategia {df.R.mean():+.3f}; diferenca {d.mean():+.3f} '
              f'(t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
            for lbl, sub in (('long', df[df.side == 1]), ('short', df[df.side == -1])):
                if len(sub) > 2:
                    ds = sub.R - sub.ctrlR
                    P(f'  controle {lbl}: {sub.ctrlR.mean():+.3f} vs {sub.R.mean():+.3f}; '
                      f'dif {ds.mean():+.3f} (t={ds.mean() / ds.std() * np.sqrt(len(sub)):.2f})')
            P('saidas:', df.why.map({0.0: 'stop', 1.0: 'alvo', 2.0: 'angulo flat', 3.0: 'fim',
                                     4.0: 'inversao'}).value_counts().to_dict())
            P(f'duracao mediana {np.median(df.mins) / 60:.1f} h; stop mediano '
              f'{df.riscoRel.median() * 1e4:.0f} bp; custo mediano {df.costR.median():.3f} R')
            sd = df.net.sort_values()
            P(f'pior trade {sd.iloc[0]:+.2f} R; 5 melhores somam {sd.iloc[-5:].sum():+.1f} R de '
              f'{df.net.sum():+.1f} R totais; mediana {df.net.median():+.3f} R')
            yr = pd.to_datetime(df.tent * 60, unit='s', utc=True).dt.year
            P('por ano (n, R liq medio, R liq total):')
            P(df.groupby(yr).net.agg(['count', 'mean', 'sum']).round(3).T.to_string())
        for v in (dict(ORD=1), dict(PROT=1), dict(PROT=1, ORD=1), dict(EXITFLAT=0),
                  dict(STEEPOK=0), dict(SHORT=0), dict(LONG=0)):
            do = run_asset(name, m1, dict(BASE, **v))
            s = summ(do, yrs)
            P(f'-- variante {v}: n={s["n"]} acerto {s.get("acerto", 0):.3f} R_bruto {s.get("R_bruto", 0):+.3f} '
              f'R_liq {s.get("R_liq", 0):+.3f} PF {s.get("PF", 0):.2f} R_ano {s.get("R_ano", 0):+.1f}')
        for TF, ME, SM, RR, EF, PR in itertools.product(['15min', '30min', '1h', '4h'], [10.0, 20.0, 30.0],
                                                        [1.0, 1.5, 2.5], [1.0, 2.0, 3.0], [0, 1], [0, 1]):
            p = dict(BASE, TF=TF, MINENTRY=ME, SLMULT=SM, RR=RR, EXITFLAT=EF, PROT=PR)
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, MINENTRY=ME, SLMULT=SM, RR=RR, EXITFLAT=EF, PROT=PR)
            grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        P('-- grade de robustez (TF x angulo minimo x stop ATR x R:R x saida no flat x protecao):')
        P(g[['TF', 'MINENTRY', 'SLMULT', 'RR', 'EXITFLAT', 'PROT', 'n', 'por_ano', 'acerto', 'risco_bp',
             'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']].round(3).to_string(index=False))
        P(f'combinacoes com R_liq > 0: {(g.R_liq > 0).sum()}/{len(g)}; '
          f'com R_bruto > 0: {(g.R_bruto > 0).sum()}/{len(g)}')
        P('-- media por TF:')
        P(g.groupby('TF')[['n', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']].mean().round(3).to_string())
        P('-- media por angulo minimo:')
        P(g.groupby('MINENTRY')[['n', 'R_bruto', 'R_liq', 'R_ano']].mean().round(3).to_string())
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_tlangle_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['TF', 'MINENTRY', 'SLMULT', 'RR', 'EXITFLAT', 'PROT'],
                             values=['n', 'R_bruto', 'R_liq'],
                             aggfunc={'n': 'min', 'R_bruto': 'mean', 'R_liq': 'mean'})
        P(piv[piv.n >= 20].sort_values('R_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_tlangle.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
