"""Carteira de 5 componentes: (BTC ou ETH), (US100 ou US500), (WTI ou BRENT), XAU, XAG. Peso 1/5, 4h, 24/7.
Em cada par entra o ativo com tendencia previa mais forte: forca = |media de log(close/MA)| sobre as MAs do conjunto,
dividida pela vol de 20 dias (medida no fechamento da barra, vale na barra seguinte). Direcao = media dos sinais (+1/-1)
das MAs (como em study_ma_vol_ens). Metade da posicao quando a vol da carteira passa de X. Comparado com a escolha fixa
(BTC, US100, WTI, XAU, XAG) e com a carteira de 8 completa."""
import numpy as np, pandas as pd
import study_ma_vol_ens8 as E8, study_ma_vol_cart as S
from study_ma_vol_ens import SETS
from study_engulf_psar import CUSTO, FUND
GR = [('btc', 'eth'), ('us100', 'us500'), ('wti', 'brent'), ('xau',), ('xag',)]
AT = [a for g in GR for a in g]


def run(m1s, modo):
    S.AT = AT; bars, idx, dt, t0, t1 = S.prep('4h', m1s)
    c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
    per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
    ro = {a: np.log(b.open.shift(-1) / b.open).fillna(0.0).reindex(idx).fillna(0.0) for a, b in bars.items()}
    rows, curvas = [], {}
    for nome, cj in SETS.items():
        sig, frc = {}, {}
        for a, b in bars.items():
            c = b.close; sg, dist = [], []
            for t, n in cj:
                ma = c.rolling(n).mean() if t == 'SMA' else c.ewm(span=n, adjust=False).mean()
                sg.append(np.sign(c - ma)); dist.append(np.log(c / ma))
            vol = np.log(c).diff().rolling(120).std()
            s = pd.concat(sg, axis=1).mean(axis=1); f = pd.concat(dist, axis=1).mean(axis=1).abs() / vol
            ok = c.rolling(max(n for _, n in cj)).count() > 0
            sig[a] = s.where(ok, 0.0).shift(1).reindex(idx).ffill().fillna(0.0)
            frc[a] = f.where(ok).shift(1).reindex(idx).ffill().fillna(0.0)
        pos = {a: 0.0 * ro[a] for a in AT}; esc = {}
        for g in GR:
            if modo == 'fixo' or len(g) == 1: k = g[0]; pos[k] = sig[k] / 5; continue
            pick = frc[g[0]] >= frc[g[1]]; esc[g[0]] = float(pick.mean())
            pos[g[0]] = sig[g[0]].where(pick, 0.0) / 5; pos[g[1]] = sig[g[1]].where(~pick, 0.0) / 5
        dly = sum(pos[a] * ro[a] for a in AT).resample('1D').sum()
        vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1); pct = vol.rolling(252, min_periods=126).rank(pct=True)
        for kind, x in S.FILT:
            wd = 1.0 if kind == 'nenhum' else np.where((vol if kind == 'abs' else pct) > x, 0.5, 1.0)
            w = pd.Series(wd, dly.index).reindex(idx.normalize()).to_numpy(); w = pd.Series(np.nan_to_num(w, nan=1.0), idx)
            r_sf = 0.0; fund = 0.0
            for a in AT:
                q = pos[a] * w
                r_sf = r_sf + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a]
                fund = fund + q * FUND[a] / 100 * dt * (ro[a] != 0)
            r = r_sf - fund; curvas[(nome, kind, x)] = r
            row = dict(modo=modo, conjunto=nome, filtro=kind, x=x, frac_btc=esc.get('btc'), frac_us100=esc.get('us100'), frac_wti=esc.get('wti'))
            for p, (xa, xb) in per.items():
                m = (idx >= xa) & (idx < xb); s, s0 = S.stats(r[m], w[m]), S.stats(r_sf[m], w[m])
                row.update({f'{p}_sh': round(s['sh'], 2), f'{p}_cagr': round(s['cagr'], 1), f'{p}_dd': round(s['dd'], 1), f'{p}_sh_sf': round(s0['sh'], 2)})
            rows.append(row)
    return pd.DataFrame(rows), curvas, idx, t0, t1


if __name__ == '__main__':
    m1s = {a: E8.load(a) for a in AT}
    out = []
    for modo in ('forca', 'fixo'):
        g, cv, idx, t0, t1 = run(m1s, modo); out.append(g)
        b = g.sort_values('treino_sh', ascending=False).iloc[0]
        m = (idx >= t0) & (idx <= t1); eq = np.exp(cv[(b.conjunto, b.filtro, b.x)][m].cumsum())
        print(modo, b.conjunto, b.filtro, b.x, b[['treino_sh', 'valid_sh', 'teste_sh', 'valid_sh_sf', 'teste_sh_sf', 'treino_dd', 'valid_dd', 'teste_dd', 'valid_cagr', 'teste_cagr', 'frac_btc', 'frac_us100', 'frac_wti']].tolist(),
              'val', g.valid_sh.min(), g.valid_sh.median(), g.valid_sh.max(), 'teste', g.teste_sh.min(), g.teste_sh.median(), g.teste_sh.max(),
              'curva', round(eq.iloc[-1], 2), round(((eq / eq.cummax()) - 1).min() * 100), flush=True)
    pd.concat(out).to_csv('../results/ma_vol_sel_grade.csv', index=False)
