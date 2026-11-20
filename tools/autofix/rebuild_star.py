import bpy, sys

# Rebuild Star on the CLEAN foundation (star-rigged-fixed: clean armature rest
# + clean mesh), importing the production vertex-group weights (incl. the
# Jiggle_* groups) from the corrupted-lineage file by vertex index.
# Usage: blender -b star-rigged-fixed.blend --python rebuild_star.py -- <weights_source.blend> <out.blend>
argv = sys.argv[sys.argv.index("--") + 1:]
WSRC, OUT = argv[0], argv[1]
mesh = next(o for o in bpy.data.objects if o.type == "MESH")
with bpy.data.libraries.load(WSRC) as (src, dst):
    dst.objects = src.objects
w_obj = next(o for o in dst.objects if o is not None and o.type == "MESH")
wm = w_obj.data
print("COUNTS:", len(mesh.data.vertices), len(wm.vertices))
assert len(wm.vertices) == len(mesh.data.vertices)
# clear existing groups, recreate from source with identical weights
for g in list(mesh.vertex_groups):
    mesh.vertex_groups.remove(g)
for g in w_obj.vertex_groups:
    mesh.vertex_groups.new(name=g.name)
for i, v in enumerate(wm.vertices):
    for gr in v.groups:
        mesh.vertex_groups[gr.group].add([i], gr.weight, "REPLACE")
print("GROUPS copied:", [g.name for g in mesh.vertex_groups])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
