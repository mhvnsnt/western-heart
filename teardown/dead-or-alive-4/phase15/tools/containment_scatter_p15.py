#!/usr/bin/env python3
"""DOA4 phase 15 Job 1 pass 3 (scatter map): for entries with low
coarse coverage, split into 16 KiB chunks; per chunk, find the
chunk's 64 B head window in the mirror (first 4 occurrences) and
verify the full chunk at each candidate; record the verified
mirror offset (or absent). Chunks of all-zero bytes are recorded
as 'zero' (they match everywhere; not evidence). Output per entry:
chunk map (entry chunk index -> mirror offset or -1) merged into
segments, matched fraction. Resumable: appends per-entry JSON
lines to containment_scatter_p15.jsonl as entries complete."""
import hashlib, json, os, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
PART = 524288000
MPARTS = [os.path.join(SCR, 'mirrorparts', f'doa4-mirror-extracted-20261017.tar.part-{n:02d}')
          for n in (2, 3, 4, 5)]
MBASE = 2 * PART
MIRROR = {'chrone': (1212324864, 366094336), 'chrtwo': (1578419712, 548042752),
          'chrthree': (2135433728, 762955776)}
CH = 16384
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
    def find_all(self, win, cap=4):
        out = []; p = self.buf.find(win)
        while p >= 0 and len(out) < cap:
            out.append(p); p = self.buf.find(win, p + 1)
        return out

def scatter(entry, mir):
    n = len(entry)
    chunks = []
    for co in range(0, n, CH):
        blk = entry[co:co + CH]
        if blk.count(0) == len(blk):
            chunks.append((co, -2)); continue  # zero chunk: uninformative
        hit = -1
        for p in mir.find_all(blk[:W]):
            if mir.buf[p:p + len(blk)] == blk:
                hit = p; break
        chunks.append((co, hit))
    segs = []
    for co, p in chunks:
        if p < 0: continue
        ln = min(CH, n - co)
        if segs and co == segs[-1][0] + segs[-1][2] and p == segs[-1][1] + segs[-1][2]:
            segs[-1] = (segs[-1][0], segs[-1][1], segs[-1][2] + ln)
        else: segs.append((co, p, ln))
    matched = sum(s[2] for s in segs)
    return matched, segs, chunks

def main():
    vol = sys.argv[1]
    names = sys.argv[2:]
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    mir = Mirror(vol)
    out = open(os.path.join(SCR, 'containment_scatter_p15.jsonl'), 'a')
    for ent in man[vol + '.afs']['entries']:
        if names and ent['name'] not in names: continue
        entry = open(os.path.join(SCR, 'afs_extract', vol, ent['name']), 'rb').read()
        matched, segs, chunks = scatter(entry, mir)
        rec = {'volume': vol, 'name': ent['name'], 'size': ent['size'],
               'matched_bytes': matched, 'frac': round(matched / ent['size'], 4) if ent['size'] else 1,
               'segments': segs, 'chunks_found': sum(1 for _, p in chunks if p >= 0),
               'chunks_zero': sum(1 for _, p in chunks if p == -2),
               'chunks_total': len(chunks)}
        out.write(json.dumps(rec) + '\n'); out.flush()
        print(vol, ent['name'], ent['size'], 'scatter frac', rec['frac'], 'segs', len(segs), flush=True)
    out.close()
    print('SCATTER DONE', vol)

if __name__ == '__main__':
    main()
