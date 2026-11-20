# Kaggle GPU script 2/3 — Blender Cycles GPU render proof (runs INSIDE Blender).
# NOTEBOOK SETUP CELL (run first in the Kaggle notebook, GPU accelerator ON):
#   !wget -q https://download.blender.org/release/Blender4.5/blender-4.5.3-linux-x64.tar.xz
#   !tar -xf blender-4.5.3-linux-x64.tar.xz
#   !./blender-4.5.3-linux-x64/blender --background --python kaggle_blender_cycles_gpu.py
#   (Upload this file to the notebook working dir first.)
# PROOF: Blender prints GPU_PROOF lines (Cycles device, GPU used, output
#   PNG path + sha256). Paste that block back as the GPU-render record.
# WHAT IT RENDERS: a built-in smoke-test scene (monkey head + lights).
#   Rendering a WH GLB is the same script with an import step first:
#   bpy.ops.import_scene.gltf(filepath="fighter.glb") before render.
import hashlib, os

OUT = "/kaggle/working/gpu_proof.png"

import bpy
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "CUDA"
prefs.get_devices()
cuda_devices = [d for d in prefs.devices if d.type == "CUDA"]
for d in prefs.devices:
    d.use = (d.type == "CUDA")
print("GPU_PROOF: cycles_device_type", prefs.compute_device_type)
print("GPU_PROOF: cuda_devices", [d.name for d in cuda_devices])
print("GPU_PROOF: cycles_device_setting", scene.cycles.device)
if not cuda_devices:
    print("GPU_PROOF: status NO_CUDA_DEVICE_FOUND (is the notebook GPU accelerator ON?)")
    raise SystemExit(1)
# Smoke-test scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
bpy.ops.object.light_add(type="SUN", location=(5, -5, 10))
bpy.ops.object.camera_add(location=(4, -5, 3), rotation=(1.1, 0, 0.7))
scene.camera = bpy.context.object
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
h = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
print("GPU_PROOF: output", OUT, os.path.getsize(OUT), "bytes")
print("GPU_PROOF: output_sha256", h)
print("GPU_PROOF: status COMPLETE")
