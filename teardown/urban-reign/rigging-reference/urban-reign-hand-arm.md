# Urban Reign — hand/arm reference

Source: teardown/urban-reign/ (PPK-FORMAT.md, VGS-FORMAT.md, motion/*.gyu) +
extraction-coordinator output 2026-10-23: docs/urban-reign/URBAN-REIGN-SKINNING.md
(PR #429), decode-stats/charNNN.json, teardown/urban-reign/models/charNNN/*.glb
(72 characters, skinned GLBs decoded by teardown/urban-reign/tools/ur_decode.py).

## Bone-name pool: DECODED (49 names, chr01/chr02)

From the .vmd header bone-name pool (same set and order in chr01/chr02):

- Torso: MUNE1, MUNE2 (chest), KUBI (neck), ATAMA (head), KOSHI (hips)
- Arm: SAKOTSU_R/L (collarbone) -> KATA_R/L (shoulder) -> UDE_R/L (upper arm)
  -> TE_R/L (hand = terminal joint)
- Leg: MOMO_R/L (thigh) -> HIZA_R/L (knee) -> ASHI_R/L (foot/shin)
  -> TSUMASAKI_R/L (toe)
- Face: MIKEN, MAYU, EYE, MABUTA (eyelid), AGO (chin), KUCHI (mouth)
- Constraint helpers: *__rot / *__prot / *__slerp / *__const, j__swing,
  yR__swing, yL__swing

**No finger bones exist in the pool.** Urban Reign hands are mitten-style:
TE_R/L is the terminal hand joint. (Japanese naming matches VF5's convention:
te = hand, ude = upper arm, kata = shoulder, sakotsu = collarbone.)

## GLB structure (char001 verified)

- 37 skin joints, 38 nodes; joints emitted as bone_<id> (name<->node-id mapping
  not yet proven, so the pool names above are not yet bound to GLB node ids).
- Hand region terminates in leaf joints with no finger chains — consistent with
  the pool.

## Weight model (matters for hand/arm skinning)

- Positions AND normals are stored **premultiplied by the weight** (proof:
  |stored_normal| == w exactly for every influence). The VU1 skinning
  microprogram sums M_bone * stored with no separate weight multiply.
- Bind matrices are NOT stored in the character files; the ELF computes bone
  matrices at runtime from per-node Euler+position data.

## Motion

- .gyu motion files (general_30frame.gyu, general_normal.gyu, general_weapon.gyu)
  carry the grapple choreography; with no finger joints, all hand acting is
  wrist orientation (TE_R/L) per move.
- general_weapon.gyu is the future source for weapon-grip wrist poses once the
  .gyu track format is fully decoded.

## Takeaway

- Urban Reign is a grappling game with NO finger articulation — its hand/arm
  reference value is the **grapple wrist choreography** (.gyu), not hand bones.
- The decoded bone pool gives exact Japanese hand/arm joint names for
  retarget mapping (TE/UDE/KATA/SAKOTSU).
