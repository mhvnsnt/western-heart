# Western Heart netplay — web prototype

GGPO-style rollback multiplayer for the browser (Three.js) build, wired and tested.

## What lives here

| Path | What |
|---|---|
| `sim/fighter-sim.js` | Deterministic 1v1 fighter sim (integer fixed-point math, no floats, no RNG): walk, jump, LP/HP/LK/HK, block, hitstun/blockstun, pushback, KO, 60 s round timer. This is the **reference sim shape** the real Three.js combat must follow to be rollback-safe. |
| `vendor/lite-rollback/` | `@zakkster/lite-rollback` 1.2.1 (MIT) — zero-GC rollback session: input prediction, snapshot ring, rollback + re-simulate, confirmed-frame watermark, per-frame checksums. See `vendor/lite-rollback/ATTRIBUTION.md`. |
| `vendor/lite-rollback-webrtc/` | `@zakkster/lite-rollback-webrtc` 1.1.0 (MIT) — `RTCDataChannel` transport (`createHost`/`createJoiner`). See `ATTRIBUTION.md`. |
| `mirror.mjs` | **Determinism + rollback proof.** `node mirror.mjs` — two independent sessions, 3600 frames each, scripted fight, seeded delayed channel. Scenario A (delay == channel): 0 rollbacks, checksums equal every confirmed frame. Scenario B (channel > delay): 1100+ rollbacks, max depth 4, 0 desyncs, checksums equal. Exit 0 = PASS. |
| `demo/index.html` | Playable browser demo. **Local mirror test** (1 tab, you = P1 gold vs scripted P2, 6-frame simulated net) or **WebRTC versus** (open in 2 browsers, manual SDP copy/paste — zero server). Serve the `game/` tree over HTTP and open `netplay/demo/`. |
| `signaling/server.js` | Minimal WebSocket signaling server (room codes, 2 peers/room) for real matchmaking without SDP paste. `npm install && node server.js` → `:8765`. Game traffic stays P2P; the server only relays SDP/ICE. |

## Design decisions

- **Rollback, not lockstep, not server-authoritative.** Fighting games need local input to feel instant; rollback gives zero input delay with corrections hidden by re-simulation. Server-authoritative (netfox-style) is the Godot-target option — see `tools/netcode/godot/README.md`.
- **P2P over WebRTC data channels.** 1v1 = 2 peers; no relay server in the data path, lowest latency. NAT traversal via public STUN (Google's) works for most home NATs; symmetric NATs need TURN (not bundled — add a coturn instance when shipping).
- **inputDelay = 2 frames (33 ms).** The single biggest rollback reducer: gives the network a head start before inputs take effect. GGPO-standard practice.
- **Determinism contract for the real combat sim:** integer or fixed-point math only; seeded RNG advanced in lockstep; no wall-clock, no `Math.random`, no float physics in gameplay logic. Render interpolation reads the sim state but never writes it. Test with `mirror.mjs`-style checksum comparison before ever shipping netplay.
- **Desync detection:** `checksumAt(confirmedFrame())` compared periodically; `onDesync` fires on true divergence (not misprediction). Demo HUD shows the checksum live.

## Wiring into the Three.js build (next step, not done here)

1. Port `fighter-sim.js`'s state layout to the real combat state (positions, velocities, HP, attack/hitstun timers) as typed-array fields.
2. Make the Three.js combat tick call `simulate(fields, inputs, frame)` at fixed 60 Hz; render from `session.fields` (or interpolated between ticks).
3. Reuse `demo/index.html`'s Host/Join flow; swap manual SDP for `signaling/server.js` rooms.
4. Run the mirror proof against the REAL sim before enabling versus.

## Test evidence

`node mirror.mjs` (2026-10-16, node on this VM):
```
PASS [A lockstep-clean (delay 2 == channel 2)] frames=3600 confirmed=3599/3599 rollbacks=0/0 maxDepth=0/0 desyncs=0/0
PASS [B real-rollback (delay 2 < channel 6)] frames=3600 confirmed=3595/3595 rollbacks=1117/1149 maxDepth=4/4 desyncs=0/0
ALL PASS
```
