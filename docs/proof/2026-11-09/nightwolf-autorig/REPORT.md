# Nightwolf — learned auto-rig stack proof (UniRig), 2026-11-09

Owner order 2026-11-09 09:17 CST: replace the house rig+weights approach
with the top industry-standard auto-rig stack, run unmodified, zero hand
edits. Nightwolf is the proof case; she is rigged from her clean Tripo
statue (single fused mesh, 1,092,247 verts, no skeleton, no weights).
The PR #1692 landed file (`roster/nightwolf/attires/attire1/model-rigged.glb`)
is **not** replaced by this PR — the swap waits for own-eyes comparison
once the skin stage lands.

## What ran, where

| Stage | Where | Result |
|---|---|---|
| Skeleton prediction (UniRig, upstream unmodified) | Kaggle T4, kernel `marsfmmg/nw-unirig-run` v15, 2026-11-08 | **COMPLETE** — 52-joint skeleton FBX (1,589,052 B) from her clean statue |
| Skin weights + merge (UniRig) | Kaggle T4, driver v17 ready | **BLOCKED — quota** (below) |
| Skin weights, local CPU attempt | this VM, full env stood up 2026-11-09 | **BLOCKED — spconv requires CUDA** (below) |

Drivers: `tools/auto_rig/kaggle/unirig_run1_skeleton.py`,
`unirig_run2_skin.py`; stack doc: `tools/auto_rig/kaggle/UNIRIG-STACK.md`.
Upstream diff of the executed tree vs upstream HEAD: exactly two files,
both dependency shims (bpy/libtbb isolation; pristine extract on the bpy
path) — no model, joint, or weight code touched, ever.

## Skeleton metrics vs the PR #1692 rerig

Measured from the UniRig skeleton export against her mesh (fit space:
mesh height 2.0; ×0.835 for her 1.67 m game scale). Full data:
`skeleton-metrics.json` beside this report.

| Metric | PR #1692 rerig (landed) | UniRig skeleton (unmodified run) |
|---|---|---|
| Skeleton source | house template (58 joints), landmark fit **+ disclosed hand patch** of the fit (RightArm mirrored from LeftArm) | learned prediction, 52 joints, **zero hand edits** |
| Shoulders | template-placed | symmetric on her arm line: \|x\| 0.2305 R / 0.2227 L, Δz ≈ 0 (the original house fit collapsed RightArm to the sternum, x ≈ −0.001) |
| Forearm axis deviation from her arm geometry | height offsets 0.6 cm L / 0.4 cm R **after** the hand patch (original fit: 21.5 / 21.6 cm) | axis perp deviation **3.6 mm R / 3.8 mm L**, axis dz +0.7 / +1.3 mm — same class or better, before skinning, unpatched |
| Upper-arm axis deviation | segment median dist 0.050–0.083 m (post-patch) | 6.2 mm R / 8.1 mm L |
| Head joint | template | inside her head-region bounds (216,857 verts above the neck joint, fused headdress included) |

Skin-stage acceptance metrics (face-slab % to Head, dominant-vertex
counts, stretch under stance) are defined by the rerig report and are
computed by `tools/auto_rig/kaggle/probe_acceptance.py` the moment the
merged GLB exists; they cannot be reported before the skin run exists,
and no substitute numbers are offered.

## The two blockers, measured

1. **Kaggle weekly GPU quota exhausted.** `Maximum weekly GPU quota of
   30.00 hours reached` on every push since 2026-11-08 16:47 CST
   (watcher tries 5–8 on 2026-11-09, 09:26–09:57 CST, same message).
   Auth is healthy (OAuth; kernels list fine) — this is quota only,
   shared across lanes. The watcher re-pushes run2 automatically when
   it frees; run2's driver had already cleared every in-kernel failure
   (bpy pin, TBB clash, torch_cluster/scatter, spconv/cumm, flash-attn
   import, checkpoint load) before the quota shut.
2. **Local CPU skin run blocked at spconv.** Full CPU env stood up
   (torch 2.9.0+cpu, deps, PyG wheels, spconv-cu126 — all import,
   including `SPCONV IMPORT OK`), but spconv's implicit-GEMM path calls
   `torch.cuda.current_stream()` unconditionally
   (`spconv/pytorch/ops.py` → `cppcore.get_current_stream()`), raising
   `AssertionError: Torch not compiled with CUDA enabled` on CPU
   tensors; a null-stream shim hits the same assertion deeper. PTv3
   (both stages' backbone) routes through that path, so the learned
   stages require a CUDA environment as shipped. Patching spconv's op
   dispatch would be rewriting the library — out of bounds for this
   stack. Details: UNIRIG-STACK.md, "Local CPU stand-up".

## Survey headline (full survey beside this report)

SkinTokens/TokenRig (VAST, TOG 2026, MIT) is UniRig's successor and the
survey's rank #1 — the next wire-up on the same Kaggle route (T4's
16 GB meets its ≥14 GB VRAM floor). UniRig stays the proven wired
stack and cross-check. Everything NC/GPL/GUI-bound is reference-only;
the list and licence evidence are in `research-survey-20261109.md`.

## When the quota frees (no further decisions needed)

watcher push → run2 completes → `nightwolf_rigged.glb` downloads →
assemble (canonical names via `tools/auto_rig/backends/retarget.py`,
uniform 1.67 m normalization) → `probe_acceptance.py` metrics →
bind/Julia/King frames in the standard harness → follow-up PR with the
skinned proof set + the swap candidate. The roster file is only
replaced after own-eyes comparison against PR #1692.
