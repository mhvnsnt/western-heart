# Decision: Vain Abel verified against Bass's real DOA5 command list (worker 69, 2026-10-22)

## Owner instruction (verbatim quote)
"Get everything from Bass Armstrong wired up to Vain Abel — everything from him." / Target Tekken-scale: 200+ moves with exact inputs, not 52. "We gotta do it in a Tekken input style type of way. And play style." (INPUT-TO-MOVE FIDELITY LAW.)

## What was done
Worker 59's 200-entry wiring was audited move-by-move against the ground truth:
`deadoralive.fandom.com/wiki/Bass_Armstrong/Dead_or_Alive_5_command_list`
(~57 strikes, ~37 throws, 11 holds, 2 down attacks, 3 taunts — 110 entries).

## Mapping errors found and fixed
- **236P was "Rolling Hell Smasher"** — the real 236P is BIG BEAR PALM;
  Rolling Hell Smasher is 236P+K (added as `qcf+1+2`). This is exactly the
  input-to-move fidelity failure the user flagged: wrong move on the input.
- "Brawler Kick" (66K) duplicated Kenka Kick — real name is KENKA KICK.
- 8K "Jumping Knee" — real 8K is JUMPING HIGH KICK; 7K Jumping Knee added.
- "Bass Slammer" -> BASS BOTTOM (real). "Turning Lariat/Muscle Elbow/Middle
  Kick" -> ROUND LARIAT / ROUND MUSCLE ELBOW / TRASS KICK (real).
- "Jurassic Toss" -> JURASSIC TRAILER; "Buzz Crush" -> BUZZ CRASH (real).
- "Grizzly Rancher" -> GRIZZLY LAUNCHER (real).
- "Freaky Bomb" (not on the real list) replaced by the real DIVE BOMBER.

## Missing real moves added (13)
Big Bear Slam, Stomping, Sidestep Hell Smasher, Sidestep Knee Lift, Buffalo
Chop, Low Kick (2K), Sidestep Bear Hug, Escape Back, Reverse Bass Lariat,
Straight Jurassic Trailer, Jumping Knee (7K), Rolling Hell Smasher (236P+K).

## Taunts
Now use real names + real DOA commands: "Bustin' you up" (6,4,6+H+P+K),
"It's Showtime!" (4,6,4+H+P+K), "Come here!" (214+H+P+K). Buffalo Rampage
added as the real Power Blow special.

## Placeholder remnants removed
13 `~legacy` moves + 6 `l`-specials merged from the 69-entry placeholder had
wrong Tekken mappings (DOA 2K->`3`, K->`4`), invented names (Hell Scissors),
and duplicates. Removed; the generator no longer merges the placeholder.
5 entries flagged UNVERIFIED (not on the DOA5 command list — Canyon Dunk,
T.F.B.D., Tandem Dive, Push Away, Bear Press); kept, not deleted.

## Result
196 entries (147 moves, 38 strings, 11 specials). 0 DOA-notation leaks in
inputs. Every duplicate-input group resolves via `~variant` context keys
(wall/back/sidestep/back-turned/rising) — input-to-move fidelity holds.
All entries carry `anim_ref`s (was 53 missing). Generator variant 8 -> 9.
Commit `da6c38a`.

## Still open (needs the DOA4 ISO)
`anim_ref`s are `doa:bass:<slug>` stubs. Binding them to real animation data
requires mot.afs/anm.afs extraction — blocked on the ISO reassembly and, for
anm.afs, on the keystream RE (0/6 reproduced per the 2026-10-20 audit).
