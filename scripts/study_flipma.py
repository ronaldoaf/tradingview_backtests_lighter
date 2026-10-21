"""Hull Suite Strategy (Q9OQye4C, InSilico/DashTrader) e Backtest single EMA cross
(j9rq1wQq, che-trader) - traducao fiel do Pine (fontes abertas baixadas do pine-facade) e teste
em ouro M1 da Dukascopy, com OOS em US100/BTC/WTI/ETH.

AS DUAS SAO A MESMA FAMILIA: sempre-no-mercado, invertendo a posicao num sinal de linha de
tendencia, sem stop, sem alvo, sem filtro.

  Hull Suite ("hull"):
      HULL = HMA/EHMA/THMA(close, length=55)       (modeSwitch: Hma / Ehma / Thma)
      HMA (_src,_l) = wma(2*wma(_src,_l/2) - wma(_src,_l), round(sqrt(_l)))
      EHMA(_src,_l) = ema(2*ema(_src,_l/2) - ema(_src,_l), round(sqrt(_l)))
      THMA(_src,_l) = wma(wma(_src,_l/3)*3 - wma(_src,_l/2) - wma(_src,_l), _l)  <- chamada com l/2
      if HULL[0] > HULL[2]  -> strategy.entry("buy",  long)
      if HULL[0] < HULL[2]  -> strategy.entry("sell", short)
      strat_dir_input default "long" => strategy.risk.allow_entry_in(long): as ordens de VENDA
      nao abrem short, so FECHAM o long. Esse e o default publicado (DIR='long'); DIR='all'
      testa a versao com short de verdade.

  single EMA cross ("ema"):
      longCondition  = crossover (ema(close,10), ema(close,20))
      shortCondition = crossunder(ema(close,10), ema(close,20))
      strategy.entry("Long"/"Short", when=...) sem direction: sempre-no-mercado nos dois lados.

Como o `if` do Hull roda em TODA barra e strategy.entry com o mesmo id e ignorado estando no
mesmo lado, as duas acabam em "posicao desejada = sinal no fechamento da barra, executada na
ABERTURA da barra seguinte" - que e exatamente o que esta implementado aqui. Nao ha nada
intrabarra para resolver (sem stop/alvo), entao o teste roda no TF do grafico.

Medidas: retorno por trade em % do notional (nao existe R, nao ha stop), retorno composto
anualizado com 1x de notional, e comparacao com buy&hold do proprio ativo no mesmo periodo.
Custo: CUSTO[ativo] por perna (spread medido na Lighter) + funding FUND[ativo] pro-rata do tempo
(o long paga, o short recebe). Reporto tambem o cenario sem custo (bruto).
Controle: para cada trade, 20 trades sorteados com o MESMO lado e a MESMA duracao em barras,
comecando em barras aleatorias -> isola o que a linha de tendencia acrescenta sobre entrar no
acaso com o mesmo perfil de exposicao.

uso: python study_flipma.py [xau us100 btc wti eth ...]
"""
import os, sys, glob, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_commas import (CUSTO, FUND, OHLC, load_m1, minutes, resample,
                          ema, sma, wma, roll_max, roll_min)

TFS = {'15min': 15, '30min': 30, '1h': 60, '4h': 240, '1D': 1440, '1W': 10080}
BASE_HULL = dict(STRAT='hull', TF='4h', MODE='Hma', LEN=55, DIR='long', LEN2=20)
BASE_EMA = dict(STRAT='ema', TF='4h', MODE='Hma', LEN=10, DIR='all', LEN2=20)


# ---------------------------------------------------------------- indicadores do Hull
def _wma(x, n):
    return wma(np.ascontiguousarray(x.astype(np.float64)), max(int(n), 1))


def _ema(x, n):
    return ema(np.ascontiguousarray(x.astype(np.float64)), max(int(n), 1))


def hull(c, mode, length):
    """Fiel ao Pine: as divisoes de length sao em float (Pine v4 nao trunca), round(sqrt(l))."""
    l = float(length)
    if mode == 'Hma':
        s = int(round(np.sqrt(l)))
        return _wma(2 * _wma(c, round(l / 2)) - _wma(c, round(l)), s)
    if mode == 'Ehma':
        s = int(round(np.sqrt(l)))
        return _ema(2 * _ema(c, round(l / 2)) - _ema(c, round(l)), s)
    if mode == 'Thma':
        l = l / 2.0                                   # Mode() chama THMA(src, len/2)
        return _wma(_wma(c, round(l / 3)) * 3 - _wma(c, round(l / 2)) - _wma(c, round(l)), round(l))
    raise ValueError(mode)


