#!/usr/bin/env python3
"""DOA4 phase 16 Job 3: multi-resolution piecewise scatter.

Completes phase 15's pass-1/3 verdicts for the entries named in
phase15/containment-map.json with verdict piecewise_unresolved or
absent_windows (chrtwo 40, chrthree 107), plus jan02.tpr
cross-volume absence re-verification.

Method per entry (bytes from the verified ISO extraction):
- Resolution ladder over the entry: 16 KiB chunks, then the
  still-missing spans re-probed at 4 KiB, 1 KiB, and 256 B
  pieces. Each piece: search its first 64 B window (16 B for
  the 256 B tier's final partials, min(piece,64)) in the mmap'd
  mirror stream (all occurrences up to 8), verify the full piece
  at each candidate; record the first verified mirror offset.
- All-zero pieces are recorded as 'zero' (match everywhere; not
  containment evidence) and excluded from coverage %.
- Output per entry: ordered piece list (entry_offset,
  mirror_offset, length, tier) merged where adjacent pieces are
  contiguous in both spaces, coverage % (non-zero bytes matched /
  non-zero bytes total and overall), verdict:
  fully_scattered (>=99.9% non-zero coverage), scattered
  (partial), absent_proven (0 pieces at every tier).
- jan02.tpr is probed against ALL THREE streams at all tiers.
Resumable: appends one JSON line per entry to the output file;
reruns skip entries already present.
Usage: scatter2_p16.py <out.jsonl> [volume ...]
"""
import hashlib, json, mmap, os, struct, sys

SCR = '/home/hatch/workspace/_doa4p16-scratch'
MAP15 = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase15/containment-map.json'
TIERS = [16384, 4096, 1024, 256]

class Stream:
    def __init__(self, vol):
        self.path = os.path.join(SCR, 'mirror_streams', vol + '.bin')
        self.f = open(self.path, 'rb')
        self.mm = mmap.mmap(self.f.fileno(), 0, access=mmap.ACCESS_READ)
        self.size = os.path.getsize(self.path)
    def find_verified(self, piece, win):
        out = []
        p = self.mm.find(win)
        while p >= 0 and len(out) < 8:
            if self.mm[p:p + len(piece)] == piece:
                return p
            out.append(p)
            p = self.mm.find(win, p + 1)
        return -1

def scatter_entry(entry_bytes, stream):
    n = len(entry_bytes)
    pieces = []  # (entry_off, mirror_off, length, tier)
    missing = [(0, n)]
    for tier in TIERS:
        nxt = []
        for (s, e) in missing:
            o = s
            while o < e:
                ln = min(tier, e - o)
                blk = entry_bytes[o:o + ln]
                if blk.count(0) == len(blk):
                    pieces.append((o, -2, ln, tier))  # zero piece
                else:
                    win = blk[:min(64, ln)]
                    p = stream.find_verified(blk, win)
                    if p >= 0:
                        pieces.append((o, p, ln, tier))
                    else:
                        nxt.append((o, o + ln))
                o += ln
        missing = nxt
        if not missing: break
    pieces.sort()
    nz_total = sum(ln for (_, _, ln, _) in pieces if True)  # placeholder, computed below
    matched = sum(ln for (_, p, ln, _) in pieces if p >= 0)
    zero_b = sum(ln for (_, p, ln, _) in pieces if p == -2)
    missing_b = sum(e - s for (s, e) in missing)
    # merged segments (entry-contiguous AND mirror-contiguous, non-zero)
    segs = []
    for (o, p, ln, t) in pieces:
        if p < 0: continue
        if segs and o == segs[-1][0] + segs[-1][2] and p == segs[-1][1] + segs[-1][2]:
            segs[-1] = (segs[-1][0], segs[-1][1], segs[-1][2] + ln)
        else:
            segs.append((o, p, ln))
    return {'size': n, 'matched_bytes': matched, 'zero_bytes': zero_b,
            'missing_bytes': missing_b,
            'coverage_pct': round(100.0 * matched / n, 4) if n else 100.0,
            'coverage_nonzero_pct': round(100.0 * matched / (n - zero_b), 4) if n - zero_b else 100.0,
            'segments': segs, 'n_pieces': len([1 for (_, p, _, _) in pieces if p >= 0]),
            'missing_spans': missing[:64]}

def main():
    out_path = sys.argv[1]
    vols = sys.argv[2:] or ['chrtwo', 'chrthree']
    map15 = json.load(open(MAP15))
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p16.json')))
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            r = json.loads(line)
            done.add((r['volume'], r['name']))
    out = open(out_path, 'a')
    streams = {}
    def get_stream(vol):
        if vol not in streams: streams[vol] = Stream(vol)
        return streams[vol]
    targets = []
    for vol in vols:
        for e in map15[vol]['entries']:
            if e['verdict'] in ('piecewise_unresolved', 'absent_windows'):
                targets.append((vol, e))
    print(f'{len(targets)} scatter targets', flush=True)
    for vol, e in targets:
        if (vol, e['name']) in done: continue
        entry = open(os.path.join(SCR, 'afs_extract', vol, e['name']), 'rb').read()
        assert hashlib.sha256(entry).hexdigest() == e['sha256'], e['name']
        r = scatter_entry(entry, get_stream(vol))
        r.update({'volume': vol, 'name': e['name'], 'sha256': e['sha256'],
                  'phase15_verdict': e['verdict']})
        r['verdict'] = ('absent_proven' if r['matched_bytes'] == 0 else
                        'fully_scattered' if r['coverage_nonzero_pct'] >= 99.9 else 'scattered')
        out.write(json.dumps(r) + '\n'); out.flush()
        print(vol, e['name'], r['verdict'], r['coverage_pct'], '%', flush=True)
    # jan02.tpr: cross-volume absence re-verification at all tiers
    if ('chrone', 'jan02.tpr') not in done:
        e = [x for x in map15['chrone']['entries'] if x['name'] == 'jan02.tpr'][0]
        entry = open(os.path.join(SCR, 'afs_extract', 'chrone', 'jan02.tpr'), 'rb').read()
        assert hashlib.sha256(entry).hexdigest() == e['sha256']
        per = {}
        for vol in ('chrone', 'chrtwo', 'chrthree'):
            r = scatter_entry(entry, get_stream(vol))
            per[vol] = {'matched_bytes': r['matched_bytes'], 'coverage_pct': r['coverage_pct'],
                        'n_pieces': r['n_pieces']}
        rec = {'volume': 'chrone', 'name': 'jan02.tpr', 'sha256': e['sha256'],
               'phase15_verdict': e['verdict'], 'cross_volume': per,
               'verdict': 'absent_proven_cross_volume' if all(v['matched_bytes'] == 0 for v in per.values()) else 'scattered_cross_volume'}
        out.write(json.dumps(rec) + '\n'); out.flush()
        print('jan02.tpr cross-volume:', per, rec['verdict'], flush=True)
    out.close()
    print('SCATTER2 DONE')

if __name__ == '__main__':
    main()
