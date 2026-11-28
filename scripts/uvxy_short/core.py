"""Nucleo do estudo "short estrutural no UVXY" (perp da AlphaX).

- load(): tabela diaria com UVXY real (2011+), UVXY sintetico 1,5x (2006+, a partir do
  ^SHORTVOL), VIX, VIX3M, VIX9D, VVIX, S&P 500 e o preco do UVXY as 16:20 ET (M1 Alpaca, 2016+).
- sim(): simulador diario de uma posicao vendida com exposicao-alvo w[t] (fracao do
  patrimonio), custos por perna, funding, banda de rebalanceio, stop intradiario e liquidacao.
- stats(): metricas (CAGR, vol, Sharpe, MDD, Calmar, pior dia, tempo exposto, giro).

Convencoes
- w[t] e decidido com dados ate o fechamento do dia t.
- exec='open'  : executa na abertura de t+1 (padrao, conservador).
  exec='close' : executa no fechamento de t (otimista: ignora os 15 min entre 16:00 e 16:15).
  exec='pm'    : executa no preco das 16:20 ET de t (pos-mercado, M1 Alpaca; o perp opera 24/7).
- fund[t] e a fracao do nocional recebida pelo vendido entre o fechamento t-1 e t
  (negativo = vendido paga).
"""
import os
import numpy as np
import pandas as pd
from numba import njit

ROOT = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DD = os.path.join(ROOT, 'data', 'uvxy')

# Funding medido no perp UVXY da AlphaX (jun-nov/2026), em fracao do nocional por pregao,
# recebido pelo vendido, segundo o regime da estrutura a termo no fechamento anterior.
FUND_CONTANGO = 5.5e-4 / 1.0   # +5,5 bp/pregao quando VIX/VIX3M < 1 (~ +14%/ano)
FUND_BACKW = -33e-4            # -33 bp/pregao quando VIX/VIX3M >= 1
COST = 10e-4                   # 10 bp por perna (meio spread ~6,5 bp medido + slippage)
MMR = 0.025                    # margem de manutencao do primeiro degrau (AlphaX)


def _d(s):
    return pd.read_parquet(os.path.join(DD, f'daily_{s}.parquet'))


def pm_price(minute='16:20'):
    """Preco do UVXY no M1 da Alpaca no horario ET dado (ou o ultimo antes dele, apos 16:00)."""
    m = pd.read_parquet(os.path.join(DD, 'uvxy_1m.parquet')).close
    m.index = m.index.tz_convert('America/New_York')
    hh, mm = map(int, minute.split(':'))
    t = m.index.hour * 60 + m.index.minute
    sel = m[(t >= 16 * 60) & (t <= hh * 60 + mm)]
    out = sel.groupby(sel.index.normalize().tz_localize(None)).last()
    out.index.name = 'date'
    return out


def load(with_pm=True):
    u = _d('uvxy')
    sv = _d('shortvol').close
    D = pd.DataFrame({'o': u.open, 'h': u.high, 'l': u.low, 'c': u.close})
    idx = sv.index.union(D.index)
    D = D.reindex(idx)
    D['sv'] = sv.reindex(idx)
    for k, s in (('vix', 'vix'), ('vix3m', 'vix3m'), ('vix9d', 'vix9d'), ('vvix', 'vvix'), ('spx', 'gspc'),
                 ('qqq', 'qqq'), ('spy', 'spy')):
        D[k] = _d(s).close.reindex(idx)
    D['vixo'] = _d('vix').open.reindex(idx)
    D['vixh'] = _d('vix').high.reindex(idx)
    # dias de pregao: onde ha SPX
    D = D[D.spx.notna()]
    # UVXY sintetico 1,5x: retorno diario = 1,5 * (-ret SHORTVOL) - taxa 0,95%/ano
    rl = -D.sv.pct_change()
    D['syn_r'] = 1.5 * rl - 0.0095 / 252
    D['syn'] = (1 + D.syn_r.fillna(0)).cumprod()
    if with_pm:
        D['pm'] = pm_price().reindex(D.index)
    D['ts'] = D.vix / D.vix3m
    D['cal'] = pd.Series(D.index, index=D.index).diff().dt.days.fillna(1).values
    return D


def fund_model(ts, contango=FUND_CONTANGO, backw=FUND_BACKW):
    """Funding por pregao recebido pelo vendido, pelo regime no fechamento anterior."""
    prev = pd.Series(ts).shift(1).values
    f = np.where(prev >= 1.0, backw, contango)
    f[np.isnan(prev)] = contango
    return f


@njit(cache=True)
def _rebal(eq, q, p, tgt, cost, band, allow_entry):
    """Rebalanceia q (acoes vendidas) para tgt*eq/p quando a exposicao sai da banda multiplicativa
    [tgt/(1+band), tgt*(1+band)]. Retorna eq, q, giro (fracao do equity)."""
    cur = q * p / eq if eq > 0 else 0.0
    if tgt <= 0:
        if q > 0:
            eq -= cost * q * p
            return eq, 0.0, cur
        return eq, q, 0.0
    if q == 0 and not allow_entry:
        return eq, q, 0.0
    if q == 0 or cur > tgt * (1 + band) or cur < tgt / (1 + band):
        if not allow_entry and tgt * eq / p > q:
            return eq, q, 0.0
        nq = tgt * eq / p
        tr = abs(nq - q) * p / eq
        eq -= cost * abs(nq - q) * p
        return eq, nq, tr
    return eq, q, 0.0


