class_name FighterView
extends Node3D

## Presentation layer for one fighter. Owns NOTHING about the fight — it
## instantiates the model, exposes its AnimationPlayer, and mirrors whatever
## state FightSim reports. All fight logic lives in sim/fight_sim.gd.
##
## NOTE on clip sharing: copying another rig's Animation resources verbatim
## does NOT transfer across these rigs (probe evidence: the receiving fighter
## ended up lying flat — the stored locals are absolute poses in the source
## rig's bone frames). Cross-rig clips go through BankClipLoader's
## world-delta retarget instead. Same-profile bone names are necessary but
## not sufficient; the world-space delta is what transfers.

var model: Node3D
var skeleton: Skeleton3D
var anim_player: AnimationPlayer
## Node path from the AnimationPlayer's root to this fighter's Skeleton3D
## (e.g. "Character/Skeleton3D"). Animation tracks are addressed with it.
var track_prefix := ""
var _current_clip := ""


## glb_scene: an imported roster GLB (PackedScene from Godot's glTF import).
## model_yaw: base rotation so the model faces +X when the sim says facing=+1.
func setup(glb_scene: PackedScene, model_yaw: float) -> void:
	model = glb_scene.instantiate()
	model.rotation.y = model_yaw
	add_child(model)
	var skels := model.find_children("*", "Skeleton3D", true, false)
	if not skels.is_empty():
		skeleton = skels[0]
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty():
		anim_player = AnimationPlayer.new()
		model.add_child(anim_player)
	else:
		anim_player = players[0]
	if skeleton and anim_player:
		var ap_root: Node = anim_player.get_node(anim_player.root_node)
		track_prefix = str(ap_root.get_path_to(skeleton))
	# Embedded library clips (Idle/Walk/Run on the shipped models) loop.
	for lib_name in anim_player.get_animation_library_list():
		var lib := anim_player.get_animation_library(lib_name)
		for clip_name in lib.get_animation_list():
			if clip_name in ["Idle", "Walk", "Run"]:
				lib.get_animation(clip_name).loop_mode = Animation.LOOP_LINEAR


func add_clip(clip_name: String, anim: Animation, library_name: String = "bank") -> void:
	if not anim_player.has_animation_library(library_name):
		anim_player.add_animation_library(library_name, AnimationLibrary.new())
	anim_player.get_animation_library(library_name).add_animation(clip_name, anim)


func play_clip(full_name: String, restart: bool = false) -> void:
	if full_name == _current_clip and not restart:
		return
	if anim_player.has_animation(full_name):
		anim_player.play(full_name)
		_current_clip = full_name


## Mirror one sim snapshot (position along the fight axis + facing).
## Facing is a Y-rotation of the view root (never a negative scale — that
## would invert the mesh winding). Skeleton animation is bone-local, so the
## root rotation does not disturb it.
func apply_sim(x: float, facing: int) -> void:
	position = Vector3(x, 0.0, 0.0)
	rotation.y = 0.0 if facing > 0 else PI
