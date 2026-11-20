# Lighting + Environment Pull — Teardown Audit & Implementation (worker 27, 2026-10-22)

Owner directive (verbatim): "Pull from the most recent version of each game in the teardown files:
(1) Lighting — how each game lights its stages, light placement, color temperature, dynamic vs
baked, character vs stage lighting. Tekken 7/8, DOA6, SFV, SC6 — the newest lighting tech. Wire
their lighting approaches into our stages. (2) Environment and scenery — stage geometry,
background buildings, set dressing, ambient details. Whatever can be extracted and reused.
(3) Accessories, clothing, buildings — from all teardowns, feeding both stages AND the character
creation suite. (4) General sweep — flag anything visual/environmental we haven't pulled yet.
Priority: lighting first, then stage scenery, then accessories/clothing."

## 1. LIGHTING AUDIT — what the newest games do

### Tekken 7 (UE4) — the reference split
- **Source (in-repo):** `teardown/tekken7/tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Stages/index.md`
- Every T7 stage streams **two lighting units**: `light` ("lighting information for the
  respective map/stage" — dynamic) and `lightstatic` ("baked lighting data" — Lightmass
  lightmaps/GI). Stages that need it stream both; the suffix table documents which.
- UE4 lighting modes behind it: **static** (fully baked, fastest), **stationary** (partially
  baked, color/intensity changeable at runtime), **movable** (fully dynamic + dynamic shadows,
  slowest). Characters are dynamic meshes: lit by movable lights, indirect via volumetric
  lightmaps / SH probes.
- **What we wired:** `buildStageLightRig()` in `game/js/lighting-rig.js` implements the same
  split — hemisphere + gradient sky + fog is the *baked-ambient stand-in* (T7 `lightstatic`;
  no runtime lightmap baking exists in a browser, the hemi/sky carries the baked feel),
  key/rim/fill directionals + accent point lights are the *dynamic rig* (T7 `light`).
  Exactly one shadow-casting directional (the key), same as the UE4 convention of one
  shadowed directional per stage.

### Tekken 8 (UE5) — baked wins at 60fps
- **Sources:** dsogaming Lumen on/off comparison (2024-01), Digital Foundry tech preview via
  icon-era (2024-01), wccftech mod report.
- T8 does **not** use Lumen/Nanite/Virtual Shadow Maps — confirmed by Digital Foundry
  (strict 60fps target). It ships **baked-in stage lighting + dynamic character lights**,
  same architecture as T7. The dsogaming Lumen-mod comparison shows baked lighting beating
  Lumen on most T8 stages (Cave/Forest look worse with Lumen; characters look worse).
- **What we wired:** validation of the T7 approach — we do NOT chase real-time GI; we bake
  the mood into ambient/sky/grade and spend dynamic lights on fighters. Lumen-style GI is
  correctly out of scope for a phone browser target.

### Street Fighter V (UE4 + Enlighten) — character/stage separation
- **Sources:** 80.lv (2016-02-16): SFV runs Geomerics **Enlighten** — "advanced spherical
  harmonic probe technology, the element responsible for shading objects that move at
  runtime allowed Capcom to create indirect lighting for its characters" (Bochan Kim,
  SFV producer). Characters AND stages share the GI solution; fighters are also pushed
  **brighter than the background with strong rim** so they pop.
- **What we wired:**
  - `attachCharacterRig(fighter, stageDef)` — every fighter carries their own **key
    PointLight** (front-top, parented to the fighter root: follows them with zero
    per-frame cost) + their **soul glow** (the existing `auraLight` now idles at a
    soul-color baseline instead of 0 — zero new lights) + soul-tinted **emissive**
    (bible Grey's law: fighters are luminous *sources* — costs nothing, already in the
    standard-material shader). This is our SH-probe equivalent: light that follows
    the fighter.
  - `rimBoost` per stage (SFV-style rim pop; Helix Palace 1.25, Dreaming 1.2).

### Dead or Alive 6 (new engine) — physical lighting
- **Sources:** dualshockers (2018-06-09, Shimbori interview): DOA6 dropped the Soft Engine
  for a new engine supporting "**physical lighting**… adding more realism to characters
  and environments"; playstationlifestyle (2026-06-23, OBORO interview): "precision in
  the way light is reflected or creates shadows, reflections, and natural lighting."
- **What we wired:** no new feature — a constraint honored: keep PBR materials, keep the
  shadow-casting key, don't flatten the scene with ambient. (Our materials are
  MeshStandardMaterial throughout; the audit confirms that's the right call.)

### Soulcalibur VI (UE4)
- **In-repo:** `teardown/soulcalibur-6/TEARDOWN.md` + `docs/SCVI-MECHANICS.md` (mechanics
  docs only — 50GB+ binaries never acquired). No lighting-specific documentation found
  in the teardown; SC6 is UE4-family so it shares the T7/SFV static/stationary/movable
  pipeline. **Flagged, not invented** — no SC6-specific claims wired.

