#!/usr/bin/env python3
"""DOA4 phase 15 Job 1c prep: phase 6-12 package spans in mirror
coordinates. Per package: xpr2_offset from the phase-6 inventory
CSV; span end = max(offset+size) over every offset/size pair in the
package's assembly graph JSON (deep walk), falling back to the next
package's xpr2_offset in the same volume. Output JSON:
{volume: [{package, xpr2_offset, span_end, graph_file}]}."""
import csv, glob, json, os, re

REPO = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4'

def deep_max(node, best):
    if isinstance(node, dict):
        o, s = node.get('offset'), node.get('size')
        if isinstance(o, int) and isinstance(s, int):
            best[0] = max(best[0], o + s)
        for v in node.values(): deep_max(v, best)
    elif isinstance(node, list):
        for v in node: deep_max(v, best)
    return best[0]

def main():
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        rows = []
        with open(os.path.join(REPO, 'phase6', f'inventory-{vol}.csv')) as f:
            for r in csv.reader(f):
                if r: rows.append((r[0], int(r[1], 16)))
        rows.sort(key=lambda x: x[1])
        pkgs = []
        for i, (name, off) in enumerate(rows):
            nxt = rows[i + 1][1] if i + 1 < len(rows) else None
            g = None; end = nxt
            for cand in (f'{name}-skinned-graph.json', f'{name}_graph.json', f'{name}-graph.json'):
                p = os.path.join(REPO, 'assembly-graphs', cand)
                if os.path.exists(p):
                    g = cand
                    best = [off]
                    deep_max(json.load(open(p)), best)
                    if best[0] > off: end = best[0]
                    break
            pkgs.append({'package': name, 'xpr2_offset': off, 'span_end': end, 'graph': g})
        out[vol] = pkgs
        print(vol, len(pkgs), 'packages; graphs found', sum(1 for p in pkgs if p['graph']))
    json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p15/package_spans_p15.json', 'w'), indent=1)
    print('WROTE package_spans_p15.json')

if __name__ == '__main__':
    main()