# ---------------------------------------------------------------- motor sempre-no-mercado
@njit(cache=True)
def engine(want, o, c, t, n_ok):
    """want[j] = posicao desejada decidida no FECHAMENTO da barra j (-1/0/+1);
    a mudanca e executada a mercado na ABERTURA da barra j+1.

    out: tent texit fill exitpx side barras
    """
    n = len(o)
    out = np.zeros((n + 4, 6))
    q = 0
    pos = 0; fill = 0.0; tent = 0.0; ebar = -1
    for j in range(1, n):
        tgt = want[j - 1]
        if tgt != pos:
            px = o[j]
            if pos != 0:
                out[q, 0] = tent; out[q, 1] = t[j]; out[q, 2] = fill; out[q, 3] = px
                out[q, 4] = pos; out[q, 5] = j - ebar
                q += 1
            pos = 0
            if tgt != 0 and j >= n_ok:
                pos = tgt; fill = px; tent = t[j]; ebar = j
    if pos != 0:
        out[q, 0] = tent; out[q, 1] = t[n - 1]; out[q, 2] = fill; out[q, 3] = c[n - 1]
        out[q, 4] = pos; out[q, 5] = n - 1 - ebar
        q += 1
    return out[:q]


@njit(cache=True)
def control(starts, side, durbars, o, c):
    """mesmo lado e mesma duracao em barras, comecando numa barra sorteada."""
    n = len(o); m = len(starts); out = np.zeros(m)
    for z in range(m):
        j0 = starts[z]
        j1 = j0 + durbars[z]
        if j1 >= n: j1 = n - 1
        px = o[j0]
        ex = o[j1] if j1 > j0 else c[j1]
        out[z] = (ex - px) / px * side[z]
    return out


# ---------------------------------------------------------------- montagem
_CACHE = {}
COLS = ['tent', 'texit', 'fill', 'exitpx', 'side', 'barras']


def build(name, m1, p):
    key = (name, p['TF'])
    if key in _CACHE:
        htf = _CACHE[key]
    else:
        htf = resample(m1, p['TF'])
        if len(_CACHE) > 8: _CACHE.clear()
        _CACHE[key] = htf
    o, h, l, c = (np.ascontiguousarray(htf[k].to_numpy(np.float64)) for k in OHLC)
    if p['STRAT'] == 'hull':
        H = hull(c, p['MODE'], p['LEN'])
        H2 = np.concatenate([[np.nan, np.nan], H[:-2]])          # HULL[2]
        up = H > H2; dn = H < H2
        ok = ~np.isnan(H) & ~np.isnan(H2)
        want = np.where(ok & up, 1, np.where(ok & dn, -1, 0)).astype(np.int64)
        if p['DIR'] == 'long':                                   # allow_entry_in(long): short vira flat
            want = np.maximum(want, 0)
        elif p['DIR'] == 'short':
            want = np.minimum(want, 0)
    else:
        e1 = _ema(c, p['LEN']); e2 = _ema(c, p['LEN2'])
        pe1 = np.concatenate([[np.nan], e1[:-1]]); pe2 = np.concatenate([[np.nan], e2[:-1]])
        xup = (e1 > e2) & (pe1 <= pe2); xdn = (e1 < e2) & (pe1 >= pe2)
        want = np.zeros(len(c), np.int64)
        cur = 0
        for j in range(len(c)):
            if xup[j]: cur = 1
            elif xdn[j]: cur = -1
            want[j] = cur
        if p['DIR'] == 'long': want = np.maximum(want, 0)
        elif p['DIR'] == 'short': want = np.minimum(want, 0)
        ok = ~np.isnan(e2)
        want = np.where(ok, want, 0)
    n_ok = int(np.argmax(want != 0)) if np.any(want != 0) else len(c)
    return htf, o, c, minutes(htf.index).astype(np.int64), want, n_ok


