"""MACD Confluence Strategy (Trend + Pullback + Reversal Entries) - "blitz_locked" / TradingView
(PtmuSsWV) - traducao fiel do Pine v6 (fonte aberta baixada do pine-facade,
PUB;1c20606db61c434db6e5c6e8a8a6ae54) e teste em ouro com M1 da Dukascopy.

BUG NO SCRIPT PUBLICADO (linha 159 da fonte):
    rawLA = useTrendX and crossDn and trendOkS and (not crossPullbackOnly or macdL < 0)
    rawSA = useTrendX and crossDn and trendOkS and (not crossPullbackOnly or macdL > 0)
A entrada "T" de COMPRA usa crossDn + trendOkS, isto e, o mesmo gatilho da VENDA: compra no
cruzamento de BAIXA do MACD dentro de uma tendencia de BAIXA confirmada. Pior: como shortA exige
"not longSig", e com o default crossPullbackOnly=false as duas condicoes ficam IDENTICAS, longA
sempre ganha e shortA NUNCA dispara. Ou seja, no estado publicado o bloco de tendencia (o nucleo
da estrategia, "MACD decides WHEN, the channel + HTF decide WHETHER") so produz COMPRAS CONTRA a
tendencia. Testo as duas versoes: FIX=0 (fiel ao publicado) e FIX=1 (crossUp + trendOkL no longo,
que e a intencao obvia do autor).

Regras (defaults do Pine entre parenteses):
  regime  : basis = EMA(close, chLen=200); step = EMA(ATR(21), 12) x chMult (1,5); z = (close-basis)/step.
            trendUp = close > basis e basis > basis[10]; trendDn espelhado. ADX(14,14) >= minAdx (18).
            HTF (240 = 4h) nao repintante: request.security(..., lookahead_off) de nh[1], ou seja o
            histograma MACD da PENULTIMA barra de 4h fechada -> htfOkL exige sinal > 0.
            trendOkL = trendUp e htfOkL e ADX ok e DI+ > DI- e z < maxExt (3); trendOkS espelhado.
  entradas: T  rawLA = crossDn e trendOkS (ver BUG acima); rawSA = crossDn e trendOkS
            P  pullback: trendOk, hist do lado certo, hist acelerando (hist > hist[1] <= hist[2]),
               mergulho minimo depthL = (max(hist,12) - min(hist,4)) / max(hist,12) >= pbDepth (0,25)
               e candle a favor (close > open)
            R  reversao: pavio na banda externa (revLevel=3 bandas) nas ultimas 3 barras, virada do
               histograma e candle a favor (close > open e close > close[1]). SEM filtro de regime/HTF/ADX.
            Prioridade T > P > R, longo antes de curto, cooldown de 5 barras entre entradas.
            Sinal no fechamento, ordem a mercado na ABERTURA da barra seguinte (calc_on_every_tick=false).
            pyramiding=0: sinal contrario com posicao aberta INVERTE.
  saidas  : risco 1R = slMult (2,0) x ATR da BARRA DO SINAL (atr[1] no Pine). Alvo fixo tpR (3,0) R.
            Ao tocar beR (1,0) R de alta maxima, "arma": stop vai para o break-even e, com useTrail
            (true), passa a trilha chandelier max(high,3) - trailMult (2,5) x ATR, atualizada no
            FECHAMENTO de cada barra. momoExit (true): cruzamento contrario do MACD fecha a mercado
            depois de minHold (3) barras. maxBars = 0 (time stop desligado).
            QUIRK FIEL: strategy.exit so e chamado quando position_size != 0, isto e, no fechamento da
            barra JA preenchida -> a barra de entrada fica SEM stop e SEM alvo (PROT=0 reproduz isso;
            PROT=1 protege desde a entrada).
  tamanho : 1% do equity por trade pelo tamanho do stop (teto 2x equity de nocional). Medimos em R
            (1 trade = 1R), custo CUSTO['xau'] = 0,75 bp por perna (spread medido na Lighter). O Pine
            assume 0,05%/perna + 2 ticks de slippage - reporto esse cenario tambem.

Execucao aqui: sinais no TF do grafico (15m/30m/1h/4h) a partir do M1; dentro do trade andamos no M1,
de forma que stop/alvo/gap de fim de semana sao resolvidos minuto a minuto, com os niveis congelados
no fechamento da barra anterior (como as ordens do Pine). A abertura de cada M1 e testada primeiro,
entao um gap que pula o stop sai NA ABERTURA (pior que o stop). Convencao conservadora ORD=0 (stop
antes do alvo no mesmo minuto) e otimista ORD=1 para contraste.
Controle: para cada trade, 20 entradas a mercado em barras sorteadas com o MESMO lado, MESMO risco
relativo, MESMA gestao (break-even + trilha + alvo 3R) e MESMA duracao maxima em barras -> isola o
que o gatilho de entrada acrescenta sobre o acaso, com a gestao neutralizada.

uso: python study_macdconf.py [xau us100 btc ...]
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
BASE = dict(TF='1h', HTFMIN=240, FAST=12, SLOW=26, SIG=9,
            CHLEN=200, CHMULT=1.5, MAXEXT=3.0, MINADX=18.0, USEHTF=1,
            LONG=1, SHORT=1, TRENDX=1, CPO=0, PULLBACK=1, PBDEPTH=0.25, REV=1, REVLEVEL=3, COOLDOWN=5,
            ATRLEN=14, SLMULT=2.0, TPR=3.0, BER=1.0, TRAIL=1, TRAILMULT=2.5,
            MOMOEXIT=1, MINHOLD=3, MAXBARS=0, ORD=0, PROT=0, FIX=0)


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
def ema_nanstart(x, n):
    """ta.ema de uma serie que comeca com NaN (ex.: EMA do ATR): o seed e a SMA das n primeiras
    barras validas, como no Pine (que ignora os na iniciais)."""
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
def rma_nanstart(x, n):
    """ta.rma de uma serie com NaN iniciais (ta.change, DX): o Pine ignora os na do comeco."""
    out = np.full(len(x), np.nan)
    i0 = -1
    for i in range(len(x)):
        if x[i] == x[i]:
            i0 = i; break
    if i0 < 0 or len(x) - i0 < n: return out
    s = 0.0
    for i in range(i0, i0 + n): s += x[i]
    out[i0 + n - 1] = s / n
    a = 1.0 / n
    for i in range(i0 + n, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


@njit(cache=True)
def true_range(h, l, c):
    tr = np.empty(len(c)); tr[0] = h[0] - l[0]
    for i in range(1, len(c)):
        a = h[i] - l[i]; b = abs(h[i] - c[i - 1]); d = abs(l[i] - c[i - 1])
        tr[i] = max(a, max(b, d))
    return tr


@njit(cache=True)
def dmi(h, l, c, n, adxn):
    """ta.dmi(n, adxn) -> DI+, DI-, ADX."""
    m = len(c)
    pdm = np.zeros(m); mdm = np.zeros(m)
    for i in range(1, m):
        up = h[i] - h[i - 1]; dn = l[i - 1] - l[i]
        pdm[i] = up if (up > dn and up > 0) else 0.0
        mdm[i] = dn if (dn > up and dn > 0) else 0.0
    pdm[0] = np.nan; mdm[0] = np.nan
    trur = rma(true_range(h, l, c), n)
    rp = rma_nanstart(pdm, n); rm = rma_nanstart(mdm, n)
    dip = np.full(m, np.nan); dim = np.full(m, np.nan); dx = np.full(m, np.nan)
    for i in range(m):
        if trur[i] == trur[i] and trur[i] > 0 and rp[i] == rp[i]:
            dip[i] = 100.0 * rp[i] / trur[i]; dim[i] = 100.0 * rm[i] / trur[i]
            s = dip[i] + dim[i]
            dx[i] = abs(dip[i] - dim[i]) / (1.0 if s == 0 else s)
    adx = rma_nanstart(dx, adxn) * 100.0
    return dip, dim, adx


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


@njit(cache=True)
def barssince_le(x, maxb):
    """ta.barssince(cond) <= maxb, com cond = x[i] True; nunca verdadeiro -> False (na <= maxb)."""
    out = np.zeros(len(x), np.int64)
    last = -1
    for i in range(len(x)):
        if x[i]: last = i
        if last >= 0 and i - last <= maxb: out[i] = 1
    return out


# ---------------------------------------------------------------- gestao de um trade (comum)
@njit(cache=True)
def manage(j0, side, risk, i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atr, tpr, ber, trail, trailmult,
           prot, ordem, maxb):
    """Entra a mercado na ABERTURA da barra j0 e gere o trade como o Pine (sem saidas por sinal).

    Usado no CONTROLE: mesma gestao (break-even + trilha + alvo) do motor fiel, so sem momoExit nem
    inversao. Niveis congelados no fechamento da barra anterior (ordens ativas a partir de j0+1 se
    prot=0, reproduzindo a barra de entrada desprotegida do Pine).
    Devolve (R, barra_de_saida, minuto_de_saida, motivo, fill);
    motivo: 0 stop/trilha, 1 alvo, 3 duracao maxima, 5 fim dos dados.
    """
    a0 = i0[j0]
    fill = o1[a0]
    sl = fill - side * risk
    tp = fill + side * tpr * risk
    armed = False
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
        # --- fechamento da barra j: arma break-even / trilha
        if not armed:
            if side == 1:
                if roll_hi_bar(h1, i0, i1, j) >= fill + risk * ber:
                    armed = True
                    if sl < fill: sl = fill
            else:
                if roll_lo_bar(l1, i0, i1, j) <= fill - risk * ber:
                    armed = True
                    if sl > fill: sl = fill
        if armed and trail == 1:
            if side == 1:
                t = hh3[j] - trailmult * atr[j]
                if t == t and t > sl: sl = t
            else:
                t = ll3[j] + trailmult * atr[j]
                if t == t and t < sl: sl = t
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


# ---------------------------------------------------------------- motor fiel (com inversao e cooldown)
@njit(cache=True)
def engine(buy, sell, kind, entatr, slmult, tpr, ber, trail, trailmult, prot, ordem, maxb,
           crossUp, crossDn, minhold, momo, cooldown, i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atr):
    """Percorre as barras do TF do grafico aplicando a logica do Pine.

    out: tent texit fill risk side R why kind barras
    why: 0 stop, 1 alvo, 2 cruzamento MACD, 3 time stop, 4 inversao, 5 fim
    """
    n = len(i0)
    out = np.zeros((n + 8, 9))
    q = 0
    pos = 0; pend = 0; pkind = 0.0
    fill = 0.0; risk = 0.0; sl = 0.0; tp = 0.0; sl_act = 0.0; tp_act = 0.0
    tent = 0.0; ebar = -1; armed = False; lastentry = -1000000; tkind = 0.0
    atr_sig = 0.0
    for j in range(n):
        a, b = i0[j], i1[j]
        if b <= a: continue
        # --- abertura da barra j: executa as ordens a mercado decididas no fechamento de j-1
        if pend != 0:
            px = o1[a]
            if pos != 0:
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk
                out[q, 6] = 2.0 if pend == 2 else (3.0 if pend == 3 else 4.0)
                out[q, 7] = tkind; out[q, 8] = j - ebar
                q += 1; pos = 0
            if pend == 1 or pend == -1:
                pos = pend; fill = px; risk = atr_sig * slmult
                sl = fill - pos * risk; tp = fill + pos * tpr * risk
                sl_act = sl; tp_act = tp
                tent = t1[a]; ebar = j; armed = False; tkind = pkind
            pend = 0
        # --- caminhada no M1 dentro da barra j com os niveis congelados (PROT=0: nada na barra de entrada)
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
                    out[q, 7] = tkind; out[q, 8] = j - ebar
                    q += 1; pos = 0
                    break
        # --- fechamento da barra j
        atr_sig = entatr[j]
        cantrade = (lastentry < -999999) or (j - lastentry > cooldown)
        bl = buy[j] == 1 and cantrade
        sh = sell[j] == 1 and cantrade
        if bl and pos <= 0 and atr_sig > 0:
            pend = 1; pkind = kind[j]; lastentry = j
        elif sh and pos >= 0 and atr_sig > 0:
            pend = -1; pkind = kind[j]; lastentry = j
        if pos != 0:
            # arma break-even e trilha com os extremos da barra j (como o Pine, que usa high/low correntes)
            if not armed:
                if pos == 1:
                    if roll_hi_bar(h1, i0, i1, j) >= fill + risk * ber:
                        armed = True
                        if sl < fill: sl = fill
                else:
                    if roll_lo_bar(l1, i0, i1, j) <= fill - risk * ber:
                        armed = True
                        if sl > fill: sl = fill
            if armed and trail == 1:
                if pos == 1:
                    t = hh3[j] - trailmult * atr[j]
                    if t == t and t > sl: sl = t
                else:
                    t = ll3[j] + trailmult * atr[j]
                    if t == t and t < sl: sl = t
            sl_act = sl; tp_act = tp
            if pend == 0 and momo == 1 and (j - ebar) >= minhold:
                if (pos == 1 and crossDn[j] == 1) or (pos == -1 and crossUp[j] == 1):
                    pend = 2
            if pend == 0 and maxb > 0 and (j - ebar) >= maxb:
                pend = 3
    if pos != 0:
        px = c1[len(c1) - 1]
        out[q, 0] = tent; out[q, 1] = t1[len(t1) - 1]; out[q, 2] = fill; out[q, 3] = risk
        out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 5.0
        out[q, 7] = tkind; out[q, 8] = len(i0) - 1 - ebar
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, riscoRel, durbars, i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atr,
            tpr, ber, trail, trailmult, prot, ordem):
    """entrada a mercado na abertura de uma barra sorteada: mesmo lado, mesmo risco relativo,
    MESMA gestao (break-even + trilha + alvo) e mesma duracao maxima em barras."""
    m = len(starts); out = np.zeros(m)
    for z in range(m):
        j0 = starts[z]
        risk = abs(o1[i0[j0]]) * riscoRel[z]
        r, _, _, _, _ = manage(j0, side[z], risk, i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atr,
                               tpr, ber, trail, trailmult, prot, ordem, durbars[z])
        out[z] = r
    return out


# ---------------------------------------------------------------- montagem dos sinais
_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'risk', 'side', 'R', 'why', 'kind', 'barras']
KINDS = {1.0: 'T tendencia', 2.0: 'P pullback', 3.0: 'R reversao'}
WHYS = {0.0: 'stop/trilha', 1.0: 'alvo', 2.0: 'cruz. MACD', 3.0: 'time stop', 4.0: 'inversao', 5.0: 'fim'}


def htf_hist_sign(m1, tf, htfmin, p):
    """htfHist do Pine: request.security(lookahead_off) de nh[1] no TF de htfmin minutos.

    Para a barra do grafico que abre em T, a ultima barra de HTF FECHADA e a que fecha <= T; o
    htfCalc devolve nh[1], logo o valor e o histograma da barra de HTF ANTERIOR a essa. Duplo atraso,
    nao repintante. Se o TF do grafico >= HTF, o Pine usa o proprio TF (htfTf = timeframe.period),
    o que degenera em hist[j-1].
    """
    tfm = TFS[tf]
    if tfm >= htfmin:
        return None  # tratado no chamador: usa hist[j-1] do proprio TF
    rule = f'{htfmin}min'
    hdf = m1.resample(rule, label='left', closed='left').agg(
        {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    hc = hdf.close.to_numpy(np.float64)
    hm = ema(hc, p['FAST']) - ema(hc, p['SLOW'])
    hs = ema_nanstart(hm, p['SIG'])
    hh = hm - hs
    hatr = rma(true_range(hdf.high.to_numpy(np.float64), hdf.low.to_numpy(np.float64), hc), p['ATRLEN'])
    hh = np.where(np.isnan(hatr) | (hatr <= 0), np.nan, hh)
    prev = np.concatenate([[np.nan], hh[:-1]])              # nh[1]
    close_t = minutes(hdf.index) + htfmin                   # minuto de fechamento de cada barra de HTF
    return prev, close_t


def build(name, m1, p):
    key = (name, p['TF'], p['HTFMIN'], p['FAST'], p['SLOW'], p['SIG'], p['CHLEN'], p['CHMULT'],
           p['ATRLEN'], p['REVLEVEL'])
    if key in _CACHE: return _CACHE[key]
    htf = resample(m1, p['TF'])
    o, h, l, c = (htf[k].to_numpy(np.float64) for k in OHLC)
    atr = rma(true_range(h, l, c), p['ATRLEN'])
    macd = ema(c, p['FAST']) - ema(c, p['SLOW'])
    sig = ema_nanstart(macd, p['SIG'])
    hist = macd - sig
    prevm = np.concatenate([[np.nan], macd[:-1]])
    prevs = np.concatenate([[np.nan], sig[:-1]])
    xup = ((macd > sig) & (prevm <= prevs)).astype(np.int64)
    xdn = ((macd < sig) & (prevm >= prevs)).astype(np.int64)
    basis = ema(c, p['CHLEN'])
    step = ema_nanstart(rma(true_range(h, l, c), 21), 12) * p['CHMULT']
    with np.errstate(invalid='ignore', divide='ignore'):
        z = np.where((step > 0) & ~np.isnan(step), (c - basis) / step, 0.0)
    dip, dim, adx = dmi(h, l, c, 14, 14)
    th = minutes(htf.index)
    # HTF MACD
    r = htf_hist_sign(m1, p['TF'], p['HTFMIN'], p)
    if r is None:
        hsig = np.concatenate([[np.nan], hist[:-1]])
    else:
        prev, close_t = r
        k = np.searchsorted(close_t, th, 'right') - 1       # ultima barra de HTF fechada em <= th
        hsig = np.where(k >= 0, prev[np.clip(k, 0, len(prev) - 1)], np.nan)
    A = dict(htf=htf, o=o, h=h, l=l, c=c, th=th, atr=atr, macd=macd, hist=hist, xup=xup, xdn=xdn,
             basis=basis, step=step, z=z, dip=dip, dim=dim, adx=adx, hsig=hsig,
             hh3=roll_max(h, 3), ll3=roll_min(l, 3),
             peakH=roll_max(hist, 12), troughH=roll_min(hist, 12),
             dipLow=roll_min(hist, 4), dipHigh=roll_max(hist, 4))
    if len(_CACHE) > 6: _CACHE.clear()
    _CACHE[key] = A
    return A


def signals(A, p):
    c, o, h, l = A['c'], A['o'], A['h'], A['l']
    hist, basis, step = A['hist'], A['basis'], A['step']
    sh = lambda x, k=1: np.concatenate([np.full(k, np.nan), x[:-k]])
    h1_, h2_ = sh(hist), sh(hist, 2)
    prevc = sh(c)
    ok = ~np.isnan(A['atr']) & ~np.isnan(hist) & ~np.isnan(basis) & ~np.isnan(step) & ~np.isnan(A['adx'])
    htfOkL = np.ones(len(c), bool) if not p['USEHTF'] else (A['hsig'] > 0)
    htfOkS = np.ones(len(c), bool) if not p['USEHTF'] else (A['hsig'] < 0)
    b10 = sh(basis, 10)
    trendUp = (c > basis) & (basis > b10)
    trendDn = (c < basis) & (basis < b10)
    strongOk = A['adx'] >= p['MINADX']
    trendOkL = trendUp & htfOkL & strongOk & (A['dip'] > A['dim']) & (A['z'] < p['MAXEXT'])
    trendOkS = trendDn & htfOkS & strongOk & (A['dim'] > A['dip']) & (A['z'] > -p['MAXEXT'])
    with np.errstate(invalid='ignore', divide='ignore'):
        depthL = np.where(A['peakH'] > 0, (A['peakH'] - A['dipLow']) / A['peakH'], 0.0)
        depthS = np.where(A['troughH'] < 0, (A['dipHigh'] - A['troughH']) / np.abs(A['troughH']), 0.0)
    tagLow = barssince_le(l <= basis - step * p['REVLEVEL'], 3).astype(bool)
    tagHigh = barssince_le(h >= basis + step * p['REVLEVEL'], 3).astype(bool)
    turnUp = (hist > h1_) & (h1_ <= h2_)
    turnDn = (hist < h1_) & (h1_ >= h2_)
    TX, PB, RV = bool(p['TRENDX']), bool(p['PULLBACK']), bool(p['REV'])
    xup, xdn = A['xup'] == 1, A['xdn'] == 1
    if p['FIX']:
        rawLA = TX & xup & trendOkL & (True if not p['CPO'] else (A['macd'] < 0))
    else:                                                   # fiel ao publicado (crossDn + trendOkS)
        rawLA = TX & xdn & trendOkS & (True if not p['CPO'] else (A['macd'] < 0))
    rawLB = PB & trendOkL & (hist > 0) & turnUp & (depthL >= p['PBDEPTH']) & (c > o)
    rawLC = RV & tagLow & turnUp & (c > o) & (c > prevc)
    rawSA = TX & xdn & trendOkS & (True if not p['CPO'] else (A['macd'] > 0))
    rawSB = PB & trendOkS & (hist < 0) & turnDn & (depthS >= p['PBDEPTH']) & (c < o)
    rawSC = RV & tagHigh & turnDn & (c < o) & (c < prevc)
    gL, gS = bool(p['LONG']) & ok, bool(p['SHORT']) & ok
    lA = gL & rawLA; lB = gL & rawLB & ~lA; lC = gL & rawLC & ~lA & ~lB
    longSig = lA | lB | lC
    sA = gS & rawSA & ~longSig
    sB = gS & rawSB & ~longSig & ~sA
    sC = gS & rawSC & ~longSig & ~sA & ~sB
    shortSig = sA | sB | sC
    kind = np.zeros(len(c))
    kind[lC | sC] = 3.0; kind[lB | sB] = 2.0; kind[lA | sA] = 1.0
    return longSig.astype(np.int64), shortSig.astype(np.int64), kind


def run_asset(name, m1, p, ctrl=False, seed=1, NR=20):
    A = build(name, m1, p)
    buy, sell, kind = signals(A, p)
    t1 = minutes(m1.index).astype(np.int64)
    th = A['th']
    i0 = np.searchsorted(t1, th, 'left').astype(np.int64)
    i1 = np.searchsorted(t1, th + TFS[p['TF']], 'left').astype(np.int64)
    o1, h1, l1, c1 = (m1[k].to_numpy(np.float64) for k in OHLC)
    entatr = np.nan_to_num(A['atr'], nan=0.0)
    atrb = np.nan_to_num(A['atr'], nan=0.0)
    hh3 = np.nan_to_num(A['hh3'], nan=-1e300); ll3 = np.nan_to_num(A['ll3'], nan=1e300)
    tr = engine(buy, sell, kind, entatr, p['SLMULT'], p['TPR'], p['BER'], p['TRAIL'], p['TRAILMULT'],
                p['PROT'], p['ORD'], p['MAXBARS'], A['xup'], A['xdn'], p['MINHOLD'], p['MOMOEXIT'],
                p['COOLDOWN'], i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atrb)
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['mins'] = df.texit - df.tent
    df['px'] = df.fill.abs()
    df['riscoRel'] = df.risk / df.px
    df['costR'] = 2 * CUSTO[name] / df.riscoRel
    df['net'] = df.R - df.costR
    df['costR_pine'] = 2 * 5e-4 / df.riscoRel               # os 0,05%/perna que o proprio Pine assume
    df['net_pine'] = df.R - df.costR_pine
    if ctrl:
        rng = np.random.default_rng(seed)
        lo = int(max(p['CHLEN'], 250))
        pool = np.arange(lo, len(i0) - 2)
        pool = pool[i1[pool] > i0[pool]]
        starts = rng.choice(pool, len(df) * NR).astype(np.int64)
        db = np.maximum(df.barras.to_numpy().astype(np.int64), 1)
        cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                     np.repeat(df.riscoRel.to_numpy(), NR),
                     np.repeat(db, NR), i0, i1, o1, h1, l1, c1, t1, hh3, ll3, atrb,
                     p['TPR'], p['BER'], p['TRAIL'], p['TRAILMULT'], p['PROT'], p['ORD'])
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
    pd.set_option('display.width', 280); pd.set_option('display.max_columns', 40)
    grid_rows = []
    for name in names:
        _CACHE.clear()
        m1 = load_m1(name)
        t0, tN = m1.index[0], m1.index[-1]
        yrs = (tN - t0).days / 365.25
        bh = (m1.close.iloc[-1] / m1.close.iloc[0]) ** (1 / yrs) - 1
        P(f'\n===== {name}  M1 {t0.date()} -> {tN.date()} ({yrs:.1f} anos, {len(m1)} barras) '
          f'| buy&hold {bh * 100:+.1f}%/ano | custo/perna {CUSTO[name] * 1e4:.2f} bp')
        for FIX in (0, 1):
            p0 = dict(BASE, FIX=FIX)
            tag = 'FIEL ao publicado (bug do crossDn no longo)' if FIX == 0 else 'CORRIGIDO (crossUp + trendOkL no longo)'
            P(f'\n---------- {tag} ----------')
            df = run_asset(name, m1, p0, ctrl=True)
            df.to_csv(os.path.join(D, 'scripts', f'study_macdconf_{name}_fix{FIX}_trades.csv'), index=False)
            if FIX == 0:
                P('-- defaults do Pine:', {k: v for k, v in p0.items()})
                A = build(name, m1, p0)
                bl, sl_, kd = signals(A, p0)
                P(f'barras do TF {p0["TF"]}: {len(A["c"])}; regime: trendUp+HTF+ADX ok (long) '
                  f'{np.mean(((A["c"] > A["basis"]) & (A["adx"] >= 18)) & (A["hsig"] > 0)) * 100:.1f}% das barras; '
                  f'ADX >= 18 em {np.nanmean(A["adx"] >= 18) * 100:.1f}%; HTF long {np.nanmean(A["hsig"] > 0) * 100:.1f}%')
                P(f'sinais crus antes do cooldown: long {bl.sum()}, short {sl_.sum()} '
                  f'(tipos: {pd.Series(kd[(bl | sl_).astype(bool)]).map(KINDS).value_counts().to_dict()})')
                for FX in (0, 1):
                    bb, ss, kk = signals(A, dict(p0, FIX=FX))
                    P(f'  bloco T (tendencia) com FIX={FX}: long {int(((kk == 1) & bb.astype(bool)).sum())}, '
                      f'short {int(((kk == 1) & ss.astype(bool)).sum())}')
            tab = {'todos': summ(df, yrs), 'long': summ(df[df.side == 1], yrs),
                   'short': summ(df[df.side == -1], yrs)}
            for k, lbl in KINDS.items():
                tab[lbl] = summ(df[df.kind == k], yrs)
            cut = df.tent.quantile(0.7) if len(df) else 0
            tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7)
            tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
            P(pd.DataFrame(tab).T.round(3).to_string())
            if len(df):
                P(f'retorno em % do capital a 1% de risco/trade: {df.net.sum() / yrs:+.1f}%/ano '
                  f'(vs buy&hold {bh * 100:+.1f}%/ano), exposicao {tab["todos"]["expo"] * 100:.1f}% do tempo')
                P(f'com os 0,05%/perna que o proprio Pine assume: R_liq {df.net_pine.mean():+.3f} '
                  f'({df.net_pine.sum() / yrs:+.1f} R/ano)')
                d = df.R - df.ctrlR
                P(f'controle (entrada em barra aleatoria, mesmo lado/risco/gestao/duracao): R bruto medio '
                  f'{df.ctrlR.mean():+.3f} vs estrategia {df.R.mean():+.3f}; diferenca {d.mean():+.3f} '
                  f'(t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
                for lbl, sub in [('long', df[df.side == 1]), ('short', df[df.side == -1])] + \
                                [(KINDS[k], df[df.kind == k]) for k in KINDS]:
                    if len(sub) > 2:
                        ds = sub.R - sub.ctrlR
                        P(f'  controle {lbl:<12}: {sub.ctrlR.mean():+.3f} vs {sub.R.mean():+.3f}; '
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
        P('\n-- variantes (sobre o corrigido, FIX=1):')
        for v in (dict(ORD=1), dict(PROT=1), dict(TRAIL=0), dict(MOMOEXIT=0), dict(USEHTF=0),
                  dict(MINADX=0.0), dict(TRENDX=0), dict(PULLBACK=0), dict(REV=0),
                  dict(SHORT=0), dict(LONG=0), dict(MAXBARS=24)):
            do = run_asset(name, m1, dict(BASE, FIX=1, **v))
            s = summ(do, yrs)
            P(f'   {str(v):<24} n={s["n"]:<5} acerto {s.get("acerto", 0):.3f} R_bruto {s.get("R_bruto", 0):+.3f} '
              f'R_liq {s.get("R_liq", 0):+.3f} PF {s.get("PF", 0):.2f} R_ano {s.get("R_ano", 0):+.1f}')
        for TF, SM, TPR, TRL, MX, AD, FIX in itertools.product(
                ['15min', '30min', '1h', '4h'], [1.0, 2.0, 3.0], [1.5, 3.0, 5.0], [0, 1], [0, 1],
                [0.0, 18.0, 25.0], [0, 1]):
            p = dict(BASE, TF=TF, SLMULT=SM, TPR=TPR, TRAIL=TRL, MOMOEXIT=MX, MINADX=AD, FIX=FIX)
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, SLMULT=SM, TPR=TPR, TRAIL=TRL, MOMOEXIT=MX, MINADX=AD, FIX=FIX)
            grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        P('\n-- grade de robustez (TF x stop ATR x alvo R x trilha x saida no cruzamento x ADX min x bug/corrigido):')
        P(g[['TF', 'SLMULT', 'TPR', 'TRAIL', 'MOMOEXIT', 'MINADX', 'FIX', 'n', 'por_ano', 'acerto',
             'risco_bp', 'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']].round(3).to_string(index=False))
        P(f'combinacoes com R_liq > 0: {(g.R_liq > 0).sum()}/{len(g)}; '
          f'com R_bruto > 0: {(g.R_bruto > 0).sum()}/{len(g)}')
        for col in ('TF', 'SLMULT', 'TPR', 'TRAIL', 'MOMOEXIT', 'MINADX', 'FIX'):
            P(f'-- media por {col}:')
            P(g.groupby(col)[['n', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']].mean().round(3).to_string())
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_macdconf_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['TF', 'SLMULT', 'TPR', 'TRAIL', 'MOMOEXIT', 'MINADX', 'FIX'],
                             values=['n', 'R_bruto', 'R_liq'],
                             aggfunc={'n': 'min', 'R_bruto': 'mean', 'R_liq': 'mean'})
        P(piv[piv.n >= 20].sort_values('R_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_macdconf.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
