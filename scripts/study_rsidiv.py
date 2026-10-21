"""RSI Divergence Indicator strategy - TradingView qSLcZSyw (Pine v4 aberto,
PUB;wUU7CXCaw0qQ1hF3fjTVkjcXmCTY12oK) - traducao fiel e teste em ouro com M1 da Dukascopy.

E o indicador de divergencia padrao do TradingView (RSI + pivots) embrulhado numa estrategia
so-COMPRA. Os comentarios no topo da fonte anunciam "win rate 87,21%, profit factor 7,059" em
GOOGL - numeros de uma acao em tendencia de alta secular, sem custo e sem stop.

Regras (defaults do Pine):
  osc = ta.rsi(close, 9).  Pivots de osc com lbL=1 a esquerda e lbR=3 a direita, portanto
  confirmados 3 barras DEPOIS do fundo/topo (sem repintura: o sinal sai na barra da confirmacao).
  _inRange: a divergencia so vale se o pivo anterior estiver entre 5 e 60 barras atras.
  bullCond        = fundo de RSI mais ALTO  e fundo de preco mais BAIXO (divergencia classica)
  hiddenBullCond  = fundo de RSI mais BAIXO e fundo de preco mais ALTO  (oculta; LIGADA por default)
  longCondition   = bullCond OU hiddenBullCond  -> as duas sao usadas ao mesmo tempo, e elas sao
                    quase complementares: juntas disparam em praticamente TODO pivo de RSI, o que
                    esvazia a ideia de "divergencia" (testo os dois gatilhos separados na ablacao).
  bearCond        = topo de RSI mais BAIXO e topo de preco mais ALTO (plotHiddenBear=false)
  saida (sl_type NONE, default): ta.crossover(osc, 80) OU bearCond
  pyramiding=2, default_qty 2 -> ate duas entradas empilhadas; a saida fecha tudo.
  Variantes de stop do proprio script: PERC = 5% abaixo do min; ATR = 5 x ATR(14) abaixo do min,
  trilha monotonica atualizada no FECHAMENTO, saida em ta.crossunder(close, trilha).

BUG NA FONTE: o input atrMultiplier (3,5) NUNCA e usado. O stop por ATR usa
"stopLoss * atr(atrLength)" = 5 x ATR, isto e, o campo "Stop Loss%" (pensado em porcentagem) e
reaproveitado como multiplicador de ATR. Quem trocar o stop de 5% para, digamos, 2% esta tambem
trocando a trilha de 5xATR para 2xATR sem perceber.

Execucao: sinal no fechamento, ordem a mercado na ABERTURA da barra seguinte (fiel ao Pine com
calc_on_every_tick=false). Custo CUSTO[ativo] por perna + funding FUND[ativo] pro-rata.
Medicao em retorno sobre o nocional (1x). Controle: para cada trade, 20 entradas a mercado em
barras sorteadas com a MESMA duracao -> isola a divergencia do acaso.

uso: python study_rsidiv.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

TFS = ['15min', '30min', '1h', '4h', '1D']
BASE = dict(LEN=9, LBR=3, LBL=1, TPLEVEL=80.0, RANGEUP=60, RANGEDN=5,
            BULL=1, HBULL=1, BEAR=1, HBEAR=0, SLTYPE='NONE', SLPCT=5.0, ATRLEN=14, PYR=1)


def signals(df, p):
    c = df.close.to_numpy(float); h = df.high.to_numpy(float); l = df.low.to_numpy(float)
    osc = T.rsi_wilder(c, p['LEN'])
    lbR, lbL = p['LBR'], p['LBL']
    pl = T.pivotlow(osc, lbL, lbR)
    ph = T.pivothigh(osc, lbL, lbR)
    oscR = np.concatenate([np.full(lbR, np.nan), osc[:-lbR]]) if lbR else osc
    lowR = np.concatenate([np.full(lbR, np.nan), l[:-lbR]]) if lbR else l
    highR = np.concatenate([np.full(lbR, np.nan), h[:-lbR]]) if lbR else h

    def inrange(cond):
        b = T.barssince(np.concatenate([[False], cond[:-1]]))  # _inRange(plFound[1])
        return (b >= p['RANGEDN']) & (b <= p['RANGEUP'])

    vw_osc_l = T.valuewhen_prev(pl, oscR); vw_low = T.valuewhen_prev(pl, lowR)
    vw_osc_h = T.valuewhen_prev(ph, oscR); vw_high = T.valuewhen_prev(ph, highR)
    with np.errstate(invalid='ignore'):
        bull = pl & (oscR > vw_osc_l) & inrange(pl) & (lowR < vw_low)
        hbull = pl & (oscR < vw_osc_l) & inrange(pl) & (lowR > vw_low)
        bear = ph & (oscR < vw_osc_h) & inrange(ph) & (highR > vw_high)
        hbear = ph & (oscR > vw_osc_h) & inrange(ph) & (highR < vw_high)
    L = (bull if p['BULL'] else np.zeros(len(c), bool)) | (hbull if p['HBULL'] else np.zeros(len(c), bool))
    X = T.xover(osc, np.full(len(c), p['TPLEVEL']))
    if p['BEAR']: X = X | bear
    if p['HBEAR']: X = X | hbear
    return L & ~np.isnan(oscR), X, (bull, hbull, bear)


def trades_trail(df, L, p):
    """Variantes PERC/ATR: a saida e o crossunder do fechamento com a trilha monotonica
    max(low - sl_val) mantida desde a entrada (atualizada no fechamento de cada barra);
    execucao na abertura da barra seguinte. Fiel ao bug: sl_val do ATR = SLPCT x ATR."""
    c = df.close.to_numpy(float); l = df.low.to_numpy(float); o = df.open.to_numpy(float)
    if p['SLTYPE'] == 'ATR':
        sv = p['SLPCT'] * T.atr_rma(df.high.to_numpy(float), l, c, p['ATRLEN'])
    else:
        sv = c * p['SLPCT'] / 100.0
    n = len(df); tr = []
    units = 0; i0 = None; cost = 0.0; trail = np.nan; prev_close_above = True
    for i in range(n - 1):
        if units > 0:
            lvl = l[i] - sv[i]
            trail = lvl if trail != trail else max(trail, lvl)
            if prev_close_above and c[i] < trail:
                tr.append((i0, i + 1, units, cost / units))
                units = 0; i0 = None; cost = 0.0; trail = np.nan; prev_close_above = True
                continue
            prev_close_above = c[i] >= trail
        if L[i] and units < p['PYR']:
            if units == 0:
                i0 = i + 1; trail = np.nan; prev_close_above = True
            units += 1; cost += o[i + 1]
    return tr


def run(name, p, df, verbose=True, tag=None):
    L, X, _ = signals(df, p)
    if p['SLTYPE'] == 'NONE':
        raw = T.engine_signal_exit(df, L, X, maxunits=p['PYR'])
    else:
        raw = trades_trail(df, L, p)
    tr = T.book(df, raw, name)
    if len(tr):
        tr = tr.assign(d=1.0)
        tr['bruto'] = tr.exit / tr.entry - 1
        tr = T._cost(tr, name, True)
    o = T.summarize(df, tr, name)
    if o and verbose:
        T.line(tag or f"{p['TF']} RSI{p['LEN']} {p['SLTYPE']} pyr{p['PYR']}", o)
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M barras)")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        print("\n-- defaults (RSI 9, pivot 1/3, saida RSI>80 ou divergencia de baixa) por timeframe")
        for tf in TFS:
            p = dict(BASE, TF=tf)
            o, _ = run(name, p, cache[tf])
            if o: rows.append(dict(o, TF=tf, LEN=9, SLTYPE='NONE', PYR=1, gat='bull+oculta'))
        print("\n-- com pyramiding=2 (como o Pine publicado)")
        for tf in TFS:
            p = dict(BASE, TF=tf, PYR=2)
            o, _ = run(name, p, cache[tf])
            if o: rows.append(dict(o, TF=tf, LEN=9, SLTYPE='NONE', PYR=2, gat='bull+oculta'))
        print("\n-- gatilhos separados: divergencia CLASSICA vs OCULTA (so para ver se o sinal diz algo)")
        for tf in TFS:
            for nm, kw in (('classica', dict(BULL=1, HBULL=0)), ('oculta', dict(BULL=0, HBULL=1))):
                o, _ = run(name, dict(BASE, TF=tf, **kw), cache[tf], tag=f'{tf} so {nm}')
                if o: rows.append(dict(o, TF=tf, LEN=9, SLTYPE='NONE', PYR=1, gat=nm))
        print("\n-- variantes de trilha do proprio script (PERC 5% e ATR 5xATR, com o bug do multiplicador)")
        for tf, st in itertools.product(TFS, ('PERC', 'ATR')):
            o, _ = run(name, dict(BASE, TF=tf, SLTYPE=st), cache[tf], tag=f'{tf} trilha {st}')
            if o: rows.append(dict(o, TF=tf, LEN=9, SLTYPE=st, PYR=1, gat='bull+oculta'))
        print("\n-- grade RSI x pivot x nivel de alvo x TF")
        for tf, ln, lbr, lv in itertools.product(TFS, (5, 9, 14), (3, 5, 8), (70.0, 80.0)):
            p = dict(BASE, TF=tf, LEN=ln, LBR=lbr, TPLEVEL=lv)
            o, _ = run(name, p, cache[tf], verbose=False)
            if o: rows.append(dict(o, TF=tf, LEN=ln, LBR=lbr, TPLEVEL=lv, SLTYPE='NONE', PYR=1,
                                   gat='bull+oculta'))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_rsidiv_{name}_grid.csv'), index=False)
        print(f"\n  grade {name}: {len(g)} celulas | liq>0: {(g.bp_liq > 0).sum()} | "
              f"liq>0 e t>1: {((g.bp_liq > 0) & (g.t > 1)).sum()} | "
              f"CAGR>B&H: {(g.cagr > g.bh).sum()}")
        cols = [c for c in ['TF', 'LEN', 'LBR', 'TPLEVEL', 'SLTYPE', 'PYR', 'gat', 'trades',
                            'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh', 'sharpe',
                            'expo', 'ctl_bp', 't'] if c in g.columns]
        print(g.sort_values('bp_liq', ascending=False).head(12)[cols].to_string(
            index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
