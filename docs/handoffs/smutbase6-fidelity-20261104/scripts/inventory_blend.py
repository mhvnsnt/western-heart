import bpy, json, sys, os

argv = sys.argv[sys.argv.index("--") + 1:]
blend_path, out_json = argv[0], argv[1]

info = {"path": blend_path, "file_size": os.path.getsize(blend_path)}
info["blender_version_file"] = ".".join(str(x) for x in bpy.data.version)
info["blender_version_running"] = bpy.app.version_string

objs = list(bpy.data.objects)
info["object_count"] = len(objs)
by_type = {}
for o in objs:
    by_type[o.type] = by_type.get(o.type, 0) + 1
info["objects_by_type"] = by_type

armatures = []
total_bones = 0
for o in objs:
    if o.type == "ARMATURE":
        nb = len(o.data.bones)
        total_bones += nb
        armatures.append({"name": o.name, "bones": nb})
info["armatures"] = armatures
info["total_bones"] = total_bones

# shape keys: total key blocks minus Basis per mesh
mesh_objs = [o for o in objs if o.type == "MESH"]
total_keys = 0
meshes_with_keys = 0
per_mesh = []
for o in mesh_objs:
    kb = o.data.shape_keys
    if kb and len(kb.key_blocks) > 1:
        n = len(kb.key_blocks) - 1
        total_keys += n
        meshes_with_keys += 1
        per_mesh.append({"mesh": o.name, "shape_keys": n})
info["shape_keys_total_nonbasis"] = total_keys
info["meshes_with_shape_keys"] = meshes_with_keys
info["shape_keys_per_mesh"] = sorted(per_mesh, key=lambda d: -d["shape_keys"])[:20]

imgs = list(bpy.data.images)
packed = [i for i in imgs if i.packed_file]
info["images_total"] = len(imgs)
info["images_packed"] = len(packed)

info["object_names"] = sorted(o.name for o in objs)

with open(out_json, "w") as f:
    json.dump(info, f, indent=1)
print("INVENTORY_DONE", out_json)
