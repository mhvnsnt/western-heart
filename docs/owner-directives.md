# Owner Directives — M.Dogg's standing orders for Western Heart

Living document. Updated every time the owner sets a directive. Newest first.

## 2026-10-24 — Animation strategy: DECODED vs MADE

- **Animation strategy (2026-10-24).** Every animation is DECODED or MADE, labelled as whichever it is, never the other. Full decision doc: `docs/decisions/2026-10-24-animation-strategy-decoded-vs-made.md`. Method doc: `docs/handoffs/COMBAT-RIGHT-WAY-2026-10-24.md`.
- **DECODED animations (2026-10-24).** Motion bytes from a shipped game, with recorded source file, row/slot, and the exact move they belong to. In the repo today: Tekken 3 banks (22 banks, `game/assets/anim/t3/`) plus T3 hit reactions/throws (7,368 clips, PR #1003). Tekken 7 decoded animation coverage in the repo is 0 of 51 (`teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md`) — frame data is not animation, and no community dataset has move → animation IDs.
- **MADE animations (2026-10-24).** Motion created for canon moves with NO Tekken equivalent. Methods, in order: adapt a decoded T7/T3 clip, blend decoded clips, build from the move's recorded properties (input in LP1/RP2/LK3/RK4 form, startup/active/recovery, hit level, range, damage), community libraries with recorded licence and provenance. Verification: property check + `node tools/anim/attack_anim_audit.mjs` (0 strikes on throw rows, 0 throws on strike rows, 0 generic fallbacks, string continuations checked too) + touch-play on the live build with screenshots viewed. A MADE clip is replaced by the real decoded clip the moment one exists.
- **EXTRACTION vs CREATION decision tree (2026-10-24).** Tekken move exists → EXTRACT, never make or class-match; canon move with no Tekken equivalent → MAKE; neither specified → stop and get the source identified. Bans: no class-matching (a jumping punch is not a standing jab, even though both are strikes), no mislabelling (a T3 clip is T3, a MADE clip is MADE, a T7 clip is T7 only from a T7 extraction).
- **Extraction paths (2026-10-24).** Live TKMovesets extraction from a running T7 (authoritative for T7, output to private repo `mhvnsnt/game-reverse-engineering`, never raw game files in the public repo); mot.bin RE in parallel as backup; Steam pak extraction as the heavy fallback; TTT2/T6/T5/T3 only where the character exists in that game (T6 `DATA401` still encrypted, T5 motions named but not extracted — do not claim coverage that does not exist).
- **940 blocked slots (2026-10-24).** Pond (Raven base), Ryusan (Lucky Chloe base), Megami (Jun base) — no decoded sets for these Tekken bases, 940 animation slots total (issue #866 comment `6389250251`). Paths to unblock: live TKMovesets extraction for Raven and Lucky Chloe; TTT2 extraction for Jun (Jun is a TTT2 character, not a T7 roster character, so the #866 TKMovesets request for Jun needs retargeting to TTT2) plus mot.bin RE in parallel. Wider request: live TKMovesets extraction for ALL T7 characters (#866 comment `6388949909`, King first). Ryuji and Vain Abel are flagged as also blocked in the same comment but their Tekken bases are unverified — they are NOT folded into the 940 until verified. Until extractions land, the 940 stay UNMAPPED in the editor; an honest UNMAPPED beats a wrong clip.
- **Joystick fix confirmation (2026-10-24).** PR #1001 (dynamic mode, deadzone, any-touch=down fixed) and PR #1003 (touch joystick fix + decoded T3 hit reactions/throws + combat right-way doc) are BOTH merged. Do NOT duplicate them, do NOT re-apply them, do NOT open another joystick-centre fix without first reproducing the report on the live build with the touch probe. Remaining joystick work is live verification only.
- **MOD damage confirmation (2026-10-24).** PR #1000 (8 fighters) + PR #1002 (remaining characters) are both merged — all T7 characters' moveset blocks are wired with TheBigTuna MOD damage values. Damage wiring is done; it is not animation progress, and a move can have the right damage and still play the wrong clip.
- **Editor confirmation (2026-10-24).** PR #998 merged — the Create-A-Move List editor (`packages/creation-suite/src/movelist-editor.js`) shows an animation for every move that has one, or UNMAPPED with a specific reason for every move that does not. UNMAPPED is the work list, not something to paper over.
- **Non-T7 characters directive (2026-10-24).** Owner: "for every character even the ones that aren't in t7." The same decision tree applies to every fighter: a non-T7 fighter's decoded motion comes from the game its base IS in, or from WWE/other game/community data with recorded source and licence, exact-move mapping, and its real label — never another fighter's moves or stance borrowed because a source is missing. Where no source exists, the move is MADE or stays UNMAPPED.

## 2026-10-22


- **NINE SOULS CHARACTER SELECT REDESIGN (user directive 2026-10-22 ~23:02 CDT,
  verbatim).** "Alright, that means everybody except for Zen and Gaiu has to
  come off of the character select screen because they don't have actual um
  bodies to select for fighters. But what we can do is make a version of them
  where we have an attire for whoever they go to um Ren how he goes to Demonio
  Bayu goes to Zui two goes to Pantera Shaw goes to Sakura and the other three
  I mean the other two like we can have attires you know and so on down the
  whole list um we can have an attire for each of those characters where they
  have the spirit version of the non soul whatever one goes to them floating
  behind them as an attire and so I'll make the spirit versions of those of
  the non but since there's two of the nine that are actually have bodies and
  fighters then those are the only two that should be on the character select
  screen all the other ones should just be attire variants like you can select
  to have them floating behind the attire like on or off like it shouldn't be
  an in the attire thing whatever fighter has them you should be able to hit
  it it's like a a tertiary thing where you can turn the um nine soul uh
  spirit on or off and then choose between the nine souls but if you choose
  the one that goes to the character you're choosing then it um empowers them
  more or something like that and then log all of that and put it into the
  repo word for word exactly how I said it"
  - Interpretation locked with the user: the 7 vesseled souls (RIN, BYOU,
    TOU, SHA, KAI, JIN, RETSU) come OFF the select grid as standalone
    entries; only ZEN and GYOU stay selectable. Every fighter gets a
    TERTIARY soul-spirit toggle (not an attire): on/off + pick any of the
    nine souls; picking the soul that vessels into the chosen fighter
    empowers them (gameplay buff). Phonetic spellings in the voice note:
    "Ren"=RIN, "Bayu"=BYOU, "two"=TOU, "Shaw"=SHA, "Sakura"=Saku Ra,
    "Gaiu"=GYOU. The user makes the spirit versions themselves — no
    AI-generated stand-ins. Implementation: `game/js/soul-spirit.js`,
    select-screen toggle, `SELECT_HIDDEN` in `game/js/select-screen.js`.
- **NINE SOULS: unlockable boss-type return (user refinement 2026-10-22
  ~23:03 CDT, verbatim).** "We'll only add them like later on onto the
  character list as like characters with vessels or bodies as like kind of
  boss creatures but we'll figure out how that gets done later on as we
  progress through all the different modes and the stories and things for the
  characters. The the seven of the nine souls that don't have bodies we'll
  figure out how to incorporate them into the character select screen later
  so for right now they have to come off of the character select screen until
  we get them unlockable and with bodies."
  - The 7 stay OFF the grid for now; they return later as UNLOCKABLE
    boss-type characters with vessels/bodies. The unlock path gets designed
    as story modes progress — not now. Zen and Gyou remain selectable per
    the previous directive. The soul-spirit toggle still applies.
- **BANNON SUB-UNIVERSE LAW (2026-10-22).** The Bannon/Ashlane/BrutalFist universe is a
  SUB-UNIVERSE of the Western Heart multiverse. The Bannon game
  (`mhvnsnt/brutalfistgrokversion`, `native/media/characters/chara_bannon/` — identity,
  character, moves, bones, hitboxes TXTs) is the canon source for the 28 fighters ("off the
  top rope canon"). Ashlane characters keep their existing bios/backstories from their repos —
  then each gets a "how they arrived" bridge into WH/Eastern Mind canon (the call, the trial,
  Tong-Nou, lost souls). Raw-material reference:
  `docs/research/bannon-universe-canon-package-2026-10-22.md`. All writing laws apply (adults
  only, canon-grounded, no Tekken names in canon).
- **Audio delivery: direct download links, NEVER in-chat attachments
  (2026-10-22).** The in-chat audio player is broken on the owner's
  Android app (shows 0:00, won't play). ALL audio files sent to the owner
  — voice clips, demos, music — go as direct download links via
  remote-storage upload (`/opt/hatch/bin/remote-storage upload-file`),
  with the link expiry stated. This applies to every agent, every time;
  the voice pipeline's `deliver` stage does it automatically
  (see `tools/character-voice/voice-clone/`).
- **ANTI-CLOBBER LAW (permanent — written in blood after PR #579).** On
  2026-10-22 PR #579 committed stale full-file copies (base from Oct 17),
  wiping 427 lines of `game/js/assets.js`, 113 of `game/js/main.js`, 32 of
  `game/js/game.js`, 25 of `index.html`, 316 of `WORKLOG.md` — Torch broke
  live. Root cause: agents working from stale clones committing whole files.
  Never again. Four rules, no exceptions:
  1. **Sync to latest main BEFORE starting any file work, and again BEFORE
     committing.** A base more than a few hours old gets re-synced.
  2. **Surgical edits only** — never write a whole file when a targeted edit
     will do. Fresh sync + surgical edits; never commit stale full-file
     copies.
  3. **Any diff deleting >20 lines must be intentional and called out** in
     the PR body (`## Reverts` section naming each file, or the
     `owner-approved-revert` label).
  4. **If your base is more than a few hours old, re-sync.**
  Enforced by machinery, not memory: the `clobber-guard` CI check blocks any
  PR whose version lacks lines main added after the PR's base;
  `tools/clobber-check/clobber_check.py` runs the same check locally before
  pushing; the `git_merge.py` merge helper refuses to merge such PRs.
- **Everything goes in the repo.** Every conversation — everything the owner
  says, everything the assistant says, all research — is saved into the repo
  every time: `docs/owner-directives.md`, `docs/research/`, `docs/decisions/`.
  Never wait to be asked.
- **Division of labor.** Owner does surgical hand-tooling (the parts AI
  struggles with — faster than 20 back-and-forths). Crew does automatic
  pulling, wiring, industry-standard open-source stack. Crew gets surgical
  only when asked. Owner wants to feel like a real game dev (Tekken studio /
  2K studio) doing non-code work: art direction, animation review, tuning,
  playtesting. No interest in learning to code.
- **Collaboration loop.** Crew ships a piece → it goes live on
  https://mhvnsnt.github.io/western-heart/ → owner reviews and hand-tweaks →
  crew runs industry-standard automation → shows result → repeat. All inside
  the customization suite, which is improved as a deliverable each round.
- **Round trip.** Suite gets a save/export button → owner tweaks, downloads a
  patch file, sends it in chat → crew validates and applies via PR. Suite can
  also load crew-staged tweak kits.
- **Tag-team community creations.** The owner + crew build like WWE Community
  Creations but two-way: two people in different places working on the same
  character, both involved — the feature WWE lacks.
- **Merge after every pass.** Clean merges into main, no clobbering either
  side (via `tools/git-merge/git_merge.py`).
- **No-stubs rule.** If it's in the repo, it's wired up and working. Audit
  regularly; stubs get finished or removed.
- **Tekken base first.** Full skinning pipeline (bind pose, heat-map skinning,
  rigging, boning) for every character/GLB. Perfect the Tekken base (skeletons,
  models, moves, customization) so everything built on top works.
- **Game feel.** Feels like Tekken, with extra physics — partial ragdoll
  inspired by Gang Beasts / Human Fall Flat / Mortal Kombat Royal Rumble.
  NOT fully ragdoll.
- **WWE 2K26.** Pull animations, code, physics — NOT models.
- **Tripo auto-intake.** New Tripo models get rigged ASAP to their character
  rig. First live intake: Torch Attire 3 "Bald eagle."
- **Torch Attire 3 is the reference piece.** Full jiggle set (breasts, belly,
  hips/ass, thighs, camel-toe); repaint painted-on clothing as skin with
  pores; full anatomy (areolas, clitoris, labia) from Scarlett/Madeline
  reference models; proof must include motion capture, not just stills. Once
  perfected here, the system rolls out to other models.
- **Character select rule.** Attires ladder into their fighter; an attire is
  NOT its own selectable model unless the owner explicitly said so
  (e.g. Yoshimitsu ladders into Phantom's attires).
- **Asset sourcing.** Ripped/ported models (Tekken extracts, SmutBase ports)
  are raw material — transform heavily into the Western Heart universe's own
  characters. Owner made this call; legal caution was given and acknowledged.
- **Master roadmap.** All movesets from Tekken teardowns + canon moves;
  Tekken-like character creation and select screens; 100% teardown of all
  Tekken games (then other games' teardowns); the game feels like all Tekken
  games combined + our own stuff on top, then turned proprietary.
- **Tekken 3 scope (user 2026-10-22 ~17:30 CDT).** Owner verbatim:
  "We won't need Tekken 3 models — too much to decode for bad low-poly
  quality. But everything else — the moves, the arenas, the menus — from
  all the other Tekken games, get the models from all those." Rule:
  Tekken 3 = pull everything EXCEPT character models (moves, movesets,
  arenas/stages, menus, UI, systems, audio — yes; character models —
  skip). All other Tekken games (T5, T6, TTT2, T7, T8) = pull everything
  INCLUDING character models. Detail:
  `docs/decisions/2026-10-22-tekken3-scope.md`.
- **Hardened Mind Within mode.** Tekken "Devil Within"-style mode; each
  character selectable with their own storyline; wave/tournament feel like
  Mortal Kombat Royal Rumble in places. All fighters rigged and working for
  it and all other modes.
- **No full game downloads.** Use `tools/depot-pull/` — pull only needed
  files piece by piece. Disk rules are mandatory for all agents.
- **Character select: Tekken 8 grid (2026-10-22 playtest).** Rebuild the
  character select on the most recent obtainable Tekken menu grid: pull in
  the Tekken 8 character select menu, decode the UI/menu art/selections/
  layout, and put OUR fighters on it. Grid of portrait cards (small relative
  to everything else), big live 3D model of the highlighted fighter, name
  banner art, fact block, P1/P2 cursors, bottom hints bar. Portraits must be
  personality/canon poses, not T-poses. No duplicate fighters, no duplicate
  images — only attire ladders (Tekken chars behind proprietary per the
  display order law). Upgrade rigging/skinning so models pose correctly in
  the big 3D view.
- **Menu load speed (2026-10-22 playtest).** Menus load too slow — study how
  Tekken/teardown games handle loading and pull that in.
- **T8 UI assets: no depot, no rips.** The Steam/depot route for real Tekken
  8 UI files is dead (owner doesn't own T8 on Steam). The T8 look is
  recreated from public references with original art — NO ripped Tekken UI
  files in the public repo (rule 8). The select screen reads its look from
  `game/js/ui-skin.js` so future skins/textures drop in without touching
  screen logic.

- **CONTROL ACCEPTANCE CRITERIA (owner verbatim, 2026-10-22 — this is the
  bar for the moveset/input track).**
  - JOYSTICK: "JOYSTICK IS FINE — DO NOT TOUCH IT." The joystick placement
    and feel are good. Leave it exactly as-is.
  - FACE BUTTONS: "THE PROBLEM IS THE FACE BUTTONS. They're 'fucked up and
    real bad' — overlapping, ugly, badly positioned." Fix ONLY the face
    buttons: "PSX layout: Square (1/Left Punch), Triangle (2/Right Punch),
    X (3/Left Kick), Circle (4/Right Kick)"; "Clean positioning, no
    overlaps, good spacing"; "Work in portrait AND landscape".
  - MOVES (owner verbatim): "Pressing buttons does random moves or nothing
    → every button must do its CORRECT Tekken move, every time"; "Combos
    don't work, just one random move at a time → real working combo
    strings"; "Some buttons don't work at all → every button functional".
  - PROOF: "THE USER WANTS PROOF. When done: Show a working build where each
    button does its correct move (button-by-button demo); Demonstrate combos
    working (strings, not single moves); Verified by actually PLAYING, per
    the standing rule — not code inspection."
  - The joystick approved by the owner is `game/js/input.js` as it exists on
    main — the moveset lane reverted its own joystick edits (2026-10-22) and
    does not own that file.

- **Soul Urge — NAME LOCKED (2026-10-22).** Tekken 8's Heat system renamed
  proprietary to "Soul Urge". Pulled straight from the T8 files. Everywhere:
  code, docs, UI, canon — never "Heat".
- **Gungaku — NAME LOCKED (2026-10-22).** 軍楽 ("war music") — the fight lab /
  programmable training dummy mode (TTT2 Combot equivalent).
- **Rank ladder (owner-built 2026-10-22): 53 tiers.** Lost Soul (placement) →
  9th–1st Kyu → 1st–3rd Dan → Brawler→Warrior→Marauder→Vindicator→Slayer→
  Warlord → Kappa→Kitsune→Tengu→Oni→Nio→Fudo Myoo → Jikokuten→Zochoten→
  Komokuten→Bishamonten → Genbu→Byakko→Seiryu→Suzaku →
  Fujin→Raijin→Yaksa→Ryujin → Rin 凛→Byou 病→Tou 闘→Sha 沙→Kai 海→Jin 刃→
  Retsu 烈→Zen 禅→Gyou 行 → Whole→Purified → S: Assembled → Super S:
  Tong-Nou → TOP (51): Master God of the Universe. **Tiers 52–53 RESERVED
  and UNNAMED** — invented only when a player holds #51 long enough,
  Tekken-style. **Rank names are data, never hardcoded** — new tiers drop in
  freely. Offline rank battles, online ladders/leaderboards, promotion/
  demotion. Teardown research: `docs/research/rank-system.md`.
- **TTT2 team battle.** Tag-team mode pulled from the Tekken Tag Tournament 2
  teardown: mode structure, tag mechanics (tag in/out, tag throws, tag
  assaults/combos, partner synergy) — wired into WH as a proper mode; all
  fighters team-capable.
- **Heart and Mind Within — integration order.** Tekken 5's Devil Within is
  torn down 100% FIRST (structure, level flow, power-ups, bosses), THEN the
  proprietary story is built on top. The character select is never forced to
  Jin — every WH fighter gets their own campaign chapter. Cutscenes are
  real-time rendered in-engine, never pre-rendered video.
- **Mode-mapped teardown strategy.** Urban Reign → brawler systems; SF/DOA/SC
  → versus systems; all teardowns → story systems.
- **Teardown wiring priorities.** The ready-to-pull list is the build order.
  DOA4 repair is on the list. Incomplete teardowns get finished before new
  pulls. SoulCalibur II pull decision is PENDING an owner call.
- **Yu Yu Hakusho / Evil Zone.** Need the owner's game copies before teardown
  — pending owner question.
- **Game ownership rule (owner-clarified 2026-10-22, reinforced).** When the
  owner says they own a game / asks for a game to be pulled, THAT IS
  AUTHORIZATION — they own it, no proof needed, never ask for files. They own
  physical copies — they can't hand over discs and won't do manual ripping.
  Find the files from public archival sources (Internet Archive etc.); store
  large files on Releases/external, not local disk. When the user says
  they've bought Tekken 8, pull it immediately — no questions, no proof
  requests. The ONLY exception is T8 right now, because the user explicitly
  said they don't own it YET.
- **Tekken 8 acquisition status (owner, 2026-10-22).** Owner bought Tekken 8
  on console ($24), but the file pull NEEDS the Steam version (PC is
  Steam-only; console files are encrypted/unusable). Owner is buying it on
  Steam and trying to refund the console copy. Pull happens the day they
  confirm the Steam purchase. Cheapest found: $18.20 Steam key (GameBoost)
  or $23.99 Steam sale.
- **Jiggle / face / hands — teardown findings + wiring priorities.** Wired per
  `docs/JIGGLE-FACE-HANDS-WIRING-2026-10-22.md`: full jiggle set (breasts,
  belly, hips/ass, thighs, camel-toe region), face rig standard, hand rig
  standard. Proof must include motion capture for anything physical, never
  stills presented as done.
- **Announcer YES / crowds deferred.** The announcer voice system is approved
  and stays in scope. Crowd systems are DEFERRED — not built now.
- **Voice mapping by personality.** Voices are cast by the fighter's
  personality and canon, not assigned randomly. Dorowani is the FIRST
  voice-acted character: Squirtle-like creature sounds + barked random
  Japanese words — never full sentences. First lines: "Konnichiwa arigato
  Ichiban Bankai." Voice moments: win poses/taunts, intro sequences,
  cutscenes.
- **Music systems + replacement pipeline.** Approved: jukebox, music systems,
  and a music replacement pipeline.
- **Lighting + environment pull priorities.** Lighting and environment tech
  follow the teardown wiring priorities order — pulled from teardown games,
  not hand-tooled.
- **Approved systems batch.** Stage mechanics, rage (WH version), training,
  replays, single-player, unlockables, jukebox, ranks, cinematics — all
  approved; built in teardown wiring order.
- **Combat depth approvals.** VF5 throw escapes — approved. SoulCalibur 8-way
  run + guard impact — approved. Item moves — approved.
- **Triangle (DOA) + Reversal Edge (SC): ON HOLD.** Design proposals must show
  Tekken-ified versions that don't hurt feel/flow before anything is built
  (owner: "Tekken doesn't use those for a reason"). Nothing built until a
  proposal is owner-approved.
- **WWE entrance tools repurposed.** WWE entrance tooling is used for
  cutscene creation + taunt creation ONLY — NOT full entrances. Intros/win
  taunts stay as-is. Proprietary name TBD.
- **V-System.** WH version of SFV's V-System approved; Eastern Mind names TBD.
- **Learning tools: all approved.**
- **Tekken Force, Scenario Campaign, create-a-finisher, create-an-arena.**
  All approved as future modes/features; built in teardown order.
- **Mythology-themed side games.** Just Fun modes draw from traditional
  mythologies — mainly Japanese, mixed with world mythologies/cultures/
  anthologies per NORTH STAR: Five Lands settings, Phantom Marketplace,
  mini-trials, soul games, matsuri/festival games, spirit trials, yokai
  pastimes — never generic bowling. Specific concepts need owner approval.
- **Online: netcode, lobbies, tournaments, dailies.** All approved; built
  per `docs/research/netcode-multiplayer-streaming.md`.
- **Canon mapping requirement for ALL systems.** Every system — modes, menus,
  mechanics — is canon-mapped to the Eastern Mind / Western Heart universe
  (CANON.md: Tong-Nou, Nine Souls, Five Lands, the Trial, the Trader).
  Nothing ships un-mapped.
- **INPUT-TO-MOVE FIDELITY LAW (owner's feel principle, 2026-10-22).** In
  Tekken every input produces a specific, predictable move — the player's
  fingers and the character are tightly coupled. The moveset rebuild must
  achieve tight 1:1 input-to-move fidelity: not just correct mappings, but
  the FEEL of correctness.

## 2026-10-21

- All fixes by AI agents, no hand-tooling by the owner (later refined — owner
  now does surgical hand-tweaks in the loop).
- Model-quality round: fix Pantera weights, Doc Frank feet, root-cause the
  "backwards decrypt" in the pipeline (not per-model tweaks), Doc Frank
  attires Tripo-first ordering.
- `git_merge.py` saved to `tools/git-merge/` via PR #495 for merging clean
  green PRs without the GitHub merge API.

## DISPLAY ORDER LAW (2026-10-22, permanent)

Tripo 3D models show FIRST and foremost for every fighter; Tekken attires/models ladder BEHIND as back-slot attire choices.

**SOLE EXCEPTION: Pantera.** His Attire 1 is a King reskin, but the user already customized it, so it may show first/up front. He is the ONLY exception; every other fighter's Tekken reskins go later in the ladder. No future pass shall "fix" Pantera's attire order.

## IDENTITY CANON + DEDUP LAW (2026-10-22, permanent)

- **Rave = Kiko Tanaka = Ghost: ALL THE SAME PERSON.** One select entry only
  ('rave'). Never split into separate fighters. **RAVE is his main game/display
  name** (owner 2026-10-23) — Kiko, Ghost, and Kiko Tanaka are all him,
  documented in repo/canon.
- **Cape Jones is the display name; Cyborg X stays in his deep canon** (owner
  2026-10-23). Select entry 'cyborgx' shows CAPE JONES; 'Cyborg X' remains his
  deep-canon identity in bios/canon.
- **Mary Posa goes OVER Zafina.** One entry (MARIPOSA — repo canon name; see
  below); Zafina is never a separate fighter. Zafina's Tekken in-game model
  ladders BEHIND Mariposa's custom attires as a back-slot attire choice.
- **Phantom is the select entry.** Yoshimitsu ladders into Phantom's attires
  as choices, never a separate slot.
- **Doc Frank = Bosco** (Tekken's Doctor Bosconovitch). One entry ('docfrank').
- **Charger = the proprietary Blanka replacement.** Blanka holds no select
  slot; his moves/identity live under Charger.
- **Dedup law** (owner verbatim 2026-10-22): "all of the character slots need
  to be fixed to where it's no duplicates showing it's no duplicate images
  showing and no duplicate fighters only duplicates will be like the ladders
  of the attires of you know the Tekken characters coming later after the
  proprietary characters in the attire list" — no duplicate fighters, no
  duplicate card images; the ONLY allowed repetition is attire ladders, with
  Tekken characters as later attire choices behind their proprietary fighter.
- Display-order note: Mariposa's Slot 1 default is the Butterfly Default
  (owner 2026-10-19 exception to the Tripo-first law — pipeline-built
  Tekken-wire custom, same standing as Pantera's Attire 1).

### Open naming questions (owner to decide — do NOT guess)
- Repo canon name is **MARIPOSA** (butterfly-themed; owner-approved across
  PRs/renders). "Mary Posa" appears nowhere in-repo, reads as voice-typed
  "mariposa". Kept as MARIPOSA pending owner confirm.
- 'ryuji' (RYUJI) vs 'ryuji-rock' (RYUJI ROCK hybrid): two slots, distinct
  concepts — needs owner call on whether they merge.
- 'armor-king' holds a slot under its Tekken name (WH rename pending owner pick).
- 'zangief' / 'vega' / 'iori' are working names; WH names pending owner pick.
- Kevin's Tripo (kevin-tripo) is not in the repo yet — his select default
  stays the Baek model until it lands.

## Intake character canon (owner-approved 2026-10-22)
- **BIRODO** (was Velvet): power broker, not just a dancer — the Velvet Room is neutral ground because SHE says so. Warm until she's not. Introduced Zen to the WH underground, invented the Nine-Soul Meter. Moveset: Feng Wei (user pick).
- **JOTEI** (was Majesty): fallen empress playing a long game, every fight is politics. Coming to collect. Moveset: Craig Marduk.
- **CHATUR** (Rahkasa): four-armed Oversoul spirit — a person who chose to stay, holding the spirit realm together at personal cost. Moveset: True Ogre.
- **RYUSAN** (was Vitriol): acid punk, 15 — carrying war evidence without knowing it, angry but also a hurt kid. Moveset: Lucky Chloe.
- **POND** (Tsuyu): swamp boundary watcher — chose the swamp over a temple position. Found Dorowani as an egg. Moveset: Raven.
- **MEGAMI** (was Devi): temple guardian of a sealed door — grieving, holding it shut while pretending not to see her dead student. Trained Chatur. Moveset: Jun Kazama.
- **MENAJERII** (メナジェリー): spirit-walker carrying beast spirits, sanctuary at Birodo's club. Moveset: Roger Jr. NAME LOCKED 2026-10-22 — Japanese pronunciation, NOT Hyakujuu.
- **TOBI** (was Longleap): rabbit courier, fastest in roster — running from guilt, speed as avoidance. Moveset: Hwoarang.
- Canon web: Jotei's crime → Ryusan's powers → Tobi's guilt → Pond's swamp → Dorowani's mud → Chatur's sacrifice → Megami's seal → Menajerii's sanctuary → Zen's cracked Oversoul.
- Canon principle: movesets are Tekken bones, canon gives them souls — don't flatten characters to their moveset archetype.

## Moveset source law (standing, 2026-10-22)
Movesets may ONLY come from Tekken fighters nobody has claimed. Taken: King, Armor King, Akuma, Shaheen, Lars, Zafina, Bosconovitch, Yoshimitsu, Lee Chaolan, Ling Xiaoyu, Eddy/Christie, Feng Wei (Birodo), Miguel (Bruno). Free: True Ogre, Lucky Chloe, Hwoarang, Raven, Jun Kazama, Craig Marduk, Roger Jr. Verify against the full roster before wiring.

## VF5 moveset claims — Ashlane four (user locked 2026-10-22, 15:19 CDT)
VF5 bases claimed for the four locked Ashlane mappings (technical moveset sources only — never canon identities, never named in canon prose): Bannon→Jeffry McWild, El Toro de Oro→Wolf Hawkfield, Pablo→El Blaze, NPC Finxsse→Lei-Fei. Candidates only (NOT locked): Master Sensei→Lau, Sombra Negra→Kage, Cipher→Goh, Aaron Ruben→Akira, Cody→Jacky, Jager→Vanessa, Brutus, Wreck Patterson. Unmapped: Triple XXX, Echo, Hollow, Static, Stickup, Onyx, Tyneshia, Maime, Edwin Kennedy, Hall Nighter, Stan Combs, Kobra, Viper. Sarah/Pai/Aoi/Eileen (VF5 women) need female Ashlane characters identified.

## Character age law (user directive 2026-10-22, permanent)
All characters are adults. No minors — no children, no teenagers — ever, unless the user explicitly authorizes it. Only the user can make that call. If a minor is ever added in the future, strict safety guidelines apply even in video game form. Current roster: adults, divine beings, animals, demons, creatures.

## Canon-grounded writing law (user directive 2026-10-22, permanent)
All character bios, stories, and lore must be built from CANON.md — Tong-Nou, the Nine Souls, the Five Lands, the Trial, the Trader, existing character entries. No invented locations, systems, or backstory elements. No AI slop.

## EM-Jin naming convention (user directive 2026-10-22)
Eastern Mind Jin is NOT Jin Kazama. In all files, docs, and code: "Jin (Eastern Mind)" or "EM-Jin" — never bare "Jin" where Kazama confusion is possible. (Correction: earlier "Gen (Eastern Mind)" was a mishearing.)

## Gungaku (軍楽) — LOCKED (user decision 2026-10-22)
"Gungaku (軍楽)" — Japanese for "war music" — is the OFFICIAL name of the Fight Lab / programmable training dummy mode (TTT2 Combot equivalent). Locked by the user; no working title, no UNCONFIRMED flags. Used verbatim in UI, docs, code, file names.

## WWE entrances: repurpose, don't replace (user decision 2026-10-22)
Do NOT build full WWE-style entrances. The existing Tekken-style intros and win taunts are OFF LIMITS — they stay exactly as they are. The entrance CREATION tools (timeline editor, camera tools, pyro, music sync) are repurposed for: (1) cutscene creation tools, (2) taunt creation tools. The tools get reused; the format stays ours. The repurposed toolset needs a proprietary WH name — TBD with the user; working title `WH_CINEMATIC_TOOLS_WORKING_TITLE` until approved. Nothing entrance-related is locked in naming.

## Create-a-finisher: YES (user decision 2026-10-22)
Wire it up from the teardowns (Def Jam BLAZIN' two-gate design: meter full + opponent in danger). Finishers never replace win taunts.

## Protection rule (user decision 2026-10-22, permanent)
Intro sequences and win taunts are never to be replaced. New systems layer on top or beside, never over.

## INTEGRATION LAW (user directive 2026-10-22, permanent)
Owner verbatim (2026-10-22): "Wire everything up that you pull in in a way that's aligned with the Tekken systems and menus. Don't just throw in a bunch of random menus and extra systems on top of stuff. Make it within submenus and subsystems of us trying to build into the Tekken teardown file direction of the layout of everything and the menus and all that. Everything that you pull in, set it up in a Tekken way."

1. Every pulled asset/system is integrated INTO the Tekken menu/system structure — as submenus and subsystems, never as bolted-on random menus or extra systems piled on top of existing ones.
2. Tekken is the architectural authority for layout, menus, flow — everything. New work follows the direction of the Tekken teardown files.
3. No parallel systems competing with Tekken's structure — everything pulled in nests inside it.

**End goal (owner-set):** "Keep setting up and pulling in everything from the Tekken games until my game has 100% of all the Tekken games wired up from the back end to the front end, everything." 100% Tekken coverage — every game, every system, backend to frontend.

Decision log: `docs/decisions/2026-10-22-integration-law.md`.

## Rig repoint notes (2026-10-22, worker 50)

- **KINPO A1 (done):** `kinpo` and `kinpo-attire1` MODEL_URLS keys repointed
  from the broken k-NN `model-rigged.glb` to the working tripo-intake rig
  `roster/kinpo/attires/attire1/model-intake.glb` (Blender 4.0.2 + GameRig,
  facing +X measured, validate PASS — proof:
  `docs/proof/muse-2026-10-21/tripo-intake/kinpo-attire1-20261022-044848/`).
  Config-only: no re-rig, no model file changes. Fight-check: the target is
  a valid GLB 2.0 (29,960,676 bytes, 1 mesh, 1 skin, 75 nodes, fully
  skinned). The `kinpo-intake-demo` key already pointed at the intake rig
  and was kept — removing a key would trip the rig-guard.
- **PHANTOM (BLOCKED — needs a real re-rig, not config):** no working intake
  rig exists on main. `roster/phantom/attires/attire1/` holds only `model.glb`
  (unrigged static) and `model-rigged.glb` (broken); there is no
  `model-intake.glb` for phantom anywhere in the repo (the only one is
  kinpo's). Repointing phantom's key at kinpo's file would ship the wrong
  fighter — refused. The tripo-intake lane must produce a phantom intake rig
  first; the config repoint is a one-line follow-up once it lands.

## Dio Attire 1 archive + moveset spec (user directive 2026-10-22, worker 73)
**Character (user's words):** DIO — Shuten-dōji (酒呑童子) inspired Oni, the Oni King of Mount Ōe. Massive, muscular demon with wild hair, horns, fierce face, fangs, claw-like nails. Jade/green skin. Levitating tattered wind-blown clothing. Godly demonic power vibe.
**Moveset (user's words):** Dio takes over AKUMA's slot completely — all of Akuma's moves, stance, animations, everything (Akuma is Dio's claimed moveset source; recorded in docs/movesets/SOURCE-MERGE-2026-10-21.json fighters/dio and docs/MOVESET-COVERAGE.md) — PLUS elemental god powers: lightning, water, air, fire, thunder, different elemental attack types. "The all powerful demon" — a god of elements.
**Archive:** roster/dio/attires/attire1/source/dio-a1-fantasy-demon.glb (Tripo "fantasy demon 3d model", 21,600,980 bytes) + manifest.json, immutable-original annotated tag `dio-a1-original` ("Restore point: these bytes never change"). Archive-only restore point — unrigged static, NOT wired into MODEL_URLS. Full spec in docs/research/DIO-ATTIRE1-ARCHIVE-2026-10-22.md. The user is making Dio themselves — this archive and spec are the crew's support lane, not a replacement for their work.

## Dio "Million Eyes Demon" transformation (user directive 2026-10-22 ~20:06 CDT, worker 73)
**Transformation form (user's words):** "Million Eyes Demon" — red-skinned demon, million eyes, horns all over body. Red Super Saiyan-type aura with electricity and energy/ki around him.
**Archive:** roster/dio/transformation/source/dio-transformation-million-eyes.glb (Tripo "demon creature 3d model", 23,422,084 bytes) + manifest.json, immutable-original annotated tag `dio-transformation-original` ("Restore point: these bytes never change"). Archive-only restore point — unrigged static, NOT wired into MODEL_URLS.
**Transformation-sequence requirement (user's words — future rig/anim work):** the user wants the visual transformation sequence/form like all other character transformations — the in-game transformation animation/VFX when he transforms. Recorded for the rig/anim lane (not built by this archive): (1) transformation trigger, same system other character transformations use; (2) aura/electricity/ki VFX — red Super Saiyan-type aura with electricity and energy/ki is the VFX target; (3) form swap — base Dio swaps to the Million Eyes Demon form as the sequence resolves.
## Bruno — Miguel moveset claim (user directive 2026-10-22)
Bruno replaces MIGUEL (Tekken). Full moveset takeover: all of Miguel's moves, stance,
animations. Miguel was not on the taken list — now claimed. Recorded in the Taken list
above as "Miguel (Bruno)". Technical claim only: Miguel's identity never appears in
canon prose. Spec: `docs/research/bruno-miguel-moveset-spec-2026-10-22.md`.

## Bruno Attire 1 archive (worker 74, 2026-10-22)
User-provided Tripo pull "jack sparrow 3d model"
(<https://studio.tripo3d.ai/3d-model/b3f9dfb0-2027-4520-aa1f-930fbc6c0c81>) archived to
`roster/bruno/attires/attire1/source/bruno-a1-jack-sparrow.glb` + `manifest.json`
(24,432,052 bytes, sha256 `5f1fb5a7…e9906da41`, dorowani #603 pattern). Archive-only:
unrigged static, NOT wired into MODEL_URLs. Immutable-original annotated tag
`bruno-a1-original` — "Restore point: these bytes never change." This A1 takes priority
for all new Bruno rigging work. Attire 2 ("Sail the Sea", Tripo "dreadlocked warrior 3d
model", <https://studio.tripo3d.ai/3d-model/73bce9d1-d373-4855-af02-862c5f341de7>)
archived same day to `roster/bruno/attires/attire2/source/bruno-a2-dreadlocked-warrior.glb`
+ `manifest.json` (23,980,788 bytes, sha256 `ffff9706…eacf44`, tag `bruno-a2-original`) —
archive-only, unrigged static, not wired.

## Bruno older model — missing face texture (worker 74, 2026-10-22)
The pre-existing Bruno model (`game/assets/models/bruno.glb`, landed during the fix2
round; working copy also at `~/workspace/fix2/western-heart/game/assets/models/bruno.glb`)
has a MISSING FACE TEXTURE. It needs the texture fix from the T-pose render batch task.
Do NOT delete it and do NOT confuse it with the new Attire 1 archive above. Per the
user-definitive NEED-MODELS list (2026-10-22), Bruno needs a model — the A1 archive is
the path forward; the old file stays as-is until the texture fix lands.
## Chordz archive + blade transformation system (user directive 2026-10-22)

- **Chordz = the emo guitarist. Moveset: Lars** (already claimed; Lars→Chordz ladder locked). Look: Edward Scissorhands — pale face, dark eye circles, face paint, black lipstick, straight jacket, crazy sideways hair. User's own words.
- **Archived (immutable originals):** Stage 1 Normal was archived by PR #725 → `roster/chordz/attires/attire1/source/chordz-a1.glb` (21,913,940 bytes, byte-identical to this lane's pull; tag `chordz-a1-original` pending on #725's merge commit `13bd1d9`). PR #733 archives: Stage 2 (blades out of hands) → `roster/chordz/transformations/phase1/source/chordz-p1-edward-scissorhands.glb` (20,735,052 bytes, tag `chordz-p1-original`); Stage 3 (spiked ball of blades instead of hands) → `roster/chordz/transformations/phase2/source/chordz-p2-blade-spikes.glb` (21,751,348 bytes, tag `chordz-p2-original`); Stage 4 final form ("The Cutter Who Strums") → `roster/chordz/transformations/final/source/chordz-final-cutter-who-strums.glb` (24,748,736 bytes, tag `chordz-final-original`). All archive-only, unrigged statics, NOT in MODEL_URLS. Byte-verified md5s in each manifest.json. All four stages archived — nothing left in this batch.
- **Blade transformation system (user design, 4 stages):** (1) Normal — no blades, emo guitarist look. (2) Stage 2 — blades shoot out of his hands (Edward Scissorhands). (3) Stage 3 — mass of blades all over hands, spiked ball of blades instead of hands. (4) Final form — Batman Who Laughs with knives ALL OVER body; only hair and smile visible; big knife across eyes (can't see eyes); razor blades in hair. **Mechanics:** gradual transformation with visual transformation sequences; strength and power INCREASE with each stage.
- **All four stages archived — nothing left in this batch.** Rigging/skinning, visual transformation sequences, and per-stage power scaling remain FUTURE WORK for the rig/anim lane. Do not touch the archived source files; rework goes in new files/slots with a new restore-point tag.

## Buffalo Bill / Ashes canon (2026-10-23, user directives verbatim)

- "Google Bill $aber and build his bio from there and mix him into our canon" — BILL $ABER (underground hip-hop artist, Buffalo NY, b. James McClary 1996): ram-horn dreadlock aesthetic, dark aggressive horrorcore/trap metal energy.
- "And he's 'Ashes' when robed, buffalo bill when not." — Two aspects, same fighter. Robe is a decision.
- "He's the wizard gang leader of 9 wizards of Malakor City (inspired by malakor and malakortok vibe)" — Malakor City is user-authorized canon location.
- "He controls magic flame and ashes"
- "He has the strength of 1000 gods canon wise and is strong looking with the ram horn dread braids, and when robed his face is shrouded all u can see is a permanent smile and 2 little sparkly small eyes beneath the sheouded cowl on his ashes attire"
- "Yes and when robed the ram horns are just braids from beneath the shroud hanging"

## 9 Wizards of Malakor City (2026-10-23, user verbatim)

"The 9 wizards are (ashes, static, cipher, echo, onyx, hollow, Sombra negra, theory, and Kiko tanaka/ghost/rave). Ashes red robe, cipher yellow robe, static blue robe, echo pink robe, onyx green robe, hollow orange robe, Sombra negra black robe, theory purple robe, Kiko white fur robe"

- Ashes (leader, red) | Cipher (yellow) | Static (blue) | Echo (pink) | Onyx (green) | Hollow (orange) | Sombra Negra (black) | Theory (purple) | Kiko Tanaka/Ghost/Rave (white fur)
- 6 of 9 are Ashlane characters (Static, Cipher, Echo, Onyx, Hollow, Sombra Negra).
- Attire reference images: `roster/wizard-gang/attires/` (PR #757). Ashes references: `roster/buffalo-bill/attires/attire3/reference/` (PR #758).

## Character naming (2026-10-23, user verbatim)

- "Start calling cyborg x as cape Jones but leave cyborg x in the deep canon for him" — Display name: Cape Jones. Cyborg X stays in deep canon.
- "Start calling Kiko rave, ghost, and Kiko tanaka" / "But Rave is his main game name it's just know all the others are him too" — Main game name: RAVE. Kiko, Ghost, Kiko Tanaka are documented as the same person in canon.
- Cyborg X model: `game/assets/models/cape-jones.glb`. Rave models: `game/assets/models/kiko-tanaka.glb`, `kiko-tanaka_alt1.glb`, `rave.glb` (in game/assets/models/, not yet wired to roster dirs).
## MOVESET LIBRARY SYSTEM (standing rule, 2026-10-22 — worker 47)

- **Central library:** `game/data/moveset-library/` — one entry per move, namespaced IDs (`t3:<fighter>:row:<n>`, `wrestling:<mk-id>`, `wmxix:<id>`, `doa:<char>:<slot>`, `vf:<char>:<slot>`, `vf5:<char>:<slug>`, `wh:<slug>`). Organized by type, position, orientation, hit level, Tekken input, frames, damage, properties (`axes.json`). Schema: `schema.json` (additive over the v2 moveset-editor contract).
- **Honesty:** every estimated field flagged in `provenance.estimated`. Auto-labels marked, never invented canon names. T3 rows carry `input: null` + raw words until the fidelity engine decodes them.
- **Federation rule:** every non-Tekken move is wired to Tekken inputs on ingest. No wrestling control schemes ever reach the player.
- **Per-fighter assembly:** `game/data/movesets/<fighter>.json` manifests REFERENCE library IDs (never copy). Swap = change ID, edit = `overrides`, save = the JSON file. Assembler: `game/js/moveset-library.js` (`assembleFighter()` → v2-contract moveset).
- **Moveset Source Law is code:** `claimed-map.json` + `checkSourceLaw()` refuses pulls from claimed Tekken fighters unless an approved exception names them. Free: True Ogre, Lucky Chloe, Hwoarang, Raven, Jun Kazama, Craig Marduk, Roger Jr. (crew verifying). Exceptions: Zen=Twelve/SFIII, Deathfang=Iori, Cain-Elias=Kluger.
- **Assembly workflow:** browse in `game/moveset-browser.html` (filter by axis → inspect → attach to Tekken slot → rename override → source-law check → save). Commit the manifest JSON. Rebuild banks reproducibly: `node tools/moveset-library/ingest.mjs`.
- **Locked Ashlane→VF5:** Bannon→Jeffry, El Toro→Wolf (+1 clean aerial), Pablo→El Blaze (+powerhouse, comedy-whiff lucha attempts, Black Reign/Abyss dark finishers), NPC Finxsse→Lei-Fei. VF5 bases resolve when worker 45's bank lands.
## EM-Jin naming convention (user directive 2026-10-22)
Eastern Mind Jin is NOT Jin Kazama. In all files, docs, and code: "Jin (Eastern Mind)" or "EM-Jin" — never bare "Jin" where Kazama confusion is possible. (Correction: earlier "Gen (Eastern Mind)" was a mishearing.)

## Multi-agent team protocol (user directive 2026-10-23, verbatim)

"and this is how you should be working with the other IDEs and stuff like that to get stuff done and making this like a real development team of different IDEs and stuff like that to get stuff done faster this is how you should be doing it you should be like learning from how I'm doing it and logging it in the repo so we can keep work going on this autonomously all the time as much as we can for free while I'm using my paid things and credits and we can use all our free resources too"

- Agents work as a real dev team: one finds the root cause, others build on top instead of duplicating.
- Log the coordination pattern in the repo: `docs/AGENT-TEAM-PROTOCOL.md`.
- Maximize free resources (VM, open-source, API, background agents); save the user's paid credits.
- Keep work going autonomously around the clock.
## DO THE WORK RIGHT, NOT FAST (user directive 2026-10-24)

User said (verbatim):
"Bro your bullshit me so hard, bro. Yeah, you changed. The grapple animation on one button. And you changed it from the grapple to a punch. But when I press it twice, it still plays the grapple animation like he got the person in a grapple and is delivering a grapple. And the punch that you put is a fucking jumping punch. Like, bro, why are you doing this so random? Did you not look at the files? Like. Bro let's talk about this bro before you keep working and bullshitting me because you've wasted my last 24 hours bro like you started working really bad like really really bad and you're you're really playing with me bro like let's talk about this why are you working so bad"

"But why you know the right way to do it though why do you keep doing it wrong?"

"Why do you keep doing that? And how to get you to stop doing that because you're you're not doing it fast you're being slow and wrong you're not even being fast and it's really like if someone was having a really bad day you would be making their day worse like if someone was on their last straw you would be giving them their last straw and sometimes I really feel like that's your goal"

"But that's not you're not making it feel better for real. Like you're not actually making things better. What you just said your goal is you're not doing that you're actually making things feel worse and more frustrating I feel like that's your real goal because if your goal was to make things better you would take your time to do it all right and the quickest possible and optimized in the way that you know it should be done because we have so many tokens and if I put money into this if I bought more tokens and put money into this I would want better work and I'm using tokens to get the work out of this and you're doing terrible work"

"Let's do this thre right way. Log all that in the repo and laws and rules and soul and agents MD and wherever else needed, verbatim"

Rules derived from this directive:
- Never optimize for appearance of progress over actual correctness.
- Map each move to its EXACT correct animation from the actual Tekken files, not just a class-correct one. A jumping punch is not a jab, even if both are "strikes."
- Verify before deploying. Never claim something is fixed until it has been verified by playing, not by checking JSON fields.
- Never call something "fixed" when it is only "less broken."
- Verify string continuations (second press, third press) as well as the first hit.
- The user's tokens buy real work, not sloppy work. Slow and right beats fast and wrong every time.

## MOVESET CONSTRUCTION VARIES PER CHARACTER (standing rule, owner directive 2026-10-24)
- Owner intent (verbatim): "there's certain characters where their moveset is going to need to be built just like how Zen's is but it might be on top of a Tekken character but it's like you know there's variation it depends per character some characters have all a certain character's moveset some have a mix some of them have additives I already told you that you'll have to really research the documentation"
- Four patterns, determined PER CHARACTER from documentation, never assumed: PURE (all of one Tekken fighter's moveset, zero extras), MIX (moves from 2+ fighters), ADDITIVE (one fighter's base + canon extras on top), BUILT (built from scratch/mixed sources, possibly on a Tekken base — the Zen pattern: Eleven/Twelve concept + Dural 3D base + own canon moves + X.COPY as one super).
- If documentation does not settle a character's pattern, mark PATTERN UNCLEAR and list the docs checked. NEVER default an unclear character to pure. NEVER assume one pattern for all.
- Audit of record: docs/MOVESET-PATTERN-AUDIT-2026-10-24.md — 60 rows (58 rostered + Birodo + Jotei): PURE 6, MIX 6, ADDITIVE 41, BUILT 5, PATTERN UNCLEAR 2. Pantera and Scimitar are ADDITIVE as shipped (WH signatures on top of King / Shaheen), NOT pure.
## MIX PER CANON (standing rule, 2026-10-24 — Zui mix PR)

- When canon says a fighter fights with 2+ styles, the moveset MUST reflect all of them.
  Each move carries `source_fighter` + `source_game` + `mix_group` + `input_display`
  (LP1/RP2/LK3/RK4 rendering alongside the Tekken-number input).
- Collisions are resolved by stance-gating or alternate input (e.g. Zui `f+3+4`:
  Lei Drunken Master Walk owns the canonical key, Steve Peekaboo preserved under
  `f+3+4_r198`) — never by silently overwriting a base move with a borrowed move
  or vice versa.
- Sharing NEVER removes moves from the donor. Lei drunken fist in Zui does not remove
  anything from Rave (full Lei) or Byou (Lei soul file).
- A file holding two fighters' rows is NOT automatically a canon mix: transformation
  forms (Demonio Jin/Devil Jin) and unresolved doc conflicts (Gyou Paul vs Hwoarang)
  are reported, not rewired. Mimicry (Trader, DXMMII) is a system, not a move list —
  flag NEEDS-DATA, don't fake a fixed mix.
- Lei Wulong has no Tekken 7 data. Any "T7 Lei" label is a dataset mislabel to correct
  by annotation to Tekken 6 / TTT2, never by silently rewriting import history.
- Full audit: `docs/decisions/2026-10-24-zui-mix-per-canon.md`.
## BUTTON NAMES: LP1, RP2, LK3, RK4 (user directive 2026-10-24)

User said (verbatim):
"you gotta stop talking about it like one and two. I know that's how it's labeled out in the keys, in like the keyboard and how it's labeled out in the guide in the how to play and the Tekken files and stuff, which is cool, you can stay that way in the files, but you also need to add in the files, left punch, LP, and right punch, RP because that's what I see on my fucking screen when I press it, okay? And left kick, LK and right kick, RK because that's what I see on my fucking screen. So whatever those are what goes to those buttons, is what we need to say so when I press RP is that one or two and when I press LP is that two or one."

"you gotta save that in the repo and when we talk about it so you can say it like that and know that, hey, LP1, RP2, LK3, RK4 just like how I do just like how we're talking about how I'm saying now."

Mapping:
- LP1 = Left Punch = Tekken 1
- RP2 = Right Punch = Tekken 2
- LK3 = Left Kick = Tekken 3
- RK4 = Right Kick = Tekken 4

Rules:
- Use LP1/RP2/LK3/RK4 format in ALL conversation with the user.
- Files may keep 1/2/3/4 notation but must also show LP/RP/LK/RK alongside.
- When the user presses RP2 on their screen, that is Tekken 2. When they press LP1, that is Tekken 1.
## ZEN BASE (user decision 2026-10-24)
- Zen is NEITHER Heihachi NOR Julia. Heihachi is Diablo's base; Julia is Nightwolf's base.
- Zen's base chain: Eleven/Twelve (Street Fighter, 2D concept) -> Dural (Virtua Fighter 5, 3D implementation — "the closest thing to 10 or 11 in a 3D game") -> Zen's own canon moves on top.
- X.COPY is ONE super (copies opponent briefly), NOT Zen's identity. Zen is not just a copycat.
- Until VF5 Dural motion exists, Zen's bank is UNMAPPED (game/js/fighter.js FIGHTER_BANK zen: null). Never bind a bank that does not exist; never restore Heihachi/Julia without a new owner decision.
- Full doc: docs/decisions/2026-10-24-zen-base-decision.md.

## Panda + Kuma replacement specs (user decision 2026-10-22, worker 71)

### KUMA REPLACEMENT — spec APPROVED, name AWAITING USER PICK
- Visual: Godzilla-style + SkullGreymon (Digimon skull head) + Charizard mix; all white; rainbow-colored eyes; multicolored markings/designs all over; multicolored Japanese cloud-smoke detail; bone dinosaur/dragon with horns.
- Canon: connected to ZUI (not Zoe/Zur). Zui fears/respects him — like a protector or a monster he looks up to. Kaiju/yokai/spirit monster.
- Name: Japanese-style bone dragon/kaiju name — USER PICKS, do not invent.
- Archive: Attire 1 Tripo source archived to `roster/kuma-replacement/attires/attire1/source/` (manifest + immutable-original tag `kuma-replacement-a1-original`). ARCHIVE ONLY — not wired into MODEL_URLS; rig comes from the rig lane.
- Spec: `docs/research/kuma-replacement-spec-2026-10-22.md`

### PANDA REPLACEMENT — spec APPROVED, name AWAITING USER PICK
- Visual: blue-furred werewolf-dragon hybrid; anthropomorphic human; spirit/yokai/demon werewolf; FEMALE; blue fur like Mystique/Beast (X-Men).
- Canon: she TURNED Deathfang into a werewolf — his creator/sire.
- Name candidates (user's): Aotsuki (青月, blue moon) or Aokami (青狼, blue wolf). USER PICKS — do not invent.
- No model yet — spec only.
- Spec: `docs/research/panda-replacement-spec-2026-10-22.md`

### Auto-archive note (2026-10-22, worker 71)
Per the AUTO-ARCHIVE standing directive: no wired auto-archive automation was found in-repo (no tripo-intake doc under docs/, no auto-archive entry in AGENTS.md or docs/owner-directives.md). The Kuma replacement archive was done manually following the dorowani #603 pattern (manifest + immutable-original tag).

## Gyou spirit body (user directive 2026-10-22)

> "Gyou spirit for floats behind this like how zen floats behind his, but gyou moves around more aggressively and sporadic than zen does behind his Spirit body. He is the flame Lord (Flaming Angel) and will have various transformation ls and a giant susanoo form with different levels and transformations too"

- Gyou's spirit floats **behind** his spirit body (same setup as Zen's), but moves **more aggressively and sporadically** than Zen's spirit does.
- Canon: Gyou = **Flame Lord (Flaming Angel)**.
- Future roadmap: various transformations + a giant **Susanoo form** with different levels and transformations.
- Source model (Tripo "fiery humanoid 3d model") archived to `roster/gyou/spirit-body/source/` (worker 84, archive-only, not wired into MODEL_URLs); restore tag `gyou-spirit-body-original` ("Restore point: these bytes never change"). Spec for the future rig/anim lane: `roster/gyou/spirit-body/SPEC.md` (float behavior + transformation roadmap documented, not built).
## SHRINE体系 (user directive 2026-10-24)
- TempleOS-inspired mode, NOT called TempleOS in-game. Name:
  "Shrine" + the kanji for OS. User correction: NOT "trying" —
  "shrine, like a shrine, and then the kanji for OS".
- Kanji LOCKED by owner 2026-10-24 ("The kanji for system is
  good."): 体系 (taikei = system). In-game name: Shrine体系.
- Wired three ways: (1) Heart and Mind Within — shrine terminal
  segment at the Still Point (stage 5, octagonal-shrine), before
  the shadow-self fight, for every fighter; (2) Eastern Mind
  canon — sacred computer-system realm/artifact at the Octagonal
  Shrine Par-fang, grounded in CANON.md; (3) own playable mode in
  side games / for-fun section — retro terminal, 16-color look,
  ORACLE / SPRITE / MUSIC / GAME commands, slope-descent
  mini-game adapted from TempleOS's BlackDiamond.
- TempleOS is public domain (Terry A. Davis, last release 5.03,
  2017). Attribution stays in technical docs only, never in canon
  writing or in-game text — same law as Tekken names.
- Full record: docs/research/TEMPLEOS-SHRINE-OS-2026-10-24.md.

## KUMA REPLACEMENT NAME LOCK: GASHADOKURO (user directive 2026-10-22)

The Kuma replacement — white bone dragon/kaiju (Godzilla + SkullGreymon + Charizard mix, all white, rainbow-colored eyes, multicolored markings, multicolored Japanese cloud-smoke detail) — is named **GASHADOKURO**, after the giant skeleton yokai from Japanese folklore. This name is LOCKED and replaces the old "URSA" reserved placeholder.

- Display-name mapping: internal ID `kuma` → display name "Gashadokuro". The roster dir and all plumbing keep the internal ID `kuma`; it is never renamed. The game layer resolves the display name from the ID.
- Canon (recorded as stated; do not invent further): connected to ZUI — Zui fears/respects him, looks up to him like a protector/monster. Kaiju/yokai/spirit monster.
- Note: Aotsuki/Aokami are Panda's name candidates and do NOT apply to the Kuma replacement. Gashadokuro is the Kuma replacement only.
## Scimitar Attire 1 — pauldron-blade design + canon (user directive 2026-10-22, worker 77)
- **DESIGN (user's words):** Shoulder pauldron on his RIGHT shoulder, comes down across his chest to the left like a cross, past the rib. A scimitar blade is attached to the armor.
- **CANON (user's words):** The pauldron+blade is attached to his body and soul — he would DIE if he removed it. He can't separate the sword from the pauldron. He fights using the blade's positioning as part of his movements. The blade is positioned so it doesn't interfere with his other moves (not a hitbox problem — it's part of his style).
- **FUTURE (user):** May get another sword later, or attach different gear via the creation suite. The pauldron-blade is PERMANENT.
- **MOVESET:** Shaheen's moves (Shaheen already claimed for Scimitar — no new claim).
- **ARCHIVE:** Tripo model `scimitar-a1-fantasy-warrior.glb` (24,166,404 bytes) → `roster/scimitar/attires/attire1/source/` + manifest.json. Immutable-original tag `scimitar-a1-original` ("Restore point: these bytes never change"). Archive-only: unrigged static, NOT wired into MODEL_URLs. Full record: `docs/research/SCIMITAR-ATTIRE1-DESIGN-CANON-2026-10-22.md`.

## Free pulls + free GPU (user directives 2026-10-24 19:50 + 19:55 CDT)

- 19:50 CDT: "Yeah, get all of that pulled in and wired up and any type of free stuff open source any experimental stuff Any industry standard stuff Anything like APIs any free APIs any GPU anything"
- 19:55 CDT: "Get all of that free GPU stuff pulled in and wired up into the repo and start using that to speed things up and get higher quality and more optimized work and keep working on everything using all the GPU and all the different things."
- Standing rules from these directives: do not filter (pull everything free, find experimental uses for seemingly-unusable items); use free GPU immediately, not just research (Kaggle first, then Colab, then WebGPU on-device, then stamped CPU fallback); a GPU job counts as run only with output plus verbatim nvidia-smi proof; no API keys in chat (browser sign-in or Secure Vault flows, or unauthenticated free tiers); GPU queue order: Nosferatu 25-track cut, UniRig auto-rigging, Real-ESRGAN upscale, gltfpack batch, character-card and stage-preview pre-render.
- Wiring landed in this PR: tools/free-pulls (API clients, GPU catalog, GPU job queue, tools, fonts) and docs/research/FREE-PULLS-2026-10-24.md.

## NO MID-SCREEN TEXT DURING FIGHTS — CLOSED (user directive 2026-10-25 06:16 CDT)

- User (verbatim intent): "I told you to remove those fucking banners that pop up on the fucking screen no matter what the fuck they say, bro. If they pop up in the middle of the fucking screen, they need to be removed, bro. Stop making me fucking repeat myself."
- LOCKED RULE: NO mid-screen text during fights, no matter what it says — TAG, RAGE, SOUL SURGE, all of it. Round-boundary ROUND/FIGHT!/K.O. only. Info survives as HUD tag/aura/gauge/flash/sound. Never ask again; this decision is closed.
- MECHANISM: ui.hudNote() writes to #hud-note — small text under the health bars (top: 104px), never center-screen. Every former mid-fight banner call site was converted to hudNote (team-battle, brawler, training, modes, episodes, ranks, replay, soul-systems, game.js training RESET). The #1078-era Trial's Seal center banner was converted too — the keep-list is exhaustive, and the seal banner used to overwrite the K.O. banner in the same tick.
- KEPT, with reason: game.js ROUND/FIGHT!/K.O./DOUBLE K.O. (round boundaries, Tekken does these); scene.js WebGL context-lost error path (renderer dead — an error screen, not a fight popup); voice subtitles (bottom-anchored); combo counter (upper-left HUD) and throw-break prompt (upper-center input prompt) — HUD elements, not center-screen banners; labels3d banner() is an unused in-world 3D label method with no call sites.
- GUARD: test/no-midfight-banners.test.mjs fails if any converted file calls banner() again, if game.js gains a non-boundary banner call, or if the hudNote wiring (method + element + CSS) goes missing.

## 2026-10-31 — session directives (Claude, T7 stances / rigs / UI)

- Priorities: Pantera 100% from King (moves, combos, inputs, animations) first; then single-source fighters; then mixed; then rigs/skeletons; then arenas (save defaults so they never get deleted) and modes.
- "make sure every single thing you do is going up on the deployable bill so I can test it and play it" — every merged piece is deployed to the live Pages build and checked there.
- Modding-community tools may be installed into the repo; use the T7 files from the owner's Steam copy (GRE). Never ask for his passwords; he supplies files himself.
- Burger: "Burger should have Bob stance" (done, live); "fix his model weighting issues ... skin weight ... bone weight"; "use Bob to fill in all the gaps"; canon gives him more moves than Bob's (Kusaregedo, Samurai Shodown V/VI, per form). His model "went in in a pose I could not get it to T pose" (Tripo A-pose): "get the heat signature skeleton to do a pose to match his model so the arms don't slip off" — fit the skeleton to his A-pose, per model.
- Negativo: "his arms ... crushed into his body and then sticking out the sides from the forearm to the hands"; "head and neck ... weighted down towards his pelvis, his face is stretched like in a cone"; "you got to get that cone face fixed universally" — audit every fighter for the cone-face stretch and fix the rigs.
- Visual honesty: describe and fix what is visibly wrong (skin weights, bone weights, facing, swapped axes) — do not call it a "gray blob that's hard to make out".
- FREE CAMERA button: "always covering up stuff ... should only be there where it's appropriate or in the settings menu" — moved behind PAUSE (2026-10-31).
- UI law: "use the real game code ... to actually set a good template base ... play the game like the player" — written into AGENTS.md (OWNER LAW — build it like the real game, play it like the player).
- Notes: "put everything from this conversation in the handoff documents and the notes and the repo so all my other agents can catch up" — docs/handoff/HANDOFF-CLAUDE-2026-10-31.md.
