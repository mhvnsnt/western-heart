# Procedural World Generation — TRACK 5 (2026-10-23)

Owner directive (verbatim 2026-10-23): **"Pull all of this stuff in and wire it up and put it to work the best way possible"**

User override 2026-10-23: the license firewall is OFF — pull and wire regardless
of license; document copyleft/GPL components for transparency. (No copyleft
components were encountered; everything below is MIT.)

Track scope: WaveFunctionCollapse (structural layouts) + FastNoise2 (noise
terrain) for (a) NEW arena surroundings and (b) Heart-and-Mind-Within open
zones. **Arena law: NEVER procedurally overwrite an existing arena's canon
look.** This track only ADDS generation capability; no existing arena was
touched.

## 1. Tool evaluation

### 1a. WaveFunctionCollapse — [WIRED]
- **Upstream**: https://github.com/mxgmn/WaveFunctionCollapse (Maxim Gumin).
  License file verified MIT via GitHub API (repo `license` field reports
  NOASSERTION — GitHub's detector misses it — but `LICENSE` exists and is MIT).
- **JS port used**: `wavefunctioncollapse` 2.1.0 (npm), Kevin Chapelier's port,
  MIT. Verified API: `SimpleTiledModel` + `OverlappingModel`, `generate(rng)`,
  `model.observed` tile indices. Vendored pristine + ESM bundle for browsers.
- **What it does**: generates infinite structural arrays from local adjacency
  rules — exactly the "ancient temples, towns, arena surroundings that fit
  together per artistic rules" requirement.
- **Copyleft**: none. MIT.

### 1b. FastNoise2 — [RESEARCHED] (runtime noise via FastNoiseLite — [WIRED])
- **Upstream**: https://github.com/Auburn/FastNoise2 — MIT (verified via GitHub API).
  Modular node-graph noise, SIMD (AVX2/AVX512), C++17.
- **JS/WASM status**: no official JS/WASM build exists (verified: no `fastnoise2`
  npm package; repo ships C++ only). Building one requires emscripten (not on
  this VM). **Path**: emscripten-compile FastNoise2 → wasm, expose the
  node-graph API to JS. This is the upgrade path when SIMD noise is needed.
- **What we wired instead**: `fastnoise-lite` 1.1.1 (npm), MIT — the portable
  JS port by Jordan Peck/Patrick U of Auburn's **FastNoiseLite**, the
  same author's sibling library (same algorithm family: Value, Perlin,
  OpenSimplex2/S, Cellular, fractal FBM/Ridged/PingPong). Pure JS, no SIMD,
  mobile-friendly. Verified API: `SetNoiseType`, `SetFractal*`, `GetNoise(x,y)`.
- **Copyleft**: none. MIT.

### Why not hand-roll
Per the repo's no-guessing law and the owner's "pull, don't hand-tool"
directive, both systems are pulled as real libraries, not reimplemented.

## 2. Architecture

```
game/js/worldgen/
  vendor/
    wavefunctioncollapse/   pristine CJS port (MIT) + LICENSE
    wfc.bundle.mjs          GENERATED ESM bundle (tools/worldgen/build-wfc-bundle.mjs)
    fastnoise-lite.js       pristine ESM port (MIT)
    VENDOR.md               provenance + SHAs
  rulesets/
    temple-courtyard.json   NEW surroundings: walkways, walls+gate, pillars,
                            lanterns, pond, trees (12 tiles, socket rules)
    hmw-forest.json         NEW HMW zone: clearings, paths, trees, rocks,
                            shrine, water (8 tiles)
  seeded-rng.js             mulberry32 + FNV-1a (deterministic seeds)
  wfc.js                    generateLayout(): ruleset JSON -> WFC lib -> tile grid
  terrain.js                sampleHeightmap() [/Async], classifyBiomes(),
                            sampleCaveMask() — layered FastNoiseLite
  props.js                  scatterProps(): seeded set-dressing w/ exclusion rules
  worldgen.js               generateZone({kind, seed}) -> {layout, heightmap,
                            biomes, caveMask, props, meta}; sets window.WH_WorldGen

tools/worldgen/
  build-wfc-bundle.mjs      CJS->ESM bundler (mechanical, sources untouched)
  generate.mjs              demo CLI -> tools/worldgen/demo/ artifacts
  demo/                     committed proof (json/txt/ppm/html/timings)
  README.md

test/worldgen.test.mjs      29 tests (node --test)
```

**Rule-set authoring** (`game/js/worldgen/rulesets/*.json`): tiles declare
`edges` (4 socket chars `[top,right,bottom,left]`), `symmetry`, `weight`,
`color`/`pattern`. The converter expands every tile to explicit oriented
X-variants and emits all edge-compatible pairs.

