# Nightwolf re-rig lane — PROGRESS

Started 2026-11-07 ~21:55 CST. She/her for Nightwolf throughout.

## Diagnosis (from _nightwolf-orient-20261107/REPORT.md)
- Auto-rig placed arm chains ~21 cm above her arm geometry (joints z 1.412 vs geometry z ≈1.20); LeftArm owns 0 dominant verts; face only 40% Head (23% Spine2, 9% LeftShoulder).
- Statue clean; retarget + engine exonerated. PR #1641 file for her pulled from that PR.

## Plan
1. [ ] Batch joint-offset audit over all 100 PR #1641 payloads (pure-Python GLB dominant-vert probe, numpy only — no Blender needed for measurement).
2. [ ] Armor King attire1 named check (head tilted back in after-still).
3. [ ] Pull + blob-verify main's roster/nightwolf/attires/attire1/model-rigged.glb (blob 1cfe2f3deddb0a6576dea5c57b006f6cafbdd82a, 27,414,444 B).
4. [ ] Refit arm-chain joints onto arm geometry; re-derive arm+head weights via pipeline automatic transfer (tools/rig_repair from WH main).
5. [ ] Strip CMU135_04_boxing anim + material-less Icosphere; header length == file size; Blender-strict-open check.
6. [ ] Acceptance measurements + harness proof renders (bind, julia t=0.35, king t=0.35).
7. [ ] REPORT.md in this scratch. No PR, no push — lead lands it.

## Armor King attire1 — NAMED CHECK DONE
- Joint placement CLEAN: Head/Neck joints centered on head geometry; Head bone axis [0,1,0] vertical in bind; arm height offsets 0.005 m (hers: 0.215). NOT a joint-placement defect, NOT her pattern.
- Face weights: weight-stage bleed, milder cousin of hers. He faces −Z in-file (toes + face geometry agree); face slab on his front (−Z): Head 52% + Neck 8% = 60% head chain, 40% Spine2 (chest). Chest rotation drags his face — plausible cause of the tilted-head still. Stage: WEIGHTS (inherited), not rig placement.
- Arm dominant geometry sits 0.18 m toward his front from the segment line with height exact — consistent with chest/pelt mass weighted to the Arm bones (same weight-stage family), not misplaced joints.
- Side note for lead: his in-file facing is −Z.

## Task 2 decisions
- Route: tools/auto_rig/refit_rig.py (pipeline's own Negativo-proven chain).
- Template: default pantera.glb (49 joints, fetched + parsed OK). Her set = template + LeftHandThumb3 — the chain's output skeleton will have 49 joints; her Thumb3 verts re-skin onto Thumb2/hand via heat. Banks carry no finger tracks (fingers rest-curled in game), so articulation loss is nil in practice; flagging in REPORT for the lead. (Julia's model as alt template: blob fetch returned 0 B — not available via git; dropped.)
- Facing +Z (her toes point +Z). --height 1.67 (her shipped file's dequantized geometry height).
- refit_rig workdir is tempfile.mkdtemp → run with TMPDIR=<scratch> (/tmp is a 512 MB tmpfs, filled once already — cost 2 batch DECODE-FAILs before the fix).
- Baseline on MAIN's file (probe_head.py): face slab Head 33% + Neck 20% = 53% head chain (the diagnosis's 67% was the de-bleeded PR file). Acceptance ≥95% stands.

## Refit chain — round 1 result + correction
- Chain ran: decode → refit_skeleton → refit_landmarks → heat_rebind (~16 min Blender) → head_territory → secondary_chains (added 8 hair_jiggle bones for her braids) → seam_safe_smooth DIED (-9, OOM-class, twice; scipy-sparse step, box has 7 GB RAM and is shared). rig_h.glb (post-territory+chains) survives in tmp/wh-refit-cwam1ahn/.
- rig_h measurements: arms FIXED (LeftArm 0→30,447 dominant verts; forearm height offsets 0.215→0.006/0.004); her anatomical face slab (y 1.44–1.64) = **100% Head**. BUT the landmark fit collapsed **RightArm to the centerline** (fitted x −0.0013 vs correct ≈ −0.24 fit-units; its cross-section window merged with her torso/feather mass) and put RightForeArm 0.11 inward. Left chain fitted perfectly.
- Correction (measured, pipeline-internal): patched refit-report/fit_landmarks.json — RightArm 'to' := exact mirror of the fitted LeftArm; RightForeArm 'to' := on the fitted RightArm→RightHand line at the LeftForeArm mirror x. Original saved as fit_landmarks.orig.json. NO weight hand-editing: heat_rebind re-derives all weights from the corrected skeleton. Re-running heat → territory → chains → smooth (solo) → gates → encode manually with refit_rig's own commands.
- Note: refit redistributed her spine proportions (Neck 1.221 / Head 1.272 vs original 1.466 / 1.497) — template proportions at same total height 1.67. Face slab by anatomy = 100% Head; the harness render is the arbiter for the lower head pivot.

