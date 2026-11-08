import json,time,urllib.request,os,sys
from concurrent.futures import ThreadPoolExecutor
B='https://mainnet.zklighter.elliot.ai/api/v1'
ob={m['symbol']:m['market_id'] for m in json.load(open('ob.json'))['order_book_details']}
syms=sys.argv[1].split(','); os.makedirs('fund',exist_ok=True)
def get(u):
    for k in range(10):
        try:
            j=json.load(urllib.request.urlopen(u,timeout=30))
            if j.get('code')==23000: time.sleep(10); continue
            return j
        except Exception: time.sleep(3)
    return {}
def dl(s):
    if s not in ob: return
    m=ob[s]; d={}; end=int(time.time())
    while True:
        c=get(f'{B}/fundings?market_id={m}&resolution=1h&start_timestamp=1700000000&end_timestamp={end}&count_back=500').get('fundings') or []
        new=[x for x in c if x['timestamp'] not in d]
        if not new: break
        for x in c: d[x['timestamp']]=x
        end=min(x['timestamp'] for x in c)-1; time.sleep(0.2)
    r=[float(x['rate'])/100*(1 if x['direction']=='long' else -1) for x in d.values()]
    json.dump(dict(n=len(r),anual=sum(r)/max(len(r),1)*24*365),open(f'fund/{s}.json','w')); print(s,len(r),flush=True)
with ThreadPoolExecutor(6) as ex: list(ex.map(dl,syms))
