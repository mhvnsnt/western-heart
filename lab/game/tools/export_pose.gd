## Export a reusable pose (per-bone local transforms) from a GLB clip at a time, as JSON.
## xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/export_pose.gd -- <out.json> <anim> <time> [glb]
extends SceneTree

func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var out: String = a[0]; var anim: String = a[1]; var t := float(a[2])
	var glb: String = a[3] if a.size() > 3 else "res://assets/pantera_leoman.glb"
	var m: Node3D = (load(glb) as PackedScene).instantiate(); root.add_child(m)
	var ap: AnimationPlayer = m.find_children("*", "AnimationPlayer", true, false)[0]
	ap.play(anim); ap.seek(t, true); ap.pause()
	var sk: Skeleton3D = m.find_children("*", "Skeleton3D", true, false)[0]
	var bones := {}
	for i in sk.get_bone_count():
		var p := sk.get_bone_pose_position(i); var q := sk.get_bone_pose_rotation(i); var s := sk.get_bone_pose_scale(i)
		bones[sk.get_bone_name(i)] = {"pos": [p.x, p.y, p.z], "rot_xyzw": [q.x, q.y, q.z, q.w], "scale": [s.x, s.y, s.z]}
	var d := {"format": "wh-pose/1", "source_glb": glb, "clip": anim, "time_s": t, "clips_available": Array(ap.get_animation_list()),
		"skeleton": sk.name, "bone_count": sk.get_bone_count(), "space": "bone-local (Skeleton3D pose)", "bones": bones}
	var f := FileAccess.open(out, FileAccess.WRITE); f.store_string(JSON.stringify(d, "  ")); f.close()
	print("POSE ", out, " bones=", sk.get_bone_count(), " clips=", ap.get_animation_list())
	quit()
