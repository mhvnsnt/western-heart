# URBAN REIGN → WESTERN HEART — CANON CONVERSION RECORD (street-reign)

**Lane:** Urban Reign sweep lane 1, wiring phase (owner acceptance
target 2026-10-20 ~20:57 CDT). **Date:** 2026-10-21.
**Universe name:** Urban Reign → `street-reign` (root `RENAME-MAP.md`:
"Urban Reign | `street-reign` | Street reign brawlers"; its phase
note: "Phase 2: street-reign (Urban Reign) — game uses UR systems").
**Companion file:** `WIRING-INVENTORY.md` (every file, its status,
its consuming path).

Rules (same as the other games' records): no invented names or
canon — every mapping below cites the repo document that already
establishes it. Anything without a documented mapping is FLAGGED,
never filled in. The conversion is ADDITIVE: teardown files keep
their source names for provenance; WH canon names apply only where
canon already establishes them.

---

## 1. What is wired (2026-10-21)

All 72 character PPKs decoded to skinned GLBs (PR #429; completion
gates G1–G5 pass — `docs/urban-reign/URBAN-REIGN-GATES.md`) and
registered in the playable build as **street-reign guests** under
their source ids:

- Models: `game/assets/models/street-reign/charNNN.glb`,
  `MODEL_URLS` keys `ur-char001`..`ur-char072` (`game/js/assets.js`).
- Roster: `game/js/roster-full.js`, bonus tier, ids
  `ur-char001`..`ur-char072`, display names `CHAR001`..`CHAR072`
  (the game's own PPK ids — see §2), shared moveset key
  `street-reign`, no tint (the GLBs are untextured — texture decode
  is still open, PR #306 stands — so no colorway is faked).
- Moveset: `game/assets/movesets/street-reign.json` (schema v2,
  `proxy: true`) — the WH engine base set (values from
  `game/js/fighter.js` built-ins). UR-native movelists replace it
  when the motion-bank decode lands (§3).
- Select screen: fighters without portraits get the monogram plate
  (`game/js/select-screen.js`) — no portrait is borrowed from
  another fighter.

## 2. Fighter identities — FLAGGED, not mapped

Canon contains **no per-fighter mapping** from Urban Reign's
roster to WH vessels/souls: `CANON.md` and `game/js/roster-full.js`
were checked (no UR fighter appears as a declared `base:`), and
`teardown/urban-reign/TEARDOWN.md` names only the protagonist
(Brad Hawk, "brawler-for-hire, Green Harbor") without a
per-PPK identity table. The repo's per-PPK identity is the id
itself (`char001`..`char072`); two of the 72 are documented in
`TEARDOWN.md` as Tekken guest models (Paul/Law) without saying
which PPKs they are.

Therefore: **no UR fighter is renamed to a WH canon name in this
wiring.** Display names are the source ids. A per-fighter identity
pass (which PPK is Brad Hawk, which are the Tekken guests, and any
owner vessel mapping) is FLAGGED for the owner/coordinator — the
evidence route is the game's own data (character-select order in
the mission/UI data + the recomp project's RAM tables), not
invention.

## 3. Documented UR → canon relationships (already in canon)

These exist in `CANON.md` today and are recorded here so the
street-reign record is complete; this lane changed none of them:

- **Cain Elias** (WH fighter): his moveset is documented as
  "Glen Kluger (Urban Reign biker gang leader) or a fitting Tekken
  character" (`CANON.md`, Vain Abel's brother entry, owner
  2026-10-19). When UR's native movelists decode, Glen Kluger's
  data is the source for Cain Elias's conversion — the specific
  PPK for Kluger is part of the §2 identity pass.
- **Slice / Ryuji-based fighter** (foundation entry, owner
  2026-10-19): moveset = "Ryuji base + The Rock's moves + wrestling
  moves from Urban Reign / Tekken / other teardown games" — UR is a
  documented move *source* for this fighter.
- **RENAME-MAP phase note:** "game uses UR systems" — UR's
  multi-fighter brawler systems are the documented Phase-2
  foundation; the mode layer is the coordinator's sequencing, not
  this lane's claim.

## 4. Stages — registry state

7 stage PPKs (`ppks/stages/`: stage003, stage004, stage020,
stage028, stage029, stage030, stage031) are extracted but their
static geometry is **not decoded** — no stage-registry entry is
claimed in `game/js/stages.js`. They are FLAGGED per file in
`WIRING-INVENTORY.md`. When the stage decode lands, each stage
gets a registry entry under the `street-reign` universe name with
its source id kept (e.g. `street-reign/stage003`), following the
model wiring pattern of §1.

## 5. What "done" means here (honest state)

- **Decoded:** character models 72/72, gates G1–G5 pass (PR #429).
- **Wired into the build:** selectable guest fighters with their
  real models + engine base moveset (this PR). Verification: the
  lane's resolution check (every roster model key → MODEL_URLS →
  existing file; every moveset key → existing file) passes 72/72,
  and `game/tests/model-key-guard.test.mjs` runs 2/3 pass in the
  lane's sparse tree with the third (file-existence) failing only
  on pre-existing fighters whose model files are not in the sparse
  checkout — all 49 flagged paths verified present on main, and
  zero street-reign entries flagged — output quoted in the PR body.
- **Not yet:** UR-native animations in the build (.gyu banks
  indexed, sampler cracked, conversion open), UR-native movelists
  (proxy in place, labeled), textures (PR #306), stage models,
  per-fighter canon identities (§2 flag).
