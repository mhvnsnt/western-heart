# Western Heart Arena Pipeline — Research & Build Plan

**Date:** 2026-10-23
**Status:** Research complete. Pipeline tooling built. Full arena rebuilds AFTER models → animations → menus (user sequencing).

**User directive (verbatim):** "breaking down our files and tearing down our motherfucking tech and seeing how they build their arenas, how they build all their parts of the game how they do it and then start bringing it in and setting our stuff up like that so we can build more parts of our arena and have like those better quality parts and shit and figure out how they do it"

**Refinement (verbatim):** "Don't just take the user's word on canon — RESEARCH WHY each arena looks the way it does. Read the canon docs to understand the in-universe reason for each arena's look. Then upgrade quality from that understanding. Use Tekken 7 and other games' teardown files as the technical reference for HOW to achieve the quality."

**Companion docs:**
- Canon research (full, ~30KB, every claim canon-quoted): `~/workspace/arena-canon-research.md`
- Teardown technique research (full, methods only): `~/workspace/arena-technique-research.md`

---

## PART 1: CANON — WHY EACH ARENA LOOKS THE WAY IT DOES

> **ARENA LAW (user-locked 2026-10-23):** Upgrade graphics QUALITY (god rays, lighting fidelity, effects quality, geometry) but PRESERVE colors and canon look. **"Colour is law"** (CANON.md §8 L1381–1385) — the head-world runs on one shared palette "the way a body runs on one blood." Never introduce hues outside it. Upgrade the quality of the light, never the intent of it.

**The cosmology:** Tong-Nou is a giant green head floating in darkness — "It is a body, and the lands are its organs" (CANON.md §1 L20, §8 L1321). The sky inside the head is the inside of the head — dark, vast, veined. Each arena is one of the head's organs/lands.

| Arena | In-Universe Reason (canon-quoted) | Upgrade Direction (quality, NOT look) |
|-------|----------------------------------|--------------------------------------|
| **TREE OF LIFE** (Wood/Ming-ken) | The cosmos's nursery: "glowing souls hang like fruit too high to pick and too bright to ignore" (§8 L1351). Where souls begin AND are kept. The blinding washed-out sky = light of countless unborn souls. **Intentional — never dim it.** | God rays, better bloom falloff, atmospheric scattering on soul-fruit glow |
| **PLAINS OF CHI-U** (Fire) | "Burning sky… the Fire Tower of Time burns and never collapses… Time does not pass here; it *accumulates*, like heat" (§8 L1353). Fire = honest confrontation. | Heat-haze distortion, eternal-flame tower with three visible tiers, ground flame tongues |
| **OCTAGONAL SHRINE PAR-FANG** (Earth/The Source) | "Eight-sided, ancient, still. The sky above is the inside of the head — dark, vast, veined" (§1 L38). Winning here is "absorption, not explosion" (§8 L1361). | Layered flesh-like veined sky with slow pulse synced to the head's heartbeat; weathered inscribed stone. More presence, not more light. |
| **HELIX PALACE** (Metal) | Desire as architecture: five glowing rooms (Greed, Appetite, Immortality, Sexual Desire, Destruction), "everything reflects, nothing is what it seems" (§1 L39). Pink Narwhal club interior is user-authorized. | Real reflections, PBR richness, keep five canon-coded pod colors distinct; hint the spiral palace beyond |
| **PALACE OF DREAMING** (Water) | "Won't stay still… the floor reflects a sky that isn't there. Change is the only law" (§1 L40). Souls "dream the room's" dreams (§8 L1357). | True planar floor reflection showing a *different* sky than overhead; refractive water-walls; never still or sharp |
| **PHANTOM MARKETPLACE** | "The smallest land and the only one that is a *verb*" under the Eyeball Mountains "which watch, which have always watched" (§8 L1359). "Nothing here is real, but the prices are." | Eyeballs genuinely watchful (saccades toward impacts); add the Trader's scales and ledger (canon names them, currently missing) |
| **TONG-NOU** (Void) | The giant green head itself — "not a metaphor… it is a body, and the lands are its organs" (§1 L20). This stage = the outside view. Eyes tracking fighters = the Purifier watching. | Flesh-like subsurface translucency, vein-pulse, heartbeat eyes that occasionally skip; keep the void truly void (no stars — "not night, not space, just the dark") |
| **SUN RĀ — THE STARING SKY** (boss) | Quarantined pocket realm; "cute evil sun" cursed to stare forever with bleeding eyes; "wrong fire… he burns souls for fuel" (§7 L1188–1208). | Lean into cute-evil; canon blood VFX (eyes + corner of grin); polish the datamosh shift |
| **T3 RETRO / NO MERCY / T7 DOJO** | Legacy tiers — honestly labeled, no canon conflicts. T3 = Tekken history; No Mercy = Bannon sub-universe (§9). | Geometry/texture fidelity only, not look changes |

