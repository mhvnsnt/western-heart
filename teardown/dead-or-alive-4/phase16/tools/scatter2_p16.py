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
piece (read from the ISO extraction on demand). The finest tier
runs in pattern batches of 60,000 to bound automaton memory.
All-zero pieces are recorded as 'zero' (they match everywhere;
not containment evidence) and excluded from the non-zero
coverage figure.

Dependency note: pyahocorasick (pip). The build available on
this VM is str-only, so patterns and the haystack are bridged
through latin-1 (1 char == 1 byte, byte-exact); all
verification is on raw bytes. Set PYTHONPATH to wherever the
package is installed when running.

RESUMABILITY: per-volume state (pieces found + missing spans)
is saved atomically after EVERY tier to
<scratch>/scatter2_state_<vol>.json; a killed run resumes at
the next tier. Final per-entry lines append to the output
JSONL only when a volume completes; reruns skip completed
(volume, name) pairs.

Per entry output: ordered piece list merged into segments
(entry_offset, mirror_offset, length), coverage % overall and
non-zero, verdict fully_scattered (>=99.9% non-zero coverage) /
scattered / absent_proven (0 verified pieces at every tier —
the Aho-Corasick pass is a whole-stream search, so a piece
with no verified candidate is absent at that piece size).
jan02.tpr is probed against ALL THREE streams at all tiers.

