"""ICT Master Suite [Trading IQ] (ABYnIcdl, Pine v6) -- so o modelo ligado por padrao: "2022 Model".

Traducao direta de zzLiq / fairValueGap / model2022Long / model2022Short (o resto do script e desenho
ou modelos desligados). Com o TF do grafico como finalTF, todo request.security e o proprio grafico.

  1. ZigZag por ATR: a perna vira quando o preco recua atrLiqSweep = ATR(14) x (10 - 6) do extremo.
  2. Topos/fundos IGUAIS: dois pivos consecutivos do mesmo tipo a menos de 1 ATR um do outro formam
     um grupo de liquidez (vai acumulando enquanto os novos pivos ficam na faixa).
  3. Varredura: grupo de fundos iguais + fechamento >= ultimo topo + 1 ATR = "up sweep"
     (fundo do grupo = Lx). Espelhado para topos iguais rompidos para baixo ("down sweep").
  4. FVGs (gap de 3 velas) so sao coletados a partir do ultimo pivo do grupo varrido (onlyFVGliq);
     depois, cada novo FVG do mesmo lado so entra se for mais alto (baixo) que o ultimo registrado.
     Um FVG de alta morre quando o close fica abaixo do seu fundo.
  5. Long: com a varredura viva e sem posicao, ordem LIMITADA no topo do FVG de alta (abaixo do close,
     acima de Lx) mais perto de Lx + 0,5 x (maxima desde a varredura - Lx). Alvo = maxima desde a
     varredura; stop = Lx. A ordem e cancelada numa nova varredura ou se o close passar de Lx + 10 ATR.
     Cada varredura so gera um trade. Short espelhado.

Execucao: ordens decididas no fechamento valem a partir da barra seguinte; preenchimento da limitada,
alvo e stop resolvidos no M1 (gap alem do nivel executa na abertura do minuto; stop antes do alvo no
mesmo minuto). Custo CUSTO + funding. Controle: mesmo lado, mesma duracao (aberto-a-aberto).

uso: python study_ict2022.py [xau us100 wti btc eth]
"""
import os, sys, itertools
import numpy as np, pandas as pd
from numba import njit

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1, _bracket

TFS = ['5min', '15min', '1h', '4h']
BIG = 20e20


@njit(cache=True)
def _first_fill(mo, mh, ml, a, b, llim, slim):
    """Primeiro minuto em [a,b) que preenche a limitada de compra (llim) ou de venda (slim).
    Devolve (minuto, lado, preco)."""
    for m in range(a, b):
        if llim == llim and ml[m] <= llim:
            return m, 1, min(mo[m], llim)
        if slim == slim and mh[m] >= slim:
            return m, -1, max(mo[m], slim)
    return -1, 0, 0.0


class Side:
    """Estado do model2022Long (sgn=+1) ou model2022Short (sgn=-1). Precos do short sao tratados
    no espelho (x -> -x), o que transforma maxima/minima e topo/fundo do FVG automaticamente."""
    def __init__(self, sgn, fib):
        self.sgn = sgn; self.fib = fib
        self.includes = set(); self.trailing = 0
        self.hh = -BIG                          # getHighestHigh=0 / getLowestLow=20e20 no espelho
        self.dist = BIG
        self.line0 = None                        # y1 da linha 0% (Lx) enquanto existir
        self.order = None                        # (limite, alvo, stop) em precos reais


