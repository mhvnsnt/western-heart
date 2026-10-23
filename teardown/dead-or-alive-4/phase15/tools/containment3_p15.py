#!/usr/bin/env python3
"""DOA4 phase 15 Job 1 pass 3 (fine refinement): for entries whose
pass-2 coverage is < 95%, run a fine segment walk over the mirror:
anchor candidates from distinctive windows (entry offsets 0, 1/4,
1/2, 3/4; first 16 occurrences each); from the best anchor, extend
with 64 KiB chunk compares (C-speed) + bisection to the exact
divergence byte; at a divergence, continuation search tries the
entry windows at eo, eo+64, eo+128, eo+1024 within the next 8 MiB
of mirror (handles embedded-field rewrites and small insertions/
deletions on either side). Records segments + gap list (entry-side
gaps with sizes) so the audit can classify the divergence pattern.
Output: containment_fine_p15.json keyed by volume/name."""
import hashlib, json, os, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
PART = 524288000
MPARTS = [os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
          for n in (2, 3, 4, 5)]
MBASE = 2 * PART
MIRROR = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
          'chrthree': (2135433728, 762955776)}
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
    def find_all(self, win, cap=16, start=0, end=None):
        out = []; p = self.buf.find(win, start, end if end is not None else self.size)
        while p >= 0 and len(out) < cap:
            out.append(p); p = self.buf.find(win, p + 1, end if end is not None else self.size)
        return out

def extend(entry, eo, mir, mo):
    """Exact match length from (eo, mo) using chunk compares + bisect."""
    n = min(len(entry) - eo, mir.size - mo)
    lo = 0
    # chunk phase
    step = 65536
    done = 0
    while done + step <= n and entry[eo + done:eo + done + step] == mir.buf[mo + done:mo + done + step]:
        done += step
    # bisect the remainder
    lo, hi = done, min(n, done + step)
    # first ensure hi is a mismatch point or n
    while lo < hi:
        mid = (lo + hi) // 2
        if entry[eo:eo + mid + 1] == mir.buf[mo:mo + mid + 1]: lo = mid + 1
        else: hi = mid
    return lo

def fine_walk(entry, mir):
    n = len(entry)
    anchors = set()
    for frac in (0, n // 4, n // 2, (3 * n) // 4):
        win = entry[frac:frac + W]
        if len(win) < W: continue
        for p in mir.find_all(win):
            anchors.add(p - frac)
    best = None
    for base in sorted(a for a in anchors if a >= 0):
        segs = []; gaps = []
        eo, mo = 0, base
        # align: base was derived for one window; walk from entry 0 only
        # if base corresponds to entry offset 0 for the frac-0 anchor;
        # general case: start at the smallest anchor frac.
        # Simpler robust walk: start at (0, base) IF entry[:W] matches,
        # else start from the anchor's own frac.
        start_frac = 0
        if mir.buf[base:base + W] != entry[:W]:
            # find which frac this base came from
            ok = False
            for frac in (n // 4, n // 2, (3 * n) // 4):
                if mir.buf[base + frac:base + frac + W] == entry[frac:frac + W]:
                    start_frac = frac; ok = True; break
            if not ok: continue
        eo, mo = start_frac, base + start_frac
        if start_frac > 0: gaps.append((0, start_frac))
        while eo < n:
            k = extend(entry, eo, mir, mo)
            if k > 0:
                segs.append((eo, mo, k)); eo += k; mo += k
            if eo >= n: break
            # continuation: try entry windows at eo+delta in mirror [mo, mo+8MiB)
            found = None
            for delta in (0, 64, 128, 256, 1024, 4096):
                if eo + delta + W > n: break
                win = entry[eo + delta:eo + delta + W]
                for p in mir.find_all(win, cap=4, start=mo, end=min(mir.size, mo + (8 << 20))):
                    found = (eo + delta, p); break
                if found: break
            if not found: 
                gaps.append((eo, n - eo)); eo = n; break
            if found[0] > eo: gaps.append((eo, found[0] - eo))
            eo, mo = found
        cov = sum(s[2] for s in segs)
        if best is None or cov > best[0]:
            best = (cov, segs, gaps)
    if best is None: return 0, [], [(0, n)]
    return best

def main():
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    p2 = json.load(open(os.path.join(SCR, 'containment_map2_p15.json'))) if os.path.exists(
        os.path.join(SCR, 'containment_map2_p15.json')) else None
    # pass 2 may still be running; use pass-1 map for the <95% selection if needed
    p1 = json.load(open(os.path.join(SCR, 'containment_map_p15.json')))
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        mir = Mirror(vol)
        rows = {}
        for ent in man[vol + '.afs']['entries']:
            p1e = [e for e in p1[vol]['entries'] if e['name'] == ent['name']][0]
            if p1e['verdict'] == 'contiguous': continue
            entry = open(os.path.join(SCR, 'afs_extract', vol, ent['name']), 'rb').read()
            cov, segs, gaps = fine_walk(entry, mir)
            rows[ent['name']] = {'covered_bytes': cov, 'size': ent['size'],
                                 'frac': round(cov / ent['size'], 4) if ent['size'] else 1,
                                 'segments': segs,
                                 'gaps': gaps,
                                 'gap_sizes': sorted([g[1] for g in gaps], reverse=True)[:12]}
            print(vol, ent['name'], ent['size'], 'fine frac', rows[ent['name']]['frac'],
                  'segs', len(segs), 'gaps', len(gaps), flush=True)
        out[vol] = rows
        del mir
    json.dump(out, open(os.path.join(SCR, 'containment_fine_p15.json'), 'w'), indent=1)
    print('WROTE containment_fine_p15.json')

if __name__ == '__main__':
    main()
