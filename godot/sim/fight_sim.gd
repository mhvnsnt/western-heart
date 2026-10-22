class_name FightSim
extends RefCounted

## Deterministic fixed-step fight simulation core — Western Heart (Godot).
##
## ARCHITECTURE LAW (engine research, owner lock 2026-10-21): the fight state
## lives HERE, in a pure simulation that advances one fixed tick at a time from
## integer input bitmasks. No Node references, no engine physics, no wall
## clock, no RNG — same inputs in, same state out, on every machine. That is
## what makes rollback netcode possible later (Godot's own physics is
## documented non-deterministic, so the fight must never be driven by it).
## Presentation (fighter_view.gd / main.gd) only READS this state.

const TICK_RATE := 60.0          # ticks per second (matches project physics tps)
const WALK_SPEED := 1.7          # m/s — Tekken-3-derived lab value (1.7 m per 60 frames)
const WALK_BACK_SPEED := 1.3     # m/s
const ATTACK_TICKS := 52         # t3_light: 26 frames @30fps = 52 ticks @60Hz
const ATTACK_LUNGE := 0.55       # m/s forward drift while attacking
const PUSH_DISTANCE := 0.85      # min separation between fighters (lab PUSHBOX)
const ARENA_MIN := -4.4
const ARENA_MAX := 4.4

# Input bits (per fighter, per tick)
const IN_LEFT := 1
const IN_RIGHT := 2
const IN_ATTACK := 4

# Fighter states
const ST_IDLE := 0
const ST_WALK_FWD := 1
const ST_WALK_BACK := 2
const ST_ATTACK := 3

var frame := 0                   # absolute tick counter — the only clock

var p1_x := -1.2
var p2_x := 1.2
var p1_state := ST_IDLE
var p2_state := ST_IDLE
var p1_state_frame := 0          # ticks spent in current state
var p2_state_frame := 0
var p1_facing := 1               # +1 faces +X, -1 faces -X
var p2_facing := -1

var _p1_prev_input := 0
var _p2_prev_input := 0


## Advance the simulation exactly one tick. Inputs are bitmasks (IN_*).
func step(p1_input: int, p2_input: int) -> void:
	frame += 1
	_step_fighter(1, p1_input, _p1_prev_input)
	_step_fighter(2, p2_input, _p2_prev_input)
	_p1_prev_input = p1_input
	_p2_prev_input = p2_input
	# Facing: always face the opponent (slice rule; real game adds crouch/turn states).
	p1_facing = 1 if p2_x >= p1_x else -1
	p2_facing = -p1_facing
	# Pushbox: fighters cannot occupy the same space.
	var mid := (p1_x + p2_x) * 0.5
	if p2_x - p1_x < PUSH_DISTANCE:
		p1_x = mid - PUSH_DISTANCE * 0.5
		p2_x = mid + PUSH_DISTANCE * 0.5
	p1_x = clampf(p1_x, ARENA_MIN, ARENA_MAX)
	p2_x = clampf(p2_x, ARENA_MIN, ARENA_MAX)


func _step_fighter(who: int, input: int, prev_input: int) -> void:
	var x := p1_x if who == 1 else p2_x
	var state := p1_state if who == 1 else p2_state
	var sframe := p1_state_frame if who == 1 else p2_state_frame
	var facing := p1_facing if who == 1 else p2_facing
	sframe += 1
	if state == ST_ATTACK:
		x += ATTACK_LUNGE * facing / TICK_RATE
		if sframe >= ATTACK_TICKS:
			state = ST_IDLE
			sframe = 0
	else:
		var fwd := IN_RIGHT if facing > 0 else IN_LEFT
		var back := IN_LEFT if facing > 0 else IN_RIGHT
		if input & fwd:
			state = ST_WALK_FWD
			x += WALK_SPEED * facing / TICK_RATE
		elif input & back:
			state = ST_WALK_BACK
			x -= WALK_BACK_SPEED * facing / TICK_RATE
		else:
			state = ST_IDLE
		# Attack triggers on the press edge only.
		if (input & IN_ATTACK) and not (prev_input & IN_ATTACK):
			state = ST_ATTACK
			sframe = 0
	if who == 1:
		p1_x = x; p1_state = state; p1_state_frame = sframe
	else:
		p2_x = x; p2_state = state; p2_state_frame = sframe


## Read-only snapshot for the presentation layer.
func state_name(state: int) -> String:
	match state:
		ST_IDLE: return "idle"
		ST_WALK_FWD: return "walk_fwd"
		ST_WALK_BACK: return "walk_back"
		ST_ATTACK: return "attack"
	return "?"
