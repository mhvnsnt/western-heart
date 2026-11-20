# PIECE 4 — Urban Reign feel layer (QUEUED — spawn AFTER Pieces 1–3)

**Source:** Jay's order 2026-11-08 ~12:08 — the brawler mode plays kind of like Urban Reign, so stack UR's moves and inputs on top of it. Coordinator task add, 2026-11-08 ~12:10.
**Sequencing:** AFTER Pieces 1–3. It touches the same fight code — do NOT run in parallel with Piece 1 or 2. Spawn when Pieces 1–3 have all reported.
**Same rules as Pieces 1–3:** fresh clone of main (`fcaa8b1d` — verify HEAD after cloning; no sparse checkouts; no /tmp clones), small verifiable commits, repo tests green (zero new failures), one PR, no merge, proof watched in motion.

## The stack

Grounded in the repo's own teardown, `TEARDOWN-PART-C-URBAN-REIGN.md` §2.2–2.5 + §2.7.

**BASE (already in the game):** Tekken 5 brawler mode — simple punch/kick/block/jump kit (Surge donor kit, `gym_ikdv_*`, 165 moves in the library; inputs/damage/hitboxes still UNMEASURED), waves of enemies → boss, 5 stages, meter → transform, gems heal + Force, ranks S/A/B/C, 40 symbols. The brawler engine (`game/js/brawler.js`) currently reuses each fighter's versus moveset.

**LAYER 1 (THIS PIECE — the UR feel, in this build order):**
1. Three-press string, third hit juggles → then free choice (air grapple / special / reposition / grab a weapon). Proposed name "Descent String" (Jay call #3, unanswered — wire the mechanic, keep the name out of UI until he calls it).
2. Direction = body region on strikes AND grapples (Up = head, Left/Right = upper body, Down = lower body). Proposed name "Region Strike" (call #15).
3. Dodge-timing instead of a block button + deflect + grapple-break on the same timing. Proposed name "Dodge Window" (call #4).
4. Grapple system: low/high grapples, air grapples, counters, reversals, catch grapples (catch a launched enemy mid-air), Double Attack (hit two enemies at once when facing/surrounded by two).
5. Running: dash/run-up, run up walls → Diving Strike / Diving Grapple; running directional moves (running powerbomb, stunner, leg whip, mid-air powerbomb).
6. Quick Recovery: timed press before landing after being launched — up at once in a chosen direction; avoids down strikes/grapples.
7. SPA meter: builds on attacking, being hit, dodging; two-button trigger (Circle+Triangle shape); neutral = get-off-me knockback, Up = big slow charged hit, Left/Right = multi-hit, Down = buff (Power Up +50% attack / Concentration auto-deflect+auto-break / Super Armor / Arcanum unlocks specials). SPAs can't be countered/reversed/dodged except by another SPA; can be buffered; gauge also spends to recover from stun. NOTE: this is the proven shape for our Nine-Soul Meter + Soul Surge — wire the FEEL, keep our names.
8. Weapons: 30+ (bats, pipes, bottles, shovels, 2x4s, knives) — pick up / discard, throw, catch thrown weapons, no durability; environment as weapon (smash launched enemies into walls/cars/furniture for extra damage).
9. Body-region damage: head/upper/lower each with own health; yellow injured, red destroyed; destroying lower body stuns easily; upper body makes the enemy drop a weapon.
10. Target lock + switch target while held; camera reset.

**DATA TO BUILD FROM (already on disk, no new download):** 484 UR named moves annotated as `motdatName` in `game/assets/movesets/ur-charNNN.json` (27 fighters); 31 UR moveset JSONs; shared pools `game/assets/anim/ur-general-{normal,30frame,weapon}/` (829 motions, unassigned per fighter — assignment is part of this piece where a measured basis exists, UNMAPPED with reason where none exists, never invented); 72 UR GLBs in `game/assets/models/street-reign/` (untextured phase-1 copies; textured swap is a separate named follow-up, NOT this piece).

**LAYER 2 (structure — mostly already in Pantera's flow, do NOT rebuild):** missions/trials, partners earned by beating + the 5 commands, double-teams. This piece is the FEEL only.

**LAYER 3 (ours — already in code, do NOT touch):** wrestling language (card/corner/tag), souls (Nine-Soul Meter, embers, stands), Force Claiming.

## Honest status to start from

UR feel in the brawler is C5 15% — named, not wired. The brawler still plays on versus movesets + the DW Surge kit. This piece closes that gap, system by system, in the order above. If a system's numbers are unmeasured (UR frame data was never measured — the manual gives the shape, not numbers), wire the SHAPE with the measured UR clip data and mark the numbers as the values they are (placeholder rates labelled with source + uncertainty, never presented as measured). If a system hits a real blocker, stop that system at the blocker, write the exact blocker + what would unblock it, and report — do not hand-build a workaround and call it the fix. Update `HEARTMIND-COMPLETION.md` C5 row with measured evidence if the score moves. Proof: a live brawl, phone-size, video, each system shown working — proof under `~/workspace/western-heart-audit/proof-ur-feel/`, NOT /tmp.

## Guardrails (same as Pieces 1–3)

- CANON LAWS (Jay): there is NO Jin Kazama in our game at all — the ONLY Jin is the soul JIN (the Blade Soul), pickable as Phantom. "Devil" may appear ONLY in OUR own way and language, NEVER in the Devil Within way. Pantera is male (he/him); every other fighter by name only, no guessed pronouns.
- STANDING RULE (Jay 2026-11-08): top-level industry-standard way, from their source and code — not hand-tooled, not homebrewed, fully wired up, landed in the repo, from research, never guessing. Our own code is thin glue only.
- No commercial game code/models/art/audio/logos/dialogue copied into the game, even privately — measure and rebuild in our own code.
- DISK: VM quota freed 2026-11-08 ~11:27 but the edge moves — on EDQUOT stop, delete ONLY own partials, report exact error + bytes written, never touch `~/workspace/video-mocap` or `browser_downloads` (Jay's files, never delete).
- Workdir for the clone: `~/workspace/ur-feel/repo` (fresh single-branch clone of main, HEAD verified `fcaa8b1d`). Branch: `ur-feel-layer`.
