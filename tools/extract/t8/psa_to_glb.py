"""psa_to_glb.py — Blender: import a T8 .psk skeleton + .psa anims, export one GLB per clip,
ready for tools/anim-retarget/retarget_rot.py --bonemap tools/extract/t8/t8_to_wh.json.
Needs the io_scene_psk_psa add-on (github.com/DarklightGames/io_scene_psk_psa, GPL-3) installed in Blender.
Usage: blender -b --python psa_to_glb.py -- --psk alisa.psk --psa alisa_anims.psa --out outdir/"""
import bpy, sys, argparse, os
a = sys.argv[sys.argv.index("--")+1:]
p = argparse.ArgumentParser(); p.add_argument("--psk"); p.add_argument("--psa"); p.add_argument("--out"); args = p.parse_args(a)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="io_scene_psk_psa")
bpy.ops.import_scene.psk(filepath=args.psk)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
bpy.context.view_layer.objects.active = arm
bpy.ops.import_scene.psa(filepath=args.psa)
os.makedirs(args.out, exist_ok=True)
for act in list(bpy.data.actions):
    arm.animation_data_create(); arm.animation_data.action = act
    s, e = act.frame_range; bpy.context.scene.frame_start, bpy.context.scene.frame_end = int(s), int(e)
    for o in bpy.data.objects: o.select_set(o == arm)
    bpy.ops.export_scene.gltf(filepath=os.path.join(args.out, f"{act.name}.glb"), export_format="GLB", use_selection=True,
        export_animations=True, export_frame_range=True, export_anim_single_armature=True)
    print("WROTE", act.name)
