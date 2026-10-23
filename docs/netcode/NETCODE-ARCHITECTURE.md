# Western Heart netcode — architecture (2026-10-22)

How online versus works, what is playable today, what is still
architectural, and the real constraints of browser P2P. No hype.

## The approach: rollback (GGPO), not lockstep, not server-authoritative

Fighting games need local inputs to feel instant. Rollback gives zero
input delay: both players simulate every frame immediately, predicting
the remote player's input; when the real input arrives and the
prediction was wrong, the sim rolls back to the mispredicted frame and
re-simulates. This is the GGPO algorithm (2009), and it is what TTT2
shipped — contemporary press noted TTT2's netcode was a modified version
of Soul Calibur 5's, tuned until "my combo timing hasn't noticeably
changed at all" (see docs/research/online-lobby-tournament-research.md).

Delay-based netcode (wait for both inputs every frame) is obsolete for
fighters: every frame stalls on the slowest ping. Server-authoritative
is the escalation path for ranked/anti-cheat, not the starting point.

## What exists (wired and proven)

| Piece | Where | Status |
|---|---|---|
| Rollback session | `game/netplay/vendor/lite-rollback/` (`@zakkster/lite-rollback` 1.2.1, MIT) | vendored, proven |
| WebRTC transport | `game/netplay/vendor/lite-rollback-webrtc/` (1.1.0, MIT) | vendored, proven |
| Deterministic reference sim | `game/netplay/sim/fighter-sim.js` | proven |
| Determinism + rollback proof | `game/netplay/mirror.mjs` (`node mirror.mjs` — ALL PASS) | proven |
| Playable 2P demo | `game/netplay/demo/index.html` | playable |
| Signaling + lobby server | `game/netplay/signaling/server.js` | tested (16/16 protocol tests) |
| Input codec (WH inputs → net word) | `game/netplay/bridge/input-codec.js` | tested (7/7) |
| Sim adapter + determinism harness | `game/netplay/bridge/sim-adapter.js` | tested (600-frame self-test) |
| Lobby client (rooms, ready, rotation, spectate, chat, fight requests) | `game/netplay/lobby/lobby-protocol.js` | tested (5/5 fake-server + 9/9 real-server) |
| Lobby/tournament/challenges UI | `game/js/online.js`, `tournament-ui.js` | built, needs browser playtest |

## What I added this round (worker 32)

1. **`bridge/input-codec.js`** — maps the real WH input shape
   (`InputManager`: Tekken 1/2/3/4 limbs, chords, grab, surge, dodge,
   transform, block, sidestep taps) onto the 16-bit netcode input word
   that lite-rollback's wire codec carries. Chord specials ride as limb
   pairs so the remote sim resolves them identically.
2. **`bridge/sim-adapter.js`** — `WhNetSim`: the deterministic-sim hook
   contract. FIELD_CONTRACT documents the typed-array layout the real
   combat must expose; `checksumFields` (FNV-1a) is the desync-detection
   primitive; `selfTest` runs any tick twice and compares per-frame
   checksums. `runReferenceSelfTest` proves the adapter preserves
   determinism on the real reference sim (600 frames, 0 mismatches).
3. **Lobby protocol v2** (`signaling/server.js` + `lobby-protocol.js`) —
   TTT2-style quick match / custom match (directory) / create session,
   SFV-style battle lounges (owner settings: set rotation length,
   password, private slots, spectator toggle, ranked flag), World
   Arena-style fight requests, 8-player rooms, spectators, host
   migration, quick-chat, tournament bracket broadcast, WebRTC mesh
   signaling relay. The v1 2-peer demo protocol is unchanged.
4. **`online.js` OnlineController** — ONLINE menu entry, hub, lounge
   browser/create/room, lobby UI, `NetVersus` (WebRTC + rollback versus
   on the reference sim, playable), local tournament runner wiring,
   daily-challenge screens, unlock toasts.
5. **Tournament engine** (`js/tournament.js` + `tournament-ui.js`) —
   single-elim brackets (4/8/16), standard seeding, BYE walkovers,
   CPU fill, serializable bracket JSON (broadcastable), local
   tournament flow playing real fights.
6. **Daily challenges** (`data/challenges.js` + `js/challenges.js`) —
   24 challenges as data, deterministic daily rotation (1 ember + 1
   flame + 1 inferno), weekly rotating events with reward multipliers,
   progress tracked from real match stats via additive hooks
   (no game.js/modes.js edits), manual reward claims.
