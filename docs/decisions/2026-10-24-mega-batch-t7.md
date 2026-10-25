# Mega-batch T7 — decision log (2026-10-24)

## What was done in one pass (scripted, no hand edits)
- Decoded T7 mot.bin at move level for 51 characters (batch) + fetched the
  3 already-decoded on private main (Alisa, Bob, Lee) + Raven/Chloe from
  prior work = 56 move→clip maps, 0 bank anomalies.
- Parsed all 53 .mvl display files into titles + LP1/RP2/LK3/RK4 presses.
- Built a unified index for 38 WH fighters: mot moves/cancels/banks +
  display titles + TheBigTuna frame data, with an input-matched join layer
  (1,322 joined, 740 ambiguous, 2,426 unmatched of 4,488 frame rows).
- Audited the 8 live MOD fighters' moveset files on main and surgically
  patched them (script `mega-batch-t7/audit_patch.py`, verified by
  `mega-batch-t7/verify_patched.mjs` + `test/mega-batch-t7.test.mjs`).

## T8 purge (NEVER T8 for T7 Pantera — and the other 7 MOD fighters)
- Live files carried 1,411 T8 animation refs in playable moves (Pantera 215).
- T8 anim + T7-confirmed move (t7 block, TheBigTuna row, or .mvl display
  press match): anim_ref replaced with `UNMAPPED:t7-clip-pending`, kept
  playable on fallback animation, flagged `t8_anim_removed_20261024`.
- T8 anim + NO T7 evidence: entry moved to `t8_quarantine_20261024`
  (preserved in-file, NOT playable, reversible). 631 quarantined total.
- 4 string-referenced moves were restored from quarantine as UNMAPPED so
  the patch newly breaks zero strings (verified: patched unresolved string
  hits == original unresolved string hits for all 8 fighters).
