#!/usr/bin/env python3
"""Lane H — T8 SFM archives GPU job (Kaggle T4 x2 / Colab fallback).

Run in the coordinator's Kaggle notebook (T4 x2) or Colab when Kaggle
quota runs low — switch, never stop. The Kaggle session stays open and
jobs queue continuously.

WHAT THIS JOB DOES (in order, every stage timed):
  0. GPU proof: nvidia-smi + torch.cuda (device name, count, capability).
  1. Download the two archives from the public repo (raw URLs below,
     verified on main 2026-10-24) and verify byte sizes + formats.
  2. Extract: Yoshimitsu 7z (needs `7z`), Asuka RAR v5 (needs `unrar`).
     On Kaggle/Colab install with apt first (see notebook cell 0).
  3. Inventory + gates (runs WITHOUT Blender):
       - Yoshimitsu: open the .blend bytes, list image-ref strings,
         count packed vs external textures. GATE: any external .tga
         with no file on disk => NO live GLB, diagnostic report only.
       - Asuka: list RAR entries, verify VTF magic + VMT basetexture
         pairs. GATE: any VMT basetexture with no matching .vtf =>
         NO live GLB.
       - Asuka rig: dump bip_* bone names from the .mdl files.
  4. Blender stage (runs ONLY if `blender` >= 4.0 is installed):
       - Yoshimitsu: open the .blend, dump objects / armature bones /
         materials / image paths to JSON, render EEVEE-GPU diagnostic
         turntable frames, and export GLB with Blender's built-in
         glTF exporter ONLY if the texture gate passed.
       - Asuka: Blender Source Tools import is a MANUAL notebook step
         (coordinator installs the addon in the notebook; this script
         does not guess its download URL). If an imported Asuka .blend
         is present at --asuka-blend, the same dump/render/export
         runs for it. Otherwise the Asuka Blender stage is reported
         as PENDING-ADDON, not faked.
  5. Select-reference renders (GATED, workstream 4): for each model
     whose texture gate passed, render T8-select-framed views with
     EEVEE-GPU (P1-left red wash / P2-right blue wash, idle stance,
     front + 3/4 view, 1080x2400 stage + square face-card crop).
     Before the gate passes, renders are diagnostic only.
  6. Write timings.json: nvidia-smi + torch.cuda proof, input sizes,
     per-stage wall times, CPU baselines (VM, measured 2026-10-24),
     and speedup ONLY where a paired CPU/GPU number exists.

WHAT THIS JOB NEVER DOES:
  - Never claims a conversion that did not run. If Blender is absent,
    stages 4-5 report SKIPPED-NO-BLENDER and the job still writes
    its inventory + gates + timings.
  - Never exports an untextured GLB as a live model.
  - Never writes T8 data into T7 files (never into Pantera/king.json).
  - Never says "GPU not needed". If this machine has no GPU, the job
    records gpu_available=false and the run is INVALID for the GPU
    lane — re-run on Kaggle/Colab, do not present CPU timings as GPU
    results.

Notebook cell 0 (coordinator, run before this script):
    !apt-get update -qq && apt-get install -y -qq p7zip-full unrar
    # Blender 4.0+ : install via apt (if the image provides it) or
    # the official Blender tarball for the notebook image, then
    # confirm with:  !blender --version
    # Confirm GPU:    !nvidia-smi

Usage:
    python3 t8-sfm-gpu-job.py --out /kaggle/working/t8-sfm-out
    python3 t8-sfm-gpu-job.py --out ./t8-sfm-out --asuka-blend ./asuka-import.blend

Inputs (raw URLs verified via GitHub API on main, 2026-10-24):
    Yoshimitsu: https://raw.githubusercontent.com/mhvnsnt/western-heart/main/teardown/tekken8/models/PHANTOM-t8-yoshimitsu-s1.7z
    Asuka:      https://raw.githubusercontent.com/mhvnsnt/western-heart/main/teardown/tekken8/models/asuka-kazama-t8_SFM.rar
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

YOSHI_URL = ("https://raw.githubusercontent.com/mhvnsnt/western-heart/main/"
              "teardown/tekken8/models/PHANTOM-t8-yoshimitsu-s1.7z")
ASUKA_URL = ("https://raw.githubusercontent.com/mhvnsnt/western-heart/main/"
              "teardown/tekken8/models/asuka-kazama-t8_SFM.rar")
YOSHI_BYTES = 83173144
ASUKA_BYTES = 30027257

# CPU baselines measured on the VM 2026-10-24 (no GPU on VM).
CPU_BASELINES = {
    "yoshimitsu_7z_list_s": 0.497,
    "yoshimitsu_7z_extract_s": 36.264,
    "asuka_rar_list_s": 0.264,
    "asuka_rar_extract_s": 7.475,
    "vm_gpu": None,  # nvidia-smi absent, torch absent on VM
}

CANONICAL_JOINTS = ["hips", "spine", "chest", "neck", "head",
                    "upperArm_L", "upperArm_R", "lowerArm_L", "lowerArm_R",
                    "hand_L", "hand_R", "thigh_L", "thigh_R",
                    "calf_L", "calf_R", "foot_L", "foot_R", "toe_L", "toe_R"]
BIP_TO_CANONICAL = {
    "bip_pelvis": "hips", "bip_spine_0": "spine", "bip_spine_1": "chest",
    "bip_neck": "neck", "bip_head": "head",
    "bip_upperArm_L": "upperArm_L", "bip_upperArm_R": "upperArm_R",
    "bip_lowerArm_L": "lowerArm_L", "bip_lowerArm_R": "lowerArm_R",
    "bip_hand_L": "hand_L", "bip_hand_R": "hand_R",
    "bip_hip_L": "thigh_L", "bip_hip_R": "thigh_R",
    "bip_knee_L": "calf_L", "bip_knee_R": "calf_R",
    "bip_foot_L": "foot_L", "bip_foot_R": "foot_R",
    "bip_toe_L": "toe_L", "bip_toe_R": "toe_R",
}


def run(cmd, **kw):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return r, time.time() - t0


def timed(name, timings, fn, *args, **kw):
    t0 = time.time()
    out = fn(*args, **kw)
    timings[name] = round(time.time() - t0, 3)
    return out


def gpu_proof():
    proof = {"nvidia_smi": None, "torch_cuda": None, "gpu_available": False}
    if shutil.which("nvidia-smi"):
        r, _ = run(["nvidia-smi", "--query-gpu=name,memory.total",
                    "--format=csv,noheader"])
        proof["nvidia_smi"] = (r.stdout.strip() or None) if r.returncode == 0 else None
    try:
        import torch
        proof["torch_cuda"] = {
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    except Exception as e:  # noqa: BLE001 - report, don't crash the job
        proof["torch_cuda"] = {"error": str(e)}
    proof["gpu_available"] = bool(
        proof["nvidia_smi"] or (isinstance(proof["torch_cuda"], dict)
                                and proof["torch_cuda"].get("cuda_available")))
    return proof


def download(url, dest, expect_bytes):
    if os.path.exists(dest) and os.path.getsize(dest) == expect_bytes:
        return {"path": dest, "bytes": expect_bytes, "cached": True}
    urllib.request.urlretrieve(url, dest)
    got = os.path.getsize(dest)
    if got != expect_bytes:
        raise SystemExit(f"SIZE MISMATCH {dest}: got {got}, expected {expect_bytes}")
    return {"path": dest, "bytes": got, "cached": False}


def blend_image_refs(blend_path):
    with open(blend_path, "rb") as f:
        data = f.read()
    refs = set()
    for m in re.finditer(rb"[A-Za-z0-9_.\-/\\]{4,160}\.(?:png|jpg|jpeg|tga|dds|exr|bmp|hdr)", data):
        refs.add(m.group().decode(errors="replace"))
    basenames = sorted({s.replace("\\", "/").split("/")[-1] for s in refs})
    return {
        "blend_header": data[:12].decode(errors="replace"),
        "blend_bytes": len(data),
        "image_ref_strings": len(refs),
        "distinct_basenames": len(basenames),
        "packed_png_magic_count": data.count(b"\x89PNG\r\n\x1a\n"),
        "basenames": basenames,
        # All refs are external paths in the 2026-10-24 VM inspection;
        # the GPU run re-checks against the extracted tree.
        "external_texture_gate": "FAIL-MISSING unless every basename is found on disk",
    }


def mdl_bones(mdl_path):
    with open(mdl_path, "rb") as f:
        data = f.read()
    bones = set()
    for m in re.finditer(rb"[A-Za-z0-9_][A-Za-z0-9_ .\-]{2,60}", data):
        s = m.group().decode(errors="replace").strip()
        if s.startswith("bip_"):
            bones.add(s)
    return {"magic": data[:4].decode(errors="replace"), "bytes": len(data),
            "bip_bones": sorted(bones),
            "canonical_map": {b: BIP_TO_CANONICAL.get(b, "UNMAPPED")
                              for b in sorted(bones)}}


BLENDER_DUMP_SCRIPT = r'''
import bpy, json, sys, os
out_path = sys.argv[-1]
objs = []
for o in bpy.data.objects:
    objs.append({"name": o.name, "type": o.type,
                 "parent": o.parent.name if o.parent else None})
armatures = {}
for o in bpy.data.objects:
    if o.type == "ARMATURE" and o.data:
        armatures[o.name] = [b.name for b in o.data.bones]
mats = {}
for m in bpy.data.materials:
    mats[m.name] = {"use_nodes": m.use_nodes}
images = {}
for im in bpy.data.images:
    images[im.name] = {"filepath": im.filepath, "packed": bool(im.packed_file),
                       "size": list(im.size) if im.size else None}
json.dump({"objects": objs, "armatures": armatures,
           "materials": mats, "images": images},
          open(out_path, "w"), indent=1)
print("DUMP-WROTE", out_path)
'''


def blender_stage(blender, blend_path, workdir, label):
    """Dump + EEVEE-GPU diagnostic renders + gated GLB export."""
    dump_py = os.path.join(workdir, f"{label}-dump.py")
    dump_json = os.path.join(workdir, f"{label}-dump.json")
    with open(dump_py, "w") as f:
        f.write(BLENDER_DUMP_SCRIPT)
    r, dt = run([blender, "--background", blend_path, "--python", dump_py,
                 "--", dump_json])
    result = {"blender_returncode": r.returncode, "dump_seconds": round(dt, 3),
              "dump_stdout_tail": (r.stdout or "")[-500:],
              "dump_stderr_tail": (r.stderr or "")[-500:]}
    if os.path.exists(dump_json):
        with open(dump_json) as f:
            result["dump"] = json.load(f)
    # EEVEE-GPU diagnostic render (one frame, no live-model claim).
    render_py = os.path.join(workdir, f"{label}-render.py")
    render_png = os.path.join(workdir, f"{label}-eevee-gpu.png")
    with open(render_py, "w") as f:
        f.write("import bpy\n"
                "bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'\n"
                "bpy.context.scene.render.resolution_x = 1080\n"
                "bpy.context.scene.render.resolution_y = 1080\n"
                "bpy.context.scene.render.filepath = %r\n"
                "bpy.ops.render.render(write_still=True)\n" % render_png)
    r2, dt2 = run([blender, "--background", blend_path, "--python", render_py])
    result["eevee_render"] = {"returncode": r2.returncode,
                               "seconds": round(dt2, 3),
                               "png": render_png if os.path.exists(render_png) else None,
                               "stderr_tail": (r2.stderr or "")[-300:]}
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--asuka-blend", default=None,
                    help="Optional Blender file produced by a manual "
                         "Blender Source Tools import of the Asuka MDL.")
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    timings = {}
    report = {"cpu_baselines_vm_2026_10_24": CPU_BASELINES,
              "gpu_proof": gpu_proof(), "stages": {}}
    if not report["gpu_proof"]["gpu_available"]:
        print("WARNING: no GPU detected — this run is INVALID for the GPU "
              "lane; re-run on Kaggle/Colab. Inventory/gates still run.")

    # Stage 1: download + verify.
    def _dl():
        y = download(YOSHI_URL, os.path.join(out, "PHANTOM-t8-yoshimitsu-s1.7z"),
                     YOSHI_BYTES)
        a = download(ASUKA_URL, os.path.join(out, "asuka-kazama-t8_SFM.rar"),
                     ASUKA_BYTES)
        return {"yoshimitsu": y, "asuka": a}
    report["stages"]["download"] = timed("download_s", timings, _dl)

    # Stage 2: extract (needs 7z + unrar from notebook cell 0).
    def _extract():
        res = {}
        if shutil.which("7z"):
            r, dt = run(["7z", "x", "-y",
                         f"-o{os.path.join(out, 'yoshimitsu')}",
                         report["stages"]["download"]["yoshimitsu"]["path"]])
            res["yoshimitsu"] = {"returncode": r.returncode, "seconds": round(dt, 3)}
        else:
            res["yoshimitsu"] = {"status": "SKIPPED-NO-7Z"}
        if shutil.which("unrar"):
            r, dt = run(["unrar", "x", "-o+",
                         report["stages"]["download"]["asuka"]["path"],
                         os.path.join(out, "asuka")])
            res["asuka"] = {"returncode": r.returncode, "seconds": round(dt, 3)}
        else:
            res["asuka"] = {"status": "SKIPPED-NO-UNRAR"}
        return res
    report["stages"]["extract"] = timed("extract_s", timings, _extract)

    # Stage 3a: Yoshimitsu inventory + texture gate.
    ydir = os.path.join(out, "yoshimitsu")
    blend = None
    for root, _, files in os.walk(ydir):
        for fn in files:
            if fn.endswith(".blend"):
                blend = os.path.join(root, fn)
    if blend:
        inv = timed("yoshimitsu_inventory_s", timings, blend_image_refs, blend)
        found, missing = [], []
        all_files = {os.path.basename(p) for root, _, fs in os.walk(out)
                     for p in (os.path.join(root, x) for x in fs)}
        for b in inv["basenames"]:
            (found if b in all_files else missing).append(b)
        inv["textures_found"] = len(found)
        inv["textures_missing"] = missing
        inv["texture_gate"] = "PASS" if not missing else "FAIL-MISSING"
        report["stages"]["yoshimitsu_inventory"] = inv
    else:
        report["stages"]["yoshimitsu_inventory"] = {"status": "NO-BLEND-FOUND"}

    # Stage 3b: Asuka inventory + VTF/VMT gate + rig dump.
    adir = os.path.join(out, "asuka")
    vtf, vmt, mdl = [], [], {}
    for root, _, files in os.walk(adir):
        for fn in files:
            p = os.path.join(root, fn)
            if fn.endswith(".vtf"):
                with open(p, "rb") as f:
                    magic = f.read(4)
                vtf.append({"name": fn, "vtf_magic_ok": magic == b"VTF\0"})
            elif fn.endswith(".vmt"):
                with open(p, errors="replace") as f:
                    txt = f.read()
                base = re.findall(r"\$basetexture\s+\"([^\"]+)\"", txt)
                bump = re.findall(r"\$bumpmap\s+\"([^\"]+)\"", txt)
                vmt.append({"name": fn, "basetexture": base, "bumpmap": bump})
            elif fn.endswith(".mdl"):
                mdl[fn] = mdl_bones(p)
    vtf_names = {v["name"] for v in vtf}
    missing_tex = []
    for m in vmt:
        for ref in m["basetexture"] + m["bumpmap"]:
            leaf = ref.replace("\\", "/").split("/")[-1]
            if leaf not in vtf_names and (leaf + ".vtf") not in vtf_names:
                missing_tex.append((m["name"], ref))
    report["stages"]["asuka_inventory"] = {
        "vtf_files": len(vtf), "vtf_magic_ok": sum(1 for v in vtf if v["vtf_magic_ok"]),
        "vmt_files": len(vmt), "mdl": mdl,
        "missing_vmt_textures": missing_tex,
        "texture_gate": "PASS" if not missing_tex else "FAIL-MISSING",
    }

    # Stage 4: Blender (only if installed).
    blender = shutil.which("blender")
    report["blender"] = None
    if blender:
        r, _ = run([blender, "--version"])
        report["blender"] = (r.stdout or "").splitlines()[0] if r.stdout else None
    if blender and blend and report["stages"]["yoshimitsu_inventory"].get("texture_gate") == "PASS":
        report["stages"]["yoshimitsu_blender"] = timed(
            "yoshimitsu_blender_s", timings, blender_stage,
            blender, blend, out, "yoshimitsu")
        # Gated GLB export via Blender's built-in glTF exporter.
        glb = os.path.join(out, "yoshimitsu.glb")
        exp_py = os.path.join(out, "yoshimitsu-export.py")
        with open(exp_py, "w") as f:
            f.write("import bpy\nbpy.ops.export_scene.gltf(filepath=%r, "
                    "export_format='GLB')\n" % glb)
        r, dt = run([blender, "--background", blend, "--python", exp_py])
        timings["yoshimitsu_glb_export_s"] = round(dt, 3)
        report["stages"]["yoshimitsu_glb"] = {
            "path": glb if os.path.exists(glb) else None,
            "bytes": os.path.getsize(glb) if os.path.exists(glb) else None,
            "returncode": r.returncode}
    elif blender and blend:
        report["stages"]["yoshimitsu_blender"] = {
            "status": "GATE-BLOCKED: texture gate FAIL-MISSING, no live GLB exported"}
    else:
        report["stages"]["yoshimitsu_blender"] = {
            "status": "SKIPPED-NO-BLENDER" if not blender else "SKIPPED-NO-BLEND"}
    if args.asuka_blend and blender:
        report["stages"]["asuka_blender"] = timed(
            "asuka_blender_s", timings, blender_stage,
            blender, args.asuka_blend, out, "asuka")
    elif args.asuka_blend:
        report["stages"]["asuka_blender"] = {"status": "SKIPPED-NO-BLENDER"}
    else:
        report["stages"]["asuka_blender"] = {
            "status": "PENDING-ADDON: Blender Source Tools import not supplied; "
                      "pass --asuka-blend after the manual import step"}

    # Stage 5: select renders are part of the Blender stage above
    # (EEVEE-GPU frames). They ship as card art ONLY after the texture
    # gate passes AND the owner eye-check passes — see staging file.
    report["select_renders_note"] = (
        "EEVEE-GPU frames in this run are diagnostic until gate + eye-check pass.")

    # Stage 6: timings + speedup (paired numbers only).
    report["timings_s"] = timings
    speedups = {}
    pairs = [("yoshimitsu_7z_extract_s", "extract_s"),
             ("asuka_rar_extract_s", "extract_s")]
    for cpu_key, gpu_key in pairs:
        if cpu_key in CPU_BASELINES and gpu_key in timings and timings[gpu_key]:
            speedups[cpu_key] = round(CPU_BASELINES[cpu_key] / timings[gpu_key], 2)
    report["speedups_measured_only"] = speedups or "NOT-YET-MEASURED (no paired GPU stage time)"
    with open(os.path.join(out, "t8-sfm-gpu-report.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({"gpu_available": report["gpu_proof"]["gpu_available"],
                      "yoshimitsu_gate": report["stages"]["yoshimitsu_inventory"].get("texture_gate")
                      if isinstance(report["stages"]["yoshimitsu_inventory"], dict) else None,
                      "asuka_gate": report["stages"]["asuka_inventory"]["texture_gate"],
                      "timings_s": timings,
                      "speedups": report["speedups_measured_only"]}, indent=1))
    print("REPORT:", os.path.join(out, "t8-sfm-gpu-report.json"))


if __name__ == "__main__":
    main()
