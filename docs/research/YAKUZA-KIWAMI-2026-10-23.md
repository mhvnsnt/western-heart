# Yakuza Kiwami (2016) — Brawler Systems Research for Heart and Mind Within

**Date:** 2026-10-23
**Owner instruction:** "Perfect for heart and mind within"
**Researcher:** DoggByte (subagent)
**Game:** Yakuza Kiwami (Legacy) — Ryu Ga Gotoku Studio / Sega. User owns it on Steam (account vil3m), 26.7 hrs played.
**Purpose:** Feed **Heart and Mind Within** (HMW) — WH's per-character 3D beat-em-up story campaigns, modeled on Tekken 5's Devil Within mode.

> **Research status:** This VM has **no Steam credentials**, so **no game files were pulled**. Nothing below is
> reconstructed from a fake pull. Section 1 is researched from public sources (each claim cited).
> Section 7 is a concrete extraction plan for the day Steam access exists. Anything that can only be
> settled by opening the game files is explicitly marked **[AWAITS FILE PULL]**.

---

## 0. Engine note (read this first)

Yakuza Kiwami (2016) does **not** run on the Dragon Engine. It runs on **Yakuza 0's engine** — the
pre-Dragon-Engine RGG engine — with Yakuza 0's graphics, engine, and combat system [S1][S2]. The first
Dragon Engine game was Yakuza 6 (2016); Kiwami 2 (2017) was the first Kiwami title on it, and "every
mainline entry starting from Yakuza 6 uses the polished Dragon Engine," while "2015's Yakuza 0 …
uses the old engine" [S3]. For teardown purposes this is good news: the old engine has the most
mature public modding tooling (Section 7). Steam PC release: February 19, 2019 [S1].

---

## 1. Beat-em-up combat systems (researched)

### 1.1 Four switchable styles

Kiryu has four fighting styles, all unlocked from the start, switched on the fly with the D-pad
[ S4][S5][S6]:

| Style | Role | Crowd-fight behavior |
|---|---|---|
| **Brawler** | All-rounder; most combos and options | Default crowd tool; has grab |
| **Rush** | Fast kickboxer; long weak combos, chained dodges/weaves, **no grab** | 1v1 / boss specialist — dodge-heavy |
| **Beast** | Slow, heavy hits, super armor; **auto-picks-up nearby objects mid-combo** | Mob specialist — grabs weapons/people as combo starters |
| **Dragon** | Starts nearly unusable (empty skill tree); becomes the strongest once leveled | Leveled via the Majima Everywhere system (§1.6) |

Skills learned in the Body/Soul/Tech trees (health / heat / abilities) include the ability to
**switch styles mid-combo**, which players compare to Devil May Cry 5's seamless switching [S6].
Skill points come from EXP earned in every fight; the Dragon tree levels only through Majima
Everywhere encounters [S6].

**HMW transfer:** mid-combo style switching is the single biggest depth mechanic to lift. For HMW
campaigns, give each protagonist a small set of switchable "forms" (Brawler-equivalent default,
a Rush-equivalent evasive form, a Beast-equivalent crowd form) with **switch-on-the-fly after
unlock**, rather than one flat moveset. This is exactly the "editable moveset library per fighter"
idea from the user's moveset-library directive, applied to brawler mode.

### 1.2 Input grammar

