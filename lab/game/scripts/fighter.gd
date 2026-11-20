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
var char_id := ""
var height_cm := 0.0

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

## Height hook (owner rule c): scale the model to data/characters/heights.json.
func apply_height(id: String) -> void:
	char_id = id
	height_cm = HeightScale.apply(model, id)

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
		"idle", "walk_fwd", "walk_back", "crouch_hold":
			if state == "crouch_hold":
				if not i.get("down", false): _set_state("idle")
				_animate(frame); return
			var slot := ""
			for s in ["grab", "heavy", "medium", "light"]:
				if i.get(s + "_pressed", false): slot = s; break
			if slot != "":
				start_move(slot)
			elif i.get("up", false):
				jump_kind = "jump_fwd" if i.get("fwd", false) else ("jump_back" if i.get("back", false) else "jump_up")
				_set_state("jump")
			elif i.get("down", false):
				_set_state("crouch")
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
		"jump":
			if t_state <= JUMP_PRE and not i.get("up", false) and not i.get("down", false):
				ss_kind = "sidestep_a" if facing > 0 else "sidestep_b"; _set_state("sidestep")
			elif t_state <= JUMP_PRE and i.get("down", false):
				_set_state("crouch")
			elif t_state >= JUMP_FRAMES:
				_set_state("idle")
		"crouch":
			if t_state <= CROUCH_ENTRY and not i.get("down", false) and not i.get("up", false):
				ss_kind = "sidestep_b" if facing > 0 else "sidestep_a"; _set_state("sidestep")
			elif t_state >= CROUCH_ENTRY:
				_set_state("crouch_hold" if i.get("down", false) else "idle")
		"sidestep":
			if t_state >= SIDESTEP_FRAMES: _set_state("idle")
		"hitstun", "blockstun":
			stun -= 1
			position.x += kb_vel; kb_vel *= 0.85
			if stun <= 0: _set_state("idle")
		"ko":
			position.x += kb_vel; kb_vel *= 0.9
	_animate(frame)

static var move_counts := {}   # movement-state entries, printed with MATCH RESULT

func _set_state(s: String) -> void:
	if s != state:
		state = s; t_state = 0
		if s in ["jump", "crouch", "crouch_hold", "sidestep"]:
			var k: String = s if s != "jump" else jump_kind
			if s == "sidestep": k = ss_kind
			move_counts[k] = move_counts.get(k, 0) + 1

func take_hit(m: Dictionary, attacker_facing: float) -> void:
	hp = maxi(hp - int(m["damage"]), 0)
	kb_vel = m["knockback"] / 10.0 * attacker_facing
	if hp == 0:
		_set_state("ko"); return
	_set_state("hitstun"); stun = m["hitstun"]; stun_total = stun

func take_block(m: Dictionary, attacker_facing: float) -> void:
	kb_vel = m["knockback"] / 20.0 * attacker_facing
	_set_state("blockstun"); stun = m["blockstun"]; stun_total = stun

## REAL teardown clips (lab/tools/t3_motion_bake.py, decoded T3 motion banks) win over the
## authored clips.py ones whenever the model carries them. See docs/anim/PROCEDURAL_AUDIT.md.
const REAL := {"idle": "t3_stance_b", "win": "t3_win_lp", "heavy": "t3_heavy", "grab": "t3_grab", "light": "t3_light", "medium": "t3_medium",
	"walk_fwd": "t3_walk_fwd", "walk_back": "t3_walk_back", "hit": "t3_hit", "block": "t3_block", "ko": "t3_ko",
	"crouch": "t3_crouch", "crouch_hold": "t3_crouch_hold", "jump_up": "t3_jump_up", "jump_fwd": "t3_jump_fwd", "jump_back": "t3_jump_back",
	"sidestep_a": "t3_sidestep_a", "sidestep_b": "t3_sidestep_b"}

## Movement inputs and timing from the T3 USA branch lists (King divmot03 + divmot99 common rows,
## EXE table 0x80017C78, CALL/RETURN semantics of BranchFind 0x8002E078). Dump: lab/tools/t3_branch_dump.py.
##   standing slot 3: 8 -> 127 jump_up, 9 -> 129 jump_fwd, 7 -> 131 jump_back, 2 -> 59 crouch.
##   slot 127 (jump, air window 9-38, 48 frames): neutral in frames 1-8 -> sidestep, cond 0x3E (sideFlag clear) 283 / 0x3F (set) 285.
##   slot 59 (crouch entry, 8 frames): neutral in frames 1-8 -> sidestep, cond 0x3E 285 / 0x3F 283; held -> 40 crouch_hold.
## sideFlag (fighter +0xC6) is set on the right-hand side (it mirrors the stick), i.e. facing -X here.
const JUMP_PRE := 8            # branch window 1-8 before the air window 9-38
const JUMP_FRAMES := 48        # t3_jump_* clip length (decoded)
const CROUCH_ENTRY := 8        # slot 59 clip length and sidestep window
const SIDESTEP_FRAMES := 14    # t3_sidestep_* clip length (decoded)
var use_real := true
var jump_kind := "jump_up"
var ss_kind := "sidestep_a"

func _real(name: String) -> String:
	if use_real and REAL.has(name) and ap.has_animation(REAL[name]): return REAL[name]
	return ""

func _play(name: String, t: float) -> void:
	var r := _real(name)
	if r != "":
		var L := ap.get_animation(r).length
		if name in ["idle", "walk_fwd", "walk_back"]: t = fmod(float(t_state) / 60.0, L)
		elif name in ["hit", "block"]: t = minf(float(stun_total - stun) / 60.0, L) if state in ["hitstun", "blockstun"] else minf(0.2, L)
		elif name in ["crouch", "crouch_hold", "jump_up", "jump_fwd", "jump_back", "sidestep_a", "sidestep_b"]:
			t = fmod(float(t_state) / 60.0, L) if name == "crouch_hold" else minf(float(t_state) / 60.0, L)
		elif name == "ko": t = minf(float(t_state) / 60.0, L)
		elif name == "win": t = minf(float(t_state) / 60.0, L)
		else: t = minf(float(mframe) / 60.0, L)  # attacks: real T3 frames, 60 fps
		name = r
	if name != cur_anim:
		ap.play(name); cur_anim = name
	ap.seek(t, true)

func _animate(frame: int) -> void:
	match state:
		"idle", "walk_fwd", "walk_back", "win":
			var n: String = state if state != "walk_back" else "walk_back"
			var L: float = LOOP[n]
			_play(n, fmod(t_state / 60.0, L))
		"crouch", "crouch_hold":
			_play(state, 0.0)
		"jump":
			_play(jump_kind, 0.0)
		"sidestep":
			_play(ss_kind, 0.0)
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
