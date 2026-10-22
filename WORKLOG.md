# WORKLOG — DEATHFANG build (2026-10-19/20, branch feat/deathfang-yamazaki-20261019)

Owner orders 2026-10-19 ~20:06–20:12 CDT: build DEATHFANG (all caps, one word) —
proprietary character based on Iori Yagami; keeps Iori's moves/stance/animations;
reskin as prisoner/slave to his own grief, chained/shackled, emo, Soul Eater
"NO FUTURE" face tattoo; transforms into a chained prisoner werewolf
(Free, Soul Eater, folds in). Werewolf GLB lands in a follow-up PR; base form +
moveset merged first.

## Lane 1 — moveset + wiring (done)
- `game/assets/movesets/deathfang.json`: 24 moves — Iori's full kit (10 T3-proxy
  base moves + Yami Barai + Maiden Masher from iori.json, renamed) + Oniyaki,
  Kototsuki In, Aoi Hana rekka ×3, Dokugami, Tsumagushi, Ya Otome super,
  2 throws, werewolf transform, NO FUTURE signature. Tekken inputs throughout.
- `game/js/assets.js`: `deathfang` + reserved `deathfang-werewolf` keys.
- `game/js/roster-full.js`: DEATHFANG entry (surge: NO FUTURE).
- `game/js/movesets.js`: `deathfang` added to MOVESET_IDS.
- JS syntax-checked with node --check.

## Lane 2 — attire 1 GLB (done, own-eyes rendered)
Method: SURGICAL GLB edit (no Blender re-export — the Sketchfab model's custom
Diffuse/Glossy/Emission node tree does not survive a Principled-only export).
1. `roster/deathfang/tools/df_texture_reskin.py` (Blender 4.0.2 headless):
   UV-category masks by dominant skin weight (hair red→emo black incl. a
   crimson-color catch, pants→charcoal, jacket/shirt deepened, skin paled);
   NO FUTURE tattoo drawn on the face region of the texture.
2. `roster/deathfang/tools/df_chains.py` (system python): iron chain geometry
   (torus links) built in glTF space — accessor space == joint world space,
   measured: dominant-weight vert centroids ≈ joint origins. Wrist shackles +
   5-link dangling chains, ankle shackles + 5-link inter-ankle chain, neck
   collar + 3 hanging links, 2 chest cross chains.
3. `roster/deathfang/tools/df_merge.py` (pygltflib, append-only): original
   blob untouched; reskinned texture swapped in via images[0]; 8 skinned
   chain meshes appended (JOINTS_0 100% to anchor bone; inter-ankle chain
   whole-link-per-foot), DEATHFANG_IRON material (metallic 0.9), nodes added
   under Object_10. All 59 animations + skeleton preserved byte-for-byte.
Renders (textured, own-eyes viewed): `docs/tpose-refs/deathfang/a1_front.png`,
`a1_back.png`, `a1_face.png`. Cycles CPU under xvfb (Eevee lacks libEGL on VM).

Known follow-ups: werewolf transform GLB (attire 2), tattoo legibility pass
(face is mostly hair-covered in Iori's style — tattoo sits on the forehead
band), in-game stance test of the inter-ankle chain under wide stances.

---

## 2026-10-20 — Pantera GLB repair (Idle clip + skin joints + seams)

Lane: fix/pantera-idle-clip-20261020. Tool: tools/auto_rig/repair_pantera_glb.py
(reproducible; run from tools/auto_rig). Gate: tools/auto_rig/anim_check.py.

Diagnosis (all measured, not eyeballed):
1. Idle clip Hips translations orbit a mean 8.21 m from bind — an
   exporter's scene placement baked into the clip (smooth periodic bob,
   key0 == key47, just centered in the wrong place).
2. JOINTS_0 in 8 prims (arms, boots1-3, fingers, gloveparts, pants,
   thighs) referenced L/R-mirrored joints — under any non-bind pose the
   geometry followed the opposite side's bones (the "gyro arms" knot).
   The repo already had the audited correction in pantera_fixed.glb
   (docs/qa/anim/pantera_skin_lr_fix_before_after.jpg) but the game
   wires pantera.glb (game/js/assets.js MODEL_URLS).
3. Hard 100%/100% skin seams (pants crotch L/R UpLeg, chest logo
   Spine/Spine2) tore under the Idle stance: edge-stretch p99.9 11.27.

Fixes applied to game/assets/models/pantera.glb (in place, 14 accessors,
JSON untouched, file size unchanged):
1. Idle Hips keys re-centered on bind (v' = bind + (v - mean)); the
   authored bob (max |v-bind| 0.63 m) is preserved.
2. 8 JOINTS_0 accessors transplanted byte-for-byte from pantera_fixed.glb.
3. Seam weights iteratively averaged across edges with ratio > 2.0
   (7 rounds; prims 4/13/14/17; capped at 4 influences, renormalized).

Gate after repair: ALL CLIPS PASS — Idle root dev 0.63 m (was 8.21),
edge p99.9 1.88 (gate 2.5), edge max 2.00, tearing max 0.085 m.
Run/Walk remain 2-keyframe rest-pose stubs by design: real locomotion
is the runtime Tekken 3 bank layer (game/js/t3anims.js); baking wh-anim
data into the GLB is a separate change owned by the motion-bake lane.

Same disease, NOT fixed here (flagged): steve-fox.glb (16 fighters share
it) and pantera_fixed.glb itself carry the identical broken Idle
(root 8.21 m; edge 5.82 / 6.20) — they need the same root re-center
(+ seam blend for pantera_fixed). Pre-existing cosmetic defect also
flagged: belt2/buckles prims are authored displaced at neck height
across the whole pantera model family; renders confirm they float at
the shoulders in the shipped model. Not repositioned — no source of
truth for their intended placement (see docs/RULES_NO_GUESSING.md).

## 2026-10-20 — Forward-merge of moveset-cluster-a-t8 (PR #357) into main (recovery run)
- Method: `git merge origin/main` in the lane worktree; 18 moveset JSONs resolved by semantic-union script (/tmp tooling, verifier re-checked every entry against both source versions — all OK); game/js/movesets.js resolved to main's version (branch's only functional addition, koreshi in MOVESET_IDS, already on main; branch header garble not carried over).
- ONE deletion, named per anti-clobber law 4: the branch's duplicate `koreshi` roster block in game/js/roster-full.js (comment + 2 lines, placeholder model steve-fox) removed because the merge also carries main's canonical koreshi entry (model koreshi, surge/stats/ai) — same dedupe as PR #363's kronos. Roster after: 57 entries, 57 unique ids.
- Merged counts (moves): pantera 333, phantom 405, koreshi 329, samura1 302, cyborgx 290, sakura 282, sha 281, torch 274, purplerain 263, star 260, kingtyrant 258, skull 255, kinpo 253, diablo 247, burger 246, demonio 237, awapop 299, scimitar 196 — all at/above both source versions.

