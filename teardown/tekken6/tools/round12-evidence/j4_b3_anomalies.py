#!/usr/bin/env python3
"""Round 12 Job 4: B3 anomalies."""
import json, struct, zlib, collections, hashlib
CEN=json.load(open('/home/hatch/workspace/_t6r9-clone/teardown/tekken6/tools/round7-evidence/r7_census.json'))
cs=CEN['containers']
def classify(c):
    slots={s['slot']:s for s in c.get('slots',[])}
    if c['kind']=='B-texture': return 'B-texture'
    if c['kind']=='dir-other': return 'dir-other'
    magics={s['slot']:s['magic'] for s in c.get('slots',[])}
    sizes={s['slot']:s['size'] for s in c.get('slots',[])}
    has_bone=any(m=='BONE' for m in magics.values()); has_ndpp=any(m=='NDPP' for m in magics.values())
    full=(magics.get(1)=='BONE' and magics.get(0)=='NDPP' and magics.get(10)=='NDPP' and magics.get(12)=='BONE' and sizes.get(12)==1664)
    if full: return 'full-char'
    if sizes.get(0)==624 and sizes.get(9,0)>10000: return 'stage-pattern'
    if has_bone: return 'boned-part'
    if has_ndpp: return 'rigid-part'
    return 'A-other'
for c in cs: c['class']=classify(c)
anchors=[i for i,c in enumerate(cs) if c['class']=='full-char']
print('anchors:', len(anchors))
segs=[]
for k,a in enumerate(anchors):
    b=anchors[k+1] if k+1<len(anchors) else len(cs)
    segs.append((a,b))
lens=[b-a for a,b in segs]
print('segment lengths:', lens)
double=[k for k,(a,b) in enumerate(segs) if b-a>250]
print('double-size segments (>250):', double)
# slice decode machinery
WORK='/home/hatch/workspace/_t6r4-work'
OFF=38592*2048
with open(f'{WORK}/bulk_decrypted_r6.bin','rb') as fh:
    fh.seek(OFF); SLICE=fh.read(81591641)
print('slice read', len(SLICE))
def decode(c):
    j=c['rel']; w=struct.unpack('<5I', SLICE[j:j+20])
    return zlib.decompress(SLICE[j+20:j+20+w[4]])
def slot_starts(c):
    starts={}; pos=None
    n,hs=struct.unpack_from('<II', decode_cache(c),0) if False else (None,None)
    return None
# (a) interior scan of double segments
for k in double:
    a,b=segs[k]
    extra_bone=0; containers_with_extra=[]; name_hits=collections.Counter(); dup_sha=0
    seen=collections.Counter(cs[i]['sha256'] for i in range(a,b))
    dup_sha=sum(v-1 for v in seen.values() if v>1)
    bone_hdr_extra=[]
    for i in range(a,b):
        c=cs[i]; out=decode(c)
        slot_pos=set()
        # compute slot start offsets from pairs
        pos=struct.unpack_from('<II', out, 4)[0] if len(out)>=8 else 0
        # header size: use census pairs cumulative
        p=0
        starts=[]
        hdr=struct.unpack_from('<II', out, 0)[1]
        p=hdr
        for (s,e) in c.get('pairs',[]):
            if s: starts.append(p)
            p+=s
        slot_pos=set(starts)
        nb=out.count(b'BONE')
        slot_bone=sum(1 for s in c.get('slots',[]) if s['magic']=='BONE')
        if nb!=slot_bone:
            extra_bone+=nb-slot_bone; containers_with_extra.append((c['n'], nb, slot_bone))
        name_hits['kao_']+=out.count(b'kao_'); name_hits['MODEL_HEAD']+=out.count(b'MODEL_HEAD'); name_hits['chr_']+=out.count(b'chr_')
    print(f'seg {k} (n {a}..{b-1}, {b-a} containers): BONE fourcc beyond slot starts: {extra_bone}, containers w/ mismatch: {len(containers_with_extra)} {containers_with_extra[:5]}, names: {dict(name_hits)}, duplicate-sha extras: {dup_sha}')
# (b) stub segment 26
a,b=segs[26]
print(f'--- stub segment 26: containers n {a}..{b-1} ({b-a}) ---')
print(collections.Counter(cs[i]['class'] for i in range(a,b)))
for i in range(a,b):
    c=cs[i]
    print(f"  n={c['n']} kind={c['kind']} class={c['class']} len={c['len']} slots={[(s['slot'],s['magic'],s['size']) for s in c.get('slots',[])]}")
# (c) closing anchors BONE parse
for ai in (26,27):
    c=cs[anchors[ai]]
    out=decode(c)
    slots={s['slot']:s for s in c.get('slots',[])}
    print(f'--- anchor {ai}: n={c["n"]} len={c["len"]} slot1={slots.get(1)} slot12={slots.get(12)} ---')
    # locate slot1 bytes
    hdr=struct.unpack_from('<II', out, 0)[1]; p=hdr
    offs={}
    for (s,e) in c.get('pairs',[]):
        offs[len(offs)]=p; p+=s
    for slotno in (1,12):
        if slots.get(slotno) and slots[slotno]['magic']=='BONE':
            so=offs[slotno]; sec=out[so:so+slots[slotno]['size']]
            n=struct.unpack_from('<I', sec, 16)[0]
            table=struct.unpack_from('<8I', sec, 24)
            print(f'  slot{slotno}: size={len(sec)} bone count N at +16 = {n}, table={table}')
# BONE formula from known: parse idx00/idx04 top-76
import glob, os
def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out=[]; start=hs
    for i in range(n):
        szx, end = struct.unpack_from('<II', data, 8+i*8)
        out.append((start, szx)); start = end if end else start
    return out
for name,slotno in (('idx00',1),('idx00',12),('idx04',1),('idx04',12)):
    f=glob.glob(f'/home/hatch/workspace/_t6r4-work/decoded76/{name}_*.bin')[0]
    d=open(f,'rb').read(); o,s=slots_of(d)[slotno]; sec=d[o:o+s]
    n=struct.unpack_from('<I', sec, 16)[0]; table=struct.unpack_from('<8I', sec, 24)
    print(f'{name} slot{slotno}: BONE size={s} N={n} table={table} tail_after_names={s-(table[5]+32*n)}')
# (d) segment 27 stage cluster
a,b=segs[27]
stage=[cs[i] for i in range(a,b) if cs[i]['class']=='stage-pattern']
print(f'--- segment 27: {b-a} containers, stage-pattern {len(stage)} ---')
sigs=collections.Counter()
for c in stage:
    sig=tuple((s['slot'],s['magic'],s['size']) for s in c.get('slots',[]))
    sigs[sig]+=1
print('distinct full slot signatures among the 42:', len(sigs))
for sig,cnt in sigs.most_common(8): print('  x',cnt, sig)
print('stage cluster lens:', sorted(c['len'] for c in stage)[:5], '...', sorted(c['len'] for c in stage)[-5:])
print('slot9 sizes:', sorted({s['size'] for c in stage for s in c.get('slots',[]) if s['slot']==9})[:10])
