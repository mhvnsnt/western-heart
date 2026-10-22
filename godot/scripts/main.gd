extends Node3D

## Western Heart — Godot vertical slice (engine lock: Godot 4.7.2, Mobile).
##
## Proves the production pipeline end to end:
##   roster GLB -> Godot native glTF import -> deterministic sim (sim/)
##   -> presentation (FighterView) -> decoded T3 bank clip on a real fighter
##   -> touch controls -> Android APK export.
##
## P1 = PANTERA (game/assets/models/pantera.glb, HOUSE-49, T7-King family)
## P2 = STAR    (game/assets/models/star-house49.glb, MINI re-templated onto
##               the same HOUSE-49 profile — driven by Pantera's clips via
##               name-track sharing, the runtime BoneMap equivalent)
##
## Proof mode: run with `-- --proof --proof-out=<abs dir>` and the slice plays
## a scripted input timeline (idle -> walk -> bank-clip attack), captures two
## frames, prints PROOF_* lines, and quits.

const PANTERA_GLB := "res://assets/models/pantera.glb"
const STAR_GLB := "res://assets/models/star-house49.glb"
const BANK_LIGHT := "res://assets/anim/t3_light.json"
const BANK_STANCE := "res://assets/anim/t3_stance.json"
const BANK_WALK := "res://assets/anim/t3_walk_fwd.json"
const MODEL_YAW := PI / 2.0  # shipped GLBs face +Z; +90 deg about Y faces +X

var sim := FightSim.new()
var p1: FighterView
var p2: FighterView
var _held := 0                # touch/keyboard input bits for P1
var _status: Label
var _prev_p1_state := -1

var _proof := false
var _proof_dir := ""
var _proof_shots := {}

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	_proof = "--proof" in args
	for a in args:
		if a.begins_with("--proof-out="):
			_proof_dir = a.substr(12)
	_build_stage()
	_build_fighters()
	_build_hud()
	print("SLICE READY | P1 clips: ", p1.anim_player.get_animation_list())
	print("SLICE READY | P2 clips: ", p2.anim_player.get_animation_list())
	print("SLICE READY | P1 bones: ", p1.skeleton.get_bone_count(), " P2 bones: ", p2.skeleton.get_bone_count())
	print("SLICE READY | retarget conv: P1=", BankClipLoader.detect_conv(p1.skeleton), " P2=", BankClipLoader.detect_conv(p2.skeleton), " (0=none 1=rotX90 2=rotX-90 3=zmirror)")


func _build_stage() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.10, 0.12, 0.20)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.75, 0.75, 0.82)
	e.ambient_light_energy = 0.55
	env.environment = e
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 30, 0)
	sun.light_energy = 1.15
	add_child(sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(26, 16)
	ground.mesh = plane
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.16, 0.17, 0.22)
	gm.roughness = 0.95
	ground.material_override = gm
	add_child(ground)
	var cam := Camera3D.new()
	cam.position = Vector3(0, 1.55, 4.8)
	cam.fov = 40.0
	add_child(cam)
	cam.look_at(Vector3(0, 0.95, 0), Vector3.UP)
	cam.current = true


func _build_fighters() -> void:
	p1 = FighterView.new()
	add_child(p1)
	p1.setup(load(PANTERA_GLB) as PackedScene, MODEL_YAW)
	p2 = FighterView.new()
	add_child(p2)
	p2.setup(load(STAR_GLB) as PackedScene, MODEL_YAW)
	# The bank proof: REAL decoded Tekken 3 clips (bank king_on_pantera_leoman)
	# retargeted onto each rig by BankClipLoader's world-delta solver.
	# Pantera's attack = t3_light (King move row 35 — a crouch-leap strike).
	var bank_anim := BankClipLoader.load_clip(BANK_LIGHT, p1.skeleton, p1.track_prefix, BankClipLoader.detect_conv(p1.skeleton), true)
	if bank_anim:
		p1.add_clip("light", bank_anim, "bank")
	# Star ships with no clips of her own in this slice; she runs on the same
	# bank's stance + walk, retargeted onto her re-templated rig by the same
	# solver (her own clip set is a later pipeline step — see README).
	var star_conv := BankClipLoader.detect_conv(p2.skeleton)
	var stance := BankClipLoader.load_clip(BANK_STANCE, p2.skeleton, p2.track_prefix, star_conv, false)
	if stance:
		stance.loop_mode = Animation.LOOP_LINEAR
		p2.add_clip("Idle", stance, "bank")
	var walk := BankClipLoader.load_clip(BANK_WALK, p2.skeleton, p2.track_prefix, star_conv, false)
	if walk:
		walk.loop_mode = Animation.LOOP_LINEAR
		p2.add_clip("Walk", walk, "bank")
	_apply_views()


