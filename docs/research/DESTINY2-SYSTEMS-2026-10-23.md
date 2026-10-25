# Destiny 2 — Game Systems Research for Western Heart
**Date:** 2026-10-23
**Steam App ID:** 1085660 (free-to-play)
**Status:** ⚠️ PUBLIC-SOURCE RESEARCH ONLY — NO Steam file pull was possible in this session (subagent has no Steam client, no game install, no asset access). Every substantive claim below is cited to a public source (Destinypedia/D2 Wiki, Bungie Help, Bungie dev talks, community wikis, press). Nothing below is inferred from game files or presented as extracted data. Anything marked [AWAITS FILE PULL] is what still needs the actual Destiny 2 install on the credentialed machine.

---

## Owner instruction (verbatim)

> *"Destiny 2: character customization and depth and world building"*

---

## Section 0: What Destiny 2 is

Destiny 2 (Bungie, launched 2017, free-to-play on Steam as app 1085660) is a "shared-world shooter" — a first-person sci-fi universe spanning the solar system in which players are Guardians (one of three classes: Titan, Hunter, Warlock; one of three origins: Human, Awoken, Exo), pursuing a live-service loop of story campaigns, raids, dungeons, strikes, PvP, and patrol activities. Its customization depth is not in the face creator but in its layered systems: Armor 2.0 stats/mods, Armor Synthesis (transmog), a 250+ shader library, and a modular subclass system (3.0 Aspects/Fragments, plus Prismatic). Its world-building is a masterclass in art direction — a "mythic sci-fi" universe built on the theme "nature ascendant over lost human civilization" with a deliberately limited, aged color palette.

---

## 1. Character customization

### [RESEARCHED]

**1a. The base character creator — shallow, deliberately.**
- At character creation a Guardian picks: class (Titan/Hunter/Warlock), origin (Human, Awoken, Exo — locked forever), body type, face, hair/head, and markings. That is the complete set.
- Bungie itself confirms the recustomization feature (added ahead of The Final Shape, 2024) lets players "change the body type, face, hair/head, and markings" anytime for free — but "it won't be possible to change from one origin to another (i.e., Human, Exo, or Awoken)."
  - Source: https://www.bungie.net/en/Forums/Post/257432690 ; https://theloadout.com/destiny-2/character-customization-update ; https://primagames.com/gaming/how-to-customize-your-guardians-appearance-in-destiny-2-race-body-type-and-more
- **Key insight for WH:** Bungie barely invests in the face creator. The real customization identity of a Guardian is almost entirely *gear* (armor/shaders/ornaments). Faces are hidden under helmets most of the time — Bungie's cinematic director Jimmie Myers even had to publicly remind players to turn the "helmet off" option on to see faces in The Final Shape cinematics.
  - Source: https://dotesports.com/destiny/news/with-the-final-shapes-face-rework-its-finally-time-to-leave-your-destiny-2-helmet-at-home

**1b. The class silhouette system — three reads at a glance.**
- Bungie's GDC 2013 character-design talk established hard silhouette rules: the Titan reads as a V-shape (80% armor / 20% cloth); the Warlock reads as an inverted V (20% armor / 80% cloth, long robes); the Hunter sits in the middle (50/50, hood + improvised tech).
  - Source: https://mp1st.com/news/destiny-bungie-reveals-brave-new-worlds
- **WH pull:** silhouette-first class identity. Fighters should be readable at a distance by silhouette ratio, not just texture.

**1c. Armor sets — the REAL customization layer (visual + mechanical).**
- Armor has 5 slots (helmet, gauntlets, chest, legs, class item). The visual shape of armor is where Guardian identity lives.
- Armor 2.0 (Shadowkeep, 2019): each armor piece rolls 6 stats — Mobility (sprint/jump), Resilience (shield HP), Recovery (health regen speed), Discipline (grenade cooldown), Intellect (super cooldown), Strength (melee cooldown). Masterworking grants +2 to all stats per piece.
  - Source: armor-stat descriptions via https://www.bungie.net/en-us/Forums/Post/264514981?sort=0&page=0 (community-sourced guide mirrors at multiple domains corroborate the six-stat list)
- Armor mods slot into pieces and consume energy (Arc/Solar/Void/Stasis affinity) — cooldowns, damage resist, weapon synergy. Mods are per-slot with an energy budget (masterwork raises it to 10).
- Exotics (one weapon + one armor at a time) carry unique game-changing perks and custom geometry — the "hero piece" of a build.

