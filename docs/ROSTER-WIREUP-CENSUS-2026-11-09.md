# ROSTER WIRE-UP CENSUS — 2026-11-09

Owner order (2026-11-09 ~20:58 CST): "Get all the models actually wired into
the repo so they are selectable without it asking me for a file from my
storage or library like a real game."

Method: re-verified on current main (head 6f8d8a8d, pushed 2026-11-10
02:46 UTC) via the GitHub API — full trees for roster/ (1,672 entries),
game/ (4,012), customization/, lab/, moveset-library/, teardown/ (57,481),
plus raw parses of game/js/assets.js, roster-full.js, attires.js,
characters.js, select-screen.js, core-set.js and material-status.js, and a
faithful re-implementation of the game's own attiresFor() gate run over
every roster entry. The 2026-10-23 numbers were used only as a suspect
list; every line below was re-measured.

## Headline numbers

- MODEL_URLS (game/js/assets.js): **222 keys — all 222 resolve to files on
  main. Zero broken keys.**
- Selectable roster (FULL_ROSTER, game/js/roster-full.js): **85 entries.**
- Passing the attire + material gates (characters.js ROSTER): **79** at
  census start → **81** after this PR.
- Actually visible on the select grid (ROSTER minus select-screen.js
  SELECT_HIDDEN): **78** at census start → **80** after this PR.
- Remaining not selectable after this PR: **5 entries, all named below**
  (byou, tou, ryuji, bf-maime, zen) — zero unnamed gaps.

## The six hidden at census start — verdict per fighter

1. **GYOU — WIRED IN THIS PR.** Canon: the spirit body IS the fighter
   (roster/gyou/CANON.md). His own Tripo "fiery humanoid" was archived
   unrigged at roster/gyou/spirit-body/ (source sha256 a1bd1432…). PR #1600
   (Wave 3 L3, still open/CONFLICTING) rigged it on the auto_rig refit
   pipeline as roster/gyou/spirit-body/model-rigged.glb and proved it in
   fixed-step fights (50 bones, hwoarang bank). This PR carries that exact
   file over (blob 6777e2dd…, 32,476,664 B — byte-identical, not a
   re-export), adds MODEL_URLS key `gyou-attire1`, sets his roster model,
   and takes him off SELECT_HIDDEN. Re-verified here: GLB parses, 1 skin /
   50 joints / 1 animation; the game's own material audit (auditGltf) =
   PASS. `gyou-spirit` (his floating spirit form) is unchanged.
2. **KAI — WIRED IN THIS PR.** His own soul-body shell `kai-body` existed
   and resolved, but the material gate quarantined it ("1 untextured":
   ModelHair_Base_Material017 carried no texture and no colour). PR #1600
   repaired that one material with the authored flat colour sampled from
   the model's OWN hair texture (RGB 0.197/0.153/0.106; JSON-chunk-only,
   +44 B, geometry untouched). This PR carries the repaired file over
   (blob 4cd9341a…, 25,644,200 B) and lifts the quarantine line.
   Re-verified here with the game's own audit code: main's file FAILS
   (1 untextured, that exact material), the carried file PASSES (24/24).
