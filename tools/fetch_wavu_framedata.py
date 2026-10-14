#!/usr/bin/env python3
"""Fetch public T8 frame data from wavu.wiki (CC0) Cargo API -> docs/t7t8-reference/frame-data/<body>.json"""
import json, sys, time, urllib.parse, urllib.request, pathlib
F="id,name,input,parent,target,damage,startup,recv,tot,crush,block,hit,ch"
OUT=pathlib.Path(__file__).resolve().parents[1]/"docs/t7t8-reference/frame-data"
def q(body, off):
    p={"action":"cargoquery","tables":"Move","fields":F,"where":f"id LIKE '{body}-%'","limit":"500","offset":str(off),"format":"json"}
    r=urllib.request.Request("https://wavu.wiki/w/api.php?"+urllib.parse.urlencode(p),headers={"User-Agent":"WH-reference/1.0"})
    return [x["title"] for x in json.load(urllib.request.urlopen(r,timeout=60)).get("cargoquery",[])]
for body in sys.argv[1:]:
    rows,off=[],0
    while True:
        b=q(body,off); rows+=b; off+=500
        if len(b)<500: break
        time.sleep(1)
    rows=[r for r in rows if r["id"].startswith(body+"-")]
    json.dump({"source":"https://wavu.wiki/t/"+body.replace(' ','_')+"_movelist","license":"CC0-1.0 (wavu.wiki)","game":"Tekken 8","body":body,"moves":rows},open(OUT/f"{body.lower().replace(' ','_')}.json","w"),indent=1,ensure_ascii=False)
    print(body,len(rows)); time.sleep(1)
