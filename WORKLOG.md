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
## 2026-10-22 — loadspeed lane: menu load speed (worker 4 of 4)
Owner: "we need to make the menus look a little cleaner and load a little faster because they take forever to load..."
AUDIT (tools/loadbench/ — Node harness replaying each transition's fetch
sequence with 6-way parallelism + V8 parse timing; localhost = lower bound):
- T1 boot→menu: 43 files, 2.00 MB JS, ~330ms + ~105-210ms parse. All 39 JS
  modules (incl. every fight system) parsed before first paint.
- T1b boot async: 13 files, 0.39 MB (7 real-moveset JSONs ~300KB + index...).
- T2 menu→select: 4 base GLBs = 26.13 MB fired the instant select opened
  (~21s of pipe saturation on 10 Mbps) — the "takes forever".
- T3 select→stage: 41 thumb PNG requests (3.25 MB) + 17 that 404'd.
- T4 card tap→preview: 17-22 MB Tripo GLB per tap; superseded taps kept
  downloading in the background, stealing the new tap's bandwidth.
TEKKEN TECHNIQUES PULLED IN (from teardown/):
- Tekken 3 BNS "index first, records on demand" (tekken3/docs/TEKKEN3-ARCHITECTURE.md):
  new game/js/lazy.js — fighter/movesets/t3anims/modes/heartmind/episodes/
  transform-cinematic stream via import() on first use, warmed during idle.
  Boot graph 39 → 34 files (−0.22 MB JS before first paint).
- Background streaming behind menus: real-moveset JSONs moved boot→startFight;
  base-model warm moved select-open→requestIdleCallback lane (0 bytes blocking).
- Priority lanes: loadModels rewritten as abort-aware fetch + parseAsync;
  card taps abort superseded preview downloads and preempt the idle lane.
- Urban Reign VGS single-atlas UI (urban-reign/UI-SYSTEM.md): 41 stage thumbs
  → game/assets/stages/thumbs/atlas.png + atlas.json; 41 requests → 2.
- game/js/loadperf.js: boot→menu / menu→select / select→stage /
  highlight→preview marks (window.__loadperf.summary()).
AFTER (same harness): T1 38 files/1.78 MB; T1b 3 files/0.05 MB;
T2 0 blocking bytes (24.07 MB idle lane, custom base skipped when absent);
T3 2 files/3.34 MB; T4 aborts + full-pipe. Verified: node --check ×8,
import-graph trace, Node harness vs real served GLBs (fetch/parse/ingest,
abort, dedup, idle warm, lazy module caching), atlas coverage 41/58 stages
(17 thumb-less keep swatch fallback = old onerror behavior).
Inputs untouched. Select grid untouched (worker 1).
Full writeup: docs/research/menu-load-speed-2026-10-22.md.

## 2026-10-22 — Engine decision deep research (Claude session, branch claude/amazing-keller-p8644u)

Owner: "WebGL and Three.js are permanently stripped ... Godot 4 native mobile ... Or even whatever's
better than that ... based on research, deep research", judged on this build, direct APK (no store),
what each engine costs when the game sells, roster more than 36 fighters.

- Method: five parallel research agents (Godot 4.7/4.8; Unity 6 vs Unreal 5.8; open-source engines;
  fighting-game engine ecosystem; repo migration constraints from a local repo scan), then one report
  writer over the five notes. Web sources are linked inline; repo facts link to commit e3ae81b76.
- Output: `docs/ENGINE-DECISION-2026-10-22.md` (recommendation: stay on Godot, 4.3 -> 4.7.x now, 4.8
  when stable; $0 at any sales level; signed arm64 APK from Linux CI). Notes:
  `docs/research/engine-2026-10-22/*.md`.
- Roster count from the repo scan: 58 FULL_ROSTER entries / 49 display names / 50 model keys.
- Unverified items are listed in the report's last section. No Godot binary in this container, so
  the Lab tests were not re-run.

## 2026-10-22 — BATCH-RIG SWEEP, batch 1: awa-pop attire2 (DoggByte subagent)

Owner directive: EVERY static/unrigged model in the roster gets rigged in ONE sweep.
Parent refinements applied: (1) proof needs BIND + IDLE STANCE + ANIMATION (T-pose alone
insufficient — the Julia backwards-shins case); (2) identity canon: Rave = Kiko Tanaka =
Ghost (one fighter), Mary Posa OVER Zafina, Doc Frank = Bosco, Yoshimitsu ladders into
Phantom; Tripo-first display order (Pantera A1 sole exception).

