# Session Directives Consolidation — Owner-Locked (2026-10-22)

Consolidated record of this session's owner directives on modes, systems,
teardown priorities, audio, combat depth, and online. Each item below is an
owner directive; the standing-law versions live in
`docs/owner-directives.md` (2026-10-22 section). No gaps: everything the owner
asked for in this session is captured here or referenced.

## Core system name locks

- **Soul Urge — NAME LOCKED (2026-10-22).** Tekken 8's Heat system renamed
  proprietary to "Soul Urge". Pulled straight from the T8 files. All code,
  docs, UI, and canon references use "Soul Urge"; never "Heat".
- **Gungaku — NAME LOCKED (2026-10-22).** 軍楽 ("war music") — the fight lab /
  programmable training dummy mode, the WH equivalent of TTT2's Combot.
  Gungaku is its permanent name.
- **EM-Jin naming convention.** Eastern Mind Jin is NOT Jin Kazama. In all
  files, docs, and code: "Jin (Eastern Mind)" or "EM-Jin" — never bare "Jin"
  where Kazama confusion is possible.

## Rank ladder (owner-built 2026-10-22, 53 tiers)

Tekken formula: real terms at the bottom → real mythology in the middle →
WH cosmology at the top. **Rank names are DATA, never hardcoded** — new tiers
drop in freely. Tiers 52–53 are RESERVED and UNNAMED — invented only when a
player holds #51 long enough, Tekken-style (Tekken God → True → Prime →
Omega). Systems: offline rank battles, online ladders/leaderboards,
promotion/demotion.

Full list:
1. Lost Soul (placement)
2–10. 9th Kyu → 1st Kyu
11–13. 1st Dan → 3rd Dan
14–19. Brawler → Warrior → Marauder → Vindicator → Slayer → Warlord
20–25. Kappa → Kitsune → Tengu → Oni → Nio → Fudo Myoo
26–29. Jikokuten → Zochoten → Komokuten → Bishamonten (Four Heavenly Kings)
30–33. Genbu → Byakko → Seiryu → Suzaku (Four Guardian Beasts)
34–37. Fujin → Raijin → Yaksa → Ryujin (Gods)
38–46. Rin 凛 → Byou 病 → Tou 闘 → Sha 沙 → Kai 海 → Jin 刃 → Retsu 烈 → Zen 禅 → Gyou 行 (Nine Souls)
47–48. Whole → Purified (Apex)
49. S: Assembled
50. Super S: Tong-Nou
51. TOP: Master God of the Universe
52–53. RESERVED (unnamed)

## Modes approved this session

- **TTT2 team battle (owner directive).** Tekken Tag Tournament 2 teardown
  supplies the mode structure and tag mechanics: tag in/out, tag throws, tag
  assaults/combos, partner synergy. Wired into WH as a proper mode; all
  fighters team-capable.
- **Heart and Mind Within — integration order (owner directive).** Tekken 5's
  Devil Within is torn down 100% FIRST (structure, level flow, power-ups,
  bosses), THEN the proprietary story is built on top. The character select
  is never forced to Jin — every WH fighter gets their own campaign chapter.
  Per-character 3D beat-em-up campaigns, real-time rendered cutscenes (not
  pre-rendered video), animated in-engine.
- **Tekken Force, Scenario Campaign, create-a-finisher, create-an-arena.**
  All approved as future modes/features; built in teardown wiring order.
- **Mythology-themed side games (owner directive).** Just Fun modes draw from
  traditional mythologies — mainly Japanese, mixed with world mythologies /
  cultures / anthologies per NORTH STAR. Settings: the Five Lands, Phantom
  Marketplace, mini-trials, soul games, matsuri / festival games, spirit
  trials, yokai pastimes — never generic bowling. Specific concepts need
  owner approval.
- **Gungaku** (see name locks above) — the fight lab / programmable training
  dummy mode.

## Teardown strategy and priorities (owner directives)

- **Mode-mapped teardown strategy.** Urban Reign → brawler systems; SF/DOA/SC
  → versus systems; all teardowns → story systems. Detail:
  `docs/research/mode-mapped-teardown-audit-2026-10-22.md`.
- **Teardown wiring priorities.** The ready-to-pull list is the build order.
  DOA4 repair is on the list. Incomplete teardowns get finished before new
  pulls. SoulCalibur II pull decision is PENDING an owner call.
- **Yu Yu Hakusho / Evil Zone: owner's game copies needed.** Teardown cannot
  start until the owner provides access to their copies — pending owner
  question. (Also see game ownership rule below.)
