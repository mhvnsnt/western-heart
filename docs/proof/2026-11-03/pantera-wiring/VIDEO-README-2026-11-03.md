# Pantera fight video — proof for the wiring fix (PR #1548)

`pantera-fight-proof-20261103-fixed2.mp4` — 13.5 s, 270 frames at 20 fps, recorded from the
actual game (the served build's own three.js renderer, real fight vs Zen on shrine; frames are
the game's renderer output — the DOM HUD layer is not in these frames). Pantera runs the FIXED
fighter.js (main since PR #1548, squash 392352ed). Full per-phase data: `video-pantera-log.json`.

| Phase | Result |
|---|---|
| idle fighting pose (3 s) | held stance, no input |
| attack `1` | strike, 11.1 dmg, no throw |
| attack `2` | strike, 11.1 dmg, no throw |
| attack `d/f+2` | strike, 19.8 dmg, no throw |
| attack `u/f+4` | strike, 16.1 dmg, no throw |
| string `f+2,1,1` (sequential presses) | full string lands, 35.9 dmg, **no grapple clip** |
| combo `1,2` (sequential presses) | 22.3 dmg, **no grapple clip** |
| grapple `1+3` (deliberate) | throw executes (grab → flip → slam), **23.5 dmg** |
| grapple two-finger (`1`, then `3` 0.1 s later) | chord rescue converts to `1+3`, throw anim executes (0 dmg vs bankless Zen — anomaly A1 family, see diagnosis doc) |
| grapple `2+4` (deliberate) | does not complete vs bankless Zen (0 dmg — anomaly A1, pre-existing, carried in the diagnosis doc) |

Capture method (for reproduction): local serve of the game tree, headless Chromium,
identity gate on `p1.char.id === 'pantera'` + `roundState === 'fight'`, game paused and
stepped deterministically (`_update(1/120)`, capture every 6 steps = 20 fps), each frame
rendered by `game.arena.renderer.render(scene, camera)` and read from the renderer's own
canvas. On this VM the GL backend must be Mesa/llvmpipe (`--use-angle=gl` under Xvfb);
SwiftShader costs 40–160 s per presented frame here and the compositor paths
(screencast / captureScreenshot) effectively never present.
