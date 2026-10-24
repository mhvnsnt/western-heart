## Western Heart Lab — Tekken 3 1v1 slice on King's real T3 stage (stage l).
## P1: keyboard / gamepad / touch.  P2: CPU.  --autoplay: P1 is driven by a CPU
## that injects InputMap actions (the same path keyboard/touch use) for capture.
extends Node3D

const ROUND_FRAMES := 60 * 60
const WIN_ROUNDS := 2
const ACTIONS := {
	"p1_left": [KEY_A, KEY_LEFT], "p1_right": [KEY_D, KEY_RIGHT], "p1_up": [KEY_W, KEY_UP], "p1_down": [KEY_DOWN],
	"p1_light": [KEY_J], "p1_medium": [KEY_K], "p1_heavy": [KEY_L], "p1_grab": [KEY_U], "p1_block": [KEY_SPACE, KEY_S], "p1_mask": [KEY_M],
}
const PAD := {"p1_light": JOY_BUTTON_X, "p1_medium": JOY_BUTTON_Y, "p1_heavy": JOY_BUTTON_B, "p1_grab": JOY_BUTTON_A,
	"p1_block": JOY_BUTTON_RIGHT_SHOULDER, "p1_mask": JOY_BUTTON_BACK, "p1_left": JOY_BUTTON_DPAD_LEFT, "p1_right": JOY_BUTTON_DPAD_RIGHT,
	"p1_up": JOY_BUTTON_DPAD_UP, "p1_down": JOY_BUTTON_DPAD_DOWN}

var p1: Fighter
var p2: Fighter
var ai2: FighterAI
var ai1: FighterAI
var autoplay := false
var shots_dir := ""
var shot_done := {}
var frame := 0
var round_frame := 0
var round_no := 1
var wins := [0, 0]
var phase := "intro"
var phase_t := 0
var prev := {}
var hud: Hud
const PUSHBOX := 0.85
var cam: Camera3D
var shake := 0.0
var spark: MeshInstance3D
var spark_t := 0
var quit_after_match := false
var stats_hits := 0
var stats_blocks := 0

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	autoplay = "--autoplay" in args
	quit_after_match = "--quit-after-match" in args
	for a in args:
		if a.begins_with("--shots="): shots_dir = a.substr(8)
	_setup_input()
	_build_stage()
	var king: PackedScene = _real_glb("res://assets/t3_king")
	# P1 = PANTERA (owner's first original fighter; CANON: King's wrestler frame -> King T3 move table)
	var attire := "leoman"
	for a in args:
		if a.begins_with("--p1-attire="): attire = a.split("=")[1]
	p1 = Fighter.new(); add_child(p1)
	if attire == "leoman":
		p1.setup(_real_glb("res://assets/pantera_leoman"), "king", Color(1, 1, 1), true); p1.rig_id = "wh_canonical_autorig"
		p1.display_name = "PANTERA (Leo-Man)"
	else:
		p1.setup(king, "king", Color(0.7, 0.45, 1.0)); p1.display_name = "PANTERA (T3 body)"
	p2 = Fighter.new(); add_child(p2); p2.setup(king, "king", Color(1.0, 0.55, 0.5)); p2.display_name = "KING"
	var p1_char := "pantera"; var p2_char := "king"
	for a in args:
		if a.begins_with("--p1-char="): p1_char = a.split("=")[1]
		if a.begins_with("--p2-char="): p2_char = a.split("=")[1]
	for pc in [[p1, p1_char], [p2, p2_char]]:
		var f: Fighter = pc[0]; f.apply_height(pc[1])
		print("HEIGHT %s id=%s cm=%d measured_m=%.3f" % [f.display_name, pc[1], int(f.height_cm), HeightScale.measure(f.model)])
	if not ("--no-mask" in args):
		p2.wear_mask({"tint": Color(1, 1, 1)})   # Bannon mask on the T3 rig from round 1
	ai2 = FighterAI.new(7, 0.55)
	ai1 = FighterAI.new(3, 0.65)
	hud = Hud.new(); add_child(hud)
	hud.setup("--touch" in args or DisplayServer.is_touchscreen_available())
	for i in 2:   # in-game height readout (owner rule c)
		var hf: Fighter = [p1, p2][i]
		if hf.height_cm > 0.0: hud.names[i].text += "  %d cm" % int(hf.height_cm)
	cam = Camera3D.new(); add_child(cam); cam.fov = 40
	spark = MeshInstance3D.new(); var sm := SphereMesh.new(); sm.radius = 0.12; sm.height = 0.24; spark.mesh = sm
	var smat := StandardMaterial3D.new(); smat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED; smat.albedo_color = Color(1, 0.9, 0.4)
	spark.material_override = smat; spark.visible = false; add_child(spark)
	_start_round()

