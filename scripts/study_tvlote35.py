"""Lote 35 (2026-10-27): Linear Regression Pearson's R - Trend Channel Strategy (x11joe, `6VHnjgfp`, Pine v4),
um dos 5 de prioridade baixa em estrategias/puladas_complexas.md. Grade completa nos 5 ativos (ver docs/LOTE35_TV.md).

uso: python study_tvlote35.py xau us100 wti btc eth
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
from study_tvlote7 import run_g, ohlc, TFS
from study_tvlote9 import summary
from study_tvlote25 import posflat
from study_tvlote30 import R


@njit(cache=True)
def pearson_pick(c, kmax, kmin, step, pos, neg):
    """Laco do script: k = kmax, kmax-step, ..., kmin; R de Pearson de close[i] contra i (i = barras atras, logo
    R > 0 = baixa). Para no primeiro k com R >= pos ou R <= neg; sem nenhum, fica o R do ultimo k (kmin).
    Devolve (R escolhido, 1 se algum k atingiu o limiar)."""
    n = len(c); out = np.full(n, np.nan); hit = np.zeros(n)
    for j in range(kmax - 1, n):
        k = kmax
        while k >= kmin:
            ex = 0.0; ey = 0.0; ex2 = 0.0; ey2 = 0.0; exy = 0.0
            for i in range(k):
                y = c[j - i]; ex += i; ey += y; ex2 += i * i; ey2 += y * y; exy += y * i
            den = np.sqrt(ex2 - ex * ex / k) * np.sqrt(ey2 - ey * ey / k)
            r = (exy - ex * ey / k) / den if den > 0 else 0.0
            out[j] = r
            if r >= pos or r <= neg:
                hit[j] = 1.0
                break
            k -= step
    return out, hit


def run_lpr(name, df, mm, tag, rows=None, verbose=True, kmax=360, kmin=24, step=12, pos=0.85, neg=-0.71,
            forte=False, long_ok=True, short_ok=True, **extra):
    """R < 0 (alta) compra, R > 0 (baixa) vende; sempre posicionado e inverte, como no script. forte=True: so
    fica posicionado quando algum periodo atingiu o limiar (o resto zera)."""
    o, h, l, c = ohlc(df)
    r, hit = pearson_pick(np.asarray(c, float), kmax, kmin, step, pos, neg)
    if forte:
        p = np.where(hit > 0, np.where(r < 0, 1, np.where(r > 0, -1, 0)), 0)
        return run_g(name, df, posflat(df, mm, p, long_ok, short_ok), tag, rows, verbose, extra)
    return R(name, df, mm, tag, rows, verbose, extra, r < 0, r > 0, long_ok, short_ok)


side2 = ('ambos', 'long')
sk = lambda s: dict(short_ok=s == 'ambos')
GRID = {
    'lpr': (run_lpr, "1. Linear Regression Pearson's R", 'k360 sempre ambos',
            [(f"k{k} {'forte' if f else 'sempre'} {s}", dict(kmax=k, forte=f, **sk(s)))
             for k, f, s in itertools.product((360, 120), (False, True), side2)]),
}


def KW(est, cfg):
    """kwargs de uma celula da grade a partir do rotulo (usado por study_veredito_lote)."""
    fn, _, dflt, combos = GRID[est]
    return {} if cfg == dflt else dict(combos)[cfg]


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        cache = {tf: T.resample(m1, tf) for tf in TFS}
        rows = []
        for est, (fn, label, default_cfg, combos) in GRID.items():
            print(f"\n### {label}", flush=True)
            for tf in TFS:
                df = cache[tf]
                fn(name, df, mm, f"{tf} {est.upper()} default", rows, est=est, TF=tf, cfg=default_cfg)
                for cfg, kw in combos:
                    if cfg == default_cfg: continue
                    fn(name, df, mm, '', rows, False, est=est, TF=tf, cfg=cfg, **kw)
        summary(pd.DataFrame(rows).drop_duplicates(['est', 'TF', 'cfg']), name, 'tvlote35')


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth'])
