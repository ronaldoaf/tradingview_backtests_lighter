"""Gold/Silver RSI + EMA162 (lote 21, lx4O1PPu) com treino / validacao / teste nos 5 ativos.

Regra (como escrito): long com close > EMA162 e RSI14 < 35; short com close < EMA162 e RSI14 > 35.
'corrigido': short com RSI14 > 65 (parece ser a intencao do autor). O exit do script nunca dispara,
entao so a entrada contraria inverte (ou zera, se so comprado). Execucao na abertura da barra seguinte,
custo Lighter por perna + funding pro-rata (tvlib.equity). Tambem roda sem funding para medir o efeito.
Split por tempo de cada ativo: 60% treino, 20% validacao, 20% teste.
Celula escolhida pelo maior Sharpe do TREINO (com funding, minimo 30 trades no treino); aprovada se Sharpe da VALIDACAO > 0,5.
"""
import sys, itertools, numpy as np, pandas as pd
import tvlib
from tvlib import load_m1v, resample, rsi_wilder, engine_bars, book, equity

TFS = ['15min', '30min', '1h', '4h']
VAR = ['escrito', 'corrigido']
LADOS = ['long', 'ambos']
LIM = 0.5


def bh(df):
    r = np.log(df.close).diff().fillna(0); d = r.resample('1D').sum(); d = d[d != 0]
    return float(d.mean() / d.std() * np.sqrt(252))


def run(name):
    m1 = load_m1v(name)
    t0, t1 = m1.index[0], m1.index[-1]
    c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
    per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
    f0 = tvlib.FUND.get(name, 5.0)
    rows = []
    for tf in TFS:
        df = resample(m1, tf)
        c = df.close.to_numpy(float)
        r_ = rsi_wilder(c, 14); e = df.close.ewm(span=162, adjust=False).mean().to_numpy(float)
        for var, lado in itertools.product(VAR, LADOS):
            L = (c > e) & (r_ < 35); S = (c < e) & (r_ > (65 if var == 'corrigido' else 35))
            L[:162] = S[:162] = False
            r = dict(ativo=name, tf=tf, var=var, lado=lado)
            for p, (a, b) in per.items():
                k0 = df.index.searchsorted(a); k1 = df.index.searchsorted(b)
                sub = df.iloc[k0:k1]
                tr = engine_bars(sub, L[k0:k1], S[k0:k1], short_ok=(lado == 'ambos'), flat_on_opp=(lado == 'long'))
                r[f'{p}_n'] = len(tr)
                if len(tr) < 5:
                    for k in ('sh', 'cagr', 'dd', 'sh_sf', 'cagr_sf'): r[f'{p}_{k}'] = np.nan
                    continue
                bk = book(sub, tr, name)
                q = equity(sub, bk, name)
                tvlib.FUND[name] = 0.0
                q0 = equity(sub, bk, name)
                tvlib.FUND[name] = f0
                r.update({f'{p}_sh': round(q['sharpe'], 2), f'{p}_cagr': round(q['cagr'] * 100, 1),
                          f'{p}_dd': round(q['dd'] * 100, 1), f'{p}_sh_sf': round(q0['sharpe'], 2),
                          f'{p}_cagr_sf': round(q0['cagr'] * 100, 1)})
            rows.append(r)
    g = pd.DataFrame(rows)
    d4 = resample(m1, '4h')
    info = {p: bh(d4[(d4.index >= a) & (d4.index < b)]) for p, (a, b) in per.items()}
    return g, per, info, f0


if __name__ == '__main__':
    allg, res = [], []
    for a in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
        g, per, info, f0 = run(a); allg.append(g)
        best = g[g.treino_n >= 30].dropna(subset=["treino_sh"]).sort_values('treino_sh', ascending=False).iloc[0]
        res.append(dict(ativo=a, fund_aa=f0, celula=f"{best.tf} {best["var"]} {best.lado}",
                        treino=f"{per['treino'][0].date()}..{per['treino'][1].date()}",
                        valid=f"{per['valid'][0].date()}..{per['valid'][1].date()}",
                        teste=f"{per['teste'][0].date()}..{per['teste'][1].date()}",
                        **{k: best[k] for k in best.index if '_' in k},
                        bh_sh_val=round(info['valid'], 2), bh_sh_teste=round(info['teste'], 2),
                        aprovada=bool(best.valid_sh > LIM),
                        celulas_val_gt=int((g.valid_sh > LIM).sum()), n_cel=len(g)))
        print(res[-1], flush=True)
    pd.concat(allg).to_csv('../results/gs_tvt_grade.csv', index=False)
    pd.DataFrame(res).to_csv('../results/gs_tvt_resumo.csv', index=False)
    print(pd.DataFrame(res).to_string(index=False))