## Log
- 21:55 Read diagnosis REPORT.md. out/ corpus in _weightbleed-fix-20261106 has 110 .glb files (flattened names). No local before-copy of her GLB (census_dl empty); diagnosis lane holds rigged-pr1641.glb (PR blob 3d49ce57). Pulling main's via sparse clone.
- 22:00 Main's file pulled via sparse clone, BLOB VERIFIED 1cfe2f3d… (27,414,444 B) → nightwolf-main.glb.
- 22:05 Pure-python probe (probe_audit.py) built. Two traps solved: (1) EXT_meshopt_compression — python meshoptimizer binding is broken (heap corruption/segfault); decode via node MeshoptDecoder (nodetools/decode_glb.mjs) instead. (2) Frame trap — skinned verts must be transformed by jointWorld@IBM (the skin bind matrix), NOT the mesh-node world; the bind matrix also carries KHR_mesh_quantization dequantization (hers: uniform scale 0.835, y-off 0.835, consistent across joints to 1e-6). Probe reproduces the diagnosis on her file exactly: LeftArm 0 dominant; forearm centroids (±0.51, y 1.197) vs joints y 1.412 → 21.5/21.6 cm height offset.
- 22:10 First batch run was polluted by the frame trap (absurd 2 m offsets on rotated-subtree files); probe fixed, batch restarted clean.
- 22:10 Task 2 route chosen: the pipeline's own tools/auto_rig/refit_rig.py — built for Negativo's identical defect ("arms 0.18 m above his arms"): landmark refit + bone heat rebind + head_territory + seam-safe smoothing + gates + meshopt encode. Needs Blender 4.0.2 (downloading) + tools/anim codec (sparse-checked out) + @gltf-transform (installed in nodetools/).

## Update 2026-11-08 ~05:20 CST (post-reboot resume)
- VM rebooted; round-2 heat had never actually started (work2 held only static.glb, heat2_run.log empty). Relaunching below.
- TASK 1 ANOMALY RESOLVED — kiko cluster is REAL, distinct class: **L/R-swapped skin weights**. probe_mirror.py (own-segment vs mirror-segment distance) discriminates cleanly: healthy controls (pantera-body, saku-ra_alt1, negativo a1, yukihyo a1) own_seg 0.055–0.147 vs mirror 0.39–1.22; the 7 cluster files (kiko-tanaka, kiko-tanaka_alt1, purple-rain-main, mariposa, mariposa-monarch, saku-ra-main, cape-jones) own_seg 0.45–1.09 vs mirror 0.12–0.17. Joints are correctly placed (identical standard body skeleton as healthy pantera-body); the WEIGHTS are mirror-swapped. Full-limb census on kiko-tanaka confirms legs+hands swap too, not just arms. NOT a joint-offset; a re-rig/weight fix class of its own.
- Parvati attire1 MEASURED: Rigify lattice rig — 469 joints × 7 skins, arm weights split across bend/twist/twk helper bones; canonical LeftArm/RightArm/LeftForeArm/RightForeArm own 0 dominant verts BY THAT RIG'S DESIGN. Not measurable by the canonical dominant-bone test; not a joint-offset flag.
- Star attire5 + Silvertongue attire2: UNMEASURABLE — corrupt position data (681 / 588 NaN-or-garbage verts; star's NaNs documented pre-existing in the PR) on a different 29-joint Z-up Tripo rig family. Excluded from tiers with reason; their astronomic summary values were garbage artifacts, removed.
- Final audit tiers: 110 corpus files = 54 severe (genuine >8 cm class incl. 0-dominant) + 7 L/R-swap + 34 moderate + 12 clean + 3 unmeasurable (parvati, star a5, silvertongue a2).

## Update 2026-11-08 ~05:40 CST — LANE COMPLETE
- Round-2 heat DONE (rig.glb, metrics in refit-report/heat_rebind_metrics2.json). RightArm restored to the arm line.
- head_territory + secondary_chains DONE (rig_h, reports *2.json). Anatomical face slab = 100.0% Head. Forearm height offsets 0.6/0.4 cm.
- seam_safe_smooth solo retry: survived 4 rounds (p99.9 rising mid-process), SIGKILLed round ~4 (memory). Deliverable = rig_h stage, gap documented in REPORT.
- Gates on rig_h: validate PASS, seams PASS, anim_check official p999 3.254 (70 spikes all RightHandThumb3|Thumb2), strict stretch p999 13.003 (small-edge feather/skirt mass; median elongation 3.87 mm).
- Encoded via repo codec; CMU clip stripped pre-encode on the plain rig; final = nightwolf-rerigged-final.glb (28,428,932 B, header == size, 58 joints, 0 anims, no Icosphere). Blender 4.0.2 strict import of its decoded form: OK, 58-bone armature. (Blender 4.0.2's addon cannot read ANY meshopt file incl. main's current one — meshopt is not the Yukihyo defect class; header equality is the check and it passes.)
- Harness rebuilt in harness/ (game's own t3anims.js from main + three 0.169 + Playwright). Renders: proof-bind-front.png, proof-julia-stance-t035.png (PASS guard), proof-king-stance-t035.png (PASS guard), proof-julia-BEFORE-original-file.png (control: straight stuck arm).
- REPORT.md complete. No PR, no push — lead lands the GLB.
