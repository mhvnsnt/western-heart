# three-nebula — attribution & wiring

- **Upstream:** https://github.com/creativelifeform/three-nebula
- **Version vendored:** 13.3.0 (2026-10-22)
- **License:** MIT (see LICENSE.md in this dir)
- **File:** `three-nebula.mjs` — the package's ESM build, unmodified.
  Imports `three` (resolved by the game's import map).
- **Import map:** `"three-nebula": "./vendor/three-nebula/three-nebula.mjs"`

## Why
Owner playtest bug 2026-10-22: "HIT EFFECTS — current ones look prototype —
pull Tekken's hit effects and replace." The game's `_spawnImpact` hand-rolls
8 sprite blobs per hit. three-nebula is a JSON-driven GPU particle engine
(emitters, behaviours, zones, JSON presets) — the standard way to get
Tekken-grade impact bursts, block sparks, KO explosions and dust without
hand-rolling particle code per effect.

## What uses it
- `game/js/hitfx-nebula.js` — `WHHitFX`: JSON presets
  (`impact`, `heavy`, `ko`, `block`, `dust`, `surge`) + `spawn()` API.
- Layering (tool-unification law, 2026-10-22): the game's `HitFX`
  (`game/js/hitfx.js`) owns hit presentation (spark/ring/flash/hitstop).
  Nebula LAYERS GPU particle richness on top for heavy/KO hits via the
  `Game.prototype._spawnImpact` patch in `game/js/integration.js` — it
  never replaces HitFX. Designers author Nebula JSONs into
  `game/assets/fx/` and register via `registerJSON()`.

## Preset workflow
Designers author effects in the Nebula designer, export JSON, drop into
`game/assets/fx/`, register in `hitfx-nebula.js` `PRESETS`. No code per effect.