### ⚠️ Canon Contradictions (user review BEFORE any upgrade)

1. **SHRINE OF THE BLADE — NO CANON SOURCE.** Name appears nowhere in CANON.md. Tagged "Phantom home stage" but canon gives Phantom the Marketplace (named after him, §2 L144) / Helix Palace (§2 L134), and Diablo the Plains of Chi-U (§2 L165). Also collides with Octagonal Shrine (canon's only shrine). **User decides: re-ground with user-written canon, retire it, or mark non-canon versus-only.**
2. **SUN RĀ code/prop named "Mars"** (mars-sky.glb, MARS_POS). Canon: he is a *sun* (§7 L1188). Rename. (Minor.)
3. **SUN RĀ description claims "Central Mountain is Kevin's home turf"** — no canon source; Kevin's element is Fire/Chi-U (§7). Drop or have user write the canon. (Minor.)

### Global Principles
1. **Colour is law** — never leave the head-world's shared palette.
2. **Upgrade light quality, never light intent.**
3. **"A land whose force has been claimed… its colours *settle*"** (§8) — future dynamic-grade hook: per-ladder-progress color settling. Worth a lane.
4. **Fighters are luminous sources in a luminous darkness** — stage upgrades must keep fighter readability first.

---

## PART 2: TEARDOWN — HOW REAL GAMES BUILD ARENAS

### The 5 Key Pipeline Patterns

**1. Arena = named mesh groups, not one blob (No Mercy — cleanest documented).**
AkiModel pieces → per-piece OBJs with `g <file_id>_<label>` groups → `convert_nomercy.py` emits one GLTF mesh per group (names preserved: `Titan_Tron`, `Ring_Mat`) so game code targets regions. Flat per-face normals, per-vertex RGB → `COLOR_0`, UVs preserved. Fighting surface detected and normalized to y=0. Fighters always spawn at y=0 regardless of source geometry.

**2. Arena = package manifest, not one file (WMXIX).**
Each arena slot = base mesh (`.ymg`) + textures (`.tex`) + skeleton (`.ycg`) + entrance staging (`.ent`) + ground (`.gt`) + lighting rig (`.light`) + overlays (`.scr`). Geometry, materials, lighting, crowd, and staging are separate concerns loaded by an arena loader. YOBJ format cracked: f32 verts, 20-byte face-index records, material table with absolute offsets.

**3. Venue = config composition (Def Jam).**
48 venues in `VENUE.XML`: each = model pack + display name + ID + `<crowd>` + `<crowd2>` + `<ambient>` + `<sounds>` + `<speechID>` refs. Atmosphere is data-driven composition, not baked geometry. Direct model for WH stage manifests.

**4. Static world + runtime assembly (all sources agree).**
The ROM/file ships the static scene. The game engine's arena builder does the procedural work: ropes NEVER exist in No Mercy ROM (generated at runtime); crowd sections are stored as templates and instanced around the bowl at runtime; ring posts/turnbuckles have no placement data (game code places them). WH's `buildNoMercy()` already mirrors this — loads the GLB, then procedurally rebuilds cage walls, mat, posts, ropes.

**5. Reskins are additive, originals always ship (No Mercy).**
`reskin_stage.py`: vertex-color tint multiply (night/sunset/bloodmoon/ultraviolet), per-group recolor, JSON sidecar material overrides. Variants are additive files (`arena_raw.night.glb`). Lighting/mood variants don't duplicate geometry.

### File Formats (sources)

| Game | Format | Status |
|------|--------|--------|
| WMXIX arenas | YOBJ (f32 verts, 20B index records, material table) | CRACKED, 43 arenas extracted |
| No Mercy arenas | AkiModel pieces → OBJ + .vc sidecar | 100% teardown, 17 assemblies |
| T3 stages | PS1 TMD records (`A\x00\x00\x00` magic) | 100% teardown; BNS on-demand loading |
| VF5 arenas | FArC → `stgXXX_obj.bin` + `stgXXX_tex.bin` | 18 arenas on release vf5-ps3-v1, up to 300k polys/stage |
| Urban Reign stages | PPK (`ppk\0` magic, sub-chunk table) | 7 PPKs extracted, inner format NOT decoded |
| TTT2 stages | Archive chunks | 29 documented, 10 breakable; chunks opaque |
| T7 stages | 34 mapped | Geometry unpacking in progress (Steam) |

### Geometry Pipeline (the reusable steps)

1. **Extract** → per-piece geometry (OBJ, point cloud, etc.)
2. **Assemble** → world-placed structures + local-template small parts (separate!)
3. **Normalize** → uniform world scale (meters), fighting surface → y=0
4. **Convert** → game-ready GLB (one mesh per named group, vertex colors, UVs)
5. **Variants** → additive reskins (tint, group recolor, sidecar overrides)

### Collision / Boundaries (taxonomy from sources)

| Type | Pattern | Source |
|------|---------|--------|
| `WALL` | Architecture closes in; wall splat/combos; per-wall damage | DOA6 danger zones |
| `EDGE` | Ring-out kill plane | Soulcalibur (`ring_out_enabled`, `edge_type`) |
| `INFINITE` | No boundary (open field) | — |
| `BREAKABLE` | Floors/walls break → multi-tier transition | TTT2 (10 stages), DOA6 |
| `DESTRUCTIBLE` | Props break on contact (separate from boundary) | Urban Reign |

Current WH: single scalar `wallDistance` + flat floor (`GROUND_Y = 0`). The taxonomy above is the upgrade target.

### Lighting Techniques (technique, not values)

1. **Baked vertex lighting** (N64/No Mercy): per-vertex RGB sidecar — zero runtime cost, look preserved exactly. WH replays via `COLOR_0`.
2. **Lighting rig as separate data** (WMXIX `.light` files): lighting is NOT baked into the mesh. WH equivalent: extend stage JSON `lighting` block into a real rig spec.
3. **Layered light rig** (WH `buildBase` already): hemisphere + directional key with shadows + rim + fill + distance fog. Standard fighting-game shape.
4. **Skybox + fog**: gradient sky + panorama cylinder (`fog: false` on distant art). Distance fog ties arena to backdrop.
5. **Light in textures** (N64): glow baked into texture art ("Lights_Above_the_Structures").
6. **Quality ladder**: baked vertex color/AO (free) → separate light-rig data → lightmaps (static GI) → dynamic key + shadow → bloom/god-rays (post-process, PS4-era engine effects, not arena-file data).

### Effects

- **Crowd = instanced templates**, not arena geometry (all sources). Placement is game code.
- **Crowd = swappable module** (WMXIX `audi.pac`, Def Jam `<crowd>` config refs).
- **Ropes = procedural** (verified zero rope meshes in No Mercy ROM).
- **WH current**: per-arena particles (maple leaves, lanterns, motes), interior point lights, edge-marker torus, canvas-generated textures.

### Stage Transitions

- **Multi-tier** (TTT2, DOA6): breakable floors/walls → fight moves to lower floor.
- **Enclosed ↔ open** (WMXIX): Hell in a Cell (box) vs. open Revenge-Mode environments.
- **WH now**: edge marker torus, `wallDistance`, `hidePlatform` flag, per-builder `update(dt, t)` hook (where transitions live).
- **Gap**: TTT2/DOA transition trigger rules not yet decoded (next RE lane).

---

## PART 3: WH ARENA PIPELINE — TOOLING BUILT

All in `tools/arena-pipeline/`:

### 1. `arena_validate.py` — stage definition validator
Validates `game/js/stages.js` STAGES array:
- Required fields (id, name, dims, spawns, lighting, floor, builder)
- Dims sane (Tekken-standard bounds: 16.8m width reference)
- Spawns within wallDistance
- Lighting block complete (sky, fog, hemi, sun, rim, fill)
- CANON LANDS stages have swatch + universe + element (canon grounding)

### 2. `canon_lock.py` — canon color/lighting CI guard
**Enforces the user's arena law.** Snapshots canon-locked fields (sky gradients, fog/hemisphere/sun/rim/fill colors, floor tints, swatches) for all CANON LANDS stages. `--check` fails CI on any unauthorized change. `--approve "<user quote>"` overrides with a logged reference. Baseline: `canon_baseline.json` (8 canon stages).

### 3. `arena_assemble.py` — venue manifest assembler
Follows Def Jam VENUE.XML + WMXIX package patterns. Takes a stage manifest JSON (geometry + builder + crowd + ambient + sounds + lighting_rig + canon refs), validates all files exist, emits a game-ready `.package.json`. `--validate-all` batch-checks a manifests directory.

### Pipeline Flow (how it all fits)

```
Arena source (OBJ/GLB/procedural)
    → arena_assemble.py (manifest: geometry + crowd + ambient + sounds + lighting_rig)
    → arena_validate.py (dims, spawns, lighting completeness, canon grounding)
    → canon_lock.py --check (colors/lighting unchanged for CANON LANDS)
    → game loader (buildStage → builder fills THREE.Group)
```

---

## PART 4: PER-ARENA UPGRADE PLAN

**Sequencing (user law):** models → animations → menus FIRST. Arena rebuilds AFTER. The research above + pipeline tooling is the preparation phase. When the rebuild lane opens, per arena:

| Arena | Canon Direction | Teardown Technique | Build Tasks |
|-------|----------------|-------------------|-------------|
| TREE OF LIFE | God rays, bloom falloff, soul-fruit scattering. NEVER dim. | Post-process bloom (PS4-era); emissive instancing (No Mercy pattern) | Upgrade soul-fruit to instanced emissive mesh; add god-ray post pass |
| PLAINS OF CHI-U | Heat-haze, 3-tier flame tower, ground tongues | Distortion shader; layered geometry | Flame tower rebuild (3 tiers); heat-haze post |
| OCTAGONAL SHRINE | Veined sky pulse, weathered stone | Canvas-generated textures (WH pattern); slow shader pulse | Vein-sky shader with heartbeat sync |
| HELIX PALACE | Real reflections, 5 pod colors, spiral hint | PBR materials; reflection probes | PBR upgrade; reflection probe pass |
| PALACE OF DREAMING | True planar reflection (different sky), water-walls | Planar reflection (render target) | Reflection plane; refraction shader |
| PHANTOM MARKETPLACE | Watchful eyeballs, Trader's scales + ledger | Saccade animation; prop placement | Eyeball tracking; add canon props |
| TONG-NOU | Subsurface translucency, vein-pulse, void stays void | SSS approximation; emissive pulse | Flesh shader; heartbeat sync |
| SUN RĀ | Cute-evil polish, blood VFX, datamosh | Particle VFX; transition shader | Blood particle system; rename Mars→Sun Rā |
| SHRINE OF THE BLADE | **BLOCKED — needs user canon decision** | — | Await user: re-ground, retire, or mark non-canon |

---

## Sources

Every claim above traces to:
- `~/workspace/arena-canon-research.md` (canon quotes with CANON.md § + line)
- `~/workspace/arena-technique-research.md` (teardown methods with file paths)
- `teardown/ARENA-INVENTORY.md` (cross-game inventory)
- `teardown/wmxix/arenas/ARENA-FORMAT.md` (YOBJ crack)
- `teardown/wwf-no-mercy/arenas/ARENAS.md` (assembly pattern)
- `tools/stage-arena-pull/convert_nomercy.py` (GLB pipeline)
- `teardown/tekken3/docs/TEKKEN3-ARCHITECTURE.md` (TMD, BNS loading)
- `teardown/virtua-fighter-5/stages/README.md` (FArC format)
- `teardown/def-jam-fight-for-ny/surgical/xml/VENUE.XML` (venue manifest)
- `game/js/stages.js` (current WH implementation)
