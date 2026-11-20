# DW curve bake log

Reference clip: gym_ozb3_greaction2.dat (frame 0 rest pose). Facing (pelvis forward): 0.00 deg from +Z.
root_rest_y: 0.885044 m. DW Hips->Chest: 0.13 m (scale vs king: 0.952381).

## Assumptions (DW data has no positions for these)
- Head/Neck rest: king-bank proportions at the same scale (Chest->Head 0.4229 m, Chest->Neck 0.273 m).
- ToeBase rest: Foot + [0, -0.1, 0.153] m (king-bank foot direction).
- 27-bone clips share the 35-bone rest pose; their bone lengths are transferred, unverified until the watched render.
- Dropped bones (unmapped, documented): 2 (lone spin/prop), 8 (fixed marker), 9/10 (chest chain, nature unidentified).

## Skipped-joint residual (real limit of the 35->21 bone map)
The canonical hierarchy skips DW joints 5 (Chest) and 7 (UpLeg). Their rotations are folded into the child local, but the child POSITION cannot be recovered from the parent rotation alone — the residual is the skipped joint rotation change x its offset (chest ~44-65 mm, upleg ~95-190 mm, up to 200-400 mm at the foot during a big throw). Joint rotations are correct; only the torso-match direction is bounded by a few degrees. The render is the arbiter.

## Clips baked
  ozhe_power: 45f step 2 (23 kf @ 30 fps, 35 bones)
  oznj_meteorite: 110f step 2 (56 kf @ 30 fps, 35 bones)
  ozt4_aidoring: 60f step 2 (31 kf @ 30 fps, 35 bones)
  ozt4_goron: 57f step 2 (29 kf @ 30 fps, 35 bones)
  ozt4_kamae: 80f step 2 (41 kf @ 30 fps, 35 bones)

## Moves mapped
- (none — this pack is DATA: every clip is baked, no move mapping is claimed. Mapping owed, not guessed.)

## Unmapped (baked as data, mapping owed — not guessed)
- gym_ozhe_power.dat
- gym_oznj_meteorite.dat
- gym_ozt4_aidoring.dat
- gym_ozt4_goron.dat
- gym_ozt4_kamae.dat

## Excluded from this pack (measured — not bakeable with this FK model)
- ozhe_1ckj66a: missing file — no data in TK5DATA2 (list reference only, no curves to bake)
