#!/usr/bin/env python3
"""Build GLB + preview renders from extracted NDPP bounding boxes.
Run under Blender: xvfb-run -a env -u PYTHONPATH <blender> -b -P build_glb.py
"""
import bpy
import json
import os
import math

BOXES_JSON = '/home/hatch/workspace/game-reverse-engineering/tekken6/work/extract/boxes.json'
OUT_DIR = '/home/hatch/workspace/game-reverse-engineering/tekken6/work/extract/output'
GLB_PATH = os.path.join(OUT_DIR, 'ndpp_bounding_volumes.glb')
PREVIEW_PATH = os.path.join(OUT_DIR, 'preview_grid.png')
PREVIEW2_PATH = os.path.join(OUT_DIR, 'preview_closeup.png')

os.makedirs(OUT_DIR, exist_ok=True)

with open(BOXES_JSON) as f:
    sections = json.load(f)

# --- clear scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)

def box_tris(verts):
    """Map 8 verts to corners, return triangle list. verts: list of 8 [x,y,z]."""
    mins = [min(v[i] for v in verts) for i in range(3)]
    maxs = [max(v[i] for v in verts) for i in range(3)]
    corner_of = []
    for v in verts:
        ci = 0
        for ax in range(3):
            dmin = abs(v[ax] - mins[ax])
            dmax = abs(v[ax] - maxs[ax])
            if dmax < dmin:
                ci |= (1 << ax)
        corner_of.append(ci)
    c2v = {}
    for vi, ci in enumerate(corner_of):
        if ci not in c2v:
            c2v[ci] = vi
    quads = [
        (0, 1, 3, 2), (4, 6, 7, 5),
        (0, 4, 5, 1), (2, 3, 7, 6),
        (0, 2, 6, 4), (1, 5, 7, 3),
    ]
    tris = []
    for q in quads:
        try:
            a, b, c, d = (c2v[x] for x in q)
        except KeyError:
            continue
        tris.append((a, b, c))
        tris.append((a, c, d))
    return tris

# --- build one object per section; arrange sections on a grid for the preview ---
# Grid layout: 19 cols x 19 rows (357 sections)
COLS = 19
CELL = 4.0

all_verts = []   # for merged export we keep per-section objects instead
sec_objects = []

for s in sections:
    idx = s['section']
    boxes = s['boxes']
    if not boxes:
        continue
    gx = (idx % COLS) * CELL
    gz = (idx // COLS) * CELL
    verts = []
    faces = []
    voff = 0
    for b in boxes:
        bv = b['verts']
        # translate box verts into grid cell
        tv = [(v[0] + gx, v[1], v[2] + gz) for v in bv]
        tris = box_tris(bv)
        verts.extend(tv)
        for t in tris:
            faces.append((t[0] + voff, t[1] + voff, t[2] + voff))
        voff += 8
    if not faces:
        continue
    mesh = bpy.data.meshes.new(f'section_{idx:03d}')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f'section_{idx:03d}', mesh)
    bpy.context.collection.objects.link(obj)
    sec_objects.append(obj)

print(f"created {len(sec_objects)} section objects")

# --- export GLB ---
bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format='GLB',
    export_apply=True,
)
print(f"exported {GLB_PATH} ({os.path.getsize(GLB_PATH)} bytes)")

# --- setup render: camera + lights looking at the grid ---
# Grid spans 19*4=76 in x and z. Center at (38, 0, 38).
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.world.use_nodes = True

# camera
cam_data = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
# position: above and to the side, looking at grid center
cam.location = (38 + 55, 55, 38 + 55)
# point at center
import mathutils
direction = mathutils.Vector((38, 0, 38)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

# sun light
light_data = bpy.data.lights.new(name='sun', type='SUN')
light_data.energy = 3.0
light = bpy.data.objects.new('sun', light_data)
bpy.context.collection.objects.link(light)
light.rotation_euler = (math.radians(45), 0, math.radians(30))

# material: wireframe-ish orange
mat = bpy.data.materials.new('boxmat')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (1.0, 0.45, 0.1, 1.0)
for o in sec_objects:
    o.data.materials.append(mat)

scene.render.filepath = PREVIEW_PATH
bpy.ops.render.render(write_still=True)
print(f"rendered {PREVIEW_PATH}")

# --- closeup: frame first 3x3 sections ---
cam.location = (4 + 8, 10, 4 + 8)
direction = mathutils.Vector((4, 0, 4)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = PREVIEW2_PATH
bpy.ops.render.render(write_still=True)
print(f"rendered {PREVIEW2_PATH}")
