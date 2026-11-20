# Steam library for Western Heart (owner's 85 games, uses, pull order)

Updated 2026-10-28 by Grok. Full 85-license list: `docs/tech/STEAM-LIBRARY.md` (this plan builds on it). Raw extracted files live only in private `mhvnsnt/game-reverse-engineering` (`teardown/<game>/`) — never this repo or its Pages site.
(`teardown/<game>/`) or `mhvnsnt/box-storage` release parts — never in the public western-heart repo or its Pages site.
Owner law: TEKKEN 7 + existing Western Heart work is the base; every other game layers on top as an extension.
No credentials are stored here.

## Sources
- [S1] `western-heart` `docs/tech/STEAM-LIBRARY.md` (owner pasted his 85-license library, 2026-10-23; app ids + use column + source ranking + pull split).
- [S2] Owner's Oct 23 2026 dev-chat direction (Grok Bot memory): Yakuza 0/Kiwami/Kiwami 2 and Nioh 1/2 for the "heart and mind within" story and Japanese side; Gang Beasts for physics + heart-and-mind-inside mode; Fallout 3 and Destiny 2 for character-creation depth/parts (Destiny 2 also world building); Red Faction: Guerrilla for environment destruction; DCS World for powers/customization/animations; Red Dead Online for euphoria physics and ragdolling; WWE 2K for creation suite/anims/rigs; Fire Pro for sim + AI; Wrestling Empire for world variety.
- [S3] Owner, 2026-10-28 (t268u): "other games ... Like Yakuza games. The Neo games. Red Dead, all of that".
- [S4] Canon: Yakuza heat actions become **Spirit Actions** (魂 ACTION / 魂アクション); "Heat Action" never shown on screen.

- [S5] Owner's confirmed 85-game library + per-game uses, relayed 2026-10-28. The canonical 85-license inventory already lives in [S1]; this plan does not duplicate it.
- Existing research to build on (western-heart `docs/research/`): FIRE-PRO-SYSTEMS-2026-10-23.md, RE-FIREPRO-DESTINY2-PLAN-2026-10-23.md, WRESTLING-EMPIRE-2026-10-23.md, WWE2K22-CREATION-SUITE-2026-10-23.md, RE-WWE2K22-PLAN-2026-10-23.md, YAKUZA-KIWAMI-2026-10-23.md, YAKUZA-EXPANDED-2026-10-23.md, NIOH-SYSTEMS / NIOH2-SYSTEMS-2026-10-23.md, RE-GEOMOD-NIOH2-PLAN-2026-10-23.md, GANG-BEASTS-PHYSICS-2026-10-23.md, `docs/research/pulls/*/pull.json`.

## Owner priority order [S5]
1. **Fire Pro Wrestling World** (133 h played) — match engine (hidden stamina/spirit meters), CPU AI (probability tables + psychology sliders), creation depth → WH Creation Suite + new **WATCH/SIMULATE mode** (build any fighter, watch AI sims) with WH inputs. PULL FIRST. App id is **564230** (570940 is Dark Souls Remastered, not Fire Pro).
2. **Wrestling Empire** — many rule sets on one combat system, backstage roaming world; "heart and mind within" story mode.
3. **WWE 2K22** (+2K19, 2K20) — animations, rigs, customization, creation suite (~10k parts), community creations.
4. **Yakuza Kiwami, Kiwami 2, Yakuza 0** — heat actions → Spirit Actions, style switching, story, Japanese culture, city hubs.
5. **Gang Beasts** — active-ragdoll physics.
6. **Nioh, Nioh 2** — character depth/customization, Eastern mythology lore, Guardian Spirits.
Also: Fallout 3 GOTY (char-creation parts), Red Faction: Guerrilla (destruction), DCS World (powers/customization/anims), Red Dead Online (euphoria ragdoll), Overgrowth (traversal, free-flow combat, parkour), Creativerse (evaluate), Destiny 2 (customization, world). TEKKEN 7 = separate running job. **TEKKEN 8 not owned on Steam: off-limits.**

## Status legend
DONE = in `teardown/` on main · PARTIAL = some data pulled · NEXT = queued · TODO = not started

