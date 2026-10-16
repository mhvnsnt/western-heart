# Netcode / multiplayer / streaming — research (2026-10-16)

Researched from: GitHub trending/topics, repo READMEs and changelogs read directly, Godot Asset Library, 2026 release notes. No training-data guesses; every repo below was fetched and license-checked on 2026-10-16.

**Bottom line for Western Heart:** web build now → `game/netplay/` (wired, proven); Godot 4 desktop target → netfox; Godot 4 web export (if ever) → Snoring Cat rollback; matchmaking → self-hosted Nakama; phone playtests of desktop builds → Sunshine/Moonlight.

---

## 1. Rollback netcode — state of the art 2026

Rollback (GGPO algorithm: predict remote inputs, simulate, resimulate on misprediction) remains the standard for fighting games. It needs **determinism** — same inputs + same state → same next state, on every machine — and full state save/load. What changed since GGPO (2009, pond3r/GGPO, public-domain-ish reference):

### Web / JavaScript
- **`@zakkster/lite-rollback` 1.2.1 (MIT)** — ✅ PULLED. Single-file ESM, zero dependencies, zero allocations after construction. `createRollback` (binary ring buffer) + `createSession` (GGPO-shaped: `step`/`setLocalInput`/`feedRemoteInput`, input-delay lead, confirmed-frame watermark, `checksumAt`, stats, `packInputs`/`unpackInputs` wire codec). Its own docs benchmark a **Tekken-style fighter (~4 KB state, 7–15 frame rollback depth)** as "fine". Sister packages: `-webrtc` (✅ PULLED, RTCDataChannel transport) and `-local` (BroadcastChannel, two-tab testing).
- **`rollback-netcode` npm (MIT, someusername6)** — fuller-featured TS alternative: N-player (4+), mesh/star topologies, desync detection + auto-recovery, WebRTC transport, live demo + API docs + FAQ, **documented 60 Hz 2-player fighting-game tuning** (mesh topology, 120-frame snapshot history, input redundancy 2). Not vendored (one web stack is enough); `npm i rollback-netcode` if we outgrow lite-rollback.
- **GGRS (Rust, MIT, gschup/ggrs)** — the maintained Rust GGPO port; `bevy_ggrs` for Bevy; **WASM-compatible**. Relevant only if we ever go Rust.

### Godot 4
- **netfox (MIT, foxssake/netfox)** — ✅ PULLED. The most mature Godot 4 netcode framework: fixed-tick timing, `RollbackSynchronizer` (client prediction + server reconciliation), `TickInterpolator`, network-condition simulator, **physics + rollback** (v1.35+), noray NAT punchthrough. AssetLib-listed, Forest Brawl demo, active through Oct 2026. Client-server topology.
- **godot-rollback-netcode (MIT, Snoring Cat)** — ✅ PULLED. Game-agnostic GGPO-style framework, **pure GDScript, no GDExtension** — the only Godot rollback that works in **web exports**. Pluggable transport: ENet, WebSocket, **WebRTC**. `NetworkOrchestrator` autoload, 60 FPS frame driver, NTP-style frame sync. Consumed via git submodule upstream.
- **Snopek's godot-rollback-netcode** — the classic (Godot 3 → 4 port, AssetLib #2450). As of 2026-10-16 the GitHub repo path 404s (gone/renamed); source unverifiable → excluded. Snoring Cat covers the same ground, verified MIT.
- **orbitnet (crashtestbrandt, 2026)** — new: Rust GDExtension rollback core, 3 lanes (rollback/state/command), ENet + Steam transports. Excluded: **no web support**, per-platform native binaries, heavier operationally than both vendored options.

### Determinism — the hard requirement (applies to every option)
- Integer or fixed-point math in gameplay logic. IEEE floats *can* diverge across CPUs/platforms; Godot's built-in physics is **not** guaranteed deterministic cross-machine → run combat on a custom fixed-point sim, physics for visuals only.
- Seeded RNG advanced in lockstep (xorshift in state, never `randf()` unseeded, never `Math.random()`).
- Fixed update order, no wall-clock in sim logic.
- Proof method: two instances, same input script, compare per-frame checksums at the confirmed watermark (`mirror.mjs` does exactly this).

---

## 2. Networking libs & matchmaking

