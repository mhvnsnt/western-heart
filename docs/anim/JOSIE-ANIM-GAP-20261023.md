# Josie Rizal motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T7 FIRST, then
TTT2/T6/T5, T3 LAST (fallback only).** Josie debuted in Tekken 7 — T7 is her ONLY source game. TTT2/T6/T5/T3 have no Josie data and can never fill this gap. A dedicated
extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the
intake manifest for that lane — pull what exists now, fill the precise gaps
below rather than settling for substitutes.

waterfall's canon base is Josie Rizal (Tekken 7, 2015). Her MOVESET data is now complete on her own T7 tables (366 moves: 195 t7chicken + 25 rbnorway verified missing, incl. her CD (f,n,d) moves — see `game/assets/movesets/waterfall.json` `t7_import_note`). Her MOTION is not: no Josie motion exists anywhere yet.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Josie Rizal
motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/waterfall.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter waterfall's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t7/josie/` (new T7 motion bank; no T7 banks exist
yet — the T7 motion extraction lane owns the format decision), registered
for `waterfall` so per-move `anim_ref`s (`t7:josie:…`) resolve to real clips.
Required files (mirroring the wh-anim/1 bank shape — see
`game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- stance/idle (Josie Rizal's signature stance, used in combat) — plus BT/FC/WS/SS/SWS/SWB/CD stance idles (combat stances)
- light / medium / heavy / grab action clips
- block, hit, hit-launch, KO clips
- walk fwd/back, dash fwd, backdash, crouch, jump fwd/back/up, sidesteps
- per-move clips for the 366 T7 moves (`anim_ref: t7:josie:…`)
  — baked when the motion lands

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- intro pose → wires to the `intro` slot only
- win pose → wires to the `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW
here before it lands, and the moveset lane rejects SHOW-tagged clips.

## Source A — T7 (FIRST priority; only source; she debuted in T7))

T7 Josie motion lives in the T7 data. Status: not extracted. The T5/T6/TTT2/T7 100% extraction lane owns this — Josie's T7 movelist is fully on disk as frame data (`docs/t7t8-reference/frame-data-t7/josie.json`, 195 rows) so the move→clip mapping is ready when motion lands.

## Source B — TTT2/T6/T5 (SECOND priority)

Not applicable — Josie debuted in T7; no TTT2/T6/T5 motion exists.

## Why T3 cannot fill it (LAST priority — fallback empty)

Josie did not exist in Tekken 3 (1997). There is no Josie motion stream; `teardown/tekken3/animations/` has none of her. Per the owner's source-priority directive, T3 is fallback only — and for Josie the fallback is empty. Do not settle for a T3 substitution.

## Unblock sequence (for the lane that cracks a source)

1. Decode Josie Rizal's motion stream → convert to the bank clip format
   (same shape `jsonToClip` reads in `game/js/t3anims.js`; T7 lane owns
   the exact schema — coordinate before baking).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake per-move clips for the 366 T7 moveset moves; SHOW clips bake to
   the intro/win slots only.
4. Register the bank for `waterfall`; combat stance and per-move rows go
   live (the 366 moves already carry `anim_ref`s); intro/win poses wire
   to their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/waterfall.json`: 341 → **366 moves**
(195 from the T7 t7chicken frame-data diff + 25 rbnorway).
All 25 pulled moves carry `"set": "FIGHT"` and the file carries the
`anim_set_lock` block. Verified: JSON parses; move-count and semantic-diff
audit in the PR body; `node --test game/tests/fighter-completeness.test.mjs`.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** every move in
`game/assets/movesets/waterfall.json` is covered by the file-level
`anim_set_lock` (`"set": "FIGHT"` stamped per-move on this pass's pulls).
SHOW animations (win/intro poses, taunts, cutscenes) are tracked in the
FIGHT/SHOW sections above — they wire to intro/win slots and cutscenes
only and must NEVER enter the moveset without the user's explicit
approval.