@njit(cache=True)
def _sim(O, H, C, X, w, fund, mode, cost, band, stop, cool, mmr):
    """mode 0: executa em C[t]; 1: em O[t+1]; 2: em X[t] (preco pos-mercado de t).
    Stop: zera se o preco sobe stop (fracao) acima do fechamento anterior (gap -> executa na abertura).
    cool: pregoes sem novas entradas depois de um stop.
    Retorna equity no fechamento, giro diario, exposicao no fechamento, numero de stops, flag de liquidacao."""
    n = len(C)
    E = np.empty(n); EXP = np.zeros(n); TURN = np.zeros(n)
    eq = 1.0; q = 0.0
    nstop = 0; liq = 0; cd = 0
    E[0] = eq
    pend = 0.0
    for t in range(1, n):
        if eq <= 0 or liq == 1:
            E[t] = 0.0
            continue
        p0 = C[t - 1]
        eq += q * p0 * fund[t]
        stopped = False
        lvl = p0 * (1 + stop)
        seg = p0
        if mode == 1:
            o = O[t]
            if q > 0 and stop > 0 and o >= lvl:
                eq -= q * (o - p0); eq -= cost * q * o; TURN[t] += q * o / max(eq, 1e-12); q = 0.0
                stopped = True
            else:
                eq -= q * (o - p0)
                if q > 0 and eq <= mmr * q * o:
                    liq = 1; eq = 0.0; q = 0.0; E[t] = 0.0
                    continue
                eq, q, tr = _rebal(eq, q, o, pend, cost, band, cd == 0)
                TURN[t] += tr
            seg = o
        px = C[t] if mode != 2 else X[t]
        if q > 0:
            if stop > 0 and not stopped and H[t] >= lvl:
                fill = max(lvl, seg)
                eq -= q * (fill - seg); eq -= cost * q * fill; TURN[t] += q * fill / max(eq, 1e-12); q = 0.0
                stopped = True
            elif eq - q * (H[t] - seg) <= mmr * q * H[t]:
                liq = 1; eq = 0.0; q = 0.0; E[t] = 0.0
                continue
            else:
                eq -= q * (px - seg)
        if mode != 1 and not stopped:
            eq, q, tr = _rebal(eq, q, px, w[t], cost, band, cd == 0)
            TURN[t] += tr
        if mode == 2 and q > 0:
            eq -= q * (C[t] - px)
        if stopped:
            nstop += 1; cd = cool
        elif cd > 0:
            cd -= 1
        pend = w[t]
        E[t] = eq
        EXP[t] = q * C[t] / eq if eq > 0 else 0.0
    return E, TURN, EXP, nstop, liq


def sim(D, w, px='c', exec='open', fund=None, cost=COST, band=0.0, stop=0.0, cool=0, mmr=MMR):
    """D: tabela de load() (ja recortada). px: 'c' (UVXY real) ou 'syn' (sintetico; sem O/H)."""
    if px == 'c':
        O, H, C = D.o.values, D.h.values, D.c.values
    else:
        C = D[px].values
        O = C.copy(); H = C.copy()
        if 'syn_o' in D:
            O = D.syn_o.values; H = D.syn_h.values
    X = D.pm.values if exec == 'pm' else C
    if exec == 'pm':
        X = np.where(np.isnan(X), C, X)
    w = np.nan_to_num(np.asarray(w, dtype=float))
    f = np.zeros(len(C)) if fund is None else np.nan_to_num(np.asarray(fund, dtype=float))
    mode = {'close': 0, 'open': 1, 'pm': 2}[exec]
    E, T, X_, ns, lq = _sim(O.astype(float), H.astype(float), C.astype(float), X.astype(float), w, f, mode,
                            cost, band, stop, cool, mmr)
    return pd.DataFrame({'equity': E, 'turn': T, 'exp': X_}, index=D.index), ns, lq


def stats(res, ns=0, lq=0):
    e = res.equity
    r = e.pct_change().fillna(0)
    yrs = (e.index[-1] - e.index[0]).days / 365.25
    cagr = (e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1 if e.iloc[-1] > 0 else -1.0
    vol = r.std() * np.sqrt(252)
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    dd = (e / e.cummax() - 1).min()
    return dict(cagr=cagr, vol=vol, sharpe=sh, mdd=dd, calmar=cagr / abs(dd) if dd < 0 else np.nan,
                worst=r.min(), expo=(res.exp > 0).mean(), lev=res.exp[res.exp > 0].mean() if (res.exp > 0).any() else 0,
                turn=res.turn.sum() / yrs, stops=ns / yrs, liq=lq)


def yearly(res):
    e = res.equity
    y = e.resample('YE').last()
    y0 = pd.concat([pd.Series([e.iloc[0]], index=[e.index[0]]), y])
    out = y0.pct_change().dropna()
    out.index = out.index.year
    return out


def fmt(s):
    return ('CAGR %6.1f%%  vol %5.1f%%  Sh %5.2f  MDD %6.1f%%  Calmar %5.2f  pior dia %6.1f%%  exposto %3.0f%%  '
            'lev %.2f  giro %5.1fx/a  stops %4.1f/a%s' % (
                s['cagr'] * 100, s['vol'] * 100, s['sharpe'], s['mdd'] * 100, s['calmar'], s['worst'] * 100,
                s['expo'] * 100, s['lev'], s['turn'], s['stops'], '  LIQUIDOU' if s['liq'] else ''))
