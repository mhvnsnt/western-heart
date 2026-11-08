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
  dwhadoh00: 45f step 2 (23 kf @ 30 fps, 27 bones)
  dwup00: 60f step 2 (31 kf @ 30 fps, 27 bones)
  ikdv_36_nage_f: 120f step 2 (61 kf @ 30 fps, 35 bones)
  ikdv_36_nage_y: 126f step 2 (64 kf @ 30 fps, 35 bones)
  ikdv_b_nage_f: 170f step 2 (86 kf @ 30 fps, 35 bones)
  ikdv_b_nage_y: 170f step 2 (86 kf @ 30 fps, 35 bones)
  ikdv_ppp_nage_f: 92f step 2 (47 kf @ 30 fps, 35 bones)
  ikdv_ppp_nage_y: 92f step 2 (47 kf @ 30 fps, 35 bones)

## Moves mapped
- surge: dwhadoh00 (gym_dwhadoh00.dat) — Surge Form beam (wave file).
- surge-trigger: dwup00 (gym_dwup00.dat) — Soul Surge Bloom trigger — plays once when Surge Form starts.
- 1+3: ikdv_36_nage_f (gym_ikdv_36_nage_f.dat) — Surge Form front throw 1+3 (Surge Kit donor, first pair).
- 2+4: ikdv_36_nage_y (gym_ikdv_36_nage_y.dat) — Surge Form front throw 2+4 (Surge Kit donor, first pair).

## Unmapped (baked as data, mapping owed — not guessed)
- gym_ikdv_b_nage_f.dat
- gym_ikdv_b_nage_y.dat
- gym_ikdv_ppp_nage_f.dat
- gym_ikdv_ppp_nage_y.dat
