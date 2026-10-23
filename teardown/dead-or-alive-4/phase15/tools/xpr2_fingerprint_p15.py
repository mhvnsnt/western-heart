#!/usr/bin/env python3
"""DOA4 phase 15 Job 1c: XPR2 directory fingerprints. Parses the
16 B-record directory (the phase-6 scan_pkgs method: records of
(magic, f1, f2, f3) while magic in {XPR2, USER, TX2D, VBUF, IBUF}
or zeros) at (a) every ISO .tpr entry start, (b) every 16-aligned
XPR2 occurrence in the mirror streams. A bundle's fingerprint =
the full (magic, f2) record sequence. Matching report: for each
ISO .tpr, mirror bundles with identical fingerprints, and the
best partial matches by common-prefix length + multiset overlap.
Output: xpr2_fingerprints_p15.json."""
import json, os, re, struct, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
PART = 524288000
MPARTS = [os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
          for n in (2, 3, 4, 5)]
MBASE = 2 * PART
MIRROR = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
          'chrthree': (2135433728, 762955776)}
MAGICS = (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF')

def parse_dir(d, pos):
    recs = []
    while pos + 16 <= len(d):
        m = d[pos:pos + 4]
        if m in MAGICS:
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16])
            recs.append((m.decode(), f1, f2, f3)); pos += 16
        elif m == b'\x00' * 4:
            pos += 16
        else:
            break
    return recs

def fp(recs):
    return [(k, f2) for (k, f1, f2, f3) in recs]

def load_mirror(name):
    off, size = MIRROR[name]
    buf = bytearray(); goff = off; left = size
    while left > 0:
        rel = goff - MBASE; pi, lo = rel // PART, rel % PART
        take = min(left, PART - lo)
        with open(MPARTS[pi], 'rb') as f:
            f.seek(lo); b = f.read(take)
        assert len(b) == take
        buf += b; goff += take; left -= take
    return bytes(buf)

def main():
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    out = {'iso': {}, 'mirror': {}}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        iso_fps = {}
        for ent in man[vol + '.afs']['entries']:
            if not ent['name'].endswith('.tpr'): continue
            d = open(os.path.join(SCR, 'afs_extract', vol, ent['name']), 'rb').read()
            recs = parse_dir(d, 0)
            iso_fps[ent['name']] = {'nrec': len(recs), 'fp': fp(recs)}
        out['iso'][vol] = iso_fps
        mir = load_mirror(vol)
        bundles = []
        for m in re.finditer(rb'XPR2', mir):
            p = m.start()
            if p % 16: continue
            recs = parse_dir(mir, p)
            kinds = {}
            for (k, _, _, _) in recs: kinds[k] = kinds.get(k, 0) + 1
            if kinds.get('USER', 0) >= 4:
                bundles.append({'offset': p, 'nrec': len(recs), 'fp': fp(recs)})
        out['mirror'][vol] = bundles
        print(vol, 'iso tpr fps:', len(iso_fps), 'mirror bundles:', len(bundles), flush=True)
        # exact fingerprint matches
        by_fp = {}
        for b in bundles: by_fp.setdefault(json.dumps(b['fp']), []).append(b['offset'])
        for name, f in iso_fps.items():
            hit = by_fp.get(json.dumps(f['fp']))
            if hit: print('  EXACT', vol, name, '-> mirror', hit, flush=True)
        del mir
    json.dump(out, open(os.path.join(SCR, 'xpr2_fingerprints_p15.json'), 'w'))
    print('WROTE xpr2_fingerprints_p15.json')

if __name__ == '__main__':
    main()
