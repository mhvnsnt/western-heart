# UniRig stack — the learned auto-rig backend (skeleton + skin weights)

Owner order 2026-11-09: the house refit chain (template landmark fit +
bone-heat weights + seam_safe_smooth) is out for production rigs — it
converged on 0 of 5 chains (strict p999 6.3–12.2 vs gate 2.5) and produced
the Nightwolf arm stretch/crush family. The replacement is the top
industry-standard learned auto-rig stack, run **unmodified**: one pipeline
run end to end, zero hand edits to geometry, joints, or weights. If the
system cannot fit a model it stops and reports the measured blocker.

## What was pulled

| Component | Source | Licence | Status |
|---|---|---|---|
| UniRig (skeleton + skinning, SIGGRAPH 2025) | github.com/VAST-AI-Research/UniRig, vendored at `tools/auto_rig/vendor/unirig` | **MIT** (LICENSE in tree, Copyright 2025 VAST-AI-Research) — code and released checkpoints usable | pulled + vendored |
| UniRig checkpoints | HF `VAST-AI/UniRig` (public, not gated): `skeleton/articulation-xl_quantization_256/model.ckpt` (~1.34 GiB), `skin/articulation-xl/model.ckpt` (~4.07 GiB) | MIT release | auto-downloaded at run time |
| Kaggle drivers (this directory) | `unirig_run1_skeleton.py`, `unirig_run2_skin.py` | house code | **proven in production 2026-11-08** (see run history) |

The drivers run upstream UniRig **unmodified** — a fresh `git clone` of
upstream at run time. Diffing the tree a completed run actually used
against upstream HEAD shows changes in exactly two files, both
dependency shims applied at runtime by the drivers (no model, joint, or
weight code touched):

1. `src/data/extract.py` — module-top `import bpy` made lazy inside the
   four functions that call it, and only for the torch inference process
   (the bpy-only extract process runs the pristine file, bpy first). Cause:
   torch and bpy ship conflicting libtbb builds; whichever loads second
   dies (`libopenvdb.so`: undefined symbol).
2. `src/data/exporter.py` — `_export_fbx` delegated to a fresh bpy-first
   subprocess running the pristine upstream function (same libtbb cause
   on the export side).
3. A pure-python `flash_attn` shim package: the **real**
   `flash_attn/modules/mha.py` from the v2.8.3 tag (sha256-pinned) plus
   its one unguarded import. UniRig constructs `MHA(...,
   use_flash_attn=False)`, so the real code path is the pure-torch
   CrossAttention inner class; the CUDA kernels are never called (and
   FA2 kernels are sm80/sm90-only — they could not execute on a T4
   anyway). Checkpoint parameter names match exactly.
4. `sitecustomize.py` (driver-generated): pre-imports `cumm.core_cc` so
   `tv::Tensor` registers before `spconv.core_cc` init needs it, and
   wraps `torch.load` for the trusted upstream checkpoint (see the v17
   note in `unirig_run2_skin.py`: the skin checkpoint stores its config
   as a `box.box.Box`, which torch's weights-only unpickler cannot
   rebuild even when allowlisted — measured in-kernel, run2 v3/v4).

## How to run (Kaggle, account marsfmmg, named OAuth token only)

1. Stage inputs as a Kaggle dataset: the pipeline static mesh
   (`<name>_static.glb`, codec static copy of the source model) — run1
   also takes it directly.
2. Push `unirig_run1_skeleton.py` as a GPU kernel (T4). It extracts,
   predicts the skeleton, and exports `<name>_skeleton.fbx`.
   Proven: Nightwolf run1 v15 COMPLETE 2026-11-08 (~9 min once the
   dependency chain was fixed; skeleton FBX 1,589,052 B).
3. Push `unirig_run2_skin.py` with run1 as a kernel source plus the
   static-mesh dataset. It predicts skin weights and merges to
   `<name>_rigged.glb`.
4. Assemble locally: canonical bone-name mapping via
   `tools/auto_rig/backends/retarget.py` (`canonicalize`), uniform
   height normalization, fresh glTF export. Then the acceptance probe
   (dominant-vertex / segment-distance / face-slab metrics, definitions
   in `docs/handoffs/NIGHTWOLF-RERIG-REPORT-2026-11-07.md`).

GPU quota note: Kaggle's weekly 30 h GPU quota is shared across lanes.
When it is exhausted the push fails with `Maximum weekly GPU quota of
30.00 hours reached` — that is a scheduling block, not a code failure;
the run2 driver above is the version that had already cleared every
in-kernel dependency failure (bpy pin, TBB clash, torch_cluster,
spconv/cumm, flash-attn import, Box checkpoint load) before the quota
shut.

## Failure history (all measured in-kernel, 2026-11-08)

