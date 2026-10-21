"""[STRATEGY][RS]ZigZag PA Strategy V4.1 (RicardoSantos, NEDEDcsP, Pine v2).

Regra publicada:
  - ZigZag de 2 barras: pivo de alta quando a barra anterior e de alta e a atual de baixa
    (valor = highest(high,2)), pivo de baixa no inverso (lowest(low,2)); so alterna direcao.
  - O zigzag e lido numa resolucao ALTERNATIVA (default 60 min) via security(tickerid, tf, zigzag())
    e so e colocado no grafico na primeira barra de cada candle HTF (change(time(tf)) != 0).
    Pine v2 nao tem o parametro lookahead e o security() historico devolve o valor FINAL do candle
    HTF corrente  <-- OLHA O FUTURO (ate 1 candle HTF inteiro).
  - x,a,b,c,d = 5 ultimos pivos; razoes XAB/ABC/BCD/XAD testadas contra 17 padroes harmonicos
    (Bat, Gartley, Crab, Shark, 5-O, Wolf, H&S, triangulos, AB=CD e os "Anti").
  - Long: padrao de alta (d < c) e close <= fib(0.236) da perna c->d; short espelhado.
    Saida (strategy.close, ordem a mercado na abertura seguinte): high >= fib(0.618) [alvo] ou
    low <= fib(-0.236) [stop], com fib recalculado a cada barra sobre o c/d CORRENTE.
  - pyramiding=0: entrada contraria inverte a posicao.

Testes:
  peek     : como publicado (valor do candle HTF corrente) - so mede o tamanho do vies.
  honesto  : mesma regra com o ultimo candle HTF FECHADO.
  grade    : TF do grafico x TF alternativo x janela de entrada x alvo x stop, no modo honesto.

Execucao: sinal no fechamento, ordem na ABERTURA seguinte (como strategy.close/entry do Pine).
Custo CUSTO[ativo] por perna + funding FUND[ativo] pro-rata. Controle: mesmo lado, mesma duracao.

uso: python study_zigzagpa.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

# (TF do grafico, TF do zigzag); None = zigzag no proprio grafico (useAltTF=false)
CFGS = [('5min', '1h'), ('15min', '1h'), ('15min', '4h'), ('30min', '4h'), ('1h', '1D'),
        ('15min', None), ('1h', None), ('4h', None), ('1D', None)]


# ------------------------------------------------------------------ zigzag (funcao do Pine)
@njit(cache=True)
def _zigzag(o, h, l, c):
    n = len(c); zz = np.full(n, np.nan); d = 0
    for i in range(1, n):
        up1 = c[i - 1] >= o[i - 1]; dn1 = c[i - 1] <= o[i - 1]
        up = c[i] >= o[i]; dn = c[i] <= o[i]
        dprev = d
        if up1 and dn: d = -1
        elif dn1 and up: d = 1
        if up1 and dn and dprev != -1:
            zz[i] = max(h[i], h[i - 1])
        elif dn1 and up and dprev != 1:
            zz[i] = min(l[i], l[i - 1])
    return zz


def zigzag(df):
    return _zigzag(*(df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close')))


def chart_zigzag(df, m1, alt, peek):
    """sz no grafico. Com alt: so na primeira barra de cada candle HTF; peek=True devolve o valor
    final do candle HTF corrente (security() do Pine v2), peek=False o do ultimo HTF fechado."""
    if alt is None:
        return zigzag(df)
    htf = T.resample(m1, alt)
    zz = zigzag(htf)
    if not peek:
        zz = np.concatenate([[np.nan], zz[:-1]])
    g = htf.index.searchsorted(df.index, side='right') - 1     # candle HTF que contem a barra
    first = np.r_[True, g[1:] != g[:-1]] & (g >= 0)
    sz = np.full(len(df), np.nan)
    sz[first] = zz[g[first]]
    return sz


def last5(sz):
    """valuewhen(sz, sz, k) para k = 4..0 -> x, a, b, c, d."""
    n = len(sz); out = np.full((5, n), np.nan)
    piv = np.where(~np.isnan(sz) & (sz != 0))[0]
    cnt = np.searchsorted(piv, np.arange(n), side='right')    # pivos ate a barra i, inclusive
    vals = sz[piv]
    for k in range(5):                                          # k=0 -> d (ultimo), k=4 -> x
        idx = cnt - 1 - k
        ok = idx >= 0
        out[4 - k, ok] = vals[idx[ok]]
    return out


# ------------------------------------------------------------------ padroes harmonicos
def _rng(v, lo, hi):
    return (v >= lo) & (v <= hi)


def patterns(x, a, b, c, d):
    with np.errstate(divide='ignore', invalid='ignore'):
        xab = np.abs(b - a) / np.abs(x - a)
        xad = np.abs(a - d) / np.abs(x - a)
        abc = np.abs(b - c) / np.abs(a - b)
        bcd = np.abs(c - d) / np.abs(b - c)
    # divisao por zero no Pine e na -> toda comparacao falsa
    xab, xad, abc, bcd = (np.where(np.isfinite(v), v, np.nan) for v in (xab, xad, abc, bcd))
    R = _rng
    P = {
        'Bat': R(xab, .382, .5) & R(abc, .382, .886) & R(bcd, 1.618, 2.618) & (xad <= .618),
        'AntiBat': R(xab, .5, .886) & R(abc, 1., 2.618) & R(bcd, 1.618, 2.618) & R(xad, .886, 1.),
        'AltBat': (xab <= .382) & R(abc, .382, .886) & R(bcd, 2., 3.618) & (xad <= 1.13),
        'Butterfly': (xab <= .786) & R(abc, .382, .886) & R(bcd, 1.618, 2.618) & R(xad, 1.27, 1.618),
        'AntiButterfly': R(xab, .236, .886) & R(abc, 1.13, 2.618) & R(bcd, 1., 1.382) & R(xad, .5, .886),
        'ABCD': R(abc, .382, .886) & R(bcd, 1.13, 2.618),
        'Gartley': R(xab, .5, .618) & R(abc, .382, .886) & R(bcd, 1.13, 2.618) & R(xad, .75, .875),
        'AntiGartley': R(xab, .5, .886) & R(abc, 1., 2.618) & R(bcd, 1.5, 5.) & R(xad, 1., 5.),
        'Crab': R(xab, .5, .875) & R(abc, .382, .886) & R(bcd, 2., 5.) & R(xad, 1.382, 5.),
        'AntiCrab': R(xab, .25, .5) & R(abc, 1.13, 2.618) & R(bcd, 1.618, 2.618) & R(xad, .5, .75),
        'Shark': R(xab, .5, .875) & R(abc, 1.13, 1.618) & R(bcd, 1.27, 2.24) & R(xad, .886, 1.13),
        'AntiShark': R(xab, .382, .875) & R(abc, .5, 1.) & R(bcd, 1.25, 2.618) & R(xad, .5, 1.25),
        '5o': R(xab, 1.13, 1.618) & R(abc, 1.618, 2.24) & R(bcd, .5, .625) & R(xad, 0., .236),
        'Wolf': R(xab, 1.27, 1.618) & R(abc, 0., 5.) & R(bcd, 1.27, 1.618) & R(xad, 0., 5.),
        'HnS': R(xab, 2., 10.) & R(abc, .9, 1.1) & R(bcd, .236, .88) & R(xad, .9, 1.1),
        'ConTria': R(xab, .382, .618) & R(abc, .382, .618) & R(bcd, .382, .618) & R(xad, .236, .764),
        'ExpTria': R(xab, 1.236, 1.618) & R(abc, 1., 1.618) & R(bcd, 1.236, 2.) & R(xad, 2., 2.236),
    }
    anyp = np.zeros(len(d), bool)
    for v in P.values():
        anyp |= v
    return anyp, P


def setup(df, m1, alt, peek):
    sz = chart_zigzag(df, m1, alt, peek)
    x, a, b, c, d = last5(sz)
    anyp, P = patterns(x, a, b, c, d)
    return dict(c=c, d=d, bull=anyp & (d < c), bear=anyp & (d > c), P=P, npiv=int((~np.isnan(sz)).sum()))


def signals(df, st, ew=0.236, tp=0.618, sl=-0.236):
    c, d = st['c'], st['d']
    rng = np.abs(d - c)
    sgn = np.where(d > c, -1.0, 1.0)            # f_last_fib: d>c ? d - r*rate : d + r*rate
    fib = lambda r: d + sgn * rng * r
    cl = df.close.to_numpy(float); hi = df.high.to_numpy(float); lo = df.low.to_numpy(float)
    le = st['bull'] & (cl <= fib(ew))
    lx = (hi >= fib(tp)) | (lo <= fib(sl))
    se = st['bear'] & (cl >= fib(ew))
    sx = (lo <= fib(tp)) | (hi >= fib(sl))
    return le, lx & ~np.isnan(d), se, sx & ~np.isnan(d)


@njit(cache=True)
def _sim(le, lx, se, sx):
    """Ordens decididas no fechamento da barra i e executadas na abertura de i+1 (pyramiding=0)."""
    n = len(le); pos = 0; i0 = -1
    ei = np.empty(n, np.int64); ej = np.empty(n, np.int64); es = np.empty(n, np.int64); k = 0
    for i in range(n - 1):
        new = pos
        if pos == 0:
            if le[i]: new = 1
            elif se[i]: new = -1
        elif pos == 1:
            if se[i]: new = -1
            elif lx[i]: new = 0
        else:
            if le[i]: new = 1
            elif sx[i]: new = 0
        if new != pos:
            j = i + 1
            if pos != 0:
                ei[k] = i0; ej[k] = j; es[k] = pos; k += 1
            pos = new; i0 = j
    return ei[:k], ej[:k], es[:k]


# ------------------------------------------------------------------ controle vetorizado
def _control_fast(df, trades, name, nsim=20, **kw):
    """Mesmo controle do tvlib (mesmo lado, mesma duracao, entrada sorteada), vetorizado:
    as saidas desta estrategia sao ordens a mercado na abertura, basta o retorno aberto-a-aberto."""
    o = df.open.to_numpy(float)
    secs = df.index.to_series().diff().dt.total_seconds().median()
    n = len(o)
    durs = np.maximum(1, trades.j.to_numpy(np.int64) - trades.i.to_numpy(np.int64))
    sides = trades.d.to_numpy(float)
    hi = np.maximum(n - durs - 1, 1)
    yrs = durs * secs / (365 * 86400)
    res = np.zeros(nsim)
    for s in range(nsim):
        i = (T.RNG.random(len(durs)) * hi).astype(np.int64)
        r = sides * (o[i + durs] / o[i] - 1) - 2 * T.CUSTO[name] - T.FUND.get(name, 5.0) / 100 * yrs * sides
        res[s] = r.mean()
    return res


T.control_dur = _control_fast


def run(name, df, sig, tag, rows=None, verbose=True, long_ok=True, short_ok=True, **extra):
    le, lx, se, sx = sig
    if not long_ok: le = np.zeros_like(le)
    if not short_ok: se = np.zeros_like(se)
    ei, ej, es = _sim(le, lx, se, sx)
    tr = T.book(df, list(zip(ei, ej, es)), name)
    o = T.summarize(df, tr, name)
    if o:
        o['long_frac'] = float((tr.d > 0).mean())
        if verbose: T.line(tag, o)
        if rows is not None: rows.append(dict(o, tag=tag, **extra))
    elif verbose:
        print(f"  {tag:<34} (menos de 10 trades)")
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}  ({len(m1)/1e6:.2f}M barras)")
        cache = {tf: T.resample(m1, tf) for tf in {c[0] for c in CFGS}}
        rows = []
        for tf, alt in CFGS:
            df = cache[tf]
            lab = f"{tf}/{alt or '-'}"
            modes = (True, False) if alt else (False,)
            for peek in modes:
                st = setup(df, m1, alt, peek)
                mode = 'peek' if peek else 'honesto'
                print(f"\n### {lab} {mode}: {st['npiv']} pivos, barras com padrao de alta "
                      f"{st['bull'].mean():.0%} / baixa {st['bear'].mean():.0%}")
                sig = signals(df, st)
                run(name, df, sig, f"{lab} {mode} default", rows, est=mode, TF=tf, alt=alt or '-',
                    cfg='ew.236 tp.618 sl-.236')
                if peek:
                    continue
                run(name, df, sig, f"{lab} {mode} so long", rows, short_ok=False, est='hon_long',
                    TF=tf, alt=alt or '-', cfg='ew.236 tp.618 sl-.236')
                run(name, df, sig, f"{lab} {mode} so short", rows, long_ok=False, est='hon_short',
                    TF=tf, alt=alt or '-', cfg='ew.236 tp.618 sl-.236')
                for ew, tp, sl in itertools.product((0.0, 0.236, 0.382, 0.5), (0.382, 0.618, 1.0, 1.618),
                                                    (-0.236, -0.5, -1.0)):
                    run(name, df, signals(df, st, ew, tp, sl), '', rows, verbose=False, est='grade',
                        TF=tf, alt=alt or '-', cfg=f'ew{ew} tp{tp} sl{sl}')

        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'results', f'study_zigzagpa_{name}_grid.csv'), index=False)
        h = g[g.est != 'peek']
        print(f"\n=== resumo {name}: {len(h)} celulas honestas ===")
        print(f"  liq>0 {int((h.bp_liq > 0).sum())} | liq>0 e t>2 {int(((h.bp_liq > 0) & (h.t > 2)).sum())}"
              f" | CAGR>B&H {int((h.cagr > h.bh).sum())} | Sharpe>0 {int((h.sharpe > 0).sum())}")
        p = g[g.est == 'peek']
        print(f"  peek: {len(p)} celulas, CAGR medio {p.cagr.mean():+.1%}, liq medio {p.bp_liq.mean():+.1f}bp")
        cols = ['est', 'TF', 'alt', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr',
                'bh', 'sharpe', 'dd', 'expo', 'ctl_bp', 't']
        print("\n  top 15 honestas por CAGR:")
        print(h.sort_values('cagr', ascending=False).head(15)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
