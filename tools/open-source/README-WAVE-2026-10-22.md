# tools/open-source/ — 2026-10-22 wave addendum (worker 22)

Addendum to `README.md` (which covers the 2026-10-19 pull-ins). The
2026-10-22 comprehensive integration pass added these. Full audit, license
log and wiring map: `docs/research/OPEN-SOURCE-WAVE-2026-10-22.md`.

## New game-side vendor libs (all MIT, ESM, in game/vendor/)

| Lib | Version | Vendored as | Wired to |
|---|---|---|---|
| cannon-es (pmndrs) | 0.20.0 | `game/vendor/cannon-es/cannon-es.js` | `game/js/physics.js` — arena props, debris, KO tumble |
| three-mesh-bvh (gkjohnson) | 0.9.16 | `game/vendor/three-mesh-bvh/index.module.js` | `game/js/hitdetect.js` — BVH hit-verify layer |
| three-nebula (creativelifeform) | 13.3.0 | `game/vendor/three-nebula/three-nebula.mjs` | `game/js/hitfx-nebula.js` — particle hit FX |
| troika-three-text (protectwise) | 0.52.5 | `game/vendor/troika-three-text/` (+ troika-three-utils 0.52.5, troika-worker-utils 0.53.0, webgl-sdf-generator 1.1.1, bidi-js 1.1.0) | `game/js/labels3d.js` — 3D nameplates/damage |
| camera-controls (yomotsu) | 3.1.2 | `game/vendor/camera-controls/camera-controls.module.js` | `game/js/camdirector.js` — cutscenes/photo mode |

Each dir carries its upstream LICENSE + an ATTRIBUTION.md with the why
and the wiring. Import map entries live in `game/index.html`.

## New pipeline tool (MIT, not vendored — CDN on the pipeline machine)

| Tool | Version | Lives at | Wired to |
|---|---|---|---|
| lip-sync-engine (biolimbo) | 1.0.3 | `tools/character-voice/lipsync/` (engine via unpkg) | `game/js/lipsync-player.js` — jaw-bone cue playback |

The 37MB acoustic model is never vendored or shipped; the game only sees
KB-sized `*.cues.json`.

## Wired this pass (were unwired)

- `tools/stable-fast-3d/` + `tools/triposr/` → `tools/tripo-intake/image-to-3d.md`
  (image→3D source path feeding the standard intake).
- `tools/procgen/arena-gen/` three.json props → `WHPhysics.loadArenaProps()`.
- `game/netplay/` demo → NETPLAY (BETA) entry in the ui-wh options menu.

## Still unwired — deliberate (see docs/decisions/2026-10-22-integration-unwired.md)

Tone.js · Chatterbox (external by design) · Materialize/ArmorPaint (app
workflows, documented) · transformers.js · Rapier · MoCapAnything ·
BlenRig 6 · WMXIX .ymg (blocked) · WWE 2K pac (blocked) · T7 uasset items
(open) · lip-sync WASM (CDN by design).
