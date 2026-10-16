# netcode/multiplayer/streaming — pull-in log (2026-10-16)

Branch: `research/netcode-multiplayer`. Every finding is wired or explicitly excluded below.

## Pulled (vendored into the repo)

| What | Source | Version | License | Landed | Why it beats what we had |
|---|---|---|---|---|---|
| lite-rollback (rollback session core) | peshovurtoleta/lite-rollback | 1.2.1 | MIT | `game/netplay/vendor/lite-rollback/` | We had no rollback core for web. Zero-GC, single-file ESM, GGPO-shaped; explicitly benchmarks Tekken-style fighters as fine. |
| lite-rollback-webrtc (WebRTC transport) | peshovurtoleta/lite-rollback-webrtc | 1.1.0 | MIT | `game/netplay/vendor/lite-rollback-webrtc/` | We had no WebRTC transport. Plugs into the session's transport contract. |
| netfox (Godot 4 netcode framework) | foxssake/netfox | main 2026-10-16 | MIT | `tools/netcode/godot/netfox/` | Most mature Godot 4 rollback/prediction framework; noray NAT punchthrough; AssetLib. |
| godot-rollback-netcode (Snoring Cat) | snoringcatgames/godot-rollback-netcode | main 2026-10-16 | MIT | `tools/netcode/godot/snoringcat-rollback-netcode/` | Only pure-GDScript (no GDExtension) Godot rollback — the only one that works in web exports; WebRTC transport. |
| nakama-godot (Godot client SDK) | heroiclabs/nakama-godot | main 2026-10-16 | Apache-2.0 | `tools/netcode/godot/nakama-client/` | Official client for our self-hosted Nakama matchmaking. |

## Built (new, additive — existing playable build untouched)

| What | Path | Test evidence |
|---|---|---|
| Deterministic 1v1 fighter sim (integer fixed-point) | `game/netplay/sim/fighter-sim.js` | `node mirror.mjs` — see below |
| Determinism + rollback proof | `game/netplay/mirror.mjs` | **ALL PASS**: A) 3600f lockstep, 0 rollbacks, checksums equal every confirmed frame; B) 3600f real-rollback, 1117/1149 rollbacks, max depth 4, 0 desyncs, checksums equal |
| Playable browser demo (mirror + WebRTC host/join) | `game/netplay/demo/index.html` | Syntax-checked; manual playtest path documented |
| WebSocket signaling server (room codes) | `game/netplay/signaling/server.js` | `node --check` clean |
| Nakama self-host | `tools/netcode/matchmaking/docker-compose.yml` | Compose config validated by inspection |
| Sunshine/Moonlight phone-playtest guide | `tools/netcode/streaming/SUNSHINE-PLAYTEST-GUIDE.md` | Research-backed (Sunshine v2026.914, Oct 2026) |

## Researched, documented, NOT vendored (with reason)

| What | Reason |
|---|---|
| someusername6/rollback-netcode (TS, MIT, npm) | Fuller-featured TS alternative (N-player, desync recovery, live demo). Documented in research doc; not vendored to avoid two competing web stacks. `npm i rollback-netcode` if we outgrow lite-rollback. |
| GGRS / bevy_ggrs (Rust, MIT) | The Rust GGPO standard; WASM-compatible. Relevant only if we go Rust/Bevy — we didn't (Godot 4 is the target). Documented. |
| ampactor-labs/two-top (phone-vs-phone brawler) | **No license file** (all rights reserved by default) — code NOT pulled. Referenced as a live proof (Bevy+GGRS+Matchbox, CI determinism across 4 platforms, APK). |
| dsnopek/godot-rollback-netcode (Snopek's classic) | Repo appears gone/renamed (GitHub 404 on the known path as of 2026-10-16); the Godot 4 AssetLib entry may still exist but the source couldn't be verified — excluded until verifiable. Snoring Cat's addon covers the same ground, MIT, verified. |
| crashtestbrandt/orbitnet (Rust GDExtension rollback) | Interesting (Rust core, 3 lanes) but **no web export support** and needs compiled GDExtension binaries per platform — heavier than both vendored Godot options. Documented. |
| Nakama server | Runs from official Docker image — vendoring a Go server into the game repo would be wrong; compose file is the wiring. |
| Sunshine / Moonlight | **GPL-3.0** — fine to run as infra, not vendored/linked into the game. Installed from official releases when needed. |
| GGPO (original, pond3r/GGPO) | Public-domain-ish reference implementation; superseded by maintained ports (GGRS). Documented as the algorithm ancestor. |
| ENet | Already inside Godot (`ENetMultiplayerPeer`); no pull needed. zpl-c/enet fork noted for standalone use. |
| Steam (GodotSteam) | Only relevant if shipping on Steam; documented, not vendored. |

## Next wiring steps (not in this PR)

1. Port the real Three.js combat state to `fighter-sim.js`'s typed-array field layout; fixed 60 Hz sim tick.
2. Swap demo's manual SDP for `signaling/server.js` rooms in the versus flow.
3. Godot 4 project: drop in `netfox` (desktop) or `snoringcat` (web export); re-run a `mirror.mjs`-style checksum proof against the GDScript sim before enabling versus.
4. Stand up Nakama via the compose file when accounts/leaderboards are wanted; add TURN (coturn) for symmetric-NAT players.
