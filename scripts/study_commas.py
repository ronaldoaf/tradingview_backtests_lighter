"""3Commas Bot (Bjorgum, TradingView MvlwAzSg) - traducao fiel do Pine (fonte aberta baixada do
pine-facade, PUB;b3d1b9c1f597491390fb5eca58097871) e teste em ouro com M1 da Dukascopy.

ATENCAO - O QUE ESTE SCRIPT E: um TEMPLATE de webhook para bots do 3Commas. O proprio autor marca
no codigo o bloco de entrada com "These conditions are the only thing that you would change to put
in your own criteria". O gatilho que vem de fabrica e um cruzamento de medias simples:
    validLongEntry  = ta.crossover (ma1, ma2) and not na(atr)
    validShortEntry = ta.crossunder(ma1, ma2) and not na(atr)
Ou seja, estamos testando "cruzamento de EMA21/EMA50 com bracket de ATR/pivo e RR 1:1". O valor do
script esta no encanamento de risco (stop no pivo + ATR, alvo por RR, trilha opcional), nao numa
ideia de entrada.

Regras (defaults do Pine entre parenteses):
  MAs     : ma1 = EMA(close, maLength1=21), ma2 = EMA(close, maLength2=50). maType1/maType2 escolhem
            entre EMA/HEMA/SMA/HMA/WMA/DEMA/VWMA/VWAP/T3 (aqui implemento todas menos as de volume).
            HEMA = ta.ema(haOpen, len), com haOpen Heikin-Ashi recursivo.
  entrada : cruzamento (crossover para compra, crossunder para venda) no FECHAMENTO da barra
            (barstate.isconfirmed), ordem a mercado na ABERTURA da barra seguinte.
            FLIP (false) = sinal contrario com posicao aberta e IGNORADO; so entra estando FLAT.
            longTrades/shortTrades (true/true), filtro de sessao (false) e de data (desligados).
  stop    : longStop  = ta.lowest (low,  swinglookback=5) - ATR(atrLen=14) x RiskM (1,0)
            shortStop = ta.highest(high, swinglookback=5) + ATR x RiskM
            (lowest/highest INCLUEM a barra do sinal).
  alvo    : risco_pine = close_do_sinal - longStop; alvo = close_do_sinal + RnR (1,0) x risco_pine.
            useLimit (true); com useLimit=false o unico jeito de sair e a trilha.
  trilha  : trailStop (FALSE por padrao). Quando ligada: trailingStop nasce no stop fixo e, a cada
            FECHAMENTO de barra com lookForExit, vira max(trailingStop, src - ATR x trailStopSize),
            src = lowest(low, 5) por padrao ("High/Low"), ou close[1]/open[1]. rrExit (0,0) = a
            trilha comeca a valer na propria entrada; rrExit > 0 exige tocar essa fracao do alvo.
  QUIRK   : o Pine chama strategy.exit TODA barra (nao so quando ha posicao), logo a ordem bracket
            ja esta no book na barra do fill -> a barra de entrada ESTA protegida (PROT=1 e o
            default aqui; PROT=0 testa o contrario para contraste).
  tamanho : default_qty_type=cash, 10k fixos sobre 10k de capital (1x). Medimos em R (1 trade = 1R
            de risco), com R = |fill - stop| medido no FILL REAL, nao no close do sinal - essa
            diferenca e justamente o que faz o RR efetivo nao ser 1,00.
  custo   : CUSTO[ativo] por perna (spread medido na Lighter; ouro 0,75 bp) + funding FUND[ativo]
            proporcional ao tempo (o long paga, o short recebe). O Pine assume 0,05%/perna +
            1 tick de slippage; reporto esse cenario tambem (net_pine).

Execucao aqui: sinais no TF do grafico (15m/30m/1h/4h) a partir do M1; dentro do trade andamos no
M1, de forma que stop/alvo/gap de fim de semana sao resolvidos minuto a minuto, com os niveis
congelados no fechamento da barra anterior (como as ordens do Pine). A abertura de cada M1 e testada
primeiro, entao um gap que pula o stop sai NA ABERTURA (pior que o stop). Convencao conservadora
ORD=0 (stop antes do alvo no mesmo minuto) e otimista ORD=1 para contraste.
Controle: para cada trade, 20 entradas a mercado em barras sorteadas com o MESMO lado, MESMO risco
relativo, MESMA gestao (alvo/trilha) e MESMA duracao maxima em barras -> isola o que o cruzamento de
medias acrescenta sobre entrar no acaso com o mesmo encanamento de risco.

uso: python study_commas.py [xau us100 btc wti eth ...]
"""
import os, sys, glob, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO, FUND
CUSTO = dict(CUSTO, eth=0.5e-4); FUND = dict(FUND, eth=11.2)  # ETH: spread como BTC, funding medio Lighter 11,2%/ano

