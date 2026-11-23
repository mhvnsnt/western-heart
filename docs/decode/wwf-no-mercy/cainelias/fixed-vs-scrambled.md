# CAIN ELIAS — fixed vs scrambled

- **Repo file fixed:** `game/assets/movesets/cainelias.json`
- **Fix PR:** #1804 (https://github.com/mhvnsnt/western-heart/pull/1804)
- **Date fixed:** 2026-11-20
- **Fixed by:** Phase 2 Lane D (scramble sweep)

## 1. What was fixed
- What was wrong, in plain words: the file's 5 WWF No Mercy throws carried clip frame counts (and the seconds + recovery derived from them) that were estimated by analogy, not measured from the clips they point at. All 5 were wrong — 0 of 5 matched the clips' real frame counts. A player would see throw timings built on wrong totals (e.g. the 121-frame Undertaker 01 clip was timed as 45 frames; the 15-frame Swinging Chokeslam was timed as 18).
- Before: 5 moves with analogy-estimated bank_total_frames 21 / 43 / 18 / 45 / 44. After: measured bank_total_frames 69 / 86 / 15 / 121 / 65, with bank_total_s and recovery recomputed by the file's own formulas. 15 numbers changed, nothing else.
- File hashes: before sha256 `8203a91e1ff421d83799ed962990a2fb35c8496f75e41d7261b1f49ad0afdd84` → after sha256 `8870b7e7c641e55d87fa09c81aa783b0bca4ab741aba6de50f3a4500a9f981ae`.

## 2. How it was scrambled
- The scramble mechanism for this game/file: mechanism M9, wrong FileTable window (see `docs/decode/wwf-no-mercy/scramble.md`). The 5 refs were flagged SUSPECT in `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md` ("5 No Mercy anim_refs are SUSPECT (wrong FileTable window) — flagged, not fixed"). The No Mercy ROM has several overlapping ID windows (ROM file IDs, move AnimIDs, menu file IDs); reading a clip ID from the wrong window silently points at a different clip or a wrong frame count.
- Evidence it was scrambled (not just wrong-character): the numbers that proved it — the repo's own animation-bank manifest (`teardown/wwf-no-mercy/animations/manifest.json`, 5,787 clips) lists measured nframes per clip file; the 5 cainelias bank_total_frames matched 0 of 5 (69 vs 21, 86 vs 43, 15 vs 18, 121 vs 45, 65 vs 44). The convention bank_total_frames = manifest nframes is independently confirmed by `teardown/wwf-no-mercy/animations/clips/anim_3322.npy` (nframes 13) = `game/data/moveset-library/banks/wrestling.json` move mk-0000 frames.total 13.

