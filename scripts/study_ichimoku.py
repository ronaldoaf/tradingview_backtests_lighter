"""Ichimoku + Daily-Candle_X + HULL-MA_X + MacD - SeaSide420 / TradingView (RJBjyl2W, Pine v4
aberto, PUB;3177) - traducao fiel e teste em ouro com M1 da Dukascopy.

Regras (defaults do Pine; TODAS as entradas usam o preco de ABERTURA como fonte):
  hma1 = ta.hma(open, 14)            hma2 = ta.hma(open[1], 14)   -> hma2 = hma1 defasado 1 barra,
         logo "hma1 > hma2" e apenas "a HullMA esta SUBINDO" (nao e cruzamento de duas medias).
  D1 = security(tickerid, "D", open, lookahead_off)   D2 = o mesmo de open[1]
         com lookahead_off, dentro do dia em formacao o Pine devolve o ultimo dia FECHADO, logo
         D1 > D2 = "a abertura diaria de ontem foi maior que a de anteontem" (filtro de 1 bit/dia).
  Ichimoku: donchian(n) = avg(lowest(low,n), highest(high,n));
         leadLine1 = avg(donchian(9), donchian(26)); leadLine2 = donchian(52).
         A CONDICAO usa os valores NAO deslocados (o displacement=26 so entra nos plots), portanto
         nao ha repintura nem lookahead - mas tambem nao e a nuvem do Ichimoku de verdade.
  MACD custom = ta.hma(open,12) - ta.hma(open,26);  aMACD = ta.hma(MACD, 9)   (HMA, nao EMA)
  long  = hma1>hma2 E D1>D2 E open>hma2 E leadLine1>leadLine2 E MACD>aMACD
  short = espelhado.
  SAIDAS: nao existem (os blocos de stop/alvo estao COMENTADOS na fonte). pyramiding=0 ->
  o sistema fica SEMPRE NO MERCADO, invertendo quando o lado oposto aparece. Mesma familia do
  Hull Suite ja reprovada ([[flipma-study]]).
  O proprio script declara commission_value=0,25% POR PERNA + 1 tick de slippage; reporto tambem
  esse cenario, mas a conta principal usa o spread real da Lighter (CUSTO[ativo]).

Execucao: sinal no fechamento, ordem a mercado na ABERTURA da barra seguinte (SHIFT=1, fiel).
Como todas as fontes sao a ABERTURA da barra, a condicao ja esta decidida no inicio da barra;
testo tambem SHIFT=0 (entrar na abertura da propria barra do sinal), que e legitimo aqui e e o
cenario mais favoravel possivel para a estrategia.

Medicao: retorno sobre o nocional (1x) com percent_of_equity=100, custo por perna (inverter = 2
pernas) e funding pro-rata. Comparacoes: buy & hold do mesmo periodo e controle aleatorio com o
MESMO lado e a MESMA duracao de cada trade.

uso: python study_ichimoku.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

TFS = ['15min', '30min', '1h', '4h', '1D']
BASE = dict(PERIOD=14, CONV=9, BASEP=26, LAG=52, MFAST=12, MSLOW=26, MSIG=9,
            LONG=1, SHORT=1, SHIFT=1, DAILY=1, ICHI=1, MACD=1, HULL=1)


def donchian(h, l, n):
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    return (hi + lo) / 2


def daily_prev_open(df):
    """security(..., 'D', open, lookahead_off) e o mesmo de open[1]: abertura do ultimo dia
    FECHADO e do dia anterior a ele, propagadas barra a barra."""
    s = pd.Series(df.open.to_numpy(float), index=df.index)
    dop = s.resample('1D').first().dropna()
    d1 = dop.shift(1); d2 = dop.shift(2)
    key = df.index.floor('1D')
    return d1.reindex(key).to_numpy(), d2.reindex(key).to_numpy()


def signals(df, p):
    o = df.open.to_numpy(float)
    h = df.high.to_numpy(float); l = df.low.to_numpy(float)
    hma1 = T.hma(o, p['PERIOD'])
    # hma(open[1], n) = hma(open, n) defasada 1 barra (a WMA e linear e invariante ao deslocamento)
    hma2 = np.concatenate([[np.nan], hma1[:-1]])
    d1, d2 = daily_prev_open(df)
    lead1 = (donchian(h, l, p['CONV']) + donchian(h, l, p['BASEP'])) / 2
    lead2 = donchian(h, l, p['LAG'])
    macd = T.hma(o, p['MFAST']) - T.hma(o, p['MSLOW'])
    amacd = T.hma(macd, p['MSIG'])
    hull_up = (hma1 > hma2) & (o > hma2) if p['HULL'] else np.ones(len(o), bool)
    hull_dn = (hma1 < hma2) & (o < hma2) if p['HULL'] else np.ones(len(o), bool)
    day_up = (d1 > d2) if p['DAILY'] else np.ones(len(o), bool)
    day_dn = (d1 < d2) if p['DAILY'] else np.ones(len(o), bool)
    ichi_up = (lead1 > lead2) if p['ICHI'] else np.ones(len(o), bool)
    ichi_dn = (lead1 < lead2) if p['ICHI'] else np.ones(len(o), bool)
    mac_up = (macd > amacd) if p['MACD'] else np.ones(len(o), bool)
    mac_dn = (macd < amacd) if p['MACD'] else np.ones(len(o), bool)
    ok = ~np.isnan(hma1) & ~np.isnan(hma2) & ~np.isnan(lead2) & ~np.isnan(amacd) & ~np.isnan(d2)
    L = hull_up & day_up & ichi_up & mac_up & ok
    S = hull_dn & day_dn & ichi_dn & mac_dn & ok
    return L, S


def run(name, p, df, verbose=True, tag=None, comm=None):
    L, S = signals(df, p)
    tr_raw = T.engine_bars(df, L, S, long_ok=bool(p['LONG']), short_ok=bool(p['SHORT']),
                           flat_on_opp=not (p['LONG'] and p['SHORT']), shift=p['SHIFT'])
    tr = T.book(df, tr_raw, name)
    if comm is not None and len(tr):   # cenario de custo do proprio script (0,25%/perna)
        tr = tr.assign(ret_sf=tr.bruto - 2 * comm, ret=tr.bruto - 2 * comm - tr.fund)
    o = T.summarize(df, tr, name)
    if o and verbose:
        T.line(tag or f"P{p['PERIOD']} {p['TF']} L{p['LONG']}S{p['SHORT']} sh{p['SHIFT']}", o)
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M barras)")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        print("\n-- defaults (Period 14) por timeframe, fiel (entrada na abertura seguinte)")
        for tf in TFS:
            p = dict(BASE, TF=tf)
            o, _ = run(name, p, cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'PERIOD', 'LONG', 'SHORT', 'SHIFT')}))
        print("\n-- idem com o custo declarado no proprio script (0,25%/perna)")
        for tf in TFS:
            p = dict(BASE, TF=tf)
            o, _ = run(name, p, cache[tf], comm=0.0025, tag=f"P14 {tf} custo 0,25%/perna")
            if o: rows.append(dict(o, TF=tf, PERIOD=14, LONG=1, SHORT=1, SHIFT=1))
        print("\n-- entrada na abertura da propria barra do sinal (SHIFT=0, cenario otimista)")
        for tf in TFS:
            p = dict(BASE, TF=tf, SHIFT=0)
            o, _ = run(name, p, cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'PERIOD', 'LONG', 'SHORT', 'SHIFT')}))
        print("\n-- lados separados (um lado so; sinal contrario apenas zera)")
        for tf, (lg, sh) in itertools.product(TFS, ((1, 0), (0, 1))):
            p = dict(BASE, TF=tf, LONG=lg, SHORT=sh)
            o, _ = run(name, p, cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'PERIOD', 'LONG', 'SHORT', 'SHIFT')}))
        print("\n-- ablacao dos quatro filtros (1h e 4h): o que cada bloco acrescenta")
        for tf in ('1h', '4h'):
            for nm, kw in (('so Hull', dict(DAILY=0, ICHI=0, MACD=0)),
                           ('so diario', dict(HULL=0, ICHI=0, MACD=0)),
                           ('so Ichimoku', dict(HULL=0, DAILY=0, MACD=0)),
                           ('so MACD-Hull', dict(HULL=0, DAILY=0, ICHI=0)),
                           ('sem diario', dict(DAILY=0)), ('sem Ichimoku', dict(ICHI=0)),
                           ('sem MACD', dict(MACD=0))):
                o, _ = run(name, dict(BASE, TF=tf, **kw), cache[tf], tag=f'{tf} {nm}')
        print("\n-- grade Period x TF")
        for tf, per in itertools.product(TFS, (7, 14, 21, 28, 56, 100)):
            p = dict(BASE, TF=tf, PERIOD=per)
            o, _ = run(name, p, cache[tf], verbose=False)
            if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'PERIOD', 'LONG', 'SHORT', 'SHIFT')}))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_ichimoku_{name}_grid.csv'), index=False)
        print(f"\n  grade {name}: {len(g)} celulas | liq>0: {(g.bp_liq > 0).sum()} | "
              f"liq>0 e t>1: {((g.bp_liq > 0) & (g.t > 1)).sum()} | "
              f"CAGR>B&H: {(g.cagr > g.bh).sum()}")
        print(g.sort_values('bp_liq', ascending=False).head(12)[
            ['TF', 'PERIOD', 'LONG', 'SHORT', 'SHIFT', 'trades', 'por_ano', 'bp_bruto', 'bp_liq',
             'win', 'cagr', 'bh', 'sharpe', 'expo', 'ctl_bp', 't']].to_string(
            index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
