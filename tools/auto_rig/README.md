# tools/auto_rig — unified auto-rig system for Western Heart

Production-grade auto-rigging, built from real 2026 research
(see `docs/AUTO-RIG-DEEP-RESEARCH-2026.md`). One CLI, six backends, one gate.

## Quick start

```bash
# CPU baseline (no GPU needed) — the PR #264-proven path
python3 tools/auto_rig/auto_rig.py --in MODEL.glb --out RIGGED.glb \
    --backend blender-heat

# dense Tripo static: k-NN weight transfer from a donor rig
python3 tools/auto_rig/auto_rig.py --in STATIC.glb --out RIGGED.glb \
    --backend knn --donor game/assets/models/pantera.glb

# GameRig: fresh game-ready skeleton generated per-mesh (Rigify-based),
# with a CMU mocap clip baked in as animation proof
python3 tools/auto_rig/auto_rig.py \
    --in roster/baek/attires/master-white/baek-master-white.glb \
    --out baek_gamerig.glb --backend gamerig \
    --donor assets/free-pull-1/cmu-mocap/fighting/135_04.bvh \
    --clip CMU135_04_boxing --clip-start 240 --clip-frames 72 --clip-step 4

# GPU: AI skeleton prediction (Kaggle/Colab)
python3 tools/auto_rig/kaggle/auto_rig_gpu.py --backend magicarticulate \
    --in MODEL.glb --outdir out/
```

Every run ends at `validate.py` — the playable gate (valid glTF, skinned
mesh, Mixamo-style bones, 1.5–2.2 m, stretch < 2.5). Nothing ships that
doesn't pass.

## Backends

| Backend | Needs | What it does |
|---|---|---|
| `blender-heat` | Blender 4.0.2 (local) | normalize → fixed WH skeleton → heat-diffusion weights. Deterministic. For T-pose/A-pose humanoids. |
| `gamerig` | Blender 4.0.2 (local) | GameRig (vendored Rigify feature set) generates a fresh single-hierarchy deform skeleton fitted to the mesh → bone-heat skinning → optional donor clip baked (GLB clips or CMU BVH). Skeleton fits the mesh. See `examples/gamerig-baek/` and `tools/open-source/gamerig/USAGE.md`. |
| `knn` | numpy/scipy | k-NN weight transfer from a donor rig. For dense statics Blender chokes on. |
| `magicarticulate` | CUDA 4.6GB+ | AI skeleton prediction (Apache-2.0, vendored). 1–2 s/mesh. |
| `unirig` | CUDA 8GB+ | AI skeleton + skinning (MIT, vendored). |
| `puppeteer` | CUDA 8GB+ | AI rig + video-guided animation (Apache-2.0, vendored). |

## Layout

```
tools/auto_rig/
  auto_rig.py            unified CLI
  validate.py            playable gate
  backends/
    normalize.py         pure-Python GLB normalize (bake transforms, feet y=0, scale)
    blender_heat.py      Blender: build WH skeleton + heat weights + export
    gamerig_backend.py   Blender: GameRig generate + fit + skin + clip bake + export
    skeleton_template.json  52-bone WH Mixamo-style template (Y-up, faces -Z)
    knn_transfer.py      k-NN weight transfer from donor rig
    ai_rig.py            GPU adapter: run vendor AI, canonicalize joint names
    retarget.py          bone-name canonicalization + gate bone list
  vendor/
    unirig/              MIT — skeleton + skinning prediction
    magicarticulate/     Apache-2.0 — fastest skeleton predictor
    puppeteer/           Apache-2.0 — rig + video-guided animation
  checkpoints/README.md  weight download commands (never vendored)
  kaggle/auto_rig_gpu.py GPU runner for Kaggle/Colab
  tests/                 unit tests
```

## Vendoring policy

Code + configs + READMEs + LICENSEs are vendored with a `VENDOR.md` each
(upstream URL, license, what was excluded). Excluded: demo meshes, doc
images/videos, `.git`. Checkpoints are never vendored — they download on
the GPU box.

NOT pulled (documented in the research doc): RigNet (GPLv3 — copyleft),
Auto-Rig Pro (commercial), Pinocchio original (superseded — Blender's bone
heat is the same heat-diffusion math, maintained).

## Design decisions (from the #264 post-mortem)

- **Mesh fits the skeleton, never the reverse.** The WH skeleton is fixed;
  meshes normalize to it. Skeleton-fitting is the hard problem — that's what
  the AI backends are for. (rig_repair's refit.py did the reverse and
  detached arms.)
- **Canonicalization over geometric retarget** for foreign skeletons
  (preserves native structure; geometric retarget is the fallback).
- **Every vertex gets a weight.** Bone heat leaves disconnected islands
  unweighted; unweighted verts crash the glTF exporter. The backend assigns
  them to the nearest bone.
- **Inputs are never modified.** Every stage writes a new file.
