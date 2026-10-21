# Doc Frank bind normalization (2026-10-21)

## The defect (owner-spotted)
Doc Frank's head faced his opponent but his body was backwards. Root cause,
proven in the facing lane's DIAGNOSIS.md: his auto-rigged GLBs carry
pose-encoded bind locals (Spine1 90 deg about X, Head 21.5 deg X, Hips
180 deg Z, plus 100+ helper bones). `fighter.js` stage-2 retargeting
(`createT3Actions` -> `retargetClipToRig`) premultiplies every animation
track by the model's bind locals (`out = bind x clip`), skipping only
bones whose bind is identity. On standard rigs the driven bones' binds are
identity, so stage 2 is a no-op for them. On Doc Frank it re-applied his
pose-encoded binds over the solved pose, folding his torso ~177 deg at the
waist while his head still tracked the opponent.

## The fix (Option A: model-local, isolation-safe)
Every joint's bind local rotation in Doc Frank's GLBs is set to IDENTITY —
all of them, Hips included. Why Hips too: stage 2 only skips identity
binds, and the Hips 180 deg Z premultiply alone still rotated his solved
pose ~157 deg off the source (measured with the facing lane's sim, the
instrument that matched the live game to <1 deg on the original file).
Known-good fighters are unaffected-by-stage-2 because their DRIVEN bones
carry identity binds (Pantera's spine/head binds are identity; that is the
property that matters, not his Hips). With every bind identity, stage 2 is
a literal no-op for Doc Frank and the played pose is exactly the stage-1
solve, which matches the source clips.

Joint world bind positions are preserved exactly; inverse bind matrices
are recomputed as `IBM' = W'^-1 * W * IBM`, so `W' * IBM' == W * IBM` and
skinned vertices at bind pose are unchanged. No shared code touched, no
other character touched. Tools: `fix_binds.py` (plain GLBs),
`fix_binds_meshopt.py` (attire3/base, whose IBM accessor sits in a
meshopt-compressed bufferView: the decoded IBMs are rewritten and appended
as a plain bufferView; the old compressed view is left orphaned, harmless).

## Files fixed (all rigged Doc Frank GLBs; unrigged statics have no binds)
- `game/assets/models/doc-frank.glb` (178 joints)
- `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` (178)
- `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop.glb` (178)
- `roster/doc-frank/attires/attire1/pre-transform/model.glb` (178)
- `roster/doc-frank/attires/attire3/base/model.glb` (73, meshopt IBMs)

Not fixed (no skin / no binds — static Tripo pulls, unchanged):
attire1/post-transform, attire2 base+transformed, attire3/transformed,
attire4 base+transformed, attire2/dome-fix accessories.

## Verification (numeric, independently checked)
- `scan_binds.py` after fix: ALL bind locals identity in every fixed file.
- `verify_skin.py` (independent re-parse, CPU skinning at bind pose):
  max skinned-vertex deviation vs the original files = 1.21e-07 (template
  rigs); attire3 bone-matrix invariance through really-decoded meshopt IBMs
  = 2.98e-08; joint world positions identical everywhere.
- attire3 fixed file re-parsed by glTF-Transform NodeIO + meshopt decoder:
  OK, 73 joints / 73 IBMs.
- Facing-lane sim (validated against the live game on the original file):
  fixed GLB on the bosconovitch bank, stage 1 == stage 2 == 0.8 deg
  (shoulders) / 6.9 deg (pelvis) from the source clip; gunjack bank
  0.1 / 34.4 deg (the pelvis figure is the source clip's own bladed
  stance, present at stage 1 for the original file too). The original
  file scored 108.6 / 98.1 deg at stage 2 on the same instrument.
- Game-code pose export (the real `t3anims.js` in Node, full stage-2
  path): stance at 40% — shoulders +1.7 deg, head +10.8 deg, pelvis
  +5.9 deg, 0 NaN bones, rest frame all-zero. Identical numbers for the
  base GLB and the hood GLB (+1.5 deg shoulders). Before the fix the same
  path folded him (shoulders -164.9 deg).
- Visual proof frames: `docs/proof-docfrank-bindfix-20261021/`.
