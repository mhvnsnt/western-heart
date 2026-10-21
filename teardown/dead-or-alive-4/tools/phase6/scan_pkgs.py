import struct, sys, json
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch

AFS = {
    'chrone':   (1212324864, 366094336),
    'chrtwo':   (1578419712, 548042752),
    'chrthree': (2135433728, 762955776),
}
MAGICS = (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF')
CH = 1 << 23

def parse_dir(d, xp):
    recs = []; pos = xp
    while pos < len(d) - 16:
        m = d[pos:pos + 4]
        if m in MAGICS:
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16])
            recs.append((m.decode(), f1, f2, f3)); pos += 16
        elif m == b'\x00' * 4:
            pos += 16
        else:
            break
    return recs

def scan(name):
    base, size = AFS[name]
    nch = (size + CH - 1) // CH
    hits = []
    with ThreadPoolExecutor(5) as ex:
        chunks = list(ex.map(lambda i: fetch(base + i * CH, min(CH, size - i * CH)), range(nch)))
    print(f'{name}: fetched {sum(len(c) for c in chunks)} bytes', flush=True)
    carry = b''; coff = 0
    for ci, d in enumerate(chunks):
        buf = carry + d; boff = ci * CH - len(carry)
        i = 0
        while True:
            j = buf.find(b'XPR2', i)
            if j < 0: break
            i = j + 1
            xp = boff + j
            if xp % 16: continue
            if j + 60000 > len(buf): continue
            recs = parse_dir(buf, j)
            kinds = {}
            for r in recs: kinds[r[0]] = kinds.get(r[0], 0) + 1
            if kinds.get('USER', 0) >= 4:
                hits.append({'xp': xp, 'kinds': kinds, 'f2': recs[0][2], 'nrec': len(recs)})
        carry = d[-60000:]
    return hits

if __name__ == '__main__':
    name = sys.argv[1]
    hits = scan(name)
    json.dump(hits, open(f'/home/hatch/workspace/_doa4p2-scratch/p6/{name}_pkgs.json', 'w'), indent=1)
    for h in hits: print(name, hex(h['xp']), h['kinds'], 'f2', hex(h['f2']))
    print(name, 'TOTAL', len(hits))