7. **Unlockables** (`js/unlockables.js`) — minimal registry (titles,
   portrait frames) that challenges pay into; the full catalog drops
   in later without API changes.

## Playable vs architectural — the honest table

| Feature | Verdict |
|---|---|
| Lobby create/browse/join, ready-up, rotation, spectators, chat, fight requests | PLAYABLE (needs signaling server running) |
| Quick match (random pair) | PLAYABLE |
| Netcode versus (rollback + prediction + WebRTC) | PLAYABLE — on the **reference sim**, not WH fighters |
| Input prediction / rollback / resimulate | PLAYABLE (lite-rollback, proven by mirror.mjs) |
| Local single-elim tournaments (real fights) | PLAYABLE |
| Lounge-hosted tournament bracket broadcast | PLAYABLE (bracket syncs; matches play locally) |
| Daily challenges + weekly events + rewards | PLAYABLE (offline modes feed progress) |
| Real-fighter online versus (WH models, movesets, stages) | ARCHITECTURAL — needs the combat sim port (below) |
| Ranked ladder / leaderboards | ARCHITECTURAL — Nakama lane is researched, not wired |
| Spectating a live netplay match | ARCHITECTURAL — lobby has spectator roles; stream relay not built |

## The remaining hard work: porting the combat sim

Rollback needs **determinism**: same inputs + same state → same next
state, on every machine. The reference sim proves the pattern, but the
real combat (`game/js/game.js` + `fighter.js`) currently runs on floats,
`THREE.Vector3`, wall-clock timers, and `Math.random()`. Porting means:

1. Move gameplay state (positions, velocities, HP, timers, facing) into
   the FIELD_CONTRACT typed-array layout (fixed-point integers).
2. Replace float physics in hit detection with integer math.
3. Seed all RNG and advance it in lockstep.
4. Run the combat tick at a fixed 60 Hz, driven by the session; render
   interpolates but never writes sim state.
5. Run the mirror proof against the REAL sim before enabling versus.

`WhNetSim.selfTest` is the harness for step 5. Until then, any claim of
"online versus with real fighters" would be fake — so we don't make it.

## Browser P2P constraints (real, not theoretical)

- **NAT traversal**: WebRTC data channels need STUN for most home
  NATs (Google's public STUN is the default) and TURN for symmetric
  NATs. No TURN server is bundled — budget a coturn instance before
  shipping. Some player pairs simply won't connect P2P; the fallback
  is a relay (Nakama relay / TURN), which keeps rollback feel.
- **No authority**: P2P rollback has no referee. Fine for casual
  lounges; not for prize ranked. Cheat-resistance needs the
  authoritative-server lane (netfox on Godot, or a headless sim).
- **2 players per match**: the session, codec, and sim are 1v1. Tag
  mechanics (TTT2-style) would need a 4-input sim — designed for,
  not built.
- **Same-version requirement**: both peers must run the same sim
  build, or checksums diverge instantly. The lobby should gate on a
  build hash (stubbed, not enforced).
- **Mobile browsers**: WebRTC data channels work on mobile Chrome/
  Safari, but backgrounding the tab kills the peer connection. Matches
  are best-effort on phones.

## Tuning notes (from the teardowns + GGPO practice)

- `inputDelay = 2` frames (33 ms): the single biggest rollback
  reducer — gives the network a head start before inputs take effect.
- Snapshot ring 120 frames (2 s of history) covers real-world jitter.
- Input redundancy 4 on the wire (each packet repeats the last 4
  inputs) so single packet loss doesn't cause a misprediction storm.
- Desync detection: compare `checksumAt(confirmedFrame())`
  periodically; a true desync (not misprediction) means the sims
  diverged — the honest recovery is resync from host snapshot
  (not yet implemented).

## Roadmap

1. Combat sim port (the big one) — FIELD_CONTRACT → real fighters.
2. Mirror proof on the real sim, then enable WH-fighter netplay.
3. TURN server + connection-bar display (SFV-style 2–5 bars).
4. Ranked queue via Nakama (researched in
   docs/research/netcode-multiplayer-streaming.md) with
   server-verified results.
5. Spectator stream relay for lounge matches.
6. Resync-from-snapshot on confirmed desync.
