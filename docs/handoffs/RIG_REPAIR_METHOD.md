# Rig-Repair Pipeline: full method

Written 2026-10-15. Owner order: a PERMANENT automatic pipeline that fixes every
character rig defect and runs every model in every game (Bannon, AshLane, Brutal
Fist, Western Heart) through it so these bugs never recur. Lives in western-heart
`tools/rig_repair/` (PRs #164–#168), ported from Bannon PR #77's tools per Grok's
documented next step.

## The defect class

Skin weights disagreeing with the skeleton:
- **Wings**: torso skin weighted to arm bones (flies with the arm in crucifix).
- **Glued hands**: limb verts weighted to the wrong body region (812 hand verts
  weighted >0.5 to leg bones on the test model; 2,675 verts >25 cm from their
  dominant bone).
- **Skeleton outside the mesh**: arm bones sitting ~5 cm outside the skin
  (Stick-Up v2 58-joint skeleton). The residual after weight-only fixes.
- **Holes / floating chunks / ghost hands**: open edges, islands, unweighted verts.
- **Mirrored skin**: Left*/Right* bones swapped (Pantera case: 5,805
  side-weighted verts on the opposite-side bone → 0 after fix).

## The 9 stages

`python3 tools/rig_repair/pipeline.py --in MODEL.glb --outdir out --tag <name>`
(batch: `xargs -P 4`). Every stage writes a VERSIONED file (`{tag}_{stage}.glb`) +
JSON report. Inputs are NEVER touched. `--from-stage` resume, `--skip-proof`.

| # | Stage | Tool | What it does |
|---|-------|------|--------------|
| 1 | detect | `rig_repair.py detect` | Multi-mesh/primitive scan; meshopt + multi-buffer decode (pure Python, no vendored node_modules). Reports skin, influences, holes, non-manifold. ~1.5 s. |
| 2 | transfer | `rig_repair.py transfer --limb-separate` | Weight transfer from a canonical skeleton. De-hardcoded: mesh name from target, tolerant joint matching via synonym tables, loud skip (not crash) on non-Mixamo, multi-primitive, preserves extensions. |
| 3 | refit | `refit.py` (headless Blender) | **The core new step.** No free tool refits an EXISTING skeleton in place (all auto-riggers build new skeletons, breaking clip compatibility). Implements the vendor-documented "volume mode" algorithm from Voxel Heat Diffuse Skinning: per arm/leg joint, ray-cast through the mesh on 3 axes; inside (ray-parity vote) → shortest chord midpoint; outside → nearest surface + half inward thickness. Clamp 0.10 m; outliers to JSON. Inverse bind matrices recomputed on export so existing clips (local rotations) play unchanged. One Blender process per model (crash isolation); `env -u PYTHONPATH`. |
| 4 | reskin | `reskin.py` / `reskin_heat.py` (Blender) | **CONDITIONAL, default `none`.** Surface-Heat-Diffuse-Skinning (MIT, meshonline) or Blender bone heat. Measured on the test model: shd re-skin was WORSE than transfer weights (Hips 40% dominance; stretch 94.74–136.18 vs 27.71–44.73 input). Re-skin only when weights are missing or stale. |
| 5 | separate | `separate.py` (numpy) | Standalone limb/body separation (no transfer source needed): dominant bone >0.20 m away (bind pose) → reassign to nearest plausible bone of the correct body region via joint synonym tables. Full accessor remap on GLB rebuild. |
| 6 | armpit | `armpit.py` (numpy) | De-bleed (arm weights → 0 beyond 0.14 m from arm segments), contrast sharpen p=1.6, torso-side correction (torso verts must not carry arm weights even when the hanging forearm passes close; nearest bind-pose segment is the discriminator). Corrective Smooth baked into WEIGHTS, not mesh positions (export-time modifiers don't transfer to engines). |
| 7 | weldcap | `weldcap.py` (Blender + numpy) | Recalc normals + HARD ASSERT on the exported file: `boundary_edges_holes == 0` (welded by position so UV seams don't count), non-manifold ≤ input count. FAILS loudly. |
| 8 | gate | `rigcheck/rig_check.py` | Static checks (skin, skeleton names, rest pose, scale 1.3–2.3 m, weights normalized, ≤4 influences, bind==rest) + 6 standard clips (idle, walk, jab, kick, hit_react, knockdown — procedural fixtures in `clips/standard/`, not game content): NaN, p99.9 edge stretch ≤ 2.5, ground contact, hinge flips. Exit 0 = PASS, 1 = FAIL. |
| 9 | proof | `proof.py` (Blender) | Stress-pose renders (arms raised, crucifix, finger guns, walk, rest) with clay material override. Media proof standard: open every render yourself; SHA-256 in the manifest. |

## Measured results (Stick-Up v1, decimated — own runs)

| Stage | stretch p99.9 (6 clips) |
|---|---|
| Input (STICKUP_repaired.glb) | 27.71 – 44.73 |
| refit alone | 37.21 – 52.31 (joints moved, weights still wrong — worse) |
| refit + shd reskin | 94.74 – 136.18 (reskin is conditional for this reason) |
| refit + separate | 9.52 – 13.32 |
| + armpit | 10.75 – 15.05 |
| + weldcap (final) | 10.75 – 15.05 |

Crucifix "wings" visually gone (before/after renders viewed). Remaining stretch is
ball-joint skin under extreme rotation; the 2.5 threshold is aspirational for LBS
without corrective shapes — the pipeline drives the metric ~3× down toward it.

Pantera case (`case1_pantera_proof.txt`): arm-mesh Idle p99.9 11.95 → 2.11; re-run
byte-identical (deterministic). Logo emblem mesh unchanged (rigid, 21.32 — not a
skin defect).

## Lessons (do not "optimize" these away)

- **Chained numpy assignment is a silent no-op:** `Dw[mask][:, cols] = 0` modifies
  a copy. Use `Dw[np.ix_(mask, cols)] = 0`. (Cost a full armpit iteration.)
- **bmesh.remove_doubles creates holes:** even at 1e-6 it manufactured 19
  boundary edges on a watertight mesh. Never use it; assert instead.
- **bmesh sees UV seams as boundaries:** "capping" them manufactures holes.
  Weld by position (numpy) before counting.
- **Blender is Z-up, glTF is Y-up:** the importer converts; `arm.data.bones`
  head/tail are NOT populated (use edit bones); pose targets must be converted.
- **Corrective Smooth is a no-op at rest:** bake into weights, not mesh positions.
- **Sharp boundaries concentrate stretch:** decisive weight assignment at a genuine
  transition zone (armpit) can raise p99.9 vs a diffuse blend. Fix mis-assignments
  (separate), be conservative at true transitions.
- **Bone parents must be restored** after `use_connect` moves or the export writes
  a broken hierarchy.

## Video-production decision notes

- Entrance/promo renders (e.g. Pantera PR #169) are GATED on rig-repair: the
  final render does not ship until the model's gate numbers are on record. The
  pre-render package (canon table, plates, music, Blender scene, post script) can
  land first; the full render waits.
- Proof renders are clay-override stress poses, NOT the final video frames —
  they exist to show deformation, not to look finished.
- Media proof standard applies to every render the owner sees: own-eyes check,
  SHA-256 manifest, versioned files only.

## PR map

- #164: baseline (detect + transfer + gate + 6 clips + Track-1 fixes). Branch
  `rig-repair/pipeline-1`.
- #165: refit + conditional re-skin. Branch `rig-repair/refit-2`.
- #166: separate + armpit. Branch `rig-repair/separate-armpit-3`.
- #168: weldcap + proof + orchestrator + validation. Branch
  `rig-repair/orchestrator-4`.

Merge order #164 → #165 → #166 → #168. Merge decision is the owner's.
