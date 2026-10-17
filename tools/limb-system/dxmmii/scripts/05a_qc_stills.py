# Stage 5a — QC stills at the key state-transition frames.
import bpy

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/dxmmii_4arm_rig.blend")
S = bpy.context.scene
QC = {
    1: "f001_attached_idle",
    60: "f060_retract_mid",
    84: "f084_hidden",
    114: "f114_grow_mid",
    150: "f150_flourish",
    168: "f168_detach_switch",
    200: "f200_gyro_float",
    240: "f240_reattach_switch",
    280: "f280_finale",
}
for f, name in QC.items():
    S.frame_set(f)
    S.render.filepath = f"/home/hatch/workspace/dxmmii-limbs/renders/stills/qc_{name}.png"
    bpy.ops.render.render(write_still=True)
    print("QC still:", name)
print("STAGE5A DONE")
