"""Matriz de correlacao entre todas as estrategias de docs/APROVADAS.md, so no periodo antes do OOS.
OOS = 2a metade usada na robustez (inicio por ativo em CORTE); cada estrategia so entra com os dias anteriores ao corte
do seu ativo, e cada par usa os dias em que as duas estao dentro do periodo (correlacao par a par).
Retorno diario: posicao marcada no 15m do proprio ativo (close a close), custo e funding no dia da saida.
uso: python study_aprovadas_corr.py  ->  results/study_aprovadas_corr.txt e _corr.csv"""
import os, sys
import numpy as np, pandas as pd
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote6 import M1
import study_tvlote4 as L4, study_tvlote7 as L7, study_tvlote12 as L12, study_tvlote13 as L13, study_tvlote17 as L17
import study_tvlote19 as L19, study_tvlote20 as L20, study_tvlote21 as L21, study_tvlote22 as L22
import study_tvlote23 as L23, study_tvlote24 as L24, study_tvlote25 as L25, study_tvlote26 as L26
import study_tvlote27 as L27, study_tvlote28 as L28, study_tvlote29 as L29, study_tvlote30 as L30
import study_tvlote31 as L31, study_tvlote32 as L32, study_tvlote33 as L33

CORTE = {'xau': '2022-11-22', 'wti': '2021-11-17', 'btc': '2023-05-17', 'eth': '2023-05-17'}


def ppst(n, df, mm):
    L, S = L4.ppst_signals(df, prd=5, F=2.0, Pd=10)
    return L4.run_bars(n, df, L, S, 'ppst')


# (rotulo, ativo, TF, funcao(nome, df, mm) -> (resumo, trades))
EST = [
    ('§1 Trailing SL XAU 30m', 'xau', '30min', lambda n, d, m: L7.run_tsl(n, d, '', None, False, val=2.0)),
    ('§2 RSI-MA ETH 15m', 'eth', '15min', lambda n, d, m: L12.run_rsima(n, d, m, '', rl=10, ml=50)),
    ('§3 Pivot ST ETH 15m', 'eth', '15min', ppst),
    ('§4a UT Bot ETH 30m', 'eth', '30min', lambda n, d, m: L13.run_ut(n, d, m, '', a=5.0, atr_n=11, shorts=True)),
    ('§4b Ichimoku ETH 15m', 'eth', '15min', lambda n, d, m: L13.run_ichi(n, d, m, '', ts=20, ks=60, sb=120, off=60)),
    ('§4c Scalping ETH 30m', 'eth', '30min', lambda n, d, m: L13.run_scalp(n, d, m, '', sma_len=25, ema_len=0)),
    ('§5 FTSMA ETH 30m', 'eth', '30min', lambda n, d, m: L17.run_ftsma(n, d, m, '', use_ft=True)),
    ('§6 ABCD BTC 1h', 'btc', '1h', lambda n, d, m: L19.run_abcd(n, d, m, '', sl=0.04, rr=5.0)),
    ('§7 Follow Line ETH 30m', 'eth', '30min', lambda n, d, m: L20.run_fline(n, d, m, '', ln=21, dev=1.0)),
    ('§8 MA Consec ETH 4h', 'eth', '4h', lambda n, d, m: L21.run_cons(n, d, m, '', nb=4, malen=1)),
    ('§9 MA Band WTI 4h', 'wti', '4h', lambda n, d, m: L22.run_mab(n, d, m, '', ln=40, rr=3.0)),
    ('§10 Super trend V ETH 15m', 'eth', '15min', lambda n, d, m: L23.run_stv(n, d, m, '', short_ok=True)),
    ('§11 BEST ST ETH 1h', 'eth', '1h', lambda n, d, m: L24.run_best(n, d, m, '')),
    ('§12 VWAPStrategy ETH 30m', 'eth', '30min', lambda n, d, m: L24.run_vwap(n, d, m, '')),
    ('§13 Chandelier ETH 30m', 'eth', '30min', lambda n, d, m: L25.run_ce(n, d, m, '')),
    ('§14 THMA ETH 15m', 'eth', '15min', lambda n, d, m: L25.run_thma(n, d, m, '', ln=100)),
    ('§15 SM Pivot ETH 15m', 'eth', '15min', lambda n, d, m: L25.run_smp(n, d, m, '', sl=0.0, tp=0.0)),
    ('§16 HULL+T3 ETH 1h', 'eth', '1h', lambda n, d, m: L25.run_ht3(n, d, m, '', ln=100)),
    ('§17 5 EMA ETH 4h', 'eth', '4h', lambda n, d, m: L26.run_e5(n, d, m, '', rr=3.0)),
    ('§18 Wyckoff ETH 4h', 'eth', '4h', lambda n, d, m: L27.run_wyk(n, d, m, '', sl=0.03)),
    ('§19 HA MACD BTC 1h', 'btc', '1h', lambda n, d, m: L28.run_hamacd(n, d, m, '')),
    ('§20 HA PA WTI 4h', 'wti', '4h', lambda n, d, m: L28.run_hapa(n, d, m, '', ha=False, short_ok=True)),
    ('§21 Golden Edge WTI 30m', 'wti', '30min', lambda n, d, m: L29.run_ged(n, d, m, '', f=9, s=50)),
    ('§22 Multi-MA ETH 15m', 'eth', '15min', lambda n, d, m: L30.run_mma(n, d, m, '', ln=150)),
    ('§23 Multi-MA ETH 4h', 'eth', '4h', lambda n, d, m: L30.run_mma(n, d, m, '')),
    ('§24 Multi-MA BTC 4h', 'btc', '4h', lambda n, d, m: L30.run_mma(n, d, m, '', ln=150)),
    ('§25 MACD+Stoch WTI 4h', 'wti', '4h', lambda n, d, m: L31.run_mst(n, d, m, '', ls=14)),
    ('§26 TSI ST ETH 15m', 'eth', '15min', lambda n, d, m: L32.run_tss(n, d, m, '')),
    ('§27 TSI ST ETH 30m', 'eth', '30min', lambda n, d, m: L32.run_tss(n, d, m, '', per=32)),
    ('§28 VWAP X EMA ETH 30m', 'eth', '30min', lambda n, d, m: L33.run_vxe(n, d, m, '')),
]


