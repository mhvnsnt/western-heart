"""Star: retarget CMU lambada BVH onto StarRig with the Rokoko Studio Live
Blender plugin (rsl.retarget_animation), scripted headless.
In: star-jiggle-baked-v3.blend (rig + jiggle bones + weights + textures).
The old hand-spring StarRigAction is removed in the working copy only.
Out: star_rokoko.blend with a fresh retargeted action on the 22 base bones.
"""
import bpy, sys, os, zipfile

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, BVH, OUT, ROKOKO_ZIP = argv[0], argv[1], argv[2], argv[3]

# --- install + enable the Rokoko addon ---
bpy.ops.preferences.addon_install(filepath=ROKOKO_ZIP, overwrite=True)
mods = [m for m in bpy.context.preferences.addons]
import addon_utils
for mod in addon_utils.modules():
    if "rokoko" in mod.__name__.lower():
        addon_utils.enable(mod.__name__, default_set=True)
        print("ROKOKO MODULE ENABLED:", mod.__name__)
        break
else:
    raise SystemExit("rokoko addon module not found after install")

bpy.ops.wm.open_mainfile(filepath=SRC)
arm = bpy.data.objects["StarRig"]
if arm.animation_data and arm.animation_data.action:
    old = arm.animation_data.action
    arm.animation_data.action = None
    bpy.data.actions.remove(old)
    print("removed old action in working copy")

before = set(bpy.data.objects)
bpy.ops.import_anim.bvh(filepath=BVH, axis_forward="-Z", axis_up="Y")
new_objs = [o for o in bpy.data.objects if o not in before]
src_arm = next(o for o in new_objs if o.type == "ARMATURE")
print("BVH ARMATURE:", src_arm.name, "bones:", len(src_arm.data.bones),
      "action:", src_arm.animation_data.action.name if src_arm.animation_data else None,
      "range:", src_arm.animation_data.action.frame_range[:] if src_arm.animation_data else None)
print("BVH BONES:", [b.name for b in src_arm.data.bones])

sc = bpy.context.scene
sc.rsl_retargeting_armature_source = src_arm
sc.rsl_retargeting_armature_target = arm

PAIRS = [("Hips", "Hips"), ("LowerBack", "Spine"), ("Spine", "Spine1"),
         ("Spine1", "Spine2"), ("Neck", "Neck"), ("Head", "Head"),
         ("LeftShoulder", "Shoulder.L"), ("LeftArm", "UpperArm.L"),
         ("LeftForeArm", "ForeArm.L"), ("LeftHand", "Hand.L"),
         ("RightShoulder", "Shoulder.R"), ("RightArm", "UpperArm.R"),
         ("RightForeArm", "ForeArm.R"), ("RightHand", "Hand.R"),
         ("LeftUpLeg", "UpLeg.L"), ("LeftLeg", "Leg.L"),
         ("LeftFoot", "Foot.L"), ("LeftToeBase", "ToeBase.L"),
         ("RightUpLeg", "UpLeg.R"), ("RightLeg", "Leg.R"),
         ("RightFoot", "Foot.R"), ("RightToeBase", "ToeBase.R")]
sc.rsl_retargeting_bone_list.clear()
sbones = {b.name for b in src_arm.data.bones}
for s, t in PAIRS:
    if s not in sbones:
        print("SOURCE BONE MISSING, skipped:", s); continue
    item = sc.rsl_retargeting_bone_list.add()
    item.bone_name_key = s.lower()
    item.bone_name_source = s
    item.bone_name_target = t
print("BONE LIST:", len(sc.rsl_retargeting_bone_list))

res = bpy.ops.rsl.retarget_animation()
print("RETARGET RESULT:", res)
act = arm.animation_data.action if arm.animation_data else None
print("TARGET ACTION:", act.name if act else None,
      "fcurves:", len(act.fcurves) if act else 0,
      "range:", act.frame_range[:] if act else None)
if act:
    act.use_fake_user = True
    from collections import Counter
    c = Counter()
    for fc in act.fcurves:
        if "pose.bones" in fc.data_path:
            c[fc.data_path.split('"')[1]] += 1
    print("ACTION BONES:", dict(c))
bpy.data.objects.remove(src_arm, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED:", OUT)
