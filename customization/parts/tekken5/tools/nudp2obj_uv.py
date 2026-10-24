"""NUDP -> OBJ with UVs, normals and per-submesh materials (textureIndex).

W7e extension of the W7b tolerant writer (~/workspace/_w7b-work/nudp2obj_tol.py):
geometry decode is ModelMagic's VIFerator exactly as W7b used it; this writer
additionally emits the vn/vt streams VIFerator already parses and a usemtl
line per submesh (material.textureIndex from the NUDP material record), so
TIM2 pictures can be bound in Blender. PS2 UVs are kept raw (GS REPEAT wrap
handles the out-of-0..1 ranges present in the data); V is flipped to the
OBJ/glTF convention.
"""
import sys
sys.path.insert(0, '/home/hatch/workspace/tk5-lanes/research/dl2/Tekken5_Tools/ModelMagic')
from model_nudp import NUDP
from vifMaker import VIFerator
from fileRW import FRead

def convert(src, dst):
    nud = NUDP(); nud.read(FRead(open(src, 'rb')))
    o = open(dst, 'w')
    o.write('# nudp2obj_uv: ModelMagic VIF decode, UV+normals+material textureIndex\n')
    cur = 1; ok = bad = 0; texidx = set(); verts = faces = 0
    for gi, g in enumerate(nud.MeshGroups):
        for si, sm in enumerate(g.subMeshs):
            texidx.add(sm.material.textureIndex)
            o.write('usemtl tex%03d\n' % sm.material.textureIndex)
            for vi, blob in enumerate(sm.vifDMA):
                try:
                    t = VIFerator(); t.read_vif(FRead(blob.data))
                    if not t.verts: continue
                    o.write('o G%d_S%d_V%d\n' % (gi, si, vi))
                    for v in t.verts:
                        o.write('v %f %f %f\n' % tuple(v.pos))
                        o.write('vn %f %f %f\n' % tuple(v.norm))
                        o.write('vt %f %f\n' % (v.uv[0], 1.0 - v.uv[1]))
                    strips = t.get_faces(); mx = 0
                    for st in strips:
                        o.write('f ' + ' '.join('%d/%d/%d' % (x + cur, x + cur, x + cur) for x in st) + '\n')
                        faces += 1
                    if strips: mx = max(max(st) for st in strips) + 1
                    cur += mx; verts += len(t.verts); ok += 1
                except Exception:
                    bad += 1
    o.close()
    return {'groups': len(nud.MeshGroups), 'blobs_ok': ok, 'blobs_bad': bad,
            'verts': verts, 'faces': faces, 'tex_indices': sorted(texidx)}

if __name__ == '__main__':
    import json
    print(json.dumps(convert(sys.argv[1], sys.argv[2])))
