#!/usr/bin/env python3
"""DOA4 phase 16 Job 3: multi-resolution piecewise scatter (batched).

Completes phase 15's probe-grade verdicts for the entries named
in phase15/containment-map.json with verdict
piecewise_unresolved or absent_windows (chrtwo 40, chrthree 107),
plus jan02.tpr cross-volume absence re-verification.

Method (per volume): a resolution ladder over each entry —
16 KiB pieces, then still-missing spans re-probed at 4 KiB,
1 KiB, and 256 B. All pieces of all target entries at one tier
are searched in ONE Aho-Corasick pass (pyahocorasick) over the
mirror stream using each piece's first 24 bytes as the pattern;
every candidate is then verified byte-exact against the full
piece (read from the ISO extraction on demand). All-zero pieces
are recorded as 'zero' (they match everywhere; not containment
evidence) and excluded from the non-zero coverage figure.

Per entry output: ordered piece list merged into segments
(entry_offset, mirror_offset, length), coverage % overall and
non-zero, verdict fully_scattered (>=99.9% non-zero coverage) /
scattered / absent_proven (0 verified pieces at every tier —
the Aho-Corasick pass is a whole-stream search, so a piece with
no verified candidate is absent at that piece size, proven at
24 B window granularity and verified at full-piece size).
jan02.tpr is probed against ALL THREE streams at all tiers.

Entry bytes are asserted against the phase-15 map's sha256
before use (they come from the whole-ISO-verified extraction).
Resumable: one JSON line per entry appended to the output;
reruns skip completed (volume, name) pairs.
Usage: scatter2_p16.py <out.jsonl> [volume ...]
"""
import hashlib, json, os, sys
import ahocorasick  # pyahocorasick; this build is str-only, so all
# patterns and the haystack are bridged through latin-1 (1 char ==
# 1 byte, byte-exact); verification is always on raw bytes.

SCR = '/home/hatch/workspace/_doa4p16-scratch'
MAP15 = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase15/containment-map.json'
TIERS = [16384, 4096, 1024, 256]
WIN = 24

def entry_bytes(vol, name):
    return open(os.path.join(SCR, 'afs_extract', vol, name), 'rb').read()

def run_volume(vol, targets, stream_bytes, stream_str, out, done):
    """targets: list of (name, sha256, cross=False). Returns per-entry results."""
    state = {}  # name -> {'size':n, 'pieces':[(off,moff,len,tier)], 'missing':[(s,e)], 'zero':bytes}
    for name, sha, cross in targets:
        if (vol, name) in done: continue
        b = entry_bytes('chrone' if cross else vol, name)
        assert hashlib.sha256(b).hexdigest() == sha, name
        state[name] = {'size': len(b), 'pieces': [], 'missing': [(0, len(b))], 'zero': 0, 'bytes': b}
    for tier in TIERS:
        jobs = []  # (name, off, ln)
        for name, st in state.items():
            nxt = []
            for (s, e) in st['missing']:
                o = s
                while o < e:
                    ln = min(tier, e - o)
                    blk = st['bytes'][o:o + ln]
                    if blk.count(0) == len(blk):
                        st['pieces'].append((o, -2, ln, tier)); st['zero'] += ln
                    else:
                        jobs.append((name, o, ln))
                    o += ln
            st['missing'] = []
        if not jobs:
            break
        auto = ahocorasick.Automaton()
        for idx, (name, o, ln) in enumerate(jobs):
            auto.add_word(state[name]['bytes'][o:o + WIN].decode('latin-1'), idx)
        auto.make_automaton()
        found = {}
        for end, idx in auto.iter(stream_str):
            if idx in found: continue
            name, o, ln = jobs[idx]
            cand = end - WIN + 1
            if stream_bytes[cand:cand + ln] == state[name]['bytes'][o:o + ln]:
                found[idx] = cand
        still = {}
        for idx, (name, o, ln) in enumerate(jobs):
            if idx in found:
                state[name]['pieces'].append((o, found[idx], ln, tier))
            else:
                still.setdefault(name, []).append((o, o + ln))
        for name, spans in still.items():
            state[name]['missing'] = spans
        print(f'{vol} tier {tier}: jobs {len(jobs)}, found {len(found)}', flush=True)
    results = {}
    for name, st in state.items():
        pieces = sorted(st['pieces'])
        matched = sum(ln for (_, p, ln, _) in pieces if p >= 0)
        missing_b = sum(e - s for (s, e) in st['missing'])
        segs = []
        for (o, p, ln, t) in pieces:
            if p < 0: continue
            if segs and o == segs[-1][0] + segs[-1][2] and p == segs[-1][1] + segs[-1][2]:
                segs[-1] = (segs[-1][0], segs[-1][1], segs[-1][2] + ln)
            else:
                segs.append((o, p, ln))
        n = st['size']
        results[name] = {'size': n, 'matched_bytes': matched, 'zero_bytes': st['zero'],
                         'missing_bytes': missing_b,
                         'coverage_pct': round(100.0 * matched / n, 4) if n else 100.0,
                         'coverage_nonzero_pct': round(100.0 * matched / (n - st['zero']), 4) if n - st['zero'] else 100.0,
                         'segments': segs, 'n_pieces': len([1 for (_, p, _, _) in pieces if p >= 0]),
                         'missing_spans': st['missing'][:64]}
    return results

