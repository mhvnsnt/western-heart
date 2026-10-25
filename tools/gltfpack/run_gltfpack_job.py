#!/usr/bin/env python3
"""run_gltfpack_job.py — gltfpack optimize job for the suite job queue.

Spec: {"tool":"gltfpack","params":{"in":"<input.glb>","cc":True},"out":"<out.glb>"}

Flag policy (Lane 5, 2026-10-24 — pinned, do not drift):
  -cc : ON by default. Safe: game/js/assets.js calls
        loader.setMeshoptDecoder(MeshoptDecoder), so -cc outputs
        load as-is. Never use bare -c.
  -kn : ON by default. Bone names are load-bearing for skinned
        fighters (the EXPORT panel optimizes fighters). The batch
        runner (batch-optimize.py) omits -kn for UNSKINNED stage
        props only, where it measurably costs size (Jungle Outpost:
        -cc 219,160 bytes without -kn vs 284,540 with -kn).
  -tc : OPT-IN ONLY (params.tc must be true). Texture compression
        GREW a textured model +7% in one measurement, and -tc
        output needs the three.js Basis transcoder (WASM) wired
        before it ships — never a silent default. Measure per asset.
  -si : OFF unless params.simplify_ratio AND
        params.simplify_approved are both set. Simplification is
        NEVER blind on a skinned fighter (LOD is stages/props only,
        owner eye-check per asset).
  no_quant (legacy): plain run, no flags at all.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _bin():
    p = os.path.join(HERE, "vendor", "gltfpack")
    if not os.path.isfile(p):
        raise RuntimeError("gltfpack not fetched. Run: bash tools/gltfpack/fetch-gltfpack.sh")
    return p


def run_job(spec, log=print):
    params = spec.get("params", {})
    src = params["in"]
    out = spec.get("out")
    if not out:
        raise RuntimeError("spec needs 'out'")
    before = os.path.getsize(src)
    if params.get("no_quant"):
        cmd = [_bin(), "-i", os.path.abspath(src), "-o", os.path.abspath(out)]
    else:
        cmd = [_bin(), "-i", os.path.abspath(src), "-o", os.path.abspath(out)]
        if params.get("cc", True):
            cmd.append("-cc")
        if params.get("kn", True):
            cmd.append("-kn")
        if params.get("tc"):
            cmd.append("-tc")
        if params.get("simplify_ratio"):
            if not params.get("simplify_approved"):
                raise RuntimeError(
                    "simplification refused: set simplify_approved=true "
                    "per asset (owner eye-check) — never simplify blind, "
                    "never a skinned fighter without approval")
            cmd += ["-si", str(params["simplify_ratio"])]
    log("run: " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    log(r.stdout[-1500:] if r.stdout else "")
    if r.returncode != 0:
        raise RuntimeError("gltfpack failed:\n" + (r.stderr or "")[-2000:])
    after = os.path.getsize(out)
    log(f"optimized: {before/1e6:.1f}MB -> {after/1e6:.1f}MB")
    return os.path.abspath(out)


def main(argv=None):
    import argparse, json, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    a = ap.parse_args(argv)
    with open(a.spec) as fh:
        spec = json.load(fh)
    print(run_job(spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
