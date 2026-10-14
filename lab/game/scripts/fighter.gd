## One Lab fighter: T3-imported model + MoveTable-driven state machine.
class_name Fighter
extends Node3D

const MAX_HP := 170            # Tekken 3 life bar
const WALK_F := 1.7 / 60.0     # m per frame
const WALK_B := 1.3 / 60.0
const LOOP := {"idle": 1.0, "walk_fwd": 0.8, "walk_back": 0.8, "win": 1.0}

var table: MoveTable
var hp := MAX_HP
var state := "idle"
var move := {}
var mframe := 0
var stun := 0
var stun_total := 1
var hitstop := 0
var connected := false
var facing := 1.0              # +1 faces +X
var kb_vel := 0.0
var inp := {}
var t_state := 0
var ap: AnimationPlayer
var cur_anim := ""
var model: Node3D
var display_name := "KING"

var skeleton: Skeleton3D
var rig_id := "wh_canonical_t3"
var mask: Attire

func wear_mask(params := {}) -> void:
	if mask == null:
		mask = Attire.attach(skeleton, "res://attire/bannon_mask/bannon_mask.manifest.json", rig_id, params)
	else:
		mask.set_params(params); mask.set_part("whole", true)

func setup(model_scene: PackedScene, fighter_id: String, tint: Color, keep_textures := false) -> void:
	table = MoveTable.load_fighter(fighter_id)
	model = model_scene.instantiate()
	add_child(model)
	ap = model.find_children("*", "AnimationPlayer", true, false)[0]
	ap.speed_scale = 0.0
	skeleton = model.find_children("*", "Skeleton3D", true, false)[0]
	if keep_textures:
		for mi in model.find_children("*", "MeshInstance3D", true, false):
			for s in (mi as MeshInstance3D).mesh.get_surface_count():
				var m: StandardMaterial3D = (mi as MeshInstance3D).mesh.surface_get_material(s).duplicate()
				m.albedo_color = tint; m.cull_mode = BaseMaterial3D.CULL_DISABLED
				(mi as MeshInstance3D).set_surface_override_material(s, m)
		return
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var mat := StandardMaterial3D.new()
		mat.vertex_color_use_as_albedo = true
		mat.albedo_color = tint
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		mat.roughness = 0.8
		for s in (mi as MeshInstance3D).mesh.get_surface_count():
			(mi as MeshInstance3D).set_surface_override_material(s, mat)

func reset(x: float, face: float) -> void:
	hp = MAX_HP; state = "idle"; mframe = 0; stun = 0; hitstop = 0; kb_vel = 0.0
	position = Vector3(x, 0, 0); set_facing(face)

func set_facing(face: float) -> void:
	facing = face
	model.rotation.y = PI / 2.0 if face > 0 else -PI / 2.0

func is_attacking() -> bool:
	return state == "attack"

func is_blocking() -> bool:
	return (state in ["idle", "walk_back", "blockstun"]) and (inp.get("back", false) or inp.get("block", false))

func start_move(slot: String) -> void:
	move = table.get_move(slot); state = "attack"; mframe = 0; connected = false

func tick(i: Dictionary, frame: int) -> void:
	inp = i
	if hitstop > 0:
		hitstop -= 1
		_animate(frame); return
	t_state += 1
	match state:
		"idle", "walk_fwd", "walk_back":
			var slot := ""
			for s in ["grab", "heavy", "medium", "light"]:
				if i.get(s + "_pressed", false): slot = s; break
			if slot != "":
				start_move(slot)
			elif i.get("fwd", false) and not i.get("block", false):
				_set_state("walk_fwd"); position.x += WALK_F * facing
			elif i.get("back", false) and not i.get("block", false):
				_set_state("walk_back"); position.x -= WALK_B * facing
			else:
				_set_state("idle")
		"attack":
			mframe += 1
			if MoveTable.phase(move, mframe) == "startup" and move["slot"] in ["medium", "grab"]:
				position.x += 0.6 / move["startup"] * facing * 0.5
			if MoveTable.phase(move, mframe) == "done":
				_set_state("idle")
		"hitstun", "blockstun":
			stun -= 1
			position.x += kb_vel; kb_vel *= 0.85
			if stun <= 0: _set_state("idle")
		"ko":
			position.x += kb_vel; kb_vel *= 0.9
	_animate(frame)

func _set_state(s: String) -> void:
	if s != state: state = s; t_state = 0

func take_hit(m: Dictionary, attacker_facing: float) -> void:
	hp = maxi(hp - int(m["damage"]), 0)
	kb_vel = m["knockback"] / 10.0 * attacker_facing
	if hp == 0:
		_set_state("ko"); return
	_set_state("hitstun"); stun = m["hitstun"]; stun_total = stun

func take_block(m: Dictionary, attacker_facing: float) -> void:
	kb_vel = m["knockback"] / 20.0 * attacker_facing
	_set_state("blockstun"); stun = m["blockstun"]; stun_total = stun

func _play(name: String, t: float) -> void:
	if name != cur_anim:
		ap.play(name); cur_anim = name
	ap.seek(t, true)

func _animate(frame: int) -> void:
	match state:
		"idle", "walk_fwd", "walk_back", "win":
			var n: String = state if state != "walk_back" else "walk_back"
			var L: float = LOOP[n]
			_play(n, fmod(t_state / 60.0, L))
		"attack":
			_play(move["anim"], MoveTable.anim_time(move, mframe))
		"hitstun":
			_play("hit", minf(0.4 * (1.0 - float(stun) / stun_total) + 0.08, 0.4))
		"blockstun":
			_play("block", 0.2)
		"ko":
			_play("ko", minf(t_state / 60.0, 1.2))
	if state in ["idle", "walk_back"] and inp.get("block", false):
		_play("block", 0.2)
