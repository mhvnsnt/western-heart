# Stage 02br — repair Rigify DEF hierarchy on the real-model rig.
# TWO repairs:
# 1. REPOSITION: Rigify's limbs.arm generator misplaced the DEF arm bones
#    (DEF-upper_arm.L tail at 0.1804 instead of metarig 0.2609, etc.).
#    Reset DEF arm head/tail from the fitted metarig (01_metarig_real.blend).
# 2. REPARENT: the generation cross-parented arm DEF chains through .001
#    duplicates; reparent into clean chains.
# THEN mute all constraints on arm DEF chains -> pure FK.
# (Leg DEFs are correctly subdivided by Rigify; spine DEFs are fine; only
#  the 4 arm chains need repositioning.)
import bpy
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
rig = bpy.data.objects["DXMMII_rig"]

# read the fitted metarig positions
bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/01_metarig_real.blend")
meta = bpy.data.objects["DXMMII_metarig_real"]
meta_pos = {}
for bn in ('upper_arm.L', 'forearm.L', 'hand.L',
           'upper_arm.R', 'forearm.R', 'hand.R',
           'upper_arm.x.L', 'forearm.x.L', 'hand.x.L',
           'upper_arm.x.R', 'forearm.x.R', 'hand.x.R'):
    b = meta.data.bones[bn]
    meta_pos['DEF-' + bn] = (Vector(b.head_local), Vector(b.tail_local))
    print("metarig", bn, [round(v, 4) for v in b.head_local], "->", [round(v, 4) for v in b.tail_local])

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
rig = bpy.data.objects["DXMMII_rig"]

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
eb = rig.data.edit_bones
# 1. reposition from metarig (head, tail) and set PROVEN rolls
# Rigify's limbs.arm generator misplaces DEF bones AND leaves wrong rolls.
# EMPIRICAL FINDING (2026-10-16): for mirrored arm bones (+X vs -X), the
# rolls must be IDENTICAL (not negated) for FK to mirror. Tested: R upper
# with roll 271deg (same as L's 271.9deg) raises with Z-, while negated
# roll (-271deg) inverts. Using proxy's proven rolls, same both sides.
PROVEN_ROLL = 4.7455  # upper arm (271.9deg)
PROVEN_ROLL_FORE = 4.9383  # forearm/hand
for bn, (h, t) in meta_pos.items():
    e = eb[bn]
    e.head, e.tail = h, t
    if 'forearm' in bn or 'hand' in bn:
        e.roll = PROVEN_ROLL_FORE
    else:
        e.roll = PROVEN_ROLL
    print(f"repositioned {bn} roll={e.roll:.4f}")
# 2. reparent into clean chains
for root, mid, tip in (("DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L"),
                       ("DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"),
                       ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L"),
                       ("DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R")):
    eb[mid].parent = eb[root]; eb[mid].use_connect = False
    eb[tip].parent = eb[mid]; eb[tip].use_connect = False
    print(f"repaired: {root} -> {mid} -> {tip}")
bpy.ops.object.mode_set(mode="OBJECT")

for bn in ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L",
           "DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R",
           "DEF-upper_arm.x.L", "DEF-forearm.x.L", "DEF-hand.x.L",
           "DEF-upper_arm.x.R", "DEF-forearm.x.R", "DEF-hand.x.R"):
    for c in rig.pose.bones[bn].constraints:
        c.mute = True
    rig.pose.bones[bn].rotation_mode = "XYZ"
print("arm DEF chains: pure FK")

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/dxmmii-limbs/blend/02_rig_real.blend")
print("STAGE02BR DONE")
