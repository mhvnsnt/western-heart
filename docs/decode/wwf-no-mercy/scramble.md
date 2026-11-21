# WWF No Mercy — scramble mechanism

First fix lane for this game: Phase 2 Lane D, 2026-11-20 (PR #1804, `game/assets/movesets/cainelias.json`).

## The mechanism (M9 — wrong FileTable window)

WWF No Mercy (N64, 2000) stores its data in a ROM file table with several
overlapping ID windows. The ones that matter for animation refs:

- **ROM file IDs** — the animation bank runs from `0x2DD9` (FirstAnimationFileID)
  to `0x4473` (5,787 clips in `teardown/wwf-no-mercy/animations/manifest.json`).
- **Move AnimIDs** — the move menu indexes animations from base `0x3322`
  (FirstMoveAnimationID). The repo manifest records `anim_id = file_id − 0x3322`
  per clip (verified on all 5 cainelias refs and on anim_3322).
- **Menu file IDs** — VPWStudio's `MenuItems_Moves.cs` carries a separate
  `file_id` per menu row (e.g. `0x4b7b` for the Chokeslam from Hell row), which
  is neither the clip file ID nor the AnimID.

Reading a clip ID from the wrong window silently points at a different clip
(or a wrong frame count) while still looking like a valid reference — that is
the scramble for this game. The earlier W3b extraction-window error (fixed by
the W3c-corrected re-extraction, PR #1755, merged 2026-11-19) is the same
failure mode at the bank level.

## How it was solved

No cipher to break. The community decode is AKI-Club/VPWStudio
(move-menu parsing + FileTableDB, 19,462 ROM files) plus the repo's own
teardown: `teardown/wwf-no-mercy/animations/manifest.json` (measured nframes
per clip), `teardown/wwf-no-mercy/moves/moves-enriched.json` (1,682 menu rows
with anim_file_id, anim_id, name, menu label, raw damage, and the
`anim_table_matches_menu` flag), and `teardown/wwf-no-mercy/animations/MOVE-ANIM-MAP.md`.

The one genuine window ambiguity found so far: the "Swinging Chokeslam" menu
row — the menu window says clip `0x3a5c` (anim_id 1850), the anim-table window
says `0x3a5e` (anim_id 1852); the DB flags `anim_table_matches_menu: false`.
Undecided as of PR #1804; see `cainelias/fixed-vs-scrambled.md` §8.

## Status

- Clip files + manifest + enriched DB: present in-repo, verified live 2026-11-20.
- `game/data/moveset-library/banks/wrestling.json` (4,409 moves): refs resolve
  (4,409 unique anim refs, one per move); damage/frames partly estimated —
  verification + estimate replacement is follow-up work, not this fix.
- `game/assets/movesets/cainelias.json` 5 refs: re-resolved in PR #1804
  (frames corrected; 2 taunts misclassified as throws + the 3A5E ambiguity open).