## 2026-10-20 — Forward-merge of moveset-cluster-b-t7 (PR #359) into main (recovery run)
- Method: `git merge origin/main` in a dedicated worktree; the 10 conflicted moveset JSONs resolved by semantic-union script and re-verified entry-by-entry against both source versions (independent verifier: ALL OK). Contested keys keep main's entry; branch T7 entries rekeyed <key>_t7 with t7_input recorded; each file carries a forward_merge provenance block. mariposa.json is the branch's new file (223 moves, Zafina base) and lands as a pure addition; game/js/movesets.js auto-merged to the exact id union (74 ids incl. mariposa, zero duplicates, all resolve to files).
- Deletions introduced by this merge: none.
- Merged counts (moves): rave 625, mariposa-monarch 328, lili 325, slice 312, yukihyo 306, bruno 296, michiko 293, negativo 251, dio 230, thor 225 — all at/above both source versions.

# WORKLOG — Burger Kusaregedo Kit (2026-10-19)

## Task
Wire Youkai Kusaregedo's full kit into Burger per owner 2026-10-19 ~18:41 CDT.
Owner confirmed Samurai Shodown (not Onimusha) is the right source.

## Sources (NO-GUESSING compliance)
- Frame data: https://dreamcancel.com/wiki/Samurai_Shodown_VI/Kusaregedo (Tekitogate)
- Powers/story: https://snk.fandom.com/wiki/Youkai_Kusaregedo
- Research doc: ~/workspace/burger-kusaregedo/KUSAREGEDO-MOVESET.md
- All startup/active frames are real SamSho VI data (60fps -> seconds).
- Damage scaled to WH 100HP. Kusaregedo's fixed grab % preserved.

## Files
- `game/assets/movesets/burger-demon.json` (NEW): 24 moves, 8 specials. Full kit + form-mix + 2 exclusives.
- `game/assets/movesets/burger-speed-demon.json` (NEW): 12 moves, 3 specials. Quick moves.
- `game/assets/movesets/burger-the-mouth.json` (NEW): 12 moves, 3 specials. Head/bite.
- `game/js/movesets.js` (EDIT): registered 3 IDs in MOVESET_IDS.
- `game/js/roster-full.js` (EDIT): Burger `forms` block — chain base -> speed-demon -> the-mouth -> demon.
- `roster/burger/ATTIRE-SLOTS.md` (EDIT): documented per-form movesets + chain.

