#!/usr/bin/env python3
"""Apply MPFB2 morph targets to ANY suite character GLB as shape keys (headless).

Usage:
  blender -b --python apply_mpfb_morphs.py -- \
      --mpfb-src /path/to/mpfb2 --glb in.glb \
      --morphs '{"bulk":0.6,"height":0.4}' --out out.glb

Target paths resolve against <mpfb-src>/src/mpfb/data/targets/<group>/<name>.target.gz
(same tree pulled into mhvnsnt/cape-jones production/tools/mpfb2, PR #128).

Mapping: MPFB deltas live in the MPFB base-mesh vertex space (19,158 verts).
They transfer onto the target mesh via KD-tree nearest-neighbor — the same
transfer mpfb_wire_cj.py used to build the CJ shape keys (see
cape-jones production/tools/mpfb2/WIRING.md). Each suite morph becomes a shape
key named MPFB_<id>.
"""
import bpy, sys, os, json, gzip, argparse, math
from mathutils import Vector
from mathutils.kdtree import KDTree

SUITE_MAP = json.load(open(os.path.join(os.path.dirname(__file__), 'MANIFEST.json')))

def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument('--mpfb-src', required=True)
    ap.add_argument('--glb', required=True)
    ap.add_argument('--morphs', required=True)
    ap.add_argument('--out', required=True)
    return ap.parse_args(argv)

def load_target(mpfb_src, rel):
    path = os.path.join(mpfb_src, 'src', 'mpfb', 'data', 'targets', rel + '.target.gz')
    if not os.path.exists(path):
        path = os.path.join(mpfb_src, 'src', 'mpfb', 'data', 'targets', rel + '.target')
    opener = gzip.open if path.endswith('.gz') else open
    deltas = {}
    with opener(path, 'rt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            i = int(parts[0])
            deltas[i] = (float(parts[1]), float(parts[2]), float(parts[3]))
    return deltas

def load_base_obj(mpfb_src):
    path = os.path.join(mpfb_src, 'src', 'mpfb', 'data', '3dobjs', 'base.obj')
    verts = []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                _, x, y, z = line.split()
                verts.append((float(x), float(y), float(z)))
    return verts

def main():
    args = parse_args()
    morphs = json.loads(args.morphs)
    macro = {m['id']: m for m in SUITE_MAP['macro_morphs']}

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=args.glb)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise SystemExit('no meshes in ' + args.glb)

    base_verts = load_base_obj(args.mpfb_src)
    print('MPFB base verts:', len(base_verts))

    for obj in meshes:
        mesh = obj.data
        n = len(mesh.vertices)
        tree = KDTree(n)
        for i, v in enumerate(mesh.vertices):
            tree.insert(Vector(v.co), i)
        tree.balance()
        # map every target-mesh vert -> nearest MPFB base vert
        nearest = [tree.find(Vector(v.co))[1] for v in mesh.vertices]

        acc = {}   # morph_id -> list of (vert_i, dx,dy,dz)
        for mid, val in morphs.items():
            if mid not in macro or not val:
                continue
            m = macro[mid]
            targets = m['mpfb'] if isinstance(m['mpfb'], list) else [m['mpfb']]
            per_vert = {}
            for rel in targets:
                rel = rel.replace('{min,max}', 'max' if val >= 0 else 'min')
                deltas = load_target(args.mpfb_src, rel)
                for bidx, d in deltas.items():
                    if bidx < len(base_verts):
                        per_vert[bidx] = per_vert.get(bidx, (0, 0, 0))
                        s = abs(val) / len(targets)
                        per_vert[bidx] = (per_vert[bidx][0] + d[0] * s,
                                          per_vert[bidx][1] + d[1] * s,
                                          per_vert[bidx][2] + d[2] * s)
            vlist = [(i, per_vert[b]) for i, b in enumerate(nearest) if b in per_vert]
            acc[mid] = vlist

        if not obj.data.shape_keys:
            obj.shape_key_add(name='Basis', from_mix=False)
        for mid, vlist in acc.items():
            sk = obj.shape_key_add(name='MPFB_' + mid, from_mix=False)
            for i, d in vlist:
                sk.data[i].co = mesh.vertices[i].co + Vector(d)
            sk.value = 1.0
        print('shape keys on', obj.name, [k.name for k in obj.data.shape_keys.key_blocks])

    bpy.ops.export_scene.gltf(filepath=args.out, export_format='GLB')
    print('WROTE', args.out)

main()
