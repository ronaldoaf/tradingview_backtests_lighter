"""ICT Master Suite [Trading IQ] (ABYnIcdl, Pine v6): os modelos que vem DESLIGADOS por padrao.

  unicorn  Unicorn: P1<P3 (fundo mais baixo), P2>P1 e close>=P2; breaker de baixa (OB de baixa violado
           para cima) acima de P1 e formado depois de P3; FVG de alta depois de P3 que encoste no
           breaker. Limitada em min(topo FVG, topo breaker), stop P1, alvo = 1o pivo acima da entrada.
  ote      Optimal Trade Entry: estrutura Up, perna desde o pivo do MSS >= atrTF; limitada em
           maxima - 0,79 x perna, stop no inicio da perna, alvo maxima + 0,5 x perna.
  sb       Silver Bullet (so 5min): janelas NY 03-04, 10-11, 14-15; vies = direcao do ZigZag do 15min;
           FVG de alta (high[2]<low) -> limitada no low, alvo/stop nos pivos acima/abaixo. 1 por janela.
  lr       Liquidity Raid: faixa 13:30-16:00 NY; depois, rompimento do fundo (raid) + breaker de baixa
           formado depois do raid com close acima do topo e topo > fundo da faixa -> limitada no topo,
           alvo = 1o pivo acima, stop = minima do raid. 1 por sessao.
Todos espelhados no short. ZigZag base: reversao de atrTF = 2 x ATR(14), buffer 0. Order blocks pelo
z-score do log-retorno (|z|>=2) depois de 10 barras de lateralidade, como no getOB do script.

Execucao identica ao study_ict2022 (limitada/alvo/stop no M1, stop primeiro no mesmo minuto).
uso: python study_ictsuite.py [modelo,...] [ativo ...]
"""
import os, sys
import numpy as np, pandas as pd

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, 'scripts'))
import tvlib as T
from study_tvlote4 import trades_frame, finish
from study_tvlote6 import M1, _bracket
from study_ict2022 import _first_fill

BIG = 20e20
TFS = ['5min', '15min', '1h']


def zz_dir(df):
    """Direcao do ZigZag (atr 2xATR14) ao fim de cada barra -- usado como vies do Silver Bullet."""
    h, l, c = (df[k].to_numpy(float) for k in ('high', 'low', 'close'))
    atr = 2 * T.atr_rma(h, l, c, 14)
    out = np.zeros(len(c)); dr = 0; point = c[0]
    for i in range(len(c)):
        A = atr[i]
        if A != A:
            continue
        if dr == 1:
            point = max(point, h[i])
            if l[i] <= point - A and h[i] != point:
                dr = -1; point = l[i]
        elif dr == -1:
            point = min(point, l[i])
            if h[i] >= point + A and l[i] != point:
                dr = 1; point = h[i]
        else:
            if h[i] >= point + A: dr = 1; point = h[i]
            elif l[i] <= point + A: dr = -1; point = l[i]
        out[i] = dr
    return out


