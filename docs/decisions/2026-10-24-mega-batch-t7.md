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