def run_model(df, mm, agg=6, fib=0.5, long_ok=True, short_ok=True):
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    n = len(c)
    atr = T.atr_rma(h, l, c, 14)
    atrLS = atr * (10 - agg)
    b2m = mm.b2m(df); nm = len(mm.o)

    # ---- estado do zzLiq (pontos = (indice_barra, preco))
    point = c[0]; timeP = 0; dr = 0
    cP = pP = p2P = None
    sweepPoint = sweepPointDn = None
    sweepPointArr = []; sweepPointArrDn = []
    upArr = []; dnArr = []; upDisp = set(); dnDisp = set()
    upHigh = 0.0; dnLow = BIG
    upSweeps = []; dnSweeps = []                 # (t_ini, topo, t_fim, fundo)
    upFirst = set(); dnFirst = set()
    # ---- FVGs: lista com o mais recente primeiro; cada um (H, L, dir, T)
    fvg = []; upPrices = []; dnPrices = []
    take = {'Up': 0, 'Down': 0}
    sides = {1: Side(1, fib), -1: Side(-1, fib)}
    # ---- posicao
    pos = 0; ent_i = -1; ent_px = 0.0; ent_side = 0
    trades = []
    traded_bar = {1: -1, -1: -1}; closed_bar = {1: -1, -1: -1}

    for i in range(n):
        # ================= execucao intrabar (ordens vindas do fechamento anterior)
        if i > 0:
            a = b2m[i]; b = b2m[i + 1] if i + 1 < n else nm
            m0 = a
            while m0 < b:
                if pos == 0:
                    lo = sides[1].order if long_ok else None
                    so = sides[-1].order if short_ok else None
                    if lo is None and so is None:
                        break
                    m, sd, px = _first_fill(mm.o, mm.h, mm.l, m0, b,
                                            lo[0] if lo else np.nan, so[0] if so else np.nan)
                    if m < 0:
                        break
                    pos = sd; ent_i = i; ent_px = px; ent_side = sd
                    tg, st = (lo if sd > 0 else so)[1:]
                    sides[1].order = None; sides[-1].order = None    # posicao aberta: a outra e cancelada no fechamento
                    traded_bar[sd] = i
                    cur_tp, cur_sl = tg, st
                    m0 = m
                # em posicao: alvo/stop a partir do minuto corrente
                mm_, px, code = _bracket(mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, m0, b, pos, cur_sl, cur_tp)
                if code == 0:
                    break
                trades.append((ent_i, max(i, ent_i + 1) if i + 1 < n else i, pos, ent_px, px))
                closed_bar[pos] = i
                pos = 0
                m0 = mm_ + 1
        if i < 2 or atr[i] != atr[i]:
            continue

        # ================= fairValueGap (antes do zzLiq)
        cl = c[i]
        if upPrices or dnPrices:
            gmax = max(upPrices) if upPrices else np.nan
            gmin = min(dnPrices) if dnPrices else np.nan
            isH = cl < gmax; isL = cl > gmin
            if fvg and (isH or isL):
                keep = []
                for f in fvg:
                    if isH and f[2] == 'Up':
                        if cl < f[0]:
                            continue
                        keep.append(f); continue
                    if isL and f[2] == 'Down' and cl > f[1]:
                        continue
                    keep.append(f)
                fvg = keep
        H2, L, H, L2, t1 = h[i - 2], l[i], h[i], l[i - 2], i - 1
        if take['Up'] != 0 and H2 < L:
            if take['Up'] == 1 or not fvg:
                fvg.insert(0, (H2, L, 'Up', t1)); upPrices.append(H2); take['Up'] = 2
            elif L > fvg[0][1]:
                fvg.insert(0, (H2, L, 'Up', t1)); upPrices.append(H2)
            else:
                take['Up'] = 0
        if take['Down'] != 0 and L2 > H:
            if take['Down'] == 1 or not fvg:
                fvg.insert(0, (H, L2, 'Down', t1)); dnPrices.append(L2); take['Down'] = 2
            elif H < fvg[0][0]:
                fvg.insert(0, (H, L2, 'Down', t1)); dnPrices.append(L2)
            else:
                take['Down'] = 0

        # ================= zzLiq
        A = atrLS[i]; R = atr[i]
        if dr == 1:
            point = max(point, h[i])
            if h[i] == point: timeP = i
            cP = (timeP, point)
            if l[i] <= point - A and h[i] != point:
                if p2P is not None:
                    sweepPoint = p2P; sweepPointArr.append(sweepPoint)
                if sweepPointDn is not None and p2P is not None and len(sweepPointArrDn) >= 2:
                    if not dnArr:
                        gP, gC = p2P, cP
                        if gC[0] not in dnDisp and gP[0] not in dnDisp and abs(gC[1] - gP[1]) <= R:
                            dnLow = sweepPointArrDn[-1][1]; dnArr += [gP, gC]
                    else:
                        gC = p2P; gF = dnArr[0]
                        if abs(gC[1] - gF[1]) <= R:
                            dnLow = min(sweepPointArrDn[-1][1], dnLow); dnArr.append(gC)
                        else:
                            dnArr = []; dnLow = BIG
                            gP = sweepPointArrDn[-2]
                            if gC[0] not in dnDisp and gP[0] not in dnDisp and abs(gC[1] - gP[1]) <= R:
                                dnLow = sweepPointArrDn[-1][1]; dnArr += [gP, gC]
                if p2P is not None:
                    sweepPointDn = p2P; sweepPointArrDn.append(sweepPointDn)
                if pP is not None:
                    p2P = pP
                pP = (timeP, point); cP = (i, l[i]); dr = -1; point = l[i]; timeP = i
        elif dr == -1:
            point = min(l[i], point)
            if l[i] == point: timeP = i
            cP = (timeP, point)
            if h[i] >= point + A and l[i] != point:
                if p2P is not None:
                    sweepPointDn = p2P; sweepPointArrDn.append(sweepPointDn)
                if sweepPoint is not None and p2P is not None and len(sweepPointArr) >= 2:
                    if not upArr:
                        gP, gC = p2P, cP
                        if gC[0] not in upDisp and gP[0] not in upDisp and abs(gC[1] - gP[1]) <= R:
                            upHigh = sweepPointArr[-1][1]; upArr += [gP, gC]
                    else:
                        gC = p2P; gF = upArr[0]
                        if abs(gC[1] - gF[1]) <= R:
                            upHigh = max(sweepPointArr[-1][1], upHigh); upArr.append(gC)
                        else:
                            upArr = []; upHigh = 0.0
                            gP = sweepPointArr[-2]
                            if gC[0] not in upDisp and gP[0] not in upDisp and abs(gC[1] - gP[1]) <= R:
                                upHigh = sweepPointArr[-1][1]; upArr += [gP, gC]
                if p2P is not None:
                    sweepPoint = p2P; sweepPointArr.append(sweepPoint)
                if pP is not None:
                    p2P = pP
                pP = (timeP, point); cP = (i, h[i]); dr = 1; point = h[i]; timeP = i
        if dr == 0:
            if h[i] >= point + A:
                if pP is not None: p2P = pP
                pP = (timeP, point); cP = (i, h[i]); dr = 1; point = h[i]; timeP = i
            elif l[i] <= point + A:
                if pP is not None: p2P = pP
                pP = (timeP, point); cP = (i, l[i]); dr = -1; point = l[i]; timeP = i

        if upArr and upHigh != 0 and cl >= upHigh + R:
            top = max(p[1] for p in upArr); bot = min(p[1] for p in upArr)
            upDisp.update(p[0] for p in upArr)
            if upArr[0][0] not in upFirst:
                upFirst.add(upArr[0][0]); upSweeps.append((upArr[0][0], top, i, bot))
                take['Up'] = 1
                k = i - upArr[-1][0]
                for bb in range(k, 0, -1):
                    if i - bb - 2 >= 0:
                        g2, gl = h[i - bb - 2], l[i - bb]
                        if g2 < gl:
                            fvg.insert(0, (g2, gl, 'Up', i - bb - 1)); upPrices.append(g2); take['Up'] = 2
                upHigh = 0.0; upArr = []
        if dnArr and dnLow != BIG and cl <= dnLow - R:
            top = max(p[1] for p in dnArr); bot = min(p[1] for p in dnArr)
            dnDisp.update(p[0] for p in dnArr)
            if dnArr[0][0] not in dnFirst:
                dnFirst.add(dnArr[0][0]); dnSweeps.append((dnArr[0][0], top, i, bot))
                take['Down'] = 1
                k = i - dnArr[-1][0]
                for bb in range(k, 0, -1):
                    if i - bb - 2 >= 0:
                        gh, g2 = h[i - bb], l[i - bb - 2]
                        if g2 > gh:
                            fvg.insert(0, (gh, g2, 'Down', i - bb - 1)); dnPrices.append(g2); take['Down'] = 2
                dnLow = BIG; dnArr = []

        # ================= model2022Long / model2022Short
        for sg, sweeps in ((1, upSweeps), (-1, dnSweeps)):
            S = sides[sg]
            if traded_bar[sg] == i:
                S.includes.add(S.trailing)
            if closed_bar[sg] == i:
                S.line0 = None; S.dist = BIG
            if not sweeps:
                continue
            sw = sweeps[-1]
            stime = sw[0]
            if pos == 0:
                far = S.line0 is not None and sg * cl >= sg * S.line0 + R * 10
                if S.trailing != stime or far:
                    S.order = None; S.includes.add(S.trailing)
                    S.hh = -BIG; S.dist = BIG; S.line0 = None
            if pos == -sg:
                S.order = None; S.hh = -BIG; S.dist = BIG
            if stime not in S.includes and pos == 0:
                hi_m = sg * h[i] if sg > 0 else -l[i]           # maxima no espelho
                if hi_m > S.hh:
                    S.dist = BIG
                S.hh = max(hi_m, S.hh)
                Lx = sw[3] if sg > 0 else -sw[1]                  # fundo varrido (espelho: -topo)
                rng = Lx + (S.hh - Lx) * S.fib
                found = None
                for f in fvg:
                    if f[2] != ('Up' if sg > 0 else 'Down'):
                        continue
                    edge = sg * (max(f[0], f[1]) if sg > 0 else min(f[0], f[1]))
                    if sg * cl > edge and edge >= Lx:
                        d = abs(edge - rng)
                        S.dist = min(d, S.dist)
                        if S.dist == d:
                            found = edge
                if found is not None:
                    S.line0 = sg * Lx
                    S.order = (sg * found, sg * S.hh, sg * Lx)      # limite, alvo, stop (reais)
            S.trailing = stime
    return trades, len(upSweeps), len(dnSweeps)


