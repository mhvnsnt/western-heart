#!/usr/bin/env python3
"""DOA4 phase 15 Job 1: containment audit. For every named entry of
the ISO's chrone/chrtwo/chrthree AFS containers (extracted by
afs_extract_p15.py from the VERIFIED ISO), locate its payload in the
corresponding MIRROR raw stream (extracted-tar parts 02-05, each
digest-verified by fetch_mirror_parts_p15.py before this runs).
Method per entry: exact search of the head 64B window; on a hit,
streaming full-entry compare at that offset (contiguous verdict).
On failure: probe head/mid/tail 64B windows independently; then a
segment walk — from the last matched position, compare forward in
64 KiB chunks and, at the first mismatch, search the next 64B
window of the entry within the following 4 MiB of mirror to find
the continuation segment (piecewise verdict with segment list).
Windows not found anywhere = absent (per window).
Outputs: containment_map_p15.json (per entry: name, size, sha256,
verdict, segments) + coverage stats per volume (union of covered
mirror intervals; gap list with sizes/zero-fraction/head hex)."""
import hashlib, json, os, struct, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
PART = 524288000
MPARTS = [os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
          for n in (2, 3, 4, 5)]
MBASE = 2 * PART  # tar offset where part-02 begins
MIRROR = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
          'chrthree': (2135433728, 762955776)}
W = 64

class Mirror:
    """Memory-mapped-ish access: load the volume once (<=763 MB)."""
    def __init__(self, name):
        off, size = MIRROR[name]
        self.size = size
        buf = bytearray()
        goff = off; left = size
        while left > 0:
            rel = goff - MBASE
            pi, lo = rel // PART, rel % PART
            take = min(left, PART - lo)
            with open(MPARTS[pi], 'rb') as f:
                f.seek(lo); b = f.read(take)
            assert len(b) == take
            buf += b; goff += take; left -= take
        self.buf = bytes(buf)

def segments_for(entry, mir):
    """Return (verdict, segments list of (entry_off, mirror_off, len))."""
    n = len(entry)
    head = entry[:W]
    p = mir.buf.find(head)
    if p >= 0:
        if mir.buf[p:p + n] == entry:
            return 'contiguous', [(0, p, n)]
    # window probes
    probes = {}
    for label, eo in (('head', 0), ('mid', max(0, n // 2 - W // 2)), ('tail', max(0, n - W))):
        probes[label] = mir.buf.find(entry[eo:eo + W])
    found = {k: v for k, v in probes.items() if v >= 0}
    if not found:
        return 'absent', []
    if 'head' not in found:
        return 'piecewise', [(eo, mo, W) for eo, mo in
                             ((0, probes['head']), (max(0, n // 2 - W // 2), probes['mid']),
                              (max(0, n - W), probes['tail'])) if mo >= 0]
    # segment walk from head
    segs = []
    eo, mo = 0, found['head']
    while eo < n:
        # extend while equal
        mx = min(n - eo, mir.size - mo)
        k = 0
        while k < mx and entry[eo + k] == mir.buf[mo + k]:
            k += 1
        if k:
            segs.append((eo, mo, k)); eo += k; mo += k
        if eo >= n: break
        # find continuation: next 64B window of entry at/after mo, within 4 MiB
        win = entry[eo:eo + W]
        q = mir.buf.find(win, mo, min(mir.size, mo + (4 << 20)))
        if q < 0:
            return 'piecewise', segs
        mo = q
    return 'piecewise', segs

def coverage(mir_size, all_segs):
    iv = sorted((mo, mo + ln) for _, segs in all_segs for (_, mo, ln) in segs)
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    covered = sum(b - a for a, b in merged)
    gaps = []
    prev = 0
    for a, b in merged:
        if a > prev: gaps.append((prev, a))
        prev = max(prev, b)
    if prev < mir_size: gaps.append((prev, mir_size))
    return covered, merged, gaps

def main():
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        mir = Mirror(vol)
        info = man[vol + '.afs']
        rows = []
        for ent in info['entries']:
            path = os.path.join(SCR, 'afs_extract', vol, ent['name'])
            entry = open(path, 'rb').read()
            assert len(entry) == ent['size'] and hashlib.sha256(entry).hexdigest() == ent['sha256']
            verdict, segs = segments_for(entry, mir)
            rows.append({'name': ent['name'], 'size': ent['size'], 'sha256': ent['sha256'],
                         'verdict': verdict, 'segments': segs})
            print(vol, ent['name'], ent['size'], verdict, len(segs), flush=True)
        covered, merged, gaps = coverage(mir.size, [(r['name'], r['segments']) for r in rows])
        gapinfo = []
        for a, b in gaps:
            g = mir.buf[a:b]
            zf = (g.count(0) / len(g)) if g else 0
            gapinfo.append({'mirror_off': a, 'size': b - a, 'zero_fraction': round(zf, 4),
                            'head_hex': g[:32].hex()})
        out[vol] = {'mirror_size': mir.size, 'covered_bytes': covered,
                    'coverage_pct': round(100 * covered / mir.size, 4),
                    'entries': rows, 'gaps': gapinfo}
        print(vol, 'coverage', out[vol]['coverage_pct'], '% gaps', len(gaps), flush=True)
        del mir
    json.dump(out, open(os.path.join(SCR, 'containment_map_p15.json'), 'w'), indent=1)
    print('WROTE containment_map_p15.json')

if __name__ == '__main__':
    main()
