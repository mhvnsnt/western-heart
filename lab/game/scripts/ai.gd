## Simple deterministic CPU opponent: spacing, pokes, whiff punishes, blocking.
class_name FighterAI
extends RefCounted

var rng := RandomNumberGenerator.new()
var hold := {}
var wait := 0
var aggression := 0.6

func _init(seed: int, aggr: float = 0.6) -> void:
	rng.seed = seed; aggression = aggr

func think(me: Fighter, opp: Fighter) -> Dictionary:
	var out := {"fwd": false, "back": false, "block": false}
	var dist := absf(opp.position.x - me.position.x)
	if wait > 0:
		wait -= 1
		for k in hold: out[k] = hold[k]
		return out
	hold = {}
	if me.state in ["hitstun", "attack", "ko"]:
		return out
	if opp.is_attacking() and dist < 1.6 and rng.randf() < 0.45:
		hold = {"block": true, "back": true}; wait = rng.randi_range(10, 24)
	elif dist > 1.25:
		hold = {"fwd": true}; wait = rng.randi_range(6, 18)
	elif rng.randf() < aggression:
		var r := rng.randf()
		var slot := "light" if r < 0.38 else ("medium" if r < 0.68 else ("heavy" if r < 0.9 else "grab"))
		out[slot + "_pressed"] = true
		wait = rng.randi_range(4, 14)
	else:
		hold = {"back": true}; wait = rng.randi_range(8, 20)
	for k in hold: out[k] = hold[k]
	return out
