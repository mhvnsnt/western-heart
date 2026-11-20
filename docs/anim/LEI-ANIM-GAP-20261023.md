# Lei Wulong motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T7 FIRST, then
TTT2/T6/T5, T3 LAST (fallback only).** Lei debuted in Tekken 2 — T7 is his current game and the primary source; TTT2/T6/T5 hold his modern motion; the T3 lei bank (PR #405) is the fallback. A dedicated
extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the
intake manifest for that lane — pull what exists now, fill the precise gaps
below rather than settling for substitutes.

byou's canon base is Lei Wulong (Tekken 2, 1995). His MOVESET data is now complete on his own T7 tables (728 moves: 524 t7chicken + 47 rbnorway, on top of the 157 legacy T3-proxy rows kept verbatim — see `game/assets/movesets/byou.json` `t7_import_note`). His MOTION is not: no T7 Lei motion is extracted yet.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Lei Wulong
motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/byou.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter byou's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t7/lei/` (new T7 motion bank; no T7 banks exist
yet — the T7 motion extraction lane owns the format decision), registered
for `byou` so per-move `anim_ref`s (`t7:lei:…`) resolve to real clips.
Required files (mirroring the wh-anim/1 bank shape — see
`game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- stance/idle (Lei Wulong's signature stance, used in combat) — plus SNA/TIG/DGN/DRG/CRA/PHX/PAN/TGR stance idles (combat stances)
- light / medium / heavy / grab action clips
- block, hit, hit-launch, KO clips
- walk fwd/back, dash fwd, backdash, crouch, jump fwd/back/up, sidesteps
- per-move clips for the 728 T7 moves (`anim_ref: t7:lei:…`)
  — baked when the motion lands

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- intro pose → wires to the `intro` slot only
- win pose → wires to the `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW
here before it lands, and the moveset lane rejects SHOW-tagged clips.

## Source A — T7 (FIRST priority; debut-game generation; no T8 data exists for Lei as a WH source))

T7 Lei motion lives in the T7 data. Status: not extracted. The T5/T6/TTT2/T7 100% extraction lane owns this — Lei's T7 movelist is fully on disk as frame data (`docs/t7t8-reference/frame-data-t7/lei.json`, 524 rows) so the move→clip mapping is ready when motion lands.

## Source B — TTT2/T6/T5 (SECOND priority)

TTT2/T6/T5 Lei motion is the second-priority modern source. Same extraction lane; no Lei motion extracted from these yet.

## Why T3 is fallback only (and real here)

The T3 lei motion bank EXISTS on disk (`game/assets/anim/t3/lei/`, PR #405: action clips + skeleton.json). Per source priority it is the fallback, not the source — usable for Lei's classic clips only, never as a substitute for his T7 movelist motion.

## Unblock sequence (for the lane that cracks a source)

1. Decode Lei Wulong's motion stream → convert to the bank clip format
   (same shape `jsonToClip` reads in `game/js/t3anims.js`; T7 lane owns
   the exact schema — coordinate before baking).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake per-move clips for the 728 T7 moveset moves; SHOW clips bake to
   the intro/win slots only.
4. Register the bank for `byou`; combat stance and per-move rows go
   live (the 728 moves already carry `anim_ref`s); intro/win poses wire
   to their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/byou.json`: 157 → **728 moves**
(524 from the T7 t7chicken frame-data diff + 47 rbnorway).
All 571 pulled moves carry `"set": "FIGHT"` and the file carries the
`anim_set_lock` block. Verified: JSON parses; move-count and semantic-diff
audit in the PR body; `node --test game/tests/fighter-completeness.test.mjs`.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** every move in
`game/assets/movesets/byou.json` is covered by the file-level
`anim_set_lock` (`"set": "FIGHT"` stamped per-move on this pass's pulls).
SHOW animations (win/intro poses, taunts, cutscenes) are tracked in the
FIGHT/SHOW sections above — they wire to intro/win slots and cutscenes
only and must NEVER enter the moveset without the user's explicit
approval.
