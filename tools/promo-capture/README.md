# promo-capture — HUD-off, deterministic in-engine capture (Western Heart)

Capture tooling only. It drives the real game build in headless Chrome (Playwright, SwiftShader) and never edits game code
or saves anything into the game. Owner focus 2026-11-27: models, animations and promo clips from the extracted game data
(see HANDOFF.md "OWNER FOCUS"). Output is PRIVATE until the owner says otherwise.

## What it does
- **Deterministic frames** (`vclock.js`, injected before page scripts): `requestAnimationFrame`, `performance.now` and
  `Date.now` are virtualised after `__vclock.begin()`. Each `__vclock.step(ms)` runs exactly one game frame, so a slow
  software renderer still yields a smooth 30 fps sequence (`dt = 1000/60` gives clean 2x slow motion).
- **HUD off**: hides `#hud`, the touch pad/buttons, pause, banners and free-camera bars with an injected stylesheet.
- **Camera**: gates the authored fight camera with the arena's own free-camera gate (`arena.setFreeCamera(true)`, the same
  gate `game/js/free-camera.js` uses) and places the camera every frame from the live fighter positions — two-shot,
  single-fighter focus, yaw/height/fov per shot. On exit the authored camera recomputes itself.
- **Real inputs**: Playwright key events through `game/js/input.js` (Digit1..4 = 1/2/3/4, WASD = directions; P1 faces +x).
- Optional promo look: `BLOOM=strength,threshold` (capture-time only; default game is 0.85,0.8).

## Scripts
| Script | Purpose |
|---|---|
| `pantera-moves.mjs <outDir> ["1;b+1,4;..."]` | Real-input hit test, Pantera vs Zen: damage dealt, clips Pantera's mixer actually played, peak-frame stills. Appends `rows.jsonl`. Compare against `game/assets/anim/t7/king/graph.json` (expected anim + T7 damage per move). |
| `trailer-capture.mjs <outDir> [startShot]` | 900-frame (30 s @ 30 fps) shot list, Pantera vs Zen, one folder of JPEG frames per shot. |

Run against the live build (default `https://western-heart.pages.dev`) or a local server via `WH_URL=http://127.0.0.1:8822`.
`npm i playwright` if the repo's node_modules are absent; Chrome at `/usr/bin/google-chrome` or set `CHROME=`.

## Rules
- Private projects: commercial base data is fine in private captures; anything public still follows
  `docs/PROMO-CINEMATIC-KIT.md` (no teardown models in released/sold material) until the owner customizes it.
- media-proof-standard: look at check frames before calling a clip done; ffprobe + full decode every encode.
