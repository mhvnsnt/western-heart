# PIECE 8 — Pantera HeartMind expansion (QUEUED — spawn AFTER Pieces 4 and 5)

**Source:** Jay's order 2026-11-08 ~12:17 — the base template is the mix: T5 brawler-mode progression + UR-style inputs mixed with Tekken-style inputs + all UR mechanics Tekken is missing + all Tekken mechanics UR is missing — and each character gets their own story on top of it. Pantera's is built already; now make his LONGER (double or triple) by mixing in the UR stuff and building more story for him. After his is done, the same expansion repeats per character (the mapping agent's map drives the order — do not start the next character until Pantera's expansion is done and proved).
**Sequencing:** AFTER Pieces 4 (UR feel layer) and 5 (UR structure layer) — it builds on their wiring. Do NOT run in parallel with Pieces 1, 2, or 4. Spawn when Pieces 4 and 5 have both reported.
**Same rules as Pieces 1–7:** fresh clone of main (`fcaa8b1d` — verify HEAD after cloning; no sparse checkouts; no /tmp clones), small verifiable commits, repo tests green (zero new failures), one PR, no merge, proof watched in motion.

## What to build

- EXTEND `PANTERA_FLOW` in `game/js/heartmind-flows.js` (landed in PR #1649, head `aa7b6c9b` — the existing 5 rooms THE THRESHOLD / GALLERY OF MASKS / DROWNING ROOM / FURNACE / STILL POINT stay intact as the core; EXTEND, do not rewrite). Double or triple the length: more rooms and more story beats per room, built from Pantera's own canon (his story in `game/js/heartmind.js` `HEARTMIND_STORIES`, his canon relationships — Demonio, Diablo, SAM-UR-A1) + the UR mission shapes (waves → objective → boss; 100-mission structure from the census in `~/workspace/urban-reign-redux/UR-STAGE-MISSION-DECODE-FOLLOWON.md` — mission shapes only, NEVER Brad's story) + the T5 brawler progression (deeper stages, waves → boss, meter, ranks — the decoded DW data in `teardown/tekken5/`).
- The cross-mix in his flow: UR inputs mixed with Tekken inputs (the Piece 4 feel layer — string, dodge, aim, grabs, running, meter, weapons, region damage, lock — plus the versus Tekken inputs the brawler mode keeps), UR mechanics Tekken lacks + Tekken mechanics UR lacks, both present in his trials. Partner rule stays: Demonio joins his corner after the Gallery of Masks (UR partner-earned-by-beating, translated); partner switch between fights only, never mid-fight.
- Each new room: its own story beat (Pantera's words, his story — never Brad's, never Jin Kazama's), its own wave table, its own boss kind from the shared kinds (warden / masks / ogre / sphere / shadow), its own tuning (difficulty/restore steps above the shared flow the way his current rooms are). No "Devil" and no "Jin" anywhere in his story (test asserts it); "The Devil That Stays..." is NOT his chapter (unassigned, do not assign it).
- Update `HEARTMIND-COMPLETION.md` (Pantera rows) with measured evidence if scores move.

## Guardrails (same as Pieces 1–7)

- CANON LAWS (Jay): there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul), pickable as Phantom. "Devil" may appear ONLY in OUR own way and language, NEVER in the Devil Within way. Pantera is male (he/him); every other fighter by name only, no guessed pronouns.
- STANDING RULE (Jay 2026-11-08): top-level industry-standard way, from their source and code — not hand-tooled, not homebrewed, fully wired up, landed in the repo, from research, never guessing. Our own code is thin glue only.
- No commercial game code/models/art/audio/logos/dialogue copied into the game, even privately — measure and rebuild in our own code.
- If any piece hits a real blocker, stop at the blocker, write the exact blocker + what would unblock it, and report — do not hand-build a workaround and call it the fix.
- Proof: a live playthrough of the EXTENDED Pantera flow, phone-size, video, watched in motion — proof under `~/workspace/western-heart-audit/proof-pantera-extended/`, NOT /tmp.
- DISK: VM quota freed 2026-11-08 ~11:27 but the edge moves — the output-disc build died on quota again, so treat quota as FRAGILE: on EDQUOT stop, delete ONLY own partials, report exact error + bytes written, never touch `~/workspace/video-mocap` or `browser_downloads` (Jay's files, never delete).
- Workdir for the clone: `~/workspace/pantera-extended/repo` (fresh single-branch clone of main, HEAD verified `fcaa8b1d`). Branch: `pantera-extended`.
