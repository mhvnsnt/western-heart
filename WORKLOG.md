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