## 3. Decoding steps
- Tool used: no new tool. The solved decode is the repo's own No Mercy teardown: `teardown/wwf-no-mercy/animations/manifest.json` (W3c-corrected re-extraction, PR #1755, merged 2026-11-19) + `teardown/wwf-no-mercy/moves/moves-enriched.json` (1,682 menu rows from AKI-Club/VPWStudio).
- Exact steps, in order, so the decode is reproducible:
  1. Confirm each ref file exists: `teardown/wwf-no-mercy/animations/clips/anim_34EB.npy` (read directly, 10,892 B) and the other four as entries in `teardown/wwf-no-mercy/animations/manifest.json`.
  2. Read measured nframes per file_id from the manifest (34EB 69, 37A5 86, 3A5E 15, 43D4 121, 4405 65).
  3. Cross-check clip identity in the enriched DB by anim_file_id (34EB "Chokeslam from Hell", 37A5 "Two Handed Chokeslam", 43D4 "Undertaker", 4405 "Undertaker 02"; 3A5E has no DB row — see §8).
  4. Replace bank_total_frames with manifest nframes; bank_total_s = nframes / 60 rounded to 3 decimals; recovery = bank_total_s − startup − active (startup 0.4, active 0.033 on all 5 rows — the file's own identity).
  5. Verify with the line-anchored transform (workdir `phase2-lane-d-nont7/transform_cainelias.py`): assert all 15 old values at their lines, assert the result parses as JSON, record before/after sha256.
- What the solved decode changed vs our raw version: 15 numbers (5 frames, 5 seconds, 5 recoveries). No clip bytes, no refs, no names, no damage values changed.

## 4. Cracking steps
- No cracking needed; community decode already solved this. The No Mercy file table and animation format were decoded by the AKI-Club/VPWStudio community tools and the repo's own W3c re-extraction (PR #1755). No cipher was broken in this fix.

## 5. Decomp / recomp steps
- No decomp exists for this game and none was used. The solved version came from community re-documentation (AKI-Club/VPWStudio move-menu parsing + FileTableDB) and the repo's teardown (`teardown/wwf-no-mercy/`), wired into Western Heart through the manifest + enriched move DB. Nothing was recomped; the fix corrects metadata to match already-decoded clips.

## 6. Before / after proof
- Measurements (same method before and after): manifest nframes per clip vs cainelias bank_total_frames — before 0/5 match, after 5/5 match (69, 86, 15, 121, 65).
- No motion bytes changed, so no side-by-side frames or in-game visual check applies to this fix; verification is the manifest/DB cross-check plus the transform assertions (15/15 old values asserted at their lines, JSON parses, 36,988 bytes before → 36,989 after, no other bytes changed).
- Test results: no test files were modified and no game test suite was run for this metadata-only fix; the transform script's own assertions are the gate (see §3 step 5).

## 7. Sources
- AKI-Club/VPWStudio (public GitHub repo) — move-menu parsing (AnimID, FirstAnimationFileID 0x2DD9, FirstMoveAnimationID 0x3322) and the FileTableDB (19,462 ROM files).
- Repo teardown: `teardown/wwf-no-mercy/animations/manifest.json`, `teardown/wwf-no-mercy/moves/moves-enriched.json`, `teardown/wwf-no-mercy/animations/MOVE-ANIM-MAP.md` (2026-11-19, W3c re-extraction PR #1755).
- `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md` — the SUSPECT flag this fix partially resolves.
- Archive.org check (2026-11-20, checked FIRST per standing law): title search "WWF No Mercy" (50 hits) — the only game-file item is `wwf-no-mercy-prototypes` (3 prototype ROMs, June E3 Alpha / July 19 2000 NTSC / Aug 2000 alpha, 33,554,432 B each; the August ROM is flagged in the item's own review as a possibly corrupt/bad dump); no No Mercy animation dump or teardown material on archive.org. The repo's decoded clips (from the Rev-A retail ROM) were not re-sourced from archive.org — they already exist in-repo.

## 8. Known gaps / follow-ups
- The two Undertaker clips are entrance/taunt clips per the enriched DB (43D4 "Undertaker", In-Ring Entrance Taunt, raw damage 0; 4405 "Undertaker 02", Standing Taunt, raw damage 0) but are still listed in this file as throws with damage 22. Reclassifying them (or replacing them with real Undertaker throw clips) needs a coordinator/owner call — NOT changed in this PR.
- The 3A5E ref is ambiguous and NOT decided here: the menu window says the Swinging Chokeslam clip is 0x3a5c (anim_id 1850, 27 frames); the anim-table window says 0x3a5e (anim_id 1852, 15 frames); the DB flags anim_table_matches_menu false. This PR corrects the frames for the currently-referenced clip (0x3a5e, 15 frames) and leaves the ref switch open.
- Damage values and startup/active on all 5 moves remain analogy estimates (WH damage scale is not the raw DB damage: 34EB raw 25 vs file 28, 37A5 raw 40 vs file 28). 3A5E startup 0.4 s exceeds its measured 0.25 s clip — its timing fields are inconsistent and need re-derivation.
- The blanket "wrong FileTable window" flag is now localized, not sustained as a whole: file identities are correct for 4 of 5 (names match the DB), and only the 3A5E menu-vs-table mismatch remains a genuine window question.
- STATUS.md row for this fix is owed once Lane X1's docs/decode/ skeleton lands (docs/decode/ was 404 on main at PR time); this PR adds only the per-file doc, no skeleton files.
