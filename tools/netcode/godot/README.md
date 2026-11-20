# Godot 4 netplay — wiring guide

Design target for Western Heart. Two vendored options; they solve different halves.

## The two lanes

### Lane 1 — netfox (`netfox/`, MIT)
**Use for:** server-authoritative multiplayer with rollback-flavored responsiveness.
- `RollbackSynchronizer` node: client prediction + server reconciliation per entity. Implement `_rollback_tick()` on fighters.
- `TickInterpolator`: render 60+ fps from a lower network tickrate.
- `netfox.noray`: free NAT punchthrough (public relay `tomfol.io:8890` for prototyping; self-host noray for shipping).
- Built-in network-condition simulator (latency/packet loss) — test without `tc`.
- Physics + rollback supported (v1.35+).

**Topology:** client-server (one player hosts, or a dedicated headless Godot server). Server is authoritative; clients predict.

### Lane 2 — snoringcat godot-rollback-netcode (`snoringcat-rollback-netcode/`, MIT)
**Use for:** GGPO-style peer-to-peer rollback, especially if the web export matters.
- Pure GDScript, **no GDExtension** — the only rollback option that runs in Godot **web exports** (GDExtensions don't load on web).
- Pluggable transport: ENet (desktop), WebSocket, **WebRTC** (browser P2P).
- `NetworkOrchestrator` autoload, 60 FPS frame driver, `ReconcilableState` base class for fighters, NTP-style frame sync.
- Consume via `addons/rollback_netcode/` + the `Netcode` autoload; see its `QUICKSTART.md`.

**Topology:** peer-to-peer rollback (GGPO-shaped). No authoritative server needed for 1v1.

## Recommendation for Western Heart

| Build | Pick | Why |
|---|---|---|
| Web (Three.js, now) | `game/netplay/` (lite-rollback, already wired) | Browser-native, zero-dep, proven by `mirror.mjs`. |
| Godot 4 desktop (target) | **netfox** RollbackSynchronizer | Most mature, AssetLib, noray punchthrough, server-authoritative = cheat-resistant ranked. |
| Godot 4 web export (if ever) | **snoringcat** rollback | Only GDExtension-free rollback; WebRTC transport matches the web prototype's topology. |

**Determinism law (both lanes):** the fighter sim must be integer/fixed-point, seeded RNG in lockstep, no wall-clock in gameplay logic, fixed update order. Godot's built-in physics is NOT guaranteed deterministic across machines — run combat on a custom fixed-point sim (port `game/netplay/sim/fighter-sim.js` semantics), use physics only for visuals.

## Matchmaking + accounts

See `tools/netcode/matchmaking/` — self-hosted Nakama (Docker) for accounts, 1v1 matchmaker, leaderboards; `nakama-client/` is the Godot SDK. For pure P2P without accounts: noray (vendored in netfox) or the `game/netplay/signaling/` room server for web.

## Transports

- **ENet** ships inside Godot (`ENetMultiplayerPeer`) — MIT, reliable-UDP, the default for desktop. Single-header maintained fork: zpl-c/enet (IPv6).
- **WebRTC** in Godot 4 works for P2P data; in web exports use the browser's own WebRTC (as `game/netplay` does).
- **Steam**: GodotSteam + `SteamMultiplayerPeer` for Steam P2P lobbies (swap-in replacement for ENetMultiplayerPeer). Documented, not vendored — only relevant if we ship on Steam.
