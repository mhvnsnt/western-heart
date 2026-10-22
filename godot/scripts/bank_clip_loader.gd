class_name BankClipLoader
extends RefCounted

## Builds a Godot Animation from a decoded wh-anim/1 bank clip (the same JSON
## the web runtime plays via game/js/t3anims.js), so the Godot build runs on
## REAL decoded Tekken 3 motion — teardown data, not keyframed placeholders.
##
## RETARGET METHOD — world-delta transfer (the runtime counterpart of a
## BoneMap retarget; the same principle as the web runtime's solver):
##   1. FK the clip on its OWN canonical-22 rig (rest locals are identity;
##      rest world positions ship in assets/anim/t3_skeleton.json).
##   2. Per bone, the world-space delta D = world_pose * inverse(world_rest).
##   3. Apply D (converted from glTF space to the target skeleton's space)
##      to the target rig's rest world pose; convert back to bone locals
##      top-down and key those.
## A naive bind-premultiply of the raw local quaternions was tried first and
## REJECTED with probe evidence: the canonical rig's bone-local axes do not
## match the target rig's, so every simple formula lifted the feet ~0.5 m at
## the strike frame. World-space deltas are the quantity that transfers.
##
## Canonical mapping (from t3anims.js): 'Chest' -> target 'Spine2' when the
## target has Spine2 and no Chest; 'Root' has no counterpart (its translation
## is the root_t track, applied to the target Hips as a position delta);
## target 'Spine1' (no canonical counterpart) takes slerp(D Spine, D Chest).

const CANON_TO_TARGET := {"Chest": "Spine2"}
const SKELETON_PATH := "res://assets/anim/t3_skeleton.json"

const CONV_NONE := 0
const CONV_ROTX90 := 1   # glTF Y-up -> Godot skeleton space (rotX +90)
const CONV_ROTXM90 := 2  # rotX -90
const CONV_ZMIRROR := 3  # Z-mirror conjugation
const CONV_XMIRROR := 4  # X-mirror conjugation
const CONV_ROTY180 := 5  # rotY 180 conjugation

static var _bank_skel: Dictionary = {}


static func _conv_quat(q: Quaternion, conv: int) -> Quaternion:
	match conv:
		CONV_ROTX90:
			var p := Quaternion(Vector3(1, 0, 0), PI / 2.0)
			return (p * q * p.inverse()).normalized()
		CONV_ROTXM90:
			var p := Quaternion(Vector3(1, 0, 0), -PI / 2.0)
			return (p * q * p.inverse()).normalized()
		CONV_ZMIRROR:
			return Quaternion(-q.x, -q.y, q.z, q.w)
		CONV_XMIRROR:
			return Quaternion(q.x, -q.y, -q.z, q.w)
		CONV_ROTY180:
			var p := Quaternion(Vector3(0, 1, 0), PI)
			return (p * q * p.inverse()).normalized()
	return q


static func _conv_vec(v: Vector3, conv: int) -> Vector3:
	match conv:
		CONV_ROTX90: return Vector3(v.x, -v.z, v.y)
		CONV_ROTXM90: return Vector3(v.x, v.z, -v.y)
		CONV_ZMIRROR: return Vector3(v.x, v.y, -v.z)
		CONV_XMIRROR: return Vector3(-v.x, v.y, v.z)
		CONV_ROTY180: return Vector3(-v.x, v.y, -v.z)
	return v


static func _load_bank_skeleton() -> Dictionary:
	if not _bank_skel.is_empty():
		return _bank_skel
	var data = JSON.parse_string(FileAccess.get_file_as_string(SKELETON_PATH))
	var order: Array = []
	var parent: Dictionary = {}
	var rest_world: Dictionary = {}
	for j in data["joints"]:
		var n: String = j["name"]
		order.append(n)
		parent[n] = j["parent"] if j["parent"] != null else ""
		var r: Array = j["rest"]
		rest_world[n] = Vector3(float(r[0]), float(r[1]), float(r[2]))
	_bank_skel = {"order": order, "parent": parent, "rest_world": rest_world}
	return _bank_skel