## Priority games
| # | Game | App ID | What to pull | Why / WH gap it fixes | Status |
|---|---|---|---|---|---|
| 0 | TEKKEN 7 | 389730 | movesets, anims, stages, customization, pakchunk1 patch | base combat core: move links, cancel windows, grab pairing, frame data (random moves / strings not comboing / grabs without opponent anim) | PARTIAL — `teardown/tekken7-steam/`, `pakchunk0/`, `tkdata/`; pakchunk1_P in progress (`/workspace/t7p1P`) |
| 1 | Yakuza 0 | 638970 | `hact.par` (heat actions), `motion/Battle*.par`, `battlepar/`, `behavior.par`, fighting-style data | Spirit Actions system (context grabs/environment finishers), style switching, paired-grab animations with victim side | NEXT after Fire Pro data |
| 2 | Yakuza Kiwami | 834530 | hact, battle motion, behavior | Spirit Actions, brawler strings, paired grabs | DONE (partial pars) — `teardown/yakuza-kiwami/` |
| 3 | Yakuza Kiwami 2 | 927380 | Dragon Engine motion (.gmt), ragdoll/physics params, hact | ragdoll + hit reactions, Spirit Actions v2 | TODO |
| 4 | WWE 2K19 | 960740 | movesets, anims, CAW | grapple pairing (both bodies animated), creation suite | DONE/PARTIAL — `teardown/wwe2k19/` |
| 5 | WWE 2K20 / 2K22 | 1015500 / 1255630 | movesets, anims, CAW, rigs | creation suite, best rig/anim quality | Muse lane (`teardown/wwe2k/`) |
| 6 | Fire Pro Wrestling World | 564230 | move library, edit-wrestler, AI logic | sim mode + CPU AI | PARTIAL — code DONE (`teardown/firepro/decompiled`, 1792 C# files incl. AI + match + edit); data tables (StreamingAssets move/wrestler/AI data) **NEXT** |
| 7 | Wrestling Empire | 1620340 | moves, world data | world variety | DONE — `teardown/wrestling-empire/` |
| 8 | Gang Beasts | 285900 | physics/ragdoll code (il2cpp) | active-ragdoll, heart-and-mind-inside mode | DONE — `teardown/gang-beasts/` |
| 9 | Nioh: Complete Edition ("Neo") | 485510 | weapon movesets, stance system, character creator, yokai/spirit system | stances (high/mid/low) → style system; Japanese spirit/guardian lore for "Eastern Mind" side; Ki pulse ↔ stamina | TODO |
| 10 | Nioh 2 Complete Edition | 1325200 | weapon movesets, Yokai Shift/burst counter, deep creator | burst-counter → Spirit counter; creator sliders | TODO |
| 11 | Red Dead Online / RDR2 | 1404210 (RDO) / 1174180 (RDR2; ownership of RDO only per [S2]) | euphoria-style ragdoll tuning, hit reactions, lasso/grapple | ragdoll and physical hit reactions; "Western" side flavor | TODO — RAGE .rpf archives; heavy (~120 GB) |
| 12 | Overgrowth | 25000 | procedural anim + physics combat (open-sourced engine) | procedural reactions, physics combat | TODO |
| 13 | MGSV TPP / GZ | 287700 / 311340 | CQC anims | grabs, counters | TODO |
| 14 | Middle-earth: Shadow of War | 356190 | finishers, combat anims | finishers ↔ Spirit Actions | TODO |
| 15 | The Witcher 3 | 292030 | combat anims | weapon combat | TODO |
| 16 | Skyrim SE / PSO2 NGS / Spore / Dragon's Dogma DA | 489830 / 1056640 / 17390 / 367500 | morphs, sliders, body physics, creature creator, grab/climb | creation suite depth | TODO |
| 17 | Fallout 3 / Destiny 2 | 22370 / 1085660 | char creation parts; world building | creation depth, world builder | TODO |
| 18 | Red Faction: Guerrilla | 20500 (Re-Mars-tered 667720) | destruction system | environment destruction | TODO |
| 19 | DCS World | 223750 | — (sim) | powers / customization / animations per [S2] | TODO (low) |
| 20 | Pro Wrestling X, Drunken Wrestlers 2, UNDEFEATED | — | grappling physics, active ragdoll, hero anims | grapple physics | TODO |

App ids marked `—` are not looked up yet. App ids not in [S1] (Fallout 3, RF:G, RDO/RDR2) are public store ids to verify against the account licenses before download.

## Pull method (every game)
1. DepotDownloader with the saved login, `-filelist` limited to the needed archives; one chunk at a time.
2. Extract with open tools (ParManager for Yakuza PAR, repak/umodel for UE, il2cppdumper for Unity).
3. Push to `teardown/<game>/` in batches with SHA-256 lists; files >50 MB go to `box-storage` release parts.
4. Verify hashes on the remote, delete local copy, keep ≥8 GB free, never collide with a running job.

## Progress log
- 2026-10-28: Fire Pro data tables landed in game-reverse-engineering #66 (`teardown/firepro/data/`). Yakuza 0 batch b1 raw archives landed in #67 (`teardown/yakuza-0/`). Watch/Simulate + CPU AI spec: western-heart #1158.
