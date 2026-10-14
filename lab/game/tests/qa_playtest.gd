## QA playtest harness (Grok Bot QA lane). Loads the real Lab scene (scenes/main.tscn),
## replaces the CPU P2 with a scripted dummy, and drives P1 through the SAME InputMap
## actions the keyboard/gamepad/touch use (Input.action_press / action_release).
## Every physics frame (60 Hz) it logs both fighters' state, then prints frame-data
## measurements per scenario as "QA|" lines and writes res://../../build/qa/qa_log.csv.
##
## Run headless (numbers only):
##   godot --headless --path lab/game -s res://tests/qa_playtest.gd
## Run with rendering + PNG proof frames (needs xvfb):
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path lab/game --rendering-driver opengl3 -s res://tests/qa_playtest.gd -- --capture
## Full method: docs/PLAYTEST-METHOD.md
extends SceneTree

class Dummy extends FighterAI:
	var mode := "stand"   # stand | block
	func _init() -> void: super(1, 0.0)
	func think(_me: Fighter, _opp: Fighter) -> Dictionary:
		return {"fwd": false, "back": mode == "block", "block": mode == "block"}

const ACTS := ["p1_left", "p1_right", "p1_light", "p1_medium", "p1_heavy", "p1_grab", "p1_block"]

var main: Node
var dummy := Dummy.new()
var capture := false
var out_dir := ""
var scenarios: Array = []
var si := -1
var f := 0                 # frame inside current scenario
var sc: Dictionary
var log_rows: PackedStringArray = ["scenario,f,p1_state,p1_mframe,p1_phase,p1_x,p1_hitstop,p2_state,p2_stun,p2_hp,p2_x,cam_x,cam_z"]
var ev: Dictionary         # per-scenario measurement scratch
var started := false
var wait := 2

func _initialize() -> void:
	capture = "--capture" in OS.get_cmdline_user_args()
	out_dir = ProjectSettings.globalize_path("res://").path_join("../../build/qa")
	DirAccess.make_dir_recursive_absolute(out_dir)
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	# script: list of {name, dist, p2, len, inputs: {frame: [actions held that frame]}}
	scenarios = [
		_s("walk_fwd_60f", 3.0, "stand", 70, _hold("p1_right", 1, 60)),
		_s("walk_back_60f", 3.0, "stand", 70, _hold("p1_left", 1, 60)),
		_s("dash_fwd_doubletap", 3.0, "stand", 50, _merge([_tap("p1_right", 1), _tap("p1_right", 5)])),
		_s("jab_on_hit", 0.9, "stand", 90, _tap("p1_light", 1)),
		_s("jab_on_block", 0.9, "block", 90, _tap("p1_light", 1)),
		_s("medium_on_hit", 0.9, "stand", 110, _tap("p1_medium", 1)),
		_s("heavy_launcher_standin_on_hit", 0.9, "stand", 130, _tap("p1_heavy", 1)),
		_s("heavy_on_block", 0.9, "block", 130, _tap("p1_heavy", 1)),
		_s("throw_vs_blocking", 0.8, "block", 130, _tap("p1_grab", 1)),
		_s("ten_hit_string_mash_J_every4f", 0.9, "stand", 140, _mash("p1_light", 1, 10, 4)),
		_s("jab_buffered_during_recovery", 0.9, "stand", 120, _merge([_tap("p1_light", 1), _tap("p1_light", 30)])),
		_s("ko_heavy_on_10hp", 0.9, "stand", 200, _tap("p1_heavy", 1), 10),
	]

func _s(n, dist, p2m, length, inputs, p2hp := 170) -> Dictionary:
	return {"name": n, "dist": dist, "p2": p2m, "len": length, "in": inputs, "p2hp": p2hp}
func _hold(a, from, to) -> Dictionary:
	var d := {}
	for i in range(from, to + 1): d[i] = [a]
	return d
func _tap(a, at) -> Dictionary: return {at: [a], at + 1: [a]}   # 2-frame press like a human tap
func _mash(a, at, n, every) -> Dictionary:
	var d := {}
	for k in n: d[at + k * every] = [a]
	return d
func _merge(ds: Array) -> Dictionary:
	var d := {}
	for x in ds:
		for k in x: d[k] = d.get(k, []) + x[k]
	return d

func _next() -> bool:
	si += 1
	if si >= scenarios.size(): return false
	sc = scenarios[si]; f = 0
	ev = {"press": [], "active": [], "hit": [], "block": [], "p1_free": -1, "p2_free": -1, "x0": 0.0, "states": []}
	main.ai2 = dummy; dummy.mode = sc["p2"]
	main.phase = "fight"; main.phase_t = 999; main.round_frame = 0; main.wins = [0, 0]
	main.p1.reset(-sc["dist"] / 2.0, 1.0); main.p2.reset(sc["dist"] / 2.0, -1.0)
	main.p2.hp = sc["p2hp"]; main.prev = {}
	ev["x0"] = main.p1.position.x
	for a in ACTS: Input.action_release(a)
	return true

func _physics_process(_dt: float) -> bool:
	if wait > 0:
		wait -= 1; return false
	if not started:
		started = true
		main.autoplay = false
		if not _next(): return true
	f += 1
	# inject this frame's inputs BEFORE main._physics_process reads them
	for a in ACTS: Input.action_release(a)
	for a in sc["in"].get(f, []): Input.action_press(a)
	if sc["in"].has(f) and not sc["in"].has(f - 1): ev["press"].append(f)
	call_deferred("_observe", f)
	if f >= sc["len"]:
		call_deferred("_finish")
	return false

func _observe(fr: int) -> void:
	var p1: Fighter = main.p1; var p2: Fighter = main.p2
	var ph: String = MoveTable.phase(p1.move, p1.mframe) if p1.state == "attack" else "-"
	log_rows.append("%s,%d,%s,%d,%s,%.3f,%d,%s,%d,%d,%.3f,%.2f,%.2f" % [sc["name"], fr, p1.state, p1.mframe, ph, p1.position.x, p1.hitstop, p2.state, p2.stun, p2.hp, p2.position.x, main.cam.position.x, main.cam.position.z])
	var last: Array = ev["states"]
	var key := "%s/%s" % [p1.state, p2.state]
	if last.is_empty() or last[-1][1] != key: last.append([fr, key])
	if ph == "active" and (ev["active"].is_empty() or ev["active"][-1] < fr - 1 - p1.hitstop - 1): ev["active"].append(fr)
	if p2.state == "hitstun" and p2.stun == p2.stun_total and p2.hitstop > 0 and not ev.get("hs_" + str(fr - 1), false):
		pass
	if capture and (fr % 6 == 0 or ph == "active"):
		var img := root.get_viewport().get_texture().get_image()
		if img: img.save_png(out_dir.path_join("%02d_%s_f%03d.png" % [si, sc["name"], fr]))

func _finish() -> void:
	if f < sc["len"]: return
	var st: Array = ev["states"]
	var p1: Fighter = main.p1; var p2: Fighter = main.p2
	print("QA|%s|presses=%s|first_active_frames=%s|transitions=%s|p1_dx=%.3f|p2_hp=%d|p2_x=%.3f" % [sc["name"], str(ev["press"]), str(ev["active"]), str(st), p1.position.x - ev["x0"], p2.hp, p2.position.x])
	if not _next():
		var fa := FileAccess.open(out_dir.path_join("qa_log.csv"), FileAccess.WRITE)
		fa.store_string("\n".join(log_rows)); fa.close()
		print("QA|DONE|log=%s" % out_dir.path_join("qa_log.csv"))
		quit()
