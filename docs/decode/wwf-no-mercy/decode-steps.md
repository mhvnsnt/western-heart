# WWF No Mercy — decode steps

First fix lane for this game: Phase 2 Lane D, 2026-11-20 (PR #1804).

## Re-resolving a No Mercy animation ref (the repeatable procedure)

1. **Confirm the clip file exists.** `teardown/wwf-no-mercy/animations/clips/anim_<FILEID>.npy`
   (list the directory; the contents API pages at 1,000 entries — check the
   manifest instead for bulk confirmation).
2. **Read the measured frame count.** In `teardown/wwf-no-mercy/animations/manifest.json`,
   find the entry with `file_id` `0x<FILEID>` and read `nframes` (also `kind`
   and `anim_id`). The manifest has 5,787 clips, range first `0x2dd9`, last
   `0x4473`, `move_anim_base` `0x3322`.
3. **Check the clip identity.** In `teardown/wwf-no-mercy/moves/moves-enriched.json`
   (1,682 menu rows), find the row with `anim_file_id` `0x<FILEID>` and read
   `name`, `menu_label`, `anim_id`, `anim_table_value`,
   `anim_table_matches_menu`, and raw `damage`. The row's `anim_id` must equal
   `file_id − 0x3322`; if `anim_table_matches_menu` is false, the ref is
   ambiguous between the menu window and the anim-table window — do not switch
   the ref unilaterally.
4. **Check the frames convention.** `bank_total_frames` in a moveset file means
   manifest `nframes` (confirmed: `anim_3322.npy` nframes 13 =
   `game/data/moveset-library/banks/wrestling.json` move mk-0000 frames.total 13).
5. **Write the correction.** `bank_total_frames` = manifest nframes;
   `bank_total_s` = nframes / 60 rounded to 3 decimals; `recovery` =
   `bank_total_s − startup − active` (the file's own identity on the rows
   fixed in PR #1804). Do not touch damage, move class, or the ref itself
   without a coordinator/owner call — those are judgments, not measurements.
6. **Verify.** Line-anchored transform asserting every old value at its line,
   JSON still parses, before/after sha256 recorded. Land branch → PR → merge
   only, with the instruction-gate PR body and the per-file
   `fixed-vs-scrambled.md` in the same PR.

## Tools

- AKI-Club/VPWStudio (public GitHub repo) — move-menu parsing + FileTableDB.
  Parser, not data; move names come from the menu rows + the repo manifest.
- Repo teardown tools under `teardown/wwf-no-mercy/tools/` and `teardown/wwf-no-mercy/animations/FORMAT.md`
  (npy int16, shape (nframes, 26, 3)).
- No decryption, no cipher, no decomp involved in this decode.