## Pick the space conversion for a target rig from its own rest pose:
## canonical space is glTF (Y-up, faces +Z). A rig whose skeleton space is
## Z-up (e.g. Pantera — its armature wrapper carries the axis conversion)
## needs rotX+90; a rig already in Y-up skeleton space (e.g. Star) needs at
## most the Z mirror, decided by which way its toes point.
static func detect_conv(skeleton: Skeleton3D) -> int:
	var world := _rest_world(skeleton)
	var pos: Array = world[0]
	var hips := pos[skeleton.find_bone("Hips")] as Vector3
	var head := pos[skeleton.find_bone("Head")] as Vector3
	var up := head - hips
	if absf(up.z) > absf(up.y):
		return CONV_ROTX90
	var foot := pos[skeleton.find_bone("LeftFoot")] as Vector3
	var toe_i := skeleton.find_bone("LeftToeBase")
	if toe_i >= 0:
		var toe := pos[toe_i] as Vector3
		if toe.z < foot.z:
			# Rig faces -Z in its own skeleton space (Star): its space is the
			# canonical space turned 180 degrees about Y — a proper rotation,
			# NOT a mirror (probe evidence: Z-mirror threw her guard overhead,
			# rotY180 lands hands at guard height 0.97-1.31, head above hips).
			return CONV_ROTY180
	return CONV_NONE


## FK over a skeleton's rest pose -> [world positions, world quaternions].
static func _rest_world(skeleton: Skeleton3D) -> Array:
	var count := skeleton.get_bone_count()
	var pos: Array[Vector3] = []
	var quat: Array[Quaternion] = []
	pos.resize(count)
	quat.resize(count)
	for i in count:
		var rest := skeleton.get_bone_rest(i)
		var rp := rest.origin
		var rq := rest.basis.get_rotation_quaternion()
		var par := skeleton.get_bone_parent(i)
		if par < 0:
			pos[i] = rp
			quat[i] = rq
		else:
			quat[i] = quat[par] * rq
			pos[i] = pos[par] + quat[par] * rp
	return [pos, quat]