**1d. Armor Synthesis (transmog) — the structural masterpiece.**
- Introduced Season of the Splicer (2021). Ada-1's Loom converts any armor appearance in the player's Collections into a permanent **Universal Ornament** for that slot/class, applied to any Legendary armor — appearance fully decoupled from stats.
- Currencies: Synthweave (Plate=Titan, Strap=Hunter, Bolt=Warlock, Template=universal), capped at 15 per class; Synthstrand → Synthcord loop via Ada-1 bounties.
- Appearance Customization screen (top-right of character screen) holds shaders + ornaments per slot; outfits savable as **Loadouts**.
- **Critical structural lesson:** *appearance and stats are separate data tracks.* Ornament = mesh/geometry reference; shader = color/material; armor piece = stats/mods. They combine at render, never baked together.
  - Sources: https://d2.destinygamewiki.com/wiki/Armor_Synthesis ; https://d2.destinygamewiki.com/wiki/Transmog ; https://help.bungie.net/hc/en-us/articles/360059413251-Armor-Synthesis-Guide ; https://www.thegamer.com/destiny-2-transmog-synthweave-guide/ ; https://gamerempire.net/?p=53716

**1e. Shaders — material-assigned color channels, not paint.**
- A shader is a 4-color (sometimes with a texture on one channel) palette item applied per armor piece (or all-at-once for 2,500 Glimmer; 500 per piece). Since Season of the Splicer, shaders are infinite-use once unlocked; applying costs Glimmer only. ~250+ shaders exist in collections.
- Community reverse-observation (widely corroborated): shader colors are assigned to *materials* per armor piece (metals get channel X, fabrics get channel Y, accents get channel Z), and each armor piece rotates which channels map where — which is why the same shader looks different on different armor, and the icon's 4 wedges (top=primary, right=secondary, bottom=tertiary, left=detail) don't always predict results. This is player-observed behavior, not official Bungie documentation.
  - Sources: https://spuf.org/2020/12/04/destiny-2s-shaders-just-dont-seem-right/ ; https://www.bungie.net/en-us/Forums/Post/259418040?sort=0&page=0 ; https://destiny.fandom.com/wiki/Shader
- **WH pull:** shaders are exactly the right architecture for WH's creation-suite recolors — per-piece material-channel palettes (metal/fabric/accent/detail) instead of per-pixel paint. Infinite-use-unlock + small apply cost is a proven economy.

**1f. Where the depth actually lives.** Face creator: shallow. Gear layers: deep (armor sets × exotics × ornaments × 250+ shaders × class silhouette rules). Bungie's bet is that players express identity through *equipment systems with stat meaning*, not through a face slider.

### [AWAITS FILE PULL]
- Actual shader definitions (per-channel material mapping tables, texture references) — need the game files to see how a shader asset is structured (color channels × material masks).
- Armor geometry + material-slot assignments (which material channel each mesh region uses).
- The Armor Synthesis data model (how Collections → ornament unlock records are stored).
- Class-item geometry and the helmet-on/off cinematic flag implementation.

---

## 2. World building

### [RESEARCHED]

**2a. The Director — the map IS the game.**
- The Director is the destination-select map screen: every Destination (Tower, EDZ, Cosmodrome, Nessus, Dreaming City, Moon, Europa, Throne World, Neomuna, Pale Heart, Kepler…) appears as a node with landing zones, activity icons, and real-time public-event timers. Since the D2 redesign, players fast-travel directly between landing zones on the map with ~10s loads — orbit is rarely visited.
  - Sources: https://help.bungie.net/hc/en-us/articles/45946334996756--7-Understanding-The-Director-World-Screen ; https://www.polygon.com/2017/8/24/16186764/destiny-2-pre-review-impressions-earth-patrol-lost-sectors-adventures
- **WH pull:** a Director-style hub map for WH's game modes (arcade ladder, story chapters, training lab, online) with live status icons and instant landing-zone travel would directly answer the user's menu complaints (menus from teardowns, touch targets).

**2b. Patrol Zones — mixed instancing as the design unit.**
- Terminology (D2 Wiki): *Sectors* are subdivisions that are either **open-world** (multiple fireteams coexist freely) or **instanced** (each fireteam gets its own copy). *Patrol Zones* = playable portions of a location containing a mix of both — host to Patrols, Adventures, Public Events, Lost Sectors, Strikes. *Social Spaces* = safe third-person vendor hubs (the Tower). *Mission Areas* = instanced maps for specific activities (all Crucible maps are Mission Areas).
  - Source: https://d2.destinygamewiki.com/wiki/Lost_Sector (via Destinations page: https://d2.destinygamewiki.com/mediawiki/index.php?title=Destinations&oldid=34818&mobileaction=toggle_view_mobile&printable=yes)
