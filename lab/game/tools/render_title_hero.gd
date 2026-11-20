## Title-screen hero: Pantera in his P1 attire (pantera_leoman.glb, the Lab's default P1 attire)
## posed from the GLB's own clips. Low camera, 3/4 angle, warm key + purple rim.
## xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_title_hero.gd -- <outdir> [anim] [time]
extends SceneTree

func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var out: String = a[0] if a.size() > 0 else "/tmp"
	var poses := [["win", 0.6], ["win", 1.0], ["heavy", 0.4], ["grab", 0.35]]
	if a.size() > 2: poses = [[a[1], float(a[2])]]
	for p in poses: await _render(out, p[0], p[1])
	quit()

func _render(out: String, anim: String, t: float) -> void:
	var vp := SubViewport.new(); vp.size = Vector2i(900, 1200); vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS; root.add_child(vp)
	var m: Node3D = (load("res://assets/pantera_leoman.glb") as PackedScene).instantiate(); vp.add_child(m)
	var ap: AnimationPlayer = m.find_children("*", "AnimationPlayer", true, false)[0]
	ap.play(anim); ap.seek(t, true); ap.pause()
	m.rotation.y = deg_to_rad(28)
	var cam := Camera3D.new(); vp.add_child(cam); cam.fov = 34
	cam.look_at_from_position(Vector3(0.1, 0.55, 3.6), Vector3(0, 0.98, 0))
	var key := DirectionalLight3D.new(); key.rotation_degrees = Vector3(-25, 30, 0); key.light_energy = 1.4; key.light_color = Color(1, 0.88, 0.7); vp.add_child(key)
	var rim := DirectionalLight3D.new(); rim.rotation_degrees = Vector3(-5, 205, 0); rim.light_energy = 2.2; rim.light_color = Color(0.62, 0.3, 1.0); vp.add_child(rim)
	var env := WorldEnvironment.new(); var e := Environment.new(); e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.55, 0.5, 0.65); e.ambient_light_energy = 0.6
	env.environment = e; vp.add_child(env)
	for i in 4: await process_frame
	var path := "%s/pantera_hero_%s_%.2f.png" % [out, anim, t]
	vp.get_texture().get_image().save_png(path); print("HERO ", path)
	vp.queue_free()