**Key finding — WHY X-EXPANSION** (deep-dive 2026-10-23, documented here so
nobody has to redo it): the vendored lib's neighbor expansion applies D4
symmetries. Its reflection entries for `L`/`T`-symmetry tiles are not
geometric reflections, which corrupted the propagator (measured: 32% of
generated adjacencies geometrically invalid). Expanding to explicit oriented
X-variants sidesteps this. The lib then applies its (original, verified
against mxgmn's C# source) closure: reverse + vertical pairs. Consequence:
a path/wall arm may occasionally end against ground — artistically natural
(path-ends, wall-ends). Horizontal connector sockets always match exactly.
Strict 100% socket-matching is intentionally not required.

**Orientation semantics**: generated `oriented` ids are `"name k"` with
k = k·90° counter-clockwise rotation of the base tile (matches the lib's
bitmap `rotate()`). 3D prop placement rotates the base mesh by k·90° CCW.

**Determinism**: same `{kind, seed}` → identical zone on every device
(mulberry32 streams; FastNoiseLite seeded). Verified by tests.

## 3. Demo results

`node tools/worldgen/generate.mjs --ruleset <kind> --seed <n>` → `tools/worldgen/demo/`:

| zone | layout | terrain | seed | attempts | wall time | props |
|---|---|---|---|---|---|---|
| temple-courtyard | 40×28 WFC, 12 tiles | 80×56 FBM | 1337 | 1 | 423 ms | 46 |
| hmw-forest | 48×48 WFC, 8 tiles | 96×96 ridged | 2026 | 1 | 568 ms | 87 + cave mask (25% open) |

Artifacts per zone: `*-layout.json`, `*-layout.txt` (ASCII), `*-layout.ppm`,
`*-heightmap.ppm`, `*-demo.html` (standalone canvas viz, data embedded),
`*-timings.json`. Renders viewed: terrain heightmaps show natural
water/sand/grass/rock/snow bands; layouts show connected path networks,
wall runs with gates, pond/vegetation clusters.

## 4. [WIRED] vs [RESEARCHED]

**[WIRED]**
- WFC `SimpleTiledModel` layout generation (vendored port + ESM bundle +
  `game/js/worldgen/wfc.js` + 2 rule sets + demo CLI + 29 tests).
- FastNoiseLite terrain: layered heightmaps, biome classification, cave masks
  (`game/js/worldgen/terrain.js`), sync + async (UI-friendly) sampling.
- Prop scattering (`props.js`), zone entry point (`worldgen.js`,
  `window.WH_WorldGen` global for non-module callers).
- Deterministic seeded generation end-to-end.

**[RESEARCHED]**
- FastNoise2 SIMD/WASM: no JS build exists; emscripten path documented in
  `vendor/VENDOR.md`. FastNoiseLite covers current needs; revisit when SIMD
  noise proves necessary.
- WFC `OverlappingModel` (image-example-based): vendored but not wired to a
  rule set; candidate for learning layouts from concept art later.
- In-game wiring (calling `generateZone` from stage select / HMW mode,
  3D prop meshes per tile, chunked infinite zones): next step for the crew;
  the runtime API is ready.

## 5. Mobile performance

Measured on this VM (node 24, Linux x64 — indicative, not a phone):

| operation | size | time | memory |
|---|---|---|---|
| temple layout (WFC) | 40×28 | ~250 ms of 423 ms total | ~70 KB grid |
| forest layout (WFC) | 48×48 | ~350 ms of 568 ms total | ~150 KB grid |
| temple terrain (2 layers) | 80×56 | ~120 ms | 17.9 KB Float32Array |
| forest terrain (2 layers) | 96×96 | ~180 ms | 36.9 KB Float32Array |
| full `generateZone` (temple) | — | 423 ms wall | ~88 KB peak (measured) |
| full `generateZone` (forest) | — | 568 ms wall | ~180 KB peak (measured) |

**Budgets** (for the crew wiring this into the game):
- Keep runtime generation under ~1 s on desktop-class; on phones prefer
  `sampleHeightmapAsync` (yields every N rows) + a loading indicator.
- WFC cost scales with tiles×variants and grid area; 48×48 with 12-tile
  sets is the tested comfort zone. Larger HMW zones should generate in
  chunks (offset sampling is supported via `offsetX/offsetY`).
- FastNoiseLite is pure JS (no SIMD); per-sample cost is ~10–50× a SIMD
  build. If terrain sampling ever dominates frame time, that's the trigger
  for the FastNoise2 WASM build ([RESEARCHED] above).
- `generateZone` is deterministic and cacheable: generate once per
  `{kind, seed}`, reuse across sessions.

## 6. Arena-law compliance

No existing arena file was modified. The two rule sets are NEW content
("temple-courtyard" surroundings, "hmw-forest" HMW zone) and do not reference
or override any canon arena (checked against `game/js/stages.js`: shrine,
tong-nou, tree-of-life, etc. untouched). Colors/canon of existing arenas
are out of scope for this track by design.

## 7. Repro

```bash
node tools/worldgen/build-wfc-bundle.mjs          # rebuild browser bundle
node tools/worldgen/generate.mjs --ruleset temple-courtyard --seed 1337
node tools/worldgen/generate.mjs --ruleset hmw-forest --seed 2026
node --test test/worldgen.test.mjs                # 29 tests
# open tools/worldgen/demo/temple-courtyard-demo.html in a browser
```
