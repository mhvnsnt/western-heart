#!/usr/bin/env python3
"""DOA4 phase 16 Job 3: merge scatter2 results into an updated
machine-readable containment map (ADDITIVE: the phase-15 map is
copied in full; per-entry phase-16 results are attached as
'p16_scatter' and the entry verdict is superseded ONLY where the
scatter pass changes it, each change logged in 'p16_changes').
Also recomputes union coverage per volume with phase-16 segments
included. Usage: merge_map2_p16.py <scatter2.jsonl> <out.json>
"""
import json, sys

MAP15 = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase15/containment-map.json'

def union_len(pairs):
    tot = 0; cur = None
    for s, e in sorted(pairs):
        if cur is None or s > cur[1]:
            if cur: tot += cur[1] - cur[0]
            cur = [s, e]
        else:
            cur[1] = max(cur[1], e)
    if cur: tot += cur[1] - cur[0]
    return tot

def main():
    scat = {}
    jan02 = None
    for line in open(sys.argv[1]):
        r = json.loads(line)
        if r['name'] == 'jan02.tpr' and 'cross_volume' in r:
            jan02 = r
        else:
            scat[(r['volume'], r['name'])] = r
    m = json.load(open(MAP15))
    changes = []
    for vol in ('chrtwo', 'chrthree'):
        extra_segs = []
        for e in m[vol]['entries']:
            r = scat.get((vol, e['name']))
            if not r: continue
            e['p16_scatter'] = {'verdict': r['verdict'], 'coverage_pct': r['coverage_pct'],
                                'coverage_nonzero_pct': r['coverage_nonzero_pct'],
                                'matched_bytes': r['matched_bytes'], 'zero_bytes': r['zero_bytes'],
                                'missing_bytes': r['missing_bytes'], 'segments': r['segments'],
                                'n_pieces': r['n_pieces'], 'missing_spans': r['missing_spans']}
            newv = {'fully_scattered': 'scattered', 'scattered': 'scattered',
                    'absent_proven': 'absent_proven'}[r['verdict']]
            if newv != e['verdict']:
                changes.append({'volume': vol, 'name': e['name'],
                                'phase15_verdict': e['verdict'], 'phase16_verdict': newv,
                                'coverage_pct': r['coverage_pct']})
                e['verdict'] = newv
            extra_segs += [(s[1], s[1] + s[2]) for s in r['segments']]
        # union coverage: phase-15 segments (entry space -> mirror space is
        # per entry; union must be in MIRROR space)
        mir = []
        for e in m[vol]['entries']:
            for (eo, mo, ln) in e.get('pass1_segments', []):
                mir.append((mo, mo + ln))
            if 'p16_scatter' in e:
                for (eo, mo, ln) in e['p16_scatter']['segments']:
                    mir.append((mo, mo + ln))
        u = union_len(mir)
        m[vol]['p16_union_covered_bytes'] = u
        m[vol]['p16_union_coverage_pct'] = round(100.0 * u / m[vol]['mirror_size'], 4)
    if jan02:
        for e in m['chrone']['entries']:
            if e['name'] == 'jan02.tpr':
                e['p16_jan02_cross_volume'] = jan02['cross_volume']
                e['p16_jan02_verdict'] = jan02['verdict']
    m['p16_changes'] = changes
    m['p16_scatter_source'] = 'phase16/tools/scatter2_p16.py multi-resolution (16K/4K/1K/256B) mmap scatter'
    json.dump(m, open(sys.argv[2], 'w'), indent=1)
    print(f'changes: {len(changes)}')
    for c in changes: print(c)
    for vol in ('chrtwo', 'chrthree'):
        print(vol, 'union coverage p15', m[vol].get('union_coverage_pct'), '-> p16', m[vol]['p16_union_coverage_pct'])
    if jan02: print('jan02.tpr:', jan02['verdict'], jan02['cross_volume'])

if __name__ == '__main__':
    main()
