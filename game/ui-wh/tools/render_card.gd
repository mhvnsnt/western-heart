## Western Heart card renderer: any GLB (runtime load) + optional kitbash recipe JSON.
## xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://../../game/ui-wh/tools/render_card.gd -- <glb> <out_prefix> [recipe.json|none] [yaw]
## Writes <out_prefix>_bust.png (512x512) and <out_prefix>_full.png (512x1024), transparent bg, same lights as render_ui_portraits.gd.
extends SceneTree

func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var recipe := {}
	if a.size() > 2 and a[2] != "none": recipe = JSON.parse_string(FileAccess.get_file_as_string(a[2]))
	var doc := GLTFDocument.new(); var st := GLTFState.new()
	if doc.append_from_file(a[0], st) != OK: printerr("LOAD FAIL ", a[0]); quit(1); return
	var vp := SubViewport.new(); vp.transparent_bg = true; vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS; root.add_child(vp)
	for framing in ["full", "bust"]:
		vp.size = Vector2i(512, 512) if framing == "bust" else Vector2i(512, 1024)
		for c in vp.get_children(): c.queue_free()
		await process_frame
		var model: Node3D = doc.generate_scene(st); vp.add_child(model)
		model.rotation.y = deg_to_rad(float(a[3]) if a.size() > 3 else 20.0)
		await process_frame
		var sks := model.find_children("*", "Skeleton3D", true, false)
		var sk: Skeleton3D = sks[0] if sks.size() else null
		_apply(model, sk, recipe)
		await process_frame
		var lo := Vector3(INF, INF, INF); var hi := -lo
		if sk:
			for bi in sk.get_bone_count():
				var gp: Vector3 = sk.global_transform * sk.get_bone_global_pose(bi).origin
				lo = lo.min(gp); hi = hi.max(gp)
			var hh := hi.y - lo.y; hi.y += hh * 0.08; lo.y -= hh * 0.02
		else:
			for mi in model.find_children("*", "MeshInstance3D", true, false):
				var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
				lo = lo.min(b.position); hi = hi.max(b.end)
		var h := hi.y - lo.y; var cy := lo.y; var cx := (lo.x + hi.x) * 0.5; var cz := (lo.z + hi.z) * 0.5
		var cam := Camera3D.new(); vp.add_child(cam)
		if framing == "bust":
			cam.fov = 28; cam.look_at_from_position(Vector3(cx, cy + h * 0.86, cz + h * 1.05), Vector3(cx, cy + h * 0.84, cz))
		else:
			cam.fov = 30; cam.look_at_from_position(Vector3(cx, cy + h * 0.5, cz + h * 2.1), Vector3(cx, cy + h * 0.5, cz))
		var key := DirectionalLight3D.new(); key.rotation_degrees = Vector3(-30, 35, 0); key.light_energy = 1.3; vp.add_child(key)
		var rim := DirectionalLight3D.new(); rim.rotation_degrees = Vector3(-10, 200, 0); rim.light_energy = 0.9; rim.light_color = Color(1, 0.6, 0.3); vp.add_child(rim)
		var env := WorldEnvironment.new(); var e := Environment.new(); e.background_mode = Environment.BG_CLEAR_COLOR
		e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.6, 0.55, 0.7); e.ambient_light_energy = 0.7
		env.environment = e; vp.add_child(env)
		for i in 6: await process_frame
		var path := "%s_%s.png" % [a[1], framing]; vp.get_texture().get_image().save_png(path); print("CARD ", path, " h=", h)
	quit()

func _apply(model: Node3D, sk: Skeleton3D, r: Dictionary) -> void:
	if r.is_empty(): return
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m3 := mi as MeshInstance3D
		if String(m3.name) in r.get("hide", []): m3.visible = false
		if r.get("tint", {}).has(String(m3.name)):
			var c: Array = r["tint"][String(m3.name)]
			var src = m3.get_active_material(0)
			if src is BaseMaterial3D:
				var m: BaseMaterial3D = src.duplicate(); m.albedo_color = Color(c[0], c[1], c[2])
				if c.size() > 3 and c[3] == 0: m.albedo_texture = null
				m3.set_surface_override_material(0, m)
	if sk == null: return
	for bn in r.get("pose", {}):
		var bi := sk.find_bone(bn); if bi < 0: continue
		var e: Array = r["pose"][bn]
		sk.set_bone_pose_rotation(bi, sk.get_bone_pose_rotation(bi) * Quaternion.from_euler(Vector3(deg_to_rad(e[0]), deg_to_rad(e[1]), deg_to_rad(e[2]))))
	for p in r.get("props", []):
		var att := Node3D.new(); model.add_child(att)
		att.global_position = sk.global_transform * sk.get_bone_global_pose(sk.find_bone(p["bone"])).origin
		var mat := StandardMaterial3D.new(); var c: Array = p["color"]; mat.albedo_color = Color(c[0], c[1], c[2]); mat.roughness = 0.6
		var o: Array = p["offset"]; var base := Vector3(o[0], o[1], o[2])
		var holder := Node3D.new(); att.add_child(holder); holder.top_level = false
		match p["kind"]:
			"gourd":
				for s in [[0.055, 0.0], [0.04, 0.085]]:
					var mi := MeshInstance3D.new(); var sm := SphereMesh.new(); sm.radius = s[0]; sm.height = s[0] * 2; mi.mesh = sm; mi.material_override = mat; mi.position = base + Vector3(0, s[1], 0); holder.add_child(mi)
			"beads":
				for i in 18:
					var t := TAU * i / 18.0
					var mi := MeshInstance3D.new(); var sm := SphereMesh.new(); sm.radius = 0.014; sm.height = 0.028; mi.mesh = sm; mi.material_override = mat
					mi.position = base + Vector3(cos(t) * 0.11, sin(t) * 0.02 - absf(sin(t * 0.5)) * 0.12, sin(t) * 0.09 + 0.02); holder.add_child(mi)
			"sash":
				var mi := MeshInstance3D.new(); var tm := TorusMesh.new(); tm.inner_radius = 0.15; tm.outer_radius = 0.19; mi.mesh = tm; mi.material_override = mat; mi.position = base; holder.add_child(mi)
