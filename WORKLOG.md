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

## 2026-10-21 — Lane 1: playability code fixes (B1 / B4 / B5)

Branch: `fix/playability-code-fixes-20261021`. Three audit blockers from
~/workspace/audit/REPORT.md fixed as code-only changes (no asset changes).
Tool: GitHub Git Database API (no git push available on the VM).

- **B1 (fight-start hang)** — `game/js/assets.js` ~line 634: the `_facingReady.then(...)`
  gate in `loadModels`/`loadOne` had no rejection handler and the 90s
  `LOAD_TIMEOUT_MS` was disarmed before it, so a throw in `feetFacingCue` or an
  unsettled `_facingReady` hung `startFight` forever ("Entering the arena…").
  Now: try/catch around the facing computation defaulting to +Z (with a
  `[WH]` console.warn), plus a rejection handler that also defaults to +Z and
  resolves — the load can never hang on the facing gate.
- **B4 (stuck always-on aura)** — `game/js/fighter.js` `_enter(state)` (~line 838):
  clears `this.attack`/`this.attackName` when leaving the attack state, so an
  interrupted Soul Surge (receiveHit → hitstun/knockdown/ko, throw-lock) can no
  longer latch `attackName === 'surge'` and stick the aura on permanently.
  Belt-and-suspenders in `game/js/game.js` `_startRound()` (~line 151): clears
  both fighters' `attack`/`attackName` on round reset (that path assigns
  `state=` directly, bypassing `_enter`).
- **B5 (unguarded `char.surge.*` reads)** — `game/js/game.js` lines 255-256, 400,
  453-454: 45 of 59 roster entries have no `surge` object; a full-meter surge
  threw `TypeError`. Now uses `?.` with fallbacks mirroring the existing guard
  in `fighter.js:388-389` (`surge ? surge.color : colors.trim`; accent → `0xffffff`;
  name → `'SOUL SURGE'`). Checked existing `surge.name` values in
  `game/js/roster-full.js` (e.g. "PANTHER'S WRATH", "COLD FLAME") before picking
  the generic fallback.

Verification: `node --check` clean on all three modified files; edited regions
re-read to confirm exact placement; no secret-like patterns (gitleaks not
installed on this VM — grep scan instead, clean). Repo laws respected: one
commit per change, feature branch + PR, merge via API only when mergeable and
CI green.

## 2026-10-21 — Lane 4: rig batch 1 (6 fighters) — knn backend

Branch: `fix/rig-batch-1-20261021`. Audit B2: 22 unrigged static fighters.
This batch rigs 6: Scimitar, Waterfall, Armor King, Charger (Attire 1+2),
Saku Ra. Tool: GitHub Git Database API (no git push available on the VM).

