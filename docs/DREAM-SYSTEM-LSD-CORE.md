# Western Heart — Dream System core (LSD dream system, Phase 2)

Branch: `phase2/lsd-dream-core` — MERGED to main (2026-11-20 slice; files live at `game/js/dream-system.js`, `game/data/dream-stages.json`, `game/dream.html`, `test/dream-system.test.mjs`). Wired into God Within mode 2026-11-26 (branch `godwithin/wiring-20261126`): one dream night plays between lives on every death — see `docs/GOD-WITHIN.md` and `game/js/godwithin.js`.
Owner orders: "pull them in and wire into Western Heart with WH canon + WH
characters (never clones)" and "make the game PLAY better" (2026-11-20).
LSD is a CORE building block for Western Heart, not a side piece.

## What shipped in this slice

A playable slice of the LSD dream system wired into Western Heart as its
dream-progression/ranking core. Open `game/dream.html`, press
BEGIN THE DREAM, walk with WASD / arrows (or the on-screen pad).

| Piece | File | What it is |
|---|---|---|
| DreamSys state object | `game/js/dream-system.js` | Pure ES module, no imports, no DOM. Timer (15 ticks/s), mood accumulators, journal (save block), all 6 link kinds, scores, flashbacks, special days, texture cycle, ambience. |
| WH dream data | `game/data/dream-stages.json` | 8 WH dream stages, 7 WH entities, fixed/facing/extra/scripted link tables, fall rules, 6 special days, 16 ambience families, headings, scripted walks. |
| Playable slice | `game/dream.html` | Top-down canvas dream-walk: move, log chunk/entity moods, wall/facing/scripted/extra/character links, falls, timer, day-end graph plot, shards payout, flashback replay. |
| Hub wiring | `game/side-games.html` | 4th playable prototype card ("Dream of the Palace") → `dream.html`. |
| Tests | `test/dream-system.test.mjs` | 21 node tests, all passing (`node test/dream-system.test.mjs`). CI runs `test/*.test.mjs`. |

## The loop (what the player feels)

1. **Enter a dream.** One dream is one day. The dreamer (Pantera, Demonio,
   or a Wandering Soul) wakes in a WH dream stage — Palace of Dreaming,
   Phantom Marketplace, Octagonal Shrine, Tree of Life, Plains of Chi-U,
   Helix Palace, Shrine of the Blade, Central Mountain.
2. **Walk and touch.** Every chunk entered logs its mood; every soul
   touched logs theirs. The HUD shows the day point forming live.
3. **The day plots.** When the timer ends (or the dreamer falls off the
   edge of the world), the day point plots on the 365-day graph in its
   colour band — black, blue, green, cyan, red, pink, yellow, white.
4. **Tomorrow starts from yesterday.** The graph point picks the first
   chunk with that mood, and the next dream starts there. The loop is the
   ranking: the graph IS the progression.
5. **Links move you.** Fixed wall links, random wall links (timer % 16),
   facing links (±44°), extra links (Tree of Life), scripted walks
   (Palace), character-sent links (bump Scimitar, walk near Phantom),
   falls. Fixed + facing links are the 30 navigation goals; flag 13 can
   never be completed — the decomp says so, and WH keeps the quirk
   honestly instead of silently fixing it.
6. **Flashbacks.** Score above 9,999,999 with a kept memory unlocks
   FLASHBACK: replay kept moments (16 s each), no logging, no graph
   point, the day does not advance.

## Sources — used whole vs built (PULL-WORKING-COMPLETE LAW)

Owner law 2026-11-20 ~15:05 EST: prefer the project that ALREADY has the
material pulled apart AND put back together, working — pulled in WHOLE.
A candidate counts only if VERIFIED complete AND working.

- **figglewatts/LSDRevamped (MIT, v1.0.0 FINAL)** — complete + working as
  a Unity/C# remake. Cannot run in WH's static vanilla-JS web build
  (no Unity runtime). Used as the working reference: its DreamSystem.cs
  structure is the shape this module follows.
- **TheShovel/lsd-dream-emu-ds, `lsd-web/js/game.js`** — the ONLY JS
  implementation found (repo search "LSD dream emulator javascript": 0
  repos; code search for DreamSystem JS: 56 hits, only this one is LSD).
  All 1,509 lines read. It IS a real JS port of Revamped's loop
  (DreamSequence / Journal / DreamSystem, 60–360 s dreams, 19×19 spawn
  map, special days, flashbacks, TriggerLink entities). USED AS THE
  WORKING-JS BASE: the class shape, constants and flow of
  `game/js/dream-system.js` come from it. BUT it is NOT verified
  complete + working: no README, no demo/index.html, 0 stars, no tests
  for it, STR video paths stubbed ("aren't decoded in this port"),
  needs the LSD ISO + full lsd-web engine + converted LSD data, and it
  declares NO licence (upstream Revamped is MIT). So it counts as the
  closest working JS, not as a verified whole-pull.
