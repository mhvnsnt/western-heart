# Rig/Skin Auto-Fix Pipeline — handoff (2026-10-29)

Owner order (2026-10-29): "Use any modern community stuff, any reverse
engineered industry standard stuff or software, anything that will fix
all of the rigging and skinning and skin weight problems… pull it in
and wire it up so it'll automatically fix the game… make sure it lands
and get it fixing the game and working on it automatically."

This revives checkpoint `rig-pipeline-universal` (needs_owner since
2026-10-15). Its 2026-10-15 PRs (#164/#165/#166/#168, docs #173) were
verified MERGED before this work started; the pipeline they landed
(auto_rig.py, refit, gates) is the base this lane extends — nothing
was redone.

## Research (verified on GitHub, 2026-10-29)

| Tool | Source | License | Status here |
|---|---|---|---|
| UniRig | VAST-AI-Research/UniRig (~1.9k★) | MIT | already vendored; skeleton prediction only — its skinning-weight model is still "coming soon" upstream |
| Puppeteer | Seed3D/Puppeteer (NeurIPS 2025) | Apache-2.0 | already vendored; GPU inference |
| MagicArticulate | Articulation-XL2.0 (CVPR 2025) | Apache-2.0 | already vendored; GPU inference |
| Surface Heat Diffuse Skinning | meshonline/Surface-Heat-Diffuse-Skinning @578fed6 | MIT | **vendored this lane** (`tools/auto_rig/vendor/surface-heat-diffuse/`) + headless backend `backends/surface_heat.py`; helper builds with g++ and runs (proof below) |
| Bounded biharmonic weights (libigl) | libigl | MPL-2.0 | documented reference only — needs tetrahedralization, fragile on game meshes; not vendored |
| Blender built-in bone heat | Blender | GPL (app) | already wired as `backends/blender_heat.py`; same heat family, weaker on close surfaces — the fallback |
| Pinocchio | MIT (research) | MIT | not pulled: superseded for this roster — heat methods handle the WH template skeleton directly |

## What was built (all under `tools/auto_rig/`)

1. **`backends/skin_audit.py`** — bind-space skin/skeleton audit
   (10 checks; see README). Key design point: all distances are
   computed against inverse-bind-matrix joint positions, the same
   space as the raw vertices. Node-graph world positions falsely flag
   healthy rigs; an earlier calibration of this audit flagged a good
   gamerig example at ~1 m error before the IBM fix.
2. **`backends/weight_cleanup.py`** — automatic weight repair
   (contamination prune → global dead-major revival by anatomical
   territory → unweighted fill → duplicate-safe Laplacian smoothing →
   post-smoothing far-prune → prune-to-4 + renormalize).
   Two real bugs were found and fixed against the synthetic fixture
   during this build: per-prim deadness spraying (dead must be
   GLOBAL), and `np.put_along_axis` silently zeroing weights on rows
   that repeat a joint across slots (padding) — accumulation is used
   instead.
3. **`rigfix.py`** — the one-command orchestrator:
   audit → cleanup → re-audit → validate.py gate, JSON report,
   exit 0 only on full pass.
4. **`backends/surface_heat.py`** + vendored add-on — wholesale
   re-skin by surface heat diffusion, driven headlessly (the upstream
   operator is modal/UI-only; the backend drives its own
   write-data → helper → read-weights pipeline synchronously).
5. **`proof_pose.py`** — posed proof renders for dead-joint checks.
6. **`tests/test_skin_fixes.py`** — synthetic regression fixture
   (planted dead joint + planted contamination). Existing suite still
   green: anim_check 7/7, retarget 3/3, gamerig_rename pass
   (test_normalize skips without its Blender fixture — pre-existing).

## Proof — test fighter: Baek (`game/assets/models/baek.glb`)

Chosen because it is the in-game model, is owned by no active rig
lane (charfix-batch3 is paused; Pantera/Deathfang/Rig & Pose Studio
belong to another chat and were not touched), and had a measured
failure: the audit found both Hand joints dead.

- BEFORE: audit FAIL — dead majors `LeftHand`, `RightHand`;
  contaminated weight mass 0.087% (33 verts); validate.py also fails
  `fingers_symmetric` on the original (pre-existing).
- Cleanup: 128 contaminated slots pruned, 707 verts revived onto the
  Hand joints, 7 unweighted verts filled.
- AFTER: **audit PASS, all 10 checks** (contamination 0.003%, sums
  exact, proportions/feet/folds unchanged); validate hard checks
  pass; `rigfix.py` exit 0. `fingers_symmetric` still fails exactly
  as on the original — not a regression, not claimed fixed.
- Surface-heat backend proof: re-skinned the gamerig Baek example
  end-to-end (`SURFACE_HEAT_DONE`); output passes sums/unweighted/
  JOINTS_1 audit checks (some minor joints land ~zero under heat —
  that is what the cleanup revival stage is for; the stages compose).
- Renders (viewed by the author): rest front/back/side and posed
  (forearm ±55°, hand ±65°) before vs after — envelope unchanged, no
  new tearing or detachment from the cleanup. Honest limits: the
  dead-Hand revival is proven by the audit numbers; at render
  resolution the wrist motion difference is not separately visible.
  Two pre-existing defects in the shipped Baek model were seen and
  are NOT fixed by this lane: a wrist seam gap under hard bends
  (separate part prims) and a stray flat black bar prim at belt
  height. Both are in the original file.

## What remains for a full-roster run

1. Batch driver: run `rigfix.py` over `game/assets/models/*.glb`
   (audit-only first to triage; ~30 roster models), one PR per
   character (per-character isolation), each with its own
   before/after audit JSON + proof renders.
2. Skeleton-level failures (proportion/folded flags) route to
   `refit_skeleton.py`/`auto_rig.py` re-rigs, not weight cleanup —
   the audit report says which.
3. Seam-weld stage for multi-part exports (the Baek wrist gap class)
   — not built here; needs a merge-by-distance + boundary weight
   blend tool.
4. Wire `rigfix.py --skip-cleanup` audit into intake so every new
   model lands with an audit report next to it.
