"""Gold Trend Trail [XAUUSD] (blitz_locked, TradingView) - traducao fiel do Pine v6 (fonte aberta baixada
do pine-facade, PUB;d33eb1136204448983b8f3eb67b28bc6) e teste em ouro com M1 da Dukascopy.

Regras do script (defaults do Pine entre parenteses):
  regime  : ER de Kaufman = |close-close[erLen]| / soma(|close-close[1]|, erLen)  (erLen=20);
            erRank = ta.percentrank(ER, rankLook=200); arma quando erRank >= rankMin (65) em DUAS barras
            seguidas, desarma quando erRank < rankMin - hyst (15); troca so a cada dwell (15) barras.
            Dormente -> trilha destruida (dir=0), sem trades.
  trilha  : mult = baseMlt (2,6) x (1 + (1-ER) x adaptAmt (0,6) + volPr x volAmt (0,5) x 0,5),
            volPr = percentrank(ATR(14), 100)/100; rawUp = hl2 - mult x ATR, rawDn = hl2 + mult x ATR;
            ratchet classico (upB sobe quando close[1] > upB[1], dnB desce quando close[1] < dnB[1]);
            dir vira 1 quando close > dnB[1], -1 quando close < upB[1]. Ao armar, dir = sinal de
            close - close[erLen] e a trilha nasce em rawUp/rawDn.
  entrada : flip da trilha (entryUp/entryDn) + close do lado certo da EMA50 + espaco ate o pivo oposto
            (pivot 5/5, >= roomATR (1,0) x ATR, nivel ja rompido nao bloqueia) + RSI(14) <= 72 (long) /
            >= 28 (short) + barra na sessao 02:00-16:00 NY + stopDist >= minRatr (0,5) x ATR.
            Sinal no fechamento, ordem no ABERTURA da barra seguinte (process_orders_on_close=false).
  saidas  : stop = trilha, com ratchet so a favor (slPx = max(slPx, trail) no long);
            TP1 = close_do_sinal + 1,2 x stopDist fecha tp1Pct (50%); TP2 = +3,0 x stopDist fecha o resto.
            Flip contra a posicao fecha (ou inverte, se os filtros do lado oposto passarem).
            dormExit (false) = nao fecha quando o regime dorme -> stop congela e o trade pode durar semanas.
            QUIRK FIEL: strategy.exit so e chamado no fechamento da barra, logo a barra de entrada fica
            SEM stop e SEM alvo (parametro PROT=0 reproduz isso; PROT=1 protege desde a entrada).
  tamanho : riskPct (1%) do capital / stopDist, limitado por maxLev (10x). Medimos em R, entao o sizing
            so importa pelo teto de alavancagem (anotado abaixo); 1 trade = 1R de risco.

Execucao aqui: sinais no TF alto (15m/30m/1h) a partir do M1; dentro do trade andamos no M1, de forma que
stop/alvo/gap de fim de semana sao resolvidos barra a barra. Convencao conservadora ORD=0 (stop antes do
alvo na mesma barra de 1 minuto) e otimista ORD=1 para contraste. A abertura de cada M1 e testada primeiro,
entao um gap que pula o stop sai NA ABERTURA (pior que o stop), como na vida real.
Custos: CUSTO['xau'] = 0,75 bp por perna (spread medido na Lighter), 2 pernas em R = 2 x custo x preco / risco.
O proprio Pine usa slippage = 20 ticks (US$ 0,20) -> na faixa de 0,5 bp, mesma ordem de grandeza.
Controle: para cada trade, 20 entradas a mercado em minutos sorteados (mesmo lado, mesmo risco relativo,
mesma estrutura 1,2R/3R com parcial, stop fixo, mesma duracao maxima) -> o que o regime+trilha acrescenta.

uso: python study_goldtrail.py [xau us100 btc ...]
"""
import os, sys, glob, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO

