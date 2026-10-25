import bpy, sys, json
from mathutils import Vector

# Acceptance measurements on a FINAL file:
#  - edge-length distribution stats per mesh at sampled frames (vs bind)
#  - jiggle visibility: evaluated vert displacement with the 'Jiggle' NLA track
#    live vs muted, over soft-region verts (breast/butt groups), per frame.
# Usage: blender -b <file> --python measure_final.py -- <out.json> <region groups csv>
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, GROUPS = argv[0], argv[1].split(",")
FRAMES = [12, 18, 24, 30, 36, 42, 48]
scene = bpy.context.scene
for o in bpy.data.objects:
    o.hide_viewport = False; o.hide_render = False
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
meshes = [o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > 100
          and o.name != "Icosphere"]

def edge_stats(ob, dg):
    rest = ob.data
    rl = sorted((rest.vertices[e.vertices[0]].co - rest.vertices[e.vertices[1]].co).length for e in rest.edges)
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    pl = sorted((me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length for e in me.edges)
    ev.to_mesh_clear()
    n = min(len(rl), len(pl))
    over = sum(1 for i in range(n) if pl[i] > 1.5 * rl[i])
    return {"over": over, "total": n, "max_ratio": round(pl[-1] / max(rl[-1], 1e-9), 2)}

def region_verts(ob):
    idx = set()
    gis = {ob.vertex_groups[g].index for g in GROUPS if g in ob.vertex_groups}
    for v in ob.data.vertices:
        for gr in v.groups:
            if gr.group in gis and gr.weight > 0.3:
                idx.add(v.index)
    return sorted(idx)

def eval_region(ob, dg, idx):
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    pts = {i: tuple(me.vertices[i].co) for i in idx}
    ev.to_mesh_clear()
    return pts

res = {"edge": {}, "jiggle_delta": {}}
track = None
if arm.animation_data:
    for t in arm.animation_data.nla_tracks:
        if t.name == "Jiggle":
            track = t
for ob in meshes:
    idx = region_verts(ob)
    res["edge"][ob.name] = {}
    deltas = []
    for f in FRAMES:
        scene.frame_set(f); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        res["edge"][ob.name][str(f)] = edge_stats(ob, dg)
        if track is not None and idx:
            on = eval_region(ob, dg, idx)
            track.mute = True
            bpy.context.view_layer.update()
            dg2 = bpy.context.evaluated_depsgraph_get()
            off = eval_region(ob, dg2, idx)
            track.mute = False
            bpy.context.view_layer.update()
            ds = [(Vector(on[i]) - Vector(off[i])).length for i in idx]
            deltas.append({"frame": f, "mean": round(sum(ds) / len(ds), 4),
                           "max": round(max(ds), 4), "verts": len(idx)})
    if deltas:
        res["jiggle_delta"][ob.name] = deltas
json.dump(res, open(OUT, "w"), indent=1)
print("FINAL_MEASURE_WROTE", OUT)
