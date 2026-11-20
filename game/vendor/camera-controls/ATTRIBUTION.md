# camera-controls — attribution & wiring

- **Upstream:** https://github.com/yomotsu/camera-controls
- **Version vendored:** 3.1.2 (2026-10-22)
- **License:** MIT (see LICENSE in this dir)
- **File:** `camera-controls.module.js` — the package's ESM build, unmodified.
  Zero imports; requires `CameraControls.install({ THREE })` before use.
- **Import map:** `"camera-controls": "./vendor/camera-controls/camera-controls.module.js"`

## Why
Owner directive 2026-10-22: real-time rendered cutscenes with characters
animated in-engine. The game's camera code is hand-rolled per scene.
camera-controls gives smooth damped `setLookAt` / `fitToBox` transitions —
the standard tool for cutscene camera direction and a photo-mode camera in
the creation suite — without rewriting the fight camera.

## What uses it
- `game/js/camdirector.js` — `WHCamDirector`: cutscene shot list
  (shot = {pos, target, dolly, transition}), photo-mode orbit rig.
- Fight camera untouched; director is opt-in per scene/cutscene.
