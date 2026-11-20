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
  ozb3_360: 100f step 2 (51 kf @ 30 fps, 35 bones)
  ozb3_burn: 210f step 2 (106 kf @ 30 fps, 35 bones)
  ozb3_burn2: 147f step 2 (74 kf @ 30 fps, 35 bones)
  ozb3_bwalk00: 35f step 2 (18 kf @ 30 fps, 35 bones)
  ozb3_bwalk01: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ozb3_dead: 500f step 2 (251 kf @ 30 fps, 35 bones)
  ozb3_firehado2: 153f step 2 (77 kf @ 30 fps, 35 bones)
  ozb3_fumi: 125f step 2 (63 kf @ 30 fps, 35 bones)
  ozb3_greaction2: 30f step 2 (16 kf @ 30 fps, 35 bones)
  ozb3_guardkama2: 10f step 2 (6 kf @ 30 fps, 35 bones)
  ozb3_guardpose: 2f step 2 (2 kf @ 30 fps, 35 bones)
  ozb3_guardroop2: 72f step 2 (37 kf @ 30 fps, 35 bones)
  ozb3_houmingf: 175f step 2 (88 kf @ 30 fps, 35 bones)
  ozb3_issoku: 60f step 2 (31 kf @ 30 fps, 35 bones)
  ozb3_kamae: 72f step 2 (37 kf @ 30 fps, 35 bones)
  ozb3_kamaguard2: 5f step 2 (3 kf @ 30 fps, 35 bones)
  ozb3_lwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ozb3_run00: 54f step 2 (28 kf @ 30 fps, 35 bones)
  ozb3_run01: 54f step 2 (28 kf @ 30 fps, 35 bones)
  ozb3_rwalk: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ozb3_shippo: 100f step 2 (51 kf @ 30 fps, 35 bones)
  ozb3_tatumaki: 110f step 2 (56 kf @ 30 fps, 35 bones)
  ozb3_tobinoki: 60f step 2 (31 kf @ 30 fps, 35 bones)
  ozb3_toujyou: 460f step 2 (231 kf @ 30 fps, 35 bones)
  ozb3_tunoupper2: 120f step 2 (61 kf @ 30 fps, 35 bones)
  ozb3_walk00: 64f step 2 (33 kf @ 30 fps, 35 bones)
  ozb3_walk01: 90f step 2 (46 kf @ 30 fps, 35 bones)
  ozb3_warp1: 100f step 2 (51 kf @ 30 fps, 35 bones)
  ozb3_warp2: 105f step 2 (53 kf @ 30 fps, 35 bones)

## Moves mapped
- (none — this pack is DATA: every clip is baked, no move mapping is claimed. Mapping owed, not guessed.)

## Unmapped (baked as data, mapping owed — not guessed)
- gym_ozb3_360.dat
- gym_ozb3_burn.dat
- gym_ozb3_burn2.dat
- gym_ozb3_bwalk00.dat
- gym_ozb3_bwalk01.dat
- gym_ozb3_dead.dat
- gym_ozb3_firehado2.dat
- gym_ozb3_fumi.dat
- gym_ozb3_greaction2.dat
- gym_ozb3_guardkama2.dat
- gym_ozb3_guardpose.dat
- gym_ozb3_guardroop2.dat
- gym_ozb3_houmingf.dat
- gym_ozb3_issoku.dat
- gym_ozb3_kamae.dat
- gym_ozb3_kamaguard2.dat
- gym_ozb3_lwalk.dat
- gym_ozb3_run00.dat
- gym_ozb3_run01.dat
- gym_ozb3_rwalk.dat
- gym_ozb3_shippo.dat
- gym_ozb3_tatumaki.dat
- gym_ozb3_tobinoki.dat
- gym_ozb3_toujyou.dat
- gym_ozb3_tunoupper2.dat
- gym_ozb3_walk00.dat
- gym_ozb3_walk01.dat
- gym_ozb3_warp1.dat
- gym_ozb3_warp2.dat

## Excluded from this pack (measured — not bakeable with this FK model)
- ozb3_all_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_demo_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_hado_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_horming_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_shipo1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_tatumakiup_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
- ozb3_tunoup_teil1: 4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)