def run_model(df, mm, model, long_ok=True, short_ok=True, ote_lvl=0.79, ote_tp=0.5, bias15=None):
    o, h, l, c = (df[k].to_numpy(float) for k in ('open', 'high', 'low', 'close'))
    n = len(c)
    atr = T.atr_rma(h, l, c, 14); atrTF = 2 * atr
    b2m = mm.b2m(df); nm = len(mm.o)
    ny = df.index.tz_convert('America/New_York')
    hm = (ny.hour * 60 + ny.minute).to_numpy()
    day = ny.normalize().asi8
    lr = np.log(c / np.roll(c, 1)); lr[0] = 0.0
    sgn = np.sign(c - o)

    # ---- zz
    dr = 0; point = c[0]; timeP = 0
    pP = p2P = None; cP = None
    struct = ''; mrp = 0.0; ote_start = (0, c[0])
    hist = []                                   # pivos, mais recente primeiro: (barra, preco)
    # ---- order blocks: listas [inicio, topo, fundo, status(0/1)] mais recente primeiro
    bull = []; bear = []
    lower = BIG; higher = 0.0; lower_hist = []; isRange = False
    # ---- FVG (todos, mais recente primeiro): (topo, fundo, dir, barra)
    fvg = []
    # ---- estado dos modelos
    orders = {1: None, -1: None}
    inc = {1: set(), -1: set()}; pend = {1: None, -1: None}
    ote_hp = {1: (-1, -BIG), -1: (-1, -BIG)}; ote_used = {1: set(), -1: set()}; ote_last = -1
    sb_done = set()
    lr_state = dict(day=None, H=-BIG, L=BIG, hiT=None, loT=None, raidL=None, raidH=None, done=set())

    pos = 0; ent_i = -1; ent_px = 0.0; trades = []; just = 0
    for i in range(n):
        just = 0
        if i > 0:
            a = b2m[i]; b = b2m[i + 1] if i + 1 < n else nm
            m0 = a
            while m0 < b:
                if pos == 0:
                    lo = orders[1] if long_ok else None
                    so = orders[-1] if short_ok else None
                    if lo is None and so is None:
                        break
                    m, sd, px = _first_fill(mm.o, mm.h, mm.l, m0, b,
                                            lo[0] if lo else np.nan, so[0] if so else np.nan)
                    if m < 0:
                        break
                    pos = sd; ent_i = i; ent_px = px; just = sd
                    cur_tp, cur_sl = (lo if sd > 0 else so)[1:]
                    orders = {1: None, -1: None}
                    m0 = m
                mm_, px, code = _bracket(mm.o, mm.h, mm.l, mm.no, mm.nh, mm.nl, m0, b, pos, cur_sl, cur_tp)
                if code == 0:
                    break
                trades.append((ent_i, max(i, ent_i + 1) if i + 1 < n else i, pos, ent_px, px))
                pos = 0; m0 = mm_ + 1
        if i < 2 or atr[i] != atr[i]:
            continue
        cl = c[i]; A = atrTF[i]

        # ================= zz (estrutura, pivos, inicio da perna do OTE)
        if dr == 1:
            if p2P is not None:
                if c[i - 1] <= p2P[1] < cl and p2P[1] != mrp:
                    mrp = p2P[1]
                    if struct == 'Down':
                        struct = 'Up'; ote_start = pP
            point = max(point, h[i])
            if h[i] == point: timeP = i
            cP = (timeP, point)
            if l[i] <= point - A and h[i] != point:
                if pP is not None:
                    p2P = pP
                    if cl < p2P[1] and p2P[1] != mrp:
                        mrp = p2P[1]
                        if struct == 'Up':
                            struct = 'Down'; ote_start = cP
                pP = (timeP, point); cP = (i, l[i]); hist.insert(0, pP)
                dr = -1; point = l[i]; timeP = i
        elif dr == -1:
            if p2P is not None:
                if c[i - 1] > p2P[1] >= cl and p2P[1] != mrp:
                    mrp = p2P[1]
                    if struct == 'Up':
                        struct = 'Down'; ote_start = pP
            point = min(point, l[i])
            if l[i] == point: timeP = i
            cP = (timeP, point)
            if h[i] >= point + A and l[i] != point:
                if pP is not None:
                    p2P = pP
                    if cl > p2P[1] and p2P[1] != mrp:
                        mrp = p2P[1]
                        if struct == 'Down':
                            struct = 'Up'; ote_start = cP
                pP = (timeP, point); cP = (i, h[i]); hist.insert(0, pP)
                dr = 1; point = h[i]; timeP = i
        if dr == 0:
            if h[i] >= point + A:
                if pP is not None: p2P = pP
                pP = (timeP, point); cP = (i, h[i]); hist.insert(0, pP)
                dr = 1; point = h[i]; timeP = i; struct = 'Up'
            elif l[i] <= point + A:
                if pP is not None: p2P = pP
                pP = (timeP, point); cP = (i, l[i]); hist.insert(0, pP)
                dr = -1; point = l[i]; timeP = i; struct = 'Down'
        if len(hist) > 60:
            del hist[60:]

        # ================= getOB
        if model in ('unicorn', 'lr'):
            lo_ = max(0, i - 200)
            w = lr[lo_ + 1:i + 1]
            sd_ = w.std()
            z = (lr[i] - w.mean()) / sd_ if sd_ > 0 else 0.0
            if len(lower_hist) >= 10 and lower == lower_hist[-10]:
                isRange = True
            plo, phi = lower, higher
            lower = min(lower, l[i]); higher = max(higher, h[i])
            for arr, up in ((bull, True), (bear, False)):
                keep = []
                for ob in arr:
                    if ob[3] == 0:
                        if (cl < ob[2]) if up else (cl > ob[1]):
                            ob[3] = 1
                    elif (cl > ob[1]) if up else (cl < ob[2]):
                        continue
                    keep.append(ob)
                arr[:] = keep
            def add(arr, s):
                for k in range(i - 1, max(-1, i - 500), -1):
                    if sgn[k] == s:
                        arr.insert(0, [k, h[k], l[k], 0]); break
            if higher != phi:
                if isRange:
                    if z >= 2: add(bull, -1)
                    elif z <= -2: add(bull, 1)
                    isRange = False
                lower = l[i] - atr[i]; higher = h[i] + atr[i]
            elif lower != plo:
                if isRange:
                    if z >= 2: add(bear, -1)
                    elif z <= -2: add(bear, 1)
                    isRange = False
                higher = h[i] + atr[i]; lower = l[i] - atr[i]
            lower_hist.append(lower)
            if len(lower_hist) > 20: del lower_hist[:10]
            if len(bull) > 50: del bull[50:]
            if len(bear) > 50: del bear[50:]

        # ================= FVG (todos)
        if h[i - 2] < l[i]:
            fvg.insert(0, (l[i], h[i - 2], 1, i - 1))
        if l[i - 2] > h[i]:
            fvg.insert(0, (l[i - 2], h[i], -1, i - 1))
        if len(fvg) > 80:
            del fvg[80:]

        if pos != 0:
            orders = {1: None, -1: None}

        # ================= modelos
        if model == 'unicorn' and len(hist) >= 10:
            P1, P2, P3 = hist[1], hist[2], hist[3]
            for s in (1, -1):
                if just == s:
                    inc[s].add(P2[0]); pend[s] = None
                if pend[s] is not None:
                    q1, q2 = pend[s]
                    rng = abs(q1[1] - q2[1])
                    if s * (l[i] if s > 0 else h[i]) <= s * q1[1] or s * cP[1] >= s * q2[1] + rng \
                            or s * hist[0][1] >= s * q2[1] + rng:
                        orders[s] = None; pend[s] = None; inc[s].add(P2[0])
            if pos == 0:
                for s, obs in ((1, bear), (-1, bull)):
                    if P2[0] in inc[s] or not (s * P2[1] > s * P1[1] and s * cl >= s * P2[1]
                                               and s * P1[1] < s * P3[1]):
                        continue
                    blk = None
                    for ob in obs:
                        if ob[3] == 1 and (ob[2] >= P1[1] if s > 0 else ob[2] <= P1[1]) and ob[0] >= P3[0]:
                            blk = ob; break
                    if blk is None:
                        continue
                    tb, bb = blk[1], blk[2]
                    for f in fvg:
                        if f[2] != s or f[3] < P3[0]:
                            continue
                        hi, lo_ = f[0], f[1]
                        if not (cl >= hi if s > 0 else cl <= lo_):
                            continue
                        if (hi >= tb and lo_ <= tb) or (hi >= bb and lo_ <= bb) or (hi >= tb and lo_ <= bb) \
                                or (hi <= tb and lo_ >= bb):
                            ent = min(hi, tb) if s > 0 else max(lo_, bb)
                            tp = next((p[1] for p in hist if s * p[1] > s * ent), None)
                            if tp is not None:
                                orders[s] = (ent, tp, P1[1]); pend[s] = (P1, P2)
                            break

        elif model == 'ote':
            st = ote_start
            if st[0] != ote_last:
                ote_last = st[0]; ote_hp = {1: (-1, -BIG), -1: (-1, -BIG)}
            for s in (1, -1):
                ext = h[i] if s > 0 else l[i]
                if s * ext > ote_hp[s][1]:
                    ote_hp[s] = (i, s * ext); orders[s] = None
                if pos != 0:
                    orders[s] = None
                hpT, hp = ote_hp[s][0], s * ote_hp[s][1]
                if s * cl < s * st[1]:
                    ote_used[s].add(hpT)
                want = 'Up' if s > 0 else 'Down'
                if struct == want and pos == 0 and hpT >= 0 and hpT not in ote_used[s] \
                        and s * (hp - st[1]) >= A and orders[s] is None:
                    rngv = hp - st[1]
                    ent = hp - ote_lvl * rngv
                    if s * cl >= s * ent:
                        orders[s] = (ent, hp + ote_tp * rngv, st[1])
                if just == s:
                    ote_used[s].add(hpT)

        elif model == 'sb':
            t = hm[i]
            sess = next((k for k, (a0, a1) in enumerate(((180, 240), (600, 660), (840, 900)))
                         if a0 <= t < a1), None)
            if sess is None or pos != 0:
                orders = {1: None, -1: None}
            if just:
                sb_done.add((day[i], sess))
            key = (day[i], sess)
            if sess is not None and pos == 0 and key not in sb_done and orders[1] is None \
                    and orders[-1] is None and i > 0 and hm[i - 1] >= (180, 600, 840)[sess]:
                bias = bias15[i]
                if bias > 0 and h[i - 2] < l[i] and cl > l[i]:
                    tp = next((p[1] for p in hist if p[1] > h[i]), None)
                    sl = next((p[1] for p in hist if p[1] < l[i]), None)
                    if tp is not None and sl is not None:
                        orders[1] = (l[i], tp, sl)
                elif bias < 0 and l[i - 2] > h[i] and cl < h[i]:
                    tp = next((p[1] for p in hist if p[1] < l[i]), None)
                    sl = next((p[1] for p in hist if p[1] > h[i]), None)
                    if tp is not None and sl is not None:
                        orders[-1] = (h[i], tp, sl)

        elif model == 'lr':
            S = lr_state; t = hm[i]
            if 810 <= t < 960:
                if S['day'] != day[i]:
                    S.update(day=day[i], H=h[i], L=l[i], raidL=None, raidH=None, lrp=BIG, hrp=-BIG)
                    orders = {1: None, -1: None}
                else:
                    S['H'] = max(S['H'], h[i]); S['L'] = min(S['L'], l[i])
            elif S['day'] is not None:
                d0 = S['day']
                if S['raidL'] is None and l[i] < S['L']:
                    S['raidL'] = i
                if S['raidH'] is None and h[i] > S['H']:
                    S['raidH'] = i
                if S['raidL'] is not None:
                    S['lrp'] = min(S['lrp'], l[i])
                if S['raidH'] is not None:
                    S['hrp'] = max(S['hrp'], h[i])
                if just:
                    S['done'].add((d0, just))
                for s, obs, rk in ((1, bear, 'raidL'), (-1, bull, 'raidH')):
                    if (s > 0 and cl < S['L']) or (s < 0 and cl > S['H']):
                        orders[s] = None
                    if S[rk] is None or (d0, s) in S['done'] or pos != 0:
                        continue
                    best = None
                    for ob in obs:
                        if ob[3] != 1 or ob[0] < S[rk]:
                            continue
                        if s > 0 and cl > ob[1] and ob[1] > S['L']:
                            best = ob[1] if best is None else max(best, ob[1])
                        if s < 0 and cl < ob[2] and ob[2] < S['H']:
                            best = ob[2] if best is None else min(best, ob[2])
                    if best is None:
                        continue
                    tp = next((p[1] for p in hist if s * p[1] > s * best), None)
                    sl = S['lrp'] if s > 0 else S['hrp']
                    if tp is not None:
                        orders[s] = (best, tp, sl)
    return trades


