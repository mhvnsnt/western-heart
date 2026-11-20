# Matchmaking — self-hosted, open source

## Nakama (accounts + 1v1 matchmaker + leaderboards)

- **Server:** Heroic Labs Nakama, Apache-2.0, runs from Docker — `docker compose up -d` with the `docker-compose.yml` here. No code vendored (official image).
- **Godot client:** `tools/netcode/godot/nakama-client/` (Apache-2.0, vendored) — `Nakama.gd` autoload.
- **Web client:** `@heroiclabs/nakama-js` on npm (same protocol).

**1v1 fighting match flow:**
1. Client authenticates (device id is enough for prototyping; add Google/Apple for shipping).
2. `socket.add_matchmaker(2, 2, { mode: "ranked" })` — Nakama pairs two players.
3. On `matchmaker_matched`, both clients open a **direct WebRTC data channel** (P2P, lowest latency) using the match token for signaling auth — or fall back to Nakama's realtime relay if NAT blocks P2P.
4. Rollback session runs over the data channel (`game/netplay/` on web, snoringcat/netfox on Godot).
5. Winner reports via an authoritative RPC; server writes to the leaderboard (never trust client-reported wins blindly — verify match token + both clients' result).

**Server modules** (`modules/`, mounted into the container): write matchmaking hooks and result validation in Lua or TypeScript. Kept empty here — game logic first, anti-cheat later.

## P2P without accounts (lighter paths)

| Path | What | When |
|---|---|---|
| noray (vendored in `netfox/`) | Free NAT punchthrough relay | Godot P2P versus with no backend at all. Public instance `tomfol.io:8890` for prototyping; self-host for shipping. |
| `game/netplay/signaling/` | Our own 60-line WebSocket room server | Web versus with room codes; zero infra beyond one tiny node process. |
| Steam lobbies | GodotSteam + `SteamMultiplayerPeer` | If we ship on Steam — free relay + NAT traversal built in. Not vendored (Steam-only). |

## Cost note

All of the above is $0 self-hosted. Nakama's paid cloud exists but we don't need it — one $5–10 VPS runs Nakama + the signaling server + a coturn TURN instance for thousands of concurrent 1v1 matches (fighting matches are tiny: inputs only, ~a few KB/s per match).
