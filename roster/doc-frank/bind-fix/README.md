# Doc Frank bind normalization (2026-10-21)

## The defect (owner-spotted)
Doc Frank's head faced his opponent but his body was backwards. Root cause,
proven in `~/workspace/_docfrank-facing/DIAGNOSIS.md` (lane workdir): his
auto-rigged GLBs carry pose-encoded bind locals (Spine1 90 deg about X, Head
21.5 deg X, plus 100+ helper bones). `fighter.js` stage-2 retargeting
(`createT3Actions` -> `retargetClipToRig`) premultiplies every animation
track by the model's bind locals (`out = bind x clip`). On standard rigs
(Pantera, Steve Fox) every bind local is identity except Hips (180 deg Z,
the intended convention), so stage 2 is a no-op for them. On Doc Frank it
re-applied his 90 deg spine bind over the solved pose, folding his torso
~177 deg at the waist while his head still tracked the opponent.

## The fix (Option A: model-local, isolation-safe)
`fix_binds.py` rewrites ONLY Doc Frank's GLBs: every joint's bind local
rotation is set to identity, except the Hips joint, which keeps the standard
180 deg Z. Joint world bind positions are preserved; inverse bind matrices
are recomputed as `IBM' = W'^-1 * W * IBM`, so `W' * IBM' == W * IBM` and
skinned vertices at bind pose are unchanged. No shared code touched, no
other character touched. `fix_binds_meshopt.py` is the same fix for a GLB
whose IBM accessor sits in a meshopt-compressed bufferView (attire3/base):
the decoded IBMs are rewritten and appended as a plain bufferView (the old
compressed view is left orphaned, harmless).

## Files fixed (all rigged Doc Frank GLBs; unrigged statics have no binds)
- `game/assets/models/doc-frank.glb` (178 joints)
- `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb` (178)
- `roster/doc-frank/attires/machine-shop/doc-frank-machine-shop.glb` (178)
- `roster/doc-frank/attires/attire1/pre-transform/model.glb` (178)
- `roster/doc-frank/attires/attire3/base/model.glb` (73, meshopt IBMs)

Not fixed (no skin / no binds — static Tripo pulls, unchanged):
attire1/post-transform, attire2 base+transformed, attire3/transformed,
attire4 base+transformed, attire2/dome-fix accessories.

## Verification (own-eyes + numeric)
- `scan_binds.py` after fix: exactly ONE non-identity bind local per file —
  Hips 180.0 deg about Z — the standard convention.
- `verify_skin.py` (independent re-parse, CPU skinning at bind pose):
  max skinned-vertex deviation vs the original files = 1.21e-07 (template
  rigs); attire3 bone-matrix invariance through really-decoded meshopt IBMs
  = 2.98e-08; joint world positions identical everywhere.
- attire3 fixed file re-parsed by glTF-Transform NodeIO + meshopt decoder:
  OK, 1 skin / 73 joints / 73 IBMs.
- In-game proof frames: `docs/proof-docfrank-bindfix-20261021/`.
