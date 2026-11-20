import bpy, sys
import numpy as np

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
# 1) source cap: import CC0 buzzed alone, evaluated world verts
bpy.ops.import_scene.gltf(filepath='/home/hatch/workspace/_wh-work/cs-proof3/customization/parts/hair/cc0/Hair_Buzzed.gltf')
dg = bpy.context.evaluated_depsgraph_get()
src = None
for o in sc.objects:
    if o.type == 'MESH' and 'Buzzed' in o.name:
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        src = np.array([list(e.matrix_world @ v.co) for v in m.vertices])
        e.to_mesh_clear()
print("SRC verts", src.shape, "center", src.mean(axis=0).round(3))
# clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index('--') + 1])
dg = bpy.context.evaluated_depsgraph_get()
dst = None
for o in sc.objects:
    if o.type == 'MESH' and 'Buzzed' in o.name:
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        dst = np.array([list(e.matrix_world @ v.co) for v in m.vertices])
        e.to_mesh_clear()
print("DST verts", dst.shape, "center", dst.mean(axis=0).round(3))
assert src.shape == dst.shape, "vert count mismatch"
# Kabsch: find R, t minimizing |R src + t - dst| (same vertex order in both files)
cs, cd = src.mean(axis=0), dst.mean(axis=0)
X, Y = src - cs, dst - cd
H = X.T @ Y
U, S, Vt = np.linalg.svd(H)
d = np.sign(np.linalg.det(Vt.T @ U.T))
D = np.diag([1, 1, d])
R = Vt.T @ D @ U.T
t = cd - R @ cs
resid = np.abs((src @ R.T + t) - dst).max()
print("KABSCH max resid", resid)
print("R=\n", R.round(4))
# express R as euler XYZ degrees
import math
sy = -R[2, 0]
ry = math.asin(max(-1, min(1, sy)))
cy = math.cos(ry)
rx = math.atan2(R[2, 1] / cy, R[2, 2] / cy)
rz = math.atan2(R[1, 0] / cy, R[0, 0] / cy)
print("euler XYZ deg: rx=%.2f ry=%.2f rz=%.2f" % (math.degrees(rx), math.degrees(ry), math.degrees(rz)))
print("t=", t.round(4))
# also: where would the source center land under R with the CURRENT placement translation removed?
print("KABSCH DONE")
