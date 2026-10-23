#!/usr/bin/env python3
"""DOA4 phase 13 Job 3(a): TX2D texture-record identity census.

For every phase-6 package (148) parse the XPR2 directory from the
mirror release (range fetches via p6/fetch.py, AFS global offsets per
p6/scan_pkgs.py) and record, per TX2D record:
  L1 layout key = (fmt, endian, tiled, pitch_px, w, h)   [base excluded:
    pool offset is package-local layout, not content identity]
  L2 content hash = sha256 of the raw payload bytes the phase-6
    decoder consumes (size formula per fmt from p6/tx2d_decode.py).
Outputs JSON: per package -> list of {idx, l1, l2, fmt, w, h, base}.
Calibration controls: identical head copies (chrtwo pkg11-16 x6,
pkg35-40 x6, pkg44=45) must share 100% of L2 hashes; the 23 proven
head->body pairings (phase 10/11) measure whether proven pairs share
TX2D payloads at all (premise test for the pairing signal).
"""
import hashlib, json, struct, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch

AFS = {
    'chrone':   (1212324864, 366094336),
    'chrtwo':   (1578419712, 548042752),
    'chrthree': (2135433728, 762955776),
}
INV = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase6/inventory-%s.csv'
MAGICS = (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF')
WIN = 1 << 18  # 256KB directory window

def payload_need(fmt, pitch_px, wp, hp):
    wb, hb = max(wp // 4, 1), max(hp // 4, 1)
    if fmt == 18:
        return max(pitch_px // 4, wb) * max(hb, 32) * 8
    if fmt == 20:
        return max(pitch_px // 4, wb) * max(hb, 32) * 16
    if fmt == 6:
        return max(pitch_px, wp) * max(hp, 32) * 4
    return None

L1_ONLY = '--l1-only' in sys.argv

def census_pkg(afs_name, xp):
    base_afs, _ = AFS[afs_name]
    d = fetch(base_afs + xp, WIN)
    def u32(o): return struct.unpack('>I', d[o:o + 4])[0]
    if d[0:4] != b'XPR2':
        return {'error': 'no XPR2 at xp', 'head4': d[:4].hex()}
    hdr_f1 = u32(4)
    recs = []; pos = 0
    while pos < len(d) - 16:
        m = d[pos:pos + 4]
        if m in MAGICS:
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16])
            recs.append((m.decode(), f1, f2, f3)); pos += 16
        elif m == b'\x00' * 4:
            pos += 16
        else:
            break
    pool = xp + ((hdr_f1 + 0xFFF) & ~0xFFF)
    texs = []
    for (m, f1, f2, f3) in recs:
        if m != 'TX2D':
            continue
        if f1 + 40 > len(d):
            texs.append({'error': 'desc beyond window', 'f1': f1}); continue
        w = struct.unpack('>10I', d[f1:f1 + 40])
        dw0, dw1, dw2 = w[7], w[8], w[9]
        fmt = dw1 & 0x3F; endian = (dw1 >> 6) & 3; base = (dw1 >> 12) << 12
        pitch_px = ((dw0 >> 22) & 0x1FF) << 5; tiled = dw0 >> 31
        wp = (dw2 & 0x1FFF) + 1; hp = ((dw2 >> 13) & 0x1FFF) + 1
        need = payload_need(fmt, pitch_px, wp, hp)
        texs.append({'l1': [fmt, endian, tiled, pitch_px, wp, hp],
                     'desc_sha': hashlib.sha256(d[f1:f1 + 40]).hexdigest(),
                     'l2': None, 'fmt': fmt, 'w': wp, 'h': hp,
                     'base': base, 'need': need})
    # one pool-span fetch per package, slice payloads locally
    spans = [] if L1_ONLY else [(t['base'], t['need']) for t in texs
             if t['need'] is not None and t['need'] <= (1 << 24)]
    if spans:
        end = max(b + n for b, n in spans)
        pooldata = fetch(base_afs + pool, end)
        for t in texs:
            if t['need'] is not None and t['need'] <= (1 << 24):
                raw = pooldata[t['base']:t['base'] + t['need']]
                if len(raw) == t['need']:
                    t['l2'] = hashlib.sha256(raw).hexdigest()
    return {'nrec': len(recs), 'tex': texs}

def main():
    out = {}
    for afs_name in ('chrone', 'chrtwo', 'chrthree'):
        rows = [l.split(',') for l in open(INV % afs_name).read().splitlines() if l.strip()]
        for r in rows:
            name, xp = r[0], int(r[1], 16)
            out[name] = census_pkg(afs_name, xp)
            t = out[name]
            print(name, 'nrec', t.get('nrec'), 'tex', len(t.get('tex', [])),
                  'l2', sum(1 for x in t.get('tex', []) if x.get('l2')), flush=True)
    tag = 'texrecord_census_l1.json' if L1_ONLY else 'texrecord_census.json'
    json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p13/' + tag, 'w'), indent=1)
    print('WROTE', tag)

if __name__ == '__main__':
    main()