def run_asset(name, m1, p, ctrl=False, seed=1, NR=20):
    htf, o, c, t, want, n_ok = build(name, m1, p)
    tr = engine(want, o, c, t, n_ok)
    df = pd.DataFrame(tr, columns=COLS)
    if len(df) == 0: return df
    df['mins'] = df.texit - df.tent
    df['ret'] = (df.exitpx - df.fill) / df.fill * df.side          # bruto, em % do notional
    yrs_t = df.mins / (365.25 * 1440)
    df['cost'] = 2 * CUSTO[name] + FUND.get(name, 5.0) / 100 * yrs_t * df.side
    df['net'] = df.ret - df.cost
    if ctrl:
        rng = np.random.default_rng(seed)
        lo = max(n_ok, 10)
        pool = np.arange(lo, len(o) - 2)
        if len(pool) > 10:
            starts = rng.choice(pool, len(df) * NR).astype(np.int64)
            db = np.maximum(df.barras.to_numpy().astype(np.int64), 1)
            cr = control(starts, np.repeat(df.side.to_numpy().astype(np.int64), NR),
                         np.repeat(db, NR), o, c)
            df['ctrlRet'] = cr.reshape(-1, NR).mean(1)
    return df


def summ(df, yrs):
    if len(df) == 0: return dict(n=0)
    eq = np.prod(1 + df.net.to_numpy())
    eqb = np.prod(1 + df.ret.to_numpy())
    w = df.net[df.net > 0].sum(); ls = -df.net[df.net < 0].sum()
    return dict(n=len(df), por_ano=len(df) / yrs, acerto=(df.net > 0).mean(),
                ret_bruto=df.ret.mean() * 100, custo=df.cost.mean() * 100,
                ret_liq=df.net.mean() * 100, PF=w / ls if ls > 0 else np.nan,
                cagr=(eq ** (1 / yrs) - 1) * 100 if eq > 0 else -100.0,
                cagr_bruto=(eqb ** (1 / yrs) - 1) * 100 if eqb > 0 else -100.0,
                horas=np.nanmedian(df.mins) / 60, expo=df.mins.sum() / (yrs * 365.25 * 1440))


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
        for tag, BASE, desc in [
                ('HULL', BASE_HULL, 'Hull Suite: HMA(close,55), long quando HULL>HULL[2], '
                                    'strat_dir=long (venda so fecha)'),
                ('EMA', BASE_EMA, 'single EMA cross: EMA(10) x EMA(20), sempre-no-mercado nos dois lados')]:
            P(f'\n---------- defaults do Pine - {tag} ----------')
            P(f'-- {desc}')
            P('-- TF do grafico aqui: 4h (o Pine nao fixa TF; a grade abaixo varre 15m..1W)')
            df = run_asset(name, m1, BASE, ctrl=True)
            df.to_csv(os.path.join(D, 'scripts', f'study_flipma_{tag.lower()}_{name}_trades.csv'),
                      index=False)
            tab = {'todos': summ(df, yrs), 'long': summ(df[df.side == 1], yrs),
                   'short': summ(df[df.side == -1], yrs)}
            cut = df.tent.quantile(0.7) if len(df) else 0
            tab['IS_70%'] = summ(df[df.tent <= cut], yrs * 0.7)
            tab['OOS_30%'] = summ(df[df.tent > cut], yrs * 0.3)
            P(pd.DataFrame(tab).T.round(3).to_string())
            if len(df):
                s = tab['todos']
                P(f'retorno composto 1x: {s["cagr"]:+.1f}%/ano liquido ({s["cagr_bruto"]:+.1f}% bruto) '
                  f'vs buy&hold {bh * 100:+.1f}%/ano; exposicao {s["expo"] * 100:.1f}% do tempo')
                if 'ctrlRet' in df:
                    d = df.ret - df.ctrlRet
                    P(f'controle (mesma barra? nao - barra aleatoria, mesmo lado e mesma duracao): '
                      f'bruto medio {df.ctrlRet.mean() * 100:+.3f}% vs estrategia {df.ret.mean() * 100:+.3f}%; '
                      f'dif {d.mean() * 100:+.3f}% (t={d.mean() / d.std() * np.sqrt(len(df)):.2f})')
                    for lbl, sub in [('long', df[df.side == 1]), ('short', df[df.side == -1])]:
                        if len(sub) > 2:
                            ds = sub.ret - sub.ctrlRet
                            P(f'  controle {lbl:<6}: {sub.ctrlRet.mean() * 100:+.3f}% vs '
                              f'{sub.ret.mean() * 100:+.3f}%; dif {ds.mean() * 100:+.3f}% '
                              f'(t={ds.mean() / ds.std() * np.sqrt(len(sub)):.2f})')
                sd = df.net.sort_values()
                P(f'pior trade {sd.iloc[0] * 100:+.2f}%; 5 melhores somam {sd.iloc[-5:].sum() * 100:+.1f}% '
                  f'de {df.net.sum() * 100:+.1f}% somados; mediana {df.net.median() * 100:+.3f}%')
                yr = pd.to_datetime(df.tent * 60, unit='s', utc=True).dt.year
                P('por ano (n, ret liq medio %, soma %):')
                P((df.assign(pct=df.net * 100).groupby(yr).pct
                   .agg(['count', 'mean', 'sum'])).round(2).T.to_string())
            P(f'\n-- variantes {tag} (uma mudanca por vez):')
            vs = ([dict(DIR='all'), dict(DIR='short'), dict(MODE='Ehma'), dict(MODE='Thma'),
                   dict(LEN=21), dict(LEN=100), dict(LEN=180), dict(LEN=200), dict(TF='1D'),
                   dict(TF='1h'), dict(TF='1W')] if tag == 'HULL' else
                  [dict(DIR='long'), dict(DIR='short'), dict(LEN=9, LEN2=21),
                   dict(LEN=20, LEN2=50), dict(LEN=50, LEN2=200), dict(TF='1D'), dict(TF='1h'),
                   dict(TF='15min'), dict(TF='1W')])
            for v in vs:
                s = summ(run_asset(name, m1, dict(BASE, **v)), yrs)
                P(f'   {str(v):<34} n={s["n"]:<5} acerto {s.get("acerto", 0):.3f} '
                  f'bruto {s.get("ret_bruto", 0):+.3f}% liq {s.get("ret_liq", 0):+.3f}% '
                  f'PF {s.get("PF", 0):.2f} CAGR {s.get("cagr", -100):+.1f}%')
        # ---------------- grade de robustez conjunta
        for TF, DIR in itertools.product(['15min', '30min', '1h', '4h', '1D', '1W'],
                                         ['long', 'short', 'all']):
            for MODE, LEN in itertools.product(['Hma', 'Ehma', 'Thma'], [21, 55, 100, 180, 200]):
                p = dict(BASE_HULL, TF=TF, DIR=DIR, MODE=MODE, LEN=LEN)
                s = summ(run_asset(name, m1, p), yrs)
                s.update(ativo=name, fam='hull', TF=TF, DIR=DIR, var=MODE, LENs=str(LEN))
                grid_rows.append(s)
            for L1, L2 in [(5, 10), (10, 20), (9, 21), (20, 50), (50, 200)]:
                p = dict(BASE_EMA, TF=TF, DIR=DIR, LEN=L1, LEN2=L2)
                s = summ(run_asset(name, m1, p), yrs)
                s.update(ativo=name, fam='ema', TF=TF, DIR=DIR, var='EMAx', LENs=f'{L1}/{L2}')
                grid_rows.append(s)
        g = pd.DataFrame([r for r in grid_rows if r['ativo'] == name])
        cols = ['fam', 'TF', 'DIR', 'var', 'LENs', 'n', 'por_ano', 'acerto', 'ret_bruto', 'custo',
                'ret_liq', 'PF', 'cagr', 'cagr_bruto', 'expo']
        P('\n-- grade de robustez (familia x TF x direcao x variacao x comprimentos):')
        P(g[cols].round(3).to_string(index=False))
        P(f'combinacoes com ret_liq > 0: {(g.ret_liq > 0).sum()}/{len(g)}; '
          f'com ret_bruto > 0: {(g.ret_bruto > 0).sum()}/{len(g)}; '
          f'que batem o buy&hold no composto liquido: {(g.cagr > bh * 100).sum()}/{len(g)}')
        P('-- top 15 por CAGR liquido:')
        P(g.nlargest(15, 'cagr')[cols].round(3).to_string(index=False))
        for col in ('fam', 'TF', 'DIR', 'var', 'LENs'):
            P(f'-- media por {col}:')
            P(g.groupby(col)[['n', 'acerto', 'ret_bruto', 'custo', 'ret_liq', 'cagr']]
              .mean().round(3).to_string())
    gg = pd.DataFrame(grid_rows)
    gg.to_csv(os.path.join(D, 'scripts', 'study_flipma_grid.csv'), index=False)
    if len(names) > 1:
        P('\n== por celula, media entre ativos (so celulas com n>=20 em todos):')
        piv = gg.pivot_table(index=['fam', 'TF', 'DIR', 'var', 'LENs'],
                             values=['n', 'ret_bruto', 'ret_liq', 'cagr'],
                             aggfunc={'n': 'min', 'ret_bruto': 'mean', 'ret_liq': 'mean',
                                      'cagr': 'mean'})
        P(piv[piv.n >= 20].sort_values('ret_liq', ascending=False).round(3).to_string())
    with open(os.path.join(D, 'scripts', 'study_flipma.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
