"""Lote 15 do TradingView (2026-10-22): 5 estrategias nos 5 ativos (ver docs/LOTE15_TV.md).

Ignorados (regra: templates/utilitarios nao sao testados):
  - Fixed Percent Stop Loss & Take Profit % (00WHGEoc): exemplo de como pôr SL/TP percentual.
  - Autoview Build-a-bot (iVHq4EFG): modelo de automacao com alertas para extensao do Chrome.
  - AUTOMATIC GRID BOT (6qZpzElZ): robo de grade que exige faixa de preco manual; nao e sinal.

  1. [RS] Spot/Binary Scalper V0 (PMqutqKQ, Pine v2)
     Compra quando a vela atravessa a Tenkan(7) de baixo para cima (open < tenkan < close) com DI+ > 20;
     venda no espelho com DI- > 20. Sessao 04:00-15:00 (horario da bolsa; aqui UTC, variante sem
     sessao). TP/SL de 200/150 ticks virou percentual (grade, mesma proporcao 4:3).
  2. Simple profitable trading strategy / Combined Strategy (QoNKoXwW, Pine v3)
     Long com EMAs 8>13>21>34>55, 40 < RSI14 < 70 e Stoch14 < 80; sai com EMA13 < EMA55, RSI > 70 ou
     Stoch > 95. Short no espelho (EMAs invertidas, 30 < RSI < 60, Stoch > 20; sai com EMA13 > EMA55,
     RSI < 30 ou Stoch < 5).
  3. Trendline Breaks with Multi Fibonacci Supertrend (aVzNdTMg, Pine v6)
     Linhas de tendencia que partem de cada pivo (8/8) com inclinacao ATR/8; long quando o close
     rompe a linha de cima, DI+ > DI- (13) e close > EMA21 da media de 3 SuperTrends (0,618/1,618/
     2,618 x ATR13). Sai quando close[1] cruza a EMA de volta, no stop de 8 x ATR13 ou no alvo de 1%
     (o trailing de 0,01% depois do alvo foi tratado como saida no alvo). Short no espelho.
  4. Crypto BOT lower timeframes / "Price EMA with stock" (IS7yz9s4, Pine v4)
     Long: preco cruzou/tocou a EMA50 nas ultimas 5 barras, close > EMA50 > EMA100, Stoch(5,3) cruza
     20 para cima e histograma MACD >= 0. Short no espelho. TP/SL de 10% (o exit so e armado em
     barras de "toque"; aqui fica sempre armado).
  5. BTC bot (DPBeZbMP, Pine v4)
     Long quando cc = 3*RSI21 - 2*EMA21(RSI21) cruza 0 para cima; sai (o "sell" fecha o long, padrao
     long-only) quando close[1] cruza acima do R3 do pivo semanal anterior. Stop 15%, alvos 3/5/7/10%
     de 25% cada (aqui: um alvo unico, grade 3/5/10%).

uso: python study_tvlote15.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote8 import ema, dmi
from study_tvlote9 import summary
from study_tvlote10 import shift

NAN = np.nan
roll = lambda x, n: pd.Series(x).rolling(n)


def donch(h, l, n):
    return (roll(h, n).max() + roll(l, n).min()).to_numpy() / 2


def stoch(c, h, l, n):
    lo = roll(l, n).min().to_numpy(); hi = roll(h, n).max().to_numpy()
    with np.errstate(divide='ignore', invalid='ignore'):
        return 100 * (c - lo) / (hi - lo)


# ------------------------------------------------------------------ 1. Spot/Binary Scalper
def run_sbs(name, df, mm, tag, rows=None, verbose=True, conv=7, th=20, sl=0.005, session=True, long_ok=True,
            short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    tk = donch(h, l, conv)
    p, m, _ = dmi(h, l, c, 14)
    L = (o < tk) & (c > tk) & (p > th); S = (o > tk) & (c < tk) & (m > th)
    if session:
        hr = df.index.hour + df.index.minute / 60
        ok = np.asarray((hr >= 4) & (hr < 15)); L &= ok; S &= ok
    r = gsim(df, mm, L, S, slp=sl, tpp=sl * 4 / 3, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Combined Strategy
def run_comb(name, df, mm, tag, rows=None, verbose=True, long_ok=True, short_ok=True, use_osc=True, **extra):
    o, h, l, c = ohlc(df)
    e = {n: ema(c, n) for n in (8, 13, 21, 34, 55)}
    rsi = T.rsi_wilder(c, 14); k = stoch(c, h, l, 14)
    upE = (e[8] > e[13]) & (e[13] > e[21]) & (e[21] > e[34]) & (e[34] > e[55])
    dnE = (e[8] < e[13]) & (e[13] < e[21]) & (e[21] < e[34]) & (e[34] < e[55])
    if use_osc:
        L = upE & (rsi < 70) & (rsi > 40) & (k < 80); S = dnE & (rsi > 30) & (rsi < 60) & (k > 20)
        XL = (e[13] < e[55]) | (rsi > 70) | (k > 95); XS = (e[13] > e[55]) | (rsi < 30) | (k < 5)
    else:
        L, S, XL, XS = upE, dnE, e[13] < e[55], e[13] > e[55]
    r = gsim(df, mm, L, S, XL, XS, rev=False, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. TMFS
def st_line(h, l, c, f, n):
    atr = np.nan_to_num(T.atr_rma(h, l, c, n)); hl2 = (h + l) / 2
    N = len(c); up = hl2 - f * atr; dn = hl2 + f * atr; d = np.ones(N); out = np.empty(N)
    for i in range(N):
        if i:
            if c[i - 1] > up[i - 1]: up[i] = max(up[i], up[i - 1])
            if c[i - 1] < dn[i - 1]: dn[i] = min(dn[i], dn[i - 1])
            d[i] = d[i - 1]
            if d[i - 1] == -1 and c[i] > dn[i - 1]: d[i] = 1
            elif d[i - 1] == 1 and c[i] < up[i - 1]: d[i] = -1
        out[i] = up[i] if d[i] == 1 else dn[i]
    out[0] = NAN
    return out


def run_tmfs(name, df, mm, tag, rows=None, verbose=True, swing=8, sl_atr=8.0, tp=0.01, dmi_n=13, long_ok=True,
             short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    avg = sum(st_line(h, l, c, f, 13) for f in (0.618, 1.618, 2.618)) / 3
    sm = ema(np.nan_to_num(avg, nan=c[0]), 21)
    ph = T.pivothigh(h, swing, swing); pl = T.pivotlow(l, swing, swing)
    atr_s = np.nan_to_num(T.atr_rma(h, l, c, swing)); slope = atr_s / swing
    n = len(c); ut = np.zeros(n); lt = np.zeros(n); us = ls = 0.0; ubs = np.zeros(n, int); lbs = np.zeros(n, int)
    for i in range(n):
        if ph[i]:
            us = slope[i]; ut[i] = h[i - swing]
        else:
            ut[i] = (ut[i - 1] if i else 0.0) - us
        if pl[i]:
            ls = slope[i]; lt[i] = l[i - swing]
        else:
            lt[i] = (lt[i - 1] if i else 0.0) + ls
        pu = ubs[i - 1] if i else 0; pd_ = lbs[i - 1] if i else 0
        ubs[i] = 0 if ph[i] else (1 if c[i] > ut[i] else pu)
        lbs[i] = 0 if pl[i] else (1 if c[i] < lt[i] else pd_)
    p, m, _ = dmi(h, l, c, dmi_n)
    L = (ubs > shift(ubs, 1)) & (p > m) & (c > sm)
    S = (lbs > shift(lbs, 1)) & (m > p) & (c < sm)
    c1 = shift(c, 1)
    XL = T.xunder(c1, sm); XS = T.xover(c1, sm)
    a13 = T.atr_rma(h, l, c, 13)
    na = np.full(n, NAN)
    r = gsim(df, mm, L, S, XL, XS, SLL=c - sl_atr * a13, TPL=c * (1 + tp) if tp else na,
             SLS=c + sl_atr * a13, TPS=c * (1 - tp) if tp else na, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. EMA STOCH (Crypto BOT lower TF)
def run_es(name, df, mm, tag, rows=None, verbose=True, sl=0.10, long_ok=True, short_ok=True, **extra):
    o, h, l, c = ohlc(df)
    e50, e100 = ema(c, 50), ema(c, 100)
    k = T.sma(stoch(c, h, l, 5), 3)
    hist = (lambda m_: m_ - ema(m_, 9))(ema(c, 12) - ema(c, 26))
    cr = np.zeros(len(c), bool); tch = np.zeros(len(c), bool)
    crossed = lambda x: T.xover(x, e50) | T.xunder(x, e50)
    for j in range(5):
        cr |= np.nan_to_num(shift(crossed(c).astype(float), j)) == 1
    for j in range(1, 5):
        tch |= np.nan_to_num(shift((crossed(l) | crossed(h)).astype(float), j)) == 1
    near = cr | tch
    L = near & (c > e50) & T.xover(k, np.full_like(k, 20.0)) & (e50 > e100) & (hist >= 0)
    S = near & (c < e50) & T.xunder(k, np.full_like(k, 80.0)) & (e50 < e100) & (hist <= 0)
    r = gsim(df, mm, L, S, slp=sl, tpp=sl, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 5. BTC bot
def weekly_r3(df, factor=2.0):
    w = df.resample('W-MON', label='left', closed='left').agg({'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    pp = (w.high + w.low + w.close) / 3
    r3 = (w.high + factor * (pp - w.low)).shift(1)       # semana anterior fechada
    return r3.reindex(df.index, method='ffill').to_numpy()


def run_btcb(name, df, mm, tag, rows=None, verbose=True, length=21, sl=0.15, tp=0.05, shorts=False, **extra):
    o, h, l, c = ohlc(df)
    vr = T.rsi_wilder(c, length); pp = ema(np.nan_to_num(vr, nan=50), length)
    cc = (vr + (vr - pp) * 5 + pp) / 2
    L = T.xover(cc, np.zeros_like(cc))
    S = T.xover(shift(c, 1), weekly_r3(df))
    if shorts:
        r = gsim(df, mm, L, S, slp=sl, tpp=tp, rev=True)
    else:
        r = gsim(df, mm, L, np.zeros_like(L), S, None, slp=sl, tpp=tp, rev=False)
    return run_g(name, df, r, tag, rows, verbose, extra)


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []; side2 = ('ambos', 'long')

        print("\n### 1. Spot/Binary Scalper (Tenkan7 + DI>20, sessao 04-15)")
        for tf in TFS:
            df = cache[tf]
            run_sbs(name, df, mm, f"{tf} SBS default", rows, est='sbs', TF=tf, cfg='sl0.5% sessao ambos')
            for sl, ses, side in itertools.product((0.0025, 0.005, 0.01, 0.02), (True, False), side2):
                run_sbs(name, df, mm, '', rows, False, sl=sl, session=ses, short_ok=side == 'ambos', est='sbs', TF=tf,
                        cfg=f'sl{sl:.2%} ' + ('sessao' if ses else '24h') + f' {side}')

        print("\n### 2. Combined Strategy (fita de EMAs + RSI + Stoch)")
        for tf in TFS:
            df = cache[tf]
            run_comb(name, df, mm, f"{tf} COMB default", rows, est='comb', TF=tf, cfg='osc ambos')
            for uo, side in itertools.product((True, False), side2):
                run_comb(name, df, mm, '', rows, False, use_osc=uo, short_ok=side == 'ambos', est='comb', TF=tf,
                         cfg=('osc' if uo else 'so EMAs') + f' {side}')

        print("\n### 3. TMFS (rompimento de LT + media de 3 SuperTrends)")
        for tf in TFS:
            df = cache[tf]
            run_tmfs(name, df, mm, f"{tf} TMFS default", rows, est='tmfs', TF=tf, cfg='sw8 sl8atr tp1% ambos')
            for sw, tp, side in itertools.product((8, 20), (0.01, 0.03, 0.0), side2):
                run_tmfs(name, df, mm, '', rows, False, swing=sw, tp=tp, short_ok=side == 'ambos', est='tmfs', TF=tf,
                         cfg=f'sw{sw} sl8atr tp{tp:.0%} {side}')

        print("\n### 4. EMA STOCH (Crypto BOT lower timeframes)")
        for tf in TFS:
            df = cache[tf]
            run_es(name, df, mm, f"{tf} ES default", rows, est='es', TF=tf, cfg='sl/tp10% ambos')
            for sl, side in itertools.product((0.01, 0.03, 0.10), side2):
                run_es(name, df, mm, '', rows, False, sl=sl, short_ok=side == 'ambos', est='es', TF=tf,
                       cfg=f'sl/tp{sl:.0%} {side}')

        print("\n### 5. BTC bot (cc do RSI21 x 0; saida no R3 semanal)")
        for tf in TFS:
            df = cache[tf]
            run_btcb(name, df, mm, f"{tf} BTCB default", rows, est='btcb', TF=tf, cfg='sl15% tp5% long')
            for tp, sh in itertools.product((0.03, 0.05, 0.10), (False, True)):
                run_btcb(name, df, mm, '', rows, False, tp=tp, shorts=sh, est='btcb', TF=tf,
                         cfg=f'sl15% tp{tp:.0%} ' + ('ambos' if sh else 'long'))

        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote15')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
