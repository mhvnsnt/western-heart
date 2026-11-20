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
  kmb1_bakutyu: 65f step 2 (33 kf @ 30 fps, 35 bones)
  kmb1_bakutyushot: 205f step 1 (205 kf @ 60 fps, 35 bones)
  kmb1_charge_shot_02: 137f step 2 (69 kf @ 30 fps, 35 bones)
  kmb1_guard_mm: 30f step 2 (16 kf @ 30 fps, 35 bones)
  kmb1_hijump_shot: 200f step 2 (101 kf @ 30 fps, 35 bones)
  kmb1_histep_l: 55f step 2 (28 kf @ 30 fps, 35 bones)
  kmb1_histep_r: 55f step 2 (28 kf @ 30 fps, 35 bones)
  kmb1_jumpmachinegun: 211f step 1 (211 kf @ 60 fps, 35 bones)
  kmb1_kamae: 150f step 2 (76 kf @ 30 fps, 35 bones)
  kmb1_lk: 64f step 2 (33 kf @ 30 fps, 35 bones)
  kmb1_lk_histep_r: 60f step 2 (31 kf @ 30 fps, 35 bones)
  kmb1_lturn180: 30f step 2 (16 kf @ 30 fps, 35 bones)
  kmb1_lturn90: 20f step 2 (11 kf @ 30 fps, 35 bones)
  kmb1_machinegun: 225f step 1 (225 kf @ 60 fps, 35 bones)
  kmb1_machinegun_f: 60f step 2 (31 kf @ 30 fps, 35 bones)
  kmb1_rk: 70f step 2 (36 kf @ 30 fps, 35 bones)
  kmb1_rk_histep_l: 70f step 2 (36 kf @ 30 fps, 35 bones)
  kmb1_rturn180: 30f step 2 (16 kf @ 30 fps, 35 bones)
  kmb1_rturn90: 20f step 2 (11 kf @ 30 fps, 35 bones)
  kmb1_run01_start: 32f step 2 (17 kf @ 30 fps, 35 bones)
  kmb1_run02_loop: 32f step 2 (17 kf @ 30 fps, 35 bones)
  kmb1_run03_walk: 32f step 2 (17 kf @ 30 fps, 35 bones)
  kmb1_shortshot_shot: 65f step 2 (33 kf @ 30 fps, 35 bones)
  kmb1_shortshot_soten: 102f step 2 (52 kf @ 30 fps, 35 bones)
  kmb1_shotgun_cyop: 59f step 2 (30 kf @ 30 fps, 35 bones)
  kmb1_shotgun_shot: 65f step 2 (33 kf @ 30 fps, 35 bones)
  kmb1_shotgun_soten: 102f step 2 (52 kf @ 30 fps, 35 bones)
  kmb1_step_in: 45f step 2 (23 kf @ 30 fps, 35 bones)
  kmb1_step_l: 40f step 2 (21 kf @ 30 fps, 35 bones)
  kmb1_step_r: 40f step 2 (21 kf @ 30 fps, 35 bones)
  kmb1_tojo: 180f step 1 (180 kf @ 60 fps, 35 bones)
  kmb1_walk_f01_start: 30f step 2 (16 kf @ 30 fps, 35 bones)
  kmb1_walk_f02_loop: 45f step 2 (23 kf @ 30 fps, 35 bones)
  kmb1_walk_l: 75f step 2 (38 kf @ 30 fps, 35 bones)
  kmb1_walk_r: 75f step 2 (38 kf @ 30 fps, 35 bones)
  kmb1_wdown: 91f step 2 (46 kf @ 30 fps, 35 bones)
  kmb1_wshot: 69f step 2 (35 kf @ 30 fps, 35 bones)
  kmb1_yoko_l: 125f step 2 (63 kf @ 30 fps, 35 bones)
  kmb1_yoko_r: 125f step 2 (63 kf @ 30 fps, 35 bones)

## Moves mapped
- (none — this pack is DATA: every clip is baked, no move mapping is claimed. Mapping owed, not guessed.)

## Unmapped (baked as data, mapping owed — not guessed)
- gym_kmb1_bakutyu.dat
- gym_kmb1_bakutyushot.dat
- gym_kmb1_charge_shot_02.dat
- gym_kmb1_guard_mm.dat
- gym_kmb1_hijump_shot.dat
- gym_kmb1_histep_l.dat
- gym_kmb1_histep_r.dat
- gym_kmb1_jumpmachinegun.dat
- gym_kmb1_kamae.dat
- gym_kmb1_lk.dat
- gym_kmb1_lk_histep_r.dat
- gym_kmb1_lturn180.dat
- gym_kmb1_lturn90.dat
- gym_kmb1_machinegun.dat
- gym_kmb1_machinegun_f.dat
- gym_kmb1_rk.dat
- gym_kmb1_rk_histep_l.dat
- gym_kmb1_rturn180.dat
- gym_kmb1_rturn90.dat
- gym_kmb1_run01_start.dat
- gym_kmb1_run02_loop.dat
- gym_kmb1_run03_walk.dat
- gym_kmb1_shortshot_shot.dat
- gym_kmb1_shortshot_soten.dat
- gym_kmb1_shotgun_cyop.dat
- gym_kmb1_shotgun_shot.dat
- gym_kmb1_shotgun_soten.dat
- gym_kmb1_step_in.dat
- gym_kmb1_step_l.dat
- gym_kmb1_step_r.dat
- gym_kmb1_tojo.dat
- gym_kmb1_walk_f01_start.dat
- gym_kmb1_walk_f02_loop.dat
- gym_kmb1_walk_l.dat
- gym_kmb1_walk_r.dat
- gym_kmb1_wdown.dat
- gym_kmb1_wshot.dat
- gym_kmb1_yoko_l.dat
- gym_kmb1_yoko_r.dat

## Excluded from this pack (measured — not bakeable with this FK model)
- (none — every decoded clip of this group is baked)
