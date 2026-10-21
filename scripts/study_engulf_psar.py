"""Engolfo + Parabolic SAR em indices, candles de 15m ou agregados (Dukascopy bid 15m, 2017-01 .. 2026-09).

Regra: o candle t engole o corpo do candle t-1 com cor oposta
  alta : t-1 vermelho, t verde, O_t <= C_{t-1}, C_t >= O_{t-1}, corpo_t > corpo_{t-1}  -> long
  baixa: t-1 verde, t vermelho, O_t >= C_{t-1}, C_t <= O_{t-1}, corpo_t > corpo_{t-1}  -> short
Entra no fechamento de t. Stop inicial na minima (long) / maxima (short) do engolfo. Trailing = Parabolic SAR.
Uma posicao por vez; sinais com posicao aberta sao ignorados. O stop de cada barra so usa informacao ate a barra anterior.
  sar=grafico : SAR continuo do grafico; o stop sobe para o SAR quando ele esta do lado certo do preco (nunca desce).
  sar=entrada : SAR de Wilder iniciado na entrada: SAR0 = minima do engolfo, EP = maxima do engolfo, AF = af0.
Stop executado no nivel, ou na abertura se a barra abrir alem dele. Custo por perna CUSTO (spread medido na Lighter, ~$1k).
Dados: indices/WTI = Dukascopy bid 15m 2017+; xau = Dukascopy bid 15m; btc = Binance BTCUSDT 15m 2020+.
Controle: entradas aleatorias (mesma densidade, direcao sorteada, stop na minima/maxima da barra) com a mesma saida.

uso: python study_engulf_psar.py [--tf 1h] [us500 us100 us30 us2000 xau wti btc]   (tf: 15min, 30min, 1h, 4h ...)
"""
import os, sys, glob
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
CUSTO = {'us500': 1.2e-4, 'us100': 1.2e-4, 'us30': 1.2e-4, 'us2000': 1.2e-4, 'xau': 0.75e-4, 'wti': 1.0e-4, 'btc': 0.5e-4}
FUND = {'us500': 3.1, 'us100': 4.5, 'us30': 8.4, 'us2000': 8.4, 'xau': 13.8, 'wti': 67.7, 'btc': 10.9}  # funding anual medio que o long paga na Lighter (%)


def load15(name):
    if name == 'btc':
        b = pd.read_parquet(os.path.join(D, 'data', 'binance', 'klines_15m', 'BTCUSDT.parquet'))
        return b.set_index(pd.to_datetime(b.ts, unit='ms', utc=True))[['o', 'h', 'l', 'c', 'v']].set_axis(
            ['open', 'high', 'low', 'close', 'volume'], axis=1)
    if name == 'xau':
        sys.path.insert(0, os.path.join(D, 'scripts'))
        from study_gold_box import load_duka
        x = load_duka()
        return x[x.index >= '2017-01-01']  # antes de 2017 so ha um mes solto de 2005
    fs = sorted(glob.glob(os.path.join(D, 'data', f'duka_{name}', '*.parquet')))
    return pd.concat([pd.read_parquet(f) for f in fs if os.path.getsize(f) > 0])


def load(name, tf='15min'):
    df = load15(name)
    df = df[~df.index.duplicated()].sort_index()
    df = df[df.high > df.low]
    if tf != '15min':
        df = df.resample(tf, label='left', closed='left').agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()
        df = df[df.high > df.low]
    return df


def engulf(o, c):
    o1, c1 = np.roll(o, 1), np.roll(c, 1)
    body, body1 = np.abs(c - o), np.abs(c1 - o1)
    bull = (c1 < o1) & (c > o) & (o <= c1) & (c >= o1) & (body > body1)
    bear = (c1 > o1) & (c < o) & (o >= c1) & (c <= o1) & (body > body1)
    s = bull.astype(int) - bear.astype(int); s[0] = 0
    return s


def psar(h, l, a0=0.02, inc=0.02, mx=0.2):
    """sar[i] = nivel valido durante a barra i (calculado ate i-1); up[i] = SAR abaixo do preco."""
    n = len(h); sar = np.full(n, np.nan); up = np.zeros(n, bool)
    trend, ep, af, nxt = True, h[0], a0, l[0]
    for i in range(1, n):
        sar[i], up[i] = nxt, trend
        if trend:
            if l[i] <= nxt:
                trend, s, ep, af = False, max(h[i], ep), l[i], a0
                nxt = max(s + af * (ep - s), h[i], h[i - 1])
            else:
                if h[i] > ep: ep, af = h[i], min(af + inc, mx)
                nxt = min(nxt + af * (ep - nxt), l[i], l[i - 1])
        else:
            if h[i] >= nxt:
                trend, s, ep, af = True, min(l[i], ep), h[i], a0
                nxt = min(s + af * (ep - s), l[i], l[i - 1])
            else:
                if l[i] < ep: ep, af = l[i], min(af + inc, mx)
                nxt = max(nxt + af * (ep - nxt), h[i], h[i - 1])
    return sar, up


