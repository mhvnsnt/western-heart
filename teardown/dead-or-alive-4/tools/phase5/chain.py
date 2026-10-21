import struct, json, numpy as np
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
links={o['index']: o['hie_node']['links'] for o in g['objects']}
nxt={}
for i,l in links.items():
    if l[0]<len(links): nxt[l[0]]=i
heads=[i for i in links if i not in nxt]
print('heads (no predecessor):', heads)
for h in heads:
    chain=[]; x=h
    while x is not None:
        chain.append(x); x=nxt.get(x)
    print(f'chain from {h}: {chain}')
