# Red Faction: Guerrilla — Geo-Mod 2.0 Environment Destruction Research
**Date:** 2026-10-23
**Status: PUBLIC-SOURCES ONLY.** No Steam file pull was performed and no game files were accessed for this report. Every technical claim below is sourced from publicly available interviews, developer talks/write-ups, wikis, and analysis pieces, each cited. Anything that requires the actual game binaries or data is explicitly flagged [AWAITS FILE PULL]. No claims have been fabricated to fill gaps.
**Owner instruction (verbatim):** *"Red Faction: guerilla : world and environment destruction"*
**Steam app IDs:** 20500 (Red Faction: Guerrilla, original 2009), 667720 (Red Faction: Guerrilla Re-Mars-tered, 2018 remaster by Kaiko)

---

## 0. What the game is

[RESEARCHED] Red Faction: Guerrilla (Volition/THQ, 2009; Re-Mars-tered remaster by Kaiko/THQ Nordic, 2018) is a third-person open-world shooter set on Mars. Its signature feature is the Geo-Mod 2.0 engine: a physics-based, real-time structural destruction system in which nearly every man-made structure can be damaged, stressed, and collapsed through genuine simulation rather than scripted sequences. It is widely cited (e.g., by The Finals' developers) as the reference implementation of structural destruction in games. Sources: https://gmtk.substack.com/p/how-games-do-destruction, https://www.redfactionwiki.com/wiki/Geomod

---

## 1. Geo-Mod 2.0: How the destruction actually works

### 1.1 The stress system (core extraction)

[RESEARCHED] The heart of Geo-Mod 2.0 is a real-time **structural stress analysis** that developer Volition calls "stress" (per Game Maker's Toolkit's technical breakdown):

1. **A building is made of hundreds of individual destructible parts** ("bricks"). Each part carries two stats: **force** (its weight/mass) and **strength** (how much mass it can hold up). Different materials get different values — a load-bearing concrete pillar has far higher strength than a pane of glass.
2. **Parts are grouped into structural layers.** For a simple tower these are horizontal tiers, "like a big stack of pancakes"; for bridges and overhangs the layering is more complex.
3. **Each layer's stats are tallied** — combined weight *including everything above it*, versus combined strength.
4. **The stress check is a single comparison:** is the layer's strength greater than the weight of everything above it? If not, **that layer fails and everything above it converts from static geometry into free rigid-body physics objects** that crash down.
5. **Cascading failure is emergent:** falling debris is itself damaging, so an upper floor's collapse can crush the layers beneath it or slam sideways into a neighboring building.

This is what makes Guerrilla's destruction feel real rather than arbitrary: a watchtower with three of four supports destroyed *will* topple like a felled tree, because the stress math says so — unlike Teardown (which waits for full detachment, so one strand of voxels can hold a building up) or Battlefield: Bad Company 2 (which swaps in a pre-canned collapse after a damage threshold).
Source: https://gmtk.substack.com/p/how-games-do-destruction ; Ringer corroboration with Volition dev quotes: https://www.theringer.com/2024/02/02/video-games/destruction-video-games-battlefield-bad-company-red-faction-battlebit-teardown-the-finals

[RESEARCHED] The stress calculation is not instantaneous — **buildings can take seconds or even minutes to begin collapsing after being weakened**, and Volition deliberately tuned the pacing so structures "slowly take their course" under gravity rather than snapping down (buildings dropping too fast diminished the experience). Designers even described hearing the weakened building "creaking and groaning" before failure — a feedback cue worth stealing.
Sources: https://www.cbr.com/designer-talks-red-faction-guerrilla/ (creaking/groaning metal supports), https://www.gamerstemple.com/games17/001951/001951p203.asp (delayed, gravity-driven collapse tuned deliberately)

### 1.2 Pre-broken meshes, not real-time CSG

[RESEARCHED] Unlike the original Red Faction (Geo-Mod 1.0, 2001), which performed real-time CSG boolean operations to cut holes in terrain/walls, **Geo-Mod 2.0 uses pre-broken meshes**: environment artists author buildings already fractured into **"shards"** — individually-crafted pieces that break off along specified joints. The shards must be small enough to respond differently to forces arriving from different directions, so destruction looks directionally correct (e.g., a charge on one side buckles the building that way).
Sources: https://www.redfactionwiki.com/wiki/Geomod ("uses pre-broken meshes that respond in a realistic manner to physical forces such as stress and kinetic impact"), https://www.linegames.org/news/i/view-L3JlZC1mYWN0aW9uLWd1ZXJpbGxhcy1kZXN0cnVjdGlibGUtc2NlbmVyeS1tYWtlcy1pdC1zdGlsbC13b3J0aC13bGF5aW5nLXRvZGF5 (shards crafted along joints, sized for directional response)

### 1.3 Physics stack: Geo-Mod + Havok side by side

[RESEARCHED] Volition did not do everything in one solver. Per lead multiplayer programmer DJ Hirko (in a multiplayer preview interview): **"The Havok engine works in tandem with the separate geo-mod engine but they both handle different properties and types of physics."** Havok handled standard physics; the Geo-Mod engine handled destruction physics. Splitting the workloads this way kept frame rate up during simultaneous normal physics and large-scale destruction — multiplayer held a reported 60 fps with a full lobby detonating buildings.
Source: https://www.gamingnexus.com/Article/2231/Red-Faction-Guerrilla-Multiplayer-preview/

[AWAITS FILE PULL] The exact division of labor between Havok and Geo-Mod 2.0 internals (which solver owns rigid bodies during collapse, whether stress data lives in Geo-Mod's own structures or Havok bodies) cannot be determined from public sources — it needs the binaries and/or symbols.

### 1.4 Two-tier calculation: big destruction vs. small destruction

[RESEARCHED] A contemporary write-up of Luke Schneider's GDC 2009 talk notes: **"Large destruction calculated differently than small, otherwise CPU would grind to halt."** Volition tiered the simulation fidelity by scale — the full layer-stress analysis for buildings, cheaper handling for small props/debris. Related design rules from the same talk: limit the destruction enemy AI can cause (players will bait it), make AI visibly react to explosions (cheap, sells the sim), and **projectile debris kills enemies but never the player** — a tuned rule, not a physics outcome.
Source: https://www.gamedeveloper.com/design/gdc-2009---day-5-4---those-who-seek-destruction-find-luke

### 1.5 What Volition said publicly about building it

[RESEARCHED]
- Associate Producer Sean Kennedy: **everything man-made is completely destructible** — buildings, vehicles, props — because of "true physics-based destruction with realistic stressing." Buildings had to be **built architecturally sound in the editor**; early Volition test buildings collapsed under their own weight during development because the artists weren't accounting for load paths. Source: https://www.gamewatcher.com/interviews/red-faction-guerrilla-interview/11408
- Press claims on effort: THQ brand manager Clint Chapman said Volition spent **four years** on the destruction engine; a later retrospective says **six months** was spent building the Geo-Mod 2.0 engine itself. (These are inconsistent press-era claims — take either with salt.) Sources: https://www.worthplaying.com/article/2008/4/7/previews/50217-ps3x360pc-preview-red-faction-guerrilla/, https://www.linegames.org/news/i/view-L3JlZC1mYWN0aW9uLWd1ZXJpbGxhcy1kZXN0cnVjdGlibGUtc2NlbmVyeS1tYWxlcy1pdC1zdGlsbC13b3J0aC13bGF5aW5nLXRvZGF5
- Materials behave like materials: wood/metal/stone each have mass and distinct behavior; **glass spiders (cracks radially) on first impact, then shatters** on the next. Buildings are engineered with metal girder superstructures reinforcing stone, "because of RFG's structural simulation technology." Source: https://www.gamesxtreme.com/article/3974/red-faction-guerrilla-preview
- Design rule for readability: **everything man-made is destructible; all natural terrain is indestructible** — kept so players always know the rules and designers can keep gameplay shapes. (Geo-Mod 1.0's terrain deformation was deliberately dropped.) Source: https://gameinformer.com/games/red_faction_armageddon/b/pc/archive/2010/06/14/the-evolution-of-destruction
- Senior Producer Jim Boone on why Geo-Mod 2.0 never went into Saints Row: the tech is **density-limited** — it pushed PS3/360 "to the nth degree" for a few very large buildings; a dense city of destructible buildings was "literally impossible" on that hardware. On Mars the buildings sit in **separated compounds so destruction is contained** and chain reactions sputter out. Source: http://www.gamewatcher.com/news/2013-12-08-volition-literally-impossible-to-apply-geomod-2-0-tech-to-saints-row-engine

### 1.6 Dev talks and presentations (found, public)

[RESEARCHED]
- **GDC 2009:** Volition gave **two highly-rated lectures** on the destruction tech. One was technical designer Luke Schneider's **"Destruction of Design"** (design-side lessons; write-up: https://www.gamedeveloper.com/design/gdc-2009---day-5-4---those-who-seek-destruction-find-luke). A later GDC Vault listing confirms the two 2009 lectures and adds **"Multiplayer Level Design in Red Faction: Guerrilla"** (2010, lead multiplayer designer). Sources: https://www.gdcvault.com/play/1012881/Multiplayer-Level-Design-in-Red
- Per a Polycount thread with apparent Volition staff participation, **programmers and tech artists also gave GDC presentations on the destruction tech** — findable via the GDC Vault site. Separately, Dave Samuel presented at GDC 2012 on "Communication & Iteration of Visual Effects in Red Faction." Source: https://polycount.com/discussion/comment/1452450/ ; http://en.wikipedia.org/wiki/geomod
- **The Finals (Embark, 2023)** is the public proof the technique transfers: its developers were **directly inspired by Volition's work** and implemented the same stress system (fractured parts + real-time stress + layer-fails-if-force-exceeds-strength) on Unreal Engine 5 / PhysX. Source: https://gmtk.substack.com/p/how-games-do-destruction

[AWAITS FILE PULL] The GDC 2009 programming talk's actual slides/specifics (data structures, update cadence of the stress solver, layer graph construction) are behind the GDC Vault paywall or lost; public sources only give the design-side summaries. The real solver detail lives in the binaries.

---

## 2. Technical architecture: data structures, authoring, performance budget

### 2.1 Data structures (what public sources establish)

[RESEARCHED] From the GMTK breakdown, the minimal working data model is:
- **Part (shard)**: mesh chunk + mass/force + strength + material tag.
- **Layer**: ordered set of parts; aggregated `totalStrength`, and `totalWeightAbove` (own weight + everything resting on it).
- **Structure graph**: parts → layers → building. The stress check runs per layer: `if layer.strength < weightOfEverythingAbove(layer): fail layer`.
- **State machine per part**: static (intact, participates in stress) → stressed/weakened (damage accumulates, creak feedback) → dynamic rigid body (layer failed) → rubble/debris (damage-dealing, despawnable).

This is **not a finite-element solver and not a node/beam lattice** — it is a much cheaper **layered aggregate check**. That cheapness is the whole point: it ran on a 2005-era Xbox 360.

[AWAITS FILE PULL] The real per-part data layout (how parts store damage, how layers handle non-vertical structures like bridges/overhangs, how the "takes a while to compute" delay is scheduled across frames, and any beam-level detail below the layer granularity) is not documented publicly. Volition's internal formats are needed.

### 2.2 Authoring pipeline

[RESEARCHED]
- **CLOE** is Volition's in-house design tool used for developing Geo-Mod environments (per the Red Faction wiki). Source: https://www.redfactionwiki.com/w/index.php?title=Geo-Mod&oldid=9507
- Authoring a building = **modeling it pre-fractured into shards along joints**, tagging each shard with material properties (mass, strength), and arranging layers so the structure is **self-supporting at rest** (the engine verifies this the hard way: unsound buildings collapse in the editor).
- Environment artists had to re-learn architecture: steel beams, foundations, girder superstructures — real load-bearing design — because the sim punishes decorative-only construction.
- Surface/texture cost: pre-broken meshes needed extra textures per shard (fracture faces), increasing memory cost.
Sources: https://www.theringer.com/2024/02/02/video-games/destruction-video-games-battlefield-bad-company-red-faction-battlebit-teardown-the-finals, https://www.linegames.org/news/i/view-L3JlZC1mYWN0aW9uLWd1ZXJpbGxhcy1kZXN0cnVjdGlibGUtc2NlbmVyeS1tYWxlcy1pdC1zdGlsbC13b3J0aC13bGF5aW5nLXRvZGF5

[AWAITS FILE PULL] CLOE's actual data schema, the shard-joint authoring format, material property tables, and how layers are assigned to non-trivial geometry (bridges, cantilevers, domes) are internal to Volition and only recoverable from the shipped data files.

### 2.3 Performance budget (what the hardware says)

[RESEARCHED]
- The engine shipped on Xbox 360 / PS3 (2005–2006 hardware) with full-building destruction plus multiplayer. Reviewers noted the frame rate held well until the heaviest late-game weaponry; the remaster holds 60 fps on modern hardware. Contemporary accounts say heavy destruction could dip PS3/360 into the low 20s.
- Key budget tricks established publicly: (a) **two-tier destruction calculation** (large vs. small handled differently); (b) **contained compounds** — buildings physically separated so collapse chains can't cascade across the whole map; (c) **sparse density** — a handful of large structures per area rather than a dense city; (d) separate physics engines for gameplay vs. destruction physics; (e) natural terrain entirely exempt from the sim.
- GDC talk note: "Large destruction calculated differently than small, otherwise CPU would grind to halt."
Sources: https://www.gamedeveloper.com/design/gdc-2009---day-5-4---those-who-seek-destruction-find-luke, http://www.gamewatcher.com/news/2013-12-08-volition-literally-impossible-to-apply-geomod-2-0-tech-to-saints-row-engine, https://www.gamingnexus.com/Article/2231/Red-Faction-Guerrilla-Multiplayer-preview/, https://www.linegames.org/news/i/view-L3JlZC1mYWN0aW9uLWd1ZXJpbGxhcy1kZXN0cnVjdGlibGUtc2NlbmVyeS1tYWxlcy1pdC1zdGlsbC13b3J0aC13bGF5aW5nLXRvZGF5

[AWAITS FILE PULL] Exact budgets (max active rigid bodies, per-frame ms for the stress solver, shard counts per building) are not published. These would need profiler runs against the PC build.

---

## 3. What WH can pull: the transferable technique

[RESEARCHED → actionable inference from the above public findings; no WH file work done]

The transferable asset is **the technique, not Volition's code or models**: a lightweight, layered stress simulation for authored set-pieces.

1. **The stress model is phone-friendly.** The core algorithm is an aggregate per-layer comparison (`strength < weightAbove → fail`), not FEA and not a per-voxel sim. A fighting-game arena needs only *dozens* of parts (pillars, walls, floor slabs, railings, hanging props), not hundreds — trivially within a mobile/Three.js frame budget. The Finals' UE5/PhysX reimplementation proves the design ports to modern engines.
2. **Authoring pattern:** build arena set-pieces as pre-fractured "shards" along authored joints, tag each with (mass, strength, material), group into layers, and require the set-piece to be self-supporting at rest. This is a concrete pipeline WH can implement in Blender/GLTF export: shard meshes + a sidecar JSON of part/layer/material stats. (This is an original proposal derived from the research — not Volition's format.)
3. **Two-tier sim:** cheap local shatter (decals, particles, small debris via the game's existing physics) vs. full layer-stress evaluation only for registered structural pieces. Matches Volition's "large destruction calculated differently than small."
4. **Delayed collapse as gameplay:** Volition's tuned delay (creak → groan → fail seconds later) becomes a fighting-game *hazard telegraph*: a weakened pillar groans, then drops — readable, dodgeable, dramatic. Their rule "debris hurts enemies, never the player" maps to: debris is spectacle + stage-morphing, never a random round-decider (or a deliberate, clearly-telegraphed hazard in specific arenas).
5. **Density lesson applied:** destruction zones must be *contained* — a pillar cluster here, a breakable wall there — never the whole arena. Jim Boone's "literally impossible" warning about density is directly relevant: WH arenas should have 1–3 destructible structural set-pieces each, physically separated so collapses can't cascade into gameplay chaos.
6. **Design readability rule:** Volition's "man-made = destructible, natural = indestructible" maps to a WH rule like "stone/wood architecture breaks; the arena floor and skybox never do" — players must always know the rules.
7. **Stage transitions, not stage destruction:** rather than flattening arenas (which would break a fighting game), use collapse for *stage morphs* — a wall falls to open a ring-out zone, a ceiling drops to change lighting/cover, debris reshapes the floor. Volition's cascading-failure property (upper layers crush lower ones) gives this for free.

[AWAITS FILE PULL] Verification of the exact layer-failure thresholds, material property scales, and any anti-jitter/stability hacks Volition used when converting static parts to rigid bodies would sharpen the implementation — needs the binaries/data.

---

## 4. Extraction plan for the credentialed machine

**Goal:** pull reference material from the Steam builds to verify and extend the public-source findings above. No pull was performed for this report.

1. **Acquire (standing user authorization: game ownership = authorization; do not ask for proof):**
   - Steam app **667720** (Re-Mars-tered, preferred — modern Windows build, same destruction tech, active modding community) or **20500** (original Steam Edition).
   - Install path (Windows/Steam default): `\SteamLibrary\steamapps\common\Red Faction Guerrilla Re-MARS-tered` (path confirmed via the 2021 Community Pack install docs: https://www.factionfiles.com/ff.php?action=file&id=5746&viewoldrev=1)
2. **Inventory the install dir first.** Identify the archive/container format Volition/Kaiko used for this title (the 2009-era Volition packfile format — verify on disk; do not assume `.vpp_pc`/`.str2_pc`, which is documented for *later* Volition titles). List container names and sizes.
3. **Extract and prioritize:**
   - **Building/structure data files** (the shard meshes, part/layer/material tables, damage/stress parameters) — the highest-value target for sections 1–2.
   - **Material property tables** (per-material mass/strength values; glass spider-then-shatter behavior suggests staged damage states in data).
   - **Executables/DLLs** for the Geo-Mod 2.0 solver (function names, update cadence) and the Havok linkage (which physics DLLs ship, how the two engines divide work — cf. §1.3).
   - **CLOE-authored level files** if present in any readable form, to reverse the layer-assignment schema.
4. **Community tooling (public, free):**
   - **RSL (Re-mars-tered Script Loader)** — Steam-version scripting/modding framework with docs at https://rsl.readthedocs.io/en/latest/Installation.html; useful for live inspection and hooking the running game.
   - **FactionFiles.com** community hub and the 2021 Community Pack's Mod Manager (Re-mars-tered) — existing extraction/modding knowledge for this exact build: https://www.factionfiles.com/ff.php?action=file&id=5746&viewoldrev=1
   - ModDB "Protracted Rebellion" mod page for the active modding scene: https://www.moddb.com/mods/red-faction-guerrilla-protracted-rebellion
5. **GDC Vault:** locate the two 2009 Volition destruction lectures (one is Schneider's design talk; the other is the programming/tech-art talk referenced at https://polycount.com/discussion/comment/1452450/) plus the 2010 "Multiplayer Level Design in Red Faction: Guerrilla" talk (https://www.gdcvault.com/play/1012881/Multiplayer-Level-Design-in-Red). Vault access may require membership — check.
6. **Deliverables for WH:** (a) shard/layer/material schema reconstructed from data files; (b) stress-solver parameters and update scheduling; (c) a worked example (one building: parts → layers → stats → failure sequence) as the reference spec for the WH arena implementation in §3. **Extract structure and parameters only — no game assets are to be reused in WH** (technique transfer, per owner intent).

---

## 5. Vision mapping: Geo-Mod techniques → WH arena destruction

| Geo-Mod 2.0 concept (researched) | WH arena application |
|---|---|
| Layered stress check: `strength < weightAbove → fail` | Cheap per-arena structural sim: pillars/walls as parts with (mass, strength), layers tallied each hit; runs on phone hardware |
| Pre-broken "shards" along authored joints | Arena set-pieces modeled pre-fractured in Blender; shard mesh + sidecar JSON (part/layer/material stats) at export |
| Buildings must be architecturally sound at rest | WH authoring rule: destructible set-pieces self-support in-editor; the sim verifies it |
| Two-tier calculation (large vs. small destruction) | Small debris = cheap particles/rigid bits; only structural pieces get the full stress evaluation |
| Delayed collapse + creak/groan audio | Telegraph system: weakened structure groans, then fails seconds later — readable, dodgeable arena hazard |
| "Debris hurts enemies, never the player" | Debris = spectacle + stage morph, never a random round-ender; telegraphed hazards only in designated arenas |
| Contained compounds; sparse density | 1–3 destructible set-pieces per arena, physically separated; collapses can't cascade across the stage |
| Man-made destructible / natural indestructible | WH readability rule: architecture breaks, arena floor and sky never do |
| Falling debris damages other parts (cascade) | Stage morphs for free: upper collapse crushes lower structures, reshaping the arena mid-fight |
| The Finals' UE5/PhysX reimplementation | Proof the stress design ports to modern engines — WH can implement it in its own Three.js + physics stack without Volition code |

**Bottom line:** Geo-Mod 2.0's genius was never raw physics power — it was a *cheap, readable, layered aggregate simulation* plus an *authoring discipline* (pre-fractured shards, real load paths, contained density). That entire package ports to a fighting-game arena: WH doesn't need a city's worth of buildings, it needs a dozen well-authored structural set-pieces whose collapses are telegraphed, contained, and dramatic. The technique is engine-agnostic; the work is in the authoring pipeline (shard + layer + material sidecar data) and the tuning (delay, thresholds, debris rules).
