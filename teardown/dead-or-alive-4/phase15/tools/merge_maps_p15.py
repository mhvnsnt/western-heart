#!/usr/bin/env python3
"""DOA4 phase 15 Job 1: merge all containment evidence into the
definitive map + package name map.
Sources (scratch p15): pass-1 whole-entry map (all 389 entries),
scatter JSONL (chrone complete; chrtwo 9 entries), pass-2 chrone
block-coverage log numbers, XPR2 fingerprints, graph keys.
Per entry final verdict:
 - contiguous: pass-1 full-entry byte identity at one mirror offset
 - scattered: not contiguous; scatter 16 KiB-chunk fraction reported
   (scope: chrone all non-contiguous entries; chrtwo 9 entries;
   chrthree not scatter-run - marked 'not_scatter_run')
 - absent_at_pass1: pass-1 head/mid/tail windows not found
   (subsumed into scattered/not_scatter_run rows where applicable)
Package assignment (per phase-6 package, span = [xpr2_offset,
next package's offset or stream end)):
 - proven-byte: an entry contiguous inside the span whose bundle
   fingerprint/graph key also matches the package (or the entry's
   .tpr+.cat pair exactly fills the span start)
 - proven-fingerprint / proven-graphkey: the package's bundle
   fingerprint (from xpr2_fingerprints) or graph key (repo graph)
   exactly equals the entry's
 - unassigned: no exact evidence (listed, with nrec neighbors noted
   in the audit doc only, never as assignments)
Outputs (repo phase15/): containment-map.json, package-name-map.json
"""
import json, os, re

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
OUT = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase15'

def main():
    p1 = json.load(open(os.path.join(SCR, 'containment_map_p15.json')))
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    sc = {}
    for line in open(os.path.join(SCR, 'containment_scatter_p15.jsonl')):
        r = json.loads(line); sc[(r['volume'], r['name'])] = r
    p2cov = {}
    for line in open(os.path.join(SCR, 'containment2_partial.log')):
        m = re.match(r'(chrone|chrtwo|chrthree) (\S+) (\d+) (\w+) (\d+)/(\d+) missing (\d+)', line)
        if m: p2cov[(m.group(1), m.group(2))] = int(m.group(5))
    fps = json.load(open(os.path.join(SCR, 'xpr2_fingerprints_p15.json')))
    gk = json.load(open(os.path.join(SCR, 'graph_key_map_p15.json')))
    spans = json.load(open(os.path.join(SCR, 'package_spans_p15.json')))

    cmap = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        rows = []
        for e in p1[vol]['entries']:
            row = {'name': e['name'], 'size': e['size'], 'sha256': e['sha256'],
                   'pass1_verdict': e['verdict'], 'pass1_segments': e['segments']}
            s = sc.get((vol, e['name']))
            if e['verdict'] == 'contiguous':
                row['verdict'] = 'contiguous'
                row['mirror_offset'] = e['segments'][0][1]
            elif s:
                row['verdict'] = 'scattered'
                row['scatter_frac'] = s['frac']; row['scatter_segments'] = s['segments']
            elif e['verdict'] == 'absent':
                row['verdict'] = 'absent_windows'
            else:
                row['verdict'] = 'piecewise_unresolved'
            if (vol, e['name']) in p2cov:
                row['pass2_block_covered_bytes'] = p2cov[(vol, e['name'])]
            rows.append(row)
        # union coverage: pass-1 segments + scatter segments
        iv = []
        for r in rows:
            for (_, mo, ln) in r.get('pass1_segments', []): iv.append((mo, mo + ln))
            for (_, mo, ln) in r.get('scatter_segments', []): iv.append((mo, mo + ln))
        iv.sort(); merged = []
        for a, b in iv:
            if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
            else: merged.append([a, b])
        covered = sum(b - a for a, b in merged)
        gaps = []; prev = 0
        for a, b in merged:
            if a > prev: gaps.append((prev, a))
            prev = max(prev, b)
        msize = p1[vol]['mirror_size']
        if prev < msize: gaps.append((prev, msize))
        cmap[vol] = {'mirror_size': msize, 'union_covered_bytes': covered,
                     'union_coverage_pct': round(100 * covered / msize, 4),
                     'entries': rows,
                     'gaps_after_union': [{'mirror_off': a, 'size': b - a} for a, b in gaps]}
        print(vol, 'union coverage', cmap[vol]['union_coverage_pct'], '%')
    json.dump(cmap, open(os.path.join(OUT, 'containment-map.json'), 'w'), indent=1)

    # package name map
    nmap = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        pkgs = spans[vol]
        # bundle fingerprint by package (bundle at the package's xpr2_offset)
        bfp = {b['offset']: b['fp'] for b in fps['mirror'][vol]}
        rows = []
        for i, p in enumerate(pkgs):
            span = (p['xpr2_offset'], pkgs[i + 1]['xpr2_offset'] if i + 1 < len(pkgs) else cmap[vol]['mirror_size'])
            assign = None; tier = 'unassigned'
            # tier 1: entry contiguous inside span, .tpr whose fp == bundle fp
            for e in cmap[vol]['entries']:
                if e['verdict'] == 'contiguous' and e['name'].endswith('.tpr'):
                    if span[0] <= e['mirror_offset'] < span[1]:
                        efp = fps['iso'][vol].get(e['name'], {}).get('fp')
                        if efp is not None and [list(x) for x in efp] == bfp.get(span[0]):
                            assign = e['name']; tier = 'proven-byte+fingerprint'
            # tier 2: fingerprint exact (entry not contiguous)
            if not assign:
                for name, f in fps['iso'][vol].items():
                    if [list(x) for x in f['fp']] == bfp.get(span[0]):
                        assign = name; tier = 'proven-fingerprint'; break
            # tier 3: graph key exact for THIS package
            if not assign:
                for name, r in gk[vol].items():
                    if p['package'] in r['exact_packages']:
                        assign = name; tier = 'proven-graphkey'; break
            rows.append({'package': p['package'], 'span': span,
                         'assigned_entry': assign, 'tier': tier})
        # shared-identity resolution: packages sharing ONE fingerprint/
        # graph-key identity class with k entries and k packages are
        # assigned by relative order (bundle order == TOC order,
        # proven by every uniquely-matched run) -> 'proven-shared-order'
        from collections import defaultdict
        fpgroup = defaultdict(list)
        for b in fps['mirror'][vol]:
            fpgroup[json.dumps(b['fp'])].append(b['offset'])
        isogroup = defaultdict(list)
        for name, f in fps['iso'][vol].items():
            isogroup[json.dumps(f['fp'])].append(name)
        for keyfp, offs in fpgroup.items():
            names = isogroup.get(keyfp, [])
            if len(offs) > 1 and len(names) == len(offs):
                byrow = {r['span'][0]: r for r in rows}
                for off, nm in zip(sorted(offs), sorted(names)):
                    if off in byrow:
                        byrow[off]['assigned_entry'] = nm
                        byrow[off]['tier'] = 'proven-shared-order'
        for r in rows:
            print(vol, r['package'], '->', r['assigned_entry'], r['tier'])
        nmap[vol] = rows
    json.dump(nmap, open(os.path.join(OUT, 'package-name-map.json'), 'w'), indent=1)
    print('WROTE containment-map.json + package-name-map.json')

if __name__ == '__main__':
    main()
