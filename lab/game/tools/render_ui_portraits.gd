## Renders menu/UI portraits from the owner's own GLBs (no AI faces).
## xvfb-run godot --rendering-driver opengl3 --path lab/game -s res://tools/render_ui_portraits.gd -- <outdir>
extends SceneTree

const JOBS := [
	# id, glb, framing (bust|full), silhouette
	["pantera", "res://assets/pantera_leoman.glb", "bust", false],
	["pantera", "res://assets/pantera_leoman.glb", "full", false],
	["unknown", "res://assets/pantera_leoman.glb", "bust", true],
	["unknown", "res://assets/pantera_leoman.glb", "full", true],
]

func _init() -> void:
	await process_frame
	var out: String = OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size() > 0 else "/tmp"
	for j in JOBS:
		await _render(j[0], j[1], j[2], j[3], out)
	quit()

func _render(id: String, glb: String, framing: String, sil: bool, out: String) -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(512, 512) if framing == "bust" else Vector2i(512, 1024)
	vp.transparent_bg = true; vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(vp)
	var model: Node3D = (load(glb) as PackedScene).instantiate(); vp.add_child(model)
	var ap: AnimationPlayer = model.find_children("*", "AnimationPlayer", true, false).front() if model.find_children("*", "AnimationPlayer", true, false).size() else null
	if ap and ap.has_animation("idle"): ap.play("idle"); ap.seek(0.0, true); ap.pause()
	model.rotation.y = deg_to_rad(20)
	var h := _measure(model)
	if sil:
		var m := StandardMaterial3D.new(); m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED; m.albedo_color = Color(0.05, 0.02, 0.08)
		for mi in model.find_children("*", "MeshInstance3D", true, false): (mi as MeshInstance3D).material_override = m
	var cam := Camera3D.new(); vp.add_child(cam)
	if framing == "bust":
		cam.fov = 28; cam.look_at_from_position(Vector3(0, h * 0.86, h * 1.05), Vector3(0, h * 0.84, 0))
	else:
		cam.fov = 30; cam.look_at_from_position(Vector3(0, h * 0.5, h * 2.1), Vector3(0, h * 0.5, 0))
	var key := DirectionalLight3D.new(); key.rotation_degrees = Vector3(-30, 35, 0); key.light_energy = 1.3; vp.add_child(key)
	var rim := DirectionalLight3D.new(); rim.rotation_degrees = Vector3(-10, 200, 0); rim.light_energy = 0.9; rim.light_color = Color(1, 0.6, 0.3); vp.add_child(rim)
	var env := WorldEnvironment.new(); var e := Environment.new(); e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.6, 0.55, 0.7); e.ambient_light_energy = 0.7
	env.environment = e; vp.add_child(env)
	for i in 4: await process_frame
	var img := vp.get_texture().get_image()
	var path := "%s/%s_%s.png" % [out, id, framing]
	img.save_png(path); print("PORTRAIT ", path, " h=", h)
	vp.queue_free()

func _measure(model: Node3D) -> float:
	var lo := INF; var hi := -INF
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		lo = minf(lo, b.position.y); hi = maxf(hi, b.end.y)
	return hi - lo
