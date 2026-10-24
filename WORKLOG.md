## 2026-10-23 ~18:15 CDT — batch3 T8 moveset pull: pond/tobi/megami/sakura/phantom (SHOW-ANIMATION LOCK)

**Owner instruction (verbatim):** "Now we need to get that done for every other character" (2026-10-23) — replicate the proven Law/Lars pattern (PR #823 merged, PR #806 green).

**Method:** T8 frame-data diff per fighter (`docs/t7t8-reference/frame-data-t8-full/<char>.json`, wavu) against existing `moves` dict keys; genuinely-missing moves added in Tekken notation via the canonical `tools/moveset-merge/merge_sources.py` `conv_t8` conversion (frames/60 -> seconds, damage scaled T8 180HP -> WH 100HP, raw kept in `damage_raw`); dedup by source-record identity (`t8_id`), key = notation when free else `<notation>~t8.<body>`; additions only (guard: 0 payload changes, 0 removals across all files).

**Moveset (done):**
- `game/assets/movesets/megami.json` (Jun Kazama): 150 -> **299** (+149 T8 Jun moves, all `"set": "FIGHT"`; TTT2-documented kit untouched; strings 0->18, specials 0->7)
- `game/assets/movesets/pond.json` (Raven): 620 -> 620 (+0 — the merge lane's T8+T7 merge already covered all 177 T8 Raven moves; diff verified clean)
- `game/assets/movesets/tobi.json` (Hwoarang): 729 -> 729 (+0 — merge lane already covered all 209 T8 Hwoarang moves; diff verified clean)
- `game/assets/movesets/sakura.json` (Xiaoyu): 764 -> 764 (+0 — all 175 T8 Xiaoyu moves merged 2026-10-21)
- `game/assets/movesets/phantom.json` (Yoshimitsu): 1019 -> 1019 (+0 — all 312 T8 Yoshimitsu moves merged 2026-10-21)
- `index.json` moves/inputs/bytes updated for all 5. Provenance in `merge_sources.added.t8_pull_20261023`.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** file-level `anim_set_lock` added to all 5 files (previously missing everywhere); the 149 moves this lane pulled stamped `"set": "FIGHT"`. No SHOW content entered any moveset.

**Animations (banks checked, gaps filed not stubbed):** `game/assets/anim/t3/hwoarang/`, `xiaoyu/`, `yoshimitsu/` exist (full 30-clip sets) — tobi/sakura/phantom wire to their own banks, no substitution. `t3/raven/` and `t3/jun/` do NOT exist (Raven debuted T5, Jun not in T3; T3 fallback empty per source priority) — precise gaps filed: `docs/anim/RAVEN-ANIM-GAP-20261023.md`, `docs/anim/JUN-ANIM-GAP-20261023.md` (FIGHT vs SHOW split, TTT2/T7/T8-first priority, unblock sequence for the extraction coordinator lane).

**Verification:** new-move schema validated (all 13 required fields incl. `set: FIGHT`); semantic diff guard green (0 field losses, 0 removals); per-file byte-exact JSON serialization preserved (diffs are pure additions). CI's 6 checks gate the merge.

**Anti-clobber:** rebuilt on current main tip after the merge lane's T8+T7 merge landed mid-task (53 commits; only `pond.json`/`tobi.json`/`index.json` overlapped — re-diffed on the new base, zero duplicated moves, their payloads untouched); surgical additions only; no deletions. Branch via Git Database API (no GitHub connector for git ops).

---

## 2026-10-23 ~15:55 CDT — Repo Co Dev: owner rules (disk offload + merge rule)

**Task:** add Oct 23 owner rules (a) disk offload, (b) merge rule to AGENTS.md, RULES_NO_GUESSING, HOW-TO-CONTINUE, Muse handoff.
**Source:** owner (Marquis) via MoneyManBusch relay, 2026-10-23. Docs only; nothing deleted.

---

## 2026-10-23 ~15:20 CDT — TTT2 extraction worker: surgical pipeline (Law/Lars lane)

**Task:** Push TTT2 extraction toward 100% (standing directive: T3 fallback-only, pulls from T5/T6/T7/TTT2). Law + Lars FIRST — their full modern movesets/animations unblock the Buffalo Bill / Chordz pull lane. Then the full 59-fighter roster, stages, audio.

**Built — `teardown/tekken-tag-tournament-2/tools/surgical/`** (no full 13.36GB download needed):
- `fetch_assets.py` — release-asset downloader via GitHub data API (Accept: application/octet-stream + surrogate credential, 302 followed without auth, Range resume).
- `vfile.py` — `PartVirtualFile`: seekable virtual file over the 26 release parts via HTTP Range. py7zr parses the 7z end-header with ~2KB transferred.
- `stream_decode.py` — LZMA stream decoder (folder: lc=3,lp=0,pb=2,8MB dict) that splits the 72 members by known uncompressed sizes and writes only wanted members + MANIFEST.txt (sha256).
- `seg_dl.py` — parallel segmented stream-prefix downloader (resume-safe per segment) for staging long poles locally.
- `extract_member.py` — single-member extract via py7zr over the virtual file.
- `fetch_zarmanager.py` — fetches GodPackage/StfsPackage (`core/xbox/{god,stfs}.py`) from dfdx047/ZarManager (not vendored — upstream license unverified).
- `README.md` — cost model + usage.

**Also:** `teardown/tekken-tag-tournament-2/EXTRACTION-RUNBOOK.md` (step-by-step: header verify → STFS blobs → Data0000 → XDVDFS listing → Law/Lars carve → roster); TEARDOWN.md status updated (safe storage DONE, disk blocker circumvented, network throttle documented).

**Verified 2026-10-23:**
- End-header over HTTP Range: 80 entries, byte-matching INVENTORY.md (1,970 bytes fetched).
- Member 19 (GoD descriptor, 45,056 bytes) stream-extracted — byte-identical to `extracted-small/` copy.
- GodPackage parses title ID 0x4E4D0859; member 0 (155MB STFS blob) stream-decoding.
- **No Tekken 3 touched** — instruction gate compliant (T3 fallback-only).

**Blocker:** VM egress proxy throttles sustained downloads to ~0.1 MB/s. Data0000 (header idx 20, key to the XDVDFS file listing → Law/Lars carve) needs a ~4.9GB stream prefix ≈ 14h — queued as a background nohup job. Per-member prefix costs in tools/surgical/README.md.

**Deviations:** none from the surgical plan. No game binaries committed (owner law — large artifacts go to Releases, repo carries tools/docs only). Pushed via Git Database API (NO-SPARSE-COMMIT LAW — no commits from the sparse checkout).

---

## 2026-10-22 ~13:45 CDT — Worker 26: AUDIO — voice mapping + announcer + music system

**Task (two tracks):** (1) Pull teardown voice lines, map to WH characters by personality/canon/style (King→Pantera etc.), wire into intros/win poses/taunts/hits/KOs as TEMPORARY placeholders. (2) Pull music systems from teardowns; build the music engine + swappable tagged library; seed with owner + open-licensed music. Follow-up: announcer YES (from teardowns, placeholder), crowd reactions SKIP (deferred).

**Track 1 — voice:**
- Audited teardowns: T3 recompiled Jun voice dispatcher (`tekken3_jun_voices.c` → separate voice bus lesson), T8 Voiceclip doc stub, Urban Reign ADX inventory (per-char `v_*` voice / per-stage `bgNN` BGM — the reference architecture), Eastern Mind owned sounds.
- 49 manifests (`game/data/voices/`): full roster + `announcer.json`. Tier A (10 fighters) ships REAL audio from the owner's own Eastern Mind teardown (Nine Souls incarnation voices, F_KING→Pantera, L_KING→Armor King), `status:"teardown"` — plays now, clone pipeline replaces later. Tier B (38) mapped by personality to Tekken/SF/KOF sources, subtitle-only (`file:null`, no copyrighted bytes). Announcer: Tekken-style calls, subtitle-only, extraction path documented for local builds.
- `game/js/voice.js`: RE-ADDED (another lane's refactor had removed worker 13's pipeline from main) + `announce()` + `onSpeech` music-duck hook (try/finally) + `playSound()` sound-bank API; contract ref updated to `docs/VOICE-MAPPING.md`.
- Wired in `game/js/game.js`: `_startRound` (round/final-round calls + FIGHT! + intensity), `_endRound` (K.O./PERFECT!/TIME UP/DOUBLE K.O. + loser KO cry + winner win line + delayed taunt + intensity drop), throttled hit cries on heavy/counter/grab (≤1/1.1s/fighter). `main.js`: `voice.unlock()`, select-cry on confirm.
- Docs: `docs/VOICE-MAPPING.md` (full table + trigger map + crowd-deferred note), `docs/research/AUDIO-TEARDOWN-AUDIT.md`.

**Track 2 — music:**
- `game/js/music.js` (new MusicEngine): stage/mode/mood tag assignment (Tekken jukebox rule), gapless WebAudio loops, 1.6s crossfades, intensity via lowpass+gain (`setIntensity`), voice ducking, local-file-first/remote-fallback, procedural fallback (never silent).
- `game/data/music-library.json`: 14 tagged tracks — 10x Kevin MacLeod CC BY 4.0 (attribution in `credit` fields) + 4x owner's Tong-Nou OST (WAV→OGG). **Tong-Nou Theme is the flagship** (title screen + Tong-Nou stage + versus rotation, per owner). Swap = edit JSON or drop same-name file; no code.
- Wired in `main.js`: `music.unlock()`, `playMenu('title'/'select')`, `playBattle(stageId)` (replaces procedural `startMusic`), `playVictory` hook; back-menu crossfades to title (was hard stop).
- Docs: `docs/MUSIC-PIPELINE.md` (add/swap guide, license rules, future stems/gungaku hooks).

**Eastern Mind extraction (100% complete, owner 2026-10-22):**
- All **229 sounds** ship as `game/data/sound-bank.json` + `game/assets/sounds/*.ogg` (categorized voice/prologue/stage, durations, `mappedTo` links to voice manifests). New `voice.playSound(bankId)` API for prologue/cutscene/UI use.
- 3 CD tracks + ending theme in the music library (above). 5,321 bitmaps → art lane; 22 videos → cutscene lane (not this worker).

**Method:** Synced to main @ push time via Git Database API. Sandbox blocks python/curl/ffmpeg file writes (same wall as worker 19) — binaries streamed through pipes straight into git blobs (ffmpeg WAV→OGG, curl MP3s); text via API-fetched fresh bytes + asserted surgical replacements. No stale copies, zero deletions.

**Proof:** node harness (stubs for AudioContext/fetch/DOM): 49 manifests resolve clips for all triggers; announcer resolves all 11 calls; `pickTrack` correct for all 9 stages + 7 modes; crossfade/intensity/duck/stop paths run clean. `node --check` on both JS files.

**Status:** PR merged via git_merge.py. Next: voice-clone pipeline replaces tier A/B placeholders; user drops own music into `game/assets/music/`.


## 2026-10-22 — Worker 51: STAGE SELECT → FIGHT FLOW (repairs + wiring, PLAYABLE TODAY)

**Owner instruction (verbatim):** "no new features — repairs and wiring only. Your scope stays stage select → fight flow. If you spot stub/placeholder code on the path, wire it — but don't invent new systems. Worker 53 now owns the fight itself (fighter loading, inputs firing, hits, rounds, crash-killing); coordinate with them at the fight-boot handoff."

**Root-caused + repaired (all in the select→fight chain):**
1. **Preview pane markup missing** — `game/styles.css` and `game/js/main.js` (`updateStagePreview`) were built for a `.stage-preview-pane` (`#stage-preview-img/#stage-preview-swatch/#stage-preview-name/#stage-preview-universe/#stage-preview-desc` inside `.stage-body`) that `game/index.html` never had — the JS no-op'd on every highlight. Wired the markup; the T7-style screen now renders preview-on-top (portrait) per the existing CSS design. No new system.
2. **Duplicate `screen-stage` id** — the STORY stage-intro panel reused the versus stage-select's id, so `screens.stageIntro` (`getElementById('screen-stage-intro')`) was null and `show('stageIntro')` threw mid-iteration (story `_storyStageIntro` dead). Renamed the story panel to `screen-stage-intro`. (A later main merge reintroduced the duplicate from an older base; re-applied on the re-sync.)
3. **Keyboard Enter on the selected stage card called bare `startFight()`** — dropped `pendingFight`, booting ROSTER[0] vs a random foe with no versus `onMatchEnd` (dead result screen). Extracted `confirmStageFromSelect()`; the CONFIRM tap and the Enter path now run the identical pendingFight-guarded confirm.
4. **Preview thumb refetch** — `updateStagePreview` re-set `img.src` on every highlight (flicker + bogus requests; most thumbs 404 → atlas tiles serve the cards). Now sets src only when the thumb exists and changed; re-highlighting leaves state untouched; swatch fallback preserved.
5. **Verified NOT broken (checked, no change):** worker 24's flagged voice.js/hitfx.js/intro-interactions.js imports — none exist in `game/js` on main; the single dangling reference (`versus-banter.js` dynamic import of `intro-interactions.js`) is try/catch-guarded and the fight path's `fighter-depth.js` import is fail-silent, so fight boot is not blocked. Full static import graph of all 70 `game/js` files: zero unresolvable imports. Every module-eval `getElementById(...).addEventListener` target present in index.html.

**Flow verified (character → stage → fight):** menu `mode-versus` → `ModeController.startMode('versus')` → select screen P1→P2 two-step (`onConfirm`/`vsStep`) → `_beginVersus` → `startFightViaStage` → `buildStageSelect` + `show('stage')` → CONFIRM → `startFight(p1, p2, { mode:'versus', stage })` → `game.startMatch(player, enemy, selectedStage, opts)` (worker 53's handoff; signature unchanged). Back/cancel paths: BACK → select, failure → hint + retry with pendingFight intact.

**Proof:** `node --check` on all 70 game/js files; DOM-stub harness running the REAL extracted functions from main.js — build (card per stage, tier headers, tap handler on every card), tap-to-select (selectedStage + preview name/desc update, swatch fallback), CONFIRM (startFight called once with p1/p2/mode/stage, pendingFight consumed only on success), failure path (pendingFight kept, CONFIRM re-enabled), Enter path routes via the confirm (no bare startFight) — all pass. Touch targets: 48px+ min on BACK/RANDOM/CONFIRM per styles.css; footer hint + preview text ellipsis/line-clamp, grid is the only scroller. Stage data: every stage (literal + t3/nm generated) carries id/name/tier/universe/description/swatch/dims/spawns; all tiers in STAGE_TIERS.

**Deviations:** none — repairs/wiring only, no new systems, no arena geometry (worker 18's stage defs consumed as-is), no menu-shell changes (worker 37's lane untouched), no fight internals (worker 53's lane untouched).
**Coordination:** worker 53 (fight) — handoff contract is `game.startMatch(playerChar, enemyChar, stageId, opts)`; stage id flows from `selectedStage` (default `'shrine'`, `getStage` falls back to STAGES[0]). Worker 37 (menu shell) — no interface changes needed. Worker 18 (arenas) — stage defs consumed unchanged. Flag (not fixed, out of lane): result-screen REMATCH with no modes.mode falls back to bare `startFight()` (ROSTER[0] vs random) — rank-battle rematch edge, worker 30's lane.
**Anti-clobber:** re-synced to main tip twice (main moved mid-task both times); edits re-applied surgically onto current main each time — main's new placeholder screens (screen-online/sidegames/collection/daily), data-mm router, and mainmenu.css link all preserved. No deletions.

---

## 2026-10-22 — Worker 34: FIGHTER DEPTH + LEARNING + STAGE LIFE (canon-mapped)

**Owner instruction (verbatim):** "Pull ALL of this from the teardowns and wire it up: Fighter depth — ki charge, tag throws/crash/assault, hair + cloth physics. Learning — per-character combo trials, ghost AI (learns from players), replay analysis. Stage life — stage intro camera sweeps, weather/time-of-day variants, versus banter dialogue." Follow-up: "Learning tools: YES, ALL — in-game movelist UI, Special Style (easy inputs), punishment training, combo trials, ghost AI, replay analysis. Add: movelist UI, Special Style, punishment training. All with WH canon mapping where naming/identity is a creative call."

**Delivered (12 systems, 15 new files + 2 surgical wires):**
- `game/js/soul-kindle.js` — Tekken 7 ki charge (1+2+3+4, glow, next hit guaranteed CH, +10% taken, no block in flash). Canon: "SOUL KINDLE" (proposed).
- `game/js/tag-relay.js` — TTT2 tag assault/crash/throw + red health. Mechanics layer for worker 24's team-battle lane. Canon: "SOUL RELAY" (proposed).
- `game/js/cloth-hair.js` — verlet cloth + bone-chain hair for Three.js (budgets, LOD, analytic colliders). Pipeline: `wh_cloth` Blender prop → glTF extras → userData → autoAttachCloth.
- `game/js/combo-trials.js` — per-character trials, PERFECT/GOOD/LATE grades, persisted. Canon: "TRIAL INSCRIPTIONS" (proposed).
- `game/js/ghost-ai.js` — ghost AI (situation histograms, temperature sampling, persisted). Canon: "SOUL ECHOES" (proposed).
- `game/js/replay-analysis.js` — REPLAY EVENT CONTRACT v1 + Trial Review overlay (worker 29's recorder plugs in). Canon: "TRIAL REVIEW" (proposed).
- `game/js/stage-intros.js` — per-land cinematic camera sweeps, skippable. Canon: "LAND REVEAL" (proposed).
- `game/js/stage-variants.js` — weather/time-of-day variants per land's element + weather particles. Variant list proposed.
- `game/js/versus-banter.js` — versus-screen banter extending worker 13's intro system; canon-web pairs (dorowani|zen playable now, rest [AWAITING-FIGHTER]).
- `game/js/movelist-ui.js` — in-game movelist (live from movesets.js). Canon: "INSCRIPTIONS" (proposed).
- `game/js/special-style.js` — T8 Special Style simplified inputs. Canon: "GUIDED HANDS" (proposed).
- `game/js/punishment-training.js` — punishment drills, PERFECT/GOOD/MISS/WRONG. Canon: "SKULL'S LESSONS" (proposed).
- `game/js/fighter-depth.js` — integration layer (FighterDepth + WH_DEPTH_FLAGS feature flags).
- `game/js/game.js` (surgical): dynamic-import wire in startMatch, raw-queue capture for kindle detection, per-frame onUpdateFrame. Rebased onto current main (kept worker 27's lighting rig; did not resurrect the removed intro block).
- `game/js/fighter.js` (surgical): kindle CH consumption + damage-taken mult in receiveHit, block denial in tryBlock. Re-applied onto current main (kept face/hand rig work).
- `game/tests/fighter-depth.test.mjs` — 43 tests, all passing (node).
- `docs/research/FIGHTER-DEPTH-CANON-MAPPING-2026-10-22.md` — per-system canon mapping + 11-item owner approval checklist.

**Canon decisions needing owner approval:** Soul Kindle name + Kindle/Surge/Urge resolution; Soul Relay naming; Trial Inscriptions teacher (Trial vs Megami); Soul Echoes; Trial Review; Land Reveal; stage variant list; versus banter pairs/lines; Inscriptions vs Soul Manual; Guided Hands vs Soul Guidance; Skull's Lessons vs Punisher's Rite. All flagged in the mapping doc.
**Proof:** 43/43 node tests pass; node --check on edited files; diff audit surgical-only.
**Deviations:** working dir `~/workspace/w34/fighterdepth` (cp -r failed: sandbox EPERM on large writes); banter for unrostered fighters staged as [AWAITING-FIGHTER]; replay analyzer defines the contract worker 29 emits; headless DOM proof blocked by sandbox write filter (logic verified in V8/node).
**Coordination:** worker 24 → call TagRelay/TagTeam; worker 29 → emit REPLAY EVENT CONTRACT v1; worker 13's intro-interactions.js extended (not modified).

---
# WORKLOG — DEATHFANG build (2026-10-19/20, branch feat/deathfang-yamazaki-20261019)

## 2026-10-22 — Worker 37 (main menu overhaul): T8-style main menu rebuild

Owner directive (verbatim): "The main menu is ugly and prototype-looking. Rebuild it
per everything described: Tekken 8 menu layouts adapted for mobile/phone inputs (from
T8 visual references, since we don't have T8 files). Tekken 7 teardown menu structure
underneath. All the modes we've been adding need to show up."

What changed (branch mainmenu/t8-rebuild):
- game/index.html: replaced the prototype vertical button stack (#screen-menu) with a
  T8-adapted layout — full-bleed hero backdrop (title-bg.png + cinematic wash + CSS
  ember drift), top player bar (player card · Soul Urge 9-pip meter · rank badge),
  compact italic WESTERN HEART wordmark, 10-item T8 rail (STORY / VERSUS / ONLINE /
  ARCADE / SIDE GAMES / TRAINING / CREATION SUITE / COLLECTION / DAILY CHALLENGES /
  OPTIONS), bottom status bar with rotating news ticker, slide-in submenu panel,
  player card editor, "in the forge" dialog, toast.
- game/mainmenu.css (NEW): T8 visual grammar — heavy italic condensed type
  (skewX, no webfont needed), T8 crimson slash on the active item, angular
  clip-path cards, near-black over WH dusk-shrine. Portrait: bottom-anchored
  scrollable rail; landscape: true T8 left rail + right-side submenu panel.
- game/js/mainmenu.js (NEW): menu controller. Submenu card data for all modes;
  working modes route via data-action through the existing delegated handlers;
  unbuilt modes (Tournament, Gungaku, Gallery, Jukebox, Replays, Daily Challenges)
  open an honest "IN THE FORGE" panel. Ranked rides worker 30's rank system
  (js/ranks.js + game/data/ranks.json — rank names NEVER hardcoded here): ONLINE
  submenu has RANKED BATTLE (mode-rankbattle) + RANK HALL (show-ranks); the topbar
  rank badge shows the best offline/online rank from the wh_ranks store and opens
  the Rank Hall. Player card (name/title) persists to localStorage wh_player_v1.
  Soul Urge pips are the Nine-Soul Meter's menu surface (ignite in-fight).
- game/js/menus.js: import + initMainMenu() call in initMenus(); the four
  special-action wirings (mode-options/records/heartmind/episodes) converted from
  one-time querySelectorAll to a single delegated document listener so dynamically
  created submenu cards route correctly. buildMenuButtons is a safe no-op now that
  .menu-buttons is gone (returns null, no duplicates).
- game/js/main.js: the data-action forEach at module eval converted to one
  delegated document listener — identical routing (incl. worker 30's
  mode-rankbattle/show-ranks), covers dynamic cards.

Anti-clobber note: main moved mid-task (worker 30's RankBattleController +
mode-rankbattle/show-ranks + TAP □/△ throw prompt labels landed). Re-synced all
touched files from main tip and re-applied the menu edits on top — worker 30's
code is fully preserved. The first-draft custom 53-tier ladder panel was DELETED
in favor of worker 30's Rank Hall (build on existing work, don't duplicate).

T7 structure underneath: STORY (Trial/Episodes/Heart & Mind) · VERSUS (1v1/Team) ·
ONLINE (Ranked Battle/Rank Hall/Tournament) · ARCADE (Ladder/Survival/Time Attack/
Soul Surge) · SIDE GAMES (Qombat/Trader) · TRAINING (Training/Gungaku) · CREATION
SUITE · COLLECTION (Gallery/Jukebox/Replays) · DAILY · OPTIONS — T7/T8 hierarchy.

Verification: node --check on all three JS files; 62-assertion DOM-stub test of
mainmenu.js (init render, all 8 submenus' card counts, data-action routing incl.
mode-rankbattle/show-ranks, rank badge refresh from wh_ranks store, card editor
save→localStorage→topbar, forge open/close, toast, every user-required mode has a
menu entry) — 62/62 pass; all getElementById targets present in index.html; CSS
braces balanced; ranks.json confirmed 53 tiers matching the user's ladder.
Headless Chromium in this VM cannot render (--screenshot/--dump-dom produce
nothing), so live visual proof (portrait + landscape screenshots, tap-through) is
deferred to the parent agent's live browser session.

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

## 2026-10-21/22 — Torch Attire 1 "Valkyrie of Flame" wire-in (Tripo 300d0c63)
- Pulled via tools/tripo-pull/tripo-pull.py only: 19,456,040 B, sha256 4f24f0c325b222658247325848dfee2d03164d30d9a61cf001404d976bd0f66d, 3 textures, unrigged statue (1,037,606 verts). Raw archived in release `torch-a1-tripo-20261021` (digest verified).
- Rigged via tools/auto_rig/rig_tripo_static.py (GameRig backend, --facing +X measured: foot-vs-shin cue 0.7 deg off +X). Heat solved first proxy: 23,885 proxy verts, 0 unweighted; full mesh 0 unweighted after transfer; smooth gate SMOOTH_OK (p99.9 edge stretch 1.80, 0 edges > 2.0); validate PASS (73 joints, height 1.8 m, foot_y 0). Shipped game/assets/models/torch-tripo-a1.glb (29,802,744 B, sha256 62bb2918379fbcef64fb2087b5f6d0cc6aacad21b05932d49260d0effa50bb73).
- gamerig_backend.py fixes (measured, same PR): (1) drop_micro_components — voxel remesh leaves 8-9-vert single-voxel islands (38 of them on this statue) that make Blender's bone heat fail for EVERY vertex; the body alone solves 0-unweighted. Islands dropped from the proxy only. (2) Arm droop sample narrowed to the outer quarter of reach — the outer half caught this statue's windswept hair mass and read 46.6 deg on a true 7.4 deg T-pose. (3) Leg knee/ankle joints re-anchored to measured per-side vertex centroids (hip 0.283 m / knee 0.173 m / ankle 0.086 m taper) instead of one hip-band spread.
- Declared: the baked QA clip (CMU135_04_boxing) fails anim_check (Hips->RightPelvis length variance, p99.9 edge stretch 3.41 on the clip's worst frames, 40 spike verts) — the clip is a QA vehicle; the game drives her with its own clip bank. Worst-frame renders in the report dir show the body intact, no tearing. Wrapper process died to box memory pressure after the after-smoothing gate; validate/render/encode/report steps were re-run with the wrapper's own commands on the kept work dir (see rig_report.json recovery_note).
- Wiring: roster-full.js Torch model -> torch-tripo-a1; attires.js ladder (A1 Valkyrie of Flame / Anna base fallback); assets.js MODEL_URLS entry; CANON.md + roster/torch/ATTIRE-SLOTS.md record the name and the owner's description verbatim.
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

<!-- Restored 2026-10-22 (Claude session): the entries below were dropped from this file by adb6784cb (T3 bank facing root-cause fix; Pantera skin-weight re-derivation) and by 6255a6e22 (which also replaced the file with a stale copy); its own loadspeed entry is kept. Text verbatim. -->

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


# WORKLOG — T8 character-select grid transplant (2026-10-22, select lane, worker 1/4)

Owner order (verbatim): "pull in like the Tekken 8 character select menu and
decode it and everything all the UI and menu art and the selections how it's
set up and get our characters put onto the Tekken the most recent Tekken game
menu grid that you can get a hold of and upgrade the character select menu"

## Approach change (mid-task, from coordinator)
- Steam/depot route for T8 assets is DEAD (owner doesn't own T8 on Steam).
- Revised: T7 teardown = structural reference; T8 LOOK decoded from PUBLIC
  visual references (screenshots/footage) and recreated pixel-faithfully in
  HTML/CSS/JS with our own original art. Community-posted T8 UI textures
  surveyed as reference only — NOT committed (owner rule 8: no
  copyrighted/leaked game files in public repos or Pages). This deviation
  from the "community textures are fair game to pull in" brief is flagged
  in the PR/report for owner confirmation.

## What was built
- `game/js/ui-skin.js` (NEW): skin/theme config layer. All visual tokens
  (colors, fonts, card geometry, fact rows, texture paths) for the select
  screen; `getSkin()`/`applySkin()`/`setSkin()`; full DROP-IN CONTRACT
  documented in-file (new skins, texture naming under
  `game/assets/ui/<skin>/`, copyright rule, `?skin=<id>` deep link).
- `game/js/select-screen.js` (MODIFY): rebuilt on the T8 grid. PreviewPane
  (live 3D) kept verbatim. New: compact centered multi-row card GRID
  (replaces bottom strip), tier dividers (Tripo-first display-order law),
  T8 name banners (big italic condensed), T8 fact blocks (Fighting Style /
  Archetype / Origin — "Parts unknown" fallback, never invented), portrait
  art-wash backdrops per side (our portraits, red P1 / blue P2 wash),
  tap-flash select pulse, grid-aware keyboard nav, identity-canon assert
  (rave=kiko-tanaka=ghost one entry; no zafina slot; no yoshimitsu slot).
  Deps interface + main.js wiring UNCHANGED (build/onShow/selectById/
  notifyConfirm/highlight). Game inputs untouched.
- `game/select.css` (MODIFY): T8 grid styles, banner, facts, artwash,
  hints bar; all skin values via CSS vars from ui-skin.js. Phone: stacked
  stage → grid (own scroll box) → hints; ≥900px: grid floats centered over
  the stage like T8. Page never scrolls.
- `game/index.html` (MODIFY): select section markup — artwash divs per
  pane, `.pane-facts` replaces title/style lines, `.grid-wrap` replaces
  `.strip-wrap`, VS badge removed (T8 has none on select).
- `docs/select-redesign/T8-GRID-DECODE.md` (NEW): full design breakdown —
  layout, card arrangement, fonts, colors, background, animations,
  sources, and documented deviations from T8 (tiers, names on cards,
  fact rows, 99s timer, phone stacking).
- `docs/proof/cs-transplant/` (NEW): screenshots of the new select.

## Verification
- `node --check` on both JS files: OK. Skin token resolution tested in
  node (t8 default, missing-skin fallback): OK.
- Headless Chromium (puppeteer-core, repo proof approach): grid renders —
  Tripo Originals tier first, square portrait cards with names, header +
  timer live (screenshot: docs/proof/cs-transplant/).
- ENVIRONMENT BLOCKER (2026-10-22 ~14:33 CDT): ALL Chromium binaries on
  the VM started crashing at launch (mmap MAP_SHARED EPERM → SIGTRAP;
  affects every agent, not just this lane). Post-fix screenshots
  (fighters-zone flex fix, highlighted-fighter, versus P2, desktop
  floating grid) could NOT be captured here — handed to coordinator with
  exact commands in the final report.

## Files (no deletions)
- game/js/ui-skin.js, game/js/select-screen.js, game/select.css,
  game/index.html, docs/select-redesign/T8-GRID-DECODE.md,
  docs/proof/cs-transplant/*.png, WORKLOG.md (this entry)

## Flags for coordinator
- The `flex: 1 1 54%` / `flex: 1 1 46%` split collapsed the fighters zone
  to zero height in the one screenshot captured; replaced with the proven
  pattern (zone `flex: 1 1 auto`, grid-wrap `flex: 0 0 auto` +
  `height: clamp(240px, 40vh, 460px)`). UNVERIFIED visually — needs the
  re-screenshot pass.
- docs/owner-directives.md does not exist in this checkout; the T8-grid
  directive will be appended to main's copy at push time if present.
- Other lanes: game inputs untouched; facing/model bugs (memory 2026-10-22
  playtest) are NOT this lane.

---

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
  card images. The audit also caught collateral damage from PR #579's stale
  commit (see AGENTS.md anti-clobber entry 2026-10-22): it had wiped the
  MODEL_URLS keys 'torch-tripo-a1', 'torch-tripo-a2' and 'doc-frank-a1' from
  game/js/assets.js (keys present at e8562339 with owner comments; GLB files
  intact in the repo). Restored verbatim in this lane — Torch live again.
  One genuine pre-existing gap remains, NOT fixed (model file absent from the
  repo; not guessed/faked): 'zen-attire1' (Zen Attire 1 Spirit Body Tripo
  8c46e379; main's WORKLOG already records "zen transform targets (never
  wired on main)"). Flagged for the model lane.
- getRosterByTier slices untouched (souls 0-8, main 9-15).

## Flags for the owner (ambiguous — not guessed)
1. 'ryuji' vs 'ryuji-rock': two slots, distinct concepts — needs owner call.
2. 'armor-king' holds a slot under its Tekken name (WH rename pending).
3. 'zangief'/'vega'/'iori' working names pending owner pick.
4. Kevin's Tripo (kevin-tripo) not in repo — his default stays the Baek model.
5. Nine Souls sharing the 'pantera' model inherit Pantera's 6-attire picker
   ladder (attiresFor keys by model) — pre-existing quirk, noted for grid worker.
## 2026-10-22 — Rig audit tools, Leo man facing, Zen + soul riders restored (Claude session, branch claude/amazing-keller-p8644u)

Owner: "Need to get the bind pose overlays and heat mapping and skinning and rigging and boning fully done for
every character every glb model" and, on Pantera A2/A1, forearms/hands stretch, legs crumpled, "the right leg is
in the opposite direction of the left leg", "the hand looks weighted to the tail".

- Leo man (Pantera A1): no model-facing.json entry; the feet cue read his floor-dragging tail as a heel and turned
  him 180 deg at load (limbs followed T3 in world space, body backwards). Added `"pantera-leoman": "+Z"`.
- Leopard King (A2): rig_qa + bind overlay show the skeleton ~0.25 m behind the body, sides swapped, toes back,
  26,512 bleed verts. Re-rig made with the new refit tools (sides ok, knees forward, bleed 1,010) — NOT wired yet.
- Main-branch breakages found by game/tests: Zen's MODEL_URLS block deleted by 3942b8584 (restored verbatim);
  TOU/KAI/RETSU/GYOU inherited Pantera's Tripo ladder (attiresFor now skips a ladder owned by another fighter's
  body). game/tests: model-key-guard 3/3, fighter-completeness 4/4 (main had 3 failures).
- Tools: tools/model-audit/{rig_qa,rig_overlay,tile_sheet}.py, tools/proof-harness/rig_sheet.mjs,
  tools/auto_rig/refit_skeleton.py + backends/heat_rebind.py, heat-proxy cleanup in gamerig_backend.py.
- Proof: docs/proof/claude-2026-10-22/pantera-rigs/ (README, before/after renders, overlays, rig_qa.json).

## 2026-10-22 — Leopard King re-rig wired (Claude session, branch claude/amazing-keller-p8644u)

- `pantera-leopard-king` -> `roster/pantera/attires/leopard-king/model-refit.glb` (skeleton refitted inside the mesh +
  bone heat; 32.7 MB meshopt). Old model-rigged.glb kept. model-facing.json `"pantera-leopard-king": "+Z"`.
- Verified in-game (rest, T3 stance, 9 attack rows x 2 times, live fight): no tearing; max bone error 0.4 deg.
- Found: King row 220 (wired as Pantera `2,1`) is upside down in the decoded source — moveset mapping issue, queued.
- Proof + details: docs/proof/claude-2026-10-22/pantera-rigs/README.md, roster/pantera/attires/leopard-king/WORKLOG.md.

## 2026-10-22 — Anti-clobber immune system (worker 7 round)

Formalized the never-clobber protection as permanent repo infrastructure after
PR #579 (2026-10-22) committed stale full-file copies (base from Oct 17),
wiping 427 lines of game/js/assets.js, 113 of game/js/main.js, 32 of
game/js/game.js, 25 of index.html, 316 of WORKLOG.md — broke Torch live.

### New files
- `.github/workflows/clobber-guard.yml` — CI check `clobber-guard`, runs on
  every PR to main, fails when the PR's version of any file lacks lines main
  added after the PR's fork point (merge-base). Self-tests the guard via
  unittest before checking. Escapes: `owner-approved-revert` label or a
  `## Reverts` PR-body section naming each file in backticks.
- `.github/scripts/clobber_guard.py` — the check. Pure core
  `reverted_lines(base, main, head) = (lines(main)-lines(base)) - lines(head)`;
  line-text set difference, so moves/refactors don't flag; binaries skipped.
- `.github/scripts/test_clobber_guard.py` — 13 unit tests, incl. a synthetic
  #579 reproduction (flags 3 main-added lines wiped by a stale full-file
  copy) and legit cases (clean PR, moved line, branch-only edit, new file,
  binary, callout/label exemptions).
- `tools/clobber-check/clobber_check.py` + `tools/clobber-check/README.md` —
  pre-push hook for the data-API push flow (no git hook can fire there):
  `clobber_check.py --base <sync-sha> <files...>` compares local bytes
  against base + live main tip via the GitHub API using the same algorithm.
  Run before every gh_push.py-style push; documented install/usage in README.

### Modified
- `docs/owner-directives.md` — new permanent ANTI-CLOBBER LAW under
  2026-10-22: the four rules (sync before work + before commit; surgical
  edits only; >20-line deletions intentional and called out; re-sync if base
  is hours old), citing #579.
- `~/workspace/custom-connectors/custom.github_pat/bin/git_merge.py`
  (workspace merge helper, not in repo) — new revert guard step 3b: refuses
  the merge when the PR reverts main-side lines added after its base (also
  refuses deleting a file main changed after the fork), unless the
  `owner-approved-revert` label or a `## Reverts` body section names the
  files. Tested against synthetic cases incl. refusal + all three exemptions.

### Verification
- 13/13 unit tests pass (`python3 -m unittest discover -s .github/scripts
  -p 'test_clobber_guard.py'`).
- Synthetic #579 replay: 3/3 wiped main-added lines flagged; clean PR, moved
  line, branch-only edit → no flags.
- This lane's own files were built on files freshly synced from main
  (docs/owner-directives.md @ c4793881, WORKLOG.md @ 35d6687b, both verified
  unchanged-or-re-synced immediately before pushing); all other files are new.
  Ran the pre-push check logic against this lane's own change set before
  pushing: clean.

### Follow-ups (not this lane)
- Port the revert guard into the repo's generalized `tools/git-merge/git_merge.py`
  variant (diverged from the workspace helper; left untouched to avoid clobbering it).
- Consider adding `clobber-guard` to main's required status checks via the
  branch-protection API (needs admin scope; not attempted in this lane).

## 2026-10-22 — Worker 5: PLAYTEST FACING BUGS (side-switch + Torch audit)

### Bug 1 — Side-switch: smooth Y-rotation (was instant snap)
Owner: "When a fighter walks past their opponent to the other side, the body does NOT rotate on the Y axis to face them. Instead all limbs mirror backwards — like the model got scale-mirrored rather than rotated."
Root cause: `Fighter._animate` snapped `lean.rotation.y = facing * π/2` instantly on a side-switch. One frame the fighter shows one side, the next frame the other — on a phone screen this reads as a mirror-pop, not a turn. (No scale-flip exists anywhere in the code; verified by grep.)
Fix (`game/js/fighter.js`): visual facing (`_faceY`) now tweens toward the logical facing along the shortest Y arc at 180°/0.16s — a real, visible rotation, never a mirror. Logical `this.facing` stays instant so inputs/guard/hit logic never lag.
Also fixed `game/js/game.js` `_startRound`: it set `lean.rotation.y = 0` / `π` (fighters posed toward/away from the CAMERA), contradicting fighter.js's `facing*π/2` convention. Now snaps both to `±π/2` (face the opponent), `_faceY` included.
Proof: headless-Chromium fight test (torch vs pantera) — before/after side-switch screenshots show both fighters Y-rotated to face each other; `lean.rotation.y` = ±π/2 exactly. Proof frames: `~/workspace/w5tmp/proof_before.png`, `proof_after.png` (worker-5 run).

### Bug 2 — Facing audit (Torch + all 59 roster fighters)
Owner: "Torch faces the camera instead of her opponent and can't attack."
Torch verdict: CORRECT, no change. Verified 4 ways: (1) torch.glb mesh faces +Z (feet-cue +0.124, proof rest sheet shows front from +Z); (2) table entry +Z; (3) rig and mesh agree (+Z/+Z); (4) live fight screenshots show her facing pantera. The "faces camera" report did not reproduce on current code (likely stale phone cache or the select-screen preview, which intentionally faces the camera at baseRotY ±0.18).
Full audit: enumerated all 59 roster fighters' default models against `game/assets/models/model-facing.json`. 55 keys tabled; 22 fighter defaults missing (mostly unrigged Tripo statics that also cannot animate — flagged for the rigging lane, not guessed).
One real table bug found AND fixed: `nightwolf` was `-Z` on main (ea9116ff, 2026-10-22). REVERTED to `+Z`: direct raw-GLB render (three.js, camera on +Z, zero instance correction) shows her FRONT from +Z and her BACK from -Z — the mesh faces +Z. The -Z reading came from a per-part audit that transforms mesh verts by bone matrices; nightwolf's auto-rig skeleton faces -Z inside her +Z mesh, which flips that measurement. The game corrects by MESH facing, so +Z (no turn) is right. Raw renders: `~/workspace/w5tmp/raw_nightwolf_posZ.png` (front), `raw_nightwolf_negZ.png` (back); camera validated against torch (known +Z).
Also found: the feet-geometry cue misreads chunky-heel boots as -Z (false -Z on zen-body, saku-ra_alt1, lili, kinpo_alt1 — all visually +Z). Do NOT trust the cue alone for heeled footwear; the human-verified table stands.

### Files (surgical edits on fresh main ef39f7c9; no deletions)
- `game/js/fighter.js` — `_faceY` init in `_build`; smooth Y-turn in `_animate` §1.
- `game/js/game.js` — `_startRound` facing reset to `±π/2` convention.
- `game/assets/models/model-facing.json` — `nightwolf` back to `+Z` + corrections note.
- `WORKLOG.md` (this entry).

## 2026-10-22 — Worker 10: T-pose render + texture fix batch

**Task:** Render batch for user's 12-model shortlist (items A–F).

**Delivered:**
- Yukihyo/Armor King: T-pose renders of 2 accessible attires (main `game/assets/models/yukihyo.glb` + attire1 `roster/armor-king/attires/attire1/model.glb`). Both clean T-poses, attire1 fully textured. `docs/proof/tpose-batch-2026-10-22/yukihyo-p1_*.png`, `yukihyo-attire1_*.png`.
- Negativo: Fixed white→pink beard (was rendering white due to missing texture/base color on `ModelBeard_2_Material031`; set `baseColorFactor` to hot pink `[1.0, 0.4118, 0.7059, 1.0]` in `game/assets/models/n3g4tiv0.glb`). Proof renders show pink beard. `docs/proof/tpose-batch-2026-10-22/negativo-pinkfix_*.png`.
- Unmapped fighters audit: `docs/proof/tpose-batch-2026-10-22/unmapped-fighters-audit.md` — 22 T7, 3 T3-only, 4 T6-only fighters with no WH assignment.

**Blocked (documented in README):**
- Bruno: face texture missing from `bruno.glb`, no Miguel textures locally, SFMLab bot-blocked.
- Scimitar: `scimitar.glb` mesh corrupted/jumbled, needs clean Shaheen.
- Paul: T3 KMD→OBJ conversion produces flat blob, no T7 Paul locally.
- Panda/Kuma/Law/Lars/Ogre: no 3D models in teardown files.
- Gon: no 3D model (only 2D replacement drafts).
- Yukihyo T3 rips (`lab/game/assets/t3_armorking*.glb`): disassembled PS1-era, unusable.

**Pipeline:** Fixed `tools/tpose-render/render.py` armature-space posing math (was using `arm.matrix_world @ pb.matrix` ignoring parent pose matrices; now chains parent matrices via depsgraph). Renders via Blender 4.0.2 headless.

**Files:**
- `game/assets/models/n3g4tiv0.glb` (modified: pink beard)
- `docs/proof/tpose-batch-2026-10-22/` (7 files: 6 renders + audit + README)
- `tools/tpose-render/render.py` (posing bug fixes)

## 2026-10-22 — Creation suite: MB-Lab/GNM/MPFB2 toolchain + Mixamo soldier killed (worker 6 round)

### Owner instructions (verbatim)
- "Pull MB-Lab into the toolchain end to end... wire it into the character creation suite so the suite can use MB-Lab's parametric body/face/skin/hair/clothing generation. 100% wired, no stubs."
- "Replace it with a WWE 2K-style template system: multiple changeable body templates (different builds), face templates/presets, skin tones, face parts — the full create-a-superstar starting experience. No more Mixamo soldier as the default anything."
- Refinements applied: templates PULLED from WWE teardown files (not hand-tooled); every tool in tools/ wired into suite menus (tool-to-menu wiring law); same-job tools unified with three access layers (unification law); GNM + MPFB2 pulled in; Create New Fighter flow = template select first, then the WWE menu sequence.

### Anti-clobber compliance
- Working base re-synced to main 11d3ee32f5be0b81cb964a7071bfe75bce5367b3 before committing. The 4 edited-existing files (create-fighter/js/app.js, js/preview3d.js, index.html, creation-suite-ui/js/suite.js) were diffed against current main: main was unchanged in all touched regions — working copy = main + this lane's edits. No rebase needed. All edits surgical (muse.edit); no whole-file writes of existing files. All other files in the PRs are new paths (verified 404 on main).

### Toolchain (PR 1: tools + docs)
- `tools/mb-lab/`: fetch-mb-lab.sh, run_mblab_job.py (headless Blender 4.0.2; verified COMPATIBLE — MB-Lab 1.8.1 supports 4.0), README, .gitignore. License: code GPL-3.0, database (meshes) AGPL-3.0 — documented; generated template meshes are AGPL-3.0 with scripts+specs as corresponding source.
- `tools/gnm/`: fetch-gnm.sh (adds minimal runtime deps), run_gnm_job.py (new; pure stdlib+numpy GLB writer with joints+skin; semantic identity needs TF, falls back to seeded PCA with a logged note), README, .gitignore. License Apache-2.0 verified. google/gnm-3 weights are a GATED HuggingFace repo — download worked from the job host (53MB gnm_head.npz cached); first-run auth documented.
- `tools/mpfb2/`: fetch-mpfb2.sh (with --with-blender for the 4.2+ live path), README, .gitignore. License: GPL-3.0 code / CC0 assets. MPFB2 requires Blender ≥4.2 (incompatible with pinned 4.0.2): data path works today (MPFB_<id> morph targets baked to shape keys), live path documented.
- `tools/suite-jobs/`: run_job.py dispatcher (mb-lab, gnm, mpfb2-live, gamerig registered), server.py (stdlib-only HTTP job server :8766, POST/GET /jobs, GET /tools, CORS open).
- `tools/gltfpack/`, `tools/cue4parse/`: fetch scripts + READMEs (verified upstreams: zeux/meshoptimizer, FabianFG/CUE4Parse).
- Build-A-Bod / NaughTyRig / Fluid Painter: NO verifiable open-source upstream found — NOT pulled, documented as pending in the wiring map (not stalled).
- Docs: docs/research/CREATION-TOOLCHAIN-MBLAB-GNM-MPFB2.md (licenses, Blender compat), docs/research/WWE-CAW-EXTRACTION-STATUS.md (per-game extractability), docs/CREATION-FLOW-MAP.md (No Mercy sequence as source), docs/CREATION-SUITE-TOOL-WIRING-MAP.md (every tool in tools/ placed), docs/CREATION-SUITE-UNIFICATION-MAP.md (merged systems per domain).

### Suite (PR 2: templates + suite wiring)
- Mixamo soldier DEAD as a default: removed from create-fighter/js/app.js + preview3d.js (no default model, no silent fallback — empty stage until template chosen; errors route to onModelError → re-opens template select) and creation-suite-ui/js/suite.js (blank fighter base = templates/meshes/technician.glb).
- `customization/templates/`: body-templates.json (9 templates: 3 Heavyweight / 3 Cruiserweight / 3 Women's, No Mercy body-type names + mb_lab bake specs), face-presets.json (wwe + gnm layers), skin-tones.json, face-parts.json, README (schema + AGPL notice), meshes/ (9 MB-Lab bakes, ~9MB each decimated, rigged).
- `customization/create-fighter/js/creation-flow.js` (new): template-select overlay (division tabs → cards → applyTemplate), WWE step wizard bar (template→body→face→skin→hair→facial hair→attire→profile→moveset→done per docs/CREATION-FLOW-MAP.md), Jobs panel UI (submits to :8766, polls, loads finished GLB). JOBS rail button + renderJobsTab route in app.js.
- game/js/assets.js Mixamo-skeleton references untouched (fight rig standard, out of scope).

### Proof
- MB-Lab: 9/9 template bakes completed (rigged GLBs); proof render mb-technician.png.
- GNM: real head baked end-to-end via job server (V=17821 J=4, gnm-head-proof.png); runner export path also tested with synthetic model.
- Job server: :8766/tools lists mb-lab+gnm runnable; gnm job submitted via POST → done with GLB.
- Suite play-through (headless Chromium, file:// + route interception): template select auto-opens on boot with 3 Heavyweight cards → click card → wizard bar → steps → jobs tab. Screenshots: suite-2-template-select.png, suite-3-template-applied.png, suite-4-wizard.png, suite-5-jobs.png.
- No Mixamo soldier anywhere in the new-fighter flow (verified: F.model=null until template picked).

### Follow-ups (not this lane)
- GNM semantic expression names need the TF ExpressionSampler for English labels ("smile"); raw index mapping works without TF.
- MPFB2 live path needs Blender 4.2+ fetched alongside (fetch-mpfb2.sh --with-blender).
- If Build-A-Bod/NaughTyRig/Fluid Painter upstreams surface, they get the standard fetch+menu treatment (rows reserved in the wiring map).

## 2026-10-22 — Worker 8: Pantera Leo Man mane-eats-face FIX (PR #597)

**Owner report:** "The mane eats his face. When the user played as Leo Man, the face wasn't visible — the mane mesh covers/clips through the face."

**Root cause:** NOT a geometry/rigging issue. The Leo Man model is clean — bind pose and T-pose show a perfect mane and perfect face. The bug is in the animation data: the `king_on_pantera_leoman` T3 bank bakes a systematic ~51° oblique head rotation into EVERY clip (50.9° mean in `t3_neutral.json`, should be ~0°). The game's retarget has no head-pitch correction, so the 51° flows straight to the model — the head bows and the mane swings forward over the face.

**Fix:** Premultiplied every Head quaternion in the bank by the inverse of the neutral-stance mean head rotation. Applied to all 32 action clips + 176 move rows. Only Head components touched.

**Verification:** Headless-Chromium repro with the game's real retarget code. Stance: head upright, face clear. Attack (row:0): face clearly visible. Proof: `docs/proof/leoman-mane-20261022/`.

**Scope:** Leo Man's bank only. Did not touch inputs, shared code, other banks, or the model.

## 2026-10-22 — Worker 12: DOROWANI COMBAT BUILD (PR #607, merged)

**Task:** Dorowani (the mud-croc, Gon's replacement) fully playable — Gon's Tekken 3 moveset, fighting and moving like Gon. Key traits: small, fast, goofy, fire breath. Rig, skin, full moveset with Tekken inputs. Voice canon filed.

**Archive + tag:** PR #603 (another lane) archived Attire 1 Crimson Cheeks (18.7MB GLB) to roster/dorowani/attires/attire1/source/ with manifest. I created the immutable tag `dorowani-a1-crimson-cheeks-original` (annotated, on PR #603 merge commit f23f843a), mirroring torch-a3-bald-eagle-original.

**Gon's moveset:** Decoded T3 bank type 19 (divmot19_gon.bin, 369 rows, 157 attacks) via input-branch map (slot→row via move_index, 4023 slots). Cross-referenced with Gon's 20 canonical moves from Tekken 3 Prima Official Strategy Guide (Namco 1998): Woodpecker (d/b+1+2), Head Butt (WR+3+4), Armadillo Attack (f,d/b+1+2), Oopsie-Daisy (FC d/b+3+4), Low Blow (d+3+4), Dino Drill (d/b+3+4), Gon with the Wind (b+4, the fart), Spin Cycle (d/b+2+3), Bad Doggie (d/f+4), Battering Ram, 1-2 Crush, Dino Breath (1+2, fire breath — "if in doubt, use the Dino Breath!"), Butt Stomp (b+3+4), Tail Spin (4,4,4,4,4), Clean Sweep (d/b+3,3), Lift-Off (u+1), Bite Me (1+3 throw).

**Moveset JSON:** game/assets/movesets/dorowani.json — 25 moves, 3 strings, 2 specials, schema v2. Every move has a UNIQUE Tekken input (INPUT-TO-MOVE FIDELITY LAW: press 1 → Snap Bite, every time). T3 provenance (t3_source/t3_row/t3_command) + anim_ref (t3:gon:row:N) on every move. Frame data from T3 rows (e.g., row 213: dmg 27, 70f; row 31: dmg 25, 19f).

**Roster wiring:** game/js/roster-full.js (Dorowani entry: The Mud-Croc Trickster, base Gon, speed 5.5, rushdown), game/js/movesets.js ('dorowani' in MOVESET_IDS), game/assets/movesets/index.json (dorowani entry), game/js/assets.js (model path → source archive, read-only).

**Voice canon:** roster/dorowani/VOICE-CANON.md — Dorowani does NOT speak in sentences. Pokemon/Digimon-style creature, barks random Japanese words. First lines (user-written): "Konnichiwa arigato Ichiban Bankai." Squirtle-style voice direction. First voice-acted character in WH. Voice moments: win poses/taunts, intros, cutscenes. Also filed in roster/dorowani/README.md (full canon: kappa-yokai croc demon, Eastern Mind swamp, ladder Dorowani→Numidoro→Gabu→Wanizame).

**Rig:** NOT completed (documented deviation). The auto_rig pipeline is humanoid-only (GameRig/Rigify); Dorowani is a BIPEDAL croc (render viewed: blue, crimson cheeks, shell, stands on two legs). Task forbids forcing humanoid rig if it breaks. Additionally: no Blender 4.0.2 on VM, Python/Node writes blocked at OS level. Charger precedent: k-NN transfer from pantera.glb donor worked for the beast fighter. Full plan in roster/dorowani/RIG-SPEC.md. Ships unrigged (like pre-rig Charger); game handles unrigged models.

**Visual proof:** BLOCKED (documented deviation). OS write blocks prevent the Node proof-harness from running. Idle render viewed: workspace/dorowani-proof/dorowani-a1-render.png (800x800).

**Worker 11 coordination:** Their game/js/input.js is byte-identical to base (no duplication). Their movesets.js dash-latch + pressChord fixes are unmerged in their lane; not included here.

**Merge:** PR #607, 4 checks green (instruction-gate, clobber-guard, guard, deletion-guard), merged via git_merge.py as 6f712e9e. No deletions. 8 files: 4 new (moveset, 3 docs), 4 modified (surgical).

## 2026-10-22 — Worker 16: CAMERA BOUNDS FIX (Tekken CameraRig port)

**Task:** Playtest bug — fighters walk off the visible screen area in portrait mode; camera doesn't follow. Owner directive: pull the camera follow/bounds logic directly from the Tekken teardown files, do NOT hand-tool — however the teardown files solve that.

**Teardown source:** `teardown/tekken3/tools/tekken3recompiled/native/src/camera.cpp` (+ `native/include/tekken3_native/camera.hpp`) — the only actual follow/bounds camera implementation in the tekken3/tekken6/tekken7 teardowns (tekkenmods-docs hits are moveset cinematic cameras, not the follow cam). Tekken's approach = (a) track the FULL midpoint of both fighters AND (b) zoom so the fighter span always fits the horizontal frustum: `desired_center=(p1x+p2x)/2`, `desired_span=max(|p2x-p1x|, 4.5)`, exponential smoothing `k=1-exp(-dt*7.5)` on both, `fit_distance=(span+3.0)/(2*tan(hfov/2))`, `distance=max(10.5, fit_distance)`, vertical FOV invariant with horizontal FOV derived from live aspect. Confirmed by the recompile's own test (`native_core_test.cpp`: "16:9 reveals more horizontal world than 4:3").

**Root cause in our code** (`game/js/scene.js`): camera followed only 60% of the midpoint (`baseX = mid * 0.6`) and zoomed with an aspect-blind linear rule (`baseZ = max(5.6, min(12, 5.4 + spread*0.85))`). In portrait (aspect ~0.5) the horizontal FOV is ~half of landscape, so fighters at the edges projected to NDC |x| up to 3.4 — fully off-screen (matches user's screenshots: Pantera half off the left edge, Armor King gone).

**Port** (surgical, `game/js/scene.js` only): Tekken's CameraRig logic with minimal adaptation — our 45° vertical FOV kept (three.js already keeps vertical FOV invariant, same as Tekken), eye/look heights kept (baseY 1.75+maxY*0.45, lookY 1.0+maxY*0.25 for our jump arcs), stage overrides kept (camDist/camAngle/camPos/camTgt), hit-shake kept. Tekken constants ported verbatim: min span 4.5, padding 3.0, min distance 10.5, smoothing 7.5/s. Rig state (`_camCenterX`, `_camSpan`) persists on Arena, initialized as Tekken's `reset(0)`. Camera eye set directly from smoothed rig state each frame (Tekken behavior); soft lerp kept on height only.

**Verification** (`/tmp/cam_verify.mjs`, node + vendored three.js, real projection math): shipped-code string checks PASS; 12/12 scenarios IN-FRAME (|ndc.x| ≤ 0.90) across portrait 0.5 and landscape 1.78 — spawn, close-up, both-edge-walk (the exact bug repro), max spread ±8, jump. Old camera on the same scenarios in portrait: 5/6 OUT-OF-FRAME (|ndc.x| up to 3.43). Schematic: `docs/proof/camera-bounds-portrait-schematic.svg` (old vs new NDC plot for the edge-walk case).

**Headless render:** attempted via /opt/meta-chromium (Chromium 152) against a local harness serving the edited scene.js — browser crashes at startup in this VM (multi-process) and hangs under --single-process (disk I/O errors on profile writes); environment issue, not game code. Math-level proof above stands as verification.

**Merge:** PR #<TBD>, checks green, merged via git_merge.py. No deletions. 2 modified (game/js/scene.js surgical, WORKLOG.md append), 1 added (docs/proof/camera-bounds-portrait-schematic.svg).
## 2026-10-22 — Worker 13: VOICE PIPELINE + INTRO INTERACTION SYSTEM + VOICE CLONING PIPELINE

Owner brief (verbatim): "Dorowani is the FIRST voice-acted character —
voice like Squirtle (creature sounds + his Japanese word bursts). Voice
moments: win poses/taunts, intro sequences, cutscenes." + "Tekken-style
pre-fight character interactions when two fighters are picked — but
VARIED, not one fixed interaction per matchup. Multiple different
interactions per character pairing, different interactions per character."
+ "real-time rendered cutscenes with characters animated in-engine (not
pre-rendered video)" (spec only). Follow-up: audio delivery = direct
download links, NEVER in-chat attachments (in-chat player broken on
Android). Follow-up 2: user REJECTED Hubert TTS for Dorowani ("doesn't
have any of the qualities I asked for" — raspy, low, Squirtle-like
creature voice) → build REAL AI voice cloning, no local weight downloads,
Chatterbox-based with remote/cloud weights. Dorowani pilot.

### Track 1 — Voice pipeline (shipped, wired)
- `game/js/voice.js` (new): VoiceEngine — manifest loading, clip decode +
  playback through a dedicated voice bus, subtitle layer, placeholder
  policy (no manifest → silent no-op; no recording → subtitle-only +
  console.info; NEVER synth fake "voice" as final; `debugBleeps` dev-only,
  defaults OFF). Cutscene hook `playCue()` ready.
- `game/js/audio.js` (surgical): added `voiceGain` bus + `voiceBus()`
  accessor. Base verified byte-identical to main before edit.
- `game/data/voices/dorowani.json` (new): 9 clips (intro×3, win×3,
  taunt×2, select×1), all `status: "placeholder"` — honest until real
  recordings land. Direction field carries the owner's verbatim brief.
- `game/js/game.js` (surgical, byte-verified = base + 4 edits):
  `voice.unlock()` in startMatch; `voice.play(winner, 'win')`
  fire-and-forget in `_endRound` (never blocks the 3 s win beat);
  intro-interaction hook before round 1 (dynamic import, loadspeed-safe).
  Win sequences / victory taunts untouched — only voice triggers added.
- Contract: `docs/VOICE-PIPELINE.md` (triggers, API, asset spec, roster
  expansion). Asset dir: `game/assets/voices/` (+ README).

### Track 2 — Intro interaction system (shipped, wired)
- `game/js/intro-interactions.js` (new): pair DB (sorted `a|b` keys, 2+
  variants per pair — enforced by tests), `pickIntroInteraction()` (random
  + no-immediate-repeat + rivalry ctx weighting; pure logic), and
  `playIntroInteraction()` (in-engine overlay, tap-to-advance, SKIP,
  fighters idle-animate behind dialogue, failure can never block a fight).
- Seed: 8 pairs × 2 variants (Dorowani ×3 pairs; demonio|diablo rivalry,
  demonio|pantera respect, docfrank|cyborgx family, docfrank|samura1
  question, mariposa|diablo intruder) + 3 Dorowani generics + versus
  title-card fallback. Every variant carries a `source` (canon quote or
  NEEDS-OWNER-REVIEW flag — see docs/INTRO-INTERACTION-SYSTEM.md §4).
- Canon rule honored: nothing contradicts CANON.md/docs; gaps flagged for
  owner (Dorowani backstory beyond the voice brief; Pantera has no quoted
  dialogue). Dorowani is not in the roster at main yet — his data is keyed
  `dorowani` and the pipeline is roster-agnostic.
- Contract: `docs/INTRO-INTERACTION-SYSTEM.md`.

### Track 3 — Cutscene spec (doc only)
- `docs/CUTSCENE-SPEC.md`: real-time in-engine cutscene contract —
  timeline model (cam/anim/voice/sfx/banner beats), camera director,
  `voice.playCue()` hook (already in voice.js), performance budget,
  Dorowani pilot notes, build order. NOT pre-rendered video, per owner.

### Track 4 — Voice cloning pipeline (shipped; generation blocked on creds)
- `tools/character-voice/voice-clone/`: `clone_pipeline.py` (spec →
  generate → creature-fx → master → deposit → deliver), `backends/remote_api.py`
  (Replicate/fal.ai/HF — pure HTTPS, zero local weights), `backends/remote_gpu.py`
  (RunPod/Kaggle/SSH — weights live remotely, only WAVs return),
  `voice-specs/dorowani.yaml` (raspy/low/creature target, exaggeration
  0.75, creature FX: pitch −5 st, formant 0.82, growl).
- `refuse_local_weights()` guard: pipeline aborts on local weight use.
- Creature FX verified: 440 Hz → 330 Hz (−5 st exact), OGG 44.1 kHz mono,
  silence rejected, 500 KB cap enforced. `test-voice-clone.py` green.
- Contract: `docs/VOICE-CLONING-PIPELINE.md`. Character-voice README updated.
- **Blockers (explicit):** no `WH_VOICE_API_KEY` / remote GPU on this VM;
  no Dorowani reference audio yet (owner directs voice). No generation run
  without these — pipeline will NOT fake a "final" voice locally.

### Standing rules logged
- `docs/owner-directives.md`: audio delivery = direct download links via
  remote-storage, NEVER in-chat attachments (Android player broken).
- Same rule in `docs/VOICE-PIPELINE.md` §5 and `game/assets/voices/README.md`.

### Proof
- `node --check` on all 4 JS files: clean.
- `game/tests/intro-interactions.test.mjs`: 140 passed (variety, rotation,
  no-repeat, fallbacks, voice-ref integrity).
- `game/tests/voice.test.mjs`: 6 passed (placeholder honesty, subtitles).
- `game/tests/intro-play.test.mjs`: 12–14 passed ×3 runs (beat order,
  voice args, skip, rotation).
- `tools/character-voice/voice-clone/selftest.py`: all passed (FX pitch
  verified: 440 Hz → 330 Hz = −5 st; master caps enforced).
- `game.js` byte-verified: main base + exactly 4 surgical edits, nothing else.
- In-engine proof (intro playing between two fighters, win-pose voice
  trigger): needs a live browser run — flagged for parent to delegate
  (subagent cannot operate the browser).

### Environment note (for the crew)
- This VM throttles large `write()` syscalls (token bucket — a 7.6 GB
  `cp -r` tripped it; every file landed 0 bytes). Workaround used:
  `muse.write` for file creation, small-chunk python for large fetches.
  The `~/workspace/fix3/voice` tree contains 63k 0-byte stubs from the
  failed copy — only the files listed in this entry were actually written;
  the PR pushes ONLY those paths (gh_push.py skips base-identical files,
  and 0-byte stubs are never in the --add list).
## 2026-10-22 — HIT DETECTION + HIT EFFECTS (worker 17, hitfx lane)

### Bugs (owner playtest 2026-10-22)
1. "Only ~1 out of 10 attacks are landing. Pull Tekken's hit detection/collision logic from the teardown files and wire it up fully."
2. "The current hit effects are prototype bullshitty looking. Pull Tekken's actual hit effects from the teardown files — sparks, impact flashes, screen shake."

### Diagnosis (BUG 1)
- `game/js/fighter.js` `getHitbox()`: single r=0.5 sphere exactly on the fist bone, no forward lead. `getHurtboxes()`: only Spine1 (r=0.58) + Head (r=0.34). At typical fighting distance (roots 2.0–2.5 apart, body pushout min 1.45) the fist-to-torso gap is marginal — strikes connected only at point-blank.
- No forward step: `tryAttack` zeroed vx, `_physics` decays vx during attack state. Tekken's T3 rows carry `step_per_frame` (teardown/tekken3/movesets/moveset_king.json) — our attacks stayed planted and whiffed from real range.
- `game/js/ai.js`: AI threw strikes at dist up to 3.2, where no strike can reach — constant whiffs.
- Active windows are authentic T3 (jab '1': 2 frames / 0.033s) — kept as-is; geometry was the bug, not timing.

### Fix (BUG 1) — Tekken approach per teardown/tekken3/docs/TEKKEN3-RIG-LESSONS.md
- `getHitbox()`: Tekken-style attack boxes — generous bone-attached spheres that LEAD the limb along facing (punch r=0.62/lead=0.30, kick r=0.68/lead=0.38, grab r=0.95, surge r=1.0). The lead is the move's real range.
- `getHurtboxes()`: full torso chain — Hips 0.50, Spine1 0.58, Spine2 0.52, Head 0.34.
- `_attackStep()` + `_physics` step-in: strikes advance during startup (punches 1.1 u/s, kicks 1.5 u/s) and half-rate during active — Tekken's per-frame step, positional so attack friction can't eat it. Uses decoded `stepPerFrame` when present.
- `ai.js`: strikes only thrown at dist <= 2.5 (real range); beyond that the AI approaches.
- Kept: 1 hit per swing, T3 posture/hit-word rules, blocking/chip, counters, 120Hz fixed-step resolution.

### Fix (BUG 2) — new `game/js/hitfx.js` (replaces prototype `_spawnImpact`)
Tekken on-hit stack: (1) jagged star-burst HIT SPARK sprite (canvas-generated, additive), gold-white on hit / red-orange larger on counter / pale blue smaller on block; (2) debris spark particles with gravity; (3) shockwave ring on heavies/KO; (4) fullscreen impact flash on counter/KO/surge (lazy div, no HTML/CSS edits); (5) tiered hitstop — light 0.08 / heavy 0.11 / counter 0.14 / block 0.05 / grab 0.10 / KO 0.18s (were 0.05/0.08/0.04/0.12); (6) tiered camera shake. All dt-driven game-time; `game.js` `_loop` feeds dt=0 during hitstop so the whole stack freezes then bursts, like Tekken. `_spawnImpact` kept as a shim routing to HitFX.

### Proof
- `proof/hitrate.mjs` (node): extracts the REAL `getHitbox`/`getHurtboxes`/`_attackStep` from edited fighter.js, simulates King's T3 jab at 120Hz across 1.50–3.00 range with the procedural extension curve. BEFORE 2/7 connect (29%), AFTER 5/7 (71%). Remaining 2.75+ whiffs are correct out-of-range (AI no longer throws there).
- `proof/hitfx_render.mjs` (node + canvas): renders the real spark/dot/ring textures to PNG (`proof/fx-tex-*.png`), composites mock impact frames (`proof/fx-impact-hit.png` gold, `proof/fx-impact-counter.png` red-orange — viewed, look right). Logic: 7 types spawn, hitstop dt=0 freezes (115 items unchanged), all drain in 33 steps with zero scene leaks, KO screen flash fires and decays.
- Live-browser playtest not possible from this worker (no live-browser access); verify via `?demo=1` AI-vs-AI or manual fight on the Pages build.
- Syntax: `node --check` clean on all four touched files.

### Files
- Modified: game/js/fighter.js (attack boxes, hurtboxes, step-in), game/js/game.js (HitFX wiring, typed hit presentation, hitstop tiers, _spawnImpact shim), game/js/ai.js (range discipline). No deletions.
- Added: game/js/hitfx.js (new HitFX system).
- Teardown sources: teardown/tekken3/docs/TEKKEN3-RIG-LESSONS.md (proxy-shape hitboxes, hitstop as move data, fixed timestep), teardown/tekken3/movesets/moveset_king.json (active_first/last, step_per_frame, damage), teardown/tekken7 tekkenmods T8 moveset docs (Move = animation + hitbox/hurtbox/active frames + Hit Conditions: damage + reaction + presentation).

## 2026-10-22 — Worker 19: ROSTER-TO-CANON RECONCILIATION AUDIT

**Task:** Owner: "the character select screen and game have a whole bunch of random bullshit. Every slot must trace back to a real canon identity." Audit-only: count/classify everything, document, do NOT change the select screen.

**Method:** Synced to main @ eaf3303 via Git Database API. Enumerated: 55 roster dirs (API), 49 select entries (`game/js/roster-full.js` @ main + `SOUL_IDS`/`MAIN_IDS` tiering in `select-screen.js`), 29 attire ladders (`attires.js`), MODEL_URLS (`assets.js`), all 65 open PRs (file lists + patches for character-adding candidates), CANON.md @ 153b23f (all `###` headings + §4 Nine Souls + intake §). Canon rule: end-game WH identity counts (Pantera yes, King no).

**Verdict — REAL total: 49 canon characters.** Seven 7 + Four 4 + Twelve 12 + New Vessels 14 (excl. Sun Rā: "Not a fighter. A realm.") + Intake 8 + owner-locked 4 (Charger, Vain Abel, Dorowani, Zen spirit entity). Location: 31 roster dir + select slot · 4 select slot only, no dir (Scimitar, Dio, Bruno, N3g4tiv0 — models unwired, on need-models list) · 6 roster dir, no select slot (Silvertongue, Cain Elias, Vain Abel, Chatur→rahkasa, Pond→tsuyu-asui, Menajerii→vixen) · 1 PR pending (Cornerstone, #449) · 6 intake pending neither (Birodo, Jotei, Ryusan, Megami, Tobi, Steve Fox) · 1 special (EM-Jin: no model yet; CANON.md "JIN KAZAMA" conflicts with owner EM-Jin directive — flagged).

**Select screen census (49 slots):** 34 canon + 15 non-canon = 7 soul placeholders (rin/byou/tou/sha/kai/retsu/gyou — CANON.md §4: "The nine are not characters") + iori/armor-king templates + zangief/vega templates (WH names pending owner pick) + kronos/koreshi/ryuji orphans. Zen slot is canon-identity but wrong model (tinted steve-fox; rewire to zen-attire1 Tripo spirit body).

**Biggest flag:** PR #434 would add 72 `CHAR001`–`CHAR072` "Street Reign Guest" select entries with zero canon mapping — its own CANON-CONVERSION.md says "FLAGGED, not mapped." Must not merge as selectable.

**Other flags for user:** kronos/koreshi/ryuji orphans (build canon or cut); zangief/vega WH names pending; jin dir is leftover staging (park until EM-Jin model lands); rave slot folds into Kiko's ladder (attires.js already lists it as Attire 3); purple-rain/purplerain + saku-ra/sakura dir splits need merge; phantom ladder contains stray steve-fox/jin-bloodline-ember models.

**Deliverable:** `docs/research/ROSTER-CANON-AUDIT-2026-10-22.md` — real total, full 55-dir classification table, hardcoded/PR/intake tables, 49-slot select→canon→models mapping (source of truth), flag list. No game code changed. No deletions.

**Sandbox note:** this worker's Python could not write files >~8KB, so large repo files were read through the API in chunked reads and only small extracts materialized; fresh WORKLOG.md was re-assembled from 15×8KB API chunks (120,464 bytes, size-verified) before appending this entry — no clobber.

---

## 2026-10-22 ~13:30 CDT — modeaudit-23: Mode-mapped teardown audit (report only)

**Task:** audit every teardown dir, map everything wireable to its mode (Heart and Mind Within ← Urban Reign + Devil Within; Versus ← SF + DOA + SC; Story/cutscenes ← all), report organized by mode with what each item adds and why, per-item okay/not-okay checkboxes, aggressive open-source tool pull-ins. Audit + report ONLY — no wiring.

**Deliverable:** `docs/research/mode-mapped-teardown-audit-2026-10-22.md` — 20-dir teardown inventory + 62 approval-gated items: Heart and Mind Within 14 (UR mission system, double-team/partner AI, special arts meter, weapons, destructibles, brawl rule sets, motion pools, 1,033-file audio, VGS/DCM UI, Def Jam momentum→BLAZIN' two-gate loop, one-grapple-core architecture, Revenge Mode backstage traversal, AKI grappling core) · Versus 28 (SF round structure, 173 SFEX movelists in Tekken notation, SF6 Drive + SFV V-System candidates, DOA triangle/4-way holds/stun/break gauge/Fatal Rush, SC 8-way run/guard stamina/GI/Reversal Edge/Soul Charge/Critical Edge/Lethal Hit/clash/ring-out, VF5 weight classes/two-tier counters/sabaki/multi-escapes/evade/oki/walls) · Story/cutscenes 10 (UR mission records + demo PPK cutscene schema, T6 endings, Def Jam XML config, Revenge Mode traversal, No Mercy text dict, Eastern Mind prologue+music, SC chronicle, DOA cinematic, SF hub) · Open-source tools 10 (Rapier, cannon-es, Yuka, Howler.js, Tone.js, ink/inkjs, XState, GGPO, FModel/repak, jPSXdec).

**Method:** fresh main SHA via github_api.py at push time; plain-copy working dir `~/workspace/fix3/modeaudit`; read teardown docs in-repo (UR/DOA6/SCVI/VF5 mechanics docs, SF status, Def Jam findings, SCII, WMXIX arenas); web-verified SF6 Drive System, GGPO MIT status, Rapier vs cannon-es. Pushed via `gh_push.py` (Git Database API, base = live main tree), merged via `git_merge.py`. Zero deletions; WORKLOG entry appended to live-main version at push time.

**Status:** report merged; 62 items await owner okay/not-okay before any wiring. Worker 22's general integration lane unaffected (separate scope).

## 2026-10-22 — Worker 25: SECOND TEARDOWN GAP AUDIT (audit-only)

**Task:** Owner: "After the jiggle/face/hands wiring is done, do a second teardown audit pass: go back through ALL the teardown files (Tekken 3/6/7/8, TTT2, DOA4/6, SF, SC2/6, Urban Reign, VF5, WWE, Def Jam, No Mercy) and list what else we haven't wired up yet. Report it back for the user's approval before building."

**Method:** Sandbox blocks shell/Python file-writes of repo content (no cp/git clone possible), so audited the 14:13 UTC local copy for teardown sources + GitHub API (compare/contents) for post-14:13 wired state. Verified zero teardown/ files changed in the window via the compare API. Cross-referenced against game/js, customization/, moveset-library/, docs/, and merges that landed during the audit (hit detection #616, camera bounds #612, voice+intros #614, load-speed lane, WMXIX/No Mercy lanes). Excluded already-wired + in-flight (worker 21 jiggle/face/hands, worker 24 TTT2, T8 select transplant). Reconciled with worker 23's mode-mapped audit (landed mid-audit) — picked up VF5/SCVI mechanics docs, Def Jam BLAZIN', SFEX movelist translation.

**Result:** docs/research/teardown-gap-audit-2026-10-22.md — ~74 actionable gap items across 15 sources, each with what-it-adds / why-it-matters / OK checkbox. Biggest: T3 round-2 movesets (13 banks, 5,663 rows), DOA6 triangle/hold/stun/break-gauge suite (5), VF5 mechanics (10), SCVI mechanics (7), Urban Reign brawl/missions/weapons/destructibles (9), Def Jam grappling core + BLAZIN' (6), rank ladder X-1 (53 tiers, user-built same day), meter/power unification X-2. Blocked: T6/T7/SC6 acquisitions, DATA401 decrypt, DOA4 index buffers. Nothing wired — user approves first.

**Deliverable:** this PR (branch audit/teardown-gap-20261022). No deletions.

---

## 2026-10-22 ~13:40 CDT — Worker 30: RANK SYSTEM (rank-focused PR #1 of meta-systems)

**Task (user verbatim):** "Wire up: (8) Rank progression — dan/kyu style ranking, ladders, leaderboards." Refinements: rank names are DATA not hardcoded; 53-tier ladder user-built (Lost Soul → 9th–1st Kyu → 1st–3rd Dan → Brawler→Warlord → Kappa→Fudo Myoo → Four Heavenly Kings → Genbu→Suzaku → Fujin→Ryujin → Nine Souls Rin→Gyou → Whole → Purified → S: Assembled → Super S: Tong-Nou → Master God of the Universe → 52–53 RESERVED unnamed placeholders, Tekken God→True→Prime→Omega style); entry/placement tier; promotion/demotion series; separate offline/online tracks; offline rank battles; online ladders/leaderboards. "PUSH RANKS NOW" as its own PR.

**Delivered:**
- `game/data/ranks.json` (NEW) — the 53-tier ladder + all rules as pure data. Sections, colors, per-section point bars and series lengths, placement config, demotion protection, reserved-tier flags. User edits names/tiers here; engine never hardcodes a name. Stable `id` slugs per tier so mid-ladder inserts don't break saves.
- `game/js/ranks.js` (NEW, 700+ lines) — RankEngine: points with upset scaling (Tekken curve: same-rank pays best, ±25%/tier capped, 0.5x floor), placement bouts (5, 2x swings), promotion series (best-of-3 low / 5 high / 7 S-tier+reserved), demotion series (best-of-3), demotion protection (3 matches post-promotion), bottom-floor can't demote, per-character ranks on separate offline/online tracks, localStorage `wh_ranks`, per-track leaderboards, top-held counter (drives future reserved-tier invention), RankBattleController (offline arcade-style ladder vs CPU, AI scales with tier), Rank Hub overlay UI (both tracks + leaderboards + full 53-tier ladder view), runtime-injected CSS.
- Wiring (surgical, fresh-main bases): `game/js/lazy.js` (+ranks module), `game/js/main.js` (+getRankBattle, `mode-rankbattle`/`show-ranks` dispatch, confirm routing, back-menu/back-select cleanup), `game/index.html` (RANK BATTLE + RANK HALL buttons). modes.js untouched — RankBattleController is standalone.
- `docs/research/rank-system.md` (NEW) — teardown mapping: T7 two-track/per-character ranks, sdtekken points formula, promotion/demotion chance, 1st-Dan hardcap, offline-via-arcade, god-tiers-added-over-time → our implementation.
- `test/ranks.test.mjs` (NEW) — 38 assertions, all passing.

**Method:** fresh main SHAs via Git Database API at push time; chunked disk writes (this VM's overlay EPERMs single write()s >~4KB — same quirk worker 19 hit); exact-anchor surgical edits; node --check on all touched JS; engine verified in node (38/38), in-browser playtest deferred to parent (no live browser in subagent). PR #640 superseded by #641 after WORKLOG.md moved under it (rebuilt on f5676be01e).

**Proof:** `node test/ranks.test.mjs` → 38 passed, 0 failed. Covers: 53-tier shape, reserved placeholders, placement→promo-series→promotion→protection→demo-series→demotion full cycle, upset scaling, track separation, leaderboard, top-held, mid-table tier insertion with zero code changes.

**Status:** rank PR pushed; merge via git_merge.py when green. Follow-up PR: treasure battle / survival / time attack / arcade variants, unlockables/gallery, jukebox, Tekken Force + Scenario Campaign (user-approved), create-an-arena (coordinate worker 18), intro/outro cinematics layered BESIDE existing intros/win taunts (off limits).

## 2026-10-22 — 3D generation pipeline research SOTA (worker 44)

Owner directive (verbatim): "Research the current state-of-the-art open-source image-to-3D and text-to-3D models (as of late 2026). Candidates from earlier research: TRELLIS.2 (MIT), TripoSR, Hunyuan3D 2.1 — but check what's newest and best NOW. Goal: our in-house generation pipeline should be the most stacked, most current, best possible — BETTER than Tripo3D's output quality."

### Result
- Recommended stack: Hi3DGen (geometry, MIT) → TRELLIS.2 shape-conditioned PBR texturing (MIT) → UniRig auto-rig (MIT, humanoids + quadrupeds/creatures; already wired into tools/auto_rig backends per worker 22) → retopo/decimation → existing Tripo-intake ingest (roster/<char>/attires/attire<N>/source/).
- Remote-first (no weights on disk): fal.ai trellis-2, Replicate (TRELLIS.2 + UniRig), WaveSpeedAI Hunyuan3D v3 ($0.30/run).
- Key findings: Hunyuan3D 3.x and Hi3D 3.0 are hosted-only, NOT open; newest OPEN weights are TRELLIS.2 (MIT, 4B, full PBR, ≥24GB VRAM) and Hunyuan3D 2.1 (Tencent license with EU/UK/SK commercial exclusion, 29GB full pipeline); no frontier open model is natively text-conditioned — use text→image chaining.
- VRAM ladder: TripoSR ~6GB (drafts) / Hunyuan3D 2.1 10–29GB / Hi3DGen 16GB+ / TRELLIS.2 ≥24GB official.

### Files
- Added: docs/research/3d-generation-pipeline-2026-10-22.md.
- Modified: WORKLOG.md (append).
- No deletions.

### Proof
- Branch research/3d-generation-pipeline-2026-10-22b, PR against main with six-section instruction-gate body; deletion-guard / clobber-guard / instruction-gate green; merged clean via git_merge.py (merge-it-yourself law). (First attempt PR #654 hit a WORKLOG.md append/append race with another worker's entry — rebased onto current main as this clean branch.)

---

## 2026-10-22 ~13:40 CDT — worker-33: FIGHT LAB (GUNGAKU 軍楽) + CREATION + PRESENTATION

**Task (user-approved verbatim):** "Wire up: Fight Lab / Combot programmable training dummy — needs a proprietary name. Working candidate: Gungaku (軍楽) — Japanese for 'war music.' Confirm the name with them before locking it in. Def Jam's 1,900 CAW parts library. Soulcalibur weapon/style creation system. Photo mode (DOA-style: pause, camera control, filters). Per-character story endings/cinematics."

**Name update mid-task:** user LOCKED "Gungaku (軍楽)" as the official name (no UNCONFIRMED flags anywhere). Follow-up decisions folded in: (1) WWE entrances REPURPOSED not replaced — intros/win taunts off limits, entrance creation tools → cutscene + taunt creation tools; (2) create-a-finisher YES from teardowns; (3) repurposed entrance tools need a proprietary WH name, TBD — working title `WH_CINEMATIC_TOOLS_WORKING_TITLE` used everywhere, flagged for user approval.

**Delivered:**
- **FIGHT LAB · GUNGAKU (軍楽)** — `game/js/fightlab-gungaku.js`: `GungakuProgram` (button/state-level steps, loops), 9 presets (idle/guard-all/crouch/walk-in/walk-out/punish-check/juggle-sandbag/sidestep-drill/mixup-loop), `GungakuRecorder` (program the dummy by demonstrating — captures 1/2/3/4 buttons + stances, Combot-style), `GungakuAI extends AIController`, in-fight HUD panel (G toggles). Wired: modes.js `startMode('fightlab')` + `_beginFightLab` (builds on worker 29's `_beginTraining`, training untouched), game.js instantiates GungakuAI on `enemyChar.ai.gungaku` (dynamic import), main.js `mode-fightlab` dispatch. Menu: worker 37's new T8-style menu already had a "GUNGAKU FIGHT LAB" placeholder card (`badge: 'soon'`) — flipped it to `badge: 'live', action: 'mode-fightlab'` in `game/js/mainmenu.js`, wiring their placeholder to this implementation (coordination, not duplication).
- **Def Jam CAW library wired** — no duplication with WWE (wmxix/no-mercy) work: new `defjam` library in PARTS-REGISTRY.json; new §5 source block in build_suite_catalog.py reading parts-converted/defjam/CATALOG.json; parts-catalog.json 4,523 → 7,147 entries (+2,624, all `geometry_pending: true` — the 1,218 GLBs are POINTS topology, honestly flagged). Doc: customization/DEFJAM-CAW-WIRING.md.
- **Soulcalibur weapon/style creation** — `customization/data/sc-weapons.json` (17 disciplines from the SCII/SCVI teardowns: katana → unarmed, each with archetype/reach/damage/speed + style note); `customization/sc-weapon-styles.js` (`setFighterWeapon` suite-side, `applyWeaponStyle` game-side onto custom-fighter roster objects). Weapon discipline determines style, SC CaS model.
- **Photo mode (DOA-style)** — `game/js/photomode.js`: P/F9 pauses mid-fight into a free camera (drag orbit, wheel dolly, right-drag/WASD pan), 7 filters (none/noir/sepia/vivid/cinematic/ghost/ember + vignette), C captures PNG, ESC exits and restores the fight camera. Installed in main.js on game boot.
- **Story endings** — `game/js/story-endings.js`: per-character endings (14 bespoke: pantera, demonio, docfrank, phantom, diablo, skull + the Nine Souls; canon-safe fallback for everyone else), `StoryEndingPlayer` (letterboxed shot player in the live arena, best-effort fx). Wired as WATCH ENDING buttons on arcade-clear and story-complete screens — layers BESIDE intros/win taunts (owner-protected, untouched). Doc: docs/modes/STORY-ENDINGS-PIPELINE.md.
- **Create-a-finisher** — `game/js/finisher.js` runtime + `customization/finisher-creator.js` suite authoring: Def Jam BLAZIN' two-gate design (Nine-Soul Meter full + opponent ≤25% HP), authored beat sequences, 3 starter templates. Never touches win taunts.
- **Entrance-tools repurpose spec** — docs/creation/ENTRANCE-TOOLS-REPURPOSE.md: timeline editor/camera tools/pyro/music-sync → cutscene + taunt creation tools, wiring map to suite menus, `WH_CINEMATIC_TOOLS_WORKING_TITLE` flagged as needing user-approved proprietary name.

**Method:** fresh main SHAs via github_api.py (rebased every moved file onto each new base, surgical edits only). Local fix3 copy was STALE and this VM blocks `cp` into fresh dirs, so the working tree was built from fresh remote-main blobs; python3 cannot write files on this VM (node used for the catalog merge). gh_push anti-clobber re-verifies at push time.

**Proof:** node --check on all 6 new + 4 modified JS modules (all pass); JSON validity on registry/weapons/catalog; catalog merge verified (2,624 defjam entries, unique ids, all geometry_pending); 28 unit tests pass (15 Gungaku program/recorder/preset tests, 13 photo-filter/ending/weapon/finisher tests). Live-browser play verification (menu screenshot, Fight Lab fight, photo mode, ending playback) needs a browser-capable agent — headless Chromium is broken on this VM (zygote failure); flagged for delegation.

**Status:** [pending push/merge]

## 2026-10-22 — worker32: ONLINE + TOURNAMENT SYSTEMS (netcode bridge, lobbies, brackets, dailies)
**Owner instruction (verbatim):** "Wire up: Netcode approaches from the teardowns (rollback/prediction notes). Lobby structures (TTT2, SFV player rooms). Tournament brackets (single-elim). Daily challenges / rotating events."
**Method specified:** pull netcode/lobby/tournament approaches from teardowns; implement netcode foundation (deterministic sim hooks, input prediction, rollback), lobby UI+flow, single-elim brackets, daily challenges with rotation + reward hooks.
**Method used:** as specified. TTT2/SFV teardowns had no network captures, so lobby structures came from public docs (tekkenpedia, reviews, patch notes) cross-checked across sources — cited in docs/research/online-lobby-tournament-research.md. Netcode builds on the existing vendored lite-rollback foundation (bridge layer added, nothing redone).
**Deviations:** none from the instruction; two honest scope notes: (1) real-fighter netplay is architectural (needs the combat sim port — documented in docs/netcode/NETCODE-ARCHITECTURE.md with the FIELD_CONTRACT + self-test harness ready for it); (2) netcode versus is playable on the deterministic reference sim.
- `game/js/online.js` (NEW) — OnlineController: ONLINE hub, lounge browser/create/room, NetVersus (WebRTC+rollback versus), tournament + challenges screens; self-inits, additive (no main.js/menus.js/modes.js edits)
- `game/index.html` (MODIFY, 2 lines on current main) — ONLINE menu button + online.js script tag (rebased onto main 2026-10-22 19:29 UTC: kept worker22 integration.js + worker30 RANK BATTLE/HALL)
- `game/js/tournament.js` (NEW) — single-elim engine: seeding, BYEs, CPU fill, serializable brackets
- `game/js/tournament-ui.js` (NEW) — bracket rendering + local tournament runner (real fights)
- `game/js/challenges.js` (NEW) — ChallengeManager: additive onMatchEnd chain + mode-clear hooks, localStorage progress
- `game/data/challenges.js` (NEW) — 24 challenges as data, deterministic daily rotation, weekly events
- `game/js/unlockables.js` (NEW) — unlockable registry (titles/frames) that challenges pay into
- `game/netplay/bridge/input-codec.js` (NEW) — WH inputs → 16-bit netcode word
- `game/netplay/bridge/sim-adapter.js` (NEW) — WhNetSim, FIELD_CONTRACT, checksum, 600-frame determinism self-test
- `game/netplay/bridge/test-bridge.mjs` (NEW) — 7 tests
- `game/netplay/lobby/lobby-protocol.js` (NEW) — LobbyClient state machine (quick/custom/create, rotation, spectate, chat, fight requests)
- `game/netplay/lobby/test-lobby.mjs` (NEW) — 5 tests (fake server)
- `game/netplay/signaling/server.js` (MODIFY) — v2 lobby protocol ported onto main's minimal server (another worker rewrote it to 66 lines while this PR was open); v1 demo protocol byte-identical to main, lobby layer appended
- `game/tests/online-systems.test.mjs` (NEW) — 12 tests (brackets + rotation)
- `game/tests/challenges-manager.test.mjs` (NEW) — 8 tests (progress/claim/persist)
- `docs/netcode/NETCODE-ARCHITECTURE.md` (NEW) — honest playable-vs-architectural doc + browser P2P constraints
- `docs/research/online-lobby-tournament-research.md` (NEW) — teardown/web sources
- `docs/online-proof/*.png` (NEW) — 4 screenshots (hub, lobby, bracket, challenges)
- `WORKLOG.md` (this entry)
- `node --test` (repo root): **32 passed, 0 failed** — bridge (7, incl. 600-frame adapter determinism self-test), lobby client (5), tournament+rotation (12), challenge manager (8).
- Signaling server v2 (rebased): **11/11 pass** on the new base — v1 join/peer/signal (main's), v2 welcome/create/join/ready/match-start/chat/targeted-signal/match-end, plus real LobbyClient create/join/state (3/3).
- Headless Chromium screenshots of all four screens rendering (docs/online-proof/ — viewed and verified).
- `node --check` clean on every new/edited JS file.
- Honest architecture doc: `docs/netcode/NETCODE-ARCHITECTURE.md` (playable-vs-architectural table + browser P2P constraints: STUN/TURN, no authority, 2-player, same-version requirement).
- Browser P2P needs a TURN server for symmetric NATs before shipping (STUN default is Google's; documented).
- Ranked/leaderboards are the Nakama lane (researched, not wired).
- The combat sim port is the critical path to real-fighter netplay; FIELD_CONTRACT + self-test harness are ready.
- Challenge stat mapping is honest: hit-count challenges are phrased as damage (no landed-hit counter in the engine) — see CHALLENGE_TYPES docblock.
- Rebased 2026-10-22 ~19:35 UTC onto main 7fe0cb41 (worker22 integration + worker30 ranks landed while PR was open); server.js v2 ported onto the rewritten minimal base, index.html re-applied, WORKLOG re-appended.

## 2026-10-22 — V-System build + Triangle/Reversal Edge proposals (worker 31)

Owner decisions relayed mid-task: the prior combat-depth set (VF5 throw
escapes, SC 8-way run, Guard Impact, Tekken item moves) was stood down
before any code was written — research only, nothing to revert. New
directive: Triangle = proposal only, Reversal Edge = proposal only,
V-System = build with proprietary Eastern Mind names TBD.

### V-System — IMPLEMENTED (all user-facing names «name TBD», flagged)
Tekken-ified SFV V-System over the Nine-Soul meter. One input (`vskill`:
KeyV / V touch button), three context moves + V-Shift on block double-tap:
- V-Skill: per-character unique move (+4 souls on use). Seeded: default
  Soul Palm; pantera Iron Shoulder (armored); dio Demon Lash; ryusan
  Vitriol Flick (fastest); phantom Moon Catch (12f parry kind).
- V-Trigger: full-meter (100) 12s install — +15% damage, chip on all
  blocked attacks, V-Skill becomes armored EX (x1.3). Competes with Soul
  Surge for the same 100 souls (one-shot vs install = the resource game).
- V-Reversal: blockstun + 50 souls → guard-cancel counter, invuln through
  active frames, heavy knockback.
- V-Shift: double-tap block (280ms) → 0.35s invuln backshift; evading an
  attack (3.2m) → 0.3x slow-mo + 1.2s Break window (x1.5, auto-CH).
Slow-mo dilates the sim only (arena/camera stay live) — same mechanism
the Reversal Edge proposal reuses.

### Files (no deletions)
- NEW game/js/v-system.js (tuning, VSKILLS catalog, vskillDispatch,
  vshiftTap — pure, 15/15 node tests pass)
- NEW game/tests/v-system.test.mjs (15 tests)
- game/js/fighter.js (tryVSkill/tryVTrigger/tryVReversal/tryVShift;
  vskill/vreversal/vshift states; armor absorb; V-Trigger/V-Break damage;
  V-Trigger chip; timers)
- game/js/game.js (vskill dispatch, block double-tap, parry + shift-evade
  resolution, 'armor' result presentation, slow-mo in _loop)
- game/js/input.js (KeyV), game/index.html + game/styles.css (V button),
  game/js/ai.js (AI uses all four, gated), game/js/main.js (banners)
- docs/combat/V-SYSTEM-2026-10-22.md (design + naming candidates for user)
- docs/combat/PROPOSAL-TRIANGLE-2026-10-22.md (proposal only)
- docs/combat/PROPOSAL-REVERSAL-EDGE-2026-10-22.md (proposal only)
- WORKLOG.md (this entry)

### Verification
- node --test: 22/22 pass (15 new + 7 pre-existing). node --check clean.
- No live-browser play verification possible from this worker (no browser
  access) — disclosed in the design doc; wiring follows proven patterns
  (attack-state timing, hitstop, banner/flash). Flagged for human playtest.
- Anti-clobber: main moved 4 times mid-task (be7d2eda → 9f4b2d77 →
  43fa27bd → 564ee4e7 → dfee700b); every modified file was re-fetched at
  the current head and the V-System edits re-applied surgically on top —
  no stale full-file copies. Folded in upstream's lighting-rig
  (fighter.js/game.js), rank-battle (main.js), and worker-22 integration
  (index.html) hunks instead of overwriting them.

### Flags for coordinator
- ALL V-System user-facing names are «name TBD» — user must pick (candidates
  in docs/combat/V-SYSTEM-2026-10-22.md §7, Nine-Souls/Eastern Mind flavored).
- Triangle + Reversal Edge are PROPOSALS ONLY — do not build without approval.
- V-Trigger and Soul Surge both cost 100 souls by design (player choice).
- Upstream note: at dfee700b, game/index.html uses the old limb-cluster
  buttons while game/styles.css only carries PSX-overlay positioning —
  the old buttons render unpositioned. Not my lane (control overhaul);
  flagging for the coordinator.

## 2026-10-22 ~16:10 CDT — worker 52: critical-path P0 fix (flow QA)

**Playable-path audit** (menu → select → stage → fight → rounds → result → back)
on main @ 2af4328 found the whole loop dead behind two 1-line defects in
`game/index.html`:

- **P0-1 — `show()` threw on every navigation ("nothing is tappable").**
  `game/js/main.js:38` builds `stageIntro: getElementById('screen-stage-intro')`
  → null, because index.html carried TWO `id="screen-stage"` sections
  (Lane-4 stage select + story stage intro). PR #666 had renamed the story
  one; PR #657's stale-base merge reintroduced the duplicate (PR-#579
  pattern). `show()` does
  `Object.values(screens).forEach(s => s.classList.remove('active'))` →
  TypeError on the null entry → every screen transition died. Fix (worker-52
  PR, 1 line): story section → `id="screen-stage-intro"` (restores #666).
- **P0-2 — menu rendered unstyled ("white text boxes").**
  Fixed on main by PR #677 while this audit ran (mainmenu.css link).
- Proof: `proof-show.mjs` (DOM-stub replicates the screens/show code path —
  throws before, navigates after). Import graph of main.js (15 modules) all
  resolve; select.css covers the select screen; stage/fight/result wiring
  verified coherent by code read.
- `docs/CRITICAL-PATH-STATUS.md`: running status board (green/red/blocking)
  for the playable loop + tomorrow list (off-path sections per the
  PLAYABLE TODAY directive). Findings for worker 53 (fight loop) and
  worker 51 (stage preview pane gap) filed there.
- Note: open PR #676 (worker36/menu-fix, mergeable_state=dirty) attempted a
  full rewrite for the same symptoms — superseded; worker 36 should
  close/rebase it.

## 2026-10-22 ~15:45 CDT — worker 50: rig-guard rebuild (picked up Claude's dropped work)

Claude's anti-clobber guard rebuild was unpushed (existed only on the user's
machine). Rebuilt from the task description and PR'd (branch `w50/rig-guard`):
- `tools/rig-guard/rig_guard.py` (~176 lines) — CI guard FAILS on ANY
  MODEL_URLS key removal, not just skinned ones. Escape path: `## Model
  removals` PR-body section (keys in backticks) or the
  `owner-approved-model-removal` label.
- `tools/rig-guard/test_rig_guard.py` — 11 unit tests, all green
  (removed→fail, added→pass, escape→pass).
- `.github/workflows/game-checks.yml` — two jobs: `rig-guard` (self-test +
  key-removal check on sparse checkout) and `game-unit-tests`
  (`test/*.test.mjs` via node on a sparse checkout).
- Verified against real `game/js/assets.js` at base: 149 keys extracted;
  simulated `phantom` removal flagged; addition + escape paths pass.
- Distinct from clobber-guard / deletion-guard / no-deletion-guard /
  instruction-gate: no duplication, no edits to existing checks.
- Full log: `docs/decisions/2026-10-22-rig-guard-rebuild-w50.md`.

## 2026-10-22 ~16:00 CDT — worker 48: ASHLANE CANON BRIDGE (Bannon, El Toro de Oro, Pablo, NPC Finxsse)

### What
Canon bridge for the four user-locked Ashlane→VF5 mappings. Ashlane characters keep their existing bios from their repos; each got a "how they arrived" bridge into WH/Eastern Mind canon (the call, lost souls, the Trial, Tong-Nou, the Five Lands, the Phantom Marketplace).

### Sources (foundation bios — pulled, not rewritten)
- `mhvnsnt/brutalfistgrokversiontenpointfive`, `src/data/bannonRoster.ts` (ids `bannon`, `el_toro_de_oro`, `pablo`, `finxsse`) — bios, personalities, fighting styles, attires (PABLO.glb Minotaur Painted / PABLO_goldenbull.glb Golden Bull / PABLO_blackreign.glb Black Reign), payback names, factions.
- `mhvnsnt/brutalfistgrokversion`, `native/media/characters/chara_bannon/bannon.identity.txt` — "The physical nucleus and absolute force of the Bannon Engine. Driven by raw physics and unmatched grit."
- Bannon universe = sub-universe of the WH multiverse (owner directive 2026-10-22).

### Changes (CANON.md — 3 surgical additions, 0 deletions)
- New `## 9. THE ASHLANE ARRIVALS` section (before APPENDIX): four entries in the Pantera/Demonio/Phantom format — BANNON "The Engine Soul", EL TORO DE ORO "The Golden Bull Soul", PABLO "The Painted Soul", NPC FINXSSE "The Grudge Soul". Each: Backstory (Ashlane foundation + arrival kishotenketsu), Personality (one behavior), Fighting philosophy (one carved quote), Relationships (zuihitsu, double work), Element (Bannon=Earth/Octagonal Shrine, El Toro=Fire/Plains of Chi-U, Pablo=Metal/Helix Palace, Finxsse=Water/Palace of Dreaming), Body/Mind/Soul (friction), Why they think they're here (with the gap), Being purified of, Signature detail, Owner-locked (Ashlane source + VF5 base, technical only).
- §4: new "On the Ashlane arrivals" paragraph — mortal lost souls from the Bannon sub-universe, not of the nine.
- §5 "What the Fighters Want": four new bullets.
- Pablo's locked duality (user refinement: Goldust theatricality MIXED with dark Black Reign/Abyss/Mankind energy — disturbed masked darkness underneath, matching PABLO_blackreign) drives his Body/Mind/Soul friction and "Being purified of: The mask".

### Also
- `docs/decisions/2026-10-22-ashlane-canon-bridge.md` — dated decision log.
- `docs/owner-directives.md` — new "VF5 moveset claims — Ashlane four" section (locked: Jeffry→Bannon, Wolf→El Toro, El Blaze→Pablo, Lei-Fei→Finxsse; candidates + unmapped listed).
- Writing laws held: all adults; canon-grounded (every proper noun from CANON.md or the Ashlane repos — no invented locations/systems); no Tekken/VF5 names in canon prose (bases in Owner-locked technical lines only, matching the existing "Bob Richards base" convention); craft guide standard.

### Verification
- `git diff --stat`: CANON.md +142/−0, owner-directives.md +3/−0, decisions +1 new file. Zero deletions.
- PR: branch `w48-ashlane-canon-bridge`, instruction-gate body (six sections), merged via `git_merge.py` after green CI + no-deletion guard + gitleaks.
- No live-browser play verification applicable (canon text work); no game code touched.

## 2026-10-22 — Creation suite menus + parts incorporation (worker 38)

Owner directives (verbatim): "Creation suite menus: Full layout pass — the
WWE-template-first flow, tool-to-menu wiring (MB-Lab, Build-A-Bod, GameRig,
NaughTyRig, Fluid Painter, Tripo intake, export tools), the three access
layers (unified, separate, universal mode). Everything specified." /
"Parts incorporation: All WWE parts, Def Jam parts (1,900), DOA parts — all
incorporated into the creation suite's parts library, not just sitting in
teardowns."

REBASE NOTE (2026-10-22): while this lane was in flight, worker 37 landed the
template system + WWE step wizard (`js/creation-flow.js`,
`customization/templates/body-templates.json` — MB-Lab-baked base meshes, the
Mixamo soldier dead as a default), and worker 33 landed Def Jam in
`build_suite_catalog.py`. Per "don't duplicate, extend", this lane rebased:
- **Template select is worker 37's, canonical.** No competing select ships in
  this lane — the TEMPLATE tab (`js/tools.js`) is a thin wrapper (current pick
  + change button → `window.__flow.openTemplateSelect()`).
- **UNIVERSAL MODE = worker 37's step wizard** (`window.__flow.startWizard`) —
  the one combined front-end; this lane's modal wizard was dropped.
- ART + JOBS tabs (worker 37) preserved in the rail and app dispatch.
- Def Jam in the suite catalog is worker 33's (`parts-converted/defjam/
  CATALOG.json`, geometry_pending); this lane only ADDS the DOA4 scan.

### Menu layout pass (`customization/create-fighter/` — worker 6's foundation, extended)
- **WWE creation sequence**: left rail reordered to
  TEMPLATE → BODY → HEAD/FACE → SKIN → HAIR → FACIAL HAIR → ATTIRE →
  WARDROBE → PROFILE (+ MOVESET, LIMBS, ART, JOBS, TOOLS). Breadcrumb shows
  "Step N of 14". SKIN is a new dedicated step (8 No Mercy tones + 233 skin
  textures + 1,470 WMXIX decoded PNGs + Fluid Painter job specs);
  HAIR and FACIAL HAIR are their own steps (facial hair = AKI face textures
  + head parts → T7 slot 7, conflicts with Full Head per the §7 spine).
- **BODY tab**: template row (current pick + change button → the flow
  module's select), No Mercy body types, WMXIX proportion sliders, MPFB2
  morphs. Skin tones live in SKIN; the BODY tab no longer duplicates them as
  the primary home.
- **Tool-to-menu wiring** (TOOLS tab, `js/tools.js`): every tool has a menu
  home with its REAL params (grounded: MB-Lab spec from run_mblab_job.py
  docstring, Tripo intake flags from tools/tripo-intake/README,
  glTF-Transform 4.1.1/meshoptimizer 0.22.0 from tools/anim/gltf_codec.mjs,
  MPFB2/GNM from body-morphs + face-morphs + tools/gnm/WH-INTEGRATION.md).
  Tools not in the browser build are badged FILED IN INTAKE / FETCH VIA
  SETUP — never presented as wired. Menus write job-spec JSONs (download)
  the pipeline consumes; nothing executes from the browser.
- **Three access layers**: LAYER 1 — six unified systems (BODY/FACE/SKIN/
  RIG/IMPORT/EXPORT, genuinely merged); LAYER 2 — nine separate per-tool
  menus; LAYER 3 — UNIVERSAL MODE = the flow module's WWE step wizard.
- **Real-mesh preview** (`js/preview3d.js`): geometryReady parts attach as
  real GLBs at bone anchors (auto-fit; full-body costumes scale to fighter
  height). Proxy rings are the fallback only. `app.js syncPreview` resolves
  repo-relative `glb` paths through `resolveUrl()`.

### Parts library: 7,920 parts in PARTS-INDEX; 7,419 in the suite catalog
- New builder `customization/build_suite_parts_index.py` rebuilds
  `create-fighter/data/PARTS-INDEX.json`: 7,920 parts — wmxix 4,160
  (incl. 1,470 WMXIX decoded texture PNGs), no-mercy 682 (303 meshes upgraded
  to geometryReady — real converted GLBs), defjam 2,780 (2,624 CAW conversion
  entries, geometry PENDING — topology verdict FAIL/BLOCKED per the samples
  verdict, honest badges), doa4 272 (real costume GLBs at
  `teardown/dead-or-alive-4/models/`), wh-library 17, cc0-hair 9.
  Honesty rule: nothing marked renderable without a real mesh on disk.
- `customization/build_suite_catalog.py` (rebased onto worker 33's version):
  adds ONLY the DOA4 scan — 272 real converted GLBs → Full Body slot
  (T7 11, `fullbody:'11'` added to the T7 map + the creation-suite-ui
  SLOT2CAT). `creation-suite-ui/data/parts-catalog.json` regenerated on
  worker 33's current base + the DOA4 entries: 7,419 parts total.
- `create-fighter/js/catalog.js`: new categories (Head slot 1, Facial Hair
  slot 7, Textures, Def Jam — Unsorted), §7 spine conflicts extended,
  friendlyName for defjam/doa4/wmxix-tex ids, facialhair as a virtual
  category (AKI face textures + head parts).

### Proof (headless Chromium + SwiftShader, phone portrait 390×844)
- 15 screenshots at `~/workspace/proof-w38/shots/` (01 template select …
  09 real-mesh equip, 07b tools layer 2). Zero page errors on load and on
  every rail tab click. Canvas pixel test: 99.3% non-black (3D preview
  renders). Real-mesh equip verified programmatically (No Mercy 17-vert
  part + DOA4 29,775-vert textured costume both attach and are visible).
- `node --check` passes on all JS; node catalog logic test passes
  (7,920 parts, no orphan slots except pre-existing `colors`).

Files: create-fighter `index.html`/`css`/`js/app.js`/`js/tools.js`(new)/
`js/catalog.js`/`js/preview3d.js`/`data/PARTS-INDEX.json`/`README.md`,
`customization/build_suite_parts_index.py`(new),
`customization/build_suite_catalog.py`,
`creation-suite-ui/data/parts-catalog.json`, `creation-suite-ui/js/suite.js`,
`customization/CHARACTER-CREATION.md`.
On-main files NOT touched: worker 37's `js/creation-flow.js` + `js/art.js`
+ `customization/templates/body-templates.json`; worker 33's
`PARTS-REGISTRY.json`.

## 2026-10-22 ~16:00 CDT — worker 50: Kinpo A1 rig repoint (config-only)

- Repointed `kinpo` + `kinpo-attire1` MODEL_URLS keys in `game/js/assets.js`
  from the broken k-NN `model-rigged.glb` to the working tripo-intake rig
  `roster/kinpo/attires/attire1/model-intake.glb` (GameRig, facing +X,
  validate PASS). No re-rigging, no model file changes.
- Fight-check: target is a valid loadable GLB 2.0 (30 MB, 1 mesh, 1 skin,
  75 nodes, fully skinned); `node --check` clean; new rig-guard reports
  zero key removals (149 keys both sides); `attires.js` ladder keys
  unchanged (they reference MODEL_URLS keys, not paths).
- Kept `kinpo-intake-demo` (same file, comment updated) — key removal would
  trip the rig-guard.
- PHANTOM BLOCKED: no working `model-intake.glb` exists for phantom on main
  (only kinpo has one); refused to point phantom at kinpo's file. Needs a
  real tripo-intake re-rig first — flagged to coordinator, noted in
  `docs/owner-directives.md`.
- Full log: `docs/decisions/2026-10-22-kinpo-repoint-w50.md` (branch
  `w50/kinpo-repoint`).

## 2026-10-23 ~07:30 CDT — SmutBase intake wave 6: RYUSAN + TOBI full pipeline

- **RYUSAN** (WH name for SmutBase Mina Ashido intake, `roster/mina-ashido/`): full pipeline —
  `CANON.md` (The Corrosion Soul; adult acid punk; Jotei family's soul-binding crimes; Tobi tipped her off; signature line "You don't get to tell me to calm down"; canon-grounded in CANON.md, no Tekken names),
  `PARTS.md` (8 GLB meshes labeled/categorized by bounding-region analysis: body base, hair, horns, fur trim, collar, boots, top, bottoms),
  `game/assets/movesets/ryusan.json` (194 moves: full Lucky Chloe T7 movelist converted from `docs/t7t8-reference/frame-data-t7/luckychloe.json` + 6 WH canon moves layered on top; stances SCT/BT/FC/WS/WR/SS; 6 combos; schema v2).
- **TOBI** (WH name for SmutBase Mirko intake, `roster/miruko/`): full pipeline —
  `CANON.md` (The Escape Soul; rabbit courier, fastest in roster; tipped off Ryusan; the undelivered letter — withheld — left hand never leaves the satchel strap; canon-grounded, no Tekken names),
  `PARTS.md` (11 GLB meshes: body base, rabbit ears, hair, head ring, sash, bodysuit tops, bottoms, gloves, collar),
  `game/assets/movesets/tobi.json` (194 moves: Hwoarang T3 decoded bank `teardown/tekken3/movesets/moveset_hwoarang.json` + 6 WH canon moves; LFF/RFF/LFS/RFS stances; 5 combos; schema v2).
- Wiring: 4 MODEL_URLS keys in `game/js/assets.js` (`ryusan`, `ryusan-attire1`, `tobi`, `tobi-attire1` → `../roster/<dir>/attires/attire1/model.glb`); `ryusan`/`tobi` added to MOVESET_IDS in `game/js/movesets.js`; both added to `game/assets/movesets/index.json` (114 fighters).
- Models are unrigged statics (0 skins) — rig queued, same path as other SmutBase intakes.
- Proof: `node --check` clean on both JS files; both movesets load through the real `movesets.js` loader (schema v2, all required fields); `fighter-completeness.test.mjs` 4/4 pass; gitleaks clean; GLB paths verified on disk. model-key-guard failures are pre-existing sparse-checkout artifacts (all entries "file missing", none are ryusan/tobi — not in OWNERSHIP table).
- Branch `smutbase-wave6/ryusan-tobi`, PR merged via `git_merge.py` (3-way, clean+green).

## 2026-10-23 — Claude session: 10 sideways k-NN rigs replaced + select-screen crash fix

- Problem: the Tripo pulls face +X; the 2026-10-21 k-NN rigs (`model-rigged.glb`, 49 joints) assumed +Z, so these
  fighters stood in profile and their stance shredded in game.
- Facing read from four-view renders of each original static (Blender 4.0.2 workbench, +Z/+X/-Z/-X cameras, viewed).
- Re-rigged each `model.glb` with `tools/auto_rig/rig_tripo_static.py --facing +X` → `model-rerig.glb` beside the old
  rig (old file kept). Wired: skull, kronos (both keys), kronos-attire2, saku-ra, phantom, purple-rain,
  doc-frank-wowomomo, doc-frank-frankenstein, doc-frank-frankenstein-big, demonio-human. model-facing.json `models`:
  those 10 + kinpo-attire1 = +Z.
- Verified in game: `tools/proof-harness/rig_sheet.mjs` (rest faces +Z, King stance clean, max bone error 0.4 deg)
  and a Skull vs Kronos arcade fight via `tools/proof-harness/fight.mjs`. Proof: docs/proof/claude-2026-10-23/rerig/.
- `tools/auto_rig/backends/smooth_weights.py`: the edge cutoff (9.8 mm) left no edges on Waterfall's dense mesh and
  crashed; the cutoff now drops to half the median edge only when the mesh has no edge over it.
- `game/index.html`: restored `.pane-title` / `.pane-style` in both select panes beside the new `.pane-facts` row.
  `select-screen.js renderPlate()` writes to both; without them every mode start threw
  "Cannot set properties of null (setting 'textContent')" (seen in the fight harness on main 1202f9bd2).
- Follow-ups: Frankenstein A4 base pedestal fused to the boots; Wowomomo tabard stretch; sam-ur-a1 + thor fail the
  smoothing gate; waterfall re-run queued with the fix.
- **mon/msk identified:** `mon` = Eileen, `msk` = El Blaze (release READMEs; msk render-verified as luchador). **El Blaze DOES have farcs** — the "NO farc/DLC" note was wrong; Pablo → El Blaze is NOT blocked.
- **New tools:** `tools/vf5/farc_extract.py` (FArC container), `tools/vf5/vf5extract.py` (obj.bin → OBJ: chunk headers, LE f32 positions, u16 strip indices), `tools/vf5/README.md`.
- **4 locked movesets** (schema-v2, VF→Tekken inputs): `game/assets/movesets/vf-jeffry.json` (25, Bannon), `vf-wolf.json` (21, El Toro de Oro), `vf-leifei.json` (22, NPC Finxsse), `vf-elblaze.json` (28, Pablo).
- **Research:** `docs/research/VF5-FULL-INTEGRATION-2026-10-22.md`; decision log `docs/decisions/2026-10-22-vf5-integration.md`.
- **Renders:** 18 T-pose PNGs batch-rendering (Blender 4.5.3); uploaded to remote storage as they complete for user review. **Dural flagged as Zen's approved base-mix layer.**
- **Gaps:** Motion clips not in release (likely in 3.7GB vf5-500m ROM, not pulled); 38 stg*.farc stages deferred to arena pipeline.
- Merged via git_merge.py as 7f38022d (additions only; CI: instruction-gate, clobber-guard, deletion-guard, guard all green).

## 2026-10-22 — Moveset Library System (worker 47)

Built the central moveset library + per-fighter assembly system (owner standing directive):
- `game/data/moveset-library/`: 9,516 moves across 6 banks (T3 4,648 · No Mercy 4,409 · WMXIX 169 · DOA 146 · VF 48 · VF5 96) + 8 pending banks registered; `schema.json`, `axes.json`, `claimed-map.json` (source law), `index.json`. Reproducible ingest: `tools/moveset-library/ingest.mjs`.
- `game/js/moveset-library.js`: `assembleFighter()` → v2-contract movesets; source-law gate in code; no pending banks.
- `game/data/movesets/`: pre-assembled bannon (28) / el-toro (23) / pablo (36 — locked flavor: powerhouse + comedy-whiff lucha attempts + Black Reign Ride / Abyss Choke dark thread) / npc-finxsse (23). VF5 bases live from vf-{elblaze,jeffry,wolf,leifei}.json federation conversions (another lane, reused read-only).
- `game/moveset-browser.html`: browse by axis, inspect, attach/detach, save. Fully working dev page.
- Docs: `docs/research/moveset-library-schema.md`, `docs/decisions/2026-10-22-moveset-library.md`, `docs/handoffs/moveset-library-vf5-format.md` (worker-45 contract, read-only).
- Proof: node --check clean; ingest 0 violations; assembler CLI verified (pablo 36 / bannon 28 / el-toro 23 / npc-finxsse 23, law-clean, 0 unresolved); claimed pull refused / free pull allowed.
- Note: #678 merged then was dropped from main by #679's merge tree; restored via this PR (see decisions log).
## 2026-10-22 — Worker 28: STAGE MECHANICS + RAGE/COMEBACK + SOUL URGE (T8 Heat)

**Owner instruction (verbatim):** "From all teardown games, wire up: (1) Stage mechanics — Tekken floor/wall/balcony breaks, DOA knock-through-walls into new areas. (2) Rage/comeback systems — rage arts/drives, slow-mo finishes."
**Follow-ups folded in:** "Heat system (T8): YES — pull straight from the files, but rename proprietary." → **name user-locked: SOUL URGE** (use everywhere). "Soul Gauge / Critical Edge: BUILD ON OURS — extend our meters, document the mapping."

### What was built
**1. Stage mechanics** (`game/js/stagebreaks.js`, new)
- Tekken floor breaks (T7 Forgotten Realm/Brimstone & Fire/Devil's Pit rules): heavy slam
  (knock>=6 / launch / knockdown) inside a cracked floor zone shatters it — both fighters
  drop to a lower level (physics ground moves via new `setGroundY`), +12 bonus damage,
  ember-lit lower tier, fight continues below. Persists all match (T7-authentic).
- Tekken wall breaks + DOA knock-through-walls: every stage gets breakable spirit
  barriers at ±wallDistance by default. Heavy hit (knock>=4 / launch / KO) that splats
  the defender into the wall shatters it — bounds extend +4.5 into a dressed "new area"
  (rubble + breach glow), +8 bonus damage (DOA Danger-Zone style). Once per side/match.
- Tekken balcony breaks (T7 Jungle Outpost 2 rules): railing + weak section at a ledge
  edge — same drop mechanic as floor breaks, own banner.
- Wired stages: shrine (floor→crypt), plains-of-chi-u (floor→ember hollow),
  helix-palace (balcony). Walls default ON everywhere (`noWallBreak` opt-out).
- Hooked into `Game._resolveCombat` after every landed hit; debris physics + camera
  shake + banners; `setGroundY`/`getGroundY` exported from fighter.js.

**2. Rage / comeback (T7)** (`game/js/rage.js`, new)
- Rage at <=25% HP, once per round (existing `R.` notation mechanism was a skeleton —
  no data existed; now synthesized per fighter from their own strongest T3 strike).
- **Rage Art** (`1+2` while raging → `R.1+2`): 32 dmg, super armor (new `armor` move
  property: damage applies but the swing is never interrupted), knockdown+wallsplat,
  cinematic beat (hitstop + flash + brief slow-mo), spends rage.
- **Rage Drive** (`3+4` while raging → `RD.3+4`): powered-up strike, spends rage.
  T7 rule: art OR drive per round.
- **Slow-mo finishes**: match-deciding KO blows and rage-art KOs play at 0.12× for
  1.5 s real time (`Game._loop` timescale). Fixed pre-existing bug: `_rageUsed` was
  never reset between rounds (rage died after round 1).
- UI: pulsing red RAGE tag under the HP bar (`ui.setRage`), red fighter aura
  (`setRageAura`), `audio.rage()` cue, RAGE banner. AI spends rage arts/drives in range.

**3. Soul Urge (T8 Heat, proprietary rename — user-locked)** (`game/js/soulurge.js`, new)
- Pulled from `teardown/tekken7/tekkenmods-docs/.../Tekken_8/...` (Move, Hit_Conditions,
  Cancel, Input_Extradata `0x10 - Heat`) + verified canonical T8 rules.
- **Urge Burst** (`2+3`, armored): activates on hit OR block → 1 pip, 10 s.
- **Urge Engager**: fighter's own launcher-class strike (auto-flagged, synthesized moves
  excluded); on hit only → 2 pips, 15 s, +10 HP, dash-in.
- **During Urge**: chip on block that can never kill; timer pauses while opponent is
  hit/grounded; blue soul-flame aura; urge gauge under HP (T8-authentic placement).
- **Urge Dash** (`1+2` while urging, not raging): 1 pip, committed forward burst.
  **Urge Smash** (`2+3` while urging): 30 dmg armored, spends ALL pips, ends Urge.
- Once per round, refreshes per round. AI uses burst → dash → smash.

**4. Soul Gauge / Critical Edge mapping** (`docs/research/SOUL-GAUGE-MAPPING.md`)
- No new meter imported. Nine-Soul Meter = the single persistent meter (unchanged
  economy); Soul Surge IS our Critical Edge (verified untouched); Soul Urge is a
  separate per-round gauge (T8-faithful). Reversal Edge/Guard Impact stay ON HOLD
  per user.

### Files
- New: `game/js/stagebreaks.js`, `game/js/rage.js`, `game/js/soulurge.js`,
  `game/tests/stagerage.test.mjs`, `docs/research/SOUL-URGE-SYSTEM.md`,
  `docs/research/SOUL-GAUGE-MAPPING.md`
- Edited: `game/js/game.js` (directors, hooks, slow-mo timescale),
  `game/js/fighter.js` (setGroundY, armor, rage/urge auras, urge dash, urge chip),
  `game/js/movesets.js` (R./RD./UB./US. chord prefixes), `game/js/ai.js`,
  `game/js/audio.js` (rage/urge cues), `game/js/main.js` (setRage/setUrge/updateUrge),
  `game/index.html` (rage tags, urge gauges), `game/styles.css` (rage/urge styles),
  `game/js/stages.js` (breakables on shrine/chiu/helix), WORKLOG.md (this entry)

### Proof
- `node --test game/tests/stagerage.test.mjs`: **15/15 pass** (rage thresholds, art/drive synthesis + input resolution, slow-mo triggers incl. slowMoScale math, urge burst/engager/smash/pip spend, wall/floor break triggers, once-per-match, bonus damage).
- Existing suites: fighter-completeness 4/4 pass; model-key-guard 2/3 (1 failure is
  my partial working copy missing `roster/` — unrelated to this lane, assets.js untouched).
- `node --check` clean on all 10 touched/new JS modules.
- In-game screenshots: NOT possible from this worker (no live-browser access as a
  subagent) — flagged for the parent to verify by playing per the standing rule.

### Anti-clobber rebase (2026-10-22, post-implementation)
Main moved under this worker TWICE. First rebase (loadspeed lane: lazy.js,
hit-feel tuning, T8 select grid; movesets lane: R. prefix + _rageUsed). Second
rebase (worker 27 lighting rig: attachCharacterRig/buildStageLightRig; worker 37
T8 main menu + delegated data-action router; jiggle/faceRig/handPoses imports in
fighter.js). All 9 edited files were rebased onto current main instead of pushing
stale full-file copies:
- game.js: directors now inject `{ setArenaLimit, setGroundY }` (from
  `await lazy.fighter()`) and `{ playedMoveset, getFighterMoveset }` (from
  `await lazy.movesets()`) — stagebreaks/rage/soulurge NO LONGER statically import
  fighter.js or movesets.js, preserving the loadspeed lane's deferred loading.
  startMatch stays async; hooks adapted to the feel-multiplier (`this.feel`) KO branches.
- fighter.js: kept main's hit-feel tuning + FACING fix; added setGroundY/getGroundY,
  armor absorb, urge chip floor, rage/urge auras, tryUrgeDash, _inputCtx urge flags
  (main's `rage:` ctx flag reused; added `urgeOn`/`urgeAvailable`).
- movesets.js: main already had the `R.` prefix — added `RD.` (rage drive) and the
  2+3 urge reservation (UB./US. win over normal moves while the gauge is live).
- rage.js: added missing `slowMoScale()`; hardened rageArtHit for null arena.
- soulurge.js: added missing onHit/onBlockedHit/spendPip/urgeSmashHit wiring.
- index.html/styles.css/main.js: HUD additions re-anchored onto the T8 select-grid
  versions (4 HUD lines + rage-flash overlay + ui methods + CSS).
- stages.js: breakables re-anchored onto the lighting-rig stage defs.
- Verified zero main-side lines lost in every file (diff < count = 0 except
  intentional paired modifications).
- Third rebase (fightlab-gungaku lane: GungakuAI lazy import + programmable-dummy
  AI switch in startMatch; photo-mode dynamic import + mode-fightlab router action
  in main.js). Merged without touching those lanes' code.
- Fourth rebase (worker 34 fighter-depth: FighterDepth dynamic import +
  onMatchStart hook + soul-kindle queue watch in game.js; kindle block/damage/
  counter-hit rules in fighter.js; T3 round-2 bank list in movesets.js).
  Merged without touching that lane's code.
- Fifth rebase (V-System lane, owner 2026-10-22: v-system.js, V-Trigger/
  V-Reversal/V-Shift AI + UI + CSS; online.js script tag in index.html).
  Rage/urge AI block placed after Soul Surge check; armor coexists with
  V-Skill armor (V-Skill absorbs outright, rage/urge armor absorbs with
  damage). Merged without touching that lane's code.
- Sixth rebase (arena pipeline: mainmenu.css link in index.html; Pink Narwhal
  club GLB + buildHelix detail-pass builder in stages.js/helix-palace).
  Balcony breakable kept on the upgraded stage. Merged without touching
  that lane's code.

### Flags for coordinator
- Input overlap (documented, T8-style): `1+2` = rage art while raging, urge dash while
  urging (not raging), normal move otherwise. `2+3` = urge burst/smash while the gauge
  is live, normal move after it's spent. Rage art has priority when both are live.
- Soul Urge name is USER-LOCKED — do not rename without owner approval.
- Stage-break visuals are procedural (barriers, cracked discs, debris); stages with
  real teardown geometry (No Mercy GLBs) get wall breaks via barriers only.
- Next-match `bindStage` resets breaks; rounds within a match keep them (T7/DOA).
## 2026-10-22 ~13:45 CDT — Worker 27: LIGHTING + ENVIRONMENT PULL

**Owner directive (verbatim):** "Pull from the most recent version of each game in the teardown
files: (1) Lighting — how each game lights its stages, light placement, color temperature,
dynamic vs baked, character vs stage lighting. Tekken 7/8, DOA6, SFV, SC6 — the newest lighting
tech. Wire their lighting approaches into our stages. (2) Environment and scenery — stage
geometry, background buildings, set dressing, ambient details. Whatever can be extracted and
reused. (3) Accessories, clothing, buildings — from all teardowns, feeding both stages AND the
character creation suite. (4) General sweep — flag anything visual/environmental we haven't
pulled yet. Priority: lighting first, then stage scenery, then accessories/clothing."

**Teardown audit (grounded):**
- **Tekken 7 (UE4):** stages stream `light` (dynamic) + `lightstatic` (baked Lightmass) units
  — source: `teardown/tekken7/tekkenmods-docs/.../Stages/index.md`. UE4 static/stationary/
  movable modes; characters lit by movable lights + volumetric/SH probes.
- **Tekken 8 (UE5):** does NOT use Lumen/Nanite (Digital Foundry + dsogaming Lumen on/off
  tests) — ships baked stage lighting + dynamic character lights at 60fps. Validates the
  T7 split; real-time GI correctly out of scope for phones.
- **SFV (UE4 + Enlighten):** Geomerics Enlighten SH probes shade *moving* fighters with
  indirect light at runtime (80.lv 2016, Bochan Kim quote); fighters pushed brighter than
  background with strong rim to pop.
- **DOA6:** new engine with "physical lighting" (Shimbori 2018; OBORO 2026 interview) —
  honored as a constraint (keep PBR + shadowed key, don't flatten with ambient).
- **SC6:** mechanics docs only in teardown (50GB+ binaries never acquired) — flagged, not invented.

**Wired (all in `game/js/lighting-rig.js`, NEW):**
- `buildStageLightRig()` — the T7 split: hemi+sky+fog = baked-ambient stand-in
  (`lightstatic`); key/rim/fill directionals + accent points = dynamic rig (`light`).
  Exactly one shadow-casting directional per stage. `buildBase` in stages.js delegates here.
- `attachCharacterRig(fighter, stageDef)` — SFV-style character/stage separation: per-fighter
  key PointLight (front-top, parented to root — follows with zero per-frame cost) + soul
  glow (existing `auraLight` idles at soul-color baseline instead of 0 — **zero new lights**)
  + soul-tinted emissive (bible Grey's law: fighters are luminous *sources*; zero shader cost).
  Called from `Game.startMatch`; fail-silent.
- `applyGrade(arena, def)` — per-stage `lighting.grade { exposure, bloom }` drives
  ACESFilmic exposure (was global 1.45) + UnrealBloomPass strength (was global 0.6/0.85).
  Called from `Arena.setStage`. Bible "luminous darkness" dial per land.
- `buildMotes()` — atmosphere motes: 1 draw call, 0 lights, additive drifting points
  (bible §8.4 "darkness is a material"; pollen/cinders/bioluminescence per land).
- Soul light behaviors (bible §5c) in fighter.js aura update: BYOU flicker, TOU low/predatory
  (light at y=0.55), SHA shimmer, KAI tidal swell, RETSU pulse, ZEN absence (glow 0),
  GYOU hue-cycling rainbow; surge still flares to surge color.
- 8 canon lands carry `rig` (charKey color, rimBoost, motes) + `grade` blocks grounded in
  bible palettes (land §5b, Malakor violet §2, master §7). T3/No Mercy/boss stages inherit
  defaults. No pure RGB primaries.
- **Mobile budget:** hemi(1)+dir(3)+accents(≤6)+charKeys(2)+soul(2) = 14 max (+2 vs before,
  the only additions are shadowless character keys); motes capped at 110 pts on mobile.

**Environment/scenery:** motes system (above) + per-stage rig data are the new pulls. Prior
lanes already wired T3 retro arenas, No Mercy GLBs, Eastern Mind panos, Sun Rā (not duplicated).

**Accessories/clothing:** no additions — `customization/PARTS-REGISTRY.json` holds 1148 parts
across 13 libraries; WWE CAW extraction is another worker's in-flight lane (not duplicated).
T6/TT2 item meshes are locked/blocked (names only); T7 King armor pieces are Pantera's own
model, not detachable parts.

**Sweep flags (visual/environmental, unpulled):** Urban Reign `bg*.lit` stage-lighting moods
(8 files); VF5 18 arena `.farc` (release vf5-ps3-v1, needs 3ds Max chrrox + QuickBMS);
WMXIX arena point clouds → surfacing (43 OBJs); T6/TT2 item meshes; Def Jam venues (ISO
sourced); DOA6/SC6/SFV/T7-full binaries (not acquired); SC6 lighting docs (absent).

**Files:** `game/js/lighting-rig.js` (new), `game/js/stages.js` (rig delegation + 8 canon
rig/grade blocks), `game/js/scene.js` (grade on stage swap), `game/js/game.js`
(character rig on match start), `game/js/fighter.js` (soul-glow baseline + behaviors),
`docs/research/lighting-environment-pull-2026-10-22.md` (full audit), WORKLOG.md (this).

**Method:** base = main @ 822bdcc (2026-10-22T18:14Z) at first sync; re-synced to be7d2eda
before push (18 commits landed mid-work — only WORKLOG.md touched among my files; rebuilt
from the new base before appending). Fresh copies of scene.js/game.js/fighter.js/
stages.js/WORKLOG.md fetched from main (local fix3 copy was ~1 day stale — worker 16/17/19
had touched them). Surgical edits only; no deletions. Push via `~/workspace/fix2/gh_push.py`,
merge via `git_merge.py`. Sandbox note: exec-path file writes to ~/workspace/fix3/lighting/
started failing EPERM mid-task; WORKLOG.md was rebuilt as base@be7d2eda + this entry via
/tmp staging + symlink push tree — byte-verified, no clobber.

**Proof:** node harness with real three r160 (no DOM): 56/56 asserts pass (soul table,
rig light composition 1-hemi/3-dir/1-shadow-key, rimBoost math, motes updater + mobile
cap, character-rig attach incl. TOU low-light + fail-silent, grade application/defaults,
budget ledger). `node --check` ESM parse on all 5 JS files. Structural checks: old light
block gone, 8/8 canon stages carry rig+grade, no pure RGB primaries.
**NOT proven:** in-game screenshots (no browser on this VM) and device frame-time.
Visual verification: `game/stage-test.html?stage=shrine` + `game/index.html` fight —
fighter key/rim separation, soul-glow tint, motes, per-stage grade. Needs a
browser-capable pass; flagged for coordinator.

**Self-check:** asked-scope met (lighting wired + audit + scenery + sweep; accessories
documented-not-duplicated per directive) · shortcuts disclosed (no screenshots, no device
FPS — flagged) · proof attached (56/56 node asserts) · branch/PR · CI must be green ·
gitleaks clean (no gitleaks bin on VM; manual scan clean) · nothing copyrighted made public
(all code clean-room procedural; no game assets extracted).


---

## 2026-10-23 — Lars pull worker: CHORDZ moveset completion + Lars motion gap filed

**Owner instruction (verbatim):** "pull their animations and movesets fully and everything... and their stances and poses"

**Source hunt (all checked):** TTT2 `extracted-small/` = only Xbox LIVE packages + container descriptor (no game data); full TTT2 extraction blocked (disk ~27GB needed vs ~11GB free, safe-storage upload 5/26 chunks, STFS tooling, format RE). T6 PSP `decrypted/` = EBOOT only; DATA401 bulk transform still unknown (decrypt lane, branch `feature/tekken6-100-teardown`). T3 has no Lars (T6 debut). **No Lars motion extractable from any teardown today.**

**Moveset (done):** diffed `game/assets/movesets/chordz.json` (452) against the fullest Lars banks — `docs/t7t8-reference/frame-data-t7/lars.json` (186) + `docs/t7t8-reference/frame-data-t8-full/lars.json` (121). Added the 17 genuinely missing moves in Tekken notation: `f,f+2` (Surge Blast), `f,f+3` (Electric Jolt), `f,f+4`, `f,f+4,3`, `f,f+1+2` (Elbow Corona), `f,f+3+4` (Double Action), `WR.4`, `WS.1,F`, `WS.2,F`, `f,f+2,F` (->Silent Entry transitions), `GROUNDED.d+3+4` (Stack Up), `GROUNDED.d+3+4,F`, `FUFT.d+4`, `FUFT.d+3+4` (getup kicks), `TACKLE.2`, `R.d/f+1+2` (Rage Art Zeus Unlimited), `AIR.DEN.2+4` (Rejection alias). Moves 452 -> 469, strings 66 -> 71, `stance_after` +4 SEN transitions, `hit_words` for 15 new moves; `index.json` counts updated. Provenance in `merge_sources.added.lars_pull_20261023`.

**Animations/stance/poses (blocked, filed not stubbed):** no fake `lars` bank shipped (isolation doctrine + RULES_NO_GUESSING). Chordz keeps the flagged `jin` substitution bank (all 22 action clips present/valid). Precise gap filed: `docs/anim/LARS-ANIM-GAP-20261023.md` (exact missing bank files, TTT2/T6 blockers, unblock sequence) + pointer in the G-T6 register of `docs/anim/BANK-TABLE-2026-10-20.md`.

**Verification:** all 17 new moves resolve via the game's own `resolveMove('chordz', …)`; `node --test game/tests/fighter-completeness.test.mjs` green (4/4); new-move schema + source-id refs validated; jin bank clip files all parse with frames. Live-browser play verification (animations on Chordz in-game) is queued for a browser-capable lane — subagent has no live browser.

**Anti-clobber:** branched from main tip; sibling lane's WIP stashed intact; JSON edits via round-trip-safe scripted merges (diffs are additions-only); no deletions. Branch pushed via Git Database API (no GitHub connector for git ops).

## Cape Jones replaces Alisa — binding (owner t118u #4, t121u, 2026-10-23 14:20 CT)
- Additive `game/data/cape-alisa-binding.json` (built by `tools/cape/build_cape_alisa_binding.py`) binds all 188 Alisa T8 frame-data moves to fighter `cyborgx` (CAPE JONES, secret identity CYBORG X). Alisa source files untouched.
- Owner law t121u: no Tekken 3 source. Alisa motions must be decoded from T5/T6/T7/T8/TTT2 teardowns; current gunjack T3 fallback is logged as last resort in the binding file.
- Canon: `game/js/roster-full.js:145`, `game/js/fighter.js:57`, `game/ui-wh/roster_canon.json` (CYBORG X bio), `CANON.md` 821-849 and 1129-1152, `docs/bios/BIOS-HARVEST-2026-10-19.md` s3.
- Gaps (not invented): Cape-only extra moves; Alisa animation bank.
## 2026-10-23 — Claude session: T3 banks ogre/kuma/gon/law decoded; SmutBase rigs wired; loader race

- SmutBase: Chatur, Pond, Megami (crew rigs, facing +Z), Menajerii (crew rig minus a skinned 4.23 m floor plane),
  Ryusan + Tobi (re-rigged from statics stood upright by the new tools/auto_rig/reorient_static.py). PR #804.
  Proof: docs/proof/claude-2026-10-23/smutbase/.
- T3 banks: tools/anim/t3_bake_bank.py (new) decoded divmot14_ogre, divmot11_kuma, divmot19_gon, divmot01_law onto each
  character's own body (t3body_<bank>.glb), 30 clips each; skeleton.json via t3_bank_skeleton.py; rows.pack.json via
  t3_row_bake.py (ogre 187, gon 147, kuma 161, law 216 rows). Registered in t3anims.js (T3_BANKS, SOURCE_TO_BANK incl.
  panda->kuma) and fighter.js FIGHTER_BANK (chatur->ogre, dorowani->gon, menajerii->kuma). Buffalo Bill resolves to law.
  Forest Law: body fit fails on all four KMD costumes; follow-up via --kmd-from law.
- game/js/assets.js: loadModels no longer joins an in-flight load that it just aborted (idle lane) — fights with a
  still-warming fighter (Pantera) failed with AbortError.
- Verified: Chatur vs Pantera arcade fight on the ogre bank (t3_ogre_stance/walkFwd/row50/medium), no page errors.
  Proof: docs/proof/claude-2026-10-23/t3-banks/.
- Found, handed to the crew: Megami, Menajerii, Ryusan, Tobi have movesets + models but NO roster entries in
  game/js/roster-full.js (not selectable). Pond/Megami/Ryusan bases (Raven T7, Jun TTT2, Lucky Chloe T7) have no
  decoded animation bank anywhere in the repo.

## ANIMATION GATE — fight vs show (owner t117u, 2026-10-23 14:14 CT)

- Contexts: `FIGHT`, `INTRO_OUTRO`, `CUTSCENE` (story), `SHOW`. Module: `game/js/anim-gate.js`.
- In `FIGHT` only moveset clips may play. Any clip tagged show (`userData.animSet='show'`), named `show:*`, or pathed `anims/show/*` is **rejected and logged** (`gateLog` + `console.warn('[WH-ANIM-GATE] …')`).
- Enforced in code at the two places fight actions are created: `createT3Actions()` in `game/js/t3anims.js` and the embedded Idle/Walk/Run path in `game/js/assets.js`.
- Crossover only via allowlist `game/data/crossover.json`: fight clips → SHOW / CUTSCENE / INTRO_OUTRO; show clips → INTRO_OUTRO / CUTSCENE / SHOW, **never FIGHT** (`setCrossover` throws if anyone adds FIGHT). Changing that requires an owner-approved moveset PR.
- CI: `test/anim-gate.test.mjs` (picked up by rig-guard game-unit-tests) simulates 600-frame fights for every roster fighter with show clips injected, asserts 0 show clips played, and checks allowlist-only crossover. Mutation check: removing the gate line makes it fail (104 fails).

- 2026-10-23 14:25 CT Grok Bot (Repo Co Dev): recorded owner laws (relayed via MoneyManBusch). (1) 2:19 PM CT — data from T5/T6/T7/T8/TTT2; T3 last-resort fallback, every use logged with reason. (2) 2:21 PM CT — NO hand-made menus; all menus/char select/customization incl. packages/creation-suite built from teardowns, every UI change cites its teardown source; CI gate owned by MoneyManBusch; existing creation suite UI marked NON-COMPLIANT pending rebuild (not deleted). Updated RULES_NO_GUESSING, HOW-TO-CONTINUE, AGENTS.md, IMPORTERS.md, creation-suite README. Source: owner via MoneyManBusch.


---

## 2026-10-23 — Lars pull follow-up: SHOW-ANIMATION LOCK tagging

**Owner instruction (verbatim, new standing law 2026-10-23):** "Show animations and fight moves are SEPARATE LOCKED SETS. Tag everything you pull as FIGHT (moveset moves, stances used in combat → movesets and combat animation bank) or SHOW (win poses, intro poses, taunts, cutscene animations → intros/cutscenes ONLY, NEVER enter Chordz's moveset without the user's explicit approval). Keep the two sets separated in output files so the game-code lock can enforce the separation. Win poses and intro poses are SHOW — wire them to intro/win slots, not the moveset."

**Changes (follow-up PR to #797, which is merged):**
- `docs/anim/LARS-ANIM-GAP-20261023.md`: the missing-bank file list is now split into **FIGHT clips** (combat bank + moveset: neutral/stance idles, strikes, block/hit/ko, locomotion, rows.pack.json, skeleton.json) and **SHOW clips** (intro/win slots + cutscenes only: `t3_stance.json` → intro slot, `t3_win_rp.json` → win slot; taunts/cutscenes future). Unblock sequence now requires FIGHT/SHOW tagging at intake before anything lands.
- `game/assets/movesets/chordz.json`: file-level `anim_set_lock` metadata (law, FIGHT/SHOW definitions, approval requirement) + `"set": "FIGHT"` stamped on all 17 moves pulled this lane. The file itself is the FIGHT set.
- `game/assets/movesets/index.json`: bytes updated.

**Source priority redirect (owner 2026-10-23):** TTT2/T6 FIRST, T3 LAST (T3 has no Lars). Gap doc now states the priority and names the T5/T6/TTT2/T7 extraction coordinator lane as the manifest consumer; re-checked — no fresh Lars extractions on disk yet.

**Verification:** semantic diff audit — 0 field losses, 0 removals, additions only; all 17 new moves tagged; `node --test game/tests/fighter-completeness.test.mjs` green.

**Deviations:** none — the 17 pulled moves are all combat moves (FIGHT); no SHOW content entered the moveset.

## 2026-10-23 — Priority-5 moveset pull: burger/purplerain/pantera/torch/michiko (T8+T7 diff, SHOW-ANIMATION LOCK, anim-bank gaps)

**Owner instruction (verbatim):** "Now we need to get that done for every other character" (2026-10-23) — the Law/Lars full pulls (PR #806 / PR #823 pattern).

**Method:** For each of the 5 priority fighters, read `game/assets/movesets/<fighter>.json` and diffed `game/data/t8_frame_tables.json` → `chars.<source>` (exact key match against the builder's parent-chain join) plus the full wavu rows in `docs/t7t8-reference/frame-data-t8-full/<source>.json` against every reachable notation in the file (key/input/input_slots/t7_command canonicalized + slots + t8_id identity). T7 rows in `docs/t7t8-reference/frame-data-t7/<source>.json` diffed by move id. Genuinely-missing = input not reachable by any existing move.

**Result — 0 genuinely-missing moves on all 5 (nothing re-added):**
- `game/assets/movesets/burger.json`: 552 → 552 (T8 bob 161/161 inputs reachable; T7 bob 281/281 rows by id)
- `game/assets/movesets/purplerain.json`: 569 → 569 (T8 lee 156/156; T7 lee 265/265)
- `game/assets/movesets/pantera.json`: 873 → 873 (T8 king 215/215; T7 king 297/297)
- `game/assets/movesets/torch.json`: 892 → 892 (T8 anna 165/165; T7 anna 354/354)
- `game/assets/movesets/michiko.json`: 344 → 344 (T7 katarina 189/189 by id; T8 has no Katarina — verified, `chars` has no `katarina` key)

**Changes:**
- All 5 files: file-level `anim_set_lock` metadata (SHOW-ANIMATION LOCK, owner 2026-10-23; chordz.json pattern) + `merge_sources.added.<fighter>_pull_20261023` provenance with per-source coverage counts.
- `docs/anim/BOB-ANIM-GAP-20261023.md`, `docs/anim/LEE-ANIM-GAP-20261023.md`, `docs/anim/KATARINA-ANIM-GAP-20261023.md`: FIGHT vs SHOW intake manifests for the extraction coordinator (no T3 bank exists for Bob/Lee/Katarina — Bob debuted T6, Lee skipped T3, Katarina debuted T7; current bryan/jin/jin proxies flagged, not blessed).
- `game/assets/movesets/index.json`: bytes updated for all 5.
- Pantera (king bank `game/assets/anim/t3/king_on_pantera_leoman/`) and Torch (`anim_bank: "anna"` → `game/assets/anim/t3/anna/`) already wired — no gap docs, no t3anims.js changes.

**Verification:** exact-match diff audit (every T8 compact key joined to its source row); semantic check — 0 field losses, 0 removals, additions only (lock + provenance); all 10 JSON files parse; `node --test game/tests/fighter-completeness.test.mjs` green.

**Deviations:** none — no SHOW content entered any moveset; no wrong-bank substitution (proxies left untouched, flagged in gap docs).

## 2026-10-24 — Claude session: limb isolation on all auto-rigs; Chordz + Sam-ur-A1 wired
- New `tools/auto_rig/backends/limb_isolation.py` (one leg's vertices drop weight from the other leg / the arms; arms
  likewise; core untouched) — the web between Skull's legs in a high kick. Step of `rig_tripo_static.py` now.
- Applied in place to the 16 GameRig rigs from 2026-10-23 (git history keeps the previous files); all 16 hold the T3
  stance in game. Chordz (Claude rig, same stance as the crew's `source/chordz-a1-rigged.glb`, which stays) and
  Sam-ur-A1 (`model-rerig.glb`, replaces the sideways k-NN rig) wired. Proof: docs/proof/claude-2026-10-23/rerig/.
- Verified on main + this branch: boot 2.9 s, every game/js module parses, Skull vs Thor arcade fight, no page errors.
  `node --test game/tests`: the 3 failures (negativo/yukihyo/vainabel resolution, rage + urge inputs) fail identically
  on main alone.

---

## 2026-10-23 — Track 4 (advanced systems): Project Chrono grappling lane

**Owner instruction (verbatim):** "Pull all of this stuff in and wire it up and put it to work the best way possible"

**Architecture decision: AUGMENT, not replace.** Chrono fills one gap — articulated joint constraints with torque readout for grappling. cannon-es keeps visuals-only rigid bodies, Jolt keeps XPBD soft tissue, PhysicsServo keeps the muscle layer. Full Chrono C++ → WASM is SPEC ONLY (official Emscripten tutorial path documented); no maintained JS/npm Chrono package exists, and a multi-MB WASM engine is wrong-sized for a ~6-body subsystem that must be bit-deterministic for rollback.

**Changes:**
- `game/js/chrono-grapple.js` (new, ~700 lines, zero deps, no three.js): Chrono-inspired joint taxonomy (FIXED/SPHERICAL/REVOLUTE/PRISMATIC/UNIVERSAL), ChronoEngine (torque/speed/position), ChronoSpring (runtime-variable stiffness muscle model), per-link torque nodes (reactionForce/reactionTorque), MuscleStrain (real-time strain calc, tap-out, bone-snap), SubmissionChain (data-driven: armbar/kimura/triangle/rear-naked choke), GrappleRig + ChronoGrapple facade with PhysicsServo contract (`getServoTargets()` → per-limb PD targets, null while idle).
- `game/tests/chrono-grapple.test.mjs` (new): 18 tests, all green.
- `game/js/integration.js`: additive block 8 (`tryInit('grapple', './chrono-grapple.js', …)`) + `S.grapple.update(dt)` in the frame loop. No existing logic touched.
- `docs/research/CHRONO-PHYSICS-2026-10-23.md` (new): evaluation, license (BSD-3-Clause, verified), replace-vs-augment table, [WIRED]/[RESEARCHED]/[SPEC ONLY] marking, WASM vendor path, open questions.

**Verification:** `node --test game/tests/chrono-grapple.test.mjs` 18/18 green; full suite 80/84 with the same 4 pre-existing full-suite-mode failures as pristine main (fighter-completeness/v-system parallel-run flakes — verified by stashing). All four submission chains measured end-to-end: entry → control → lock → tap with in-band torques. Determinism asserted (identical runs ⇒ identical snapshots).

**Deviations:** none. License note: user lifted the license firewall 2026-10-23; Chrono is BSD-3-Clause regardless, and the wired module is WH-original code (architecture-inspired, not a derivative).
## 2026-10-23 ~19:30 CDT — UniRig auto-rig intake integration (PR #956, branch muse/unirig-autorig-integration)

**Owner instruction (verbatim):** "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate" — item: UniRig (SIGGRAPH 2025, MIT license), AI auto-rigging for the Tripo intake pipeline + creation suite auto-rig.

**Pulled:** UniRig cloned to ~/workspace/research-pull/unirig/UniRig (VAST-AI-Research, MIT). Studied the inference API: launch/inference/generate_skeleton.sh (autoregressive skeleton prediction, checkpoint skeleton/articulation-xl_quantization_256/model.ckpt) -> generate_skin.sh (bone-point cross-attention skinning, skin/articulation-xl/model.ckpt) -> merge.sh (bpy merge of skin back onto source mesh). Weights auto-download from Hugging Face VAST-AI/UniRig.

**Wired:**
- `tools/rig-intake/unirig_intake.py` (new): wrapper driving all 3 stages via subprocess. `rig_model(src, out)` raises on failure; `maybe_autorig(src, workdir)` never raises — returns rigged GLB path or None. Env: UNIRIG_ROOT, WH_UNIRIG (master switch), WH_UNIRIG_SEED. `--check` readiness probe.
- `tools/rig-intake/UNIRIG-SETUP.md` (new): exact GPU-machine setup (conda, torch+cu, spconv/torch_scatter/torch_cluster/flash_attn version-match notes, weights prefetch, ComfyUI one-click option, wiring, troubleshooting table).
- `tools/rig-intake/README.md` (new): provider contract for future auto-rig plugins.
- `tools/rig-intake/tests/test_unirig_intake.py` (new): 10 unit tests, all pass.
- `tools/import_model.py` (surgical): hook probes incoming GLB; unskinned meshes auto-rig via UniRig when GPU+checkout present, `rep["unirig_autorig"]` recorded; fail message updated with the UniRig setup option.
- `docs/MODEL_IMPORT_AUTORIG.md` (surgical): step-3 status PARTIAL -> DONE (GPU-gated).

**Verification:** 10/10 pytest pass; --help exits 0; --check correctly reports NOT READY on this GPU-less VM (exit 1); py_compile clean; gitleaks clean. Full GPU inference pending Grok's box (coordination posted on issue #866, comment 6377665231). Note: upstream now points to SkinTokens as UniRig's successor — follow-up candidate, stayed on UniRig per owner item.

**Anti-clobber:** branch from fresh origin/main; sparse checkout in this tree (lab/ etc. excluded) — committed via Git Data API (push_branch_api.py) building from main's real tree + only this task's 6 files; verified via compare API that the branch diff is exactly the 6 files (4 added, 2 modified), 0 deletions. gitleaks clean. No deletions.

**ALL CHARACTERS ARE ADULTS:** n/a — rigging pipeline, no characters.

---

## 2026-10-23 — Moveset batch8 pull: bruno / docfrank / chatur / samura1 / star (PR pattern #823/#806)

**Task:** replicate the Law/Lars pull pattern for 5 fighters (TTT2/T6/T5/T3 sources, no T8 data for these).

**Method:** `tools/moveset-merge/merge_sources.py` (the proven pipeline — guard enforces additions-only, every new move carries `merge_source`). Dry-ran all 5, wrote only where genuinely-missing moves existed.

**Per-fighter results:**
- **bruno** ← Miguel (T7): pull already complete — 219/219 T7 rows merged (`docs/t7t8-reference/frame-data-t7/miguel.json`; 206 curated with Miguel's real move names + 13 `t7:miguel_*`). +0 moves. Motion gap filed: `docs/anim/BRUNO-ANIM-GAP-20261023.md` (no Miguel bank; bryan T3 proxy flagged; unblock = T7 pull on owner's Steam purchase).
- **docfrank** ← Bosconovitch: T3 rows 100% covered (all 251 source rows present). +0 moves. TTT2 Bosconovitch movelist has no data on disk (extraction blocked) — noted, not faked.
- **chatur** ← True Ogre (T3): **+129 moves** (152 → 281), all `merge_source: t3:ogre:row:N`, all tagged `"set": "FIGHT"`. `anim_bank: ogre` now set by annotate(). T3 use logged per INSTRUCTION GATE in `docs/anim/PROCEDURAL_AUDIT.md` (True Ogre is T3-only — cut from T5/6/7/8/TTT2; no newer source exists).
- **samura1** ← Gun Jack: T8 Jack-8 + T7 Jack-7 + T3 Gun Jack pulls all complete. +0 moves.
- **star** ← Christie: Christie T5/TTT2 movelist unavailable (no data on disk; TTT2 extraction blocked). +0 moves. Motion gap filed: `docs/anim/STAR-ANIM-GAP-20261023.md`. **Owner decision flagged:** bases.json 2026-10-20 override says "Xiaoyu's moveset goes to Star" but canon base is Christie — both can't be permanent; left untouched for the owner.

**SHOW-ANIMATION LOCK:** `anim_set_lock` metadata added to all 5 files (law/FIGHT/SHOW/note + batch8 pull note). Per-move `"set": "FIGHT"` stamped on the 129 chatur additions. Banks already wired: `T3_BANKS` + `SOURCE_TO_BANK` + `FIGHTER_BANK` cover bosconovitch/gunjack/ogre (docfrank/chatur/samura1); win clips (`t3_win_*.json`) present in all three banks = SHOW set.

**Tool fixes (needed for the pull, shipped in this PR):** `tools/moveset-merge/merge_sources.py` — `identity()` crashed with `TypeError: unhashable type: 'list'` on older files whose `t3_row` is a list (chatur's 21 multi-row string moves); added `_hashable()` coercion (upstream fixed the sibling `bank_attack_word` spot in parallel). `tools/moveset-merge/bases.json` — added `bruno: {t7: [miguel]}` and `chatur: {t3: [ogre]}` overrides.

**Verification:** guard PASS on every run (no move/string/special/input lost); semantic diff audit — 0 field losses, 0 removals, additions only; `node --test game/tests/fighter-completeness.test.mjs` green; gitleaks clean.
