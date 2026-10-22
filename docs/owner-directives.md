# Owner Directives — M.Dogg's standing orders for Western Heart

Living document. Updated every time the owner sets a directive. Newest first.

## 2026-10-22


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
  ('rave'). Never split into separate fighters.
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
Movesets may ONLY come from Tekken fighters nobody has claimed. Taken: King, Armor King, Akuma, Shaheen, Lars, Zafina, Bosconovitch, Yoshimitsu, Lee Chaolan, Ling Xiaoyu, Eddy/Christie, Feng Wei (Birodo). Free: True Ogre, Lucky Chloe, Hwoarang, Raven, Jun Kazama, Craig Marduk, Roger Jr. Verify against the full roster before wiring.

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
