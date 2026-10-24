# WESTERN HEART — Chimera Build

## Six Games, One Game

Western Heart is built by reverse-engineering six games and recombining their
systems. No hand-tooled assets (except owner-designed glue). Every piece traces
to a reverse-engineered source file.

**Think of it like this:** Western Heart launches as the modern (2026) game built
on Tekken 7's foundation. But inside it, you can also play the "1997 version" —
Tekken 3's legacy content as a retro throwback mode.

### Game 1: Tekken 7 (PC, UE4) — THE PRIMARY BASE ⭐
- **Provides:** Modern fighting engine, high-fidelity character models (SK/SKT),
  51-fighter roster, deep customization system (CCI/CI), 34 stages, UE4 pipeline
- **Key findings:** Full character ID table mapped (IDs 0-56), stage ID table mapped,
  file naming conventions decoded, asset prefixes catalogued (SK/SKT/SM/BP/PA/CS/CCI/CI/T)
- **Community RE:** modding-zaibatsu/tekkenmods-docs (cloned to `tekken7/tekkenmods-docs/`)
- **Tools:** UModel (UE Viewer) working on Linux at `tekken7/tools/umodel_linux`
- **Status:** DOCS + TOOLS READY — game files (~47GB) BLOCKED on disk (18GB free, need 47GB)
- **Western Heart use:** DEFAULT character models, animations, stages, customization system.
  Owner's 7 named fighters (Pantera, Demonio, Phantom, Diablo, Skull, SAM-∪R-Λ1, Saku Ra)
  use Tekken 7 versions. 35 additional Tekken 7 fighters available for owner to name.
- **Roster doc:** `tekken7/TEKKEN7-ROSTER-MAPPING.md`

### Game 2: Tekken 3 (PS1) — LEGACY MODE 🕹️
- **Provides:** 3D fighting engine (classic), character rigs, animation data format
- **Key findings:** 27-part rigid mesh hierarchy (no skinning), ~1K tris/fighter,
  8,556 textures, animation-as-data, 67 character models
- **Status:** TEARDOWN COMPLETE — docs at `tekken3/docs/`
- **Western Heart use:** LEGACY/RETRO MODE — playable "1997 version" inside the modern game.
  16 fighters carry over to Tekken 7; 7 are Tekken 3 exclusive (Gun Jack, Mokujin,
  Ogre, True Ogre, Tiger, Baek, Gon). Classic PS1 aesthetic as a throwback.
- **Model mapping:** In progress — mapping 67 records to characters, King priority

### Game 3: Eastern Mind — The World and Soul
- **Provides:** Surreal universe, narrative, visual identity, five lands
- **Key findings:** 549MB game extracted, head-world concept, death-as-progression
- **Status:** PULLED AND ANALYZED — docs at `../animation-techniques/steal-like-artist/osamu-sato/`
- **Western Heart use:** Stages (five lands as arenas), lore, visual soul, reincarnation mechanic

### Game 4: WWF No Mercy (N64) — Wrestling Systems + Customization
- **Provides:** Wrestling move system, character creation suite, grappling animations
- **Key findings:** Fully modular customization (14M/9F body types, 98 faces,
  ~150 ring attires, ~150 upper bodies, per-limb pads), positional move slots
  (front/back × weak/strong × 8), parameterized fighting styles
- **Community RE:** chaotix610/wwfnomercy-docs (cloned to `wwf-no-mercy/re-docs/`),
  Gadge64/WWFNoMercyRecomp (cloned to `wwf-no-mercy/recomp/`)
- **Status:** ROM DOWNLOADING — teardown in progress
- **Western Heart use:** Wrestling ANIMATIONS and SYSTEMS (not character models).
  Models reserved for future projects (Bannon, wrestling game six).

### Game 5: WWE WrestleMania XIX (GameCube) — Modes + Arena Traversal
- **Provides:** Revenge Mode (mission-based, fights outside ring), Create-an-Entrance,
  WWE Shopzone (progression), Yukes engine animation approach
- **Key findings:** ~40 wrestlers, GameCube hardware (higher fidelity than N64)
- **Status:** ISO NOT YET DOWNLOADED — needs browser task (sources documented)
- **Western Heart use:** Arena traversal design, additional game modes

### Game 6: Urban Reign (PS2) — Street-Brawl Systems 🌆
- **Provides:** 4-player free-for-all brawling, 30+ weapons, destructible
  environments, AI partner double-team combat, special-arts meter
- **Key findings:** 60+ fighters (boxing/wrestling/karate/capoeira styles),
  Tekken guests Paul Phoenix + Marshall Law, 100-mission story, Weapon Battle
  and Destruction Battle multiplayer modes — made by the ex-Tekken team
- **Status:** ISO DOWNLOADING 2026-10-12 — teardown at `teardown/urban-reign/`
- **Western Heart use:** TBD by owner — **Option A:** third mode (BRAWL MODE)
  alongside Tekken/Wrestling; **Option B:** merged into Wrestling Mode as its
  hardcore street-fight variant

## The Two Fighting Modes

**Owner's key design insight:** Wrestling games move differently than Tekken.

- **TEKKEN MODE:** Horizontal 3D fighting. Sidestep movement, open plane,
  frame-perfect combat. Tekken 7's engine and models (modern), Tekken 3's models (legacy).
- **WRESTLING MODE:** Ring/arena-based fighting. Rope mechanics, turnbuckle
  interactions, apron/ringside traversal, grapple-heavy. No Mercy/WMXIX systems,
  Tekken 7 models with retargeted wrestling animations.

## The Two Eras

- **MODERN ERA (default):** Tekken 7 models, UE4 visuals, current roster.
  This is what players see on boot.
- **LEGACY ERA (1997 throwback):** Tekken 3 models, PS1 aesthetic, classic roster.
  Unlockable/playable as a retro mode inside the modern game.

## Asset Rules

1. **Western Heart uses:** Tekken 7 models (default) + Tekken 3 models (legacy mode)
   + wrestling animations/systems + Eastern Mind world
2. **Wrestling character models:** Stored SEPARATELY, NOT in Western Heart
   - Reserved for: Bannon (wrestler characters), dedicated wrestling game ("wrestling game six")
3. **No hand-tooled assets.** Only owner-designed glue (roster names, design decisions).
4. **Study only.** Nothing redistributed. (STEAL-LIKE-AN-ARTIST LAW)

## Technical Goals

1. Extract skeletons + animations from No Mercy and WMXIX
2. Test retargeting wrestling animations onto Tekken 3 character models
3. Document both games' arena/stage systems for separate fighting modes
4. Build No Mercy-style modular customization for Western Heart attires
