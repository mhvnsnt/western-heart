import bpy, os
import numpy as np
from math import radians

REPO = '/home/hatch/workspace/_wh-work/cs-proof3'
BASE = os.path.join(REPO, 'roster/baek/attires/master-white/baek-master-white-rigged.glb')
PART = os.path.join(REPO, 'customization/parts/hair/cc0/Hair_Buzzed.gltf')

# source verts (standalone)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=PART)
dg = bpy.context.evaluated_depsgraph_get()
src = None
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and 'Buzzed' in o.name:
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        src = np.array([list(e.matrix_world @ v.co) for v in m.vertices])
        e.to_mesh_clear()

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=BASE)
base_arm = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=PART)
new_objs = [o for o in bpy.context.scene.objects if o not in before]
placement = {'px': 0, 'py': 0.03, 'pz': 2.12, 'rx': 0, 'ry': 180, 'rz': 0, 's': 1.25}
for o in new_objs:
    if o.parent in new_objs:
        continue
    print("root obj", o.name, "rotation_mode:", o.rotation_mode)
    o.parent = base_arm
    o.parent_type = 'BONE'
    o.parent_bone = 'Head'
    o.matrix_parent_inverse = base_arm.matrix_world.inverted()
    o.location = (placement['px'], placement['py'], placement['pz'])
    o.rotation_euler = (radians(placement['rx']), radians(placement['ry']), radians(placement['rz']))
    s = placement['s']
    o.scale = (s, s, s)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
dst = None
for o in new_objs:
    if o.type == 'MESH' and 'Buzzed' in o.name:
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        dst = np.array([list(e.matrix_world @ v.co) for v in m.vertices])
        e.to_mesh_clear()
print("DST center", dst.mean(axis=0).round(3), "shape", dst.shape)
# Kabsch dst vs src
cs, cd = src.mean(axis=0), dst.mean(axis=0)
X, Y = src - cs, dst - cd
H = X.T @ Y
U, S, Vt = np.linalg.svd(H)
d = np.sign(np.linalg.det(Vt.T @ U.T))
R = Vt.T @ np.diag([1, 1, d]) @ U.T
print("R vs source:\n", R.round(3))
print("resid max", np.abs((src @ R.T + (cd - R @ cs)) - dst).max().round(4))
print("RY180 PROBE DONE")
