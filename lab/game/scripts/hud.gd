## HUD (life bars, timer, round pips, messages, frame-data readout) + touch controls.
class_name Hud
extends CanvasLayer

var bars := []
var timer_l: Label
var msg: Label
var msg_t := 0
var info: Label
var pops := []
var pips: Label
var names := []

func _label(size: int, pos: Vector2, align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new(); l.add_theme_font_size_override("font_size", size); l.position = pos
	l.horizontal_alignment = align; l.add_theme_color_override("font_outline_color", Color.BLACK); l.add_theme_constant_override("outline_size", 6)
	add_child(l); return l

func setup(touch: bool) -> void:
	for side in 2:
		var bg := ColorRect.new(); bg.color = Color(0.1, 0.1, 0.1, 0.8); bg.size = Vector2(520, 26); bg.position = Vector2(40 if side == 0 else 720, 30); add_child(bg)
		var fg := ColorRect.new(); fg.color = Color(1.0, 0.8, 0.15); fg.size = Vector2(516, 22); fg.position = bg.position + Vector2(2, 2); add_child(fg)
		bars.append(fg)
		var n := _label(20, bg.position + Vector2(0, 28), HORIZONTAL_ALIGNMENT_LEFT if side == 0 else HORIZONTAL_ALIGNMENT_RIGHT); n.size = Vector2(520, 24)
		n.text = "P1  PANTERA" if side == 0 else "KING  CPU"; names.append(n)
	timer_l = _label(40, Vector2(590, 18)); timer_l.size = Vector2(100, 50)
	pips = _label(18, Vector2(560, 70)); pips.size = Vector2(160, 24)
	msg = _label(72, Vector2(0, 250)); msg.size = Vector2(1280, 100)
	info = _label(16, Vector2(20, 690), HORIZONTAL_ALIGNMENT_LEFT); info.size = Vector2(1240, 22)
	var tag := _label(14, Vector2(20, 668), HORIZONTAL_ALIGNMENT_LEFT); tag.size = Vector2(900, 20)
	tag.text = "WESTERN HEART LAB  -  P1 Pantera Leo-Man (owner original, auto-rigged) vs Tekken 3 King (KMD import) + Bannon mask  -  King's T3 stage (l)  -  T3 move table"
	if touch: _touch()

func _touch() -> void:
	var specs := [["<", "p1_left", Vector2(40, 560)], [">", "p1_right", Vector2(170, 560)], ["BLK", "p1_block", Vector2(105, 450)],
		["LP", "p1_light", Vector2(1000, 560)], ["MP", "p1_medium", Vector2(1120, 560)], ["K", "p1_heavy", Vector2(1060, 450)], ["GRB", "p1_grab", Vector2(1180, 450)]]
	for s in specs:
		var b := Button.new(); b.text = s[0]; b.position = s[2]; b.size = Vector2(100, 90); b.modulate = Color(1, 1, 1, 0.75)
		b.add_theme_font_size_override("font_size", 28); b.focus_mode = Control.FOCUS_NONE
		var act: String = s[1]
		b.button_down.connect(func(): Input.action_press(act))
		b.button_up.connect(func(): Input.action_release(act))
		add_child(b)

func message(t: String, frames := 75) -> void:
	msg.text = t; msg_t = frames

func last_move(t: String) -> void:
	info.text = t

func popup(t: String, world: Vector3) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null: return
	var l := _label(28, cam.unproject_position(world) - Vector2(80, 60)); l.size = Vector2(160, 30); l.text = t
	pops.append([l, 40])

func update(p1: Fighter, p2: Fighter, frames_left: int, wins: Array, _round: int) -> void:
	bars[0].size.x = 516.0 * p1.hp / Fighter.MAX_HP
	bars[1].size.x = 516.0 * p2.hp / Fighter.MAX_HP
	bars[1].position.x = 722 + 516.0 * (1.0 - float(p2.hp) / Fighter.MAX_HP)
	timer_l.text = str(int(ceil(frames_left / 60.0)))
	pips.text = "WINS %d - %d" % [wins[0], wins[1]]
	if msg_t > 0:
		msg_t -= 1
		if msg_t == 0: msg.text = ""
	for p in pops.duplicate():
		p[1] -= 1; p[0].position.y -= 1.0; p[0].modulate.a = p[1] / 40.0
		if p[1] <= 0: p[0].queue_free(); pops.erase(p)
