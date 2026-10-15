# Universal Rig-Repair Pipeline

One-command character rig repair for all games (Bannon, AshLane, Brutal Fist,
Western Heart). Fixes the defect class where skin weights disagree with the
skeleton: torso skin weighted to limbs ("wings"), limb skin weighted to the
wrong limb (hands glued to legs), and skeletons refit outside the mesh.

## Quick start

```bash
# one model
python3 pipeline/pipeline.py --in MODEL.glb --outdir out --tag stickup

# batch (one Blender process per model per stage = crash isolation)
ls models/*.glb | xargs -P 4 -I{} python3 pipeline/pipeline.py \
    --in {} --outdir out --tag $(basename {} .glb)
```

Every stage writes a VERSIONED file (`{tag}_{stage}.glb`) + JSON report.
Inputs are NEVER touched.

## Stages

| # | Stage | Tool | What it does |
|---|-------|------|--------------|
| 1 | detect | `rig_repair.py detect` | Multi-mesh/primitive scan; meshopt + multi-buffer decode (Python, no vendored node_modules). Reports skin, influences, holes, non-manifold. |
| 2 | transfer | `rig_repair.py transfer --limb-separate` | Weight transfer from a canonical skeleton. De-hardcoded: mesh name from target, tolerant joint matching (synonym tables), loud skip on non-Mixamo, preserves extensions. |
| 3 | refit | `refit.py` (Blender) | **The core new step.** Volume-mode skeleton refit: for each joint, cast rays through the mesh on 3 axes, move the joint to the volume center (shortest chord midpoint if inside, surface + half-thickness if outside). Clamp 0.10 m. Recomputes inverse bind matrices on export so existing clips (local rotations) play unchanged. |
| 4 | reskin | `reskin.py` / `reskin_heat.py` (Blender) | **Conditional.** Surface-Heat-Diffuse-Skinning (MIT, meshonline) or Blender bone heat. Default `none`: keep transfer weights. Re-skin only when weights are missing/stale — on tested models, full re-skin destroyed good transfer weights (Hips 40% dominance). |
| 5 | separate | `separate.py` (numpy) | Topology-based limb/body separation. Reassigns verts whose dominant bone is >0.20 m away to the nearest plausible bone of the correct body region. Fixes "hands glued to legs" without a transfer source. |
| 6 | armpit | `armpit.py` (numpy) | Armpit de-bleed (arm weights → 0 beyond 0.14 m), contrast sharpen, torso-side correction (torso verts must not carry arm weights even when the hanging forearm passes close). |
| 7 | weldcap | `weldcap.py` (Blender) | Recalc normals + HARD ASSERT: zero open edges (welded by position, so UV seams don't count), non-manifold not increased. Fails loudly; the 266-open-edge incident is impossible by assertion. |
| 8 | gate | `rigcheck/rig_check.py` | Static gate: p99.9 edge stretch vs 2.5 (6 standard clips), ground contact, hinge flips. Python decode (no node_modules). |
| 9 | proof | `proof.py` (Blender) | Stress-pose renders (arms raised, crucifix, finger guns, walk) with clay material. **Open every render yourself** (media proof standard). |

## Measured result (Stick-Up v1, decimated)

| Stage | stretch p99.9 (6 clips) |
|---|---|
| Input (STICKUP_repaired.glb) | 27.7 – 44.7 |
| After refit + separate + armpit + weldcap | 10.7 – 15.1 |

The "wings" (torso skin flying with the arm in crucifix) are visually gone.
Remaining stretch is ball-joint skin under extreme rotation; the 2.5 threshold
is aspirational for LBS without corrective shapes.

## Lessons (do not "optimize" these away)

- **Chained numpy assignment is a silent no-op:** `Dw[mask][:, cols] = 0` modifies
  a copy. Use `Dw[np.ix_(mask, cols)] = 0`. (Cost us a full armpit iteration.)
- **bmesh.remove_doubles creates holes:** even at 1e-6 it manufactured 19
  boundary edges on a watertight mesh. Never use it; assert instead.
- **bmesh sees UV seams as boundaries:** "capping" them manufactures holes.
  Weld by position (numpy) before counting.
- **Blender is Z-up, glTF is Y-up:** the importer converts; `arm.data.bones`
  head/tail are NOT populated (use edit bones); pose targets must be converted.
- **Corrective Smooth is a no-op at rest:** bake into weights (de-bleed), not
  mesh positions; export-time modifiers don't transfer to game engines.
- **Sharp boundaries concentrate stretch:** decisive weight assignment at a
  genuine transition zone (armpit) can raise p99.9 vs a diffuse blend. Fix
  mis-assignments (separate), be conservative at true transitions.

## Files

- `ingest.py` — shared GLB reader (meshopt via pip `meshopt`, multi-buffer).
- `rig_repair.py` — detect + transfer (v2: multi-mesh, de-hardcoded).
- `rigcheck/rig_check.py` — the gate.
- `clips/standard/` — 6 procedural gate clips (test fixtures, not game content).
- `refit.py`, `reskin.py`, `reskin_heat.py`, `separate.py`, `armpit.py`,
  `weldcap.py`, `proof.py`, `pipeline.py` — the stages.
- `diag_stretch.py`, `diag_joints.py`, `look.py` — diagnostics.
