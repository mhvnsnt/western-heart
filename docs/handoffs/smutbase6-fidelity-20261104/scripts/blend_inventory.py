import bpy, json, sys, os

out_path = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/blend-inv.json"

data = {"blender_version": list(bpy.app.version), "file": bpy.data.filepath}
armatures = []
for ob in bpy.data.objects:
    if ob.type == "ARMATURE":
        armatures.append({
            "name": ob.name,
            "bone_count": len(ob.data.bones),
            "bones": [b.name for b in ob.data.bones],
            "pose_bone_count": len(ob.pose.bones) if ob.pose else 0,
        })
data["armatures"] = armatures

meshes = []
total_verts = 0
for ob in bpy.data.objects:
    if ob.type == "MESH":
        sk = []
        if ob.data.shape_keys:
            sk = [kb.name for kb in ob.data.shape_keys.key_blocks]
        meshes.append({
            "name": ob.name,
            "verts": len(ob.data.vertices),
            "polys": len(ob.data.polygons),
            "hide_viewport": bool(ob.hide_viewport),
            "hide_render": bool(ob.hide_render),
            "hide_get": bool(ob.hide_get()) if hasattr(ob, "hide_get") else None,
            "materials": [s.material.name if s.material else None for s in ob.material_slots],
            "uv_layers": [uv.name for uv in ob.data.uv_layers],
            "shape_keys": sk,
            "vertex_groups": len(ob.vertex_groups),
            "parent": ob.parent.name if ob.parent else None,
            "modifiers": [m.type for m in ob.modifiers],
        })
        total_verts += len(ob.data.vertices)
data["meshes"] = meshes
data["mesh_count"] = len(meshes)
data["total_verts"] = total_verts
data["object_count"] = len(bpy.data.objects)
data["objects_by_type"] = {}
for ob in bpy.data.objects:
    data["objects_by_type"][ob.type] = data["objects_by_type"].get(ob.type, 0) + 1

images = []
for im in bpy.data.images:
    images.append({
        "name": im.name, "size": [im.size[0], im.size[1]],
        "filepath": im.filepath, "packed": bool(im.packed_file),
        "source": im.source,
    })
data["images"] = images

mats = []
for m in bpy.data.materials:
    imgs = []
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                imgs.append(n.image.name)
    mats.append({"name": m.name, "tex_images": imgs, "use_nodes": bool(m.use_nodes)})
data["materials"] = mats
data["actions"] = [{"name": a.name, "frame_range": [a.frame_range[0], a.frame_range[1]]} for a in bpy.data.actions]

with open(out_path, "w") as f:
    json.dump(data, f, indent=1)
print("INVENTORY_WRITTEN", out_path)
