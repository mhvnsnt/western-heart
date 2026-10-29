import bpy, sys
import numpy as np

REPO = '/home/hatch/workspace/_wh-work/cs-proof3'
PARTS = {
    'Beard': ('customization/parts/hair/cc0/Hair_Beard.gltf', 'Beard'),
    'Eyebrows': ('customization/parts/hair/cc0/Eyebrows_Regular.gltf', 'Eyebrows'),
}

def verts_of(filepath, namekey):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=filepath)
    dg = bpy.context.evaluated_depsgraph_get()
    out = None
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and namekey in o.name:
            e = o.evaluated_get(dg)
            m = e.to_mesh()
            out = np.array([list(e.matrix_world @ v.co) for v in m.vertices])
            e.to_mesh_clear()
    return out

for tag, (rel, key) in PARTS.items():
    src = verts_of(f'{REPO}/{rel}', key)
    dst = verts_of(sys.argv[sys.argv.index('--') + 1], key)
    print(tag, 'src center', src.mean(axis=0).round(3), 'dst center', dst.mean(axis=0).round(3), 'shapes', src.shape, dst.shape)
    if src.shape == dst.shape:
        cs, cd = src.mean(axis=0), dst.mean(axis=0)
        X, Y = src - cs, dst - cd
        U, S, Vt = np.linalg.svd(X.T @ Y)
        d = np.sign(np.linalg.det(Vt.T @ U.T))
        R = Vt.T @ np.diag([1, 1, d]) @ U.T
        print(tag, 'R=\n', R.round(3), 'resid', np.abs((src @ R.T + (cd - R @ cs)) - dst).max().round(4))
print("KABSCH2 DONE")
