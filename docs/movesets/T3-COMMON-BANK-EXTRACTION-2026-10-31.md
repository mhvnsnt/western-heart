# T3 Common Bank Extraction — 2026-10-31

Lane: G2 provenance continuation (owner order 2026-10-31: finish flushing out
the guess-grade animations fighter by fighter). This closes the **U4 gap**
named by the T3 condition-code decode (PR #1370,
`docs/movesets/T3-CONDITION-CODE-DECODE-2026-10-31.md` §6): the shared
common bank that `common:N` branch targets resolve to had no JSON in either
repo. Extraction and documentation only — no moveset or game data changed.

## What the common bank is

Tekken 3 keeps one shared move bank, `divmot99_common.bin` (bank type 99,
**332 move rows**), next to the 20 character banks. Every character bank's
move index (`move_index`, 4023 slots) contains three kinds of entries:
local rows, the empty sentinel `0x3FFFFFFF`, and `0x40000000 + N` — a
reference to common row `N`. Standing basics, throws and shared transitions
route through it (e.g. Jin's standing hub `RP` branch targets `common:60`
under condition 0 and `common:61` under the condition-36 variant selector).

Two engine facts govern how the shared data resolves, both verified against
the Tekken3Remake engine port (`fight_sim.py`: BranchFind `0x8002E078`,
MoveBranchStep `0x8002DC3C`, `move_lookup`):

1. **Branch targets always resolve through the active character bank.**
   A matched branch's target slot is looked up in the *fighter's own*
   move index — including branches that live in common rows and in the
   shared branch blocks below. `divmot99` itself has **no move-index
   section** (its section 2 is size 0), which is why reading one out of it
   produces garbage: there is none.
2. **`<common>` branch records are CALLs into an EXE-resident table.**
   A branch record with command `0xC00C` does not target a move; it splices
   a shared branch list into the current list. The list is `entry` records
   from the branch-block table compiled into the game EXE at VA
   `0x80017C78` (SLUS_004.02 file offset `0x8478` — the same address the
   engine port records as `COMMON_ROWS` for JP Rev.1, re-verified here for
   the USA EXE by a unique structural signature match), starting at record
   `target_slot`, followed by a RETURN record (`0xC00D`). Across all 21
   banks there are 5,139 CALL records referencing **36 distinct blocks**.

## Provenance chain

All inputs are in-repo; the extractor is the same family that produced the
20 character banks (`teardown/tekken3/tools/local/moveset_extract.py` +
the Tekken3Remake `motion` parser), driven by the new companion tool
`teardown/tekken3/tools/local/moveset_common_extract.py`:

- `TEKKEN3.BNS` record 279 (sector 15104, 240,468 bytes;
  `teardown/tekken3/bns-table.pkl`, `docs/BNS-ORGANIZATION-PATTERN.md`)
  sliced out as `divmot99_common.bin`. SHA-256
  `2a8c754adf1f222fbac64bb9775cfdec106ce017f12e45803ec572baa6ffd241` —
  equals n0madic's original-disc index value for divmot99.
- The EXE branch-block table is read from the in-repo `SLUS_004.02`.

## Validation (all measured by the tool, asserted in code)

- **Control:** divmot03 (King, BNS record 283, SHA-256 `8ae24919…`)
  re-extracted with the same pipeline reproduces the shipped
  `moveset_king.json` exactly (moves and move_index).
- **Reference closure:** the character banks reference exactly 332 distinct
  common rows — `common:0` … `common:331` — and all 332 exist in the
  extraction. No referenced `common:N` is missing.
- **Branch accounting:** the 332 common rows' branch lists account for all
  1,521 records of divmot99's branch section (section 0), no residue.
- **Blocks:** all 36 referenced blocks extracted; every block's declared
  `entry` count is consistent across all its call sites, every block is
  followed by a RETURN record, and no block contains a nested CALL.

## Artifact

`teardown/tekken3/movesets/moveset_common.json` (+ `.csv` frame-data sheet)
in the same schema as the 20 character-bank artifacts, with two additive
top-level keys: `branch_blocks` (the 36 EXE-table blocks in the same branch
record schema, keyed by start record index) and `move_index_note`.
`move_index` is `[]` — the section does not exist in this bank (see above).

## What this does and does not unblock

- The provenance branch-walk can now step *through* common rows and CALL
  blocks instead of treating them as dead ends (the `no-branch` blocker
  class). The G2 re-sweep consumes this artifact together with the decoded
  condition table (PR #1370).
- This is graph data only. The game ships no common anim pack
  (`game/assets/anim/t3/` has no `common` directory), so mappings whose
  proven terminal row is a common row are graph-proven but not yet
  landable in game data; the G2 continuation doc counts and names them as
  the follow-up wiring item (bake a common rows pack + resolver support).
- DATA-CORRECTED is not play-verified; nothing here promotes any mapping.
