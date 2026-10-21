"""MACD + SMA 200 Strategy (by ChartArt) v1.0 - TradingView yMCa3XZD (Pine v2, aberto; fonte
extraida do HTML da pagina do script, campo script.content).

Regras do Pine (defaults entre parenteses):
  fastMA  = sma(close, 12)        slowMA = sma(close, 26)       veryslowMA = sma(close, 200)
  macd    = fastMA - slowMA       signal = sma(macd, 9)         hist = macd - signal
  long  : crossover(hist, 0)  E macd > 0 E fastMA > slowMA E close[slowLength] > veryslowMA
  short : crossunder(hist, 0) E macd < 0 E fastMA < slowMA E close[slowLength] < veryslowMA
  ordens: strategy.entry(..., stop=low) no longo e stop=high no short. Como o stop de COMPRA fica
          ABAIXO do preco atual (e o de venda ACIMA), a ordem ja esta "ativada" e preenche na
          ABERTURA da barra seguinte. (EXEC=0 = fiel; EXEC=1 = fechamento do sinal, sensibilidade.)
  cancel: strategy.cancel quando slowMA cruza a veryslowMA do lado errado - como as ordens enchem
          na barra seguinte, o cancel praticamente nunca tem efeito; nao altera posicao aberta.
  saidas: NAO EXISTEM. Sem stop, sem alvo, sem time stop (strategy.risk.max_intraday_loss(50%) e
          um disjuntor de equity, nao uma saida de trade). A posicao so muda no sinal CONTRARIO
          (pyramiding 0 -> inverte). Depois do 1o sinal o sistema fica sempre no mercado.

Quirks do publicado que a descricao nao conta:
  - "the recent price has to be above the SMA 200" na verdade e close[26] (slowLength barras atras)
    vs a SMA200 de AGORA -> um filtro defasado; QL=0 testa a leitura literal (close atual).
  - macd = diferenca de SMAs (nao EMAs), ou seja nao e o MACD padrao.
  - hist > 0 cruzando + macd > 0 + fast > slow sao fortemente redundantes entre si.

Medicao: sem stop nao ha 1R -> retorno sobre o nocional a 1x (o que o Pine faz com % of equity),
sempre contra (a) buy & hold do mesmo ativo no mesmo periodo e (b) controle aleatorio com a MESMA
estrutura (mesmo nº de inversoes, mesma alternancia de lados, instantes sorteados).
Custo: CUSTO[ativo] por perna (spread Lighter) e funding FUND[ativo] pro-rata (long paga, short
recebe) - protagonista aqui porque o carrego dura semanas.

uso: python study_macdsma.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO, FUND
from study_macdconf import load_m1, resample
from study_bbrsi import to_trades, equity_stats, control

TFS = ['15min', '30min', '1h', '4h', '1D']
BASE = dict(TF='1h', FAST=12, SLOW=26, SIG=9, VSLOW=200, QL=1, LONG=1, SHORT=1, EXEC=0, FLAT=0)


def signals(df, p):
    c = df.close.to_numpy(float)
    s = pd.Series(c)
    fast = s.rolling(p['FAST']).mean().to_numpy()
    slow = s.rolling(p['SLOW']).mean().to_numpy()
    vslow = s.rolling(p['VSLOW']).mean().to_numpy()
    macd = fast - slow
    sig = pd.Series(macd).rolling(p['SIG']).mean().to_numpy()
    hist = macd - sig
    # close[slowLength] vs veryslowMA atual (QL=1, fiel) ou close atual (QL=0, leitura literal)
    lag = p['SLOW'] if p['QL'] else 0
    cl = np.full(len(c), np.nan)
    if lag: cl[lag:] = c[:-lag]
    else: cl = c.copy()
    xup = np.zeros(len(c), bool); xup[1:] = (hist[1:] > 0) & (hist[:-1] <= 0)
    xdn = np.zeros(len(c), bool); xdn[1:] = (hist[1:] < 0) & (hist[:-1] >= 0)
    ok = ~(np.isnan(hist) | np.isnan(vslow) | np.isnan(cl))
    L = xup & (macd > 0) & (fast > slow) & (cl > vslow) & ok
    S = xdn & (macd < 0) & (fast < slow) & (cl < vslow) & ok
    return L, S


def run(name, p, df=None, m1=None, verbose=True):
    if df is None: df = resample(m1, p['TF'])
    L, S = signals(df, p)
    tr = to_trades(df, L, S, p, name)
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
    if len(tr) < 5: return None, tr
    st = equity_stats(df, tr, name)
    bh = np.expm1(np.log(df.close.iloc[-1] / df.close.iloc[0]) / yrs)
    ctl = control(df, tr, name)
    mu = tr.ret.mean()
    t = (mu - ctl.mean()) / (ctl.std(ddof=1) + 1e-12)
    out = dict(trades=len(tr), por_ano=len(tr) / yrs, bp_bruto=1e4 * tr.bruto.mean(),
               bp_liq=1e4 * mu, win=(tr.ret > 0).mean(), dias=tr.yrs.mean() * 365,
               bp_sf=1e4 * tr.ret_sf.mean(), cagr=st['cagr'], bh=bh, sharpe=st['sharpe'],
               dd=st['dd'], expo=st['expo'], ctl_bp=1e4 * ctl.mean(), t=t)
    if verbose:
        print(f"  {name} {p['TF']:>6} {p['FAST']}/{p['SLOW']}/{p['SIG']} V{p['VSLOW']} QL{p['QL']} "
              f"L{p['LONG']}S{p['SHORT']} | {len(tr):4d} tr ({out['por_ano']:.1f}/ano, {out['dias']:.0f}d) | "
              f"bruto {out['bp_bruto']:+7.0f}bp liq {out['bp_liq']:+7.0f}bp (s/fund {out['bp_sf']:+7.0f}bp, "
              f"win {out['win']:.0%}) | CAGR {out['cagr']:+.1%} vs B&H {bh:+.1%} | Sh {out['sharpe']:+.2f} "
              f"DD {out['dd']:.0%} expo {out['expo']:.0%} | ctl {out['ctl_bp']:+7.0f}bp t={t:+.2f}")
    return out, tr


KEYS = ('TF', 'FAST', 'SLOW', 'SIG', 'VSLOW', 'QL', 'LONG', 'SHORT')


def main(nomes):
    for name in nomes:
        print(f"\n===== {name} =====")
        m1 = load_m1(name)
        cache = {tf: resample(m1, tf) for tf in TFS}
        print(f"  dados {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M m1)")
        rows = []
        print("\n-- defaults (12/26/9, SMA200) por timeframe")
        for tf in TFS:
            p = dict(BASE, TF=tf)
            o, _ = run(name, p, df=cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in KEYS}))
        print("\n-- defaults com filtro sem defasagem (QL=0)")
        for tf in TFS:
            p = dict(BASE, TF=tf, QL=0)
            o, _ = run(name, p, df=cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in KEYS}))
        print("\n-- lados separados (defaults)")
        for tf in TFS:
            for lg, sh in ((1, 0), (0, 1)):
                p = dict(BASE, TF=tf, LONG=lg, SHORT=sh, FLAT=1)
                o, _ = run(name, p, df=cache[tf])
                if o: rows.append(dict(o, **{k: p[k] for k in KEYS}))
        print("\n-- grade TF x MACD x SMA lenta x filtro")
        combos = [(12, 26, 9), (8, 17, 9), (19, 39, 9), (12, 26, 5), (5, 35, 5), (24, 52, 18)]
        for tf, (f, s, g), vs, ql in itertools.product(TFS, combos, (50, 100, 200, 400), (0, 1)):
            p = dict(BASE, TF=tf, FAST=f, SLOW=s, SIG=g, VSLOW=vs, QL=ql)
            o, _ = run(name, p, df=cache[tf], verbose=False)
            if o: rows.append(dict(o, **{k: p[k] for k in KEYS}))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_macdsma_{name}_grid.csv'), index=False)
        full = g[(g.LONG == 1) & (g.SHORT == 1)]
        print(f"\n  grade: {len(full)} celulas, {(full.bp_liq > 0).sum()} com retorno liquido > 0, "
              f"{((full.bp_liq > 0) & (full.t > 1)).sum()} tambem acima do controle (t>1), "
              f"{((full.cagr > full.bh) & (full.bp_liq > 0)).sum()} tambem acima do buy&hold")
        print(full.sort_values('bp_liq', ascending=False).head(12)[
            ['TF', 'FAST', 'SLOW', 'SIG', 'VSLOW', 'QL', 'trades', 'por_ano', 'bp_bruto', 'bp_liq',
             'bp_sf', 'cagr', 'bh', 'sharpe', 'ctl_bp', 't']
        ].to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
