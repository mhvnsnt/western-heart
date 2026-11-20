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
  kob2_180: 75f step 2 (38 kf @ 30 fps, 35 bones)
  kob2_ap: 180f step 2 (91 kf @ 30 fps, 35 bones)
  kob2_back2fire: 145f step 2 (73 kf @ 30 fps, 35 bones)
  kob2_bwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  kob2_escape: 321f step 2 (161 kf @ 30 fps, 35 bones)
  kob2_fire: 120f step 2 (61 kf @ 30 fps, 35 bones)
  kob2_fly2center: 140f step 2 (71 kf @ 30 fps, 35 bones)
  kob2_fly2fire: 110f step 2 (56 kf @ 30 fps, 35 bones)
  kob2_fly2landing: 67f step 2 (34 kf @ 30 fps, 35 bones)
  kob2_flykamae: 91f step 2 (46 kf @ 30 fps, 35 bones)
  kob2_fwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  kob2_hornatk: 96f step 2 (49 kf @ 30 fps, 35 bones)
  kob2_kamae: 121f step 2 (61 kf @ 30 fps, 35 bones)
  kob2_lstep: 60f step 2 (31 kf @ 30 fps, 35 bones)
  kob2_lwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  kob2_rstep: 60f step 2 (31 kf @ 30 fps, 35 bones)
  kob2_run: 54f step 2 (28 kf @ 30 fps, 35 bones)
  kob2_rwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  kob2_snakeatk: 120f step 2 (61 kf @ 30 fps, 35 bones)
  kob2_stbwalk: 35f step 2 (18 kf @ 30 fps, 35 bones)
  kob2_stfwalk: 64f step 2 (33 kf @ 30 fps, 35 bones)
  kob2_strun: 54f step 2 (28 kf @ 30 fps, 35 bones)
  kob2_stwarp: 40f step 2 (21 kf @ 30 fps, 35 bones)
  kob2_tailatk: 111f step 2 (56 kf @ 30 fps, 35 bones)
  kob2_warp2fire: 179f step 2 (90 kf @ 30 fps, 35 bones)

## Moves mapped
- (none — this pack is DATA: every clip is baked, no move mapping is claimed. Mapping owed, not guessed.)

## Unmapped (baked as data, mapping owed — not guessed)
- gym_kob2_180.dat
- gym_kob2_ap.dat
- gym_kob2_back2fire.dat
- gym_kob2_bwalk.dat
- gym_kob2_escape.dat
- gym_kob2_fire.dat
- gym_kob2_fly2center.dat
- gym_kob2_fly2fire.dat
- gym_kob2_fly2landing.dat
- gym_kob2_flykamae.dat
- gym_kob2_fwalk.dat
- gym_kob2_hornatk.dat
- gym_kob2_kamae.dat
- gym_kob2_lstep.dat
- gym_kob2_lwalk.dat
- gym_kob2_rstep.dat
- gym_kob2_run.dat
- gym_kob2_rwalk.dat
- gym_kob2_snakeatk.dat
- gym_kob2_stbwalk.dat
- gym_kob2_stfwalk.dat
- gym_kob2_strun.dat
- gym_kob2_stwarp.dat
- gym_kob2_tailatk.dat
- gym_kob2_warp2fire.dat

## Excluded from this pack (measured — not bakeable with this FK model)
- kob2_tail1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- kob2_tail2: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- kob2_tail3: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- kob2_tail4: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
