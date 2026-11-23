#!/usr/bin/env python3
"""W6 probe: brute-force smooth s16 runs in the remaining NO-GEOMETRY files."""
import sys, json
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_decode2 as d2
import w6_extract as w

def main():
    m = json.load(open('/data/wmxix/out/caw-mesh-manifest.json'))
    nogeom = [p for p, v in m['files'].items() if v['status'] == 'NO-GEOMETRY']
    print(f'NO-GEOMETRY: {len(nogeom)}')
    from collections import Counter
    cats = Counter(p.split('/')[3] if len(p.split('/')) > 3 else '?' for p in nogeom)
    print('by category:', dict(cats))
    sizes = sorted(m['files'][p]['size'] for p in nogeom)
    print(f'sizes: min={sizes[0]} med={sizes[len(sizes)//2]} max={sizes[-1]}')
    iso = w.ISOFile()
    # brute force: every even start in [skin, skel), runs of >=8 with med<800
    for p in nogeom[:12]:
        d = iso.read(p)
        if d[:4] == b'DUMY':
            d = d[0x18:]
        if len(d) < 0x64 or d[:4] != b'YOBJ':
            print(f'{p}: len={len(d)} magic={d[:4]!r} (degenerate)')
            continue
        skin, skel = d2.u32(d, 0x60), d2.u32(d, 0x14)
        best = (0, None, None)
        for start in range(skin, min(skel, len(d) - 6), 2):
            tris = d2.extend_run(d, start, min(skel, len(d)), maxcoord=8192,
                                 maxstep=2000)
            if len(tris) >= 8:
                steps = [d2.dist(tris[i], tris[i + 1])
                         for i in range(len(tris) - 1)]
                med = d2.median(steps)
                if med < 800 and len(tris) > best[0]:
                    best = (len(tris), start, med)
        print(f'{p}: size={len(d)} skin={skin:#x} skel={skel:#x} '
              f'best_run={best[0]} at {best[1] and hex(best[1])} '
              f'med={best[2]}')
    iso.close()

if __name__ == '__main__':
    main()
