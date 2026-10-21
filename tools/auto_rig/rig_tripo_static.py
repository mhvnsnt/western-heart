#!/usr/bin/env python3
"""tools/auto_rig/rig_tripo_static.py — one command to auto-rig an unrigged Tripo static for the game.

Owner 2026-10-21: "Unrigged static statue models need to be rigged and skinned fully the auto way
as soon as they get in and get connected to a character". This chains the repo's open-source steps
that rigged Zui A1 (docs/proof/claude-2026-10-21/auto-rig-zui/):

  1. tools/anim/gltf_codec.mjs decode     (Tripo/gltfpack meshopt -> plain glTF for Blender)
  2. tools/auto_rig/backends/gamerig_backend.py   (GameRig/Rigify skeleton, bone heat via proxy,
                                                   CMU boxing clip baked as the deformation test)
  3. tools/auto_rig/backends/smooth_weights.py    (stretch-driven weight smoothing)
  4. tools/auto_rig/validate.py + anim_check.py   (the playable gate + the official anim gate)
  5. tools/auto_rig/render_poses.py               (front/back/side renders at the gate's worst frames)
  6. tools/anim/gltf_codec.mjs encode     (meshopt again, so the shipped file stays small)

The original file is never modified: the result is written beside it as <name>-rigged.glb (or --out).
Wiring the rigged file into game/js/assets.js stays a reviewed step (the script prints the line).

    python3 tools/auto_rig/rig_tripo_static.py --in roster/X/attires/attire1/model.glb \\
        --report-dir docs/proof/<date>/auto-rig-X [--facing +Z] [--keep-work]

Env: WH_BLENDER (Blender 4.0.2 binary), NODE_PATH (the node_modules folder holding @gltf-transform +
meshoptimizer; tools/setup/setup_toolchain.sh installs both; the codec runs from a copy linked to it,
since ES modules ignore NODE_PATH). Exit code 0 only when every step ran; the gate
verdicts are reported in <report-dir>/rig_report.json and must be read (UNKNOWN is never PASS).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CODEC = os.path.join(REPO, "tools", "anim", "gltf_codec.mjs")
DONOR = os.path.join(REPO, "assets", "free-pull-1", "cmu-mocap", "fighting", "135_04.bvh")


def run(cmd, env=None, log=None):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    if log:
        with open(log, "a") as f:
            f.write("$ " + " ".join(cmd) + "\n" + r.stdout[-20000:] + r.stderr[-20000:] + "\n")
    if r.returncode != 0:
        sys.exit(f"step failed ({r.returncode}): {' '.join(cmd[:6])}\n{r.stderr[-3000:]}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--report-dir", required=True)
    ap.add_argument("--facing", default=None, help="mesh facing for gamerig_backend (e.g. +Z) when the feet cue is unsure")
    ap.add_argument("--height", default="1.8")
    ap.add_argument("--keep-work", action="store_true")
    a = ap.parse_args()
    blender = os.environ.get("WH_BLENDER") or os.path.expanduser(
        "~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")
    out = a.out or os.path.splitext(a.inp)[0] + "-rigged.glb"
    os.makedirs(a.report_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="wh-rig-")
    log = os.path.join(work, "steps.log")
    dec, rig = os.path.join(work, "decoded.glb"), os.path.join(work, "rigged.glb")
    # ES modules ignore NODE_PATH: run a copy of the codec beside a node_modules link instead.
    codec = CODEC
    if os.environ.get("NODE_PATH") and not os.path.isdir(os.path.join(os.path.dirname(CODEC), "node_modules")):
        cdir = os.path.join(work, "codec")
        os.makedirs(cdir)
        os.symlink(os.environ["NODE_PATH"].split(os.pathsep)[0], os.path.join(cdir, "node_modules"))
        codec = shutil.copy(CODEC, os.path.join(cdir, "gltf_codec.mjs"))
    bl = ["xvfb-run", "-a", "env", "-u", "PYTHONPATH", "XDG_RUNTIME_DIR=/tmp", blender, "-b", "--factory-startup", "--python"]

    run(["node", codec, "decode", a.inp, dec], log=log)
    cmd = bl + [os.path.join(HERE, "backends", "gamerig_backend.py"), "--", "--in", dec, "--out", rig,
                "--height", a.height, "--donor", DONOR, "--clip", "CMU135_04_boxing", "--clip-start", "240",
                "--clip-frames", "72", "--clip-step", "4", "--metrics-out", os.path.join(a.report_dir, "gamerig_metrics.json")]
    if a.facing:
        cmd += ["--facing", a.facing]
    run(cmd, log=log)
    gate_before = os.path.join(a.report_dir, "anim_check_before_smoothing.json")
    subprocess.run([sys.executable, os.path.join(HERE, "anim_check.py"), "--in", rig, "--json-out", gate_before,
                    "--max-frames", "18", "--quiet"], capture_output=True)
    sm = run([sys.executable, os.path.join(HERE, "backends", "smooth_weights.py"), "--in", rig, "--threshold", "2.0",
              "--rounds", "12", "--frames-per-clip", "10", "--gate", "2.5"],
             env={"PYTHONPATH": HERE}, log=log)
    with open(os.path.join(a.report_dir, "smooth_weights.log"), "w") as f:
        f.write(sm.stdout)
    val = subprocess.run([sys.executable, os.path.join(HERE, "validate.py"), "--in", rig], capture_output=True, text=True)
    gate = os.path.join(a.report_dir, "anim_check_after_smoothing.json")
    subprocess.run([sys.executable, os.path.join(HERE, "anim_check.py"), "--in", rig, "--json-out", gate,
                    "--max-frames", "18", "--quiet"], capture_output=True)
    rep = json.load(open(gate))
    anim = list(rep.get("animations", {}).values())
    spike_times = sorted({round(s["time"], 2) for an in anim for s in an.get("tearing", {}).get("spikes", [])})
    times = ",".join(str(t) for t in ([0.0] + spike_times[:2] if spike_times else [0.0, 1.2, 1.7]))
    pose_dir = os.path.join(work, "poses")
    os.makedirs(pose_dir, exist_ok=True)
    run(bl + [os.path.join(HERE, "render_poses.py"), "--", rig, pose_dir, times], log=log)
    for fn in os.listdir(pose_dir):
        shutil.copy(os.path.join(pose_dir, fn), os.path.join(a.report_dir, fn))
    run(["node", codec, "encode", rig, out], log=log)
    vtxt = val.stdout[val.stdout.find("{"):] if "{" in val.stdout else "{}"
    try:
        vjs = json.loads(vtxt)
    except json.JSONDecodeError:
        vjs = {"raw": val.stdout[-2000:]}
    summary = {
        "input": a.inp, "output": out, "tool": "tools/auto_rig/rig_tripo_static.py",
        "validate": {k: vjs.get(k) for k in ("checks", "pass", "missing_bones", "height_m")},
        "anim_check": {an["name"]: {"pass": an["pass"], "failures": an["failures"],
                                    "edge_stretch_p999": an.get("edge_stretch_p999")} for an in anim},
        "pose_renders": sorted(f for f in os.listdir(pose_dir)),
        "verdict_note": "Read the renders before wiring: anim_check flags must be explained, UNKNOWN is never PASS.",
        "wire_line": f"'<model-key>': '../{os.path.relpath(out, REPO)}',",
    }
    with open(os.path.join(a.report_dir, "rig_report.json"), "w") as f:
        json.dump(summary, f, indent=1)
    shutil.copy(log, os.path.join(a.report_dir, "steps.log"))
    if not a.keep_work:
        shutil.rmtree(work, ignore_errors=True)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