- 1 slots-neutral move was restored the same way after CI caught it
  (2026-10-25): diablo slots['4'] points to '4~3' Demon Scissors, which
  the first patch run had quarantined — neutral RK4 then fell through to
  '4*' and failed input-determinism (the test's only gating failure).
  Restoring '4~3' as UNMAPPED preserves main's neutral-RK4 behavior and
  makes the gate green. Rule added to the patch script: neutral slots
  ('1'/'2'/'3'/'4') targets are never left quarantined.
- Broader follow-up (NOT done here): 556 quarantined slot VALUES remain
  across the 8 files. Their notations are T8-only until T7 clips land,
  so they stay unplayable; the resolver falling back to another move
  (rather than null) for an unmapped slot target is a resolver-lane fix.
- Deliberately NOT quarantined on guesswork alone: JGR (Reverse Jaguar
  Step) follow-ups stay quarantined because T7's own display list attests
  the stance but NOT follow-ups; Ki Charge stays quarantined (no T7 file
  attestation in our sources). Both are one-line restores from quarantine
  if T7 documentation proves them.

## MOD damage now actually live
- The game reads move BODY damage (`fighter.js` getRealMove returns
  mv.damage); t7 blocks were never used for damage. Body damage diverged
  from MOD on 1,789 entries across the 8 fighters (e.g. Pantera LP1 body
  11 = T3-scaled, MOD 9). This patch syncs body := MOD where the t7 block
  is wired and numeric-single. Multi-hit strings ("13,16") are skipped
  (per-hit logic is a follow-up, not silently flattened).
- Remaining numeric-single mismatches after patch: 0. String→chord
  violations: 0 (re-verified, PR #1007's fix held).

## Join honesty
- JOINED-BY-INPUT rows are input-matched hypotheses, NOT file-verified
  move identity. AMBIGUOUS rows (same input, several display titles —
  e.g. LP1+RP2 maps to 6 King throws differing by position) are never
  forced. The true notation↔mot-move join still needs cancel-walk or live
  extraction; the 0x8000-bank clip bytes remain the known blocker (keys
  are exact: bank + index into main MOTA).
- Display lists omit basic singles (no standalone LP1 display for King):
  singles join via frame data + wavu names, not .mvl. Documented, not hidden.

## Tap-for-audio removal (owner 2026-10-24)
- SUPERSEDED (2026-10-25): this PR's own audio edits (hint-div removal,
  howto SETTINGS toggle, `audio.js` setMuted) were REVERTED to main's
  versions. A parallel lane landed the same owner directive on main first
  (menus.js Settings sheet: MUTE ALL + SOUND toggle rows, tap hint and
  show-timer removed, music unlock preserved). Keeping both would ship two
  competing mute systems over the same master gain, so this PR now carries
  no audio-file changes of its own; the merged result keeps main's
  implementation. Original implementation, for the record:
- Removed the `TAP TO ENABLE SOUND` hint div + its show-timer. Audio now
  enables silently on the first natural tap (pointerdown listener + nav /
  fight-start calls kept — invisible, no interstitial).
- Sound on/off moved to SETTINGS: howto screen has an AUDIO toggle
  (`audio.js` setMuted, persisted as `wh_audio_muted`, master gain 0/1).
  Browser autoplay policy still applies: sound starts on first gesture,
  which is now any normal tap, not a dedicated unlock tap.

## What is NOT in this PR (explicitly)
- DLC moveset files for Birodo, Jotei, Kunimitsu, Geese, Noctis, Negan,
  Lidia (no files on main yet): data is ready (unified index + maps),
  files are NOT created here — creating select-screen fighters without a
  playtest risks breaking fight load. Next lane builds them from this data.
- Fahkumram / Leroy: no mot.bin, no TheBigTuna; wavu fetch failed on a
  local browser-service error (not retried per tool guidance) — needs a
  live-browser fetch by the parent lane.
- Kaggle GPU notebook is prepared (docs/research/kaggle-t7-batch-notebook.ipynb)
  for parallel clip analysis; it was NOT executed by this lane (no live
  browser), so no GPU speedup is claimed for this pass. Execution is a
  parent browser task.
- Pre-existing unresolved string hits (7–43 per fighter) are unchanged by
  this patch and remain a follow-up lane.

## Revert-guard resolution (2026-10-25): main's chord rows merged in
- git_merge.py refused the first merge attempt: main's PR #1043 chord fix
  (standing LP1+RP2 clips) changed one entry each in demonio.json and
  diablo.json after this PR's base, and this branch's older copies lacked
  those lines. Resolved surgically, 3 lines per file, no other changes:
  demonio `1+2__main` name/anim/t3_row r32 -> r92 (T3 jin row 92);
  diablo `1+2__main` r37 -> r133 (T3 heihachi row 133). This PR's MOD
  damage sync on those entries (demonio 5, diablo 33, both equal to their
  t7.damage) is KEPT — main's change did not touch damage, so there is no
  field conflict. Verified after the edit: 0 T8 anims, 0 MOD mismatches,
  quarantine counts unchanged (demonio 93, diablo 66), diablo 4~3 neutral
  restore intact.

## Combat-systems re-sync (2026-10-25): main's pantera annotations merged in
- Main's PR #1045 combat-systems lane changed 3 pantera entries after
  this PR's base (powerCrush/screw annotations from wavu T7 data):
  SS.2 gained screw=true + screw_source, db+1+2 and uf+3+4 gained
  powerCrush=true + powerCrush_source. This branch's pantera was
  re-patched from main's new pantera with the same scripted rules
  (T8 purge + MOD sync + quarantine + restores); the re-patch differs
  from the branch pantera in ONLY those 3 entries, quarantine identical
  (106), 0 T8 anims, 0 MOD mismatches. ui_sources: main dropped one
  screen-menu source line (Base_OnlineMenu.png); this branch follows
  main (screen-menu keeps 7 sources, still sourced).

## Branch-update merge (2026-10-25): main merged into the branch to resolve pantera adjacency
- Plain line merge cannot merge this PR's pantera: main's PR #1045
  annotation on `db+1+2` sits immediately before `db+1+2,2` and
  `db+1+2,3+4`, which this PR quarantines (T8 anims). The modification
  hunk and the deletion hunk are adjacent, so both git merge and
  merge-file report a conflict even though the correct result is
  unambiguous (verified entry-by-entry in the re-patch step above).
- Resolution: branch updated with a merge commit (parents: branch head
  + main). Its tree is main's tree plus this PR's 25 files, with
  pantera = the re-patched file (main's annotations + this PR's
  purge/sync/quarantine). No main-side content is dropped: every
  main-only file is byte-identical to main, and every PR file was
  verified against main's versions before the merge commit.

## Second re-sync (2026-10-25): main's community-mocap annotations merged in
- Main's community-mocap lane added `community_base` + `community_base_status`
  (pending-gpu-retarget) to 2-4 canon signature entries in 6 movesets
  (demonio qcf+1/qcf+P, diablo 1+4/P+K, kinpo 1+2/S, phantom D+S/d+1+2/u+1/u+P,
  scimitar 1+2/S, skull 1+2/S) plus top-level `canon_moves` updates. All 6
  files were re-patched from main's new versions with the identical
  scripted rules; each re-patch differs from the branch file in ONLY
  those annotations + canon_moves, quarantine counts identical, restores
  intact (demonio 4~3/f+3+4, diablo 4~3 slots, scimitar 3+4), 0 T8 anims,
  0 MOD mismatches. Second branch-update merge commit carries them.

## Third re-sync (2026-10-25): main's t7_motbin metadata merged in
- Main's motbin lane added top-level `t7_motbin` metadata (decoded mot.bin
  counts, banks, anim_ref format, source blob SHAs) to 6 movesets
  (demonio, diablo, pantera, phantom, scimitar, skull) with ZERO move-entry
  changes. All 6 files were re-patched from main's new versions with the
  identical scripted rules; each re-patch differs from the branch file in
  ONLY the t7_motbin top-level key, quarantine counts identical, restores
  intact, 0 T8 anims, 0 MOD mismatches. Main's new audio/UI files were
  checked against the PR test first (main.js TAP TO ENABLE SOUND occurrence
  is a removal comment only; index.html has no hint/div; menus.js MUTE ALL
  + SOUND present) and taken verbatim. Main moved once more (to 96e044f3)
  between re-patch and merge without touching any PR file, so the merge
  commit's main parent is 96e044f3 with identical PR-file content.
  Third branch-update merge commit carries them.
