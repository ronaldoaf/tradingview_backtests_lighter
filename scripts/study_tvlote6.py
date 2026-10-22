"""Lote 6 do TradingView (2026-10-21): 4 estrategias (a 5a da lista, ICT Master Suite, fica de fora;
ver docs/LOTE6_TV.md).

  1. Hammers & Stars Strategy v1.2 (ZenAndTheArtOfTrading, t776tkZv, Pine v6)
     Martelo: corpo inteiro no terco superior da vela (fib 0.333), range <= 3 ATR; estrela espelhada.
     Entrada a mercado, stop no menor low das 2 ultimas velas - 1 ATR, alvo 1R. So entra flat.
  2. Iron Support Resistance Automat / "Scalping Support Resistance" (HPotter, gp332Dao, Pine v5)
     Nivel = lowest(hlc3,10)[5]. Flat e close < nivel: buy STOP no nivel; close > nivel: sell STOP
     no nivel. Alvo e stop de 1% do nivel. Publicado com ShowBackTest=false: no historico NAO opera.
  3. Bollinger Band with RSI (pKOaIHpb, Pine v4)
     Long quando RSI(14) < 30 e close < BB(20,2) inferior; pyramiding=50 de US$1000 sobre
     US$10000. Saida em RSI > 70, alvo +10% / stop -25% do preco medio.
  4. SUPERTREND ATR WITH TRAILING STOP LOSS (L9GkARD2, Pine v4)
     SuperTrend de ATR(1) x 3. Long (default) quando a direcao e 1, sai quando vira ou o close
     cruza um stop de -3% que sobe 1:1 depois de +1% de lucro. Opcao SHORT espelhada.

Execucao: sinal no fechamento, ordem na abertura seguinte; stops/alvos/ordens stop de entrada
resolvidos no M1 (stop antes do alvo no mesmo minuto). Custo CUSTO + funding. Controle: mesmo lado
e mesma duracao, aberto-a-aberto (nao replica stop/alvo).

uso: python study_tvlote6.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_zigzagpa import _sim  # noqa: F401 (o import instala o controle vetorizado)
from study_tvlote4 import trades_frame, finish, lag

TFS = ['15min', '30min', '1h', '4h', '1D']


class M1:
    """Arrays do M1 e o mapeamento barra do grafico -> primeiro minuto."""
    def __init__(self, m1):
        self.idx = m1.index
        self.o = m1.open.to_numpy(float); self.h = m1.high.to_numpy(float); self.l = m1.low.to_numpy(float)
        self.no, self.nh, self.nl = -self.o, -self.l, -self.h      # espelho para o lado vendido

    def b2m(self, df):
        return self.idx.searchsorted(df.index).astype(np.int64)


@njit(cache=True)
def _bracket(mo, mh, ml, nmo, nmh, nml, a, b, side, sl, tp):
    """Primeiro toque de stop/alvo em [a,b) para o lado dado. Devolve (minuto, preco, codigo)."""
    if side > 0:
        return T_first_touch(mo, mh, ml, a, b, sl, tp, True)
    m, px, c = T_first_touch(nmo, nmh, nml, a, b, -sl, -tp, True)
    return m, -px, c


T_first_touch = T._first_touch


# ------------------------------------------------------------------ 1. Hammers & Stars
def hs_signals(df, atr_max=3.0, fib=0.333, ema_len=0):
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    atr = T.atr_rma(h, l, c, 14)
    rng = np.abs(h - l)
    atrf = (rng <= atr_max * atr) | (atr_max == 0)
    ema = pd.Series(c).ewm(span=max(ema_len, 1), adjust=False).mean().to_numpy()
    el = (ema_len == 0) | (c > ema); es = (ema_len == 0) | (c < ema)
    bullfib = (l - h) * fib + h; bearfib = (h - l) * fib + l
    lob = np.minimum(o, c); hib = np.maximum(o, c)
    ok = (c != o) & ~np.isnan(atr) & atrf
    return ok & (lob >= bullfib) & el, ok & (hib <= bearfib) & es, atr


@njit(cache=True)
def _hs_sim(o, h, l, c, L, S, atr, smult, rr, b2m, mo, mh, ml, nmo, nmh, nml, nm):
    n = len(c); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    i = 1; busy_until = -1          # minuto ate o qual ha posicao
    while i < n - 1:
        if b2m[i + 1] <= busy_until or not (L[i] or S[i]):
            i += 1; continue
        if L[i]:
            side = 1; st = min(l[i], l[i - 1]) - atr[i] * smult; tg = c[i] + (c[i] - st) * rr
        else:
            side = -1; st = max(h[i], h[i - 1]) + atr[i] * smult; tg = c[i] - (st - c[i]) * rr
        j = i + 1; a = b2m[j]
        m, px, code = _bracket(mo, mh, ml, nmo, nmh, nml, a, nm, side, st, tg)
        if code == 0:
            break
        jj = j
        while jj + 1 < n and b2m[jj + 1] <= m:
            jj += 1
        EI[k] = j; EJ[k] = max(jj, j + 1) if jj + 1 < n else jj; ES[k] = side; PI[k] = o[j]; PO[k] = px; k += 1
        busy_until = m
        i = jj          # a barra que contem a saida ja pode gerar sinal no seu fechamento
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_hs(name, df, mm, tag, rows=None, verbose=True, smult=1.0, rr=1.0, fib=0.333, ema_len=0,
           long_ok=True, short_ok=True, **extra):
    L, S, atr = hs_signals(df, 3.0, fib, ema_len)
    if not long_ok: L = np.zeros_like(L)
    if not short_ok: S = np.zeros_like(S)
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    r = _hs_sim(o, h, l, c, L, S, atr, smult, rr, mm.b2m(df), mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl,
                len(mm.o))
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 2. Iron Support Resistance
@njit(cache=True)
def _sr_sim(o, c, lev, b2m, mo, mh, ml, nmo, nmh, nml, nm, tpp, slp, long_ok, short_ok):
    n = len(c); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); ES = np.empty(n, np.int64)
    PI = np.empty(n); PO = np.empty(n)
    i = 0
    while i < n - 1:
        L = lev[i]
        if L != L or c[i] == L:
            i += 1; continue
        side = 1 if c[i] < L else -1
        if (side > 0 and not long_ok) or (side < 0 and not short_ok):
            i += 1; continue
        a = b2m[i + 1]; b = b2m[i + 2] if i + 2 < n else nm
        fm = -1; fpx = 0.0
        for m in range(a, b):                       # ordem stop de entrada valida so na barra i+1
            if side > 0 and mh[m] >= L:
                fm = m; fpx = max(mo[m], L); break
            if side < 0 and ml[m] <= L:
                fm = m; fpx = min(mo[m], L); break
        if fm < 0:
            i += 1; continue
        tg = L + side * L * tpp; st = L - side * L * slp
        # minuto da entrada: o restante dele conta (stop primeiro), como ordem OCO apos o fill
        m, px, code = _bracket(mo, mh, ml, nmo, nmh, nml, fm, nm, side, st, tg)
        if code == 0:
            break
        j = i + 1; jj = j
        while jj + 1 < n and b2m[jj + 1] <= m:
            jj += 1
        EI[k] = j; EJ[k] = max(jj, j + 1) if jj + 1 < n else jj; ES[k] = side; PI[k] = fpx; PO[k] = px; k += 1
        i = jj
    return EI[:k], EJ[:k], ES[:k], PI[:k], PO[:k]


def run_sr(name, df, mm, tag, rows=None, verbose=True, lb=10, pb=5, tp=1.0, sl=1.0, long_ok=True,
           short_ok=True, **extra):
    hlc3 = ((df.high + df.low + df.close) / 3).to_numpy(float)
    lev = lag(pd.Series(hlc3).rolling(lb).min().to_numpy(), pb)
    r = _sr_sim(df.open.to_numpy(float), df.close.to_numpy(float), lev, mm.b2m(df), mm.o, mm.h, mm.l,
                mm.no, mm.nh, mm.nl, len(mm.o), tp / 100, sl / 100, long_ok, short_ok)
    tr = trades_frame(df, *r, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 3. Bollinger + RSI (pyramiding 50)
@njit(cache=True)
def _bbrsi_sim(o, h, l, E, X, tp, sl, maxu):
    """Long com piramide: cada barra com sinal soma 1 unidade (abertura seguinte) ate maxu. Alvo/stop
    sobre o preco medio, testados na barra (stop primeiro); RSI>70 fecha na abertura seguinte."""
    n = len(o); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64); U = np.empty(n); PI = np.empty(n); PO = np.empty(n)
    units = 0; cost = 0.0; i0 = -1; pend = False; close_next = False
    for j in range(1, n):
        if close_next and units > 0:
            EI[k] = i0; EJ[k] = j; U[k] = units; PI[k] = cost / units; PO[k] = o[j]; k += 1
            units = 0; cost = 0.0
        close_next = False
        if pend and units < maxu:
            if units == 0: i0 = j
            units += 1; cost += o[j]
        pend = False
        if units > 0:
            avg = cost / units
            st = avg * (1 - sl); tg = avg * (1 + tp)
            px = 0.0
            if o[j] <= st: px = o[j]
            elif l[j] <= st: px = st
            elif o[j] >= tg: px = o[j]
            elif h[j] >= tg: px = tg
            if px > 0:
                EI[k] = i0; EJ[k] = min(j + 1, n - 1); U[k] = units; PI[k] = avg; PO[k] = px; k += 1
                units = 0; cost = 0.0
        if E[j]: pend = True
        if X[j] and units > 0: close_next = True
    return EI[:k], EJ[:k], U[:k], PI[:k], PO[:k]


def run_bbrsi(name, df, tag, rows=None, verbose=True, rsi_lo=30, rsi_hi=70, bbl=20, mult=2.0, tp=0.10,
              sl=0.25, maxu=50, unit=0.1, **extra):
    c = df.close.to_numpy(float)
    rsi = T.rsi_wilder(c, 14)
    lower = T.sma(c, bbl) - mult * T.stdev_pop(c, bbl)          # stdev do Pine = populacional
    E = (rsi < rsi_lo) & (c < lower); X = rsi > rsi_hi
    ei, ej, u, pi, po = _bbrsi_sim(df.open.to_numpy(float), df.high.to_numpy(float),
                                   df.low.to_numpy(float), E, X, tp, sl, maxu)
    tr = trades_frame(df, ei, ej, np.ones(len(ei), np.int64), pi, po, name)
    if len(tr):
        tr['u'] = u * unit                                    # US$1000 por unidade sobre US$10000
        for col in ('bruto', 'ret_sf', 'fund', 'ret'):
            tr[col] = tr[col] * tr.u
        tr['u_raw'] = u
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ 4. SuperTrend ATR com trailing
@njit(cache=True)
def _st_dir(h, l, c, atr):
    n = len(c); d = np.ones(n); ls = np.zeros(n); ss = np.zeros(n)
    for i in range(n):
        hl2 = (h[i] + l[i]) / 2
        a = atr[i]
        lsv = hl2 - a; ssv = hl2 + a
        lp = ls[i - 1] if i and ls[i - 1] == ls[i - 1] else lsv
        sp = ss[i - 1] if i and ss[i - 1] == ss[i - 1] else ssv
        if i and c[i - 1] > lp: lsv = max(lsv, lp)
        if i and c[i - 1] < sp: ssv = min(ssv, sp)
        ls[i] = lsv; ss[i] = ssv
        dd = d[i - 1] if i else 1.0
        if dd == -1 and c[i] > sp: dd = 1
        elif dd == 1 and c[i] < lp: dd = -1
        d[i] = dd
    return d


@njit(cache=True)
def _sttsl_sim(c, d, side, init_sl):
    """Reproduz a maquina de estados do script (decisoes no fechamento, fills na abertura seguinte).
    side=1 LONG, -1 SHORT."""
    n = len(c); k = 0
    EI = np.empty(n, np.int64); EJ = np.empty(n, np.int64)
    pos = 0; i0 = -1; entry = 0.0; upd = 0.0; slp_price = 0.0
    for i in range(n - 1):
        slpct = -init_sl if side > 0 else init_sl          # nao-var: reinicia a cada barra
        crossed = (c[i] <= slp_price) if side > 0 else (c[i] >= slp_price)
        close_cond = d[i] == -1 if side > 0 else d[i] == 1
        open_cond = d[i] == 1 if side > 0 else d[i] == -1
        new_pos = pos
        if pos != 0 and (crossed or close_cond):
            entry = 0.0; upd = 0.0; slp_price = 0.0
            new_pos = 0
        if pos == 0 and open_cond:
            entry = c[i]; upd = entry; slp_price = entry + entry * slpct / 100
            new_pos = side
        if upd != 0.0 and pos != 0:
            pct = (c[i] - upd) / upd * 100
            if (side > 0 and pct > 1) or (side < 0 and pct < -1):
                slpct = slpct + pct + (-1.0 if side > 0 else 1.0)
                nsl = upd + upd * slpct / 100
                slp_price = max(slp_price, nsl) if side > 0 else min(slp_price, nsl)
                upd = slp_price
        if new_pos != pos:
            j = i + 1
            if pos != 0:
                EI[k] = i0; EJ[k] = j; k += 1
            if new_pos != 0:
                i0 = j
            pos = new_pos
    return EI[:k], EJ[:k]


def run_sttsl(name, df, tag, rows=None, verbose=True, side=1, period=1, mult=3.0, init_sl=3.0, **extra):
    h, l, c = (df[k].to_numpy(float) for k in ('high', 'low', 'close'))
    if period == 1:
        pc = np.concatenate([[np.nan], c[:-1]])
        atr = np.fmax(h - l, np.fmax(np.abs(h - pc), np.abs(l - pc)))
    else:
        atr = T.atr_rma(h, l, c, period)
    d = _st_dir(h, l, c, mult * np.nan_to_num(atr))
    ei, ej = _sttsl_sim(c, d, side, init_sl)
    tr = T.book(df, [(i, j, side) for i, j in zip(ei, ej)], name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


# ------------------------------------------------------------------ main
def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []

        print("\n### 1. Hammers & Stars (stop 1 ATR, alvo 1R)")
        for tf in TFS:
            df = cache[tf]
            run_hs(name, df, mm, f"{tf} HS default", rows, est='hs', TF=tf, cfg='s1 rr1 fib.333 ema0')
            for sm, rr, fib, ema, lo in itertools.product((0.5, 1.0, 2.0), (1.0, 1.5, 2.0), (0.333, 0.25),
                                                          (0, 50, 200), (False, True)):
                run_hs(name, df, mm, '', rows, verbose=False, smult=sm, rr=rr, fib=fib, ema_len=ema,
                       short_ok=not lo, est='hs', TF=tf,
                       cfg=f's{sm} rr{rr} fib{fib} ema{ema}' + (' so long' if lo else ''))

        print("\n### 2. Iron Support Resistance (10/5, 1%/1%) com ShowBackTest=true")
        for tf in TFS:
            df = cache[tf]
            run_sr(name, df, mm, f"{tf} SR default", rows, est='sr', TF=tf, cfg='lb10 pb5 tp1 sl1')
            for lb, pb, tp, sl, lo in itertools.product((10, 20), (2, 5), (0.5, 1.0, 2.0), (0.5, 1.0, 2.0),
                                                        (False, True)):
                run_sr(name, df, mm, '', rows, verbose=False, lb=lb, pb=pb, tp=tp, sl=sl, short_ok=not lo,
                       est='sr', TF=tf, cfg=f'lb{lb} pb{pb} tp{tp} sl{sl}' + (' so long' if lo else ''))

        print("\n### 3. Bollinger Band with RSI (piramide 50 x 10% do capital)")
        for tf in TFS:
            df = cache[tf]
            run_bbrsi(name, df, f"{tf} BBRSI default", rows, est='bbrsi', TF=tf, cfg='30/70 pyr50')
            run_bbrsi(name, df, f"{tf} BBRSI 1 unidade 1x", rows, maxu=1, unit=1.0, est='bbrsi', TF=tf,
                      cfg='30/70 u1')
            for lo_, hi_, mult, mu in itertools.product((20, 25, 30, 35), (60, 70, 80), (1.5, 2.0, 2.5),
                                                       ((1, 1.0), (10, 0.1))):
                run_bbrsi(name, df, '', rows, verbose=False, rsi_lo=lo_, rsi_hi=hi_, mult=mult, maxu=mu[0],
                          unit=mu[1], est='bbrsi', TF=tf, cfg=f'{lo_}/{hi_} bb{mult} u{mu[0]}')

        print("\n### 4. SuperTrend ATR(1)x3 com trailing stop (LONG por default)")
        for tf in TFS:
            df = cache[tf]
            run_sttsl(name, df, f"{tf} STTSL LONG", rows, est='sttsl', TF=tf, cfg='LONG p1 m3 sl3')
            run_sttsl(name, df, f"{tf} STTSL SHORT", rows, side=-1, est='sttsl', TF=tf, cfg='SHORT p1 m3 sl3')
            for side, per, mult, isl in itertools.product((1, -1), (1, 10), (1.0, 2.0, 3.0, 4.0), (1.0, 3.0, 5.0)):
                run_sttsl(name, df, '', rows, verbose=False, side=side, period=per, mult=mult, init_sl=isl,
                          est='sttsl', TF=tf, cfg=f"{'LONG' if side > 0 else 'SHORT'} p{per} m{mult} sl{isl}")

        g = pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg'])
        g.to_csv(os.path.join(D, 'results', f'study_tvlote6_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        for est, h in g.groupby('est'):
            print(f"  {est:6s} {len(h):4d} cel | liq>0 {int((h.bp_liq > 0).sum()):4d} | "
                  f"liq>0 e t>2 {int(((h.bp_liq > 0) & (h.t > 2)).sum()):3d} | "
                  f"CAGR>B&H {int((h.cagr > h.bh).sum()):3d} | melhor CAGR {h.cagr.max():+.1%}")
        cols = ['est', 'TF', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh',
                'sharpe', 'dd', 'expo', 'ctl_bp', 't']
        print("\n  top 15 por CAGR:")
        print(g.sort_values('cagr', ascending=False).head(15)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))
        print("\n  top 10 por t:")
        print(g.sort_values('t', ascending=False).head(10)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
