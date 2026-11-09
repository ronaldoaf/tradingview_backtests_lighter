"""Carteira de 6 ativos (5 + XAG) com media longa + metade com vol da carteira alta. So 4h.
Reusa study_ma_vol_cart; XAG = Dukascopy 1m (data/xag_1m_dl.py), spread 0,65 bp (VPS), funding 16,2% a.a.
(XAU 13,8% + diferenca media XAU/XAG de 2,4% medida na Lighter)."""
import os, pandas as pd
import tvlib, study_ma_vol_cart as S
from study_engulf_psar import CUSTO, FUND
CUSTO['xag'] = 0.65e-4; FUND['xag'] = 16.2
_orig = tvlib.load_m1v
def load(name):
    if name != 'xag': return _orig(name)
    x = pd.read_parquet(os.path.join(tvlib.D, 'data', 'silver', 'xag_1m.parquet'))
    x = x[~x.index.duplicated()].sort_index()[tvlib.OHLCV]; return x[x.high >= x.low]
S.load_m1v = load
S.AT = ['xau', 'us100', 'wti', 'btc', 'eth', 'xag']
S.TFS_RUN = ['4h']
if __name__ == '__main__':
    g = S.run(); g.to_csv('../results/ma_vol_cart6_grade.csv', index=False)
    pd.set_option('display.width', 250)
    print(g.sort_values('treino_sh', ascending=False).head(10).to_string(index=False))
    print(g.groupby(['filtro', 'x'], dropna=False)[['treino_sh', 'valid_sh', 'teste_sh']].median().round(2))
    print((g.valid_sh > 0).mean(), (g.teste_sh > 0).mean())
