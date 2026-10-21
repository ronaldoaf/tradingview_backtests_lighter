"""Flawless Victory Strategy (15min BTC "Machine Learning Strategy") - Bunghole / TradingView
(i3Uc79fF, Pine v4 aberto, PUB;1BVZuaaWOUGrbnKzHCECJiO5DMdrSK36) - traducao fiel e teste.

NAO TEM NADA DE MACHINE LEARNING. O titulo diz "Machine Learning Strategy" mas a fonte e
Bollinger + RSI (e MFI na v3) com tres conjuntos de constantes cravados no codigo. O unico
vestigio de "otimizacao" sao os stops/alvos com TRES casas decimais (6,604% / 2,328% /
8,882% / 2,317%), que e a assinatura classica de grade varrida no proprio periodo de teste
(BTC 15m) - ou seja, parametros ajustados ao historico, nao aprendidos.

Regras (constantes do Pine, so-COMPRA nas tres versoes):
  RSI = ta.rsi(close, 14) (Wilder);  MFI = ta.mfi(hlc3, 14);  BB com stdev POPULACIONAL
  BB1 = sma(close,20) +- 1,0*stdev(close,20)      BB2 = sma(close,17) +- 1,0*stdev(close,17)
  v1 (sem stop/alvo):  compra close < BB1_inf E RSI > 42 ; vende close > BB1_sup E RSI > 70
  v2 (SL 6,604% / TP 2,328%): compra close < BB2_inf E RSI > 42 ; vende close > BB2_sup E RSI > 76
  v3 (SL 8,882% / TP 2,317%): compra close < BB1_inf E MFI < 60 ;
                              vende close > BB1_sup E RSI > 65 E MFI > 64
  Sinal no fechamento, ordem a mercado na ABERTURA da barra seguinte (calc_on_every_tick=false).
  pyramiding=0: sinal de compra com posicao aberta nao faz nada. strategy.exit de v2/v3 fica ativo
  desde a barra de entrada.

Guarda invertida (nao e bug, e consequencia): o "guard" de venda da v1/v2 e RSI > 70/76, isto e,
a estrategia so SAI quando o mercado esta esticado para CIMA. Se o preco cair depois da compra,
a v1 nao tem saida nenhuma - fica carregando o long ate aparecer uma banda superior com RSI alto.

Medicao: retorno sobre o nocional (1x), que e o que o Pine faz com percent_of_equity=100.
Custo CUSTO[ativo] por perna (spread Lighter) + funding FUND[ativo] pro-rata (o long paga).
Stop/alvo das v2/v3 resolvidos minuto a minuto no M1, com a abertura de cada minuto testada
primeiro (gap que pula o stop sai NA ABERTURA, pior que o stop). Quando stop e alvo caem no
mesmo minuto, o stop sai primeiro (conservador).
Controle: para cada trade, 20 entradas a mercado em barras sorteadas, com a MESMA duracao maxima
e o MESMO stop/alvo -> isola o gatilho BB+RSI/MFI do acaso com a mesma gestao.

uso: python study_flawless.py [xau btc us100 wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

TFS = ['5min', '15min', '30min', '1h', '4h', '1D']
VERS = {
    # (bblen, bbmult, guarda de compra, guarda de venda, sl, tp)
    'v1': dict(BBLEN=20, BBMULT=1.0, BUY=('rsi>', 42.0), SELL=[('rsi>', 70.0)], SL=0.0, TP=0.0),
    'v2': dict(BBLEN=17, BBMULT=1.0, BUY=('rsi>', 42.0), SELL=[('rsi>', 76.0)], SL=0.06604, TP=0.02328),
    'v3': dict(BBLEN=20, BBMULT=1.0, BUY=('mfi<', 60.0), SELL=[('rsi>', 65.0), ('mfi>', 64.0)],
               SL=0.08882, TP=0.02317),
}


def signals(df, p):
    c = df.close.to_numpy(float)
    hlc3 = ((df.high + df.low + df.close) / 3).to_numpy(float)
    v = df.volume.to_numpy(float)
    rsi = T.rsi_wilder(c, 14)
    mf = T.mfi(hlc3, v, 14)
    basis = T.sma(c, p['BBLEN']); dev = p['BBMULT'] * T.stdev_pop(c, p['BBLEN'])
    up, lo = basis + dev, basis - dev
    ind = {'rsi': rsi, 'mfi': mf}

    def guard(g):
        k, lv = g[0][:3], g[1]
        return (ind[k] > lv) if g[0][-1] == '>' else (ind[k] < lv)

    buy = (c < lo) & guard(p['BUY'])
    sell = (c > up)
    for g in p['SELL']:
        sell = sell & guard(g)
    ok = ~np.isnan(lo) & ~np.isnan(rsi) & ~np.isnan(mf)
    return buy & ok, sell & ok


def run(name, tf, ver, m1, df, sl=None, tp=None, verbose=True, tag=None):
    p = VERS[ver]
    sl = p['SL'] if sl is None else sl
    tp = p['TP'] if tp is None else tp
    L, X = signals(df, p)
    if sl > 0 or tp > 0:
        raw = T.engine_sltp(df, m1, L, X, sl, tp)
        tr = T.book_sltp(df, raw, name)
    else:
        raw = T.engine_signal_exit(df, L, X)
        tr = T.book(df, [(i, j, 1.0) for i, j, u, e in raw], name)
    o = T.summarize(df, tr, name, sl=sl, tp=tp, m1=m1)
    if o and verbose:
        T.line(tag or f'{ver} {tf} SL{sl:.2%}/TP{tp:.2%}', o)
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M barras)")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        print("\n-- defaults das tres versoes, por timeframe (15min = o do titulo)")
        for ver, tf in itertools.product(('v1', 'v2', 'v3'), TFS):
            o, tr = run(name, tf, ver, m1, cache[tf])
            if o:
                rows.append(dict(o, ver=ver, TF=tf, SL=VERS[ver]['SL'], TP=VERS[ver]['TP']))
        print("\n-- sensibilidade do par stop/alvo (v2 e v3, so no TF do titulo e vizinhos)")
        for ver, tf, sl, tp in itertools.product(('v2', 'v3'), ('15min', '1h'),
                                                 (0.02, 0.04, 0.0660, 0.0888, 0.15),
                                                 (0.01, 0.0233, 0.05, 0.10)):
            o, _ = run(name, tf, ver, m1, cache[tf], sl=sl, tp=tp, verbose=False)
            if o:
                rows.append(dict(o, ver=ver, TF=tf, SL=sl, TP=tp))
        print("\n-- v1/v2/v3 sem stop nem alvo (so os gatilhos de BB+RSI/MFI)")
        for ver, tf in itertools.product(('v2', 'v3'), TFS):
            o, _ = run(name, tf, ver, m1, cache[tf], sl=0.0, tp=0.0,
                       tag=f'{ver} {tf} sem SL/TP')
            if o:
                rows.append(dict(o, ver=ver, TF=tf, SL=0.0, TP=0.0))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_flawless_{name}_grid.csv'), index=False)
        pos = g[(g.bp_liq > 0)]
        print(f"\n  grade {name}: {len(g)} celulas | liq>0: {len(pos)} | liq>0 e t>1: "
              f"{((g.bp_liq > 0) & (g.t > 1)).sum()} | liq>0 e CAGR>B&H: "
              f"{((g.bp_liq > 0) & (g.cagr > g.bh)).sum()}")
        print(g.sort_values('bp_liq', ascending=False).head(12)[
            ['ver', 'TF', 'SL', 'TP', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win',
             'cagr', 'bh', 'sharpe', 'expo', 'ctl_bp', 't']].to_string(
            index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
