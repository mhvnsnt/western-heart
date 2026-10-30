# Steam games pull — master index — every owned game, where its pack lives (Lane 7, 2026-10-24)

Status: SPEC-ONLY. No game files were accessible from this VM (phone-only user; Steam remote
download previously reported "Unable to reach your PC"), so no commercial game assets were
extracted in this pass and none are included in the PR. Each pack below is the teardown path +
conversion/wire schema for a machine that HAS the owned game installed, plus the exact blocker
and unblock path where a pull cannot proceed from here. Raw commercial files, if ever extracted,
go ONLY in the PRIVATE game-reverse-engineering repo, never in public western-heart.

Canon + play-style law (applies to every row): everything wired WITHIN CANON.md (Tong-Nou,
Nine Souls, Five Lands, Trial, Trader — no invented lore) and WITHIN Tekken combat
(LP1=Left Punch=Tekken 1, RP2=Right Punch=Tekken 2, LK3=Left Kick=Tekken 3, RK4=Right Kick=Tekken 4,
strings, Tekken feel). Anything brought in with another game's name is renamed to Eastern Mind /
Western Heart canon in user-facing writing; Tekken/proprietary names stay in technical files only.
Game ships with NO famous names. Tekken + existing WH work = THE BASE; everything else plugs in
ON TOP. All characters adults. Display order: user's own models FIRST (Tripo + SmutBase);
Tekken models as back-slot attires. Sole exception: Pantera Attire 1 (user-customized King reskin).
Frame data / MOD damage: UNMAPPED unless a source file in the pack contains it — never estimated
as measured. License firewall OFF per user override: pull everything regardless of license,
document copyleft, never block — but that override does not create game files that do not exist here.

Partition: this PR touches NEW files under `docs/research/pulls/<game>/` + `docs/research/` only.
Existing moveset banks and lane-owned files are NOT edited; where a bank already exists, the pack
is a wire note for the owning lane.

## Partition map

| PR | Contents |
|---|---|
| Priority PR (this PR) | TEKKEN 7, TEKKEN 8, Yakuza 0 / Kiwami / Kiwami 2, Nioh CE, Nioh 2 CE, Gang Beasts |
| Wrestling PR | WWE 2K19 / 2K20 / 2K22 / 2K26, every-other-WWE-2K family, Fire Pro Wrestling World, WWF No Mercy (wire note), WWE WrestleMania XIX (wire note, PROVISIONAL), Wrestling Empire, Pro Wrestling X, Drunken Wrestlers 2, creation-suite template |
| Rest PR | Every remaining Steam-snapshot title (85-title snapshot minus the above, plus duplicates noted) |

## Per-game pack locations

