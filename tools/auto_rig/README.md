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

## Animation validation (anim_check.py)

`validate.py` gates the MODEL; `anim_check.py` gates the ANIMATION.
Headless (pure python + numpy, no Blender) retarget validator: bone-length
variance, rest deviation, vertex tearing spikes, p99.9 edge stretch,
root-offset drift, and wrong-node channel detection — the failure modes
behind the 2026-10-19 tearing incidents. Full method + findings:
`docs/RETARGET-MOVEDECODE-RESEARCH-2026.md`.

```bash
python3 tools/auto_rig/anim_check.py --in MODEL.glb [--anim NAME]
# or fold into the playable gate (implements validate.py check #5):
python3 tools/auto_rig/validate.py --in MODEL.glb --clips CLIPS_DIR
```

Tests: `tools/auto_rig/tests/test_anim_check.py` (synthetic GLB fixtures,
one per failure mode).

## Skin audit + automatic weight repair (rigfix.py, 2026-10-29)

Stretch gates alone shipped deformed models before (Leopard King
#448: passed p99.9 stretch, legs folded to spine — rest-rotation and
weight-domain defects no stretch number can see). The repair lane
measures and fixes the weight domain directly:

    # one command: audit -> cleanup -> re-audit -> playable gate
    python3 rigfix.py --in MODEL.glb --out MODEL_rigfixed.glb \
        --report REPORT.json        # exit 0 only on a full pass

- `backends/skin_audit.py` — the measuring instrument. Weight sums,
  unweighted verts, JOINTS_1 overflow, **dead major joints** (a body
  joint carrying zero weight), **cross-body contamination** (weight
  on a joint whose bone segment is far from the vertex vs its nearest
  segment — bind-space, computed from inverse bind matrices),
  skeleton proportions vs `backends/skeleton_template.json`, folded
  rest chains, joints outside the mesh volume, feet planted.
- `backends/weight_cleanup.py` — the fix: prune contaminated slots,
  **revive globally dead major joints** by proximity reassignment to
  their anatomical territory (a dead Hand's finger-dominated verts get
  real Hand weight again), fill unweighted verts, edge-Laplacian
  smoothing with duplicate-safe accumulation, a post-smoothing
  far-prune, prune-to-4 + exact renormalization. Input never modified.
- `backends/surface_heat.py` + `vendor/surface-heat-diffuse/` — full
  re-skin by surface heat diffusion (MIT, meshonline; helper built
  from vendored C++ with g++, driven headlessly through the add-on's
  own write/run/read pipeline). Use when weights must be recomputed
  wholesale; falls back to `blender_heat.py` when unavailable.
- `proof_pose.py` — Blender posed proof renders (named bones at fixed
  angles) so a revival can be checked by eye, not just by numbers.
- `tests/test_skin_fixes.py` — synthetic GLB with a planted dead joint
  + planted contamination; audit must flag both, cleanup must fix both.

Proof on the in-game Baek model (`game/assets/models/baek.glb`,
2026-10-29): audit BEFORE failed with dead `LeftHand`/`RightHand`
(the model's hand verts were 100% finger-weighted) and 0.087%
contaminated weight mass; cleanup pruned 128 contaminated slots,
revived 707 verts, filled 7 unweighted; audit AFTER passes all 10
checks (contamination 0.003%). Rest and posed renders before/after
are unchanged in envelope — no new tearing; two pre-existing defects
were noted, not hidden: a wrist seam gap under hard bends and a stray
flat bar prim at belt height, both present in the shipped original.

## Landmark re-fit pipeline (`refit_rig.py`, 2026-11-01 — Negativo)

For a T-pose model whose skeleton lands in the wrong place (hair / hats / horns make the mesh taller than the
body, so a height-scaled template puts the chest bones in the face, the arms above the arms, the hip joints in
the belly — the owner's "cone face", "arms crushed like a steamroller", "head and neck weighted toward the
pelvis"):

```bash
export WH_BLENDER=/path/to/blender-4.0.2-linux-x64/blender NODE_PATH=/path/to/node_modules
python3 tools/auto_rig/refit_rig.py --in roster/X/attires/attire1/source/x-a1.glb \
    --out roster/X/attires/attire1/source/x-a1-rigged.glb \
    --report-dir docs/proof/<date>/refit-X --facing +X --height 2.0
```

| Step | Tool | What it does |
|---|---|---|
| 1 | `refit_skeleton.py` | template joints (pantera.glb, King's 49) fitted inside the mesh + static bind copy |
| 2 | `refit_landmarks.py` | arms from clean arm slices (armpit, thinnest wrist), hips/knees from the crotch, neck base + chin from the mid-line front profile, spine centred between front and back surfaces; mirror-completes one-sided chains |
| 3 | `backends/heat_rebind.py` | Blender bone heat via voxel proxy; `--height` (the game renders a GLB at its own size: match the model you replace); `--donor` bakes the CMU 135_04 boxing gate clip |
| 4 | `head_territory.py` | head + every hair spike on the Head bone by mesh connectivity (no height cut), faded in by geodesic distance from where hair touches the shoulders; neck cylinder blends Neck -> Head |
| 5 | `backends/seam_safe_smooth.py` | stretch-masked Laplacian on WELDED vertices + continuous 4-bone limit, until strict p99.9 <= 2.5 |
| 6 | gates | `validate.py`, `anim_check.py` (official), `rig_inspect.py seams / stretch / shares` (+ fit / sections / weights PNGs) -> `rig_report.json` |

Lessons that apply to EVERY rig (all measured on Negativo):
- **Hard 4-bone truncation tears dense meshes.** Neighbours whose 4th/5th bones swap rank keep different bones
  (RightUpLeg 0.05 vs Spine2 0.04 on 0.5 mm apart) -> 7-9 mm tears on every kick. Limit continuously: subtract
  the 5th-largest weight from the top 4 (`seam_safe_smooth.top4`, `smooth_weights.limit4`).
- **UV-seam copies must carry identical weights.** `smooth_weights.py` used to update one copy only (6,688
  drifted copies, up to 0.546) -> the seam cracks open in motion and no edge metric sees it. Fixed
  2026-11-01; check any rig with `rig_inspect.py seams`.
- **A hard "head territory" tears hair that rests on the shoulders** (2,157 edges > 20 mm, up to 127 mm). Fade
  it in geodesically.
- **Stretch ratios on 1 mm edges measure noise.** `anim_check.py` keeps only edges >= 0.5% of the height (it
  read 1.42 when every-edge p99.9 was 4.73); `smooth_weights` / `seam_safe_smooth` keep edges >= half the
  median. Read `rig_inspect.py stretch`: it also gives the elongation in mm.
- **`anim_check` tearing spikes on the boxing clip are mostly the feet** (the clip swings them with the root
  pinned; every rig in docs/proof shows 30-80). The spike report now names the moving vertex's own joints
  (it used to print skin joints 0-3, i.e. "Hips, Spine", for every vertex).

Diagnostics for any fighter: `python3 tools/auto_rig/rig_inspect.py {fit,sections,weights,shares,seams,stretch} ...`
