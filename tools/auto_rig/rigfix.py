"""tools/auto_rig/rigfix.py — ONE automatic rig/skin fix pass.

    python3 rigfix.py --in MODEL.glb --out MODEL_rigfixed.glb \
        [--report REPORT.json] [--smooth-iters 6]

Pipeline (each stage is a real tool in this folder, not a guess):
  1. skin_audit (backends/skin_audit.py) — measure the input: weight
     sums, unweighted verts, JOINTS_1 overflow, DEAD major joints,
     cross-body CONTAMINATION (far-segment weights), skeleton
     proportions vs the WH template, folded chains, joints outside
     the mesh, feet planted. Stretch numbers alone missed every one
     of these in the field (Leopard King #448); this stage exists so
     the numbers that matter are measured before anyone claims a fix.
  2. weight_cleanup (backends/weight_cleanup.py) — fix what's
     fixable in the weight domain: prune contaminated slots, revive
     globally dead major joints by proximity reassignment to their
     anatomical territory, fill unweighted verts, edge-Laplacian
     smoothing, prune-to-4 + exact renormalization.
  3. skin_audit again on the OUTPUT — the fix only counts if the
     audit passes on the file that will ship.
  4. validate.py playable gate on the output.

The input file is never modified. Exit code 0 only when the output
passes the full skin audit AND the validate gate's hard checks
(valid glTF, skinned, bones present, height in range).

For models whose skeleton/proportions are wrong (not just weights),
run auto_rig.py / refit_skeleton.py first — this pass fixes weights
on the model's own skeleton and says so in the report. For a full
heat-diffusion re-skin inside Blender, see backends/surface_heat.py
(vendored MIT Surface Heat Diffuse Skinning) with blender_heat.py as
the built-in fallback.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "backends"))


def run_audit(path):
    import skin_audit
    import importlib
    importlib.reload(skin_audit)
    return skin_audit.audit(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report")
    ap.add_argument("--smooth-iters", type=int, default=6)
    ap.add_argument("--revive-frac", type=float, default=0.5)
    ap.add_argument("--skip-cleanup", action="store_true",
                    help="audit only (before/after measurement)")
    a = ap.parse_args()

    rep = {"in": a.inp, "out": a.out, "stages": {}}
    before = run_audit(a.inp)
    rep["stages"]["audit_before"] = {
        "pass": before["pass"], "checks": before["checks"],
        "measured": before["measured"]}
    print(f"audit_before pass={before['pass']} "
          f"dead={before['measured'].get('dead_major_joints')} "
          f"contam={before['measured'].get('contaminated_weight_mass')}")

    if not a.skip_cleanup:
        import weight_cleanup
        crep = weight_cleanup.cleanup(a.inp, a.out,
                                      revive_frac=a.revive_frac,
                                      smooth_iters=a.smooth_iters)
        rep["stages"]["cleanup"] = crep["changes"]
        rep["stages"]["cleanup_dead"] = crep.get("dead_major_joints")
        print("cleanup:", crep["changes"])
    else:
        rep["stages"]["cleanup"] = "skipped"

    after = run_audit(a.out if not a.skip_cleanup else a.inp)
    rep["stages"]["audit_after"] = {
        "pass": after["pass"], "checks": after["checks"],
        "measured": after["measured"]}
    print(f"audit_after pass={after['pass']} "
          f"dead={after['measured'].get('dead_major_joints')} "
          f"contam={after['measured'].get('contaminated_weight_mass')}")

    target = a.out if not a.skip_cleanup else a.inp
    val = subprocess.run([sys.executable,
                          os.path.join(HERE, "validate.py"),
                          "--in", target], capture_output=True, text=True)
    try:
        vrep = json.loads(val.stdout)
        vchecks = vrep.get("checks", {})
    except Exception:
        vchecks = {}
    rep["stages"]["validate"] = vchecks
    hard = all(vchecks.get(k) is True for k in
               ("valid_gltf", "skinned_mesh", "bones_present",
                "height_ok"))
    rep["pass"] = bool(after["pass"] and hard)
    print("validate hard checks:", hard, "| RIGFIX PASS:", rep["pass"])
    if a.report:
        with open(a.report, "w") as f:
            json.dump(rep, f, indent=1)
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
