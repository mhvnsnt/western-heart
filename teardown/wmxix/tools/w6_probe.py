#!/usr/bin/env python3
"""W6 probe: survey CAW .ymg layout across versions (run on the VM)."""
import sys, struct, math, random
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_extract as w

def s16(b, i): return struct.unpack('>h', b[i:i + 2])[0]
def u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def hdr(d):
    return dict(bones=u32(d, 0x10), skel=u32(d, 0x14), mats=u32(d, 0x18),
                mattab=u32(d, 0x1C), texn=u32(d, 0x24), gctc=u32(d, 0x38),
                base=u32(d, 0x54), t1=u32(d, 0x5C), skin=u32(d, 0x60))

def backward_run(d, end, maxstep=1500, maxcoord=8192):
    triples = []
    o = end - 6
    prev = None
    while o >= 0x80:
        t = (s16(d, o), s16(d, o + 2), s16(d, o + 4))
        if max(abs(x) for x in t) > maxcoord:
            break
        if prev is not None and dist(t, prev) > maxstep:
            break
        triples.append(t)
        prev = t
        o -= 6
    triples.reverse()
    return o + 6, triples

def main():
    iso = w.ISOFile()
    ymgs = sorted(p for p in iso.files
                  if p.startswith('edit_data/MODEL/') and p.endswith('.ymg'))
    byver = {}
    for p in ymgs:
        d = iso.read(p)
        if d[:4] == b'YOBJ':
            byver.setdefault(struct.unpack('>I', d[8:12])[0], []).append(p)
    random.seed(7)
    for ver in (0x30001, 0x40001, 0x40002, 0x40003, 0x30002):
        ps = byver.get(ver, [])
        print(f'=== version {ver:#x} ({len(ps)} files) ===')
        for p in random.sample(ps, min(6, len(ps))):
            d = iso.read(p)
            h = hdr(d)
            short = '/'.join(p.split('/')[-2:])
            found = None
            for end in (h['skel'], h['skel'] - 4, h['skel'] - 2):
                start, tris = backward_run(d, end)
                if len(tris) >= 20:
                    found = (end, start, len(tris))
                    break
            recs = [d[h['skin'] + r * 8:h['skin'] + r * 8 + 8].hex()
                    for r in range(4)]
            if found:
                end, start, n = found
                print(f'{short} size={len(d)} skin={h["skin"]:#x} '
                      f'skel={h["skel"]:#x} end={end:#x} run_start={start:#x} '
                      f'n={n} start-skin={start - h["skin"]}')
            else:
                print(f'{short} size={len(d)} skin={h["skin"]:#x} '
                      f'skel={h["skel"]:#x} NO-RUN')
            print(f'    skin recs: {recs}')
    iso.close()

if __name__ == '__main__':
    main()