Entry bytes are asserted against the phase-15 map's sha256
before use (they come from the whole-ISO-verified extraction).
Usage: scatter2_p16.py <out.jsonl> [volume ...]
"""
import hashlib, json, mmap, os, sys
import ahocorasick

SCR = '/home/hatch/workspace/_doa4p16-scratch'
MAP15 = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase15/containment-map.json'
TIERS = [16384, 4096, 1024, 256]
WIN = 24
BATCH = 60000

def entry_bytes(vol, name):
    return open(os.path.join(SCR, 'afs_extract', vol, name), 'rb').read()

_CACHE = {}
def get_bytes(state, name):
    if name not in _CACHE:
        _CACHE.clear()
        _CACHE[name] = state[name]['bytes'] if state[name].get('bytes') else entry_bytes(state[name]['src'], name)
    return _CACHE[name]

def state_path(vol):
    return os.path.join(SCR, f'scatter2_state_{vol}.json')

def save_state(vol, state):
    tmp = state_path(vol) + '.tmp'
    json.dump(state, open(tmp, 'w'))
    os.replace(tmp, state_path(vol))

def run_tier(vol, state, stream_mm, stream_str, tier):
    jobs = []
    for name, st in state.items():
        nxt = []
        for (s, e) in st['missing']:
            o = s
            while o < e:
                ln = min(tier, e - o)
                blk = get_bytes(state, name)[o:o + ln]
                if blk.count(0) == len(blk):
                    st['pieces'].append([o, -2, ln, tier]); st['zero'] += ln
                else:
                    jobs.append((name, o, ln))
                o += ln
        st['missing'] = []
    found_count = 0
    bsz = 20000 if tier <= 256 else BATCH
    for b0 in range(0, len(jobs), bsz):
        batch = jobs[b0:b0 + bsz]
        auto = ahocorasick.Automaton()
        for idx, (name, o, ln) in enumerate(batch):
            auto.add_word(get_bytes(state, name)[o:o + WIN].decode('latin-1'), idx)
        auto.make_automaton()
        found = {}
        for end, idx in auto.iter(stream_str):
            if idx in found: continue
            name, o, ln = batch[idx]
            cand = end - WIN + 1
            if stream_mm[cand:cand + ln] == get_bytes(state, name)[o:o + ln]:
                found[idx] = cand
        for idx, (name, o, ln) in enumerate(batch):
            if idx in found:
                state[name]['pieces'].append([o, found[idx], ln, tier]); found_count += 1
            else:
                state[name]['missing'].append([o, o + ln])
        del auto
    print(f'{vol} tier {tier}: jobs {len(jobs)}, found {found_count}', flush=True)

def finalize(name, st):
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
    return {'size': n, 'matched_bytes': matched, 'zero_bytes': st['zero'],
            'missing_bytes': missing_b,
            'coverage_pct': round(100.0 * matched / n, 4) if n else 100.0,
            'coverage_nonzero_pct': round(100.0 * matched / (n - st['zero']), 4) if n - st['zero'] else 100.0,
            'segments': segs, 'n_pieces': len([1 for (_, p, _, _) in pieces if p >= 0]),
            'missing_spans': st['missing'][:64]}

def run_volume(vol, targets, stream_mm, stream_str, done, tag=''):
    """targets: list of (name, sha256, src_volume). State key includes tag."""
    key = vol + tag
    state = None
    if os.path.exists(state_path(key)):
        raw = json.load(open(state_path(key)))
        tiers_done = raw.pop('__tiers__', 0)
        state = {}
        for name, st in raw.items():
            st['bytes'] = None
            state[name] = st
        print(f'{key}: resumed state, tiers done: {tiers_done}', flush=True)
    else:
        state = {}
        for name, sha, src in targets:
            if (vol, name) in done and not tag: continue
            b = entry_bytes(src, name)
            assert hashlib.sha256(b).hexdigest() == sha, name
            state[name] = {'size': len(b), 'pieces': [], 'missing': [[0, len(b)]],
                           'zero': 0, 'bytes': None, 'src': src, 'sha256': sha}
            del b
        tiers_done = 0
    for ti, tier in enumerate(TIERS):
        if ti < tiers_done: continue
        run_tier(key, state, stream_mm, stream_str, tier)
        snap = {name: {k: v for k, v in st.items() if k != 'bytes'} for name, st in state.items()}
        snap['__tiers__'] = ti + 1
        save_state(key, snap)
    results = {name: finalize(name, st) for name, st in state.items()}
    if os.path.exists(state_path(key)): os.remove(state_path(key))
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
        targets = [(e['name'], e['sha256'], vol) for e in map15[vol]['entries']
                   if e['verdict'] in ('piecewise_unresolved', 'absent_windows')]
        print(f'{vol}: {len(targets)} targets', flush=True)
        spath = os.path.join(SCR, 'mirror_streams', vol + '.bin')
        with open(spath, 'rb') as f:
            stream_str = f.read().decode('latin-1')
        sf = open(spath, 'rb')
        stream_mm = mmap.mmap(sf.fileno(), 0, access=mmap.ACCESS_READ)
        res = run_volume(vol, targets, stream_mm, stream_str, done)
        stream_mm.close(); sf.close(); del stream_str
        for e in map15[vol]['entries']:
            if e['name'] not in res: continue
            r = res[e['name']]
            r.update({'volume': vol, 'name': e['name'], 'sha256': e['sha256'],
                      'phase15_verdict': e['verdict']})
            r['verdict'] = ('absent_proven' if r['matched_bytes'] == 0 else
                            'fully_scattered' if r['coverage_nonzero_pct'] >= 99.9 else 'scattered')
            out.write(json.dumps(r) + '\n'); out.flush()
            print(vol, e['name'], r['verdict'], r['coverage_pct'], '%', flush=True)
    if ('chrone', 'jan02.tpr') not in done:
        e = [x for x in map15['chrone']['entries'] if x['name'] == 'jan02.tpr'][0]
        per = {}
        for vol in ('chrone', 'chrtwo', 'chrthree'):
            spath = os.path.join(SCR, 'mirror_streams', vol + '.bin')
            with open(spath, 'rb') as f:
                stream_str = f.read().decode('latin-1')
            sf = open(spath, 'rb')
            stream_mm = mmap.mmap(sf.fileno(), 0, access=mmap.ACCESS_READ)
            res = run_volume(vol, [('jan02.tpr', e['sha256'], 'chrone')], stream_mm,
                             stream_str, set(), tag='_jan02')
            stream_mm.close(); sf.close(); del stream_str
            r = res['jan02.tpr']
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