- **klnuno/lsd-decomp docs/engine (MATCHING, 1,447/1,447 functions)** —
  the verified spec. Where the JS port and the decomp disagree, THIS
  BUILD FOLLOWS THE DECOMP. Divergences (all marked DIVERGENCE in the
  code):
  1. Graph eval: Revamped/TheShovel mean + banded-last (±2) → decomp
     `sum/count + last/3`, wrap past ±9.
  2. Spawn-pick: 19×19 spawnMap → decomp `Stage_FindChunkByMood` scan
     + arrival-point / `chunkKey % count` rule; no match → stage 1 random.
  3. Links: TriggerLink entities + random-linkable → decomp 6-kind
     `Link_Find` tables (fixed/facing/extra/scripted/character/random/fall).
  4. Flashback gate: entity-count > 100 → decomp unlockScore
     > 9,999,999 + ≥1 memory; 10-slot {stage, place, rotation, length,
     day} store with `timer % 9` overflow.
  5. Timer: random 60–360 s → decomp per-start-stage limits
     (60…600 s); the timer is NOT reset by links.
  6. Fade colour: threshold rules → decomp 3×3 band table.
- **figglewatts/libLSD (MIT)** — C# LBD loader. Same stack wall as
  Revamped; and WH stages are WH-authored JSON, not LSD LBD files
  (commercial game data stays out of the public WH repo). Reference for
  the chunk format shape only (20×20 tiles, 12-byte records, 7 slots).
- **WH-internal** — `game/js/stage-levels.js` read in full: fight-stage
  LEVELS geometry, not tile/chunk streaming; no reuse.
  `game/js/worldgen/seeded-rng.js` read in full: mulberry32, explicitly
  "NOT for gameplay-critical randomness" — NOT the PSY-Q LCG the decomp
  specifies, so the LCG is inline in the module (3 lines, documented).

## Pieces with no complete working source

- The LSD dream loop as a JS module in WH's static web build — built as
  above (TheShovel base + decomp corrections).
- The 6-kind link tables as executable WH logic — built from the decomp
  spec (TheShovel has no link tables).
- WH dream stages/link data — WH-authored JSON (WH canon by definition).
- The WH canvas dream-walk shell + WHIdentity/shards wiring — WH-original,
  following `side-games.html` patterns.

## Numbers (all from the decomp, verified in tests)

- Chunk 0xA000 square, 20×20 tiles of 0x800; 7 map slots (dreamer's
  chunk + 6 hex neighbours — odd rows shifted half a chunk).
- Mood axes s8 -9..9; resolve `sum/count + last/3`; wrap past ±9.
- Timer 15 ticks/s; wall links only on `timer % 16 == 0`; random link
  `rand() % 6` stages 0–5 (current shifts to next).
- Facing links need yaw within ±44° and walking forward.
- Scores: 1,000,000/nav flag, 50,000,000 for all 30, −11,024/dynamic
  link, floor 0; instance = record points ×1000, clamped 0–50,000,000.
- Flashbacks: `rand() % 3 == 0` keeps the moment, max 10, overflow
  `timer % 9`, 16 s each.
- RNG: PSY-Q LCG `state*0x41C64E6D+0x3039`, bits 16–30.
- Texture sets on a 40-day clock (1/2/3/4 sets); ambience family
  `(day + stage) & 15`.

## WH canon notes

- Stage grids + dream lengths follow the LSD table's SHAPE (same grid
  sizes and second counts, matched by grid shape). Places, names, moods,
  links and entities are WH canon: no LSD stage names, no Grey Man, no
  LSD entities appear anywhere in the slice.
- Dreamer: Pantera / Demonio / Wandering Soul (cosmetic in v1 — the
  dreamer changes the label, not the mechanics; documented in the code).
- Shards payout: 20 base per day dreamed + 5 per navigation goal held
  (WH payout rule, documented in `dream.html`).

## Proof status

- 21/21 node tests pass (`node test/dream-system.test.mjs`): LCG, mood
  resolve (incl. the decomp's own (8,−4)→(−9,−5) yellow and (4,−4)
  cyan examples), colour table, Link_Find, ±44° facing, scores,
  flashback store/gate, journal round-trip, chooseStart, texture clock,
  special days, wall-link gating, random/extra/fall links, a full
  simulated day, and the shipped data file's integrity.
- A scripted multi-day headless playthrough (walk/touch/link/time-up
  across days, no browser) is in the lane checkpoint.
- **PROOF GAP (honest):** browser-capture proof (screenshots/video of
  `dream.html` running) is BLOCKED — Chromium is SIGTRAP-broken
  box-wide. The page was verified by module tests + headless simulation,
  not by a live browser run. Parent own-eyes gate required before the
  owner sees it; a browser lane should capture the page when Chromium
  is fixed.

## Sources (for the record)

- klnuno/lsd-decomp `docs/engine/dream-system.md`, `links.md`,
  `stages-and-places.md`, `randomness.md` (fork: mhvnsnt/lsd-decomp).
- figglewatts/LSDRevamped `LSDR/Assets/Scripts/Dream/DreamSystem.cs`
  (MIT) — fork: mhvnsnt/LSDRevamped.
- TheShovel/lsd-dream-emu-ds `lsd-web/js/game.js` (no licence declared;
  header: "ported from LSDRevamped").
- figglewatts/libLSD (MIT) — fork: mhvnsnt/libLSD.
- `sato/lsd/README.md` in mhvnsnt/game-reverse-engineering (Phase 1 pull).
- LSD game image: release `sato-lsd-20261120` (18 parts, verified).
  No game files were downloaded or staged by this lane.
