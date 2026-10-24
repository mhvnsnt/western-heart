## Per-character height metadata applied at runtime (owner rule c).
## Measures the model's rest-pose mesh height, then scales the model so it stands
## at data/characters/heights.json height_cm. Unknown/null heights keep native size.
class_name HeightScale
extends RefCounted

const DATA := "res://data/characters/heights.json"
static var _db := {}

static func entry(char_id: String) -> Dictionary:
	if _db.is_empty():
		_db = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	return _db["characters"].get(char_id, {})

static func height_cm(char_id: String) -> float:
	var h = entry(char_id).get("height_cm")
	return float(h) if h != null else 0.0

## Rest-pose height in meters of every mesh under `model`, in the model's parent space.
static func measure(model: Node3D) -> float:
	var lo := INF; var hi := -INF
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		var xf: Transform3D = model.transform * model.global_transform.affine_inverse() * m.global_transform \
			if m.is_inside_tree() else _rel(model, m)
		var box: AABB = xf * m.get_aabb()
		lo = minf(lo, box.position.y); hi = maxf(hi, box.end.y)
	return hi - lo if hi > lo else 0.0

static func _rel(model: Node3D, n: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY; var c: Node = n
	while c != null and c != model:
		if c is Node3D: t = (c as Node3D).transform * t
		c = c.get_parent()
	return model.transform * t

## Scales `model` to the character's height. Returns the applied height in cm (0 = unchanged).
static func apply(model: Node3D, char_id: String) -> float:
	var target := height_cm(char_id)
	if target <= 0.0: return 0.0
	model.scale = Vector3.ONE
	var native := measure(model)
	if native <= 0.0: return 0.0
	var s := (target / 100.0) / native
	model.scale = Vector3.ONE * s
	return target
