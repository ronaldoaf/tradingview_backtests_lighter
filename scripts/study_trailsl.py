"""Trailing SL Strategy (QuantNomad, n3vj0MIi) — https://www.tradingview.com/script/n3vj0MIi/

Stop-and-reverse sempre-no-mercado com uma unica linha de stop:
  comprado : linha = max(linha_anterior, minima - p*fechamento)   (so sobe)
  vendido  : linha = min(linha_anterior, maxima + p*fechamento)   (so desce)
A linha e recalculada SO no fechamento de cada barra; durante a barra seguinte a ordem stop fica
parada nesse nivel. Quando o preco toca a linha, a posicao vira (fecha e abre o lado oposto no
mesmo fill, dobro do tamanho) e a linha e refeita do zero pelo novo lado, no fechamento da barra
em que a virada ocorreu. Sem alvo e sem saida por tempo: a unica saida e a virada.

Execucao: o toque e resolvido minuto a minuto no M1. A abertura de cada minuto e testada antes do
range, logo um gap que pula o nivel sai NA ABERTURA (pior que o nivel). No maximo uma virada por
barra, porque a linha do novo lado so existe a partir do fechamento dessa barra.

Custo: 2 pernas por virada (CUSTO[ativo] cada) + funding pro-rata (o long paga, o short recebe).
Benchmarks: buy & hold do ativo e controle aleatorio de mesmo lado e mesma duracao.

uso: python study_tvlote7.py [xau us100 btc wti eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T

TFS = ['15min', '30min', '1h', '4h', '1D']
PCTS = [0.0100, 0.0125, 0.0150, 0.0175, 0.0200, 0.0225, 0.0250, 0.0300, 0.0400, 0.0500]
DOC = 0.0200   # o stop que o documento recomenda
DOCTF = '30min'


@njit(cache=True)
def _run(bo, bh, bl, bc, b2m, mo, mh, ml, pct, side0):
    """Devolve (i_in, i_out, m_in, m_out, entry, exit, side) por trade, na ordem das viradas."""
    n = len(bc)
    cap = 4 * n + 8
    ii = np.empty(cap, np.int64); jj = np.empty(cap, np.int64)
    mi = np.empty(cap, np.int64); mj = np.empty(cap, np.int64)
    pe = np.empty(cap, np.float64); px = np.empty(cap, np.float64)
    sd = np.empty(cap, np.int64)
    k = 0

    pos = side0
    i_in = 1; m_in = b2m[1]; ent = bo[1]        # entra na abertura da barra 1
    line = bl[0] - pct * bc[0] if pos > 0 else bh[0] + pct * bc[0]

    for i in range(1, n - 1):
        a = b2m[i]; b = b2m[i + 1]
        hit = -1; fill = 0.0
        for m in range(a, b):
            if pos > 0:
                if mo[m] <= line:
                    hit = m; fill = mo[m]; break
                if ml[m] <= line:
                    hit = m; fill = line; break
            else:
                if mo[m] >= line:
                    hit = m; fill = mo[m]; break
                if mh[m] >= line:
                    hit = m; fill = line; break
        if hit >= 0:
            ii[k] = i_in; jj[k] = i; mi[k] = m_in; mj[k] = hit
            pe[k] = ent; px[k] = fill; sd[k] = pos; k += 1
            pos = -pos
            i_in = i; m_in = hit; ent = fill
            # linha do novo lado, refeita do zero no fechamento desta barra
            line = bl[i] - pct * bc[i] if pos > 0 else bh[i] + pct * bc[i]
        else:
            # a linha so anda a favor
            if pos > 0:
                nv = bl[i] - pct * bc[i]
                if nv > line: line = nv
            else:
                nv = bh[i] + pct * bc[i]
                if nv < line: line = nv
    return ii[:k], jj[:k], mi[:k], mj[:k], pe[:k], px[:k], sd[:k]


def run(df, m1, pct, name, side0=1):
    b2m = m1.index.searchsorted(df.index).astype(np.int64)
    b2m = np.append(b2m, len(m1))
    r = _run(df.open.to_numpy(float), df.high.to_numpy(float), df.low.to_numpy(float),
             df.close.to_numpy(float), b2m,
             m1.open.to_numpy(float), m1.high.to_numpy(float), m1.low.to_numpy(float),
             float(pct), int(side0))
    ii, jj, mi, mj, pe, px, sd = r
    if len(ii) == 0:
        return None
    mix = m1.index
    out = pd.DataFrame(dict(t_in=mix[mi], t_out=mix[mj], i=ii, j=np.maximum(jj, ii + 1),
                            d=sd.astype(float), u=1.0, entry=pe, exit=px))
    out['bruto'] = out.d * (out.exit / out.entry - 1)
    out['yrs'] = (out.t_out - out.t_in).dt.total_seconds() / (365 * 86400)
    return T._cost(out, name, True)


def summ(df, tr, name, nsim=20):
    return T.summarize(df, tr, name, nsim=nsim, minimo=8)


def thirds(df, m1, pct, name):
    """CAGR vs B&H em cada terco do periodo, para ver se o resultado esta concentrado."""
    bnds = pd.date_range(df.index[0], df.index[-1], periods=4)
    out = []
    for a, b in zip(bnds[:-1], bnds[1:]):
        d2 = df[(df.index >= a) & (df.index < b)]
        m2 = m1[(m1.index >= a) & (m1.index < b)]
        if len(d2) < 50:
            out.append(None); continue
        tr = run(d2, m2, pct, name)
        out.append(summ(d2, tr, name, nsim=10) if tr is not None else None)
    return out


def main(names):
    for name in names:
        m1 = T.load_m1v(name)
        print(f"\n===== {name}  M1 {m1.index[0].date()} -> {m1.index[-1].date()} "
              f"({len(m1):,} min) | custo {1e4*T.CUSTO[name]:.2f}bp/perna, "
              f"funding {T.FUND.get(name, 5.0):.1f}%a.a.")

        dfs = {tf: T.resample(m1, tf) for tf in TFS}

        print(f"\n-- defaults do documento ({DOC:.2%} de stop) e o padrao do script (4%)")
        for tf in TFS:
            for pct in (DOC, 0.04):
                tr = run(dfs[tf], m1, pct, name)
                o = summ(dfs[tf], tr, name)
                if o: T.line(f"{tf} stop {pct:.2%}", o)

        print(f"\n-- grade stop x TF")
        rows = []
        for tf, pct in itertools.product(TFS, PCTS):
            tr = run(dfs[tf], m1, pct, name)
            o = summ(dfs[tf], tr, name)
            if o:
                rows.append(dict(tf=tf, pct=pct, **o))
        g = pd.DataFrame(rows)
        if len(g) == 0:
            print("  (sem trades)"); continue
        pos = (g.bp_liq > 0).sum(); bate = (g.cagr > g.bh).sum()
        print(f"\n  grade {name}: {len(g)} celulas | liq>0: {pos} | liq>0 e t>1: "
              f"{((g.bp_liq > 0) & (g.t > 1)).sum()} | CAGR>B&H: {bate}")
        cols = ['tf', 'pct', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh',
                'sharpe', 'dd', 'expo', 'ctl_bp', 't']
        print(g.sort_values('bp_liq', ascending=False)[cols].head(15).to_string(index=False))
        g.to_csv(os.path.join(D, 'results', f'study_tvlote7_{name}_grid.csv'), index=False)

        # ---------------- robustez da celula do documento
        print(f"\n-- robustez da celula do documento ({DOCTF}, stop {DOC:.2%})")
        df = dfs[DOCTF]
        tr = run(df, m1, DOC, name)
        if tr is None:
            continue

        print("  tercos do periodo:")
        for k, o in enumerate(thirds(df, m1, DOC, name), 1):
            if o: T.line(f"terco {k}", o)

        print("  out-of-sample (metade 1 calibra, metade 2 mede):")
        meio = df.index[len(df) // 2]
        for tag, d2 in (('metade 1', df[df.index < meio]), ('metade 2', df[df.index >= meio])):
            m2 = m1[(m1.index >= d2.index[0]) & (m1.index <= d2.index[-1])]
            t2 = run(d2, m2, DOC, name)
            o = summ(d2, t2, name, nsim=10)
            if o: T.line(tag, o)

        print("  multiplicador de custo (na celula do documento):")
        base_c, base_f = T.CUSTO[name], T.FUND.get(name, 5.0)
        for mult in (1, 2, 4):
            T.CUSTO[name] = base_c * mult; T.FUND[name] = base_f * mult
            t2 = run(df, m1, DOC, name)
            o = summ(df, t2, name, nsim=10)
            if o: T.line(f"custo x{mult}", o)
        T.CUSTO[name] = base_c; T.FUND[name] = base_f

        print("  lado inicial (o resultado nao deve depender disso):")
        for s, tag in ((1, 'comeca long'), (-1, 'comeca short')):
            t2 = run(df, m1, DOC, name, side0=s)
            o = summ(df, t2, name, nsim=10)
            if o: T.line(tag, o)

        tr.to_csv(os.path.join(D, 'results', f'study_tvlote7_{name}_trades.csv'), index=False)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    main(args or ['xau'])
