"""Varredura de liquidez + deslocamento + reteste (conceitos de price action, pseudocodigo do anexo).

Regra (por barra de tf, so dentro da janela de horario ET):
  1. Sweep de baixa: low < min(low[1..N]) e close > esse minimo -> arma compra; stop = low - 0.2*ATR.
     Sweep de alta simetrico arma venda. O estado zera fora da janela.
  2. Deslocamento: candle a favor com corpo >= k*ATR(14) e corpo/range >= 0.70 (pode ser o proprio
     candle do sweep ou um posterior, dentro da janela).
  3. Entrada LIMITADA: 'mid' = 50% do candle de deslocamento; 'fvg' = meio do FVG formado com o
     candle seguinte (low[j+1] > high[j-1] na compra), senao nao entra.
  4. Ordem vale EXP barras de tf; cancela se o alvo for tocado antes do preenchimento.
  5. Alvo = RR*R; breakeven apos +1R (opcional); stop/alvo resolvidos no M1, stop primeiro no mesmo
     minuto; saida forcada FLAT minutos apos o fim da janela.
  6. Filtro ATR opcional: ATR(14) > SMA(ATR,50).
Resultado por trade em R liquido: custo Lighter 2 pernas (CUSTO*preco/R) + funding pro-rata.
Conta: 1% de risco por trade, nao composto (anual% = soma(R)/anos).
Desenvolvimento ate 2023-12-31; 2024+ e fora da amostra.
"""
import sys, itertools, numpy as np, pandas as pd
from numba import njit
from tvlib import load_m1v, resample, atr_rma, CUSTO, FUND

CORTE = pd.Timestamp('2024-01-01', tz='UTC')
JANELAS = {'ldn': (180, 360), 'ny830': (510, 690), 'ny': (570, 720)}  # minutos ET [a, b)
FLAT = 240
EXP = 6


@njit(cache=True)
def sim(o, h, l, c, atr, atrok, et, day, m1beg, m1end, mo, mh, ml, mc, mday_et,
        N, k, use_atr, fvg, rr, be, wa, wb, flat):
    n = len(o)
    out = np.full((n, 7), np.nan)  # bar, lado, entrada, stop, saida, R bruto, minutos
    nt = 0
    arm = 0; stp = 0.0; i = N + 1
    while i < n - 2:
        inwin = et[i] >= wa and et[i] < wb
        if not inwin:
            arm = 0; i += 1; continue
        lo = 1e18; hi = -1e18
        for j in range(i - N, i):
            lo = min(lo, l[j]); hi = max(hi, h[j])
        if l[i] < lo and c[i] > lo:
            arm = 1; stp = l[i] - 0.2 * atr[i]
        if h[i] > hi and c[i] < hi:
            arm = -1; stp = h[i] + 0.2 * atr[i]
        if arm == 0 or (use_atr and not atrok[i]):
            i += 1; continue
        body = abs(c[i] - o[i]); rg = h[i] - l[i]
        if not (rg > 0 and body >= k * atr[i] and body / rg >= 0.7 and (c[i] - o[i]) * arm > 0):
            i += 1; continue
        side = arm; arm = 0
        sig = i
        if fvg:
            sig = i + 1
            if side == 1:
                if not (l[i + 1] > h[i - 1]): i += 1; continue
                ent = 0.5 * (l[i + 1] + h[i - 1])
            else:
                if not (h[i + 1] < l[i - 1]): i += 1; continue
                ent = 0.5 * (h[i + 1] + l[i - 1])
        else:
            ent = 0.5 * (h[i] + l[i])
        R = (ent - stp) * side
        if R <= 0:
            i += 1; continue
        tp = ent + side * rr * R
        # --- fase de ordem pendente no M1
        a = m1beg[sig]; e = m1end[min(sig + EXP, n - 1)]
        fill = -1
        for m in range(a, e):
            if side == 1:
                if mh[m] >= tp and ml[m] > ent: break
                if ml[m] <= ent: fill = m; break
            else:
                if ml[m] <= tp and mh[m] < ent: break
                if mh[m] >= ent: fill = m; break
        if fill < 0:
            i = sig + 1; continue
        # --- posicao
        dl = np.floor(mday_et[fill] / 1440.0) * 1440.0 + wb + flat
        sl = stp; besw = False; px = np.nan; m = fill; first = True
        while m < len(mo):
            if m > fill and mday_et[m] >= dl:
                px = mo[m]; break
            if side == 1:
                if ml[m] <= sl: px = min(sl, mo[m]) if not first else sl; break
                if mh[m] >= tp and not first: px = tp; break
                if be and mh[m] >= ent + R: sl = max(sl, ent)
            else:
                if mh[m] >= sl: px = max(sl, mo[m]) if not first else sl; break
                if ml[m] <= tp and not first: px = tp; break
                if be and ml[m] <= ent - R: sl = min(sl, ent)
            first = False; m += 1
        if np.isnan(px):
            break
        out[nt, 0] = sig; out[nt, 1] = side; out[nt, 2] = ent; out[nt, 3] = R
        out[nt, 4] = px; out[nt, 5] = side * (px - ent) / R; out[nt, 6] = m - fill
        nt += 1
        # pula ate a barra apos a saida
        while i < n - 2 and m1beg[i] <= m: i += 1
    return out[:nt]


