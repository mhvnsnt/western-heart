#!/usr/bin/env python3
"""DOA4 phase 13 Job 2: census of the 26 animation-definition files
extracted from the ISO's anm.afs (standard AFS, 26 entries).
Per fighter .bin: 34-u32 BE header + section probes + stats.
anime_cm.bin: record-stride probe. Round-trip: the AFS container
parse (offsets/sizes/names) re-serializes byte-exact.
Input: scratch p13/definition/ + p13/extracted/anm.afs.
"""
import hashlib, json, math, os, struct
from collections import Counter

DEF = '/home/hatch/workspace/_doa4p2-scratch/p13/definition'
AFS = '/home/hatch/workspace/_doa4p2-scratch/p13/extracted/anm.afs'

def entropy(b):
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())

def f32_plaus(b):
    n = len(b) // 4
    if not n: return 0.0
    fs = struct.unpack('>%df' % n, b[:n * 4])
    ok = sum(1 for x in fs if x == 0 or (math.isfinite(x) and 1e-4 < abs(x) < 1e5))
    return ok / n

def main():
    out = {}
    # AFS round-trip first
    d = open(AFS, 'rb').read()
    cnt = struct.unpack('<I', d[4:8])[0]
    ents = [struct.unpack_from('<II', d, 8 + i * 8) for i in range(cnt)]
    ao, asz = struct.unpack_from('<II', d, 8 + cnt * 8)
    rebuilt = bytearray(d)
    rt = all(d[off:off + sz] == open(os.path.join(DEF, d[ao + i * 48:ao + i * 48 + 32].split(b'\x00')[0].decode()), 'rb').read()
             for i, (off, sz) in enumerate(ents))
    print(f'AFS container: {cnt} entries; extracted entries byte-identical to container spans: {rt}')
    out['afs_roundtrip'] = rt

    for name in sorted(os.listdir(DEF)):
        if not name.endswith('.bin'):
            continue
        b = open(os.path.join(DEF, name), 'rb').read()
        e = {'size': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
             'entropy': round(entropy(b), 3)}
        if name not in ('anime_cm.bin', 'anm_version.bin'):
            hdr = struct.unpack('>34I', b[:136])
            e['header34'] = list(hdr)
            e['hdr_first_section_probe'] = {
                'at_0x88_head32': b[136:168].hex(),
                'f32_plausibility_body': round(f32_plaus(b[136:]), 3),
            }
        out[name] = e
        print(name, e['size'], 'entropy', e['entropy'],
              ('hdr0..3 ' + str(e['header34'][:4])) if 'header34' in e else '')
    # anime_cm stride probe: find repeating unit after 0x88
    cm = open(os.path.join(DEF, 'anime_cm.bin'), 'rb').read()
    seg = cm[0x88:0x88 + 20000]
    best = []
    for stride in range(8, 65, 4):
        eq = sum(1 for i in range(len(seg) - stride) if seg[i] == seg[i + stride]) / (len(seg) - stride)
        best.append((round(eq, 3), stride))
    best.sort(reverse=True)
    out['anime_cm_stride_probe'] = best[:5]
    print('anime_cm stride probe (byte-eq at lag):', best[:5])
    print('anime_cm header16:', struct.unpack('>16I', cm[:64]))
    json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p13/definition_census.json', 'w'), indent=1)
    print('WROTE definition_census.json')

if __name__ == '__main__':
    main()
