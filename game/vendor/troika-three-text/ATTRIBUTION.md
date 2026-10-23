# troika-three-text — attribution & wiring

- **Upstream:** https://github.com/protectwise/troika (packages/troika-three-text)
- **Version vendored:** 0.52.5 (2026-10-22)
- **License:** MIT (see LICENSE in this dir)
- **Files (all unmodified ESM builds):**
  - `troika-three-text.esm.js` — main entry
  - `troika-three-utils.esm.js` — `troika-three-utils` 0.52.5 (MIT)
  - `troika-worker-utils.esm.js` — `troika-worker-utils` 0.53.0 (MIT)
  - `webgl-sdf-generator.mjs` — `webgl-sdf-generator` 1.1.1 (MIT)
  - `bidi.mjs` — `bidi-js` 1.1.0 (MIT)
- **Import map** (game/index.html):
  - `"troika-three-text": "./vendor/troika-three-text/troika-three-text.esm.js"`
  - `"troika-three-utils"`, `"troika-worker-utils"`, `"webgl-sdf-generator"`,
    `"bidi-js"` → the files above.

## Why
SDF-based 3D text for three.js: parses TTF/OTF directly, worker-offloaded
layout, any-material patching (lighting/shadows/fog keep working). The game
needs crisp in-world text: fighter nameplates, floating damage numbers,
arena signage, cutscene titles — without canvas-texture hacks.

## What uses it
- `game/js/labels3d.js` — `WHLabels`: nameplate + damage-number + banner API.
- Loaded lazily by `game/js/integration.js`; falls back to sprites if troika
  fails (e.g. worker blocked).
