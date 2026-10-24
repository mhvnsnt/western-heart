#!/usr/bin/env python3
"""run_gltfpack_job.py — gltfpack optimize job for the suite job queue.

Spec: {"tool":"gltfpack","params":{"in":"<input.glb>","cc":True},"out":"<out.glb>"}
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
    cmd = [_bin(), "-i", os.path.abspath(src), "-o", os.path.abspath(out),
           "-cc", "-tc"]
    if params.get("no_quant"):
        cmd = [_bin(), "-i", os.path.abspath(src), "-o", os.path.abspath(out)]
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
