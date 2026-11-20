# OSS Fighting Games & Animation Sources Already in the Owner's Repos

**Date:** 2026-10-22
**Worker:** 61 (repo mining)
**Purpose:** FIRST-step inventory of open-source fighting-game content the owner already collected in their own repos, for worker 62's public OSS survey. Every find ships with per-find usability notes.

**Repos inventoried** (full recursive tree via GitHub API, 2026-10-22):
- `mhvnsnt/brutalfistgrokversiontenpointfive` (880 entries) — BANNON fighting game (React+PWA), `public/motion/` bank, `animation_bridge/`, `src/engine/`
- `mhvnsnt/AshLane-prototype` (1,174 entries) — AshLane PWA, `public/models/` parts library, `public/motion/ual/`, `src/game3d/yokosuka/`, `tools/mocap/`
- `mhvnsnt/brutalfistgrokversion` (287 entries) — BANNON native game, `native/media/characters/chara_bannon/`, TXT canon files

---

## 1. Schwarzerblitz Engine — BSD-3-Clause (ENGINE, not vendored — contract shims only)

**What it is:** Open-source 3D fighting game engine by AndreaJens (C++, Irrlicht-based renderer the owner's docs call "Schwarzerlicht/Irrlicht"). Real OSS fighting game.

**Where in owner's repos:** `brutalfistgrokversiontenpointfive/src/engine/`:
- `SchwarzerblitzCharacterSchema.ts` (1.2 KB) — character contract: name/mesh/movesFile/bonesFile/hitboxFile/hurtboxFile, life, walkSpeed, jumpSpeed, weight, per-state frame counts, `aiArchetype` (Aggressor/Tactician/Luchador/Balanced/JackOfAllTrades)
- `SchwarzerblitzCompat.ts` (1.5 KB) — browser/native boundary contract: 60 Hz sim authority, React presentation-only, x-fighting-lane/z-sidestep-lane coordinates, BANNON combat contract + grapple pin verification
- `SchwarzerblitzInput.ts` (1.8 KB) — input bitmask buffer with motion-command detection (double-tap f/f, b/b; quarter-circle f/b) over a 24-sample window
- `SchwarzerblitzMoveCatalog.ts` (1.9 KB) — move schema: full frame data + hitbox + `animationAliases` (fuzzy clip-name matching) + range/priority/low-mid-throw flags + cancel/armor/invincible frames
- `SchwarzerblitzRuntimeManifest.ts` (1.7 KB) — 60 Hz tick, 3 rounds, 60s timer, 250 HP, states Neutral/Startup/Active/Recovery/Hitstun/Blockstun/KO, animation channels (idle/walk/light/heavy/guard/hit/block/ko), input channels, **plus `nativeReference` pointing at the upstream repo**: `AndreaJens/SchwarzerblitzEngine`, `FK_AIManager.cpp`, `EffectHandler.cpp`, `CShaderPre.cpp`
- `src/engine/retarget/AnimationSourceRegistry.ts` (15.8 KB) — license-aware animation source registry with source-type taxonomy, legal notes, and priority-based clip resolution

**License notes (from the owner's own registry):** engine is BSD-3-Clause; **Schwarzerblitz character/stage/music assets are NOT redistributable** — engine/reference use only.

**Usability for Western Heart:**
- The **input buffer** (`SchwarzerblitzInput.ts`) is a clean, drop-in motion-command detector (double-taps, quarter-circles) — directly relevant when the deferred input-fidelity work resumes. Port to vanilla JS; do not build a parallel input system.
- The **move catalog schema** aligns with the moveset library's move entries; `animationAliases` is the fuzzy-matching pattern the library needs for clip assignment.
- The **engine itself** is worker 62's prime survey target: BSD-3 fighting engine with AI manager, effect handler, shader system. Survey for AI archetypes, effect pipeline, and anything portable — engine code only, never its character/stage/music assets.

## 2. NightSky Engine — MIT (reference only, not vendored)

**What it is:** MIT-licensed fighting-game framework (rollback-netcode heritage).

**Where:** referenced in `AnimationSourceRegistry.ts` ("NIGHTSKY_ENGINE — MIT-licensed fighting framework (engine/reference only)") and `animation_bridge/SOURCE_REGISTRY.json` ("NightSkyEngine and Tekken research remain architecture/frame-data references").

**Usability:** architecture/frame-data reference for WH's online rank ladders. Worker 62: survey the public NightSky repo for rollback/netcode patterns portable to WH's netcode lane.

## 3. YokosukaJS (Allen Ussher) — MIT (VENDORED, ported)

**What it is:** River City Ransom-style beat-em-up engine (JavaScript).

**Where:** `AshLane-prototype/src/game3d/yokosuka/` — `animata.ts`, `model.ts`, `directors.ts`, `belt.ts`, plus `NOTICE.txt` carrying the full MIT license text and provenance notes.

**What's vendored:** the state machine (states/groups/transitions ported from the upstream `model.yaml`), punch/kick/walk/turn/hurt/dying animation state data; owner added a `jumping` state + transition. **Explicitly NOT included:** the sprite images (`images/`, `resources/spritesheet.json` — River City Ransom rips, not licensed for reuse); the fighters in that ward are KayKit CC0 adventurers.

**Usability:** directly scaffolds WH's locked **Heart and Mind Within** feature — per-character 3D beat-em-up story campaigns modeled on Tekken 5's Devil Within. The beat-em-up state machine (punch/kick/walk/turn/hurt/dying/jump) is a proven starting scaffold. MIT — clean for reuse with the NOTICE preserved.

## 4. Quaternius Universal Animation Library — CC0 (VENDORED)

**What it is:** Quaternius's free/standard animation set for the Quaternius modular character system: **86 clips** — UAL1 (43: locomotion, barehand combat, reactions), UAL2 (43: melee/weapon combat).

**Where:** `AshLane-prototype/public/motion/ual/` — `UAL1_Standard.glb` (7.4 MB), `UAL2_Standard.glb` (7.9 MB), `AnimationLibrary_Godot_Standard.gltf` + `.bin`, `LICENSE.txt` ("Quaternius Universal Animation Library, free standard set. CC0. https://quaternius.com/packs/universalanimationlibrary.html"). Companion code: `src/game3d/quaternius.ts` (part-attach by bone-name rebind, `tintSkin()`, `partsFor()`), `docs/QUATERNIUS.md`, `assets/characters/quaternius/QUATERNIUS_LICENSE_CC0.txt`. Modular parts in `public/models/cast/quaternius/`: Superhero Male/Female full bodies (16 MB each, 65-joint rig, ~13k tris) + 9 hair/beard/eyebrow parts.

**Rig facts:** 65-joint Quaternius rig; clips need NO retargeting on Quaternius bodies. Owner's `retargetUal()` maps Quaternius 65-joint → 58-joint Mixamo skeleton (drops root + 12 leaf/end-effectors).

**Usability:**
- 86 CC0 clips fill locomotion/reaction gaps no teardown covers; wire as a CC0 source in the animation bank (this PR adds the source entry; full clip-name enumeration happens at build time from the GLBs).
- `attachPart()` (bone-name rebind, no retargeting) is the proven pattern for the creation suite's part-attachment system.
- Worker 62: survey quaternius.com for the extended/pro animation sets and sibling CC0 packs (more body parts, more clips).

## 5. Owner's Mixamo-convention motion bank (owner's own FBX→JSON conversions)

**What:** 75 JSON motion clips, 52-bone Mixamo convention (`{file, bytes, dur, keys, bones, src: "<name>.fbx"}` in `public/motion/index.json`): BOXING ×6, CAPOEIRA, GINGA ×3, ESQUIVA, wrestling (CHOKESLAM, DDT, GERMANSUPLEX, SUPLEX, DOUBLE_LEG_TAKEDOWN___VICTIM, BODY_JAB_CROSS), hit reactions (HIT_TO_HEAD/BODY, HIT_ON_SIDE_OF_HEAD, HIT_ON_THE_BACK, HIT_REACTION), guards (GUARD_HIGH/LOW), stances (STANCE_BLADED/CROUCH/WIDE), taunts (TAUNT_ARMS_WIDE/CALLOUT/FLEX/POINT), locomotion (IDLE, walks, runs, crouch walks, DWARF_WALK, DRUNK_*), KIP_UP, knockdowns.
**Where:** `brutalfistgrokversiontenpointfive/public/motion/*.json` + `index.json` + `combat_clip_map.json` + `local.json`.
**Crown jewel:** `combat_clip_map.json` — **140 combat moves mapped to 91 clips, scored by limb/trajectory/height/style** (e.g. `"APRON JAY KICK": {"clip": "ApronJayKick", "limb": "KICK", "traj": "SPINNING", "score": 99}`). This is a ready-made move→clip mapping that drops into the moveset library's `anim_ref` model.
**License:** owner's registry marks these `license: "owner-granted"` (owner's own conversions; Mixamo source clips are royalty-free to the account holder).
**Usability:** wired into the moveset library by this PR as the `owner-motion-bank` animation source (75 clips + combat move→clip map). Wrestling grapples (suplexes/chokeslam/DDT) cover what teardown sets lack.

## 6. KayKit + Kenney — CC0 (VENDORED)

**Where:** `AshLane-prototype/public/models/{kaykit (35), kenney (29), env (28), weapons (25), props (21)}`.
**Usability:** arena/stage props, character-select backdrops, creation-suite base bodies. CC0 — safe for arenas and the suite's template bodies. Worker 62: check KayKit/Kenney for newer CC0 packs (animated characters, dungeon/martial-arts sets).

## 7. BANNON native game data (owner's own IP)

**Where:** `brutalfistgrokversion/native/` — DirectX `.x` mesh (`BF_bannon.x` 3.4 MB) + animations (`idle.x`, `running.x`, `walkFast.x`), GLB conversions (`BANNON_rigged.glb`, `idle.glb`, `running.glb`, walking.glb), `bones.txt`, `moves.txt`, `identity`/`character.txt`, `additionalHitboxes.txt`, `roster.json`, `portrait.png`, `selectionPreview0.png`, `fightPreview.png`, `bannon.png`.
**Usability:** canon source for the BANNON sub-universe (identity/character/moves/bones/hitboxes TXT files feed the moveset library and the ASHLANE CANON BRIDGE work); portraits feed select-screen work; the `.x`→GLB path documents the owner's DirectX conversion pipeline.

## 8. Owner's mocap tooling (bonus find)

**Where:** `AshLane-prototype/tools/mocap/` — `video_to_clip.py` (30 KB), `verify_capture.py` (21 KB).
**Usability:** the owner's video→clip mocap pipeline — directly relevant to the standing proof requirement (motion capture for physical claims like jiggle). Not wired this round; flagged for the rig/proof lanes.

---

## For worker 62 (public OSS survey) — survey targets confirmed from owner's repos

1. **`AndreaJens/SchwarzerblitzEngine`** (BSD-3) — full OSS fighting engine; AI manager, effects, shaders. Engine code only.
2. **NightSky engine/framework** (MIT) — rollback/netcode architecture.
3. **`quaternius.com/packs/`** (CC0) — extended/pro animation library sets + sibling CC0 packs.
4. **KayKit / Kenney new packs** (CC0) — animated characters, arena-ready sets.
5. **Mixamo** (Adobe account, royalty-free to holder) — Taekwondo kicks, Judo throws, Karate katas (owner's FIGHTING_STYLES.md already lists these as the pull list for styles with zero clips).
6. **CMU mocap database** (public domain) — martial-arts clips (also on owner's pull list).

## License handling rules for anything pulled

- CC0/MIT/BSD-3: keep the license text with the asset (as the owner did with `NOTICE.txt`, `LICENSE.txt`, `QUATERNIUS_LICENSE_CC0.txt`).
- Schwarzerblitz: engine code OK (BSD-3); **never** its character/stage/music assets.
- Mixamo-derived: owner's own conversions, marked owner-granted; keep the provenance note.
- Tekken: research/reference only, never bytes (owner's registry already encodes this).
