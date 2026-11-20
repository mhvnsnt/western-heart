"""Round 7 census on the CLEAN bulk (bulk_decrypted_r6.bin, retained workdir).
Part 1: every embedded GZIP container in the entry-87 slice (offset
38592*2048, 81,591,641 B): zlib-decode (adler-verified), then classify by
the round-7 container directory: slot count (13=type A / 6=type B), slot
magics (NDPP/BONE/NTPP/...), sizes. Part 2: every literal NDPP occurrence
in the slice with its section header (size, flags) and chain validity.
Outputs r7_census.json next to this script. No game bytes are copied -
offsets/sizes/hashes only."""
import struct, zlib, json, collections, hashlib
WORK='/home/hatch/workspace/_t6r4-work'
OFF=38592*2048; SIZE=81591641
with open(f'{WORK}/bulk_decrypted_r6.bin','rb') as f:
    f.seek(OFF); data=f.read(SIZE)
print('slice', len(data))
# --- NDPP occurrences ---
ndpp=[]
i=0
while True:
    j=data.find(b'NDPP', i)
    if j<0: break
    size,flags=struct.unpack_from('<II', data, j+4) if j+12<=len(data) else (0,0)
    ndpp.append({'rel':j,'size':size,'flags':hex(flags),'size_sane':20<=size<=2_000_000 and j+size<=len(data)})
    i=j+4
print('NDPP occurrences:', len(ndpp), 'sane sizes:', sum(1 for n in ndpp if n['size_sane']))
# --- embedded GZIP containers ---
def classify(out):
    if len(out)<8: return {'kind':'tiny','len':len(out)}
    cnt,hdr=struct.unpack_from('<II', out, 0)
    if out[4:7]==b'COM': return {'kind':'COM-like','len':len(out)}
    if cnt not in (13,6) or hdr not in (8+8*cnt, 16+8*cnt):
        return {'kind':'other','len':len(out),'head':out[:16].hex()}
    pairs=[struct.unpack_from('<II', out, 8+k*8) for k in range(cnt)]
    slots=[]; pos=hdr
    for k,(s,e) in enumerate(pairs):
        if s: slots.append({'slot':k,'size':s,'end':e,'magic':out[pos:pos+4].decode('latin1')})
        pos+=s
    magics=[s['magic'] for s in slots]
    if cnt==13:
        kind='A-model' if 'NDPP' in magics else 'dir-other'
    else:
        kind='B-texture' if out[hdr:hdr+4]==b'NTPP' else 'dir-other'
    return {'kind':kind,'len':len(out),'slots':slots,'pairs':pairs,'tile_ok':pos==len(out)}
kinds=collections.Counter(); containers=[]; bad=0
i=0; idx=0
while True:
    j=data.find(b'GZIP', i)
    if j<0: break
    i=j+4
    if j+20>len(data): bad+=1; continue
    w=struct.unpack('<5I', data[j:j+20])
    if not (w[1]==1 and w[2]==1 and 0<w[4]<=len(data)-j-20 and 0<w[3]<50_000_000): bad+=1; continue
    body=data[j+20:j+20+w[4]]
    if body[:2]!=b'\x78\xda': bad+=1; continue
    try: out=zlib.decompress(body)
    except Exception: bad+=1; continue
    if len(out)!=w[3] or zlib.adler32(out)!=struct.unpack('>I', body[-4:])[0]: bad+=1; continue
    c=classify(out); kinds[c['kind']]+=1
    containers.append({'n':idx,'rel':j,'out_len':len(out),'sha256':hashlib.sha256(out).hexdigest(),**c})
    idx+=1
print('containers adler-exact:', idx, 'bad/skipped:', bad, 'kinds:', dict(kinds))
json.dump({'ndpp_count':len(ndpp),'ndpp':ndpp,'container_count':idx,'kinds':dict(kinds),'containers':containers},
          open('/home/hatch/workspace/_t6r4-work/wh/teardown/tekken6/tools/round7-evidence/r7_census.json','w'))
print('wrote r7_census.json')
