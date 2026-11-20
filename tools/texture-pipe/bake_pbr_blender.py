#!/usr/bin/env python3
"""
bake_pbr_blender.py — headless Blender PBR map baker for WH fighters.

Takes a gray-clay GLB and bakes a texture set from the mesh itself:
  - AO          (Blender bake, per-vertex dirt in crevices)
  - normal      (tangent-space; from --highpoly if given, else from the mesh)
  - roughness   (cavity heuristic: dark AO -> rougher)
  - albedo      (flat mid-gray fallback; paint over it in ArmorPaint/GIMP)

Also ensures the mesh has usable UVs (Smart UV Project when missing).

Usage (headless):
  xvfb-run -a env -u PYTHONPATH <blender> -b --python bake_pbr_blender.py -- \\
      --in MODEL.glb --outdir TEXDIR/ [--size 1024] [--highpoly HIPOLY.glb]
      [--samples 16]

Output: TEXDIR/{material}_{ao,normal,roughness,albedo}.png
"""
import argparse, os, sys

import bpy

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--size", type=int, default=1024)
    p.add_argument("--highpoly", default=None)
    p.add_argument("--samples", type=int, default=16)
    return p.parse_args(argv)

def ensure_uvs(obj):
    me = obj.data
    if not me.uv_layers:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
        print(f"  UVs: smart-projected for {obj.name}", flush=True)
    else:
        print(f"  UVs: existing ({len(me.uv_layers)} layers)", flush=True)

def new_image(name, size):
    img = bpy.data.images.new(name, width=size, height=size,
                              alpha=False, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if name.endswith("_albedo") else "Non-Color"
    return img

def bake(obj, img, bake_type, use_selected=False):
    mat = obj.data.materials[0] if obj.data.materials else None
    if mat is None:
        mat = bpy.data.materials.new(name="__bake__")
        obj.data.materials.append(mat)
    mat.use_nodes = True
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    mat.node_tree.nodes.active = tex
    for n in mat.node_tree.nodes:
        n.select = (n == tex)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = ARGS.samples
    scene.cycles.device = "CPU"
    scene.render.bake.use_selected_to_active = use_selected
    bpy.ops.object.bake(type=bake_type, use_clear=True, margin=16)
    mat.node_tree.nodes.remove(tex)

def main():
    global ARGS
    ARGS = parse_args()
    os.makedirs(ARGS.outdir, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=ARGS.inp)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise SystemExit("no meshes in " + ARGS.inp)
    print(f"baking {len(meshes)} mesh(es) from {ARGS.inp}", flush=True)

    hipoly = []
    if ARGS.highpoly:
        bpy.ops.import_scene.gltf(filepath=ARGS.highpoly)
        hipoly = [o for o in bpy.context.scene.objects
                  if o.type == "MESH" and o not in meshes]
        print(f"highpoly sources: {len(hipoly)}", flush=True)

    import numpy as np
    for obj in meshes:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.context.view_layer.update()
        ensure_uvs(obj)
        tag = obj.data.materials[0].name if obj.data.materials else obj.name
        tag = "".join(c if c.isalnum() or c in "-_" else "_" for c in tag)

        ao_img = new_image(f"{tag}_ao", ARGS.size)
        bake(obj, ao_img, "AO")
        ao_img.filepath_raw = os.path.join(ARGS.outdir, f"{tag}_ao.png")
        ao_img.file_format = "PNG"
        ao_img.save()

        nrm_img = new_image(f"{tag}_normal", ARGS.size)
        if hipoly:
            for h in hipoly:
                h.select_set(True)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bake(obj, nrm_img, "NORMAL", use_selected=True)
            for h in hipoly:
                h.select_set(False)
        else:
            bake(obj, nrm_img, "NORMAL")
        nrm_img.filepath_raw = os.path.join(ARGS.outdir, f"{tag}_normal.png")
        nrm_img.file_format = "PNG"
        nrm_img.save()

        # roughness from inverted AO (cheap cavity heuristic)
        w, h = ao_img.size
        px = np.array(ao_img.pixels[:]).reshape(h, w, 4)
        rough = 1.0 - px[..., 0] * 0.5
        rough_img = new_image(f"{tag}_roughness", ARGS.size)
        rgba = np.dstack([rough, rough, rough, np.ones_like(rough)])
        rough_img.pixels = rgba.ravel().tolist()
        rough_img.filepath_raw = os.path.join(ARGS.outdir, f"{tag}_roughness.png")
        rough_img.file_format = "PNG"
        rough_img.save()

        # albedo: flat mid-gray base for painting over
        alb_img = new_image(f"{tag}_albedo", ARGS.size)
        alb_img.pixels = [0.5, 0.5, 0.5, 1.0] * (ARGS.size * ARGS.size)
        alb_img.filepath_raw = os.path.join(ARGS.outdir, f"{tag}_albedo.png")
        alb_img.file_format = "PNG"
        alb_img.save()

        print(f"  wrote {tag}_{{ao,normal,roughness,albedo}}.png", flush=True)
        obj.select_set(False)

    print("BAKE DONE ->", ARGS.outdir, flush=True)

if __name__ == "__main__":
    main()
