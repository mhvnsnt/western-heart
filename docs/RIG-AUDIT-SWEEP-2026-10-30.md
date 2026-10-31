# Rig audit sweep — roster GLBs (B3, 2026-10-30)

Tool: `tools/auto_rig/backends/skin_audit.py` on main (10 gates: skinned, weight sums,
unweighted verts, JOINTS_1, dead major joints, contamination, proportions, folded
chains, joints inside mesh, feet planted). Every GLB under `roster/` was enumerated
from main's tree (247 files, sizes verified against current blob SHAs).
Files were fetched one at a time, audited, and deleted before the next fetch.

## Counts

- Total roster GLBs enumerated: 247
- PASS: 1
- PASS-AFTER-FIX: 3
- FAIL: 39
- AUDIT-ERROR: 19
- DEFERRED-FOR-SIZE: 20
- NOT-YET-AUDITED: 165
- Audited (any verdict except NOT-YET-AUDITED and DEFERRED-FOR-SIZE): 62

## Reading the verdicts

- FAIL with skinned=False: the file carries no skin at all (unrigged source/static
  models — most plain model.glb and source/ files). Not a weight defect; there is
  nothing for weight cleanup to fix until the model is rigged.
- AUDIT-ERROR ValueError (offset / buffer size): the file is EXT_meshopt_compression
  (gltfpack-style); skin_audit reads physical buffer offsets and cannot decode it.
  A decode path exists (gltf-transform copy, proven on Baek attire1), after which
  the audit can run — subject to vert count (Baek attire1 decoded is 1,622,503
  verts and the pure-Python audit timed out at 280 s / 150 s caps on this VM).
- DEFERRED-FOR-SIZE: single file over ~45 MB, per the lane's scratch-disk rule.
- PASS-AFTER-FIX: failed as shipped, fixed by rigfix in the Baek PR (B3 step 1).

## Per-GLB table (roster order)