def main():
    out_path = sys.argv[1]
    vols = sys.argv[2:] or ['chrtwo', 'chrthree']
    map15 = json.load(open(MAP15))
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path):
            r = json.loads(line)
            done.add((r['volume'], r['name']))
    out = open(out_path, 'a')
    for vol in vols:
        targets = [(e['name'], e['sha256'], False) for e in map15[vol]['entries']
                   if e['verdict'] in ('piecewise_unresolved', 'absent_windows')]
        print(f'{vol}: {len(targets)} targets', flush=True)
        stream = open(os.path.join(SCR, 'mirror_streams', vol + '.bin'), 'rb').read()
        res = run_volume(vol, targets, stream, stream.decode('latin-1'), out, done)
        for e in map15[vol]['entries']:
            if e['name'] not in res: continue
            r = res[e['name']]
            r.update({'volume': vol, 'name': e['name'], 'sha256': e['sha256'],
                      'phase15_verdict': e['verdict']})
            r['verdict'] = ('absent_proven' if r['matched_bytes'] == 0 else
                            'fully_scattered' if r['coverage_nonzero_pct'] >= 99.9 else 'scattered')
            out.write(json.dumps(r) + '\n'); out.flush()
            print(vol, e['name'], r['verdict'], r['coverage_pct'], '%', flush=True)
        del stream
    # jan02.tpr cross-volume
    if ('chrone', 'jan02.tpr') not in done:
        e = [x for x in map15['chrone']['entries'] if x['name'] == 'jan02.tpr'][0]
        per = {}
        for vol in ('chrone', 'chrtwo', 'chrthree'):
            stream = open(os.path.join(SCR, 'mirror_streams', vol + '.bin'), 'rb').read()
            res = run_volume(vol, [('jan02.tpr', e['sha256'], True)], stream, stream.decode('latin-1'), out, set())
            r = res['jan02.tpr']
            per[vol] = {'matched_bytes': r['matched_bytes'], 'coverage_pct': r['coverage_pct'],
                        'n_pieces': r['n_pieces']}
            del stream
        rec = {'volume': 'chrone', 'name': 'jan02.tpr', 'sha256': e['sha256'],
               'phase15_verdict': e['verdict'], 'cross_volume': per,
               'verdict': 'absent_proven_cross_volume' if all(v['matched_bytes'] == 0 for v in per.values()) else 'scattered_cross_volume'}
        out.write(json.dumps(rec) + '\n'); out.flush()
        print('jan02.tpr cross-volume:', per, rec['verdict'], flush=True)
    out.close()
    print('SCATTER2 DONE')

if __name__ == '__main__':
    main()