OHLC = ['open', 'high', 'low', 'close']
TFS = {'15min': 15, '30min': 30, '1h': 60, '4h': 240}
BASE = dict(TF='1h', MA1='EMA', MA2='EMA', LEN1=21, LEN2=50, ATRLEN=14, RISKM=1.0, SWING=5,
            RNR=1.0, USELIMIT=1, TRAIL=0, TRAILMULT=1.0, TRAILSRC='High/Low', RREXIT=0.0,
            FLIP=0, LONG=1, SHORT=1, PROT=1, ORD=0, MAXBARS=0)


def load_m1(name):
    if name == 'xau':
        x = pd.read_parquet(os.path.join(D, 'data', 'gold', 'xau_1m.parquet'))
    elif name in ('us100', 'us500', 'wti'):
        fs = sorted(glob.glob(os.path.join(D, 'data', f'duka1m_{name}', '*.parquet')))
        x = pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f) > 0])
    else:
        sym = {'btc': 'BTCUSDT', 'eth': 'ETHUSDT'}[name]
        b = pd.read_parquet(os.path.join(D, 'data', 'binance', 'klines_1m', f'{sym}.parquet'))
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
    """ta.ema: seed = SMA das n primeiras barras validas (NaN iniciais ignorados, como no Pine)."""
    out = np.full(len(x), np.nan)
    i0 = -1
    for i in range(len(x)):
        if x[i] == x[i]:
            i0 = i; break
    if i0 < 0 or len(x) - i0 < n: return out
    s = 0.0
    for i in range(i0, i0 + n): s += x[i]
    out[i0 + n - 1] = s / n
    a = 2.0 / (n + 1)
    for i in range(i0 + n, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


@njit(cache=True)
def sma(x, n):
    out = np.full(len(x), np.nan)
    s = 0.0
    for i in range(len(x)):
        s += x[i]
        if i >= n: s -= x[i - n]
        if i >= n - 1: out[i] = s / n
    return out


@njit(cache=True)
def wma(x, n):
    out = np.full(len(x), np.nan)
    dn = n * (n + 1) / 2.0
    for i in range(n - 1, len(x)):
        s = 0.0
        for k in range(n): s += x[i - n + 1 + k] * (k + 1)
        out[i] = s / dn
    return out


@njit(cache=True)
def true_range(h, l, c):
    tr = np.empty(len(c)); tr[0] = h[0] - l[0]
    for i in range(1, len(c)):
        a = h[i] - l[i]; b = abs(h[i] - c[i - 1]); d = abs(l[i] - c[i - 1])
        tr[i] = max(a, max(b, d))
    return tr


@njit(cache=True)
def ha_open(o, h, l, c):
    """_haOpen() do Pine: haOpen = (haOpen[1] + haClose[1]) / 2, semeado com (open+close)/2."""
    n = len(c); out = np.empty(n)
    out[0] = (o[0] + c[0]) / 2.0
    for i in range(1, n):
        hc = (o[i - 1] + h[i - 1] + l[i - 1] + c[i - 1]) / 4.0
        out[i] = (out[i - 1] + hc) / 2.0
    return out


@njit(cache=True)
def roll_max(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        m = -1e300; ok = True
        for k in range(i - n + 1, i + 1):
            if x[k] != x[k]: ok = False; break
            if x[k] > m: m = x[k]
        if ok: out[i] = m
    return out


@njit(cache=True)
def roll_min(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        m = 1e300; ok = True
        for k in range(i - n + 1, i + 1):
            if x[k] != x[k]: ok = False; break
            if x[k] < m: m = x[k]
        if ok: out[i] = m
    return out


def hma(x, n):
    """ta.hma = wma(2*wma(x, n/2) - wma(x, n), sqrt(n)), com as divisoes inteiras do Pine."""
    h = int(n // 2); s = int(np.sqrt(n))
    a = wma(x, max(h, 1)); b = wma(x, n)
    raw = 2 * a - b
    i0 = np.argmax(~np.isnan(raw)) if np.any(~np.isnan(raw)) else len(raw)
    out = np.full(len(x), np.nan)
    if i0 < len(raw):
        out[i0:] = wma(np.ascontiguousarray(raw[i0:]), max(s, 1))
    return out


def get_ma(kind, length, o, h, l, c, hao):
    if kind == 'EMA': return ema(c, length)
    if kind == 'SMA': return sma(c, length)
    if kind == 'WMA': return wma(c, length)
    if kind == 'HMA': return hma(c, length)
    if kind == 'HEMA': return ema(hao, length)
    if kind == 'DEMA':
        e1 = ema(c, length); e2 = _ema_nan(e1, length)
        return 2 * e1 - e2
    if kind == 'T3':
        es = [ema(c, length)]
        for _ in range(5): es.append(_ema_nan(es[-1], length))
        a = 0.7
        c1 = -a ** 3; c2 = 3 * a * a + 3 * a ** 3; c3 = -6 * a * a - 3 * a - 3 * a ** 3
        c4 = 1 + 3 * a + a ** 3 + 3 * a * a
        return c1 * es[5] + c2 * es[4] + c3 * es[3] + c4 * es[2]
    raise ValueError(kind)


def _ema_nan(x, n):
    """ta.ema de uma serie com NaN iniciais (EMA de EMA): o Pine ignora os na do comeco."""
    return ema(np.ascontiguousarray(x.astype(np.float64)), n)


# ---------------------------------------------------------------- gestao de um trade (comum)
@njit(cache=True)
def manage(j0, side, risk, tpdist, i0, i1, o1, h1, l1, c1, t1, trsrc, atr,
           trail, trailmult, uselimit, rrexit, prot, ordem, maxb):
    """Entra a mercado na ABERTURA da barra j0 e gere o bracket do Pine.

    tpdist: distancia ao alvo em preco (ja vem do RnR x risco do close do sinal); <= 0 = sem alvo.
    Devolve (R, barra_de_saida, minuto_de_saida, motivo, fill);
    motivo: 0 stop/trilha, 1 alvo, 3 duracao maxima, 5 fim dos dados.
    """
    a0 = i0[j0]
    fill = o1[a0]
    sl = fill - side * risk
    tp = fill + side * tpdist if uselimit == 1 and tpdist > 0 else side * 1e300
    trig = fill + side * tpdist * rrexit if tpdist > 0 else fill
    looking = (rrexit == 0.0)
    sl_act = sl; tp_act = tp
    live = prot == 1
    n = len(i0)
    for j in range(j0, n):
        a, b = i0[j], i1[j]
        if b > a and live:
            for i in range(a, b):
                s = side
                if (o1[i] - sl_act) * s <= 0:
                    return (o1[i] - fill) * s / risk, j, t1[i], 0.0, fill
                if (o1[i] - tp_act) * s >= 0:
                    return (o1[i] - fill) * s / risk, j, t1[i], 1.0, fill
                hi = h1[i] if s == 1 else -l1[i]
                lo = l1[i] if s == 1 else -h1[i]
                ssl = sl_act if s == 1 else -sl_act
                stp = tp_act if s == 1 else -tp_act
                hitsl = lo <= ssl; hittp = hi >= stp
                if ordem == 0 and hitsl:
                    return (sl_act - fill) * s / risk, j, t1[i], 0.0, fill
                if hittp:
                    return (tp_act - fill) * s / risk, j, t1[i], 1.0, fill
                if ordem == 1 and hitsl:
                    return (sl_act - fill) * s / risk, j, t1[i], 0.0, fill
        live = True
        # --- fechamento da barra j: gatilho da trilha e ratchet (como o Pine, com a barra corrente)
        if trail == 1 and not looking and rrexit != 0.0:
            if side == 1:
                if roll_hi_bar(h1, i0, i1, j) >= trig: looking = True
            else:
                if roll_lo_bar(l1, i0, i1, j) <= trig: looking = True
        if trail == 1 and looking:
            t = trsrc[j] - side * trailmult * atr[j]
            if t == t and (t - sl) * side > 0: sl = t
        sl_act = sl; tp_act = tp
        if maxb > 0 and (j - j0) >= maxb:
            if j + 1 < n:
                return (o1[i0[j + 1]] - fill) * side / risk, j, t1[i0[j + 1]], 3.0, fill
            return (c1[len(c1) - 1] - fill) * side / risk, j, t1[len(t1) - 1], 3.0, fill
    return (c1[len(c1) - 1] - fill) * side / risk, n - 1, t1[len(t1) - 1], 5.0, fill


@njit(cache=True)
def roll_hi_bar(h1, i0, i1, j):
    m = -1e300
    for i in range(i0[j], i1[j]):
        if h1[i] > m: m = h1[i]
    return m


@njit(cache=True)
def roll_lo_bar(l1, i0, i1, j):
    m = 1e300
    for i in range(i0[j], i1[j]):
        if l1[i] < m: m = l1[i]
    return m


# ---------------------------------------------------------------- motor fiel
@njit(cache=True)
def engine(buy, sell, slL, slS, tpdL, tpdS, trsrcL, trsrcS, atr,
           trail, trailmult, uselimit, rrexit, flip, prot, ordem, maxb,
           i0, i1, o1, h1, l1, c1, t1):
    """Percorre as barras do TF do grafico aplicando a logica do Pine.

    out: tent texit fill risk side R why barras tpdist
    why: 0 stop/trilha, 1 alvo, 3 time stop, 4 inversao (FLIP), 5 fim
    """
    n = len(i0)
    out = np.zeros((n + 8, 9))
    q = 0
    pos = 0; pend = 0
    fill = 0.0; risk = 0.0; sl = 0.0; tp = 0.0; sl_act = 0.0; tp_act = 0.0
    trig = 0.0; looking = False; tpd = 0.0
    tent = 0.0; ebar = -1
    pend_sl = 0.0; pend_tpd = 0.0
    for j in range(n):
        a, b = i0[j], i1[j]
        if b <= a: continue
        # --- abertura da barra j: executa a ordem a mercado decidida no fechamento de j-1
        if pend != 0:
            px = o1[a]
            if pos != 0:                                   # inversao (so acontece com FLIP=1)
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 4.0
                out[q, 7] = j - ebar; out[q, 8] = tpd
                q += 1; pos = 0
            pos = pend; fill = px
            risk = abs(fill - pend_sl)                     # R medido no FILL REAL
            sl = pend_sl; tpd = pend_tpd
            tp = fill + pos * tpd if uselimit == 1 and tpd > 0 else pos * 1e300
            trig = fill + pos * tpd * rrexit if tpd > 0 else fill
            looking = (rrexit == 0.0)
            sl_act = sl; tp_act = tp
            tent = t1[a]; ebar = j
            pend = 0
            if risk <= 0:                                  # stop do lado errado do fill (gap) -> sai
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = 1.0
                out[q, 4] = pos; out[q, 5] = 0.0; out[q, 6] = 0.0
                out[q, 7] = 0; out[q, 8] = tpd
                q += 1; pos = 0
        # --- caminhada no M1 dentro da barra j com os niveis congelados
        if pos != 0 and (prot == 1 or j > ebar):
            for i in range(a, b):
                s = pos
                done = 0; rr = 0.0; why = 0.0
                if (o1[i] - sl_act) * s <= 0:
                    rr = (o1[i] - fill) * s / risk; why = 0.0; done = 1
                elif (o1[i] - tp_act) * s >= 0:
                    rr = (o1[i] - fill) * s / risk; why = 1.0; done = 1
                else:
                    hi = h1[i] if s == 1 else -l1[i]
                    lo = l1[i] if s == 1 else -h1[i]
                    ssl = sl_act if s == 1 else -sl_act
                    stp = tp_act if s == 1 else -tp_act
                    hitsl = lo <= ssl; hittp = hi >= stp
                    if ordem == 0 and hitsl:
                        rr = (sl_act - fill) * s / risk; why = 0.0; done = 1
                    elif hittp:
                        rr = (tp_act - fill) * s / risk; why = 1.0; done = 1
                    elif ordem == 1 and hitsl:
                        rr = (sl_act - fill) * s / risk; why = 0.0; done = 1
                if done == 1:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = rr; out[q, 6] = why
                    out[q, 7] = j - ebar; out[q, 8] = tpd
                    q += 1; pos = 0
                    break
        # --- fechamento da barra j
        if pos != 0:
            if trail == 1 and not looking and rrexit != 0.0:
                if pos == 1:
                    if roll_hi_bar(h1, i0, i1, j) >= trig: looking = True
                else:
                    if roll_lo_bar(l1, i0, i1, j) <= trig: looking = True
            if trail == 1 and looking:
                src = trsrcL[j] if pos == 1 else trsrcS[j]
                t = src - pos * trailmult * atr[j]
                if t == t and (t - sl) * pos > 0: sl = t
            sl_act = sl; tp_act = tp
            if maxb > 0 and (j - ebar) >= maxb:
                out[q, 0] = tent; out[q, 1] = t1[b - 1]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = (c1[b - 1] - fill) * pos / risk; out[q, 6] = 3.0
                out[q, 7] = j - ebar; out[q, 8] = tpd
                q += 1; pos = 0
        # sinais: so entra estando FLAT, ou invertendo se FLIP=1
        if buy[j] == 1 and (pos == 0 or (pos == -1 and flip == 1)) and slL[j] == slL[j]:
            if tpdL[j] > 0 or uselimit == 0:
                pend = 1; pend_sl = slL[j]; pend_tpd = tpdL[j]
        elif sell[j] == 1 and (pos == 0 or (pos == 1 and flip == 1)) and slS[j] == slS[j]:
            if tpdS[j] > 0 or uselimit == 0:
                pend = -1; pend_sl = slS[j]; pend_tpd = tpdS[j]
    if pos != 0:
        px = c1[len(c1) - 1]
        out[q, 0] = tent; out[q, 1] = t1[len(t1) - 1]; out[q, 2] = fill; out[q, 3] = risk
        out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 5.0
        out[q, 7] = len(i0) - 1 - ebar; out[q, 8] = tpd
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, riscoRel, rrmult, durbars, i0, i1, o1, h1, l1, c1, t1,
            trsrcL, trsrcS, atr, trail, trailmult, uselimit, rrexit, prot, ordem):
    """entrada a mercado na abertura de uma barra sorteada: mesmo lado, mesmo risco relativo,
    mesmo alvo em R, MESMA gestao e mesma duracao maxima em barras."""
    m = len(starts); out = np.zeros(m)
    for z in range(m):
        j0 = starts[z]
        px = o1[i0[j0]]
        risk = abs(px) * riscoRel[z]
        trsrc = trsrcL if side[z] == 1 else trsrcS
        r, _, _, _, _ = manage(j0, side[z], risk, rrmult[z] * risk, i0, i1, o1, h1, l1, c1, t1,
                               trsrc, atr, trail, trailmult, uselimit, rrexit, prot, ordem,
                               durbars[z])
        out[z] = r
    return out


# ---------------------------------------------------------------- montagem dos sinais
_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'risk', 'side', 'R', 'why', 'barras', 'tpdist']
WHYS = {0.0: 'stop/trilha', 1.0: 'alvo', 3.0: 'time stop', 4.0: 'inversao', 5.0: 'fim'}


def build(name, m1, p):
    key = (name, p['TF'], p['MA1'], p['MA2'], p['LEN1'], p['LEN2'], p['ATRLEN'], p['SWING'],
           p['RISKM'], p['RNR'])
    if key in _CACHE: return _CACHE[key]
    htf = resample(m1, p['TF'])
    o, h, l, c = (np.ascontiguousarray(htf[k].to_numpy(np.float64)) for k in OHLC)
    hao = ha_open(o, h, l, c)
    atr = rma(true_range(h, l, c), p['ATRLEN'])
    ma1 = get_ma(p['MA1'], p['LEN1'], o, h, l, c, hao)
    ma2 = get_ma(p['MA2'], p['LEN2'], o, h, l, c, hao)
    sh = lambda x: np.concatenate([[np.nan], x[:-1]])
    p1, p2 = sh(ma1), sh(ma2)
    xup = ((ma1 > ma2) & (p1 <= p2)).astype(np.int64)
    xdn = ((ma1 < ma2) & (p1 >= p2)).astype(np.int64)
    ll = roll_min(l, p['SWING']); hh = roll_max(h, p['SWING'])
    slL = ll - atr * p['RISKM']
    slS = hh + atr * p['RISKM']
    tpdL = p['RNR'] * (c - slL)                            # distancia do alvo, do CLOSE do sinal
    tpdS = p['RNR'] * (slS - c)
    A = dict(htf=htf, o=o, h=h, l=l, c=c, th=minutes(htf.index), atr=atr, ma1=ma1, ma2=ma2,
             xup=xup, xdn=xdn, ll=ll, hh=hh, slL=slL, slS=slS, tpdL=tpdL, tpdS=tpdS)
    if len(_CACHE) > 8: _CACHE.clear()
    _CACHE[key] = A
    return A


def run_asset(name, m1, p, ctrl=False, seed=1, NR=20):
    A = build(name, m1, p)
    ok = ~np.isnan(A['atr'])
    buy = (A['xup'] == 1) & ok & bool(p['LONG'])
    sell = (A['xdn'] == 1) & ok & bool(p['SHORT'])
    t1 = minutes(m1.index).astype(np.int64)
    th = A['th']
    i0 = np.searchsorted(t1, th, 'left').astype(np.int64)
    i1 = np.searchsorted(t1, th + TFS[p['TF']], 'left').astype(np.int64)
    o1, h1, l1, c1 = (np.ascontiguousarray(m1[k].to_numpy(np.float64)) for k in OHLC)
    atrb = np.nan_to_num(A['atr'], nan=0.0)
    src = p['TRAILSRC']
    if src == 'High/Low':
        trsrcL = np.nan_to_num(A['ll'], nan=-1e300); trsrcS = np.nan_to_num(A['hh'], nan=1e300)
    else:
        base = A['c'] if src == 'Close' else A['o']
        prev = np.concatenate([[np.nan], base[:-1]])
        trsrcL = np.nan_to_num(prev, nan=-1e300); trsrcS = np.nan_to_num(prev, nan=1e300)
    tr = engine(buy.astype(np.int64), sell.astype(np.int64),
                A['slL'], A['slS'], np.nan_to_num(A['tpdL'], nan=-1.0),
                np.nan_to_num(A['tpdS'], nan=-1.0), trsrcL, trsrcS, atrb,
                p['TRAIL'], p['TRAILMULT'], p['USELIMIT'], p['RREXIT'], p['FLIP'],
                p['PROT'], p['ORD'], p['MAXBARS'], i0, i1, o1, h1, l1, c1, t1)
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['mins'] = df.texit - df.tent
    df['px'] = df.fill.abs()
    df['riscoRel'] = df.risk / df.px
    df['rrmult'] = df.tpdist / df.risk                     # RR efetivo (!= RnR por causa do fill)
    yrs_t = df.mins / (365.25 * 1440)
    df['costR'] = (2 * CUSTO[name] + FUND.get(name, 5.0) / 100 * yrs_t * df.side) / df.riscoRel
    df['net'] = df.R - df.costR
    df['costR_pine'] = 2 * 5e-4 / df.riscoRel              # os 0,05%/perna que o proprio Pine assume
    df['net_pine'] = df.R - df.costR_pine
    if ctrl:
        rng = np.random.default_rng(seed)
        lo = int(max(p['LEN2'] * 3, 250))
        pool = np.arange(lo, len(i0) - 2)
        pool = pool[i1[pool] > i0[pool]]
        starts = rng.choice(pool, len(df) * NR).astype(np.int64)
        db = np.maximum(df.barras.to_numpy().astype(np.int64), 1)
        rrm = np.nan_to_num(df.rrmult.to_numpy(), nan=p['RNR'])
        cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                     np.repeat(df.riscoRel.to_numpy(), NR), np.repeat(rrm, NR),
                     np.repeat(db, NR), i0, i1, o1, h1, l1, c1, t1,
                     trsrcL, trsrcS, atrb, p['TRAIL'], p['TRAILMULT'], p['USELIMIT'],
                     p['RREXIT'], p['PROT'], p['ORD'])
        df['ctrlR'] = cr.reshape(-1, NR).mean(1)
    return df


def summ(df, yrs):
    if len(df) == 0: return dict(n=0)
    w = df.net[df.net > 0].sum(); ls = -df.net[df.net < 0].sum()
    return dict(n=len(df), por_ano=len(df) / yrs, acerto=(df.net > 0).mean(), R_bruto=df.R.mean(),
                custo_R=df.costR.mean(), R_liq=df.net.mean(), PF=w / ls if ls > 0 else np.nan,
                R_ano=df.net.sum() / yrs, risco_bp=df.riscoRel.median() * 1e4,
                rr=df.rrmult.median(), horas=np.nanmedian(df.mins) / 60,
                expo=df.mins.sum() / (yrs * 365.25 * 1440))


def main(names):
    lines = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s, flush=True); lines.append(s)
    pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40)
    grid_rows = []
    for name in names:
        _CACHE.clear()
        m1 = load_m1(name)
        t0, tN = m1.index[0], m1.index[-1]
        yrs = (tN - t0).days / 365.25
        bh = (m1.close.iloc[-1] / m1.close.iloc[0]) ** (1 / yrs) - 1
        P(f'\n===== {name}  M1 {t0.date()} -> {tN.date()} ({yrs:.1f} anos, {len(m1)} barras) '
          f'| buy&hold {bh * 100:+.1f}%/ano | custo/perna {CUSTO[name] * 1e4:.2f} bp '
          f'| funding long {FUND.get(name, 5.0):.1f}%/ano')
        P('\n---------- defaults do Pine (EMA21 x EMA50, 1h, stop pivo5 - 1xATR14, RR 1:1, sem trilha) ----------')
        P('-- parametros:', {k: v for k, v in BASE.items()})
        df = run_asset(name, m1, BASE, ctrl=True)
        df.to_csv(os.path.join(D, 'scripts', f'study_commas_{name}_trades.csv'), index=False)
        A = build(name, m1, BASE)
        P(f'barras do TF {BASE["TF"]}: {len(A["c"])}; cruzamentos crus: up {int(A["xup"].sum())}, '
          f'dn {int(A["xdn"].sum())} -> trades efetivos {len(df)} '
          f'(o resto cai porque FLIP=0 ignora o sinal contrario dentro do trade)')
        tab = {'todos': summ(df, yrs), 'long': summ(df[df.side == 1], yrs),
               'short': summ(df[df.side == -1], yrs)}
        cut = df.tent.quantile(0.7) if len(df) else 0
        tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7)
        tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
        P(pd.DataFrame(tab).T.round(3).to_string())
        if len(df):
            P(f'retorno em % do capital a 1% de risco/trade: {df.net.sum() / yrs:+.1f}%/ano '
              f'(vs buy&hold {bh * 100:+.1f}%/ano), exposicao {tab["todos"]["expo"] * 100:.1f}% do tempo')
            P(f'com os 0,05%/perna que o proprio Pine assume: R_liq {df.net_pine.mean():+.3f} '
              f'({df.net_pine.sum() / yrs:+.1f} R/ano)')
            P(f'RR efetivo mediano {df.rrmult.median():.3f} (RnR pedido = {BASE["RNR"]}): o alvo e medido '
              f'do close do sinal e a entrada e no open seguinte')
            d = df.R - df.ctrlR
            P(f'controle (entrada em barra aleatoria, mesmo lado/risco/alvo/gestao/duracao): R bruto medio '
              f'{df.ctrlR.mean():+.3f} vs estrategia {df.R.mean():+.3f}; diferenca {d.mean():+.3f} '
              f'(t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
            for lbl, sub in [('long', df[df.side == 1]), ('short', df[df.side == -1])]:
                if len(sub) > 2:
                    ds = sub.R - sub.ctrlR
                    P(f'  controle {lbl:<6}: {sub.ctrlR.mean():+.3f} vs {sub.R.mean():+.3f}; '
                      f'dif {ds.mean():+.3f} (t={ds.mean() / ds.std() * np.sqrt(len(sub)):.2f})')
            P('saidas:', df.why.map(WHYS).value_counts().to_dict())
            P(f'duracao mediana {np.median(df.mins) / 60:.1f} h ({np.median(df.barras):.0f} barras); '
              f'stop mediano {df.riscoRel.median() * 1e4:.0f} bp; custo mediano {df.costR.median():.3f} R')
            sd = df.net.sort_values()
            P(f'pior trade {sd.iloc[0]:+.2f} R; 5 melhores somam {sd.iloc[-5:].sum():+.1f} R de '
              f'{df.net.sum():+.1f} R totais; mediana {df.net.median():+.3f} R')
            yr = pd.to_datetime(df.tent * 60, unit='s', utc=True).dt.year
            P('por ano (n, R liq medio, R liq total):')
            P(df.groupby(yr).net.agg(['count', 'mean', 'sum']).round(3).T.to_string())
        P('\n-- variantes (uma mudanca por vez sobre os defaults):')
        for v in (dict(ORD=1), dict(PROT=0), dict(FLIP=1), dict(TRAIL=1), dict(TRAIL=1, USELIMIT=0),
                  dict(TRAIL=1, RREXIT=0.6), dict(RNR=2.0), dict(RNR=0.6), dict(RISKM=1.2),
                  dict(SHORT=0), dict(LONG=0), dict(MA1='HEMA', MA2='SMA', LEN1=50, LEN2=100),
                  dict(MAXBARS=24)):
            do = run_asset(name, m1, dict(BASE, **v))
            s = summ(do, yrs)
            P(f'   {str(v):<46} n={s["n"]:<5} acerto {s.get("acerto", 0):.3f} '
              f'R_bruto {s.get("R_bruto", 0):+.3f} R_liq {s.get("R_liq", 0):+.3f} '
              f'PF {s.get("PF", 0):.2f} R_ano {s.get("R_ano", 0):+.1f}')
        # grade de robustez
        for TF, MAS, LENS, RNR, RISKM, TRL in itertools.product(
                ['15min', '30min', '1h', '4h'],
                [('EMA', 'EMA'), ('SMA', 'SMA'), ('HEMA', 'SMA'), ('HMA', 'EMA')],
                [(9, 21), (21, 50), (50, 100)], [0.6, 1.0, 2.0, 3.0], [0.5, 1.0, 2.0], [0, 1]):
            p = dict(BASE, TF=TF, MA1=MAS[0], MA2=MAS[1], LEN1=LENS[0], LEN2=LENS[1],
                     RNR=RNR, RISKM=RISKM, TRAIL=TRL)
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, MAs=f'{MAS[0]}/{MAS[1]}', LENs=f'{LENS[0]}/{LENS[1]}',
                     RNR=RNR, RISKM=RISKM, TRAIL=TRL)
            grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        P('\n-- grade de robustez (TF x tipo de MA x comprimentos x RR x ATR do stop x trilha):')
        P(g[['TF', 'MAs', 'LENs', 'RNR', 'RISKM', 'TRAIL', 'n', 'por_ano', 'acerto', 'risco_bp',
             'rr', 'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']].round(3).to_string(index=False))
        P(f'combinacoes com R_liq > 0: {(g.R_liq > 0).sum()}/{len(g)}; '
          f'com R_bruto > 0: {(g.R_bruto > 0).sum()}/{len(g)}')
        P('-- top 15 por R_ano liquido:')
        P(g.nlargest(15, 'R_ano')[['TF', 'MAs', 'LENs', 'RNR', 'RISKM', 'TRAIL', 'n', 'acerto',
                                   'R_bruto', 'R_liq', 'R_ano', 'PF']].round(3).to_string(index=False))
        for col in ('TF', 'MAs', 'LENs', 'RNR', 'RISKM', 'TRAIL'):
            P(f'-- media por {col}:')
            P(g.groupby(col)[['n', 'acerto', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']].mean().round(3).to_string())
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_commas_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['TF', 'MAs', 'LENs', 'RNR', 'RISKM', 'TRAIL'],
                             values=['n', 'R_bruto', 'R_liq'],
                             aggfunc={'n': 'min', 'R_bruto': 'mean', 'R_liq': 'mean'})
        P(piv[piv.n >= 20].sort_values('R_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_commas.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