- Solo and multiplayer share the same geography: you walk into a patrol zone alone and other fireteams are just *there*, doing the same space. Matchmaking is ambient, not menu-driven.

**2c. Public Events — ambient multiplayer without a lobby.**
- Public Events spawn on timers shown live on the Director map; anyone in the zone can join mid-event. Heroic versions trigger via hidden mechanics (e.g., specific objective sequences), rewarding mastery knowledge. They scale participation: a solo player can contribute, a crowd completes faster.
  - Sources: Polygon preview (timers on map, congregation design): https://www.polygon.com/2017/8/24/16186764/destiny-2-pre-review-impressions-earth-patrol-lost-sectors-adventures ; Bungie Help on destination rewards/tiers: https://help.bungie.net/hc/en-us/articles/45946334996756--7-Understanding-The-Director-World-Screen
- Community feedback consistently says open-world seasonal activities embedded *in patrol zones* (Contact, Seraph Towers) felt the most alive — "immersion and a living world… shared purpose and community" — versus isolated activity nodes.
  - Source: https://www.bungie.net/en-ph/Forums/Post/265015687?sort=0&page=0
- **WH pull:** the "spaces feel alive" technique = shared geography + scheduled ambient events + visible timers. WH's hub/lobby could run scheduled ambient content (arcade challenges, community fight nights) on a visible clock.

**2d. Lost Sectors — hidden instanced dungeons in open space.**
- Lost Sectors are instanced mini-dungeons tucked into patrol zones, marked by a subtle in-world symbol + map icon; loop-back path to entrance; boss guards a cache chest; re-enterable for re-farmed rewards. Higher-difficulty Legend/Master variants became the solo endgame Exotic farm.
  - Source: https://d2.destinygamewiki.com/wiki/Lost_Sector
- Design pattern: *discovery in the open world, challenge in the instance.* The entrance is public; the content is private.

**2e. Art direction pipeline — "mythic sci-fi" as a system.**
- GDC 2013 ("Brave New World", Christopher Barrett + Joe Staten): Destiny started as traditional fantasy (wizards, grub lords, giant frogs), then fused fantasy with sci-fi — "What does a buried tomb look like next to a sci-fi setting? What does gold look like next to an assault rifle?" Hundreds of visual "touchstones" converged on one anchor image (cloaked soldier + white space tiger; codename "Tiger").
  - Source: https://www.polygon.com/2013/3/28/4158618/destiny-bungie-gdc-concept-art/ ; https://www.gamedeveloper.com/design/video-bungie-s-world-of-i-destiny-i-from-concept-to-production
- Unifying rules the team could follow: (1) **limited, slightly-aged color palette** — futuristic elements given a feeling of history, non-traditional palettes; (2) **theme: "nature ascendant over lost human civilization"**; (3) **mystery at the intersection of expected and unexpected** — familiar first, then strange (abandoned aircraft cemetery full of alien soldiers; frozen city of machines).
  - Source: https://80.lv/articles/world-building-and-art-direction-of-destiny
- Technical enablers: heavy post pipeline — LUT color correction, vignette, tone mapping, chromatic aberration, light streaks, full-screen bloom — with artists iterating in-engine in real time.
  - Source: https://80.lv/articles/world-building-and-art-direction-of-destiny
- Influences: Tarkovsky (Solaris/Stalker), Terry Gilliam's Time Bandits, '70s sci-fi art (John Harris, Beksinski, Gric), anime, sculptors Takeya/Yokoyama.
  - Source: https://www.polygon.com/2013/3/28/4158618/destiny-bungie-gdc-concept-art/
- **WH pull:** this maps directly onto WH's art-direction work (the user's "visual art direction bible"): define the *theme* first (WH: psychedelic/ontological Buddhist/Hindu + Eastern Mind cosmology), derive a *limited palette*, enforce *silhouette rules*, and build the *post pipeline* (LUTs, bloom, tone mapping) as the unifying layer — not hand-painted per-arena work. Note WH's existing arena law (upgrade quality, preserve colors) is the same instinct as Bungie's "aged palette" discipline.

