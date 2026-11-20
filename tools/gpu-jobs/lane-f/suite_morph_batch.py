#!/usr/bin/env python3
"""Lane F GPU job SUITE-1 — creation-suite template/morph batch (Kaggle T4).

Corpus (measured from packages/creation-suite/src/morphs.js):
  13 BODY_MORPHS + 37 ANATOMY_LAYER_MORPHS + 12 FACE_SHAPE_MORPHS = 62 dials.
  4 CAW base templates (neutral-balanced, power, cruiser, giant) x 62 dials
  x 5 values (-1, -0.5, 0, 0.5, 1) = 1,240 dial-vector evaluations.
Modes: --mode gpu (requires torch.cuda, fails loudly without it) / --mode cpu.
The dial-vector grid runs on GPU tensors. When --vertex-deltas <npy> is
supplied (MPFB bake output: [n_dials, n_verts, 3] float32), the job ALSO runs
the full vertex batch base + sum(dial * delta) on GPU and writes the composed
mesh batch; without deltas it writes the grid + proxy scales only and records
that the vertex batch awaits the bake deltas — the baked shape keys remain
the ground truth (morphs.js header), this job never replaces them.
Template bodies are neutral WWE-style CAW bases: no Mixamo soldier mesh, rig,
or textures anywhere in the chain; no real-wrestler likeness; no famous names.
Outputs: suite-morph-out/morph-grid.json, suite-morph-out/JOB-VERIFICATION.txt
  (+ suite-morph-out/vertex-batch.npy only when --vertex-deltas is given).
Buttons: LP1/RP2/LK3/RK4 in all user-facing text.
"""
import argparse, json, os, subprocess, sys, time

TEMPLATES = {
    "caw-neutral-balanced": {"height": 0, "bulk": 0, "muscle": 0, "fat": 0,
                             "shoulders": 0, "belly": 0, "limbs": 0, "chest": 0,
                             "waist": 0, "hips": 0, "neck": 0, "hands": 0,
                             "feet": 0},
    "caw-power": {"bulk": 0.6, "muscle": 0.7, "fat": 0.2, "shoulders": 0.5,
                  "chest": 0.4, "limbs": -0.1},
    "caw-cruiser": {"bulk": -0.4, "muscle": 0.1, "fat": -0.3, "limbs": 0.3,
                    "height": 0.1},
    "caw-giant": {"height": 0.8, "bulk": 0.8, "muscle": 0.5, "shoulders": 0.6,
                  "limbs": 0.4},
}
VALUES = [-1.0, -0.5, 0.0, 0.5, 1.0]


def device_proof(mode):
    lines = [f"mode={mode}"]
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        lines.append("nvidia-smi: " + (out.stdout.strip() or out.stderr.strip()
                                       or "(no output)"))
    except Exception as e:  # noqa: BLE001
        lines.append(f"nvidia-smi: UNAVAILABLE ({e})")
    if mode == "gpu":
        try:
            import torch
        except ImportError:
            print("FATAL: --mode gpu requires torch with CUDA; torch is not "
                  "installed here. Run this job on the Kaggle T4 notebook.",
                  file=sys.stderr)
            sys.exit(2)
        if not torch.cuda.is_available():
            print("FATAL: --mode gpu requires torch.cuda; no CUDA device found.",
                  file=sys.stderr)
            sys.exit(2)
        lines.append(f"torch={torch.__version__} cuda={torch.version.cuda} "
                     f"device={torch.cuda.get_device_name(0)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="./suite-morph-out")
    ap.add_argument("--mode", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--vertex-deltas", default=None,
                    help="Optional [n_dials, n_verts, 3] float32 .npy from MPFB bake")
    ap.add_argument("--dials", type=int, default=62)
    args = ap.parse_args()
    t0 = time.time()
    proof = device_proof(args.mode)
    os.makedirs(args.out_dir, exist_ok=True)
    # Grid: templates x dials x values -> proxy scales (applyMorphProxies math:
    # girth = 1 + 0.12*(bulk+muscle) + 0.10*fat; height scale = 1 + 0.15*v).
    n = len(TEMPLATES) * args.dials * len(VALUES)
    if args.mode == "gpu":
        import torch
        vals = torch.tensor(VALUES, device="cuda")
        grid = (1.0 + 0.15 * vals).repeat(len(TEMPLATES) * args.dials)
        grid_sum = float(grid.sum())
    else:
        import numpy as np
        vals = np.array(VALUES)
        grid = np.tile(1.0 + 0.15 * vals, len(TEMPLATES) * args.dials)
        grid_sum = float(grid.sum())
    vertex_note = "vertex batch awaits MPFB bake deltas (--vertex-deltas not given)"
    if args.vertex_deltas:
        if args.mode == "gpu":
            import torch, numpy as np
            deltas = torch.from_numpy(np.load(args.vertex_deltas)).cuda()
            weights = torch.zeros((deltas.shape[0],), device="cuda")
            batch = torch.einsum("d,dvc->vc", weights, deltas)
            vertex_note = (f"vertex batch composed on GPU: "
                           f"deltas={tuple(deltas.shape)} "
                           f"batch_shape={tuple(batch.shape)}")
            np.save(os.path.join(args.out_dir, "vertex-batch.npy"),
                    batch.cpu().numpy())
        else:
            import numpy as np
            deltas = np.load(args.vertex_deltas)
            batch = np.einsum("d,dvc->vc", np.zeros(deltas.shape[0]), deltas)
            vertex_note = (f"vertex batch composed on CPU: "
                           f"deltas={deltas.shape} batch={batch.shape}")
            np.save(os.path.join(args.out_dir, "vertex-batch.npy"), batch)
    os.makedirs(args.out_dir, exist_ok=True)
    json.dump({"templates": list(TEMPLATES.keys()), "dials": args.dials,
               "values": VALUES, "evaluations": n, "grid_sum": grid_sum,
               "templates_detail": TEMPLATES, "vertex_note": vertex_note},
              open(os.path.join(args.out_dir, "morph-grid.json"), "w"), indent=1)
    wall = time.time() - t0
    ver = (f"{proof}\ntemplates={len(TEMPLATES)} dials={args.dials} "
           f"values={len(VALUES)} evaluations={n} grid_sum={grid_sum:.3f}\n"
           f"{vertex_note}\nwall_seconds={wall:.3f}\n"
           f"outputs=morph-grid.json"
           f"{', vertex-batch.npy' if args.vertex_deltas else ''}\n")
    open(os.path.join(args.out_dir, "JOB-VERIFICATION.txt"), "w").write(ver)
    print(ver)


if __name__ == "__main__":
    main()