func _setup_input() -> void:
	for a in ACTIONS:
		if not InputMap.has_action(a): InputMap.add_action(a)
		for k in ACTIONS[a]:
			var e := InputEventKey.new(); e.physical_keycode = k; InputMap.action_add_event(a, e)
		var j := InputEventJoypadButton.new(); j.button_index = PAD[a]; InputMap.action_add_event(a, j)
	for pair in [["p1_left", -1.0], ["p1_right", 1.0]]:
		var m := InputEventJoypadMotion.new(); m.axis = JOY_AXIS_LEFT_X; m.axis_value = pair[1]; InputMap.action_add_event(pair[0], m)

func _build_stage() -> void:
	var env := WorldEnvironment.new(); var e := Environment.new()
	e.background_mode = Environment.BG_COLOR; e.background_color = Color(0.32, 0.36, 0.55)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.75, 0.75, 0.8); e.ambient_light_energy = 0.6
	env.environment = e; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-50, 30, 0); sun.light_energy = 1.1; add_child(sun)
	var pano: Node3D = (load("res://assets/t3_stage_l.glb") as PackedScene).instantiate(); add_child(pano)
	for mi in pano.find_children("*", "MeshInstance3D", true, false):
		var m := StandardMaterial3D.new(); m.vertex_color_use_as_albedo = true; m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED; m.cull_mode = BaseMaterial3D.CULL_DISABLED
		(mi as MeshInstance3D).material_override = m
	var img := Image.create(64, 64, false, Image.FORMAT_RGB8)
	for y in 64:
		for x in 64:
			img.set_pixel(x, y, Color(0.42, 0.36, 0.28) if ((x / 8) + (y / 8)) % 2 == 0 else Color(0.36, 0.30, 0.23))
	var tex := ImageTexture.create_from_image(img)
	var floor := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(60, 60); floor.mesh = pm
	var fm := StandardMaterial3D.new(); fm.albedo_texture = tex; fm.uv1_scale = Vector3(30, 30, 1); fm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	floor.material_override = fm; add_child(floor)

func _start_round() -> void:
	p1.reset(-1.1, 1.0); p2.reset(1.1, -1.0)
	round_frame = 0; phase = "intro"; phase_t = 0
	hud.message("ROUND %d" % round_no if round_no < 3 else "FINAL ROUND")
	# Round 2+: Pantera puts on the Bannon mask too (second rig: canonical auto-rig), editable tint
	if round_no >= 2 and p1.mask == null and not ("--no-mask" in OS.get_cmdline_user_args()):
		p1.wear_mask({"tint": Color(0.75, 0.6, 1.0), "roughness": 0.4, "metallic": 0.3})

func _p1_input() -> Dictionary:
	if autoplay:
		var d := ai1.think(p1, p2)
		for k in ["left", "right", "up", "down", "light", "medium", "heavy", "grab", "block"]:
			Input.action_release("p1_" + k)
		var fwd_act := "p1_right" if p1.facing > 0 else "p1_left"
		var back_act := "p1_left" if p1.facing > 0 else "p1_right"
		if d.get("fwd"): Input.action_press(fwd_act)
		if d.get("back"): Input.action_press(back_act)
		if d.get("block"): Input.action_press("p1_block")
		if d.get("up"): Input.action_press("p1_up")
		if d.get("down"): Input.action_press("p1_down")
		for s in ["light", "medium", "heavy", "grab"]:
			if d.get(s + "_pressed"): Input.action_press("p1_" + s)
	var right := Input.is_action_pressed("p1_right"); var left := Input.is_action_pressed("p1_left")
	var i := {"fwd": right if p1.facing > 0 else left, "back": left if p1.facing > 0 else right, "block": Input.is_action_pressed("p1_block"),
		"up": Input.is_action_pressed("p1_up"), "down": Input.is_action_pressed("p1_down")}
	for s in ["light", "medium", "heavy", "grab"]:
		var now := Input.is_action_pressed("p1_" + s)
		i[s + "_pressed"] = now and not prev.get(s, false)
		prev[s] = now
	return i

func _physics_process(_dt: float) -> void:
	frame += 1; phase_t += 1
	if shots_dir != "":   # --shots=<dir>: one proof frame per movement clip (frame 6 of the state)
		for f in [p1, p2]:
			var key: String = f.ss_kind if f.state == "sidestep" else (f.jump_kind if f.state == "jump" else f.state)
			if f.state in ["jump", "crouch", "crouch_hold", "sidestep"] and f.t_state == 6 and not shot_done.has(key):
				shot_done[key] = true
				get_viewport().get_texture().get_image().save_png(shots_dir.path_join("lab_%s.png" % key))
	var i1 := _p1_input()
	var i2 := ai2.think(p2, p1)
	if Input.is_action_just_pressed("p1_mask"):
		if p1.mask == null: p1.wear_mask()
		else: p1.mask.set_part("whole", not p1.mask.mesh_root.visible)
	if phase == "intro":
		i1 = {}; i2 = {}
		if phase_t > 75: phase = "fight"; hud.message("FIGHT!", 40)
	elif phase != "fight":
		i1 = {}; i2 = {}
	p1.tick(i1, frame); p2.tick(i2, frame)
	if phase == "fight":
		round_frame += 1
		_resolve(p1, p2); _resolve(p2, p1)
		_separate()
		if p1.hp == 0 or p2.hp == 0 or round_frame >= ROUND_FRAMES: _end_round()
	elif phase == "roundover" and phase_t > 150:
		if wins[0] >= WIN_ROUNDS or wins[1] >= WIN_ROUNDS:
			phase = "matchover"; phase_t = 0
			hud.message("%s WINS THE MATCH" % ("PLAYER 1" if wins[0] > wins[1] else "CPU"), 9999)
			print("MATCH RESULT wins=%s rounds=%d hits=%d blocks=%d frames=%d moves=%s" % [str(wins), round_no, stats_hits, stats_blocks, frame, str(Fighter.move_counts)])
		else:
			round_no += 1; _start_round()
	elif phase == "matchover" and phase_t > 180 and quit_after_match:
		get_tree().quit()
	_camera()
	if spark_t > 0:
		spark_t -= 1; spark.visible = spark_t > 0; spark.scale = Vector3.ONE * (1.0 + (6 - spark_t) * 0.25)
	hud.update(p1, p2, ROUND_FRAMES - round_frame, wins, round_no)