### [AWAITS FILE PULL]
- Tiger Engine specifics (sector/instancing tech, streaming, LOD) — no public Tiger Engine documentation found; Bungie keeps engine internals private.
- Skybox/lighting rigs per destination (how each patrol zone's distinct look is composed: LUT + light rig + fog).
- Public event spawn/scale logic and Director map data format.
- Actual shader/sky material assets.

---

## 3. Depth systems

### [RESEARCHED]

**3a. Power level — a 4-band progression ladder.**
- Overall Power = average of equipped gear Power + seasonal artifact bonus. Four bands: **Floor** (new characters start here; expansions raise all gear to it) → **Soft Cap** (any drop upgrades) → **Powerful Cap** (only Powerful rewards upgrade) → **Pinnacle Cap** (only Pinnacle rewards upgrade; the hard cap). Caps rise each season; floor rises per expansion.
  - Source: https://d2.destinygamewiki.com/wiki/Power_Level ; https://arcader.org/news/destiny-2-power-level-guide-all-caps-and-powerful-and-pinnacle-gear-sources-explained/
- Seasonal Artifact: account-wide item granting *uncapped* bonus Power from XP (resets each season). Effective power = gear average + artifact bonus; artifact bonus doesn't affect drop power.
  - Source: https://d2.destinygamewiki.com/wiki/Power_Level
- Since The Final Shape: **Power Leader / Adjusted Power** — in a fireteam, lower players are auto-raised to 5 below the highest member, removing the grind gate for endgame participation.
  - Source: https://arcader.org/news/destiny-2-power-level-guide-all-caps-and-powerful-and-pinnacle-gear-sources-explained/
- **WH pull:** WH's rank ladder (the user's 53-tier system) is the analog of Power bands — soft/pinnacle-style gating on *rank climb* (e.g., rank floors, promotion series) plus a catch-up mechanic like Adjusted Power for friends joining late.

**3b. Seasonal Artifact mods — the rotating meta grid.**
- Each season's artifact carries a grid of ~25 mods (anti-Champion mods, economy mods, build-enabling perks). Unlocking costs glimmer; the grid is the season's buildcrafting vocabulary and rotates every ~3 months, forcing meta refresh without rebalancing every gun.
  - (Structural description corroborated across the power-level and artifact sources above; exact current-season grid contents rotate and were not catalogued here — needs file/API pull for specifics.)

**3c. Subclass 3.0 — the modular ability system.**
- Structure (rolled out Stasis → Void 3.0 → Solar 3.0 → Arc 3.0 → Strand): each subclass = **Super** (pick 1 of several) + **class ability** + **movement mode** + **melee** (pick of several) + **grenades** (universal pool — any class can use any grenade of that element) + **2 Aspects** (class-specific, build-defining perks; each grants a fixed number of Fragment slots, shown as pips) + **Fragments** (class-agnostic minor passives; can carry stat trade-offs like +10 Recovery / −10 Discipline).
  - Sources: https://www.Thegamer.Com/destiny-2-solar-rework-aspects-fragments-keywords/ ; https://www.ggrecon.com/guides/destiny-2-arc-3-0/ ; https://etapoena.pages.dev/post/weve-seen-void-30-and-its-going-to-change-destiny-2-buildcrafting-forever-8n7ym/ ; https://www.gameslearningsociety.org/wiki/how-do-you-unlock-3-0-fragments/
- Design rule: Aspects are *class identity* (only 2 of ~3 equipped; they define the playstyle); Fragments are *seasoning* (many small passives, stat costs create trade-off tension).
- Keywords system: each element has named buffs/debuffs (e.g., Arc: Amplified/Blind/Jolt; Solar: Cure/Radiant/Scorch/Ignite; Void: Devour/Invisibility/Weaken/Volatile) — a shared vocabulary so Fragments, Exotics, and mods can all key off the same verbs.
  - Source: https://www.ggrecon.com/guides/destiny-2-arc-3-0/

