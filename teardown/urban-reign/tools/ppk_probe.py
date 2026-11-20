#!/usr/bin/env python3
"""Probe a Namco PPK package: header + inner chunk census.
PPK header (from stage028.ppk probe):
  @0: magic 'ppk\\0'
  @4: total size field
  @8: 0x200 (512) — data offset
"""
import struct, sys, os, collections

def probe(path):
    d = open(path, 'rb').read()
    if d[:4] != b'ppk\x00':
        return {'file': path, 'magic': repr(d[:4]), 'error': 'not a ppk'}
    total = struct.unpack('<I', d[4:8])[0]
    dataoff = struct.unpack('<I', d[8:12])[0]
    out = {'file': os.path.basename(path), 'len': len(d), 'total_field': total,
           'data_offset': dataoff}
    # scan body for 4-byte ASCII tags (printable) at aligned offsets
    tags = collections.Counter()
    for i in range(dataoff, len(d) - 4, 4):
        w = d[i:i+4]
        if all(32 <= b < 127 or b == 0 for b in w) and w.strip(b'\x00'):
            t = w.decode('ascii', 'replace')
            if len(t.strip('\x00')) >= 2:
                tags[w] += 1
    out['top_tags'] = [(t.hex(), n) for t, n in tags.most_common(20)]
    # look for sub-file magic signatures anywhere
    sigs = {b'NMD\x00': 'NMD(model?)', b'TM2\x00': 'TIM2(texture)', b'NUD\x00': 'NUD', b'ppk\x00': 'nested ppk'}
    found = {}
    for s, name in sigs.items():
        idxs = []
        i = d.find(s)
        while i != -1:
            idxs.append(i)
            i = d.find(s, i+1)
        if idxs: found[name] = idxs[:10]
    out['signatures'] = found
    return out

if __name__ == '__main__':
    import json
    res = [probe(p) for p in sys.argv[1:]]
    print(json.dumps(res, indent=1))