func _resolve(a: Fighter, d: Fighter) -> void:
	if not a.is_attacking() or a.connected or d.state == "ko": return
	if MoveTable.phase(a.move, a.mframe) != "active": return
	if absf(d.position.x - a.position.x) > a.move["range"]: return
	a.connected = true
	var m: Dictionary = a.move
	var contact := (a.position + d.position) * 0.5 + Vector3(0, 1.2 if m["slot"] != "heavy" else 1.0, 0)
	if d.is_blocking() and not m["unblockable"]:
		stats_blocks += 1; d.take_block(m, a.facing); a.hitstop = m["hit_freeze"] / 2; d.hitstop = a.hitstop
		hud.popup("BLOCK  -%d" % 0 if false else "BLOCKED", contact)
	else:
		stats_hits += 1; d.take_hit(m, a.facing); a.hitstop = m["hit_freeze"]; d.hitstop = m["hit_freeze"]
		shake = 0.06 if m["slot"] == "heavy" else 0.03
		spark.position = contact; spark_t = 6; spark.visible = true
		hud.popup("%s %d" % [m["slot"].to_upper(), m["damage"]], contact)
	hud.last_move("%s %s  T3 row %d  s%d a%d r%d  dmg %d  freeze %d" % [a.display_name, m["slot"], m["t3_row"], m["startup"], m["active"], m["recovery"], m["damage"], m["hit_freeze"]])

func _separate() -> void:
	# Pushbox: T3 bodies never interpenetrate; ~0.85 m keeps chests apart (was 0.6, models overlapped).
	var dx := p2.position.x - p1.position.x
	if absf(dx) < PUSHBOX:
		var push := (PUSHBOX - absf(dx)) * 0.5 * signf(dx if dx != 0 else 1.0)
		p1.position.x -= push; p2.position.x += push
	for f in [p1, p2]: f.position.x = clampf(f.position.x, -5.0, 5.0)
	var face := 1.0 if p2.position.x > p1.position.x else -1.0
	if p1.state != "attack": p1.set_facing(face)
	if p2.state != "attack": p2.set_facing(-face)

func _end_round() -> void:
	phase = "roundover"; phase_t = 0
	var w := 0 if p1.hp > p2.hp else (1 if p2.hp > p1.hp else -1)
	if w >= 0: wins[w] += 1
	var winner: Fighter = p1 if w == 0 else p2
	if w >= 0 and winner.state != "ko": winner._set_state("win")
	hud.message("K.O." if (p1.hp == 0 or p2.hp == 0) else "TIME", 150)

func _camera() -> void:
	if phase == "intro" and phase_t < 70:
		# round-intro beauty shot: 3/4 front of each fighter's head (shows the Bannon mask / attire)
		var f: Fighter = p1 if phase_t < 35 else p2
		var head := f.position + Vector3(0, 1.62, 0)
		cam.position = head + Vector3(f.facing * 1.1, 0.05, 0.75)
		cam.look_at(head); return
	var mid := (p1.position.x + p2.position.x) * 0.5
	var sep := absf(p1.position.x - p2.position.x)
	# Tekken-3-style framing: side-on, chest height, fighters fill ~55-60% of screen height (was far/high, ~35%).
	var target := Vector3(mid, 1.15, clampf(3.0 + sep * 0.6, 3.4, 6.5))
	cam.position = cam.position.lerp(target, 0.12) if (frame > 1 and not (phase == "intro" and phase_t < 72)) else target
	var off := Vector3(randf_range(-shake, shake), randf_range(-shake, shake), 0)
	shake *= 0.85
	cam.look_at(Vector3(mid, 0.95, 0) + off)

## Prefer the *_t3real.glb (same model + REAL decoded T3 clips). --anim=authored forces the old file.
func _real_glb(base: String) -> PackedScene:
	if not ("--anim=authored" in OS.get_cmdline_user_args()) and ResourceLoader.exists(base + "_t3real.glb"):
		return load(base + "_t3real.glb")
	return load(base + ".glb")
