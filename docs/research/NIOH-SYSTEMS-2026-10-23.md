# Nioh: Complete Edition — Systems Research for Western Heart
**Date:** 2026-10-23
**Owner instruction:** *"Perfect for character depth and customization plus heart and mind inside and code and lore for Japanese and mythology and eastern mind type canon building"*
**Researcher:** DoggByte (subagent)
**Status of every claim in this doc:** marked **[RESEARCHED]** (public sources, cited) or **[AWAITS FILE PULL]** (needs the Steam install on a machine with credentials — this VM has none, so nothing here was pulled from game files).

---

## 0. LORE FIREWALL — READ FIRST

**NEVER copy Nioh lore into Western Heart.** No yokai names, no Guardian Spirit identities, no William/Kelley/Amrita/Saoirse material, no Sengoku plot beats go into WH canon. WH canon comes **ONLY** from the project's own `CANON.md` (Tong-Nou, the Nine Souls, the Five Lands, the Trial). Nioh is reference **exclusively for structure and technique**: how to organize a mythology compendium, how to layer character-depth systems, how to frame missions around legend, how to build a deep skill/build system. Everything in this doc about Nioh's *content* is described only so we can extract the *pattern* and rebuild it with WH canon. All characters are adults — this doc concerns game systems, not characters, but the rule stands across the project.

---

## 1. Character depth systems (Nioh 1, Complete Edition)