**3d. Prismatic — the fusion layer (The Final Shape, 2024).**
- Prismatic lets players equip abilities, Aspects, and Supers from *all five* damage types (Arc/Solar/Void/Stasis/Strand) in one subclass — a curated cross-element pool (not everything; Bungie adjusted some Aspects to enable new interactions). New **Facets** (Prismatic-only Fragments) explicitly reward mixing: e.g., Facet of Dominance (Void grenades Weaken, Arc grenades Jolt), Facet of Balance (Light kills→melee energy, Darkness kills→grenade energy).
- **Transcendence**: dealing Light damage fills a Light meter, Darkness damage fills a Dark meter; when both fill, Transcendence grants ability regen + weapon damage + damage resist and replaces the grenade with a class-specific dual-element Prismatic grenade. Kills while Transcendent extend it.
  - Sources: https://d2.destinygamewiki.com/wiki/Prismatic ; https://www.gamespot.com/articles/destiny-2-the-final-shape-new-prismatic-subclass-fuses-light-and-darkness-for-the-first-time-ever/1100-6522514/ ; https://thenerdstash.com/destiny-2-prismatic-subclass-full-guide/ ; https://patchtracker.gg (Dev Insights: Prismatic Deep Dive, cited in search results)
- Bungie explicitly calls Prismatic "this advanced subclass where you have more buildcrafting options, more potential combinations, more Fragments than you normally get, and more Fragment slots to socket them" — gameplay feature lead Sam Dunn.
  - Source: https://www.gamespot.com/articles/destiny-2-the-final-shape-new-prismatic-subclass-fuses-light-and-darkness-for-the-first-time-ever/1100-6522514/
- **WH pull:** this is the single most mappable system. WH's per-fighter customization = subclass structure: Aspects ↔ signature traits/stances (2 build-defining picks), Fragments ↔ small passive perks with stat trade-offs, Keywords ↔ shared combat verbs (launch, crumple, wall-splat…), Prismatic ↔ cross-style fusion fighters (Zen's Dural+Twelve+canon kit is literally a Prismatic build). Even Transcendence maps: a dual-meter super state filled by dealing two damage types.

**3e. Buildcrafting as a whole — the layer stack.**
1. Subclass (Aspect/Fragment/keyword verbs) → 2. Armor stats (6 stats → cooldown/regen economy) → 3. Armor mods (energy-budgeted slots) → 4. Weapons + weapon perks → 5. Exotic armor (one build-around) → 6. Artifact mods (seasonal vocabulary) → 7. Appearance (ornament/shader/loadout, zero stat impact). Seven independent layers, each with its own economy, none invalidating the others.

### [AWAITS FILE PULL]
- Actual Aspect/Fragment/keyword data tables (names, effects, slot counts, stat deltas) — extractable from game files or the Bungie API (public API, no credential needed for definitions).
- Artifact mod grids per season.
- Armor stat-roll distributions and mod energy-cost tables.
- Keyword/verb master list (the full buff/debuff taxonomy).

---

## 4. Extraction plan for the credentialed machine

Destiny 2 is free-to-play on Steam (app 1085660) — install is ~100+ GB; plan disk accordingly. Note: the user has NOT yet authorized this pull (game-ownership rule: pull when the user says they own it or asks; D2 is F2P so install is trivially authorized once the user confirms they want the research lane opened).

1. **Install on the credentialed machine:** `steamcmd +app_update 1085660` or Steam client install. Confirm with user before the ~120GB download.
2. **Bungie API first (no game install needed):** api.bungie.net is public for *definitions* — pull DestinyInventoryItemDefinition for all shaders (color channel data), ornaments, Aspects, Fragments, artifact mods, armor mods. This alone answers most [AWAITS FILE PULL] items in sections 1 and 3. (API key via Bungie developer portal; read-only key suffices.)
3. **Game files (Tiger Engine packages):** extract shader/material definitions (channel→material mapping), armor mesh material-slot assignments, skybox/lighting rigs per destination, Director map data. Tooling: community Tiger research exists (check current state at pull time); do NOT redistribute extracted assets — research use only, consistent with the user's standing position on sourced assets (transform, don't ship rips).
4. **Target artifacts for WH:**
   - `shader_definition → {channels[4]: {color, material_mask, texture}}` — the template for WH's recolor system.
   - `aspect/fragment/keyword tables` — the template for WH's fighter-trait system.
   - `destination lighting rig (LUT + light rig + fog + post chain)` — the template for WH's arena art pipeline.
   - `Director map node schema` — the template for WH's mode-select hub.