| GLB | Size (B) | Verdict | Detail (failing gates / key metrics) |
|---|---|---|---|
| roster/armor-king/attires/attire1/model-rigged.glb | 487,688 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (293368) |
| roster/armor-king/attires/attire1/model.glb | 397,876 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/awa-pop/attires/attire2/model-rigged.glb | 30,118,392 | AUDIT-ERROR | ValueError: buffer is smaller than requested size |
| roster/awa-pop/attires/attire2/model.glb | 20,834,332 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/awa-pop/awa-pop-attire-1.glb | 20,583,812 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/baek/attires/attire1/model-rigged.glb | 23,796,696 | AUDIT-ERROR | failed=tool-limit: EXT_meshopt_compression unreadable by skin_audit (accessor offset beyond BIN chunk); decoded via gltf-transform = 1622503 verts/73 joints, audit >280s timeout on decoded form |
| roster/baek/attires/attire1/model.glb | 8,473,628 | FAIL | failed=skinned=False verts=None joints=None (unskinned source model) |
| roster/baek/attires/master-white/baek-master-white-rigged.glb | 570,500 | PASS-AFTER-FIX (was FAIL) | failed_before=no_dead_joints verts=3990 joints=50 sum_bad=0 unweighted=0 joints1=False dead_major_before=LeftHand;RightHand dead_n_before=14 contam_pct_before=0.087 contam_verts_before=21 / cleanup 128 pruned/707 revived/7 filled -> contam_pct_after=0.003 dead_major_after=none (fix PR branch rigfix/baek-wh100-b3-20261030, staged) |
| roster/baek/attires/master-white/baek-master-white.glb | 469,640 | FAIL | failed=skinned=False (unskinned source model) |
| roster/baek/attires/master-white/model-custom.glb | 579,492 | PASS-AFTER-FIX (was FAIL) | failed_before=no_dead_joints verts=4000 joints=50 sum_bad=0 unweighted=0 joints1=False dead_major_before=LeftHand;RightHand dead_n_before=14 contam_pct_before=0.086 contam_verts_before=21 / cleanup 134/758/7 -> contam_pct_after=0.003 dead_major_after=none |
| roster/baek/attires/master-white/model-kevin-diff.glb | 1,124,404 | PASS-AFTER-FIX (was FAIL) | failed_before=no_dead_joints verts=5551 joints=50 sum_bad=0 unweighted=0 joints1=False dead_major_before=LeftHand;RightHand dead_n_before=14 contam_pct_before=0.083 contam_verts_before=24 / cleanup 217/700/7 -> contam_pct_after=0.001 dead_major_after=none |
| roster/blanka/attires/attire1/model.glb | 4,561,072 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/bruno/attires/attire1/source/bruno-a1-jack-sparrow.glb | 24,432,052 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/bruno/attires/attire1/source/bruno-a1.glb | 24,432,052 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/bruno/attires/attire2/source/bruno-a2-dreadlocked-warrior.glb | 23,980,788 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea-rigged.glb | 31,669,920 | AUDIT-ERROR | ValueError: buffer is smaller than requested size |
| roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea.glb | 23,980,788 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/buffalo-bill/attires/attire1/source/buffalo-bill-a1-render.glb | 14,265,296 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/buffalo-bill/attires/attire1/source/buffalo-bill-a1.glb | 20,391,004 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/buffalo-bill/attires/attire2/source/buffalo-bill-a2-render.glb | 14,820,616 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/buffalo-bill/attires/attire2/source/buffalo-bill-a2.glb | 21,441,832 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/buffalo-bill/attires/attire3/model-rigged.glb | 30,836,224 | AUDIT-ERROR | numpy.linalg.LinAlgError: Singular matrix |
| roster/buffalo-bill/attires/attire3/model.glb | 21,120,912 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire1/model-rigged.glb | 19,860,460 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (19733532) |
| roster/burger/attires/attire1/model.glb | 20,712,948 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire2/model.glb | 20,316,404 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire3/model.glb | 20,833,904 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire4/model.glb | 20,955,312 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire5/model.glb | 22,340,904 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire6/model.glb | 20,908,984 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/burger/attires/attire7/model.glb | 21,954,676 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/cain-elias/attires/attire1/model.glb | 21,711,300 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/cain-elias/attires/attire2/model.glb | 21,921,892 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/charger/attires/attire1/model-rigged.glb | 17,451,836 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (17324912) |
| roster/charger/attires/attire1/model.glb | 18,005,236 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/charger/attires/attire2/model-rigged.glb | 16,594,452 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (16467528) |
| roster/charger/attires/attire2/model.glb | 17,370,960 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/chordz/attires/attire1/model-rigged.glb | 28,860,080 | AUDIT-ERROR | numpy.linalg.LinAlgError: Singular matrix |
| roster/chordz/attires/attire1/source/chordz-a1-rigged.glb | 28,849,992 | AUDIT-ERROR | ValueError: buffer is smaller than requested size |
| roster/chordz/attires/attire1/source/chordz-a1.glb | 21,913,940 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/chordz/transformations/final/source/chordz-final-cutter-who-strums.glb | 24,748,736 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/chordz/transformations/phase1/source/chordz-p1-edward-scissorhands.glb | 20,735,052 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/chordz/transformations/phase2/source/chordz-p2-blade-spikes.glb | 21,751,348 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/cyborg-x/attires/attire1/model-rigged.glb | 86,192,130 | DEFERRED-FOR-SIZE |  |
| roster/deathfang/attires/attire1/model.glb | 16,333,308 | PASS | failed=- verts=67755 joints=73 sum_bad=0 unweighted=0 joints1=False dead_major= dead_n=25 contam_pct=0.011 contam_verts=59 prop_flags=0 folded=0 outside=0 |
| roster/deathfang/attires/attire2/model.glb | 17,397,904 | FAIL | failed=no_contamination,joints_inside_mesh verts=66442 joints=73 sum_bad=0 unweighted=0 joints1=False dead_major= dead_n=25 contam_pct=0.358 contam_verts=1389 prop_flags=0 folded=0 outside=2 |
| roster/deathfang/attires/attire3/model.glb | 13,625,408 | FAIL | failed=no_dead_joints verts=9807 joints=79 sum_bad=0 unweighted=0 joints1=False dead_major=_rootJoint;Bip001_00;Bone L Shoulder_041;Bone R Shoulder_058 dead_n=4 contam_pct=0.0 contam_verts=0 prop_flags=0 folded=0 outside=0 |
| roster/demonio/attires/attire1/model.glb | 28,872,600 | AUDIT-ERROR | ValueError: buffer is smaller than requested size |
| roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb | 25,698,348 | FAIL | failed=no_dead_joints,no_contamination,proportions_ok verts=14498 joints=50 sum_bad=0 unweighted=0 joints1=False dead_major=LeftUpLeg;LeftLeg;RightUpLeg;RightLeg dead_n=4 contam_pct=37.875 contam_verts=5530 prop_flags=1 folded=0 outside=0 |
| roster/demonio/attires/human/model-rerig.glb | 28,737,644 | AUDIT-ERROR | ValueError: buffer is smaller than requested size |
| roster/demonio/attires/human/model-rigged.glb | 19,377,980 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (19250964) |
| roster/demonio/attires/human/model.glb | 56,667,288 | DEFERRED-FOR-SIZE |  |
| roster/demonio/attires/winged-devil/model-rigged.glb | 19,010,652 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (18883216) |
| roster/demonio/attires/winged-devil/model.glb | 55,823,720 | DEFERRED-FOR-SIZE |  |
| roster/diablo/attires/attire1/model-rigged.glb | 22,100,148 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (21972800) |
| roster/diablo/attires/attire1/model.glb | 22,770,984 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/diablo/attires/attire2/model.glb | 22,503,560 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/dio/attires/attire1/source/dio-a1-fantasy-demon.glb | 21,600,980 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/dio/attires/attire1/source/dio-a1-jade-god-rigged.glb | 28,618,288 | AUDIT-ERROR | numpy.linalg.LinAlgError: Singular matrix |
| roster/dio/attires/attire1/source/dio-a1-jade-god.glb | 21,600,980 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/dio/transformation/source/dio-transformation-million-eyes.glb | 23,422,084 | FAIL | failed=skinned=False verts=None joints=None sum_bad=None unweighted=None joints1=None dead_major= dead_n=0 contam_pct=None contam_verts=None prop_flags=0 folded=0 outside=0 |
| roster/doc-frank/attires/attire1/post-transform/model-rigged.glb | 25,225,856 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (25200432) |
| roster/doc-frank/attires/attire1/post-transform/model.glb | 57,113,408 | DEFERRED-FOR-SIZE |  |
| roster/doc-frank/attires/attire1/pre-transform/model.glb | 2,510,960 | FAIL | failed=no_dead_joints,proportions_ok verts=10442 joints=178 sum_bad=0 unweighted=0 joints1=False dead_major=root ground;Hips;RightShoulder;RightArm;arm right wrist root;LeftShoulder;LeftArm;arm left wrist root;RightLeg;LeftLeg dead_n=10 contam_pct=0.067 contam_verts=24 prop_flags=2 folded=0 outside=0 |
| roster/doc-frank/attires/attire2/base/model-rerig.glb | 28,273,076 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (28209952) |
| roster/doc-frank/attires/attire2/base/model-rigged.glb | 18,189,772 | AUDIT-ERROR | ValueError: offset must be non-negative and no greater than buffer length (18061904) |
| roster/doc-frank/attires/attire2/base/model.glb | 41,184,968 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v1-thindisc.glb | 76,117,932 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v4.glb | 76,321,008 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/doc-frank/attires/attire2/dome-fix/model-dome-glass-v5.glb | 76,449,144 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/doc-frank/attires/attire2/dome-fix/model-dome-glass.glb | 76,140,792 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/doc-frank/attires/attire2/transformed/model-rigged.glb | 23,887,648 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire2/transformed/model.glb | 41,797,212 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire3/base/model.glb | 29,489,092 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire3/transformed/model-rigged.glb | 24,759,980 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire3/transformed/model.glb | 40,614,276 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/base/model-rerig.glb | 28,518,140 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/base/model-rigged.glb | 19,160,088 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/base/model.glb | 21,524,900 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/transformed/model-rerig.glb | 29,703,496 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/transformed/model-rigged.glb | 24,964,156 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/attire4/transformed/model.glb | 22,946,508 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb | 2,221,852 | NOT-YET-AUDITED |  |
| roster/doc-frank/attires/machine-shop/doc-frank-machine-shop.glb | 2,511,208 | NOT-YET-AUDITED |  |
| roster/dorowani/attires/attire1/source/dorowani-a1-crimson-cheeks-rigged.glb | 30,982,692 | NOT-YET-AUDITED |  |
| roster/dorowani/attires/attire1/source/dorowani-a1-crimson-cheeks.glb | 18,776,972 | NOT-YET-AUDITED |  |
| roster/dxmmii/attires/attire1/model-rigged.glb | 32,846,444 | NOT-YET-AUDITED |  |
| roster/dxmmii/attires/attire1/model.glb | 60,345,304 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/dxmmii/attires/attire2/model.glb | 54,101,760 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb | 403,316 | NOT-YET-AUDITED |  |
| roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork.glb | 290,569 | NOT-YET-AUDITED |  |
| roster/gyou/attires/spirit-form/model.glb | 17,034,224 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/model.glb | 26,875,868 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/source/fiery_humanoid_3d_model.glb | 0 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/transformations/flame-eternal/model.glb | 26,512,240 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/transformations/godflame/model.glb | 27,642,692 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/transformations/guardian/model.glb | 26,211,972 | NOT-YET-AUDITED |  |
| roster/gyou/spirit-body/transformations/level1/model.glb | 26,133,012 | NOT-YET-AUDITED |  |
| roster/iori/attires/attire1/model.glb | 12,304,580 | NOT-YET-AUDITED |  |
| roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb | 25,657,736 | NOT-YET-AUDITED |  |
| roster/king-tyrant/attires/attire1/model.glb | 19,405,988 | NOT-YET-AUDITED |  |
| roster/king-tyrant/attires/attire2/model.glb | 19,292,836 | NOT-YET-AUDITED |  |
| roster/king-tyrant/attires/attire3/model.glb | 18,586,860 | NOT-YET-AUDITED |  |
| roster/king-tyrant/attires/attire4/model.glb | 19,157,944 | NOT-YET-AUDITED |  |
| roster/kinpo/attires/attire1/model-intake.glb | 29,960,676 | NOT-YET-AUDITED |  |
| roster/kinpo/attires/attire1/model-rigged.glb | 19,495,752 | NOT-YET-AUDITED |  |
| roster/kinpo/attires/attire1/model.glb | 20,304,060 | NOT-YET-AUDITED |  |
| roster/kinpo/attires/attire2/model.glb | 18,389,124 | NOT-YET-AUDITED |  |
| roster/koreshi/attires/attire1/model-rigged.glb | 24,694,684 | NOT-YET-AUDITED |  |
| roster/koreshi/attires/attire1/model.glb | 25,414,700 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire1/model-rerig.glb | 29,355,124 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire1/model-rigged.glb | 18,483,400 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire1/model.glb | 19,128,636 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire2/model-rerig.glb | 29,240,856 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire2/model-rigged.glb | 19,691,544 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire2/model.glb | 20,392,600 | NOT-YET-AUDITED |  |
| roster/kronos/attires/attire3/model.glb | 21,485,380 | NOT-YET-AUDITED |  |
| roster/kuma-replacement/attires/attire1/source/kuma-replacement-a1.glb | 32,333,152 | NOT-YET-AUDITED |  |
| roster/kuma/attires/attire1/source/kuma-a1.glb | 32,333,152 | NOT-YET-AUDITED |  |
| roster/lili/attires/noir-gala/lili-noir-gala.glb | 19,552,956 | NOT-YET-AUDITED |  |
| roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb | 90,429,536 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/mariposa/attires/monarch/mariposa-monarch.glb | 22,127,910 | NOT-YET-AUDITED |  |
| roster/mariposa/attires/slot2/model.glb | 21,221,888 | NOT-YET-AUDITED |  |
| roster/michiko/attires/attire1/model-rigged.glb | 29,567,824 | NOT-YET-AUDITED |  |
| roster/michiko/attires/attire2/model-rigged.glb | 30,748,576 | NOT-YET-AUDITED |  |
| roster/mina-ashido/attires/attire1/model-rerig.glb | 2,121,260 | NOT-YET-AUDITED |  |
| roster/mina-ashido/attires/attire1/model-rigged.glb | 12,146,544 | NOT-YET-AUDITED |  |
| roster/mina-ashido/attires/attire1/model.glb | 4,387,244 | NOT-YET-AUDITED |  |
| roster/miruko/attires/attire1/model-rerig-textured.glb | 4,119,856 | NOT-YET-AUDITED |  |
| roster/miruko/attires/attire1/model-rerig.glb | 2,570,352 | NOT-YET-AUDITED |  |
| roster/miruko/attires/attire1/model-rigged.glb | 14,674,608 | NOT-YET-AUDITED |  |
| roster/miruko/attires/attire1/model.glb | 5,648,588 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire1/source/negativo-a1-futuristic-superhero.glb | 23,252,660 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire1/source/negativo-a1-rigged.glb | 31,143,220 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire1/source/negativo-a1.glb | 23,252,660 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire2/source/negativo-a2-rigged.glb | 35,072,400 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire2/source/negativo-a2-sci-fi-armored-suit.glb | 27,085,484 | NOT-YET-AUDITED |  |
| roster/negativo/attires/attire2/source/negativo-a2.glb | 27,085,484 | NOT-YET-AUDITED |  |
| roster/nightwolf/attires/attire1/model.glb | 21,870,928 | NOT-YET-AUDITED |  |
| roster/panda/attires/attire1/source/aotsuki-a1-rigged.glb | 28,516,692 | NOT-YET-AUDITED |  |
| roster/panda/attires/attire1/source/aotsuki-a1.glb | 19,208,680 | NOT-YET-AUDITED |  |
| roster/pantera/attires/classic/pantera-classic.glb | 7,625,916 | NOT-YET-AUDITED |  |
| roster/pantera/attires/crimson-rage/pantera-attire5-crimson.glb | 14,675,572 | NOT-YET-AUDITED |  |
| roster/pantera/attires/leomon/model.glb | 4,414,284 | NOT-YET-AUDITED |  |
| roster/pantera/attires/leomon/tail/pantera_tail.glb | 28,360 | NOT-YET-AUDITED |  |
| roster/pantera/attires/leopard-king/model-refit.glb | 32,679,076 | NOT-YET-AUDITED |  |
| roster/pantera/attires/leopard-king/model-rigged.glb | 81,620,772 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/pantera/attires/leopard-king/model.glb | 23,362,216 | NOT-YET-AUDITED |  |
| roster/pantera/attires/p2-wired/pantera-attire4-p2.glb | 14,548,052 | NOT-YET-AUDITED |  |
| roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb | 7,434,348 | NOT-YET-AUDITED |  |
| roster/pantera/pantera_rigged.glb | 709,992 | NOT-YET-AUDITED |  |
| roster/pantera/tail-rig/pantera_body.glb | 7,207,428 | NOT-YET-AUDITED |  |
| roster/pantera/tail-rig/pantera_tail.glb | 28,360 | NOT-YET-AUDITED |  |
| roster/parvati/attires/attire1/model-rigged.glb | 30,860,048 | NOT-YET-AUDITED |  |
| roster/parvati/attires/attire1/model.glb | 23,541,928 | NOT-YET-AUDITED |  |
| roster/phantom/attires/attire1/model-rerig.glb | 29,340,456 | NOT-YET-AUDITED |  |
| roster/phantom/attires/attire1/model-rigged.glb | 21,448,812 | NOT-YET-AUDITED |  |
| roster/phantom/attires/attire1/model.glb | 21,957,208 | NOT-YET-AUDITED |  |
| roster/props/stage-accessories/tripo_demo_model.glb | 8,971,340 | NOT-YET-AUDITED |  |
| roster/purplerain/attires/attire1/model-rerig.glb | 28,465,008 | NOT-YET-AUDITED |  |
| roster/purplerain/attires/attire1/model-rigged.glb | 18,179,944 | NOT-YET-AUDITED |  |
| roster/purplerain/attires/attire1/model.glb | 18,982,308 | NOT-YET-AUDITED |  |
| roster/rahkasa/attires/attire1/model-rigged-textured.glb | 2,361,776 | NOT-YET-AUDITED |  |
| roster/rahkasa/attires/attire1/model-rigged.glb | 9,817,884 | NOT-YET-AUDITED |  |
| roster/rahkasa/attires/attire1/model.glb | 3,706,016 | NOT-YET-AUDITED |  |
| roster/ryuji-rock/attires/attire1/model-rigged.glb | 29,138,548 | NOT-YET-AUDITED |  |
| roster/ryuji-rock/attires/attire1/model.glb | 18,872,720 | NOT-YET-AUDITED |  |
| roster/ryuji-rock/attires/attire1/source/cornerstone-a1.glb | 18,872,720 | NOT-YET-AUDITED |  |
| roster/ryuji-rock/attires/attire1/source/ryuji-rock-a1-tattooed-man.glb | 18,872,720 | NOT-YET-AUDITED |  |
| roster/sakura/attires/attire1/model-rerig.glb | 28,382,684 | NOT-YET-AUDITED |  |
| roster/sakura/attires/attire1/model-rigged.glb | 18,561,660 | NOT-YET-AUDITED |  |
| roster/sakura/attires/attire1/model.glb | 19,347,460 | NOT-YET-AUDITED |  |
| roster/sam-ur-a1/attires/attire1/model-rerig.glb | 30,667,524 | NOT-YET-AUDITED |  |
| roster/sam-ur-a1/attires/attire1/model-rigged.glb | 22,318,188 | NOT-YET-AUDITED |  |
| roster/sam-ur-a1/attires/attire1/model.glb | 7,449,416 | NOT-YET-AUDITED |  |
| roster/scimitar/attires/attire1/source/scimitar-a1.glb | 24,166,404 | NOT-YET-AUDITED |  |
| roster/silvertongue/attires/attire1/model-rigged.glb | 33,223,348 | NOT-YET-AUDITED |  |
| roster/silvertongue/attires/attire1/model.glb | 23,872,756 | NOT-YET-AUDITED |  |
| roster/silvertongue/attires/attire2/model-improved.glb | 36,078,536 | NOT-YET-AUDITED |  |
| roster/silvertongue/attires/attire2/model.glb | 23,430,592 | NOT-YET-AUDITED |  |
| roster/silvertongue/attires/spy-debut/silvertongue-spy-debut.glb | 14,971,672 | NOT-YET-AUDITED |  |
| roster/skull/attires/attire1/model-rerig.glb | 33,398,296 | NOT-YET-AUDITED |  |
| roster/skull/attires/attire1/model-rigged.glb | 24,005,452 | NOT-YET-AUDITED |  |
| roster/skull/attires/attire1/model.glb | 24,678,364 | NOT-YET-AUDITED |  |
| roster/slice/attires/attire1/model-rigged.glb | 29,245,236 | NOT-YET-AUDITED |  |
| roster/slice/attires/attire1/model.glb | 18,884,292 | NOT-YET-AUDITED |  |
| roster/slice/attires/attire2/model.glb | 52,403,356 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/star/attires/attire1/model.glb | 19,717,000 | NOT-YET-AUDITED |  |
| roster/star/attires/attire2/model.glb | 18,441,084 | NOT-YET-AUDITED |  |
| roster/star/attires/attire3/model.glb | 18,649,660 | NOT-YET-AUDITED |  |
| roster/star/attires/attire5/model-improved.glb | 34,875,032 | NOT-YET-AUDITED |  |
| roster/star/attires/attire5/model.glb | 19,077,152 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire1/source/theory-a1-render.glb | 14,749,152 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire1/source/theory-a1.glb | 22,369,448 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire2/source/theory-a2-render.glb | 13,460,620 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire2/source/theory-a2.glb | 18,773,404 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire3/source/theory-a3-render.glb | 14,389,256 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire3/source/theory-a3.glb | 20,769,628 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire4/source/theory-a4-render.glb | 15,511,084 | NOT-YET-AUDITED |  |
| roster/theory/attires/attire4/source/theory-a4.glb | 21,511,628 | NOT-YET-AUDITED |  |
| roster/thor/attires/attire1/model-rerig.glb | 30,869,328 | NOT-YET-AUDITED |  |
| roster/thor/attires/attire1/model-rigged.glb | 20,721,672 | NOT-YET-AUDITED |  |
| roster/thor/attires/attire1/model.glb | 21,459,020 | NOT-YET-AUDITED |  |
| roster/thor/attires/attire2/model.glb | 24,147,212 | NOT-YET-AUDITED |  |
| roster/torch/attires/attire3/source/torch-a3-bald-eagle.glb | 19,409,480 | NOT-YET-AUDITED |  |
| roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb | 7,053,488 | NOT-YET-AUDITED |  |
| roster/tsuyu-asui/attires/attire1/model-rigged.glb | 16,375,536 | NOT-YET-AUDITED |  |
| roster/tsuyu-asui/attires/attire1/model.glb | 5,800,644 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire1/model-rigged.glb | 30,366,268 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire1/model.glb | 20,967,888 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire2/model-rigged.glb | 29,067,968 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire2/model.glb | 19,846,172 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire3/model-rigged.glb | 28,999,692 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire3/model.glb | 19,614,052 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire4/model-rigged.glb | 29,990,708 | NOT-YET-AUDITED |  |
| roster/vainabel/attires/attire4/model.glb | 20,336,888 | NOT-YET-AUDITED |  |
| roster/vega/attires/attire1/model.glb | 1,624,744 | NOT-YET-AUDITED |  |
| roster/vixen/attires/attire1/model-rigged-noplane.glb | 13,896,480 | NOT-YET-AUDITED |  |
| roster/vixen/attires/attire1/model-rigged.glb | 14,653,404 | NOT-YET-AUDITED |  |
| roster/vixen/attires/attire1/model.glb | 41,676,940 | NOT-YET-AUDITED |  |
| roster/waterfall/attires/attire1/model-rigged.glb | 17,316,348 | NOT-YET-AUDITED |  |
| roster/waterfall/attires/attire1/model.glb | 18,028,208 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb | 33,174,092 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire1/source/yukihyo-a1.glb | 22,766,764 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride-rigged.glb | 33,257,868 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire2/source/yukihyo-a2-bobcat-pride.glb | 23,162,356 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king-rigged.glb | 32,100,272 | NOT-YET-AUDITED |  |
| roster/yukihyo/attires/attire3/source/yukihyo-a3-tiger-king.glb | 23,220,700 | NOT-YET-AUDITED |  |
| roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb | 5,840,076 | NOT-YET-AUDITED |  |
| roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb | 6,271,368 | NOT-YET-AUDITED |  |
| roster/zangief/attires/attire1/model-rigged.glb | 10,082,112 | NOT-YET-AUDITED |  |
| roster/zangief/attires/attire1/model.glb | 20,090,176 | NOT-YET-AUDITED |  |
| roster/zen/attires/attire1/model-rigged.glb | 29,237,496 | NOT-YET-AUDITED |  |
| roster/zen/attires/attire1/model.glb | 57,367,520 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/oversoul/model-rigged-original.glb | 89,960,556 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/oversoul/model-rigged.glb | 21,025,188 | NOT-YET-AUDITED |  |
| roster/zen/oversoul/model.glb | 57,381,932 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/spirit/model-rigged-original.glb | 86,010,820 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/spirit/model-rigged.glb | 17,786,892 | NOT-YET-AUDITED |  |
| roster/zen/spirit/model.glb | 54,385,012 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/tentacle/model-rigged-original.glb | 92,268,096 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zen/tentacle/model-rigged.glb | 21,280,892 | NOT-YET-AUDITED |  |
| roster/zen/tentacle/model.glb | 58,606,064 | DEFERRED-FOR-SIZE | single file over ~45 MB scratch rule; not fetched |
| roster/zui/attires/attire1/model-rigged.glb | 31,930,816 | NOT-YET-AUDITED |  |
| roster/zui/attires/attire1/model.glb | 20,699,580 | NOT-YET-AUDITED |  |
| roster/zui/attires/attire2/model.glb | 22,441,284 | NOT-YET-AUDITED |  |
| roster/zui/imports/base_v1.glb | 23,311,408 | NOT-YET-AUDITED |  |

