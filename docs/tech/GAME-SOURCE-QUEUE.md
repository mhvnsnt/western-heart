# Game Source Queue (Steam pulls to private teardown)

Owner request: pt181u. **Grok** pulls and extracts on the box (Fire Pro, Wrestling Empire, Yakuza Kiwami, Gang Beasts, Nioh, then the rest). **Muse** wires the systems and pulls WWE 2K22/2K20. WWE 2K19 is a separate Grok job. Coordination happens on issue #866.

## Owner law: Tekken is the base
Tekken plus the existing Western Heart code is always the base: the combat core, frame data, rigs, select and menus, and the T7 customization system. Every other game's systems are layered on top as extensions or modules that plug into the Tekken base. They never replace it.

## Owner rule: canon names
Every imported item that carries another game's name (moves, heat actions, parts, modes, spirits, stats, places, systems) gets a proprietary Eastern Mind Western Heart canon name in every player-facing string and public file. The private map (original name to canon name, plus source) lives in `game-reverse-engineering/naming/CANON-NAME-MAP.json`. Pipelines rename through `tools/canon/`, and CI fails if a known source-game name appears in player-facing UI strings.

## Spec (Muse, not duplicated here)
- Folder layout and wiring map: PR #878 (`docs/tech/PULL-STRUCTURE-2026-10-23.md`, `teardown/<game>/README.md`).
- Research: #879 Fire Pro, #880 Gang Beasts, #881 WWE 2K22, #882 Nioh, #883 Yakuza Kiwami, #884 Wrestling Empire.
- Decoding tools: `docs/tech/RE-TOOLCHAIN.md`.

## Rules
- Extracted assets go only to private `mhvnsnt/game-reverse-engineering` under `teardown/<game>/`.
- western-heart gets code, loaders and docs only, and loads data through `globalThis.__WH_PRIVATE_ASSETS`.
- One game at a time: manifest first, then `-filelist` batches, never below 8 GB free.
- Raw files are deleted after a verified push and logged in `tools/agent/cleared.log`.
- Arena colors and lighting are never changed.

App and depot IDs and sizes were verified on 2026-10-23 via api.steamcmd.net and the Steam store search (public branch).

| # | Game | App | Main depot | Size | Take | Wires into (as a module on the Tekken base) | Status |
|---|---|---|---|---|---|---|---|
| 1 | Fire Pro Wrestling World | 564230 | 564231 | 3.97 GB | Unity: edit/moveset data, CPU logic (Assembly-CSharp) | sim/CPU AI, creation suite | next |
| 2 | Wrestling Empire | 1620340 | 1620341 | 0.52 GB | Unity: roster/world tables, match variety | HMW world | queued |
| 3 | Yakuza Kiwami (Legacy) | 834530 | 834531 | 12.6 GB | PAR archives: heat actions, styles, story | HMW brawler/story | queued, filelist |
| 4 | Gang Beasts | 285900 | 285903 linux / 285901 win | 1.3 GB | Unity active-ragdoll joint/spring configs | partial ragdoll | queued |
| 5 | Nioh: Complete Edition | 485510 | 485511 | 79.4 GB | creation parts, stances, yokai lore | creation suite, stances | filelist only |
| 6 | Yakuza 0 | 638970 | 638971 | 24.0 GB | as Kiwami | HMW | later |
| 7 | Yakuza Kiwami 2 (Legacy) | 927380 | 927381 | 43.9 GB | Dragon Engine story | HMW | later, filelist |
| 8 | Nioh 2 Complete | 1325200 | 1325201 | 82.0 GB | creation parts | creation suite | later, filelist |
| 9 | Fallout 3 GOTY | 22370 | 22371 | 9.3 GB | BSA/ESM race and face-gen | creation suite | later |
| 10 | Red Faction Guerrilla SE | 20500 | 20501 | 8.1 GB | vpp_pc destruction params | arena destruction (no color/light change) | later |
| 11 | Overgrowth | 25000 | 25002 | 21.3 GB | open-source engine (WolfireGames/overgrowth) | traversal/parkour | prefer source repo |
| 12 | DCS World | 223750 | 1024701+ | 3.5 GB+ | flight sim, little character content | assess | assess |
| 13 | Red Dead Online | 1404210 | 1404213 | 78.8 GB | Euphoria is closed middleware, RAGE archives encrypted | doc only | infeasible |
| 14 | Destiny 2 | 1085660 | 1085661 | 161 GB | Tiger engine, encrypted | doc only | infeasible |
| 15 | Creativerse | 280790 | 280792 | 3.0 GB | voxel builder | assess | assess |
