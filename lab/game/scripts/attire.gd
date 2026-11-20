## Shared, editable attire attachment (Bannon mask first). Loads <id>.manifest.json,
## finds the head socket by alias, applies the per-rig preset + user transform, and exposes
## material params (tint, texture on/off, roughness, metallic, emission, normal strength) and part toggles.
## API: var a := Attire.attach(skeleton, "res://attire/bannon_mask/bannon_mask.manifest.json", "wh_canonical_t3", {"tint": Color.RED})
class_name Attire
extends BoneAttachment3D

var manifest := {}
var preset := {}
var holder: Node3D
var mesh_root: Node3D
var materials := []   # duplicated, editable StandardMaterial3D per surface
var params := {}

static func attach(skel: Skeleton3D, manifest_path: String, rig_id: String, overrides := {}) -> Attire:
	var a := Attire.new()
	a.manifest = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
	a.preset = a.manifest["presets"][rig_id]
	var bone := -1
	for alias in [a.preset["bone"]] + Array(a.manifest["socket"]["bone_aliases"]):
		bone = skel.find_bone(alias)
		if bone >= 0: break
	assert(bone >= 0, "attire: no head bone on skeleton")
	a.bone_idx = bone
	skel.add_child(a)
	a.holder = Node3D.new(); a.add_child(a.holder)
	var scene: PackedScene = load(manifest_path.get_base_dir().path_join(a.manifest["mesh"]))
	a.mesh_root = scene.instantiate(); a.holder.add_child(a.mesh_root)
	for mi in a.mesh_root.find_children("*", "MeshInstance3D", true, false):
		for s in (mi as MeshInstance3D).mesh.get_surface_count():
			var src = (mi as MeshInstance3D).mesh.surface_get_material(s)
			var m: StandardMaterial3D = (src.duplicate() if src is StandardMaterial3D else StandardMaterial3D.new())
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			(mi as MeshInstance3D).set_surface_override_material(s, m); a.materials.append(m)
	for slot in a.manifest["material_slots"]:
		for k in slot["params"]: a.params[k] = slot["params"][k]["default"]
	a.set_transform_params(a.manifest.get("user_transform", {}))
	a.set_params(overrides)
	return a

## The bone's rest orientation is applied by BoneAttachment3D; the preset is expressed in that frame.
func set_transform_params(user: Dictionary) -> void:
	var o: Array = preset["offset"]; var q: Array = preset["rotation"]
	var add: Array = user.get("offset_add", [0, 0, 0]); var e: Array = user.get("rotation_euler_deg_add", [0, 0, 0])
	var basis := Basis(Quaternion(q[0], q[1], q[2], q[3])) * Basis.from_euler(Vector3(deg_to_rad(e[0]), deg_to_rad(e[1]), deg_to_rad(e[2])))
	var s: float = float(preset["scale"]) * float(user.get("scale_mul", 1.0))
	holder.transform = Transform3D(basis.scaled(Vector3.ONE * s), Vector3(o[0] + add[0], o[1] + add[1], o[2] + add[2]))

func set_params(p: Dictionary) -> void:
	for k in p: params[k] = p[k]
	for m in materials:
		var t = params.get("tint", [1, 1, 1, 1])
		m.albedo_color = t if t is Color else Color(t[0], t[1], t[2], t[3])
		if not params.get("use_texture", true): m.albedo_texture = null
		m.roughness = params.get("roughness", 0.7); m.metallic = params.get("metallic", 0.0)
		var em = params.get("emission", [0, 0, 0, 1]); var ec: Color = em if em is Color else Color(em[0], em[1], em[2])
		m.emission_enabled = params.get("emission_energy", 0.0) > 0.0
		m.emission = ec; m.emission_energy_multiplier = params.get("emission_energy", 0.0)
		m.normal_scale = params.get("normal_strength", 1.0)

func set_part(part_id: String, on: bool) -> void:
	if part_id == "whole": mesh_root.visible = on
