# tools/rig_repair: verifiable rig and skin defect fixes

Each case fixes only a defect that can be proved from the file itself, and each one writes a NEW file. Originals are never changed.

## Case 1: `game/assets/models/pantera.glb`, Left/Right swapped skin
- **Defect:** 5,805 of 5,805 vertices with |x| > 0.15 m whose dominant joint is a Left*/Right* bone sit on the opposite side from that bone's bind position. Every clip, including the model's own Idle, tears the arms across the body.
- **Fix:** `swap_lr_joints.py pantera.glb pantera_fixed.glb` remaps each `JOINTS_0` index to the bone with the mirrored name. Weights, positions, inverse bind matrices, nodes and clips are untouched. `RightHandThumb3` has no Left partner and carries no weight; the script asserts this. The script refuses to run unless at least 99% of side vertices are on the wrong side. `demonio.glb` has 0 of 3,028 wrong, so it is refused.
- **Verification** (`case1_pantera_proof.txt`):
  - Symmetry: 0 of 5,805 vertices on the opposite side after the fix. A re-run is byte-identical.
  - Tearing, measured with `stretch_check.py` (worst triangle-edge stretch on the arms mesh): Idle 11.95 → 2.11. T3 clips baked onto each file: stance_b 21.2 → 5.1, light 22.3 → 5.5, ko 17.5 → 4.0.
  - Render: `docs/qa/anim/pantera_skin_lr_fix_before_after.jpg`.
- **Not fixed (case 2 candidates, authored weighting, not a swap):**
  - The wrist cuffs (`belt2`, `buckles`) are weighted entirely to Spine/Spine1, so they float at the T-pose wrist positions.
  - `logo` is weighted to Spine/Spine2.
  - `pants` is weighted to the UpLegs only, with no Hips weight, so edges stretch 12–24× in wide stances.
  - Assigning these to other bones would be a choice, not a verifiable fix, so they are left for the owner.
