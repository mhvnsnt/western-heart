#!/usr/bin/env python3
"""char064 recovery (Phase 5 Job 3a): group 0 packet 3 (63 verts) is a
batched strip of TWO rigid sub-objects (slots {19,20} then {23,24});
the slot transition at vert 42 coincides with a uvflag segment break
(vert 42 has uvflag=1, which starts a new face segment in the decoder's
own strip grammar). The stock decoder can only assign ONE palette
window per packet-piece, and no single window anchors all four
singleton islands, so the packet is dropped (1260 parsed -> 1197
placed). This script splits that one run at the segment break into
two runs (42 + 21 verts) and runs the decoder's standard pipeline
(assign_by_trusted_fit -> polish_by_faces -> assemble -> write_glb)
unchanged otherwise. Per-character isolation: char064 only."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ur_decode as U

def decode_split(ppk_path, glb_path, char_name, split_gi=0, split_pkt=3, split_at=42):
    data = open(ppk_path, 'rb').read()
    vmd = U.read_vmd(data)
    pal = dict(U.PALETTES)
    base = {tuple(v) for v in U.PALETTES.values()}
    base |= {tuple(v[::-1]) for v in U.PALETTES.values()}
    for name, vals in U.parse_header_palettes(vmd).items():
        if tuple(vals) not in base:
            pal[name] = vals
    U._ACTIVE_PALETTES = pal
    groups, runs = U.parse_groups(vmd)
    # split the target run at the segment break
    s, c = runs[split_gi][split_pkt]
    assert 0 < split_at < c, (s, c, split_at)
    runs[split_gi][split_pkt:split_pkt+1] = [(s, split_at), (s + split_at, c - split_at)]
    maxslot = -1
    for g in groups:
        for v in g:
            for inf in v['infs']:
                sl = U.slot_of(inf)
                if sl > maxslot: maxslot = sl
    if maxslot >= max(len(P) for P in pal.values()):
        node_max = U.parse_node_max(vmd)
        pal['ID'] = list(range(node_max + 1))
        U._ACTIVE_PALETTES = pal
    pieces, assign, fit_resid, W, parent, sct = U.assign_by_trusted_fit(groups, runs)
    assign, W, parent = U.polish_by_faces(pieces, assign, W, parent)
    W, parent, verts, faces, frame_resid = U.assemble(pieces, assign, W, parent)
    stats = U.write_glb(glb_path, W, parent, verts, faces, char_name)
    def pid_name(pid):
        gi, lo, hi = pid
        return f"g{gi}:{lo}-{hi}"
    stats['palette_families'] = sorted(pal.keys())
    stats['node_max'] = U.parse_node_max(vmd)
    stats['groups'] = len([g for g in groups if g])
    stats['total_verts_parsed'] = sum(len(g) for g in groups)
    stats['placed_verts'] = stats['verts']
    stats['assignment'] = {pid_name(pid): list(c) for pid, c in assign.items()}
    stats['frame_residuals'] = {pid_name(k): round(float(v), 5) for k, v in frame_resid.items()}
    stats['trusted_fit_residuals'] = {pid_name(k): round(float(v), 5) for k, v in fit_resid.items()}
    stats['split'] = dict(group=split_gi, packet=split_pkt, at_vert=split_at,
                          note="run split at uvflag segment break coinciding with slot-set transition {19,20}->{23,24}")
    return stats

if __name__ == '__main__':
    st = decode_split(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'char064')
    print(json.dumps(st, indent=1))