5. **Deliverables:** parsed JSON of the above + a mapping doc (this file's Vision mapping section, updated with real field names).

---

## 5. Vision mapping — Destiny 2 → Western Heart

| Destiny 2 system | What it is | WH mapping |
|---|---|---|
| Armor Synthesis / Universal Ornaments | Appearance (mesh) fully decoupled from stats; any collected look becomes a reusable ornament per slot | **WH creation suite core law:** attire geometry, stats/moves, and colors are three separate data tracks that combine at render. Tripo/SmutBase models = "collections"; user picks = ornaments; Tekken base kits ladder behind as back-slot attires (already the user's ATTIRE ORDER 5-7 RULE — D2 proves the architecture) |
| Shaders (4 material channels) | Per-piece palette assigned to material channels (metal/fabric/accent/detail), infinite-use unlock + small apply fee | **WH recolor system:** replace per-model hand-painted variants with a shader library — 4-channel palettes (skin/cloth/metal/accent) applicable to any attire. Fixes the "which colorway" problem (e.g., Dorowani's 5 colorways) as data, not 5 models |
| Class silhouette rules (80/20, 50/50, 20/80) | Instant class readability at distance | **Fighter readability pass:** each WH fighter gets a silhouette ratio rule so they're distinguishable in motion, per the facing/side-switch fix work |
| Director map | Hub map with live activity icons, landing-zone fast travel, real-time event timers | **WH mode-select hub:** arcade ladder / story / Gungaku lab / online as Director nodes with live status (daily challenges, community fight nights) — built from teardown UI per the user's menus-from-teardowns law, touch-first per MOBILE INPUT LAW |
| Patrol zones (mixed open/instanced sectors) | Solo and multiplayer share geography; ambient matchmaking | **WH social hub/lobby:** fighters idle/train in a shared space; other players' ghosts walk by — no lobby menus needed |
| Public Events + Heroic triggers | Scheduled ambient co-op with hidden mastery mechanics, timers on the map | **WH live events:** scheduled in-hub events (boss rush, community challenges) on a visible clock; heroic variants for skilled players |
| Lost Sectors | Hidden instanced challenges inside open space; discovery public, content private | **WH secret content:** hidden arcade paths / bonus fights discoverable in-hub, instanced per player |
| "Mythic sci-fi" art pipeline | Theme → limited aged palette → silhouette rules → post chain (LUT/bloom/tone-map) as the unifying layer | **WH visual art direction bible:** same pipeline order — theme (psychedelic Buddhist/Hindu + Eastern Mind) → limited palette → silhouette → post chain per arena; this is *how* you kill the "blocky 3js prototype" look without hand-tooling each arena |
| Subclass 3.0 (Aspects/Fragments/Keywords) | 2 build-defining Aspects (with Fragment-slot pips) + many small Fragments with stat trade-offs + shared verb keywords | **WH fighter customization:** each fighter = 2 signature Aspects (stances/traits, e.g., Tentacle Mode, Oversoul) + Fragment-style minor perks with trade-offs (+damage/−defense); shared combat keyword verbs across the roster so perks/mods compose |
| Prismatic + Facets + Transcendence | Cross-element fusion pool; Facets reward mixing; dual-meter super state | **WH fusion fighters:** Zen (Dural+Twelve+canon) is a Prismatic build by design; Transcendence = dual-meter super state (e.g., fill Soul + Wrath meters → transformation). Facets = perks that only proc on mixed-style play |
| Seasonal Artifact grid | Rotating seasonal mod vocabulary; meta refresh without rebalancing everything | **WH seasonal balance:** a rotating perk grid per season keeps the meta fresh without touching every fighter's frame data |
| Power bands + Adjusted Power | Soft/Powerful/Pinnacle caps; fireteam catch-up to −5 below leader | **WH rank ladder:** promotion-series gating modeled on power bands; Adjusted-Power-style catch-up so friends can play ranked together |
| Buildcrafting layer stack (7 layers) | Subclass → stats → mods → weapons → exotic → artifact → appearance; independent economies | **WH build depth without complexity:** fighter kit → stat tuning → perk mods → signature gear → seasonal grid → appearance — same stack shape, each layer optional |

**The one-line takeaway:** Bungie's depth comes from *decoupled layers with independent economies* — never from one giant customization screen. WH should copy the architecture (appearance/stats/kit/mods as separate tracks that compose), not any single feature. And Bungie's world-building comes from *theme-first art direction + shared geography with scheduled ambient life* — the Director and patrol model is the proven answer to "how do spaces feel alive."

---

*Research compiled 2026-10-23 from public sources only. No game files were accessed; no Steam pull was performed. All [AWAITS FILE PULL] items require the credentialed-machine extraction plan in Section 4.*