static func load_clip(path: String, skeleton: Skeleton3D, track_prefix: String, conv: int = CONV_ROTX90, use_root_motion: bool = true) -> Animation:
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(data) != TYPE_DICTIONARY:
		push_error("BankClipLoader: bad JSON in " + path)
		return null
	var fps: float = data.get("fps", 30.0)
	var rots: Dictionary = data.get("rot_xyzw", {})
	var root_t: Array = data.get("root_t", [])
	var bs := _load_bank_skeleton()
	var order: Array = bs["order"]
	var bparent: Dictionary = bs["parent"]
	var brest: Dictionary = bs["rest_world"]
	var frame_count: int = (rots[rots.keys()[0]] as Array).size()

	# Source local offsets (rest world - parent rest world).
	var offset: Dictionary = {}
	for n in order:
		var p: String = bparent[n]
		offset[n] = brest[n] - (brest[p] if p != "" else Vector3.ZERO)

	# Target rig: rest world pose via FK over the skeleton's own rests.
	var bone_count := skeleton.get_bone_count()
	var trest_quat: Array[Quaternion] = []
	trest_quat.resize(bone_count)
	for i in bone_count:
		trest_quat[i] = skeleton.get_bone_rest(i).basis.get_rotation_quaternion()
	var rest_world := _rest_world(skeleton)
	var tworld_pos: Array = rest_world[0]
	var tworld_quat: Array = rest_world[1]

	# Which canonical bone drives each target bone?
	var driver: Dictionary = {}  # target idx -> canonical name ("" = none)
	for i in bone_count:
		var tname := skeleton.get_bone_name(i)
		var canon := ""
		if rots.has(tname):
			canon = tname
		elif tname == "Spine2" and rots.has("Chest") and skeleton.find_bone("Chest") < 0:
			canon = "Chest"
		elif tname == "Spine1":
			canon = "@spine1"  # virtual: slerp of Spine/Chest deltas
		driver[i] = canon

	var anim := Animation.new()
	anim.length = float(frame_count) / fps
	# Pre-create rotation tracks for driven bones + a Hips position track.
	var rot_track: Dictionary = {}
	for i in bone_count:
		if driver[i] != "":
			var t := anim.add_track(Animation.TYPE_ROTATION_3D)
			anim.track_set_path(t, NodePath(track_prefix + ":" + skeleton.get_bone_name(i)))
			rot_track[i] = t
	# Hip translation: applied only when use_root_motion (attack clips — the
	# leap lives in root_t). Looping stance/walk clips skip it, matching the
	# web runtime, which never applies root_t (the stance slot even contains
	# a deep get-up crouch in its root track that must not dip the fighter).
	var hips_idx := skeleton.find_bone("Hips")
	var pos_track := -1
	if use_root_motion:
		pos_track = anim.add_track(Animation.TYPE_POSITION_3D)
		anim.track_set_path(pos_track, NodePath(track_prefix + ":Hips"))

	for f in frame_count:
		var time := float(f) / fps
		# --- source FK (canonical rig, identity rest rotations) ---
		var swq: Dictionary = {}
		var swp: Dictionary = {}
		for n in order:
			var p: String = bparent[n]
			var lq := Quaternion.IDENTITY
			if rots.has(n) and f < (rots[n] as Array).size():
				var a: Array = rots[n][f]
				lq = Quaternion(float(a[0]), float(a[1]), float(a[2]), float(a[3]))
			if p == "":
				var rt: Array = root_t[f]
				swp[n] = Vector3(float(rt[0]), float(rt[1]), float(rt[2]))
				swq[n] = lq
			else:
				swq[n] = swq[p] * lq
				swp[n] = swp[p] + swq[p] * offset[n]
		# World deltas (source rest world rotations are identity, so D == swq,
		# computed generally anyway would need rest FK — identity by format).
		var delta: Dictionary = {}
		for n in order:
			delta[n] = _conv_quat(swq[n], conv)
		# --- apply to target, top-down (skeleton index order is topological) ---
		var posed_wq: Array[Quaternion] = []
		posed_wq.resize(bone_count)
		for i in bone_count:
			var par := skeleton.get_bone_parent(i)
			var parent_wq := Quaternion.IDENTITY if par < 0 else posed_wq[par]
			var canon: String = driver[i]
			if canon == "":
				# Undriven bone: hold rest local.
				posed_wq[i] = parent_wq * trest_quat[i]
				continue
			var d: Quaternion
			if canon == "@spine1":
				d = delta["Spine"].slerp(delta["Chest"], 0.5)
			else:
				d = delta[canon]
			posed_wq[i] = d * tworld_quat[i]
			var local_q := (parent_wq.inverse() * posed_wq[i]).normalized()
			anim.rotation_track_insert_key(rot_track[i], time, local_q)
		# Hips position: rest world + converted source hip displacement.
		if use_root_motion:
			var src_hip_delta: Vector3 = swp["Hips"] - brest["Hips"]
			var hip_pos: Vector3 = tworld_pos[hips_idx] + _conv_vec(src_hip_delta, conv)
			anim.position_track_insert_key(pos_track, time, hip_pos)
	# Quaternion sign continuity: FK products can emit q where the neighboring
	# key has -q (same rotation, opposite sign); interpolating across a sign
	# flip takes the long way around and visibly tumbles the body mid-clip.
	# Enforce dot(prev, cur) >= 0 along every rotation track.
	for t in anim.get_track_count():
		if anim.track_get_type(t) != Animation.TYPE_ROTATION_3D:
			continue
		var prev: Quaternion = anim.track_get_key_value(t, 0)
		for k in range(1, anim.track_get_key_count(t)):
			var cur: Quaternion = anim.track_get_key_value(t, k)
			if prev.dot(cur) < 0.0:
				cur = -cur
				anim.track_set_key_value(t, k, cur)
			prev = cur
	print("BankClipLoader: %s -> %d driven bones, %d frames @ %dfps (conv=%d)" % [path, rot_track.size(), frame_count, int(fps), conv])
	return anim