def daily(tr, base):
    """Retorno diario de uma lista de trades marcada nas barras de base (close a close)."""
    idx = base.index; p = np.zeros(len(idx) + 1)
    a = idx.searchsorted(pd.DatetimeIndex(tr.t_in)); b = idx.searchsorted(pd.DatetimeIndex(tr.t_out))
    np.add.at(p, a, tr.d.to_numpy(float)); np.add.at(p, b, -tr.d.to_numpy(float))
    pos = pd.Series(np.cumsum(p)[:-1], idx)
    r = (pos * base.pct_change().fillna(0)).resample('1D').sum()
    cost = (tr.ret - tr.bruto).groupby(pd.DatetimeIndex(tr.t_out).floor('1D')).sum()
    return r.add(cost.reindex(r.index).fillna(0), fill_value=0), pos


def main():
    R = {}; BH = {}; out = []
    for ativo in ('xau', 'wti', 'btc', 'eth'):
        sel = [e for e in EST if e[1] == ativo]
        m1 = T.load_m1v(ativo); mm = M1(m1); cache = {}
        base = T.resample(m1, '15min').close; corte = pd.Timestamp(CORTE[ativo], tz=base.index.tz)
        bh = base.resample('1D').last().pct_change().fillna(0); BH[f'B&H {ativo.upper()}'] = bh[bh.index < corte]
        for rot, _, tf, fn in sel:
            df = cache.setdefault(tf, T.resample(m1, tf))
            tr = fn(ativo, df, mm)[1]
            r, _ = daily(tr, base); r = r[r.index < corte]
            R[rot] = r
            print(f'{rot:<28} {len(tr):6d} trades  dias IS {len(r)}  {r.index[0].date()}..{r.index[-1].date()}', flush=True)
    M = pd.DataFrame(R)
    C = M.corr(min_periods=120)
    CB = pd.concat([M, pd.DataFrame(BH)], axis=1).corr(min_periods=120)
    pd.set_option('display.width', 400); pd.set_option('display.max_columns', 60)
    C.round(2).to_csv(os.path.join(D, 'results', 'study_aprovadas_corr.csv'))
    out.append('Periodo antes do OOS (corte por ativo): ' + ', '.join(f'{k.upper()} < {v}' for k, v in CORTE.items()))
    out.append('\nCorrelacao dos retornos diarios (Pearson, par a par nos dias comuns)\n' + C.round(2).to_string())
    out.append('\nCorrelacao com o B&H de cada ativo\n' + CB.loc[list(R), list(BH)].round(2).to_string())
    tri = C.where(np.triu(np.ones(C.shape, bool), 1)).stack().dropna().sort_values()
    out.append('\nPares mais correlacionados\n' + tri.tail(15)[::-1].round(2).to_string())
    out.append('\nPares menos correlacionados\n' + tri.head(15).round(2).to_string())
    txt = '\n'.join(out); print(txt)
    open(os.path.join(D, 'results', 'study_aprovadas_corr.txt'), 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
