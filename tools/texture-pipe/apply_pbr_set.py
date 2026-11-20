#!/usr/bin/env python3
"""
apply_pbr_set.py — wire a PBR texture set into a GLB, headless Blender.

Reads a manifest (see tools/texture-pipe/README.md) mapping GLB material
names to texture files, builds Principled BSDF node trees, exports a
textured GLB ready for the game (glTF metallic-roughness workflow).

Usage (headless):
  xvfb-run -a env -u PYTHONPATH <blender> -b --python apply_pbr_set.py -- \\
      --in MODEL.glb --setdir TEXDIR/ --manifest TEXDIR/manifest.json \\
      --out MODEL-textured.glb

Texture keys per material: baseColor (sRGB), normal (Non-Color),
roughness (Non-Color), metallic as scalar, ao (Non-Color, multiplied
into baseColor), emissive (sRGB).
"""
import argparse, json, os, sys

import bpy

SRGB_KEYS = {"baseColor", "albedo", "emissive"}

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--setdir", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)

def load_image(path, srgb):
    img = bpy.data.images.load(path)
    img.colorspace_settings.name = "sRGB" if srgb else "Non-Color"
    return img

def wire_material(mat, spec, setdir):
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.get("Material Output") or nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def tex_node(key, label):
        fname = spec.get(key)
        if not fname:
            return None
        path = os.path.join(setdir, fname)
        if not os.path.exists(path):
            print(f"  WARN: {label} file missing: {path}", flush=True)
            return None
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = load_image(path, key in SRGB_KEYS)
        node.label = label
        return node

    # baseColor (+ optional AO multiply)
    bc = tex_node("baseColor", "BaseColor")
    ao = tex_node("ao", "AO")
    if bc:
        src = bc.outputs["Color"]
        if ao:
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = "MULTIPLY"
            mix.inputs["Fac"].default_value = 1.0
            nt.links.new(bc.outputs["Color"], mix.inputs["Color1"])
            nt.links.new(ao.outputs["Color"], mix.inputs["Color2"])
            src = mix.outputs["Color"]
        nt.links.new(src, bsdf.inputs["Base Color"])

    nrm = tex_node("normal", "Normal")
    if nrm:
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.space = "TANGENT"
        nt.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])

    rgh = tex_node("roughness", "Roughness")
    if rgh:
        nt.links.new(rgh.outputs["Color"], bsdf.inputs["Roughness"])
    elif isinstance(spec.get("roughness"), (int, float)):
        bsdf.inputs["Roughness"].default_value = float(spec["roughness"])

    if isinstance(spec.get("metallic"), (int, float)):
        bsdf.inputs["Metallic"].default_value = float(spec["metallic"])
    met = tex_node("metallicMap", "Metallic")
    if met:
        nt.links.new(met.outputs["Color"], bsdf.inputs["Metallic"])

    emi = tex_node("emissive", "Emissive")
    if emi:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emissive"
        nt.links.new(emi.outputs["Color"], bsdf.inputs[key])

def main():
    args = parse_args()
    with open(args.manifest) as f:
        manifest = json.load(f)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=args.inp)

    wired, missing = 0, []
    for mat in bpy.data.materials:
        spec = manifest.get(mat.name)
        if not spec:
            low = mat.name.lower().replace(" ", "")
            hit = next((k for k in manifest if k.lower().replace(" ", "") == low), None)
            spec = manifest.get(hit) if hit else None
        if not spec:
            missing.append(mat.name)
            continue
        wire_material(mat, spec, args.setdir)
        wired += 1
    print(f"wired {wired} material(s); no manifest entry for: {missing or 'none'}", flush=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=args.out,
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
    )
    print("WROTE", args.out, flush=True)

if __name__ == "__main__":
    main()