**Backend substitution (why not rig_tripo_static.py / Blender):** Blender is
not installed on this VM and the VM has ~8 GB RAM (~300 MB free) — the
Blender+GameRig path OOMs on dense Tripo statics. The repo's own
`tools/auto_rig/README.md` documents the `knn` backend as "for dense statics
Blender chokes on" (numpy/scipy only, both installed). Donor rig:
`game/assets/models/pantera.glb` (49-bone WH Mixamo-style skeleton, per the
README's knn example). Pipeline per model: (decode meshopt if needed) →
`knn_transfer.py` → `.npz` → `apply_skin.py` → rigged GLB → `validate.py`
(the playable gate). Output convention follows the proven Zui path:
`model-rigged.glb` written BESIDE the original `model.glb` (owner's original
stays untouched); `MODEL_URLS` repointed to the rigged file.

**Local bug-fix patches** (documented in the script headers; the repo
scripts as-shipped crash or produce garbage on the real donor/inputs —
method unchanged, still k-NN from the pantera donor → validate gate):
- P1: donor `JOINTS_0` is UNSIGNED_BYTE (raw uint8 = joint indices); the
  repo script read it as float32 → garbage weights for every vertex.
- P2: donor reference used only mesh 0 (a 202-vert accessory); now all
  donor meshes are concatenated.
- P3: transfer every target prim (not just mesh 0 prim 0); one global
  normalize so multi-mesh models stay aligned.
- P4: chunked k-NN accumulation (RAM bound).
- P5: `--rotate-y` + normalize params stored in `.npz` for exact reuse.
- P6: `validate.py` height measured over the model union, not just
  prim 0 (multi-prim statics failed the gate on an accessory prim).
- P7: `decode_meshopt.py` — Tripo GLBs are EXT_meshopt_compression;
  decoded with the `meshopt` PyPI package before transfer.
- P8: far-vert fallback — verts with no donor coverage (>0.10–0.16 m)
  blend to their nearest donor joint (smoothstep) instead of inheriting
  hand/foot weights (e.g. Waterfall's hair disc, Charger's shoulder bar).
- P9: target node transforms baked to world space (armor-king's -90° X
  Sketchfab root).
- P10: normalize aligns x/z CENTERS (repo mapped min-corner on all axes,
  shifting bodies ~0.6 m off the donor when proportions differ); y still
  aligns feet (min to min).

**Facing:** determined per model by anatomical signals (nose-sharpness test,
head-texture face-vs-hair color, feet toe cue, textured renders viewed);
k-NN distance as tiebreaker only. Scimitar/Charger/Charger-A2/Saku Ra face
+Z (rotate-y 0); Waterfall/Armor King face -Z (rotate-y 180).

**Batch 1 manifest** (input → output, validate verdict):
- scimitar (`game/assets/models/scimitar.glb` 13.3 MB → `scimitar-rigged.glb`
  14.0 MB): PASS. 25,448 verts, 9 prims; pose test (40° LeftArm rotation
  moves only left-arm verts, max 0.15 m) sane. Pilot model.
- waterfall (`roster/waterfall/attires/attire1/model.glb` 18.0 MB →
  `model-rigged.glb`): PASS. 1,016,911 verts; hair disc → Head via P8.
- armor-king (`roster/armor-king/attires/attire1/model.glb` 0.4 MB →
  `model-rigged.glb`): PASS. 29 meshes / 5,679 verts (multi-mesh path).
- charger (`roster/charger/attires/attire1/model.glb` 18.0 MB →
  `model-rigged.glb`): PASS. 1,011,689 verts; side agreement 1.000 on k-NN
  verts.
- charger-attire2 (`roster/charger/attires/attire2/model.glb` 17.4 MB →
  `model-rigged.glb`): PASS. 1,022,542 verts.
- saku-ra (`roster/sakura/attires/attire1/model.glb` 19.3 MB →
  `model-rigged.glb`): PASS. 1,007,864 verts.

All: `validate.py` PASS (valid glTF, ≥1 skinned mesh, 0 missing bones of the
20-gate set, height 1.75 m, feet y=0); bone names exactly the WH Mixamo set;
donor Idle clip copied (147 channels). Peak RAM 367–616 MB, wall 0.4–17 s
per model (1 M-vert Tripo models ~7–17 s knn + ~4 s apply). No model failed
validation; none skipped.

`MODEL_URLS` repoints (7 keys): `scimitar`, `waterfall`, `armor-king`,
`charger`, `charger-attire2`, `saku-ra` → their `model-rigged.glb`.

**Correction (2026-10-21):** Waterfall was re-processed with rotate-y 0
(+Z) instead of 180. Three independently-confirmed Tripo models (Charger,
Charger-A2 via nose-sharpness; Saku Ra via head-texture face color) all face
+Z, establishing the Tripo export convention; the far-vert fallback count
dropped 7x (940k → 137k) with the +Z facing, confirming better geometric
alignment. The model-rigged.glb in this PR is the +Z version.

# WORKLOG — Moveset gaps B3: Frankenstein file + charger-attire2 index (2026-10-21, branch fix/moveset-gaps-20261021)

Subagent lane (audit REPORT.md B3): two gaps closed, four commits.

## GAP 1 — doc-frank-frankenstein had no moveset file, no MOVESET_MAP entry
- New `game/assets/movesets/doc-frank-frankenstein.json`: derived from
  `doc-frank-hood.json` (same fighter DOC FRANK, same gunjack T3 teardown
  source, same SOURCE-MERGE lineage). Verified: hood and wowomomo share a
  byte-identical 788-move dict under their own ids, so sibling attire =
  identical frame data is the established convention. Only the `fighter` id
  and a new `derivation` provenance object changed; all frame data
  (moves/strings/specials/slots/hit_words/stance_after/merge_sources)
  verified byte-identical to the source file. No hand-authored frame data
  (docs/RULES_NO_GUESSING.md). The repo's own generator
  (tools/gen-movesets-t3.py) could not be re-run here: the decoded bank data
  (teardown/tekken3/movesets, banks/) is not in this checkout.
- `game/js/movesets.js`: added 'doc-frank-frankenstein' to MOVESET_IDS
  (commented, matching list style).
- `game/js/fighter.js`: added 'doc-frank-frankenstein': 'gunjack' to
  MOVESET_MAP (beside the sibling doc-frank entries).
- `game/assets/movesets/index.json`: added the fighters entry, computed with
  the tool's own formula (tools/moveset-merge/merge_sources.py build_index):
  display DOC FRANK, tekken_base "Doc Frank", t3_source gunjack,
  anim_bank bosconovitch, moves 788, inputs 176, bytes 568638.
- `game/tests/fighter-completeness.test.mjs`: removed
  'doc-frank-frankenstein' from KNOWN_GAPS. Test run: 4/4 pass
  (node --test game/tests/fighter-completeness.test.mjs).

## GAP 2 — charger-attire2.json on disk but never fetched
- File existed on disk and 'charger-attire2' was already in MOVESET_IDS
  (movesets.js:69), but absent from `game/assets/movesets/index.json`, so
  runtime _fetchOne skipped it and Charger Attire 2 fought on the bryan
  aggregate. Added the index entry with the tool's formula: display CHARGER,
  tekken_base "Blanka (SF) — fighter replaced by CHARGER (owner 2026-10-20)",
  t3_source bryan, moves 199, inputs 199, bytes 92625 (real file size;
  charger's own entry is 94261).
- Index key order verified identical to a fresh build_index() run.

## Noted, not in this lane's scope
- `deathfang-werewolf.json` exists on disk but is also absent from
  index.json (found while verifying build_index()). Left alone; belongs to
  another lane.

## Instruction-gate episode (same PR, follow-up note)
- The `instruction-gate` CI check failed on the first PR body (AGENTS.md law 15:
  the body must carry the six sections Owner instruction / Method specified /
  Method used / Deviations / Proof / Self-check). Rewrote the body with those
  sections verbatim; validated it locally against the repo's own gate script
  (.github/scripts/instruction_gate.py::check) before pushing the update.
- Note for future lanes: editing the PR body via the API did NOT retrigger the
  workflow (no new run appeared for the `edited` event; close/reopen did not
  either). A fresh `synchronize` (this commit) was needed to get a new run
  with the fixed body in the event payload. (Same experience as Lane 1 on
  PR #471.)

# WORKLOG — B6 lane 3: drop ryuji-rock roster entry + Vega-style T3 bone remap for Slice (2026-10-21, branch fix/ryuji-slice-20261021)

## Item 1 — drop ryuji-rock roster entry (model pending owner Tripo link)
- `roster/ryuji-rock/attires/attire1/` contains ONLY `README.md` (no `model.glb`); the README documents a full model hunt (2026-10-19) that found nothing usable. Per the repo's own intake convention ("roster entry is only added once the model is on disk, so the fighter is never selectable with a missing model") and `docs/RULES_NO_GUESSING.md`, removed ONLY the `{ id: 'ryuji-rock', ... }` entry from `FULL_ROSTER` in `game/js/roster-full.js` (59 → 58 entries).
- Kept for when the model lands: `game/assets/movesets/ryuji-rock.json`, `'ryuji-rock'` in `MOVESET_IDS`, the `MOVESET_MAP` entry, the `MODEL_URLS` entry in `game/js/assets.js`, and `roster/ryuji-rock/` + README (owner's Tripo share link → `tools/tripo-pull`).
- Verified against current main: full grep of `game/js` shows no other references — `attires.js`: none; no `forms`/`transform`/`targetModel` refs (the entry had none); `fighter.js:73` is a passive aggregate-bank fallback map keyed by fighter id (untouched per constraints); `movesets.js`/`assets.js` entries kept intentionally. `'ryuji'` (steve-fox stand-in, CornerStone lane's stale entry) untouched.
- `game/tests/fighter-completeness.test.mjs` iterates `FULL_ROSTER`: ryuji-rock was file-present + loaded (not a gap), so removal cannot newly fail it. `game/tests/model-key-guard.test.mjs`: ryuji-rock was `pending: true` (skipped), so removal cannot newly fail it either.

## Item 2 — Vega-style runtime T3 bone remap for Slice (game/js/assets.js)
- Slice's GLB (`roster/slice/attires/attire1/model.glb`, 52,403,356 bytes, Tekken 7 Dragunov teardown): 198-joint T7 skeleton, 17 skinned meshes, 1 skin. Core joints carry T7 names (`Hip`, `Spine1`, `L_Arm`, …) with no T3 `Hips`/`Spine`/`Chest`/… set, so the T3 stance gate (`select-screen.js`: needs `Hips`/`RightArm`/`Head`) never fired → bind pose.
- Bone-name list + hierarchy + bind quaternions extracted from the GLB JSON chunk with python3 (no Blender). Authored `SLICE_MODEL_URL` + `SLICE_T3_BONE_REMAP` (19 renames; `Neck`/`Head` already T3-named on this rig) + `remapSliceBones(fighterId, model)` with Vega's strict scheme-signature discipline (applies ONLY when `MODEL_URLS[fighterId]` is Slice's URL AND every source name is present AND no target name already exists; otherwise strict no-op). Wired into `createInstance` next to the Vega call; the `bones.Spine1`/`bones.Spine2` dict-alias block (fighter.js procedural layer: hurt capsule + attack origin) extended to `sliceRemapped`. Vega's remap untouched.
- Measured deviations from the Vega pattern (documented in-code, not guessed): (1) `MODEL_00` carries a 180° skeleton-frame rotation, not a wrapper rotation — a naive copy of Vega's full-chain factorization tips the converted skeleton to Z-up (head.y − hips.y = 0.000, verified numerically → select-screen fit gate would fail); only non-bone wrappers are factored, preserving authored Y-up world positions (head.y − hips.y = 0.751). (2) `Spine1` is authored as a SIBLING of `Hip` (both under `BASE`) — the T7 layout — while T3 banks assume Mixamo `Hips → Spine` and `retargetT3Clips` emits a `Hips.position` vertical root-motion track; so `Spine` is reparented under `Hips` (world transform preserved) to complete the T7→T3 hierarchy conversion. The game's `analyzeRig` is hierarchy-adaptive (dynamic chest LCA + spine chain), so the retarget consumes the converted rig as designed. All `__offset` joints verified (ancestor walk) as sibling/leaf helpers — no in-chain neutralization needed, unlike Vega.
- Verification: node harness running the ACTUAL extracted `remapSliceBones` against a THREE hierarchy rebuilt from the real GLB node data (repo's vendored three.js) — 54/54 checks: strict no-ops (wrong URL / missing source / second call), 19 renames, 198 bones preserved, parent chain above Hips == canonical `(-0.7071, 0, 0, 0.7071)`, all 21 driven bind locals canonical, world positions preserved Y-up, clip conjugation identical to the canonical rig, Hips root motion moves torso + legs together. `node --check` clean on both edited files.

## Flag (not my lane)
- The B1 facing-gate guard (Lane 1, commit `587d63cf`) is ABSENT from current main's `game/js/assets.js` although it is in the file's history — likely dropped in merge #460. Lane 1 should re-apply it; the B1 hang vector may be live again.

## PR
- PR: https://github.com/mhvnsnt/western-heart/pull/477

## 2026-10-21 — Lane 4 rig batch 2: Phantom, Diablo, Skull, Sam-ur-a1, Kinpo, Purple Rain

All six are single-mesh meshopt Tripo statics (~1.0M verts). Facing: rotate-y 0
(+Z) per the Tripo export convention established in batch 1 (3/3 confident
anatomical signals). Diablo fitted a real tail (179k verts, chain hips→down-back).
All six pass validate.py.

| fighter | verts | far_fb | facing | tail | validate | time |
|---|---|---|---|---|---|---|
| phantom | 1,053,849 | 293,458 | +Z | no | PASS | knn 10.5s / apply 5.7s |
| diablo | 989,472 | 419,567 | +Z | YES (179k) | PASS | knn 9.8s / apply 7.7s |
| skull | 1,009,636 | 175,402 | +Z | no | PASS | knn 9.8s / apply 5.9s |
| sam-ur-a1 | 1,013,030 | 298,280 | +Z | no | PASS | knn 8.4s / apply 4.7s |
| kinpo | 1,000,652 | 149,570 | +Z | no | PASS | knn 8.3s / apply 3.2s |
| purplerain | 1,024,038 | 184,151 | +Z | no | PASS | knn 6.4s / apply 4.1s |

Peak RAM 491–857MB (diablo tail-fit the highest). Outputs meshopt-compressed
(18–24MB vs 70–80MB logical). SHA-256s in batch2/SHASUMS-rigged.txt.

## 2026-10-21 — Lane 4 rig batch 3: Thor, Demonio-Winged, Demonio-Human, Doc Frank Wowomomo, Doc Frank Frankenstein

Thor and Doc-Frank-Frankenstein are meshopt Tripo statics; Demonio-Winged/Human
and Doc-Frank-Wowomomo are raw (uncompressed) Tripo exports (~55MB). All
single-mesh, ~1.0M verts. Facing: rotate-y 0 (+Z) per the Tripo export
convention (Doc-Frank-Frankenstein nose-sharpness decisive +Z). Demonio-Winged
fitted a real tail (118k verts); its wings (616k far verts) use the far-vert
smoothstep fallback. All five pass validate.py.

| fighter | verts | far_fb | facing | tail | validate | time |
|---|---|---|---|---|---|---|
| thor | 1,023,359 | 462,975 | +Z | no | PASS | knn 6.0s / apply 4.3s |
| demonio-winged | 994,129 | 616,436 | +Z | YES (118k) | PASS | knn 9.5s / apply 8.9s |
| demonio-human | 1,008,360 | 211,878 | +Z | no | PASS | knn 7.0s / apply 6.8s |
| doc-frank-wowomomo | 1,003,987 | 209,333 | +Z | no | PASS | knn 7.0s / apply 6.6s |
| doc-frank-frankenstein | 974,909 | 165,696 | +Z | no | PASS | knn 5.0s / apply 3.2s |

Peak RAM 468–858MB (demonio-winged tail-fit the highest). Outputs
meshopt-compressed (18–21MB vs 70–73MB logical). SHA-256s in
batch3/SHASUMS-rigged.txt.

## 2026-10-21 — Lane 4 rig batch 4: Zangief, Burger, Kronos, Kronos-Attire2 (Timberwolf), Koreshi

All five are Tripo statics. Zangief is smaller (363k verts, raw export,
y-centered — normalize handles it); the rest are meshopt-compressed ~1.0M
verts. Facing: rotate-y 0 (+Z) per the Tripo export convention. All five pass
validate.py. This completes all 22 unrigged fighters.

| fighter | verts | far_fb | facing | tail | validate | time |
|---|---|---|---|---|---|---|
| zangief | 363,134 | 209,539 | +Z | no | PASS | knn 3.6s / apply 1.8s |
| burger | 1,003,047 | 328,685 | +Z | no | PASS | knn 6.9s / apply 4.7s |
| kronos | 1,000,377 | 259,750 | +Z | no | PASS | knn 5.9s / apply 3.8s |
| kronos-attire2 | 1,010,767 | 209,815 | +Z | no | PASS | knn 6.1s / apply 3.9s |
| koreshi | 1,013,835 | 269,882 | +Z | no | PASS | knn 7.1s / apply 3.6s |

Peak RAM 214–626MB. Outputs meshopt-compressed (10–25MB vs 24–72MB logical).
SHA-256s in batch4/SHASUMS-rigged.txt.

## 2026-10-21 (~23:14 CDT) — Doc Frank attire reorder: Tripo models lead, Tekken reskins to the back (owner verbatim override)

Owner verbatim: "his 1, 2, 3, 4, 5 should be his Tripo models; the Tekken reskins go toward the back, not 1 or 2. Stop showing me the Tekken versions first — show the Tripo 3D models I made for him."

Root cause found: the 2026-10-21 ~19:08 CDT "ladder rule" lane had put Attire 1's pre-form old man (`doc-frank-a1`) at picker slot 1 as the default — but its file lineage is the PR #263 machine-shop texture reskin of the Bosconovitch base (a Tekken reskin, not a Tripo model), so the user was still seeing a Tekken version first. The picker order the user sees is controlled by `ATTIRE_VARIANTS['docfrank']` in `game/js/attires.js` (rendered chip-by-chip in order by `renderAttires()` in `game/js/select-screen.js`; default = first entry via `selectedAttireModel()`; player fights go through `resolveFighterAttire()` in `game/js/main.js`). The "owner ladder rule" comment the coordinator remembered in `roster-full.js` does not exist — the actual control point is the attires.js ladder.

Change (reorder only — every model stays reachable, nothing deleted):
- `game/js/attires.js`: `ATTIRE_VARIANTS['docfrank']` reordered — all 7 Tripo models first (slots 1–7: Attire 1 Transformed, Wowomomo pair, Hood pair, Frankenstein pair), Tekken-based models at the back (slots 8–10: old-man pre-form, Bosconovitch base, Machine Shop reskin). Default = slot 1 = `doc-frank-big` (Tripo). Labels now carry provenance: `(TRIPO)` / `(TEKKEN RESKIN)` / `(TEKKEN CANON)`.
- `game/js/roster-full.js`: main `docfrank` entry model `doc-frank-a1` → `doc-frank-big` (matches the picker default; CPU-enemy Doc Frank now also shows the Tripo model).
- `game/js/assets.js`: `doc-frank-a1` comment corrected (was falsely claiming "Forefront default").
- `roster/doc-frank/ATTIRE-SLOTS.md`: ladder rule replaced with the owner's verbatim override; picker-order table (slots 1–10) added; history entry added.
- Old→new slot mapping: 1→8 (old man), 2→1 (big), 3–8→2–7 (pairs), 9→9, 10→10.

Known trade-off (documented in-code): with the Tripo bigger form as the default, TRANSFORM from the default swaps big→big (no visual change); selecting a back-slot old-man form and transforming still lands on the Tripo bigger form. The A1 two-form pair is intact.

Validation:
- `node --check` clean on all three edited JS files.
- `node --test game/tests/model-key-guard.test.mjs`: "own model on both resolution paths" PASS (docfrank player→`doc-frank-big`, enemy→`doc-frank-big`, both in own-list); the file-existence subtest fails only on rigged GLBs absent from the pre-#482 snapshot tree (phantom/diablo/skull/… `model-rigged.glb`) — pre-existing, none doc-frank related (proven via pristine-tree run).
- `node --test game/tests/fighter-completeness.test.mjs`: "newly wired attire ladders keep the current default" PASS. Two pre-existing failures, both proven unrelated: moveset KNOWN_GAPS (frankenstein moveset JSON added to main after the snapshot) and zen transform targets (never wired on main).
- Picker proof: executed the real `attiresFor()`/`selectedAttireModel()` against the real `FULL_ROSTER` in node — slots 1–7 Tripo, 8–10 Tekken, default `doc-frank-big`. Rendered proof image from that exact data: `docfrank_picker_proof.png` (viewed).
- Headless Chromium in this VM cannot perform HTTP navigation (verified: even example.com and trivial pages return empty; `--screenshot` hangs), so no live 3D select-screen capture was possible here — the user reviews the reordered picker on the live Pages build per the loop.

## PR
- PR: https://github.com/mhvnsnt/western-heart/pull/502


## 2026-10-21 — Tripo auto-intake lane: tools/tripo-intake (rig new Tripo statics ASAP)

Owner directive (verbatim): "As soon as a Tripo model comes in you need to get it rigged automatically ASAP to the character rig that it goes to."

Built the intake the owner asked for (PR #TBD):

- tools/tripo-intake/intake.py — orchestrator. `inbox/<fighter>/attire<N>.glb`
  (+ optional `attire<N>.json` sidecar) → env check → claim (fighter id must be
  an existing `roster/<dir>`, never guessed; slot must not hold
  `model-rigged.glb`, never clobbers; input must be an unrigged static) →
  sha256 + `ledger.json` (identical bytes re-decide identically) →
  `gltf_codec` decode → `facing_check.py` → `rig_tripo_static.py --facing` →
  gates on `rig_report.json` → stage
  `roster/<fighter>/attires/attire<N>/model-rigged.glb` + `WIRING-CHECKLIST.md`
  → archive the inbox original to `outbox/<fighter>/attire<N>/<timestamp>/`.
  Exit 0 done / 2 refused / 3 failed. Wiring `game/js/*` stays a REVIEWED step —
  the intake never edits game code.
- tools/tripo-intake/facing_check.py — automatic facing determination on the
  decoded static. cue1 = gamerig foot-vs-shin centroid math (Blender-free port
  of `normalize_and_face`, snapped to ±X/±Z, raw angle never trusted); cue2 =
  `assets.js` `feetFacingCue` port on both axes (|score| ≥ 0.05, the game's own
  threshold). Confidence gate: cues agree AND residual ≤ 15° AND toe offset ≥
  1.5% of height AND ≥ 500 band verts — else REFUSE (exit 2), never guess.
  Verified on synthetic T-poses: all 4 cardinal facings CONFIDENT; the 16°-
  off-axis case (the demonio-a1 failure mode), a skirt-occluded foot band, and
  a featureless sphere all REFUSE.
- tools/tripo-intake/README.md — runbook: drop-in convention, stage table,
  facing gate, what-done-looks-like, the manual wiring checklist, cron-vs-
  manual recommendation (manual trigger recommended; cron as notifier only).
- game/tripo-intake.html — suite dropzone/dashboard: drop a GLB to validate
  it locally (GLB header parse, 0-skins check, sha256), get the exact inbox
  path + intake commands, download the sidecar JSON; shows recent intakes
  from `ledger.json` and the demo.
- tools/TOOLS-INDEX.md §3 — linked.

Gate semantics (aligned with the repo's actual practice): `validate.py` is the
HARD playable gate — it must pass or nothing stages. `anim_check` is the
deformation stress gate: its flags are RECORDED (even the shipped Zui A1
carries anim_check flags on the CMU clip) and must be explained by viewing the
renders before wiring.

Dry run (end-to-end, --dry-run): temp copy of
`roster/kinpo/attires/attire1/model.glb` (sha256
`ec67f8f0ddd57e97a915cc85408df08956dcc8bfddfe982698261f03fb6a155f`, matches
`roster/kinpo/ATTIRE-SLOTS.md`; original untouched; staged outside the repo).

- facing_check: CONFIDENT +X — cue1 raw yaw 2.8° (snapped +X, residual 2.8°),
  cue2 x-score +0.157 vs z-score −0.043 (dominant +X), toe offset 3.2% of
  height, 74k foot verts. Both cues agree.
- NOTE: the 2026-10-21 k-NN batch lanes rigged kinpo assuming +Z ("Tripo export
  convention", batch 2). The intake measures +X on the source mesh. The facing
  gate exists because that assumption is not always true — flagging for the
  coordinator: kinpo's shipped `model-rigged.glb` may carry 90°-off weights.
- rig: `rig_tripo_static.py` completed (exit 0); `validate.py` PASS (valid glTF, skinned mesh, canonical bones, height 1.8 m, no missing bones); `anim_check` flags recorded: Hips->LeftPelvis bone variance 155.5%, 40 tearing spikes, p99.9 edge stretch 1.927 (stress-clip flags of the kind the shipped Zui A1 carries; explained by viewed renders). Output `model-rigged.glb` 30.0 MB (sha256 `642c7b3e…`); 9 pose renders.
- proof: `docs/proof/muse-2026-10-21/tripo-intake/` (`facing_report.json`,
  `rig_report.json`, `intake_summary.json`, pose renders — viewed,
  `steps.log`).

Demo (visible in the suite): the dry-run output committed as
`roster/kinpo/attires/attire1/model-intake.glb` + `MODEL_URLS` key
`'kinpo-intake-demo'` (suite-viewer demo key only; the live game keeps using
`'kinpo'`). View at `game/customization-viewer.html?fighter=kinpo-intake-demo`.

Env note: this VM's Blender 4.0.2 needed libEGL/libGL (`Couldn't open
libEGL.so.1`). apt hung on the mirror; extracted `libegl1_1.7.0-1build1` +
`libgl1` debs from the Ubuntu pool (libglvnd) to `~/workspace/tools/syslibs`
and set `LD_LIBRARY_PATH`. Documented in `tools/tripo-intake/README.md`
troubleshooting.

First dry-run attempt failed at the final encode with ENOSPC (`/tmp` is a
512MB tmpfs); re-ran with stage/report roots and TMPDIR on the overlay
filesystem. All intake stages completed on the re-run.

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
`docs/fixes/docfrank-feet-rootcause-20261021/before-after-stance.png`,
`docs/fixes/docfrank-feet-rootcause-20261021/sidebyside-original-vs-posed.png`.
