#!/usr/bin/env python3
"""tools/auto_rig/repair_stevefox_shirt.py — per-file skin repair for
game/assets/models/steve-fox.glb (the PR #372 pattern: repair ONE model's
own file with pipeline tooling; no other character's file is touched).

DEFECT (audit 2026-10-20, docs/POSE-AUDIT-2026-10-20.md): the model's
Shirt mesh — 2,246 verts including both full sleeves — was weighted 100%
to Spine/Spine1 with ZERO arm-bound verts. In motion the sleeves held
the bind T-pose while the separate Arms/Gloves meshes followed the arm
bones, so every fighter using this model showed detached arms and
floating T-pose sleeves.

FIX: re-skin ONLY the Shirt mesh with Blender automatic (heat) weights
onto the model's OWN existing armature (stage: weights), then patch the
Shirt primitive's JOINTS_0/WEIGHTS_0 in a copy of the GLB (stage: patch).
Verts the heat solver cannot reach keep their original weights. No pose
values, no geometry, no other mesh, no other file is changed.

USAGE
  # stage 1 — run under Blender:
  xvfb-run -a env -u PYTHONPATH blender -b --python \
    tools/auto_rig/repair_stevefox_shirt.py -- weights \
    --in game/assets/models/steve-fox.glb --npz /tmp/shirt_weights.npz
  # stage 2 — plain python:
  python3 tools/auto_rig/repair_stevefox_shirt.py patch \
    --in game/assets/models/steve-fox.glb --npz /tmp/shirt_weights.npz \
    --out game/assets/models/steve-fox.glb
Verify afterwards: pose_gate.py + a front render at Idle frame ~40 —
sleeves must follow the arms (see docs/POSE-AUDIT-2026-10-20.md).
"""
import sys


def stage_weights(inp, outp):
    import bpy
    import numpy as np
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=inp)
    arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    shirt = next(o for o in bpy.context.scene.objects
                 if o.type == 'MESH' and 'Shirt' in o.name)
    bpy.ops.object.select_all(action='DESELECT')
    shirt.select_set(True)
    bpy.context.view_layer.objects.active = shirt
    shirt.vertex_groups.clear()
    for m in list(shirt.modifiers):
        if m.type == 'ARMATURE':
            shirt.modifiers.remove(m)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    groups = [g.name for g in shirt.vertex_groups]
    nv = len(shirt.data.vertices)
    J = np.zeros((nv, 4), dtype=np.int32)
    W = np.zeros((nv, 4), dtype=np.float32)
    for v in shirt.data.vertices:
        infl = sorted(((g.weight, groups[g.group]) for g in v.groups),
                      key=lambda t: -t[0])[:4]
        tot = sum(w for w, _ in infl) or 1.0
        for k, (w, name) in enumerate(infl):
            J[v.index, k] = groups.index(name)
            W[v.index, k] = w / tot
    np.savez(outp, joints=J, weights=W, group_names=np.array(groups))
    print('SHIRT-RESKIN-OK groups:', len(groups))


def stage_patch(inp, npz, outp):
    import json, struct
    import numpy as np
    raw = bytearray(open(inp, 'rb').read())
    jl = struct.unpack_from('<I', raw, 12)[0]
    j = json.loads(raw[20:20 + jl])
    boff = 20 + jl
    d = np.load(npz, allow_pickle=True)
    J, W = d['joints'], d['weights']
    group_names = [str(x) for x in d['group_names']]
    joint_names = [j['nodes'][i].get('name') for i in j['skins'][0]['joints']]
    name_to_joint = {n: i for i, n in enumerate(joint_names)}
    Jfile = np.vectorize(lambda g: name_to_joint[group_names[g]])(J).astype(np.int64)
    shirt_node = next(n for n in j['nodes']
                      if 'mesh' in n and 'Shirt' in n.get('name', ''))
    prim = j['meshes'][shirt_node['mesh']]['primitives'][0]
    nv = j['accessors'][prim['attributes']['POSITION']]['count']
    assert nv == len(J), f'vert count mismatch: file {nv} vs npz {len(J)}'

    def acc_span(ai):
        a = j['accessors'][ai]
        bv = j['bufferViews'][a['bufferView']]
        return a, bv.get('byteOffset', 0) + a.get('byteOffset', 0), bv.get('byteStride')

    ja, joff, jstride = acc_span(prim['attributes']['JOINTS_0'])
    wa, woff, wstride = acc_span(prim['attributes']['WEIGHTS_0'])
    jfmt = {5121: 'B', 5123: 'H', 5125: 'I'}[ja['componentType']]
    patched = kept = 0
    for v in range(nv):
        if W[v].sum() < 1e-6:
            kept += 1
            continue
        jo = joff + v * (jstride or struct.calcsize(jfmt) * 4)
        struct.pack_into('<4' + jfmt, raw, boff + 8 + jo, *Jfile[v])
        wo = woff + v * (wstride or 16)
        struct.pack_into('<4f', raw, boff + 8 + wo, *W[v])
        patched += 1
    open(outp, 'wb').write(bytes(raw))
    print(f'PATCH-OK patched={patched} kept-original={kept} verts={nv}')


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    stage = argv[0]
    opts = {}
    it = iter(argv[1:])
    for k in it:
        opts[k.lstrip('-')] = next(it)
    if stage == 'weights':
        stage_weights(opts['in'], opts['npz'])
    elif stage == 'patch':
        stage_patch(opts['in'], opts['npz'], opts['out'])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
