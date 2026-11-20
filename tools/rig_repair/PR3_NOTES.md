# PR 3: Limb separation + armpit correction

## separate.py — standalone limb/body separation (numpy)

Promoted from `transfer --limb-separate` to a standalone stage: the defect
class (verts weighted to the wrong body region) exists in already-weighted
models with no transfer source.

- For each vert, if the dominant bone is >0.20 m away (bind pose), reassign to
  the nearest plausible bone of the correct body region (arm/leg/torso via the
  joint synonym tables).
- Fixes "hands glued to legs": measured 812 hand-region verts weighted >0.5 to
  leg bones on the test model; 2,675 verts >25 cm from their dominant bone.
- Rebuilds the GLB with full accessor remap (fixes two rebuild bugs: accessor
  byteOffset slicing, stale indices/IBM refs).

Measured: stretch 28–45 → 9.5–13.3 (refit + separate, before armpit).

## armpit.py — armpit de-bleed + sharpen + torso-side (numpy)

- **De-bleed:** arm weights → 0 beyond 0.14 m from arm segments (k-NN bleed fix).
- **Sharpen:** contrast p=1.6 on arm-vs-torso blends inside the region.
- **Torso-side:** torso verts must not carry arm weights, however close the
  hanging forearm passes (proximity != limb). Uses nearest bind-pose segment
  as the torso/limb discriminator.

**Decision (documented in-file):** Corrective Smooth is baked into WEIGHTS, not
mesh positions. Rationale: Corrective Smooth is a no-op at rest pose, and
export-time modifier state doesn't transfer to game engines. The weight-side
fix (de-bleed) achieves the same without mesh mutation.

**Critical bug found & fixed:** `Dw[mask][:, cols] = 0` (chained boolean
indexing) is a SILENT NO-OP — it modifies a copy. All corrections were
discarded until fixed with `Dw[np.ix_(mask, cols)] = 0`. Documented in
`pipeline/README.md` lessons.

Measured: 9.5–13.3 → 8.4–11.2 (with smoothing-order fix: corrections run after
smoothing, not before, so they aren't diffused away).

## Note on sharpness vs stretch

Decisive weight assignment at a GENUINE transition zone (armpit) can raise
p99.9 vs a diffuse blend (sharp boundary concentrates stretch over fewer
edges). The stage fixes mis-assignments (separate) and is conservative at true
transitions. See validation in PR 4.