def run(name, df, mm, model, tag, rows=None, verbose=True, **kw):
    extra = kw.pop('extra', {})
    trs = run_model(df, mm, model, **kw)
    if trs:
        ei, ej, es, pi, po = (np.array(x) for x in zip(*trs))
    else:
        ei = ej = es = np.zeros(0, np.int64); pi = po = np.zeros(0)
    tr = trades_frame(df, ei.astype(np.int64), ej.astype(np.int64), es.astype(np.int64), pi, po, name)
    return finish(name, df, tr, tag, rows, verbose, extra), tr


def main(models, nomes):
    for name in nomes:
        print(f"\n================= {name} =================", flush=True)
        m1 = T.load_m1v(name); mm = M1(m1)
        print(f"  M1 {m1.index[0].date()} -> {m1.index[-1].date()}")
        rows = []
        bias = None
        for tf in TFS:
            df = T.resample(m1, tf)
            print(f"\n### {tf}", flush=True)
            for md in models:
                kw = {}
                if md == 'sb':
                    if tf != '5min':
                        continue
                    d15 = T.resample(m1, '15min')
                    z = pd.Series(zz_dir(d15), index=d15.index + pd.Timedelta('15min'))
                    kw['bias15'] = z.reindex(df.index + pd.Timedelta('5min'), method='ffill').fillna(0).to_numpy()
                for lab, lo, so in (('', True, True), (' so long', True, False), (' so short', False, True)):
                    run(name, df, mm, md, f"{tf} {md}{lab}", rows, long_ok=lo, short_ok=so,
                        extra=dict(model=md, TF=tf, cfg='default' + lab), **kw)
                if md == 'ote':
                    for lvl in (0.62, 0.705):
                        for tpx in (0.5, 1.0, 2.0):
                            run(name, df, mm, md, f"{tf} ote lvl{lvl} tp{tpx}", rows, verbose=False,
                                ote_lvl=lvl, ote_tp=tpx, extra=dict(model=md, TF=tf, cfg=f'lvl{lvl} tp{tpx}'))
        g = pd.DataFrame(rows)
        g.to_csv(os.path.join(D, 'results', f'study_ictsuite_{name}_grid.csv'), index=False)
        print(f"\n=== resumo {name} ({len(g)} celulas) ===")
        cols = ['model', 'TF', 'cfg', 'trades', 'por_ano', 'bp_liq', 'win', 'cagr', 'bh', 'sharpe', 'dd', 't']
        for md, gg in g.groupby('model'):
            print(f"  {md}: liq>0 {int((gg.bp_liq > 0).sum())}/{len(gg)} | CAGR>B&H {int((gg.cagr > gg.bh).sum())}"
                  f" | melhor CAGR {gg.cagr.max():+.1%}")
        print(g.sort_values('cagr', ascending=False).head(10)[cols]
              .to_string(index=False, float_format=lambda v: f'{v:.3f}'))


if __name__ == '__main__':
    a = sys.argv[1:]
    models = a[0].split(',') if a and not a[0] in ('xau', 'us100', 'wti', 'btc', 'eth') else ['unicorn', 'ote', 'sb', 'lr']
    if a and a[0].split(',')[0] in ('unicorn', 'ote', 'sb', 'lr'):
        a = a[1:]
    main(models, a or ['xau'])
