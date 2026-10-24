# STICK-UP v2 production decision log

Written 2026-10-15. Every production call made while building the universal
rig-repair pipeline, and WHY — so no future worker re-litigates them.

Measured baseline (own runs, `rigcheck/rig_check.py`, 6 standard clips):
STICKUP_repaired.glb (v1, decimated) stretch p99.9 = 27.71–44.73 vs the 2.5 gate
threshold. STICK-UP v2 rig gate: v1 = 16.6–52.9, HQ = 9.9–17.1 — both FAIL.
Residual after weight-only fixes: the 58-joint skeleton's arm bones sit ~5 cm
outside the mesh.

## Decisions

1. **Refit the skeleton in place instead of re-rigging.** No free tool refits an
   EXISTING skeleton (all auto-riggers build new skeletons, breaking clip
   compatibility with every existing animation). Implemented the
   vendor-documented "volume mode" algorithm from Voxel Heat Diffuse Skinning as
   headless Blender Python (`refit.py`): ray-cast on 3 axes per joint, shortest
   chord midpoint if inside, surface + half-thickness if outside, 0.10 m clamp.
   Inverse bind matrices recomputed on export → existing clips (local rotations)
   play unchanged. Measured: 14 joints moved (shoulders/arms/upleg 2–3 cm;
   elbows/wrists/knees/ankles 10 cm clamped, were 4–10 cm outside the mesh).

2. **Re-skin is CONDITIONAL, default `none`.** shd (meshonline, MIT) re-skin
   measured 94.74–136.18 — far worse than the 27.71–44.73 input (Hips dominated
   40% of verts, RightShoulder 25%). Blender heat re-skin: 37.21–52.31. Both
   destroyed good transfer weights. The pipeline keeps transfer weights and
   fixes them via separate+armpit. Re-skin only when weights are missing/stale.

3. **Separate promoted to a standalone stage.** `transfer --limb-separate` only
   helps when a transfer source exists. Already-weighted models (the common
   case) have mis-weighted verts with no source to transfer from, so `separate.py`
   works from the existing weights: dominant bone >0.20 m away (bind pose) →
   reassign to nearest plausible bone of the correct body region. Fixed 812
   hand verts weighted >0.5 to leg bones. Measured: 37.21–52.31 → 9.52–13.32
   (refit + separate).

4. **Armpit fix = de-bleed + sharpen + torso-side, baked into WEIGHTS.**
   De-bleed: arm weights → 0 beyond 0.14 m from arm segments. Sharpen:
   contrast p=1.6 on arm-vs-torso blends. Torso-side: torso verts must not
   carry arm weights however close the hanging forearm passes (proximity ≠
   limb). Corrective Smooth baked into weights, NOT mesh positions — it is a
   no-op at rest pose and export-time modifier state doesn't transfer to game
   engines. Corrections run AFTER smoothing so they aren't diffused away.
   Measured: 9.52–13.32 → 10.75–15.05 (slight rise is the honest sharp-boundary
   effect — decisive assignment at a genuine transition concentrates stretch).

5. **Weldcap is a HARD ASSERT, not a repair.** The 266-open-edge incident
   proved silent hole-manufacture is possible. `weldcap.py` recalculates
   normals then asserts zero open edges (welded by position, so UV seams don't
   count) and non-manifold ≤ input — and FAILS loudly on violation.
   `bmesh.remove_doubles` is banned (created 19 holes at 1e-6 on a watertight
   mesh). Blind auto-capping deferred until a model with real cut holes needs it.

6. **The 2.5 gate threshold is aspirational, kept anyway.** Remaining stretch is
   ball-joint skin under extreme rotation — inherent to LBS without corrective
   shapes. The pipeline drives the metric ~3× down (27.71–44.73 → 10.75–15.05)
   and eliminates the visible defects (wings gone, verified by eye). The gate
   stays strict so regressions are loud; models that fail it ship with the
   numbers on record, not with a lowered bar.

7. **Versioned outputs, inputs never touched.** Every stage writes
   `{tag}_{stage}.glb` + JSON report (lane artifacts: `STICKUP_refit.glb`,
   `STICKUP_sep.glb`, `STICKUP_armpit.glb`, `STICKUP_final.glb`). Owner law:
   never edit originals. Enables `--from-stage` resume and before/after proof.

8. **Python decode, no vendored node_modules.** `rigcheck` was dead on arrival
   (missing node_modules → FileNotFoundError before node ran). `ingest.py` is a
   shared pure-Python GLB reader: honors `bufferView["buffer"]`, decodes
   EXT_meshopt_compression via pip `meshopt`, raises `DracoError` for draco.
   Verified: meshopt STICKUP.glb → 12,633 verts / 54,000 indices, identical
   metrics to the plain file.

9. **The 6 standard gate clips ship as procedural fixtures.** The full gate
   could never PASS without clips, and no game clips belong in the tool repo.
   `make_clips.py` generates idle, walk, jab, kick, hit_react, knockdown —
   labeled as test fixtures, not game content.

10. **One command + batch with crash isolation.** The owner's order is that
    EVERY model in EVERY game runs through this, automatically. `pipeline.py`
    is one command per model; batch via `xargs -P 4`; one Blender process per
    model per stage so a crash kills one stage, not the batch.

## Bugs found and fixed (permanent lessons)

- **Chained numpy assignment is a silent no-op:** `Dw[mask][:, cols] = 0`
  modifies a copy. All armpit corrections were discarded until fixed with
  `Dw[np.ix_(mask, cols)] = 0`. Cost a full iteration.
- **Accessor byteOffset slicing + stale indices/IBM refs** in GLB rebuild
  (separate.py) — fixed with full accessor remap.
- **`transfer` de-hardcoded:** was STICK-UP-specific (hardcoded `STICKUP_HQ`
  mesh name, hard-crash on non-Mixamo, single-primitive silent data loss,
  dropped extensions, `--retarget` default mismatch). Now: mesh name from
  target, synonym-table joint matching, loud skip on non-Mixamo, multi-primitive,
  extensions preserved.
- **Bone parents must be restored** after `use_connect` moves (Blender), or the
  export writes a broken hierarchy. `arm.data.bones` head/tail are NOT populated
  by the glTF importer — use edit bones. Blender Z-up vs glTF Y-up on all
  pose/ray targets.
