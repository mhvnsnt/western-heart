# PIECE 6 — UR data wiring (QUEUED — spawn AFTER Pieces 1–4)

**Source:** Jay's order 2026-11-08 ~12:11 — all the Urban Reign stuff the Tekken brawler mode doesn't have, into HeartMind. Coordinator task add, 2026-11-08 ~12:12.
**Sequencing:** AFTER Pieces 1–4. Same fight code — do NOT run in parallel with Pieces 1, 2 or 4. Spawn when Pieces 1–4 have all reported. (May run in parallel with Piece 5 — different files — coordinator decides at spawn time.)
**Same rules as Pieces 1–4:** fresh clone of main (`fcaa8b1d` — verify HEAD after cloning; no sparse checkouts; no /tmp clones), small verifiable commits, repo tests green (zero new failures), one PR, no merge, proof watched in motion.

## All from the repo itself, no new download

1. **Textured swap:** 72 textured GLBs (`teardown/urban-reign/textured-models/charNNN_textured.glb`, 733 images) → `game/assets/models/street-reign/charNNN.glb` via the repo's own `ur_embed.py` / `ur_batch_embed.py` (re-run with textured GLBs as base for the 31 pmot fighters so clips survive; copy all 72 under the existing names; re-run the roster resolution check 72/72). The 31 animated game GLBs carry embedded clips the textured GLBs do not — it is NOT a plain file swap.
2. **Per-fighter pool assignment:** the 829 general-pool motions (`game/assets/anim/ur-general-{normal,30frame,weapon}/`) assigned per fighter where a measured basis exists; UNMAPPED with reason where none exists, never invented.
   - COORDINATOR NOTE — overlap with Piece 4: Piece 4's data section also assigns these pools. Piece 4 runs FIRST. Your item 2 verifies/completes what's left — do NOT redo or contradict Piece 4's assignments; if Piece 4 already assigned a motion, keep it and say so.
3. **484 named UR moves → moveset-library templates** (closes the Lane 8 pending-ingest row for UR). Names are `motdatName` annotations already in `game/assets/movesets/ur-charNNN.json` (27 fighters); 402 records stay unproven (307 in another fighter's bank, 92 with no bank, 3 borderline, 5 P1 jump kicks with no source bank anywhere) — unproven stays unproven, never assigned.
4. **Audio:** ADX music + sound banks (`teardown/urban-reign/sound/ok_adx/adx/` + `audio/`) converted into the game's existing sound path (`game/js/audio.js`, fetch + decodeAudioData takes WAV). No audio in git — remote hosting or build-time generation, same rule as the DW audio.
5. **Stages:** verify the 6 registered UR arenas in `game/js/stages.js` actually load and play (they are OBJ + builder `urstage`). stage020 stays BLOCKED (both readers fail identically, EOF, no op-0 terminator — the unblocker is the Redux Editor on Windows, Jay's machine) — do NOT force it, report it as blocked.

## Guardrails (same as Pieces 1–4)

- CANON LAWS (Jay): there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul), pickable as Phantom. "Devil" may appear ONLY in OUR own way and language, NEVER in the Devil Within way. Pantera is male (he/him); every other fighter by name only, no guessed pronouns.
- STANDING RULE (Jay 2026-11-08): top-level industry-standard way, from their source and code — not hand-tooled, not homebrewed, fully wired up, landed in the repo, from research, never guessing. Our own code is thin glue only.
- No commercial game code/models/art/audio/logos/dialogue copied into the game, even privately — measure and rebuild in our own code.
- If any item hits a real blocker, stop that item at the blocker, write the exact blocker + what would unblock it, and report — do not hand-build a workaround and call it the fix.
- Update `HEARTMIND-COMPLETION.md` (C2/C3/C4/C7 rows) with measured evidence if scores move.
- Proof: live, phone-size, video, each item shown working — proof under `~/workspace/western-heart-audit/proof-ur-all/`, NOT /tmp.
- DISK: VM quota freed 2026-11-08 ~11:27 but the edge moves — on EDQUOT stop, delete ONLY own partials, report exact error + bytes written, never touch `~/workspace/video-mocap` or `browser_downloads` (Jay's files, never delete).
- Workdir for the clone: `~/workspace/ur-data-wiring/repo` (fresh single-branch clone of main, HEAD verified `fcaa8b1d`). Branch: `ur-data-wiring`.
