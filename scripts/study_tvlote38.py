"""Lote 38 do TradingView (2026-10-27): ultimo lote, posicoes 1001 a 1007 da lista; 4 estrategias nos 5 ativos com a
grade completa dos lotes 26 a 37 (ver docs/LOTE38_TV.md, com as puladas).

uso: python study_tvlote38.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import gsim, run_g, ohlc, TFS
from study_tvlote9 import summary
from study_tvlote20 import sh
from study_tvlote25 import hh, ll, Z, NAN
from study_tvlote30 import R


def cross(a, b):
    return T.xover(a, b) | T.xunder(a, b)


# ------------------------------------------------------------------ 1. Robot Wealth Simple Pairs Trade (oqmZwvbA)
def run_rwp(name, df, mm, tag, rows=None, verbose=True, n=20, z=2.0, long_ok=True, short_ok=True, **extra):
    """Num ativo so (o 'par' do script e o grafico): close cruzando (em qualquer sentido) a banda de baixo da BB 20 x 2
    compra, a de cima vende; close cruzando a media zera; sinal contrario inverte."""
    o, h, l, c = ohlc(df); m = T.sma(c, n); d = z * T.stdev_pop(c, n); x = cross(c, m)
    res = gsim(df, mm, cross(c, m - d), cross(c, m + d), x, x, rev=True, long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 2. Kijun-Sen Strategy DasanC (UdTnzvG6)
def run_kij(name, df, mm, tag, rows=None, verbose=True, n=20, long_ok=True, short_ok=True, **extra):
    """Vela abrindo abaixo da Kijun 20 e fechando acima compra (espelho vende), so sem posicao; close do outro lado da
    Kijun fecha (lote por risco, stop em pontos x 100000 e alvo de 100 pontos ficaram de fora)."""
    o, h, l, c = ohlc(df); k = (hh(h, n) + ll(l, n)) / 2
    res = gsim(df, mm, (o < k) & (c > k), (o > k) & (c < k), c < k, c > k, rev=False,
               long_ok=long_ok, short_ok=short_ok)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 3. Trailing Stop Loss (YToR5J20)
def run_tsl(name, df, mm, tag, rows=None, verbose=True, p=(21, 49), tsl=0.075, long_ok=True, short_ok=False, **extra):
    """So long: SMA21 cruzando acima da SMA49 compra, abaixo fecha; trailing de 7,5% abaixo da maior maxima desde o
    sinal, conferido no fechamento (saida na abertura seguinte, nao no toque)."""
    o, h, l, c = ohlc(df); f, s = T.sma(c, p[0]), T.sma(c, p[1]); L = T.xover(f, s)
    g = np.cumsum(L); mx = pd.Series(h).groupby(g).cummax().to_numpy()
    X = T.xunder(f, s) | ((g > 0) & (c < mx * (1 - tsl)) if tsl > 0 else Z(c))
    res = gsim(df, mm, L, Z(c), X & ~L, rev=False, short_ok=False)
    return run_g(name, df, res, tag, rows, verbose, extra)


# ------------------------------------------------------------------ 4. SMAcross-mvr (4j0UOOB8)
def run_smx(name, df, mm, tag, rows=None, verbose=True, p=(10, 50), long_ok=True, short_ok=True, **extra):
    """SMA10 da abertura cruzando a SMA50 da abertura: acima compra, abaixo vende; inverte (modo A, padrao)."""
    o, h, l, c = ohlc(df); f, s = T.sma(o, p[0]), T.sma(o, p[1])
    return R(name, df, mm, tag, rows, verbose, extra, T.xover(f, s), T.xunder(f, s), long_ok, short_ok)


side2 = ('ambos', 'long')
sk = lambda s: dict(short_ok=s == 'ambos')
pr = lambda v: '/'.join(f'{x:g}' for x in v)


def g2(key, vals, fmt):
    return [(fmt(v) + f' {s}', {key: v, **sk(s)}) for v, s in itertools.product(vals, side2)]


GRID = {
    'rwp': (run_rwp, "1. Robot Wealth Pairs (BB 20x2)", 'z2 ambos', g2('z', (2.0, 1.5), lambda v: f'z{v:g}')),
    'kij': (run_kij, "2. Kijun-Sen DasanC", 'n20 ambos', g2('n', (20, 60), lambda v: f'n{v}')),
    'tsl': (run_tsl, "3. Trailing Stop Loss (SMA 21/49)", 'tsl7.5',
            [('tsl15', dict(tsl=0.15)), ('semtsl', dict(tsl=0.0)), ('50/200 tsl7.5', dict(p=(50, 200)))]),
    'smx': (run_smx, "4. SMAcross-mvr", '10/50 ambos', g2('p', ((10, 50), (50, 200)), pr)),
}
TF_EST = {}


def KW(est, cfg):
    """kwargs de uma celula da grade a partir do rotulo (usado por study_veredito_lote)."""
    fn, _, dflt, combos = GRID[est]
    return {} if cfg == dflt else dict(combos)[cfg]


def main(nomes, ests=None):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        for est, (fn, label, default_cfg, combos) in GRID.items():
            if ests and est not in ests: continue
            print(f"\n### {label}", flush=True)
            for tf in TF_EST.get(est, TFS):
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    if cfg == default_cfg: continue
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote38')


if __name__ == '__main__':
    a = sys.argv[1:]
    main([x for x in a if '=' not in x] or ['xau', 'us100', 'wti', 'btc', 'eth'],
         next((x.split('=')[1].split(',') for x in a if x.startswith('est=')), None))
