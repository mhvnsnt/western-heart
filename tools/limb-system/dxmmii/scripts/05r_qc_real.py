# Stage 05r — render the 5 states on the REAL DXMMII + QC stills.
# Spec (matches viz/dxmmii_*.png): front ortho, white void, full arm reach.
# CYCLES 8spp, emission-ified materials. Fixed framing from the union bbox of
# the 5 state frames (consistent across states for comparison).
import bpy, json
from mathutils import Vector

bpy.ops.wm.open_mainfile(
    filepath="/home/hatch/workspace/dxmmii-limbs/blend/dxmmii_4arm_rig_REAL.blend")
S = bpy.context.scene
S.render.engine = 'CYCLES'
S.cycles.samples = 8
S.render.resolution_x = 1024
S.render.resolution_y = 1024
world = bpy.data.worlds.new('W')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
S.world = world
for m in bpy.data.materials:
    if m.use_nodes:
        bsdf = m.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            alb = None
            for l in m.node_tree.links:
                if l.to_node == bsdf and l.to_socket.name == 'Base Color':
                    alb = l.from_node
            em = m.node_tree.nodes.new('ShaderNodeEmission')
            if alb:
                m.node_tree.links.new(alb.outputs[0], em.inputs[0])
            m.node_tree.links.new(
                em.outputs[0], m.node_tree.nodes.get('Material Output').inputs[0])

STATES = {
    "state_attached": 1,
    "state_retracting": 60,
    "state_hidden": 84,
    "state_growing": 114,
    "state_detached": 200,
}
QC = {
    "qc_f150_flourish": 150,
    "qc_f168_detach": 168,
    "qc_f240_reattach": 240,
    "qc_f280_finale": 280,
}

def frame_bbox(frames):
    mn = Vector((9, 9, 9)); mx = Vector((-9, -9, -9))
    for f in frames:
        S.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        for o in S.objects:
            # only the DXMMII model parts (never Rigify WGT widgets)
            if o.type != 'MESH' or not o.name.startswith('DXR_'):
                continue
            oe = o.evaluated_get(dg)
            if oe.hide_render:
                continue
            M = oe.matrix_world
            for v in oe.data.vertices:
                w = M @ v.co
                mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx

mn, mx = frame_bbox(list(STATES.values()))
ctr = (mn + mx) / 2
span = max((mx - mn).x, (mx - mn).y, (mx - mn).z)
print("union bbox ctr", tuple(round(v, 3) for v in ctr), "span", round(span, 3), flush=True)

bpy.ops.object.camera_add(location=(ctr.x, ctr.y - 2.5, ctr.z))
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = span * 1.22
d = (ctr - cam.location).normalized()
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
S.camera = cam

import os
os.makedirs("/home/hatch/workspace/dxmmii-limbs/renders/real", exist_ok=True)
for name, f in {**STATES, **QC}.items():
    S.frame_set(f)
    S.render.filepath = f"/home/hatch/workspace/dxmmii-limbs/renders/real/{name}.png"
    bpy.ops.render.render(write_still=True)
    print("rendered", name, f"f{f}", flush=True)
print("STAGE05R DONE")
