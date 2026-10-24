# Stage 4b — REPAIR the Rigify DEF hierarchy for the arms.
# The generation cross-parented DEF chains through .001 duplicates
# (DEF-forearm.x.L parented to DEF-upper_arm.x.L.001, etc.), breaking FK.
# Repair: reparent each arm's DEF chain into a clean hierarchy and convert the
# extra-arm DEF chains to pure FK (mute all constraints). This is the standard
# game-engine skeleton the R&D specifies; Rigify FK/IK controls remain for UI.
import bpy

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/dxmmii_4arm_rig.blend")
rig = bpy.data.objects["DXMMII_rig"]
arm = rig.data

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.edit_bones

CHAINS = {
    # (root, mid, tip): reparent mid->root, tip->mid (keep offset)
    "extra_L": ("DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L"),
    "extra_R": ("DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"),
    "main_L": ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L"),
    "main_R": ("DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R"),
}

for key, (root, mid, tip) in CHAINS.items():
    for child, new_parent in ((mid, root), (tip, mid)):
        eb[child].parent = eb[new_parent]
        eb[child].use_connect = False
    print(f"repaired chain {key}: {root} -> {mid} -> {tip}")

bpy.ops.object.mode_set(mode="OBJECT")

# Mute ALL constraints on the repaired DEF chains -> pure FK.
# (The COPY_TRANSFORMS/STRETCH_TO mechanism was non-functional on these chains.)
for key, (root, mid, tip) in CHAINS.items():
    for bn in (root, mid, tip):
        for c in rig.pose.bones[bn].constraints:
            c.mute = True
        # direct FK: XYZ euler
        rig.pose.bones[bn].rotation_mode = "XYZ"
print("constraints muted on repaired DEF chains; rotation_mode=XYZ")

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/dxmmii_4arm_rig.blend")
print("STAGE4B DONE")