def backtest(o, h, l, c, sig, mode, sar, up, p=(0.02, 0.02, 0.2), dist=None):
    """dist: distancia do stop inicial por barra (controle); None = minima/maxima do candle de sinal."""
    a0, inc, mx = p
    n = len(c); out = []; i = 1
    while i < n - 1:
        d = sig[i]
        if d == 0: i += 1; continue
        entry = c[i]; stop = (l[i] if d > 0 else h[i]) if dist is None else entry - d * dist[i]; R = abs(entry - stop)
        if R <= 0: i += 1; continue
        ws, ep, af = stop, (h[i] if d > 0 else l[i]), a0
        j = i + 1; px = None
        while j < n:
            if mode == 'grafico':
                if d > 0 and up[j]: stop = max(stop, sar[j])
                elif d < 0 and not up[j]: stop = min(stop, sar[j])
            else:
                stop = ws
            if d > 0 and l[j] <= stop: px = min(o[j], stop); break
            if d < 0 and h[j] >= stop: px = max(o[j], stop); break
            if mode == 'entrada':
                if d > 0:
                    if h[j] > ep: ep, af = h[j], min(af + inc, mx)
                    ws = min(ws + af * (ep - ws), l[j], l[j - 1])
                else:
                    if l[j] < ep: ep, af = l[j], min(af + inc, mx)
                    ws = max(ws + af * (ep - ws), h[j], h[j - 1])
            j += 1
        if px is None: break
        out.append((i, j, d, entry, px, R))
        i = j
    return out


def trades_df(tr, idx, name):
    t = pd.DataFrame(tr, columns=['i', 'j', 'd', 'entry', 'exit', 'R'])
    t['t_in'], t['t_out'] = idx[t.i], idx[t.j]
    t['bars'] = t.j - t.i
    t['custo'] = CUSTO[name]
    fund = FUND.get(name, 5.0) / 100 * (t.t_out - t.t_in).dt.total_seconds() / (365 * 86400) * t.d  # long paga, short recebe
    t['ret_bruto'] = t.d * (t.exit / t.entry - 1)
    t['ret'] = t.ret_bruto - 2 * t.custo - fund
    t['R_bruto'] = t.d * (t.exit - t.entry) / t.R
    t['R_liq'] = t.ret * t.entry / t.R
    t['stop_bp'] = t.R / t.entry * 1e4
    return t


def stats(t):
    if len(t) == 0: return {}
    yrs = (t.t_out.iloc[-1] - t.t_in.iloc[0]).days / 365.25
    day = t.groupby(t.t_out.dt.floor('D')).ret.sum()
    day = day.reindex(pd.date_range(day.index[0], day.index[-1], freq='B'), fill_value=0)
    eq = t.ret.cumsum()
    gp, gl = t.ret[t.ret > 0].sum(), -t.ret[t.ret < 0].sum()
    return {'trades': len(t), 'tr_ano': len(t) / yrs, 'acerto': (t.ret > 0).mean(), 'stop_bp': t.stop_bp.median(),
            'R_bruto': t.R_bruto.mean(), 't_bruto': t.R_bruto.mean() / t.R_bruto.std() * np.sqrt(len(t)),
            'bp_bruto': t.ret_bruto.mean() * 1e4, 'R_liq': t.R_liq.mean(), 'bp_liq': t.ret.mean() * 1e4, 'PF': gp / gl if gl else np.nan,
            'barras': t.bars.median(), 'ret_ano%': t.ret.sum() / yrs * 100, 'sharpe': day.mean() / day.std() * np.sqrt(252),
            'maxDD%': (eq - eq.cummax()).min() * 100, 'R_ano': t.R_liq.sum() / yrs}