def run(name, df, mm, tag, rows=None, verbose=True, agg=6, fib=0.5, long_ok=True, short_ok=True, **extra):
    trs, nu, nd = run_model(df, mm, agg, fib, long_ok, short_ok)
    if trs:
        ei, ej, es, pi, po = (np.array(x) for x in zip(*trs))
    else:
        ei = ej = es = np.zeros(0, np.int64); pi = po = np.zeros(0)
    tr = trades_frame(df, ei.astype(np.int64), ej.astype(np.int64), es.astype(np.int64), pi, po, name)
    o = finish(name, df, tr, tag, rows, verbose, dict(extra, sweeps_up=nu, sweeps_dn=nd))
    if verbose:
        print(f"      varreduras: {nu} de alta, {nd} de baixa")
    return o, tr


def main(nomes):
    for name in nomes:
        print(f"\n================= {name} =================")
        m1 = T.load_m1v(name)
        mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        rows = []
        for tf in TFS:
            df = T.resample(m1, tf)
            print(f"\n### {tf}")
            run(name, df, mm, f"{tf} ICT2022 default", rows, est='default', TF=tf, cfg='agg6 fib.5')
            run(name, df, mm, f"{tf} ICT2022 so long", rows, short_ok=False, est='long', TF=tf,
                cfg='agg6 fib.5 so long')
            run(name, df, mm, f"{tf} ICT2022 so short", rows, long_ok=False, est='short', TF=tf,
                cfg='agg6 fib.5 so short')
            if tf == '5min':
                continue
            for agg, fib in itertools.product((4, 5, 6, 7, 8), (0.382, 0.5, 0.618, 0.786)):
                if agg == 6 and fib == 0.5:
                    continue
                run(name, df, mm, '', rows, verbose=False, agg=agg, fib=fib, est='grade', TF=tf,
                    cfg=f'agg{agg} fib{fib}')
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'results', f'study_ict2022_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        print(f"  liq>0 {int((g.bp_liq > 0).sum())} | liq>0 e t>2 {int(((g.bp_liq > 0) & (g.t > 2)).sum())}"
              f" | CAGR>B&H {int((g.cagr > g.bh).sum())} | melhor CAGR {g.cagr.max():+.1%}")
        cols = ['TF', 'cfg', 'trades', 'por_ano', 'bp_bruto', 'bp_liq', 'win', 'cagr', 'bh', 'sharpe',
                'dd', 'expo', 'ctl_bp', 't']
        print("\n  top 12 por CAGR:")
        print(g.sort_values('cagr', ascending=False).head(12)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    main(sys.argv[1:] or ['xau'])
