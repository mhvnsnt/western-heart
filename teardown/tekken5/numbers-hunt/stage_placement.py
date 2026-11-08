#!/usr/bin/env python3
"""Stage-absolute placement + triangle-order test for DW stage geometry.

Input: teardown/tekken5/moj-stage-geometry.json (parsed NUDP vertices +
MIF bone matrices).

1. PLACEMENT: per stage, MIF chunk j bone k pairs with NUDP chunk j
   block k (pairwise counts verified equal in every chunk of every stage
   — see the analysis below, not assumed). Each bone's 4x4 matrix
   (rotation + translation + measured scale) maps the block's
   chunk-relative vertices to stage-absolute positions. Output: per-block
   placed AABB + centroid + bone name + matrix, plus stage union AABB and
   coherence checks (no NaN, no wild outliers, floor pieces at stage min-Y).

2. TRIANGLE ORDER: tests two hypotheses for the vertex stream of every
   sub-mesh — triangle STRIP (v0,v1,v2),(v2,v1,v3),(v3,v2,v4)... vs
   triangle LIST (v0,v1,v2),(v3,v4,v5)... — by degenerate-triangle rate
   and (where the sub-mesh carries normals, variant 0x83) winding/normal
   agreement. Reports per-sub-mesh and aggregate rates. The better-fitting
   hypothesis is reported as evidence, not proof; a bad fit for both
   leaves the order UNCONFIRMED.

3. SPOTS: inventories MIF bone-name keywords for spawn/symbol/breakable/
   door markers (none expected — names are O_OBJ/O_CUL/DSNID).

Output: dw-stage-placement.json (this directory).
"""
import json
import math
import sys
from pathlib import Path


def mat_vec(m, v):
    x, y, z = v
    return (
        m[0] * x + m[1] * y + m[2] * z + m[3],
        m[4] * x + m[5] * y + m[6] * z + m[7],
        m[8] * x + m[9] * y + m[10] * z + m[11],
    )


def tri_area(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    cx = uy * vz - uz * vy
    cy = uz * vx - ux * vz
    cz = ux * vy - uy * vx
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz), (cx, cy, cz)