| Game | Pack |
|---|---|
| Gang Beasts | `docs/research/pulls/gang-beasts/pull.json` (pr1-priority) |
| Nioh: Complete Edition | `docs/research/pulls/nioh/pull.json` (pr1-priority) |
| Nioh 2 – The Complete Edition | `docs/research/pulls/nioh-2/pull.json` (pr1-priority) |
| TEKKEN 7 | `docs/research/pulls/tekken7/pull.json` (pr1-priority) |
| TEKKEN 8 | `docs/research/pulls/tekken8/pull.json` (pr1-priority) |
| Yakuza 0 | `docs/research/pulls/yakuza-0/pull.json` (pr1-priority) |
| Yakuza Kiwami (Legacy) | `docs/research/pulls/yakuza-kiwami/pull.json` (pr1-priority) |
| Yakuza Kiwami 2 (Legacy + Kiwami 2) | `docs/research/pulls/yakuza-kiwami-2/pull.json` (pr1-priority) |
| Drunken Wrestlers 2 | `docs/research/pulls/drunken-wrestlers-2/pull.json` (pr2-wrestling) |
| Fire Pro Wrestling World | `docs/research/pulls/fire-pro-wrestling-world/pull.json` (pr2-wrestling) |
| Pro Wrestling X | `docs/research/pulls/pro-wrestling-x/pull.json` (pr2-wrestling) |
| Wrestling Empire | `docs/research/pulls/wrestling-empire/pull.json` (pr2-wrestling) |
| Every other WWE 2K game (2K14–2K25, 2K Battlegrounds, WWE '12/'13, SmackDown vs Raw era, WrestleMania XIX — see also wmxix pack) | `docs/research/pulls/wwe-2k-family/pull.json` (pr2-wrestling) |
| WWE 2K19 | `docs/research/pulls/wwe-2k19/pull.json` (pr2-wrestling) |
| WWE 2K20 | `docs/research/pulls/wwe-2k20/pull.json` (pr2-wrestling) |
| WWE 2K22 | `docs/research/pulls/wwe-2k22/pull.json` (pr2-wrestling) |
| WWE 2K26 | `docs/research/pulls/wwe-2k26/pull.json` (pr2-wrestling) |
| WWE WrestleMania XIX (banked — WIRE NOTE ONLY, do not edit the bank) | `docs/research/pulls/wwe-wrestlemania-xix/pull.json` (pr2-wrestling) |
| WWF No Mercy (banked — WIRE NOTE ONLY, do not edit the bank) | `docs/research/pulls/wwf-no-mercy/pull.json` (pr2-wrestling) |
| 3on3 FreeStyle: Rebound | `docs/research/pulls/3on3-freestyle-rebound/pull.json` (pr3-rest) |
| Aimlabs | `docs/research/pulls/aimlabs/pull.json` (pr3-rest) |
| Alien Swarm: Reactive Drop | `docs/research/pulls/alien-swarm-reactive-drop/pull.json` (pr3-rest) |
| Angel Wings | `docs/research/pulls/angel-wings/pull.json` (pr3-rest) |
| Borderlands 3 | `docs/research/pulls/borderlands-3/pull.json` (pr3-rest) |
| Century: Age of Ashes | `docs/research/pulls/century-age-of-ashes/pull.json` (pr3-rest) |
| Conqueror's Blade | `docs/research/pulls/conqueror-s-blade/pull.json` (pr3-rest) |
| Counter-Strike 2 | `docs/research/pulls/counter-strike-2/pull.json` (pr3-rest) |
| Crab Game | `docs/research/pulls/crab-game/pull.json` (pr3-rest) |
| Creativerse | `docs/research/pulls/creativerse/pull.json` (pr3-rest) |
| Crossout | `docs/research/pulls/crossout/pull.json` (pr3-rest) |
| DC Universe Online | `docs/research/pulls/dc-universe-online/pull.json` (pr3-rest) |
| DCS World Steam Edition | `docs/research/pulls/dcs-world-steam-edition/pull.json` (pr3-rest) |
| Destiny 2 | `docs/research/pulls/destiny-2/pull.json` (pr3-rest) |
| Digimon Masters Online | `docs/research/pulls/digimon-masters-online/pull.json` (pr3-rest) |
| Dragon's Dogma: Dark Arisen | `docs/research/pulls/dragon-s-dogma-dark-arisen/pull.json` (pr3-rest) |
| Drug Dealer Simulator: Free Sample | `docs/research/pulls/drug-dealer-simulator-free-sample/pull.json` (pr3-rest) |
| eFootball | `docs/research/pulls/efootball/pull.json` (pr3-rest) |
| ENDLESS Space – Definitive Edition | `docs/research/pulls/endless-space-definitive-edition/pull.json` (pr3-rest) |
| Fallout 3 - Game of the Year Edition | `docs/research/pulls/fallout-3-game-of-the-year-edition/pull.json` (pr3-rest) |
| Fallout Shelter | `docs/research/pulls/fallout-shelter/pull.json` (pr3-rest) |
| Game Migrated to Another Steam Page | `docs/research/pulls/game-migrated-to-another-steam-page/pull.json` (pr3-rest) |
| Gorilla Tag | `docs/research/pulls/gorilla-tag/pull.json` (pr3-rest) |
| H1Z1: Test Server | `docs/research/pulls/h1z1-test-server/pull.json` (pr3-rest) |
| Halo Infinite | `docs/research/pulls/halo-infinite/pull.json` (pr3-rest) |
| Heavy Burger | `docs/research/pulls/heavy-burger/pull.json` (pr3-rest) |
| Just Cause 2 | `docs/research/pulls/just-cause-2/pull.json` (pr3-rest) |
| Knightfall: Rivals | `docs/research/pulls/knightfall-rivals/pull.json` (pr3-rest) |
| L.A. Noire | `docs/research/pulls/l-a-noire/pull.json` (pr3-rest) |
| Master Spy | `docs/research/pulls/master-spy/pull.json` (pr3-rest) |
| Max Payne 2: The Fall of Max Payne | `docs/research/pulls/max-payne-2-the-fall-of-max-payne/pull.json` (pr3-rest) |
| Max Payne 3 | `docs/research/pulls/max-payne-3/pull.json` (pr3-rest) |
| MechWarrior Online | `docs/research/pulls/mechwarrior-online/pull.json` (pr3-rest) |
| METAL GEAR SOLID V: GROUND ZEROES | `docs/research/pulls/metal-gear-solid-v-ground-zeroes/pull.json` (pr3-rest) |
| METAL GEAR SOLID V: THE PHANTOM PAIN | `docs/research/pulls/metal-gear-solid-v-the-phantom-pain/pull.json` (pr3-rest) |
| Middle-earth: Shadow of War | `docs/research/pulls/middle-earth-shadow-of-war/pull.json` (pr3-rest) |
| Muck | `docs/research/pulls/muck/pull.json` (pr3-rest) |
| Old School RuneScape | `docs/research/pulls/old-school-runescape/pull.json` (pr3-rest) |
| Overgrowth | `docs/research/pulls/overgrowth/pull.json` (pr3-rest) |
| Paladins | `docs/research/pulls/paladins/pull.json` (pr3-rest) |
| Paladins - Public Test | `docs/research/pulls/paladins-public-test/pull.json` (pr3-rest) |
| Path of Exile | `docs/research/pulls/path-of-exile/pull.json` (pr3-rest) |
| Phantasy Star Online 2 New Genesis | `docs/research/pulls/phantasy-star-online-2-new-genesis/pull.json` (pr3-rest) |
| Portal Reloaded | `docs/research/pulls/portal-reloaded/pull.json` (pr3-rest) |
| Quantum Replica | `docs/research/pulls/quantum-replica/pull.json` (pr3-rest) |
| Re-Legion | `docs/research/pulls/re-legion/pull.json` (pr3-rest) |
| Red Dead Online | `docs/research/pulls/red-dead-online/pull.json` (pr3-rest) |
| Red Faction | `docs/research/pulls/red-faction/pull.json` (pr3-rest) |
| Red Faction: Armageddon | `docs/research/pulls/red-faction-armageddon/pull.json` (pr3-rest) |
| Red Faction Guerrilla Re-Mars-tered | `docs/research/pulls/red-faction-guerrilla-re-mars-tered/pull.json` (pr3-rest) |
| Red Faction: Guerrilla Steam Edition | `docs/research/pulls/red-faction-guerrilla-steam-edition/pull.json` (pr3-rest) |
| Rogue Company | `docs/research/pulls/rogue-company/pull.json` (pr3-rest) |
| RuneScape | `docs/research/pulls/runescape/pull.json` (pr3-rest) |
| SMITE | `docs/research/pulls/smite/pull.json` (pr3-rest) |
| SMITE - Public Test | `docs/research/pulls/smite-public-test/pull.json` (pr3-rest) |
| Splitgate | `docs/research/pulls/splitgate/pull.json` (pr3-rest) |
| Spore | `docs/research/pulls/spore/pull.json` (pr3-rest) |
| Spore: Creepy & Cute Parts Pack | `docs/research/pulls/spore-creepy-cute-parts-pack/pull.json` (pr3-rest) |
| Spore: Galactic Adventures | `docs/research/pulls/spore-galactic-adventures/pull.json` (pr3-rest) |
| STAR WARS: The Old Republic | `docs/research/pulls/star-wars-the-old-republic/pull.json` (pr3-rest) |
| Tales of the Neon Sea | `docs/research/pulls/tales-of-the-neon-sea/pull.json` (pr3-rest) |
| Tap Ninja | `docs/research/pulls/tap-ninja/pull.json` (pr3-rest) |
| The Elder Scrolls V: Skyrim Special Edition | `docs/research/pulls/the-elder-scrolls-v-skyrim-special-edition/pull.json` (pr3-rest) |
| The Witcher 3: Wild Hunt — Remastered | `docs/research/pulls/the-witcher-3-wild-hunt-remastered/pull.json` (pr3-rest) |
| UNDEFEATED | `docs/research/pulls/undefeated/pull.json` (pr3-rest) |
| Walking Simulator 2020 | `docs/research/pulls/walking-simulator-2020/pull.json` (pr3-rest) |
| War Robots | `docs/research/pulls/war-robots/pull.json` (pr3-rest) |
| Yu-Gi-Oh! Duel Links | `docs/research/pulls/yu-gi-oh-duel-links/pull.json` (pr3-rest) |
| Yu-Gi-Oh! Master Duel | `docs/research/pulls/yu-gi-oh-master-duel/pull.json` (pr3-rest) |
| Z1 Battle Royale | `docs/research/pulls/z1-battle-royale/pull.json` (pr3-rest) |