OHLC = ['open', 'high', 'low', 'close']
TFS = {'15min': 15, '30min': 30, '1h': 60}
BASE = dict(TF='1h', ATRLEN=14, BASEMLT=2.6, ADAPT=0.6, VOLAMT=0.5, VOLLOOK=100,
            ERLEN=20, RANKLOOK=200, RANKMIN=65, HYST=15, DWELL=15,
            MOM=1, MOMLEN=50, SR=1, PIVLEN=5, ROOMATR=1.0, RSI=1, RSILEN=14, RSIHI=72, RSILO=28,
            TP1R=1.2, TP1PCT=0.5, TP2R=3.0, MINRATR=0.5, DORMEXIT=0, SESS=1, ORD=0, PROT=0)


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
def rsi_pine(c, n):
    up = np.zeros(len(c)); dn = np.zeros(len(c))
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if d > 0: up[i] = d
        else: dn[i] = -d
    u = rma(up[1:], n); v = rma(dn[1:], n)
    out = np.full(len(c), np.nan)
    for i in range(len(u)):
        if u[i] == u[i]:
            out[i + 1] = 100.0 if v[i] == 0 else (0.0 if u[i] == 0 else 100.0 - 100.0 / (1.0 + u[i] / v[i]))
    return out


@njit(cache=True)
def percentrank(x, n):
    """ta.percentrank: % dos n valores anteriores que sao <= o valor atual."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        c = 0
        for k in range(1, n + 1):
            if x[i - k] <= x[i]: c += 1
        out[i] = 100.0 * c / n
    return out


@njit(cache=True)
def last_pivots(h, l, k):
    """lastPH/lastPL como no Pine: so passam a existir k barras DEPOIS da barra do pivo."""
    n = len(h); ph = np.full(n, np.nan); pl = np.full(n, np.nan)
    cph = np.nan; cpl = np.nan
    for i in range(n):
        p = i - k
        if p >= k:
            okh = True; okl = True
            for d in range(1, k + 1):
                if not (h[p] > h[p - d] and h[p] >= h[p + d]): okh = False
                if not (l[p] < l[p - d] and l[p] <= l[p + d]): okl = False
            if okh: cph = h[p]
            if okl: cpl = l[p]
        ph[i] = cph; pl[i] = cpl
    return ph, pl


@njit(cache=True)
def regime_trail(c, hl2, atr, er, erRank, basemlt, adapt, volamt, volpr, rankmin, hyst, dwell, erlen):
    n = len(c)
    armed = np.zeros(n, np.int64); dirv = np.zeros(n, np.int64)
    trail = np.full(n, np.nan); upB = np.full(n, np.nan); dnB = np.full(n, np.nan)
    arm = False; swbar = 0
    for i in range(n):
        if i > 0: arm = armed[i - 1] == 1
        can = i - swbar >= dwell
        if erRank[i] == erRank[i]:
            r1 = erRank[i - 1] if i > 0 and erRank[i - 1] == erRank[i - 1] else 0.0
            if (not arm) and can and erRank[i] >= rankmin and r1 >= rankmin:
                arm = True; swbar = i
            elif arm and can and erRank[i] < rankmin - hyst:
                arm = False; swbar = i
        armed[i] = 1 if arm else 0
        if atr[i] != atr[i]: continue
        mult = basemlt * (1.0 + (1.0 - er[i]) * adapt + volpr[i] * volamt * 0.5)
        ru = hl2[i] - mult * atr[i]; rd = hl2[i] + mult * atr[i]
        if not arm:
            dirv[i] = 0; upB[i] = np.nan; dnB[i] = np.nan
        elif i == 0 or dirv[i - 1] == 0:
            dirv[i] = 1 if (i >= erlen and c[i] >= c[i - erlen]) else (-1 if i >= erlen else 1)
            upB[i] = ru; dnB[i] = rd
        else:
            pu = upB[i - 1] if upB[i - 1] == upB[i - 1] else ru
            pd_ = dnB[i - 1] if dnB[i - 1] == dnB[i - 1] else rd
            upB[i] = max(ru, pu) if c[i - 1] > pu else ru
            dnB[i] = min(rd, pd_) if c[i - 1] < pd_ else rd
            dirv[i] = 1 if c[i] > pd_ else (-1 if c[i] < pu else dirv[i - 1])
        if dirv[i] == 1: trail[i] = upB[i]
        elif dirv[i] == -1: trail[i] = dnB[i]
    return armed, dirv, trail


# ---------------------------------------------------------------- motor de trades
@njit(cache=True)
def engine(i0, i1, hc, trail, dirv, buy, sell, eup, edn, stopd, regclose,
           t1, o1, h1, l1, c1, tp1r, tp1pct, tp2r, dormexit, ordem, prot):
    """maquina de estados sobre as barras do TF alto; stop/alvos resolvidos no M1."""
    n = len(hc); out = np.full((n, 10), np.nan); q = 0
    pos = 0; fill = 0.0; risk = 0.0; sl = 0.0; tp1 = 0.0; tp2 = 0.0
    half = 0; acc = 0.0; tent = 0.0; ebar = -1; pend = 0   # pend: 1 long, -1 short, 2 fechar
    risk_new = 0.0; sl_new = 0.0; tp1_new = 0.0; tp2_new = 0.0
    for j in range(n):
        a, b = i0[j], i1[j]
        if b <= a: continue
        # --- abertura da barra j: executa o que foi decidido no fechamento de j-1
        if pend != 0:
            px = o1[a]
            if pos != 0:
                acc += (px - fill) * (1 - tp1pct * half) * pos / risk
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = acc; out[q, 6] = 2.0 if pend == 2 else 4.0
                out[q, 7] = abs(fill); out[q, 8] = (t1[a] - tent); out[q, 9] = half
                q += 1; pos = 0
            if pend == 1 or pend == -1:
                pos = pend; fill = px; risk = risk_new; sl = sl_new; tp1 = tp1_new; tp2 = tp2_new
                half = 0; acc = 0.0; tent = t1[a]; ebar = j
            pend = 0
        # --- caminhada no M1 dentro da barra j (ordens ativas so a partir da barra seguinte a entrada)
        if pos != 0 and (prot == 1 or j > ebar):
            for i in range(a, b):
                s = pos
                # 1) abertura (gap atravessa o nivel -> sai na abertura)
                if (o1[i] - sl) * s <= 0:
                    acc += (o1[i] - fill) * s * (1 - tp1pct * half) / risk
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = acc; out[q, 6] = 0.0; out[q, 7] = abs(fill)
                    out[q, 8] = t1[i] - tent; out[q, 9] = half
                    q += 1; pos = 0; break
                if half == 0 and (o1[i] - tp1) * s >= 0:
                    acc += (o1[i] - fill) * s * tp1pct / risk; half = 1
                if (o1[i] - tp2) * s >= 0:
                    acc += (o1[i] - fill) * s * (1 - tp1pct * half) / risk
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = acc; out[q, 6] = 1.0; out[q, 7] = abs(fill)
                    out[q, 8] = t1[i] - tent; out[q, 9] = half
                    q += 1; pos = 0; break
                hi = h1[i] if s == 1 else -l1[i]
                lo = l1[i] if s == 1 else -h1[i]
                ssl = sl if s == 1 else -sl
                st1 = tp1 if s == 1 else -tp1
                st2 = tp2 if s == 1 else -tp2
                hitsl = lo <= ssl; hit1 = (half == 0) and hi >= st1; hit2 = hi >= st2
                if ordem == 0 and hitsl:
                    acc += (ssl - (fill if s == 1 else -fill)) * (1 - tp1pct * half) / risk
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = acc; out[q, 6] = 0.0; out[q, 7] = abs(fill)
                    out[q, 8] = t1[i] - tent; out[q, 9] = half
                    q += 1; pos = 0; break
                if hit1:
                    acc += (st1 - (fill if s == 1 else -fill)) * tp1pct / risk; half = 1
                if hit2:
                    acc += (st2 - (fill if s == 1 else -fill)) * (1 - tp1pct * half) / risk
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = acc; out[q, 6] = 1.0; out[q, 7] = abs(fill)
                    out[q, 8] = t1[i] - tent; out[q, 9] = half
                    q += 1; pos = 0; break
                if ordem == 1 and hitsl:
                    acc += (ssl - (fill if s == 1 else -fill)) * (1 - tp1pct * half) / risk
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = acc; out[q, 6] = 0.0; out[q, 7] = abs(fill)
                    out[q, 8] = t1[i] - tent; out[q, 9] = half
                    q += 1; pos = 0; break
        # --- fechamento da barra j: ratchet do stop e decisao da proxima ordem
        if pos > 0 and dirv[j] == 1 and trail[j] == trail[j]:
            if trail[j] > sl: sl = trail[j]
        elif pos < 0 and dirv[j] == -1 and trail[j] == trail[j]:
            if trail[j] < sl: sl = trail[j]
        risk_new = stopd[j]; sl_new = trail[j]
        tp1_new = hc[j] + stopd[j] * tp1r; tp2_new = hc[j] + stopd[j] * tp2r
        if buy[j] == 0:
            tp1_new = hc[j] - stopd[j] * tp1r; tp2_new = hc[j] - stopd[j] * tp2r
        if dormexit == 1 and regclose[j] == 1 and pos != 0:
            pend = 2
        elif pos > 0:
            if sell[j] == 1: pend = -1
            elif edn[j] == 1: pend = 2
            elif buy[j] == 1:                                  # re-sinal sem nova posicao: zera os niveis
                sl = trail[j]; tp1 = hc[j] + stopd[j] * tp1r; tp2 = hc[j] + stopd[j] * tp2r
        elif pos < 0:
            if buy[j] == 1: pend = 1
            elif eup[j] == 1: pend = 2
            elif sell[j] == 1:
                sl = trail[j]; tp1 = hc[j] - stopd[j] * tp1r; tp2 = hc[j] - stopd[j] * tp2r
        else:
            if buy[j] == 1: pend = 1
            elif sell[j] == 1: pend = -1
    if pos != 0:
        px = c1[len(c1) - 1]
        acc += (px - fill) * pos * (1 - tp1pct * half) / risk
        out[q, 0] = tent; out[q, 1] = t1[len(t1) - 1]; out[q, 2] = fill; out[q, 3] = risk
        out[q, 4] = pos; out[q, 5] = acc; out[q, 6] = 3.0; out[q, 7] = abs(fill)
        out[q, 8] = t1[len(t1) - 1] - tent; out[q, 9] = half
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, riscoRel, dur, tp1r, tp1pct, tp2r, t1, o1, h1, l1, c1, ordem):
    """entrada a mercado num minuto sorteado: mesmo lado, mesmo risco relativo, mesma estrutura e duracao."""
    m = len(starts); out = np.zeros(m)
    for z in range(m):
        s0 = starts[z]; sg = side[z]; fill = o1[s0]
        risk = abs(fill) * riscoRel[z]
        sl = fill - sg * risk; tp1 = fill + sg * tp1r * risk; tp2 = fill + sg * tp2r * risk
        half = 0; acc = 0.0; done = 0
        for i in range(s0, len(c1)):
            if t1[i] - t1[s0] > dur[z]:
                acc += (c1[i] - fill) * sg * (1 - tp1pct * half) / risk; done = 1; break
            hi = h1[i] if sg == 1 else -l1[i]
            lo = l1[i] if sg == 1 else -h1[i]
            ssl = sl if sg == 1 else -sl
            st1 = tp1 if sg == 1 else -tp1
            st2 = tp2 if sg == 1 else -tp2
            f = fill if sg == 1 else -fill
            hitsl = lo <= ssl; hit1 = (half == 0) and hi >= st1; hit2 = hi >= st2
            if ordem == 0 and hitsl:
                acc += (ssl - f) * (1 - tp1pct * half) / risk; done = 1; break
            if hit1:
                acc += (st1 - f) * tp1pct / risk; half = 1
            if hit2:
                acc += (st2 - f) * (1 - tp1pct * half) / risk; done = 1; break
            if ordem == 1 and hitsl:
                acc += (ssl - f) * (1 - tp1pct * half) / risk; done = 1; break
        if done == 0:
            acc += (c1[len(c1) - 1] - fill) * sg * (1 - tp1pct * half) / risk
        out[z] = acc
    return out


# ---------------------------------------------------------------- montagem dos sinais
def sess_ok(idx):
    """barra cujo INICIO cai em 02:00-16:00 de Nova York (como time(tf, "0200-1600", NY) do Pine)."""
    et = idx.tz_convert('America/New_York')
    a = et.hour * 60 + et.minute
    return ((a >= 120) & (a < 960)).astype(np.int64)


_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'risk', 'side', 'R', 'why', 'px', 'mins', 'half']


def build(name, m1, p):
    key = (name, p['TF'], p['ATRLEN'], p['BASEMLT'], p['ADAPT'], p['VOLAMT'], p['VOLLOOK'], p['ERLEN'],
           p['RANKLOOK'], p['RANKMIN'], p['HYST'], p['DWELL'], p['MOMLEN'], p['PIVLEN'], p['RSILEN'])
    if key in _CACHE: return _CACHE[key]
    htf = resample(m1, p['TF'])
    o, h, l, c = (htf[k].to_numpy(np.float64) for k in OHLC)
    hl2 = (h + l) / 2
    atr = rma(true_range(h, l, c), p['ATRLEN'])
    volpr = np.nan_to_num(percentrank(atr, p['VOLLOOK']), nan=50.0) / 100.0
    erlen = p['ERLEN']
    net = np.abs(c - np.concatenate([np.full(erlen, np.nan), c[:-erlen]]))
    d1 = np.abs(np.diff(c, prepend=c[0])); d1[0] = np.nan
    path = pd.Series(d1).rolling(erlen).sum().to_numpy()
    er = np.where(path > 0, net / path, 0.0)
    er = np.nan_to_num(er, nan=0.0)
    erRank = percentrank(er, p['RANKLOOK'])
    erRank[:p['RANKLOOK'] + erlen] = np.nan
    armed, dirv, trail = regime_trail(c, hl2, atr, er, erRank, p['BASEMLT'], p['ADAPT'], p['VOLAMT'],
                                      volpr, float(p['RANKMIN']), float(p['HYST']), p['DWELL'], erlen)
    emaM = ema(c, p['MOMLEN']); rsiV = rsi_pine(c, p['RSILEN'])
    lastPH, lastPL = last_pivots(h, l, p['PIVLEN'])
    A = dict(htf=htf, atr=atr, er=er, erRank=erRank, armed=armed, dirv=dirv, trail=trail,
             emaM=emaM, rsiV=rsiV, lastPH=lastPH, lastPL=lastPL, c=c, o=o, h=h, l=l,
             sess=sess_ok(htf.index), th=minutes(htf.index))
    if len(_CACHE) > 8: _CACHE.clear()
    _CACHE[key] = A
    return A


def signals(A, p):
    c, atr, dirv, trail = A['c'], A['atr'], A['dirv'], A['trail']
    eup = (dirv == 1) & (np.concatenate([[0], dirv[:-1]]) != 1)
    edn = (dirv == -1) & (np.concatenate([[0], dirv[:-1]]) != -1)
    momL = True if not p['MOM'] else c >= A['emaM']
    momS = True if not p['MOM'] else c <= A['emaM']
    ph, pl = A['lastPH'], A['lastPL']
    if p['SR']:
        roomL = np.isnan(ph) | (c >= ph) | ((ph - c) >= p['ROOMATR'] * atr)
        roomS = np.isnan(pl) | (c <= pl) | ((c - pl) >= p['ROOMATR'] * atr)
    else:
        roomL = roomS = True
    rsiL = True if not p['RSI'] else A['rsiV'] <= p['RSIHI']
    rsiS = True if not p['RSI'] else A['rsiV'] >= p['RSILO']
    ses = (A['sess'] == 1) if p['SESS'] else True
    stopd = np.abs(c - np.where(np.isnan(trail), c, trail))
    stopOK = (stopd >= p['MINRATR'] * atr) & (stopd > 0)
    ok = ~np.isnan(atr) & ~np.isnan(A['emaM']) & ~np.isnan(A['rsiV'])
    buy = (eup & momL & roomL & rsiL & ses & stopOK & ok).astype(np.int64)
    sell = (edn & momS & roomS & rsiS & ses & stopOK & ok).astype(np.int64)
    was = np.concatenate([[0], A['armed'][:-1]])
    regclose = ((A['armed'] == 0) & (was == 1)).astype(np.int64)
    return buy, sell, eup.astype(np.int64), edn.astype(np.int64), stopd, regclose


def run_asset(name, m1, p, ctrl=False, seed=1):
    A = build(name, m1, p)
    buy, sell, eup, edn, stopd, regclose = signals(A, p)
    t1 = minutes(m1.index).astype(np.int64)
    th = A['th']
    i0 = np.searchsorted(t1, th, 'left').astype(np.int64)
    i1 = np.searchsorted(t1, th + TFS[p['TF']], 'left').astype(np.int64)
    o1, h1, l1, c1 = (m1[k].to_numpy(np.float64) for k in OHLC)
    tr = engine(i0, i1, A['c'], A['trail'], A['dirv'].astype(np.int64), buy, sell, eup, edn, stopd, regclose,
                t1, o1, h1, l1, c1, p['TP1R'], p['TP1PCT'], p['TP2R'], p['DORMEXIT'], p['ORD'], p['PROT'])
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['riscoRel'] = df.risk / df.px
    df['costR'] = 2 * CUSTO[name] / df.riscoRel
    df['net'] = df.R - df.costR
    if ctrl:
        rng = np.random.default_rng(seed)
        NR = 20
        maxd = df.mins.to_numpy()
        ok = np.flatnonzero(t1 <= t1[-1] - 60)
        starts = rng.choice(ok, len(df) * NR).astype(np.int64)
        cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                     np.repeat(df.riscoRel.to_numpy(), NR), np.repeat(maxd, NR).astype(np.float64),
                     p['TP1R'], p['TP1PCT'], p['TP2R'], t1, o1, h1, l1, c1, p['ORD'])
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
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
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
        df.to_csv(os.path.join(D, 'scripts', f'study_goldtrail_{name}_trades.csv'), index=False)
        P('-- defaults do Pine:', {k: v for k, v in BASE.items()})
        tab = {}
        tab['todos'] = summ(df, yrs)
        tab['long'] = summ(df[df.side == 1], yrs); tab['short'] = summ(df[df.side == -1], yrs)
        cut = df.tent.quantile(0.7) if len(df) else 0
        tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7); tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
        P(pd.DataFrame(tab).T.round(3).to_string())
        if len(df):
            P(f'retorno em % do capital a 1% de risco/trade: {df.net.sum() / yrs * 1.0:+.1f}%/ano '
              f'(vs buy&hold {bh * 100:+.1f}%/ano), exposicao {tab["todos"]["expo"] * 100:.1f}% do tempo')
            d = df.R - df.ctrlR
            P(f'controle (entrada aleatoria, mesmo lado/risco/estrutura/duracao): R bruto medio '
              f'{df.ctrlR.mean():+.3f} vs estrategia {df.R.mean():+.3f}; diferenca {d.mean():+.3f} '
              f'(t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
            P('saidas:', df.why.map({0.0: 'stop', 1.0: 'TP2', 2.0: 'flip/dormente', 3.0: 'fim',
                                     4.0: 'inversao'}).value_counts().to_dict())
            P(f'parcial em TP1 tocada em {df.half.mean() * 100:.0f}% dos trades')
            yr = pd.to_datetime(df.tent * 60, unit='s', utc=True).dt.year
            P('por ano (n, R liq medio, R liq total):')
            P(df.groupby(yr).net.agg(['count', 'mean', 'sum']).round(3).T.to_string())
        for v in (dict(ORD=1), dict(PROT=1), dict(PROT=1, ORD=1), dict(DORMEXIT=1), dict(SESS=0)):
            do = run_asset(name, m1, dict(BASE, **v))
            s = summ(do, yrs)
            P(f'-- variante {v}: n={s["n"]} acerto {s.get("acerto", 0):.3f} R_bruto {s.get("R_bruto", 0):+.3f} '
              f'R_liq {s.get("R_liq", 0):+.3f} PF {s.get("PF", 0):.2f} R_ano {s.get("R_ano", 0):+.1f}')
        for TF, RM, BM, MO, SR, PR in itertools.product(['15min', '30min', '1h'], [55, 65, 75],
                                                        [2.0, 2.6, 3.4], [0, 1], [0, 1], [0, 1]):
            p = dict(BASE, TF=TF, RANKMIN=RM, BASEMLT=BM, MOM=MO, SR=SR, PROT=PR)
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, RANKMIN=RM, BASEMLT=BM, MOM=MO, SR=SR, PROT=PR)
            grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        P('-- grade de robustez (TF x percentil de armar x distancia da trilha x EMA x S/R x protecao):')
        P(g[['TF', 'RANKMIN', 'BASEMLT', 'MOM', 'SR', 'PROT', 'n', 'por_ano', 'acerto', 'risco_bp',
             'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']].round(3).to_string(index=False))
        P(f'combinacoes com R_liq > 0: {(g.R_liq > 0).sum()}/{len(g)}; '
          f'com R_bruto > 0: {(g.R_bruto > 0).sum()}/{len(g)}')
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_goldtrail_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['TF', 'RANKMIN', 'BASEMLT', 'MOM', 'SR', 'PROT'],
                             values=['n', 'R_bruto', 'R_liq'],
                             aggfunc={'n': 'min', 'R_bruto': 'mean', 'R_liq': 'mean'})
        P(piv[piv.n >= 20].sort_values('R_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_goldtrail.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