## What the audited range shows (66 of 247, roster order through doc-frank)

- Only ONE shipped rig passed all 10 gates as-is: deathfang attire1 model.glb
  (contamination 0.011%). The three Baek master-white rigs passed after the B3 step-1 fix.
- Most plain model.glb / source files are unskinned (FAIL skinned=False): they are
  intake sources, not playable rigs, and weight cleanup has nothing to act on.
- 19 of 66 are AUDIT-ERROR, in two classes: (a) EXT_meshopt_compression files the
  audit cannot decode (ValueError on buffer offsets) — the single biggest blocker
  class; a decode stage (gltf-transform copy, proven) must land before these rigs
  can even be measured; (b) singular inverse-bind matrices (buffalo-bill attire3,
  chordz attire1) — a degenerate joint in the bind pose, a skeleton-stage defect.
- Worst measured weight defect in the whole audited range: demonio bloodline-ember
  at 37.875% contaminated weight mass (5,530 verts), with both leg chains dead
  (LeftUpLeg/LeftLeg/RightUpLeg/RightLeg) and one proportion flag.

## Recommended fix order (worst contamination first, measured FAILs only)

1. roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb — 37.875%
   contamination, dead leg majors, 1 proportion flag. Weight cleanup first (prune +
   leg revival), then re-audit; the proportion flag is skeleton-stage and may keep
   the gate red after weights are fixed — that remainder must be reported, not hidden.
