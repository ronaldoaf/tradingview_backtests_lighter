"""Bollinger + RSI, Double Strategy (by ChartArt) v1.1 - TradingView uCV8I4xA (Pine v2, aberto;
fonte extraida do HTML da pagina do script, campo script.content).

Regras do Pine (defaults entre parenteses):
  vrsi   = rsi(close, RSIlength=6)              (Wilder/rma)
  BB     = sma(close, BBlength=200) +- 2 * stdev(close, 200)   (stdev populacional, como ta.stdev)
  long   : crossover(vrsi, 50)  E crossover(close, BBlower)    na MESMA barra
  short  : crossunder(vrsi, 50) E crossunder(close, BBupper)   na MESMA barra
  ordens : strategy.entry(..., stop=BBlower/BBupper) com cancel na barra seguinte se o sinal nao
           repetir. Para o longo, o stop de compra fica ABAIXO do preco (close acabou de cruzar a
           banda para cima) -> a ordem esta "ativada" e preenche na abertura da barra seguinte;
           idem no short. Logo, na pratica: sinal no fechamento, entrada na ABERTURA da proxima barra.
           (EXEC=0 = fiel; EXEC=1 = entrada no fechamento do sinal, so para sensibilidade.)
  saidas : NAO EXISTEM. Sem stop, sem alvo, sem time stop. A posicao so muda quando o sinal
           CONTRARIO aparece (pyramiding default 0 -> inverte). Depois do primeiro sinal o sistema
           fica sempre no mercado, de um lado ou do outro.

Consequencia para a medicao: sem stop nao ha 1R. Medimos em retorno sobre o nocional (1x), que e o
que o Pine faz com "% of equity". Reportamos retorno por trade (bp), retorno anual composto a 1x,
Sharpe diario, DD maximo e exposicao, sempre contra:
  (a) buy & hold do mesmo ativo no mesmo periodo;
  (b) controle aleatorio com a MESMA estrutura: mesmo numero de inversoes, mesma alternancia de
      lados, instantes sorteados -> isola o gatilho (RSI+BB) do simples fato de estar no mercado.
Custo: CUSTO[ativo] por perna (spread Lighter) x |variacao de posicao| (inverter = 2 pernas), mais
funding FUND[ativo] proporcional ao tempo (o long paga, o short recebe) - decisivo aqui porque a
estrategia carrega posicao por semanas.

uso: python study_bbrsi.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
sys.path.insert(0, os.path.join(D, 'scripts'))
from study_engulf_psar import CUSTO, FUND
from study_macdconf import load_m1, resample

OHLC = ['open', 'high', 'low', 'close']
TFS = ['15min', '30min', '1h', '4h', '1D']
BASE = dict(TF='1h', RSILEN=6, BBLEN=200, BBMULT=2.0, LEVEL=50.0, LONG=1, SHORT=1, EXEC=0, FLAT=0)
RNG = np.random.default_rng(20261021)


def rsi_wilder(c, n):
    d = np.diff(c, prepend=np.nan)
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    up[0] = dn[0] = np.nan
    def rma(x):
        out = np.full(len(x), np.nan)
        if len(x) < n + 1: return out
        out[n] = np.mean(x[1:n + 1])
        a = 1.0 / n
        for i in range(n + 1, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
        return out
    u, v = rma(up), rma(dn)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(v == 0, 100.0, 100.0 - 100.0 / (1.0 + u / v))


def signals(df, p):
    c = df.close.to_numpy(float)
    vrsi = rsi_wilder(c, p['RSILEN'])
    s = pd.Series(c)
    basis = s.rolling(p['BBLEN']).mean().to_numpy()
    dev = p['BBMULT'] * s.rolling(p['BBLEN']).std(ddof=0).to_numpy()
    up, lo = basis + dev, basis - dev
    def xover(a, b):
        out = np.zeros(len(a), bool)
        out[1:] = (a[1:] > b[1:]) & (a[:-1] <= b[:-1])
        return out & ~np.isnan(a) & ~np.isnan(b)
    L = xover(vrsi, np.full(len(c), p['LEVEL'])) & xover(c, lo)
    S = xover(np.full(len(c), p['LEVEL']), vrsi) & xover(up, c)
    return L, S


def to_trades(df, L, S, p, name):
    """posicao: +1/-1 alternando; execucao na abertura da barra seguinte (EXEC=0)."""
    o = df.open.to_numpy(float); c = df.close.to_numpy(float)
    px = o if p['EXEC'] == 0 else c
    shift = 1 if p['EXEC'] == 0 else 0
    ev = []  # (idx_execucao, lado)
    for i in np.where(L | S)[0]:
        j = i + shift
        if j < len(df): ev.append((j, 1 if L[i] else -1))
    tr = []
    pos = 0; i0 = None
    for j, side in ev:
        # FLAT=1 (teste de um lado so): sinal contrario apenas ZERA a posicao, nao inverte
        if p['FLAT'] and ((side > 0 and not p['LONG']) or (side < 0 and not p['SHORT'])):
            if pos != 0 and j > i0:
                tr.append((i0, j, pos)); pos, i0 = 0, None
            continue
        if side == pos: continue
        if pos != 0 and j > i0:
            tr.append((i0, j, pos))
        if pos == 0 or i0 is None or j > i0:
            pos, i0 = side, j
    out = pd.DataFrame(tr, columns=['i', 'j', 'd'])
    if len(out) == 0: return out
    out['t_in'] = df.index[out.i]; out['t_out'] = df.index[out.j]
    out['entry'] = px[out.i]; out['exit'] = px[out.j]
    yrs = (out.t_out - out.t_in).dt.total_seconds() / (365 * 86400)
    out['bruto'] = out.d * (out.exit / out.entry - 1)
    out['fund'] = FUND.get(name, 5.0) / 100 * yrs * out.d
    out['ret'] = out.bruto - 2 * CUSTO[name] - out.fund   # inverter = 1 perna de saida + 1 de entrada
    out['ret_sf'] = out.bruto - 2 * CUSTO[name]           # sem funding (so spread)
    out['yrs'] = yrs
    return out


def equity_stats(df, tr, name):
    """serie diaria de equity a 1x para Sharpe/DD."""
    pos = pd.Series(0.0, index=df.index)
    for _, r in tr.iterrows(): pos.iloc[r.i:r.j] = r.d
    r = np.log(df.close).diff().fillna(0.0) * pos.shift(1).fillna(0.0)
    cost = pd.Series(0.0, index=df.index)
    chg = pos.diff().abs().fillna(0.0)
    cost -= chg * CUSTO[name]
    fr = FUND.get(name, 5.0) / 100 * (df.index.to_series().diff().dt.total_seconds() / (365 * 86400)).fillna(0.0)
    r = r + cost - pos.shift(1).fillna(0.0) * fr
    d = r.resample('1D').sum()
    d = d[d != 0]
    eq = r.cumsum()
    yrs = (df.index[-1] - df.index[0]).total_seconds() / (365 * 86400)
    return dict(cagr=np.expm1(eq.iloc[-1] / yrs), sharpe=d.mean() / d.std() * np.sqrt(252) if d.std() else np.nan,
                dd=float((eq - eq.cummax()).min()), expo=float((pos != 0).mean()))


def control(df, tr, name, nsim=300):
    """mesma quantidade de inversoes e mesma alternancia de lados, instantes sorteados."""
    px = df.open.to_numpy(float); n = len(df)
    lo = int(tr.i.iloc[0]); hi = int(tr.j.iloc[-1])
    k = len(tr) + 1
    res = []
    for _ in range(nsim):
        pts = np.sort(RNG.choice(np.arange(lo, hi), size=k, replace=False))
        sides = tr.d.to_numpy()
        rr = []
        for m in range(len(sides)):
            a, b = pts[m], pts[m + 1]
            if b <= a: continue
            yrs = (df.index[b] - df.index[a]).total_seconds() / (365 * 86400)
            rr.append(sides[m] * (px[b] / px[a] - 1) - 2 * CUSTO[name] - FUND.get(name, 5.0) / 100 * yrs * sides[m])
        res.append(np.mean(rr))
    return np.array(res)


def run(name, p, df=None, m1=None, verbose=True):
    if df is None: df = resample(m1, p['TF']) if p['TF'] != '1D' else resample(m1, '1D')
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
               bp_sf=1e4 * tr.ret_sf.mean(), cagr=st['cagr'], bh=bh, sharpe=st['sharpe'], dd=st['dd'], expo=st['expo'],
               ctl_bp=1e4 * ctl.mean(), t=t)
    if verbose:
        print(f"  {name} {p['TF']:>6} RSI{p['RSILEN']}/BB{p['BBLEN']} L{p['LONG']}S{p['SHORT']} | "
              f"{len(tr):4d} tr ({out['por_ano']:.1f}/ano, {out['dias']:.0f}d medios) | bruto {out['bp_bruto']:+7.0f}bp"
              f" liq {out['bp_liq']:+7.0f}bp (s/fund {out['bp_sf']:+7.0f}bp, win {out['win']:.0%}) | CAGR {out['cagr']:+.1%} vs B&H {bh:+.1%}"
              f" | Sh {out['sharpe']:+.2f} DD {out['dd']:.0%} expo {out['expo']:.0%}"
              f" | ctl {out['ctl_bp']:+7.0f}bp t={t:+.2f}")
    return out, tr


def main(nomes):
    for name in nomes:
        print(f"\n===== {name} =====")
        m1 = load_m1(name)
        cache = {}
        for tf in TFS:
            cache[tf] = resample(m1, tf)
        print(f"  dados {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M m1)")
        print("\n-- defaults (RSI 6 / BB 200) por timeframe")
        rows = []
        for tf in TFS:
            p = dict(BASE, TF=tf)
            o, tr = run(name, p, df=cache[tf])
            if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'RSILEN', 'BBLEN', 'LONG', 'SHORT')}))
        print("\n-- lados separados (defaults)")
        for tf in TFS:
            for lg, sh in ((1, 0), (0, 1)):
                p = dict(BASE, TF=tf, LONG=lg, SHORT=sh, FLAT=1)
                o, _ = run(name, p, df=cache[tf])
                if o: rows.append(dict(o, **{k: p[k] for k in ('TF', 'RSILEN', 'BBLEN', 'LONG', 'SHORT')}))
        print("\n-- grade RSI x BB x TF")
        for tf, rl, bl in itertools.product(TFS, (4, 6, 9, 14), (50, 100, 200, 400)):
            p = dict(BASE, TF=tf, RSILEN=rl, BBLEN=bl)
            o, _ = run(name, p, df=cache[tf], verbose=False)
            if o:
                rows.append(dict(o, **{k: p[k] for k in ('TF', 'RSILEN', 'BBLEN', 'LONG', 'SHORT')}))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'scripts', f'study_bbrsi_{name}_grid.csv'), index=False)
        full = g[(g.LONG == 1) & (g.SHORT == 1)]
        print(f"\n  grade: {len(full)} celulas, {(full.bp_liq > 0).sum()} com retorno liquido > 0, "
              f"{((full.bp_liq > 0) & (full.t > 1)).sum()} tambem acima do controle (t>1)")
        print(full.sort_values('bp_liq', ascending=False).head(10)[
            ['TF', 'RSILEN', 'BBLEN', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'bp_sf', 'cagr', 'bh', 'sharpe', 'ctl_bp', 't']
        ].to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