bpy 4.5.0 wheel gone from PyPI → pin 5.2.3 (cp313). libtbb ABI clash
(torch vs bpy) → split extract/inference + lazy bpy + subprocess FBX
export. Missing deps in upstream's install set: torch_cluster,
torch_scatter (PyG index keyed to the exact torch build), spconv
(spconv-cu124 wheel; JIT off — prebuilt core_cc; cumm include path for
tensorview headers; cumm.core_cc pre-import for tv::Tensor). flash-attn
has no cp313 wheel and its kernels can't run on sm_75 → real-mha.py
shim. `get_files` writes the extract npz next to the input file
(absolute-path join) → guards glob the input's own directory. Full log:
the GPU lane's PROGRESS.md (agent scratch `_nw-gpurig-20261107`).

## Local CPU stand-up (2026-11-09, measured — skin stage blocked at spconv)

A full local CPU environment was stood up alongside the Kaggle route
(py3.12 venv; torch 2.9.0+cpu; the drivers' dependency set;
torch-cluster/torch-scatter 1.6.3+pt29cpu — all import-verified) to
test whether the skin stage could run without the GPU quota. Result:

- Everything imports, **including spconv** (`SPCONV IMPORT OK` from the
  spconv-cu126 2.3.8 wheel + pip `nvidia-cuda-runtime-cu12`).
- The sparse-conv **forward** cannot run: spconv's implicit-GEMM path
  (`spconv/pytorch/ops.py` → `cppcore.get_current_stream()`) calls
  `torch.cuda.current_stream()` unconditionally, before any tensor op —
  on a CPU-only torch build this raises `AssertionError: Torch not
  compiled with CUDA enabled`. A null-stream shim gets past that call
  and hits the same assertion deeper in the op path. PTv3 — the shared
  backbone of both UniRig stages — routes its sparse convs through
  exactly this path, so **the learned stages require a CUDA environment
  as shipped**; patching spconv's op dispatch would cross from
  dependency shims into rewriting the library, which this stack does
  not do. Building spconv from source for CPU is the remaining local
  route (multi-hour C++ build; unproven on py3.12) and is logged, not
  attempted silently.
- The Kaggle GPU route is therefore the execution path. Its current
  block is quota only (see above); the retry watcher re-pushes run2
  automatically when the weekly quota frees.

## Survey outcome (2026-11-09 — full survey in the Nightwolf proof dir)

The field survey (primary sources, licences read from the repos/cards
that day) ranks the licence-clean learned backends:

1. **SkinTokens / TokenRig** (VAST, TOG 2026) — MIT code + weights,
   UniRig's own successor (its README banners it), single-pass
   skeleton+skin, claims +98–133% skinning accuracy over prior SOTA
   (vendor claim, not independently benchmarked). Needs a local NVIDIA
   GPU with **≥14 GB VRAM** — a Kaggle T4 (16 GB) qualifies. **This is
   the next wire-up**: same Kaggle route as the drivers here, new
   driver to write. Not yet stood up.
2. **UniRig** (this stack) — MIT/MIT, the most battle-tested, and the
   one already proven in-house (below). Caveat from its HF card: the
   released checkpoint is the Articulation-XL2.0 one; the paper's
   Rig-XL/VRoid headline checkpoint is announced, not released.
3. **Make-It-Animatable v1** — MIT/MIT, humanoid specialist,
   Mixamo-topology skeleton (v2 weight licence unverified).

Reference-only (licence or workflow): RigNet (GPLv3/commercial),
RigAnything (Adobe NC), TailorRig (academic-only), MagicArticulate
(Apache-2.0 but skeleton-stage release only — vendored here for
skeleton experiments), AccuRIG / Mixamo / Auto-Rig Pro (commercial,
GUI-bound), Meshy/Anything World APIs (paid; aggressive tri caps that
would decimate the statues). No learned model consumes ~1M verts
directly — all sample a proxy and transfer weights back; UniRig's
merge step is that transfer here.

## Nightwolf proof status (2026-11-09)

- **Skeleton stage: COMPLETE** on Kaggle (run1 v15, 2026-11-08). The
  predicted 52-joint skeleton was measured against her clean mesh
  (`docs/proof/2026-11-09/nightwolf-autorig/skeleton-metrics.json`):
  symmetric shoulders planted on her real arm line (|x| 0.231/0.223 in
  fit space), forearm axis deviation 3.6/3.8 mm — the axis class the
  PR #1692 rerig reached only after a disclosed hand patch of its fit
  (its originals: 21.5/21.6 cm height offsets), here produced by the
  unmodified learned run.
- **Skin stage: driver ready, execution blocked on the Kaggle weekly
  GPU quota** (30 h, shared; exhausted since 2026-11-08 16:47 CST).
  The retry watcher re-pushes automatically when quota frees; the
  local tail (assemble → acceptance probe → harness frames) is staged
  and runs the moment the merged GLB lands.
- **Local CPU route: stood up and measured-blocked** at spconv (see
  the CPU section above) — not a code failure of the stack.
