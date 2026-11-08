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
  ikdv_all_beam: 85f step 2 (43 kf @ 30 fps, 35 bones)
  ikdv_b_nage_f: 170f step 2 (86 kf @ 30 fps, 35 bones)
  ikdv_b_nage_y: 170f step 2 (86 kf @ 30 fps, 35 bones)
  ikdv_beam: 85f step 2 (43 kf @ 30 fps, 35 bones)
  ikdv_chaku: 20f step 2 (11 kf @ 30 fps, 35 bones)
  ikdv_d_beam: 65f step 2 (33 kf @ 30 fps, 35 bones)
  ikdv_d_jump_k: 57f step 1 (57 kf @ 60 fps, 35 bones)
  ikdv_d_jump_p: 62f step 2 (32 kf @ 30 fps, 35 bones)
  ikdv_d_nagi_beam: 70f step 2 (36 kf @ 30 fps, 35 bones)
  ikdv_dsrp: 65f step 2 (33 kf @ 30 fps, 35 bones)
  ikdv_dsrp_k: 77f step 2 (39 kf @ 30 fps, 35 bones)
  ikdv_dv2kam2: 101f step 2 (51 kf @ 30 fps, 35 bones)
  ikdv_dv_jz: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ikdv_fstep: 32f step 2 (17 kf @ 30 fps, 35 bones)
  ikdv_jump_beam: 130f step 2 (66 kf @ 30 fps, 35 bones)
  ikdv_jump_k: 77f step 2 (39 kf @ 30 fps, 35 bones)
  ikdv_jump_p: 63f step 2 (32 kf @ 30 fps, 35 bones)
  ikdv_jz_dv: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ikdv_k_1: 55f step 1 (55 kf @ 60 fps, 35 bones)
  ikdv_k_2: 59f step 2 (30 kf @ 30 fps, 35 bones)
  ikdv_k_3: 66f step 1 (66 kf @ 60 fps, 35 bones)
  ikdv_k_4: 70f step 2 (36 kf @ 30 fps, 35 bones)
  ikdv_l2idou: 40f step 2 (21 kf @ 30 fps, 35 bones)
  ikdv_lturn: 30f step 2 (16 kf @ 30 fps, 35 bones)
  ikdv_lturn90: 20f step 2 (11 kf @ 30 fps, 35 bones)
  ikdv_lukemi: 50f step 2 (26 kf @ 30 fps, 35 bones)
  ikdv_nara: 66f step 2 (34 kf @ 30 fps, 35 bones)
  ikdv_nige00: 61f step 2 (31 kf @ 30 fps, 35 bones)
  ikdv_p_1: 39f step 2 (20 kf @ 30 fps, 35 bones)
  ikdv_p_2: 40f step 2 (21 kf @ 30 fps, 35 bones)
  ikdv_p_3: 54f step 2 (28 kf @ 30 fps, 35 bones)
  ikdv_p_4: 51f step 2 (26 kf @ 30 fps, 35 bones)
  ikdv_p_5: 56f step 2 (29 kf @ 30 fps, 35 bones)
  ikdv_p_kaitenk: 64f step 1 (64 kf @ 60 fps, 35 bones)
  ikdv_pk: 49f step 1 (49 kf @ 60 fps, 35 bones)
  ikdv_ppk: 69f step 1 (69 kf @ 60 fps, 35 bones)
  ikdv_ppp_nage_f: 92f step 2 (47 kf @ 30 fps, 35 bones)
  ikdv_ppp_nage_y: 92f step 2 (47 kf @ 30 fps, 35 bones)
  ikdv_r2idou: 40f step 2 (21 kf @ 30 fps, 35 bones)
  ikdv_rturn: 30f step 2 (16 kf @ 30 fps, 35 bones)
  ikdv_rturn90: 20f step 2 (11 kf @ 30 fps, 35 bones)
  ikdv_rukemi: 50f step 2 (26 kf @ 30 fps, 35 bones)
  ikdv_run_p: 52f step 2 (27 kf @ 30 fps, 35 bones)
  ikdv_shoryu: 50f step 2 (26 kf @ 30 fps, 35 bones)
  ikdv_sjk: 67f step 2 (34 kf @ 30 fps, 35 bones)
  ikdv_sjk00: 66f step 2 (34 kf @ 30 fps, 35 bones)
  ikdv_sjk01: 60f step 2 (31 kf @ 30 fps, 35 bones)
  ikdv_sjk02: 70f step 2 (36 kf @ 30 fps, 35 bones)
  ikdv_sjk03: 70f step 2 (36 kf @ 30 fps, 35 bones)
  ikdv_sway: 35f step 2 (18 kf @ 30 fps, 35 bones)

## Moves mapped
- surge: dwhadoh00 (gym_dwhadoh00.dat) — Surge Form beam (wave file).
- surge-trigger: dwup00 (gym_dwup00.dat) — Soul Surge Bloom trigger — plays once when Surge Form starts.
- 1+3: ikdv_36_nage_f (gym_ikdv_36_nage_f.dat) — Surge Form front throw 1+3 (Surge Kit donor, first pair).
- 2+4: ikdv_36_nage_y (gym_ikdv_36_nage_y.dat) — Surge Form front throw 2+4 (Surge Kit donor, first pair).

## Unmapped (baked as data, mapping owed — not guessed)
- gym_ikdv_all_beam.dat
- gym_ikdv_b_nage_f.dat
- gym_ikdv_b_nage_y.dat
- gym_ikdv_beam.dat
- gym_ikdv_chaku.dat
- gym_ikdv_d_beam.dat
- gym_ikdv_d_jump_k.dat
- gym_ikdv_d_jump_p.dat
- gym_ikdv_d_nagi_beam.dat
- gym_ikdv_dsrp.dat
- gym_ikdv_dsrp_k.dat
- gym_ikdv_dv2kam2.dat
- gym_ikdv_dv_jz.dat
- gym_ikdv_fstep.dat
- gym_ikdv_jump_beam.dat
- gym_ikdv_jump_k.dat
- gym_ikdv_jump_p.dat
- gym_ikdv_jz_dv.dat
- gym_ikdv_k_1.dat
- gym_ikdv_k_2.dat
- gym_ikdv_k_3.dat
- gym_ikdv_k_4.dat
- gym_ikdv_l2idou.dat
- gym_ikdv_lturn.dat
- gym_ikdv_lturn90.dat
- gym_ikdv_lukemi.dat
- gym_ikdv_nara.dat
- gym_ikdv_nige00.dat
- gym_ikdv_p_1.dat
- gym_ikdv_p_2.dat
- gym_ikdv_p_3.dat
- gym_ikdv_p_4.dat
- gym_ikdv_p_5.dat
- gym_ikdv_p_kaitenk.dat
- gym_ikdv_pk.dat
- gym_ikdv_ppk.dat
- gym_ikdv_ppp_nage_f.dat
- gym_ikdv_ppp_nage_y.dat
- gym_ikdv_r2idou.dat
- gym_ikdv_rturn.dat
- gym_ikdv_rturn90.dat
- gym_ikdv_rukemi.dat
- gym_ikdv_run_p.dat
- gym_ikdv_shoryu.dat
- gym_ikdv_sjk.dat
- gym_ikdv_sjk00.dat
- gym_ikdv_sjk01.dat
- gym_ikdv_sjk02.dat
- gym_ikdv_sjk03.dat
- gym_ikdv_sway.dat

## Excluded from this pack (measured — not bakeable with this FK model)
- (none — every decoded clip of this group is baked)