3. **BYOU — NAMED BLOCKER (no own-body model exists in holdings).**
   Base Wang Jinrei (owner ruling 2026-11-06; his moveset was rebased to
   Wang's full T6 kit then). Searches run: full repo trees (roster/game/
   teardown — no Wang model file anywhere), teardown/tekken6 (Wang's T6
   PSP package is moveset data + NDPP mesh sections that are UNSKINNED and
   UNTEXTURED — bone palette unproven, NTPP textures undecoded; T6 lane
   blockers B1/B2), GRE tekken6-psp-v1 release (same NDPP source), WH + GRE
   release lists (60 + 40 tags — no Wang model), workspace staging
   (tripo-recovery/ no longer exists on this VM; its archive release
   tripo-recovery-originals-20261021 holds the 10 known Tripo pulls, all
   already wired — see below). His recorded vessel (Zui/Steve body) is
   forbidden by the no-wrong-body gate (owner order 2026-10-23, #866) and
   by attiresFor()'s own law. He stays modelPending — the gate's
   prescribed state — until a Wang body is produced (T6 palette/texture
   decode, or a TTT2 extraction; Wang is not in Tekken 7).
4. **TOU — NAMED BLOCKER with a live route (extraction, not wiring).**
   Base Paul Phoenix. No Paul model file exists in the repo (full-tree
   search, 0 hits — same verdict as PR #1600's lane). BUT his real source
   is now held: Paul (code `pau`) is a base-roster Tekken 7 character and
   his full 1P part set sits in the owner's own pakchunk0 — located in the
   pak index (T7 wire-up scratch index-pakchunk0.json): SK_CH_pau_fac,
   SK_CH_pau_bdu_1p, SK_CH_pau_bdl_1p, SK_CH_pau_har_1p + their textures,
   skinned to the shared T7 skeleton. The extraction machinery is landed
   (PR #1700: pak range reader + driver + umodel; 9 bases already
   extracted with skeleton + Namco weights). What remains is a production
   job in that pattern (range-fetch → umodel export → assemble → texture
   bake → fight proof), and the range source (release tekken7-gamefiles-v1)
   was at 14/54 parts transferred when checked. His declared rider body
   (Pantera) is forbidden by the same no-wrong-body gate. He stays
   modelPending until the Paul extraction lands.
5. **RYUJI — HIDDEN BY OWNER RULING, not a missing model.** Owner ruling
   #6 (docs/handoffs/ROSTER-100-FIX-2026-11-04.md, recorded in
   tools/portraits/KNOWN-PLACEHOLDERS.json): ryuji is the hidden same-body
   hybrid of CORNERSTONE (ryuji-rock, who IS selectable with his own
   wired model); ryuji's card is byte-identical to ryuji-rock's by that
   ruling. No distinct Ryuji/Yamazaki model exists in holdings (he is an
   SNK/KoF character; no KoF teardown holdings in repo). Left exactly as
   ruled.
6. **BF-MAIME — NAMED BLOCKER (material/texture production, not wiring).**
   Her model is wired (key `bf-maime` resolves to
   roster/bf-maime/attires/attire1/model-rigged.glb) but the material gate
   quarantines it: "15 untextured". The repo holds no textured version and
   no loose textures for her (her roster dir contains only that one GLB);
   workspace staging search found none. Lifting this needs texture
   production/repair on 15 materials — the material lane's work, not a
   registry fix. She stays quarantined (never offered a broken model).

## Also flagged (no action taken — parent/owner call)

- **ZEN** is in select-screen.js SELECT_HIDDEN although he has wired,
  passing models (zen, zen-spirit, zen-tentacle, zen-oversoul). The
  comment above the set says only the seven vesseled souls came off the
  grid and "only ZEN and GYOU stay selectable as spirit fighters" — the
  set contradicts its own comment. The Nov 6 souls lane (PR #1600) also
  left zen hidden while un-hiding the five it wired, so this lane does
  not un-hide him unilaterally; flagged here for a ruling.
- Pending attire slot (correct behaviour, not a gap): negativo-attire2 is
  `pending: true` in the ladder (rig hasn't landed) — the picker hides it
  until it does, exactly as designed.
- Quarantined keys that do NOT hide their fighter (ladder remaps to the
  first passing own attire in characters.js): cyborg-x (Cape Jones plays
  his refit attire), torch, yukihyo, saku-ra_alt1, kinpo-legacy/kinpo-t8/
  kinpo_alt1, jin-t7, zen-body, demonio-bloodline-ember,
  jin-bloodline-ember, armor-king (not a standalone roster entry).
- Held models with no roster entry (not wired — adding a fighter is a
  roster decision, not wiring): roster/theory (attire1 + attire2 source
  GLBs), roster/kuma-replacement (attire1 source GLB; gashadokuro holds
  the slot), roster/torch/attires/attire3 source GLB (Torch is selectable
  via her wired keys), roster/props (stage accessories — not a fighter).
- Madelyn: separate lane in flight (PP PR #40 fixed GLB → WH). Listed
  here as in-flight; NOT wired by this lane.

## Old-census suspects — re-verified and closed

- cornerstone broken key (attires/attire1/model.glb missing): the key is
  gone; Cornerstone = `ryuji-rock`, model key resolves. CLOSED.
- ryuji-rock wired-but-absent: key resolves to
  roster/ryuji-rock/attires/attire1/model-rigged.glb on main. CLOSED.
- Moveset-but-no-model dirs (dio, koreshi, bruno, chordz, lili, blanka,
  iori): all have resolving model keys today. CLOSED.
- The 10 pulled-not-wired Tripo models (phantom, skull, saku_ra,
  waterfall, purple_rain, thor, mariposa, dxmmii, cape_jones, kiko):
  every one has a resolving MODEL_URLS key on main. CLOSED. (Their old
  staging home ~/workspace/tripo-recovery/ no longer exists; the archive
  of it is release tripo-recovery-originals-20261021.)
- Movesets: 239 per-id JSONs in game/assets/movesets. The roster
  `moveset` field names the Tekken base style (heihachi/xiaoyu/bryan/
  yoshimitsu/gunjack/king have no per-id file by design — they resolve
  through the bank/step-plan layer in fighter.js + full-movelist.js).
  Not a selectability gap.

## File-picker sweep (Step 3) — every surface found, with verdicts

Player paths swept: character select + loaders (game/index.html,
select-screen.js, assets.js, attires.js), customization (identity.html,
customization-harness.html, customization-viewer.html,
customization/creation-suite-ui/index.html, js/custom-fighter.js,
js/customization-consumer.js, js/user-portraits.js) and every game root
page. **No surface on any player path asks for a model/fighter file.**
Fighters load only from the game's own served roster files (MODEL_URLS).
Four file inputs exist in the wider tree; none gates content:

1. game/tripo-intake.html — `<input type="file" accept=".glb">` + drop
   zone. The dev Tripo intake tool (the model pipeline's front door).
   Verified unlinked from every player page/menu (index.html,
   side-games.html, settings.html, identity.html, game.js, wh-boot.js,
   ui-screen.js, menus.js — 0 references). Stays as a dev-only tool at
   that path, off the player path.
2. game/js/ui-gaps.js — "IMPORT REPLAY JSON" button creates a JSON file
   input. A replay-sharing feature (imports a Western Heart replay file
   into the replay list); gates no roster content. Stays.
3. customization/create-fighter/index.html — LOAD button + hidden JSON
   file input. One of three load routes on that page, beside in-page
   PRESETS (save/load/delete named builds) and SAVE; creating and using
   a fighter needs no file. Import/export convenience. Stays.
4. customization/create-fighter/art-studio.html — LOAD IMAGE + hidden
   image file input for the TOAST UI image editor (decal/art tool).
   Optional tool page; gates nothing. Stays.

## What this PR changes

- roster/gyou/spirit-body/model-rigged.glb (new; blob carried from
  PR #1600, byte-identical)
- game/assets/models/kai-body.glb (repaired file carried from PR #1600,
  byte-identical; +44 B JSON-chunk authored colour vs main)
- game/js/assets.js (+ `gyou-attire1` key)
- game/js/roster-full.js (gyou model: 'gyou-attire1', modelPending removed)
- game/js/material-status.js (kai-body quarantine line removed — the
  state the generator produces for the repaired file; no other key's
  audit depends on kai-body)
- game/js/select-screen.js ('gyou' off SELECT_HIDDEN + dated note)
- game/tests/model-key-guard.test.mjs (gyou ownership: pending →
  own [gyou-attire1, gyou-spirit]; kai comment)
- game/assets/models/MODEL-STATUS.md (dated wire-up section)
- docs/ROSTER-WIREUP-CENSUS-2026-11-09.md (this file)

After this PR: 81/85 roster entries pass the gates, 80 visible on the
select grid. The 5 remaining are named above with their exact blockers —
none is a wiring gap.
