# Combat, moves and controls: the right way (2026-10-24)

Owner: "do all this the correct way and log in the documents the right way to do it ... Muse is wasting my tokens
and my time ... get it all pushed to the playable build so I can really test it ... for every character, even the
ones that aren't in T7."

This page is the working method for every agent (Claude, Muse, Grok, Repo Co Dev). It is what found and fixed the
real bugs on 2026-10-24. Follow it in order. It replaces guessing, "should work", and keyboard-only testing.

## 1. Test the way the owner plays: phone, touch, VERSUS

The owner plays on a phone, landscape, by touch: VERSUS → 1V1 VERSUS → setup → CHOOSE FIGHTERS → P1/P2 → fight,
with the on-screen joystick and the LP/RP/LK/RK buttons. Keyboard events and direct function calls do NOT exercise
that path. Every one of the bugs below was invisible to keyboard tests.

| Tool | What it does |
|---|---|
| `tools/proof-harness/touch_play.mjs OUT p1 p2` | iPhone-landscape viewport, touch only. It taps the menus along the owner's path, then drives the joystick and the buttons with real CDP multi-touch: finger 0 on the stick, finger 1 on the buttons. Per input it logs what P1's move buffer recorded and P2's damage. It ends with a 20 s free fight against the CPU and screenshots every case. |
| `tools/proof-harness/stick_probe.mjs` (`URL=...`) | Drags the stick in each direction by touch and prints what the game read: axisX, up/down, stickDir, P1 state. Run it against the LIVE site first to see what the owner sees. |
| `tools/proof-harness/live_inputs.mjs` | Keyboard timing cases (qcf, f,f, chords). Useful for timing only. It is not proof of phone play. |
| `node --test test/*.test.mjs game/tests/*.test.mjs` | Unit tests. Before blaming your change, compare against main in the same setup (`git archive origin/main ...` into a scratch dir). |

Done means: the touch harness on a build that contains your change shows the right moves, you viewed its PNGs, and the
same run on the live site shows the bug, so before and after are both on record.

## 2. The bugs found today, and their real causes

| Owner report | Real cause | Fix |
|---|---|---|
| "any touch to the joystick makes it go down; up needs a weird wide drag" | nipplejs (static mode) stores the stick centre once, at creation. It is created at boot while the fight HUD is hidden, so it stored (0,0). Live: stored {0,0} vs real {87,299}. Every touch read as down, so the fighter crouched and buttons came out as FC./WS. moves. | `dynamicPage: true` (PR #1003) |
| "random moves", "1 then 3 gives a throw" | Chord window was 140 ms: 1,3 became 1+3 (a throw), 1,2 became 1+2. | 50 ms window + event timestamps (PR #996) |
| qcf / dash / held moves don't come out | Direction history fed at 120 Hz while its windows count 60 fps frames, so every window was half length. | Entries weighted by time (PR #996) |
| "left punch does a grab", "left kick does a crouching spin kick" | The animation lookup played whatever row `anim_t3` named. Pantera's 1 → King's throw-attempt row 290. 585 strikes played throw rows, and 7,237 inputs played the generic light/medium/heavy clip. | `_attackClipPlan`: own row, same-input row, donor, then same button at the same height. Strike/throw types are enforced. (PR #996) |

The pattern: a symptom that looks like "the data is wrong" was a runtime bug every time. Find the cause with a probe
on the live build before changing data.

## 3. Data sources, in order (owner law)

1. **T7/T8 move lists and frame data**: in the repo. `docs/t7t8-reference/frame-data-t7` (TekkenBot); the
   TheBigTuna T7 data via the #999 parser (LP1/RP2/LK3/RK4); `docs/t7t8-reference/frame-data-t8-full`; MOD damage
   (#1000). Use them for each move's input, startup, active, recovery, hit level and damage.
2. **T7 animations**: NOT in the repo. Coverage is 0 of 51 (`teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md`). There are
   only two real ways to get them:
   - live extraction with TKMovesets (GPL-3.0) from a running T7 on the owner's PC or Grok's box; it gives exact
     move → animation pairs;
   - the Steam pak extraction (`teardown/tekken7/T7-STEAM-EXTRACTION.md`, 47 GB, on the owner's machine).

   Until one of them is run, the decoded T3 banks are the logged fallback (`docs/anim/PROCEDURAL_AUDIT.md`). Never
   invent, guess or "class-match" an animation and call it T7.
3. **T3 decoded banks**: real bytes from the shipped game. 22 banks; rows per move in `rows.pack.json`. Hit
   reactions, throw-victim and thrower clips are in `reactions.pack.json` (7,368 clips, decoded from the EXE tables;
   contract in `docs/anim/T3-REACTIONS.md`).
4. **Characters with no Tekken base**: their own canon source. Search the repo teardowns (WWE / No Mercy / Def Jam /
   MK research docs). Report what's missing; don't borrow another fighter's moves or stance.

## 4. One pipeline for every character, not one character at a time by hand

Run the same tools over the whole roster. Fix the tool when a character fails, not the character's data by hand.

1. Set the canon base: `roster/<id>/CANON.md` → `tools/moveset-merge/bases.json`.
2. Build the move list: `tools/moveset-merge/merge_sources.py --write --only <id>` (additions only; the tool guards
   against losing anything). Then regenerate `game/assets/movesets/index.json`.
3. Animation bank: the moveset's `anim_bank` is the canon base's decoded bank (never another fighter's).
4. Animation audit: `node tools/anim/attack_anim_audit.mjs`, per fighter. It must show 0 strikes on throw rows, 0
   throws on strike rows, and 0 generic fallbacks.
5. Inputs: `test/input-timing.test.mjs` and the reachability test (every notation in the list resolves to its own
   move).
6. Play it: `touch_play.mjs` for the fighter, by touch, and view the PNGs.
7. Ship (section 5).

## 5. Ship so the owner can play it the same hour

1. Build and verify in a scratch copy: `git archive origin/main ...` plus your files, with the big asset folders
   symlinked. Never commit from a partial tree; build commits with a temporary index (`GIT_INDEX_FILE`) from
   verified blobs.
2. Push to your branch and open the PR with the template.
3. Deploy the playable build at once from the PR's commit, without a checkout:
   `python3 tools/deploy/build_pages.py --ref <commit> --onto origin/gh-pages`. The new gh-pages commit only adds or
   updates files and refuses any removal. Then `git push origin <deploy-commit>:refs/heads/gh-pages` (fast-forward).
4. Merge when the required checks pass. GitHub blocks it before that, and that cannot be bypassed.

## 6. Never again

- Calling something "fixed" without a touch run on the built game and viewed screenshots.
- Deleting or blanking wrong animations instead of mapping the right one. That's "less broken", not fixed.
- Pushing substitute data (a T3 or class-matched clip) labelled as T7.
- Testing with keyboard or direct calls and reporting it as how the owner plays.
- Holding finished work off the playable build. Deploy each verified piece the same hour.
