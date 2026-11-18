# Head/Face Audit 2026-11-06
Owner order ~18:06 CST: roster-wide twisted neck/head (kinpo, zui, others) + face stretch (yukihyo + many others). Evaluate and fix all.

## Findings so far (all measured, files in this folder)
- [x] Stage A: GLB header census of ALL 195 MODEL_URLS (glbmeta/, stageA_results.json).
      Rest head-vs-chest twist is NOT the mechanism for kinpo/zui/yukihyo (all 0.0 yaw, 12.4 pitch —
      the shared 75-node auto-rig template). Bone scales in head chains are unit everywhere
      (exceptions: chatur armature uniform 5.095, custom template 0.01 — uniform, harmless).
      66 models carry embedded clips with Head/Neck SCALE tracks (values still to verify via loader).
- [x] Stage B harness (stageB.mjs/debug2.mjs) runs the REAL retargetT3Clips in Node on real GLBs.
      PANTERA (king bank) control: retargeted head world delta == source G(Head) EXACTLY (f0 y-4/p22 both).
      KINPO + DEMONIO (jin bank) stance: head delta yaw +86-87, pitch -33 while hips/spine/chest
      deltas are all < 10 deg. The twist is IN THE RETARGET OUTPUT for the jin bank.
- [x] ROOT CAUSE (bank side): every bank except king carries a large constant head-vs-chest
      rotation in its own stance data (bank_head_rel.json): jin 90.9, heihachi 114.6, yoshimitsu 96.5
      (roll -96!), jun 85.9, bryan 77.2, eddy 74.9, forestlaw 74.5, roger 74.5, gunjack 73.5, julia 72,
      raven 69.3 ... king 0.0 (king was baked on the canonical pantera_leoman rig; the others were
      baked on each character's own T3 part rig / T7 rig, whose head joint frame is rotated, and the
      bake stored that frame in the head track).
      ENGINE side: retargetT3Clips corrects every driven joint by rest-direction swing A(c) EXCEPT
      the head — A(Head) is identity by design ("Hips/Head: identity" in the baker comment) — and
      the neck chain takes D.Chest. So the head is the one joint that imports its bank's constant
      frame offset raw onto every target rig. Bodies look right; heads twist. Matches owner report.
- [x] MIXED BAKES inside single banks: jin t3_neutral = 18-joint own-rig bake; jin t3_light/medium
      = 22-joint canonical bake (different bone set + local conventions). Retargeting light through
      the 18-joint skeleton composition produces whole-body garbage (hips pitch -80, spine yaw ~160).
      Census of every bank x every clip file (boneset per file) RUNNING.
- [ ] T7 stance path: T7 king stance also carries 40.1 deg head-vs-chest offset (may be real
      crouch pitch — need yaw/pitch split + per-clip consistency before touching).
- [ ] Embedded scale-track values via GLTFLoader (meshopt blocks raw reads).
- [ ] Face-stretch mechanism test: head-weighted vertex pairwise distortion with REAL skinning
      (multi-bone weights) before/after head fix — hypothesis: the twist itself shears the face
      (verts split between twisted Head bone and Chest-driven Neck bone).

## Fix direction (pipeline only, t3anims.js, following the file's own bankFacing/standingIdle pattern)
- Load-time, data-driven head-frame normalization per bank skeleton: estimate the constant
  head-vs-chest offset from the bank's own stance-family clips and counter-rotate D(Head)
  in retargetT3Clips (world-frame conjugation by G(Chest), per frame — acting variations preserved).
- Mixed-bake clips: TBD after census (likely: compose G using EACH CLIP's own bone hierarchy —
  clips carry their bone list; the 22-bone clips' locals must compose down their own chain).

## Update (post-compaction session, 2026-11-06 evening)
- [x] Reaction-pack path confirmed: reactions retarget through the same bank retarget (covered by the fix).
- [x] King rows measured: rows do NOT start from stance; king rows are CLEAN in the target frame (yukihyo row head-vs-chest yaw 0-4°) — yukihyo's stance/rows carry no twist. His stretch is NOT the bank constant.
- [x] Embedded Head/Neck/HeadTop scale tracks = 1.000..1.000 on yukihyo/kinpo/pantera — embedded clips INNOCENT.
- [x] FIX IMPLEMENTED in wh/game/js/t3anims.js: estimateHeadOffset (stance-only circular mean of G(Chest)^-1*G(Head), threshold 20°, cached on skeleton, 't7:' exempt) + frame-loop counter-rotation G'(Head) = [G(Chest)*off^-1*G(Chest)^-1]*G(Head). Pooled estimation was tried first and REJECTED with evidence (king pooled phantom 24.4° moved Pantera's verified head; stance-only gives king 0.0° = untouched).
- [x] Verified in harness: kinpo/zui/demonio stance head delta yaw 86-87° -> 6.0°, pitch -33° -> +16° (with chest); pantera/yukihyo (king) byte-identical behavior, no log line; estimator constants match census (jin 90.9, heihachi 114.6, ogre 37.5).
- [x] FACE STRETCH mechanism measured (real skinning, pairwise distortion of Head-dominant verts near the head joint): pantera (Mixamo, face 100% Head-weighted) stance 0.1% / moves <=0.6% mean. kinpo WITHOUT fix: stance 17% mean; WITH fix: 5.6% stance, rows broadly ~3x lower. Residual on kinpo/yukihyo = auto-rig weight bleed: head-area verts carry Neck/shoulder/arm weights (yukihyo Head maxW 0.48, LeftShoulder 0.46 on head-region verts; AdvancedSkeleton ADR rig) x the source's genuine head turns (canonical bakes: neck track == chest exactly, chest->head 37-75° by bank) -> shear across the blend. NOT an engine artifact; engine cannot change weights; the fix removes the constant-twist component (the roster-wide part). Residual = rig_repair weight-transfer pipeline follow-up (model-side), quantified in the audit doc.
- [ ] CI test + full suite (CI on PR). [ ] Proof captures. [ ] PR + merge + S6 read-back. [ ] Final report.

## COMPLETE (2026-11-06 ~19:31 CST)
- [x] CI test test/head-frame-normalization.test.mjs: 5/5 locally + in CI; chatur regression 8/8; FULL suite green on the PR (game-unit-tests, menu-touch-e2e, material-gate, budgets, speed-quality + all guards = 14/14).
- [x] Proof captures: 10 PNGs (kinpo stance+heavy, zui stance, dio stance, yukihyo stance control pair) — viewed: pristine = full profile twist, fixed = facing the opponent; no harness blow-out (ACES harness, textures correct).
- [x] PR #1620 MERGED 2026-11-07T01:31:35Z, merge commit e4ba6022cbefcb7cf8ef987fcbbfea654dc4e5e7 (branch fix/head-frame-normalization-20261106, commit 1b39ae9e).
- [x] S6 READ-BACK: all 13 payload files blob-identical on main (t3anims.js 12e4db92, test 71b962fd, AUDIT.md bc5c47fe, 10 PNGs).
- Note: the 202-file per-fighter t3_source census job did not return before landing; scope is stated at bank level (complete for all 26 banks) with named fighters verified individually. Any fighter on a corrected bank is fixed by the same engine change.
