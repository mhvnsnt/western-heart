# Federation source files (worker 59, 2026-10-22)

Raw converted movelists from the DOA4 and KOF-3D federation rounds — the pre-ingest
source data for the moveset library.

- `doa4/` — 17 files, 1,206 moves. DOA4 command lists (deadoralive.fandom.com) converted
  to Tekken notation under the INPUT-TO-MOVE FIDELITY LAW: P/K/G + directions ->
  1/2/3/4 + directions, Tekken frame conventions @60fps, one specific predictable
  Tekken input per move. Damage/frames estimated from archetype and flagged
  estimated in each file's `source_page`. Fighters: alpha152, bayman, bradwong,
  christie, ein, eliot, genfu, hayate, helena, hitomi, kokoro, lamariposa
  (= Lisa Hamilton), leifang, leon, spartan458 (= Nicole-458), tengu (= Bankotsubo),
  zack.
- `kof3d/` — 6 files, 93 moves. KOF XIV movelists (snk.fandom.com) converted the same
  way: iori, kyo, leona, terry, king, mai. Iori Yagami is Deathfang's moveset
  source (user-approved exception). Full 3D teardown of KOF: Maximum Impact 2
  in progress — these XIV files are the bridge until MI2 extraction lands.

## Ingest linkage (worker 47's lane — read-only reuse)

The central library lives at `moveset-library/` (MOVE-DATABASE.json, MOVE-SLOTS.json,
pantera-moveset.json). These federation files are NOT yet ingested into
MOVE-DATABASE.json — the ingest mapping against the real schema is the next step.
Worker 47's files are not edited here; the linkage is documented, not duplicated.

## Claimed map

`moveset-library/movesets/CLAIMED-MAP.json` is the single source of truth for which
source fighter feeds which WH/Ashlane character. Each file carrying a lock also has
a `wh_claimed_map` provenance field.

## INTEGRATION LAW compliance (standing user directive 2026-10-22)

Tekken is the architectural authority — nothing here creates a parallel DOA/KOF
subsystem:

- **Inputs:** every move is stored in Tekken notation (1/2/3/4 + directions).
  No DOA P/K/G scheme and no KOF A/B/C/D scheme survives in the data.
- **Feel:** frame data, damage scale, and combo structure follow Tekken
  conventions @60fps (INPUT-TO-MOVE FIDELITY LAW). Animations are sourced;
  timing is Tekken.
- **Fighters:** wired fighters land in `game/assets/movesets/` as roster peers
  (e.g. `vainabel.json` sits alongside `armor-king.json`, `deathfang.json`) —
  never in a separate DOA/KOF roster, select screen, or menu.
- **Renders:** DOA4 roster T-poses in `docs/proof/` are review artifacts for
  mapping picks. When a picked fighter enters the game, it enters as a
  Tekken-style select entry with attire ladders — never a "DOA roster" screen.
- **Ingest:** when these files are ingested into MOVE-DATABASE.json, moves land
  in Tekken move slots organized by Tekken input/limb conventions, not by
  source-game categories. Source game is provenance metadata only.
- **Backend staging only:** the `doa4/` and `kof3d/` directory split below is
  source provenance for the source law (claimed vs free), not a menu or system
  structure. It never surfaces in-game.