### 1.1 Eight stats, each weapon-mapped [RESEARCHED]
Nioh gives the player eight stats to distribute at shrines using Amrita (the game's XP): **Body, Heart, Stamina, Strength, Skill, Dexterity, Magic, Spirit** (Polygon's Nioh guide, https://www.polygon.com/nioh-guide/2017/2/3/14500664/stats-level-up-body-heart-stamina-strength-skill-dexterity-magic-spirit-weapons-presige-skill-points/). Each stat does four jobs at once:
1. **Scales specific weapons** — e.g. Body scales Spears (B+), Heart scales Swords and Bows (B+), Stamina scales Cannons, Strength scales Axes, Skill scales Dual Swords and Rifles, Dexterity scales Kusarigama (GameFAQs stat guide, https://Gamefaqs.gamespot.com/boards/222766-nioh-complete-edition/74970134).
2. **Feeds secondary attributes** — Life, Ki, Ki Pulse strength, Equipment Weight Max, Ninjutsu/Onmyo power and capacity, Guardian Spirit Bond, elemental resistances (same GameFAQs guide).
3. **Unlocks skill points** — Body/Heart/Stamina/Strength/Skill feed Samurai skill points; Dexterity feeds Ninja skill points; Magic feeds Onmyo skill points; Spirit feeds Guardian Spirit bond (Polygon guide).
4. **Gates armor perks** — Strength unlocks heavy-armor special effects; Skill unlocks light-armor ones (GameFAQs guide).

The key structural trick: **every stat point is simultaneously offense, defense, and progression currency.** There is no dead stat.

**Transferable technique for WH/HMW:** one stat, four payoffs (weapon damage scaling, a defensive/utility attribute, skill-tree currency, armor-perk gating). This is the density formula behind Nioh's build depth.

### 1.2 Three skill trees + per-weapon trees [RESEARCHED]
- **Samurai skill points** buy into **per-weapon skill trees** — each of the 7 weapon types (katana, dual katana, spear, axe/hammer, kusarigama, odachi, tonfa) has ~45 unlockable skills: new combo strings, finishers, stance-switch cancels, parries, passives (Polygon guide; lp.zone overview https://www.lp.zone/t/nioh-pulsing-ki-like-its-1600/586). Samurai points are earned from leveling weapon-scaling stats **and** from weapon proficiency (using the weapon in combat) — in Nioh 1, per the beginner FAQ, "Samurai points are used for all weapons. Just gain levels and use different weapon types to gain more points" (https://pastebin.com/yTMRVJYC).
- **Ninja skill points** (from Dexterity) unlock the ninjutsu tree: shuriken, kunai, bombs, poisons, smoke, traps — essentially a consumable/loadout system tied to a stat (Polygon guide).
- **Onmyo skill points** (from Magic) unlock the onmyo magic tree: talismans that grant temporary buffs to stats, weapon elements, or defenses (Polygon guide).
- Higher tree tiers are gated behind **Dojo missions** (see §5.2): you must beat a mastery duel at Dexterity/Magic thresholds (10/15/20) to unlock the next tier (GameFAQs in-depth stats thread, https://gamefaqs.gamespot.com/boards/181161-nioh/74987933).
- Cap: Samurai tree is fully completable around level ~400 in deep NG+; Ninja/Onmyo are effectively completable but may force choices between some skills (Steam forum, https://steamcommunity.com/app/485510/discussions/0/3122659822732475759/?l=koreana).

**Transferable technique:** three orthogonal progression currencies (weapon-mastery, trickster-toolkit, spirit-magic) + per-weapon move-unlock trees + dojo-gated tiers. For HMW, each fighter's campaign could gate their canon techniques behind dojo-style trials instead of handing out the full movelist.

### 1.3 Stance system — three movesets per weapon [RESEARCHED]
Every weapon has **three stances** — High / Mid / Low — switched on the fly (R1 + Triangle/Square/X), each with distinct attack animations, damage, Ki cost, and defensive properties (PlayStation Blog, https://blog.playstation.com/2020/03/11/survive-nioh-2s-opening-hours-with-9-gameplay-tips/):
- **High:** max damage, max Ki cost, heavy attacks break guards and eat enemy Ki; dodge is a roll (costliest).
- **Mid:** balanced; best blocking (regains Ki while guard-moving); most parries are mid-stance-only; dodge is a step then roll.
- **Low:** fastest, cheapest Ki, lowest damage; best for dodging and applying status effects; dodge is a quick step (cheapest). (Fextralife stances page, https://nioh2.wiki.fextralife.com/High+Stance)
- **Ki Pulse:** after an attack string, a timed R1 tap recovers spent Ki; **Flux** = switching stance during a Ki Pulse for extra recovery, which enables stance-cancel combo routing (PS Blog; lp.zone).

**Transferable technique:** a stance layer is a *multiplier on build variety* — 7 weapons × 3 stances ≈ 21 distinct movesets. For WH fighters, "stance" could map to per-fighter Tekken stances (e.g. Zafina's stances) gated behind the Samurai-style per-weapon tree, with stance-switch cancels as an advanced technique.

### 1.4 Guardian Spirits — bonded companion system [RESEARCHED]
- ~30+ Guardian Spirits, each with: an element (Fire/Water/Wind/Lightning/Earth), passive bonuses (e.g. attack enhancement %, Amrita earned %, life recovery), a **Might** stat and **Action/Recovery/Tenacity** ratings governing the **Living Weapon** transformation (Fextralife, https://nioh.wiki.fextralife.com/Spirit+Guardians).
- **Living Weapon:** activated at full Amrita gauge (Triangle+Circle) — temporary invulnerability, weapon infused with the spirit's element, big damage boost; gauge drains over time and on hits; re-pressing the input fires the spirit's **unique skill** (Fextralife).
- Spirits are leveled to 30 with Amrita in NG+ ("Enhance Guardian"), improving Protection and Living Weapon stats (Fextralife).
- **Dual-spirit system (patch 1.08):** a secondary spirit confers a halved passive plus a **combination attribute** determined by the element pair (e.g. fire+wind = Ki Recovery Speed, fire+lightning = Quick Attack Damage, water+wind = Life Recovery after Living Weapon — 15 documented pair rules) (Fextralife).
- Spirits also protect your dropped Amrita on death — they are mechanically the "soul bank" (Fextralife).

**Transferable technique:** a bonded-spirit layer is WH-canon-compatible in *structure* (Eastern Mind already has souls/spirits/Oversoul lore) — a per-fighter "soul companion" granting passive build bonuses + a transformation super + combinable pair bonuses. **Content must come from WH canon (Nine Souls, etc.), never from Nioh's spirit roster.**

### 1.5 Loot and build crafting [RESEARCHED]
- **Rarity tiers:** Common → Exotic → **Divine** → **Ethereal** (endgame), each with randomized **special effects**; some effects are **inheritable** (transferable between items) (Fandom Blacksmith, https://nioh.fandom.com/wiki/Blacksmith; GameFAQs Bloodshed's End build guide, https://gamefaqs.gamespot.com/ps4/222933-nioh-bloodsheds-end/faqs/75964).
- **Blacksmith operations:** Forge (craft from smithing texts/materials), **Soul Match** (sacrifice a higher-level item to raise a base item's level — like Destiny's Infusion — and transfer inheritable effects at max familiarity), **Reforge** (reroll one special effect), **Temper** (pick the replacement effect from a list, using Umbracite), **Refashion** (transmog — appearance only), Disassemble (break down for materials) (Fandom Blacksmith; Fextralife FAQ https://nioh.wiki.fextralife.com/FAQ).
- **Forged gear requires half the stat requirements** of found gear, and repeated forging is a path to rare "star" skills — crafting is a first-class build path, not a consolation (GameFAQs build guide).
- **Set bonuses and Graces** (DLC): armor sets and endgame "graces" grant multi-piece bonuses; the Abyss defilement system rerolls graces — the deep-endgame build chase (GameFAQs build guide).

**Transferable technique:** Soul Match (keep your favorite gear competitive forever) + Reforge/Temper (controlled affix reroll) + Refashion (looks decoupled from stats) is the complete loot-crafting loop. For HMW: fighter "attire loadouts" could carry WH-canon set bonuses; tempering maps to move-property tuning.

---

## 2. Customization systems

### 2.1 Nioh 1: fixed protagonist + cosmetic skins [RESEARCHED]
Nioh 1's protagonist is fixed (William). Appearance customization is limited to **skins purchased with Glory at the Hidden Teahouse** — purely cosmetic, changing model and voice, **not applied in cutscenes** (Steam forum, https://steamcommunity.com/app/485510/discussions/0/1519260397797949415/). Equipment appearance can be changed freely via **Refashion** at the blacksmith (Fandom Blacksmith).

### 2.2 Nioh 2/3: full character creator (context for what the series evolved into) [RESEARCHED]
Nioh 2 added a deep character creator (gender, build, face down to fringe curl), re-accessible from the Hut, with presets and a shareable **character code** system; Nioh 3 keeps this plus per-slot transmog cataloged automatically from found gear and a "Transform" option to take on NPC appearances (GameFAQs Hut guide, https://gamefaqs.gamespot.com/ps4/241160-nioh-2/faqs/78230/hut; Polygon Nioh 3 appearance guide, https://www.polygon.com/nioh-3-change-appearance-transmog-how-to/). Also **Equipment Sets / Builds** save slots: full loadouts including stats, skills, and skill customization, switchable between missions (GameFAQs Hut guide).

**Transferable technique for WH:** the character-creation suite is already WH's own project — Nioh confirms the *pattern*: creator-at-start + re-editable-later + shareable codes + transmog catalog + named build loadouts. WH's suite should ship named build slots (gear + stats + skill choices) as a first-class feature, matching Nioh 2's "Builds."

---

## 3. Japanese mythology — STRUCTURE AND TECHNIQUE ONLY (no content transfer)

### 3.1 The compendium pattern: "Amrita Memories" / Illustrations [RESEARCHED]
Nioh structures its folklore as an **in-game encyclopedia** ("View Illustrations" at the Hut) with entries for **Yokai, story characters, and Guardian Spirits**, unlocked as you progress; you can also rewatch unlocked cutscenes there (GameFAQs Hut guide). Each entry follows a fixed information architecture — example from the fan wiki mirroring the game's entries (https://nioh.wiki.fextralife.com/Yokai):
- **Name + classification** (e.g. "Yoki — when a human is transformed into a demon by Amrita").
- **A short in-world description** written as folklore-natural-history (e.g. Onyudo: fallen monks who "collect the skulls of their victims and wear them across their shoulders like a rosary").
- **Behavioral notes** tying lore to gameplay (habitat, temperament, what provokes it).
- Bosses recur as regular enemies later, and the entries explicitly frame them as *a species, not individuals* — lore justifying mechanical reuse (TV Tropes, http://tvtropes.org/pmwiki/pmwiki.php/Characters/NiohEnemiesAndBosses).

A fan-compiled "Secrets of the Dead" PDF shows the same architecture for Guardian Spirits: spirit name + pronunciation + a paragraph linking the spirit to a historical figure's legend (https://f07eb630-23ff-4298-a1df-d7940f1ba2dc.filesusr.com/ugd/097a5b_0226a8e79ebd45d49999ffda7dbfb009.pdf?index=true).

**Transferable technique (STRUCTURE ONLY):** WH's Eastern Mind canon needs exactly this information architecture — a compendium with fixed entry slots (name, classification, in-world description, behavioral/combat notes, "species not individual" framing for reuse). WH fills it with **its own canon only** (Nine Souls, Tong-Nou entities, Trial lore). Nioh proves the pattern works: folklore entries double as design docs for enemy behavior.

### 3.2 Mission framing around legend [RESEARCHED]
- Missions are selected from a **region map**, not an open world; each region (Kyushu, Chugoku, Kinki, Tokai, Sekigahara, Omi, Tohoku…) is a chapter of the historical-folklore arc, and missions are named as legend-beats ("The Spirit Stone Slumbers," "Spider Nest Castle," "The Demon of Mount Hiei") (Fandom regions, https://nioh.fandom.com/wiki/Category:The_Way_of_the_Samurai; Samurai Gamers mission list, https://samurai-gamers.com/nioh/).
- **Mission types:** Main (story, mandatory, unique bosses), Sub (optional side stories, sometimes harder than mains), Twilight (rotating harder remixes, 2 per 24h real time), Dojo (training duels that gate skill tiers) (Fandom Dojo, https://nioh.fandom.com/wiki/Dojo_Missions; fuzionbyte region guide, https://fuzionbyte.com/nioh-omi-region-missions/).
- Completing missions **unlocks compendium entries** ("Unlocks Hattori Hanzo Entry 1") — progression and lore-unlock are the same event (Fandom Main Missions, https://nioh.fandom.com/wiki/Main_Missions).
- **Difficulty cycles:** Way of the Samurai → Strong → Demon → Wise → Nioh (NG+0–4), each unlocking whole regions at once and switchable up/down (Steam forum).
- **The Abyss:** a 999-floor endgame gauntlet (4-floor runs, defilement rerolls gear graces) — the infinite-content tail (GameFAQs build guide).
- **Kodama:** collectible forest spirits guided back to shrines; each grants a shrine **Blessing** (Amrita gain, weapon/armor/elixir drop rates) chosen per region — folklore-as-progression-knob (Samurai Gamers, https://samurai-gamers.com/nioh/kodama-explained-nioh/; Fextralife Kodama, https://nioh.wiki.fextralife.com/Kodama).
- **Shrines** are checkpoints where you level up, assign skill points, offer items, and respawn enemies — the loop hub (Alchetron gameplay summary, https://alchetron.com/Nioh).

**Transferable technique (STRUCTURE ONLY):** HMW campaigns should be region-mapped chapters with four mission types (Story / Side / Rotating challenge / Dojo-trial), compendium entries unlocked by mission completion, shrine-equivalent hubs (WH-canon: Trial gates? Nine-Soul shrines?), collectible spirit-guides granting per-chapter blessings, and NG+ difficulty cycles plus an Abyss-style endless gauntlet. All names/content from WH canon.

---

## 4. Code architecture — what is publicly known [RESEARCHED where sourced; GAPS marked]

- **Engine lineage:** Team Ninja's games share a graphics-engine lineage from Ninja Gaiden 3 → Dead or Alive 5's Yawaraka engine → refined for Nioh (with Katana Engine confirmed for later titles like Wo Long and Rise of Ronin; whether Nioh 1 itself is "Katana Engine" is **disputed** — the engine began as a middleware library, KTGL, so "uses Katana" ≠ "made in Katana"; Wikipedia talk page, https://en.wikipedia.org/wiki/Talk:Katana_Engine). Team Ninja has **not** moved to Unreal; Nioh 3 still runs on proprietary Katana Engine tech (Wccftech, https://wccftech.com/roundup/nioh-3-everything-we-know-about-team-ninjas-supernatural-action-rpg/).
- **Design process (GDC 2017):** director Fumihiko Yasuda's talk "Nioh: Reinventing the Samurai Action Genre" details using public **alpha/beta demos as live playtest telemetry** to re-align development — the game's famously tight feel came from instrumented public testing, not just internal QA (Game Developer, https://www.gamedeveloper.com/design/at-gdc-2017-you-ll-hear-how-the-i-nioh-i-devs-revamped-samurai-action-games). 12-year development, three full remakes (OpenCritic/Denfaminico via https://opencritic.com/news/12526/nioh-producer-says-he-wouldve-been-fired-if-he-wasnt-his-own-boss-due-to-games-12-year-dev-time).
- **Rendering/perf posture:** Nioh shipped with player-selectable **Action Mode (60fps)** vs **Movie/Graphic Mode (high resolution)** on console — a deliberate "player controls the perf budget" philosophy rare on console at the time (MCV interview, https://mcvuk.com/business-news/when-dark-souls-met-ninja-gaiden-team-ninja-talks-nioh/).
- **Modding surface:** effectively **none official**. No public SDK, no documented archive formats found in public sources. The PC modding that exists is save-editors and cosmetic texture swaps traded on Nexus/Steam forums (Steam forums passim). **No QuickBMS scripts, no unpackers, no format docs surfaced in public search** — treat this as a gap, not a finding.
- **Save data (PC):** Koei Tecmo titles store saves under `Documents\KoeiTecmo\NIOH\Savedata\<SteamID>\` (observed on Nioh 2's Nexus save mods, https://www.nexusmods.com/nioh2/mods/95 — Nioh 1 path is analogous; verify at pull time).

**[AWAITS FILE PULL]:** everything below needs the actual Steam install.

---

## 5. Extraction plan (for when Steam access exists)

Context: user owns Nioh: Complete Edition on Steam. This VM has no Steam credentials, so no pull was attempted or faked.

1. **Acquire:** install SteamCMD on a credentialed machine, `app_update 485510` (Nioh: Complete Edition app ID — verify at pull time via SteamDB/store page; do not hardcode blindly). Expected footprint ~80GB.
2. **Inventory first:** list the install tree (`nioh.exe`, data dirs). Koei Tecmo PC titles typically ship large packed archives; enumerate extensions and sizes before touching anything. Record the tree into `docs/research/NIOH-FILE-INVENTORY-<date>.md`.
3. **Priority extraction targets** (structure/technique only — no lore content leaves the lab):
   - **Skill-tree data:** per-weapon/ninja/onmyo skill definitions, unlock costs, dojo gates → maps to HMW per-fighter technique unlock tables.
   - **Stat/weapon scaling tables:** the damage formulas behind the GameFAQs scaling grades (B+/C+/D+) → reference for WH's own stat→move scaling.
   - **Guardian Spirit definitions:** passive-bonus schema, Living Weapon parameters (Might/Action/Recovery/Tenacity), element-pair combination rules → schema reference for WH's soul-companion system (WH content only).
   - **Mission/region tables:** mission lists, unlock conditions, reward tables, compendium-entry unlock mapping → template for HMW campaign data schema.
   - **UI/menu assets:** skill-tree UI, blacksmith UI, compendium UI — layout/technique reference for WH's own menus (WH already has a "menus from teardowns" law; Nioh's dense RPG menus are a second reference pole next to Tekken's).
   - **Animation data:** stance animation sets per weapon (NOT to reuse — Team Ninja's animation *organization*: how 3 stances × N weapons are stored and blended).
   - **Compendium text format:** how entries are stored/structured (the information-architecture template for WH's canon compendium).
4. **Tooling:** no official tools exist. Plan: binary reconnaissance (file headers, `strings`), then write format notes; check community (Nexus Nioh discords, Steam guides) for any unpacker that appears after this doc's date. If archives resist, fall back to **black-box documentation** (record observable behavior + UI text via screenshots) — still valuable for systems design.
5. **Where assets land in WH repo:** NOT in the game repo as-is. Research derivatives go to `docs/research/` (this file's siblings); any extracted *schemas/templates* (rebuilt, WH-canon-filled) go under the appropriate system design docs. Never commit Nioh's copyrighted assets, text, or lore to the repo.
6. **Legal note:** the user owns the game; extraction is for interoperability/research of systems structure. Do not redistribute extracted assets. This matches the project's standing "game ownership = authorization to pull" rule, with the same constraint applied to other owned titles.

---

## 6. Mapping to Heart and Mind Within (HMW)

HMW = per-character 3D beat-'em-up story campaigns (Tekken 5 Devil Within model). Nioh's systems map to HMW as follows — **structure only, WH canon content**:

| Nioh system | HMW application |
|---|---|
| Region map → mission select | Campaign chapter map per fighter (Five Lands regions, WH-canon) |
| Main / Sub / Twilight / Dojo mission types | Story missions / side stories / rotating challenge missions / dojo trials that gate technique unlocks |
| Dojo missions gate skill tiers | Each fighter's canon techniques unlock via in-world trials, not menus |
| Shrine hubs (level, skills, respawn) | Chapter hubs (WH-canon equivalent — e.g. Trial gates) for build management between missions |
| Kodama blessings per region | Collectible WH spirits granting per-chapter boons (WH-canon entities) |
| Compendium entries unlocked by missions | WH canon codex (Nine Souls, Tong-Nou, Trial lore) unlocked by campaign progress — same info architecture (§3.1) |
| NG+ difficulty cycles | Campaign replay tiers with remixed enemy layouts |
| The Abyss (999-floor gauntlet) | Endless gauntlet mode per fighter — the HMW endgame tail |
| 8 stats × 4 payoffs | HMW fighter progression: one XP pool feeding move unlocks, defensive traits, and gear perks simultaneously |
| Guardian Spirit + Living Weapon | Per-fighter soul-companion (WH-canon soul) granting passive build bonuses + a transformation super; pair-combination rules for tag/team modes |
| Soul Match / Reforge / Temper / Refashion | HMW gear/loadout crafting: keep favorite loadouts competitive (Soul Match), tune move properties (Temper), looks decoupled from stats (Refashion) |
| Builds save slots (Nioh 2) | Named HMW loadouts: gear + stats + skill choices, switchable between missions |
| Stance system (High/Mid/Low) | Design reference for per-fighter stance depth: 3 stance behaviors per weapon/move-set with distinct risk/reward, stance-cancel routing for advanced play |

**Explicitly NOT transferred:** any Nioh creature, spirit, person, place, plot beat, term (Amrita, Ki, Yokai, etc.), or text. WH's canon vocabulary (Nine Souls, Tong-Nou, Trial, Oversoul…) fills every slot above.

---

## 7. Sources

Public sources only; no game files were accessed.

- Stats & leveling: https://www.polygon.com/nioh-guide/2017/2/3/14500664/stats-level-up-body-heart-stamina-strength-skill-dexterity-magic-spirit-weapons-presige-skill-points/
- Stat scaling & equipment: https://Gamefaqs.gamespot.com/boards/222766-nioh-complete-edition/74970134
- Stat soft caps & skill-point economy: https://gamefaqs.gamespot.com/boards/181161-nioh/74987933
- Skill-point acquisition (Nioh 1 vs 2): https://pastebin.com/yTMRVJYC
- Maxing skill trees: https://steamcommunity.com/app/485510/discussions/0/3122659822732475759/?l=koreana
- Guardian Spirits & Living Weapon: https://nioh.wiki.fextralife.com/Spirit+Guardians
- Stances & Ki Pulse: https://blog.playstation.com/2020/03/11/survive-nioh-2s-opening-hours-with-9-gameplay-tips/
- Stance details: https://nioh2.wiki.fextralife.com/High+Stance
- Combat overview (stances, skill trees, Ki): https://www.lp.zone/t/nioh-pulsing-ki-like-its-1600/586
- Blacksmith (Soul Match/Reforge/Temper/Refashion): https://nioh.fandom.com/wiki/Blacksmith
- Build crafting endgame: https://gamefaqs.gamespot.com/ps4/222933-nioh-bloodsheds-end/faqs/75964
- Upgrade FAQ: https://nioh.wiki.fextralife.com/FAQ
- Mission lists: https://samurai-gamers.com/nioh/
- Regions & mission categories: https://nioh.fandom.com/wiki/Category:The_Way_of_the_Samurai
- Main missions & entry unlocks: https://nioh.fandom.com/wiki/Main_Missions
- Dojo missions: https://nioh.fandom.com/wiki/Dojo_Missions
- Official manual (mission types): https://www.gamecity.ne.jp/manual/t2wNiSht/steam/usa/4000.html
- Twilight/NG+ structure: https://fuzionbyte.com/nioh-omi-region-missions/
- NG+ region unlocks & skins: https://steamcommunity.com/app/485510/discussions/0/1519260397797949415/
- Yokai compendium entries: https://nioh.wiki.fextralife.com/Yokai
- Kodama & blessings: https://samurai-gamers.com/nioh/kodama-explained-nioh/ and https://nioh.wiki.fextralife.com/Kodama
- Hut (appearance, builds, illustrations): https://gamefaqs.gamespot.com/ps4/241160-nioh-2/faqs/78230/hut
- Nioh 3 appearance/transmog: https://www.polygon.com/nioh-3-change-appearance-transmog-how-to/
- Gameplay loop summary: https://alchetron.com/Nioh
- Engine lineage dispute: https://en.wikipedia.org/wiki/Talk:Katana_Engine
- Proprietary engine (Nioh 3): https://wccftech.com/roundup/nioh-3-everything-we-know-about-team-ninjas-supernatural-action-rpg/
- GDC 2017 dev talk: https://www.gamedeveloper.com/design/at-gdc-2017-you-ll-hear-how-the-i-nioh-i-devs-revamped-samurai-action-games
- Action vs Graphics mode: https://mcvuk.com/business-news/when-dark-souls-met-ninja-gaiden-team-ninja-talks-nioh/
- 12-year development: https://opencritic.com/news/12526/nioh-producer-says-he-wouldve-been-fired-if-he-wasnt-his-own-boss-due-to-games-12-year-dev-time
- Nioh 2 save path (Nexus): https://www.nexusmods.com/nioh2/mods/95

---
*End of doc. Lore firewall restated: structure and technique only. WH canon fills every slot.*
