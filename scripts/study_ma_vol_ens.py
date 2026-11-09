"""Carteira com VARIAS medias: posicao de cada ativo = media dos sinais (+1/-1) de um conjunto de MAs, peso 1/N.
Metade da posicao quando a vol da carteira (20d, ate o dia anterior) passa de X. So 4h. Carteiras de 5 e de 6 (com XAG).
Mesmos custos/split de study_ma_vol_cart. Conjuntos poucos e fixados antes, para reduzir a escolha no treino."""
import itertools, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import study_ma_vol_cart6  # registra xag
import study_ma_vol_cart as S
from study_engulf_psar import CUSTO, FUND
SETS = {'SMA+EMA 100-300': [(t, n) for t in ('SMA', 'EMA') for n in (100, 150, 200, 250, 300)],
        'SMA+EMA 75-400': [(t, n) for t in ('SMA', 'EMA') for n in S.MAS],
        'EMA 75-400': [('EMA', n) for n in S.MAS], 'SMA 75-400': [('SMA', n) for n in S.MAS]}
FILT = S.FILT


def run(AT, m1s):
    S.AT = AT; N = len(AT)
    bars, idx, dt, t0, t1 = S.prep('4h', {a: m1s[a] for a in AT})
    c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
    per = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
    ro = {a: np.log(b.open.shift(-1) / b.open).fillna(0.0).reindex(idx).fillna(0.0) for a, b in bars.items()}
    bh = sum((ro[a] - FUND[a] / 100 * dt * (ro[a] != 0)) / N for a in AT)
    rows, curvas = [], {}
    for nome, cj in SETS.items():
        pos = {}
        for a, b in bars.items():
            c = b.close; sg = []
            for t, n in cj:
                ma = c.rolling(n).mean() if t == 'SMA' else c.ewm(span=n, adjust=False).mean()
                sg.append(np.sign(c - ma).where(ma.notna(), np.nan))
            s = pd.concat(sg, axis=1).mean(axis=1).where(c.rolling(max(n for _, n in cj)).count() > 0, 0.0).fillna(0.0)
            pos[a] = s.shift(1).fillna(0.0).reindex(idx).ffill().fillna(0.0) / N
        dly = sum(pos[a] * ro[a] for a in AT).resample('1D').sum()
        vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1)
        pct = vol.rolling(252, min_periods=126).rank(pct=True)
        for kind, x in FILT:
            wd = 1.0 if kind == 'nenhum' else np.where((vol if kind == 'abs' else pct) > x, 0.5, 1.0)
            w = pd.Series(wd, dly.index).reindex(idx.normalize()).to_numpy(); w = pd.Series(np.nan_to_num(w, nan=1.0), idx)
            r_sf = 0.0; fund = 0.0
            for a in AT:
                q = pos[a] * w
                r_sf = r_sf + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a]
                fund = fund + q * FUND[a] / 100 * dt * (ro[a] != 0)
            r = r_sf - fund; curvas[(nome, kind, x)] = r
            row = dict(carteira=N, conjunto=nome, filtro=kind, x=x)
            for p, (xa, xb) in per.items():
                m = (idx >= xa) & (idx < xb)
                s, s0 = S.stats(r[m], w[m]), S.stats(r_sf[m], w[m])
                row.update({f'{p}_sh': round(s['sh'], 2), f'{p}_cagr': round(s['cagr'], 1), f'{p}_dd': round(s['dd'], 1),
                            f'{p}_sh_sf': round(s0['sh'], 2), f'bh_{p}': round(S.sharpe(bh[m]), 2)})
            rows.append(row)
    return pd.DataFrame(rows), curvas, ro, idx, t0, t1


if __name__ == '__main__':
    A6 = ['xau', 'us100', 'wti', 'btc', 'eth', 'xag']
    m1s = {a: S.load_m1v(a) for a in A6}
    out = []
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))
    for ax, AT in zip(axs, (A6[:5], A6)):
        g, cv, ro, idx, t0, t1 = run(AT, m1s); out.append(g)
        b = g.sort_values('treino_sh', ascending=False).iloc[0]
        m = (idx >= t0) & (idx <= t1); N = len(AT)
        dd = lambda s: (s / s.cummax() - 1).min() * 100
        eb = np.exp((sum(ro[a] for a in AT) / N)[m].cumsum())
        eq = np.exp(cv[(b.conjunto, b.filtro, b.x)][m].cumsum())
        e0 = np.exp(cv[(b.conjunto, 'nenhum', None)][m].cumsum())
        ax.plot(eb.index, eb, 'k--', lw=1.4, label=f'Carteira B&H 1/{N} (x{eb.iloc[-1]:.2f}, DD {dd(eb):.0f}%)')
        ax.plot(e0.index, e0, color='#4c78a8', lw=1.4, label=f'{b.conjunto}, sem filtro (x{e0.iloc[-1]:.2f}, DD {dd(e0):.0f}%)')
        ax.plot(eq.index, eq, color='#d62728', lw=2.4, label=f'{b.conjunto}, filtro {b.filtro} {b.x} (x{eq.iloc[-1]:.2f}, DD {dd(eq):.0f}%)')
        for f in (0.6, 0.8): ax.axvline(t0 + (t1 - t0) * f, color='gray', ls=':')
        ax.set_yscale('log'); ax.grid(alpha=.3); ax.legend(loc='upper left', fontsize=9)
        ax.set_title(f'Carteira de {N} ativos, 4h, várias médias (escolhida pelo treino; linhas: fim do treino e da validação)')
    fig.tight_layout(); fig.savefig('../results/ma_vol_ens_curva.png', dpi=130)
    g = pd.concat(out); g.to_csv('../results/ma_vol_ens_grade.csv', index=False)
    pd.set_option('display.width', 250)
    print(g[['carteira', 'conjunto', 'filtro', 'x', 'treino_sh', 'valid_sh', 'teste_sh', 'valid_sh_sf', 'teste_sh_sf', 'treino_dd', 'valid_dd', 'teste_dd', 'valid_cagr', 'teste_cagr', 'bh_treino', 'bh_valid', 'bh_teste']].to_string(index=False))