## Per-form distribution
- **Demon (final)**: FULL kit (7 signatures + 16 normals) + smaller-form abilities
  (demon-dash, rapid-bites, mega-chomp, head-slam, hungry-eyes, feral-rend)
  + exclusives (INFINITE HUNGER ultimate, Gaki's Feast armor stance).
- **Speed Demon**: Flying Head Butt (up/down), Quick Palm, Speed Boot, Backflip + speed kit.
- **The Mouth**: Huge Headbutt, Mega Chomp, Head Slam, Tongue Lick/Sweep, Maw of Hunger.

## Verification
- All 3 JSONs: schema_version 2, valid JSON, fighter IDs match filenames.
- `node --check` passes on both edited JS files.
- `git status`: 3 modified + 3 new, zero deletions (anti-clobber check clean).

## Follow-ups (not in this PR)
- Mini Tank form (model pulled 2026-10-19): needs its own moveset + chain slot.
- New form models (speed-demon, the-mouth) not yet wired to roster/ — Tripo pulls exist in ~/workspace/tripo-recovery/.
- Bob's full Tekken moveset for Burger base (separate lane).
- Kusaregedo animation clips: anim_ref points to samsho:kusaregedo/ — clips to be built from footage.

## 2026-10-20 ~23:00 CT — Claude: T3 bank runtime retarget (fighters no longer collapse)
Branch `claude/amazing-keller-p8644u`. Full write-up + Muse directives: `docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md`.
- Root cause: wh-anim/1 bank quaternions are local rotations of identity-rest source rigs
  (`lab/game/assets/pantera_leoman_t3real.glb`, `t3_<bank>_t3real.glb`); the game bound them raw onto
  non-identity-rest Mixamo/Biped rigs.
- `tools/anim/t3_bank_skeleton.py` (python3, numpy) → `game/assets/anim/t3/<bank>/skeleton.json` (6 banks, SHA-256 of source GLB);
  `--check`: all 3,292 channels match their source GLB (max err 8.6e-7).
- `game/js/t3anims.js` `retargetT3Clips` (port of `lab/tools/t3_motion_bake.py` retarget math) + `canonBoneName`;
  `game/js/fighter.js` `_bindT3`, T3 stance/walk/backdash/jump in idle/walk/dodge/jump states.
- Verified: headless Chromium (Playwright 1.56, SwiftShader) demo fight pantera vs rin; frames viewed;
  head-above-hips 0.43–0.52 m every sampled frame (before: Pantera pitched sideways, Demonio flat).
  Proof: `docs/proof/claude-2026-10-20/retarget/`.

---

# WORKLOG — CHARGER build (2026-10-20, branch feat/charger-blanka-replacement-20261020)

Owner order 2026-10-20 ~13:32–13:34 CDT: CHARGER replaces Blanka — "his name is
charger cause of blankas attacks and movesets will be attach to him but he's
got powers of ice and electricity". Two owner Tripo links (Attire 1 + Attire 2).

## Pulls (tools/tripo-pull, public-api strategy)
- Attire 1 `b91318ce-2ccd-43eb-8691-d675b3ee8b10` "ice monster 3d model" →
  `~/workspace/tripo-recovery/charger_attire1/` (18,005,236 B, 1 mesh, 3 textures).
- Attire 2 `f87e24eb-0c0b-4444-9409-4f4dabc0bb32` "green spiky creature 3d model" →
  `~/workspace/tripo-recovery/charger_attire2/` (17,370,960 B, 1 mesh, 3 textures).
- Transport note: the tool's urllib reads died mid-stream through this VM's
  egress proxy (IncompleteRead, reproduced 3x) while curl completed the same
  endpoint reads. The tool's own strategy/verify/manifest code ran unmodified
  via a curl-backed transport shim (`~/workspace/_wh-work/charger-scratch/
  tripo_pull_shim.py`) — same public project-detail API, no sign-in, per the
  TRIPO-PULL-TOOL law (never ask for a login; check the method).
- `tools/render-prep` validate on both: RESULT OK — all 3 textures decode per
  model (Color/ORM/NormalGL), no NaN warnings; meshopt+quantization present
  (roster ships raw like KRONOS/KORESHI; game decodes via MeshoptDecoder).

## Wiring
- GLBs copied byte-identical (sha256-verified) to
  `roster/charger/attires/attire1/model.glb` + `attire2/model.glb`;
  `roster/charger/README.md` documents sources.
- `game/js/roster-full.js`: `blanka` entry replaced by `charger` (attires
  `['charger','charger-attire2']`) + `charger-attire2` entry.
- `game/js/assets.js`: `charger` + `charger-attire2` MODEL_URLS keys added
  (`blanka` key kept — his files stay).
- `game/js/movesets.js`: `charger` added to MOVESET_IDS.
- `game/js/fighter.js`: MOVESET_MAP `charger: 'bryan'`, `'charger-attire2': 'bryan'`.
- `game/assets/movesets/charger.json`: built from `blanka.json` by
  `~/workspace/_wh-work/charger-scratch/build_charger_moveset.py` — 199/199
  moves, inputs + all non-name data field-identical (script-asserted); 46
  signature names renamed (Electric Thunder→Cryo Thunder, Rolling family→
  Frostcharge, Ground Shave Rolling→Glacier Shave Roll); map recorded in the
  JSON's `canon_rename_map` and in `RENAME-MAP.md` (CHARGER section).
- NOT deleted: `roster/blanka/`, `blanka.json`, `sf-blanka.json`, `blanka`
  code keys. Only the playable roster entry changed.

## Proof
- Front renders of both attires from render-prep copies (own-eyes verified):
  `~/workspace/your_files/charger-attire1-front-20261020.png`,
  `~/workspace/your_files/charger-attire2-front-20261020.png`.
- Node smoke test: roster module loads, `charger` + `charger-attire2` resolve,
  charger.json move count == blanka.json (199).


---

# WORKLOG — WMXIX texture remainder decode (Job 2, 2026-10-20, branch cs-gapfill/j2-wmxix-tex-remainder)

Owner order (2026-10-20 ~22:14 CDT, creation-suite gap-fill): the WMXIX
texture batch decode remainder from the wiring audit.

- New tool `customization/tools/decode_wmxix_tex_remainder.py` (pure
  Python, no Blender): parses the .tex little-endian container directory
  and decodes the first entry with the validated TPL tile math, extended
  to accept the variant TPL magic 0x0120AF30 that blocked all 426
  remaining .tex files; plus standalone TPL, TGA (PIL), TIM2 (indexed-8,
  CSM1 CLUT unswizzle, verified against the sibling TGA), and PSD
  (PIL + a PackBits RLE composite reader for the file PIL rejects).
- Batch result: 433 of 446 target entries decoded to PNG under
  `customization/parts-converted/wmxix-textures/`; CATALOG.json WMXIX
  converted textures 1,044 -> 1,477; blocked_no_tpl 426 -> 0.
  Remaining 13 proven non-textures (8 .ycg palette data, 1 build
  script.txt, 3 .ymm YOBJ meshes, 1 .tpg index) carry detail reasons.
- Unified runtime catalog regenerated with `build_suite_catalog.py`
  (total unchanged 4,523; WMXIX texture assets 1,044 -> 1,477).
  Creation-suite tests by filename: catalogs.test.js 5/5, dna.test.js 4/4.
- Full counts, per-class forensic evidence, and proof:
  `customization/parts-converted/WMXIX-TEX-REMAINDER-REPORT-2026-10-20.md`.
- Environment note: this VM intermittently denies file-write flushes
  (Errno 1, silent 0-byte truncation) — the tool verifies every write by
  read-back and retries, with a perl-pipe fallback; all 1,477 output
  PNGs re-verified on disk after the batch (0 missing, 0 invalid).

---

# WORKLOG — Doc Frank "owl" fix + backward T3 banks (2026-10-21, branch claude/amazing-keller-p8644u)

Owner: "his whole body is facing the wrong way and his head is facing the right way like a owl".

- Diagnosis team (workflow: GLB-data lane completed; runtime/live lanes hit the session limit and
  their work was redone directly). GLB lane measured all Doc Frank models: binds exact, the 90 deg
  pelvis frame is cancelled by Spine1 and is not the cause (hood attire has none and folds the same).
- Root cause: 5 T3 banks baked facing -Z while declaring +Z (bosconovitch, eddy, gunjack,
  yoshimitsu, heihachi own-rig). Independent offline check: `tools/anim/t3_bank_facing.py` (new).
- Fix, `game/js/t3anims.js` (all data-derived, generic):
  - `bankFacing()` + `turnSkeleton()`/`turnData()` in `loadT3Clips`: knee-bend cue from the bank's
    own frames; backward banks turned 180 deg about Y, Left/Right relabelled, before any clip is built.
  - `standingIdle()`: Dr. B's slot-3 "neutral" is a 15-frame fall (root 0.45 -> -0.45 m); a bank
    whose slot-3 clip drops > 1/4 hip height idles in its own guard hold, ping-pong
    (THREE.LoopPingPong via clip.userData.pingpong). Only bosconovitch triggers. The loop-point
    search over his round-start clip was tried first and rejected on sight (arms-wide stretch).
  - Floor contact in `retargetT3Clips` (`rig.contact`, `rig.floorY` from analyzeRig): no joint below
    its standing-rest height (bosconovitch/yoshimitsu root heights don't match their skeletons).
- Proof (viewed): `docs/proof/claude-2026-10-21/docfrank-facing/` — before/after renders for all
  turned banks, live fight before/after (hips 1.0 -> -0.88 m before; 0.78-0.97 m guard bob after),
  regression fights (0 page errors). Harness: tools/proof-harness/fight.mjs; old-vs-new served
  side by side (old t3anims.js on :8766) with the GLB lane's retarget_check.mjs.
- Also: `tools/moveset-merge/merge_sources.py --only` now updates only those fighters' report
  entries (an earlier `--only zui` run had replaced the 96-fighter SOURCE-MERGE report; restored,
  zui entry updated to 654 moves). `tools/auto_rig/auto_rig.py`: WH_BLENDER env override.
  `tools/auto_rig/backends/gamerig_backend.py`: arm/hand fit computed from a template snapshot
  (palm/finger subtree was left 0.23 m below the hand) and bone heat retried on coarser proxies
  with a triangle-based decimate target (zui-attire1 heat failed for every vertex before).
- Not done here: Phantom and Sam-ur-a1 models have ZERO skinned meshes (unrigged statics, on main
  since 2026-10-18) — queued for the auto-rig pass with Zui/Diablo/Rave.

---

# WORKLOG — T3 bank facing root-cause fix (2026-10-22, model-quality lane)

## Root cause (the user's "decrypted backwards")
`lab/tools/t3_to_gltf.py` `import_fighter` and `lab/tools/t3_motion_bake.py`
`T3Space` chose each bank's forward direction from the HEAD-MESH centroid
("muzzle leads"). On characters whose head/hair mass sits behind the face,
this picked backwards, baking 5 of 17 T3 animation banks facing -Z:
bosconovitch (-179.5°), eddy (-178.6°), gunjack (149.9°), heihachi (137.7°),
yoshimitsu (155.1°) — measured with tools/anim/t3_bank_facing.py, the offline
twin of the runtime's bankFacing() knee check in game/js/t3anims.js.
The game patched it at load (turn 180° about Y + Left/Right relabel per bank);
this fix gets it right at the source instead.

Related (separate): the k-NN weight pipeline (tools/auto_rig/backends/
knn_transfer.py) has no automatic facing alignment — facing is a manual
--rotate-y. See the model-quality lanes' reports.

## Fix
1. `lab/tools/t3_to_gltf.py`, `lab/tools/t3_motion_bake.py`: facing heuristic
   replaced with the KNEE-BEND cue (knees are anatomical and never lie):
   lateral = shoulder line (hip line fallback for partial KMDs like heihachi);
   forward = the candidate with positive total knee offset from the hip-ankle
   midline. Head-centroid kept only as a fallback when knees give no signal.
   Validated on all 15 available KMD+stance pairs: positive knee scores
   everywhere, reproduces the 12 good bakes, corrects the 5 bad ones.
2. The 5 already-baked banks corrected OFFLINE with the exact runtime
   transform (t3anims.js turnSkeleton/turnData): game/assets/anim/t3/
   {bosconovitch,eddy,gunjack,heihachi,yoshimitsu}/ — skeleton.json (18 joints
   each), all 30 t3_*.json clips each, rows.pack.json (647/208/152/111 rows;
   heihachi has no pack). Bones L/R-relabeled in place, quats conjugated
   (x,y,z,w)->(-x,y,-z,w), root_t (x,y,z)->(-x,y,-z).
3. Runtime needs NO change: bankFacing() now measures knees-forward on all 17
   banks and the turn becomes a no-op (kept as a data-driven safety net).

## Proof
tools/anim/t3_bank_facing.py before → after:
- bosconovitch -179.5° → 0.5°, eddy -178.6° → 1.4°, gunjack 149.9° → -30.1°,
  heihachi 137.7° → -42.3°, yoshimitsu 155.1° → -24.9°. All 17 "ok", none
  TURNED. (Residual angles within the ±61° untouched band, same as anna/lei.)
- Pack integrity: bone lists L/R-symmetric, quats unit-norm after conjugation.

## Files
- lab/tools/t3_to_gltf.py (facing heuristic)
- lab/tools/t3_motion_bake.py (T3Space facing heuristic)
- game/assets/anim/t3/{bosconovitch,eddy,gunjack,heihachi,yoshimitsu}/
  skeleton.json, t3_*.json (30 each), rows.pack.json (4 banks)

---

## 2026-10-21 — Pantera skin-weight re-derivation (live model + Attire 1)

Lane: fix/pantera-weights-20261021. Tool: tools/auto_rig/reskin_pantera_weights.py
(reproducible; run from tools/auto_rig). Gates: tools/auto_rig/anim_check.py,
tools/auto_rig/validate.py.

### Wiring confirmed (step a)
- Live key `pantera: 'assets/models/pantera.glb'` (game/js/assets.js MODEL_URLS).
- Attire 1 = the same file: game/js/attires.js ATTIRE_VARIANTS['pantera'][0] =
  { model: 'pantera', label: 'ATTIRE 1' }. So "live Pantera" and "Pantera
  Attire 1" are the SAME GLB: game/assets/models/pantera.glb (7,625,912 bytes,
  sha256 2626d231a6aaff694117a55183171ad9c11f45a40eb3054afa52ab8dc55f6b6a).
  One fix covers both. (pantera_alt1.glb is a legacy T7 reskin NOT in the
  current attire ladder — out of scope.)

### Diagnosis (measured, not eyeballed — step c)
Per-region dominant-joint dump on the live file (11,376 skinned verts):
- R/L FOREARM: only 13.7%/13.8% weighted to ForeArm; 47-49% to Hand,
  36-38% to Spine/Spine1. (User: "forearm down through hands: stretching".)
- L HAND: 80.7% LeftHand, 17% to Spine/Spine1 (torso-glue; user: "hand
  weighted to the tail" — the tail hangs off the pelvis/back).
- WAIST (0.98<y<1.12): 0% Hips; 62% to Left/RightUpLeg, 36% Spine.
  (User: "from waist down: stretching".)
- TAIL (443 verts, z<-0.15): 26% LeftLeg, 26% RightLeg, 12% each foot,
  22% UpLegs — 0% Hips/Spine. Tail tears whenever legs move oppositely.
- THIGH/SHIN: 30-35% weighted one joint too distal (thigh→Leg, shin→Foot).
- IBMs verified consistent (max err 2.6e-7); skeleton itself is fine.
- pantera_fixed.glb (2026-10-20 L/R transplant source) carries the SAME bad
  WEIGHTS_0 — the transplant fixed joint indices only, not values.

### Fix (pipeline-level, step d — NO hand-painted weights)
New script tools/auto_rig/reskin_pantera_weights.py re-derives ALL
JOINTS_0/WEIGHTS_0 in place (skeleton, IBMs, animations, materials untouched):
1. k-NN (k=4, inverse-distance) from steve-fox.glb — same 49-joint Mixamo
   skeleton, clean weights (92%+ forearm/shin/bicep), same -Z facing/T-pose.
2. Side-constrained matching (|x|>3cm ⇒ same-side donor verts only).
3. Tail rule: smoothstep blend from k-NN at base to rigid Hips at tip.
4. Anatomical side correction: opposite-side influences mirrored + merged.
5. Seam blend (repair_pantera_glb.py method) until anim_check gate passes.
Result: R forearm 13.7%→99.9%, L forearm 13.8%→97.4%, waist Spine 36%→73%,
shins 62%→90-93%, tail 100% Hips-weighted. anim_check: all 4 clips PASS
(Idle p99.9 edge stretch 1.97 < 2.5 gate; was failing at 14.81 pre-blend).

### Validation (step e)
- anim_check.py: Idle/Run/TPose/Walk all PASS.
- validate.py: valid_gltf/skinned_mesh/bones_present true (height_ok false —
  pre-existing: validate measures mesh 0 prim 0 only, a 202-vert accessory).
- tools/auto_rig/tests: 7/7, all passed, 3/3 pass (1 skip: missing Blender e2e GLB).
- packages/creation-suite node tests: 6/6, 4/4, 4/4 pass (the `node --test test/`
  directory form fails on a Node CLI module-resolution quirk; individual files pass).
- In-game: proof-harness fight pantera vs demonio captured before/after;
  frames viewed. Before: forearms/hands stretch, legs crumple. After: model
  loads, fight runs, no collapse.

### Files (no deletions)
- game/assets/models/pantera.glb (weights re-derived; 7,625,912 bytes)
- tools/auto_rig/reskin_pantera_weights.py (new, reproducible pipeline)
- WORKLOG.md (this entry)

### Flags for coordinator
- SHARED CODE: none changed. The fix is a new Pantera-specific script + data.
  knn_transfer.py / apply_skin.py untouched.
- DONOR NOTE: pantera.glb is the k-NN donor for saku-ra, waterfall, charger,
  armor-king, scimitar (2026-10-21 batch). They were rigged from the BAD
  weights and likely inherit the forearm/waist/tail symptoms — the root-cause
  lane should re-run those transfers against this fixed file.
- pantera_alt1.glb (legacy, not in attire ladder) still has old weights.

## Doc Frank feet fix (2026-10-21/22, branch fix/docfrank-feet-20261021)

User report (verbatim): "Bosco/Doc Frank — really close, but both feet stick
out to the side instead of forward on all his models. Fix that; I don't know
if the feet are twisted or backwards. Everything else is pretty close."

### Diagnosis (two distinct causes, verified by measurement)

**Cause A — animated models (retarget data bug, shared stage):**
All 5 Doc Frank roster entries animate on the bosconovitch T3 animation bank.
That bank's `game/assets/anim/t3/bosconovitch/skeleton.json` carried a
degenerate `foot_tip`: Left ≈ +90°, Right ≈ −109° (sideways). Produced by
`tools/anim/t3_bank_skeleton.py`'s "centroid of foot-part verts" heuristic
applied to Bosconovitch's blobby 27-vert T3 foot parts. `t3anims.js`
`retargetT3Clips` swings every target foot to that vector, baking ~±60°
symmetric duck feet into every frame.
- Proof: Node harness running the game's real `t3anims.js`:
  doc-frank.glb + bosconovitch bank stance @40% → Left +62.8°, Right −53.6°.
  Same model + jin bank (sane foot_tip) → +5.5°/+11.3° (forward). Model data
  is fine; bank data was the cause.

**Cause B — static Tripo models (geometry bug, per-model):**
wowomomo (attire2/base), wowomomo-big, hood-big each have ONE foot modeled
sideways (PCA: one foot ~84° from lateral, other ~1–8°). The wowomomo *base*
Tripo pull has it too — a Tripo generation defect in the source asset, not
repo-introduced. frankenstein-base and frankenstein-big (both meshopt) have
BOTH feet sideways (PCA yaw ~90° both). Confirmed by Blender 4.0.2 renders
(viewed).

### Fix

**A (shared stage — FLAG FOR COORDINATOR):**
- `tools/anim/t3_bank_skeleton.py`: foot_tip computation now keeps the part
  centroid when its yaw agrees with the WH-Canonical-22 template toe within
  60° (good banks regenerate byte-identical), else uses the template toe
  `(0,−0.08,±0.21)` rotated into the bank frame, scaled by ankle height.
  Rationale: clips were baked for the canonical rig, so foot_tip must be the
  canonical toe, not the T3 part centroid.
- `game/assets/anim/t3/bosconovitch/skeleton.json`: surgical 6-number edit to
  foot_tip → canonical toe, forward +Z, 21° down. (Full tool re-run reverted:
  would have clobbered the offline 2026-10-22 facing-fix.)
- Validation: probe now gives Left −8.4°, Right +35.0°; source's own stance
  feet are Left −9.2°, Right +32.7° — retarget faithful within ~2°. The 35°
  turnout is Bosconovitch's real stance, not a bug.

**B (static geometry — 5 models):**
Rotated sideways foot(s) ~90° about ankle (Y axis) to forward, using
gltf-transform 4.1.1 + meshoptimizer 0.22.0 (industry-standard stack).
POSITION and NORMAL both rotated. Blender 4.0.2 renders viewed before/after.
- `roster/doc-frank/attires/attire2/base/model.glb` (wow): left foot −90°
- `roster/doc-frank/attires/attire2/transformed/model.glb` (wow-big): left −90°
- `roster/doc-frank/attires/attire3/transformed/model.glb` (hood-big): left −90°
- `roster/doc-frank/attires/attire4/base/model.glb` (frank-base): both (±90°)
- `roster/doc-frank/attires/attire4/transformed/model.glb` (frank-big): both
- `roster/doc-frank/attires/attire1/post-transform/model.glb` (doc-big):
  verified OK (feet forward), no change.
- Validation: extent ratios (Z > X = forward) confirm all fixed. Blender
  renders viewed.

### Files (no deletions)
- tools/anim/t3_bank_skeleton.py (foot_tip method)
- game/assets/anim/t3/bosconovitch/skeleton.json (foot_tip 6 numbers)
- 5 GLBs listed above (foot geometry)
- WORKLOG.md (this entry)

### Flags for coordinator
- SHARED STAGE CHANGED: `tools/anim/t3_bank_skeleton.py` foot_tip method.
  The parallel k-NN root-cause lane should be aware. The change is
  conservative (good banks regenerate byte-identical).
- The bosconovitch bank foot_tip fix affects ALL fighters using that bank,
  not just Doc Frank. This is correct — the bank data was wrong.
- attire1/pre-transform/model.glb (unwired, T7 bone names) cannot be
  retargeted by canonBoneName (returns null for 'leg right ankle'). Not
  in-game, not fixed.
- doc-frank-wowomomo and doc-frank-frankenstein model-rigged.glb files exist
  on main but are UNWIRED (assets.js points to unrigged model.glb). Not fixed.

---

## 2026-10-22 — Master roadmap PASS 1: moveset stub audit (audit only, no wiring)

Branch: `audit/moveset-stub-pass1-20261022`. Doc:
`docs/MOVESET-STUB-AUDIT-2026-10-22.md`.

**Method:** a move counts as WIRED iff the game's own fight logic
(`fighter.js::_moveRowAction`) can play its real T3 row clip — `t3_row` /
`anim_t3` resolving through `SOURCE_TO_BANK` into the fighter's bank with
the row baked in `game/assets/anim/t3/<bank>/rows.pack.json`. Bank
resolution replicates `bankIdFor`; the loader gate (`_fetchOne` → null
when `index.json` lacks the id) is replicated too. Audit-only: nothing
wired, nothing removed.

**Headline:** 59 roster fighters, 34,247 base moves — 16,948 wired
(49.5%), **17,299 unwired (50.5%)**. Strings 13% wired (492/3,656),
specials 8% wired (133/1,579). Only byou clears 90% wired base moves.

**Gap classes found:**
- A. Moveset never loads: `charger-attire2` (selectable roster fighter,
  file exists, not in `index.json`), `deathfang-werewolf` (DEATHFANG
  transform target, not in `index.json`), `doc-frank-frankenstein`
  (roster id, no file at all).
- B. No anim bank: `ryuji` — 103 moves, 0 wired, kofxv refs only, no KOF
  teardown exists.
- C. Bank mismatch: `zen` 639/639 unwired (FIGHTER_BANK override 'julia'
  vs heihachi-based data — one-line suspect); doc-frank trio 365
  gunjack→bosconovitch leftover rows; gyou/kai/tou/nightwolf/awapop/
  rave/kingtyrant partials (jin/heihachi/xiaoyu rows vs fighter bank).
- D. No row wiring: 11,888 moves (68.7% of unwired) — worst:
  kronos-attire2 (1,708), koreshi (936), rave (798), phantom (652).
- E. Rows referenced but never baked in rows.pack.json (T8/T7-merged
  rows; jin_soul, retsu, rin, demonio-bloodline-ember, demonio-winged…).
  `heihachi_ownrig` ships no rows.pack.json at all.
- F. Declared proxies (5): deathfang, koreshi, ryuji-rock,
  deathfang-werewolf, cainelias.
- G. Stub markers: samura1 `qcf+1+2` (rocket-fist PLACEHOLDER anim),
  demonio-winged ×3 placeholder anims, ryuji.json TODO canon note.
- H. 36 orphan moveset files (not roster, not form targets).
- 2,757 moves carry `t3_source` values the game can't resolve
  (sf6/sfv/sf4/original/urban-reign/doa-bass) — never wireable as-is.

**Teardown coverage per game:** T3 100% (20 banks decoded, 16 baked +
heihachi_ownrig unbaked; forestlaw/gon/kuma/law/ogre decoded, never
baked); T7 King-only; T6 blocked (DATA401 encrypted); TTT2 blocked
(not extracted); DOA/VF community movelists only; SF Akuma-pattern
translations; KOF none; Urban Reign no move banks.

**Recommended wiring order for follow-up passes:** P0 loader/index
one-liners (charger-attire2, deathfang-werewolf, zen bank fix,
doc-frank-frankenstein decision) → P1 bank-mismatch remaps → P2 bake
missing rows → P3 row assignment (11,888) → P4 proxies → P5 ryuji
source decision → P6 orphans.

**Flags for coordinator:** `MOVESET_IDS` in `game/js/movesets.js` is
stale relative to `index.json` (nothing outside movesets.js reads it;
live loader keys off roster ids + index). The wiring passes should
treat `index.json` as the source of truth and may want to regenerate it
(it currently gates out 2 ids that have files).

## 2026-10-22 — BACKWARDS BODY PARTS AUDIT: Julia (nightwolf) facing fix

**Task:** Per-part facing audit (parent task: "BACKWARDS BODY PARTS AUDIT"). User reported Julia's shins/feet/torso/head face backwards while thighs/arms look correct.

**Method:** Built `tools/model-audit/per_part_facing.py` — measures each body part's absolute facing (+Z/-Z) from mesh geometry:
- Head: nose = farthest vert from head joint (p95)
- Torso: chest = max protrusion from spine axis (p95)
- Foot: toe joint direction + mesh reach verification
- Shin: calf = bulk (median) protrusion from shin axis, upper third only (avoids boots)
- Thigh/upperarm/forearm/hand: weaker cues, reported but not flagged
- Consensus: majority vote of high-conf parts

**Julia finding:** NO per-part flips. All parts face -Z consistently (head -Z, torso -Z, foot -Z via toe joint, shin calf +Z posterior = correct for -Z, thigh ~symmetric, arms T-pose correct). The skeleton is fully consistent (all W@IBM = identity, yaw 0).

**Root cause:** Whole-model facing error, not per-part. `game/assets/models/model-facing.json` recorded nightwolf as +Z, but the mesh faces -Z (Blender rest renders from +Z show her back; nose/chest/toes all -Z). The game therefore did NOT turn her, so in-game she faces away. Viewed from the game's +Z front, the asymmetric parts (head, torso, shins, feet) read as "backwards" while symmetric parts (thighs, arms) "look correct" — exactly the user's report.

**Fix:** `model-facing.json`: nightwolf +Z → -Z. The game now turns her 180° at instance creation (designed mechanism, `assets.js` line 709). No rig change needed (no rig defect exists).

**Proof:** `docs/proof/2026-10-22/julia-facing/julia_before_after.png` — before (from +Z: her back, parts called out) / after (her front, as the game will show).

**Roster audit (full):** Ran the checker on all 57 game models. Genuine per-part flips found (to be fixed fighter-by-fighter):
- michiko.glb (+Z): head -Z, thighs -Z (head+thighs flipped)
- star.glb (+Z): head -Z, thighs -Z (head+thighs flipped)
- pantera-body.glb (-Z): head +Z (head flipped)
- pantera_alt1.glb (-Z): head +Z (head flipped)
- yukihyo.glb (+Z): torso -Z (torso flipped)
- zafina.glb (+Z): shins +Z (calf anterior = backwards)
- lili.glb, thor.glb: one thigh each asymmetric (needs visual verification)
- Many models flag shins (cue noise from boots; verified OK on nightwolf)

Full per-fighter list in the task report.
## 2026-10-22 — Character-select dedup audit + stage-select audit (branch fix/select-dedup-20261022)

Owner directive (verbatim): "attires ladder into their fighter — an attire must NOT appear as its own
separate selectable model UNLESS the user explicitly said so." Concrete example: "there is a Phantom
model AND a separate Yoshimitsu model on the select screen — Yoshimitsu is supposed to ladder into
Phantom's attires, not stand alone."

Audit method: enumerated all 58 FULL_ROSTER cards (game/js/roster-full.js), cross-checked each
against ATTIRE_VARIANTS (game/js/attires.js), model lineage, ATTIRE-SLOTS.md files, RENAME-MAP.md,
CANON.md/ROSTER.md, and WORKLOG directives. Stage side: enumerated all 58 STAGES ids across the
5 tiers in game/js/stages.js and checked for dupes, missing assets, and miswired selection.

Folded (card removed, model re-homed into the fighter's ladder — nothing deleted):
- jin_soul (JIN, the Blade Soul, Yoshimitsu base/moveset) -> PHANTOM ladder as
  { model: 'steve-fox', label: 'JIN · BLADE SOUL' }. Canon: Phantom is the vessel of JIN (CANON.md).
- demonio-bloodline-ember, demonio-winged, demonio-human -> DEMONIO ladder (already listed).
- doc-frank-wowomomo, doc-frank-hood, doc-frank-frankenstein, doc-frank-machine-shop ->
  DOC FRANK ladder (already listed, owner Tripo-first order kept).
- charger-attire2 -> CHARGER (new 'charger' ladder; no key existed, Attire 2 would've been lost).
- kronos-attire2 -> KRONOS ladder (already listed).
Roster: 58 -> 48 selectable cards.

Behavior preserved:
- Doc Frank's single `transform` -> per-model `forms` map: each folded attire keeps its own old
  transform target (wowomomo->wowomomo-big, hood->hood-big, frankenstein->frankenstein-big;
  doc-frank-big default stays big->big no-op). Fighter/main.js already consume `forms`.
- Tiers switched from positional slices to SOUL_IDS/MAIN_IDS membership (game/js/roster-full.js,
  game/js/select-screen.js) — folding cards no longer shifts fighters between tiers.
  getFighter default fixed to find 'pantera' by id (was FULL_ROSTER[9]).
- tripo-fighters.json: 9 folded ids dropped (matches tripo_fighters.py regeneration).

Wiring fixes (broken entries found by the audit):
- ATTIRE_VARIANTS 'mariposa'/'dxmmii' keys matched no fighter id/model (orphaned ladders) ->
  re-keyed to the roster card ids 'mariposa-monarch'/'dxmmii-patchwork'. Contents/order kept
  (Mariposa: "ONE character ... Never split into two characters", roster/mariposa/ATTIRE-SLOTS.md).
- MODEL_URLS was missing 'zen-attire1' (Zen's select preview showed MODEL PENDING),
  'zen-tentacle', 'zen-oversoul', 'zen-spirit' (his transform targets) — all four GLBs exist;
  key names per roster/zen/ATTIRE-SLOTS.md. Added to game/js/assets.js.

Kept as-is (correct single-card pattern, ladder keyed by own id): baek-master-white (KEVIN), zui.

Flagged for the owner (no directive found, not guessed):
- Stage select shows the No Mercy arenas TWICE: 'WRESTLING' tier (17 OBJ stages, ids nm-arena-*)
  and 'WWF NO MERCY' tier (17 GLB stages, ids nm-*). 15 same-arena overlaps; all 34 assets exist;
  selection wiring is correct (unique ids, no X-loads-Y). Needs owner call: keep both tiers or
  retire one (recommend the GLB tier — per-arena dims/cameras/interior lighting).

Proof: tools/roster/dedup_audit.mjs — 36 checks, all pass (folds, tier partition, ladder wiring,
stage id uniqueness, transform preservation). Run: node tools/roster/dedup_audit.mjs.
Visual before/after captures of the select screen need a live browser (not available to this
session) — delegated to the parent agent.
## Doc Frank feet — root-cause completion (2026-10-22, branch fix/docfrank-feet-rootcause-20261021)
Independent measured diagnosis (game's real `game/js/t3anims.js` path, stance
clip @40%): the sideways splay lived in the bosconovitch bank's `foot_tip`
reference (stored +92°/−109° off forward, from the generator's foot-part
centroid heuristic) — not the clip decode (foot bones −6°/+36°), not the
retarget (posed == source exactly on the healthy jin bank), not the models
(all rest at 0°). Full write-up: `docs/fixes/docfrank-feet-rootcause-20261021/DIAGNOSIS.md`.
PR #508 fixed the tool's derivation and the six foot_tip numbers, but on a
skeleton.json that had been pre-turned offline (file note: "2026-10-22 facing
fix … turned 180 about Y + L/R relabelled offline"). The clips were never
turned, so the runtime stopped turning the bank and the retarget paired
turned joint names with unturned clip tracks: measured A1 +44.6°/−16.6° vs
source +29.6°/−7.1°, Leo man +55.7° with feet floating (ankle y 0.18–0.29).
This change: regenerated all 17 banks with the merged fixed tool
(`tools/anim/t3_bank_skeleton.py`). 11 banks byte-identical; 6 change —
bosconovitch (joints back to the GLB-native frame the clips were baked in,
runtime bankFacing turn applies again; foot_tip = corrected canonical toe)
and anna/bryan/eddy/julia/yoshimitsu (foot_tip only, same defect class).
No runtime code, no GLB edits, no deletions.
After (same harness): source FK −6.0°/+35.9°; Doc Frank A1 posed
+3.8°/+27.5°; Leo man +11.8°/+23.6°; Attire 3 base +2.7°/+28.2° — feet
forward on all his rigged models at once; the right-foot turnout is
Bosconovitch's own stance in the decoded motion. Proof renders (viewed):
`docs/fixes/docfrank-feet-rootcause-20261021/before_after_stance.png`,
`docs/fixes/docfrank-feet-rootcause-20261021/sidebyside_original_vs_posed.png`.