The base input grammar is consistent across styles: **Square = light attack** (combo strings),
**Triangle = heavy/finisher**, **Circle = grab** with style-specific outcomes (e.g. Beast throw
animations differ from Brawler's), **hold R1 = lock-on**, **L1 = reposition behind enemy**
[S7]. Players are explicitly taught *not* to mash: `Square→Triangle` and `Square→Square→Triangle`
knockdown sequences outperform mashing [S7]. Rush cannot grab at all [S7].

**HMW transfer:** lock the brawler input grammar to this small, fixed verb set
(light chain / heavy finisher / grab / lock-on / reposition). This mirrors the user's
input-to-move fidelity law — one input, one predictable move — instead of the "random-feeling"
mappings the playtest flagged.

### 1.3 Heat gauge, heat mode, heat actions

Fighting (dealing damage, grapples, charge attacks) fills a **heat gauge**; the gauge is spent to
execute **heat actions** — brutal context-sensitive finishers triggered by Triangle when a prompt
appears [S8][S9]. A maxed gauge ("Climax Heat Gauge") unlocks **Climax Heat Mode** [S10].
Heat actions are the fun core of the combat: arm-breaks to disarm gunmen, bicycle-over-the-head,
nails-in-the-mouth, wall slams [S8][S9][S11].

Heat actions are gated by **context conditions**, documented per-move in the Play Log [S12]:

- **Heat state:** some need base heat, some Climax heat, some a flashing-red (critical) health bar,
  some full health.
- **Enemy state:** downed enemy, grabbed enemy, enemy near a wall, enemy attacking (counter heat actions).
- **Environment:** street weapons in hand (weapon heat actions are largely style-agnostic; knuckles
  favor Rush, hammers favor Beast), terrain objects.
- **Positioning:** e.g. Rush wall-splat counters.

The game tracks every heat action performed in the Play Log; 40 are needed for full CP rewards
[S12]. Grab heat actions and weapon/terrain heat actions are unlocked via the skill grid ("Weapon &
Terrain essence") [S10].

**HMW transfer:** this is the template for HMW's **contextual finishers** — a heat meter that fills
from fighting, spent on finishers whose availability is a function of (enemy state × position ×
weapon × heat level). The Play Log tracking is also worth copying: a per-campaign "finisher log"
that rewards experimentation. Note the constraint discipline: heat actions never fire at random;
the prompt only appears when the context matches. That is the anti-randomness rule HMW fights need.

### 1.4 Boss healing vs. Kiwami moves (phase-break design)

New in Kiwami: during boss fights the enemy can **turtle up and start healing**. The counter is the
**Kiwami heat move**: the boss slumps with a **colored aura** — red = Dragon, blue = Brawler,
yellow = Beast, pink = Rush. Switch to the matching style color, with a full heat charge, and the
Kiwami move interrupts the heal and deals a large chunk of damage [S2][S13][S14]. The Kiwami moves
must be unlocked in the skill grid, which caused a documented difficulty wall at the early Shimano
funeral fight for players who hadn't unlocked the right one [S14].

**HMW transfer:** lift this as the **boss phase-break mechanic** for HMW campaigns. A boss that
heals unless the player reads a color-coded telegraph and answers with the matching form is a
readable, skill-based anti-turtle system — far better than a DPS race. The cautionary tale transfers
too: never gate the counter behind an unlock the player might not have at that boss.

### 1.5 Enemy AI and crowd-fight design

- **Role assignment in crowds.** When a fight starts, enemies take on distinguishable roles: one
  circles, one tries to grab from behind, one looks for a weapon (e.g. a bicycle) to throw [S15].
- **Attack pacing.** Enemies do not all attack at once; attacks come in a rotation that reads like a
  choreographed movie fight [S15]. Weapon users (rifle, sword, chainsaw) are priority threats the
  player is expected to deal with first [S16].
- **Grab counters.** Overusing grabs gets punished — enemies, especially bosses, start countering
  them [S7].
- **Bystander arena.** On street fights, bystanders run up and close in, **forming a fight arena**
  ring around the combat [S15]. The fight gets a stage without leaving the open city.

**HMW transfer:** the crowd-fight director for HMW is: (1) cap simultaneous attackers, (2) assign
visible roles (circler / grabber / weapon-seeker) so the crowd reads as individuals, (3) punish
grab spam with counters, (4) auto-form a bystander ring so street fights get arena framing for
free. Point (4) is cheap and high-value on mobile: no separate arena load, just crowd placement.

### 1.6 Lock-on and camera

Lock-on is **hold R1** to target enemies precisely (recommended especially for bosses) [S7].
The remake was specifically noted for its "much better camera than the original" PS2 game [S4].
Fights otherwise play in the open street with no arena transition — the camera frames the
bystander ring described above [S15].

**HMW transfer:** hold-to-lock soft targeting (mobile-friendly: a tap-toggle, not a hold), and a
camera that pulls back to frame the crowd ring rather than cutting to a separate arena.

### 1.7 Majima Everywhere (recurring-rival system)

Goro Majima ambushes Kiryu at scripted and random points all over Kamurocho — disguised, in
mini-games, mid-story — in ranked encounters that are the **primary XP source for the Dragon
style** [S2][S6]. It turns the whole city into a training system: the rival *is* the progression.

**HMW transfer:** a per-campaign "rival ambush" system — a recurring rival who jumps the player
across the hub map at escalating ranks, each win unlocking the protagonist's signature form
(Dragon-style equivalent). This is directly reusable for HMW's per-character campaigns.

---

## 2. City / world design (researched)

### 2.1 Kamurocho: dense, compact, real

Kamurocho is a fictional-but-faithful facsimile of Tokyo's Kabukichō — "right down to the curve
of certain streets and shop-front façades," rebuilt per-entry to track the real district's changes
[S17]. It is deliberately **compact**: "big enough to be convincing but small enough that
substantial portions of gameplay aren't spent chugging from point A to point B" — essential
because Kiryu "can't seem to walk a city block without being accosted by thugs" [S11].

**HMW transfer:** each HMW campaign hub should be **one dense district, not a big empty map**.
Density beats square footage, especially on mobile. One walkable district per character keeps
encounter pacing tight.

### 2.2 Zakkyo density (GDC 2025)

At GDC 2025 ("The Secret to Narrative-Driven and Short-Term Development in Like a Dragon"), RGG
designers explained the density trick: Kamurocho's **zakkyo buildings** — multi-tenant buildings
symbolic of Japanese city centers. Two advantages per design manager Eiji Hamatsu: "the visual
image of a glamorous entertainment district" and "the diversity of experiences that can be obtained
from multiple different shops crammed into a limited amount of space. In Kamurochō, moving across
one wall or ascending one flight of stairs can create a completely different scene or experience"
[S18].

**HMW transfer:** build HMW hubs vertically. One building = many scenes. Stairs/walls as scene
transitions is cheaper than new geometry and reads as density on a phone screen.

### 2.3 Asset/map reuse as emotional design (GDC 2025)

The same talk addressed the reused-Kamurocho question head-on: reuse works because locations
reappear "as a necessary part of telling the story," creating "the joy of revisiting a place
where a past story has left its mark" and "the satisfaction of coming back to a place where a
certain event occurred, but for a different reason" — accumulated stories turn revisits into
"meaningful encounters" [S19]. The freed-up resources go into new content [S19].

**HMW transfer:** this is the strongest city-design argument for HMW. With **per-character
campaigns**, WH should build **one shared set of hubs** (Tong-Nou locales) and run every
character's story through them. Each revisit lands differently because the story left its mark —
the GDC-verified version of "revisit with new eyes." This multiplies content per megabyte of map.

### 2.4 Streaming and loading (old engine)

On the old engine, the district itself streams as you walk, but **entering shops/interiors hits a
loading screen** — the seamless door-walkthrough only arrived with the Dragon Engine (Yakuza 6):
"walk up to a door and walk right through it rather than see a loading screen" was the noted new
thing [S20], and Dragon Engine games are described as having "very few loading screens … the
world is all connected," while "older titles like Yakuza 0" still have them [S21].

**HMW transfer:** interior loads are acceptable and era-authentic; keep HMW hubs streaming
seamlessly at street level and use short loads only at interior doors. No need to over-engineer
seamless interiors on mobile.

### 2.5 The living-street layer

Street encounters trigger constantly while walking [S11]; the Coliseum in West Park offers
structured arena combat with every street weapon available, which doubles as the place to practice
weapon heat actions [S12]; locker keys, hidden items, and food bonuses reward exploration [S22].

**HMW transfer:** ambient street encounters + one structured arena per hub (Coliseum equivalent)
covers both the "brawling while traveling" and "deliberate practice" needs.

---

## 3. Story-mode structure (researched)

### 3.1 Chapters

Kiwami has **13 chapters**, each varying in length [S23][S24]:

1. October 1, 1995: Fate of a Kinslayer · 2. December 5, 2005: 10 Years Gone · 3. Funeral of Fists ·
4. An Encounter · 5. Purgatory · 6. Father and Child · 7. The Dragon and the Koi · 8. The Scheme ·
9. The Rescue · 10. Shape of Love · 11. Honor and Humanity · 12. Reunited · 13. The End of Battle
[S24].

Chapter flow interleave: early chapters are **cutscene-heavy with chained boss fights** before the
city properly opens up (a documented pacing flaw — the long boss gauntlet before free roam)
[S14]. Main-story beats alternate with free-roam brawling; story completion runs ~20 hours,
average playthrough 33+, 100% ~82 hours [S24].

**HMW transfer:** chapter-gated campaign structure maps 1:1 onto HMW. The caution transfers too:
don't front-load a boss gauntlet before the player has their tools (the Shimano/Kiwami-move wall
[S14] is the exact failure mode to avoid).

### 3.2 Substories (side content)

**78 substories**, chapter-gated (e.g. Substory 1 requires Chapter 4) [S23][S25]. They range from
one-off gags to **multi-part chains** (the "Bump and Scam" saga runs 17→20 across four linked
entries) [S25]. Missable ones can be cleaned up in **Premium Adventure** — post-story free roam
[S23]. New Game Plus carries abilities, EXP, money, CP, and completion — **but not substories**,
which must be finished in a single run [S24].

**HMW transfer:** substory architecture for HMW = chapter-gated side missions, some chained
across 3–4 parts, tracked in a completion list, with a post-campaign free-roam mode for cleanup.
The "substories don't carry over" rule is a retention mechanic worth copying deliberately.

### 3.3 Supporting structure

- **Play Log / Completion List** tracks everything (heat actions performed, substories, minigames)
  [S12][S22].
- **Climax Battles**: post-game gauntlet challenges from the main menu (e.g. Proving Ground 1–6
  with fixed loadouts and constraints like "Rush only, can't get hit") [S22][S16].
- **Coliseum tournaments** at West Park feed both story (paintings for Komaki's training) and
  combat mastery [S2].
- **Minigames** (karaoke, pocket circuit, mahjong, batting, darts, MesuKing…) are the pacing
  valves between story beats [S22].

**HMW transfer:** per-campaign completion list + post-campaign gauntlet mode (Climax-Battle
equivalent with fixed-constraint challenges) gives HMW endgame legs without new story content.

---

## 4. HMW technique map (every transfer in one place)

| # | Yakuza Kiwami technique | Transfers to HMW as |
|---|---|---|
| 1 | Mid-combo style switching (Brawler/Rush/Beast) | Switchable combat forms per protagonist, unlocked progressively |
| 2 | Fixed input grammar (light chain / heavy finisher / grab / lock-on / reposition) | Brawler-mode input law — one input, one predictable move |
| 3 | Heat gauge + context-gated heat actions | Contextual finishers: heat meter spent only when (enemy state × position × weapon) matches |
| 4 | Kiwami aura-match boss phase-break | Color-telegraphed boss heal-break; never gate the counter behind a missable unlock |
| 5 | Crowd role assignment + attack rotation + grab-spam counters | Crowd-fight director: capped simultaneous attackers, visible roles |
| 6 | Bystander ring forms the arena | Free arena framing for street fights — no arena load |
| 7 | Majima Everywhere rival ambushes | Recurring-rival system; rival fights = signature-form XP |
| 8 | Dense compact Kamurocho; zakkyo vertical density | One dense district per hub; build vertically, stairs as scene changes |
| 9 | GDC 2025: revisits as emotional encounters | **Shared hubs across all character campaigns** — story-marked revisits |
| 10 | Street streaming + interior loads | Stream streets, load interiors; don't over-engineer seamlessness on mobile |
| 11 | 13 chapters, cutscene↔fight interleave | Chapter-gated campaign skeleton |
| 12 | 78 chapter-gated substories, some chained | Side-mission architecture with multi-part chains |
| 13 | Premium Adventure + NG+ (substories don't carry) | Post-campaign free roam; deliberate retention rules |
| 14 | Climax Battles / Coliseum | Post-campaign gauntlet mode with fixed-constraint challenges |

---

## 5. What this research does NOT cover (be honest)

- Exact animation inventories (how many heat-action GMTs, their IDs/names) — **[AWAITS FILE PULL]**.
- Kamurocho map geometry, collision, encounter spawn tables — **[AWAITS FILE PULL]**.
- Enemy AI parameters (attack-slot counts, aggro radii, role weights) — only observed behavior is
  documented above; internals need the files or a debug build — **[AWAITS FILE PULL]**.
- Audio/voice pipeline (.cpk contents) — **[AWAITS FILE PULL]**.
- Tekken 5's Devil Within structure itself (the other half of the HMW reference) — separate
  research track, not this doc.

---

## 6. Legal / sourcing note

The user owns Yakuza Kiwami on Steam — per the standing game-ownership rule, that is authorization
to pull. The user's standing position: ripped assets are raw material to be **transformed heavily**
into WH's own characters/systems, not shipped as-is. This doc proposes extracting for
**study and reference** (animation timing, encounter design, city layout); any art that ships in WH
must be transformed per that position.

---

## 7. Extraction plan (execute when Steam access exists)

No files were touched on this VM. When a machine with the user's Steam library is available:

### 7.1 Tools (all public, verified)

| Tool | Purpose | Source |
|---|---|---|
| **ParTool** | Unpack/repack `.par` archives (drag-and-drop) | Yakuza modding community (Steam guide [S26]) |
| **RyuModManager (RMM)** | Load unpacked mods without repacking | Yakuza modding community (Steam guide [S26]) |
| **GMD Blender plugin** | Import/export `.gmd` skinned models (`File → Import → Yakuza GMD`) | Community plugin (Steam guide [S26]) |
| **yakuza-gmt-blender** (mosamadeeb) | Import/export `.gmt`/`.cmt`/`.ifa` animations; auto-detects version; retarget to other armatures | GitHub wiki [S27] |
| Paint.NET / GIMP + dds plugin | Edit `.dds` textures | Steam guide [S26] |

### 7.2 Exact paths (Steam install: `…\steamapps\common\Yakuza Kiwami\`)

- `media\data\chara\w64\adv\…` — **gameplay character models** (`mesh.par` per folder) [S26][S28].
- `media\data\chara\w64\auth\…` — **cutscene character models** (note: on Ultra settings the game
  uses `auth` models for gameplay too) [S26][S28].
- `media\data\motion\…` — gameplay animation `.gmt` files [S27].
- `media\data\hact\…` — heat-action / special animation `.gmt` files (import with "Is Auth/Hact"
  enabled) [S27].
- Textures ship as `.dds` alongside the `.gmd` inside each `mesh.par` [S26].
- `.cpk` archives — audio (guide covers editing .cpk; voice work comes later) [S26].

### 7.3 What to extract, in order

1. **Heat-action animation set**: all `.gmt` in `hact\` + weapon heat actions — the contextual-finisher
   reference (timing, camera cuts, hit-stop feel). Retarget samples to a WH rig via yakuza-gmt-blender
   to study timing curves.
2. **Style movesets**: Brawler/Rush/Beast base combo `.gmt`s from `motion\` — input-grammar reference.
3. **Kamurocho map geometry**: stage/field assets — density and blockout reference for HMW hubs.
4. **Boss Kiwami-move set**: the aura-match finishers — phase-break reference.
5. **Encounter/chapter scripts**: spawn tables and chapter gating — substory/chapter architecture reference.

### 7.4 Where assets land in the WH repo

- Research notes: `docs/research/yakuza-kiwami/` (timing analyses, screenshots, design notes).
- Extracted reference assets: **not** committed to the repo — per the standing rule, large files go
  to Releases/external storage, never local disk bloat. Keep a manifest (`ASSET-MANIFEST.md`) in the
  research folder pointing at the external archive.
- Transformed/proprietary derivatives only enter `customization/` or game dirs after heavy
  transformation, per the user's sourced-asset position (§6).

### 7.5 Verification after pull

For each extracted class: import into Blender via the plugins above, confirm the asset opens and
plays (animation) or renders (model/map), and log the verified inventory back into
`docs/research/yakuza-kiwami/`. Nothing is "pulled" until it opens cleanly.

---

## Sources

- [S1] Yakuza Kiwami — Yakuza Wiki: "the graphics, engine and combat system of Yakuza 0"; Steam release
  Feb 19, 2019. https://yakuza.fandom.com/wiki/Yakuza_Kiwami
- [S2] Yakuza Kiwami — Sega Wiki: "utilising the engine, graphics and combat engine from Yakuza 0";
  Kiwami aura-color boss mechanic; Majima Everywhere/Coliseum details. https://sega.fandom.com/wiki/Yakuza_Kiwami
- [S3] gameland.gg: "every mainline entry starting from Yakuza 6 uses the polished Dragon Engine.
  2015's Yakuza 0 … also uses the old engine." https://gameland.gg/is-the-next-like-a-dragon-game-yakuza-kiwami-3-devs-answer/
- [S4] ComingSoon Switch review: "using the Yakuza 0 engine"; "much better camera than the original."
  https://www.comingsoon.net/games/reviews/1869208-yakuza-kiwami-nintendo-switch-review
- [S5] GameRant combat ranking: four styles "offering different approaches depending on the enemy type,
  the number of enemies, and the environment." https://gamerant.com/yakuza-series-combat-systems-mechanics-best-worst/
- [S6] TheBaBlueprint: all four styles unlocked at start; Dragon tree leveled via Majima Everywhere;
  style-switching skills make combat "like Devil May Cry 5." https://thebablueprint.com/23935/game-on/game-on-yakuza-kiwami/
- [S7] "Beginner's Combat Guide to Yakuza 0" summary: hold R1 lock-on; Square→Triangle combos;
  Circle grabs with style-specific outcomes; L1 reposition; Rush can't grab; bosses counter grab spam.
  https://webscriptlab.com/JJNPpEdQMQ-youtube-summary/
- [S8] Cultured Vultures review: Brawler/Rush/Beast/Dragon roles; heat attacks. https://culturedvultures.com/?p=63538
- [S9] Rice Digital review: heat gauge unlocks stronger moves; Brawler/Rush/Beast properties; Beast
  auto-pickup. https://ricedigital.co.uk/yakuza-kiwami-review-like-dragon-ps4/
- [S10] NexusMods "Rebalancing Mod" docs: Climax Heat Gauge; grapples/charge attacks build heat;
  Beast super armor; heat-action healing. https://www.nexusmods.com/yakuzakiwami/mods/5?tab=docs
- [S11] Boston Phoenix: compact Kamurocho; constant street accosting; heat gauge and context-sensitive
  heat attacks. https://bostonphoenix.com/Boston/RecRoom/23431-YAKUZA/?rel=inf
- [S12] GameFAQs Heat Actions guide (CyricZ): per-move conditions (Climax/Critical/Full/weapon);
  Play Log tracking; 40 for CP; Coliseum as weapon source. https://gamefaqs.gamespot.com/ps4/181171-yakuza-kiwami/faqs/75194/heat-actions
- [S13] GameFAQs boards: boss slumps with colored aura at <50% HP; switch to matching style color;
  full heat charge required; interrupts healing. https://gamefaqs.gamespot.com/boards/181171-yakuza-kiwami/75720067
- [S14] Hardcore Gaming 101: bosses turtle and heal; Kiwami heat moves punish; early-game unlock wall
  at the Shimano funeral fight. http://www.hardcoregaming101.net/yakuza-kiwami/amp/
- [S15] Scientific Gamer (Yakuza 0, same engine): enemy role assignment (circler/grabber/weapon-seeker);
  bystanders form a fight arena ring; style-specific heat actions. https://scientificgamer.com/thoughts-yakuza-0/
- [S16] Steam "Climax Battles Tips" guide: enemy threat types (rifle/sword/chainsaw); Proving Ground
  constraints. https://steamcommunity.com/sharedfiles/filedetails/?l=schinese&id=1674631735
- [S17] NDA News / Game Informer via art director Nobuaki Mitake: Kamurocho as faithful Kabukichō
  facsimile, rebuilt per entry. https://au.nda.news/yakuza-st_14514/news/like-a-dragon-infinite-wealth-review-sprawl-over-density-sn_5423562/
- [S18] 80.lv on RGG's GDC 2025 session: zakkyo buildings — "moving across one wall or ascending one
  flight of stairs can create a completely different scene or experience." https://80.lv/articles/like-a-dragon-devs-on-the-effective-reuse-of-kamuroch-map-assets
- [S19] AUTOMATON on RGG's GDC 2025 session: revisiting story-marked locations as "meaningful
  encounters"; reuse frees resources for new content. https://automaton-media.com/en/news/like-a-dragon-cleverly-avoids-complaints-about-reused-assets-by-getting-players-emotionally-attached-to-its-recurring-locations/
- [S20] clickbliss (Yakuza 6): walking through doors "rather than see a loading screen" was the new
  thing — i.e. old-engine games load at interiors. https://clickbliss.net/post/172588835174/yakuza-6-makes-kamurocho-feel-like-a-new
- [S21] GameFAQs boards: Dragon Engine games have "very few loading screens … the world is all
  connected"; "older titles like Yakuza 0" still have them. https://gamefaqs.gamespot.com/boards/264564-xbox-series-x/80498903
- [S22] GameFAQs Kiwami FAQ (CyricZ): full guide TOC — chapters, substories by chapter, Majima
  Everywhere, Coliseum, Climax Battles, minigames, Play Log. https://gamefaqs.gamespot.com/ps4/181171-yakuza-kiwami/faqs/75194/faq
- [S23] Pro Game Guides: 13 chapters, 78 substories, Premium Adventure cleanup. https://progameguides.com/yakuza/how-many-chapters-and-substories-does-yakuza-kiwami-have/
- [S24] TheGamer: 13-chapter list; ~20h story / 33h+ average / 82h+ 100%; NG+ carries progress but
  not substories. https://www.thegamer.com/yakuza-kiwami-how-long-to-beat/
- [S25] Neoseeker substories: chapter requirements; "Bump and Scam" 4-part chain. https://www.neoseeker.com/yakuza-kiwami/walkthrough/Substories
- [S26] Steam guide "Small modding info-dump/guide — Yakuza Kiwami": ParTool unpack/repack .par;
  adv/auth model folders; mesh.par; GMD Blender plugin; .dds textures; .cpk editing.
  https://steamcommunity.com/sharedfiles/filedetails/?l=turkish&id=2813243580
- [S27] yakuza-gmt-blender wiki (mosamadeeb): GMT/CMT/IFA import/export; "Is Auth/Hact" for
  auth/hact folders; motion folder for gameplay anims; retargeting. https://github-wiki-see.page/m/mosamadeeb/yakuza-gmt-blender/wiki/Importing-Animations
- [S28] Steam Yakuza 0 modding info-dump: adv = gameplay models, auth = cutscene models; Kiwami
  assets compatible. https://steamcommunity.com/sharedfiles/filedetails/?id=1464174627&l=polish
