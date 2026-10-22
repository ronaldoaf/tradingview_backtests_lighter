"""Lote 14 do TradingView (2026-10-22): 5 estrategias nos 5 ativos (ver docs/LOTE14_TV.md).

  1. Crypto Scalper (Divergence Macd Psar Ema 200) (84YDnJ9V, Pine v4)
     Short: PSAR de alta, histograma MACD(12/26/9) > 0 e close < EMA60 armam uma ordem stop no PSAR;
     ela executa quando o PSAR vira para baixo. Long no espelho. TP/SL: long 24,5%/100%, short 5,5%/3%.
     Aqui: sinal = condicao na barra anterior + virada do PSAR na barra atual; ordem na abertura seguinte.
  2. QuantNomad Heikin-Ashi PSAR (0iKy7lyG, Pine v4)
     PSAR calculado sobre as velas Heikin-Ashi; a virada do PSAR inverte a posicao. Sempre no mercado.
  3. (V Bottom/V Top Pattern [Misu], 6qmzhNzi: ignorado; as ordens da estrategia estao comentadas no
     codigo publicado, entao o script nao opera. Substituto: HullMA Strategy, item 6.)
  4. Forex Master v4.0 (AIZqyS45, Pine v2)
     Long: close cruza a BB(20, 1,5) de baixo para cima com EMA6(DX50) < EMA12(DX50) (tendencia
     perdendo forca). Short no espelho. TP/SL de 500 ticks virou percentual (grade).
  5. Delta-RSI with filters (0OdCms2T, Pine v4)
     Derivada, no ultimo ponto, do polinomio de grau 3 ajustado as 50 ultimas barras do RSI(21);
     compra quando cruza acima da EMA9 dela, vende quando cruza abaixo. Filtros desligados por padrao.
     O script fecha o short com a condicao do long (bug), entao na pratica o sinal contrario inverte.
  6. HullMA Strategy (qQ0MJCVL, Pine v2)
     HMA(16) subindo (vs a HMA da barra anterior) = comprado, senao vendido. Sempre no mercado.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos no M1 (stop antes do alvo).
uso: python study_tvlote14.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema
from study_tvlote9 import summary
from study_tvlote10 import shift, psar_up

NAN = np.nan


# ------------------------------------------------------------------ 1. Crypto Scalper
def run_cs(name, df, mm, tag, rows=None, verbose=True, ema_len=60, tpl=0.245, sll=1.0, tps=0.055, sls=0.03,
           long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    up = psar_up(h, l, c, 0.02, 0.02, 0.2)
    hist = (lambda m: m - ema(m, 9))(ema(c, 12) - ema(c, 26))
    out = ema(c, ema_len)
    upp = np.concatenate([[False], up[:-1]])
    condS = shift((up & (hist > 0) & (c < out)).astype(float), 1) == 1
    condL = shift((~up & (hist < 0) & (c > out)).astype(float), 1) == 1
    S = condS & upp & ~up; L = condL & ~upp & up
    na = np.full(len(c), NAN)
    r = gsim(df, mm, L, S, SLL=c * (1 - sll) if sll < 1 else na, TPL=c * (1 + tpl) if tpl else na,
             SLS=c * (1 + sls) if sls else na, TPS=c * (1 - tps) if tps else na, rev=True,
             long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Heikin-Ashi PSAR
def ha_psar_dir(o, h, l, c, start=0.02, inc=0.02, mx=0.2):
    n = len(c)
    hc = (o + h + l + c) / 4; ho = np.empty(n); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, n):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    hh = np.maximum(h, np.maximum(ho, hc)); hl = np.minimum(l, np.minimum(ho, hc))
    ps = np.full(n, NAN); af = np.zeros(n); td = np.zeros(n, int); ep = np.zeros(n)
    for i in range(1, n):
        init = i < 2 or ps[i - 2] != ps[i - 2]
        l2s = td[i - 1] == 1 and hc[i] <= ps[i - 1]
        s2l = td[i - 1] == -1 and hc[i] >= ps[i - 1]
        chg = init or l2s or s2l
        if init:
            td[i] = 1 if hc[i - 1] > ho[i - 1] else -1
        else:
            td[i] = -1 if l2s else (1 if s2l else td[i - 1])
        if chg:
            af[i] = start
        elif (td[i] == 1 and hh[i] > ep[i - 1]) or (td[i] == -1 and l[i] < ep[i - 1]):
            af[i] = min(mx, af[i - 1] + inc)
        else:
            af[i] = af[i - 1]
        if chg and td[i] == 1:
            ep[i] = hh[i]
        elif chg and td[i] == -1:
            ep[i] = hl[i]
        else:
            ep[i] = max(ep[i - 1], hh[i]) if td[i] == 1 else min(ep[i - 1], hl[i])
        if init:
            ps[i] = hl[i - 1] if hc[i - 1] > ho[i - 1] else hh[i - 1]
        elif chg:
            ps[i] = ep[i - 1]
        else:
            ps[i] = ps[i - 1] + af[i] * (ep[i] - ps[i - 1]) if td[i] == 1 else ps[i - 1] - af[i] * (ps[i - 1] - ep[i])
    return td


def run_hap(name, df, mm, tag, rows=None, verbose=True, start=0.02, inc=0.02, mx=0.2, long_ok=True, short_ok=True,
            **extra):
    o, h, l, c = ohlc(df)
    td = ha_psar_dir(o, h, l, c, start, inc, mx)
    tp = np.concatenate([[0], td[:-1]])
    L = (td == 1) & (tp == -1); S = (td == -1) & (tp == 1)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. Forex Master
def run_fm(name, df, mm, tag, rows=None, verbose=True, bl=20, bm=1.5, adx_n=50, sl=0.01, tp=0.01, long_ok=True,
           short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    basis = T.sma(c, bl); dev = bm * pd.Series(c).rolling(bl).std(ddof=0).to_numpy()
    up, lo = basis + dev, basis - dev
    ph, pl, pc = shift(h, 1), shift(l, 1), shift(c, 1)
    tr = np.nan_to_num(np.maximum(np.maximum(h - l, np.abs(h - pc)), np.abs(l - pc)), nan=0)
    dmp = np.where((h - ph) > (pl - l), np.maximum(h - ph, 0), 0); dmp = np.nan_to_num(dmp)
    dmm = np.where((pl - l) > (h - ph), np.maximum(pl - l, 0), 0); dmm = np.nan_to_num(dmm)
    a = 1 - 1 / adx_n
    s = lambda x: pd.Series(x).ewm(alpha=1 / adx_n, adjust=False).mean().to_numpy() * adx_n  # Wilder com soma
    st, sp, sm = s(tr), s(dmp), s(dmm)
    with np.errstate(divide='ignore', invalid='ignore'):
        dp, dm = sp / st * 100, sm / st * 100
        dx = np.nan_to_num(np.abs(dp - dm) / (dp + dm) * 100)
    weak = ema(dx, 6) < ema(dx, 12)
    L = T.xover(c, lo) & weak; S = T.xunder(c, up) & weak
    r = gsim(df, mm, L, S, slp=sl, tpp=tp, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. Delta-RSI
def poly_deriv_weights(window, degree):
    """Pesos w tais que w . y (y do mais antigo ao mais recente) = derivada no ultimo ponto do polinomio
    de minimos quadrados de grau `degree` (o diff() do script: pinv via QR, igual ao lstsq)."""
    x = np.arange(window, dtype=float)
    J = np.vander(x, degree + 1, increasing=True)
    C = np.linalg.pinv(J)
    d = np.array([i * (window - 1) ** (i - 1) if i else 0.0 for i in range(degree + 1)])
    return d @ C


def run_drsi(name, df, mm, tag, rows=None, verbose=True, rl=21, window=50, degree=3, sig=9, mode='signal',
             long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    src = T.rsi_wilder(c, rl)
    w = poly_deriv_weights(window, degree)
    d = np.convolve(np.nan_to_num(src), w[::-1], mode='full')[:len(c)]
    d[:window + rl] = NAN
    if mode == 'zero':
        z = np.zeros_like(d); L, S = T.xover(d, z), T.xunder(d, z)
    else:
        sl_ = np.array(ema(np.nan_to_num(d), sig)); sl_[np.isnan(d)] = NAN
        L, S = T.xover(d, sl_), T.xunder(d, sl_)
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 6. HullMA
def run_hull(name, df, mm, tag, rows=None, verbose=True, n=16, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    hn = int(round(n / 2)); sq = int(round(np.sqrt(n)))
    n1 = T.wma(2 * T.wma(c, hn) - T.wma(c, n), sq)
    n2 = T.wma(2 * T.wma(shift(c, 1), hn) - T.wma(shift(c, 1), n), sq)
    st = n1 > n2
    prev = np.concatenate([[False], st[:-1]])
    ok = ~np.isnan(n2)
    L = st & ~prev & ok; S = ~st & prev & ok
    r = gsim(df, mm, L, S, S if not short_ok else None, None, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. Crypto Scalper (PSAR + MACD + EMA60)")
        for tf in TFS:
            df = cache[tf]
            run_cs(name, df, mm, f"{tf} CS default", rows, est='cs', TF=tf, cfg='e60 tp/sl default')
            for el, ex, side in itertools.product((60, 200), ('default', 'sem', 'sim2'), side2):
                kw = dict(default={}, sem=dict(tpl=0, sll=1.0, tps=0, sls=0),
                          sim2=dict(tpl=0.04, sll=0.02, tps=0.04, sls=0.02))[ex]
                run_cs(name, df, mm, '', rows, False, ema_len=el, short_ok=side == 'ambos', est='cs', TF=tf,
                       cfg=f'e{el} tp/sl {ex} {side}', **kw)

        print("\n### 2. Heikin-Ashi PSAR [QuantNomad]")
        for tf in TFS:
            df = cache[tf]
            run_hap(name, df, mm, f"{tf} HAP default", rows, est='hap', TF=tf, cfg='0.02/0.02/0.2 ambos')
            for (s0, mx), side in itertools.product(((0.02, 0.2), (0.01, 0.1), (0.005, 0.05)), side2):
                run_hap(name, df, mm, '', rows, False, start=s0, inc=s0, mx=mx, short_ok=side == 'ambos', est='hap',
                        TF=tf, cfg=f'{s0}/{s0}/{mx} {side}')

        print("\n### 4. Forex Master v4.0 (BB20x1,5 + ADX fraco)")
        for tf in TFS:
            df = cache[tf]
            run_fm(name, df, mm, f"{tf} FM default", rows, est='fm', TF=tf, cfg='bb20 1.5 sl1% tp1% ambos')
            for bm, sl, side in itertools.product((1.5, 2.0), (0.005, 0.01, 0.02), side2):
                run_fm(name, df, mm, '', rows, False, bm=bm, sl=sl, tp=sl, short_ok=side == 'ambos', est='fm', TF=tf,
                       cfg=f'bb20 {bm} sl{sl:.1%} tp{sl:.1%} {side}')

        print("\n### 5. Delta-RSI (grau 3, janela 50, RSI21, sinal EMA9)")
        for tf in TFS:
            df = cache[tf]
            run_drsi(name, df, mm, f"{tf} DRSI default", rows, est='drsi', TF=tf, cfg='r21 w50 d3 signal ambos')
            for (rl, wn), md, side in itertools.product(((21, 50), (14, 30), (21, 100)), ('signal', 'zero'), side2):
                run_drsi(name, df, mm, '', rows, False, rl=rl, window=wn, mode=md, short_ok=side == 'ambos',
                         est='drsi', TF=tf, cfg=f'r{rl} w{wn} d3 {md} {side}')

        print("\n### 6. HullMA Strategy (HMA16 subindo/descendo)")
        for tf in TFS:
            df = cache[tf]
            run_hull(name, df, mm, f"{tf} HULL default", rows, est='hull', TF=tf, cfg='n16 ambos')
            for n, side in itertools.product((9, 16, 30, 55, 100), side2):
                run_hull(name, df, mm, '', rows, False, n=n, short_ok=side == 'ambos', est='hull', TF=tf,
                         cfg=f'n{n} {side}')

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote14')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