func _build_hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	_status = Label.new()
	_status.set_anchors_preset(Control.PRESET_CENTER_TOP)
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_status.add_theme_font_size_override("font_size", 22)
	root.add_child(_status)
	var mk_button := func(text: String, preset: Control.LayoutPreset, offset: Vector2) -> Button:
		var b := Button.new()
		b.text = text
		b.custom_minimum_size = Vector2(118, 80)
		b.add_theme_font_size_override("font_size", 30)
		b.set_anchors_preset(preset)
		b.position = offset
		root.add_child(b)
		return b
	var left: Button = mk_button.call("◀", Control.PRESET_BOTTOM_LEFT, Vector2(28, -108))
	var right: Button = mk_button.call("▶", Control.PRESET_BOTTOM_LEFT, Vector2(168, -108))
	var atk: Button = mk_button.call("ATK", Control.PRESET_BOTTOM_RIGHT, Vector2(-146, -108))
	left.button_down.connect(func() -> void: _held |= FightSim.IN_LEFT)
	left.button_up.connect(func() -> void: _held &= ~FightSim.IN_LEFT)
	right.button_down.connect(func() -> void: _held |= FightSim.IN_RIGHT)
	right.button_up.connect(func() -> void: _held &= ~FightSim.IN_RIGHT)
	atk.button_down.connect(func() -> void: _held |= FightSim.IN_ATTACK)
	atk.button_up.connect(func() -> void: _held &= ~FightSim.IN_ATTACK)


func _physics_process(_delta: float) -> void:
	var input := _held
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT):
		input |= FightSim.IN_LEFT
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT):
		input |= FightSim.IN_RIGHT
	if Input.is_physical_key_pressed(KEY_J):
		input |= FightSim.IN_ATTACK
	if _proof:
		input = _proof_input(sim.frame)
	sim.step(input, 0)
	_apply_views()
	if _proof:
		_proof_timeline()


func _apply_views() -> void:
	p1.apply_sim(sim.p1_x, sim.p1_facing)
	p2.apply_sim(sim.p2_x, sim.p2_facing)
	var p1_clip := _clip_for(sim.p1_state, true)
	var restart := sim.p1_state == FightSim.ST_ATTACK and _prev_p1_state != FightSim.ST_ATTACK
	p1.play_clip(p1_clip, restart)
	_prev_p1_state = sim.p1_state
	p2.play_clip(_clip_for(sim.p2_state, false))
	if _status != null:
		_status.text = "WESTERN HEART — GODOT SLICE   frame %d   PANTERA: %s   STAR: %s" % [
			sim.frame, sim.state_name(sim.p1_state), sim.state_name(sim.p2_state)]


func _clip_for(state: int, is_p1: bool) -> String:
	if is_p1:
		match state:
			FightSim.ST_WALK_FWD, FightSim.ST_WALK_BACK:
				return "Walk"
			FightSim.ST_ATTACK:
				return "bank/light"
		return "Idle"
	match state:
		FightSim.ST_WALK_FWD, FightSim.ST_WALK_BACK:
			return "bank/Walk"
	return "bank/Idle"


# Scripted proof timeline (deterministic — same frames every run).
func _proof_input(frame: int) -> int:
	if frame >= 40 and frame < 100:
		return FightSim.IN_RIGHT
	if frame == 120:
		return FightSim.IN_ATTACK
	return 0


func _proof_timeline() -> void:
	if sim.frame % 20 == 0:
		print("PROOF_TICK frame=", sim.frame, " p1=", sim.state_name(sim.p1_state), " x=", snappedf(sim.p1_x, 0.01))
	if sim.frame == 84 and not _proof_shots.has("walk"):
		_proof_shots["walk"] = true
		_capture("slice_walk.png")
	if sim.frame == 138 and not _proof_shots.has("attack"):
		_proof_shots["attack"] = true
		_capture("slice_attack.png")
	if sim.frame >= 160:
		print("PROOF_DONE frame=", sim.frame)
		get_tree().quit()


func _capture(file_name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := _proof_dir.path_join(file_name) if not _proof_dir.is_empty() else "user://" + file_name
	var err := img.save_png(path)
	print("PROOF_SHOT ", path, " err=", err, " size=", img.get_size())
