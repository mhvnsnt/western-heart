"""DOA4 Phase 6 batch driver: for one AFS, assemble + skin every package.
Window per package: [xp-0x360000, min(afs_size, xp+0xD00000, next_xp+0x360000)).
Per-package isolation: window bytes, graph, build all package-local.
Outputs: <tag>-skinned.glb, <tag>_graph.json, <tag>_report.txt in outdir;
appends inventory CSV rows. Usage: batch6.py <afs> <outdir> [start_idx]
"""
import sys, os, json, struct
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
sys.path.insert(0, '/home/hatch/workspace/_doa4p5-clone/teardown/dead-or-alive-4/tools')
from fetch import fetch
import doa4_assemble as A
import build6 as B

AFS = {
    'chrone':   (1212324864, 366094336),
    'chrtwo':   (1578419712, 548042752),
    'chrthree': (2135433728, 762955776),
}
SCR = '/home/hatch/workspace/_doa4p2-scratch/p6'

def run(afs, outdir, start=0):
    base, size = AFS[afs]
    hits = json.load(open(f'{SCR}/{afs}_pkgs.json'))
    hits = sorted(hits, key=lambda h: h['xp'])
    xps = [h['xp'] for h in hits]
    f2s = {h['xp']: h.get('f2', 0) for h in hits}
    os.makedirs(outdir, exist_ok=True)
    inv = open(os.path.join(outdir, 'inventory.csv'), 'a')
    for k, xp in enumerate(xps):
        if k < start: continue
        tag = f'{afs}-pkg{k:02d}'
        glb = os.path.join(outdir, f'{tag}-skinned.glb')
        if os.path.exists(glb):
            print(f'[{tag}] exists, skip', flush=True); continue
        nxt = xps[k + 1] if k + 1 < len(xps) else size
        w0 = max(0, xp - 0x360000)
        w1 = min(size, max(xp + 0xD00000, xp + f2s.get(xp, 0) + 0x300000))
        if k + 1 < len(xps): w1 = min(w1, nxt + 0x360000)
        print(f'[{tag}] xp={xp:#x} window [{w0:#x},{w1:#x}) {w1-w0} bytes', flush=True)
        data = fetch(base + w0, w1 - w0)
        winf = os.path.join(SCR, f'{tag}_win.bin')
        open(winf, 'wb').write(data)
        try:
            pkg = A.parse_package(data, xp - w0)
        except Exception as e:
            print(f'[{tag}] GRAPH PARSE FAIL: {e}', flush=True)
            inv.write(f'{tag},{xp:#x},0,0,0,0,0,GRAPH_FAIL:{type(e).__name__}\n'); inv.flush()
            os.remove(winf); continue
        worlds = A.world_matrices(pkg)
        for o, w in zip(pkg['objects'], worlds): o['world_matrix'] = w
        gf = os.path.join(outdir, f'{tag}_graph.json')
        json.dump(pkg, open(gf, 'w'))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report = B.build(winf, gf, glb, tag)
        open(os.path.join(outdir, f'{tag}_report.txt'), 'w').write(buf.getvalue())
        from collections import Counter
        q = Counter(r.split('[')[-1].rstrip(']') for r in report if '[' in r)
        nmesh = buf.getvalue().count('meshes ')
        meshes = [l for l in buf.getvalue().splitlines() if ' meshes ' in l]
        nm = int(meshes[-1].split()[-1]) if meshes else 0
        inv.write(f"{tag},{xp:#x},{pkg['object_count']},{len(report)},{nm},{q.get('clean',0)},{q.get('moderate',0)},{q.get('poor',0)}\n")
        inv.flush()
        os.remove(winf)
        print(f'[{tag}] done meshes={nm} quality={dict(q)}', flush=True)
    inv.close()

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
