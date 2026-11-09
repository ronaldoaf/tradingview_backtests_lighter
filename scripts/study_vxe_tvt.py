"""VWAP X EMA (lote 33) com treino / validacao / teste nos 5 ativos.

Regra: VWAP diaria ancorada (reinicia 00:00 UTC, hlc3*volume); long quando EMA(close, ef) cruza
acima da VWAP, short (ou zera, se so comprado) quando cruza abaixo. Execucao na abertura da barra
seguinte, custo Lighter por perna + funding pro-rata (tvlib.equity).
Split por tempo do periodo de cada ativo: 60% treino, 20% validacao, 20% teste.
Escolha da celula: maior Sharpe no TREINO; aprovada se Sharpe da VALIDACAO > 1,0. Teste so reportado.
"""
import os, sys, numpy as np, pandas as pd
from tvlib import load_m1v, resample, xover, xunder, engine_bars, book, equity

TFS = ['30min', '1h', '4h']
EFS = [9, 20, 50, 100]
LADOS = ['long', 'ambos']
FILT = int(os.environ.get('FILT_SMA', '0'))  # 1: long so acima da SMA200, short so abaixo


def trades_target(L, S, up, dn, ambos):
    """alvo apos cada cruzamento; filtro bloqueia o lado contrario (zera). Execucao na barra seguinte."""
    tr = []; pos = 0; i0 = None
    for i in np.where(L | S)[0]:
        j = i + 1
        if j >= len(L): break
        tgt = (1 if up[i] else 0) if L[i] else ((-1 if ambos else 0) if dn[i] else 0)
        if tgt == pos: continue
        if pos != 0: tr.append((i0, j, pos))
        pos, i0 = tgt, j
    return tr


def vwap_day(df):
    pv = (df.high + df.low + df.close) / 3 * df.volume
    g = df.index.floor('1D')
    return pv.groupby(g).cumsum() / df.volume.groupby(g).cumsum().replace(0, np.nan)


def bh(df):
    r = np.log(df.close).diff().fillna(0); d = r.resample('1D').sum(); d = d[d != 0]
    return float(d.mean() / d.std() * np.sqrt(252)), float(np.expm1(r.sum()))


def run(name):
    m1 = load_m1v(name)
    t0, t1 = m1.index[0], m1.index[-1]
    c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
    per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
    rows = []
    for tf in TFS:
        df = resample(m1, tf)
        vw = vwap_day(df).to_numpy(float)
        up = (df.close > df.close.rolling(200).mean()).to_numpy()
        for ef in EFS:
            e = df.close.ewm(span=ef, adjust=False).mean().to_numpy(float)
            L, S = xover(e, vw), xunder(e, vw)
            for lado in LADOS:
                r = dict(ativo=name, tf=tf, ef=ef, lado=lado)
                for p, (a, b) in per.items():
                    sub = df[(df.index >= a) & (df.index < b)]
                    k0 = df.index.searchsorted(a); k1 = k0 + len(sub)
                    if FILT:
                        tr = trades_target(L[k0:k1], S[k0:k1], up[k0:k1], ~up[k0:k1], lado == 'ambos')
                    else:
                        tr = engine_bars(sub, L[k0:k1], S[k0:k1], short_ok=(lado == 'ambos'),
                                         flat_on_opp=(lado == 'long'))
                    if len(tr) < 5:
                        r.update({f'{p}_sh': np.nan, f'{p}_cagr': np.nan, f'{p}_dd': np.nan, f'{p}_n': len(tr)}); continue
                    q = equity(sub, book(sub, tr, name), name)
                    r.update({f'{p}_sh': round(q['sharpe'], 2), f'{p}_cagr': round(q['cagr'] * 100, 1),
                              f'{p}_dd': round(q['dd'] * 100, 1), f'{p}_n': len(tr)})
                rows.append(r)
    g = pd.DataFrame(rows)
    d4 = resample(m1, '4h')
    info = {p: bh(d4[(d4.index >= a) & (d4.index < b)]) for p, (a, b) in per.items()}
    return g, per, info


if __name__ == '__main__':
    allg, res = [], []
    for a in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
        g, per, info = run(a); allg.append(g)
        best = g.sort_values('treino_sh', ascending=False).iloc[0]
        res.append(dict(ativo=a, celula=f"{best.tf} ema{best.ef} {best.lado}",
                        treino=f"{per['treino'][0].date()}..{per['treino'][1].date()}",
                        valid=f"{per['valid'][0].date()}..{per['valid'][1].date()}",
                        teste=f"{per['teste'][0].date()}..{per['teste'][1].date()}",
                        **{k: best[k] for k in best.index if '_' in k},
                        bh_sh_val=round(info['valid'][0], 2), bh_sh_teste=round(info['teste'][0], 2),
                        aprovada=bool(best.valid_sh > 1.0),
                        celulas_val_gt1=int((g.valid_sh > 1.0).sum()), n_cel=len(g)))
        print(res[-1], flush=True)
    pd.concat(allg).to_csv(f'../results/vxe_tvt{"_sma" if FILT else ""}_grade.csv', index=False)
    pd.DataFrame(res).to_csv(f'../results/vxe_tvt{"_sma" if FILT else ""}_resumo.csv', index=False)
    print(pd.DataFrame(res).to_string(index=False))
