#!/usr/bin/env python3
"""tools/auto_rig/auto_rig.py — unified auto-rig CLI for Western Heart.

    python3 auto_rig.py --in MODEL.glb --out RIGGED.glb --backend BACKEND

Backends:
    blender-heat       CPU. Bone-heat auto-rig onto the fixed WH skeleton
                       (mesh fits the skeleton). The PR #264-proven path.
                       Needs: Blender 4.0.2 at ~/workspace/tools/blender/.
    knn                CPU. k-NN weight transfer from a donor rigged mesh.
                       For dense Tripo statics (~1M verts).
    magicarticulate    GPU. AI skeleton prediction (Apache-2.0, vendored).
    unirig             GPU. AI skeleton + skinning (MIT, vendored).
    puppeteer          GPU. AI rig + video-guided animation (Apache-2.0).

Every run ends with validate.py (the playable gate). Nothing ships that
doesn't pass.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.path.expanduser("~/workspace/tools/blender/blender-4.0.2-linux-x64/blender")


def run(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(cmd, capture_output=True, text=True, env=e)
    if r.returncode != 0:
        print(r.stdout[-2000:], file=sys.stderr)
        print(r.stderr[-2000:], file=sys.stderr)
        raise RuntimeError("command failed: " + " ".join(cmd[:4]))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--backend", required=True,
                    choices=["blender-heat", "knn", "magicarticulate",
                             "unirig", "puppeteer"])
    ap.add_argument("--donor", default=None, help="knn donor rigged GLB")
    ap.add_argument("--height", type=float, default=1.8)
    ap.add_argument("--skip-validate", action="store_true")
    a = ap.parse_args()

    bdir = os.path.join(HERE, "backends")
    if a.backend == "blender-heat":
        # two stages: normalize (pure python) then rig (Blender)
        norm = a.out + ".normalized.glb"
        run([sys.executable, os.path.join(bdir, "normalize.py"),
             "--in", a.inp, "--out", norm, "--height", str(a.height)])
        env = {"XDG_RUNTIME_DIR": "/tmp"}
        run(["xvfb-run", "-a", "env", "-u", "PYTHONPATH", BLENDER, "-b",
             "--factory-startup", "--python",
             os.path.join(bdir, "blender_heat.py"), "--",
             "--in", norm, "--out", a.out, "--mesh-facing=-Z"],
            env=env)
        os.remove(norm)
    elif a.backend == "knn":
        if not a.donor:
            sys.exit("--donor is required for the knn backend")
        run([sys.executable, os.path.join(bdir, "knn_transfer.py"),
             "--in", a.inp, "--donor", a.donor, "--out", a.out])
        print("knn weights written to %s.npz — apply with apply_skin.py" % a.out)
    else:
        run([sys.executable, os.path.join(bdir, "ai_rig.py"),
             "--backend", a.backend, "--in", a.inp])

    if not a.skip_validate and a.backend == "blender-heat":
        r = run([sys.executable, os.path.join(HERE, "validate.py"),
                 "--in", a.out])
        print(r.stdout)


if __name__ == "__main__":
    main()
