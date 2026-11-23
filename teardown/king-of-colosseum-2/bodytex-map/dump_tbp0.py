import sys
sys.path.insert(0, '/home/hatch/workspace/nakamura-side-by-side/work/koc2-model')
from koc2_mdl_parse import parse_file
m = parse_file(sys.argv[1])
print(f"{sys.argv[1]}: {len(m['sections'])} sections")
for si, s in enumerate(m['sections']):
    tbp0s = []
    for p in s['packets']:
        blk6c = p['blk6c']; blk70 = p['blk70']
        tbp0 = blk6c & 0x3FFF
        tbp1 = (blk6c >> 14) & 0x3FFF  # guess: second field?
        tbp0s.append((tbp0, blk6c, blk70))
    xs=[]; ys=[]; zs=[]
    for p in s['packets']:
        for v in p['verts']:
            xs.append(v['pos'][0]); ys.append(v['pos'][1]); zs.append(v['pos'][2])
    rng = f"x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] z[{min(zs):.1f},{max(zs):.1f}]" if xs else ""
    uv=[]
    for p in s['packets']:
        for v in p['verts']:
            uv.append(v['uv'])
    uvr = f"u[{min(u[0] for u in uv):.2f},{max(u[0] for u in uv):.2f}] v[{min(u[1] for u in uv):.2f},{max(u[1] for u in uv):.2f}]" if uv else ""
    tb = " ".join(f"{t[0]:#06x}(w4={t[1]:#010x},w5={t[2]:#010x})" for t in tbp0s)
    print(f"sec{si:2d} type={s['type']} pkts={len(s['packets'])} {rng} {uvr}\n     TBP0: {tb}")