2. roster/deathfang/attires/attire2/model.glb — 0.358% contamination (1,389 verts)
   plus 2 joints outside the mesh (skeleton-stage; cleanup alone will not pass it).
3. roster/baek game-file twin: game/assets/models/baek.glb — 0.087%, dead Hands;
   the identical cleanup to the landed roster fix (128/707/7) applies; owned by
   whichever lane owns game assets, flagged in docs/handoffs/RIGFIX-BAEK-2026-10-30.md.
4. roster/deathfang/attires/attire3/model.glb — dead majors are foreign-named
   (_rootJoint, Bip001_00, Bone L/R Shoulder): rigfix was RUN on it in this lane and
   revived 0 verts (the revival territory map is WH-canon names) and validate hard
   checks fail, so it is NOT a weight-cleanup fix; it needs a skeleton rename /
   retemplate stage first. No fix is claimed for it here.
5. roster/doc-frank/attires/attire1/pre-transform/model.glb — dead majors plus
   proportion flags on a 178-joint skeleton; skeleton-stage review before cleanup.
6. The meshopt class (19 AUDIT-ERROR in the audited range, more expected in the
   un-audited range): land a decode stage in the pipeline (decode, audit, cleanup,
   then a shipping decision on re-encode vs decoded) — until then these rigs are
   unmeasurable, which is itself a 100%-readiness blocker.
7. Singular-IBM rigs (buffalo-bill attire3, chordz attire1): bind-pose repair stage.

Next after Baek, per this order: demonio bloodline-ember (item 1).