def prep(name):
    m = load_m1v(name)
    m1t = m.index.values.astype('datetime64[m]').astype(np.int64)
    met = m.index.tz_convert('America/New_York')
    mmin = (met.tz_localize(None).values.astype('datetime64[m]').astype(np.int64)).astype(np.float64)
    M = dict(o=m.open.values, h=m.high.values, l=m.low.values, c=m.close.values, et=mmin / 1440.0, t=m1t)
    tfs = {}
    for tf, mins in (('5min', 5), ('15min', 15)):
        b = resample(m, tf)
        bt = b.index.values.astype('datetime64[m]').astype(np.int64)
        et = b.index.tz_convert('America/New_York')
        atr = atr_rma(b.high.values, b.low.values, b.close.values, 14)
        atrok = atr > pd.Series(atr).rolling(50).mean().values
        tfs[tf] = dict(o=b.open.values, h=b.high.values, l=b.low.values, c=b.close.values, atr=np.nan_to_num(atr),
                       atrok=np.nan_to_num(atrok).astype(np.bool_), et=(et.hour * 60 + et.minute).values,
                       wd=et.dayofweek.values,
                       beg=np.searchsorted(m1t, bt + mins), end=np.searchsorted(m1t, bt + mins), idx=b.index)
    return M, tfs


def run_cell(name, M, T, wn, N, k, ua, fvg, rr, be):
    wa, wb = JANELAS[wn]
    # minutos absolutos ET do M1 em "dias" (mday_et*1440 = minuto absoluto) -> passamos minuto absoluto/1440
    r = sim(T['o'], T['h'], T['l'], T['c'], T['atr'], T['atrok'], T['et'], T['wd'], T['beg'], T['end'],
            M['o'], M['h'], M['l'], M['c'], M['dabs'], N, k, ua, fvg, rr, be, wa, wb, FLAT)
    if len(r) == 0:
        return None
    t = pd.DataFrame(r, columns=['bar', 'side', 'ent', 'R', 'px', 'Rb', 'mins'])
    t['time'] = T['idx'][t.bar.astype(int).values]
    cst = 2 * CUSTO[name] * t.ent / t.R
    fund = FUND[name] / 100 * t.mins / (365 * 1440) * t.side * t.ent / t.R
    t['Rn'] = t.Rb - cst - fund
    t['custoR'] = cst
    return t


def stats(t, a, b):
    s = t[(t.time >= a) & (t.time < b)]
    yrs = (b - a).days / 365.25
    if len(s) < 2:
        return dict(n=len(s))
    r = s.Rn.values
    eq = np.cumsum(r)
    return dict(n=len(s), tpa=round(len(s) / yrs, 1), hit=round((r > 0).mean(), 3), expR=round(r.mean(), 3),
                anual=round(r.sum() / yrs, 1), sharpe=round(r.mean() / r.std() * np.sqrt(len(s) / yrs), 2),
                ddR=round((eq - np.maximum.accumulate(eq)).min(), 1), custoR=round(s.custoR.mean(), 3))


GRID = list(itertools.product(['5min', '15min'], list(JANELAS), [10, 20, 40], [1.0, 1.5, 2.0], [0, 1], [0, 1],
                              [1.5, 2.0, 2.5, 3.0], [0, 1]))


def main(name):
    M, tfs = prep(name)
    # minuto absoluto ET (para deadline): passa como dias ET "fracionarios" * 1440 = minuto; usamos minutos/1440 inteiro
    M['dabs'] = M['et'] * 1440.0  # minuto absoluto ET
    t0 = tfs['5min']['idx'][0]; t1 = tfs['5min']['idx'][-1]
    rows = []; best = {}
    for tf, wn, N, k, ua, fvg, rr, be in GRID:
        t = run_cell(name, M, tfs[tf], wn, N, k, ua, fvg, rr, be)
        if t is None:
            continue
        ins = stats(t, t0, CORTE); oos = stats(t, CORTE, t1)
        rows.append(dict(ativo=name, tf=tf, jan=wn, N=N, k=k, atr=ua, fvg=fvg, rr=rr, be=be,
                         **{f'is_{a}': v for a, v in ins.items()}, **{f'oos_{a}': v for a, v in oos.items()}))
        best[(tf, wn, N, k, ua, fvg, rr, be)] = t
    g = pd.DataFrame(rows)
    g.to_csv(f'../results/sweep_{name}_grid.csv', index=False)
    return g, best


if __name__ == '__main__':
    for a in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
        g, _ = main(a)
        ok = g[g.is_n >= 100]
        print(a, len(g), 'celulas; IS>0:', round((ok.is_anual > 0).mean(), 3), 'OOS>0:', round((ok.oos_anual > 0).mean(), 3),
              'corr Sharpe IS/OOS:', round(ok.is_sharpe.corr(ok.oos_sharpe), 2), flush=True)