### Color temperature / placement (synthesis, adapted for Three.js)
- Key: warm-to-neutral directional, low-ish angle (existing per-stage `sun` blocks kept).
- Rim: cool/land-palette directional from behind (existing `rim` blocks kept, boostable).
- Fill: soft frontal from camera side (existing `fill` blocks kept).
- Character key: warm white `#ffe9d2` default, per-stage overridable (Fire land gets ember
  `#ffc0a0`, Dreaming gets cyan `#c8f0ff`, Marketplace gets Trader gold `#ffd76a`).
- Ambient: hemisphere sky/ground per land (bible land palettes).
- Accents: per-builder point lights (lanterns etc., unchanged).

### Grade hooks (new)
- `applyGrade(arena, def)` in `lighting-rig.js`, called from `Arena.setStage`:
  per-stage `lighting.grade = { exposure, bloom }` drives `renderer.toneMappingExposure`
  (ACESFilmic, was a global 1.45) and `UnrealBloomPass.strength` (was global 0.6/0.85).
  This is the bible's "luminous darkness" dial — each land gets its own grade
  (e.g. Tong-Nou: exposure 1.35 / bloom 0.85 — dark with light blooming out of it).

### Soul light behaviors (bible §5c, wired in fighter.js)
| Soul | Color | Behavior wired |
|---|---|---|
| RIN 凛 | `#F0F4FF` | steady cold glow |
| BYOU 病 | `#9DBE3C` | flickering, wrong (dual-sine flicker) |
| TOU 闘 | `#A31621` | low, predatory (light sits at y=0.55) |
| SHA 沙 | `#E0A93E` | shimmering heat (sine shimmer) |
| KAI 海 | `#0E6B6B` | rolling, tidal (slow swell) |
| JIN 刃 | `#C8D0DC` | steady hard edge |
| RETSU 烈 | `#E85D1F` | explosive radial pulse |
| ZEN 禅 | `#050508` | absence of light (glow 0) |
| GYOU 行 | rainbow | hue-cycling streak |

### Mobile perf budget
Forward-renderer cost scales with light count. Budget: hemi(1)+dir(3)+accents(≤6)+
charKeys(2)+soul(2) = **14 max**. The soul glow reuses the existing auraLight (was already
in the budget at intensity 0); the only additions are the 2 character key PointLights
(no shadows). Motes: 1 draw call, 0 lights, capped at 110 points on mobile.
Emissive: zero extra shader cost. Verified by node harness (56 asserts) — see Proof.

## 2. ENVIRONMENT / SCENERY

### Already pulled (prior lanes — not duplicated)
- Tekken 3: 15 retro arenas — real TMD geometry + decoded texture atlases
  (`game/assets/stages/t3/`), wired via `t3-*` builders.
- WWF No Mercy: 17 arenas — GLB conversions with vertex colors
  (`game/assets/stages/nomercy/`), wired via `nomercy` builder.
- Eastern Mind: 6 pano backdrops on the canon lands (cylindrical backdrop).
- Sun Rā boss arena: GLB + planet textures, wired.
- Registry: 41 stages (8 canon + 15 T3 retro + 17 No Mercy + 1 boss).

### Pulled this lane
- **Atmosphere motes** (`buildMotes` in lighting-rig.js): per-stage floating
  dust/soul-motes/pollen/cinders — bible §8.4 "darkness is a material" (nebula wisps,
  soul-motes), Tree of Life "pollen-light motes", Shrine "dust motes in lantern beams",
  Chi-U "floating cinders", Dreaming "bioluminescent drift", Marketplace "Nostalgia
  Haze". 1 draw call, 0 lights, additive, slow rise + sway + wrap. Every stage gets
  them via `buildBase`; the 8 canon lands carry tuned color/count in their `rig` blocks;
  T3/No Mercy/boss stages get the subtle Nostalgia Haze default.
