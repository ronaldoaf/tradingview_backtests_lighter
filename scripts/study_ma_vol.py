"""Tendencia por media longa com filtro de volatilidade, treino / validacao / teste nos 5 ativos.

Regra: posicao +1 com close > MA, -1 (ou 0 se so comprado) com close < MA. MA = SMA ou EMA de
75/100/150/200/250/300/400 barras. Filtro de vol: vol realizada (desvio dos log-retornos em ~20 dias)
comparada com o seu percentil no ultimo ~1 ano (janela movel, sem lookahead). Se o percentil
passar de X, a posicao vira metade ('meia') ou zero ('fora'). X em {0,7; 0,8; 0,9}; 'nenhum' = sem filtro.
Sinal no fechamento, execucao na abertura da barra seguinte. Retorno barra a barra (abertura->abertura),
custo CUSTO por unidade de mudanca de posicao, funding FUND pro-rata a posicao (long paga, short recebe).
Sharpe com retornos diarios de todos os dias com barra (dias fora contam como zero).
Split por tempo: 60/20/20. Celula escolhida pelo maior Sharpe do TREINO (com funding).
"""
import sys, itertools, numpy as np, pandas as pd
from tvlib import load_m1v, resample
from study_engulf_psar import CUSTO, FUND

TFS = {'1h': (480, 6048), '4h': (120, 1512), '1D': (20, 252)}  # (janela da vol, janela do percentil) em barras
MAS = [75, 100, 150, 200, 250, 300, 400]
FILT = [('nenhum', None)] + [(a, x) for a in ('meia', 'fora') for x in (0.7, 0.8, 0.9)]
LIM = 0.5


def stats(r, pos, idx):
    s = pd.Series(r, idx)
    d = s.resample('1D').sum()[s.resample('1D').count() > 0]
    yrs = (idx[-1] - idx[0]).total_seconds() / (365 * 86400)
    eq = s.cumsum()
    return dict(sh=float(d.mean() / d.std() * np.sqrt(252)) if d.std() > 0 else np.nan,
                cagr=float(np.expm1(eq.iloc[-1] / yrs)) * 100, dd=float((eq - eq.cummax()).min()) * 100,
                expo=float(np.abs(pos).mean()), giro=float(np.abs(np.diff(pos)).sum() / yrs))


def run(name):
    m1 = load_m1v(name)
    t0, t1 = m1.index[0], m1.index[-1]
    c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
    per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
    cst, f = CUSTO[name], FUND[name] / 100
    rows, bh = [], {}
    for tf, (wv, wp) in TFS.items():
        df = resample(m1, tf)
        o, c = df.open.to_numpy(float), df.close
        ro = np.append(np.log(o[1:] / o[:-1]), 0.0)          # retorno abertura t -> abertura t+1
        dt = np.append(np.diff(df.index.values).astype('timedelta64[s]').astype(float) / (365 * 86400), 0.0)
        lr = np.log(c).diff()
        vol = lr.rolling(wv).std()
        pct = vol.rolling(wp, min_periods=wp // 2).rank(pct=True).to_numpy()
        sl = {p: (df.index.searchsorted(a), df.index.searchsorted(b)) for p, (a, b) in per.items()}
        if tf == '1D':
            for p, (k0, k1) in sl.items():
                bh[p] = stats(ro[k0:k1] - f * dt[k0:k1], np.ones(k1 - k0), df.index[k0:k1])['sh']
        for tipo, n in itertools.product(('SMA', 'EMA'), MAS):
            ma = (c.rolling(n).mean() if tipo == 'SMA' else c.ewm(span=n, adjust=False).mean()).to_numpy()
            above = (c.to_numpy() > ma).astype(float)
            base = np.where(np.isnan(ma), np.nan, 2 * above - 1)
            for lado, (acao, x) in itertools.product(('long', 'ambos'), FILT):
                sig = base.copy()
                if lado == 'long': sig = np.where(sig < 0, 0.0, sig)
                if x is not None:
                    hi = np.nan_to_num(pct, nan=0.0) > x
                    sig = np.where(hi, sig * (0.5 if acao == 'meia' else 0.0), sig)
                sig = np.nan_to_num(sig)
                pos = np.append(0.0, sig[:-1])                    # sinal no fechamento -> posicao da barra seguinte
                chg = np.abs(np.diff(np.append(0.0, pos)))
                r_sf = pos * ro - chg * cst
                r = r_sf - pos * f * dt
                row = dict(ativo=name, tf=tf, ma=f'{tipo}{n}', lado=lado, filtro=acao, x=x)
                for p, (k0, k1) in sl.items():
                    a = stats(r[k0:k1], pos[k0:k1], df.index[k0:k1])
                    b = stats(r_sf[k0:k1], pos[k0:k1], df.index[k0:k1])
                    row.update({f'{p}_sh': round(a['sh'], 2), f'{p}_cagr': round(a['cagr'], 1),
                                f'{p}_dd': round(a['dd'], 1), f'{p}_sh_sf': round(b['sh'], 2),
                                f'{p}_cagr_sf': round(b['cagr'], 1), f'{p}_expo': round(a['expo'], 2),
                                f'{p}_giro': round(a['giro'], 1)})
                rows.append(row)
    return pd.DataFrame(rows), per, bh


if __name__ == '__main__':
    allg, res = [], []
    SUF = '_' + sys.argv[1] if len(sys.argv) == 2 else ''
    for a in (sys.argv[1:] or ['xau', 'us100', 'wti', 'btc', 'eth']):
        g, per, bh = run(a); allg.append(g)
        best = g.sort_values('treino_sh', ascending=False).iloc[0]
        b0 = g[g.filtro == 'nenhum'].sort_values('treino_sh', ascending=False).iloc[0]
        res.append(dict(ativo=a, celula=f"{best.tf} {best.ma} {best.lado} {best.filtro} {best.x}",
                        periodos='|'.join(f"{p}:{x.date()}..{y.date()}" for p, (x, y) in per.items()),
                        **{k: best[k] for k in best.index if k[:5] in ('trein', 'valid', 'teste')},
                        bh_sh_tr=round(bh['treino'], 2), bh_sh_val=round(bh['valid'], 2), bh_sh_teste=round(bh['teste'], 2),
                        sem_filtro=f"{b0.tf} {b0.ma} {b0.lado}", sf_val_sh=b0.valid_sh, sf_teste_sh=b0.teste_sh,
                        aprovada=bool(best.valid_sh > LIM),
                        pct_cel_val_gt=round(float((g.valid_sh > LIM).mean()) * 100, 0), n_cel=len(g)))
        print(res[-1], flush=True)
    pd.concat(allg).to_csv(f'../results/ma_vol_grade{SUF}.csv', index=False)
    pd.DataFrame(res).to_csv(f'../results/ma_vol_resumo{SUF}.csv', index=False)
    print(pd.DataFrame(res).to_string(index=False))
