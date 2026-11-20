# Nipple.js — Attribution

**Library:** nipplejs — a virtual joystick for touch and mouse
**Author:** Yoann Moinet
**Upstream:** https://github.com/yoannmoinet/nipplejs
**License:** MIT (see `LICENSE` in this directory)
**Vendored version:** v0.10.2 (official published build from npm / jsDelivr)

## Files

- `nipplejs.js` — official v0.10.2 UMD build (byte-identical to the published npm package).
- `nipplejs.min.js` — official v0.10.2 minified UMD build.
- `LICENSE` — upstream MIT license text.

## Verification

- SHA-256 (recorded at vendoring, 2026-10-23):
  - `nipplejs.js`: `b6a612a11381a67a0f0c16166448183e1c160609d370713a1aa5625d1c087253`
  - `nipplejs.min.js`: `e11f26c34e1410801d6f2c691d307a79725c993b4af6fd7b8c74d3c0d84c291d`
  - `LICENSE`: `c2b08e655eae157edbeced89a20f684ff83b588f05813332440f7ccde09a3e33`

## Usage in Western Heart

Loaded by `game/index.html` before the game module graph and wired in
`game/js/input.js` (`InputManager._bindJoystick`) as the mobile virtual
joystick. It maps the left-thumb directional vector to the game's existing
directional input state (`axisX`, `_udStick` tap-vs-hold); the PSX action
buttons (`.act-btn` / `data-btn`) are untouched and keep their own handlers,
so multi-touch (stick + buttons) works. If the vendored build ever fails to
load, `input.js` falls back to the previous hand-rolled touch binding.

Copyright (c) 2014 Yoann Moinet <yoann.moinet@gmail.com> — all rights
reserved under the MIT license.
