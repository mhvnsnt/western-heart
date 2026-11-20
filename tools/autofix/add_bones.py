import bpy, sys

# Add missing bones (the Jiggle_* set) to the target rig, copying rest
# head/tail/roll/parent from a donor rig loaded via library.
# Usage: blender -b <target.blend> --python add_bones.py -- <donor.blend> <donor_arm> <target_arm> <out>
argv = sys.argv[sys.argv.index("--") + 1:]
DONOR, DARM, TARM, OUT = argv
tgt = bpy.data.objects[TARM]
have = {b.name for b in tgt.data.bones}
with bpy.data.libraries.load(DONOR) as (src, dst):
    dst.objects = src.objects
don = next(o for o in dst.objects if o is not None and o.type == "ARMATURE"
           and any(b.name.startswith("Jiggle_") for b in o.data.bones))
missing = [b.name for b in don.data.bones if b.name not in have]
print("MISSING BONES:", missing)
specs = {}
from mathutils import Vector
for b in don.data.bones:
    if b.name in missing:
        M = b.matrix_local
        specs[b.name] = (tuple(b.head_local), tuple(b.tail_local),
                         Vector((M[0][2], M[1][2], M[2][2])),
                         b.parent.name if b.parent else None)
bpy.context.view_layer.objects.active = tgt
tgt.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
for name, (head, tail, zaxis, parent) in specs.items():
    eb = tgt.data.edit_bones.new(name)
    eb.head = head; eb.tail = tail
    eb.align_roll(zaxis)
    if parent and parent in tgt.data.edit_bones:
        eb.parent = tgt.data.edit_bones[parent]
bpy.ops.object.mode_set(mode="OBJECT")
print("BONES NOW:", len(tgt.data.bones))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
