"""Job 4: draw-order / sampler-slot hypothesis test on chrone pkg00.
Proven (phase 6, evidence-backed): decl1->tex30, decl12->tex40, decl30->tex40.
A positional rule maps a decl's position in some ordering to a texture in some
ordering. Test every combination of: decl orderings x texture orderings x
{direct index, mod-cycle} and check reproduction of ALL 3 proven assignments."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
import build6 as B
from tx2d_decode import parse_tx2d
d = open('/home/hatch/workspace/_doa4p2-scratch/p6/chrone_pkg00_window.bin','rb').read()
g = json.load(open('/home/hatch/workspace/_doa4p2-scratch/work/chrone_pkg00_graph.json'))
texs = parse_tx2d(d, g['xpr2_offset'])
decls = B.parse_decls(d, g)
print('textures:', len(texs), 'decls:', len(decls))
for i,t in enumerate(texs): print(f"  tex{i}: fmt={t['fmt']} off={t.get('offset')} size={t.get('size')}")
draw = [dd['decl_id'] for dd in decls]  # parse order = file/draw order
print('decl parse order:', draw)
proven = {1:30, 12:40, 30:40}
pos = {did:i for i,did in enumerate(draw)}
print('proven decl positions in draw order:', {k:pos[k] for k in proven})
# texture orderings
allidx = list(range(len(texs)))
diffuse = [i for i,t in enumerate(texs) if t['fmt'] in (18,20)]
byoff = sorted(allidx, key=lambda i: texs[i].get('offset') or 0)
bysize = sorted(allidx, key=lambda i: texs[i].get('size') or 0)
orderings = {'table': allidx, 'diffuse-only': diffuse, 'by-offset': byoff, 'by-size': bysize}
# decl orderings: draw order position, decl_id itself, per-object slot
slot = {}
seen = {}
for dd in decls:
    o = dd['obj']; slot[dd['decl_id']] = seen.get(o,0); seen[o] = seen.get(o,0)+1
declkeys = {'draw-pos': pos, 'decl-id': {did:did for did in draw}, 'obj-slot': slot}
hits = []
for dn, dk in declkeys.items():
    for tn, tl in orderings.items():
        for mode in ('direct','mod'):
            ok = True
            for did, want in proven.items():
                k = dk[did]
                got = tl[k] if (mode=='direct' and k < len(tl)) else (tl[k % len(tl)] if mode=='mod' else None)
                if got != want: ok = False; break
            if ok: hits.append((dn, tn, mode))
            # report direct-index results for the record
            if mode=='direct':
                res = {did: (tl[dk[did]] if dk[did] < len(tl) else None) for did in proven}
                print(f'{dn} x {tn} direct: {res} (want {proven})')
print('RULES REPRODUCING ALL 3:', hits if hits else 'NONE')
