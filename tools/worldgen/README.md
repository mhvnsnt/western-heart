# tools/worldgen — procedural world generation pipeline (TRACK 5, 2026-10-23)

Build-time tools for WaveFunctionCollapse layouts + FastNoise terrain.
Runtime modules live in `game/js/worldgen/`. Nothing here touches existing
arenas — it generates NEW surroundings and Heart-and-Mind-Within zones.

## Quick start

```bash
# (Re)build the WFC browser bundle from vendored sources (only needed after a vendor update)
node tools/worldgen/build-wfc-bundle.mjs

# Generate a demo zone + proof artifacts
node tools/worldgen/generate.mjs --ruleset temple-courtyard --seed 1337
node tools/worldgen/generate.mjs --ruleset hmw-forest --seed 2026

# Run the tests
node --test test/worldgen.test.mjs
```

## Files

| file | does |
|---|---|
| `build-wfc-bundle.mjs` | Bundles pristine `game/js/worldgen/vendor/wavefunctioncollapse/*.js` (CommonJS) into `game/js/worldgen/vendor/wfc.bundle.mjs` (ESM). Mechanical wrap; sources never modified. |
| `generate.mjs` | Demo CLI. Runs `generateZone()` and writes proof artifacts into `tools/worldgen/demo/`: `*-layout.json`, `*-layout.txt` (ASCII), `*-layout.ppm`, `*-heightmap.ppm`, `*-demo.html` (standalone canvas viz), `*-timings.json` (perf + memory). |
| `demo/` | Generated demo artifacts (committed as proof). |

## Rule sets

Rule sets live in `game/js/worldgen/rulesets/*.json` (single source of truth;
both the runtime and this CLI read them). Format:

```json
{
  "name": "temple-courtyard",
  "tilesize": 8,
  "tiles": [
    { "name": "path", "symmetry": "I", "weight": 6,
      "color": [202,182,150], "pattern": "solid", "edges": "fpfp" }
  ]
}
```

- `edges`: 4 socket chars `[top,right,bottom,left]`. Compatibility is exact
  match. Keep it simple: `f` = open ground, `p` = path, `w` = wall.
- `symmetry`: `X` (uniform tiles ONLY), `I` (I-symmetric tiles), or `F`.
  Do NOT use `L`/`T` expecting the lib to get reflections right — the
  converter expands every tile to explicit oriented X variants (see
  `game/js/worldgen/wfc.js` header: "WHY X-EXPANSION").
- `pattern`: `solid` `checker` `border` `cross` `dots` `circle` `diag`
  (rasterized to the tile bitmap; purely visual).
- `weight`: relative frequency.

Orientation `k` of a generated tile = `k * 90deg` counter-clockwise rotation
of the base tile (for 3D prop placement).

## Demo outputs

`tools/worldgen/demo/` after running `generate.mjs`:

- `temple-courtyard-*`: 40×28 WFC layout + 80×56 terrain, seed 1337
- `hmw-forest-*`: 48×48 WFC layout + 96×96 terrain + cave mask, seed 2026

Open `*-demo.html` in any browser (fully standalone, data embedded).
