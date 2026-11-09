# Angel Straight displacement — attribution + GLB fit fix (2026-11-09)

## Verdict
The straight part's **geometry sits 0.05 m too low relative to its own
rig** in the shipped GLB (build/export stage). The rig, skins, IBMs,
weights and Blender-side band placement are all correct. The shipped
canonical proofs compounded the error with a second, independent one:
the hair-fix harness's hardcoded −0.33 m compensation (a Defect B
measurement artifact — see PARVATI-V4-ATTIRE1-LANDING-2026-11-09.md).
The GLB is fixed in this PR by translating all geometry (AngelStraight
mesh, 3 prims + AngelHeadband mesh) by +0.05 m in Y — exactly what the
build's fit stage does in the blend (cf. fix_band.py's vertex-level fit
transforms). The part's build blends no longer exist on disk, so the
correction was applied to the exported geometry with the measured
vector; everything else is byte-identical.

## What was ruled out (measured)
- Rig difference: none. The straight and afro GLBs carry IDENTICAL rigs
  (1 skin each; 'head' joint world (0, 1.629, −0.004) in both; same hip
  and neck placements). Joint name casing differences exist (back1/Back2,
  bangsL_A1/BangsL_A2 etc.) but bind identically.
- Bind error: afro 9.3e-07, straight 1.4e-05 (three.js bindcheck: K =
  JW·IBM = identity, max err over weighted joints 9.2e-06). No
  animations, no skin.skeleton fields, joint scales ≈ 1.0.
- File-space geometry is anatomically sane solo (shell y 1.281–1.825,
  band on the hairline of its own frame). Solo renders are coherent.

## The three measurements that convict the geometry-vs-rig offset
1. **Strand-root offset**: mean offset of strand-root verts from their
   hair-chain joints — straight: (+0.001, **−0.051**, +0.019); afro
   control: (+0.001, +0.015, +0.004). Every straight chain (back, bangs,
   left, right) shows the same systematic −Y displacement.
2. **Cap edge vs the body's own hairline**: the pilot body's own
   AngelHairScalpCap front edge (morphed) bottoms at world y 1.623. The
   straight's cap front edge under standard head-joint composition lands
   at 1.573 — 5 cm low. After the fix: 1.623. Exact.
3. **Band vs the body's own band**: the pilot body's own AngelHeadband
   (morphed) spans world y 1.611–1.655. The part's band under head-joint
   composition: 1.562–1.620 (5 cm low — the "visor"/floating-slab read).
   After the fix: 1.612–1.670, on the hairline.
   Crown clearance after fix: shell top 1.733 vs morphed crown 1.690
   (+4.3 cm); before the fix the crown poked 7 mm ABOVE the shell top
   (1.683) — the "bare scalp dome" in the rejected proofs.

## Fix + preservation audit
- Only POSITION floats of the 4 prims changed (+0.05 Y), plus the
  accessors' min/max Y scalars (JSON diff = 8 scalars).
- BIN length identical (11,593,896 B); all 530,685 differing bytes lie
  inside the 4 POSITION accessor ranges. Rig, IBMs, weights, indices,
  normals, materials, images byte-identical.
- New file: 11,606,856 B (was 11,607,996; JSON digit-length change only),
  sha256 recorded in the PR.
- Post-fix root offset: (+0.001, −0.011, +0.018) — same relationship
  class as the afro (+0.015). Residual −0.011 Y is smaller than the
  afro's own +0.015 deviation.

## Composition rule (for future part fits)
Compose hair parts by **head-joint alignment** (part root offset = body
Head joint − part head joint). Never apply ad-hoc vertical constants:
the −0.33 constant in `_hair-fix-20261108/stage.html` line 57 came from
the refuted Defect B centroid artifact and displaces any part fitted
with it (≈ +0.087 too high on the v4 body: correct offset there is
−0.417 = 1.212 − 1.629). The correct offset must be recomputed per body
from the two rigs' head joints.

## Caveats
- The part was authored from Parvati-Commission.blend's Flora hair
  (build_straight_fix.py) against the Daz head, not re-fitted on the
  pilot's morphed head like the afro was. This fix corrects the measured
  fit error; the design's own properties remain: no bangs (deleted in
  the build), so the pilot head's high forehead (brow ≈1.53 → hairline
  ≈1.62, AngelFace proportions) reads long, and a small faceted patch
  shows at the parting in close-ups (present in the shipped file's
  renders before this fix as well).
- In the band-ON close proof, the band sits on the hairline; its upper
  arc reads behind the front strand fall from the low face camera —
  layering of the authored design, not displacement.
- Flora remains Megami's default hair; afro + straight remain options.
  Registry entry count unchanged (1,192 parts); the registry stores no
  size/sha for parts, so no registry edit was needed.
