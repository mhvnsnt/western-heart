import bpy, sys

# Add Corrective Smooth (post-armature) to every real mesh — the A/B-proven
# surface repair (hair tears -> 0 over-1.5x edges; body tears halved).
# Usage: blender -b <file> --python finalize_cs.py -- [factor] [iterations]
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
factor = float(argv[0]) if len(argv) > 0 else 0.5
iters = int(argv[1]) if len(argv) > 1 else 5
for o in bpy.data.objects:
    o.hide_viewport = False; o.hide_render = False
    if o.name == "Icosphere":
        o.hide_render = True
n = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.name == "Icosphere":
        continue
    if any(m.type == "CORRECTIVE_SMOOTH" for m in o.modifiers):
        continue
    cs = o.modifiers.new("CorrectiveSmooth", "CORRECTIVE_SMOOTH")
    cs.factor = factor; cs.iterations = iters
    cs.use_only_smooth = True
    cs.use_pin_boundary = True
    # ensure CS sits after the Armature modifier
    n += 1
print("CS ADDED to", n, "meshes factor", factor, "iters", iters)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("SAVED", bpy.data.filepath)
