#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, json, statistics, time, urllib.request, urllib.error
from pathlib import Path


def one(url, method, headers, body, timeout):
    started=time.perf_counter()
    req=urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(); status=r.status
    except urllib.error.HTTPError as exc:
        exc.read(); status=exc.code
    return status, time.perf_counter()-started


def pct(values,p):
    if not values:return 0.0
    xs=sorted(values);i=min(len(xs)-1,max(0,math.ceil(p*len(xs))-1));return xs[i]

if __name__=='__main__':
    import math
    ap=argparse.ArgumentParser(description='SYNERGY enterprise HTTP load harness')
    ap.add_argument('--url',default='http://127.0.0.1:8000/enterprise/health')
    ap.add_argument('--method',default='GET')
    ap.add_argument('--requests',type=int,default=500)
    ap.add_argument('--concurrency',type=int,default=32)
    ap.add_argument('--timeout',type=float,default=3.0)
    ap.add_argument('--token',default='')
    ap.add_argument('--body-file',default='')
    args=ap.parse_args()
    body=Path(args.body_file).read_bytes() if args.body_file else None
    headers={'Content-Type':'application/json'}
    if args.token:headers['Authorization']='Bearer '+args.token
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        rows=list(ex.map(lambda _:one(args.url,args.method.upper(),headers,body,args.timeout),range(args.requests)))
    elapsed=time.perf_counter()-start
    lat=[x[1] for x in rows];statuses={}
    for s,_ in rows:statuses[s]=statuses.get(s,0)+1
    report={'requests':len(rows),'seconds':elapsed,'rps':len(rows)/elapsed if elapsed else 0,'p50_ms':pct(lat,.50)*1000,'p95_ms':pct(lat,.95)*1000,'p99_ms':pct(lat,.99)*1000,'statuses':statuses}
    print(json.dumps(report,indent=2,sort_keys=True))