- **ENet** — reliable-UDP, sequencing, channels, fragmentation. Already inside Godot as `ENetMultiplayerPeer`. Maintained single-header fork: zpl-c/enet (IPv6, MIT). No pull needed for Godot; noted for standalone use.
- **Nakama (Apache-2.0, heroiclabs/nakama)** — ✅ WIRED (not vendored — it's a Go server). Self-hosted via `tools/netcode/matchmaking/docker-compose.yml` (Nakama + Postgres). Gives accounts, **1v1 matchmaker**, realtime socket, leaderboards, chat; server logic in Go/TS/Lua. Godot client vendored (`tools/netcode/godot/nakama-client/`); web uses `@heroiclabs/nakama-js`. $0 to self-host; one small VPS handles thousands of 1v1 matches (inputs only, KB/s per match).
- **noray** — free NAT-punchthrough relay; public instance `tomfol.io:8890` for prototyping, self-host for shipping. Vendored inside netfox (`netfox.noray`).
- **Steam** — GodotSteam + `SteamMultiplayerPeer` is a drop-in ENet replacement with free relay/NAT. Only relevant if shipping on Steam; documented, not vendored.

**Recommended 1v1 flow:** Nakama matchmaker pairs players → direct WebRTC P2P data channel (lowest latency; our signaling server or noray for NAT) → rollback session → winner verified server-side via match token → leaderboard. Fallback to Nakama relay if P2P fails.

---

## 3. Web multiplayer — WebRTC data channels

Proven path, wired in `game/netplay/`:
- `@zakkster/lite-rollback-webrtc` (`createHost`/`createJoiner`/`connectPeer`): data channel opens, `assertTransport`-verified, then `packInputs`/`unpackInputs` move inputs each frame with redundancy 4.
- Signaling is deliberately separate: manual SDP copy/paste in the demo (zero server), `signaling/server.js` (60-line WS room server) for real use.
- NAT: public STUN (Google) covers most home NATs; symmetric NATs need TURN — budget a coturn instance when shipping, not before.
- Live precedent: `two-top` (ampactor-labs) — phone-vs-phone rollback brawler, Bevy + GGRS + Matchbox WebRTC, CI proving sim bit-identical across 4 platforms, ships APK + browser build. **No license file** → referenced, code not pulled.

---

## 4. Cloud gaming — Sunshine / Moonlight (Oct 2026)

- **Sunshine** (LizardByte/Sunshine, **GPL-3.0**): self-hosted GameStream host, v2026.914.233613 (Sept 2026). Vulkan encoding, PipeWire/KWin capture on Linux, signed installers, AMD/Intel/NVIDIA hw encode + software fallback. Extremely active.
- **Moonlight** (moonlight-stream, **GPL-3.0**): clients for Android, iOS, Windows, macOS, Linux, tvOS.
- **License honesty:** GPL-3.0 is fine for our use (run Sunshine on our box, owner installs Moonlight on his phone; nothing linked into the game or distributed with it). Not vendored — install from official releases.
- **Key insight:** the web build needs NO streaming — the owner opens the hosted URL in his phone browser directly (lower latency than any stream). Sunshine/Moonlight is for the future **Godot desktop build**. Setup guide: `tools/netcode/streaming/SUNSHINE-PLAYTEST-GUIDE.md` (pairing, apps.json, Tailscale instead of port-forwarding, Bluetooth controller forwarding).
- **Caveat:** this VM has no GPU — software encoding only here. Serious stream playtests want a GPU host.

---

## 5. Dedicated servers — topology for a fighting game

| Topology | How | Verdict for WH |
|---|---|---|
| **P2P rollback** (GGPO) | 2 peers, inputs only, each simulates | ✅ **Best for 1v1.** Zero input delay, no server cost, lowest latency. Cheat-resistance is the weakness (no authority) — acceptable for casual, not for prize ranked. |
| **Rollback-relay** | P2P protocol, server relays packets when NAT blocks direct | Good fallback (Nakama relay / TURN). Keeps rollback feel. |
| **Authoritative dedicated** | Headless Godot/Nakama sim, clients predict + reconcile | Best cheat-resistance for ranked; adds server cost + one network hop of latency. netfox is built for this. |
| Delay-based (lockstep) | Wait for both inputs each frame | ❌ Obsolete for fighters — every frame stalls on the slowest ping. |

**Recommendation:** ship casual versus on P2P rollback (free, fastest); run ranked through Nakama matchmaking with server-verified results, and keep the authoritative-server lane (netfox) as the escalation path if cheating ever matters.

---

## 6. What was pulled, and what's excluded

Full log: `tools/netcode/PULLIN.md`. Pulled: lite-rollback 1.2.1, lite-rollback-webrtc 1.1.0, netfox, snoringcat godot-rollback-netcode, nakama-godot client — all MIT/Apache-2.0, all vendored with ATTRIBUTION.md. Built: `fighter-sim.js`, `mirror.mjs` (ALL PASS), `demo/index.html`, `signaling/server.js`, Nakama compose, Sunshine guide.
Excluded with reason: `rollback-netcode` npm (kept as documented alternative), GGRS (Rust-only relevance), two-top (no license), Snopek's addon (repo unverifiable), orbitnet (no web, heavy), Nakama server binary (Docker image, not vendored), Sunshine/Moonlight (GPL — infra use only), original GGPO (superseded), ENet standalone (already in Godot), Steam (ship-only).

## 7. Next steps

1. Port real Three.js combat state to the sim's typed-array layout; fixed 60 Hz tick calling `simulate`.
2. Swap demo SDP-paste for `signaling/server.js` rooms.
3. Godot 4: netfox (desktop) / snoringcat (web export); checksum-proof the GDScript sim before versus.
4. Nakama up when accounts/leaderboards are wanted; coturn for symmetric NATs.
