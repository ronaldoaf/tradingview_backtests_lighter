"""Lote 2026-10-21c do TradingView: 5 estrategias, todas SEMPRE-NO-MERCADO (long/short alternados).

  1. Open Close Cross Strategy R5.1 (JustUncleL / JayRogers, vObmEraY, Pine v3)
     SMMA(8) do open e do close, lidos numa resolucao ALTERNATIVA 3x a do grafico via
     security(..., lookahead=barmerge.lookahead_on)  <-- OLHA O FUTURO.
     Teste nas duas versoes: 'peek' (como publicado) e 'hon' (valor do ultimo candle HTF FECHADO).
  2. UT Bot Strategy (VKMgZdYr, Pine v4, creditado a HPotter)
     Trilha de ATR: nLoss = a*ATR(c); flip quando o preco cruza a trilha. a=1, c=10.
  3. Twin Optimized Trend Tracker / TOTT (KivancOzbilgic, eENf7NpJ, Pine v5)
     OTT sobre VAR MA(40) com banda de 1% e gatilho defasado 2 barras (OTTup[2]/OTTdn[2]),
     mais um "twin" de +-0,1% (coeff) que cria zona morta.
  4. ANN Strategy v2 (sirolf2009, oY725jQw, Pine v2)
     MLP 1-5-33-1 com pesos cravados. A entrada e UM escalar (variacao de ohlc4) e todas as
     ativacoes sao monotonas -> a rede inteira colapsa num limiar sobre a variacao do dia.
     O script imprime a prova numerica (monotonicidade + limiar efetivo).
  5. MACD ReLoaded (KivancOzbilgic, VO6DY8s1, Pine v5)
     MACD 12/26/9 com MA selecionavel (default VAR); flip no cruzamento do histograma com zero.

Execucao: sinal no fechamento da barra, ordem na ABERTURA da seguinte (Pine com
calc_on_every_tick=false). Custo CUSTO[ativo] por perna + funding FUND[ativo] pro-rata.
Controle: para cada trade, entradas sorteadas com o MESMO lado e a MESMA duracao.

uso: python study_tvlote3.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

TFS = ['15min', '30min', '1h', '4h', '1D']


# ------------------------------------------------------------------ MAs do Kivanc / JustUncleL
def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()


@njit(cache=True)
def _var(src, length):
    n = len(src); out = np.zeros(n); va = 2.0 / (length + 1)
    ud = np.zeros(n); dd = np.zeros(n)
    for i in range(1, n):
        if src[i] > src[i - 1]: ud[i] = src[i] - src[i - 1]
        elif src[i] < src[i - 1]: dd[i] = src[i - 1] - src[i]
    su = 0.0; sd = 0.0
    for i in range(n):
        su += ud[i]; sd += dd[i]
        if i >= 9: su -= ud[i - 9]; sd -= dd[i - 9]
        cmo = 0.0 if (su + sd) == 0 else (su - sd) / (su + sd)
        k = va * abs(cmo)
        out[i] = k * src[i] + (1 - k) * (out[i - 1] if i else 0.0)
    return out


@njit(cache=True)
def _wwma(src, length):
    n = len(src); out = np.zeros(n); a = 1.0 / length
    for i in range(n):
        out[i] = a * src[i] + (1 - a) * (out[i - 1] if i else 0.0)
    return out


@njit(cache=True)
def _smma(src, length):
    """v7 do OCC: seed = sma(len), depois (prev*(len-1)+src)/len."""
    n = len(src); out = np.full(n, np.nan); s = 0.0
    for i in range(n):
        s += src[i]
        if i >= length: s -= src[i - length]
        if i == length - 1: out[i] = s / length
        elif i >= length: out[i] = (out[i - 1] * (length - 1) + src[i]) / length
    return out


@njit(cache=True)
def _ssma(src, length):
    """SuperSmoother de Ehlers (v12 do OCC)."""
    n = len(src); out = np.zeros(n)
    a1 = np.exp(-1.414 * 3.14159 / length)
    b1 = 2 * a1 * np.cos(1.414 * 3.14159 / length)
    c2 = b1; c3 = -a1 * a1; c1 = 1 - c2 - c3
    for i in range(n):
        p = src[i - 1] if i else 0.0
        out[i] = c1 * (src[i] + p) / 2 + c2 * (out[i - 1] if i else 0.0) + c3 * (out[i - 2] if i > 1 else 0.0)
    return out


def linreg(x, n, off):
    """ta.linreg(src, n, off): valor da reta de minimos quadrados em (n-1-off)."""
    s = pd.Series(x)
    idx = np.arange(n, dtype=float)
    xm = idx.mean(); sxx = ((idx - xm) ** 2).sum()
    ym = s.rolling(n).mean().to_numpy()
    sxy = s.rolling(n).apply(lambda w: ((idx - xm) * (w - w.mean())).sum(), raw=True).to_numpy()
    b = sxy / sxx
    return (ym - b * xm) + b * (n - 1 - off)


def tsf(x, n):
    a = linreg(x, n, 0); return a + (a - linreg(x, n, 1))


def t3(x, n, a=0.7):
    e = x
    es = []
    for _ in range(6):
        e = ema(e, n); es.append(e)
    c1 = -a ** 3; c2 = 3 * a * a + 3 * a ** 3; c3 = -6 * a * a - 3 * a - 3 * a ** 3
    c4 = 1 + 3 * a + a ** 3 + 3 * a * a
    return c1 * es[5] + c2 * es[4] + c3 * es[3] + c4 * es[2]


def zlema(x, n):
    lag = int(n / 2) if (n / 2) == round(n / 2) else int((n - 1) / 2)
    z = np.asarray(x, float).copy()
    z[lag:] = 2 * z[lag:] - np.asarray(x, float)[:-lag] if lag else z
    if lag: z[:lag] = np.nan
    return ema(z, n)


def getma(kind, x, n, vol=None):
    x = np.asarray(x, float)
    if kind == 'SMA': return T.sma(x, n)
    if kind == 'EMA': return ema(x, n)
    if kind == 'WMA': return T.wma(x, n)
    if kind == 'DEMA': return 2 * ema(x, n) - ema(ema(x, n), n)
    if kind == 'TEMA':
        v2 = ema(x, n); return 3 * (v2 - ema(v2, n)) + ema(ema(v2, n), n)
    if kind == 'TMA': return T.sma(T.sma(x, int(np.ceil(n / 2))), int(np.floor(n / 2)) + 1)
    if kind == 'TMA3': return T.sma(T.sma(x, n), n)          # v11 do OCC
    if kind == 'VAR': return _var(x, float(n))
    if kind == 'WWMA': return _wwma(x, float(n))
    if kind == 'ZLEMA': return zlema(x, n)
    if kind == 'TSF': return tsf(x, n)
    if kind == 'HULL': return T.wma(2 * T.wma(x, max(1, int(round(n / 2)))) - T.wma(x, n),
                                    max(1, int(round(np.sqrt(n)))))
    if kind == 'TILL': return t3(x, n)
    if kind == 'SMMA': return _smma(x, n)
    if kind == 'SSMA': return _ssma(x, float(n))
    if kind == 'LSMA': return linreg(x, n, 6)
    if kind == 'VWMA':
        v = np.asarray(vol, float)
        return T.sma(x * v, n) / T.sma(v, n)
    raise ValueError(kind)


# ------------------------------------------------------------------ 1. Open Close Cross R5.1
def occ_signals(df, kind='SMMA', ln=8, mult=3, peek=True, delay=0):
    """closeSeries/openSeries = MA(close/open) na resolucao base; depois security() numa
    resolucao mult x maior. peek=True reproduz lookahead_on (valor FINAL do candle HTF corrente,
    conhecido so no fim dele); peek=False usa o ultimo candle HTF fechado."""
    o = df.open.to_numpy(float); c = df.close.to_numpy(float)
    if delay:
        o = np.concatenate([np.full(delay, np.nan), o[:-delay]])
        c = np.concatenate([np.full(delay, np.nan), c[:-delay]])
    if mult <= 1:
        cs = getma(kind, c, ln, df.volume.to_numpy(float)); os_ = getma(kind, o, ln, df.volume.to_numpy(float))
        return T.xover(cs, os_), T.xunder(cs, os_)
    # bloco HTF: mult barras base agrupadas (como o candle da resolucao alternativa)
    g = np.arange(len(df)) // mult
    hc = pd.Series(c).groupby(g).last().to_numpy()
    ho = pd.Series(o).groupby(g).first().to_numpy()
    hv = pd.Series(df.volume.to_numpy(float)).groupby(g).sum().to_numpy()
    hcs = getma(kind, hc, ln, hv); hos = getma(kind, ho, ln, hv)
    if not peek:                       # so o candle HTF ANTERIOR esta fechado
        hcs = np.concatenate([[np.nan], hcs[:-1]]); hos = np.concatenate([[np.nan], hos[:-1]])
    cs = hcs[g]; os_ = hos[g]
    return T.xover(cs, os_), T.xunder(cs, os_)


# ------------------------------------------------------------------ 2. UT Bot
@njit(cache=True)
def _utbot(src, atr, a):
    n = len(src); ts = np.zeros(n); pos = np.zeros(n)
    for i in range(n):
        nl = a * atr[i]
        p = ts[i - 1] if i else 0.0
        s1 = src[i - 1] if i else 0.0
        if src[i] > p and s1 > p: ts[i] = max(p, src[i] - nl)
        elif src[i] < p and s1 < p: ts[i] = min(p, src[i] + nl)
        elif src[i] > p: ts[i] = src[i] - nl
        else: ts[i] = src[i] + nl
        if i:
            if s1 < p and src[i] > p: pos[i] = 1
            elif s1 > p and src[i] < p: pos[i] = -1
            else: pos[i] = pos[i - 1]
    return ts, pos


def ut_signals(df, a=1.0, c=10):
    src = df.close.to_numpy(float)
    atr = T.atr_rma(df.high.to_numpy(float), df.low.to_numpy(float), src, c)
    atr = np.where(np.isnan(atr), 0.0, atr)
    ts, _ = _utbot(src, atr, a)
    # ema(src,1) == src; above/below = crossover de src com a trilha
    L = T.xover(src, ts) & (src > ts)
    S = T.xover(ts, src) & (src < ts)
    bad = np.arange(len(src)) < c
    L[bad] = False; S[bad] = False
    return L, S


# ------------------------------------------------------------------ 3. TOTT
@njit(cache=True)
def _ott(ma, percent):
    n = len(ma); out = np.zeros(n); d = 1
    ls_p = ma[0] * (1 - percent * 0.01); ss_p = ma[0] * (1 + percent * 0.01)
    for i in range(n):
        fark = ma[i] * percent * 0.01
        ls = ma[i] - fark; ss = ma[i] + fark
        if i:
            ls = max(ls, ls_p) if ma[i] > ls_p else ls
            ss = min(ss, ss_p) if ma[i] < ss_p else ss
            if d == -1 and ma[i] > ss_p: d = 1
            elif d == 1 and ma[i] < ls_p: d = -1
        mt = ls if d == 1 else ss
        out[i] = mt * (200 + percent) / 200 if ma[i] > mt else mt * (200 - percent) / 200
        ls_p = ls; ss_p = ss
    return out


def tott_signals(df, kind='VAR', ln=40, percent=1.0, coeff=0.001):
    src = df.close.to_numpy(float)
    ma = getma(kind, src, ln, df.volume.to_numpy(float))
    ma = np.where(np.isnan(ma), src, ma)
    ott = _ott(ma, percent)
    up = ott * (1 + coeff); dn = ott * (1 - coeff)
    up2 = np.concatenate([[np.nan, np.nan], up[:-2]])
    dn2 = np.concatenate([[np.nan, np.nan], dn[:-2]])
    return T.xover(ma, up2), T.xunder(ma, dn2)


# ------------------------------------------------------------------ 4. ANN v2
W1 = np.array([0.8446488687, -0.5674069006, 0.8676766445, 0.5200611473, -0.2215499554])
W2 = np.array([
    [0.3341657935, -2.0060003664, 0.8606354375, 0.9184846912, -0.8531172267],
    [-0.0394076437, -0.4720374911, 0.2900968524, 1.0653326022, 0.3000188806],
    [-0.559307785, -0.9353655177, 1.2133832962, 0.1952686024, 0.8552068166],
    [-0.4293220754, 0.8484259409, -0.7154087313, 0.1102971055, 0.2279392724],
    [0.9111779155, 0.2801691115, 0.0039982713, -0.5648257117, 0.3281705155],
    [-0.2963954503, 0.4046532178, 0.2460580977, 0.6608675819, -0.8732022547],
    [0.8810811932, 0.6903706878, -0.5953059103, -0.3084040686, -0.4038498853],
    [-0.5687101164, 0.2736758588, -0.2217360382, 0.8742950972, 0.2997583987],
    [0.0708459913, 0.8221730616, -0.7213265567, -0.3810462836, 0.0503867753],
    [0.4880140595, 0.9466627196, 1.0163097961, -0.9500386514, -0.6341709382],
    [1.3402207103, 0.0013395288, 3.4813009133, -0.8636814677, 41.3171047132],
    [1.2388217292, -0.6520886912, 0.3508321737, 0.6640560714, 1.5936220597],
    [-0.1800525171, -0.2620989752, 0.056675277, -0.5045395315, 0.2732553554],
    [-0.7776331454, 0.1895231137, 0.5384918862, 0.093711904, -0.3725627758],
    [-0.3181583022, 0.2467979854, 0.4341718676, -0.7277619935, 0.1799381758],
    [-0.5558227731, 0.3666152536, 0.1538243225, -0.8915928174, -0.7659355684],
    [0.6111516061, -0.5459495224, -0.5724238425, -0.8553500765, -0.8696190472],
    [0.6843667454, 0.408652181, -0.8830470112, -0.8602324935, 0.1135462621],
    [-0.1569048216, -1.4643247888, 0.5557152813, 1.0482791924, 1.4523116833],
    [0.5207514017, -0.2734444192, -0.3328660936, -0.7941515963, -0.3536051491],
    [-0.4097807954, 0.3198619826, 0.461681627, -0.1135575498, 0.7103339851],
    [-0.8725014237, -1.0312091401, 0.2267643037, -0.6814258121, 0.7524828703],
    [-0.3986855003, 0.4962556631, -0.7330224516, 0.7355772164, 0.3180141739],
    [-1.083080442, 1.8752543187, 0.3623326265, -0.348145191, 0.1977935038],
    [-0.0291290625, 0.0612906199, 0.1219696687, -1.0273685429, 0.0872219768],
    [0.931791094, -0.313753684, -0.3028724837, 0.7387076712, 0.3806140391],
    [0.2630619402, -1.9827996702, -0.7741413496, 0.1262957444, 0.2248777886],
    [-0.2666322362, -1.124654664, 0.7288282621, -0.1384289204, 0.2395966188],
    [0.6611845175, 0.0466048937, -0.1980999993, 0.8152350927, 0.0032723211],
    [-0.3150344751, 0.1391754608, 0.5462816249, -0.7952302364, -0.7520712378],
    [-0.0576916066, 0.3678415302, 0.6802537378, 1.1437036331, -0.8637405666],
    [0.7016273068, 0.3978601709, 0.3157049654, -0.2528455662, -0.8614146703],
    [1.1741126834, -1.4046408959, 1.2914477803, 0.9904052964, -0.6980155826]])
W3 = np.array([-0.1366382003, 0.8161960822, -0.9458773183, 0.4692969576, 0.0126710629,
               -0.0403001012, -0.0116244898, -0.4874816289, -0.6392241448, -0.410338398,
               -0.1181027081, 0.1075562037, -0.5948728252, 0.5593677345, -0.3642935247,
               -0.2867603217, 0.142250271, -0.0535698019, -0.034007685, -0.3594532426,
               0.2551095195, 0.4214344983, 0.8941621336, 0.6283377368, -0.7138020667,
               -0.1426738249, 0.172671223, 0.0714824385, -0.3268182144, -0.0078989755,
               -0.2032828145, -0.0260631534, 0.4918037012])


def ann_out(x):
    """Saida da rede para a variacao percentual x (escalar ou vetor)."""
    x = np.atleast_1d(np.asarray(x, float))
    l1 = np.tanh(np.outer(x, W1))
    l2 = np.tanh(l1 @ W2.T)
    return np.tanh(l2 @ W3)


def ann_signals(df, thr_delta=0.0):
    o = df.open.to_numpy(float); h = df.high.to_numpy(float)
    l = df.low.to_numpy(float); c = df.close.to_numpy(float)
    ohlc4 = (o + h + l + c) / 4
    prev = np.concatenate([[np.nan], ohlc4[:-1]])
    pct = ohlc4 / prev - 1
    y = ann_out(np.nan_to_num(pct))
    y[np.isnan(pct)] = np.nan
    buying = np.where(y > thr_delta, 1, np.where(y < -thr_delta, -1, 0))
    # buying[i] = buying[i-1] quando fica na zona morta (aqui so se thr_delta>0)
    s = pd.Series(np.where(buying == 0, np.nan, buying)).ffill().to_numpy()
    s = np.where(np.isnan(pct), np.nan, s)
    L = np.zeros(len(s), bool); S = np.zeros(len(s), bool)
    L[1:] = (s[1:] == 1) & (s[:-1] != 1)
    S[1:] = (s[1:] == -1) & (s[:-1] != -1)
    return L, S


# ------------------------------------------------------------------ 5. MACD ReLoaded
def macdre_signals(df, kind='VAR', n1=12, n2=26, n3=9):
    c = df.close.to_numpy(float); v = df.volume.to_numpy(float)
    m1 = getma(kind, c, n1, v); m2 = getma(kind, c, n2, v)
    macd = m1 - m2
    sig = getma(kind, macd, n3, v)
    hist = macd - sig
    z = np.zeros(len(c))
    return T.xover(hist, z), T.xunder(hist, z)


# ------------------------------------------------------------------ controle vetorizado
def _control_fast(df, trades, name, nsim=20, **kw):
    """Mesmo controle do tvlib (mesmo lado, mesma duracao, entrada sorteada), mas vetorizado:
    estas 5 estrategias nao tem stop/alvo, entao basta o retorno aberto-a-aberto."""
    o = df.open.to_numpy(float)
    secs = (df.index.to_series().diff().dt.total_seconds().median())
    n = len(o)
    durs = np.maximum(1, trades.j.to_numpy(np.int64) - trades.i.to_numpy(np.int64))
    sides = trades.d.to_numpy(float)
    hi = np.maximum(n - durs - 1, 1)
    res = np.zeros(nsim)
    yrs = durs * secs / (365 * 86400)
    for s in range(nsim):
        i = (T.RNG.random(len(durs)) * hi).astype(np.int64)
        r = sides * (o[i + durs] / o[i] - 1) - 2 * T.CUSTO[name] - T.FUND.get(name, 5.0) / 100 * yrs * sides
        res[s] = r.mean()
    return res


T.control_dur = _control_fast


# ------------------------------------------------------------------ runner
def run(name, df, L, S, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    raw = T.engine_bars(df, L, S, long_ok=long_ok, short_ok=short_ok)
    tr = T.book(df, raw, name)
    o = T.summarize(df, tr, name)
    if o:
        if verbose: T.line(tag, o)
        if rows is not None: rows.append(dict(o, tag=tag, **extra))
    return o, tr


def prova_ann():
    print("\n-- ANN v2: a rede 1-5-33-1 e funcao de UMA variavel (a variacao do ohlc4); verificacao")
    for lim in (0.02, 0.05, 0.20, 1.00):
        xs = np.linspace(-lim, lim, 20001); xs = xs[xs != 0]
        ys = ann_out(xs)
        print(f"   |variacao| <= {lim:5.0%}: sinal(rede) == sinal(variacao) em {np.mean(np.sign(ys)==np.sign(xs)):7.2%}"
              f" dos pontos | estritamente crescente: {bool(np.all(np.diff(ys) > 0))}")
    print(f"   rede em -1% / 0 / +1%: {ann_out([-0.01, 0.0, 0.01]).round(6)}  (impar e minuscula)")
    print("   => na faixa util a rede e so o SINAL da variacao: 'comprado se ohlc4 > ohlc4[1]'.")
    print("      Fora de +-20% (nunca num candle diario) ela inverte, por saturacao do peso 41,3.")


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M barras)")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []

        print("\n### 1. Open Close Cross R5.1 (SMMA 8, resolucao alternativa 3x)")
        print("  -- como publicado: lookahead_on (NAO e negociavel, so mostra o tamanho do vies)")
        for tf in TFS:
            run(name, cache[tf], *occ_signals(cache[tf], peek=True), f"{tf} OCC peek(3x)",
                rows, est='occ', TF=tf, cfg='peek')
        print("  -- honesto: mesma regra com o candido HTF ja fechado")
        for tf in TFS:
            run(name, cache[tf], *occ_signals(cache[tf], peek=False), f"{tf} OCC honesto(3x)",
                rows, est='occ', TF=tf, cfg='honesto')
        print("  -- honesto, grade de MA x periodo x multiplicador")
        for tf, k, ln, mu in itertools.product(TFS, ('SMMA', 'DEMA', 'EMA', 'HULL'), (8, 13, 21), (1, 3, 5)):
            run(name, cache[tf], *occ_signals(cache[tf], kind=k, ln=ln, mult=mu, peek=False),
                f"{tf} OCC {k}{ln} x{mu}", rows, verbose=False, est='occ', TF=tf,
                cfg=f'hon {k}{ln} x{mu}')

        print("\n### 2. UT Bot Strategy (a x ATR(c), flip)")
        for tf in TFS:
            run(name, cache[tf], *ut_signals(cache[tf]), f"{tf} UT a=1 ATR10", rows,
                est='ut', TF=tf, cfg='a1 c10')
        print("  -- grade a x c")
        for tf, a, c in itertools.product(TFS, (0.5, 1.0, 2.0, 3.0), (7, 10, 14, 21)):
            run(name, cache[tf], *ut_signals(cache[tf], a, c), f"{tf} UT a={a} c={c}", rows,
                verbose=False, est='ut', TF=tf, cfg=f'a{a} c{c}')

        print("\n### 3. TOTT (VAR MA 40, 1%, twin 0,1%)")
        for tf in TFS:
            run(name, cache[tf], *tott_signals(cache[tf]), f"{tf} TOTT VAR40 1%", rows,
                est='tott', TF=tf, cfg='VAR40 p1 c0.001')
        print("  -- grade periodo x percent x coeff")
        for tf, ln, pc, co in itertools.product(TFS, (20, 40, 80), (0.5, 1.0, 2.0), (0.0, 0.001, 0.005)):
            run(name, cache[tf], *tott_signals(cache[tf], ln=ln, percent=pc, coeff=co), '',
                rows, verbose=False, est='tott', TF=tf, cfg=f'VAR{ln} p{pc} c{co}')

        print("\n### 4. ANN Strategy v2")
        for tf in TFS:
            run(name, cache[tf], *ann_signals(cache[tf]), f"{tf} ANN", rows,
                est='ann', TF=tf, cfg='thr 0')
        print("  -- so long / so short (a rede e um sinal de 1 barra de momento)")
        for tf in TFS:
            run(name, cache[tf], *ann_signals(cache[tf]), f"{tf} ANN so long", rows,
                short_ok=False, est='ann', TF=tf, cfg='so long')
            run(name, cache[tf], *ann_signals(cache[tf]), f"{tf} ANN so short", rows,
                long_ok=False, est='ann', TF=tf, cfg='so short')

        print("\n### 5. MACD ReLoaded (VAR 12/26/9, cruzamento do histograma)")
        for tf in TFS:
            run(name, cache[tf], *macdre_signals(cache[tf]), f"{tf} MACDre VAR", rows,
                est='macdre', TF=tf, cfg='VAR 12/26/9')
        print("  -- grade tipo de MA x comprimentos")
        for tf, k in itertools.product(TFS, ('VAR', 'EMA', 'TILL', 'HULL', 'TSF', 'ZLEMA', 'WWMA')):
            run(name, cache[tf], *macdre_signals(cache[tf], kind=k), '', rows, verbose=False,
                est='macdre', TF=tf, cfg=f'{k} 12/26/9')
        for tf, (a, b, s) in itertools.product(TFS, ((8, 21, 5), (12, 26, 9), (19, 39, 9), (24, 52, 18))):
            run(name, cache[tf], *macdre_signals(cache[tf], 'VAR', a, b, s), '', rows,
                verbose=False, est='macdre', TF=tf, cfg=f'VAR {a}/{b}/{s}')

        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_tvlote3_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        for est, sub in g.groupby('est'):
            h = sub[sub.cfg != 'peek'] if est == 'occ' else sub
            print(f"  {est:7s} {len(h):4d} cel | liq>0 {int((h.bp_liq>0).sum()):4d} | "
                  f"liq>0 e t>2 {int(((h.bp_liq>0)&(h.t>2)).sum()):3d} | "
                  f"CAGR>B&H {int((h.cagr>h.bh).sum()):3d} | melhor liq {h.bp_liq.max():+7.1f}bp")
        cols = ['est', 'TF', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr',
                'bh', 'sharpe', 'expo', 'ctl_bp', 't']
        print("\n  top 15 por retorno liquido/trade (sem a versao peek):")
        print(g[~((g.est == 'occ') & (g.cfg == 'peek'))].sort_values('bp_liq', ascending=False)
              .head(15)[cols].to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    prova_ann()
    main(sys.argv[1:] or ['xau'])
