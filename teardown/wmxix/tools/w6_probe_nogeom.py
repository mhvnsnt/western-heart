#!/usr/bin/env python3
"""W6 probe: inspect NO-GEOMETRY CAW files + mpc stubs (VM)."""
import sys, struct, json
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import w6_decode2 as d2
import w6_extract as w

def main():
    iso = w.ISOFile()
    for p in ('edit_data/MODEL/Man/Gears/mz0_000/g0.ymg',
              'edit_data/MODEL/Man/Gears/mz0_034/g0.ymg',
              'edit_data/MODEL/Man/Gears/mz0_122/g0.ymg',
              'edit_data/MODEL/Man/Gears/mz0_038/g0.ymg'):
        d = iso.read(p)
        print(f'{p} size={len(d)} magic={d[:4]}')
        if len(d) >= 0x64 and d[:4] == b'YOBJ':
            skin = d2.u32(d, 0x60)
            skel = d2.u32(d, 0x14)
            print(f'  bones={d2.u32(d, 0x10)} skel={skel:#x} mats={d2.u32(d, 0x18)} '
                  f'skin={skin:#x} t1={d2.u32(d, 0x5c):#x} base={d2.u32(d, 0x54):#x}')
            for r in range(3):
                o = skin + r * 8
                if o + 8 <= len(d):
                    print(f'  rec{r}: {d[o:o + 8].hex()}')
            best = (0, None)
            for start in range(skin, min(skin + 200, len(d) - 6), 2):
                tris = d2.extend_run(d, start, len(d))
                if len(tris) > best[0]:
                    steps = [d2.dist(tris[i], tris[i + 1])
                             for i in range(len(tris) - 1)]
                    if d2.median(steps) < 400:
                        best = (len(tris), start)
            print(f'  best run anywhere: n={best[0]} at '
                  f'{best[1] and hex(best[1])}')
        else:
            print(f'  raw bytes: {d[:84].hex()}')
    # mpc stubs
    idx = json.load(open('/data/wmxix/tools-src/docs/WMXIX-MPC-INDEX.json'))
    mpc = iso.read('motion/move.mpc')
    for m in idx['motions']:
        for c in m['clips']:
            if m['motion_id'] in ('1500', '1501', '1502', '1504', '1506') \
                    and c['sub'] == '00C':
                off = 0x8240 + c['data_offset']
                raw = mpc[off:off + c['size_bytes']]
                print(f"stub {m['motion_id']}_00C size={c['size_bytes']} "
                      f"magic={raw[:8]!r} head={raw[:32].hex()}")
    iso.close()

if __name__ == '__main__':
    main()