def main(names, tf):
    tfmin = pd.Timedelta(tf).total_seconds() / 60
    rows, years, ctrl, sizes = [], [], [], []
    for name in names:
        df = load(name, tf)
        o, h, l, c = (df[k].to_numpy() for k in ('open', 'high', 'low', 'close'))
        idx = df.index
        et = idx.tz_convert('America/New_York'); mins = et.hour * 60 + et.minute
        ny = np.asarray((mins + tfmin > 9 * 60 + 30) & (mins < 16 * 60))  # candle que cruza o pregao a vista de NY
        sig = engulf(o, c)
        sar, up = psar(h, l)
        for sess, s in (('24h', sig), ('NY', np.where(ny, sig, 0))):
            for mode in ('grafico', 'entrada'):
                t = trades_df(backtest(o, h, l, c, s, mode, sar, up), idx, name)
                for lado, tt in (('L+S', t), ('long', t[t.d > 0]), ('short', t[t.d < 0])):
                    rows.append({'ativo': name, 'sessao': sess, 'sar': mode, 'lado': lado, **stats(tt)})
                y = t.groupby(t.t_in.dt.year).agg(n=('ret', 'size'), R_liq=('R_liq', 'mean'), ret=('ret', 'sum'))
                y['ret'] *= 100
                years.append(y.assign(ativo=name, sessao=sess, sar=mode).reset_index())
                if mode == 'grafico':
                    q = pd.qcut(t.stop_bp, 5)
                    sz = t.groupby(q, observed=True).agg(n=('ret', 'size'), R_bruto=('R_bruto', 'mean'), R_liq=('R_liq', 'mean'),
                                                         bp_bruto=('ret_bruto', lambda x: x.mean() * 1e4))
                    sizes.append(sz.assign(ativo=name, sessao=sess).reset_index())
            # controle: entradas aleatorias com a mesma densidade de sinais, direcao sorteada, stop a 1 range do candle (piso 2bp)
            dens = (s != 0).mean(); rng = np.random.default_rng(7)
            for mode in ('grafico', 'entrada'):
                for rep in range(20):
                    rs = np.where(rng.random(len(c)) < dens, rng.choice([-1, 1], len(c)), 0)
                    if sess == 'NY': rs = np.where(ny, rs, 0)
                    st = stats(trades_df(backtest(o, h, l, c, rs, mode, sar, up, dist=np.maximum(h - l, 2e-4 * c)), idx, name))
                    ctrl.append({'ativo': name, 'sessao': sess, 'sar': mode, 'rep': rep, 'R_liq': st['R_liq'],
                                 'R_bruto': st['R_bruto'], 'bp_bruto': st['bp_bruto'], 'ret_ano%': st['ret_ano%']})
        # sensibilidade do SAR (24h e NY, SAR do grafico)
        for p in ((0.01, 0.01, 0.1), (0.02, 0.02, 0.2), (0.04, 0.04, 0.4)):
            sp, upp = psar(h, l, *p)
            for sess, s in (('24h', sig), ('NY', np.where(ny, sig, 0))):
                for mode in ('grafico', 'entrada'):
                    st = stats(trades_df(backtest(o, h, l, c, s, mode, sp, upp, p), idx, name))
                    rows.append({'ativo': name, 'sessao': sess, 'sar': f'{mode} {p[0]}/{p[2]}', 'lado': 'sens', **st})
        print(f'{name}: {len(df)} barras {idx[0]:%Y-%m-%d} .. {idx[-1]:%Y-%m-%d}', flush=True)

    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    r = pd.DataFrame(rows)
    fmt = {'tr_ano': 0, 'acerto': 3, 'stop_bp': 1, 'R_bruto': 3, 't_bruto': 1, 'bp_bruto': 2, 'R_liq': 3, 'bp_liq': 2, 'PF': 2, 'barras': 0,
           'ret_ano%': 1, 'sharpe': 2, 'maxDD%': 1, 'R_ano': 1}
    r = r.round(fmt)
    print(f'\n== ENGOLFO + PSAR, {tf}, custo/perna (bp) { {k: v * 1e4 for k, v in CUSTO.items() if k in names} } ==')
    print(r[r.lado != 'sens'].to_string(index=False))
    print('\n== sensibilidade do SAR (L+S) ==')
    print(r[r.lado == 'sens'].drop(columns='lado').to_string(index=False))
    cc = pd.DataFrame(ctrl).groupby(['ativo', 'sessao', 'sar']).agg(
        R_bruto_med=('R_bruto', 'mean'), R_bruto_p5=('R_bruto', lambda x: x.quantile(.05)), R_bruto_p95=('R_bruto', lambda x: x.quantile(.95)),
        bp_bruto_med=('bp_bruto', 'mean'), R_liq_med=('R_liq', 'mean'), ret_ano_med=('ret_ano%', 'mean')).round(3)
    print('\n== controle: entradas aleatorias, mesma saida (20 sorteios) ==')
    print(cc.to_string())
    print('\n== por tamanho do engolfo (quintis do stop em bp, SAR do grafico) ==')
    print(pd.concat(sizes).round(3).to_string(index=False))
    y = pd.concat(years)
    print('\n== por ano (L+S): R liquido medio por trade / retorno % no ano (1x nocional) ==')
    print(y.pivot_table(index=['ativo', 'sessao', 'sar'], columns='t_in', values='R_liq').round(2).to_string())
    print(y.pivot_table(index=['ativo', 'sessao', 'sar'], columns='t_in', values='ret').round(1).to_string())
    r.to_csv(os.path.join(D, 'scripts', f'study_engulf_psar_{tf}_{"-".join(names)}.csv'), index=False)


if __name__ == '__main__':
    a = sys.argv[1:]; tf = '15min'
    if '--tf' in a: k = a.index('--tf'); tf = a[k + 1]; del a[k:k + 2]
    main(a or ['us500'], tf)
