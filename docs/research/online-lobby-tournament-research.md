# Online systems research — lobbies, tournaments, netcode (2026-10-22)

What the teardowns actually contained, what the web confirmed, and what
we built from each. Sources are cited; nothing is invented.

## 1. TTT2 online structure

**Teardown status**: the repo's TTT2 teardown
(`teardown/tekken-tag-tournament-2/`) covers roster, stages, and
extraction tooling — it has NO lobby/network packet captures. The
lobby structure below comes from public documentation (tekkenpedia,
contemporary reviews), cross-checked across multiple sources.

**TTT2 Player Matches** (tekkenpedia — eng.tekkenpedia.com/wiki/tekken_tag_tournament_2/):
- **Quick Match**: randomly matched against an opponent. No rank effect.
- **Custom Match**: set search parameters, pick a lobby from a list.
- **Create Session**: host a lobby with specific settings; opponents join.
- **World Arena**: lobby rooms themed as world areas; send fight requests
  to players in the room; a **tournament room** randomly matches
  competitors — the direct ancestor of our single-elim mode.
- Ranked matches are separate; player matches never touch rank.
- Lobbies support **spectators**; there is a **Replay Channel**.
- While matchmaking, players wait in a **training zone** (not a static
  "searching" screen) — a UX detail worth stealing later.

**TTT2 netcode**: contemporary press (TheSixthAxis, entertainmentfuse)
reports it as a modified version of Soul Calibur 5's netcode, tuned for
TTT2 — "the best online mode for a fighting game at launch," with combo
timing that "hasn't noticeably changed at all" versus offline. This is
the bar: rollback tuned until combos survive.

**Built from this**: Quick Match (matchmaking queue → auto-lobby),
Custom Match (lobby directory), Create Session (host with settings),
World Arena fight requests, the tournament room → our bracket mode,
player-match/ranked separation (ranked flag is a stub).

## 2. SFV Battle Lounges

**Teardown status**: the repo's SFV teardown (`teardown/street-fighter-5/`)
covers cast/models — no lobby captures. Structure from public
documentation (reviews, patch notes, EventHubs).

**Battle Lounge** (theouterhaven.net review; pushsquare.com; eventhubs.com):
- Lounge **owner customization**: length of a set before rotation,
  **passwords**, **private slots**, enable/disable character select for
  speed matches, and more — "closely emulate the feel of running real
  casual sessions."
- **8 players** per lounge (raised from 2 in the March 2016 update),
  plus a **spectator option**.
- **Connection restriction**: lounges can require 2–5 / 3–5 / 4–5 / 5
  bars; results filterable by restriction; green/red join icons.
- **Rematch button** on online rounds.
- Ranked and Casual matchmaking exist outside lounges (CFN).

**Built from this**: lounge settings (rotation length, password,
spectate toggle, max players 8), spectator role, host-controlled match
start with rotation pair, connection-bar restriction (designed, stubbed
— needs real ping measurement), rematch-equivalent (tournament NEXT
MATCH / lobby re-queue).

## 3. Netcode approaches (GGPO / rollback)

Already researched in depth: `docs/research/netcode-multiplayer-streaming.md`
(2026-10-16) — lite-rollback vendored and proven, WebRTC transport,
signaling server, mirror.mjs ALL PASS, Nakama/noray/netfox lanes
documented. This round added the **bridge layer** (input codec +
sim adapter + determinism harness) and the **lobby signaling protocol**;
the architecture doc is `docs/netcode/NETCODE-ARCHITECTURE.md`.

Key GGPO points applied:
- Predict remote inputs, simulate, resimulate on misprediction
  (lite-rollback: input prediction, snapshot ring, confirmed-frame
  watermark, per-frame checksums).
- `inputDelay = 2` frames — GGPO-standard rollback reducer.
- Determinism contract: integer/fixed-point math, seeded lockstep RNG,
  no wall-clock, no `Math.random` in the tick.
- Desync detection via confirmed-frame checksums (not mispredictions).

## 4. Tournament brackets

No teardown contained a bracket implementation to pull (TTT2's
tournament room is matchmaking, not a visible bracket). The single-elim
engine (`game/js/tournament.js`) is original, using standard
competition seeding (1vN / 2v(N-1) placement), 4/8/16 fields, BYE
walkovers, CPU fill, and serializable bracket JSON so the lounge host
can broadcast it. This matches how the FGC actually runs lounge
tournaments on top of SFV-style lobbies.

## 5. Daily challenges / rotating events

SFV's Challenge Mode (tutorials, combo trials, missions for Fight Money)
is the lineage: pre-defined missions, tracked and rewarded with
currency. Ours: 24 challenges as data, deterministic daily rotation
(same dailies worldwide), weekly themed events with reward multipliers,
progress from real match stats, rewards paid into the unlockables
registry (titles/frames now; full catalog later).

## 6. What's NOT pulled (honest gaps)

- No packet captures of TTT2/SFV netcode exist in the teardowns; the
  GGPO behavior is from the vendored lite-rollback implementation and
  public documentation, not from reverse-engineered game code.
- Connection-bar measurement (real ping/jitter stats) is stubbed.
- Ranked ladder, leaderboards, and accounts are Nakama-lane future work.
