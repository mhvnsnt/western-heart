#!/usr/bin/env python3
"""DOA4 phase 15 Job 1 pass 2: block-level containment. For entries
that pass 1 did not prove contiguous, split into 64 KiB blocks; for
each block find candidate mirror positions via up to 3 probe windows
(block start / +50% / +75%, 64 B exact, first 8 occurrences each),
verify the block bytes at each candidate, and record the verified
segment. Adjacent block segments at consecutive mirror offsets are
merged. Verdicts: contiguous (pass-1 result, re-verified here when
the full compare succeeds at any head-window occurrence),
piecewise (>=1 verified block segment, not contiguous),
partial-head (only the head window's block differs - reported as
piecewise with the missing block list), absent (no verified block).
Also emits per-block missing lists for piecewise entries so the
audit shows exactly which bytes of an entry are not in the mirror.
Output: containment_map2_p15.json."""
import hashlib, json, os, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
PART = 524288000
MPARTS = [os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
          for n in (2, 3, 4, 5)]
MBASE = 2 * PART
MIRROR = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
          'chrthree': (2135433728, 762955776)}
BLK = 65536
W = 64

class Mirror:
    def __init__(self, name):
        off, size = MIRROR[name]
        self.size = size
        buf = bytearray(); goff = off; left = size
        while left > 0:
            rel = goff - MBASE; pi, lo = rel // PART, rel % PART
            take = min(left, PART - lo)
            with open(MPARTS[pi], 'rb') as f:
                f.seek(lo); b = f.read(take)
            assert len(b) == take
            buf += b; goff += take; left -= take
        self.buf = bytes(buf)
    def find_all(self, win, cap=8):
        out = []; p = self.buf.find(win)
        while p >= 0 and len(out) < cap:
            out.append(p); p = self.buf.find(win, p + 1)
        return out

def block_segment(entry, boff, mir):
    """Find the mirror position of entry block at boff, or None."""
    blk = entry[boff:boff + BLK]
    if len(blk) < W: return None
    for wfrac in (0, len(blk) // 2, (3 * len(blk)) // 4):
        win = blk[wfrac:wfrac + W]
        if len(win) < W: continue
        for p in mir.find_all(win):
            base = p - wfrac
            if base >= 0 and mir.buf[base:base + len(blk)] == blk:
                return base
    return None

def full_contiguous(entry, mir):
    """Try every occurrence of the head and a mid window."""
    n = len(entry)
    cands = set()
    for eo in (0, n // 3, (2 * n) // 3):
        win = entry[eo:eo + W]
        for p in mir.find_all(win, cap=16):
            cands.add(p - eo)
    for base in sorted(cands):
        if base >= 0 and mir.buf[base:base + n] == entry:
            return base
    return None

def audit_entry(entry, mir):
    base = full_contiguous(entry, mir)
    if base is not None:
        return 'contiguous', [(0, base, len(entry))], []
    segs = []; missing = []
    nblk = (len(entry) + BLK - 1) // BLK
    for bi in range(nblk):
        boff = bi * BLK
        blen = min(BLK, len(entry) - boff)
        if blen < W:
            missing.append(bi); continue
        p = block_segment(entry, boff, mir)
        if p is None: missing.append(bi)
        else: segs.append((boff, p, blen))
    # merge adjacent
    merged = []
    for s in segs:
        if merged and s[0] == merged[-1][0] + merged[-1][2] and s[1] == merged[-1][1] + merged[-1][2]:
            merged[-1] = (merged[-1][0], merged[-1][1], merged[-1][2] + s[2])
        else: merged.append(list(s))
    if not merged: return 'absent', [], missing
    return 'piecewise', [tuple(m) for m in merged], missing

def coverage(mir_size, all_segs):
    iv = sorted((mo, mo + ln) for segs in all_segs for (_, mo, ln) in segs)
    merged = []
    for a, b in iv:
        if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
        else: merged.append([a, b])
    covered = sum(b - a for a, b in merged)
    gaps = []; prev = 0
    for a, b in merged:
        if a > prev: gaps.append((prev, a))
        prev = max(prev, b)
    if prev < mir_size: gaps.append((prev, mir_size))
    return covered, gaps

def main():
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        mir = Mirror(vol)
        rows = []
        for ent in man[vol + '.afs']['entries']:
            entry = open(os.path.join(SCR, 'afs_extract', vol, ent['name']), 'rb').read()
            assert hashlib.sha256(entry).hexdigest() == ent['sha256']
            verdict, segs, missing = audit_entry(entry, mir)
            cov = sum(s[2] for s in segs)
            rows.append({'name': ent['name'], 'size': ent['size'], 'sha256': ent['sha256'],
                         'verdict': verdict, 'segments': segs, 'covered_bytes': cov,
                         'missing_blocks': missing})
            print(vol, ent['name'], ent['size'], verdict, f'{cov}/{ent["size"]}',
                  'missing', len(missing), flush=True)
        covered, gaps = coverage(mir.size, [r['segments'] for r in rows])
        gapinfo = []
        for a, b in gaps:
            g = mir.buf[a:b]
            gapinfo.append({'mirror_off': a, 'size': b - a,
                            'zero_fraction': round(g.count(0) / len(g), 4) if g else 0,
                            'head_hex': g[:32].hex()})
        out[vol] = {'mirror_size': mir.size, 'covered_bytes': covered,
                    'coverage_pct': round(100 * covered / mir.size, 4),
                    'entries': rows, 'gaps': gapinfo}
        print(vol, 'COVERAGE', out[vol]['coverage_pct'], '% gaps', len(gaps), flush=True)
        del mir
    json.dump(out, open(os.path.join(SCR, 'containment_map2_p15.json'), 'w'), indent=1)
    print('WROTE containment_map2_p15.json')

if __name__ == '__main__':
    main()
