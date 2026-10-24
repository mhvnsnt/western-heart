# WIRING-MAP — pulled sources → Western Heart systems (2026-10-23)

Owner (t204): "everything that we've pulled in so far get it wired up where appropriate".
Rules: Tekken + Western Heart base stays; everything here is an **extension**. Raw/derived game
assets load only from the private pack (`__WH_PRIVATE_ASSETS`); this repo gets code + docs only.
Clean-room: code here is written from design notes, never pasted from decompiled sources.
Player-visible names go through `tools/canon` (private `naming/CANON-NAME-MAP.json`).
No wrong bodies on any fighter. Show/cutscene clips are gated from movesets (`anim-gate.js`).

| Source (private repo) | Feeds system | Integration point | Status | Canon name |
|---|---|---|---|---|
| Fire Pro AI logic sheets (AIParam, AIPriorityAct, AIOpt_*, Cpu_Fight*) — #53 | Data-driven CPU personality layer | `game/js/ai/cpu-personality.js` → `AIController` personality in `game.js` startMatch (`personalityForChar`); roster `archetype` → CPU archetype | **WIRED** (this PR) — public default archetypes; private derived table via `__WH_CPU_LOGIC` | CPU Style (brawler / grappler / turtle / showboat / technician) |
| Fire Pro Cpu_Fight (CPU-vs-CPU) — #53 | Watch + Simulate | Watch = `?demo=1` AI-vs-AI (existing, now uses personalities); Simulate = `game/js/sim-match.js` `simulateMatch()` (seeded, best-of-N) | **WIRED** (logic + tests); menu entry → menus job (#932/#943) owns menu files | Watch Mode / Simulate |
| Fire Pro edit / move-craft (EditSkillData, EditPointTbl, *_Craft dialogs) — #53 | Creation-suite move-craft data | `customization/` move editor (MOVESET_EDITOR_SPEC.md) | NEXT — split with Muse (#879 research) | Move Forge |
| Yakuza Kiwami heat actions / HACT (1491 scene PARs) — #55/#57 | Context-sensitive finishers on the existing HEAT/URGE gauge | `game/js/spirit-actions.js`; `game.js` p1 queue: 2+3 while URGE on + context (wall, downed, stun, back-turned, prop) → `_spiritCheck` | **WIRED** (logic + input hook + tests). Cinematic clip lookup from private `__WH_SHOW_CLIPS.spirit` (show-only) | **Spirit Action** — UI `魂 ACTION`, ja `魂アクション`. Never "Heat Action". Distinct from the `HEAT` touch button (2+3 URGE gauge). |
| Yakuza Kiwami motion (~6,200 combat anims) — #55 | Show / cutscene clip bank only | private `__WH_SHOW_CLIPS`; Track 7 cinematic director (#936) | GATED, not in movesets. Clip conversion NEXT | — |
| Yakuza scenario / battle tables — #55 | Story/brawler (HMW) | Track 7 story (#936), Muse #883 | NEXT (Muse lane) | — |
| WWE 2K19 CAW parts, 597 DDS textures, 6 YOBJ models — #58 | Creation-suite parts by t7layout slot | `game/js/creation-parts-private.js` `loadPrivateParts()` → reads private `creation-parts/manifest.json` (glb, slot, canon:true) | Loader **WIRED** + tests. YOBJ→glTF converter **IN PROGRESS** (no off-the-shelf converter; DDS textures convert directly) | Parts take canon names at conversion |
| Gang Beasts IL2CPP class design (Actor/BodyHandeler/grab, ragdoll) — #59, Muse #880 | Grab-hold + ragdoll behaviour on existing active ragdoll | `game/js/grab-hold.js` (per-hand grip, limb targets, struggle drain, leverage throw impulse; `applyRelease` → physics bodies) | **WIRED** module + tests; hookup into `chrono-grapple.js` lane (#930) after it lands | Grip / Hold |
| Tekken 7 movesets, stages, anims, customization tables — #50/#51/#52 | Combat + select + customization | `movesets.js`, `select-t7-layout.js`, `t7-ui-private.js`, `customization-consumer.js` | WIRED (existing); combat-input (#951), select (#947), menus (#932/#943) jobs own those files | per CANON.md |
| Wrestling Empire World / Character / Editor / Progress — #53, Muse #884 | HMW world sim, roster editor, career progress | `tournament.js`, `ranks.js`, `unlockables.js` | NEXT — split with Muse | — |
| Soul systems (owner design) | KESSHOU + Nine-Soul Release + Reihou + Trial's Seal, per-fighter variants | `game/js/soul-systems.js`, `finisher.js`, `game/data/soul-variants.json` | **WIRED** — see `docs/design/SOUL-SYSTEMS.md` | 結章 KESSHOU · 九魂解放 Nine-Soul Release · 霊放 Reihou · 試練の封 Trial's Seal |
| Nioh 1/2 | Character depth (Muse #882) | — | BLOCKED: ~70 GB each vs disk | — |

Tests: `test/wiring.test.mjs`, `test/soul-systems.test.mjs` (run by game-checks). Proof: `proof/wiring/`.
Work split: Muse keeps move-craft (Fire Pro edit), Wrestling Empire world/progress and Yakuza
story wiring per #878/#879/#883/#884; Grok keeps CPU, Spirit Action, parts conversion, grab-hold, soul systems.
