# PIECE 5 — UR structure layer into HeartMind (QUEUED — spawn AFTER Pieces 1–4)

**Source:** Jay's order 2026-11-08 ~12:11 — "all of that urban rain stuff that the Tekken brawler mode doesn't have, add that in to our HeartMind Within mode, and wire it in somehow." Coordinator task add, 2026-11-08 ~12:12.
**Sequencing:** AFTER Pieces 1–4. Same fight code — do NOT run in parallel with Pieces 1, 2 or 4. Spawn when Pieces 1–4 have all reported.
**Same rules as Pieces 1–4:** fresh clone of main (`fcaa8b1d` — verify HEAD after cloning; no sparse checkouts; no /tmp clones), small verifiable commits, repo tests green (zero new failures), one PR, no merge, proof watched in motion.

## Grounding

`TEARDOWN-PART-C-URBAN-REIGN.md` §2.1/§2.5 + the mission census (`~/workspace/urban-reign-redux/UR-STAGE-MISSION-DECODE-FOLLOWON.md`: 100/100 census, 87 decoded, 55 stage names, mission→stage PPK mapping measured).

## Wire, in this order

1. **Trials:** the UR 100-mission structure as HeartMind trials (wave + objective + boss per trial; retry on fail from a menu). Proposed name "Trials" (Jay call #2, unanswered — wire the structure, keep the name out of UI until he calls it).
2. **Partner commands, translated to wrestling:** double-team/tag, call for help, split up, pass a weapon, switch fighters (UR manual p.34 — R2 + button). Proposed name "Twin Strike" for the double-team (call #5).
3. **Double-team attacks:** launch an enemy and the partner catches and slams them; surround-an-enemy trigger; grapple assist (attack an enemy the partner is holding).
4. **Free Mode:** play trials with any unlocked fighter. **Challenge mode:** wave survival, solo (co-op shape later — the Furnace is the shape). **Versus** (KO/points rules), **Practice**, **Tutorial**, **Fighter Files** (character profiles) as HeartMind-adjacent modes.

## Measured vs unmeasured

- Mission `.bin` semantics PROVEN (off00 place label, spawn X/Z, facing, slot-1 spawn/presence, record counts, activation flags) — wire what's measured.
- Several fields are UNPROVEN (0x02, 0x1e, 0x20, 0x24, 0x28, 0x74/76, 0xac, 0x1d0, 0x1884 slot table) — those stay unwired and marked, never guessed.
- 9 missions NOT DECODED (VMDs 7dd4, 01cd, bd01) — skip them, report them.

## Guardrails (same as Pieces 1–4)

- CANON LAWS (Jay): there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul), pickable as Phantom. "Devil" may appear ONLY in OUR own way and language, NEVER in the Devil Within way. Pantera is male (he/him); every other fighter by name only, no guessed pronouns.
- STANDING RULE (Jay 2026-11-08): top-level industry-standard way, from their source and code — not hand-tooled, not homebrewed, fully wired up, landed in the repo, from research, never guessing. Our own code is thin glue only.
- No commercial game code/models/art/audio/logos/dialogue copied into the game, even privately — measure and rebuild in our own code.
- If any system hits a real blocker, stop that system at the blocker, write the exact blocker + what would unblock it, and report — do not hand-build a workaround and call it the fix.
- Update `HEARTMIND-COMPLETION.md` (C4 row and any other row that moves) with measured evidence if scores move.
- Proof: live, phone-size, video, each system shown working — proof under `~/workspace/western-heart-audit/proof-ur-all/`, NOT /tmp.
- DISK: VM quota freed 2026-11-08 ~11:27 but the edge moves — on EDQUOT stop, delete ONLY own partials, report exact error + bytes written, never touch `~/workspace/video-mocap` or `browser_downloads` (Jay's files, never delete).
- Workdir for the clone: `~/workspace/ur-structure/repo` (fresh single-branch clone of main, HEAD verified `fcaa8b1d`). Branch: `ur-structure-heartmind`.