- **Game ownership rule (owner-clarified 2026-10-22).** When the owner says
  they own a game and want it torn down, THAT IS AUTHORIZATION. They own
  they own it, no proof needed, never ask for files. They own
  physical copies — they can't hand over discs and won't do manual ripping.
  Find the files from public archival sources (Internet Archive etc.); store
  large files on Releases/external, not local disk. When the owner says
  they've bought Tekken 8, pull it immediately — no questions, no proof
  requests. The ONLY exception is T8 right now, because the owner explicitly
  said they don't own it YET.
- **T8 UI assets: no depot, no rips.** The Steam/depot route for real Tekken 8
  UI files is dead (owner doesn't own T8 on Steam). The T8 look is recreated
  from public references with original art — NO ripped Tekken UI files in the
  public repo. The select screen reads its look from `game/js/ui-skin.js` so
  future skins/textures drop in without touching screen logic.

## Presentation, physics, audio (owner directives)

- **Jiggle / face / hands teardown findings + wiring priorities.** Wired per
  `docs/JIGGLE-FACE-HANDS-WIRING-2026-10-22.md`: full jiggle set (breasts,
  belly, hips/ass, thighs, camel-toe region), face rig standard, hand rig
  standard. Motion-capture proof required for anything physical, never
  stills presented as done.
- **Announcer YES / crowds deferred.** The announcer voice system is approved
  and stays in scope. Crowd systems are DEFERRED — not built now.
- **Audio: voice mapping by personality.** Voices are cast by the fighter's
  personality and canon, not assigned randomly. Dorowani is the FIRST
  voice-acted character: Squirtle-like creature sounds + barked random
  Japanese words — never full sentences. First lines: "Konnichiwa arigato
  Ichiban Bankai." Voice moments: win poses/taunts, intro sequences,
  cutscenes.
- **Music systems + replacement pipeline.** Approved: jukebox, music systems,
  and a music replacement pipeline. Audio delivery rule: ALL audio to the
  owner goes as direct download links via remote-storage (never in-chat
  attachments — the in-chat player is broken on the owner's Android app).
- **Lighting + environment pull priorities.** Lighting and environment tech
  follow the teardown wiring priorities order — pulled from teardown games,
  not hand-tooled.

## Approved systems batch (owner directives)

Stage mechanics, rage (WH version), training, replays, single-player,
unlockables, jukebox, ranks, cinematics — all approved; built in teardown
wiring order.

## Combat depth approvals (owner directives)

- VF5 throw escapes — approved.
- SoulCalibur 8-way run + guard impact — approved.
- Item moves — approved.
- **Triangle system (DOA) + Reversal Edge (SC): ON HOLD.** Design proposals
  must show Tekken-ified versions that don't hurt feel/flow before anything
  is built. Owner: "Tekken doesn't use those for a reason." Nothing built
  until a proposal is owner-approved.
- **Input-to-move fidelity law (owner's feel principle).** In Tekken every
  input produces a specific, predictable move — the player's fingers and the
  character are tightly coupled. The WH moveset rebuild must achieve this
  tight 1:1 input-to-move fidelity: not just correct mappings, but the FEEL
  of correctness. "Doesn't feel like pressing that button should make them do
  that move" is a bug.

## Online (owner directives)

Netcode, lobbies, tournaments, daily events — all approved. Built per
`docs/research/netcode-multiplayer-streaming.md`.

## Repurposed / renamed systems (owner directives)

- **WWE entrance tools repurposed.** WWE entrance tooling is used for
  cutscene creation + taunt creation ONLY — NOT full entrances. Intros/win
  taunts stay as-is. Proprietary name TBD.
- **V-System.** WH version of SFV's V-System approved; Eastern Mind names TBD.
- **Learning tools: all approved.**
- **Canon mapping requirement for ALL systems.** Every system — modes, menus,
  mechanics — is canon-mapped to the Eastern Mind / Western Heart universe
  (CANON.md: Tong-Nou, Nine Souls, Five Lands, the Trial, the Trader).
  Nothing ships un-mapped.

## Coverage note

Owner-directives.md already carried: audio delivery rule, anti-clobber law,
everything-in-repo rule, division of labor, collaboration loop, display
order law, identity canon + dedup law, intake character canon, moveset source
law, age law, canon-grounded writing law, EM-Jin naming, character select
(T8 grid), menu load speed, T8 no-rips rule. This file adds the session's
remaining directives; the standing-law versions were added to
owner-directives.md in the same PR.
