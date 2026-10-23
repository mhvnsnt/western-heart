import struct, sys, json, os
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch
AFS = {'chrtwo': (1578419712, 548042752)}
MAGICS = (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF')
CH = 1 << 23
name = sys.argv[1]
base, size = AFS[name]
outp = f'/home/hatch/workspace/_doa4p2-scratch/p6/{name}_pkgs.json'
hits = []
if os.path.exists(outp + '.partial'):
    hits = json.load(open(outp + '.partial'))
done_chunks = set(h.get('_chunk', -1) for h in hits)
carry = b''
nch = (size + CH - 1) // CH
for ci in range(nch):
    d = fetch(base + ci * CH, min(CH, size - ci * CH))
    if ci in done_chunks:
        carry = d[-60000:]; continue
    buf = carry + d; boff = ci * CH - len(carry)
    i = 0
    while True:
        j = buf.find(b'XPR2', i)
        if j < 0: break
        i = j + 1
        xp = boff + j
        if xp % 16: continue
        if j + 60000 > len(buf): continue
        recs = []; pos = j
        while pos < len(buf) - 16:
            m = buf[pos:pos + 4]
            if m in MAGICS:
                f1, f2, f3 = struct.unpack('>3I', buf[pos + 4:pos + 16])
                recs.append((m.decode(), f1, f2, f3)); pos += 16
            elif m == b'\x00' * 4: pos += 16
            else: break
        kinds = {}
        for r in recs: kinds[r[0]] = kinds.get(r[0], 0) + 1
        if kinds.get('USER', 0) >= 4:
            hits.append({'xp': xp, 'kinds': kinds, 'f2': recs[0][2], 'nrec': len(recs), '_chunk': ci})
            print('hit', hex(xp), kinds, flush=True)
    carry = d[-60000:]
    json.dump(hits, open(outp + '.partial', 'w'))
    print(f'chunk {ci}/{nch} hits={len(hits)}', flush=True)
for h in hits: h.pop('_chunk', None)
json.dump(hits, open(outp, 'w'), indent=1)
print(name, 'TOTAL', len(hits))
