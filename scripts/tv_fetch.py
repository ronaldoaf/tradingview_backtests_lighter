"""Baixa o Pine Script publicado de um script do TradingView.
uso: python tv_fetch.py <final-da-url> [...]   -> grava pine/<id>.pine e imprime versao/security/lookahead
"""
import os, re, sys, json, urllib.request

D = os.environ.get('EDGE_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(slug):
    req = urllib.request.Request(f'https://www.tradingview.com/script/{slug}/',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    i = s.find('"script":{"id"')
    j = s.find('"content":', i) + len('"content":')
    src, _ = json.JSONDecoder().raw_decode(s[j:])
    if src:
        return src
    # scripts novos vem com content vazio: o fonte aberto sai do pine-facade pelo script_id_part
    m = re.search(r'"script_id_part":"(PUB;[^"]+)"', s[i:])
    if not m:
        return ''
    req = urllib.request.Request('https://pine-facade.tradingview.com/pine-facade/get/'
                                 + m.group(1).replace(';', '%3B') + '/last',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read()).get('source') or ''
    except Exception:
        return ''


def triage(src):
    v = re.search(r'//\s*@version\s*=\s*(\d+)', src)
    ver = int(v.group(1)) if v else 1
    sec = len(re.findall(r'\b(?:request\.)?security\s*\(', src))
    la = 'lookahead_on' in src
    rep = []
    if sec and (ver <= 2 or la):
        rep.append('security() olha o futuro (Pine<=2 ou lookahead_on)')
    if re.search(r'\bstrategy\.(entry|order)\b', src) is None:
        rep.append('sem strategy.entry/order')
    return dict(versao=ver, security=sec, lookahead_on=la, alertas=rep)


if __name__ == '__main__':
    os.makedirs(os.path.join(D, 'pine'), exist_ok=True)
    for slug in sys.argv[1:]:
        src = fetch(slug)
        p = os.path.join(D, 'pine', slug.split('-')[0] + '.pine')
        open(p, 'w').write(src)
        print(slug, len(src.splitlines()), 'linhas', triage(src) if src else 'CODIGO FECHADO/PROTEGIDO')