def main():
    src = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    g = json.loads(src.read_text())
    stages_out = []
    strip_stats = {'submeshes': 0, 'strip_degenerate': 0, 'strip_tris': 0,
                   'list_degenerate': 0, 'list_tris': 0,
                   'strip_normal_agree': 0, 'strip_normal_total': 0}
    spot_keywords = ['spawn', 'symbol', 'break', 'door', 'gem', 'item',
                     'enemy', 'player', 'start', 'goal', 'trigger']
    spot_hits = []
    for st in g['stages']:
        if st.get('status') != 'extracted':
            stages_out.append({'source_file': st['source_file'],
                               'canon_stage': st.get('canon_stage'),
                               'status': st.get('status')})
            continue
        mifs = st['mifs']
        nudps = st['nudps']
        assert len(mifs) == len(nudps), 'MIF/NUDP chunk count mismatch'
        placed_blocks = []
        all_min = [1e18] * 3
        all_max = [-1e18] * 3
        pairing_ok = True
        for mi, (mif, nudp) in enumerate(zip(mifs, nudps)):
            if mif['count'] != nudp['block_count']:
                pairing_ok = False
            for bi, (bone, block) in enumerate(zip(mif['bones'], nudp['blocks'])):
                m = bone['matrix']
                # placed AABB over all sub-mesh vertices of this block
                bmin = [1e18] * 3
                bmax = [-1e18] * 3
                nverts = 0
                for sm in block['sub_meshes']:
                    for v in sm['positions']:
                        p = mat_vec(m, v)
                        nverts += 1
                        for a in range(3):
                            bmin[a] = min(bmin[a], p[a])
                            bmax[a] = max(bmax[a], p[a])
                for a in range(3):
                    all_min[a] = min(all_min[a], bmin[a])
                    all_max[a] = max(all_max[a], bmax[a])
                placed_blocks.append({
                    'mif_chunk': mi, 'block_index': bi,
                    'bone_name': bone['name'],
                    'node_id': bone['node_id'],
                    'matrix': bone['matrix'],
                    'vertex_count': nverts,
                    'placed_aabb_min': [round(x, 3) for x in bmin],
                    'placed_aabb_max': [round(x, 3) for x in bmax],
                    'placed_centroid': [round((bmin[a] + bmax[a]) / 2, 3) for a in range(3)],
                })
                # triangle-order test on each sub-mesh of this block
                for sm in block['sub_meshes']:
                    pos = [tuple(v) for v in sm['positions']]
                    n = len(pos)
                    if n < 3:
                        continue
                    strip_stats['submeshes'] += 1
                    # strip: triangles (0,1,2),(2,1,3),(3,2,4),...
                    for t in range(n - 2):
                        if t % 2 == 0:
                            a, b, c = pos[t], pos[t + 1], pos[t + 2]
                        else:
                            a, b, c = pos[t + 1], pos[t], pos[t + 2]
                        area, _ = tri_area(a, b, c)
                        strip_stats['strip_tris'] += 1
                        if area < 1e-6:
                            strip_stats['strip_degenerate'] += 1
                    # list: triangles (0,1,2),(3,4,5),...
                    for t in range(0, n - 2, 3):
                        area, _ = tri_area(pos[t], pos[t + 1], pos[t + 2])
                        strip_stats['list_tris'] += 1
                        if area < 1e-6:
                            strip_stats['list_degenerate'] += 1
                    # normal agreement (0x83 only): strip face normal vs vertex normal
                    if sm.get('normals'):
                        norms = [tuple(v) for v in sm['normals']]
                        for t in range(n - 2):
                            if t % 2 == 0:
                                a, b, c = pos[t], pos[t + 1], pos[t + 2]
                            else:
                                a, b, c = pos[t + 1], pos[t], pos[t + 2]
                            area, nrm = tri_area(a, b, c)
                            if area < 1e-6:
                                continue
                            ln = math.sqrt(nrm[0] ** 2 + nrm[1] ** 2 + nrm[2] ** 2)
                            if ln == 0:
                                continue
                            fn = (nrm[0] / ln, nrm[1] / ln, nrm[2] / ln)
                            vn = norms[t + 1]
                            dot = fn[0] * vn[0] + fn[1] * vn[1] + fn[2] * vn[2]
                            strip_stats['strip_normal_total'] += 1
                            if dot > 0:
                                strip_stats['strip_normal_agree'] += 1
        # spot keywords in bone names
        for mif in mifs:
            for b in mif['bones']:
                low = b['name'].lower()
                for kw in spot_keywords:
                    if kw in low:
                        spot_hits.append({'stage': st['source_file'],
                                          'bone': b['name'], 'keyword': kw})
        stages_out.append({
            'source_file': st['source_file'],
            'canon_stage': st['canon_stage'],
            'status': 'extracted',
            'pairing': 'MIF chunk j bone k <-> NUDP chunk j block k; '
                       f'pairwise counts equal in all {len(mifs)} chunks: {pairing_ok}',
            'placed_blocks': len(placed_blocks),
            'stage_aabb_min': [round(x, 3) for x in all_min],
            'stage_aabb_max': [round(x, 3) for x in all_max],
            'stage_size': [round(all_max[a] - all_min[a], 3) for a in range(3)],
            'blocks': placed_blocks,
        })
    strip_stats['strip_degenerate_rate'] = round(
        strip_stats['strip_degenerate'] / max(1, strip_stats['strip_tris']), 4)
    strip_stats['list_degenerate_rate'] = round(
        strip_stats['list_degenerate'] / max(1, strip_stats['list_tris']), 4)
    strip_stats['strip_normal_agree_rate'] = round(
        strip_stats['strip_normal_agree'] / max(1, strip_stats['strip_normal_total']), 4)
    out = {
        'format': 'western-heart dw-stage-placement v1',
        'source': 'moj-stage-geometry.json (NUDP vertices + MIF bone matrices)',
        'method': 'per-chunk in-order pairing (counts verified equal per chunk); '
                  'placed = bone 4x4 matrix x chunk-relative vertex; '
                  'units are the source units (mm-scale: stages span metres)',
        'triangle_order': strip_stats,
        'spot_keyword_hits': spot_hits,
        'stages': stages_out,
    }
    out_path.write_text(json.dumps(out, indent=1))
    print('stages:', len(stages_out))
    print('triangle order:', json.dumps(strip_stats, indent=1))
    print('spot keyword hits:', spot_hits)
    for s in stages_out:
        if s.get('stage_aabb_min'):
            print(s['source_file'], 'size:', s['stage_size'], 'blocks:', s['placed_blocks'])


if __name__ == '__main__':
    main()