- **Per-stage light-rig data**: all 8 canon lands now carry `rig` (charKey color,
  rimBoost, motes) + `grade` (exposure, bloom) blocks grounded in bible palettes
  (§5b land palettes, §2 Malakor violet, §7 master palette). No pure RGB primaries
  anywhere (bible don't).

### Flagged (not pulled — needs a lane with the right tooling)
- **VF5 PS3 stages** (18 arenas, `teardown/virtua-fighter-5/stages/README.md`): geometry
  + textures extracted to release `vf5-ps3-v1` as `.farc`; import needs the chrrox 3ds
  Max script + TXP.bms QuickBMS pass. Stage IDs mapped (Arena, Bar, Dojo, NYC, Shinto
  Shrine, Sea, Snow, Terrace…). High value: real Sega arcade stage geometry.
- **WMXIX arenas** (`teardown/wmxix/arenas/`: 43 files, 324k verts as OBJ **point
  clouds** — `bg/00` full arena bowl, `ring.obj`, `kaijo_x8.obj` 14k verts): renders
  verified but they're point clouds, not meshes — surfacing/reconstruction work needed
  before any can dress a stage. `customization/WORKLOG-WMXIX-YMG.md` tracks the format.
- **Urban Reign** (`teardown/urban-reign/`): 7 stage PPKs (alleys, bars, rooftops,
  Chinatown, junkyards) extracted (34MB) but inner Namco geometry NOT decoded; PLUS
  `data/light/stage/bg*.lit` — **per-stage lighting data** (the intended mood per
  arena, 8 files). The `.lit` decode is a clean future lighting-mood pull.
- **DOA6 / SC6 / SFV / T7-full**: binaries never acquired (32GB/50GB/26GB/47GB) —
  mechanics/docs only. No geometry or light rigs extractable without the games.
- **Tekken 6 PSP**: encrypted (PPSSPP live-dump guide ready, not run).
- **Def Jam FFNY**: ISO sourced, venue pull pending.

## 3. ACCESSORIES / CLOTHING / BUILDINGS

### Character creation suite (coordinate, don't duplicate)
- `customization/PARTS-REGISTRY.json`: **1148 parts** across 13 libraries (cc0-hair,
  eye-library, decal-library-pantera, no-mercy, wmxix, superhero, reskin libraries…).
  Healthy — nothing added here to avoid duplicating the in-flight WWE CAW extraction
  (`customization/extract_caw_parts.py`, `wwe2k-caw/`, `mat-legends-caw.json` — another
  worker's lane).
- Tekken 6/TT2 customization research (`teardown/tekken6-customization-research.md`,
  `teardown/ttt2-customization-research.md`): item NAME tables decoded (10,495 records:
  Sledgehammer, Leather Pants, Topknot, Ki effects…), but **item 3D models still
  locked** (T6) / extraction blocked (TT2 truncated 7z). Names without meshes can't
  feed the suite — flagged.
- T7 King armor pieces (`teardown/tekken7/king/`, `king-variants/`): textures for
  Pantera's own model, not detachable accessories — correctly NOT registered as parts.

### Stages (buildings/architecture)
- No Mercy GLB arenas already carry their architecture (already wired as stages).
- No new building meshes extracted this lane: the extractable architecture sources are
  the flagged items above (VF5 farc, WMXIX point clouds, Urban Reign PPKs).
- Stage set-dressing added: atmosphere motes (see §2) + per-stage grade.

## 4. GENERAL SWEEP — visual/environmental, not yet pulled
1. Urban Reign `bg*.lit` stage lighting moods (8 files, documented format location).
2. VF5 18 arena `.farc` files (release `vf5-ps3-v1`) — needs 3ds Max chrrox + QuickBMS.
3. WMXIX arena point clouds → mesh surfacing (43 OBJs).
4. T6/TT2 customization item meshes (locked/blocked).
5. Def Jam venue pull (ISO sourced).
6. DOA6/SC6/SFV/T7-full binaries (not acquired; owner decision).
7. SC6-specific lighting documentation (teardown has mechanics only).
8. wmxix crowd/arena-detail `_ad2.obj` LOD variants (extracted, never triaged for reuse).

## Files changed
- `game/js/lighting-rig.js` (NEW): soul table, stage rig builder, character rig,
  grade hooks, motes, light budget.
- `game/js/stages.js`: buildBase delegates lights to `buildStageLightRig`; 8 canon
  lands gain `rig` + `grade` blocks.
- `game/js/scene.js`: `applyGrade` on every stage swap.
- `game/js/game.js`: `attachCharacterRig(p1/p2)` on match start.
- `game/js/fighter.js`: soul-glow baseline + per-soul behaviors in the aura update.
- `docs/research/lighting-environment-pull-2026-10-22.md` (this file).
- `WORKLOG.md`: worker-27 entry.

## Proof
- node harness `/tmp/lr-test/test.mjs` (real three r160, no DOM): **56/56 asserts pass**
  — soul table validity, stage rig light composition (1 hemi / 3 dir / 1 shadow key /
  rimBoost math), motes updater + mobile cap, character rig attach (soul resolve,
  surge-color memory, low-light for TOU, key placement, fail-silent), grade
  application + defaults, budget ledger.
- `node --check` ESM parse: lighting-rig.js, stages.js, scene.js, game.js, fighter.js.
- Structural: old inline light block gone from buildBase; all 8 canon stages carry
  rig+grade; no pure RGB primaries.
- Screenshots: NOT producible from this worker (no browser on the VM). To verify
  visually: open `game/stage-test.html?stage=shrine` (or any canon land) and
  `game/index.html` for a fight — check fighter rim/key separation, soul-glow tint,
  motes, and per-stage grade. Before/after screenshots should be captured by a
  browser-capable pass.
- Mobile perf: light budget documented (14 max, +2 vs before — the only additions are
  the shadowless character keys); motes capped at 110 points on mobile; no new
  shadow-casting lights. Frame-time measurement needs a device pass (flagged).