### Enumeration (current main c4be0d1, verified via GLB header scan)
- 114 unique wired files (119 MODEL_URLS keys): 28 already rigged (*-rigged.glb),
  1 rewire-only (`burger-demon` -> existing burger a1 model-rigged.glb),
  26 TRUE STATICS (verified skins=0), 1 missing (ryuji-rock — blocked, needs owner's Tripo link).
- Full list: ~/workspace/fix2/BATCHRIG-ENUMERATION.md
- 23 dense Tripo (~1M verts) + 3 light (10-12k verts). Zen's spirit body NOT FOUND on disk
  (searched WORKLOG, roster/, intake-stage/, game/assets/models/) — needs location from coordinator.

### Batch 1: awa-pop attire2 (dense Tripo, 1,009,108 verts)
- Tool: tools/auto_rig/rig_tripo_static.py (GameRig heavy path, Blender 4.0.2).
- Result: PASS. Proxy heat (9 unweighted / 14k proxy verts), 681 fixed on full mesh (0.07%).
  smooth_weights: round 0 p99.9 = 1.24 (gate 2.5) — SMOOTH_OK, no edges above threshold.
  validate.py: PASS. anim_check (CMU boxing): p999 1.24.
- Proof: bind renders (front/back/side, viewed — clean), CMU clip renders, stance proof
  via tools/auto_rig/stance_proof.py (T3 nina bank: neutral stance + walk, foot-yaw check).
- Output: roster/awa-pop/attires/attire2/model-rigged.glb, wired to `awa-pop-attire2` key.

### Pipeline fixes (in this batch)
- tools/auto_rig/rig_tripo_static.py: added `--python-exit-code 1` to Blender invocations.
  Blender 4.0 does NOT propagate Python exceptions to the exit code by default; a failed
  Blender step silently continued to smoothing (found on blanka pilot).
- tools/auto_rig/rig_tripo_static.py: add ~/workspace/tools/syslibs/{egl,gl} to
  LD_LIBRARY_PATH when present (this VM). render_poses.py crashed with missing libEGL.so.1.
- NEW tools/auto_rig/stance_proof.py: T3 stance/walk proof (world-delta retarget, same math
  as t3anims.js retargetT3Clips + bankFacing correction). Renders stance front/side + walk
  mid; reports foot yaw in stance (backwards-feet check). Pose-and-render (no keyframing)
  for speed on dense meshes.

### Failure case: blanka (light, 10,321 verts)
- GameRig direct bone-heat FAILED: 2,100/10,321 verts unweighted (20%). p999 52.76,
  mesh tears in stance. NOT SHIPPED. Needs k-NN from donor or blender-heat backend.
- pantera crimson-rage + p2 (11k verts) likely same — will try k-NN from pantera.glb.

### Provenance
- Input: roster/awa-pop/attires/attire2/model.glb (Tripo pull, on main).
- Donor clip: assets/free-pull-1/cmu-mocap/fighting/135_04.bvh (CMU, on main).
- Bank: game/assets/anim/t3/nina/ (awapop -> nina per fighter.js bankIdFor override).

## 2026-10-22 — SmutBase intake sweep (DoggByte subagent)

Standing order: every SmutBase model in `~/workspace/browser_downloads/` gets
pulled into the repo and wired up. 15 downloads intaken this round.

**Landed in-repo (this + 2 follow-up PRs):**
- `docs/SMUTBASE-INTAKE-QUEUE.md` — the living queue + manifest (all 15 models,
  hashes, per-model notes, next steps).
- `roster/rahkasa/intake/RahkasaV1.1.blend` — four-armed female, user's
  Oversoul spirit-body pick (Eastern Mind canon).
- `roster/mina-ashido/intake/`, `roster/miruko/intake/`, `roster/tsuyu-asui/intake/`
  — Rigify/IK .blends + textures, original names kept so `//` relative texture
  paths stay linked.
- `game/assets/stages/pink-narwhal/` — arena asset (NOT a character). Open
  question: is this the club/DJ base (b8ada591) from CLUB-ARENA-PLAN.md?
  Needs a Blender look before the arena lane builds on it.
- `game/assets/materials/fishnet/` — fishnet material (RenCeifer), shared
  material for the customization suite.

**Staged in workspace (over the 95MB blobs-API limit / third-party code —
registered in the queue doc, not committed):**
- `~/workspace/fix2/lily/` — Lily donor, 2.6GB extracted (rig/skeleton donor
  for the female roster, user-approved body reference).
- `~/workspace/fix2/smutbase-source/{cydney,nyoka,parvati,vixen}/` — 541MB /
  557MB / 596MB / 985MB .blends. Cydney: size up breasts/ass at rig time.
  Vixen: needs a full Tekken-notation moveset (not her source game's inputs).
- `~/workspace/fix2/smutbase-source/movie-maddness/` — 929MB .blend, contents
  unidentified, NOT intaken as a character.
- `~/workspace/fix2/smutbase-source/tools/{fluidpainter-nsfw,buildabod-male,buildabod-female}/`
  — Blender addons (third-party code stays out of the repo tree per owner law).

**Notes:** Nyoka.rar downloaded twice, byte-identical (md5 e16869e3…),
extracted once. Miruko, Tsuyu, movie-maddness + 3 addon zips were not on the
queue list — intaken anyway. Still incoming: SmutBase 22968842 (camel-toe
check at intake: removable vs painted-on), 91fca296, 0b8ceb43, c278fcf4.
`tools/tripo-intake/` does not apply (Tripo GLB pulls only); Blender rig lane
owns the next step. Blender is not installed on this VM.

## 2026-10-22 — Torch Attire 2 "Red demon" wire-in (Muse subagent lane)

- PULLED the owner's Tripo link (2026-10-21 ~22:40 CDT,
  7f8c7874-de2a-438f-a84f-744d1eef21e9) with `tools/tripo-pull/tripo-pull.py`
  ONLY. The pull first failed 14x: the egress proxy severed every urllib
  response from api.tripo3d.ai mid-body (IncompleteRead at 3-80 KB) while
  curl completed the same GET in ~1.5 s (diagnosed read-only; API code 0,
  link valid, never a login issue). Fixed at the source in tripo-pull:
  IncompleteRead is now retryable and both the GET and download paths fall
  back to a curl transport. Installed copy + this repo copy patched.
- Raw statue: 18,006,604 B, sha256
  52e6840dbc07ec670a75514ffa4252c4bf497292399e2c28e490e4e3450a99c7,
  1,029,809 verts, 3 embedded textures, unrigged. Archived in release
  `torch-a2-tripo-20261021` (asset digest verified == local sha256).
- Facing measured on the decoded mesh before rigging: foot-vs-shin cue
  +0.055 on X, -0.005 on Z — toes point +X; rigged with `--facing +X`.
- Rigged via `tools/auto_rig/rig_tripo_static.py` (the PR #570-patched
  intake) onto the 73-joint GameRig template. Report + gate renders:
  `docs/proof/claude-2026-10-22/auto-rig-torch-a2/`.
- Wired as Attire 2: `game/js/assets.js` MODEL_URLS `torch-tripo-a2`,
  `game/js/attires.js` picker ladder (1 Valkyrie of Flame / 2 Red demon /
  3 Anna Base fallback). Attire 1 untouched; her roster default stays
  `torch-tripo-a1`. Name + owner description recorded verbatim in
  `CANON.md` and `roster/torch/ATTIRE-SLOTS.md`.
- Proof render (own eyes): `torch-a2-reddemon-front-20261021.png`.
- Resume addendum (2026-10-22, second lane): the wrapper run OOM-died
  (137) three times in the clip bake, so the ship model was produced by
  the identical gamerig backend run without the optional donor clip
  (manual-backend-noclip.sh, wait-gated to a zero-Blender window;
  BACKEND EXIT 0, heat clean first proxy — 23,942 proxy verts, 0
  unweighted), then the wrapper's own finisher steps (finish-rig.sh):
  validate PASS (missing_bones []), pose renders, meshopt encode to
  28,530,756 B. smooth_weights exited "no animations to evaluate
  against" — no smoothing applied. Full deviations in the PR body.

---

# WORKLOG — Character-select dedup, Mariposa/DXMMII ladder completion (2026-10-22, worker 3/4 of select overhaul)

Owner instruction (verbatim): "all of the character slots need to be fixed to
where it's no duplicates showing it's no duplicate images showing and no
duplicate fighters only duplicates will be like the ladders of the attires of
you know the Tekken characters coming later after the proprietary characters
in the attire list"

## Situation found
The working snapshot this lane started from predated main: the 9 duplicate
select entries (DEMONIO x4, DOC FRANK x5, CHARGER x2, KRONOS x2) were ALREADY
removed on main at e8562339a5df ("48 selectable fighters", owner rule
2026-10-22: attires ladder, never stand alone as selectable cards). Rebased
onto main instead of re-applying — no clobber of the Torch/Doc-Frank
Tripo-first ladder reorders or the Zen forms work that landed meanwhile.
Remaining gaps closed by this lane (all per the slot maps + display-order law):

## Changes (data/wiring only — select-screen.js untouched)
- game/js/roster-full.js: 'mariposa-monarch' default model ->
  'mariposa-butterfly-default' (her owner-designated Slot 1, 2026-10-19);
  'dxmmii-patchwork' default model -> 'dxmmii-tripo' (his Slot 1 Tripo
  Default). Entry ids deliberately KEPT (EPISODES, HEARTMIND_STORIES,
  MOVESET_MAP, moveset files, portraits keyed by them; Fighter._movesetId =
  charData.id so renaming would silently switch moveset files).
- game/js/attires.js: 'mariposa-monarch' ladder corrected to slot-map order —
  Butterfly Default / Tripo / Monarch / Tekken Zafina back-slot (was missing
  Slot 1 and the Zafina ladder-back; 'mariposa-slot2' dropped, byte-identical
  to 'mariposa' per roster/TRIPO-REGISTRY.md). 'dxmmii-patchwork' ladder
  corrected — Tripo Default / Patchwork DJ / Blockhead (was leading with the
  retired wooden-dummy 'dxmmii' base).
- game/js/assets.js: new MODEL_URLS keys 'mariposa-butterfly-default'
  (roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb)
  and 'dxmmii-tripo' (roster/dxmmii/attires/attire1/model.glb); both GLBs
  verified (glTF magic).
- game/data/tripo-fighters.json: regenerated via tools/roster/tripo_fighters.py.
- tools/roster/audit_select_dedup.py: NEW — asserts zero duplicate fighter
  identities, zero duplicate card images, every ladder model key resolves.
  Kept in repo for CI.

## Canon applied / confirmed
- Rave = Kiko Tanaka = Ghost: one entry ('rave'). Phantom = select entry,
  Yoshimitsu ladders as T8. Doc Frank = Bosco: one entry. Charger = Blanka
  replacement, no Blanka slot. Mary Posa over Zafina: one MARIPOSA entry,
  Zafina only as back-slot attire. (Repo canon name is MARIPOSA —
  butterfly-themed, owner-approved across PRs/renders; "Mary Posa" appears
  nowhere in-repo, reads as voice-typed "mariposa". Kept MARIPOSA; flagged
  for owner confirm in docs/owner-directives.md.)

## Verification
- node --check clean on roster-full.js, attires.js, assets.js.
- Audit: 48 select entries, ZERO duplicate fighter identities, ZERO duplicate
  card images. Four pre-existing wiring gaps surfaced by the audit (all on
  main, none introduced here — model files not in the repo, so not
  guessed/faked; flagged for the model lane): 'zen-attire1' (Zen Attire 1
  Spirit Body Tripo 8c46e379; main's WORKLOG already records "zen transform
  targets (never wired on main)"), 'torch-tripo-a1' / 'torch-tripo-a2'
  (Torch's Tripo A1/A2; roster/torch/attires/ has only attire3),
  'doc-frank-a1' (Doc Frank Attire 1 old-man Tekken reskin).
- getRosterByTier slices untouched (souls 0-8, main 9-15).

## Flags for the owner (ambiguous — not guessed)
1. 'ryuji' vs 'ryuji-rock': two slots, distinct concepts — needs owner call.
2. 'armor-king' holds a slot under its Tekken name (WH rename pending).
3. 'zangief'/'vega'/'iori' working names pending owner pick.
4. Kevin's Tripo (kevin-tripo) not in repo — his default stays the Baek model.
5. Nine Souls sharing the 'pantera' model inherit Pantera's 6-attire picker
   ladder (attiresFor keys by model) — pre-existing quirk, noted for grid worker.
