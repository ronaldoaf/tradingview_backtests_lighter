"""Buy&Sell Strategy depends on AO+Stoch+RSI+ATR by SerdarYILMAZ (TradingView RpYoQCVJ)
- traducao fiel do Pine (fonte aberta, PUB;TfrUjDEBUT7M7cNaUcJOBmhkoI0Syx58) e teste em ouro com
M1 da Dukascopy, com OOS em US100/BTC/WTI/ETH.

O proprio autor avisa no codigo: "This strategy is just for training... Don't make buy or sell
decision with this strategy." Testo de todo jeito, como as outras da fila.

Regras (defaults do Pine entre parenteses):
  AO    : awesome = (sma(hl2, fast=5) - sma(hl2, slow=34)) * 1000      (o *1000 e so escala de plot)
  Stoch : k = sma(stoch(close,high,low, K=14), D=3)   (d = sma(k, smooth=3) e calculado e NAO usado)
  RSI   : rsi = rsi(close, rsilength=10)
  ATR   : atrvalue = rma(tr, atrlen=14)
  Long  : k < 20 and rsi < 30 and awesome > awesome[1]
          stoploss = low - atr ; takeprofit = close + atr   (NIVEIS ABSOLUTOS do fechamento do sinal)
  Short : k > 80 and rsi > 70 and awesome < awesome[1]
          stoploss = high + atr ; takeprofit = close - atr
  ordem : strategy.entry e a mercado -> fill na ABERTURA da barra seguinte; strategy.exit e
          chamado na BARRA DO SINAL, logo o bracket ja esta no book quando a entrada executa
          (barra de entrada protegida; PROT=0 testa o contrario).
  QUIRK CENTRAL: o alvo dista exatamente 1 ATR do close, mas o stop dista (close-low) + 1 ATR.
          O payoff e portanto ASSIMETRICO CONTRA (RR < 1) por construcao - nada no script compensa
          isso com taxa de acerto. Mede-se aqui como RR efetivo.
  QUIRK 2: strategy.exit("TP/SL") e chamado sem from_entry -> vale para qualquer entrada aberta;
          como as condicoes long/short sao mutuamente exclusivas e extremas, a inversao
          praticamente nao ocorre. FLIP=1 (sinal contrario inverte) e o default; FLIP=0 contrasta.
  QUIRK 3: nao ha filtro de tendencia nem de sessao; e sobrecompra/sobrevenda pura em 3 osciladores
          com concordancia exigida (k<20 E rsi<30 E AO subindo), o que deixa a amostra pequena.

Execucao aqui: sinais no TF do grafico (15m/30m/1h/4h/1D) a partir do M1; dentro do trade andamos
no M1, com os niveis ABSOLUTOS congelados no fechamento da barra do sinal, como as ordens do Pine.
A abertura de cada M1 e testada primeiro, entao um gap que pula o stop sai NA ABERTURA (pior que o
stop). Convencao conservadora ORD=0 (stop antes do alvo no mesmo minuto) e otimista ORD=1.
Medida em R: 1 trade = 1R de risco, com R = |fill - stop| medido no FILL REAL.
Custo: CUSTO[ativo] por perna (spread da Lighter) + funding FUND[ativo] pro-rata (long paga).
Controle: para cada trade, 20 entradas a mercado em barras sorteadas com o MESMO lado, MESMO risco
relativo, MESMO alvo em R e MESMA duracao maxima -> isola o que a confluencia dos 3 osciladores
acrescenta sobre entrar no acaso com o mesmo bracket.

uso: python study_serdar.py [xau us100 btc wti eth ...]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_commas import (CUSTO, FUND, OHLC, load_m1, minutes, resample,
                          rma, sma, true_range, roll_max, roll_min)

TFS = {'15min': 15, '30min': 30, '1h': 60, '4h': 240, '1D': 1440}
BASE = dict(TF='1h', FAST=5, SLOW=34, K=14, DD=3, RSILEN=10, ATRLEN=14,
            KLO=20.0, KHI=80.0, RLO=30.0, RHI=70.0, ATRM=1.0, RNR=0.0,
            FLIP=1, LONG=1, SHORT=1, PROT=1, ORD=0, MAXBARS=0)
# RNR=0 => alvo do Pine (1 ATR do close). RNR>0 => alvo = fill + RNR * risco (para contraste).


@njit(cache=True)
def rsi_pine(c, n):
    """ta.rsi: rma dos ganhos/perdas (seed = media simples das n primeiras diferencas)."""
    m = len(c); out = np.full(m, np.nan)
    if m <= n: return out
    up = np.zeros(m); dn = np.zeros(m)
    for i in range(1, m):
        d = c[i] - c[i - 1]
        if d > 0: up[i] = d
        else: dn[i] = -d
    su = 0.0; sd = 0.0
    for i in range(1, n + 1): su += up[i]; sd += dn[i]
    au = su / n; ad = sd / n
    out[n] = 100.0 if ad == 0 else 100.0 - 100.0 / (1 + au / ad)
    a = 1.0 / n
    for i in range(n + 1, m):
        au = a * up[i] + (1 - a) * au
        ad = a * dn[i] + (1 - a) * ad
        out[i] = 100.0 if ad == 0 else 100.0 - 100.0 / (1 + au / ad)
    return out


def stoch_pine(c, h, l, n):
    hh = roll_max(h, n); ll = roll_min(l, n)
    rng = hh - ll
    with np.errstate(invalid='ignore', divide='ignore'):
        out = 100.0 * (c - ll) / rng
    out[rng == 0] = 0.0                        # ta.stoch com faixa nula -> 0 (como o Pine)
    out[np.isnan(hh) | np.isnan(ll)] = np.nan
    return out


@njit(cache=True)
def manage(j0, side, sl, tp, i0, i1, o1, h1, l1, c1, t1, prot, ordem, maxb):
    """Entra a mercado na abertura da barra j0 com niveis ABSOLUTOS sl/tp congelados.
    Devolve (fill, R, barra_saida, minuto_saida, motivo)."""
    a0 = i0[j0]
    fill = o1[a0]
    risk = (fill - sl) * side
    if risk <= 0:
        return fill, 0.0, j0, t1[a0], 0.0, risk
    n = len(i0)
    live = prot == 1
    for j in range(j0, n):
        a, b = i0[j], i1[j]
        if b > a and live:
            for i in range(a, b):
                s = side
                if (o1[i] - sl) * s <= 0:
                    return fill, (o1[i] - fill) * s / risk, j, t1[i], 0.0, risk
                if (o1[i] - tp) * s >= 0:
                    return fill, (o1[i] - fill) * s / risk, j, t1[i], 1.0, risk
                hi = h1[i] if s == 1 else -l1[i]
                lo = l1[i] if s == 1 else -h1[i]
                ssl = sl if s == 1 else -sl
                stp = tp if s == 1 else -tp
                hitsl = lo <= ssl; hittp = hi >= stp
                if ordem == 0 and hitsl:
                    return fill, (sl - fill) * s / risk, j, t1[i], 0.0, risk
                if hittp:
                    return fill, (tp - fill) * s / risk, j, t1[i], 1.0, risk
                if ordem == 1 and hitsl:
                    return fill, (sl - fill) * s / risk, j, t1[i], 0.0, risk
        live = True
        if maxb > 0 and (j - j0) >= maxb:
            return fill, (c1[b - 1] - fill) * side / risk, j, t1[b - 1], 3.0, risk
    return fill, (c1[len(c1) - 1] - fill) * side / risk, n - 1, t1[len(t1) - 1], 5.0, risk


@njit(cache=True)
def engine(buy, sell, slL, slS, tpL, tpS, flip, prot, ordem, maxb,
           i0, i1, o1, h1, l1, c1, t1):
    """out: tent texit fill risk side R why barras tpdist"""
    n = len(i0)
    out = np.zeros((n + 8, 9))
    q = 0
    pos = 0; pend = 0
    fill = 0.0; risk = 0.0; sl = 0.0; tp = 0.0
    tent = 0.0; ebar = -1
    pend_sl = 0.0; pend_tp = 0.0
    for j in range(n):
        a, b = i0[j], i1[j]
        if b <= a: continue
        if pend != 0:
            px = o1[a]
            if pos != 0:
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = risk
                out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 4.0
                out[q, 7] = j - ebar; out[q, 8] = abs(tp - fill)
                q += 1; pos = 0
            pos = pend; fill = px; sl = pend_sl; tp = pend_tp
            risk = (fill - sl) * pos
            tent = t1[a]; ebar = j
            pend = 0
            if risk <= 0:                      # gap pulou o stop antes de entrar -> sai no proprio fill
                out[q, 0] = tent; out[q, 1] = t1[a]; out[q, 2] = fill; out[q, 3] = 1.0
                out[q, 4] = pos; out[q, 5] = 0.0; out[q, 6] = 0.0
                out[q, 7] = 0; out[q, 8] = abs(tp - fill)
                q += 1; pos = 0
        if pos != 0 and (prot == 1 or j > ebar):
            for i in range(a, b):
                s = pos
                done = 0; rr = 0.0; why = 0.0
                if (o1[i] - sl) * s <= 0:
                    rr = (o1[i] - fill) * s / risk; why = 0.0; done = 1
                elif (o1[i] - tp) * s >= 0:
                    rr = (o1[i] - fill) * s / risk; why = 1.0; done = 1
                else:
                    hi = h1[i] if s == 1 else -l1[i]
                    lo = l1[i] if s == 1 else -h1[i]
                    ssl = sl if s == 1 else -sl
                    stp = tp if s == 1 else -tp
                    hitsl = lo <= ssl; hittp = hi >= stp
                    if ordem == 0 and hitsl:
                        rr = (sl - fill) * s / risk; why = 0.0; done = 1
                    elif hittp:
                        rr = (tp - fill) * s / risk; why = 1.0; done = 1
                    elif ordem == 1 and hitsl:
                        rr = (sl - fill) * s / risk; why = 0.0; done = 1
                if done == 1:
                    out[q, 0] = tent; out[q, 1] = t1[i]; out[q, 2] = fill; out[q, 3] = risk
                    out[q, 4] = s; out[q, 5] = rr; out[q, 6] = why
                    out[q, 7] = j - ebar; out[q, 8] = abs(tp - fill)
                    q += 1; pos = 0
                    break
        if pos != 0 and maxb > 0 and (j - ebar) >= maxb:
            out[q, 0] = tent; out[q, 1] = t1[b - 1]; out[q, 2] = fill; out[q, 3] = risk
            out[q, 4] = pos; out[q, 5] = (c1[b - 1] - fill) * pos / risk; out[q, 6] = 3.0
            out[q, 7] = j - ebar; out[q, 8] = abs(tp - fill)
            q += 1; pos = 0
        if buy[j] == 1 and (pos == 0 or (pos == -1 and flip == 1)) and slL[j] == slL[j]:
            pend = 1; pend_sl = slL[j]; pend_tp = tpL[j]
        elif sell[j] == 1 and (pos == 0 or (pos == 1 and flip == 1)) and slS[j] == slS[j]:
            pend = -1; pend_sl = slS[j]; pend_tp = tpS[j]
    if pos != 0:
        px = c1[len(c1) - 1]
        out[q, 0] = tent; out[q, 1] = t1[len(t1) - 1]; out[q, 2] = fill; out[q, 3] = risk
        out[q, 4] = pos; out[q, 5] = (px - fill) * pos / risk; out[q, 6] = 5.0
        out[q, 7] = len(i0) - 1 - ebar; out[q, 8] = abs(tp - fill)
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, riscoRel, rrmult, durbars, i0, i1, o1, h1, l1, c1, t1, prot, ordem):
    m = len(starts); out = np.zeros(m)
    for z in range(m):
        j0 = starts[z]
        px = o1[i0[j0]]
        risk = abs(px) * riscoRel[z]
        sl = px - side[z] * risk
        tp = px + side[z] * rrmult[z] * risk
        _, r, _, _, _, _ = manage(j0, side[z], sl, tp, i0, i1, o1, h1, l1, c1, t1,
                                  prot, ordem, durbars[z])
        out[z] = r
    return out


_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'risk', 'side', 'R', 'why', 'barras', 'tpdist']
WHYS = {0.0: 'stop', 1.0: 'alvo', 3.0: 'time stop', 4.0: 'inversao', 5.0: 'fim'}


def build(name, m1, p):
    key = (name, p['TF'], p['FAST'], p['SLOW'], p['K'], p['DD'], p['RSILEN'], p['ATRLEN'], p['ATRM'])
    if key in _CACHE: return _CACHE[key]
    htf = resample(m1, p['TF'])
    o, h, l, c = (np.ascontiguousarray(htf[k].to_numpy(np.float64)) for k in OHLC)
    hl2 = (h + l) / 2.0
    ao = (sma(hl2, p['FAST']) - sma(hl2, p['SLOW'])) * 1000.0
    st = stoch_pine(c, h, l, p['K'])
    k = sma(np.ascontiguousarray(np.where(np.isnan(st), 0.0, st)), p['DD'])
    k[:p['K'] + p['DD'] - 2] = np.nan
    rsi = rsi_pine(c, p['RSILEN'])
    atr = rma(true_range(h, l, c), p['ATRLEN']) * p['ATRM']
    A = dict(htf=htf, o=o, h=h, l=l, c=c, th=minutes(htf.index), ao=ao, k=k, rsi=rsi, atr=atr,
             slL=l - atr, slS=h + atr, tpL=c + atr, tpS=c - atr)
    if len(_CACHE) > 8: _CACHE.clear()
    _CACHE[key] = A
    return A


def run_asset(name, m1, p, ctrl=False, seed=1, NR=20):
    A = build(name, m1, p)
    ao = A['ao']; pao = np.concatenate([[np.nan], ao[:-1]])
    ok = ~np.isnan(A['atr']) & ~np.isnan(A['k']) & ~np.isnan(A['rsi']) & ~np.isnan(pao)
    buy = ok & (A['k'] < p['KLO']) & (A['rsi'] < p['RLO']) & (ao > pao) & bool(p['LONG'])
    sell = ok & (A['k'] > p['KHI']) & (A['rsi'] > p['RHI']) & (ao < pao) & bool(p['SHORT'])
    slL, slS = A['slL'], A['slS']
    if p['RNR'] > 0:                                     # alvo por RR do risco (contraste)
        tpL = A['c'] + p['RNR'] * (A['c'] - slL)
        tpS = A['c'] - p['RNR'] * (slS - A['c'])
    else:
        tpL, tpS = A['tpL'], A['tpS']
    t1 = minutes(m1.index).astype(np.int64)
    th = A['th']
    i0 = np.searchsorted(t1, th, 'left').astype(np.int64)
    i1 = np.searchsorted(t1, th + TFS[p['TF']], 'left').astype(np.int64)
    o1, h1, l1, c1 = (np.ascontiguousarray(m1[kk].to_numpy(np.float64)) for kk in OHLC)
    tr = engine(buy.astype(np.int64), sell.astype(np.int64), slL, slS, tpL, tpS,
                p['FLIP'], p['PROT'], p['ORD'], p['MAXBARS'], i0, i1, o1, h1, l1, c1, t1)
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['mins'] = df.texit - df.tent
    df['px'] = df.fill.abs()
    df['riscoRel'] = df.risk / df.px
    df['rrmult'] = df.tpdist / df.risk
    yrs_t = df.mins / (365.25 * 1440)
    df['costR'] = (2 * CUSTO[name] + FUND.get(name, 5.0) / 100 * yrs_t * df.side) / df.riscoRel
    df['net'] = df.R - df.costR
    df['costR_pine'] = 2 * 5e-4 / df.riscoRel
    df['net_pine'] = df.R - df.costR_pine
    if ctrl:
        rng = np.random.default_rng(seed)
        lo = int(max(p['SLOW'] * 3, 150))
        pool = np.arange(lo, len(i0) - 2)
        pool = pool[i1[pool] > i0[pool]]
        starts = rng.choice(pool, len(df) * NR).astype(np.int64)
        db = np.maximum(df.barras.to_numpy().astype(np.int64), 1)
        rrm = np.nan_to_num(df.rrmult.to_numpy(), nan=1.0)
        cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                     np.repeat(df.riscoRel.to_numpy(), NR), np.repeat(rrm, NR),
                     np.repeat(db, NR), i0, i1, o1, h1, l1, c1, t1, p['PROT'], p['ORD'])
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
    pd.set_option('display.width', 320); pd.set_option('display.max_columns', 40)
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
        P('\n---------- defaults do Pine (1h; k<20 e rsi<30 e AO subindo; stop low-ATR, alvo close+ATR) ----------')
        P('-- parametros:', {k: v for k, v in BASE.items()})
        df = run_asset(name, m1, BASE, ctrl=True)
        df.to_csv(os.path.join(D, 'scripts', f'study_serdar_{name}_trades.csv'), index=False)
        A = build(name, m1, BASE)
        ao = A['ao']; pao = np.concatenate([[np.nan], ao[:-1]])
        okk = ~np.isnan(A['atr']) & ~np.isnan(A['k']) & ~np.isnan(A['rsi']) & ~np.isnan(pao)
        nb = int((okk & (A['k'] < 20) & (A['rsi'] < 30) & (ao > pao)).sum())
        ns = int((okk & (A['k'] > 80) & (A['rsi'] > 70) & (ao < pao)).sum())
        P(f'barras do TF {BASE["TF"]}: {len(A["c"])}; sinais crus: long {nb}, short {ns} -> trades '
          f'efetivos {len(df)} (o resto cai por ja estar posicionado)')
        P(f'quanto cada condicao filtra (barras validas={int(okk.sum())}): k<20 '
          f'{int((okk & (A["k"] < 20)).sum())}, rsi<30 {int((okk & (A["rsi"] < 30)).sum())}, '
          f'AO subindo {int((okk & (ao > pao)).sum())}, k<20 & rsi<30 '
          f'{int((okk & (A["k"] < 20) & (A["rsi"] < 30)).sum())}')
        tab = {'todos': summ(df, yrs), 'long': summ(df[df.side == 1], yrs),
               'short': summ(df[df.side == -1], yrs)}
        cut = df.tent.quantile(0.7) if len(df) else 0
        tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7)
        tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
        P(pd.DataFrame(tab).T.round(3).to_string())
        if len(df):
            P(f'retorno em % do capital a 1% de risco/trade: {df.net.sum() / yrs:+.1f}%/ano '
              f'(vs buy&hold {bh * 100:+.1f}%/ano), exposicao {tab["todos"]["expo"] * 100:.1f}% do tempo')
            P(f'com os 0,05%/perna de um cenario tipico de corretora: R_liq '
              f'{df.net_pine.mean():+.3f} ({df.net_pine.sum() / yrs:+.1f} R/ano)')
            P(f'RR efetivo mediano {df.rrmult.median():.3f} -- o alvo dista 1 ATR do close e o stop '
              f'(close-low)+1 ATR, logo o payoff e assimetrico CONTRA por construcao')
            P(f'taxa de acerto necessaria para empatar nesse RR: '
              f'{1 / (1 + df.rrmult.median()):.3f}; observada (liquida) {(df.net > 0).mean():.3f}')
            d = df.R - df.ctrlR
            P(f'controle (entrada em barra aleatoria, mesmo lado/risco/alvo em R/duracao): R bruto '
              f'medio {df.ctrlR.mean():+.3f} vs estrategia {df.R.mean():+.3f}; diferenca '
              f'{d.mean():+.3f} (t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
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
        for v in (dict(ORD=1), dict(PROT=0), dict(FLIP=0), dict(SHORT=0), dict(LONG=0),
                  dict(KLO=25.0, KHI=75.0), dict(KLO=30.0, KHI=70.0),
                  dict(RLO=35.0, RHI=65.0), dict(RLO=40.0, RHI=60.0),
                  dict(RNR=1.0), dict(RNR=2.0), dict(RNR=3.0), dict(ATRM=2.0), dict(ATRM=0.5),
                  dict(MAXBARS=24), dict(TF='15min'), dict(TF='4h'), dict(TF='1D')):
            s = summ(run_asset(name, m1, dict(BASE, **v)), yrs)
            P(f'   {str(v):<32} n={s["n"]:<5} acerto {s.get("acerto", 0):.3f} '
              f'rr {s.get("rr", 0):.2f} R_bruto {s.get("R_bruto", 0):+.3f} '
              f'R_liq {s.get("R_liq", 0):+.3f} PF {s.get("PF", 0):.2f} R_ano {s.get("R_ano", 0):+.1f}')
        for TF, THR, RNR, ATRM, LS in itertools.product(
                ['15min', '30min', '1h', '4h', '1D'],
                [(20.0, 30.0), (25.0, 35.0), (30.0, 40.0), (35.0, 45.0)],
                [0.0, 1.0, 2.0, 3.0], [0.5, 1.0, 2.0], ['both', 'long', 'short']):
            p = dict(BASE, TF=TF, KLO=THR[0], KHI=100 - THR[0], RLO=THR[1], RHI=100 - THR[1],
                     RNR=RNR, ATRM=ATRM, LONG=int(LS != 'short'), SHORT=int(LS != 'long'))
            s = summ(run_asset(name, m1, p), yrs)
            s.update(ativo=name, TF=TF, THR=f'k{THR[0]:.0f}/r{THR[1]:.0f}', RNR=RNR, ATRM=ATRM, LS=LS)
            grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        cols = ['TF', 'THR', 'RNR', 'ATRM', 'LS', 'n', 'por_ano', 'acerto', 'risco_bp', 'rr',
                'R_bruto', 'custo_R', 'R_liq', 'PF', 'R_ano', 'expo']
        P('\n-- grade de robustez (TF x limiares x alvo x ATR do stop x lado):')
        P(g[cols].round(3).to_string(index=False))
        P(f'combinacoes com R_liq > 0: {(g.R_liq > 0).sum()}/{len(g)}; '
          f'com R_bruto > 0: {(g.R_bruto > 0).sum()}/{len(g)}; '
          f'com n >= 50 e R_liq > 0: {((g.R_liq > 0) & (g.n >= 50)).sum()}/{(g.n >= 50).sum()}')
        P('-- top 15 por R_ano liquido (n >= 30):')
        P(g[g.n >= 30].nlargest(15, 'R_ano')[cols].round(3).to_string(index=False))
        for col in ('TF', 'THR', 'RNR', 'ATRM', 'LS'):
            P(f'-- media por {col}:')
            P(g.groupby(col)[['n', 'acerto', 'rr', 'R_bruto', 'custo_R', 'R_liq', 'R_ano']]
              .mean().round(3).to_string())
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_serdar_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['TF', 'THR', 'RNR', 'ATRM', 'LS'],
                             values=['n', 'R_bruto', 'R_liq'],
                             aggfunc={'n': 'min', 'R_bruto': 'mean', 'R_liq': 'mean'})
        P(piv[piv.n >= 20].sort_values('R_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_serdar.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
