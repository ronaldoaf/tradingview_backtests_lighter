"""Carteira de 4 componentes (BTC|ETH, US100|US500, WTI|BRENT, XAU|XAG), 4h, 24/7 - melhorias:
 1) pesos: 'igual' (1/4) ou 'ivol' (inverso da vol de ~20d do ativo escolhido, normalizado para somar 1);
 2) dimensionamento: filtro antigo (metade acima de X) ou vol-alvo da carteira: escala = min(alvo / vol_20d, teto),
    teto 1 (sem alavancar acima do bruto 1x) ou 2;
 3) controle aleatorio: em cada par o ativo e sorteado (cadeia com a MESMA frequencia de trocas da escolha real),
    50 sorteios, mesma regra/custos da celula escolhida.
Escolha da celula pelo Sharpe do treino; custos Lighter + funding como em study_ma_vol_sel."""
import sys, numpy as np, pandas as pd
import study_ma_vol_ens8 as E8, study_ma_vol_cart as S
from study_ma_vol_ens import SETS
from study_engulf_psar import CUSTO, FUND
GR = [('btc', 'eth'), ('us100', 'us500'), ('wti', 'brent'), ('xau', 'xag')]
AT = [a for g in GR for a in g]
FILT = S.FILT + [(f'alvo{t}', x) for t in (1, 2) for x in (0.08, 0.10, 0.12, 0.15, 0.20)]
RNG = np.random.default_rng(7)

S.AT = AT
m1s = {a: E8.load(a) for a in AT}
bars, idx, dt, t0, t1 = S.prep('4h', m1s)
c1, c2 = t0 + (t1 - t0) * 0.6, t0 + (t1 - t0) * 0.8
PER = {'treino': (t0, c1), 'valid': (c1, c2), 'teste': (c2, t1)}
ro = {a: np.log(b.open.shift(-1) / b.open).fillna(0.0).reindex(idx).fillna(0.0) for a, b in bars.items()}
avol = {a: np.log(b.close).diff().rolling(120).std().shift(1).reindex(idx).ffill() for a, b in bars.items()}


def sinais(cj):
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
    return sig, frc


def aleat(pick):
    p = pick.to_numpy(); q = (p[1:] != p[:-1]).mean(); fr = p.mean()
    out = np.empty(len(p), bool); out[0] = RNG.random() < fr
    flips = RNG.random(len(p)) < q
    for i in range(1, len(p)):
        out[i] = (not out[i - 1]) if flips[i] else out[i - 1]
    return pd.Series(out, pick.index)


def carteira(sig, frc, peso, kind, x, rand=False):
    pos = {a: 0.0 * ro[a] for a in AT}; raw, vv = {}, {}
    for g in GR:
        pick = frc[g[0]] >= frc[g[1]]
        if rand: pick = aleat(pick)
        for a, m in ((g[0], pick), (g[1], ~pick)):
            raw[a] = sig[a].where(m, 0.0); vv[a] = avol[a].where(m)
    if peso == 'igual':
        w = {a: 0.25 for a in AT}
    else:
        inv = {g: (1 / vv[g[0]]).fillna(1 / vv[g[1]]) for g in GR}; tot = sum(inv.values())
        w = {}
        for g in GR:
            for a in g: w[a] = (inv[g] / tot).fillna(0.25)
    pos = {a: raw[a] * w[a] for a in AT}
    dly = sum(pos[a] * ro[a] for a in AT).resample('1D').sum()
    vol = (dly.rolling(20).std() * np.sqrt(252)).shift(1); pct = vol.rolling(252, min_periods=126).rank(pct=True)
    if kind == 'nenhum': wd = 1.0
    elif kind == 'abs': wd = np.where(vol > x, 0.5, 1.0)
    elif kind == 'pct': wd = np.where(pct > x, 0.5, 1.0)
    else: wd = np.clip(x / vol, 0, float(kind[-1])).fillna(1.0)
    k = pd.Series(wd, dly.index).reindex(idx.normalize()).to_numpy(); k = pd.Series(np.nan_to_num(k, nan=1.0), idx)
    r_sf = 0.0; fund = 0.0; gross = 0.0
    for a in AT:
        q = pos[a] * k
        r_sf = r_sf + q * ro[a] - q.diff().abs().fillna(q.abs()) * CUSTO[a]
        fund = fund + q * FUND[a] / 100 * dt * (ro[a] != 0); gross = gross + q.abs()
    return r_sf - fund, r_sf, gross


def mets(r, r_sf, gross):
    row = {}
    for p, (xa, xb) in PER.items():
        m = (idx >= xa) & (idx < xb); s, s0 = S.stats(r[m], gross[m]), S.stats(r_sf[m], gross[m])
        row.update({f'{p}_sh': round(s['sh'], 2), f'{p}_cagr': round(s['cagr'], 1), f'{p}_dd': round(s['dd'], 1),
                    f'{p}_sh_sf': round(s0['sh'], 2), f'{p}_bruto': round(s['escala'], 2)})
    return row


if __name__ == '__main__':
    rows, cache = [], {}
    for nome, cj in SETS.items():
        cache[nome] = sinais(cj)
        for peso in ('igual', 'ivol'):
            for kind, x in FILT:
                r, r_sf, gr = carteira(*cache[nome], peso, kind, x)
                rows.append(dict(conjunto=nome, peso=peso, filtro=kind, x=x, **mets(r, r_sf, gr)))
    g = pd.DataFrame(rows); g.to_csv('../results/ma_vol_sel4_v2_grade.csv', index=False)
    pd.set_option('display.width', 250)
    cols = ['treino_sh', 'valid_sh', 'teste_sh', 'valid_sh_sf', 'teste_sh_sf', 'treino_dd', 'valid_dd', 'teste_dd', 'valid_cagr', 'teste_cagr', 'teste_bruto']
    g['fam'] = g.peso + '/' + g.filtro.str.replace(r'\d', '', regex=True).where(~g.filtro.str.startswith('alvo'), g.filtro)
    for fam, h in g.groupby('fam'):
        b = h.sort_values('treino_sh', ascending=False).iloc[0]
        print(f'{fam:16s} {b.conjunto:16s} {b.filtro} {b.x}', b[cols].tolist(), 'med val/teste', h.valid_sh.median(), h.teste_sh.median(), 'min', h.valid_sh.min(), h.teste_sh.min())
    b = g.sort_values('treino_sh', ascending=False).iloc[0]
    print('GERAL', b.conjunto, b.peso, b.filtro, b.x, b[cols].tolist())
    # controle aleatorio nas duas celulas de referencia
    ref = [('SMA+EMA 75-400', 'igual', 'abs', 0.20), (b.conjunto, b.peso, b.filtro, b.x)]
    res = []
    for cj, peso, kind, x in ref:
        real = mets(*carteira(*cache[cj], peso, kind, x))
        sims = pd.DataFrame([mets(*carteira(*cache[cj], peso, kind, x, rand=True)) for _ in range(50)])
        for p in ('treino', 'valid', 'teste'):
            res.append(dict(celula=f'{cj} {peso} {kind} {x}', periodo=p, real=real[f'{p}_sh'], aleat_media=round(sims[f'{p}_sh'].mean(), 2),
                            aleat_p95=round(sims[f'{p}_sh'].quantile(.95), 2), pct_aleat_maior=round((sims[f'{p}_sh'] >= real[f'{p}_sh']).mean() * 100)))
    res = pd.DataFrame(res); res.to_csv('../results/ma_vol_sel4_aleat.csv', index=False); print(res.to_string(index=False))
